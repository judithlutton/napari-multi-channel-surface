"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/stable/plugins/building_a_plugin/guides.html#readers
"""

from collections.abc import Callable
from pathlib import Path

import meshio
import numpy as np
from pandas import DataFrame


def napari_get_reader(path: str | Path | list[str | Path]) -> Callable:
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # we assume that if one path is readable, then all are readable.
        path = path[0]
    path = Path(path)
    # if we know we cannot read the file, we immediately return None.
    if path.suffix not in meshio.extension_to_filetypes:
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths to valid surface files and return a list of
    LayerData tuples representing those surfaces.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        `(data, meta_kwargs, layer_type)`, where `data=(points,cells)` contains vertex coordinates and surface faces;
        `meta_kwargs` is a `dict`, containing the key `features` if point data is read,
        `meta_kwargs['metadata']` being a `dict` mapping channel names to color values;
        and `layer_type='surface'`.
    """
    # handle both a string and a list of strings
    paths = path if isinstance(path, list) else [path]
    # Read all data
    layer_data = [surface_reader(p) for p in paths]
    return layer_data


def surface_reader(path):
    """Read surface data and return as a LayerData object

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [meta_kwargs, [layer_type]]), "meta_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or os.PathLike
        Path to file.

    Returns
    -------
    layer_data : tuple
        A tuple conforming to the napari LayerData tuple specification, in the form
            `(data, meta_kwargs, layer_type)`.
        Here, `data=(points,cells)` contains vertex coordinates and surface faces;
        `meta_kwargs` is a `dict`, containing the key `metadata` if point data is read,
        `meta_kwargs['features']` being a `dict` mapping channel names to color values;
        and `layer_type='surface'`.
    """
    # TODO: use try/except to catch read errors
    try:
        mesh = meshio.read(path)
    except SystemExit as exc:
        raise RuntimeError(
            "Surface file is not in a readable format."
        ) from exc

    points = mesh.points
    cells = np.array([])
    for cell in mesh.cells:
        if cell.type == "triangle":
            cells = cell.data
            break
    # TODO: account for the possibility of meshio cell types that can act as faces but aren't triangles.
    # TODO: (optional) allow points if no cell lists are triangles
    data = (points, cells)

    # kwargs used by viewer.add_surface() during layer creation
    meta_kwargs = {}
    if len(mesh.point_data) > 0:
        # store point_data as the metadata item `'point_data'`
        meta_kwargs["metadata"] = {}
        meta_kwargs["metadata"]["point_data"] = DataFrame(mesh.point_data)

    layer_type = "surface"
    return (data, meta_kwargs, layer_type)
