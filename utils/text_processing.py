import re
import PyPDF2
import pdfplumber
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import io
import tempfile
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Enhanced skill keywords database
SKILL_KEYWORDS = [
    # Programming Languages
    'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
    'typescript', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell',
    
    # Web Frontend
    'react', 'angular', 'vue', 'vue.js', 'node.js', 'django', 'flask', 'spring', 'express',
    'html', 'html5', 'css', 'css3', 'bootstrap', 'tailwind', 'sass', 'less', 'webpack',
    'jquery', 'next.js', 'nuxt.js', 'svelte', 'redux', 'mobx',
    
    # Web Backend
    'spring boot', 'laravel', 'asp.net', 'ruby on rails', 'fastapi', 'nestjs',
    
    # Databases
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'nosql', 'cassandra',
    'dynamodb', 'mariadb', 'sqlite', 'elasticsearch', 'neo4j', 'couchdb',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'devops',
    'gitlab', 'github actions', 'circleci', 'travis ci', 'terraform', 'ansible', 'puppet', 'chef',
    
    # Data Science & AI
    'machine learning', 'deep learning', 'ai', 'artificial intelligence', 'tensorflow', 'pytorch', 
    'scikit-learn', 'keras', 'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly',
    'data analysis', 'data science', 'statistics', 'nlp', 'computer vision', 'opencv',
    
    # Mobile Development
    'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
    
    # Tools & Methodologies
    'git', 'github', 'gitlab', 'bitbucket', 'version control', 'svn',
    'agile', 'scrum', 'kanban', 'jira', 'confluence', 'trello',
    'rest api', 'graphql', 'soap', 'microservices', 'api development',
    'linux', 'unix', 'ubuntu', 'centos', 'windows server',
    
    # Data & Analytics
    'excel', 'power bi', 'tableau', 'data visualization', 'looker', 'qlik',
    'spark', 'hadoop', 'kafka', 'airflow', 'etl', 'data warehouse',
    
    # Security
    'cybersecurity', 'network security', 'penetration testing', 'ethical hacking',
    'security', 'firewall', 'encryption', 'ssl', 'tls',
    
    # Design
    'ui/ux', 'figma', 'adobe xd', 'sketch', 'photoshop', 'illustrator', 'indesign',
    
    # Marketing
    'seo', 'digital marketing', 'google analytics', 'social media marketing',
    'content marketing', 'email marketing', 'google ads', 'facebook ads',
    
    # Soft Skills
    'leadership', 'communication', 'teamwork', 'problem solving', 'project management',
    'critical thinking', 'analytical', 'presentation', 'time management'
]

def extract_pdf_text(file_obj):
    """
    Extract text from PDF file with comprehensive error handling and OCR fallback
    
    Args:
        file_obj: Either a file path string or a file-like object
        
    Returns:
        str: Extracted text from the PDF
        
    Raises:
        ValueError: If text extraction fails with all methods
    """
    text = ""
    extraction_method = None
    
    # Method 1: PyPDF2 (fastest)
    try:
        if isinstance(file_obj, str):
            with open(file_obj, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        else:
            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_obj)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text and len(text.strip()) >= 50:
            extraction_method = "PyPDF2"
            return text.strip()
    except Exception as e:
        print(f"PyPDF2 extraction failed: {str(e)}")
    
    # Method 2: pdfplumber (better for complex PDFs)
    try:
        if isinstance(file_obj, str):
            with pdfplumber.open(file_obj) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        else:
            file_obj.seek(0)
            with pdfplumber.open(file_obj) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        
        if text and len(text.strip()) >= 50:
            extraction_method = "pdfplumber"
            return text.strip()
    except Exception as e:
        print(f"pdfplumber extraction failed: {str(e)}")
    
    # Method 3: OCR fallback (for scanned/image PDFs)
    try:
        images = None
        
        if isinstance(file_obj, str):
            images = convert_from_path(file_obj, dpi=300)
        else:
            file_obj.seek(0)
            pdf_bytes = file_obj.read()
            images = convert_from_bytes(pdf_bytes, dpi=300)
        
        if images:
            text = ""
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image, lang='eng')
                if page_text:
                    text += page_text + "\n"
            
            if text and len(text.strip()) >= 50:
                extraction_method = "OCR (pytesseract)"
                return text.strip()
    except Exception as e:
        print(f"OCR extraction failed: {str(e)}")
    
    # If all methods failed
    if not text or len(text.strip()) < 50:
        raise ValueError(
            "Failed to extract sufficient text from PDF using all available methods "
            "(PyPDF2, pdfplumber, OCR). The file may be corrupted, empty, or in an unsupported format."
        )
    
    return text.strip()

