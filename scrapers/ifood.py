import requests
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

SOURCES = [
    "https://www.cuponomia.com.br/cupons/ifood",
    "https://pelando.com.br/tag/ifood",
]

def scrape_ifood() -> list[dict]:
    coupons = []
    
    try:
        r = requests.get(SOURCES[0], headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("article, [class*='coupon'], [class*='offer']")
        for card in cards[:10]:
            code_el = card.select_one("[class*='code'], code")
            disc_el = card.select_one("[class*='discount'], [class*='off']")
            link_el = card.select_one("a[href]")
            valid_el = card.select_one("[class*='expir'], [class*='valid']")
            title_el = card.select_one("h2, h3, [class*='title']")

            code = code_el.text.strip() if code_el else "SEM CODIGO"
            disc = disc_el.text.strip() if disc_el else ""
            link = link_el["href"] if link_el else "https://www.ifood.com.br"
            valid = valid_el.text.strip() if valid_el else "Sem data"
            title = title_el.text.strip() if title_el else "Cupom iFood"

            if not link.startswith("http"):
                link = "https://www.cuponomia.com.br" + link

            coupons.append({
                "id": f"ifood_cuponomia_{code}",
                "title": title[:80],
                "code": code,
                "discount": disc,
                "link": link,
                "valid": valid,
            })
    except Exception as e:
        print(f"ifood cuponomia err: {e}")

    try:
        r = requests.get(SOURCES[1], headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("article, [class*='deal']")
        for card in cards[:5]:
            title_el = card.select_one("h2, h3, [class*='title']")
            link_el = card.select_one("a[href]")
            disc_el = card.select_one("[class*='price'], [class*='discount']")

            title = title_el.text.strip() if title_el else "Deal iFood"
            link = link_el["href"] if link_el else SOURCES[1]
            disc = disc_el.text.strip() if disc_el else ""

            if not link.startswith("http"):
                link = "https://pelando.com.br" + link

            match = re.search(r'\b([A-Z0-9]{4,15})\b', title)
            code = match.group(1) if match else "VER LINK"

            coupons.append({
                "id": f"ifood_pelando_{title[:30]}",
                "title": title[:80],
                "code": code,
                "discount": disc,
                "link": link,
                "valid": "Ver no link",
            })
    except Exception as e:
        print(f"ifood pelando err: {e}")

    return coupons
