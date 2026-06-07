from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash
import pandas as pd
import numpy as np
from datetime import datetime
import os
import io
import base64
import logging
from werkzeug.utils import secure_filename

# Utils Imports (Ensure these files exist in your project structure)
try:
    from utils.text_processing import process_text, extract_pdf_text
    from utils.recommendations import get_job_recommendations, get_candidate_recommendations
    from utils.resume_analyzer import analyze_resume, get_course_recommendations
    from utils.resume_generator import generate_multiple_candidates
    from utils.pdf_generator import create_resume_pdf, generate_resume_buffer
    from utils.ai_resume_generator import generate_ai_resume, DisabilityFriendlyResumeGenerator
    from utils.accessibility_matcher import match_jobs_with_accessibility, get_job_accessibility_details, AccessibilityJobMatcher
    from utils.transportation_manager import TransportationManager
    from utils.career_guidance import get_career_guidance, CareerGuidanceAI
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Missing utility module: {e}")
    # Create dummy functions if imports fail to prevent app crash during build
    pass

from auth import login_required, register_user, authenticate_user, update_last_login
from database import Database

# Import routes if available
try:
    from rafeeq_routes import register_rafeeq_routes
except ImportError:
    register_rafeeq_routes = lambda app, jobs_df: None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_RESUMES_FOLDER'] = 'generated_resumes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# IMPORTANT: Change this secret key in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('data/resumes', exist_ok=True)
os.makedirs('generated_resumes', exist_ok=True)

# Load datasets
jobs_df = pd.DataFrame()
cities_df = pd.DataFrame()

try:
    if os.path.exists('data/saudi_jobs.csv'):
        jobs_df = pd.read_csv('data/saudi_jobs.csv')
    if os.path.exists('data/saudi_cities.csv'):
        cities_df = pd.read_csv('data/saudi_cities.csv')
    logger.info(f"Loaded {len(jobs_df)} jobs and {len(cities_df)} cities")
except Exception as e:
    logger.error(f"Error loading datasets: {e}")

# Initialize resumes CSV if doesn't exist
RESUMES_CSV_PATH = 'data/resumes/resumes_data.csv'
if not os.path.exists(RESUMES_CSV_PATH):
    pd.DataFrame(columns=['resume_id', 'name', 'email', 'phone', 'skills', 'experience', 
                          'education', 'upload_date', 'processed_text', 'file_path']).to_csv(
        RESUMES_CSV_PATH, index=False)

