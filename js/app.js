import { MAX_VENDORS, MAX_PRODUCTS_PER_VENDOR, vendorSlots, applicationError } from './capacity.mjs';
import { menswearVendors } from './menswear-data.mjs';
import { productDraftManager } from './product-drafts.js';
import { categorySelection, categoryTrail, productCategoryPath, productInCategory, categoryURL } from './taxonomy.mjs';
import { taxonomyPicker } from './taxonomy-ui.js';
import { menswearRoute } from './menswear-routing.mjs';
import { renderMenswearCollection, renderMenswearProduct } from './menswear-page.js';
import {
  availableQty,
  channelLabel,
  discountPct,
  freezeOrderSnapshot,
  liabilityCopy,
  liveListings,
  stockCopy
} from './catalog.mjs';

const knownVendors = menswearVendors;
const APP_KEY = 'clearance-demo-apps';
const THEME_KEY = 'clearance-theme';
const VIEWS = ['market', 'seller', 'manage', 'menswear', 'menswearDetail'];
let previousView = null;
let previousMenswearProduct = null;
let previousMenswearPath = null;
const STATUS_LABEL = { pending: '검토 대기(체험)', approved: '승인(체험)', rejected: '반려(체험)' };

let category = {major:'',middle:'',minor:''};
let lastFocus = null;
const dialog = document.getElementById('productDialog');
const themeBtn = document.getElementById('themeBtn');
const themeColor = document.getElementById('themeColor');

