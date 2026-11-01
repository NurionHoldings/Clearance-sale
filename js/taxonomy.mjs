// Dapanda's own three-level merchandise taxonomy. Vendor, brand and condition are separate dimensions.
const major=(id,name,rows)=>({id,name,children:rows.map(([mid,label,leaves])=>({id:mid,name:label,children:leaves.map(([leaf,text])=>({id:leaf,name:text}))}))});
export const taxonomy=[
 major('menswear','남성복',[
  ['pants','바지',[['slacks','슬랙스'],['denim','청바지'],['cotton','면바지'],['shorts','반바지'],['cargo','카고바지']]],
  ['suits','슈트',[['two-piece','투피스 슈트'],['three-piece','쓰리피스 슈트'],['suit-jackets','정장 재킷'],['suit-pants','정장 바지']]],
  ['sportswear','운동복',[['training-sets','트레이닝 세트'],['sports-tops','스포츠 상의'],['sports-pants','스포츠 하의'],['compression','기능성 이너웨어']]],
  ['hiking','등산복',[['jackets','등산 재킷'],['pants','등산 바지'],['tops','등산 티셔츠'],['vests','등산 조끼']]],
  ['outerwear','아우터',[['padding','패딩'],['coats','코트'],['jackets','재킷'],['windbreakers','바람막이'],['vests','베스트']]],
  ['tops','상의',[['tshirts','티셔츠'],['sweatshirts','맨투맨'],['hoodies','후드'],['polo','카라 티셔츠']]],
  ['shirts','셔츠',[['oxford','옥스퍼드 셔츠'],['dress','드레스 셔츠'],['casual','캐주얼 셔츠'],['linen','리넨 셔츠']]],
  ['knitwear','니트·카디건',[['round','라운드넥 니트'],['turtleneck','터틀넥 니트'],['cardigans','카디건'],['vests','니트 조끼']]],
  ['innerwear','속옷·홈웨어',[['underwear','속옷'],['pajamas','잠옷'],['loungewear','실내복']]]
 ]),
 major('womenswear','여성복',[
  ['tops','상의',[['tshirts','티셔츠'],['blouses','블라우스'],['shirts','셔츠'],['hoodies','맨투맨·후드']]],
  ['pants','바지',[['slacks','슬랙스'],['denim','청바지'],['cotton','면바지'],['shorts','반바지']]],
  ['dresses','원피스',[['mini','미니 원피스'],['midi','미디 원피스'],['long','롱 원피스']]],
  ['skirts','스커트',[['mini','미니 스커트'],['midi','미디 스커트'],['long','롱 스커트']]],
  ['outerwear','아우터',[['jackets','재킷'],['coats','코트'],['padding','패딩'],['vests','베스트']]],
  ['knitwear','니트·카디건',[['round','라운드넥 니트'],['turtleneck','터틀넥 니트'],['cardigans','카디건']]],
  ['suits','슈트·셋업',[['pants-sets','팬츠 슈트'],['skirt-sets','스커트 슈트'],['casual-sets','캐주얼 셋업']]],
  ['sportswear','운동복',[['training-sets','트레이닝 세트'],['leggings','레깅스'],['tops','스포츠 상의']]],
  ['hiking','등산복',[['jackets','등산 재킷'],['pants','등산 바지'],['tops','등산 티셔츠']]],
  ['innerwear','속옷·홈웨어',[['underwear','속옷'],['pajamas','잠옷'],['loungewear','실내복']]]
 ]),
 major('footwear','신발',[
  ['sneakers','운동화',[['casual','캐주얼 운동화'],['running','러닝화'],['walking','워킹화'],['training','트레이닝화'],['court','농구·테니스화']]],
  ['dress-shoes','구두',[['derby','더비·옥스퍼드'],['loafers','로퍼'],['pumps','펌프스'],['flats','플랫슈즈']]],
  ['outdoor','아웃도어화',[['hiking','등산화'],['trekking','트레킹화'],['trail','트레일 러닝화']]],
  ['boots','부츠',[['ankle','앵클부츠'],['long','롱부츠'],['rain','레인부츠']]],
  ['sandals','샌들·슬리퍼',[['sandals','샌들'],['slides','슬리퍼'],['clogs','클로그']]]
 ]),
 major('accessories','액세서리',[
  ['bags','가방',[['crossbody','크로스백'],['tote','토트백'],['backpack','백팩'],['travel','여행가방']]],
  ['wallets','지갑',[['short','반지갑'],['long','장지갑'],['card','카드지갑']]],
  ['hats','모자',[['baseball','야구모자'],['hiking','등산모자'],['bucket','버킷햇'],['beanie','비니']]],
  ['belts','벨트',[['leather','가죽 벨트'],['casual','캐주얼 벨트']]],
  ['scarves','스카프·머플러',[['scarves','스카프'],['mufflers','머플러']]],
  ['eyewear','안경·선글라스',[['frames','안경테'],['sunglasses','선글라스']]],
  ['socks','양말·장갑',[['socks','양말'],['gloves','장갑']]]
 ]),
 major('watches','시계',[
  ['fashion','패션 시계',[['analog','아날로그 시계'],['digital','디지털 시계']]],
  ['mechanical','기계식 시계',[['automatic','오토매틱'],['manual','수동 시계']]],
  ['smart','스마트워치',[['watch','스마트워치'],['bands','스마트밴드']]],
  ['parts','시계 용품',[['straps','시곗줄'],['storage','보관함']]]
 ]),
 major('jewelry','귀금속',[
  ['gold','금 주얼리',[['rings','금 반지'],['necklaces','금 목걸이'],['bracelets','금 팔찌'],['earrings','금 귀걸이']]],
  ['silver','실버 주얼리',[['rings','실버 반지'],['necklaces','실버 목걸이'],['bracelets','실버 팔찌'],['earrings','실버 귀걸이']]],
  ['gems','보석 주얼리',[['diamond','다이아몬드 주얼리'],['colored','유색보석 주얼리'],['pearls','진주 주얼리']]],
  ['bullion','골드바·실버바',[['gold-bars','골드바'],['silver-bars','실버바']]]
 ]),
 major('appliances','가전',[
  ['television','TV·영상가전',[['led','LED TV'],['oled','OLED TV'],['projectors','프로젝터']]],
  ['kitchen','주방가전',[['refrigerators','냉장고'],['microwave','전자레인지'],['rice-cookers','전기밥솥'],['air-fryers','에어프라이어']]],
  ['cleaning','청소·생활가전',[['stick','스틱 청소기'],['robot','로봇 청소기'],['washers','세탁기'],['dryers','건조기']]],
  ['climate','계절·환경가전',[['air-conditioners','에어컨'],['fans','선풍기'],['heaters','난방기'],['purifiers','공기청정기']]],
  ['digital','디지털 기기',[['computers','컴퓨터'],['tablets','태블릿'],['audio','음향기기']]]
 ]),
 major('home','가구·인테리어',[
  ['bedroom','침실 가구',[['beds','침대'],['mattresses','매트리스'],['wardrobes','옷장']]],
  ['living','거실 가구',[['sofas','소파'],['tables','거실 테이블'],['cabinets','수납장']]],
  ['office','서재·사무 가구',[['desks','책상'],['chairs','의자'],['shelves','책장']]],
  ['decor','인테리어 소품',[['lighting','조명'],['curtains','커튼'],['rugs','러그']]]
 ]),
 major('kitchen','생활·주방',[
  ['cookware','조리도구',[['pots','냄비'],['pans','프라이팬'],['utensils','조리도구 세트']]],
  ['tableware','식기',[['plates','접시·그릇'],['cutlery','수저·커트러리'],['cups','컵·텀블러']]],
  ['storage','정리·수납',[['boxes','수납함'],['racks','정리 선반']]],
  ['household','생활용품',[['bath','욕실용품'],['cleaning','청소용품'],['laundry','세탁용품']]],
  ['bedding','침구',[['blankets','이불'],['pillows','베개'],['sheets','침구 커버']]]
 ]),
 major('food','식품·농산물',[
  ['fruit','과일',[['apples','사과'],['pears','배'],['citrus','감귤·오렌지'],['seasonal','제철 과일']]],
  ['vegetables','채소',[['leafy','잎채소'],['roots','뿌리채소'],['mushrooms','버섯']]],
  ['meat','정육·계란',[['pork','돼지고기'],['beef','소고기'],['chicken','닭고기'],['eggs','계란']]],
  ['seafood','수산',[['fish','생선'],['shellfish','조개·갑각류'],['dried','건어물·김']]],
  ['dairy','유제품',[['milk','우유'],['yogurt','요거트'],['cheese','치즈']]],
  ['grains','쌀·잡곡',[['rice','쌀'],['mixed','잡곡'],['beans','콩']]],
  ['ready-meals','간편식·밀키트',[['meal-kits','밀키트'],['rice-meals','즉석밥·도시락'],['soups','국·탕·찌개']]],
  ['frozen','냉동식품',[['dumplings','만두'],['fried','튀김·너겟'],['desserts','아이스크림']]],
  ['snacks','과자·간식',[['chips','과자'],['nuts','견과류'],['chocolate','초콜릿']]],
  ['drinks','생수·음료',[['water','생수'],['juice','주스'],['coffee-tea','커피·차']]],
  ['bakery','베이커리',[['bread','식빵·빵'],['desserts','케이크·디저트']]],
  ['condiments','양념·소스',[['sauces','소스·장류'],['oils','식용유·오일'],['spices','조미료']]],
  ['processed','기타 가공식품',[['snacks','가공 간식'],['drinks','가공 음료'],['ready-meals','가공 간편식'],['condiments','가공 조미료']]]
 ]),
 major('tools','공구·산업용품',[
  ['hand','수공구',[['sets','공구 세트'],['drivers','드라이버'],['wrenches','렌치'],['pliers','플라이어']]],
  ['power','전동공구',[['drills','드릴'],['grinders','그라인더'],['saws','전동톱']]],
  ['safety','안전용품',[['helmets','안전모'],['shoes','안전화'],['gloves','작업 장갑']]],
  ['supplies','산업 소모품',[['fasteners','나사·볼트'],['tapes','테이프'],['abrasives','연마용품']]]
 ]),
 major('sports','스포츠·레저',[
  ['fitness','헬스·트레이닝',[['sets','트레이닝복'],['weights','웨이트 용품'],['mats','요가·운동 매트']]],
  ['hiking','등산·아웃도어',[['jackets','등산 의류'],['packs','등산 배낭'],['poles','등산 스틱']]],
  ['camping','캠핑',[['tents','텐트'],['chairs','캠핑 의자'],['cookware','캠핑 취사도구']]],
  ['golf','골프',[['clubs','골프채'],['balls','골프공'],['bags','골프가방']]],
  ['cycling','자전거',[['bikes','자전거'],['parts','부품'],['accessories','자전거 용품']]]
 ])
];
export function categorySelection(params=new URLSearchParams()) {
 const root=taxonomy.find(x=>x.id===params.get('major'));
 const mid=root?.children.find(x=>x.id===params.get('middle'));
 const leaf=mid?.children.find(x=>x.id===params.get('minor'));
 return {major:root?.id||'',middle:mid?.id||'',minor:leaf?.id||''};
}
export function categoryTrail(selection) {
 const root=taxonomy.find(x=>x.id===selection.major);if(!root)return [];
 const mid=root.children.find(x=>x.id===selection.middle);if(!mid)return [root];
 const leaf=mid.children.find(x=>x.id===selection.minor);return leaf?[root,mid,leaf]:[root,mid];
}
const samplePaths={
 'p-menswear':['menswear','outerwear','padding'],'p-men-knit':['menswear','knitwear','round'],'p-men-shirt':['menswear','shirts','oxford'],'p-men-trousers':['menswear','pants','slacks'],'p-men-coat':['menswear','outerwear','coats'],'p-men-cardigan':['menswear','knitwear','cardigans'],
 'p-womenswear':['womenswear','knitwear','round'],'p-sportswear':['sports','fitness','sets'],'p-hikingwear':['sports','hiking','jackets'],
 'p-sneakers':['footwear','sneakers','casual'],'p-dress-shoes':['footwear','dress-shoes','derby'],'p-hikingboots':['footwear','outdoor','hiking'],
 'p-cap':['accessories','hats','baseball'],'p-hikinghat':['accessories','hats','hiking'],'p-silver-necklace':['jewelry','silver','necklaces'],'p-gold-ring':['jewelry','gold','rings'],
 'p-rice':['food','grains','rice'],'p-apples':['food','fruit','apples'],'p-kitchenware':['kitchen','cookware','utensils'],'p-tools':['tools','hand','sets'],
 'p-refurb-tv':['appliances','television','led'],'p-refurb-vacuum':['appliances','cleaning','stick'],'p-display-microwave':['appliances','kitchen','microwave']
};
export const productCategoryPath=p=>p.categoryPath||samplePaths[p.id]||[];
export function productInCategory(p,selection) {const ids=productCategoryPath(p);return (!selection.major||ids[0]===selection.major)&&(!selection.middle||ids[1]===selection.middle)&&(!selection.minor||ids[2]===selection.minor);}
export function categoryURL(selection,base='#/market',params=new URLSearchParams()) {
 const next=new URLSearchParams(params);for(const key of ['major','middle','minor']){next.delete(key);if(selection[key])next.set(key,selection[key]);}return base+(next.toString()?'?'+next.toString():'');
}
