#!/usr/bin/env python3
"""
测试脚本 - 验证文件夹上传功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import upload_folder_to_icloud, list_local_folder_contents
from pyicloud import PyiCloudService
from dotenv import load_dotenv

def test_upload():
    print("=== 上传功能测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取凭据
    apple_id = os.getenv('APPLE_ID')
    apple_password = os.getenv('APPLE_PASSWORD')
    
    if not apple_id or not apple_password:
        print("✗ 请先设置 APPLE_ID 和 APPLE_PASSWORD 环境变量")
        return False
    
    try:
        # 连接 iCloud
        print("正在连接iCloud...")
        api = PyiCloudService(apple_id, apple_password, china_mainland=True)
        
        if api.requires_2fa:
            print("需要两步验证，测试跳过")
            return False
            
        print("✓ 成功连接到iCloud")
        
        # 从环境变量获取测试路径
        local_folder = os.getenv('LOCAL_FOLDER_PATH')
        remote_name = os.getenv('REMOTE_FOLDER_NAME')
        
        if not local_folder:
            print("✗ 环境变量 LOCAL_FOLDER_PATH 未设置")
            return False
            
        if not Path(local_folder).exists():
            print(f"✗ 本地文件夹不存在: {local_folder}")
            return False
            
        print(f"测试配置:")
        print(f"  本地文件夹: {local_folder}")
        print(f"  远程文件夹名: {remote_name}")
            
        # 显示本地文件夹内容
        print("\n本地文件夹内容:")
        list_local_folder_contents(local_folder)
        
        # 测试上传 (使用跳过模式避免交互)
        print(f"\n开始测试上传...")
        success = upload_folder_to_icloud(api, local_folder, remote_name, conflict_mode='skip')
        
        if success:
            print("\n🎉 上传测试成功!")
            return True
        else:
            print("\n❌ 上传测试失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_upload()