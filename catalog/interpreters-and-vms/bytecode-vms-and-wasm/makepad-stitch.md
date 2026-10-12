# Stitch (makepad)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust Wasm interpreter using tail-call threaded code; about 1.1x faster than WAMR fast-interp in wasmi-benchmarks (bug-fixed fork measured).

| | |
|---|---|
| **Beats** | WAMR fast interpreter and Wasmtime Pulley (execution); Wasmtime Cranelift (startup) |
| **Claimed result** | wasmi-benchmarks (AMD EPYC 7763, run by the Wasmi author): execution geomean over 18 common cases has the Robbepop/stitch v0.1-dev fork about 1.05-1.10x faster than wasm3 and Wasm3-class interpreters; over Stitch's own 20 cases 1.10x vs WAMR fast-interp and 1.035x vs wasm3; Wasmi v2 is 1.26x faster than Stitch (derived from the per-case SVGs). First-party README table: old Wasmi 0.31.2 baseline, wasm3 runner commented out. |
| **Workload** | wasmi-benchmarks execution suite: 22 cases, geometric mean of per-case ratios against the fastest runtime for each case. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7763 (named in the plot title; the plots repo also holds data for Apple M2 Pro, Apple M4 Pro, an Intel i7700 and Intel Xeon Platinum 8573C, not read here) |
| **Compiler and flags** | cargo run --release in coremark/ (Rust release profile; rustc version not stated). Harness pins wasmi 0.31.2 and wasmtime 20.0.1; the wasm3 runner (wasm3 crate 0.3.1) is commented out in coremark/Cargo.toml and coremark/src/main.rs at HEAD. |
| **Adoption** | 144 stars |
| **Last commit** | 2025-11-20 |
| **Links** | [repository](https://github.com/makepad/stitch) · [benchmark](https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg) |

## Verdict

Independent wasmi-benchmarks (criterion, AMD EPYC 7763, Aug 2026) measured the bug-fixed fork Robbepop/stitch v0.1-dev at a geomean of 15.73x the per-case fastest runtime, vs 16.51x Wasm3, 17.07x WAMR fast-interp, 27.92x Wasmtime Pulley and 12.40x Wasmi v2; the geomean covers the 18 of 21 execute cases every runtime ran (I reproduced all these values from the per-case plots). The first-party README CoreMark scores (Stitch 2950/1684/4592 vs Wasm3 2911/1734/3951 on M2 Pro/Xeon E312xx/i9-13900K) show Stitch roughly tied with Wasm3 on Mac and Linux and about 1.16x ahead on Windows.

## Use it when

- A pure-Rust, dependency-free Wasm interpreter on 64-bit macOS, Linux or Windows where JIT is not allowed and fast build times matter (README: 2.29 s build vs 15.61 s Wasmi and 81 s Wasmtime on M2 Pro).
- Compute-heavy MVP Wasm modules (no SIMD, no tail calls) where an interpreter within about 10% of WAMR fast-interp and Wasm3 is acceptable.
- Experiments with tail-call threaded interpreter design in Rust; the executor and compiler are compact enough to read.
- Hosts that already have a Wasmtime-style embedding and want an interpreter fallback with a similar API shape.

## Skip it when

- Anything correctness-critical: upstream issues #3 and #4 (open since July 2025 and June 2026) show live locals and stack registers not preserved on entering block/if/loop, so valid modules return wrong values; the fixes exist only in the Robbepop/stitch v0.1-dev fork.
- If you want the fastest Rust interpreter: in the same wasmi-benchmarks run Wasmi v2 (x12.40) and Silverfir-nano (x9.02) beat Stitch (x15.73) on AMD EPYC 7763; Stitch trails Wasmi v2 by about 1.26x over the 20 cases it runs (derived from page data).
- Large or modern modules: function bodies over 128 KiB, data segments over 1 MB and more than one memory are rejected at HEAD (src/config.rs), and SIMD, WASI, tail calls and the BigInt proposal are unsupported; FFmpeg is reported not to load (issue #1).
- 32-bit targets, Miri or any build where LLVM might not apply sibling-call optimisation; there is no trampoline fallback, so the interpreter would overflow the native stack.
- Untrusted code with a strong safety requirement: large amounts of unaudited unsafe code (README).

## How it is fast

Each Wasm instruction is compiled into a sequence of 'threaded' Rust functions that all share one signature, so each handler ends with a sibling call (tail call) that LLVM turns into a jump. Six integer and two float values (ip, sp, memory base and size, an integer and two float accumulators) are passed as arguments, which keeps the hot interpreter state in hardware registers; on Windows it forces the sysv64 ABI to get enough argument registers. Functions are compiled lazily on first call, and many specialised variants per instruction trade instruction-cache pressure for fewer stack moves.

## Compared with alternatives

Pick it over wasm3 or WAMR only when you need a pure-Rust, dependency-free interpreter with fast compile times and can live with roughly equal speed (1.04x over Wasm3, 1.10x over WAMR in wasmi-benchmarks); pick Wasmi v2 for a faster Rust interpreter with tail-call support, Silverfir-nano for the fastest interpreter in that suite, and wasm3 for 32-bit or microcontroller targets.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (criterion and wast are dev-dependencies only) |
| **Minimum toolchain** | Rust edition 2021; HEAD uses size_of/align_of from the prelude, so Rust 1.80+ (inferred, not documented); release build required (debug profile set to opt-level 1) |
| **Platforms** | 64-bit only: x86-64 and aarch64 on macOS, Linux, Windows (README); no 32-bit |
| **Thread safety** | Engine is Arc/Mutex-backed and cloneable across threads; execution needs &mut Store; host functions must be Send + Sync; Store Send/Sync not documented |
| **Drop-in for the baseline** | partial — API shape is close to Wasmtime/Wasmi (Engine/Store/Linker/Func) but it is a different crate with fewer proposals and no WASI |

## Gotchas

- Open wrong-result bugs #3 and #4 (filed by the Wasmi author): e.g. a block with br_if returns 0 instead of 42. The wasmi-benchmarks numbers come from the Robbepop/stitch v0.1-dev fork (initial snapshot Sep 2025), which fixes #3/#4, raises the 128 KiB function-body limit and carries further fixes (memory.grow frame fixup, grow_with_stack, operand popping) whose presence at upstream HEAD was not confirmed; the published speed is for code that is not in makepad/stitch.
- crates.io still serves makepad-stitch 0.1.0 from 2024-05-13 (2,521 downloads); repo HEAD (Nov 2025) is newer and unreleased, so `cargo install makepad-stitch` gets the old code.
- Func::call without a caller-supplied Stack allocates a fresh zeroed 8 MiB stack per top-level call (src/func.rs); pass your own Stack for many short calls.
- README CoreMark table compares against Wasmi 0.31.2 (now about 4x slower than Wasmi v2 in wasmi-benchmarks: x51.35 vs x12.40), and the Wasm3 runner is commented out of coremark/, so the Wasm3 column cannot be rerun from the repo.

## Known shortcomings

- The wasm3 runner is commented out of the harness and the baseline is an old Wasmi 0.31.2; open wrong-result bugs (issues #3 and #4). The independent wasmi-benchmarks run uses the bug-fixed fork Robbepop/stitch v0.1-dev, about 1.05-1.10x faster than wasm3, with Wasmi v2 faster still. Rust, not C++.
- Enricher (via tinywasm): the wasmi-benchmarks cross-check builds wasmtime 47.0.0 with default-features=false, so its Cranelift startup column compiles single-threaded and startup gaps against Wasmtime are overstated.
- Enricher: the wasmi-benchmarks EPYC geomean reproduces from the per-case SVGs over 18 common cases, not 22 (bulk-ops, counter-param and fibonacci-tail are dropped); over its own 20 cases Stitch is only 1.10x faster than WAMR and 1.035x than wasm3, and Wasmi v2 is 1.26x faster than Stitch. The measured code is the Robbepop/stitch v0.1-dev fork, which fixes issues #3 and #4, raises the 128 KiB function-body limit that upstream src/config.rs still caps (likely cause of the FFmpeg issue #1) and fixes memory.grow, grow_with_stack and operand pops; crates.io still has 0.1.0 from 2024-05-13.

## Caveats and trade-offs

Only a single CoreMark workload; the edge over wasm3 is within a few percent on Mac and negative on Linux, and Wasmtime's JIT is 4-8x faster than Stitch, so it does not beat any JIT baseline in the category. The Wasmi baseline is the old 0.31.2 stack interpreter (open issue #2 asks for an update since Wasmi 0.32+ is much faster); the wasm3 runner is commented out of the published harness. Open correctness issues #3 and #4 (filed by the Wasmi author, July 2025 and June 2026): live locals and registers are not preserved on entering block/if/loop, so some modules return wrong results (example returns 0 instead of 42); unfixed upstream. Relies on LLVM sibling-call optimisation with no guarantee; 64-bit only; no SIMD or WASI; large amount of unaudited unsafe code (README). Independent wasmi-labs/wasmi-benchmarks plots (Aug 2026; criterion, profile.bench lto=fat, codegen-units=1) measure a bug-fixed fork (Robbepop/stitch branch v0.1-dev, shown as 'Stitch (lazy)'): geomean execute time relative to the fastest runtime is Stitch 15.73 vs Wasm3 (eager) 16.51 on AMD EPYC 7763, 11.94 vs 12.64 on Apple M2 Pro, 9.70 vs 10.71 on Apple M4 Pro (about 1.05-1.10x faster than Wasm3, derived from page data), but Wasmi v2 (eager) is faster than Stitch on all three (12.40, 8.83, 8.06). The record's claim about rebeckerspecialties/wasm-benchmark was not checked by the verifier. [retier] The wasm3 runner is commented out of the first-party harness and its baseline is Wasmi 0.31.2. Open wrong-result bugs in upstream (issues #3, #4); the measured Robbepop/stitch v0.1-dev fork fixes them, raises the 128 KiB function-body limit still capped in upstream src/config.rs (likely cause of the FFmpeg issue #1), and fixes memory.grow, grow_with_stack and operand pops; crates.io still ships 0.1.0 (2024-05-13). wasmi-benchmarks builds wasmtime without parallel compilation, so startup gaps against Wasmtime are overstated. Rust, not C++.

Relies on LLVM sibling-call optimization (not guaranteed) and a 64-bit target only; about 15k lines of code with significant unsafe and no external audit (README).

## Maintenance

Upstream makepad/stitch saw a cleanup burst in Nov 2025 but no response to four open issues including two wrong-result bugs; MIT and small enough to vendor, but treat it as experimental and prefer the Robbepop fork or Wasmi v2 for real use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now C.
- **Tier reason:** First-party CoreMark table in the README with CPU models and a public harness (coremark/src/main.rs, cargo run --release), but no rustc or C compiler version, and the wasm3 path is commented out of the harness at HEAD, so the Wasm3 column cannot be reproduced as published. Independent wasmi-benchmarks plots exist but measure a bug-fixed fork (Robbepop/stitch v0.1-dev), not this repo, so they do not lift this entry to B.
- **Verifier notes:** README numbers match the record exactly (2950/1684/4592 vs Wasm3 2911/1734/3951; Windows about 1.16x, derived). Keep at C; shortcomings to record: wasm3 runner commented out of the harness, stale Wasmi 0.31.2 baseline, unfixed wrong-result bugs (issues #3, #4), Wasmi v2 now faster in the independent wasmi-benchmarks suite. Metadata checked: MIT, 144 stars, last commit 2025-11-20, active.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/makepad/stitch>
  - <https://github.com/makepad/stitch/commits>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/README.md>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/coremark/Cargo.toml>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/coremark/src/main.rs>
  - <https://github.com/makepad/stitch/issues?q=is%3Aissue>
  - <https://github.com/makepad/stitch/issues/3>
  - <https://github.com/makepad/stitch/issues/2>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/stitch/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasm3/Cargo.toml>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/commits/main>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/main/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/main/data/apple-m2-pro/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/main/data/apple-m4-pro/lin-scale/geomean-execute.svg>
  - <https://github.com/Robbepop/stitch/tree/v0.1-dev>
  - <https://github.com/Robbepop/stitch/commits/v0.1-dev/>
- **Sources the enricher read:**
  - <https://github.com/makepad/stitch>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/README.md>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/coremark/Cargo.toml>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/coremark/src/main.rs>
  - <https://github.com/makepad/stitch/tree/main/src>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/code.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/stack.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/engine.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/func.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/store.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/executor/mod.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/compiler/mod.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/runtime/memory.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/module.rs>
  - <https://raw.githubusercontent.com/makepad/stitch/HEAD/src/decode.rs>
  - <https://github.com/makepad/stitch/issues?q=is%3Aissue>
  - <https://github.com/makepad/stitch/issues/1>
  - <https://github.com/makepad/stitch/issues/3>
  - <https://github.com/makepad/stitch/issues/4>
  - <https://github.com/makepad/stitch/commits>
  - <https://crates.io/api/v1/crates/makepad-stitch>
  - <https://github.com/wasmi-labs/wasmi-benchmarks>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/stitch/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/stitch/lib.rs>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/bins>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/bins/plot.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/main/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/tree/main/data/amd-epyc-7763/lin-scale>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/tree/main/data/amd-epyc-7763/lin-scale/execute>
  - https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/main/data/amd-epyc-7763/lin-scale/execute/ (all 21 per-case SVGs)
  - <https://github.com/Robbepop/stitch/commits/v0.1-dev/>
  - <https://github.com/Robbepop/stitch/commit/9d117f84344c9c7fd58ced48af8fdeb5442b19f4>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/makepad/stitch`) · [data/wave12/enrich/raw/github_com_makepad_stitch.json](../../../data/wave12/enrich/raw/github_com_makepad_stitch.json) (enrichment confidence 0.8)

</details>
