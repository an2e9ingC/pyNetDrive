# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Windows NAS network drive mapping tool with three variants:
- `openNetDrive.py` - Primary GUI app (tkinter, 墨绿色 theme)
- `openNetDrive_pywebview.py` - Alternative GUI (pywebview/WebView2)
- `smart_reconnect.py` - CLI version

## Development Commands

**Run variants:**
```bash
python openNetDrive.py          # tkinter GUI
python openNetDrive_pywebview.py # pywebview GUI
python smart_reconnect.py       # CLI
```

**Install dependencies:**
```bash
pip install colorama           # for CLI version
pip install pywebview          # for pywebview GUI
```

## Architecture Notes

**User auto-detection** (`determine_target_user`):
- System user `xuchuan` → NAS user `mr` → N: drive
- System user `ruiwa` → NAS user `lady` → M: drive
- Default fallback: `mr`

**Drive mapping:**
- Personal: `\\NAS4MrLady\home` → N: (mr) or M: (lady)
- Public: `\\NAS4MrLady\home_public` → P: (shared)
- Uses `net use` commands with `/persistent:no`

**Startup integration:**
- Windows registry key `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Entry name: `01_openNetDrive`

## Key Functions

All three files share core business logic:
- `is_drive_valid(drive)` - Check if drive is mapped
- `delete_connection(drive)` - Remove mapping via `net use /delete`
- `create_connection(drive, path, user, password)` - Create mapping
