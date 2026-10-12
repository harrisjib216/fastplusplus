# as-str

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `AssemblyScript` · `MIT` · 🟢 active

> Zero-copy UTF-16/UTF-8 string views for AssemblyScript with SIMD/SWAR search; beats stdlib String on search and ASCII case folding.

| | |
|---|---|
| **Beats** | AssemblyScript standard library String methods (native String ops compiled by asc, run in V8 15.1.42) |
| **Claimed result** | Per-operation chart docs/charts/v0.2.2/per-op-speedup (native = 1.0x, str SIMD build; rounded bar labels; footer 'Wed Jun 24 2026, v0.2.2, v8 15.1.42, a1025c0, main'): replace 11x, indexOf 8.2x, includes 8.1x, toUpperCase 3.9x, toLowerCase 3.8x, replaceAll 3.5x, lastIndexOf 2.5x, trimStart and trimEnd 1.5x, trim 1.4x, padStart 1.4x, padEnd 1.2x, charCodeAt 1.2x, compare 1.1x; slice, substring, split, equals, repeat, concat 1.0x; slower on startsWith 0.7x, endsWith 0.8x, length 0.8x, substr, charAt, at and codePointAt 0.9x. Throughput chart (2 kb input, Mops/s, native / SWAR / SIMD): indexOf and includes about 1 / 4 / 6, toUpperCase and toLowerCase about 1 / 3 / 5, lastIndexOf 11 / 28 / 28, trim 10 / 15 / 15, slice 23 / 22 / 22, compare 11 / 12 / 12, equals 10 / 10 / 10. |
| **Workload** | as-bench microbenchmarks in assembly/__benches__/str.bench.ts: one 1024-UTF-16-unit (2 KB) ASCII string built from a repeated pangram with the needle 'needle' near the end and 8-space trim padding; each suite times a native String method against the str free function on the same input (view-producing ops return a view instead of a copied string; replace/replaceAll replace 'needle' with 'NEEDLE'); per-op chart is the SIMD build, throughput chart shows native, SWAR and SIMD builds. |
| **Metric** | throughput |
| **Compiler and flags** | asc (assemblyscript ^0.28.18) through as-bench ^0.1.0; SIMD build --enable simd --enable bulk-memory, SWAR build --enable bulk-memory --disable simd (as-bench.config.json); warmup 250 ms, measurement 500 ms, 20000 resamples; V8 15.1.42 per the chart footer; optimisation level not stated |
| **Adoption** | 1 star, 0 forks, 28 commits on main; package.json version 0.6.0 (release commit 2026-07-30), no GitHub releases published |
| **Last commit** | 2026-07-30 |
| **Links** | [repository](https://github.com/JairusSW/as-str) · [benchmark](https://github.com/JairusSW/as-str) |

## Verdict

First-party as-bench microbenchmarks (assembly/__benches__/str.bench.ts) at v0.2.2, commit a1025c0, 24 June 2026, V8 15.1.42, CPU not stated: on one 1,024-unit ASCII string the str SIMD build ran indexOf/includes about 0.75 vs 6.3 Mops/s (8.1-8.2x), lastIndexOf 11 vs 28 Mops/s (2.5x), toUpperCase/toLowerCase 3.8-3.9x and replace 11x faster than the AssemblyScript 0.28 stdlib String compiled with the same flags, while equals, compare, slice and most single-character queries were 0.7-1.1x. Both arms are in the same module, and the equality test uses a distinct copy so the stdlib's pointer-equality shortcut does not fire, so the comparison is fair, but it covers only that one input.

## Use it when

- Substring search (indexOf, includes, replace) on haystacks of hundreds to thousands of UTF-16 units in AssemblyScript: 8.1-8.2x for indexOf/includes and 11x for replace on a 1,024-unit ASCII string (author's v0.2.2 chart).
- ASCII case folding (toUpperCase/toLowerCase) of mostly-ASCII text such as headers, identifiers or keys: about 3.8-3.9x over the stdlib's Unicode-aware loop.
- Tokenizing and trimming input (log lines, request lines, CSV fields) where most substrings are inspected and discarded rather than kept, so materialization is rare.
- Text that already lives as UTF-8 bytes (WASI, network, JSON payloads): `str8.fromBuffer` slices and searches it without transcoding to UTF-16.
- An existing AssemblyScript codebase that can try the `as-str/auto` transform, which turns safe internal string locals into allocation-free packed spans without source edits (measure on your own workload, as the README advises).

## Skip it when

- Cheap per-call queries: length, charAt, at, codePointAt and substr measured 0.8-0.9x and startsWith/endsWith 0.7-0.8x of native on the author's chart; slice, substring, split, equals, repeat and concat are about 1.0x.
- Non-ASCII text in toUpperCase/toLowerCase: the fast path bails out and the view is materialized and passed to the native method, which adds a copy over calling native directly.
- Code that needs JavaScript String semantics or passes strings across many API boundaries: semantics mirror AssemblyScript's String, views are a distinct type, and every boundary crossing costs a `toString()` copy.
- Long-lived small slices of large inputs: a view keeps its whole backing string reachable, so a retained 10-character view pins the full source buffer.
- Projects that need a proven dependency: single author, 1 star, no issues filed, 11 npm releases between 24 June and 30 July 2026, and the published charts predate the v0.4-0.6 transform rewrite.

## How it is fast

Search uses a memchr-style first-code-unit filter (`findUnit`) that tests 8 UTF-16 units per step with `i16x8.eq` + bitmask under `--enable simd`, or 4 units per step with Mycroft's SWAR zero-lane trick on u64 words otherwise, then confirms the tail with a size-tiered byte compare; the stdlib's `indexOf` instead calls `compareImpl` at every candidate position. Case conversion checks the range is ASCII with one vector scan and folds a-z/A-Z in a single allocate-and-fold pass, where the stdlib over-allocates 3x, walks the Unicode special-case tables per code unit and then reallocates. View-producing ops (slice, trim, split) move two pointers instead of copying characters, so they avoid copying characters but still allocate one view object.

## Compared with alternatives

Among the catalogued AssemblyScript entries, as-string-sink (MaxGraey) speeds up building strings by concatenation, and json-as (same author) parses JSON; pick as-str when the hot path reads existing text (search, trim, slice, case-fold), and combine it with as-string-sink when you also build output.

## Integration

| | |
|---|---|
| **Form** | module (npm package of AssemblyScript source, plus optional asc transforms as-str/global, as-str/auto, as-str/single) |
| **Dependencies** | utf-as ^0.3.1 (UTF-8/UTF-16 encode and decode); peer dependency assemblyscript &gt;=0.28.10 |
| **Minimum toolchain** | AssemblyScript asc 0.28.10+ (benchmarked with ^0.28.18); SIMD tier needs --enable simd, otherwise the SWAR tier is compiled |
| **Platforms** | any WebAssembly host that runs asc output; SIMD path needs Wasm SIMD128 support (chosen at compile time via ASC_FEATURE_SIMD); views rely on AssemblyScript's non-moving GC |
| **Thread safety** | not documented (views are plain GC objects; AssemblyScript modules are single-threaded per instance) |
| **Drop-in for the baseline** | partial — the free functions take a native string and return the same results as String methods (differential-fuzzed per the README), and as-str/auto rewrites native string code automatically, but `str` is a separate type and view results must be materialized with toString() wherever a native string is required |

## Gotchas

- lastIndexOf is not SIMD/SWAR accelerated at HEAD: util.ts `lastIndexOf` is a scalar backward loop that only checks the first code unit before the tail compare, although the README's Architecture section says `findUnit` powers it; the throughput chart accordingly shows identical SWAR and SIMD bars (28 Mops/s), and its 2.5x comes from skipping the stdlib's per-position compareImpl call.
- 'Without allocating' applies only to the transforms' packed spans: every `str.slice`, `trim`, `split` piece is a heap-allocated 3-field Str object (the Architecture section says a view op is exactly one allocation), which is why view ops chart at 1.0-1.5x rather than large gains.
- replaceAll scans the haystack twice (a counting pass, then a copy pass, each calling indexOf until no match), so it gains 3.5x versus replace's 11x; str.replace and replaceAll also return a fresh copy when nothing matches, whereas the stdlib returns the original string.
- Benchmark scope: one 1,024-unit ASCII string with the needle at code unit 953 (8 pad + 21 x 45-unit phrase, derived from str.bench.ts) and one 'n' false candidate per phrase; no non-ASCII input, short haystack or needle-dense case is measured, and the charts carry no CPU or OS.

## Known shortcomings

- Numbers match the v0.2.2 charts (replace 11x, indexOf 8.2x) but there is no CPU model, one 2 KB input, the chart predates v0.6.0 and several operations run at 0.7-0.9x native.
- Harness fair (same module and flags, equality test on a distinct copy). At HEAD lastIndexOf is a scalar backward loop despite the README's findUnit claim (SWAR and SIMD both 28 Mops/s); every view still heap-allocates a Str object, so view ops gain only 1.0-1.5x; replaceAll scans twice (3.5x vs replace's 11x); the benchmark is one 1,024-unit ASCII input with the needle at unit 953; charts are v0.2.2 only with no CPU.

## Caveats and trade-offs

Charts are from v0.2.2 (commit a1025c0, 2026-06-24) while the repo is now at v0.6.0; no CPU or OS stated; baseline is the AssemblyScript stdlib String, not JavaScript or C++; values are read from chart images with rounded labels; a single 2 KB ASCII input with one needle near the end, so the search speedups reflect SIMD/SWAR scanning versus the stdlib's scalar loop on a long haystack; view-producing ops compare returning a view with copying a string, a semantic difference; several ops are 0.7-0.9x of native; the README's Flavors link to github.com/AssemblyScript/as-str returns 404.

A str is a 3-field view over a UTF-16 string, so it is a different type from String (conversions needed at API boundaries); several operations (startsWith, endsWith, length, charAt) are slower than native; semantics mirror AssemblyScript String, not JavaScript.

## Maintenance

Active single-author project (npm 0.1.0 to 0.6.0 between 24 June and 30 July 2026, last commit 2026-07-30), MIT and small enough to vendor, but the only published charts are for v0.2.2, so re-measure on current code; the README's Flavors link (github.com/AssemblyScript/as-str) is a 404.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party as-bench microbenchmarks (assembly/__benches__/str.bench.ts, as-bench.config.json, scripts/build-charts.sh) against the AssemblyScript native String methods; build flags (--enable simd --enable bulk-memory, or --disable simd for SWAR) and V8 15.1.42 are stated, but no CPU model, OS or asc optimisation level, so not A.
- **Verifier notes:** Numbers match the v0.2.2 per-op and throughput charts (PNG and SVG on the docs branch); bench code is public and the native baseline is built with the same flags. Shortcomings: no CPU model, single input chosen by the author, chart predates current v0.6.0, several ops slower than native.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-65 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/JairusSW/as-str>
  - <https://github.com/JairusSW/as-str/commits>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/README.md>
  - <https://github.com/JairusSW/as-str/tree/docs/charts/v0.2.2>
  - <https://raw.githubusercontent.com/JairusSW/as-str/refs/heads/docs/charts/v0.2.2/per-op-speedup.png>
  - <https://raw.githubusercontent.com/JairusSW/as-str/refs/heads/docs/charts/v0.2.2/throughput.png>
  - <https://raw.githubusercontent.com/JairusSW/as-str/refs/heads/docs/charts/v0.2.2/per-op-speedup.svg>
  - <https://raw.githubusercontent.com/JairusSW/as-str/refs/heads/docs/charts/v0.2.2/throughput.svg>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/as-bench.config.json>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/package.json>
  - <https://github.com/JairusSW/as-str/tree/main/assembly/__benches__>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/assembly/__benches__/str.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/scripts/build-charts.sh>
  - <https://github.com/AssemblyScript/as-str>
- **Sources the enricher read:**
  - <https://github.com/JairusSW/as-str>
  - <https://github.com/JairusSW/as-str/issues?q=is%3Aissue>
  - <https://github.com/JairusSW/as-str/tree/docs/charts>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/README.md>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/package.json>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/as-bench.config.json>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/asconfig.json>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/CONTEXT.md>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/assembly/index.ts>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/assembly/str.ts>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/assembly/util.ts>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/assembly/__benches__/str.bench.ts>
  - <https://raw.githubusercontent.com/JairusSW/as-str/HEAD/scripts/build-charts.sh>
  - <https://raw.githubusercontent.com/JairusSW/as-str/refs/heads/docs/charts/v0.2.2/per-op-speedup.svg>
  - <https://raw.githubusercontent.com/JairusSW/as-str/refs/heads/docs/charts/v0.2.2/throughput.svg>
  - <https://raw.githubusercontent.com/JairusSW/as-str/refs/heads/docs/charts/v0.2.2/throughput.png>
  - <https://registry.npmjs.org/as-str>
  - <https://github.com/JairusSW/as-bench>
  - <https://raw.githubusercontent.com/JairusSW/as-bench/HEAD/assembly/index.ts>
  - <https://raw.githubusercontent.com/JairusSW/as-bench/HEAD/as-bench.config.json>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/main/std/assembly/string.ts>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/main/std/assembly/util/string.ts>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jairussw/as-str`) · [data/wave13/enrich/raw/github_com_jairussw_as_str.json](../../../data/wave13/enrich/raw/github_com_jairussw_as_str.json) (enrichment confidence 0.7)

</details>
