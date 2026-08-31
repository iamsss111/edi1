# Environment Setup
**Project:** Online Examination Platform
**Document:** Environment Setup
**Version:** 1.0
**Backend:** Python + Flask
**Database:** MySQL
**Database Name:** `finaldb`
**ORM:** SQLAlchemy
**Authentication:** JWT
**Testing:** pytest

---

# 1. Purpose
This document defines the development environment required to build and run the Online Examination Platform.

The purpose of this setup is to ensure that all developers use a consistent environment and can independently clone, configure, run, and test the project.

The environment consists of:

- System prerequisites
- Python installation
- Python virtual environment
- Backend dependencies
- MySQL database
- `finaldb` database schema
- Environment variables
- Flask configuration
- Database configuration
- Testing tools
- Code-quality tools
- API testing tools
- Git configuration

---

# 2. System Prerequisites
The following software shall be installed before starting development.

SoftwarePurposePythonBackend developmentMySQL ServerDatabase serverMySQL WorkbenchDatabase managementGitVersion controlVS Code / PyCharmCode editor/IDEPostmanAPI testingThe development team should use compatible versions of Python and MySQL.

---

# 3. Python Version
The project shall use:

```
Python 3.12.x
```
Verify the installed version:

```
python --version
```
Expected output:

```
Python 3.12.x
```
All developers should use the same Python major/minor version.

---

# 4. MySQL Version
MySQL shall be used as the project's relational database management system.

The default local configuration shall be:

```
Host: localhost
Port: 3306
Database: finaldb
```
Verify that MySQL Server is installed and running before starting the Flask application.

---

# 5. Project Directory
The project shall follow the following basic structure:

```
online-examination-platform/
│
├── backend/
├── frontend/
├── database/
├── docs/
├── .gitignore
└── README.md
```
The Flask backend shall be located inside:

```
backend/
```

---

# 6. Python Virtual Environment
A separate Python virtual environment shall be used for the backend.

Navigate to the backend directory:

```
cd backend
```
Create the virtual environment:

```
python -m venv .venv
```

---

## 6.1 Activate Virtual Environment

### Windows

```
.venv\Scripts\activate
```

### Linux/macOS

```
source .venv/bin/activate
```
After activation, the terminal should display:

```
(.venv)
```

---

## 6.2 Verify Virtual Environment
Run:

```
python --version
```
and:

```
pip --version
```
The Python executable should point to the project's `.venv`.

### Windows

```
where python
```

### Linux/macOS

```
which python
```

---

# 7. Upgrade pip
After activating the virtual environment:

```
python -m pip install --upgrade pip
```

---

# 8. Backend Dependencies
The project shall use the following primary Python packages.

PackagePurposeFlaskBackend web frameworkFlask-SQLAlchemySQLAlchemy integration with FlaskFlask-MigrateDatabase migration supportPyMySQLMySQL database driverpython-dotenvLoading environment variablesFlask-JWT-ExtendedJWT authenticationMarshmallowRequest/response validation and serializationpytestAutomated testingBlackCode formattingRuffCode lintingisortImport sorting
---

# 9. Install Dependencies
With `.venv` activated, install the required packages:

```
pip install Flask Flask-SQLAlchemy Flask-Migrate PyMySQL python-dotenv Flask-JWT-Extended marshmallow pytest black ruff isort
```
Verify installation:

```
pip list
```

---

# 10. Requirements File
After installing the required packages, generate:

```
backend/requirements.txt
```
using:

```
pip freeze > requirements.txt
```
The `requirements.txt` file shall be committed to Git.

Another developer should be able to recreate the Python environment using:

```
pip install -r requirements.txt
```

---

# 11. Database Setup
The application shall use MySQL.

The project database shall be named:

```
finaldb
```
Create the database using MySQL Workbench or the MySQL command line.

```
CREATE DATABASE finaldb;
```
Select the database:

```
USE finaldb;
```

