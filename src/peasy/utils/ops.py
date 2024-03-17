from typing import Literal, Tuple, overload

import numpy as np


@overload
def group_indices(x, as_mask: Literal[False] = False) -> Tuple[np.ndarray, list[np.ndarray]]: ...


@overload
def group_indices(x, as_mask: Literal[True]) -> Tuple[np.ndarray, list[np.ndarray]]: ...


def group_indices(x, as_mask=False):
    """Returns an index array pointing to unique elements in x.

    Parameters
    __________
    x: array-like
    as_mask: bool
        If True, will return masks where the indices point to the elements
        inside the group.

    Returns
    _______
    (unique_items, group_indices): (ndarray, List[ndarray])
        The first element contains an array of the unique elements and the
        second contains a list of arrays.

    Examples
    ________
    >>> group_indices([1, 4, 3, 2, 1, 2, 3, 3, 4])
    (array([1, 2, 3, 4]), [array([0, 4]), array([3, 5]), array([2, 6, 7]), array([1, 8])])
    >>> group_indices([1, 1, 1])
    (array([1]), [array([0, 1, 2])])
    >>> group_indices([1, 4, 2, 2, 1], as_mask=True)[1][0].astype(int)
    array([1, 0, 0, 0, 1])
    >>> group_indices([1, 4, 2, 2, 1], as_mask=True)[1][1].astype(int)
    array([0, 0, 1, 1, 0])
    >>> group_indices([1, 4, 2, 2, 1], as_mask=True)[1][2].astype(int)
    array([0, 1, 0, 0, 0])
    """
    assert x.ndim == 1
    if x.size == 0:
        raise ValueError("Encountered 0-sized array.")
    argidx = np.argsort(x, kind='stable')
    sorted_x = x[argidx]
    unique_items, first_indices = np.unique(sorted_x, return_index=True)
    groups = np.split(argidx, first_indices[1:])
    assert len(unique_items) == len(groups)

    if as_mask:
        _groups = [np.zeros(len(x), dtype=bool) for _ in range(len(groups))]
        for group, _group in zip(groups, _groups):
            _group[group] = True
        groups = _groups

    return unique_items, groups
