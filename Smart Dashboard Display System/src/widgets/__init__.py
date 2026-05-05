"""
widgets/__init__.py — Widget registry.
Maps string names (used in config schedules) to widget classes.
"""

from widgets.clock   import ClockWidget
from widgets.sysmon  import SysmonWidget
from widgets.weather import WeatherWidget
from widgets.spotify import SpotifyWidget
from widgets.finance import FinanceWidget
from widgets.todo    import TodoWidget

REGISTRY: dict[str, type] = {
    "clock":   ClockWidget,
    "sysmon":  SysmonWidget,
    "weather": WeatherWidget,
    "spotify": SpotifyWidget,
    "finance": FinanceWidget,
    "todo":    TodoWidget,
}


def build_widget(name: str, width: int = 240, height: int = 240):
    """Instantiate a widget by its registry name. Raises KeyError if unknown."""
    cls = REGISTRY[name]
    return cls(width=width, height=height)
