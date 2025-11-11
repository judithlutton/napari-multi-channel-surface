import os
from pathlib import Path

import meshio
import numpy as np
import pytest
import pyvista as pv
from pandas import DataFrame

from napari_multi_channel_surface import napari_get_reader
from napari_multi_channel_surface._reader import read_surface

# cell_type_dim = {"line": 2, "triangle": 3, "quad": 4}
point_data_file_types = [".ply", ".vtk", ".vtu"]
no_point_data_file_types = [".stl", ".vol"]
suffix_list = point_data_file_types + no_point_data_file_types


# TODO: specify params on test-by-test basis to avoid running unnecessary tests.
# @pytest.fixture(
#     params=[["triangle"], ["triangle", "line"], ["line", "triangle", "quad"]]
# )
# def simple_mesh(request):
#     """A simple mesh fixture to test reading and writing."""
#     points = [[0, 0, 0], [0, 20, 20], [10, 0, 0], [10, 10, 10]]
#     cell_types = getattr(request,'param',['triangle'])

#     cells: list[tuple[str, list[np.ndarray]]] = []
#     for s in cell_types:
#         d = cell_type_dim[s]
#         cells += [(s, [np.arange(d) + i for i in range(5 - d)])]
#     return meshio.Mesh(points, cells)


# def test_simple_mesh(tmp_path: Path, simple_mesh: meshio.Mesh):
#     """Confirm that the `simple_mesh` fixture can be written and read correctly with `meshio`."""
#     # Save test mesh data
#     mesh_file = tmp_path.joinpath("test-mesh.ply")
#     simple_mesh.write(mesh_file)

#     # Read mesh data
#     mesh_in = meshio.read(mesh_file)

#     np.testing.assert_allclose(simple_mesh.points, mesh_in.points)
#     assert len(simple_mesh.cells) == len(mesh_in.cells)
#     for cell in simple_mesh.cells:
#         cell_type = cell.type
#         cell_found = False
#         for cell_in in mesh_in.cells:
#             if cell_in.type == cell_type:
#                 assert np.all(cell.data == cell_in.data)
#                 cell_found = True
#                 break
#         assert cell_found


@pytest.mark.parametrize(
    "simple_mesh,suffix",
    [(["triangle"], suffix) for suffix in suffix_list]
    + [(["line", "triangle"], ".vtu")],
    indirect=["simple_mesh"],
)
def test_surface_reader(tmp_path: Path, simple_mesh: meshio.Mesh, suffix: str):
    """Test the `surface_reader` function, which reads a single surface file.

    The output is of the form `(data, metadata, layer_type)`, where
    `data` is a 2-tuple of the form `(vertices, faces)`;
    `metadata` is a dict providing options to `viewer.add_surface()`; and
    `layer_type` is a str set to `'surface'`.
    """

    # Get cells relevant to napari
    triangles = []
    for cell in simple_mesh.cells:
        if cell.type == "triangle":
            triangles = cell.data

    # Save test mesh data
    mesh_file = os.path.join(tmp_path, "test-mesh" + suffix)
    simple_mesh.write(mesh_file)

    # Read mesh data
    layer_data = read_surface(mesh_file)

    # test layer data format
    assert len(layer_data) == 3
    assert isinstance(layer_data[1], dict)
    assert layer_data[2] == "surface"

    # test data content
    data = layer_data[0]
    assert len(data) in (2, 3)
    np.testing.assert_allclose(simple_mesh.points, data[0])
    assert np.all(data[1] == triangles)


