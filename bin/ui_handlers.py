# UI处理模块 - 实现网页悬浮窗和弹窗功能

class UIHandlers:
    def __init__(self, page):
        self.page = page
        self.history_content = ""  # 添加历史消息记录
    
    async def init_async(self):
        """异步初始化方法，需要在创建 UIHandlers 后调用"""
        await self._initialize_floating_window()
        # 隐藏输入框，默认不显示
        await self.hide_input()
    
    async def _initialize_floating_window(self):
        """初始化网页右下角的悬浮窗"""
        # 将悬浮窗代码注入到当前页面
        await self.page.evaluate(self._get_init_script())
    
    def _get_init_script(self):
        """返回悬浮窗初始化脚本"""
        return """
        // 创建样式元素
        var style = document.createElement('style');
        style.innerHTML = `
            .floating-window {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 350px;
                height: 400px;
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                overflow-y: auto;
                z-index: 9999;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            }
            .floating-window-title {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
                text-align: center;
                padding-bottom: 5px;
                border-bottom: 1px solid #555;
            }
            .floating-window-content {
                white-space: pre-wrap;
                word-wrap: break-word;
                margin-bottom: 10px;
            }
            .floating-window-close {
                position: absolute;
                top: 5px;
                right: 10px;
                cursor: pointer;
                color: #aaa;
            }
            .floating-window-close:hover {
                color: white;
            }
            .floating-window-input-container {
                display: flex;
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #555;
            }
            .floating-window-input {
                flex: 1;
                padding: 5px;
                border: 1px solid #555;
                border-radius: 4px 0 0 4px;
                background-color: #333;
                color: white;
            }
            .floating-window-button {
                padding: 5px 10px;
                border: 1px solid #555;
                border-radius: 0 4px 4px 0;
                background-color: #555;
                color: white;
                cursor: pointer;
            }
            .floating-window-button:hover {
                background-color: #666;
            }
        `;
        document.head.appendChild(style);
        
        // 创建悬浮窗容器
        var floatingWindow = document.createElement('div');
        floatingWindow.className = 'floating-window';
        
        // 创建标题元素
        var title = document.createElement('div');
        title.className = 'floating-window-title';
        title.textContent = '运行状态';
        floatingWindow.appendChild(title);
        
        // 创建关闭按钮
        var closeBtn = document.createElement('div');
        closeBtn.className = 'floating-window-close';
        closeBtn.textContent = '×';
        closeBtn.onclick = function() {
            this.parentElement.style.display = 'none';
        };
        floatingWindow.appendChild(closeBtn);
        
        // 创建内容容器
        var content = document.createElement('div');
        content.className = 'floating-window-content';
        content.id = 'status-content';
        floatingWindow.appendChild(content);
        
        // 创建输入容器
        var inputContainer = document.createElement('div');
        inputContainer.className = 'floating-window-input-container';
        // 默认隐藏输入容器
        inputContainer.style.display = 'none';
        
        // 创建输入框
        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'floating-window-input';
        input.placeholder = '请输入命令...';
        inputContainer.appendChild(input);
        
        // 创建提交按钮
        var button = document.createElement('button');
        button.className = 'floating-window-button';
        button.textContent = '提交';
        inputContainer.appendChild(button);
        
        // 将输入容器添加到悬浮窗
        floatingWindow.appendChild(inputContainer);
        
        // 将悬浮窗添加到页面
        document.body.appendChild(floatingWindow);
        
        // 用于存储状态信息和输入回调
        var statusContent = document.getElementById('status-content');
        var inputCallback = null;
        
        // 添加状态信息到悬浮窗
        window.addStatus = function(message) {
            var timestamp = new Date().toLocaleTimeString();
            statusContent.innerHTML += '[' + timestamp + '] ' + message + '\\n';
            // 自动滚动到底部
            statusContent.scrollTop = statusContent.scrollHeight;
        };
        
        // 设置状态内容（用于恢复记录）
        window.setStatusContent = function(content) {
            statusContent.innerHTML = content;
            // 自动滚动到底部
            statusContent.scrollTop = statusContent.scrollHeight;
        };
        
        // 获取当前状态内容
        window.getStatusContent = function() {
            return statusContent.innerHTML;
        };
        
        // 清空状态信息
        window.clearStatus = function() {
            statusContent.innerHTML = '';
        };
        
        // 设置输入回调
        window.setInputCallback = function(callback) {
            inputCallback = callback;
            input.focus(); // 自动聚焦到输入框
        };
        
        // 处理输入提交
        button.onclick = function() {
            if (inputCallback) {
                var value = input.value.trim();
                input.value = ''; // 清空输入框
                inputCallback(value);
                inputCallback = null;
            }
        };
        
        // 处理回车键提交
        input.onkeypress = function(e) {
            if (e.key === 'Enter') {
                button.click();
            }
        };
        
        // 显示输入容器
        window.showInputContainer = function() {
            inputContainer.style.display = 'flex';
        };
        
        // 隐藏输入容器
        window.hideInputContainer = function() {
            inputContainer.style.display = 'none';
        };
        """
    
    async def _check_floating_window(self, page=None):
        """检查悬浮窗是否存在，如果不存在则重新初始化并恢复之前的记录"""
        target_page = page if page is not None else self.page
        
        try:
            # 检查addStatus函数是否存在
            result = await target_page.evaluate("typeof window.addStatus === 'function'")
            if not result:
                # 重新初始化悬浮窗
                await target_page.evaluate(self._get_init_script())
                
                # 恢复之前的状态内容
                if self.history_content:
                    await target_page.evaluate(f"setStatusContent('{self.history_content}');")
        except:
            pass
    
    async def print_to_window(self, message, end='\n', target_page=None):
        """将信息打印到悬浮窗"""
        page_to_use = target_page if target_page is not None else self.page
        
        # 检查悬浮窗是否存在
        await self._check_floating_window(page_to_use)
        
        # 处理换行符和特殊字符
        message = str(message).replace('"', '&quot;').replace("'", "\\'").replace('\n', '\\n')
        # 执行JavaScript添加状态信息
        await page_to_use.evaluate(f"addStatus('{message}');")
        # 同时在控制台打印（可选）
        print(message, end=end)
        
        # 更新历史记录
        timestamp = await page_to_use.evaluate("new Date().toLocaleTimeString()")
        self.history_content += f'[{timestamp}] {str(message).replace("\\'", "'")}\\n'
    
    async def input_from_window(self, message):
        """从悬浮窗获取用户输入"""
        # 检查悬浮窗是否存在
        await self._check_floating_window()
        
        # 首先显示提示信息
        await self.print_to_window(message)
        
        # 显示输入框
        await self.show_input()
        
        # 使用Promise等待用户输入
        script = """
        new Promise((resolve) => {
            window.setInputCallback(resolve);
        });
        """
        return await self.page.evaluate(script)
    
    async def clear_window(self):
        """清空悬浮窗内容"""
        # 检查悬浮窗是否存在
        await self._check_floating_window()
        await self.page.evaluate("clearStatus();")
        # 清空历史记录
        self.history_content = ""
    
    async def show_input(self):
        """显示输入框"""
        try:
            await self.page.evaluate("showInputContainer();")
        except:
            pass
    
    async def hide_input(self):
        """隐藏输入框"""
        try:
            await self.page.evaluate("hideInputContainer();")
        except:
            pass