import os
import sys

print("===========================================")
print("      ngrok 首次綁定金鑰設定小幫手 (Python版)")
print("===========================================")
print("\n為了防止駭客濫用，ngrok 規定第一次使用必須綁定您的專屬金鑰 (authtoken)。")
print("\n步驟 1: 請先前往 https://dashboard.ngrok.com/get-started/your-authtoken")
print("步驟 2: 註冊/登入後，找到頁面上的 Your Authtoken 並將那串長長的英數字複製起來。")

try:
    token = input("\n步驟 3: 請在此處「按右鍵貼上」您的 authtoken，然後按 Enter：").strip()
    
    if not token:
        print("\n❌ 您沒有輸入任何內容！請關閉視窗後重新執行。")
    else:
        print("\n正在為您綁定...")
        # 執行 ngrok 指令
        result = os.system(f"ngrok config add-authtoken {token}")
        
        if result == 0:
            print("\n✅ 綁定成功！您現在可以關閉此視窗，並重新點擊【啟動ngrok.bat】了！")
        else:
            print(f"\n❌ 綁定過程中發生錯誤 (錯誤碼: {result})，請確認您的 ngrok 是否有正確下載。")
            
except KeyboardInterrupt:
    print("\n已取消操作。")

print("\n請按任意鍵退出...")
os.system("pause >nul")
