import pathlib
from collections import namedtuple
from dataclasses import dataclass, field
from enum import Enum, auto
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
    ["title", "xlabel", "ylabel", "xticklabels", "yticklabels", "legend"],
    defaults=(11,) * 6,  # type: ignore
)


def validate_font_size(font_size: float | dict | FontSize) -> FontSize:
    """Validates and returns a FontSize tuple.
    """
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


def _get_palette(name, discrete: bool = False):
    """Parses palette."""
    palettes = D_PALETTES if discrete else C_PALETTES
    pal: str | List[str] = palettes[name]
    if isinstance(pal, str):  # Check seaborn
        pal = sns.color_palette(pal, as_cmap=False).as_hex()
    return DiscretePalette(pal) if discrete else ContinuousPalette(pal)


class _Cmap(Enum):
    def _generate_next_value_(name, *args):
        return Palette(
            d_pal=_get_palette(name, True),
            c_pal=_get_palette(name, False)
        )


class Cmap(_Cmap):
    COZY = auto()
    CHERRY_PIE = auto()
    VINTAGE = auto()
    WARPPED = auto()
    OFFICE = auto()
    MONOCHROME = auto()
    GIVE_ME_ALL = auto()


def validate_cmap(cmap: str | Cmap) -> Palette:
    """Validates a string or list and returns a Palette.
    """
    if isinstance(cmap, Cmap):
        return cmap.value

    if not isinstance(cmap, str):
        raise ValueError(
            "Expected a colormap of type str, but "
            f"found type {type(cmap)}."
        )

    try:
        pal = D_PALETTES[cmap.upper()]
    except Exception:  # Check seaborn if not found in peasy.
        pal = sns.color_palette(cmap).as_hex()

    return Palette(pal)


def validate_palette(palette: str | List[str] | Cmap | Palette) -> Palette:
    """Validates either a palette or cmap."""
    if isinstance(palette, Palette):
        return palette
    if isinstance(palette, (str, Cmap)):
        return validate_cmap(palette)
    return Palette(palette)


@dataclass
class Legend:
    loc: int | str = 'r'
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

        if self.outside and self.loc not in ['r', 'l', 'b', 't']:
            raise ValueError(
                "Outside legend is only supported "
                "for loc in ['r', 'l', 'b', 't']."
            )

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


class LineStyle(Enum):
    NONE = None
    DUO = LineStyleList(['-', '--'])
    TRIO = LineStyleList(['-', '--', '-.'])
    DIVERSE = LineStyleList(['-', '--', '-.', ':', (0, (3, 2, 1, 2, 1, 2))])
    DASHDOT = LineStyleList([(0, (4, 2, 1, 2, *((1, 2) * i))) for i in range(5)])
    LONG_DASHDOT = LineStyleList([(0, (7, 2, 1, 2, *((1, 2) * i))) for i in range(5)])


def validate_linestyle(
    linestyle: str | List[str] | InfList | LineStyle | None,
) -> LineStyleList | None:
    """Validates and returns an InfList."""
    if linestyle is None:
        return None
    if isinstance(linestyle, InfList):
        return LineStyleList(linestyle)
    if isinstance(linestyle, LineStyle):
        return linestyle.value
    if isinstance(linestyle, str):
        return getattr(LineStyle, linestyle.upper()).value
    if isinstance(linestyle, list):
        return LineStyleList(linestyle)
    raise ValueError(
        f"`linestyle` of type {type(linestyle)} "
        "not understood."
    )


MarkerList: TypeAlias = InfList


class Marker(Enum):
    NONE = None
    DUO = MarkerList(['o', '>'])
    TRIO = MarkerList(['o', '>', 's'])
    DIVERSE = MarkerList(['o', '>', 's', 'x', '.', 'd'])


def validate_marker(
    marker: str | List[str] | InfList | Marker | None
) -> MarkerList | None:
    """Validates and returns an InfList."""
    if marker is None:
        return None
    if isinstance(marker, InfList):
        return MarkerList(marker)
    if isinstance(marker, Marker):
        return marker.value
    if isinstance(marker, str):
        return getattr(Marker, marker.upper()).value
    if isinstance(marker, list):
        return MarkerList(marker)
    raise ValueError(
        f"`marker` of type {type(marker)} "
        "not understood."
    )
