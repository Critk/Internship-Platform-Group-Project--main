from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for, make_response
from flask_login import login_user
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token
from App.models import User

from.index import index_views

from App.controllers import (
    login,
    get_all_users,  # Import the missing function
    create_user
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    
@auth_views.route('/users', methods=['GET', 'POST'])
def get_user_pages():
    users = get_all_users()
    return render_template('users.html', users=users)

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")








@auth_views.route('/login', methods=['GET', 'POST'])
def login_action():
    if request.method == 'POST':
        data = request.form
        token = login(data['username'], data['password'])

        if not token:
            flash('Bad username or password. Retry or Create an Account', 'error')
            return redirect(url_for('index_views.index_page'))

        from App.models import User
        user = User.query.filter_by(username=data['username']).first()

        if user:
            login_user(user)
            flash(f'Login Successful. Welcome {user.user_type.title()}!')

            # Render intermediate redirect template
            # Determine redirect URL based on user type
            if user.user_type == 'student':
                redirect_url = '/student-dashboard' # or your actual student dashboard route
            elif user.user_type == 'company':
                redirect_url = '/company-dashboard'  # or your actual company dashboard route
            elif user.user_type == 'staff':
                redirect_url = '/staff-dashboard'  # or your actual staff dashboard route
            else:
                redirect_url = redirect('/all_users')  # fallback

            response = make_response(render_template('login_redirect.html', redirect_url=redirect_url))
            set_access_cookies(response, token)
            return response

    return render_template('users.html')




@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(url_for('index_views.index_page'))  # whatever your landing route is called
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response