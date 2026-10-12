# Zipp (Rust JavaScript and Python VM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust JavaScript engine (plus experimental Python frontend) whose interpreter ran about 1.6x faster than QuickJS-NG on its own suite.

| | |
|---|---|
| **Beats** | QuickJS-NG v0.16.2 (maintained QuickJS fork) for the interpreter; Node.js, Bun and Deno for the JIT builds |
| **Claimed result** | Interpreter (ZIPP_NOJIT=1) vs QuickJS-NG v0.16.2 on real13: v0.0.5 startup-adjusted geomean 0.6413x of QuickJS-NG's time (cold 0.6439x; 12 of 13 point wins; about 1.56x faster, derived from page data); v0.0.6 at e3acee352074 cold 0.6090x and startup-adjusted 0.6058x (13 of 13 wins; about 1.64x faster, derived from page data). micro5 vs QuickJS-NG: 0.8556x startup-adjusted (5 of 5). With JITs on, vs Node v24.12.0 / Bun 1.3.14 / Deno 2.6.10 (canonical PGO capture at 8229b3fc): 0.728x / 0.594x / 0.460x across all 30 rows; 0.614x / 0.531x / 0.521x on the 13 normal rows; 0.878x / 0.752x / 0.765x on the retained ten without the three architecture diagnostics; hostile 17 0.829x Node. Median launch 7.4 ms vs Node 30.4 ms, Bun 43.3 ms, Deno 82.6 ms. |
| **Workload** | Frozen 'real13' set of 13 JavaScript programs and a 5-program micro set run as fresh processes (six counterbalanced repetitions, 10,000-sample bootstrap, exact-output checks) against pinned QuickJS-NG and Boa builds on one Windows x86-64 host; separate canonical captures against Node, Bun and Deno. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X3D, Windows 11 (bench/comparison/README.md); the raw canonical JSON reports platform 'Windows-10-10.0.26200-SP0', processor 'AMD64 Family 26 Model 68 Stepping 0, AuthenticAMD' |
| **Compiler and flags** | Zipp: Rust/Cargo 1.92.0, repository release profile (opt-level 3, fat LTO, codegen-units 1, aborting panics), default features, no extra RUSTFLAGS and no PGO for the QuickJS-NG and Boa runs; the Node/Bun/Deno capture used a Windows PGO build via tools/pgo.sh. QuickJS-NG: official v0.16.2 release binary qjs-windows-x86_64.exe (SHA-256 7b27412de844403545bd151fbe49191b4d5b91a9e15b5db7c863fea54639a82b), built by upstream CI under MSYS2 UCRT64 in CMake Release mode with static mimalloc; exact compiler package revision not stamped. |
| **Adoption** | 6 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/f2i-com/zipp.org) · [benchmark](https://github.com/f2i-com/zipp.org/blob/main/bench/comparison/README.md) |

## Verdict

On one AMD Ryzen 9 9950X3D under Windows 11, Zipp's release-default build run as an interpreter (ZIPP_NOJIT=1; Rust 1.92.0, opt-level 3, fat LTO, no PGO) took 0.6413x (v0.0.5, 12 of 13 rows) and 0.6058x (v0.0.6, 13 of 13) of the official QuickJS-NG v0.16.2 Windows binary's startup-adjusted time on the project's 13-program suite, using six counterbalanced fresh-process repetitions and stdout checked against Node. The JIT ratios against Node v24.12.0, Bun 1.3.14 and Deno 2.6.10 (0.878x Node on the retained ten) come from a PGO build at 8229b3fc, before the B280 call-order fix; the later 14770703 capture measured 1.0025x Node on those ten.

## Use it when

- A Rust host that needs a modern, near-complete ES2025 engine and wants more interpreter throughput than QuickJS-NG on x86-64 (0.606x of QuickJS-NG's time on 13 programs at v0.0.6, interpreter only).
- Short-lived CLI scripts where process launch dominates: 7.4 ms median empty launch versus 30.4 ms Node, 43.3 ms Bun and 82.6 ms Deno in the canonical capture.
- Trusted, loop- or typed-array-heavy code on x86-64 Windows or Linux with the JIT on (typedarray-math 144 ms vs Node 200 ms, map-set-heavy 672 ms vs 784 ms).
- Running untrusted scripts under instruction, heap, output and wall-time budgets via the separately built interpreter-only zipp-sandbox, when speed matters less than containment.
- Experiments that need Python and JavaScript in one VM instance (opt-in python-js-interop feature).

## Skip it when

- C or C++ hosts: there is no C API, and zipp-vm is not published on crates.io (crates.io returns 'crate zipp-vm does not exist'), so embedding means a git dependency plus your own FFI layer.
- Browser/WASM deployments chosen for speed or size: the v0.0.5 WASM module took 2.107x QuickJS-NG's adjusted time, is 3.6x larger raw (5.48 MB vs 1.53 MB), and in the v0.0.6 exact-suite attempt validated only 7 of 28 script rows within its production instruction and heap limits.
- Promise-, JSON- or allocation-heavy application code: async-promise-chain 1.12x and json-large 1.01x Node in the canonical capture; allocation survival 1.772x, warm router 1.674x and React-style reconcile 1.646x Node in the hostile suite.
- Anything needing a mature, widely deployed engine: 6 stars, effectively one author, 0.0.x releases every few days, a forced-JIT segfault fixed on 2026-09-02 and a method-call ordering bug fixed in v0.0.15 (B280); ARM64 only has a small integer baseline JIT.
- Memory- or footprint-constrained embedding: the v0.0.5 and v0.0.6 Windows release CLIs were about 7.9 MB versus 2.1 MB for the qjs binary, and the default parser bounds assume a 256 MiB interpreter thread stack.

## How it is fast

Values are NaN-boxed in 64 bits and the interpreter uses explicit register frames, with per-call-site inline caches guarded on receiver identity or exact shape plus version counters, and a non-moving generational nursery GC. On x86-64 a dynasm JIT offers hot loops (OSR) and functions to progressively broader tiers (SROA, unboxed INT/INT-GPR, DOUBLE register homes, boxed MEM with guarded ICs) with precise side exits to the interpreter, plus fused native map/filter kernels for callbacks. Release builds use fat LTO, one codegen unit, panic=abort and mimalloc; the Node/Bun/Deno capture also used PGO.

## Compared with alternatives

Pick Zipp over QuickJS, gkurt/quickjs or PrimJS only when the host is Rust on x86-64 and you want a faster native interpreter (or a JIT) with near-complete ES2025; for a C/C++ host, a small binary or WASM, QuickJS-NG or Escargot remain the safer choices, and V8 or SpiderMonkey if you need a mature JIT.

## Integration

| | |
|---|---|
| **Form** | crate (git/path dependency on crates/zipp-vm; not on crates.io) plus prebuilt CLI and wasm-bindgen package |
| **Dependencies** | dynasm/dynasmrt (JIT feature), project fork of regress (zipp-regress), num-bigint, num-traits, unicode-id-start, unicode-normalization, rustc-hash, self_cell; the CLI adds mimalloc; optional zipp-pyparse and wgpu-based zipp-gpu for Python |
| **Minimum toolchain** | Stable Rust, edition 2021 (no rust-version declared); benchmarks built with Rust/Cargo 1.92.0 |
| **Platforms** | x86-64 Windows and Linux (mature JIT; release binaries for both); ARM64 Linux/Windows/macOS with a smaller integer baseline JIT; wasm32 and other targets interpreter-only |
| **Thread safety** | Not documented for the native API; one ScriptState is one VM, and the security guide asks for one Worker/WASM instance per untrusted tenant |
| **Drop-in for the baseline** | no |

## Gotchas

- The 13-program real13 suite and the hostile suite are written by the project as acceptance tests for its own optimizations (property-ic-shapes.js says it is the acceptance benchmark for milestone M3), and the QuickJS-NG geomean includes the three 'architecture diagnostic' rows; per-row QuickJS-NG timings stay in gitignored target/comparison/results.
- Harness flaw in the JIT headline: in the canonical JSON, property-ic-shapes takes 9.6 ms cold against a 7.5 ms empty launch, about 2 ms for roughly 140 million property reads and writes (5 phases x 7 receiver counts x 4,000,000), about 0.015 ns each, so the JIT must collapse or elide the loops; its 0.04x Node row measures loop elimination, not inline-cache speed, and the three diagnostics pull the all-13 ratio from 0.878x to 0.614x Node.
- array_ops.rs recognizes the exact compiler output of three arrow callbacks 'used by the cross-engine WASM workload' (map x\*2, filter mod 3, reduce add) in every build that is not x86-64 with the JIT (WASM and ARM64 included); the 0.095x QuickJS-NG WASM kernel result became 1.815x with those lanes off.
- ZIPP_RELAXED_CALL_ORDER=1 restores the faster pre-B280 method-call lowering, which the docs call observably wrong for getters and proxy traps; enabling the `instrument` feature (execution budgets) turns the JIT off for that VM.

## Known shortcomings

- Tier A rests on the QuickJS-NG interpreter comparison (bench/comparison/run_native.py plus bench/real, Rust 1.92.0 opt-level 3 with fat LTO and one codegen unit, SHA-pinned QuickJS-NG v0.16.2 binary, Ryzen 9 9950X3D, Windows 11); the MSYS2 GCC revision is unstamped. The Node, Bun and Deno numbers predate the later-fixed B280 call-order bug and a later capture is slower (1.0025x Node; retained-ten 0.878x Node), so the JIT-engine comparison is C-grade only. QuickJS-NG raw JSON is gitignored, only 6 repetitions, Zipp v0.0.5/v0.0.6. The Wasm build is 2.107x slower than QuickJS-NG and its kernel win comes from exact-shape lanes that the native x86-64 build excludes.
- Enricher: the property-ic-shapes row is 9.6 ms cold against a 7.5 ms empty launch, about 2 ms for roughly 140M property accesses (0.015 ns each), so the JIT collapses the loops and the 0.04x-of-Node row measures loop elimination, not inline caches; the three self-written diagnostic rows pull the 13-row geomean from 0.878x to 0.614x of Node, and the QuickJS-NG geomean includes them too with per-row raw data not committed. array_ops.rs pattern-matches three exact Wasm-workload callbacks in every non-x86-64-JIT build (Wasm, ARM64), so only the native x86-64 numbers are free of benchmark-specific fast paths. zipp-vm is not on crates.io, has no C API and needs a 256 MiB stack. run_native.py itself is clean (Node output checked every run, fresh processes, no PGO).

## Caveats and trade-offs

First-party, self-labelled diagnostic captures (diagnostic_only:true) with only six repetitions for the QuickJS-NG runs. The QuickJS-NG raw result JSONs sit in gitignored target/comparison/results by policy; only summaries and hashes are committed. The QuickJS-NG ratios are for v0.0.5 and v0.0.6 and were not rerun on current main (0.0.21). The Node/Bun/Deno canonical capture at 8229b3fc predates B280 (v0.0.15), which fixed method-call ordering that was 'observably wrong for a getter or proxy trap'. The later 14770703 capture is slower (headline ten 1.0025x Node, all 13 0.677x), and no headline is claimed for it. The 13-normal geomean (0.614x Node) leans on three architecture diagnostics (property-ic-shapes 0.04x, polymorphic-objects-v2 0.30x, sparse-array-v2 0.59x); the retained ten give 0.878x. 'Faster than Node on every row' is not met (21 of 30). The canonical raw JSON reports zipp 0.0.12 while the README says 0.0.13. The WASM build is slower than QuickJS-NG: v0.0.5 adjusted 2.107x, and v0.0.6 compared only 5 of 30 rows (0.96x). The five-kernel WASM speed-up (0.095x QuickJS-NG) was dominated by exact bytecode-shape lanes (1.815x with them off). Those lanes (vm/array_ops.rs) compile only when not (jit and x86_64), so the native x86-64 captures exclude them. The project is a rapid, largely machine-assisted rewrite with 6 stars; Rust, not C++. [retier] Native x86-64 comparison against QuickJS-NG v0.16.2 is public and pinned (Rust 1.92.0, fat LTO, Ryzen 9 9950X3D, Windows 11; MSYS2 GCC revision unstamped). The Node, Bun and Deno rows predate the later-fixed B280 call-order bug and a later capture is slower (retained-ten 0.878x of Node; the 13-row geomean drops to 0.614x once three self-written diagnostic rows are included, and the property-ic-shapes row measures loop elimination rather than inline caches). array_ops.rs pattern-matches three Wasm-workload callbacks in the Wasm and ARM64 builds, so only the native x86-64 numbers are free of benchmark-specific fast paths; the Wasm build is 2.107x slower than QuickJS-NG. Six repetitions, per-row QuickJS-NG raw data gitignored, no C API, 256 MiB stack.

Embeds as a Rust library or runs in the browser as WebAssembly; the browser WASM module was 2.1x slower than QuickJS-NG and 3.6x larger (5.56 MB vs 1.53 MB raw) in the README's own historical capture. Not a drop-in C API. Python frontend is experimental and a GPU lab is bundled, so the crate is large.

## Maintenance

Very active (last commit 2026-09-29, release 0.0.21, about 2,100 commits, 0 open issues) and Apache-2.0, but a 6-star, effectively single-author 0.0.x project. It is usable from Rust only as a git dependency, and its published comparisons describe v0.0.5/v0.0.6 and pre-B280 builds, not current main.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A for the QuickJS-NG headline. bench/comparison/README.md gives the public harness (bench/comparison/run_native.py over the bench/real 13-case corpus) and Zipp's compiler and flags (Rust/Cargo 1.92.0, release profile: opt-level 3, fat LTO, one codegen unit, no RUSTFLAGS, no PGO). The baseline is the official QuickJS-NG v0.16.2 qjs-windows-x86_64.exe, pinned by SHA-256 and built by upstream CI under MSYS2 UCRT64 in CMake Release mode (exact GCC revision unstamped), and the host is named as AMD Ryzen 9 9950X3D on Windows 11. The Node/Bun/Deno numbers alone would be C: they were measured at 8229b3fc, before B280 fixed call ordering that was 'observably wrong for a getter or proxy trap', and the later capture is slower.
- **Verifier notes:** Confirmed and upgraded C to A on the QuickJS-NG interpreter comparison: public harness and corpus, Rust 1.92.0 flags, a hash-pinned official baseline binary, and a named CPU. The only gap is the unstamped MSYS2 GCC revision of the official QuickJS-NG build; cap at C if that counts as a missing compiler. Shortcomings to record: the Node/Bun/Deno numbers come from pre-B280 code that had a later-fixed call-order correctness bug (C-grade on their own) and regressed afterwards; the QuickJS-NG raw JSONs are not committed; the results are historical (v0.0.5 and v0.0.6, six reps); the WASM build is slower than QuickJS-NG; and the WASM kernel claim depended on exact-shape lanes, which the native build excludes.
- **Fields the verifier corrected:** `benchmark_url`, `hardware`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** stamped GCC revision and post-B280 Node comparison; re-run without the self-written diagnostic rows
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/README.md>
  - <https://github.com/f2i-com/zipp.org>
  - <https://github.com/f2i-com/zipp.org/commits>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/bench/comparison/README.md>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/bench/comparison/run_native.py>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/bench/real13_8229b3fc_pgo_2026-09-02.json>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/PERF_ROADMAP.md>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/crates/zipp-vm/src/vm/array_ops.rs>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/LICENSE-APACHE>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/tools/pgo.sh>
- **Sources the enricher read:**
  - <https://github.com/f2i-com/zipp.org>
  - <https://github.com/f2i-com/zipp.org/commits/main>
  - <https://github.com/f2i-com/zipp.org/issues>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/README.md>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/DOC.md>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/PERF_ROADMAP.md>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/bench/comparison/README.md>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/bench/comparison/run_native.py>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/bench/real/property-ic-shapes.js>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/bench/real13_8229b3fc_pgo_2026-09-02.json>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/crates/zipp-vm/src/vm/array_ops.rs>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/crates/zipp-vm/Cargo.toml>
  - <https://raw.githubusercontent.com/f2i-com/zipp.org/HEAD/crates/zipp-cli/Cargo.toml>
  - <https://crates.io/api/v1/crates/zipp-vm>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/f2i-com/zipp.org`) · [data/wave12/enrich/raw/github_com_f2i_com_zipp_org.json](../../../data/wave12/enrich/raw/github_com_f2i_com_zipp_org.json) (enrichment confidence 0.6)

</details>
