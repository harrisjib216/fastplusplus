# LFI (Lightweight Fault Isolation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> In-process software sandbox for native Arm64/x86-64 code; about 7% overhead versus 16-67% for AOT Wasm engines on SPEC 2017.

| | |
|---|---|
| **Beats** | WebAssembly ahead-of-time engines: WAMR 1.2.2 (LLVM AOT), Wasm2c 1.0.33 + Clang (with UVWASI), Wasmtime 16.0.0 (Cranelift AOT); all relative to native code compiled with LTO |
| **Claimed result** | ASPLOS 2024 paper Table 4, geomean run-time overhead over native LTO code on the 7 SPEC CPU2017 rate benchmarks that build for WASI: LFI 7.3% (GCP T2A) / 6.4% (Apple M1) vs WAMR 22.3% / 18.2%, Wasm2c 40.7% / 37.5% (16.5% / 15.7% after the paper's barrier removal and pinned heap register), Wasmtime 47.0% / 67.1%. Derived from page data: LFI-sandboxed code runs about 1.14x (T2A) / 1.11x (M1) faster than WAMR AOT, about 1.09x faster than the tuned Wasm2c, and 1.37x / 1.57x faster than Wasmtime. Over all 14 supported SPEC benchmarks LFI O2 overhead is 6.4% (M1) and 7.3% (T2A), about 1% when loads are not sandboxed. Repo README at HEAD: 7% (Arm64) / 8% (x86-64) overhead for read and write sandboxing, 1.5% / 6% for writes only (geomean SPEC 2017); lfi-research README: LLVM-based AOT Wasm compilers 'incur upwards of 20% runtime overhead'. |
| **Workload** | Run-time overhead versus native code compiled with LTO on SPEC CPU2017 single-copy rate C/C++ benchmarks (14 for LFI; the 7 that build under WASI for the Wasm comparison), Arm64 only in the paper, for in-process software sandboxing compared with WebAssembly AOT sandboxing. |
| **Metric** | throughput |
| **Hardware** | Apple M1 MacBook Air 3.2 GHz (Asahi Linux 6.3.0); Google Cloud T2A instance 3.0 GHz (Linux 6.1.0) |
| **Compiler and flags** | LLVM/Clang 15.0.7 with the LFI rewriter for native, LFI and Wasm builds; Wasm bytecode further optimized with wasm-opt, SIMD128 enabled, bounds checks replaced by guard pages; Wasmtime run in AOT mode. Per-benchmark SPEC compile flags are in the artifact's cpu2017/config files (paper text does not list them; artifact not opened). |
| **Adoption** | 119 stars |
| **Last commit** | 2026-01-27 |
| **Links** | [repository](https://github.com/lfi-project/lfi) · [benchmark](https://zyedidia.github.io/papers/lfi_asplos24.pdf) |

## Verdict

In the ASPLOS 2024 paper, LFI-sandboxed SPEC CPU2017 rate benchmarks (LLVM 15.0.7 with LTO for native and LFI, Arm64 only; the repo's current SPEC configs use -O3 -fomit-frame-pointer -static-pie -flto=full, and wasi-sdk clang -O3 -msimd128 -flto=full for Wasm) ran with 6.4% (Apple M1) and 7.3% (GCP T2A) geomean overhead over native LTO code, versus 18.2%/22.3% for WAMR 1.2.2 AOT, 15.7%/16.5% for a tuned Wasm2c 1.0.33 and 67.1%/47.0% for Wasmtime 16.0.0 AOT on the 7 benchmarks that build for WASI (about 1.11-1.14x faster than WAMR, derived from page data). The project's later lfi-bench SPEC runs with LLVM 20.1.7 + LTO report 6.9% on a Mac Mini M2 and 7.1% (AMD Ryzen 9 7950X) / 7.9% (unnamed Intel CPU) on x86-64 for full isolation, which back the HEAD README's 7%/8% figures.

## Use it when

- You need to isolate an existing C/C++ library (parsers, codecs, compression, image decoders) inside your own process and can rebuild it from source with a dedicated toolchain.
- Throughput-sensitive sandboxed code on Linux Arm64 or x86-64 where 15-70% Wasm AOT overhead is too much and about 7% (full isolation) or 1.5-5% (stores-only fault isolation) is acceptable.
- Many sandboxes per process with very frequent host/sandbox transitions: up to about 64K sandboxes on Arm64 (about 3K on x86-64), tens-of-cycles context switches.
- Code that uses features WASI cannot express: C++ exceptions, setjmp/longjmp, hand-written assembly, threads, fork-style process emulation.
- Research or prototyping of SFI-based compartmentalisation (for example RLBox-style library sandboxing) where you can follow an active research codebase.

## Skip it when

- You need portable, architecture-independent modules or a stable binary format: LFI binaries are tied to the target ISA and LFI toolchain version, by design.
- You must run fully adversarial code today: the lfi-runtime README says the runtime is currently used for library isolation of code written by an honest party in SYS_MINIMAL mode, hardening for arbitrarily malicious programs is ongoing, and a sandbox can still make the runtime fault or abort.
- Platforms other than Linux on Arm64/x86-64 (RISC-V is experimental; no Windows or macOS host runtime documented), or sandboxes that need more than 4 GiB of memory.
- You only have third-party binaries or .wasm modules and cannot recompile: LFI needs source (or assembly) built with its toolchain and sysroot (musl, libc++, compiler-rt, mimalloc).
- Production use that needs a stable API: the project restructured into separate repositories (lfi-runtime, lfi-rewriter, lfi-verifier, lfi-bind) in January 2026 and the library-sandboxing tutorial is still 'coming soon'.

## How it is fast

Software fault isolation with guard-free addressing: on Arm64 every load/store is rewritten into the 32-bit zero-extending register addressing mode off a reserved base register (x21), so most memory accesses cost 0-1 extra cycles instead of a separate 2-cycle guard; stack-pointer and link-register invariants, redundant-guard hoisting into two reserved registers and 80 KiB guard regions remove most remaining checks. Because the rewrite runs on the assembly that a normal optimising LLVM pipeline emits, the code keeps full -O3 + LTO optimisation (no extra Wasm IR or C translation step, no Wasm indirect-call type checks), and a small static verifier rather than the compiler carries the trust. Host calls and cross-sandbox yields go through a read-only call table without a hardware mode switch (22-26 ns syscall vs 129-160 ns native Linux, 17-18 ns yield in the paper).

## Compared with alternatives

Pick LFI over wasm2c (WABT), WAMR or aWsm when you recompile C/C++ from source anyway, run on Linux Arm64/x86-64, and want the lowest in-process sandboxing overhead plus native features (exceptions, assembly, threads); pick wasm2c, w2c2 or WAMR when you need a portable Wasm module format, non-Linux hosts, or a spec-conforming, production-hardened runtime.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | LFI LLVM/Clang toolchain and LFI sysroot (musl, libc++, compiler-rt, mimalloc; prebuilt bundles on the releases page) for guest code; liblfi runtime built with meson/ninja; lfi-bind (Go) for library trampolines |
| **Minimum toolchain** | Guest code: LFI-patched Clang (research release shipped LLVM 19; lfi-bench numbers use LLVM 20.1.7; paper used LLVM 15.0.7). Host runtime: C compiler plus meson and ninja; C++ for the optional sbox tainting library. |
| **Platforms** | Linux on Arm64 (ARMv8.0-A plus LSE) and x86-64; RISC-V experimental; tested on Apple M1/M2 under Asahi Linux (16 KiB pages), GCP T2A, AMD Ryzen 9 7950X |
| **Thread safety** | Multithreaded sandboxes supported (one LFIContext per sandbox thread, per-thread alternate signal stack); per-box mapping/copy calls are synchronised by a per-box lock, but lfi_box_free must not run concurrently with other calls on the same box. |
| **Drop-in for the baseline** | no |

## Gotchas

- Security defaults: lfi-run skips verification unless passed -v and gives the sandbox full filesystem access by default; LFIOptions also exposes no_verify and allow_wx, and liblfi does not stop a runtime from granting MAP_SHARED mappings that alias W and X pages. The lfi-llvm-toolchain README also says the upstream-LLVM aarch64_lfi target does not yet rewrite memory accesses or control flow, so build guests with the bundled rewriter toolchain and keep the verifier on.
- x86-64 toolchain correctness bug, open issue #14 (filed 2026-10-06): at -O1/-O2 the TLS rewrite of 'cmpq %fs:var, %reg' uses the live source register as scratch, giving wrong results and crashes (for example in Rust std thread-local destructor lists); workaround -mno-tls-direct-seg-refs. This affects x86-64 guests, not the Arm64 numbers in the paper.
- The paper's Wasm comparison is favourable to Wasm in some respects and unusual in others: WAMR and the authors' modified Wasm2c are non-conforming (no trap-semantics compiler barrier), the pinned-heap-register Wasm2c does not fully handle cross-module indirect calls, native code is run inside the LFI runtime so both sides share its faster syscalls, and only 7 of 14 benchmarks build for WASI. Table 4's LFI row (7.3% T2A / 6.4% M1) is identical to the paper's 14-benchmark geomean although the caption says it covers the 7-benchmark subset; the paper does not say whether it was recomputed.
- On the artifact's open CoreMark alternative the gap is much smaller than on SPEC: LFI 1.10x native vs WAMR 1.13x, Wasm2c 1.16x and Wasmtime 2.66x (M1, Asahi Linux). Current SPEC configs run a single iteration per benchmark (iterations = 1, reportable = 0) with patched SPEC sources and integrity checks disabled, so per-benchmark differences of 1-2% are within noise.

## Known shortcomings

- Sandboxes native code rather than running Wasm; the ASPLOS 2024 Table 4 numbers (LFI overhead 7.3%/6.4% against WAMR 22.3%/18.2%, wasm2c 40.7%/37.5%, wasmtime 47.0%/67.1%) are Arm64 only, measured on the lfi-research code, with WAMR and wasm2c run in non-conforming configurations and SPEC workloads that are licensed (not A). The README's x86-64 numbers have no source; the record's original snippet figures were wrong and were replaced.
- Enricher: the lfi-runtime threat model covers honest-party libraries only (SYS_MINIMAL mode, the guest can abort the runtime), lfi-run skips the verifier without -v, and open x86-64 miscompile issue #14 (TLS cmp clobbers a register at -O1/-O2). Paper Table 4's LFI row (7.3%/6.4%) is identical to the 14-benchmark geomean although the caption says a 7-benchmark subset; SPEC configs use iterations=1; the artifact CoreMark gap is small (LFI 1.10x vs WAMR 1.13x). lfi-bench spec2017 (LLVM 20.1.7 LTO) backs the HEAD README: M2 6.9%, 7950X 7.1%, unnamed Intel 7.9%.

## Caveats and trade-offs

Different execution model from a Wasm VM: LFI sandboxes native code recompiled with its own LLVM toolchain and replaces Wasm rather than running Wasm faster. Paper numbers are Arm64 only and were measured on the original research implementation (lfi-research branch, MPL-2.0; repo HEAD is MIT and the code now lives in sibling repos lfi-runtime, lfi-rewriter, lfi-verifier after submodules were removed in January 2026). The x86-64 figures (8% and 6%) in the HEAD README have no linked measurement; the lfi-research README gave \~9-10% for x86-64. In the paper WAMR and the modified Wasm2c were run as non-conforming Wasm implementations (no trap-semantics compiler barrier), only 7 of 14 benchmarks could be compared with Wasm, and SPEC CPU2017 is a licensed suite so reproduction needs a SPEC licence (artifact offers CoreMark as an alternative). Research project; x86-64 verifier was incomplete in the research version.

Sandboxes native C/C++/assembly rather than Wasm bytecode: no stable binary format, no platform independence, Arm64 and x86-64 only (RISC-V experimental); needs an LFI compiler toolchain and a verifier; \~64K (Arm64) or \~3K (x86-64) sandboxes of up to 4 GiB per address space.

## Maintenance

Active research project (lfi-project/lfi last commit 2026-01-27, lfi-runtime 400+ commits, 119 stars on the umbrella repo), MIT-licensed at HEAD (the lfi-research branch with the paper's code is MPL-2.0); usable today for library isolation of trusted-but-buggy code, but the runtime is not yet hardened against fully malicious guests and the x86-64 toolchain has an open miscompilation.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B: the peer-reviewed ASPLOS 2024 paper (Yedidia, 'Lightweight Fault Isolation', Table 4 and Figure 4) measures LFI against WAMR 1.2.2 AOT, Wasm2c 1.0.33 and Wasmtime 16.0.0 AOT on SPEC CPU2017 with LLVM 15.0.7 on Apple M1 and GCP T2A, with an artifact (zyedidia/lfi-artifact). Not A because SPEC CPU2017 sources are licensed rather than public and the compile flags live only in the artifact's SPEC config files, not in the paper.
- **Verifier notes:** Paper read from the raw.githubusercontent.com mirror of zyedidia/zyedidia.github.io (the github.io page itself is blocked); Table 4 confirms LFI's 6-7% overhead vs 15-67% for WAMR, Wasm2c and Wasmtime, so the record's search-snippet figures (Wasmtime about 150%, wasm2c about 197%) were wrong and are replaced. Tier raised C to B on the peer-reviewed paper; baseline now named (WAMR and Wasmtime are category baselines). Metadata checked: MIT at HEAD (MPL-2.0 on lfi-research), 119 stars, last commit 2026-01-27, active.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lfi-project/lfi>
  - <https://github.com/lfi-project/lfi/commits>
  - <https://raw.githubusercontent.com/lfi-project/lfi/lfi-research/README.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi/HEAD/README.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lfi-project/lfi/lfi-research/LICENSE>
  - <https://raw.githubusercontent.com/zyedidia/zyedidia.github.io/master/papers/lfi_asplos24.pdf>
- **Sources the enricher read:**
  - <https://github.com/lfi-project/lfi>
  - <https://raw.githubusercontent.com/lfi-project/lfi/HEAD/README.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi/lfi-research/README.md>
  - <https://raw.githubusercontent.com/zyedidia/zyedidia.github.io/master/papers/lfi_asplos24.pdf>
  - <https://github.com/zyedidia/lfi-artifact>
  - <https://raw.githubusercontent.com/zyedidia/lfi-artifact/HEAD/README.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi-runtime/HEAD/README.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi-runtime/HEAD/core/include/lfi_core.h>
  - <https://github.com/lfi-project/lfi-runtime>
  - <https://github.com/lfi-project/lfi-runtime/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/lfi-project/lfi-bench/HEAD/README.md>
  - <https://github.com/lfi-project/lfi-bench/tree/master/spec2017>
  - <https://raw.githubusercontent.com/lfi-project/lfi-bench/HEAD/spec2017/README.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi-bench/HEAD/spec2017/aarch64-lfi.csv>
  - <https://raw.githubusercontent.com/lfi-project/lfi-bench/HEAD/spec2017/aarch64-lfi-stores.csv>
  - <https://raw.githubusercontent.com/lfi-project/lfi-bench/HEAD/spec2017/x86_64-lfi.amd.csv>
  - <https://raw.githubusercontent.com/lfi-project/lfi-bench/HEAD/spec2017/x86_64-lfi.intel.csv>
  - <https://raw.githubusercontent.com/lfi-project/lfi-verifier/HEAD/README.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi-bind/HEAD/README.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi-llvm-toolchain/HEAD/README.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi/HEAD/docs/DETAILS.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi/HEAD/docs/LIBRARIES.md>
  - <https://raw.githubusercontent.com/lfi-project/lfi/HEAD/docs/BENCHMARKING.md>
  - <https://github.com/lfi-project/lfi/tree/master/specinvoke/config>
  - <https://github.com/lfi-project/lfi/tree/master/specinvoke/config/aarch64>
  - <https://raw.githubusercontent.com/lfi-project/lfi/master/specinvoke/config/aarch64/lfi-clang.cfg>
  - <https://raw.githubusercontent.com/lfi-project/lfi/master/specinvoke/config/aarch64/native-clang.cfg>
  - <https://raw.githubusercontent.com/lfi-project/lfi/master/specinvoke/config/aarch64/wasm.cfg>
  - <https://github.com/lfi-project/lfi/issues?q=is%3Aissue>
  - <https://github.com/lfi-project/lfi/issues/14>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/lfi-project/lfi`) · [data/wave12/enrich/raw/github_com_lfi_project_lfi.json](../../../data/wave12/enrich/raw/github_com_lfi_project_lfi.json) (enrichment confidence 0.8)

</details>
