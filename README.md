# napari-multi-channel-surface

[![License MIT](https://img.shields.io/pypi/l/napari-multi-channel-surface.svg?color=green)](https://github.com/judithlutton/napari-multi-channel-surface/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-multi-channel-surface.svg?color=green)](https://pypi.org/project/napari-multi-channel-surface)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-multi-channel-surface.svg?color=green)](https://python.org)
[![tests](https://github.com/judithlutton/napari-multi-channel-surface/workflows/tests/badge.svg)](https://github.com/judithlutton/napari-multi-channel-surface/actions)
<!---
[![codecov](https://codecov.io/gh/judithlutton/napari-multi-channel-surface/branch/main/graph/badge.svg)](https://codecov.io/gh/judithlutton/napari-multi-channel-surface)
--->
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-multi-channel-surface)](https://napari-hub.org/plugins/napari-multi-channel-surface)
[![npe2](https://img.shields.io/badge/plugin-npe2-blue?link=https://napari.org/stable/plugins/index.html)](https://napari.org/stable/plugins/index.html)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json)](https://github.com/copier-org/copier)

A [napari] plugin to enable easy interaction with multi-channel surfaces

----------------------------------

## Overview

The goal of this plugin is to provide a means for reading, writing, and interacting with surfaces containing
multiple color channels in [napari]. When reading, color channel data is imported into the `napari.layers.Surface` metadata dictionary under the key `'point_data'`. 
Different channels can be used to color the surface in [napari] using the `Channel Select` widget supplied with this plugin. 
Multi-channel surfaces are saved using the `point_data` metadata key to save each named channel.

Visualization of single channel vertex data is made possible in [napari] through the `vertex_values` Surface Layer property,
while the `vertex_colors` property enables RGB and RGBA representations.
Surface file formats such as `'.vtu'` provide the option of storing a variable number of features recorded at each vertex, 
and `napari-multi-channel-surface` provides functionality to utilise data in these formats.

## Installation

### In napari
This plugin was developed for use in the [napari] app. To install the plugin, go to

`Plugins` > `Install/Uninstall Plugins...`

Type `napari-multi-channel-surface` in the search box and click install next to the
entry `napari-multi-channel-surface` in the search results.

### With pip

You can install `napari-multi-channel-surface` via [pip]:

```
pip install napari-multi-channel-surface
```

If napari is not already installed, you can install `napari-multi-channel-surface` with napari and Qt via:

```
pip install "napari-multi-channel-surface[all]"
```


To install latest development version :

```
pip install git+https://github.com/judithlutton/napari-multi-channel-surface.git
```

## Usage

### Reading and writing
Reading and writing mesh files can be performed in [napari] using the read and save functions in the `File` menu.

#### File formats

`napari-multi-channel-surface` uses [meshio] to read and write mesh files, and supports files with the following extensions:
```
['.ply', '.vtk', '.vtu', '.xdmf', '.xmf', '.h5m', '.avs', '.e', '.exo', '.ex2', '.hmf', '.med', '.dat', '.tec']
```
This subset of file types supported by [meshio] can store color channel data.

### Channel Select Widget
You can use the `Channel Select` widget with any data loaded with `napari-multi-channel-surface`. Simply load the surface(s) and open the widget with

`Plugins` > `Channel Select (Multi Channel Surface)`

The widget allows you to select the surface you wish to interact with, (`Surface` dropdown) and and which channel you wish to view (`Channel` dropdown).

### Helpful hints for using the widget:
* If your channels have widely varying ranges, set auto-contrast to `continuous`
* Popular choices of colormaps include `viridis`, `plasma`, and `turbo`.

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"napari-multi-channel-surface" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

----------------------------------

This [napari] plugin was generated with [copier] using the [napari-plugin-template].

[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[MIT]: http://opensource.org/licenses/MIT
[napari-plugin-template]: https://github.com/napari/napari-plugin-template

[file an issue]: https://github.com/judithlutton/napari-multi-channel-surface/issues

[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
[meshio]: https://github.com/nschloe/meshio
