import {createRequire} from 'node:module';
import {readFile,writeFile,readdir} from 'node:fs/promises';
const require=createRequire(import.meta.url);
let validator;
try{validator=require(process.env.GLTF_VALIDATOR_MODULE||'gltf-validator');}
catch{validator=require('/tmp/gullyverse-limestone-validator-20261012/node_modules/gltf-validator');}
const dir='public/models/gullyverse/limestone-excavation',rows=[];
for(const file of(await readdir(dir)).filter(f=>f.endsWith('.glb'))){
 const b=await readFile(dir+'/'+file),r=await validator.validateBytes(new Uint8Array(b),{uri:file});
 rows.push({file:dir+'/'+file,bytes:b.length,...r});
 console.log(file,r.issues.numErrors,'errors',r.issues.numWarnings,'warnings');
 if(r.issues.numErrors||r.issues.numWarnings)process.exitCode=1;
}
await writeFile('reports/stage-2c2-limestone-excavation-2026-10-13/raw/glTF-validator.json',JSON.stringify(rows,null,2));
