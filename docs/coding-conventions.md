# Coding Conventions
**Project:** Online Examination Platform
**Document:** Coding Conventions
**Version:** 1.0
**Status:** Approved for Development
**Backend:** Python + Flask
**Database:** MySQL (`finaldb`)
**ORM:** SQLAlchemy
**Testing:** pytest

---

# 1. Purpose
This document defines the coding standards, naming conventions, architectural rules, formatting rules, error-handling practices, database conventions, API conventions, Git conventions, and code-quality requirements for the Online Examination Platform.

The primary purpose of these conventions is to ensure that:

- Code written by different developers follows the same structure and style.
- The project remains readable and maintainable.
- Developers can understand and modify each other's code easily.
- Business logic remains separated from API and database logic.
- Database and API naming remains consistent.
- Code quality can be checked automatically.
- Future developers can continue development without having to learn individual coding styles.
All developers contributing to the project shall follow these conventions.

---

# 2. General Development Principles
The following principles shall be followed throughout the project.

## 2.1 Readability
Code shall be written primarily for readability and maintainability.

Prefer:

```
total_marks = calculate_total_marks(answers)
```
over:

```
tm = calc(a)
```
Variable and function names should clearly communicate their purpose.

---

## 2.2 Simplicity
Code should be kept as simple as reasonably possible.

Developers should avoid:

- unnecessary abstractions
- unnecessary classes
- duplicated logic
- overly complex functions
- unnecessary dependencies
- premature optimization
Complexity should only be introduced when it provides a clear benefit.

---

## 2.3 Single Responsibility
Each class, function, module, and layer should have a clearly defined responsibility.

For example:

```
Route
    ↓
Handles HTTP request/response

Service
    ↓
Handles business logic

Repository
    ↓
Handles database operations

Model
    ↓
Represents database entities
```
A route should not directly contain complex business logic or database queries.

---

## 2.4 Don't Repeat Yourself
Repeated business logic should be centralized.

If the same logic is required in multiple locations, it should generally be moved to an appropriate service or utility function.

---

## 2.5 Security by Default
Security-related requirements shall be considered during implementation rather than added at the end.

Developers shall:

- never store plain-text passwords
- never hard-code credentials
- validate input
- verify authorization
- protect authenticated endpoints
- avoid exposing sensitive information
- use parameterized/ORM queries
- keep secrets outside source control

---

# 3. Technology Standards
The project shall follow the following technology standards.

AreaStandardProgramming LanguagePythonBackend FrameworkFlaskDatabaseMySQLORMSQLAlchemyAPI StyleRESTful APIAuthenticationJWT-based authenticationTestingpytestCode FormattingBlackLintingRuffImport SortingisortEnvironment Configuration`.env`Version ControlGitRepository HostingGitHubAll developers should use compatible versions of the project's dependencies as specified in `requirements.txt`.

---

# 4. Project Structure
The backend shall follow the established layered structure.

```
backend/
│
├── app/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── extensions/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── models/
│   │   └── __init__.py
│   │
│   ├── routes/
│   │   └── __init__.py
│   │
│   ├── services/
│   │   └── __init__.py
│   │
│   ├── repositories/
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   └── utils/
│       └── __init__.py
│
├── tests/
│   └── __init__.py
│
├── run.py
├── requirements.txt
├── .env
└── .env.example
```
Additional modules may be added when required, but the established architecture shall not be unnecessarily changed.

---

# 5. File Naming Conventions
Python files shall use lowercase `snake_case`.

### Correct

```
user_service.py
exam_service.py
exam_repository.py
question_routes.py
result_service.py
database.py
```

### Incorrect

```
UserService.py
userService.py
Exam-Service.py
EXAM_SERVICE.py
```
File names should describe their purpose clearly.

---

# 6. Folder Naming Conventions
Folder names shall use lowercase names.

Examples:

```
models/
services/
repositories/
routes/
schemas/
utils/
config/
extensions/
tests/
```
Avoid inconsistent capitalization such as:

```
Models/
Services/
Routes/
```

