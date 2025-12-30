from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DateOperationType(str, Enum):
    INSERT = "insert"
    DELETE = "delete"


class DateItemSchema(BaseModel):
    calendar_date: date = Field(
        ...,
        alias="date", 
        description="Calendar date in ISO format (YYYY-MM-DD)."
    )
    color_bg: str = Field(
        ...,
        alias="color", 
        description="Background color used to render the calendar cell."
    )
    color_text: str = Field(
        ...,
        alias="textColor", 
        description="Text color used for the date label."
    )

    model_config = {
        "populate_by_name": True
    }


class DatesByUserSchema(BaseModel):
    ok: bool = Field(
        ...,
        description="True if the fetch dates by user succeeded, False otherwise."
    )
    dates: list[DateItemSchema] = Field(
        default=[],
        description="List of dates for the user (empty list if none)."
    )
    message: Optional[str] = Field(
        default=None,
        description="Error description, present if the fetch dates by user failed."
    )


class DateOperationSchema(BaseModel):
    oper_type: DateOperationType = Field(
        ...,
        alias="operType", 
        description="Operation type for the date item: 'insert' to add/update, 'delete' to remove."
    )
    item: DateItemSchema = Field(
        ...,
        description="The date item the operation applies to."
    )

    model_config = {
        "populate_by_name": True
    }


class DateBatchRequestSchema(BaseModel):
    batch: list[DateOperationSchema] = Field(
        ...,
        min_length=1,
        description="List of date items to process in a single batch. Must contain at least one item."
    )


class DateOperationResultSchema(BaseModel):
    ok: bool = Field(
        ...,
        description="True if the operation succeeded, False otherwise."
    )
    operation: DateOperationSchema = Field(
        ...,
        description="The date operation that was applied. Includes the operation type and the date item."
    )
    message: Optional[str] = Field(
        default=None,
        description="Error description, present if the operation failed."
    )


class DateBatchResponseSchema(BaseModel):
    ok: bool = Field(
        ...,
        description="True if the HTTP request succeeded (received a 2xx response), False otherwise."
    )
    results: Optional[list[DateOperationResultSchema]] = Field(
        default=None,
        description="List of results for individual date operations."
    )
    message: Optional[str] = Field(
        default=None,
        description="Error description, present if the HTTP request failed."
    )
