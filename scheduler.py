import schedule
import time
from datetime import datetime, timedelta
import pymysql
from pymysql.cursors import DictCursor
from config import Config
import json
import logging
import threading
from main import run_read_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=DictCursor
    )

def run_scheduled_task(config_id):
    """执行定时任务"""
    logger.info(f"Running scheduled task for config {config_id}")
    try:
        db = get_db()
        cur = db.cursor()
        
        # 获取配置信息
        cur.execute('SELECT * FROM user_configs WHERE id = %s', (config_id,))
        config = cur.fetchone()
        
        if not config or not config['is_active']:
            logger.warning(f"Config {config_id} is not active or not found")
            return
            
        # 设置运行状态
        cur.execute('''
            UPDATE user_configs 
            SET is_running = TRUE, last_run = NOW()
            WHERE id = %s
        ''', (config_id,))
        db.commit()
            
        # 如果是单次任务，执行后清除调度
        if config['schedule_type'] == 'once':
            cur.execute('''
                UPDATE user_configs 
                SET schedule_type = NULL, schedule_time = NULL, schedule_days = NULL 
                WHERE id = %s
            ''', (config_id,))
            db.commit()
        
        # 准备推送配置
        push_config = None
        if config['push_method']:
            push_config = {
                'method': config['push_method'],
                'pushplus_token': config['pushplus_token'],
                'telegram_bot_token': config['telegram_bot_token'],
                'telegram_chat_id': config['telegram_chat_id']
            }
        
        # 在新线程中运行任务
        headers = json.loads(config['headers'])
        cookies = json.loads(config['cookies'])
        thread = threading.Thread(
            target=run_read_task,
            args=(headers, cookies, config['read_num'], push_config, config_id)
        )
        thread.start()
        
    except Exception as e:
        logger.error(f"Error running scheduled task: {str(e)}")
    finally:
        cur.close()
        db.close()

def setup_schedules():
    """设置所有定时任务"""
    logger.info("Setting up schedules...")
    schedule.clear()
    
    db = get_db()
    cur = db.cursor()
    try:
        # 获取所有启用的定时任务
        cur.execute('''
            SELECT id, schedule_type, schedule_time, schedule_days 
            FROM user_configs 
            WHERE is_active = TRUE 
            AND schedule_type IS NOT NULL 
            AND schedule_time IS NOT NULL
        ''')
        configs = cur.fetchall()
        
        for config in configs:
            if not config['schedule_time']:
                continue
                
            schedule_time = config['schedule_time']
            if isinstance(schedule_time, timedelta):
                schedule_time = (datetime.min + schedule_time).time()
            
            time_str = schedule_time.strftime('%H:%M')
            
            if config['schedule_type'] == 'daily':
                schedule.every().day.at(time_str).do(
                    run_scheduled_task, config['id']
                ).tag(f'config_{config["id"]}')
                logger.info(f"Set up daily task for config {config['id']} at {time_str}")
                
            elif config['schedule_type'] == 'weekly' and config['schedule_days']:
                days = config['schedule_days'].split(',')
                for day in days:
                    scheduler = None
                    if day == '1':  # 周一
                        scheduler = schedule.every().monday
                    elif day == '2':  # 周二
                        scheduler = schedule.every().tuesday
                    elif day == '3':  # 周三
                        scheduler = schedule.every().wednesday
                    elif day == '4':  # 周四
                        scheduler = schedule.every().thursday
                    elif day == '5':  # 周五
                        scheduler = schedule.every().friday
                    elif day == '6':  # 周六
                        scheduler = schedule.every().saturday
                    elif day == '7':  # 周日
                        scheduler = schedule.every().sunday
                    
                    if scheduler:
                        scheduler.at(time_str).do(
                            run_scheduled_task, config['id']
                        ).tag(f'config_{config["id"]}')
                        logger.info(f"Set up weekly task for config {config['id']} on day {day} at {time_str}")
                    
            elif config['schedule_type'] == 'once':
                # 对于单次任务，检查时间是否已过
                now = datetime.now()
                schedule_datetime = datetime.combine(now.date(), schedule_time)
                if schedule_datetime <= now:
                    schedule_datetime += timedelta(days=1)
                
                schedule.every().day.at(time_str).do(
                    run_scheduled_task, config['id']
                ).tag(f'config_{config["id"]}')
                logger.info(f"Set up one-time task for config {config['id']} at {time_str}")
                
    except Exception as e:
        logger.error(f"Error setting up schedules: {str(e)}")
    finally:
        cur.close()
        db.close()

def reload_schedules():
    """重新加载所有调度"""
    logger.info("Reloading schedules...")
    setup_schedules()

if __name__ == '__main__':
    setup_schedules()
    # 每小时重新加载一次调度
    schedule.every().hour.do(reload_schedules)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
