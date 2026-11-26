#!/usr/bin/env python3
"""check_handoff.py DIR  -- verifies the append-order rules of handoff/ (record 0002).
Rules: H1 filename NNNN-slug.md; H2 numbers contiguous from 0001, no repeats;
H3 records immutable (git history: added once, never modified or deleted);
H4 seven fields present in PROTOCOL.md order, Claim in {exact, construction, open};
H5 Delta token is INITIAL for 0001, else the immediately preceding number;
H6 'Corrects: NNNN' (optional) names an earlier existing record.
Exit 0 on PASS, 1 on FAIL. Output is deterministic."""
import re, sys, subprocess, os
root = sys.argv[1] if len(sys.argv) > 1 else '.'
hd = os.path.join(root, 'handoff')
NAME = re.compile(r'^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$')
FIELDS = ['Source', 'Reader', 'Claim', 'Check', 'Receipt', 'Delta', 'Open']
files = sorted(f for f in os.listdir(hd) if f != '.gitkeep')
res = {}; fails = []
def rec(k, ok, where=''):
    res.setdefault(k, []).append((ok, where))
nums = []
for f in files:
    m = NAME.match(f)
    rec('H1', bool(m), f)
    if m: nums.append((int(m.group(1)), f))
rec('H2', [n for n, _ in nums] == list(range(1, len(nums) + 1)), 'numbers ' + ','.join('%04d' % n for n, _ in nums))
byn = dict(nums)
for n, f in nums:
    txt = open(os.path.join(hd, f), encoding='utf-8').read()
    pos = -1; ok = True
    for fld in FIELDS:
        mm = re.search(r'^- \*\*%s\*\* — ' % fld, txt, re.M)
        if not mm or mm.start() < pos: ok = False; break
        pos = mm.start()
    rec('H4', ok, f)
    cm = re.search(r'^- \*\*Claim\*\* — `?(exact|construction|open)`?\b', txt, re.M)
    rec('H4', bool(cm), f + ' claim')
    dm = re.search(r'^- \*\*Delta\*\* — (INITIAL|\d{4})\b', txt, re.M)
    want = 'INITIAL' if n == 1 else '%04d' % (n - 1)
    rec('H5', bool(dm) and dm.group(1) == want, '%s want %s got %s' % (f, want, dm.group(1) if dm else 'none'))
    cr = re.search(r'^Corrects: (\d{4})$', txt, re.M)
    if cr: rec('H6', int(cr.group(1)) < n and int(cr.group(1)) in byn, f)
def git(*a):
    return subprocess.run(['git', '-C', root] + list(a), capture_output=True, text=True)
if git('rev-parse', '--git-dir').returncode != 0:
    h3 = 'UNVERIFIED (not a git repository)'
elif git('rev-parse', '--is-shallow-repository').stdout.strip() == 'true':
    h3 = 'UNVERIFIED (shallow clone; run on a full clone)'
else:
    out = git('log', '--diff-filter=MDR', '--name-only', '--format=', '--', 'handoff/').stdout.split()
    out = [o for o in out if o != 'handoff/.gitkeep']
    h3 = 'PASS' if not out else 'FAIL ' + ','.join(sorted(set(out)))
print('HANDOFF CHECK')
bad = False
for k in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']:
    if k == 'H3':
        print(k, h3); bad |= h3.startswith('FAIL'); continue
    if k not in res: print(k, 'N/A'); continue
    f = [w for ok, w in res[k] if not ok]
    print(k, 'PASS' if not f else 'FAIL ' + '; '.join(f)); bad |= bool(f)
print('RESULT', 'FAIL' if bad else 'PASS')
sys.exit(1 if bad else 0)
