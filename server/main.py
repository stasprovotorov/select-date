from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Literal, Annotated


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
async def calendar_change(request: Request, data: CalendarChange):
    print('Body data:', data.model_dump(), sep='\n')
    print('Header data:', request.headers, sep='\n')
