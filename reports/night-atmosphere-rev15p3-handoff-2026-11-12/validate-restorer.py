import hashlib, json, subprocess, sys, tempfile, zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
script = root / 'restore-checkpoints.py'
checks = {}
with tempfile.TemporaryDirectory(prefix='breeze-restore-test-') as tmp:
    t = Path(tmp); downloads = t / 'downloads'; downloads.mkdir(); archives = []
    for i in range(2):
        name = f'fixture-{i}.zip'; zpath = t / name
        payload = (b'Breeze native/browser restoration fixture\n' * (i + 1))
        member = f'reports/source-{i}/nested/file.txt'
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr(member, payload)
        data = zpath.read_bytes(); parts = []
        for j, offset in enumerate(range(0, len(data), 91)):
            b = data[offset:offset+91]; pn = name + f'.part{j+1:03d}'
            (downloads / pn).write_bytes(b)
            parts.append({'name':pn,'index':j,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        archives.append({'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'parts':parts,'payloads':[{'path':member,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}]})
    manifest = t / 'manifest.json'; manifest.write_text(json.dumps({'archives':archives}))
    def run(dest):
        return subprocess.run([sys.executable, str(script), str(downloads), str(dest), '--manifest', str(manifest)], capture_output=True, text=True)
    good = run(t / 'good'); assert good.returncode == 0, good.stderr
    for i in range(2):
        assert (t / 'good' / f'reports/source-{i}/nested/file.txt').read_bytes() == b'Breeze native/browser restoration fixture\n' * (i + 1)
    checks['two_archive_nested_payload_restore'] = True
    occupied = run(t / 'good'); assert occupied.returncode != 0 and 'nonempty' not in occupied.stderr and 'new, empty' in occupied.stderr
    checks['existing_directory_preserved'] = True
    part = downloads / archives[0]['parts'][0]['name']; original = part.read_bytes(); part.write_bytes(b'X' + original[1:])
    bad = run(t / 'corrupt'); assert bad.returncode != 0 and 'Part checksum failed' in bad.stderr
    checks['corrupt_part_rejected'] = True; part.write_bytes(original)
    escaped = t / 'unsafe.zip'
    with zipfile.ZipFile(escaped, 'w') as z: z.writestr('../escaped.txt', b'bad')
    data = escaped.read_bytes(); name = 'unsafe.zip.part001'; (downloads / name).write_bytes(data)
    manifest.write_text(json.dumps({'archives':[{'name':'unsafe.zip','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'parts':[{'name':name,'index':0,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}],'payloads':[{'path':'../escaped.txt','bytes':3,'sha256':hashlib.sha256(b'bad').hexdigest()}]}]}))
    unsafe = run(t / 'unsafe'); assert unsafe.returncode != 0 and 'Unsafe archive path' in unsafe.stderr and not (t / 'escaped.txt').exists()
    checks['archive_path_escape_rejected'] = True
result = {'status':'PASS','scope':'Restorer behaviour with small two-archive fixtures; real source archive integrity separately checked for every payload and authenticated remote part','checks':checks}
(root / 'restorer-verification.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