---

# 7. Class Naming Conventions
Classes shall use PascalCase.

### Correct

```
class UserService:
    pass

class ExamRepository:
    pass

class ExamAttempt:
    pass
```

### Incorrect

```
class userService:
    pass

class exam_repository:
    pass
```
Class names should normally be nouns representing the object or responsibility.

---

# 8. Function and Method Naming
Functions and methods shall use lowercase `snake_case`.

### Correct

```
def create_exam():
    pass

def get_exam_by_id(exam_id):
    pass

def calculate_result(attempt_id):
    pass

def submit_exam(attempt_id):
    pass
```
Function names should normally begin with a meaningful verb.

Common prefixes include:

```
create_
get_
find_
update_
delete_
validate_
calculate_
assign_
submit_
publish_
check_
```

---

# 9. Variable Naming
Variables shall use lowercase `snake_case`.

### Correct

```
exam_id = 101
student_id = 25
total_marks = 50
exam_duration = 60
attempt_count = 1
```

### Incorrect

```
ExamID = 101
studentId = 25
tm = 50
x = 60
```
Variable names should describe the data they contain.

---

# 10. Boolean Naming
Boolean variables should use names that clearly communicate a true/false state.

Prefer:

```
is_active
is_published
is_completed
has_attempted
is_authenticated
```
Avoid:

```
active
publish
complete
```
when the meaning could be ambiguous.

---

# 11. Constant Naming
Constants shall use uppercase `SNAKE_CASE`.

Example:

```
MAX_EXAM_DURATION = 180
DEFAULT_PAGE_SIZE = 20
JWT_EXPIRATION_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5
```
Constants should not be repeatedly hard-coded throughout the application.

---

# 12. Type Hints
Type hints should be used where they improve readability and maintainability.

Example:

```
def get_exam_by_id(exam_id: int) -> Exam | None:
    ...
```
For collections:

```
def get_exam_ids() -> list[int]:
    ...
```
Type hints are especially encouraged for:

- service methods
- repository methods
- utility functions
- functions with complex parameters or return values

---

# 13. Import Conventions
Imports shall be organized into three groups:

1. Standard library
2. Third-party libraries
3. Project/application imports
Example:

```
import logging
from datetime import datetime

from flask import Blueprint, jsonify, request

from app.services.exam_service import ExamService
from app.utils.exceptions import ValidationError
```
Unused imports shall be removed.

Import ordering should be automatically maintained using `isort`.

---

# 14. Code Formatting
The project shall use **Black** as the standard Python formatter.

Indentation shall use:

```
4 spaces
```
Tabs shall not be used for Python indentation.

Example:

```
def create_exam(data):
    if not data:
        return None

    return exam_service.create_exam(data)
```
Developers should not manually format code differently from the project's configured formatter.

---

# 15. Line Length
Code should follow the line-length configuration established by the project's formatter and linter.

Long statements should preferably be broken into readable sections rather than forcing developers to read excessively long lines.

Example:

```
exam = exam_service.create_exam(
    student_id=student_id,
    exam_id=exam_id,
    start_time=start_time,
)
```

---

# 16. Comments
Comments should explain **why** something is done when the reason is not obvious.

Avoid comments that simply repeat the code.

### Poor example

```
# Add 1 to count
count += 1
```

### Better example

```
# Prevent duplicate attempts for the same scheduled examination.
if existing_attempt:
    raise DuplicateAttemptError()
```
Comments should be kept accurate when the related code changes.

---

# 17. Docstrings
Public classes and functions should have docstrings where their purpose is not immediately obvious.

Example:

```
def calculate_result(attempt_id: int) -> Result:
    """Calculate and store the result for a completed exam attempt."""
```
Docstrings should describe:

- purpose
- important parameters where necessary
- return value where useful
- important exceptions where applicable

---

# 18. Layered Architecture
The backend shall follow the following general flow:

```
Client
   ↓
Route / Controller
   ↓
Schema / Validation
   ↓
Service
   ↓
Repository
   ↓
SQLAlchemy / Database
   ↓
finaldb
```
Each layer shall have a defined responsibility.

