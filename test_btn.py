# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox

COLORS = {
    'btn_red': '#dc2626',
    'btn_gray': '#6b7280',
    'bg_white': '#ffffff',
    'text_muted': '#6b9080',
    'text_primary': '#064e3b',
    'warning': '#d97706',
    'bg_secondary': '#d1fae5',
}

def test_dialog():
    root = tk.Tk()
    root.title("主窗口")
    root.geometry("600x400+300+200")

    def open_dialog():
        dialog = tk.Toplevel(root)
        dialog.title("确认卸载")
        dialog.resizable(False, False)

        # 使用 grid 布局
        dialog.grid_rowconfigure(0, weight=0)
        dialog.grid_rowconfigure(1, weight=0)
        dialog.grid_columnconfigure(0, weight=1)

        # 内容框架
        content = tk.Frame(dialog, bg=COLORS['bg_white'])
        content.grid(row=0, column=0, sticky='ew', padx=20, pady=20)

        tk.Label(content, text="卸载确认", font=('Microsoft YaHei UI', 14, 'bold'),
                 fg=COLORS['btn_red'], bg=COLORS['bg_white']).pack(anchor=tk.W)
        tk.Label(content, text="即将卸载...", font=('Microsoft YaHei UI', 10),
                 fg=COLORS['text_muted'], bg=COLORS['bg_white']).pack(anchor=tk.W, pady=10)
        tk.Label(content, text="• 开机启动项", font=('Microsoft YaHei UI', 10),
                 fg=COLORS['text_primary'], bg=COLORS['bg_white']).pack(anchor=tk.W)
        tk.Label(content, text="• 快捷方式", font=('Microsoft YaHei UI', 10),
                 fg=COLORS['text_primary'], bg=COLORS['bg_white']).pack(anchor=tk.W)

        var1 = tk.BooleanVar(value=True)
        var2 = tk.BooleanVar(value=True)
        tk.Checkbutton(content, text="保留配置", variable=var1,
                       bg=COLORS['bg_white']).pack(anchor=tk.W, pady=5)
        tk.Checkbutton(content, text="保留日志", variable=var2,
                       bg=COLORS['bg_white']).pack(anchor=tk.W)
        tk.Label(content, text="\n注意：程序文件保留", font=('Microsoft YaHei UI', 8),
                 fg=COLORS['warning'], bg=COLORS['bg_white']).pack(anchor=tk.W, pady=10)

        # 按钮框架 - grid 底部
        btn_frame = tk.Frame(dialog, bg=COLORS['bg_white'])
        btn_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 20))

        def on_cancel():
            dialog.destroy()
        def on_confirm():
            print("确认")
            dialog.destroy()

        btn_confirm = tk.Button(btn_frame, text="确认卸载", font=('Microsoft YaHei UI', 10, 'bold'),
                                fg='#ffffff', bg='#dc2626', relief=tk.RAISED, bd=2,
                                padx=20, pady=8, command=on_confirm)
        btn_confirm.pack(side=tk.RIGHT, padx=5)

        btn_cancel = tk.Button(btn_frame, text="取消", font=('Microsoft YaHei UI', 10),
                               fg='#ffffff', bg='#6b7280', relief=tk.RAISED, bd=2,
                               padx=20, pady=8, command=on_cancel)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

        # 更新后设置位置
        root.update_idletasks()
        dialog.update_idletasks()

        w, h = 420, 360
        x = root.winfo_x() + (root.winfo_width() - w) // 2
        y = root.winfo_y() + (root.winfo_height() - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        dialog.attributes('-topmost', True)
        dialog.transient(root)
        dialog.grab_set()

    tk.Label(root, text="点击按钮测试对话框", pady=20).pack()
    tk.Button(root, text="打开对话框", command=open_dialog,
              bg=COLORS['btn_red'], fg='white', padx=20, pady=10).pack()

    root.mainloop()

if __name__ == "__main__":
    test_dialog()
