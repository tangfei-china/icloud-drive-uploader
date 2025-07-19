#!/usr/bin/env python3
"""
iCloud Drive 文件夹上传工具

自动化上传整个文件夹结构到 iCloud Drive，支持递归上传、冲突处理和连接恢复。

核心功能：
- 递归上传文件夹和文件
- 智能处理 iCloud API 缓存问题
- 多种冲突处理模式（跳过/覆盖/询问）
- 自动重连策略确保上传成功

使用方法：
    uv run python main.py

配置：
通过 .env 文件配置以下变量：
- APPLE_ID: Apple ID 邮箱
- APPLE_PASSWORD: Apple 密码
- LOCAL_FOLDER_PATH: 本地文件夹路径
- REMOTE_FOLDER_NAME: 远程文件夹名称（可选）
- CONFLICT_MODE: 冲突处理模式（skip/overwrite/ask）

关键技术点：
- 使用重新连接策略解决 iCloud API 文件夹创建后无法立即访问的问题
- 备用上传策略：当文件夹创建失败时，使用扁平化命名上传文件
- 支持中国大陆 iCloud 服务
"""

from pyicloud import PyiCloudService
import os
import mimetypes
import time
from pathlib import Path
from dotenv import load_dotenv


def upload_folder_to_icloud(api, local_folder_path, remote_folder_name=None, conflict_mode='ask'):
    """
    递归上传整个文件夹到iCloud Drive
    
    Args:
        api: PyiCloudService实例
        local_folder_path: 本地文件夹路径
        remote_folder_name: 远程文件夹名称(可选，默认使用本地文件夹名)
        conflict_mode: 文件冲突处理模式 ('ask', 'overwrite', 'skip')
    """
    local_path = Path(local_folder_path)

    if not local_path.exists() or not local_path.is_dir():
        print(f"✗ 错误：本地文件夹 '{local_folder_path}' 不存在或不是文件夹")
        return False

    # 确定远程文件夹名称
    if remote_folder_name is None:
        remote_folder_name = local_path.name

    print(f"\n=== 开始上传文件夹 '{local_path.name}' 到iCloud Drive ===")

    try:
        # 首先检查文件夹是否已存在
        try:
            remote_folder = api.drive[remote_folder_name]
            print(f"⚠ 文件夹 '{remote_folder_name}' 已存在，继续上传内容...")
        except:
            # 文件夹不存在，创建新文件夹
            print(f"正在创建远程文件夹: {remote_folder_name}")
            api.drive.mkdir(remote_folder_name)
            # 创建后重新获取文件夹对象
            remote_folder = api.drive[remote_folder_name]
            print(f"✓ 成功创建文件夹: {remote_folder_name}")

        # 递归上传文件夹内容
        success_count, error_count = _upload_folder_contents(remote_folder, local_path, "", conflict_mode, api)

        print(f"\n📊 上传统计:")
        print(f"  ✓ 成功: {success_count} 个文件")
        print(f"  ✗ 失败: {error_count} 个文件")

        # 如果有成功上传的文件，就认为部分成功
        # 如果所有文件都失败，才认为完全失败
        return success_count > 0

    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⚠ 文件夹 '{remote_folder_name}' 已存在，继续上传内容...")
            try:
                remote_folder = api.drive[remote_folder_name]
                success_count, error_count = _upload_folder_contents(remote_folder, local_path, "", conflict_mode, api)

                print(f"\n📊 上传统计:")
                print(f"  ✓ 成功: {success_count} 个文件")
                print(f"  ✗ 失败: {error_count} 个文件")

                return success_count > 0
            except Exception as e2:
                print(f"✗ 访问已存在文件夹失败: {e2}")
                return False
        else:
            print(f"✗ 创建文件夹失败: {e}")
            return False


