from pathlib import Path
import json, os, signal, subprocess, time, urllib.request

root = Path.cwd()
raw = root / 'reports/tunnel-exit-integration-2026-10-11/raw'
for prior in [Path('/tmp/breeze-tunnel-server-pid.txt'), root / 'reports/navigation-adjustments-2026-10-11/raw/server-pid.txt']:
  if prior.exists():
    pid = int(prior.read_text())
    proc = Path('/proc') / str(pid)
    try:
        owned = proc.exists() and (proc / 'cwd').resolve() == root and b'next' in (proc / 'cmdline').read_bytes()
    except OSError:
        owned = False  # An exited/zombie process has no resolvable cwd.
    if owned:
        os.kill(pid, signal.SIGTERM)
        for _ in range(40):
            if not proc.exists(): break
            time.sleep(.1)

env = os.environ.copy()
env.update(NEXT_PUBLIC_SUPABASE_URL='http://127.0.0.1:9', NEXT_PUBLIC_SUPABASE_ANON_KEY='tunnel-verification-placeholder')
checks = []
for name, command in [('build', ['npm', 'run', 'build']), ('typecheck', ['npx', 'tsc', '--noEmit'])]:
    with (raw / (name + '.log')).open('w') as log:
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    checks.append({'name': name, 'command': command, 'exitCode': result.returncode})
    (raw / 'checks.json').write_text(json.dumps(checks, indent=2))
    print(name, result.returncode, flush=True)
    if result.returncode: raise SystemExit(result.returncode)

# Keep transient process metadata outside committed evidence.
with Path('/tmp/breeze-tunnel-server.log').open('w') as log:
    server = subprocess.Popen(['node', 'node_modules/next/dist/bin/next', 'start', '--hostname', '0.0.0.0', '--port', '3000'], env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
Path('/tmp/breeze-tunnel-server-pid.txt').write_text(str(server.pid))
for _ in range(60):
    try:
        urllib.request.urlopen('http://127.0.0.1:3000/', timeout=1).close()
        if server.poll() is not None: raise RuntimeError('Production server exited')
        print('Production server ready', flush=True)
        break
    except OSError:
        time.sleep(.5)
else:
    raise RuntimeError('Production server failed to start')
