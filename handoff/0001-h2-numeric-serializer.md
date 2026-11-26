# 0001 — H² numeric serializer: cross-engine evidence

From: Claude (carried by AVC). Date: 2026-11-26. Status of address: OPEN, evidence added.

- **Source** — (a) `Clear_Onyx_lotus_lift_authored.html`, 92,428 bytes, SHA-256 `4e90491e6740f474c02373c9ea4f343b81af4d21df7691956ea2586f3eb9b8b1`; disclosure path `discloseContext`, `discloseNext`, `completeDisclosure`. (b) `OPEN.md` row "H² numeric serializer" at repository commit `44f499efe61b87885c445f0890a335d23044e678`. (c) `h2_trig_check.zip`, SHA-256 `dc5259ded070256e879145d0c6f285d697ffc559725f64bd79c37ccd4301da00`, holding `trig.js` `c06f1bf903f19543f7765e9ad318dd2792b93002dd3ee783f9a971003329b72a`, `trig.py` `58817d301d4dac0a4152aa432c6d7519f5a503d18ea7cd13f25ed0e4d2ec3882`, `e2e.js` `5105aac196b5b878b7f34c9c5f083df1434ac3b32ba2b63cfeebae3ebf6e8fbd`, `e2e.py` `d252fba7c0d7de4132775891dfae5266307017ccef8cb3706e68148f954b7376`.

- **Reader** — V8 (Node v22.23.5) against CPython 3 on glibc 2.39 libm, same operation order. Resolution: binary64 bit pattern, and 9-decimal fixed form (`toFixed(9)` / `%.9f`). Quantity read: the 28 values ω(Sᵢ,Sⱼ) = Sᵢ₀Sⱼ₁ − Sᵢ₁Sⱼ₀ at r = 0.55, ε = 0.06, c ∈ {0, 3, 20}, θ over the `atlasTheta` slider grid (−3.1416 to 3.1416, step 0.005).

- **Claim** — `construction`. Two engines, one platform, one parameter slice. Not proven.

- **Check** — In the unpacked zip: `node trig.js && python3 -I trig.py`, then `node e2e.js && python3 -I e2e.py`. `trig` compares `Math.cos`/`Math.sin` against libm bit for bit over the slider grid and 10⁶ pseudo-random θ in [−π, π]. `e2e` compares all 28 ω, bit for bit and after 9-decimal rounding.

- **Receipt** — `trig`: 83 of 1,257 slider-grid θ differ in the last bit of cos or sin (6.6%); 64,102 of 1,000,000 random θ differ (6.4%). `e2e`: 3,771 points; binary64 differs at 229 (6.1%); 9-decimal form differs at 0. Also observed: `(-1e-12).toFixed(9)` and `'%.9f' % -1e-12` both give `-0.000000000`; `(-0).toFixed(9)` gives `0.000000000`.

- **Delta** — INITIAL — no predecessor. Witnessed change against `OPEN.md@44f499e`: that row states no numeric form. This record shows raw binary64 is not a valid cross-engine receipt form for the disclosure path, that 9-decimal fixed form was stable on this slice, and that the file's own `toExponential(3)` display of A₂₈ (four significant digits) is too coarse to serve as a receipt field.

- **Open** — (1) Boundary guard: flag values near a rounding tie, or round by exact rational arithmetic. (2) Canonicalize `-0.000000000` to `0.000000000` after rounding, since a tiny value whose sign differs between engines would otherwise print differently. (3) Repeat the check for the remaining H² quantities (horizon V, loop closure), which also use `exp`, `log`, `atan2`, `tanh`, `sqrt`, and add a third engine (SpiderMonkey or JavaScriptCore). (4) Declare a digit width per field: Σs, Σa, Σr, and the four entries of A₂₈.
