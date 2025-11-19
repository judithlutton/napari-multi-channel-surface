"""
Surface writer for saving multi-channel point data stored in `metadata['point_data']`.

It implements the Writer specification.
see: https://napari.org/stable/plugins/building_a_plugin/guides.html#writers
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

import meshio
import numpy as np
from pandas import DataFrame

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = tuple[DataType, dict, str]


def write_single_surface(path: str | Path, data: Any, meta: dict) -> list[str]:
    """Write a single ``Surface`` layer.

    Parameters
    ----------
    path : str or Path
        A path indicating where to save the image file.
    data : tuple
        Must have vertex locations at ``data[0]``, with shape ``(N,3)``, and
        (triangular) faces at ``data[1]``, with shape ``(M,3)``
    meta : dict
        A dictionary containing all other attributes from the ``Surface`` layer.
        Channels must be located in ``meta['metadata']['point_data']`` as a ``pandas`` ``DataFrame``

    Returns
    -------
    list of str :
        A ``list`` containing a single string representing the path to the saved file.

    See Also
    --------
    write_multiple, napari.layers.Surface
    """
    cells = [("triangle", np.array(data[1]))]
    mesh = meshio.Mesh(data[0], cells=cells)
    if "metadata" in meta and "point_data" in meta["metadata"]:
        point_data = meta["metadata"]["point_data"]
        if (
            isinstance(point_data, DataFrame)
            and point_data.shape[0] == data[0].shape[0]
        ):
            for k in point_data.columns:
                mesh.point_data[k] = np.array(point_data[k])
    mesh.write(path)

    # return path to any file(s) that were successfully written
    return [str(path)]


def write_multiple(path: str, data: list[FullLayerData]) -> list[str]:
    """Write multiple Surface layers.

    Parameters
    ----------
    path : str
        A string path indicating the directory in which to save the data file(s).
    data : list of tuple
        each ``tuple`` has the form ``(data, meta, layer_type)``,
        where
        ``data = (points, cells)`` contains vertex coordinates (``points``) and faces (``cells``);
        ``meta`` is a ``dict`` containing metadata attributes;
        and ``layer_type`` is a string.
        Channel data must be stored as a ``pandas`` ``DataFrame`` in
        ``meta['metadata']['point_data']``.
        All entries with ``layer_type != 'surface'`` are ignored.

    Returns
    -------
    list of str :
        A ``list`` containing (potentially multiple) string paths to the saved file(s).

    See Also
    --------
    write_single_surface, napari.layers.Surface
    """

    out_dir = Path(path)
    if out_dir.is_file():
        # Not allowing multi-surface files at this point.
        return []

    output_files = []
    output_args = []
    # Identify relevant layers and assign output paths
    for layer in data:
        layer_data, meta, layer_type = layer
        if layer_type == "surface":
            # Correct data type, can write
            name = meta.get("name", "mesh0.vtu")
            mesh_file = out_dir.joinpath(name)
            if mesh_file.suffix == "":
                # Apply an appropriate suffix
                mesh_file = out_dir.joinpath(f"{mesh_file.stem}.vtu")
            if mesh_file in output_files:
                # Avoid overwriting current dataset
                number_match = re.match(r".*[\D](\d+)", mesh_file.stem)
                if number_match is None:
                    # Previous file has no number suffix, start counting at 0
                    mesh_file = out_dir.joinpath(
                        f"{mesh_file.name}0{mesh_file.suffix}"
                    )
                else:
                    # Number suffix found, start counting at the next integer
                    current_str = number_match.group(1)
                    name_base = mesh_file.stem[: -len(current_str)]
                    next_number = int(current_str) + 1
                    mesh_file = out_dir.joinpath(
                        f"{name_base}{next_number}{mesh_file.suffix}"
                    )
                    while mesh_file in output_files:
                        next_number += 1
                        mesh_file = out_dir.joinpath(
                            f"{name_base}{next_number}{mesh_file.suffix}"
                        )
            output_files.append(mesh_file)
            output_args.append((mesh_file, layer_data, meta))

    output_paths = []
    out_dir.mkdir(exist_ok=True)
    # write output files
    for mesh_file, layer_data, meta in output_args:
        mesh_path = write_single_surface(mesh_file, layer_data, meta)
        output_paths.extend(mesh_path)
    # return path to any file(s) that were successfully written
    return output_paths
