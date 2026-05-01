from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os

# Initialize Flask App
app = Flask(__name__)

cors_origins = os.getenv("CORS_ORIGINS", "*")
CORS(app, resources={r"/*": {"origins": cors_origins}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    with open(os.path.join(BASE_DIR, "career_rf_model.pkl"), "rb") as f:
        model = pickle.load(f)
except Exception as e:
    model = None

try:
    with open(os.path.join(BASE_DIR, "career_tfidf.pkl"), "rb") as f:
        vectorizer = pickle.load(f)
except Exception as e:
    vectorizer = None

try:
    with open(os.path.join(BASE_DIR, "career_label_encoder.pkl"), "rb") as f:
        le = pickle.load(f)
except Exception as e:
    le = None

# API Home Route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Career Prediction API is running 🚀"})

# Prediction Route
@app.route("/predict", methods=["POST"])
def predict():
    try:
        if model is None or vectorizer is None:
            return jsonify({"error": "Model or vectorizer not loaded properly"}), 500

        data = request.get_json()
        # Extract the 4 input fields
        course = data.get("course", "")
        specialization = data.get("specialization", "")
        interests = data.get("interests", "")
        skills = data.get("skills", "")

        if not any([course, specialization, interests, skills]):
            return jsonify({"error": "All input fields are empty"}), 400

        combined_input = f"{course} {specialization} {interests} {skills}".strip()
        X_input = vectorizer.transform([combined_input])
        prediction = model.predict(X_input)[0]

        if isinstance(prediction, (np.generic, np.ndarray)):
            prediction = prediction.item()

        if le is not None:
            prediction = le.inverse_transform([prediction])[0]
        else:
            prediction = str(prediction)

        return jsonify({"predicted_career": prediction})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    debug_flag = os.getenv("FLASK_DEBUG", "0") in ("1", "true", "True")
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_flag)
