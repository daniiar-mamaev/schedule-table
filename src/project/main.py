import os

import motor.motor_asyncio
from bson import ObjectId
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
    task: str | None = None
    start_day: str | None = None
    end_day: str | None = None


class Schedule(BaseModel):
    blocks: list[Block]


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/schedule")
async def get_schedule():
    blocks = await collection.find().to_list(1000)
    for block in blocks:
        block["_id"] = str(block["_id"])
    return {"blocks": blocks}


@app.post("/person/add")
async def add_person(block: Block):
    block_dict = block.model_dump()
    result = await collection.insert_one(block_dict)
    return {"_id": str(result.inserted_id)}


@app.post("/task/add")
async def add_task(block: Block):
    form_data = block.model_dump()
    person = form_data.get("person")
    task = form_data.get("task")
    start_day = form_data.get("start_day")
    end_day = form_data.get("end_day")
    await collection.update_one(
        {"person": person, "task": None}, {"$set": {"task": task, "start_day": start_day, "end_day": end_day}}
    )

    return {"message": "Task added successfully"}


# @app.post("/task/edit")
# async def edit_task(body: dict):
#     body_id = body.pop("_id")
#     await collection.update_one({"_id": ObjectId(body_id)}, {"$set": body})

#     return {"message": "Task updated successfully"}


# @app.get("/people")
# async def get_people():
#     people = await collection.find({}).to_list(1000)
#     response = {}
#     for person in people:
#         person["_id"] = str(person["_id"])
#         response[person["person"]] = str(person["_id"])
#     print(response)
#     return response
