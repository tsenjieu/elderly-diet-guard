import json
import csv
import os

class FoodChecker:
    def __init__(self, db_path=None):
        if db_path is None:
            # 預設路徑：與當前檔案同層的 data/food_database.csv
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "data", "food_database.csv")
        
        self.db_path = db_path
        self.food_db = {}
        self.load_database()

    def load_database(self):
        """讀取 CSV 食材資料庫"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"找不到食材資料庫：{self.db_path}")
            
        with open(self.db_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name")
                if name:
                    self.food_db[name] = dict(row)

    def search_foods(self, keyword: str) -> list:
        """根據關鍵字模糊搜尋食材名稱，回傳匹配的名稱清單"""
        if keyword in self.food_db:
            return [keyword] # 完全比對優先
        
        return [k for k in self.food_db.keys() if keyword in k]

    def check_food(self, food_name: str, conditions: list) -> dict:
        """
        根據使用者的慢性病狀態，判定某個食材的綜合燈號。
        
        :param food_name: 食材名稱（如：'芭樂'）
        :param conditions: 慢性病清單，可包含：['痛風', '高血壓', '糖尿病', '高血脂']
        :return: 包含最終燈號與原因的字典
        """
        # 建立疾病對應資料庫欄位名稱的 mapping
        mapping = {
            "痛風": "gout",
            "高血壓": "hypertension",
            "糖尿病": "diabetes",
            "高血脂": "hyperlipidemia"
        }

        if food_name not in self.food_db:
            return {
                "name": food_name,
                "light": "UNKNOWN",
                "reason": "資料庫中暫無此食材資料，建議保守食用或諮詢醫師。"
            }

        food_data = self.food_db[food_name]
        
        # 如果使用者完全沒勾選任何疾病，視為完全健康（理論上預設為全綠，或依據一般飲食指引）
        if not conditions:
            return {
                "name": food_name,
                "light": "GREEN",
                "reason": "未偵測到特殊慢性病，一般人可正常適量食用。"
            }

        # 判定權重：RED > YELLOW > GREEN
        weights = {"RED": 3, "YELLOW": 2, "GREEN": 1, "UNKNOWN": 0}
        max_weight = 0
        final_light = "GREEN"

        # 針對使用者勾選的每種疾病，找出最嚴重的燈號
        for cond in conditions:
            db_field = mapping.get(cond)
            if db_field and db_field in food_data:
                field_light = food_data[db_field]
                if weights.get(field_light, 0) > max_weight:
                    max_weight = weights[field_light]
                    final_light = field_light

        return {
            "name": food_name,
            "light": final_light,
            "reason": food_data.get("reason", "無詳細說明。"),
            "individual_lights": {cond: food_data.get(mapping.get(cond), "UNKNOWN") for cond in conditions}
        }
