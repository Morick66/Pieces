from functools import wraps
from flask import Flask, Response, request, render_template, redirect, url_for, jsonify, send_from_directory
import json
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
IDEAS_FILE = '/data/data.json'
UPLOAD_FOLDER = '/data/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

USERNAME = os.getenv('USERNAME', 'admain')
PASSWORD = os.getenv('PASSWORD', 'pieces')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def load_ideas():
    if os.path.exists(IDEAS_FILE):
        with open(IDEAS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def save_ideas(ideas):
    with open(IDEAS_FILE, 'w', encoding='utf-8') as file:
        json.dump(ideas, file, ensure_ascii=False, indent=4)

def get_timestamped_filename(filename):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{timestamp}_{uuid.uuid4().hex}.{ext}"
    return new_filename

@app.route('/')
@requires_auth
def index():
    ideas = load_ideas()
    return render_template('index.html', ideas=ideas)

@app.route('/add', methods=['POST'])
@requires_auth
def add_idea():
    new_idea = request.form.get('idea')
    local_timestamp = request.form.get('local_timestamp')
    file = request.files.get('file')
    if new_idea:
        ideas = load_ideas()
        timestamp = local_timestamp
        idea_id = str(uuid.uuid4())
        filename = None
        if file and allowed_file(file.filename):
            filename = get_timestamped_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ideas.insert(0, {'id': idea_id, 'idea': new_idea, 'timestamp': timestamp, 'image': filename})
        save_ideas(ideas)
    return redirect(url_for('index'))

@app.route('/delete/<idea_id>', methods=['POST'])
@requires_auth
def delete_idea(idea_id):
    ideas = load_ideas()
    for idea in ideas:
        if idea['id'] == idea_id:
            if idea.get('image'):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], idea['image']))
            ideas.remove(idea)
            break
    save_ideas(ideas)
    return '', 204

@app.route('/edit/<idea_id>', methods=['GET', 'POST'])
@requires_auth
def edit_idea(idea_id):
    ideas = load_ideas()
    idea = next((idea for idea in ideas if idea['id'] == idea_id), None)
    if request.method == 'POST':
        new_idea = request.form.get('idea')
        file = request.files.get('file')
        if idea:
            if new_idea:
                idea['idea'] = new_idea
            if file and allowed_file(file.filename):
                if idea.get('image'):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], idea['image']))
                filename = get_timestamped_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                idea['image'] = filename
            save_ideas(ideas)
            return redirect(url_for('index'))
    return render_template('edit.html', idea=idea)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/data.json')
def get_ideas_json():
    if os.path.exists(IDEAS_FILE):
        with open(IDEAS_FILE, 'r', encoding='utf-8') as file:
            ideas = json.load(file)
        return jsonify(ideas)
    return jsonify([])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
