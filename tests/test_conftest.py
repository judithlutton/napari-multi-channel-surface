"""Test fixtures in conftest.py"""

from pathlib import Path

import meshio
import numpy as np
import pytest


@pytest.mark.parametrize(
    "simple_mesh",
    [["triangle"], ["triangle", "line"], ["line", "triangle", "quad"]],
    indirect=True,
)
def test_simple_mesh_write_read(tmp_path: Path, simple_mesh: meshio.Mesh):
    """Confirm that the `simple_mesh` fixture can be written and read correctly with `meshio`."""
    # Save test mesh data
    mesh_file = tmp_path.joinpath("test-mesh.ply")
    simple_mesh.write(mesh_file)

    # Read mesh data
    mesh_in = meshio.read(mesh_file)

    np.testing.assert_allclose(simple_mesh.points, mesh_in.points)
    assert len(simple_mesh.cells) == len(mesh_in.cells)
    for cell in simple_mesh.cells:
        cell_type = cell.type
        cell_found = False
        for cell_in in mesh_in.cells:
            if cell_in.type == cell_type:
                assert np.all(cell.data == cell_in.data)
                cell_found = True
                break
        assert cell_found
