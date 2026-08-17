"""
bot_monitor.py - Мониторинг системы (обертка для phone_monitor.py)
Запускается как отдельный процесс для совместимости
"""

import time
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BotMonitor")

def main():
    """Запуск монитора системы"""
    
    # Проверка Termux
    is_termux = os.path.exists("/data/data/com.termux")
    
    if is_termux:
        logger.info("📱 Запуск монитора в Termux режиме")
        try:
            from phone_monitor import start_monitor
            start_monitor()
            logger.info("✅ Монитор телефона запущен")
            
            # Держим поток живым
            while True:
                time.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Монитор остановлен пользователем")
        except ImportError:
            logger.warning("⚠️ phone_monitor.py не найден")
    else:
        logger.info("🖥️ Запуск монитора в ПК режиме")
        # Здесь можно добавить мониторинг для ПК

if __name__ == "__main__":
    main()
