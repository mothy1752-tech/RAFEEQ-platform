"""
AI-powered resume generator for creating synthetic candidate profiles
matching job descriptions
"""

import random
from datetime import datetime, timedelta
import re

# Skills database by category
SKILLS_DATABASE = {
    'programming': [
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 
        'Rust', 'Swift', 'Kotlin', 'TypeScript', 'Scala', 'R'
    ],
    'web_frontend': [
        'React', 'Angular', 'Vue.js', 'HTML5', 'CSS3', 'Bootstrap', 
        'Tailwind CSS', 'SASS', 'jQuery', 'Next.js', 'Svelte'
    ],
    'web_backend': [
        'Node.js', 'Django', 'Flask', 'Spring Boot', 'Express.js', 
        'FastAPI', 'Laravel', 'Ruby on Rails', 'ASP.NET'
    ],
    'database': [
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server',
        'DynamoDB', 'Cassandra', 'Neo4j', 'Elasticsearch'
    ],
    'cloud_devops': [
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 
        'GitLab CI', 'Terraform', 'Ansible', 'CircleCI'
    ],
    'data_science': [
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 
        'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 
        'Data Analysis', 'Statistical Analysis', 'NLP'
    ],
    'mobile': [
        'React Native', 'Flutter', 'Swift', 'Kotlin', 'Android', 
        'iOS', 'Xamarin', 'Ionic'
    ],
    'tools': [
        'Git', 'GitHub', 'JIRA', 'Agile', 'Scrum', 'REST API', 
        'GraphQL', 'Microservices', 'Linux', 'Bash'
    ],
    'soft_skills': [
        'Team Leadership', 'Problem Solving', 'Communication', 
        'Project Management', 'Critical Thinking', 'Collaboration',
        'Time Management', 'Adaptability', 'Mentoring'
    ]
}

# Saudi Arabian names database
SAUDI_FIRST_NAMES = [
    'Mohammed', 'Ahmed', 'Abdullah', 'Khalid', 'Fahad', 'Saleh', 'Omar',
    'Ali', 'Hassan', 'Ibrahim', 'Yousef', 'Nasser', 'Saud', 'Faisal',
    'Tariq', 'Waleed', 'Majed', 'Mansour', 'Rashed', 'Saad',
    'Fatima', 'Aisha', 'Maha', 'Noura', 'Sara', 'Huda', 'Lama',
    'Reem', 'Haya', 'Nada', 'Shahad', 'Joud', 'Raghad', 'Aseel'
]

SAUDI_LAST_NAMES = [
    'Al-Ghamdi', 'Al-Zahrani', 'Al-Otaibi', 'Al-Harbi', 'Al-Shehri',
    'Al-Qahtani', 'Al-Dosari', 'Al-Mutairi', 'Al-Maliki', 'Al-Subai',
    'Al-Juhani', 'Al-Ahmadi', 'Al-Rashid', 'Al-Salem', 'Al-Turki',
    'Al-Saud', 'Al-Habib', 'Al-Khalifa', 'Al-Mansour', 'Al-Farah'
]

SAUDI_UNIVERSITIES = [
    'King Saud University',
    'King Abdulaziz University',
    'King Fahd University of Petroleum and Minerals',
    'Imam Abdulrahman Bin Faisal University',
    'King Khalid University',
    'Umm Al-Qura University',
    'Princess Nourah bint Abdulrahman University',
    'Taibah University',
    'Qassim University',
    'King Faisal University'
]

DEGREES = [
    "Bachelor's in Computer Science",
    "Bachelor's in Software Engineering",
    "Bachelor's in Information Technology",
    "Bachelor's in Data Science",
    "Master's in Computer Science",
    "Master's in Software Engineering",
    "Master's in Artificial Intelligence",
    "Bachelor's in Information Systems",
    "Master's in Cybersecurity",
    "Bachelor's in Computer Engineering"
]

COMPANIES = [
    'Saudi Aramco', 'SABIC', 'STC', 'Mobily', 'Zain KSA', 'NCB',
    'Al Rajhi Bank', 'SAMBA Financial Group', 'Riyad Bank', 'Accenture',
    'IBM', 'Microsoft', 'Oracle', 'SAP', 'Tech Mahindra', 'Wipro',
    'Elm Company', 'Tahakom', 'ekar', 'Careem', 'Jahez', 'Mrsool'
]

