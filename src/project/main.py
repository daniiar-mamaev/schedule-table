import os

import motor.motor_asyncio
from bson import ObjectId
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
collection_person = db.person
collection_task = db.task


class Person(BaseModel):
    name: str


class Task(BaseModel):
    person: str
    task: str | None = None
    start_day: str | None = None
    end_day: str | None = None


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/schedule")
async def get_schedule():
    person_list = await collection_person.find().to_list(1000)
    person_dict = {}
    for person in person_list:
        person["_id"] = str(person["_id"])
        person_dict[person["_id"]] = person["name"]
    task_list = await collection_task.find().to_list(1000)
    for task in task_list:
        task["_id"] = str(task["_id"])
        task["person"] = person_dict[task["person"]]

    return {"task_list": task_list}


@app.post("/person/add")
async def add_person(person: Person):
    existing_person = await collection_person.find_one({"name": person.name})
    if existing_person:
        return {"message": "A person with this name already exists"}

    insert_result = await collection_person.insert_one({"name": person.name})
    person_id = insert_result.inserted_id

    new_task = Task(person=str(person_id)).model_dump()
    await collection_task.insert_one(new_task)

    return {"message": "Person added successfully"}


@app.post("/person/get")
async def get_person(body: dict):
    task_id = body.get("task_id")
    task = await collection_task.find_one({"_id": ObjectId(task_id)})
    person = await collection_person.find_one({"_id": task["person"]})
    return person["name"]


@app.get("/get_persons")
async def get_persons():
    people = await collection_person.find({}, {"_id": 0}).to_list(1000)
    people = [person["name"] for person in people]
    print(people)
    return people


@app.post("/task/update")
async def add_task(body: dict):
    task = body.get("task")
    start_day = body.get("start_day")
    end_day = body.get("end_day")
    task_id = body.get("task_id")
    task = await collection_task.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"task": task, "start_day": start_day, "end_day": end_day}},
    )

    return {"message": "Task updated successfully"}


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
