import sys
import os
import unittest

# 確保能讀取到 food_logic
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from food_logic.checker import FoodChecker
from food_logic.tracker import DietTracker

class TestFoodLogic(unittest.TestCase):
    def setUp(self):
        # 測試路徑
        self.db_path = os.path.join(parent_dir, "food_logic", "data", "food_database.csv")
        self.log_path = os.path.join(current_dir, "test_diet_logs.json")
        self.checker = FoodChecker(db_path=self.db_path)
        self.tracker = DietTracker(log_path=self.log_path)

    def tearDown(self):
        # 移除測試 log 檔案
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def test_guava_gout_and_diabetes(self):
        """測試 痛風+糖尿病 查詢 芭樂"""
        # 芭樂在資料庫中對痛風是 GREEN, 糖尿病是 GREEN
        result = self.checker.check_food("芭樂", ["痛風", "糖尿病"])
        self.assertEqual(result["light"], "GREEN")

    def test_milkfish_gout_only(self):
        """測試 單純痛風 查詢 虱目魚肚"""
        # 虱目魚肚在資料庫中對痛風是 RED
        result = self.checker.check_food("虱目魚肚", ["痛風"])
        self.assertEqual(result["light"], "RED")

    def test_milkfish_hypertension_only(self):
        """測試 單純高血壓 查詢 虱目魚肚"""
        # 虱目魚肚在資料庫中對高血壓是 GREEN
        result = self.checker.check_food("虱目魚肚", ["高血壓"])
        self.assertEqual(result["light"], "GREEN")

    def test_diet_tracker_meal(self):
        """測試 飲食紀錄儲存功能"""
        record = self.tracker.log_meal("午餐", "芭樂", "GREEN", "一掌心")
        self.assertEqual(record["meal_type"], "午餐")
        self.assertEqual(record["food_name"], "芭樂")
        
        summary = self.tracker.get_daily_summary(record["date"])
        self.assertEqual(summary["summary"]["GREEN"], 1)
        self.assertEqual(summary["summary"]["total"], 1)

if __name__ == '__main__':
    unittest.main()
