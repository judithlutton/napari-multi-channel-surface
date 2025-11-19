"""
This module contains reader functions to load surfaces and color data into napari.
"""

from collections.abc import Callable
from pathlib import Path

import meshio
import numpy as np
from pandas import DataFrame

from ._constants import _FILE_EXTENSIONS


def napari_get_reader(path: str | Path | list[str | Path]) -> Callable | None:
    """Get a reader function able to read single or multiple surfaces with channel data.

    Parameters
    ----------
    path : str or Path or list of str or list of Path
        Path to file, or list of paths.

    Returns
    -------
    Callable or None
        A function that reads all valid input paths in ``path``, or ``None``
        if no valid input paths can be found.

    See Also
    --------
    reader_function : function returned by ``napari_get_reader``.
    read_surface : function used by ``reader_function`` to read individual surfaces.

    Notes
    -----
    This function conforms to the 'reader contribution' specification for napari.
    For details of this specification, see:
    https://napari.org/stable/plugins/building_a_plugin/guides.html#readers
    """
    # Implementation extension for future commit
    # valid_path_found = False
    # if isinstance(path, list):
    #     # Check all paths to ensure that at least one is readable
    #     for p in path:
    #         if Path(p).suffix in _FILE_EXTENSIONS:
    #             valid_path_found = True
    #             break
    # else:
    #     valid_path_found = Path(path).suffix in _FILE_EXTENSIONS
    # return reader_function if valid_path_found else None
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # we assume that if one path is readable, then all are readable.
        path = path[0]
    path = Path(path)
    # if we know we cannot read the file, we immediately return None.
    if path.suffix not in _FILE_EXTENSIONS:
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of
    ``LayerData`` ``tuple`` s representing surfaces read from the input path(s).

    Parameters
    ----------
    path : str or Path or list of str or list of Path
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuple
        A ``list`` of ``LayerData`` ``tuple`` s where each tuple in the list is of the form
        ``(data, meta_kwargs, layer_type)``.

    See Also
    --------
    read_surface : function called to read each input surface.
    """
    # handle both a string and a list of strings
    paths = path if isinstance(path, list) else [path]
    # Read all data
    layer_data = [read_surface(p) for p in paths]
    return layer_data


def read_surface(path):
    """Read surface data and return as a ``LayerData`` ``tuple``

    A ``LayerData`` ``tuple``
    is given by

        ``(data, meta_kwargs, layer_type)``,

    where, for ``Surface`` layers,
    ``data = (points, cells)`` contains vertex coordinates (``points``)
    and vertex indices forming the corners of each mesh face (``cells``);
    ``meta_kwargs`` is a ``dict``;
    and ``layer_type = 'surface'``.
    If point data is read, it is stored as a ``DataFrame`` in
    ``meta_kwargs['metadata']['point_data']``, otherwise ``meta_kwargs`` is empty.

    Parameters
    ----------
    path : str or Path
        Path to file.

    Returns
    -------
    layer_data : tuple
        A tuple conforming to the napari LayerData tuple specification, in the form
        ``(data, meta_kwargs, layer_type)``.

    Raises
    ------
    RuntimeError :
        If an error occurred while attempting to read the file from disk.

    See Also
    --------
    napari.layers.Surface
    """
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
    data = (points, cells)

    # kwargs used by viewer.add_surface() during layer creation
    meta_kwargs = {}
    n_points = points.shape[0]
    if len(mesh.point_data) > 0:
        # store point_data as the metadata item ``'point_data'```
        point_data = {}
        for k in mesh.point_data:
            if mesh.point_data[k].size == n_points:
                # Force to be 1D to fit DataFrame specification
                point_data[k] = mesh.point_data[k].flatten()
            elif (
                mesh.point_data[k].shape[0] == n_points
                and len(mesh.point_data[k].shape) == 2
            ):
                # 2D array, split into channels
                n_channels = mesh.point_data[k].shape[1]
                # TODO: make more robust by checking that no other channels have the given set of names
                for i in range(n_channels):
                    point_data[f"{k}_C{i}"] = mesh.point_data[k][:, i]

        meta_kwargs["metadata"] = {"point_data": DataFrame(point_data)}

    layer_type = "surface"
    return (data, meta_kwargs, layer_type)
