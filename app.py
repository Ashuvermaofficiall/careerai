import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import pdfplumber

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Configure Gemini model with correct model name
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Chat with Gemini
@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')
    if not question.strip():
        return jsonify({'response': '⚠️ Please ask something...'})
    try:
        response = model.generate_content(question)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'response': f'⚠️ Error: {str(e)}'})

# Resume Upload and Scoring
@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'score': '⚠️ No file uploaded'})
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'score': '⚠️ Empty filename'})
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)

    try:
        with pdfplumber.open(filepath) as pdf:
            text = ''.join(page.extract_text() or '' for page in pdf.pages)

        if not text.strip():
            return jsonify({'score': '⚠️ Could not read resume text.'})

        prompt = f"Give a resume quality score out of 10 with reasoning: {text[:3000]}"
        result = model.generate_content(prompt)
        return jsonify({'score': result.text})
    except Exception as e:
        return jsonify({'score': f'⚠️ Error analyzing resume: {str(e)}'})

# Job Suggestions via RapidAPI
@app.route('/jobs', methods=['POST'])
def get_jobs():
    data = request.get_json()
    query = data.get('query', '')
    url = "https://jsearch.p.rapidapi.com/search"
    params = {
        "query": query,
        "page": "1",
        "num_pages": "1"
    }
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST")
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        jobs = response.json().get("data", [])
        if not jobs:
            return jsonify({"jobs": ["❌ No jobs found for your query."]})

        job_results = []
        for job in jobs[:5]:
            title = job.get("job_title", "N/A")
            company = job.get("employer_name", "N/A")
            location = job.get("job_city", "N/A")
            link = job.get("job_apply_link", "#")
            job_results.append(f"{title} at {company} ({location}) - [Apply Here]({link})")

        return jsonify({"jobs": job_results})
    except Exception as e:
        return jsonify({"jobs": [f"⚠️ Error fetching jobs: {str(e)}"]})

if __name__ == '__main__':
    app.run(debug=True)