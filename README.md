# openNetDrive

Windows NAS 网络驱动器自动连接工具，支持智能用户识别和一键映射。

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 特性

- **现代化 GUI** - 祖母绿主题，清新现代审美，支持多显示器居中显示
- **智能用户识别** - 根据 Windows 登录用户自动选择 NAS 账户，支持自定义映射关系
- **多映射配置** - 支持添加多组 NAS 路径与本地盘符映射，配置持久化保存
- **密码加密保存** - 支持加密保存密码，开机自动连接
- **实时状态反馈** - 连接过程中显示进度，状态灯直观显示连接状态
- **开机自启** - 支持通过注册表添加开机自动运行
- **一键卸载** - 支持通过界面快捷卸载程序，可选保留配置和日志

## 快速开始

### 方式一：直接运行（推荐）

从 [Releases](https://github.com/an2e9ingC/openNetDrive/releases) 下载最新版本的 `openNetDrive.exe`，双击即可运行，无需安装 Python。

### 方式二：源码运行

#### 环境要求

- Windows 10/11
- Python 3.6+
- tkinter (Python 内置)

#### 安装

```bash
# 克隆或下载本仓库
cd openNetDrive
```

#### 运行

```bash
python openNetDrive.py
```

### 打包成独立可执行文件

```bash
# 安装打包工具
pip install -r requirements.txt

# 运行打包脚本
python build_release.py
```

打包完成后，`release/` 目录中的 `openNetDrive.exe` 即为独立可执行文件。

## 功能说明

### 用户自动映射

支持根据 Windows 登录用户名自动匹配 NAS 用户名，映射关系可在 `config.json` 中自定义配置：

```json
{
  "user_mapping": {
    "windows_user1": "nas_user1",
    "windows_user2": "nas_user2"
  }
}
```

### 驱动器映射

支持自定义 NAS 路径与本地盘符的映射关系：

- 支持多组映射配置
- 映射设置为非持久化（`/persistent:no`）
- 自动检测并避开已占用的盘符

### GUI 功能

- ✅ 多组映射配置管理
- ✅ 单行独立连接/断开按钮
- ✅ 一键连接所有/断开所有
- ✅ 状态灯直观显示连接状态
- ✅ 密码大写锁定实时提示
- ✅ 保存密码（加密存储）
- ✅ 开机自启快捷配置
- ✅ 运行日志记录与查看
- ✅ 一键卸载功能（可选保留配置和日志）

### 配置文件

首次运行后会自动生成 `config.json` 配置文件：

```json
{
  "mappings": [
    {"nas_path": "\\\\YOUR_NAS\\share", "drive": "Z:", "enabled": true}
  ],
  "last_user": "auto",
  "auto_startup": false,
  "user_mapping": {
    "windows_user": "nas_user"
  },
  "saved_password": "加密的密码"
}
```

### 开机自启

GUI 版本支持一键添加开机自启（通过 HKCU 注册表 Run 键），重启后自动运行。

### 卸载程序

GUI 版本支持一键卸载程序，点击界面右下角的"卸载软件"按钮即可：
- 删除程序文件
- 删除开机自启注册表项
- 可选是否保留配置文件（`config.json`）
- 可选是否保留日志文件（`logs/` 目录）

## 项目结构

```
openNetDrive/
├── openNetDrive.py            # tkinter GUI 主版本
├── openNetDrive_pywebview.py  # pywebview GUI 版本（可选）
├── smart_reconnect.py         # CLI 版本（可选）
├── build_release.py           # 打包脚本
├── requirements.txt           # 依赖列表
├── config.json                # 配置文件（运行时生成，已加入 .gitignore）
├── logs/                      # 日志目录（运行时生成，已加入 .gitignore）
├── release/                   # 打包发布目录
│   ├── openNetDrive.exe       # 独立可执行文件
│   ├── config.json            # 配置文件模板
│   └── 使用说明.txt           # 简要使用说明
├── CLAUDE.md                  # AI 助手配置
├── README.md
└── .gitignore
```

## 技术栈

- **GUI 框架**: tkinter / pywebview (可选)
- **系统调用**: Windows `net use` 命令
- **注册表操作**: winreg
- **配置存储**: JSON
- **打包工具**: PyInstaller

## 注意事项

1. 首次运行需要输入 NAS 密码
2. 映射设置为非持久化（`/persistent:no`），重启后需重新连接
3. 需要确保 NAS 服务器在网络中可访问
4. 日志文件按日期存储在 `logs/` 目录
5. 密码使用 base64 编码存储，请勿在公共场合分享配置文件

## 更新日志

### v2026.3.22
- 新增一键卸载功能，支持可选保留配置和日志
- 添加 PyInstaller 兼容性支持，修复打包相关问题
- 添加 `build_release.py` 打包脚本
- 添加 `release/` 发布目录配置

### v2026.3.16
- 初始版本
- 现代化 UI，祖母绿主题
- 支持多组映射配置
- 单行独立连接/断开按钮
- 一键连接所有/断开所有
- 密码加密保存
- 用户映射关系可配置
- 状态灯直观显示连接状态
- 密码大写锁定实时提示
- 开机自启快捷配置
- 运行日志记录与查看
- 多显示器居中显示

## License

MIT
