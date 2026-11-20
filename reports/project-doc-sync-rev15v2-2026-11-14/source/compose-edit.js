function compose(doc,content,report,phase,inventory){
 const tab=doc.tabs[0],tabId=tab.tabId,paras=tab.body.content.filter(x=>x.paragraph);const ptext=p=>p.paragraph.elements.map(e=>e.textRun?.content??(e.inlineObjectElement?'\uFFFC':'')).join('');const flat=paras.map(ptext).join('');const lastReviewed=paras.map(ptext).find(t=>t.startsWith('LAST_CHATGPT_REVIEWED_HANDOFF_ID:'));const chatStatus=paras.map(ptext).find(t=>t.startsWith('CHATGPT_STATUS:'));if(!lastReviewed||!chatStatus)throw Error('Shared state fields missing');if(flat.includes(content.handoffId))throw Error('Handoff already recorded; reconcile before editing');
 const body=t=>({kind:'body',text:t}),link=(t,u)=>({kind:'link',text:t,url:u}),h1=t=>({kind:'h1',text:t});
 const header=[h1('CURRENT CODEX STATUS / 14 NOVEMBER 2026 / REV15V2'),body('NATIVE ENVIRONMENT UPDATED — LATEST EVENTS/GATE DIRECTION ACCEPTED BY THE USER'),body('The complete native master now has 58 scenes. Current work includes detailed open shops and shop boards, continuous wet asphalt and rebuilt potholes, English highway-style navigation, weathered cypher houses/windows, the coloured Events wall and the narrow outward-open steel gate beyond the navigation stand.'),body('Events uses dusty terracotta plaster with all eight posters preserved. The whole Team building and its eight mural states remain unchanged by the latest wall/gate work. The user said “great” after the latest combined delivery and requested this update.'),link('Latest combined review PDF — Events wall and open cypher gate',content.latestPDF),link('Current complete native recovery and source checkpoint',content.nativePhase),link('Consolidated report and verified restoration links',report.url),body('Original quarry movement code remains unchanged. Full-world private walkable/website integration, the new gate collision/navigation registry and real-device validation are pending. Accommodation has replaced Schedule; the final navigation board is English-only. Older current-status entries below are historical.'),body('This is the migrated document owned by losersamurai09@gmail.com. New backups use the destination Breeze Drive. Earlier account files and revision history remain preserved.'),body('')];
 const latest=[h1('CURRENT LATEST CODEX HANDOFF / 14 NOVEMBER 2026'),body(content.handoffId+' — READY_FOR_REVIEW; USER_ACCEPTED_LATEST_DIRECTION'),body('Resume from '+inventory.scene+' in the 58-scene packed Rev15V2 master. Controller: '+inventory.teamController+'; team_index 0–7, Organising Committee first, no Coordinators. The dated handoff at the end records all work since the 12 November night handoff, including the migration, shops, road, navigation, house/window work and final Events/gate corrections.'),link('Consolidated implementation report',report.url),link('Latest combined review PDF',content.latestPDF),link('Verified current source and native recovery chain',content.nativePhase),body('The user accepted the presented Events wall and gate direction with “great”. Full-world production integration remains pending. Older summaries below do not replace this resume point.'),body('')];
 const stateLines=[
 'CURRENT_PHASE: REV15V2_NATIVE_ENVIRONMENT_COMPLETE_DOCUMENTATION_RECONCILED_2026_11_14',
 'CODEX_STATUS: READY_FOR_REVIEW; USER_ACCEPTED_LATEST_EVENTS_GATE_DIRECTION; DOCUMENT_SYNC_COMPLETE; CURRENT_PACKED_MASTER_58_SCENES; WEBSITE_INTEGRATION_PENDING',
 'CODEX_HANDOFF_ID: '+content.handoffId,
 'CODEX_REPORT_URL: '+report.url,
 'CODEX_REVIEW_PDF_URL: '+content.latestPDF,
 'CODEX_GALLERY_URL: '+content.latestPDF+' (visual reviews delivered in PDF)',
 'CODEX_BACKUP_FOLDER_URL: '+content.nativePhase,
 'CODEX_BACKUP_VERIFICATION: PASS — destination owner/parent/size and authenticated download-back SHA256; 61 V2 checkpoint payloads and actual reassembly verified; V1/V2 source reconstructions and independent fresh openings passed; complete native base chain is indexed.',
 'CURRENT_MASTER: reports/cypher-entry-rev15v2-open-steel-gate-2026-11-14/delivery/Gullyverse-Rev15V2-Open-Steel-Cypher-Gate.blend',
 'CURRENT_MASTER_SHA256: '+content.master.editedSHA256,
 'CURRENT_MASTER_BYTES: '+content.master.editedBytes,
 'CURRENT_SCENE: '+inventory.scene,
 'CURRENT_TEAM_CONTROLLER: '+inventory.teamController+'; team_index 0–7; eight teams; Organising Committee first; no Coordinators',
 'CURRENT_DOCUMENTATION_BACKUP_URL: '+phase.url,
 'CURRENT_SHARED_DOCUMENT_URL: '+(doc.document_url??doc.url),
 'CURRENT_BACKUP_ACCOUNT: losersamurai09@gmail.com; CSD361 excluded; old-account originals and revision histories retained',
 lastReviewed.trimEnd(),chatStatus.trimEnd(),
 'USER_VISUAL_APPROVAL: Earlier recorded approvals retained. On 14 November the user said “great” after the presented Events coloured-plaster/open-gate delivery and requested this update; the latest direction is accepted for continuation.',
 'PENDING_NAVIGATION: Sign-label decision resolved — Accommodation replaces Schedule. English-only text is centred and 12% larger; green/white styling and diagonal arrows remain. The sponsor LED is unchanged. Full website destination/collision integration is pending.',
 'NEXT_PROMPT_STATUS: DOCUMENTATION_SYNC_ONLY; PREVIOUSLY_REQUESTED_PRIVATE_WALKABLE_INTEGRATION_REMAINS_PENDING; NO_NEW_IMPLEMENTATION_STARTED',
 'NEXT_PROMPT_TEXT: Resume authorized whole-world work from Rev15V2 and the latest dated handoff. Preserve the original movement/input controller and account for the new gate corridor when implementing the private full-world preview. Do not resume stale Schedule, Coordinator-first, nine-slide or pre-V2 master pointers. This document update does not itself start another implementation phase.',
 ''
 ];const state=stateLines.map(body);
 const specs=[{key:'append',start:605675,end:605675,parts:content.sections,red:true,append:true},{key:'state',start:29386,end:32067,parts:state,red:false},{key:'latest',start:15394,end:16206,parts:latest,red:true},{key:'header',start:1,end:2007,parts:header,red:true}];
 const expectedOld={header:'CURRENT CODEX STATUS / 2026-11-12 / REV15P2 NIGHT LOOK APPROVED\n',latest:'CURRENT LATEST CODEX HANDOFF / 2026-11-11\n',state:'CURRENT_PHASE: REV15O_NATIVE_ENVIRONMENT_COMPLETE_DOCUMENTATION_RECONCILED_2026_11_11\n'};
 const requests=[],blocks=[];let expectedText=flat;const red={red:198/255,green:40/255,blue:40/255};const black={red:0,green:0,blue:0};const range=(start,end)=>({tabId,startIndex:start,endIndex:end});
 for(const s of specs){
  if(!s.append){const p=paras.find(p=>p.startIndex===s.start);if(!p||ptext(p)!==expectedOld[s.key])throw Error('Stale range '+s.key);if(!paras.some(p=>p.endIndex===s.end))throw Error('Range end not a paragraph boundary');}
  const text=s.parts.map(p=>p.text+'\n').join('');const insert=s.append?text:text.slice(0,-1);if(!s.append)requests.push({deleteContentRange:{range:range(s.start,s.end-1)}});requests.push({insertText:{location:{tabId,index:s.start},text:insert}});const end=s.start+insert.length;
  requests.push({updateParagraphStyle:{range:range(s.start,end),paragraphStyle:{namedStyleType:'NORMAL_TEXT',spaceAbove:{magnitude:0,unit:'PT'},spaceBelow:{magnitude:6,unit:'PT'},keepWithNext:false,keepLinesTogether:false},fields:'namedStyleType,spaceAbove,spaceBelow,keepWithNext,keepLinesTogether'}});
  requests.push({updateTextStyle:{range:range(s.start,end),textStyle:{bold:false,italic:false,underline:false,fontSize:{magnitude:11,unit:'PT'},weightedFontFamily:{fontFamily:'Arial'},foregroundColor:{color:{rgbColor:s.red?red:black}}},fields:'bold,italic,underline,fontSize,weightedFontFamily,foregroundColor,link'}});
  let cursor=s.start;
  for(const part of s.parts){const e=cursor+part.text.length;
   if(part.kind==='h1'||part.kind==='h2'){
    requests.push({updateParagraphStyle:{range:range(cursor,e),paragraphStyle:{namedStyleType:part.kind==='h1'?'HEADING_1':'HEADING_2',keepWithNext:true},fields:'namedStyleType,keepWithNext'}});
    requests.push({updateTextStyle:{range:range(cursor,e),textStyle:{fontSize:{magnitude:part.kind==='h1'?18:16,unit:'PT'}},fields:'fontSize'}});
   }
   if(part.kind==='link')requests.push({updateTextStyle:{range:range(cursor,e),textStyle:{link:{url:part.url},foregroundColor:{color:{rgbColor:{red:.06666667,green:.33333334,blue:.8}}},underline:true},fields:'link,foregroundColor,underline'}});
   cursor=e+1;
  }
  blocks.push({...s,text});expectedText=s.append?expectedText.slice(0,s.start-1)+text+expectedText.slice(s.start-1):expectedText.slice(0,s.start-1)+text+expectedText.slice(s.end-1);
 }
 return {document_id:doc.documentId,tabId,revisionId:doc.revisionId,requests,blocks,expectedText,beforeText:flat,lastReviewed: lastReviewed.trimEnd(),chatStatus:chatStatus.trimEnd(),handoffId:content.handoffId};
}
