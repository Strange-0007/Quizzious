# Quizzious-App  
*A simple exam preparation site for students*

## Milestone 1: Database Models and Schema Setup

### Key Implementation Details
- Implemented bcrypt for secure password hashing
- Programmatic table creation using SQLAlchemy
- Flask-Login integration with session management
- Basic template structure without CSS/JS (styling postponed)

---

## Application Structure

```

project-root/
├── app.py            \# Contains routes and core logic
├── templates/        \# HTML templates
│   ├── admin/        \# Admin dashboard templates
│   └── user/         \# User interface templates
├── static/           \# Static files (CSS/JS/images)
└── database.db       \# SQLite database file

```

---

## Database Schema

### Tables Overview

**users**  
```

id: Integer (Primary Key)
username: String (Unique, Email)
full_name: String
qualification: String
dob: Date
password: String (Hashed)
role: String (admin/user)

```

**subjects**  
```

id: Integer (Primary Key)
name: String
description: Text

```

**chapters**  
```

id: Integer (Primary Key)
subject_id: Integer (Foreign Key)
name: String
description: Text

```

**quizzes**  
```

id: Integer (Primary Key)
quiz_name: String
chapter_id: Integer (Foreign Key)
date_of_quiz: DateTime
time_duration: Integer (minutes)
remarks: Text

```

**questions**  
```

id: Integer (Primary Key)
quiz_id: Integer (Foreign Key)
question_statement: Text
option1: String
option2: String
option3: String
option4: String
correct_option: Integer (1-4)

```

**scores**  
```

id: Integer (Primary Key)
quiz_id: Integer (Foreign Key)
user_id: Integer (Foreign Key)
time_stamp_of_attempt: DateTime
total_scored: Integer
total_questions: Integer

```

---
## Milestone 2:  Authentication and Role Management

## Security Implementation
- **Password Encryption**: Bcrypt with salt rounds
- **Session Management**: Flask-Login with cookie-based sessions
- **Secret Key**: `guess_me_if_u_can` (temporary development value)

---

## Current Features
- Role-based access control (Admin/User)
- Separate dashboards for users and admins
- Basic CRUD operations through web interface
- Quiz attempt tracking
- Logout functionality

---

## Temporary Configurations
```


# app.py excerpt

app.secret_key = 'guess_me_if_u_can'  \# Development-only key

```

---

## Pending Tasks
- [ ] CSS/JavaScript integration
- [ ] Input validation improvements
- [ ] Error handling pages
- [ ] Password recovery system
- [ ] Quiz timer implementation

---

## Development Notes
- Test data inserted via Flask shell
- Database relationships managed through SQLAlchemy ORM
- Basic Jinja2 template inheritance implemented
- Session timeout set to browser close

## Milestone 3: Admin Dashboard Enhancements

### Core Admin Functionalities
- **Subject Management**: Full CRUD operations through web interface
- **Chapter Organization**: Nested chapter management within subjects
- **Quiz Configuration**: Time-bound quiz setup with chapter association
- **Question Bank**: Multiple-choice management with answer validation
- **User Monitoring**: Read-only access to user profiles and attempt history

### Technical Implementation
- **Route Protection**: Custom `@admin_required` decorator using functools.wraps
- **Efficient Routing**: Flask redirects with flashed error messages for unauthorized access
- **Dynamic Forms**: Jinja2-generated forms with conditional rendering
- **Bulk Operations**: Batch question insertion via CSV upload (basic implementation)


### Security Measures
- Role verification before database write operations
- Session validation for all admin endpoints
- Server-side validation for all CRUD operations
- Atomic transactions for data integrity

### personal note :
 - Used wraps….
 - Added templates for all admin functionalities without any design 
 - The functionalities works
 - Used wraps for efficient redirecting





## Milestone 4: User Dashboard and Quiz System

