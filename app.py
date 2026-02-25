from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# -----------------------------
# MongoDB Connection
# -----------------------------
MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not set in environment variables")

client = MongoClient(MONGO_URI)
db = client["schoolDB"]       # make sure this matches your DB name
collection = db["students"]   # make sure this matches your collection name

print("✅ MongoDB Connected Successfully")


# -----------------------------
# Root Route (IMPORTANT)
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return "School API Running Successfully 🚀", 200


# -----------------------------
# Chat Route
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"reply": "No JSON data received"}), 400

        student_id = str(data.get("student_id")).strip()
        student_class = str(data.get("class")).strip()
        section = str(data.get("section")).strip()
        message = str(data.get("message")).strip().lower()

        # 🔍 DEBUG PRINT (check logs in Render)
        print("Searching for:", student_id, student_class, section)

        student = collection.find_one({
            "student_id": student_id,
            "class": student_class,
            "section": section
        })

        if not student:
            return jsonify({"reply": "Student not found"}), 404

        if message == "attendance":
            attendance = student.get("attendance", "Not Available")
            return jsonify({
                "reply": f"{student['name']}'s attendance is {attendance}"
            }), 200

        return jsonify({"reply": "Invalid message"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Render Port Binding
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
