@echo off
chcp 65001 >nul
echo ========================================================
echo   【舒酸與三高守護者】強制背景程序清除與重啟
echo ========================================================
echo.
echo 正在強制終結所有卡在背景的 Python 服務...
taskkill /F /IM python.exe >nul 2>&1
echo [OK] 舊程序已全數清除。
echo.
echo 正在重新載入最新程式碼並啟動 LINE 機器人...
uvicorn main:app --reload
pause
