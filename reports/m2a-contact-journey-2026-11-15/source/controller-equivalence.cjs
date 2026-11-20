const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const esbuild=require('/workspace/Breeze-2027/node_modules/esbuild');const R='/dev/shm/m2a-contact-journey-2026-11-15',W='/dev/shm/Breeze-2027-runtime',out=R+'/scratch';
for(const [label,contents]of [['before',fs.readFileSync(R+'/source/runtime.before.ts','utf8')],['after',fs.readFileSync(W+'/components/immersive/runtime.ts','utf8')]])esbuild.buildSync({stdin:{contents,resolveDir:W+'/components/immersive',loader:'ts'},tsconfig:W+'/tsconfig.json',bundle:true,platform:'node',format:'cjs',outfile:out+'/runtime-'+label+'.cjs'});
const Before=require(out+'/runtime-before.cjs').ImmersiveRuntime,After=require(out+'/runtime-after.cjs').ImmersiveRuntime;let count=0;const hash=crypto.createHash('sha256');
for(const initial of ['hub','aftermovie'])for(const reduced of [false,true]){
const a=new Before(initial),b=new After(initial);a.reduced=b.reduced=reduced;a.markReady(0);b.markReady(0);a.enter();b.enter();
for(let i=0;i<4200;i++){
 for(const r of [a,b]){
  if(r.getSnapshot().phase==='covered')r.markReady(r.getSnapshot().serial);
  if(i>0&&i%600===0)r.requestDestination((i/600)%2?'aftermovie':'hub','map');
  if(i%600===100)r.setMap(true);if(i%600===160)r.setMap(false);
  if(i%600===300&&r.getSnapshot().scene==='aftermovie')r.setMovie(true);if(i%600===390)r.setMovie(false);
  r.input.forward=Math.sin(i*.07);r.input.strafe=Math.cos(i*.03);r.input.lookX=Math.sin(i)*.002;r.input.lookY=Math.cos(i)*.001;r.tick(i%377===0?.6:1/60);
 }
 const snapshot=r=>({state:r.getSnapshot(),pose:r.pose,opacity:r.opacity,cover:r.revealOpacity,map:r.mapProgress,camera:r.cameraPose(i%2?390/844:16/9)});
 const aa=snapshot(a),bb=snapshot(b);assert.deepEqual(aa,bb);hash.update(JSON.stringify(bb));count++;
}}
const result={status:'PASS',defaultQuarryFramesCompared:count,allDefaultStatePoseCameraOpacityAndMapValuesBitExact:true,traceSHA256:hash.digest('hex'),originalSnapshot:'source/runtime.before.ts',scope:'Default original hub/Aftermovie behavior; new native adapter intentionally uses its own coordinates'};fs.writeFileSync(R+'/evidence/controller-equivalence.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
