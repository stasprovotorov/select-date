from fastapi import FastAPI, Header, status
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()


class SelectedDate(BaseModel):
    year: int
    month: int
    day: int
    color: str | None = None
    text_color: str | None = None


@app.post('/calendar/{date}', status_code=status.HTTP_201_CREATED)
async def calendar_select_date(
    date: str, 
    date_data: SelectedDate,
    authorization: Annotated[str | None, Header()]
):
    print('FastAPI POST')
    print(date)
    print(authorization)
    print(date_data)

    return date_data


@app.delete('/calendar/{date}', status_code=status.HTTP_204_NO_CONTENT)
async def calendar_deselect_date(
    date: str,
    authorization: Annotated[str | None, Header()]
):
    print('FastAPI DELETE')
    print(date)
    print(authorization)
