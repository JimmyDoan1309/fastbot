from fastapi import FastAPI, Depends
from .routers import bot
import uvicorn

app = FastAPI()
app.include_router(bot.router)
