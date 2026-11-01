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
