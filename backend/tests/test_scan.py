"""
Unit tests for security scanning functionality
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SupabaseDB
from unittest.mock import Mock, patch
import uuid

client = TestClient(app)

@pytest.fixture
def mock_db():
    """Mock database for testing"""
    with patch('app.core.db.SupabaseDB') as mock:
        db = Mock()
        db.create_scan.return_value = {
            "id": str(uuid.uuid4()),
            "repository_id": str(uuid.uuid4()),
            "status": "pending",
            "total_vulnerabilities": 0
        }
        db.get_scan.return_value = {
            "id": str(uuid.uuid4()),
            "status": "completed",
            "total_vulnerabilities": 5
        }
        mock.return_value = db
        yield db

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_scan(mock_db):
    """Test scan creation"""
    repo_id = str(uuid.uuid4())
    response = client.post(
        "/api/scans/",
        json={"repository_id": repo_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"

def test_get_scan(mock_db):
    """Test retrieving scan details"""
    scan_id = str(uuid.uuid4())
    response = client.get(f"/api/scans/{scan_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["total_vulnerabilities"] == 5

def test_create_repository():
    """Test repository creation"""
    response = client.post(
        "/api/repositories/",
        json={
            "repo_name": "test/repo",
            "repo_url": "https://github.com/test/repo.git",
            "branch": "main"
        }
    )
    # Will fail without auth, but tests the endpoint exists
    assert response.status_code in [200, 401, 422]

def test_list_repositories():
    """Test listing repositories"""
    response = client.get("/api/repositories/")
    # Will fail without auth, but tests the endpoint exists
    assert response.status_code in [200, 401]

@pytest.mark.asyncio
async def test_scanner_integration():
    """Test security scanner integration"""
    from app.services.scanner import SecurityScanner
    
    scanner = SecurityScanner()
    # Test that scanner initializes correctly
    assert scanner is not None

def test_vulnerability_model():
    """Test vulnerability data model"""
    from app.models.vulnerability import Vulnerability
    
    vuln = Vulnerability(
        scan_id=str(uuid.uuid4()),
        vulnerability_type="SQL_INJECTION",
        severity="high",
        file_path="/app/main.py",
        line_number=42,
        description="Potential SQL injection"
    )
    assert vuln.severity == "high"
    assert vuln.vulnerability_type == "SQL_INJECTION"

def test_scan_model():
    """Test scan data model"""
    from app.models.scan import Scan
    
    scan = Scan(
        repository_id=str(uuid.uuid4()),
        status="pending"
    )
    assert scan.status == "pending"
    assert scan.total_vulnerabilities == 0