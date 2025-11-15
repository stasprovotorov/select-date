from pydantic import BaseModel, Field


class SelectedDateSchema(BaseModel):
    year: int = Field(ge=1)
    month: int = Field(ge=0, le=11)
    day: int = Field(ge=1, le=31)
    color: str = Field(min_length=1)
    textColor: str = Field(min_length=1)
