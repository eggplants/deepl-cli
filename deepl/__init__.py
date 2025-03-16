__version__ = "1.0.0"

from .deepl import DeepLCLI, DeepLCLIError, DeepLCLIPageLoadError

__all__ = ("DeepLCLI", "DeepLCLIError", "DeepLCLIPageLoadError")
