#!/usr/bin/env python3
"""
iCloud Drive API 调试工具

用于测试和验证 pyicloud 库的功能：
- 连接测试
- 文件夹访问
- 文件上传测试
- API 响应验证

使用方法：
    uv run python debug_api.py

需要配置 .env 文件中的 APPLE_ID 和 APPLE_PASSWORD
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyicloud import PyiCloudService
from dotenv import load_dotenv

def debug_api():
    print("=== pyiCloud API 调试 ===")
    
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
            print("需要两步验证，调试跳过")
            return False
            
        print("✓ 成功连接到iCloud")
        
        # 检查Desktop文件夹
        print("\n检查已创建的文件夹...")
        try:
            test_folder = api.drive['Desktop']
            print(f"✓ 找到文件夹: Desktop")
            
            # 查看文件夹内容
            print("文件夹内容:")
            items = list(test_folder.dir())
            for item in items:
                print(f"  - {item.name if hasattr(item, 'name') else item}")
                
                # 如果是文件夹，尝试查看子内容
                if hasattr(item, 'type') and item.type == 'FOLDER':
                    try:
                        sub_items = list(item.dir())
                        print(f"    └─ {len(sub_items)} 个子项目:")
                        for sub_item in sub_items:
                            print(f"      - {sub_item.name if hasattr(sub_item, 'name') else sub_item}")
                    except Exception as e:
                        print(f"    └─ 无法访问子内容: {e}")
                elif hasattr(item, 'name') and item.name in ['Rules', 'Workflows']:
                    try:
                        # 尝试访问这些文件夹
                        sub_folder = test_folder[item.name]
                        sub_items = list(sub_folder.dir())
                        print(f"    └─ {len(sub_items)} 个子项目:")
                        for sub_item in sub_items:
                            print(f"      - {sub_item.name if hasattr(sub_item, 'name') else sub_item}")
                    except Exception as e:
                        print(f"    └─ 无法访问子内容: {e}")
                
            # 测试直接在文件夹中创建文件
            print("\n测试创建子文件夹...")
            try:
                test_folder.mkdir('debug_subfolder')
                print("✓ 子文件夹创建成功")
                
                # 验证创建
                sub_folder = test_folder['debug_subfolder']
                print("✓ 子文件夹访问成功")
                
            except Exception as e:
                print(f"✗ 子文件夹创建失败: {e}")
                
            # 测试文件上传
            print("\n测试文件上传...")
            test_file_path = "/tmp/debug_test.txt"
            with open(test_file_path, 'w') as f:
                f.write("Debug test content")
                
            try:
                with open(test_file_path, 'rb') as f:
                    test_folder.upload(f, filename='debug_test.txt')
                print("✓ 文件上传成功")
                
                # 验证文件
                uploaded_file = test_folder['debug_test.txt']
                print("✓ 文件验证成功")
                
            except Exception as e:
                print(f"✗ 文件上传失败: {e}")
                
            # 清理
            os.remove(test_file_path)
                
        except Exception as e:
            print(f"✗ 访问文件夹失败: {e}")
            
    except Exception as e:
        print(f"✗ 调试失败: {e}")
        return False

if __name__ == "__main__":
    debug_api()