# quickjs-jit (Longbridge JIT-enabled QuickJS-NG distribution)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust (with the vendored QuickJS-NG C engine)` · `MIT` · 🟢 active

> Tiered Cranelift JIT bolted onto a patched QuickJS-NG via rquickjs; 20-50x the interpreter on scalar kernels, still slower than Bun everywhere.

| | |
|---|---|
| **Beats** | QuickJS-NG interpreter (same runtime with the JIT detached); Bun 1.4.0 (JavaScriptCore) also measured as the external target |
| **Claimed result** | Current README matrix (35 scenarios, Linux x86_64, measured 2026-09-30, revision 8fa2a48 = v0.12.11; QuickJS = the same binary with the JIT detached, QuickJS-NG fd0a0210): versus QuickJS 23 scenarios faster, 7 tied, 5 slower; e.g. scalar-control-flow 49.2x faster (2.13 ms vs 0.0434 ms per ten calls), scalar-expressions 47.4x, fibonacci-iterative 45.8x, quickjs-bitops 42.6x, fibonacci-recursive 27.1x (9.91 ms vs 0.361 ms), float64-dense 22.2x; slower cases collections 0.98x, strings-json 0.96x, json-codec 0.96x, map-set-bigint 0.99x, exceptions-promises-async 0.98x. Versus Bun 1.4.0 all 35 scenarios are slower (closest fibonacci-recursive 0.73x of Bun speed, widest methods-dynamic 0.012x). |
| **Workload** | 35 JavaScript scenarios (scalar loops, fibonacci, calls, property access, typed arrays, JSON, regexp, collections, exceptions); latency in ms per ten workload calls, median over processes of each process's upper-median of 16 timed batches, paired geometric-mean ratios with 95% confidence intervals. |
| **Metric** | latency |
| **Hardware** | 13th Gen Intel Core i7-13700KF, Linux 7.2.5 x86_64, CPU 8 pinned, powersave governor (the same README also has an Apple M3 matrix, no CPU pinning) |
| **Compiler and flags** | rustc 1.98.1 / LLVM 22.1.8, release build (harness built with 'cargo build --release --manifest-path benchmarks/Cargo.toml --bins'); JIT back end is Cranelift 0.116 (jit/Cargo.toml); QuickJS-NG commit fd0a0210b7be00957751871e7e01b8291268fc29 compiled through the sys crate's build.rs with the cc crate's release defaults (C compiler and version not named); Bun 1.4.0 default flags, launched from a .mjs file |
| **Adoption** | 15 stars, 1 fork (GitHub fork of DelSkayn/rquickjs); published on crates.io as quickjs-jit (latest 0.12.6, 2026-09-03, 110 downloads); the measured 0.12.11 exists only in git |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/longbridge/quickjs-jit) · [benchmark](https://github.com/longbridge/quickjs-jit) |

## Verdict

On an Intel Core i7-13700KF (Linux, CPU 8 pinned, powersave), revision 8fa2a48 (v0.12.11) with production automatic tiering ran 23 of 35 scenarios faster than the same binary with the JIT detached (patched QuickJS-NG fd0a0210), e.g. scalar-control-flow 49.2x and fibonacci-recursive 27.1x, tied on 7 and 2-4% slower on 5, and slower than Bun 1.4.0 on all 35; latencies are medians over 30 fresh processes of 16 timed ten-call batches after 64 warmup batches, with checksums outside timing and paired bootstrap 95% intervals, built with rustc 1.98.1 / LLVM 22.1.8 release.

## Use it when

- Rust applications already embedding rquickjs/QuickJS whose scripts spend time in numeric loops, integer/bit arithmetic, Float64 math, packed or typed-array traversal or monomorphic property access (README matrix: 22-49x the interpreter on these kernels)
- Embedders that want QuickJS's small footprint and fast startup but need hot pure-JS kernels several times faster, and can call jit.poll() regularly from the runtime thread
- Linux, macOS or Windows on x86_64 or aarch64, where native execution is enabled
- Teams willing to pin an exact patch version (or git revision) of all quickjs-jit crates and track a fast-moving experimental project

## Skip it when

- Peak JavaScript throughput: Bun 1.4.0 (JavaScriptCore) beats it on all 35 scenarios, from 0.73x Bun speed on fibonacci-recursive down to 0.012x on methods-dynamic; V8 was not measured
- Workloads dominated by strings, JSON, RegExp, Map/Set/BigInt, closures, exceptions or promises: the current matrix shows tied or 1-4% slower than the interpreter (json-codec 0.96x, strings-json 0.96x, collections 0.98x)
- C or C++ embedders: the JIT is Rust and is consumed through rquickjs crates; taking it into a C++ host means vendoring the patched C engine plus the Rust runtime
- wasm32 and other targets: the compiler feature is excluded on wasm and native execution is limited to little-endian x86_64/aarch64 on Linux, macOS and Windows
- Production code that needs a stable, published release: crates.io stops at 0.12.6 (2026-09-03) while the measured 0.12.11 is git-only, and the JIT ABI rejects mismatched runtime/core/sys patch versions at startup

## How it is fast

Hot functions and loops (default thresholds 32 calls / 56 loop iterations) are profiled through interpreter feedback probes and compiled on one background worker by Cranelift 0.116: a Tier 1 baseline compiler and a Tier 2 optimizing tier built on a semantic SSA IR with Int32/Float64 speculation, shape-token property guards, a bounded polymorphic inline cache, effect-free inlining, loop-invariant guard motion, OSR and deoptimization back to the interpreter. Automatic tiering runs profitability trials and demotes artifacts that do not beat the interpreter, which is why string, JSON, regexp, collection and exception scenarios end up at interpreter speed rather than slower.

## Compared with alternatives

Pick it over goja-perf when the host is Rust rather than Go and you want a JIT rather than a faster interpreter, and over Graal.js, Perry or katsu when you need QuickJS's tiny embeddable footprint with hot-loop speedups rather than peak or cold-start speed; for any workload where Bun or V8 can be used, they remain faster.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | quickjs-jit, quickjs-jit-core, quickjs-jit-sys (vendored patched QuickJS-NG built with the cc crate), quickjs-jit-runtime with feature 'compiler' (cranelift-codegen/frontend/module/object/native 0.116, gimli, postcard, target-lexicon, serde, serde_json, serde_yaml, rustc-hash; libc or windows-sys) |
| **Minimum toolchain** | Rust 1.87 (rust-version in Cargo.toml); benchmarks built with rustc 1.98.1 / LLVM 22.1.8; a C compiler for the vendored engine |
| **Platforms** | Native JIT: x86_64 and aarch64 on Linux, macOS and Windows (little-endian); other rquickjs targets (i686, loongarch64, musl, wasm32-wasip1/2) run interpreter-only |
| **Thread safety** | Inherits rquickjs: a Runtime is driven from one thread; compilation runs on a background worker (1 by default) and installation and reclamation happen only in jit.poll() on the runtime thread |
| **Drop-in for the baseline** | partial: source-compatible with rquickjs (same library name, Cargo package rename) and runs unchanged JavaScript, but the host must attach the JIT, call poll(), and pin exact matching patch versions of all crates |

## Gotchas

- Tier-up depends on the host calling jit.poll(): the benchmark polls after every ten-call batch and warms 641 calls before timing, so an embedder that rarely polls sees slower or no tier-up; the README's own gpui-shell section shows 0.12.10 regressing a real host 8x (127.1 vs 15.1 us per compute render) while the kernel matrix looked fine.
- The README and benchmarks/README still carry historical tables where the JIT beats Bun (Apple M3 scalar-loop 4.8x Bun, focused iterative Fibonacci 1.45x faster than Bun); docs/PERFORMANCE_NEXT.md says those Bun readings were inflated 1.2x-32x by a one-off JSC stall under 'bun -e' and must not be cited. Only the v3 (file-launch) matrix is valid.
- The 'QuickJS' column is this repo's patched QuickJS-NG (JIT ABI compiled in, feedback probes gated off, shape header grown 64 to 72 bytes), not a stock QuickJS-NG or Bellard QuickJS build; all workloads run a fixed tiny input (workload(2000, 0)), so the 20-50x figures are per-call latencies of 2-80 us kernels.
- Stability is still moving: 0.12.11 deliberately pushed exceptions-sync and for-of-array back to interpreter speed (0.21x and 0.36x of 0.12.10) to fix the host regression; development is AI-assisted (recent commits co-authored by claude and codex), and the install snippet at the top of the README still pins =0.12.2.

## Known shortcomings

- First-party README matrix (v0.12.11, commit 8fa2a48): the control is the same QuickJS-NG binary with the JIT detached, the C compiler is unnamed, the JIT is still compiling during timed runs on some kernels, and quickjs-jit is slower than Bun on all 35 scenarios. Rust plus Cranelift fork of DelSkayn/rquickjs (crates.io has only 0.12.6); filed under jits.
- Enricher: the harness is sound (checksums outside timing, paired bootstrap) but the 'QuickJS' column is the repo's own patched QuickJS-NG (about 28 patches with the JIT ABI compiled in), not stock; the workload is a fixed tiny input (workload(2000, 0)) and tier-up needs a host jit.poll(). The README and benchmarks/README still carry old JIT-beats-Bun tables that docs/PERFORMANCE_NEXT.md calls invalid (a 'bun -e' JavaScriptCore stall inflated Bun 1.2x-32x); the README install snippet pins 0.12.2 while crates.io stops at 0.12.6.

## Caveats and trade-offs

First-party matrix run on the author's own machine, though the harness, scripts, raw process records, metadata and binary hashes are all in the repo. Not a V8 win: every scenario is slower than Bun (JavaScriptCore) and V8 was not measured. The interpreter control is QuickJS-NG (fd0a0210) in the same binary with the JIT detached, not Bellard's QuickJS. Wins are on scalar and numeric kernels (many 20-50x); string, JSON, collection, regexp and exception scenarios are tied or 1-4% slower. v0.12.11 fixed a 0.12.10 regression in real gpui-shell renders by deferring P2 opcodes, which gave back exceptions-sync (0.21x the speed of 0.12.10) and for-of-array (0.36x) to interpreter speed. The protocol warms 640 calls and polls the JIT after every batch, so embedders that never poll see different tier-up behaviour; the diagnostics table shows compilation still active during timing on some kernels (float64-dense: only 4 of 30 processes quiet, 29 outlier batches; numeric 9 quiet). The JIT is Rust (Cranelift 0.116) over a vendored C engine, outside a strict C++ filter. Development is AI-assisted (AGENTS.md; recent commits co-authored by claude). crates.io has only 0.12.6; the README warns that runtime and core crates must share an exact patch version.

Experimental tiered JIT on top of QuickJS-NG; the JIT ABI depends on internal QuickJS structure layouts so the runtime, core and sys crates must be the same patch version; consumed as a Rust crate (rquickjs API), so C++ users would have to take the C engine plus JIT sources from the repo directly.

## Maintenance

Active (last commit 2026-09-30, near-daily releases by Longbridge with AI co-authors) and MIT-licensed, but experimental and only 15 stars; the benchmarked 0.12.11 must be taken from git with all crates pinned to one revision.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** The README's current JIT_MATRIX block (revision 8fa2a48, v0.12.11, measured 2026-09-30) carries every quoted number, and the harness is public: benchmarks/ (jit-bench built with 'cargo build --release --manifest-path benchmarks/Cargo.toml', benchmarks/paired.py, benchmarks/scripts/\*.js, protocol shared-js-multibatch-v3) with raw process records and metadata JSON under benchmarks/results/. Toolchain (rustc 1.98.1 / LLVM 22.1.8, release build), CPU model (Intel Core i7-13700KF, CPU 8 pinned, powersave governor) and the QuickJS-NG commit are all stated, so A holds; the C compiler that builds the vendored engine is not named, but the interpreter control is the same binary with the JIT detached.
- **Verifier notes:** All quoted numbers match the README's current matrix row by row; metadata checked on the GitHub page (MIT, 15 stars, not archived, last commit 2026-09-30) and crates.io. The repo is a GitHub fork of DelSkayn/rquickjs, but the JIT is new work, so it is not a duplicate of the listed QuickJS or QuickJS-NG entries. It is a JIT, so the 'jits' category may fit better than language-interpreters.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `is_fork_of`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/longbridge/quickjs-jit>
  - <https://github.com/longbridge/quickjs-jit/commits>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/README.md>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/results/shell-tiering-8fa2a48-metadata-x86_64.json>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/sys/build.rs>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/jit/Cargo.toml>
  - <https://crates.io/api/v1/crates/quickjs-jit>
- **Sources the enricher read:**
  - <https://github.com/longbridge/quickjs-jit>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/README.md>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/README.md>
  - <https://github.com/longbridge/quickjs-jit/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/batch-driver.js>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/run.rs>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/suites.lock>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/scripts/scalar-control-flow.js>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/scripts/scalar-expressions.js>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/scripts/fibonacci-iterative.js>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/scripts/fibonacci-recursive.js>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/scripts/float64-dense.js>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/scripts/quickjs-bitops.js>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/benchmarks/scripts/numeric.js>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/jit/Cargo.toml>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/jit/src/lib.rs>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/jit/src/config.rs>
  - <https://github.com/longbridge/quickjs-jit/tree/main/jit/src>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/sys/build.rs>
  - <https://github.com/longbridge/quickjs-jit/tree/main/sys/patches>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/sys/patches/README.md>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/docs/PERFORMANCE_NEXT.md>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/longbridge/quickjs-jit/HEAD/LICENSE>
  - <https://github.com/longbridge/quickjs-jit/issues?q=is%3Aissue>
  - <https://github.com/longbridge/quickjs-jit/commits/main>
  - <https://crates.io/api/v1/crates/quickjs-jit>
  - <https://crates.io/api/v1/crates/quickjs-jit-runtime>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/longbridge/quickjs-jit`) · [data/wave12/enrich/raw/github_com_longbridge_quickjs_jit.json](../../../data/wave12/enrich/raw/github_com_longbridge_quickjs_jit.json) (enrichment confidence 0.75)

</details>
