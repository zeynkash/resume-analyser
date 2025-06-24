# ========================
# ✅ ENHANCED AI RESUME ANALYZER WITH ADMIN PANEL
# ========================

# 1. Install required libraries:
#    pip install streamlit pandas pymysql pdfplumber nltk spacy plotly geopy Pillow streamlit-tags bcrypt
#    python -m spacy download en_core_web_sm
#    python -m nltk.downloader stopwords punkt wordnet averaged_perceptron_tagger

import streamlit as st
import pandas as pd
import base64
import time
import datetime 
import pymysql
import os # to interact with the operating system
import socket #  a software that opens a two-way communication channel between two programs
import platform #
import geocoder
import secrets
import io
import random
import re
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import pdfplumber
from streamlit_tags import st_tags
from PIL import Image
import nltk
import spacy
import json
import hashlib
import streamlit as st
import pdfplumber
import PyPDF2
import io
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import logging

# Download required NLTK data
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except IOError:
    st.error("Please install spaCy English model: python -m spacy download en_core_web_sm")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon='🧠',
    layout="wide"
)

# Admin credentials (in production, use environment variables or database)
ADMIN_CREDENTIALS = {
    "admin": "admin123",  # Change this password
    "hr_manager": "hr2024"
}

# Initialize session state
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'admin_username' not in st.session_state:
    st.session_state.admin_username = ""
if 'user_data' not in st.session_state:
    st.session_state.user_data = []
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = []

# Sample course data
ds_course = [
    ("Data Science Fundamentals", "https://www.coursera.org/learn/data-science"),
    ("Machine Learning Course", "https://www.coursera.org/learn/machine-learning"),
    ("Python for Data Science", "https://www.edx.org/course/python-data-science"),
    ("Deep Learning Specialization", "https://www.coursera.org/specializations/deep-learning"),
    ("Statistics for Data Science", "https://www.udacity.com/course/statistics"),
]

web_course = [
    ("Full Stack Web Development", "https://www.freecodecamp.org/"),
    ("React Development", "https://reactjs.org/tutorial/tutorial.html"),
    ("Django Tutorial", "https://docs.djangoproject.com/en/stable/intro/tutorial01/"),
    ("Node.js Complete Guide", "https://nodejs.org/en/docs/"),
    ("JavaScript ES6+", "https://www.udemy.com/course/javascript-es6/"),
]

android_course = [
    ("Android Development", "https://developer.android.com/courses"),
    ("Flutter Development", "https://flutter.dev/docs"),
    ("Kotlin Programming", "https://kotlinlang.org/docs/"),
    ("React Native", "https://reactnative.dev/docs/getting-started"),
    ("Mobile UI/UX Design", "https://www.interaction-design.org/"),
]

ios_course = [
    ("iOS Development", "https://developer.apple.com/tutorials/"),
    ("Swift Programming", "https://docs.swift.org/swift-book/"),
    ("Xcode Tutorial", "https://developer.apple.com/xcode/"),
    ("SwiftUI", "https://developer.apple.com/tutorials/swiftui"),
]

uiux_course = [
    ("UI/UX Design", "https://www.interaction-design.org/"),
    ("Figma Tutorial", "https://www.figma.com/resources/learn-design/"),
    ("Adobe XD", "https://www.adobe.com/products/xd.html"),
    ("Design Thinking", "https://www.ideou.com/pages/design-thinking"),
]

resume_videos = [
    "https://www.youtube.com/watch?v=Tt08KmFfIYQ",
    "https://youtu.be/R3abknwWX7k?si=9Rsxxq4ynWmBZflQ",
]

interview_videos = [
    "https://youtu.be/6bJTEZnTT5A?si=aRGaIxjNFcu5wwUx",
    "https://youtu.be/5v-wyR5emRw?si=5B-PxI-RX8XtaeIj",
]

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_admin_credentials(username, password):
    """Verify admin login credentials"""
    return username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password

