import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_cors import CORS
from functools import reduce



load_dotenv()
app = Flask(__name__)
CORS(app)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(GOOGLE_API_KEY)
MONGO_URI = os.getenv('MONGODB_URI')
cluster = MongoClient(MONGO_URI)
db = cluster["leftover"]
collection = db["foodrequests"]

model = genai.GenerativeModel('gemini-pro')
@app.get("/quote")
def quote():
    response = model.generate_content("Give One Food statistics as a single string statement\n", stream=False)
    return response.text


@app.post("/chat")
def chat():
    request_body = request.json.get("message")
    response = model.generate_content("You are CrumsAI, an AI Assistant that can help with food leftover managment, you can help in giving ideas for food management, food planning and leftover management.\nRules:(1. Reply should be short and consise 2. Do not reutrn markdown of any kind of formatting)\n"+request_body, stream=False)
    return response.text

@app.post("/get_insights")
def get_insights():
    user_uid = request.json.get("uid")
    insights = collection.find({"userId":user_uid})
    insightHistory = []
    for insight in insights:
        insightHistory.append(dict({
            "quantity":insight["quantity"],
            "date":insight["createdAt"]
        }))
    # change datetime object date to simple date
    for insight in insightHistory:
        insight["date"] = insight["date"].strftime("%Y-%m-%d")
    
    # if there are more than on quantity for a single date, add them up
    insightHistory = sorted(insightHistory, key=lambda x: x["date"])


    
    return jsonify(insightHistory)

    
    

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
