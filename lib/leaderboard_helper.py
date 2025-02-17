import pymongo
import os

client = pymongo.MongoClient(os.getenv('mongo_url'))
db = client.quiz
coll = db.leaderboard

def increment_correct(user_id, guild_id , theme):
    user = coll.find_one({"_id": user_id})

    if user is None:
        coll.insert_one({"_id": user_id, "guild_id": guild_id, f"{theme}": { "amount_correct": 1}})
        return True

    coll.update_one({"_id": user_id}, {"$inc": {f"{theme}.amount_correct": 1}})
    return True

def get_correct_answers(user_id):
    user = coll.find_one({"_id": user_id})

    if user is None:
        return 0

    correct = int(user["amount_correct"])
    return correct
