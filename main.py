from pywork import Framework
import routes.map_routes as map_routes  # Importamos las rutas
from services.map_service import MapService  # Importamos el servicio de mapas

# Crear la instancia del framework
app = Framework()

# Registrar dependencias (MapService)
map_service = MapService()
app.register_dependency("map_service", map_service)

# Registrar módulos de rutas
app.register_module(map_routes.module)

# Ejecutar el servidor
if __name__ == "__main__":
    app.run()