---

# 19. Route Layer Conventions
Routes are responsible for handling HTTP requests and responses.

Routes may:

- receive HTTP requests
- extract request data
- perform/request schema validation
- call services
- return HTTP responses
- return appropriate HTTP status codes
Routes should not contain complex business logic.

### Preferred

```
@exam_bp.post("/exams")
def create_exam():
    data = request.get_json()

    exam = exam_service.create_exam(data)

    return jsonify(exam), 201
```

### Avoid

```
@exam_bp.post("/exams")
def create_exam():
    # Multiple database queries
    # Business rules
    # Mark calculations
    # Authorization logic
    # Complex validation
    # Transaction management
    # Response construction
```
Complex logic should be moved to the appropriate service/repository layer.

---

# 20. Service Layer Conventions
The service layer contains business logic.

Examples:

```
ExamService
QuestionService
AttemptService
ResultService
AuthenticationService
ProctoringService
```
Services may:

- apply business rules
- coordinate multiple repositories
- validate business conditions
- perform calculations
- manage business transactions where appropriate
Example:

```
class ExamService:

    def create_exam(self, data):
        self.validate_exam_data(data)

        exam = self.exam_repository.create(data)

        return exam
```
Business rules should not be duplicated across routes.

---

# 21. Repository Layer Conventions
Repositories are responsible for database access.

Examples:

```
UserRepository
ExamRepository
QuestionRepository
ResultRepository
```
Repositories should contain operations such as:

```
def find_by_id(self, exam_id):
    ...

def find_by_code(self, exam_code):
    ...

def create(self, exam):
    ...

def update(self, exam):
    ...

def delete(self, exam):
    ...
```
Business decisions should generally remain in the service layer.

---

# 22. Model Layer Conventions
Models represent database entities and relationships.

Models shall correspond to the finalized `finaldb` database design.

Model names should use PascalCase.

Example:

```
class Exam(db.Model):
    ...
```
Database fields shall follow the existing `finaldb` schema.

Developers shall not independently rename or restructure database fields without discussing the database change with the team.

---

# 23. Database Naming Conventions
The project database is named:

```
finaldb
```
The finalized database schema shall be treated as the source of truth for database structure.

Database naming shall remain consistent.

Columns should generally use:

```
snake_case
```
Examples:

```
user_id
exam_id
question_id
attempt_id
created_at
updated_at
start_time
end_time
total_marks
```
Foreign keys should normally follow:

```
<entity>_id
```
Examples:

```
user_id
exam_id
question_id
attempt_id
```
Existing `finaldb` names shall not be changed merely for stylistic reasons.

---

# 24. Database Integrity
Database constraints shall be used wherever appropriate.

These may include:

- Primary keys
- Foreign keys
- NOT NULL constraints
- UNIQUE constraints
- CHECK constraints where supported and appropriate
- Referential integrity
- Appropriate indexes
Application logic shall not be relied upon as the only protection for important data-integrity requirements.

---

# 25. ORM Conventions
SQLAlchemy shall be used for database interaction through the established application database configuration.

Raw SQL should only be used when there is a clear technical reason.

Developers shall avoid constructing SQL queries using string concatenation with user-provided values.

Example of prohibited practice:

```
query = "SELECT * FROM user WHERE id = " + user_id
```
ORM queries or parameterized queries shall be used instead.

---

# 26. API Naming Conventions
The project shall use REST-style API naming.

API routes shall use nouns representing resources.

Example:

```
/api/v1/users
/api/v1/questions
/api/v1/exams
/api/v1/attempts
/api/v1/results
/api/v1/proctoring
```
Avoid action-based URLs such as:

```
/getUsers
/createExam
/deleteExam
```
The HTTP method should represent the action.

---

# 27. HTTP Methods
The following conventions shall be used.

MethodPurposeGETRetrieve dataPOSTCreate a resource or perform a non-idempotent operationPUTReplace/update a resourcePATCHPartially update a resourceDELETEDelete a resourceExample:

