"""Tests for the dataclass constructor"""
import pytest
from dataclasses import dataclass

from .dataclass import get_dataclass_field, create_dataclass
from ..field_types import type_definitions


class TestGetDataClassTest:
    """Tests for the `get_dataclass_field` function"""

    def test_function_is_called(self, mocker):
        """Test that the function in a field dictionary is called"""

        mock_function = mocker.Mock()
        field = {"name": "test", "type": "int"}
        type_definitions = {("int", "dataclass"): mock_function}

        get_dataclass_field(field, type_definitions)

        mock_function.assert_called_once_with("test")

    def test_function_not_called_when_not_int(self, mocker):
        """Test that the function in a field dictionary is not called when the type is not int"""

        mock_function = mocker.Mock()
        field = {"name": "test", "type": "str"}
        type_definitions = {("int", "dataclass"): mock_function}

        with pytest.raises(ValueError):
            get_dataclass_field(field, type_definitions)

    def test_no_name(self):
        """Test that an error is raised when the field has no name"""

        field = {"type": "int"}
        type_definitions = {("int", "dataclass"): lambda x: x}

        with pytest.raises(ValueError):
            get_dataclass_field(field, type_definitions)

    def test_no_type(self):
        """Test that an error is raised when the field has no type"""

        field = {"name": "test"}
        type_definitions = {("int", "dataclass"): lambda x: x}

        with pytest.raises(ValueError):
            get_dataclass_field(field, type_definitions)


class TestCreateDataclass:
    """Tests for the `create_dataclass` function"""

    def test_constructor_is_called(self, mocker):
        """Test that the function in a field dictionary is called"""

        mock_constructor = mocker.Mock()
        definition = {"name": "test", "fields": [{"name": "test", "type": "int"}]}
        type_definitions = {("int", "dataclass"): mock_constructor}

        create_dataclass(definition, type_definitions)

        mock_constructor.assert_called_once_with("test")

    def test_function_called_for_each_field(self, mocker):
        """Test that `get_dataclass_field` is called for each field"""
        # Patch `make_dataclass` so it doesn't raise an error
        mocker.patch("base_schema.constructors.dataclass.make_dataclass")
        # Patch `get_dataclass_field` so we can tell what it it called with
        mock_function = mocker.patch(
            "base_schema.constructors.dataclass.get_dataclass_field"
        )

        definition = {"name": "test", "fields": [{"name": "test", "type": "int"}]}
        type_definitions = {("int", "dataclass"): lambda x: x}

        create_dataclass(definition, type_definitions)

        # Check that `get_dataclass_field` was called with the correct arguments
        mock_function.assert_called_once_with(
            {"name": "test", "type": "int"}, type_definitions=type_definitions
        )

    def test_no_name(self):
        """Test that an error is raised when the definition has no name"""

        definition = {"fields": [{"name": "test", "type": "int"}]}
        type_definitions = {("int", "dataclass"): lambda x: x}

        with pytest.raises(ValueError):
            create_dataclass(definition, type_definitions)

    def test_no_fields(self):
        """Test that an error is raised when the definition has no fields"""

        definition = {"name": "test"}
        type_definitions = {("int", "dataclass"): lambda x: x}

        with pytest.raises(ValueError):
            create_dataclass(definition, type_definitions)

    def test_make_dataclass_called_with_constructed_fields(self, mocker):
        """Test that `make_dataclass` is called with the correct arguments"""

        mocker.patch(
            "base_schema.constructors.dataclass.get_dataclass_field",
            return_value=("test", int),
        )
        mock_function = mocker.patch(
            "base_schema.constructors.dataclass.make_dataclass"
        )

        definition = {"name": "test", "fields": [{"name": "test", "type": "int"}]}
        type_definitions = {("int", "dataclass"): lambda x: x}

        create_dataclass(definition, type_definitions)

        mock_function.assert_called_once_with(cls_name="test", fields=[("test", int)])


class TestDataclassIntegration:
    """Tests for the dataclass constructor"""

    def test_integration(self):
        """Test that the dataclass constructor can be used to create a dataclass without any patches"""

        schema = {
            "name": "test",
            "fields": [
                {
                    "name": "field_1",
                    "type": "int",
                },
                {
                    "name": "field_2",
                    "type": "str",
                },
            ],
        }

        result = create_dataclass(schema, type_definitions)

        assert isinstance(dataclass, result)


