from .user import create_user
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()
    
    # Create test users
    create_user(
        username='bob',
        password='bobpass',
        email='bob@example.com',
        name='Bob Smith',
        user_type='student',
        student_id='S12345',
        university='State University',
        major='Computer Science',
        graduation_year=2024,
        gpa=3.8,
        skills='Python, Java, SQL'
    )
    
    create_user(
        username='acme',
        password='acmepass',
        email='acme@example.com',
        name='ACME Corp',
        user_type='company',
        company_id='C1001',
        industry='Technology',
        website='www.acme.com',
        description='Leading tech company'
    )
    
    create_user(
        username='admin',
        password='adminpass',
        email='admin@example.com',
        name='Admin User',
        user_type='staff',
        staff_id='A001',
        department='Career Services'
    )
