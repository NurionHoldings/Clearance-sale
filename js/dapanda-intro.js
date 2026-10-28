// Approved logo remains an unmodified image; motion is a separate presentation layer.
const dialog = document.querySelector('#dapandaEntry');
const logo = dialog.querySelector('img');
const closeButton = dialog.querySelector('button');
const replay = document.querySelector('#replayDapandaIntro');
const status = dialog.querySelector('[role="status"]');
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
let timer;
let fallback;
let previousFocus;
const sessionKey = 'dapanda-intro-seen-v1';
function closeIntro() {
  clearTimeout(timer);
  clearTimeout(fallback);
  dialog.classList.remove('playing');
  if (dialog.open) dialog.close();
  if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
}
function startMotion() {
  if (!dialog.open || reduced.matches) return;
  clearTimeout(fallback);
  dialog.classList.add('playing');
  status.textContent = '잠시 후 다판다로 이동합니다.';
  timer = setTimeout(closeIntro, 5800);
}
function openIntro() {
  if (typeof dialog.showModal !== 'function' || dialog.open) return;
  previousFocus = document.activeElement;
  status.textContent = reduced.matches ? '움직임을 줄인 로고 화면입니다.' : '로고를 불러오는 중입니다.';
  dialog.showModal();
  closeButton.focus();
  if (reduced.matches) return;
  fallback = setTimeout(closeIntro, 8000); // A failed or slow image never blocks entry.
  if (logo.complete) {
    if (logo.naturalWidth) startMotion(); else closeIntro();
  }
}
logo.addEventListener('load', startMotion);
logo.addEventListener('error', closeIntro);
closeButton.addEventListener('click', closeIntro);
dialog.addEventListener('cancel', (event) => { event.preventDefault(); closeIntro(); });
replay.addEventListener('click', openIntro);
reduced.addEventListener('change', () => { if (reduced.matches) closeIntro(); });
let seen = false;
try { seen = sessionStorage.getItem(sessionKey) === '1'; sessionStorage.setItem(sessionKey, '1'); } catch { /* Storage is optional. */ }
if (!seen && !reduced.matches) openIntro();
