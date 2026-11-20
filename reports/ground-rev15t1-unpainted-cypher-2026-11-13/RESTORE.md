# Restore the unpainted cypher revision

This is an incremental native checkpoint with a verified complete base. The new material library, runtime ground GLB, authored maps, scripts, PDF and evidence are saved in this revision. The full base is not duplicated.

1. Download all twelve Rev15T master parts using the exact Drive links in delivery/Base-Rev15T-Native-Parts.json. Run:

       python source/restore-base.py DOWNLOADS_DIRECTORY BASE_OUTPUT.blend

   The helper checks every part and the whole master and refuses to overwrite an existing output. Required base SHA256: 8c0745fcb068ba8039a8196742e0b500e905026e842e09788e565d3c34a459fc. The complete base remains in https://drive.google.com/drive/folders/1irpOPfPbjGSp4qry_JOhfhBn1p2PSFuZ.

2. Download Rev15T1-Unpainted-Asphalt-Material.blend into delivery/ and reconstruct the edited master:

       blender -b --python source/apply-edit.py -- --base BASE_OUTPUT.blend --material delivery/Rev15T1-Unpainted-Asphalt-Material.blend --output NEW_REV15T1.blend

   Use a new output filename. This retains all 49 historical scenes and adds the unpainted Rev15T1 scene. It preserves geometry and transforms and retains the flat asphalt centre. This restoration was executed successfully in a fresh Blender process. It reconstructs the scene from native data; it is not a byte-for-byte duplicate of a specific working Blender save.

3. Rev15T1-Unpainted-Asphalt-Ground.glb is the complete updated standalone ground runtime asset. It replaces the prior ground GLB in a future integration. Production website integration remains pending.

The source ZIP preserves repository-relative paths under reports/ground-rev15t1-unpainted-cypher-2026-11-13. Its PAYLOAD-SHA256.json checks every payload. Extract it into an empty directory and open that report directory for the commands above. Verify the ZIP and separately uploaded native/runtime files with SHA256SUMS.txt and Dependency-Index.json.

The material library contains its packed texture dependencies. Reauthoring maps uses make-road-art.py, NumPy and Pillow; paintedCircle is false in road-layout.json. PDF generation uses ReportLab, Pillow and pypdf with the bundled fonts and license. Earlier checkpoints, sharing settings and the old-account migration originals are preserved.
