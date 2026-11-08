#!/bin/zsh
# Build "Netflix History.app" (and a zip to share) into dist/.
# Needs uv and Node. Run from anywhere: ./desktop/build-mac.sh
set -euo pipefail
cd "${0:A:h}/.."

[[ -d web/node_modules ]] || npm --prefix web install
npm --prefix web run build

uv run --directory api --group desktop --group build pyinstaller \
  --noconfirm --clean --windowed \
  --name "Netflix History" \
  --icon ../desktop/AppIcon.icns \
  --osx-bundle-identifier io.github.ajd1776.netflixhistory \
  --add-data ../web/dist:web \
  --collect-submodules uvicorn \
  --distpath ../dist --workpath ../build --specpath ../build \
  ../desktop/launch.py

ditto -c -k --keepParent "dist/Netflix History.app" "dist/Netflix-History-mac.zip"
echo "\nBuilt: dist/Netflix History.app  (shareable: dist/Netflix-History-mac.zip)"
