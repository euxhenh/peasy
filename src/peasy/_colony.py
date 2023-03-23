import logging
from numbers import Number
from typing import List, Tuple

import matplotlib.pyplot as plt
import seaborn as sns

from ._artist import Artist, MultiArtist
from ._palettes import Palette
from ._params import (
    Cmap,
    Despine,
    FontSize,
    Legend,
    LineStyle,
    Marker,
    validate_despine,
    validate_font_size,
    validate_legend,
    validate_linestyle,
    validate_marker,
    validate_palette_or_cmap,
)

logger = logging.getLogger(__name__)


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
    spine_weight: float
        The width in pixels of the spine axis.
    palette: List[str]
        A list of colors in hex. Takes precedence over cmap.
    cmap: str | Cmap
        If str, should be the lowercase version of a CMAP colorscheme.
    legend: dict | Legend
        Legend options.
    linestyle: str | List[str] | LineStyle
        If str, will map to a LineStyle key. If list of str, will treat as
        a list of str linestyles.
    marker: str | List[str] | Marker
        If str, should equal an enumeration in Marker. If List of str,
        should be a list of markers. These will be repeated in case we run
        out of markers.
    """

    def __init__(
        self,
        *,
        ax_figsize: Number | Tuple[Number, Number] = 5,
        font_size: Number | dict[str, Number] | FontSize = 11,
        despine: bool | str | dict[str, str] | Despine = 'tr',
        palette: List[str] | Palette | None = None,
        cmap: str | Cmap | None = Cmap.OFFICE,
        legend: dict | Legend | None = None,
        linestyle: str | List[str] | LineStyle | None = LineStyle.NONE,
        marker: str | List[str] | Marker | None = Marker.NONE,
        spine_weight: Number | None = None,
    ):
        self.ax_figsize: Tuple[Number, Number] = (
            (ax_figsize, ax_figsize) if isinstance(ax_figsize, Number)
            else ax_figsize
        )
        self.font_size: FontSize = validate_font_size(font_size)
        self.despine: Despine = validate_despine(despine)
        self.palette: Palette = validate_palette_or_cmap(palette, cmap)
        self.legend: Legend = validate_legend(legend)
        self.linestyle = validate_linestyle(linestyle)
        self.marker = validate_marker(marker)
        self.spine_weight: Number = spine_weight

    @property
    def ax_aspect_equal(self) -> bool:
        return self.ax_figsize[0] == self.ax_figsize[1]

    def new_artist(self, multi: bool = False) -> Artist | MultiArtist:
        """Returns an artist or multiartist for drawing figures.
        """
        artist = Artist(colony=self) if not multi else MultiArtist(colony=self)
        return artist

    def get_ax_figsize(self, *, nrows: int = 1, ncols: int = 1) -> Tuple[Number, Number]:
        """Returns the figure size for the given number of rows and
        columns.
        """
        w, h = self.ax_figsize
        return (ncols * w, nrows * h)

    def add_legend(self, ax: plt.Axes, legend: Legend | None = None) -> None:
        """Add legend and find a good location."""
        if legend is None:
            legend = self.legend
        n_labels = len(ax.get_legend_handles_labels()[0])
        if n_labels == 0:  # Show legend only if there are labels
            return
        if legend.outside == 'auto':
            outside = True if n_labels >= legend.auto_thresh else False
        else:
            outside = legend.outside

        if not outside:
            ax.legend(loc=legend.loc_plt, **legend.kwargs)
        else:
            pdict = {
                'r': ('center left', (1.04, 0.5)),
                'l': ('center right', (-0.1, 0.5)),
                't': ('lower center', (0.5, 1.1)),
                'b': ('upper center', (0.5, -0.1)),
            }
            kwargs = legend.kwargs.copy()
            if legend.loc in ['t', 'b']:
                kwargs.setdefault('ncol', n_labels)  # Horizontal legend

            loc, bbox_to_anchor = pdict[legend.loc]
            ax.legend(loc=loc, bbox_to_anchor=bbox_to_anchor,
                      prop={'size': self.font_size.legend}, **kwargs)

    def prettify_axis(self, ax: plt.Axes) -> None:
        """Applies all decorations to axis."""
        if self.ax_aspect_equal:
            # Special case when we want a perfect square plot
            ax.set_box_aspect(1)
        sns.despine(ax=ax, **self.despine._asdict())
        self.add_legend(ax=ax)
        if self.spine_weight:
            plt.setp(ax.spines.values(), linewidth=self.spine_weight)

    def write_on(
        self,
        ax: plt.Axes,
        /,
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
    ) -> None:
        """Adds text to axes.
        """
        if title:
            ax.set_title(title, fontsize=self.font_size.title)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=self.font_size.xlabel)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=self.font_size.ylabel)
        ax.tick_params(axis='x', labelsize=self.font_size.xticklabels)
        ax.tick_params(axis='y', labelsize=self.font_size.yticklabels)
