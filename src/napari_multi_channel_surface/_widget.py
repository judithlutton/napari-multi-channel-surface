"""
This module provides a widget to change the channels in a `napari.layers.Surface` object.
Here, channels are assumed to be stored in `Surface.metadata['point_data'].

References:
- Widget specification: https://napari.org/stable/plugins/building_a_plugin/guides.html#widgets
- magicgui docs: https://pyapp-kit.github.io/magicgui/
"""

from typing import TYPE_CHECKING

import magicgui.widgets as widgets
import numpy as np
from napari.utils import notifications

if TYPE_CHECKING:
    import napari

# TODO: consider if layer interaction is better handled through built-in selection.
# TODO: multi-channel colors


class SurfaceChannelChange(widgets.Container):
    """Container widget with widgets and their callbacks for changing surface channels.

    Parameters
    ----------
    viewer : napari.viewer.Viewer
        The Viewer object to which the widget is attached.
    """

    def __init__(self, viewer: "napari.viewer.Viewer") -> None:
        super().__init__()
        self._viewer = viewer
        # use create_widget to generate widgets from type annotations
        self._surface_layer_combo = DynamicComboBox(
            label="Surface", annotation="napari.layers.Surface"
        )
        # Selection widget
        self._channel_selector = DynamicComboBox(label="Channel")
        # assign callbacks
        # Update surface list on any change in the viewer layers
        self._viewer.layers.events.connect(self._on_layers_changed)
        # update channel list when surface changes
        self._surface_layer_combo.changed.connect(self._on_change_surface)
        # update surface representation when channel changes
        self._channel_selector.changed.connect(self._on_change_channel)
        # append into/extend the container with your widgets
        self.extend(
            [
                self._surface_layer_combo,
                self._channel_selector,
            ]
        )
        self._on_layers_changed(None)
        self._on_change_surface(self._surface_layer_combo.value)

        self.native_parent_changed.connect(
            lambda x: notifications.show_debug(
                f"Widget parent changed. Backend: {x}"
            )
        )

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
        # TODO: control selected value
        # TODO: update channel selector
        if event is None:
            notifications.show_debug("Creating surface layer list")
        elif str(event.type) in [
            "inserted",
            "removed",
            "moved",
            "changed",
            "reordered",
        ]:
            notifications.show_debug(
                f"Updating surface layer list in response to {event.type}"
            )
        else:
            notifications.show_debug(
                f"Ignoring surface layer event {event.type}"
            )
            return
        surface_list = [
            x for x in self._viewer.layers if type(x).__name__ == "Surface"
        ]
        self._surface_layer_combo.choices = surface_list
        if len(surface_list) == 0:
            # no surfaces present: clear channel widget
            self._on_change_surface(None)

    def _on_change_surface(
        self, surface_layer: "napari.layers.Surface | None"
    ):
        """Callback for the event of a new surface layer being selected in `_surface_layer_combo`.

        Updates the choices of channels from the new surface layer selection.

        Parameters
        ----------
        surface_layer : napari.layers.Surface
            The selected `Surface` object
        """
        notifications.show_debug("Selected surface changed")
        current_channel = (
            self._channel_selector.value
            if len(self._channel_selector.choices) > 0
            else None
        )
        channels = ()
        if (
            surface_layer is not None
            and "point_data" in surface_layer.metadata
        ):
            # Surface layer contains point_data.
            n_points = surface_layer.vertices.shape[0]
            point_data = surface_layer.metadata["point_data"]
            if np.shape(point_data)[0] == n_points:
                # Point data is in the correct format
                channels = tuple(point_data.columns)
        self._channel_selector.choices = channels
        if current_channel in channels and current_channel is not None:
            self._channel_selector.value = current_channel

    def _on_change_channel(self, channel_name):
        """Callback for the event of a new channel being selected in `_channel_selector`.

        Updates the `vertex_values` attribute of the `Surface` object.

        Parameters
        ----------
        channel_name : str
            The selected channel to be displayed.
        """
        notifications.show_debug("Selected channel changed")
        surface_layer = self._surface_layer_combo.value
        if surface_layer is None:
            return
        point_data = surface_layer.metadata["point_data"]
        notifications.show_debug(f"{channel_name=}")
        if channel_name in point_data:
            surface_layer.vertex_values = np.array(point_data[channel_name])
        else:
            notifications.show_warning(
                f"Point data {channel_name} not found in Surface {surface_layer}. No changes made."
            )


class DynamicComboBox(widgets.ComboBox):
    """ComboBox Widget (dropdown menu) for selecting channels with dynamic updating of choices.

    Notes
    -----
    This is a small extension of the ComboBox widget to allow dynamic
    updating of choices.
    A `Container` object can reset values of all children in response to interactions with
    napari.
    To counter this, we initialize `choices` with a function that returns the `choices` property.
    This function is set as the default choices function, so `reset_choices` does nothing.
    """

    def __init__(self, **kwargs):
        choices = kwargs.pop("choices") if "choices" in kwargs else ()
        super().__init__(choices=self._return_choices, **kwargs)
        self.choices = choices

    def _return_choices(
        self, widget: widgets.bases.CategoricalWidget
    ) -> tuple:
        return self.choices
