import pytest
from starlette.testclient import TestClient
from pywork.core import Framework

@pytest.fixture
def client():
    framework = Framework()
    @framework.route("/test", methods=["GET"])
    async def test_route():
        return {"message": "Ruta de prueba exitosa"}
    
    app = framework.get_app()
    return TestClient(app)

def test_test_route(client):
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Ruta de prueba exitosa"}
