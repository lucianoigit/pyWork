# test/test_routes.py

import pytest
from starlette.testclient import TestClient
from pywork.core import Framework
from starlette.responses import JSONResponse  # Importa JSONResponse

@pytest.fixture
def client():
    # Crea una instancia de Framework y define una ruta de prueba
    framework = Framework()

    @framework.route("/test", methods=["GET"])
    async def test_route():
        # Devuelve JSONResponse en lugar de un diccionario directamente
        return JSONResponse({"message": "Ruta de prueba exitosa"})

    # Usa get_app() para obtener la instancia de la aplicación configurada
    app = framework.get_app()  # Configura la app sin iniciar el servidor
    return TestClient(app)  # Devuelve un cliente de prueba

def test_test_route(client):
    # Realiza una solicitud GET a la ruta de prueba
    response = client.get("/test")

    # Verifica que el código de respuesta sea 200 y el mensaje sea correcto
    assert response.status_code == 200
    assert response.json() == {"message": "Ruta de prueba exitosa"}
