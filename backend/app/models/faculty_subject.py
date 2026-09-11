"""
FacultySubject model - represents subject assignments to faculty.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class FacultySubject(db.Model):
    """
    Represents the assignment of a subject to a faculty member
    for a particular semester and academic year.
    """

    __tablename__ = 'FacultySubject'

    faculty_subject_id = db.Column(
        'FacultySubjectID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    faculty_id = db.Column(
        'FacultyID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Faculty.FacultyID',
            name='fk_faculty_subject_faculty',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    subject_id = db.Column(
        'SubjectID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Subject.SubjectID',
            name='fk_faculty_subject_subject',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    semester = db.Column(
        'Semester',
        db.SmallInteger,
        nullable=False
    )

    year = db.Column(
        'Year',
        db.Integer,
        nullable=False
    )

    is_active = db.Column(
        'IsActive',
        db.Boolean,
        nullable=False,
        default=True
    )

    assigned_at = db.Column(
        'AssignedAt',
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    # Faculty 1 ───── M FacultySubject
    faculty = db.relationship(
        'Faculty',
        back_populates='subject_assignments'
    )

    # Subject 1 ───── M FacultySubject
    subject = db.relationship(
        'Subject',
        back_populates='faculty_assignments'
    )

    __table_args__ = (
        db.CheckConstraint(
            'Semester > 0',
            name='chk_faculty_subject_semester'
        ),

        db.CheckConstraint(
            'Year > 0',
            name='chk_faculty_subject_year'
        ),

        db.Index(
            'idx_faculty_subject_faculty',
            'FacultyID'
        ),

        db.Index(
            'idx_faculty_subject_subject',
            'SubjectID'
        ),

        db.Index(
            'idx_faculty_subject_active',
            'IsActive'
        ),

        db.UniqueConstraint(
            'FacultyID',
            'SubjectID',
            'Semester',
            'Year',
            name='uq_faculty_subject_assignment'
        ),
    )

    def __repr__(self) -> str:
        return (
            f'<FacultySubject faculty={self.faculty_id} '
            f'subject={self.subject_id} '
            f'semester={self.semester} '
            f'year={self.year}>'
        )