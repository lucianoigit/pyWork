# core.py
import logging
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
import uvicorn
from jinja2 import Environment, FileSystemLoader
from functools import wraps
from .Dependency_container import container, LifeCycle  # Importamos el contenedor y ciclos de vida

# Configurar el logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Framework:
    def __init__(self):
        self.routes = []
        self.template_env = Environment(loader=FileSystemLoader('templates'))
        logger.debug("Framework inicializado")

    def register_dependency(self, abstract_class, implementation_class, life_cycle=LifeCycle.SINGLETON):
        """Registrar una dependencia en el contenedor con un ciclo de vida."""
        container.register(abstract_class, implementation_class, life_cycle)

    def get_dependency(self, abstract_class):
        """Obtener una dependencia registrada por su clase abstracta"""
        return container.resolve(abstract_class)
        
    def inject(self, func):
        """Inyectar dependencias automáticamente en las rutas."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Resolver dependencias basadas en las anotaciones de la función
            for param_name, param_type in func.__annotations__.items():
                if param_type in container.dependencies:
                    kwargs[param_name] = container.resolve(param_type)
            return await func(*args, **kwargs)
        return wrapper

    def route(self, path: str, methods: list = ["GET"]):
        """Método para agregar rutas dinámicamente, permite múltiples métodos"""
        def decorator(func):
            func = self.inject(func)

            async def route_handler(request):
                try:
                    if "POST" in methods and request.method == "POST":
                        body = await request.json()
                        validated_data = func.__annotations__.get("data", None)
                        if validated_data:
                            body = validated_data(**body)  # Validar los datos
                        response = await func(data=body)
                    else:
                        response = await func()
                    
                    return JSONResponse(response) if "POST" in methods else HTMLResponse(response)
                except ValidationError as e:
                    return JSONResponse({"error": e.errors()}, status_code=400)
                except Exception as e:
                    logger.error(f"Error en la ruta {path}: {str(e)}")
                    return JSONResponse({"error": str(e)}, status_code=500)

            # Registrar la ruta para los métodos adecuados
            self.routes.append(Route(path, route_handler, methods=methods))
            logger.debug(f"Ruta {methods} registrada: {path}")
            return func
        return decorator

    def render_template(self, template_name, **context):
        """Renderizar una plantilla HTML usando Jinja2"""
        template = self.template_env.get_template(template_name)
        return template.render(**context)

    def use_script(self, script_content, script_name):
        """Guarda el script en un archivo JS y devuelve la etiqueta <script>"""
        script_path = f"pywork/static/{script_name}.js"
        with open(script_path, "w") as script_file:
            script_file.write(script_content)
        return f'<script src="/static/{script_name}.js"></script>'

    def run(self):
        """Método para ejecutar el servidor"""
        logger.debug("Ejecutando el servidor en 127.0.0.1:8000")
        app = Starlette(debug=True, routes=self.routes)
        app.mount("/static", StaticFiles(directory="pywork/static"), name="static")
        uvicorn.run(app, host="127.0.0.1", port=8000)