---

# 12. Database Schema
The finalized database schema shall be stored in:

```
database/schema.sql
```
The `schema.sql` file shall contain the finalized `finaldb` database structure.

The database schema shall include:

- Tables
- Primary keys
- Foreign keys
- Unique constraints
- NOT NULL constraints
- CHECK constraints where appropriate
- Indexes where required
- Relationships
The finalized `finaldb` schema shall be treated as the source of truth for the application's database structure.

---

# 13. Importing the Database Schema
After creating `finaldb`, execute:

```
database/schema.sql
```
using MySQL Workbench.

Alternatively, use the MySQL command line:

```
mysql -u root -p finaldb < database/schema.sql
```
Then verify:

```
USE finaldb;
SHOW TABLES;
```
The expected tables should appear.

---

# 14. Environment Variables
Environment-specific configuration shall be stored in a `.env` file.

The `.env` file shall contain configuration such as:

- Flask environment
- Application secret key
- JWT secret key
- Database host
- Database port
- Database name
- Database username
- Database password
The `.env` file shall **never be committed to Git**.

---

# 15. `.env` File
Create:

```
backend/.env
```
Use the following structure:

```
FLASK_ENV=development

SECRET_KEY=replace-with-local-secret-key
JWT_SECRET_KEY=replace-with-local-jwt-secret-key

DB_HOST=localhost
DB_PORT=3306
DB_NAME=finaldb
DB_USER=root
DB_PASSWORD=replace-with-local-mysql-password
```
Replace the placeholder values with the local developer's actual configuration.

---

# 16. `.env.example` File
Create:

```
backend/.env.example
```
Use:

```
FLASK_ENV=development

SECRET_KEY=
JWT_SECRET_KEY=

DB_HOST=localhost
DB_PORT=3306
DB_NAME=finaldb
DB_USER=
DB_PASSWORD=
```
The `.env.example` file shall be committed to Git.

It provides a template for other developers without exposing credentials.

---

# 17. `.env` Security Rules
The following rules shall always be followed:

### DO

```
Use environment variables for secrets.
Keep .env local.
Commit .env.example.
Use different credentials for different environments.
```

### DO NOT

```
Commit .env.
Hard-code database passwords.
Hard-code JWT secrets.
Hard-code application secret keys.
Share production credentials in the repository.
```

---

# 18. `.gitignore` Configuration
The project root `.gitignore` shall contain:

```
# Python
__pycache__/
*.py[cod]

# Virtual environment
.venv/
venv/
env/

# Environment variables
.env
.env.*
!.env.example

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log

# IDE
.vscode/
.idea/

# Operating system
.DS_Store
Thumbs.db
```
This prevents sensitive and generated files from being committed.

---

# 19. Flask Configuration
Application configuration shall be centralized.

The configuration module shall be located at:

```
backend/app/config/settings.py
```
The configuration shall read environment variables rather than hard-coded credentials.

The application configuration should include:

```
SECRET_KEY
JWT_SECRET_KEY
DATABASE configuration
Application environment
```

---

# 20. Database Configuration
SQLAlchemy shall obtain database configuration from environment variables.

The required variables are:

```
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```
The application shall use these values to establish a connection with:

```
MySQL → finaldb
```
The database credentials shall not be written directly into Python source code.

---

# 21. Application Factory Configuration
The Flask application shall use the application factory pattern.

The general application startup flow shall be:

```
run.py
   ↓
create_app()
   ↓
Load environment configuration
   ↓
Initialize Flask extensions
   ↓
Initialize SQLAlchemy
   ↓
Initialize JWT
   ↓
Register API routes
   ↓
Return Flask application
```
The application factory shall be located in:

```
backend/app/__init__.py
```

---

# 22. Application Entry Point
The backend shall have:

```
backend/run.py
```
The entry point shall create the Flask application using the application factory.

General structure:

```
run.py
   ↓
create_app()
   ↓
Flask Application
```
The application should be started using:

