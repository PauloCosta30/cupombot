import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

URL = "https://pelando.com.br/cupons"

def scrape_pelando() -> list[dict]:
    coupons = []
    try:
        r = requests.get(URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("article, [class*='coupon']")

        for card in cards[:10]:
            store_el = card.select_one("[class*='store'], [class*='brand']")
            code_el = card.select_one("[class*='code'], code")
            disc_el = card.select_one("[class*='discount'], [class*='off']")
            link_el = card.select_one("a[href]")
            valid_el = card.select_one("[class*='expir'], time")
            title_el = card.select_one("h2, h3, [class*='title']")

            store = store_el.text.strip() if store_el else "Pelando"
            code = code_el.text.strip() if code_el else "VER LINK"
            disc = disc_el.text.strip() if disc_el else ""
            link = link_el["href"] if link_el else URL
            valid = valid_el.text.strip() if valid_el else "Ver no link"
            title = title_el.text.strip() if title_el else "Oferta Pelando"

            if not link.startswith("http"):
                link = "https://pelando.com.br" + link

            coupons.append({
                "id": f"pelando_{code}_{title[:20]}",
                "title": f"[{store}] {title[:60]}",
                "code": code,
                "discount": disc,
                "link": link,
                "valid": valid,
            })
    except Exception as e:
        print(f"pelando err: {e}")

    return coupons
