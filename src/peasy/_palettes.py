import logging
import re
from typing import List

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import (
    ListedColormap,
    to_hex,
    to_rgb,
    to_rgba,
    to_rgba_array,
)
from seaborn._core import variable_type

from ._bubbles import InfList
from ._validation import there_should_be_at_least_one

logger = logging.getLogger(__name__)


__all__ = ['DiscretePalette', 'ContinuousPalette', 'Palette']


class DiscretePalette(InfList):
    """A modified palette that repeats colors if we run out.
    Also better supports extending, appending, etc.

    Parameters
    __________
    pal: List[str]
        A list of hex color codes or rgb tuples (lists).
    """

    def __init__(self, pal: List[str]):
        items = []
        for item in pal:
            if not isinstance(item, str):
                item = to_hex(item)
            elif not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', item):
                raise ValueError(f"{item} is not a valid hex color.")
            items.append(item)

        super().__init__(items)

    def as_rgb(self, drop_alpha: bool = True) -> List:
        """Convert self to rgb values."""
        fn = to_rgb if drop_alpha else to_rgba
        return [fn(i) for i in self.data]

    def as_rgb_array(self, drop_alpha: bool = True) -> np.ndarray:
        """Convert self to rgb numpy array."""
        # Drop alpha
        arr = to_rgba_array(self.data)
        if drop_alpha:
            arr = arr[:, :3]
        return arr

    def _repr_html_(self):
        """Rich display of the color palette in an HTML frontend.

        Source: seaborn.palettes._ColorPalette
        """
        s = 55
        n = len(self)
        html = f'<svg  width="{n * s}" height="{s}">'
        for i, c in enumerate(self.data):
            html += (
                f'<rect x="{i * s}" y="0" width="{s}" height="{s}" style="fill:{c};'
                'stroke-width:2;stroke:rgb(255,255,255)"/>'
            )
        html += '</svg>'
        return html


class ContinuousPalette(ListedColormap):
    """A palette for floating point values."""

    def __init__(self, colors: ListedColormap | List[str], n: int = 256):
        if isinstance(colors, ListedColormap):
            colors = colors.colors
        else:
            colors = sns.blend_palette(colors, n_colors=n, as_cmap=False).as_hex()

        super().__init__(colors)

    def __len__(self) -> int:
        return len(self.colors)


class Palette:
    """A palette for both discrete or continuous values."""

    def __init__(
        self,
        d_pal: DiscretePalette | None = None,
        c_pal: ContinuousPalette | ListedColormap | None = None,
        pal: List[str] | None = None,
        d_n: int = 12,
        c_n: int = 256,
    ):
        there_should_be_at_least_one(d_pal, c_pal, pal)

        if c_pal is not None and isinstance(c_pal, ListedColormap):
            c_pal = ContinuousPalette(c_pal)

        if d_pal is None:
            if pal is not None:
                d_pal = DiscretePalette(pal)
            else:
                assert c_pal is not None
                step = (len(c_pal) - 1) // d_n
                d_pal = [c_pal[i] for i in range(0, len(c_pal), step)]

        if c_pal is None:
            if pal is not None:
                c_pal = ContinuousPalette(pal, n=c_n)
            else:
                assert d_pal is not None
                c_pal = ContinuousPalette(d_pal, n=c_n)

        self._d_pal = d_pal
        self._c_pal = c_pal

    @property
    def d_pal(self) -> DiscretePalette:
        return self._d_pal

    @property
    def c_pal(self) -> ContinuousPalette:
        return self._c_pal

    def __call__(self, hue, force_discrete: bool = False):
        """Converts hue to a list of hex colors."""
        hue = np.asarray(hue)
        # Determine whether we should use discrete or continuous palette
        # based on float or not
        if hue.dtype.kind == 'f' and not force_discrete:
            colors = [to_hex(c) for c in self.c_pal(hue)]
        else:
            colors = [self.d_pal[i] for i in hue]
        return colors

    def _repr_html_(self):
        html = self.c_pal._repr_html_()
        html += self.d_pal._repr_html_()
        return html


def palette_from_variable_type(
    var: pd.Series,
    palette: Palette,
) -> DiscretePalette | ContinuousPalette:
    """Returns a discrete or continuous palette based on the type of
    var.
    """
    if isinstance(palette, Palette):
        hue_type: str = variable_type(var)
        if hue_type == 'numeric':
            palette = palette.c_pal
        else:
            palette = palette.d_pal
    return palette
