import re

STORE_EMOJI = {
    "iFood": "🍔",
    "Amazon": "📦",
    "Shopee": "🛒",
    "Mercado Livre": "🛍️",
    "Pelando": "🔥",
    "Cuponomia": "🎫",
}

# Códigos inválidos que devem ser rejeitados
INVALID_CODES = {"SEM CODIGO", "SEM CÓDIGO", "AUTOMATICO", "AUTOMÁTICO", "VER LINK", "VER NO LINK", "CLIQUE AQUI", ""}


def extract_discount_from_text(text: str) -> str:
    """
    Extrai desconto de textos livres como:
    - "de R$ 199 por R$ 159" 
    - "era 299 agora 199"
    - "20% OFF"
    - "50% de desconto"
    """
    if not text:
        return ""
    
    text = text.upper()
    
    # Padrão: X% OFF / X% de desconto
    match = re.search(r'(\d+)\s*%\s*(OFF|DESCONTO|DE\s+DESCONTO)', text)
    if match:
        return f"{match.group(1)}% OFF"
    
    # Padrão: de R$ X por R$ Y
    match = re.search(r'DE\s*R?\$?\s*(\d+[.,]?\d*)\s*(?:POR|PARA|AGORA)\s*R?\$?\s*(\d+[.,]?\d*)', text)
    if match:
        old_price = float(match.group(1).replace(',', '.'))
        new_price = float(match.group(2).replace(',', '.'))
        if old_price > new_price:
            discount_pct = int(((old_price - new_price) / old_price) * 100)
            return f"{discount_pct}% OFF (R$ {old_price:.0f} → R$ {new_price:.0f})"
    
    # Padrão: era X agora Y
    match = re.search(r'(?:ERA|DE)\s*R?\$?\s*(\d+[.,]?\d*)\s*(?:AGORA|POR)\s*R?\$?\s*(\d+[.,]?\d*)', text)
    if match:
        old_price = float(match.group(1).replace(',', '.'))
        new_price = float(match.group(2).replace(',', '.'))
        if old_price > new_price:
            discount_pct = int(((old_price - new_price) / old_price) * 100)
            return f"{discount_pct}% OFF (R$ {old_price:.0f} → R$ {new_price:.0f})"
    
    return ""


def is_valid_coupon_code(code: str) -> bool:
    """Verifica se o código do cupom é válido"""
    if not code or not isinstance(code, str):
        return False
    
    code_upper = code.strip().upper()
    
    # Rejeita códigos inválidos
    if code_upper in INVALID_CODES:
        return False
    
    # Código válido deve ter pelo menos 3 caracteres alfanuméricos
    alphanumeric = re.sub(r'[^A-Z0-9]', '', code_upper)
    if len(alphanumeric) < 3:
        return False
    
    return True


def format_coupon_message(store: str, coupon: dict) -> str:
    emoji = STORE_EMOJI.get(store, "🏷️")
    title = coupon.get("title", "Cupom").strip()
    code = coupon.get("code", "").strip()
    discount = coupon.get("discount", "").strip()
    link = coupon.get("link", "").strip()
    valid = coupon.get("valid", "Sem data").strip()

    # Tenta extrair desconto do título se não houver discount explícito
    if not discount and title:
        discount = extract_discount_from_text(title)
    
    # Tenta extrair desconto da própria string discount
    if discount:
        extracted = extract_discount_from_text(discount)
        if extracted:
            discount = extracted

    lines = [f"{emoji} <b>{store}</b> — Novo Cupom!", "", f"📌 <b>{title}</b>"]

    if discount:
        lines.append(f"💸 <b>Desconto:</b> {discount}")

    lines.append(f"🎟️ <b>Código:</b> <code>{code}</code>")
    lines.append(f"📅 <b>Validade:</b> {valid}")

    if link:
        lines += ["", f'🔗 <a href="{link}">Usar cupom agora</a>']

    lines += ["", "━━━━━━━━━━━━━━━━━━━━", "🤖 CupomBot"]
    return "\n".join(lines)
