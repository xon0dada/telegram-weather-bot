"""
Telegram 天氣機器人主程式 - 智能互動版
功能：
- 天氣查詢、新聞查詢、股市查詢
- AI 智慧對話（帶記憶）
- 互動選單
"""

import requests
import time
import os

import weather
import news
import stock

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8789469759:AAGIeXhWe9FrG7218TUEvVfK4-I2Z34dg0o")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
GEMINI_API_KEY = "AIzaSyABqGlwKaKo4lQQ4XYpA_FIUXNU61d9jfs"

# 對話記憶（Simple）
conversation_history = {}

def get_ai_response(prompt, user_id):
    """
    帶記憶的 AI 對話
    會記住之前的對話
    """
    # 取得歷史
    history = conversation_history.get(user_id, [])
    
    # 建立對話上下文
    context = ""
    if history:
        # 取最近 3 輪對話
        recent = history[-6:]  # 3 questions + 3 answers
        for i in range(0, len(recent), 2):
            if i < len(recent):
                context += f"使用者: {recent[i]}\n"
            if i+1 < len(recent):
                context += f"你: {recent[i+1]}\n"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    full_prompt = f"""你是一個友善的台灣資訊助手，請用輕鬆自然的繁體中文對話。

{context}
使用者: {prompt}

請用自然的對話方式回答，不要用列表格式。如果涉及投資，請提醒這只是參考。
"""
    
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        data = r.json()
        
        if "candidates" in data:
            response = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # 記住對話
            if user_id not in conversation_history:
                conversation_history[user_id] = []
            conversation_history[user_id].append(prompt)
            conversation_history[user_id].append(response)
            
            # 只記住最近 10 輪
            if len(conversation_history[user_id]) > 20:
                conversation_history[user_id] = conversation_history[user_id][-20:]
            
            return response
    except:
        pass
    
    return "嗯...讓我想一想再回答你～"

def get_updates(offset):
    return requests.get(f"{API_URL}/getUpdates", params={"offset": offset}).json()

def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_menu(chat_id):
    """發送互動選單"""
    menu = """📋 請選擇功能：

1️⃣ 天氣 - 查詢天氣
2️⃣ 新聞 - 最新新聞
3️⃣ 股市 - 查詢股價
4️⃣ 熱門 - 熱門股票
5️⃣ 股市新聞 - 股市新聞
6️⃣ 評價 2330 - 本益比/殖利率

💬 或者直接問我任何問題！"""
    send_message(chat_id, menu)

print("🤖 智能機器人啟動中...")
print("💡 輸入「選單」或「功能」查看選單")

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
                    
                    # 歡迎新使用者 或 輸入選單
                    if "選單" in text or "功能" in text or "/start" in text:
                        send_menu(chat_id)
                        
                    elif "天氣" in text:
                        send_message(chat_id, weather.get_weather())
                        
                    elif "新聞" in text and "股市" not in text:
                        send_message(chat_id, news.get_news())
                        
                    elif "股市" in text or "股票" in text:
                        import re
                        match = re.search(r'(\d{4,6})', text)
                        symbol = match.group(1) if match else "2330"
                        
                        if "評價" in text or "本益比" in text or "殖利率" in text:
                            send_message(chat_id, stock.get_valuation(symbol))
                        else:
                            send_message(chat_id, stock.get_stock(symbol))
                        
                    elif "熱門" in text or "TOP" in text.upper():
                        send_message(chat_id, stock.get_top50())
                    
                    elif "股市新聞" in text:
                        send_message(chat_id, stock.get_stock_news())
                    
                    # 其他交給 AI（帶記憶）
                    else:
                        # 回覆思考中
                        send_message(chat_id, "🤔 讓我想想...")
                        
                        response = get_ai_response(text, user_id)
                        send_message(chat_id, response)
                        
                        # 提醒可以用選單
                        send_message(chat_id, "\n💡 輸入「選單」查看所有功能～")
        
        time.sleep(1)
        
    except KeyboardInterrupt:
        break