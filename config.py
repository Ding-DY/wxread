import os
from datetime import timedelta

class Config:
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    
    # MySQL配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '700826')
    MYSQL_DB = os.getenv('MYSQL_DB', 'wxread')
    
    # 微信读书配置
    WXREAD_BASE_URL = 'https://weread.qq.com'
    WXREAD_READ_URL = WXREAD_BASE_URL + '/web/book/read'
    WXREAD_KEY = "3c5c8717f3daf09iop3423zafeqoi"
    
    # 日志配置
    LOG_DIR = 'logs'
    LOG_FILE = os.path.join(LOG_DIR, 'wxread.log')
    LOG_FORMAT = '%(asctime)s - %(levelname)-8s - %(message)s'
    
    # 任务配置
    MAX_CONCURRENT_TASKS = 5  # 最大并发任务数
    MAX_RUN_TIME = 7200  # 最大运行时间(秒)
    DEFAULT_READ_NUM = 120  # 默认阅读次数
    
    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # 推送配置
    PUSHPLUS_URL = 'http://www.pushplus.plus/send'
    TELEGRAM_API_URL = 'https://api.telegram.org/bot{}/sendMessage'
