from importlib import metadata
from typing import List

from langchain_bocha.bocha_search import BochaSearch
from langchain_bocha.schemas import (
    ImageValue,
    QueryContext,
    SearchResponse,
    VideoValue,
    WebPageValue,
    WebSearchImages,
    WebSearchVideos,
    WebSearchWebPages,
)

try:
    __version__: str = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__: List[str] = [
    "BochaSearch",
    "SearchResponse",
    "WebPageValue",
    "WebSearchWebPages",
    "ImageValue",
    "VideoValue",
    "WebSearchImages",
    "WebSearchVideos",
    "QueryContext",
    "__version__",
]
