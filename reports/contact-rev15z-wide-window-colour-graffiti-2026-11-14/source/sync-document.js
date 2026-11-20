async function(tools,before,pdfURL,store){
 const id='1mUE4J2QCNMHk0ryoiSSOADbkjdwi3FN5IG5GZhoIBTU',R='/workspace/Breeze-2027/reports/contact-rev15z-wide-window-colour-graffiti-2026-11-14';
 const unpack=r=>r.structuredContent??r;
 const live=unpack(await tools.mcp__codex_apps__google_drive_get_document({document_id:id}));
 if(live.revisionId!==before.revisionId)throw Error('Shared document changed; inspect the current document before editing.');
 const text=`CURRENT CODEX STATUS / 14 NOVEMBER 2026 / REV15Z
ORIGINAL ACCOMMODATION GRAFFITI RESTORED - ONE WIDE CONTACT WINDOW - NO ATTENDANT
The user's correction supersedes the Y white lettering and person/left-bay layout. Accommodation now uses the exact earlier X1 orange/gold/pink COMING above SOON artwork, original mesh, UVs, transform, material and packed image. The foreground Accommodation barrier, coping/trim, small supporting graphic and extra destination label remain absent; the cypher house wall, door, window and existing wall lamp remain.
CONTACT US uses matching bold colourful graffiti image lettering centred above one wide enquiry window. The attendant, separate left bay, shutter pieces and centre divider are removed. A single 4.76 m outer frame contains a recessed 4.52 m wide form surface spanning its usable opening. All 189 original crowd members remain; there is no additional Contact person. Two local house lamps illuminate the new frontage.
Current full native: Gullyverse-Rev15Z-Wide-Contact-Window-and-Restored-Graffiti.blend, scene REV15Z / Wide Contact window and restored graffiti; 63 scenes and 146 packed images. All 62 historical scene memberships and 3,211 non-target Y objects/materials/UVs/transforms remain exact, including the three previously opened window meshes, eight Team mural states and eight Events posters. Navigation/LED sponsors, road, houses, old non-Contact lights/world/exposure and all eight checked application/movement files are unchanged. Fresh opening and reconstruction from the independently restored Y master passed. Exact original Accommodation geometry/material/image and the absence of a Contact attendant/centre divider are verified.
Private 1440x900 laptop and 390x844 phone form checks passed. The desktop form is 1,141.89 px wide; phones use the readable form sheet. Failure retains the message, confirmed local test success clears it, and duplicate submits are avoided. No overflow or page/request/GL errors occurred. Tests use injected local stubs and send no real messages. The isolated browser uses temporary house context/diagnostic lighting; it is separate from the full website environment and performance claims.
Four-page review PDF: ${pdfURL}
Versioned Z recovery location: https://drive.google.com/drive/folders/1I1r0UwtFVHjMLvbZKlULDJr9U6SX0hMQ . The editable combined native component, separate Contact/Accommodation GLBs, source/assets, manifest and private form are included. Full-world native recovery reuses the complete verified Y dependency chain plus Z. RESTORE.md, source-part hashes and authenticated download-back receipts accompany the checkpoint.
User visual approval of Z and art freeze remain open. Full-world website mounting/baking, movement/pointer-lock/focus lifecycle and existing endpoint/admin-inbox integration remain pending; Events poster/expiry/admin-role policy is still proposed. Deadline: 28 November 2026, Asia/Kolkata, hour unspecified. No production application code, database/admin access, commit, push, PR or deployment changed. The earlier Y preview is superseded; all prior document text, formatting, images and review notes below remain as history.

`;
 const response=await tools.mcp__codex_apps__google_drive_batch_update_document({document_id:id,requests:[{insertText:{location:{index:1,tabId:'t.0'},text}}],write_control:{requiredRevisionId:before.revisionId}});
 if(response.isError)throw Error(JSON.stringify(response));
 const after=unpack(await tools.mcp__codex_apps__google_drive_get_document({document_id:id}));
 const oldRows=before.tabs[0].body.content,all=after.tabs[0].body.content,L=text.length,newOldRows=all.filter(r=>r.startIndex>=L+1);
 const shift=v=>Array.isArray(v)?v.map(shift):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,['startIndex','endIndex'].includes(k)&&typeof x==='number'?x-L:shift(x)])):v;
 const oldContent=oldRows.filter(r=>r.paragraph||r.table||r.tableOfContents),recovered=newOldRows.map(shift);
 if(JSON.stringify(oldContent)!==JSON.stringify(recovered))throw Error('Historical document object preservation mismatch; inspect before claiming completion.');
 const plain=d=>d.tabs[0].body.content.flatMap(r=>r.paragraph?.elements??[]).map(e=>e.textRun?.content??'').join('');
 if(plain(after)!==text+plain(before))throw Error('Text readback mismatch');
 const stableImage=v=>Array.isArray(v)?v.map(stableImage):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).filter(([k])=>k!=='contentUri').map(([k,x])=>[k,stableImage(x)])):v;
 if(JSON.stringify(stableImage(before.tabs[0].inlineObjects))!==JSON.stringify(stableImage(after.tabs[0].inlineObjects)))throw Error('Inline image preservation mismatch');
 const proof={status:'PASS',documentId:id,beforeRevision:before.revisionId,afterRevision:after.revisionId,historicalParagraphObjectsPreserved:oldContent.length,allPriorTextStylesImageBindingsAndReviewMarkersExact:true,inlineImages:Object.keys(after.tabs[0].inlineObjects??{}).length,insertedUTF16Length:L,expiringImageContentURIsExcluded:true};
 for(const [file,value]of [['document-snapshots/after.json',after],['evidence/document-verification.json',proof],['document-snapshots/inserted-text.json',{text}]])await tools.apply_patch('*** Begin Patch\n*** Add File: '+R+'/'+file+'\n+'+JSON.stringify(value)+'\n*** End Patch');
 store('ZDocAfter',after);return proof;
}
