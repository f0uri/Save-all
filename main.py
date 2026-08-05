#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Save Pro - Universal Media Downloader
Copyright 2026 Youssef Mansouri
Neon, iOS-style, multi-platform downloader (Instagram / TikTok / Facebook / X / Pinterest)
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
        '؀' <= ch <= 'ۿ' or 'ݐ' <= ch <= 'ݿ'
        or 'ࢠ' <= ch <= 'ࣿ' or 'ﭐ' <= ch <= '﷿'
        or 'ﹰ' <= ch <= '﻿'
        for ch in text
    )
    if not has_arabic:
        return text
    try:
        return _shape_arabic(_strip_unsupported_glyphs(text))
    except Exception:
        return text

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage, Image as KvImage
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Mesh
from kivy.metrics import dp
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior

Window.softinput_mode = "below_target"

_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoNaskhArabic-Regular.ttf")
if os.path.exists(_FONT_PATH):
    LabelBase.register(DEFAULT_FONT, _FONT_PATH)

# ---------------------------------------------------------------------------
# Neon dark palette
# ---------------------------------------------------------------------------
BG_DARK = (0.043, 0.043, 0.078, 1)
CARD_DARK = (0.086, 0.086, 0.145, 0.92)
CARD_DARK_2 = (0.11, 0.11, 0.18, 0.92)

NEON_PINK = (1.0, 0.20, 0.66, 1)
NEON_PURPLE = (0.62, 0.26, 1.0, 1)
NEON_CYAN = (0.0, 0.92, 1.0, 1)
NEON_BLUE = (0.20, 0.55, 1.0, 1)
NEON_INDIGO = (0.47, 0.42, 1.0, 1)
NEON_RED = (1.0, 0.20, 0.32, 1)
NEON_GREEN = (0.25, 1.0, 0.62, 1)
NEON_YELLOW = (1.0, 0.85, 0.25, 1)

TEXT_MAIN = (0.94, 0.95, 1.0, 1)
TEXT_MUTED = (0.56, 0.58, 0.70, 1)
TEXT_FAINT = (0.40, 0.42, 0.54, 1)

