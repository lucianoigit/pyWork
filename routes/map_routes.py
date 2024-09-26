from pywork import Framework
from models.map_model import MapRequest  # Importamos el modelo Pydantic
from services.map_service import MapService  # Importamos el servicio

module = Framework()

@module.post("/map")
async def create_map(data: MapRequest, map_service: MapService):
    """Ruta POST que recibe datos de mapa y usa MapService"""
    mapa = map_service.generate_map(data.lat, data.lon, data.zoom)
    return {"message": mapa}

@module.get("/map/view")
async def show_map(map_service:MapService):
    """Ruta GET que muestra un mapa con JavaScript dinámico"""
    message = map_service.process_message("¡Bienvenido a PyWork!")
    # Generar un script dinámico usando el método use_script de Framework
    script_tag = module.use_script("""
        console.log('Mapa cargado con JavaScript generado en el servidor');
        // Aquí puedes inicializar un mapa usando Leaflet o Google Maps
    """, "map_script")
    
    # Renderizar la plantilla HTML con Jinja2 e inyectar el script dinámico
    return module.render_template(
        "map.html", 
        title=message, 
        header="Mapa Dinámico",
        script_tag=script_tag  # Inyectar el script generado dinámicamente
    )
