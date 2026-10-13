import {chromium} from 'playwright';
import {readFile,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
export const root=process.env.GULLYVERSE_ARTIFACT_ROOT||'reports/stage-2c1-geological-refinement-2026-10-13',base=process.env.GULLYVERSE_BASE_URL||'http://127.0.0.1:3000';
export const world=JSON.parse(await readFile('public/models/gullyverse/blockout.layout.json','utf8'));
export const launch=()=>chromium.launch({executablePath:'/usr/bin/chromium',headless:true});
export async function instrument(context){
 await context.route('**/api/**',r=>['GET','HEAD'].includes(r.request().method())?r.continue():r.abort());
 await context.addInitScript(()=>{
  window.__audit={contexts:[],tasks:[],createdVideos:[]};
  const get=HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext=function(type,...args){const gl=get.call(this,type,...args);if(gl&&['webgl','webgl2'].includes(type)&&!window.__audit.contexts.some(c=>c.gl===gl)){
   const stats={};for(const resource of ['Texture','Buffer','Program','Shader','Framebuffer','Renderbuffer','VertexArray','Query']){
    const make=gl['create'+resource]?.bind(gl),del=gl['delete'+resource]?.bind(gl);if(!make||!del)continue;const set=new WeakSet();stats[resource]={created:0,deleted:0,active:0};
    gl['create'+resource]=function(...a){const o=make(...a);if(o){set.add(o);stats[resource].created++;stats[resource].active++;}return o;};
    gl['delete'+resource]=function(o){if(o&&set.has(o)){set.delete(o);stats[resource].deleted++;stats[resource].active--;}return del(o);};
   }
   const ext=gl.getExtension('WEBGL_debug_renderer_info');window.__audit.contexts.push({gl,stats,renderer:gl.getParameter(ext?ext.UNMASKED_RENDERER_WEBGL:gl.RENDERER),vendor:gl.getParameter(ext?ext.UNMASKED_VENDOR_WEBGL:gl.VENDOR),attributes:gl.getContextAttributes(),extensions:gl.getSupportedExtensions()});
  }return gl;};
  const create=Document.prototype.createElement;Document.prototype.createElement=function(tag,...args){const el=create.call(this,tag,...args);if(tag.toLowerCase()==='video')window.__audit.createdVideos.push(new WeakRef(el));return el;};
  new PerformanceObserver(l=>window.__audit.tasks.push(...l.getEntries().map(e=>({at:e.startTime,ms:e.duration})))).observe({type:'longtask',buffered:true});
 });
}
export async function snapshot(page){return page.evaluate(()=>{const d=window.__gullyverse,r=d?.runtime||window.__auditRuntime;return{snapshot:r?.getSnapshot(),pose:r?{...r.pose}:null,renderer:d?.renderer,stats:d?.stats,memory:d?.memory.at(-1),gpuTimer:d?.gpuTimer,canvasCount:document.querySelectorAll('canvas').length,contexts:window.__audit.contexts.map(c=>({renderer:c.renderer,vendor:c.vendor,attributes:c.attributes,stats:c.stats,extensions:c.extensions,lost:c.gl.isContextLost()})),videos:window.__audit.createdVideos.map(v=>v.deref()).filter(Boolean).map(v=>({src:v.getAttribute('src'),time:v.currentTime,paused:v.paused,readyState:v.readyState,connected:v.isConnected})),viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio}};});}
export async function local(page,id){await page.waitForFunction(id=>{if(window.__gullyverse?.runtime)window.__auditRuntime=window.__gullyverse.runtime;const s=window.__auditRuntime?.getSnapshot();return s&&(s.phase==='error'||s.phase==='local'&&s.scene===id);},id,{timeout:100000});const s=await snapshot(page);assert.notEqual(s.snapshot.phase,'error',s.snapshot.error||'Failed scene');}
export async function map(page,id){await page.getByRole('button',{name:/^Map/}).click();await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',null,{timeout:30000});await page.getByRole('button',{name:id==='hub'?'Gullyverse hub':'Aftermovie',exact:true}).click();await local(page,id);}
export const pose=page=>page.evaluate(()=>({...window.__gullyverse.runtime.pose}));
export async function look(page,target){const p=await pose(page);let left=Math.atan2(Math.sin(Math.atan2(-(target[0]-p.x),-(target[2]-p.z))-p.yaw),Math.cos(Math.atan2(-(target[0]-p.x),-(target[2]-p.z))-p.yaw));while(Math.abs(left)>.001){const turn=Math.max(-.5,Math.min(.5,left));await page.mouse.move(600,300);await page.mouse.down();await page.mouse.move(600-turn/.003,300,{steps:3});await page.mouse.up();left-=turn;}}
export async function key(page,code,ms){await page.keyboard.down(code);await page.waitForTimeout(ms);await page.keyboard.up(code);}
export async function save(name,value){await writeFile(root+'/raw/'+name,JSON.stringify(value,null,2));}