```
GET    /api/v1/exams
POST   /api/v1/exams
GET    /api/v1/exams/{id}
PUT    /api/v1/exams/{id}
DELETE /api/v1/exams/{id}
```

---

# 28. API Versioning
API endpoints shall use versioning.

The initial API version shall be:

```
/api/v1/
```
Example:

```
/api/v1/auth/login
/api/v1/users
/api/v1/questions
/api/v1/exams
/api/v1/attempts
/api/v1/results
```
Future incompatible API changes may be introduced through a new version such as:

```
/api/v2/
```

---

# 29. HTTP Status Codes
The API shall use appropriate HTTP status codes.

StatusMeaning200Successful request201Resource successfully created204Successful request with no response body400Bad request401Authentication required/failed403Access forbidden404Resource not found409Resource conflict422Validation error500Internal server errorDevelopers shall avoid returning `200 OK` for every situation.

---

# 30. API Response Structure
API responses should follow a consistent structure.

### Successful response

```
{
    "success": true,
    "data": {}
}
```

### Error response

```
{
    "success": false,
    "message": "Exam not found"
}
```
For validation errors:

```
{
    "success": false,
    "message": "Validation failed",
    "errors": {}
}
```
The exact response structure should remain consistent across modules.

---

# 31. Request Validation
All externally supplied input shall be validated before being used.

This includes:

- request body
- query parameters
- path parameters
- authentication data
- exam-related input
- question-related input
Validation should occur at the API/schema boundary where possible, while business-specific validation belongs in the service layer.

---

# 32. Authentication and Authorization
Authentication shall use the project's JWT-based authentication mechanism.

Protected endpoints shall verify authentication before processing the request.

Authorization shall verify whether the authenticated user has permission to perform the requested operation.

For example:

```
Student
    → Attempt assigned examination

Examiner
    → Create and manage examinations

Admin
    → Manage system-level users and resources
```
Authentication and authorization logic shall not be duplicated across every route.

---

# 33. Password Handling
Passwords shall never be stored in plain text.

Passwords must be securely hashed using an approved password-hashing mechanism.

Passwords shall never be:

- logged
- returned in API responses
- stored in source code
- stored in `.env` unless required as part of an external development/test setup

---

# 34. Environment Variables
Environment-specific configuration shall be stored using environment variables.

Examples include:

```
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
SECRET_KEY
JWT_SECRET_KEY
```
Sensitive values shall not be hard-coded.

The actual `.env` file shall not be committed to Git.

A sanitized `.env.example` file shall be committed.

Example:

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=finaldb
DB_USER=
DB_PASSWORD=

SECRET_KEY=
JWT_SECRET_KEY=
```

---

# 35. Error Handling
Application errors should be handled consistently.

The application should use appropriate custom exceptions where necessary.

Example:

```
class ExamNotFoundError(Exception):
    pass
```
Instead of exposing internal implementation details to clients, the API should return a clear and safe error message.

Avoid returning:

```
database stack traces
file paths
passwords
secret keys
internal configuration
```
to API consumers.

---

# 36. Logging
The Python `logging` module shall be used for backend logging.

Developers should not use `print()` as the primary application logging mechanism.

Example:

```
logger.info("Exam created successfully")
logger.warning("Suspicious activity detected")
logger.error("Failed to create exam")
```
Logs shall not contain:

- passwords
- authentication tokens
- secret keys
- sensitive personal information
- confidential examination information unless required and appropriately controlled

---

# 37. Proctoring and Suspicious Activity Logging
The proctoring module shall record relevant suspicious activities such as:

```
tab switching
window focus loss
full-screen exit
other configured suspicious events
```
Each activity should be recorded consistently with the database design.

Activity records should contain the information required by `finaldb`, such as the relevant examination attempt, activity type, timestamp, and configured status/severity fields.

Proctoring logic shall not contain AI-based functionality unless such functionality is explicitly added to the project requirements later.

---

# 38. Transaction Handling
Operations that modify multiple related database records and must succeed or fail together should use appropriate database transaction handling.

For example:

```
Submit Exam
    ↓
