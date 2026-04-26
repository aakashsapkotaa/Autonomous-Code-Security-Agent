"""
CVE Lookup Agent
================
Parses dependency manifests from a cloned repo (or raw file content stored in
Supabase), queries OSV.dev and NVD in parallel, deduplicates results, and
persists findings to the `cve_findings` table.

Supported manifest files
------------------------
- requirements.txt  (PyPI)
- Pipfile            (PyPI)
- poetry.lock        (PyPI)
- package.json       (npm)

External APIs used
------------------
- OSV.dev  https://api.osv.dev/v1/querybatch   (no key required)
- NVD 2.0  https://services.nvd.nist.gov/rest/json/cves/2.0  (key optional but
           recommended — set NVD_API_KEY in .env for higher rate limits)
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

from app.core.config import settings
from app.core.db import db
from app.models.cve import CVEFinding, CVESummary, PackageRef

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
NVD_CVE_URL   = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# OSV batch size limit
OSV_CHUNK = 1000

# httpx timeout (seconds)
TIMEOUT = httpx.Timeout(30.0, connect=10.0)

# ── Manifest parsers ──────────────────────────────────────────────────────────

def _parse_requirements_txt(content: str, source_file: str = "requirements.txt") -> list[PackageRef]:
    """Parse pip requirements.txt / requirements-*.txt."""
    pkgs: list[PackageRef] = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-", "git+", "http")):
            continue
        # Strip extras, env markers, options
        line = re.split(r"\s*[;#]", line)[0].strip()
        # Match name==version or name>=version etc.
        m = re.match(r"^([A-Za-z0-9_.\-]+)\s*[=><~!]+\s*([^\s,]+)", line)
        if m:
            pkgs.append(PackageRef(
                name=m.group(1).lower(),
                version=m.group(2).strip(),
                ecosystem="PyPI",
                source_file=source_file,
            ))
    return pkgs


def _parse_pipfile(content: str) -> list[PackageRef]:
    """Parse Pipfile [packages] / [dev-packages] sections."""
    pkgs: list[PackageRef] = []
    in_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped in ("[packages]", "[dev-packages]"):
            in_section = True
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            in_section = False
            continue
        if not in_section or not stripped or stripped.startswith("#"):
            continue
        m = re.match(r'^([A-Za-z0-9_.\-]+)\s*=\s*["\']?([^"\'*\s]*)["\']?', stripped)
        if m and m.group(2):
            pkgs.append(PackageRef(
                name=m.group(1).lower(),
                version=m.group(2).lstrip("=~^><!") or "latest",
                ecosystem="PyPI",
                source_file="Pipfile",
            ))
        elif re.match(r'^([A-Za-z0-9_.\-]+)\s*=\s*["\']?\*["\']?', stripped):
            # wildcard version — still track the package
            name_match = re.match(r'^([A-Za-z0-9_.\-]+)', stripped)
            if name_match:
                pkgs.append(PackageRef(
                    name=name_match.group(1).lower(),
                    version="*",
                    ecosystem="PyPI",
                    source_file="Pipfile",
                ))
    return pkgs


def _parse_poetry_lock(content: str) -> list[PackageRef]:
    """Parse poetry.lock [[package]] blocks."""
    pkgs: list[PackageRef] = []
    name = version = None
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[[package]]":
            name = version = None
        elif stripped.startswith("name ="):
            name = stripped.split("=", 1)[1].strip().strip('"')
        elif stripped.startswith("version ="):
            version = stripped.split("=", 1)[1].strip().strip('"')
        if name and version:
            pkgs.append(PackageRef(
                name=name.lower(),
                version=version,
                ecosystem="PyPI",
                source_file="poetry.lock",
            ))
            name = version = None
    return pkgs


def _parse_package_json(content: str) -> list[PackageRef]:
    """Parse package.json dependencies + devDependencies."""
    pkgs: list[PackageRef] = []
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return pkgs
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        for pkg_name, ver_spec in data.get(section, {}).items():
            # Strip semver range prefixes: ^1.2.3 → 1.2.3
            version = re.sub(r"^[^0-9]*", "", str(ver_spec)).split(" ")[0]
            if version:
                pkgs.append(PackageRef(
                    name=pkg_name.lower(),
                    version=version,
                    ecosystem="npm",
                    source_file="package.json",
                ))
    return pkgs


def parse_manifests(repo_path: str) -> list[PackageRef]:
    """
    Walk a cloned repo directory and parse all supported manifest files.
    Returns a deduplicated list of PackageRef objects.
    """
    root = Path(repo_path)
    all_pkgs: list[PackageRef] = []

    parsers: list[tuple[str, callable]] = [
        ("requirements*.txt", _parse_requirements_txt),
        ("Pipfile",           _parse_pipfile),
        ("poetry.lock",       _parse_poetry_lock),
        ("package.json",      _parse_package_json),
    ]

    for pattern, parser in parsers:
        for path in root.rglob(pattern):
            # Skip node_modules / .venv / venv
            if any(p in path.parts for p in ("node_modules", ".venv", "venv", "__pycache__")):
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                rel = str(path.relative_to(root))
                if pattern == "requirements*.txt":
                    pkgs = _parse_requirements_txt(content, rel)
                elif pattern == "package.json":
                    pkgs = _parse_package_json(content)
                else:
                    pkgs = parser(content)
                all_pkgs.extend(pkgs)
                logger.info(f"Parsed {len(pkgs)} packages from {rel}")
            except Exception as e:
                logger.warning(f"Failed to parse {path}: {e}")

    # Deduplicate by (name, version, ecosystem)
    seen: set[tuple] = set()
    unique: list[PackageRef] = []
    for p in all_pkgs:
        key = (p.name, p.version, p.ecosystem)
        if key not in seen:
            seen.add(key)
            unique.append(p)

    logger.info(f"Total unique packages to check: {len(unique)}")
    return unique


# ── OSV.dev ───────────────────────────────────────────────────────────────────

async def _query_osv_batch(
    client: httpx.AsyncClient,
    packages: list[PackageRef],
) -> list[dict]:
    """
    Query OSV.dev /v1/querybatch for up to OSV_CHUNK packages at once.
    Returns raw OSV vuln dicts tagged with the originating PackageRef.
    """
    results: list[dict] = []

    for i in range(0, len(packages), OSV_CHUNK):
        chunk = packages[i : i + OSV_CHUNK]
        payload = {
            "queries": [
                {
                    "version": pkg.version,
                    "package": {"name": pkg.name, "ecosystem": pkg.ecosystem},
                }
                for pkg in chunk
            ]
        }
        try:
            resp = await client.post(OSV_BATCH_URL, json=payload, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            for pkg, result in zip(chunk, data.get("results", [])):
                for vuln in result.get("vulns", []):
                    vuln["_pkg"] = pkg   # attach source package
                    results.append(vuln)
        except Exception as e:
            logger.warning(f"OSV batch query failed (chunk {i}): {e}")

    return results


def _osv_to_finding(vuln: dict, scan_id: str) -> Optional[CVEFinding]:
    """Convert a raw OSV vuln dict to a CVEFinding."""
    pkg: PackageRef = vuln.get("_pkg")
    if not pkg:
        return None

    # Prefer CVE alias, fall back to OSV ID
    aliases: list[str] = vuln.get("aliases", [])
    cve_id = next((a for a in aliases if a.startswith("CVE-")), vuln.get("id", "UNKNOWN"))

    # CVSS score — OSV embeds it in severity list
    cvss_score: Optional[float] = None
    severity_label = "unknown"
    for sev in vuln.get("severity", []):
        if sev.get("type") == "CVSS_V3":
            score_str = sev.get("score", "")
            # score may be a vector string or a float
            try:
                cvss_score = float(score_str)
            except ValueError:
                # Extract base score from vector if present
                m = re.search(r"/(\d+\.\d+)$", score_str)
                if m:
                    cvss_score = float(m.group(1))
        if sev.get("type") in ("CVSS_V3", "CVSS_V2"):
            severity_label = _cvss_to_label(cvss_score)

    # Fix version — first entry in affected[].ranges[].events where "fixed" key exists
    fix_version: Optional[str] = None
    for affected in vuln.get("affected", []):
        for rng in affected.get("ranges", []):
            for event in rng.get("events", []):
                if "fixed" in event:
                    fix_version = event["fixed"]
                    break
            if fix_version:
                break
        if fix_version:
            break

    # Reference URL
    refs = vuln.get("references", [])
    ref_url = refs[0].get("url") if refs else None

    return CVEFinding(
        id="",           # filled by Supabase
        scan_id=scan_id,
        package_name=pkg.name,
        package_version=pkg.version,
        ecosystem=pkg.ecosystem,
        source_file=pkg.source_file,
        cve_id=cve_id,
        cvss_score=cvss_score,
        severity=severity_label,
        description=vuln.get("summary") or vuln.get("details", "")[:500],
        fix_version=fix_version,
        reference_url=ref_url,
        source="osv",
        created_at=datetime.now(timezone.utc),
    )


# ── NVD 2.0 ───────────────────────────────────────────────────────────────────

async def _query_nvd_for_cve(
    client: httpx.AsyncClient,
    cve_id: str,
) -> Optional[dict]:
    """Fetch enriched NVD data for a single CVE ID."""
    headers = {"apiKey": settings.NVD_API_KEY} if settings.NVD_API_KEY else {}
    try:
        resp = await client.get(
            NVD_CVE_URL,
            params={"cveId": cve_id},
            headers=headers,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        vulns = resp.json().get("vulnerabilities", [])
        return vulns[0].get("cve") if vulns else None
    except Exception as e:
        logger.debug(f"NVD lookup for {cve_id} failed: {e}")
        return None


def _enrich_from_nvd(finding: CVEFinding, nvd_cve: dict) -> CVEFinding:
    """Overwrite/fill missing fields on a CVEFinding using NVD data."""
    # CVSS v3.1 base score
    metrics = nvd_cve.get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        entries = metrics.get(key, [])
        if entries:
            data = entries[0].get("cvssData", {})
            score = data.get("baseScore")
            if score is not None:
                finding = finding.model_copy(update={
                    "cvss_score": float(score),
                    "severity": _cvss_to_label(float(score)),
                })
            break

    # Description (English preferred)
    for desc in nvd_cve.get("descriptions", []):
        if desc.get("lang") == "en":
            finding = finding.model_copy(update={"description": desc["value"][:500]})
            break

    # Reference URL
    refs = nvd_cve.get("references", [])
    if refs and not finding.reference_url:
        finding = finding.model_copy(update={"reference_url": refs[0].get("url")})

    return finding


# ── Severity helper ───────────────────────────────────────────────────────────

def _cvss_to_label(score: Optional[float]) -> str:
    if score is None:
        return "unknown"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    return "low"


# ── Main agent ────────────────────────────────────────────────────────────────

class CVELookupAgent:
    """
    Orchestrates manifest parsing → OSV batch query → optional NVD enrichment
    → Supabase persistence.
    """

    async def run(
        self,
        scan_id: str,
        repo_path: Optional[str] = None,
        manifest_contents: Optional[dict[str, str]] = None,
    ) -> CVESummary:
        """
        Parameters
        ----------
        scan_id          : UUID of the scan record in Supabase.
        repo_path        : Path to a locally cloned repo (preferred).
        manifest_contents: Fallback dict of {filename: raw_content} when no
                           local clone is available.

        Returns a CVESummary with all findings.
        """
        # 1. Parse packages
        packages: list[PackageRef] = []

        if repo_path:
            packages = parse_manifests(repo_path)
        elif manifest_contents:
            packages = self._parse_from_dict(manifest_contents)

        if not packages:
            logger.info(f"[CVE] No packages found for scan {scan_id}")
            return self._empty_summary(scan_id)

        # 2. Query OSV (batch, fast, no key needed)
        async with httpx.AsyncClient() as client:
            osv_vulns = await _query_osv_batch(client, packages)
            logger.info(f"[CVE] OSV returned {len(osv_vulns)} raw findings")

            # 3. Convert to CVEFinding objects
            findings: list[CVEFinding] = []
            for raw in osv_vulns:
                f = _osv_to_finding(raw, scan_id)
                if f:
                    findings.append(f)

            # 4. Deduplicate by (package, cve_id)
            seen: set[tuple] = set()
            unique_findings: list[CVEFinding] = []
            for f in findings:
                key = (f.package_name, f.cve_id)
                if key not in seen:
                    seen.add(key)
                    unique_findings.append(f)

            # 5. NVD enrichment — only for CVE-* IDs, run concurrently
            cve_ids = [f.cve_id for f in unique_findings if f.cve_id.startswith("CVE-")]
            if cve_ids:
                logger.info(f"[CVE] Enriching {len(cve_ids)} CVEs from NVD")
                nvd_tasks = [_query_nvd_for_cve(client, cid) for cid in cve_ids]
                nvd_results = await asyncio.gather(*nvd_tasks, return_exceptions=True)

                nvd_map: dict[str, dict] = {}
                for cid, result in zip(cve_ids, nvd_results):
                    if isinstance(result, dict):
                        nvd_map[cid] = result

                enriched: list[CVEFinding] = []
                for f in unique_findings:
                    nvd_data = nvd_map.get(f.cve_id)
                    enriched.append(_enrich_from_nvd(f, nvd_data) if nvd_data else f)
                unique_findings = enriched

        # 6. Persist to Supabase (delete old findings for this scan first)
        self._save(scan_id, unique_findings)

        # 7. Build summary
        return self._build_summary(scan_id, unique_findings)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_from_dict(contents: dict[str, str]) -> list[PackageRef]:
        pkgs: list[PackageRef] = []
        dispatch = {
            "requirements.txt": _parse_requirements_txt,
            "Pipfile":           _parse_pipfile,
            "poetry.lock":       _parse_poetry_lock,
            "package.json":      _parse_package_json,
        }
        for filename, content in contents.items():
            base = Path(filename).name
            parser = dispatch.get(base)
            if parser:
                pkgs.extend(parser(content) if base != "requirements.txt"
                            else _parse_requirements_txt(content, filename))
        return pkgs

    @staticmethod
    def _save(scan_id: str, findings: list[CVEFinding]) -> None:
        try:
            # Remove stale findings for this scan
            db.client.table("cve_findings").delete().eq("scan_id", scan_id).execute()

            if not findings:
                return

            rows = [
                {
                    "scan_id":          f.scan_id,
                    "package_name":     f.package_name,
                    "package_version":  f.package_version,
                    "ecosystem":        f.ecosystem,
                    "source_file":      f.source_file,
                    "cve_id":           f.cve_id,
                    "cvss_score":       f.cvss_score,
                    "severity":         f.severity,
                    "description":      f.description,
                    "fix_version":      f.fix_version,
                    "reference_url":    f.reference_url,
                    "source":           f.source,
                }
                for f in findings
            ]
            # Insert in chunks of 500 to stay within Supabase payload limits
            for i in range(0, len(rows), 500):
                db.client.table("cve_findings").insert(rows[i : i + 500]).execute()

            logger.info(f"[CVE] Saved {len(findings)} findings for scan {scan_id}")
        except Exception as e:
            logger.error(f"[CVE] Failed to save findings: {e}")

    @staticmethod
    def _build_summary(scan_id: str, findings: list[CVEFinding]) -> CVESummary:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
        for f in findings:
            counts[f.severity if f.severity in counts else "unknown"] += 1
        return CVESummary(
            scan_id=scan_id,
            total=len(findings),
            critical=counts["critical"],
            high=counts["high"],
            medium=counts["medium"],
            low=counts["low"],
            unknown=counts["unknown"],
            packages_affected=len({f.package_name for f in findings}),
            findings=findings,
        )

    @staticmethod
    def _empty_summary(scan_id: str) -> CVESummary:
        return CVESummary(
            scan_id=scan_id, total=0, critical=0, high=0,
            medium=0, low=0, unknown=0, packages_affected=0, findings=[],
        )


# Singleton
cve_agent = CVELookupAgent()
