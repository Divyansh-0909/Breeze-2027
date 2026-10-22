import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';

test('only the WIP deployment enables the selected cave/C9 default at build time', () => {
  for (const [branch, expected] of [
    ['work-in-progress-2027', '1'],
    ['main', '0'],
    ['codex/navigation-board', '0'],
    ['', '0'],
  ]) {
    const value = execFileSync(process.execPath, ['-e',
      "process.stdout.write(require('./next.config.js').env.NEXT_PUBLIC_GULLYVERSE_WIP_DEFAULT)"], {
      cwd: process.cwd(),
      env: {...process.env, VERCEL_GIT_COMMIT_REF: branch,
        NEXT_PUBLIC_GULLYVERSE_WIP_DEFAULT: '1'},
      encoding: 'utf8',
    });
    assert.equal(value, expected, `branch ${branch || '(unconfigured)'}`);
  }
});
