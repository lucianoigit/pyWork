import os
import sys

def create_clean_architecture(project_path):
    # Crear estructura para Clean Architecture
    os.makedirs(os.path.join(project_path, 'api', 'routes'))
    os.makedirs(os.path.join(project_path, 'aplicacion', 'services'))
    os.makedirs(os.path.join(project_path, 'aplicacion', 'dependency_injection'))
    os.makedirs(os.path.join(project_path, 'dominio', 'entities'))
    os.makedirs(os.path.join(project_path, 'dominio', 'repositories'))
    os.makedirs(os.path.join(project_path, 'infraestructura', 'dependency_injection'))

    # Crear archivos __init__.py en todos los directorios
    create_init_files(project_path)

    # Crear archivo para dependencias de infraestructura
    with open(os.path.join(project_path, 'infraestructura', 'dependency_injection', 'dependency_injection.py'), 'w') as f:
        f.write(
            '''def register_infrastructure_dependencies(app):
    from dominio.repositories.usuario_repository import UsuarioRepository
    from infraestructura.repositories.usuario_repository_impl import UsuarioRepositoryImpl

    app.register_dependency(UsuarioRepository, UsuarioRepositoryImpl)
'''
        )

    # Crear archivo para dependencias de la aplicación
    with open(os.path.join(project_path, 'aplicacion', 'dependency_injection', 'dependency_injection.py'), 'w') as f:
        f.write(
            '''def register_application_dependencies(app):
    from aplicacion.services.usuario_service import UsuarioService
    from dominio.repositories.usuario_repository import UsuarioRepository

    usuario_repo = app.get_dependency(UsuarioRepository)
    app.register_dependency(UsuarioService, UsuarioService(usuario_repo))
'''
        )

    # Crear archivo de rutas en api/routes.py
    with open(os.path.join(project_path, 'api', 'routes', 'routes.py'), 'w') as f:
        f.write(
            '''def setup_routes(app):
    @app.route("/usuarios", methods=["GET"])
    async def get_usuarios():
        return {"message": "Lista de usuarios"}
'''
        )

    # Crear archivo main.py específico para Clean Architecture
    with open(os.path.join(project_path, 'main.py'), 'w') as f:
        f.write(
            '''from api.routes.routes import setup_routes
from infraestructura.dependency_injection.dependency_injection import register_infrastructure_dependencies
from aplicacion.dependency_injection.dependency_injection import register_application_dependencies
from pywork import Framework

app = Framework()

def setup():
    # Registrar dependencias
    register_infrastructure_dependencies(app)
    register_application_dependencies(app)

    # Registrar rutas de API
    setup_routes(app)

if __name__ == "__main__":
    setup()
    app.run()
'''
        )

def create_mvch_architecture(project_path):
    # Crear estructura para MVCH (HybridMVC)
    os.makedirs(os.path.join(project_path, 'controllers', 'views'))
    os.makedirs(os.path.join(project_path, 'controllers', 'api'))
    os.makedirs(os.path.join(project_path, 'models'))
    os.makedirs(os.path.join(project_path, 'infrastructure', 'dependency_injection'))
    os.makedirs(os.path.join(project_path, 'templates'))
    os.makedirs(os.path.join(project_path, 'static', 'js'))

    # Crear archivos __init__.py en todos los directorios
    create_init_files(project_path)

    # Crear archivo de dependencias de infraestructura
    with open(os.path.join(project_path, 'infrastructure', 'dependency_injection', 'dependency_injection.py'), 'w') as f:
        f.write(
            '''def register_infrastructure_dependencies(app):
    from models.usuario_model import UsuarioModel

    app.register_dependency(UsuarioModel, UsuarioModel)
'''
        )

    # Crear archivo de rutas en controllers/api.py
    with open(os.path.join(project_path, 'controllers', 'api', 'api.py'), 'w') as f:
        f.write(
            '''def setup_api_routes(app):
    @app.route("/api/usuarios", methods=["GET"])
    async def get_api_usuarios():
        return {"message": "Lista de usuarios desde API"}
'''
        )

    # Crear archivo de rutas para vistas en controllers/views.py
    with open(os.path.join(project_path, 'controllers', 'views', 'views.py'), 'w') as f:
        f.write(
            '''def setup_view_routes(app):
    @app.route("/usuarios", methods=["GET"])
    async def get_view_usuarios():
        return app.render_template("index.html", title="Lista de usuarios")
'''
        )

    # Crear archivo de ejemplo para un template y script JS
    with open(os.path.join(project_path, 'templates', 'index.html'), 'w') as f:
        f.write(
            '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HybridMVC Example</title>
</head>
<body>
    <h1>Bienvenido a la vista renderizada del servidor</h1>
    <script src="/static/js/main.js"></script>
</body>
</html>
'''
        )

    with open(os.path.join(project_path, 'static', 'js', 'main.js'), 'w') as f:
        f.write(
            '''console.log('Script de JavaScript cargado desde el servidor.');'''
        )

    # Crear archivo main.py específico para MVCH
    with open(os.path.join(project_path, 'main.py'), 'w') as f:
        f.write(
            '''from controllers.api.api import setup_api_routes
from controllers.views.views import setup_view_routes
from infrastructure.dependency_injection.dependency_injection import register_infrastructure_dependencies
from pywork import Framework

app = Framework()

def setup():
    # Registrar dependencias
    register_infrastructure_dependencies(app)

    # Registrar rutas de vistas y APIs
    setup_view_routes(app)
    setup_api_routes(app)

if __name__ == "__main__":
    setup()
    app.run()
'''
        )

def create_init_files(project_path):
    """Crea archivos __init__.py vacíos en todos los directorios."""
    for root, dirs, files in os.walk(project_path):
        for dir_name in dirs:
            init_file_path = os.path.join(root, dir_name, '__init__.py')
            with open(init_file_path, 'w') as f:
                pass

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
        print("Opciones de arquitectura: clean, mvch")
        sys.exit(1)

    project_name = sys.argv[1]
    architecture = sys.argv[2].lower()
    project_path = os.path.join(os.getcwd(), project_name)

    try:
        if architecture == 'clean':
            create_clean_architecture(project_path)
        elif architecture == 'mvch':
            create_mvch_architecture(project_path)
        else:
            print(f"Arquitectura desconocida: {architecture}")
            sys.exit(1)

        print(f"Proyecto {project_name} con arquitectura {architecture} creado exitosamente.")

    except Exception as e:
        print(f"Error al crear el proyecto: {e}")

if __name__ == "__main__":
    create_project()
