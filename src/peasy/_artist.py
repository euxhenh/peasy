from __future__ import annotations

import logging
from collections import namedtuple
from itertools import zip_longest
from math import ceil
from typing import TYPE_CHECKING, List

import matplotlib.pyplot as plt
import numpy as np

from ._validation import there_can_be_only_one
from .functional import lineplot

if TYPE_CHECKING:
    from ._colony import Colony

logger = logging.getLogger(__name__)

Sketch = namedtuple('Sketch', ['fn', 'args', 'kwargs'])


def prettify_axis(fn):
    """A decorator that applies axis prep on end."""

    def _inner(self, *args, ax: plt.Axes | None = None, **kwargs):
        text_kwargs, kwargs = Artist._extract_axes_text(**kwargs)
        ax = fn(self, *args, ax=ax, **kwargs)
        # Post-prep
        self.colony.write_on(ax, **text_kwargs)
        self.colony.prettify_axis(ax)
        self.colony.correct_font_size(ax)
        return ax

    return _inner


class Artist:
    """A base artist class containing most plotting funtions.
    """

    def __init__(self, colony: Colony):
        self.colony = colony

    @staticmethod
    def _extract_axes_text(**kwargs):
        text_kwargs = {}
        text_kwargs['title'] = kwargs.pop('title', None)
        text_kwargs['xlabel'] = kwargs.pop('xlabel', None)
        text_kwargs['ylabel'] = kwargs.pop('ylabel', None)
        return text_kwargs, kwargs

    @prettify_axis
    def lineplot(self, *lines, ax: plt.Axes | None = None, **kwargs) -> plt.Axes:
        """A simple line plot (or multiple lines).
        """
        return lineplot(*lines, ax=ax, **kwargs)

    @prettify_axis
    def sketch(self, fn, /, *args, **kwargs):
        """For any other plotting fn, such as from seaborn."""
        ax = fn(*args, **kwargs)
        return ax


class MultiArtist(Artist):
    """A multiartist class that draws multiple figures in a grid. Uses
    plt.subplots with added functionality.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._queue = []

    @property
    def queue(self) -> List[Sketch]:
        return self._queue

    def __len__(self) -> int:
        return len(self.queue)

    def clear(self) -> None:
        """Clears all elements from the queue.
        """
        self.queue.clear()

    def lineplot(self, *args, **kwargs):
        self.queue.append(Sketch(super().lineplot, args=args, kwargs=kwargs))

    def sketch(self, *args, **kwargs):
        """For any other plotting fn, such as from seaborn."""
        self.queue.append(Sketch(super().sketch, args=args, kwargs=kwargs))

    def show(
        self,
        ncols: int | None = 3,
        nrows: int | None = None,
        tight_layout: bool = True,
        clear: bool = True,
        **kwargs
    ):
        """Displays the grid plot."""
        there_can_be_only_one(ncols, nrows)
        if nrows is None:
            ncols = min(ncols, len(self))  # In case we have less plots
            nrows = ceil(len(self) / ncols)
        elif ncols is None:
            nrows = min(nrows, len(self))
            ncols = ceil(len(self) / nrows)
        kwargs['ncols'] = ncols
        kwargs['nrows'] = nrows
        kwargs['figsize'] = self.colony.get_ax_figsize(nrows=nrows, ncols=ncols)

        _, axes = plt.subplots(**kwargs)

        if ncols == nrows == 1:
            axes = np.array(axes)  # For the for loop

        for i, (sketch, ax) in enumerate(zip_longest(self.queue, axes.flat)):
            # Remove axis if we ran out of sketches
            if sketch is None:
                ax.remove()
                continue
            fn, args, ax_kwargs = sketch
            if 'ax' in ax_kwargs:
                raise ValueError("Cannot pass `ax` to a MultiArtist.")
            try:
                fn(*args, ax=ax, **ax_kwargs)
            except Exception as e:
                logger.error(f"Exception raised from Plot #{i}.")
                raise e

        if tight_layout:
            plt.tight_layout()

        if clear:
            self.clear()

        return axes
