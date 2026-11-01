import { taxonomy, categorySelection } from './taxonomy.mjs';
export const foodCategories=taxonomy.find(x=>x.id==='food').children;
export const foodProducts=[
 ['ar-apple','산뜻한 사과','3입 · 약 750g','fruit','apples',6900,8,'ambient','apple','국내산','신선한 식탁'],
 ['ar-citrus','제철 감귤','1봉 · 1kg','fruit','citrus',7900,12,'ambient','citrus','국내산','신선한 식탁'],
 ['ar-greens','아삭한 샐러드 채소','1팩 · 150g','vegetables','leafy',3900,10,'chilled','greens','상품 등록 시 확인','신선한 식탁'],
 ['ar-carrot','요리에 쓰기 좋은 당근','1봉 · 500g','vegetables','roots',2900,14,'ambient','carrot','국내산','신선한 식탁'],
 ['ar-pork','구이용 돼지고기','1팩 · 500g','meat','pork',12900,6,'chilled','meat','국내산','신선한 식탁'],
 ['ar-eggs','매일 쓰는 신선란','1팩 · 10구','meat','eggs',4900,10,'chilled','eggs','국내산','신선한 식탁'],
 ['ar-fish','손질 고등어','1팩 · 2쪽','seafood','fish',7900,4,'frozen','fish','상품 등록 시 확인','신선한 식탁'],
 ['ar-milk','담백한 우유','1팩 · 900mL','dairy','milk',2900,12,'chilled','milk','상품 등록 시 확인','매일의 기본'],
 ['ar-yogurt','플레인 요거트','1개 · 400g','dairy','yogurt',3900,0,'chilled','yogurt','상품 등록 시 확인','매일의 기본'],
 ['ar-rice','우리 쌀','1포 · 2kg','grains','rice',12900,8,'ambient','rice','국내산','매일의 기본'],
 ['ar-mealkit','따뜻한 한 끼 밀키트','1팩 · 2인분','ready-meals','meal-kits',9900,7,'chilled','meal','상품 등록 시 확인','간편한 한 끼'],
 ['ar-dumpling','든든한 냉동만두','1봉 · 500g','frozen','dumplings',5900,9,'frozen','dumpling','상품 등록 시 확인','간편한 한 끼'],
 ['ar-chips','바삭한 초코칩 쿠키','1봉 · 60g','snacks','chips',1900,20,'ambient','chips','상품 등록 시 확인','잠깐의 달콤함'],
 ['ar-nuts','하루 견과','1봉 · 200g','snacks','nuts',6900,10,'ambient','nuts','상품 등록 시 확인','잠깐의 달콤함'],
 ['ar-water','가볍게 챙기는 생수','500mL × 6병','drinks','water',2900,15,'ambient','water','상품 등록 시 확인','매일의 기본'],
 ['ar-juice','상큼한 오렌지 주스','1병 · 1L','drinks','juice',4900,10,'chilled','juice','상품 등록 시 확인','잠깐의 달콤함'],
 ['ar-bread','부드러운 식빵','1봉 · 400g','bakery','bread',3900,6,'ambient','bread','상품 등록 시 확인','매일의 기본'],
 ['ar-sauce','요리의 기본 토마토소스','1병 · 500mL','condiments','sauces',4900,8,'ambient','sauce','상품 등록 시 확인','매일의 기본']
].map(([id,title,unit,middle,minor,price,stock,storage,art,origin,theme])=>({id,title,unit,categoryPath:['food',middle,minor],price,stock,storage,art,origin,theme,sellerId:'arirang-demo',sellerOfRecord:'아리랑 식품 예시 업체 (가상)',executable:false}));
export const storageLabels={ambient:'실온',chilled:'냉장',frozen:'냉동'};
export function foodState(params=new URLSearchParams()) {return {classification:categorySelection(new URLSearchParams({major:'food',middle:params.get('middle')||'',minor:params.get('minor')||''})),q:(params.get('q')||'').slice(0,80),sort:['price-asc','price-desc'].includes(params.get('sort'))?params.get('sort'):'recommend',stock:params.get('stock')==='1'};}
export function filteredFood(state){const c=state.classification;const rows=foodProducts.filter(p=>(!c.middle||p.categoryPath[1]===c.middle)&&(!c.minor||p.categoryPath[2]===c.minor)&&(!state.stock||p.stock>0)&&(`${p.title} ${p.unit} ${p.theme}`.includes(state.q.trim())));if(state.sort==='price-asc')rows.sort((a,b)=>a.price-b.price);if(state.sort==='price-desc')rows.sort((a,b)=>b.price-a.price);return rows;}
export function normalizeBasket(raw){if(!raw||typeof raw!=='object'||Array.isArray(raw))return {};const basket={};for(const p of foodProducts){const n=raw[p.id];if(Number.isSafeInteger(n)&&n>0&&p.stock>0)basket[p.id]=Math.min(n,p.stock);}return basket;}
export function basketSummary(raw){const basket=normalizeBasket(raw);return foodProducts.reduce((a,p)=>{const n=basket[p.id]||0;return {count:a.count+n,total:a.total+p.price*n,lines:a.lines+(n?1:0)};},{count:0,total:0,lines:0});}
