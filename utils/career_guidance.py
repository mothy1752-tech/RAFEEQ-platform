from database import Database
import json

class CareerGuidanceAI:
    """
    Provide career guidance and support for people with disabilities
    """
    
    def __init__(self):
        self.db = Database()
        self.interview_tips = self._load_interview_tips()
        self.career_paths = self._load_career_paths()
        self.accommodation_templates = self._load_accommodation_templates()
        self.workplace_tips = self._load_workplace_tips()
    
    def _load_interview_tips(self):
        """Load interview tips by disability type"""
        return {
            'mobility_wheelchair': [
                {
                    'title': 'Discussing Accessibility Needs',
                    'content': 'Be clear and confident when discussing your accessibility needs. Frame them as practical requirements rather than limitations. Example: "I use a wheelchair for mobility and would need to ensure the workspace is accessible."'
                },
                {
                    'title': 'Highlighting Strengths',
                    'content': 'Focus on your skills, experience, and achievements. Emphasize your problem-solving abilities and adaptability, which are valuable traits developed through navigating accessibility challenges.'
                },
                {
                    'title': 'Asking About Accommodations',
                    'content': 'It\'s appropriate to ask about workplace accessibility during the interview. Questions like "Is the office wheelchair accessible?" or "What accommodations does the company provide?" show you\'re thinking practically about the role.'
                },
                {
                    'title': 'Remote Interview Setup',
                    'content': 'For video interviews, ensure your camera is at eye level and your background is professional. Test your equipment beforehand to avoid technical issues.'
                }
            ],
            'mobility_crutches': [
                {
                    'title': 'Discussing Mobility',
                    'content': 'If relevant, briefly mention your mobility aid and any accommodations you might need, such as accessible parking or a workspace near facilities.'
                },
                {
                    'title': 'Emphasizing Flexibility',
                    'content': 'Highlight your ability to adapt and manage your time effectively. These are valuable professional skills.'
                },
                {
                    'title': 'Workplace Layout',
                    'content': 'Ask about the office layout and whether workstations can be arranged to minimize walking distances if needed.'
                }
            ],
            'mobility_walker': [
                {
                    'title': 'Professional Presentation',
                    'content': 'Your mobility aid is simply a tool you use. Focus the conversation on your qualifications and how you can contribute to the role.'
                },
                {
                    'title': 'Practical Considerations',
                    'content': 'Discuss any practical needs, such as accessible parking, elevator access, or workspace arrangements that would help you perform optimally.'
                }
            ],
            'limited_mobility': [
                {
                    'title': 'Focus on Capabilities',
                    'content': 'Emphasize what you can do and how you\'ve successfully performed similar roles or tasks in the past.'
                },
                {
                    'title': 'Flexible Arrangements',
                    'content': 'If you need flexible hours or occasional remote work, frame it as a way to maximize your productivity and contribution.'
                }
            ],
            'general': [
                {
                    'title': 'Disclosure Decision',
                    'content': 'You\'re not required to disclose your disability unless you need accommodations. If you choose to disclose, focus on how you\'ve successfully managed your work responsibilities.'
                },
                {
                    'title': 'Confidence is Key',
                    'content': 'Approach the interview with confidence. Your disability is one aspect of who you are, but your skills and experience are what make you a strong candidate.'
                },
                {
                    'title': 'Prepare Questions',
                    'content': 'Prepare thoughtful questions about the role, team, and company culture. This shows your genuine interest and professionalism.'
                }
            ]
        }
    
    def _load_career_paths(self):
        """Load suitable career paths by skills and accessibility"""
        return {
            'technology': {
                'paths': [
                    'Software Developer',
                    'Web Developer',
                    'Data Analyst',
                    'IT Support Specialist',
                    'UX/UI Designer',
                    'Digital Marketing Specialist'
                ],
                'accessibility_notes': 'Technology careers often offer excellent remote work opportunities and flexible schedules. Many roles can be performed entirely from home with the right equipment.',
                'required_skills': ['Computer proficiency', 'Problem-solving', 'Analytical thinking']
            },
            'business': {
                'paths': [
                    'Business Analyst',
                    'Project Manager',
                    'Customer Service Representative',
                    'Sales Representative',
                    'Administrative Assistant',
                    'Human Resources Specialist'
                ],
                'accessibility_notes': 'Business roles increasingly offer hybrid and remote options. Many companies are implementing inclusive workplace policies.',
                'required_skills': ['Communication', 'Organization', 'Time management']
            },
            'creative': {
                'paths': [
                    'Graphic Designer',
                    'Content Writer',
                    'Social Media Manager',
                    'Video Editor',
                    'Photographer',
                    'Marketing Coordinator'
                ],
                'accessibility_notes': 'Creative fields offer significant flexibility and remote work opportunities. Portfolio-based work allows you to showcase abilities effectively.',
                'required_skills': ['Creativity', 'Attention to detail', 'Communication']
            },
            'education': {
                'paths': [
                    'Online Tutor',
                    'Curriculum Developer',
                    'Educational Content Creator',
                    'Training Specialist',
                    'E-learning Designer'
                ],
                'accessibility_notes': 'Education roles, especially online teaching and content development, offer excellent remote opportunities and flexible schedules.',
                'required_skills': ['Communication', 'Patience', 'Subject expertise']
            },
            'finance': {
                'paths': [
                    'Accountant',
                    'Financial Analyst',
                    'Bookkeeper',
                    'Tax Preparer',
                    'Financial Advisor'
                ],
                'accessibility_notes': 'Finance roles often involve desk work that can be performed remotely. Many firms offer flexible arrangements.',
                'required_skills': ['Analytical skills', 'Attention to detail', 'Mathematical ability']
            }
        }
    
    def _load_accommodation_templates(self):
        """Load accommodation request templates"""
        return {
            'wheelchair_access': {
                'subject': 'Workplace Accessibility Accommodation Request',
                'template': '''Dear [Hiring Manager/HR],

I am writing to discuss workplace accessibility accommodations for the [Position Title] role. I use a wheelchair for mobility and would like to ensure the workspace meets the following accessibility requirements:

• Wheelchair-accessible entrance and workspace
• Elevator access (if applicable)
• Accessible restroom facilities
• Accessible parking space
• Adequate workspace for wheelchair maneuverability

I am confident that with these accommodations in place, I can perform all essential functions of the role effectively. I am happy to discuss these requirements further and work together to ensure a smooth onboarding process.

Thank you for your consideration.

Best regards,
[Your Name]'''
            },
            'flexible_schedule': {
                'subject': 'Flexible Schedule Accommodation Request',
                'template': '''Dear [Hiring Manager/HR],

I am excited about the [Position Title] opportunity and would like to discuss a flexible work schedule arrangement. Due to [medical appointments/therapy sessions/transportation needs], I would benefit from:

• Flexible start and end times
• Option to work from home [X] days per week
• Ability to make up hours as needed

I am committed to meeting all job responsibilities and deadlines. This flexibility would enable me to maintain optimal productivity while managing my health needs.

I look forward to discussing how we can structure a schedule that works for both the team and my requirements.

Best regards,
[Your Name]'''
            },
            'remote_work': {
                'subject': 'Remote Work Accommodation Request',
                'template': '''Dear [Hiring Manager/HR],

I am very interested in the [Position Title] position and would like to discuss the possibility of a remote work arrangement. Working remotely would allow me to:

• Eliminate transportation challenges
• Work in an optimally configured home office
• Maintain consistent productivity without physical barriers
• Reduce fatigue from commuting

I have [X years] of experience working remotely and am proficient with all necessary collaboration tools including [list tools]. I am confident I can deliver excellent results while working from home.

I am happy to discuss this arrangement further and explore options that work for the team.

Best regards,
[Your Name]'''
            },
            'special_equipment': {
                'subject': 'Special Equipment Accommodation Request',
                'template': '''Dear [Hiring Manager/HR],

I am writing regarding the [Position Title] role to discuss equipment accommodations that would enable me to perform at my best. I would need the following:

• [Specific equipment, e.g., ergonomic chair, adjustable desk]
• [Assistive technology, e.g., screen reader, voice recognition software]
• [Other requirements]

I have experience using this equipment and it enables me to work efficiently and comfortably. I am happy to provide additional information about these tools and how they support my work.

Thank you for considering these accommodations.

Best regards,
[Your Name]'''
            }
        }
    
    def _load_workplace_tips(self):
        """Load workplace success tips"""
        return {
            'mobility_wheelchair': [
                'Organize your workspace for maximum efficiency and accessibility',
                'Build relationships with colleagues to create a supportive network',
                'Communicate openly about your needs while maintaining professionalism',
                'Take regular breaks to maintain comfort and productivity',
                'Advocate for yourself when accessibility improvements are needed'
            ],
            'mobility_crutches': [
                'Plan your day to minimize unnecessary movement',
                'Keep frequently used items within easy reach',
                'Communicate with your supervisor about any needed adjustments',
                'Take breaks as needed to manage fatigue',
                'Build strong professional relationships'
            ],
            'mobility_walker': [
                'Arrange your workspace for optimal accessibility',
                'Communicate your needs clearly and professionally',
                'Focus on your strengths and contributions',
                'Maintain a positive attitude and professional demeanor',
                'Seek support when needed'
            ],
            'general': [
                'Focus on your performance and contributions',
                'Build strong professional relationships',
                'Communicate effectively with your team',
                'Stay organized and manage your time well',
                'Continue developing your skills',
                'Advocate for yourself professionally',
                'Maintain work-life balance'
            ]
        }
    
    def get_interview_tips(self, disability_type, job_type=None):
        """
        Provide disability-specific interview guidance
        """
        tips = self.interview_tips.get(disability_type, self.interview_tips['general'])
        
        # Add general tips
        general_tips = self.interview_tips['general']
        
        all_tips = tips + general_tips
        
        return {
            'disability_type': disability_type,
            'tips': all_tips,
            'general_advice': 'Remember: You are interviewing them as much as they are interviewing you. Assess whether the company culture and environment will support your success.'
        }
    
    def suggest_career_paths(self, user_profile):
        """
        Recommend suitable career paths based on:
        - Skills and interests
        - Physical capabilities
        - Market demand
        - Accessibility considerations
        """
        skills = user_profile.get('skills', [])
        interests = user_profile.get('interests', [])
        disability_type = user_profile.get('disability_type')
        
        suggested_paths = []
        
        # Match skills to career fields
        for field, data in self.career_paths.items():
            match_score = 0
            
            # Check skill match
            for skill in skills:
                if any(req_skill.lower() in skill.lower() for req_skill in data['required_skills']):
                    match_score += 1
            
            # Check interest match
            for interest in interests:
                if field.lower() in interest.lower():
                    match_score += 2
            
            if match_score > 0:
                suggested_paths.append({
                    'field': field.title(),
                    'paths': data['paths'],
                    'accessibility_notes': data['accessibility_notes'],
                    'required_skills': data['required_skills'],
                    'match_score': match_score
                })
        
        suggested_paths.sort(key=lambda x: x['match_score'], reverse=True)
        
        if suggested_paths:
            return suggested_paths[:3]
        
        return [
            {
                'field': k.title(),
                'paths': v['paths'],
                'accessibility_notes': v['accessibility_notes'],
                'required_skills': v['required_skills'],
                'match_score': 0
            }
            for k, v in list(self.career_paths.items())[:3]
        ]
    
    def generate_accommodation_request_template(self, accommodation_type):
        """
        Create professional accommodation request letters
        """
        template = self.accommodation_templates.get(accommodation_type)
        
        if not template:
            return None
        
        return {
            'type': accommodation_type,
            'subject': template['subject'],
            'template': template['template'],
            'tips': [
                'Customize the template with your specific details',
                'Be clear and specific about your needs',
                'Focus on how accommodations enable your productivity',
                'Maintain a professional and positive tone',
                'Be open to discussion and collaboration'
            ]
        }
    
    def provide_workplace_tips(self, disability_type):
        """
        Tips for succeeding in the workplace
        """
        tips = self.workplace_tips.get(disability_type, self.workplace_tips['general'])
        
        return {
            'disability_type': disability_type,
            'tips': tips,
            'additional_resources': [
                'Know your rights under disability employment laws',
                'Document any accessibility issues or concerns',
                'Seek mentorship from other professionals',
                'Join professional networks and communities',
                'Continue developing your skills and expertise'
            ]
        }
    
    def get_guidance_content(self, category, disability_type=None):
        """
        Get guidance content from database by category
        """
        conn = self.db.connect()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        try:
            if disability_type:
                cursor.execute('''
                    SELECT * FROM guidance_content
                    WHERE category = %s AND (disability_specific = %s OR disability_specific IS NULL)
                    ORDER BY helpful_count DESC, created_at DESC
                    LIMIT 10
                ''', (category, disability_type))
            else:
                cursor.execute('''
                    SELECT * FROM guidance_content
                    WHERE category = %s
                    ORDER BY helpful_count DESC, created_at DESC
                    LIMIT 10
                ''', (category,))
            
            content = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return content
            
        except Exception as e:
            cursor.close()
            conn.close()
            return []
    
    def mark_content_helpful(self, content_id):
        """
        Increment helpful count for content
        """
        conn = self.db.connect()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE guidance_content
                SET helpful_count = helpful_count + 1
                WHERE content_id = %s
            ''', (content_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return False


def get_career_guidance(user_profile, guidance_type='interview'):
    """
    Main function to get career guidance
    """
    guidance = CareerGuidanceAI()
    
    disability_type = user_profile.get('disability_type', 'general')
    
    if guidance_type == 'interview':
        return guidance.get_interview_tips(disability_type)
    elif guidance_type == 'career_paths':
        return guidance.suggest_career_paths(user_profile)
    elif guidance_type == 'workplace':
        return guidance.provide_workplace_tips(disability_type)
    else:
        return guidance.get_guidance_content(guidance_type, disability_type)