```
python run.py
```

---

# 23. Development Server
During development, the Flask application shall run locally.

Default address:

```
http://127.0.0.1:5000
```
The exact host and port may be configured through the project configuration if required.

---

# 24. Health Check Endpoint
A basic health-check endpoint should be implemented before starting feature development.

Endpoint:

```
GET /api/v1/health
```
Expected response:

```
{
    "success": true,
    "message": "Online Examination Platform API is running"
}
```
This endpoint is used to confirm that the Flask backend is running correctly.

---

# 25. Database Connection Verification
The database connection shall be tested after the Flask application is configured.

Verification flow:

```
Flask Application
       ↓
SQLAlchemy
       ↓
MySQL
       ↓
finaldb
```
The application should successfully connect to `finaldb` before feature development begins.

---

# 26. Development Tools
The following tools shall be installed in the virtual environment.

### Black
Used for code formatting.

```
black .
```

### Ruff
Used for code-quality and lint checks.

```
ruff check .
```

### isort
Used for import sorting.

```
isort .
```

### pytest
Used for automated tests.

```
pytest
```

---

# 27. Code Formatting Verification
Before pushing code, run:

```
black .
```
This ensures Python files follow the project's formatting standard.

---

# 28. Linting Verification
Run:

```
ruff check .
```
Developers should resolve relevant linting errors before creating a pull request.

---

# 29. Import Sorting Verification
Run:

```
isort .
```
This ensures imports are consistently organized.

---

# 30. Testing Verification
Run:

```
pytest
```
All relevant tests should pass before merging feature branches into `develop`.

---

# 31. API Testing Environment
Postman shall be used for API testing during development.

Initial API testing should verify:

```
GET /api/v1/health
```
As development progresses, API collections should be maintained for:

```
Authentication
Users
Questions
Exams
Assignments
Attempts
Answers
Results
Proctoring
Notifications
Administration
```

---

# 32. Testing Database
A separate database should be used for automated testing where database modification is required.

Development:

```
finaldb
```
Testing:

```
finaldb_test
```
Tests should not intentionally modify or delete important development data.

The testing database configuration shall be introduced when database-dependent automated tests are implemented.

---

# 33. Development Environment
The initial development environment shall be:

```
Environment: Development
Database: finaldb
Database Host: localhost
Database Port: 3306
Flask Host: 127.0.0.1
Flask Port: 5000
```

---

# 34. Environment Reproducibility
Both developers must be able to independently recreate the development environment.

The expected setup process is:

```
Clone repository
      ↓
Install Python
      ↓
Create .venv
      ↓
Activate .venv
      ↓
Install requirements.txt
      ↓
Create .env
      ↓
Create finaldb
      ↓
Apply schema.sql
      ↓
Run Flask
      ↓
Test health endpoint
```
No developer should need another developer's `.env` file or virtual environment.

---

# 35. New Developer Setup
A new developer joining the project shall follow these steps.

### Step 1
Clone the repository:

```
git clone <repository-url>
```

### Step 2
Navigate into the project:

```
cd online-examination-platform
```

### Step 3
Navigate to backend:

```
cd backend
```

### Step 4
Create the virtual environment:

```
python -m venv .venv
```

### Step 5
Activate it.

Windows:

```
.venv\Scripts\activate
```
Linux/macOS:

```
source .venv/bin/activate
```

### Step 6
Install dependencies:

```
pip install -r requirements.txt
```

### Step 7
Create `.env` from `.env.example`.

Windows:

```
copy .env.example .env
```
Linux/macOS:

```
cp .env.example .env
```

### Step 8
Configure the database credentials inside `.env`.

### Step 9
Create MySQL database:

```
CREATE DATABASE finaldb;
```

### Step 10
Execute:

```
database/schema.sql
```

### Step 11
Run the backend:

```
python run.py
```

### Step 12
Test:

```
GET /api/v1/health
```

