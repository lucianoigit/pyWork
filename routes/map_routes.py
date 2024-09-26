from models.map_model import MapRequest  # Importamos el modelo Pydantic
from services.IMapService import IMapService  # Importamos la interfaz del servicio

def setup_routes(app):
    @app.route("/map", methods=["POST"])
    async def create_map(data: MapRequest, map_service: IMapService):
        """Ruta POST que recibe datos de mapa y usa IMapService"""
        mapa = map_service.generate_map(data.lat, data.lon, data.zoom)
        return {"message": mapa}

    @app.route("/map/view", methods=["GET"])
    async def show_map(map_service: IMapService):
        """Ruta GET que muestra un mapa con JavaScript dinámico"""
        message = map_service.process_message("¡Bienvenido a PyWork!")
        return message
