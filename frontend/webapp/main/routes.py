from flask import (
    render_template, request, redirect, url_for, flash,
    send_from_directory, current_app
)
from werkzeug.utils import secure_filename
import os

from . import main_bp
from backend.utils.state_rules import STATE_CHECKLISTS
from backend.utils.validators import valid_email, valid_name
from backend.services.validator import infer_present_docs

def _allowed_file(filename: str) -> bool:
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    )

@main_bp.route('/')
def index():
    return render_template('index.html', states=sorted(STATE_CHECKLISTS.keys()))

@main_bp.route('/upload', methods=['POST'])
def upload():
    try:
        candidate_name = request.form.get('candidate_name', '').strip()
        email = request.form.get('email', '').strip()
        state = request.form.get('state', 'Berlin')

        # Input validation
        if not valid_name(candidate_name):
            flash('Please enter a valid candidate name (no path separators or control characters).')
            return redirect(url_for('main.index'))
        if not valid_email(email):
            flash('Please enter a valid email address.')
            return redirect(url_for('main.index'))
        if state not in STATE_CHECKLISTS:
            flash('Invalid state selected.')
            return redirect(url_for('main.index'))

        files = request.files.getlist('files') or []
        if not files:
            flash('No files attached.')
            return redirect(url_for('main.index'))
        if len(files) > current_app.config['MAX_FILES_PER_UPLOAD']:
            flash(f'Too many files. Max {current_app.config["MAX_FILES_PER_UPLOAD"]} allowed per upload.')
            return redirect(url_for('main.index'))

        # create per-candidate folder (name_email)
        cand_dir_name = secure_filename(f"{candidate_name}_{email}")
        cand_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], cand_dir_name)
        os.makedirs(cand_dir, exist_ok=True)

        uploaded, bad_type = [], []
        for file in files:
            if not file or not file.filename:
                continue
            if not _allowed_file(file.filename):
                bad_type.append(file.filename)
                continue
            mime = (file.mimetype or '').lower()
            if mime not in current_app.config['ALLOWED_MIME_TYPES']:
                bad_type.append(file.filename)
                continue

            fname = secure_filename(file.filename)
            file.save(os.path.join(cand_dir, fname))
            uploaded.append(f"{cand_dir_name}/{fname}")  # store relative path for serving

        if not uploaded:
            flash('No valid files uploaded. Allowed types: PDF, JPG, PNG.')
            if bad_type:
                flash('Rejected: ' + ', '.join(bad_type[:5]) + ('...' if len(bad_type) > 5 else ''))
            return redirect(url_for('main.index'))

        # Keep your detection logic
        uploaded_names_only = [os.path.basename(p) for p in uploaded]
        present = infer_present_docs(uploaded_names_only)
        required = STATE_CHECKLISTS.get(state, [])
        missing = [doc for doc in required if doc not in present]

        return render_template(
            'results.html',
            candidate_name=candidate_name,
            email=email,
            state=state,
            uploaded=uploaded,               # include relative paths
            required=required,
            present=sorted(list(present)),
            missing=missing
        )
    except Exception:
        flash('An unexpected error occurred while processing your upload.')
        return redirect(url_for('main.index'))

@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # filename is like "candidate_email/file.pdf"
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