---

# 36. Environment Setup Verification Checklist
Each developer shall verify the following:

```
[ ] Python is installed
[ ] Correct Python version is being used
[ ] MySQL Server is installed
[ ] MySQL Server is running
[ ] Git is installed
[ ] Repository has been cloned
[ ] Virtual environment has been created
[ ] Virtual environment is activated
[ ] requirements.txt has been installed
[ ] Black is installed
[ ] Ruff is installed
[ ] isort is installed
[ ] pytest is installed
[ ] .env has been created
[ ] .env contains valid local configuration
[ ] .env is ignored by Git
[ ] .env.example exists
[ ] finaldb has been created
[ ] schema.sql has been executed
[ ] finaldb tables are available
[ ] Flask application starts successfully
[ ] Database connection works
[ ] Health-check endpoint works
[ ] API can be tested through Postman
```

---

# 37. Final Environment Structure
After completing the environment setup, the relevant project structure should look like:

```
online-examination-platform/
│
├── backend/
│   │
│   ├── .venv/                 # Not committed
│   ├── .env                   # Not committed
│   ├── .env.example           # Committed
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   │
│   │   ├── extensions/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
│
├── database/
│   └── schema.sql
│
├── docs/
│   ├── coding-conventions.md
│   └── environment-setup.md
│
├── frontend/
│
├── .gitignore
└── README.md
```

---

# 38. Environment Setup Rules
The following rules are mandatory:

1. Every developer shall use the project's specified Python version.
2. Every developer shall use a project-specific virtual environment.
3. Dependencies shall be installed from `requirements.txt`.
4. Database configuration shall use environment variables.
5. Secrets shall never be hard-coded.
6. `.env` shall never be committed.
7. `.env.example` shall be maintained and committed.
8. `finaldb` shall follow the finalized database schema.
9. The development database shall be locally configured for each developer.
10. Database-dependent tests shall use a separate testing database where required.
11. Code-quality tools shall be used before committing code.
12. The application shall be verified locally before creating a pull request.

---

# 39. Definition of Environment Setup Complete
The environment setup shall be considered complete when:

```
Python
   ↓
Virtual Environment
   ↓
Dependencies
   ↓
Environment Variables
   ↓
Flask Application
   ↓
SQLAlchemy
   ↓
MySQL
   ↓
finaldb
   ↓
Health Check
```
works successfully on both developers' machines.

Both developers should be able to clone the repository and reproduce the development environment without receiving another developer's private configuration files.

---

# 40. Environment Setup Completion Checklist

```
ENVIRONMENT SETUP — FINAL CHECK

[ ] Python installed
[ ] Python version confirmed
[ ] MySQL installed
[ ] MySQL Server running
[ ] Git installed
[ ] Project repository created/cloned
[ ] Project folders created
[ ] .gitignore configured
[ ] .venv created
[ ] .venv activated
[ ] pip upgraded
[ ] Flask installed
[ ] SQLAlchemy installed
[ ] Flask-Migrate installed
[ ] PyMySQL installed
[ ] python-dotenv installed
[ ] Flask-JWT-Extended installed
[ ] Marshmallow installed
[ ] pytest installed
[ ] Black installed
[ ] Ruff installed
[ ] isort installed
[ ] requirements.txt generated
[ ] finaldb created
[ ] schema.sql created
[ ] schema.sql executed
[ ] .env created
[ ] .env.example created
[ ] .env added to .gitignore
[ ] Flask configuration created
[ ] SQLAlchemy configuration created
[ ] JWT configuration created
[ ] Application factory created
[ ] run.py created
[ ] Health-check endpoint created
[ ] Flask application runs
[ ] Database connection verified
[ ] Health endpoint tested
[ ] Postman configured
[ ] Both developers verified the setup
[ ] Environment setup documented in README

STATUS: READY FOR FEATURE DEVELOPMENT
```

---

# End of Environment Setup Document