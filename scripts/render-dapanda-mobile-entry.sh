#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Reframe the existing film: full-screen crowd, then an uncropped logo over
# the original navy backdrop. No new imagery is introduced.
ffmpeg -hide_banner -loglevel warning -y -i assets/video/dapanda-entry.mp4 \
  -f lavfi -i 'color=c=0x07111e:s=720x1280:r=24:d=11.208333' \
  -filter_complex '
    [0:v]fps=24,split=2[crowd][logo];
    [crowd]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuva420p,fade=t=out:st=3.2:d=1.8:alpha=1[full];
    [logo]scale=540:-2,format=yuva420p,fade=t=in:st=3.2:d=1.8:alpha=1[brand];
    [1:v][full]overlay=0:0:shortest=1[scene];
    [scene][brand]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[out]' \
  -map '[out]' -an -c:v libx264 -preset medium -crf 23 -movflags +faststart \
  assets/video/dapanda-entry-portrait.mp4
ffmpeg -hide_banner -loglevel warning -y -i assets/video/dapanda-entry-portrait.mp4 \
  -an -c:v libvpx-vp9 -b:v 0 -crf 33 -row-mt 1 \
  assets/video/dapanda-entry-portrait.webm
