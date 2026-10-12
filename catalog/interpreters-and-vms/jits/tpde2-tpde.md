# TPDE (TPDE-LLVM back-end)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Single-pass baseline back-end framework; its LLVM-IR back-end compiles 10-20x faster than LLVM's -O0 back-end at similar code speed.

| | |
|---|---|
| **Beats** | LLVM -O0 code generation (clang/llc back-end) |
| **Claimed result** | README: TPDE-LLVM compiles 10--20x faster than LLVM -O0 with similar code quality. docs/tpde-llvm/main.md: compile times typically 10--20x faster than the LLVM -O0 back-end with similar execution time; code size \~10-30% larger for -O0 IR and similar for -O1 IR. |
| **Workload** | Compiling LLVM-IR to machine code at -O0 quality with TPDE-LLVM versus LLVM's -O0 back-end. |
| **Metric** | compile-time |
| **Adoption** | 671 stars; used for a Wasmtime back-end and in Umbra per search snippets |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/tpde2/tpde) · [benchmark](https://github.com/tpde2/tpde) |

## Verdict

README and docs/tpde-llvm/main.md state first-party that TPDE-LLVM compiles 10-20x faster than the LLVM -O0 back-end with similar execution time and 10-30% larger code for -O0 IR. Paper snippets only (arXiv 2505.22610 and the CGO 2026 version, both blocked here): SPECint 2017 -O0 IR built with Clang/LLVM 20.1.7, 8-24x faster than LLVM -O0 with geomean 12.15x on x86-64 and 18.96x on AArch64 (Apple M1 under Asahi Linux; x86-64 CPU not seen), run time within about 9%, about 80-85x faster than the LLVM -O1 back-end on -O1 IR, and a Cranelift-IR adapter in Wasmtime compiling 4.27x faster than Cranelift's default mode.

## Use it when

- JIT compilers that already emit LLVM-IR (query engines, language runtimes) where LLVM's -O0 codegen latency dominates time-to-first-execution and baseline code quality is acceptable.
- Debug or unoptimized builds of C, C++ or Fortran on x86-64 or AArch64 Linux where the LLVM back-end stage is a large share of compile time (plugin for Clang/Flang 22+).
- A tier-0 or baseline tier for your own SSA IR: implement an IRAdaptor and instruction selection instead of lowering to LLVM-IR first.
- Clang -O0 or -O1 generated IR: the docs say this typically compiles; on -O1 IR code size is similar to LLVM's.

## Skip it when

- You need optimized code: TPDE produces -O0-quality machine code by design, and the docs say an optimizing back-end is not its goal.
- Targets beyond ELF x86-64-v1 and AArch64 Armv8.1 Linux with the small PIC code model: no Windows/COFF, no macOS/Mach-O, no RISC-V.
- Vector-heavy IR (Clang -O2 and higher output typically fails on unsupported vector operations and falls back to LLVM); shufflevector is always scalarized and many vector intrinsics are missing.
- IR using computed goto, IFuncs, non-empty inline assembly, non-C calling conventions, half/bfloat, or integers wider than i128.
- Whole-build speedups are the goal: the 10-20x covers only the back-end stage, so Clang front-end parsing and linking are unchanged and end-to-end gains are smaller (not quantified in the repo).

## How it is fast

One analysis pass computes block layout (mostly reverse post-order) and per-value live intervals with reference counts, then a single pass over the IR does instruction selection, register allocation and machine-code encoding together, with no intermediate Machine IR and no separate register-allocation pass. Values are freed from registers and stack slots as soon as their reference count reaches zero. Instruction-selection code is largely generated offline by TPDE-Encodegen, which compiles small C 'snippet' functions through LLVM and turns the resulting machine code into encoder functions for x86-64 and AArch64.

## Compared with alternatives

Pick TPDE when your system already produces LLVM-IR (or another SSA IR) and you want a far faster -O0-quality back-end that emits standard ELF objects and falls back to LLVM on unsupported input; copy-and-patch designs like PochiVM or WasmNow can be faster still but need you to build stencils for your own language or Wasm, and AsmJit or sljit make you write instruction selection and register handling yourself.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | LLVM/Clang 19.1-23.1 for TPDE-LLVM and TPDE-Encodegen (prefer 21.1; the LLVM version must match Clang/Flang when used as a plugin); Python 3.10+; other dependencies bundled as git submodules; core framework builds without LLVM |
| **Minimum toolchain** | GNU-compatible C++20 compiler (Clang 19+, GCC 14+); CMake |
| **Platforms** | x86-64 (x86-64-v1) and AArch64 (Armv8.1) Linux ELF only |
| **Thread safety** | not documented (LLVMCompiler is non-copyable and compilation modifies the module; use one compiler instance per thread) |
| **Drop-in for the baseline** | partial: through the Clang/Flang 22+ plugin (-fpass-plugin=tpde-plugin.so) it replaces the LLVM back-end with no code changes and falls back to LLVM on unsupported input, but most LLVM code-generation options are ignored and only Linux ELF targets work |

## Gotchas

- Compilation modifies the input module: constant expressions inside functions are expanded into instructions and thread-local accesses are rewritten to llvm.threadlocal.address.
- The built-in JIT mapper supports only typical ELF constructs (no TLS); for more, map the object through LLVM ORC (see tpde-llvm/tools/tpde-lli.cpp). An OrcJIT emission-layer segfault (issue #26) and a wrong RIP-relative string offset with -ftpde on LLVM 20.1.8 (issue #39, garbage output) were reported and closed in 2026; a register-allocation fatal error on llvm.smul.with.overflow.i128 (issue #45) is still open.
- Atomics may use stronger ordering than requested (atomicrmw is always seq_cst), x86_fp80 is slow and mostly unsupported, and non-ABI vector types have an in-register layout incompatible with LLVM, so they cannot cross function boundaries.
- The repo carries no benchmark scripts or results; every number comes from the paper (SPEC CPU 2017, proprietary) that this session could reach only through search snippets, so the speedups cannot be re-run from public code.

## Known shortcomings

- The 10-20x compile-time win is against LLVM -O0 only, with -O0-level code quality; TPDE handles an LLVM-IR subset with fallback to LLVM, and the SPEC numbers are not reproducible from the repo. CGO 2026 paper and Zenodo artifact were snippet only (arXiv and TUM hosts blocked); retier candidate once the paper is reachable.
- Enricher: no benchmark code in the repo and the CGO 2026 paper remained blocked; snippets give Clang/LLVM 20.1.7 and AArch64 on an Apple M1 under Asahi Linux with no x86 CPU seen. The speedup covers the back-end stage only; Clang/Flang 22+ use the -fpass-plugin route with no patch (the patch is for 19-21); issue #45 (register-allocator fatal error) open, #39 (wrong RIP offset with -ftpde) closed.

## Caveats and trade-offs

Compile-time win only; generated code is -O0 quality, not comparable to V8 TurboFan, HotSpot C2 or LLVM -O2. TPDE-LLVM supports a subset of LLVM-IR (x86-64-v1 and AArch64 Armv8.1 ELF only; Clang -O2 and higher IR typically fails on unsupported vector operations and falls back to the full LLVM back-end); code size 10-30% larger for -O0 IR. The README cites only the arXiv preprint 2505.22610; the peer-reviewed version is CGO 2026 (Schwarz, Kamm, Engelke) with an artifact on Zenodo (record 17619677) running SPEC CPU 2017, which is proprietary, so the evaluation is not fully reproducible. Paper numbers are snippet only and differ by version: arXiv snippet says 8-24x faster than LLVM -O0 on SPEC CPU 2017 with geomean 12.15x (x86-64) and 18.96x (AArch64) and run time within +-9%; the CGO snippet says 8-26x, geomean 16.2x/18.7x over -O0 and 85.8x/80.0x over -O1. The search agent's Wasmtime/Cranelift figures (4.27x faster compile than Cranelift, Cranelift code 1.64x faster) were not re-checked.

Single-pass back-end aimed at -O0 quality baseline code, not optimized code. Targets ELF-based x86-64 and AArch64 (Armv8.1) only. Usable as library for JIT, as tpde-llc tool, or in Clang/Flang 22+ with a patch. Needs LLVM-IR (or another SSA IR through its adapters).

## Maintenance

Active (1,124 commits, last on 2026-09-22 adding LLVM 23/24 adjustments, 3 open issues); Apache-2.0 WITH LLVM-exception and usable today as a Clang/Flang 22+ plugin or library, but it supports only a subset of LLVM-IR and the authors have not answered the open 'ready for production use?' issue (#6).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** The README and docs/tpde-llvm/main.md state the 10-20x compile-time win over the LLVM -O0 back-end (first-party, no methodology), and the evaluation is in a peer-reviewed CGO 2026 paper with a Zenodo artifact (SPEC CPU 2017, x86-64 and AArch64 images); the paper, artifact and CGO page were seen only through search snippets (arxiv.org, home.cit.tum.de, 2026.cgo.org, discourse.llvm.org blocked), and SPEC is proprietary with hardware and flags unseen, so not A.
- **Verifier notes:** Record accurate; README and docs carry the 10-20x figure, paper only via snippets (blocked hosts), so B rests on the CGO 2026 acceptance and Zenodo artifact seen in search results. Shortcomings: -O0 code quality only, LLVM-IR subset with fallback, SPEC-based evaluation not reproducible, paper not opened. Candidate for a paper-access retier check (arXiv 2505.22610 or home.cit.tum.de/\~engelke/pubs/2602-cgo1.pdf).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/README.md>
  - <https://github.com/tpde2/tpde>
  - <https://github.com/tpde2/tpde/commits>
  - <https://github.com/tpde2>
  - <https://github.com/tpde2/tpde/tree/master/docs>
  - <https://github.com/tpde2/tpde/tree/master/docs/tpde-llvm>
  - <https://github.com/tpde2/tpde/tree/master/utils>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/docs/tpde-llvm/main.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/docs/main.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/README.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/docs/main.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/docs/tpde-llvm/main.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/docs/tpde/overview.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/docs/tpde/main.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/docs/tpde/guide.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/docs/tpde/adaptor.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/tpde-llvm/include/tpde-llvm/LLVMCompiler.hpp>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/tpde-llvm/tools/tpde-llc.cpp>
  - <https://github.com/tpde2/tpde>
  - <https://github.com/tpde2/tpde/tree/master/docs>
  - <https://github.com/tpde2/tpde/tree/master/docs/tpde>
  - <https://github.com/tpde2/tpde/tree/master/utils>
  - <https://github.com/tpde2/tpde/tree/master/tpde-llvm/tools>
  - <https://github.com/tpde2/tpde/commits/master>
  - <https://github.com/tpde2/tpde/issues?q=is%3Aissue>
  - <https://github.com/tpde2/tpde/issues/4>
  - <https://github.com/tpde2/tpde/issues/6>
  - <https://github.com/tpde2/tpde/issues/10>
  - <https://github.com/tpde2/tpde/issues/39>
  - <https://github.com/buster14a/buster/issues/2632>
  - https://arxiv.org/abs/2505.22610 (EGRESS_BLOCKED)
  - https://ar5iv.labs.arxiv.org/html/2505.22610 (EGRESS_BLOCKED)
  - https://home.cit.tum.de/\~engelke/pubs/2602-cgo1.pdf (EGRESS_BLOCKED)
  - https://llvm.org/devmtg/2024-03/slides/llvm-fast-backend.pdf (EGRESS_BLOCKED)
  - https://pith.science/paper/2505.22610 (EGRESS_BLOCKED)
  - WebSearch snippets for arxiv.org/pdf/2505.22610, home.cit.tum.de/\~engelke/pubs/2602-cgo1.pdf and zenodo.org/records/17619677
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/tpde2/tpde`) · [data/wave12/enrich/raw/github_com_tpde2_tpde.json](../../../data/wave12/enrich/raw/github_com_tpde2_tpde.json) (enrichment confidence 0.7)

</details>
