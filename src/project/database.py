import os

import motor.motor_asyncio
from pydantic import BaseModel

mongo_pass = os.getenv("MONGO_DB_PASSWORD")
client = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb+srv://myAtlasDBUser:{mongo_pass}@myatlasclusteredu.cjz9tzt.mongodb.net/?retryWrites=true&w=majority&appName=myAtlasClusterEDU"
)
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