JOB_TITLES = [
    'Software Engineer', 'Senior Developer', 'Full Stack Developer',
    'Backend Developer', 'Frontend Developer', 'Data Scientist',
    'DevOps Engineer', 'Machine Learning Engineer', 'Mobile Developer',
    'System Administrator', 'Database Administrator', 'Technical Lead',
    'Software Architect', 'QA Engineer', 'Security Analyst'
]


def extract_keywords_from_job_description(job_description):
    """Extract relevant keywords and requirements from job description"""
    text_lower = job_description.lower()
    
    extracted_skills = []
    for category, skills in SKILLS_DATABASE.items():
        for skill in skills:
            if skill.lower() in text_lower:
                extracted_skills.append(skill)
    
    # Extract experience requirements
    exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
    exp_match = re.search(exp_pattern, text_lower)
    required_experience = int(exp_match.group(1)) if exp_match else random.randint(2, 8)
    
    # Detect seniority level
    seniority = 'mid'
    if any(word in text_lower for word in ['senior', 'lead', 'principal', 'architect']):
        seniority = 'senior'
    elif any(word in text_lower for word in ['junior', 'entry', 'graduate']):
        seniority = 'junior'
    
    return {
        'skills': extracted_skills if extracted_skills else get_random_skills(8),
        'experience_years': required_experience,
        'seniority': seniority
    }


def get_random_skills(count=10):
    """Get random skills from database"""
    all_skills = []
    for skills in SKILLS_DATABASE.values():
        all_skills.extend(skills)
    return random.sample(all_skills, min(count, len(all_skills)))


def generate_phone_number():
    """Generate Saudi Arabian phone number"""
    prefixes = ['050', '053', '054', '055', '056', '058', '059']
    return f"+966 {random.choice(prefixes)} {random.randint(100, 999)} {random.randint(1000, 9999)}"


def generate_email(first_name, last_name):
    """Generate professional email"""
    domains = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com']
    name_part = f"{first_name.lower()}.{last_name.lower().replace('al-', '')}"
    return f"{name_part}@{random.choice(domains)}"


def generate_work_experience(seniority, experience_years, skills):
    """Generate realistic work experience"""
    experiences = []
    current_year = datetime.now().year
    years_covered = 0
    
    num_jobs = 1 if seniority == 'junior' else (2 if seniority == 'mid' else 3)
    
    for i in range(num_jobs):
        job_duration = random.randint(2, 4) if i < num_jobs - 1 else (experience_years - years_covered)
        if job_duration <= 0:
            break
            
        end_year = current_year if i == 0 else (current_year - years_covered)
        start_year = end_year - job_duration
        
        company = random.choice(COMPANIES)
        title = random.choice(JOB_TITLES)
        
        # Adjust title based on seniority
        if seniority == 'senior' and 'Senior' not in title:
            title = f"Senior {title}"
        elif seniority == 'junior':
            title = title.replace('Senior ', '')
        
        job_skills = random.sample(skills, min(5, len(skills)))
        
        experience = {
            'title': title,
            'company': company,
            'duration': f"{start_year} - {'Present' if i == 0 else str(end_year)}",
            'description': f"Developed and maintained applications using {', '.join(job_skills[:3])}. Led projects improving system performance and user experience.",
            'skills_used': job_skills
        }
        
        experiences.append(experience)
        years_covered += job_duration
    
    return experiences


def generate_education(seniority):
    """Generate education background"""
    university = random.choice(SAUDI_UNIVERSITIES)
    degree = random.choice(DEGREES)
    
    current_year = datetime.now().year
    graduation_year = current_year - random.randint(3, 12)
    
    education = {
        'degree': degree,
        'university': university,
        'graduation_year': graduation_year,
        'gpa': round(random.uniform(3.5, 4.0), 2)
    }
    
    # Add master's for senior positions
    if seniority == 'senior' and random.random() > 0.5:
        master_degree = random.choice([
            "Master's in Computer Science",
            "Master's in Software Engineering",
            "Master's in Artificial Intelligence"
        ])
        education['masters'] = {
            'degree': master_degree,
            'university': random.choice(SAUDI_UNIVERSITIES),
            'graduation_year': graduation_year + 3
        }
    
    return education


