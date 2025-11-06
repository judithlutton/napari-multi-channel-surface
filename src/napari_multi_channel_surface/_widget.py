"""
This module provides a widget to change the channels in a `napari.layers.Surface` object.
Here, channels are assumed to be stored in `Surface.metadata['point_data'].

References:
- Widget specification: https://napari.org/stable/plugins/building_a_plugin/guides.html#widgets
- magicgui docs: https://pyapp-kit.github.io/magicgui/
"""

from typing import TYPE_CHECKING

from magicgui.widgets import Container, RadioButtons, create_widget
from napari.layers import Surface

if TYPE_CHECKING:
    import napari


class SurfaceChannelChange(Container):
    """Container widget with widgets and their callbacks for changing surface channels.

    Parameters
    ----------
    viewer : napari.viewer.Viewer
        The Viewer object to which the widget is attached.
    """

    def __init__(self, viewer: "napari.viewer.Viewer") -> None:
        super().__init__()
        self._viewer = viewer
        # TODO: determine if _channels is really useful here
        self._channels: list[str] = []
        # use create_widget to generate widgets from type annotations
        self._surface_layer_combo = create_widget(
            label="Surface", annotation="napari.layers.Surface"
        )
        # Selection widget
        self._channel_selector = RadioButtons()
        self._surface_layer_combo.changed.connect(self._on_change_surface)
        self._channel_selector.changed.connect(self._on_change_channel)
        self._viewer.layers.events.connect(self._on_layers_changed)
        # append into/extend the container with your widgets
        self.extend(
            [
                self._surface_layer_combo,
                self._channel_selector,
            ]
        )
        if len(viewer.layers) > 0:
            self._on_layers_changed(None)
            self._on_change_surface(self._surface_layer_combo.value)

    def _on_layers_changed(self, event):
        """Callback for the event of the layers in `_viewer` changing.

        Parameters
        ----------
        event : napari.events.Event
            change event triggered by adding, removing, or replacing a layer in `_viewer`.

        Notes
        -----
        Implementation finds all `napari.layers.Surface` layer object in `_viewer.layers`
        from scratch each time a change event is triggered.
        Since these events involve loading/unloading data, it is unlikely
        that the inefficiency of this approach will be noticeable. Alternatives would require handling
        each event type separately, and could become more dependent on the LayerList representation.
        For the same reasons, there is no distinction drawn between changing and changed events,
        so when a layer is added, removed, or replaced, the function is called twice.
        """
        self._surface_layer_combo.choices = [
            x for x in self._viewer.layers if type(x) is Surface
        ]

    def _on_change_surface(self, surface_layer: Surface | None):
        """Callback for the event of a new surface layer being selected in `_surface_layer_combo`.

        Updates the choices of channels from the new surface layer selection.

        Parameters
        ----------
        surface_layer : napari.layers.Surface
            The selected `Surface` object
        """
        current_channel = self._channel_selector.value
        self._channels = []
        if (
            surface_layer is not None
            and "point_data" in surface_layer.metadata
        ):
            n_points = surface_layer.vertices.shape[0]
            point_data = surface_layer.metadata["point_data"]
            if point_data.shape[0] == n_points:
                self._channels = list(point_data.columns)
        self._channel_selector.choices = self._channels
        if current_channel in self._channels:
            self._channel_selector.value = current_channel

    def _on_change_channel(self, channel_name):
        """Callback for the event of a new channel being selected in `_channel_selector`.

        Updates the `vertex_values` attribute of the `Surface` object.

        Parameters
        ----------
        channel_name : str
            The selected channel to be displayed.
        """
        surface_layer = self._surface_layer_combo.value
        if surface_layer is None:
            return
        point_data = surface_layer.metadata["point_data"]
        if channel_name in point_data:
            surface_layer.vertex_values = point_data[channel_name]
