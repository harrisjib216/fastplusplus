# Fizzy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Dependency-free C++17 WebAssembly 1.0 interpreter whose eager parse-and-instantiate beats Cranelift JIT runtimes and WAMR fast-interp on startup.

| | |
|---|---|
| **Beats** | Wasmtime (Cranelift), Wasmer (Cranelift) startup |
| **Claimed result** | Startup (compile plus instantiate) geomean relative to the fastest runtime per test (lower is better), AMD EPYC 7763: Fizzy x17.83 vs WAMR fast-interpreter x56.73, V8 x33.27, Wasmer (Cranelift) x1484.15, Wasmtime (Cranelift) x1634.19 (about 3.2x lower than WAMR fast-interp, derived from page data). Fizzy is below WAMR fast-interp on all five CPU data sets (Apple M2 Pro 18.69 vs 49.35, Apple M4 Pro 17.20 vs 43.90, Intel i7-7700 17.63 vs 61.71, Xeon Platinum 8573C 11.21 vs 44.15) and below V8 on four of them, but not on Apple M2 Pro (Fizzy 18.69 vs V8 16.97). |
| **Workload** | wasmi-benchmarks startup suite: compile + instantiate of 7 modules from tiny to huge, geometric mean of per-case ratios against the fastest runtime for each case. |
| **Metric** | startup |
| **Hardware** | AMD EPYC 7763 (named in the plot title; the plots repo also holds data for Apple M2 Pro, Apple M4 Pro, an Intel i7700 and Intel Xeon Platinum 8573C, not read here) |
| **Compiler and flags** | Built by the wasmi-benchmarks harness through Robin Freyler's fizzyx 0.1.1 crate: fizzyx-sys build.rs runs Fizzy's CMake via the Rust cmake crate with FIZZY_TESTING=OFF, FIZZY_WASI=OFF and a force-included compat_shim.hpp; Rust harness profile.bench lto=fat, codegen-units=1. C++ compiler, version and CMake build type are not stated. Fizzy's own README performance setup: CMAKE_BUILD_TYPE=Release (-O3), LTO, latest GCC or Clang, libstdc++, no -march=native. |
| **Adoption** | 241 stars |
| **Last commit** | 2025-11-10 |
| **Links** | [repository](https://github.com/wasmx/fizzy) · [benchmark](https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg) |

## Verdict

In Robin Freyler's wasmi-benchmarks startup suite (criterion timing of parse + validate + instantiate of 7 modules through his fizzyx Rust bindings; Fizzy built by cmake-rs, which resolves the Cargo bench profile to CMAKE_BUILD_TYPE=Release, i.e. -O3 -DNDEBUG without LTO, C++ compiler version not stated), Fizzy's geomean on an AMD EPYC 7763 was 17.83x the per-case fastest runtime versus WAMR fast-interp 56.73x, V8 33.27x, Wasmer Cranelift 1484x and Wasmtime Cranelift 1634x. The harness unwraps Module::new, so each reported time is a successful parse, not an early error; the win is startup only, and execution on the same suite is about 2.7x slower than WAMR fast-interp.

## Use it when

- Short-lived modules where parse + validate + instantiate dominates and you would otherwise pay JIT compile time (Wasmtime/Wasmer Cranelift startup geomean \~1500-1600x the fastest runtime vs Fizzy 17.8x on EPYC 7763).
- Deterministic contract execution that needs per-instruction gas metering, a call-depth bound and a hard memory cap from a small, heavily tested C++17 codebase.
- Embedding a WebAssembly 1.0 engine into a C or C++ host with no third-party dependencies, via a C API or CMake find_package.
- Modules that use only WebAssembly 1.0 features and small-to-medium code sections (it won bz2, coremark, argon2 and erc20 startup against V8 on EPYC).

## Skip it when

- Compute-heavy or long-running guest code: execution geomean is 45.6x the fastest runtime vs WAMR fast-interp 17.1x and V8 1.05x on EPYC 7763, and Fizzy's own v0.5.0 table shows wasm3 0.4.7 at 26% of Fizzy's execution time.
- Modules that need post-MVP features (bulk memory, SIMD, multi-value, reference types, tail calls); the wasmi-benchmarks harness skips Fizzy on its bulk-ops, fibonacci-tail and counter-param execute tests.
- Running WASI programs: fizzy-wasi implements only a limited subset of wasi_snapshot_preview1 over uvwasi, failed the libsodium suite (no poll_oneoff), and has open memory-corruption reports (#857 invalid write in fd_write, #858 invalid read) unanswered since 2024-08.
- Very large modules or when startup is the only metric: lazy validators start faster (Wasmi v2 lazy x1.37, Wasm3 lazy x2.77) and V8 beat Fizzy on ffmpeg (35 ms vs 215 ms) and spidermonkey (11 ms vs 52 ms).
- Projects that need an actively maintained engine: no code changes since 2023-03-03, and big-endian targets are rejected at CMake configure time.

## How it is fast

Parsing and validation run in one pass (the spec's validation algorithm with a control-frame stack) that emits a compact internal code: opcodes and their immediates in one byte array, with branch targets and stack-drop counts resolved at parse time so execution keeps no control stack. Each function's maximum operand-stack height is precomputed, so arguments, locals and operand stack share one allocation (128-byte inline buffer, heap above that). There is no code generation, so startup is a linear parse, which is why its startup geomean is 83-92x lower than Wasmer and Wasmtime with Cranelift JIT compilation (derived from page data); execution is a plain switch-dispatch loop, with metering compiled in or out by a template parameter.

## Compared with alternatives

Pick Fizzy over wasm3, WAMR or Wasmi when you want a dependency-free C++17 interpreter with gas metering, strict spec conformance and fast eager startup, and execution speed is secondary; wasm3 and WAMR fast-interp run code roughly 2.7-4x faster, Wasmi (lazy) and DLR-FT wasm-interpreter start faster, and toywasm or submilli-wasm give similar startup with more proposal support.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the library (uvwasi only for the optional fizzy-wasi tool; test tools pull dependencies through Hunter) |
| **Minimum toolchain** | C++17, CMake 3.15; GCC 15/libstdc++ 15 and libc++ 19+ (Xcode 16) need small source shims (missing &lt;algorithm&gt; include, std::char_traits&lt;unsigned char&gt;) |
| **Platforms** | little-endian only; x86-64 and 32-bit x86 (SSE2 required for compliant floats); aarch64 macOS ran in wasmi-benchmarks via the fizzyx bindings, but upstream issue #709 'Support Apple Silicon natively' is still open |
| **Thread safety** | not documented; ExecutionContext is described as per execution thread and an Instance owns its mutable memory and globals, so do not share an Instance across threads without external locking |
| **Drop-in for the baseline** | partial — same job as Wasmtime/Wasmer/WAMR (load, link host functions, call exports) but its own C API, at most one result per function and only function imports in the fizzyx Rust bindings; no wasm-c-api support (issue #696 open) |

## Gotchas

- Each WebAssembly call recurses into execute() on the native C++ stack, up to CallStackLimit = 2048 nested calls before trapping; size host thread stacks for that depth.
- Fizzy does not touch the floating-point environment: the host must keep round-to-nearest and must not enable FP exception traps (feenableexcept), or results become non-compliant or unpredictable; x87 builds need -msse2 -mfpmath=sse.
- fizzy_instantiate caps linear memory at 256 MB (4096 pages) by default unless memory_pages_limit is raised (max 65536 pages = 4 GB); memory is a zero-filled std::basic_string&lt;uint8_t&gt; allocated at instantiate.
- Upstream no longer builds unmodified on GCC 15 (capi.cpp uses std::transform without &lt;algorithm&gt;) or libc++ 19+ (no char_traits&lt;unsigned char&gt;); the fizzyx crate force-includes a compat_shim.hpp, and you would need the same patch.

## Known shortcomings

- Startup-only win in the wasmi-benchmarks suite (x17.83 vs WAMR fast-interp x56.73 and V8 x33.27 on an EPYC 7763); loses execution (x45.63 vs WAMR x17.07), V8 is faster on ffmpeg, spidermonkey, pulldown-cmark and the M2 Pro geomean. MVP only, no code change since March 2023, run through a wrapper written by the Wasmi author with no compiler versions.
- Enricher (via tinywasm): wasmi-benchmarks builds wasmtime 47.0.0 with default-features=false, so the Cranelift startup column compiles single-threaded and the startup gap against Wasmtime is overstated against a default multi-core build.
- Enricher: no harness flaw (Module::new unwrap makes all 7 startup timings real parses; cmake-rs maps the bench profile to CMake Release -O3 -DNDEBUG, no LTO); execution is 2.7x slower than WAMR, no code commits since 2023-03-03, does not build unpatched on GCC 15 or libc++ 19+ (fizzyx compat_shim), and fizzy-wasi memory-corruption issues #857 and #858 have been open since August 2024.

## Caveats and trade-offs

Startup-only win: on the same suite Fizzy's execution geomean is x45.63 vs WAMR fast-interpreter x17.07, Wasm3 (eager) x16.51 and V8 x1.05 on EPYC 7763 (about 2.7x slower than WAMR fast-interp, derived from page data), so it is not faster than any category baseline at running code. Per-test startup on EPYC: V8 is faster than Fizzy on ffmpeg (35.46 ms vs 215.36 ms), spidermonkey (10.94 ms vs 52.31 ms) and pulldown-cmark (2.30 ms vs 2.72 ms); Fizzy wins on bz2, coremark, argon2 and erc20. Lazy-validating interpreters are far faster at startup (Wasm3 lazy x2.77, Wasmi v2 lazy x1.37). The WAMR comparison is against its fast-interpreter mode, which precompiles at load. Suite is maintained by the author of the competing Wasmi runtime and the Fizzy bindings (fizzyx) are his; plots are regenerated in place (last EPYC update 2026-08-25, values as of 2026-10-06). Fizzy implements WebAssembly 1.0 (MVP) only. Latest commit (2025-11-10) is a README merge; the last code change was 2023-03-03. Fizzy's own CHANGELOG (v0.5.0 detailed results, hardware not stated) shows execution about 5.1x faster than WABT 1.0.19 interpreter (508%) but only 1.7x faster than WABT 1.0.12 (167%), while wasm3 0.4.7 took 26% of Fizzy's execution time and 27% of its instantiation time. Fizzy failed in Frank Denis's libsodium 2021-Q1 run (needs WASI poll_oneoff).

WebAssembly 1.0 only; supports no GC, SIMD or newer proposals. Built for deterministic blockchain use (metering, canonical floating point).

## Maintenance

Dormant: the last code change was 2023-03-03 (last release 0.8.0, 2022-06-28, also the latest fizzy crate), later commits are README-only and 2024 security reports are unanswered; Apache-2.0, dependency-free and small enough to vendor if you carry the GCC 15/libc++ 19 build patches.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now B.
- **Tier reason:** Independent third-party suite wasmi-benchmarks (public harness benches/criterion/startup.rs, runtimes/fizzy/lib.rs; plots in wasmi-labs/wasmi-benchmarks-plots) shows Fizzy at x17.83 startup geomean vs WAMR fast-interpreter x56.73, V8 x33.27, Wasmer Cranelift x1484.15 and Wasmtime Cranelift x1634.19 on an AMD EPYC 7763 (values matched to runtime names by SVG y-coordinate). CPU model and Cargo profile are public but the C++ compiler, its version and the CMake build type used for Fizzy are not stated, so not A.
- **Verifier notes:** Numbers verified exactly on the EPYC 7763 geomean-startup plot, mapping labels to values by y-coordinate rather than file order. Real but narrow win: startup (parse plus validate plus instantiate) only; execution is about 2.7x slower than WAMR fast-interp and about 43x slower than V8, and V8 beats it on the three largest startup modules and on the M2 Pro geomean. Code dormant since 2023-03; record shortcomings: startup-only, execution slower than every baseline, MVP-only, wrapper written by competing-runtime author.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-execute.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/ffmpeg.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/spidermonkey.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/pulldown-cmark.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/bz2.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/coremark.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/argon2.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/startup/erc20.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/apple-m2-pro/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/apple-m4-pro/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/intel-i7700/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/intel-xeon-platinum-8573c/lin-scale/geomean-startup.svg>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/apple-m2-pro/lin-scale/geomean-execute.svg>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/tree/main/data>
  - <https://github.com/wasmi-labs/wasmi-benchmarks-plots/commits/main>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/startup.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/fizzy/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/fizzy/lib.rs>
  - <https://crates.io/api/v1/crates/fizzyx>
  - <https://raw.githubusercontent.com/wasmi-labs/fizzyx/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/fizzyx/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/fizzyx/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/wasmi-labs/fizzyx/HEAD/crates/fizzyx-sys/build.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/fizzyx/HEAD/crates/fizzyx-sys/Cargo.toml>
  - <https://github.com/wasmx/fizzy>
  - <https://github.com/wasmx/fizzy/commits/master>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/README.md>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2021-Q1>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/lib/fizzy/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/lib/fizzy/execute.cpp>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/lib/fizzy/parser_expr.cpp>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/lib/fizzy/instantiate.cpp>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/lib/fizzy/stack.hpp>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/lib/fizzy/execution_context.hpp>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/lib/fizzy/limits.hpp>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/lib/fizzy/module.hpp>
  - <https://raw.githubusercontent.com/wasmx/fizzy/HEAD/include/fizzy/fizzy.h>
  - <https://github.com/wasmx/fizzy/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/wasmx/fizzy/issues/857>
  - <https://github.com/wasmx/fizzy/commits/master>
  - <https://crates.io/api/v1/crates/fizzy>
  - <https://crates.io/api/v1/crates/fizzyx>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/fizzy/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/startup.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/fizzyx/HEAD/crates/fizzyx-sys/build.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/fizzyx/HEAD/crates/fizzyx-sys/shim/compat_shim.hpp>
  - <https://raw.githubusercontent.com/wasmi-labs/fizzyx/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/wasmi-labs/fizzyx/HEAD/README.md>
  - <https://raw.githubusercontent.com/rust-lang/cmake-rs/HEAD/src/lib.rs>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/wasmx/fizzy`) · [data/wave12/enrich/raw/github_com_wasmx_fizzy.json](../../../data/wave12/enrich/raw/github_com_wasmx_fizzy.json) (enrichment confidence 0.75)

</details>
