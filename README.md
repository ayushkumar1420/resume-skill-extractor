<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Skill Extractor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px 0;
            background-color: #2c3e50;
            color: white;
            border-radius: 5px;
        }
        h1 {
            margin: 0;
            font-size: 2.2em;
        }
        .upload-area {
            background-color: white;
            padding: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            text-align: center;
        }
        .file-input {
            display: none;
        }
        .upload-btn {
            display: inline-block;
            padding: 12px 24px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .upload-btn:hover {
            background-color: #2980b9;
        }
        .file-name {
            margin-top: 10px;
            font-size: 14px;
            color: #666;
        }
        .results {
            display: none;
            background-color: white;
            padding: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .skills-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 20px;
        }
        .skill-tag {
            background-color: #e1f5fe;
            color: #0288d1;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
        }
        .text-preview {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top: 4px solid #3498db;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            color: #e74c3c;
            margin-top: 10px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Resume Skill Extractor</h1>
            <p>Upload your resume and we'll extract the relevant skills</p>
        </header>

        <div class="upload-area">
            <h2>Upload Your Resume</h2>
            <p>Supported formats: PDF, DOCX, TXT</p>
            
            <input type="file" id="resume-upload" class="file-input" accept=".pdf,.docx,.txt">
            <label for="resume-upload" class="upload-btn">Choose File</label>
            
            <div class="file-name" id="file-name">No file chosen</div>
            <div class="error" id="error-message"></div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Processing your resume...</p>
            </div>
        </div>

        <div class="results" id="results">
            <h2>Extracted Skills</h2>
            <div class="skills-container" id="skills-container">
                <!-- Skills will be added here dynamically -->
            </div>
            
            <h3>Text Preview</h3>
            <div class="text-preview" id="text-preview"></div>
        </div>
    </div>

    <script>
        document.getElementById('resume-upload').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('file-name').textContent = file.name;
                document.getElementById('error-message').style.display = 'none';
                
                // Show loading spinner
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';
                
                uploadFile(file);
            }
        });

        function uploadFile(file) {
            const formData = new FormData();
            formData.append('resume', file);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    document.getElementById('error-message').textContent = data.error;
                    document.getElementById('error-message').style.display = 'block';
                    return;
                }
                
                // Display results
                const skillsContainer = document.getElementById('skills-container');
                skillsContainer.innerHTML = '';
                
                if (data.skills && data.skills.length > 0) {
                    data.skills.forEach(skill => {
                        const skillTag = document.createElement('div');
                        skillTag.className = 'skill-tag';
                        skillTag.textContent = skill;
                        skillsContainer.appendChild(skillTag);
                    });
                } else {
                    skillsContainer.innerHTML = '<p>No skills detected in the resume.</p>';
                }
                
                // Display text preview
                document.getElementById('text-preview').textContent = data.text || 'No text extracted.';
                
                // Show results section
                document.getElementById('results').style.display = 'block';
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error-message').textContent = 'An error occurred: ' + error.message;
                document.getElementById('error-message').style.display = 'block';
                console.error('Error:', error);
            });
        }
    </script>
</body>
</html>
