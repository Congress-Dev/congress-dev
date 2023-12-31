from pydantic import BaseModel

from typing import Any, List, get_type_hints, Annotated, get_args, get_origin
from typing import TypeVar, Generic, Type, Any
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
                columns.append(column.label(field_name))
        return columns

    @classmethod
    def from_sqlalchemy(cls, row: Any):
        field_values = {}
        # type_hints = get_type_hints(cls)
        # for field_name, field_type in type_hints.items():
        #     if hasattr(field_type, '__origin__') and field_type.__origin__ is ColMap:
        #         column = field_type.__args__[1]
        #         field_values[field_name] = getattr(row, column.name)
        return cls(**field_values)