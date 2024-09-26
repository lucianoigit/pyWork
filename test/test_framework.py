import pytest
from starlette.testclient import TestClient
from pywork import Framework

# Servicio de prueba
class MyService:
    def process_message(self, message: str) -> str:
        return f"Mensaje procesado: {message}"

# Ruta de prueba
app = Framework()

@app.get("/")
async def index(my_service: MyService):
    message = my_service.process_message("¡Bienvenido a PyWork!")
    return message

# Ruta POST con validación de datos
from pydantic import BaseModel

class MessageModel(BaseModel):
    message: str

@app.post("/process")
async def process_message(data: MessageModel, my_service: MyService):
    processed_message = my_service.process_message(data.message)
    return {"message": processed_message}

# Registrar dependencias y configurar el cliente de pruebas
my_service = MyService()
app.register_dependency("my_service", my_service)

@pytest.fixture
def client():
    app_instance = Framework()
    app_instance.register_dependency("my_service", my_service)
    return TestClient(app_instance)

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Mensaje procesado: ¡Bienvenido a PyWork!" in response.text

def test_process_message(client):
    response = client.post("/process", json={"message": "Hola"})
    assert response.status_code == 200
    assert response.json() == {"message": "Mensaje procesado: Hola"}
