#!/usr/bin/env python3
"""j1_d2_fixture.py BASE_DIR OUT_DIR -- writes the D2 mutants (record 0007) from receipts/0003-j1-fixture/base.
Each mutant changes bytes of exactly one file. For lab.txt and self.txt the CHAIN is rebuilt over the
mutated bytes with the J-05 formula (c0 = SHA256("J1"); c_k = SHA256(c_{k-1} || "date reg len" || h_k)),
so I8 is not the failing check; the only intended failure is I1. For CHAIN.txt the mutated bytes are the
file itself. Standard library only; output is deterministic."""
import sys, os, hashlib

base, out = sys.argv[1], sys.argv[2]
BOM = b'\xef\xbb\xbf'
files = {n: open(os.path.join(base, n), 'rb').read() for n in ('lab.txt', 'self.txt', 'CHAIN.txt')}
rows = [l.split(' ') for l in files['CHAIN.txt'].decode().split('\n') if l]   # date reg len h link


def first_lf(b): return b.index(b'\n')


def bare_offset(b):
    ln5 = 0
    for _ in range(4): ln5 = b.index(b'\n', ln5) + 1      # start of line 5
    return ln5 + 5                                        # after "Inbox"


# name -> (file, transform on a byte prefix); each transform is local so it can be applied to chain prefixes
def t_bom(p): return BOM + p
def t_first(p):
    i = first_lf(files['lab.txt'])
    return p[:i] + b'\r\n' + p[i + 1:] if len(p) > i else p
def t_bare(p):
    i = bare_offset(files['lab.txt'])
    return p[:i] + b'\r' + p[i:] if len(p) > i else p
def t_barehdr(p):
    i = first_lf(files['lab.txt']) - 6                    # between "L-" and "000001" in the first header
    return p[:i] + b'\r' + p[i:] if len(p) > i else p
def t_drop1(p):                                           # separation control: drop the first self.txt entry (six lines)
    b = files['self.txt']; cut = 0
    for _ in range(6): cut = b.index(b'\n', cut) + 1
    return p[cut:] if len(p) > cut else b''
def t_all(p): return p.replace(b'\n', b'\r\n')

MUT = [('bom_lab', 'lab.txt', t_bom), ('bom_self', 'self.txt', t_bom), ('bom_chain', 'CHAIN.txt', t_bom),
       ('cr_lab_first', 'lab.txt', t_first), ('cr_lab_bare', 'lab.txt', t_bare), ('cr_lab_bare_hdr', 'lab.txt', t_barehdr),
       ('cr_lab_all', 'lab.txt', t_all), ('cr_self_all', 'self.txt', t_all),
       ('ctl_first_id_self', 'self.txt', t_drop1), ('cr_chain_one', 'CHAIN.txt', None), ('cr_chain_all', 'CHAIN.txt', t_all)]


def rechain(newfiles, mutated, tf):
    c = {r: hashlib.sha256(b'J1').digest() for r in 'LS'}
    lines = []
    for date, reg, ln, _h, _link in rows:
        fn = 'lab.txt' if reg == 'L' else 'self.txt'
        pre = files[fn][:int(ln)]
        if fn == mutated: pre = tf(pre)
        h = hashlib.sha256(pre).digest()
        m = ('%s %s %d' % (date, reg, len(pre))).encode('ascii')
        c[reg] = hashlib.sha256(c[reg] + m + h).digest()
        lines.append('%s %s %d %s %s' % (date, reg, len(pre), h.hex(), c[reg].hex()))
    return ('\n'.join(lines) + '\n').encode('ascii')


for name, fn, tf in MUT:
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    nf = dict(files)
    if fn == 'CHAIN.txt':
        nf['CHAIN.txt'] = (files['CHAIN.txt'].replace(b'\n', b'\r\n', 1) if tf is None else tf(files['CHAIN.txt']))
    else:
        nf[fn] = tf(files[fn])
        nf['CHAIN.txt'] = rechain(nf, fn, tf)
    for n, b in nf.items():
        open(os.path.join(d, n), 'wb').write(b)
