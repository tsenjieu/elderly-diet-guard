import os
import sys
import subprocess

print("===========================================")
print("      GitHub 自動推送雲端小幫手")
print("===========================================")
print("\n為了將機器人放上雲端，我們需要把這些程式碼傳送到您的 GitHub 帳號。")
print("\n步驟 1: 請先前往 https://github.com/new 建立一個新的專案 (Repository)。")
print("        -> Repository name 隨便取 (例如: linebot-health)")
print("        -> 選擇 Public 或 Private 都可以")
print("        -> 直接點擊最下方的 Create repository 按鈕")
print("\n步驟 2: 建立成功後，複製網址列的網址 (例如: https://github.com/您的帳號/linebot-health.git)")

try:
    repo_url = input("\n步驟 3: 請在此處「按右鍵貼上」那串網址，然後按 Enter：").strip()
    
    if not repo_url or not repo_url.startswith("http"):
        print("\n❌ 網址格式錯誤！請關閉視窗後重新執行。")
    else:
        print("\n🚀 正在為您打包並傳送程式碼，請稍候...\n")
        
        git_exe = r'"C:\Program Files\Git\cmd\git.exe"'
        commands = [
            ("設定 Git 名稱...", f"{git_exe} config --global user.name \"LineBot Developer\""),
            ("設定 Git 信箱...", f"{git_exe} config --global user.email \"developer@antigravity.local\""),
            ("初始化 Git...", f"{git_exe} init"),
            ("加入所有檔案...", f"{git_exe} add ."),
            ("建立版本紀錄...", f'{git_exe} commit -m "Ready for Render Deployment"'),
            ("設定主分支...", f"{git_exe} branch -M main"),
            ("連結雲端倉庫...", f"{git_exe} remote add origin {repo_url}"),
            ("更新雲端連結...", f"{git_exe} remote set-url origin {repo_url}"),
            ("開始上傳...", f"{git_exe} push -u origin main --force")
        ]
        
        for desc, cmd in commands:
            print(f"> {desc}")
            # 不擷取輸出，直接印在畫面上，避免 Windows 的編碼解碼問題 (cp950 / UTF-8)
            result = subprocess.run(cmd, shell=True)
            if result.returncode != 0:
                print(f"⚠️ 執行警告！")
                
        print("\n✅ 推送完成！請回到您的 GitHub 網頁重新整理，看看檔案是不是都上去了！")
        print("接下來，請參考我傳給您的教學，前往 Render 進行最終連線。")
        
except KeyboardInterrupt:
    print("\n已取消操作。")

print("\n請按任意鍵退出...")
os.system("pause >nul")
