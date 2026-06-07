
import re
from utils.text_processing import extract_email, extract_phone, extract_skills, SKILL_KEYWORDS

# Course recommendations by field
COURSES = {
    'data_science': [
        {'name': 'Machine Learning Crash Course by Google', 'url': 'https://developers.google.com/machine-learning/crash-course', 'free': True},
        {'name': 'Data Science Professional Certificate - IBM', 'url': 'https://www.coursera.org/professional-certificates/ibm-data-science', 'free': False},
        {'name': 'Applied Data Science with Python - University of Michigan', 'url': 'https://www.coursera.org/specializations/data-science-python', 'free': False},
        {'name': 'TensorFlow Developer Certificate', 'url': 'https://www.tensorflow.org/certificate', 'free': False},
        {'name': 'Machine Learning by Andrew Ng', 'url': 'https://www.coursera.org/learn/machine-learning', 'free': False},
    ],
    'web_development': [
        {'name': 'The Complete Web Developer Course', 'url': 'https://www.udemy.com/course/the-complete-web-developer-course-2/', 'free': False},
        {'name': 'React - The Complete Guide', 'url': 'https://www.udemy.com/course/react-the-complete-guide/', 'free': False},
        {'name': 'Node.js, Express, MongoDB & More', 'url': 'https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/', 'free': False},
        {'name': 'Full Stack Web Development - Free', 'url': 'https://www.freecodecamp.org/', 'free': True},
        {'name': 'Django for Beginners', 'url': 'https://www.udemy.com/course/django-for-beginners/', 'free': False},
    ],
    'mobile_development': [
        {'name': 'iOS & Swift - Complete iOS Development Bootcamp', 'url': 'https://www.udemy.com/course/ios-13-app-development-bootcamp/', 'free': False},
        {'name': 'Android Development for Beginners', 'url': 'https://www.udacity.com/course/android-basics-nanodegree-by-google--nd803', 'free': False},
        {'name': 'Flutter & Dart - Complete Guide', 'url': 'https://www.udemy.com/course/learn-flutter-dart-to-build-ios-android-apps/', 'free': False},
        {'name': 'React Native - The Practical Guide', 'url': 'https://www.udemy.com/course/react-native-the-practical-guide/', 'free': False},
    ],
    'devops': [
        {'name': 'Docker and Kubernetes: The Complete Guide', 'url': 'https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/', 'free': False},
        {'name': 'AWS Certified Solutions Architect', 'url': 'https://aws.amazon.com/certification/certified-solutions-architect-associate/', 'free': False},
        {'name': 'DevOps Engineering Course', 'url': 'https://www.udacity.com/course/cloud-dev-ops-nanodegree--nd9991', 'free': False},
        {'name': 'CI/CD with Jenkins', 'url': 'https://www.udemy.com/course/jenkins-from-zero-to-hero/', 'free': False},
    ],
    'cybersecurity': [
        {'name': 'Cybersecurity Specialization', 'url': 'https://www.coursera.org/specializations/cyber-security', 'free': False},
        {'name': 'Ethical Hacking from Scratch', 'url': 'https://www.udemy.com/course/learn-ethical-hacking-from-scratch/', 'free': False},
        {'name': 'CompTIA Security+ Certification', 'url': 'https://www.comptia.org/certifications/security', 'free': False},
    ],
    'general': [
        {'name': 'CS50: Introduction to Computer Science', 'url': 'https://www.edx.org/course/introduction-computer-science-harvardx-cs50x', 'free': True},
        {'name': 'Python for Everybody', 'url': 'https://www.py4e.com/', 'free': True},
        {'name': 'Git and GitHub for Beginners', 'url': 'https://www.udemy.com/course/git-and-github-for-beginners/', 'free': False},
    ]
}

