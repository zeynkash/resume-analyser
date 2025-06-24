# resume-analyser
An intelligent resume analysis tool that extracts key information from resumes, provides personalized recommendations, and features a comprehensive admin dashboard for analytics and management

✨ Features
Resume Analysis: Extract contact info, skills, and experience level

Personalized Recommendations: Get skill suggestions and course links

Resume Scoring: Get instant resume quality score (0-100)

Career Guidance: Field-specific recommendations

Admin Dashboard: User analytics, feedback management, and system monitoring

PDF Handling: Advanced text extraction from PDFs (including OCR)

🚀 Quick Start Guide
Prerequisites
Python 3.7+

Tesseract OCR installed (Installation Guide)

⚙️ Installation:
# Clone the repository
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Download NLP resources
python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords punkt wordnet averaged_perceptron_tagger


🔑 Admin Credentials
Username	Password
admin	admin123
hr_manager	hr2024

🏃 Running the Application
streamlit run App.py


🧭 User Guide
1. Upload Resume
Go to User section in sidebar

Fill basic information (name, email, phone)

Upload PDF resume

View analysis results within seconds

2. Get Recommendations
See missing skills to improve

Get personalized course links

Watch resume/interview preparation videos

3. Provide Feedback
Rate your experience (1-5 stars)

Share comments for improvement

👨‍💼 Admin Guide
Login with admin credentials

Access dashboard tabs:

📊 Analytics: User metrics and trends

👥 Users: View/export user data

💬 Feedback: Manage user feedback

⚙️ Settings: Configure system parameters

🔧 System: Monitor server health

🛠️ Technical Stack
Framework: Streamlit

NLP: spaCy, NLTK

PDF Processing: pdfplumber, PyMuPDF, PyPDF2

OCR: Tesseract, pdf2image

Data Visualization: Plotly

Database: Session state (in-memory)

⚠️ Troubleshooting
Problem: PDF text extraction fails
Solution:

Ensure Tesseract is installed and in PATH

Verify PDF is text-selectable (not image-only)

Try smaller PDF files (<50MB)

Problem: Missing NLP resources
Solution:
python -m spacy download en_core_web_sm
python -m nltk.downloader all

📈 Roadmap
Add database integration (MySQL/PostgreSQL)

Implement user authentication

Add multi-language support

Include job market trends

Develop Chrome extension version

Note: For production use, change the default admin credentials in the code and implement proper database storage instead of session state.



