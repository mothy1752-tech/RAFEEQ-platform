# Utils package initialization
"""
Utils package for RAFEEQ Inclusive Employment Platform
Contains text processing, recommendations, resume analysis, and generation utilities
"""

from .text_processing import (
    extract_pdf_text,
    process_text,
    extract_email,
    extract_phone,
    extract_skills,
    extract_linkedin_profile,
    extract_github_profile,
    SKILL_KEYWORDS
)

from .recommendations import (
    get_job_recommendations,
    get_candidate_recommendations,
    calculate_tfidf_similarity,
    calculate_count_similarity,
    calculate_knn_similarity
)

from .resume_analyzer import (
    analyze_resume,
    get_course_recommendations,
    extract_name,
    extract_experience,
    extract_education,
    detect_field,
    calculate_resume_score,
    generate_recommendations
)

from .resume_generator import (
    generate_candidate_profile,
    generate_multiple_candidates,
    extract_keywords_from_job_description
)



__all__ = [
    # Text processing
    'extract_pdf_text',
    'process_text',
    'extract_email',
    'extract_phone',
    'extract_skills',
    'extract_linkedin_profile',
    'extract_github_profile',
    'SKILL_KEYWORDS',
    
    # Recommendations
    'get_job_recommendations',
    'get_candidate_recommendations',
    'calculate_tfidf_similarity',
    'calculate_count_similarity',
    'calculate_knn_similarity',
    
    # Resume analyzer
    'analyze_resume',
    'get_course_recommendations',
    'extract_name',
    'extract_experience',
    'extract_education',
    'detect_field',
    'calculate_resume_score',
    'generate_recommendations',
    
    # Resume generator
    'generate_candidate_profile',
    'generate_multiple_candidates',
    'extract_keywords_from_job_description',
    
 
]

__version__ = '1.0.0'