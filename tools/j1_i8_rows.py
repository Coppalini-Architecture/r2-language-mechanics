#!/usr/bin/env python3
"""j1_i8_rows.py -- I8 row-boundary readings for an unterminated final CHAIN.txt fragment (record 0011).
Two readings of what a "row" of V(CHAIN) is (V per record 0008):
  T1  a row is every line of V(CHAIN), the unterminated final fragment included:  split(V, LF), one trailing '' dropped.
  T2  a row is every LF-terminated line of V(CHAIN); an unterminated final fragment is not a row:  split(V, LF)[:-1].
Row verification is the J-05 chain formula (shared by both readings, nothing else differs between them); the I8 line is the
first failing row. Reads no reader output except in `matrix`, which runs the two readers only to tabulate them.
  j1_i8_rows.py rows DIR                           facts and I8 under T1 and T2 for one directory
  j1_i8_rows.py matrix READER_A READER_B DIR...    table: fragment line, each reader's I8, I8 under T1 and T2, agreement
  j1_i8_rows.py emit T1|T2 EXPECTED_0010 DIR...    expected outputs (reader format, header line omitted) for the 0010 matrix plus aux
Standard library only; deterministic."""
import sys, os, re, hashlib, subprocess

ROW = re.compile(r'^(\d{4}-\d{2}-\d{2}) ([LS]) (\d+) ([0-9a-f]{64}) ([0-9a-f]{64})$')


def view(b):                                    # V(F) = CRLF->LF(stripOneLeadingBOM(B_F))
    if b.startswith(b'\xef\xbb\xbf'): b = b[3:]
    return b.replace(b'\r\n', b'\n')


def rows(d, reading):
    v = view(open(os.path.join(d, 'CHAIN.txt'), 'rb').read()).decode('utf-8').split('\n')
    if reading == 'T1': return v[:-1] if v[-1] == '' else v
    return v[:-1]


def i8(d, reading):                             # first failing row line, or None
    raw = {R: open(os.path.join(d, fn), 'rb').read() for R, fn in (('L', 'lab.txt'), ('S', 'self.txt'))}
    st = {R: (hashlib.sha256(b'J1').digest(), -1, '') for R in 'LS'}
    for i, line in enumerate(rows(d, reading), 1):
        m = ROW.match(line)
        if not m: return i
        date, R, ln, h, link = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
        c, pl, pd = st[R]
        if ln > len(raw[R]) or ln < pl or date < pd: return i
        hh = hashlib.sha256(raw[R][:ln]).digest()
        nc = hashlib.sha256(c + ('%s %s %d' % (date, R, ln)).encode('ascii') + hh).digest()
        if hh.hex() != h or nc.hex() != link: return i
        st[R] = (nc, ln, date)
    return None


def frag(d):                                    # raw line of an unterminated final fragment, or None
    b = open(os.path.join(d, 'CHAIN.txt'), 'rb').read()
    return None if b == b'' or b.endswith(b'\n') else b.count(b'\n') + 1


def cell(x): return 'PASS' if x is None else 'FAIL CHAIN.txt:%d' % x


def reader_i8(reader, d):
    out = subprocess.run([sys.executable, '-I', reader, d], capture_output=True, text=True).stdout.split('\n')
    return [l for l in out if l.startswith('I8 ')][0][3:]


def name(d): return os.path.basename(d.rstrip('/'))


def blocks(path):
    out, cur = {}, None
    for l in open(path, encoding='utf-8').read().split('\n'):
        if l.startswith('== '): cur = l[3:]; out[cur] = []
        elif l and cur: out[cur].append(l)
    return out


mode = sys.argv[1]
if mode == 'rows':
    d = sys.argv[2]; f = frag(d)
    print('rows T1 %d T2 %d fragment %s' % (len(rows(d, 'T1')), len(rows(d, 'T2')), 'none' if f is None else f))
    print('I8 T1 ' + cell(i8(d, 'T1'))); print('I8 T2 ' + cell(i8(d, 'T2')))
elif mode == 'matrix':
    ra, rb, ds = sys.argv[2], sys.argv[3], sys.argv[4:]
    print('# dir | fragment line | A I8 | B I8 | I8 under T1 | I8 under T2 | A=T1 A=T2 B=T1 B=T2 (y/n)')
    for d in ds:
        a, b, t1, t2 = reader_i8(ra, d), reader_i8(rb, d), cell(i8(d, 'T1')), cell(i8(d, 'T2'))
        f = frag(d)
        yn = ''.join('y' if x == y else 'n' for x, y in ((a, t1), (a, t2), (b, t1), (b, t2)))
        print('%s | %s | %s | %s | %s | %s | %s' % (name(d), '-' if f is None else f, a, b, t1, t2, ' '.join(yn)))
elif mode == 'emit':
    reading, exp, ds = sys.argv[2], blocks(sys.argv[3]), sys.argv[4:]
    for d in ds:
        n = name(d); new = i8(d, reading)
        if n in exp:                            # carried from 0010; its I8 line must be the one this reading derives
            lines = exp[n]
            assert lines[7] == 'I8 ' + cell(new), (n, lines[7], cell(new))
            lines = lines[:7]
        else:                                   # aux: lab/self as base (I2-I7 PASS), CHAIN missing terminal LF -> raw line (record 0010 rule)
            b = open(os.path.join(d, 'CHAIN.txt'), 'rb').read()
            assert not b.endswith(b'\n'), n
            lines = ['I1 FAIL CHAIN.txt:%d' % (b.count(b'\n') + 1)] + ['I%d PASS' % k for k in range(2, 8)]
        fails = [l[:2] for l in lines if 'FAIL' in l] + (['I8'] if new is not None else [])
        print('== ' + n); print('\n'.join(lines)); print('I8 ' + cell(new))
        print('RESULT FAIL ' + ','.join(fails) if fails else 'RESULT PASS')
