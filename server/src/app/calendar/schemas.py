from datetime import date
from enum import Enum
from pydantic import BaseModel, Field


class DateOperationType(str, Enum):
    INSERT = "insert"
    DELETE = "delete"


class DateItemSchema(BaseModel):
    calendar_date: date = Field(alias="calendarDate")
    color_bg: str = Field(alias="colorBg")
    color_text: str = Field(alias="colorText")

    model_config = {
        "populate_by_name": True
    }


class DatesForUserSchema(BaseModel):
    ok: bool
    item: list[DateItemSchema] = []
    message: str | None = None


class DateOperationSchema(BaseModel):
    oper_type: DateOperationType = Field(alias="operType")
    item: DateItemSchema

    model_config = {
        "populate_by_name": True
    }


class DateBatchRequestSchema(BaseModel):
    batch: list[DateOperationSchema] = Field(min_length=1)


class DateOperationResultSchema(BaseModel):
    ok: bool
    operation: DateOperationSchema
    message: str | None = Field(None)


class DateBatchResponseSchema(BaseModel):
    ok: bool
    result: list[DateOperationResultSchema] | None = Field(None)
    message: str | None = Field(None)
