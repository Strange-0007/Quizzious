from flask import Flask, render_template, request, redirect, url_for, session,flash, jsonify, make_response
import sqlite3
from controllers.init_db import init_db
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from bcrypt import hashpw, gensalt, checkpw
from functools import wraps
from datetime import datetime, timedelta
from utils.form_handler import FormHandler

app = Flask(__name__)

app.secret_key = 'guess_me_if_u_can' # Secret key for session management which can be anything ... im just lazy to think :)

@app.route('/') # Home page route 
def home():
    # Clear any lingering session data if user isn't authenticated
    if not current_user.is_authenticated and session.get('username'):
        session.clear()
        
    response = make_response(render_template('home.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

login_manager = LoginManager() # Creating an instance of LoginManager for using functionalities of flask_login
login_manager.init_app(app) # creating an instance of login manager for the app
login_manager.login_view = 'login' 

class User(UserMixin): # user model class for storing user data
    def __init__(self, id, username, role, full_name=None):
        self.id = id
        self.username = username  
        self.role = role
        self.full_name = full_name

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

@login_manager.user_loader # user loader for loading the user
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, full_name FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2], user[3])
    return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            print("Form data received:", request.form) # Add debug logging
            
            # Check for required fields
            required_fields = ['username', 'full_name', 'qualification', 'dob', 'password']
            for field in required_fields:
                if field not in request.form:
                    flash(f"Missing required field: {field}", "danger")
                    return render_template('register.html')
                    
            username = request.form['username']
            full_name = request.form['full_name']
            qualification = request.form['qualification']
            dob = request.form['dob']
            password = request.form['password']
            
            # Password validation
            password_validation = validate_password(password)
            if not password_validation['valid']:
                flash(f"Password is not strong enough: {password_validation['message']}", "danger")
                return render_template('register.html')
            
            # Email validation
            if not is_valid_email(username):
                flash("Please enter a valid email address for the username", "danger")
                return render_template('register.html')
            
            # Age validation
            if not is_valid_age(dob):
                flash("You must be at least 12 years old to register", "danger")
                return render_template('register.html')
            
            # Hashing the password using bcrypt
            hashed_password = hashpw(password.encode('utf-8'), gensalt())

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            try: # try block for handling exceptions
                cursor.execute("INSERT INTO users (username, full_name, qualification, dob, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
                               (username, full_name, qualification, dob, hashed_password, 'user'))  # insering as user
                conn.commit()
                flash("Registration successful! You can now log in.", "success")  # indicating that registration is successful
                return redirect(url_for('login'))  # Redirecting to login after successful registration
            except sqlite3.IntegrityError:
                flash("Username already exists. Please choose a different one.", "danger")  # indicating that username already exists
            finally:
                conn.close() #closing the connection after the registration is done 
        except Exception as e:
            print("Registration error:", str(e))
            flash(f"Registration failed: {str(e)}", "danger")
            return render_template('register.html')
    
    return render_template('register.html')

def validate_password(password):
    """Validate password strength"""
    errors = []
    
    # Check minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    # Check for uppercase letters
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Check for lowercase letters
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Check for digits
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    # Check for special characters
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"
    if not any(c in special_chars for c in password):
        errors.append("Password must contain at least one special character")
    
    if errors:
        return {"valid": False, "message": " ".join(errors)}
    return {"valid": True, "message": "Password is strong"}

