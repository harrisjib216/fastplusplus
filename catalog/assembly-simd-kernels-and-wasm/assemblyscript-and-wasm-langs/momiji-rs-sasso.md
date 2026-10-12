# sasso

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (native, N-API and WebAssembly engines)` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust SCSS/Sass compiler matching dart-sass 1.104.1 output; ships native CLI, crate, C ABI and npm (wasm plus N-API) builds.

| | |
|---|---|
| **Beats** | dart-sass 1.104.1 (the 138-stylesheet table does not name the dart-sass form; bench/three_way.md compares the dart2js JS CLI that npx sass runs, the native-VM CLI, sass-embedded and the sass JS library in-process, at dart-sass 1.100.0/1.101.0) |
| **Claimed result** | 138 stylesheets in one process, best of five (2026-09-17, macOS arm64, 12-core M2 Max per issue #83): sasso 0.15.0 binary 137 ms, npx sasso native engine 266 ms, wasm engine 610 ms, dart-sass 1.104.1 2268 ms; these sasso rows compile on 12 threads while npm sass compiles files sequentially, so like-for-like single-threaded numbers are the binary at -j 1 681 vs 2322 ms (3.4x, issue #83), the npm native engine at -j 1 0.86 s vs 2268 ms (2.6x), and the sequential wasm engine before 0.15.0 2340 ms, parity with dart-sass (derived from page data). Pure compile of the large file: sasso 7.4 ms (warm 200-iteration loop; 10.4 ms after a regression found by the 2026-09-15 audit) vs dart2js 105.4 ms warm (bench/dart_vs_grass.md) and 97.1 ms (three_way.md), about 9-14x; the README's \~29x divides the warm sasso loop by a cold dart-sass compile minus startup (\~216 ms). Linux x86_64 one-entry-point run (2026-10-02): binary 4.3 ms, npm path 38.3 ms vs dart-sass 20.7 ms (npm path slower). |
| **Workload** | Compile a 138-stylesheet tree (lila's own flags), best of five, measured against the published npm package. |
| **Metric** | latency |
| **Hardware** | arm64 macOS 26.3.0, 12 cores (bench/three_way.md); 138-stylesheet table on macOS arm64 (2026-09-17); one Linux x86_64 run dated 2026-10-02; CPU model not stated |
| **Compiler and flags** | Rust release build with LTO (exact Cargo profile not checked); wasm size build opt-level z + LTO + panic=abort + strip + wasm-opt -Oz, speed build opt-level 3 + wasm-opt -O3; wasm timings in Node 22; bench/scripts/run_bench.sh (hyperfine, RUNS=12 WARMUP=3 LOOP_N=200) times native sasso, grass 0.13.4, the dart-sass JS bin and npx sass only, not the wasm engine |
| **Adoption** | 7 stars, 2 forks, 1,557 commits; crates.io 2,054 downloads (1,433 recent); npm monthly downloads not checked (npm API blocked here) |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/momiji-rs/sasso) · [benchmark](https://github.com/momiji-rs/sasso) |

## Verdict

On an arm64 macOS 12-core machine (M2 Max per issue #83), the native binary compiled a generated \~26k-line stylesheet in 11.7 ms cold against 354 ms for the dart-sass 1.101.0 JS CLI and 26.5 ms for grass 0.13.4 (hyperfine); warm per-compile cost in the older full three_way.md run is 9.8-10.4 ms against 97.1 ms for the dart2js sass library in-process (about 9.3x), 63.8 ms for the sass-embedded native-VM daemon (about 6x) and 21.9 ms for grass (the README's later 7.4 ms is from a different run). On 21 real-world projects (sasso 0.7.0 vs dart-sass 1.101.0 JS CLI) end-to-end speedups were 3.5-42x, about 2.5-5.5x on the largest trees once dart-sass's 137 ms start-up is removed (derived from page data); the 138-file Lichess table (137 ms vs 2268 ms) compares a 12-thread sasso with a dart-sass form the README does not name.

## Use it when

- CI or build scripts that shell out to `sass` once per file, where dart-sass's 140-500 ms start-up per invocation dominates
- Embedding a Sass compiler in a Rust, Go (wazero, no cgo), Ruby, Python or PHP process without a Node or Dart toolchain
- Browser or edge use where shipping the dart-sass compiler as JavaScript is too heavy (size wasm build about 356 KB gzip)
- Large multi-entry trees (Lichess-style, 100+ entry points) on a multi-core machine, where its parallel CLI beats the sequential npm `sass` CLI
- Projects that want current dart-sass semantics (CSS Color 4, modern serialization) that grass, pinned to dart-sass 1.54.3, does not give

## Skip it when

- Single-entry builds through the npm CLI: one Linux entry point took 38.3 ms via node_modules/.bin/sasso against 20.7 ms for dart-sass (issue #272); use the binary (4.3 ms) instead
- Stylesheets relying on dart-sass 1.105 features (first-class modules, meta.load / meta.get-module, issue #281) or on --pkg-importer and deprecation-selection flags, which the binary does not support
- Pipelines that need dart-sass's exact error behaviour everywhere: 62 open issues, many parity bugs (e.g. #297 and #253 compile input dart rejects, #282 @extend across media queries)
- Memory-constrained parallel builds: the arena keeps each thread's high-water mark, 478 MB peak for the binary at -j 12 on Lichess and about 1.35 GB for a --watch pool
- Teams that need a mature, widely deployed compiler: v0.x, 7 GitHub stars, about 2,000 crates.io downloads

## How it is fast

Native code with no VM or Node start-up (1.8 ms process floor against 139 ms for the dart-sass JS bin). The binary installs a scoped bump-arena global allocator (ScopedAlloc) that turns each compile's allocations into pointer bumps freed at the end, and composite values are reference-counted so passing a list or map is an O(1) refcount bump; later rounds cut allocations on the large corpus from 377,761 to 155,656. Multi-file builds compile in parallel, one worker per core by default.

## Compared with alternatives

No sibling compiles Sass; the nearest catalogued pattern is a JS tool rewritten in a compiled language and shipped as wasm (svgo.mbt for SVG optimisation, calaminejs for spreadsheet reading). Pick sasso when the job is SCSS compilation and you can run its native binary or addon; its wasm build alone is roughly 1.5-3.5x slower than native.

## Integration

| | |
|---|---|
| **Form** | crate + CLI binary (cargo-dist, Homebrew, Nix) + npm package (wasm build plus optional N-API addon) + C ABI static/shared lib |
| **Dependencies** | none at runtime; chrono only on Windows for the CLI's --watch timestamp (optional cli-clock feature) |
| **Minimum toolchain** | Rust 1.74 (declared rust-version); Node version for the npm package not documented beyond the Node 22 used for wasm timings |
| **Platforms** | any std target incl. wasm32-unknown-unknown and wasm32-wasip1; prebuilt binaries for Linux gnu/musl, macOS and Windows on x86_64/aarch64; native npm addon only on macOS and Linux (wasm fallback elsewhere) |
| **Thread safety** | compile runs in a per-thread arena scope; tests/arena_threads.rs runs 8 threads x 200 concurrent compiles with byte-identical results. Send/Sync bounds of Options and Importer not checked. |
| **Drop-in for the baseline** | partial — the CLI takes dart-sass's flags and the npm package mirrors the modern JS API (sass-loader, Vite alias), but legacy-API callers, --pkg-importer, deprecation-selection flags and dart-sass 1.105 first-class modules are not covered |

## Gotchas

- Harness flaw in the headline 138-stylesheet table: sasso compiles in parallel (12 threads on the 12-core M2 Max named in issue #83) while the dart-sass row does not name its form; the npm `sass` CLI compiles multiple files sequentially (dart-sass lib/src/executable/concurrent/js.dart aliases the concurrent call to the plain one; only the Dart VM build uses isolates). Single-threaded, the binary at -j 1 took 681 ms against 2322 ms (3.4x, issue #83), the npm native engine at -j 1 0.86 s against 2268 ms (2.6x, 0.16.0 changelog), and the sequential wasm CLI before 0.15.0 took 2340 ms, at parity with dart-sass; the record's \~3.7x wasm figure comes from the worker pool.
- The arena speed-up is only active when ScopedAlloc is the #[global_allocator]: the CLI installs it, a Rust embedder must do so itself (the N-API addon was 14-26% slower until 0.16.0 for this reason), and the wasm builds run without it.
- Harness flaw in the README's 'pure compile' row: sasso's 7.4 ms is a warm 200-iteration in-process loop, while dart-sass's \~216 ms is derived as cold single-file minus start-up, i.e. one compile on an unwarmed V8 JIT. The repo's own warm measurements of dart2js put it at 105.4 ms per compile (K=20 copies in one invocation, bench/dart_vs_grass.md) and 97.1 ms (sass JS library in-process, three_way.md), so the warm pure-compute gap is about 9-14x (9.3x within the single three_way.md run, 97.1 vs 10.4 ms), not \~29x (derived from page data). run_bench.sh also differs per engine in small ways: sasso uses --no-css while dart-sass writes to /dev/null, grass writes no files in the batch row, and grass --loop re-reads the file each iteration while sasso reads it once.
- Published numbers are stale relative to the code: bench/README.md says the 7.4 ms/compile in three_way.md is from master dc5099b and the 2026-09-15 audit found a 7.4 to 10.4 ms regression; the dart-sass baseline in three_way.md and real_world.md is 1.100.0/1.101.0 and parity there was checked after whitespace and colour canonicalization, not byte-for-byte.

## Known shortcomings

- No CPU model; the Wasm timings sit outside run_bench.sh and the Wasm vs dart-sass comparison in the README is cross-run (only the 138-file table is same-run, 610 vs 2268 ms); the npm path is slower than dart-sass on a single entry (38.3 vs 20.7 ms); a Rust SCSS compiler, loose fit for the AssemblyScript category.
- Harness flaw 1: the 138-stylesheet table runs sasso on 12 threads (12-core M2 Max, issue #83) while npm sass compiles files one at a time, so the \~3.7x wasm figure comes from parallelism; single-threaded, the binary at -j 1 took 681 vs 2322 ms (3.4x), the npm native engine at -j 1 0.86 s vs 2268 ms (2.6x), and the sequential wasm engine before 0.15.0 took 2340 ms, the same as dart-sass. Harness flaw 2: the README 'pure compile \~29x' compares sasso's warm 200-iteration loop with dart-sass's cold single compile minus startup (\~216 ms); the repo's own warm dart2js numbers are 105.4 and 97.1 ms, so the warm gap is about 9-14x. The 7.4 ms figure is stale (the audit found a regression to 10.4 ms); library embedders only get the arena speed if they install ScopedAlloc as the global allocator.

## Caveats and trade-offs

First-party numbers; CPU model not stated. The headline 19-30x is for the native binary against the dart2js JS CLI, not WebAssembly; the wasm figure in a same-run table is 610 ms vs 2268 ms. The README's wasm-vs-dart comparison is cross-run (wasm refreshed 2026-06-13, dart-sass forms from an earlier full run at 1.100.0), and run_bench.sh does not time the wasm build at all. bench/three_way.md predates the allocation-reduction rounds by the README's own note. In the one-entry-point Linux x86_64 run (2026-10-02) the npm path is slower than dart-sass: 38.3 ms through node_modules/.bin/sasso vs 20.7 ms for dart-sass (the binary takes 4.3 ms). Category fit is loose: a Rust SCSS compiler that ships a wasm build, not a wasm-targeting language. Not a brand-new repo: crates.io crate created 2026-06-06, 1,557 commits; 7 stars. [retier] First-party numbers; the headline 19-30x is for the native binary against the dart2js JS CLI, not WebAssembly. Harness flaw 1: the 138-stylesheet table runs sasso in parallel (12 threads) while the npm sass CLI compiles files one at a time (dart-sass lib/src/executable/concurrent/js.dart aliases the concurrent call to the plain one; only the Dart VM build uses isolates), so the wasm engine's \~3.7x comes from parallelism and the sequential wasm engine is at parity with dart-sass. Harness flaw 2: the README 'pure compile' row compares a warm 200-iteration in-process loop with a cold single dart-sass compile minus start-up; the repo's own warm dart2js measurements put the gap at about 9-14x. The wasm-vs-dart comparison in the README is cross-run and run_bench.sh does not time the wasm build. The arena speed-up is only active when ScopedAlloc is the global allocator: the CLI installs it, a Rust embedder must do so itself (the N-API addon was 14-26% slower until 0.16.0), and the wasm builds run without it. Published numbers are stale relative to the code (7.4 to 10.4 ms regression); parity with dart-sass was checked after whitespace and colour canonicalization, not byte-for-byte. Category fit is loose (a Rust SCSS compiler that also ships a wasm build).

Sync APIs need synchronous importers; async APIs use an asyncify module. Drop-in for the sass modern API with 62 open issues; not every dart-sass feature may be covered.

## Maintenance

Very active (0.21.0 on 2026-10-03, commits to 2026-10-07, about 1,557 commits since June 2026) and MIT OR Apache-2.0, but v0.x with 62 open issues and a tiny user base; the native binary is the form whose speed claims hold up.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers in the README and bench/three_way.md; the hyperfine harness bench/scripts/run_bench.sh is public but covers only native sasso, grass, the dart-sass JS bin and npx sass (no wasm engine), and the machine is given only as 'arm64 macOS, 12 cores' with no CPU model, so not A.
- **Verifier notes:** Numbers in the record match the README. Confirm at C; shortcomings: no CPU model, wasm timings outside the public harness and cross-run against dart-sass, npm CLI slower than dart-sass on a single entry point, loose fit for assemblyscript-and-wasm-langs (orchestrator may want a category override).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/momiji-rs/sasso>
  - <https://github.com/momiji-rs/sasso/commits>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/README.md>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/three_way.md>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/scripts/run_bench.sh>
  - <https://crates.io/api/v1/crates/sasso>
- **Sources the enricher read:**
  - <https://github.com/momiji-rs/sasso>
  - <https://github.com/momiji-rs/sasso/commits/master>
  - <https://github.com/momiji-rs/sasso/issues>
  - <https://github.com/momiji-rs/sasso/issues/83>
  - <https://github.com/momiji-rs/sasso/tree/master/bench>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/README.md>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/three_way.md>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/scripts/run_bench.sh>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/grass_runner/src/main.rs>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/grass_runner/Cargo.toml>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/perf_audit_2026-09-15.md>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/dart_vs_grass.md>
  - <https://raw.githubusercontent.com/momiji-rs/sasso/HEAD/bench/real-world/real_world.md>
  - <https://raw.githubusercontent.com/sass/dart-sass/main/lib/src/executable/concurrent.dart>
  - <https://raw.githubusercontent.com/sass/dart-sass/main/lib/src/executable/concurrent/js.dart>
  - <https://raw.githubusercontent.com/sass/dart-sass/main/lib/src/executable/concurrent/vm.dart>
  - <https://crates.io/api/v1/crates/sasso>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/momiji-rs/sasso`) · [data/wave13/enrich/raw/github_com_momiji_rs_sasso.json](../../../data/wave13/enrich/raw/github_com_momiji_rs_sasso.json) (enrichment confidence 0.62)

</details>
