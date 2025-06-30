import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from resume_parser import parse_resume  # Make sure resume_parser.py exists
from gtts import gTTS

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
HF_API_KEY = os.getenv("HF_API_KEY")

app = Flask(__name__)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-pro")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        question = request.json.get("question")
        if not question:
            return jsonify({"error": "Please enter a valid question"}), 400

        response = model.generate_content(question)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    tts = gTTS(text)
    tts.save("static/voice.mp3")
    return jsonify({"url": "/static/voice.mp3"})

@app.route("/job_suggestions", methods=["POST"])
def job_suggestions():
    query = request.json.get("query")
    if not query:
        return jsonify({"error": "No job query provided"}), 400

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    params = {"query": query, "page": "1", "num_pages": "1"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        jobs = response.json().get("data", [])
        return jsonify(jobs[:5])
    else:
        return jsonify({"error": "Failed to fetch job suggestions"}), 500

@app.route("/resume_score", methods=["POST"])
def resume_score():
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume_file = request.files["resume"]
    text = parse_resume(resume_file)

    prompt = f"Evaluate the following resume content and give a score out of 10:\n\n{text}"
    response = model.generate_content(prompt)

    return jsonify({"score": response.text})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
