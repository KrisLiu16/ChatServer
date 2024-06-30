from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory, flash, session
from werkzeug.utils import secure_filename
import uuid
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'static/uploads'
AVATAR_FOLDER = 'static/avatars'
CHAT_FOLDER = 'static/chat'
DATA_FOLDER = 'data'
ADMIN_PASSWORD = 'maomaoqiu'  # 管理员密码

# 确保文件夹存在
for folder in [UPLOAD_FOLDER, AVATAR_FOLDER, CHAT_FOLDER, DATA_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)


# 加载所有用户信息
def load_users():
    users = []
    for filename in os.listdir(AVATAR_FOLDER):
        if filename.endswith('.json'):
            with open(os.path.join(AVATAR_FOLDER, filename), 'r', encoding='utf-8') as f:
                user = json.load(f)
                user['avatar_path'] = os.path.join(AVATAR_FOLDER, user['avatar'])
                users.append(user)
    return users


# 加载所有帖子信息，并按时间戳倒序排列
def load_posts():
    posts = []
    for filename in os.listdir(CHAT_FOLDER):
        if filename.endswith('.json'):
            with open(os.path.join(CHAT_FOLDER, filename), 'r', encoding='utf-8') as f:
                post = json.load(f)
                posts.append(post)
    posts_sorted = sorted(posts, key=lambda x: x['timestamp'], reverse=True)
    return posts_sorted


# 主页，显示聊天内容
@app.route('/')
def chat():
    if 'user' not in session:
        return redirect(url_for('login'))

    posts = load_posts()
    users = load_users()
    current_user = session['user']

    # 为当前用户添加头像路径
    for user in users:
        if user['nickname'] == current_user['nickname']:
            current_user['avatar_path'] = user['avatar_path']
            break

    return render_template('chat.html', posts=posts, current_user=current_user)


# 登录页面，处理用户登录请求
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        users = load_users()
        user = next((user for user in users if user['nickname'] == nickname and user['password'] == password), None)
        if user:
            session['user'] = user
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': '昵称或密码错误'})

    return render_template('login.html')


# 注册页面，处理用户注册请求
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        avatar = request.files['avatar']

        # 生成唯一标识符
        uid = datetime.now().strftime('%Y%m%d%H%M%S%f')

        # 检查昵称是否已存在
        users = load_users()
        if any(user['nickname'] == nickname for user in users):
            return jsonify({'success': False, 'message': '昵称已被占用'})

        # 保存头像文件
        avatar_filename = f'{uid}.png'
        avatar_path = os.path.join(AVATAR_FOLDER, avatar_filename)
        avatar.save(avatar_path)

        # 保存用户信息到 JSON 文件
        user = {'nickname': nickname, 'password': password, 'avatar': avatar_filename}
        user_path = os.path.join(AVATAR_FOLDER, f'{nickname}.json')
        with open(user_path, 'w', encoding='utf-8') as f:
            json.dump(user, f, ensure_ascii=False, indent=4)

        # 存储用户会话
        session['user'] = user

        return jsonify({'success': True, 'message': '注册成功'})

    return render_template('register.html')
#登出
@app.route('/logout', methods=['GET'])
def logout():
    # 清空表单
    session.clear()
    # 重定向到登录
    return redirect(url_for('login'))

# 注销，清除用户会话并删除用户文件和头像
@app.route('/logoff', methods=['GET'])
def logoff():
    if 'user' in session:
        user = session['user']
        # 删除用户 JSON 文件
        user_json_path = os.path.join(AVATAR_FOLDER, user['nickname'] + '.json')
        if os.path.exists(user_json_path):
            os.remove(user_json_path)

        # 删除用户头像文件
        avatar_path = os.path.join(AVATAR_FOLDER, user['avatar'])
        if os.path.exists(avatar_path):
            os.remove(avatar_path)

        # 清空会话
        session.clear()

    # 重定向到登录页面
    return redirect(url_for('login'))


# 发布新帖子，处理帖子提交请求
@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        text = request.form['text']
        images = request.files.getlist('images')
        image_filenames = []
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        for image in images:
            if image:
                image_filename = secure_filename(timestamp + '_' + image.filename)
                image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                image.save(image_path)
                image_filenames.append(image_filename)

        post = {
            'id': str(uuid.uuid4()),
            'nickname': session['user']['nickname'],
            'avatar': session['user']['avatar'],
            'text': text,
            'images': image_filenames,
            'timestamp': timestamp
        }
        post_path = os.path.join(CHAT_FOLDER, timestamp + '.json')
        with open(post_path, 'w', encoding='utf-8') as f:
            json.dump(post, f, ensure_ascii=False, indent=4)

        return redirect(url_for('chat'))
    return render_template('new_post.html')
# 删除帖子，根据帖子ID删除对应的帖子文件
@app.route('/delete_post/<post_id>', methods=['POST'])
def delete_post(post_id):
    posts = load_posts()
    post = next((post for post in posts if post['id'] == post_id), None)
    if post:
        post_path = os.path.join(CHAT_FOLDER, post['timestamp'] + '.json')
        if os.path.exists(post_path):
            os.remove(post_path)
        posts.remove(post)
    return redirect(url_for('chat'))


# 文件上传页面
@app.route('/file')
def upload_file():
    return render_template('upload.html')


# 处理文件上传请求
@app.route('/upload', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        return jsonify({'message': '未选择文件', 'success': False})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': '未选择文件', 'success': False})
    if file:
        file_path = os.path.join(DATA_FOLDER, file.filename)
        file.save(file_path)
        return jsonify({'message': '文件上传成功', 'success': True})


# 管理员登录页面
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            return redirect(url_for('file_list'))
        else:
            flash('密码错误')
            return redirect(url_for('admin'))
    return render_template('admin_login.html')


# 文件列表页面，列出所有上传的文件
@app.route('/file_list')
def file_list():
    files = []
    for root, dirs, filenames in os.walk(DATA_FOLDER):
        for filename in filenames:
            filepath = os.path.relpath(os.path.join(root, filename), DATA_FOLDER)
            files.append(filepath)
    return render_template('file_list.html', files=files)


# 文件下载功能，根据文件名下载文件
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(DATA_FOLDER, filename, as_attachment=True)


# 文件删除功能，根据文件名删除文件
@app.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'文件 {filename} 删除成功')
    else:
        flash(f'文件 {filename} 未找到')
    return redirect(url_for('file_list'))


# 文件重命名功能，根据文件名重命名文件
@app.route('/rename/<path:filename>', methods=['POST'])
def rename_file(filename):
    new_name = request.form.get('new_name')
    file_path = os.path.join(DATA_FOLDER, filename)
    new_path = os.path.join(DATA_FOLDER, new_name)
    if os.path.exists(file_path):
        os.rename(file_path, new_path)
        flash(f'文件 {filename} 重命名为 {new_name}')
    else:
        flash(f'文件 {filename} 未找到')
    return redirect(url_for('file_list'))


# 主程序入口
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
