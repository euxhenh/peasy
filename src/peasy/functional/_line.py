from itertools import zip_longest
from typing import List, Literal, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .._bubbles import InfList, default, default_index, default_range
from .._palettes import Palette
from .._params import LineStyleList, MarkerList
from .._validation import consistent_length

__all__ = ['line_plot']


def _line_plot(
    ax, x, y=None, label=None, color=None,
    linestyle=None, marker=None, shade=None,
    shade_alpha=None, **kwargs,
):
    """Helper function that checks if x in a Line.
    """
    line_no = len(ax.lines)
    if isinstance(color, Palette):
        color = color.d_pal[line_no]  # Use discrete palette
    linestyle = default_index(linestyle, InfList, line_no)
    marker = default_index(marker, InfList, line_no)

    args = (x,) if y is None else (x, y)
    ax.plot(*args, label=label, color=color,
            linestyle=linestyle, marker=marker, **kwargs)
    if shade is not None:
        xcoord = args[0] if len(args) == 2 else np.arange(len(args[0]))
        consistent_length(shade[0], shade[1], xcoord)
        ax.fill_between(xcoord, shade[0], shade[1], color=color, alpha=shade_alpha)


def line_plot(
    x: List | np.ndarray,
    y: List | np.ndarray | None = None,
    /,
    label: str | List[str] | None = None,
    color: str | Palette | None = None,
    linestyle: str | LineStyleList | None = None,
    marker: str | MarkerList | None = None,
    shade: Tuple[List, List] | Tuple[np.ndarray, np.ndarray] | None = None,
    shade_alpha: float = 0.2,
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

    if ndim > 1:
        for param, name in zip(
            [label, color, linestyle, marker],
            ['label', 'color', 'linestyle', 'marker'],
        ):
            if isinstance(param, str):
                raise ValueError(
                    f"Parameter `{name}` cannot be a "
                    "string if plotting 2D arrays."
                )

    if ax is None:
        ax = plt.gca()

    kwargs['shade_alpha'] = shade_alpha

    if ndim == 1:
        _line_plot(ax=ax, x=x, y=y, label=label, color=color,
                   linestyle=linestyle, marker=marker, shade=shade,
                   **kwargs)
        return ax

    # ndim == 2 now
    n = len(x)
    if isinstance(color, Palette):
        color = color(np.arange(n))
    linestyle = default_range(linestyle, InfList, n)
    marker = default_range(marker, InfList, n)

    consistent_length(x, y, label, color, linestyle, marker)
    # This should follow the same order of arguments as in the declaration
    # of this function
    to_iter = (
        x, default(y), default(label), default(color),
        default(linestyle), default(marker), zip(*default(shade)),
    )
    for args in zip_longest(*to_iter):
        line_plot(*args, ax=ax, ndim=1, **kwargs)

    return ax
