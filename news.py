import requests
from bs4 import BeautifulSoup
import re

URLS = [
    "https://news.ltn.com.tw/list/business",
    "https://www.setn.com/",
    "https://www.storm.mg/category/business"
]

def get_news():
    try:
        all_news = []
        for url in URLS:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                r = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(r.text, "html.parser")
                titles = soup.find_all("a", {"class": re.compile(r"(title|item-title)")})[:3]
                for t in titles:
                    text = t.get_text(strip=True)
                    if text and len(text) > 10:
                        all_news.append(text)
            except:
                continue
        if not all_news:
            return "📰 目前無法取得新聞"
        news = "📰 台灣新聞\n\n"
        for i, n in enumerate(all_news[:5], 1):
            news += f"{i}. {n[:50]}...\n"
        return news
    except:
        return "📰 新聞服務異常"

def get_taiwan_news():
    return get_news()