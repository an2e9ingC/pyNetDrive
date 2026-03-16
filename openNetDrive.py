# -*- coding: utf-8 -*-
"""
openNetDrive — 清新现代版网络磁盘映射工具
- 祖母绿主题，清新现代审美
- 支持多组映射配置
- 配置文件自动保存
"""
import os
import sys
import subprocess
import time
import threading
import string
import logging
import json
import ctypes
from datetime import datetime

# ==========================================
# tkinter 依赖检查
# ==========================================
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
except ImportError:
    print("当前 Python 环境未提供 tkinter 图形界面支持。")
    print("请使用官方 Python 安装包（安装时勾选 Tcl/Tk / tkinter）。")
    input("按回车键退出...")
    sys.exit(1)

# ==========================================
# 配置文件路径
# ==========================================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# ==========================================
# 日志配置
# ==========================================
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"openNetDrive_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# 业务逻辑
# ==========================================

def get_system_username() -> str:
    try:
        return os.getlogin()
    except Exception:
        return os.environ.get('USERNAME', 'unknown')

def determine_target_user(sys_user: str, force_user: str = None, config_mgr: 'ConfigManager' = None) -> str:
    """根据系统用户名确定 NAS 用户名"""
    if force_user and str(force_user).strip() and str(force_user).strip().lower() not in ("自动", ""):
        return str(force_user).strip().lower()
    # 从配置文件获取用户映射关系
    if config_mgr:
        return config_mgr.get_user_mapping(sys_user)
    # 默认映射关系
    sys_user_lower = sys_user.lower()
    if sys_user_lower == "xuchuan":
        return "mr"
    elif sys_user_lower == "ruiwa":
        return "lady"
    return "mr"

def get_used_drives() -> set:
    """获取当前已被占用的盘符集合"""
    used = set()
    try:
        res = subprocess.run("net use", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="gbk", errors="ignore")
        for line in (res.stdout or "").splitlines():
            line = line.strip()
            if len(line) >= 2 and line[1] == ':':
                used.add(line[:2].upper())
    except Exception:
        pass
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            used.add(f"{letter}:")
    return used


# ==========================================
# 键盘大小写状态检测（ctypes）
# ==========================================

VK_CAPITAL = 0x14

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetKeyState.argtypes = [ctypes.c_int]
user32.GetKeyState.restype = ctypes.c_short


def is_capslock_on() -> bool:
    try:
        state = user32.GetKeyState(VK_CAPITAL)
        return bool(state & 0x0001)
    except Exception:
        return False

def is_drive_valid(drive: str) -> bool:
    try:
        res = subprocess.run(f"net use {drive}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0 and os.path.exists(drive)
    except Exception:
        return False

def delete_connection(drive: str):
    try:
        subprocess.run(f"net use {drive} /delete /yes", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def create_connection(drive: str, path: str, user: str, password: str) -> tuple:
    """创建连接，返回 (成功标志，错误消息)"""
    cmd = f'net use {drive} "{path}" "{password}" /user:"{user}" /persistent:no'
    try:
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='gbk', errors='ignore')
        output = res.stdout.strip()
        if res.returncode == 0:
            time.sleep(0.3)
            if os.path.exists(drive):
                return True, ""
            # 有些情况下命令成功但无法立即验证，也认为成功
            return True, ""
        # 连接失败，返回错误信息
        return False, output
    except Exception as e:
        return False, str(e)


# ==========================================
# Windows 开机启动（注册表 Run）
# ==========================================
STARTUP_REG_NAME = "01_openNetDrive"

def _is_windows() -> bool:
    return sys.platform.startswith("win")

def add_to_startup() -> bool:
    if not _is_windows():
        return False
    try:
        import winreg
    except Exception:
        return False
    try:
        exe = sys.executable
        script = os.path.abspath(__file__)
        cmd = f'"{exe}" "{script}"'
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, STARTUP_REG_NAME, 0, winreg.REG_SZ, cmd)
        return True
    except Exception:
        return False

def remove_from_startup() -> bool:
    if not _is_windows():
        return False
    try:
        import winreg
    except Exception:
        return False
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            try:
                winreg.DeleteValue(key, STARTUP_REG_NAME)
                return True
            except FileNotFoundError:
                return False
    except Exception:
        return False

def is_in_startup() -> bool:
    if not _is_windows():
        return False
    try:
        import winreg
    except Exception:
        return False
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            try:
                value, _ = winreg.QueryValueEx(key, STARTUP_REG_NAME)
            except FileNotFoundError:
                return False
        if not value:
            return False
        exe = sys.executable
        script = os.path.abspath(__file__)
        expected_cmd = f'"{exe}" "{script}"'
        return expected_cmd.lower() == str(value).strip().lower()
    except Exception:
        return False


# ==========================================
# 祖母绿主题配色
# ==========================================
COLORS = {
    # 主色调：祖母绿
    'emerald': '#047857',
    'emerald_light': '#10b981',
    'emerald_dark': '#065f46',
    'emerald_hover': '#059669',

    # 按钮颜色
    'btn_blue': '#2563eb',
    'btn_blue_hover': '#1d4ed8',
    'btn_orange': '#ea580c',
    'btn_orange_hover': '#c2410c',
    'btn_green': '#059669',
    'btn_green_hover': '#047857',
    'btn_red': '#dc2626',
    'btn_red_hover': '#b91c1c',
    'btn_gray': '#6b7280',

    # 背景色系
    'bg_primary': '#ecfdf5',
    'bg_secondary': '#d1fae5',
    'bg_white': '#ffffff',

    # 文字色系
    'text_primary': '#064e3b',
    'text_secondary': '#34d399',
    'text_muted': '#6b9080',

    # 状态色
    'success': '#059669',
    'success_bg': '#d1fae5',
    'warning': '#d97706',
    'warning_bg': '#fef3c7',
    'error': '#dc2626',
    'error_bg': '#fee2e2',

    # 边框与分隔
    'border': '#a7f3d0',
    'divider': '#6ee7b7',
}