Window.clearcolor = BG_DARK

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
# Platform definitions
# ---------------------------------------------------------------------------
PLATFORMS = [
    {"id": "instagram", "mono": "IG", "label": ar("انستقرام"),
     "color": NEON_PINK, "hint": ar("الصق رابط ريلز أو منشور من انستقرام")},
    {"id": "tiktok", "mono": "TT", "label": ar("تيك توك"),
     "color": NEON_CYAN, "hint": ar("الصق رابط فيديو من تيك توك")},
    {"id": "facebook", "mono": "f", "label": ar("فيسبوك"),
     "color": NEON_BLUE, "hint": ar("الصق رابط فيديو أو ريلز من فيسبوك")},
    {"id": "x", "mono": "X", "label": "X",
     "color": NEON_INDIGO, "hint": ar("الصق رابط فيديو من منصة X")},
    {"id": "pinterest", "mono": "P", "label": ar("بنترست"),
     "color": NEON_RED, "hint": ar("الصق رابط بن من بنترست")},
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
    opts = {
        "outtmpl": os.path.join(download_dir, "%(title).80s.%(ext)s"),
        "format": "bestvideo+bestaudio/best/bestaudio",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": _SilentLogger(),
        "user_agent": get_ua(),
        "retries": 2,
        "socket_timeout": 20,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None, ar("فشل التحميل")
        files = [
            os.path.join(download_dir, f)
            for f in sorted(os.listdir(download_dir))
            if os.path.isfile(os.path.join(download_dir, f)) and not f.endswith((".json", ".txt", ".part"))
        ]
        if not files:
            return None, ar("لم يتم العثور على ملفات")
        return files, None
    except Exception as e:
        return None, str(e)[:300]

def fetch_preview(url):
    """Fetch metadata + a direct playable URL WITHOUT downloading, for in-app preview."""
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
        return {
            "title": info.get("title") or ar("بدون عنوان"),
            "thumbnail": info.get("thumbnail") or "",
            "duration": info.get("duration"),
            "play_url": play_url,
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


def _rr(pos, size, radius):
    return (pos[0], pos[1], size[0], size[1], radius)

class GlowPanel(BoxLayout):
    """A dark rounded panel with a soft neon-glow border."""
    def __init__(self, glow_color=NEON_PURPLE, radius=dp(20), fill=CARD_DARK, **kwargs):
        super().__init__(**kwargs)
        self._radius = radius
        self._glow = glow_color
        with self.canvas.before:
            Color(*glow_color[:3], 0.10)
            self._g3 = Line(rounded_rectangle=(0, 0, 0, 0, radius), width=dp(9))
            Color(*glow_color[:3], 0.18)
            self._g2 = Line(rounded_rectangle=(0, 0, 0, 0, radius), width=dp(5))
            Color(*fill)
            self._fill = RoundedRectangle(radius=[radius] * 4)
            Color(*glow_color[:3], 0.75)
            self._g1 = Line(rounded_rectangle=(0, 0, 0, 0, radius), width=dp(1.4))
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._fill.pos = self.pos
        self._fill.size = self.size
        for g in (self._g1, self._g2, self._g3):
            g.rounded_rectangle = _rr(self.pos, self.size, self._radius)

class NeonInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(54)
        self.font_size = "15sp"
        self.padding = [dp(16), dp(17), dp(16), dp(14)]
        self.background_normal = ""
        self.background_active = ""
        self.background_color = (0, 0, 0, 0)
        self.foreground_color = TEXT_MAIN
        self.hint_text_color = TEXT_FAINT
        self.cursor_color = NEON_CYAN
        with self.canvas.before:
            Color(*CARD_DARK_2)
            self._bg = RoundedRectangle(radius=[dp(16)] * 4)
            self._glow_color = Color(*NEON_PURPLE[:3], 0.35)
            self._border = Line(rounded_rectangle=(0, 0, 0, 0, dp(16)), width=dp(1.4))
        self.bind(pos=self._upd, size=self._upd, focus=self._on_focus)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = _rr(self.pos, self.size, dp(16))

    def _on_focus(self, inst, val):
        target = 0.95 if val else 0.35
        Animation(a=target, duration=0.18).start(self._glow_color)

class _DownloadArrowIcon(Widget):
    def __init__(self, color=(1, 1, 1, 1), **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(18), dp(18)))
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
        top = self.y + self.height * 0.92
        mid = self.y + self.height * 0.42
        w = self.width * 0.34
        self._stem.points = [cx, top, cx, mid]
        self._arrow.points = [cx - w, mid + self.height * 0.05, cx, mid - self.height * 0.08, cx + w, mid + self.height * 0.05]
        self._base.points = [self.x + self.width * 0.12, self.y + self.height * 0.06, self.x + self.width * 0.88, self.y + self.height * 0.06]

class _MusicNoteIcon(Widget):
    def __init__(self, color=(1, 1, 1, 1), **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(18), dp(18)))
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color)
            self._stem = Line(points=[0, 0, 0, 0], width=dp(1.6), cap="round")
            self._flag = Line(points=[0, 0, 0, 0, 0, 0], width=dp(1.6), joint="round", cap="round")
            self._head = Ellipse(pos=(0, 0), size=(0, 0))
        self.bind(pos=self._upd, size=self._upd)
        self._upd()

    def _upd(self, *a):
        head_r = self.width * 0.20
        hx = self.x + self.width * 0.32
        hy = self.y + self.height * 0.24
        self._head.pos = (hx - head_r, hy - head_r)
        self._head.size = (head_r * 2, head_r * 2)
        stem_x = hx + head_r * 0.9
        top_y = self.y + self.height * 0.90
        self._stem.points = [stem_x, hy, stem_x, top_y]
        self._flag.points = [stem_x, top_y, stem_x + self.width * 0.30, top_y - self.height * 0.14, stem_x, top_y - self.height * 0.26]

