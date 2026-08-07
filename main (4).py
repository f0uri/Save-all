#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Save Pro - Universal Media Downloader
Copyright 2026 Youssef Mansouri
Premium iOS-style, multi-platform downloader (Instagram / TikTok / Facebook / X / Pinterest)
Paste a public link and download - no login, no account required.
"""
import os, time, sqlite3, threading
import yt_dlp

# -- Pure-Python Arabic shaping (no external packages) --
_AR_FORMS = {
    "\u0621": (0xFE80, 0xFE80, 0xFE80, 0xFE80),
    "\u0622": (0xFE81, 0xFE81, 0xFE81, 0xFE82),
    "\u0623": (0xFE83, 0xFE83, 0xFE83, 0xFE84),
    "\u0624": (0xFE85, 0xFE85, 0xFE85, 0xFE86),
    "\u0625": (0xFE87, 0xFE87, 0xFE87, 0xFE88),
    "\u0626": (0xFE89, 0xFE8B, 0xFE8C, 0xFE8A),
    "\u0627": (0xFE8D, 0xFE8D, 0xFE8D, 0xFE8E),
    "\u0628": (0xFE8F, 0xFE91, 0xFE92, 0xFE90),
    "\u0629": (0xFE93, 0xFE93, 0xFE93, 0xFE94),
    "\u062A": (0xFE95, 0xFE97, 0xFE98, 0xFE96),
    "\u062B": (0xFE99, 0xFE9B, 0xFE9C, 0xFE9A),
    "\u062C": (0xFE9D, 0xFE9F, 0xFEA0, 0xFE9E),
    "\u062D": (0xFEA1, 0xFEA3, 0xFEA4, 0xFEA2),
    "\u062E": (0xFEA5, 0xFEA7, 0xFEA8, 0xFEA6),
    "\u062F": (0xFEA9, 0xFEA9, 0xFEA9, 0xFEAA),
    "\u0630": (0xFEAB, 0xFEAB, 0xFEAB, 0xFEAC),
    "\u0631": (0xFEAD, 0xFEAD, 0xFEAD, 0xFEAE),
    "\u0632": (0xFEAF, 0xFEAF, 0xFEAF, 0xFEB0),
    "\u0633": (0xFEB1, 0xFEB3, 0xFEB4, 0xFEB2),
    "\u0634": (0xFEB5, 0xFEB7, 0xFEB8, 0xFEB6),
    "\u0635": (0xFEB9, 0xFEBB, 0xFEBC, 0xFEBA),
    "\u0636": (0xFEBD, 0xFEBF, 0xFEC0, 0xFEBE),
    "\u0637": (0xFEC1, 0xFEC3, 0xFEC4, 0xFEC2),
    "\u0638": (0xFEC5, 0xFEC7, 0xFEC8, 0xFEC6),
    "\u0639": (0xFEC9, 0xFECB, 0xFECC, 0xFECA),
    "\u063A": (0xFECD, 0xFECF, 0xFED0, 0xFECE),
    "\u0641": (0xFED1, 0xFED3, 0xFED4, 0xFED2),
    "\u0642": (0xFED5, 0xFED7, 0xFED8, 0xFED6),
    "\u0643": (0xFED9, 0xFEDB, 0xFEDC, 0xFEDA),
    "\u0644": (0xFEDD, 0xFEDF, 0xFEE0, 0xFEDE),
    "\u0645": (0xFEE1, 0xFEE3, 0xFEE4, 0xFEE2),
    "\u0646": (0xFEE5, 0xFEE7, 0xFEE8, 0xFEE6),
    "\u0647": (0xFEE9, 0xFEEB, 0xFEEC, 0xFEEA),
    "\u0648": (0xFEED, 0xFEED, 0xFEED, 0xFEEE),
    "\u0649": (0xFEEF, 0xFEEF, 0xFEEF, 0xFEF0),
    "\u064A": (0xFEF1, 0xFEF3, 0xFEF4, 0xFEF2),
}
_AR_NON_CONNECTORS = set("\u0621\u0622\u0623\u0624\u0625\u0627\u0629\u062F\u0630\u0631\u0632\u0648\u0649")
_LAM = "\u0644"
_LAM_ALEF_LIGATURES = {
    "\u0627": (0xFEFB, 0xFEFC),
    "\u0622": (0xFEF5, 0xFEF6),
    "\u0623": (0xFEF7, 0xFEF8),
    "\u0625": (0xFEF9, 0xFEFA),
}

def _shape_arabic(text):
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == _LAM and i + 1 < n and text[i + 1] in _LAM_ALEF_LIGATURES:
            iso, fin = _LAM_ALEF_LIGATURES[text[i + 1]]
            prev = text[i - 1] if i > 0 else ""
            connects_from_prev = prev in _AR_FORMS and prev not in _AR_NON_CONNECTORS
            out.append(chr(fin if connects_from_prev else iso))
            i += 2
            continue
        if ch not in _AR_FORMS:
            out.append(ch)
            i += 1
            continue
        prev = text[i - 1] if i > 0 else ""
        nxt = text[i + 1] if i + 1 < n else ""
        has_prev = prev in _AR_FORMS and prev not in _AR_NON_CONNECTORS
        has_next = nxt in _AR_FORMS or (nxt == _LAM and False)
        self_connects = ch not in _AR_NON_CONNECTORS
        iso, init, med, fin = _AR_FORMS[ch]
        if has_prev and self_connects and has_next:
            out.append(chr(med))
        elif has_prev and not (self_connects and has_next):
            out.append(chr(fin))
        elif (not has_prev) and self_connects and has_next:
            out.append(chr(init))
        else:
            out.append(chr(iso))
        i += 1
    return "".join(reversed(out))

def _strip_unsupported_glyphs(text):
    if not text:
        return text
    out = []
    for ch in text:
        cp = ord(ch)
        if (
            0x1F000 <= cp <= 0x1FFFF
            or 0x2600 <= cp <= 0x27BF
            or 0x2190 <= cp <= 0x21FF
            or 0x2B00 <= cp <= 0x2BFF
            or cp in (0xFE0E, 0xFE0F)
            or cp == 0x200D
        ):
            continue
        out.append(ch)
    return "".join(out)

def ar(text):
    """Shape + visually reorder Arabic text only. English/numbers stay as-is."""
    if not text:
        return text
    text = str(text)
    has_arabic = any(
        '\u0600' <= ch <= '\u06FF' or '\u0750' <= ch <= '\u077F'
        or '\u08A0' <= ch <= '\u08FF' or '\uFB50' <= ch <= '\uFDFF'
        or '\uFE70' <= ch <= '\uFEFF'
        for ch in text
    )
    if not has_arabic:
        return text
    try:
        return _shape_arabic(_strip_unsupported_glyphs(text))
    except Exception:
        return text

from kivy.app import App
from kivy.config import Config
Config.set("kivy", "keyboard_mode", "system")
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.image import AsyncImage, Image as KvImage
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Mesh, Rectangle, StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.graphics.texture import Texture
from kivy.graphics.context_instructions import PushMatrix, PopMatrix, Scale, Translate
from kivy.metrics import dp
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.effects.dampedscroll import DampedScrollEffect
from kivy.uix.video import Video
from kivy.uix.modalview import ModalView
from kivy.uix.slider import Slider
from kivy.uix.button import Button

Window.softinput_mode = "pan"

_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoNaskhArabic-Regular.ttf")
if os.path.exists(_FONT_PATH):
    LabelBase.register(DEFAULT_FONT, _FONT_PATH)

# ---------------------------------------------------------------------------
# Premium 2026 Dark Palette (Glassmorphism & Neons)
# ---------------------------------------------------------------------------
BG_DARK = (0.02, 0.02, 0.03, 1.0)
GLASS_BG = (0.09, 0.09, 0.12, 0.65)
GLASS_BORDER = (1.0, 1.0, 1.0, 0.05)
GLASS_BORDER_ACTIVE = (1.0, 1.0, 1.0, 0.15)
NEON_PINK = (1.0, 0.15, 0.50, 1)
NEON_PURPLE = (0.55, 0.20, 1.0, 1)
NEON_CYAN = (0.0, 0.85, 1.0, 1)
NEON_BLUE = (0.15, 0.45, 1.0, 1)
NEON_INDIGO = (0.35, 0.30, 1.0, 1)
NEON_RED = (1.0, 0.25, 0.35, 1)
NEON_GREEN = (0.15, 0.90, 0.50, 1)
NEON_YELLOW = (1.0, 0.80, 0.15, 1)
NEON_ORANGE = (1.0, 0.50, 0.10, 1)
TEXT_MAIN = (0.96, 0.96, 0.98, 1)
TEXT_MUTED = (0.60, 0.62, 0.68, 1)
TEXT_FAINT = (0.40, 0.42, 0.48, 1)
Window.clearcolor = BG_DARK

# ---------------------------------------------------------------------------
# Gradient texture helper (Smooth horizontal rendering)
# ---------------------------------------------------------------------------
_GRADIENT_CACHE = {}

def _get_gradient_texture(c1, c2, steps=64):
    key = (tuple(round(v, 3) for v in c1), tuple(round(v, 3) for v in c2), steps)
    tex = _GRADIENT_CACHE.get(key)
    if tex is not None:
        return tex
    buf = bytearray()
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        r = c1[0] + (c2[0] - c1[0]) * t
        g = c1[1] + (c2[1] - c1[1]) * t
        b = c1[2] + (c2[2] - c1[2]) * t
        a1 = c1[3] if len(c1) > 3 else 1.0
        a2 = c2[3] if len(c2) > 3 else 1.0
        a = a1 + (a2 - a1) * t
        buf += bytes([
            int(max(0, min(1, r)) * 255), int(max(0, min(1, g)) * 255),
            int(max(0, min(1, b)) * 255), int(max(0, min(1, a)) * 255),
        ])
    tex = Texture.create(size=(steps, 1), colorfmt="rgba")
    tex.blit_buffer(bytes(buf), colorfmt="rgba", bufferfmt="ubyte")
    tex.wrap = "clamp_to_edge"
    _GRADIENT_CACHE[key] = tex
    return tex

def _rr(pos, size, radius):
    return (pos[0], pos[1], size[0], size[1], radius)

# ---------------------------------------------------------------------------
# Local storage: recent-downloads history (no accounts, no login)
# ---------------------------------------------------------------------------
def _get_db_path():
    try:
        from kivy.app import App as _App
        app = _App.get_running_app()
        if app is not None:
            return os.path.join(app.user_data_dir, "savepro.db")
    except Exception:
        pass
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "savepro.db")

DB_PATH = None

def init_db():
    global DB_PATH
    if DB_PATH is None:
        DB_PATH = _get_db_path()
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS history ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, platform TEXT, url TEXT, "
        "filename TEXT, created_at REAL)"
    )
    conn.commit()
    conn.close()

def save_history(platform, url, filename):
    try:
        if DB_PATH is None:
            init_db()
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO history (platform, url, filename, created_at) VALUES (?,?,?,?)",
            (platform, url, filename, time.time()),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_history(limit=12):
    try:
        if DB_PATH is None:
            init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT platform, url, filename, created_at FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

UAS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
]

def get_ua():
    import random
    return random.choice(UAS)

# ---------------------------------------------------------------------------
# Platform definitions (real icons via CDN, no local files needed)
# ---------------------------------------------------------------------------
# CDN URLs for platform icons (PNG)
ICON_URLS = {
    "instagram": "https://img.icons8.com/fluency/48/instagram-new.png",
    "tiktok": "https://img.icons8.com/fluency/48/tiktok.png",
    "facebook": "https://img.icons8.com/fluency/48/facebook.png",
    "x": "https://img.icons8.com/fluency/48/twitterx.png",
    "pinterest": "https://img.icons8.com/fluency/48/pinterest.png",
}

PLATFORMS = [
    {"id": "instagram", "label": ar("انستقرام"),
     "color": NEON_PINK, "hint": ar("الصق رابط ريلز أو منشور من انستقرام"), "letter": "I"},
    {"id": "tiktok", "label": ar("تيك توك"),
     "color": NEON_CYAN, "hint": ar("الصق رابط فيديو من تيك توك"), "letter": "T"},
    {"id": "facebook", "label": ar("فيسبوك"),
     "color": NEON_BLUE, "hint": ar("الصق رابط فيديو أو ريلز من فيسبوك"), "letter": "F"},
    {"id": "x", "label": "X",
     "color": TEXT_MAIN, "hint": ar("الصق رابط فيديو من منصة X"), "letter": "X"},
    {"id": "pinterest", "label": ar("بنترست"),
     "color": NEON_RED, "hint": ar("الصق رابط بن من بنترست"), "letter": "P"},
]
PLATFORM_BY_ID = {p["id"]: p for p in PLATFORMS}

# ---------------------------------------------------------------------------
# Media download (yt_dlp handles all supported platforms from a public URL)
# ---------------------------------------------------------------------------
class _SilentLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def download_media(url, download_dir):
    os.makedirs(download_dir, exist_ok=True)
    base_opts = {
        "outtmpl": os.path.join(download_dir, "%(title).80s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": _SilentLogger(),
        "user_agent": get_ua(),
        "retries": 2,
        "socket_timeout": 20,
    }
    last_err = ar("فشل التحميل")
    for fmt in ("best[ext=mp4]/best", "best", "worst"):
        opts = dict(base_opts)
        opts["format"] = fmt
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    continue
                files = [
                    os.path.join(download_dir, f)
                    for f in sorted(os.listdir(download_dir))
                    if os.path.isfile(os.path.join(download_dir, f)) and not f.endswith((".json", ".txt", ".part"))
                ]
                if files:
                    return files, None
        except Exception as e:
            last_err = str(e)[:300]
            continue
    return None, last_err

def fetch_preview(url):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": _SilentLogger(),
        "user_agent": get_ua(),
        "socket_timeout": 20,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None, ar("تعذّرت المعاينة")
            play_url = info.get("url")
            if not play_url:
                fmts = info.get("formats") or []
                playable = [
                    f for f in fmts
                    if f.get("url") and f.get("vcodec") not in (None, "none") and f.get("acodec") not in (None, "none")
                ]
                if playable:
                    playable.sort(key=lambda f: f.get("height") or 0)
                    play_url = playable[-1]["url"]
                elif fmts:
                    play_url = fmts[-1].get("url")
            filesize = info.get("filesize") or info.get("filesize_approx")
            resolution = info.get("resolution") or (f"{info.get('width')}x{info.get('height')}" if info.get('width') else None)
            return {
                "title": info.get("title") or ar("بدون عنوان"),
                "thumbnail": info.get("thumbnail") or "",
                "duration": info.get("duration"),
                "play_url": play_url,
                "resolution": resolution,
                "filesize": filesize,
                "extractor": info.get("extractor_key", "")
            }, None
    except Exception as e:
        return None, str(e)[:250]

def download_audio_only(url, download_dir):
    os.makedirs(download_dir, exist_ok=True)
    base_opts = {
        "outtmpl": os.path.join(download_dir, "%(title).80s.%(ext)s"),
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": _SilentLogger(),
        "user_agent": get_ua(),
        "retries": 2,
        "socket_timeout": 20,
    }
    with_mp3 = dict(base_opts)
    with_mp3["postprocessors"] = [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }]
    last_err = ar("فشل تحميل الصوت")
    for opts in (with_mp3, base_opts):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    continue
                files = [
                    os.path.join(download_dir, f)
                    for f in sorted(os.listdir(download_dir))
                    if os.path.isfile(os.path.join(download_dir, f)) and not f.endswith((".json", ".txt", ".part"))
                ]
                if files:
                    return files, None
        except Exception as e:
            last_err = str(e)[:300]
            continue
    return None, last_err

# ---------------------------------------------------------------------------
# UI Components & Behaviors (Premium 2026 Redesign)
# ---------------------------------------------------------------------------
class ElasticBehavior(ButtonBehavior):
    """Elastic touch interaction (scales down smoothly on press)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.scale_instr = Scale(1, 1, 1)
        with self.canvas.after:
            PopMatrix()
        self.bind(pos=self.update_scale_origin, size=self.update_scale_origin)

    def update_scale_origin(self, *args):
        self.scale_instr.origin = self.center

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            Animation.cancel_all(self.scale_instr)
            Animation(x=0.96, y=0.96, z=1, duration=0.1, t='out_quad').start(self.scale_instr)
            return True
        return False

    def on_touch_up(self, touch):
        res = super().on_touch_up(touch)
        Animation.cancel_all(self.scale_instr)
        Animation(x=1, y=1, z=1, duration=0.4, t='out_elastic').start(self.scale_instr)
        return res

