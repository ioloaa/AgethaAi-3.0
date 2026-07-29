"""
Мониторинг системы (телефон/сервер).
Запускается отдельно или как поток.
"""
import time
import platform
import logging
from datetime import datetime

from utils.system_monitor import SystemMonitor, TermuxCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Monitor")

PSUTIL_AVAILABLE = False
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    pass


def collect_stats():
    # Если Termux — используем его API
    if TermuxCollector.is_available():
        return TermuxCollector.collect()

    # Иначе psutil (Linux/Windows/macOS)
    stats = {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "timestamp": datetime.now().isoformat(),
    }

    if PSUTIL_AVAILABLE:
        stats.update({
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_percent": psutil.virtual_memory().percent,
            "ram_used_mb": psutil.virtual_memory().used // 1024 // 1024,
            "disk_percent": psutil.disk_usage('/').percent,
        })

        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                stats["battery_percent"] = battery.percent
                stats["battery_plugged"] = battery.power_plugged

        net_io = psutil.net_io_counters()
        stats["net_sent_mb"] = net_io.bytes_sent // 1024 // 1024
        stats["net_recv_mb"] = net_io.bytes_recv // 1024 // 1024

    return stats


def main():
    logger.info("Монитор системы запущен")
    while True:
        try:
            stats = collect_stats()
            SystemMonitor.update_state(stats)
            logger.debug(f"Обновлено состояние: {stats}")
        except Exception as e:
            logger.error(f"Ошибка мониторинга: {e}")
        time.sleep(30)


if __name__ == "__main__":
    main()
