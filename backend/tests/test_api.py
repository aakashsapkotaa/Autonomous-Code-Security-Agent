"""
SecureShift — Full Test Suite
==============================
Covers:
  - Unit tests        : URL validator, repo name extractor, manifest parsers,
                        CVE severity helper, patch helper
  - Integration tests : every FastAPI endpoint via in-process TestClient
                        (no running server needed)
  - DB smoke          : Supabase connection, CRUD operations
  - Config            : required env vars present

Run all:
    cd backend
    ../.venv/Scripts/python.exe -m pytest tests/test_api.py -v

Run only unit tests (fastest, no network):
    ../.venv/Scripts/python.exe -m pytest tests/test_api.py -v -m "not integration"
"""

import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── module-level imports ──────────────────────────────────────────────────────
from app.main import app
from app.services.scan_service import ScanService
from app.services.cve_lookup import (
    _parse_requirements_txt,
    _parse_pipfile,
    _parse_poetry_lock,
    _parse_package_json,
    _cvss_to_label,
)
from app.services.pr_agent import PRAgent
from app.core.db import db, SupabaseDB
from app.core.config import settings

# Single shared TestClient — spins up the ASGI app in-process, no server needed
client = TestClient(app, raise_server_exceptions=False)

_svc = ScanService()


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get(path: str, **kw):
    return client.get(path, **kw)

def post(path: str, json: dict, **kw):
    return client.post(path, json=json, **kw)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. UNIT — URL validator
# ═══════════════════════════════════════════════════════════════════════════════