const won = (n) => Number(n).toLocaleString('ko-KR') + '원';
function uid() {
  return crypto.randomUUID ? crypto.randomUUID() : 'id-' + Date.now() + '-' + Math.random().toString(16).slice(2);
}
function parseHash() {
  const parts = location.hash.split('?')[0].replace(/^#\/?/, '').split('/').filter(Boolean);
  if (parts[0] === 'menswear') {
    const page = menswearRoute(location.hash);
    return { view: page.level === 'product' ? 'menswearDetail' : 'menswear', menswearId: page.productId, menswearRoute: page, productId: null };
  }
  if (parts[0] === 'product' && parts[1]) return { view: 'market', productId: parts[1] };
  if (['market', 'seller', 'manage'].includes(parts[0])) return { view: parts[0], productId: null };
  return { view: 'market', productId: null };
}
function go(view, productId) {
  const next = productId ? '#/product/' + productId : '#/' + view;
  if (location.hash === next) applyRoute();
  else location.hash = next;
}
function preferredTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === 'dark' || saved === 'light') return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}
function applyTheme(theme) {
  const dark = theme === 'dark';
  document.documentElement.classList.toggle('dark', dark);
  document.body.classList.toggle('dark', dark);
  themeColor.setAttribute('content', dark ? '#131b29' : '#101827');
  themeBtn.setAttribute('aria-pressed', dark ? 'true' : 'false');
}
function normalizeApps(raw) {
  if (!Array.isArray(raw)) return [];
  return raw.filter(a => a && typeof a === 'object').map((a, i) => {
    const status = ['pending', 'approved', 'rejected'].includes(a.status) ? a.status : 'pending';
    return {
      id: String(a.id || 'legacy-' + i),
      name: String(a.name || '').trim().slice(0, 60),
      type: String(a.type || '').slice(0, 30),
      createdAt: a.createdAt || new Date(0).toISOString(),
      status
    };
  }).filter((a) => a.name);
}
function getApps() {
  try { return normalizeApps(JSON.parse(localStorage.getItem(APP_KEY) || '[]')); }
  catch { return []; }
}
function setApps(apps) {
  try {
    localStorage.setItem(APP_KEY, JSON.stringify(apps));
    return true;
  } catch {
    return false;
  }
}
function syncNav(view) {
  document.querySelectorAll('header nav [data-view]').forEach((btn) => {
    if (btn.dataset.view === view) btn.setAttribute('aria-current', 'page');
    else btn.removeAttribute('aria-current');
  });
}
function showView(id) {
  for (const name of VIEWS) document.getElementById(name).classList.toggle('hidden', name !== id);
  const menswear = id === 'menswear' || id === 'menswearDetail';
  document.getElementById('marketHero').classList.toggle('hidden', menswear);
  document.getElementById('marketDemoNotice').classList.toggle('hidden', menswear);
  syncNav(menswear ? 'market' : id);
  if (id === 'manage') renderApps();
  if (id === 'seller') renderCapacity();
}
function renderCategories() {
  document.getElementById('categories').innerHTML = taxonomyPicker(category);
}
function renderProducts() {
  const q = document.getElementById('query').value.trim().toLowerCase();
  const items = liveListings().filter((x) => {
    if (!productInCategory(x, category)) return false;
    const ids=productCategoryPath(x),labels=categoryTrail({major:ids[0],middle:ids[1],minor:ids[2]}).map(c=>c.name);
    const hay = [x.title, ...labels, x.sellerOfRecord, channelLabel(x), x.region, x.condition].join(' ').toLowerCase();
    return hay.includes(q);
  });
  const root = document.getElementById('products');
  const status = document.getElementById('resultStatus');
  root.replaceChildren();
  status.textContent = items.length ? items.length + '건 표시 (예시 상품, 거래 없음)' : (q ? '검색 결과가 없습니다.' : '선택한 분류에 등록된 예시 상품이 없습니다.');
  for (const p of items) {
    const article = document.createElement('article');
    article.className = 'card';
    const art = document.createElement('div');
    art.className = 'art';
    art.setAttribute('aria-hidden', 'true');
    art.textContent = p.subcategory || p.category;
    const detail = document.createElement('div');
    detail.className = 'details';
    const tag = document.createElement('span');
    tag.className = 'tag';
    const ids=productCategoryPath(p);
    tag.textContent = categoryTrail({major:ids[0],middle:ids[1],minor:ids[2]}).map(c=>c.name).join(' · ');
    const h = document.createElement('h3');
    h.textContent = p.title;
    const seller = document.createElement('p');
    seller.className = 'muted';
    seller.textContent = '법적 판매자: ' + p.sellerOfRecord;
    const stock = document.createElement('p');
    stock.className = 'muted';
    stock.textContent = stockCopy(p) + (availableQty(p) === 0 ? ' · 판매가능 없음' : '');
    if (p.listPrice > p.price && p.price > 0) {
      const old = document.createElement('div');
      old.className = 'old';
      old.textContent = won(p.listPrice);
      detail.append(tag, h, seller, stock, old);
    } else {
      detail.append(tag, h, seller, stock);
    }
    const row = document.createElement('div');
    row.className = 'row';
    const price = document.createElement('span');
    price.className = 'price';
    price.textContent = won(p.price);
    row.append(price);
    const off = discountPct(p.price, p.listPrice);
    if (off !== null) {
      const discount = document.createElement('strong');
      discount.textContent = off + '% 할인';
      row.append(discount);
    }
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = p.subcategory === '남성복' ? '남성복 입점업체 보기' : '상세 보기';
    btn.addEventListener('click', () => {
      lastFocus = btn;
      if (p.subcategory === '남성복') location.hash = '#/menswear/clothing';
      else go('market', p.id);
    });
    detail.append(row, btn);
    article.append(art, detail);
    root.append(article);
  }
}
function render() {
  renderCategories();
  renderProducts();
}
function fact(dl, label, value) {
  const dt = document.createElement('dt');
  dt.textContent = label;
  const dd = document.createElement('dd');
  dd.textContent = value;
  dl.append(dt, dd);
}
function fillDialog(p) {
  document.getElementById('productTitle').textContent = p.title;
  document.getElementById('productChannel').textContent = channelLabel(p);
  const dl = document.getElementById('productFacts');
  dl.replaceChildren();
  fact(dl, '법적 판매자', p.sellerOfRecord);
  fact(dl, '판매 채널', channelLabel(p));
  const ids=productCategoryPath(p),trail=categoryTrail({major:ids[0],middle:ids[1],minor:ids[2]});
  fact(dl, '대분류', trail[0]?.name || '미분류');
  fact(dl, '중분류', trail[1]?.name || '미분류');
  fact(dl, '소분류', trail[2]?.name || '미분류');
  fact(dl, '상태', p.condition);
  fact(dl, '지역', p.region);
  fact(dl, '보유 재고', String(p.qtyOnHand));
  fact(dl, '예약 재고', String(p.qtyReserved) + ' (실제 예약 처리 없음)');
  fact(dl, '판매가능', String(availableQty(p)));
  fact(dl, '검수', p.status === 'approved' ? '예시 승인(데모 데이터)' : p.status);
  fact(dl, '판매가', won(p.price));
  if (p.listPrice > p.price && p.price > 0) fact(dl, '정가(예시)', won(p.listPrice));
  const off = discountPct(p.price, p.listPrice);
  if (off !== null) fact(dl, '할인', off + '%');
  document.getElementById('productLiability').textContent = liabilityCopy(p);
  const snap = freezeOrderSnapshot(p, 1);
  document.getElementById('productSnapshot').textContent = JSON.stringify(snap, null, 2);
}
function applyRoute() {
  const route = parseHash();
  showView(route.view);
  if (route.view === 'menswear' || route.view === 'menswearDetail') {
    if (dialog.open) dialog.close();
    if (location.hash !== route.menswearRoute.canonical) history.replaceState(null, '', route.menswearRoute.canonical);
    if (route.view === 'menswear') renderMenswearCollection();
    else renderMenswearProduct(route.menswearId);
    const titles = {collection:'남성복',category:'남성복 · 입점업체 선택',vendor:'남성복 · 업체별 상품',samples:'남성복 · 화면 예시',product:'남성복 · 개별 상품'};
    document.title = titles[route.menswearRoute.level] + ' | 다판다';
    const pagePath = route.menswearRoute.canonical.split('?')[0];
    if (previousView !== route.view || previousMenswearProduct !== route.menswearId || previousMenswearPath !== pagePath) {
      window.scrollTo({ top: 0, behavior: 'instant' });
      document.getElementById(route.view).querySelector('h1')?.focus({ preventScroll: true });
    }
    previousView = route.view; previousMenswearProduct = route.menswearId; previousMenswearPath = pagePath;
    return;
  }
  category = categorySelection(new URLSearchParams(location.hash.split('?')[1] || ''));
  render();
  previousView = route.view; previousMenswearProduct = null; previousMenswearPath = null;
  document.title = '다판다 | 빠른 판매, 좋은 상품, 합리적인 가격 (데모)';
  const p = route.productId ? liveListings().find((x) => x.id === route.productId) : null;
  if (p) {
    fillDialog(p);
    if (!dialog.open) dialog.showModal();
  } else {
    if (dialog.open) dialog.close();
    if (route.productId) document.getElementById('resultStatus').textContent = '해당 상품을 찾을 수 없습니다.';
  }
}
const draftManager=productDraftManager(()=>getApps().filter(a=>a.status==='approved'));
function renderCapacity(){const remaining=vendorSlots(knownVendors,getApps());document.querySelectorAll('[data-vendor-capacity]').forEach(el=>{el.textContent=`입점 정원 ${MAX_VENDORS}개 · 등록·심사 대기 ${MAX_VENDORS-remaining}개 · 남은 정원 ${remaining}개 / 업체별 상품 최대 ${MAX_PRODUCTS_PER_VENDOR}개`;});}
function renderApps() {
  renderCapacity();
  draftManager.refresh();
  const el = document.getElementById('applications');
  el.replaceChildren();
  const apps = getApps();
  if (!apps.length) {
    el.textContent = '체험 신청 내역이 없습니다.';
    return;
  }
  apps.forEach((a) => {
    const row = document.createElement('div');
    row.className = 'app-item';
    const info = document.createElement('p');
    info.style.margin = '0';
    const when = Number.isNaN(Date.parse(a.createdAt)) ? '-' : new Date(a.createdAt).toLocaleString('ko-KR');
    info.textContent = a.name + ' · ' + a.type + ' · ' + STATUS_LABEL[a.status] + ' · ' + when;
    const actions = document.createElement('div');
    actions.className = 'app-actions';
    const approve = document.createElement('button');
    approve.type = 'button';
    approve.className = 'primary';
    approve.textContent = '승인';
    approve.disabled = a.status === 'approved';
    approve.addEventListener('click', () => setAppStatus(a.id, 'approved'));
    const reject = document.createElement('button');
    reject.type = 'button';
    reject.textContent = '반려';
    reject.disabled = a.status === 'rejected';
    reject.addEventListener('click', () => setAppStatus(a.id, 'rejected'));
    actions.append(approve, reject);
    row.append(info, actions);
    el.append(row);
  });
}
function setAppStatus(id, status) {
  const current=getApps(),target=current.find(a=>a.id===id);
  if(!target)return;
  if(status==='approved'){const error=applicationError(knownVendors,current,target.name,id);if(error){document.getElementById('manageStatus').textContent=error;return;}}
  const apps = current.map((a) => a.id === id ? { ...a, status } : a);
  if (!setApps(apps)) {
    document.getElementById('manageStatus').textContent = '브라우저 저장 용량을 초과했습니다.';
    return;
  }
  renderApps();
}

