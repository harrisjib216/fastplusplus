# WasmNow (copy-and-patch WebAssembly baseline compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Research copy-and-patch WebAssembly baseline JIT; OOPSLA 2021 paper: 4.9-6.5x faster compiles, 39-63% faster code than V8 Liftoff.

| | |
|---|---|
| **Beats** | Google Chrome (V8) Liftoff baseline WebAssembly compiler; also Wasmer Singlepass named in README |
| **Claimed result** | Versus Chrome's Liftoff: on Coremark compiles 5x faster while generating 39% faster code; on PolyBenchC compiles 6.5x faster while generating 63% faster code (README). |
| **Workload** | Coremark and PolyBenchC compiled to WebAssembly: compile time and generated-code speed versus Liftoff. |
| **Metric** | compile-time |
| **Hardware** | Intel Core i7-7700HQ 2.80 GHz (single CPU), from the OOPSLA 2021 paper |
| **Compiler and flags** | clang++ 10.0.0 (LLVM 10.0.0 release binaries installed in dockerfile/Dockerfile on Ubuntu 18.04); production flavor adds -O3 -DNDEBUG, plus -pthread -mavx2 (CMakeLists.txt); built via pochivm-build cmake/make production. Liftoff/Chrome version and flags not stated in the repo. |
| **Adoption** | 63 stars |
| **Last commit** | 2021-10-23 |
| **Links** | [repository](https://github.com/sillycross/WasmNow) · [benchmark](https://github.com/sillycross/WasmNow) |

## Verdict

OOPSLA 2021 paper (opened from the author's sillycross.github.io repository via raw.githubusercontent.com): on an Intel i7-7700HQ at 2.80 GHz (turbo on, Ubuntu 20.04, 32 GB), all compilers limited to one CPU, at least 30 runs with CI95 under 2%, copy-and-patch compiles 4.9-6.5x faster than Chrome 81's Liftoff (timed as new WebAssembly.Module after the bytes are in memory) and 12.7-18.5x faster than Wasmer 1.0 SinglePass across Coremark, PolyBenchC, AutoCAD and clang.wasm; its code runs 39% faster than Liftoff's on 10,000 Coremark iterations and 63% faster on average across the 30 PolyBenchC kernels. WasmNow was built with clang++ 10 at -O3 -mavx2.

## Use it when

- Studying or reproducing copy-and-patch: a compact, working reference for building a stencil-based baseline tier for a stack bytecode.
- Benchmarking a new Wasm baseline compiler against a published, peer-reviewed data point (Coremark, PolyBenchC, AutoCAD and clang.wasm on x86-64).
- Running trusted, compute-only WebAssembly 1.0 modules (no SIMD, threads or newer proposals) on x86-64 Linux with AVX2 where startup latency matters more than peak speed, accepting research-grade code.
- Borrowing the stencil-library build pipeline for your own JIT; the same technique was later adopted by CPython's JIT (separate catalogue entry).

## Skip it when

- Any untrusted WebAssembly: the README says outright not to, the code has had no auditing or fuzzing, the parser skips validation, and the code region is mapped read-write-execute at once.
- Production embedding: there is no embedding API, no CLI for arbitrary modules, only partial WASI (other modules hit 'WASI import not implemented'), and the project has been abandoned since 2021 (4 commits).
- Platforms other than x86-64 Linux: memory access uses arch_prctl(ARCH_SET_GS), the build adds -mavx2, and builds run only through the provided Docker image.
- Peak-throughput workloads: it is a baseline tier only, with no optimizing tier or tier-up. The paper puts it at Wasmer Cranelift's level (2.6% slower on Coremark, 4.6% faster on PolyBenchC), below TurboFan/LLVM-class output.
- Modules using post-1.0 features (SIMD, threads, reference types, multi-memory): only the 1.0 core spec is implemented.

## How it is fast

Copy-and-patch: at build time clang compiles templated C++ stencil generators into object code for every variant of each opcode (how many int/float operands are already in registers, whether the result spills), and the MetaVar tool turns the relocation records into patchable 'holes' in a stencil library. At compile time WasmEmitStencil looks up the stencil for (opcode, in-register counts, spill flag), memcpys its bytes and patches a few constants and offsets, with no instruction selection or encoding, so most opcodes cost a table lookup plus a memcpy. Stencils use the GHC calling convention so the top of the Wasm operand stack stays in registers (light register allocation) and tail jumps become fallthroughs, which is why the output also beats Liftoff's code; linear memory is addressed through the x86 GS segment base inside a 4 GiB reservation.

## Compared with alternatives

Pick WasmNow over WARP or V8 Liftoff only to study or reproduce copy-and-patch on WebAssembly; to run real Wasm use a production engine or WARP, and for a maintained fast baseline back-end for your own IR look at TPDE (LLVM IR, 10-20x faster than -O0) or the CPython copy-and-patch JIT. PochiVM is the same author's sibling, applying the technique to a C++ metaprogramming AST instead of Wasm bytecode.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | LLVM/Clang 10.0.0 (stencil generation and PochiVM's LLVM backend are linked into the binary), Docker (Ubuntu 18.04 build image), CMake + Ninja, ccache (CMake aborts with 'ccache not found!' without it), bundled googletest |
| **Minimum toolchain** | C++17, clang++ 10.0.0 (pinned in dockerfile/Dockerfile), CMake 3.10 |
| **Platforms** | x86-64 Linux only, AVX2 required (-mavx2) |
| **Thread safety** | not documented; compilation is single-threaded and the linear-memory base lives in the per-thread GS register (SetGs before running), so one running instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (compile-time comparison): WasmNow's timed ParseModule never validates the module (its readers say they assume 'the module has passed validation' and the checks are assert() calls, compiled out by -DNDEBUG in the production build), while the paper times Liftoff as `new WebAssembly.Module(data)`, which per the WebAssembly JS API must validate before compiling and also builds JS objects. The paper does not mention this asymmetry, so part of the 4.9-6.5x compile-time gap may come from skipped validation rather than from copy-and-patch.
- Coremark and PolyBenchC modules hold only about 30 kB of code (0.6 ms to compile, 0.2 ms of it memory-manager setup per the paper), so those ratios rest on sub-millisecond timings; the in-repo BenchmarkAll averages only 5 runs and times WasmNow alone. Neither the Liftoff JS harness nor the exact Chrome flags are published.
- The code buffer is mmap'd PROT_READ|PROT_WRITE|PROT_EXEC (no W^X), and malformed input is undefined behaviour because validation is skipped.
- The build sets -Weverything -Werror and requires the pinned clang 10 Docker image; a newer compiler is likely to fail on new warnings. The README says the license is MIT, but no LICENSE file appears at the repo top level.

## Known shortcomings

- Research prototype abandoned in 2021: the Liftoff side of the comparison and the CPU model are not in the repo (OOPSLA 2021 paper snippet only), WASI support is partial and the README carries a security warning.
- Enricher: the OOPSLA 2021 paper (PDF in the sillycross.github.io repo: i7-7700HQ 2.80 GHz, Chrome 81 Liftoff, Wasmer 1.0, single CPU, 30+ runs) was opened; tier stays B because the Liftoff JS harness and Chrome flags are unpublished. Harness flaw: the timed ParseModule skips validation (the parser assumes a validated module, checks are assert() only and compiled out by -DNDEBUG) while Liftoff is timed through new WebAssembly.Module, which must validate, so the 4.9-6.5x compile gap may be partly skipped validation. RWX code region; no CLI or API (PR #1 unmerged since 2023).

## Caveats and trade-offs

Peer-reviewed support is the OOPSLA 2021 paper 'Copy-and-Patch Compilation' (Xu and Kjolstad, Distinguished Paper Award); its abstract per search snippet gives 4.9x-6.5x faster compilation and 39%-63% faster generated code than Liftoff on Coremark and PolyBenchC, matching the README; the PDF was not opened (fredrikbk.com, sillycross.github.io, arXiv blocked; no copy in the sillycross.github.io repo). The repo benchmark harness (test_parser.cpp) measures WasmNow only; Liftoff measurements and the CPU model are not in the repo. Beats Liftoff, a baseline tier, not V8's optimizing TurboFan. Research prototype: 4 commits, last in Oct 2021; WebAssembly 1.0 core only with partial WASI (runs Coremark and PolyBenchC, other modules may hit unimplemented imports); requires AVX2 (-mavx2); the author warns not to run untrusted WebAssembly with it (unaudited JIT, sandbox-escape risk). [retier] Research prototype abandoned in 2021: partial WASI, README security warning, RWX code region, no CLI or API (PR #1 unmerged since 2023). Paper setup (OOPSLA 2021, PDF in the sillycross.github.io repo): Chrome 81 Liftoff and Wasmer 1.0 as baselines, 30+ runs, single CPU; the Liftoff JS harness and Chrome flags are not published. The timed ParseModule skips validation (the parser assumes a validated module, its checks are assert() only and compiled out by -DNDEBUG) while Liftoff is timed through new WebAssembly.Module, which must validate per the JS API, so part of the 4.9-6.5x compile-time gap may be skipped validation.

Research-grade proof of concept: README warns not to run untrusted WebAssembly with it. Only WebAssembly 1.0 core, partial WASI, Linux plus docker only, dead code left over from PochiVM. Only a baseline tier; no optimizing tier.

## Maintenance

Abandoned research prototype (4 commits, last October 2021, author says no plan to fix WASI gaps); MIT per README and readable as a reference implementation, but not for running untrusted code or embedding without substantial work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** README numbers (Coremark 5x faster compile and 39% faster code, PolyBenchC 6.5x and 63% versus Chrome's Liftoff) match the peer-reviewed OOPSLA 2021 copy-and-patch paper (Distinguished Paper), whose abstract per search snippet reports 4.9x-6.5x faster compilation and 39%-63% faster code than Liftoff. Not A: the repo's harness (test_parser.cpp: WasmCompilation.BenchmarkAll, WasmExecution.CoremarkWasiBenchmark, PolyBenchC_\*) times only WasmNow, the Liftoff side (Chrome version, flags) is not in the repo, and no CPU model is stated; the paper PDF was not opened.
- **Verifier notes:** Record accurate; claims match README and the paper abstract (snippet). Shortcomings: Liftoff side not reproducible from the repo, no CPU model, abandoned 2021 research prototype with partial WASI and an explicit security warning, beats only the baseline tier. Copy-and-patch technique later adopted by CPython's JIT (separate entry).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `hardware`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/README.md>
  - <https://github.com/sillycross/WasmNow>
  - <https://github.com/sillycross/WasmNow/commits>
  - <https://github.com/sillycross/WasmNow/tree/main>
  - <https://github.com/sillycross/WasmNow/tree/main/dockerfile>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/test_parser.cpp>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/dockerfile/Dockerfile>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/pochivm-build>
  - <https://github.com/sillycross/sillycross.github.io>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/README.md>
  - <https://github.com/sillycross/WasmNow>
  - <https://github.com/sillycross/WasmNow/tree/main/wasm_inputs>
  - <https://github.com/sillycross/WasmNow/pulls>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/test_parser.cpp>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/dockerfile/Dockerfile>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/pochivm-build>
  - <https://raw.githubusercontent.com/sillycross/WasmNow/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sillycross/sillycross.github.io/master/assets/copy-and-patch.pdf>
  - <https://raw.githubusercontent.com/WebAssembly/spec/main/document/js-api/index.bs>
  - https://ar5iv.labs.arxiv.org/html/2011.13127 (EGRESS_BLOCKED)
  - https://developer.mozilla.org/en-US/docs/WebAssembly/Reference/JavaScript_interface/Module/Module (EGRESS_BLOCKED)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/sillycross/wasmnow`) · [data/wave12/enrich/raw/github_com_sillycross_wasmnow.json](../../../data/wave12/enrich/raw/github_com_sillycross_wasmnow.json) (enrichment confidence 0.85)

</details>
