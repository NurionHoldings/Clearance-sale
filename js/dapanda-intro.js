// Approved artwork stays intact. MP4: real crowd -> dissolve -> animated logo.
const dialog = document.querySelector('#dapandaEntry');
const video = dialog.querySelector('video');
const logo = dialog.querySelector('img');
const closeButton = dialog.querySelector('button');
const replay = document.querySelector('#replayDapandaIntro');
const status = dialog.querySelector('[role="status"]');
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const boot = globalThis.dapandaEntryBoot;
const sessionKey = boot?.sessionKey || 'dapanda-intro-seen-v3';
let timers = [];
let previousFocus;
let fallingBack = false;
let lastProgress = 0;
const later = (fn, delay) => { const id = setTimeout(fn, delay); timers.push(id); return id; };
function clearTimers() { timers.forEach(clearTimeout); timers = []; }
function closeIntro() {
  boot?.release();
  clearTimers();
  video.pause();
  dialog.classList.remove('playing', 'cinema-playing');
  if (dialog.open) dialog.close();
  if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
}
function fallbackLogo() {
  if (!dialog.open || fallingBack) return;
  fallingBack = true;
  clearTimers();
  video.pause();
  dialog.classList.remove('cinema-playing');
  status.textContent = '다판다에 오신 것을 환영합니다.';
  if (!reduced.matches) {
    dialog.classList.add('playing');
    later(closeIntro, 5800);
  }
}
function openIntro() {
  if (typeof dialog.showModal !== 'function' || dialog.open) { boot?.release(); return; }
  previousFocus = document.activeElement;
  fallingBack = false;
  status.textContent = reduced.matches ? '움직임을 줄인 로고 화면입니다.' : '다판다를 만나보세요.';
  dialog.showModal();
  boot?.release(); // The modal now covers the viewport before the home is revealed.
  closeButton.focus();
  if (reduced.matches) return; // Do not even load video for reduced-motion users.
  dialog.classList.add('cinema-playing');
  if (!video.getAttribute('src')) video.src = video.dataset.src;
  video.muted = true;
  video.currentTime = 0;
  lastProgress = 0;
  const attempt = video.play();
  if (attempt) attempt.catch(fallbackLogo);
  later(() => { if (!video.currentTime) fallbackLogo(); }, 5000);
  later(closeIntro, 20000); // Hard bound even on stalls or network interruption.
}
video.addEventListener('timeupdate', () => {
  if (!dialog.open || fallingBack) return;
  const time = video.currentTime;
  if (time > lastProgress) {
    lastProgress = time;
    status.textContent = time < 3.2 ? '사람과 상품이 만나는 순간' : '빠른 판매, 좋은 상품, 합리적인 가격';
  }
});
video.addEventListener('ended', closeIntro);
video.addEventListener('error', fallbackLogo);
logo.addEventListener('error', () => { if (fallingBack || reduced.matches) closeIntro(); });
closeButton.addEventListener('click', closeIntro);
dialog.addEventListener('cancel', (event) => { event.preventDefault(); closeIntro(); });
replay.addEventListener('click', openIntro);
reduced.addEventListener('change', () => { if (reduced.matches) closeIntro(); });
let seen = false;
try { seen = sessionStorage.getItem(sessionKey) === '1'; sessionStorage.setItem(sessionKey, '1'); } catch { /* Storage is optional. */ }
if (!seen && !reduced.matches && !boot?.timedOut) openIntro();
else boot?.release();
