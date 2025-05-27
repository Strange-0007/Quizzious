import sqlite3
import bcrypt

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Creatoing Users Table using execute method
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,  -- This will be the email
            full_name TEXT,
            qualification TEXT,
            dob DATE,
            password TEXT,
            role TEXT
        )
    ''')
    admin_password = 'admin'  # Plain text password
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

    # Insert admin user with hashed password this hashing is for security purposes it seems .... need to learn how it works
    cursor.execute("INSERT OR IGNORE INTO users (username, full_name, qualification, dob, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
                   ('admin@gmail.com', 'admin', 'admin', '10-09-2002', hashed_password, 'admin'))  # Change 'admin_password' to a secure password
 # Change 'admin_password' to a secure password 

    
    # Creating Subjects Table to store subjects with subject id as primary key and name is compulsary
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            additional_fields TEXT
        )
    ''')

    # Creating Chapters Table to store chapters with chapter id as primary key and name is compulsary
    # subject_id is a foreign key to subjects table that refernces id column of subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            additional_fields TEXT,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')

    # Creating Quizzes Table to store quizzes with quiz id as primary key and quiz_name, chapter_id, date_of_quiz, time_duration are compulsary
    # chapter_id is a foreign key to chapters table that refernces id column of chapters table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_name TEXT NOT NULL,
    chapter_id INTEGER NOT NULL,
    date_of_quiz DATE NOT NULL,
    time_duration INTEGER NOT NULL,  -- Change to INTEGER to store total minutes
    remarks TEXT,
    FOREIGN KEY (chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
)
''')

    # Creating Questions Table to store questions with question id as primary key and quiz_id, question_statement, option1, option2, option3, option4, correct_option are compulsary
    # quiz_id is a foreign key to quizzes table that refernces id column of quizzes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            question_statement TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT,
            option4 TEXT,
            correct_option INTEGER, -- This will store the index of the correct option (1-4)
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        )
    ''')

    # Creating Scores Table to store scores with score id as primary key and quiz_id, user_id, time_stamp_of_attempt, total_scored, total_questions are compulsary
    # quiz_id is a foreign key to quizzes table that refernces id column of quizzes table
    # user_id is a foreign key to users table that refernces id column of users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            user_id INTEGER,
            time_stamp_of_attempt DATETIME,
            total_scored INTEGER,
            total_questions INTEGER,
            additional_fields TEXT,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Creating Question Responses Table to store user responses to questions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            user_answer INTEGER NOT NULL,
            FOREIGN KEY (score_id) REFERENCES scores (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')

#commit the changes to database and close the connection to database
    conn.commit()
    conn.close()