Save final answers
    ↓
Calculate result
    ↓
Store result
    ↓
Commit transaction
```
If a critical step fails, the transaction should be rolled back where appropriate.

---

# 39. Testing Conventions
The project shall use `pytest`.

Tests should be organized according to the project's test structure.

Example:

```
tests/
├── test_authentication.py
├── test_users.py
├── test_questions.py
├── test_exams.py
├── test_attempts.py
├── test_results.py
└── test_proctoring.py
```
Tests should cover important:

- successful operations
- validation failures
- authorization failures
- edge cases
- business rules
- database interactions where applicable

---

# 40. Test Naming
Test functions should clearly describe what they verify.

Example:

```
def test_create_exam_successfully():
    ...

def test_create_exam_without_title_fails():
    ...

def test_student_cannot_access_unassigned_exam():
    ...

def test_exam_auto_submits_when_time_expires():
    ...
```
Avoid vague names such as:

```
def test_exam():
    ...
```

---

# 41. Git Branch Naming
The project shall follow the branching structure:

```
main
  ↓
develop
  ↓
feature branches
```
Major feature branches should follow:

```
feature/<feature-name>
```
Examples:

```
feature/authentication-users
feature/question-bank
feature/exam-management
feature/exam-assignment
feature/exam-attempt
feature/evaluation-results
feature/proctoring
feature/notifications
feature/admin-reporting
```
Bug-fix branches should use:

```
fix/<issue-name>
```
Example:

```
fix/exam-timer
fix/login-validation
```

---

# 42. Git Commit Conventions
Commit messages shall use a consistent prefix.

The following prefixes shall be used:

```
feat:
fix:
refactor:
test:
docs:
chore:
```

### Examples

```
feat: add user registration
feat: implement exam creation
fix: correct exam timer calculation
fix: resolve duplicate exam attempt issue
refactor: simplify result calculation
test: add authentication tests
docs: update API documentation
chore: update project dependencies
```
Commit messages should be concise and describe the actual change.

---

# 43. Commit Guidelines
Developers should:

- make small, logical commits
- avoid committing unrelated changes together
- write meaningful commit messages
- avoid committing generated files
- avoid committing `.env`
- ensure code works before pushing
Avoid commits such as:

```
update
changes
final
test
asdf
```

---

# 44. Pull Request Guidelines
Before merging a feature branch into `develop`, the developer should verify:

```
- Code follows project coding conventions
- Code is formatted
- Linting passes
- Tests pass
- No hard-coded credentials exist
- No unnecessary files are included
- Database changes are documented
- API changes are documented
- No unrelated changes are included
```
The second developer should review the changes before merging whenever practical.

---

# 45. Code Review Guidelines
Code reviews should focus on:

- correctness
- security
- maintainability
- architecture
- readability
- database integrity
- API consistency
- test coverage
- unnecessary duplication
Code review comments should be constructive and focused on the code rather than the developer.

---

# 46. Dependency Management
Project dependencies shall be recorded in:

```
requirements.txt
```
When adding a new dependency, the developer should ensure that:

1. The dependency is actually required.
2. It does not duplicate existing functionality unnecessarily.
3. It is compatible with the project.
4. The dependency is added to `requirements.txt`.
5. Other developers can install it successfully.
Installation:

```
pip install -r requirements.txt
```

---

# 47. Code Quality Tools
The project shall use the following tools:

### Black
Used for automatic code formatting.

```
black .
```

### Ruff
Used for linting and detecting code-quality issues.

```
ruff check .
```

### isort
Used for organizing imports.

```
isort .
```

### pytest
Used for automated testing.

```
pytest
```
Before creating a pull request, developers should run the project's configured formatting, linting, import-sorting, and test commands.

---

# 48. Generated and Temporary Files
The following files/directories should not be committed unless explicitly required:

```
__pycache__/
.venv/
.env
.pytest_cache/
.coverage
*.log
IDE-specific configuration
temporary files
```
These should be included in `.gitignore`.

---

# 49. Documentation Conventions
Documentation should be updated when significant functionality changes.

Documentation may include:

```
README.md
docs/
API documentation
database documentation
architecture documentation
```
When an API changes significantly, the relevant API documentation should also be updated.

---

# 50. Database Change Convention
Developers shall not directly modify the finalized `finaldb` structure without agreement from the development team.

Any database change should identify:

```
1. What is changing?
2. Why is it changing?
3. Which tables are affected?
4. Which relationships are affected?
5. Whether existing data is affected?
6. Whether ORM models must change?
7. Whether API/service logic must change?
```
Database changes should be represented through the project's database migration/schema process as appropriate.

---

# 51. Feature Development Workflow
Every major feature should generally follow this workflow:

```
Requirement
    ↓
