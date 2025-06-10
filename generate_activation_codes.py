#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax TTS 激活码生成工具 v3.0
用于生成15位短激活码
"""

import sys
import json
from license_manager import LicenseManager

def main():
    """主函数"""
    print("🔐 MiniMax TTS 激活码生成工具 v3.0")
    print("=" * 50)
    
    license_manager = LicenseManager()
    
    while True:
        print("\n请选择操作:")
        print("1. 生成激活码")
        print("2. 验证激活码") 
        print("3. 查询激活码状态")
        print("4. 查看激活记录")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            generate_code(license_manager)
        elif choice == "2":
            verify_code(license_manager)
        elif choice == "3":
            check_status(license_manager)
        elif choice == "4":
            show_activation_log(license_manager)
        elif choice == "5":
            print("再见!")
            break
        else:
            print("❌ 无效选择，请重新输入")

def generate_code(license_manager):
    """生成激活码"""
    print("\n📝 生成新的激活码")
    print("-" * 30)
    
    try:
        # 获取用户输入
        user_id = input("用户ID (默认: default): ").strip() or "default"
        
        # 有效期选择
        print("\n有效期选项:")
        print("1. 1天")
        print("2. 7天")  
        print("3. 1个月 (30天)")
        print("4. 半年 (180天)")
        print("5. 1年 (365天)")
        print("6. 永久 (100年)")
        
        period_choice = input("请选择有效期 (1-6, 默认: 5): ").strip() or "5"
        period_map = {
            "1": 1,
            "2": 7,
            "3": 30,
            "4": 180,
            "5": 365,
            "6": 36500
        }
        days_valid = period_map.get(period_choice, 365)
        
        # 生成激活码
        activation_code, activation_id = license_manager.generate_activation_code(
            days_valid=days_valid,
            user_id=user_id
        )
        
        # 获取有效期描述
        period_desc = {
            1: "1天",
            7: "7天", 
            30: "1个月",
            180: "半年",
            365: "1年",
            36500: "永久"
        }.get(days_valid, f"{days_valid}天")
        
        print(f"\n✅ 激活码生成成功!")
        print("=" * 50)
        print(f"🆔 激活码ID: {activation_id}")
        print(f"👤 用户ID: {user_id}")
        print(f"📅 有效期: {period_desc}")
        print(f"🔒 设备绑定: 单设备绑定")
        print(f"📋 版本: 全功能版")
        print(f"\n🔑 激活码 (15位):")
        print(f"{activation_code}")
        print("=" * 50)
        
        # 保存到文件
        save_choice = input("\n是否保存激活码到文件? (y/N): ").strip().lower()
        if save_choice == 'y':
            filename = f"activation_code_{activation_id[:8]}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"MiniMax TTS 激活码 v3.0\n")
                f.write(f"===================\n")
                f.write(f"激活码ID: {activation_id}\n")
                f.write(f"用户ID: {user_id}\n")
                f.write(f"有效期: {period_desc}\n")
                f.write(f"设备绑定: 单设备绑定\n")
                f.write(f"版本: 全功能版\n")
                f.write(f"\n激活码 (15位):\n{activation_code}\n")
            print(f"✅ 已保存到文件: {filename}")
        
    except Exception as e:
        print(f"❌ 生成激活码失败: {e}")

def verify_code(license_manager):
    """验证激活码"""
    print("\n🔍 验证激活码")
    print("-" * 30)
    
    activation_code = input("请输入激活码 (15位): ").strip()
    if not activation_code:
        print("❌ 激活码不能为空")
        return
    
    if len(activation_code) != 15:
        print("❌ 激活码必须是15位")
        return
    
    try:
        is_valid, result = license_manager.validate_activation_code(activation_code, check_device_binding=False)
        
        if is_valid:
            print(f"\n✅ 激活码有效!")
            print("=" * 30)
            print(f"🆔 激活码ID: {result.get('activation_id', 'N/A')}")
            print(f"📅 过期时间: {result.get('expire_date', 'N/A')}")
            print(f"⏰ 有效天数: {result.get('days_valid', 'N/A')} 天")
            print(f"📝 版本: {result.get('version', 'N/A')}")
            print("=" * 30)
        else:
            print(f"\n❌ 激活码无效: {result}")
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")

def check_status(license_manager):
    """查询激活码状态"""
    print("\n🔍 查询激活码状态")
    print("-" * 30)
    
    activation_code = input("请输入激活码 (15位): ").strip()
    if not activation_code:
        print("❌ 激活码不能为空")
        return
    
    if len(activation_code) != 15:
        print("❌ 激活码必须是15位")
        return
    
    try:
        success, result = license_manager.check_activation_status(activation_code)
        
        if success:
            print(f"\n📊 激活码状态信息:")
            print("=" * 30)
            print(f"🔄 状态: {result['message']}")
            print(f"📅 过期时间: {result['expire_date']}")
            print(f"⏰ 有效天数: {result['days_valid']} 天")
            print(f"🔢 激活次数: {result['activation_count']}")
            
            if result['status'] == 'activated' and result.get('device_info'):
                device_info = result['device_info']
                print(f"\n💻 激活设备信息:")
                print(f"   设备指纹: {device_info['device_fingerprint']}")
                print(f"   首次激活: {device_info['first_activation'][:19]}")
                print(f"   最后激活: {device_info['last_activation'][:19]}")
            
            print("=" * 30)
        else:
            print(f"\n❌ 查询失败: {result}")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")

def show_activation_log(license_manager):
    """显示激活记录"""
    print("\n📊 激活记录")
    print("-" * 30)
    
    try:
        import os
        if not os.path.exists(license_manager.activation_log_file):
            print("📝 暂无激活记录")
            return
        
        with open(license_manager.activation_log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        if not log_data:
            print("📝 暂无激活记录")
            return
        
        print(f"共找到 {len(log_data)} 个激活记录:\n")
        
        for activation_id, info in log_data.items():
            print(f"🆔 激活码ID: {activation_id[:8]}...")
            print(f"📅 首次激活: {info.get('first_activation', 'N/A')[:19]}")
            print(f"🔢 激活次数: {info.get('count', 0)}")
            
            devices = info.get('devices', [])
            if devices:
                print(f"💻 激活设备:")
                for i, device in enumerate(devices, 1):
                    if isinstance(device, dict):
                        device_fp = device.get('device_fingerprint', 'N/A')
                        last_activation = device.get('last_activation', 'N/A')
                        print(f"   {i}. 设备: {device_fp[:8]}... (最后激活: {last_activation[:10]})")
            
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ 读取激活记录失败: {e}")

if __name__ == "__main__":
    main() 