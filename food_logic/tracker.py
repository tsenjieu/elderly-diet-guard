import json
import os
from datetime import datetime

class DietTracker:
    def __init__(self, log_path=None):
        if log_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(current_dir, "data", "diet_logs.json")
            
        self.log_path = log_path
        self.logs = []
        self.load_logs()

    def load_logs(self):
        """讀取歷史飲食紀錄"""
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    self.logs = json.load(f)
            except json.JSONDecodeError:
                self.logs = []
        else:
            self.logs = []

    def save_logs(self):
        """儲存飲食紀錄至檔案"""
        # 確保資料夾存在
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=2)

    def log_meal(self, meal_type: str, food_name: str, light: str, portion: str) -> dict:
        """
        記錄一筆飲食。
        
        :param meal_type: 早、午、晚、點心
        :param food_name: 食物名稱
        :param light: 燈號（RED / YELLOW / GREEN）
        :param portion: 份量（一碗、一掌心、一小盤...）
        """
        # 台灣本地時間
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        record = {
            "timestamp": now,
            "date": date_str,
            "meal_type": meal_type,
            "food_name": food_name,
            "light": light,
            "portion": portion
        }
        
        self.logs.append(record)
        self.save_logs()
        return record

    def delete_last_record(self) -> dict:
        """刪除最後一筆飲食紀錄（防誤按）"""
        if self.logs:
            removed = self.logs.pop()
            self.save_logs()
            return removed
        return None

    def delete_record_by_timestamp(self, timestamp: str) -> dict:
        """根據時間戳記精準刪除指定紀錄"""
        for i, log in enumerate(self.logs):
            if log.get("timestamp") == timestamp:
                removed = self.logs.pop(i)
                self.save_logs()
                return removed
        return None

    def get_range_summary(self, days: int = 7) -> dict:
        """取得過去指定天數的飲食燈號統計"""
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1) # 包含今天
        
        range_records = []
        for log in self.logs:
            log_date_str = log.get("date")
            if log_date_str:
                try:
                    log_date = datetime.strptime(log_date_str, "%Y-%m-%d")
                    if start_date.date() <= log_date.date() <= end_date.date():
                        range_records.append(log)
                except ValueError:
                    continue
                    
        summary = {"RED": 0, "YELLOW": 0, "GREEN": 0, "UNKNOWN": 0, "total": 0}
        for rec in range_records:
            light = rec.get("light", "UNKNOWN")
            if light in summary:
                summary[light] += 1
                summary["total"] += 1
                
        return {
            "days": days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "summary": summary,
            "records": range_records
        }

    def get_daily_summary(self, date_str: str = None) -> dict:
        """
        取得某一天的飲食燈號統計（圓餅圖數據來源）
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            
        daily_records = [log for log in self.logs if log.get("date") == date_str]
        
        summary = {"RED": 0, "YELLOW": 0, "GREEN": 0, "total": 0}
        for rec in daily_records:
            light = rec.get("light")
            if light in summary:
                summary[light] += 1
                summary["total"] += 1
                
        return {
            "date": date_str,
            "summary": summary,
            "records": daily_records
        }
