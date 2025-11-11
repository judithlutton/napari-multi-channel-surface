try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._reader import napari_get_reader
from ._sample_data import stanford_bunny
from ._widget import SurfaceChannelChange
from ._writer import write_multiple, write_single_surface

__all__ = (
    "napari_get_reader",
    "write_single_surface",
    "write_multiple",
    "stanford_bunny",
    "SurfaceChannelChange",
)
