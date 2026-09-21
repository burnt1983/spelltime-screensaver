# Spelltime

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

## What it runs on

| Desktop | Idle watcher |
|---|---|
| GNOME (Mutter) | IdleMonitor, no polling |
| Cinnamon / others | logind IdleHint, or `xprintidle` if installed |

This is a GTK 3 fullscreen window, so it also works as a **desklet-style gadget
on Cinnamon** if you launch `spelltime` yourself. It is not a Cinnamon spice
yet (those are GJS packages in the Linux Mint spices store).

## Uninstall

```bash
./uninstall.sh
```

## Licence

MIT. See [LICENSE](LICENSE).
