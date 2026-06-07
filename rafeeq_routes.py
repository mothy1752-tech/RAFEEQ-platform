"""
RAFEEQ Platform Additional Routes
Add these routes to app.py before the if __name__ == '__main__': block
"""

import json
from flask import jsonify, request, session, render_template
from utils.ai_resume_generator import generate_ai_resume
from utils.accessibility_matcher import match_jobs_with_accessibility
from utils.transportation_manager import TransportationManager
from utils.career_guidance import get_career_guidance, CareerGuidanceAI
from database import Database
from auth import login_required
import logging

logger = logging.getLogger(__name__)

# ==================== RAFEEQ PLATFORM ENDPOINTS ====================

def register_rafeeq_routes(app, jobs_df):
    """Register all RAFEEQ-specific routes"""
    
    @app.route('/api/generate-ai-resume', methods=['POST'])
    @login_required
    def generate_ai_resume_api():
        """Generate AI-powered disability-friendly resume"""
        try:
            user_id = session['user_id']
            
            # Get user profile
            db = Database()
            conn = db.connect()
            if not conn:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Get form data
            work_history = request.json.get('work_history', [])
            education = request.json.get('education', [])
            skills = request.json.get('skills', [])
            
            # Prepare user profile
            user_profile = {
                'full_name': user['full_name'],
                'email': user['email'],
                'phone': request.json.get('phone', ''),
                'location': request.json.get('location', ''),
                'disability_type': user.get('disability_type'),
                'preferred_work_mode': user.get('preferred_work_mode'),
                'requires_accessible_building': user.get('requires_accessible_building'),
                'requires_flexible_hours': user.get('requires_flexible_hours'),
                'requires_special_equipment': user.get('requires_special_equipment'),
                'equipment_details': user.get('equipment_details'),
                'include_accessibility_statement': request.json.get('include_accessibility_statement', False)
            }
            
            # Generate resume
            resume_result = generate_ai_resume(user_id, user_profile, work_history, education, skills)
            
            # Save to database
            cursor.execute('''
                INSERT INTO resumes (
                    user_id, name, email, phone, skills, experience, education,
                    professional_summary, accessibility_statement, generated_by_ai, processed_text
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s)
            ''', (
                user_id,
                user_profile['full_name'],
                user_profile['email'],
                user_profile['phone'],
                ', '.join(skills),
                str(work_history),
                str(education),
                resume_result['resume_data']['professional_summary'],
                str(resume_result['resume_data'].get('accessibility_statement')),
                resume_result['resume_text']
            ))
            
            resume_id = cursor.lastrowid
            conn.commit()
            
            # Update user resume_generated flag
            cursor.execute('UPDATE users SET resume_generated = TRUE WHERE id = %s', (user_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'resume_id': resume_id,
                'resume_data': resume_result['resume_data'],
                'message': 'Resume generated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in generate_ai_resume_api: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/accessibility-job-match', methods=['POST'])
    @login_required
    def accessibility_job_match():
        """Get accessibility-aware job recommendations"""
        try:
            user_id = session['user_id']
            
            # Get user profile
            db = Database()
            conn = db.connect()
            if not conn:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Prepare user profile
            user_profile = {
                'disability_type': user.get('disability_type'),
                'preferred_work_mode': user.get('preferred_work_mode'),
                'requires_accessible_building': user.get('requires_accessible_building'),
                'requires_flexible_hours': user.get('requires_flexible_hours'),
                'requires_special_equipment': user.get('requires_special_equipment'),
                'mobility_assistance_needed': user.get('mobility_assistance_needed')
            }
            
            # Get resume text if available
            resume_text = request.json.get('resume_text')
            top_n = request.json.get('top_n', 10)
            
            # Get job recommendations
            recommendations = match_jobs_with_accessibility(
                user_profile,
                jobs_df,
                resume_text,
                top_n
            )
            
            if recommendations.empty:
                return jsonify({
                    'success': True,
                    'recommendations': [],
                    'message': 'No matching jobs found with your accessibility requirements'
                })
            
            return jsonify({
                'success': True,
                'recommendations': recommendations.to_dict('records'),
                'total_jobs': len(recommendations)
            })
            
        except Exception as e:
            logger.error(f"Error in accessibility_job_match: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/transportation/book', methods=['POST'])
    @login_required
    def book_transportation():
        """Book accessible transportation"""
        try:
            user_id = session['user_id']
            
            pickup = request.json.get('pickup_location')
            dropoff = request.json.get('dropoff_location')
            pickup_time = request.json.get('pickup_time')
            booking_type = request.json.get('booking_type', 'other')
            
            needs = {
                'city': request.json.get('city'),
                'vehicle_requirements': request.json.get('vehicle_requirements', {}),
                'needs_companion': request.json.get('needs_companion', False),
                'special_requirements': request.json.get('special_requirements', {})
            }
            
            transport_manager = TransportationManager()
            success, result = transport_manager.book_ride(
                user_id, pickup, dropoff, pickup_time, booking_type, needs
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'booking': result,
                    'message': 'Transportation booked successfully'
                })
            else:
                return jsonify({'success': False, 'error': result}), 400
                
        except Exception as e:
            logger.error(f"Error in book_transportation: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/transportation/track/<int:booking_id>')
    @login_required
    def track_transportation(booking_id):
        """Track transportation booking"""
        try:
            transport_manager = TransportationManager()
            tracking_info = transport_manager.track_ride(booking_id)
            
            if tracking_info:
                return jsonify({
                    'success': True,
                    'tracking': tracking_info
                })
            else:
                return jsonify({'success': False, 'error': 'Booking not found'}), 404
                
        except Exception as e:
            logger.error(f"Error in track_transportation: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/transportation/history')
    @login_required
    def transportation_history():
        """Get user's transportation booking history"""
        try:
            user_id = session['user_id']
            transport_manager = TransportationManager()
            bookings = transport_manager.get_user_booking_history(user_id)
            
            return jsonify({
                'success': True,
                'bookings': bookings
            })
            
        except Exception as e:
            logger.error(f"Error in transportation_history: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/career-guidance/<guidance_type>')
    @login_required
    def career_guidance_api(guidance_type):
        """Get career guidance content"""
        try:
            user_id = session['user_id']
            
            # Get user profile
            db = Database()
            conn = db.connect()
            if not conn:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            user_profile = {
                'disability_type': user.get('disability_type', 'general'),
                'skills': user.get('skills', '').split(',') if user.get('skills') else [],
                'interests': []
            }
            
            guidance = get_career_guidance(user_profile, guidance_type)
            
            return jsonify({
                'success': True,
                'guidance': guidance
            })
            
        except Exception as e:
            logger.error(f"Error in career_guidance_api: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/accommodation-template/<template_type>')
    @login_required
    def get_accommodation_template(template_type):
        """Get accommodation request template"""
        try:
            guidance = CareerGuidanceAI()
            template = guidance.generate_accommodation_request_template(template_type)
            
            if template:
                return jsonify({
                    'success': True,
                    'template': template
                })
            else:
                return jsonify({'success': False, 'error': 'Template not found'}), 404
                
        except Exception as e:
            logger.error(f"Error in get_accommodation_template: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/update-disability-profile', methods=['POST'])
    @login_required
    def update_disability_profile():
        """Update user's disability profile"""
        try:
            user_id = session['user_id']
            
            db = Database()
            conn = db.connect()
            if not conn:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Build update query
            update_fields = []
            params = []
            
            if 'disability_type' in request.json:
                update_fields.append('disability_type = %s')
                params.append(request.json['disability_type'])
            
            if 'disability_description' in request.json:
                update_fields.append('disability_description = %s')
                params.append(request.json['disability_description'])
            
            if 'physical_capabilities' in request.json:
                update_fields.append('physical_capabilities = %s')
                params.append(json.dumps(request.json['physical_capabilities']))
            
            if 'physical_limitations' in request.json:
                update_fields.append('physical_limitations = %s')
                params.append(json.dumps(request.json['physical_limitations']))
            
            if 'accessibility_needs' in request.json:
                update_fields.append('accessibility_needs = %s')
                params.append(json.dumps(request.json['accessibility_needs']))
            
            if 'preferred_work_mode' in request.json:
                update_fields.append('preferred_work_mode = %s')
                params.append(request.json['preferred_work_mode'])
            
            if 'requires_accessible_building' in request.json:
                update_fields.append('requires_accessible_building = %s')
                params.append(request.json['requires_accessible_building'])
            
            if 'requires_flexible_hours' in request.json:
                update_fields.append('requires_flexible_hours = %s')
                params.append(request.json['requires_flexible_hours'])
            
            if 'requires_special_equipment' in request.json:
                update_fields.append('requires_special_equipment = %s')
                params.append(request.json['requires_special_equipment'])
            
            if 'equipment_details' in request.json:
                update_fields.append('equipment_details = %s')
                params.append(request.json['equipment_details'])
            
            if 'mobility_assistance_needed' in request.json:
                update_fields.append('mobility_assistance_needed = %s')
                params.append(request.json['mobility_assistance_needed'])
            
            if 'preferred_cities' in request.json:
                update_fields.append('preferred_cities = %s')
                params.append(json.dumps(request.json['preferred_cities']))
            
            if update_fields:
                update_fields.append('profile_completed = TRUE')
                params.append(user_id)
                
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(query, params)
                conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error in update_disability_profile: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/transportation')
    @login_required
    def transportation_page():
        """Transportation booking page"""
        return render_template('transportation.html')

    @app.route('/career-guidance')
    @login_required
    def career_guidance_page():
        """Career guidance page"""
        from flask import session, redirect, url_for
        if session.get('user_type') == 'recruiter':
            return redirect(url_for('recruiter'))
        return render_template('career_guidance.html')

    @app.route('/resume-builder')
    @login_required
    def resume_builder_page():
        """AI Resume Builder page"""
        from flask import session, redirect, url_for
        if session.get('user_type') == 'recruiter':
            return redirect(url_for('recruiter'))
        return render_template('resume_builder.html')
