from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# -----------------------------
# MongoDB Connection (Use ENV variable in Render)
# -----------------------------
MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["schoolDB"]          # your DB name
collection = db["students"]      # your collection name

# -----------------------------
# Chat Endpoint
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        student_id = data.get("student_id")
        student_class = data.get("class")
        section = data.get("section")
        message = data.get("message")

        # 🔍 Find student
        student = collection.find_one({
            "student_id": str(student_id),
            "class": str(student_class),
            "section": str(section)
        })

        if not student:
            return jsonify({"reply": "Student not found. Please check student ID."}), 404

        if message.lower() == "attendance":
            attendance = student.get("attendance", "Not Available")
            return jsonify({
                "reply": f"{student['name']}'s attendance is {attendance}"
            }), 200

        return jsonify({"reply": "Invalid message"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Run for Render
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
