#!/usr/bin/env python3
"""Fullscreen black screensaver with a large white spelled-out time."""
from __future__ import annotations

import os
import signal
import sys

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk, Pango

PIDFILE = os.path.expanduser("~/.cache/spelltime-screensaver.pid")

NUM_WORDS = {
    0: "twelve",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
    21: "twenty one",
    22: "twenty two",
    23: "twenty three",
    24: "twenty four",
    25: "twenty five",
    26: "twenty six",
    27: "twenty seven",
    28: "twenty eight",
    29: "twenty nine",
    30: "thirty",
    31: "thirty one",
    32: "thirty two",
    33: "thirty three",
    34: "thirty four",
    35: "thirty five",
    36: "thirty six",
    37: "thirty seven",
    38: "thirty eight",
    39: "thirty nine",
    40: "forty",
    41: "forty one",
    42: "forty two",
    43: "forty three",
    44: "forty four",
    45: "forty five",
    46: "forty six",
    47: "forty seven",
    48: "forty eight",
    49: "forty nine",
    50: "fifty",
    51: "fifty one",
    52: "fifty two",
    53: "fifty three",
    54: "fifty four",
    55: "fifty five",
    56: "fifty six",
    57: "fifty seven",
    58: "fifty eight",
    59: "fifty nine",
}


def hour_word(hour_24: int) -> int:
    hour = hour_24 % 12
    return 12 if hour == 0 else hour


def spell_minute(minute: int) -> str:
    if minute == 0:
        return "o'clock"
    if minute == 15:
        return "quarter past"
    if minute == 30:
        return "half past"
    if minute == 45:
        return "quarter to"
    if minute < 30:
        return f"{NUM_WORDS[minute]} past"
    return f"{NUM_WORDS[60 - minute]} to"


def spell_time(hour_24: int, minute: int) -> str:
    hour = hour_word(hour_24)
    minute_phrase = spell_minute(minute)
    if minute == 0:
        return f"{NUM_WORDS[hour]} o'clock"
    if minute <= 30:
        return f"{minute_phrase} {NUM_WORDS[hour]}"
    next_hour = 1 if hour == 12 else hour + 1
    return f"{minute_phrase} {NUM_WORDS[next_hour]}"


def claim_pidfile() -> None:
    if os.path.exists(PIDFILE):
        try:
            with open(PIDFILE, encoding="utf-8") as handle:
                old_pid = int(handle.read().strip())
            os.kill(old_pid, signal.SIGTERM)
        except (ProcessLookupError, ValueError, OSError):
            pass
    os.makedirs(os.path.dirname(PIDFILE), exist_ok=True)
    with open(PIDFILE, "w", encoding="utf-8") as handle:
        handle.write(str(os.getpid()))


def release_pidfile() -> None:
    try:
        os.remove(PIDFILE)
    except FileNotFoundError:
        pass


