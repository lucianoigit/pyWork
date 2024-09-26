class MapService:
    def generate_map(self, lat: float, lon: float, zoom: int):
        return f"Generando mapa en latitud {lat}, longitud {lon} con zoom {zoom}"


    def process_message(self, message: str):
        return f"Mensaje procesado: {message}"