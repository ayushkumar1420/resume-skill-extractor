# app.py
from flask import Flask, render_template, request, jsonify
import os
import PyPDF2
import docx
from collections import Counter
import re
import spacy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

# Load Spacy model for NLP processing
nlp = spacy.load('en_core_web_sm')

# Common skills database (can be expanded)
SKILLS_DB = [
    'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin',
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'laravel',
    'machine learning', 'deep learning', 'ai', 'data analysis', 'data science',
    'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'aws', 'azure', 'google cloud',
    'docker', 'kubernetes', 'git', 'jenkins', 'ci/cd', 'rest api', 'graphql',
    'project management', 'agile', 'scrum', 'devops', 'cybersecurity', 'networking',
    'linux', 'windows server', 'bash', 'powershell', 'excel', 'tableau', 'power bi',
    'photoshop', 'illustrator', 'ui/ux', 'figma', 'adobe xd', 'seo', 'digital marketing'
]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            return file.read()
    return ""

def preprocess_text(text):
    # Convert to lowercase and remove special characters
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

def extract_skills(text):
    # Process text with Spacy
    doc = nlp(text)
    
    # Extract noun chunks and named entities that might represent skills
    potential_skills = set()
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        if any(skill in chunk_text for skill in SKILLS_DB):
            potential_skills.add(chunk_text)
    
    for ent in doc.ents:
        if ent.label_ in ['SKILL', 'PRODUCT', 'ORG']:  # These labels often contain skills
            ent_text = ent.text.lower()
            if any(skill in ent_text for skill in SKILLS_DB):
                potential_skills.add(ent_text)
    
    # Simple keyword matching with skills database
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    for skill in SKILLS_DB:
        if skill in ' '.join(tokens):
            potential_skills.add(skill)
    
    # Additional processing to find multi-word skills
    for i in range(len(tokens) - 1):
        bigram = ' '.join(tokens[i:i+2])
        if bigram in SKILLS_DB:
            potential_skills.add(bigram)
    
    for i in range(len(tokens) - 2):
        trigram = ' '.join(tokens[i:i+3])
        if trigram in SKILLS_DB:
            potential_skills.add(trigram)
    
    # Filter and format results
    final_skills = []
    for skill in potential_skills:
        # Check if the skill is in our database or contains a skill from our database
        if any(db_skill in skill for db_skill in SKILLS_DB):
            # Find the most specific match
            best_match = max((db_skill for db_skill in SKILLS_DB if db_skill in skill), key=len, default=None)
            if best_match and best_match not in final_skills:
                final_skills.append(best_match)
    
    return sorted(final_skills)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            text = extract_text_from_file(filepath)
            skills = extract_skills(text)
            
            # Clean up - remove the uploaded file after processing
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'success': True,
                'skills': skills,
                'text': text[:500] + '...' if len(text) > 500 else text  # Return first 500 chars for preview
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)