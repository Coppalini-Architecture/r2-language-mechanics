#!/usr/bin/env python3
"""j1_check.py DIR  -- reference check for R² journal J1 (integrity checks I1-I8).
DIR holds lab.txt, self.txt, CHAIN.txt. Reads only. Runs all eight checks and reports
each failing check with the first offending line (file:line, 1-based).
Readings of the J-sections adopted here are listed in handoff/0003; the I1-failure carrier is handoff/0008."""
import re, sys, os, hashlib, unicodedata
from datetime import datetime, timedelta, timezone
d = sys.argv[1]
FILES = [('L', 'lab.txt'), ('S', 'self.txt')]
HDR = re.compile(r'^## (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}[+-]\d{2}:\d{2}) ([LS])-(\d{6})$')
TS = re.compile(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})([+-])(\d{2}):(\d{2})$')
ORDER = ['kind', 'subject', 'noticed', 'refs', 'closes', 'outcome', 'corrects', 'habit', 'cadence', 'done', 'promoted']
KINDS = {'L': {'NOTICE', 'TODO', 'WIP', 'UPDATE', 'HABIT', 'CLOSE', 'CORRECT'},
         'S': {'REVIEW', 'PROSE', 'POEM', 'ACCOLADE', 'GOAL', 'PREFERENCE', 'QUOTE', 'THOUGHT'}}
OPENERS = {'L': {'NOTICE', 'TODO', 'WIP'}, 'S': {'GOAL'}}
ALLOWED = {'L': {'kind', 'subject', 'noticed', 'refs', 'closes', 'outcome', 'corrects', 'habit', 'cadence', 'done'},
           'S': {'kind', 'subject', 'refs', 'closes', 'outcome', 'corrects', 'promoted'}}
OUTCOMES = {'done', 'dropped', 'superseded', 'merged'}
IDLIST = re.compile(r'^[LS]-\d{6}(, [LS]-\d{6})*$')
BOM = b'\xef\xbb\xbf'
def view(b):
    """V(F) = CRLF->LF(stripOneLeadingBOM(B_F)); handoff 0008. I1 reads raw bytes; I2-I7 and the CHAIN rows read V(F)."""
    if b.startswith(BOM): b = b[3:]
    return b.decode('utf-8', 'replace').replace('\r\n', '\n')
fails = {}
def fail(k, f, ln):
    fails.setdefault(k, (f, ln))
def utc(ts):
    m = TS.match(ts)
    if not m: return None
    y, mo, dd, hh, mi, sg, oh, om = m.groups()
    try:
        off = timedelta(hours=int(oh), minutes=int(om)) * (1 if sg == '+' else -1)
        return datetime(int(y), int(mo), int(dd), int(hh), int(mi), tzinfo=timezone(off)).astimezone(timezone.utc)
    except ValueError:
        return None
raw = {}; entries = {'L': [], 'S': []}
for R, fn in FILES:
    p = os.path.join(d, fn); b = open(p, 'rb').read(); raw[fn] = b
    # I1
    if b.startswith(b'\xef\xbb\xbf'): fail('I1', fn, 1)
    if b'\r' in b: fail('I1', fn, b[:b.index(b'\r')].count(b'\n') + 1)
    try:
        t = b.decode('utf-8')
        for i, line in enumerate(t.split('\n'), 1):
            if not unicodedata.is_normalized('NFC', line): fail('I1', fn, i); break
    except UnicodeDecodeError as e:
        fail('I1', fn, b[:e.start].count(b'\n') + 1); t = b.decode('utf-8', 'replace')
    if not t.endswith('\n') or t.endswith('\n\n'): fail('I1', fn, t.count('\n') + (0 if t.endswith('\n') else 1))
    lines = view(b).split('\n')
    if lines and lines[-1] == '': lines = lines[:-1]
    # I2 parse
    i = 0
    while i < len(lines):
        ln = i + 1; line = lines[i]
        m = HDR.match(line)
        if not m:
            fail('I2', fn, ln); i += 1; continue
        if m.group(2) != R: fail('I2', fn, ln)
        e = dict(file=fn, reg=R, line=ln, ts=m.group(1), id=int(m.group(3)), fields={}, flines={})
        if utc(m.group(1)) is None: fail('I2', fn, ln)
        i += 1; last = -1
        while i < len(lines) and lines[i] != '':
            fm = re.match(r'^([a-z]+): (.+)$', lines[i])
            if not fm or fm.group(1) not in ORDER or ORDER.index(fm.group(1)) <= last or fm.group(1) not in ALLOWED[R]:
                fail('I2', fn, i + 1)
            else:
                last = ORDER.index(fm.group(1)); e['fields'][fm.group(1)] = fm.group(2); e['flines'][fm.group(1)] = i + 1
            i += 1
        if i >= len(lines): fail('I2', fn, len(lines)); entries[R].append(e); break
        i += 1  # blank line after fields
        f = e['fields']
        if 'kind' not in f or 'subject' not in f or f.get('kind') not in KINDS[R]: fail('I2', fn, ln)
        if ('closes' in f) != ('outcome' in f) or f.get('outcome', 'done') not in OUTCOMES: fail('I2', fn, ln)
        for k in ('refs', 'closes', 'corrects', 'promoted'):
            if k in f and not IDLIST.match(f[k]): fail('I2', fn, e['flines'][k])
        if 'noticed' in f and utc(f['noticed']) is None: fail('I2', fn, e['flines']['noticed'])
        while i < len(lines) and not lines[i].startswith('#'):
            i += 1
        if i < len(lines):  # next header: exactly one blank line before it, none before that
            if not (lines[i - 1] == '' and i - 2 >= 0 and lines[i - 2] != ''): fail('I2', fn, i + 1)
        entries[R].append(e)