def _create_and_access_folder(parent_folder, folder_name, api=None, parent_path=""):
    """
    创建并访问文件夹的增强函数 - 核心技术实现
    
    解决 iCloud API 的关键问题：文件夹创建后由于缓存无法立即访问
    
    策略：
    1. 立即访问：尝试直接访问新创建的文件夹
    2. 重新连接：创建新的 API 连接绕过缓存
    3. 传统重试：等待并重试访问
    
    Args:
        parent_folder: 父文件夹对象
        folder_name: 要创建的文件夹名称
        api: PyiCloudService实例，用于重新连接
        parent_path: 父文件夹路径，用于重新连接后定位
    
    Returns:
        文件夹对象或None（如果所有策略都失败）
    """
    print(f"  创建子文件夹: {folder_name}")
    
    try:
        # 尝试创建文件夹
        parent_folder.mkdir(folder_name)
        print(f"  ✓ 子文件夹创建成功: {folder_name}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  ⚠ 子文件夹 '{folder_name}' 创建时提示已存在")
        else:
            print(f"  ✗ 创建子文件夹失败: {folder_name}, {e}")
            return None
    
    # 立即尝试访问
    try:
        sub_folder = parent_folder[folder_name]
        list(sub_folder.dir())  # 验证
        print(f"  ✓ 文件夹立即访问成功: {folder_name}")
        return sub_folder
    except Exception as e:
        print(f"  ⚠ 立即访问失败: {e}")
    
    # 如果立即访问失败，使用重新连接策略
    if api:
        print(f"  🔄 使用重新连接策略...")
        try:
            # 创建新的 API 连接（获取当前凭据）
            import os
            from dotenv import load_dotenv
            load_dotenv()
            new_api = PyiCloudService(os.getenv('APPLE_ID'), os.getenv('APPLE_PASSWORD'), china_mainland=True)
            
            # 重新导航到父文件夹
            if parent_path:
                # 如果有父路径，按路径导航
                current_folder = new_api.drive
                for path_part in parent_path.split('/'):
                    if path_part:
                        current_folder = current_folder[path_part]
                parent_folder = current_folder
            else:
                # 默认情况下，假设父文件夹是 Desktop
                parent_folder = new_api.drive['Desktop']
            
            # 访问新创建的文件夹
            sub_folder = parent_folder[folder_name]
            list(sub_folder.dir())  # 验证
            print(f"  ✓ 重新连接后访问成功: {folder_name}")
            return sub_folder
            
        except Exception as e:
            print(f"  ✗ 重新连接策略失败: {e}")
    
    # 如果重新连接也失败，尝试传统重试
    print(f"  ⚠ 使用传统重试策略...")
    for retry_count in range(3):
        try:
            wait_time = 3 + retry_count * 2
            print(f"  等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
            
            # 强制刷新父文件夹并访问
            parent_items = list(parent_folder.dir())  # 强制刷新
            sub_folder = parent_folder[folder_name]
            list(sub_folder.dir())  # 验证
            print(f"  ✓ 传统重试成功: {folder_name}")
            return sub_folder
                
        except Exception as e:
            print(f"  ⚠ 传统重试 ({retry_count + 1}/3) 失败: {e}")
    
    print(f"  ✗ 所有策略都失败，无法访问文件夹: {folder_name}")
    return None


def _upload_folder_contents(remote_folder, local_folder_path, relative_path, conflict_mode='ask', api=None):
    """递归上传文件夹内容"""
    success_count = 0
    error_count = 0

    try:
        items = list(local_folder_path.iterdir())
        print(f"正在处理文件夹: {local_folder_path.name} (包含 {len(items)} 个项目)")

        for item in items:
            item_relative_path = os.path.join(relative_path, item.name) if relative_path else item.name

            if item.is_file():
                # 上传文件
                if _upload_single_file(remote_folder, item, item_relative_path, conflict_mode):
                    success_count += 1
                else:
                    error_count += 1

            elif item.is_dir():
                # 创建子文件夹并递归上传
                sub_remote_folder = None
                folder_created = False
                
                # 首先检查文件夹是否已存在
                try:
                    sub_remote_folder = remote_folder[item.name]
                    print(f"  ⚠ 子文件夹 '{item.name}' 已存在，继续上传内容...")
                    
                    # 验证文件夹是否真的可用（通过尝试列出内容）
                    try:
                        list(sub_remote_folder.dir())
                    except:
                        print(f"  ⚠ 文件夹 '{item.name}' 存在但不可访问，将尝试重新创建")
                        sub_remote_folder = None
                        
                except:
                    # 文件夹不存在，尝试创建
                    sub_remote_folder = None
                    
                    # 使用改进的文件夹创建策略
                    sub_remote_folder = _create_and_access_folder(remote_folder, item.name, api)
                    
                    if sub_remote_folder is None:
                        print(f"  ✗ 无法创建或访问子文件夹: {item.name}")
                        # 作为备用策略，尝试直接上传文件到当前文件夹
                        print(f"  🔄 备用策略：将子文件夹内容上传到当前位置")
                        for sub_item in item.iterdir():
                            if sub_item.is_file():
                                backup_relative_path = f"{item.name}_{sub_item.name}"
                                if _upload_single_file(remote_folder, sub_item, backup_relative_path, conflict_mode):
                                    success_count += 1
                                    print(f"  ✓ 备用上传成功: {backup_relative_path}")
                                else:
                                    error_count += 1
                        continue

                # 如果成功获取到子文件夹，递归上传内容
                if sub_remote_folder is not None:
                    try:
                        sub_success, sub_error = _upload_folder_contents(sub_remote_folder, item, item_relative_path, conflict_mode, api)
                        success_count += sub_success
                        error_count += sub_error
                    except Exception as e:
                        print(f"  ✗ 上传子文件夹内容失败: {item.name}, {e}")
                        error_count += 1
                else:
                    print(f"  ✗ 无法访问子文件夹: {item.name}")
                    error_count += 1

        return success_count, error_count

    except Exception as e:
        print(f"✗ 读取本地文件夹失败: {e}")
        return 0, 1


def _upload_single_file(remote_folder, file_path, relative_path, conflict_mode='ask'):
    """上传单个文件"""
    try:
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        print(f"  上传文件: {relative_path} ({file_size_mb:.2f} MB)")

        # 检查文件类型
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if file_size > 100 * 1024 * 1024:  # 100MB限制
            print(f"  ⚠ 文件过大，跳过: {relative_path}")
            return False

        # 检查文件是否已存在
        filename = file_path.name
        file_exists = False
        try:
            existing_file = remote_folder[filename]
            file_exists = True
        except:
            pass  # 文件不存在

        if file_exists:
            if conflict_mode == 'skip':
                print(f"  ⚠ 文件已存在，跳过: {relative_path}")
                return True
            elif conflict_mode == 'overwrite':
                print(f"  🔄 文件已存在，覆盖: {relative_path}")
                # 删除现有文件
                try:
                    existing_file.delete()
                    print(f"  ✓ 已删除现有文件: {relative_path}")
                except Exception as e:
                    print(f"  ✗ 删除现有文件失败: {relative_path}, {e}")
                    return False
            elif conflict_mode == 'ask':
                print(f"  ⚠ 文件已存在: {relative_path}")
                while True:
                    try:
                        action = input(f"    请选择操作 (s=跳过, o=覆盖, sa=全部跳过, oa=全部覆盖): ").strip().lower()
                    except EOFError:
                        print("  使用默认选择：跳过文件")
                        return True
                        
                    if action == 's':
                        print(f"  ⏭ 跳过文件: {relative_path}")
                        return True
                    elif action == 'o':
                        print(f"  🔄 覆盖文件: {relative_path}")
                        try:
                            existing_file.delete()
                            print(f"  ✓ 已删除现有文件: {relative_path}")
                            break
                        except Exception as e:
                            print(f"  ✗ 删除现有文件失败: {relative_path}, {e}")
                            return False
                    elif action == 'sa':
                        print(f"  ⏭ 跳过文件并设置全部跳过模式: {relative_path}")
                        # 注意：这里只能影响当前文件，全局模式需要在上层处理
                        return True
                    elif action == 'oa':
                        print(f"  🔄 覆盖文件并设置全部覆盖模式: {relative_path}")
                        try:
                            existing_file.delete()
                            print(f"  ✓ 已删除现有文件: {relative_path}")
                            # 注意：这里只能影响当前文件，全局模式需要在上层处理
                            break
                        except Exception as e:
                            print(f"  ✗ 删除现有文件失败: {relative_path}, {e}")
                            return False
                    else:
                        print("  ✗ 无效选择，请输入 s, o, sa 或 oa")

        with open(file_path, 'rb') as file_in:
            # 明确指定文件名进行上传
            remote_folder.upload(file_in, filename=filename)

        # 上传完成 (不进行立即验证，因为iCloud Drive API需要同步时间)
        print(f"  ✓ 上传成功: {relative_path}")
        return True

    except Exception as e:
        print(f"  ✗ 上传失败 {relative_path}: {e}")
        return False


def list_local_folder_contents(folder_path):
    """列出本地文件夹内容"""
    path = Path(folder_path)
    if not path.exists():
        print(f"✗ 文件夹不存在: {folder_path}")
        return

    print(f"\n=== 本地文件夹内容: {path.name} ===")
    items = list(path.iterdir())
    print(f"总共 {len(items)} 个项目:")

    for item in items:
        if item.is_file():
            size_mb = item.stat().st_size / (1024 * 1024)
            print(f"  📄 {item.name} ({size_mb:.2f} MB)")
        elif item.is_dir():
            sub_items = list(item.iterdir()) if item.is_dir() else []
            print(f"  📁 {item.name}/ ({len(sub_items)} 项目)")


def main():
    """非交互式主函数 - 自动上传配置的文件夹"""
    print("=== iCloud Drive Uploader (自动模式) ===")
    print("注意：iCloud Drive API可能因账户类型、地区或服务配置而不可用")

    # 加载 .env 文件（如果存在）
    load_dotenv()

    # 获取配置
    apple_id = os.getenv('APPLE_ID')
    apple_password = os.getenv('APPLE_PASSWORD')
    local_folder = os.getenv('LOCAL_FOLDER_PATH')
    remote_name = os.getenv('REMOTE_FOLDER_NAME')
    conflict_mode = os.getenv('CONFLICT_MODE', 'skip')  # 默认跳过已存在文件

    # 验证必需的配置
    if not apple_id or not apple_password:
        print("✗ 错误：请设置 APPLE_ID 和 APPLE_PASSWORD 环境变量")
        print("示例：export APPLE_ID='your_apple_id@example.com'")
        print("     export APPLE_PASSWORD='your_password'")
        exit(1)

    if not local_folder:
        print("✗ 错误：请设置 LOCAL_FOLDER_PATH 环境变量")
        print("示例：export LOCAL_FOLDER_PATH='/path/to/your/folder'")
        exit(1)

    if not Path(local_folder).exists():
        print(f"✗ 错误：本地文件夹不存在: {local_folder}")
        exit(1)

    # 显示配置信息
    print(f"\n配置信息:")
    print(f"  Apple ID: {apple_id}")
    print(f"  本地文件夹: {local_folder}")
    print(f"  远程文件夹名: {remote_name or '使用本地文件夹名'}")
    print(f"  冲突处理模式: {conflict_mode}")

    try:
        # 登录iCloud
        print("\n正在登录iCloud...")
        api = PyiCloudService(apple_id, apple_password, china_mainland=True)

        # 检查两步验证
        if api.requires_2fa:
            print("✗ 错误：需要两步验证，自动模式不支持")
            print("请先手动运行一次建立受信任会话，或使用应用专用密码")
            exit(1)

        print("✓ 登录成功！")

        # 建立受信任会话
        if not api.is_trusted_session:
            print("正在建立受信任会话...")
            try:
                api.trust_session()
                print("✓ 已建立受信任会话")
            except Exception as e:
                print(f"⚠ 建立信任失败: {e}")

        # 测试iCloud Drive访问
        print("\n正在测试iCloud Drive访问...")
        drive = api.drive
        files = list(drive.dir())
        print(f"✓ 成功连接到iCloud Drive (根目录有 {len(files)} 个项目)")

        # 显示本地文件夹内容
        print(f"\n本地文件夹内容预览:")
        list_local_folder_contents(local_folder)

        # 开始上传
        print(f"\n开始自动上传 '{local_folder}' 到iCloud Drive...")
        success = upload_folder_to_icloud(api, local_folder, remote_name, conflict_mode)

        if success:
            print(f"\n🎉 文件夹上传完成！")
            return True
        else:
            print(f"\n❌ 文件夹上传失败")
            return False

    except Exception as e:
        print(f"✗ 操作失败: {e}")
        return False


if __name__ == "__main__":
    main()
