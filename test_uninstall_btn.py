# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

COLORS = {
    'btn_red': '#dc2626',
    'btn_gray': '#6b7280',
    'bg_white': '#ffffff',
    'text_muted': '#6b9080',
    'text_primary': '#064e3b',
    'warning': '#d97706',
    'btn_red_hover': '#b91c1c',
    'bg_secondary': '#d1fae5',
    'emerald': '#047857',
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

class TestApp:
    def __init__(self, root):
        self.root = root
        root.title("openNetDrive 测试")
        root.geometry("800x500+300+200")

        # 主框架
        main = tk.Frame(root, bg=COLORS['bg_white'])
        main.pack(fill=tk.BOTH, expand=True)

        # 标题
        tk.Label(main, text="openNetDrive 测试", font=('Microsoft YaHei UI', 16, 'bold'),
                 fg=COLORS['emerald'], bg=COLORS['bg_white']).pack(pady=20)

        # 按钮行
        btn_row = tk.Frame(main, bg=COLORS['bg_white'])
        btn_row.pack(fill=tk.X, padx=20, pady=10)

        # 左侧框架
        left_frame = tk.Frame(btn_row, bg=COLORS['bg_white'])
        left_frame.pack(side=tk.LEFT)

        # 开机自启复选框
        self.var_startup = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(left_frame, text="开机自动运行", variable=self.var_startup,
                           font=FONTS['label'], fg=COLORS['text_muted'],
                           bg=COLORS['bg_white'])
        cb.pack(side=tk.LEFT)

        # 卸载按钮
        self.btn_uninstall = tk.Button(left_frame, text="卸载软件", font=FONTS['label'],
                                       fg=COLORS['btn_red'], bg=COLORS['bg_white'],
                                       activeforeground=COLORS['btn_red'], activebackground=COLORS['bg_white'],
                                       relief=tk.SOLID, bd=1, padx=12, pady=4, cursor='hand2',
                                       command=self._do_uninstall)
        self.btn_uninstall.pack(side=tk.LEFT, padx=(20, 0))
        print("卸载按钮已创建")

        # 右侧按钮
        right_frame = tk.Frame(btn_row, bg=COLORS['bg_white'])
        right_frame.pack(side=tk.RIGHT)

        btn = tk.Button(right_frame, text="测试按钮", font=FONTS['button'],
                       bg=COLORS['btn_red'], fg=COLORS['bg_white'],
                       command=lambda: print("测试"))
        btn.pack(side=tk.LEFT)

    def _do_uninstall(self):
        print("卸载按钮被点击!")
        dialog = tk.Toplevel(self.root)
        dialog.title("确认卸载")
        dialog.withdraw()

        main_frame = tk.Frame(dialog, bg=COLORS['bg_white'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="卸载确认", font=('Microsoft YaHei UI', 14, 'bold'),
                 fg=COLORS['btn_red'], bg=COLORS['bg_white']).pack(anchor=tk.W)

        tk.Label(main_frame, text="即将卸载...", font=FONTS['label'],
                 fg=COLORS['text_muted'], bg=COLORS['bg_white']).pack(anchor=tk.W, pady=10)

        var_keep = tk.BooleanVar(value=True)
        tk.Checkbutton(main_frame, text="保留配置", variable=var_keep,
                      font=FONTS['label'], bg=COLORS['bg_white']).pack(anchor=tk.W)

        btn_frame = tk.Frame(main_frame, bg=COLORS['bg_white'])
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=15)

        def on_confirm():
            print("确认卸载!")
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_cancel = tk.Button(btn_frame, text="取消", font=FONTS['button'],
                              bg=COLORS['btn_gray'], fg=COLORS['bg_white'],
                              command=on_cancel)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

        btn_confirm = tk.Button(btn_frame, text="确认卸载", font=FONTS['button'],
                               bg=COLORS['btn_red'], fg=COLORS['bg_white'],
                               command=on_confirm)
        btn_confirm.pack(side=tk.RIGHT, padx=5)

        # 更新后显示
        dialog.update_idletasks()
        w, h = 400, 250

        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2

        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = TestApp(root)
    print("应用启动，请点击'卸载软件'按钮测试")
    root.mainloop()
