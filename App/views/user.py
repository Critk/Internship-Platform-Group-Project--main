from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, current_user

from.index import index_views

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    get_student_applications,
    get_available_positions,
    apply_to_position,
    get_profile_completeness,
    get_company_positions,
    create_internship_position,
    update_application_status,
    get_all_applications,
    update_student_profile


)

#userViews------------------------userViews-------------------------userViews--------------------------------------userViews
user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)



@user_views.route('/users', methods=['POST'])
def create_user_action():
    try:
        # Get all form data with proper defaults
        data = {
            'username': request.form.get('username'),
            'password': request.form.get('password'),
            'email': request.form.get('email'),
            'name': request.form.get('name'),
            'user_type': request.form.get('user_type', 'student')  # Default to student
        }
        
        # Validate required fields
        if not all(data.values()):  # Check if any field is empty
            raise ValueError("All fields are required")
            
        # Create the user
        user = create_user(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            name=data['name'],
            user_type=data['user_type']
        )
        
        if not user:
            flash('User creation failed', 'error')
            return redirect(url_for('user_views.get_user_page'))
        
        # Success messages
        if data['user_type'] == 'student':
            flash(f"Student {data['username']} created!", 'success')
        elif data['user_type'] == 'company':
            flash(f"Company {data['username']} created!", 'success')
        elif data['user_type'] == 'staff':
            flash(f"Staff {data['username']} created!", 'success')
        else:
            flash(f"User {data['username']} created!", 'success')
            
    except Exception as e:
        flash(f'Error creating user: {str(e)}', 'error')
    
    return redirect(url_for('user_views.get_user_page'))


@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)



@user_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    user = create_user(data['username'], data['password'])
    return jsonify({'message': f"user {user.username} created with id {user.id}"})




@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')





#studentViews------------------------studentViews-------------------------studentViews--------------------------------------studentViews
student_views = Blueprint('student_views', __name__, template_folder='../templates')

@student_views.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('auth_views.login_page'))
    
    applications = get_student_applications(current_user.id)
    completeness = get_profile_completeness(current_user.id)
    return render_template('student/dashboard.html', applications=applications, completeness=completeness)


@student_views.route('/positions')
@login_required
def view_positions():
    positions = get_available_positions(current_user.id)
    return render_template('student/positions.html', positions=positions)



@student_views.route('/apply/<int:position_id>', methods=['POST'])
@login_required
def apply_position(position_id):
    cover_letter = request.form.get('cover_letter')
    if apply_to_position(current_user.id, position_id, cover_letter):
        flash('Application submitted!', 'success')
    else:
        flash('Application failed', 'error')
    return redirect(url_for('student_views.dashboard'))

@student_views.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        if update_student_profile(
            current_user.id,
            university=request.form.get('university'),
            major=request.form.get('major'),
            graduation_year=request.form.get('graduation_year'),
            skills=request.form.get('skills')
        ):
            flash('Profile updated!', 'success')
        else:
            flash('Update failed', 'error')
        return redirect(url_for('student_views.dashboard'))
    
    return render_template('student/edit_profile.html')




#companyViews------------------------companyViews-------------------------companyViews--------------------------------------companyViews
company_views = Blueprint('company_views', __name__, template_folder='../templates')

@company_views.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'company':
        flash('Access denied', 'error')
        return redirect(url_for('auth_views.login_page'))
    
    positions = get_company_positions(current_user.id)
    return render_template('company/dashboard.html', positions=positions)


@company_views.route('/positions/new', methods=['GET', 'POST'])
@login_required
def new_position():
    if request.method == 'POST':
        position_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'requirements': request.form.get('requirements'),
            'location': request.form.get('location'),
            'salary': request.form.get('salary'),
            'duration': request.form.get('duration'),
            'deadline': request.form.get('deadline'),
            'skills_required': request.form.get('skills_required')
        }
        if create_internship_position(current_user.id, **position_data):
            flash('Position created!', 'success')
            return redirect(url_for('company_views.dashboard'))
        flash('Failed to create position', 'error')
    return render_template('company/new_position.html')

@company_views.route('/position/<int:position_id>/shortlist/<int:application_id>')
@login_required
def shortlist_application(position_id, application_id):
    if update_application_status(application_id, 'shortlisted'):
        flash('Application shortlisted', 'success')
    else:
        flash('Operation failed', 'error')
    return redirect(url_for('company_views.view_position', position_id=position_id))




#staffViews------------------------staffViews-------------------------staffViews--------------------------------------staffViews
staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

@staff_views.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'staff':
        flash('Access denied', 'error')
        return redirect(url_for('auth_views.login_page'))
    
    applications = get_all_applications()
    return render_template('staff/dashboard.html', applications=applications)

@staff_views.route('/application/<int:application_id>/shortlist')
@login_required
def shortlist_app(application_id):
    if shortlist_application(application_id):
        flash('Application shortlisted', 'success')
    else:
        flash('Operation failed', 'error')
    return redirect(url_for('staff_views.dashboard'))






#notificationViews------------------------notificationViews-------------------------notificationViews--------------------------------------notificationViews











#searchViews------------------------searchViews-------------------------searchViews--------------------------------------searchViews