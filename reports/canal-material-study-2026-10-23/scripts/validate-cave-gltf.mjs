import {createRequire} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const validator=require(process.env.GULLYVERSE_GLTF_VALIDATOR || 'gltf-validator');
const rows=[];
for(const name of ['cave-entrance.glb','entry-clearance.glb']){
 const path='public/models/gullyverse/c9-cave-recovery/'+name,data=await readFile(path);
 const result=await validator.validateBytes(new Uint8Array(data),{uri:name});
 rows.push({path,bytes:data.length,sha256:createHash('sha256').update(data).digest('hex'),result});
 console.log(name,result.issues.numErrors,'errors',result.issues.numWarnings,'warnings');
}
await writeFile('reports/canal-material-study-2026-10-23/raw/cave-gltf-validation-final.json',JSON.stringify({validatorVersion:validator.version(),status:rows.some(r=>r.result.issues.numErrors||r.result.issues.numWarnings)?'FAIL':'PASS',rows},null,2));
if(rows.some(r=>r.result.issues.numErrors||r.result.issues.numWarnings))process.exitCode=1;
