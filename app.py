"""
==============================================================================
UPSC CANDIDATE MANAGEMENT SYSTEM - ENTERPRISE CLOUD EDITION
==============================================================================
Designed for: CBSE Class 12 Computer Science Project (Practical Submission)
Target Environment: Vercel Cloud Hosting & Local XAMPP Testing
Database Backend: MySQL (sql12.freesqldatabase.com)

FEATURES INCLUDED IN THIS BUILD:
1. Public & Secure Admin Routing (Role-Based Access Control)
2. Advanced Aggregate SQL Queries (GROUP BY, COUNT)
3. CSV Data Export (Python File Handling Concept)
4. Dynamic Search Engine (SQL LIKE Clause)
5. Server-side Validation with Regex
6. Custom Error Handling (404, 500 pages)
7. System Logging
8. Automated Dummy Data Seeding
==============================================================================
"""

import os
import csv
import io
import re
import logging
from datetime import datetime
from flask import Flask, request, session, redirect, url_for, make_response
import mysql.connector

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Setup standard logging to track errors and admin actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================
app = Flask(__name__)
# Cryptographic key required for secure Admin sessions
app.secret_key = 'upsc_super_secure_enterprise_key_2026_v2_ultimate'

# ============================================================================
# CLOUD MYSQL DATABASE CONFIGURATION
# ============================================================================
# ACTION REQUIRED: Replace these with your freesqldatabase.com credentials
DB_HOST = "sql12.freesqldatabase.com"
DB_PORT = 3306                     
DB_USER = "	sql12830941"      # e.g., sql12715xxx
DB_PASSWORD = "dWeYdFy5kw"  # e.g., aBcDeFg
DB_NAME = "sql12830941"          # e.g., sql12715xxx

# ============================================================================
# HARDCODED ADMIN CREDENTIALS
# ============================================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "UpscAdmin2026"

# ============================================================================
# DATABASE CONNECTION & SETUP FUNCTIONS
# ============================================================================

def get_db_connection():
    """
    Establishes a connection to the remote MySQL database.
    CBSE Concept: Database Connectivity using mysql.connector
    """
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
        logger.error(f"Database Connection Failed: {err}")
        raise

