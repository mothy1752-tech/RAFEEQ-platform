from flask import session, redirect, url_for, flash
from functools import wraps
import hashlib
from database import Database

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def register_user(username, email, password, full_name, user_type, disability_data=None):
    """Register a new user with optional disability profile"""
    db = Database()
    conn = db.connect()
    if conn:
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(password)
            
            if disability_data:
                # Registration with disability profile
                cursor.execute('''
                    INSERT INTO users (
                        username, email, password, full_name, user_type,
                        disability_type, disability_description, physical_capabilities,
                        physical_limitations, accessibility_needs, preferred_work_mode,
                        requires_accessible_building, requires_flexible_hours,
                        requires_special_equipment, equipment_details,
                        mobility_assistance_needed, preferred_cities, profile_completed
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    username, email, hashed_password, full_name, user_type,
                    disability_data.get('disability_type'),
                    disability_data.get('disability_description'),
                    disability_data.get('physical_capabilities'),
                    disability_data.get('physical_limitations'),
                    disability_data.get('accessibility_needs'),
                    disability_data.get('preferred_work_mode'),
                    disability_data.get('requires_accessible_building', False),
                    disability_data.get('requires_flexible_hours', False),
                    disability_data.get('requires_special_equipment', False),
                    disability_data.get('equipment_details'),
                    disability_data.get('mobility_assistance_needed', False),
                    disability_data.get('preferred_cities'),
                    True  # profile_completed
                ))
            else:
                # Basic registration
                cursor.execute('''
                    INSERT INTO users (username, email, password, full_name, user_type)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (username, email, hashed_password, full_name, user_type))
            
            conn.commit()
            return True, "Registration successful"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
            conn.close()
    return False, "Database connection failed"

def authenticate_user(username, password):
    """Authenticate user credentials"""
    db = Database()
    conn = db.connect()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            
            if user and verify_password(password, user['password']):
                return True, dict(user)
            return False, None
        except Exception as e:
            return False, None
        finally:
            cursor.close()
            conn.close()
    return False, None

def update_last_login(user_id):
    """Update user's last login timestamp"""
    db = Database()
    conn = db.connect()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s', (user_id,))
            conn.commit()
        except Exception as e:
            # Log error but don't crash
            pass
        finally:
            cursor.close()
            conn.close()
