from collections.abc import Callable
from functools import wraps
from typing import Dict, Optional

class Register:
    def __init__(self, field_type: str, fallback: Optional[str]):
        self.field_type = field_type
        self._type_definitions: Dict[tuple, Callable] = {}

    def __call__(self, constructor: str):

        def decorator(func: Callable):
            self._type_definitions[(self.field_type, constructor)] = func
            return func

        return decorator