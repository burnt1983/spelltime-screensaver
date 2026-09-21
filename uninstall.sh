#!/usr/bin/env bash
set -euo pipefail
systemctl --user disable --now spelltime-idle.service >/dev/null 2>&1 || true
rm -f \
  "${HOME}/.local/bin/spelltime" \
  "${HOME}/.local/bin/spelltime-idle" \
  "${HOME}/.local/share/applications/spelltime.desktop" \
  "${HOME}/.config/autostart/spelltime-idle.desktop" \
  "${HOME}/.config/systemd/user/spelltime-idle.service"
rm -rf "${HOME}/.local/share/spelltime"
echo "Removed Spelltime."
