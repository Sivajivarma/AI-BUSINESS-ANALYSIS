
import os

from pymongo import MongoClient

from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)


client = MongoClient(MONGO_URI)


db = client["ai_business_analytics"]


# Collections

datasets_collection = db["datasets"]

business_records_collection = db["business_records"]