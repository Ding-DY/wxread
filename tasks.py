import json
import logging
from datetime import datetime
import pymysql
from pymysql.cursors import DictCursor
from main import run_read_task
from config import Config
import os

# 配置日志
if not os.path.exists(Config.LOG_DIR):
    os.makedirs(Config.LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=DictCursor
    )

def run_active_configs():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 获取所有活跃的配置
        cur.execute('SELECT * FROM user_configs WHERE is_active = TRUE')
        configs = cur.fetchall()
        
        for config in configs:
            try:
                # 解析配置
                headers = json.loads(config['headers'])
                cookies = json.loads(config['cookies'])
                read_num = config['read_num']
                push_method = config['push_method']
                push_config = {
                    'method': push_method,
                    'pushplus_token': config['pushplus_token'],
                    'telegram_bot_token': config['telegram_bot_token'],
                    'telegram_chat_id': config['telegram_chat_id']
                }
                
                # 运行阅读任务
                run_read_task(headers, cookies, read_num, push_config)
                
                # 更新最后运行时间
                cur.execute('''
                    UPDATE user_configs 
                    SET last_run = %s 
                    WHERE id = %s
                ''', (datetime.now(), config['id']))
                conn.commit()
                
                logger.info(f"Successfully ran configuration {config['id']}")
                
            except Exception as e:
                logger.error(f"Error running configuration {config['id']}: {str(e)}")
                continue
                
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_active_configs() 