def generate_certifications(skills):
    """Generate relevant certifications"""
    cert_mapping = {
        'AWS': 'AWS Certified Solutions Architect',
        'Azure': 'Microsoft Azure Administrator',
        'GCP': 'Google Cloud Professional',
        'Docker': 'Docker Certified Associate',
        'Kubernetes': 'Certified Kubernetes Administrator',
        'Python': 'Python Institute PCAP',
        'Java': 'Oracle Certified Java Programmer',
        'Machine Learning': 'TensorFlow Developer Certificate',
        'Scrum': 'Certified Scrum Master',
    }
    
    certifications = []
    for skill in skills:
        if skill in cert_mapping and random.random() > 0.6:
            certifications.append(cert_mapping[skill])
    
    # Add general certifications
    if random.random() > 0.7:
        certifications.append('PMP - Project Management Professional')
    
    return certifications[:4]  # Limit to 4 certifications


def generate_projects(skills):
    """Generate project descriptions"""
    projects = []
    project_templates = [
        "E-commerce platform with payment integration using {skills}",
        "Real-time data analytics dashboard built with {skills}",
        "Mobile application with {users} users using {skills}",
        "Microservices architecture implementation using {skills}",
        "Machine learning model for prediction with {accuracy}% accuracy using {skills}",
        "Enterprise resource planning system using {skills}",
        "Cloud-native application deployed on {cloud} using {skills}"
    ]
    
    num_projects = random.randint(2, 4)
    for _ in range(num_projects):
        template = random.choice(project_templates)
        project_skills = random.sample(skills, min(3, len(skills)))
        
        project = template.format(
            skills=', '.join(project_skills),
            users=f"{random.randint(10, 500)}K",
            accuracy=random.randint(85, 99),
            cloud=random.choice(['AWS', 'Azure', 'GCP'])
        )
        projects.append(project)
    
    return projects


def generate_resume_text(profile):
    """Generate formatted resume text"""
    resume_text = f"""
{profile['name']}
{profile['email']} | {profile['phone']}
Saudi Arabia

PROFESSIONAL SUMMARY
{profile['summary']}

SKILLS
{', '.join(profile['skills'])}

WORK EXPERIENCE
"""
    
    for exp in profile['experience']:
        resume_text += f"\n{exp['title']} at {exp['company']}\n"
        resume_text += f"{exp['duration']}\n"
        resume_text += f"• {exp['description']}\n"
        resume_text += f"Technologies: {', '.join(exp['skills_used'])}\n"
    
    resume_text += "\n\nEDUCATION\n"
    resume_text += f"{profile['education']['degree']}\n"
    resume_text += f"{profile['education']['university']}, {profile['education']['graduation_year']}\n"
    resume_text += f"GPA: {profile['education']['gpa']}/4.0\n"
    
    if 'masters' in profile['education']:
        resume_text += f"\n{profile['education']['masters']['degree']}\n"
        resume_text += f"{profile['education']['masters']['university']}, {profile['education']['masters']['graduation_year']}\n"
    
    if profile['certifications']:
        resume_text += "\n\nCERTIFICATIONS\n"
        for cert in profile['certifications']:
            resume_text += f"• {cert}\n"
    
    if profile['projects']:
        resume_text += "\n\nPROJECTS\n"
        for project in profile['projects']:
            resume_text += f"• {project}\n"
    
    return resume_text.strip()


def generate_candidate_profile(job_description):
    """Generate a complete candidate profile matching job description"""
    
    # Extract requirements from job description
    requirements = extract_keywords_from_job_description(job_description)
    
    # Generate basic info
    first_name = random.choice(SAUDI_FIRST_NAMES)
    last_name = random.choice(SAUDI_LAST_NAMES)
    full_name = f"{first_name} {last_name}"
    
    # Generate profile
    profile = {
        'name': full_name,
        'email': generate_email(first_name, last_name),
        'phone': generate_phone_number(),
        'skills': requirements['skills'],
        'seniority': requirements['seniority'],
        'experience_years': requirements['experience_years'],
        'summary': f"Experienced software professional with {requirements['experience_years']}+ years in software development. Expertise in {', '.join(requirements['skills'][:3])}. Proven track record of delivering high-quality solutions.",
    }
    
    # Generate detailed sections
    profile['experience'] = generate_work_experience(
        profile['seniority'], 
        profile['experience_years'], 
        profile['skills']
    )
    profile['education'] = generate_education(profile['seniority'])
    profile['certifications'] = generate_certifications(profile['skills'])
    profile['projects'] = generate_projects(profile['skills'])
    
    # Generate full resume text
    profile['resume_text'] = generate_resume_text(profile)
    
    return profile


def generate_multiple_candidates(job_description, count=5):
    """Generate multiple candidate profiles"""
    candidates = []
    for i in range(count):
        profile = generate_candidate_profile(job_description)
        profile['candidate_id'] = f"GEN_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}"
        candidates.append(profile)
    
    return candidates