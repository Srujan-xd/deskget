    """
    widgets/base.py — Abstract base class for all display widgets.

    Every widget must implement render() which returns a 240x240 RGB
    Pillow Image ready to push to DisplayPanel.show().
    """

    import logging
    from abc import ABC, abstractmethod
    from PIL import Image, ImageDraw, ImageFont

    log = logging.getLogger(__name__)

    # Lazy font cache — avoid re-opening font files on every frame
    _font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


    def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
        key = (path, size)
        if key not in _font_cache:
            try:
                _font_cache[key] = ImageFont.truetype(path, size)
            except OSError:
                log.warning("Font not found: %s — falling back to default", path)
                _font_cache[key] = ImageFont.load_default()
        return _font_cache[key]


    def make_canvas(width: int = 240, height: int = 240, bg=(10, 10, 20)) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        """Create a blank canvas and its drawing context."""
        img  = Image.new("RGB", (width, height), bg)
        draw = ImageDraw.Draw(img)
        return img, draw


    def draw_header(draw: ImageDraw.ImageDraw, title: str, font_path: str, theme: dict, width: int = 240) -> None:
        """Draw a coloured title bar at the top of a panel."""
        bar_h = 32
        draw.rectangle([(0, 0), (width, bar_h)], fill=theme["primary"])
        font = load_font(font_path, 16)
        bbox = draw.textbbox((0, 0), title, font=font)
        tw   = bbox[2] - bbox[0]
        draw.text(((width - tw) // 2, 7), title, font=font, fill=(0, 0, 0))


    def draw_divider(draw: ImageDraw.ImageDraw, y: int, theme: dict, width: int = 240) -> None:
        draw.line([(10, y), (width - 10, y)], fill=theme["dim"], width=1)


    class BaseWidget(ABC):
        """
        Base class for all widgets.

        Subclasses override:
        - render()      — return a PIL Image (240x240 RGB)
        - update()      — fetch / refresh data (called on a schedule)
        - REFRESH_S     — class attribute: how often update() is called
        """

        REFRESH_S: int = 60   # default: refresh data every 60 s
        NAME: str      = "widget"

        def __init__(self, width: int = 240, height: int = 240) -> None:
            self.width  = width
            self.height = height
            self._error: str | None = None

        # ------------------------------------------------------------------
        # Must implement
        # ------------------------------------------------------------------

        @abstractmethod
        def render(self) -> Image.Image:
            """Return the current frame as a 240x240 RGB PIL Image."""
            ...

        def update(self) -> None:
            """Fetch / refresh external data. Called every REFRESH_S seconds."""
            pass

        # ------------------------------------------------------------------
        # Helpers available to subclasses
        # ------------------------------------------------------------------

        def _blank(self, bg=None) -> tuple[Image.Image, ImageDraw.ImageDraw]:
            from config import THEME
            return make_canvas(self.width, self.height, bg or THEME["bg"])

        def _font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
            from config import FONT_BOLD, FONT_REGULAR
            return load_font(FONT_BOLD if bold else FONT_REGULAR, size)

        def _theme(self) -> dict:
            from config import THEME
            return THEME

        def _error_frame(self, message: str) -> Image.Image:
            img, draw = self._blank()
            t = self._theme()
            draw_header(draw, self.NAME.upper(), self._font_path(bold=True), t)
            draw.text((10, 50), "Error:", font=self._font(14, bold=True), fill=t["danger"])
            # Word-wrap crude split
            words = message.split()
            line, y = "", 72
            for w in words:
                test = (line + " " + w).strip()
                if draw.textbbox((0, 0), test, font=self._font(12))[2] > 220:
                    draw.text((10, y), line, font=self._font(12), fill=t["secondary"])
                    y   += 18
                    line = w
                else:
                    line = test
            if line:
                draw.text((10, y), line, font=self._font(12), fill=t["secondary"])
            return img

        def _font_path(self, bold: bool = False) -> str:
            from config import FONT_BOLD, FONT_REGULAR
            return FONT_BOLD if bold else FONT_REGULAR
