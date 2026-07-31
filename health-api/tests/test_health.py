from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_api_returns_expected_shape():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert data["status"] in ["ok", "degraded", "down"]

    assert "services" in data
    assert isinstance(data["services"], list)
    assert len(data["services"]) >= 2


def test_health_api_contains_expected_services():
    response = client.get("/api/v1/health")
    data = response.json()

    services = data["services"]
    service_ids = {service["id"] for service in services}

    # subs 探测已随门户下线暂时注释，恢复时一并打开
    # assert "subs" in service_ids
    assert "cli-proxy-api" in service_ids
    assert "smart-notes" in service_ids


def test_each_service_has_required_fields():
    response = client.get("/api/v1/health")
    data = response.json()

    for service in data["services"]:
        assert "id" in service
        assert "name" in service
        assert "url" in service
        assert "status" in service
        assert service["status"] in ["up", "degraded", "down", "planned"]
        assert "statusCode" in service
        assert "latencyMs" in service


def test_planned_services_are_not_probed():
    response = client.get("/api/v1/health")
    data = response.json()

    planned_services = [
        service for service in data["services"]
        if service["status"] == "planned"
    ]

    # 当前所有服务均已上线探测，若后续新增 planned 服务，确保其不被探测
    for service in planned_services:
        assert service["statusCode"] is None
        assert service["latencyMs"] is None