class WordClockScreensaver(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(Gtk.WindowType.TOPLEVEL)
        self.set_title("Word Clock Screensaver")
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)
        self.set_accept_focus(True)
        self.set_can_focus(True)
        try:
            self.set_type_hint(Gdk.WindowTypeHint.SCREENSAVER)
        except Exception:
            pass
        self.fullscreen()
        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.KEY_PRESS_MASK
            | Gdk.EventMask.SCROLL_MASK
        )
        self.connect("motion-notify-event", self.on_user_activity)
        self.connect("button-press-event", self.on_user_activity)
        self.connect("key-press-event", self.on_user_activity)
        self.connect("scroll-event", self.on_user_activity)
        self.connect("realize", self.on_realize)
        self.connect("destroy", self.on_destroy)

        css = Gtk.CssProvider()
        css.load_from_data(
            b"""
            window { background-color: #000000; }
            label#clock {
                color: #ffffff;
                font-size: 96px;
                font-weight: bold;
                font-family: Sans;
            }
            """
        )
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.label = Gtk.Label(label="")
        self.label.set_name("clock")
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_line_wrap(True)
        self.label.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.label.set_max_width_chars(24)
        self.label.set_halign(Gtk.Align.CENTER)
        self.label.set_valign(Gtk.Align.CENTER)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)
        box.pack_start(self.label, True, True, 0)
        self.add(box)
        self.show_all()
        self.update_time()
        GLib.timeout_add_seconds(1, self.update_time)

    def on_realize(self, _widget) -> None:
        window = self.get_window()
        if window is not None:
            window.set_events(
                window.get_events()
                | Gdk.EventMask.POINTER_MOTION_MASK
                | Gdk.EventMask.BUTTON_PRESS_MASK
                | Gdk.EventMask.KEY_PRESS_MASK
                | Gdk.EventMask.SCROLL_MASK
            )
            try:
                cursor = Gdk.Cursor.new_for_display(
                    self.get_display(), Gdk.CursorType.BLANK_CURSOR
                )
                window.set_cursor(cursor)
            except Exception:
                pass
        self.grab_focus()

    def on_destroy(self, _widget) -> None:
        release_pidfile()

    def on_user_activity(self, _widget, _event) -> bool:
        self.dismiss()
        return True

    def dismiss(self) -> None:
        release_pidfile()
        Gtk.main_quit()

    def update_time(self) -> bool:
        now = GLib.DateTime.new_now_local()
        self.label.set_text(spell_time(now.get_hour(), now.get_minute()))
        return True


class WordClockGadget(Gtk.Window):
    """Desktop desklet / panel chip — spelled time, no frame."""

    def __init__(self, panel: bool = False) -> None:
        super().__init__(Gtk.WindowType.TOPLEVEL)
        self.set_title("Spelltime")
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        try:
            self.stick()
        except Exception:
            pass
        screen = self.get_screen()
        visual = screen.get_rgba_visual() if screen is not None else None
        if visual is not None:
            self.set_visual(visual)

        size = "22px" if panel else "42px"
        css = Gtk.CssProvider()
        css.load_from_data(
            f"""
            window {{ background-color: transparent; }}
            label#clock {{
                color: #ffffff;
                font-size: {size};
                font-weight: bold;
                font-family: Sans;
            }}
            """.encode()
        )
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.label = Gtk.Label(label="")
        self.label.set_name("clock")
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_line_wrap(True)
        pad = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        pad.set_margin_top(8)
        pad.set_margin_bottom(8)
        pad.set_margin_start(12)
        pad.set_margin_end(12)
        pad.pack_start(self.label, True, True, 0)
        self.add(pad)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_press)
        self.update_time()
        GLib.timeout_add_seconds(1, self.update_time)
        self.show_all()

    def on_press(self, _w, event) -> bool:
        if event.button == 1:
            try:
                self.begin_move_drag(
                    int(event.button), int(event.x_root), int(event.y_root), int(event.time)
                )
            except Exception:
                pass
            return True
        if event.button == 3:
            menu = Gtk.Menu()
            quit_it = Gtk.MenuItem(label="Quit")
            quit_it.connect("activate", lambda *_: Gtk.main_quit())
            menu.append(quit_it)
            menu.show_all()
            menu.popup_at_pointer(event)
            return True
        return False

    def update_time(self) -> bool:
        now = GLib.DateTime.new_now_local()
        self.label.set_text(spell_time(now.get_hour(), now.get_minute()))
        return True


def main() -> int:
    gadget = "--desklet" in sys.argv or "--panel" in sys.argv
    if gadget:
        WordClockGadget(panel="--panel" in sys.argv)
        Gtk.main()
        return 0

    claim_pidfile()

    def handle_signal(_signum, _frame) -> None:
        release_pidfile()
        Gtk.main_quit()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    WordClockScreensaver()
    Gtk.main()
    release_pidfile()
    return 0


if __name__ == "__main__":
    sys.exit(main())
