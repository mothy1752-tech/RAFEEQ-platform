import pymysql
from pymysql import Error
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # إعدادات الاتصال بقاعدة البيانات البعيدة
        # يتم قراءة القيم من Environment Variables (الأفضل للأمان)
        # إذا لم توجد، يتم استخدام القيم الافتراضية الموضحة أدناه
        
        self.host = os.getenv('DB_HOST', '193.203.184.246')
        self.user = os.getenv('DB_USER', 'u864760987_RAFEEQ')
        self.password = os.getenv('DB_PASS', 'Raffek12342#')
        self.port = int(os.getenv('DB_PORT', 3306))
        
        # ملاحظة: في الاستضافات المشتركة، عادة ما يكون اسم قاعدة البيانات مطابقاً لاسم المستخدم
        # أو يبدأ ببادئة مشتركة. تأكد من الاسم الصحيح من لوحة تحكم الاستضافة (cPanel).
        # لقد افترضت هنا أنه مطابق لاسم المستخدم.
        self.database = os.getenv('DB_NAME', 'u864760987_RAFEEQ')
        
        self.connection = None
        
    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            # الاتصال بدون تحديد قاعدة بيانات لمحاولة إنشائها
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            logger.info(f"Database '{self.database}' created or already exists")
            cursor.close()
            conn.close()
            return True
        except Error as e:
            # في الاستضافات المشتركة، غالباً لا يملك المستخدم صلاحية CREATE DATABASE
            # لذا نتجاهل الخطأ إذا كان بسبب الصلاحيات، ونفترض أن القاعدة موجودة
            if "Access denied" in str(e) or "CREATE DATABASE" in str(e):
                logger.warning(f"Could not create database (likely missing permissions): {e}")
                logger.info(f"Assuming database '{self.database}' already exists on the server.")
                return True
            else:
                logger.error(f"Error creating database: {e}")
                raise
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"Successfully connected to database '{self.database}' on host '{self.host}'")
            return self.connection
        except Error as e:
            logger.error(f"Error connecting to database: {e}")
            return None
    
    def create_tables(self):
        """Create all necessary tables for RAFEEQ platform"""
        try:
            # محاولة إنشاء قاعدة البيانات (قد تفشل في الاستضافات المشتركة وهذا طبيعي)
            self.create_database()
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            # لا نوقف البرنامج هنا، لنحاول الاتصال بالقاعدة المفترض وجودها
        
        conn = self.connect()
        if not conn:
            logger.error("Failed to connect to database after creation attempt")
            raise Exception("Cannot connect to database")
        
        try:
            cursor = conn.cursor()
            
            # Step 1: Create base tables without foreign keys first
            
            # Enhanced Users table with disability profile
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    user_type ENUM('candidate', 'recruiter', 'admin') NOT NULL DEFAULT 'candidate',
                    
                    -- Disability-specific fields
                    disability_type ENUM('mobility_wheelchair', 'mobility_crutches', 'mobility_walker', 'limited_mobility', 'other') DEFAULT NULL,
                    disability_description TEXT,
                    physical_capabilities JSON,
                    physical_limitations JSON,
                    accessibility_needs JSON,
                    
                    -- Work preferences
                    preferred_work_mode ENUM('remote', 'onsite', 'hybrid', 'flexible') DEFAULT NULL,
                    requires_accessible_building BOOLEAN DEFAULT FALSE,
                    requires_flexible_hours BOOLEAN DEFAULT FALSE,
                    requires_special_equipment BOOLEAN DEFAULT FALSE,
                    equipment_details TEXT,
                    mobility_assistance_needed BOOLEAN DEFAULT FALSE,
                    preferred_cities JSON,
                    
                    -- Profile completion tracking
                    profile_completed BOOLEAN DEFAULT FALSE,
                    resume_generated BOOLEAN DEFAULT FALSE,
                    
                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Step 2: Create companies table (referenced by jobs)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    company_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    company_name VARCHAR(255) NOT NULL,
                    industry VARCHAR(100),
                    description TEXT,
                    website VARCHAR(255),
                    
                    -- Accessibility profile
                    inclusive_employer_certified BOOLEAN DEFAULT FALSE,
                    accessibility_statement TEXT,
                    building_accessibility_features JSON,
                    disability_hiring_policy TEXT,
                    accommodations_provided JSON,
                    success_stories JSON,
                    
                    -- Ratings
                    accessibility_rating DECIMAL(3,2) DEFAULT 0.00,
                    wheelchair_accessible_rating INT DEFAULT 0,
                    flexible_work_rating INT DEFAULT 0,
                    accommodation_responsiveness INT DEFAULT 0,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            ''')
            
            # Step 3: Create jobs table (referenced by applications)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id INT AUTO_INCREMENT PRIMARY KEY,
                    company_id INT,
                    position_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    requirements TEXT,
                    skills_required TEXT,
                    location VARCHAR(100),
                    salary VARCHAR(100),
                    
                    -- Accessibility features
                    is_remote_available BOOLEAN DEFAULT FALSE,
                    is_hybrid_available BOOLEAN DEFAULT FALSE,
                    flexible_hours BOOLEAN DEFAULT FALSE,
                    wheelchair_accessible BOOLEAN DEFAULT FALSE,
                    has_elevator BOOLEAN DEFAULT FALSE,
                    has_accessible_parking BOOLEAN DEFAULT FALSE,
                    has_accessible_restrooms BOOLEAN DEFAULT FALSE,
                    provides_special_equipment BOOLEAN DEFAULT FALSE,
                    disability_friendly_certified BOOLEAN DEFAULT FALSE,
                    accessibility_features JSON,
                    accommodation_policy TEXT,
                    
                    -- Standard fields
                    posted_at DATE,
                    apply_link VARCHAR(500),
                    rating DECIMAL(3,2) DEFAULT 0.00,
                    is_active BOOLEAN DEFAULT TRUE,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
                )
            ''')
            
            # Step 4: Create resumes table (referenced by applications)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resumes (
                    resume_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    skills TEXT,
                    experience TEXT,
                    education TEXT,
                    
                    -- AI-generated content
                    professional_summary TEXT,
                    accessibility_statement TEXT,
                    generated_by_ai BOOLEAN DEFAULT FALSE,
                    
                    -- Files and processing
                    file_path VARCHAR(255),
                    processed_text LONGTEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Step 5: Create applications table (depends on users, jobs, resumes)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    application_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    job_id INT NOT NULL,
                    resume_id INT,
                    cover_letter TEXT,
                    accommodation_requests TEXT,
                    status ENUM('pending', 'reviewed', 'interview_scheduled', 'rejected', 'accepted') DEFAULT 'pending',
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
                    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE SET NULL
                )
            ''')
            
            # Step 6: Create transportation services table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transportation_services (
                    service_id INT AUTO_INCREMENT PRIMARY KEY,
                    service_name VARCHAR(255) NOT NULL,
                    city VARCHAR(100) NOT NULL,
                    vehicle_type ENUM('wheelchair_van', 'accessible_sedan', 'standard_accessible') NOT NULL,
                    has_wheelchair_lift BOOLEAN DEFAULT FALSE,
                    has_ramp BOOLEAN DEFAULT FALSE,
                    can_accommodate_companion BOOLEAN DEFAULT FALSE,
                    driver_trained BOOLEAN DEFAULT FALSE,
                    contact_phone VARCHAR(20),
                    pricing_per_km DECIMAL(10,2),
                    availability_status ENUM('available', 'busy', 'offline') DEFAULT 'available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Step 7: Create transportation bookings table (depends on users and transportation_services)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transportation_bookings (
                    booking_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    service_id INT NOT NULL,
                    booking_type ENUM('interview', 'work_commute', 'training', 'other') NOT NULL,
                    pickup_location VARCHAR(255) NOT NULL,
                    dropoff_location VARCHAR(255) NOT NULL,
                    pickup_time DATETIME NOT NULL,
                    needs_companion BOOLEAN DEFAULT FALSE,
                    special_requirements TEXT,
                    status ENUM('pending', 'confirmed', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (service_id) REFERENCES transportation_services(service_id) ON DELETE CASCADE
                )
            ''')
            
            # Step 8: Create career guidance content table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS guidance_content (
                    content_id INT AUTO_INCREMENT PRIMARY KEY,
                    content_type ENUM('video', 'article', 'template', 'tip') NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    content LONGTEXT,
                    disability_specific VARCHAR(100),
                    category ENUM('interview', 'workplace', 'rights', 'skills', 'accommodation') NOT NULL,
                    video_url VARCHAR(500),
                    helpful_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Step 9: Create company reviews table (depends on companies and users)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS company_reviews (
                    review_id INT AUTO_INCREMENT PRIMARY KEY,
                    company_id INT NOT NULL,
                    user_id INT NOT NULL,
                    accessibility_rating INT CHECK (accessibility_rating BETWEEN 1 AND 5),
                    accommodation_rating INT CHECK (accommodation_rating BETWEEN 1 AND 5),
                    workplace_culture_rating INT CHECK (workplace_culture_rating BETWEEN 1 AND 5),
                    review_text TEXT,
                    would_recommend BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Step 10: Create job descriptions table (legacy support)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    job_title VARCHAR(200),
                    description LONGTEXT,
                    processed_text LONGTEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("All RAFEEQ tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise
    
    def close(self):
        if self.connection:
            self.connection.close()

# Initialize database on import (Optionally)
# It's better to call create_tables() explicitly in the app startup to control timing
if __name__ == "__main__":
    db = Database()
    print("Creating database and tables...")
    try:
        db.create_tables()
        print("Database setup completed!")
    except Exception as e:
        print(f"An error occurred: {e}")
