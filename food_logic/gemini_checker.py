import os
import json
import requests

class GeminiChecker:
    def __init__(self):
        # 讀取環境變數
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("找不到 GEMINI_API_KEY，請確認環境變數已設定。")

    def check_food_with_ai(self, food_name):
        """
        透過 Gemini API (REST) 判定食材對四大慢性病的威脅燈號
        """
        prompt = f"""
        你是一位極度專業的「三高（高血壓、高血糖/糖尿病、高血脂）與痛風」臨床營養師。
        請針對使用者輸入的內容：【{food_name}】，判斷是否為食材、飲料或料理，若是，請進行飲食禁忌與營養評估。

        【非食物防呆機制】：
        如果使用者輸入的明顯【不是食物或料理】（例如：問候語「你好」、天氣、無意義的亂碼、生活閒聊），請直接將 JSON 中的 "is_food" 設為 false，其他欄位保留空字串即可。

        【極度重要——最嚴格保守原則】（若為食物）：
        作為臨床醫療系統，你必須採取「最嚴格、最保守」的判定態度。絕不輕易給予 GREEN（綠燈）。若該料理包含以下高危險因子，請毫不猶豫判定為 YELLOW 或 RED：
        - 痛風：凡含有「肉湯、火鍋濃湯、內臟、海鮮、高湯、肉類加工品」 -> 判定 RED。
        - 高血壓：凡含有「麻辣、重鹹、濃縮醬汁、醃漬物、沾醬」 -> 判定 RED。
        - 糖尿病：凡含有「高糖、勾芡、精緻澱粉、含糖醬料」 -> 判定 RED。
        - 高血脂：凡含有「油炸、油煎、肥肉、動物油、麻辣紅油」 -> 判定 RED。

        請嚴格遵守以下燈號判定標準：
        - "GREEN": 完全健康安全、無負擔。
        - "YELLOW": 普林/鈉/糖/脂肪偏中等，非急性發作期可「極少量嚴格控量」食用。
        - "RED": 絕對地雷，極易誘發急性併發症或發作，強烈不建議食用。

        你【必須】僅回傳一個 JSON 格式的字串，嚴格禁止包含任何 Markdown 區塊（例如不要有 ```json 標記）或是多餘的解釋文字。
        JSON 格式範例：
        {{
            "is_food": true,
            "name": "{food_name}",
            "nutritional_analysis": "（思維鏈）先客觀分析此食材的特性，例如：此為麻辣油炸食品，高鹽高油。",
            "gout": "RED/YELLOW/GREEN",
            "hypertension": "RED/YELLOW/GREEN",
            "diabetes": "RED/YELLOW/GREEN",
            "hyperlipidemia": "RED/YELLOW/GREEN",
            "reason": "給長輩的一句話醫護級貼心提醒（限50字以內）。"
        }}
        """

        try:
            # 使用最穩定的 REST API v1 正式版，避開 v1beta 的模型找不到地雷
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code != 200:
                raise ValueError(f"API 狀態碼錯誤：{response.status_code}, 內容：{response.text[:100]}")
                
            res_json = response.json()
            text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # 清理可能的 Markdown 語法（防呆）
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()
                
            # 解析 JSON
            parsed_data = json.loads(text)
            
            # 轉換為與本地 FoodChecker 完全一致的輸出格式
            formatted_result = {
                "is_food": parsed_data.get("is_food", True),
                "name": parsed_data.get("name", food_name),
                "reason": parsed_data.get("reason", "資料不足，建議諮詢醫師。"),
                "individual_lights": {
                    "痛風": parsed_data.get("gout", "UNKNOWN"),
                    "高血壓": parsed_data.get("hypertension", "UNKNOWN"),
                    "糖尿病": parsed_data.get("diabetes", "UNKNOWN"),
                    "高血脂": parsed_data.get("hyperlipidemia", "UNKNOWN")
                }
            }
            return formatted_result
            
        except Exception as e:
            print(f"Gemini API 呼叫失敗: {e}")
            # 萬一失敗，回傳一個安全的預設綠燈卡片，避免當機
            return {
                "name": food_name,
                "individual_lights": {
                    "痛風": "UNKNOWN",
                    "高血壓": "UNKNOWN",
                    "糖尿病": "UNKNOWN",
                    "高血脂": "UNKNOWN"
                },
                "reason": "目前 AI 分析連線障礙，保守起見無法判定安全度。建議您詢問專業醫師。"
            }