class GlassCard(BoxLayout):
    """Modern Glassmorphism card."""
    def __init__(self, radius=dp(24), **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        with self.canvas.before:
            self.bg_color = Color(*GLASS_BG)
            self.bg_rect = RoundedRectangle(radius=[radius])
            self.border_color = Color(*GLASS_BORDER)
            self.border_line = Line(rounded_rectangle=(0, 0, 0, 0, radius), width=dp(1))
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = _rr(self.pos, self.size, self.radius)

class PremiumInput(TextInput):
    """2026 Style Text Input with focus animations."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(56)
        self.font_size = "15sp"
        self.padding = [dp(18), dp(18), dp(18), dp(16)]
        self.background_normal = ""
        self.background_active = ""
        self.background_color = (0, 0, 0, 0)
        self.foreground_color = TEXT_MAIN
        self.hint_text_color = TEXT_FAINT
        self.cursor_color = NEON_PURPLE
        with self.canvas.before:
            Color(0.04, 0.04, 0.06, 0.8)
            self._bg = RoundedRectangle(radius=[dp(18)])
            self._glow_color = Color(*GLASS_BORDER)
            self._border = Line(rounded_rectangle=(0, 0, 0, 0, dp(18)), width=dp(1.2))
        self.bind(pos=self._upd, size=self._upd, focus=self._on_focus)

    def _upd(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = _rr(self.pos, self.size, dp(18))

    def _on_focus(self, inst, val):
        if val:
            Animation(rgba=(*NEON_PURPLE[:3], 0.6), duration=0.2, t='out_cubic').start(self._glow_color)
        else:
            Animation(rgba=GLASS_BORDER, duration=0.2, t='out_cubic').start(self._glow_color)

class PremiumButton(ElasticBehavior, BoxLayout):
    """Gradient or solid beautiful button with perfect typography."""
    def __init__(self, text="", gradient=None, bg_color=None, text_color=TEXT_MAIN, icon_widget=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(56)
        with self.canvas.before:
            if gradient:
                Color(1, 1, 1, 1)
                self._fill = RoundedRectangle(radius=[dp(18)], texture=_get_gradient_texture(gradient[0], gradient[1]))
            else:
                Color(*(bg_color or (0.15, 0.15, 0.18, 1)))
                self._fill = RoundedRectangle(radius=[dp(18)])
        self.bind(pos=self._upd, size=self._upd)
        self.add_widget(Widget())
        if icon_widget:
            self.add_widget(icon_widget)
        self.label = Label(
            text=text, font_size="15sp", bold=True,
            color=text_color, size_hint=(None, None)
        )
        self.label.bind(texture_size=lambda inst, val: setattr(self.label, "size", val))
        self.add_widget(self.label)
        self.add_widget(Widget())

    def _upd(self, *args):
        self._fill.pos = self.pos
        self._fill.size = self.size

class PlatformCard(ElasticBehavior, GlassCard):
    """Premium 2026 App Store style platform card with real icon from CDN."""
    def __init__(self, platform, on_select=None, **kwargs):
        super().__init__(radius=dp(22), **kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (dp(110), dp(130))
        self.padding = [dp(12), dp(16), dp(12), dp(12)]
        self.spacing = dp(8)
        self.platform = platform
        self.on_select = on_select
        # Icon container with circular background
        icon_wrap = AnchorLayout(size_hint_y=None, height=dp(56))
        self.icon_bg = Widget(size_hint=(None, None), size=(dp(56), dp(56)))
        with self.icon_bg.canvas:
            self._glow_c = Color(*platform["color"][:3], 0.0)
            self._glow = Ellipse(pos=self.icon_bg.pos, size=self.icon_bg.size)
            self._icon_c = Color(0.12, 0.12, 0.15, 1)
            self._icon_bg_el = Ellipse(pos=self.icon_bg.pos, size=self.icon_bg.size)
        self.icon_bg.bind(pos=self._upd_icon, size=self._upd_icon)
        icon_wrap.add_widget(self.icon_bg)
        # Real icon from CDN
        icon_url = ICON_URLS.get(platform["id"])
        self.icon_img = AsyncImage(
            source=icon_url,
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        # Fallback label (if image fails to load)
        self.fallback_label = Label(
            text=platform.get("letter", platform["id"][0].upper()),
            font_size="20sp", bold=True, color=TEXT_MAIN,
            size_hint=(None, None), size=(dp(32), dp(32)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.fallback_label.opacity = 0  # hidden by default
        self.icon_img.bind(on_error=lambda inst, val: setattr(self.fallback_label, 'opacity', 1))
        icon_wrap.add_widget(self.icon_img)
        icon_wrap.add_widget(self.fallback_label)
        self.add_widget(icon_wrap)
        self._label = Label(
            text=platform["label"], font_size="13sp", color=TEXT_MUTED, bold=True,
            valign="middle", halign="center"
        )
        self.add_widget(self._label)

    def _upd_icon(self, *args):
        cx, cy = self.icon_bg.center_x, self.icon_bg.center_y
        r = self.icon_bg.width / 2
        self._icon_bg_el.pos = (cx - r, cy - r)
        self._icon_bg_el.size = (r * 2, r * 2)
        glow_r = r + dp(12)
        self._glow.pos = (cx - glow_r, cy - glow_r)
        self._glow.size = (glow_r * 2, glow_r * 2)

    def set_selected(self, selected):
        if selected:
            Animation(rgba=(*self.platform["color"][:3], 0.15), duration=0.2).start(self._glow_c)
            Animation(rgba=self.platform["color"], duration=0.2).start(self._icon_c)
            Animation(color=TEXT_MAIN, duration=0.2).start(self._label)
            Animation(rgba=GLASS_BORDER_ACTIVE, duration=0.2).start(self.border_color)
            Animation(rgba=(0.12, 0.12, 0.16, 0.9), duration=0.2).start(self.bg_color)
        else:
            Animation(rgba=(*self.platform["color"][:3], 0.0), duration=0.2).start(self._glow_c)
            Animation(rgba=(0.12, 0.12, 0.15, 1), duration=0.2).start(self._icon_c)
            Animation(color=TEXT_MUTED, duration=0.2).start(self._label)
            Animation(rgba=GLASS_BORDER, duration=0.2).start(self.border_color)
            Animation(rgba=GLASS_BG, duration=0.2).start(self.bg_color)

    def on_release(self):
        if self.on_select:
            self.on_select(self.platform["id"])

# ---------------------------------------------------------------------------
# Icons (for download/audio buttons)
# ---------------------------------------------------------------------------
class _DownloadArrowIcon(Widget):
    def __init__(self, color=(1, 1, 1, 1), **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(20), dp(20)))
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color)
            self._stem = Line(points=[0, 0, 0, 0], width=dp(1.8), cap="round")
            self._arrow = Line(points=[0, 0, 0, 0, 0, 0], width=dp(1.8), joint="round", cap="round")
            self._base = Line(points=[0, 0, 0, 0], width=dp(1.8), cap="round")
        self.bind(pos=self._upd, size=self._upd)
        self._upd()

    def _upd(self, *a):
        cx = self.x + self.width / 2
        top = self.y + self.height * 0.95
        mid = self.y + self.height * 0.35
        w = self.width * 0.35
        self._stem.points = [cx, top, cx, mid]
        self._arrow.points = [cx - w, mid + self.height * 0.1, cx, mid - self.height * 0.05, cx + w, mid + self.height * 0.1]
        self._base.points = [self.x + self.width * 0.1, self.y + self.height * 0.05, self.x + self.width * 0.9, self.y + self.height * 0.05]

class _MusicNoteIcon(Widget):
    def __init__(self, color=(1, 1, 1, 1), **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(20), dp(20)))
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color)
            self._stem = Line(points=[0, 0, 0, 0], width=dp(1.8), cap="round")
            self._flag = Line(points=[0, 0, 0, 0, 0, 0], width=dp(1.8), joint="round", cap="round")
            self._head = Ellipse(pos=(0, 0), size=(0, 0))
        self.bind(pos=self._upd, size=self._upd)
        self._upd()

    def _upd(self, *a):
        head_r = self.width * 0.22
        hx = self.x + self.width * 0.35
        hy = self.y + self.height * 0.25
        self._head.pos = (hx - head_r, hy - head_r)
        self._head.size = (head_r * 2, head_r * 2)
        stem_x = hx + head_r * 0.9
        top_y = self.y + self.height * 0.95
        self._stem.points = [stem_x, hy, stem_x, top_y]
        self._flag.points = [stem_x, top_y, stem_x + self.width * 0.35, top_y - self.height * 0.15, stem_x, top_y - self.height * 0.30]

class _PlayTriangleIcon(Widget):
    def __init__(self, color=(1, 1, 1, 1), **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(24), dp(24)))
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color)
            self._tri = Mesh(mode="triangle_fan")
        self.bind(pos=self._upd, size=self._upd)
        self._upd()

    def _upd(self, *a):
        x0 = self.x + self.width * 0.32
        y0 = self.y + self.height * 0.18
        x1 = self.x + self.width * 0.32
        y1 = self.y + self.height * 0.82
        x2 = self.x + self.width * 0.88
        y2 = self.y + self.height * 0.50
        self._tri.vertices = [x0, y0, 0, 0, x1, y1, 0, 0, x2, y2, 0, 0]
        self._tri.indices = [0, 1, 2]

class _PlayOverlay(ElasticBehavior, Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(64), dp(64)))
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.05, 0.05, 0.08, 0.6)
            self._circle = Ellipse(pos=self.pos, size=self.size)
            Color(1, 1, 1, 0.9)
            self._ring = Line(circle=(0, 0, 0), width=dp(1.8))
        self.icon = _PlayTriangleIcon(color=(1, 1, 1, 1))
        self.add_widget(self.icon)
        self.bind(pos=self._upd, size=self._upd)
        self._upd()

    def _upd(self, *a):
        self._circle.pos = self.pos
        self._circle.size = self.size
        cx, cy = self.center_x, self.center_y
        self._ring.circle = (cx, cy, self.width / 2)
        self.icon.size = (self.width * 0.45, self.height * 0.45)
        self.icon.pos = (cx - self.icon.width / 2, cy - self.icon.height / 2)

# ---------------------------------------------------------------------------
# Loading / Skeleton states
# ---------------------------------------------------------------------------
class SkeletonPulseWidget(GlassCard):
    """Pulsing placeholder for beautiful loading states."""
    def __init__(self, **kwargs):
        super().__init__(radius=dp(20), **kwargs)
        self.bg_color.rgba = (0.15, 0.15, 0.18, 0.4)
        self.border_color.rgba = (0, 0, 0, 0)
        self._anim = Animation(a=0.8, duration=0.8, t='in_out_sine') + Animation(a=0.4, duration=0.8, t='in_out_sine')
        self._anim.repeat = True
        self._anim.start(self.bg_color)

class ShimmerLine(Widget):
    """Indeterminate progress bar that looks elegant."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(4)
        with self.canvas:
            Color(1, 1, 1, 0.05)
            self.bg = RoundedRectangle(radius=[dp(2)])
            self.fill_color = Color(*NEON_CYAN)
            self.fill = RoundedRectangle(radius=[dp(2)])
        self.bind(pos=self._upd, size=self._upd)
        self.fill_width = 0
        self.fill_x = 0
        self._anim = None

    def _upd(self, *a):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.fill.pos = (self.x + self.fill_x, self.y)
        self.fill.size = (self.fill_width, self.size[1])

    def start(self):
        if self._anim: Animation.cancel_all(self)
        self.fill_width = self.width * 0.3
        self.fill_x = -self.fill_width
        self._anim = Animation(fill_x=self.width, duration=1.2, t='in_out_quad')
        self._anim.bind(on_complete=self._restart_anim)
        self._anim.start(self)

    def _restart_anim(self, *args):
        self.fill_x = -self.fill_width
        self._anim.start(self)

    def stop(self, success=True):
        if self._anim: Animation.cancel_all(self)
        if success:
            self.fill_color.rgba = NEON_GREEN
            Animation(fill_x=0, fill_width=self.width, duration=0.3, t='out_quad').start(self)
        else:
            self.fill_color.rgba = NEON_RED
            Animation(fill_x=0, fill_width=self.width, duration=0.3, t='out_quad').start(self)

# ---------------------------------------------------------------------------
# Notification Toast (Dialog replacement)
# ---------------------------------------------------------------------------
class ToastContainer(FloatLayout):
    def show_toast(self, text, is_error=False):
        toast = GlassCard(radius=dp(16), size_hint=(None, None), size=(dp(300), dp(50)))
        toast.pos_hint = {'center_x': 0.5}
        toast.y = -dp(100)
        if is_error:
            toast.border_color.rgba = (*NEON_RED[:3], 0.4)
            toast.bg_color.rgba = (*NEON_RED[:3], 0.1)
        else:
            toast.border_color.rgba = (*NEON_GREEN[:3], 0.4)
            toast.bg_color.rgba = (*NEON_GREEN[:3], 0.1)
        lbl = Label(text=ar(text), color=TEXT_MAIN, font_size="13sp", bold=True)
        toast.add_widget(lbl)
        self.add_widget(toast)
        anim = Animation(y=dp(40), duration=0.5, t='out_back')
        anim.bind(on_complete=lambda *args: Clock.schedule_once(lambda dt: self._hide_toast(toast), 3.0))
        anim.start(toast)

    def _hide_toast(self, toast):
        anim = Animation(y=-dp(100), opacity=0, duration=0.4, t='in_back')
        anim.bind(on_complete=lambda *args: self.remove_widget(toast))
        anim.start(toast)

# ---------------------------------------------------------------------------
# History Row
# ---------------------------------------------------------------------------
class HistoryRow(ElasticBehavior, GlassCard):
    """Modern notification-style history item."""
    def __init__(self, platform_id, filename, ts, **kwargs):
        super().__init__(radius=dp(16), **kwargs)
        self.size_hint_y = None
        self.height = dp(64)
        self.padding = [dp(12), dp(8), dp(12), dp(8)]
        self.spacing = dp(14)
        self.bg_color.rgba = (0.1, 0.1, 0.13, 0.5)
        p = PLATFORM_BY_ID.get(platform_id, PLATFORMS[0])
        icon_box = AnchorLayout(size_hint=(None, None), size=(dp(40), dp(48)))
        icon_bg = Widget(size_hint=(None, None), size=(dp(40), dp(40)))
        with icon_bg.canvas:
            Color(*p["color"][:3], 0.2)
            self._ebg = Ellipse(pos=icon_bg.pos, size=icon_bg.size)
        icon_bg.bind(pos=lambda i, v: setattr(self._ebg, "pos", v))
        icon_box.add_widget(icon_bg)
        # Use CDN icon
        icon_url = ICON_URLS.get(p["id"])
        icon_img = AsyncImage(
            source=icon_url,
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_x':0.5, 'center_y':0.5}
        )
        fallback = Label(
            text=p.get("letter", p["id"][0].upper()),
            font_size="14sp", bold=True, color=p["color"],
            size_hint=(None, None), size=(dp(24), dp(24)),
            pos_hint={'center_x':0.5, 'center_y':0.5}
        )
        fallback.opacity = 0
        icon_img.bind(on_error=lambda inst, val: setattr(fallback, 'opacity', 1))
        icon_box.add_widget(icon_img)
        icon_box.add_widget(fallback)
        self.add_widget(icon_box)
        text_box = BoxLayout(orientation="vertical", spacing=dp(2))
        name = os.path.basename(filename) if filename else "-"
        text_box.add_widget(Label(
            text=name, font_size="14sp", color=TEXT_MAIN, bold=True,
            halign="left", valign="bottom", shorten=True, shorten_from="right",
            text_size=(dp(180), dp(22))
        ))
        import datetime
        date_str = datetime.datetime.fromtimestamp(ts).strftime("%d %b • %H:%M") if ts else ""
        text_box.add_widget(Label(
            text=date_str, font_size="11sp", color=TEXT_MUTED,
            halign="left", valign="top", text_size=(dp(180), dp(18))
        ))
        self.add_widget(text_box)
        self.add_widget(Widget()) # spacer

# ---------------------------------------------------------------------------
# Media Preview Card
# ---------------------------------------------------------------------------
class MediaPreviewCard(GlassCard):
    """Beautiful dynamic media preview card."""
    def __init__(self, data, platform_color, original_url, on_download_video=None, on_download_audio=None, on_play=None, **kwargs):
        super().__init__(radius=dp(24), **kwargs)
        self.orientation = "vertical"
        self.padding = [dp(16), dp(16), dp(16), dp(16)]
        self.spacing = dp(16)
        self.size_hint_y = None
        self.height = dp(420)
        self.border_color.rgba = (*platform_color[:3], 0.3)
        self.bg_color.rgba = (0.1, 0.1, 0.14, 0.7)
        self.original_url = original_url
        # Thumbnail area with Stencil clipping for perfect rounded corners
        thumb_wrap = FloatLayout(size_hint_y=None, height=dp(210))
        with thumb_wrap.canvas.before:
            StencilPush()
            self._thumb_mask = RoundedRectangle(radius=[dp(18)])
            StencilUse()
            Color(0.05, 0.05, 0.08, 1)
            self._thumb_bg = RoundedRectangle(radius=[dp(18)])
        with thumb_wrap.canvas.after:
            StencilUnUse()
            self._thumb_mask_after = RoundedRectangle(radius=[dp(18)])
            StencilPop()
        thumb_wrap.bind(pos=self._upd_thumb, size=self._upd_thumb)
        thumb = AsyncImage(
            source=data.get("thumbnail") or "", allow_stretch=True, keep_ratio=True,
            size_hint=(1, 1), pos_hint={"x": 0, "y": 0}
        )
        thumb_wrap.add_widget(thumb)
        play_btn = _PlayOverlay(pos_hint={"center_x": 0.5, "center_y": 0.5})
        play_btn.bind(on_release=lambda *a: on_play and on_play(original_url, None))
        thumb_wrap.add_widget(play_btn)
        self.add_widget(thumb_wrap)
        # Info Area
        info_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(48), spacing=dp(4))
        title = Label(
            text=ar(data.get("title") or ""), font_size="16sp", bold=True, color=TEXT_MAIN,
            size_hint_y=None, height=dp(24), halign="left", valign="middle",
            shorten=True, shorten_from="right", text_size=(dp(280), dp(24))
        )
        info_box.add_widget(title)
        meta_row = BoxLayout(spacing=dp(12), size_hint_y=None, height=dp(18))
        dur = data.get("duration")
        dur_txt = "-"
        if isinstance(dur, (int, float)) and dur > 0:
            m, s = divmod(int(dur), 60)
            dur_txt = f"{m}:{s:02d}"
        res_txt = data.get("resolution") or "HD"
        fs = data.get("filesize")
        fs_txt = f"{fs / (1024*1024):.1f} MB" if fs else "Unknown"
        meta_text = f"{dur_txt} • {res_txt} • {fs_txt}"
        meta_row.add_widget(Label(text=meta_text, font_size="12sp", color=TEXT_MUTED, halign="left", text_size=(dp(280), dp(18))))
        info_box.add_widget(meta_row)
        self.add_widget(info_box)
        # Actions
        btn_col = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(96))
        video_btn = PremiumButton(
            text=ar("تحميل الفيديو"), gradient=(platform_color, NEON_PURPLE),
            text_color=(1, 1, 1, 1), icon_widget=_DownloadArrowIcon(color=(1, 1, 1, 1))
        )
        video_btn.height = dp(44)
        video_btn.bind(on_release=lambda *a: on_download_video and on_download_video())
        btn_col.add_widget(video_btn)
        audio_btn = PremiumButton(
            text=ar("الصوت فقط"), bg_color=(0.15, 0.15, 0.20, 1),
            text_color=TEXT_MAIN, icon_widget=_MusicNoteIcon(color=TEXT_MAIN)
        )
        audio_btn.height = dp(44)
        audio_btn.bind(on_release=lambda *a: on_download_audio and on_download_audio())
        btn_col.add_widget(audio_btn)
        self.add_widget(btn_col)

    def _upd_thumb(self, inst, val):
        self._thumb_mask.pos = inst.pos
        self._thumb_mask.size = inst.size
        self._thumb_bg.pos = inst.pos
        self._thumb_bg.size = inst.size
        self._thumb_mask_after.pos = inst.pos
        self._thumb_mask_after.size = inst.size

