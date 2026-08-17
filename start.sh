# start.sh
#!/data/data/com.termux/files/usr/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    AgethaAi Bot — FPE Edition         ║${NC}"
echo -e "${BLUE}║    Запуск в Termux                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

# Проверка .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo -e "${YELLOW}Создайте его: cp .env.example .env${NC}"
    exit 1
fi

# Загрузка переменных
source .env

# Проверка токена
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ TELEGRAM_BOT_TOKEN не задан!${NC}"
    exit 1
fi

# Проверка Termux
if [ -d "/data/data/com.termux" ]; then
    echo -e "${GREEN}📱 Режим Termux активирован${NC}"
fi

# Создание папки для логов
mkdir -p logs

# Запуск
echo -e "${GREEN}🚀 Запуск бота...${NC}"
echo -e "${YELLOW}📝 Логи: logs/bot.log${NC}"

# Запуск с логированием
python telegram_bot.py 2>&1 | tee -a logs/bot.log