# Keywords for field detection
FIELD_KEYWORDS = {
    'data_science': ['machine learning', 'data science', 'deep learning', 'ai', 'artificial intelligence', 
                     'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'data analysis', 'statistics'],
    'web_development': ['web development', 'html', 'css', 'javascript', 'react', 'angular', 'vue', 
                        'node.js', 'django', 'flask', 'php', 'laravel', 'wordpress'],
    'mobile_development': ['mobile', 'android', 'ios', 'swift', 'kotlin', 'flutter', 'react native'],
    'devops': ['devops', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'terraform'],
    'cybersecurity': ['security', 'cybersecurity', 'ethical hacking', 'penetration testing', 'network security'],
}

def analyze_resume(text):
    """Analyze resume and extract key information"""
    
    # Extract basic info
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    
    # Extract skills
    skills = extract_skills(text, SKILL_KEYWORDS)
    
    # Detect field
    detected_field = detect_field(text, skills)
    
    # Calculate experience years
    experience = extract_experience(text)
    
    # Extract education
    education = extract_education(text)
    
    # Calculate resume score
    score = calculate_resume_score(text, skills)
    
    # Generate recommendations
    recommendations = generate_recommendations(text, skills)
    
    return {
        'name': name,
        'email': email,
        'phone': phone,
        'skills': skills,
        'detected_field': detected_field,
        'experience': experience,
        'education': education,
        'score': score,
        'recommendations': recommendations
    }

def extract_name(text):
    """Extract name from resume with improved logic"""
    lines = text.split('\n')
    
    # Skip common header words
    skip_words = ['resume', 'cv', 'curriculum vitae', 'personal data', 'personal information', 
                  'contact', 'profile', 'bio', 'about', 'overview', 'summary']
    
    # Look for name patterns
    name_patterns = [
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$',  # John Smith format
        r'name\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',  # Name: John Smith
        r'([A-Z][A-Z\s]+)(?:\n|$)',  # JOHN SMITH format
    ]
    
    for line in lines[:10]:
        line = line.strip()
        if not line or len(line) < 3 or len(line) > 60:
            continue
            
        line_lower = line.lower()
        
        # Skip lines with skip words
        if any(word in line_lower for word in skip_words):
            continue
            
        # Skip lines with email or phone
        if '@' in line or re.search(r'\d{3,}', line):
            continue
        
        # Try patterns
        for pattern in name_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Validate name (should be 2-4 words, each starting with capital)
                words = name.split()
                if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                    return name
        
        # Simple heuristic: first line that looks like a name
        words = line.split()
        if 2 <= len(words) <= 4 and all(len(w) > 1 for w in words):
            if not any(char.isdigit() for char in line) and not any(c in line for c in ['@', ':', ';', '/']):
                return line
    
    return "Not detected"

def extract_experience(text):
    """Extract years of experience with improved patterns"""
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'experience\s*:?\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*experience',
        r'(\d+)\+?\s*yrs?\s*experience',
        r'experience\s*:?\s*(\d+)\+?\s*yrs?',
    ]
    
    text_lower = text.lower()
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            years = int(match.group(1))
            return f"{years}+ years"
    
    # Try to count work experiences
    work_patterns = [
        r'(\d{4})\s*-\s*(\d{4}|present|current)',
        r'(\d{4})\s*to\s*(\d{4}|present|current)',
    ]
    
    total_years = 0
    for pattern in work_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            start_year = int(match[0])
            end_year = 2024 if match[1] in ['present', 'current'] else int(match[1])
            total_years += max(0, end_year - start_year)
    
    if total_years > 0:
        return f"{total_years}+ years"
    
    return "Not specified"

def extract_education(text):
    """Extract education information with better logic"""
    education_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'diploma', 'degree', 
                          'university', 'college', 'institute', 'b.sc', 'm.sc', 'mba', 
                          'b.tech', 'm.tech', 'bsc', 'msc', 'ba', 'ma']
    
    education_info = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Skip very short lines or lines that are clearly not education
        if len(line) < 5:
            continue
            
        # Check if line contains education keywords
        if any(keyword in line_lower for keyword in education_keywords):
            # Get this line and possibly next line for complete info
            edu_text = line.strip()
            if i + 1 < len(lines) and len(lines[i + 1].strip()) > 3:
                next_line = lines[i + 1].strip()
                # Add next line if it doesn't contain education keyword (continuation)
                if not any(keyword in next_line.lower() for keyword in education_keywords):
                    edu_text += " " + next_line
            
            # Clean up the text
            edu_text = re.sub(r'\s+', ' ', edu_text)
            education_info.append(edu_text)
    
    if education_info:
        # Return first 2 education entries
        return '; '.join(education_info[:2])
    
    return "Not specified"

def detect_field(text, skills):
    """Detect the career field based on skills and text content"""
    text_lower = text.lower()
    field_scores = {}
    
    for field, keywords in FIELD_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in text_lower:
                score += 1
        field_scores[field] = score
    
    if max(field_scores.values()) > 0:
        return max(field_scores, key=field_scores.get)
    return 'general'

def calculate_resume_score(text, skills):
    """Calculate resume quality score out of 100"""
    score = 0
    text_lower = text.lower()
    
    # Check for important sections (20 points each)
    if 'objective' in text_lower or 'summary' in text_lower or 'profile' in text_lower:
        score += 20
    if 'experience' in text_lower or 'work history' in text_lower or 'employment' in text_lower:
        score += 20
    if 'education' in text_lower or 'qualification' in text_lower:
        score += 20
    if 'skills' in text_lower or 'technical skills' in text_lower:
        score += 15
    if 'project' in text_lower or 'portfolio' in text_lower:
        score += 15
    if 'certification' in text_lower or 'certificate' in text_lower or 'award' in text_lower:
        score += 10
    
    return min(score, 100)

def generate_recommendations(text, skills):
    """Generate recommendations for resume improvement"""
    recommendations = []
    text_lower = text.lower()
    
    if 'objective' not in text_lower and 'summary' not in text_lower and 'profile' not in text_lower:
        recommendations.append("Add a professional summary or objective statement at the beginning")
    
    if 'project' not in text_lower:
        recommendations.append("Include relevant projects to showcase your practical skills")
    
    if len(skills) < 5:
        recommendations.append("Add more technical skills relevant to your field")
    
    if 'certification' not in text_lower and 'certificate' not in text_lower:
        recommendations.append("Consider adding relevant certifications to strengthen your profile")
    
    if 'achievement' not in text_lower and 'award' not in text_lower:
        recommendations.append("Highlight your achievements and awards if any")
    
    if 'linkedin' not in text_lower and 'github' not in text_lower:
        recommendations.append("Add links to your LinkedIn profile or GitHub portfolio")
    
    return recommendations

def get_course_recommendations(field, num_courses=5):
    """Get course recommendations based on detected field"""
    if field in COURSES:
        return COURSES[field][:num_courses]
    return COURSES['general'][:num_courses]
