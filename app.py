import streamlit as st
import ollama
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import time  # Import time module

# Load environment variables
load_dotenv()

# Get LLM Response
def get_llm_response(input_prompt):
    start_time = time.time()  # Record the start time
    try:
        llmResponse = ollama.generate(
            model='llama3',
            prompt=input_prompt,
            stream=False)
        end_time = time.time()  # Record the end time
        response_time = end_time - start_time  # Calculate response time
        return llmResponse.response, response_time
    except Exception as e:
        print(f"Error calling Ollama: {e}")

# PDF to Text Parser
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Streamlit App
st.title("Smart ATS")
st.text("Improve Your Resume ATS Compatibility")

jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload your resume as a PDF")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None and jd.strip():
        # Extract resume text from the uploaded PDF
        resume_text = input_pdf_text(uploaded_file)
        
        # Construct the prompt dynamically
        input_prompt = f"""
        Hey Act Like a skilled or very experienced ATS (Application Tracking System)
        with a deep understanding of tech field, software engineering, data science, data analyst,
        and big data engineer. Your task is to evaluate the resume based on the given job description.
        You must consider that the job market is very competitive, and you should provide 
        the best assistance for improving the resumes. Assign the percentage match based 
        on the JD, assign rating/10 based on JD, list the missing keywords with high accuracy and give an AI response wheather we shoukd hire or not, with proper reason.
        
        Resume: {resume_text}
        Description: {jd}
        
        I want the response in one single string having the structure:
        {{"JD Match":"%","Rating":"0/10","AI response":"","MissingKeywords":[],"Profile Summary":""}}
        """
        
        # Get LLM response and response time
        response, response_time = get_llm_response(input_prompt)
        # Find the starting index of the JSON part (the first curly brace)
        json_start_index = response.find("{")

        # Find the ending index of the JSON part (the last closing curly brace)
        json_end_index = response.rfind("}")

        # Extract the JSON portion of the string
        json_str = response[json_start_index:json_end_index + 1].strip()

        # Extract the note (everything after the JSON part)
        note_start_index = json_end_index + 1  # After the last closing brace of JSON
        note_str = response[note_start_index:].strip()

        print(json_str, note_str)

        if response is None:
            st.error("Error: Received no response from the LLM.")
        else:
            # Debugging: Print the raw response to inspect it
            # st.write("Raw Response from Model:")
            # st.write(response)  # This will display the raw response in the app
            
            # Display the response time
            st.write(f"Response Time: {response_time:.2f} seconds")
            
            # Try to parse the response as JSON
            try:
                response_json = json.loads(json_str)
                st.subheader("ATS Evaluation")
                st.write(f"**JD Match**: {response_json.get('JD Match', 'N/A')}")
                st.write(f"**Rating**: {response_json.get('Rating', '0')}")
                st.write(f"**Response**: {response_json.get('AI response', 'N/A')}")
                st.write(f"**Missing Keywords**: {', '.join(response_json.get('MissingKeywords', []))}")
                st.write(f"**Profile Summary**: {response_json.get('Profile Summary', 'N/A')}")
            except json.JSONDecodeError:
                st.error("Error: Unable to parse the response from the model.")
                st.write(response)  # Display raw response for debugging
            
    elif not jd.strip():
        st.error("Please paste a job description.")
    else:
        st.error("Please upload a PDF resume.")




# Add "Developed by" in bottom corner
st.markdown("""
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            background-color: rgba(0, 0, 0, 0.1);
            color: #555;
        }
    </style>
    <div class="footer">
        Developed by Kamalesh
    </div>
""", unsafe_allow_html=True)