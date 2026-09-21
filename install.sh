#!/usr/bin/env bash
# Install Spelltime for the current user (no root needed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BIN="${HOME}/.local/bin"
SHARE="${HOME}/.local/share/spelltime"
APPS="${HOME}/.local/share/applications"
AUTO="${HOME}/.config/autostart"
UNIT="${HOME}/.config/systemd/user"

mkdir -p "$BIN" "$SHARE" "$APPS" "$AUTO" "$UNIT"
install -m 0755 "$ROOT/spelltime.py" "$SHARE/spelltime.py"
install -m 0755 "$ROOT/idle-activate.py" "$SHARE/idle-activate.py"
ln -sfn "$SHARE/spelltime.py" "$BIN/spelltime"
ln -sfn "$SHARE/idle-activate.py" "$BIN/spelltime-idle"

sed "s|^Exec=spelltime$|Exec=${BIN}/spelltime|" \
    "$ROOT/data/spelltime.desktop" > "$APPS/spelltime.desktop"
sed "s|^Exec=spelltime-idle$|Exec=${BIN}/spelltime-idle|" \
    "$ROOT/data/spelltime-idle.desktop" > "$AUTO/spelltime-idle.desktop"
chmod 0755 "$APPS/spelltime.desktop" "$AUTO/spelltime-idle.desktop"

install -m 0644 "$ROOT/data/spelltime-idle.service" "$UNIT/spelltime-idle.service"
if command -v systemctl >/dev/null 2>&1; then
  systemctl --user daemon-reload
  systemctl --user enable --now spelltime-idle.service >/dev/null 2>&1 || true
fi

echo "Installed Spelltime."
echo "  Preview now:     spelltime"
echo "  Idle watcher:    spelltime-idle  (enabled at login)"
echo "  Idle delay:      5 minutes (set SPELLTIME_IDLE_MS, e.g. 180000 for 3 min)"
echo "Move the mouse or press a key to dismiss the clock."
