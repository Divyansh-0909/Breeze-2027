const updateTerraceDoc = async (payload) => {
 const id="1ynihhc-k0aSRGVY6oJttLY8MD1AhKPahCcqheL-g56k";
 const read=load("terraceDocFresh")??await tools.mcp__codex_apps__google_drive_get_document({document_id:id});
 if(read.isError)throw Error("Doc read failed");
 const d=read.structuredContent,t=d.tabs[0],tabId=t.tabId||t.tabProperties?.tabId;
 function els(body){let a=[];for(const p of body.content||[]){if(p.paragraph)a.push(...p.paragraph.elements||[]);if(p.table)for(const r of p.table.tableRows||[])for(const c of r.tableCells||[])a.push(...els(c));}return a;}
 function linear(body){const a=Array(body.content.at(-1).endIndex).fill("\u0000");for(const e of els(body)){const s=e.textRun?.content||(e.inlineObjectElement?"\uFFFC":"");for(let i=0;i<s.length;i++)a[e.startIndex+i]=s[i];}return a.join("");}
 const before=linear(t.body),old=els(t.body),plans=[];
 if(before.includes("CODEX HANDOFF — "+payload.id))throw Error("Handoff already exists: reconcile without duplicate");
 const head=t.body.content.find(p=>(p.paragraph?.elements||[]).map(x=>x.textRun?.content||"").join("")==="LATEST CODEX HANDOFF\n");
 if(!head)throw Error("Top header missing");
 plans.push({start:head.endIndex,end:head.endIndex,text:payload.notice,kind:"notice"});
 const end=t.body.content.at(-1).endIndex-1;plans.push({start:end,end,text:payload.completion,kind:"completion"});
 for(const[key,value]of Object.entries(payload.values)){
  const p=t.body.content.find(p=>p.startIndex<20000&&(p.paragraph?.elements||[]).map(x=>x.textRun?.content||"").join("").startsWith(key+": "));
  if(!p)throw Error("Field missing "+key);
  plans.push({start:p.startIndex+key.length+2,end:p.endIndex-1,text:value,kind:key});
 }
 plans.sort((a,b)=>b.start-a.start);let expected=before;const req=[];
 for(const p of plans){
  expected=expected.slice(0,p.start)+p.text+expected.slice(p.end);
  if(p.end>p.start)req.push({deleteContentRange:{range:{startIndex:p.start,endIndex:p.end,tabId}}});
  req.push({insertText:{location:{index:p.start,tabId},text:p.text}});
  const range={startIndex:p.start,endIndex:p.start+p.text.length,tabId};
  req.push({updateTextStyle:{range,textStyle:{},fields:"link"}});
  for(const m of p.text.matchAll(/https:\/\/[^\s]+/g))req.push({updateTextStyle:{range:{startIndex:p.start+m.index,endIndex:p.start+m.index+m[0].length,tabId},textStyle:{link:{url:m[0]}},fields:"link"}});
  req.push({updateTextStyle:{range,textStyle:{foregroundColor:{color:{rgbColor:{red:198/255,green:40/255,blue:40/255}}}},fields:"foregroundColor"}});
 }
 const write=await tools.mcp__codex_apps__google_drive_batch_update_document({document_id:id,write_control:{requiredRevisionId:d.revisionId},requests:req});
 if(write.isError)throw Error("Doc write uncertain/failed; re-read before retry");
 const after=(await tools.mcp__codex_apps__google_drive_get_document({document_id:id})).structuredContent,at=after.tabs.find(t=>(t.tabId||t.tabProperties?.tabId)===tabId),linearAfter=linear(at.body);
 if(linearAfter!==expected)throw Error("Non-target text mismatch");
 const colors=Array(linearAfter.length).fill(null);
 for(const e of els(at.body)){const c=e.textRun?.textStyle?.foregroundColor?.color?.rgbColor;if(e.textRun)for(let i=e.startIndex;i<e.endIndex;i++)colors[i]=c;}
 const same=(a,b)=>!!a&&!!b&&["red","green","blue"].every(k=>Math.abs((a[k]||0)-(b[k]||0))<1e-5);
 const shift=i=>i+plans.filter(p=>p.end<=i).reduce((n,p)=>n+p.text.length-(p.end-p.start),0);
 let green=0,red=0;
 for(const e of old){const c=e.textRun?.textStyle?.foregroundColor?.color?.rgbColor;if(!c||!(c.green>.25&&c.green>(c.red||0)*1.2&&c.green>(c.blue||0)*1.2))continue;
  for(let i=e.startIndex;i<e.endIndex;i++){if(plans.some(p=>p.end>p.start&&p.start<=i&&i<p.end))throw Error("Protected green is inside mutable field");if(!same(c,colors[shift(i)]))throw Error("Protected green formatting changed");green++;}
 }
 for(const p of plans){const s=p.start+plans.filter(x=>x.start<p.start).reduce((n,x)=>n+x.text.length-(x.end-x.start),0);for(let i=s;i<s+p.text.length;i++){if(!same(colors[i],{red:198/255,green:40/255,blue:40/255}))throw Error("Red range mismatch");red++;}}
 const proof={id:payload.id,status:"READY_FOR_REVIEW",documentUrl:after.url||after.document_url,revision:after.revisionId,tabId,coreFieldsUpdated:Object.keys(payload.values),allNonTargetTextUnchanged:true,protectedGreenUTF16UnitsUnchanged:green,newRedUTF16Units:red,foregroundColor:"#C62828",priorChatGPTStatusAndReviewedHandoffIdUnchanged:true,topNoticeAndAppendedHandoffVerified:true};
 store("terraceDocProof",proof);
 for(const[name,value]of [["SHARED-DOC-HANDOFF-VERIFICATION.json",JSON.stringify(proof,null,2)],["CODEX-HANDOFF.txt",payload.completion]])await tools.apply_patch("*** Begin Patch\n*** Add File: "+load("terraceO")+"/checkpoint/"+name+"\n+"+value.replace(/\n/g,"\n+")+"\n*** End Patch");
 return proof;
};

