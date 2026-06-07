import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

def get_job_recommendations(cv_text, jobs_df, locations=None, top_n=10):
    """Get job recommendations based on CV"""

    # Filter by location if specified
    if locations:
        filtered_jobs = jobs_df[jobs_df['location'].isin(locations)].copy()
    else:
        filtered_jobs = jobs_df.copy()

    if len(filtered_jobs) == 0:
        return pd.DataFrame()

    # Combine job fields for matching
    filtered_jobs['combined_text'] = (
        filtered_jobs['position_name'] + ' ' +
        filtered_jobs['description'] + ' ' +
        filtered_jobs['skills_required']
    )

    # TF-IDF similarity
    tfidf_scores = calculate_tfidf_similarity(
        filtered_jobs['combined_text'].tolist(),
        [cv_text]
    )

    # Count Vectorizer similarity
    count_scores = calculate_count_similarity(
        filtered_jobs['combined_text'].tolist(),
        [cv_text]
    )

    # KNN similarity
    knn_scores = calculate_knn_similarity(
        filtered_jobs['combined_text'].tolist(),
        [cv_text],
        min(100, len(filtered_jobs))
    )

    # Combine scores
    filtered_jobs['tfidf_score'] = tfidf_scores
    filtered_jobs['count_score'] = count_scores
    filtered_jobs['knn_score'] = knn_scores

    # Normalize and combine
    scaler = MinMaxScaler()
    filtered_jobs[['tfidf_norm', 'count_norm', 'knn_norm']] = scaler.fit_transform(
        filtered_jobs[['tfidf_score', 'count_score', 'knn_score']]
    )

    # Weighted average (TF-IDF: 40%, Count: 30%, KNN: 30%)
    filtered_jobs['final_score'] = (
        0.4 * filtered_jobs['tfidf_norm'] +
        0.3 * filtered_jobs['count_norm'] +
        0.3 * filtered_jobs['knn_norm']
    )

    # Sort and return top N
    recommendations = filtered_jobs.nlargest(top_n, 'final_score')

    return recommendations[[
        'job_id', 'company', 'position_name', 'description', 'salary',
        'location', 'rating', 'reviews_count', 'posted_at', 'apply_link',
        'skills_required', 'final_score'
    ]]

def get_candidate_recommendations(job_text, resumes_df, top_n=5):
    """Get top N candidate recommendations for a job description"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Filter out NaN values and empty strings from processed_text
    resumes_df = resumes_df.copy()
    resumes_df['processed_text'] = resumes_df['processed_text'].fillna('').astype(str)
    resumes_df = resumes_df[resumes_df['processed_text'].str.strip() != '']

    if len(resumes_df) == 0:
        return pd.DataFrame()

    # Prepare documents
    documents = [job_text] + resumes_df['processed_text'].tolist()

    # TF-IDF similarity
    tfidf_scores = calculate_tfidf_similarity(
        resumes_df['processed_text'].tolist(),
        [job_text]
    )

    # Count Vectorizer similarity
    count_scores = calculate_count_similarity(
        resumes_df['processed_text'].tolist(),
        [job_text]
    )

    # KNN similarity
    knn_scores = calculate_knn_similarity(
        resumes_df['processed_text'].tolist(),
        [job_text],
        min(20, len(resumes_df))
    )

    # Combine scores
    resumes_df['tfidf_score'] = tfidf_scores
    resumes_df['count_score'] = count_scores
    resumes_df['knn_score'] = knn_scores

    # Normalize and combine
    scaler = MinMaxScaler()
    resumes_df[['tfidf_norm', 'count_norm', 'knn_norm']] = scaler.fit_transform(
        resumes_df[['tfidf_score', 'count_score', 'knn_score']]
    )

    # Weighted average
    resumes_df['match_score'] = (
        0.4 * resumes_df['tfidf_norm'] +
        0.3 * resumes_df['count_norm'] +
        0.3 * resumes_df['knn_norm']
    )

    # Sort and return top N
    recommendations = resumes_df.nlargest(top_n, 'match_score')

    return recommendations[[
        'resume_id', 'name', 'email', 'phone', 'skills', 'experience',
        'education', 'upload_date', 'match_score', 'file_path'
    ]]

def calculate_tfidf_similarity(documents, query):
    """Calculate TF-IDF cosine similarity"""
    vectorizer = TfidfVectorizer(stop_words='english')
    doc_vectors = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform(query)

    similarities = cosine_similarity(query_vector, doc_vectors)[0]
    return similarities

def calculate_count_similarity(documents, query):
    """Calculate Count Vectorizer cosine similarity"""
    vectorizer = CountVectorizer(stop_words='english')
    doc_vectors = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform(query)

    similarities = cosine_similarity(query_vector, doc_vectors)[0]
    return similarities

def calculate_knn_similarity(documents, query, n_neighbors):
    """Calculate KNN similarity scores"""
    vectorizer = TfidfVectorizer(stop_words='english')
    doc_vectors = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform(query)

    # Ensure n_neighbors doesn't exceed number of samples
    n_neighbors = min(n_neighbors, len(documents))

    knn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
    knn.fit(doc_vectors)

    distances, indices = knn.kneighbors(query_vector)

    # Convert distances to similarity scores (1 - distance)
    similarities = np.zeros(len(documents))
    for i, (dist_list, idx_list) in enumerate(zip(distances, indices)):
        for dist, idx in zip(dist_list, idx_list):
            similarities[idx] = 1 - dist

    return similarities