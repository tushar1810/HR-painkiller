# main.py

from cv_reader import extract_text_from_pdf, extract_cgpa, extract_project_summary, extract_candidate_name,generate_detailed_summary
import os

import requests

API_URL = "https://api-inference.huggingface.co/models/tuner007/pegasus_summarizer"
headers = {"Authorization": "Bearer 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"}



def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()




def process_cv(pdf_folder):
    cv_data = []  # List to store (candidate_name, cgpa) pairs

    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            text = extract_text_from_pdf(pdf_path)
            cgpa = extract_cgpa(text)
            project_summary = extract_project_summary(text)
            # Extract candidate name as the first string before a newline character
            candidate_name = extract_candidate_name(text)
            # Append the (candidate_name, cgpa) pair to the list
            cv_data.append((candidate_name, cgpa,project_summary))
            

    # Sort the list based on CGPA (considering None as the lowest value)
    cv_data.sort(key=lambda x: float(x[1]) if x[1] is not None else float('-inf'), reverse=True)

    # Print the sorted pairs
    for candidate_name, cgpa, project_summary in cv_data:
        if project_summary:
            detailed_summary = query(project_summary)
            print(f"Candidate: {candidate_name}\nCGPA: {cgpa}\nDetailed Project Summary: {detailed_summary}\n{'-'*30}")
					# print(f"Candidate: {candidate_name}\nCGPA: {cgpa}\nProject Summary: {project_summary}\n{'-'*30}")



def main():
    # query()
    pdf_path = 'cv.pdf'  # Change this to the path of your PDF file
    text = extract_text_from_pdf(pdf_path)
    cgpa = extract_cgpa(text)
    name = extract_candidate_name(text)
    print(f"Extracted candidate name: {name}")
    if cgpa:
        print(f"Extracted CGPA: {cgpa}")
    else:
        print("CGPA not found in the PDF.")

if __name__ == "__main__":
    cv_folder = "all_cv"
    process_cv(cv_folder)
    # main()



	
