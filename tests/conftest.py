"""Shared fixtures for all tests."""

import meshio
import numpy as np
import pytest

cell_type_dim = {"line": 2, "triangle": 3, "quad": 4}


@pytest.fixture
def simple_mesh(request):
    """A simple mesh fixture to test reading and writing."""
    points = [[0, 0, 0], [0, 20, 20], [10, 0, 0], [10, 10, 10]]
    cell_types = getattr(request, "param", ["triangle"])

    cells: list[tuple[str, list[np.ndarray]]] = []
    for s in cell_types:
        d = cell_type_dim[s]
        cells += [(s, [np.arange(d) + i for i in range(5 - d)])]
    return meshio.Mesh(points, cells)
