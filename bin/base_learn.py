# 基础学习模块

import time

# 自定义异常,用于跳出循环
class SkipToNextCourse(Exception):
    pass

class BaseLearn:
    def __init__(self, page, max_attempts=50, ui_handler=None):
        self.page = page
        self.max_attempts = max_attempts
        self.ui_handler = ui_handler
        self.page_ui_handlers = {}  # 存储不同页面的UI处理器
        if ui_handler:
            self.page_ui_handlers[page] = ui_handler  # 为主页面注册UI处理器
    
# 修改print_message方法以支持目标页面
    async def print_message(self, message, end='\n', target_page=None):
        """统一的消息输出方法"""
        target_page = target_page if target_page is not None else self.page
        
        # 如果目标页面有对应的UIHandler，则使用它
        if target_page in self.page_ui_handlers:
            ui_handler = self.page_ui_handlers[target_page]
            await ui_handler.print_to_window(message, end=end)
        elif self.ui_handler:  # 否则使用默认UIHandler
            await self.ui_handler.print_to_window(message, end=end)
        else:
            print(message, end=end)
    
    async def input_message(self, message):
        """统一的输入方法"""
        if self.ui_handler:
            return await self.ui_handler.input_from_window(message)
        else:
            return input(message)
    
    async def new_window(self):
        """等待并切换到新标签页"""
        # 监听新页面的创建
        async with self.page.context.expect_page() as page_info:
            pass
        new_page = await page_info.value 
        
        print(f"检测到新页面打开: {new_page.url}")
        
        # 等待新页面加载完成
        await new_page.wait_for_load_state("domcontentloaded")
        
        # 额外等待，确保页面完全加载
        time.sleep(2)
        
        # 等待页面网络空闲
        try:
            await new_page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass  # 如果超时也继续
        
        # 在新标签页中也显示悬浮窗
        if self.ui_handler:
            # 为新页面创建UI处理器
            from ui_handlers import UIHandlers
            new_ui_handler = UIHandlers(new_page)
            # 异步初始化新页面的UI处理器
            await new_ui_handler.init_async()
            # 注册新页面的UI处理器
            self.page_ui_handlers[new_page] = new_ui_handler
            print(f"已为新页面初始化悬浮窗")
        
        return new_page

    
    async def click_learning_classroom(self):
        """点击学习课堂按钮"""
        try:
            # 等待页面完全加载（网络空闲状态）
            await self.page.wait_for_load_state("networkidle")
            
            # 等待关键元素出现，最多等待10秒
            await self.page.wait_for_selector('.item', timeout=10000, state="attached")
            
            # 获取主页面的item元素
            main_page_items = await self._get_main_page_elements('.item')
            if main_page_items and len(main_page_items) > 2:
                # 确保元素可见且可交互
                await main_page_items[2].scroll_into_view_if_needed()
                await main_page_items[2].wait_for_element_state("visible")
                
                # 点击元素
                await main_page_items[2].click()
                
                # 等待导航完成
                await self.page.wait_for_load_state("domcontentloaded")
                
                # 等待新页面内容出现（按钮元素）
                await self.page.wait_for_selector('.btn', timeout=10000, state="attached")
                
                print("成功点击学习课堂")
                return True
            else:
                print("未找到足够的item元素")
                return False
        except Exception as e:
            print(f"未找到课程。请检查是否已打开学习网站并登录。错误: {e}")
            return False
    
    async def _get_main_page_elements(self, selector):
        """获取主页面上的元素列表"""
        try:
            # 等待页面完全加载
            await self.page.wait_for_load_state("networkidle")
            
            # 等待选择器元素出现
            await self.page.wait_for_selector(selector, timeout=10000, state="attached")
            
            # 获取页面上的所有匹配元素
            elements = await self.page.query_selector_all(selector)
            return elements
        except Exception as e:
            print(f"获取页面元素时出错: {e}")
            return []
    
    async def click_enter_learning(self, button_index):
        """点击进入学习按钮"""
        print(f"尝试点击索引 {button_index}的按钮...")
        try:
            time.sleep(3)
            # 等待页面完全加载
            await self.page.wait_for_load_state("networkidle")
            
            # 等待包含"进入学习"文本的btn元素出现，最多等待10秒
            await self.page.wait_for_selector('div.btn:has-text("进入学习")', timeout=10000, state="attached")
            
            # 获取页面上所有包含"进入学习"文本的btn元素
            enter_learning_btns = await self.page.query_selector_all('div.btn:has-text("进入学习")')
            print(f"专题数量： {len(enter_learning_btns)} ")
            
            if button_index < len(enter_learning_btns):
                # 确保元素可见且可交互
                await enter_learning_btns[button_index].scroll_into_view_if_needed()
                await enter_learning_btns[button_index].wait_for_element_state("visible")
                
                # 直接点击指定索引的元素
                await enter_learning_btns[button_index].click()
                print(f"已点击索引 {button_index} 的进入学习按钮")            
                
                # 等待导航完成
                await self.page.wait_for_load_state("domcontentloaded")
                
                # 尝试等待新页面内容出现（开始学习按钮）
                try:
                    await self.page.wait_for_selector('.btn', timeout=10000, state="attached")
                except Exception as e:
                    print(f"等待新页面内容超时，但专题存在: {e}")
                    return True
                
                return True
            else:
                print(f"按钮索引 {button_index} 超出范围，找到 {len(enter_learning_btns)} 个进入学习按钮")
                return False
        except Exception as e:
            print(f"点击进入学习按钮时出错: {e}")
            return False
    
    async def click_start_learning(self, attempt):
        """点击专题内的开始学习/继续学习按钮"""
        try:
            # 等待页面结构改变
            time.sleep(3)
            await self.page.wait_for_load_state("domcontentloaded")
            
            # 优先查找包含"继续学习"文本的按钮
            continue_learning_btns = await self.page.query_selector_all('div.btn:has-text("继续学习")')
            if len(continue_learning_btns) > 0:
                await continue_learning_btns[0].click()
                print("已点击'继续学习'按钮")
                return True
            
            # 如果没有"继续学习"按钮，查找包含"开始学习"文本的按钮
            start_learning_btns = await self.page.query_selector_all('div.btn:has-text("开始学习")')
            if len(start_learning_btns) > 0:
                await start_learning_btns[0].click()
                print("已点击'开始学习'按钮")
                return True           
            return False       
        except Exception as e:
            print(f"点击开始学习按钮时出错: {e}")
            return False
    
    async def play_videos(self, target_page=None):
        """播放视频列表"""
        if target_page is None:
            target_page = self.page
            
        try:
            # 等待页面加载
            await target_page.wait_for_load_state("domcontentloaded")
            time.sleep(3)
            
            print("开始播放视频...")
            
            # 等待页面完全稳定
            await target_page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)
            
            # 在目标页面上直接查找item2元素
            item2_elements = await target_page.query_selector_all('.item2')
            if not item2_elements or len(item2_elements) == 0:
                print("未找到.item2元素，尝试等待...")
                time.sleep(5)
                item2_elements = await target_page.query_selector_all('.item2')
                
            if item2_elements and len(item2_elements) > 0:
                await item2_elements[0].click()
                print("已点击.item2元素")
            else:
                print("未找到.item2元素，跳过")
                return
            
            # 等待页面更新
            time.sleep(3)
            
            # 查找滚动视图中的视频
            scrollbar_views = await target_page.query_selector_all('.el-scrollbar__view')
            print(f"找到 {len(scrollbar_views)} 个滚动视图")
            
            for view in scrollbar_views:
                # 直接查找视频元素（class="vvitem"）
                video_elements = await view.query_selector_all('.vvitem')
                print(f"找到 {len(video_elements)} 个视频元素")
                
                if video_elements:
                    # 点击第一个视频元素
                    await video_elements[0].click()
                    print(f"点击了第一个视频元素")
                    time.sleep(3)
                    
                    # 循环检测当前视频是否播完
                    for i in range(len(video_elements)):
                        if i < len(video_elements):
                            # 获取当前视频文本
                            try:
                                current_video_text = await video_elements[i].inner_text()
                                if not current_video_text or current_video_text.strip() == '':
                                    current_video_text = f"视频 {i+1}"
                            except Exception as e:
                                current_video_text = f"视频 {i+1}"
                                print(f"获取视频文本失败: {e}")
                            
                            await self.print_message(f"\n正在播放：{current_video_text}\n若出现异常，将在4分钟后尝试重新播放", target_page=target_page)           
                            time.sleep(3)
                            error_count = 0  # 重置错误计数器
                            str0 = "200"  # 错误指标
                            
                            while True:
                                try:
                                    # 获取播放进度
                                    vvstr_elements = await target_page.query_selector_all('.vvstr')
                                    
                                    # 获取播放进度
                                    if vvstr_elements and len(vvstr_elements) > 0:
                                        try:
                                            progress_text = await vvstr_elements[0].inner_text()
                                            str1 = progress_text[-4:] if len(progress_text) >= 4 else "0%"
                                        except:
                                            str1 = "0%"
                                    else:
                                        str1 = "0%"
                                    
                                    time.sleep(3)
                                    if str0 != str1:
                                        error_count = 0
                                        str0 = str1
                                    else:
                                        error_count += 1  # 播放进度未改变时增加错误计数
                                    
                                    # 检查播放进度是否达到100%
                                    if str1 == "100%":
                                        if i + 1 < len(video_elements):
                                            await video_elements[i + 1].click()
                                            break
                                        else:
                                            await self.print_message("\n本课程播放完成", target_page=target_page)
                                            break
                                    
                                    # 异常次数过多时退出循环
                                    if error_count >= 15:
                                        await self.print_message("\n检测到异常状态，尝试恢复学习流程", target_page=target_page)
                                        raise SkipToNextCourse()
                                    
                                    time.sleep(10)
                                    
                                except SkipToNextCourse as e:
                                    raise
                                except Exception as e:
                                    await self.print_message(f"发生错误: {e}")
                                    await self.print_message(f"发生错误: {e}", target_page=target_page)
                                    break
        except Exception as e:
            await self.print_message(f"播放视频时出错: {e}")
    
    
    async def run_learning_cycle(self, button_index):
        """执行学习循环"""
        for attempt in range(self.max_attempts):
            new_page = None  # 初始化new_page变量
            try:
                print(f"开始第 {attempt + 1} 次学习尝试")
                
                # 点击学习课堂
                if not await self.click_learning_classroom():
                    print("点击学习课堂失败，结束本次尝试")
                    break
                
                # 点击进入学习
                enter_learning_result = await self.click_enter_learning(button_index)
                if not enter_learning_result:
                    await self.print_message("该专题不存在或已过期")
                    break
                
                # 点击开始学习/继续学习
                start_learning_result = await self.click_start_learning(attempt)
                if not start_learning_result:
                    if attempt == 0:
                        await self.print_message("无可学课程")
                    break
                
                # 等待并切换到新标签页，然后播放视频
                print("等待新页面打开...")
                new_page = await self.new_window()
                await self.play_videos(new_page)
                
                # 关闭新页面，回到原页面
                try:
                    if new_page and not new_page.is_closed():
                        await new_page.close()
                        print("已关闭新页面")
                except:
                    print("关闭新页面时出现异常")
                
            except:
                await self.print_message("跳过当前课程，尝试下一个课程")
                if new_page and not new_page.is_closed():
                        await new_page.close()
                continue  # 继续下一个课程