@pytest.mark.parametrize(
    "suffix,n_channels",
    [(s, n) for s in point_data_file_types for n in [1, 5]],
)
def test_surface_reader_point_data(
    tmp_path: Path, simple_mesh: meshio.Mesh, suffix: str, n_channels: int
):
    """Test how reader function handles files with point data."""
    # add some point data to the mix
    for n in range(n_channels):
        simple_mesh.point_data[f"data{n}"] = (
            np.arange(simple_mesh.points.shape[0]) + n
        )
    data_names = list(simple_mesh.point_data.keys())

    # Save test mesh data
    mesh_file = os.path.join(tmp_path, "test-mesh" + suffix)
    simple_mesh.write(mesh_file)

    # Read test mesh data
    mesh_data = read_surface(mesh_file)
    layer_data, layer_attributes, _ = mesh_data

    # Confirm that metadata is one of the read attributes
    assert "metadata" in layer_attributes
    assert isinstance(layer_attributes["metadata"], dict)

    # Confirm that point_data has been read
    assert "point_data" in layer_attributes["metadata"]

    point_data = layer_attributes["metadata"]["point_data"]
    assert isinstance(point_data, DataFrame)

    for name in data_names:
        assert name in point_data
        np.all(simple_mesh.point_data[name] == point_data[name])


def test_surface_reader_point_data_rgb(
    tmp_path: Path, simple_mesh: meshio.Mesh
):
    """Test how reader function handles files with RGB point data."""
    n_points = simple_mesh.points.shape[0]
    # Add RGB data to mesh
    simple_mesh.point_data["RGB"] = np.arange(n_points * 3).reshape([-1, 3])
    simple_mesh.point_data["dummy"] = np.zeros(n_points)

    # Save test mesh data
    mesh_file = tmp_path.joinpath("mesh.vtk")
    simple_mesh.write(mesh_file)

    # Read test mesh data
    mesh_data = read_surface(mesh_file)
    layer_attributes = mesh_data[1]

    # Confirm that metadata is one of the read attributes
    assert "metadata" in layer_attributes
    assert isinstance(layer_attributes["metadata"], dict)

    # Confirm that point_data has been read
    assert "point_data" in layer_attributes["metadata"]

    point_data = layer_attributes["metadata"]["point_data"]
    assert isinstance(point_data, DataFrame)

    rgb_columns = [x for x in point_data.columns if x.startswith("RGB")]
    assert len(rgb_columns) == 3
    for i in range(3):
        i_found = False
        for k in rgb_columns:
            if k.endswith(str(i)):
                assert np.all(
                    simple_mesh.point_data["RGB"][:, i] == point_data[k]
                )
                i_found = True
                break
        assert i_found


def test_surface_reader_cell_data():
    """Future functionality test: import cell data."""


def test_reader_function_directory(tmp_path: Path):
    """Future functionality test: import directory."""


# TODO: setup with pyvista
def test_surface_reader_meshio_error(tmp_path: Path):
    """Confirm that `surface_reader` returns the correct exceptions when meshio fails to read."""
    bad_file = tmp_path.joinpath("bad_mesh.vtk")
    with pytest.raises(meshio.ReadError):
        read_surface(bad_file)
    mesh = pv.Sphere()
    mesh.save(bad_file)

    with pytest.raises(RuntimeError):
        read_surface(bad_file)


@pytest.mark.parametrize("suffix", suffix_list)
def test_reader(tmp_path: Path, simple_mesh: meshio.Mesh, suffix: str):
    """Test the reader function satisfies the plugin specification."""
    # Save test mesh data
    mesh_file = tmp_path.joinpath(f"mesh{suffix}")
    simple_mesh.write(mesh_file)

    # Confirm that we get a reader function
    reader = napari_get_reader(mesh_file)
    assert callable(reader)

    # Check data the format is in the form of a LayerData list.
    layer_data_list = reader(mesh_file)
    assert isinstance(layer_data_list, list) and len(layer_data_list) > 0
    layer_data_tuple = layer_data_list[0]
    assert isinstance(layer_data_tuple, tuple) and len(layer_data_tuple) == 3

    # make sure it's the same as it started
    data, kwargs, layer_type = layer_data_tuple
    assert layer_type == "surface"
    saved_points, saved_cells = data
    np.testing.assert_allclose(simple_mesh.points, saved_points)
    np.testing.assert_allclose(simple_mesh.cells[0].data, saved_cells)


def test_get_reader_pass():
    reader = napari_get_reader("fake.file")
    assert reader is None
