import json
import requests
from config import Config
import ast

def process_dict_text(text):
    """处理用户输入的字典文本"""
    try:
        # 移除变量名赋值部分
        if '=' in text.split('{', 1)[0]:
            text = '{' + text.split('{', 1)[1]
        
        # 处理注释行
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if '#' in line:
                line = line[:line.index('#')]
            if line.strip():
                cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)
        
        # 尝试使用ast.literal_eval解析
        try:
            return ast.literal_eval(text)
        except:
            # 如果ast解析失败，尝试json解析
            text = text.replace("'", '"')  # 将单引号替换为双引号
            return json.loads(text)
    except Exception as e:
        raise ValueError(f"Failed to parse dictionary: {str(e)}")

def validate_headers(headers):
    """验证headers格式和必要字段"""
    required_fields = ['accept', 'content-type', 'origin', 'referer', 'user-agent']
    missing_fields = []
    
    # 不区分大小写检查
    headers_lower = {k.lower(): v for k, v in headers.items()}
    for field in required_fields:
        if field not in headers_lower:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required headers: {', '.join(missing_fields)}"
    return True, None

def validate_cookies(cookies):
    """验证cookies的有效性"""
    required_cookies = {
        'wr_skey': '登录密钥',
        'wr_vid': '用户ID',
        'wr_rt': '刷新令牌',
        'wr_localvid': '本地ID'
    }
    missing_cookies = []
    
    for cookie, desc in required_cookies.items():
        if cookie not in cookies:
            missing_cookies.append(f"{cookie} ({desc})")
    
    if missing_cookies:
        return False, (
            "缺少必要的Cookie:\n" + 
            "\n".join(f"- {cookie}" for cookie in missing_cookies) +
            "\n请确保从微信读书网页版复制完整的Cookie"
        )
        
    # 检查cookie值是否为空
    empty_cookies = [
        f"{cookie} ({desc})" 
        for cookie, desc in required_cookies.items() 
        if not cookies.get(cookie)
    ]
    if empty_cookies:
        return False, (
            "以下Cookie值为空:\n" +
            "\n".join(f"- {cookie}" for cookie in empty_cookies) +
            "\n请尝试重新登录微信读书并复制Cookie"
        )
    
    return True, None

def test_connection(headers, cookies):
    """测试连接是否有效"""
    try:
        # 先尝试访问主页
        response = requests.get('https://weread.qq.com/web/shelf', 
                              headers=headers, 
                              cookies=cookies,
                              timeout=5)
        if response.status_code != 200:
            return False, f"Failed to access WeRead (status code: {response.status_code}). Please check your cookies."
        
        # 测试是否已登录
        if 'login' in response.url.lower():
            return False, "Login required. Please update your cookies."
            
        return True, None
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def validate_config(headers_text, cookies_text):
    """验证完整配置"""
    try:
        # 解析并验证headers
        try:
            headers = process_dict_text(headers_text)
        except Exception as e:
            return False, f"Invalid headers format: {str(e)}"
        
        valid, error = validate_headers(headers)
        if not valid:
            return False, error
            
        # 解析并验证cookies
        try:
            cookies = process_dict_text(cookies_text)
        except Exception as e:
            return False, f"Invalid cookies format: {str(e)}"
            
        valid, error = validate_cookies(cookies)
        if not valid:
            return False, error
            
        # 测试连接
        valid, error = test_connection(headers, cookies)
        if not valid:
            return False, error
            
        return True, None
    except Exception as e:
        return False, f"Validation error: {str(e)}" 