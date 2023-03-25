import logging
from collections import UserList

logger = logging.getLogger(__name__)


def default(x, value=list()):
    """If x is None, returns a safe empty array for use in zip_longest.
    """
    return value if x is None else x


def default_index(x, expected_type, idx):
    """If x is of expected_type, return x[idx], otherwise x."""
    return x[idx] if isinstance(x, expected_type) else x


def default_range(x, expected_type, n):
    """If x is of expected_type, return x[0:n], otherwise x."""
    return [x[i] for i in range(n)] if isinstance(x, expected_type) else x


class InfList(UserList):
    """Extends Pythonic lists to loop back at the beginning if index is out
    of bounds.
    """

    def __getitem__(self, i, /):
        return self.data[i % len(self.data)]