# Database Initialization
# We create the DB instance, but we don't force crash if connection fails yet.
db = Database()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = Database()
    conn = db.connect()
    stats = {
        'total_jobs': len(jobs_df),
        'total_candidates': 0,
        'new_messages': 5,
        'upcoming_interviews': 3
    }
    if conn:
        cursor = conn.cursor()
        try:
            if os.path.exists(RESUMES_CSV_PATH):
                resumes_df = pd.read_csv(RESUMES_CSV_PATH)
                stats['total_candidates'] = len(resumes_df)
        except Exception as e:
            logger.error(f"Error reading resumes CSV: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('dashboard.html', stats=stats)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, user = authenticate_user(username, password)
        
        if success:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            session['full_name'] = user['full_name']
            session['email'] = user.get('email', '')
            update_last_login(user['id'])
            flash('Login successful! Welcome to RAFEEQ.', 'success')
            if user['user_type'] == 'recruiter':
                return redirect(url_for('recruiter'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        user_type = request.form.get('user_type')
        
        success, message = register_user(username, email, password, full_name, user_type)
        
        if success:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Registration failed: {message}', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/candidate')
@login_required
def candidate():
    if session.get('user_type') == 'recruiter':
        flash('This page is for job seekers only.', 'warning')
        return redirect(url_for('recruiter'))
    locations = []
    if not cities_df.empty and 'city_name' in cities_df.columns:
        locations = cities_df['city_name'].unique().tolist()
    return render_template('candidate.html', locations=locations)

@app.route('/recruiter')
@login_required
def recruiter():
    if session.get('user_type') not in ('recruiter', 'admin'):
        flash('This page is for employers only.', 'warning')
        return redirect(url_for('dashboard'))
    return render_template('recruiter.html')

@app.route('/resume-analyzer')
@login_required
def resume_analyzer_page():
    if session.get('user_type') == 'recruiter':
        return redirect(url_for('recruiter'))
    return render_template('resume_analyzer.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        db = Database()
        conn = db.connect()
        if conn:
            cursor = conn.cursor()
            try:
                full_name = request.form.get('full_name')
                email = request.form.get('email')
                cursor.execute('UPDATE users SET full_name = %s, email = %s WHERE id = %s', 
                             (full_name, email, session['user_id']))
                conn.commit()
                session['full_name'] = full_name
                flash('Profile updated successfully!', 'success')
            except Exception as e:
                flash(f'Error updating profile: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()
        return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        db = Database()
        conn = db.connect()
        if conn:
            cursor = conn.cursor()
            try:
                if 'current_password' in request.form:
                    from auth import hash_password, verify_password
                    cursor.execute('SELECT password FROM users WHERE id = %s', (session['user_id'],))
                    user = cursor.fetchone()
                    if user and verify_password(request.form.get('current_password'), user['password']):
                        new_password = hash_password(request.form.get('new_password'))
                        cursor.execute('UPDATE users SET password = %s WHERE id = %s', 
                                     (new_password, session['user_id']))
                        conn.commit()
                        flash('Password updated successfully!', 'success')
                    else:
                        flash('Current password is incorrect!', 'danger')
                else:
                    flash('Settings updated successfully!', 'success')
            except Exception as e:
                flash(f'Error updating settings: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()
        return redirect(url_for('settings'))
    return render_template('settings.html')

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/jobs-map')
@login_required
def jobs_map():
    google_maps_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('jobs_map.html', google_maps_key=google_maps_key)

@app.route('/api/recommend-jobs', methods=['POST'])
def recommend_jobs():
    """API endpoint to get job recommendations based on uploaded resume"""
    try:
        file = request.files.get('resume')
        locations = request.form.getlist('locations[]')
        num_jobs = int(request.form.get('num_jobs', 10))
        
        if not file:
            logger.warning("No file uploaded")
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        try:
            pdf_text = extract_pdf_text(file)
            if not pdf_text or len(pdf_text.strip()) < 50:
                return jsonify({'success': False, 'error': 'Could not extract enough text from PDF. Please ensure the PDF contains readable text.'}), 400
        except ValueError as ve:
            logger.error(f"PDF extraction error: {ve}")
            return jsonify({'success': False, 'error': str(ve)}), 400
        except Exception as e:
            logger.error(f"Unexpected error extracting PDF: {e}")
            return jsonify({'success': False, 'error': 'Failed to process PDF file'}), 500
        
        processed_text = process_text(pdf_text)
        
        if not processed_text:
            return jsonify({'success': False, 'error': 'No meaningful content found in resume'}), 400
        
        recommendations = get_job_recommendations(
            processed_text, 
            jobs_df, 
            locations=locations if locations else None, 
            top_n=num_jobs
        )
        
        if recommendations.empty:
            return jsonify({
                'success': True,
                'recommendations': [],
                'total_jobs': 0,
                'message': 'No matching jobs found. Try adjusting your search criteria.'
            })
        
        return jsonify({
            'success': True,
            'recommendations': recommendations.to_dict('records'),
            'total_jobs': len(recommendations)
        })
    
    except Exception as e:
        logger.error(f"Error in recommend_jobs: {str(e)}")
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/recommend-candidates', methods=['POST'])
def recommend_candidates():
    """API endpoint to get candidate recommendations based on job description"""
    try:
        job_description = request.form.get('job_description')
        num_candidates = int(request.form.get('num_candidates', 5))
        
        if not job_description or not job_description.strip():
            logger.warning("No job description provided")
            return jsonify({'success': False, 'error': 'No job description provided'}), 400
        
        if len(job_description.strip()) < 50:
            return jsonify({'success': False, 'error': 'Job description is too short. Please provide more details.'}), 400
        
        try:
            processed_jd = process_text(job_description)
            if not processed_jd:
                return jsonify({'success': False, 'error': 'Could not process job description'}), 400
        except Exception as e:
            logger.error(f"Error processing job description: {e}")
            return jsonify({'success': False, 'error': 'Failed to process job description'}), 500
        
        try:
            if not os.path.exists(RESUMES_CSV_PATH):
                return jsonify({'success': False, 'error': 'No resumes database found. Please upload resumes first.'}), 404
            
            resumes_df = pd.read_csv(RESUMES_CSV_PATH)
            
            if len(resumes_df) == 0:
                return jsonify({'success': False, 'error': 'No resumes in database. Please upload resumes first.'}), 404
            
            if 'processed_text' not in resumes_df.columns:
                return jsonify({'success': False, 'error': 'Resume database is corrupted. Please re-upload resumes.'}), 500
            
        except Exception as e:
            logger.error(f"Error loading resumes: {e}")
            return jsonify({'success': False, 'error': 'Failed to load resumes database'}), 500
        
        try:
            recommendations = get_candidate_recommendations(
                processed_jd, 
                resumes_df, 
                top_n=num_candidates
            )
            
            if recommendations.empty:
                return jsonify({
                    'success': True,
                    'recommendations': [],
                    'total_candidates': 0,
                    'message': 'No matching candidates found.'
                })
            
            return jsonify({
                'success': True,
                'recommendations': recommendations.to_dict('records'),
                'total_candidates': len(recommendations)
            })
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return jsonify({'success': False, 'error': 'Failed to generate recommendations'}), 500
    
    except ValueError as ve:
        logger.error(f"ValueError in recommend_candidates: {ve}")
        return jsonify({'success': False, 'error': 'Invalid input parameters'}), 400
    except Exception as e:
        logger.error(f"Error in recommend_candidates: {str(e)}")
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/generate-candidates', methods=['POST'])
def generate_candidates():
    """API endpoint to generate AI-powered candidate profiles matching job description"""
    try:
        job_description = request.form.get('job_description')
        num_candidates = int(request.form.get('num_candidates', 5))
        
        if not job_description or not job_description.strip():
            return jsonify({'success': False, 'error': 'No job description provided'}), 400
        
        if len(job_description.strip()) < 50:
            return jsonify({'success': False, 'error': 'Job description is too short. Please provide more details.'}), 400
        
        # Limit number of candidates
        num_candidates = min(num_candidates, 10)
        
        # Generate candidate profiles
        generated_profiles = generate_multiple_candidates(job_description, num_candidates)
        
        # Save generated profiles to database
        resumes_df = pd.read_csv(RESUMES_CSV_PATH)
        
        for profile in generated_profiles:
            # Create PDF for each candidate
            pdf_filename = f"{profile['candidate_id']}.pdf"
            pdf_path = os.path.join(app.config['GENERATED_RESUMES_FOLDER'], pdf_filename)
            
            create_resume_pdf(profile, pdf_path)
            
            # Add to database
            new_resume = {
                'resume_id': len(resumes_df) + 1,
                'name': profile['name'],
                'email': profile['email'],
                'phone': profile['phone'],
                'skills': ', '.join(profile['skills']),
                'experience': f"{profile['experience_years']}+ years",
                'education': profile['education']['degree'],
                'upload_date': datetime.now().isoformat(),
                'processed_text': process_text(profile['resume_text']),
                'file_path': pdf_path
            }
            
            resumes_df = pd.concat([resumes_df, pd.DataFrame([new_resume])], ignore_index=True)
        
        # Save updated database
        resumes_df.to_csv(RESUMES_CSV_PATH, index=False)
        
        # Prepare response data
        candidates_data = []
        for profile in generated_profiles:
            candidates_data.append({
                'candidate_id': profile['candidate_id'],
                'name': profile['name'],
                'email': profile['email'],
                'phone': profile['phone'],
                'skills': ', '.join(profile['skills']),
                'experience': f"{profile['experience_years']}+ years",
                'education': profile['education']['degree'],
                'summary': profile['summary'],
                'match_score': 0.95  # High match score for generated candidates
            })
        
        return jsonify({
            'success': True,
            'generated_candidates': candidates_data,
            'total_generated': len(candidates_data),
            'message': f'Successfully generated {len(candidates_data)} candidate profiles'
        })
    
    except Exception as e:
        logger.error(f"Error in generate_candidates: {str(e)}")
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/download-resume/<candidate_id>')
def download_resume(candidate_id):
    """API endpoint to download candidate resume as PDF"""
    try:
        resumes_df = pd.read_csv(RESUMES_CSV_PATH)
        
        # Find candidate by ID or name
        if candidate_id.startswith('GEN_'):
            # Generated resume
            candidate = resumes_df[resumes_df['file_path'].str.contains(candidate_id, na=False)]
        else:
            # Search by resume_id
            candidate = resumes_df[resumes_df['resume_id'] == int(candidate_id)]
        
        if candidate.empty:
            return jsonify({'success': False, 'error': 'Candidate not found'}), 404
        
        file_path = candidate.iloc[0]['file_path']
        candidate_name = candidate.iloc[0]['name']
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Resume file not found'}), 404
        
        # Prepare filename for download
        safe_name = candidate_name.replace(' ', '_')
        download_name = f"{safe_name}_Resume.pdf"
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        logger.error(f"Error in download_resume: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to download resume'}), 500

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume_api():
    """API endpoint to analyze uploaded resume"""
    new_resume = None
    filepath = None
    
    try:
        file = request.files.get('resume')
        
        if not file:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_filename)
        
        try:
            file.save(filepath)
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return jsonify({'success': False, 'error': 'Failed to save file'}), 500
        
        try:
            pdf_text = extract_pdf_text(filepath)
            
            if not pdf_text or len(pdf_text.strip()) < 50:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'success': False, 'error': 'Could not extract enough text from PDF'}), 400
            
            analysis = analyze_resume(pdf_text)
            
        except ValueError as ve:
            logger.error(f"PDF extraction error: {ve}")
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'error': str(ve)}), 400
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'error': 'Failed to analyze resume'}), 500
        
        courses = get_course_recommendations(analysis.get('detected_field', 'general'))
        
        new_resume = {
            'resume_id': 0,
            'name': analysis.get('name', 'Not detected'),
            'email': analysis.get('email', 'Not detected'),
            'phone': analysis.get('phone', 'Not detected'),
            'skills': ', '.join(analysis.get('skills', [])),
            'experience': analysis.get('experience', 'Not specified'),
            'education': analysis.get('education', 'Not specified'),
            'upload_date': datetime.now().isoformat(),
            'processed_text': process_text(pdf_text),
            'file_path': filepath
        }
        
        try:
            resumes_df = pd.read_csv(RESUMES_CSV_PATH)
            new_resume['resume_id'] = len(resumes_df) + 1
            
            resumes_df = pd.concat([resumes_df, pd.DataFrame([new_resume])], ignore_index=True)
            resumes_df.to_csv(RESUMES_CSV_PATH, index=False)
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'courses': courses,
            'resume_id': new_resume.get('resume_id', 0)
        })
    
    except Exception as e:
        logger.error(f"Error in analyze_resume_api: {str(e)}")
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/stats')
def get_stats():
    """API endpoint to get system statistics"""
    try:
        resumes_df = pd.read_csv(RESUMES_CSV_PATH)
        
        stats = {
            'total_jobs': len(jobs_df),
            'total_resumes': len(resumes_df),
            'locations': cities_df['city_name'].unique().tolist() if not cities_df.empty else [],
            'job_categories': jobs_df['position_name'].value_counts().head(10).to_dict() if not jobs_df.empty else {}
        }
        
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs-map-data')
def get_jobs_map_data():
    """API endpoint to get jobs organized by city for map visualization"""
    try:
        jobs_by_city = []
        
        for _, city in cities_df.iterrows():
            city_jobs = jobs_df[jobs_df['location'] == city['city_name']]
            
            jobs_list = city_jobs[['company', 'position_name', 'salary', 'apply_link']].to_dict('records') if len(city_jobs) > 0 else []
            
            jobs_by_city.append({
                'city': city['city_name'],
                'city_ar': city['city_name_ar'],
                'latitude': float(city['latitude']),
                'longitude': float(city['longitude']),
                'jobs': jobs_list
            })
        
        return jsonify({'jobs_by_city': jobs_by_city})
    
    except Exception as e:
        logger.error(f"Error in get_jobs_map_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-ats-resume', methods=['POST'])
@login_required
def generate_ats_resume():
    """Generate a professional ATS-formatted PDF resume from builder form data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_RIGHT
        import io as _io

        PAGE_W, PAGE_H = A4
        L_MARGIN = 22 * mm
        R_MARGIN = 22 * mm
        CONTENT_W = PAGE_W - L_MARGIN - R_MARGIN

        buffer = _io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=L_MARGIN,
            rightMargin=R_MARGIN,
            topMargin=20 * mm,
            bottomMargin=20 * mm
        )

        story = []
        BLACK = colors.black
        DARK = colors.HexColor('#111111')
        MID = colors.HexColor('#333333')

        name_style = ParagraphStyle('Name', fontSize=28, fontName='Helvetica-Bold',
                                    textColor=BLACK, spaceAfter=4, leading=32)
        contact_style = ParagraphStyle('Contact', fontSize=10, fontName='Helvetica',
                                       textColor=MID, spaceAfter=0, leading=14)
        sec_hdr_style = ParagraphStyle('SecHdr', fontSize=10, fontName='Helvetica-Bold',
                                       textColor=BLACK, spaceBefore=14, spaceAfter=3,
                                       wordWrap='CJK')
        body_style = ParagraphStyle('Body', fontSize=10, fontName='Helvetica',
                                    textColor=MID, spaceAfter=4, leading=15)
        company_style = ParagraphStyle('Company', fontSize=10, fontName='Helvetica-Bold',
                                       textColor=BLACK, spaceAfter=0, leading=14)
        date_style = ParagraphStyle('Date', fontSize=10, fontName='Helvetica-Bold',
                                    textColor=BLACK, alignment=TA_RIGHT, leading=14)
        job_title_style = ParagraphStyle('JobTitle', fontSize=10, fontName='Helvetica-Bold',
                                         textColor=BLACK, spaceAfter=3, leading=14)
        skill_style = ParagraphStyle('Skill', fontSize=10, fontName='Helvetica',
                                     textColor=MID, leading=16)
        edu_bold_style = ParagraphStyle('EduBold', fontSize=10, fontName='Helvetica-Bold',
                                        textColor=BLACK, spaceAfter=1, leading=14)
        edu_sub_style = ParagraphStyle('EduSub', fontSize=10, fontName='Helvetica',
                                       textColor=MID, spaceAfter=7, leading=14)
        col_hdr_style = ParagraphStyle('ColHdr', fontSize=10, fontName='Helvetica-Bold',
                                       textColor=BLACK, spaceAfter=8)

        def sec_header(text):
            return [
                Paragraph(text.upper(), sec_hdr_style),
                HRFlowable(width='100%', thickness=1, color=BLACK, spaceAfter=6)
            ]

        full_name = session.get('full_name') or session.get('username') or 'Candidate Name'

        story.append(Paragraph(full_name, name_style))

        contact_parts = []
        if data.get('phone'):
            contact_parts.append(data['phone'])
        if session.get('email'):
            contact_parts.append(session['email'])
        if data.get('location'):
            contact_parts.append(data['location'])
        if contact_parts:
            story.append(Paragraph(' \u00b7 '.join(contact_parts), contact_style))

        story.append(Spacer(1, 6))
        story.append(HRFlowable(width='100%', thickness=1.5, color=BLACK, spaceAfter=0))
        story.append(Spacer(1, 8))

        if data.get('summary'):
            story.extend(sec_header(data.get('jobTitle', 'Professional Summary') if data.get('jobTitle') else 'Professional Summary'))
            story.append(Paragraph(data['summary'], body_style))
            story.append(Spacer(1, 4))

        skills_raw = data.get('skills', '')
        if skills_raw:
            skills_list = [s.strip() for s in skills_raw.split(',') if s.strip()]
            story.extend(sec_header('Key Competencies'))
            COLS = 3
            rows = []
            row = []
            for skill in skills_list:
                row.append(Paragraph(skill, skill_style))
                if len(row) == COLS:
                    rows.append(row)
                    row = []
            if row:
                while len(row) < COLS:
                    row.append(Paragraph('', skill_style))
                rows.append(row)
            col_w = CONTENT_W / COLS
            skill_tbl = Table(rows, colWidths=[col_w] * COLS)
            skill_tbl.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            story.append(skill_tbl)
            story.append(Spacer(1, 4))

        work_entries = data.get('work', [])
        if work_entries:
            story.extend(sec_header('Professional Experience'))
            for i, job in enumerate(work_entries):
                title = job.get('title', '')
                company = job.get('company', '')
                desc = job.get('desc', '')
                date_range = job.get('dateRange', '')
                if company or title:
                    left_cell = Paragraph(company or title, company_style)
                    right_cell = Paragraph(date_range, date_style) if date_range else Paragraph('', date_style)
                    row_tbl = Table([[left_cell, right_cell]],
                                    colWidths=[CONTENT_W * 0.62, CONTENT_W * 0.38])
                    row_tbl.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    story.append(row_tbl)
                    if company and title:
                        story.append(Paragraph(f'<b>{title}</b>', job_title_style))
                if desc:
                    for line in desc.split('\n'):
                        line = line.strip()
                        if line:
                            story.append(Paragraph(line, body_style))
                if i < len(work_entries) - 1:
                    story.append(Spacer(1, 8))

        education_entries = data.get('education', [])
        has_access = data.get('showAccessibility') and data.get('accessNeeds')

        if education_entries or has_access:
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width='100%', thickness=1, color=BLACK, spaceAfter=8))

            edu_items = [Paragraph('EDUCATION & CERTIFICATIONS', col_hdr_style)]
            for edu in education_entries:
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                year = edu.get('year', '')
                if degree:
                    edu_items.append(Paragraph(f'<b>{degree}</b>', edu_bold_style))
                sub_parts = []
                if institution:
                    sub_parts.append(institution)
                if year:
                    sub_parts.append(year)
                if sub_parts:
                    edu_items.append(Paragraph(', '.join(sub_parts), edu_sub_style))

            right_items = []
            if has_access:
                right_items.append(Paragraph('WORKPLACE ACCOMMODATIONS', col_hdr_style))
                for line in data['accessNeeds'].split('\n'):
                    line = line.strip()
                    if line:
                        right_items.append(Paragraph(line, body_style))

            max_rows = max(len(edu_items), len(right_items), 1)
            while len(edu_items) < max_rows:
                edu_items.append(Paragraph('', body_style))
            while len(right_items) < max_rows:
                right_items.append(Paragraph('', body_style))

            two_col_data = [[edu_items[r], Paragraph('', body_style), right_items[r]]
                            for r in range(max_rows)]
            left_w = CONTENT_W * 0.46
            div_w = 2
            right_w = CONTENT_W - left_w - div_w
            two_col_tbl = Table(two_col_data, colWidths=[left_w, div_w, right_w])
            two_col_tbl.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, -1), 0),
                ('RIGHTPADDING', (0, 0), (0, -1), 10),
                ('LEFTPADDING', (2, 0), (2, -1), 10),
                ('RIGHTPADDING', (2, 0), (2, -1), 0),
                ('LEFTPADDING', (1, 0), (1, -1), 0),
                ('RIGHTPADDING', (1, 0), (1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LINEAFTER', (0, 0), (0, -1), 1, colors.HexColor('#cccccc')),
            ]))
            story.append(two_col_tbl)

        elif education_entries:
            story.extend(sec_header('Education & Certifications'))
            for edu in education_entries:
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                year = edu.get('year', '')
                if degree:
                    story.append(Paragraph(f'<b>{degree}</b>', edu_bold_style))
                sub_parts = []
                if institution:
                    sub_parts.append(institution)
                if year:
                    sub_parts.append(year)
                if sub_parts:
                    story.append(Paragraph(', '.join(sub_parts), edu_sub_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        safe_name = full_name.replace(' ', '_')
        response = send_file(
            _io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=f'{safe_name}_Resume.pdf',
            mimetype='application/pdf'
        )
        return response

    except Exception as e:
        logger.error(f"Error generating ATS resume: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics')
def get_analytics():
    """API endpoint to get analytics data for dashboard"""
    try:
        jobs_by_city = jobs_df['location'].value_counts().to_dict() if not jobs_df.empty else {}
        
        top_categories = jobs_df['position_name'].str.split().str[-2:].str.join(' ').value_counts().head(10).to_dict() if not jobs_df.empty else {}
        
        salary_ranges = {
            '15k-20k SAR': len(jobs_df[jobs_df['salary'].str.contains('1[5-9]000|20000', na=False)]) if not jobs_df.empty else 0,
            '20k-25k SAR': len(jobs_df[jobs_df['salary'].str.contains('2[0-4]000|25000', na=False)]) if not jobs_df.empty else 0,
            '25k-30k SAR': len(jobs_df[jobs_df['salary'].str.contains('2[5-9]000|30000', na=False)]) if not jobs_df.empty else 0,
            '30k-40k SAR': len(jobs_df[jobs_df['salary'].str.contains('3[0-9]000|40000', na=False)]) if not jobs_df.empty else 0,
            '40k+ SAR': len(jobs_df[jobs_df['salary'].str.contains('4[0-9]000|50000', na=False)]) if not jobs_df.empty else 0
        }
        
        ratings_dist = {
            '4.5-5.0': len(jobs_df[(jobs_df['rating'] >= 4.5) & (jobs_df['rating'] <= 5.0)]) if not jobs_df.empty else 0,
            '4.0-4.4': len(jobs_df[(jobs_df['rating'] >= 4.0) & (jobs_df['rating'] < 4.5)]) if not jobs_df.empty else 0,
            '3.5-3.9': len(jobs_df[(jobs_df['rating'] >= 3.5) & (jobs_df['rating'] < 4.0)]) if not jobs_df.empty else 0,
            '3.0-3.4': len(jobs_df[(jobs_df['rating'] >= 3.0) & (jobs_df['rating'] < 3.5)]) if not jobs_df.empty else 0,
            'Below 3.0': len(jobs_df[jobs_df['rating'] < 3.0]) if not jobs_df.empty else 0
        }
        
        all_skills = ' '.join(jobs_df['skills_required']) if not jobs_df.empty else ''
        skill_counts = pd.Series(all_skills.split()).value_counts().head(15).to_dict() if all_skills else {}
        
        timeline = jobs_df['posted_at'].value_counts().sort_index().head(10).to_dict() if not jobs_df.empty else {}
        
        analytics = {
            'jobs_by_city': jobs_by_city,
            'top_categories': top_categories,
            'salary_ranges': salary_ranges,
            'ratings_distribution': ratings_dist,
            'top_skills': skill_counts,
            'posting_timeline': timeline
        }
        
        return jsonify(analytics)
    
    except Exception as e:
        logger.error(f"Error in get_analytics: {e}")
        return jsonify({'error': str(e)}), 500

# Register RAFEEQ routes
try:
    from rafeeq_routes import register_rafeeq_routes
    register_rafeeq_routes(app, jobs_df)
except ImportError:
    pass

# Initialize DB at startup (Runs on both Local and Render)
# We do this here so it runs every time the app starts, ensuring tables exist.
logger.info("Attempting to initialize database...")
try:
    db.create_tables()
    logger.info("Database 'RAFEEQ' and tables initialized successfully")
except Exception as e:
    # If DB fails (e.g., IP not whitelisted yet), log error but don't crash the app
    logger.error(f"Database initialization failed: {e}")
    logger.error("App will start, but Login/Register features will not work until DB is accessible.")

if __name__ == '__main__':
    logger.info("Starting RAFEEQ Inclusive Employment Platform locally...")
    # Note: Tables are already initialized above, so we don't need to call it here again.
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
