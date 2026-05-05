"""
widgets/sysmon.py — CPU, RAM, Disk, and CPU temperature monitor.
Requires: psutil
"""

import logging
import psutil

from widgets.base import BaseWidget, draw_header, draw_divider

log = logging.getLogger(__name__)


class SysmonWidget(BaseWidget):
    NAME      = "sysmon"
    REFRESH_S = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data: dict = {}

    def update(self) -> None:
        try:
            # CPU: non-blocking interval=None, so we use a 0.2 s sample
            self._data = {
                "cpu_pct":  psutil.cpu_percent(interval=0.2),
                "cpu_temp": self._cpu_temp(),
                "ram":      psutil.virtual_memory(),
                "disk":     psutil.disk_usage("/"),
                "net":      psutil.net_io_counters(),
            }
        except Exception as exc:
            log.exception("sysmon update failed: %s", exc)

    # ------------------------------------------------------------------
    def render(self):
        t = self._theme()
        img, draw = self._blank()

        draw_header(draw, "SYSTEM", self._font_path(bold=True), t)

        if not self._data:
            draw.text((10, 50), "Loading...", font=self._font(16), fill=t["dim"])
            return img

        y = 40
        gap = 48

        def bar_row(label: str, pct: float, value_str: str, bar_color):
            nonlocal y
            font_label = self._font(13, bold=True)
            font_val   = self._font(12)
            draw.text((10, y), label, font=font_label, fill=t["text"])
            draw.text((200 - draw.textbbox((0,0), value_str, font=font_val)[2], y), value_str, font=font_val, fill=t["secondary"])
            # Background bar
            bx, by, bw, bh = 10, y + 18, 220, 12
            draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=t["card"], outline=t["dim"])
            fill_w = int(bw * min(pct, 100) / 100)
            if fill_w > 0:
                draw.rectangle([(bx, by), (bx + fill_w, by + bh)], fill=bar_color)
            y += gap

        cpu = self._data.get("cpu_pct", 0)
        ram = self._data.get("ram")
        disk = self._data.get("disk")
        temp = self._data.get("cpu_temp")

        # CPU
        cpu_color = t["success"] if cpu < 60 else t["accent"] if cpu < 85 else t["danger"]
        bar_row("CPU", cpu, f"{cpu:.0f}%", cpu_color)

        # RAM
        if ram:
            ram_gb = ram.used / 1e9
            bar_row("RAM", ram.percent, f"{ram_gb:.1f} GB / {ram.total/1e9:.1f} GB", t["primary"])

        # Disk
        if disk:
            disk_gb = disk.used / 1e9
            bar_row("Disk", disk.percent, f"{disk_gb:.0f} GB / {disk.total/1e9:.0f} GB", t["accent"])

        # CPU Temperature
        if temp is not None:
            temp_color = t["success"] if temp < 55 else t["accent"] if temp < 70 else t["danger"]
            draw.text((10, y), "Temp", font=self._font(13, bold=True), fill=t["text"])
            draw.text((10, y + 16), f"{temp:.1f} °C", font=self._font(22, bold=True), fill=temp_color)

        return img

    # ------------------------------------------------------------------
    @staticmethod
    def _cpu_temp() -> float | None:
        try:
            temps = psutil.sensors_temperatures()
            for key in ("cpu_thermal", "coretemp", "cpu-thermal"):
                if key in temps and temps[key]:
                    return temps[key][0].current
        except AttributeError:
            pass
        # Fallback: read Pi thermal zone
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                return int(f.read().strip()) / 1000.0
        except OSError:
            return None
