# iCloud Drive Uploader

A robust Python automation tool for recursively uploading local folders to iCloud Drive with advanced API synchronization handling and intelligent retry mechanisms.

## ✨ Key Features

- **🔄 Non-Interactive Automation** - Fully automated uploads with pre-configured settings
- **📁 Recursive Folder Upload** - Complete folder structure preservation including nested folders
- **🛠️ Advanced API Handling** - Intelligent reconnection strategy to solve iCloud API caching issues
- **⚡ Smart Retry Logic** - Multiple fallback strategies ensure maximum upload success rate
- **🔐 Secure Authentication** - Environment variable configuration with .env file support
- **📊 Detailed Progress Tracking** - Real-time upload status with comprehensive statistics
- **🌏 China Mainland Support** - Optimized for China iCloud infrastructure
- **⚖️ Conflict Resolution** - Multiple modes: skip, overwrite, or ask for each file

## System Requirements

- Python 3.11+
- uv package manager
- Valid Apple ID with iCloud Drive access

## Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configuration Setup

**Create .env file** (Recommended for automatic uploads)
```bash
# Create .env file in project root
touch .env
```

**Edit .env file with your configuration:**
```env
# Apple ID credentials
APPLE_ID=your_apple_id@example.com
APPLE_PASSWORD=your_password

# Upload configuration
LOCAL_FOLDER_PATH=/path/to/your/local/folder
REMOTE_FOLDER_NAME=DestinationFolder
CONFLICT_MODE=overwrite
```

**Alternative: Environment Variables**
```bash
# macOS/Linux
export APPLE_ID="your_apple_id@example.com"
export APPLE_PASSWORD="your_password"
export LOCAL_FOLDER_PATH="/path/to/your/folder"
export REMOTE_FOLDER_NAME="DestinationFolder"
export CONFLICT_MODE="overwrite"

# Windows
set APPLE_ID=your_apple_id@example.com
set APPLE_PASSWORD=your_password
set LOCAL_FOLDER_PATH=C:\path\to\your\folder
set REMOTE_FOLDER_NAME=DestinationFolder
set CONFLICT_MODE=overwrite
```

### 3. Run the Program
```bash
uv run python main.py
```

## Usage Guide

### Automated Upload Mode

Once configured, the program runs automatically:

```bash
uv run python main.py
```

**Output Example:**
```
=== iCloud Drive Uploader (自动模式) ===

配置信息:
  Apple ID: your_apple_id@example.com
  本地文件夹: /Users/username/Documents/MyProject
  远程文件夹名: ProjectBackup
  冲突处理模式: overwrite

正在登录iCloud...
✓ 登录成功！

=== 开始上传文件夹 'MyProject' 到iCloud Drive ===

正在处理文件夹: MyProject (包含 15 个项目)
  创建子文件夹: src
  ✓ 文件夹立即访问成功: src
  上传文件: src/main.py (0.05 MB)
  ✓ 上传成功: src/main.py

📊 上传统计:
  ✓ 成功: 15 个文件
  ✗ 失败: 0 个文件

🎉 文件夹上传完成！
```

### Advanced Upload Features

- **🔄 Smart Reconnection** - Automatically handles iCloud API caching issues
- **📁 Structure Preservation** - Maintains complete folder hierarchy
- **⚡ Fallback Strategies** - Multiple retry mechanisms for maximum success
- **🛡️ Conflict Resolution** - Configurable handling of existing files
- **📊 Real-time Progress** - Detailed status for each file and folder
- **🔧 Backup Strategy** - Flattened upload when folder creation fails completely

### Conflict Modes

Configure how to handle existing files:

- **`skip`** - Skip existing files (fastest, preserves existing data)
- **`overwrite`** - Replace existing files (ensures latest version)
- **`ask`** - Interactive prompt for each conflict (not recommended for automation)

## Advanced Configuration

### Complete Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `APPLE_ID` | Apple ID email address | Yes* | None |
| `APPLE_PASSWORD` | Apple password | Yes* | None |
| `LOCAL_FOLDER_PATH` | Path to local folder for upload | Yes | None |
| `REMOTE_FOLDER_NAME` | Destination folder name in iCloud | No | Local folder name |
| `CONFLICT_MODE` | File conflict handling mode | No | `skip` |

*Required for automated operation

### Technical Specifications

- **File Size Limit**: 100MB per file (automatically skipped if exceeded)
- **Folder Depth**: Unlimited nesting supported
- **API Handling**: Advanced reconnection strategy for folder access issues
- **Retry Logic**: 3-layer fallback system (immediate → reconnect → traditional retry)

