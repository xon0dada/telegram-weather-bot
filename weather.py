"""
天氣模組 - 取得天氣資料
包含：天氣、天氣預報、天氣預警
"""

import requests

GEMINI_API_KEY = "AIzaSyABqGlwKaKo4lQQ4XYpA_FIUXNU61d9jfs"

def get_weather(lat=25.0330, lon=121.5654):
    """取得目前天氣"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
    r = requests.get(url).json()
    current = r["current_weather"]
    daily = r["daily"]
    temp_min = daily['temperature_2m_min'][0]
    temp_max = daily['temperature_2m_max'][0]
    return f"🌤 台灣台北天氣\n\n目前: {current['temperature']}°C\n風速: {current['windspeed']} km/h\n今天: {temp_min}~{temp_max}°C"

def get_weather_forecast(lat=25.0330, lon=121.5654):
    """取得一週天氣預報"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=7"
    try:
        r = requests.get(url).json()
        daily = r.get("daily", {})
        times = daily.get("time", [])
        maxTemps = daily.get("temperature_2m_max", [])
        minTemps = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])
        
        # 天氣代碼翻譯
        weather_desc = {
            0: "☀️ 晴", 1: "🌤️ 晴時多雲", 2: "⛅ 多雲", 3: "☁️ 陰",
            45: "🌫️ 霧", 48: "🌫️ 霧", 51: "🌧️ 小雨", 53: "🌧️ 中雨", 55: "🌧️ 大雨",
            61: "🌧️ 雨", 63: "🌧️ 雨", 65: "🌧️ 大雨", 71: "❄️ 雪", 73: "❄️ 雪",
            80: "🌧️ 陣雨", 81: "🌧️ 陣雨", 82: "🌧️ 強陣雨", 95: "⛈️ 雷雨", 96: "⛈️ 雷雨"
        }
        
        result = "📅 一週天氣預報\n\n"
        for i in range(min(7, len(times))):
            date = times[i][-5:]  # 取月日
            desc = weather_desc.get(codes[i], f"🌤️ {codes[i]}")
            result += f"{date}: {minTemps[i]}~{maxTemps[i]}°C {desc}\n"
        
        return result
    except:
        return "📅 無法取得天氣預報"

def get_weather_alert():
    """取得天氣預警 (地震、颱風)"""
    prompt = "請用繁體中文列出目前台灣的天氣預警，包括：\n1. 地震資訊（如果有）\n2. 颱風資訊（如果有）\n3. 其他天氣警訊\n如果沒有請說「目前沒有預警」。請只列出重點，不要超過3句。"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        if "candidates" in data:
            return "🔔 " + data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        pass
    
    return "🔔 目前無法取得預警資訊"

DEFAULT_LOCATION = (25.0330, 121.5654)

def set_location(lat, lon):
    global DEFAULT_LOCATION
    DEFAULT_LOCATION = (lat, lon)

def get_weather_yilan():
    """宜蘭天氣"""
    return get_weather(24.7021, 121.7377)

def get_weather_taichung():
    """台中天氣"""
    return get_weather(24.1477, 120.6736)

def get_weather_kaohsiung():
    """高雄天氣"""
    return get_weather(22.6273, 120.3014)