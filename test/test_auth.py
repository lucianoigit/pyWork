# test/test_auth.py

import pytest
from starlette.testclient import TestClient
from pywork.core import Framework
from jose import jwt
from starlette.responses import JSONResponse

@pytest.fixture
def client():
    # Crea una instancia del framework y configura una ruta protegida
    framework = Framework()

    # Configura la ruta "/secure" con token_required usando configure_route
    @framework.configure_route("/secure", methods=["GET"], middleware_func=framework.token_required(required_permissions=["admin"]))
    async def secure_route(request):
        return {"message": "Acceso permitido"}

    # Configura la aplicación sin iniciar el servidor
    app = framework.get_app()
    return TestClient(app)

def test_access_secure_route_with_valid_token(client):
    # Genera un token JWT válido con permisos de "admin"
    payload = {"sub": "user123", "permissions": ["admin"]}
    token = jwt.encode(payload, "secret", algorithm="HS256")

    # Realiza la solicitud con el token en el encabezado de autorización
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})

    # Verifica que el acceso sea permitido
    assert response.status_code == 200
    assert response.json() == {"message": "Acceso permitido"}

def test_access_secure_route_with_invalid_token(client):
    # Genera un token JWT sin permisos de "admin"
    payload = {"sub": "user123", "permissions": ["user"]}
    token = jwt.encode(payload, "secret", algorithm="HS256")

    # Realiza la solicitud con el token de usuario sin permisos
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})

    # Verifica que el acceso sea denegado debido a permisos insuficientes
    assert response.status_code == 403
    assert response.json() == {"error": "Permisos insuficientes"}

def test_access_secure_route_without_token(client):
    # Realiza la solicitud sin token
    response = client.get("/secure")

    # Verifica que el acceso sea denegado debido a la falta de token
    assert response.status_code == 401
    assert response.json() == {"error": "Token faltante"}
