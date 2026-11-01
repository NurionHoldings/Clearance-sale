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
