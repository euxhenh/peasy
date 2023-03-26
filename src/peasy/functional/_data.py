import logging
from collections.abc import KeysView
from operator import attrgetter
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

__all__ = ['Data']


class Data:
    """A generic class for data."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __str__(self) -> str:
        cls_name = attrgetter('__class__.__name__')
        s = f"{cls_name(self)}("
        for k, v in self.kwargs.items():
            s += f"{k}:{cls_name(v)}, "
        s = (s[:-2] if len(self.kwargs) else s) + ")"
        return s

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self.x)

    def asdict(self) -> Dict[str, Any]:
        return self.kwargs

    def asdf(self, keys: List[str] | KeysView | None = None) -> pd.DataFrame:
        data = self.asdict()
        if keys is not None:
            data = {k: data[k] for k in keys}
        return pd.DataFrame(data=data)

    @staticmethod
    def is_atomic(val, error: str = "raise") -> bool:
        """Returns true if vale is atomic + str."""
        if isinstance(val, (int, float, str, bool)):
            return True
        if hasattr(val, '__len__'):
            return False
        msg = (
            f"Variable of type '{val}' is not atomic "
            "or does not implement a '__len__' method."
        )
        if error == "raise":
            raise ValueError(msg)
        elif error == "warn":
            logger.warning(msg)
            return False
        else:
            raise ValueError(f"Could not understand error='{error}'")