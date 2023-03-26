import logging
from collections import UserList
from collections.abc import Iterable

logger = logging.getLogger(__name__)


def default(x, value=list()):
    """If x is None, returns a safe empty array for use in zip_longest.
    """
    return value if x is None else x


def default_index(x, *, expected_type=None, idx=0):
    """If x is of expected_type, return x[idx], otherwise x."""
    if expected_type is not None:
        return x[idx] if isinstance(x, expected_type) else x
    return x[idx] if isinstance(x, Iterable) else x


def default_range(x, *, expected_type, n):
    """If x is of expected_type, return x[0:n], otherwise x."""
    return [x[i] for i in range(n)] if isinstance(x, expected_type) else x


class InfList(UserList):
    """Extends Pythonic lists to loop back at the beginning if index is out
    of bounds.
    """

    def __getitem__(self, i):
        if not isinstance(i, slice):
            return self.data[i % len(self.data)]
        indices = list(range(i.stop)[i])
        return [self.data[idx % len(self.data)] for idx in indices]
