from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('DB_NAME')]
users_collection = db['users']

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password') 

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

   
    user_id = users_collection.insert_one({
        "username": username,
        "email": email,
        "password": password  
    }).inserted_id

    return jsonify({"message": "User registered successfully",
        "id": str(user_id),
        "toast": "Welcome aboard! Your registration was successful."
        }), 201

if __name__ == '__main__':
    app.run(debug=True)