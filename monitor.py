from datetime import datetime
import pymysql
from pymysql.cursors import DictCursor
from config import Config
import logging
from push import push

logger = logging.getLogger(__name__)

def get_db():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=DictCursor
    )

def check_running_tasks():
    db = get_db()
    cur = db.cursor()
    try:
        # 检查运行中的任务
        cur.execute('SELECT * FROM user_configs WHERE is_running = TRUE')
        running_configs = cur.fetchall()
        
        # 检查并发任务数量
        if len(running_configs) > Config.MAX_CONCURRENT_TASKS:
            logger.warning(f"Too many concurrent tasks: {len(running_configs)}")
            # 保留最早启动的任务，停止其他任务
            configs_to_stop = sorted(running_configs, 
                                   key=lambda x: x['last_run'])[Config.MAX_CONCURRENT_TASKS:]
            for config in configs_to_stop:
                cur.execute('''
                    UPDATE user_configs 
                    SET is_running = FALSE 
                    WHERE id = %s
                ''', (config['id'],))
                # 发送通知
                if config['push_method']:
                    push("❌ 任务被强制停止：并发任务数超限", 
                         config['push_method'],
                         config['pushplus_token'],
                         config['telegram_bot_token'],
                         config['telegram_chat_id'])
        
        # 检查任务运行时间
        for config in running_configs:
            if config['last_run'] and (datetime.now() - config['last_run']).total_seconds() > Config.MAX_RUN_TIME:
                logger.warning(f"Task {config['id']} exceeded max run time")
                cur.execute('''
                    UPDATE user_configs 
                    SET is_running = FALSE 
                    WHERE id = %s
                ''', (config['id'],))
                # 发送通知
                if config['push_method']:
                    push("❌ 任务被强制停止：超过最大运行时间", 
                         config['push_method'],
                         config['pushplus_token'],
                         config['telegram_bot_token'],
                         config['telegram_chat_id'])
        
        db.commit()
    except Exception as e:
        logger.error(f"Error checking running tasks: {str(e)}")
    finally:
        cur.close()
        db.close()

def cleanup_expired_schedules():
    """清理过期的一次性调度"""
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute('''
            UPDATE user_configs 
            SET schedule_type = NULL, schedule_time = NULL, schedule_days = NULL 
            WHERE schedule_type = 'once' 
            AND schedule_time < NOW()
        ''')
        db.commit()
    finally:
        cur.close()
        db.close()

if __name__ == '__main__':
    import time
    while True:
        check_running_tasks()
        cleanup_expired_schedules()
        time.sleep(60) 