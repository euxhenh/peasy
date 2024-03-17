import numpy as np
import pandas as pd
import seaborn as sns

from .._custom_typing import Number
from .._palettes import Palette, palette_from_variable_type
from ..utils.ops import group_indices
from ._data import Data, as_combined_df


class Scatter(Data):

    def __init__(self, x, y=None, /, **kwargs):
        x = np.asarray(x)
        if y is None:
            if x.shape[1] != 2:
                raise ValueError(
                    "Expected `x` to be 2-dimensional, but"
                    f"found shape `{x.shape=}`."
                )
            _x, _y = x.T
        else:
            _x = x
            _y = np.asarray(y)
        super().__init__(x=_x, y=_y, **kwargs)


def _add_centroids(
    df: pd.DataFrame, ax,
    x: str = 'x', y: str = 'y',
    hue: str = 'index',
    **kwargs,
):
    items, groups = group_indices(df[hue])
    for item, group in zip(items, groups):
        x1 = df[x][group].mean()
        x2 = df[y][group].mean()
        ax.text(x1, x2, item)


def scatterplot(
    *scatters: Scatter,
    x: str = "x", y: str = "y",
    hue: str = "index",
    palette: Palette | None = None,
    # Some defaults for these
    linewidth: Number = 0,
    s: Number = 8,
    alpha: float = 0.8,
    add_centroids: bool = False,
    **kwargs,
):
    """Scatterplots."""
    df = as_combined_df(*scatters)
    palette = palette_from_variable_type(df[hue], palette)
    kwargs['linewidth'] = linewidth
    kwargs['s'] = s
    kwargs['alpha'] = alpha
    ax = sns.scatterplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
    if add_centroids:
        _add_centroids(df, ax=ax, x=x, y=y, hue=hue)
    return ax
