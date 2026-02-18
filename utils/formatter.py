STORE_EMOJI = {
    "iFood": "🍔",
    "Amazon": "📦",
    "Shopee": "🛒",
    "Mercado Livre": "🛍️",
    "Pelando": "🔥",
    "Cuponomia": "🎫",
}

def format_coupon_message(store: str, coupon: dict) -> str:
    emoji = STORE_EMOJI.get(store, "🏷️")
    title = coupon.get("title", "Cupom")
    code = coupon.get("code", "SEM CODIGO")
    discount = coupon.get("discount", "")
    link = coupon.get("link", "")
    valid = coupon.get("valid", "Sem data")

    lines = [f"{emoji} <b>{store}</b> — Novo Cupom!", "", f"📌 <b>{title}</b>"]

    if discount:
        lines.append(f"💸 <b>Desconto:</b> {discount}")

    if code.upper() not in ("SEM CODIGO", "AUTOMATICO", "VER LINK"):
        lines.append(f"🎟️ <b>Código:</b> <code>{code}</code>")
    else:
        lines.append(f"🎟️ <b>Cupom:</b> {code}")

    lines.append(f"📅 <b>Validade:</b> {valid}")

    if link:
        lines += ["", f'🔗 <a href="{link}">Usar cupom agora</a>']

    lines += ["", "━━━━━━━━━━━━━━━━━━━━", "🤖 CupomBot"]
    return "\n".join(lines)
