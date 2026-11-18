#!/bin/sh
# NavQL installer for Linux (x64).
#
#   curl -fsSL https://navql.com/install.sh | sh
#
# Installs the latest NavQL AppImage for the current user (no sudo): the app in
# ~/.local/share/navql, a `navql` command in ~/.local/bin and an entry in the applications menu.
# The AppImage updates itself afterwards. Run it again to reinstall; uninstall with
#
#   curl -fsSL https://navql.com/install.sh | sh -s -- --uninstall
#
# By installing NavQL you agree to its Terms of Use (https://navql.com/terms.html) and
# Privacy Policy (https://navql.com/privacy.html).
set -eu

APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/navql"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"
APPIMAGE="$APP_DIR/NavQL.AppImage"
API="https://api.github.com/repos/navql/releases/releases/latest"

say() { printf '%s\n' "$*"; }
fail() { printf 'navql: %s\n' "$*" >&2; exit 1; }

fetch() { # fetch URL [FILE]: prints to stdout, or saves to FILE
  if command -v curl >/dev/null 2>&1; then
    if [ $# -gt 1 ]; then curl -fL --progress-bar -o "$2" "$1"; else curl -fsSL "$1"; fi
  elif command -v wget >/dev/null 2>&1; then
    if [ $# -gt 1 ]; then wget -q --show-progress -O "$2" "$1"; else wget -qO- "$1"; fi
  else
    fail "curl or wget is needed"
  fi
}

uninstall() {
  rm -f "$APPIMAGE" "$BIN_DIR/navql" "$DESKTOP_DIR/navql.desktop" "$ICON_DIR/navql.svg"
  rmdir "$APP_DIR" 2>/dev/null || true
  command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
  say "NavQL uninstalled. Your connections and settings are still in ~/.config/NavQL (delete that folder to remove them)."
}

case "${1:-}" in
  --uninstall) uninstall; exit 0 ;;
  "") ;;
  *) fail "unknown option: $1 (the only option is --uninstall)" ;;
esac

case "$(uname -s)" in
  Linux) ;;
  Darwin) fail "this script is for Linux. On macOS: brew install --cask navql/tap/navql (or download from https://navql.com)" ;;
  *) fail "this script is for Linux. Downloads for other systems: https://navql.com" ;;
esac
case "$(uname -m)" in
  x86_64 | amd64) ;;
  *) fail "NavQL for Linux is x64 only for now ($(uname -m) is not supported yet)" ;;
esac

say "Finding the latest NavQL…"
url=$(fetch "$API" | grep -o '"browser_download_url": *"[^"]*x86_64\.AppImage"' | head -n 1 | sed 's/.*"\(https:[^"]*\)"/\1/')
[ -n "$url" ] || fail "could not find the AppImage in the latest release (https://github.com/navql/releases/releases)"
version=$(printf '%s' "$url" | sed 's/.*NavQL-\(.*\)-x86_64\.AppImage/\1/')

mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR"
tmp="$APPIMAGE.download"
trap 'rm -f "$tmp"' EXIT
say "Downloading NavQL $version…"
fetch "$url" "$tmp"
chmod 755 "$tmp"
mv -f "$tmp" "$APPIMAGE"
ln -sf "$APPIMAGE" "$BIN_DIR/navql"

fetch "https://navql.com/assets/navql-icone.svg" "$ICON_DIR/navql.svg" 2>/dev/null || true
cat > "$DESKTOP_DIR/navql.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=NavQL
Comment=Database client for PostgreSQL, MySQL, SQL Server, MongoDB, Redis and SQLite
Exec="$APPIMAGE" %U
Icon=navql
Terminal=false
Categories=Development;Database;
StartupWMClass=NavQL
EOF
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

say ""
say "NavQL $version is installed: open it from the applications menu, or run: navql"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) say "(Add $BIN_DIR to your PATH to use the navql command.)" ;;
esac
# AppImages need FUSE 2; Ubuntu 22.04 and later do not install it by default.
if ! { ldconfig -p 2>/dev/null | grep -q 'libfuse\.so\.2'; } && ! [ -e /usr/lib/x86_64-linux-gnu/libfuse.so.2 ] && ! [ -e /lib/x86_64-linux-gnu/libfuse.so.2 ]; then
  say ""
  say "NavQL needs FUSE 2, which this system does not seem to have. Install it with:"
  if [ -r /etc/os-release ] && grep -q 'VERSION_ID="2[4-9]' /etc/os-release && grep -qi ubuntu /etc/os-release; then
    say "  sudo apt install libfuse2t64"
  elif command -v apt-get >/dev/null 2>&1; then
    say "  sudo apt install libfuse2"
  elif command -v dnf >/dev/null 2>&1; then
    say "  sudo dnf install fuse-libs"
  elif command -v pacman >/dev/null 2>&1; then
    say "  sudo pacman -S fuse2"
  else
    say "  (the package is usually called libfuse2 or fuse2)"
  fi
fi
say ""
say "By installing NavQL you agree to its Terms of Use (https://navql.com/terms.html) and Privacy Policy (https://navql.com/privacy.html)."
