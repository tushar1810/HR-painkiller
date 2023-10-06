import os
import re
from flask import Flask, render_template, request
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
import openai
from nltk.tokenize import sent_tokenize
from werkzeug.utils import secure_filename

import requests

app = Flask(__name__)


API_URL = "https://api-inference.huggingface.co/models/tuner007/pegasus_summarizer"
headers = {"Authorization": "Bearer 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"}

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Set your Azure Text Analytics API key and endpoint
azure_key = 'your-azure-key'
azure_endpoint = 'your-azure-endpoint'

# Create a Text Analytics client
credential = AzureKeyCredential(azure_key)
text_analytics_client = TextAnalyticsClient(endpoint=azure_endpoint, credential=credential)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()

        # print(text)
    return text
    # Your existing code for extracting text from a PDF

def extract_cgpa(text):
    column_name_pattern = re.compile(r'GPA\s*/\s*Marks\s*\(%\)', re.IGNORECASE)
    match_column = column_name_pattern.search(text)

    if match_column:
        # Look for the value after the column name
        value_pattern = re.compile(r'\b\d+(\.\d+)?\b')
        match_value = value_pattern.search(text[match_column.end():])

        if match_value:
            return match_value.group()
    return None
    # Your existing code for extracting CGPA

def extract_candidate_name(text):
    lines = text.split('\n')
    candidate_name = lines[0].strip() if lines else None
    return candidate_name
    # Your existing code for extracting candidate name

def extract_project_summary(text):
    #working
    # Extract projects section based on the specific label "PROJECTS"
    # projects_pattern = re.compile(r'PROJECTS(.*?)(?=(PROJECTS|$))', re.DOTALL | re.IGNORECASE)
    projects_pattern = re.compile(r'PROJECTS(.*?)(?=(TECHNICAL SKILLS|$))', re.DOTALL | re.IGNORECASE)
    match = projects_pattern.search(text)

    if match:
        projects_text = match.group(1).strip()
        # print(projects_text)
        # Split projects based on bullet points
        projects_list = re.split(r'\s*•\s*', projects_text)

        # Use sentence summarization (extract the first sentence as a summary) for each project
        summaries = []
        for project in projects_list:
            if project:
                # Split the project details based on hyphens
                details = re.split(r'\s*-\s*', project)
                # Use the first sentence of the first detail as a summary
                summary = sent_tokenize(details[0])[0] if details else None
                summaries.append(summary)

        # Combine project summaries into a single paragraph
        summary_paragraph = ' '.join(summaries)

        return summary_paragraph if summaries else None

    return None


def process_cv(cv_text):
    cgpa = extract_cgpa(cv_text)
    candidate_name = extract_candidate_name(cv_text)
    project_details = extract_project_summary(cv_text)

    if project_details:
        detailed_summary = query(project_details)
        return f"Candidate: {candidate_name}\nCGPA: {cgpa}\nDetailed Project Summary: {detailed_summary}"
    else:
        return "No projects found in the CV."

@app.route('/', methods=['GET', 'POST'])

        # if cv_file and cv_file.filename.endswith('.pdf'):


def index():
    result = None
    if request.method == 'POST':
        cv_file = request.files['cv_file']
        if cv_file and allowed_file(cv_file.filename):
             filename = secure_filename(cv_file.filename)
             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
             cv_file.save(filepath)
             cv_text = extract_text_from_pdf(filepath)
             result = process_cv(cv_text)
            #  os.remove(filepath)
        else:
                    result = "Please upload a PDF file."
    return render_template('index.html', result=result)

		#  return render_template('index.html', result=result)
    


if __name__ == '__main__':
    app.run(debug=True)
