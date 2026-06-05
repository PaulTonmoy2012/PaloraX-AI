from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

#connecting to mongodb
client = MongoClient(MONGO_URI)
#accessing the database as db
db = client[DATABASE_NAME]

conversations_collection = db["conversations"]