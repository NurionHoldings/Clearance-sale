import { categorySelection, categoryURL } from './taxonomy.mjs';
export function marketReturnURL(params=new URLSearchParams()) {
 const selected=categorySelection(params),next=new URLSearchParams(),q=(params.get('q')||'').slice(0,80).trim();if(q)next.set('q',q);
 return categoryURL(selected,'#/market',next);
}
export function productDetailURL(id,selection,q='') {
 const params=new URLSearchParams();if(q.trim())params.set('q',q.trim().slice(0,80));
 return categoryURL(selection,'#/product/'+encodeURIComponent(id),params);
}
export function menswearStepURLs(selection){
 return ['#/menswear',categoryURL({major:'menswear',middle:selection.middle||'',minor:''},'#/menswear/clothing'),categoryURL({major:'menswear',middle:selection.middle||'',minor:selection.minor||''},'#/menswear/clothing')];
}
export function detailNavigation(previousHref) {
 const href=String(previousHref).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 return `<nav class="page-return-nav" aria-label="이전 화면 및 홈 이동"><a href="${href}" data-page-previous>← 이전</a><a href="#/market" data-page-home>홈가기</a></nav>`;
}
