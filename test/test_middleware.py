# test/test_middleware.py

import pytest
from starlette.testclient import TestClient
from pywork.core import Framework

@pytest.fixture
def client():
    # Instancia el framework y define una ruta de prueba
    framework = Framework()

    @framework.route("/test", methods=["GET", "OPTIONS"])  # Incluye OPTIONS aquí
    async def test_route():
        return {"message": "Ruta de prueba exitosa"}

    # Obtener la aplicación configurada con CORS habilitado
    app = framework.get_app(mvch_mode=False)
    
    # Ajusta allow_methods para permitir todos los métodos
    framework.add_cors(app, allow_origins=["*"], allow_methods=["*"], allow_headers=["Authorization"])
    
    return TestClient(app)

def test_cors_middleware(client):
    # Realiza una solicitud OPTIONS para probar el CORS
    response = client.options("/test", headers={"Origin": "http://example.com"})
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "*"
