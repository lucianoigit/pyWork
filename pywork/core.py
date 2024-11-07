from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
import uvicorn
import os
from pydantic import ValidationError
from jinja2 import Environment, FileSystemLoader
from .Dependency_container import container, LifeCycle
from functools import wraps
import logging
import paho.mqtt.client as mqtt

# Configuración del logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Framework:
    def __init__(self):
        self.routes = []
        self.template_env = Environment(loader=FileSystemLoader('templates'))
        self.oauth = OAuth()  # Integración de OAuth
        self.providers = {}  # Almacenar proveedores OAuth
        self.mqtt_clients = {}  # Almacenar clientes MQTT por conexión
        logger.debug("Framework inicializado")

    # Configurar OAuth con un proveedor
    def setup_oauth(self, provider_name, client_id, client_secret, authorize_url, token_url):
        """Configurar un proveedor OAuth"""
        self.providers[provider_name] = self.oauth.register(
            name=provider_name,
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=authorize_url,
            token_url=token_url,
            client_kwargs={"scope": "openid email profile"}
        )

    # Redirigir al login de OAuth
    async def login_with_oauth(self, request, provider_name):
        redirect_uri = request.url_for(f'{provider_name}_callback')
        return await self.providers[provider_name].authorize_redirect(request, redirect_uri)

    # Callback de OAuth para obtener el token
    async def oauth_callback(self, request, provider_name):
        token = await self.providers[provider_name].authorize_access_token(request)
        user_info = await self.providers[provider_name].parse_id_token(request, token)
        return user_info

    # Registrar dependencias
    def register_dependency(self, abstract_class, implementation_class, life_cycle=LifeCycle.SINGLETON):
        container.register(abstract_class, implementation_class, life_cycle)

    # Obtener dependencias
    def get_dependency(self, abstract_class):
        return container.resolve(abstract_class)

    # Inyectar dependencias automáticamente
    def inject(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for param_name, param_type in func.__annotations__.items():
                if param_type in container.dependencies:
                    kwargs[param_name] = container.resolve(param_type)
            return await func(*args, **kwargs)
        return wrapper

    # Definir rutas con múltiples métodos
    def route(self, path: str, methods: list = ["GET"]):
        def decorator(func):
            func = self.inject(func)

            async def route_handler(request):
                try:
                    if "POST" in methods and request.method == "POST":
                        body = await request.json()
                        validated_data = func.__annotations__.get("data", None)
                        if validated_data:
                            body = validated_data(**body)
                        response = await func(data=body)
                    else:
                        response = await func()
                    return JSONResponse(response) if "POST" in methods else HTMLResponse(response)
                except ValidationError as e:
                    return JSONResponse({"error": e.errors()}, status_code=400)
                except Exception as e:
                    logger.error(f"Error en la ruta {path}: {str(e)}")
                    return JSONResponse({"error": str(e)}, status_code=500)

            self.routes.append(Route(path, route_handler, methods=methods))
            logger.debug(f"Ruta {methods} registrada: {path}")
            return func
        return decorator

    # Renderizar plantillas usando Jinja2
    def render_template(self, template_name, **context):
        template = self.template_env.get_template(template_name)
        return template.render(**context)

    # Usar scripts dinámicos en plantillas
    def use_script(self, script_content, script_name):
        script_path = f"pywork/static/{script_name}.js"
        with open(script_path, "w") as script_file:
            script_file.write(script_content)
        return f'<script src="/static/{script_name}.js"></script>'

    # Registrar WebSocket
    def websocket(self, path: str):
        def decorator(func):
            async def websocket_handler(websocket):
                await websocket.accept()
                await func(websocket)
                await websocket.close()
            self.routes.append(WebSocketRoute(path, websocket_handler))
            logger.debug(f"WebSocket registrado en {path}")
            return func
        return decorator

    # Configurar CORS
    def add_cors(self, app, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
        )

    # Generar esquema OpenAPI para Swagger
    def generate_openapi(self):
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

    # Middleware para validar tokens JWT y permisos integrados
    def token_required(self, required_permissions=None):
        """Middleware que valida el token JWT y permisos opcionales."""
        def decorator(func):
            @wraps(func)
            async def wrapper(request, *args, **kwargs):
                token = request.headers.get("Authorization")
                if not token:
                    return JSONResponse({"error": "Token faltante"}, status_code=401)

                try:
                    token = token.split(" ")[1]
                    payload = jwt.decode(token, "secret", algorithms=["HS256"])
                    request.state.user = payload["sub"]
                    request.state.permissions = payload.get("permissions", [])

                    if required_permissions:
                        user_permissions = set(request.state.permissions)
                        if not user_permissions.issuperset(set(required_permissions)):
                            return JSONResponse({"error": "Permisos insuficientes"}, status_code=403)

                except JWTError:
                    return JSONResponse({"error": "Token inválido"}, status_code=401)

                return await func(request, *args, **kwargs)
            return wrapper
        return decorator

    # Configurar rutas genéricas para autenticación personalizada
    def configure_route(self, path: str, methods: list = ["GET"], middleware_func=None):
        def decorator(func):
            if middleware_func:
                func = middleware_func(func)

            async def route_handler(request):
                try:
                    if "POST" in methods and request.method == "POST":
                        body = await request.json()
                        response = await func(request, body)
                    else:
                        response = await func(request)
                    return JSONResponse(response)
                except Exception as e:
                    logger.error(f"Error en la ruta {path}: {str(e)}")
                    return JSONResponse({"error": str(e)}, status_code=500)

            self.routes.append(Route(path, route_handler, methods=methods))
            logger.debug(f"Ruta {methods} registrada: {path}")
            return func
        return decorator

    # Soporte para MQTT (Protocolo de Comunicación IoT)
    def mqtt_connect(self, broker_url, broker_port, on_message_callback, client_id=None):
        """Conectar al servidor MQTT"""
        def on_connect(client, userdata, flags, rc):
            logger.debug(f"Conectado al broker MQTT con código {rc}")
            client.subscribe("#")  # Suscribirse a todos los tópicos

        def on_disconnect(client, userdata, rc):
            logger.warning(f"Desconexión del broker MQTT con código {rc}")

        client = mqtt.Client(client_id)
        client.on_connect = on_connect
        client.on_message = on_message_callback
        client.on_disconnect = on_disconnect

        client.connect(broker_url, broker_port, 60)
        self.mqtt_clients[client_id or broker_url] = client

    def mqtt_publish(self, topic, payload, qos=0, retain=False, client_id=None):
        """Publicar un mensaje a un tópico MQTT"""
        client = self.mqtt_clients.get(client_id or list(self.mqtt_clients.keys())[0])
        if client:
            client.publish(topic, payload, qos, retain)

    def start_mqtt_loop(self, client_id=None):
        """Iniciar el loop del cliente MQTT"""
        client = self.mqtt_clients.get(client_id or list(self.mqtt_clients.keys())[0])
        if client:
            client.loop_start()

    # Crear una instancia de la aplicación para pruebas
    def get_app(self, mvch_mode=False):
        logger.debug("Configurando la aplicación de Starlette")
        app = Starlette(debug=True, routes=self.routes)

        # Si estamos en MVCH, monta archivos estáticos
        if mvch_mode:
            static_dir = "pywork/static"
            if os.path.exists(static_dir):
                app.mount("/static", StaticFiles(directory=static_dir), name="static")
                logger.debug(f"Carpeta estática montada: {static_dir}")
            else:
                logger.warning(f"Carpeta estática no encontrada: {static_dir}. No se montará.")

        # Añadir CORS en cualquier modo
        self.add_cors(app)
        app.add_middleware(SessionMiddleware, secret_key="supersecret")  # Middleware de sesión

        return app  # Devolver el objeto app para pruebas

    # Ejecutar el servidor
    def run(self, mvch_mode=False):
        logger.debug("Ejecutando el servidor en 127.0.0.1:8000")
        app = self.get_app(mvch_mode)
        uvicorn.run(app, host="127.0.0.1", port=8000)
