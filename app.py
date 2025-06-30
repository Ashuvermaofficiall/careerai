import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# API Keys from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
HF_API_KEY = os.getenv("HF_API_KEY")

# Gemini AI setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("message", "").strip()
    if not question:
        return jsonify({"message": "Please say something!"}), 400

    try:
        response = model.generate_content(question)
        return jsonify({"message": response.text})
    except Exception as e:
        return jsonify({"message": "AI error: " + str(e)}), 500

@app.route("/score_resume", methods=["POST"])
def score_resume():
    file = request.files['resume']
    text = file.read().decode('utf-8')

    api_url = "https://api-inference.huggingface.co/models/mrm8488/bert-small-finetuned-age_news-classification"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(api_url, headers=headers, data=text)

    if response.status_code == 200:
        result = response.json()
        label = result[0][0]['label']
        score = result[0][0]['score']
        feedback = f"Resume classified as: {label}\nConfidence: {round(score * 100, 2)}%"
    else:
        feedback = "Error analyzing resume."
        score = 0

    return jsonify({"score": round(score * 100, 2), "feedback": feedback})

@app.route("/job_suggestions", methods=["POST"])
def job_suggestions():
    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"jobs": []})

    url = "https://jsearch.p.rapidapi.com/search"
    params = {"query": query, "num_pages": "1"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        jobs_data = response.json()
        jobs = [
            {
                "title": job["job_title"],
                "company": job["employer_name"],
                "location": job["job_city"],
                "url": job["job_apply_link"]
            }
            for job in jobs_data.get("data", [])[:5]
        ]
        return jsonify({"jobs": jobs})
    except Exception as e:
        return jsonify({"jobs": [], "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
