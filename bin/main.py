#  程序入口、初始化、交互界面V1.1 (Playwright版)
import os
import asyncio

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from base_learn import BaseLearn
from ui_handlers import UIHandlers

async def run_selected_script():
    web_address = "https://www.sqgj.gov.cn/index"
    page = None
    context = None
    
    # 显示系统原生通知
    import subprocess
    import platform
    
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows使用PowerShell发送通知（使用System.Windows.Forms）
            try:
                result = subprocess.run([
                    "powershell", "-NoProfile", "-Command",
                    "try { Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $form = New-Object System.Windows.Forms.Form; $form.WindowState = [System.Windows.Forms.FormWindowState]::Minimized; $form.ShowInTaskbar = $false; $notify = New-Object System.Windows.Forms.NotifyIcon; $notify.Icon = [System.Drawing.SystemIcons]::Information; $notify.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info; $notify.BalloonTipTitle = '浏览器启动中'; $notify.BalloonTipText = '正在启动浏览器，请耐心等待...'; $notify.Visible = $true; $notify.ShowBalloonTip(5000); Start-Sleep -Milliseconds 100; $notify.Dispose(); $form.Close(); } catch { Write-Error $_.Exception.Message }"
                ], timeout=5, text=True, capture_output=True)
                
                if result.returncode != 0:
                    print(f"通知发送失败: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("通知发送超时")
            except Exception as e:
                print(f"通知发送异常: {e}")
                
        elif system == "Linux":
            # Linux使用notify-send发送通知
            try:
                subprocess.run([
                    "notify-send", "-i", "info", "-t", "5000",
                    "浏览器启动中", "正在启动浏览器，请耐心等待..."
                ], timeout=2, check=True)
            except Exception as e:
                print(f"Linux通知发送失败: {e}")
                
    except Exception as e:
        print(f"通知系统初始化失败: {e}")
    
    try:
        # 获取项目根目录下的res文件夹路径
        res_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "res"))
        os.makedirs(res_dir, exist_ok=True)  # 确保res目录存在
        
        # 设置环境变量，指定Playwright浏览器路径
        browsers_path = os.path.join(res_dir, "browsers")
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
        
        # 检查浏览器是否已安装
        chromium_dir = os.path.join(browsers_path, "chromium-*")
        if not any(os.path.exists(os.path.join(browsers_path, d)) for d in os.listdir(browsers_path) if d.startswith("chromium-")):
            print("未检测到浏览器，请先下载chromium-1208浏览器到res/browsers目录")
            return
        
        # 设置用户数据目录
        user_data_dir = os.path.join(res_dir, "chrome-user-data")
        
        # 使用Stealth方式创建异步playwright上下文
        async with Stealth().use_async(async_playwright()) as p:
            # 使用持久化上下文
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                viewport={'width': 1900, 'height': 900},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--window-position=0,0',
                    '--disable-background-timer-throttling',  # 防止后台定时器节流
                    '--disable-renderer-backgrounding',       # 防止渲染器后台化
                    '--disable-backgrounding-occluded-windows', # 防止被遮挡窗口后台化
                ]
            )
            
            # 获取持久化上下文中已存在的页面，如果没有则创建新页面
            pages = context.pages
            if pages:
                page = pages[0]
            else:
                page = await context.new_page()
            
            # 访问目标网站并等待页面完全加载
            print("正在加载目标网站...")
            await page.goto(web_address, wait_until='networkidle')
                        
            # 初始化UI处理器（在网页上显示悬浮窗）
            ui_handler = UIHandlers(page)
            # 异步初始化UI处理器
            await ui_handler.init_async()
            
            # 显示欢迎信息
            await ui_handler.print_to_window("陕西干部网络学院刷课工具")
            
            while True:
                # 检查浏览器是否仍然有效
                try:
                    if page and not page.is_closed():
                        await page.evaluate("1 + 1")
                except:
                    print("浏览器已关闭，退出程序")
                    break
                
                try:
                    # 显示菜单选项
                    menu_message =  "\n输入 0 完成网络自学\n"
                    menu_message += "输入 整数n 完成第n个专题学习\n"
                    menu_message += "输入 A 学习全部课程\n"
                    menu_message += "输入 Q 退出程序"
                    await ui_handler.print_to_window(menu_message)
                    
                    # 显示输入框并获取用户输入
                    choice = await ui_handler.input_from_window("\n请登录并选课后输入功能编号：")
                except Exception as e:
                    print(f"浏览器已关闭，退出程序: {e}")
                    break
                
                # 处理用户输入
                if choice and choice.lower() == 'q':
                    await ui_handler.print_to_window("程序退出")
                    break
                elif choice and choice.lower() == 'a':
                    try:
                        await ui_handler.print_to_window("开始学习所有课程...")
                        for i in range(10):
                            try:
                                if i == 0:
                                    await ui_handler.print_to_window("开始完成网络自学...")
                                else:
                                    await ui_handler.print_to_window(f"开始学习第{i}个专题...")
                                learner = BaseLearn(page, ui_handler=ui_handler)  # 使用page而不是driver
                                await learner.run_learning_cycle(button_index=i)
                            except Exception as e:
                                await ui_handler.print_to_window(f"\n专题 {i} 已学完或发生错误: {str(e)}")
                                await ui_handler.print_to_window("继续执行下一个专题...")
                    except Exception as e:
                        print(f"浏览器已关闭，退出程序")
                        break
                else:
                    try:
                        if choice:
                            choice = int(choice)
                            if 0 <= choice <= 9:
                                if choice == 0:
                                    await ui_handler.print_to_window("开始完成网络自学...")
                                else:
                                    await ui_handler.print_to_window(f"开始学习第{choice}个专题...")
                                learner = BaseLearn(page, ui_handler=ui_handler)
                                await learner.run_learning_cycle(button_index=choice)
                            else:
                                await ui_handler.print_to_window("请输入0-9之间的整数")
                        else:
                            await ui_handler.print_to_window("请输入有效的整数（0-9）或A（执行所有选项）")
                    except ValueError:
                        await ui_handler.print_to_window("请输入有效的整数（0-9）或A（执行所有选项）")
                    except Exception as e:
                        print(f"浏览器已关闭，退出程序")
                        break
            
            # 程序正常退出时关闭浏览器
            if context:
                await context.close()
        
    except Exception as e:
        print(f"浏览器启动失败: {e}")
        print("请确保已在res/browsers目录中安装了Playwright浏览器")
        return

    # 程序正常退出时关闭浏览器
    if context:
        await context.close()


if __name__ == "__main__":
    asyncio.run(run_selected_script())