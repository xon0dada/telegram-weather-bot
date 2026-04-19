import requests
import json
import time

BOT_TOKEN = "8789469759:AAGIeXhWe9FrG7218TUEvVfK4-I2Z34dg0o"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_weather(lat=25.0330, lon=121.5654):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
    r = requests.get(url).json()
    current = r["current_weather"]
    daily = r["daily"]
    return f"🌤 台灣台北天氣\n\n目前: {current['temperature']}°C\n風速: {current['windspeed']} km/h\n\n未來幾天:\n" + "\n".join([f"{daily['time'][i]}: {daily['temperature_2m_min'][i]}~{daily['temperature_2m_max'][i]}°C" for i in range(3)])

def get_updates(offset):
    return requests.get(f"{API_URL}/getUpdates", params={"offset": offset}).json()

def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

print("🤖 Weather Bot 啟動中... 按 Ctrl+C 停止")

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
                        weather = get_weather()
                        send_message(chat_id, weather)
                    else:
                        send_message(chat_id, "請輸入「天氣」查詢天氣資訊")
        time.sleep(1)
    except KeyboardInterrupt:
        break