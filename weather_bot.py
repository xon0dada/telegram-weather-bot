"""
Telegram 智能機器人 - Web版
"""

from flask import Flask, request
import requests
import time
import os
import json
import re

import weather
import news as news_module
import stock
import ledger

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8789469759:AAGIeXhWe9FrG7218TUEvVfK4-I2Z34dg0o")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
GEMINI_API_KEY = "AIzaSyABqGlwKaKo4lQQ4XYpA_FIUXNU61d9jfs"

conversation_history = {}

def send_message(chat_id, text):
    """發送訊息"""
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

def get_ai_response(prompt, user_id):
    """AI 回覆"""
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
    full_prompt = f"""你是我的好朋友，我們在LINE上面聊天用。

{context}
對方說：{prompt}

請用輕鬆、自然、口語化的方式回覆，就像朋友聊天一樣。可以使用表情符號，但不要用列表或編號。盡量簡短一點。

如果聊到投資股票相關，要記得說「這只是參考喔，投資有風險～」
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
            conversation_history[user_id].extend([prompt, response])
            if len(conversation_history[user_id]) > 20:
                conversation_history[user_id] = conversation_history[user_id][-20:]
            return response
    except:
        pass
    return "👀 讓我想想..."

def handle_message(chat_id, text, user_id):
    """處理訊息"""
    text_lower = text.lower()
    
    # 選單
    if "選單" in text or "功能" in text or "/start" in text:
        menu = """📋 請選擇功能：

🌤 天氣 - 天氣
📅 天氣預報 - 一週天氣  
📝 分類 - 分類清單
📊 餘額 - 查看餘額
📝 記錄 - 查看記錄

💰 收入 500 - 記錄收入
💸 支出 300 - 記錄支出
"""
        send_message(chat_id, menu)
    
    # 天氣
    elif "天氣預報" in text or "一週" in text:
        send_message(chat_id, weather.get_weather_forecast())
    elif "天氣" in text:
        send_message(chat_id, weather.get_weather())
    
    # 記帳
    elif "收入" in text or ("+" in text and re.search(r'\d', text)):
        match = re.search(r'(\d+)', text)
        if match:
            amount = int(match.group(1))
            note = text.replace("收入", "").replace("+", "").replace(str(amount), "").strip()
            send_message(chat_id, ledger.add_income(amount, note))
    
    elif "支出" in text or "-" in text:
        match = re.search(r'(\d+)', text)
        if match:
            amount = int(match.group(1))
            category = "📦 其他"
            cats = ["餐飲", "交通", "購物", "娛樂", "醫療", "房租", "投資", "電話", "電費", "3C", "服飾", "禮物", "旅遊", "學習", "寵物"]
            cat_emojis = {"餐飲": "🍔 餐飲", "交通": "🚗 交通", "購物": "🛒 購物", "娛樂": "🎬 娛樂", "醫療": "🏥 醫療", "房租": "🏠 房租", "投資": "💰 投資", "電話": "📱 電話", "電費": "💡 電費", "3C": "💻 3C", "服飾": "👕 服飾", "禮物": "🎁 禮物", "旅遊": "✈️ 旅遊", "學習": "📚 學習", "寵物": "🐱 寵物"}
            for cat in cats:
                if cat in text:
                    category = cat_emojis.get(cat, f"📦 {cat}")
                    text = text.replace(cat, "")
                    break
            note = re.sub(r'\d+', '', text).replace("支出", "").replace("-", "").strip()
            send_message(chat_id, ledger.add_expense(amount, category, note if note else "-"))
    
    elif "餘額" in text or "帳本" in text:
        send_message(chat_id, ledger.get_balance())
    elif "記錄" in text:
        send_message(chat_id, ledger.get_records())
    elif "分類" in text:
        send_message(chat_id, ledger.get_categories())
    elif "清除" in text:
        send_message(chat_id, ledger.clear_records())
    
    # AI 對話
    else:
        send_message(chat_id, "🤔 讓我想一下...")
        response = get_ai_response(text, user_id)
        send_message(chat_id, response)

@app.route("/", methods=["POST"])
def webhook():
    """Webhook 處理"""
    try:
        update = request.get_json()
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            user_id = str(chat_id)
            text = update["message"].get("text", "")
            handle_message(chat_id, text, user_id)
    except:
        pass
    return "OK"

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)