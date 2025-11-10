import numpy as np
import pytest
from pandas import DataFrame

from napari_multi_channel_surface._widget import (
    DynamicComboBox,
    SurfaceChannelChange,
)


def test_surface_channel_change_widget(make_napari_viewer):
    """Confirm that the `SurfaceChannelChange` widget functions as expected when opened
    with existing surface layer present.

    Tests run:
    * current layer selected on openning
    * channel options list is correct
    * channel change widget updates the vertex_values
    """
    viewer = make_napari_viewer()
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
    cells = np.array([[0, 1, 2], [1, 2, 3]])
    point_data = DataFrame(
        {f"data{i}": np.arange(len(points)) + i for i in range(2)}
    )
    layer = viewer.add_surface(
        (points, cells), metadata={"point_data": point_data}
    )
    scc_widget = SurfaceChannelChange(viewer)

    # Confirm that the layer is selected
    assert scc_widget._surface_layer_combo.value == layer
    # Confirm that channel lists are correct
    assert list(scc_widget._channel_selector.choices) == list(
        point_data.columns
    )

    # Confirm that the channel selector does indeed change the value
    for channel_name in point_data.columns:
        scc_widget._channel_selector.value = channel_name
        print(f"{point_data=}")
        print(f"{layer.vertex_values=}")
        # Confirm that the layer vertex data is updated
        assert np.all(layer.vertex_values == point_data[channel_name])


def test_surface_channel_change_widget_multisurface(make_napari_viewer):
    """Confirm that the `SurfaceChannelChange` widget functions as expected when multiple
    surfaces are added"""
    viewer = make_napari_viewer()
    layers = []
    layer_names = []
    for k in range(2):
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
        cells = np.array([[0, 1, 2], [1, 2, 3]])
        point_data = DataFrame(
            {f"data{i + k}": np.arange(len(points)) + i for i in range(2)}
        )
        layers.append(
            viewer.add_surface(
                (points, cells), metadata={"point_data": point_data}
            )
        )
        layer_names.append(list(point_data.columns))
    scc_widget = SurfaceChannelChange(viewer)
    # Confirm that the layer is selected
    print(scc_widget._surface_layer_combo.choices)
    assert list(scc_widget._surface_layer_combo.choices) == layers
    for k in range(2):
        scc_widget._surface_layer_combo.value = layers[k]
        # Confirm that channel lists update correctly
        print(scc_widget._channel_selector.choices)
        assert list(scc_widget._channel_selector.choices) == layer_names[k]


@pytest.mark.parametrize("init_choices", [(), ("a",)])
def test_dynamic_combo_box(init_choices):
    """Confirm that the DynamicComboBox class behaves like a ComboBox that does not reset."""
    choices = ("a", "b")
    if len(init_choices) == 0:
        # Default choices = ()
        combo_box = DynamicComboBox()
    else:
        combo_box = DynamicComboBox(choices=init_choices)
    # Test 1: DynamicComboBox.__init__ behaves like ComboBox.__init__
    assert combo_box.choices == init_choices
    combo_box.choices = choices
    combo_box.reset_choices()
    # Test 2: DynamicComboBox choices don't reset
    assert combo_box.choices == choices
