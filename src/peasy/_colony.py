from typing import List, Tuple

import matplotlib.pyplot as plt
import seaborn as sns

from ._artist import Artist, MultiArtist
from ._params import (
    Cmap,
    Despine,
    FontSize,
    Marker,
    validate_despine,
    validate_font_size,
)


class Colony:
    """An artist colony. The colony class is the mother of all global
    parameters, ensuring that each Artist uses the same figure size, font
    size, spine configuration etc. The colony can create new artists by
    calling the method `get_artist`. This additionally takes a multi=bool
    argument that initializes a MultiArtist if set to True.

    Parameters
    __________
    ax_figsize: int | Tuple[int, int]
        The figure size to use for a single axis. If drawing a grid, then
        each subplot will have this figure size. If single int, will return
        a square figure. Format: (width, height).
    font_size: int | dict | FontSize
        If int, will set a global size for all fonts. If dict, must
        have the same keys that FontSize has.
    despine: bool | str | dict | Despine
        If True, will remove all four spines. If False, will keep all
        four spines. If str, can contain any of the characters t, l, b, r
        for top, left, bottom, right, respectively, for the spines you wish
        to remove. If dict, must have the same keys as Despine.
    cmap: str | Cmap
        If str, should be the lowercase version of a CMAP colorscheme.
    markers: str | List[str] | Marker
        If str, should equal an enumeration in Marker. If List of str,
        should be a list of markers. These will be repeated in case we run
        out of markers.
    """

    def __init__(
        self,
        *,
        ax_figsize: float | Tuple[float, float] = (5, 5),
        font_size: float | dict | FontSize = 11,
        despine: bool | str | dict | Despine = 'tr',
        spine_weight: float | None = None,
        cmap: str | Cmap = Cmap.COZY,
        markers: str | List[str] | Marker = Marker.SIMPLE,
    ):
        self.ax_figsize = ax_figsize
        self.font_size: FontSize = validate_font_size(font_size)
        self.despine: Despine = validate_despine(despine)
        self.spine_weight = spine_weight
        self.cmap = cmap
        self.markers = markers

    @property
    def ax_aspect_equal(self) -> bool:
        return isinstance(self.ax_figsize, float)

    def get_artist(self, multi: bool = False) -> Artist | MultiArtist:
        """Returns an artist or multiartist for drawing figures.
        """
        artist = Artist(colony=self) if not multi else MultiArtist(colony=self)
        return artist

    def get_ax_figsize(self, *, nrows: int = 1, ncols: int = 1) -> Tuple[float, float]:
        """Returns the figure size for the given number of rows and
        columns.
        """
        if self.ax_aspect_equal:
            return (ncols * self.ax_figsize, nrows * self.ax_figsize)  # type: ignore
        w, h = self.ax_figsize  # type: ignore
        return (ncols * w, nrows * h)

    def prettify_axis(self, ax: plt.Axes) -> None:
        """Applies all decorations to axis.
        """
        if self.ax_aspect_equal:
            # Special case when we want a perfect square plot
            ax.set_aspect('equal', adjustable='box')
        sns.despine(ax=ax, **self.despine._asdict())
        if self.spine_weight:
            plt.setp(ax.spines.values(), linewidth=self.spine_weight)