def process_text(text):
    """Process text for NLP analysis with improved cleaning"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text)
    
    # Remove email addresses (but preserve them for extraction)
    text = re.sub(r'\S+@\S+', ' ', text)
    
    # Remove special characters but keep important ones
    text = re.sub(r'[^a-z0-9\s+#./]', ' ', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords but keep important terms
    stop_words = set(stopwords.words('english'))
    # Keep some important words that are usually stopwords
    important_words = {'over', 'under', 'above', 'below', 'between', 'through', 'during', 'before', 'after'}
    stop_words = stop_words - important_words
    
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    return ' '.join(tokens)

def extract_email(text):
    """Extract email address with improved patterns"""
    if not text:
        return "Not detected"
    
    # Multiple email patterns
    email_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    ]
    
    for pattern in email_patterns:
        emails = re.findall(pattern, text)
        if emails:
            for email in emails:
                if '@' in email and '.' in email.split('@')[1]:
                    # Filter out common false positives
                    if not any(invalid in email.lower() for invalid in ['example.com', 'test.com', 'domain.com']):
                        return email.lower()
    
    # Try with context
    email_match = re.search(r'(?:e[-\s]?mail|email)\s*:?\s*([^\s,;]+@[^\s,;]+)', text, re.IGNORECASE)
    if email_match:
        return email_match.group(1).lower()
    
    return "Not detected"

def extract_phone(text):
    """Extract phone number with improved patterns for international formats"""
    if not text:
        return "Not detected"
    
    # Phone number patterns (international and local formats)
    phone_patterns = [
        # International format with country code
        r'\+\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        # US/Standard format
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        # General international
        r'\+?\d{10,15}',
        # With labels
        r'(?:phone|mobile|tel|cell)\s*:?\s*([\d\s\-\+\(\)]{10,})',
        # Saudi format
        r'\+?966[-.\s]?5\d[-.\s]?\d{3}[-.\s]?\d{4}',
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean the match
            phone = re.sub(r'[^\d+]', '', match)
            # Valid phone should have 10-15 digits
            if 10 <= len(phone) <= 15:
                # Return the original formatted version
                return match.strip()
    
    return "Not detected"

def extract_skills(text, skill_keywords):
    """Extract skills from text with improved matching"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_skills = set()
    
    for skill in skill_keywords:
        skill_lower = skill.lower()
        
        # Exact match
        if skill_lower in text_lower:
            found_skills.add(skill.title())
        
        # Match with common variations
        variations = [
            skill_lower.replace('.', ''),  # nodejs instead of node.js
            skill_lower.replace(' ', ''),   # machinelearning instead of machine learning
            skill_lower.replace('-', ' '),  # ci cd instead of ci-cd
        ]
        
        for variation in variations:
            if variation in text_lower and variation != skill_lower:
                found_skills.add(skill.title())
                break
    
    return sorted(list(found_skills))

def extract_linkedin_profile(text):
    """Extract LinkedIn profile URL"""
    if not text:
        return None
    
    linkedin_patterns = [
        r'linkedin\.com/in/[\w-]+',
        r'linkedin\.com/pub/[\w-]+',
        r'(?:https?://)?(?:www\.)?linkedin\.com/in/([\w-]+)',
    ]
    
    for pattern in linkedin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

def extract_github_profile(text):
    """Extract GitHub profile URL"""
    if not text:
        return None
    
    github_patterns = [
        r'github\.com/[\w-]+',
        r'(?:https?://)?(?:www\.)?github\.com/([\w-]+)',
    ]
    
    for pattern in github_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None