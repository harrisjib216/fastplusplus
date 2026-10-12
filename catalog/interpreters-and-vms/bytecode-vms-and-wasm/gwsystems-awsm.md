# aWsm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Research ahead-of-time Wasm-to-LLVM compiler plus a tiny C runtime; its 2020 PolyBench/C slowdown over native C was 13.4%, against WAVM 28.1% and Wasmer 149.8%.

| | |
|---|---|
| **Beats** | Wasmer; WAVM; Lucet; Node.js with Emscripten; wasm3 on microcontrollers |
| **Claimed result** | x86-64 average slowdown over native: Wasmer 149.8%, WAVM 28.1%, Node.js + Emscripten 84.0%, Lucet 92.8%, aWsm 13.4%. aarch64: aWsm 6.7%. Cortex-M7 40.2% and M4 24.9%, versus 'more than 10x' for the wasm3 interpreter on microcontrollers (links wasm3's Performance.md). |
| **Workload** | PolyBench/C slowdown over native C, on x86-64, aarch64 (Raspberry Pi) and Cortex-M4/M7, for an ahead-of-time Wasm-to-LLVM compiler with a small C runtime. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the cross-runtime comparison. The repo's code_benches/run.py (native vs aWsm only) builds native code with clang -O3 and Wasm with wasi-sdk/wasmception clang -O3 -flto, then compiles aWsm's LLVM bitcode with clang -O3. |
| **Adoption** | 353 stars |
| **Last commit** | 2026-07-13 |
| **Links** | [repository](https://github.com/gwsystems/aWsm) · [benchmark](https://github.com/gwsystems/aWsm/blob/HEAD/README.md) |

## Verdict

First-party, May 2020: on x86-64, aWsm's mean PolyBench/C slowdown over native C was 13.4% (standard deviation 34.65 points), against WAVM 28.1%, Node.js+Emscripten 84.0%, Lucet 92.8% and Wasmer 149.8%; on aarch64 (Raspberry Pi) it was 6.7%, and on Cortex-M7/M4 it was 40.2%/24.9%. The 2020 comparator versions (Wasmer 0.12.0, Lucet 0.4.1) and the 24-of-30-kernels-within-1.1x figure come from the Middleware 2020 Sledge paper, seen in search snippets only. The README states no CPU, compiler version or aWsm bounds-check mode. The repo's run.py compares only native against aWsm variants, both built with clang -O3 -flto -g.

## Use it when

- Sandboxing compute-bound C/C++ compiled to Wasm (MVP feature set) inside a native program, where AOT compile time at build is fine and you want speed close to native.
- Arm Cortex-M firmware that needs software-isolated components: on an nRF52840 (Cortex-M4), Arm's bento-linker measured aWsm at 78,896 ns against 132,688 ns for WAMR AOT and 2,079,359 ns for wasm3 on qsort, with code size close to native (5,280 B vs 5,228 B).
- Research on bounds-checking strategies: swapping one runtime C file changes the isolation mechanism, and the compiler is under 3.5K lines of Rust.
- Builds that want plain ELF objects to link statically rather than a runtime that loads modules at run time.

## Skip it when

- Anything that needs post-MVP Wasm: SIMD, threads, multi-value (issue #72), f32/f64 globals (issue #102) and other roadmap features are unsupported, and wasmparser is pinned at 0.58 (2020). The README says not every Wasm instruction is implemented.
- Running untrusted or third-party Wasm in production: the Wasm spec test suite is not run (issue #46), and issue #56 (open since 2021) reports invalid LLVM bitcode at -O1/-O2/-O3 and wrong output at -O0 for modules that run correctly on Wasmtime.
- Workloads that need fast download-to-run latency, such as JIT or interpreter use cases; the README says the AOT design is not a fit there.
- Teams that need a supported toolchain: pinned to Rust 1.56.0, LLVM 13, wasi-sdk 12 and a forked llvm-rs branch. The README calls it a research prototype that is 'not currently turn-key'.
- Hosts that run many instances in one process with the stock runtime: linear memory, its size and the indirect table are process globals. Sledge supplies its own multi-sandbox runtime.

## How it is fast

Every Wasm load and store becomes a call to a small always_inline C stub (get_i32, set_f64 and so on), and indirect calls go through a C table check; LLVM LTO inlines these into the generated code, so the guest gets the full clang -O3 pipeline. Bounds checks are a link-time choice among memory/\*.c files: on 64-bit Unix (64bit_nix.c) the runtime reserves 4 GiB plus one 64 KiB guard page as PROT_NONE, so loads and stores carry no check and stray accesses fault. Other files do explicit compare-and-assert checks (generic.c), Intel MPX, x86-32 segmentation, Cortex-M MPU or wrap-around masking, or no protection at all.

## Compared with alternatives

Pick aWsm over WAMR (AOT) or wasm3 for Cortex-M firmware where code size and speed close to native matter: the bento-linker run shows aWsm at 1.7x to 2.9x WAMR AOT speed and 4.4x to 26x wasm3 on qsort, mandelbrot and maze (derived from page data). On servers, the actively maintained source-translation siblings wasm2c (WABT) and w2c2 take a similar Wasm-to-native-compiler route with far broader feature support. LFI is the better sibling if you need SPEC-scale programs at single-digit overhead.

## Integration

| | |
|---|---|
| **Form** | Rust CLI compiler (cargo build) plus a C runtime source-drop compiled and LTO-linked with the generated bitcode |
| **Dependencies** | LLVM/clang 13 with libc++ (llvm-alt from the gwsystems/llvm-rs 'sfbase' branch), wasmparser 0.58, a Wasm C toolchain (wasi-sdk 12 or the wasmception submodule), and libuv plus uvwasi for the WASI backing |
| **Minimum toolchain** | Rust 1.56.0 (pinned by install_deb.sh), LLVM 13, wasi-sdk 12 |
| **Platforms** | x86-64, x86-32, aarch64 and Thumb (Cortex-M4/M7); the hosted pipeline (run.py) supports Linux and macOS |
| **Thread safety** | Not documented. The stock runtime keeps linear memory, memory_size, runtime_heap_base and the indirect table in process-wide globals, so it supports one sandbox instance per process. |
| **Drop-in for the baseline** | no |

## Gotchas

- On Linux and macOS, awsm_assert is plain assert(). Building the runtime with -DNDEBUG, the usual release flag, silently removes the explicit bounds checks (generic.c), the indirect-call type checks and other runtime checks. Only the 64bit_nix.c guard-page mode keeps memory isolation without them.
- The effective address is computed as a 32-bit add of base and the static offset (load_val/store_val in src/codegen/block.rs), so base+offset at or above 2^32 wraps to low memory instead of trapping as the spec requires. The access stays inside the sandbox, but faulting programs behave differently than on spec-conforming runtimes.
- Harness flaw in the repo's own benchmark (code_benches/run.py): it times whole process runs (minimum of 10), sends stdout and stderr to /dev/null and never checks results. A miscompile like issue #56 would be timed without being noticed. It also builds several variants (no protection, -u fast-unsafe float truncation, MPX, guard pages), and the README tables do not say which one produced 13.4%.
- The cross-runtime table (Wasmer, WAVM, Lucet, Node.js) cannot be reproduced from the repo: there is no harness for the other runtimes, and the README gives no CPU, compiler versions or aWsm memory mode. Arm's bento-linker notes that its aWsm runtime isolates only 'as long as you can ensure the binary has not been tampered'.

## Known shortcomings

- README table from May 2020 with no methodology: the comparator harness is not public and there is no wasmtime row; the Sledge paper that may hold versions was snippet only (gwu and nsf hosts blocked), so a paper-access retier to B is possible. bento-linker nRF52840 numbers against WAMR AOT and wasm3 added to caveats.
- Enricher: code_benches/run.py sends output to /dev/null and never checks it, while open issue #56 reports invalid bitcode at -O1 to -O3 and wrong output at -O0, so miscompiles would be timed unnoticed; the runtime's awsm_assert is assert(), so -DNDEBUG strips bounds and indirect-call checks, and the base+offset add wraps at 32 bits without trapping (not spec). 2020 first-party numbers with no CPU, versions or bounds-check mode; MVP only, Rust 1.56 and LLVM 13. bento-linker ratio against wasm3 corrected to 4.4x-26x.

## Caveats and trade-offs

README says 'these numbers are from May 2020'; hardware, compiler versions and flags are not given in the README. A search snippet (snippet only) says the Middleware 2020 Sledge paper holds the same x86-64 comparison with Wasmer v0.12.0, WAVM v0.0.0-prerelease and Lucet v0.4.1, and that aWsm is within 1.1x of native on 24 of 30 PolyBench/C kernels; the paper itself was not reachable (a paper-access retier could move this to B). Wasmtime is absent from the x86-64 table, and all comparator versions are 2020-era. Microcontroller support: Arm's bento-linker README (an Arm collaborator of the aWsm group) measures aWsm on an nRF52840 (Cortex-M4, arm-none-eabi-gcc -Os -flto -mcpu=cortex-m4, compiler version not stated) at 78,896 ns vs 132,688 ns for WAMR AOT and 2,079,359 ns for wasm3 on qsort, and 6,823,538 ns vs 12,368,716 ns (WAMR AOT) and 157,946,032 ns (wasm3) on maze. Rust compiler plus C runtime: only the generated objects and runtime are linked into C/C++ programs. The 2026-07-13 last commit is a submodule bump; the previous code change was 2025-11-19 and the README pins Rust 1.56.0, so development is slow.

Ahead-of-time compiler through LLVM, so compile latency; the runtime is under 5K lines of C and the compiler under 3.5K lines of Rust; output is ELF objects; seven selectable memory-bounds-check mechanisms. Not a fit where interpreters or JIT are required.

## Maintenance

Slow, single-maintainer upkeep driven by the Sledge project: one or two commits a year since 2024 (the last code change on 2025-11-19 added a Makefile .so build, and the 2026-07-13 commit is a submodule bump), on Rust 1.56/LLVM 13. It is BSD-3-Clause and small enough to vendor, but it is a research prototype with 24 open issues, including an unresolved miscompile report.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section carries the quoted PolyBench/C slowdown table (Wasmer 149.8%, WAVM 28.1%, Node.js+Emscripten 84.0%, Lucet 92.8%, aWsm 13.4%) with no hardware, versions or flags; the repo's code_benches/run.py only compares native against aWsm variants, and the peer-reviewed Sledge (Middleware 2020) and eWASM (EMSOFT 2020) papers holding the methodology are unreachable here (www2.seas.gwu.edu and par.nsf.gov EGRESS_BLOCKED), so first-party C.
- **Verifier notes:** README numbers match exactly; repo 353 stars, BSD-3-Clause, not a fork, last commit 2026-07-13 (submodule bump). Shortcomings: 2020-era first-party numbers without methodology in the repo, no Wasmtime row, comparator harness not public; peer-reviewed paper blocked here.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/gwsystems/aWsm/blob/HEAD/README.md>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/README.md>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/LICENSE>
  - <https://github.com/gwsystems/aWsm>
  - <https://github.com/gwsystems/aWsm/commits/master>
  - <https://github.com/gwsystems/aWsm/tree/master>
  - <https://github.com/gwsystems/aWsm/tree/master/code_benches>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/master/code_benches/run.py>
  - <https://raw.githubusercontent.com/arm-software/bento-linker/HEAD/README.md>
  - <https://github.com/ARM-software/bento-linker/tree/master/examples>
  - <https://raw.githubusercontent.com/ARM-software/bento-linker/master/examples/awsm-qsort/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/README.md>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/doc/design.md>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/code_benches/run.py>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/install_deb.sh>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/runtime/memory/64bit_nix.c>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/runtime/memory/generic.c>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/runtime/memory/no_protection.c>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/runtime/wasm_instructions/memory/64bit_nix.c>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/runtime/runtime.c>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/runtime/runtime.h>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/src/codegen/function.rs>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/src/codegen/block.rs>
  - <https://raw.githubusercontent.com/gwsystems/aWsm/HEAD/src/codegen/memory.rs>
  - <https://github.com/gwsystems/aWsm/tree/master/runtime/memory>
  - <https://github.com/gwsystems/aWsm/tree/master/src>
  - <https://github.com/gwsystems/aWsm/tree/master/src/codegen>
  - <https://github.com/gwsystems/aWsm/issues>
  - <https://github.com/gwsystems/aWsm/issues/99>
  - <https://github.com/gwsystems/aWsm/issues/56>
  - <https://github.com/gwsystems/aWsm/commits/master>
  - <https://raw.githubusercontent.com/arm-software/bento-linker/HEAD/README.md>
  - https://www.jahrhundert.net/papers/sledge-awsm-CR-MW2020.pdf (EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/gwsystems/awsm`) · [data/wave12/enrich/raw/github_com_gwsystems_awsm.json](../../../data/wave12/enrich/raw/github_com_gwsystems_awsm.json) (enrichment confidence 0.65)

</details>