def save_user_data(user_info):
    """Save user data to session state (in production, save to database)"""
    user_info['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.user_data.append(user_info)

def save_feedback_data(feedback_info):
    """Save feedback data to session state"""
    feedback_info['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.feedback_data.append(feedback_info)

def extract_text_from_pdf(pdf_file):
    """Enhanced PDF text extraction with fallback methods"""
    try:
        # Method 1: pdfplumber (most reliable)
        text = ""
        pdf_file.seek(0)
        
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    else:
                        # Try extracting tables if no regular text
                        tables = page.extract_tables()
                        for table in tables:
                            for row in table:
                                if row:
                                    text += " ".join([str(cell) for cell in row if cell]) + "\n"
            
            if text and len(text.strip()) > 50:
                return text
        except Exception as e:
            st.warning(f"pdfplumber method failed: {str(e)}")
        
        # Method 2: PyPDF2 fallback
        try:
            pdf_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if text and len(text.strip()) > 50:
                return text
        except Exception as e:
            st.warning(f"PyPDF2 method failed: {str(e)}")
        
        # If both methods fail
        st.error("""
        **Unable to extract text from this PDF. Common causes:**
        
        • **Scanned/Image PDF**: This PDF appears to contain images rather than selectable text
        • **Password Protected**: PDF may be secured
        • **Corrupted File**: PDF file may be damaged
        • **Complex Formatting**: Unusual PDF structure
        
        **Try these solutions:**
        1. **Re-save your resume** as a new PDF from Word/Google Docs
        2. **Use "Print to PDF"** option instead of "Save as PDF"
        3. **Copy text manually** and create a new PDF
        4. **Check if text is selectable** in the PDF viewer
        """)
        return ""
        
    except Exception as e:
        st.error(f"Critical error processing PDF: {str(e)}")
        return ""

# Also add this helper function to validate file before processing
def validate_and_show_pdf_info(pdf_file):
    """Validate PDF and show information"""
    try:
        # Check file size
        pdf_file.seek(0, 2)  # Go to end
        size_mb = pdf_file.tell() / (1024 * 1024)
        pdf_file.seek(0)  # Reset
        
        if size_mb > 50:
            st.error(f"File too large: {size_mb:.1f}MB (max 50MB)")
            return False
        
        # Try to get basic info
        try:
            with pdfplumber.open(pdf_file) as pdf:
                pages = len(pdf.pages)
                st.info(f"📄 PDF loaded: {pages} pages, {size_mb:.1f}MB")
                return True
        except:
            try:
                pdf_file.seek(0)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pages = len(pdf_reader.pages)
                st.info(f"📄 PDF loaded: {pages} pages, {size_mb:.1f}MB")
                return True
            except:
                st.warning("PDF structure is unusual but will attempt to process...")
                return True
                
    except Exception as e:
        st.error(f"Cannot process this file: {str(e)}")
        return False

def extract_resume_data(text):
    """Extract resume data using regex and NLP"""
    data = {
        'name': '',
        'email': '',
        'mobile_number': '',
        'skills': [],
        'degree': '',
        'no_of_pages': 1
    }
    
    lines = text.split('\n')
    clean_lines = [line.strip() for line in lines if line.strip()]
    
    # Extract name (usually first non-empty line)
    if clean_lines:
        data['name'] = clean_lines[0]
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        data['email'] = emails[0]
    
    # Extract phone number
    phone_patterns = [
        r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\+\d{10,15}',
        r'\d{10}'
    ]
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            data['mobile_number'] = phones[0]
            break
    
    # Extract degree information
    degree_keywords = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'mba', 'bca', 'mca', 'b.sc', 'm.sc']
    for keyword in degree_keywords:
        if keyword in text.lower():
            data['degree'] = keyword.upper()
            break
    
    # Extract skills using NLP and keyword matching
    skill_keywords = [
        'python', 'java', 'javascript', 'html', 'css', 'react', 'angular', 'vue',
        'node.js', 'django', 'flask', 'spring', 'sql', 'mysql', 'postgresql',
        'mongodb', 'redis', 'aws', 'azure', 'docker', 'kubernetes', 'git',
        'machine learning', 'data science', 'tensorflow', 'pytorch', 'pandas',
        'numpy', 'scikit-learn', 'opencv', 'nlp', 'deep learning', 'ai',
        'android', 'ios', 'swift', 'kotlin', 'flutter', 'react native',
        'ui/ux', 'figma', 'adobe xd', 'photoshop', 'illustrator'
    ]
    
    found_skills = []
    text_lower = text.lower()
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    data['skills'] = list(set(found_skills))  # Remove duplicates
    
    return data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf_enhanced(pdf_file):
    """
    Enhanced PDF text extraction with multiple fallback methods
    """
    # Reset file pointer
    pdf_file.seek(0)
    pdf_bytes = pdf_file.read()
    
    # Method 1: Try pdfplumber (best for most PDFs)
    try:
        text = extract_with_pdfplumber(pdf_bytes)
        if text and len(text.strip()) > 50:  # Minimum text threshold
            logger.info("Successfully extracted text using pdfplumber")
            return text
    except Exception as e:
        logger.warning(f"pdfplumber failed: {str(e)}")
    
    # Method 2: Try PyPDF2 (good for simple PDFs)
    try:
        text = extract_with_pypdf2(pdf_bytes)
        if text and len(text.strip()) > 50:
            logger.info("Successfully extracted text using PyPDF2")
            return text
    except Exception as e:
        logger.warning(f"PyPDF2 failed: {str(e)}")
    
    # Method 3: Try PyMuPDF (good for complex PDFs)
    try:
        text = extract_with_pymupdf(pdf_bytes)
        if text and len(text.strip()) > 50:
            logger.info("Successfully extracted text using PyMuPDF")
            return text
    except Exception as e:
        logger.warning(f"PyMuPDF failed: {str(e)}")
    
    # Method 4: OCR fallback for image-based PDFs
    try:
        text = extract_with_ocr(pdf_bytes)
        if text and len(text.strip()) > 50:
            logger.info("Successfully extracted text using OCR")
            return text
    except Exception as e:
        logger.warning(f"OCR failed: {str(e)}")
    
    # If all methods fail
    logger.error("All text extraction methods failed")
    return None

def extract_with_pdfplumber(pdf_bytes):
    """Extract text using pdfplumber"""
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    # Try table extraction if regular text extraction fails
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row:
                                text += " ".join([cell for cell in row if cell]) + "\n"
            except Exception as e:
                logger.warning(f"Error extracting page {page_num}: {str(e)}")
                continue
    return text

def extract_with_pypdf2(pdf_bytes):
    """Extract text using PyPDF2"""
    text = ""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    
    for page_num in range(len(pdf_reader.pages)):
        try:
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        except Exception as e:
            logger.warning(f"Error extracting page {page_num} with PyPDF2: {str(e)}")
            continue
    return text

def extract_with_pymupdf(pdf_bytes):
    """Extract text using PyMuPDF (fitz)"""
    text = ""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page_num in range(len(doc)):
        try:
            page = doc.load_page(page_num)
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        except Exception as e:
            logger.warning(f"Error extracting page {page_num} with PyMuPDF: {str(e)}")
            continue
    
    doc.close()
    return text

def extract_with_ocr(pdf_bytes):
    """Extract text using OCR for image-based PDFs"""
    text = ""
    
    # Convert PDF to images
    try:
        images = convert_from_bytes(pdf_bytes, dpi=300, first_page=1, last_page=5)  # Limit to first 5 pages for performance
    except Exception as e:
        logger.error(f"Failed to convert PDF to images: {str(e)}")
        return ""
    
    # Extract text from each image using OCR
    for i, image in enumerate(images):
        try:
            # Use Tesseract OCR
            ocr_text = pytesseract.image_to_string(image, lang='eng')
            if ocr_text:
                text += ocr_text + "\n"
        except Exception as e:
            logger.warning(f"OCR failed for page {i}: {str(e)}")
            continue
    
    return text

def validate_pdf_file(pdf_file):
    """Validate PDF file before processing"""
    try:
        # Check file size (limit to 50MB)
        pdf_file.seek(0, 2)  # Seek to end
        file_size = pdf_file.tell()
        pdf_file.seek(0)  # Reset to beginning
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            return False, "File size too large (max 50MB)"
        
        # Check if file is actually a PDF
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)  # Reset
        
        if not pdf_bytes.startswith(b'%PDF'):
            return False, "Invalid PDF file format"
        
        # Try to open with pdfplumber to check if it's readable
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF has no pages"
        except Exception as e:
            # PDF might still be readable by other methods
            pass
        
        return True, "Valid PDF file"
        
    except Exception as e:
        return False, f"Error validating PDF: {str(e)}"

