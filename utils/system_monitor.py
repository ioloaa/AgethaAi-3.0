"""
System Monitor — мониторинг состояния системы/телефона
Работает на Linux, Windows, macOS и Android/Termux
"""
import subprocess
import platform
import json
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TermuxCollector:
    """Сбор данных через Termux API (Android)"""

    @staticmethod
    def is_available() -> bool:
        try:
            subprocess.run(["which", "termux-battery-status"],
                           capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @classmethod
    def collect(cls) -> Dict:
        stats = {
            "platform": "Android/Termux",
            "python_version": platform.python_version(),
            "last_update": datetime.now().isoformat(),  # ← ИСПРАВЛЕНО: было "timestamp"
        }

        # Батарея
        try:
            result = subprocess.run(
                ["termux-battery-status"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                battery = json.loads(result.stdout)
                stats["battery_percent"] = battery.get("percentage")
                stats["battery_status"] = battery.get("status")
                stats["battery_temperature"] = battery.get("temperature")
                stats["battery_health"] = battery.get("health")
        except Exception as e:
            logger.debug(f"termux-battery-status error: {e}")

        # Инфо о системе
        try:
            result = subprocess.run(
                ["termux-info"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info = json.loads(result.stdout)
                stats["device"] = info.get("device", "Unknown")
                stats["android_version"] = info.get("android_version")
                stats["api_level"] = info.get("api_level")
                stats["termux_version"] = info.get("app_version")
        except Exception as e:
            logger.debug(f"termux-info error: {e}")

        # Инфо об устройстве
        try:
            result = subprocess.run(
                ["termux-telephony-deviceinfo"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                tele = json.loads(result.stdout)
                stats["device_id"] = tele.get("device_id", "N/A")
                stats["network_type"] = tele.get("network_type", "N/A")
                stats["phone_type"] = tele.get("phone_type", "N/A")
                stats["sim_country"] = tele.get("sim_country_iso", "N/A")
        except Exception as e:
            logger.debug(f"termux-telephony-deviceinfo error: {e}")

        # CPU load
        try:
            with open("/proc/loadavg", "r") as f:
                load = f.read().strip().split()
                stats["cpu_load_1m"] = load[0] if load else "N/A"
        except Exception as e:
            logger.debug(f"cpu load error: {e}")

        # RAM (из /proc/meminfo)
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = f.read()
                total = None
                available = None
                for line in meminfo.split("\n"):
                    if line.startswith("MemTotal:"):
                        total = int(line.split()[1]) // 1024  # MB
                    elif line.startswith("MemAvailable:"):
                        available = int(line.split()[1]) // 1024
                if total and available:
                    used = total - available
                    stats["ram_total_mb"] = total
                    stats["ram_used_mb"] = used
                    stats["ram_available_mb"] = available
                    stats["ram_percent"] = round((used / total) * 100, 1)
        except Exception as e:
            logger.debug(f"ram error: {e}")

        # Диск
        try:
            result = subprocess.run(
                ["df", "-h", "/data"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        stats["disk_total"] = parts[1]
                        stats["disk_used"] = parts[2]
                        stats["disk_available"] = parts[3]
                        stats["disk_percent"] = parts[4]
        except Exception as e:
            logger.debug(f"disk error: {e}")

        # Аптайм
        try:
            result = subprocess.run(
                ["uptime", "-p"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                stats["uptime"] = result.stdout.strip()
        except Exception:
            try:
                result = subprocess.run(
                    ["uptime"],
                    capture_output=True, text=True, timeout=3
                )
                if result.returncode == 0:
                    stats["uptime"] = result.stdout.strip()
            except Exception as e:
                logger.debug(f"uptime error: {e}")

        # Ядро
        try:
            result = subprocess.run(
                ["uname", "-r"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                stats["kernel"] = result.stdout.strip()
        except Exception as e:
            logger.debug(f"kernel error: {e}")

        return stats


class SystemMonitor:
    _state: Dict = {}
    _last_update: str = ""

    @classmethod
    def update_state(cls, state: Dict):
        cls._state = state
        cls._last_update = datetime.now().isoformat()
        cls._state["last_update"] = cls._last_update

    @classmethod
    def get_state(cls) -> Optional[Dict]:
        if not cls._state:
            # Пробуем Termux
            if TermuxCollector.is_available():
                return TermuxCollector.collect()
            # Fallback на базовую инфу
            try:
                return {
                    "platform": platform.system(),
                    "python_version": platform.python_version(),
                    "last_update": datetime.now().isoformat(),
                    "note": "Монитор не запущен. Запусти bot_monitor.py для полной статистики."
                }
            except Exception:
                return None
        return dict(cls._state)

    @classmethod
    def get_formatted_state(cls) -> str:
        state = cls.get_state()
        if not state:
            return "⚠️ Нет данных о состоянии системы."
        lines = ["📱 *Состояние системы*", ""]
        for key, value in state.items():
            if key == "last_update":
                lines.append(f"🕐 *Последнее обновление:* `{value}`")
            elif key == "battery_percent":
                lines.append(f"🔋 *Батарея:* `{value}%`")
            elif key == "battery_status":
                lines.append(f"⚡ *Статус:* `{value}`")
            elif key == "battery_temperature":
                lines.append(f"🌡 *Температура:* `{value}°C`")
            elif key == "cpu_load_1m":
                lines.append(f"🖥 *CPU Load:* `{value}`")
            elif key == "ram_percent":
                lines.append(f"💾 *RAM:* `{state.get('ram_used_mb', '?')} / {state.get('ram_total_mb', '?')} MB ({value}%)`")
            elif key == "disk_percent":
                lines.append(f"💿 *Диск:* `{state.get('disk_used', '?')} / {state.get('disk_total', '?')} ({value})`")
            elif key == "uptime":
                lines.append(f"⏱ *Аптайм:* `{value}`")
            elif key == "device":
                lines.append(f"📲 *Устройство:* `{value}`")
            elif key == "android_version":
                lines.append(f"🤖 *Android:* `{value}`")
            elif key == "network_type":
                lines.append(f"📶 *Сеть:* `{value}`")
            elif isinstance(value, (int, float)):
                lines.append(f"• {key}: `{value:.2f}`" if isinstance(value, float) else f"• {key}: `{value}`")
            else:
                lines.append(f"• {key}: `{value}`")
        return "\n".join(lines)
