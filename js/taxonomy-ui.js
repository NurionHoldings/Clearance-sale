import { taxonomy, categoryTrail, categoryURL } from './taxonomy.mjs';
export function taxonomyPicker(selection,{menswear=false,base='#/menswear/clothing',params=new URLSearchParams()}={}) {
 const trail=categoryTrail(selection),mid=trail[1],root=trail[0];
 const list=(rows,key,current)=>rows.map(row=>{
  const value={...selection,[key]:row.id};if(key==='major'){value.middle='';value.minor='';}if(key==='middle')value.minor='';
  const href=menswear&&value.major==='menswear'?categoryURL(value,base,params):categoryURL(value);
  return `<a href="${href}" data-taxonomy-level="${key}" data-taxonomy-id="${row.id}"${row.id===current?' aria-current="true"':''}>${row.name}</a>`;
 }).join('');
 return `<section class="taxonomy-picker" aria-label="대분류 중분류 소분류 선택"><div class="taxonomy-picker-heading"><strong>상품 카테고리</strong><span>대분류 → 중분류 → 소분류</span><a href="${menswear?'#/menswear':'#/market'}">전체 보기</a></div><div class="taxonomy-columns"><div class="taxonomy-column"><h3><span>01</span> 대분류</h3><div class="taxonomy-options">${list(taxonomy,'major',selection.major)}</div></div><div class="taxonomy-column"><h3><span>02</span> 중분류${root?' · '+root.name:''}</h3>${root?`<div class="taxonomy-options">${list(root.children,'middle',selection.middle)}</div>`:'<p class="taxonomy-prompt">대분류를 먼저 선택해 주세요.</p>'}</div><div class="taxonomy-column"><h3><span>03</span> 소분류${mid?' · '+mid.name:''}</h3>${mid?`<div class="taxonomy-options">${list(mid.children,'minor',selection.minor)}</div>`:'<p class="taxonomy-prompt">중분류를 먼저 선택해 주세요.</p>'}</div></div><p class="taxonomy-current">현재 분류: <strong>${trail.length?trail.map(x=>x.name).join(' › '):'전체 상품'}</strong></p></section>`;
}
