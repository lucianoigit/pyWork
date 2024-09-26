from pydantic import BaseModel

class MapRequest(BaseModel):
    lat: float
    lon: float
    zoom: int = 12  # Zoom por defecto
