from collections import namedtuple
from enum import Enum, auto


FontSize = namedtuple(
    'FontSize',
    ["title", "xlabel", "ylabel", "xticks", "yticks", "legend"],
)

Spine = namedtuple(
    'Spine',
    ['top', 'left', 'bottom', 'right'],
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
