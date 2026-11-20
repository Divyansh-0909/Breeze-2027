import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
const motionPreference=matchMedia('(prefers-reduced-motion: reduce)');
const query=new URLSearchParams(location.search),mobile=query.has('mobile'),el=id=>document.getElementById(id);
const scene=new THREE.Scene(),config=await(await fetch('cameras.json')).json();
const fogColor=new THREE.Color().setRGB(...config.fogLinearColor);scene.background=fogColor;scene.fog=new THREE.FogExp2(fogColor,config.fogDensity);
const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setPixelRatio(mobile?Math.min(devicePixelRatio,.85):Math.min(devicePixelRatio,1));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.AgXToneMapping;renderer.toneMappingExposure=1.15;el('viewport').append(renderer.domElement);
const camera=new THREE.PerspectiveCamera(50,1,.08,160);let view='far',fogOn=true,paused=motionPreference.matches,ready=false,last=performance.now(),offset=0,led,model;
const convert=a=>new THREE.Vector3(a[0],a[2],-a[1]);
scene.add(new THREE.HemisphereLight(0x8badd8,0x3e342c,.24));
const moon=new THREE.DirectionalLight(0x779ac6,.18);moon.position.set(-10,30,2);scene.add(moon);
// Three practical pools, no runtime shadow maps. The floor carries baked shadows.
for(const [p,w] of [[[-3.33,-7,8.85],27],[[-3.33,2,9.3],18],[[3.33,-16,8.7],30]]){const l=new THREE.PointLight(0xffac57,w,11,2);l.position.copy(convert(p));scene.add(l);}
const board=new THREE.PointLight(0xffd6a0,55,10,2);board.position.copy(convert([0,9.9,14.776]));scene.add(board);
function setCamera(key){view=key;const c=config.cameras.find(x=>x.key===key);camera.position.copy(convert(c.position));camera.lookAt(convert(c.target));camera.aspect=innerWidth/innerHeight;camera.fov=THREE.MathUtils.radToDeg(2*Math.atan(Math.tan(THREE.MathUtils.degToRad(c.fovDegrees)/2)/camera.aspect));camera.updateProjectionMatrix();for(const b of document.querySelectorAll('[data-camera]'))b.setAttribute('aria-pressed',String(b.dataset.camera===key));}
function resize(){renderer.setSize(innerWidth,innerHeight);setCamera(view);}addEventListener('resize',resize);resize();
function setFog(on){fogOn=on;scene.fog.density=on?config.fogDensity:0;el('haze').textContent=on?'Mist on':'Mist off';el('haze').setAttribute('aria-pressed',String(on));}
function setPaused(on){paused=on;el('pause').textContent=on?'Play signs':'Pause signs';el('pause').setAttribute('aria-pressed',String(on));}
document.querySelectorAll('[data-camera]').forEach(b=>b.onclick=()=>setCamera(b.dataset.camera));el('haze').onclick=()=>setFog(!fogOn);el('pause').onclick=()=>setPaused(!paused);motionPreference.addEventListener('change',e=>setPaused(e.matches));setPaused(paused);
const gl=renderer.getContext(),timer=gl.getExtension('EXT_disjoint_timer_query_webgl2'),queries=[],gpu=[],frames=[],cpu=[];let collecting=false,frameAt=null,benchmarking=false;
const capabilities={webgl2:renderer.capabilities.isWebGL2,maxTextureSize:renderer.capabilities.maxTextureSize,astc:!!gl.getExtension('WEBGL_compressed_texture_astc'),s3tc:!!gl.getExtension('WEBGL_compressed_texture_s3tc'),etc:!!gl.getExtension('WEBGL_compressed_texture_etc'),gpuTimer:!!timer,renderer:gl.getParameter(gl.getExtension('WEBGL_debug_renderer_info')?.UNMASKED_RENDERER_WEBGL??gl.RENDERER)};
function tick(now){requestAnimationFrame(tick);const dt=Math.min((now-last)/1000,.1);last=now;if(document.hidden||benchmarking)return;if(ready&&!paused){offset=(offset+dt*30)%10676;if(led)led.uniforms.uOffset.value=offset;}
 if(collecting&&frameAt!==null)frames.push(now-frameAt);if(collecting)frameAt=now;
 while(queries.length&&gl.getQueryParameter(queries[0],gl.QUERY_RESULT_AVAILABLE)){const q=queries.shift();if(!gl.getParameter(timer.GPU_DISJOINT_EXT))gpu.push(gl.getQueryParameter(q,gl.QUERY_RESULT)/1e6);gl.deleteQuery(q);}
 const q=collecting&&timer?gl.createQuery():null;if(q)gl.beginQuery(timer.TIME_ELAPSED_EXT,q);const start=performance.now();renderer.render(scene,camera);if(collecting)cpu.push(performance.now()-start);if(q){gl.endQuery(timer.TIME_ELAPSED_EXT);queries.push(q);}}