class TestURLValidator:
    @pytest.mark.parametrize("url,expected", [
        ("https://github.com/user/repo",          True),
        ("https://github.com/my-org/my-repo",     True),
        ("https://github.com/user/repo/",         True),
        ("http://github.com/user/repo",           True),
        ("https://github.com/user/repo.git",      True),
        ("https://gitlab.com/user/repo",          False),
        ("https://github.com/user",               False),
        ("https://github.com/",                   False),
        ("not-a-url",                             False),
        ("",                                      False),
        ("https://github.com/user/repo/extra",    False),
    ])
    def test_validate_github_url(self, url, expected):
        result = _svc.validate_github_url(url)
        assert result == expected, (
            f"\n  URL      : {url!r}"
            f"\n  Expected : {expected}"
            f"\n  Got      : {result}"
        )

    @pytest.mark.parametrize("url,expected_name", [
        ("https://github.com/user/my-repo",   "my-repo"),
        ("https://github.com/user/my-repo/",  "my-repo"),
        ("https://github.com/org/project",    "project"),
    ])
    def test_extract_repo_name(self, url, expected_name):
        result = _svc.extract_repo_name(url)
        assert result == expected_name, (
            f"\n  URL      : {url!r}"
            f"\n  Expected : {expected_name!r}"
            f"\n  Got      : {result!r}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. UNIT — Manifest parsers
# ═══════════════════════════════════════════════════════════════════════════════

class TestManifestParsers:
    def test_requirements_txt_basic(self):
        content = "requests==2.28.0\nflask>=2.0.0\n# comment\n-r other.txt\n"
        pkgs = _parse_requirements_txt(content)
        names = [p.name for p in pkgs]
        assert "requests" in names
        assert "flask" in names
        assert len(pkgs) == 2

    def test_requirements_txt_versions(self):
        content = "django==4.2.1\nnumpy~=1.24.0\n"
        pkgs = _parse_requirements_txt(content)
        versions = {p.name: p.version for p in pkgs}
        assert versions["django"] == "4.2.1"
        assert versions["numpy"] == "1.24.0"

    def test_requirements_txt_ecosystem(self):
        pkgs = _parse_requirements_txt("requests==2.28.0\n")
        assert pkgs[0].ecosystem == "PyPI"

    def test_package_json_basic(self):
        content = '{"dependencies":{"express":"^4.18.0","lodash":"4.17.21"}}'
        pkgs = _parse_package_json(content)
        names = [p.name for p in pkgs]
        assert "express" in names
        assert "lodash" in names

    def test_package_json_strips_semver_prefix(self):
        content = '{"dependencies":{"react":"^18.2.0"}}'
        pkgs = _parse_package_json(content)
        assert pkgs[0].version == "18.2.0"

    def test_package_json_ecosystem(self):
        pkgs = _parse_package_json('{"dependencies":{"axios":"1.0.0"}}')
        assert pkgs[0].ecosystem == "npm"

    def test_package_json_invalid(self):
        pkgs = _parse_package_json("not json")
        assert pkgs == []

    def test_pipfile_basic(self):
        content = "[packages]\nrequests = \"*\"\ndjango = \">=3.2\"\n[dev-packages]\npytest = \"*\"\n"
        pkgs = _parse_pipfile(content)
        names = [p.name for p in pkgs]
        assert "requests" in names
        assert "django" in names
        assert "pytest" in names

    def test_poetry_lock_basic(self):
        content = (
            "[[package]]\nname = \"requests\"\nversion = \"2.28.0\"\n\n"
            "[[package]]\nname = \"flask\"\nversion = \"2.3.0\"\n"
        )
        pkgs = _parse_poetry_lock(content)
        versions = {p.name: p.version for p in pkgs}
        assert versions["requests"] == "2.28.0"
        assert versions["flask"] == "2.3.0"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. UNIT — CVE severity helper
# ═══════════════════════════════════════════════════════════════════════════════

class TestCVESeverityHelper:
    @pytest.mark.parametrize("score,expected", [
        (9.8,  "critical"),
        (9.0,  "critical"),
        (8.5,  "high"),
        (7.0,  "high"),
        (6.9,  "medium"),
        (4.0,  "medium"),
        (3.9,  "low"),
        (0.0,  "low"),
        (None, "unknown"),
    ])
    def test_cvss_to_label(self, score, expected):
        result = _cvss_to_label(score)
        assert result == expected, (
            f"\n  Score    : {score}"
            f"\n  Expected : {expected!r}"
            f"\n  Got      : {result!r}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. UNIT — PR Agent patch helper
# ═══════════════════════════════════════════════════════════════════════════════

class TestPRAgentPatch:
    _agent = PRAgent.__new__(PRAgent)  # skip __init__ (needs token)

    def test_patch_by_snippet(self):
        source = "x = 1\npassword = 'secret'\ny = 2\n"
        result = self._agent._apply_patch(source, "password = 'secret'", "password = os.environ['PASSWORD']", None)
        assert "os.environ['PASSWORD']" in result
        assert "secret" not in result

    def test_patch_by_line_number(self):
        source = "line1\nBAD_LINE\nline3\n"
        result = self._agent._apply_patch(source, None, "GOOD_LINE", 2)
        assert "GOOD_LINE" in result
        assert "BAD_LINE" not in result

    def test_patch_no_match_returns_original(self):
        source = "unchanged code\n"
        result = self._agent._apply_patch(source, "nonexistent snippet", "fix", None)
        assert result == source


# ═══════════════════════════════════════════════════════════════════════════════
# 5. UNIT — Config
# ═══════════════════════════════════════════════════════════════════════════════

class TestConfig:
    def test_supabase_url_set(self):
        assert settings.SUPABASE_URL, "SUPABASE_URL must be set in .env"

    def test_supabase_key_set(self):
        assert settings.SUPABASE_KEY, "SUPABASE_KEY must be set in .env"

    def test_supabase_service_role_set(self):
        assert settings.SUPABASE_SERVICE_ROLE_KEY, "SUPABASE_SERVICE_ROLE_KEY must be set"

    def test_openrouter_key_set(self):
        assert settings.OPENROUTER_API_KEY, "OPENROUTER_API_KEY must be set in .env"

    def test_allowed_origins_includes_localhost(self):
        origins = settings.ALLOWED_ORIGINS
        assert any("localhost" in o for o in origins), (
            f"Expected localhost in ALLOWED_ORIGINS, got: {origins}"
        )

    def test_allowed_origins_includes_5173(self):
        assert "http://localhost:5173" in settings.ALLOWED_ORIGINS


# ═══════════════════════════════════════════════════════════════════════════════
# 6. UNIT — DB smoke tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestDatabase:
    def test_client_initialises(self):
        instance = SupabaseDB()
        assert instance.client is not None

    def test_list_repositories_returns_list(self):
        result = db.list_repositories()
        assert isinstance(result, list), (
            f"\n  Expected : list"
            f"\n  Got      : {type(result).__name__}"
        )

    def test_get_nonexistent_scan_returns_none(self):
        result = db.get_scan(str(uuid.uuid4()))
        assert result is None

    def test_get_nonexistent_repo_returns_none(self):
        result = db.get_repository(str(uuid.uuid4()))
        assert result is None

    def test_get_nonexistent_user_returns_none(self):
        result = db.get_user_by_id(str(uuid.uuid4()))
        assert result is None

    def test_get_vulnerabilities_unknown_scan_returns_empty(self):
        result = db.get_vulnerabilities(str(uuid.uuid4()))
        assert result == []

    def test_get_ai_fixes_unknown_vuln_returns_empty(self):
        result = db.get_ai_fixes(str(uuid.uuid4()))
        assert result == []


# ═══════════════════════════════════════════════════════════════════════════════
# 7. INTEGRATION — Health endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestHealthEndpoints:
    def test_root_returns_200(self):
        r = get("/")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}\n{r.text}"
        body = r.json()
        assert body["status"] == "operational"
        assert "version" in body

    def test_health_returns_200(self):
        r = get("/api/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "healthy"
        assert "timestamp" in body
        assert "service" in body

    def test_ready_returns_200(self):
        r = get("/api/ready")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ready"

    def test_swagger_docs_accessible(self):
        r = get("/api/docs")
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")

    def test_openapi_json_accessible(self):
        r = get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema
        assert "info" in schema


# ═══════════════════════════════════════════════════════════════════════════════
# 8. INTEGRATION — Tool check endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestToolCheck:
    def test_tools_check_returns_200(self):
        r = get("/api/scans/tools/check")
        assert r.status_code == 200
        body = r.json()
        assert "tools" in body
        assert "bandit" in body["tools"]
        assert "trufflehog" in body["tools"]
        assert "safety" in body["tools"]
        assert "missing" in body
        assert isinstance(body["missing"], list)

    def test_tools_check_response_shape(self):
        r = get("/api/scans/tools/check")
        body = r.json()
        for tool, available in body["tools"].items():
            assert isinstance(available, bool), (
                f"Tool '{tool}' availability should be bool, got {type(available)}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 9. INTEGRATION — Repository endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestRepositoryEndpoints:
    def test_list_repos_returns_200(self):
        r = get("/api/repositories/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_nonexistent_repo_returns_404(self):
        r = get(f"/api/repositories/{uuid.uuid4()}")
        assert r.status_code == 404
        assert "detail" in r.json()

    def test_get_bad_id_returns_404(self):
        r = get("/api/repositories/bad-id")
        assert r.status_code == 404

    def test_create_repo_missing_body_returns_422(self):
        r = post("/api/repositories/", json={})
        assert r.status_code == 422
        body = r.json()
        assert "detail" in body

    def test_create_repo_missing_url_returns_422(self):
        r = post("/api/repositories/", json={"repo_name": "test"})
        assert r.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# 10. INTEGRATION — Scan endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestScanEndpoints:
    def test_get_nonexistent_scan_returns_404(self):
        r = get(f"/api/scans/{uuid.uuid4()}")
        assert r.status_code == 404
        assert "detail" in r.json()

    def test_trigger_missing_body_returns_422(self):
        r = post("/api/scans/trigger", json={})
        assert r.status_code == 422

    def test_trigger_missing_repo_url_returns_422(self):
        r = post("/api/scans/trigger", json={"repo_id": str(uuid.uuid4())})
        assert r.status_code == 422

    def test_trigger_nonexistent_repo_returns_404(self):
        r = post("/api/scans/trigger", json={
            "repo_id":  str(uuid.uuid4()),
            "repo_url": "https://github.com/test/repo",
        })
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_trigger_invalid_github_url_returns_422(self):
        r = post("/api/scans/trigger", json={
            "repo_id":  str(uuid.uuid4()),
            "repo_url": "https://gitlab.com/user/repo",
        })
        # 404 (repo not found) or 422 (invalid URL) — both acceptable
        assert r.status_code in (404, 422)

    def test_trigger_valid_request_creates_scan(self):
        """
        End-to-end: create a real repo record, then trigger a scan.
        Expected: 200 with scan_id, status=pending.
        """
        from app.core.db import db

        # Create a test repo directly in DB
        repo = db.create_repository({
            "user_id":   None,
            "repo_url":  "https://github.com/fastapi/fastapi",
            "repo_name": "fastapi-test",
        })
        if not repo:
            pytest.skip("Could not create test repository in Supabase")

        repo_id = repo["id"]
        try:
            r = post("/api/scans/trigger", json={
                "repo_id":  repo_id,
                "repo_url": "https://github.com/fastapi/fastapi",
            })

            # ── Expected output ──────────────────────────────────────────────
            # {
            #   "scan_id": "<uuid>",
            #   "status":  "pending",
            #   "message": "Scan started successfully..."
            # }
            assert r.status_code == 200, (
                f"\n  Expected : 200"
                f"\n  Got      : {r.status_code}"
                f"\n  Body     : {r.text}"
            )
            body = r.json()
            assert "scan_id" in body, f"Missing 'scan_id' in response: {body}"
            assert body["status"] == "pending", (
                f"\n  Expected status : 'pending'"
                f"\n  Got             : {body['status']!r}"
            )
            assert "Scan started" in body["message"]

            # Verify scan record was created in Supabase
            scan = db.get_scan(body["scan_id"])
            assert scan is not None, "Scan record not found in Supabase after trigger"
            assert scan["repo_id"] == repo_id

        finally:
            # Cleanup
            db.client.table("repositories").delete().eq("id", repo_id).execute()


# ═══════════════════════════════════════════════════════════════════════════════
# 11. INTEGRATION — Vulnerability endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestVulnerabilityEndpoints:
    def test_get_nonexistent_vuln_returns_404(self):
        r = get(f"/api/vulnerabilities/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_get_bad_uuid_returns_404(self):
        r = get("/api/vulnerabilities/bad-id")
        assert r.status_code == 404

    def test_get_vulns_for_unknown_scan_returns_empty_list(self):
        r = get(f"/api/vulnerabilities/scan/{uuid.uuid4()}")
        assert r.status_code == 200
        assert r.json() == []


# ═══════════════════════════════════════════════════════════════════════════════
# 12. INTEGRATION — CVE endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestCVEEndpoints:
    def test_get_cves_nonexistent_scan_returns_404(self):
        r = get(f"/api/cves/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_run_cve_missing_body_returns_422(self):
        r = post(f"/api/cves/{uuid.uuid4()}/run", json={})
        assert r.status_code in (404, 422)

    def test_cve_run_with_manifest_contents(self):
        """
        Create a real scan, run CVE lookup with inline manifest content,
        verify summary shape.
        """
        from app.core.db import db

        repo = db.create_repository({
            "user_id":   None,
            "repo_url":  "https://github.com/test/cve-test",
            "repo_name": "cve-test",
        })
        if not repo:
            pytest.skip("Could not create test repository")

        scan = db.create_scan({
            "repo_id": repo["id"],
            "status":  "completed",
        })
        if not scan:
            pytest.skip("Could not create test scan")

        scan_id = scan["id"]
        try:
            r = post(f"/api/cves/{scan_id}/run", json={
                "manifest_contents": {
                    "requirements.txt": "requests==2.28.0\ndjango==3.2.0\n"
                }
            })

            # ── Expected output ──────────────────────────────────────────────
            # {
            #   "scan_id": "<uuid>",
            #   "total": <int>,
            #   "critical": <int>, "high": <int>, "medium": <int>,
            #   "low": <int>, "unknown": <int>,
            #   "packages_affected": <int>,
            #   "findings": [...]
            # }
            assert r.status_code == 200, f"CVE run failed: {r.text}"
            body = r.json()
            assert body["scan_id"] == scan_id
            assert "total" in body
            assert "findings" in body
            assert isinstance(body["findings"], list)
            assert body["total"] == len(body["findings"])
            # counts must sum correctly
            count_sum = body["critical"] + body["high"] + body["medium"] + body["low"] + body["unknown"]
            assert count_sum == body["total"], (
                f"Severity counts {count_sum} != total {body['total']}"
            )

        finally:
            db.client.table("scans").delete().eq("id", scan_id).execute()
            db.client.table("repositories").delete().eq("id", repo["id"]).execute()


# ═══════════════════════════════════════════════════════════════════════════════
# 13. INTEGRATION — Chatbot endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestChatbotEndpoint:
    def test_chat_missing_message_returns_422(self):
        r = post("/api/chatbot/chat", json={})
        assert r.status_code == 422

    def test_chat_valid_message_returns_200(self):
        r = post("/api/chatbot/chat", json={"message": "What is SecureShift?"})
        assert r.status_code == 200
        body = r.json()
        # response must have some reply field
        assert any(k in body for k in ("reply", "response", "message", "content")), (
            f"Expected a reply field in chatbot response, got keys: {list(body.keys())}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 14. INTEGRATION — CORS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestCORS:
    def test_cors_header_present_for_allowed_origin(self):
        r = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r.status_code == 200
        assert "access-control-allow-origin" in r.headers

    def test_cors_allows_localhost_5173(self):
        r = get("/api/health", headers={"Origin": "http://localhost:5173"})
        acao = r.headers.get("access-control-allow-origin", "")
        assert acao in ("http://localhost:5173", "*"), (
            f"Expected CORS allow for localhost:5173, got: {acao!r}"
        )
