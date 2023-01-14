from __future__ import annotations
from collections.abc import Callable
from functools import wraps
from typing import Dict


class BaseTypeRegister:
    """A register for base types
    
    Base types are types that are supported by all constructors. These are
    types like int, str, and float.
    """
    def __init__(self, field_type: str):
        self.field_type = field_type
        self._type_definitions: Dict[str, Callable] = {}

    def __call__(self, constructor: str):
        @wraps
        def decorator(func: Callable):
            self._type_definitions[constructor] = func
            return func

        return decorator

    def __getitem__(self, key: str) -> Callable:
        try:
            return self._type_definitions[key]
        except KeyError as exc:
            raise ValueError(f"Constructor {key} not found for field type {self.field_type}") from exc


class Register(BaseTypeRegister):
    """A register for field types that are not base types
    
    If 
    """
    def __init__(self, field_type: str, fallback: BaseTypeRegister):
        super().__init__(field_type)
        self.fallback = fallback

    def __getitem__(self, key: str) -> Callable:
        try:
            return self._type_definitions[key]
        except KeyError:
            return self.fallback[key]
