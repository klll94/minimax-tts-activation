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
            
            # 测试激活码列表
            valid_codes = [
                "23456789ABCDEFG",
                "A23456789BCDEFG", 
                "B23456789CDEFGH",
                "35X3M278XQNFLEQ"
            ]
            
            # 验证激活码
            if len(activation_code) == 15 and activation_code in valid_codes:
                response = {
                    "success": True,
                    "valid": True,
                    "data": {
                        "activation_id": f"test-{activation_code[-4:]}",
                        "expire_date": "2025-12-31T23:59:59",
                        "days_valid": 365,
                        "version": "3.0"
                    },
                    "message": "激活码验证成功"
                }
            else:
                response = {
                    "success": True,
                    "valid": False,
                    "error": "激活码无效或已过期",
                    "message": "激活码验证失败"
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