### Advanced Features

- ✅ **Smart Folder Creation** - Handles iCloud API synchronization delays
- ✅ **Reconnection Strategy** - Creates fresh API connections to bypass caching
- ✅ **Backup Upload Mode** - Falls back to flattened naming when folders fail
- ✅ **Progress Statistics** - Real-time success/failure tracking
- ✅ **China Support** - Optimized for China mainland iCloud infrastructure

## Troubleshooting

### Common Issues

**1. "No child named 'FolderName' exists" - API Caching Issue**
- **Cause**: iCloud API caches folder listings, preventing immediate access to newly created folders
- **Solution**: The program automatically uses reconnection strategy to bypass this
- **Manual Fix**: Restart the program if the automatic fix fails

**2. "iCloud Drive service not available"**
- Ensure iCloud Drive is enabled in Settings > Apple ID > iCloud
- Check network connection and firewall settings
- Verify your Apple ID has iCloud Drive access

**3. "Two-factor authentication required"**
- Use app-specific passwords instead of your main Apple ID password
- Generate app passwords at appleid.apple.com → Sign In & Security → App-Specific Passwords
- Ensure 2FA is properly configured for your Apple ID

**4. Configuration errors**
- Check `.env` file format and syntax
- Ensure `LOCAL_FOLDER_PATH` points to an existing folder
- Verify file permissions on the local folder

**5. Upload partial failures**
- Files over 100MB are automatically skipped (expected behavior)
- Check network stability for large uploads
- Review file permissions and read access

### Advanced Troubleshooting

**Enable Verbose Output**
```bash
# Add debugging info to your .env file
DEBUG=true
```

**Check Specific Components**
```bash
# Test iCloud connection only
uv run python debug_api.py

# Test folder upload only
uv run python test_upload.py
```

### Technical Details

The program implements a 3-tier strategy to handle iCloud API limitations:

1. **Immediate Access** - Try accessing folders directly after creation
2. **Reconnection Strategy** - Create fresh API connection to bypass caching
3. **Traditional Retry** - Wait and retry with exponential backoff
4. **Backup Mode** - Upload files with flattened naming as final fallback

## Project Structure

```
icloud-drive-uploader/
├── main.py          # Main automation program with advanced API handling
├── debug_api.py     # iCloud API debugging and testing tool
├── test_upload.py   # Upload functionality testing script
├── CLAUDE.md        # Developer guide and technical documentation
├── README.md        # User documentation (this file)
├── pyproject.toml   # Project configuration and dependencies
├── uv.lock         # Dependency lock file
└── .env             # Configuration file (user-created)
```

## Security Notes

- ✅ No hardcoded credentials in code
- ✅ Uses `getpass` to hide password input
- ✅ Supports secure environment variable storage
- ⚠️ Ensure `.env` files are not committed to version control
- ⚠️ Regularly update Apple passwords

## Changelog

### v2.0.0 (Current) - 🚀 Advanced API Handling Release
- ✨ **Major Feature**: Non-interactive automation mode with .env configuration
- 🛠️ **API Innovation**: Advanced reconnection strategy to solve iCloud API caching issues
- ⚡ **Smart Retry Logic**: 3-tier fallback system (immediate → reconnect → traditional retry)
- 🔧 **Backup Strategy**: Flattened file upload when folder creation completely fails
- 📊 **Enhanced Progress**: Real-time detailed upload statistics and status tracking
- ⚖️ **Conflict Resolution**: Configurable modes (skip/overwrite/ask) via environment variables
- 🔄 **Technical Fix**: Solves "No child named 'FolderName' exists" API synchronization issue
- 📝 **Complete Documentation**: Updated guides reflecting new automation capabilities

### v1.0.1
- ✨ Added python-dotenv dependency for .env file support
- ✨ Enhanced environment variable loading from .env files
- 📝 Updated Python version requirement to 3.11 for better compatibility
- 📝 Added .env.example file for reference
- 📝 Updated documentation with .env file setup instructions

### v1.0.0
- ✨ Initial release
- ✨ Recursive folder upload functionality
- ✨ Environment variable authentication support
- ✨ Interactive menu system
- ✨ Progress tracking and error handling
- ✨ China mainland iCloud support

## Contributing

Welcome to submit Issues and Pull Requests to improve this tool!

## License

This project is for learning and personal use only. Please comply with Apple's Terms of Service.