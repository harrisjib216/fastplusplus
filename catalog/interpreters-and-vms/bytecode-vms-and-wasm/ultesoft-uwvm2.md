# UWVM2 (u2 interpreter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++26 WebAssembly runtime whose 'u2' direct-threaded interpreter reports about 1.7x lower geomean wall time than wasm3 on Apple Silicon.

| | |
|---|---|
| **Beats** | wasm3 |
| **Claimed result** | Wall-time ratio uwvm/wasm3 geomean 0.5957 over n=383 modules (u2 faster on average), median 0.7116; ChaCha20 398ms vs 515ms, SHA512 202ms vs 220ms, BLAKE2s 3094ms vs 3427ms (internal time). |
| **Workload** | Wall time of 383 .wasm modules that both uwvm2's u2 interpreter and wasm3 could run, plus WASI algorithm kernels (ChaCha20, SHA512, BLAKE2s), on AArch64 Apple Silicon. |
| **Metric** | throughput |
| **Hardware** | AArch64 Apple M-series (exact chip not stated) |
| **Adoption** | 14 stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/UlteSoft/uwvm2) · [benchmark](https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/src/uwvm2/runtime/compiler/uwvm_int/readme.md) |

## Verdict

The authors' own February 2026 AArch64 Apple M-series case study (README section 9.1, 'not universal claims') reports a uwvm/wasm3 wall-time ratio with geomean 0.5957 and median 0.7116 over 383 .wasm modules that both engines ran. It also gives internal kernel times of ChaCha20 398 vs 515 ms, SHA512 202 vs 220 ms and BLAKE2s 3094 vs 3427 ms. The exact chip, compiler, flags, wasm3 version and uwvm runtime options are not stated, and the corpus is not published.

## Use it when

- Interpreter-only execution of compute-heavy Wasm (hashing, ciphers, integer loops) on AArch64 or x86-64 SysV hosts, where wasm3 is the current choice and a JIT is not allowed or not wanted
- A command-line WASI P1 runner that has to cover unusual targets (DOS/DJGPP, Windows 9x/NT through MinGW, BSDs, SerenityOS, LoongArch, RISC-V) from one codebase
- A tiered setup where a fast-starting interpreter warms up before an LLVM JIT takes over (the --runtime-tiered mode, which the u2 design targets)
- Hosts with or without virtual memory, using the allocator-based linear-memory backends instead of mmap

## Skip it when

- You need an embeddable library with a stable C API like wasm3's m3_\* or WAMR's wasm_runtime_\*: uwvm2 is built and documented as an executable
- Code size matters: the specialized opfunc tables put the Mach-O __TEXT at about 1.4 MB, and the authors say u2 is not a minimal interpreter in the wasm3/WAMR class
- Memory-heavy or branch-heavy kernels: the authors' own analysis says these can lose to wasm3 because u2's general memory paths lengthen dependence chains
- Your toolchain cannot do full C++26 (Clang &gt;= 21 or GCC &gt;= 16, libstdc++ &gt;= 15 or libc++ &gt;= 21; MSVC is unsupported)
- Modules that need Wasm 2.0/3.0 features, threads or WASI P2: documents/features.md marks them unsupported (only Wasm 1.0 and WASI P1 are ticked), and the 383-module comparison covers only modules both engines ran

## How it is fast

