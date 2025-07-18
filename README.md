# iCloud Drive Uploader

A powerful Python tool for recursively uploading local folders to iCloud Drive with secure authentication and progress tracking.

## Features

- **Recursive Folder Upload** - Upload entire folder structures including subfolders
- **Secure Authentication** - Environment variables or secure interactive password input
- **Progress Tracking** - Real-time upload progress with file counts and sizes
- **Smart Error Handling** - Handle duplicates, file size limits, and permissions
- **Interactive Interface** - User-friendly command-line menu system
- **China Mainland Support** - Automatic configuration for China iCloud servers

## System Requirements

- Python 3.11+
- uv package manager
- Valid Apple ID with iCloud Drive access

## Quick Start

### 1. Install Dependencies
```bash
uv install
```

### 2. Setup Authentication

**Method 1: Environment Variables (Recommended)**
```bash
# macOS/Linux
export APPLE_ID="your_apple_id@example.com"
export APPLE_PASSWORD="your_password"

# Windows
set APPLE_ID=your_apple_id@example.com
set APPLE_PASSWORD=your_password
```

**Method 2: Interactive Input**
If environment variables are not set, the program will securely prompt for credentials.

### 3. Run the Program
```bash
uv run python main.py
```

## Usage Guide

### Main Menu Options

After startup, you'll see these options:

```
Please select an operation:
1. Upload local folder to iCloud Drive
2. View local folder contents
3. View current iCloud Drive contents
4. Exit
```

### Upload Folders

1. Select option `1`
2. Enter the full path to your local folder
3. Enter remote folder name (optional, leave blank to use local folder name)
4. Wait for upload completion and view statistics

**Example:**
```
Enter local folder path: /Users/username/Documents/MyProject
Enter remote folder name (leave blank to use local folder name): ProjectBackup
```

### Upload Features

- **Auto-create folder structure** - Recreates complete folder hierarchy in iCloud Drive
- **Duplicate handling** - Continues uploading to existing folders without overwriting
- **Large file skip** - Automatically skips files over 100MB
- **Detailed logging** - Shows upload status and size for each file
- **Upload statistics** - Displays success/failure counts after completion

## Advanced Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `APPLE_ID` | Apple ID email address | No* |
| `APPLE_PASSWORD` | Apple password | No* |

*If not set, program will prompt for input

### File Size Limits

- Maximum single file size: **100MB**
- Files exceeding limit are automatically skipped and logged

### Supported Operations

- ✅ Create new folders
- ✅ Upload various file types
- ✅ Handle nested folder structures
- ✅ Detect and skip duplicate folders
- ✅ Display detailed error messages

## Troubleshooting

### Common Issues

**1. "iCloud Drive service not available"**
- Ensure iCloud Drive is enabled in Settings > Apple ID > iCloud
- Check network connection
- Try restarting the program

**2. "Two-factor authentication required"**
- Enter the verification code received on your other devices
- Ensure two-factor authentication is enabled for your Apple ID

**3. "Upload failed" errors**
- Check file permissions
- Verify file size doesn't exceed limits
- Ensure stable network connection

**4. China mainland connection issues**
- Program automatically configures `china_mainland=True`
- If issues persist, check network environment

### Debug Mode

The program includes detailed logging that shows:
- Connection status
- File upload progress
- Error details
- Statistics information

## Project Structure

```
icloud-drive-uploader/
├── main.py          # Main program file
├── CLAUDE.md        # Developer guide
├── README.md        # Usage documentation (this file)
├── pyproject.toml   # Project configuration
└── uv.lock         # Dependency lock file
```

## Security Notes

- ✅ No hardcoded credentials in code
- ✅ Uses `getpass` to hide password input
- ✅ Supports secure environment variable storage
- ⚠️ Ensure `.env` files are not committed to version control
- ⚠️ Regularly update Apple passwords

## Changelog

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