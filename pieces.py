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

USERNAME = os.getenv('USERNAME', 'admin')
PASSWORD = os.getenv('PASSWORD', 'pieces')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_svg(icon_name):
    path = os.path.join(app.static_folder, f"icons/{icon_name}.svg")
    try:
        with open(path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise Exception(f"Error: icon '{icon_name}.svg' is not found under 'static/icons' folder")

# 注册为全局函数
app.jinja_env.globals.update(load_svg=load_svg)

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
    link = request.form.get('link')
    local_timestamp = request.form.get('local_timestamp')
    files = request.files.getlist('files')  # 获取多个文件
    print("Received idea:", new_idea)
    ideas = load_ideas()
    idea_id = str(uuid.uuid4())
    filenames = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = get_timestamped_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filenames.append(filename)

    ideas.insert(0, {'id': idea_id, 'idea': new_idea, 'link': link, 'timestamp': local_timestamp, 'images': filenames})
    save_ideas(ideas)
    return redirect(url_for('index'))

@app.route('/delete/<idea_id>', methods=['POST'])
@requires_auth
def delete_idea(idea_id):
    ideas = load_ideas()
    updated_ideas = [idea for idea in ideas if idea['id'] != idea_id]
    # 获取需要删除的想法
    idea_to_delete = next((idea for idea in ideas if idea['id'] == idea_id), None)
    if idea_to_delete:
        # 删除关联的图片文件
        if 'images' in idea_to_delete:
            for img in idea_to_delete['images']:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
                except OSError as e:
                    print(f"Error deleting image {img}: {e}")
    # 保存更新后的想法列表
    save_ideas(updated_ideas)
    return '', 204

@app.route('/delete-image/<idea_id>/<filename>', methods=['POST'])
@requires_auth
def delete_image(idea_id, filename):
    ideas = load_ideas()
    idea = next((item for item in ideas if item['id'] == idea_id), None)
    if idea and filename in idea['images']:
        idea['images'].remove(filename)  # 从想法中删除引用
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)  # 删除文件
            save_ideas(ideas)  # 保存更改
            return '', 204
    return 'Not Found', 404

@app.route('/edit/<idea_id>', methods=['POST'])
@requires_auth
def edit_idea(idea_id):
    ideas = load_ideas()
    idea = next((idea for idea in ideas if idea['id'] == idea_id), None)
    if not idea:
        return 'Idea not found', 404

    # 更新想法内容
    new_idea_content = request.form.get('idea')
    if new_idea_content:
        idea['idea'] = new_idea_content

    # 处理新文件上传
    new_files = request.files.getlist('new_files')
    for file in new_files:
        if file and allowed_file(file.filename):
            filename = get_timestamped_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            idea['images'].append(filename)  # 添加新文件

    # 处理待删除的文件
    to_delete_files = request.form.getlist('to_delete_files')
    for filename in to_delete_files:
        if filename in idea['images']:
            idea['images'].remove(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.remove(file_path)

    save_ideas(ideas)
    return redirect(url_for('index'))


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
    app.run(host='0.0.0.0', port=10055, debug=False)
