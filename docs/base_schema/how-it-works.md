# How `base_schema` works

`base_schema` allows you to define a schema once, then convert it to other schema types like `dataclasses`, `pydantic` `BaseModel`, `pandera` `DataFrameSchema`, or `spark` `StructType`. This allows you to define your schema once, and then use it in multiple places. It does this by passing a standardised dictionary to a constructor function for each schema type.

## Parts of the API

### `base_schema`

Here is a simple example of how you would use `base_schema` to define a schema:

```yaml
name: Person
fields:
  - name: name
    type: str
    description: The person's name
  - name: age
    type: int
    description: The person's age
```

This is a simple schema that defines a `Person` object. It has two fields: `name` and `age`. The `name` field is a `str`, and the `age` field is an `int`. If you passed this schema to `base_schema`, it would return a `base_schema` object. If you converted this to a `dataclass`, it woudl be the equivalent of:

```python
@dataclass
class Person:
    name: str
    age: int
```

If you converted this to a `pydantic` `BaseModel`, it would be the equivalent of:

```python
class Person(BaseModel):
    name: str
    age: int
```

Here is a more complex example that include data validation and type conversion:

```yaml
name: Person
fields:
  - name: name
    type: str
    description: The person's name
  - name: age
    type: int
    description: The person's age
    validators:
      - minimum: 0
      - maximum: 150 
```

This schema is the same as the previous one, but it has some additional features. It has a validator that checks that the `age` field is between 0 and 150. It also has a converter that converts the `age` field to an `int`. If you passed this schema to `base_schema`, it would return a `base_schema` object. If you converted this to a `dataclass`, it woudl be the equivalent of:

```python
@dataclass
class Person:
    name: str
    age: int
```

If you converted this to a `pydantic` `BaseModel`, it would be the equivalent of:

```python
class Person(BaseModel):
    name: str = Field(..., description="The person's name")
    age: conint(ge=0, le=150) = Field(..., description="The person's age")
```

### Constructors

`base_schema` has a number of constructors that allow you to convert your schema to different schema types. Here is a list of the constructors:

- `dataclass`: This constructor takes a schema and returns a `dataclass` object.
- `pydantic`: This constructor takes a schema and returns a `pydantic` `BaseModel` object.
- `pandera`: This constructor takes a schema and returns a `pandera` `DataFrameSchema` object.
- `spark`: This constructor takes a schema and returns a `spark` `StructType` object.

### Validator

The `validator` module allows you to check that your schema is valid. Simply run `validator.validate(schema)` to check that your schema is valid. If it is not valid, it will raise an exception.

### Type definitions

The `base_schema` types are organized into a hierarchy. At the top are the base types:

- `str`
- `int`
- `float`
- `bool`
- `datetime`
- `date`
- `time`
- `timedelta`
- `bytes`

Each of these types defines a method that each of the constructors can use to convert the field to the correct type. For example, the `str` type defines a `to_dataclass` method that converts the field to a `str` in a `dataclass`. Each of these types also define some basic validators that are generally supported by most contstrucors. For example, the `str` type defines a `min_length` validator that checks that the string is at least a certain length. Each of these types also define some basic converters that are generally supported by most contstrucors.