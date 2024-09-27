from pywork import Framework
from services.map_service import MapService  # Implementación concreta
from services.IMapService import IMapService  # Interfaz

# Inicializar la aplicación
app = Framework()

# Cargar las rutas desde el directorio "routes"
import routes.map_routes as map_routes  # Importar las rutas de los mapas
map_routes.setup_routes(app)  # Registrar las rutas en la aplicación

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run()
