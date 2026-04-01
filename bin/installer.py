#!/usr/bin/env python3
# Playwright Chromium浏览器安装程序

import os
import sys
import subprocess
import playwright


def get_browser_install_path():
    """获取浏览器安装路径"""
    # 使用项目根目录下的res/browsers目录
    browsers_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "res", "browsers"))
    os.makedirs(browsers_path, exist_ok=True)
    return str(browsers_path)


def install_chromium_browser():
    """安装Chromium浏览器"""
    print("正在安装Chromium浏览器...")
    
    # 设置浏览器安装路径
    browsers_path = get_browser_install_path()
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
    
    # 直接调用playwright install chromium命令
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"]
    )
    
    return result.returncode == 0


if __name__ == "__main__":
    install_chromium_browser()