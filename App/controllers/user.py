from App.models import User, Student, Company, Staff, InternshipPosition, Application, Notification
from App.database import db
from werkzeug.security import generate_password_hash


# User Functions---------------------User Functions------------------User Functions------------------User Functions
def create_user(username, password, email, name, user_type, **kwargs):
    newuser = User(username=username, password=password, email=email, name=name, user_type=user_type)

    db.session.add(newuser)
    db.session.commit()
    return newuser


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_user(id):
    return User.query.get(id)

def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        db.session.add(user)
        return db.session.commit()
    return None




# Student Functions----------------------------Student Functions----------------------------Student Functions----------------------------Student Functions

def get_student_by_id(student_id):
    """Get student by ID"""
    return Student.query.get(student_id)




def apply_to_position(student_id, position_id, cover_letter=None):
    existing_application = Application.query.filter_by(
        student_id=student_id, 
        position_id=position_id
    ).first()
    
    if existing_application:
        return None
    
    position = InternshipPosition.query.get(position_id)
    if not position or not position.is_active:
        return None
    
    application = Application(
        student_id=student_id,
        position_id=position_id,
        cover_letter=cover_letter
    )
    
    db.session.add(application)
    db.session.commit()
    return application

def get_student_applications(student_id):
    return Application.query.filter_by(student_id=student_id).order_by(Application.application_date.desc()).all()

def get_available_positions(student_id):
    # Get positions the student hasn't applied to
    applied_positions = db.session.query(Application.position_id).filter_by(student_id=student_id)
    return InternshipPosition.query.filter(
        InternshipPosition.is_active == True,
        InternshipPosition.id.notin_(applied_positions)
    ).order_by(InternshipPosition.created_at.desc()).all()

def get_profile_completeness(student_id):
    student = Student.query.get(student_id)
    if not student:
        return 0
    
    required_fields = [
        student.student_id,
        student.university,
        student.major,
        student.graduation_year,
        student.skills
    ]
    
    completed = sum(1 for field in required_fields if field)
    return int((completed / len(required_fields)) * 100)



def update_student_profile(student_id, **kwargs):
    """Update student profile information"""
    student = Student.query.get(student_id)
    if not student:
        return False
    
    for key, value in kwargs.items():
        if hasattr(student, key) and value is not None:
            setattr(student, key, value)
    
    db.session.commit()
    return True


def match_student_to_positions(student_id):
    """Match student skills to available positions"""
    student = Student.query.get(student_id)
    if not student or not student.skills:
        return []
    
    student_skills = set(skill.strip().lower() for skill in student.skills.split(','))
    positions = InternshipPosition.query.filter_by(is_active=True).all()
    
    matches = []
    for position in positions:
        if not position.skills_required:
            continue
            
        required_skills = set(skill.strip().lower() for skill in position.skills_required.split(','))
        matched_skills = student_skills.intersection(required_skills)
        match_percentage = len(matched_skills) / len(required_skills) * 100 if required_skills else 0
        
        if match_percentage >= 30:  # Only show positions with at least 30% match
            matches.append({
                'position': position,
                'match_percentage': round(match_percentage),
                'matched_skills': ', '.join(matched_skills)
            })
    
    return sorted(matches, key=lambda x: x['match_percentage'], reverse=True)[:5]  # Return top 5 matches





# Company Functions-----------------------------Company Functions----------------------------Company Functions----------------------------Company Functions
def create_internship_position(company_id, title, description, requirements, **kwargs):
    position = InternshipPosition(
        company_id=company_id,
        title=title,
        description=description,
        requirements=requirements,
        location=kwargs.get('location'),
        salary=kwargs.get('salary'),
        duration=kwargs.get('duration'),
        deadline=kwargs.get('deadline'),
        skills_required=kwargs.get('skills_required')
    )
    
    db.session.add(position)
    db.session.commit()
    return position

def get_company_positions(company_id):
    return InternshipPosition.query.filter_by(company_id=company_id).order_by(InternshipPosition.created_at.desc()).all()

def get_position_applications(position_id):
    return Application.query.filter_by(position_id=position_id).order_by(Application.application_date.desc()).all()

def update_application_status(application_id, status, notes=None):
    application = Application.query.get(application_id)
    if not application:
        return None
    
    application.status = status
    if notes:
        application.notes = notes
    
    # Create notification for student
    notification = Notification(
        user_id=application.student.id,
        message=f"Your application for {application.position.title} has been {status}",
        link=f"/applications"
    )
    db.session.add(notification)
    
    db.session.commit()
    return application






# Staff Functions---------------------Staff Functions------------------Staff Functions------------------Staff Functions
def get_all_applications():
    return Application.query.order_by(Application.application_date.desc()).all()

def shortlist_application(application_id, notes=None):
    return update_application_status(application_id, 'shortlisted', notes)

def reject_application(application_id, notes=None):
    return update_application_status(application_id, 'rejected', notes)

def hire_application(application_id, notes=None):
    return update_application_status(application_id, 'hired', notes)





# Notification Functions-------------------Notification Functions------------------Notification Functions------------------Notification Functions
def get_user_notifications(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at.desc()).all()

def mark_notification_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification:
        notification.is_read = True
        db.session.commit()
        return True
    return False




# Search Functions--------------------Search Functions------------------Search Functions------------------Search Functions------------------
def search_positions(keyword=None, location=None, company=None, skill=None):
    query = InternshipPosition.query.filter_by(is_active=True)
    
    if keyword:
        query = query.filter(
            (InternshipPosition.title.ilike(f'%{keyword}%')) |
            (InternshipPosition.description.ilike(f'%{keyword}%'))
        )
    
    if location:
        query = query.filter(InternshipPosition.location.ilike(f'%{location}%'))
    
    if company:
        query = query.join(Company).filter(Company.name.ilike(f'%{company}%'))
    
    if skill:
        query = query.filter(InternshipPosition.skills_required.ilike(f'%{skill}%'))
    
    return query.order_by(InternshipPosition.created_at.desc()).all()



    