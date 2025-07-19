# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for interacting with iCloud services using the `pyicloud` library. The project uses `uv` for dependency management.

## Development Commands

- **Install dependencies**: `uv install`
- **Run the main script**: `uv run python main.py`
- **Add dependencies**: `uv add <package-name>`

## Architecture

- `main.py`: Entry point that authenticates with iCloud and provides folder upload functionality
- `pyproject.toml`: Project configuration and dependencies managed by uv
- Uses `pyicloud` library for iCloud API interactions

## Security Considerations

**UPDATED**: Credentials are now properly handled through environment variables:

1. **Environment Variables**: Set `APPLE_ID` and `APPLE_PASSWORD` environment variables
2. **Fallback Input**: If environment variables are not set, the program will prompt for credentials securely
3. **Password Security**: Uses `getpass` module to hide password input
4. **No Hardcoded Credentials**: All hardcoded credentials have been removed from the codebase

### Setting Environment Variables

**macOS/Linux:**
```bash
export APPLE_ID="your_apple_id@example.com"
export APPLE_PASSWORD="your_password"
```

**Windows:**
```cmd
set APPLE_ID=your_apple_id@example.com
set APPLE_PASSWORD=your_password
```

**Or create a `.env` file** (recommended for development):
```
APPLE_ID=your_apple_id@example.com
APPLE_PASSWORD=your_password
```

## Features

### Core Functionality
1. **iCloud Drive Access**: Connect to and browse iCloud Drive contents
2. **Folder Upload**: Recursively upload entire folder structures to iCloud Drive
3. **Non-Interactive Mode**: Automated uploading with pre-configured paths via environment variables

### Upload Features
- **Recursive Upload**: Automatically handles nested folders and files
- **Progress Tracking**: Shows upload status with file counts and sizes
- **Error Handling**: Graceful handling of duplicates, file size limits, and permissions
- **Smart Resumption**: Continues uploading to existing folders without conflict
- **API Sync Fix**: Advanced connection refresh strategy to handle iCloud API caching issues

### Advanced Features
- **Connection Refresh**: Automatically creates new API connections when folder access fails due to caching
- **Multiple Retry Strategies**: Uses both immediate access and reconnection fallback methods
- **Backup Upload Strategy**: Falls back to flattened file naming when folder creation completely fails

## Code Structure

The application follows this flow:
1. **Credential Management**: Load from environment or prompt user securely
2. **iCloud Authentication**: Initialize PyiCloudService with China mainland support
3. **2FA Handling**: Process two-factor authentication if required
4. **Session Trust**: Establish trusted session for iCloud Drive access
5. **Interactive Operations**: Provide menu-driven interface for folder operations