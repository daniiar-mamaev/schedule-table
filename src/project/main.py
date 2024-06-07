from bson import ObjectId
from fastapi import APIRouter, Request

from .database import Person, Task, collection_person, collection_task
from .dependencies import templates

router = APIRouter()


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/schedule")
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


@router.post("/person/add")
async def add_person(person: Person):
    existing_person = await collection_person.find_one({"name": person.name})
    if existing_person:
        return {"message": "A person with this name already exists"}

    insert_result = await collection_person.insert_one({"name": person.name})
    person_id = insert_result.inserted_id

    new_task = Task(person=str(person_id)).model_dump()
    await collection_task.insert_one(new_task)

    return {"message": "Person added successfully"}


@router.post("/person/get")
async def get_person(body: dict):
    task_id = body.get("task_id")
    task = await collection_task.find_one({"_id": ObjectId(task_id)})
    person = await collection_person.find_one({"_id": task["person"]})
    return person["name"]


@router.get("/get_persons")
async def get_persons():
    people = await collection_person.find({}, {"_id": 0}).to_list(1000)
    people = [person["name"] for person in people]
    print(people)
    return people


@router.post("/task/update")
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


@router.post("/task/delete")
async def delete_task(body: dict):
    task_id = body.get("task_id")
    await collection_task.update_one(
        {"_id": ObjectId(task_id)}, {"$set": {"task": None, "start_day": None, "end_day": None}}
    )
    return {"message": "Task deleted successfully"}
