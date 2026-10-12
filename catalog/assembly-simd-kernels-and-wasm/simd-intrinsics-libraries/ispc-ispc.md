# ISPC (Intel SPMD Program Compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> LLVM-based compiler for an SPMD C dialect that runs kernels on CPU SIMD lanes; 3-7x one-core speedups over serial C++ in Intel's examples.

| | |
|---|---|
| **Beats** | reference serial C++ implementations of the examples/ workloads (gcc 4.2.1 on OS X 10.7.2; MSVC 2010 on Windows Server 2008 for the 40-core table) |
| **Claimed result** | InPar 2012 paper Table 2 (4-core 3.4 GHz Core i7 iMac, 8-wide AVX), versus serial non-SIMD C++: 1 core / 1 thread aobench 5.58x, Binomial Options 4.39x, Black-Scholes 7.43x, Mandelbrot 5.85x, Ray Tracer 6.85x, Stencil 3.37x, Volume Rendering 3.24x (geomean about 5.0x, derived from page data); 4 cores / 8 threads 12.03x-34.82x. Table 3 (40-core Xeon E7-8870, SSE4, 80 threads, MSVC 2010 serial baseline): 9.40x-243.18x. SSE to AVX geomean 1.42x. README: 'frequently provides a 3x or more speedup on architectures with 4-wide vector SSE units and 5x-6x on architectures with 8-wide AVX vector units'. ispc.github.io/perf.html (gcc 4.2.1 serial baseline on the same iMac): 1 core 3.60x-8.45x, 4 cores 15.53x-33.43x. |
| **Workload** | The example programs in the repo's examples/ directory (aobench, binomial and Black-Scholes options pricing, Mandelbrot, ray tracer, 3D stencil, volume rendering; perf page adds deferred shading and Perlin noise), each timed against its included serial C++ reference (minimum of several runs; the examples print '(N.NNx speedup from ISPC)'). |
| **Metric** | throughput |
| **Hardware** | 4-core 3.4 GHz Intel Core i7 Apple iMac with AVX (exact model not stated; first-generation AVX, Sandy Bridge era) for Table 2 and the perf page; 2-way hyper-threaded 40-core Intel Xeon E7-8870 at 2.40 GHz with SSE4 on Windows Server 2008 for Table 3. |
| **Compiler and flags** | ispc of 2011-2012 (built on LLVM); serial C++ baseline compiled with clang built from the same LLVM (paper notes gcc gave essentially the same results); 40-core runs used MSVC 2010; perf page used gcc 4.2.1 (OS X 10.7.2). Optimization flags not stated. |
| **Adoption** | 3k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/ispc/ispc) · [benchmark](https://github.com/ispc/ispc.github.com/blob/main/papers/ispc_inpar_2012.pdf) |

## Verdict

The InPar 2012 paper by ispc's Intel authors reports single-core speedups of 3.24x (volume rendering) to 7.43x (Black-Scholes) over serial non-SIMD C++ built with clang on the same LLVM, on a 4-core 3.4 GHz Core i7 iMac with 8-wide AVX (unnamed model, flags unstated), 12.03x-34.82x on 4 cores with 8 threads, and 9.40x-243.18x on an 80-thread 40-core Xeon E7-8870 with SSE4 against MSVC 2010 serial code; nothing newer has been published, and no comparison against intrinsics or SIMD libraries was measured.

## Use it when

- Compute-bound float or int kernels with data-dependent branches (ray tracing, volume rendering, options pricing, noise, image filters) that compilers fail to auto-vectorize and that you do not want to hand-write in intrinsics.
- One kernel source compiled for SSE4, AVX2, AVX-512 and NEON in one go, with the generated dispatcher picking the best target at run time.
- Workloads that want both SIMD and multicore from one model: task launch scales across cores through a task system you supply (or examples/common/tasksys.cpp).
- Projects with C or C++ hosts that can add a compiler step: CMake 3.19.2+ has native ISPC language support with Make and Ninja generators, and release binaries exist for Linux, Windows and macOS.
- Code that will run on Intel GPUs as well, using the same language and the Xe targets.

## Skip it when

- You need a header-only C++ SIMD library with no extra toolchain: ispc is a separate LLVM-based compiler, and building it from source needs a patched LLVM (v1.31.0 is pinned to an LLVM 23 commit).
- Short, simple loops that clang or gcc already auto-vectorize at -O3 -march=native; the published speedups are against non-SIMD serial code, and the paper's only intrinsics comparisons are user anecdotes at 0.99x-1.05x.
- Code where bit-exact agreement with libm matters and you cannot pass --math-lib=system: the default math library is ispc's own vector approximations (sin max abs error about 1.45e-6), and the fast-math modes trade further precision.
- Memory-bound or gather/scatter-heavy kernels on AVX2 and NEON: open Performance issues include a NEON gather regression (#3721), an about 20% regression tied to LLVM after 18.1 (#3649) and inefficient shuffle and popcnt codegen (#3771, #3676).
- You need SVE or wide RISC-V support in production: rvv-x4 and PowerPC targets are experimental and excluded from official binaries.

## How it is fast

The SPMD-on-SIMD model maps a gang of program instances (4 to 64 depending on target, e.g. avx2-i32x16) onto SIMD lanes and turns divergent control flow into masked execution, so complex data-dependent loops vectorize where auto-vectorizers give up. 'uniform' values stay in scalar registers and control flow on them stays scalar; coherent-control-flow checks and 'all lanes on' specializations skip masking when lanes agree; a late pass turns varying-index gathers and scatters into plain vector loads and stores when access is actually linear; SOA types avoid gathers. The paper's ablation (Table 1, geomean over the examples) loses 0.45x without uniform data and control flow, 0.73x without all-on mask handling and 0.79x without the gather/scatter pass.

## Compared with alternatives

Pick ispc over C++ SIMD wrappers such as Pure SIMD or std::experimental::simd (marcelcases/simd) when kernels are long and branchy and you want one source to retarget across SSE4/AVX2/AVX-512/NEON with runtime dispatch; stay with a wrapper or intrinsics (or Vectis-style hand kernels) for small hot loops where an extra compiler in the build is not worth it.

## Integration

| | |
|---|---|
| **Form** | compiler (build tool) emitting object files and a C/C++ header; also usable as a C++ library with an experimental JIT since v1.28.0 |
| **Dependencies** | none at run time for non-task code; task launches need user-supplied ISPCAlloc/ISPCLaunch/ISPCSync with C linkage (examples/common/tasksys.cpp provides one); Windows binaries need the Visual C++ redistributable |
| **Minimum toolchain** | ispc release binary (v1.31.0 current); any C/C++ compiler that links the objects; CMake 3.19.2+ for native ISPC language support; source builds need a patched LLVM (LLVM 18 and 19 dropped in v1.31.0) |
| **Platforms** | hosts Windows, macOS, Linux, FreeBSD; targets x86 SSE2 to AVX-512 and AVX10.2 (avx10.2nvl/dmr enable APX by default), Arm NEON (ARMv7/ARMv8), Intel Xe GPUs; experimental rvv-x4 and ppc64le |
| **Thread safety** | not documented as a library property; exported functions are ordinary C-callable code, and the task-system hooks take per-caller handles so launches from several threads can be told apart |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry in the examples behind the numbers: the serial C++ references call scalar libm expf/logf/powf while the ispc kernels use ispc's own vectorized default math library, so options-pricing speedups mix SIMD with a math-library swap; the current examples' CMake also builds the C++ reference with only -m64 and the Release defaults (no -march), and on Windows with /fp:fast /Oi.
- The two Intel tables on the same 4-core iMac disagree by more than the paper admits: it says gcc gave 'essentially the same results' as the clang baseline, yet the perf page's gcc 4.2.1 baseline gives Binomial 7.94x vs the paper's 4.39x and Ray Tracer 4.31x vs 6.85x (about 1.8x and 0.63x apart, derived from page data); Black-Scholes reaches 8.45x on one core with 8-wide AVX, more than the lane count.
- The options example prices 128k identical options (S=100, X=98, T=2, r=0.02, v=5 for every element), so lanes never diverge, and it checks results only by printing averages; each example reports the minimum of 3 rdtsc-timed runs.
- Multi-core figures fold in tasks and hyper-threading: the 40-core table reaches 243.18x against MSVC 2010 serial code, above the 160x ideal, and the paper attributes the excess mostly to hyper-threading.

## Known shortcomings

- Raised C to B on the peer-reviewed InPar 2012 paper (copy at raw.githubusercontent.com/ispc/ispc.github.com/main/papers/ispc_inpar_2012.pdf): single core 3.24x-7.43x vs serial C++, geomean about 5.0x (derived); 2011-era numbers, CPU model and flags unstated, first-party authors; a compiler, not an intrinsics library.
- Harness flaws in the examples behind the numbers: the serial C++ references call scalar libm expf/logf/powf while ispc uses its own vectorized math library, so the options speedups include a math-library swap; the C++ reference is built with -m64 only (no -march); the options example prices 128k identical options (no lane divergence) and checks results only by printed averages. The paper says gcc gave 'essentially the same' results, yet the perf page (gcc 4.2.1, same iMac) shows Binomial 7.94x vs 4.39x and Ray Tracer 4.31x vs 6.85x, and Black-Scholes reaches 8.45x on one core above the 8-lane AVX width.

## Caveats and trade-offs

Evidence is from ISPC's Intel authors: a peer-reviewed paper (InPar 2012) plus Intel's perf page, both measured around 2011-2012 on first-generation AVX and SSE4 hardware with an unnamed Core i7 model, unstated flags and an unstated ispc version; nothing newer is published. The baseline is serial non-SIMD C++ (both versions 'received equivalent amounts of performance tuning'), not hand-written intrinsics or SIMD libraries (Highway, xsimd); the paper gives only user anecdotes for intrinsics parity (0.99x-1.05x). Multi-core figures combine task parallelism and hyper-threading with SIMD. ispc is a compiler for an SPMD C dialect, not an intrinsics library, so the category fit is loose. The ispc.github.io perf page was read from its source in the ispc/ispc.github.com repo (github.io blocked here). [retier] Evidence is from ISPC's Intel authors: a peer-reviewed paper (InPar 2012) plus Intel's perf page, both measured around 2011-2012 on first-generation AVX and SSE4 hardware with an unnamed Core i7 model, unstated flags and an unstated ispc version; nothing newer is published. The baseline is serial non-SIMD C++, not hand-written intrinsics or SIMD libraries (Highway, xsimd); the paper gives only user anecdotes for intrinsics parity (0.99x-1.05x). Harness asymmetries in the examples behind the numbers: the serial C++ references call scalar libm expf/logf/powf while the ispc kernels use ispc's own vectorized math library, so the options-pricing speedups mix SIMD with a math-library swap; the examples' CMake builds the C++ reference with -m64 and Release defaults only (no -march), on Windows with /fp:fast /Oi; the options example prices 128k identical options (no lane divergence) and checks results only by printed averages; each example reports the minimum of 3 rdtsc-timed runs. The two Intel tables on the same iMac disagree more than the paper's 'gcc gave essentially the same results' admits: Binomial 7.94x (perf page, gcc 4.2.1) vs 4.39x (paper, clang), Ray Tracer 4.31x vs 6.85x, and Black-Scholes reaches 8.45x on one core with 8-wide AVX. Multi-core figures fold in tasks and hyper-threading (243.18x on 40 cores exceeds the 160x ideal). ispc is a compiler for an SPMD C dialect, not an intrinsics library, so the category fit is loose.

A separate SPMD language and compiler (outputs object files callable from C/C++) rather than an intrinsics library; targets x86 SSE2/SSE4/AVX/AVX2/AVX-512, ARM NEON and Intel GPUs. Examples are in the repo's examples/ directory.

## Maintenance

Very active (v1.31.0 June 2026 on LLVM 23, frequent releases adding AVX10.2, Granite Rapids, Nova Lake and Zen targets, 3k stars, 269 open issues), BSD-3-Clause and copyable, but the speedup evidence is 2011-2012 first-party data on Sandy Bridge-era hardware.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the peer-reviewed InPar 2012 paper (Pharr and Mark, copy at ispc.github.com/papers/ispc_inpar_2012.pdf) Table 2 shows single-core ispc speedups of 3.24x-7.43x over serial non-SIMD C++ on the example workloads in the repo's examples/ directory; not A because the CPU is only '4-core 3.4GHz Core-i7' (no model) and no flags are given.
- **Verifier notes:** Upgrade to B on the peer-reviewed InPar 2012 paper, reached via raw.githubusercontent.com/ispc/ispc.github.com/main/papers/ispc_inpar_2012.pdf; the README claim is a summary of those numbers (single-core geomean about 5.0x on AVX). Metadata confirmed: BSD-3-Clause, 3.0k stars, last commit 2026-10-10, active, not a fork. Benchmark code is public (examples/cpu/\*/ with serial references), so an A retier would need a modern run with CPU model and flags.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-11 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ispc/ispc>
  - <https://github.com/ispc/ispc/commits/main>
  - <https://raw.githubusercontent.com/ispc/ispc/main/README.md>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/mandelbrot/mandelbrot.cpp>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/cmake/AddISPCExample.cmake>
  - <https://github.com/ispc/ispc.github.com>
  - <https://github.com/ispc/ispc.github.com/tree/main/papers>
  - <https://raw.githubusercontent.com/ispc/ispc.github.com/main/perf.html>
  - <https://raw.githubusercontent.com/ispc/ispc.github.com/master/perf.html>
  - <https://raw.githubusercontent.com/ispc/ispc.github.com/main/papers/ispc_inpar_2012.pdf>
- **Sources the enricher read:**
  - <https://github.com/ispc/ispc>
  - <https://raw.githubusercontent.com/ispc/ispc/main/README.md>
  - <https://raw.githubusercontent.com/ispc/ispc/main/docs/ispc.rst>
  - <https://raw.githubusercontent.com/ispc/ispc.github.com/main/papers/ispc_inpar_2012.pdf>
  - <https://raw.githubusercontent.com/ispc/ispc.github.com/main/perf.html>
  - <https://github.com/ispc/ispc/tree/main/examples/cpu>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/README.txt>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/cmake/AddISPCExample.cmake>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/cmake/AddISPCExampleModern.cmake>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/options/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/options/options.cpp>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/options/options.ispc>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/options/options_serial.cpp>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/cpu/options/options_defs.h>
  - <https://raw.githubusercontent.com/ispc/ispc/main/examples/common/timing.h>
  - <https://github.com/ispc/ispc/releases>
  - <https://github.com/ispc/ispc/issues?q=is%3Aissue+is%3Aopen+label%3APerformance>
  - https://www.intel.com/content/dam/develop/external/us/en/documents/simd-made-easy-with-intel-ispc.pdf (not reachable: ENOTFOUND)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ispc/ispc`) · [data/wave13/enrich/raw/github_com_ispc_ispc.json](../../../data/wave13/enrich/raw/github_com_ispc_ispc.json) (enrichment confidence 0.75)

</details>
