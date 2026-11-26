#!/usr/bin/env python3
"""j1_check2.py DIR -- second implementation of the R2 journal J1 check (I1..I8).
Written from the spec (J-01..J-05, doc rev 19) and the readings listed in
handoff 0003 only. Standard library only.

Output (fixed):
  J1 CHECK
  I1 PASS | I1 FAIL file:line   ... through I8
  RESULT PASS | RESULT FAIL I<a>[,I<b>...]
"""
import sys, os, re, hashlib, unicodedata
from datetime import datetime, timedelta, timezone

FILES = [('lab.txt', 'L'), ('self.txt', 'S'), ('CHAIN.txt', None)]
FIELD_ORDER = ['kind', 'subject', 'noticed', 'refs', 'closes', 'outcome',
               'corrects', 'habit', 'cadence', 'done', 'promoted']
L_KINDS = {'NOTICE', 'TODO', 'WIP', 'UPDATE', 'HABIT', 'CLOSE', 'CORRECT'}
S_KINDS = {'REVIEW', 'PROSE', 'POEM', 'ACCOLADE', 'GOAL', 'PREFERENCE', 'QUOTE', 'THOUGHT'}
OPENERS = {'L': {'NOTICE', 'TODO', 'WIP'}, 'S': {'GOAL'}}
OUTCOMES = {'done', 'dropped', 'superseded', 'merged'}
S_FORBIDDEN = {'noticed', 'habit', 'cadence', 'done'}
INSTANT = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})'
HEADER = re.compile(r'^## (%s) ([LS])-(\d{6})$' % INSTANT)
FIELDLINE = re.compile(r'^([a-z]+): (\S.*)$')
IDLIST = re.compile(r'^[LS]-\d{6}(?:, ?[LS]-\d{6})*$')
IDTOK = re.compile(r'[LS]-\d{6}')


def utc(s):
    d = datetime.strptime(s[:16], '%Y-%m-%dT%H:%M')
    if s.endswith('Z') or len(s) == 16:
        return d.replace(tzinfo=timezone.utc)
    sign = 1 if s[16] == '+' else -1
    off = timedelta(hours=int(s[17:19]), minutes=int(s[20:22])) * sign
    return d.replace(tzinfo=timezone(off)).astimezone(timezone.utc)


