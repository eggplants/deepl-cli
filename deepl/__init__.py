""".. include:: ../README.md"""  # noqa: D415

import importlib.metadata

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

from .deepl import DeepLCLI, DeepLCLIError, DeepLCLIPageLoadError

__all__ = ("DeepLCLI", "DeepLCLIError", "DeepLCLIPageLoadError")
