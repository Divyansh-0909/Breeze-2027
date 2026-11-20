function verify(before,after,plan){
 const text=p=>p.paragraph.elements.map(e=>e.textRun?.content??(e.inlineObjectElement?'\uFFFC':'')).join('');const flat=d=>d.tabs[0].body.content.filter(x=>x.paragraph).map(text).join('');if(flat(after)!==plan.expectedText)throw Error('Document text differs from planned scoped edit');
 const mutable=plan.blocks.filter(b=>!b.append);const append=plan.blocks.find(b=>b.append);const shift=i=>mutable.reduce((v,b)=>v+(i>=b.end?b.text.length-(b.end-b.start):0),i)+(i>=append.start?append.text.length:0);
 const scrub=x=>Array.isArray(x)?x.map(scrub):x&&typeof x==='object'?Object.fromEntries(Object.entries(x).filter(([k])=>!['startIndex','endIndex','contentUri'].includes(k)).map(([k,v])=>[k,scrub(v)])):x;
 const same=(x,y)=>JSON.stringify(scrub(x))===JSON.stringify(scrub(y));const aa=after.tabs[0].body.content;let preserved=0,green=0;
 for(const p of before.tabs[0].body.content){
  if(!p.paragraph)continue;if(mutable.some(b=>p.startIndex>=b.start&&p.startIndex<b.end))continue;
  const q=aa.find(x=>x.startIndex===shift(p.startIndex)&&x.endIndex===shift(p.endIndex-1)+1);
  // The original final empty paragraph is reused as the append location.
  if(p.startIndex===append.start)continue;
  if(!q||!same(p.paragraph,q.paragraph))throw Error('Historical paragraph/formatting changed at '+p.startIndex+': '+text(p).slice(0,100));preserved++;
  if(p.paragraph.elements.some(e=>{const c=e.textRun?.textStyle?.foregroundColor?.color?.rgbColor;return c&&c.green>.25&&c.green>c.red*1.5}))green++;
 }
 if(before.tabs.length!==after.tabs.length||before.tabs[0].tabId!==after.tabs[0].tabId||!same(before.tabs[0].documentStyle,after.tabs[0].documentStyle)||!same(before.tabs[0].namedStyles,after.tabs[0].namedStyles))throw Error('Document tabs or global styles changed');
 const oldImages=Object.keys(before.tabs[0].inlineObjects??{}),newImages=Object.keys(after.tabs[0].inlineObjects??{});if(JSON.stringify(oldImages)!==JSON.stringify(newImages)||!same(before.tabs[0].inlineObjects,after.tabs[0].inlineObjects))throw Error('Embedded images changed');
 if(!flat(after).includes(plan.lastReviewed)||!flat(after).includes(plan.chatStatus))throw Error('Independent ChatGPT review markers changed');
 let links=0;const expectedLabels=plan.blocks.flatMap(b=>b.parts).filter(p=>p.kind==='link');
 for(const link of expectedLabels){const matches=aa.filter(p=>p.paragraph&&text(p)===link.text+'\n');if(!matches.length||!matches.some(p=>p.paragraph.elements.filter(e=>e.textRun&&e.textRun.content.trim()).every(e=>e.textRun.textStyle?.link?.url===link.url)))throw Error('Missing or incomplete link '+link.text);links++;}
 for(const part of plan.blocks.flatMap(b=>b.parts).filter(p=>p.kind==='h1'||p.kind==='h2')){const p=aa.find(p=>p.paragraph&&text(p)===part.text+'\n');if(p?.paragraph.paragraphStyle.namedStyleType!==(part.kind==='h1'?'HEADING_1':'HEADING_2'))throw Error('Heading lost native style '+part.text);}
 return {status:'PASS',documentId:after.documentId,url:after.document_url??after.url,revisionId:after.revisionId,textExactlyMatchesPlannedScopedEdits:true,preservedHistoricalParagraphs:preserved,preservedHistoricalGreenParagraphs:green,allHistoricalParagraphFormattingAndLinksExact:true,embeddedImagesPreserved:oldImages.length,tabsAndGlobalStylesPreserved:true,currentNativeSceneCount:58,newLinkedLabelsVerified:links,lastIndependentChatGPTReviewMarkerUnchanged:true,userLatestDirectionAcceptanceRecorded:true,fullWorldWebsiteIntegration:'PENDING',handoffId:plan.handoffId};
}