def main(d):
    raw = {}
    for fn, _ in FILES:
        with open(os.path.join(d, fn), 'rb') as f:
            raw[fn] = f.read()
    fails = {}  # check -> first offending 'file:line'

    def fail(check, fn, line):
        fails.setdefault(check, '%s:%d' % (fn, line))

    # ---------- I1 ----------
    for fn, _ in FILES:
        b = raw[fn]
        if fails.get('I1'):
            break
        if b.startswith(b'\xef\xbb\xbf'):
            fail('I1', fn, 1); break
        try:
            t = b.decode('utf-8')
        except UnicodeDecodeError as e:
            fail('I1', fn, b[:e.start].count(b'\n') + 1); break
        if '\r' in t:
            fail('I1', fn, t[:t.index('\r')].count('\n') + 1); break
        bad = None
        for i, ln in enumerate(t.split('\n'), 1):
            if unicodedata.normalize('NFC', ln) != ln:
                bad = i; break
        if bad:
            fail('I1', fn, bad); break
        if not t.endswith('\n'):
            fail('I1', fn, t.count('\n') + 1); break
        if t.endswith('\n\n'):
            fail('I1', fn, t.count('\n'))  # the blank line after the final newline
            break
        if t == '':
            fail('I1', fn, 1); break

    text = {fn: raw[fn].decode('utf-8', 'replace').replace('\r', '') for fn, _ in FILES}

    # ---------- parse registers (I2) ----------
    regs = {}   # reg letter -> list of entries
    for fn, reg in FILES[:2]:
        lines = text[fn].split('\n')
        if lines and lines[-1] == '':
            lines.pop()
        entries = []
        cur = None
        i = 0
        n = len(lines)
        ok2 = True

        def f2(ln):
            fail('I2', fn, ln)

        # locate headers: every line beginning with '#' is a header or an I2 failure
        hdr_idx = []
        for k, ln in enumerate(lines):
            if ln.startswith('#'):
                if HEADER.match(ln):
                    hdr_idx.append(k)
                else:
                    f2(k + 1)
        if not lines:
            f2(1)
        elif not lines[0].startswith('#'):
            f2(1)
        for h, k in enumerate(hdr_idx):
            end = hdr_idx[h + 1] if h + 1 < len(hdr_idx) else n
            m = HEADER.match(lines[k])
            ent = {'line': k + 1, 'instant': m.group(1), 'reg': m.group(2),
                   'num': int(m.group(3)), 'fields': [], 'fl': {}, 'kind': None}
            if m.group(2) != reg:
                f2(k + 1)
            # separator before the next header: exactly one blank line
            block = lines[k + 1:end]
            if h + 1 < len(hdr_idx):
                if not block or block[-1] != '':
                    f2(end)  # missing blank line before the next header
                else:
                    block = block[:-1]
                    if block and block[-1] == '':
                        f2(end)  # more than one blank line between entries
            # fields until first blank line
            j = 0
            last_idx = -1
            while j < len(block) and block[j] != '':
                ln = block[j]
                lno = k + 2 + j
                fm = FIELDLINE.match(ln)
                if not fm or fm.group(1) not in FIELD_ORDER:
                    f2(lno); j += 1; continue
                key, val = fm.group(1), fm.group(2)
                idx = FIELD_ORDER.index(key)
                if idx <= last_idx:
                    f2(lno)
                last_idx = max(last_idx, idx)
                if key in ent['fl']:
                    f2(lno)
                ent['fl'][key] = (val, lno)
                j += 1
            if j >= len(block):
                f2(k + 1 + len(block) + 1 if block else k + 2)   # no blank line after fields
            fl = ent['fl']
            if 'kind' not in fl or 'subject' not in fl:
                f2(k + 1)
            else:
                if fl['kind'][1] != k + 2 or fl['subject'][1] != k + 3:
                    pass  # order already enforced above
                kind = fl['kind'][0]
                ent['kind'] = kind
                if kind not in (L_KINDS if reg == 'L' else S_KINDS):
                    f2(fl['kind'][1])
            if reg == 'S':
                for fk in S_FORBIDDEN:
                    if fk in fl:
                        f2(fl[fk][1])
            for key, (val, lno) in fl.items():
                if key in ('noticed',) and not re.fullmatch(INSTANT, val):
                    f2(lno)
                if key in ('refs', 'closes', 'corrects', 'promoted') and not IDLIST.match(val):
                    f2(lno)
                if key == 'outcome' and val not in OUTCOMES:
                    f2(lno)
                if key == 'done' and val not in ('yes', 'no'):
                    f2(lno)
            if 'closes' in fl and 'outcome' not in fl:
                f2(fl['closes'][1])
            entries.append(ent)
        regs[reg] = entries

    def idstr(e):
        return '%s-%06d' % (e['reg'], e['num'])

    def ids_in(val):
        return IDTOK.findall(val)

    # ---------- I3 ----------
    for fn, reg in FILES[:2]:
        prev = None
        for e in regs[reg]:
            if prev is not None and e['num'] != prev + 1:
                fail('I3', fn, e['line']); break
            prev = e['num']

    # ---------- I4 ----------
    for fn, reg in FILES[:2]:
        prev = None
        for e in regs[reg]:
            try:
                t = utc(e['instant'])
                nt = utc(e['fl']['noticed'][0]) if 'noticed' in e['fl'] else None
            except Exception:
                continue
            if prev is not None and t < prev:
                fail('I4', fn, e['line']); break
            if nt is not None and nt > t:
                fail('I4', fn, e['fl']['noticed'][1]); break
            prev = t

    # ---------- I5 ----------
    seen_pos = {}   # id -> (register, position, utc)
    for reg in 'LS':
        for pos, e in enumerate(regs[reg]):
            try:
                seen_pos[idstr(e)] = (reg, pos, utc(e['instant']))
            except Exception:
                seen_pos[idstr(e)] = (reg, pos, None)
    for fn, reg in FILES[:2]:
        for pos, e in enumerate(regs[reg]):
            done_e = False
            for key in ('refs', 'closes', 'corrects', 'promoted'):
                if key not in e['fl']:
                    continue
                val, lno = e['fl'][key]
                for tid in ids_in(val):
                    if tid[0] == 'S' and reg == 'L':
                        continue   # I6's business
                    t = seen_pos.get(tid)
                    if t is None:
                        fail('I5', fn, lno); done_e = True; break
                    if t[0] == reg:
                        if not t[1] < pos:
                            fail('I5', fn, lno); done_e = True; break
                    else:
                        me = seen_pos.get(idstr(e))
                        if t[2] is None or me is None or me[2] is None or t[2] > me[2]:
                            fail('I5', fn, lno); done_e = True; break
                if done_e:
                    break
            if done_e:
                break
        if 'I5' in fails:
            break

    # ---------- I6 ----------
    for e in regs['L']:
        for key, (val, lno) in e['fl'].items():
            if re.search(r'S-\d{6}', val):
                fail('I6', 'lab.txt', lno); break
        if 'I6' in fails:
            break

    # ---------- I7 ----------
    for fn, reg in FILES[:2]:
        kind_of = {idstr(e): e['kind'] for e in regs[reg]}
        closed = set()
        for e in regs[reg]:
            if 'closes' not in e['fl']:
                continue
            val, lno = e['fl']['closes']
            bad = False
            for tid in ids_in(val):
                if tid[0] == reg and tid not in kind_of:
                    continue   # nonexistent target is I5's, not I7's
                if tid[0] != reg or kind_of[tid] not in OPENERS[reg] or tid in closed:
                    bad = True
            for tid in ids_in(val):
                closed.add(tid)
            if bad:
                fail('I7', fn, lno); break
        if 'I7' in fails:
            break

    # ---------- I8 ----------
    c = hashlib.sha256(b'J1').digest()
    chain_prev = {}
    last = {}
    prev_date = {}
    clines = text['CHAIN.txt'].split('\n')
    if clines and clines[-1] == '':
        clines.pop()
    links = {'L': hashlib.sha256(b'J1').digest(), 'S': hashlib.sha256(b'J1').digest()}
    row = re.compile(r'^(\d{4}-\d{2}-\d{2}) ([LS]) (\d+) ([0-9a-f]{64}) ([0-9a-f]{64})$')
    for i, ln in enumerate(clines, 1):
        m = row.match(ln)
        if not m:
            fail('I8', 'CHAIN.txt', i); break
        date, reg, ln_s, h, link = m.groups()
        length = int(ln_s)
        fb = raw['lab.txt' if reg == 'L' else 'self.txt']
        if str(length) != ln_s or length > len(fb):
            fail('I8', 'CHAIN.txt', i); break
        if reg in last and length < last[reg]:
            fail('I8', 'CHAIN.txt', i); break
        if reg in prev_date and date < prev_date[reg]:
            fail('I8', 'CHAIN.txt', i); break
        hh = hashlib.sha256(fb[:length]).digest()
        if hh.hex() != h:
            fail('I8', 'CHAIN.txt', i); break
        m_k = ('%s %s %d' % (date, reg, length)).encode('ascii')
        nl = hashlib.sha256(links[reg] + m_k + hh).digest()
        if nl.hex() != link:
            fail('I8', 'CHAIN.txt', i); break
        links[reg] = nl
        last[reg] = length
        prev_date[reg] = date

    # ---------- report ----------
    out = ['J1 CHECK']
    for k in ['I%d' % i for i in range(1, 9)]:
        out.append('%s %s' % (k, ('FAIL ' + fails[k]) if k in fails else 'PASS'))
    bad = [k for k in ['I%d' % i for i in range(1, 9)] if k in fails]
    out.append('RESULT ' + ('FAIL ' + ','.join(bad) if bad else 'PASS'))
    sys.stdout.write('\n'.join(out) + '\n')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
