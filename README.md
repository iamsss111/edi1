# Online Examination Platform

A web-based Online Examination Platform designed to manage users, examinations, questions, exam attempts, evaluation, results, and examination monitoring.

---

# 1. Project Overview

The Online Examination Platform provides a centralized system for conducting and managing online examinations.

The platform is designed to support different users and responsibilities within the examination process.

The major functional areas include:


Authentication & User Management
Question Bank
Exam Management
Exam Assignment
Exam Attempt
Evaluation & Results
Proctoring & Suspicious Activity
Notifications
Administration & Reporting


# 2. Technology Stack

## Backend
Python
Flask
SQLAlchemy
Flask-Migrate
JWT Authentication


## Database
MySQL
Database: finaldb


## Testing
pytest


## Code Quality
Black
Ruff
isort


## API Testing
Postman


## Version Control
Git
GitHub


---

# 3. Project Structure
online-examination-platform/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── config/
│   │   ├── extensions/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   │
│   ├── tests/
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
│
├── database/
│   └── schema.sql
│
├── docs/
│   ├── coding-conventions.md
│   ├── environment-setup.md
│   └── ...
│
├── frontend/
│
├── .gitignore
└── README.md


# 4. Prerequisites
Install the following before starting development:
Python 3.12.x
MySQL Server
MySQL Workbench
Git
VS Code / PyCharm
Postman


# 5. Clone the Repository
Clone the repository:
git clone <repository-url>


Navigate into the project:
cd online-examination-platform


# 6. Backend Setup
Navigate to the backend:
cd backend


---

# 7. Create Python Virtual Environment
Create the virtual environment:
python -m venv .venv


---

# 8. Activate Virtual Environment

### Windows
.venv\Scripts\activate


### Linux/macOS
source .venv/bin/activate


After activation, the terminal should display:
(.venv)


---

# 9. Install Dependencies

Upgrade pip:
python -m pip install --upgrade pip


Install project dependencies:
pip install -r requirements.txt


---

# 10. Environment Configuration

Create a `.env` file inside the backend directory.
Copy:
.env.example

to:
.env


### Windows
copy .env.example .env

### Linux/macOS
cp .env.example .env


---

# 11. Configure `.env`

The `.env` file should contain:

FLASK_ENV=development

SECRET_KEY=replace-with-local-secret-key
JWT_SECRET_KEY=replace-with-local-jwt-secret-key

DB_HOST=localhost
DB_PORT=3306
DB_NAME=finaldb
DB_USER=root
DB_PASSWORD=replace-with-local-mysql-password


Do not commit `.env` to Git.

---

# 12. Database Setup

The project uses:
Database: finaldb
Host: localhost
Port: 3306


Create the database:
CREATE DATABASE finaldb;

Select the database:
USE finaldb;

---

# 13. Apply Database Schema

The finalized database schema is located at:
database/schema.sql
Execute the schema using MySQL Workbench.

Verify the database:
USE finaldb;
SHOW TABLES;

The finalized `finaldb` schema shall be treated as the source of truth for the application database.

---

# 14. Run the Backend

From the backend directory, with the virtual environment activated:
python run.py


The development server should start locally.

Default address:
http://127.0.0.1:5000


---

# 15. Health Check

Verify that the backend is running.

Endpoint:
GET /api/v1/health


Expected response:
{
    "success": true,
    "message": "Online Examination Platform API is running"
}


This confirms that the Flask application is running.

---

# 16. Database Connection

The application connects to:
Flask
   ↓
SQLAlchemy
   ↓
PyMySQL
   ↓
MySQL
   ↓
finaldb

Database credentials are loaded from `.env`.

Database credentials must never be hard-coded into the application source code.

---

# 17. Code Formatting

The project uses Black.

Run:
black .


---

# 18. Linting

The project uses Ruff.

Run:
ruff check .


---

# 19. Import Sorting

The project uses isort.

Run:
isort .


---

# 20. Testing

The project uses pytest.

Run:
pytest


All tests should pass before code is merged into the development branch.

---

# 21. Git Branching Strategy

The project follows:
main
  ↓
develop
  ↓
feature branches


Major feature branches should follow:
feature/<feature-name>


Examples:
feature/authentication-users
feature/question-bank
feature/exam-management
feature/exam-assignment
feature/exam-attempt
feature/evaluation-results
feature/proctoring
feature/notifications
feature/admin-reporting


