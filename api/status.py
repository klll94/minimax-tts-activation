from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
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
            
            # 状态数据
            status_data = {
                "23456789ABCDEFG": {
                    "status": "activated",
                    "message": "激活码已激活",
                    "expire_date": "2025-12-31T23:59:59",
                    "days_valid": 365,
                    "activation_count": 1
                },
                "A23456789BCDEFG": {
                    "status": "valid",
                    "message": "激活码有效，未激活",
                    "expire_date": "2025-12-31T23:59:59",
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
            
            # 查询状态
            if activation_code in status_data:
                response = {
                    "success": True,
                    "data": status_data[activation_code]
                }
            else:
                response = {
                    "success": False,
                    "error": "激活码不存在或无效"
                }
            
            # 发送响应
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            # 错误处理
            error_response = {
                "success": False,
                "error": f"服务器错误: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_OPTIONS(self):
        # 处理CORS预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
