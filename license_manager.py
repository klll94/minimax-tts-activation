import hashlib
import hmac
import base64
import datetime
import json
import os
import uuid
import platform
import struct
import time
from cryptography.fernet import Fernet

class LicenseManager:
    def __init__(self):
        # 使用与secure_standalone_generator.py相同的密钥种子
        self.secret_key = b"TTS_AUDIO_GENERATOR_2024_SECURE_KEY_SEED"
        
        # 统一存储位置 - 使用用户目录，避免不同文件夹重复激活
        user_home = os.path.expanduser("~")
        app_data_dir = os.path.join(user_home, ".minimax_tts")
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir, exist_ok=True)
        
        self.license_file = os.path.join(app_data_dir, "license.dat")
        self.activation_log_file = os.path.join(app_data_dir, "activation_log.json")
        
        # 有效期预设选项（天数）
        self.validity_periods = {
            1: 1,        # 1天
            2: 7,        # 7天  
            3: 30,       # 1月
            4: 180,      # 半年
            5: 365,      # 1年
            6: 36500     # 永久（100年）
        }
        
    def _generate_key(self):
        """从固定种子生成Fernet密钥"""
        key_hash = hashlib.sha256(self.secret_key).digest()
        return base64.urlsafe_b64encode(key_hash)
    
    def _get_device_fingerprint(self):
        """生成设备指纹"""
        # 获取设备信息
        machine_id = platform.machine()
        processor = platform.processor()
        system = platform.system()
        node = platform.node()
        
        # 尝试获取更多硬件信息
        try:
            import psutil
            # 获取CPU信息
            cpu_count = str(psutil.cpu_count())
            # 获取内存信息
            memory = str(psutil.virtual_memory().total)
        except ImportError:
            cpu_count = "unknown"
            memory = "unknown"
        
        # 组合设备信息
        device_info = f"{machine_id}_{processor}_{system}_{node}_{cpu_count}_{memory}"
        
        # 生成设备指纹
        device_hash = hashlib.sha256(device_info.encode()).hexdigest()
        return device_hash[:16]  # 取前16位作为设备指纹
    
    def _generate_short_code(self, days_valid, activation_id):
        """生成15位短激活码"""
        # 使用时间戳的后3字节（足够唯一性）
        timestamp = int(time.time()) & 0xFFFFFF  # 取低24位
        
        # 将有效天数编码为期限类型
        period_type = 0
        for key, value in self.validity_periods.items():
            if value == days_valid:
                period_type = key
                break
        
        # 使用UUID的部分内容作为唯一标识（4字节）
        uuid_bytes = uuid.UUID(activation_id).bytes[:4]
        
        # 组合数据：时间戳(3字节) + 期限类型(1字节) + UUID(4字节) = 8字节
        raw_data = struct.pack('>I', timestamp)[1:] + struct.pack('B', period_type) + uuid_bytes
        
        # 生成校验码（1字节）
        checksum = hashlib.md5(raw_data + self.secret_key).digest()[:1]
        
        # 组合完整数据：原始数据(8字节) + 校验码(1字节) = 9字节
        full_data = raw_data + checksum
        
        # 使用Base32编码，但只用数字和大写字母（避免混淆）
        # 自定义字符集：去掉容易混淆的字符
        chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # 32个字符，去掉0,1,I,O
        
        # 将9字节转为整数
        data_int = int.from_bytes(full_data, byteorder='big')
        
        # Base32编码
        result = ""
        while data_int > 0:
            result = chars[data_int % 32] + result
            data_int //= 32
        
        # 确保正好15位
        if len(result) > 15:
            result = result[-15:]  # 取后15位
        else:
            result = result.zfill(15)  # 补齐到15位
        
        return result
    
    def _parse_short_code(self, activation_code):
        """解析15位短激活码"""
        try:
            if len(activation_code) != 15:
                return None, "激活码必须是15位"
            
            # Base32解码（自定义字符集）
            chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
            data_int = 0
            for char in activation_code:
                if char not in chars:
                    return None, "激活码包含无效字符"
                data_int = data_int * 32 + chars.index(char)
            
            # 转换为字节（9字节）
            try:
                full_data = data_int.to_bytes(9, byteorder='big')
            except OverflowError:
                return None, "激活码格式错误"
            
            # 分离数据和校验码
            raw_data = full_data[:8]
            checksum = full_data[8:9]
            
            # 验证校验码
            expected_checksum = hashlib.md5(raw_data + self.secret_key).digest()[:1]
            if checksum != expected_checksum:
                return None, "激活码无效"
            
            # 解析数据
            # 时间戳(3字节) + 期限类型(1字节) + UUID(4字节)
            timestamp_bytes = b'\x00' + raw_data[:3]  # 补齐为4字节
            timestamp = struct.unpack('>I', timestamp_bytes)[0]
            period_type = struct.unpack('B', raw_data[3:4])[0]
            uuid_bytes = raw_data[4:8]
            
            # 构造完整UUID（用0填充剩余字节）
            full_uuid_bytes = uuid_bytes + b'\x00' * 12
            activation_id = str(uuid.UUID(bytes=full_uuid_bytes))
            
            # 获取有效天数
            days_valid = self.validity_periods.get(period_type, 365)
            
            # 计算过期时间（由于时间戳只有3字节，需要推算完整时间戳）
            current_time = int(time.time())
            # 找到最接近的完整时间戳
            full_timestamp = (current_time & 0xFF000000) | timestamp
            if full_timestamp > current_time + 86400:  # 如果超过当前时间1天，说明是上个周期
                full_timestamp -= 0x1000000
            
            generated_date = datetime.datetime.fromtimestamp(full_timestamp)
            expire_date = generated_date + datetime.timedelta(days=days_valid)
            
            return {
                "activation_id": activation_id,
                "generated_date": generated_date.isoformat(),
                "expire_date": expire_date.isoformat(),
                "days_valid": days_valid,
                "version": "3.0"
            }, None
            
        except Exception as e:
            return None, f"激活码解析失败: {str(e)}"

    def generate_activation_code(self, days_valid=365, user_id="default"):
        """
        生成15位短激活码（简化版本）
        
        Args:
            days_valid: 有效天数（1,7,30,180,365,36500）
            user_id: 用户ID（仅用于记录）
        """
        # 验证有效期是否在预设范围内
        if days_valid not in self.validity_periods.values():
            raise ValueError(f"有效期必须是以下值之一: {list(self.validity_periods.values())}")
        
        # 生成唯一的激活码ID
        activation_id = str(uuid.uuid4())
        
        # 生成15位短激活码
        activation_code = self._generate_short_code(days_valid, activation_id)
        
        return activation_code, activation_id

    def validate_activation_code(self, activation_code, check_device_binding=True):
        """验证15位短激活码"""
        try:
            # 解析激活码
            license_data, error = self._parse_short_code(activation_code)
            if error:
                return False, error
            
            # 检查过期时间
            expire_date = datetime.datetime.fromisoformat(license_data["expire_date"])
            if datetime.datetime.now() > expire_date:
                return False, "激活码已过期"
            
            # 检查设备绑定（单设备激活限制）
            if check_device_binding:
                activation_id = license_data.get("activation_id")
                device_fp = self._get_device_fingerprint()
                
                # 检查是否当前设备已经激活过
                if self._is_device_activated(activation_id, device_fp):
                    # 当前设备已激活过，允许继续使用
                    return True, license_data
                
                # 检查是否有其他设备激活过
                activation_count = self._get_activation_count(activation_id)
                if activation_count > 0:
                    # 激活码已在其他设备上使用，拒绝激活
                    return False, "激活码已在其他设备上激活，每个激活码只能在一台设备上使用"
            
            return True, license_data
            
        except Exception as e:
            return False, f"激活码验证失败: {str(e)}"

    def check_activation_status(self, activation_code):
        """检查激活码是否已被激活使用"""
        try:
            # 解析激活码获取ID
            license_data, error = self._parse_short_code(activation_code)
            if error:
                return False, error
            
            activation_id = license_data.get("activation_id")
            activation_count = self._get_activation_count(activation_id)
            
            if activation_count == 0:
                return True, {
                    "status": "unused",
                    "message": "激活码未使用",
                    "activation_count": 0,
                    "expire_date": license_data.get("expire_date"),
                    "days_valid": license_data.get("days_valid")
                }
            else:
                # 获取激活设备信息
                device_info = self._get_activation_device_info(activation_id)
                return True, {
                    "status": "activated",
                    "message": "激活码已被使用",
                    "activation_count": activation_count,
                    "expire_date": license_data.get("expire_date"),
                    "days_valid": license_data.get("days_valid"),
                    "device_info": device_info
                }
                
        except Exception as e:
            return False, f"查询激活状态失败: {str(e)}"
    
    def _get_activation_device_info(self, activation_id):
        """获取激活设备信息"""
        if not os.path.exists(self.activation_log_file):
            return None
        
        try:
            with open(self.activation_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            activation_record = log_data.get(activation_id, {})
            devices = activation_record.get("devices", [])
            
            if devices and len(devices) > 0:
                device = devices[0]  # 只取第一个设备（单设备绑定）
                return {
                    "device_fingerprint": device.get("device_fingerprint", "unknown")[:8] + "...",
                    "first_activation": device.get("first_activation", "unknown"),
                    "last_activation": device.get("last_activation", "unknown")
                }
            
            return None
        except:
            return None
    
    def _is_device_activated(self, activation_id, device_fp):
        """检查当前设备是否已经激活过"""
        if not os.path.exists(self.activation_log_file):
            return False
        
        try:
            with open(self.activation_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            activation_record = log_data.get(activation_id, {})
            devices = activation_record.get("devices", [])
            
            for device_record in devices:
                if isinstance(device_record, dict) and device_record.get("device_fingerprint") == device_fp:
                    return True
            
            return False
        except:
            return False
    
    def _get_activation_count(self, activation_id):
        """获取激活码的使用次数"""
        if not os.path.exists(self.activation_log_file):
            return 0
        
        try:
            with open(self.activation_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            return log_data.get(activation_id, {}).get("count", 0)
        except:
            return 0
    
    def _record_activation(self, activation_id, license_data):
        """记录激活使用"""
        device_fp = self._get_device_fingerprint()
        
        # 读取现有日志
        log_data = {}
        if os.path.exists(self.activation_log_file):
            try:
                with open(self.activation_log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except:
                log_data = {}
        
        # 确保log_data是字典类型
        if not isinstance(log_data, dict):
            log_data = {}
        
        # 更新激活记录
        if activation_id not in log_data:
            log_data[activation_id] = {
                "count": 0,
                "devices": [],
                "first_activation": datetime.datetime.now().isoformat()
            }
        
        # 确保devices字段是列表
        if not isinstance(log_data[activation_id].get("devices"), list):
            log_data[activation_id]["devices"] = []
        
        # 检查设备是否已记录
        device_recorded = False
        for device_record in log_data[activation_id]["devices"]:
            if isinstance(device_record, dict) and device_record.get("device_fingerprint") == device_fp:
                device_recorded = True
                device_record["last_activation"] = datetime.datetime.now().isoformat()
                break
        
        # 只有新设备才增加激活计数
        if not device_recorded:
            log_data[activation_id]["count"] += 1
            log_data[activation_id]["devices"].append({
                "device_fingerprint": device_fp,
                "first_activation": datetime.datetime.now().isoformat(),
                "last_activation": datetime.datetime.now().isoformat()
            })
        
        # 保存日志
        try:
            with open(self.activation_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # 如果保存失败，至少不影响激活流程
            print(f"保存激活日志失败: {e}")
    
    def save_license(self, activation_code):
        """保存激活码到本地文件"""
        try:
            # 不再重新验证，因为调用此方法前已经验证过了
            # 直接解析激活码以获取license_data
            license_data, error = self._parse_short_code(activation_code)
            if error:
                print(f"保存许可证失败: {error}")
                return False
            
            # 记录激活使用
            activation_id = license_data.get("activation_id")
            if activation_id:
                self._record_activation(activation_id, license_data)
            
            # 将激活码加密保存到本地
            fernet = Fernet(self._generate_key())
            encrypted_code = fernet.encrypt(activation_code.encode())
            
            # 确保目录存在
            license_dir = os.path.dirname(self.license_file)
            if not os.path.exists(license_dir):
                os.makedirs(license_dir, exist_ok=True)
            
            with open(self.license_file, 'wb') as f:
                f.write(encrypted_code)
            
            print(f"✅ 许可证已保存到: {self.license_file}")
            return True
            
        except Exception as e:
            print(f"❌ 保存许可证失败: {e}")
            return False
    
    def load_local_license(self):
        """从本地文件加载并验证许可证"""
        if not os.path.exists(self.license_file):
            return False, "未找到许可证文件"
        
        try:
            with open(self.license_file, 'rb') as f:
                encrypted_code = f.read()
            
            fernet = Fernet(self._generate_key())
            activation_code = fernet.decrypt(encrypted_code).decode()
            
            # 加载时不检查设备绑定，因为本地保存的就是当前设备激活的
            return self.validate_activation_code(activation_code, check_device_binding=False)
            
        except Exception as e:
            return False, f"许可证文件损坏: {str(e)}"
    
    def get_license_info(self):
        """获取许可证信息"""
        valid, license_data = self.load_local_license()
        if valid:
            expire_date = datetime.datetime.fromisoformat(license_data["expire_date"])
            days_remaining = (expire_date - datetime.datetime.now()).days
            return {
                "valid": True,
                "user_id": license_data.get("user_id", "unknown"),
                "expire_date": expire_date.strftime("%Y-%m-%d"),
                "days_remaining": max(0, days_remaining),
                "version": license_data.get("version", "3.0"),
                "activation_id": license_data.get("activation_id", "unknown")
            }
        else:
            return {"valid": False, "message": license_data}

# 生成一些测试激活码的工具函数
def generate_test_codes():
    """生成测试用的激活码"""
    manager = LicenseManager()
    
    # 生成不同有效期的激活码
    codes = {}
    
    code1, id1 = manager.generate_activation_code(30, "trial_user")
    codes["30天试用版"] = code1
    
    code2, id2 = manager.generate_activation_code(365, "standard_user")
    codes["1年正式版"] = code2
    
    code3, id3 = manager.generate_activation_code(36500, "premium_user")
    codes["永久版"] = code3
    
    return codes

if __name__ == "__main__":
    # 测试功能
    manager = LicenseManager()
    
    # 生成测试激活码
    test_codes = generate_test_codes()
    print("=== 测试激活码 ===")
    for name, code in test_codes.items():
        print(f"{name}: {code}")
        print(f"验证结果: {manager.validate_activation_code(code)}")
        print("-" * 50) 