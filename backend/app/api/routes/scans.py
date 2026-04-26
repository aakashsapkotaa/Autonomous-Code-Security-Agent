"""
Scan management endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from app.services.scanner import scanner
from app.core.db import db
from datetime import datetime
import shutil
import logging
import re as _re

logger = logging.getLogger(__name__)
router = APIRouter()


class ScanTriggerRequest(BaseModel):
    repo_url: str
    repo_id: str
    scan_id: Optional[str] = None


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str


# ── Tool availability check ───────────────────────────────────────────────────

def _check_tools() -> dict[str, bool]:
    return {
        "bandit":     shutil.which("bandit")     is not None,
        "trufflehog": shutil.which("trufflehog") is not None,
        "safety":     shutil.which("safety")     is not None,
    }


# ── Background scan task ──────────────────────────────────────────────────────

async def run_scan_background(scan_id: str, repo_url: str):
    from app.services.ai_fixer import OpenRouterClient

    try:
        logger.info(f"[scan:{scan_id}] ▶ started for {repo_url}")
        db.update_scan(scan_id, {"status": "running"})
        db.create_scan_log(scan_id, f"Scan started for {repo_url}", "info")

        vulnerabilities = await scanner.scan_repository(repo_url)
        logger.info(f"[scan:{scan_id}] found {len(vulnerabilities)} vulnerabilities")
        db.create_scan_log(scan_id, f"Scanner found {len(vulnerabilities)} issues", "info")

        # Normalise file paths — strip local temp dir prefix
        temp_prefix = getattr(scanner, "temp_dir", None) or ""

        fixer = OpenRouterClient()
        fixes_saved = 0

        for i, vuln in enumerate(vulnerabilities):
            raw_path = vuln.get("file_path", "")

            # Strip temp dir prefix → repo-relative forward-slash path
            if temp_prefix and raw_path.startswith(temp_prefix):
                rel = raw_path[len(temp_prefix):].lstrip("/\\").replace("\\", "/")
            else:
                # Strip any absolute Windows/Unix prefix, keep relative tail
                m = _re.match(r'^(?:[A-Za-z]:[/\\]|/).*?[/\\]((?:[^/\\]+[/\\])*[^/\\]+)$', raw_path)
                rel = m.group(1).replace("\\", "/") if m else raw_path.replace("\\", "/")

            vuln_data = {
                "scan_id":            scan_id,
                "file_path":          rel,
                "vulnerability_type": vuln.get("vulnerability_type", ""),
                "severity":           vuln.get("severity", "low"),
                "description":        vuln.get("description", ""),
                "line_number":        vuln.get("line_number"),
                "code_snippet":       vuln.get("code_snippet"),
                "tool":               vuln.get("tool", "unknown"),
            }

            vuln_record = db.create_vulnerability(vuln_data)
            if not vuln_record:
                logger.warning(f"[scan:{scan_id}] failed to save vuln #{i}")
                continue

            logger.info(f"[scan:{scan_id}] vuln {i+1}/{len(vulnerabilities)} saved — {rel} ({vuln.get('vulnerability_type')})")

            # Generate AI fix
            try:
                fix_result = await fixer.generate_fix(
                    vuln.get("vulnerability_type", ""),
                    vuln.get("severity", "low"),
                    rel,
                    vuln.get("description", ""),
                    vuln.get("code_snippet"),
                )

                logger.info(
                    f"[scan:{scan_id}] AI fix {i+1}: "
                    f"suggested={bool(fix_result.get('suggested_fix'))}, "
                    f"fixed_code_len={len(str(fix_result.get('fixed_code') or ''))}, "
                    f"confidence={fix_result.get('confidence', 0):.2f}"
                )

                # Ensure fixed_code is never null — fallback to suggested_fix
                fixed_code = fix_result.get("fixed_code") or fix_result.get("suggested_fix", "")

                fix_record = db.create_ai_fix({
                    "vulnerability_id": vuln_record["id"],
                    "suggested_fix":    fix_result.get("suggested_fix", ""),
                    "fixed_code":       fixed_code,
                    "ai_model":         "openrouter",
                    "confidence_score": fix_result.get("confidence", 0.5),
                })

                if fix_record:
                    fixes_saved += 1
                    logger.info(f"[scan:{scan_id}] ✅ fix saved id={fix_record['id']}")
                else:
                    logger.error(f"[scan:{scan_id}] ❌ db.create_ai_fix returned None for vuln {vuln_record['id']}")

            except Exception as fix_err:
                logger.error(f"[scan:{scan_id}] ❌ AI fix failed for vuln {i+1}: {fix_err}", exc_info=True)
                # Save placeholder so PR agent always has something
                db.create_ai_fix({
                    "vulnerability_id": vuln_record["id"],
                    "suggested_fix":    f"Fix {vuln.get('vulnerability_type','')}: {vuln.get('description','')}",
                    "fixed_code":       f"# TODO: Fix {vuln.get('vulnerability_type','')} — {vuln.get('description','')}",
                    "ai_model":         "placeholder",
                    "confidence_score": 0.1,
                })

        logger.info(f"[scan:{scan_id}] ✅ complete — {len(vulnerabilities)} vulns, {fixes_saved} AI fixes saved")
        db.create_scan_log(scan_id, f"AI fixes generated: {fixes_saved}/{len(vulnerabilities)}", "info")

        db.update_scan(scan_id, {
            "status":                "completed",
            "total_vulnerabilities": len(vulnerabilities),
            "scan_completed_at":     datetime.utcnow().isoformat(),
        })

    except Exception as e:
        logger.error(f"[scan:{scan_id}] ❌ fatal: {e}", exc_info=True)
        db.update_scan(scan_id, {
            "status":            "failed",
            "scan_completed_at": datetime.utcnow().isoformat(),
        })
        db.create_scan_log(scan_id, f"Scan failed: {str(e)}", "error")


# ── POST /api/scans/trigger ───────────────────────────────────────────────────

@router.post("/trigger", response_model=ScanResponse)
async def trigger_scan(request: ScanTriggerRequest, background_tasks: BackgroundTasks):
    logger.info(f"[trigger] repo_id={request.repo_id} url={request.repo_url}")

    repo = db.get_repository(request.repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{request.repo_id}' not found")

    if not _re.match(r"^https?://github\.com/[\w\-]+/[\w.\-]+/?$", request.repo_url):
        raise HTTPException(status_code=422, detail=f"Invalid GitHub URL: {request.repo_url}")

    tools = _check_tools()
    missing = [t for t, ok in tools.items() if not ok]
    if missing:
        logger.warning(f"[trigger] Tools not in PATH: {missing}")

    scan = db.create_scan({
        "repo_id":         request.repo_id,
        "status":          "pending",
        "scan_started_at": datetime.utcnow().isoformat(),
    })
    if not scan:
        raise HTTPException(status_code=500, detail="Failed to create scan record")

    scan_id = scan["id"]
    logger.info(f"[trigger] scan record created: {scan_id}")
    db.create_scan_log(scan_id, "Scan queued", "info")

    background_tasks.add_task(run_scan_background, scan_id, request.repo_url)

    tool_note = f" (missing: {', '.join(missing)})" if missing else ""
    return ScanResponse(
        scan_id=scan_id,
        status="pending",
        message=f"Scan started{tool_note}",
    )


# ── GET /api/scans/{scan_id} ──────────────────────────────────────────────────

@router.get("/{scan_id}")
async def get_scan_status(scan_id: str):
    scan = db.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    vulnerabilities = db.get_vulnerabilities(scan_id)
    for vuln in vulnerabilities:
        vuln["ai_fixes"] = db.get_ai_fixes(vuln["id"])
    return {"scan": scan, "vulnerabilities": vulnerabilities}


# ── GET /api/scans/tools/check ────────────────────────────────────────────────

@router.get("/tools/check")
async def check_tools():
    tools = _check_tools()
    return {"tools": tools, "all_available": all(tools.values()), "missing": [t for t, ok in tools.items() if not ok]}
