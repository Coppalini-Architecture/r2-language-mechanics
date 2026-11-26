#!/usr/bin/env python3
"""qsa_check.py SCHEMA.json FIXTURE.txt -- exhaustive check of the finite address map (q,s) -> a
declared in MOONLIGHT-LAMBDA-001.schema v0.3 (record 0005). Standard library only.
FIXTURE.txt is parsed and compared field by field (F1). Output is deterministic; exit 0 on PASS, 1 on FAIL."""
import sys, json, hashlib

PIN = 'c85c2f34eb9ff6fd2e01463be9f7eb6afb5414a8eb97ddd24fb5fac59675caad'
LAW = 'a = s + 137 * mod(q - s, 4)'
SAFE = 2 ** 53 - 1


def nmod(x, m):
    """Non-negative residue in 0..m-1, for any integer x (not the truncated remainder)."""
    return ((x % m) + m) % m


def law(q, s):
    return s + 137 * nmod(q - s, 4)


if len(sys.argv) != 3:
    sys.stderr.write('usage: qsa_check.py SCHEMA.json FIXTURE.txt\n'); sys.exit(2)
raw = open(sys.argv[1], 'rb').read()
sch = json.loads(raw.decode('utf-8'))
out = []
ok = True


def rec(name, good, detail=''):
    global ok
    ok &= good
    out.append('%s %s%s' % (name, 'PASS' if good else 'FAIL', (' ' + detail) if detail else ''))


out.append('QSA CHECK')
rec('S0 sha256 pin', hashlib.sha256(raw).hexdigest() == PIN, '%d bytes' % len(raw))
rec('S1 declared law text', sch['dome_receipt']['dome']['law'] == LAW)
rec('S2 declared domains', sch['finite_address']['domains'] == {'q': '0..3', 's': '0..136', 'a': '0..547'})
pairs = [(q, s) for q in range(4) for s in range(137)]
vals = {p: law(*p) for p in pairs}
rec('A1 range', all(0 <= a <= 547 for a in vals.values()), '%d pairs' % len(pairs))
rec('A2 uniqueness', len(set(vals.values())) == 548, '%d distinct' % len(set(vals.values())))
rec('A3 coverage', set(vals.values()) == set(range(548)))
rec('A4 a mod 4 = q', all(a % 4 == q for (q, s), a in vals.items()))
rec('A5 a mod 137 = s', all(a % 137 == s for (q, s), a in vals.items()))
rec('A6 round-trip (q,s)->a->(q,s)', all((a % 4, a % 137) == p for p, a in vals.items()))
rec('A7 round-trip a->(q,s)->a', all(law(a % 4, a % 137) == a for a in range(548)))
# s_input fixture: the file is parsed; every field is compared with the recomputation.
# rows: s_input s a(q=0) a(q=1) a(q=2) a(q=3); non-comment lines only.
DECLARED = [-SAFE, -411, -138, -137, -136, -2, -1, 0, 1, 136, 137, 138, 411, SAFE]
canon = lambda t: len(t) > 0 and str(int(t)) == t if t.lstrip('-').isdigit() else False
reason = ''
rows = []
try:
    ftxt = open(sys.argv[2], 'rb').read().decode('utf-8')
    for ln in ftxt.split('\n'):
        if ln == '' or ln.startswith('#'):
            continue
        f = ln.split(' ')
        if len(f) != 6 or not all(canon(t) for t in f):
            reason = 'malformed row: ' + ln[:40]; break
        rows.append([int(t) for t in f])
    if not reason and [r[0] for r in rows] != DECLARED:
        reason = 'inputs differ from the 14 declared (count %d)' % len(rows)
    if not reason:
        for r in rows:
            s = nmod(r[0], 137)
            if r[1:] != [s] + [law(q, s) for q in range(4)]:
                reason = 'value mismatch at s_input %d' % r[0]; break
except (OSError, UnicodeDecodeError) as e:
    reason = 'fixture unreadable'
rec('F1 s_input fixture file, 14 rows x 6 fields', reason == '', reason)
if reason == '':
    for r in rows:
        out.append('  s_input %d -> %d' % (r[0], r[1]))
out.append('RESULT ' + ('PASS' if ok else 'FAIL'))
sys.stdout.write('\n'.join(out) + '\n')
sys.exit(0 if ok else 1)
