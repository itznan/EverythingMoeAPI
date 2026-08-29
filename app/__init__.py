"""EverythingMoe API package."""

from app.api.main import app
from app.utils.client import EverythingMoeAPI

__version__ = "1.2.0"
__all__ = ["app", "EverythingMoeAPI", "__version__"]
