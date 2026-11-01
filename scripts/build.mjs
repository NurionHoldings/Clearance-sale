import {createHash} from 'node:crypto';
import {cp,mkdir,rm,readFile,writeFile} from 'node:fs/promises';
import {build} from 'esbuild';
await rm('dist',{recursive:true,force:true});await mkdir('dist',{recursive:true});
for(const p of ['index.html','operations.html','live.html','robots.txt','assets','js'])await cp(p,'dist/'+p,{recursive:true});
const manifest=JSON.parse(await readFile('media-source/background-music/manifest.json','utf8'));
const parts=[];
for(const part of manifest.parts){
 const bytes=await readFile('media-source/background-music/'+part.file);
 if(bytes.length!==part.size||createHash('sha256').update(bytes).digest('hex')!==part.sha256)throw new Error('Audio source integrity failure: '+part.file);
 parts.push(bytes);
}
const music=Buffer.concat(parts);
if(music.length!==manifest.size||createHash('sha256').update(music).digest('hex')!==manifest.sha256)throw new Error('Audio integrity failure');
await mkdir('dist/assets/audio',{recursive:true});await writeFile('dist/assets/audio/'+manifest.file,music);
await build({entryPoints:{'operations-client':'src/operations.js'},bundle:true,format:'esm',outdir:'dist/js',minify:true,target:'es2022'});
console.log('Built storefront + authenticated operations. Server code and documents are excluded from static assets.');