Database impact analysis
    ↓
API design
    ↓
Schema/model
    ↓
Repository
    ↓
Service
    ↓
Route
    ↓
Testing
    ↓
Code formatting
    ↓
Linting
    ↓
Pull Request
    ↓
Code Review
    ↓
Merge into develop
```
This workflow should be followed consistently across modules.

---

# 52. Example Feature Implementation
For example, implementing exam creation should follow:

```
POST /api/v1/exams
        ↓
Exam Route
        ↓
Request Validation
        ↓
Exam Service
        ↓
Exam Repository
        ↓
Exam Model
        ↓
MySQL / finaldb
```
The route should not directly perform all database and business operations.

---

# 53. Naming Summary
ElementConventionExamplePython filesnake_case`exam_service.py`Folderlowercase`services/`ClassPascalCase`ExamService`Functionsnake_case`create_exam()`Methodsnake_case`get_exam_by_id()`Variablesnake_case`exam_id`ConstantUPPER_SNAKE_CASE`MAX_EXAM_DURATION`Booleanis_/has_`is_active`Database columnsnake_case`created_at`Foreign keyentity_id`exam_id`API resourceplural noun`/exams`API version`/api/v1/``/api/v1/exams`Feature branchfeature/name`feature/exam-management`Bug branchfix/name`fix/exam-timer`
---

# 54. Developer Checklist
Before pushing code, the developer should verify:

```
[ ] Code follows PEP 8
[ ] Naming conventions are followed
[ ] No unnecessary duplicate code exists
[ ] Routes contain no unnecessary business logic
[ ] Business logic is placed in services
[ ] Database operations are placed in repositories
[ ] Database changes follow finaldb design
[ ] API naming follows REST conventions
[ ] Input is validated
[ ] Authentication/authorization is handled
[ ] No passwords or secrets are hard-coded
[ ] .env is not committed
[ ] Error handling is consistent
[ ] Logging does not expose sensitive information
[ ] Tests have been added/updated
[ ] pytest passes
[ ] Ruff passes
[ ] Black formatting is applied
[ ] isort formatting is applied
[ ] Commit message follows Git conventions
[ ] No unrelated changes are included
```

---

# 55. Definition of Done
A feature shall generally be considered complete when:

1. The required functionality has been implemented.
2. The implementation follows the project architecture.
3. Database changes, if any, are complete and documented.
4. API endpoints follow the defined API conventions.
5. Input validation is implemented.
6. Authentication and authorization requirements are satisfied.
7. Appropriate error handling is implemented.
8. Relevant tests have been written.
9. Tests pass successfully.
10. Code formatting and linting pass.
11. No secrets or temporary files are committed.
12. Documentation has been updated where necessary.
13. The feature has been reviewed.
14. The feature branch can be merged into `develop` safely.

---

# 56. Final Development Rule
Consistency is more important than individual developer preference.

If a developer has a personal coding style that differs from this document, the project conventions shall take precedence.

Any proposed change to these conventions should be discussed and agreed upon by the development team before being adopted.

This document shall be updated whenever a major project-wide development standard changes.

---
**End of Coding Conventions Document**