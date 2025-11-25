#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.admin.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports
from flask import flash, redirect, render_template, url_for
from flask_login import login_required
from backend.datamodule.models.role import Role
from frontend.webapp.admin import admin_bp
from frontend.webapp.forms import UserForm
from frontend.webapp.utils import admin_required
from backend.datamodule.models.user import User

# --- Admin dashboard
# User Management
@login_required
@admin_required
@admin_bp.get("/dashboard/admin/usermanagement")
def user_management():
    # get users from database
    users_tuple = User.get_all_users()
    users = [User.from_tuple(u) for u in users_tuple]
    print(users)
    # get form
    form = UserForm()
    return render_template("admin_usermanagement.html", users=users, form=form, selected_user=None)

@admin_bp.route("/dashboard/admin/usermanagement/new", methods=["GET", "POST"])
@admin_required
def user_new():
    form = UserForm()
    users_tuple = User.get_all_users()
    users = [User.from_tuple(u) for u in users_tuple]
    if form.validate_on_submit():
        # create user in DB
        # check for existing username/email
        user_in_db = User.get_by_username(form.username.data)
        if user_in_db:
            # handle existing user case
            flash('Username already exists.', 'error')
            return render_template("admin_usermanagement.html",
                                      users=users,
                                      form=form,
                                      selected_user=None)
        # create new user
        # get role id from role name
        role_id = Role.get_role_id_by_name(form.role_name.data)
        print(f'Role ID for role {form.role_name.data}: {role_id}')
        new_user = User(username=form.username.data,
                      email=form.email.data,
                      password=form.password.data,
                      role_id=role_id,
                      b_admin=form.role_name.data == 'admin')
        if new_user:
            print(f'Creating new user: {new_user.username}, role_id: {new_user.role_id}, is_admin: {new_user.b_admin}')
            new_user.insert()
            flash('User created successfully.', 'success')
        else:
            flash('Error creating user.', 'error')
            return render_template("admin_usermanagement.html",
                                      users=users,
                                      form=form,
                                      selected_user=None)
        return redirect(url_for("admin.user_edit", user_id=new_user.id))
    return render_template("admin_usermanagement.html",
                           users=users,
                           form=form,
                           selected_user=None)


@admin_bp.route("/dashboard/admin/usermanagement/users/<user_id>", methods=["GET", "POST"])
@admin_required
def user_edit(user_id):
    user = User.from_tuple(User.get_by_id(user_id))
    #convert b_admin flag to 'yes'/'no' for form
    user.b_admin = 'yes' if user.b_admin else 'no'
    all_users_tuple = User.get_all_users()
    all_users = []
    for u in all_users_tuple:
        # get role name for each user
        user_obj = User.from_tuple(u)
        # get role name
        user_obj.role_name = Role.get_by_role_id(user_obj.role_id).role_name if user_obj.role_id else None
        # get is_admin flag as 'yes'/'no'
        user_obj.b_admin = 'yes' if user_obj.b_admin else 'no'
        # append to list
        all_users.append(user_obj)

        
    form = UserForm(obj=user)
    if form.validate_on_submit():
        # update user in DB
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = form.password.data
        # get role id from role name
        role_id = Role.get_role_id_by_name(form.role_name.data)
        user.role_id = role_id
        user.b_admin = True if form.role_name.data == 'admin' else False
        values = (user.role_id, user.username, user.password, user.email, user.b_admin, user.salt, user.pepper, user.id)
        user_tuple = user.update(values=values)
        if not user_tuple:
            flash('Error updating user.', 'error')
            return render_template("admin_usermanagement.html",
                                      users=all_users,
                                      form=form,
                                      selected_user=user)
        flash('User updated successfully.', 'success')
        return redirect(url_for("admin.user_edit", user_id=user_id))
    return render_template("admin_usermanagement.html",
                           users=all_users,
                           form=form,
                           selected_user=user)

@admin_bp.post("/dashboard/admin/usermanagement/users/<user_id>/delete")
@admin_required
def user_delete(user_id):
    User.delete(user_id)
    return redirect(url_for("admin.user_new"))


# Requiremets Management
@login_required
@admin_required
@admin_bp.get("/dashboard/admin/requirementsmanagement")
def requirements_management():
    return render_template("admin_requirementsmanagement.html")

# System logs
@login_required
@admin_required
@admin_bp.get("/dashboard/admin/systemlogs")
def system_logs():
    return render_template("admin_systemlogs.html")

