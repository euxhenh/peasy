import logging
from typing import List

from ._bubbles import InfList

logger = logging.getLogger(__name__)


class Palette(InfList):
    """A modified palette that repeats colors if we run out.
    Also better supports extending, appending, etc.
    """

    def __init__(self, pal: List[str]):
        for item in pal:
            if not isinstance(item, str):
                raise ValueError(
                    "Expected color hex code but found "
                    f"element of type {type(item)}."
                )
        super().__init__(pal)

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
