    @classmethod
    def get_formatted_state(cls, state: Dict = None) -> str:
        if state is None:
            state = cls.get_state()
        if not state:
            return "⚠️ Нет данных о состоянии системы."

        lines = ["📱 Состояние системы", ""]

        # Батарея
        if "battery_percent" in state:
            bp = state["battery_percent"]
            bs = state.get("battery_status", "N/A")
            bt = state.get("battery_temperature")
            if bp is not None:
                lines.append(f"🔋 Батарея: {bp}% ({bs})")
            if bt is not None:
                lines.append(f"🌡 Температура: {bt}°C")

        # CPU
        if "cpu_load_1m" in state:
            lines.append(f"🖥 CPU Load: {state['cpu_load_1m']}")

        # RAM
        if "ram_percent" in state:
            ru = state.get("ram_used_mb", "?")
            rt = state.get("ram_total_mb", "?")
            rp = state["ram_percent"]
            lines.append(f"💾 RAM: {ru} / {rt} MB ({rp}%)")

        # Диск
        if "disk_percent" in state:
            du = state.get("disk_used", "?")
            dt = state.get("disk_total", "?")
            dp = state["disk_percent"]
            lines.append(f"💿 Диск: {du} / {dt} ({dp})")

        # Устройство
        if "device" in state:
            lines.append(f"📲 Устройство: {state['device']}")
        if "android_version" in state:
            lines.append(f"🤖 Android: {state['android_version']}")
        if "network_type" in state:
            lines.append(f"📶 Сеть: {state['network_type']}")

        # Система
        if "uptime" in state:
            lines.append(f"⏱ Аптайм: {state['uptime']}")
        if "kernel" in state:
            lines.append(f"⚙️ Ядро: {state['kernel']}")

        # Прочее
        if "note" in state:
            lines.append(f"\n{state['note']}")

        lines.append(f"\n🕐 Обновлено: {state.get('last_update', 'N/A')}")

        return "\n".join(lines)
