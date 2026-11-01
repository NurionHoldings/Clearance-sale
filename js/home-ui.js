import { photo, categoryPhotos } from './photo-library.mjs';
import { taxonomy, categoryURL } from './taxonomy.mjs';
import { taxonomyPicker } from './taxonomy-ui.js';
import { garmentArt } from './menswear-art.mjs';
import { foodArt } from './arirang-art.mjs';
const svg=body=>`<svg viewBox="0 0 240 230" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><ellipse cx="120" cy="190" rx="75" ry="9" fill="#263b50" opacity=".06"/>${body}</svg>`;
const art={
 footwear:svg('<path d="m61 101 42 11 23-25 21 42 47 18q17 8 10 30H43q-8-28 18-76" fill="#c8bdab"/><path d="M43 169h161v13H43Z" fill="#faf7ef"/><path d="m115 120 20-5m-14 17 21-5m-14 16 21-5" stroke="#f9f6ed" stroke-width="5"/>'),
 accessories:svg('<path d="M65 89h110l13 96H52Z" fill="#516477"/><path d="M89 96V72a31 31 0 0 1 62 0v24" fill="none" stroke="#b49b71" stroke-width="8"/><path d="M91 130q29 30 58 0" stroke="#d7bc8e" stroke-width="7" fill="none"/>'),
 watches:svg('<path d="M100 29h40v170h-40Z" fill="#a18b70"/><rect x="79" y="73" width="82" height="92" rx="24" fill="#c5aa7d"/><rect x="87" y="81" width="66" height="76" rx="18" fill="#263c50"/><path d="M120 93v29l22 12" fill="none" stroke="#ebd6ae" stroke-width="4"/>'),
 jewelry:svg('<circle cx="119" cy="132" r="45" fill="none" stroke="#c4a06d" stroke-width="14"/><path d="m88 71 16-22h33l18 22-35 37Z" fill="#dbe4e7" stroke="#b79c77" stroke-width="4"/><path d="m88 71 67 0m-51-22 16 59 17-59" fill="none" stroke="#fff" stroke-width="3"/>'),
 appliances:svg('<rect x="38" y="48" width="166" height="111" rx="9" fill="#35495a"/><rect x="46" y="56" width="150" height="95" rx="3" fill="#9eb1b6"/><path d="m46 141 53-55 38 27 32-42 27 25v55H46Z" fill="#75938f"/><path d="M119 160v22m-34 4h70" stroke="#536777" stroke-width="7"/>'),
 home:svg('<path d="M53 96q0-29 29-29h76q29 0 29 29v61H53Z" fill="#a9b7aa"/><rect x="37" y="111" width="166" height="61" rx="15" fill="#899e90"/><path d="M52 177v14m137-14v14M120 81v69" stroke="#53675b" stroke-width="7"/><path d="M58 119v31h125v-31" fill="none" stroke="#c5cec1" stroke-width="9"/>'),
 kitchen:svg('<path d="M63 100h113v55q0 25-26 25H89q-26 0-26-25Z" fill="#b5b9b7"/><path d="M56 99h126M91 84h55m-27-12v12M47 112H29v31h22m130-31h22v31h-22" fill="none" stroke="#6a7e86" stroke-width="9" stroke-linecap="round"/>'),
 tools:svg('<path d="M47 95h146v86H47Z" fill="#798e93"/><path d="M91 95V71h58v24" fill="none" stroke="#4a6067" stroke-width="9"/><path d="M47 128h146" stroke="#c7d1c8" stroke-width="5"/><rect x="109" y="119" width="22" height="20" rx="3" fill="#d3b274"/>'),
 sports:svg('<path d="m70 67 13 106m87-106-13 106M47 120l146-2" fill="none" stroke="#6f8d87" stroke-width="13" stroke-linecap="round"/><circle cx="119" cy="119" r="43" fill="#bdab8c"/><path d="m86 92 66 52m-3-54-60 58" stroke="#e9ddc7" stroke-width="4"/>')
};
const productArt={
 'p-cap':svg('<path d="M62 139q0-69 58-69t58 69Z" fill="#8c9b91"/><path d="M61 138h120q35 0 33 17-37 18-99 6l-61-6Z" fill="#596e62"/><path d="M119 73v64m-35-4q1-38 23-55" stroke="#bdc9b7" stroke-width="3" fill="none"/>'),
 'p-hikinghat':svg('<path d="m81 81 78 0 20 61H61Z" fill="#b5a584"/><ellipse cx="120" cy="150" rx="91" ry="22" fill="#8b8b6d"/><path d="m67 126 105 0 6 16H62Z" fill="#6c7c69"/>'),
 'p-dress-shoes':svg('<path d="m53 106 45 12 21-25 30 44 50 10q21 8 12 30H42q-10-29 11-71" fill="#4d4e4d"/><path d="M42 172h167v10H42Z" fill="#917558"/><path d="m107 121 20-2m-13 11 20-1m-12 12 20-1" stroke="#b9aea1" stroke-width="3"/>'),
 'p-hikingboots':svg('<path d="m79 56 58 0-3 61 25 20 41 10q18 9 10 30H47q-9-37 18-65Z" fill="#a29173"/><path d="M48 169h163v16H48Z" fill="#4c5e58"/><path d="M89 69h33m-33 16h32m-35 17h34m-20 26 25-5m-13 17 26-5" stroke="#dfd0ab" stroke-width="4"/>'),
 'p-silver-necklace':svg('<path d="M71 46C30 181 208 181 167 46" fill="none" stroke="#9eafb5" stroke-width="6"/><path d="m101 149 18-19 20 19-20 24Z" fill="#e9f0ee" stroke="#9eafb5" stroke-width="4"/>'),
 'p-refurb-vacuum':svg('<path d="m85 183 61-89" stroke="#738b96" stroke-width="10"/><path d="m138 99 32-46 25 18-32 46Z" fill="#647d8c"/><path d="m154 56 13-16 28 20-12 17" stroke="#495c6a" stroke-width="6" fill="none"/><rect x="48" y="174" width="93" height="19" rx="7" fill="#445f6e"/><path d="m138 100 15 10" stroke="#c5a27f" stroke-width="15"/>'),
 'p-display-microwave':svg('<rect x="35" y="68" width="170" height="112" rx="12" fill="#aab6b8"/><rect x="45" y="80" width="116" height="85" rx="5" fill="#425c6a"/><path d="m59 140 39-40 46 26" fill="none" stroke="#739096" stroke-width="6"/><rect x="174" y="84" width="20" height="16" rx="2" fill="#435d63"/><circle cx="184" cy="130" r="10" fill="#e3e7e0"/><path d="M55 180v9m130-9v9" stroke="#607a84" stroke-width="7"/>')
};
const clothing=(kind='아우터',swatch='#465669',id='')=>garmentArt({kind,swatch,id});
export function categoryArt(id){if(categoryPhotos[id])return photo(categoryPhotos[id]);if(id==='menswear')return clothing('셔츠','#8b9da5');if(id==='womenswear')return clothing('니트','#bcae9e');if(id==='food')return foodArt('apple');return art[id]||art.accessories;}
export function catalogArt(p){if(productArt[p.id])return productArt[p.id];if(p.subcategory==='남성복')return garmentArt(p);if(p.id==='p-womenswear')return clothing('니트','#bcae9e');if(p.id==='p-sportswear')return clothing('아우터','#82958a');if(p.id==='p-hikingwear')return clothing('아우터','#b29570');if(p.id==='p-rice')return foodArt('rice');if(p.id==='p-apples')return foodArt('apple');const root=p.categoryPath?.[0]||({'신발류':'footwear','모자':'accessories','귀금속':'jewelry','가전제품':'appliances','공산품':p.id==='p-tools'?'tools':'kitchen'})[p.category];return categoryArt(root);}
export function homeCategories(selection){if(selection.major)return taxonomyPicker(selection);return `<section class="home-categories" aria-labelledby="homeCategoryTitle"><div class="home-section-heading"><div><p class="home-kicker">EXPLORE THE MARKET</p><h2 id="homeCategoryTitle">어떤 상품을 찾으세요?</h2></div><span>품목을 선택하면 중·소분류로 이어집니다.</span></div><nav class="home-category-grid" aria-label="대분류 선택">${taxonomy.map(c=>`<a href="${categoryURL({major:c.id,middle:'',minor:''})}" data-taxonomy-level="major" data-taxonomy-id="${c.id}"><span>${categoryArt(c.id)}</span><strong>${c.name}</strong></a>`).join('')}</nav></section>`;}
export function updateHomeNavigation(view,selection,q=''){
 const params=new URLSearchParams(location.hash.split('?')[1]||'');
 const mode=selection?.major?'listing':params.get('browse')==='categories'?'categories':q.trim()||params.get('focus')==='search'?'search':'home';
 document.body.dataset.marketMode=mode;
 const active=(view==='menswear'||view==='menswearDetail')?'categories':view==='arirang'?(location.hash.split('?')[0]==='#/arirang/cart'?'cart':'food'):view==='market'?(mode==='listing'||mode==='categories'?'categories':mode==='search'?'search':'home'):'';
 document.querySelectorAll('#mobileNav a').forEach(a=>{if(a.dataset.tab===active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
}
export function initializeHome(){
 const mobile=matchMedia('(max-width:760px)'),form=document.getElementById('searchForm');
 const positionSearch=()=>{document.getElementById(mobile.matches?'homeSearchBar':'homeHeroSearchSlot').append(form);};positionSearch();mobile.addEventListener('change',positionSearch);
 document.querySelectorAll('#mobileNav [data-tab=home],#mobileNav [data-tab=categories],header .brand').forEach(a=>a.addEventListener('click',()=>{document.getElementById('query').value='';if(location.hash===a.getAttribute('href'))window.dispatchEvent(new HashChangeEvent('hashchange'));}));
document.getElementById('homeHeroArt').innerHTML=`${photo('fashion',true)}<span class="photo-editorial-label">CURATED EVERYDAY<br><strong>일상에 좋은 발견</strong><small>카테고리 연출 이미지</small></span>`;document.getElementById('homeMenswearArt').innerHTML=photo('knit');document.getElementById('homeFoodArt').innerHTML=photo('food');}