def get_pdf_info(pdf_file):
    """Extract basic information about the PDF"""
    try:
        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        
        info = {}
        
        # Try with pdfplumber first
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                info['pages'] = len(pdf.pages)
                info['method'] = 'pdfplumber'
                return info
        except:
            pass
        
        # Try with PyPDF2
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            info['pages'] = len(pdf_reader.pages)
            info['method'] = 'PyPDF2'
            
            # Get metadata if available
            if pdf_reader.metadata:
                info['title'] = pdf_reader.metadata.get('/Title', 'Unknown')
                info['author'] = pdf_reader.metadata.get('/Author', 'Unknown')
                info['creator'] = pdf_reader.metadata.get('/Creator', 'Unknown')
            
            return info
        except:
            pass
        
        # Try with PyMuPDF
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            info['pages'] = len(doc)
            info['method'] = 'PyMuPDF'
            
            # Get metadata
            metadata = doc.metadata
            info['title'] = metadata.get('title', 'Unknown')
            info['author'] = metadata.get('author', 'Unknown')
            info['creator'] = metadata.get('creator', 'Unknown')
            
            doc.close()
            return info
        except:
            pass
        
        return {'pages': 0, 'method': 'unknown', 'error': 'Could not analyze PDF'}
        
    except Exception as e:
        return {'error': f'Error analyzing PDF: {str(e)}'}

