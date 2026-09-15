"""
Admin services.

Admin is responsible for creating subjects and assigning
subjects to Faculty.
"""

from app.extensions.database import db
from app.models import (
    Faculty,
    FacultySubject,
    Subject,
    User,
    Role,
    Department,
    Student,
    Exam,
    ExamQuestion,
    CandidateRegistration,
    Question,
    QuestionOption,
    ExamAttempt,
    StudentAnswer,
    Result,
    AuditLog,
)
from app.utils.password import hash_password


def create_subject(
    user_id,
    department_id,
    subject_code,
    subject_name,
    description=None,
    credits=None,
):
    """Create a new subject."""

    if not subject_code or not str(subject_code).strip():
        raise ValueError("Subject code is required.")

    if not subject_name or not str(subject_name).strip():
        raise ValueError("Subject name is required.")

    try:
        department_id = int(department_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid department_id.")

    subject_code = str(subject_code).strip()
    subject_name = str(subject_name).strip()

    existing = Subject.query.filter_by(subject_code=subject_code).first()
    if existing is not None:
        raise ValueError("A subject with this subject code already exists.")

    if credits is not None:
        try:
            credits = int(credits)
        except (TypeError, ValueError):
            raise ValueError("Credits must be a valid integer.")

        if credits <= 0:
            raise ValueError("Credits must be greater than 0.")

    subject = Subject(
        department_id=department_id,
        created_by=user_id,
        subject_code=subject_code,
        subject_name=subject_name,
        description=description,
        credits=credits,
        is_active=True,
    )

    try:
        db.session.add(subject)
        db.session.commit()
        return subject
    except Exception:
        db.session.rollback()
        raise

def update_subject(
    subject_id,
    department_id=None,
    subject_code=None,
    subject_name=None,
    description=None,
    credits=None,
):
    """Update an existing subject."""

    try:
        subject_id = int(subject_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid subject_id.")

    subject = Subject.query.filter_by(
        subject_id=subject_id
    ).first()

    if subject is None:
        raise ValueError("Subject not found.")

    if department_id is not None:
        try:
            department_id = int(department_id)
        except (TypeError, ValueError):
            raise ValueError("Invalid department_id.")

        department = Department.query.filter_by(
            department_id=department_id
        ).first()

        if department is None:
            raise ValueError("Department not found.")

        if not department.is_active:
            raise ValueError(
                "Cannot assign subject to an inactive department."
            )

        subject.department_id = department_id

    if subject_code is not None:
        subject_code = str(subject_code).strip()

        if not subject_code:
            raise ValueError("Subject code cannot be empty.")

        existing = (
            Subject.query
            .filter(
                Subject.subject_code == subject_code,
                Subject.subject_id != subject.subject_id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "A subject with this subject code already exists."
            )

        subject.subject_code = subject_code

    if subject_name is not None:
        subject_name = str(subject_name).strip()

        if not subject_name:
            raise ValueError("Subject name cannot be empty.")

        subject.subject_name = subject_name

    if description is not None:
        subject.description = str(description).strip()

    if credits is not None:
        try:
            credits = int(credits)
        except (TypeError, ValueError):
            raise ValueError("Credits must be a valid integer.")

        if credits <= 0:
            raise ValueError("Credits must be greater than 0.")

        subject.credits = credits

    try:
        db.session.commit()
        return subject

    except Exception:
        db.session.rollback()
        raise


def set_subject_status(subject_id, is_active):
    """Activate or deactivate a subject."""

    try:
        subject_id = int(subject_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid subject_id.")

    if not isinstance(is_active, bool):
        raise ValueError(
            "is_active must be true or false."
        )

    subject = Subject.query.filter_by(
        subject_id=subject_id
    ).first()

    if subject is None:
        raise ValueError("Subject not found.")

    subject.is_active = is_active

    try:
        db.session.commit()
        return subject

    except Exception:
        db.session.rollback()
        raise

def get_all_subjects():
    """Return all subjects."""

    return (
        Subject.query
        .order_by(Subject.subject_id.desc())
        .all()
    )


def get_all_faculty():
    """Return all Faculty profiles."""

    return (
        Faculty.query
        .order_by(Faculty.faculty_id.asc())
        .all()
    )


def assign_subject_to_faculty(
    faculty_id,
    subject_id,
    semester,
    year,
):
    """Assign a subject to a Faculty member."""

    try:
        faculty_id = int(faculty_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid faculty_id.")

    try:
        subject_id = int(subject_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid subject_id.")

    try:
        semester = int(semester)
    except (TypeError, ValueError):
        raise ValueError("Semester must be a valid integer.")

    try:
        year = int(year)
    except (TypeError, ValueError):
        raise ValueError("Year must be a valid integer.")

    if semester <= 0:
        raise ValueError("Semester must be greater than 0.")

    if year <= 0:
        raise ValueError("Year must be greater than 0.")

    faculty = Faculty.query.filter_by(faculty_id=faculty_id).first()

    if faculty is None:
        raise ValueError("Faculty not found.")

    subject = Subject.query.filter_by(subject_id=subject_id).first()

    if subject is None:
        raise ValueError("Subject not found.")

    if not subject.is_active:
        raise ValueError("Cannot assign an inactive subject.")

    existing = FacultySubject.query.filter_by(
        faculty_id=faculty_id,
        subject_id=subject_id,
        semester=semester,
        year=year,
    ).first()

    if existing is not None:
        if existing.is_active:
            raise ValueError(
                "This subject is already assigned to this Faculty for this semester and year."
            )

        # Reactivate an old assignment instead of creating a duplicate.
        existing.is_active = True

        try:
            db.session.commit()
            return existing
        except Exception:
            db.session.rollback()
            raise

    assignment = FacultySubject(
        faculty_id=faculty_id,
        subject_id=subject_id,
        semester=semester,
        year=year,
        is_active=True,
    )

    try:
        db.session.add(assignment)
        db.session.commit()
        return assignment
    except Exception:
        db.session.rollback()
        raise


def get_faculty_subjects(faculty_id):
    """Return all assignments for a Faculty member."""

    try:
        faculty_id = int(faculty_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid faculty_id.")

    faculty = Faculty.query.filter_by(faculty_id=faculty_id).first()

    if faculty is None:
        raise ValueError("Faculty not found.")

    return (
        FacultySubject.query
        .filter_by(faculty_id=faculty_id)
        .order_by(
            FacultySubject.year.desc(),
            FacultySubject.semester.desc(),
            FacultySubject.faculty_subject_id.desc(),
        )
        .all()
    )


def deactivate_faculty_subject(faculty_subject_id):
    """Deactivate an assignment while preserving its history."""

    try:
        faculty_subject_id = int(faculty_subject_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid faculty_subject_id.")

    assignment = FacultySubject.query.filter_by(
        faculty_subject_id=faculty_subject_id
    ).first()

    if assignment is None:
        raise ValueError("Faculty subject assignment not found.")

    assignment.is_active = False

    try:
        db.session.commit()
        return assignment
    except Exception:
        db.session.rollback()
        raise

def get_all_users():
    """
    Return all platform users for Admin management.
    """
    return (
        User.query
        .join(Role)
        .order_by(User.user_id.asc())
        .all()
    )


def get_user_by_id(user_id):
    """
    Return a single user by ID.
    """
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid user_id.")

    user = User.query.filter_by(user_id=user_id).first()

    if user is None:
        raise ValueError("User not found.")

    return user


def create_user(
    first_name,
    last_name,
    email,
    password,
    role_name,
    phone=None,
):
    """
    Admin creates a platform user.
    """

    if not first_name or not str(first_name).strip():
        raise ValueError("First name is required.")

    if not last_name or not str(last_name).strip():
        raise ValueError("Last name is required.")

    if not email or not str(email).strip():
        raise ValueError("Email is required.")

    if not password:
        raise ValueError("Password is required.")

    if not role_name or not str(role_name).strip():
        raise ValueError("Role is required.")

    first_name = str(first_name).strip()
    last_name = str(last_name).strip()
    email = str(email).strip().lower()
    role_name = str(role_name).strip().upper()

    allowed_roles = {"ADMIN", "FACULTY", "STUDENT"}

    if role_name not in allowed_roles:
        raise ValueError(
            "Role must be ADMIN, FACULTY, or STUDENT."
        )

    existing_email = User.query.filter_by(email=email).first()

    if existing_email is not None:
        raise ValueError(
            "A user with this email already exists."
        )

    if phone is not None:
        phone = str(phone).strip()

        if not phone:
            phone = None

        if phone is not None:
            existing_phone = User.query.filter_by(
                phone=phone
            ).first()

            if existing_phone is not None:
                raise ValueError(
                    "A user with this phone number already exists."
                )

    role = Role.query.filter_by(role_name=role_name).first()

    if role is None:
        raise ValueError("Role not found.")

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        role_id=role.role_id,
        is_active=True,
    )

    try:
        db.session.add(user)
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise


def update_user(
    user_id,
    first_name=None,
    last_name=None,
    email=None,
    phone=None,
):
    """
    Admin updates basic user information.
    """

    user = get_user_by_id(user_id)

    if first_name is not None:
        first_name = str(first_name).strip()

        if not first_name:
            raise ValueError("First name cannot be empty.")

        user.first_name = first_name

    if last_name is not None:
        last_name = str(last_name).strip()

        if not last_name:
            raise ValueError("Last name cannot be empty.")

        user.last_name = last_name

    if email is not None:
        email = str(email).strip().lower()

        if not email:
            raise ValueError("Email cannot be empty.")

        existing = (
            User.query
            .filter(
                User.email == email,
                User.user_id != user.user_id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "A user with this email already exists."
            )

        user.email = email

    if phone is not None:
        phone = str(phone).strip()

        if not phone:
            phone = None

        if phone is not None:
            existing = (
                User.query
                .filter(
                    User.phone == phone,
                    User.user_id != user.user_id,
                )
                .first()
            )

            if existing is not None:
                raise ValueError(
                    "A user with this phone number already exists."
                )

        user.phone = phone

    try:
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise


def set_user_status(user_id, is_active):
    """
    Activate or deactivate a user.

    An Admin cannot deactivate the last active Admin.
    """

    user = get_user_by_id(user_id)

    if not isinstance(is_active, bool):
        raise ValueError("is_active must be true or false.")

    if user.is_active == is_active:
        return user

    if not is_active and user.role.role_name == "ADMIN":
        active_admin_count = (
            User.query
            .join(Role)
            .filter(
                Role.role_name == "ADMIN",
                User.is_active.is_(True),
            )
            .count()
        )

        if active_admin_count <= 1:
            raise ValueError(
                "Cannot deactivate the last active Admin."
            )

    user.is_active = is_active

    try:
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise


def change_user_role(user_id, role_name):
    """
    Change a user's platform role.
    """

    user = get_user_by_id(user_id)

    role_name = str(role_name).strip().upper()

    allowed_roles = {"ADMIN", "FACULTY", "STUDENT"}

    if role_name not in allowed_roles:
        raise ValueError(
            "Role must be ADMIN, FACULTY, or STUDENT."
        )

    role = Role.query.filter_by(role_name=role_name).first()

    if role is None:
        raise ValueError("Role not found.")

    if user.role.role_name == "ADMIN" and role_name != "ADMIN":
        active_admin_count = (
            User.query
            .join(Role)
            .filter(
                Role.role_name == "ADMIN",
                User.is_active.is_(True),
            )
            .count()
        )

        if user.is_active and active_admin_count <= 1:
            raise ValueError(
                "Cannot remove the role from the last active Admin."
            )

    user.role_id = role.role_id

    try:
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise


def reset_user_password(user_id, new_password):
    """
    Admin resets a user's password.
    """

    user = get_user_by_id(user_id)

    if not new_password:
        raise ValueError("New password is required.")

    if len(str(new_password)) < 8:
        raise ValueError(
            "Password must be at least 8 characters long."
        )

    user.password_hash = hash_password(str(new_password))

    try:
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise


def get_faculty_by_id(faculty_id):
    """Return a single Faculty profile by ID."""

    try:
        faculty_id = int(faculty_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid faculty_id.")

    faculty = Faculty.query.filter_by(
        faculty_id=faculty_id
    ).first()

    if faculty is None:
        raise ValueError("Faculty not found.")

    return faculty


def create_faculty(
    first_name,
    last_name,
    email,
    password,
    department_id,
    employee_number,
    designation,
    phone=None,
):
    """
    Create a Faculty account.

    Creates both the User and Faculty profile in one transaction.
    """

    if not first_name or not str(first_name).strip():
        raise ValueError("First name is required.")

    if not last_name or not str(last_name).strip():
        raise ValueError("Last name is required.")

    if not email or not str(email).strip():
        raise ValueError("Email is required.")

    if not password:
        raise ValueError("Password is required.")

    if not employee_number or not str(employee_number).strip():
        raise ValueError("Employee number is required.")

    if not designation or not str(designation).strip():
        raise ValueError("Designation is required.")

    try:
        department_id = int(department_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid department_id.")

    first_name = str(first_name).strip()
    last_name = str(last_name).strip()
    email = str(email).strip().lower()
    employee_number = str(employee_number).strip()
    designation = str(designation).strip()

    department = Department.query.filter_by(
        department_id=department_id
    ).first()

    if department is None:
        raise ValueError("Department not found.")

    if not department.is_active:
        raise ValueError("Cannot assign Faculty to an inactive department.")

    existing_email = User.query.filter_by(email=email).first()

    if existing_email is not None:
        raise ValueError(
            "A user with this email already exists."
        )

    existing_employee = Faculty.query.filter_by(
        employee_number=employee_number
    ).first()

    if existing_employee is not None:
        raise ValueError(
            "A Faculty member with this employee number already exists."
        )

    if phone is not None:
        phone = str(phone).strip()

        if not phone:
            phone = None

        if phone is not None:
            existing_phone = User.query.filter_by(
                phone=phone
            ).first()

            if existing_phone is not None:
                raise ValueError(
                    "A user with this phone number already exists."
                )

    role = Role.query.filter_by(
        role_name="FACULTY"
    ).first()

    if role is None:
        raise ValueError("FACULTY role not found.")

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        role_id=role.role_id,
        is_active=True,
    )

    try:
        db.session.add(user)
        db.session.flush()

        faculty = Faculty(
            user_id=user.user_id,
            department_id=department_id,
            employee_number=employee_number,
            designation=designation,
        )

        db.session.add(faculty)
        db.session.commit()

        return faculty

    except Exception:
        db.session.rollback()
        raise


def update_faculty(
    faculty_id,
    first_name=None,
    last_name=None,
    email=None,
    phone=None,
    department_id=None,
    employee_number=None,
    designation=None,
):
    """Update Faculty account and profile information."""

    faculty = get_faculty_by_id(faculty_id)
    user = faculty.user

    if first_name is not None:
        first_name = str(first_name).strip()

        if not first_name:
            raise ValueError("First name cannot be empty.")

        user.first_name = first_name

    if last_name is not None:
        last_name = str(last_name).strip()

        if not last_name:
            raise ValueError("Last name cannot be empty.")

        user.last_name = last_name

    if email is not None:
        email = str(email).strip().lower()

        if not email:
            raise ValueError("Email cannot be empty.")

        existing = (
            User.query
            .filter(
                User.email == email,
                User.user_id != user.user_id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "A user with this email already exists."
            )

        user.email = email

    if phone is not None:
        phone = str(phone).strip()

        if not phone:
            phone = None

        if phone is not None:
            existing = (
                User.query
                .filter(
                    User.phone == phone,
                    User.user_id != user.user_id,
                )
                .first()
            )

            if existing is not None:
                raise ValueError(
                    "A user with this phone number already exists."
                )

        user.phone = phone

    if department_id is not None:
        try:
            department_id = int(department_id)
        except (TypeError, ValueError):
            raise ValueError("Invalid department_id.")

        department = Department.query.filter_by(
            department_id=department_id
        ).first()

        if department is None:
            raise ValueError("Department not found.")

        if not department.is_active:
            raise ValueError(
                "Cannot assign Faculty to an inactive department."
            )

        faculty.department_id = department_id

    if employee_number is not None:
        employee_number = str(employee_number).strip()

        if not employee_number:
            raise ValueError(
                "Employee number cannot be empty."
            )

        existing = (
            Faculty.query
            .filter(
                Faculty.employee_number == employee_number,
                Faculty.faculty_id != faculty.faculty_id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "A Faculty member with this employee number already exists."
            )

        faculty.employee_number = employee_number

    if designation is not None:
        designation = str(designation).strip()

        if not designation:
            raise ValueError(
                "Designation cannot be empty."
            )

        faculty.designation = designation

    try:
        db.session.commit()
        return faculty

    except Exception:
        db.session.rollback()
        raise


def set_faculty_status(faculty_id, is_active):
    """Activate or deactivate a Faculty member."""

    faculty = get_faculty_by_id(faculty_id)

    if not isinstance(is_active, bool):
        raise ValueError(
            "is_active must be true or false."
        )

    faculty.user.is_active = is_active

    try:
        db.session.commit()
        return faculty

    except Exception:
        db.session.rollback()
        raise


def get_all_students():
    """Return all Student profiles."""

    return (
        Student.query
        .order_by(Student.student_id.asc())
        .all()
    )


def get_student_by_id(student_id):
    """Return a single Student profile by ID."""

    try:
        student_id = int(student_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid student_id.")

    student = Student.query.filter_by(
        student_id=student_id
    ).first()

    if student is None:
        raise ValueError("Student not found.")

    return student


def create_student(
    first_name,
    last_name,
    email,
    password,
    department_id,
    roll_number,
    enrollment_number,
    year,
    semester,
    phone=None,
):
    """
    Create a Student account.

    Creates both the User and Student profile in one transaction.
    """

    if not first_name or not str(first_name).strip():
        raise ValueError("First name is required.")

    if not last_name or not str(last_name).strip():
        raise ValueError("Last name is required.")

    if not email or not str(email).strip():
        raise ValueError("Email is required.")

    if not password:
        raise ValueError("Password is required.")

    if not roll_number or not str(roll_number).strip():
        raise ValueError("Roll number is required.")

    if not enrollment_number or not str(enrollment_number).strip():
        raise ValueError("Enrollment number is required.")

    try:
        department_id = int(department_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid department_id.")

    try:
        year = int(year)
    except (TypeError, ValueError):
        raise ValueError("Year must be a valid integer.")

    try:
        semester = int(semester)
    except (TypeError, ValueError):
        raise ValueError("Semester must be a valid integer.")

    if year <= 0:
        raise ValueError("Year must be greater than 0.")

    if semester <= 0:
        raise ValueError("Semester must be greater than 0.")

    first_name = str(first_name).strip()
    last_name = str(last_name).strip()
    email = str(email).strip().lower()
    roll_number = str(roll_number).strip()
    enrollment_number = str(enrollment_number).strip()

    department = Department.query.filter_by(
        department_id=department_id
    ).first()

    if department is None:
        raise ValueError("Department not found.")

    if not department.is_active:
        raise ValueError(
            "Cannot assign Student to an inactive department."
        )

    existing_email = User.query.filter_by(
        email=email
    ).first()

    if existing_email is not None:
        raise ValueError(
            "A user with this email already exists."
        )

    existing_roll = Student.query.filter_by(
        roll_number=roll_number
    ).first()

    if existing_roll is not None:
        raise ValueError(
            "A Student with this roll number already exists."
        )

    existing_enrollment = Student.query.filter_by(
        enrollment_number=enrollment_number
    ).first()

    if existing_enrollment is not None:
        raise ValueError(
            "A Student with this enrollment number already exists."
        )

    if phone is not None:
        phone = str(phone).strip()

        if not phone:
            phone = None

        if phone is not None:
            existing_phone = User.query.filter_by(
                phone=phone
            ).first()

            if existing_phone is not None:
                raise ValueError(
                    "A user with this phone number already exists."
                )

    role = Role.query.filter_by(
        role_name="STUDENT"
    ).first()

    if role is None:
        raise ValueError("STUDENT role not found.")

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        role_id=role.role_id,
        is_active=True,
    )

    try:
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.user_id,
            department_id=department_id,
            roll_number=roll_number,
            enrollment_number=enrollment_number,
            year=year,
            semester=semester,
            is_active=True,
        )

        db.session.add(student)
        db.session.commit()

        return student

    except Exception:
        db.session.rollback()
        raise


def update_student(
    student_id,
    first_name=None,
    last_name=None,
    email=None,
    phone=None,
    department_id=None,
    roll_number=None,
    enrollment_number=None,
    year=None,
    semester=None,
):
    """Update Student account and profile information."""

    student = get_student_by_id(student_id)
    user = student.user

    if first_name is not None:
        first_name = str(first_name).strip()

        if not first_name:
            raise ValueError("First name cannot be empty.")

        user.first_name = first_name

    if last_name is not None:
        last_name = str(last_name).strip()

        if not last_name:
            raise ValueError("Last name cannot be empty.")

        user.last_name = last_name

    if email is not None:
        email = str(email).strip().lower()

        if not email:
            raise ValueError("Email cannot be empty.")

        existing = (
            User.query
            .filter(
                User.email == email,
                User.user_id != user.user_id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "A user with this email already exists."
            )

        user.email = email

    if phone is not None:
        phone = str(phone).strip()

        if not phone:
            phone = None

        if phone is not None:
            existing = (
                User.query
                .filter(
                    User.phone == phone,
                    User.user_id != user.user_id,
                )
                .first()
            )

            if existing is not None:
                raise ValueError(
                    "A user with this phone number already exists."
                )

        user.phone = phone

    if department_id is not None:
        try:
            department_id = int(department_id)
        except (TypeError, ValueError):
            raise ValueError("Invalid department_id.")

        department = Department.query.filter_by(
            department_id=department_id
        ).first()

        if department is None:
            raise ValueError("Department not found.")

        if not department.is_active:
            raise ValueError(
                "Cannot assign Student to an inactive department."
            )

        student.department_id = department_id

    if roll_number is not None:
        roll_number = str(roll_number).strip()

        if not roll_number:
            raise ValueError("Roll number cannot be empty.")

        existing = (
            Student.query
            .filter(
                Student.roll_number == roll_number,
                Student.student_id != student.student_id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "A Student with this roll number already exists."
            )

        student.roll_number = roll_number

    if enrollment_number is not None:
        enrollment_number = str(enrollment_number).strip()

        if not enrollment_number:
            raise ValueError(
                "Enrollment number cannot be empty."
            )

        existing = (
            Student.query
            .filter(
                Student.enrollment_number == enrollment_number,
                Student.student_id != student.student_id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "A Student with this enrollment number already exists."
            )

        student.enrollment_number = enrollment_number

    if year is not None:
        try:
            year = int(year)
        except (TypeError, ValueError):
            raise ValueError("Year must be a valid integer.")

        if year <= 0:
            raise ValueError("Year must be greater than 0.")

        student.year = year

    if semester is not None:
        try:
            semester = int(semester)
        except (TypeError, ValueError):
            raise ValueError("Semester must be a valid integer.")

        if semester <= 0:
            raise ValueError("Semester must be greater than 0.")

        student.semester = semester

    try:
        db.session.commit()
        return student

    except Exception:
        db.session.rollback()
        raise


def set_student_status(student_id, is_active):
    """Activate or deactivate a Student."""

    student = get_student_by_id(student_id)

    if not isinstance(is_active, bool):
        raise ValueError(
            "is_active must be true or false."
        )

    student.is_active = is_active
    student.user.is_active = is_active

    try:
        db.session.commit()
        return student

    except Exception:
        db.session.rollback()
        raise


def get_all_exams():
    """
    Get all exams for Admin oversight.

    Includes:
    - Exam details
    - Subject details
    - Faculty/creator details
    - Schedule information
    - Question count
    - Candidate registration count
    """
    from sqlalchemy import func

    exams = (
        db.session.query(
            Exam,
            Subject,
            User,
            func.count(db.distinct(ExamQuestion.exam_question_id)).label(
                'question_count'
            ),
            func.count(db.distinct(CandidateRegistration.registration_id)).label(
                'candidate_count'
            )
        )
        .join(Subject, Exam.subject_id == Subject.subject_id)
        .join(User, Exam.created_by == User.user_id)
        .outerjoin(
            ExamQuestion,
            Exam.exam_id == ExamQuestion.exam_id
        )
        .outerjoin(
            CandidateRegistration,
            Exam.exam_id == CandidateRegistration.exam_id
        )
        .group_by(
            Exam.exam_id,
            Subject.subject_id,
            User.user_id
        )
        .order_by(Exam.exam_id.asc())
        .all()
    )

    return exams


def get_exam_by_id(exam_id):
    """
    Get a single exam with Admin oversight information.
    """
    from sqlalchemy import func

    if not isinstance(exam_id, int) or exam_id <= 0:
        raise ValueError("Invalid exam ID.")

    result = (
        db.session.query(
            Exam,
            Subject,
            User,
            func.count(db.distinct(ExamQuestion.exam_question_id)).label(
                'question_count'
            ),
            func.count(db.distinct(CandidateRegistration.registration_id)).label(
                'candidate_count'
            )
        )
        .join(Subject, Exam.subject_id == Subject.subject_id)
        .join(User, Exam.created_by == User.user_id)
        .outerjoin(
            ExamQuestion,
            Exam.exam_id == ExamQuestion.exam_id
        )
        .outerjoin(
            CandidateRegistration,
            Exam.exam_id == CandidateRegistration.exam_id
        )
        .filter(Exam.exam_id == exam_id)
        .group_by(
            Exam.exam_id,
            Subject.subject_id,
            User.user_id
        )
        .first()
    )

    if not result:
        raise ValueError("Exam not found.")

    return result


def get_all_questions():
    """Return all questions with subject and creator information."""
    from sqlalchemy import func

    results = (
        db.session.query(
            Question,
            Subject,
            User,
            func.count(QuestionOption.option_id).label('option_count')
        )
        .join(Subject, Question.subject_id == Subject.subject_id)
        .join(User, Question.created_by == User.user_id)
        .outerjoin(
            QuestionOption,
            Question.question_id == QuestionOption.question_id
        )
        .group_by(
            Question.question_id,
            Subject.subject_id,
            User.user_id
        )
        .order_by(Question.question_id.asc())
        .all()
    )

    return results


def get_question_by_id(question_id):
    """Return one question with subject, creator and option information."""
    try:
        question_id = int(question_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid question ID.")

    question = Question.query.filter_by(question_id=question_id).first()

    if question is None:
        raise ValueError("Question not found.")

    return question


def set_question_status(question_id, is_active):
    """Activate or deactivate a question."""
    try:
        question_id = int(question_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid question ID.")

    if not isinstance(is_active, bool):
        raise ValueError("is_active must be true or false.")

    question = Question.query.filter_by(
        question_id=question_id
    ).first()

    if question is None:
        raise ValueError("Question not found.")

    question.is_active = is_active

    try:
        db.session.commit()
        return question
    except Exception:
        db.session.rollback()
        raise

def get_all_exam_registrations():
    """Return all exam registrations with exam, subject and student details."""
    registrations = (
        db.session.query(
            CandidateRegistration,
            Exam,
            Subject,
            Student,
            User
        )
        .join(Exam, CandidateRegistration.exam_id == Exam.exam_id)
        .join(Subject, Exam.subject_id == Subject.subject_id)
        .join(Student, CandidateRegistration.student_id == Student.student_id)
        .join(User, Student.user_id == User.user_id)
        .order_by(CandidateRegistration.registration_id.asc())
        .all()
    )

    return registrations


def get_exam_registrations(exam_id):
    """Return all registrations for a specific exam."""
    try:
        exam_id = int(exam_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid exam ID.")

    exam = Exam.query.filter_by(exam_id=exam_id).first()

    if exam is None:
        raise ValueError("Exam not found.")

    registrations = (
        db.session.query(
            CandidateRegistration,
            Student,
            User
        )
        .join(Student, CandidateRegistration.student_id == Student.student_id)
        .join(User, Student.user_id == User.user_id)
        .filter(CandidateRegistration.exam_id == exam_id)
        .order_by(CandidateRegistration.registration_id.asc())
        .all()
    )

    return exam, registrations


def get_registration_by_id(registration_id):
    """Return one exam registration with student and exam details."""
    try:
        registration_id = int(registration_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid registration ID.")

    result = (
        db.session.query(
            CandidateRegistration,
            Exam,
            Subject,
            Student,
            User
        )
        .join(Exam, CandidateRegistration.exam_id == Exam.exam_id)
        .join(Subject, Exam.subject_id == Subject.subject_id)
        .join(Student, CandidateRegistration.student_id == Student.student_id)
        .join(User, Student.user_id == User.user_id)
        .filter(
            CandidateRegistration.registration_id == registration_id
        )
        .first()
    )

    if result is None:
        raise ValueError("Registration not found.")

    return result

def get_all_attempts():
    """Return all examination attempts with student and exam details."""

    results = (
        db.session.query(
            ExamAttempt,
            CandidateRegistration,
            Exam,
            Subject,
            Student,
            User,
            Result,
        )
        .join(
            CandidateRegistration,
            ExamAttempt.registration_id ==
            CandidateRegistration.registration_id
        )
        .join(
            Exam,
            CandidateRegistration.exam_id == Exam.exam_id
        )
        .join(
            Subject,
            Exam.subject_id == Subject.subject_id
        )
        .join(
            Student,
            CandidateRegistration.student_id == Student.student_id
        )
        .join(
            User,
            Student.user_id == User.user_id
        )
        .outerjoin(
            Result,
            ExamAttempt.attempt_id == Result.attempt_id
        )
        .order_by(ExamAttempt.attempt_id.asc())
        .all()
    )

    return results

def get_exam_attempts(exam_id):
    """Return all attempts made for a particular exam."""

    try:
        exam_id = int(exam_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid exam ID.")

    exam = Exam.query.filter_by(exam_id=exam_id).first()

    if exam is None:
        raise ValueError("Exam not found.")

    results = (
        db.session.query(
            ExamAttempt,
            CandidateRegistration,
            Student,
            User,
            Result,
        )
        .join(
            CandidateRegistration,
            ExamAttempt.registration_id ==
            CandidateRegistration.registration_id
        )
        .join(
            Student,
            CandidateRegistration.student_id == Student.student_id
        )
        .join(
            User,
            Student.user_id == User.user_id
        )
        .outerjoin(
            Result,
            ExamAttempt.attempt_id == Result.attempt_id
        )
        .filter(
            CandidateRegistration.exam_id == exam_id
        )
        .order_by(ExamAttempt.attempt_id.asc())
        .all()
    )

    return exam, results

def get_attempt_by_id(attempt_id):
    """Return detailed information for one examination attempt."""

    try:
        attempt_id = int(attempt_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid attempt ID.")

    result = (
        db.session.query(
            ExamAttempt,
            CandidateRegistration,
            Exam,
            Subject,
            Student,
            User,
            Result,
        )
        .join(
            CandidateRegistration,
            ExamAttempt.registration_id ==
            CandidateRegistration.registration_id
        )
        .join(
            Exam,
            CandidateRegistration.exam_id == Exam.exam_id
        )
        .join(
            Subject,
            Exam.subject_id == Subject.subject_id
        )
        .join(
            Student,
            CandidateRegistration.student_id == Student.student_id
        )
        .join(
            User,
            Student.user_id == User.user_id
        )
        .outerjoin(
            Result,
            ExamAttempt.attempt_id == Result.attempt_id
        )
        .filter(
            ExamAttempt.attempt_id == attempt_id
        )
        .first()
    )

    if result is None:
        raise ValueError("Examination attempt not found.")

    return result

def get_attempt_integrity_events(attempt_id):
    """Return browser integrity events recorded for an attempt."""

    try:
        attempt_id = int(attempt_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid attempt ID.")

    attempt = ExamAttempt.query.filter_by(
        attempt_id=attempt_id
    ).first()

    if attempt is None:
        raise ValueError("Examination attempt not found.")

    events = (
        AuditLog.query
        .filter(
            AuditLog.entity_type == 'ExamAttempt',
            AuditLog.entity_id == attempt_id,
            AuditLog.action.in_([
                'TAB_SWITCH',
                'WINDOW_BLUR',
                'FULLSCREEN_EXIT',
                'PAGE_HIDDEN',
            ])
        )
        .order_by(AuditLog.created_at.asc())
        .all()
    )

    return attempt, events

def get_all_results():
    """Return all generated examination results with student and exam details."""

    results = (
        db.session.query(
            Result,
            ExamAttempt,
            CandidateRegistration,
            Exam,
            Subject,
            Student,
            User,
        )
        .join(
            ExamAttempt,
            Result.attempt_id == ExamAttempt.attempt_id
        )
        .join(
            CandidateRegistration,
            ExamAttempt.registration_id ==
            CandidateRegistration.registration_id
        )
        .join(
            Exam,
            CandidateRegistration.exam_id == Exam.exam_id
        )
        .join(
            Subject,
            Exam.subject_id == Subject.subject_id
        )
        .join(
            Student,
            CandidateRegistration.student_id == Student.student_id
        )
        .join(
            User,
            Student.user_id == User.user_id
        )
        .order_by(Result.result_id.asc())
        .all()
    )

    return results

def get_exam_results_for_admin(exam_id):
    """Return all generated results for a specific examination."""

    try:
        exam_id = int(exam_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid exam ID.")

    exam = Exam.query.filter_by(
        exam_id=exam_id
    ).first()

    if exam is None:
        raise ValueError("Exam not found.")

    results = (
        db.session.query(
            Result,
            ExamAttempt,
            CandidateRegistration,
            Student,
            User,
        )
        .join(
            ExamAttempt,
            Result.attempt_id == ExamAttempt.attempt_id
        )
        .join(
            CandidateRegistration,
            ExamAttempt.registration_id ==
            CandidateRegistration.registration_id
        )
        .join(
            Student,
            CandidateRegistration.student_id == Student.student_id
        )
        .join(
            User,
            Student.user_id == User.user_id
        )
        .filter(
            CandidateRegistration.exam_id == exam_id
        )
        .order_by(Result.result_id.asc())
        .all()
    )

    return exam, results

def get_result_by_id(result_id):
    """Return one result with complete exam and student details."""

    try:
        result_id = int(result_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid result ID.")

    result = (
        db.session.query(
            Result,
            ExamAttempt,
            CandidateRegistration,
            Exam,
            Subject,
            Student,
            User,
        )
        .join(
            ExamAttempt,
            Result.attempt_id == ExamAttempt.attempt_id
        )
        .join(
            CandidateRegistration,
            ExamAttempt.registration_id ==
            CandidateRegistration.registration_id
        )
        .join(
            Exam,
            CandidateRegistration.exam_id == Exam.exam_id
        )
        .join(
            Subject,
            Exam.subject_id == Subject.subject_id
        )
        .join(
            Student,
            CandidateRegistration.student_id == Student.student_id
        )
        .join(
            User,
            Student.user_id == User.user_id
        )
        .filter(
            Result.result_id == result_id
        )
        .first()
    )

    if result is None:
        raise ValueError("Result not found.")

    return result

def get_dashboard_statistics():
    """
    Return summary statistics for the Admin dashboard.
    """

    total_users = User.query.count()

    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = User.query.filter_by(is_active=False).count()

    total_faculty = Faculty.query.count()
    active_faculty = (
        db.session.query(Faculty)
        .join(User, Faculty.user_id == User.user_id)
        .filter(User.is_active == True)
        .count()
    )

    total_students = Student.query.count()
    active_students = (
        db.session.query(Student)
        .join(User, Student.user_id == User.user_id)
        .filter(User.is_active == True)
        .count()
    )

    total_subjects = Subject.query.count()
    active_subjects = Subject.query.filter_by(is_active=True).count()
    inactive_subjects = Subject.query.filter_by(is_active=False).count()

    total_exams = Exam.query.count()

    total_questions = Question.query.count()
    active_questions = Question.query.filter_by(is_active=True).count()
    inactive_questions = Question.query.filter_by(is_active=False).count()

    total_registrations = CandidateRegistration.query.count()

    total_attempts = ExamAttempt.query.count()

    in_progress_attempts = (
        ExamAttempt.query
        .filter(ExamAttempt.status == 'InProgress')
        .count()
    )

    submitted_attempts = (
        ExamAttempt.query
        .filter(ExamAttempt.status == 'Submitted')
        .count()
    )

    auto_submitted_attempts = (
        ExamAttempt.query
        .filter(ExamAttempt.status == 'AutoSubmitted')
        .count()
    )

    total_results = Result.query.count()

    passed_results = (
        Result.query
        .filter(Result.result_status == 'Pass')
        .count()
    )

    failed_results = (
        Result.query
        .filter(Result.result_status == 'Fail')
        .count()
    )

    pending_results = (
        Result.query
        .filter(Result.result_status == 'Pending')
        .count()
    )

    total_faculty_subject_assignments = FacultySubject.query.count()

    active_faculty_subject_assignments = (
        FacultySubject.query
        .filter(FacultySubject.is_active == True)
        .count()
    )

    total_integrity_events = (
        AuditLog.query
        .filter(
            AuditLog.entity_type == 'ExamAttempt',
            AuditLog.action.in_([
                'TAB_SWITCH',
                'WINDOW_BLUR',
                'FULLSCREEN_EXIT',
                'PAGE_HIDDEN',
            ])
        )
        .count()
    )

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": inactive_users,
        },

        "faculty": {
            "total": total_faculty,
            "active": active_faculty,
        },

        "students": {
            "total": total_students,
            "active": active_students,
        },

        "subjects": {
            "total": total_subjects,
            "active": active_subjects,
            "inactive": inactive_subjects,
        },

        "exams": {
            "total": total_exams,
        },

        "questions": {
            "total": total_questions,
            "active": active_questions,
            "inactive": inactive_questions,
        },

        "registrations": {
            "total": total_registrations,
        },

        "attempts": {
            "total": total_attempts,
            "in_progress": in_progress_attempts,
            "submitted": submitted_attempts,
            "auto_submitted": auto_submitted_attempts,
        },

        "results": {
            "total": total_results,
            "passed": passed_results,
            "failed": failed_results,
            "pending": pending_results,
        },

        "faculty_subject_assignments": {
            "total": total_faculty_subject_assignments,
            "active": active_faculty_subject_assignments,
        },

        "integrity_events": {
            "total": total_integrity_events,
        },
    }

def get_all_audit_logs():
    """
    Return all audit logs with associated user information.
    """
    results = (
        db.session.query(AuditLog, User)
        .outerjoin(User, AuditLog.user_id == User.user_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return results


def get_audit_log_by_id(audit_id):
    """
    Return a single audit log with associated user information.
    """
    if not isinstance(audit_id, int) or audit_id <= 0:
        raise ValueError("Invalid audit log ID.")

    result = (
        db.session.query(AuditLog, User)
        .outerjoin(User, AuditLog.user_id == User.user_id)
        .filter(AuditLog.audit_id == audit_id)
        .first()
    )

    if not result:
        raise ValueError("Audit log not found.")

    return result