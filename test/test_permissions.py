import pytest
from starlette.testclient import TestClient
from jose import jwt
from pywork.core import Framework

@pytest.fixture
def client():
    # Crear instancia del framework y configurar la ruta protegida
    app = Framework()

    # Definir la ruta solo para usuarios con permisos de "admin"
    @app.configure_route("/admin", methods=["GET"], middleware_func=app.token_required(required_permissions=["admin"]))
    async def admin_only_route(request):
        return {"message": "Welcome, admin!"}

    return TestClient(app.get_app())

# Test 1: Acceso exitoso a ruta con token de admin
def test_access_admin_route_with_valid_token(client):
    # Crear token JWT con permisos de "admin"
    payload = {"sub": "admin_user", "permissions": ["admin"]}
    token = jwt.encode(payload, "secret", algorithm="HS256")

    response = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome, admin!"}

# Test 2: Acceso denegado a ruta con token sin permisos de "admin"
def test_access_admin_route_with_invalid_token(client):
    # Crear token JWT sin permisos de "admin"
    payload = {"sub": "normal_user", "permissions": ["user"]}
    token = jwt.encode(payload, "secret", algorithm="HS256")

    response = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {"error": "Permisos insuficientes"}

# Test 3: Acceso denegado a ruta sin token
def test_access_admin_route_without_token(client):
    response = client.get("/admin")  # No se envía token en los headers
    assert response.status_code == 401
    assert response.json() == {"error": "Token faltante"}
