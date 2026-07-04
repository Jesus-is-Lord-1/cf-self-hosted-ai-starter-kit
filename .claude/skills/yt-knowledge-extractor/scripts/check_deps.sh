#!/usr/bin/env bash
# Dependency check for yt-knowledge-extractor
missing=0
for cmd in yt-dlp ffmpeg curl python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "MISSING: $cmd"
    missing=1
  else
    echo "OK: $cmd ($($cmd --version 2>/dev/null | head -1))"
  fi
done
if [ $missing -eq 1 ]; then
  echo ""
  echo "Install:"
  echo "  sudo apt update && sudo apt install -y ffmpeg curl python3-pip"
  echo "  pip install yt-dlp --break-system-packages"
  exit 1
fi
echo "All dependencies present."
