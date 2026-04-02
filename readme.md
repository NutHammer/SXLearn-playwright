# 陕西干部网络学院自动刷课工具

手动登录、选课后，本程序可以自动学完所有已选课程。  
在一台电脑上复制多个此程序可以独立运行并各操作一个账号。

# 兼容性

已经测试可用的并提供发行版的平台：x86处理器的windows11，x86虚拟机中的UOS 1070，arm虚拟机中的UOS 1070。

x86及arm架构的ubuntu，debian，银河麒麟，可尝试UOS的发行版。

mac os理论上可用，但无法提供发行版。

# 使用发行版

1.安装浏览器。  
下载并解压缩浏览器。

windows：

下载地址：https://cdn.playwright.dev/chrome-for-testing-public/145.0.7632.6/win64/chrome-win64.zip

启动路径：./res/browsers/chromium-1208/chrome-win64/chrome.exe

&#x20;linux\_amd64:

下载地址:  https://cdn.playwright.dev/chrome-for-testing-public/145.0.7632.6/linux64/chrome-linux64.zip

启动路径：./res/browsers/chromium-1208/chrome-linux64/chrome

&#x20;linux\_arm64:

下载地址:  https://cdn.playwright.dev/dbazure/download/playwright/builds/chromium/1208/chromium-linux-arm64.zip

启动路径：./res/browsers/chromium-1208/chrome-linux/chrome

&#x20;

2.运行程序，等待程序启动浏览器。  
windows：运行main.exe  
UOS：运行main

&#x20;

3.完成登录和选课。

&#x20;

4.输入要学习的课程序号，按回车。

&#x20;

5.等待程序运行。  
程序开始显示播放进度后就可以开始进行其他工作，保持浏览器和本程序在后台运行即可（可以最小化，但不能同时运行大型游戏等需要持续保持前台的软件）。  
程序运行时，如果需要使用浏览器，请使用其他浏览器，不要在播视频的这个浏览器上操作。

# 使用源码运行

1. 安装依赖：pip install playwright ; pip install playwright-stealth
2. 安装浏览器：运行bin/installer.py。
3. 运行bin/main.py
4. 按照发行版使用步骤3-5执行。

# 已知问题  
由于playwright自身限制，浏览器视图大小无法调整，暂无可靠的解决方案。  
有一些多余的等待机制，导致程序看起来运行缓慢，但对整体运行时间来说影响非常小，暂时不会单独修复此问题。

# 已知问题

由于playwright自身限制，浏览器视图大小无法调整，暂无可靠的解决方案。

