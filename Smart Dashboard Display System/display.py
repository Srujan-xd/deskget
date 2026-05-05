"""
display.py — ST7789 display wrapper

Wraps the Pimoroni st7789 library so the rest of the code never
touches the hardware directly.  Each DisplayPanel instance owns one
physical screen.
"""

import logging
from PIL import Image

try:
    import st7789
    _HW_AVAILABLE = True
except ImportError:
    _HW_AVAILABLE = False
    logging.warning("st7789 library not found — running in HEADLESS mode (images saved to disk)")

log = logging.getLogger(__name__)


class DisplayPanel:
    """
    Thin wrapper around a single ST7789 screen.

    Parameters
    ----------
    name        : human-readable label used in log messages ("left", "right")
    cs          : SPI chip-select GPIO pin (BCM)
    dc          : Data/Command GPIO pin (BCM) — shared between panels
    rst         : Reset GPIO pin (BCM), optional
    backlight   : Backlight GPIO pin (BCM), optional
    port        : SPI port number (default 0)
    spi_speed   : SPI clock in Hz (default 40 MHz)
    width       : panel width in pixels (default 240)
    height      : panel height in pixels (default 240)
    rotation    : 0 / 90 / 180 / 270 (default 90)
    """

    def __init__(
        self,
        name: str,
        cs: int,
        dc: int,
        rst: int | None = None,
        backlight: int | None = None,
        port: int = 0,
        spi_speed: int = 40_000_000,
        width: int = 240,
        height: int = 240,
        rotation: int = 90,
    ) -> None:
        self.name   = name
        self.width  = width
        self.height = height
        self._hw    = None

        if _HW_AVAILABLE:
            log.info("Initialising display '%s' (cs=%d, dc=%d)", name, cs, dc)
            self._hw = st7789.ST7789(
                height       = height,
                width        = width,
                port         = port,
                cs           = cs,
                dc           = dc,
                rst          = rst,
                backlight    = backlight,
                spi_speed_hz = spi_speed,
                rotation     = rotation,
            )
            self._hw.begin()
            log.info("Display '%s' ready (%dx%d)", name, width, height)
        else:
            log.warning("Display '%s' running in HEADLESS mode", name)

        # Clear to black on startup
        self.fill((0, 0, 0))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show(self, image: Image.Image) -> None:
        """Push a Pillow RGBA/RGB image to the screen."""
        # Ensure correct size and mode
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.LANCZOS)
        if image.mode != "RGB":
            image = image.convert("RGB")

        if self._hw is not None:
            self._hw.display(image)
        else:
            # Headless: save PNG for desktop debugging
            path = f"/tmp/gadget_{self.name}.png"
            image.save(path)
            log.debug("Headless: saved frame to %s", path)

    def fill(self, color: tuple[int, int, int]) -> None:
        """Fill the screen with a solid colour."""
        img = Image.new("RGB", (self.width, self.height), color)
        self.show(img)

    def blank(self) -> None:
        """Turn the screen off (black)."""
        self.fill((0, 0, 0))

    # ------------------------------------------------------------------
    # Context manager support  (with DisplayPanel(...) as d: ...)
    # ------------------------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.blank()


def create_displays_from_config() -> tuple["DisplayPanel", "DisplayPanel"]:
    """
    Convenience factory that reads src/config.py and returns (disp1, disp2).
    Import and call this from main.py.
    """
    from config import (
        DISP1_CS, DISP1_RST, DISP1_BL,
        DISP2_CS, DISP2_RST, DISP2_BL,
        DISP_DC, DISP_SPI_PORT, DISP_SPI_SPEED,
        DISP_WIDTH, DISP_HEIGHT, DISP_ROTATION,
    )

    d1 = DisplayPanel(
        name      = "left",
        cs        = DISP1_CS,
        dc        = DISP_DC,
        rst       = DISP1_RST,
        backlight = DISP1_BL,
        port      = DISP_SPI_PORT,
        spi_speed = DISP_SPI_SPEED,
        width     = DISP_WIDTH,
        height    = DISP_HEIGHT,
        rotation  = DISP_ROTATION,
    )

    d2 = DisplayPanel(
        name      = "right",
        cs        = DISP2_CS,
        dc        = DISP_DC,
        rst       = DISP2_RST,
        backlight = DISP2_BL,
        port      = DISP_SPI_PORT,
        spi_speed = DISP_SPI_SPEED,
        width     = DISP_WIDTH,
        height    = DISP_HEIGHT,
        rotation  = DISP_ROTATION,
    )

    return d1, d2
