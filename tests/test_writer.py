from pathlib import Path

import meshio
import numpy as np

from napari_multi_channel_surface import write_multiple, write_single_surface


def test_write_single(tmp_path, simple_mesh):
    mesh_file = tmp_path.joinpath("mesh.vtu")
    data = (simple_mesh.points, simple_mesh.cells[0].data)
    meta = {}
    output_path = write_single_surface(mesh_file, data, meta)
    assert output_path[0] == str(mesh_file)
    saved_mesh = meshio.read(mesh_file)
    np.testing.assert_allclose(saved_mesh.points, simple_mesh.points)
    np.testing.assert_array_equal(
        saved_mesh.cells[0].data, simple_mesh.cells[0].data
    )


def test_write_multiple(tmp_path, simple_mesh):
    mesh_dir = tmp_path.joinpath("mesh/")
    layer_data = [
        (
            (simple_mesh.points + k, simple_mesh.cells[0].data[k:]),
            {},
            "surface",
        )
        for k in range(2)
    ]
    output_paths = write_multiple(mesh_dir, layer_data)
    assert output_paths[0] != output_paths[1]

    for p, layer in zip(output_paths, layer_data, strict=True):
        assert Path(p).parent == mesh_dir
        saved_mesh = meshio.read(p)
        np.testing.assert_allclose(saved_mesh.points, layer[0][0])
        np.testing.assert_array_equal(saved_mesh.cells[0].data, layer[0][1])