# 字体配置
FONTS = {
    'title': ('Microsoft YaHei UI', 14, 'bold'),
    'subtitle': ('Microsoft YaHei UI', 9),
    'section_title': ('Microsoft YaHei UI', 10, 'bold'),
    'label': ('Microsoft YaHei UI', 9),
    'label_bold': ('Microsoft YaHei UI', 9, 'bold'),
    'entry': ('Microsoft YaHei UI', 9),
    'button': ('Microsoft YaHei UI', 9, 'bold'),
    'button_normal': ('Microsoft YaHei UI', 9),
    'log': ('Consolas', 9),
    'status': ('Microsoft YaHei UI', 9),
}

# ==========================================
# 配置管理
# ==========================================

class ConfigManager:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self._load()
        # 确保配置中包含所有必要字段
        self._ensure_default_fields()

    def _load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载配置失败：{e}")
        return {
            'mappings': [],
            'last_user': '自动',
            'auto_startup': False,
            'user_mapping': {
                'xuchuan': 'mr',
                'ruiwa': 'lady'
            },
            'saved_password': None  # 加密保存的密码
        }

    def _ensure_default_fields(self):
        """确保配置中包含所有必要字段"""
        modified = False
        if 'user_mapping' not in self.config:
            self.config['user_mapping'] = {
                'xuchuan': 'mr',
                'ruiwa': 'lady'
            }
            modified = True
        if 'saved_password' not in self.config:
            self.config['saved_password'] = None
            modified = True
        if 'auto_startup' not in self.config:
            self.config['auto_startup'] = False
            modified = True
        if 'last_user' not in self.config:
            self.config['last_user'] = '自动'
            modified = True
        if 'mappings' not in self.config:
            self.config['mappings'] = []
            modified = True
        if modified:
            self.save()

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"保存配置失败：{e}")

    def add_mapping(self, nas_path, drive):
        mapping = {
            'nas_path': nas_path,
            'drive': drive.upper(),
            'enabled': True
        }
        self.config['mappings'].append(mapping)
        self.save()
        return mapping

    def remove_mapping(self, index):
        if 0 <= index < len(self.config['mappings']):
            del self.config['mappings'][index]
            self.save()

    def get_mappings(self):
        return self.config['mappings'].copy()

    def set_last_user(self, user):
        self.config['last_user'] = user
        self.save()

    def get_last_user(self):
        return self.config.get('last_user', '自动')

    def set_user_mapping(self, sys_user, nas_user):
        if 'user_mapping' not in self.config:
            self.config['user_mapping'] = {}
        self.config['user_mapping'][sys_user.lower()] = nas_user.lower()
        self.save()

    def get_user_mapping(self, sys_user):
        user_mapping = self.config.get('user_mapping', {})
        return user_mapping.get(sys_user.lower(), 'mr')

    def set_saved_password(self, password):
        """加密保存密码"""
        if password:
            # 简单 base64 编码（注意：这不是强加密，仅用于避免明文）
            import base64
            encoded = base64.b64encode(password.encode('utf-8')).decode('utf-8')
            self.config['saved_password'] = encoded
        else:
            self.config['saved_password'] = None
        self.save()

    def get_saved_password(self):
        """获取保存的密码"""
        encoded = self.config.get('saved_password')
        if encoded:
            try:
                import base64
                return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
            except Exception:
                return None
        return None


# ==========================================
# 主窗口应用
# ==========================================

class OpenNetDriveApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("openNetDrive")
        self.root.configure(bg=COLORS['bg_primary'])

        # 配置管理器
        self.config_mgr = ConfigManager()

        # 状态跟踪
        self._connecting = False
        self._log_expanded = False
        self._mapping_frames = {}  # 存储每个映射的状态帧
        self._connect_results = {}  # 存储连接结果

        self._build_ui()
        self._init_size()
        self._load_saved_mappings()

    def _center_on_primary_monitor(self):
        """将窗口居中显示在主显示器上"""
        self.root.update_idletasks()

        try:
            user32 = ctypes.windll.user32
            MONITOR_DEFAULTTOPRIMARY = 1
            hmon = user32.MonitorFromWindow(self.root.winfo_id(), MONITOR_DEFAULTTOPRIMARY)

            class MONITORINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint),
                            ("rcMonitor", ctypes.wintypes.RECT),
                            ("rcWork", ctypes.wintypes.RECT),
                            ("dwFlags", ctypes.c_uint)]

            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            user32.GetMonitorInfoW(hmon, ctypes.byref(mi))

            sw = mi.rcWork.right - mi.rcWork.left
            sh = mi.rcWork.bottom - mi.rcWork.top
            sx = mi.rcWork.left
            sy = mi.rcWork.top
        except Exception:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            sx = 0
            sy = 0

        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()

        x = sx + (sw - w) // 2
        y = sy + (sh - h) // 2

        self.root.geometry(f"+{x}+{y}")

    def _init_size(self):
        """根据内容初始化窗口大小"""
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        # 宽度增加 20%，高度降低 10%
        new_w = int(w * 1.2)
        new_h = int(h * 0.9)
        self.root.minsize(max(new_w, 1020), max(new_h, 700))
        self.root.geometry(f"{max(new_w, 1020)}x{max(new_h, 700)}")

    def _build_ui(self):
        self._center_on_primary_monitor()

        # 顶部标题栏
        self._build_header()

        # 主体内容区
        content_frame = tk.Frame(self.root, bg=COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        # 认证信息卡片
        self._build_auth_card(content_frame)

        # 添加映射卡片
        self._build_add_mapping_card(content_frame)

        # 映射列表卡片
        self._build_mappings_card(content_frame)

        # 连接按钮和开机自启同行
        self._build_button_startup_row(content_frame)

        # 日志区（默认折叠）
        self._build_log_section(content_frame)

    def _build_header(self):
        header = tk.Frame(self.root, bg=COLORS['emerald'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title_container = tk.Frame(header, bg=COLORS['emerald'])
        title_container.pack(side=tk.LEFT, padx=20, pady=14)

        icon_canvas = tk.Canvas(title_container, width=28, height=28, bg=COLORS['emerald'], highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 10))
        icon_canvas.create_rectangle(5, 7, 23, 21, fill=COLORS['bg_white'], outline=COLORS['emerald_light'], width=2)
        icon_canvas.create_line(5, 12, 23, 12, fill=COLORS['emerald_light'], width=2)

        tk.Label(title_container, text="openNetDrive", font=FONTS['title'],
                 fg=COLORS['bg_white'], bg=COLORS['emerald']).pack(side=tk.LEFT, anchor=tk.W)

    def _build_auth_card(self, parent):
        card = tk.Frame(parent, bg=COLORS['bg_white'], relief=tk.FLAT)
        card.pack(fill=tk.X, pady=(0, 8))

        inner = tk.Frame(card, bg=COLORS['bg_white'])
        inner.pack(fill=tk.X, padx=20, pady=12)

        # 标题行
        tk.Label(inner, text="认证信息", font=FONTS['section_title'],
                 fg=COLORS['emerald'], bg=COLORS['bg_white']).pack(anchor=tk.W, pady=(0, 10))

        # 用户名和密码同行显示
        row_frame = tk.Frame(inner, bg=COLORS['bg_white'])
        row_frame.pack(fill=tk.X, pady=3)

        # 用户名 - 固定标签宽度 8
        user_frame = tk.Frame(row_frame, bg=COLORS['bg_white'])
        user_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        tk.Label(user_frame, text="用户名", width=8, anchor=tk.W, font=FONTS['label'],
                 fg=COLORS['text_primary'], bg=COLORS['bg_white']).pack(side=tk.LEFT, padx=(0, 6))

        self.var_user = tk.StringVar(value=self.config_mgr.get_last_user())
        # 自动匹配默认用户名
        if self.var_user.get() == "自动":
            sys_user = get_system_username()
            default_user = determine_target_user(sys_user, None, self.config_mgr)
            self.var_user.set(default_user)

        # 使用 Entry 代替 Combobox，支持用户输入
        entry_user = tk.Entry(user_frame, textvariable=self.var_user, font=FONTS['entry'], width=10, relief=tk.SOLID, bd=1)
        entry_user.pack(side=tk.LEFT, expand=True)
        entry_user.bind('<KeyRelease>', lambda _: self.config_mgr.set_last_user(self.var_user.get()))

        # 密码 - 固定标签宽度 8
        pass_frame = tk.Frame(row_frame, bg=COLORS['bg_white'])
        pass_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0))

        tk.Label(pass_frame, text="密码", width=8, anchor=tk.W, font=FONTS['label'],
                 fg=COLORS['text_primary'], bg=COLORS['bg_white']).pack(side=tk.LEFT, padx=(0, 6))

        pass_entry_frame = tk.Frame(pass_frame, bg=COLORS['bg_white'])
        pass_entry_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.entry_pass = tk.Entry(pass_entry_frame, show='•', font=FONTS['entry'],
                                   width=40, relief=tk.SOLID, bd=1)
        self.entry_pass.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.entry_pass.bind('<FocusIn>', lambda _: self._start_kbd_watch())
        self.entry_pass.bind('<Return>', lambda _: self._do_connect())

        self.kbd_label = tk.Label(pass_entry_frame, text="", font=('Microsoft YaHei UI', 8, 'bold'),
                                  fg=COLORS['warning'], bg=COLORS['bg_white'])
        self.kbd_label.pack(side=tk.LEFT, padx=(6, 0))

        # 保存密码选项
        self.var_save_password = tk.BooleanVar(value=False)
        self.cb_save_password = tk.Checkbutton(pass_frame, text="保存密码", variable=self.var_save_password,
                                               font=FONTS['label'], fg=COLORS['text_muted'],
                                               bg=COLORS['bg_white'], selectcolor=COLORS['bg_secondary'],
                                               activebackground=COLORS['bg_white'], activeforeground=COLORS['text_primary'],
                                               command=self._on_save_password_changed)
        self.cb_save_password.pack(anchor=tk.W, pady=(8, 0))

        # 加载保存的密码
        saved_pwd = self.config_mgr.get_saved_password()
        if saved_pwd:
            self.entry_pass.delete(0, tk.END)
            self.entry_pass.insert(0, saved_pwd)
            self.var_save_password.set(True)

    def _build_add_mapping_card(self, parent):
        """添加映射配置卡片"""
        card = tk.Frame(parent, bg=COLORS['bg_white'], relief=tk.FLAT)
        card.pack(fill=tk.X, pady=(0, 8))

        inner = tk.Frame(card, bg=COLORS['bg_white'])
        inner.pack(fill=tk.X, padx=20, pady=12)

        # 标题行
        tk.Label(inner, text="添加映射", font=FONTS['section_title'],
                 fg=COLORS['emerald'], bg=COLORS['bg_white']).pack(anchor=tk.W, pady=(0, 10))

        # 目标盘符和 NAS 路径同行显示
        row_frame = tk.Frame(inner, bg=COLORS['bg_white'])
        row_frame.pack(fill=tk.X, pady=3)

        # 目标盘符 - 固定标签宽度 8
        drive_frame = tk.Frame(row_frame, bg=COLORS['bg_white'])
        drive_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        tk.Label(drive_frame, text="目标盘符", width=8, anchor=tk.W, font=FONTS['label'],
                 fg=COLORS['text_primary'], bg=COLORS['bg_white']).pack(side=tk.LEFT, padx=(0, 6))

        self.var_drive = tk.StringVar(value="")
        self.combo_drive = ttk.Combobox(drive_frame, textvariable=self.var_drive, state='readonly',
                                        width=10, font=FONTS['entry'])
        self.combo_drive.pack(side=tk.LEFT, expand=True)
        self._refresh_available_drives()

        # NAS 路径 - 固定标签宽度 8
        path_frame = tk.Frame(row_frame, bg=COLORS['bg_white'])
        path_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0))

        tk.Label(path_frame, text="NAS 路径", width=8, anchor=tk.W, font=FONTS['label'],
                 fg=COLORS['text_primary'], bg=COLORS['bg_white']).pack(side=tk.LEFT, padx=(0, 6))

        self.entry_path = tk.Entry(path_frame, font=FONTS['entry'], width=40, relief=tk.SOLID, bd=1)
        self.entry_path.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.entry_path.bind('<FocusIn>', lambda _: self.entry_path.config(bg=COLORS['bg_secondary']))
        self.entry_path.bind('<FocusOut>', lambda _: self.entry_path.config(bg=COLORS['bg_white']))

        # 添加按钮
        btn_add = tk.Button(row_frame, text="添加", font=FONTS['button'],
                            fg=COLORS['bg_white'], bg=COLORS['emerald'],
                            activeforeground=COLORS['bg_white'], activebackground=COLORS['emerald_hover'],
                            relief=tk.FLAT, bd=0, padx=20, pady=6, cursor='hand2',
                            command=self._add_mapping)
        btn_add.pack(side=tk.LEFT, padx=(10, 0))
        self._bind_hover(btn_add, COLORS['emerald'], COLORS['emerald_hover'])

    def _build_mappings_card(self, parent):
        """映射列表卡片"""
        card = tk.Frame(parent, bg=COLORS['bg_white'], relief=tk.FLAT)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        inner = tk.Frame(card, bg=COLORS['bg_white'])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        # 标题行
        title_frame = tk.Frame(inner, bg=COLORS['bg_white'])
        title_frame.pack(fill=tk.X)

        tk.Label(title_frame, text="映射列表", font=FONTS['section_title'],
                 fg=COLORS['emerald'], bg=COLORS['bg_white']).pack(side=tk.LEFT)

        # 映射列表容器（可滚动）
        self.mappings_container = tk.Frame(inner, bg=COLORS['bg_white'])
        self.mappings_container.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def _build_button_startup_row(self, parent):
        """连接按钮和开机自启同行"""
        card = tk.Frame(parent, bg=COLORS['bg_white'], relief=tk.FLAT)
        card.pack(fill=tk.X, pady=(0, 8))

        inner = tk.Frame(card, bg=COLORS['bg_white'])
        inner.pack(fill=tk.X, padx=20, pady=10)

        # 左侧：开机自启
        self.var_startup = tk.BooleanVar(value=is_in_startup())
        self.cb_startup = tk.Checkbutton(inner, text="开机自动运行", variable=self.var_startup,
                                         font=FONTS['label'], fg=COLORS['text_muted'],
                                         bg=COLORS['bg_white'], selectcolor=COLORS['bg_secondary'],
                                         activebackground=COLORS['bg_white'], activeforeground=COLORS['text_primary'],
                                         command=self._toggle_startup)
        self.cb_startup.pack(side=tk.LEFT)

        # 右侧：连接按钮、断开所有按钮和状态
        btn_container = tk.Frame(inner, bg=COLORS['bg_white'])
        btn_container.pack(side=tk.RIGHT)

        # 状态指示器
        self.status_indicator_label = tk.Label(btn_container, text="", font=FONTS['status'],
                                               fg=COLORS['text_muted'], bg=COLORS['bg_white'])
        self.status_indicator_label.pack(side=tk.LEFT, padx=(0, 10))

        # 断开所有按钮 - 橙色
        self.btn_disconnect_all = tk.Button(btn_container, text="断开所有", font=FONTS['button'],
                                            fg=COLORS['bg_white'], bg=COLORS['btn_orange'],
                                            activeforeground=COLORS['bg_white'], activebackground=COLORS['btn_orange_hover'],
                                            relief=tk.FLAT, bd=0, padx=24, pady=8, cursor='hand2',
                                            command=self._do_disconnect_all)
        self.btn_disconnect_all.pack(side=tk.LEFT, padx=(0, 8))
        self._bind_hover(self.btn_disconnect_all, COLORS['btn_orange'], COLORS['btn_orange_hover'])

        # 连接按钮 - 蓝色
        self.btn_connect = tk.Button(btn_container, text="连接所有", font=FONTS['button'],
                                     fg=COLORS['bg_white'], bg=COLORS['btn_blue'],
                                     activeforeground=COLORS['bg_white'], activebackground=COLORS['btn_blue_hover'],
                                     relief=tk.FLAT, bd=0, padx=24, pady=8, cursor='hand2',
                                     command=self._do_connect)
        self.btn_connect.pack(side=tk.LEFT)
        self._bind_hover(self.btn_connect, COLORS['btn_blue'], COLORS['btn_blue_hover'])

    def _build_log_section(self, parent):
        """日志区域"""
        card = tk.Frame(parent, bg=COLORS['bg_white'], relief=tk.FLAT)
        card.pack(fill=tk.X, pady=(0, 8))

        inner = tk.Frame(card, bg=COLORS['bg_white'])
        inner.pack(fill=tk.X, padx=20, pady=10)

        # 标题行
        title_frame = tk.Frame(inner, bg=COLORS['bg_white'])
        title_frame.pack(fill=tk.X)

        tk.Label(title_frame, text="运行日志", font=FONTS['section_title'],
                 fg=COLORS['emerald'], bg=COLORS['bg_white']).pack(side=tk.LEFT)

        # 展开/折叠按钮
        self.btn_toggle_log = tk.Button(title_frame, text="▶ 查看日志", font=('Microsoft YaHei UI', 8),
                                        fg=COLORS['text_muted'], bg=COLORS['bg_white'],
                                        activeforeground=COLORS['emerald'],
                                        relief=tk.FLAT, bd=0, cursor='hand2',
                                        command=self._toggle_log)
        self.btn_toggle_log.pack(side=tk.RIGHT)

        # 日志文本区域（默认隐藏）
        self.log_frame = tk.Frame(inner, bg=COLORS['bg_primary'], relief=tk.SOLID, bd=1)

        self.log_text = scrolledtext.ScrolledText(self.log_frame, font=FONTS['log'], wrap=tk.WORD,
                                                   bg=COLORS['bg_primary'], fg=COLORS['text_primary'],
                                                   relief=tk.FLAT, padx=10, pady=8, height=11, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_configure('success', foreground=COLORS['success'])
        self.log_text.tag_configure('warning', foreground=COLORS['warning'])
        self.log_text.tag_configure('error', foreground=COLORS['error'])
        self.log_text.tag_configure('info', foreground=COLORS['text_muted'])

    def _create_mapping_row(self, index, nas_path, drive):
        """创建单个映射行的 UI"""
        frame = tk.Frame(self.mappings_container, bg=COLORS['bg_secondary'], relief=tk.FLAT)
        frame.pack(fill=tk.X, pady=3)

        # 状态灯
        canvas = tk.Canvas(frame, width=12, height=12, bg=COLORS['bg_secondary'], highlightthickness=0)
        canvas.pack(side=tk.LEFT, padx=(8, 6))
        indicator = canvas.create_oval(2, 2, 10, 10, fill=COLORS['error'], outline=COLORS['error'], width=2)

        # 盘符标签
        tk.Label(frame, text=f"{drive}", font=FONTS['label_bold'],
                 fg=COLORS['text_primary'], bg=COLORS['bg_secondary'], width=4, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 6))

        # 路径 - 使用更长宽度显示完整路径
        tk.Label(frame, text=nas_path, font=FONTS['status'],
                 fg=COLORS['text_muted'], bg=COLORS['bg_secondary'], anchor=tk.W, wraplength=400).pack(side=tk.LEFT, padx=(0, 10))

        # 状态文字
        status_var = tk.StringVar(value="未连接")
        tk.Label(frame, textvariable=status_var, font=FONTS['status'],
                 fg=COLORS['text_muted'], bg=COLORS['bg_secondary'], width=6).pack(side=tk.LEFT, padx=(0, 10))

        # 连接按钮 - 蓝色
        btn_connect = tk.Button(frame, text="连接", font=('Microsoft YaHei UI', 7),
                                fg=COLORS['bg_white'], bg=COLORS['btn_blue'],
                                relief=tk.FLAT, bd=0, padx=10, pady=2, cursor='hand2',
                                command=lambda i=index: self._connect_single_mapping(i))
        btn_connect.pack(side=tk.RIGHT, padx=(4, 2), pady=2)

        # 打开按钮 - 白色字体
        btn_open = tk.Button(frame, text="打开", font=('Microsoft YaHei UI', 7, 'bold'),
                             fg='#ffffff', bg=COLORS['emerald'],
                             state=tk.DISABLED, relief=tk.FLAT, bd=0, padx=10, pady=2, cursor='hand2',
                             command=lambda d=drive: self._open_drive(d))
        btn_open.pack(side=tk.RIGHT, padx=(4, 2), pady=2)

        # 删除按钮
        btn_delete = tk.Button(frame, text="删除", font=('Microsoft YaHei UI', 7),
                               fg=COLORS['bg_white'], bg=COLORS['btn_red'],
                               relief=tk.FLAT, bd=0, padx=10, pady=2, cursor='hand2',
                               command=lambda i=index: self._delete_mapping(i))
        btn_delete.pack(side=tk.RIGHT, padx=(4, 2), pady=2)

        # 断开按钮 - 未连接时置灰
        btn_disconnect = tk.Button(frame, text="断开", font=('Microsoft YaHei UI', 7),
                                   fg=COLORS['bg_white'], bg=COLORS['text_muted'],
                                   state=tk.DISABLED, relief=tk.FLAT, bd=0, padx=10, pady=2, cursor='hand2',
                                   command=lambda d=drive: self._disconnect_drive(d))
        btn_disconnect.pack(side=tk.RIGHT, padx=(4, 2), pady=2)

        return {
            'frame': frame,
            'canvas': canvas,
            'indicator': indicator,
            'status_var': status_var,
            'btn_open': btn_open,
            'btn_disconnect': btn_disconnect,
            'btn_connect': btn_connect,
        }

    def _bind_hover(self, btn, normal, hover):
        def on_enter(_):
            btn.configure(bg=hover)
        def on_leave(_):
            btn.configure(bg=normal)
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

    def _refresh_available_drives(self):
        used = get_used_drives()
        available = [f"{c}:" for c in string.ascii_uppercase if f"{c}:" not in used]
        self.combo_drive['values'] = available

    def _start_kbd_watch(self):
        def update():
            caps = is_capslock_on()
            if caps:
                self.kbd_label.configure(text="⚠ 大写", fg=COLORS['warning'])
            else:
                self.kbd_label.configure(text="✓ 小写", fg=COLORS['success'])
            try:
                focus = self.root.focus_get()
                if focus == self.entry_pass:
                    self.root.after(300, update)
            except Exception:
                pass
        update()

    def _on_save_password_changed(self):
        """保存密码选项变化时处理"""
        if self.var_save_password.get():
            # 保存密码
            password = self.entry_pass.get().strip()
            if password:
                self.config_mgr.set_saved_password(password)
                self._log("密码已保存", "success")
        else:
            # 清除保存的密码
            self.config_mgr.set_saved_password(None)
            self._log("已清除保存的密码", "warning")

    def _log(self, msg: str, tag: str = None):
        """记录日志到文件和界面"""
        logger.info(msg)

        if self._log_expanded:
            self.root.after(0, self._update_log_text, msg, tag)

    def _update_log_text(self, msg: str, tag: str = None):
        self.log_text.configure(state=tk.NORMAL)
        if tag:
            self.log_text.insert(tk.END, msg + '\n', tag)
        else:
            self.log_text.insert(tk.END, msg + '\n')
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _toggle_log(self):
        """展开/折叠日志"""
        if self._log_expanded:
            # 折叠
            self.log_frame.pack_forget()
            self.btn_toggle_log.configure(text="▶ 查看日志")
            self._log_expanded = False
        else:
            # 展开
            self.log_frame.pack(fill=tk.X, pady=(8, 0))
            self.btn_toggle_log.configure(text="◀ 折叠日志")
            self._log_expanded = True
            # 刷新日志内容
            self._refresh_log_display()

    def _refresh_log_display(self):
        """刷新日志显示"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        log_path = os.path.join(LOG_DIR, f"openNetDrive_{datetime.now().strftime('%Y%m%d')}.log")
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if 'ERROR' in line:
                            self.log_text.insert(tk.END, line + '\n', 'error')
                        elif 'WARNING' in line:
                            self.log_text.insert(tk.END, line + '\n', 'warning')
                        elif '成功' in line or '完成' in line:
                            self.log_text.insert(tk.END, line + '\n', 'success')
                        else:
                            self.log_text.insert(tk.END, line + '\n', 'info')
            except Exception:
                pass
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _load_saved_mappings(self):
        """加载保存的映射配置"""
        mappings = self.config_mgr.get_mappings()
        for i, m in enumerate(mappings):
            self._add_mapping_to_ui(i, m['nas_path'], m['drive'], m.get('enabled', True))
        # 加载完成后更新连接状态
        self.root.after(500, self._update_all_status)

    def _add_mapping_to_ui(self, index, nas_path, drive, enabled=True):
        """添加映射到 UI"""
        mapping_ui = self._create_mapping_row(index, nas_path, drive)
        self._mapping_frames[drive] = {
            'ui': mapping_ui,
            'nas_path': nas_path,
            'drive': drive,
            'enabled': enabled,
        }

    def _add_mapping(self):
        """添加映射配置"""
        nas_path = self.entry_path.get().strip()
        drive = self.var_drive.get().strip().upper()

        if not nas_path:
            messagebox.showwarning("警告", "请输入 NAS 路径")
            return
        if not drive:
            messagebox.showwarning("警告", "请选择目标盘符")
            return

        # 添加到配置
        self.config_mgr.add_mapping(nas_path, drive)

        # 添加到 UI
        index = len(self.config_mgr.get_mappings()) - 1
        self._add_mapping_to_ui(index, nas_path, drive)

        # 清空输入
        self.entry_path.delete(0, tk.END)
        self.var_drive.set("")

        self._log(f"已添加映射：{drive} -> {nas_path}", "success")

    def _delete_mapping(self, index):
        """删除映射配置"""
        mappings = self.config_mgr.get_mappings()
        if index >= len(mappings):
            return

        m = mappings[index]
        drive = m['drive']
        nas_path = m['nas_path']

        # 先断开连接（无论是否连接成功都执行）
        try:
            delete_connection(drive)
        except Exception:
            pass

        # 从配置删除
        self.config_mgr.remove_mapping(index)

        # 重新索引剩余映射（会自动重建 UI）
        self._rebuild_mappings_ui()

        self._log(f"已删除映射：{drive} -> {nas_path}", "warning")

    def _rebuild_mappings_ui(self):
        """重建映射 UI"""
        # 清空现有 UI
        for widget in self.mappings_container.winfo_children():
            widget.destroy()
        self._mapping_frames.clear()

        # 重新加载
        mappings = self.config_mgr.get_mappings()
        for i, m in enumerate(mappings):
            self._add_mapping_to_ui(i, m['nas_path'], m['drive'], m.get('enabled', True))

    def _disconnect_drive(self, drive):
        """断开指定驱动器的连接"""
        def work():
            self.root.after(0, lambda: self.status_indicator_label.configure(text=f"⏳ 断开 {drive}...", fg=COLORS['text_muted']))
            logger.info(f"断开连接：{drive}")
            delete_connection(drive)
            self.root.after(0, lambda: self.status_indicator_label.configure(text=f"✓ {drive} 已断开", fg=COLORS['success']))
            self.root.after(1000, lambda: self.status_indicator_label.configure(text=""))
            self.root.after(500, self._update_all_status)
        threading.Thread(target=work, daemon=True).start()

    def _do_disconnect_all(self):
        """断开所有连接"""
        mappings = self.config_mgr.get_mappings()
        if not mappings:
            messagebox.showwarning("警告", "没有映射配置")
            return

        def work():
            self.root.after(0, lambda: self._set_disconnect_all_state(True))
            try:
                for m in mappings:
                    drive = m['drive']
                    self.root.after(0, lambda d=drive: self.status_indicator_label.configure(text=f"⏳ 断开 {d}...", fg=COLORS['text_muted']))
                    logger.info(f"断开连接：{drive}")
                    delete_connection(drive)
                    self._log(f"{drive} 已断开", "warning")

                self.root.after(0, lambda: self.status_indicator_label.configure(text="✓ 已全部断开", fg=COLORS['success']))
                self.root.after(1000, lambda: self.status_indicator_label.configure(text=""))
                self.root.after(500, self._update_all_status)
            except Exception as e:
                logger.error(f"断开所有连接失败：{e}")
                self.root.after(0, lambda: messagebox.showerror("错误", f"断开所有连接失败:\n{e}"))
            finally:
                self.root.after(500, lambda: self._set_disconnect_all_state(False))

        threading.Thread(target=work, daemon=True).start()

    def _set_disconnect_all_state(self, disconnecting: bool):
        """设置断开所有按钮的状态"""
        if disconnecting:
            self.btn_disconnect_all.configure(state=tk.DISABLED, text="断开中...", bg=COLORS['btn_gray'])
        else:
            self.btn_disconnect_all.configure(state=tk.NORMAL, text="断开所有", bg=COLORS['btn_orange'])

    def _connect_single_mapping(self, index):
        """连接单个映射"""
        mappings = self.config_mgr.get_mappings()
        if index >= len(mappings):
            return

        password = (self.entry_pass.get() or "").strip()
        if not password:
            messagebox.showwarning("警告", "请先输入密码")
            return

        sys_user = get_system_username()
        target_user = determine_target_user(sys_user, None if self.var_user.get().lower() in ("自动", "") else self.var_user.get())

        m = mappings[index]
        nas_path = m['nas_path']
        drive = m['drive']

        def work():
            self.root.after(0, lambda: self.status_indicator_label.configure(text=f"⏳ 连接 {drive}...", fg=COLORS['text_muted']))
            logger.info(f"连接 {drive} -> {nas_path}")

            if not is_drive_valid(drive):
                delete_connection(drive)
                success, err_msg = create_connection(drive, nas_path, target_user, password)
                if success:
                    self.root.after(0, lambda: self.status_indicator_label.configure(text=f"✓ {drive} 成功", fg=COLORS['success']))
                    logger.info(f"{drive} 连接成功")
                    self._log(f"{drive} -> {nas_path} 连接成功", "success")
                else:
                    self.root.after(0, lambda: self.status_indicator_label.configure(text=f"✗ {drive} 失败", fg=COLORS['error']))
                    logger.error(f"{drive} 连接失败：{err_msg}")
                    self._log(f"{drive} -> {nas_path} 连接失败：{err_msg}", "error")
                    self.root.after(0, lambda: messagebox.showerror("连接失败", f"{drive} 连接失败:\n{err_msg}"))
            else:
                logger.info(f"{drive} 已存在连接")
                self._log(f"{drive} 已存在连接", "info")

            self.root.after(500, self._update_all_status)
            self.root.after(1000, lambda: self.status_indicator_label.configure(text=""))

        threading.Thread(target=work, daemon=True).start()

    def _open_drive(self, drive: str):
        try:
            os.startfile(drive)
            logger.info(f"已打开 {drive}")
            self._log(f"已打开 {drive}", "success")
        except Exception as e:
            logger.error(f"无法打开 {drive}: {e}")
            messagebox.showerror("打开失败", f"无法打开 {drive}:\n{e}")

    def _update_all_status(self):
        """更新所有映射的状态"""
        for idx, mapping in self._mapping_frames.items():
            drive = mapping['drive']
            ui = mapping['ui']
            is_connected = is_drive_valid(drive)

            if is_connected:
                ui['status_var'].set("已连接")
                ui['canvas'].itemconfig(ui['indicator'], fill=COLORS['success'], outline=COLORS['success'])
                ui['btn_open'].configure(state=tk.NORMAL, bg=COLORS['emerald'])
                ui['btn_disconnect'].configure(state=tk.NORMAL, bg=COLORS['btn_orange'])
                ui['btn_connect'].configure(state=tk.DISABLED, bg=COLORS['text_muted'])
                self._bind_hover(ui['btn_disconnect'], COLORS['btn_orange'], COLORS['btn_orange_hover'])
            else:
                ui['status_var'].set("未连接")
                ui['canvas'].itemconfig(ui['indicator'], fill=COLORS['error'], outline=COLORS['error'])
                ui['btn_open'].configure(state=tk.DISABLED, bg=COLORS['text_muted'])
                ui['btn_disconnect'].configure(state=tk.DISABLED, bg=COLORS['text_muted'])
                ui['btn_connect'].configure(state=tk.NORMAL, bg=COLORS['btn_blue'])
                self._bind_hover(ui['btn_connect'], COLORS['btn_blue'], COLORS['btn_blue_hover'])

    def _do_connect(self):
        if self._connecting:
            return

        password = (self.entry_pass.get() or "").strip()
        sys_user = get_system_username()
        target_user = determine_target_user(sys_user, None if self.var_user.get().lower() in ("自动", "") else self.var_user.get())

        if not password:
            messagebox.showwarning("警告", "请先输入 NAS 密码")
            return

        mappings = self.config_mgr.get_mappings()
        if not mappings:
            messagebox.showwarning("警告", "请先添加映射配置")
            return

        # 清空连接结果
        self._connect_results = {}

        def work():
            self.root.after(0, lambda: self._set_connecting(True))
            has_error = False
            error_messages = []

            try:
                for i, m in enumerate(mappings):
                    nas_path = m['nas_path']
                    drive = m['drive']

                    # 更新状态显示
                    self.root.after(0, lambda d=drive: self.status_indicator_label.configure(text=f"⏳ 连接 {d}...", fg=COLORS['text_muted']))
                    logger.info(f"步骤：连接 {drive} -> {nas_path}")

                    if not is_drive_valid(drive):
                        delete_connection(drive)
                        success, err_msg = create_connection(drive, nas_path, target_user, password)
                        if success:
                            self.root.after(0, lambda d=drive: self.status_indicator_label.configure(text=f"✓ {d} 成功", fg=COLORS['success']))
                            logger.info(f"{drive} 连接成功")
                            self._connect_results[drive] = True
                            self._log(f"{drive} -> {nas_path} 连接成功", "success")
                        else:
                            has_error = True
                            error_messages.append(f"{drive}: {err_msg if err_msg else '连接失败'}")
                            self.root.after(0, lambda d=drive: self.status_indicator_label.configure(text=f"✗ {d} 失败", fg=COLORS['error']))
                            logger.error(f"{drive} 连接失败：{err_msg}")
                            self._log(f"{drive} -> {nas_path} 连接失败：{err_msg}", "error")
                            continue
                    else:
                        logger.info(f"{drive} 已存在连接")
                        self._connect_results[drive] = True
                        self._log(f"{drive} 已存在连接", "info")

                    # 更新该映射的状态
                    self.root.after(500, self._update_all_status)

                # 完成
                if has_error:
                    self.root.after(0, lambda: self.status_indicator_label.configure(text="✗ 部分失败", fg=COLORS['error']))
                    logger.error(f"连接完成，但有错误")
                    self._log("连接完成，部分映射失败", "error")
                    error_detail = "\n".join(error_messages)
                    self.root.after(0, lambda: messagebox.showerror("连接失败", f"以下映射连接失败:\n{error_detail}"))
                else:
                    self.root.after(0, lambda: self.status_indicator_label.configure(text="✓ 连接完成", fg=COLORS['success']))
                    logger.info("所有连接完成")
                    self._log("所有连接任务完成", "success")
                    # 连接成功后，根据 checkbox 状态保存密码
                    if self.var_save_password.get():
                        self.config_mgr.set_saved_password(password)
                        logger.info("密码已保存")
                    else:
                        self.config_mgr.set_saved_password(None)

                self.root.after(1500, lambda: self.status_indicator_label.configure(text=""))
                self.root.after(500, self._update_all_status)

            except Exception as e:
                error_msg = f"连接失败：{e}"
                logger.error(error_msg)
                self._log(error_msg, "error")
                self.root.after(0, lambda: self.status_indicator_label.configure(text="✗ 连接异常", fg=COLORS['error']))
                messagebox.showerror("错误", error_msg)
            finally:
                self.root.after(500, lambda: self._set_connecting(False))

        t = threading.Thread(target=work, daemon=True)
        t.start()

    def _set_connecting(self, connecting: bool):
        self._connecting = connecting
        if connecting:
            self.btn_connect.configure(state=tk.DISABLED, text="连接中...", bg=COLORS['btn_gray'])
        else:
            self.btn_connect.configure(state=tk.NORMAL, text="连接所有", bg=COLORS['btn_blue'])

    def _toggle_startup(self):
        if self.var_startup.get():
            if add_to_startup():
                logger.info("已添加开机自动运行")
                messagebox.showinfo("开机启动", "已添加开机自动运行")
            else:
                logger.error("添加开机启动失败")
                messagebox.showerror("错误", "添加开机启动失败")
                self.var_startup.set(False)
        else:
            if remove_from_startup():
                logger.info("已取消开机自动运行")
                messagebox.showinfo("开机启动", "已取消开机自动运行")
            else:
                logger.warning("取消开机启动失败或未找到启动项")

    def run(self):
        self.root.mainloop()

def main():
    app = OpenNetDriveApp()
    app.run()

if __name__ == "__main__":
    main()
