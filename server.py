from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

try:
    client = MongoClient(os.getenv('MONGO_URI'), serverSelectionTimeoutMS=5000)
    db = client[os.getenv('DB_NAME')]
    users_collection = db['users']
    client.admin.command('ping')
    print("Connected to MongoDB successfully.")
except errors.ServerSelectionTimeoutError as err:
    print(f"Failed to connect to MongoDB: {err}")
    # Don't exit, let the app start even if DB connection fails

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({"error": "All fields are required"}), 400

        if users_collection.find_one({"email": email}):
            return jsonify({"error": "User already exists"}), 400

        user_id = users_collection.insert_one({
            "username": username,
            "email": email,
            "password": password  # In production, hash this password
        }).inserted_id

        return jsonify({
            "message": "User registered successfully",
            "id": str(user_id),
            "toast": "Welcome aboard! Your registration was successful."
        }), 201
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({"error": "Email and password are required"}), 400

        user = users_collection.find_one({"email": email})

        if not user or user["password"] != password:
            return jsonify({"error": "Invalid email or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user": {
                "username": user["username"],
                "email": user["email"],
            },
            "toast": "Welcome back! You've successfully logged in."
        }), 200
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)