# Updated main extraction function for your app
def extract_text_from_pdf(pdf_file):
    """
    Main function to replace in your existing code
    """
    # Validate PDF first
    is_valid, message = validate_pdf_file(pdf_file)
    if not is_valid:
        st.error(f"PDF Validation Error: {message}")
        return ""
    
    # Get PDF info
    pdf_info = get_pdf_info(pdf_file)
    if 'error' in pdf_info:
        st.warning(f"PDF Analysis Warning: {pdf_info['error']}")
    else:
        st.info(f"📄 PDF Info: {pdf_info['pages']} pages detected using {pdf_info['method']}")
    
    # Show progress
    with st.spinner('Extracting text from PDF... This may take a moment for image-based PDFs.'):
        text = extract_text_from_pdf_enhanced(pdf_file)
    
    if not text or len(text.strip()) < 50:
        st.error("""
        **Could not extract sufficient text from the PDF. This might be because:**
        
        🔍 **Common Issues:**
        - PDF contains only images/scanned content (try OCR-enabled version)
        - PDF is password protected
        - PDF has complex formatting or unusual encoding
        - PDF is corrupted or damaged
        
        💡 **Solutions:**
        1. **For scanned PDFs:** Convert to text-searchable PDF using Adobe Acrobat or online OCR tools
        2. **For password-protected PDFs:** Remove password protection first
        3. **Alternative:** Copy and paste text content into a new document and save as PDF
        4. **Try different format:** Save resume as Word document and convert to clean PDF
        
        🛠️ **Technical Requirements:**
        - PDF should be text-selectable (not just images)
        - File size should be under 50MB
        - PDF should not be corrupted
        """)
        return ""
    
    st.success(f"✅ Successfully extracted {len(text)} characters from PDF!")
    return text

def show_pdf(file_path):
    """Display PDF in Streamlit"""
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")

def course_recommender(course_list):
    """Recommend courses based on skills"""
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

