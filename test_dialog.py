# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox

COLORS = {
    'btn_red': '#dc2626',
    'btn_gray': '#6b7280',
    'bg_white': '#ffffff',
    'text_muted': '#6b9080',
    'text_primary': '#064e3b',
    'warning': '#d97706',
    'btn_red_hover': '#b91c1c',
    'bg_secondary': '#d1fae5',
}

FONTS = {
    'label': ('Microsoft YaHei UI', 10),
    'button': ('Microsoft YaHei UI', 10),
    'caption': ('Microsoft YaHei UI', 8),
}

def _bind_hover(btn, normal, hover):
    def on_enter(_):
        btn.configure(bg=hover)
    def on_leave(_):
        btn.configure(bg=normal)
    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)

def create_uninstall_dialog(root):
    """创建卸载对话框"""
    dialog = tk.Toplevel(root)
    dialog.title("确认卸载")

    # 隐藏窗口直到完全准备好
    dialog.withdraw()

    # 主框架
    main_frame = tk.Frame(dialog, bg=COLORS['bg_white'])
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # 标题
    tk.Label(main_frame, text="卸载确认", font=('Microsoft YaHei UI', 14, 'bold'),
             fg=COLORS['btn_red'], bg=COLORS['bg_white']).pack(anchor=tk.W)

    tk.Label(main_frame, text="即将卸载 openNetDrive，将删除以下内容:",
             font=FONTS['label'], fg=COLORS['text_muted'],
             bg=COLORS['bg_white']).pack(anchor=tk.W, pady=(15, 10))

    # 选项框架
    options_frame = tk.Frame(main_frame, bg=COLORS['bg_white'])
    options_frame.pack(fill=tk.X, anchor=tk.W)

    tk.Label(options_frame, text="  • 开机启动项", font=FONTS['label'],
             fg=COLORS['text_primary'], bg=COLORS['bg_white'],
             anchor=tk.W).pack(fill=tk.X)
    tk.Label(options_frame, text="  • 桌面/开始菜单快捷方式", font=FONTS['label'],
             fg=COLORS['text_primary'], bg=COLORS['bg_white'],
             anchor=tk.W).pack(fill=tk.X)

    var_keep_config = tk.BooleanVar(value=True)
    var_keep_logs = tk.BooleanVar(value=True)

    tk.Checkbutton(options_frame, text="  保留配置文件 (config.json)",
                   font=FONTS['label'], fg=COLORS['text_primary'],
                   bg=COLORS['bg_white'], selectcolor=COLORS['bg_secondary'],
                   variable=var_keep_config, anchor=tk.W).pack(fill=tk.X, pady=(10, 0))

    tk.Checkbutton(options_frame, text="  保留日志文件 (logs/*)",
                   font=FONTS['label'], fg=COLORS['text_primary'],
                   bg=COLORS['bg_white'], selectcolor=COLORS['bg_secondary'],
                   variable=var_keep_logs, anchor=tk.W).pack(fill=tk.X)

    tk.Label(main_frame, text="\n注意：程序文件将保留，可手动删除整个目录。",
             font=FONTS['caption'], fg=COLORS['warning'],
             bg=COLORS['bg_white'], wraplength=360,
             justify=tk.LEFT).pack(anchor=tk.W, fill=tk.X, pady=(10, 0))

    # 按钮框架
    btn_frame = tk.Frame(main_frame, bg=COLORS['bg_white'])
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))

    def on_cancel():
        dialog.destroy()

    def on_confirm():
        print("确认卸载!")
        dialog.destroy()

    # 确认卸载按钮
    btn_confirm = tk.Button(btn_frame, text="确认卸载", font=FONTS['button'],
                            fg=COLORS['bg_white'], bg=COLORS['btn_red'],
                            activeforeground=COLORS['bg_white'], activebackground=COLORS['btn_red_hover'],
                            relief=tk.FLAT, bd=0, padx=24, pady=6, cursor='hand2',
                            command=on_confirm)
    btn_confirm.pack(side=tk.RIGHT, padx=(5, 0))
    _bind_hover(btn_confirm, COLORS['btn_red'], COLORS.get('btn_red_hover', COLORS['btn_red']))

    # 取消按钮
    btn_cancel = tk.Button(btn_frame, text="取消", font=FONTS['button'],
                           fg=COLORS['bg_white'], bg=COLORS['btn_gray'],
                           activeforeground=COLORS['bg_white'], activebackground=COLORS['btn_gray'],
                           relief=tk.FLAT, bd=0, padx=24, pady=6, cursor='hand2',
                           command=on_cancel)
    btn_cancel.pack(side=tk.RIGHT, padx=(5, 0))
    _bind_hover(btn_cancel, COLORS['btn_gray'], '#555555')

    # 对话框居中 - 强制更新后获取实际大小
    dialog.update_idletasks()
    actual_width = dialog.winfo_reqwidth()
    actual_height = dialog.winfo_reqheight()

    # 如果自动计算的高度太小，使用估算值
    if actual_height < 200:
        actual_height = 280

    # 使用 Toplevel 的 transient 实现相对于父窗口居中
    dialog.transient(root)

    # 手动设置几何位置（在 transient 之后）
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    x = root_x + (root_width - 400) // 2
    y = root_y + (root_height - actual_height) // 2

    dialog.geometry(f"400x{actual_height}+{x}+{y}")
    dialog.resizable(False, False)
    dialog.deiconify()  # 显示窗口

    # 强制聚焦
    dialog.focus_set()

    return dialog

def main():
    root = tk.Tk()
    root.title("测试主窗口")
    root.geometry("600x400+300+200")

    tk.Label(root, text="点击按钮测试卸载对话框", font=FONTS['label']).pack(pady=20)

    btn = tk.Button(root, text="打开卸载对话框", font=FONTS['button'],
                    bg=COLORS['btn_red'], fg=COLORS['bg_white'],
                    command=lambda: create_uninstall_dialog(root))
    btn.pack(pady=20)

    print("Starting main loop...")
    root.mainloop()

if __name__ == "__main__":
    main()
