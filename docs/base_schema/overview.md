# Base schema overview

`base_schema` allows you to define a schema once, then convert it to other schema types like `dataclasses`, `pydantic` `BaseModel`, `pandera` `DataFrameSchema`, or `spark` `StructType`. This allows you to define your schema once, and then use it in multiple places.

## Why use `base_schema`?

Schemas are an important part of any data workflow. They allow you to define the structure of your data, and then validate it. This is especially important when you are working with data that is coming from multiple sources, or when you are working with data that is being transformed in multiple steps. If you don't have a schema, it is easy to make mistakes that can lead to bugs, or even worse, data that is incorrect.

But depending on how you use your data, you may need to use different schema types. For example, if you are using `pandas` to do some data analysis, you may want to use `pandera` `DataFrameSchema`. But if you are using `spark` to do some data analysis, you may want to use `spark` `StructType`. And if you are using `pydantic` to do some data validation, you may want to use `pydantic` `BaseModel`. 

`base_schema` allows you to define your schema once, and then convert it to any of these schema types. 

## How to use `base_schema`

