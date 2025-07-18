from pyicloud import PyiCloudService
import os
import mimetypes
from pathlib import Path


def upload_folder_to_icloud(api, local_folder_path, remote_folder_name=None):
    """
    递归上传整个文件夹到iCloud Drive
    
    Args:
        api: PyiCloudService实例
        local_folder_path: 本地文件夹路径
        remote_folder_name: 远程文件夹名称(可选，默认使用本地文件夹名)
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
        # 创建根文件夹
        print(f"正在创建远程文件夹: {remote_folder_name}")
        api.drive.mkdir(remote_folder_name)
        remote_folder = api.drive[remote_folder_name]
        print(f"✓ 成功创建文件夹: {remote_folder_name}")

        # 递归上传文件夹内容
        success_count, error_count = _upload_folder_contents(remote_folder, local_path, "")

        print(f"\n📊 上传统计:")
        print(f"  ✓ 成功: {success_count} 个文件")
        print(f"  ✗ 失败: {error_count} 个文件")

        return success_count > 0 and error_count == 0

    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⚠ 文件夹 '{remote_folder_name}' 已存在，继续上传内容...")
            try:
                remote_folder = api.drive[remote_folder_name]
                success_count, error_count = _upload_folder_contents(remote_folder, local_path, "")

                print(f"\n📊 上传统计:")
                print(f"  ✓ 成功: {success_count} 个文件")
                print(f"  ✗ 失败: {error_count} 个文件")

                return success_count > 0 and error_count == 0
            except Exception as e2:
                print(f"✗ 访问已存在文件夹失败: {e2}")
                return False
        else:
            print(f"✗ 创建文件夹失败: {e}")
            return False


def _upload_folder_contents(remote_folder, local_folder_path, relative_path):
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
                if _upload_single_file(remote_folder, item, item_relative_path):
                    success_count += 1
                else:
                    error_count += 1

            elif item.is_dir():
                # 创建子文件夹并递归上传
                try:
                    print(f"  创建子文件夹: {item.name}")
                    remote_folder.mkdir(item.name)
                    sub_remote_folder = remote_folder[item.name]
                    print(f"  ✓ 子文件夹创建成功: {item.name}")

                    # 递归上传子文件夹内容
                    sub_success, sub_error = _upload_folder_contents(sub_remote_folder, item, item_relative_path)
                    success_count += sub_success
                    error_count += sub_error

                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"  ⚠ 子文件夹 '{item.name}' 已存在，继续上传内容...")
                        try:
                            sub_remote_folder = remote_folder[item.name]
                            sub_success, sub_error = _upload_folder_contents(sub_remote_folder, item,
                                                                             item_relative_path)
                            success_count += sub_success
                            error_count += sub_error
                        except Exception as e2:
                            print(f"  ✗ 访问已存在子文件夹失败: {e2}")
                            error_count += 1
                    else:
                        print(f"  ✗ 创建子文件夹失败: {e}")
                        error_count += 1

        return success_count, error_count

    except Exception as e:
        print(f"✗ 读取本地文件夹失败: {e}")
        return 0, 1


def _upload_single_file(remote_folder, file_path, relative_path):
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

        with open(file_path, 'rb') as file_in:
            remote_folder.upload(file_in)

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


print("=== iCloud Drive Uploader ===")
print("注意：iCloud Drive API可能因账户类型、地区或服务配置而不可用")

# 从环境变量获取凭据，如果为空则提示输入
print("\n正在获取登录凭据...")

# 尝试从环境变量获取凭据
apple_id = os.getenv('APPLE_ID')
apple_password = os.getenv('APPLE_PASSWORD')

# 如果环境变量为空，提示用户输入
if not apple_id:
    apple_id = input("请输入Apple ID: ").strip()
    if not apple_id:
        print("✗ Apple ID不能为空")
        exit(1)

if not apple_password:
    import getpass
    apple_password = getpass.getpass("请输入Apple密码: ").strip()
    if not apple_password:
        print("✗ 密码不能为空")
        exit(1)

print("正在登录iCloud...")
api = PyiCloudService(apple_id, apple_password, china_mainland=True)

# 检查是否需要进行两步验证
if api.requires_2fa:
    print("需要进行两步验证。")
    code = input("请输入验证码: ")
    result = api.validate_2fa_code(code)
    print("验证结果: ", result)

    if not result:
        print("验证失败。")
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
print(f"\n当前会话状态: {'受信任' if api.is_trusted_session else '不受信任'}")

print("\n正在测试iCloud Drive访问...")
try:
    drive = api.drive
    files = list(drive.dir())
    print(f"✓ 成功！iCloud Drive根目录有 {len(files)} 个项目:")

    for item in files:
        if hasattr(item, 'name'):
            item_type = "📁" if hasattr(item, 'type') and item.type == 'FOLDER' else "📄"
            print(f"  {item_type} {item.name}")
        else:
            print(f"  📄 {item}")  # 如果没有name属性，直接打印对象

    print(f"\n程序运行成功！已连接到iCloud Drive。")

    # 提供文件夹上传功能
    print("\n" + "=" * 50)
    print("📁 文件夹上传功能")
    print("=" * 50)

    while True:
        print("\n请选择操作:")
        print("1. 上传本地文件夹到iCloud Drive")
        print("2. 查看本地文件夹内容")
        print("3. 查看iCloud Drive当前内容")
        print("4. 退出")

        choice = input("\n请输入选择 (1-4): ").strip()

        if choice == '1':
            # 上传文件夹
            local_folder = input("请输入本地文件夹路径: ").strip()
            if not local_folder:
                print("✗ 请输入有效的文件夹路径")
                continue

            remote_name = input("请输入远程文件夹名称 (留空使用本地文件夹名): ").strip()
            remote_name = remote_name if remote_name else None

            print(f"\n开始上传 '{local_folder}' 到iCloud Drive...")
            success = upload_folder_to_icloud(api, local_folder, remote_name)

            if success:
                print(f"\n🎉 文件夹上传完成！")
            else:
                print(f"\n❌ 文件夹上传失败")

        elif choice == '2':
            # 查看本地文件夹内容
            local_folder = input("请输入本地文件夹路径: ").strip()
            if local_folder:
                list_local_folder_contents(local_folder)
            else:
                print("✗ 请输入有效的文件夹路径")

        elif choice == '3':
            # 查看iCloud Drive内容
            print("\n刷新iCloud Drive内容...")
            try:
                files = list(api.drive.dir())
                print(f"\niCloud Drive根目录当前有 {len(files)} 个项目:")
                for item in files:
                    if hasattr(item, 'name'):
                        item_type = "📁" if hasattr(item, 'type') and item.type == 'FOLDER' else "📄"
                        print(f"  {item_type} {item.name}")
                    else:
                        print(f"  📄 {item}")
            except Exception as e:
                print(f"✗ 获取iCloud Drive内容失败: {e}")

        elif choice == '4':
            print("👋 再见！")
            break

        else:
            print("✗ 无效选择，请输入 1-4")

except Exception as e:
    print(f"✗ iCloud Drive不可用: {e}")
    print("\n可能的解决方案:")
    print("1. 确保在 设置 > Apple ID > iCloud 中启用了 iCloud Drive")
    print("2. 确保你的Apple账户支持iCloud Drive API访问")
    print("3. 尝试在不同地区的网络环境下运行")
    print("4. 检查Apple开发者账户是否有API访问权限")

    # 显示可用的其他服务
    print(f"\n其他可用的iCloud服务:")
    available_services = []

    services_to_test = [
        ('photos', '照片库'),
        ('contacts', '通讯录'),
        ('calendar', '日历'),
        ('reminders', '提醒事项')
    ]

    for service_name, service_desc in services_to_test:
        try:
            service = getattr(api, service_name)
            # 简单测试服务是否可用
            if service_name == 'photos':
                albums = service.albums
                available_services.append(f"✓ {service_desc}")
            elif service_name == 'contacts':
                contacts = service.all()
                available_services.append(f"✓ {service_desc}")
            else:
                available_services.append(f"✓ {service_desc}")
        except Exception:
            available_services.append(f"✗ {service_desc}")

    for service in available_services:
        print(f"  {service}")