document.querySelectorAll('header nav [data-view]').forEach((btn) => {
  btn.addEventListener('click', () => go(btn.dataset.view));
});
document.querySelector('.footer-bottom a[href="#top"]').addEventListener('click', (event) => {
  event.preventDefault();
  window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
  document.querySelector('header .brand').focus({ preventScroll: true });
});
themeBtn.addEventListener('click', () => {
  const next = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
  localStorage.setItem(THEME_KEY, next);
  applyTheme(next);
});
document.getElementById('searchForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const next=categoryURL(category);
  if(location.hash!==next)location.hash=next;
  render();
});
document.getElementById('query').addEventListener('input', () => {
  if (!document.getElementById('market').classList.contains('hidden')) renderProducts();
});
document.getElementById('sellerForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  const name = String(f.get('name') || '').trim().slice(0, 60);
  const type = String(f.get('type') || '').slice(0, 30);
  const statusEl = document.getElementById('sellerStatus');
  if (!name) {
    statusEl.textContent = '업체명을 입력하세요.';
    return;
  }
  const apps = getApps();
  const error=applicationError(knownVendors,apps,name);
  if(error){statusEl.textContent=error;return;}
  apps.push({ id: uid(), name, type, createdAt: new Date().toISOString(), status: 'pending' });
  if (!setApps(apps)) {
    statusEl.textContent = '브라우저 저장에 실패했습니다. 저장 용량을 확인하세요.';
    return;
  }
  statusEl.textContent = '체험 신청을 브라우저에 저장했습니다. 실제 접수는 아닙니다.';
  renderCapacity();
  e.target.reset();
});
document.getElementById('clearDemo').addEventListener('click', () => {
  if (!confirm('이 브라우저의 체험 입점 신청과 상품 초안을 모두 지울까요?')) return;
  draftManager.clear();
  localStorage.removeItem(APP_KEY);
  renderApps();
});
document.getElementById('closeProduct').addEventListener('click', () => dialog.close());
dialog.addEventListener('close', () => {
  if (parseHash().productId) location.hash = '#/market';
  if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
});
window.addEventListener('hashchange', applyRoute);
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (localStorage.getItem(THEME_KEY)) return;
  applyTheme(e.matches ? 'dark' : 'light');
});

applyTheme(preferredTheme());
if (!location.hash) history.replaceState(null, '', '#/market');
render();
applyRoute();