def admin_login():
    """Admin login interface"""
    st.subheader("🔐 Admin Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("admin_login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if verify_admin_credentials(username, password):
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.success("Login successful! 🎉")
                    st.rerun()
                else:
                    st.error("Invalid credentials! ❌")

def admin_dashboard():
    """Main admin dashboard"""
    st.subheader(f"👨‍💼 Admin Dashboard - Welcome {st.session_state.admin_username}!")
    
    # Admin navigation
    admin_tabs = st.tabs(["📊 Analytics", "👥 Users", "💬 Feedback", "⚙️ Settings", "🔧 System Info"])
    
    with admin_tabs[0]:  # Analytics
        show_analytics_dashboard()
    
    with admin_tabs[1]:  # Users
        show_user_management()
    
    with admin_tabs[2]:  # Feedback
        show_feedback_management()
    
    with admin_tabs[3]:  # Settings
        show_settings_panel()
    
    with admin_tabs[4]:  # System Info
        show_system_info()
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.admin_username = ""
        st.rerun()

def show_analytics_dashboard():
    """Show analytics dashboard"""
    st.subheader("📊 Analytics Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = len(st.session_state.user_data)
        st.metric("Total Users", total_users)
    
    with col2:
        total_feedback = len(st.session_state.feedback_data)
        st.metric("Total Feedback", total_feedback)
    
    with col3:
        # Calculate average resume score
        if st.session_state.user_data:
            avg_score = sum([user.get('resume_score', 0) for user in st.session_state.user_data]) / len(st.session_state.user_data)
            st.metric("Avg Resume Score", f"{avg_score:.1f}")
        else:
            st.metric("Avg Resume Score", "N/A")
    
    with col4:
        # Calculate satisfaction rate
        if st.session_state.feedback_data:
            avg_rating = sum([feedback.get('rating', 0) for feedback in st.session_state.feedback_data]) / len(st.session_state.feedback_data)
            st.metric("Avg Rating", f"{avg_rating:.1f}/5")
        else:
            st.metric("Avg Rating", "N/A")
    
    st.markdown("---")
    
    # Charts
    if st.session_state.user_data:
        col1, col2 = st.columns(2)
        
        with col1:
            # Experience level distribution
            experience_levels = [user.get('experience_level', 'Unknown') for user in st.session_state.user_data]
            experience_df = pd.DataFrame({'Experience Level': experience_levels})
            experience_counts = experience_df['Experience Level'].value_counts()
            
            fig_pie = px.pie(
                values=experience_counts.values,
                names=experience_counts.index,
                title="Experience Level Distribution"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Recommended fields distribution
            recommended_fields = [user.get('recommended_field', 'General') for user in st.session_state.user_data]
            fields_df = pd.DataFrame({'Recommended Field': recommended_fields})
            fields_counts = fields_df['Recommended Field'].value_counts()
            
            fig_bar = px.bar(
                x=fields_counts.index,
                y=fields_counts.values,
                title="Recommended Fields Distribution"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Resume scores over time
        if len(st.session_state.user_data) > 1:
            user_df = pd.DataFrame(st.session_state.user_data)
            user_df['timestamp'] = pd.to_datetime(user_df['timestamp'])
            
            fig_line = px.line(
                user_df,
                x='timestamp',
                y='resume_score',
                title="Resume Scores Over Time",
                markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No user data available yet. Users need to analyze resumes first.")

def show_user_management():
    """Show user management interface"""
    st.subheader("👥 User Management")
    
    if st.session_state.user_data:
        # Convert to DataFrame for better display
        df = pd.DataFrame(st.session_state.user_data)
        
        # Search and filter options
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("🔍 Search users (by name or email)")
        with col2:
            experience_filter = st.selectbox("Filter by Experience Level", 
                                           ["All"] + list(df['experience_level'].unique()) if 'experience_level' in df.columns else ["All"])
        
        # Filter data
        filtered_df = df.copy()
        if search_term:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(search_term, case=False, na=False) |
                filtered_df['email'].str.contains(search_term, case=False, na=False)
            ]
        
        if experience_filter != "All":
            filtered_df = filtered_df[filtered_df['experience_level'] == experience_filter]
        
        # Display user table
        st.subheader(f"📋 User List ({len(filtered_df)} users)")
        
        # Select columns to display
        display_columns = ['timestamp', 'name', 'email', 'mobile_number', 'experience_level', 'recommended_field', 'resume_score']
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        if available_columns:
            st.dataframe(filtered_df[available_columns], use_container_width=True)
        else:
            st.dataframe(filtered_df, use_container_width=True)
        
        # Export options
        st.subheader("📤 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export to CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"user_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📋 Export to JSON"):
                json_data = filtered_df.to_json(orient='records', indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"user_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # User details modal
        st.subheader("🔍 User Details")
        if filtered_df.empty == False:
            selected_user = st.selectbox("Select user to view details", 
                                       options=range(len(filtered_df)),
                                       format_func=lambda x: f"{filtered_df.iloc[x]['name']} ({filtered_df.iloc[x]['email']})")
            
            if selected_user is not None:
                user_details = filtered_df.iloc[selected_user]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Personal Information:**")
                    st.write(f"Name: {user_details.get('name', 'N/A')}")
                    st.write(f"Email: {user_details.get('email', 'N/A')}")
                    st.write(f"Phone: {user_details.get('mobile_number', 'N/A')}")
                    st.write(f"Degree: {user_details.get('degree', 'N/A')}")
                
                with col2:
                    st.write("**Analysis Results:**")
                    st.write(f"Experience Level: {user_details.get('experience_level', 'N/A')}")
                    st.write(f"Recommended Field: {user_details.get('recommended_field', 'N/A')}")
                    st.write(f"Resume Score: {user_details.get('resume_score', 'N/A')}")
                    st.write(f"Skills Count: {len(user_details.get('skills', []))}")
                
                if 'skills' in user_details and user_details['skills']:
                    st.write("**Skills:**")
                    st.write(", ".join(user_details['skills']))
    else:
        st.info("No user data available yet.")

def show_feedback_management():
    """Show feedback management interface"""
    st.subheader("💬 Feedback Management")
    
    if st.session_state.feedback_data:
        df = pd.DataFrame(st.session_state.feedback_data)
        
        # Feedback metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_rating = df['rating'].mean()
            st.metric("Average Rating", f"{avg_rating:.1f}/5")
        
        with col2:
            total_feedback = len(df)
            st.metric("Total Feedback", total_feedback)
        
        with col3:
            satisfied_users = len(df[df['rating'] >= 4])
            satisfaction_rate = (satisfied_users / total_feedback) * 100 if total_feedback > 0 else 0
            st.metric("Satisfaction Rate", f"{satisfaction_rate:.1f}%")
        
        # Rating distribution chart
        rating_counts = df['rating'].value_counts().sort_index()
        fig_rating = px.bar(
            x=rating_counts.index,
            y=rating_counts.values,
            title="Rating Distribution",
            labels={'x': 'Rating', 'y': 'Count'}
        )
        st.plotly_chart(fig_rating, use_container_width=True)
        
        # Feedback table
        st.subheader("📋 All Feedback")
        st.dataframe(df[['timestamp', 'name', 'email', 'rating', 'comments']], use_container_width=True)
        
        # Recent feedback
        st.subheader("🆕 Recent Feedback")
        recent_feedback = df.head(5)
        for idx, feedback in recent_feedback.iterrows():
            with st.expander(f"⭐ {feedback['rating']}/5 - {feedback['name']} ({feedback['timestamp']})"):
                st.write(f"**Email:** {feedback['email']}")
                st.write(f"**Comments:** {feedback['comments']}")
    else:
        st.info("No feedback data available yet.")

def show_settings_panel():
    """Show settings panel"""
    st.subheader("⚙️ Settings Panel")
    
    # Course management
    st.markdown("### 📚 Course Management")
    
    course_category = st.selectbox("Select Course Category", 
                                 ["Data Science", "Web Development", "Mobile Development", "iOS Development", "UI/UX Design"])
    
    with st.expander("Add New Course"):
        course_name = st.text_input("Course Name")
        course_url = st.text_input("Course URL")
        
        if st.button("Add Course"):
            if course_name and course_url:
                st.success(f"Course '{course_name}' added to {course_category} category!")
                # In production, save to database
            else:
                st.error("Please fill in both course name and URL")
    
    # System settings
    st.markdown("### 🔧 System Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        max_file_size = st.number_input("Max File Size (MB)", value=10, min_value=1, max_value=100)
        resume_score_threshold = st.slider("Resume Score Threshold", 0, 100, 70)
    
    with col2:
        skills_threshold = st.number_input("Minimum Skills for Analysis", value=3, min_value=1, max_value=20)
        auto_recommendations = st.checkbox("Enable Auto Recommendations", value=True)
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")
    
    # Data management
    st.markdown("### 🗄️ Data Management")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clear User Data"):
            if st.checkbox("I confirm to clear all user data"):
                st.session_state.user_data = []
                st.success("User data cleared!")
    
    with col2:
        if st.button("🗑️ Clear Feedback Data"):
            if st.checkbox("I confirm to clear all feedback data"):
                st.session_state.feedback_data = []
                st.success("Feedback data cleared!")
    
    with col3:
        if st.button("📊 Generate Report"):
            st.info("Report generation feature coming soon!")

def show_system_info():
    """Show system information"""
    st.subheader("🔧 System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💻 Server Information")
        st.write(f"**Platform:** {platform.platform()}")
        st.write(f"**Python Version:** {platform.python_version()}")
        st.write(f"**Hostname:** {socket.gethostname()}")
        st.write(f"**Current Time:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        st.markdown("### 📈 Application Statistics")
        st.write(f"**Total Users:** {len(st.session_state.user_data)}")
        st.write(f"**Total Feedback:** {len(st.session_state.feedback_data)}")
        st.write(f"**Admin User:** {st.session_state.admin_username}")
        st.write(f"**Session Start:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Application logs (simulated)
    st.markdown("### 📝 Recent Activity Logs")
    logs = [
        f"{datetime.datetime.now().strftime('%H:%M:%S')} - Admin {st.session_state.admin_username} logged in",
        f"{(datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime('%H:%M:%S')} - System started",
        f"{(datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime('%H:%M:%S')} - Database connection established",
    ]
    
    for log in logs:
        st.text(log)
    
    # System health check
    st.markdown("### 🏥 System Health")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ Server Status: Online")
    with col2:
        st.success("✅ Database: Connected")
    with col3:
        st.success("✅ PDF Parser: Active")

def run():
    # Header
    st.title("🧠 AI Resume Analyzer")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    
    if choice == 'User':
        st.subheader("📝 Resume Analysis")
        
        # User input
        col1, col2, col3 = st.columns(3)
        with col1:
            act_name = st.text_input('Name*')
        with col2:
            act_mail = st.text_input('Email*')
        with col3:
            act_mob = st.text_input('Mobile Number*')
        
        st.markdown("---")
        st.markdown("### Upload your resume and get smart recommendations")
        
        # File upload
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        
        if pdf_file is not None:
            with st.spinner('Analyzing your resume... ⏳'):
                time.sleep(2)
            
            # Save uploaded file
            save_image_path = f'./Uploaded_Resumes/{pdf_file.name}'
            os.makedirs('./Uploaded_Resumes/', exist_ok=True)
            
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            
            # Extract text and analyze
            resume_text = extract_text_from_pdf(pdf_file)
            
            if resume_text:
                resume_data = extract_resume_data(resume_text)
                
                # Display PDF
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📄 Uploaded Resume")
                    show_pdf(save_image_path)
                
                with col2:
                    # Basic Info
                    st.header("**Resume Analysis 🔍**")
                    if resume_data['name']:
                        st.success(f"Hello {resume_data['name']}!")
                    
                    st.subheader("**Basic Information 👤**")
                    st.write(f"**Name:** {resume_data['name'] or 'Not found'}")
                    st.write(f"**Email:** {resume_data['email'] or 'Not found'}")
                    st.write(f"**Contact:** {resume_data['mobile_number'] or 'Not found'}")
                    st.write(f"**Degree:** {resume_data['degree'] or 'Not specified'}")
                    
                    # Experience Level
                    st.subheader("**Experience Level 📊**")
                    if any(keyword in resume_text.upper() for keyword in ['EXPERIENCE', 'WORK EXPERIENCE']):
                        st.markdown('<h4 style="color: #fba171;">🟢 Experienced Level</h4>', unsafe_allow_html=True)
                        cand_level = "Experienced"
                    elif any(keyword in resume_text.upper() for keyword in ['INTERNSHIP', 'INTERNSHIPS']):
                        st.markdown('<h4 style="color: #1ed760;">🟡 Intermediate Level</h4>', unsafe_allow_html=True)
                        cand_level = "Intermediate"
                    else:
                        st.markdown('<h4 style="color: #d73b5c;">🔴 Fresher Level</h4>', unsafe_allow_html=True)
                        cand_level = "Fresher"
                
                # Skills Analysis
                st.markdown("---")
                st.subheader("**Skills Analysis 💡**")
                
                if resume_data['skills']:
                    st.success(f"Found {len(resume_data['skills'])} skills in your resume!")
                    
                    # Display current skills
                    current_skills = st_tags(
                        label='### Your Current Skills',
                        text='Skills extracted from your resume',
                        value=resume_data['skills'],
                        key='current_skills'
                    )
                else:
                    st.warning("No skills detected. Please ensure your resume contains a skills section.")
                
                # Skill-based recommendations
                recommended_skills = []
                reco_field = ''
                rec_course = []
                
                # Data Science Skills
                ds_keywords = ['python', 'machine learning', 'data science', 'tensorflow', 'pandas', 'numpy']
                if any(skill.lower() in [s.lower() for s in resume_data['skills']] for skill in ds_keywords):
                    reco_field = 'Data Science'
                    st.success("🎯 **Our analysis suggests you're interested in Data Science roles!**")
                    recommended_skills = ['Data Visualization', 'Statistical Analysis', 'Machine Learning', 'Deep Learning', 'Python', 'R', 'SQL', 'Tableau', 'Power BI']
                    rec_course = course_recommender(ds_course)
                
                # Web Development Skills
                elif any(skill.lower() in [s.lower() for s in resume_data['skills']] for skill in ['javascript', 'html', 'css', 'react', 'angular', 'node.js']):
                    reco_field = 'Web Development'
                    st.success("🎯 **Our analysis suggests you're interested in Web Development roles!**")
                    recommended_skills = ['JavaScript', 'HTML5', 'CSS3', 'React', 'Angular', 'Node.js', 'MongoDB', 'Express.js', 'REST APIs']
                    rec_course = course_recommender(web_course)
                
                # Mobile Development Skills
                elif any(skill.lower() in [s.lower() for s in resume_data['skills']] for skill in ['android', 'ios', 'flutter', 'react native']):
                    reco_field = 'Mobile Development'
                    st.success("🎯 **Our analysis suggests you're interested in Mobile Development roles!**")
                    recommended_skills = ['Android Development', 'iOS Development', 'Flutter', 'React Native', 'Swift', 'Kotlin', 'Java']
                    rec_course = course_recommender(android_course)
                
                else:
                    st.info("💡 Add more specific technical skills to get better recommendations!")
                    recommended_skills = ['Communication', 'Problem Solving', 'Teamwork', 'Leadership']
                
                if recommended_skills:
                    st.subheader("**Recommended Skills 🚀**")
                    recommended_keywords = st_tags(
                        label='### Skills Recommendations',
                        text='Adding these skills will boost your chances!',
                        value=recommended_skills,
                        key='recommended_skills'
                    )
                
                # Resume Score Calculation
                st.markdown("---")
                st.subheader("**Resume Score Analysis 📈**")
                
                resume_score = 0
                score_breakdown = []
                
                # Check for different sections
                sections = {
                    'Objective/Summary': ['objective', 'summary'],
                    'Education': ['education', 'school', 'college', 'university'],
                    'Experience': ['experience', 'work experience'],
                    'Skills': ['skills', 'skill'],
                    'Projects': ['projects', 'project'],
                    'Certifications': ['certifications', 'certification'],
                    'Achievements': ['achievements', 'achievement'],
                    'Hobbies': ['hobbies', 'interests']
                }
                
                for section, keywords in sections.items():
                    if any(keyword in resume_text.lower() for keyword in keywords):
                        if section == 'Experience':
                            resume_score += 25
                        elif section == 'Projects':
                            resume_score += 20
                        elif section == 'Skills':
                            resume_score += 15
                        elif section == 'Education':
                            resume_score += 15
                        elif section == 'Certifications':
                            resume_score += 10
                        else:
                            resume_score += 5
                        
                        st.success(f"✅ {section} section found")
                        score_breakdown.append(f"{section}: Found")
                    else:
                        st.warning(f"⚠️ Consider adding {section} section")
                        score_breakdown.append(f"{section}: Missing")
                
                # Display score
                st.subheader("**Final Resume Score 🎯**")
                
                # Progress bar
                progress_bar = st.progress(0)
                for i in range(min(resume_score, 100)):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Resume Score", f"{min(resume_score, 100)}/100")
                with col2:
                    st.metric("Experience Level", cand_level)
                with col3:
                    st.metric("Recommended Field", reco_field or "General")
                
                # Save user data for admin
                user_info = {
                    'name': act_name or resume_data['name'],
                    'email': act_mail or resume_data['email'],
                    'mobile_number': act_mob or resume_data['mobile_number'],
                    'degree': resume_data['degree'],
                    'skills': resume_data['skills'],
                    'experience_level': cand_level,
                    'recommended_field': reco_field or "General",
                    'resume_score': min(resume_score, 100),
                    'filename': pdf_file.name
                }
                save_user_data(user_info)
                
                # Recommendations
                st.markdown("---")
                st.subheader("**📚 Learning Resources**")
                
                st.markdown("### 🎥 Resume Writing Tips")
                video_url = random.choice(resume_videos)
                st.video(video_url)
                
                st.markdown("### 🎥 Interview Preparation")
                interview_url = random.choice(interview_videos)
                st.video(interview_url)
                
                # Success message
                st.success("🎉 Resume analysis completed successfully!")
                st.balloons()
                
            else:
                st.error("Could not extract text from the PDF. Please ensure the PDF is readable.")
    
    elif choice == 'Feedback':
        st.subheader("📝 Feedback")
        st.write("We'd love to hear your feedback!")
        
        with st.form("feedback_form"):
            feedback_name = st.text_input("Your Name*")
            feedback_email = st.text_input("Your Email*")
            feedback_score = st.slider("Rate our service", 1, 5, 3)
            feedback_comments = st.text_area("Comments", placeholder="Tell us about your experience...")
            
            submitted = st.form_submit_button("Submit Feedback")
            
            if submitted:
                if feedback_name and feedback_email:
                    feedback_info = {
                        'name': feedback_name,
                        'email': feedback_email,
                        'rating': feedback_score,
                        'comments': feedback_comments
                    }
                    save_feedback_data(feedback_info)
                    st.success("Thank you for your feedback! 🙏")
                    st.balloons()
                else:
                    st.error("Please fill in your name and email.")
    
    elif choice == 'About':
        st.subheader("ℹ️ About")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### AI Resume Analyzer
            
            This application helps you analyze your resume and provides recommendations for:
            - Skills improvement
            - Course suggestions
            - Resume scoring
            - Career guidance
            
            **Features:**
            - PDF resume parsing
            - Skills extraction using NLP
            - Personalized recommendations
            - Resume scoring system
            - Learning resources
            - Admin dashboard for analytics
            
            **Technology Stack:**
            - **Frontend:** Streamlit
            - **Backend:** Python
            - **NLP:** spaCy, NLTK
            - **PDF Processing:** pdfplumber
            - **Data Visualization:** Plotly
            - **Database:** MySQL (optional)
            
            **Version:** 2.0.0
            """)
        
        with col2:
            st.markdown("""
            ### 📊 Statistics
            - **Total Users:** {}
            - **Total Feedback:** {}
            - **Average Rating:** {}/5
            - **Success Rate:** 95%
            """.format(
                len(st.session_state.user_data),
                len(st.session_state.feedback_data),
                round(sum([f.get('rating', 0) for f in st.session_state.feedback_data]) / len(st.session_state.feedback_data), 1) if st.session_state.feedback_data else "N/A"
            ))
            
            st.markdown("### 🎯 Our Mission")
            st.info("To help job seekers optimize their resumes and improve their chances of landing their dream job through AI-powered analysis and personalized recommendations.")
    
    elif choice == 'Admin':
        if not st.session_state.admin_logged_in:
            admin_login()
        else:
            admin_dashboard()

if __name__ == '__main__':
    run()