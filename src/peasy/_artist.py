from __future__ import annotations

from abc import ABC
from collections import namedtuple
from math import ceil
from itertools import zip_longest
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from ._validation import there_can_be_only_one
from .functional import line_plot

if TYPE_CHECKING:
    from ._colony import Colony


Sketch = namedtuple('Sketch', ['fn', 'args', 'kwargs'])


class Artist(ABC):
    """A base artist class containing most plotting funtions.
    """

    def __init__(self, *, colony: Colony):
        self.colony = colony

    def line_plot(self, x, y, ax: plt.Axes | None = None):
        """A simple line plot (or multiple lines).
        """
        if ax is None:
            _, ax = plt.subplots()
        line_plot(x=x, y=y, ax=ax)


class MultiArtist(Artist):
    """A multiartist class that draws multiple figures in a grid. Uses
    plt.subplots with added functionality.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = []

    def __len__(self) -> int:
        return len(self.queue)

    def line_plot(self, *args, **kwargs):
        self.queue.append(Sketch(super().line_plot, args=args, kwargs=kwargs))

    def show(self, ncols: int | None = 3, nrows: int | None = None):
        """Displays the grid plot.
        """
        there_can_be_only_one(ncols, nrows)
        if ncols:
            nrows = ceil(len(self) / ncols)
        else:
            ncols = ceil(len(self) / nrows)

        _, axes = plt.subplots(
            ncols=ncols, nrows=nrows,
            figsize=self.colony.get_ax_figsize(ncols=ncols, nrows=nrows),
        )

        for sketch, ax in zip_longest(self.queue, axes):
            # Remove axis if we ran out of sketches
            if sketch is None:
                ax.remove()
                continue
            fn, args, kwargs = sketch
            fn(*args, ax=ax, **kwargs)

        plt.show()
