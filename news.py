"""
新聞模組 - 新聞、電影、翻譯
"""

import requests
import re

GEMINI_API_KEY = "AIzaSyABqGlwKaKo4lQQ4XYpA_FIUXNU61d9jfs"

def get_news():
    """取得台灣新聞"""
    prompt = "請用繁體中文列出 5 條 台灣 最重要的最新新聞標題，一行一條"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.post(url, json=payload, headers=headers)
        data = r.json()
        if "candidates" in data:
            return "📰 " + data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        pass
    return "📰 新聞服務異常"

def get_movies():
    """取得熱映電影"""
    try:
        url = "https://movies.yahoo.com.tw/rss/focus.xml"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)
        
        # 嘗試解析 XML
        if "channel" in r.text:
            prompt = "請列出目前 Yahoo 熱映中的 5 部電影，用繁體中文，一行一條"
            return get_movies_ai(prompt)
    except:
        pass
    
    return get_movies_ai("請列出目前台灣熱映中的 5 部電影，一行一條")

def get_movies_ai(prompt):
    """用 AI 取得電影資訊"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        if "candidates" in data:
            return "🎬 " + data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        pass
    return "🎬 無法取得電影資訊"

def translate(text, target="en"):
    """
    翻譯功能
    text: 要翻譯的文字
    target: 目標語言 (en=英文, zh=中文, ja=日文)
    """
    lang_map = {"en": "英文", "zh": "中文", "ja": "日文", "ko": "韓文", "fr": "法文", "de": "德文"}
    lang = lang_map.get(target, "英文")
    
    prompt = f"請把以下文字翻譯成 {lang}：\n{text}"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        if "candidates" in data:
            result = data["candidates"][0]["content"]["parts"][0]["text"]
            return f"🌐 翻譯結果：\n{result}"
    except:
        pass
    return "🌐 翻譯失敗"

def translate_english(text):
    """翻譯成英文"""
    return translate(text, "en")

def translate_chinese(text):
    """翻譯成中文"""
    return translate(text, "zh")

def translate_japanese(text):
    """翻譯成日文"""
    return translate(text, "ja")

def get_exchange_rate():
    """取得匯率"""
    prompt = "請列出最新的匯率：\n1. USD 對 TWD（美金換台幣）\n2. JPY 對 TWD（日幣換台幣）\n3. EUR 對 TWD（歐元換台幣）\n只列出數字，大約值即可"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        if "candidates" in data:
            return "💱 " + data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        pass
    return "💱 無法取得匯率"

def get_taiwan_news():
    return get_news()