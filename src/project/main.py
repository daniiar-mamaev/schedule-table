import os

import motor.motor_asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


def create_app() -> FastAPI:
    debug = not os.getenv("APP_ENV") == "PROD"
    app = FastAPI(
        debug=debug,
        openapi_url="/openapi.json" if debug else None,
        docs_url="/docs" if debug else None,
        redoc_url="/redoc" if debug else None,
        title="Knowledge Hub",
        version="0.1.0",
    )
    current_dir = os.path.dirname(os.path.realpath(__file__))
    static_dir = os.path.join(current_dir, ".", "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    return app


app = create_app()

current_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(current_dir, ".", "templates")
templates = Jinja2Templates(directory=template_dir)

# MongoDB setup
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client.schedule_db
collection = db.schedule


# Pydantic models
class Block(BaseModel):
    person: str
    task: str
    start_day: str
    end_day: str


class Schedule(BaseModel):
    blocks: list[Block]


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/schedule", response_model=Schedule)
async def get_schedule():
    blocks = await collection.find().to_list(1000)
    return {"blocks": blocks}


@app.post("/api/schedule")
async def update_schedule(schedule: Schedule):
    await collection.drop()
    await collection.insert_many([block.dict() for block in schedule.blocks])
    return {"message": "Schedule updated successfully"}
