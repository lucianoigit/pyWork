import pytest
from pywork import Framework

def test_framework_initialization():
    app = Framework()
    assert app is not None, "Framework instance could not be initialized."
    assert isinstance(app.routes, list), "Framework routes should be initialized as a list."
    assert len(app.routes) == 0, "Framework routes list should be empty on initialization."