Bug fixes should use:
fix/<issue-name>


Example:
fix/exam-timer


---

# 22. Commit Convention

Commit messages should use the following prefixes:
feat:
fix:
refactor:
test:
docs:
chore:


Examples:
feat: implement exam creation
fix: resolve exam timer issue
test: add exam service tests
docs: update environment setup
refactor: simplify result calculation
chore: update dependencies


---

# 23. Coding Conventions

All developers shall follow the project's coding conventions.
The complete coding standards are documented in:
docs/coding-conventions.md


Developers should review this document before implementing features.

---

# 24. Environment Setup Documentation

Complete environment setup instructions are available at:
docs/environment-setup.md


This document explains:
Python installation
Virtual environment
Dependencies
MySQL
finaldb
.env
Flask configuration
Database configuration
Testing tools
Code-quality tools


---

# 25. Security Rules

The following rules are mandatory:
[ ] Never commit .env
[ ] Never hard-code passwords
[ ] Never hard-code JWT secrets
[ ] Never commit API secrets
[ ] Never store plain-text passwords
[ ] Never expose sensitive information in API responses
[ ] Never commit the .venv directory


---

# 26. Development Workflow

The standard development workflow is:
Pull latest develop
       ↓
Create feature branch
       ↓
Implement feature
       ↓
Write/update tests
       ↓
Run Black
       ↓
Run isort
       ↓
Run Ruff
       ↓
Run pytest
       ↓
Commit changes
       ↓
Push feature branch
       ↓
Create Pull Request
       ↓
Code Review
       ↓
Merge into develop


---

# 27. Backend Architecture

The backend follows layered architecture:
Client
   ↓
Routes
   ↓
Schemas / Validation
   ↓
Services
   ↓
Repositories
   ↓
Models / SQLAlchemy
   ↓
MySQL
   ↓
finaldb


Responsibilities:

### Routes

Handle HTTP requests and responses.

### Schemas

Validate and serialize request/response data.

### Services

Contain business logic.

### Repositories

Handle database operations.

### Models

Represent database entities and relationships.

---

# 28. API Structure

The API uses versioning:
/api/v1/


Example endpoints:
/api/v1/auth
/api/v1/users
/api/v1/questions
/api/v1/exams
/api/v1/assignments
/api/v1/attempts
/api/v1/results
/api/v1/proctoring


---

# 29. Project Database

The project's finalized database is:
finaldb


Database changes must follow the approved database design.
Developers should not independently modify the database structure without agreement from the development team.

---

# 30. Troubleshooting

## Virtual environment not activated

Windows:
.venv\Scripts\activate


Linux/macOS:
source .venv/bin/activate


---

## Dependencies missing

Run:
pip install -r requirements.txt


---

## Database connection failure

Verify:
MySQL Server is running
DB_HOST is correct
DB_PORT is correct
DB_NAME is finaldb
DB_USER is correct
DB_PASSWORD is correct


---

## Flask application not starting

Verify:
Virtual environment is active
Dependencies are installed
.env exists
Configuration is correct
run.py exists


Then run:
python run.py


---

# 31. Developer Setup Checklist

[ ] Repository cloned
[ ] Python 3.12.x installed
[ ] MySQL installed and running
[ ] Backend directory accessed
[ ] .venv created
[ ] .venv activated
[ ] Dependencies installed
[ ] .env created
[ ] .env configured
[ ] finaldb created
[ ] schema.sql executed
[ ] Flask application started
[ ] Database connection verified
[ ] Health endpoint tested
[ ] Postman configured
[ ] pytest executed
[ ] Black executed
[ ] Ruff executed
[ ] isort executed


---

# 32. Project Status

The project is currently under active development.

Development should follow the project's:
Requirements
↓
Database Design
↓
Architecture
↓
Coding Conventions
↓
Environment Setup
↓
Feature Development
↓
Testing
↓
Integration
↓
Deployment

---

# 33. Documentation

Project documentation is maintained inside:
docs/


Important documents include:
docs/
├── coding-conventions.md
├── environment-setup.md
└── ...


All developers should update relevant documentation when making significant architectural or functional changes.

---

# 34. Support

For development issues, developers should first verify:
1. Python version
2. Virtual environment
3. Dependencies
4. .env configuration
5. MySQL server
6. finaldb
7. Flask configuration
8. Application logs


Only after these checks should the issue be escalated to the development team.

---

# End of README
