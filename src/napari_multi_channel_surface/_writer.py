"""
This module is an example of a barebones writer plugin for napari.

It implements the Writer specification.
see: https://napari.org/stable/plugins/building_a_plugin/guides.html#writers

Replace code below according to your needs.
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
    """Writes a single surface layer.

    Parameters
    ----------
    path : str
        A string path indicating where to save the image file.
    data : The layer data
        The `.data` attribute from the napari layer.
    meta : dict
        A dictionary containing all other attributes from the napari layer
        (excluding the `.data` layer attribute).

    Returns
    -------
    [path] : A list containing the string path to the saved file.
    """

    # Surface layer data = (vertices,faces)
    cells = [("triangle", np.array(data[1]))]
    mesh = meshio.Mesh(data[0], cells=cells)
    if "point_data" in meta:
        point_data = meta["point_data"]
        if (
            isinstance(point_data, DataFrame)
            and point_data.shape[0] == data[0].shape[0]
        ):
            for k in point_data.columns:
                mesh.point_data[k] = point_data[k]
    mesh.write(path)

    # return path to any file(s) that were successfully written
    return [str(path)]


def write_multiple(path: str, data: list[FullLayerData]) -> list[str]:
    """Writes multiple layers of different types.

    Parameters
    ----------
    path : str
        A string path indicating where to save the data file(s).
    data : A list of layer tuples.
        Tuples contain three elements: (data, meta, layer_type)
        `data` is the layer data
        `meta` is a dictionary containing all other metadata attributes
        from the napari layer (excluding the `.data` layer attribute).
        `layer_type` is a string, eg: "image", "labels", "surface", etc.

    Returns
    -------
    [path] : A list containing (potentially multiple) string paths to the saved file(s).
    """

    out_dir = Path(path)
    if out_dir.is_file():
        # Not allowing multi-surface files at this point.
        return []

    output_files = []
    output_data = []
    for layer in data:
        data, meta, layer_type = layer
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
                    mesh_file = out_dir.joinpath(
                        f"{mesh_file.name}0{mesh_file.suffix}"
                    )
                else:
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
            output_data.append((data, meta))

    output_paths = []
    out_dir.mkdir(exist_ok=True)
    for mesh_file, layer_data in zip(output_files, output_data, strict=True):
        data, meta = layer_data
        mesh_path = write_single_surface(mesh_file, data, meta)
        output_paths.extend(mesh_path)
    # return path to any file(s) that were successfully written
    return output_paths
