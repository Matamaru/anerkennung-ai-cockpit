#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.auth.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports

from flask import flash, render_template, request, url_for, redirect
from flask_login import login_user, logout_user, login_required
from backend.datamodule.models import user
from frontend.webapp.auth import auth_bp
from backend.datamodule.models.user import User

# --- Login page
@auth_bp.get("/login")
def login():
    return render_template("login.html")

@auth_bp.post("/login")
def login_submit():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # lookup user
    user_tuple = User.get_by_username(username)
    # print(f'lookup user_tuple: {user_tuple}')
    if user_tuple is None:
        redirect_url = url_for('auth.login')
        print(f'User not found: {username}')
        flash('Invalid username or password.', 'error')
        return redirect(redirect_url)
    else:
        user = User.from_tuple(user_tuple)
        # check password
        if not user.check_password(password):
            print('Password check failed.')
            flash('Invalid username or password.', 'error')
            redirect_url = url_for('auth.login')
            return redirect(redirect_url)
        else:
            # success: log in user via Flask-Login
            login_user(user)
            print(f"User {user.username} logged in successfully.")
            flash('Logged in successfully.', 'success')
            redirect_url = url_for('main.dashboard')
            return redirect(redirect_url)

# Logout route
@auth_bp.get("/logout")
@login_required
def logout():
    logged_out = logout_user()
    print(f'User logged out: {logged_out}')
    return redirect(url_for("main.index")) 

@auth_bp.post("/logout")
@login_required
def logout_post():
    logged_out = logout_user()
    print(f'User logged out: {logged_out}')
    return redirect(url_for("main.index"))

# --- Registration page
@auth_bp.get("/register")
def register():
    return render_template("register.html")

@auth_bp.post("/register")
def register_submit():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    email = request.form.get("email", "")

    # check if user already exists
    existing_user = User.get_by_username(username)
    if existing_user is not None:
        print(f'User already exists: {username}')
        redirect_url = url_for('auth.register')
        return redirect(redirect_url)

    # create new user
    new_user = User(username=username, password=password, email=email)
    if new_user is None:
        print('User creation failed.')
        redirect_url = url_for('auth.register')
        return redirect(redirect_url)

    print(f'User {new_user.username} created successfully.')
    # log in the new user
    login_user(new_user)
    redirect_url = url_for('main.dashboard')
    return redirect(redirect_url)