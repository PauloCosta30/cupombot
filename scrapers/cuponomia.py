import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

URL = "https://www.cuponomia.com.br/cupons"

def scrape_cuponomia() -> list[dict]:
    coupons = []
    try:
        r = requests.get(URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("article, [class*='coupon-card']")

        for card in cards[:10]:
            store_el = card.select_one("[class*='store'], [class*='brand']")
            code_el = card.select_one("[class*='code'], code")
            disc_el = card.select_one("[class*='discount'], [class*='off']")
            link_el = card.select_one("a[href]")
            valid_el = card.select_one("[class*='expir'], [class*='valid']")
            title_el = card.select_one("h2, h3, [class*='title']")

            store = store_el.text.strip() if store_el else "Cuponomia"
            code = code_el.text.strip() if code_el else "SEM CODIGO"
            disc = disc_el.text.strip() if disc_el else ""
            link = link_el["href"] if link_el else URL
            valid = valid_el.text.strip() if valid_el else "Ver no link"
            title = title_el.text.strip() if title_el else "Oferta"

            if not link.startswith("http"):
                link = "https://www.cuponomia.com.br" + link

            coupons.append({
                "id": f"cuponomia_{code}_{store[:15]}",
                "title": f"[{store}] {title[:60]}",
                "code": code,
                "discount": disc,
                "link": link,
                "valid": valid,
            })
    except Exception as e:
        print(f"cuponomia err: {e}")

    return coupons
