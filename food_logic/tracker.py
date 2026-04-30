import json
import os
from datetime import datetime
import gspread

class DietTracker:
    def __init__(self, log_path=None):
        if log_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(current_dir, "data", "diet_logs.json")
            
        self.log_path = log_path
        self.logs = []
        self.sheet = None
        self.users_sheet = None
        
        # 嘗試連線 Google Sheets
        self._init_google_sheets()
        
        # 若未連線成功，則讀取本地資料
        if not self.sheet:
            self.load_logs()

    def _init_google_sheets(self):
        """初始化 Google Sheets 連線，並同步資料"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # 優先找尋 Render Secret Files 路徑，再找本地根目錄
        creds_path = "/etc/secrets/google_credentials.json"
        if not os.path.exists(creds_path):
            creds_path = os.path.join(parent_dir, "google_credentials.json")
            
        if os.path.exists(creds_path):
            try:
                # 使用 gspread 內建的 service_account 方法，更簡潔且不依賴舊套件
                client = gspread.service_account(filename=creds_path)
                
                # 開啟主要飲食表單
                self.sheet = client.open("長輩飲食紀錄庫").sheet1
                self.logs = self.sheet.get_all_records()
                
                # 開啟或建立使用者名單表單
                try:
                    self.users_sheet = client.open("長輩飲食紀錄庫").worksheet("Users")
                except gspread.exceptions.WorksheetNotFound:
                    # 如果找不到 Users 分頁，則建立一個並加上標題
                    self.users_sheet = client.open("長輩飲食紀錄庫").add_worksheet(title="Users", rows="100", cols="5")
                    self.users_sheet.append_row(["user_id", "display_name", "last_active"])
                
                print("✅ 成功連線 Google Sheets 並同步資料庫與使用者名單！")
            except Exception as e:
                print(f"⚠️ Google Sheets 連線失敗: {e}")
                self.sheet = None
                self.users_sheet = None
        else:
            print("⚠️ 找不到 google_credentials.json，將使用本地 JSON 儲存。")

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
            "type": "food",
            "meal_type": meal_type,
            "food_name": food_name,
            "light": light,
            "portion": portion,
            "amount_cc": ""
        }
        
        self.logs.append(record)
        
        if self.sheet:
            try:
                row = [
                    record["timestamp"], record["date"], record["type"],
                    record["meal_type"], record["food_name"], record["light"],
                    record["portion"], record["amount_cc"]
                ]
                self.sheet.append_row(row)
            except Exception as e:
                print(f"寫入 Google Sheets 失敗: {e}")
                self.save_logs()
        else:
            self.save_logs()
            
        return record

    def log_water(self, amount_cc: int) -> dict:
        """
        記錄一筆飲水。
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        record = {
            "timestamp": now,
            "date": date_str,
            "type": "water",
            "meal_type": "飲水",
            "food_name": f"{amount_cc}cc",
            "light": "WATER",
            "portion": "",
            "amount_cc": amount_cc
        }
        
        self.logs.append(record)
        
        if self.sheet:
            try:
                row = [
                    record["timestamp"], record["date"], record["type"],
                    record["meal_type"], record["food_name"], record["light"],
                    record["portion"], record["amount_cc"]
                ]
                self.sheet.append_row(row)
            except Exception as e:
                print(f"寫入 Google Sheets 失敗: {e}")
                self.save_logs()
        else:
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
            if str(log.get("timestamp")) == str(timestamp):
                removed = self.logs.pop(i)
                
                if self.sheet:
                    try:
                        # 尋找試算表中的該時間戳，找到後刪除整列
                        cell = self.sheet.find(str(timestamp))
                        if cell:
                            self.sheet.delete_rows(cell.row)
                    except Exception as e:
                        print(f"刪除 Google Sheets 紀錄失敗: {e}")
                else:
                    self.save_logs()
                    
                return removed
        return None

    # --- 使用者推播管理 ---
    
    def register_user(self, user_id: str, display_name: str = ""):
        """註冊新使用者至 Users 表單，若已存在則更新最後活動時間"""
        if not self.users_sheet:
            return
            
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cell = self.users_sheet.find(user_id)
            if cell:
                # 已存在，更新活動時間 (假設 user_id 在 A 欄, last_active 在 C 欄)
                self.users_sheet.update_cell(cell.row, 3, now)
                if display_name:
                    self.users_sheet.update_cell(cell.row, 2, display_name)
            else:
                # 新使用者
                self.users_sheet.append_row([user_id, display_name, now])
                print(f"🆕 已註冊新使用者: {user_id}")
        except Exception as e:
            print(f"註冊使用者失敗: {e}")

    def get_all_users(self) -> list:
        """取得所有已註冊的使用者 ID 列表"""
        if not self.users_sheet:
            return []
        try:
            records = self.users_sheet.get_all_records()
            return [r["user_id"] for r in records if r.get("user_id")]
        except Exception as e:
            print(f"讀取使用者名單失敗: {e}")
            return []

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
                    
        summary = {"RED": 0, "YELLOW": 0, "GREEN": 0, "UNKNOWN": 0, "total": 0, "water_total": 0}
        for rec in range_records:
            if rec.get("type") == "water":
                summary["water_total"] += rec.get("amount_cc", 0)
            else:
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
        
        summary = {"RED": 0, "YELLOW": 0, "GREEN": 0, "total": 0, "water_total": 0}
        for rec in daily_records:
            if rec.get("type") == "water":
                summary["water_total"] += rec.get("amount_cc", 0)
            else:
                light = rec.get("light")
                if light in summary:
                    summary[light] += 1
                    summary["total"] += 1
                
        return {
            "date": date_str,
            "summary": summary,
            "records": daily_records
        }
