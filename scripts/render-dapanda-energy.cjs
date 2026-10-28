/** Render ARKAON V12-inspired energy motion on the approved alpha logo.
 * npm install --no-save @napi-rs/canvas; requires ffmpeg on PATH.
 * node scripts/render-dapanda-energy.cjs [output.webm]
 * Only the user-owned brand art is drawn; no reference-video pixels are reused.
 */
const { createCanvas, loadImage } = require('@napi-rs/canvas');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const path = require('node:path');
const W=1280,H=720,FPS=24,DURATION=8;
const root=path.resolve(__dirname,'..');
const output=process.argv[2]||path.join(root,'assets/video/dapanda-energy-alpha.webm');
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
function flare(c,x,y,s,color,a){
 c.save();c.globalAlpha*=a;c.globalCompositeOperation='screen';
 const g=c.createRadialGradient(x,y,0,x,y,s*3);g.addColorStop(0,'#ffffff');g.addColorStop(.1,color);g.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=g;c.fillRect(x-s*3,y-s*3,s*6,s*6);
 c.strokeStyle='#fff4d8';c.lineWidth=.7;c.beginPath();c.moveTo(x-s*2,y);c.lineTo(x+s*2,y);c.moveTo(x,y-s*2);c.lineTo(x,y+s*2);c.stroke();c.restore();
}
function orbit(c,cx,cy,rx,ry,tilt,t,color,index){
 c.save();c.translate(cx,cy);c.rotate(tilt);c.strokeStyle=color;c.globalAlpha*=.45;c.lineWidth=.8;c.beginPath();c.ellipse(0,0,rx,ry,0,0,Math.PI*2);c.stroke();c.restore();
 const phase=t*(.65+index*.1)+index*2.2;
 for(let k=0;k<36;k++){
  const theta=phase-k*.022;
  const px=rx*Math.cos(theta),py=ry*Math.sin(theta);
  const x=cx+px*Math.cos(tilt)-py*Math.sin(tilt),y=cy+px*Math.sin(tilt)+py*Math.cos(tilt);
  c.save();c.globalAlpha*=Math.pow(1-k/36,2)*.9;c.fillStyle=color;c.shadowBlur=k?4:16;c.shadowColor=color;c.beginPath();c.arc(x,y,k?1.1:3.4,0,Math.PI*2);c.fill();c.restore();
  if(k===0)flare(c,x,y,5,color,.75);
 }
}
(async()=>{
 const logo=await loadImage(path.join(root,'assets/dapanda-logo-transparent.png'));
 const canvas=createCanvas(W,H),c=canvas.getContext('2d');
 const shine=createCanvas(logo.width,logo.height),s=shine.getContext('2d');
 // A light adaptation for the small navy lettering on a dark cinematic backdrop.
 const textLight=createCanvas(logo.width,logo.height),l=textLight.getContext('2d');
 l.drawImage(logo,0,0);l.globalCompositeOperation='source-in';l.fillStyle='#f2ddba';
 l.beginPath();l.rect(0,logo.height*.78,logo.width*.36,logo.height*.22);l.rect(logo.width*.36,logo.height*.67,logo.width*.64,logo.height*.15);l.fill();
 const ff=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgba','-s',`${W}x${H}`,'-r',String(FPS),'-i','pipe:0','-an','-c:v','libvpx-vp9','-pix_fmt','yuva420p','-b:v','0','-crf','30','-deadline','good','-cpu-used','4','-row-mt','1','-auto-alt-ref','0',output],{stdio:['pipe','ignore','inherit']});
 const done=once(ff,'close');
 for(let n=0;n<FPS*DURATION;n++){
  const t=n/FPS,alpha=ease(t/1.6);
  c.clearRect(0,0,W,H);c.save();c.globalAlpha=alpha;
  // Three luminous orbital planes echo the reference's continuous energy flow.
  orbit(c,640,352,535,218,-.07,t,'#6edbff',0);
  orbit(c,640,355,528,163,.14,t,'#efc88a',1);
  orbit(c,340,355,182,154,-.24,t,'#9cbbff',2);
  // Curved gold/blue ribbons behind the artwork, with a moving current.
  for(let j=0;j<2;j++){
   c.save();c.globalAlpha*=.35;c.strokeStyle=j?'#e6b876':'#65c8f7';c.lineWidth=1.1;c.shadowBlur=9;c.shadowColor=c.strokeStyle;c.beginPath();
   for(let x=80;x<=1200;x+=8){const y=350+Math.sin(x/170+t*.6+j*2.2)*(92+j*25);if(x===80)c.moveTo(x,y);else c.lineTo(x,y);}c.stroke();c.restore();
  }
  // Tiny satellites and glimmering particles, deterministic and reproducible.
  for(let i=0;i<42;i++){
   const a=i*2.39996+t*(i%2?-.07:.07),r=410+(i%7)*18;
   const x=640+Math.cos(a)*r,y=355+Math.sin(a)*(180+i%5*9);
   const pulse=.18+.55*Math.pow((Math.sin(t*2+i*1.7)+1)/2,5);
   c.save();c.globalAlpha*=pulse;c.fillStyle=i%3?'#99dfff':'#ffe1a3';c.fillRect(x,y,i%4?1.2:2.1,i%4?1.2:2.1);c.restore();
  }
  // Logo softly settles into place, then breathes as in the reference.
  const scale=.86+.14*ease(t/2.7)+.006*Math.sin(t*1.7);
  const w=1050*scale,h=w*logo.height/logo.width,x=(W-w)/2,y=(H-h)/2;
  c.save();c.shadowColor='#b88847';c.shadowBlur=8+3*Math.sin(t*1.4);c.drawImage(logo,x,y,w,h);c.restore();
  c.save();c.globalAlpha*=.93;c.drawImage(textLight,x,y,w,h);c.restore();
  // The sweep is alpha-masked to the artwork; no rectangular matte is introduced.
  s.clearRect(0,0,shine.width,shine.height);s.globalCompositeOperation='source-over';s.drawImage(logo,0,0);s.globalCompositeOperation='source-in';
  const sx=((t*.32)%1.6-.3)*logo.width;const g=s.createLinearGradient(sx-100,0,sx+100,logo.height*.2);g.addColorStop(0,'rgba(255,255,255,0)');g.addColorStop(.5,'rgba(211,242,255,.7)');g.addColorStop(1,'rgba(255,255,255,0)');s.fillStyle=g;s.fillRect(0,0,shine.width,shine.height);
  c.save();c.globalCompositeOperation='screen';c.globalAlpha*=.7;c.drawImage(shine,x,y,w,h);c.restore();
  for(const [u,v,phase] of [[.074,.2,0],[.35,.22,2],[.54,.6,4],[.9,.3,1],[.2,.68,3]]){
   const pulse=Math.pow((Math.sin(t*2+phase)+1)/2,7);flare(c,x+w*u,y+h*v,5+pulse*4,'#ffe3b1',.15+.75*pulse);
  }
  // Arc scanning inside the iridescent tile, confined around the bag handle.
  c.save();c.translate(x+w*.2,y+h*.42);c.strokeStyle='#b5efff';c.lineWidth=.9;c.globalAlpha*=.35;c.shadowBlur=8;c.shadowColor='#66d8ff';c.beginPath();c.ellipse(0,0,w*.085,h*.17,0,t*1.2,t*1.2+1.4);c.stroke();c.restore();
  c.restore();
  const bytes=Buffer.from(c.getImageData(0,0,W,H).data);
  if(!ff.stdin.write(bytes))await once(ff.stdin,'drain');
  if(n%48===0)process.stdout.write(`frame ${n}/${FPS*DURATION}\n`);
 }
 ff.stdin.end();const [code]=await done;if(code)throw Error(`ffmpeg exited ${code}`);
 console.log(output);
})().catch(e=>{console.error(e);process.exitCode=1});
