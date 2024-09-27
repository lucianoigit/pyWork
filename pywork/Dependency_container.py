# dependency_container.py
import inspect
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class LifeCycle(Enum):
    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"

class DependencyContainer:
    def __init__(self):
        self.dependencies = {}
        self.scoped_instances = {}

    def register(self, abstract_class, implementation_class, life_cycle=LifeCycle.SINGLETON):
        """Registrar una dependencia en el contenedor."""
        self.dependencies[abstract_class] = {"class": implementation_class, "life_cycle": life_cycle}
        logger.debug(f"Registrado: {abstract_class.__name__} -> {implementation_class.__name__} [{life_cycle.value}]")

    def resolve(self, cls, scoped_context=None):
        """Resuelve una dependencia por su clase."""
        if cls not in self.dependencies:
            raise ValueError(f"No se ha registrado una implementación para '{cls.__name__}'")

        dep_info = self.dependencies[cls]
        implementation_class = dep_info["class"]
        life_cycle = dep_info["life_cycle"]

        # Ciclo de vida Singleton
        if life_cycle == LifeCycle.SINGLETON:
            if not hasattr(implementation_class, '_instance'):
                implementation_class._instance = self._create_instance(implementation_class)
            return implementation_class._instance

        # Ciclo de vida Scoped
        elif life_cycle == LifeCycle.SCOPED:
            if scoped_context is None:
                raise ValueError("No se ha proporcionado un contexto de ámbito (scoped_context)")
            if cls not in scoped_context:
                scoped_context[cls] = self._create_instance(implementation_class)
            return scoped_context[cls]

        # Ciclo de vida Transient
        elif life_cycle == LifeCycle.TRANSIENT:
            return self._create_instance(implementation_class)

    def _create_instance(self, cls):
        """Crear una instancia de la clase con sus dependencias inyectadas."""
        constructor_params = inspect.signature(cls.__init__).parameters
        if not constructor_params:
            return cls()
        else:
            resolved_params = {
                param: self.resolve(param_type.annotation)
                for param, param_type in constructor_params.items()
                if param != 'self'
            }
            return cls(**resolved_params)

# Instancia global del contenedor
container = DependencyContainer()
