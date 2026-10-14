from app.main import app


def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_index_returns_message():
    response = client().get("/")
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_health_ok():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_metrics_exposed():
    response = client().get("/metrics")
    assert response.status_code == 200
    assert b"app_requests_total" in response.data
