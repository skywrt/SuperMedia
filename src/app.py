# src/app.py
import os
import json
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from sehuatang_scraper import SeHuaTangScraper
from downloader import DownloaderClient

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
app.secret_key = os.urandom(24)

# 加载配置
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

CONFIG = load_config()

# 从环境变量获取用户名密码
VALID_USERNAME = os.environ.get('WEB_USERNAME', 'admin')
VALID_PASSWORD = os.environ.get('WEB_PASSWORD', 'supermedia123')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html', config=CONFIG['web'])

@app.route('/search')
@login_required
def search():
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify({'error': '请输入搜索内容'}), 400
    
    try:
        scraper = SeHuaTangScraper(CONFIG['search_sources']['sehuatang'])
        results = scraper.search(keyword)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
@login_required
def download():
    data = request.json
    magnet = data.get('magnet')
    title = data.get('title')
    downloader_type = data.get('downloader', os.environ.get('DOWNLOADER_TYPE', 'aria2'))
    
    if not magnet:
        return jsonify({'error': '缺少磁力链接'}), 400
    
    try:
        client = DownloaderClient(
            downloader_type,
            os.environ.get('DOWNLOADER_URL', ''),
            os.environ.get('DOWNLOADER_TOKEN', '')
        )
        task_id = client.add_download(magnet, title)
        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5678, debug=False)
