# ============================================================
# Desktop Gadget — Configuration
# Raspberry Pi Zero 2 W + 2x ST7789 240x240 TFT (SPI)
# ============================================================

# ------------------------------------------------------------------
# SPI / GPIO Pin Assignments (BCM numbering)
# ------------------------------------------------------------------

# Shared SPI0 bus pins (hardware-fixed, do not change)
DISP_SPI_PORT  = 0   # SPI0
DISP_DC        = 9   # Data/Command — shared between both displays
DISP_SPI_SPEED = 40_000_000  # 40 MHz (reduced from 80 MHz for dual-display stability)

# Display 1 — LEFT screen (CE0)
DISP1_CS  = 8   # SPI CE0
DISP1_RST = 27  # Reset (optional but recommended)
DISP1_BL  = 19  # Backlight PWM

# Display 2 — RIGHT screen (CE1)
DISP2_CS  = 7   # SPI CE1
DISP2_RST = 17  # Reset
DISP2_BL  = 18  # Backlight PWM

# Display geometry
DISP_WIDTH    = 240
DISP_HEIGHT   = 240
DISP_ROTATION = 90   # 0 / 90 / 180 / 270

# ------------------------------------------------------------------
# Widget Schedules
# Each display cycles through its list; set WIDGET_INTERVAL in seconds.
# Valid names: "clock", "weather", "finance", "todo", "sysmon", "spotify"
# ------------------------------------------------------------------

DISP1_SCHEDULE     = ["clock", "weather", "finance", "todo"]
DISP2_SCHEDULE     = ["sysmon", "spotify", "weather"]
WIDGET_INTERVAL    = 15   # seconds each widget stays on screen
WIDGET_TRANSITION  = True # fade/wipe between widgets (set False if too slow on Pi Zero)

# ------------------------------------------------------------------
# OpenWeatherMap (free tier — https://openweathermap.org/api)
# ------------------------------------------------------------------

OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
OPENWEATHER_CITY    = "New York"
OPENWEATHER_UNITS   = "metric"   # "metric" = °C | "imperial" = °F
WEATHER_REFRESH_S   = 600        # re-fetch every 10 minutes

# ------------------------------------------------------------------
# Spotify (https://developer.spotify.com/dashboard)
# ------------------------------------------------------------------

SPOTIFY_CLIENT_ID     = "395314f590444aa697c74cf09eb3b2e3"
SPOTIFY_CLIENT_SECRET = "09c45cc7baaa4d428faf8590bd149389"
SPOTIFY_REDIRECT_URI  = "http://localhost:8888/callback"
SPOTIFY_SCOPE         = "user-read-playback-state user-read-currently-playing"
SPOTIFY_REFRESH_S     = 5   # poll interval in seconds

# ------------------------------------------------------------------
# Finance (symbols are yfinance-compatible)
# ------------------------------------------------------------------

FINANCE_SYMBOLS   = ["AAPL", "MSFT", "BTC-USD", "ETH-USD"]
FINANCE_REFRESH_S = 60    # re-fetch every minute (respect free rate limits)

# ------------------------------------------------------------------
# To-Do list
# One task per line in this plain-text file.
# The gadget reads it at startup and whenever the file changes.
# ------------------------------------------------------------------

TODO_FILE = "todos.txt"

# ------------------------------------------------------------------
# UI Theme  (R, G, B  tuples)
# ------------------------------------------------------------------

THEME = {
    "bg":       (10,  10,  20),
    "primary":  (0,   200, 255),
    "secondary":(180, 180, 200),
    "accent":   (255, 180, 0),
    "danger":   (255, 60,  60),
    "success":  (60,  220, 100),
    "text":     (240, 240, 255),
    "dim":      (90,  90,  110),
    "card":     (25,  25,  45),
}

# ------------------------------------------------------------------
# Fonts — DejaVu is pre-installed on Raspberry Pi OS
# ------------------------------------------------------------------

FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

LOG_LEVEL = "INFO"   # DEBUG | INFO | WARNING | ERROR
