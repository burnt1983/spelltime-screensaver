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

if [ -d "$ROOT/cinnamon" ]; then
  mkdir -p "${HOME}/.local/share/cinnamon/desklets" "${HOME}/.local/share/cinnamon/applets"
  cp -a "$ROOT/cinnamon/desklets/." "${HOME}/.local/share/cinnamon/desklets/"
  cp -a "$ROOT/cinnamon/applets/." "${HOME}/.local/share/cinnamon/applets/"
fi
cat > "$APPS/spelltime-desklet.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Spelltime Desklet
Comment=Spelled-out word clock on the desktop
Exec=${BIN}/spelltime --desklet
Icon=preferences-system-time
Terminal=false
Categories=Utility;Clock;
EOF
chmod 0755 "$APPS/spelltime-desklet.desktop"

echo "Installed Spelltime."
echo "  Screensaver:  spelltime            (idle watcher: spelltime-idle)"
echo "  Desklet:      spelltime --desklet  (transparent word clock)"
echo "  Panel chip:   spelltime --panel"
echo "Idle delay 5 minutes (SPELLTIME_IDLE_MS). Cinnamon: Desklets → Spelltime."
