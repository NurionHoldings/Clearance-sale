# Dapanda entrance video

- Original footage: **High Angle View of a Crowded Shopping Mall**, George Morina / Pexels, video 15007111.
- Source: https://www.pexels.com/video/high-angle-view-of-a-crowded-shopping-mall-15007111/
- Original download: https://videos.pexels.com/video-files/15007111/15007111-uhd_3840_2160_31fps.mp4
- License: https://www.pexels.com/license/ (checked 2026-10-28). Website/marketing use and modification permitted; no implied endorsement. Footage is a separate scene, not part of the brand mark itself.
- Used source segment: 00:02–00:07, audio removed, resized to 1280×720 / 24 fps.
- The location is a crowded indoor shopping mall; no claim is made that it is a specific department store or operated by Dapanda.
- Logo: user-approved Dapanda artwork, `../dapanda-logo-premium.png`.
- Output: `dapanda-entry.mp4`, 11.2 seconds, H.264/yuv420p, silent, faststart.
- Timeline: crowd 0–3.2s, dissolve 3.2–5s, transparent energy-logo on dark navy 5–11.2s.
- Render: `bash scripts/render-dapanda-entry.sh /path/to/source.mp4` (FFmpeg required).

## Motion reference and alpha assets
- User-supplied reference: ARKAON_Energy_Flow_V12(1).mp4, 8s / 960×640 / 15fps. Reviewed at multiple timestamps.
- Recreated visual families: blue/gold orbital tracers and tails; curved energy currents; satellite sparkles; starburst flares; alpha-masked surface glints; scanning arc inside symbol; subtle scale/breathing.
- The animation is reimplemented for Dapanda, not an extraction of editable motion data, and contains no ARKAON image or footage pixels.
- Approved logo background removed with image generation; original retained. `dapanda-logo-transparent.png` includes real alpha outside the full logo, keeping the iridescent emblem tile intact.
- Compositing layer: `dapanda-energy-alpha.webm` (VP9 alpha, 8s / 24fps). Decode with libvpx-vp9 when compositing in FFmpeg. MP4 is an opaque final film; use PNG/WebM for transparency.
- Render alpha: `node scripts/render-dapanda-energy.cjs` before rendering the entrance MP4.

## Mobile playback derivatives
- `dapanda-entry-mobile.mp4`: same film, 640×360 / 24fps, H.264 Constrained Baseline level 3.0, yuv420p, silent, faststart.
- `dapanda-entry-poster.jpg`: first frame from the licensed shopping scene.
- `dapanda-entry-mobile.webm`: VP9 alternative of the same 640×360 film for browsers without H.264 support.
