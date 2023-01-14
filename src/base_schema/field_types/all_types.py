"""Gather all field types into a single dictionary."""
from typing import Dict

from .int import int_register
from .str import str_register
from ..register import BaseTypeRegister

type_definitions: Dict[str, BaseTypeRegister] = {
    register.field_type: register for register in (int_register, str_register)
}
