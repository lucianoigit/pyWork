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

class Framework:
    def __init__(self):
        self.routes = []
        self.dependencies = {}  # Contenedor de dependencias
        # Configurar Jinja2 para usar la carpeta 'templates'
        self.template_env = Environment(loader=FileSystemLoader('templates'))

    def register_dependency(self, name: str, dependency):
        """Registrar una dependencia en el contenedor"""
        self.dependencies[name] = dependency

    def inject(self, func):
        """Inyectar dependencias automáticamente en las rutas"""
        async def wrapper(*args, **kwargs):
            # Recorre las anotaciones de tipo de la función
            for param_name, param_type in func.__annotations__.items():
                # Si la anotación de tipo coincide con alguna dependencia registrada
                for dep_name, dep in self.dependencies.items():
                    if isinstance(dep, param_type):
                        kwargs[param_name] = dep  # Inyectar la dependencia
                        break
                else:
                    raise ValueError(f"La dependencia '{param_name}' de tipo '{param_type.__name__}' no está registrada.")
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise RuntimeError(f"Error ejecutando la función '{func.__name__}': {str(e)}")
        return wrapper

    def get(self, path: str):
        """Decorador para definir rutas GET"""
        def decorator(func):
            func = self.inject(func)  # Inyectar dependencias automáticamente
            async def route_handler(request):
                try:
                    response = await func()
                    return HTMLResponse(response)
                except Exception as e:
                    # Manejo de errores: devuelve una respuesta JSON con el error
                    return JSONResponse({"error": str(e)}, status_code=500)
            self.routes.append(Route(path, route_handler, methods=["GET"]))
            return func
        return decorator

    def post(self, path: str):
        """Decorador para definir rutas POST con validación de datos"""
        def decorator(func):
            func = self.inject(func)  # Inyectar dependencias automáticamente
            async def route_handler(request):
                try:
                    # Obtener el cuerpo de la solicitud y validar con Pydantic
                    body = await request.json()
                    validated_data = func.__annotations__.get("data", None)
                    if validated_data:
                        body = validated_data(**body)  # Validar los datos
                    response = await func(body)
                except ValidationError as e:
                    return JSONResponse({"error": e.errors()}, status_code=400)
                except Exception as e:
                    # Manejo de errores: devuelve una respuesta JSON con el error
                    return JSONResponse({"error": str(e)}, status_code=500)
                return JSONResponse(response)
            self.routes.append(Route(path, route_handler, methods=["POST"]))
            return func
        return decorator

    def render_template(self, template_name, **context):
        """Renderizar una plantilla HTML usando Jinja2"""
        template = self.template_env.get_template(template_name)
        return template.render(**context)

    def use_script(self, script_content, script_name):
        """Guarda el script en un archivo JS y devuelve la etiqueta <script>"""
        script_path = os.path.join(SCRIPTS_DIR, f"{script_name}.js")
        
        # Guardar el contenido del script en el archivo
        with open(script_path, "w") as script_file:
            script_file.write(script_content)
        
        # Retornar la etiqueta <script> para incrustar en HTML
        return f'<script src="/static/{script_name}.js"></script>'

    def register_module(self, module):
        """Registrar todas las rutas de un módulo"""
        self.routes.extend(module.routes)

    def run(self):
        """Método para ejecutar el servidor"""
        app = Starlette(debug=True, routes=self.routes)
        app.mount("/static", StaticFiles(directory=SCRIPTS_DIR), name="static")
        uvicorn.run(app, host="127.0.0.1", port=8000)
