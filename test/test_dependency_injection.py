from abc import ABC, abstractmethod
import pytest
from pywork import Framework
from pywork.Dependency_container import LifeCycle

# Mock dependency class
class IService(ABC):
    @abstractmethod
    def process(self) -> str:
        pass
    
class ServiceMock(IService):
    def __init__(self):
        self.value = "Mocked Service"

    def process(self) -> str:
        return "Service Mock Processed"

def test_register_dependency_with_interface():
    """Test that a dependency can be registered with an interface as the key."""
    app = Framework()
    app.register_dependency(IService, ServiceMock)
    resolved = app.get_dependency(IService)
    assert isinstance(resolved, ServiceMock), "Dependency resolution failed for interface injection."
    assert resolved.process() == "Service Mock Processed", "Resolved dependency did not return expected result."

def test_dependency_lifecycle_singleton():
    """Test singleton lifecycle management for dependency injection."""
    app = Framework()
    app.register_dependency(IService, ServiceMock, life_cycle=LifeCycle.SINGLETON)
    instance1 = app.get_dependency(IService)
    instance2 = app.get_dependency(IService)
    assert instance1 is instance2, "Singleton lifecycle is not maintained for dependencies registered by interface."

def test_dependency_lifecycle_transient():
    """Test transient lifecycle management for dependency injection."""
    app = Framework()
    app.register_dependency(IService, ServiceMock, life_cycle=LifeCycle.TRANSIENT)
    instance1 = app.get_dependency(IService)
    instance2 = app.get_dependency(IService)
    assert instance1 is not instance2, "Transient lifecycle is not maintained for dependencies registered by interface."