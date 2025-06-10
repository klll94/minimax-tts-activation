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
            
            # 验证激活码
            if self.validate_code(activation_code):
                response = {
                    "success": True,
                    "valid": True,
                    "data": {
                        "activation_id": f"test-{activation_code[-4:]}",
                        "expire_date": "2025-12-31T23:59:59",
                        "days_valid": 365,
                        "version": "3.0",
                        "status": "valid"
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
    
    def validate_code(self, code):
        """验证激活码"""
        if len(code) != 15:
            return False
        
        # 检查字符集
        allowed_chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        for char in code:
            if char not in allowed_chars:
                return False
        
        # 测试激活码列表
        test_codes = [
            "23456789ABCDEFG",
            "A23456789BCDEFG", 
            "B23456789CDEFGH",
            "C23456789DEFGHI",
            "35X3M278XQNFLEQ"
        ]
        
        return code in test_codes
