import * as THREE from "three";

let fonts: { ready:boolean; promise:Promise<void>; error?:unknown } | undefined;
/** Suspend the complete critical scene until the repository's paint fonts are usable. */
export function requireWorldFonts() {
  if(!fonts) {
    const state={ready:false,promise:Promise.resolve(),error:undefined as unknown};
    state.promise=Promise.all([
      new FontFace("GullyversePaint","url('/fonts/Fatal%20Fighter.ttf')").load(),
    ]).then(loaded=>{loaded.forEach(font=>document.fonts.add(font));state.ready=true;}).catch(error=>{state.error=error;state.ready=true;});
    fonts=state;
  }
  if(!fonts.ready) throw fonts.promise;
  if(fonts.error) throw fonts.error;
}
function random(seed:number) {let n=seed;return ()=>{n=(n*1664525+1013904223)>>>0;return n/4294967296;};}
function texture(canvas:HTMLCanvasElement) {const t=new THREE.CanvasTexture(canvas);t.colorSpace=THREE.SRGBColorSpace;return t;}
function surfaceCanvas(kind:"rock"|"ground") {
  const canvas=document.createElement("canvas");canvas.width=canvas.height=512;
  const ctx=canvas.getContext("2d")!,data=ctx.createImageData(512,512),rnd=random(kind==="rock"?941:278);
  for(let y=0;y<512;y++) for(let x=0;x<512;x++) {
    const i=(y*512+x)*4;
    const grain=(rnd()-.5)*24;
    const broad=kind==="rock"?Math.sin(x*.07+Math.sin(y*.045)*3)*5+Math.cos(y*.021)*4:Math.sin(x*.019)*Math.sin(y*.023)*2;
    const value=(kind==="rock"?202:193)+grain+broad;
    data.data[i]=value+(kind==="rock"?0:11);data.data[i+1]=value-2;data.data[i+2]=value-(kind==="rock"?5:19);data.data[i+3]=255;
  }
  ctx.putImageData(data,0,0);
  if(kind==="rock") {
    // Short branching fissures; periodic copies make the canvas tile continuously.
    for(let j=0;j<72;j++) {
      const x=rnd()*512,y=rnd()*512,length=15+rnd()*105,slant=(rnd()-.5)*.7;
      for(const ox of [-512,0,512]) for(const oy of [-512,0,512]) {
        ctx.strokeStyle=`rgba(49,51,50,${.12+rnd()*.22})`;ctx.lineWidth=.5+rnd()*1.4;ctx.beginPath();ctx.moveTo(x+ox,y+oy);
        for(let k=1;k<7;k++) ctx.lineTo(x+ox+slant*length*k/6+Math.sin(k*2+j)*3,y+oy+length*k/6);
        ctx.stroke();
      }
    }
  } else {
    for(let i=0;i<11000;i++) {const x=rnd()*512,y=rnd()*512,r=.3+rnd()*1.1;ctx.fillStyle=i%3?"#b1a99d55":"#4a4a4044";ctx.beginPath();ctx.ellipse(x,y,r,r*.65,rnd()*3,0,Math.PI*2);ctx.fill();}
  }
  const t=texture(canvas);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=2;return t;
}
export const makeRockTexture=()=>surfaceCanvas("rock");
export const makeGroundTexture=()=>surfaceCanvas("ground");
function crown(ctx:CanvasRenderingContext2D,x:number,y:number,size:number) {
  ctx.strokeStyle="#d4ad42";ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(x-size*.5,y+size*.4);ctx.lineTo(x-size*.7,y-size*.3);ctx.lineTo(x-size*.15,y);ctx.lineTo(x,y-size*.6);ctx.lineTo(x+size*.2,y);ctx.lineTo(x+size*.65,y-size*.35);ctx.lineTo(x+size*.4,y+size*.35);ctx.closePath();ctx.stroke();
}
function orbit(ctx:CanvasRenderingContext2D,x:number,y:number,size:number) {
  ctx.strokeStyle="#e5e0d2";ctx.lineWidth=3;ctx.beginPath();ctx.arc(x,y,size*.4,0,Math.PI*2);ctx.stroke();
  for(const scale of [.45,.8]) {ctx.beginPath();ctx.ellipse(x,y,size*.4*scale,size*.4,0,0,Math.PI*2);ctx.stroke();}
  ctx.beginPath();ctx.ellipse(x,y,size*.59,size*.14,-.35,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(x,y-size*.5);ctx.lineTo(x,y+size*.5);ctx.stroke();
}
export function makeBoardTexture(label:string,color:string,arrow?:readonly number[]) {
  const hero=label==="GULLYVERSE",canvas=document.createElement("canvas");canvas.width=hero?1024:512;canvas.height=hero?256:128;
  const ctx=canvas.getContext("2d")!,w=canvas.width,h=canvas.height,rnd=random(label.length*113+label.charCodeAt(0));
  ctx.fillStyle="#20211f";ctx.fillRect(0,0,w,h);
  for(let i=0;i<650;i++) {ctx.fillStyle=i%3?"#a79b7344":"#01050744";ctx.fillRect(rnd()*w,rnd()*h,rnd()*11+1,rnd()*3+1);}
  // Uneven scraped metal edge, without a clean graphic frame.
  for(let i=0;i<100;i++) {ctx.fillStyle="#bca879";const x=rnd()*w,y=rnd()<.5?rnd()*6:h-rnd()*6;ctx.fillRect(x,y,rnd()*8+1,rnd()*3+1);}
  for(const x of [9,w-9]) for(const y of [9,h-9]) {ctx.fillStyle="#bcb09a";ctx.beginPath();ctx.arc(x,y,3,0,Math.PI*2);ctx.fill();}
  ctx.textBaseline="middle";ctx.textAlign="center";
  if(hero) {
    orbit(ctx,94,128,145);crown(ctx,290,33,48);
    ctx.save();ctx.translate(590,113);ctx.rotate(-.035);ctx.font="156px GullyversePaint";ctx.fillStyle="#ece7db";ctx.fillText("GULLYVERSE",0,0,805);ctx.restore();
    ctx.save();ctx.translate(702,213);ctx.rotate(-.035);ctx.fillStyle="#d4ad42";ctx.fillRect(-221,-31,442,63);ctx.fillStyle="#1b1c18";ctx.font="60px GullyversePaint";ctx.fillText("BREEZE 2027",0,0,422);ctx.restore();
  } else {
    const hasArrow=!!arrow,side=arrow&&arrow[0]>Math.abs(arrow[1])*.3?1:-1;
    const cx=hasArrow?(side<0?w*.6:w*.41):w*.5,maxWidth=hasArrow?w*.75:w*.92;
    ctx.font="900 97px 'Arial Narrow',Arial,sans-serif";ctx.fillStyle=color;ctx.fillText(label,cx,h*.54,maxWidth);
    if(arrow) {
      ctx.save();ctx.translate(side<0?w*.1:w*.9,h*.5);ctx.rotate(Math.atan2(arrow[1],arrow[0]));
      ctx.strokeStyle=color;ctx.lineWidth=11;ctx.lineCap="square";ctx.lineJoin="miter";
      ctx.beginPath();ctx.moveTo(-25,0);ctx.lineTo(25,0);ctx.moveTo(3,-24);ctx.lineTo(27,0);ctx.lineTo(3,24);ctx.stroke();ctx.restore();
    }
  }
  // Missing paint is irregular and sparse enough to preserve reading.
  ctx.globalCompositeOperation="source-over";ctx.fillStyle="#292a2555";
  for(let i=0;i<250;i++) ctx.fillRect(rnd()*w,rnd()*h,rnd()*3+.4,rnd()*4+.4);
  return texture(canvas);
}
export function makeGraffitiTexture(label:string,color:string,seed:number) {
  const canvas=document.createElement("canvas");canvas.width=512;canvas.height=128;
  const ctx=canvas.getContext("2d")!,rnd=random(seed);
  ctx.scale(.5,.5);
  ctx.textAlign="center";ctx.textBaseline="middle";ctx.font="156px GullyversePaint";
  ctx.fillStyle=color;ctx.shadowColor=color;ctx.shadowBlur=2;
  ctx.save();ctx.translate(512,127);ctx.rotate((rnd()-.5)*.035);ctx.fillText(label,0,0,950);ctx.restore();ctx.shadowBlur=0;
  // Spray grain, chipped paint and a few paint runs are transparent over real rock.
  ctx.globalCompositeOperation="destination-out";
  for(let i=0;i<1400;i++) {ctx.fillStyle=`rgba(0,0,0,${rnd()*.85})`;ctx.fillRect(rnd()*1024,rnd()*256,.5+rnd()*3,.5+rnd()*3);}
  ctx.globalCompositeOperation="source-over";ctx.fillStyle=color;ctx.globalAlpha=.18;
  for(let i=0;i<100;i++) {const x=64+rnd()*896,y=75+rnd()*95;ctx.beginPath();ctx.arc(x,y,rnd()*1.4+.3,0,Math.PI*2);ctx.fill();}
  return texture(canvas);
}
