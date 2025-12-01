#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.candidate.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.3
#****************************************************************************

#=== Imports
import os
import pathlib
from uuid import uuid4
from flask import json, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.datamodule.models.document_data_sql import INSERT_DOCUMENT_DATA
from backend.datamodule.models.status_sql import SELECT_BY_NAME
from backend.datamodule.models.document import Document
from backend.datamodule.models.document_data import DocumentData
from backend.datamodule.models.document_type import DocumentType
from backend.datamodule.models.document_type_sql import SELECT_DOCUMENT_TYPE_BY_NAME
from backend.datamodule.models.file import File
from backend.datamodule.models.file_type import FileType
from backend.datamodule.models.status import Status
from frontend.webapp.candidate import candidate_bp
from frontend.webapp.utils import candidate_required
from backend.datamodule.models.profession import Profession
from backend.datamodule.models.country import Country
from backend.datamodule.models.state import State 
from backend.datamodule.models.application import Application
from backend.datamodule import db
from backend.services.ocr import analyze_bytes


#=== helpers

def _load_select_data():
    professions_tuple = Profession.get_all()
    professions = [Profession.from_tuple(p) for p in professions_tuple] if professions_tuple else []
    countries_tuple = Country.get_all()
    countries = [Country.from_tuple(c) for c in countries_tuple] if countries_tuple else []
    states_tuple = State.get_all()
    states = [State.from_tuple(s) for s in states_tuple] if states_tuple else []
    return professions, countries, states

def _attach_display_data(applications, professions, countries, states):
    """
    Attach profession_name, country_name, state_name to each Application object.
    """

    prof_map = {p.id: p.name for p in professions}
    country_map = {c.id: c.name for c in countries}
    state_map = {s.id: s.name for s in states}

    for a in applications:
        # IDs -> names
        a.profession_name = prof_map.get(a.profession_id)
        a.country_name = country_map.get(a.country_id)
        a.state_name = state_map.get(a.state_id)

    return applications

def get_documents_for_application(application_id) -> list[Document]:
    """Fetch all documents linked to a given application ID."""
    query = """
    SELECT 
        ad.id AS app_doc_id,
        ad.application_id,
        d.id AS document_id,
        d.file_id,
        dt.name AS document_type_name,
        f.filename,
        f.filepath,
        doc_data.ocr_full_text,
        d.status_id,
        ad.requirements_id
    FROM _app_docs ad
    JOIN _documents d ON ad.document_id = d.id
    JOIN _document_types dt ON d.document_type_id = dt.id
    JOIN _files f ON d.file_id = f.id
    JOIN _document_datas doc_data ON d.document_data_id = doc_data.id
    WHERE ad.application_id = %s
    """
    try:
        db.connect()
        db.cursor.execute(query, (application_id,))
        doc_tuples = db.cursor.fetchall()
        if doc_tuples:
            print(f"Fetched {len(doc_tuples)} documents for application {application_id}")
            return [Document.from_tuple(dt) for dt in doc_tuples]
        else:
            print(f"No documents found for application {application_id}")
            return []
    except Exception as e:
        print(f"Error fetching documents for application {application_id}: {e}")
        return []
    finally:
        db.close_conn()


def get_requirements_for_application(application_id) -> list[dict]:
    """Fetch all requirements linked to a given application ID."""
    query = """
    SELECT r.id, r.name, r.description
    FROM _requirements r
    JOIN _app_docs ad ON r.id = ad.requirements_id
    WHERE ad.application_id = %s
    """
    try:
        db.connect()
        db.cursor.execute(query, (application_id,))
        req_tuples = db.cursor.fetchall()
        #print(f"Requirement tuples in candidate.get_requirements_for_application: {req_tuples}")
        requirements = []
        for rt in req_tuples:
            requirements.append({
                'id': rt[0],
                'name': rt[1],
                'description': rt[2]
            })
        #print(f"Fetched {len(requirements)} requirements for application {application_id}")
        return requirements
    except Exception as e:
        print(f"Error fetching requirements for application {application_id}: {e}")
        return []
    finally:
        db.close_conn()