class _PlayTriangleIcon(Widget):
    def __init__(self, color=(1, 1, 1, 1), **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(22), dp(22)))
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color)
            self._tri = Mesh(mode="triangle_fan")
        self.bind(pos=self._upd, size=self._upd)
        self._upd()

    def _upd(self, *a):
        x0 = self.x + self.width * 0.30
        y0 = self.y + self.height * 0.16
        x1 = self.x + self.width * 0.30
        y1 = self.y + self.height * 0.84
        x2 = self.x + self.width * 0.86
        y2 = self.y + self.height * 0.50
        self._tri.vertices = [x0, y0, 0, 0, x1, y1, 0, 0, x2, y2, 0, 0]
        self._tri.indices = [0, 1, 2]

class _PlayOverlay(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(58), dp(58)))
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0, 0.45)
            self._circle = Ellipse(pos=self.pos, size=self.size)
            Color(1, 1, 1, 0.85)
            self._ring = Line(circle=(0, 0, 0), width=dp(1.4))
        self.icon = _PlayTriangleIcon(color=(1, 1, 1, 1))
        self.add_widget(self.icon)
        self.bind(pos=self._upd, size=self._upd)
        self._upd()

    def _upd(self, *a):
        self._circle.pos = self.pos
        self._circle.size = self.size
        cx = self.center_x
        cy = self.center_y
        r = self.width / 2
        self._ring.circle = (cx, cy, r)
        self.icon.size = (self.width * 0.5, self.height * 0.5)
        self.icon.pos = (cx - self.icon.width / 2, cy - self.icon.height / 2)

