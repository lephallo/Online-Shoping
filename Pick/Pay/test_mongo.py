import os
from pymongo import MongoClient
from dotenv import load_dotenv
import ssl

load_dotenv()

mongo_uri = os.getenv("MONGO_URL")

if not mongo_uri:
    print("❌ MONGO_URL not found in environment variables.")
else:
    print(f"🔍 MONGO_URL: {mongo_uri}")
    try:
        mongo_client = MongoClient(mongo_uri)
        mongo_client.admin.command('ping')
        print("✅ MongoDB connection successful.")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
