#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.admin.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports
from flask import flash, redirect, render_template, url_for, request
from flask_login import login_required
from backend.datamodule.models.country import Country
from backend.datamodule.models.state import State
from backend.datamodule.models.requirements import Requirements
from backend.datamodule.models.role import Role
from frontend.webapp.admin import admin_bp
from frontend.webapp.forms import RequirementForm, UserForm
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
        # create user instances from tuples
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
    user = User.from_tuple(User.get_by_id(user_id))
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for("admin.user_management"))
    user.delete()
    flash('User deleted successfully.', 'success')
    return redirect(url_for("admin.user_management"))


# Requiremets Management
def _str_to_bool(value: str) -> bool:
    return value.lower() == "true"


@admin_bp.route("/dashboard/admin/requirements", methods=["GET"])
@login_required
@admin_required
def requirements_management():
    """
    Show list of requirements (left) and detail form (right).
    Optional filters: ?country=...&state=...
    Optional selected requirement: ?req_id=123
    """
    # get filters and selected requirement from form args
    filter_country = request.args.get("country") or ""
    filter_state = request.args.get("state") or ""
    selected_req_id = request.args.get("req_id", type=str)

    # Load list for left side
    req_tuple = Requirements.get_all()
    requirements = [Requirements.from_tuple(r) for r in req_tuple] if req_tuple else []

    selected_req = Requirements.get_by_id(selected_req_id) if selected_req_id else None
#    print(f"Selected requirement ID: {selected_req_id}, found: {selected_req is not None}")

    # --- selected_req -> form data (convert IDs to names just for the form) ---
    if selected_req and selected_req.country_id:
        country_tuple = Country.get_by_id(selected_req.country_id)
        if country_tuple:
            country = Country.from_tuple(country_tuple)
            selected_country_name = country.name
        else:
            selected_country_name = ""
    else:
        selected_country_name = ""

    if selected_req and selected_req.state_id:
        state_tuple = State.get_by_id(selected_req.state_id)
        if state_tuple:
            state = State.from_tuple(state_tuple)
            selected_state_name = state.name
        else:
            selected_state_name = ""
    else:
        selected_state_name = ""

    if selected_req:
        form = RequirementForm(
            country_name=selected_country_name,
            state_name=selected_state_name,
            req_name=selected_req.name,  # or selected_req.req_name, depending on your model
            description=selected_req.description,
            optional="true" if selected_req.optional else "false",
            translation_required="true" if selected_req.translation_required else "false",
            fullfilled="true" if selected_req.fullfilled else "false",
        )
    else:
        form = RequirementForm()
        if filter_country:
            form.country_name.data = filter_country
        if filter_state:
            form.state_name.data = filter_state

    # ========= Build country/state name caches from ALL requirements =========
    all_requirements = requirements  # keep original list

    country_name_by_id: dict[str, str] = {}
    state_name_by_id: dict[str, str] = {}

    country_ids = set()
    state_ids = set()
    for req in all_requirements:
        if req.country_id:
            country_ids.add(req.country_id)
        if req.state_id:
            state_ids.add(req.state_id)

    # resolve countries
    for cid in country_ids:
        ct = Country.get_by_id(cid)
        if not ct:
            continue
        c = Country.from_tuple(ct)
        country_name_by_id[cid] = c.name

    # resolve states
    for sid in state_ids:
        st = State.get_by_id(sid)
        if not st:
            continue
        s = State.from_tuple(st)
        state_name_by_id[sid] = s.name

    # list of country names for dropdown
    countries = sorted(set(country_name_by_id.values()))

    # map: country_name -> set of state_names (no duplicates)
    states_for_country: dict[str, set[str]] = {}
    for req in all_requirements:
        cid = req.country_id
        sid = req.state_id
        c_name = country_name_by_id.get(cid)
        s_name = state_name_by_id.get(sid)
        if not c_name or not s_name:
            continue
        states_for_country.setdefault(c_name, set()).add(s_name)

    # convert sets to sorted lists
    states_for_country = {
        c: sorted(list(s_set)) for c, s_set in states_for_country.items()
    }

    # fallback: ALL states (used if something with mapping goes wrong)
    all_states = sorted(set(state_name_by_id.values()))

    # annotate each requirement with country_name/state_name for template
    for req in all_requirements:
        req.country_name = country_name_by_id.get(req.country_id, "")
        req.state_name = state_name_by_id.get(req.state_id, "")

    # ========= Apply filters by *names* =========
    filtered_requirements = all_requirements

    if filter_country:
        filtered_requirements = [
            r for r in filtered_requirements
            if r.country_name == filter_country
        ]

    if filter_state:
        filtered_requirements = [
            r for r in filtered_requirements
            if r.state_name == filter_state
        ]

    requirements = filtered_requirements

    return render_template(
        "admin_requirementsmanagement.html",
        requirements=requirements,
        selected_req=selected_req,
        form=form,
        filter_country=filter_country,
        filter_state=filter_state,
        countries=countries,
        states_for_country=states_for_country,
        all_states=all_states,
    )


@admin_bp.route("/requirements/save", methods=["POST"])
@login_required
@admin_required
def requirements_save():
    form = RequirementForm()
    req_id = request.form.get("req_id", type=int)

    if not form.validate_on_submit():
        flash("Please correct the errors in the form.", "danger")
        # re-display management page with current selection
        args = {}
        if req_id:
            args["req_id"] = req_id
        if form.country_name.data:
            args["country"] = form.country_name.data
        if form.state_name.data:
            args["state"] = form.state_name.data
        return redirect(url_for("admin.requirements_management", **args))

    data = {
        "country_name": form.country_name.data.strip(),
        "state_name": (form.state_name.data or "").strip() or None,
        "req_name": form.req_name.data.strip(),
        "description": (form.description.data or "").strip() or None,
        "optional": _str_to_bool(form.optional.data),
        "translation_required": _str_to_bool(form.translation_required.data),
        "fullfilled": _str_to_bool(form.fullfilled.data),
    }

    if req_id:
        Requirements.update(req_id, data)
        flash("Requirement updated.", "success")
        new_id = req_id
    else:
        new_id = Requirements.create(data)
        flash("Requirement created.", "success")

    return redirect(
        url_for(
            "admin.requirements_management",
            req_id=new_id,
            country=data["country_name"],
            state=data["state_name"] or "",
        )
    )


@admin_bp.route("/requirements/<req_id>/delete", methods=["POST"])
@login_required
@admin_required
def requirement_delete(req_id: str):
    Requirements.delete(req_id)
    flash("Requirement deleted.", "success")
    return redirect(url_for("admin.requirements_management"))


@admin_bp.route("/requirements/<req_id>/copy", methods=["POST"])
@login_required
@admin_required
def requirement_copy(req_id: str):
    new_id = Requirements.copy(req_id)
    if not new_id:
        flash("Requirement not found – nothing copied.", "warning")
        return redirect(url_for("admin.requirements_management"))

    flash("Requirement copied.", "success")
    return redirect(url_for("admin.requirements_management", req_id=new_id))

#========= System Administration Routes =========
# System logs
@login_required
@admin_required
@admin_bp.get("/dashboard/admin/systemlogs")
def system_logs():
    return render_template("admin_systemlogs.html")

