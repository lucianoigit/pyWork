from http.client import HTTPException
import logging
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from jose import JWTError, jwt  # Necesita 'python-jose'
import uvicorn
import os
from pydantic import ValidationError
from jinja2 import Environment, FileSystemLoader
from .Dependency_container import container, LifeCycle  # Contenedor de dependencias ya implementado
from functools import wraps

# Configuración del logger
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

    def websocket(self, path: str):
        """Registro de WebSockets en una ruta"""
        def decorator(func):
            async def websocket_handler(websocket):
                await websocket.accept()
                await func(websocket)
                await websocket.close()
            self.routes.append(WebSocketRoute(path, websocket_handler))
            logger.debug(f"WebSocket registrado en {path}")
            return func
        return decorator

    def add_cors(self, app, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]):
        """Configurar middleware CORS para la app"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
        )

    def generate_openapi(self):
        """Generar el esquema OpenAPI para Swagger"""
        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "API de Mi Framework",
                "version": "1.0.0"
            },
            "paths": {}
        }
        for route in self.routes:
            openapi_schema["paths"][route.path] = {
                "get": {
                    "summary": "Ruta dinámica",
                    "responses": {
                        "200": {
                            "description": "Respuesta exitosa"
                        }
                    }
                }
            }
        return openapi_schema

    def token_required(self, func):
        """Middleware para validar tokens JWT en rutas protegidas"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = kwargs.get('token')
            if token:
                try:
                    decoded_token = jwt.decode(token, "secret", algorithms=["HS256"])
                    kwargs['user'] = decoded_token['sub']
                except JWTError:
                    raise HTTPException(status_code=401, detail="Token inválido")
            return func(*args, **kwargs)
        return wrapper

    def run(self, mvch_mode=False):
        """Método para ejecutar el servidor, dependiendo de si es MVCH o Clean Architecture"""
        logger.debug("Ejecutando el servidor en 127.0.0.1:8000")
        app = Starlette(debug=True, routes=self.routes)

        # Si estamos en MVCH, monta los archivos estáticos
        if mvch_mode:
            static_dir = "pywork/static"
            if os.path.exists(static_dir):
                app.mount("/static", StaticFiles(directory=static_dir), name="static")
                logger.debug(f"Carpeta estática montada: {static_dir}")
            else:
                logger.warning(f"Carpeta estática no encontrada: {static_dir}. No se montará.")

        # Añadir CORS en cualquier modo
        self.add_cors(app)
        uvicorn.run(app, host="127.0.0.1", port=8000)
