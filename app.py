from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
import json
from config import Config
import logging
from validators import validate_config
from main import run_read_task
from scheduler import setup_schedules
import threading
import schedule
import time

app = Flask(__name__)

# 配置
app.config.from_object(Config)

# 添加自定义过滤器
@app.template_filter('dayname')
def dayname_filter(day):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    try:
        return days[int(day)-1]
    except (ValueError, IndexError):
        return 'Invalid day'

# 添加日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            cursorclass=DictCursor
        )
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT id, password_hash FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
            
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cur = db.cursor()
        
        # Check if username exists
        cur.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cur.fetchone():
            flash('Username already exists')
            return render_template('register.html')
            
        # Create new user
        password_hash = generate_password_hash(password)
        cur.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)',
                   (username, password_hash))
        db.commit()
        cur.close()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM user_configs WHERE user_id = %s', (session['user_id'],))
    configs = cur.fetchall()
    cur.close()
    
    return render_template('dashboard.html', configs=configs)

@app.route('/config/add', methods=['GET', 'POST'])
def add_config():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        try:
            # 获取用户输入
            headers_text = request.form['headers']
            cookies_text = request.form['cookies']
            read_num = request.form.get('read_num', 120)
            push_method = request.form.get('push_method', '')
            pushplus_token = request.form.get('pushplus_token', '')
            telegram_bot_token = request.form.get('telegram_bot_token', '')
            telegram_chat_id = request.form.get('telegram_chat_id', '')
            
            # 验证配置
            valid, error = validate_config(headers_text, cookies_text)
            if not valid:
                flash(f'Configuration validation failed: {error}')
                return render_template('add_config.html')
            
            # 处理headers和cookies文本
            def process_dict_text(text):
                # 移除可能的变量名赋值
                if '=' in text.split('{', 1)[0]:
                    text = '{' + text.split('{', 1)[1]
                
                # 理注释
                lines = text.split('\n')
                cleaned_lines = []
                for line in lines:
                    if '#' in line:
                        line = line[:line.index('#')]
                    if line.strip():
                        cleaned_lines.append(line)
                text = '\n'.join(cleaned_lines)
                
                # 尝试eval转换为字典
                try:
                    return eval(text)
                except:
                    # 如果eval失败，尝试使用json.loads
                    # 将Python风格的字典转换为JSON风格
                    text = text.replace("'", '"')  # 将单引号替换为双引号
                    return json.loads(text)
            
            # 转换headers和cookies
            headers_dict = process_dict_text(headers_text)
            cookies_dict = process_dict_text(cookies_text)
            
            # 转换为JSON字符串存储
            headers_json = json.dumps(headers_dict)
            cookies_json = json.dumps(cookies_dict)
            
            db = get_db()
            cur = db.cursor()
            cur.execute('''
                INSERT INTO user_configs 
                (user_id, headers, cookies, read_num, push_method, 
                pushplus_token, telegram_bot_token, telegram_chat_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (session['user_id'], headers_json, cookies_json, read_num, push_method,
                 pushplus_token, telegram_bot_token, telegram_chat_id))
            db.commit()
            cur.close()
            
            flash('Configuration added successfully!')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Error: Unable to parse headers or cookies. Please check the format. ({str(e)})')
            
    return render_template('add_config.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/config/<int:id>/toggle', methods=['POST'])
def toggle_config(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        data = request.get_json()
        active = data.get('active', False)
        
        db = get_db()
        cur = db.cursor()
        cur.execute('''
            UPDATE user_configs 
            SET is_active = %s 
            WHERE id = %s AND user_id = %s
        ''', (active, id, session['user_id']))
        db.commit()
        cur.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/config/<int:id>/details')
def config_details(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM user_configs WHERE id = %s AND user_id = %s', 
                (id, session['user_id']))
    config = cur.fetchone()
    cur.close()
    
    if not config:
        return jsonify({'error': 'Configuration not found'}), 404
        
    return jsonify({
        'id': config['id'],
        'headers': json.loads(config['headers']),
        'cookies': json.loads(config['cookies']),
        'read_num': config['read_num'],
        'push_method': config['push_method'],
        'pushplus_token': config['pushplus_token'],
        'telegram_bot_token': config['telegram_bot_token'],
        'telegram_chat_id': config['telegram_chat_id'],
        'is_active': config['is_active'],
        'last_run': config['last_run'].isoformat() if config['last_run'] else None,
        'created_at': config['created_at'].isoformat(),
        'updated_at': config['updated_at'].isoformat()
    })

@app.route('/config/<int:id>/delete', methods=['POST'])
def delete_config(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        db = get_db()
        cur = db.cursor()
        
        # 先删除相关的任务历史记录
        cur.execute('DELETE FROM task_history WHERE config_id = %s', (id,))
        
        # 再删除配置
        cur.execute('''
            DELETE FROM user_configs 
            WHERE id = %s AND user_id = %s
        ''', (id, session['user_id']))
        
        db.commit()
        cur.close()
        
        flash('配置已删除')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/config/<int:id>/start', methods=['POST'])
def start_config(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        db = get_db()
        cur = db.cursor()
        
        # 检查配置是否存在且属于当前用户
        cur.execute('SELECT * FROM user_configs WHERE id = %s AND user_id = %s', 
                   (id, session['user_id']))
        config = cur.fetchone()
        
        logger.info(f"Starting config {id} for user {session['user_id']}")
        
        if not config:
            logger.error(f"Configuration {id} not found for user {session['user_id']}")
            return jsonify({'error': 'Configuration not found'}), 404
            
        # 检查配置是否已经在运行
        if config['is_running']:
            logger.warning(f"Configuration {id} is already running")
            return jsonify({'error': 'Configuration is already running'}), 400
            
        # 检查配置是否激活
        if not config['is_active']:
            logger.warning(f"Configuration {id} is not active")
            return jsonify({'error': 'Configuration is not active'}), 400
            
        # 启动配置
        cur.execute('''
            UPDATE user_configs 
            SET is_running = TRUE 
            WHERE id = %s
        ''', (id,))
        db.commit()
        
        # 在后台启动任务
        import threading
        
        def run_task():
            with app.app_context():
                task_id = None
                try:
                    # 创建新的数据库连接
                    db = pymysql.connect(
                        host=app.config['MYSQL_HOST'],
                        user=app.config['MYSQL_USER'],
                        password=app.config['MYSQL_PASSWORD'],
                        database=app.config['MYSQL_DB'],
                        cursorclass=DictCursor
                    )
                    cur = db.cursor()
                    
                    logger.info(f"Creating task history record for config {id}")
                    # 创建任务历史记录
                    cur.execute('''
                        INSERT INTO task_history (config_id, start_time, status)
                        VALUES (%s, NOW(), 'running')
                    ''', (id,))
                    task_id = cur.lastrowid
                    db.commit()
                    
                    logger.info(f"Parsing configuration data for config {id}")
                    headers = json.loads(config['headers'])
                    cookies = json.loads(config['cookies'])
                    read_num = config['read_num']
                    
                    push_config = {
                        'method': config['push_method'],
                        'pushplus_token': config['pushplus_token'],
                        'telegram_bot_token': config['telegram_bot_token'],
                        'telegram_chat_id': config['telegram_chat_id']
                    }
                    
                    logger.info(f"Starting read task for config {id}")
                    try:
                        run_read_task(headers, cookies, int(read_num), push_config, config_id=id)
                    except Exception as e:
                        logger.error(f"Read task failed: {str(e)}")
                        raise
                    
                    logger.info(f"Read task completed successfully for config {id}")
                    # 更新任务历史为成功
                    cur.execute('''
                        UPDATE task_history 
                        SET status = 'success', end_time = NOW(), read_minutes = %s
                        WHERE id = %s
                    ''', (read_num * 0.5, task_id))
                    db.commit()
                    
                except Exception as e:
                    logger.error(f"Error running configuration {id}: {str(e)}")
                    logger.exception("Detailed error traceback:")
                    # 更新任务历史为失败
                    if task_id:
                        cur.execute('''
                            UPDATE task_history 
                            SET status = 'failed', end_time = NOW(), error_message = %s
                            WHERE id = %s
                        ''', (str(e), task_id))
                        db.commit()
                finally:
                    # 任务完成后更新状态
                    cur.execute('''
                        UPDATE user_configs 
                        SET is_running = FALSE, last_run = NOW()
                        WHERE id = %s
                    ''', (id,))
                    db.commit()
                    cur.close()
                    db.close()
        
        logger.info(f"Starting background thread for config {id}")
        thread = threading.Thread(target=run_task)
        thread.start()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error in start_config: {str(e)}")
        logger.exception("Detailed error traceback:")
        return jsonify({'error': str(e)}), 500

@app.route('/config/<int:id>/stop', methods=['POST'])
def stop_config(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        db = get_db()
        cur = db.cursor()
        
        # 更新配置状态
        cur.execute('''
            UPDATE user_configs 
            SET is_running = FALSE 
            WHERE id = %s AND user_id = %s
        ''', (id, session['user_id']))
        
        # 更新任务历史记录
        cur.execute('''
            UPDATE task_history 
            SET status = 'stopped', end_time = NOW()
            WHERE config_id = %s AND status = 'running'
        ''', (id,))
        
        db.commit()
        cur.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/config/<int:id>/schedule', methods=['POST'])
def schedule_config(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        data = request.get_json()
        schedule_type = data.get('type')
        schedule_time = data.get('time', '')
        
        # 转换时间格式
        if schedule_time:
            try:
                hours, minutes = map(int, schedule_time.split(':'))
                from datetime import time
                schedule_time = time(hours, minutes)
            except ValueError:
                return jsonify({'error': 'Invalid time format'}), 400
                
        schedule_days = data.get('days', '')
        
        db = get_db()
        cur = db.cursor()
        cur.execute('''
            UPDATE user_configs 
            SET schedule_type = %s, schedule_time = %s, schedule_days = %s 
            WHERE id = %s AND user_id = %s
        ''', (schedule_type, schedule_time, schedule_days, id, session['user_id']))
        db.commit()
        cur.close()
        
        # 重新加载调度
        from scheduler import reload_schedules
        reload_schedules()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    cur = db.cursor()
    
    # 获取用户的所有配置ID
    cur.execute('SELECT id FROM user_configs WHERE user_id = %s', (session['user_id'],))
    config_ids = [row['id'] for row in cur.fetchall()]
    
    if config_ids:
        # 获取这些配置的历史记录
        cur.execute('''
            SELECT * FROM task_history 
            WHERE config_id IN ({})
            ORDER BY start_time DESC
            LIMIT 100
        '''.format(','.join(['%s'] * len(config_ids))), tuple(config_ids))
        history = cur.fetchall()
    else:
        history = []
    
    cur.close()
    return render_template('history.html', history=history)

@app.route('/history/clear', methods=['POST'])
def clear_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        db = get_db()
        cur = db.cursor()
        
        # 获取用户的配置ID
        cur.execute('SELECT id FROM user_configs WHERE user_id = %s', (session['user_id'],))
        config_ids = [row['id'] for row in cur.fetchall()]
        
        if config_ids:
            # 删除这些配置的历史记录
            cur.execute('''
                DELETE FROM task_history 
                WHERE config_id IN ({})
            '''.format(','.join(['%s'] * len(config_ids))), tuple(config_ids))
            db.commit()
        
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/config/<int:id>/edit', methods=['POST'])
def edit_config(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        data = request.get_json()
        
        # 验证数据
        read_num = data.get('read_num', 120)
        if not isinstance(read_num, int) or read_num <= 0:
            return jsonify({'error': 'Invalid read_num'}), 400
            
        push_method = data.get('push_method', '')
        pushplus_token = data.get('pushplus_token', '')
        telegram_bot_token = data.get('telegram_bot_token', '')
        telegram_chat_id = data.get('telegram_chat_id', '')
        
        # 验证推送配置
        if push_method == 'pushplus' and not pushplus_token:
            return jsonify({'error': 'PushPlus token is required'}), 400
        if push_method == 'telegram' and (not telegram_bot_token or not telegram_chat_id):
            return jsonify({'error': 'Telegram bot token and chat ID are required'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # 更新配置
        cur.execute('''
            UPDATE user_configs 
            SET read_num = %s,
                push_method = %s,
                pushplus_token = %s,
                telegram_bot_token = %s,
                telegram_chat_id = %s
            WHERE id = %s AND user_id = %s
        ''', (read_num, push_method, pushplus_token, telegram_bot_token, 
              telegram_chat_id, id, session['user_id']))
        
        db.commit()
        cur.close()
        
        flash('配置已更新')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 启动调度器
def start_scheduler():
    setup_schedules()
    schedule.every().hour.do(setup_schedules)  # 每小时重新加载一次调度
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# 在新线程中启动调度器
scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 