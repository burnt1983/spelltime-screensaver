#!/usr/bin/env python3
"""Start the word-clock screensaver after a few minutes idle.

On GNOME, uses Mutter IdleMonitor watches (no polling). While the clock is up,
idle/lock is inhibited so the lock screen does not cover it.

On other desktops (Cinnamon, etc.) it falls back to logind IdleHint, then
to a simple idle timer.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib

HERE = Path(__file__).resolve().parent
SPELLTIME = HERE / "spelltime.py"
IDLE_MS = int(os.environ.get("SPELLTIME_IDLE_MS", str(5 * 60 * 1000)))
BUS_NAME = "org.gnome.Mutter.IdleMonitor"
BUS_PATH = "/org/gnome/Mutter/IdleMonitor/Core"
BUS_IFACE = "org.gnome.Mutter.IdleMonitor"
APP_ID = "uk.lee.spelltime"


class IdleActivate:
    def __init__(self) -> None:
        self.proxy: Gio.DBusProxy | None = None
        self.idle_watch = 0
        self.proc: subprocess.Popen | None = None
        self._connecting = False
        self._fallback = False
        self._connect()

    def _connect(self) -> bool:
        if self._connecting:
            return True
        self._connecting = True
        try:
            conn = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            self.proxy = Gio.DBusProxy.new_sync(
                conn,
                Gio.DBusProxyFlags.NONE,
                None,
                BUS_NAME,
                BUS_PATH,
                BUS_IFACE,
                None,
            )
            self.proxy.connect("g-signal", self._on_signal)
            self._arm_idle()
        except Exception:
            self.proxy = None
            self._start_fallback()
        finally:
            self._connecting = False
        return False

    def _start_fallback(self) -> None:
        if self._fallback:
            return
        self._fallback = True
        GLib.timeout_add_seconds(15, self._poll_idle)

    def _poll_idle(self) -> bool:
        if self.proc is not None and self.proc.poll() is None:
            return True
        idle_ms = _idle_milliseconds()
        if idle_ms is not None and idle_ms >= IDLE_MS:
            self._start_saver()
        return True

    def _call(self, method: str, signature: str, *args):
        if self.proxy is None:
            return None
        return self.proxy.call_sync(
            method,
            GLib.Variant(f"({signature})", args) if signature else None,
            Gio.DBusCallFlags.NONE,
            4000,
            None,
        )

    def _arm_idle(self) -> None:
        if self.idle_watch:
            try:
                self._call("RemoveWatch", "u", self.idle_watch)
            except Exception:
                pass
            self.idle_watch = 0
        result = self._call("AddIdleWatch", "t", IDLE_MS)
        if result is not None:
            self.idle_watch = int(result.unpack()[0])
        else:
            self._start_fallback()

    def _on_signal(self, _proxy, _sender, signal: str, params: GLib.Variant) -> None:
        if signal != "WatchFired":
            return
        watch_id = int(params.unpack()[0])
        if watch_id != self.idle_watch:
            return
        self.idle_watch = 0
        self._start_saver()

    def _start_saver(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            return
        if not SPELLTIME.is_file():
            self._arm_idle()
            return
        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        if os.environ.get("WAYLAND_DISPLAY"):
            env["WAYLAND_DISPLAY"] = os.environ["WAYLAND_DISPLAY"]
        cmd = [sys.executable, str(SPELLTIME)]
        inhibit = _which("gnome-session-inhibit")
        if inhibit:
            cmd = [
                inhibit,
                "--app-id",
                APP_ID,
                "--reason",
                "Word clock screensaver",
                "--inhibit",
                "idle",
                *cmd,
            ]
        self.proc = subprocess.Popen(cmd, env=env, start_new_session=True)
        GLib.child_watch_add(self.proc.pid, self._on_saver_exit)

    def _on_saver_exit(self, _pid: int, _status: int) -> None:
        self.proc = None
        if not self._fallback:
            self._arm_idle()


def _which(name: str) -> str | None:
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        path = Path(folder) / name
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def _idle_milliseconds() -> int | None:
    """Best-effort idle time for Cinnamon and other non-Mutter desktops."""
    xprintidle = _which("xprintidle")
    if xprintidle:
        try:
            out = subprocess.check_output([xprintidle], text=True, timeout=2)
            return int(out.strip())
        except (subprocess.SubprocessError, ValueError):
            pass
    try:
        conn = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        login = Gio.DBusProxy.new_sync(
            conn,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.freedesktop.login1",
            "/org/freedesktop/login1",
            "org.freedesktop.login1.Manager",
            None,
        )
        uid = os.getuid()
        result = login.call_sync(
            "GetUser",
            GLib.Variant("(u)", (uid,)),
            Gio.DBusCallFlags.NONE,
            2000,
            None,
        )
        user_path = result.unpack()[0]
        user = Gio.DBusProxy.new_sync(
            conn,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.freedesktop.login1",
            user_path,
            "org.freedesktop.login1.User",
            None,
        )
        idle = user.get_cached_property("IdleHint")
        if idle is not None and bool(idle.unpack()):
            since = user.get_cached_property("IdleSinceHint")
            if since is not None:
                # IdleSinceHint is microseconds since epoch (CLOCK_MONOTONIC_RAW
                # on some systems). Treat any idle hint as "long enough".
                return IDLE_MS
        return 0
    except Exception:
        return None


def main() -> int:
    GLib.set_prgname("spelltime-idle")
    IdleActivate()
    GLib.MainLoop().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
