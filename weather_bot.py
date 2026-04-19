import requests
import json
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8789469759:AAGIeXhWe9FrG7218TUEvVfK4-I2Z34dg0o")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_weather(lat=25.0330, lon=121.5654):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
    r = requests.get(url).json()
    current = r["current_weather"]
    daily = r["daily"]
    return f"🌤 台灣台北天氣\n\n目前: {current['temperature']}°C\n風速: {current['windspeed']} km/h\n\n未來幾天:\n" + "\n".join([f"{daily['time'][i]}: {daily['temperature_2m_min'][i]}~{daily['temperature_2m_max'][i]}°C" for i in range(3)])

def get_news():
    try:
        url = "https://newsapi.org/v2/top-headlines?country=tw&apiKey=demo"
        r = requests.get(url).json()
        articles = r.get("articles", [])[:5]
        if not articles:
            return "📰 目前無法取得新聞"
        news = "📰 台灣新聞\n\n"
        for i, a in enumerate(articles, 1):
            news += f"{i}. {a.get('title', '無標題')}\n"
        return news
    except:
        return "📰 新聞服務待設定"

def get_stock(symbol="2330"):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.TW"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers).json()
        result = r.get("chart", {}).get("result", [])
        if result:
            meta = result[0].get("meta", {})
            price = meta.get("regularMarketPrice", "N/A")
            name = meta.get("symbol", symbol)
            return f"📈 {name} 台積電\n目前價格: {price} TWD"
        return f"📈 {symbol} 無法取得資料"
    except:
        return "📈 股市服務待設定"

def get_updates(offset):
    return requests.get(f"{API_URL}/getUpdates", params={"offset": offset}).json()

def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

print("🤖 Bot 啟動中... 按 Ctrl+C 停止")

offset = None
while True:
    try:
        updates = get_updates(offset)
        if updates["ok"]:
            for result in updates["result"]:
                offset = result["update_id"] + 1
                if "message" in result:
                    chat_id = result["message"]["chat"]["id"]
                    text = result["message"]["text"]
                    if "天氣" in text:
                        send_message(chat_id, get_weather())
                    elif "新聞" in text:
                        send_message(chat_id, get_news())
                    elif "股市" in text or "股票" in text:
                        send_message(chat_id, get_stock())
                    else:
                        send_message(chat_id, "📋 可用指令：\n• 天氣 - 查詢天氣\n• 新聞 - 查詢新聞\n• 股市 - 查詢台積電")
        time.sleep(1)
    except KeyboardInterrupt:
        break