#!/usr/bin/env python3
"""j1_d3_fixture.py BASE_DIR OUT_DIR -- writes the D3 coordinate mutants (record 0009) from receipts/0003-j1-fixture/base.
Whole-file I1 defects: missing terminal LF, one or two extra terminal LFs, a CRLF placed beyond line 1 of CHAIN.txt
(recovered rows otherwise valid), CRLF mid-file in lab.txt and self.txt, and one two-defect file (non-NFC at line 23, CR at line 40).
For lab.txt and self.txt mutants the CHAIN is rebuilt over the mutated bytes (J-05 formula), so I8 is not the intended failure;
for CHAIN.txt mutants the mutated bytes are the file itself. Standard library only; deterministic."""
import sys, os, hashlib

base, out = sys.argv[1], sys.argv[2]
files = {n: open(os.path.join(base, n), 'rb').read() for n in ('lab.txt', 'self.txt', 'CHAIN.txt')}
rows = [l.split(' ') for l in files['CHAIN.txt'].decode().split('\n') if l]   # date reg len h link


def lf_offset(b, line):                      # byte offset of the LF that ends raw line `line` (1-based)
    o = -1
    for _ in range(line): o = b.index(b'\n', o + 1)
    return o


def full(fn): return len(files[fn])
def no_lf(fn):  return lambda p: p[:-1] if len(p) == full(fn) else p
def x_lf(fn, k): return lambda p: p + b'\n' * k if len(p) == full(fn) else p
def crlf_at(fn, lines):                      # LF ending each listed line written CR LF (base offsets; later offsets first)
    offs = sorted((lf_offset(files[fn], l) for l in lines), reverse=True)
    def t(p):
        for j in offs:
            if len(p) > j: p = p[:j] + b'\r\n' + p[j + 1:]
        return p
    return t
def nfd_then_cr(p):                          # self.txt: CR LF at line 40, then the body e-acute (line 23, as in 0003 mut_I1) written e + U+0301
    p = crlf_at('self.txt', [40])(p)
    i = files['self.txt'].index(b'\xc3\xa9', files['self.txt'].index(b'\xc3\xa9') + 2)
    return p[:i] + b'e\xcc\x81' + p[i + 2:] if len(p) > i + 1 else p

def badlast(p):                              # CHAIN.txt without terminal LF, first hex digit of the last row's h changed (aux, not a coordinate mutant)
    p = no_lf('CHAIN.txt')(p)
    rs = p.split(b'\n'); f = rs[-1].split(b' ')
    f[3] = (b'0' if f[3][:1] != b'0' else b'1') + f[3][1:]
    rs[-1] = b' '.join(f)
    return b'\n'.join(rs)

MUT = [('lab_noLF', 'lab.txt', no_lf('lab.txt')), ('self_noLF', 'self.txt', no_lf('self.txt')), ('chain_noLF', 'CHAIN.txt', no_lf('CHAIN.txt')),
       ('lab_xLF1', 'lab.txt', x_lf('lab.txt', 1)), ('self_xLF1', 'self.txt', x_lf('self.txt', 1)), ('chain_xLF1', 'CHAIN.txt', x_lf('CHAIN.txt', 1)),
       ('lab_xLF2', 'lab.txt', x_lf('lab.txt', 2)), ('chain_xLF2', 'CHAIN.txt', x_lf('CHAIN.txt', 2)),
       ('chain_cr_l7', 'CHAIN.txt', crlf_at('CHAIN.txt', [7])), ('chain_cr_l20', 'CHAIN.txt', crlf_at('CHAIN.txt', [20])),
       ('chain_cr_l5_l12', 'CHAIN.txt', crlf_at('CHAIN.txt', [5, 12])),
       ('lab_cr_l40', 'lab.txt', crlf_at('lab.txt', [40])), ('self_cr_l20', 'self.txt', crlf_at('self.txt', [20])),
       ('self_nfd23_cr40', 'self.txt', nfd_then_cr),
       ('aux_chain_noLF_badlast', 'CHAIN.txt', badlast)]


def rechain(fn_mut, tf):
    c = {r: hashlib.sha256(b'J1').digest() for r in 'LS'}
    lines = []
    for date, reg, ln, _h, _link in rows:
        fn = 'lab.txt' if reg == 'L' else 'self.txt'
        pre = files[fn][:int(ln)]
        if fn == fn_mut: pre = tf(pre)
        h = hashlib.sha256(pre).digest()
        m = ('%s %s %d' % (date, reg, len(pre))).encode('ascii')
        c[reg] = hashlib.sha256(c[reg] + m + h).digest()
        lines.append('%s %s %d %s %s' % (date, reg, len(pre), h.hex(), c[reg].hex()))
    return ('\n'.join(lines) + '\n').encode('ascii')


for name, fn, tf in MUT:
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    nf = dict(files)
    if fn == 'CHAIN.txt': nf['CHAIN.txt'] = tf(files['CHAIN.txt'])
    else:
        nf[fn] = tf(files[fn])
        nf['CHAIN.txt'] = rechain(fn, tf)
    for n, b in nf.items():
        open(os.path.join(d, n), 'wb').write(b)
