#!/usr/bin/env bash
set -euo pipefail
# Requires the alpha energy layer rendered by render-dapanda-energy.cjs.
# Usage: bash scripts/render-dapanda-entry.sh /path/to/15007111-source.mp4
cd "$(dirname "$0")/.."
ffmpeg -hide_banner -loglevel warning -y \
  -f lavfi -i 'color=c=0x07111e:s=1280x720:r=24:d=11.2' \
  -ss 2 -t 5 -i "$1" \
  -c:v libvpx-vp9 -i assets/video/dapanda-energy-alpha.webm \
  -filter_complex "
    [1:v]fps=24,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,format=rgba,
      fade=t=out:st=3.2:d=1.8:alpha=1[mall];
    [0:v][mall]overlay=eof_action=pass[scene];
    [2:v]setpts=PTS-STARTPTS+3.2/TB[energy];
    [scene][energy]overlay=eof_action=pass:format=auto,format=yuv420p[out]" \
  -map '[out]' -an -t 11.2 -r 24 -c:v libx264 -preset medium -crf 22 -movflags +faststart assets/video/dapanda-entry.mp4
