from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from seaborn._core import variable_type

from .._bubbles import default
from .._custom_typing import Number
from .._palettes import Palette
from .._params import Cmap
from ._data import Data

__all__ = ['Line', 'lineplot']


class Line(Data):

    def __init__(self, x, y=None, /, **kwargs):
        _x = x if y is not None else np.arange(len(x))
        _y = y if y is not None else x
        super().__init__(x=_x, y=_y, **kwargs)


def lineplot(
    lines: Line | Iterable[Line],
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
    if isinstance(lines, Line):
        lines = [lines]

    dfs = []
    for i, line in enumerate(lines):
        df = line.asdf()
        if hue == 'index' and 'index' not in df:  # Create this
            df['index'] = str(i)
        dfs.append(df)

    df: pd.DataFrame = pd.concat(dfs, ignore_index=True, copy=False)

    if isinstance(palette, Palette):
        hue_type: str = variable_type(df[hue])
        if hue_type == 'numeric':
            palette = palette.c_pal
        else:
            palette = palette.d_pal

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
