import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

SOURCES = [
    ("https://www.cuponomia.com.br/cupons/mercado-livre", "ml_cuponomia", "https://www.cuponomia.com.br"),
    ("https://pelando.com.br/tag/mercado-livre", "ml_pelando", "https://pelando.com.br"),
]

def scrape_mercadolivre() -> list[dict]:
    coupons = []

    for url, prefix, base in SOURCES:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("article, [class*='coupon'], [class*='offer']")

            for card in cards[:8]:
                code_el = card.select_one("[class*='code'], code")
                disc_el = card.select_one("[class*='discount'], [class*='off']")
                link_el = card.select_one("a[href]")
                valid_el = card.select_one("[class*='expir'], [class*='valid']")
                title_el = card.select_one("h2, h3, [class*='title']")

                code = code_el.text.strip() if code_el else "SEM CODIGO"
                disc = disc_el.text.strip() if disc_el else ""
                link = link_el["href"] if link_el else "https://www.mercadolivre.com.br"
                valid = valid_el.text.strip() if valid_el else "Ver no link"
                title = title_el.text.strip() if title_el else "Cupom ML"

                if not link.startswith("http"):
                    link = base + link

                coupons.append({
                    "id": f"{prefix}_{code}",
                    "title": title[:80],
                    "code": code,
                    "discount": disc,
                    "link": link,
                    "valid": valid,
                })
        except Exception as e:
            print(f"ml {prefix} err: {e}")

    return coupons
