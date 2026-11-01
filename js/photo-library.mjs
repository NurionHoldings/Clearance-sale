// Central image assignments. Replace the local file or change the key here.
// These editorial stock photographs are not actual merchant inventory.
export const categoryPhotos = Object.freeze({
 menswear:'shirt', womenswear:'fashion', footwear:'shoes', accessories:'bag',
 watches:'watch', jewelry:'jewelry', appliances:'appliances', home:'furniture',
 kitchen:'kitchen', food:'food', sports:'sports', tools:'tools'
});
export const productPhotos = Object.freeze({
 'p-men-knit':'knit', 'p-men-shirt':'shirt', 'p-men-coat':'coat'
});
const labels = {
 knit:'접힌 니트의 질감', fashion:'옷걸이에 정리된 의류', shoes:'브라운 가죽 구두',
 bag:'브라운 가죽 가방', watch:'가죽 스트랩 시계', jewelry:'주얼리 스타일링',
 appliances:'가전이 배치된 주방과 거실', furniture:'가죽 소파', kitchen:'주방용품',
 food:'신선한 과일과 채소', sports:'운동용 덤벨', shirt:'옷걸이에 걸린 셔츠', coat:'걸려 있는 베이지 코트', tools:'수공구가 담긴 공구함'
};
export function photo(key, eager = false) {
 if (!Object.hasOwn(labels,key)) return '';
 return `<img class="market-photo" src="assets/photos/${key}.webp" alt="${labels[key]} · 연출 이미지" loading="${eager?'eager':'lazy'}" decoding="async" width="640" height="640"${eager?' fetchpriority="high"':''}>`;
}
