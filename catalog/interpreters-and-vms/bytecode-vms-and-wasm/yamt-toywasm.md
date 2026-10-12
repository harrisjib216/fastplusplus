# toywasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Portable C11 in-place WebAssembly interpreter with eager validation; instantiates modules about 90x faster than single-threaded Wasmtime/Wasmer Cranelift.

| | |
|---|---|
| **Beats** | Wasmtime and Wasmer (Cranelift) startup |
| **Claimed result** | Startup geomean on AMD EPYC 7763 relative to the per-case fastest runtime (lower is better): Toywasm x18.35 versus Wasmtime (Cranelift) x1634.19, Wasmer (Cranelift) x1484.15, Wasmtime (Winch) x298.15 and Wasmer (Singlepass) x162.12; V8 is x33.27. |
| **Workload** | wasmi-benchmarks startup suite: compile + instantiate of 7 modules from tiny to huge, geometric mean of per-case ratios against the fastest runtime for each case. |
| **Metric** | startup |
| **Hardware** | AMD EPYC 7763 (named in the plot title; the plots repo also holds data for Apple M2 Pro, Apple M4 Pro, an Intel i7700 and Intel Xeon Platinum 8573C, not read here) |
| **Compiler and flags** | Built by the wasmi-benchmarks harness through Robin Freyler's toywasmx 0.2 crate (features: upstream-default toggles plus tail-call): toywasmx-sys build.rs compiles toywasm with the Rust cc crate, -std=c11, -D_POSIX_C_SOURCE=199506L, -DNDEBUG, -fshort-enums; optimisation level from the Cargo bench profile (lto=fat, codegen-units=1). C compiler and version not stated. |
| **Adoption** | 119 stars |
| **Last commit** | 2026-08-01 |
| **Links** | [repository](https://github.com/yamt/toywasm) · [benchmark](https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks-plots/HEAD/data/amd-epyc-7763/lin-scale/geomean-startup.svg) |

## Verdict

wasmi-benchmarks times compile plus instantiate of 7 modules, from erc20 to ffmpeg, on an AMD EPYC 7763 GitHub Actions runner, with toywasm built by gcc-15 via the toywasmx 0.2 crate. Toywasm's startup geomean is x18.35 against the per-case fastest runtime, versus x1634.19 for Wasmtime Cranelift and x1484.15 for Wasmer Cranelift; Wasmtime was compiled without parallel compilation. The win holds on all five CPU data sets, but it is startup-only.

## Use it when

- You load large or many modules and run only a little of each, so instantiation latency dominates. In wasmi-benchmarks on EPYC 7763 it starts ffmpeg in about 211 ms, while Wasmtime Cranelift, built there without parallel compilation, is about 90x slower over the startup geomean.
- Hosts where a JIT is not allowed or not available: microcontrollers via NuttX (esp32), wasm32-wasi (toywasm runs on itself), i386, arm64, riscv64, NetBSD and Windows (core wasm only).
- Embedders who want a small, readable C codebase under BSD-2-Clause with broad proposal coverage (SIMD, threads, EH, tail-call, custom page sizes) and a low memory footprint. The author's ffmpeg startup run peaks at about 40 MB RSS, against 200-550 MB for Wasmtime and Wasmer.
- Sandboxing where read-only module mapping, restartable execution, timeouts (--timeout) and heap-usage limits (--max-memory) matter more than raw speed.

## Skip it when

- Compute-heavy work. In the author's own ffmpeg run it takes 65.0 s, against 18.4 s for Wasm3 and 23.1 s for the WAMR fast interpreter, and the JITs take 3.5-11.9 s. In wasmi-benchmarks its execution geomean is x318.96, the slowest of the runtimes.
- When startup is all that matters, lazy runtimes start faster: Wasm3 (lazy) is x2.77 and Wasmi lazy is x1.37-1.56, against toywasm x18.35. V8 starts ffmpeg and spidermonkey faster. On the author's MacBook the WAMR classic interpreter starts as fast (0.19 s vs 0.18 s).
- Projects that need a stable API or ABI: the README lists both as non-goals, and version numbers are not semver.
- Builds with GCC or MSVC: the musttail dispatch is enabled only under clang (platform.h). The README recommends clang with LTO, so other compilers produce a slower interpreter.
- Wasm GC, the component model, or full WASI on Windows: GC is an open request (#282), and Windows supports core wasm only.

## How it is fast

Startup is cheap because nothing is compiled. The module is decoded and validated eagerly, then executed in place from the read-only bytecode. Validation leaves only small side annotations: a jump table for forward branches (searched by binary search, with a 4-entry jump cache), local and result-type cell-index tables, and value-size annotations for value-polymorphic instructions. A Cranelift JIT instead has to generate machine code for every function. For execution it uses per-instruction handler functions chained with clang's musttail attribute, plus a locals cache and fast paths, and it deliberately avoids huge-switch and computed-goto dispatch.

## Compared with alternatives

Pick it over Wasm3 or WAMR when you want a smaller, cleaner C codebase with eager validation and read-only in-place execution, newer proposals (EH, tail-call, threads, custom page sizes) and a low RSS, and can accept 3-4x slower compute. Fizzy starts about as fast (x17.83), but its catalogue entry says it is WebAssembly 1.0 only and has had no code changes since 2023, whereas toywasm is maintained and covers WASI. Use Wasm3 or the WAMR fast interpreter when execution speed matters.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the core library. libc and POSIX are needed for WASI; wabt and cmocka are needed only for the tests; littlefs is optional. |
| **Minimum toolchain** | C11 and CMake. Clang with musttail (LLVM 13 or later) and LTO is recommended for speed; release binaries are built with clang and ThinLTO. |
| **Platforms** | Tested on CI: macOS amd64, Ubuntu amd64, i386, arm64 and riscv64 (the last two under qemu), Windows x64 (core wasm only) and wasm32-wasi. Tested manually: NuttX (esp32, sim) and NetBSD. armhf and s390x CI is disabled. |
| **Thread safety** | Not documented as a guarantee. Modules are mapped read-only and never modified (README). A build with TOYWASM_ENABLE_WASM_THREADS runs wasi-threads with shared memories, and each thread uses its own exec_context. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the execution caveat: wasmi-benchmarks builds toywasm through the toywasmx cc-crate build script, and its Linux CI sets CC=gcc-15 (.github/actions/install-dependencies). toywasm's platform.h defines __HAVE_MUSTTAIL only when __clang__ is defined, so under gcc INSN_SUCCESS falls back to returning to the dispatch loop after every instruction. The C code also gets no LTO, because the Cargo profile's lto=fat covers Rust only. That probably explains why toywasm runs about 18.7x slower than WAMR fast-interp on EPYC (gcc), against about 8.7x on Apple M2 Pro (macOS, where cc is presumably Apple clang, so musttail is on) and 3.5x slower than Wasm3 in the author's own clang build (derived from page data). The startup claim is not affected in toywasm's disfavour.
- Harness flaw on the baseline side: rt-wasmtime is built with default-features = false (features runtime and anyhow only), so it has no parallel-compilation feature and Cranelift compiles single-threaded. Real Wasmtime first runs use many threads: the author's ffmpeg startup shows 40.94 s user against 4.87 s real. The x1634 Wasmtime ratio is therefore inflated, though toywasm still wins on startup by a wide margin.
- Annotations cost memory. On ffmpeg (15.4 MB of code) they add about 3.1 MB: a 2.4 MB jump table plus the type and cell-index tables. Disabling them (--disable-jump-table and the cellidx options) makes execution about 10x slower (624 s against 65 s on ffmpeg).
- Pointer arithmetic on NULL in empty vectors trips UBSan pointer-overflow, and the build disables that sanitizer (issue #362, Sep 2026, raised by the nanowasm R package). Out-of-memory sometimes returns ENOMEM and sometimes traps (#258).

## Known shortcomings

- Startup-only win: execution is x318.96 against WAMR's x17.07 (about 18.7x slower) in the wasmi-benchmarks suite, and the author's own startup.csv has the WAMR classic interpreter at 0.19 s against toywasm's 0.18 s. Run through a wrapper written by the Wasmi author, no compiler versions.
- Enricher (via tinywasm): wasmi-benchmarks builds wasmtime 47.0.0 with default-features=false, so the Cranelift startup column compiles single-threaded and the startup gap against Wasmtime is overstated against a default multi-core build.
- Enricher: the wasmi-benchmarks Linux CI sets CC=gcc-15 while toywasm's platform.h gates musttail on __clang__, so the gcc build falls back to return-to-loop dispatch with no LTO on the C code (cargo lto=fat covers Rust only), which likely explains 18.7x slower than WAMR fast-interp on the EPYC against about 8.7x on the M2 Pro and 3.5x vs wasm3 in the author's clang run; the rt-wasmtime baseline is built default-features=false with no parallel compilation, so the x1634 ratio is inflated (the author's own run: 40.94 s user vs 4.87 s real). UBSan issue #362 (NULL+0) and OOM ENOMEM/trap inconsistency #258.

## Caveats and trade-offs

Startup-only win: on the same suite toywasm's execution geomean is x318.96 vs WAMR fast-interpreter x17.07, Wasm3 (eager) x16.51 and V8 x1.05 on EPYC 7763 (about 18.7x slower than WAMR fast-interp, derived from page data; 128.76 vs 14.77 on Apple M2 Pro). Per-test startup on EPYC: V8 is faster than toywasm on ffmpeg (35.46 ms vs 210.84 ms), spidermonkey (10.94 ms vs 56.01 ms) and pulldown-cmark (2.30 ms vs 2.63 ms). The WAMR comparison is against its fast-interpreter mode, which precompiles at load; the author's own startup.csv (https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/startup.csv, MacBook Pro 2018 2.2 GHz 6-core i7) shows WAMR classic interpreter at 0.19 s vs toywasm 0.18 s, wamr fast interp 0.70 s, Wasmtime cached 0.27 s and Wasmtime/Wasmer first run 4.87 s/4.56 s. Wasm3 (lazy) startup is x2.77 on EPYC, far lower. Suite is maintained by the author of the competing Wasmi runtime and the toywasm bindings (toywasmx) are his; plots are regenerated in place, values as of 2026-10-06. Author's own ffmpeg.wasm run (https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/ffmpeg.txt, same MacBook, compiler flags not stated): toywasm 65.02 s vs iwasm 2.4.4 classic interpreter 210.58 s (3.2x, derived), WasmEdge 0.17.0 interpreter 198.75 s, wazero interpreter 173.08 s, but slower than wasm3 18.43 s, iwasm fast interpreter 23.14 s and wasmi 29.56 s, and far slower than JIT runtimes (3.54-11.89 s); the README itself says toywasm is slower than Wasm3 and WAMR at execution by design (in-place interpretation). [retier] Startup-only win: execution is x318.96 against WAMR's x17.07 in the wasmi-benchmarks suite, but that suite builds toywasm with gcc-15 (platform.h gates musttail on __clang__, so dispatch falls back to return-to-loop and the C code gets no LTO), which likely explains 18.7x slower than WAMR on the EPYC against about 8.7x on the M2 Pro and 3.5x vs wasm3 in the author's clang run. The Wasmtime baseline is built default-features=false without parallel compilation, so the x1634 startup ratio is inflated (the author's own run: 40.94 s user vs 4.87 s real). The author's startup.csv has the WAMR classic interpreter at 0.19 s against toywasm's 0.18 s. Run through a wrapper written by the Wasmi author with no compiler versions. UBSan issue #362, OOM trap inconsistency #258.

In-place interpreter with low memory use and annotations built at load; the slowest runtime on the wasmi-benchmarks execution geomean.

## Maintenance

Active single-maintainer project (last commit 2026-08-01, 119 stars, 3,109 commits, 13 open issues) under BSD-2-Clause, small and portable enough to vendor (NuttX apps and the nanowasm R package already embed it), but its API and ABI are explicitly unstable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now B.
- **Tier reason:** Independent third-party suite wasmi-benchmarks (public harness benches/criterion/startup.rs, runtimes/toywasm/lib.rs) shows toywasm at x18.35 startup geomean vs WAMR fast-interpreter x56.73 and V8 x33.27 on an AMD EPYC 7763, and below both on all five CPU data sets. C compiler and version are not stated (toywasm is built by the toywasmx-sys cc-crate build script), so not A.
- **Verifier notes:** Numbers verified on the EPYC 7763 geomean-startup plot by y-coordinate, and the all-five-CPUs claim checked (EPYC 18.35 vs V8 33.27; M2 Pro 16.38 vs 16.97; M4 Pro 15.52 vs 21.11; i7-7700 17.59 vs 25.25; Xeon 8573C 10.62 vs 29.21; WAMR fast-interp 43.90-61.71 throughout). Shortcomings to record: startup-only win, execution about 18.7x slower than WAMR fast-interp in the suite, WAMR classic interpreter starts as fast in the author's own data, wrapper written by a competing-runtime author.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
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
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/toywasm/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/toywasm/lib.rs>
  - <https://crates.io/api/v1/crates/toywasmx>
  - <https://raw.githubusercontent.com/wasmi-labs/toywasmx/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/toywasmx/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/toywasmx/HEAD/crates/toywasmx-sys/build.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/toywasmx/HEAD/crates/toywasmx-sys/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/toywasmx/HEAD/crates/toywasmx/Cargo.toml>
  - <https://github.com/yamt/toywasm>
  - <https://github.com/yamt/toywasm/commits/master>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/ffmpeg.txt>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/ffmpeg.md>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/startup.md>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/startup.csv>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/startup.md>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/startup.csv>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/ffmpeg.md>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/benchmark/ffmpeg.txt>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/cmake/ToywasmConfig.cmake>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/lib/platform.h>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/lib/insn.c>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/lib/exec.c>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/lib/exec_context.h>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/lib/toywasm_config.h.in>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/doc/annotations.md>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/yamt/toywasm/HEAD/examples/runwasi/runwasi.c>
  - <https://github.com/yamt/toywasm>
  - <https://github.com/yamt/toywasm/commits/master>
  - <https://github.com/yamt/toywasm/issues>
  - <https://github.com/yamt/toywasm/issues/279>
  - <https://github.com/yamt/toywasm/issues/362>
  - <https://github.com/yamt/toywasm/issues/258>
  - <https://github.com/yamt/toywasm/issues/8>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/benches/criterion/startup.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/toywasm/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/toywasm/lib.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/runtimes/wasmtime/Cargo.toml>
  - <https://github.com/wasmi-labs/wasmi-benchmarks/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/.github/workflows/startup.yml>
  - <https://raw.githubusercontent.com/wasmi-labs/wasmi-benchmarks/HEAD/.github/actions/install-dependencies/action.yml>
  - <https://raw.githubusercontent.com/wasmi-labs/toywasmx/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasmi-labs/toywasmx/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasmi-labs/toywasmx/HEAD/crates/toywasmx-sys/build.rs>
  - <https://raw.githubusercontent.com/wasmi-labs/toywasmx/HEAD/crates/toywasmx-sys/Cargo.toml>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/yamt/toywasm`) · [data/wave12/enrich/raw/github_com_yamt_toywasm.json](../../../data/wave12/enrich/raw/github_com_yamt_toywasm.json) (enrichment confidence 0.72)

</details>
