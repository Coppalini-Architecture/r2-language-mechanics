#!/usr/bin/env node
'use strict';
// qsa_check.js SCHEMA.json FIXTURE.txt -- second-runtime implementation of tools/qsa_check.py (record 0006).
// Same checks, same output text, so the output can be diffed byte for byte against RESULTS.txt.
// Node, built-in modules only. Exit 0 on PASS, 1 on FAIL, 2 on usage.
const fs = require('fs');
const crypto = require('crypto');

const PIN = 'c85c2f34eb9ff6fd2e01463be9f7eb6afb5414a8eb97ddd24fb5fac59675caad';
const LAW = 'a = s + 137 * mod(q - s, 4)';
const SAFE = Number.MAX_SAFE_INTEGER; // 2^53 - 1

// Non-negative residue in 0..m-1. JS % truncates toward zero; this repairs the sign.
function nmod(x, m) { return ((x % m) + m) % m; }
function law(q, s) { return s + 137 * nmod(q - s, 4); }
const eq = (a, b) => a.length === b.length && a.every((v, i) => v === b[i]);

if (process.argv.length !== 4) { process.stderr.write('usage: qsa_check.js SCHEMA.json FIXTURE.txt\n'); process.exit(2); }
const raw = fs.readFileSync(process.argv[2]);
const sch = JSON.parse(raw.toString('utf8'));
const out = [];
let ok = true;
function rec(name, good, detail) {
  ok = ok && good;
  out.push(name + ' ' + (good ? 'PASS' : 'FAIL') + (detail ? ' ' + detail : ''));
}

out.push('QSA CHECK');
rec('S0 sha256 pin', crypto.createHash('sha256').update(raw).digest('hex') === PIN, raw.length + ' bytes');
rec('S1 declared law text', sch.dome_receipt.dome.law === LAW);
const dom = sch.finite_address.domains;
rec('S2 declared domains', Object.keys(dom).length === 3 && dom.q === '0..3' && dom.s === '0..136' && dom.a === '0..547');

const vals = new Map();
for (let q = 0; q < 4; q++) for (let s = 0; s < 137; s++) vals.set(q + ',' + s, law(q, s));
const all = [...vals.values()];
rec('A1 range', all.every(a => a >= 0 && a <= 547), vals.size + ' pairs');
rec('A2 uniqueness', new Set(all).size === 548, new Set(all).size + ' distinct');
rec('A3 coverage', new Set(all).size === 548 && all.every(a => Number.isInteger(a) && a >= 0 && a <= 547));
rec('A4 a mod 4 = q', [...vals].every(([k, a]) => a % 4 === +k.split(',')[0]));
rec('A5 a mod 137 = s', [...vals].every(([k, a]) => a % 137 === +k.split(',')[1]));
rec('A6 round-trip (q,s)->a->(q,s)', [...vals].every(([k, a]) => { const [q, s] = k.split(',').map(Number); return a % 4 === q && a % 137 === s; }));
let a7 = true;
for (let a = 0; a < 548; a++) if (law(a % 4, a % 137) !== a) a7 = false;
rec('A7 round-trip a->(q,s)->a', a7);

// F1: the fixture file is parsed; every field is compared with the recomputation.
const DECLARED = [-SAFE, -411, -138, -137, -136, -2, -1, 0, 1, 136, 137, 138, 411, SAFE];
const canon = t => /^-?[0-9]+$/.test(t) && BigInt(t).toString() === t && Number.isSafeInteger(Number(t));
let reason = '';
const rows = [];
try {
  const ftxt = new TextDecoder('utf-8', { fatal: true }).decode(fs.readFileSync(process.argv[3]));
  for (const ln of ftxt.split('\n')) {
    if (ln === '' || ln.startsWith('#')) continue;
    const f = ln.split(' ');
    if (f.length !== 6 || !f.every(canon)) { reason = 'malformed row: ' + ln.slice(0, 40); break; }
    rows.push(f.map(Number));
  }
  if (!reason && !eq(rows.map(r => r[0]), DECLARED)) reason = 'inputs differ from the 14 declared (count ' + rows.length + ')';
  if (!reason) {
    for (const r of rows) {
      const s = nmod(r[0], 137);
      if (!eq(r.slice(1), [s, law(0, s), law(1, s), law(2, s), law(3, s)])) { reason = 'value mismatch at s_input ' + r[0]; break; }
    }
  }
} catch (e) { reason = 'fixture unreadable'; }
rec('F1 s_input fixture file, 14 rows x 6 fields', reason === '', reason);
if (reason === '') for (const r of rows) out.push('  s_input ' + r[0] + ' -> ' + r[1]);
out.push('RESULT ' + (ok ? 'PASS' : 'FAIL'));
process.stdout.write(out.join('\n') + '\n');
process.exit(ok ? 0 : 1);