# ---------------------------------------------------------------------------
# Internal Video Player - PROFESSIONAL FIXED VERSION
# ---------------------------------------------------------------------------
class VideoPlayerPopup(ModalView):
    def __init__(self, original_url, play_url=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.auto_dismiss = False
        self.background_color = (0, 0, 0, 0.98)
        self.original_url = original_url
        self.play_url = play_url
        self._temp_file = None
        self._video_player = None
        self._native_player = None
        self._cancelled = False

        self._root = FloatLayout()

        # Loading Overlay
        self._loading = BoxLayout(
            orientation='vertical',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.8, 0.5),
            spacing=dp(20)
        )

        self._spinner = Widget(size_hint=(None, None), size=(dp(70), dp(70)))
        with self._spinner.canvas:
            Color(*NEON_CYAN)
            self._spinner_arc = Ellipse(
                pos=self._spinner.pos, size=self._spinner.size,
                angle_start=0, angle_end=300
            )
        self._spinner.bind(pos=self._upd_spinner, size=self._upd_spinner)
        self._spin_anim = (
            Animation(angle_end=660, duration=0.8, t='linear') + 
            Animation(angle_start=360, duration=0)
        )
        self._spin_anim.repeat = True

        spinner_anchor = AnchorLayout(size_hint_y=None, height=dp(90))
        spinner_anchor.add_widget(self._spinner)
        self._loading.add_widget(spinner_anchor)

        self._loading.add_widget(Label(
            text=ar("جاري تحضير الفيديو..."), font_size="20sp",
            color=TEXT_MAIN, bold=True
        ))
        self._loading.add_widget(Label(
            text=ar("يتم تحميل البيانات مؤقتاً للتشغيل السلس"),
            font_size="13sp", color=TEXT_MUTED
        ))

        self._progress = Slider(
            min=0, max=100, value=0, size_hint_y=None, height=dp(4),
            cursor_size=(0, 0), value_track=True, value_track_color=NEON_CYAN
        )
        self._loading.add_widget(self._progress)
        self._root.add_widget(self._loading)

        # Close Button
        close_btn = Button(
            text='✕', size_hint=(None, None), size=(dp(44), dp(44)),
            pos_hint={'right': 0.98, 'top': 0.98},
            background_normal='', background_color=(0.15, 0.15, 0.15, 0.7),
            color=(1, 1, 1, 1), font_size='18sp', bold=True
        )
        close_btn.bind(on_release=self._force_close)
        self._root.add_widget(close_btn)

        # Error Overlay
        self._error_box = BoxLayout(
            orientation='vertical',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.8, 0.4), spacing=dp(15), opacity=0
        )
        self._error_box.add_widget(Label(text="⚠️", font_size="48sp", color=NEON_RED))
        self._error_msg = Label(
            text="", font_size="15sp", color=TEXT_MAIN,
            halign='center', text_size=(dp(300), None)
        )
        self._error_box.add_widget(self._error_msg)

        retry_btn = PremiumButton(
            text=ar("إعادة المحاولة"), size_hint=(None, None),
            size=(dp(160), dp(48)), bg_color=(*NEON_CYAN[:3], 0.2), text_color=NEON_CYAN
        )
        retry_btn.bind(on_release=self._retry)
        self._error_box.add_widget(retry_btn)
        self._root.add_widget(self._error_box)

        self.add_widget(self._root)
        self._spin_anim.start(self._spinner_arc)

        threading.Thread(target=self._prepare, daemon=True).start()

    def _upd_spinner(self, *args):
        self._spinner_arc.pos = self._spinner.pos
        self._spinner_arc.size = self._spinner.size

    def _prepare(self):
        try:
            video_url = self.play_url
            if not video_url or not video_url.startswith('http'):
                try:
                    opts = {
                        "quiet": True, "no_warnings": True, "noprogress": True,
                        "logger": _SilentLogger(), "socket_timeout": 15,
                        "format": "best[ext=mp4]/best",
                    }
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(self.original_url, download=False)
                        if info:
                            fmts = info.get('formats', [])
                            for f in fmts:
                                if (f.get('ext') == 'mp4' and 
                                    f.get('vcodec') not in (None, 'none') and 
                                    f.get('acodec') not in (None, 'none')):
                                    video_url = f.get('url')
                                    break
                            if not video_url:
                                video_url = info.get('url')
                except Exception as e:
                    Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)
                    return

            if not video_url:
                Clock.schedule_once(
                    lambda dt: self._show_error(ar("تعذر استخراج رابط الفيديو")), 0)
                return

            if self._try_native_android(video_url):
                return

            Clock.schedule_once(lambda dt: self._buffer_and_play(video_url), 0)

        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)

    def _try_native_android(self, video_url):
        try:
            from jnius import autoclass
            from android.runnable import run_on_ui_thread

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            MediaPlayer = autoclass('android.media.MediaPlayer')
            SurfaceView = autoclass('android.view.SurfaceView')
            LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')

            activity = PythonActivity.mActivity
            self._surface_view = SurfaceView(activity)
            holder = self._surface_view.getHolder()

            @run_on_ui_thread
            def add_view():
                params = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
                activity.addContentView(self._surface_view, params)
            add_view()

            self._native_player = MediaPlayer()
            self._native_player.setDataSource(video_url)
            self._native_player.setDisplay(holder)

            OnPrepared = autoclass('android.media.MediaPlayer$OnPreparedListener')
            class PrepListener(OnPrepared):
                def __init__(self, popup): super().__init__(); self.popup = popup
                def onPrepared(self, mp):
                    Clock.schedule_once(lambda dt: self.popup._native_ready(), 0)
                    mp.start()
            self._native_player.setOnPreparedListener(PrepListener(self))

            OnError = autoclass('android.media.MediaPlayer$OnErrorListener')
            class ErrListener(OnError):
                def __init__(self, popup): super().__init__(); self.popup = popup
                def onError(self, mp, what, extra):
                    Clock.schedule_once(lambda dt: self.popup._native_failed(), 0)
                    return True
            self._native_player.setOnErrorListener(ErrListener(self))

            self._native_player.prepareAsync()
            return True
        except Exception as e:
            print(f"[NATIVE] Failed: {e}")
            return False

    def _native_ready(self):
        self._spin_anim.cancel(self._spinner_arc)
        self._loading.opacity = 0
        controls = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(50),
            pos_hint={'bottom': 1}, padding=dp(10), spacing=dp(10), opacity=0.6
        )
        self._play_btn = Button(
            text='⏸', size_hint_x=None, width=dp(50),
            background_normal='', background_color=(0.2, 0.2, 0.2, 0.8)
        )
        self._play_btn.bind(on_release=self._toggle_native)
        controls.add_widget(self._play_btn)

        stop_btn = Button(
            text='⏹', size_hint_x=None, width=dp(50),
            background_normal='', background_color=NEON_RED
        )
        stop_btn.bind(on_release=self._force_close)
        controls.add_widget(stop_btn)
        self._root.add_widget(controls)
        self._native_controls = controls

    def _toggle_native(self, *args):
        if self._native_player:
            if self._native_player.isPlaying():
                self._native_player.pause()
                self._play_btn.text = '▶'
            else:
                self._native_player.start()
                self._play_btn.text = '⏸'

    def _native_failed(self):
        self._cleanup_native()
        self._buffer_and_play(self.play_url or self.original_url)

    def _cleanup_native(self):
        try:
            if self._native_player:
                self._native_player.release()
                self._native_player = None
            if hasattr(self, '_surface_view') and self._surface_view:
                from android.runnable import run_on_ui_thread
                @run_on_ui_thread
                def remove():
                    parent = self._surface_view.getParent()
                    if parent: parent.removeView(self._surface_view)
                remove()
        except: pass

    def _buffer_and_play(self, video_url):
        def _thread():
            try:
                import urllib.request
                import tempfile

                Clock.schedule_once(
                    lambda dt: setattr(self._loading.children[1], 'text', 
                    ar("جاري التخزين المؤقت...")), 0)

                req = urllib.request.Request(video_url, headers={
                    'User-Agent': get_ua(), 'Accept': '*/*'
                })

                with urllib.request.urlopen(req, timeout=30) as resp:
                    total = int(resp.headers.get('content-length', 0)) or 5*1024*1024
                    chunk_size = 8192
                    downloaded = 0

                    fd, path = tempfile.mkstemp(suffix='.mp4')
                    with os.fdopen(fd, 'wb') as tmp:
                        while True:
                            if self._cancelled:
                                os.remove(path); return
                            chunk = resp.read(chunk_size)
                            if not chunk: break
                            tmp.write(chunk)
                            downloaded += len(chunk)
                            progress = min((downloaded / total) * 100, 99)
                            Clock.schedule_once(
                                lambda dt, p=progress: setattr(self._progress, 'value', p), 0)

                self._temp_file = path
                Clock.schedule_once(lambda dt: self._play_local(path), 0)

            except Exception as e:
                Clock.schedule_once(lambda dt: self._play_stream(video_url), 0)

        threading.Thread(target=_thread, daemon=True).start()

    def _play_local(self, path):
        self._spin_anim.cancel(self._spinner_arc)
        self._loading.opacity = 0
        try:
            from kivy.uix.videoplayer import VideoPlayer
            self._video_player = VideoPlayer(
                source=path, state='play',
                options={'allow_stretch': True, 'eos': 'stop'}
            )
            self._video_player.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
            self._video_player.size_hint = (1, 1)
            self._root.add_widget(self._video_player)
        except Exception as e:
            self._show_error(ar("فشل تشغيل الفيديو: ") + str(e))

    def _play_stream(self, url):
        self._spin_anim.cancel(self._spinner_arc)
        self._loading.opacity = 0
        try:
            from kivy.uix.videoplayer import VideoPlayer
            self._video_player = VideoPlayer(
                source=url, state='play', options={'allow_stretch': True}
            )
            self._video_player.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
            self._video_player.size_hint = (1, 1)
            self._root.add_widget(self._video_player)
        except Exception as e:
            self._show_error(
                ar("فشل التشغيل. تأكد من إضافة ffpyplayer في buildozer.spec"))

    def _show_error(self, msg):
        self._spin_anim.cancel(self._spinner_arc)
        self._loading.opacity = 0
        self._error_msg.text = msg
        self._error_box.opacity = 1

    def _retry(self, *args):
        self._error_box.opacity = 0
        self._loading.opacity = 1
        self._spin_anim.start(self._spinner_arc)
        threading.Thread(target=self._prepare, daemon=True).start()

    def _force_close(self, *args):
        self._cancelled = True
        self._cleanup_native()
        if self._video_player: self._video_player.state = 'stop'
        self.dismiss()

    def on_dismiss(self):
        self._cancelled = True
        self._cleanup_native()
        if self._video_player: self._video_player.state = 'stop'
        if self._temp_file and os.path.exists(self._temp_file):
            try: os.remove(self._temp_file)
            except: pass
        super().on_dismiss()
