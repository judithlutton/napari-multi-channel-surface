"""
This module provides sample data, read by the `napari-multi-channel-surface` reader function.
Each channel in the sample data can be viewed using the `Channel Select` widget in `napari-multi-channel-surface`.
"""

from __future__ import annotations

from pathlib import Path

from ._reader import reader_function

_sample_dir = Path(__file__).parent.joinpath("data")


def stanford_bunny():
    """Returns the standford bunny with point data 'X','Y', and 'Z' representing cartesian coordinates.

    Notes
    -----
    Surface mesh adapted from data downloaded from repository
    `https://graphics.stanford.edu/data/3Dscanrep/`.
    Source file used: `bun_zipper_res2.ply`

    Metadata:
    Stanford Bunny
    Source: Stanford University Computer Graphics Laboratory
    Scanner: Cyberware 3030 MS
    Number of scans: 10
    Total size of scans: 362,272 points (about 725,000 triangles)
    Reconstruction: zipper
    Size of reconstruction: 35947 vertices, 69451 triangles
    Comments: contains 5 holes in the bottom
    """
    data_file = _sample_dir.joinpath("bunny_xyz.vtu")
    return reader_function(data_file)
