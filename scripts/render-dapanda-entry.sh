#!/usr/bin/env bash
set -euo pipefail
# Usage: bash scripts/render-dapanda-entry.sh /path/to/15007111-source.mp4
# Source and license are documented in assets/video/CREDITS.md.
cd "$(dirname "$0")/.."
ffmpeg -hide_banner -loglevel warning -y \
  -ss 2 -t 5 -i "$1" \
  -loop 1 -framerate 30 -i assets/dapanda-logo-premium.png \
  -filter_complex "
    [0:v]fps=30,scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,trim=duration=5,setpts=PTS-STARTPTS[mall];
    [1:v]scale=1120:560,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0xfaf8f2,setsar=1,
      zoompan=z='1.055-0.055*min(on/150,1)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1280x720:fps=30,
      rotate='0.012*sin(t*1.8)*exp(-t/1.5)':fillcolor=0xfaf8f2,
      trim=duration=6.5,setpts=PTS-STARTPTS[logo];
    [mall][logo]xfade=transition=fade:duration=1.8:offset=3.2[scene];
    color=c=white@0.0:s=120x330:r=30:d=9.7,format=rgba,
      drawbox=x=40:y=0:w=28:h=330:color=white@0.26:t=fill,
      gblur=sigma=12,rotate=-0.25:fillcolor=black@0[shine];
    [scene][shine]overlay=x='160+(t-5.5)*240':y=185:enable='between(t,5.5,6.5)':shortest=1,
      format=yuv420p[out]" \
  -map '[out]' -an -t 9.7 -c:v libx264 -preset medium -crf 23 -movflags +faststart assets/video/dapanda-entry.mp4
