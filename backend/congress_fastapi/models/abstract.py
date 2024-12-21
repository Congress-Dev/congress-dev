from typing import (
    Annotated,
    Any,
    List,
    get_args,
    get_origin,
    get_type_hints,
)

from humps import camelize
from pydantic import BaseModel
from sqlalchemy import Column


class MappableBase(BaseModel):
    @classmethod
    def sqlalchemy_columns(cls) -> List[Column]:
        columns = []
        # Use get_type_hints to retrieve the annotations
        type_hints = get_type_hints(cls, include_extras=True)
        for field_name, field_type in type_hints.items():
            if get_origin(field_type) is Annotated:
                column: Column = get_args(field_type)[1]

                # Because we have the custom aliaser, we need to retrieve it
                columns.append(column.label(cls.__fields__[field_name].alias))
        return columns

    @classmethod
    def from_sqlalchemy(cls, row: Any):
        field_values = {}
        # type_hints = get_type_hints(cls)
        # for field_name, field_type in type_hints.items():
        #     if hasattr(field_type, '__origin__') and field_type.__origin__ is Annotated:
        #         column = field_type.__args__[1]
        #         field_values[field_name] = getattr(row, column.name)
        #     elif hasattr(field_type, '__origin__'):
        #         print(field_type.__origin__)
        # print(field_values)
        return cls(**row)

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        populate_by_name = True
