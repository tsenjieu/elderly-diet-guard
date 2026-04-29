import os
import sys
from dotenv import load_dotenv

# 確保能讀取到 food_logic
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

load_dotenv()

from food_logic.gemini_checker import GeminiChecker

def test():
    print("=========================================")
    print("【舒酸與三高守護者】AI 模組一鍵測試系統")
    print("=========================================")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n[狀態] ⚠️ 偵測到目前 .env 檔案中「尚未填寫」GEMINI_API_KEY。")
        print("👉 系統將強制模擬「連線異常／金鑰無效」的安全降級邏輯...")
        os.environ["GEMINI_API_KEY"] = "dummy_for_test"
    else:
        print(f"\n[狀態] ✅ 偵測到 GEMINI_API_KEY 已就緒！")
        print("👉 系統將連線 Google 進行真實數據解析...")
        
    print("\n[測試進行中] 正在獲取「麻辣臭豆腐」的營養判定...")
    
    try:
        checker = GeminiChecker()
        result = checker.check_food_with_ai("麻辣臭豆腐")
        
        print("\n=========================================")
        print(" 【AI 分析結果】")
        print("=========================================")
        print(f" 食品名稱： {result.get('name')}")
        print(" 各項燈號判定：")
        
        lights = result.get("individual_lights", {})
        light_emoji = {"RED": "🔴 【地雷】", "YELLOW": "🟡 【控量】", "GREEN": "🟢 【推薦】", "UNKNOWN": "⚪ 【未知】"}
        
        for cond in ["痛風", "高血壓", "糖尿病", "高血脂"]:
            light = lights.get(cond, "UNKNOWN")
            emoji = light_emoji.get(light, "⚪")
            print(f"   ├─ {cond}: {emoji}")
            
        print(f" 醫護級指引： {result.get('reason')}")
        print("=========================================")
        print("\n✅ 測試順利執行完畢！")
    except Exception as e:
        print(f"\n❌ 程式執行過程中發生不可預期的錯誤：{e}")

if __name__ == "__main__":
    test()
