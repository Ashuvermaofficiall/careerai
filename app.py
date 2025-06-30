import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import requests

from resume_parser import parse_resume  # Make sure resume_parser.py exists

load_dotenv()

app = Flask(__name__)

# Gemini API setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# RapidAPI setup for job suggestions
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# HuggingFace resume scoring setup
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/ehartford/writer"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question')
    if not question:
        return jsonify({'response': 'Please enter a valid question.'})
    try:
        response = model.generate_content(question)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'response': f"Error: {str(e)}"})


@app.route('/job-suggestions', methods=['POST'])
def job_suggestions():
    query = request.form.get('query')
    if not query:
        return jsonify({'error': 'Empty query'})
    
    url = "https://jsearch.p.rapidapi.com/search"
    params = {"query": query, "num_pages": "1"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        jobs = response.json().get("data", [])
        job_list = [
            {
                "title": job.get("job_title"),
                "company": job.get("employer_name"),
                "location": job.get("job_city"),
                "url": job.get("job_apply_link")
            }
            for job in jobs
        ]
        return jsonify(job_list)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/score-resume', methods=['POST'])
def score_resume():
    file = request.files.get('resume')
    if not file:
        return jsonify({'error': 'No file uploaded'})
    
    text = parse_resume(file)
    if not text:
        return jsonify({'error': 'Could not parse resume'})

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": text
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        score = response.json()
        return jsonify({'score': score})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
