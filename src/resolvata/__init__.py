"""Related data asset path resolving."""

__all__ = ["PathResolverABC", "LocalResolver"]

from ._abc import PathResolverABC
from ._local import LocalResolver
