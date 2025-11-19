"""
A module to enable reading, writing, and interacting with surface data containing multiple color channels in napari.
"""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._reader import napari_get_reader, read_surface, reader_function
from ._sample_data import stanford_bunny
from ._widget import DynamicComboBox, SurfaceChannelChange
from ._writer import write_multiple, write_single_surface

__all__ = (
    "napari_get_reader",
    "reader_function",
    "read_surface",
    "write_single_surface",
    "write_multiple",
    "SurfaceChannelChange",
    "DynamicComboBox",
    "stanford_bunny",
)