def get_document_details(document_id) -> Document:
    """Fetch detailed information for a specific document by its ID."""
    query = """
    SELECT 
        d.id AS document_id,
        d.file_id,
        dt.name AS document_type_name,
        f.filename,
        f.filepath,
        doc_data.ocr_full_text,
        d.last_modified,
        d.status_id
    FROM _documents d
    JOIN _document_types dt ON d.document_type_id = dt.id
    JOIN _files f ON d.file_id = f.id
    JOIN _document_datas doc_data ON d.document_data_id = doc_data.id
    WHERE d.id = %s
    """
    try:
        db.connect()
        db.cursor.execute(query, (document_id,))
        doc_tuple = db.cursor.fetchone()
        if doc_tuple:
            print(f"Fetched details for document {document_id}")
            return Document.from_tuple(doc_tuple)
        else:
            print(f"No details found for document {document_id}")
            return None
    except Exception as e:
        print(f"Error fetching details for document {document_id}: {e}")
        return None
    finally:
        db.close_conn()

#=== Routes

#======= Document Management Routes  =======

@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/documentmanagement", methods=["GET", "POST"])
def document_management():
    if request.method == "POST":
        # Handle document upload
        requirement_id = request.form.get("requirement_id")
        application_id = request.form.get("application_id")
        file = request.files.get("document")
        #print(f"Received upload for requirement_id={requirement_id}, application_id={application_id}, file={file.filename if file else 'No File'}")

        if not requirement_id or not application_id or not file:
            flash("Missing requirement, application, or file for upload.", "danger")
            return redirect(url_for('candidate.document_management', application_id=application_id))

        # check file type and if allowed get file_type_id
        file_ext = os.path.splitext(file.filename)[1][1:].upper()  # get extension without dot and uppercase
        ft_tuple = FileType.get_by_name(file_ext)
        if not ft_tuple:
            flash(f"File type {file_ext} is not allowed.", "danger")
            return redirect(url_for('candidate.document_management', application_id=application_id))
        else:
            file_type_id = FileType.from_tuple(ft_tuple).id
        
        # save file to storage and create File record
        # get file name and path
        filename = file.filename

        # create dir if not exists with user id in backend/uploads/<user_id>/
        user_dir = os.path.join("backend", "uploads", str(current_user.id))
        os.makedirs(user_dir, exist_ok=True)
        
        # storage path
        storage_path = os.path.join(user_dir, str(current_user.id) + "_" + filename)

        # check if document already exists in db and storage
        if os.path.exists(storage_path):
            # check in db
            try:
                db.connect()
                db.cursor.execute("SELECT * FROM _files WHERE filename = %s", (filename,))
                existing_file_tuple = db.cursor.fetchone()
            except Exception as e:
                print(f"Error checking existing file in DB: {e}")
                existing_file_tuple = None
            finally:
                db.close_conn()
            if existing_file_tuple:
                flash("A document with the same name already exists.", "danger")
                return redirect(url_for('candidate.document_management', application_id=application_id))
            else:
                # file exists in storage but not in db, proceed to save new file record
                nf_tuple = File(filename=filename, filepath=storage_path, filetype_id=file_type_id).insert()
                if not nf_tuple:
                    flash("Error saving document record for existing file.", "danger")
                    return redirect(url_for('candidate.document_management', application_id=application_id))
                else:
                    file_id = nf_tuple[0]
        else:
            #check if file with same name exists in db
            try:
                db.connect()
                db.cursor.execute("SELECT * FROM _files WHERE filename = %s", (filename,))
                existing_file_tuple = db.cursor.fetchone()
            except Exception as e:
                print(f"Error checking existing file in DB: {e}")
                existing_file_tuple = None
            finally:
                db.close_conn()
            if existing_file_tuple:
                file.save(storage_path)  # save file to storage
                file_id = File.from_tuple(existing_file_tuple).id
                if not file_id:
                    flash("Error saving document record.", "danger")
                    return redirect(url_for('candidate.document_management', application_id=application_id))
            else:
                file.save(storage_path)  # save file to storage
                file_id = File(
                    filename=filename,
                    filepath=storage_path,
                    filetype_id=file_type_id
                ).insert()[0]
                if not file_id:
                    flash("Error saving document record.", "danger")
                    return redirect(url_for('candidate.document_management', application_id=application_id))

        # Document data creation
        # use ocr module to extract text from the uploaded file
        #p = pathlib.Path(image_path)
        #b = p.read_bytes()
        #res = analyze_bytes(b) -> OrcResult object
        p = pathlib.Path(storage_path)
        b = p.read_bytes()
        res = analyze_bytes(b)
        doc_type_prediction = res.doc_type
        #print(f'Type Document Prediction: {type(doc_type_prediction)}, Value: {doc_type_prediction}')
        predictions = res.predictions
        ocr_full_text = res.ocr_text
        fields = res.fields

        # turn predictions into a single string, separated by new lines
        doc_type_prediction_str = "\n".join(doc_type_prediction) if isinstance(doc_type_prediction, list) else str(doc_type_prediction)
        predictions_str = "\n".join(predictions)

        doc_data = DocumentData( 
            ocr_doc_type_prediction=doc_type_prediction_str,
            ocr_predictions_str=predictions_str,
            ocr_full_text=ocr_full_text,
            ocr_extracted_data=fields
        )
        #print(f"Creating DocumentData with predicted type: {doc_data}")

        #print(f"DocumentData to be inserted: {doc_data.__dict__}")
        try:
            db.connect()
            db.cursor.execute(
                INSERT_DOCUMENT_DATA,
                (
                    doc_data.id,
                    doc_data.ocr_doc_type_prediction_str,
                    doc_data.ocr_predictions_str,
                    doc_data.ocr_full_text,
                    json.dumps(doc_data.ocr_extracted_data) if doc_data.ocr_extracted_data else None,
                    doc_data.layoutlm_full_text,
                    json.dumps(doc_data.layout_lm_data) if doc_data.layout_lm_data else None
                )
            )
            doc_data_tuple = db.cursor.fetchone()   
            if not doc_data_tuple:
                flash("Error saving document data record.", "danger")
                return redirect(url_for('candidate.document_management', application_id=application_id))
            else:
                document_data_id = doc_data_tuple[0]
        except Exception as e:
            print(f"Error inserting DocumentData: {e}")
            doc_data_tuple = None
        finally:
            db.close_conn()

        # status is "Uploaded" by default
        try:
            db.connect()
            db.cursor.execute(SELECT_BY_NAME, ("Uploaded",))
            status_tuple = db.cursor.fetchone()
            status = Status.from_tuple(status_tuple[0]) if status_tuple else None
            status_id = status.id if status else None
        except Exception as e:
            print(f"Error fetching status 'Uploaded': {e}")
            status_id = None
        finally:
            db.close_conn()

        # get document type id by predicted name
        try:
            db.connect()
            db.cursor.execute(SELECT_DOCUMENT_TYPE_BY_NAME, (doc_type_prediction,))
            doc_type_tuple = db.cursor.fetchone()
            if not doc_type_tuple:
                flash(f"Predicted document type '{doc_type_prediction}' is not recognized.", "danger")
                document_type_id = None
                return redirect(url_for('candidate.document_management', application_id=application_id))
            else:
                document_type = DocumentType.from_tuple(doc_type_tuple[0])
                document_type_id = document_type.id
        except Exception as e:
            print(f"Error fetching document type '{doc_type_prediction}': {e}")
            document_type_id = None
        finally:
            db.close_conn()

        # create Document record
        document = Document(
            file_id=file_id,
            document_type_id=document_type_id,
            document_data_id=document_data_id,
            status_id=status_id
        )
        try:
            db.connect()
            db.cursor.execute(
                """
                INSERT INTO _documents (id, file_id, document_type_id, document_data_id, status_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    document.id,
                    document.file_id,
                    document.document_type_id,
                    document.document_data_id,
                    document.status_id
                )
            )
            document_tuple = db.cursor.fetchone()
            if not document_tuple:
                flash("Error saving document record.", "danger")
                return redirect(url_for('candidate.document_management', application_id=application_id))
            document_id = document_tuple[0]
        except Exception as e:
            print(f"Error inserting Document: {e}")
            document_id = None
        finally:
            db.close_conn()

        # link Document to Application and Requirement in _app_docs
        
        
        # load documents to display in document management view
        documents = get_documents_for_application(application_id)   



        flash("Document uploaded successfully.", "success")
        return redirect(url_for('candidate.document_management', application_id=application_id, documents=documents))
    
    # Get the application_id from the URL or session
    application_id = request.args.get('application_id')

    if not application_id:
        return redirect(url_for('candidate.applications_management'))  # If no application selected, redirect to applications page

    # Get requirements associated with the selected application
    requirements = get_requirements_for_application(application_id)

    # Get documents associated with the selected application
    documents = get_documents_for_application(application_id)

    return render_template(
        "candidate_documentmanagement.html",
        requirements=requirements,
        documents=documents,
        application_id=application_id  # Pass the application_id to the template
    )


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/documentmanagement/details/<document_id>")
def document_details(document_id):
    # Get the details of the selected document
    document = get_document_details(document_id)
    return render_template("candidate_documentdetails.html", document=document)



#======= Application Management Routes  =======

@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/applicationmanagement")
def applications_management():
    """
    List view + right side empty (info alert).
    """
    user_id = current_user.id

    app_tuple = Application.get_by_user_id(user_id)
    applications = [Application.from_tuple(a) for a in app_tuple] if app_tuple else []

    professions, countries, states = _load_select_data()

    applications = _attach_display_data(applications, professions, countries, states)

    return render_template(
        "candidate_applicationsmanagement.html",
        applications=applications,
        application=None,
        professions=professions,
        countries=countries,
        states=states,
        is_new=False,
    )


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/applicationmanagement/new")
def applicationsmanagement_new():
    """
    Same page, but right side shows an empty 'New application' form.
    """
    user_id = current_user.id

    app_tuple = Application.get_by_user_id(user_id)
    applications = [Application.from_tuple(a) for a in app_tuple] if app_tuple else []

    professions, countries, states = _load_select_data()

    applications = _attach_display_data(applications, professions, countries, states)

    return render_template(
        "candidate_applicationsmanagement.html",
        applications=applications,
        application=None,
        professions=professions,
        countries=countries,
        states=states,
        is_new=True,
    )


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/applicationmanagement/<app_id>")
def applicationsmanagement_detail(app_id):
    """
    Same page, but right side shows details for one existing application.
    """
    user_id = current_user.id

    # list for left side
    app_tuple = Application.get_by_user_id(user_id)
    applications = [Application.from_tuple(a) for a in app_tuple] if app_tuple else []

    # single application for right side
    row = Application.get_by_id(app_id)
    application = Application.from_tuple(row) if row else None

    professions, countries, states = _load_select_data()

    applications = _attach_display_data(applications, professions, countries, states)

    return render_template(
        "candidate_applicationsmanagement.html",
        applications=applications,
        application=application,
        professions=professions,
        countries=countries,
        states=states,
        is_new=False,
    )


@login_required
@candidate_required
@candidate_bp.route(
    "/dashboard/candidate/applicationmanagement/save",
    methods=["POST"]
)
def applicationsmanagement_save():
    """
    Save new or existing application.
    """
    user_id      = current_user.id
    app_id       = request.form.get("id")
    profession_id = request.form.get("profession_id")
    country_id    = request.form.get("country_id")
    state_id      = request.form.get("state_id")

    #print(f"Saving application: id={app_id}, user_id={user_id}, profession_id={profession_id}, country_id={country_id}, state_id={state_id}")

    if app_id:
        update_app_tuple = Application.get_by_id(app_id)
        update_app = Application.from_tuple(update_app_tuple)
        values = (
            user_id,
            profession_id,
            country_id,
            state_id,
            app_id
        )
        update_app.update(values)
        selected_id = app_id
    else:
        new_application = Application(
            user_id=user_id,
            profession_id=profession_id,
            country_id=country_id,
            state_id=state_id,
        )
        new_app_tuple = new_application.insert()
        selected_id = new_app_tuple[0] if new_app_tuple else None

    try:
        db.connect()
        # Add all requirements for the profession, country and state to the application
        if selected_id:
            # Fetch all requirements for the selected profession, country, and state
            req_tuples = db.execute_query(
                """
                SELECT id FROM _requirements
                WHERE profession_id = %s AND country_id = %s AND (state_id = %s OR state_id IS NULL)
                """,
                (profession_id, country_id, state_id)
            )
            requirement_ids = [rt[0] for rt in req_tuples] if req_tuples else []
            #print(f"Linking requirements {requirement_ids} to application {selected_id}")
            

            # Clear existing links
            db.execute_query(
                """
                DELETE FROM _app_docs
                WHERE application_id = %s
                """,
                (selected_id,)
            )
            # Link each requirement to the application    
            for req_id in requirement_ids:
                db.execute_query(
                    """
                    INSERT INTO _app_docs (id, application_id, document_id, requirements_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (str(uuid4()), selected_id, None, req_id)
                )
    except Exception as e:
        print(f"Error linking requirements to application {selected_id}: {e}")
    finally:
        db.close_conn()

    return redirect(url_for("candidate.applicationsmanagement_detail", app_id=selected_id))


@login_required
@candidate_required
@candidate_bp.route(
    "/dashboard/candidate/applicationmanagement/<app_id>/delete",
    methods=["POST"]
)
def applicationsmanagement_delete(app_id):
    """
    Delete existing application.
    """
    delete_app_tuple = Application.get_by_id(app_id)
    delete_app = Application.from_tuple(delete_app_tuple)
    result = delete_app.delete()
    if result:
        # flash success message
        flash(f"Application {app_id} deleted successfully.")
    else:
        flash(f"Application {app_id} could not be deleted.")
    return redirect(url_for("candidate.applicationsmanagement_new"))


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/contact-recruiter")
def contact_recruiter():
    return render_template("candidate_contactrecruiter.html")