### Core User Features
- **Subject Navigation**: Hierarchical view of Subjects > Chapters > Quizzes
- **Timed Assessments**: JavaScript countdown timer synchronized with server duration
- **Instant Feedback**: Color-coded answer review post-submission
- **Performance Tracking**: Historical score visualization with attempt metadata

### Quiz Engine Implementation
- **Timer System**: JavaScript `setTimeout` with form auto-submit
- **Answer Validation**: Server-side option verification before scoring
- **Atomic Attempts**: Database transactions for score integrity
- **Anti-Cheat Measures**: 
  - Disabled browser context menu
  - Prevented multiple quiz instances

### personal note :
 - implemented timers
 - Added templates for all user  functionalities without any design 
 - The functionalities works


## Milestone 5: Score Management and Quiz Result Display

### Changes made 
- **user-score page**: this page has been updated such that it shows statistic of past quizzes

### personal note
- js was bit tricky to implement
- chart js was giving an issue ... which works now
- functionality final test ... works ok !

## Milestone 6: Search Functionality for Admin and Users

### Changes made 
- **user-page hierarchy**: updated user redirection flow for simplicity and less clutterimg.
- **search functionality**: search functionality is impplemented for respective pages and content is loaded according to that.

### personal note
- after quiz attempt , redirected to quiz selection page while showing the score.
- Was able to go to quiz page by going to previous page from users pov ... need to fix it.
- database data inconsistency arised ... must be fixed later
- search functionality works as expected.

## Milestone 7: Quiz Time and Duration Management

### Changes made 
- **Time limit implementation**: Deadline time for quiz submission is implemented.
- **score display and answer description**: Reveals the true answers after sumbission or post deadline.
- form protection and dashboard only reattempts have been added to fix unambiguity
  
### personal note
- Database inconsisty is fixed to my knowledge.
- previous page at compromising pages is redirected through dashboard.
- time limit and DB Query revamp and navigation flow works as intended.

## Milestone 8: API Development for Data Access

### Changes made 
- **Api access endpoints**: Added API endpoints to fetch subjects, chapters, quizzes, and scores.

### Issues encountered
- while adding api access for scores, anyyone would be able to access the scores which is bad.
- jsonify wasn't being imported for some reason

### Fixes
- session management was implemented along with api response to session id-less request as invalid.
- verified the working of API using curl.

## Milestone 9: Summary Charts and Data Visualization

### Changes made 
- **Charts**: chart.js, canvas and javascript was used to display the data.

### Issues encountered
- api endpoint for retrieving data for chart rendering was an issue.

### Fixes
- had to revamp api endpoints ... used ai suppport for clarification.

## Milestone 10: Frontend Enhancements and UI Improvements

### Changes made 
- **UI**: Found all the pages and modified the conntent and made it less cluttered along with bootstrapping.


### Issues encountered
- api endpoint for retrieving data for chart rendering was an issue again.
- After the modification of bootstrap UI rendering got affected.
- the successive quiz attempts were not being stored.
- the sessions had a BUG
  
### Fixes
- had to revamp api endpoints.
- used JS to load charts more effectively.
- changed the website to display scores and store scores so that the problem could be made with seperation of concerns in mind.
- fixed the session BUG.

### personal note
- All functionalities have been tested and is working fine.

## Milestone 11: Security Enhancements and Final Testing

### Changes made 
- **Backend Validation**: Added backend validation for all forms.
- **Bug Fixes**: Fixed Db date time bug, routing and session handling bugs.
- **Route protection**: all routes are now protected and requires session token and required role to access them.
- **Modularity enhancement**: modularity is maintained by seperating css and js from the templates to static folder.


### Issues encountered
- login and registration form validation created an issue.
- the js files were crosslinked due to some isue.
- the successive quiz attempts were not being stored and timer stopped working.
  
### Fixes
- the validation was fixed by seperating code and chnaging DOM structure.
- changed the api endpoint jsonify to include time too.

### personal note
- All functionalities have been tested and is working fine.

  
  
