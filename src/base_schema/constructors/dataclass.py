"""Constructor for dataclasses."""
from dataclasses import make_dataclass

def create_dataclass(definition: dict, type_definitions: dict):
    """Create a dataclass type from a definition.
    
    Args:
        definition (dict): The definition.
    
    Returns:
        type: The dataclass type.
    """
    name = definition["name"]
    dataclass_fields = []
    
    for field in definition["fields"]:
        name = field["name"]
        property_type = field["type"]

        constructor = type_definitions[(property_type, "dataclass")]    

        field = constructor(name)
        dataclass_fields.append(field)

    return make_dataclass(
        cls_name=name, 
        fields=dataclass_fields
        )
    
    #