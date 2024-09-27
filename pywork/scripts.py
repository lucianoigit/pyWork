import os
import sys
import shutil

def create_clean_architecture(project_path):
    # Crear estructura para Clean Architecture
    os.makedirs(os.path.join(project_path, 'api', 'routes'))
    os.makedirs(os.path.join(project_path, 'aplicacion', 'services'))
    os.makedirs(os.path.join(project_path, 'aplicacion', 'dependency_injection'))
    os.makedirs(os.path.join(project_path, 'dominio', 'entities'))
    os.makedirs(os.path.join(project_path, 'dominio', 'repositories'))
    os.makedirs(os.path.join(project_path, 'infraestructura', 'dependency_injection'))

    # Crear archivos iniciales
    create_common_files(project_path)

    # Crear archivo main.py específico para Clean Architecture
    with open(os.path.join(project_path, 'main.py'), 'w') as f:
        f.write(
            '''from api.routes import register_routes
from infraestructura.dependency_injection import register_infrastructure_dependencies
from aplicacion.dependency_injection import register_application_dependencies
from pywork import Framework

app = Framework()

def setup():
    # Registrar dependencias
    register_infrastructure_dependencies(app)
    register_application_dependencies(app)

    # Registrar rutas de API
    register_routes(app)

if __name__ == "__main__":
    setup()
    app.run()
'''
        )

def create_hybridmvc_architecture(project_path):
    # Crear estructura para HybridMVC
    os.makedirs(os.path.join(project_path, 'controllers', 'views'))
    os.makedirs(os.path.join(project_path, 'controllers', 'api'))
    os.makedirs(os.path.join(project_path, 'models'))
    os.makedirs(os.path.join(project_path, 'infrastructure', 'dependency_injection'))
    os.makedirs(os.path.join(project_path, 'templates'))
    os.makedirs(os.path.join(project_path, 'static'))

    # Crear archivos iniciales
    create_common_files(project_path)

    # Crear archivo main.py específico para HybridMVC
    with open(os.path.join(project_path, 'main.py'), 'w') as f:
        f.write(
            '''from controllers.api import register_api_routes
from controllers.views import register_view_routes
from infrastructure.dependency_injection import register_infrastructure_dependencies
from pywork import Framework

app = Framework()

def setup():
    # Registrar dependencias
    register_infrastructure_dependencies(app)

    # Registrar rutas de vistas y APIs
    register_view_routes(app)
    register_api_routes(app)

if __name__ == "__main__":
    setup()
    app.run()
'''
        )

def create_common_files(project_path):
    # Crear requirements.txt
    with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
        f.write(
            '''starlette
uvicorn
jinja2
pydantic
aiofiles
'''
        )

def create_project():
    if len(sys.argv) < 3:
        print("Uso: create-pywork <nombre_proyecto> <arquitectura>")
        print("Opciones de arquitectura: clean, hybridmvc")
        sys.exit(1)

    project_name = sys.argv[1]
    architecture = sys.argv[2].lower()
    project_path = os.path.join(os.getcwd(), project_name)

    try:
        if architecture == 'clean':
            create_clean_architecture(project_path)
        elif architecture == 'hybridmvc':
            create_hybridmvc_architecture(project_path)
        else:
            print(f"Arquitectura desconocida: {architecture}")
            sys.exit(1)

        print(f"Proyecto {project_name} con arquitectura {architecture} creado exitosamente.")

    except Exception as e:
        print(f"Error al crear el proyecto: {e}")

if __name__ == "__main__":
    create_project()
