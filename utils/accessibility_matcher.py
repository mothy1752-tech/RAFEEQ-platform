import pandas as pd
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AccessibilityJobMatcher:
    """
    Advanced job matching considering disability needs and accessibility features
    """
    
    def __init__(self):
        self.accessibility_weights = {
            'remote_work': 0.25,
            'flexible_hours': 0.20,
            'wheelchair_accessible': 0.20,
            'accessible_building': 0.15,
            'special_equipment': 0.10,
            'disability_certified': 0.10
        }
    
    def filter_by_accessibility(self, jobs_df, user_needs):
        """
        Filter jobs based on:
        - Building accessibility (wheelchair access, elevators)
        - Remote work availability
        - Flexible hours
        - Required accommodations availability
        - Transportation accessibility
        """
        if jobs_df.empty:
            return jobs_df
        
        filtered_jobs = jobs_df.copy()
        
        # Filter by work mode preference
        work_mode = user_needs.get('preferred_work_mode')
        if work_mode == 'remote':
            filtered_jobs = filtered_jobs[
                (filtered_jobs.get('is_remote_available', False) == True) |
                (filtered_jobs.get('is_hybrid_available', False) == True)
            ]
        elif work_mode == 'hybrid':
            filtered_jobs = filtered_jobs[
                filtered_jobs.get('is_hybrid_available', False) == True
            ]
        
        # Filter by accessibility requirements
        if user_needs.get('requires_accessible_building'):
            filtered_jobs = filtered_jobs[
                (filtered_jobs.get('wheelchair_accessible', False) == True) |
                (filtered_jobs.get('is_remote_available', False) == True)
            ]
        
        if user_needs.get('requires_flexible_hours'):
            filtered_jobs = filtered_jobs[
                (filtered_jobs.get('flexible_hours', False) == True) |
                (filtered_jobs.get('is_remote_available', False) == True)
            ]
        
        if user_needs.get('requires_special_equipment'):
            filtered_jobs = filtered_jobs[
                (filtered_jobs.get('provides_special_equipment', False) == True) |
                (filtered_jobs.get('is_remote_available', False) == True)
            ]
        
        return filtered_jobs
    
    def calculate_accessibility_score(self, job, user_profile):
        """
        Score jobs based on how well they match accessibility needs
        Returns: 0-100 score
        """
        score = 0
        max_score = 100
        
        # Remote work availability (25 points)
        if user_profile.get('preferred_work_mode') == 'remote':
            if job.get('is_remote_available'):
                score += 25
            elif job.get('is_hybrid_available'):
                score += 15
        elif user_profile.get('preferred_work_mode') == 'hybrid':
            if job.get('is_hybrid_available'):
                score += 25
            elif job.get('is_remote_available'):
                score += 20
        else:
            score += 10  # Base score for onsite
        
        # Flexible hours (20 points)
        if user_profile.get('requires_flexible_hours'):
            if job.get('flexible_hours'):
                score += 20
            elif job.get('is_remote_available'):
                score += 15
        else:
            score += 10
        
        # Wheelchair accessibility (20 points)
        if user_profile.get('requires_accessible_building'):
            if job.get('wheelchair_accessible') and job.get('has_elevator'):
                score += 20
            elif job.get('wheelchair_accessible'):
                score += 15
            elif job.get('is_remote_available'):
                score += 20
        else:
            score += 10
        
        # Building features (15 points)
        building_score = 0
        if job.get('has_accessible_parking'):
            building_score += 5
        if job.get('has_accessible_restrooms'):
            building_score += 5
        if job.get('has_elevator'):
            building_score += 5
        score += building_score
        
        # Special equipment (10 points)
        if user_profile.get('requires_special_equipment'):
            if job.get('provides_special_equipment'):
                score += 10
        else:
            score += 5
        
        # Disability-friendly certification (10 points)
        if job.get('disability_friendly_certified'):
            score += 10
        
        return min(score, max_score)
    
    def get_smart_recommendations(self, user_profile, jobs_df, processed_resume_text=None, top_n=10):
        """
        Combines traditional job matching with accessibility matching
        """
        if jobs_df.empty:
            return pd.DataFrame()
        
        # Step 1: Filter by accessibility requirements
        accessible_jobs = self.filter_by_accessibility(jobs_df, user_profile)
        
        if accessible_jobs.empty:
            return pd.DataFrame()
        
        # Step 2: Calculate accessibility scores
        accessible_jobs['accessibility_score'] = accessible_jobs.apply(
            lambda job: self.calculate_accessibility_score(job, user_profile),
            axis=1
        )
        
        # Step 3: If resume text provided, calculate skill match
        if processed_resume_text and 'skills_required' in accessible_jobs.columns:
            skill_scores = self._calculate_skill_match(
                processed_resume_text,
                accessible_jobs
            )
            accessible_jobs['skill_match_score'] = skill_scores
            
            # Combined score (60% accessibility, 40% skills)
            accessible_jobs['match_score'] = (
                accessible_jobs['accessibility_score'] * 0.6 +
                accessible_jobs['skill_match_score'] * 0.4
            )
        else:
            # Use only accessibility score
            accessible_jobs['match_score'] = accessible_jobs['accessibility_score']
        
        # Step 4: Sort by match score and return top N
        recommendations = accessible_jobs.sort_values(
            'match_score',
            ascending=False
        ).head(top_n)
        
        return recommendations
    
    def _calculate_skill_match(self, resume_text, jobs_df):
        """
        Calculate skill match between resume and jobs using TF-IDF
        """
        try:
            # Prepare job descriptions
            job_texts = []
            for _, job in jobs_df.iterrows():
                job_text = f"{job.get('position_name', '')} {job.get('description', '')} {job.get('skills_required', '')}"
                job_texts.append(job_text)
            
            # Add resume text
            all_texts = [resume_text] + job_texts
            
            # Calculate TF-IDF
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # Calculate cosine similarity
            resume_vector = tfidf_matrix[0:1]
            job_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(resume_vector, job_vectors)[0]
            
            # Convert to 0-100 scale
            skill_scores = (similarities * 100).tolist()
            
            return skill_scores
        except Exception as e:
            # Return default scores if calculation fails
            return [50] * len(jobs_df)
    
    def get_accessibility_insights(self, job, user_profile):
        """
        Get detailed accessibility insights for a specific job
        """
        insights = {
            'matches': [],
            'concerns': [],
            'recommendations': []
        }
        
        # Check matches
        if user_profile.get('preferred_work_mode') == 'remote' and job.get('is_remote_available'):
            insights['matches'].append('Remote work option available')
        
        if user_profile.get('requires_flexible_hours') and job.get('flexible_hours'):
            insights['matches'].append('Flexible work hours offered')
        
        if user_profile.get('requires_accessible_building'):
            if job.get('wheelchair_accessible'):
                insights['matches'].append('Wheelchair accessible facility')
            if job.get('has_elevator'):
                insights['matches'].append('Elevator access available')
            if job.get('has_accessible_parking'):
                insights['matches'].append('Accessible parking available')
        
        if job.get('disability_friendly_certified'):
            insights['matches'].append('Certified disability-friendly employer')
        
        # Check concerns
        if user_profile.get('requires_accessible_building') and not job.get('wheelchair_accessible') and not job.get('is_remote_available'):
            insights['concerns'].append('Building accessibility not confirmed')
        
        if user_profile.get('requires_flexible_hours') and not job.get('flexible_hours') and not job.get('is_remote_available'):
            insights['concerns'].append('Flexible hours not mentioned')
        
        if user_profile.get('requires_special_equipment') and not job.get('provides_special_equipment'):
            insights['concerns'].append('Special equipment provision not confirmed')
        
        # Recommendations
        if insights['concerns']:
            insights['recommendations'].append('Contact employer to discuss accommodation options')
        
        if not job.get('accommodation_policy'):
            insights['recommendations'].append('Inquire about accommodation policies during interview')
        
        return insights


def match_jobs_with_accessibility(user_profile, jobs_df, resume_text=None, top_n=10):
    """
    Main function to get accessibility-aware job recommendations
    """
    matcher = AccessibilityJobMatcher()
    recommendations = matcher.get_smart_recommendations(
        user_profile,
        jobs_df,
        resume_text,
        top_n
    )
    
    return recommendations


def get_job_accessibility_details(job, user_profile):
    """
    Get detailed accessibility information for a job
    """
    matcher = AccessibilityJobMatcher()
    insights = matcher.get_accessibility_insights(job, user_profile)
    
    accessibility_score = matcher.calculate_accessibility_score(job, user_profile)
    
    return {
        'accessibility_score': accessibility_score,
        'insights': insights
    }
