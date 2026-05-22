import pymongo
from config import DB_URI, DB_NAME

_client   = pymongo.MongoClient(DB_URI)
_database = _client[DB_NAME]
user_data = _database["users"]


async def present_user(user_id: int) -> bool:
    return bool(user_data.find_one({"_id": user_id}))


async def add_user(user_id: int) -> None:
    user_data.insert_one({"_id": user_id})


async def full_userbase() -> list:
    return [doc["_id"] for doc in user_data.find()]


async def del_user(user_id: int) -> None:
    user_data.delete_one({"_id": user_id})
