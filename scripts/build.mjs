import {cp,mkdir,rm} from 'node:fs/promises';
import {build} from 'esbuild';
await rm('dist',{recursive:true,force:true});await mkdir('dist',{recursive:true});
for(const p of ['index.html','operations.html','robots.txt','assets','js'])await cp(p,'dist/'+p,{recursive:true});
await build({entryPoints:{'operations-client':'src/operations.js'},bundle:true,format:'esm',outdir:'dist/js',minify:true,target:'es2022'});
console.log('Built storefront + authenticated operations. Server code and documents are excluded from static assets.');
