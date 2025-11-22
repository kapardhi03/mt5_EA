from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://kapardhikannekanti_db_user:3XoNc2gtr9lGY4oi@mt5-cluster.njyntuk.mongodb.net/?retryWrites=true&w=majority&appName=mt5-cluster"
client = MongoClient(uri, server_api=ServerApi("1"))

try:
    client.admin.command("ping")
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("❌ Connection failed:", e)
