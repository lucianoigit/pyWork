import logging
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
import uvicorn
import os
from pydantic import ValidationError
from jinja2 import Environment, FileSystemLoader

# Carpeta para archivos estáticos (JavaScript generado)
SCRIPTS_DIR = "pywork/static"
if not os.path.exists(SCRIPTS_DIR):
    os.makedirs(SCRIPTS_DIR)

# Configurar el logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Framework:
    def __init__(self):
        self.routes = []
        self.dependencies = {}  # Contenedor de dependencias
        self.template_env = Environment(loader=FileSystemLoader('templates'))
        logger.debug("Framework inicializado")

    def register_dependency(self, abstract_class, implementation_instance):
        """Registrar una dependencia en el contenedor asociada a una interfaz o clase abstracta"""
        logger.debug(f"Intentando registrar {abstract_class.__name__} -> {type(implementation_instance).__name__}")
        if abstract_class not in self.dependencies:
            self.dependencies[abstract_class] = implementation_instance
            logger.debug(f"Dependencia registrada: {abstract_class.__name__} -> {type(implementation_instance).__name__}")
        else:
            raise ValueError(f"La dependencia '{abstract_class.__name__}' ya está registrada")

    def inject(self, func):
        """Inyectar dependencias automáticamente en las rutas basado en la interfaz o clase abstracta"""
        async def wrapper(*args, **kwargs):
            for param_name, param_type in func.__annotations__.items():
                if param_type in self.dependencies:
                    kwargs[param_name] = self.dependencies[param_type]
                else:
                    raise ValueError(f"No se ha registrado una implementación para '{param_type.__name__}'")
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise RuntimeError(f"Error ejecutando la función '{func.__name__}': {str(e)}")
        return wrapper

    def route(self, path: str, methods: list = ["GET"]):
        """Método para agregar rutas dinámicamente, permite múltiples métodos"""
        def decorator(func):
            func = self.inject(func)  # Inyectar dependencias automáticamente

            async def route_handler(request):
                try:
                    if "POST" in methods and request.method == "POST":
                        # Obtener el cuerpo de la solicitud y validar con Pydantic si corresponde
                        body = await request.json()
                        validated_data = func.__annotations__.get("data", None)
                        if validated_data:
                            body = validated_data(**body)  # Validar los datos
                        response = await func(body)
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
        script_path = os.path.join(SCRIPTS_DIR, f"{script_name}.js")
        with open(script_path, "w") as script_file:
            script_file.write(script_content)
        return f'<script src="/static/{script_name}.js"></script>'

    def register_module(self, module):
        """Registrar todas las rutas de un módulo"""
        self.routes.extend(module.routes)
        logger.debug(f"Rutas del módulo {module} registradas")

    def run(self):
        """Método para ejecutar el servidor"""
        logger.debug("Ejecutando el servidor en 127.0.0.1:8000")
        app = Starlette(debug=True, routes=self.routes)
        app.mount("/static", StaticFiles(directory=SCRIPTS_DIR), name="static")
        uvicorn.run(app, host="127.0.0.1", port=8000)