def initialize_database():
    """
    Creates the necessary tables if they do not exist.
    CBSE Concept: DDL (Data Definition Language) - CREATE TABLE
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS candidates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            registration_no VARCHAR(15) UNIQUE NOT NULL,
            name VARCHAR(50) NOT NULL,
            dob DATE NOT NULL,
            gender VARCHAR(10) NOT NULL,
            category VARCHAR(20) NOT NULL,
            exam_center VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Remote Cloud MySQL Database verified and ready.")
    except Exception as err:
        logger.critical(f"Failed to initialize database: {err}")

# ============================================================================
# SERVER-SIDE VALIDATION MODULE
# ============================================================================

def validate_data(reg_no, name, dob_str, gender, category, exam_center):
    """
    Strict validation to ensure database integrity and prevent SQL issues.
    Returns: (Boolean status, String error message)
    """
    if not reg_no or len(reg_no) < 5 or not reg_no.isalnum():
        return False, "Registration number must be 5-15 alphanumeric characters."
    
    if not name or not re.match("^[a-zA-Z\s]+$", name) or len(name) < 3:
        return False, "Name must contain only letters and spaces (min 3 chars)."
    
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
        age_in_years = (datetime.now() - dob).days / 365.25
        if age_in_years < 18:
            return False, "Candidate must be at least 18 years old to register."
        if age_in_years > 32: # UPSC General Age Limit rule
            return False, "Candidate exceeds the maximum age limit of 32 years."
    except ValueError:
        return False, "Invalid Date Format provided."
        
    if gender not in ['Male', 'Female', 'Other']:
        return False, "Invalid Gender Selection."
        
    if category not in ['General', 'OBC', 'SC', 'ST', 'EWS']:
        return False, "Invalid Category Selection."
        
    if not exam_center or len(exam_center) < 3:
        return False, "Exam Center must be at least 3 characters."
        
    return True, ""

# ============================================================================
# MASTER UI TEMPLATE ENGINE (CSS & HTML INJECTION)
# ============================================================================

GLOBAL_CSS = """
    /* CSS Reset and Base Styles */
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    body { background: #f4f7f6; color: #2d3436; min-height: 100vh; display: flex; flex-direction: column; }
    
    /* Navigation Bar */
    .navbar { background: #1e272e; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); position: sticky; top: 0; z-index: 100; }
    .nav-brand { font-size: 1.6em; font-weight: bold; display: flex; align-items: center; gap: 12px; letter-spacing: 1px; }
    .nav-links { display: flex; gap: 20px; align-items: center; }
    .nav-links a { color: #d2dae2; text-decoration: none; padding: 10px 18px; border-radius: 4px; font-weight: 600; transition: all 0.3s ease; }
    .nav-links a:hover { background: #485460; color: white; transform: translateY(-2px); }
    .nav-links a.active { background: #0fb9b1; color: white; }
    .nav-links a.admin-btn { background: #ff3f34; color: white; box-shadow: 0 2px 5px rgba(255,63,52,0.4); }
    .nav-links a.admin-btn:hover { background: #ff5e57; box-shadow: 0 4px 8px rgba(255,63,52,0.6); }

    /* Layout Containers */
    .main-container { flex: 1; max-width: 1250px; margin: 40px auto; width: 100%; padding: 0 20px; }
    .card { background: white; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); padding: 35px; margin-bottom: 30px; border-top: 5px solid #0fb9b1; }
    .card.admin-card { border-top: 5px solid #ff3f34; }
    
    /* Typography */
    h1, h2, h3 { color: #1e272e; margin-bottom: 18px; font-weight: 700; }
    p { line-height: 1.7; color: #485460; margin-bottom: 15px; font-size: 1.05em; }
    hr { border: 0; border-top: 1px solid #d2dae2; margin: 25px 0; }
    
    /* Data Tables */
    .table-container { overflow-x: auto; background: white; border-radius: 8px; border: 1px solid #d2dae2; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 16px; text-align: left; border-bottom: 1px solid #d2dae2; }
    th { background: #f8f9fa; color: #1e272e; font-weight: 700; text-transform: uppercase; font-size: 0.85em; letter-spacing: 0.05em; }
    tr:last-child td { border-bottom: none; }
    tr:hover { background: #f1f2f6; }
    
    /* Button Framework */
    .btn { display: inline-flex; align-items: center; justify-content: center; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 0.95em; font-weight: 600; transition: all 0.2s; gap: 8px; }
    .btn-primary { background: #0fb9b1; color: white; }
    .btn-primary:hover { background: #0ca19a; }
    .btn-danger { background: #ff3f34; color: white; }
    .btn-danger:hover { background: #ff5e57; }
    .btn-success { background: #0be881; color: white; }
    .btn-success:hover { background: #05c46b; }
    .btn-dark { background: #1e272e; color: white; }
    .btn-dark:hover { background: #485460; }
    .btn-outline { background: transparent; border: 2px solid #0fb9b1; color: #0fb9b1; }
    .btn-outline:hover { background: #0fb9b1; color: white; }
    
    /* Form Elements */
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    .form-group { display: flex; flex-direction: column; }
    .form-group.full-width { grid-column: span 2; }
    label { font-weight: 700; margin-bottom: 8px; color: #1e272e; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px; }
    input, select, textarea { padding: 14px; border: 2px solid #d2dae2; border-radius: 6px; font-size: 1em; transition: all 0.3s ease; background: #f8f9fa; }
    input:focus, select:focus, textarea:focus { outline: none; border-color: #0fb9b1; background: white; box-shadow: 0 0 0 4px rgba(15, 185, 177, 0.15); }
    
    /* Search Bar Specific */
    .search-box { display: flex; gap: 10px; margin-bottom: 25px; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #d2dae2; }
    .search-box input { flex: 1; border-color: transparent; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .search-box input:focus { border-color: #0fb9b1; }

    /* Alert Banners & Badges */
    .flash { padding: 16px 20px; border-radius: 8px; margin-bottom: 25px; font-weight: 600; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .flash.error { background: #fff0f0; border-left: 5px solid #ff3f34; color: #ff3f34; }
    .flash.success { background: #f0fff4; border-left: 5px solid #0be881; color: #05c46b; }
    .badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 700; display: inline-block; }
    .badge-admin { background: #ff3f34; color: white; box-shadow: 0 0 10px rgba(255,63,52,0.5); }
    .badge-info { background: #d2dae2; color: #1e272e; }

    /* Admin Dashboard Analytics Cards */
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 25px; margin-bottom: 35px; }
    .stat-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.08); position: relative; overflow: hidden; border: 1px solid #d2dae2; }
    .stat-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: #0fb9b1; }
    .stat-card.admin-stat::before { background: #ff3f34; }
    .stat-title { font-size: 0.9em; color: #485460; text-transform: uppercase; font-weight: 800; margin-bottom: 10px; letter-spacing: 1px; }
    .stat-value { font-size: 2.5em; font-weight: 800; color: #1e272e; line-height: 1; }

    /* Footer */
    footer { background: #1e272e; color: #808e9b; text-align: center; padding: 30px; margin-top: auto; font-size: 0.95em; border-top: 4px solid #0fb9b1; }
    footer strong { color: white; }
        /* =======================================================
       MOBILE RESPONSIVENESS (Android / iOS Optimization)
       ======================================================= */
    @media (max-width: 768px) {
        /* Stack the navigation bar */
        .navbar { flex-direction: column; padding: 15px; gap: 15px; text-align: center; }
        .nav-links { flex-wrap: wrap; justify-content: center; gap: 10px; }
        .nav-links a { padding: 8px 12px; font-size: 0.9em; width: 48%; text-align: center; }
        .nav-links a.admin-btn { width: 100%; }
        
        /* Make form fields stack vertically instead of side-by-side */
        .form-grid { grid-template-columns: 1fr; gap: 15px; }
        .form-group.full-width { grid-column: span 1; }
        
        /* Adjust card padding for small screens */
        .card { padding: 20px; margin-bottom: 20px; }
        
        /* Adjust text sizes */
        h1 { font-size: 1.8em; }
        h2 { font-size: 1.5em; }
        
        /* Make buttons stretch full width */
        .btn { width: 100%; display: block; margin-bottom: 10px; }
        
        /* Stack the search bar */
        .search-box { flex-direction: column; padding: 15px; }
        
        /* Ensure table doesn't break the screen width */
        .table-container { overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 6px; }
        th, td { padding: 10px; font-size: 0.85em; }
    }
    
"""

def render_page(title, content, active_page="dashboard"):
    """
    Main HTML structural generator. Dynamically builds the navigation menu
    based on whether the user has an active admin session.
    """
    is_admin = session.get('is_admin', False)
    
    # Generate contextual navigation links
    nav_links = f"""
        <a href="/" class="{'active' if active_page == 'dashboard' else ''}">🏠 Home Registry</a>
        <a href="/about" class="{'active' if active_page == 'about' else ''}">ℹ️ About Us</a>
        <a href="/contact" class="{'active' if active_page == 'contact' else ''}">📞 Contact</a>
        <a href="/register" class="{'active' if active_page == 'register' else ''}">➕ Apply Now</a>
    """
    
    admin_btn = f"""
        <a href="/admin" class="{'active' if active_page == 'admin' else ''} btn-dark" style="margin-right:10px;">⚙️ Admin Panel</a>
        <a href="/logout" class="admin-btn">🔒 Logout</a>
    """ if is_admin else """
        <a href="/login" class="admin-btn">🔑 Admin Login</a>
    """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - UPSC Portal</title>
        <style>{GLOBAL_CSS}</style>
    </head>
    <body>
        <nav class="navbar">
            <div class="nav-brand">
                🏛️ UPSC Central
                {f'<span class="badge badge-admin">ADMINISTRATOR</span>' if is_admin else ''}
            </div>
            <div class="nav-links">
                {nav_links}
                {admin_btn}
            </div>
        </nav>
        <div class="main-container">
            {content}
        </div>
        <footer>
            <p><strong>UPSC Candidate Management System</strong> 12th project </p>
            <p>Developed by 12 CBSE </p>
            <p style="margin-top: 10px; font-size: 0.85em;">SIMPLE CODEC </p>
        </footer>
    </body>
    </html>
    """

# ============================================================================
# PUBLIC INTERFACE ROUTES
# ============================================================================

@app.route('/')
def index():
    """
    Landing page. Shows a summarized list of candidates.
    Demonstrates basic SELECT queries and HTML table generation.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, registration_no, name, category, exam_center FROM candidates ORDER BY id DESC LIMIT 50")
        candidates = cursor.fetchall()
        cursor.close()
        conn.close()

        if not candidates:
            html = """
            <div class="card" style="text-align: center; padding: 60px 20px;">
                <h2 style="font-size: 2em; color: #485460;">📭 Database is Empty</h2>
                <p>No candidates have registered for the upcoming examinations yet.</p>
                <div style="margin-top: 30px;">
                    <a href="/register" class="btn btn-primary" style="font-size: 1.2em; padding: 15px 30px;">Be the First to Register</a>
                </div>
            </div>
            """
            return render_page("Public Registry", html, "dashboard")

        rows = ""
        for c in candidates:
            rows += f"""
            <tr>
                <td><span class="badge badge-info">{c[1]}</span></td>
                <td style="font-weight: 600;">{c[2]}</td>
                <td>{c[3]}</td>
                <td>{c[4]}</td>
                <td><a href="/view/{c[0]}" class="btn btn-outline" style="padding: 6px 12px; font-size: 0.85em;">View Profile</a></td>
            </tr>
            """
        
        html = f"""
        <div class="card">
            <h2>📋 Public Candidate Registry (Top 50)</h2>
            <p>Welcome to the official UPSC registration tracking portal. Select a profile to verify application status.</p>
            <div class="table-container" style="margin-top: 20px;">
                <table>
                    <tr><th>Registration Number</th><th>Candidate Name</th><th>Category</th><th>Exam Center</th><th>Action</th></tr>
                    {rows}
                </table>
            </div>
        </div>
        """
        return render_page("Home", html, "dashboard")
        
    except Exception as e:
        logger.error(f"Index Page Error: {e}")
        return render_page("Error", f"<div class='flash error'>System Error: Database connection timeout. Please try again later.</div>", "dashboard")

@app.route('/view/<int:c_id>')
def view_profile(c_id):
    """
    Displays a detailed "Admit Card" style view for a single candidate.
    Demonstrates SQL SELECT with WHERE parameter.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates WHERE id = %s", (c_id,))
        c = cursor.fetchone()
        cursor.close()
        conn.close()

        if not c:
            return render_page("Not Found", "<div class='flash error'>Candidate Profile Not Found.</div>", "dashboard")

        reg_date = c[7].strftime("%d %B %Y, %I:%M %p") if c[7] else "N/A"

        html = f"""
        <div class="card" style="max-width: 800px; margin: 0 auto; border-top: 5px solid #1e272e;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px;">
                <div>
                    <h2 style="margin-bottom: 5px;">{c[2]}</h2>
                    <p style="color: #0fb9b1; font-weight: bold; font-size: 1.2em; margin: 0;">{c[1]}</p>
                </div>
                <div style="text-align: right;">
                    <span class="badge badge-info" style="font-size: 1em;">Status: VERIFIED</span>
                    <p style="font-size: 0.85em; margin-top: 10px;">Applied: {reg_date}</p>
                </div>
            </div>
            
            <hr>
            
            <div class="form-grid">
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <label style="color: #808e9b;">Date of Birth</label>
                    <p style="font-size: 1.2em; font-weight: 600; margin: 0;">{c[3]}</p>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <label style="color: #808e9b;">Gender</label>
                    <p style="font-size: 1.2em; font-weight: 600; margin: 0;">{c[4]}</p>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <label style="color: #808e9b;">Applicant Category</label>
                    <p style="font-size: 1.2em; font-weight: 600; margin: 0;">{c[5]}</p>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <label style="color: #808e9b;">Assigned Examination Center</label>
                    <p style="font-size: 1.2em; font-weight: 600; margin: 0;">{c[6]}</p>
                </div>
            </div>
            
            <div style="margin-top: 40px; text-align: center;">
                <a href="/" class="btn btn-dark">← Return to Registry</a>
            </div>
        </div>
        """
        return render_page(f"Profile - {c[1]}", html, "dashboard")
    except Exception as e:
        return render_page("Error", f"<div class='flash error'>Error loading profile.</div>", "dashboard")

@app.route('/about')
def about():
    """Static Information Page."""
    html = """
    <div class="card">
        <div style="text-align: center; margin-bottom: 40px;">
            <h1 style="font-size: 2.5em;">About the Project</h1>
            <p style="font-size: 1.2em; max-width: 800px; margin: 0 auto;">A modern, full-stack database management system engineered for educational demonstration.</p>
        </div>
        
        <div class="form-grid">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 12px; border: 1px solid #d2dae2;">
                <h3 style="color: #0fb9b1;">System Architecture</h3>
                <ul style="list-style-position: inside; line-height: 2;">
                    <li><strong>Frontend UI:</strong> Responsive Grid</li>
                    <li><strong>Backend Logic:</strong> Python 3.10+</li>
                    <li><strong>Data Layer:</strong> MySQL 8.0 via mysql-connector-python</li>
                    <li><strong>Hosting:</strong> Vercel Serverless Architecture</li>
                </ul>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 12px; border: 1px solid #d2dae2;">
                <h3 style="color: #ff3f34;">Security Implementations</h3>
                <ul style="list-style-position: inside; line-height: 2;">
                    <li>SQL Injection Prevention (Parameterized Queries)</li>
                    <li>Cryptographically Signed Session Cookies</li>
                    <li>Role-Based Access Control (RBAC)</li>
                    <li>Server-Side Data Sanitization</li>
                </ul>
            </div>
        </div>
    </div>
    """
    return render_page("About", html, "about")

@app.route('/contact')
def contact():
    """Static Contact/Support Page."""
    html = """
    <div class="card" style="max-width: 700px; margin: 0 auto; text-align: center;">
        <h2>📞 Examination Support Center</h2>
        <p>For technical difficulties with the registration portal, please contact the administrators below.</p>
        <hr>
        <div style="margin: 30px 0;">
            <h3 style="color: #0fb9b1;">Central Helpline</h3>
            <p style="font-size: 1.5em; font-weight: bold;">1800-UPSC-HELP</p>
            <p>Available Mon-Fri, 9:00 AM to 6:00 PM</p>
        </div>
        <div style="margin: 30px 0;">
            <h3 style="color: #0fb9b1;">Email Support</h3>
            <p style="font-size: 1.2em;">support@upsc-portal-demo.org</p>
        </div>
        <div class="flash success" style="justify-content: center;">
            Response time is currently under 24 hours.
        </div>
    </div>
    """
    return render_page("Contact Support", html, "contact")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user input, validation, and database insertion.
    CBSE Concept: HTML Forms, Python POST processing, SQL INSERT.
    """
    if request.method == 'GET':
        html = """
        <div class="card" style="max-width: 900px; margin: 0 auto;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #0fb9b1;">Candidate Registration</h1>
                <p>Ensure all details match your official documentation before submitting.</p>
            </div>
            
            <form method="POST">
                <div class="form-grid">
                    <div class="form-group full-width">
                        <label>Registration Number (Unique ID)</label>
                        <input type="text" name="reg_no" placeholder="e.g., UPSC2026101" required maxlength="15">
                        <small style="color: #808e9b; margin-top: 5px;">Alphanumeric only. Minimum 5 characters.</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Full Legal Name</label>
                        <input type="text" name="name" placeholder="As per Class 10 Certificate" required maxlength="50">
                    </div>
                    
                    <div class="form-group">
                        <label>Date of Birth</label>
                        <input type="date" name="dob" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Gender</label>
                        <select name="gender" required>
                            <option value="">-- Select --</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Applicant Category</label>
                        <select name="category" required>
                            <option value="">-- Select --</option>
                            <option value="General">General (UR)</option>
                            <option value="OBC">OBC</option>
                            <option value="SC">SC</option>
                            <option value="ST">ST</option>
                            <option value="EWS">Economically Weaker Section</option>
                        </select>
                    </div>
                    
                    <div class="form-group full-width">
                        <label>Preferred Examination Center City</label>
                        <input type="text" name="exam_center" placeholder="e.g., Hyderabad, Delhi, Mumbai" required maxlength="100">
                    </div>
                </div>
                
                <hr>
                <div style="display: flex; gap: 15px;">
                    <button type="submit" class="btn btn-primary" style="flex: 2; padding: 16px; font-size: 1.1em;">Final Submit & Register</button>
                    <button type="reset" class="btn btn-outline" style="flex: 1;">Clear Form</button>
                </div>
            </form>
        </div>
        """
        return render_page("Apply Online", html, "register")

    # Data Extraction
    reg_no = request.form.get('reg_no', '').strip()
    name = request.form.get('name', '').strip()
    dob = request.form.get('dob', '').strip()
    gender = request.form.get('gender', '')
    category = request.form.get('category', '')
    exam_center = request.form.get('exam_center', '').strip()

    # Validation
    is_valid, error_msg = validate_data(reg_no, name, dob, gender, category, exam_center)
    if not is_valid:
        logger.warning(f"Failed registration attempt: {error_msg}")
        err_html = f"<div class='card' style='max-width: 600px; margin: 0 auto;'><div class='flash error'>Validation Error: {error_msg}</div><a href='/register' class='btn btn-primary'>← Retry</a></div>"
        return render_page("Error", err_html, "register")

    # Database Operation
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO candidates (registration_no, name, dob, gender, category, exam_center) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (reg_no, name, dob, gender, category, exam_center))
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"New Candidate Registered: {reg_no} - {name}")
        
        success_html = f"""
        <div class="card" style="max-width: 600px; margin: 0 auto; text-align: center; border-top: 5px solid #0be881;">
            <div style="font-size: 4em; margin-bottom: 20px;">✅</div>
            <h2>Registration Successful!</h2>
            <p>Congratulations, <strong>{name}</strong>. Your application has been recorded in the central database.</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0; color: #808e9b;">Your Application Registration Number:</p>
                <h3 style="font-size: 2em; color: #1e272e; margin-top: 5px; letter-spacing: 2px;">{reg_no}</h3>
                <p style="margin-top: 10px; font-size: 0.85em; color: #ff3f34;">Please save this number for future reference.</p>
            </div>
            <a href="/view/{cursor.lastrowid}" class="btn btn-primary">View Full Profile</a>
        </div>
        """
        return render_page("Success", success_html, "register")
        
    except mysql.connector.IntegrityError:
        err = "<div class='flash error'>FATAL: This Registration Number is already active in the system.</div>"
        return render_page("Error", "<div class='card'>" + err + "<a href='/register' class='btn btn-primary'>Back</a></div>", "register")
    except Exception as e:
        logger.error(f"Database Insert Error: {e}")
        return render_page("Error", f"<div class='card'><div class='flash error'>Database Fault. Try again.</div></div>", "register")

# ============================================================================
# SECURITY & AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin Login Portal using Flask Sessions"""
    if request.method == 'GET':
        html = """
        <div class="card" style="max-width: 450px; margin: 50px auto; border-top: 5px solid #1e272e;">
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="font-size: 3em; margin-bottom: 10px;">🔐</div>
                <h2 style="color: #1e272e;">System Login</h2>
                <p style="font-size: 0.9em;">Restricted Access Portal</p>
            </div>
            <form method="POST">
                <div class="form-group" style="margin-bottom: 20px;">
                    <label>Administrator ID</label>
                    <input type="text" name="username" required autocomplete="off">
                </div>
                <div class="form-group" style="margin-bottom: 30px;">
                    <label>Security Passcode</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-dark" style="width: 100%; padding: 14px; font-size: 1.1em;">Authenticate Session</button>
            </form>
        </div>
        """
        return render_page("Admin Login", html, "admin")

    username = request.form['username'].strip()
    password = request.form['password'].strip()

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['is_admin'] = True
        logger.info("Admin successfully logged into the system.")
        return redirect(url_for('admin_dashboard'))
    else:
        logger.warning(f"Failed login attempt with username: {username}")
        err = "<div class='flash error'>Authentication Failed. Threat logged.</div>"
        return render_page("Login Failed", f"<div class='card' style='max-width:450px;margin:50px auto;'>{err}<a href='/login' class='btn btn-dark'>Retry</a></div>", "admin")

@app.route('/logout')
def logout():
    """Terminate admin session"""
    session.pop('is_admin', None)
    logger.info("Admin logged out.")
    return redirect(url_for('index'))

# ============================================================================
# PROTECTED ADMIN DASHBOARD ROUTES
# ============================================================================

@app.route('/admin')
def admin_dashboard():
    """
    Main Control Panel. Requires active session.
    Features search forms, data grids, and aggregate statistics.
    """
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    # Get optional search query from URL parameter
    search_query = request.args.get('search', '').strip()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Aggregate Analytics (Always calculated on full DB)
        cursor.execute("SELECT COUNT(*) FROM candidates")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT category, COUNT(*) FROM candidates GROUP BY category")
        cat_stats = dict(cursor.fetchall())
        general_count = cat_stats.get('General', 0)
        reserved_count = sum(v for k, v in cat_stats.items() if k != 'General')

        # Conditional Logic for Search Engine Implementation
        if search_query:
            # SQL LIKE clause for searching
            query = "SELECT * FROM candidates WHERE name LIKE %s OR registration_no LIKE %s ORDER BY id DESC"
            search_param = f"%{search_query}%"
            cursor.execute(query, (search_param, search_param))
        else:
            cursor.execute("SELECT * FROM candidates ORDER BY id DESC")
            
        candidates = cursor.fetchall()
        cursor.close()
        conn.close()

        # Build dynamic table rows
        rows = ""
        for c in candidates:
            rows += f"""
            <tr>
                <td>{c[0]}</td>
                <td><span class="badge badge-info">{c[1]}</span></td>
                <td><strong>{c[2]}</strong></td>
                <td>{c[6]}</td>
                <td>
                    <div style="display:flex; gap:5px;">
                        <a href="/edit/{c[0]}" class="btn btn-primary" style="padding: 6px 12px; font-size: 0.8em;">Edit</a>
                        <a href="/delete/{c[0]}" class="btn btn-danger" style="padding: 6px 12px; font-size: 0.8em;" onclick="return confirm('WARNING: Irreversible action. Delete {c[1]}?');">Del</a>
                    </div>
                </td>
            </tr>
            """
            
        html = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
            <h1 style="color: #1e272e; margin: 0;">⚙️ System Administration Console</h1>
            <div>
                <a href="/seed" class="btn btn-outline" style="margin-right: 10px;" onclick="return confirm('Generate dummy data?');">🧪 Inject Test Data</a>
                <a href="/export" class="btn btn-success">📥 Export Data (CSV)</a>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card admin-stat">
                <div class="stat-title">Total Active Records</div>
                <div class="stat-value">{total_count}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">General Category</div>
                <div class="stat-value" style="color: #0fb9b1;">{general_count}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Reserved Categories</div>
                <div class="stat-value" style="color: #ff3f34;">{reserved_count}</div>
            </div>
        </div>
        
        <div class="card admin-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0;">Database Management</h2>
            </div>
            
            <form method="GET" action="/admin" class="search-box">
                <input type="text" name="search" placeholder="Search by Registration No or Candidate Name..." value="{search_query}" style="font-size: 1.1em;">
                <button type="submit" class="btn btn-dark" style="padding: 0 30px;">🔍 Search</button>
                { '<a href="/admin" class="btn btn-outline">Clear</a>' if search_query else '' }
            </form>
            
            <div class="table-container">
                <table>
                    <tr><th>ID</th><th>Registration No.</th><th>Full Name</th><th>Exam Center</th><th>Actions</th></tr>
                    {rows if rows else '<tr><td colspan="5" style="text-align:center; padding: 20px;">No records found matching your search.</td></tr>'}
                </table>
            </div>
        </div>
        """
        return render_page("Admin Dashboard", html, "admin")
        
    except Exception as e:
        logger.error(f"Admin Dashboard Error: {e}")
        return render_page("Error", f"<div class='flash error'>DB Read Error: {e}</div>", "admin")

@app.route('/edit/<int:c_id>', methods=['GET', 'POST'])
def edit(c_id):
    """
    CRUD Operation: UPDATE. Modifies existing database records.
    """
    if not session.get('is_admin'): return redirect(url_for('login'))

    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates WHERE id = %s", (c_id,))
        c = cursor.fetchone()
        cursor.close()
        conn.close()

        if not c: return redirect(url_for('admin_dashboard'))

        html = f"""
        <div class="card admin-card" style="max-width: 600px; margin: 0 auto;">
            <h2>✏️ Modify Record: {c[1]}</h2>
            <p>Database ID: <strong>{c[0]}</strong></p>
            <hr>
            <form method="POST">
                <div class="form-group" style="margin-bottom: 20px;">
                    <label>Update Candidate Name</label>
                    <input type="text" name="name" value="{c[2]}" required>
                </div>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label>Update Applicant Category</label>
                    <select name="category" required>
                        <option value="General" {'selected' if c[5]=='General' else ''}>General</option>
                        <option value="OBC" {'selected' if c[5]=='OBC' else ''}>OBC</option>
                        <option value="SC" {'selected' if c[5]=='SC' else ''}>SC</option>
                        <option value="ST" {'selected' if c[5]=='ST' else ''}>ST</option>
                        <option value="EWS" {'selected' if c[5]=='EWS' else ''}>EWS</option>
                    </select>
                </div>
                <div class="form-group" style="margin-bottom: 30px;">
                    <label>Update Exam Center Relocation</label>
                    <input type="text" name="exam_center" value="{c[6]}" required>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="submit" class="btn btn-primary" style="flex: 1;">💾 Commit Update</button>
                    <a href="/admin" class="btn btn-dark" style="flex: 1;">Cancel</a>
                </div>
            </form>
        </div>
        """
        return render_page("Edit Candidate", html, "admin")

    # Perform DB Update
    try:
        name = request.form['name'].strip()
        category = request.form['category']
        exam_center = request.form['exam_center'].strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE candidates SET name = %s, category = %s, exam_center = %s WHERE id = %s", (name, category, exam_center, c_id))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Admin updated record ID {c_id}")
    except Exception as e:
        logger.error(f"Failed to update record {c_id}: {e}")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/delete/<int:c_id>')
def delete(c_id):
    """
    CRUD Operation: DELETE. Removes a record permanently.
    """
    if not session.get('is_admin'): return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM candidates WHERE id = %s", (c_id,))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Admin deleted record ID {c_id}")
    except Exception as e:
        logger.error(f"Failed to delete record {c_id}: {e}")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/export')
def export_csv():
    """
    File Handling: Generates a CSV file buffer and returns it as a download.
    CBSE Concept: Using the csv module to write data files.
    """
    if not session.get('is_admin'): return redirect(url_for('login'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT registration_no, name, dob, gender, category, exam_center, created_at FROM candidates")
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['Registration Number', 'Full Name', 'Date of Birth', 'Gender', 'Category', 'Exam Center', 'System Timestamp'])
        
        for row in records:
            cw.writerow(row)

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=UPSC_Database_Export_{datetime.now().strftime('%Y%m%d')}.csv"
        output.headers["Content-type"] = "text/csv"
        logger.info("Admin generated CSV Data Export.")
        return output
    except Exception as e:
        logger.error(f"Export Error: {e}")
        return redirect(url_for('admin_dashboard'))

@app.route('/seed')
def seed_database():
    """
    Developer/Examiner Tool: Automatically inserts 3 dummy records for testing.
    Prevents presenting an empty application during practical viva.
    """
    if not session.get('is_admin'): return redirect(url_for('login'))
    
    dummy_data = [
        ("UPSC2026A01", "Arjun Sharma", "2000-05-14", "Male", "General", "New Delhi Center 1"),
        ("UPSC2026B02", "Priya Patel", "2002-11-20", "Female", "OBC", "Ahmedabad Regional"),
        ("UPSC2026C03", "Rahul Verma", "1999-03-08", "Male", "SC", "Lucknow Main Campus")
    ]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT IGNORE INTO candidates (registration_no, name, dob, gender, category, exam_center) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.executemany(query, dummy_data)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Admin executed Database Seeding tool.")
    except Exception as e:
        logger.error(f"Seeding Error: {e}")
        
    return redirect(url_for('admin_dashboard'))

# ============================================================================
# ERROR HANDLING ROUTES
# ============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 Error Page"""
    html = """
    <div class="card" style="text-align: center; padding: 60px 20px;">
        <h1 style="font-size: 4em; color: #ff3f34; margin: 0;">404</h1>
        <h2>Resource Not Found</h2>
        <p>The page or profile you are looking for does not exist in our systems.</p>
        <a href="/" class="btn btn-primary" style="margin-top: 20px;">Return to Safety</a>
    </div>
    """
    return render_page("404 Error", html), 404

@app.errorhandler(500)
def server_error(e):
    """Custom 500 Error Page"""
    html = """
    <div class="card admin-card" style="text-align: center; padding: 60px 20px;">
        <h1 style="font-size: 4em; margin: 0;">⚙️ 500</h1>
        <h2>Internal Server Error</h2>
        <p>Our database servers are currently experiencing issues. Please try again later.</p>
        <a href="/" class="btn btn-dark" style="margin-top: 20px;">Retry Connection</a>
    </div>
    """
    return render_page("500 Error", html), 500

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    # Guarantee tables exist before accepting traffic
    initialize_database()
    # Run server on standard Flask port 5000
    app.run(debug=True, port=5000)
