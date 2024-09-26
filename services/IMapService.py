from abc import ABC, abstractmethod
class IMapService(ABC):
    @abstractmethod
    def generate_map(self, lat: float, lon: float, zoom: int) -> str:
        pass
    @abstractmethod  
    def process_message(self, message: str) -> str:
        pass