# -*- coding: utf-8 -*-
"""
openNetDrive 打包脚本
使用 PyInstaller 打包成独立可执行文件
"""
import os
import subprocess
import shutil
import sys

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
RELEASE_DIR = os.path.join(PROJECT_ROOT, "release")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")

def run_command(cmd, description):
    """运行命令并打印输出"""
    print(f"\n{'='*60}")
    print(f">> {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"错误：{description} 失败")
        sys.exit(1)
    return result

def clean_build_dirs():
    """清理构建目录"""
    print("\n清理旧的构建目录...")
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"  已删除：{dir_path}")

def create_release_dir():
    """创建 release 目录"""
    if os.path.exists(RELEASE_DIR):
        shutil.rmtree(RELEASE_DIR)
    os.makedirs(RELEASE_DIR)
    print(f"创建 release 目录：{RELEASE_DIR}")

def copy_extra_files():
    """复制额外的文件到 release 目录"""
    # 复制 config.json 模板
    config_src = os.path.join(PROJECT_ROOT, "config.json")
    config_dst = os.path.join(RELEASE_DIR, "config.json")
    if os.path.exists(config_src):
        shutil.copy2(config_src, config_dst)
        print(f"  已复制：config.json")

    # 复制 README.md
    readme_src = os.path.join(PROJECT_ROOT, "README.md")
    readme_dst = os.path.join(RELEASE_DIR, "README.md")
    if os.path.exists(readme_src):
        shutil.copy2(readme_src, readme_dst)
        print(f"  已复制：README.md")

def main():
    print("\n" + "="*60)
    print("openNetDrive 打包程序")
    print("="*60)

    # 1. 检查 PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller 版本：{PyInstaller.__version__}")
    except ImportError:
        print("未检测到 PyInstaller，正在安装...")
        run_command("pip install pyinstaller", "安装 PyInstaller")

    # 2. 清理旧构建
    clean_build_dirs()

    # 3. 创建 release 目录
    create_release_dir()

    # 4. 运行 PyInstaller
    # --onefile: 打包成单个可执行文件
    # --windowed: 不显示控制台窗口
    # --icon: 图标（可选）
    # --name: 输出文件名
    # --add-data: 包含额外文件（配置文件）
    cmd = (
        f'pyinstaller --onefile --windowed '
        f'--name openNetDrive '
        f'--distpath "{DIST_DIR}" '
        f'--workpath "{BUILD_DIR}" '
        f'--specpath "{PROJECT_ROOT}" '
        f'--add-data "config.json;." '
        f'"openNetDrive.py"'
    )

    run_command(cmd, "PyInstaller 打包")

    # 5. 复制文件到 release 目录
    print("\n复制文件到 release 目录...")

    # 复制主程序
    exe_src = os.path.join(DIST_DIR, "openNetDrive.exe")
    exe_dst = os.path.join(RELEASE_DIR, "openNetDrive.exe")
    shutil.copy2(exe_src, exe_dst)
    print(f"  已复制：openNetDrive.exe")

    # 复制额外文件
    copy_extra_files()

    # 6. 创建使用说明文件
    usage_txt = os.path.join(RELEASE_DIR, "使用说明.txt")
    with open(usage_txt, "w", encoding="utf-8") as f:
        f.write("""openNetDrive - Windows NAS 网络驱动器自动连接工具

使用方法：
1. 双击运行 openNetDrive.exe
2. 输入 NAS 密码
3. 点击「连接」按钮

注意事项：
- 首次运行会自动生成 config.json 配置文件
- 日志文件保存在 logs 目录
- 支持一键添加开机自启

配置文件说明：
- config.json: 映射配置、用户映射关系等
- 密码使用 base64 编码存储，请勿分享配置文件

技术支持：
详见 README.md
""")
    print(f"  已创建：使用说明.txt")

    print("\n" + "="*60)
    print("打包完成！")
    print(f"发布目录：{RELEASE_DIR}")
    print("="*60)

    # 打开 release 目录
    os.startfile(RELEASE_DIR)

if __name__ == "__main__":
    main()