def is_valid_email(email):
    """Validate email format"""
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def is_valid_age(dob):
    """Validate user is at least 12 years old"""
    from datetime import datetime, timedelta
    try:
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        min_age_date = datetime.now() - timedelta(days=12*365)
        return dob_date <= min_age_date
    except ValueError:
        return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate submitted data
        if not username or not password:
            flash("Please provide both username and password", "danger")
            return render_template('login.html')
            
        # Connect to database and check credentials
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role, full_name FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        # Verify user exists and password matches
        if user and checkpw(password.encode('utf-8'), user[2]):
            # Create user object for Flask-Login
            user_obj = User(user[0], user[1], user[3], user[4])
            login_user(user_obj)
            
            # Also store in session for compatibility with existing code
            session['role'] = user[3]
            session['username'] = user[1]
            
            flash("Login successful! Welcome back.", "success")
            
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
            
    return render_template('login.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('home'))  # Redirect to home if not admin
        return f(*args, **kwargs)
    return decorated_function

'''@app.route('/admin-dashboard') # Admin dashboard route for admin users
@login_required # login required decorator for checking if the user is logged in or not
def admin_dashboard():
    if 'username' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html', username=session['username'])
    return redirect(url_for('home'))'''


@app.route('/user-dashboard')
@login_required
def user_dashboard():
    if current_user.role == 'user':
        # Get search query if any
        search_query = request.args.get('search_query', '')
        
        # Get all available subjects
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Fetch subjects that have quizzes, with optional search filter
        if search_query:
            cursor.execute("""
                SELECT DISTINCT s.id, s.name, s.description, COUNT(q.id) as quiz_count
                FROM subjects s
                JOIN chapters c ON s.id = c.subject_id
                JOIN quizzes q ON c.id = q.chapter_id
                WHERE s.name LIKE ? OR s.description LIKE ?
                GROUP BY s.id
                ORDER BY s.name
            """, (f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("""
                SELECT DISTINCT s.id, s.name, s.description, COUNT(q.id) as quiz_count
                FROM subjects s
                JOIN chapters c ON s.id = c.subject_id
                JOIN quizzes q ON c.id = q.chapter_id
                GROUP BY s.id
                ORDER BY s.name
            """)
        
        subjects = cursor.fetchall()
        conn.close()

        return render_template('user_dashboard.html', subjects=subjects, search_query=search_query)
    return redirect(url_for('home'))

@app.route('/attempt-quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('home'))
    
    # Get if user is coming from dashboard - check both URL and form data
    from_dashboard = request.args.get('from_dashboard') == 'true' or request.form.get('from_dashboard') == 'true'
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check if user has already attempted this quiz
    cursor.execute("""
        SELECT id, total_scored, total_questions FROM scores 
        WHERE quiz_id = ? AND user_id = (SELECT id FROM users WHERE username = ?)
        ORDER BY time_stamp_of_attempt DESC LIMIT 1
    """, (quiz_id, session['username']))
    previous_attempt = cursor.fetchone()
    
    # Determine if this is a fresh attempt or showing results of a previous attempt
    allow_attempt = from_dashboard or not previous_attempt
    
    # Get quiz details for display
    cursor.execute("""
        SELECT q.quiz_name, q.time_duration, c.name as chapter_name, s.name as subject_name
        FROM quizzes q
        JOIN chapters c ON q.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE q.id = ?
    """, (quiz_id,))
    quiz_details = cursor.fetchone()
    
    if not quiz_details:
        flash("Quiz not found", "error")
        return redirect(url_for('user_dashboard'))
        
    quiz_name = quiz_details[0]
    total_duration = quiz_details[1] * 60  # Convert to seconds
    chapter_name = quiz_details[2]
    subject_name = quiz_details[3]
    
    # Initialize variables
    completed = False
    user_answers = {}
    results = {}
    score = 0
    total_questions = 0
    
    if request.method == 'POST' and allow_attempt:
        # Get all questions for this quiz
        cursor.execute("SELECT id, question_statement, option1, option2, option3, option4, correct_option FROM questions WHERE quiz_id = ?", (quiz_id,))
        all_questions = cursor.fetchall()
        total_questions = len(all_questions)
        
        if total_questions == 0:
            flash("This quiz has no questions", "error")
            conn.close()
            return redirect(url_for('user_dashboard'))
        
        # Process each question
        for question in all_questions:
            question_id = question[0]
            correct_option = question[6]
            user_answer = request.form.get(f'question_{question_id}')
            
            # Store user's answer
            if user_answer:
                user_answers[question_id] = int(user_answer)
                # Check if answer is correct
                if int(user_answer) == correct_option:
                    score += 1
                    results[question_id] = 'correct'
                else:
                    results[question_id] = 'incorrect'
            else:
                user_answers[question_id] = None
                results[question_id] = 'unanswered'
        
        # Record the score in the database
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO scores 
                (quiz_id, user_id, time_stamp_of_attempt, total_scored, total_questions) 
            VALUES 
                (?, (SELECT id FROM users WHERE username = ?), ?, ?, ?)
        """, (quiz_id, session['username'], current_time, score, total_questions))
        
        # Get the ID of the inserted score
        score_id = cursor.lastrowid
        
        # Save individual question responses (add this part)
        for question_id, answer in user_answers.items():
            if answer is not None:
                cursor.execute("""
                    INSERT INTO question_responses
                        (score_id, question_id, user_answer)
                    VALUES
                        (?, ?, ?)
                """, (score_id, question_id, answer))
        
        conn.commit()
        conn.close()
        
        # Redirect to the results page instead of showing results on same page
        return redirect(url_for('quiz_results', quiz_id=quiz_id))
        
    elif previous_attempt and not allow_attempt:
        # Redirect to results page if already attempted
        return redirect(url_for('quiz_results', quiz_id=quiz_id))
    
    # Get all questions for display
    cursor.execute("""
        SELECT id, question_statement, option1, option2, option3, option4, correct_option
        FROM questions 
        WHERE quiz_id = ?
    """, (quiz_id,))
    questions = cursor.fetchall()
    
    conn.close()
    
    # Render the template for quiz taking
    return render_template('attempt_quiz.html', 
                         quiz_id=quiz_id,
                         quiz_name=quiz_name,
                         chapter_name=chapter_name, 
                         subject_name=subject_name,
                         questions=questions, 
                         total_duration=total_duration,
                         completed=completed,
                         allow_attempt=allow_attempt,
                         previous_attempt=previous_attempt)

@app.route('/quiz-results/<int:quiz_id>')
@login_required
def quiz_results(quiz_id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check if user has attempted this quiz
    cursor.execute("""
        SELECT id, total_scored, total_questions FROM scores 
        WHERE quiz_id = ? AND user_id = (SELECT id FROM users WHERE username = ?)
        ORDER BY time_stamp_of_attempt DESC LIMIT 1
    """, (quiz_id, session['username']))
    previous_attempt = cursor.fetchone()
    
    if not previous_attempt:
        flash("You haven't attempted this quiz yet.", "warning")
        return redirect(url_for('user_dashboard'))
        
    # Get quiz details for display
    cursor.execute("""
        SELECT q.quiz_name, q.time_duration, c.name as chapter_name, s.name as subject_name
        FROM quizzes q
        JOIN chapters c ON q.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE q.id = ?
    """, (quiz_id,))
    quiz_details = cursor.fetchone()
    
    if not quiz_details:
        flash("Quiz not found", "error")
        return redirect(url_for('user_dashboard'))
        
    quiz_name = quiz_details[0]
    chapter_name = quiz_details[2]
    subject_name = quiz_details[3]
    
    # Get user's answers and correct answers
    score = previous_attempt[1]
    total_questions = previous_attempt[2]
    
    # Get all questions for display
    cursor.execute("""
        SELECT id, question_statement, option1, option2, option3, option4, correct_option
        FROM questions 
        WHERE quiz_id = ?
    """, (quiz_id,))
    questions = cursor.fetchall()
    
    # Create a dictionary of questions for easy lookup by question ID
    questions_dict = {}
    for question in questions:
        questions_dict[question[0]] = question
    
    # Get the user's answers if available (for latest attempt)
    cursor.execute("""
        SELECT question_id, user_answer 
        FROM question_responses
        WHERE score_id = ?
    """, (previous_attempt[0],))
    answers = cursor.fetchall()
    
    # Since we don't store individual question answers in the database,
    # we'll just get the correct answers for display
    user_answers = {}
    results = {}
    
    for answer in answers:
        question_id = answer[0]
        user_answer = answer[1]
        user_answers[question_id] = user_answer
        
        # Check if this question exists in our questions dictionary
        if question_id in questions_dict:
            correct_option = questions_dict[question_id][6]
            results[question_id] = 'correct' if user_answer == correct_option else 'incorrect'
        else:
            # Handle case where question might have been deleted
            results[question_id] = 'unknown'
    
    # Get chapter_id for the quiz
    cursor.execute("""
        SELECT c.id
        FROM quizzes q
        JOIN chapters c ON q.chapter_id = c.id
        WHERE q.id = ?
    """, (quiz_id,))
    chapter_id = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('quiz_results.html', 
                          quiz_id=quiz_id,
                          quiz_name=quiz_name,
                          chapter_name=chapter_name, 
                          subject_name=subject_name,
                          score=score,
                          total_questions=total_questions,
                          questions=questions, 
                          results=results,
                          user_answers=user_answers,
                          chapter_id=chapter_id)

@app.route('/admin/subject', methods=['GET', 'POST'])
@admin_required
def subject():
    if request.method == 'POST':
        # Check if it's a search request
        if 'search' in request.form:
            search_query = request.form['search_query']
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subjects WHERE name LIKE ? OR description LIKE ?", 
                          (f'%{search_query}%', f'%{search_query}%'))
            subjects = cursor.fetchall()
            conn.close()
            return render_template('subject.html', subjects=subjects, search_query=search_query)
        
        # Original POST handling for adding a subject
        name = request.form['name']
        description = request.form['description']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the subject already exists
        cursor.execute("SELECT * FROM subjects WHERE name=?", (name,))
        existing_subject = cursor.fetchone()

        if existing_subject:
            flash("Subject already exists. Please choose a different name.", "danger")  # Error message
            conn.close()
            return redirect(url_for('subject'))  # Redirect to the same page

        cursor.execute("INSERT INTO subjects (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        conn.close()
        
        flash("Subject added successfully!", "success")
        return redirect(url_for('subject'))  # Redirect to admin dashboard after creation

    else:
        search_query = request.args.get('search_query', '')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        if search_query:
            cursor.execute("SELECT * FROM subjects WHERE name LIKE ? OR description LIKE ?", 
                          (f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("SELECT * FROM subjects")
            
        subjects = cursor.fetchall()
        conn.close()
        
        return render_template('subject.html', subjects=subjects, search_query=search_query)

@app.route('/admin/edit-subject/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cursor.execute("UPDATE subjects SET name=?, description=? WHERE id=?", (name, description, subject_id))
        conn.commit()
        conn.close()
        
        flash("Subject updated successfully!", "success")
        return redirect(url_for('subject'))  # Redirect to the subjects route

    # Fetch the specific subject to edit
    cursor.execute("SELECT * FROM subjects WHERE id=?", (subject_id,))
    subject = cursor.fetchone()  # Fetch the single subject
    conn.close()
    
    return render_template('edit_subject.html', subject=subject)

@app.route('/admin/delete-subject/<int:subject_id>', methods=['POST', 'GET'])
@admin_required
def delete_subject(subject_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
    conn.commit()
    conn.close()
    
    flash("Subject deleted successfully!", "success")
    return redirect(url_for('subject'))

@app.route('/admin/chapter', methods=['GET', 'POST'])
@admin_required
def chapter():
    if request.method == 'POST':
        # Check if it's a search request
        if 'search' in request.form:
            search_query = request.form['search_query']
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT subjects.name AS subject_name, chapters.id AS chapter_id, 
                       chapters.name AS chapter_name, chapters.description 
                FROM chapters
                JOIN subjects ON chapters.subject_id = subjects.id
                WHERE chapters.name LIKE ? OR chapters.description LIKE ? OR subjects.name LIKE ?
            ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
            chapters = cursor.fetchall()
            
            cursor.execute("SELECT * FROM subjects")
            subjects = cursor.fetchall()
            
            conn.close()
            return render_template('chapter.html', subjects=subjects, chapters=chapters, search_query=search_query)
            
        # Original POST handling for adding a chapter
        subject_id = request.form['subject_id']
        name = request.form['name']
        description = request.form['description']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the chapter already exists for the selected subject
        cursor.execute("SELECT * FROM chapters WHERE name=? AND subject_id=?", (name, subject_id))
        existing_chapter = cursor.fetchone()

        if existing_chapter:
            flash("Chapter already exists under this subject. Please choose a different name.", "danger")  # Error message
            conn.close()
            return redirect(url_for('chapter'))  # Redirect to the same page

        cursor.execute("INSERT INTO chapters (subject_id, name, description) VALUES (?, ?, ?)", 
                       (subject_id, name, description))
        conn.commit()
        conn.close()
        
        flash("Chapter added successfully!", "success")
        return redirect(url_for('chapter'))  # Redirect to the chapters route

    # GET request handling
    search_query = request.args.get('search_query', '')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Fetch subjects for the dropdown
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    
    # Fetch chapters with optional search filter
    if search_query:
        cursor.execute('''
            SELECT subjects.name AS subject_name, chapters.id AS chapter_id, 
                   chapters.name AS chapter_name, chapters.description 
            FROM chapters
            JOIN subjects ON chapters.subject_id = subjects.id
            WHERE chapters.name LIKE ? OR chapters.description LIKE ? OR subjects.name LIKE ?
        ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute('''
            SELECT subjects.name AS subject_name, chapters.id AS chapter_id, 
                   chapters.name AS chapter_name, chapters.description 
            FROM chapters
            JOIN subjects ON chapters.subject_id = subjects.id
        ''')
    
    chapters = cursor.fetchall()
    conn.close()
    
    return render_template('chapter.html', subjects=subjects, chapters=chapters, search_query=search_query)

@app.route('/admin/edit-chapter/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def edit_chapter(chapter_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        subject_id = request.form['subject_id']  # Get the selected subject ID from the form
        name = request.form['name']
        description = request.form['description']
        
        # Update the chapter with the new values
        cursor.execute("UPDATE chapters SET subject_id=?, name=?, description=? WHERE id=?", (subject_id, name, description, chapter_id))
        conn.commit()
        conn.close()
        
        flash("Chapter updated successfully!", "success")
        return redirect(url_for('chapter'))  # Redirect to the chapters route

    # Fetch the specific chapter to edit
    cursor.execute("SELECT * FROM chapters WHERE id=?", (chapter_id,))
    chapter = cursor.fetchone()

    # Fetch all subjects to populate the dropdown
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    conn.close()
    
    return render_template('edit_chapter.html', chapter=chapter, subjects=subjects)

@app.route('/admin/delete-chapter/<int:chapter_id>', methods=['POST'])
@admin_required
def delete_chapter(chapter_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chapters WHERE id=?", (chapter_id,))
    conn.commit()
    conn.close()
    
    flash("Chapter deleted successfully!", "success")
    return redirect(url_for('chapter'))  # Redirect to the chapters route

@app.route('/fetch_subjects', methods=['GET'])
def fetch_subjects():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects")
    subjects = cursor.fetchall()
    conn.close()
    return jsonify(subjects)

@app.route('/fetch_chapters/<int:subject_id>', methods=['GET'])
def fetch_chapters(subject_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM chapters WHERE subject_id=?", (subject_id,))
    chapters = cursor.fetchall()
    conn.close()
    return jsonify(chapters)

@app.route('/admin/quiz', methods=['GET', 'POST'])
@admin_required
def create_quiz():
    if request.method == 'POST':
        # Check if it's a search request
        if 'search' in request.form:
            search_query = request.form['search_query']
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name FROM subjects")
            subjects = cursor.fetchall()
            
            cursor.execute("SELECT id, subject_id, name FROM chapters")
            chapters = cursor.fetchall()
            
            cursor.execute('''
                SELECT q.*, c.name AS chapter_name, s.name AS subject_name
                FROM quizzes q
                JOIN chapters c ON q.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                WHERE q.quiz_name LIKE ? OR q.remarks LIKE ? OR c.name LIKE ? OR s.name LIKE ?
            ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
            
            quizzes = cursor.fetchall()
            conn.close()
            
            return render_template('quiz.html', subjects=subjects, chapters=chapters, 
                                  quizzes=quizzes, search_query=search_query)
        
        # Original POST handling for adding a quiz
        if request.form.get('quiz_add') is not None:
            chapter_id = request.form['chapter_name']  # Get the chapter ID from the form
            quiz_name = request.form['quiz_name']  # Get the quiz name from the form
            date_of_quiz = request.form['date_of_quiz']
            time_duration_hours = int(request.form['time_duration_hours'])  # Get hours
            time_duration_minutes = int(request.form['time_duration_minutes'])  # Get minutes
            remarks = request.form.get('remarks', '')  # Default to empty if not provided
            
            # Check if the quiz already exists for the selected chapter
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quizzes WHERE quiz_name=? AND chapter_id=?", (quiz_name, chapter_id))
            existing_quiz = cursor.fetchone()

            if existing_quiz:
                flash("Quiz already exists under this chapter. Please choose a different name.", "danger")  # Error message
                conn.close()
                return redirect(url_for('create_quiz'))  # Redirect to the same page

            # Calculate total time duration in minutes
            total_time_duration = (time_duration_hours * 60) + time_duration_minutes
            
            # Insert the quiz data into the quizzes table
            cursor.execute('''
                INSERT INTO quizzes (chapter_id, quiz_name, date_of_quiz, time_duration, remarks)
                VALUES (?, ?, ?, ?, ?)
            ''', (chapter_id, quiz_name, date_of_quiz, total_time_duration, remarks))

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

            # Flash a success message and redirect
            flash("Quiz created successfully!", "success")
            return redirect(url_for('create_quiz'))

    else:
        # Handle GET request with optional search
        search_query = request.args.get('search_query', '')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name FROM subjects")
        subjects = cursor.fetchall()
        
        cursor.execute("SELECT id, subject_id, name FROM chapters")
        chapters = cursor.fetchall()
        
        if search_query:
            cursor.execute('''
                SELECT q.*, c.name AS chapter_name, s.name AS subject_name
                FROM quizzes q
                JOIN chapters c ON q.chapter_id = c.id
                JOIN subjects s ON c.subject_id = s.id
                WHERE q.quiz_name LIKE ? OR q.remarks LIKE ? OR c.name LIKE ? OR s.name LIKE ?
            ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("SELECT * FROM quizzes")
            
        quizzes = cursor.fetchall()
        conn.close()
        
        return render_template('quiz.html', subjects=subjects, chapters=chapters, 
                              quizzes=quizzes, search_query=search_query)

@app.route('/admin/delete-quiz/<int:quiz_id>', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quizzes WHERE id=?", (quiz_id,))
    conn.commit()
    conn.close()
    
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('create_quiz'))

@app.route('/admin/edit-quiz/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        print("Quiz is being updated, POST")
        quiz_name = request.form['quiz_name']  # Get the quiz name from the form
        date_of_quiz = request.form['date_of_quiz']
        time_duration_hours = int(request.form['time_duration_hours'])  # Get hours
        time_duration_minutes = int(request.form['time_duration_minutes'])  # Get minutes
        remarks = request.form['remarks']
        
        # Calculate total duration in minutes
        total_duration = (time_duration_hours * 60) + time_duration_minutes
        
        # Update the quiz with the new values
        cursor.execute("UPDATE quizzes SET quiz_name=?, date_of_quiz=?, time_duration=?, remarks=? WHERE id=?", 
                       (quiz_name, date_of_quiz, total_duration, remarks, quiz_id))
        conn.commit()
        conn.close()
        
        flash("Quiz updated successfully!", "success")
        return redirect(url_for('create_quiz'))  # Redirect to the quizzes list

    # Fetch the specific quiz to edit
    cursor.execute("SELECT * FROM quizzes WHERE id=?", (quiz_id,))
    quiz = cursor.fetchone()  # Fetch the quiz data to edit

    conn.close()
    
    return render_template('edit_quiz.html', quiz=quiz)  # Pass the quiz data to the template


@app.route('/quiz/select-chapter/<int:subject_id>', methods=['GET'])
def get_chapters(subject_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM chapters WHERE subject_id=?", (subject_id,))
    chapters = cursor.fetchall()
    conn.close()
    
    return render_template('select_chapter.html', chapters=chapters)


@app.route('/admin/question', methods=['GET', 'POST'])
@admin_required
def question():
    if request.method == 'POST':
        # Check if it's a search request
        if 'search' in request.form:
            search_query = request.form.get('search_query', '')
            subject_filter = request.form.get('subject_filter', '')
            chapter_filter = request.form.get('chapter_filter', '')
            quiz_filter = request.form.get('quiz_filter', '')
            
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            # Build dynamic query with filters
            query = """SELECT 
                subjects.name AS subject_name,
                chapters.name AS chapter_name,
                quizzes.id AS quiz_id,
                quizzes.quiz_name,
                quizzes.date_of_quiz,
                quizzes.time_duration,
                quizzes.remarks 
                
            FROM 
                quizzes
            JOIN 
                chapters ON quizzes.chapter_id = chapters.id
            JOIN 
                subjects ON chapters.subject_id = subjects.id
            WHERE 1=1"""
            
            params = []
            
            # Add conditions based on provided filters
            if search_query:
                query += """ AND (quizzes.quiz_name LIKE ? OR
                    chapters.name LIKE ? OR
                    subjects.name LIKE ?)"""
                params.extend([f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])
            
            if subject_filter:
                query += " AND subjects.name LIKE ?"
                params.append(f'%{subject_filter}%')
                
            if chapter_filter:
                query += " AND chapters.name LIKE ?"
                params.append(f'%{chapter_filter}%')
                
            if quiz_filter:
                query += " AND quizzes.quiz_name LIKE ?"
                params.append(f'%{quiz_filter}%')
            
            cursor.execute(query, params)
            quizzes = cursor.fetchall()
            conn.close()
            
            return render_template('question.html', quizzes=quizzes, 
                                  search_query=search_query,
                                  subject_filter=subject_filter, 
                                  chapter_filter=chapter_filter,
                                  quiz_filter=quiz_filter)
        
        # Rest of the existing code for adding a question
        # ...

    # GET request handling with optional search
    search_query = request.args.get('search_query', '')
    subject_filter = request.args.get('subject_filter', '')
    chapter_filter = request.args.get('chapter_filter', '')
    quiz_filter = request.args.get('quiz_filter', '')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Build dynamic query with filters
    query = """SELECT 
        subjects.name AS subject_name,
        chapters.name AS chapter_name,
        quizzes.id AS quiz_id,
        quizzes.quiz_name,
        quizzes.date_of_quiz,
        quizzes.time_duration,
        quizzes.remarks 
        
    FROM 
        quizzes
    JOIN 
        chapters ON quizzes.chapter_id = chapters.id
    JOIN 
        subjects ON chapters.subject_id = subjects.id
    WHERE 1=1"""
    
    params = []
    
    # Add conditions based on provided filters
    if search_query:
        query += """ AND (quizzes.quiz_name LIKE ? OR
            chapters.name LIKE ? OR
            subjects.name LIKE ?)"""
        params.extend([f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])
    
    if subject_filter:
        query += " AND subjects.name LIKE ?"
        params.append(f'%{subject_filter}%')
        
    if chapter_filter:
        query += " AND chapters.name LIKE ?"
        params.append(f'%{chapter_filter}%')
        
    if quiz_filter:
        query += " AND quizzes.quiz_name LIKE ?"
        params.append(f'%{quiz_filter}%')
    
    cursor.execute(query, params)
    quizzes = cursor.fetchall()
    conn.close()
    
    return render_template('question.html', quizzes=quizzes, 
                          search_query=search_query,
                          subject_filter=subject_filter,
                          chapter_filter=chapter_filter,
                          quiz_filter=quiz_filter)

@app.route('/admin/question_add', methods=['GET', 'POST'])
@admin_required
def question_add():
    # Get parameters
    quiz_id = request.args.get('quiz_id')
    quiz_subject = request.args.get('quiz_subject')
    quiz_chapter = request.args.get('quiz_chapter')
    search_query = request.args.get('search_query', '')
    
    # New parameters for advanced filtering
    option_filter = request.args.get('option_filter', '')
    correct_answer_filter = request.args.get('correct_answer_filter', '')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Handle form submission to add a new question
    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form.get('option3', '')  # Optional
        option4 = request.form.get('option4', '')  # Optional
        correct_option = request.form['correct_option']
        
        # Insert the question into the database
        cursor.execute("""
            INSERT INTO questions 
            (quiz_id, question_statement, option1, option2, option3, option4, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (quiz_id, question_statement, option1, option2, option3, option4, correct_option))
        
        conn.commit()
        flash("Question added successfully!", "success")
        
        # Redirect to maintain the same page with parameters
        return redirect(url_for('question_add', 
                              quiz_id=quiz_id, 
                              quiz_subject=quiz_subject, 
                              quiz_chapter=quiz_chapter))
    
    # Build the dynamic query with filters
    query = "SELECT * FROM questions WHERE quiz_id = ?"
    params = [quiz_id]
    
    # Add conditions based on provided filters
    if search_query:
        query += " AND question_statement LIKE ?"
        params.append(f'%{search_query}%')
    
    if option_filter:
        query += " AND (option1 LIKE ? OR option2 LIKE ? OR option3 LIKE ? OR option4 LIKE ?)"
        params.extend([f'%{option_filter}%'] * 4)
    
    if correct_answer_filter and correct_answer_filter.isdigit():
        query += " AND correct_option = ?"
        params.append(int(correct_answer_filter))
    
    # Execute the query
    cursor.execute(query, params)
    questions = cursor.fetchall()
    conn.close()

    # Render template with all parameters
    return render_template('add_question.html', 
                          quiz_id=quiz_id,
                          questions=questions, 
                          quiz_subject=quiz_subject, 
                          quiz_chapter=quiz_chapter,
                          search_query=search_query,
                          option_filter=option_filter,
                          correct_answer_filter=correct_answer_filter)

@app.route('/admin/delete-question/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id=?", (question_id,))
    conn.commit()
    conn.close()
    
    flash("Question deleted successfully!", "success")
    return redirect(url_for('question'))

@app.route('/admin/edit-question/<int:question_id>', methods=['GET', 'POST'])
@admin_required  # Ensure you have an admin_required decorator defined
def edit_question(question_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form.get('option3')  # Optional
        option4 = request.form.get('option4')  # Optional
        correct_option = request.form['correct_option']
        
        # Update the question in the database
        conn.execute('''
            UPDATE questions
            SET question_statement = ?, option1 = ?, option2 = ?, option3 = ?, option4 = ?, correct_option = ?
            WHERE id = ?
        ''', (question_statement, option1, option2, option3, option4, correct_option, question_id))
        
        conn.commit()
        conn.close()
        
        flash("Question updated successfully!", "success")
        return redirect(url_for('question'))  # Redirect to the questions route

    # Fetch the specific question to edit
    cursor.execute("SELECT * FROM questions WHERE id=?", (question_id,))
    question = cursor.fetchone()
    conn.close()
    
    if question is None:
        flash("Question not found!", "danger")
        return redirect(url_for('question'))  # Redirect if question not found

    return render_template('edit_question.html', question=question)

@app.route('/admin/manage-users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # Handle user deletion if a delete request is made
        user_id = request.form.get('delete_user_id')
        if user_id:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            flash("User deleted successfully!", "success")

    # Fetch all users
    cursor.execute("SELECT id, username, full_name, qualification FROM users where role = 'user'")
    users = cursor.fetchall()
    conn.close()

    return render_template('manage_users.html', users=users)

@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    form_handler = FormHandler()
    if request.method == 'POST':
        # Get form data
        form_data = {
            'username': request.form.get('username'),
            'full_name': request.form.get('full_name'),
            'qualification': request.form.get('qualification'),
            'dob': request.form.get('dob'),
            'password': request.form.get('password'),
            'role': request.form.get('role')
        }
        
        # Validate form data
        if form_handler.validate_user_form(form_data):
            # Process the valid form
            # Your existing code for saving user data
            return redirect(url_for('manage_users'))
        else:
            # Return to form with errors
            return render_template('edit_user.html', form_data=form_data, errors=form_handler.errors)
    
    # For GET requests or if validation fails
    # Your existing code to render the form
    return render_template('edit_user.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Fetch subjects
    cursor.execute("SELECT id, name, description FROM subjects")
    subjects = cursor.fetchall()

    # Fetch chapters
    cursor.execute("SELECT id, subject_id, name FROM chapters")
    chapters = cursor.fetchall()

    # Fetch quizzes
    cursor.execute("SELECT id, chapter_id, quiz_name FROM quizzes")
    quizzes = cursor.fetchall()

    # Get total counts
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM scores")
    total_attempts = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'admin_dashboard.html',
        subjects=subjects,
        chapters=chapters,
        quizzes=quizzes,
        total_subjects=len(subjects),
        total_chapters=len(chapters),
        total_quizzes=len(quizzes),
        total_questions=total_questions,
        total_users=total_users,
        total_attempts=total_attempts
    )


@app.route('/admin/statistics')
@admin_required
def admin_statistics():
    """Statistics page with all charts for admin"""
    return render_template('admin_statistics.html')

@app.route('/api/admin/quiz-stats', methods=['GET'])
@admin_required
def admin_quiz_stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get subject performance data
    cursor.execute("""
        SELECT 
            sub.name, 
            COUNT(s.id) as attempt_count,
            ROUND(AVG(s.total_scored * 100.0 / s.total_questions), 2) as avg_score
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        JOIN 
            chapters ch ON q.chapter_id = ch.id
        JOIN 
            subjects sub ON ch.subject_id = sub.id
        GROUP BY 
            sub.name
        ORDER BY 
            sub.name
    """)
    subject_stats = [{
        'name': row[0],
        'attempts': row[1],
        'avg_score': row[2]
    } for row in cursor.fetchall()]
    
    # Get monthly statistics for the past 6 months
    cursor.execute("""
        SELECT 
            strftime('%Y-%m', time_stamp_of_attempt) as month,
            COUNT(id) as attempts,
            ROUND(AVG(total_scored * 100.0 / total_questions), 2) as avg_percentage
        FROM 
            scores
        WHERE 
            time_stamp_of_attempt >= date('now', '-6 months')
        GROUP BY 
            month
        ORDER BY 
            month
    """)
    monthly_stats = [{
        'month': row[0],
        'attempts': row[1],
        'avg_score': row[2]
    } for row in cursor.fetchall()]
    
    # Get user participation statistics
    cursor.execute("""
        SELECT 
            u.username,
            COUNT(s.id) as attempt_count,
            ROUND(AVG(s.total_scored * 100.0 / s.total_questions), 2) as avg_score
        FROM 
            scores s
        JOIN 
            users u ON s.user_id = u.id
        GROUP BY 
            u.id
        ORDER BY 
            attempt_count DESC
        LIMIT 10
    """)
    user_stats = [{
        'username': row[0],
        'attempts': row[1],
        'avg_score': row[2]
    } for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'subject_stats': subject_stats,
        'monthly_stats': monthly_stats,
        'user_stats': user_stats
    })

@app.route('/api/admin/detailed_stats', methods=['GET'])
@admin_required
def admin_detailed_stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get quiz difficulty data
    cursor.execute("""
        SELECT 
            q.quiz_name, 
            ROUND(AVG(s.total_scored * 100.0 / s.total_questions), 2) as avg_score
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        GROUP BY 
            q.quiz_name
        ORDER BY 
            avg_score
        LIMIT 10
    """)
    quiz_difficulty = [{
        'quiz_name': row[0],
        'avg_score': row[1]
    } for row in cursor.fetchall()]
    
    # Get weekly activity data
    cursor.execute("""
        SELECT 
            'Week ' || strftime('%W', time_stamp_of_attempt) as week,
            COUNT(*) as attempts,
            ROUND(AVG(total_scored * 100.0 / total_questions), 2) as avg_score
        FROM 
            scores
        WHERE 
            time_stamp_of_attempt >= date('now', '-12 weeks')
        GROUP BY 
            strftime('%W', time_stamp_of_attempt)
        ORDER BY 
            strftime('%W', time_stamp_of_attempt) ASC
        LIMIT 12
    """)
    weekly_activity = [{
        'week': row[0],
        'attempts': row[1],
        'avg_score': row[2] if row[2] is not None else 0
    } for row in cursor.fetchall()]
    
    # Get top quizzes by attempt count
    cursor.execute("""
        SELECT 
            q.quiz_name,
            ch.name as chapter_name,
            COUNT(*) as attempt_count,
            ROUND(AVG(s.total_scored * 100.0 / s.total_questions), 2) as avg_score
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        JOIN 
            chapters ch ON q.chapter_id = ch.id
        GROUP BY 
            q.quiz_name
        ORDER BY 
            attempt_count DESC
        LIMIT 10
    """)
    top_quizzes = [{
        'quiz_name': row[0],
        'chapter_name': row[1],
        'attempt_count': row[2],
        'avg_score': row[3]
    } for row in cursor.fetchall()]
    
    # Get recent quiz attempts
    cursor.execute("""
        SELECT 
            u.username,
            q.quiz_name,
            s.total_scored,
            s.total_questions,
            s.time_stamp_of_attempt,
            ROUND(s.total_scored * 100.0 / s.total_questions, 2) as percentage
        FROM 
            scores s
        JOIN 
            users u ON s.user_id = u.id
        JOIN 
            quizzes q ON s.quiz_id = q.id
        ORDER BY 
            s.time_stamp_of_attempt DESC
        LIMIT 10
    """)
    recent_attempts = [{
        'username': row[0],
        'quiz_name': row[1],
        'score': row[2],
        'total': row[3],
        'date': row[4],
        'percentage': row[5]
    } for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'quiz_difficulty': quiz_difficulty,
        'weekly_activity': weekly_activity,
        'top_quizzes': top_quizzes,
        'recent_attempts': recent_attempts
    })

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'], role=session['role'])
    return redirect(url_for('home'))

@app.route('/user/scores')
def user_scores():
    if 'username' not in session:
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Enhanced query to get more detailed information about quiz attempts
    cursor.execute("""
        SELECT 
            q.quiz_name,
            s.total_scored,
            s.total_questions,
            s.time_stamp_of_attempt,
            c.name as chapter_name,
            sub.name as subject_name,
            ROUND(CAST(s.total_scored AS FLOAT) / CAST(s.total_questions AS FLOAT) * 100, 2) as percentage,
            sub.id as subject_id,
            c.id as chapter_id
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        JOIN 
            chapters c ON q.chapter_id = c.id
        JOIN 
            subjects sub ON c.subject_id = sub.id
        WHERE 
            s.user_id = (SELECT id FROM users WHERE username = ?)
        ORDER BY 
            s.time_stamp_of_attempt DESC
    """, (session['username'],))
    scores = cursor.fetchall()
    
    # Get all subjects for dropdown
    cursor.execute("""
        SELECT DISTINCT sub.id, sub.name 
        FROM subjects sub
        JOIN chapters c ON sub.id = c.subject_id
        JOIN quizzes q ON c.id = q.chapter_id
        JOIN scores s ON q.id = s.quiz_id
        WHERE s.user_id = (SELECT id FROM users WHERE username = ?)
        ORDER BY sub.name
    """, (session['username'],))
    subjects = cursor.fetchall()
    conn.close()

    return render_template('user_scores.html', scores=scores, subjects=subjects)

@app.route('/user/subject/<int:subject_id>')
@login_required
def user_subject(subject_id):
    if current_user.role != 'user':
        return redirect(url_for('home'))
    
    # Get search query if any
    search_query = request.args.get('search_query', '')
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get subject details
    cursor.execute("SELECT id, name, description FROM subjects WHERE id=?", (subject_id,))
    subject = cursor.fetchone()
    
    if not subject:
        flash("Subject not found.", "error")
        return redirect(url_for('user_dashboard'))
    
    # Get chapters for this subject, with optional search filter
    if search_query:
        cursor.execute("""
            SELECT c.id, c.name, c.description, COUNT(q.id) as quiz_count
            FROM chapters c
            LEFT JOIN quizzes q ON c.id = q.chapter_id
            WHERE c.subject_id = ? AND (c.name LIKE ? OR c.description LIKE ?)
            GROUP BY c.id
            ORDER BY c.name
        """, (subject_id, f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute("""
            SELECT c.id, c.name, c.description, COUNT(q.id) as quiz_count
            FROM chapters c
            LEFT JOIN quizzes q ON c.id = q.chapter_id
            WHERE c.subject_id = ?
            GROUP BY c.id
            ORDER BY c.name
        """, (subject_id,))
    
    chapters = cursor.fetchall()
    conn.close()
    
    return render_template('user_subject.html', subject=subject, chapters=chapters, search_query=search_query)

@app.route('/logout')
@login_required
def logout():
    # Clear Flask-Login session
    logout_user()
    
    # Clear all session data
    session.clear()
    
    # Create a response with cache control headers
    response = redirect(url_for('home', _cb=datetime.now().timestamp()))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    flash("You have been logged out.", "info")
    return response

@app.route('/user/chapter/<int:chapter_id>')
@login_required
def user_chapter(chapter_id):
    if current_user.role != 'user':
        return redirect(url_for('home'))
    
    # Get search query if any
    search_query = request.args.get('search_query', '')
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get chapter details
    cursor.execute("""
        SELECT c.id, c.name, c.description, s.id as subject_id, s.name as subject_name
        FROM chapters c
        JOIN subjects s ON c.subject_id = s.id
        WHERE c.id=?
    """, (chapter_id,))
    chapter = cursor.fetchone()
    
    if not chapter:
        flash("Chapter not found.", "error")
        return redirect(url_for('user_dashboard'))
    
    # Get quizzes for this chapter, with optional search filter
    if search_query:
        cursor.execute("""
            SELECT q.id, q.quiz_name, q.date_of_quiz, q.time_duration, q.remarks 
            FROM quizzes q
            WHERE q.chapter_id = ? AND (q.quiz_name LIKE ? OR q.remarks LIKE ?)
            ORDER BY q.date_of_quiz DESC
        """, (chapter_id, f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute("""
            SELECT q.id, q.quiz_name, q.date_of_quiz, q.time_duration, q.remarks 
            FROM quizzes q
            WHERE q.chapter_id = ?
            ORDER BY q.date_of_quiz DESC
        """, (chapter_id,))
    
    quizzes = cursor.fetchall()
    conn.close()
    
    return render_template('user_chapter.html', chapter=chapter, quizzes=quizzes, search_query=search_query)

@app.route('/api/subjects', methods=['GET'])
def api_subjects():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM subjects ORDER BY name")
    subjects = cursor.fetchall()
    conn.close()
    
    result = [{'id': s[0], 'name': s[1], 'description': s[2] or ''} for s in subjects]
    return jsonify(result)

@app.route('/api/chapters/<int:subject_id>', methods=['GET'])
def api_chapters(subject_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.description, COUNT(q.id) as quiz_count
        FROM chapters c
        LEFT JOIN quizzes q ON c.id = q.chapter_id
        WHERE c.subject_id = ?
        GROUP BY c.id
        ORDER BY c.name
    """, (subject_id,))
    chapters = cursor.fetchall()
    conn.close()
    
    result = [{'id': c[0], 'name': c[1], 'description': c[2] or '', 'quiz_count': c[3]} for c in chapters]
    return jsonify(result)

@app.route('/api/quizzes/<int:chapter_id>', methods=['GET'])
def api_quizzes(chapter_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.id, q.quiz_name, q.date_of_quiz, q.time_duration, q.remarks 
        FROM quizzes q
        WHERE q.chapter_id = ?
        ORDER BY q.date_of_quiz DESC
    """, (chapter_id,))
    quizzes = cursor.fetchall()
    conn.close()
    
    result = [{
        'id': q[0],
        'name': q[1],
        'date': q[2],
        'duration': q[3],
        'remarks': q[4] or ''
    } for q in quizzes]
    return jsonify(result)

@app.route('/api/user/scores', methods=['GET'])
def api_user_scores():
    # Check if user is logged in without redirecting
    if 'username' not in session:
        return jsonify({"error": "Authentication required"}), 401
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.id, s.quiz_id, q.quiz_name, s.time_stamp_of_attempt,
            ch.name as chapter_name, s.total_scored, s.total_questions,
            sub.id as subject_id, sub.name as subject_name,
            COALESCE((s.total_scored * 100.0 / NULLIF(s.total_questions, 0)), 0) as percentage
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        JOIN 
            chapters ch ON q.chapter_id = ch.id
        JOIN 
            subjects sub ON ch.subject_id = sub.id
        WHERE 
            s.user_id = (SELECT id FROM users WHERE username = ?)
        ORDER BY 
            s.time_stamp_of_attempt DESC
    """, (session['username'],))
    scores = cursor.fetchall()
    
    result = [{
        'id': s[0],
        'quiz_id': s[1],
        'quiz_name': s[2],
        'timestamp': s[3],
        'chapter_name': s[4],
        'score': s[5],
        'total_questions': s[6],
        'subject_id': s[7],
        'subject_name': s[8],
        'percentage': round(s[9], 2) if s[9] is not None else 0
    } for s in scores]
    return jsonify(result)

@app.route('/quiz/details/<int:quiz_id>')
@login_required
def quiz_details(quiz_id):
    if current_user.role != 'user':
        return redirect(url_for('home'))
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get quiz details
    cursor.execute("""
        SELECT q.id, q.quiz_name, q.date_of_quiz, q.time_duration, q.remarks,
               c.id as chapter_id, c.name as chapter_name,
               s.id as subject_id, s.name as subject_name
        FROM quizzes q
        JOIN chapters c ON q.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE q.id = ?
    """, (quiz_id,))
    quiz_data = cursor.fetchone()
    
    if not quiz_data:
        flash("Quiz not found", "error")
        return redirect(url_for('user_dashboard'))
    
    # Count questions in this quiz
    cursor.execute("SELECT COUNT(*) FROM questions WHERE quiz_id = ?", (quiz_id,))
    question_count = cursor.fetchone()[0]
    
    # Check if user has previous attempts
    cursor.execute("""
        SELECT id, total_scored, total_questions, time_stamp_of_attempt
        FROM scores 
        WHERE quiz_id = ? AND user_id = (SELECT id FROM users WHERE username = ?)
        ORDER BY time_stamp_of_attempt DESC LIMIT 1
    """, (quiz_id, session['username']))
    previous_attempt = cursor.fetchone()
    
    conn.close()
    
    return render_template('quiz_details.html', 
                          quiz=quiz_data,
                          chapter_id=quiz_data[5],
                          chapter_name=quiz_data[6],
                          subject_id=quiz_data[7],
                          subject_name=quiz_data[8],
                          question_count=question_count,
                          previous_attempt=previous_attempt)

@app.route('/api/user/dashboard_stats', methods=['GET'])
@login_required
def user_dashboard_stats():
    # Use Flask-Login's current_user instead of checking session
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get user ID directly from current_user
    user_id = current_user.id
    
    # Get recent attempts
    cursor.execute("""
        SELECT 
            q.quiz_name,
            s.total_scored,
            s.total_questions,
            ROUND((s.total_scored * 100.0 / s.total_questions), 2) as percentage,
            s.time_stamp_of_attempt,
            sub.name as subject_name
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        JOIN 
            chapters c ON q.chapter_id = c.id
        JOIN 
            subjects sub ON c.subject_id = sub.id
        WHERE 
            s.user_id = ?
        ORDER BY 
            s.time_stamp_of_attempt DESC
        LIMIT 5
    """, (user_id,))
    recent_attempts = [{
        'quiz_name': row[0],
        'score': row[1],
        'total': row[2],
        'percentage': row[3],
        'date': row[4],
        'subject_name': row[5]
    } for row in cursor.fetchall()]
    
    # Get subject performance
    cursor.execute("""
        SELECT 
            sub.name, 
            COUNT(s.id) as attempt_count,
            ROUND(AVG(s.total_scored * 100.0 / s.total_questions), 2) as avg_score
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        JOIN 
            chapters c ON q.chapter_id = c.id
        JOIN 
            subjects sub ON c.subject_id = sub.id
        WHERE 
            s.user_id = ?
        GROUP BY 
            sub.name
    """, (user_id,))
    subject_stats = [{
        'name': row[0],
        'attempts': row[1],
        'avg_score': row[2] if row[2] is not None else 0
    } for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'recent_attempts': recent_attempts,
        'subject_stats': subject_stats
    })

@app.route('/api/user/performance_stats', methods=['GET'])
@login_required
def user_performance_stats():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get timeline statistics (performance over time)
    cursor.execute("""
        SELECT 
            s.quiz_id,
            q.quiz_name,
            s.time_stamp_of_attempt as date,
            s.total_scored,
            s.total_questions,
            ROUND((s.total_scored * 100.0 / s.total_questions), 2) as score,
            ch.id as chapter_id,
            ch.name as chapter_name,
            sub.id as subject_id,
            sub.name as subject_name
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        JOIN 
            chapters ch ON q.chapter_id = ch.id
        JOIN 
            subjects sub ON ch.subject_id = sub.id
        WHERE 
            s.user_id = ?
        ORDER BY 
            s.time_stamp_of_attempt
    """, (current_user.id,))
    
    timeline_stats = [{
        'quiz_id': row[0],
        'quiz_name': row[1],
        'date': row[2],
        'scored': row[3],
        'total': row[4],
        'score': row[5],
        'chapter_id': row[6],
        'chapter_name': row[7],
        'subject_id': row[8],
        'subject_name': row[9]
    } for row in cursor.fetchall()]
    
    # Get subject statistics (aggregate performance by subject)
    cursor.execute("""
        SELECT 
            sub.id,
            sub.name,
            COUNT(s.id) as attempts,
            ROUND(AVG(s.total_scored * 100.0 / s.total_questions), 2) as avg_score,
            MAX(s.total_scored * 100.0 / s.total_questions) as best_score,
            MIN(s.total_scored * 100.0 / s.total_questions) as worst_score
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        JOIN 
            chapters ch ON q.chapter_id = ch.id
        JOIN 
            subjects sub ON ch.subject_id = sub.id
        WHERE 
            s.user_id = ?
        GROUP BY 
            sub.id
        ORDER BY 
            sub.name
    """, (current_user.id,))
    
    subject_stats = [{
        'id': row[0],
        'name': row[1],
        'attempts': row[2],
        'avg_score': row[3] if row[3] is not None else 0,
        'best_score': row[4] if row[4] is not None else 0,
        'worst_score': row[5] if row[5] is not None else 0
    } for row in cursor.fetchall()]
    
    # Get chapter statistics (aggregate performance by chapter)
    cursor.execute("""
        SELECT 
            ch.id,
            ch.name,
            sub.id as subject_id,
            COUNT(s.id) as attempts,
            ROUND(AVG(s.total_scored * 100.0 / s.total_questions), 2) as avg_score
        FROM 
            scores s
        JOIN 
            quizzes q ON s.quiz_id = q.id
        JOIN 
            chapters ch ON q.chapter_id = ch.id
        JOIN 
            subjects sub ON ch.subject_id = sub.id
        WHERE 
            s.user_id = ?
        GROUP BY 
            ch.id
        ORDER BY 
            ch.name
    """, (current_user.id,))
    
    chapter_stats = [{
        'id': row[0],
        'name': row[1],
        'subject_id': row[2],
        'attempts': row[3],
        'avg_score': row[4] if row[4] is not None else 0
    } for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'timeline_stats': timeline_stats,
        'subject_stats': subject_stats,
        'chapter_stats': chapter_stats
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)