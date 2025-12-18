from pydantic import BaseModel, Field


class SelectedDateSchema(BaseModel):
    year: int = Field(ge=1)
    month: int = Field(ge=0, le=11)
    day: int = Field(ge=1, le=31)
    color: str | None = Field(default=None, min_length=1)
    textColor: str | None = Field(default=None, min_length=1)


class DateBatchItem(BaseModel):
    action: str
    date: str
    color: str | None = None
    textColor: str | None = None


class DateBatch(BaseModel):
    batch: list[DateBatchItem]


class ApiDateItemResult(BaseModel):
    ok: bool
    action: str
    date: str
    color: str | None = None
    textColor: str | None = None
    message: str | None = None


class ApiDateBatchResultSuccessed(BaseModel):
    ok: bool = True
    results: list[ApiDateItemResult]


class ApiDateBatchResultFailed(BaseModel):
    ok: bool = False
    message: str
