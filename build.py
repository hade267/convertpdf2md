"""
Build script - Đóng gói PDF to Markdown Converter thành file .exe
Sử dụng PyInstaller để tạo standalone executable.

Cách dùng:
    python build.py
"""

import subprocess
import sys
import os

def build():
    """Chạy PyInstaller để đóng gói ứng dụng."""

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "PDF2MD",
        "--clean",

        # Thu thập data
        "--collect-all", "pymupdf",
        "--collect-all", "pymupdf4llm",
        "--collect-all", "flet",
        "--collect-all", "litellm",

        # Hidden imports
        "--hidden-import", "pymupdf",
        "--hidden-import", "pymupdf4llm",
        "--hidden-import", "fitz",
        "--hidden-import", "flet",
        "--hidden-import", "litellm",
        "--hidden-import", "converter",
        "--hidden-import", "app",
        "--hidden-import", "ai_processor",

        # Thêm source files
        "--add-data", f"converter.py{os.pathsep}.",
        "--add-data", f"app.py{os.pathsep}.",
        "--add-data", f"ai_processor.py{os.pathsep}.",

        # Entry point
        "main.py",
    ]

    print("🔧 Đang đóng gói ứng dụng...")
    print(f"📦 Lệnh: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

    if result.returncode == 0:
        exe_path = os.path.join("dist", "PDF2MD.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✅ Đóng gói thành công!")
            print(f"📁 File exe: {os.path.abspath(exe_path)}")
            print(f"📏 Kích thước: {size_mb:.1f} MB")
        else:
            print(f"\n✅ Build xong! Kiểm tra thư mục dist/")
    else:
        print(f"\n❌ Build thất bại (exit code: {result.returncode})")
        sys.exit(1)

if __name__ == "__main__":
    build()
