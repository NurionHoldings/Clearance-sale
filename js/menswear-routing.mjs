const decode=value=>{try{return decodeURIComponent(value||'')}catch{return ''}};
export const menswearCollectionPath='#/menswear';
export const menswearCategoryPath='#/menswear/clothing';
export const menswearSamplesPath='#/menswear/samples';
export const menswearVendorPath=id=>menswearCategoryPath+'/vendor/'+encodeURIComponent(id);
export function menswearRoute(hash) {
 const [path,query='']=hash.split('?'),parts=path.replace(/^#\/?/,'').split('/').filter(Boolean),params=new URLSearchParams(query);
 const suffix=params.toString()?'?'+params.toString():'';
 if(parts[1]==='product')return {level:'product',isSample:true,productId:decode(parts[2]),base:menswearSamplesPath,canonical:menswearSamplesPath+'/product/'+encodeURIComponent(decode(parts[2]))+suffix};
 if(parts[1]==='samples')return {level:parts[2]==='product'?'product':'samples',isSample:true,productId:decode(parts[3]),base:menswearSamplesPath,canonical:path+suffix};
 if(parts[1]==='clothing'&&parts[2]==='vendor') {const vendorId=decode(parts[3]);return {level:parts[4]==='product'?'product':'vendor',vendorId,productId:decode(parts[5]),base:menswearVendorPath(vendorId),canonical:path+suffix};}
 if(parts[1]==='clothing')return {level:'category',base:menswearCategoryPath,canonical:menswearCategoryPath+suffix};
 const legacyVendor=params.get('vendor');
 if(legacyVendor&&legacyVendor!=='all'){params.delete('vendor');const q=params.toString();return {level:'vendor',vendorId:legacyVendor,base:menswearVendorPath(legacyVendor),canonical:menswearVendorPath(legacyVendor)+(q?'?'+q:'')};}
 return {level:'collection',base:menswearCollectionPath,canonical:menswearCollectionPath};
}
