#!/usr/bin/env python3
"""j1_d3_matrix.py DIR... -- raw-byte coordinate matrix of whole-file I1 defects (record 0009).
For each directory and file it lists the defects found in the raw bytes, each as kind@offset->line, where
offset is the 0-based byte offset of the first offending byte (for a missing terminal LF: the end of the file, where the
LF belongs; for k extra terminal LFs: the first extra LF; for non-NFC text: the start of its line) and
line = 1 + number of LF bytes before that offset ("offset-line"). LF is the number of LF bytes in the file.
Reads no reader output; standard library only; deterministic."""
import sys, os, unicodedata

def defects(b):
    out = []
    if b.startswith(b'\xef\xbb\xbf'): out.append(('BOM', 0))
    if b'\r' in b: out.append(('CR', b.index(b'\r')))
    try:
        t = b.decode('utf-8'); off = 0
        for ln in t.split('\n'):
            if not unicodedata.is_normalized('NFC', ln): out.append(('NFC', off)); break
            off += len(ln.encode('utf-8')) + 1
    except UnicodeDecodeError as e:
        out.append(('UTF8', e.start))
    if not b.endswith(b'\n'): out.append(('noLF', len(b)))
    elif b.endswith(b'\n\n'):
        m = len(b) - len(b.rstrip(b'\n'))                    # trailing LF run
        out.append(('xLF%d' % (m - 1), len(b) - (m - 1)))
    return sorted(out, key=lambda x: x[1])

print('# dir | file LF=<LF count> defects kind@offset->offset-line (sorted by offset)')
for d in sys.argv[1:]:
    cells = []
    for fn in ('lab.txt', 'self.txt', 'CHAIN.txt'):
        b = open(os.path.join(d, fn), 'rb').read()
        df = defects(b)
        if df:
            cells.append('%s LF=%d %s' % (fn, b.count(b'\n'), ' '.join('%s@%d->%d' % (k, o, 1 + b.count(b'\n', 0, o)) for k, o in df)))
    print('%s | %s' % (os.path.basename(d.rstrip('/')), ' ; '.join(cells) if cells else 'none'))
