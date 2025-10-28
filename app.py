from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
from config import Config
from utils.state_rules import STATE_CHECKLISTS
from services.validator import infer_present_docs

app = Flask(__name__)
app.config.from_object(Config)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html', states=sorted(STATE_CHECKLISTS.keys()))

@app.route('/upload', methods=['POST'])
def upload():
    candidate_name = request.form.get('candidate_name', '').strip()
    email = request.form.get('email', '').strip()
    state = request.form.get('state', 'Berlin')

    if not candidate_name or not email:
        flash('Please enter candidate name and email.')
        return redirect(url_for('index'))

    # create per-candidate folder
    cand_dir = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f"{candidate_name}_{email}"))
    os.makedirs(cand_dir, exist_ok=True)

    uploaded = []
    for file in request.files.getlist('files'):
        if file and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            file.save(os.path.join(cand_dir, fname))
            uploaded.append(fname)

    if not uploaded:
        flash('No valid files uploaded. Allowed: pdf, jpg, jpeg, png')
        return redirect(url_for('index'))

    # Very simple rules-based presence check
    required = STATE_CHECKLISTS.get(state, [])
    present = infer_present_docs(uploaded)
    missing = [doc for doc in required if doc not in present]

    return render_template('results.html',
                           candidate_name=candidate_name,
                           email=email,
                           state=state,
                           uploaded=uploaded,
                           required=required,
                           present=sorted(list(present)),
                           missing=missing)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
