from itertools import compress


def there_can_be_only_one(*args):
    """Will raise an error if more than one arg evaluates to True.
    """
    is_true = [bool(arg) for arg in args]
    if sum(is_true) != 1:
        raise ValueError("Exactly one param should be set.")
    return list(compress(args, is_true))[0]
