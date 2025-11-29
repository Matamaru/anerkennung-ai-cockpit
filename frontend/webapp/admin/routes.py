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
from backend.datamodule.models.profession import Profession
from backend.datamodule.models.state import State
from backend.datamodule.models.requirements import Requirements
from backend.datamodule.models.document_type import DocumentType
from backend.datamodule.models.role import Role
from frontend.webapp.admin import admin_bp
from frontend.webapp.forms import DocumentTypeForm, RequirementForm, UserForm
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
    Optional filters: ?country=...&state=...&profession=...
    Optional selected requirement: ?req_id=123
    """
    # Get filters and selected requirement from form args
    filter_country = request.args.get("country") or ""
    filter_state = request.args.get("state") or ""
    filter_profession = request.args.get("profession") or ""  # New profession filter
    selected_req_id = request.args.get("req_id", type=str)

    # Load list for left side (requirements)
    req_tuple = Requirements.get_all()
    requirements = [Requirements.from_tuple(r) for r in req_tuple] if req_tuple else []
    #print(f"Total requirements loaded: {len(requirements)}")

    selected_req = Requirements.from_tuple(Requirements.get_by_id(selected_req_id)) if selected_req_id else None

    # --- selected_req -> form data (convert IDs to names just for the form) ---
    if selected_req and selected_req.country_id:
        country_tuple = Country.get_by_id(selected_req.country_id)
        selected_country_name = country_tuple[1] if country_tuple else ""
    else:
        selected_country_name = ""

    if selected_req and selected_req.state_id:
        state_tuple = State.get_by_id(selected_req.state_id)
        selected_state_name = state_tuple[2] if state_tuple else ""
    else:
        selected_state_name = ""

    if selected_req and selected_req.profession_id:
        profession_tuple = Profession.get_by_id(selected_req.profession_id)
        selected_profession_name = profession_tuple[1] if profession_tuple else ""
    else:
        selected_profession_name = ""

    # Create the form object for the selected requirement
    if selected_req:
        form = RequirementForm(
            profession_name=selected_profession_name,
            country_name=selected_country_name,
            state_name=selected_state_name,
            req_name=selected_req.name,
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
        if filter_profession:
            form.profession_name.data = filter_profession  # Set the profession filter if available

    # ========= Build country/state name caches from ALL requirements =========
    all_requirements = requirements  # keep original list
    print(f"Building name caches from {len(all_requirements)} total requirements")

    country_name_by_id: dict[str, str] = {}
    state_name_by_id: dict[str, str] = {}
    profession_name_by_id: dict[str, str] = {}

    country_ids = set()
    state_ids = set()
    profession_ids = set()

    for req in all_requirements:
        if req.country_id:
            country_ids.add(req.country_id)
        if req.state_id:
            state_ids.add(req.state_id)
        if req.profession_id:
            profession_ids.add(req.profession_id)

    # Resolve countries
    for cid in country_ids:
        ct = Country.get_by_id(cid)
        country_name_by_id[cid] = ct[1] if ct else ""

    # Resolve states
    for sid in state_ids:
        st = State.get_by_id(sid)
        state_name_by_id[sid] = st[2] if st else ""

    # Resolve professions
    for pid in profession_ids:
        pt = Profession.get_by_id(pid)
        profession_name_by_id[pid] = pt[1] if pt else ""

    # List of country names for dropdown
    countries = sorted(set(country_name_by_id.values()))

    # Map: country_name -> set of state_names (no duplicates)
    states_for_country: dict[str, set[str]] = {}
    for req in all_requirements:
        cid = req.country_id
        sid = req.state_id
        c_name = country_name_by_id.get(cid)
        s_name = state_name_by_id.get(sid)
        if not c_name or not s_name:
            continue
        states_for_country.setdefault(c_name, set()).add(s_name)

    # Convert sets to sorted lists
    states_for_country = {
        c: sorted(list(s_set)) for c, s_set in states_for_country.items()
    }

    # Map all countries and states to professions (for filtering purposes)
    professions_for_country_state: dict[tuple[str, str], set[str]] = {}
    for req in all_requirements:
        cid = req.country_id
        sid = req.state_id
        pid = req.profession_id
        c_name = country_name_by_id.get(cid)
        s_name = state_name_by_id.get(sid)
        p_name = profession_name_by_id.get(pid)
        if not c_name or not s_name or not p_name:
            continue
        professions_for_country_state.setdefault((c_name, s_name), set()).add(p_name)
    print(f"Professions for country/state mapping: {professions_for_country_state}")

    # Fallback: ALL states (used if something with mapping goes wrong)
    all_states = sorted(set(state_name_by_id.values()))

    # Annotate each requirement with country_name/state_name/profession_name for template
    for req in all_requirements:
        req.country_name = country_name_by_id.get(req.country_id, "")
        req.state_name = state_name_by_id.get(req.state_id, "")
        req.profession_name = profession_name_by_id.get(req.profession_id, "")

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

    if filter_profession:
        filtered_requirements = [
            r for r in filtered_requirements
            if r.profession_name == filter_profession
        ]

    requirements = filtered_requirements

    # Fetch all professions for the dropdown
    professions = sorted(list(profession_name_by_id.values()))

    return render_template(
        "admin_requirementsmanagement.html",
        requirements=requirements,
        selected_req=selected_req,
        form=form,
        filter_country=filter_country,
        filter_state=filter_state,
        filter_profession=filter_profession,  # Pass the selected profession filter
        countries=countries,
        states_for_country=states_for_country,
        all_states=all_states,
        professions=professions,  # List of professions for the dropdown
    )



@admin_bp.route("/dashboard/admin/requirements/save", methods=["POST"])
@login_required
@admin_required
def requirements_save():
    form = RequirementForm()
    req_id = request.form.get("req_id", type=str)

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

    values = (
        Country.from_tuple(Country.get_by_name(form.country_name.data)).id if Country.get_by_name(form.country_name.data) else None,
        State.from_tuple(State.get_by_name(form.state_name.data)).id if form.state_name.data and State.get_by_name(form.state_name.data) else None,
        form.req_name.data.strip(),
        (form.description.data or "").strip() or None,
        _str_to_bool(form.optional.data),
        _str_to_bool(form.translation_required.data),
        _str_to_bool(form.fullfilled.data),
        req_id
    )

    req_tuple = Requirements.get_by_id(req_id) if req_id else None
    if req_tuple:
        re = Requirements.from_tuple(req_tuple)
        updated_req_tuple = re.update(values=values)
        flash("Requirement updated.", "success")
        new_id = req_id
    else:
        # chek if cpountru exists, if not create it
        refreshed_list_of_countries = Country.get_all()
        country_names = [Country.from_tuple(c).name for c in refreshed_list_of_countries]
        if form.country_name.data not in country_names:
            # New country added
            new_country = Country(
                id=None,
                name=form.country_name.data,
                description=None
            )
            new_country.insert()

        # check for state existence if state name provided
        if form.state_name.data:
            refreshed_list_of_states = State.get_all()
            state_names = [State.from_tuple(s).name for s in refreshed_list_of_states]
            if form.state_name.data not in state_names:
                # New state added
                country_tuple = Country.get_by_name(form.country_name.data)
                country_id = Country.from_tuple(country_tuple).id if country_tuple else None
                new_state = State(
                    id=None,
                    country_id=country_id,
                    name=form.state_name.data,
                    abbreviation=None,
                    description=None
                )
                new_state.insert()
        # create new requirement with country/state IDs
        new_req = Requirements(
            id=None,
            country_id=Country.from_tuple(Country.get_by_name(form.country_name.data)).id if Country.get_by_name(form.country_name.data) else None,
            state_id=State.from_tuple(State.get_by_name(form.state_name.data)).id if form.state_name.data and State.get_by_name(form.state_name.data) else None,
            name=form.req_name.data.strip(),
            description=(form.description.data or "").strip() or None,
            optional=_str_to_bool(form.optional.data),
            translation_required=_str_to_bool(form.translation_required.data),
            fullfilled=_str_to_bool(form.fullfilled.data)
        )
        new_req_tuple = new_req.insert()
        if not new_req_tuple:
            flash("Error creating new requirement.", "danger")
            args = {}
            if req_id:
                args["req_id"] = req_id
            if form.country_name.data:
                args["country"] = form.country_name.data
            if form.state_name.data:
                args["state"] = form.state_name.data
            return redirect(url_for("admin.requirements_management", **args))
        else:
            new_req.id = new_req_tuple[0]  # assuming ID is the first element
            flash("Requirement created.", "success")

        # refresh state_for_country mapping in case new country and / or state was added

    return redirect(
        url_for(
            "admin.requirements_management",
            req_id=new_id if req_tuple else new_req.id,
            country=form.country_name.data or "",
            state=form.state_name.data   or "",
            
        )
    )

@admin_bp.route("/dashboard/admin/countries", methods=["GET", "POST"])
@login_required
@admin_required
def countries_management():
    countries_tuple = Country.get_all()
    countries = [Country.from_tuple(c) for c in countries_tuple] if countries_tuple else []
    return render_template("admin_country.html", countries=countries)

@admin_bp.route("/dashboard/admin/states", methods=["GET", "POST"])
@login_required
@admin_required
def states_management():
    states_tuple = State.get_all()
    states = [State.from_tuple(s) for s in states_tuple] if states_tuple else []
    return render_template("admin_state.html", states=states)


@admin_bp.route("/dashboard/admin/requirements/<req_id>/delete", methods=["POST"])
@login_required
@admin_required
def requirement_delete(req_id: str):
    del_req_tuple = Requirements.get_by_id(req_id)
    if not del_req_tuple:
        flash("Requirement not found – nothing deleted.", "warning")
        return redirect(url_for("admin.requirements_management"))
    else:
        Requirements.from_tuple(del_req_tuple).delete()
        flash("Requirement deleted.", "success")
    return redirect(url_for("admin.requirements_management"))


@admin_bp.route("/dashboard/admin/requirements/<req_id>/copy", methods=["POST"])
@login_required
@admin_required
def requirement_copy(req_id: str):
    new_id = Requirements.copy(req_id)
    if not new_id:
        flash("Requirement not found – nothing copied.", "warning")
        return redirect(url_for("admin.requirements_management"))

    flash("Requirement copied.", "success")
    return redirect(url_for("admin.requirements_management", req_id=new_id))

#============ Document Types Management =========
@admin_bp.route("/dashboard/admin/document_types", methods=["GET"])
@login_required
@admin_required
def document_types_management():
    """
    List all document types (left) and show detail form (right).
    Optional selected document type: ?doc_id=UUID
    """
    selected_doc_id = request.args.get("doc_id")  # UUID string

    # Load all document types for left side
    dt_rows = DocumentType.get_all()  # you implement this to return tuples
    document_types = [DocumentType.from_tuple(r) for r in dt_rows] if dt_rows else []

    selected_doc = DocumentType.from_tuple(DocumentType.get_by_id(selected_doc_id)) if selected_doc_id else None

    if selected_doc:
        form = DocumentTypeForm(
            name=selected_doc.name,
            description=selected_doc.description,
        )
    else:
        form = DocumentTypeForm()

    return render_template(
        "admin_documenttypes.html",
        document_types=document_types,
        selected_doc=selected_doc,
        form=form,
    )


@admin_bp.route("/dashboard/admin/document_types/save", methods=["POST"])
@login_required
@admin_required
def document_types_save():
    form = DocumentTypeForm()
    doc_id = request.form.get("doc_id")  # UUID string or None

    if not form.validate_on_submit():
        flash("Please correct the errors in the form.", "danger")
        args = {}
        if doc_id:
            args["doc_id"] = doc_id
        return redirect(url_for("admin.document_types_management", **args))

     
    if doc_id:
        # update existing document type
        values = (
            form.name.data.strip(),
            (form.description.data or "").strip() or None,
            doc_id
        )

        doc_tuple = DocumentType.get_by_id(doc_id)  
        doc = DocumentType.from_tuple(doc_tuple)
        doc.update(values=values)
        flash("Document type updated.", "success")
        new_id = doc_id
    else:
        new_doc_tuple = DocumentType(
            id=None,
            name=form.name.data.strip(),
            description=(form.description.data or "").strip() or None,
        ).insert()
        if not new_doc_tuple:
            flash("Error creating new document type.", "danger")
            return redirect(url_for("admin.document_types_management"))
        new_id = new_doc_tuple[0]  
        flash("Document type created.", "success")

    return redirect(
        url_for(
            "admin.document_types_management",
            doc_id=new_id,
        )
    )


@admin_bp.route("/dashboard/admin/document_types/<doc_id>/delete", methods=["POST"])
@login_required
@admin_required
def document_type_delete(doc_id: str):
    doc_type_tuple = DocumentType.get_by_id(doc_id)
    if not doc_type_tuple:
        flash("Document type not found – nothing deleted.", "warning")
        return redirect(url_for("admin.document_types_management"))
    else:   
        DocumentType.from_tuple(doc_type_tuple).delete()
        flash("Document type deleted.", "success")
    return redirect(url_for("admin.document_types_management"))


#========= System Administration Routes =========
# System logs
@login_required
@admin_required
@admin_bp.get("/dashboard/admin/systemlogs")
def system_logs():
    return render_template("admin_systemlogs.html")

