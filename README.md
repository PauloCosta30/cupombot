# 🎫 CupomBot - Bot de Alertas de Cupons

Bot automatizado que monitora cupons de desconto e envia alertas no Telegram.

## 🏪 Lojas Monitoradas
- 🍔 iFood
- 📦 Amazon BR
- 🛒 Shopee
- 🛍️ Mercado Livre
- 🔥 Pelando (agregador)
- 🎫 Cuponomia (agregador)

## ⚙️ Configuração

### 1. Criar o Bot no Telegram
1. Fale com @BotFather no Telegram
2. Envie /newbot
3. Escolha nome e username
4. Salve o TOKEN gerado

### 2. Pegar seu Chat ID
1. Fale com @userinfobot
2. Ele retorna seu Chat ID
3. Para grupos: adicione o bot e use o ID do grupo (começa com -100)

### 3. Deploy no Render
1. Crie conta em render.com
2. New → Background Worker
3. Conecte seu GitHub
4. Selecione este repositório
5. Adicione as variáveis de ambiente:
   - TELEGRAM_TOKEN
   - TELEGRAM_CHAT_ID

### 4. Deploy!
O bot inicia automaticamente e verifica cupons a cada 5 minutos.

## 🚀 Uso Local
\`\`\`bash
pip install -r requirements.txt
export TELEGRAM_TOKEN="seu_token"
export TELEGRAM_CHAT_ID="seu_chat_id"
python main.py
\`\`\`

## 📝 Licença
MIT
