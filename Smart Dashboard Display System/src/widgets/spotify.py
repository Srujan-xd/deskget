"""
widgets/spotify.py — Currently-playing track panel via Spotify Web API.
Requires: spotipy
"""

import logging
import time
import io

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    _SPOTIPY_OK = True
except ImportError:
    _SPOTIPY_OK = False

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

from PIL import Image

from widgets.base import BaseWidget, draw_header, draw_divider

log = logging.getLogger(__name__)


class SpotifyWidget(BaseWidget):
    NAME      = "spotify"
    REFRESH_S = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sp   = None
        self._track: dict = {}
        self._art_cache: tuple[str, Image.Image] | None = None   # (url, image)

    def _init_client(self) -> bool:
        if self._sp is not None:
            return True
        if not _SPOTIPY_OK:
            self._error = "Install spotipy: pip install spotipy"
            return False
        from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPE
        if SPOTIFY_CLIENT_ID == "YOUR_SPOTIFY_CLIENT_ID":
            self._error = "Add Spotify credentials to config.py"
            return False
        try:
            self._sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id     = SPOTIFY_CLIENT_ID,
                client_secret = SPOTIFY_CLIENT_SECRET,
                redirect_uri  = SPOTIFY_REDIRECT_URI,
                scope         = SPOTIFY_SCOPE,
                open_browser  = False,
            ))
        except Exception as exc:
            self._error = str(exc)
            return False
        return True

    def update(self) -> None:
        if not self._init_client():
            return
        try:
            pb = self._sp.current_playback()
            if pb and pb.get("item"):
                item   = pb["item"]
                images = item["album"]["images"]
                art_url = images[0]["url"] if images else None
                self._track = {
                    "title":    item["name"],
                    "artist":   ", ".join(a["name"] for a in item["artists"]),
                    "album":    item["album"]["name"],
                    "progress": pb["progress_ms"],
                    "duration": item["duration_ms"],
                    "playing":  pb["is_playing"],
                    "art_url":  art_url,
                }
                self._fetch_art(art_url)
                self._error = None
            else:
                self._track = {}
        except Exception as exc:
            self._error = str(exc)
            log.error("Spotify update failed: %s", exc)

    def _fetch_art(self, url: str | None) -> None:
        if not url or not _REQUESTS_OK:
            return
        if self._art_cache and self._art_cache[0] == url:
            return   # already have it
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            art = Image.open(io.BytesIO(r.content)).convert("RGB")
            art = art.resize((90, 90), Image.LANCZOS)
            self._art_cache = (url, art)
        except Exception as exc:
            log.warning("Album art fetch failed: %s", exc)
            self._art_cache = None

    def render(self):
        t = self._theme()
        img, draw = self._blank()
        draw_header(draw, "SPOTIFY", self._font_path(bold=True), t)

        if self._error:
            return self._error_frame(self._error)

        if not self._track:
            draw.text((10, 50), "Nothing playing", font=self._font(16), fill=t["dim"])
            draw.text((10, 74), "Start something on Spotify", font=self._font(11), fill=t["dim"])
            return img

        tr = self._track

        # Album art (top-left area below header)
        art_x, art_y = 10, 38
        if self._art_cache:
            img.paste(self._art_cache[1], (art_x, art_y))
        else:
            draw.rectangle([(art_x, art_y), (art_x + 90, art_y + 90)], fill=t["card"], outline=t["dim"])
            draw.text((art_x + 28, art_y + 35), "ART", font=self._font(14, bold=True), fill=t["dim"])

        # Track info (right of art)
        tx = 108
        draw.text((tx, 38), tr["title"],  font=self._font(13, bold=True), fill=t["primary"])

        # Wrap artist name if long
        artist = tr["artist"]
        if len(artist) > 22:
            artist = artist[:20] + "…"
        draw.text((tx, 56), artist, font=self._font(12), fill=t["secondary"])

        album = tr["album"]
        if len(album) > 20:
            album = album[:18] + "…"
        draw.text((tx, 74), album,  font=self._font(11), fill=t["dim"])

        # Play/pause indicator
        status = "  PLAYING" if tr["playing"] else "  PAUSED"
        draw.text((tx, 94), status, font=self._font(11, bold=True),
                  fill=t["success"] if tr["playing"] else t["dim"])

        draw_divider(draw, 135, t)

        # Progress bar
        dur  = max(tr["duration"], 1)
        prog = tr["progress"]
        pct  = prog / dur
        bx, by, bw, bh = 10, 142, 220, 10
        draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=t["card"], outline=t["dim"])
        draw.rectangle([(bx, by), (bx + int(bw * pct), by + bh)], fill=t["primary"])

        def ms_to_mmss(ms: int) -> str:
            s = ms // 1000
            return f"{s // 60}:{s % 60:02d}"

        draw.text((10,  158), ms_to_mmss(prog), font=self._font(11), fill=t["dim"])
        dur_str = ms_to_mmss(dur)
        dur_w   = draw.textbbox((0, 0), dur_str, font=self._font(11))[2]
        draw.text((230 - dur_w, 158), dur_str, font=self._font(11), fill=t["dim"])

        return img
