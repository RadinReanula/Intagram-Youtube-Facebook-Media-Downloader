#!/bin/sh
# Install the API on Debian without Docker.
# Run as root from a checkout of this repository:
#   sudo sh deploy/install.sh

set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
APP_USER=media-downloader
PREFIX=/opt/media-downloader
STATE=/var/lib/media-downloader

apt-get update
apt-get install -y python3 python3-venv python3-pip ffmpeg

if ! id "$APP_USER" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir "$STATE" --shell /usr/sbin/nologin "$APP_USER"
fi

install -d -o "$APP_USER" -g "$APP_USER" -m 750 "$STATE" "$STATE/tmp" "$PREFIX"
rm -rf "$PREFIX/api"
cp -a "$ROOT/api" "$PREFIX/api"
chown -R "$APP_USER:$APP_USER" "$PREFIX/api"

if [ ! -x "$PREFIX/.venv/bin/python" ]; then
  python3 -m venv "$PREFIX/.venv"
fi
"$PREFIX/.venv/bin/pip" install --upgrade pip
"$PREFIX/.venv/bin/pip" install -r "$PREFIX/api/requirements.txt"
"$PREFIX/.venv/bin/pip" install --upgrade yt-dlp
chown -R "$APP_USER:$APP_USER" "$PREFIX/.venv"

if [ ! -f /etc/media-downloader.env ]; then
  sed \
    -e "s|^YTDLP_PATH=.*|YTDLP_PATH=$PREFIX/.venv/bin/yt-dlp|" \
    -e "s|^FFMPEG_PATH=.*|FFMPEG_PATH=/usr/bin/ffmpeg|" \
    -e "s|^TEMP_DIR=.*|TEMP_DIR=$STATE/tmp|" \
    -e "s|^DATABASE_PATH=.*|DATABASE_PATH=$STATE/jobs.sqlite|" \
    "$ROOT/api/.env.example" > /etc/media-downloader.env
  chmod 640 /etc/media-downloader.env
  chown root:"$APP_USER" /etc/media-downloader.env
  echo "Edit /etc/media-downloader.env before exposing the API. Set ADMIN_TOKEN, DOWNLOAD_SIGNING_SECRET and CORS_ORIGINS. Leave ENABLE_INSTAGRAM_LOGIN off unless the site and API share a parent domain."
fi

install -m 644 "$ROOT/deploy/media-downloader.service" /etc/systemd/system/media-downloader.service
install -m 644 "$ROOT/deploy/ytdlp-update.service" /etc/systemd/system/ytdlp-update.service
install -m 644 "$ROOT/deploy/ytdlp-update.timer" /etc/systemd/system/ytdlp-update.timer
systemctl daemon-reload
systemctl enable --now media-downloader.service
systemctl enable --now ytdlp-update.timer
systemctl --no-pager --full status media-downloader.service || true
