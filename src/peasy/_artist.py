from __future__ import annotations

from abc import ABC
from collections import namedtuple
from itertools import zip_longest
from math import ceil
from typing import TYPE_CHECKING, List, Tuple, overload

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

    @staticmethod
    def _extract_text(**kwargs):
        text_kwargs = {}
        text_kwargs['title'] = kwargs.pop('title', None)
        text_kwargs['xlabel'] = kwargs.pop('xlabel', None)
        text_kwargs['ylabel'] = kwargs.pop('ylabel', None)
        text_kwargs['legend'] = kwargs.pop('legend', True)
        return text_kwargs, kwargs

    def _write_on(
        self,
        ax: plt.Axes,
        /,
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        legend: bool = True,
    ) -> None:
        """Adds text to axes.
        """
        if title:
            ax.set_title(title, fontsize=self.colony.font_size.title)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=self.colony.font_size.xlabel)
        if ylabel:
            ax.set_xlabel(ylabel, fontsize=self.colony.font_size.ylabel)
        ax.tick_params(axis='x', labelsize=self.colony.font_size.xticklabels)
        ax.tick_params(axis='y', labelsize=self.colony.font_size.yticklabels)
        # Only show legend if there are any labels == this list is nonempty
        if legend and ax.get_legend_handles_labels()[0]:
            ax.legend(prop={'size': self.colony.font_size.legend})

    def line_plot(self, x, y, ax: plt.Axes | None = None, **kwargs) -> plt.Axes:
        """A simple line plot (or multiple lines).
        """
        text_kwargs, kwargs = self._extract_text(**kwargs)
        if ax is None:
            _, ax = plt.subplots()
        line_plot(x=x, y=y, ax=ax)
        self._write_on(ax, **text_kwargs)

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

    def clear_queue(self) -> None:
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
            nrows = ceil(len(self) / ncols)
        elif ncols is None:
            ncols = ceil(len(self) / nrows)
        figsize: Tuple[float, float] = self.colony.get_ax_figsize(
            ncols=ncols, nrows=nrows)

        _, axes = plt.subplots(ncols=ncols, nrows=nrows, figsize=figsize)

        for sketch, ax in zip_longest(self.queue, axes.flat):
            # Remove axis if we ran out of sketches
            if sketch is None:
                ax.remove()
                continue
            fn, args, kwargs = sketch
            fn(*args, ax=ax, **kwargs)
            self.colony.prettify_axis(ax)

        if tight_layout:
            plt.tight_layout()

        return axes
