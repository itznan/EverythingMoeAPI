class EverythingMoeError(Exception):
    """Base exception for all EverythingMoe API errors."""


class EverythingMoeNetworkError(EverythingMoeError):
    """Raised when a network request fails, times out, or returns an unexpected HTTP status."""


class EverythingMoeNotFoundError(EverythingMoeError):
    """Raised when a requested resource returns HTTP 404."""


class EverythingMoeParseError(EverythingMoeError):
    """Raised when HTML or JSON parsing fails unexpectedly."""
