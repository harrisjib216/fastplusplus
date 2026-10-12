# BlazeDiff core-wasm (@blazediff/core-wasm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust image diff compiled to wasm32 with v128 SIMD; pixelmatch-style YIQ diff counts, about 2-6x faster than pixelmatch on large differing images.

| | |
|---|---|
| **Beats** | pixelmatch (JavaScript) |
| **Claimed result** | README table (Node.js 22, Apple M1 Max, tinybench): '\~50.8% faster on average than pixelmatch' (the arithmetic mean of per-row '% time saved' over 34 rows, 17 of them identical pairs; geometric-mean speedup about 2.3x, about 3.0x on differing rows only, derived from page data); 4k/1 332.26 ms vs 33.18 ms (about 10x as printed, about 6.1x against the 201.60 ms the same pixelmatch takes in the repo's separate JS run); 4k/3 423.14 vs 44.65 ms; small blazediff/1 1.24 vs 0.24 ms; identical pairs near parity (4k/2 identical 22.70 vs 22.17 ms). The package README's 'up to \~16x faster than pixelmatch on 4K' exceeds the table's largest ratio (10.0x). The plain-JS @blazediff/core is 4-7x faster than this wasm build on identical pairs. |
| **Workload** | Pixel-by-pixel YIQ perceptual image diff of PNG fixtures (4K, \~1.6 MP and page-sized images, with identical-pair variants), decode excluded, 25 iterations after 5 warmup, Node.js. |
| **Metric** | latency |
| **Hardware** | Apple M1 Max, Node.js 22, macOS (BENCHMARKS.md 'Hardware Specifications') |
| **Compiler and flags** | Rust (rustc version not stated), cargo build --release for wasm32-unknown-unknown with RUSTFLAGS='-C target-feature=+simd128,+bulk-memory' and the workspace release profile in crates/Cargo.toml (opt-level 3, lto = "fat", codegen-units 1, panic = abort), wasm-bindgen 0.2.100 post-processing, then wasm-opt -O3 only if wasm-opt is installed (crates/blazediff/scripts/build-wasm.sh); harness apps/image-benchmark (tinybench 5, pixelmatch ^7.2.0) under Node.js 22. |
| **Adoption** | 351 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/teimurjan/blazediff) · [benchmark](https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/benchmarks/pixel-by-pixel.md) |

## Verdict

