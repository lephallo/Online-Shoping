from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Get MongoDB URL from environment variable
MONGO_URL = os.getenv("MONGO_URL")

# Connect to MongoDB (will automatically create the database if it doesn't exist)
client = MongoClient(MONGO_URL, tls=True)

# Create or get the "picknpay" database
db = client["picknpay"]

# Create or get the "ratings" collection
ratings_collection = db["ratings"]


# Function to save ratings (as you had previously)
def save_rating(product_id, rating, user_id, username):
    ratings_collection.insert_one({
        "user_id": user_id,
        "username": username,
        "product_id": product_id,
        "rating": rating
    })

# Create or get the "activity logs" collection
activity_logs_collection = db["activity_logs"]


def log_activity(user_id, username, action, product_id=None, page_url=None):
    activity_logs_collection.insert_one({
        "user_id": user_id,
        "username": username,
        "action": action,  # e.g. "view_product", "click_add_to_cart"
        "product_id": product_id,
        "page_url": page_url,
        "timestamp": datetime.utcnow()
    })