u2 translates each function in a single pass into a direct-threaded stream of opfunc pointers, so no Wasm opcode is decoded at run time. Opfuncs tail-call the next one with musttail and keep hot paths leaf. The top of the operand stack is cached in a 'register ring' passed in ABI argument registers (on AArch64, x3-x7 for i32/i64 and v0-v7 for f32/f64/v128), which cuts operand-stack memory traffic. Translation-time fusion cuts dispatch count: adjacent-op superinstructions ('conbine' soft/heavy/extra), delay_local consumer variants that read locals directly (modelled on wasm3's _rs/_sr/_ss variants), a fused inc/cmp/br_if loop op, deletion of const+drop runs, and frame-less calls to trivial callees.

## Compared with alternatives

Pick u2 over wasm3 or the WAMR fast interpreter when you want a pure interpreter that runs as a CLI on AArch64 or x86-64 SysV, can live with a C++26 toolchain, and want an LLVM tier-up path in the same binary. Stay with wasm3 or WAMR when you need a small, embeddable C library, and look at Silverfir-nano or Wasmi when you want interpreter speed claims backed by an independent suite (wasmi-benchmarks) rather than an unpublished first-party corpus.

## Integration

| | |
|---|---|
| **Form** | CLI executable (uwvm) built with xmake; no documented embedding library API |
| **Dependencies** | Vendored fast_io, boost_unordered and bizwen headers in third-parties/; the default build also enables the LLVM JIT backend, which needs LLVM libraries and statically linked OpenSSL (configure with --execution-jit=none for an interpreter-only build); xmake &gt;= 2.9.8 |
| **Minimum toolchain** | Full ISO C++26: LLVM Clang &gt;= 21 (recommended) or GCC &gt;= 16; libstdc++ &gt;= 15 or libc++ &gt;= 21; MSVC not supported |
| **Platforms** | Over 100 target triples (Linux, Darwin, BSDs, Windows NT/9x via MinGW, clang targeting windows-msvc, DOS, WASI, Emscripten, freestanding). The register-ring cache is only on for AArch64 (5 int + 8 FP slots), x86-64 SysV/GNU (3 + 8), riscv64, loongarch64 and MIPS N32/N64; it is off for ARM32, i386, riscv32, PowerPC and MS-ABI x64 |
| **Thread safety** | Not documented for host use; the Wasm threads proposal is marked unsupported, and a multi-thread allocator memory backend exists |
| **Drop-in for the baseline** | partial — runs the same .wasm/WASI P1 modules as the wasm3 CLI, but has a different command line and no wasm3 C embedding API |

## Gotchas

- A default build compiles in the LLVM JIT, and the default runtime is tiered (interpreter plus lazy LLVM JIT), not u2 alone; pass --runtime-int to run only the interpreter. The case study does not record which uwvm command line or build options produced the wasm3 numbers.
- Release builds default to -march=native (xmake 'march' option), 'fastest' optimisation and LTO, so a default binary is tuned to the build host and may not run on older CPUs; set --march for distributable builds.
- The wasm3 comparison is unreproducible: the 383-module corpus lived in /tmp/uwvm2test, and the cited analysis note test/uwvm2test/u2_vs_wasm3_asm_stitch_analysis.txt still returns 404. The ratio uses wall time (which includes process start and translation) and only modules both engines ran. Translation-time peepholes that delete const+drop runs and inline trivial calls can make microbenchmark modules look better.
- Performance depends on the ABI. The Apple Silicon numbers come from the target with the widest register ring (5 integer + 8 FP slots); MS-ABI x64, ARM32 and i386 run with no stack-top cache at all.

## Known shortcomings

- Geomean 0.5957 against wasm3 (n=383) is verbatim from uwvm_int/readme.md section 9.1, but the corpus (/tmp/uwvm2test) and analysis note are unpublished (404), with no compiler, flags or CPU model; wasm3 is the only baseline.
- Enricher: the default build includes the LLVM JIT and runs tiered mode rather than u2 alone, the case study never states the uwvm flags or wasm3 version, release builds default to -march=native, the register-ring cache is off on MS-ABI x64, ARM32 and i386 (Apple Silicon is the best case), features.md ticks only Wasm 1.0 plus WASI preview 1, and the analysis note and corpus remain unpublished.

## Caveats and trade-offs

First-party section 9.1 of the u2 interpreter README, labelled by the authors as 'not universal claims', from a 2026-02 AArch64/Apple Silicon workflow with no CPU model, compiler or flags stated. The 383-module corpus lives in /tmp/uwvm2test and is not published; the cited analysis note test/uwvm2test/u2_vs_wasm3_asm_stitch_analysis.txt returns 404 and the repo's test/ directory has no uwvm2test folder; benchmark/ only covers parser and utility code. The README says memory-heavy and branch-heavy kernels can lose to wasm3 and that u2 trades code size for speed (not a minimal interpreter in the wasm3/WAMR class). Translation-time peepholes that delete const+drop runs and inline trivial calls could flatter microbenchmark modules in the corpus. Not compared with wasmtime, wasmer or WAMR; wasm3 is the only baseline.

Template-specialized opfuncs trade code size for speed (Mach-O __TEXT about 1.4 MB), so u2 is not a minimal wasm3-class interpreter. C++26 codebase. Tiered interpreter + JIT design; supports many platforms, WASI P1, and mmap or allocator-based linear memory.

## Maintenance

Active but effectively single-maintainer (all recent commits by MacroModel, last on 2026-09-20; 14 stars, 0 open issues); Apache-2.0 and buildable from source, but a dev-stage C++26 codebase and a CLI rather than a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Section 9.1 of the first-party u2 interpreter README gives the wasm3 comparison (geomean 0.5957, median 0.7116 over n=383; ChaCha20, SHA512, BLAKE2s times) with no compiler, flags or exact CPU, and the corpus (/tmp/uwvm2test) and analysis note are not published; the repo's benchmark/ directory covers only the parser and utils (mutex, utf, xxh3) and test/0013.uwvm_int holds correctness tests, so there is no public harness.
- **Verifier notes:** All claimed numbers appear verbatim in src/uwvm2/runtime/compiler/uwvm_int/readme.md section 9.1. Metadata confirmed: Apache-2.0 (LICENSE.md), 14 stars, last commit 2026-09-20 (active), not a fork. Shortcomings: unpublished corpus and analysis note, no compiler/flags/CPU model, wasm3 the only baseline.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/src/uwvm2/runtime/compiler/uwvm_int/readme.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/README.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/LICENSE.md>
  - <https://github.com/UlteSoft/uwvm2>
  - <https://github.com/UlteSoft/uwvm2/commits>
  - <https://github.com/UlteSoft/uwvm2/tree/master/benchmark>
  - <https://github.com/UlteSoft/uwvm2/tree/master/benchmark/0001.utils>
  - <https://github.com/UlteSoft/uwvm2/tree/master/test>
  - <https://github.com/UlteSoft/uwvm2/tree/master/test/0013.uwvm_int>
- **Sources the enricher read:**
  - <https://github.com/UlteSoft/uwvm2>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/README.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/src/uwvm2/runtime/compiler/uwvm_int/readme.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/src/uwvm2/runtime/compiler/readme.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/src/uwvm2/runtime/compiler/uwvm_int/loop_unwind.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/src/uwvm2/runtime/lib/uwvm_runtime.default.cpp>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/test/uwvm2test/u2_vs_wasm3_asm_stitch_analysis.txt>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/documents/features.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/documents/support.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/documents/how-to-build/linux.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/documents/how-to-build/darwin.md>
  - <https://github.com/UlteSoft/uwvm2/tree/master/documents/command-line>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/documents/command-line/runtime.md>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/xmake.lua>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/xmake/impl.lua>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/xmake/rule.lua>
  - <https://raw.githubusercontent.com/UlteSoft/uwvm2/HEAD/xmake/option.lua>
  - <https://github.com/UlteSoft/uwvm2/tree/master/third-parties>
  - <https://github.com/UlteSoft/uwvm2/commits>
  - <https://github.com/UlteSoft/uwvm2/issues?q=is%3Aissue>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/ultesoft/uwvm2`) · [data/wave12/enrich/raw/github_com_ultesoft_uwvm2.json](../../../data/wave12/enrich/raw/github_com_ultesoft_uwvm2.json) (enrichment confidence 0.6)

</details>
