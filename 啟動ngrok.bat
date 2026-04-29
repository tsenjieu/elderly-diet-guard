@echo off
chcp 65001 >nul
echo ========================================================
echo        啟動 ngrok 內網穿透 (將您的電腦連接至 LINE)
echo ========================================================
echo.
echo 注意：如果您是第一次使用 ngrok，請先在命令提示字元輸入以下指令：
echo ngrok config add-authtoken [您的_authtoken]
echo.
echo 正在啟動 ngrok 代理至 8000 port...
ngrok http 8000
pause
