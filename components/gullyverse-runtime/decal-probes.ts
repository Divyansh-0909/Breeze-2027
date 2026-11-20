import * as THREE from 'three';

/** Project clear texels inside real exported decal triangles for a render check. */
export function decalProbes(scene:THREE.Scene,camera:THREE.Camera,width:number,height:number){
 const points:{x:number;y:number;sourceAlpha:number}[]=[];
 scene.traverse((object:any)=>{
  if(!object.isMesh)return;const material=Array.isArray(object.material)?object.material[0]:object.material;
  if(!material?.userData.runtimeDecal||!material.map?.image)return;const image=material.map.image;
  if(!image.width||!image.height||image.data)return;
  const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;const context=canvas.getContext('2d',{willReadFrequently:true});if(!context)return;
  context.drawImage(image,0,0);const pixels=context.getImageData(0,0,image.width,image.height).data;
  const geometry=object.geometry,p=geometry.getAttribute('position'),uv=geometry.getAttribute(material.map.channel===0?'uv':`uv${material.map.channel}`),index=geometry.index;
  for(let i=0;i<(index?.count??p.count);i+=3){
   const ids=[0,1,2].map(j=>index?index.getX(i+j):i+j),v=ids.reduce((a,j)=>a.add(new THREE.Vector2().fromBufferAttribute(uv,j)),new THREE.Vector2()).multiplyScalar(1/3);material.map.transformUv(v);
   const x=Math.floor(v.x*image.width),y=Math.floor(v.y*image.height);let clear=true;
   for(let sy=y-12;sy<=y+12&&clear;sy++)for(let sx=x-12;sx<=x+12;sx++)if(sx<0||sy<0||sx>=image.width||sy>=image.height||pixels[(sy*image.width+sx)*4+3]!==0){clear=false;break}
   if(!clear)continue;const position=ids.reduce((a,j)=>a.add(new THREE.Vector3().fromBufferAttribute(p,j)),new THREE.Vector3()).multiplyScalar(1/3).applyMatrix4(object.matrixWorld).project(camera);const px=(position.x+1)*width/2,py=(1-position.y)*height/2;
   if(px>0&&px<width&&py>0&&py<height)points.push({x:px,y:py,sourceAlpha:0});
  }
 });return points;
}
