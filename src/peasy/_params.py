from collections import namedtuple
from enum import Enum, auto


_fontsize_fields = ["title", "xlabel", "ylabel", "xticklabels", "yticklabels", "legend"]
FontSize = namedtuple('FontSize', _fontsize_fields,
                      defaults=(11,) * len(_fontsize_fields))


def validate_font_size(font_size: int | dict | FontSize) -> FontSize:
    """Validates and returns a FontSize tuple.
    """
    if isinstance(font_size, FontSize):
        return FontSize
    if isinstance(font_size, dict):
        return FontSize(**font_size)
    if isinstance(font_size, int):
        return FontSize(*((font_size,) * len(FontSize._fields)))
    raise ValueError(
        f"Font size of type {type(font_size)} "
        "not understood. Please specify an int, "
        "dict or FontSize object."
    )


_despine_fields = ['top', 'left', 'bottom', 'right']
Despine = namedtuple('Despine', _despine_fields,
                     defaults=(True, False, False, True))


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


class Cmap(Enum):
    COZY = auto()
    OFFICIAL = auto()
    BW = auto()
    MONOCHROME = auto()


class Marker(Enum):
    NONE = auto()
    SIMPLE = auto()
    DISTANT = auto()
    SHAPES = auto()
