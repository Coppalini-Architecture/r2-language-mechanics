#!/usr/bin/env python3
"""j1_fixture.py OUTDIR -- writes the frozen synthetic J1 fixture and eight mutants.
OUTDIR/base/{lab,self,CHAIN}.txt and OUTDIR/mut_I1 .. mut_I8, each with the same three files.
Mutants I1-I7 change an entry before the chain is written (a defective writer); mut_I8 edits one
byte after the chain is written. Deterministic; no clock, no randomness."""
import sys, os, copy, hashlib, unicodedata
from datetime import datetime, timedelta, timezone
BASE = datetime(2026, 11, 1, tzinfo=timezone.utc)
def E(reg, n, day, hhmm, off, kind, subject, body, **f):
    return dict(reg=reg, id=n, day=day, hhmm=hhmm, off=off, kind=kind, subject=subject, body=body, f=f)
L = [
 E('L', 1, 0, '08:00', 0, 'NOTICE', 'inbox-hygiene', 'Inbox has three items older than a week.'),
 E('L', 2, 0, '09:30', -5, 'TODO', 'restore-test', 'Run the quarterly restore test.', refs='L-000001'),
 E('L', 3, 0, '12:00', 9, 'WIP', 'spec-draft', 'Drafting the journal spec, section J-04 next.'),
 E('L', 4, 0, '20:00', 0, 'HABIT', 'daily-walk', 'Declared.', habit='walk', cadence='daily', done='yes'),
 E('L', 5, 1, '07:45', -5, 'UPDATE', 'spec-draft', 'J-04 drafted.', refs='L-000003'),
 E('L', 6, 1, '08:10', 0, 'NOTICE', 'stale-file', 'A notes file has not changed in a month.', noticed='2026-11-02T07:58+00:00'),
 E('L', 7, 1, '21:00', 9, 'HABIT', 'daily-walk', 'Done.', habit='walk', done='yes'),
 E('L', 8, 2, '08:00', 0, 'CLOSE', 'inbox-hygiene', 'Inbox emptied.', closes='L-000001', outcome='done'),
 E('L', 9, 2, '10:00', -5, 'TODO', 'weekly-review', 'First weekly review.'),
 E('L', 10, 2, '21:00', 0, 'HABIT', 'daily-walk', 'Skipped.', habit='walk', done='no'),
 E('L', 11, 4, '09:00', 0, 'NOTICE', 'naming', 'The café label on the shelf file is ambiguous.'),
 E('L', 12, 4, '09:20', -5, 'CORRECT', 'stale-file', 'The file is an archive, not stale.', corrects='L-000006'),
 E('L', 13, 4, '22:00', 0, 'HABIT', 'daily-walk', 'Done.', habit='walk', done='yes'),
 E('L', 14, 5, '08:00', 9, 'CLOSE', 'stale-file', 'Archive; nothing to do.', closes='L-000006', outcome='superseded'),
 E('L', 15, 5, '11:00', 0, 'UPDATE', 'naming', 'Renamed the shelf file.', refs='L-000011'),
 E('L', 16, 6, '08:00', 0, 'CLOSE', 'restore-test', 'Restore passed.', closes='L-000002', outcome='done'),
 E('L', 17, 6, '09:00', 0, 'NOTICE', 'promote-target', 'Follow-up from a self entry.'),
 E('L', 18, 6, '21:00', -5, 'HABIT', 'daily-walk', 'Done.', habit='walk', done='yes'),
 E('L', 19, 7, '08:30', 0, 'CLOSE', 'weekly-review', 'Dropped; folded into the next one.', closes='L-000009', outcome='dropped'),
 E('L', 20, 7, '12:00', 0, 'WIP', 'fixture-matrix', 'Building the fixture.'),
 E('L', 21, 8, '08:00', 9, 'UPDATE', 'fixture-matrix', 'Mutants drafted.', refs='L-000020'),
 E('L', 22, 8, '20:30', 9, 'NOTICE', 'late-notice', 'Logged at local midnight.'),
 E('L', 23, 9, '07:00', 0, 'CLOSE', 'late-notice', 'Handled.', closes='L-000022', outcome='done'),
 E('L', 24, 9, '09:00', 0, 'HABIT', 'daily-walk', 'Done.', habit='walk', done='yes'),
]
S = [
 E('S', 1, 0, '22:00', 0, 'THOUGHT', 'first', 'A first note to self.'),
 E('S', 2, 1, '22:00', 0, 'GOAL', 'keep-journal', 'Keep the journal for a full year.'),
 E('S', 3, 2, '22:00', 0, 'REVIEW', 'week-one', 'Week one went as planned.'),
 E('S', 4, 4, '22:30', 0, 'PROSE', 'café', 'Λ wrote this at the café.'),
 E('S', 5, 6, '07:00', 0, 'THOUGHT', 'note', 'Something to act on.'),
 E('S', 6, 6, '09:10', 0, 'THOUGHT', 'promoted-note', 'Promoted the earlier note.', refs='S-000005', promoted='L-000017'),
 E('S', 7, 7, '22:00', 0, 'QUOTE', 'a-line', 'A short quote.'),
 E('S', 8, 9, '22:00', 0, 'REVIEW', 'close-goal', 'Closing the goal early.', closes='S-000002', outcome='done'),
]
ORDER = ['kind', 'subject', 'noticed', 'refs', 'closes', 'outcome', 'corrects', 'habit', 'cadence', 'done', 'promoted']
def ts(e):
    u = BASE + timedelta(days=e['day'], hours=int(e['hhmm'][:2]), minutes=int(e['hhmm'][3:]))
    loc = u.astimezone(timezone(timedelta(hours=e['off'])))
    s = '+' if e['off'] >= 0 else '-'
    return '%s%s%02d:00' % (loc.strftime('%Y-%m-%dT%H:%M'), s, abs(e['off']))
