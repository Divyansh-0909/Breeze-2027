// Codex orchestration helpers: require tools/store/load in the functions runtime.
// No credentials or signed download URLs are stored here. Blender authoring is independent.
const uploadHelper = (async function(item) {
 const parent=item.folder==="review"?load("artReview").id:load("artCheckpoint").id;
 const prior=(load("artUploadedRecords")||[]).find(x=>x.name===item.name);
 if(prior){if(prior.sha256!==item.sha256)throw Error("Refusing to replace a previously uploaded differing file");return prior;}
 const mime=item.name.endsWith(".zip")?"application/zip":item.name.endsWith(".pdf")?"application/pdf":item.name.endsWith(".json")?"application/json":item.name.endsWith(".jpg")?"image/jpeg":item.name.endsWith(".png")?"image/png":item.name.endsWith(".blend")?"application/octet-stream":"text/markdown";
 const r=await tools.mcp__codex_apps__google_drive_upload_file({file_name:item.name,file_uri:item.path,mime_type:mime,parent_folder_id:parent});
 if(r.isError||!r.structuredContent?.id)throw Error("Upload failed: "+item.name);
 const u=r.structuredContent;
 const m=(await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:u.id,fields:"id,name,size,parents,webViewLink"})).structuredContent;
 if(Number(m.size)!==item.bytes||!m.parent_ids?.includes(parent))throw Error("Metadata mismatch "+item.name);
 const raw=await tools.mcp__codex_apps__google_drive_fetch({url:u.url,download_raw_file:true,include_base64:false});
 const d=raw.structuredContent?.file_uri?.download_url;if(!d)throw Error("No raw download");
 const receipt="/workspace/gullyverse-world-concept/2026-10-27/08-rev05c-corrugated-graffiti/checkpoint/verified-"+u.id+".json";
 await tools.write_stdin({session_id:load("artVerifyWorker"),chars:JSON.stringify({url:d,id:u.id,name:item.name,bytes:item.bytes,sha256:item.sha256,receipt})+"\n",yield_time_ms:1000,max_output_tokens:1000});
 for(let n=0;n<25;n++){
   const check=await tools.exec_command({cmd:"cat '"+receipt+"'",max_output_tokens:600});
   if(check.exit_code===0){const p=JSON.parse(check.output);if(!p.verified)throw Error("Hash failed "+item.name);break;}
   if(n===24)throw Error("Verification timeout "+item.name);
   await tools.write_stdin({session_id:load("artVerifyWorker"),chars:"",yield_time_ms:1000,max_output_tokens:1000});
 }
 const record={...item,id:u.id,url:u.url,parent,fullDownloadBackSHA256Verified:true};store("artUploadedRecords",[...(load("artUploadedRecords")||[]),record]);
 await tools.apply_patch("*** Begin Patch\n*** Add File: /workspace/gullyverse-world-concept/2026-10-27/08-rev05c-corrugated-graffiti/checkpoint/uploaded-"+u.id+".json\n+"+JSON.stringify(record,null,2).split("\n").join("\n+")+"\n*** End Patch");
 notify({uploadedAndVerified:item.name,id:u.id,bytes:item.bytes});return record;
});
const updateDocHelper = (async function(payload) {
 const docId="1ynihhc-k0aSRGVY6oJttLY8MD1AhKPahCcqheL-g56k";
 const response=await tools.mcp__codex_apps__google_drive_get_document({document_id:docId});
 if(response.isError)throw Error("Doc read failed");
 const d=response.structuredContent,tab=d.tabs[0],tabId=tab.tabId;
 function els(body){let a=[];for(const x of body.content||[]){if(x.paragraph)a.push(...x.paragraph.elements||[]);if(x.table)for(const r of x.table.tableRows||[])for(const c of r.tableCells||[])a.push(...els(c));}return a;}
 function linear(body){const end=body.content.at(-1).endIndex,a=Array(end).fill("\u0000");for(const e of els(body)){const t=e.textRun?.content||(e.inlineObjectElement?"\uFFFC":"");for(let i=0;i<t.length;i++)a[e.startIndex+i]=t[i];}return a.join("");}
 const before=linear(tab.body),oldEls=els(tab.body);
 if(before.includes("CODEX HANDOFF — "+payload.id))throw Error("Handoff already exists; reconcile rather than duplicate");
 const plans=[];
 const append=tab.body.content.at(-1).endIndex-1;
 plans.push({start:append,end:append,text:payload.completion,kind:"completion"});
 const head=tab.body.content.find(p=>(p.paragraph?.elements||[]).map(e=>e.textRun?.content||"").join("")==="LATEST CODEX HANDOFF\n");
 if(!head)throw Error("Top handoff header not found");
 plans.push({start:head.endIndex,end:head.endIndex,text:payload.notice,kind:"notice"});
 for(const [key,value]of Object.entries(payload.values)){
   const p=tab.body.content.find(p=>p.startIndex<8000&&(p.paragraph?.elements||[]).map(e=>e.textRun?.content||"").join("").startsWith(key+": "));
   if(!p)throw Error("Shared field missing "+key);
   const t=p.paragraph.elements.map(e=>e.textRun?.content||"").join("");
   plans.push({start:p.startIndex+key.length+2,end:p.endIndex-1,text:value,kind:key});
 }
 plans.sort((a,b)=>b.start-a.start);
 let expected=before;const requests=[];
 for(const p of plans){
   expected=expected.slice(0,p.start)+p.text+expected.slice(p.end);
   if(p.end>p.start)requests.push({deleteContentRange:{range:{startIndex:p.start,endIndex:p.end,tabId}}});
   requests.push({insertText:{location:{index:p.start,tabId},text:p.text}});
   const range={startIndex:p.start,endIndex:p.start+p.text.length,tabId};
   requests.push({updateTextStyle:{range,textStyle:{},fields:"link"}});
   const matches=[...p.text.matchAll(/https:\/\/[^\s]+/g)];
   for(const m of matches)requests.push({updateTextStyle:{range:{startIndex:p.start+m.index,endIndex:p.start+m.index+m[0].length,tabId},textStyle:{link:{url:m[0]}},fields:"link"}});
   requests.push({updateTextStyle:{range,textStyle:{foregroundColor:{color:{rgbColor:{red:198/255,green:40/255,blue:40/255}}}},fields:"foregroundColor"}});
 }
 const write=await tools.mcp__codex_apps__google_drive_batch_update_document({document_id:docId,write_control:{requiredRevisionId:d.revisionId},requests});
 if(write.isError)throw Error("Doc batch failed; read before retrying");
 const check=await tools.mcp__codex_apps__google_drive_get_document({document_id:docId});
 if(check.isError)throw Error("Doc readback failed");
 const after=check.structuredContent,afterTab=after.tabs.find(t=>t.tabId===tabId),afterLinear=linear(afterTab.body);
 if(afterLinear!==expected)throw Error("Non-target document text mismatch");
 const allAfter=els(afterTab.body),colors=Array(afterLinear.length).fill(null);
 for(const e of allAfter)if(e.textRun){const c=e.textRun.textStyle?.foregroundColor?.color?.rgbColor;for(let i=e.startIndex;i<e.endIndex;i++)colors[i]=c;}
 const same=(c,r,g,b)=>c&&Math.abs((c.red||0)-r)<1e-5&&Math.abs((c.green||0)-g)<1e-5&&Math.abs((c.blue||0)-b)<1e-5;
 const shiftOld=i=>i+plans.filter(p=>p.end<=i).reduce((a,p)=>a+p.text.length-(p.end-p.start),0);
 let green=0,red=0;
 for(const e of oldEls){const c=e.textRun?.textStyle?.foregroundColor?.color?.rgbColor;if(!same(c,46/255,125/255,50/255))continue;
   for(let i=e.startIndex;i<e.endIndex;i++){
     if(plans.some(p=>p.end>p.start&&p.start<=i&&i<p.end))throw Error("A mutable control unexpectedly contains protected green content");
     const j=shiftOld(i);if(!same(colors[j],46/255,125/255,50/255))throw Error("Green style changed");green++;
   }
 }
 for(const p of plans){
   const s=p.start+plans.filter(x=>x.start<p.start).reduce((a,x)=>a+x.text.length-(x.end-x.start),0);
   if(afterLinear.slice(s,s+p.text.length)!==p.text)throw Error("Inserted field readback mismatch "+p.kind);
   for(let i=s;i<s+p.text.length;i++){if(!same(colors[i],198/255,40/255,40/255))throw Error("Red style mismatch "+p.kind);red++;}
 }
 const proof={id:payload.id,status:payload.status||"PARTIAL",documentUrl:after.url||after.document_url,revision:after.revisionId,tabId,coreFieldsUpdated:Object.keys(payload.values),topNoticeAndAppendedCompletionVerified:true,allNontargetDocumentTextUnchanged:true,protectedGreenUTF16UnitsUnchanged:green,newRedUTF16Units:red,foregroundColor:"#C62828",priorChatGPTStatusAndReviewedHandoffIdUnchanged:true,requestCount:requests.length};
 store("artDocProof",proof);
 await tools.apply_patch("*** Begin Patch\n*** Add File: /workspace/gullyverse-world-concept/2026-10-27/08-rev05c-corrugated-graffiti/checkpoint/SHARED-DOC-HANDOFF-VERIFICATION.json\n+"+JSON.stringify(proof,null,2).split("\n").join("\n+")+"\n*** End Patch");
 await tools.apply_patch("*** Begin Patch\n*** Add File: /workspace/gullyverse-world-concept/2026-10-27/08-rev05c-corrugated-graffiti/checkpoint/CODEX-HANDOFF.txt\n+"+payload.completion.split("\n").join("\n+")+"\n*** End Patch");
 return proof;
});
