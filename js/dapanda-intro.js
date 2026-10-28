// Silent inline film, with an explicit user-gesture path for mobile autoplay policies.
const dialog = document.querySelector('#dapandaEntry');
const video = dialog.querySelector('video');
const logo = dialog.querySelector('img');
const closeButton = dialog.querySelector('#introSkip');
const playButton = dialog.querySelector('#introPlay');
const replay = document.querySelector('#replayDapandaIntro');
const status = dialog.querySelector('[role="status"]');
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const smallScreen = matchMedia('(max-width: 767px)');
const boot = globalThis.dapandaEntryBoot;
const sessionKey = boot?.sessionKey || 'dapanda-intro-seen-v4';
let timers = [];
let previousFocus;
let fallingBack = false;
let playAttempt = 0;
const later = (fn, delay) => { const id = setTimeout(fn, delay); timers.push(id); return id; };
function clearTimers() { timers.forEach(clearTimeout); timers = []; }
function markSeen() { try { sessionStorage.setItem(sessionKey, '1'); } catch {} }
function closeIntro() {
  playAttempt++;
  boot?.release();
  clearTimers();
  video.pause();
  dialog.classList.remove('playing', 'cinema-playing', 'manual-play');
  if (dialog.open) dialog.close();
  if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
}
function fallbackLogo(gestureRequired = false) {
  if (!dialog.open || fallingBack) return;
  fallingBack = true;
  clearTimers();
  video.pause();
  dialog.classList.remove('cinema-playing');
  playButton.hidden = false;
  status.textContent = gestureRequired ? '영상 재생을 눌러 진입영상을 시작해 주세요.' : '영상을 다시 재생하거나 다판다로 바로 이동할 수 있습니다.';
  // Autoplay denial is not a missing video: keep a visible, tappable retry.
  if (!reduced.matches && !gestureRequired) {
    dialog.classList.add('playing');
    later(closeIntro, 5800);
  }
}
function startVideo(manual = false) {
  if (!dialog.open) return;
  clearTimers();
  fallingBack = false;
  const attemptId = ++playAttempt;
  dialog.classList.remove('playing');
  dialog.classList.toggle('manual-play', manual);
  dialog.classList.add('cinema-playing');
  playButton.hidden = true;
  status.textContent = '진입영상을 불러오는 중입니다.';
  const mp4 = smallScreen.matches && video.dataset.mobileSrc ? video.dataset.mobileSrc : video.dataset.src;
  const supportsH264 = !!video.canPlayType('video/mp4; codecs="avc1.42E01E"');
  const source = !supportsH264 && video.dataset.webmSrc ? video.dataset.webmSrc : mp4;
  if (video.getAttribute('src') !== source) video.src = source;
  video.muted = true;
  video.defaultMuted = true;
  video.setAttribute('muted', '');
  video.setAttribute('playsinline', '');
  video.setAttribute('webkit-playsinline', '');
  video.currentTime = 0;
  // Keep play() directly inside the tap handler; awaiting load first loses activation on iOS.
  const attempt = video.play();
  if (attempt) attempt.catch((error) => {
    if (attemptId === playAttempt && dialog.open) fallbackLogo(error.name === 'NotAllowedError');
  });
  later(() => { if (!video.currentTime) fallbackLogo(true); }, 10000);
  later(closeIntro, 26000);
}
function openIntro() {
  if (typeof dialog.showModal !== 'function' || dialog.open) { boot?.release(); return; }
  previousFocus = document.activeElement;
  dialog.showModal();
  boot?.release();
  closeButton.focus();
  playButton.hidden = false;
  if (reduced.matches) {
    status.textContent = '움직임을 줄인 로고 화면입니다. 원하면 영상을 직접 재생할 수 있습니다.';
    return;
  }
  startVideo();
}
video.addEventListener('playing', () => {
  if (dialog.open && !fallingBack) { markSeen(); status.textContent = '사람과 상품이 만나는 순간'; }
});
video.addEventListener('timeupdate', () => {
  if (dialog.open && !fallingBack && video.currentTime >= 3.2) status.textContent = '빠른 판매, 좋은 상품, 합리적인 가격';
});
video.addEventListener('ended', closeIntro);
video.addEventListener('error', () => fallbackLogo());
logo.addEventListener('error', () => { if (fallingBack || reduced.matches) closeIntro(); });
playButton.addEventListener('click', () => startVideo(true));
closeButton.addEventListener('click', () => { markSeen(); closeIntro(); });
dialog.addEventListener('cancel', (event) => { event.preventDefault(); markSeen(); closeIntro(); });
replay.addEventListener('click', openIntro);
reduced.addEventListener('change', () => { if (reduced.matches) closeIntro(); });
let seen = false;
try { seen = sessionStorage.getItem(sessionKey) === '1'; } catch {}
if (!seen && !reduced.matches && !boot?.timedOut) openIntro();
else boot?.release();