def render(e, swap=False):
    flds = dict(kind=e['kind'], subject=e['subject']); flds.update(e['f'])
    keys = [k for k in ORDER if k in flds]
    if swap: keys[0], keys[1] = keys[1], keys[0]
    return '## %s %s-%06d\n' % (ts(e), e['reg'], e['id']) + ''.join('%s: %s\n' % (k, flds[k]) for k in keys) + '\n' + e['body'] + '\n'
def prefix(es, k):
    return '\n'.join(render(e, e.get('swap', False)) for e in es[:k]).encode('utf-8')
def build(lab, slf, post=None):
    full = {'L': prefix(lab, len(lab)), 'S': prefix(slf, len(slf))}
    chain = {'L': hashlib.sha256(b'J1').digest(), 'S': hashlib.sha256(b'J1').digest()}
    rows = []
    for day in range(0, 10):
        date = (BASE + timedelta(days=day)).strftime('%Y-%m-%d')
        for R, es in (('L', lab), ('S', slf)):
            k = sum(1 for e in es if e['day'] <= day)
            b = prefix(es, k); h = hashlib.sha256(b).digest()
            chain[R] = hashlib.sha256(chain[R] + ('%s %s %d' % (date, R, len(b))).encode('ascii') + h).digest()
            rows.append('%s %s %d %s %s\n' % (date, R, len(b), h.hex(), chain[R].hex()))
    # entries are joined by one blank line; each entry text ends in '\n', so the file ends with one newline
    files = {'lab.txt': full['L'], 'self.txt': full['S'], 'CHAIN.txt': ''.join(rows).encode('ascii')}
    if post: post(files)
    return files
def mutants():
    m = {}
    def cp(): return copy.deepcopy(L), copy.deepcopy(S)
    l, s = cp(); s[3]['body'] = 'Λ wrote this at the café.'; m['I1'] = (l, s, None)
    l, s = cp(); l[4]['swap'] = True; m['I2'] = (l, s, None)
    l, s = cp(); l[23]['id'] = 25; m['I3'] = (l, s, None)
    l, s = cp(); l[15]['day'] = 5; l[15]['hhmm'] = '10:00'; m['I4'] = (l, s, None)
    l, s = cp(); l[11]['f']['corrects'] = 'L-000099'; m['I5'] = (l, s, None)
    l, s = cp(); l[20]['f']['refs'] = 'L-000020, S-000004'; m['I6'] = (l, s, None)
    l, s = cp(); l[18]['f']['closes'] = 'L-000001'; m['I7'] = (l, s, None)
    def post(files):
        b = bytearray(files['lab.txt']); i = b.index(b'Drafting'); b[i] = ord('d'); files['lab.txt'] = bytes(b)
    l, s = cp(); m['I8'] = (l, s, post)
    return m
def write(out, files):
    os.makedirs(out, exist_ok=True)
    for n, b in files.items(): open(os.path.join(out, n), 'wb').write(b)
if __name__ == '__main__':
    out = sys.argv[1]
    write(os.path.join(out, 'base'), build(L, S))
    for k, (l, s, post) in mutants().items():
        write(os.path.join(out, 'mut_' + k), build(l, s, post))
