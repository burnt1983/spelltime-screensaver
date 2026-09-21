# Spelltime

<p align="center"><img src="https://repository-images.githubusercontent.com/1380060176/ccf4129f-1cea-4c9c-b7d8-89b03b7b197a" alt="Spelltime" width="640"></p>

A fullscreen **white-on-black word clock screensaver** for Linux.

After a few minutes idle, the screen goes black and the time is spelled out in
large white type:

**quarter past three** · **half past seven** · **ten to twelve**

Move the mouse or press a key and it disappears.

![Spelltime preview](data/preview.svg)

## Install

Needs Python 3, GTK 3, and PyGObject (`python3-gi`, `gir1.2-gtk-3.0` on Debian/Ubuntu).

```bash
git clone https://github.com/burnt1983/spelltime-screensaver.git
cd spelltime-screensaver
./install.sh
```

That puts `spelltime` on your PATH, adds a login autostart, and (if systemd
user units work) enables `spelltime-idle.service`.

Preview it now:

```bash
spelltime
```

Idle delay is **5 minutes**. Change it before starting the watcher:

```bash
SPELLTIME_IDLE_MS=180000 spelltime-idle   # 3 minutes
```

## Desklet / panel (any Linux)

| Command | What you get |
|---|---|
| `spelltime` | Fullscreen screensaver (white on black) |
| `spelltime --desklet` | Frameless word clock on the desktop |
| `spelltime --panel` | Compact chip by the panel |

Works on GNOME, Cinnamon, MATE, XFCE, Budgie, LXQt, and KDE. Cinnamon: Settings → Desklets → Spelltime, or Applets for the panel chip.

## Screensaver idle watcher

| Desktop | Idle watcher |
|---|---|
| GNOME (Mutter) | IdleMonitor, no polling |
| Cinnamon / others | logind IdleHint, or `xprintidle` if installed |

## Uninstall

```bash
./uninstall.sh
```

## Licence

MIT. See [LICENSE](LICENSE).
