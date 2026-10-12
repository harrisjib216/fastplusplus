# Cranelift code generator (Bytecode Alliance Wasmtime)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> Cranelift, Wasmtime's Rust code generator: in a 2021 paper it compiled WebAssembly 7-10x faster than LLVM-based WAVM, with code about 14% slower.

| | |
|---|---|
| **Beats** | V8 (TurboFan) for generated-code speed; WAVM (LLVM-based Wasm engine) for compile speed |
| **Claimed result** | README (citing the paper's Fig. 22): generated code about 2% slower than V8 TurboFan and about 14% slower than WAVM (LLVM); compilation about an order of magnitude faster than WAVM. Paper figures, read from the bar charts (approximate): PolyBenchC average execution time normalized to copy-and-patch 0.70 for Wasmtime Cranelift, 0.69 for V8 TurboFan and 0.61 for WAVM (Fig. 22); startup delay normalized to copy-and-patch about 105-110 for Wasmtime Cranelift against about 800-1150 for WAVM on CoreMark, PolyBenchC and clang.wasm, so roughly 7-10x faster compilation than LLVM (derived from page data), while V8 TurboFan compiled faster than Cranelift on CoreMark, PolyBenchC and clang.wasm (about 45-88) and tied on AutoCAD (Fig. 18); CoreMark 10000 iterations about 0.59 s for Wasmtime Cranelift, 0.94 s for TurboFan and 0.43 s for WAVM (Fig. 20). |
| **Workload** | CoreMark 1.0 and the 30 PolyBenchC 4.2.1 kernels compiled to WebAssembly (execution time and startup delay), plus the AutoCAD (47.5 MB) and clang.wasm (30.5 MB) modules for code-generation time only; compilation limited to one CPU for every engine; Wasmtime 0.26 Cranelift against Chrome 81 V8 TurboFan, Wasmer 1.0 and WAVM (Figs. 17-22 of the paper). |
| **Metric** | compile-time |
| **Hardware** | Intel Core i7-7700HQ at 2.80 GHz, turbo on, 8 logical cores, 32 GB RAM, Ubuntu 20.04 |
| **Compiler and flags** | Wasmtime 0.26 (Cranelift), Chrome 81 V8 (TurboFan selected with browser developer flags), Wasmer 1.0, WAVM (version not given); compilation single-threaded; the flags used to build the Wasm benchmark modules are not stated in the methodology section |
| **Adoption** | 18.7k stars (wasmtime repository); crate cranelift-codegen has about 51.6M downloads on crates.io; used in production inside Wasmtime |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/bytecodealliance/wasmtime) · [benchmark](https://raw.githubusercontent.com/sillycross/sillycross.github.io/master/assets/copy-and-patch.pdf) |

## Verdict

Xu and Kjolstad's OOPSLA 2021 paper (Intel i7-7700HQ at 2.8 GHz with turbo, Ubuntu 20.04, compilation pinned to one CPU) measured Wasmtime 0.26 Cranelift against Chrome 81 V8 TurboFan, Wasmer 1.0 and WAVM. Cranelift's startup delay was about 7-10x lower than WAVM's on CoreMark, PolyBenchC and clang.wasm, but its code was slower than WAVM's (PolyBenchC average about 0.70 against 0.61-0.62, CoreMark about 0.59 s against 0.43 s). Against TurboFan it was roughly even on code speed (0.70 against 0.69 on PolyBenchC; faster on CoreMark) and slower to compile on three of four modules. Wasm build flags and the harness are not public.

## Use it when

- Embedding a WebAssembly sandbox in a C, C++ or Rust service where compile latency for each module matters and an LLVM-based ahead-of-time engine is about 10x slower to compile (paper Fig. 18: about 100-110x copy-and-patch startup delay for Wasmtime Cranelift against about 800-1100x for WAVM).
- Writing a JIT or debug-build backend in Rust that should compile much faster than LLVM while keeping code in the range of an optimizing tier (the same codegen drives rustc_codegen_cranelift).
- Multi-tenant hosts that need a maintained security process: fuzzing against V8 and the executable Wasm spec, a regalloc2 checker, published advisories and patched LTS branches (for example 36.0.17 on 2026-10-02).
- Targets limited to x86-64 (System V and Windows x64), aarch64 (Linux and macOS) on Apple silicon, s390x or riscv64; SIMD is complete on x86-64 and aarch64.

## Skip it when

- Peak throughput with compile time unimportant: LLVM via WAVM ran the PolyBenchC average about 14% faster and CoreMark in about 0.43 s against 0.59 s.
- As an alternative to V8 TurboFan on both axes: in the same paper TurboFan compiled faster on CoreMark, PolyBenchC and clang.wasm, tied on AutoCAD, and its PolyBenchC code was about 2% faster (Cranelift was faster only on CoreMark, 0.59 s against 0.94 s).
- Startup-dominated workloads of small or huge modules: baseline compilers start far sooner (copy-and-patch had two to three orders of magnitude lower startup delay than the optimizing compilers); inside Wasmtime that role belongs to the Winch baseline compiler, which had two Critical or Moderate sandbox advisories in April 2026.
- C++-only toolchains that want to drive the code generator directly: Cranelift is Rust with no stable C API, and its README says its APIs are not yet considered stable.
- Hosts outside the four backends (for example 32-bit x86 or 32-bit Arm); the README lists only x86-64, aarch64, s390x and riscv64.

## How it is fast

A single IR runs from the frontend through register allocation, instead of LLVM's chain of LLVM IR, SelectionDAG, MachineInstr and MC layers (docs/compare-llvm.md). Mid-end rewrites run on an e-graph built inside the data-flow graph (codegen/src/egraph), with optional alias analysis that removes redundant loads; instruction selection is written as ISLE rewrite rules (prelude_lower.isle and per-ISA rules). Registers come from regalloc2, either a backtracking allocator with live-range splitting or a single_pass allocator that compiles faster but spills more, and the codegen crates avoid call-stack recursion.

## Compared with alternatives

Pick Cranelift over WasmNow or other copy-and-patch baseline compilers when code quality matters (copy-and-patch's PolyBenchC code was about 1.4x slower than Cranelift's in the same paper) and you need a maintained, security-supported production runtime. Pick TPDE instead when you already emit LLVM IR and only need faster -O0-class code generation, and V8 when you are inside a browser or Node.

## Integration

| | |
|---|---|
| **Form** | crate (cranelift-codegen, cranelift-frontend, cranelift-jit, cranelift-object); for C and C++ hosts, the Wasmtime C API library with wasm.h, wasi.h, wasmtime.h and the C++ wasmtime.hh header |
| **Dependencies** | cranelift-codegen: regalloc2, hashbrown, smallvec, bumpalo, target-lexicon, log, rustc-hash, libm and sibling cranelift-\* crates (gimli, capstone, serde optional); Wasmtime adds many more |
| **Minimum toolchain** | Rust 1.97.0 on main and for 0.137.0-rc.1 (policy: at most current stable minus 2), Rust 1.96.0 for cranelift-codegen 0.136.x; edition 2024 |
| **Platforms** | x86-64 (System V and Windows x64 ABIs), aarch64 (Linux and macOS), s390x, riscv64 |
| **Thread safety** | not documented in the pages read |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the README numbers: '\~2% slower than V8' and '\~14% slower than WAVM' are ratios of Fig. 22 bars, each an arithmetic mean over 30 PolyBenchC kernels of times normalized to a third compiler (copy-and-patch), from only three runs with no confidence intervals. They are not a direct Cranelift-versus-TurboFan comparison, and Fig. 21 shows wide per-kernel scatter.
- The numbers describe Wasmtime 0.26 in 2021 and depend on the embedding: the same Cranelift inside Wasmer 1.0 took about 1.12 s on CoreMark against 0.59 s under Wasmtime (Fig. 20), and current cranelift-codegen is 0.136.2 stable or 0.137.0-rc.1.
- Raw Cranelift defaults are tuned for safety, not speed: opt_level defaults to none (the first enum value) and enable_verifier defaults to true, which the settings docs say makes compilation slower. Direct cranelift-jit users must set both before comparing compile or run time.
- Sandbox safety rests on codegen correctness: CVE-2026-34971 (GHSA-jhxm-h53p-jm7w, CVSS 9.0) was an aarch64 miscompile of load(iadd(base, ishl(index, amt))) that allowed sandbox escape with 64-bit memories when Spectre mitigations or signals-based traps were off (fixed in 36.0.7, 42.0.2 and 43.0.1), and x86-64 f64.copysign and f64x2.splat produced out-of-sandbox loads (January and April 2026). Parts of the docs are stale: compare-llvm.md still says Cranelift does no mid-level optimization, and the README badge says rustc 1.37.

## Known shortcomings

- Raised C to B on the Xu and Kjolstad copy-and-patch paper (OOPSLA 2021, PDF reached via the sillycross.github.io repo mirror): Cranelift's generated code is about 2% slower than V8 TurboFan and 14% slower than WAVM, TurboFan also compiles faster, and the only win is a 7-10x faster compile than LLVM; Wasmtime 0.26 numbers from 2021. Rust code generator, reachable from C++ through the wasmtime C API.
- Enricher: the README's 2% (vs V8) and 14% (vs WAVM) are ratios of the paper's Figure 22 arithmetic means normalized to copy-and-patch, 3 runs with no confidence intervals; the same Cranelift inside Wasmer 1.0 runs CoreMark in 1.12 s against 0.59 s under Wasmtime, so the embedding moves the result about 2x. Raw Cranelift defaults to opt_level none with the verifier on. CVE-2026-34971 (critical aarch64 miscompile, sandbox escape); measured Wasmtime 0.26 against current 0.136.2.

## Caveats and trade-offs

Numbers come from a 2021 third-party paper (Xu and Kjolstad, Copy-and-Patch Compilation, OOPSLA 2021, arXiv 2011.13127) measuring Wasmtime 0.26; current Cranelift (0.137) differs, so the figures are dated. The runtime result is a loss: about 2% slower than V8 TurboFan and about 14% slower than WAVM (LLVM) on the PolyBenchC average, though on CoreMark Cranelift's code ran faster than TurboFan's. The only win is compile speed against LLVM (WAVM), and V8 TurboFan compiled faster than Cranelift on three of four modules, so against V8 Cranelift loses on both axes. Figs. 21-22 are averages of three runs without confidence intervals; WAVM never finished AutoCAD (LLVM dead loop). Ratios above are read from bar charts and approximate. Rust, not C++. rustc_codegen_cranelift (wave 2, compilers-frontends) is a separate catalogue entry that uses Cranelift as a rustc backend.

Code generator tuned for fast compilation with a small trusted code base and fuzzing against V8; backends for x86-64, aarch64, s390x and riscv64. Cranelift itself is a Rust library; C and C++ programs reach it through the Wasmtime C API (wasmtime.h, wasm.h) or by compiling Wasm to native code, not through a stable Cranelift C API.

## Maintenance

Very active: monthly Wasmtime majors (49.0.2 stable, 50.0.0-rc.1 on 2026-10-05), patched LTS branches and frequent security releases, Apache-2.0 WITH LLVM-exception, about 51.6M crates.io downloads for cranelift-codegen; the only third-party numbers measured Wasmtime 0.26 five years ago.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the README's figures come from Xu and Kjolstad, 'Copy-and-Patch Compilation' (OOPSLA 2021, PACMPL vol. 5, article 136), a peer-reviewed paper by third-party authors, opened here from the author's checked-in PDF; its Fig. 18, 20 and 22 show Wasmtime 0.26 Cranelift against V8 TurboFan and WAVM (LLVM) on an Intel i7-7700HQ. Not A: no public benchmark harness or Wasm build flags were found, and Figs. 21-22 are averages of three runs without confidence intervals.
- **Verifier notes:** README numbers match the cited paper, which is the copy-and-patch OOPSLA 2021 paper (arXiv blocked; opened from raw.githubusercontent.com/sillycross/sillycross.github.io/master/assets/copy-and-patch.pdf and checked Figs. 18, 20, 22), so tier goes C to B. Metadata verified: Apache-2.0 WITH LLVM-exception, 18.7k stars, last commit 2026-10-06, cranelift-codegen 51,595,493 crates.io downloads. Shortcomings: loses to V8 on code speed and compile speed, wins only compile speed against LLVM, numbers from Wasmtime 0.26 in 2021, three-run averages; not a duplicate (no other wasmtime entry in wave 12).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/cranelift/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/LICENSE>
  - <https://github.com/bytecodealliance/wasmtime>
  - <https://github.com/bytecodealliance/wasmtime/commits/main>
  - <https://crates.io/api/v1/crates/cranelift-codegen>
  - <https://github.com/sillycross/sillycross.github.io>
  - <https://raw.githubusercontent.com/sillycross/sillycross.github.io/master/assets/copy-and-patch.pdf>
- **Sources the enricher read:**
  - <https://github.com/bytecodealliance/wasmtime>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/cranelift/README.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/cranelift/codegen/Cargo.toml>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/cranelift/docs/index.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/cranelift/docs/compare-llvm.md>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/cranelift/codegen/src/egraph/mod.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/cranelift/codegen/meta/src/shared/settings.rs>
  - <https://raw.githubusercontent.com/bytecodealliance/wasmtime/HEAD/cranelift/codegen/meta/src/cdsl/settings.rs>
  - <https://github.com/bytecodealliance/wasmtime/tree/main/cranelift/codegen/src>
  - <https://github.com/bytecodealliance/wasmtime/security/advisories>
  - <https://github.com/bytecodealliance/wasmtime/security/advisories?query=cranelift>
  - <https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-jhxm-h53p-jm7w>
  - <https://crates.io/api/v1/crates/cranelift-codegen>
  - <https://crates.io/api/v1/crates/cranelift-jit>
  - <https://crates.io/api/v1/crates/wasmtime>
  - <https://raw.githubusercontent.com/sillycross/sillycross.github.io/master/assets/copy-and-patch.pdf>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/bytecodealliance/wasmtime`) · [data/wave12/enrich/raw/github_com_bytecodealliance_wasmtime.json](../../../data/wave12/enrich/raw/github_com_bytecodealliance_wasmtime.json) (enrichment confidence 0.8)

</details>
