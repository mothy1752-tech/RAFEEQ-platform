import json
import random
from datetime import datetime

class DisabilityFriendlyResumeGenerator:
    """
    Generate professional resumes that highlight abilities
    while addressing accessibility needs professionally
    """
    
    def __init__(self):
        self.strength_based_phrases = {
            'mobility_wheelchair': [
                'Proficient in remote collaboration tools',
                'Strong digital communication skills',
                'Excellent problem-solving abilities',
                'Adaptable to various work environments'
            ],
            'mobility_crutches': [
                'Flexible and adaptable professional',
                'Strong time management skills',
                'Excellent organizational abilities',
                'Proven ability to work independently'
            ],
            'mobility_walker': [
                'Detail-oriented professional',
                'Strong analytical skills',
                'Excellent written communication',
                'Committed to continuous learning'
            ],
            'limited_mobility': [
                'Resourceful and innovative thinker',
                'Strong technical proficiency',
                'Excellent multitasking abilities',
                'Dedicated team player'
            ],
            'other': [
                'Highly motivated professional',
                'Strong work ethic',
                'Excellent communication skills',
                'Proven track record of success'
            ]
        }
    
    def generate_resume(self, user_profile, work_history, education, skills):
        """
        Creates a professional CV that:
        - Emphasizes what the person CAN do
        - Highlights transferable skills
        - Professionally mentions required accommodations
        - Uses strength-based language
        - Formats for ATS compatibility
        """
        resume_data = {
            'personal_info': {
                'name': user_profile.get('full_name', ''),
                'email': user_profile.get('email', ''),
                'phone': user_profile.get('phone', ''),
                'location': user_profile.get('location', '')
            },
            'professional_summary': self.generate_professional_summary(user_profile, skills),
            'skills': self.format_skills(skills, user_profile.get('disability_type')),
            'work_experience': self.format_work_history(work_history),
            'education': self.format_education(education),
            'accessibility_statement': self.create_accessibility_statement(user_profile) if user_profile.get('include_accessibility_statement') else None
        }
        
        return resume_data
    
    def generate_professional_summary(self, user_data, skills):
        """
        Creates compelling professional summary that focuses on
        capabilities and achievements
        """
        disability_type = user_data.get('disability_type', 'other')
        strength_phrases = self.strength_based_phrases.get(disability_type, self.strength_based_phrases['other'])
        
        # Build summary
        summary_parts = []
        
        # Opening statement
        summary_parts.append(f"Dedicated and accomplished professional with expertise in {', '.join(skills[:3]) if skills else 'various fields'}.")
        
        # Strength-based statement
        summary_parts.append(random.choice(strength_phrases))
        
        # Work mode preference
        work_mode = user_data.get('preferred_work_mode')
        if work_mode == 'remote':
            summary_parts.append("Experienced in remote work environments with proven ability to deliver results independently.")
        elif work_mode == 'hybrid':
            summary_parts.append("Flexible professional comfortable with both remote and on-site work arrangements.")
        elif work_mode == 'flexible':
            summary_parts.append("Adaptable professional seeking flexible work arrangements to maximize productivity.")
        
        # Closing statement
        summary_parts.append("Committed to excellence and continuous professional development.")
        
        return ' '.join(summary_parts)
    
    def suggest_skill_presentation(self, skills, disability_type):
        """
        Recommends how to present skills based on disability context
        """
        skill_categories = {
            'technical': [],
            'soft': [],
            'digital': []
        }
        
        # Common technical skills
        technical_keywords = ['programming', 'software', 'data', 'analysis', 'design', 'development', 'engineering']
        # Common soft skills
        soft_keywords = ['communication', 'leadership', 'teamwork', 'problem-solving', 'management', 'organization']
        # Digital skills
        digital_keywords = ['microsoft', 'google', 'zoom', 'slack', 'remote', 'collaboration', 'virtual']
        
        for skill in skills:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in technical_keywords):
                skill_categories['technical'].append(skill)
            elif any(keyword in skill_lower for keyword in soft_keywords):
                skill_categories['soft'].append(skill)
            elif any(keyword in skill_lower for keyword in digital_keywords):
                skill_categories['digital'].append(skill)
            else:
                skill_categories['technical'].append(skill)
        
        return skill_categories
    
    def format_skills(self, skills, disability_type):
        """Format skills in a professional manner"""
        if not skills:
            return []
        
        categorized = self.suggest_skill_presentation(skills, disability_type)
        
        formatted_skills = []
        if categorized['technical']:
            formatted_skills.append({
                'category': 'Technical Skills',
                'items': categorized['technical']
            })
        if categorized['digital']:
            formatted_skills.append({
                'category': 'Digital Proficiency',
                'items': categorized['digital']
            })
        if categorized['soft']:
            formatted_skills.append({
                'category': 'Professional Skills',
                'items': categorized['soft']
            })
        
        return formatted_skills
    
    def format_work_history(self, work_history):
        """Format work history professionally"""
        if not work_history:
            return []
        
        formatted_history = []
        for job in work_history:
            formatted_job = {
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'duration': job.get('duration', ''),
                'responsibilities': job.get('responsibilities', []),
                'achievements': job.get('achievements', [])
            }
            formatted_history.append(formatted_job)
        
        return formatted_history
    
    def format_education(self, education):
        """Format education section"""
        if not education:
            return []
        
        formatted_education = []
        for edu in education:
            formatted_edu = {
                'degree': edu.get('degree', ''),
                'institution': edu.get('institution', ''),
                'year': edu.get('year', ''),
                'honors': edu.get('honors', '')
            }
            formatted_education.append(formatted_edu)
        
        return formatted_education
    
    def create_accessibility_statement(self, needs):
        """
        Generates professional accessibility requirements section
        """
        statements = []
        
        if needs.get('requires_accessible_building'):
            statements.append("Wheelchair-accessible workspace required")
        
        if needs.get('requires_flexible_hours'):
            statements.append("Flexible work schedule preferred")
        
        if needs.get('preferred_work_mode') == 'remote':
            statements.append("Remote work arrangement preferred")
        elif needs.get('preferred_work_mode') == 'hybrid':
            statements.append("Hybrid work arrangement preferred")
        
        if needs.get('requires_special_equipment'):
            equipment = needs.get('equipment_details', '')
            if equipment:
                statements.append(f"Specialized equipment: {equipment}")
        
        if not statements:
            return None
        
        return {
            'title': 'Workplace Accommodations',
            'items': statements
        }
    
    def generate_resume_text(self, resume_data):
        """
        Generate plain text version of resume for processing
        """
        text_parts = []
        
        # Personal info
        personal = resume_data['personal_info']
        text_parts.append(f"{personal['name']}")
        text_parts.append(f"{personal['email']} | {personal['phone']}")
        if personal.get('location'):
            text_parts.append(personal['location'])
        text_parts.append("\n")
        
        # Professional summary
        text_parts.append("PROFESSIONAL SUMMARY")
        text_parts.append(resume_data['professional_summary'])
        text_parts.append("\n")
        
        # Skills
        text_parts.append("SKILLS")
        for skill_group in resume_data['skills']:
            text_parts.append(f"{skill_group['category']}: {', '.join(skill_group['items'])}")
        text_parts.append("\n")
        
        # Work experience
        if resume_data['work_experience']:
            text_parts.append("WORK EXPERIENCE")
            for job in resume_data['work_experience']:
                text_parts.append(f"{job['title']} at {job['company']}")
                text_parts.append(job['duration'])
                if job.get('responsibilities'):
                    for resp in job['responsibilities']:
                        text_parts.append(f"• {resp}")
                if job.get('achievements'):
                    for ach in job['achievements']:
                        text_parts.append(f"• {ach}")
                text_parts.append("")
        
        # Education
        if resume_data['education']:
            text_parts.append("EDUCATION")
            for edu in resume_data['education']:
                text_parts.append(f"{edu['degree']} - {edu['institution']}")
                text_parts.append(edu['year'])
                if edu.get('honors'):
                    text_parts.append(edu['honors'])
                text_parts.append("")
        
        # Accessibility statement (optional)
        if resume_data.get('accessibility_statement'):
            acc_stmt = resume_data['accessibility_statement']
            text_parts.append(acc_stmt['title'].upper())
            for item in acc_stmt['items']:
                text_parts.append(f"• {item}")
        
        return '\n'.join(text_parts)


def generate_ai_resume(user_id, user_profile, work_history=None, education=None, skills=None):
    """
    Main function to generate AI-powered resume
    """
    generator = DisabilityFriendlyResumeGenerator()
    
    # Default values if not provided
    if not work_history:
        work_history = []
    if not education:
        education = []
    if not skills:
        skills = []
    
    # Generate resume
    resume_data = generator.generate_resume(user_profile, work_history, education, skills)
    
    # Generate text version
    resume_text = generator.generate_resume_text(resume_data)
    
    return {
        'resume_data': resume_data,
        'resume_text': resume_text,
        'generated_at': datetime.now().isoformat(),
        'user_id': user_id
    }
