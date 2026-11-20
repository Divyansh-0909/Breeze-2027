async function(tools,before,text,store){
const id='1mUE4J2QCNMHk0ryoiSSOADbkjdwi3FN5IG5GZhoIBTU',R='/dev/shm/m2a-contact-journey-2026-11-15',unpack=r=>r.structuredContent??r;
const live=unpack(await tools.mcp__codex_apps__google_drive_get_document({document_id:id,fields:'documentId,title,revisionId'}));
if(live.revisionId!==before.revisionId)throw Error('Document changed; read latest before writing.');
const response=await tools.mcp__codex_apps__google_drive_batch_update_document({document_id:id,requests:[{insertText:{location:{index:1,tabId:'t.0'},text}}],write_control:{requiredRevisionId:before.revisionId}});if(response.isError)throw Error(JSON.stringify(response));
const after=unpack(await tools.mcp__codex_apps__google_drive_get_document({document_id:id})),L=text.length;
const old=before.tabs[0].body.content.filter(r=>r.paragraph||r.table||r.tableOfContents),newOld=after.tabs[0].body.content.filter(r=>r.startIndex>=L+1);
const shift=v=>Array.isArray(v)?v.map(shift):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,['startIndex','endIndex'].includes(k)&&typeof x==='number'?x-L:shift(x)])):v;
if(JSON.stringify(old)!==JSON.stringify(newOld.map(shift)))throw Error('Historical object preservation mismatch');
const plain=d=>d.tabs[0].body.content.flatMap(r=>r.paragraph?.elements??[]).map(e=>e.textRun?.content??'').join('');if(plain(after)!==text+plain(before))throw Error('Text readback mismatch');
const sanitize=v=>Array.isArray(v)?v.map(sanitize):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).filter(([k])=>k!=='contentUri').map(([k,x])=>[k,sanitize(x)])):v;
if(JSON.stringify(sanitize(before.tabs[0].inlineObjects))!==JSON.stringify(sanitize(after.tabs[0].inlineObjects)))throw Error('Inline-image preservation mismatch');
const proof={status:'PASS',documentId:id,beforeRevision:before.revisionId,afterRevision:after.revisionId,historicalParagraphObjectsPreserved:old.length,allPriorTextStylesImageBindingsAndReviewMarkersExact:true,inlineImages:Object.keys(after.tabs[0].inlineObjects??{}).length,insertedUTF16Length:L,expiringContentURIsExcluded:true};
for(const [file,value]of [['document-snapshots/before.json',sanitize(before)],['document-snapshots/after.json',sanitize(after)],['evidence/document-verification.json',proof],['document-snapshots/inserted-text.json',{text}]])await tools.apply_patch('*** Begin Patch\n*** Add File: '+R+'/'+file+'\n+'+JSON.stringify(value)+'\n*** End Patch');
store('TextureDocAfter',after);return proof;
}