class NeonButton(ButtonBehavior, BoxLayout):
    def __init__(self, text="", color=NEON_PURPLE, text_color=None, icon_widget=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(54)
        self._color = color
        with self.canvas.before:
            Color(*color[:3], 0.22)
            self._g2 = Line(rounded_rectangle=(0, 0, 0, 0, dp(16)), width=dp(10))
            Color(*color)
            self._fill = RoundedRectangle(radius=[dp(16)] * 4)
        self.bind(pos=self._upd, size=self._upd)
        tcolor = text_color or (0.05, 0.05, 0.08, 1)
        self.add_widget(Widget())
        if icon_widget is not None:
            self.add_widget(icon_widget)
        self.label = Label(
            text=text, font_size="15.5sp", bold=True,
            color=tcolor, size_hint=(None, None),
        )
        self.label.bind(texture_size=lambda inst, val: setattr(self.label, "size", val))
        self.add_widget(self.label)
        self.add_widget(Widget())

    def _upd(self, *a):
        self._fill.pos = self.pos
        self._fill.size = self.size
        self._g2.rounded_rectangle = _rr(self.pos, self.size, dp(16))

    def on_press(self):
        Animation.cancel_all(self, "opacity")
        Animation(opacity=0.8, duration=0.06).start(self)

    def on_release(self):
        Animation.cancel_all(self, "opacity")
        Animation(opacity=1, duration=0.14).start(self)

class PlatformChip(ButtonBehavior, BoxLayout):
    def __init__(self, platform, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(6)
        self.platform = platform
        self.on_select = on_select
        self.selected = False
        self.size_hint_y = None
        self.height = dp(78)

        badge_wrap = AnchorLayout(size_hint_y=None, height=dp(52))
        self.badge = Widget(size_hint=(None, None), size=(dp(52), dp(52)))
        with self.badge.canvas:
            self._glow_c = Color(*platform["color"][:3], 0.0)
            self._glow = Line(circle=(0, 0, 0), width=dp(6))
            Color(*platform["color"])
            self._circle = Ellipse()
            Color(0, 0, 0, 0.22)
            self._ring = Line(circle=(0, 0, 0), width=dp(1.2))
        self.badge.bind(pos=self._upd_badge, size=self._upd_badge)
        badge_wrap.add_widget(self.badge)
        self.add_widget(badge_wrap)

        self._label = Label(
            text=platform["label"], font_size="12sp", color=TEXT_MUTED,
            size_hint_y=None, height=dp(18),
        )
        self.add_widget(self._label)

        self._mono_overlay = Label(
            text=platform["mono"], font_size="18sp", bold=True, color=(0.06, 0.06, 0.09, 1),
        )
        badge_wrap.add_widget(self._mono_overlay)

    def _upd_badge(self, *a):
        cx = self.badge.center_x
        cy = self.badge.center_y
        r = self.badge.width / 2
        self._circle.pos = (cx - r, cy - r)
        self._circle.size = (r * 2, r * 2)
        self._ring.circle = (cx, cy, r)
        self._glow.circle = (cx, cy, r + dp(3))

    def set_selected(self, selected):
        self.selected = selected
        if selected:
            self._glow_c.a = 0.55
            self._label.color = self.platform["color"]
            Animation(width=dp(60), height=dp(60), duration=0.16, t="out_back").start(self.badge)
        else:
            self._glow_c.a = 0.0
            self._label.color = TEXT_MUTED
            Animation(width=dp(52), height=dp(52), duration=0.16).start(self.badge)

    def on_release(self):
        if self.on_select:
            self.on_select(self.platform["id"])

# ---------------------------------------------------------------------------
# History row
# ---------------------------------------------------------------------------
class HistoryRow(BoxLayout):
    def __init__(self, platform_id, filename, ts, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(46)
        self.spacing = dp(10)
        self.padding = [dp(4), 0, dp(4), 0]
        p = PLATFORM_BY_ID.get(platform_id, PLATFORMS[0])
        dot = Widget(size_hint=(None, None), size=(dp(10), dp(10)))
        with dot.canvas:
            Color(*p["color"])
            self._e = Ellipse(pos=dot.pos, size=dot.size)
        dot.bind(pos=lambda i, v: setattr(self._e, "pos", v))
        wrap = AnchorLayout(size_hint=(None, None), size=(dp(20), dp(46)))
        wrap.add_widget(dot)
        self.add_widget(wrap)
        name = os.path.basename(filename) if filename else "-"
        self.add_widget(Label(
            text=name, font_size="12.5sp", color=TEXT_MAIN,
            halign="left", valign="middle", shorten=True, shorten_from="right",
            text_size=(dp(190), dp(20)),
        ))
        self.add_widget(Widget())

# ---------------------------------------------------------------------------
# Preview card: thumbnail + internal player + choose to download video/audio
# ---------------------------------------------------------------------------
class PreviewCard(GlowPanel):
    def __init__(self, data, platform_color, on_download_video=None, on_download_audio=None, on_play=None, **kwargs):
        super().__init__(glow_color=platform_color, radius=dp(20), **kwargs)
        self.orientation = "vertical"
        self.padding = [dp(14), dp(14), dp(14), dp(14)]
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(340)
        self.data = data

        thumb_wrap = FloatLayout(size_hint_y=None, height=dp(190))
        with thumb_wrap.canvas.before:
            Color(0.05, 0.05, 0.09, 1)
            self._thumb_bg = RoundedRectangle(radius=[dp(14)] * 4)
        thumb_wrap.bind(pos=lambda i, v: setattr(self._thumb_bg, "pos", v),
                         size=lambda i, v: setattr(self._thumb_bg, "size", v))
        thumb = AsyncImage(
            source=data.get("thumbnail") or "", allow_stretch=True, keep_ratio=True,
            size_hint=(1, 1), pos_hint={"x": 0, "y": 0},
        )
        thumb_wrap.add_widget(thumb)
        play_btn = _PlayOverlay(pos_hint={"center_x": 0.5, "center_y": 0.5})
        play_btn.bind(on_release=lambda *a: on_play and on_play(data.get("play_url")))
        thumb_wrap.add_widget(play_btn)
        self.add_widget(thumb_wrap)

        title = Label(
            text=ar(data.get("title") or ""), font_size="14sp", bold=True, color=TEXT_MAIN,
            size_hint_y=None, height=dp(20), halign="left", valign="middle",
            shorten=True, shorten_from="right", text_size=(dp(280), dp(20)),
        )
        self.add_widget(title)

        dur = data.get("duration")
        dur_txt = ""
        if isinstance(dur, (int, float)) and dur > 0:
            m, s = divmod(int(dur), 60)
            dur_txt = "{:d}:{:02d}".format(m, s)
        meta_row = BoxLayout(size_hint_y=None, height=dp(16), spacing=dp(6))
        meta_row.add_widget(Label(text=dur_txt, font_size="11sp", color=TEXT_MUTED, halign="left"))
        self.add_widget(meta_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        video_btn = NeonButton(
            text=ar("تحميل الفيديو"), color=platform_color,
            text_color=(0.05, 0.05, 0.08, 1),
            icon_widget=_DownloadArrowIcon(color=(0.05, 0.05, 0.08, 1)),
        )
        video_btn.bind(on_release=lambda *a: on_download_video and on_download_video())
        btn_row.add_widget(video_btn)
        audio_btn = NeonButton(
            text=ar("الصوت فقط"), color=CARD_DARK_2, text_color=NEON_YELLOW,
            icon_widget=_MusicNoteIcon(color=NEON_YELLOW),
        )
        audio_btn.bind(on_release=lambda *a: on_download_audio and on_download_audio())
        btn_row.add_widget(audio_btn)
        self.add_widget(btn_row)

# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
class SaveProApp(App):
    def build(self):
        self.title = "Save Pro"
        init_db()
        self.selected_platform = "instagram"
        self._chips = {}

        root = FloatLayout()
        with root.canvas.before:
            Color(*BG_DARK)
            self._bg_rect = RoundedRectangle(pos=root.pos, size=root.size)
            Color(*NEON_PINK[:3], 0.10)
            self._blob1 = Ellipse(size=(dp(260), dp(260)))
            Color(*NEON_PURPLE[:3], 0.10)
            self._blob2 = Ellipse(size=(dp(300), dp(300)))
            Color(*NEON_CYAN[:3], 0.08)
            self._blob3 = Ellipse(size=(dp(220), dp(220)))
        self._drift_started = False
        root.bind(size=self._upd_bg, pos=self._upd_bg)

        col = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(14))
        root.add_widget(col)

        # header
        header = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(12))
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            header.add_widget(KvImage(source=icon_path, size_hint=(None, None), size=(dp(52), dp(52))))
        title_box = BoxLayout(orientation="vertical", size_hint_x=None, spacing=dp(2))
        title_box.bind(minimum_width=title_box.setter("width"))
        title_lbl = Label(
            text="[b]Save Pro[/b]", markup=True, font_size="26sp",
            color=TEXT_MAIN, size_hint=(None, None), halign="left",
        )
        title_lbl.bind(texture_size=lambda i, v: setattr(title_lbl, "size", v))
        title_box.add_widget(title_lbl)
        tagline_lbl = Label(
            text=ar("نزّل من أي منصة بلمسة واحدة"),
            font_size="12sp", color=NEON_CYAN, bold=True,
            size_hint=(None, None), halign="left",
        )
        tagline_lbl.bind(texture_size=lambda i, v: setattr(tagline_lbl, "size", v))
        title_box.add_widget(tagline_lbl)
        header.add_widget(title_box)
        header.add_widget(Widget())
        col.add_widget(header)

        # accent strip
        accent = BoxLayout(size_hint_y=None, height=dp(3))
        with accent.canvas:
            Color(*NEON_PINK)
            self._a1 = RoundedRectangle(radius=[dp(2)] * 4)
            Color(*NEON_PURPLE)
            self._a2 = RoundedRectangle(radius=[dp(2)] * 4)
            Color(*NEON_CYAN)
            self._a3 = RoundedRectangle(radius=[dp(2)] * 4)
        accent.bind(pos=self._upd_accent, size=self._upd_accent)
        col.add_widget(accent)

        # platform selector card
        sel_card = GlowPanel(glow_color=NEON_PURPLE, radius=dp(20))
        sel_card.orientation = "vertical"
        sel_card.padding = [dp(12), dp(14), dp(12), dp(10)]
        sel_card.spacing = dp(8)
        sel_card.size_hint_y = None
        sel_card.height = dp(126)
        sel_title = Label(
            text=ar("اختر المنصة"), font_size="12.5sp", bold=True, color=TEXT_MUTED,
            size_hint_y=None, height=dp(18), halign="left",
        )
        sel_card.add_widget(sel_title)
        chips_row = BoxLayout(spacing=dp(6))
        for p in PLATFORMS:
            chip = PlatformChip(p, on_select=self.select_platform)
            self._chips[p["id"]] = chip
            chips_row.add_widget(chip)
        sel_card.add_widget(chips_row)
        col.add_widget(sel_card)

        # link input card
        link_card = GlowPanel(glow_color=NEON_CYAN, radius=dp(20))
        link_card.orientation = "vertical"
        link_card.padding = [dp(14), dp(16), dp(14), dp(16)]
        link_card.spacing = dp(12)
        link_card.size_hint_y = None
        link_card.height = dp(168)
        self._hint_lbl = Label(
            text=PLATFORM_BY_ID["instagram"]["hint"], font_size="12.5sp",
            color=TEXT_MUTED, size_hint_y=None, height=dp(18), halign="left",
        )
        link_card.add_widget(self._hint_lbl)
        input_row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(8))
        self.ui = NeonInput(hint_text=ar("الصق الرابط هنا..."))
        input_row.add_widget(self.ui)
        paste_btn = NeonButton(text=ar("لصق"), color=CARD_DARK_2, text_color=NEON_CYAN)
        paste_btn.size_hint_x = None
        paste_btn.width = dp(64)
        paste_btn.bind(on_release=self.do_paste)
        input_row.add_widget(paste_btn)
        link_card.add_widget(input_row)
        self.preview_btn = NeonButton(text=ar("معاينة"), color=NEON_CYAN)
        self.preview_btn.bind(on_release=self.do_preview)
        link_card.add_widget(self.preview_btn)
        col.add_widget(link_card)

        # preview card slot (filled dynamically after fetching preview)
        self.preview_container = BoxLayout(orientation="vertical", size_hint_y=None, height=0)
        col.add_widget(self.preview_container)

        # status
        self.status_lbl = Label(
            text="", font_size="13sp", color=TEXT_MUTED,
            size_hint_y=None, height=dp(24),
        )
        col.add_widget(self.status_lbl)

        # history card
        hist_card = GlowPanel(glow_color=NEON_PINK, radius=dp(20))
        hist_card.orientation = "vertical"
        hist_card.padding = [dp(14), dp(12), dp(14), dp(12)]
        hist_card.spacing = dp(6)
        hist_title = Label(
            text=ar("التنزيلات الأخيرة"), font_size="12.5sp", bold=True, color=TEXT_MUTED,
            size_hint_y=None, height=dp(18), halign="left",
        )
        hist_card.add_widget(hist_title)
        sc = ScrollView()
        self.hist_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        self.hist_list.bind(minimum_height=self.hist_list.setter("height"))
        sc.add_widget(self.hist_list)
        hist_card.add_widget(sc)
        col.add_widget(hist_card)

        self.select_platform("instagram")
        self._refresh_history()
        return root

    # -- background --
    def _upd_bg(self, i, v):
        self._bg_rect.pos = i.pos
        self._bg_rect.size = i.size
        self._blob1.pos = (i.x - dp(60), i.y + i.height * 0.72)
        self._blob2.pos = (i.x + i.width * 0.55, i.y + i.height * 0.55)
        self._blob3.pos = (i.x + i.width * 0.10, i.y - dp(50))
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
        loop(self._blob1, dp(22), -dp(16), 10)
        loop(self._blob2, -dp(18), dp(20), 12)
        loop(self._blob3, dp(14), dp(12), 9)

    def _upd_accent(self, i, v):
        third = i.width / 3
        self._a1.pos = i.pos
        self._a1.size = (third, i.height)
        self._a2.pos = (i.x + third, i.y)
        self._a2.size = (third, i.height)
        self._a3.pos = (i.x + third * 2, i.y)
        self._a3.size = (third, i.height)

    # -- platform selection --
    def select_platform(self, platform_id):
        self.selected_platform = platform_id
        for pid, chip in self._chips.items():
            chip.set_selected(pid == platform_id)
        p = PLATFORM_BY_ID[platform_id]
        self._hint_lbl.text = p["hint"]

    # -- preview flow --
    def do_preview(self, *a):
        url = self.ui.text.strip()
        if not url:
            self.status_lbl.text = ar("الصق الرابط أولاً")
            self.status_lbl.color = NEON_RED
            return
        self.status_lbl.text = ar("جارٍ تحضير المعاينة...")
        self.status_lbl.color = NEON_CYAN
        self.preview_btn.disabled = True
        threading.Thread(target=self._preview_th, args=(url,)).start()

    def _preview_th(self, url):
        data, err = fetch_preview(url)
        Clock.schedule_once(lambda dt: self._preview_done(data, err, url), 0)

    def _preview_done(self, data, err, url):
        self.preview_btn.disabled = False
        self.preview_container.clear_widgets()
        if err or not data:
            Animation(height=0, duration=0.18).start(self.preview_container)
            self.status_lbl.text = ar("تعذّرت المعاينة: ") + (err or "")
            self.status_lbl.color = NEON_RED
            return
        self.status_lbl.text = ar("هذا هو المحتوى - اختر ماذا تريد أن تحمّل")
        self.status_lbl.color = TEXT_MUTED
        platform_color = PLATFORM_BY_ID[self.selected_platform]["color"]
        card = PreviewCard(
            data, platform_color,
            on_download_video=lambda: self.do_download(url, "video"),
            on_download_audio=lambda: self.do_download(url, "audio"),
            on_play=self.open_player,
        )
        self.preview_container.add_widget(card)
        Animation(height=dp(340), duration=0.22, t="out_cubic").start(self.preview_container)

    def open_player(self, play_url):
        """Play the preview in the device's own video player/browser (no bundled
        media-decoder library needed -> keeps the APK build stable)."""
        if not play_url:
            Popup(
                title="", size_hint=(0.85, 0.22),
                content=Label(text=ar("تعذّر تشغيل المعاينة، جرّب التحميل مباشرة"), color=NEON_RED, font_size="13.5sp"),
            ).open()
            return
        try:
            from jnius import autoclass
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(Uri.parse(play_url), "video/*")
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            PythonActivity.mActivity.startActivity(intent)
            return
        except Exception:
            pass
        try:
            import webbrowser
            webbrowser.open(play_url)
        except Exception:
            Popup(
                title="", size_hint=(0.85, 0.22),
                content=Label(text=ar("تعذّر فتح المعاينة"), color=NEON_RED, font_size="13.5sp"),
            ).open()

    def do_paste(self, *a):
        try:
            txt = Clipboard.paste()
            if txt:
                self.ui.text = txt.strip()
        except Exception:
            pass

    # -- download flow (from preview card) --
    def do_download(self, url, kind):
        self.status_lbl.text = ar("جارٍ التحميل...")
        self.status_lbl.color = NEON_CYAN
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
            self.status_lbl.text = ar("فشل: ") + err
            self.status_lbl.color = NEON_RED
            return
        self.status_lbl.text = ar("تم التحميل بنجاح")
        self.status_lbl.color = NEON_GREEN
        for f in files:
            save_history(platform_id, url, f)
        self.ui.text = ""
        self.preview_container.clear_widgets()
        Animation(height=0, duration=0.2).start(self.preview_container)
        self._refresh_history()

    def _refresh_history(self):
        self.hist_list.clear_widgets()
        rows = get_history(12)
        if not rows:
            self.hist_list.add_widget(Label(
                text=ar("لا توجد تنزيلات بعد"), font_size="12.5sp", color=TEXT_FAINT,
                size_hint_y=None, height=dp(30),
            ))
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
