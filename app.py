from flask import Flask, request, jsonify
from pymongo import MongoClient, errors
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Подключение к базе данных
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users_collection = db["users"]


# Test route
@app.route("/", methods=["GET"])
def index():
    return "Server is running!"


# Route for creating users
@app.route("/users", methods=["POST"])
def create_user():
    user_data = request.get_json()
    if not user_data:
        return jsonify({"error": "No data"}), 400

    username = user_data.get("username")
    email = user_data.get("email")
    password = user_data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Username, email and password are required"}), 400

    # Same name or email check
    existing_user = users_collection.find_one(
        {"$or": [{"email": email}, {"username": username}]}
    )
    if existing_user:
        if existing_user.get("email") == email:
            return jsonify({"error": "User with this email already exists"}), 400
        elif existing_user.get("username") == username:
            return jsonify({"error": "User with this username already exists"}), 400

    # Hash password
    hashed_password = generate_password_hash(password)

    # User creation
    new_user = {"username": username, "email": email, "password": hashed_password}

    # Add a user to the collection
    try:
        result = users_collection.insert_one(new_user)
    except errors.PyMongoError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    return jsonify({"message": "User created", "user_id": str(result.inserted_id)}), 201


if __name__ == "__main__":
    app.run(debug=True)
