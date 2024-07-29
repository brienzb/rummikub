from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles

from app.internal.templates import get_template_response
from app.routers.room import room
from app.routers.websocket import ws

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(room)
app.include_router(ws)


@app.get("/")
async def get_home(request: Request):
    return get_template_response(request=request, name="index.html")
