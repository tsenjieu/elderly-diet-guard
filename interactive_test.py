import sys
import os

# 確保能讀取到 food_logic
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from food_logic.checker import FoodChecker
from food_logic.tracker import DietTracker

def main():
    print("=========================================")
    print("【舒酸與三高守護者】終端機模擬測試系統")
    print("=========================================")
    
    checker = FoodChecker()
    tracker = DietTracker()
    
    # 1. 選擇慢性病狀態
    print("\n[步驟 1] 請勾選您的慢性病（多選，請輸入數字並以逗號隔開，例如：1,2）")
    print("1. 痛風")
    print("2. 高血壓")
    print("3. 糖尿病")
    print("4. 高血脂")
    print("5. 完全健康 / 無特殊慢性病")
    
    choice_map = {"1": "痛風", "2": "高血壓", "3": "糖尿病", "4": "高血脂"}
    user_input = input("請輸入您的選擇： ").strip()
    
    conditions = []
    if user_input != "5":
        for c in user_input.split(","):
            c = c.strip()
            if c in choice_map:
                conditions.append(choice_map[c])
                
    print(f"\n🔍 您目前啟用的健康模式為：【{', '.join(conditions) if conditions else '一般大眾健康模式'}】")
    print(f"💡 提示：目前為第一階段示範，資料庫內建 20 種台灣在地食材。")
    
    # 2. 開始查詢食物
    while True:
        print("\n-----------------------------------------")
        food_name = input("請輸入您想查詢的食材 (輸入 L 列出所有食材清單，輸入 Q 離開)： ").strip()
        
        if food_name.upper() == 'Q':
            break
            
        if food_name.upper() == 'L':
            foods = list(checker.food_db.keys())
            print(f"\n📖 目前資料庫中的 {len(foods)} 種食材：")
            print("、".join(foods))
            continue
        
        matched_names = checker.search_foods(food_name)
        
        if not matched_names:
            print(f"\n食品名稱： {food_name}")
            print("燈號判定： ⚪ 【未知】")
            print("健康指引： 資料庫中暫無此食材資料，建議保守食用或諮詢醫師。")
            continue
            
        if len(matched_names) > 1:
            print(f"\n找到 {len(matched_names)} 筆與「{food_name}」相關的食材：")
        
        for matched_name in matched_names:
            result = checker.check_food(matched_name, conditions)
            
            # 視覺化燈號
            light_emoji = {"RED": "🔴 【絕對禁止】", "YELLOW": "🟡 【限制食用】", "GREEN": "🟢 【放心吃】", "UNKNOWN": "⚪ 【未知】"}
            emoji = light_emoji.get(result["light"], "⚪")
            
            print(f"\n👉 食品名稱： {result['name']}")
            print(f"   燈號判定： {emoji}")
            print(f"   健康指引： {result['reason']}")
            
        # 處理記錄邏輯
        if len(matched_names) == 1:
            record_target = matched_names[0]
            light_target = checker.check_food(record_target, conditions)["light"]
        else:
            print("\n您準備享用上述哪個食材嗎？")
            for idx, name in enumerate(matched_names, 1):
                print(f"[{idx}] {name}")
            choice = input(f"請輸入數字 (1-{len(matched_names)}，或按 Enter 跳過記錄)： ").strip()
            
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(matched_names):
                continue
            record_target = matched_names[int(choice)-1]
            light_target = checker.check_food(record_target, conditions)["light"]

        if light_target != "UNKNOWN":
            print(f"\n準備將【{record_target}】寫入日誌...")
            print("[1] 早餐  [2] 午餐  [3] 晚餐  [4] 點心")
            ans = input("請選擇時段 (輸入數字 1-4，或按 Enter 不記錄)： ").strip()
            
            meal_map = {"1": "早餐", "2": "午餐", "3": "晚餐", "4": "點心"}
            if ans in meal_map:
                meal_type = meal_map[ans]
                
                print("\n[1] 一小盤  [2] 半碗  [3] 一碗  [4] 一掌心")
                p_ans = input("請選擇預估份量 (輸入數字 1-4)： ").strip()
                portion_map = {"1": "一小盤", "2": "半碗", "3": "一碗", "4": "一掌心"}
                portion = portion_map.get(p_ans, "一份")
                
                tracker.log_meal(meal_type, record_target, light_target, portion)
                print(f"✅ 已成功記錄：今日【{meal_type}】吃了【{record_target}】一份（{portion}）。")
                
                # 取得當日統計
                summary = tracker.get_daily_summary()
                stats = summary["summary"]
                print(f"📊 今日目前飲食狀況：🟢 綠燈 {stats['GREEN']} 次 | 🟡 黃燈 {stats['YELLOW']} 次 | 🔴 紅燈 {stats['RED']} 次")
                
    print("\n感謝使用【舒酸與三高守護者】測試系統！")

if __name__ == '__main__':
    main()
