// Logo-only alpha loop; no crowd footage or opaque background plate.
const video = document.querySelector('#headerLogoVideo');
const brand = video.closest('.brand');
const toggle = document.querySelector('#headerLogoToggle');
const intro = document.querySelector('#dapandaEntry');
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
let pausedByUser = false;
let failed = false;
function showStill() { brand.classList.remove('motion-ready'); }
function sync() {
  const disabled = reduced.matches || failed;
  toggle.hidden = disabled;
  if (disabled || pausedByUser || document.hidden || intro.open) {
    video.pause();
    if (disabled) showStill();
    return;
  }
  if (!video.canPlayType('video/webm; codecs="vp9"')) {
    failed = true; toggle.hidden = true; showStill(); return;
  }
  if (!video.getAttribute('src')) video.src = video.dataset.src;
  video.muted = true;
  const attempt = video.play();
  if (attempt) attempt.catch(() => { failed = true; toggle.hidden = true; showStill(); });
}
video.addEventListener('playing', () => { if (!reduced.matches && !failed) brand.classList.add('motion-ready'); });
video.addEventListener('error', () => { failed = true; sync(); });
toggle.addEventListener('click', () => {
  pausedByUser = !pausedByUser;
  toggle.textContent = pausedByUser ? '로고 재생' : '로고 정지';
  toggle.setAttribute('aria-label', pausedByUser ? '로고 애니메이션 재생' : '로고 애니메이션 일시정지');
  toggle.setAttribute('aria-pressed', String(pausedByUser));
  sync();
});
reduced.addEventListener('change', sync);
document.addEventListener('visibilitychange', sync);
new MutationObserver(sync).observe(intro, { attributes: true, attributeFilter: ['open'] });
sync();
