from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routers import bot
import uvicorn

app = FastAPI()
app.include_router(bot.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