byid = {}
for R in 'LS':
    for e in entries[R]:
        byid[(R, e['id'])] = e
# I3, I4
for R in 'LS':
    prev = None; pu = None
    for k, e in enumerate(entries[R]):
        if k > 0 and e['id'] != entries[R][k - 1]['id'] + 1: fail('I3', e['file'], e['line'])
        u = utc(e['ts'])
        if u is not None:
            if pu is not None and u < pu: fail('I4', e['file'], e['line'])
            pu = u
            if 'noticed' in e['fields']:
                nu = utc(e['fields']['noticed'])
                if nu is not None and nu > u: fail('I4', e['file'], e['flines']['noticed'])
def ids(v):
    return [(x[0], int(x[2:])) for x in v.split(', ')] if IDLIST.match(v) else []
# I5, I6, I7
closed = set()
for R in 'LS':
    pos = {id(e): k for k, e in enumerate(entries[R])}
    for e in entries[R]:
        f = e['fields']
        for k in ('refs', 'closes', 'corrects', 'promoted'):
            if k not in f: continue
            for (tr, tn) in ids(f[k]):
                t = byid.get((tr, tn)); ln = e['flines'][k]
                if t is None: fail('I5', e['file'], ln); continue
                if tr == R:
                    if pos.get(id(t), 10**9) >= pos[id(e)]: fail('I5', e['file'], ln)
                else:
                    a, b = utc(t['ts']), utc(e['ts'])
                    if a is None or b is None or a > b: fail('I5', e['file'], ln)
                if R == 'L' and tr == 'S': fail('I6', e['file'], ln)
        if 'closes' in f:
            for (tr, tn) in ids(f['closes']):
                t = byid.get((tr, tn))
                if t is None: continue
                if tr != R or t['fields'].get('kind') not in OPENERS[R] or (tr, tn) in closed:
                    fail('I7', e['file'], e['flines']['closes'])
                closed.add((tr, tn))
# I8
cp = os.path.join(d, 'CHAIN.txt'); cb = open(cp, 'rb').read()
if cb.startswith(b'\xef\xbb\xbf') or b'\r' in cb or not cb.endswith(b'\n') or cb.endswith(b'\n\n'): fail('I1', 'CHAIN.txt', 1)
state = {R: (hashlib.sha256(b'J1').digest(), -1, '') for R in 'LS'}
sizes = {'L': len(raw['lab.txt']), 'S': len(raw['self.txt'])}; files = {'L': raw['lab.txt'], 'S': raw['self.txt']}
for i, line in enumerate(view(cb).split('\n')[:-1], 1):
    m = re.match(r'^(\d{4}-\d{2}-\d{2}) ([LS]) (\d+) ([0-9a-f]{64}) ([0-9a-f]{64})$', line)
    if not m: fail('I8', 'CHAIN.txt', i); continue
    date, R, ln, h, link = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
    c, pl, pd = state[R]
    if ln > sizes[R] or ln < pl or date < pd: fail('I8', 'CHAIN.txt', i); continue
    hh = hashlib.sha256(files[R][:ln]).digest()
    nc = hashlib.sha256(c + ('%s %s %d' % (date, R, ln)).encode('ascii') + hh).digest()
    if hh.hex() != h or nc.hex() != link: fail('I8', 'CHAIN.txt', i)
    state[R] = (nc, ln, date)
print('J1 CHECK')
for k in ['I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8']:
    print(k, 'PASS' if k not in fails else 'FAIL %s:%d' % fails[k])
print('RESULT', 'PASS' if not fails else 'FAIL ' + ','.join(sorted(fails)))
sys.exit(1 if fails else 0)
