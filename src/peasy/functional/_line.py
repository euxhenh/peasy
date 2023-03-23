from collections import namedtuple
from itertools import zip_longest
from typing import List, Literal

import matplotlib.pyplot as plt
import numpy as np

from .._bubbles import InfList, default, default_index, default_list
from .._palettes import Palette
from .._validation import consistent_length, there_can_be_none

Line = namedtuple(
    'Line',
    ["x", "y", "label"],
    defaults=(None, None, None),
)


def _line_plot(
    ax, x, y=None, label=None, color=None,
    linestyle=None, marker=None, **kwargs,
):
    """Helper function that checks if x in a Line.
    """
    if isinstance(x, Line):
        there_can_be_none(y, label)
        x, y, label = x

    line_no = len(ax.lines)
    color = default_index(color, Palette, line_no)
    linestyle = default_index(linestyle, InfList, line_no)
    marker = default_index(marker, InfList, line_no)

    args = (x,) if y is None else (x, y)
    ax.plot(*args, label=label, color=color,
            linestyle=linestyle, marker=marker, **kwargs)


def line_plot(
    x: Line | List | np.ndarray,
    y: List | np.ndarray | None = None,
    /,
    label: str | List[str] | None = None,
    color: str | Palette | None = None,
    linestyle: str | InfList | None = None,
    marker: str | InfList | None = None,
    *,
    ax: plt.Axes | None = None,
    ndim: Literal[1] | Literal[2] = 1,
    **kwargs,
) -> plt.Axes:
    """Colorful line plot.

    Parameters
    __________
    x: 1D or 2D array_like object
        The x-axis coordinates. If y is None, then these will be treated as
        y-axis coordinates.
    y: 1D or 2D array_like object
        The y-axis coordinates.
    label: A string or 1D List of strings
        The legend labels of the lines.
    color: str | Palette
        The color for each line plot.
    linestyle: str | InfList
        {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
    marker: str | InfList
        A single marker or list of markers to use.
    ax: plt.Axes
        The axes to use for plotting. If None, will create one.
    ndim: int in [1, 2]
        The ndimension of x and y.
    """
    if ndim not in [1, 2]:
        raise ValueError("Only 1D and 2D arrays are supported.")
    for param, name in zip([label, color, linestyle, marker],
                           ['label', 'color', 'linestyle', 'marker']):
        if isinstance(param, str) and ndim > 1:
            raise ValueError(
                f"Parameter `{name}` cannot be a "
                "string if plotting 2D arrays."
            )

    if ax is None:
        _, ax = plt.subplots()

    if ndim == 1:
        _line_plot(ax, x, y, label, color, linestyle, marker, **kwargs)
        return ax

    # ndim == 2 now
    n = len(x)
    color = default_list(color, Palette, n)
    linestyle = default_list(linestyle, InfList, n)
    marker = default_list(marker, InfList, n)

    consistent_length(x, y, label, color, linestyle, marker)
    # This should follow the same order of arguments as in the declaration
    # of this function
    to_iter = (
        x, default(y), default(label), default(color),
        default(linestyle), default(marker)
    )
    for args in zip_longest(*to_iter):
        line_plot(*args, ax=ax, ndim=1, **kwargs)

    return ax
