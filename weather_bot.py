"""
Telegram 智能機器人 - 完整版
功能：天氣、新聞、股市、電影、翻譯、匯率、預警
"""

import requests
import time
import os

import weather
import news as news_module
import stock

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8789469759:AAGIeXhWe9FrG7218TUEvVfK4-I2Z34dg0o")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
GEMINI_API_KEY = "AIzaSyABqGlwKaKo4lQQ4XYpA_FIUXNU61d9jfs"

conversation_history = {}

def get_ai_response(prompt, user_id):
    """帶記憶的 AI 對話"""
    history = conversation_history.get(user_id, [])
    
    context = ""
    if history:
        recent = history[-6:]
        for i in range(0, len(recent), 2):
            if i < len(recent):
                context += f"User: {recent[i]}\n"
            if i+1 < len(recent):
                context += f"You: {recent[i+1]}\n"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    full_prompt = f"""你是友善的台灣生活助手，用輕鬆自然的繁對話。

{context}
User: {prompt}

用自然對話回答。投資問題提醒只是參考。
"""
    
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        data = r.json()
        
        if "candidates" in data:
            response = data["candidates"][0]["content"]["parts"][0]["text"]
            
            if user_id not in conversation_history:
                conversation_history[user_id] = []
            conversation_history[user_id].append(prompt)
            conversation_history[user_id].append(response)
            
            if len(conversation_history[user_id]) > 20:
                conversation_history[user_id] = conversation_history[user_id][-20:]
            
            return response
    except:
        pass
    
    return "讓我、組織一下語言..."

def get_updates(offset):
    return requests.get(f"{API_URL}/getUpdates", params={"offset": offset}).json()

def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_menu(chat_id):
    menu = """📋 請選擇功能：

🌤 天氣 - 查詢目前天氣
📅 天氣預報 - 一週天氣
🔔 天氣預警 - 地震/颱風
📰 新聞 - 最新新聞
🎬 電影 - 熱映中電影
💱 匯率 - 美金/日幣/歐元

📈 股市 - 2330股價
📊 熱門股票 - Top 10
📉 評價 2330 - 本益比/殖利率

🌐 翻譯 hello - 中英翻譯
💬 聊天 - AI對話

💡 直接輸入功能名稱即可！"""
    send_message(chat_id, menu)

print("🤖 智能機器人啟動中...")

offset = None

while True:
    try:
        updates = get_updates(offset)
        
        if updates["ok"]:
            for result in updates["result"]:
                offset = result["update_id"] + 1
                
                if "message" in result:
                    chat_id = result["message"]["chat"]["id"]
                    user_id = str(chat_id)
                    text = result["message"]["text"]
                    text_lower = text.lower()
                    
                    # 選單
                    if "選單" in text or "功能" in text or "/start" in text:
                        send_menu(chat_id)
                    
                    # 天氣相關
                    elif "天氣預報" in text or "一週" in text or "一周" in text:
                        send_message(chat_id, weather.get_weather_forecast())
                    
                    elif "天氣預警" in text or "預警" in text or "地震" in text or "颱風" in text:
                        send_message(chat_id, weather.get_weather_alert())
                    
                    elif "天氣" in text:
                        send_message(chat_id, weather.get_weather())
                        
                    # 新聞電影
                    elif "電影" in text:
                        send_message(chat_id, news_module.get_movies())
                    
                    elif "新聞" in text:
                        send_message(chat_id, news_module.get_news())
                    
                    # 匯率
                    elif "匯率" in text:
                        send_message(chat_id, news_module.get_exchange_rate())
                    
                    # 翻譯
                    elif "翻譯" in text or "translate" in text_lower:
                        # 取出翻譯內容
                        import re
                        # 格式: 翻譯 hello 或 translate hello
                        match = re.search(r'[:\s]+([a-zA-Z].+)', text, re.IGNORECASE)
                        if match:
                            content = match.group(1).strip()
                            send_message(chat_id, news_module.translate_english(content))
                        else:
                            send_message(chat_id, "📝 格式：翻譯 hello（翻譯英文）\n或 翻譯 你好（翻譯成英文）")
                    
                    # 股市相關
                    elif "評價" in text or "本益比" in text or "殖利率" in text:
                        import re
                        match = re.search(r'(\d{4,6})', text)
                        symbol = match.group(1) if match else "2330"
                        send_message(chat_id, stock.get_valuation(symbol))
                        
                    elif "熱門" in text or "top" in text_lower:
                        send_message(chat_id, stock.get_top50())
                    
                    elif "股市" in text or "股票" in text:
                        import re
                        match = re.search(r'(\d{4,6})', text)
                        symbol = match.group(1) if match else "2330"
                        send_message(chat_id, stock.get_stock(symbol))
                    
                    elif "股市新聞" in text:
                        send_message(chat_id, stock.get_stock_news())
                    
                    # AI 對話
                    else:
                        send_message(chat_id, "🤔 讓我想一下...")
                        response = get_ai_response(text, user_id)
                        send_message(chat_id, response)
                        
                        send_message(chat_id, "\n💡 輸入「選單」查看所有功能")
        
        time.sleep(1)
        
    except KeyboardInterrupt:
        break