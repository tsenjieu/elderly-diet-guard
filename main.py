import os
import sys
from fastapi import FastAPI, Request, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from dotenv import load_dotenv

# 讀取環境變數
load_dotenv()
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 確保載入自訂的 food_logic
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from food_logic.checker import FoodChecker

app = FastAPI()

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    print("警告：尚未設定 LINE_CHANNEL_SECRET 或 LINE_CHANNEL_ACCESS_TOKEN。請檢查 .env 檔案。")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 實例化我們的「大腦」
try:
    checker = FoodChecker()
    print("✅ 成功載入舒酸與三高核心資料庫")
except Exception as e:
    print(f"❌ 資料庫載入失敗：{e}")

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_str = body.decode("utf-8")
    
    try:
        handler.handle(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature. Please check your channel secret.")
    except Exception as e:
        print(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text.strip()
    
    # 攔截圖文選單的專屬指令
    is_menu_command = False
    if user_text.startswith("【選單】"):
        is_menu_command = True
        command = user_text.replace("【選單】", "").strip()
        
        if command == "推薦蔬菜":
            matched_names = ["高麗菜", "空心菜", "地瓜葉", "小白菜", "青江菜", "秋葵", "蘿蔔"]
        elif command == "推薦水果":
            matched_names = ["芭樂", "蘋果", "奇異果", "木瓜", "番茄", "水梨"]
        elif command == "紅燈地雷":
            matched_names = ["豬肝", "乾香菇", "皮蛋", "水煎包", "鹹酥雞", "臭豆腐", "蚵仔煎"]
        else:
            matched_names = []
    else:
        # 一般自由輸入搜尋
        matched_names = checker.search_foods(user_text)
    
    if not matched_names:
        reply_message = TextMessage(
            text=f"🔍 找不到與「{user_text}」相關的食材。\n\n"
                 "💡 建議您輸入更簡短的關鍵字（例如：將『高麗菜炒肉絲』改成『高麗菜』或『豬肉』）。"
        )
    else:
        # Carousel 最多支援 12 張卡片，我們取前 10 筆
        limit = 10
        bubbles = []
        
        for matched_name in matched_names[:limit]:
            conditions = ["痛風", "高血壓", "糖尿病", "高血脂"]
            result = checker.check_food(matched_name, conditions)
            lights = result.get("individual_lights", {})
            
            def get_emoji(light_code):
                return {"RED": "🔴", "YELLOW": "🟡", "GREEN": "🟢"}.get(light_code, "⚪")
                
            # 建立單張卡片 (Bubble) 的字典結構
            bubble = {
                "type": "bubble",
                "size": "kilo",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{result['name']}",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#FFFFFF"
                        }
                    ],
                    "backgroundColor": "#2D3E50" # 深藍色質感表頭
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": f"痛風 {get_emoji(lights.get('痛風'))}", "size": "md", "weight": "bold"},
                                {"type": "text", "text": f"血壓 {get_emoji(lights.get('高血壓'))}", "size": "md", "weight": "bold"}
                            ],
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": f"血糖 {get_emoji(lights.get('糖尿病'))}", "size": "md", "weight": "bold"},
                                {"type": "text", "text": f"血脂 {get_emoji(lights.get('高血脂'))}", "size": "md", "weight": "bold"}
                            ],
                            "margin": "md"
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": f"📝 {result['reason']}",
                            "wrap": True,
                            "size": "sm",
                            "color": "#666666",
                            "margin": "lg",
                            "maxLines": 5
                        }
                    ]
                }
            }
            bubbles.append(bubble)
            
        # 將所有卡片包裝成 Carousel
        carousel = {
            "type": "carousel",
            "contents": bubbles
        }
        
        reply_message = FlexMessage(
            alt_text=f"為您找到 {len(matched_names)} 筆與「{user_text}」相關的食材",
            contents=FlexContainer.from_dict(carousel)
        )

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply_message]
            )
        )

if __name__ == "__main__":
    import uvicorn
    # 讀取雲端環境變數中的 PORT，如果沒有則預設使用 8000
    port = int(os.environ.get("PORT", 8000))
    # 雲端部署必須設定 host="0.0.0.0" 以接受外部連線
    uvicorn.run("main:app", host="0.0.0.0", port=port)
