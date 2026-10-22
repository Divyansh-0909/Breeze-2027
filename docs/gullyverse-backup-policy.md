# Gullyverse Google Drive backup policy

The user explicitly requested uploads of the verified Recovery Phase 1 checkpoint and future project files to this folder on 18 October 2026:

https://drive.google.com/drive/folders/1ZubjkRneuOGp8x_lLN7xPAapGM3tn7av

Folder ID: `1ZubjkRneuOGp8x_lLN7xPAapGM3tn7av`.

## Current checkpoint

Preserve the original eight Recovery Phase 1 ZIP parts without repacking or changing their recorded hashes. All parts of A, B and C restore the website and editable source catalogue. Both D parts preserve the complete historical evidence set. Also upload the checksums, restoration instructions, verification manifest, technical report, browser review PDF and screenshot gallery.

The backup policy was added after that immutable checkpoint. Back it up in a separate policy addendum so that the new standing instructions are independently retained too.

Proposed child folder: `2026-10-18-Recovery-Phase1-14f36da1`. Check the actual Drive contents before creation and reuse an existing matching checkpoint rather than making unnecessary duplicates. Do not overwrite an unrelated folder or file.

## Subsequent work

After every substantial recovery or implementation phase, export and upload a versioned checkpoint before considering that work externally preserved. Include all required changed and untracked source, Blender masters, supporting maps and licenses, runtime models/materials/media, reports, screenshots/recordings, restoration instructions and SHA-256 manifests. An incremental checkpoint is acceptable only if its complete base remains verified and its dependency index makes restoration unambiguous.

Reuse verified unchanged assets where appropriate. Keep earlier versions and comparison modes. Do not change Drive sharing permissions or introduce public download access.

The user additionally required a new folder for each phase and subphase. Create distinct named phase/subphase folders, with dated checkpoints inside their corresponding folder. A dated folder clearly identifying Recovery Phase 1 serves as the initial phase folder. Do not mix subsequent phases or subphases into this folder. Record each folder ID and hierarchy in the receipts.

Never include private credentials, live `.env` contents, `node_modules`, `.next` or temporary caches. Back up actual required LFS payloads, not just pointer files. Preserve the repository's current user edits; backup authorization does not permit resetting, cleaning, committing, pushing, merging, deploying or starting another phase.

## Verification and receipts

For each upload, retain the local relative path, byte size, SHA-256, remote file ID, remote parent folder ID, available remote content checksum and verification time. Check all expected parts are present. Prefer remote SHA-256; if unavailable, compare the provider's content checksum and document the method, or re-download and hash the bytes. A successful request or filename listing alone is insufficient verification.

Keep a machine-readable receipt and a concise human-readable backup index with working Drive links. Mark external preservation complete only after actual successful uploads and verification. Keep any pending/failed entries explicit and resumable.

If Drive authentication or a suitable upload capability is unavailable, retain the ready local checkpoint and explain the exact access blocker. Do not claim files have uploaded, and do not ask again for already-authorized routine uploads.

This policy applies while working on the project; no unattended background uploader is installed by this document.
