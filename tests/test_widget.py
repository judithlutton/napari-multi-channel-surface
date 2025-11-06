import numpy as np

from napari_multi_channel_surface._widget import SurfaceChannelChange


def test_surface_channel_change_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
    cells = np.array([[0, 1, 2], [1, 2, 3]])
    point_data = {f"data{i}": np.arange(len(points)) + i for i in range(2)}
    # surface_data = (points,cells)
    layer = viewer.add_surface((points, cells), features=point_data)
    scc_widget = SurfaceChannelChange(viewer)

    # Set the widget value to the current surface layer
    scc_widget._surface_layer_combo.value = layer
    # Confirm that channel lists have been updated
    assert list(scc_widget._channel_selector.choices) == list(point_data)

    # Confirm that the channel selector does indeed change the value
    for channel_name in point_data:
        scc_widget._channel_selector.value = channel_name

        # Confirm that the layer vertex data is updated
        assert np.all(layer.vertex_values == point_data[channel_name])
