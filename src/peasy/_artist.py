from __future__ import annotations

import logging
from collections import namedtuple
from functools import partial, wraps
from itertools import zip_longest
from math import ceil
from types import MethodType
from typing import TYPE_CHECKING, List

import matplotlib.pyplot as plt
import numpy as np

from ._validation import there_can_be_only_one
from .functional import Line, Scatter, lineplot, scatterplot

if TYPE_CHECKING:
    from ._colony import Colony

logger = logging.getLogger(__name__)

Sketch = namedtuple('Sketch', ['fn', 'args', 'kwargs'])


def prettify_axis(fn):
    """A decorator that applies axis prep on end."""

    @wraps(fn)
    def _inner(self, *args, ax: plt.Axes | None = None, **kwargs):
        text_kwargs, ax_kwargs, kwargs = Artist._extract_special_keys(**kwargs)
        ax = fn(self, *args, ax=ax, **kwargs)
        # Post-prep
        self.colony.write_on(ax, **text_kwargs)
        self.colony.prettify_axis(ax, **ax_kwargs)
        self.colony.correct_font_size(ax)
        return ax

    _inner.__name__ = fn.__name__
    return _inner


def queue_fn(fn):
    """A decorator that applies axis prep on end."""
    artist_fn = getattr(Artist, fn)

    @wraps(artist_fn)
    def _inner(self, *args, **kwargs):
        to_call_fn = getattr(super(MultiArtist, self), fn)
        self.queue.append(Sketch(to_call_fn, args, kwargs))

    _inner.__name__ = fn
    return _inner


class Artist:
    """A base artist class containing most plotting funtions.
    """

    def __init__(self, colony: Colony):
        self.colony = colony

    @staticmethod
    def _extract_special_keys(**kwargs):
        text_kwargs = {}
        text_kwargs['title'] = kwargs.pop('title', None)
        text_kwargs['xlabel'] = kwargs.pop('xlabel', None)
        text_kwargs['ylabel'] = kwargs.pop('ylabel', None)
        ax_kwargs = {}
        ax_kwargs['aspect'] = kwargs.pop('aspect', None)
        return text_kwargs, ax_kwargs, kwargs

    @prettify_axis
    def lineplot(self, *lines: Line, **kwargs) -> plt.Axes:
        return lineplot(*lines, **kwargs)

    @prettify_axis
    def scatterplot(self, *scatters: Scatter, **kwargs) -> plt.Axes:
        return scatterplot(*scatters, **kwargs)

    @prettify_axis
    def sketch(self, fn, /, *args, **kwargs):
        """For any other plotting fn, such as from seaborn."""
        ax = fn(*args, **kwargs)
        return ax


class MultiArtist(Artist):
    """A multiartist class that draws multiple figures in a grid. Uses
    plt.subplots with added functionality.
    """

    _queueable = ['lineplot', 'scatterplot', 'sketch']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._queue = []

        # Assign queueable methods to self
        for fn in MultiArtist._queueable:
            setattr(self, fn, MethodType(queue_fn(fn), self))

    @property
    def queue(self) -> List[Sketch]:
        return self._queue

    def __len__(self) -> int:
        return len(self.queue)

    def clear(self) -> None:
        """Clears all elements from the queue.
        """
        self.queue.clear()

    def show(
        self,
        ncols: int | None = 3, nrows: int | None = None,
        annotate: bool = True, annot_style: str = 'a',
        tight_layout: bool = True, clear: bool = False,
        mosaic: List | None = None,
        **kwargs
    ):
        """Displays the grid plot."""
        if not len(self):
            raise ValueError("No plots found.")

        if mosaic is None:
            there_can_be_only_one(ncols, nrows)
            if nrows is None:
                ncols = min(ncols, len(self))  # In case we have less plots
                nrows = ceil(len(self) / ncols)
            elif ncols is None:
                nrows = min(nrows, len(self))
                ncols = ceil(len(self) / nrows)
            kwargs['ncols'] = ncols
            kwargs['nrows'] = nrows
            subplot_fn = plt.subplots
        else:
            mosaic = np.asarray(mosaic)
            nrows, ncols = mosaic.shape
            subplot_fn = partial(plt.subplot_mosaic, mosaic)

        kwargs['figsize'] = self.colony.get_figsize(nrows=nrows, ncols=ncols)

        _, axes = subplot_fn(**kwargs)

        if mosaic is not None:
            axes = np.asarray(list(axes.values()))

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

            if annotate:
                self.colony.annotate(ax, i=i, annot_style=annot_style)

        if tight_layout:
            plt.tight_layout()

        if clear:
            self.clear()

        return axes
