from __future__ import annotations

import logging
from collections import namedtuple
from itertools import zip_longest
from math import ceil
from typing import TYPE_CHECKING, List, Tuple, overload

import matplotlib.pyplot as plt
import numpy as np

from ._validation import there_can_be_only_one
from .functional import Line, line_plot

if TYPE_CHECKING:
    from ._colony import Colony

logger = logging.getLogger(__name__)

Sketch = namedtuple('Sketch', ['fn', 'args', 'kwargs'])


class Artist:
    """A base artist class containing most plotting funtions.
    """

    def __init__(self, *, colony: Colony):
        self.colony = colony

    @staticmethod
    def _extract_axes_text(**kwargs):
        text_kwargs = {}
        text_kwargs['title'] = kwargs.pop('title', None)
        text_kwargs['xlabel'] = kwargs.pop('xlabel', None)
        text_kwargs['ylabel'] = kwargs.pop('ylabel', None)
        text_kwargs['legend'] = kwargs.pop('legend', True)
        return text_kwargs, kwargs

    def line_plot(
        self,
        x: Line | List | np.ndarray,
        y: List | np.ndarray | None = None,
        ax: plt.Axes | None = None,
        **kwargs
    ) -> plt.Axes:
        """A simple line plot (or multiple lines).
        kwargs may have any of the keys in [title, xlabel, ylabel, legend].
        """
        text_kwargs, kwargs = self._extract_axes_text(**kwargs)
        line_plot(x, y, ax=ax, **kwargs)
        self.colony.write_on(ax, **text_kwargs)

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

    def line_plot(self, *args, **kwargs):
        self.queue.append(Sketch(super().line_plot, args=args, kwargs=kwargs))

    @overload
    def show(self, ncols: int, nrows: None, tight_layout: bool) -> List[plt.Axes]:
        ...

    @overload
    def show(self, ncols: None, nrows: int, tight_layout: bool) -> List[plt.Axes]:
        ...

    def show(self, ncols=3, nrows=None, tight_layout=True):
        """Displays the grid plot.
        """
        there_can_be_only_one(ncols, nrows)
        if nrows is None:
            ncols = min(ncols, len(self))  # In case we have less plots
            nrows = ceil(len(self) / ncols)
        elif ncols is None:
            nrows = min(nrows, len(self))
            ncols = ceil(len(self) / nrows)
        figsize: Tuple[float, float] = self.colony.get_ax_figsize(
            ncols=ncols, nrows=nrows)

        _, axes = plt.subplots(ncols=ncols, nrows=nrows, figsize=figsize)

        for i, (sketch, ax) in enumerate(zip_longest(self.queue, axes.flat)):
            # Remove axis if we ran out of sketches
            if sketch is None:
                ax.remove()
                continue
            fn, args, kwargs = sketch

            try:
                fn(*args, ax=ax, **kwargs)
            except Exception as e:
                logger.error(f"Exception raised from Plot #{i}.")
                raise e

            self.colony.prettify_axis(ax)

        if tight_layout:
            plt.tight_layout()

        return axes
