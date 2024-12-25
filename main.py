import os
import json
import time
import random
import logging
import hashlib
import requests
import urllib.parse
from push import push
from config import Config
import pymysql
from pymysql.cursors import DictCursor

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)-8s - %(message)s')
logger = logging.getLogger(__name__)

# 从capture.py导入基础数据
from capture import data as base_data

def get_db():
    """获取数据库连接"""
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=DictCursor
    )

def encode_data(data):
    """对数据进行URL编码"""
    return '&'.join(f"{k}={urllib.parse.quote(str(data[k]), safe='')}" 
                   for k in sorted(data.keys()))

def cal_hash(input_string):
    """计算哈希值"""
    _7032f5 = 0x15051505
    _cc1055 = _7032f5
    length = len(input_string)
    _19094e = length - 1

    while _19094e > 0:
        _7032f5 = 0x7fffffff & (_7032f5 ^ ord(input_string[_19094e]) << (length - _19094e) % 30)
        _cc1055 = 0x7fffffff & (_cc1055 ^ ord(input_string[_19094e - 1]) << _19094e % 30)
        _19094e -= 2

    return hex(_7032f5 + _cc1055)[2:].lower()

def get_wr_skey(headers, cookies):
    """刷新wr_skey"""
    try:
        cookie_data = {"rq": "%2Fweb%2Fbook%2Fread"}
        response = requests.post(
            Config.WXREAD_BASE_URL + '/web/login/renewal',
            headers=headers,
            cookies=cookies,
            data=json.dumps(cookie_data, separators=(',', ':'))
        )
        for cookie in response.headers.get('Set-Cookie', '').split(';'):
            if "wr_skey" in cookie:
                return cookie.split('=')[-1][:8]
    except Exception as e:
        logger.error(f"Failed to refresh wr_skey: {str(e)}")
    return None

def run_read_task(headers, cookies, read_num=120, push_config=None, config_id=None):
    """运行阅读任务"""
    logger.info("Starting read task...")
    
    def check_if_stopped():
        """检查任务是否被停止"""
        if not config_id:
            return False
            
        db = get_db()
        cur = db.cursor()
        cur.execute('''
            SELECT is_running 
            FROM user_configs 
            WHERE id = %s
        ''', (config_id,))
        result = cur.fetchone()
        cur.close()
        db.close()
        
        return not result or not result['is_running']
    
    # 创建任务历史记录
    if config_id:
        db = get_db()
        cur = db.cursor()
        cur.execute('''
            INSERT INTO task_history (config_id, start_time, status)
            VALUES (%s, NOW(), 'running')
        ''', (config_id,))
        task_id = cur.lastrowid
        db.commit()
        cur.close()
        db.close()
    
    try:
        data = base_data.copy()
        
        index = 1
        while index <= read_num:
            # 检查是否被停止
            if check_if_stopped():
                logger.info("Task was stopped by user")
                return
            
            try:
                # 更新时间戳和随机数
                data['ct'] = int(time.time())
                data['ts'] = int(time.time() * 1000)
                data['rn'] = random.randint(0, 1000)
                
                # 计算签名
                data['sg'] = hashlib.sha256(
                    f"{data['ts']}{data['rn']}{Config.WXREAD_KEY}".encode()
                ).hexdigest()
                data['s'] = cal_hash(encode_data(data))
                
                logger.info(f"⏱️ 尝试第 {index} 次阅读...")
                
                # 发送阅读请求
                response = requests.post(
                    Config.WXREAD_READ_URL,
                    headers=headers,
                    cookies=cookies,
                    data=json.dumps(data, separators=(',', ':'))
                )
                
                result = response.json()
                
                if 'succ' in result:
                    index += 1
                    logger.info(f"✅ 阅读成功，阅读进度：{(index-1) * 0.5} 分钟")
                    time.sleep(30)
                else:
                    logger.warning("❌ cookie 已过期，尝试刷新...")
                    new_skey = get_wr_skey(headers, cookies)
                    if new_skey:
                        cookies['wr_skey'] = new_skey
                        # 更新数据库中的cookies
                        if config_id:
                            db = get_db()
                            cur = db.cursor()
                            cur.execute('''
                                UPDATE user_configs 
                                SET cookies = %s 
                                WHERE id = %s
                            ''', (json.dumps(cookies), config_id))
                            db.commit()
                            cur.close()
                            db.close()
                        logger.info(f"✅ 密钥刷新成功，新密钥：{new_skey}")
                        logger.info(f"🔄 重新本次阅读。")
                    else:
                        error_msg = "❌ 无法获取新密钥，终止运行。"
                        logger.error(error_msg)
                        if push_config and push_config['method']:
                            push(error_msg, **push_config)
                        raise Exception(error_msg)
                
                # 清除本次签名
                data.pop('s', None)
                    
            except Exception as e:
                error_msg = f"❌ 阅读失败: {str(e)}"
                logger.error(error_msg)
                if push_config and push_config['method']:
                    push(error_msg, **push_config)
                raise
            
        success_msg = f"🎉 阅���任务完成！共阅读 {(index-1)*0.5} 分钟"
        logger.info(success_msg)
        if push_config and push_config['method']:
            push(success_msg, **push_config)
        
        # 更新任务历史记录为成功
        if config_id:
            db = get_db()
            cur = db.cursor()
            cur.execute('''
                UPDATE task_history 
                SET status = 'success', end_time = NOW(), read_minutes = %s
                WHERE id = %s
            ''', ((index-1) * 0.5, task_id))
            db.commit()
            cur.close()
            db.close()
            
    except Exception as e:
        # 更新任务历史记录为失败
        if config_id:
            db = get_db()
            cur = db.cursor()
            cur.execute('''
                UPDATE task_history 
                SET status = 'failed', end_time = NOW(), error_message = %s
                WHERE id = %s
            ''', (str(e), task_id))
            db.commit()
            cur.close()
            db.close()
        raise

if __name__ == '__main__':
    # 本地测试用
    from capture import headers, cookies
    run_read_task(headers, cookies)
