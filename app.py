#****************************************************************************
#    Application:   Annerkennung Ai Cockpit
#    Module:        app         
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
from config import StrictConfig as Config
from utils.state_rules import STATE_CHECKLISTS
from utils.validators import valid_email, valid_name, ext_allowed
from services.validator import infer_present_docs

#=== Flask App Setup

app = Flask(__name__)
app.config.from_object(Config)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.after_request
def add_security_header(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['X-XSS-Protection'] = '1; mode=block'
    return resp

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404

@app.errorhandler(413)
def too_large(e):
    return render_template('error.html', code=413, message='Upload too large. Reduce file size or count.'), 413

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Unexpected server error.'), 500

@app.route('/')
def index():
    return render_template('index.html', states=sorted(STATE_CHECKLISTS.keys()))

@app.route('/upload', methods=['POST'])
def upload():
    try:
        candidate_name = request.form.get('candidate_name', '').strip()
        email = request.form.get('email', '').strip()
        print(email)
        state = request.form.get('state', 'Berlin')

        # Input validation
        if not valid_name(candidate_name):
            flash('Please enter a valid candidate name (no path separators or control characters).')
            return redirect(url_for('index'))
        if not valid_email(email):
            flash('Please enter a valid email address.')
            return redirect(url_for('index'))
        if state not in STATE_CHECKLISTS:
            flash('Invalid state selected.')
            return redirect(url_for('index'))

        files = request.files.getlist('files') or []
        if not files:
            flash('No files attached.')
            return redirect(url_for('index'))
        if len(files) > app.config['MAX_FILES_PER_UPLOAD']:
            flash(f'Too many files. Max {app.config["MAX_FILES_PER_UPLOAD"]} allowed per upload.')
            return redirect(url_for('index'))

        # create per-candidate folder
        cand_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f"{candidate_name}_{email}"))
        os.makedirs(cand_dir, exist_ok=True)

        uploaded = []
        bad_type = []
        for file in files:
            if not file or not file.filename:
                continue
            if not allowed_file(file.filename):
                bad_type.append(file.filename)
                continue
            mime = (file.mimetype or '').lower()
            if mime not in app.config['ALLOWED_MIME_TYPES']:
                bad_type.append(file.filename)
                continue

            fname = secure_filename(file.filename)
            file.save(os.path.join(cand_dir, fname))
            uploaded.append(fname)

        if not uploaded:
            flash('No valid files uploaded. Allowed types: PDF, JPG, PNG.')
            if bad_type:
                flash('Rejected: ' + ', '.join(bad_type[:5]) + ('...' if len(bad_type) > 5 else ''))
            return redirect(url_for('index'))

        present = infer_present_docs(uploaded)
        required = STATE_CHECKLISTS.get(state, [])
        missing = [doc for doc in required if doc not in present]

        return render_template('results.html',
                               candidate_name=candidate_name,
                               email=email,
                               state=state,
                               uploaded=uploaded,
                               required=required,
                               present=sorted(list(present)),
                               missing=missing)
    except Exception:
        flash('An unexpected error occurred while processing your upload.')
        return redirect(url_for('index'))


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
