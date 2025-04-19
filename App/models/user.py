from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # student, company, staff

    def __init__(self, username, password, email, name, user_type):
        self.username = username
        self.set_password(password)
        self.email = email
        self.name = name
        self.user_type = user_type
       

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'user_type': self.user_type,
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)


class Student(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    student_id = db.Column(db.String(20), unique=True)
    university = db.Column(db.String(120))
    major = db.Column(db.String(120))
    graduation_year = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    skills = db.Column(db.Text)
    resume_url = db.Column(db.String(256))
    applications = db.relationship('Application', backref='student', lazy=True)
    
    def __init__(self, username, password, email, name, student_id=None, university=None, 
                major=None, graduation_year=None, gpa=None, skills=None):
        super().__init__(
            username=username,
            password=password,
            email=email,
            name=name,
            user_type='student'
        )
        self.student_id = student_id
        self.university = university
        self.major = major
        self.graduation_year = graduation_year
        self.gpa = gpa
        self.skills = skills

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    
class Company(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_id = db.Column(db.String(20), unique=True)
    industry = db.Column(db.String(120))
    website = db.Column(db.String(120))
    description = db.Column(db.Text)
    
    def __init__(self, username, password, email, name, company_id=None, 
                industry=None, website=None, description=None):
        super().__init__(
            username=username,
            password=password,
            email=email,
            name=name,
            user_type='company'
        )
        self.company_id = company_id
        self.industry = industry
        self.website = website
        self.description = description

class Staff(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    staff_id = db.Column(db.String(20), unique=True)
    department = db.Column(db.String(120))
    
    def __init__(self, username, password, email, name, staff_id=None, department=None):
        super().__init__(
            username=username,
            password=password,
            email=email,
            name=name,
            user_type='staff'
        )
        self.staff_id = staff_id
        self.department = department

class InternshipPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(120))
    salary = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    deadline = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    applications = db.relationship('Application', backref='position', lazy=True)
    skills_required = db.Column(db.Text)  # Comma-separated skills

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('internship_position.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, shortlisted, rejected, hired
    cover_letter = db.Column(db.Text)
    notes = db.Column(db.Text)  # Staff notes about the application

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(256)) 

