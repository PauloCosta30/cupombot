import asyncio
import logging
import os
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.constants import ParseMode
from aiohttp import web

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

TELEGRAM_TOKEN   = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
PORT = int(os.environ.get("PORT", 8080))  # Render fornece a porta automaticamente

SCRAPERS = {
    "iFood":         scrape_ifood,
    "Amazon":        scrape_amazon,
    "Shopee":        scrape_shopee,
    "Mercado Livre": scrape_mercadolivre,
    "Pelando":       scrape_pelando,
    "Cuponomia":     scrape_cuponomia,
}

# Contador de requisições
stats = {"requests": 0, "last_check": None, "coupons_sent": 0}


async def check_coupons(bot: Bot):
    logger.info("Verificando cupons...")
    stats["last_check"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    seen = load_seen()
    new_seen = set(seen)
    count = 0

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
                        count += 1
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.error(f"    Erro ao enviar: {e}")
        except Exception as e:
            logger.error(f"  Erro no scraper {store}: {e}")

    save_seen(new_seen)
    stats["coupons_sent"] += count
    logger.info(f"Verificacao concluida. {count} novos cupons enviados.")


# Endpoints HTTP para health check
async def health_check(request):
    stats["requests"] += 1
    return web.json_response({
        "status": "online",
        "bot": "CupomBot",
        "uptime_requests": stats["requests"],
        "last_check": stats["last_check"] or "Aguardando primeira verificacao",
        "total_coupons_sent": stats["coupons_sent"],
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })


async def ping(request):
    stats["requests"] += 1
    return web.Response(text="pong")


async def start_http_server():
    """Inicia servidor HTTP para health checks"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/ping', ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"🌐 Servidor HTTP rodando na porta {PORT}")


async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Inicia servidor HTTP
    await start_http_server()
    
    # Mensagem de inicialização
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=(
                "🤖 <b>CupomBot iniciado!</b>\n\n"
                "Monitorando cupons de:\n"
                "🍔 iFood | 📦 Amazon | 🛒 Shopee | 🛍️ Mercado Livre\n"
                "🔥 Pelando | 🎫 Cuponomia\n\n"
                "⏱️ Verificação a cada <b>5 minutos</b>.\n"
                f"🌐 Health check: Porta {PORT}\n"
                f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error(f"Erro na mensagem inicial: {e}")

    # Scheduler para verificação de cupons
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_coupons, "interval", minutes=5,
        args=[bot], next_run_time=datetime.now()
    )
    scheduler.start()

    logger.info("🚀 Bot rodando — verificando a cada 5 minutos.")
    logger.info(f"📊 Acesse http://localhost:{PORT}/ para ver status")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
