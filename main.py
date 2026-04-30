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
    TextMessageContent,
    PostbackEvent
)
from linebot.v3.messaging import TextMessage
from dotenv import load_dotenv

# 讀取環境變數
load_dotenv()
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 確保載入自訂的 food_logic
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from food_logic.checker import FoodChecker
from food_logic.gemini_checker import GeminiChecker

app = FastAPI()

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    print("警告：尚未設定 LINE_CHANNEL_SECRET 或 LINE_CHANNEL_ACCESS_TOKEN。請檢查 .env 檔案。")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 實例化我們的「大腦」
checker = FoodChecker()
ai_checker = None

from food_logic.tracker import DietTracker
tracker = DietTracker()

# 如果有設定 Gemini API Key，才啟用 AI 模式
if os.getenv("GEMINI_API_KEY"):
    try:
        ai_checker = GeminiChecker()
        print("✅ 成功啟用 Gemini AI 智慧外掛")
    except Exception as e:
        print(f"❌ Gemini AI 載入失敗：{e}")
else:
    print("ℹ️ 尚未設定 GEMINI_API_KEY，AI 外掛暫時停用。")

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
    
    if user_text == "撤銷紀錄":
        removed = tracker.delete_last_record()
        if removed:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=f"🗑️ 已成功撤銷上一筆紀錄！\n原紀錄：【{removed.get('meal_type')}】{removed.get('food_name')}")]
                    )
                )
        else:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="💡 目前資料庫中沒有可供撤銷的飲食紀錄喔！")]
                    )
                )
        return
        
    if user_text in ["記錄喝水", "喝水", "【選單】記錄喝水"]:
        water_amount = 100
        tracker.log_water(water_amount)
        
        # 取得今日飲水進度
        summary_data = tracker.get_daily_summary()
        water_total = summary_data["summary"].get("water_total", 0)
        remaining = max(0, 2000 - water_total)
        
        msg = f"💧 咕嚕咕嚕！已為您記錄 {water_amount}cc。\n今日已喝 {water_total} / 2000 cc"
        if remaining > 0:
            msg += f"，還差 {remaining}cc 就達標囉，繼續保持！"
        else:
            msg += f"🎉 恭喜！今日飲水目標 2000cc 已經順利達標囉！"
            
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=msg)]
                )
            )
        return
    days_to_query = 0
    if user_text in ["健康週報", "每週總結", "本週報告", "【選單】健康週報"]:
        days_to_query = 7
    elif user_text in ["健康月報", "每月總結", "本月報告", "【選單】健康月報"]:
        days_to_query = 30
    else:
        # 嘗試解析自填天數
        cleaned_text = user_text.replace("天", "").strip()
        if cleaned_text.isdigit():
            days_to_query = int(cleaned_text)
            
    if days_to_query > 0:
        summary_data = tracker.get_range_summary(days=days_to_query)
        summary = summary_data["summary"]
        
        msg = f"📊 【長期飲食健康報告】\n"
        msg += f"📅 統計區間：{summary_data['start_date']} ~ {summary_data['end_date']}\n"
        msg += f"⏱️ 總天數：共計 {summary_data['days']} 天\n"
        msg += f"────────────────\n"
        msg += f"🟢 推薦安全 (綠燈): {summary['GREEN']} 次\n"
        msg += f"🟡 控量食用 (黃燈): {summary['YELLOW']} 次\n"
        msg += f"🔴 地雷禁忌 (紅燈): {summary['RED']} 次\n"
        msg += f"💧 飲水總計: {summary.get('water_total', 0)} cc\n"
        msg += f"────────────────\n"
        
        if summary["total"] == 0 and summary.get("water_total", 0) == 0:
            msg += f"💡 您在這段期間還沒有記錄任何飲食或水分喔！"
        else:
            red_ratio = 0
            if summary["total"] > 0:
                red_ratio = (summary["RED"] / summary["total"]) * 100
                
            if summary["total"] == 0:
                msg += f"💧 這段期間只有記錄水份，記得也要多吃健康食物喔！"
            elif summary["RED"] == 0:
                msg += f"🎉 完美的防守戰果！您這段期間完全沒有吃到地雷紅燈，請繼續保持這項傲人的健康紀錄！"
            elif red_ratio > 30:
                msg += f"⚠️ 警訊：紅燈食物比例達 {red_ratio:.1f}%。請務必重新檢視飲食清單，並多喝水與諮詢專業醫師。"
            else:
                msg += f"💪 戰果統計：紅燈比例約為 {red_ratio:.1f}%。整體表現不錯，但仍有進步空間，繼續加油！"
                
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=msg)]
                )
            )
        return

    if user_text in ["今日總結", "今天吃了什麼", "查詢紀錄", "查看總結", "【選單】今日總結", "【選單】查看紀錄"]:
        summary_data = tracker.get_daily_summary()
        summary = summary_data["summary"]
        records = summary_data["records"]
        
        if summary["total"] == 0 and summary.get("water_total", 0) == 0:
            msg = "💡 您今天還沒有記錄任何飲食或喝水喔！\n點選下方選單就可以開始記錄了！"
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=msg)])
                )
            return
            
        # 建立一體化的 FlexMessage
        contents = [
            {
                "type": "text",
                "text": f"📅 日期：{summary_data['date']}",
                "size": "sm",
                "color": "#888888"
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "spacing": "sm",
                "contents": [
                    {"type": "text", "text": f"🟢 推薦安全 (綠燈): {summary['GREEN']} 份", "weight": "bold", "color": "#28a745"},
                    {"type": "text", "text": f"🟡 控量食用 (黃燈): {summary['YELLOW']} 份", "weight": "bold", "color": "#ffc107"},
                    {"type": "text", "text": f"🔴 地雷禁忌 (紅燈): {summary['RED']} 份", "weight": "bold", "color": "#dc3545"},
                    {"type": "text", "text": f"💧 今日飲水進度: {summary.get('water_total', 0)} / 2000 cc", "weight": "bold", "color": "#17a2b8"}
                ]
            },
            {"type": "separator", "margin": "lg"},
            {
                "type": "text",
                "text": "📋 詳細飲食清單：",
                "weight": "bold",
                "size": "md",
                "margin": "lg"
            }
        ]
        
        for rec in records:
            emoji = {"RED": "🔴", "YELLOW": "🟡", "GREEN": "🟢", "WATER": "💧"}.get(rec.get("light"), "⚪")
            row = {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "alignItems": "center",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{emoji} 【{rec.get('meal_type')}】\n{rec.get('food_name')}",
                        "wrap": True,
                        "size": "sm",
                        "flex": 3
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "color": "#FF4D4D",
                        "height": "sm",
                        "flex": 1,
                        "action": {
                            "type": "postback",
                            "label": "刪除",
                            "data": f"action=delete_by_ts&ts={rec.get('timestamp')}"
                        }
                    }
                ]
            }
            contents.append(row)
            contents.append({"type": "separator", "margin": "xs"})
            
        if len(records) > 0:
            contents = contents[:-1]
            
        # 醫護叮嚀
        if summary["RED"] > 0:
            advice = f"⚠️ 貼心醫護提醒：您今天吃到了 {summary['RED']} 次地雷紅燈食物。接下來要記得多補充水分幫助代謝，嚴格避開高油鹽料理喔！"
        elif summary["total"] > 0:
            advice = f"🎉 太棒了！您今天完全沒有吃到任何地雷紅燈食物！請繼續維持無負擔的完美飲食！"
        else:
            advice = f"💧 今天只記錄了水分，記得也要按時吃點健康的食物喔！"
            
        contents.append({"type": "separator", "margin": "lg"})
        contents.append({
            "type": "text",
            "text": advice,
            "wrap": True,
            "size": "sm",
            "color": "#555555",
            "margin": "lg"
        })
        
        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "📊 今日飲食健康總結", "weight": "bold", "size": "lg", "color": "#FFFFFF"}
                ],
                "backgroundColor": "#2D3E50"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents
            }
        }
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text="您的今日飲食健康總結", contents=FlexContainer.from_dict(bubble))]
                )
            )
        return

    if user_text in ["刪除紀錄", "編輯紀錄", "【選單】刪除紀錄"]:
        summary_data = tracker.get_daily_summary()
        records = summary_data["records"]
        
        if not records:
            msg = "💡 您今天還沒有任何飲食紀錄，無資料可刪除喔！"
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=msg)])
                )
            return
            
        # 建立 FlexMessage 的刪除按鈕卡片
        contents = []
        for rec in records:
            emoji = {"RED": "🔴", "YELLOW": "🟡", "GREEN": "🟢"}.get(rec.get("light"), "⚪")
            row = {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "alignItems": "center",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{emoji} 【{rec.get('meal_type')}】\n{rec.get('food_name')}",
                        "wrap": True,
                        "weight": "bold",
                        "size": "sm",
                        "flex": 3
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "color": "#FF4D4D",
                        "height": "sm",
                        "flex": 1,
                        "action": {
                            "type": "postback",
                            "label": "刪除",
                            "data": f"action=delete_by_ts&ts={rec.get('timestamp')}"
                        }
                    }
                ]
            }
            contents.append(row)
            contents.append({"type": "separator", "margin": "md"})
            
        # 包裝成單張 Bubble
        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "🗑️ 刪除飲食紀錄", "weight": "bold", "size": "lg", "color": "#FFFFFF"}
                ],
                "backgroundColor": "#FF4D4D"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents[:-1] # 去掉最後一個多餘的 separator
            }
        }
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text="編輯/刪除您的飲食紀錄", contents=FlexContainer.from_dict(bubble))]
                )
            )
        return

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
        if ai_checker:
            # 呼叫 Gemini AI
            result = ai_checker.check_food_with_ai(user_text)
            
            # 防呆機制 1：若 API 呼叫失敗（例如 Quota Exceeded）
            if result.get("api_failed"):
                reply_message = TextMessage(
                    text=f"💡 目前 AI 分析系統連線人數過多（伺服器忙碌中）。請稍等幾分鐘後再試試看喔！"
                )
            # 防呆機制 2：若 AI 判定輸入的不是食物
            elif result.get("is_food") == False:
                reply_message = TextMessage(
                    text=f"💡 系統偵測到「{user_text}」似乎不是食物或飲料喔！\n您可以試著輸入像「麻辣臭豆腐」或「高麗菜」等具體名稱，我會立刻為您進行健康分析！"
                )
            else:
                lights = result.get("individual_lights", {})
                
                def get_emoji(light_code):
                    return {"RED": "🔴", "YELLOW": "🟡", "GREEN": "🟢"}.get(light_code, "⚪")
                    
                # 判定 AI 綜合燈號
                weights = {"RED": 3, "YELLOW": 2, "GREEN": 1, "UNKNOWN": 0}
                max_weight = 0
                final_light = "GREEN"
                for cond_light in lights.values():
                    if weights.get(cond_light, 0) > max_weight:
                        max_weight = weights[cond_light]
                        final_light = cond_light
    
                # 建立單張 AI 卡片
            bubble = {
                "type": "bubble",
                "size": "kilo",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{result['name']} (AI分析)",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#FFFFFF"
                        }
                    ],
                    "backgroundColor": "#6A5ACD" # 紫色表頭，區別於本地資料庫
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
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "color": "#28a745",
                                    "height": "sm",
                                    "action": {
                                        "type": "postback",
                                        "label": "記早餐",
                                        "data": f"action=log_meal&meal=早餐&food={result['name']}&light={final_light}"
                                    }
                                },
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "color": "#28a745",
                                    "height": "sm",
                                    "action": {
                                        "type": "postback",
                                        "label": "記午餐",
                                        "data": f"action=log_meal&meal=午餐&food={result['name']}&light={final_light}"
                                    }
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "color": "#28a745",
                                    "height": "sm",
                                    "action": {
                                        "type": "postback",
                                        "label": "記晚餐",
                                        "data": f"action=log_meal&meal=晚餐&food={result['name']}&light={final_light}"
                                    }
                                },
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "color": "#28a745",
                                    "height": "sm",
                                    "action": {
                                        "type": "postback",
                                        "label": "記點心",
                                        "data": f"action=log_meal&meal=點心&food={result['name']}&light={final_light}"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            
            if not result.get("is_food", True) == False and not result.get("api_failed"):
                reply_message = FlexMessage(
                    alt_text=f"AI 為您分析「{user_text}」的營養成分",
                    contents=FlexContainer.from_dict({"type": "carousel", "contents": [bubble]})
                )
        else:
            reply_message = TextMessage(
                text=f"🔍 找不到與「{user_text}」相關的食材。\n\n"
                     "💡 建議您輸入更簡短的關鍵字。"
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
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "color": "#28a745",
                                    "height": "sm",
                                    "action": {
                                        "type": "postback",
                                        "label": "記早餐",
                                        "data": f"action=log_meal&meal=早餐&food={result['name']}&light={result.get('light', 'UNKNOWN')}"
                                    }
                                },
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "color": "#28a745",
                                    "height": "sm",
                                    "action": {
                                        "type": "postback",
                                        "label": "記午餐",
                                        "data": f"action=log_meal&meal=午餐&food={result['name']}&light={result.get('light', 'UNKNOWN')}"
                                    }
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "color": "#28a745",
                                    "height": "sm",
                                    "action": {
                                        "type": "postback",
                                        "label": "記晚餐",
                                        "data": f"action=log_meal&meal=晚餐&food={result['name']}&light={result.get('light', 'UNKNOWN')}"
                                    }
                                },
                                {
                                    "type": "button",
                                    "style": "primary",
                                    "color": "#28a745",
                                    "height": "sm",
                                    "action": {
                                        "type": "postback",
                                        "label": "記點心",
                                        "data": f"action=log_meal&meal=點心&food={result['name']}&light={result.get('light', 'UNKNOWN')}"
                                    }
                                }
                            ]
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

