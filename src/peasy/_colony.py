from typing import List, Tuple

from ._artist import Artist, MultiArtist
from ._params import Cmap, Marker, FontSize, Spine


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
        a square figure.
    font_size: int | dict | FontSize
        If int, will set a global size for all fonts. If dict, must
        have the same keys that FontSize has.
    spine: bool | str | dict | Spine
        If True, will enable all four spines. If False, will disable all
        four spines. If str, can contain any of the characters t, l, b, r
        for top, left, bottom, right, respectively, for the spines you wish
        to keep. If dict, must have the same keys as Spine.
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
        ax_figsize: int | Tuple[int, int] = (6, 6),
        font_size: int | dict | FontSize = 12,
        spine: bool | str | dict | Spine = 'lb',
        cmap: str | Cmap = Cmap.COZY,
        markers: str | List[str] | Marker = Marker.SIMPLE,
    ):
        self.ax_figsize = ax_figsize
        self.font_size = font_size
        self.spine = spine
        self.cmap = cmap
        self.markers = markers

    def get_artist(self, multi: bool = False) -> Artist | MultiArtist:
        """Returns an artist or multiartist for drawing figures.
        """
        artist = Artist(colony=self) if not multi else MultiArtist(colony=self)
        return artist

    def get_ax_figsize(self, *, nrows: int = 1, ncols: int = 1) -> Tuple[int, int]:
        """Returns the figure size for the given number of rows and
        columns.
        """
        if isinstance(self.ax_figsize, int):
            return (ncols * self.ax_figsize, nrows * self.ax_figsize)
        w, h = self.ax_figsize
        return (ncols * h, nrows * w)
