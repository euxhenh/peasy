from collections import namedtuple
from itertools import zip_longest
from typing import Any, List, Literal

import matplotlib.pyplot as plt
import numpy as np

from .._validation import consistent_length

Line = namedtuple(
    'Line',
    ["x", "y", "label"],
    defaults=(None, None, None),
)


def _line_plot(ax, x, y=None, label=None, **kwargs):
    """Helper function that checks if x in a Line.
    """
    if isinstance(x, Line):
        if y is not None or label is not None:
            raise ValueError(
                "Found `x` of type Line, but either "
                "`y` of `label` is not None."
            )
        x, y, label = x

    args = (x,) if y is None else (x, y)
    ax.plot(*args, label=label, **kwargs)


def line_plot(
    x: Line | List | np.ndarray,
    y: List | np.ndarray | None = None,
    /, *,
    label: Any | None = None,
    color: Any | None = None,
    ax: plt.Axes | None = None,
    ndim: Literal[1] | Literal[2] | Literal[3] = 1,
    **kwargs,
) -> plt.Axes:
    """Colorful line plot.

    Parameters
    __________
    x: 1D, 2D, or 3D array_like object
        The x-axis coordinates. If y is None, then these will be treated as
        y-axis coordinates.
    y: 1D, 2D, or 3D array_like object
        The y-axis coordinates.
    label: A string or 2D/3D List of strings
        The legend labels of the lines.
    color:
        The color for each line plot.
    ax: plt.Axes
        The axes to use for plotting. If None, will create one.
    ndim: int in [1, 3]
        The ndimension of x and y.
    """
    if ndim not in [1, 2, 3]:
        raise ValueError(
            "Multidimensional plotting is only implemented "
            "for 2D or 3D array-like objects."
        )
    if ax is None:
        _, ax = plt.subplots()

    kwargs.pop('label', None)

    if ndim == 1:
        _line_plot(ax, x, y, label, **kwargs)
    else:
        consistent_length(x, y, label)
        for _x, _y, _label in zip_longest(
            x, [] if y is None else y,
            [] if label is None else label,
        ):
            line_plot(_x, _y, label=_label, ax=ax, ndim=ndim - 1, **kwargs)  # type: ignore

    return ax
