import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles

from app.internal.alive import clean_client_task
from app.internal.alive import RefreshAliveMiddleware
from app.internal.template import get_template_response
from app.routers.room import room
from app.routers.user import user
from app.routers.websocket import websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    clean_client_thread = threading.Thread(target=clean_client_task, daemon=True)
    clean_client_thread.start()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(RefreshAliveMiddleware)

app.include_router(user)
app.include_router(room)
app.include_router(websocket)


@app.get("/")
async def get_home(request: Request):
    return get_template_response(request=request, name="index.html")
