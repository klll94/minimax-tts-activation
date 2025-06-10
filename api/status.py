import json
import sys
import os
from http.server import BaseHTTPRequestHandler

# 添加上级目录到Python路径，以便导入license_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from license_manager import LicenseManager
except ImportError:
    LicenseManager = None

def cors_headers():
    """返回CORS头部"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

def check_activation_status_simple(activation_code):
    """简化版状态查询（用于Vercel环境）"""
    # 基本格式检查
    if len(activation_code) != 15:
        return False, "激活码必须是15位"
    
    # 检查字符集
    allowed_chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    for char in activation_code:
        if char not in allowed_chars:
            return False, "激活码包含无效字符"
    
    # 模拟状态查询结果
    test_codes = {
        "23456789ABCDEFG": {
            "status": "activated",
            "message": "激活码已激活",
            "expire_date": "2025-12-31T23:59:59",
            "days_valid": 365,
            "activation_count": 1,
            "device_info": {
                "device_fingerprint": "test_device_001",
                "first_activation": "2024-06-10T10:00:00",
                "last_activation": "2024-06-10T10:00:00"
            }
        },
        "A23456789BCDEFG": {
            "status": "valid",
            "message": "激活码有效，未激活",
            "expire_date": "2025-12-31T23:59:59",
            "days_valid": 365,
            "activation_count": 0
        },
        "B23456789CDEFGH": {
            "status": "expired",
            "message": "激活码已过期",
            "expire_date": "2024-01-01T23:59:59",
            "days_valid": 365,
            "activation_count": 0
        }
    }
    
    if activation_code in test_codes:
        return True, test_codes[activation_code]
    else:
        return False, "激活码不存在"

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_response(200)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()

    def do_POST(self):
        """处理POST请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # 解析JSON
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_error_response(400, "无效的JSON格式")
                return
            
            # 检查激活码参数
            if 'activation_code' not in data:
                self.send_error_response(400, "缺少activation_code参数")
                return
            
            activation_code = data['activation_code'].strip()
            
            # 查询状态
            if LicenseManager:
                # 使用完整的license_manager
                try:
                    license_manager = LicenseManager()
                    success, result = license_manager.check_activation_status(activation_code)
                except Exception as e:
                    # 如果license_manager出错，回退到简化查询
                    success, result = check_activation_status_simple(activation_code)
            else:
                # 使用简化查询
                success, result = check_activation_status_simple(activation_code)
            
            # 返回结果
            if success:
                response_data = {
                    "success": True,
                    "data": result
                }
            else:
                response_data = {
                    "success": False,
                    "error": result
                }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            self.send_error_response(500, f"服务器错误: {str(e)}")

    def send_json_response(self, status_code, data):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()
        
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

    def send_error_response(self, status_code, message):
        """发送错误响应"""
        error_data = {
            "success": False,
            "error": message
        }
        self.send_json_response(status_code, error_data) 
