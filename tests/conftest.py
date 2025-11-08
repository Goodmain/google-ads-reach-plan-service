import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure project root is on sys.path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(scope="session")
def client():
    from app.main import app
    return TestClient(app)