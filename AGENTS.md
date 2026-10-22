# Gullyverse project backups

The user authorized Google Drive backups on 18 October 2026 for the current recovery checkpoint and future project work.

- Backup folder: https://drive.google.com/drive/folders/1ZubjkRneuOGp8x_lLN7xPAapGM3tn7av
- Policy and machine-readable destination: `docs/gullyverse-backup-policy.md` and `docs/gullyverse-backup-target.json`.
- At the end of each substantial recovery or implementation phase, prepare a versioned, independently restorable checkpoint and upload it to this folder through authenticated Drive access. Include required new, modified and untracked source, original/edited Blender masters, source materials, runtime assets, reports, visual evidence, restoration instructions and checksums.
- Routine backup uploads to this exact folder are already authorized; do not ask for upload approval again. Authentication or unavailable upload capabilities can still require the user's action.
- Keep earlier verified backups. Use versioned child folders; reuse identical verified files where appropriate. Do not overwrite a different historical backup or change sharing permissions.
- Create a distinct Drive folder for every phase and every subphase. Keep dated checkpoints within the relevant phase/subphase folder; do not combine different milestones into one flat folder.
- Verify remote parent, file size and content checksum, and record Drive file IDs and verification results. Do not claim an external backup exists before the uploads are actually verified. If access is unavailable, preserve the local checkpoint and explicitly mark uploads pending.
- Exclude credentials, live `.env` contents, dependencies, build output and temporary caches. A Git bundle alone does not back up LFS payloads.
- Backup authorization does not authorize a new art phase, public promotion, commits, pushes, merges or deployment. Follow the active task's scope.

This is a standing workflow for future work in this repository, not an unattended background upload service.
