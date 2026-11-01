// Reveal the final category's product panel, including an explicit empty state.
export function revealSelectedProducts(view) {
 requestAnimationFrame(()=>{
  const target=view==='market'?document.querySelector('.home-products-heading'):view==='menswear'?document.querySelector('#mwSelectedProducts')||document.querySelector('#mwCatalog'):view==='arirang'?document.querySelector('#arirang .ar-products'):null;
  if(!target||!target.getClientRects().length)return;
  target.scrollIntoView({behavior:'instant',block:'start'});
  const heading=target.querySelector('h2');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}
 });
}
