# swisseph-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust FFI over C (Swiss Ephemeris 2.10.03) compiled to WebAssembly` · `MIT for the wrapper (LICENSE, Cargo.toml, deno.json), but the WASM compiles in Swiss Ephemeris 2.10.03 C sources (vendor/swisseph submodule of aloistr/swisseph), which are dual-licensed AGPL-3.0 or Swiss Ephemeris Professional License (the README calls it 'GPL/Commercial')` · 🟢 active

> Swiss Ephemeris 2.10.03 C compiled to WASM through a Rust wasm-bindgen shim; beats astronomy-engine on Moon positions only (1.44x).

| | |
|---|---|
| **Beats** | astronomy-engine 2.1.19 (pure-JavaScript astronomy library; version pinned in deno.json and benches/browser_bench.html) |
| **Claimed result** | Moon position: \~182,000 iter/s vs \~126,000 iter/s for astronomy-engine, '1.44x Faster' (Deno bench). Sun position is slower: \~319,000 vs \~577,000 ops/s in Chrome and \~178,000 vs \~434,000 ops/s in Deno ('the overhead of calling WebAssembly dominates. Pure JS is faster here'). |
| **Workload** | One fixed date (2000-01-01 12:00 UT) repeated every iteration. benches/comparison.ts (deno bench): swe_julday + swe_calc_ut(SE_SUN or SE_MOON, SEFLG_SWIEPH\|SEFLG_SPEED) vs astronomy-engine GeoVector(Body, new Date('2000-01-01T12:00:00Z'), aberration=true). benches/deno_throughput.ts and benches/browser_bench.html: 100,000 Sun iterations each, timed with performance.now(). |
| **Metric** | throughput |
| **Adoption** | 4 stars; JSR, npm and crates.io badges in README |
| **Last commit** | 2026-01-12 |
| **Links** | [repository](https://github.com/fusionstrings/swisseph-wasm) · [benchmark](https://github.com/fusionstrings/swisseph-wasm) |

## Verdict

The first-party README tables (no hardware or versions) show swe_calc_ut for the Moon at about 182,000 iter/s vs astronomy-engine 2.1.19 GeoVector at about 126,000 iter/s in deno bench (1.44x). For the Sun it loses: about 319,000 vs 577,000 ops/s in Chrome and 178,000 vs 434,000 in Deno, with 100,000 iterations timed by performance.now(). All rows are one fixed date, and the WASM side runs the Moshier fallback twice per call.

## Use it when

- You already use Swiss Ephemeris conventions (swe_\* calls, SE_/SEFLG_ constants, sidereal modes, ayanamsa) and need them in a browser or Deno/Node without a native addon.
- Moon-heavy batch work (e.g. lunar tables) where the README's Deno bench shows about 182,000 vs 126,000 iter/s over astronomy-engine.
- Astrology-style output (apparent ecliptic longitude/latitude with daily speeds) where Moshier-level precision is enough; swemmoon.c quotes at most 7 arcsec longitude error for the Moshier Moon over -3000 to +3000.
- AGPL-3.0-compatible projects, or projects holding a Swiss Ephemeris Professional License.

## Skip it when

- Sun and other cheap per-call positions: the README itself shows astronomy-engine faster (about 577,000 vs 319,000 ops/s in Chrome, 434,000 vs 178,000 in Deno).
- When you need the SE1 file ephemerides or JPL files: fopen, fread and stat are stubbed (src/lib.rs) and swe_set_ephe_path is not exported, so every SEFLG_SWIEPH call silently falls back to Moshier.
- Fixed stars: swe_fixstar_ut needs sefstars.txt, which can never be opened in this build (per source reading, not run).
- Closed-source or permissively licensed products: the MIT label covers only the wrapper; the bundled Swiss Ephemeris is AGPL-3.0 or commercial.
- Production use needing maturity: 4 stars, 26 commits all from 2026-01-06 to 2026-01-12, tests that only range-check the Sun longitude (275-285 degrees) and Moon latitude.

## How it is fast

There is no algorithmic trick: the C library is compiled with clang for wasm32-unknown-unknown (build.rs sets warnings and the target but no -O flag; the libc is replaced by Rust shims over libm and a header-tagged malloc), and calls go through wasm-bindgen. The Moon win comes from running compiled C for the lunar series instead of JIT-compiled JavaScript. On cheap calls the binding cost dominates: each swe_calc_ut builds its result with Object::new plus seven Reflect::set imports across the WASM/JS boundary, which is why the Sun rows lose to pure JS.

## Compared with alternatives

No astronomy siblings are catalogued; the closest pattern is hash-wasm (C compiled to WASM behind a JS API). Unlike hash-wasm, this one wins only on its heavier call (Moon) and loses on light calls, so use it for Swiss Ephemeris API parity rather than speed.

## Integration

| | |
|---|---|
| **Form** | module (JSR @fusionstrings/swisseph-wasm 0.1.5, npm, crates.io crate; browser build with the WASM inlined) |
| **Dependencies** | none at runtime (WASM plus wasm-bindgen glue); build needs Rust with wasm32-unknown-unknown, clang/LLVM with a wasm32 target, Deno and @deno/wasmbuild ^0.21.0 |
| **Minimum toolchain** | Rust edition 2024 (1.85+), wasm-bindgen 0.2.106, Deno 2.x for build and tests; runtime: any WebAssembly host (Deno, Node, Bun, browsers) |
| **Platforms** | any WebAssembly runtime with JS glue |
| **Thread safety** | not documented; Swiss Ephemeris keeps global state (the swed struct with per-planet save areas, topo and sidereal settings), so treat each instance as single-threaded and one per worker |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the numbers (per source reading of src/lib.rs and vendored sweph.c 2.10.03, not run): the benchmarks request SEFLG_SWIEPH, but fopen returns NULL, so each call first tries the file path, falls back to Moshier, and then swe_calc_ut sees the returned ephemeris flag differ from the requested one and recomputes with a new delta T. The save-area cache never hits because the saved flags (MOSEPH) never equal the requested ones (SWIEPH). Every measured iteration therefore does two Moshier computations; requesting SEFLG_MOSEPH would likely be faster, and the README's 'more accurate' claim describes Moshier, not the SE1 files.
- The fallback is silent: the C stubs make sprintf write an empty string and printf/fprintf no-ops, so Swiss Ephemeris warnings and error texts (including 'not found in PATH ... using Moshier') come back blank. Check rc_flags & 4 (SEFLG_MOSEPH) yourself. qsort is a no-op, bsearch returns NULL and atof/atoi/sscanf return 0, so any code path that parses or sorts data is broken.
- build.rs defines NO_MOSHIER with the comment 'Use JPL ephemeris only', but neither the vendored sweph.c nor sweph.h references that macro, so it does nothing: Moshier is the only ephemeris that can run.
- The workloads differ: Swiss Ephemeris returns apparent ecliptic-of-date coordinates with speeds, while astronomy-engine GeoVector returns a J2000 equatorial vector without velocity. comparison.ts also parses a Date string inside every astronomy-engine iteration, deno_throughput.ts warms up only astronomy-engine, every row uses one fixed date (2000-01-01 12:00 UT), and no CPU, Deno, Chrome or compiler flags are stated.

## Known shortcomings

- Wins the Moon row only (1.44x) and loses the Sun rows; src/lib.rs stubs fopen to NULL, so SEFLG_SWIEPH probably falls back to Moshier and computes twice per call (source reading); MIT wrapper around the AGPL-3.0 or commercial Swiss Ephemeris (mixed).
- Enricher: confirms the verifier's finding against the vendored sweph.c 2.10.03 (the fopen stub forces the Moshier fallback, swe_calc_ut recomputes on flag mismatch and the save-area cache never hits, so two Moshier computations per timed call); the build.rs NO_MOSHIER define is a no-op, the sprintf stub blanks all warnings and errors so the fallback is silent, qsort is a no-op, bsearch returns NULL, atof/atoi return 0 and swe_fixstar_ut cannot work (source reading); each call costs 7 Reflect::set boundary imports, explaining the Sun losses; 26 commits 2026-01-06 to 01-12, dormant since.

## Caveats and trade-offs

One winning row (Moon, Deno bench only) against two losing rows (Sun, Chrome and Deno); no CPU, Deno or Chrome versions stated. The two libraries return different things (Swiss Ephemeris ecliptic longitude/latitude/distance with speeds vs astronomy-engine's equatorial J2000 GeoVector), so work per call differs. Per source reading (not run): the WASM build stubs fopen to return NULL (src/lib.rs), so no ephemeris files can load and SEFLG_SWIEPH silently falls back to the Moshier analytic ephemeris on every call; the README's 'high-precision'/'more accurate' claim therefore refers to Moshier, not the SE1 files, and swe_calc_ut then repeats the calculation because the returned ephemeris flag differs from the requested one (sweph.c), so the WASM side likely does two computations per call and its save-area cache never hits. In comparison.ts the astronomy-engine loop parses a Date string every iteration while the WASM loop calls swe_julday; deno_throughput.ts warms up only astronomy-engine. Swiss Ephemeris AGPL terms apply to anything distributing the WASM binary.

Bundles the Swiss Ephemeris C library, which the README describes as GPL/Commercial dual licensed, while the wrapper code is MIT, so redistribution inherits the ephemeris terms. Boundary-call overhead makes simple calls slower than pure JS.

## Maintenance

A one-week project (26 commits, 2026-01-06 to 2026-01-12) with no activity since and a single open self-PR, so it is dormant rather than active. Usability is mixed: the wrapper is MIT, but shipping the WASM binary carries Swiss Ephemeris AGPL-3.0 or commercial terms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks tables match the record (Moon \~182,000 vs \~126,000 iter/s, '1.44x Faster', Deno bench; Sun \~319,000 vs \~577,000 ops/s Chrome and \~178,000 vs \~434,000 ops/s Deno). Bench code is public (benches/comparison.ts via 'deno task bench', benches/deno_throughput.ts, benches/browser_bench.html) but no CPU, Deno, Chrome or compiler versions are stated, so first-party C.
- **Verifier notes:** Numbers verified on README; harness is public but lacks hardware/versions. Main shortcomings: wins only the Moon row (1.44x) and loses Sun rows \~1.8-2.4x; fopen stub means SEFLG_SWIEPH falls back to Moshier (no ephemeris files in WASM, rc_flags never checked); MIT label covers only the wrapper, bundled Swiss Ephemeris is AGPL-3.0/commercial. Metadata checked: 4 stars, last commit 2026-01-12 on branch 'creation', not a fork.
- **Fields the verifier corrected:** `baseline`, `license`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-121 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/fusionstrings/swisseph-wasm>
  - <https://github.com/fusionstrings/swisseph-wasm/commits>
  - <https://github.com/fusionstrings/swisseph-wasm/tree/creation/benches>
  - <https://github.com/fusionstrings/swisseph-wasm/tree/creation/src>
  - <https://github.com/fusionstrings/swisseph-wasm/tree/creation/wasm-includes>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/benches/comparison.ts>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/benches/deno_throughput.ts>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/benches/deno_direct_wasm.ts>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/benches/browser_bench.html>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/deno.json>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/build.rs>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/src/wrapper/stub.c>
  - <https://raw.githubusercontent.com/aloistr/swisseph/HEAD/sweph.c>
  - <https://raw.githubusercontent.com/aloistr/swisseph/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/fusionstrings/swisseph-wasm>
  - <https://github.com/fusionstrings/swisseph-wasm/commits/creation>
  - <https://github.com/fusionstrings/swisseph-wasm/tree/creation/tests>
  - <https://github.com/fusionstrings/swisseph-wasm/tree/creation/vendor>
  - <https://github.com/fusionstrings/swisseph-wasm/pulls>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/benches/comparison.ts>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/benches/deno_throughput.ts>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/benches/deno_direct_wasm.ts>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/benches/browser_bench.html>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/deno.json>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/build.rs>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/src/wrapper/stub.c>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/mod.ts>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/tests/integration_test.ts>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/tests/node_verification.js>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/vendor/swisseph/sweph.c>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/vendor/swisseph/sweph.h>
  - <https://raw.githubusercontent.com/fusionstrings/swisseph-wasm/HEAD/vendor/swisseph/swephexp.h>
  - <https://raw.githubusercontent.com/aloistr/swisseph/HEAD/sweph.c>
  - <https://raw.githubusercontent.com/aloistr/swisseph/HEAD/swephexp.h>
  - <https://raw.githubusercontent.com/aloistr/swisseph/HEAD/swemmoon.c>
  - <https://raw.githubusercontent.com/aloistr/swisseph/HEAD/sweodef.h>
  - <https://raw.githubusercontent.com/aloistr/swisseph/HEAD/swephlib.c>
  - <https://raw.githubusercontent.com/aloistr/swisseph/HEAD/swedate.c>
  - <https://github.com/cosinekitty/astronomy>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/fusionstrings/swisseph-wasm`) · [data/wave13/enrich/raw/github_com_fusionstrings_swisseph_wasm.json](../../../data/wave13/enrich/raw/github_com_fusionstrings_swisseph_wasm.json) (enrichment confidence 0.65)

</details>
