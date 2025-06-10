from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """处理POST请求"""
        # 设置响应头
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                activation_code = data.get('activation_code', '').strip()
            else:
                activation_code = ''
            
            # 查询状态
            status_info = self.get_status(activation_code)
            if status_info:
                response = {
                    "success": True,
                    "data": status_info
                }
            else:
                response = {
                    "success": False,
                    "error": "激活码不存在或无效"
                }
            
            # 发送JSON响应
            response_json = json.dumps(response, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            # 错误处理
            error_response = {
                "success": False,
                "error": f"服务器错误: {str(e)}"
            }
            error_json = json.dumps(error_response, ensure_ascii=False)
            self.wfile.write(error_json.encode('utf-8'))
    
    def get_status(self, code):
        """获取激活码状态"""
        if len(code) != 15:
            return None
        
        # 检查字符集
        allowed_chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        for char in code:
            if char not in allowed_chars:
                return None
        
        # 模拟状态数据
        status_data = {
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
            },
            "35X3M278XQNFLEQ": {
                "status": "valid",
                "message": "真实激活码，有效",
                "expire_date": "2025-06-10T23:59:59",
                "days_valid": 365,
                "activation_count": 0
            }
        }
        
        return status_data.get(code, None)
