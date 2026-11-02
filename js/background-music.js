// Keep the audible media element in its original document while full HTML menus
// load in an isolated same-origin content frame. Page scripts keep their own globals.
function musicNavigationIsChild() {
  try { return window.parent !== window && window.frameElement?.id === 'music-content-frame' && !!window.parent.__musicNavigation; } catch { return false; }
}
function installMusicNavigation({audio, controls, toggleSelector, stylesheet, focusEvent, resume}) {
  if (window.__musicNavigation) return;
  let frame, loading = false;
  window.__musicNavigation = { audio };
  const eligible = url => url.origin === location.origin && (url.pathname.endsWith('/') || /\.html$/.test(url.pathname));
  const sameDocument = (a,b) => a.pathname === b.pathname && a.search === b.search;
  function navigate(url, push = true) {
    if (!eligible(url)) return;
    if (!frame) {
      frame = document.createElement('iframe');
      frame.id = 'music-content-frame';
      frame.title = '사이트 본문';
      frame.allow = 'autoplay; fullscreen';
      frame.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;border:0;background:white;z-index:2147483646';
      const style = document.createElement('style');
      style.textContent = 'html.music-navigation-host,html.music-navigation-host body{overflow:hidden!important}html.music-navigation-host body> :not(#music-content-frame){display:none!important}@media print{#music-content-frame{position:static!important;height:100vh!important}}';
      document.head.append(style);
      for (const dialog of document.querySelectorAll('dialog[open]')) dialog.close();
      for (const video of document.querySelectorAll('video')) video.pause();
      document.documentElement.classList.add('music-navigation-host');
      frame.addEventListener('load', connect);
      document.body.append(frame);
    }
    loading = true;
    if (push) history.pushState({musicNavigation:true}, '', url.href);
    frame.contentWindow.location.replace(url.href);
  }
  function intercept(event, win) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest?.('a[href]');
    if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self') || link.relList.contains('external')) return;
    const url = new URL(link.href, win.location.href);
    if (url.origin !== location.origin && win !== window) { link.target='_top'; return; }
    if (!eligible(url) || sameDocument(url,new URL(win.location.href))) return;
    event.preventDefault();
    navigate(url);
  }
  function connect() {
    let win, doc;
    try { win = frame.contentWindow; doc = win.document; if (!doc.body || win.location.href === 'about:blank') return; } catch { return; }
    loading = false;
    document.title = doc.title;
    history.replaceState({musicNavigation:true}, '', win.location.href);
    // Child music scripts exit before constructing a second player. Pages that
    // have no player receive the same controls and stylesheet here as well.
    if (!doc.querySelector('link[data-music-navigation-style]')) {
      const link = doc.createElement('link'); link.rel='stylesheet'; link.href=stylesheet; link.dataset.musicNavigationStyle=''; doc.head.append(link);
    }
    let proxy = doc.querySelector(controls);
    if (!proxy) { proxy = document.querySelector(controls).cloneNode(true); delete proxy.dataset.disclosureReady; doc.body.append(proxy); }
    setupMusicDisclosure(doc, proxy);
    const source = document.querySelector(controls);
    function render() {
      const sourceToggle = source.querySelector(toggleSelector);
      for (const button of doc.querySelectorAll(toggleSelector)) {
        button.innerHTML=sourceToggle.innerHTML;button.removeAttribute('aria-controls');
        for (const attr of ['aria-label','aria-pressed','title']) if(sourceToggle.hasAttribute(attr))button.setAttribute(attr,sourceToggle.getAttribute(attr));
      }
      proxy.dataset.playing=source.dataset.playing || String(!audio.paused);
      const input=proxy.querySelector('input'); if(input)input.value=String(Math.round(audio.volume*100));
      const status=proxy.querySelector('[role=status]'); if(status)status.textContent=source.querySelector('[role=status]')?.textContent||'';
      const dialog=doc.querySelector('dialog[open]'); const target=dialog||doc.body;if(proxy.parentNode!==target)target.append(proxy);
    }
    doc.addEventListener('click', event => {
      if(event.target.closest?.(toggleSelector)){event.preventDefault();source.querySelector(toggleSelector).click();render();return;}
      intercept(event,win);
    });
    doc.addEventListener('input', event => {
      if(proxy.contains(event.target) && event.target.matches('input[type=range]')) {
        const input=source.querySelector('input');if(input){input.value=event.target.value;input.dispatchEvent(new Event('input',{bubbles:true}));}
      }
    });
    // An interaction in the content frame can also unlock blocked autoplay.
    function unlock(event) {
      if (!audio.paused || event.target.closest?.(toggleSelector+', [data-music-disclosure], input, textarea, select, [contenteditable]')) return;
      if (event.type==='keydown' && !['Enter',' '].includes(event.key)) return;
      resume();
    }
    doc.addEventListener('pointerup',unlock);doc.addEventListener('keydown',unlock);
    if(focusEvent)doc.addEventListener(focusEvent,()=>document.dispatchEvent(new CustomEvent(focusEvent)));
    const observer=new MutationObserver(render);observer.observe(source,{attributes:true,childList:true,subtree:true,characterData:true});
    const dialogs=new win.MutationObserver(()=>{const target=doc.querySelector('dialog[open]')||doc.body;if(proxy.parentNode!==target)target.append(proxy);});dialogs.observe(doc.body,{subtree:true,childList:true,attributes:true,attributeFilter:['open']});
    function sync(){if(!loading)history.replaceState({musicNavigation:true},'',win.location.href);}
    win.addEventListener('hashchange',sync);win.addEventListener('popstate',sync);
    win.addEventListener('pagehide',()=>{observer.disconnect();dialogs.disconnect();},{once:true});
    render();
  }
  setupMusicDisclosure(document, document.querySelector(controls));
  document.addEventListener('click', event=>intercept(event,window));
  window.addEventListener('popstate',()=>{
    if(frame && frame.contentWindow.location.href !== location.href)navigate(new URL(location.href),false);
  });
}

