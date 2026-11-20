import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const el=id=>document.getElementById(id),scene=new THREE.Scene();scene.background=new THREE.Color('#14202b');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.AgXToneMapping;renderer.toneMappingExposure=1.25;el('viewport').append(renderer.domElement);
const camera=new THREE.PerspectiveCamera(42,1,.05,200);let view='whole';
scene.add(new THREE.HemisphereLight(0xd2dfed,0x5a5248,1.8));const key=new THREE.DirectionalLight(0xffe8c5,2.3);key.position.set(0,18,-1);scene.add(key);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(35,35),new THREE.MeshStandardMaterial({color:0x41464b,roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.set(0,7.0,-11);scene.add(floor);
let manifest,sponsors,led,model,modelSceneCount=0,layout={},offset=0,paused=matchMedia('(prefers-reduced-motion: reduce)').matches,last=performance.now(),ready=false;
function resize(){renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;applyView(view);}
function applyView(which){view=which;if(which==='close'){camera.position.set(0,9.8,-4.8);camera.lookAt(0,9.7,-11);camera.fov=THREE.MathUtils.radToDeg(2*Math.atan(Math.max(1.1/6.2,2.38/(6.2*camera.aspect))));}else{camera.position.set(0,11,-1.5);camera.lookAt(0,11,-11);camera.fov=THREE.MathUtils.radToDeg(2*Math.atan(Math.max(4.55/9.5,4.05/(9.5*camera.aspect))));}camera.updateProjectionMatrix();}
function normalize(n){const p=sponsors?.periodCells||1;return((n%p)+p)%p;}
function setOffset(n){offset=normalize(n);if(led)led.uniforms.uOffset.value=offset;}
function setPaused(value){paused=value;el('pause').textContent=paused?'Play scroll':'Pause scroll';el('pause').setAttribute('aria-pressed',String(paused));last=performance.now();}
el('whole').onclick=()=>applyView('whole');el('close').onclick=()=>applyView('close');el('pause').onclick=()=>setPaused(!paused);el('sponsor').onchange=()=>setOffset(Number(el('sponsor').value));addEventListener('resize',resize);resize();
async function init(){
 manifest=await(await fetch('board.json')).json();sponsors=await(await fetch('sponsors.json')).json();
 for(const row of sponsors.logos){const option=document.createElement('option');option.value=row.startCell;option.textContent=row.name;el('sponsor').append(option);}el('count').textContent=sponsors.logoCount+' original sponsor marks';
 const atlas=await new THREE.TextureLoader().loadAsync('logo-strip.png');atlas.colorSpace=THREE.NoColorSpace;atlas.flipY=false;atlas.wrapS=atlas.wrapT=THREE.RepeatWrapping;atlas.magFilter=atlas.minFilter=THREE.NearestFilter;atlas.generateMipmaps=false;
 led=new THREE.ShaderMaterial({uniforms:{uAtlas:{value:atlas},uPeriod:{value:sponsors.periodCells},uOffset:{value:0}},vertexShader:`varying vec2 pixelUV;void main(){pixelUV=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,fragmentShader:`precision highp float;varying vec2 pixelUV;uniform sampler2D uAtlas;uniform float uPeriod;uniform float uOffset;void main(){vec2 grid=pixelUV*vec2(384.,64.);vec2 centre=floor(grid)+.5;float ink=texture2D(uAtlas,vec2((centre.x+uOffset)/uPeriod,centre.y/64.)).r;float radius=length(fract(grid)-.5);float diode=1.-smoothstep(.29,.43,radius);float halo=exp(-radius*radius*10.)*.08;vec3 c=vec3(1.,.035,.002)*((ink*7.+.008)*diode+ink*halo);gl_FragColor=vec4(c,1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`,toneMapped:true});
 const gltf=await new GLTFLoader().loadAsync('board.glb');modelSceneCount=gltf.scenes.length;model=gltf.scene;let faces=0;model.traverse(o=>{if(o.isMesh&&o.userData.ledScreen){o.material=led;faces++;}});if(faces!==1)throw Error('Expected one LED face, got '+faces);scene.add(model);model.updateMatrixWorld(true);model.traverse(o=>{if(o.userData.navigationLabel){const b=new THREE.Box3().setFromObject(o);layout[o.userData.navigationLabel]={minY:b.min.y,maxY:b.max.y};}});
 const spill=new THREE.PointLight(0xff2605,8,4,2);spill.position.set(0,9.6,-10.5);scene.add(spill);ready=true;el('status').hidden=true;setPaused(paused);
}
init().catch(e=>{el('status').textContent='The board could not load. Reload to retry.';window.previewError=String(e);console.error(e);});
function tick(now){requestAnimationFrame(tick);const seconds=Math.min((now-last)/1000,.1);last=now;if(ready&&!paused)setOffset(offset+seconds*sponsors.cellsPerSecond);renderer.render(scene,camera);}requestAnimationFrame(tick);
window.navigationPreview={stats:()=>({ready,view,paused,offsetCells:offset,periodCells:sponsors?.periodCells,logoCount:sponsors?.logoCount,modelSceneCount,layout,visibleLEDs:led?1:0,frame:Math.floor(offset)+1,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles}),setOffset,advance:seconds=>setOffset(offset+seconds*(sponsors?.cellsPerSecond||30)),pause:setPaused,view:applyView,dispose:()=>{model?.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});led?.uniforms.uAtlas.value.dispose();renderer.dispose();}};
