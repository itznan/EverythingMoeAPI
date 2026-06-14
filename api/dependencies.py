from utils.client import EverythingMoeAPI

_api_client = EverythingMoeAPI()

def get_api_client() -> EverythingMoeAPI:
    """Dependency provider for the EverythingMoe API client instance."""
    return _api_client