function setupMusicDisclosure(doc, controls) {
  if (controls.dataset.disclosureReady) return;
  controls.dataset.disclosureReady='true';
  let launcher=controls.querySelector('[data-music-disclosure]');
  if(!launcher){launcher=doc.createElement('button');launcher.type='button';launcher.dataset.musicDisclosure='';launcher.className='music-launcher';launcher.textContent='♫';controls.prepend(launcher);}
  function expand(value){controls.dataset.expanded=String(value);launcher.setAttribute('aria-expanded',String(value));launcher.setAttribute('aria-label',value?'음악 조절 닫기':'음악 조절 열기');}
  expand(false);
  launcher.addEventListener('click',()=>expand(controls.dataset.expanded!=='true'));
  doc.addEventListener('click',event=>{if(!controls.contains(event.target))expand(false);});
  doc.addEventListener('keydown',event=>{if(event.key==='Escape'&&controls.dataset.expanded==='true'){expand(false);launcher.focus();}});
}

if (!musicNavigationIsChild()) {
const audio=document.getElementById('backgroundMusic');
const buttons=[...document.querySelectorAll('[data-music-toggle]')];
const status=document.getElementById('musicStatus');
const preferenceKey='dapanda-background-music-enabled-v1';
const positionKey='dapanda-background-music-position-v1';
let enabled=true,pending=false,attempt=0,lastSaved=0;
try{enabled=localStorage.getItem(preferenceKey)!=='false';}catch{}
function preference(value){enabled=value;try{localStorage.setItem(preferenceKey,String(value));}catch{}}
function update(state,message=''){
 audio.dataset.state=state;
 const playing=state==='playing',loading=state==='loading';
 for(const button of buttons){button.textContent=playing||loading?'♫ 음악 정지':'♫ 음악 켜기';button.setAttribute('aria-pressed',String(playing));button.setAttribute('aria-label',playing||loading?'배경음악 정지':'배경음악 재생');button.title=message||button.getAttribute('aria-label');}
 status.textContent=message||(playing?'배경음악 재생 중입니다.':'배경음악이 정지되어 있습니다.');
}
function savePosition(){try{if(Number.isFinite(audio.currentTime))sessionStorage.setItem(positionKey,String(audio.currentTime));}catch{}}
function stop(remember=true){attempt++;pending=false;if(remember)preference(false);else enabled=false;disarm();audio.pause();savePosition();update('paused');}
function gesture(event){if(!enabled||event.target.closest?.('[data-music-toggle]'))return;if(event.type==='keydown'&&!['Enter',' '].includes(event.key))return;play();}
function arm(){document.addEventListener('click',gesture,true);document.addEventListener('keydown',gesture,true);}
function disarm(){document.removeEventListener('click',gesture,true);document.removeEventListener('keydown',gesture,true);}
function play(){
 if(!enabled||pending)return;
 const token=++attempt;pending=true;update('loading');
 if(!audio.getAttribute('src'))audio.src=audio.dataset.src;
 else if(audio.error)audio.load();
 // Keep play() in the user event stack when an interaction unlocks audible playback.
 audio.play().then(()=>{if(token!==attempt){if(!enabled)audio.pause();return;}pending=false;if(!enabled){audio.pause();return;}disarm();update('playing');}).catch(error=>{
  if(token!==attempt)return;pending=false;
  if(!enabled){update('paused');return;}
  if(error.name==='NotAllowedError'){update('blocked','자동재생이 제한되었습니다. 음악 켜기 버튼을 누르거나 화면을 터치하면 재생을 다시 시도합니다.');arm();}
  else if(error.name!=='AbortError'){disarm();update('error','음악을 불러오지 못했습니다. 음악 켜기로 다시 시도할 수 있습니다.');}
  else update('paused');
 });
}
for(const button of buttons)button.addEventListener('click',()=>{if(pending||!audio.paused)stop();else{preference(true);play();}});
audio.volume=.3;
audio.addEventListener('loadedmetadata',()=>{try{const position=Number(sessionStorage.getItem(positionKey));if(Number.isFinite(position)&&position>0&&position<audio.duration-1)audio.currentTime=position;}catch{}});
audio.addEventListener('playing',()=>{if(!enabled){audio.pause();return;}disarm();update('playing');});
audio.addEventListener('pause',()=>{if(!pending)update('paused');});
audio.addEventListener('error',()=>{pending=false;disarm();update('error','음악을 불러오지 못했습니다. 음악 켜기로 다시 시도해 주세요.');});
audio.addEventListener('timeupdate',()=>{if(Date.now()-lastSaved>5000){savePosition();lastSaved=Date.now();}});
window.addEventListener('pagehide',()=>{attempt++;pending=false;savePosition();audio.pause();});
window.addEventListener('pageshow',event=>{if(event.persisted&&enabled)play();});
window.addEventListener('storage',event=>{if(event.key===preferenceKey&&event.newValue==='false')stop(false);});
if(enabled)play();else update('paused');

// A deliberate switch to a live player takes audio focus without overwriting the user's saved preference.
document.addEventListener('dapanda:media-focus',()=>{stop(false);status.textContent='방송 소리를 위해 배경음악을 정지했습니다.';});

installMusicNavigation({audio,controls:'.music-control',toggleSelector:'[data-music-toggle]',stylesheet:new URL('../assets/background-music.css',import.meta.url).href,focusEvent:'dapanda:media-focus',resume:play});
}