@handler.add(PostbackEvent)
def handle_postback(event):
    import urllib.parse
    data = event.postback.data
    params = dict(urllib.parse.parse_qsl(data))
    
    if params.get("action") == "log_meal":
        meal_type = params.get("meal")
        food_name = params.get("food")
        light = params.get("light", "UNKNOWN")
        portion = "一份"
        
        tracker.log_meal(meal_type, food_name, light, portion)
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"✅ 已成功為您記錄今日【{meal_type}】！\n食物：{food_name}\n份量：{portion}\n\n💡 貼心提醒：若您按錯了，只要對我回覆「撤銷紀錄」這四個字，就可以刪除此筆記錄囉！")]
                )
            )
            
    elif params.get("action") == "delete_by_ts":
        ts = params.get("ts")
        removed = tracker.delete_record_by_timestamp(ts)
        
        if removed:
            msg = f"🗑️ 已成功為您刪除紀錄！\n原資料：【{removed.get('meal_type')}】{removed.get('food_name')}"
        else:
            msg = "💡 刪除失敗，該筆紀錄可能已被移除。"
            
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=msg)]
                )
            )

if __name__ == "__main__":
    import uvicorn
    # 讀取雲端環境變數中的 PORT，如果沒有則預設使用 8000
    port = int(os.environ.get("PORT", 8000))
    # 雲端部署必須設定 host="0.0.0.0" 以接受外部連線
    uvicorn.run("main:app", host="0.0.0.0", port=port)
