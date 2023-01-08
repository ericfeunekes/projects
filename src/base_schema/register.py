from collections.abc import Callable
from functools import wraps
from typing import Dict

type_definitions: Dict[tuple, Callable] = {}

def register_type_definition(property_type: str, constructor: str):
    """A function decorator to register a type definition.

    This decorator registers a type definition in any module that
    imports the module containing the decorated function.

    Args:
        property_type (str): The property type.
        constructor (str): The constructor function.

    Returns:
        function: The decorator function.
    """
    @wraps
    def decorator(func):
        """The decorator function.

        Args:
            func (function): The function to decorate.

        Returns:
            function: The decorated function.
        """
        type_definitions[(property_type, constructor)] = constructor
        return func

    return decorator