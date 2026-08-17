#!/usr/bin/env python3
"""
phone_monitor.py - Мониторинг состояния телефона для Termux
Запускается как отдельный поток и обновляет статус телефона
"""

import os
import json
import time
import logging
import subprocess
import threading
from datetime import datetime
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PhoneMonitor")

class PhoneState:
    """Класс для хранения состояния телефона"""
    
    _instance = None
    _state = {
        "battery": {},
        "storage": {},
        "network": {},
        "device": {},
        "cpu": {},
        "memory": {},
        "timestamp": None
    }
    _lock = threading.Lock()
    _running = True
    _update_interval = 30  # секунд
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def update(cls):
        """Обновить состояние телефона"""
        with cls._lock:
            try:
                is_termux = os.path.exists("/data/data/com.termux")
                
                # Базовое состояние
                cls._state["timestamp"] = datetime.now().isoformat()
                cls._state["is_termux"] = is_termux
                cls._state["python_version"] = __import__('platform').python_version()
                
                if not is_termux:
                    logger.warning("❌ Не Termux окружение")
                    return
                
                # 1. БАТАРЕЯ
                try:
                    result = subprocess.check_output(
                        ["termux-battery-status"], 
                        text=True, 
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    )
                    battery = json.loads(result)
                    cls._state["battery"] = {
                        "percent": battery.get("percentage", 0),
                        "status": battery.get("status", "UNKNOWN"),
                        "temperature": battery.get("temperature", 0),
                        "current": battery.get("current", 0),
                        "health": battery.get("health", "UNKNOWN"),
                        "is_charging": battery.get("status") == "CHARGING"
                    }
                except Exception as e:
                    logger.error(f"Ошибка батареи: {e}")
                    cls._state["battery"] = {"error": str(e)}
                
                # 2. ХРАНИЛИЩЕ
                try:
                    result = subprocess.check_output(
                        ["df", "-h", "/data"], 
                        text=True,
                        timeout=5
                    )
                    lines = result.split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 5:
                            cls._state["storage"] = {
                                "total": parts[1],
                                "used": parts[2],
                                "free": parts[3],
                                "percent": parts[4] if len(parts) > 4 else "0%"
                            }
                except Exception as e:
                    logger.error(f"Ошибка хранилища: {e}")
                    cls._state["storage"] = {"error": str(e)}
                
                # 3. СЕТЬ
                try:
                    # WiFi статус
                    wifi_result = subprocess.check_output(
                        ["termux-wifi-connectioninfo"],
                        text=True,
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    )
                    wifi = json.loads(wifi_result)
                    cls._state["network"] = {
                        "wifi": wifi.get("ssid", "unknown"),
                        "ip": wifi.get("ip", "unknown"),
                        "signal": wifi.get("rssi", 0)
                    }
                except:
                    # Если termux-wifi-connectioninfo не работает
                    cls._state["network"] = {"error": "WiFi info not available"}
                
                # 4. ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ
                try:
                    model = subprocess.check_output(
                        ["getprop", "ro.product.model"],
                        text=True,
                        timeout=3
                    ).strip()
                    
                    android_version = subprocess.check_output(
                        ["getprop", "ro.build.version.release"],
                        text=True,
                        timeout=3
                    ).strip()
                    
                    cls._state["device"] = {
                        "model": model,
                        "android_version": android_version,
                        "termux": os.path.exists("/data/data/com.termux")
                    }
                except Exception as e:
                    cls._state["device"] = {"error": str(e)}
                
                # 5. CPU (через /proc/stat)
                try:
                    with open("/proc/stat", "r") as f:
                        cpu_line = f.readline().split()
                    if len(cpu_line) > 4:
                        user = int(cpu_line[1])
                        nice = int(cpu_line[2])
                        system = int(cpu_line[3])
                        idle = int(cpu_line[4])
                        total = user + nice + system + idle
                        cls._state["cpu"] = {
                            "user": user,
                            "system": system,
                            "idle": idle,
                            "total": total,
                            "usage": round((user + system) / total * 100, 1) if total > 0 else 0
                        }
                except Exception as e:
                    cls._state["cpu"] = {"error": str(e)}
                
                # 6. ПАМЯТЬ (через /proc/meminfo)
                try:
                    meminfo = {}
                    with open("/proc/meminfo", "r") as f:
                        for line in f:
                            parts = line.split()
                            if len(parts) >= 2:
                                key = parts[0].rstrip(':')
                                value = int(parts[1])
                                meminfo[key] = value
                    
                    total_mem = meminfo.get("MemTotal", 0)
                    free_mem = meminfo.get("MemFree", 0)
                    available_mem = meminfo.get("MemAvailable", total_mem - free_mem)
                    
                    cls._state["memory"] = {
                        "total_mb": total_mem // 1024,
                        "free_mb": free_mem // 1024,
                        "available_mb": available_mem // 1024,
                        "used_mb": (total_mem - available_mem) // 1024,
                        "percent": round((1 - available_mem / total_mem) * 100, 1) if total_mem > 0 else 0
                    }
                except Exception as e:
                    cls._state["memory"] = {"error": str(e)}
                
                # 7. ВРЕМЯ РАБОТЫ
                try:
                    uptime = subprocess.check_output(
                        ["cat", "/proc/uptime"],
                        text=True,
                        timeout=3
                    ).split()[0]
                    uptime_seconds = int(float(uptime))
                    hours = uptime_seconds // 3600
                    minutes = (uptime_seconds % 3600) // 60
                    cls._state["uptime"] = {
                        "seconds": uptime_seconds,
                        "formatted": f"{hours}h {minutes}m"
                    }
                except:
                    pass
                
                logger.debug("✅ Состояние телефона обновлено")
                
            except Exception as e:
                logger.error(f"❌ Ошибка обновления состояния: {e}")
    
    @classmethod
    def get_state(cls) -> Dict[str, Any]:
        """Получить текущее состояние"""
        with cls._lock:
            return cls._state.copy()
    
    @classmethod
    def get_battery(cls) -> Dict[str, Any]:
        """Получить состояние батареи"""
        with cls._lock:
            return cls._state.get("battery", {})
    
    @classmethod
    def get_storage(cls) -> Dict[str, Any]:
        """Получить состояние хранилища"""
        with cls._lock:
            return cls._state.get("storage", {})
    
    @classmethod
    def get_network(cls) -> Dict[str, Any]:
        """Получить состояние сети"""
        with cls._lock:
            return cls._state.get("network", {})
    
    @classmethod
    def get_formatted_status(cls) -> str:
        """Получить форматированное состояние для вывода"""
        state = cls.get_state()
        battery = state.get("battery", {})
        storage = state.get("storage", {})
        network = state.get("network", {})
        device = state.get("device", {})
        cpu = state.get("cpu", {})
        memory = state.get("memory", {})
        uptime = state.get("uptime", {})
        
        status = "📱 **СТАТУС ТЕЛЕФОНА**\n"
        status += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Устройство
        if device and "model" in device:
            status += f"**Устройство:** {device.get('model', 'N/A')}\n"
        if device and "android_version" in device:
            status += f"**Android:** {device.get('android_version', 'N/A')}\n"
        status += f"**Python:** {state.get('python_version', 'N/A')}\n\n"
        
        # Батарея
        if battery and "percent" in battery:
            percent = battery.get("percent", 0)
            is_charging = battery.get("is_charging", False)
            status += f"**🔋 Батарея:** {percent}%"
            status += " ⚡" if is_charging else ""
            if "temperature" in battery:
                status += f" ({battery['temperature']}°C)"
            status += "\n"
            status += f"**Статус:** {battery.get('status', 'UNKNOWN')}\n\n"
        
        # Память
        if storage:
            status += f"**💾 Хранилище:**\n"
            status += f"  Всего: {storage.get('total', 'N/A')}\n"
            status += f"  Использовано: {storage.get('used', 'N/A')}\n"
            status += f"  Свободно: {storage.get('free', 'N/A')}\n"
            status += f"  Заполнено: {storage.get('percent', '0%')}\n\n"
        
        # ОЗУ
        if memory and "total_mb" in memory:
            status += f"**🧠 ОЗУ:**\n"
            status += f"  Всего: {memory.get('total_mb', 0)} MB\n"
            status += f"  Использовано: {memory.get('used_mb', 0)} MB\n"
            status += f"  Свободно: {memory.get('available_mb', 0)} MB\n"
            status += f"  Заполнено: {memory.get('percent', 0)}%\n\n"
        
        # CPU
        if cpu and "usage" in cpu:
            status += f"**⚡ CPU:** {cpu.get('usage', 0)}%\n\n"
        
        # Сеть
        if network and "wifi" in network:
            status += f"**📶 Wi-Fi:** {network.get('wifi', 'N/A')}\n"
            if "ip" in network:
                status += f"**IP:** {network.get('ip', 'N/A')}\n"
            if "signal" in network:
                status += f"**Сигнал:** {network.get('signal', 0)} dBm\n\n"
        
        # Время работы
        if uptime and "formatted" in uptime:
            status += f"**🕐 Время работы:** {uptime.get('formatted', 'N/A')}\n\n"
        
        status += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        status += f"🔄 Обновлено: {state.get('timestamp', 'N/A')}"
        
        return status


def monitor_loop():
    """Фоновый цикл обновления состояния"""
    logger.info("🔄 Запуск монитора состояния телефона...")
    
    if not os.path.exists("/data/data/com.termux"):
        logger.warning("⚠️ Это не Termux! Некоторые функции могут не работать.")
    
    PhoneState.update()  # Первое обновление
    
    while PhoneState._running:
        try:
            time.sleep(PhoneState._update_interval)
            PhoneState.update()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"❌ Ошибка в цикле монитора: {e}")
    
    logger.info("🛑 Монитор состояния остановлен")


def start_monitor():
    """Запустить монитор в отдельном потоке"""
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    logger.info("✅ Монитор состояния запущен в фоне")
    return thread


def stop_monitor():
    """Остановить монитор"""
    PhoneState._running = False
    logger.info("🛑 Остановка монитора...")


if __name__ == "__main__":
    # Тестовый запуск
    print("📱 Тестирование монитора состояния телефона")
    print("=" * 50)
    PhoneState.update()
    print(PhoneState.get_formatted_status())
    print("=" * 50)
    print("✅ Тест завершен")
