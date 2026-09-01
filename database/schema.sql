/* ============================================================
   FINALDB - ONLINE EXAMINATION PLATFORM
   DATABASE + TABLES ONLY
   MySQL 8.x
   ============================================================ */


/* ============================================================
   1. CREATE DATABASE
   ============================================================ */

CREATE DATABASE IF NOT EXISTS finaldb
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE finaldb;


/* ============================================================
   2. ROLE
   ============================================================ */

CREATE TABLE Role (
    RoleID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    RoleName VARCHAR(30) NOT NULL,
    Description VARCHAR(255) NULL,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_role_name
        UNIQUE (RoleName),

    CONSTRAINT chk_role_name
        CHECK (TRIM(RoleName) <> '')
) ENGINE = InnoDB;


/* ============================================================
   3. USER
   ============================================================ */

CREATE TABLE User (
    UserID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    RoleID BIGINT UNSIGNED NOT NULL,

    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,

    Email VARCHAR(255) NOT NULL,
    Phone VARCHAR(15) NULL,

    PasswordHash VARCHAR(255) NOT NULL,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UpdatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_user_email
        UNIQUE (Email),

    CONSTRAINT uq_user_phone
        UNIQUE (Phone),

    CONSTRAINT fk_user_role
        FOREIGN KEY (RoleID)
        REFERENCES Role(RoleID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_user_first_name
        CHECK (TRIM(FirstName) <> ''),

    CONSTRAINT chk_user_last_name
        CHECK (TRIM(LastName) <> ''),

    CONSTRAINT chk_user_email
        CHECK (Email LIKE '%@%'),

    INDEX idx_user_role (RoleID),
    INDEX idx_user_active (IsActive)
) ENGINE = InnoDB;


/* ============================================================
   4. DEPARTMENT
   ============================================================ */

CREATE TABLE Department (
    DepartmentID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    DepartmentCode VARCHAR(20) NOT NULL,
    DepartmentName VARCHAR(100) NOT NULL,

    Description VARCHAR(255) NULL,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_department_code
        UNIQUE (DepartmentCode),

    CONSTRAINT uq_department_name
        UNIQUE (DepartmentName),

    CONSTRAINT chk_department_code
        CHECK (TRIM(DepartmentCode) <> ''),

    CONSTRAINT chk_department_name
        CHECK (TRIM(DepartmentName) <> ''),

    INDEX idx_department_active (IsActive)
) ENGINE = InnoDB;


/* ============================================================
   5. STUDENT
   ============================================================ */

CREATE TABLE Student (
    StudentID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    UserID BIGINT UNSIGNED NOT NULL,
    DepartmentID BIGINT UNSIGNED NOT NULL,

    RollNumber VARCHAR(30) NOT NULL,
    EnrollmentNumber VARCHAR(30) NOT NULL,

    Year SMALLINT NOT NULL,
    Semester SMALLINT NOT NULL,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_student_user
        UNIQUE (UserID),

    CONSTRAINT uq_student_roll
        UNIQUE (RollNumber),

    CONSTRAINT uq_student_enrollment
        UNIQUE (EnrollmentNumber),

    CONSTRAINT fk_student_user
        FOREIGN KEY (UserID)
        REFERENCES User(UserID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_student_department
        FOREIGN KEY (DepartmentID)
        REFERENCES Department(DepartmentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_student_roll
        CHECK (TRIM(RollNumber) <> ''),

    CONSTRAINT chk_student_enrollment
        CHECK (TRIM(EnrollmentNumber) <> ''),

    CONSTRAINT chk_student_year
        CHECK (Year > 0),

    CONSTRAINT chk_student_semester
        CHECK (Semester > 0),

    INDEX idx_student_department (DepartmentID),
    INDEX idx_student_active (IsActive)
) ENGINE = InnoDB;


/* ============================================================
   6. FACULTY
   ============================================================ */

CREATE TABLE Faculty (
    FacultyID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    UserID BIGINT UNSIGNED NOT NULL,
    DepartmentID BIGINT UNSIGNED NOT NULL,

    EmployeeID VARCHAR(30) NOT NULL,
    Designation VARCHAR(50) NULL,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_faculty_user
        UNIQUE (UserID),

    CONSTRAINT uq_faculty_employee
        UNIQUE (EmployeeID),

    CONSTRAINT fk_faculty_user
        FOREIGN KEY (UserID)
        REFERENCES User(UserID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_faculty_department
        FOREIGN KEY (DepartmentID)
        REFERENCES Department(DepartmentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_faculty_employee
        CHECK (TRIM(EmployeeID) <> ''),

    INDEX idx_faculty_department (DepartmentID),
    INDEX idx_faculty_active (IsActive)
) ENGINE = InnoDB;


/* ============================================================
   7. SUBJECT
   ============================================================ */

CREATE TABLE Subject (
    SubjectID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    DepartmentID BIGINT UNSIGNED NOT NULL,

    SubjectCode VARCHAR(20) NOT NULL,
    SubjectName VARCHAR(100) NOT NULL,

    Description TEXT NULL,

    Credits SMALLINT NOT NULL DEFAULT 0,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CreatedBy BIGINT UNSIGNED NULL,

    CONSTRAINT uq_subject_code
        UNIQUE (SubjectCode),

    CONSTRAINT uq_subject_department_name
        UNIQUE (DepartmentID, SubjectName),

    CONSTRAINT fk_subject_department
        FOREIGN KEY (DepartmentID)
        REFERENCES Department(DepartmentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_subject_created_by
        FOREIGN KEY (CreatedBy)
        REFERENCES User(UserID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT chk_subject_code
        CHECK (TRIM(SubjectCode) <> ''),

    CONSTRAINT chk_subject_name
        CHECK (TRIM(SubjectName) <> ''),

    CONSTRAINT chk_subject_credits
        CHECK (Credits >= 0),

    INDEX idx_subject_department (DepartmentID),
    INDEX idx_subject_created_by (CreatedBy),
    INDEX idx_subject_active (IsActive)
) ENGINE = InnoDB;


/* ============================================================
   8. EXAM
   ============================================================ */

CREATE TABLE Exam (
    ExamID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    SubjectID BIGINT UNSIGNED NOT NULL,
    CreatedBy BIGINT UNSIGNED NOT NULL,

    ExamCode VARCHAR(30) NOT NULL,
    ExamTitle VARCHAR(150) NOT NULL,

    ExamType VARCHAR(30) NOT NULL,

    TotalMarks DECIMAL(6,2) NOT NULL,
    PassingMarks DECIMAL(6,2) NOT NULL,

    DurationMinutes INT NOT NULL,

    Instructions TEXT NULL,

    MaximumAttempts SMALLINT NOT NULL DEFAULT 1,

    ShuffleQuestions BOOLEAN NOT NULL DEFAULT TRUE,
    ShuffleOptions BOOLEAN NOT NULL DEFAULT TRUE,

    NegativeMarking BOOLEAN NOT NULL DEFAULT FALSE,

    NegativeMarksPerQuestion DECIMAL(5,2) NOT NULL DEFAULT 0.00,

    ExamStatus ENUM(
        'DRAFT',
        'SCHEDULED',
        'ACTIVE',
        'COMPLETED',
        'CANCELLED'
    ) NOT NULL DEFAULT 'DRAFT',

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_exam_code
        UNIQUE (ExamCode),

    CONSTRAINT fk_exam_subject
        FOREIGN KEY (SubjectID)
        REFERENCES Subject(SubjectID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_exam_created_by
        FOREIGN KEY (CreatedBy)
        REFERENCES User(UserID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_exam_code
        CHECK (TRIM(ExamCode) <> ''),

    CONSTRAINT chk_exam_title
        CHECK (TRIM(ExamTitle) <> ''),

    CONSTRAINT chk_exam_type
        CHECK (TRIM(ExamType) <> ''),

    CONSTRAINT chk_exam_total_marks
        CHECK (TotalMarks > 0),

    CONSTRAINT chk_exam_passing_marks
        CHECK (
            PassingMarks >= 0
            AND PassingMarks <= TotalMarks
        ),

    CONSTRAINT chk_exam_duration
        CHECK (DurationMinutes > 0),

    CONSTRAINT chk_exam_max_attempts
        CHECK (MaximumAttempts >= 1),

    CONSTRAINT chk_exam_negative_marks
        CHECK (NegativeMarksPerQuestion >= 0),

    INDEX idx_exam_subject (SubjectID),
    INDEX idx_exam_created_by (CreatedBy),
    INDEX idx_exam_status (ExamStatus),
    INDEX idx_exam_active (IsActive)
) ENGINE = InnoDB;


/* ============================================================
   9. EXAM SCHEDULE
   ============================================================ */

CREATE TABLE ExamSchedule (
    ScheduleID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    ExamID BIGINT UNSIGNED NOT NULL,

    StartTime DATETIME NOT NULL,
    EndTime DATETIME NOT NULL,

    RegistrationStart DATETIME NULL,
    RegistrationEnd DATETIME NULL,

    LateEntryMinutes INT NOT NULL DEFAULT 0,

    ScheduleStatus ENUM(
        'SCHEDULED',
        'ONGOING',
        'COMPLETED',
        'CANCELLED'
    ) NOT NULL DEFAULT 'SCHEDULED',

    CONSTRAINT fk_exam_schedule_exam
        FOREIGN KEY (ExamID)
        REFERENCES Exam(ExamID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_schedule_time
        CHECK (EndTime > StartTime),

    CONSTRAINT chk_registration_time
        CHECK (
            RegistrationStart IS NULL
            OR RegistrationEnd IS NULL
            OR RegistrationEnd >= RegistrationStart
        ),

    CONSTRAINT chk_late_entry
        CHECK (LateEntryMinutes >= 0),

    INDEX idx_schedule_exam (ExamID),
    INDEX idx_schedule_start (StartTime),
    INDEX idx_schedule_status (ScheduleStatus)
) ENGINE = InnoDB;


/* ============================================================
   10. QUESTION
   ============================================================ */

CREATE TABLE Question (
    QuestionID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    SubjectID BIGINT UNSIGNED NOT NULL,
    CreatedBy BIGINT UNSIGNED NOT NULL,

    QuestionType ENUM(
        'MCQ',
        'MSQ',
        'TRUE_FALSE',
        'SHORT_ANSWER',
        'DESCRIPTIVE'
    ) NOT NULL,

    QuestionText TEXT NOT NULL,

    Explanation TEXT NULL,

    DefaultMarks DECIMAL(5,2) NOT NULL DEFAULT 1.00,

    NegativeMarks DECIMAL(5,2) NOT NULL DEFAULT 0.00,

    DifficultyLevel ENUM(
        'EASY',
        'MEDIUM',
        'HARD'
    ) NOT NULL DEFAULT 'MEDIUM',

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_question_subject
        FOREIGN KEY (SubjectID)
        REFERENCES Subject(SubjectID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_question_created_by
        FOREIGN KEY (CreatedBy)
        REFERENCES User(UserID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_question_text
        CHECK (TRIM(QuestionText) <> ''),

    CONSTRAINT chk_question_default_marks
        CHECK (DefaultMarks > 0),

    CONSTRAINT chk_question_negative_marks
        CHECK (NegativeMarks >= 0),

    INDEX idx_question_subject (SubjectID),
    INDEX idx_question_created_by (CreatedBy),
    INDEX idx_question_type (QuestionType),
    INDEX idx_question_difficulty (DifficultyLevel),
    INDEX idx_question_active (IsActive)
) ENGINE = InnoDB;


/* ============================================================
   11. QUESTION OPTION
   ============================================================ */

CREATE TABLE QuestionOption (
    OptionID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    QuestionID BIGINT UNSIGNED NOT NULL,

    OptionText TEXT NOT NULL,

    OptionOrder INT NOT NULL,

    IsCorrect BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_question_option_question
        FOREIGN KEY (QuestionID)
        REFERENCES Question(QuestionID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT uq_question_option_order
        UNIQUE (QuestionID, OptionOrder),

    CONSTRAINT chk_option_text
        CHECK (TRIM(OptionText) <> ''),

    CONSTRAINT chk_option_order
        CHECK (OptionOrder > 0),

    INDEX idx_question_option_question (QuestionID)
) ENGINE = InnoDB;


/* ============================================================
   12. EXAM QUESTION
   ============================================================ */

CREATE TABLE ExamQuestion (
    ExamQuestionID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    ExamID BIGINT UNSIGNED NOT NULL,
    QuestionID BIGINT UNSIGNED NOT NULL,

    QuestionOrder INT NOT NULL,

    Marks DECIMAL(5,2) NOT NULL,

    NegativeMarks DECIMAL(5,2) NOT NULL DEFAULT 0.00,

    IsMandatory BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_exam_question_exam
        FOREIGN KEY (ExamID)
        REFERENCES Exam(ExamID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_exam_question_question
        FOREIGN KEY (QuestionID)
        REFERENCES Question(QuestionID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT uq_exam_question
        UNIQUE (ExamID, QuestionID),

    CONSTRAINT uq_exam_question_order
        UNIQUE (ExamID, QuestionOrder),

    CONSTRAINT chk_exam_question_order
        CHECK (QuestionOrder > 0),

    CONSTRAINT chk_exam_question_marks
        CHECK (Marks > 0),

    CONSTRAINT chk_exam_question_negative_marks
        CHECK (NegativeMarks >= 0),

    INDEX idx_exam_question_exam (ExamID),
    INDEX idx_exam_question_question (QuestionID)
) ENGINE = InnoDB;


/* ============================================================
   13. CANDIDATE REGISTRATION
   ============================================================ */

CREATE TABLE CandidateRegistration (
    RegistrationID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    ExamID BIGINT UNSIGNED NOT NULL,
    StudentID BIGINT UNSIGNED NOT NULL,

    RegistrationTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    RegistrationStatus ENUM(
        'REGISTERED',
        'CANCELLED',
        'WAITLISTED'
    ) NOT NULL DEFAULT 'REGISTERED',

    EligibilityVerified BOOLEAN NOT NULL DEFAULT FALSE,

    Remarks VARCHAR(255) NULL,

    CONSTRAINT fk_registration_exam
        FOREIGN KEY (ExamID)
        REFERENCES Exam(ExamID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_registration_student
        FOREIGN KEY (StudentID)
        REFERENCES Student(StudentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT uq_exam_student_registration
        UNIQUE (ExamID, StudentID),

    INDEX idx_registration_exam (ExamID),
    INDEX idx_registration_student (StudentID),
    INDEX idx_registration_status (RegistrationStatus)
) ENGINE = InnoDB;


/* ============================================================
   14. EXAM ATTEMPT
   ============================================================ */

CREATE TABLE ExamAttempt (
    AttemptID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    RegistrationID BIGINT UNSIGNED NOT NULL,

    AttemptNumber SMALLINT NOT NULL DEFAULT 1,

    StartTime DATETIME NOT NULL,

    EndTime DATETIME NULL,

    SubmittedAt DATETIME NULL,

    Status ENUM(
        'NOT_STARTED',
        'IN_PROGRESS',
        'SUBMITTED',
        'AUTO_SUBMITTED',
        'EVALUATED',
        'ABANDONED'
    ) NOT NULL DEFAULT 'NOT_STARTED',

    TotalTimeSpentSeconds INT NOT NULL DEFAULT 0,

    IPAddress VARCHAR(45) NULL,

    SubmissionMethod ENUM(
        'MANUAL',
        'AUTO'
    ) NULL,

    AutoSubmitted BOOLEAN NOT NULL DEFAULT FALSE,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UpdatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_attempt_registration
        FOREIGN KEY (RegistrationID)
        REFERENCES CandidateRegistration(RegistrationID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT uq_registration_attempt
        UNIQUE (RegistrationID, AttemptNumber),

    CONSTRAINT chk_attempt_number
        CHECK (AttemptNumber >= 1),

    CONSTRAINT chk_attempt_time
        CHECK (TotalTimeSpentSeconds >= 0),

    CONSTRAINT chk_attempt_end_time
        CHECK (
            EndTime IS NULL
            OR EndTime >= StartTime
        ),

    CONSTRAINT chk_attempt_submitted_time
        CHECK (
            SubmittedAt IS NULL
            OR SubmittedAt >= StartTime
        ),

    INDEX idx_attempt_registration (RegistrationID),
    INDEX idx_attempt_status (Status),
    INDEX idx_attempt_start (StartTime)
) ENGINE = InnoDB;


/* ============================================================
   15. STUDENT ANSWER
   ============================================================ */

CREATE TABLE StudentAnswer (
    AnswerID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    AttemptID BIGINT UNSIGNED NOT NULL,
    QuestionID BIGINT UNSIGNED NOT NULL,

    SelectedOptionID BIGINT UNSIGNED NULL,

    AnswerText TEXT NULL,

    IsMarkedForReview BOOLEAN NOT NULL DEFAULT FALSE,

    IsAnswered BOOLEAN NOT NULL DEFAULT FALSE,

    SubmittedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    TimeSpentSeconds INT NOT NULL DEFAULT 0,

    CONSTRAINT fk_answer_attempt
        FOREIGN KEY (AttemptID)
        REFERENCES ExamAttempt(AttemptID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_answer_question
        FOREIGN KEY (QuestionID)
        REFERENCES Question(QuestionID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_answer_option
        FOREIGN KEY (SelectedOptionID)
        REFERENCES QuestionOption(OptionID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT uq_attempt_question
        UNIQUE (AttemptID, QuestionID),

    CONSTRAINT chk_answer_time
        CHECK (TimeSpentSeconds >= 0),

    INDEX idx_answer_attempt (AttemptID),
    INDEX idx_answer_question (QuestionID),
    INDEX idx_answer_option (SelectedOptionID)
) ENGINE = InnoDB;


/* ============================================================
   16. RESULT
   ============================================================ */

CREATE TABLE Result (
    ResultID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    AttemptID BIGINT UNSIGNED NOT NULL,

    TotalMarksObtained DECIMAL(6,2) NOT NULL DEFAULT 0.00,

    Percentage DECIMAL(5,2) NOT NULL DEFAULT 0.00,

    TotalCorrect INT NOT NULL DEFAULT 0,

    TotalWrong INT NOT NULL DEFAULT 0,

    TotalSkipped INT NOT NULL DEFAULT 0,

    Grade VARCHAR(5) NULL,

    PassStatus BOOLEAN NOT NULL,

    ResultStatus ENUM(
        'GENERATED',
        'PUBLISHED'
    ) NOT NULL DEFAULT 'GENERATED',

    PublishedAt DATETIME NULL,

    PublishedBy BIGINT UNSIGNED NULL,

    Remarks TEXT NULL,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UpdatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_result_attempt
        UNIQUE (AttemptID),

    CONSTRAINT fk_result_attempt
        FOREIGN KEY (AttemptID)
        REFERENCES ExamAttempt(AttemptID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_result_published_by
        FOREIGN KEY (PublishedBy)
        REFERENCES User(UserID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT chk_result_marks
        CHECK (TotalMarksObtained >= 0),

    CONSTRAINT chk_result_percentage
        CHECK (
            Percentage >= 0
            AND Percentage <= 100
        ),

    CONSTRAINT chk_result_correct
        CHECK (TotalCorrect >= 0),

    CONSTRAINT chk_result_wrong
        CHECK (TotalWrong >= 0),

    CONSTRAINT chk_result_skipped
        CHECK (TotalSkipped >= 0),

    INDEX idx_result_status (ResultStatus),
    INDEX idx_result_published_by (PublishedBy)
) ENGINE = InnoDB;


/* ============================================================
   17. NOTIFICATION
   ============================================================ */

CREATE TABLE Notification (
    NotificationID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    UserID BIGINT UNSIGNED NOT NULL,

    Title VARCHAR(150) NOT NULL,

    Message TEXT NOT NULL,

    NotificationType ENUM(
        'EXAM',
        'RESULT',
        'SYSTEM',
        'REMINDER'
    ) NOT NULL DEFAULT 'SYSTEM',

    IsRead BOOLEAN NOT NULL DEFAULT FALSE,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    ReadAt DATETIME NULL,

    IsActive BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_notification_user
        FOREIGN KEY (UserID)
        REFERENCES User(UserID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_notification_title
        CHECK (TRIM(Title) <> ''),

    CONSTRAINT chk_notification_message
        CHECK (TRIM(Message) <> ''),

    INDEX idx_notification_user (UserID),
    INDEX idx_notification_read (IsRead),
    INDEX idx_notification_type (NotificationType),
    INDEX idx_notification_created (CreatedAt)
) ENGINE = InnoDB;


/* ============================================================
   18. AUDIT LOG
   ============================================================ */

CREATE TABLE AuditLog (
    AuditLogID BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    UserID BIGINT UNSIGNED NULL,

    ExamAttemptID BIGINT UNSIGNED NULL,

    Module VARCHAR(50) NOT NULL,

    Action VARCHAR(50) NOT NULL,

    EntityName VARCHAR(50) NULL,

    RecordID BIGINT UNSIGNED NULL,

    Status VARCHAR(20) NOT NULL,

    IPAddress VARCHAR(45) NULL,

    Details TEXT NULL,

    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (UserID)
        REFERENCES User(UserID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT fk_audit_attempt
        FOREIGN KEY (ExamAttemptID)
        REFERENCES ExamAttempt(AttemptID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT chk_audit_module
        CHECK (TRIM(Module) <> ''),

    CONSTRAINT chk_audit_action
        CHECK (TRIM(Action) <> ''),

    CONSTRAINT chk_audit_status
        CHECK (TRIM(Status) <> ''),

    INDEX idx_audit_user (UserID),
    INDEX idx_audit_attempt (ExamAttemptID),
    INDEX idx_audit_module_action (Module, Action),
    INDEX idx_audit_entity (EntityName, RecordID),
    INDEX idx_audit_created (CreatedAt)
) ENGINE = InnoDB;


/* ============================================================
   END OF DATABASE FOUNDATION
   ============================================================ */