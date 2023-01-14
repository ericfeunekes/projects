from base_schema.register import Register

int_register = Register(field_type="int", fallback=None)

@int_register("dataclass")
def create_dataclass_int(name: str) -> tuple:
    """Return value that can be passed to `make_dataclass` to create a
    dataclass type.

    Args:
        name (str): The name of the dataclass type.

    Returns:
        tuple: The value to pass to `make_dataclass`.
    """
    return (name, int)


@int_register("pandas")
def create_pandas_int(name: str):
    pass