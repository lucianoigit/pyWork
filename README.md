# pyWork

[![CI](https://github.com/lucianoigit/pywork/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/lucianoigit/pywork/actions)
[![Documentation Status](https://readthedocs.org/projects/pywork/badge/?version=latest)](https://pywork.readthedocs.io/)
[![MIT License](https://img.shields.io/github/license/lucianoigit/pywork)](LICENSE)

pyWork is a minimalistic Python framework inspired by FastAPI, designed for both web development and IoT applications. It includes built-in support for dependency injection, security middleware, customizable CORS, OAuth, and MQTT for IoT communication.

## Key Features

- **Web Development**: Easily define routes, use Jinja2 templating, and apply security middleware.
- **IoT Integration**: Built-in MQTT support to connect, monitor, and control IoT devices.
- **Dependency Injection**: Flexible container with configurable life cycles (Singleton, Scoped, Transient).
- **OAuth and JWT Authentication**: Secure endpoints with token-based authentication and permission validation.
- **Project Structure Options**: Supports both Clean Architecture and MVCH (Hybrid MVC) setups.

## Installation (at the moment it doesn't work, use git clone)

To install `pyWork`, you can use pip:

```bash
pip install pyWork

```

## cloned locally, install with:

```bash
pip install -e .

```

## Create new project MVCH

```bash
create-pywork my_project mvch

```

## Create new project Clean

```bash
create-pywork my_project clean

```

## Quick Start - Clean Architecture

pyWork uses a Clean Architecture structure that separates responsibilities into distinct layers. This improves the maintainability and scalability of the project. Below is a breakdown of each folder and its function within the architecture:

### Folder Structure

1- api/routes: Defines API routes. Each endpoint is configured here and may depend on services from the application layer.

2- aplication/abstractions: Contains interfaces or abstractions for services that are implemented in the application layer.

3- aplication/dependency_injection: Sets up application dependencies, registering the services required for execution.

4- aplication/services: Contains business logic in the form of services, such as UsuarioService.

5- domain/entities: Defines domain entities that represent core business concepts, such as Usuario.

6- domain/repositories: Defines interfaces for repositories, like UsuarioRepository, which are implemented in the infrastructure layer.

7- infraestructure/dependency_injection: Sets up infrastructure dependencies, such as specific repository implementations.

8- infraestructure/repositories: Implements repository interfaces defined in the domain layer, such as UsuarioRepositoryImpl, which manages user storage.

Example Configuration in main.py
The main.py file is the entry point of the application. It configures dependencies and routes before starting the server.

```python
# main.py
from api.routes.routes import setup_routes
from infraestructure.dependency_injection.dependency_injection import register_infrastructure_dependencies
from aplication.dependency_injection.dependency_injection import register_application_dependencies
from pywork import Framework

app = Framework()

def setup():
    # Register infrastructure and application dependencies
    register_infrastructure_dependencies(app)
    register_application_dependencies(app)

    # Register API routes
    setup_routes(app)

if __name__ == "__main__":
    setup()
    app.run()


```

Example of Routes in api/routes/routes.py
In this file, API routes are configured using pyWork. The endpoints are designed to interact with application services, which contain business logic.

Add @app.token_required(required_permissions=["admin"]) if your use case requires it

```python
# api/routes/routes.py
from aplication.abstractions.usuario_service import IUsuarioService
from pywork import Framework
from pydantic import BaseModel

# Request model for creating a user
class CreateUserRequest(BaseModel):
    id_usuario: int
    nombre: str
    email: str

def setup_routes(app: Framework):
    @app.route("/usuario", methods=["POST"])
    async def create_user(data: CreateUserRequest, user_service: IUsuarioService):
        """Endpoint to create a new user."""
        new_user = user_service.create_user(data.id_usuario, data.nombre, data.email)
        return {"message": f"User created: {new_user}"}

    @app.route("/usuario/{id_usuario}", methods=["GET"])
    async def get_user(id_usuario: int, user_service: IUsuarioService):
        """Endpoint to retrieve a user by their ID."""
        user = user_service.get_user(id_usuario)
        if user:
            return {"user": str(user)}
        return {"error": "User not found"}, 404


```

Application Dependency Injection in aplicacion/dependency_injection/dependency_injection.py
This file registers application-level dependencies, associating interfaces with their implementations.

```python
# aplication/dependency_injection/dependency_injection.py
def register_application_dependencies(app):
    from aplication.services.usuario_service import UsuarioService
    from aplication.abstractions.usuario_service import IUsuarioService
    from domain.repositories.usuario_repository import UsuarioRepository

    app.register_dependency(IUsuarioService, UsuarioService)


```

User Service Implementation in aplicacion/services/usuario_service.py
This service class contains the business logic for managing users, using repository abstractions from the domain layer.

```python
# aplication/services/usuario_service.py
from domain.repositories.usuario_repository import UsuarioRepository
from aplication.abstractions.usuario_service import IUsuarioService
from domain.entities.usuario import Usuario

class UsuarioService(IUsuarioService):
    def __init__(self, usuario_repository: UsuarioRepository):
        self.usuario_repository = usuario_repository

    def create_user(self, id_usuario: int, nombre: str, email: str) -> Usuario:
        new_user = Usuario(id_usuario, nombre, email)
        return self.usuario_repository.add(new_user)

    def get_user(self, id_usuario: int) -> Usuario:
        return self.usuario_repository.get(id_usuario)



```

Domain Entity Definition in dominio/entities/usuario.py
This file defines the Usuario entity, which represents a user in the system.

```python
# domain/entities/usuario.py

class Usuario:
    def __init__(self, id_usuario: int, nombre: str, email: str):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email

    def __str__(self):
        return f"User [ID: {self.id_usuario}, Name: {self.nombre}, Email: {self.email}]"


```

Domain Repository Interface in dominio/repositories/usuario_repository.py
This file defines the UsuarioRepository interface, outlining methods for user data management.

```python
# domain/repositories/usuario_repository.py

from domain.entities.usuario import Usuario
from abc import ABC, abstractmethod

class UsuarioRepository(ABC):
    @abstractmethod
    def add(self, usuario: Usuario):
        pass

    @abstractmethod
    def get(self, id_usuario: int) -> Usuario:
        pass



```

Infrastructure Dependency Injection in infraestructura/dependency_injection/dependency_injection.py
This file registers infrastructure-level dependencies, linking repository interfaces to their concrete implementations.

```python
# infraestructure/dependency_injection/dependency_injection.py
def register_infrastructure_dependencies(app):
    from domain.repositories.usuario_repository import UsuarioRepository
    from infraestructure.repositories.usuario_repository_impl import UsuarioRepositoryImpl

    app.register_dependency(UsuarioRepository, UsuarioRepositoryImpl)


```

Repository Implementation in infraestructura/repositories/usuario_repository_impl.py
This file contains the implementation of the UsuarioRepository interface, handling the actual data storage for users.

```python
# infraestructure/repositories/usuario_repository_impl.py
from domain.entities.usuario import Usuario
from domain.repositories.usuario_repository import UsuarioRepository

class UsuarioRepositoryImpl(UsuarioRepository):
    def __init__(self):
        # In a real application, this would connect to a database
        self.users = {}

    def add(self, usuario: Usuario):
        """Save a new user."""
        self.users[usuario.id_usuario] = usuario
        return usuario

    def get(self, id_usuario: int) -> Usuario:
        """Retrieve a user by their ID."""
        return self.users.get(id_usuario)


```

This Clean Architecture setup in pyWork offers a well-organized structure, where each component has a clear role, from routing and business logic to data storage. With this setup, developers can easily extend and maintain the application by working within specific layers.
