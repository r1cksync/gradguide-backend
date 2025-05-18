from pymongo import MongoClient
client = MongoClient("mongodb+srv://sagnik23102:j9TildStvOeklXmg@gradguide.zdinpa4.mongodb.net/?retryWrites=true&w=majority&appName=gradguide")
db = client["gradguide"]
print(db["college_data"].count_documents({}))