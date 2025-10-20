from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal


class SelectedDate(BaseModel):
    year: int
    month: int
    day: int
    color: str
    textColor: str


class CalendarChange(BaseModel):
    date: SelectedDate
    action: Literal['add', 'remove']


app = FastAPI()

@app.post('/calendar')
async def calendar_change(data: CalendarChange):
    print(data.model_dump())
