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
        你是一位極度嚴格且專業的「三高與痛風」臨床營養師。
        使用者剛剛輸入了：【{food_name}】

        【任務一：意圖分類（Intent Classification）】
        請判斷使用者的輸入屬於以下哪一種意圖：
        1. "FOOD"：單一食材、飲料、料理名稱查詢（如：「水餃」、「蘋果」、「麻辣臭豆腐」）。
        2. "QUESTION"：健康衛教問答、飲食建議諮詢（如：「痛風可以吃豆漿嗎？」、「糖尿病早餐吃什麼好？」）。
        3. "GREETING"：無意義閒聊、問候、亂碼（如：「你好」、「早安」、「測試123」）。

        【任務二：依據意圖產出對應內容】
        - 若意圖為 "GREETING"：
          請在 `answer` 欄位禮貌地引導使用者，例如：「您好！我是您的專屬營養師。您可以輸入任何食物名稱讓我為您分析，或是詢問我健康飲食相關的問題喔！」
          其他紅綠燈欄位請填 "UNKNOWN"。
        
        - 若意圖為 "QUESTION"：
          請在 `answer` 欄位以臨床營養師的語氣給予解答（限200字以內，分段清晰，溫暖且專業）。
          其他紅綠燈欄位請填 "UNKNOWN"。

        - 若意圖為 "FOOD"：
          請採取「最嚴格、最保守」的態度給予紅綠燈判定：
          - 痛風：含有「肉湯、內臟、海鮮、高湯」 -> 判定 RED。
          - 高血壓：含有「麻辣、重鹹、醃漬物」 -> 判定 RED。
          - 糖尿病：含有「高糖、勾芡、精緻澱粉」 -> 判定 RED。
          - 高血脂：含有「油炸、肥肉、動物油」 -> 判定 RED。
          - "GREEN": 安全無負擔 / "YELLOW": 需嚴格控量 / "RED": 絕對地雷。

        你【必須】僅回傳一個 JSON 格式的字串，嚴格禁止包含 Markdown 區塊或多餘文字。
        JSON 格式範例：
        {{
            "intent": "FOOD 或 QUESTION 或 GREETING",
            "answer": "若為 QUESTION 或 GREETING 填寫回覆文字，若為 FOOD 則留空",
            "name": "{food_name}",
            "nutritional_analysis": "（僅 FOOD 需要填寫）客觀分析特性...",
            "gout": "RED/YELLOW/GREEN 或 UNKNOWN",
            "hypertension": "RED/YELLOW/GREEN 或 UNKNOWN",
            "diabetes": "RED/YELLOW/GREEN 或 UNKNOWN",
            "hyperlipidemia": "RED/YELLOW/GREEN 或 UNKNOWN",
            "reason": "（僅 FOOD 需要填寫）給長輩的一句話提醒，限50字以內"
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
            
            # 安全取得 intent，若無則預設為 FOOD（相容舊有邏輯）
            intent = parsed_data.get("intent", "FOOD")
            answer = parsed_data.get("answer", "")
            
            # 若為 FOOD 以外的意圖，但沒給 answer，我們給個預設值
            if intent in ["QUESTION", "GREETING"] and not answer:
                answer = "您好！請告訴我您想查詢什麼食物，或是有什麼飲食問題想問我呢？"
                
            # 轉換為與本地 FoodChecker 完全一致的輸出格式
            formatted_result = {
                "intent": intent,
                "answer": answer,
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
            # 萬一失敗，回傳 api_failed 標記
            return {
                "api_failed": True,
                "intent": "ERROR",
                "name": food_name,
                "individual_lights": {
                    "痛風": "UNKNOWN",
                    "高血壓": "UNKNOWN",
                    "糖尿病": "UNKNOWN",
                    "高血脂": "UNKNOWN"
                },
                "reason": "目前 AI 伺服器忙碌，暫時無法判斷燈號。建議您先詢問專業醫師。"
            }