# ---------------------------------------------------------------------------
# Main App Layout
# ---------------------------------------------------------------------------
class SaveProApp(App):
    def build(self):
        self.title = "Save Pro"
        init_db()
        self.selected_platform = "instagram"
        self._chips = {}
        # Root layout with dynamic animated background
        root = FloatLayout()
        with root.canvas.before:
            Color(*BG_DARK)
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
            Color(*NEON_PINK[:3], 0.04)
            self._blob1 = Ellipse(size=(dp(350), dp(350)))
            Color(*NEON_PURPLE[:3], 0.04)
            self._blob2 = Ellipse(size=(dp(400), dp(400)))
            Color(*NEON_CYAN[:3], 0.03)
            self._blob3 = Ellipse(size=(dp(300), dp(300)))
        self._drift_started = False
        root.bind(size=self._upd_bg, pos=self._upd_bg)
        # Main Scrollable Content
        main_scroll = ScrollView(effect_cls=DampedScrollEffect, size_hint=(1, 1))
        col = BoxLayout(orientation="vertical", padding=[dp(20), dp(30), dp(20), dp(40)], spacing=dp(28), size_hint_y=None)
        col.bind(minimum_height=col.setter('height'))
        # Header Section
        header = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(16))
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            header.add_widget(KvImage(source=icon_path, size_hint=(None, None), size=(dp(56), dp(56))))
        else:
            # Fallback beautiful icon
            fallback = GlassCard(radius=dp(16), size_hint=(None, None), size=(dp(56), dp(56)))
            fallback.bg_color.rgba = (0.2, 0.2, 0.3, 1)
            fallback.add_widget(Label(text="SP", font_size="20sp", bold=True, color=NEON_CYAN))
            header.add_widget(fallback)
        title_box = BoxLayout(orientation="vertical", size_hint_x=None, spacing=0)
        title_box.bind(minimum_width=title_box.setter("width"))
        title_lbl = Label(
            text="Save Pro", font_size="28sp", bold=True,
            color=TEXT_MAIN, size_hint=(None, None), halign="left"
        )
        title_lbl.bind(texture_size=lambda i, v: setattr(title_lbl, "size", v))
        title_box.add_widget(title_lbl)
        tagline_lbl = Label(
            text=ar("نزّل من أي منصة بلمسة واحدة"),
            font_size="13sp", color=TEXT_MUTED, bold=True,
            size_hint=(None, None), halign="left"
        )
        tagline_lbl.bind(texture_size=lambda i, v: setattr(tagline_lbl, "size", v))
        title_box.add_widget(tagline_lbl)
        header.add_widget(title_box)
        header.add_widget(Widget())
        col.add_widget(header)
        # Platform Selector (Horizontal Scroll)
        plat_section = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(180), spacing=dp(12))
        plat_title = Label(
            text=ar("اختر المنصة"), font_size="15sp", bold=True, color=TEXT_MAIN,
            size_hint_y=None, height=dp(20), halign="left", text_size=(Window.width - dp(40), dp(20))
        )
        plat_section.add_widget(plat_title)
        h_scroll = ScrollView(effect_cls=DampedScrollEffect, size_hint_y=None, height=dp(140), do_scroll_y=False)
        chips_row = BoxLayout(orientation="horizontal", spacing=dp(16), size_hint_x=None, padding=[0, dp(4), dp(20), dp(4)])
        chips_row.bind(minimum_width=chips_row.setter("width"))
        for p in PLATFORMS:
            chip = PlatformCard(p, on_select=self.select_platform)
            self._chips[p["id"]] = chip
            chips_row.add_widget(chip)
        h_scroll.add_widget(chips_row)
        plat_section.add_widget(h_scroll)
        col.add_widget(plat_section)
        # Link Input Section
        link_section = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(200), spacing=dp(12))
        self._hint_lbl = Label(
            text=PLATFORM_BY_ID["instagram"]["hint"], font_size="15sp", bold=True,
            color=TEXT_MAIN, size_hint_y=None, height=dp(20), halign="left", text_size=(Window.width - dp(40), dp(20))
        )
        link_section.add_widget(self._hint_lbl)
        input_row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(12))
        self.ui = PremiumInput(hint_text=ar("الصق الرابط هنا..."))
        input_row.add_widget(self.ui)
        paste_btn = PremiumButton(text=ar("لصق"), bg_color=(0.15, 0.15, 0.20, 1), text_color=TEXT_MAIN)
        paste_btn.size_hint_x = None
        paste_btn.width = dp(80)
        paste_btn.bind(on_release=self.do_paste)
        input_row.add_widget(paste_btn)
        link_section.add_widget(input_row)
        self.preview_btn = PremiumButton(text=ar("معاينة"), gradient=(NEON_CYAN, NEON_BLUE), text_color=(1, 1, 1, 1))
        self.preview_btn.bind(on_release=self.do_preview)
        link_section.add_widget(self.preview_btn)
        col.add_widget(link_section)
        # Progress Indicator (Hidden by default)
        self.progress_bar = ShimmerLine()
        self.progress_bar.opacity = 0
        col.add_widget(self.progress_bar)
        # Dynamic Preview Container
        self.preview_container = BoxLayout(orientation="vertical", size_hint_y=None, height=0)
        col.add_widget(self.preview_container)
        # Download History Section
        hist_section = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(12))
        hist_section.bind(minimum_height=hist_section.setter("height"))
        hist_title_row = BoxLayout(size_hint_y=None, height=dp(24))
        hist_title = Label(
            text=ar("التنزيلات الأخيرة"), font_size="15sp", bold=True, color=TEXT_MAIN,
            halign="left", text_size=(Window.width - dp(40), dp(24))
        )
        hist_title_row.add_widget(hist_title)
        hist_section.add_widget(hist_title_row)
        self.hist_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        self.hist_list.bind(minimum_height=self.hist_list.setter("height"))
        hist_section.add_widget(self.hist_list)
        col.add_widget(hist_section)
        # Copyright footer (English)
        footer = BoxLayout(size_hint_y=None, height=dp(30))
        footer.add_widget(Label(
            text="© 2026 Youssef Mansouri",
            font_size="12sp", color=TEXT_FAINT, halign='center', valign='middle',
            size_hint=(1,1)
        ))
        col.add_widget(footer)
        main_scroll.add_widget(col)
        root.add_widget(main_scroll)
        # Global Toast Container
        self.toast = ToastContainer()
        root.add_widget(self.toast)
        self.select_platform("instagram")
        self._refresh_history()
        return root

    # -- Background Animation --
    def _upd_bg(self, inst, val):
        self._bg_rect.pos = inst.pos
        self._bg_rect.size = inst.size
        self._blob1.pos = (inst.x - dp(100), inst.y + inst.height * 0.6)
        self._blob2.pos = (inst.x + inst.width * 0.4, inst.y + inst.height * 0.3)
        self._blob3.pos = (inst.x + inst.width * 0.1, inst.y - dp(100))
        if not self._drift_started:
            self._drift_started = True
            self._start_drift()

    def _start_drift(self):
        def loop(ellipse, dx, dy, dur):
            p0 = ellipse.pos
            p1 = (p0[0] + dx, p0[1] + dy)
            anim = Animation(pos=p1, duration=dur, t="in_out_sine")
            anim += Animation(pos=p0, duration=dur, t="in_out_sine")
            anim.repeat = True
            anim.start(ellipse)
        loop(self._blob1, dp(40), -dp(30), 12)
        loop(self._blob2, -dp(35), dp(40), 15)
        loop(self._blob3, dp(25), dp(20), 10)

    # -- Platform Selection --
    def select_platform(self, platform_id):
        self.selected_platform = platform_id
        for pid, chip in self._chips.items():
            chip.set_selected(pid == platform_id)
        p = PLATFORM_BY_ID[platform_id]
        self._hint_lbl.text = p["hint"]
        self.ui.cursor_color = p["color"]

    # -- Interactions --
    def do_paste(self, *a):
        try:
            txt = Clipboard.paste()
            if not txt or not txt.strip():
                self.toast.show_toast(ar("لا يوجد نص في الحافظة"), is_error=True)
                return
            self.ui.text = txt.strip()
            Animation(rgba=(*NEON_CYAN[:3], 0.8), duration=0.2).start(self.ui._glow_color)
            Clock.schedule_once(lambda dt: Animation(rgba=GLASS_BORDER, duration=0.3).start(self.ui._glow_color), 0.3)
        except Exception:
            self.toast.show_toast(ar("لا يوجد نص في الحافظة"), is_error=True)

    def do_preview(self, *a):
        url = self.ui.text.strip()
        if not url:
            self.toast.show_toast(ar("الصق الرابط أولاً"), is_error=True)
            return
        self.preview_btn.disabled = True
        self.progress_bar.opacity = 1
        self.progress_bar.start()
        # Show Skeleton loader in preview container
        self.preview_container.clear_widgets()
        skeleton = SkeletonPulseWidget(size_hint_y=None, height=dp(420))
        self.preview_container.add_widget(skeleton)
        Animation(height=dp(420), duration=0.4, t='out_quint').start(self.preview_container)
        threading.Thread(target=self._preview_th, args=(url,)).start()

    def _preview_th(self, url):
        data, err = fetch_preview(url)
        Clock.schedule_once(lambda dt: self._preview_done(data, err, url), 0)

    def _preview_done(self, data, err, url):
        self.preview_btn.disabled = False
        self.progress_bar.stop(success=not bool(err))
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'opacity', 0), 0.4)
        self.preview_container.clear_widgets()
        if err or not data:
            Animation(height=0, duration=0.3, t='in_quint').start(self.preview_container)
            self.toast.show_toast(ar("تعذّرت المعاينة: ") + (err or ""), is_error=True)
            return
        platform_color = PLATFORM_BY_ID[self.selected_platform]["color"]
        card = MediaPreviewCard(
            data, platform_color, original_url=url,
            on_download_video=lambda: self.do_download(url, "video"),
            on_download_audio=lambda: self.do_download(url, "audio"),
            on_play=self.open_player,
        )
        # Fade in card
        card.opacity = 0
        self.preview_container.add_widget(card)
        Animation(height=dp(420), duration=0.4, t='out_quint').start(self.preview_container)
        Animation(opacity=1, duration=0.4).start(card)

    def open_player(self, original_url, play_url):
        if not original_url and not play_url:
            self.toast.show_toast(ar("تعذّر تشغيل المعاينة، جرّب التحميل مباشرة"), is_error=True)
            return
        popup = VideoPlayerPopup(original_url, play_url)
        popup.open()

    def do_download(self, url, kind):
        self.progress_bar.opacity = 1
        self.progress_bar.start()
        self.toast.show_toast("Downloading...")  # English
        threading.Thread(target=self._dl_th, args=(url, self.selected_platform, kind)).start()

    def _dl_th(self, url, platform_id, kind):
        try:
            try:
                from android.storage import primary_external_storage_path
                base = primary_external_storage_path()
            except Exception:
                base = os.path.expanduser("~")
            sd = os.path.join(base, "Download", "SavePro", platform_id + "_" + kind + "_" + str(int(time.time())))
            if kind == "audio":
                files, err = download_audio_only(url, sd)
            else:
                files, err = download_media(url, sd)
            Clock.schedule_once(lambda dt: self._dl_done(files, err, url, platform_id), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._dl_done(None, str(e)[:150], url, platform_id), 0)

    def _dl_done(self, files, err, url, platform_id):
        if err:
            self.progress_bar.stop(success=False)
            self.toast.show_toast(ar("فشل: ") + err, is_error=True)
        else:
            self.progress_bar.stop(success=True)
            self.toast.show_toast("Download complete")  # English
            for f in files:
                save_history(platform_id, url, f)
            self.ui.text = ""
            self.preview_container.clear_widgets()
            Animation(height=0, duration=0.3, t='in_quint').start(self.preview_container)
            self._refresh_history()
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'opacity', 0), 0.5)

    def _refresh_history(self):
        self.hist_list.clear_widgets()
        rows = get_history(12)
        if not rows:
            empty_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(100), spacing=dp(8))
            empty_box.add_widget(Label(text="👻", font_size="32sp", size_hint_y=None, height=dp(40)))
            empty_box.add_widget(Label(
                text=ar("لا توجد تنزيلات بعد"), font_size="14sp", color=TEXT_FAINT,
                size_hint_y=None, height=dp(30)
            ))
            self.hist_list.add_widget(empty_box)
            return
        for platform_id, url, filename, ts in rows:
            self.hist_list.add_widget(HistoryRow(platform_id, filename, ts))

def _write_crash_log(tb_text):
    try:
        try:
            from android.storage import primary_external_storage_path
            base = primary_external_storage_path()
        except Exception:
            base = os.path.expanduser("~")
        crash_dir = os.path.join(base, "Download", "SavePro")
        os.makedirs(crash_dir, exist_ok=True)
        with open(os.path.join(crash_dir, "crash_log.txt"), "w", encoding="utf-8") as f:
            f.write(tb_text)
    except Exception:
        pass

if __name__ == "__main__":
    try:
        SaveProApp().run()
    except Exception:
        import traceback
        _write_crash_log(traceback.format_exc())
        raise