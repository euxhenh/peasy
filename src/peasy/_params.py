import pathlib
from collections import namedtuple
from dataclasses import dataclass, field
from typing import List, TypeAlias

import seaborn as sns
import yaml

from ._bubbles import InfList
from ._palettes import ContinuousPalette, DiscretePalette, Palette

__all__ = ['FontSize', 'Despine', 'Cmap', 'Legend',
           'LineStyle', 'LineStyleList', 'Marker', 'MarkerList']


path = pathlib.Path(__file__).parent.resolve()
D_PALETTES = yaml.safe_load(open(path / "palettes/discrete.yaml", "r"))
C_PALETTES = yaml.safe_load(open(path / "palettes/continuous.yaml", "r"))

FontSize = namedtuple(
    'FontSize',
    ["title", "xlabel", "ylabel",
     "xticklabels", "yticklabels", "legend", "annotation"],
    defaults=(14, 14, 14, 14, 14, 14, 20),
)


def validate_font_size(font_size: float | dict | FontSize | None) -> FontSize:
    """Validates and returns a FontSize tuple.
    """
    if font_size is None:
        return FontSize()  # all defaults
    if isinstance(font_size, FontSize):
        return font_size
    if isinstance(font_size, dict):
        return FontSize(**font_size)
    if isinstance(font_size, (float | int)):
        return FontSize(*((font_size,) * len(FontSize._fields)))
    raise ValueError(
        f"Font size of type {type(font_size)} "
        "not understood. Please specify an int, "
        "dict or FontSize object."
    )


Despine = namedtuple(
    'Despine',
    ['top', 'left', 'bottom', 'right'],
    defaults=(True, False, False, True),
)


def validate_despine(despine: bool | str | dict | Despine) -> Despine:
    """Constructs and returns a Despine tuple.
    """
    if isinstance(despine, Despine):
        return despine
    if isinstance(despine, dict):
        return Despine(**despine)
    if isinstance(despine, bool):
        if despine:  # Remove all spines
            return Despine(True, True, True, True)
        # Otherwise keep all spines
        return Despine(False, False, False, False)
    if isinstance(despine, str):
        return Despine(
            top='t' in despine,
            left='l' in despine,
            bottom='b' in despine,
            right='r' in despine,
        )
    raise ValueError(
        f"Despine of type {type(despine)} "
        "not understood. Please specify a bool, "
        "str, dict, or Spine object."
    )


def _get_palette(name: str) -> Palette:
    """Parses palette."""
    pals = []
    for palette in [D_PALETTES, C_PALETTES]:
        pal: str | List[str] = palette[name]
        if isinstance(pal, str):  # Check seaborn
            pal = sns.color_palette(pal, as_cmap=False).as_hex()
        pals.append(pal)
    return Palette(d_pal=DiscretePalette(pals[0]), c_pal=ContinuousPalette(pals[1]))


class Cmap:
    COZY = _get_palette('COZY')
    CHERRY = _get_palette('CHERRY')
    VINTAGE = _get_palette('VINTAGE')
    WARPPED = _get_palette('WARPPED')
    OFFICE = _get_palette('OFFICE')
    MONOCHROME = _get_palette('MONOCHROME')
    GIVE_ME_ALL = _get_palette('GIVE_ME_ALL')


def validate_palette(palette: str | List[str] | Palette) -> Palette:
    """Validates either a palette or cmap."""
    if isinstance(palette, Palette):
        return palette
    if isinstance(palette, 'str'):
        return getattr(Cmap, palette.upper())
    return Palette(palette)


@dataclass
class Legend:
    loc: int | str = 'best'
    outside: bool | str = 'auto'
    # Threshold to determine the bool value of outside='auto'
    # (True if >= thresh)
    auto_thresh: int = 5
    # Additional kwargs to pass to ax.legend
    kwargs: dict = field(default_factory=dict)
    loc_plt: int | str = field(init=False)

    def __post_init__(self):
        self.kwargs.pop('loc', None)
        self.kwargs.setdefault('frameon', False)

        if self.outside and self.loc not in ['r', 'l', 'b', 't', 'best']:
            raise ValueError(
                "Outside legend is only supported "
                "for loc in ['r', 'l', 'b', 't', 'best]."
            )

        # If outside, best location is to the right
        if self.outside and self.loc == 'best':
            self.loc = 'r'

        cov = {'r': 'center right', 'l': 'center left',
               'b': 'lower center', 't': 'upper center'}
        self.loc_plt = cov.get(self.loc, self.loc)  # type: ignore


def validate_legend(legend: dict | Legend | None) -> Legend:
    """Validate and return a Legend."""
    if legend is None:  # use defaults
        return Legend()
    if isinstance(legend, dict):
        return Legend(**legend)
    if isinstance(legend, Legend):
        return legend
    raise ValueError(
        f"Legend of type {type(legend)} not understood."
    )


LineStyleList: TypeAlias = InfList


class LineStyle:
    NONE = None
    DUO = LineStyleList(['-', '--'])
    TRIO = LineStyleList(['-', '--', '-.'])
    DIVERSE = LineStyleList(['-', '--', '-.', ':', (0, (3, 2, 1, 2, 1, 2))])
    DASHDOT = LineStyleList([(0, (4, 2, 1, 2, *((1, 2) * i))) for i in range(5)])
    LONG_DASHDOT = LineStyleList([(0, (7, 2, 1, 2, *((1, 2) * i))) for i in range(5)])


def validate_linestyle(
    linestyle: str | List[str] | InfList | LineStyleList | None,
) -> LineStyleList:
    """Validates and returns an InfList."""
    if linestyle is None:
        return LineStyle.NONE
    if isinstance(linestyle, LineStyleList):
        return linestyle
    if isinstance(linestyle, (list, InfList)):
        return LineStyleList(linestyle)
    if isinstance(linestyle, str):
        return getattr(LineStyle, linestyle.upper())
    raise ValueError(f"`linestyle` of type {type(linestyle)} not understood.")


MarkerList: TypeAlias = InfList


class Marker:
    NONE = None
    DUO = MarkerList(['o', '>'])
    TRIO = MarkerList(['o', '>', 's'])
    DIVERSE = MarkerList(['o', '>', 's', 'x', '.', 'd'])


def validate_marker(
    marker: str | List[str] | InfList | MarkerList | None
) -> MarkerList:
    """Validates and returns an InfList."""
    if marker is None:
        return Marker.NONE
    if isinstance(marker, MarkerList):
        return marker
    if isinstance(marker, (list, InfList)):
        return MarkerList(marker)
    if isinstance(marker, str):
        return getattr(Marker, marker.upper())
    raise ValueError(f"`marker` of type {type(marker)} not understood.")
