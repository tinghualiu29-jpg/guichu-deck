#!/bin/zsh
# 双击这个文件即可打开作品。
cd "$(dirname "$0")" || exit 1

# 1 秒后打开默认浏览器
(sleep 1; open "http://localhost:8780/") &

# 前台运行本地服务器；关闭这个终端窗口即停止
exec python3 server.py
