from itertools import compress


def there_can_be_only_one(*args):
    """Will raise an error if more than one arg evaluates to True.
    """
    is_true = [bool(arg) for arg in args]
    if sum(is_true) != 1:
        raise ValueError("Exactly one param should be set.")
    return list(compress(args, is_true))[0]


def there_can_be_none(*args):
    """Will raise an error if any of arg is not None.
    """
    for arg in args:
        if arg is not None:
            raise ValueError(
                "Expected all arguments to be None "
                f"but found value {arg}."
            )


def there_should_be_at_least_one(*args):
    """Will raise an error if all args are None.
    """
    are_none = [arg is None for arg in args]
    if not any(are_none):
        raise ValueError("At least one argument must not be None.")


def there_should_be_at_most_one(*args):
    """Will raise an error if all args are None.
    """
    are_none = [arg is not None for arg in args]
    if sum(are_none) > 1:
        raise ValueError("At most one argument must not be None.")


def consistent_length(*args):
    """Ensures that all args have the same length.
    """
    lens = [len(arg) for arg in args if arg is not None]
    if len(set(lens)) > 1:
        raise ValueError(
            f"Found objects of incosistent lengths: {lens}."
        )
