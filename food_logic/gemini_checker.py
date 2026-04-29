import os
import json
import google.generativeai as genai

class GeminiChecker:
    def __init__(self):
        # 讀取環境變數
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("找不到 GEMINI_API_KEY，請確認環境變數已設定。")
            
        # 初始化 Gemini API
        genai.configure(api_key=api_key)
        # 使用穩定且快速的 gemini-1.5-flash 模型
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def check_food_with_ai(self, food_name):
        """
        透過 Gemini AI 判定食材對四大慢性病的威脅燈號
        """
        prompt = f"""
        你是一位極度專業的「三高（高血壓、高血糖/糖尿病、高血脂）與痛風」臨床營養師。
        請針對使用者輸入的食材或料理：【{food_name}】，進行飲食禁忌與營養評估。

        請嚴格遵守以下燈號判定標準：
        - "GREEN": 安全、建議食用、對該疾病有益或無害。
        - "YELLOW": 普林/鈉/糖/脂肪偏中等，非急性發作期可適量，或需控量食用。
        - "RED": 絕對地雷，易引發急性發作，高油/高糖/高鹽/高普林，強烈不建議食用。

        你【必須】僅回傳一個 JSON 格式的字串，嚴格禁止包含任何 Markdown 區塊（例如不要有 ```json 標記）或是多餘的解釋文字。
        JSON 格式範例：
        {{
            "name": "{food_name}",
            "gout": "RED/YELLOW/GREEN",
            "hypertension": "RED/YELLOW/GREEN",
            "diabetes": "RED/YELLOW/GREEN",
            "hyperlipidemia": "RED/YELLOW/GREEN",
            "reason": "給長輩的一句話醫護級提醒（限50字以內）。"
        }}
        """

        try:
            # 呼叫 API
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # 清理可能的 Markdown 語法（防呆）
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()
                
            # 解析 JSON
            data = json.loads(text)
            
            # 轉換為與本地 FoodChecker 完全一致的輸出格式
            formatted_result = {
                "name": data.get("name", food_name),
                "individual_lights": {
                    "痛風": data.get("gout", "GREEN"),
                    "高血壓": data.get("hypertension", "GREEN"),
                    "糖尿病": data.get("diabetes", "GREEN"),
                    "高血脂": data.get("hyperlipidemia", "GREEN")
                },
                "reason": data.get("reason", "資料不足，建議諮詢醫師。")
            }
            return formatted_result
            
        except Exception as e:
            print(f"Gemini API 呼叫失敗: {e}")
            # 萬一失敗，將錯誤原因秀在卡片上，方便我們隔空抓藥！
            return {
                "name": food_name,
                "individual_lights": {
                    "痛風": "GREEN",
                    "高血壓": "GREEN",
                    "糖尿病": "GREEN",
                    "高血脂": "GREEN"
                },
                "reason": f"⚠️ 除錯訊息：{str(e)[:40]}..."
            }
