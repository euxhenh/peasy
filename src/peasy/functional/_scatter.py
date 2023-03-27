import numpy as np
import seaborn as sns

from .._palettes import Palette, palette_from_variable_type
from .._params import Cmap
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


def scatterplot(
    *scatters: Scatter,
    x: str = "x", y: str = "y",
    hue: str = "index",
    palette: Palette = Cmap.OFFICE,
    **kwargs,
):
    """Scatterplots."""
    df = as_combined_df(*scatters)
    palette = palette_from_variable_type(df[hue], palette)
    ax = sns.scatterplot(data=df, x=x, y=y, hue=hue, palette=palette, **kwargs)
    return ax
