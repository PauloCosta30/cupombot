import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

def scrape_amazon() -> list[dict]:
    coupons = []

    try:
        r = requests.get("https://www.cuponomia.com.br/cupons/amazon", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.select("article, [class*='coupon']")[:10]:
            code_el = card.select_one("[class*='code'], code")
            disc_el = card.select_one("[class*='discount'], [class*='off']")
            link_el = card.select_one("a[href]")
            valid_el = card.select_one("[class*='expir'], [class*='valid']")
            title_el = card.select_one("h2, h3, [class*='title']")

            code = code_el.text.strip() if code_el else "SEM CODIGO"
            disc = disc_el.text.strip() if disc_el else ""
            link = link_el["href"] if link_el else "https://amazon.com.br"
            valid = valid_el.text.strip() if valid_el else "Sem data"
            title = title_el.text.strip() if title_el else "Cupom Amazon"

            if not link.startswith("http"):
                link = "https://www.cuponomia.com.br" + link

            coupons.append({
                "id": f"amazon_cuponomia_{code}",
                "title": title[:80],
                "code": code,
                "discount": disc,
                "link": link,
                "valid": valid,
            })
    except Exception as e:
        print(f"amazon cuponomia err: {e}")

    try:
        r = requests.get("https://www.amazon.com.br/gp/goldbox", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        for deal in soup.select("[data-asin]")[:5]:
            asin = deal.get("data-asin", "")
            title_el = deal.select_one("[class*='title'], h2")
            disc_el = deal.select_one("[class*='percentage'], [class*='badge']")

            title = title_el.text.strip() if title_el else "Oferta Amazon"
            disc = disc_el.text.strip() if disc_el else ""
            link = f"https://www.amazon.com.br/dp/{asin}" if asin else "https://amazon.com.br/deals"

            if asin:
                coupons.append({
                    "id": f"amazon_deal_{asin}",
                    "title": title[:80],
                    "code": "AUTOMATICO",
                    "discount": disc,
                    "link": link,
                    "valid": "Oferta relampago",
                })
    except Exception as e:
        print(f"amazon goldbox err: {e}")

    return coupons
