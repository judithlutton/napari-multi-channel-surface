.. napari-multi-channel-surface documentation master file, created by
   sphinx-quickstart on Tue Nov 18 17:07:57 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

napari-multi-channel-surface documentation
==========================================

napari-multi-channel-surface is a plugin for the open source bioimaging software napari, and is intended for use in napari.
The goal of this plugin is to provide a means for reading, writing, and interacting with surfaces containing
multiple color channels in napari_. When reading, color channel data is imported into the :code:`napari.layers.Surface` object
metadata under the key :code:`point_data`. Different channels can be used to color the surface in the napari_ viewer using the 'Channel Select'
widget supplied with this plugin.
Multi-channel surfaces are saved using the `point_data` metadata key to save each named channel.

Check out the :doc:`usage` section for further information, including how to
:ref:`install <installation>` the project.

.. figure:: images/bunny_x_screenshot.png
   :alt: A screenshot of the napari viewer showing the Channel Select widget in use, showing the stanford bunny colored by its x-coordinate.

   Example use of the Channel Select widget.
   The sample data provided with napari-multi-channel-surface includes the stanford bunny with color channels for each cartesian coordinate.
   Each channel can be selected in turn, to show the data distribution on the surface.
   Here we have chosen the channel 'X', and when displayed shows the colormap representation of the
   x-coordinate of each vertex on the bunny's surface.

.. _napari: https://github.com/napari/napari

.. note::

   This project is under active development.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   modules