benchmarks/pixel-by-pixel.md (updated 2026-07-29 with PR #91) times @blazediff/core-wasm against pixelmatch ^7.2.0 in one tinybench 5 process (25 iterations after 5 warmup, pre-decoded PNG buffers, no output buffer, threshold 0.1) on an Apple M1 Max under Node 22. Results: 4k/1 33.18 vs 332.26 ms, 4k/3 44.65 vs 423.14 ms, page/2 73.42 vs 513.06 ms, and identical 4K and page-sized pairs only 2-32% faster. The module is built with Rust +simd128, lto fat and opt-level 3; whether wasm-opt ran is not recorded.

## Use it when

- Visual-regression or screenshot diffing in a browser, a Cloudflare Worker, Deno or Bun, where native addons (@blazediff/core-native) are not available and the screenshots usually differ.
- Large differing pairs (1-18 MP) where pixelmatch takes 100-500 ms per call. The first-party table shows 33-73 ms on 4K and page-sized fixtures on an M1 Max under Node 22.
- You need pixelmatch-compatible counts (YIQ threshold 0.1, AA pixels excluded by default) and can accept a \~0.05% difference in counts.
- You want a small artifact with no postinstall step: about 32 KB of optimized wasm plus about 10 KB of JS glue, per the package README.

## Skip it when

- Most of your pairs are identical or nearly identical, as in a passing visual-regression suite. wasm-bindgen copies both inputs into linear memory on every call (about 143 MB for the 17.9 MP 4k/1 pair). On identical pairs the same repo's plain-JS @blazediff/core is 4-7x faster than this build (4k/1 identical: 2.50 ms vs 17.47 ms; same/1: 0.22 vs 1.11 ms), and on the 4K and page-sized identical pairs core-wasm's lead over pixelmatch shrinks to 2-32%.
- Small images under about 0.1 MP. Absolute savings are a fraction of a millisecond, and pixelmatch/6 shows only 0.75 vs 0.67 ms.
- Hosts without WebAssembly SIMD. build-wasm.sh produces only a +simd128 artifact and ships no scalar fallback.
- You need bit-identical parity with pixelmatch, such as golden counts stored in tests. Counts differ slightly (4k/1: 69,932 vs 69,912), and PR #91 (2026-07-29) changed counts on images with alpha.
- You need region analysis. It was moved to @blazediff/interpret-native, a Node N-API package with no wasm build.

## How it is fast

It is a two-pass block algorithm. The cold pass splits the image into blocks (8 to 128 px, sized from image area) and scans them with v128 integer compares plus an integer early-reject bound: delta &lt;= lambda_max \* (dr^2+dg^2+db^2) for opaque pixels. That skips blocks with no pixel above the threshold. The hot pass runs the 4-lane f32x4 YIQ delta and the anti-aliasing check only on the changed blocks, and drops to a scalar kernel for semi-transparent lanes. The module is built with RUSTFLAGS +simd128,+bulk-memory, lto fat, codegen-units 1 and opt-level 3, and wasm-opt -O3 is applied only if it is installed.

## Compared with alternatives

This is the only perceptual image-diff entry in the wasm category. Pick it over WebDSP (image filters, no published numbers) when you need a pixelmatch-compatible diff count with a same-harness benchmark. Pick it over writing your own wasm kernel in the style of zaw or kmeans-wasm when you want a maintained, published npm package with the same algorithm as the repo's native and Python builds.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (wasm-bindgen 0.2.100 glue is bundled); building from source needs Rust with the wasm32-unknown-unknown target, wasm-bindgen-cli 0.2.100 and optionally wasm-opt |
| **Minimum toolchain** | Node 18+ per README (Node 20.6+ for the import.meta.resolve recipe); any browser or edge runtime with WebAssembly SIMD (v128); rustc version for builds not stated |
| **Platforms** | any wasm host with SIMD128: browsers, Node, Cloudflare Workers, Deno, Bun; benchmarks only on Apple M1 Max under Node 22 |
| **Thread safety** | not documented; one module instance per JS realm, a synchronous call under an async wrapper, no threads |
| **Drop-in for the baseline** | partial: same algorithm family and similar options as pixelmatch, but you must call initBlazediff first, diff() returns a Promise, the argument order differs (output after width/height), and counts differ by up to \~0.05% |

## Gotchas

- Harness flaw: pixelmatch's time in the wasm table is not stable across runs. In the same tinybench process as core-wasm it ran 1.5-1.9x slower on the big differing fixtures than in the repo's separate pixelmatch run (4k/1 332.26 vs 201.60 ms, page/2 513.06 vs 267.84 ms). Across the file's own history it also moved from 287.72 ms (June 2026) to 332.26 ms (July) on 4k/1 and from 317.16 to 152.72 ms on page/1, while pixelmatch itself did not change. Against the JS-run pixelmatch numbers, the 4k/1 lead is about 6.1x, not 10x, and the geometric mean over all 34 rows is about 2.1x (derived from page data).
- The headline '\~51% faster' is the arithmetic mean of per-row '% time saved' (34 rows, 17 of them identical pairs), not a speed ratio. The geometric-mean speedup is about 2.3x, and about 3.0x on differing rows only (derived from page data). The package README also says 'up to \~16x faster than pixelmatch on 4K', but the largest ratio in the published table is 10.0x (4k/1).
- When the result count is 0, the caller's output buffer is left untouched rather than filled with the grayscale image pixelmatch draws. Two paths do this: the cold pass finds no block above threshold, or wasm.rs's copy_output skips because DiffResult.identical is diff_count == 0, which also covers anti-aliasing-only differences. If you reuse an output buffer, check the count before you trust its contents.
- Every call allocates and copies both full RGBA inputs into wasm linear memory, which never shrinks. A 4K-class pair needs about 143 MB of wasm heap, so memory-capped edge runtimes may run out on very large screenshots.

## Known shortcomings

- Pixelmatch runs 1.5-1.9x slower in the wasm run than in the JavaScript run on large diff images, so the 4k/1 10x is about 6.1x against the JavaScript-run figure (derived from page data); rustc version unstated, wasm-opt optional; same-run tinybench harness on an M1 Max.
- Harness flaw: the pixelmatch baseline is unstable across runs. In the same-process wasm run it is 1.5-1.9x slower than in the repo's separate JS run (4k/1 332.26 vs 201.60 ms, page/2 513.06 vs 267.84), and the file's own history swings (4k/1 287.72 in June vs 332.26 in July, page/1 317.16 vs 152.72) while pixelmatch itself did not change, so the 10x headline is about 6.1x against the JS-run pixelmatch. The '\~51%' is the mean of per-row % saved; the geomean speedup is 2.3x; the README's 'up to \~16x' exceeds the table's maximum 10.0x. The plain-JS @blazediff/core is 4-7x faster than the wasm build on identical pairs (the wasm path copies about 143 MB of input per call). The output buffer is left unwritten when the count is 0; the numbers include the July 2026 PR #91 alpha-parity fix.

## Caveats and trade-offs

First-party benchmark, measured in Node.js 22 on an Apple M1 Max, not in a browser. In the wasm run pixelmatch is 1.5-1.9x slower on the large differing fixtures than in the same page's JS run (4k/1 332.26 ms vs 201.60 ms, 4k/3 423.14 vs 253.77, page/2 513.06 vs 267.84) while small and identical rows agree, so the headline 4k/1 ratio of about 10x is about 6.1x against the JS-run pixelmatch time (derived from page data). Whether wasm-opt ran on the measured module is not recorded, and the rustc version is not stated. Results differ slightly from pixelmatch (counts within \~0.05%, e.g. 4k/1 69,932 vs 69,912 pixels). Byte-identical pairs used to be a 60-70% loss; pixel-by-pixel.md says skipping a scalar memcmp shortcut on wasm32 turned them into small wins (4k/2 identical 22.70 ms vs 22.17 ms). On identical pairs the plain JS @blazediff/core (2.50 ms for 4k/1) is far faster than the wasm build (17.47 ms). [retier] First-party benchmark measured in Node.js 22 on an Apple M1 Max, not in a browser; whether wasm-opt ran on the measured module is not recorded and the rustc version is not stated. Harness flaw: pixelmatch's time in the wasm table is not stable. In the same tinybench process as core-wasm it ran 1.5-1.9x slower on the big differing fixtures than in the repo's separate pixelmatch run (4k/1 332.26 vs 201.60 ms, 4k/3 423.14 vs 253.77, page/2 513.06 vs 267.84) while small and identical rows agree, and across the file's own history it moved from 287.72 ms (June 2026) to 332.26 ms (July) on 4k/1 and from 317.16 to 152.72 ms on page/1 while pixelmatch itself did not change. The '\~51%' headline is a mean of percentages, not a speed ratio. The project's own plain-JS @blazediff/core is 4-7x faster than the wasm build on identical pairs because every wasm call allocates and copies both full RGBA inputs into linear memory (about 143 MB for a 4K-class pair) that never shrinks. Results differ slightly from pixelmatch (counts within about 0.05%); the numbers include the July 2026 PR #91 alpha-parity fix. When the result count is 0 the caller's output buffer is left untouched rather than filled with the grayscale image pixelmatch draws.

Needs WebAssembly SIMD (v128). Classifies pixels with the same YIQ delta as pixelmatch but not bit-identically: counts differ by up to \~0.05% (e.g. 22,869 vs 22,883 differing pixels). Part of a larger ecosystem (JS core, native Rust binary, PyPI bindings).

## Maintenance

Active (core-wasm package 6.0.1, last commit 2026-09-21, 352 stars, MIT), a single-maintainer monorepo releasing about every two weeks. The kernel and published numbers changed in July 2026 (PR #91, faster kernel plus an alpha-blend parity fix), so pin a version and re-measure on your own screenshots, ideally in your target browser.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** benchmarks/pixel-by-pixel.md's WebAssembly table compares @blazediff/core-wasm with pixelmatch in the same tinybench run (apps/image-benchmark/src/pixel-by-pixel/blazediff-core-wasm-benchmark.ts, both called without an output buffer at default threshold 0.1), the build flags are public (crates/blazediff/scripts/build-wasm.sh RUSTFLAGS +simd128,+bulk-memory, crates/Cargo.toml release profile opt-level 3, lto fat, codegen-units 1), and BENCHMARKS.md names the Apple M1 Max and Node.js 22.
- **Retiered** A to C: Enricher: the pixelmatch baseline column in the wasm table is 1.5-1.9x slower on the large differing fixtures than the same pixelmatch in the repo's separate JS run and swings between the file's own revisions while pixelmatch did not change, so the 10x headline is about 6.1x against a stable baseline; the '\~51%' is a mean of per-row percentages (geomean 2.3x) and the project's own plain-JS core is 4-7x faster than the wasm build on identical pairs. Asymmetric and unstable baseline in a first-party harness (TensorFlow DLPerf and LC precedents): A to C.
- **Verifier notes:** Every number in claimed_speedup matches the wasm table of benchmarks/pixel-by-pixel.md (\~50.8% average, 4k/1 332.26 vs 33.18 ms, 4k/3 423.14 vs 44.65, blazediff/1 1.24 vs 0.24, 4k/2 identical 22.70 vs 22.17); the harness is a fair same-process comparison with matching options. Main shortcoming: pixelmatch ran markedly slower in the wasm run than in the JS run on large differing images, inflating the 10x headline (about 6x against the JS-run figure). Metadata checked: MIT, 351 stars, 5 forks, last commit 2026-09-21; the aslang-registry copy is already a recorded duplicate.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-79 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/benchmarks/pixel-by-pixel.md>
  - <https://github.com/teimurjan/blazediff>
  - <https://github.com/teimurjan/blazediff/commits/main>
  - <https://github.com/teimurjan/blazediff/tree/main/benchmarks>
  - <https://github.com/teimurjan/blazediff/tree/main/apps>
  - <https://github.com/teimurjan/blazediff/tree/main/packages/core-wasm>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/blazediff/scripts/build-wasm.sh>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/Cargo.toml>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/package.json>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/apps/image-benchmark/package.json>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/apps/image-benchmark/src/pixel-by-pixel/blazediff-core-wasm-benchmark.ts>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/apps/image-benchmark/src/pixel-by-pixel/external-pixelmatch-benchmark.ts>
- **Sources the enricher read:**
  - <https://github.com/teimurjan/blazediff>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/README.md>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/benchmarks/pixel-by-pixel.md>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/17fadb6/benchmarks/pixel-by-pixel.md>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/a3a6f64/benchmarks/pixel-by-pixel.md>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/7a377ed/benchmarks/pixel-by-pixel.md>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/5eb8819/benchmarks/pixel-by-pixel.md>
  - <https://github.com/teimurjan/blazediff/commits/main/benchmarks/pixel-by-pixel.md>
  - <https://github.com/teimurjan/blazediff/commits/main/packages/core-wasm>
  - <https://github.com/teimurjan/blazediff/pull/91>
  - <https://github.com/teimurjan/blazediff/issues?q=is%3Aissue>
  - <https://github.com/teimurjan/blazediff/issues/38>
  - <https://github.com/teimurjan/blazediff/issues/76>
  - <https://github.com/teimurjan/blazediff/tree/main/apps/image-benchmark/src/pixel-by-pixel>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/packages/core-wasm/README.md>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/packages/core-wasm/package.json>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/packages/core-wasm/src/index.ts>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/blazediff/src/wasm.rs>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/blazediff/src/diff.rs>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/blazediff/src/lib.rs>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/blazediff/src/types.rs>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/blazediff-shared/src/lib.rs>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/blazediff/Cargo.toml>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/Cargo.toml>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/crates/blazediff/scripts/build-wasm.sh>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/apps/image-benchmark/package.json>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/apps/image-benchmark/tsup.config.ts>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/apps/image-benchmark/src/utils.ts>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/apps/image-benchmark/src/pixel-by-pixel/blazediff-core-wasm-benchmark.ts>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/apps/image-benchmark/src/pixel-by-pixel/external-pixelmatch-benchmark.ts>
  - <https://raw.githubusercontent.com/teimurjan/blazediff/HEAD/apps/image-benchmark/src/pixel-by-pixel/blazediff-core-benchmark.ts>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/teimurjan/blazediff`) · [data/wave13/enrich/raw/github_com_teimurjan_blazediff.json](../../../data/wave13/enrich/raw/github_com_teimurjan_blazediff.json) (enrichment confidence 0.8)

</details>
