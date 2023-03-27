from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .._bubbles import default
from .._custom_typing import Number
from .._palettes import Palette, palette_from_variable_type
from .._params import Cmap
from ._data import Data, as_combined_df

__all__ = ['Line', 'lineplot']


class Line(Data):

    def __init__(self, x, y=None, /, **kwargs):
        _x = x if y is not None else np.arange(len(x))
        _y = y if y is not None else x
        super().__init__(x=_x, y=_y, **kwargs)


def lineplot(
    *lines,
    x: str = "x", y: str = "y",
    hue: str = "index",
    palette: Palette = Cmap.OFFICE,
    shade_lb: str | None = None,
    shade_ub: str | None = None,
    shade_alpha: Number = 0.3,
    **kwargs,
):
    """Plots each line in lines. Adds a special key 'index' to each line
    which can be used in any of seaborn's arguments. By default it is used
    for hue.
    """
    df = as_combined_df(*lines, with_index=hue == 'index')
    palette = palette_from_variable_type(df[hue], palette)
    ax = sns.lineplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
    _shadeplot(ax=ax, lines=lines,
               shade_lb=shade_lb, shade_ub=shade_ub, alpha=shade_alpha)
    return ax


def _shadeplot(
    ax: plt.Axes,
    lines: Iterable[Line],
    shade_lb: str | None = None,
    shade_ub: str | None = None,
    alpha: Number = 0.3,
    **kwargs,
):
    """Fills between."""
    if shade_lb is None and shade_ub is None:
        return

    for ax_line, line in zip(ax.get_lines(), lines):
        xdata, ydata = ax_line.get_xydata().T
        color = ax_line.get_color()

        # Determine what to use for y1 and y2.
        # If these are None, we resort to ydata.
        y1 = getattr(line, shade_lb, None) if shade_lb is not None else None
        y1 = default(y1, ydata)
        y2 = getattr(line, shade_ub, None) if shade_ub is not None else None
        y2 = default(y2, ydata)

        if y1 is xdata and y2 is xdata:
            # No shade for this line
            continue
        ax.fill_between(xdata, y1, y2, color=color, alpha=alpha, **kwargs)
