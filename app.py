from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai
import requests
from resume_parser import parse_resume

load_dotenv()

app = Flask(__name__)

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
HF_API_KEY = os.getenv("HF_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()
    if not question:
        return jsonify({"response": "Please enter a valid question."})

    try:
        response = model.generate_content(question)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

@app.route("/job_suggestions", methods=["POST"])
def job_suggestions():
    query = request.form.get("query", "")
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    params = {"query": query, "page": "1", "num_pages": "1"}
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        jobs = data.get("data", [])[:5]
        suggestions = [f"{job['job_title']} at {job['employer_name']}" for job in jobs]
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        return jsonify({"suggestions": [f"Error: {str(e)}"]})

@app.route("/score_resume", methods=["POST"])
def score_resume():
    file = request.files.get("resume")
    if not file:
        return jsonify({"score": "No resume uploaded."})

    try:
        resume_text = parse_resume(file)
        headers = {
            "Authorization": f"Bearer {HF_API_KEY"},
            "Content-Type": "application/json"
        }
        payload = {"inputs": resume_text}
        response = requests.post(
            "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions",
            headers=headers,
            json=payload
        )
        result = response.json()
        return jsonify({"score": result})
    except Exception as e:
        return jsonify({"score": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
