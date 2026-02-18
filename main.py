import asyncio
import logging
import os
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.constants import ParseMode

from scrapers.pelando import scrape_pelando
from scrapers.cuponomia import scrape_cuponomia
from scrapers.ifood import scrape_ifood
from scrapers.amazon import scrape_amazon
from scrapers.shopee import scrape_shopee
from scrapers.mercadolivre import scrape_mercadolivre
from utils.storage import load_seen, save_seen
from utils.formatter import format_coupon_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SCRAPERS = {
    "iFood": scrape_ifood,
    "Amazon": scrape_amazon,
    "Shopee": scrape_shopee,
    "Mercado Livre": scrape_mercadolivre,
    "Pelando": scrape_pelando,
    "Cuponomia": scrape_cuponomia,
}

async def check_coupons(bot: Bot):
    logger.info("Verificando cupons...")
    seen = load_seen()
    new_seen = set(seen)

    for store, scraper in SCRAPERS.items():
        try:
            coupons = scraper()
            logger.info(f"  {store}: {len(coupons)} cupom(ns)")
            for coupon in coupons:
                uid = coupon.get("id") or f"{store}_{coupon.get('code','')}_{coupon.get('discount','')}"
                if uid not in seen:
                    new_seen.add(uid)
                    msg = format_coupon_message(store, coupon)
                    try:
                        await bot.send_message(
                            chat_id=TELEGRAM_CHAT_ID,
                            text=msg,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=False,
                        )
                        logger.info(f"    Enviado: {uid}")
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.error(f"    Erro ao enviar: {e}")
        except Exception as e:
            logger.error(f"  Erro no scraper {store}: {e}")

    save_seen(new_seen)
    logger.info("Verificacao concluida.")

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=(
                "🤖 <b>CupomBot iniciado!</b>\n\n"
                "Monitorando cupons de:\n"
                "🍔 iFood | 📦 Amazon | 🛒 Shopee | 🛍️ Mercado Livre\n"
                "🔥 Pelando | 🎫 Cuponomia\n\n"
                "⏱️ Verificação a cada <b>5 minutos</b>.\n"
                f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error(f"Erro na mensagem inicial: {e}")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_coupons, "interval", minutes=5, args=[bot], next_run_time=datetime.now())
    scheduler.start()

    logger.info("Bot rodando — verificando a cada 5 minutos.")
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