requestAnimationFrame(tick);
let stats={};
async function init(){
 const started=performance.now();const loader=new GLTFLoader(),draco=new DRACOLoader();draco.setDecoderPath('/vendor/three/examples/jsm/libs/draco/gltf/');loader.setDRACOLoader(draco);
 const asset=query.has('draco')?'pilot-draco.glb':'pilot.glb';const gltf=await loader.loadAsync(asset);model=gltf.scene;scene.add(model);model.updateMatrixWorld(true);
 const lightmap=await new THREE.TextureLoader().loadAsync('textures/ground-lightmap.png');lightmap.flipY=false;lightmap.colorSpace=THREE.NoColorSpace;lightmap.channel=1;
 // A cheap baked roughness tile; no runtime procedural noise or SSR.
 const rough=await new THREE.TextureLoader().loadAsync('textures/damp-roughness.png');rough.colorSpace=THREE.NoColorSpace;rough.wrapS=rough.wrapT=THREE.RepeatWrapping;rough.channel=0;rough.repeat.set(.125,.125);
 let lightmapMeshes=0,lightmapUVFailures=0,ledFaces=0;const mats=new Set(),textures=new Set();
 const atlas=await new THREE.TextureLoader().loadAsync('logo-strip-0.png');const atlas1=await new THREE.TextureLoader().loadAsync('logo-strip-1.png');atlas1.colorSpace=THREE.NoColorSpace;atlas1.flipY=false;atlas1.wrapS=atlas1.wrapT=THREE.ClampToEdgeWrapping;atlas1.magFilter=atlas1.minFilter=THREE.NearestFilter;atlas1.generateMipmaps=false;atlas.colorSpace=THREE.NoColorSpace;atlas.flipY=false;atlas.wrapS=atlas.wrapT=THREE.RepeatWrapping;atlas.magFilter=atlas.minFilter=THREE.NearestFilter;atlas.generateMipmaps=false;
 led=new THREE.ShaderMaterial({fog:true,uniforms:{...THREE.UniformsLib.fog,uAtlas:{value:atlas},uAtlas1:{value:atlas1},uOffset:{value:0}},vertexShader:`varying vec2 pixelUV;
 #include <fog_pars_vertex>
 void main(){pixelUV=uv;vec4 mvPosition=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*mvPosition;
 #include <fog_vertex>
 }`,fragmentShader:`varying vec2 pixelUV;uniform sampler2D uAtlas;uniform sampler2D uAtlas1;uniform float uOffset;
 #include <fog_pars_fragment>
 void main(){vec2 grid=pixelUV*vec2(384.,64.);vec2 centre=floor(grid)+.5;float cell=mod(centre.x+uOffset,10676.);float ink=cell<5338.?texture2D(uAtlas,vec2(cell/5338.,centre.y/64.)).r:texture2D(uAtlas1,vec2((cell-5338.)/5338.,centre.y/64.)).r;float radius=length(fract(grid)-.5);float diode=1.-smoothstep(.29,.43,radius);gl_FragColor=vec4(vec3(1.,.035,.002)*((ink*5.+.008)*diode),1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 #include <fog_fragment>
 }`});
 model.traverse(o=>{if(!o.isMesh)return;o.frustumCulled=true;o.castShadow=false;o.receiveShadow=false;
  if(o.userData.ledScreen){const old=o.material;o.material=led;old.dispose();ledFaces++;}
  for(const m of Array.isArray(o.material)?o.material:[o.material]){mats.add(m);m.fog=true;if(m.userData?.groundLightmap){if(!o.geometry.getAttribute('uv1'))lightmapUVFailures++;m.aoMap=null;m.lightMap=lightmap;m.lightMapIntensity=1.4;lightmapMeshes++;}if(m.userData?.dampFloor){m.roughnessMap=rough;m.roughness=1;m.normalScale?.set(.015,.015);}for(const value of Object.values(m))if(value?.isTexture)textures.add(value);if(m.isShaderMaterial)for(const u of Object.values(m.uniforms))if(u.value?.isTexture)textures.add(u.value);m.needsUpdate=true;}});
 if(ledFaces!==1)throw Error('Expected exactly one LED face; got '+ledFaces);if(lightmapUVFailures)throw Error('Missing second UV for lightmap');
 const compileAt=performance.now();await renderer.compileAsync(scene,camera);const compileMs=performance.now()-compileAt;renderer.render(scene,camera);
 let textureBytes=0;for(const t of textures){const im=t.image;if(im?.width)textureBytes+=im.width*im.height*4*(t.generateMipmaps?4/3:1);}
 const geo=new Set();let geometryBytes=0,totalTriangles=0;model.traverse(o=>{if(o.isMesh&&!geo.has(o.geometry)){geo.add(o.geometry);for(const a of Object.values(o.geometry.attributes))geometryBytes+=a.array.byteLength;if(o.geometry.index)geometryBytes+=o.geometry.index.array.byteLength;totalTriangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;}});
 stats={asset,loadAndCompileMs:performance.now()-started,compileMs,modelScenes:gltf.scenes.length,lightmapMeshes,lightmapUVFailures,ledFaces,textureBytesEstimate:Math.round(textureBytes),geometryBytes,totalTriangles,materials:mats.size,capabilities,source:'Rev15O → isolated Rev15P pilot',fogDensity:config.fogDensity};draco.dispose();ready=true;el('status').hidden=true;
}
window.pilot={ready:()=>ready,view:setCamera,fog:setFog,pause:setPaused,offset:n=>{offset=n;if(led)led.uniforms.uOffset.value=n;},capture:on=>document.body.classList.toggle('capture',on),stats:()=>({...stats,view,fogOn,paused,offset,canvases:document.querySelectorAll('canvas').length,drawCalls:renderer.info.render.calls,visibleTriangles:renderer.info.render.triangles,rendererTextures:renderer.info.memory.textures,shaderPrograms:renderer.info.programs?.length}),benchmark:async(count=6)=>{benchmarking=true;const frames=[],cpu=[],gpu=[];let previous=null;for(let i=0;i<count;i++){await new Promise(requestAnimationFrame);const begin=performance.now();if(previous!==null)frames.push(begin-previous);previous=begin;const q=timer?gl.createQuery():null;if(q)gl.beginQuery(timer.TIME_ELAPSED_EXT,q);const start=performance.now();renderer.render(scene,camera);cpu.push(performance.now()-start);if(q)gl.endQuery(timer.TIME_ELAPSED_EXT);gl.finish();await new Promise(r=>setTimeout(r,25));if(q){if(gl.getQueryParameter(q,gl.QUERY_RESULT_AVAILABLE)&&!gl.getParameter(timer.GPU_DISJOINT_EXT))gpu.push(gl.getQueryParameter(q,gl.QUERY_RESULT)/1e6);gl.deleteQuery(q);}}benchmarking=false;return{frames,cpu,gpu,...window.pilot.stats()};},measureStart:()=>{frames.length=cpu.length=gpu.length=0;frameAt=null;collecting=true;},measureStop:()=>{collecting=false;frameAt=null;return{frames:[...frames],cpu:[...cpu],gpu:[...gpu],...window.pilot.stats()};}};
init().catch(e=>{window.pilotError=String(e);console.error(e);el('status').textContent='The view could not load. Festival directions are still available below.';});
