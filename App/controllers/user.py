from App.models import User, Student, Company, Staff, InternshipPosition, Application, Notification
from App.database import db
from werkzeug.security import generate_password_hash

def create_user(username, password, email, name, user_type, **kwargs):
    newuser = User(username=username, password=password, email=email, name=name, user_type=user_type)
    if newuser:
        db.session.add(newuser)
        db.session.commit()
        return newuser
    
    try:
        if user_type == 'student':
            user = Student(
                username=username,
                password=generate_password_hash(password),
                email=email,
                name=name,
                student_id=kwargs.get('student_id'),
                university=kwargs.get('university'),
                major=kwargs.get('major'),
                graduation_year=kwargs.get('graduation_year'),
                gpa=kwargs.get('gpa'),
                skills=kwargs.get('skills')
            )

        elif user_type == 'company':
            user = Company(
                username=username,
                password=generate_password_hash(password),
                email=email,
                name=name,
                company_id=kwargs.get('company_id'),
                industry=kwargs.get('industry'),
                website=kwargs.get('website'),
                description=kwargs.get('description')
            )

        elif user_type == 'staff':
            user = Staff(
                username=username,
                password=generate_password_hash(password),
                email=email,
                name=name,
                staff_id=kwargs.get('staff_id'),
                department=kwargs.get('department')
            )
        else:
            return None
        
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {str(e)}")
        return None



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



    