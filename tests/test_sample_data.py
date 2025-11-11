# from napari_multi_channel_surface import make_sample_data

import numpy as np

from napari_multi_channel_surface._sample_data import stanford_bunny


def test_sample_data():
    """Test that sample data conforms to the napari LayerData list specification and has coordinate values in point_data."""
    mesh = stanford_bunny()[0]
    # Confirm LayerData tuple (data,meta,layer_type)
    assert isinstance(mesh, tuple)
    assert len(mesh) == 3
    assert isinstance(mesh[0], tuple)
    assert isinstance(mesh[1], dict)
    assert mesh[2] == "surface"
    # Confirm presence of point data
    assert "metadata" in mesh[1]
    assert "point_data" in mesh[1]["metadata"]
    # Sample data surface has mesh coordinates for point data
    point_data = mesh[1]["metadata"]["point_data"]
    points = mesh[0][0]
    for i, c in enumerate(["X", "Y", "Z"]):
        assert c in point_data.columns
        np.testing.assert_allclose(point_data[c], points[:, i])
