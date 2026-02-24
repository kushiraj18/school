import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# -----------------------------
# FLASK APP
# -----------------------------
app = Flask(__name__)

# -----------------------------
# MONGODB CONNECTION (CORRECTED)
# -----------------------------
MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI environment variable not set")

client = MongoClient(MONGO_URI)
db = client["shopping"]
collection = db["Student"]

print("✅ MongoDB Connected Successfully")

# -----------------------------
# ML TRAINING
# -----------------------------
training_sentences = [
    "attendance", "my attendance", "attendance percentage",
    "result", "results", "pass or fail",
    "marks", "show marks", "subject marks",
    "fees", "fee details", "pending fees",
    "exams", "exam details", "term exam",
    "transport", "bus details", "transport details"
]

training_labels = [
    "attendance", "attendance", "attendance",
    "results", "results", "results",
    "marks", "marks", "marks",
    "fees", "fees", "fees",
    "exams", "exams", "exams",
    "transport", "transport", "transport"
]

vectorizer = TfidfVectorizer(stop_words="english")
X_train = vectorizer.fit_transform(training_sentences)

model = MultinomialNB()
model.fit(X_train, training_labels)

print("✅ ML Model Trained Successfully")

def predict_intent(text):
    vec = vectorizer.transform([text.lower()])
    return model.predict(vec)[0]

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return "School Student API is Running 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    student_id = data.get("student_id")
    user_query = data.get("message", "").strip()
    student_class = data.get("class", "").strip().upper()
    student_section = data.get("section", "").strip().upper()

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    if not user_query:
        return jsonify({"error": "message is required"}), 400

    intent = predict_intent(user_query)

    student = collection.find_one(
        {
            "student_id": student_id,
            "class": {"$regex": f"^{student_class}$", "$options": "i"} if student_class else {"$exists": True},
            "section": {"$regex": f"^{student_section}$", "$options": "i"} if student_section else {"$exists": True}
        },
        {"_id": 0}
    )

    if not student:
        return jsonify({"reply": "Student not found. Please check student ID, class, and section."}), 404

    if intent == "attendance":
        reply = student.get("attendance", {})
    elif intent == "marks":
        reply = student.get("marks", {})
    elif intent == "results":
        reply = student.get("result", {})
    elif intent == "fees":
        reply = student.get("fees", {})
    elif intent == "exams":
        reply = student.get("exams", {})
    elif intent == "transport":
        reply = student.get("transport", {})
    else:
        reply = "Sorry I couldn't understand."

    return jsonify({
        "intent": intent,
        "reply": reply
    })

# -----------------------------
# RUN FOR PRODUCTION
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
