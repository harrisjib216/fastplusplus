# Proteus (programmable runtime specialization and JIT layer on LLVM for C++, CUDA and HIP)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> LLVM-based JIT layer that respecialises existing C++, CUDA and HIP kernels on runtime values; beats AOT builds of the same code on GPUs.

| | |
|---|---|
| **Beats** | Ahead-of-time compiled CUDA/HIP/C++ kernels (typical AoT compilation of the same application) |
| **Claimed result** | CGO 2025 chart as reproduced on CGO 2026 tutorial slide 10 (olympus-hpc.github.io): end-to-end speedup over AoT with a warm persistent cache (JIT compile excluded) up to 2.80x on an AMD MI250X and 1.78x on an NVIDIA V100 (WSM5); cold-cache maxima 2.52x and 1.35x, with V100 cold SW4CK 0.93x and LULESH 0.99x. The '1.23x over Jitify' from news snippets is not reproducible from the slide bars. |
| **Workload** | End-to-end GPU application speedup from specializing kernels at run time on argument values and launch parameters (CGO 2025 paper), including JIT compile overhead. |
| **Metric** | throughput |
| **Hardware** | NVIDIA V100 and AMD MI250X (CGO 2026 tutorial slide 10). |
| **Compiler and flags** | Public harness (Olympus-HPC/proteus-benchmarks): AOT and Proteus variants of each HeCBench program are built from the same main.cu by the same Makefile with Clang (PROTEUS_CC), -std=c++14 -O3 -ffast-math, CUDA default --cuda-gpu-arch=sm_70; the Proteus build only adds -fpass-plugin=libProteusPass.so and -DENABLE_PROTEUS. The paper's exact compiler versions and flags were not read (paper blocked). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Runtime values (kernel arguments, array contents, launch bounds) become constants so LLVM can fold, unroll and prune kernel code beyond what static compilation can; the README says it uses runtime context to specialize 'and enable optimizations beyond static compilation'. |
| **Adoption** | 54 stars, 397 commits; integrated experimentally in RAJA (per search snippet) |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/llnl/proteus) · [benchmark](https://2025.cgo.org/details/cgo-2025-papers/24/Proteus-Portable-Runtime-Optimization-of-GPU-Kernel-Execution-with-Just-In-Time-Comp) |

## Verdict

The CGO 2025 paper (Georgakoudis, Parasyris, Beckingsale) was not read directly. Its HeCBench figure, reproduced on slide 10 of the CGO'26 tutorial (LLNL-PRES-2015399), compares six programs (ADAM, RSBench, WSM5, Feynman-Kac, LULESH, SW4CK) end to end against AOT builds from the same source with the same Clang -O3 -ffast-math flags (compiler version not read). On an NVIDIA V100, Proteus ranged 0.93-1.35x cold and 0.99-1.78x with the persistent cache (geomeans 1.12x and 1.24x, derived), with Jitify at 0.80-1.35x. On an AMD MI250X it ranged 1.02-2.52x cold and 1.03-2.80x cached (geomeans 1.46x and 1.55x, derived). The paper's '1.23x average over Jitify' could not be reproduced from the slide's bars.

## Use it when

- GPU kernels whose trip counts, coefficients, mode flags or launch sizes are fixed for a run but known only at run time. The CGO 2025 HeCBench WSM5 run gained 1.78x on an NVIDIA V100 and 2.80x on an AMD MI250X end to end with a warm persistent cache.
- AMD GPU codes in particular: across six HeCBench programs on MI250X every program was at least 1.02x faster, with a geomean of 1.46x cold and 1.55x warm (derived from the chart). The CGO'26 tutorial also reports Marbl/MFEM total runtime 35.2% faster on MI300A.
- Long or repeated production runs (HPC campaigns, MPI jobs) where the persistent or MPI-shared cache amortises compile time across runs and ranks.
- Replacing hand-written template or constexpr specialisation ladders, or string-based Jitify/NVRTC code, in CUDA codes. On V100, Jitify was slower than AOT on four of five programs and failed on LULESH.
- RAJA- or Kokkos-style lambda code: proteus::register_lambda specialises captured variables.

## Skip it when

- Short or one-shot runs where the compile is not amortised. The CGO'26 tutorial charts show about 0.1-0.3 s of JIT overhead per program through annotations and about 0.9-1.0 s through the C++ frontend (read from the chart). Cold V100 gains are small (geomean 1.12x), with SW4CK at 0.93x and LULESH at 0.99x.
- Values that change on most launches: every distinct value set compiles a new specialisation and adds a cache entry. Arrays or objects that the specialised code mutates also rule it out, because jit_array and jit_object require read-only inputs.
- Builds that must compile the annotated code with nvcc or GCC: the annotation interface needs Clang plus the pass plugin. CI covers LLVM 19, 20 and 22 only (LLVM 21.1.8 broke in #509, LLVM 23 support is open in #498), and AArch64 tests and cross-compilation are open issues (#539, #538).
- Sharing one persistent cache across GPU models, or MPI cache sharing at scale without testing: adding DeviceArch to cache keys is still open (#483), and MPI storage-cache initialisation can deadlock (#456, open).
- Teams that need a stable, released API: there are no GitHub releases, 60 open issues and 54 stars, and the project is research-grade.

## How it is fast

The technique is runtime constant folding, a runtime constexpr. A Clang pass plugin (libProteusPass.so) extracts the LLVM IR of annotated regions at build time and replaces their call or launch sites with stubs into the runtime. At run time, libproteus hashes the specialised values, clones the module, substitutes the constants, sets launch bounds from the real block size, runs the LLVM O3 pipeline and code generation (PTX through nvptxcompiler on CUDA, hiprtc and LLD on HIP) and launches the result. Known trip counts, coefficients and mode flags enable full unrolling, constant propagation and dead-branch removal, and tighter launch bounds help register allocation. A content-hash cache (in memory, plus a persistent .proteus directory on by default, plus optional MPI-shared caches) avoids recompiling.

## Compared with alternatives

Pick Proteus over the catalogued ClangJIT, a CPU-only research fork of Clang for C++ template JIT, when you need GPU (CUDA/HIP) kernels specialised with a maintained plugin on stock LLVM 19-22. The managed-runtime siblings (HotSpot, .NET, LuaJIT, Julia) require leaving C++, whereas Proteus keeps the existing C++/CUDA/HIP code and adds JIT specialisation to chosen kernels.

## Integration

| | |
|---|---|
| **Form** | shared lib (libproteus) plus an LLVM pass plugin (libProteusPass.so); CMake package (find_package(proteus) and add_proteus), Spack recipe, Python wheels (proteus-python 2026.10.0) |
| **Dependencies** | LLVM and Clang install (the runtime links libLLVM and libclang-cpp), CUDA Toolkit 12+ (nvptxcompiler_static) or HIP 6.2+ with hiprtc and ROCm device libraries and LLD; optional MPI and MLIR |
| **Minimum toolchain** | C++17, CMake 3.18, LLVM/Clang 19+ (CI covers 19, 20 and 22), CUDA 12.2 or ROCm 6.4.3 / 7.1.1 / 7.2.0 in CI; annotations require Clang as the AOT compiler |
| **Platforms** | Linux on x86-64 (the CI target); host CPU, NVIDIA (CUDA 12) and AMD (ROCm) GPUs; AArch64 and cross-compilation are not supported yet (issues #539, #538) |
| **Thread safety** | not documented; optional asynchronous compilation runs on PROTEUS_ASYNC_THREADS worker threads (default 1), and MPI storage-cache initialisation can deadlock (#456) |
| **Drop-in for the baseline** | partial — the existing CUDA/HIP/C++ source is kept and only annotated, but the application must be rebuilt with Clang and the Proteus pass and linked against libproteus and LLVM |

## Gotchas

- The headline 'up to 2.8x AMD, 1.78x NVIDIA' figures are the warm persistent-cache bars (WSM5) of the CGO 2025 chart. The public harness (proteus-benchmarks driver.py) runs an untimed warm-up execution with PROTEUS_USE_STORED_CACHE=1 to fill .proteus, then times a second run, so those numbers exclude JIT compile time. The cold first-run bars from the same chart are 2.52x (MI250X) and 1.35x (V100).
- The harness never checks results. driver.py records process wall time only and does not compare outputs between the AOT, Proteus and Jitify builds, the ADAM benchmark's reference check is commented out, and every variant is built with -O3 -ffast-math. In ADAM all hyperparameters are literals in main(), so the gap to AOT reflects values a template or constexpr could also have fixed at build time.
- Specialised values are baked into cached objects keyed by a content hash. The cache lives in ./.proteus of the working directory by default (PROTEUS_CACHE_DIR) and persists across runs. Device architecture is not yet part of the key (#483), so clear or separate caches when moving between GPU types.
- Annotation argument indices are 1-based, captured lambda state needs register_lambda and a jit-annotated kernel, register_lambda broke at -O0 (#533, closed), and open issue #512 reports that only the outermost annotated region is specialised.

## Known shortcomings

- CGO 2025 numbers seen only in search snippets (cgo.org, llnl.gov, hpcwire blocked); the Olympus-HPC/proteus-benchmarks harness builds AOT and JIT with identical -O3 -ffast-math but publishes no results; the repo moved to llnl/proteus.
- The CGO 2026 tutorial slide 10 (olympus-hpc.github.io via raw.githubusercontent.com) reproduces the CGO 2025 chart: GPUs are an NVIDIA V100 and an AMD MI250X; the headline 2.80x and 1.78x are warm persistent-cache bars (WSM5) where driver.py fills the cache in an untimed warm-up run, so JIT compile time is excluded (the record's 'including JIT overhead' was wrong); cold maxima are 2.52x and 1.35x, with V100 cold SW4CK 0.93x and LULESH 0.99x. The harness never checks outputs (the ADAM reference check is commented out, -ffast-math). The '1.23x over Jitify' is not reproducible from the slide bars.

## Caveats and trade-offs

Numbers are snippet only: the CGO 2025 paper (Georgakoudis, Parasyris, Beckingsale, pp. 507-522, peer-reviewed, would be tier B if read), its CGO program page, the LLNL newsroom and HPCwire were all unresolvable from this environment, and the Proteus README and docs carry no numbers or paper link. 'Up to' maxima are best cases on selected applications; the public harness (Olympus-HPC/proteus-benchmarks: HeCBench adam, feynman-kac, LULESH and others, plus RAJAPerf and LBANN configs) builds AOT and JIT variants with identical -O3 -ffast-math flags but publishes no results, and GPU models are not stated (the CUDA Makefile default sm_70 suggests a V100-class part, unconfirmed). End-to-end times include JIT compile overhead per the paper abstract snippet. The repo has moved: github.com/Olympus-HPC/proteus now resolves to llnl/proteus. [retier] The headline 2.80x and 1.78x are warm persistent-cache bars: driver.py fills the cache in an untimed warm-up run, so JIT compile time is excluded (the record's earlier 'including JIT overhead' was wrong). The harness never checks outputs (the ADAM reference check is commented out, -ffast-math).

Links an LLVM-based JIT runtime into the application; compile overhead is paid on first use (mitigated by in-memory and persistent caches); the annotation interface needs Clang to build the application with the Proteus pass.

## Maintenance

Actively developed by LLNL (last commit 2026-10-09, 397 commits, 54 stars, 60 open issues, no GitHub releases, proteus-python 2026.10.0 on PyPI) under Apache-2.0 WITH LLVM-exception, and the repo moved from Olympus-HPC to llnl/proteus. The CGO'26 tutorial slide reproduces the peer-reviewed figure with per-benchmark values and names the GPUs (V100, MI250X), which could support a tier-B retier once the claim is restated as warm-cache maxima, with the cold maxima at 2.52x and 1.35x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers (up to 2.8x AMD, 1.78x NVIDIA end-to-end vs AOT; 1.23x average over Jitify) come from the CGO 2025 paper and were seen only in WebSearch snippets of the CGO program page, LLNL newsroom and HPCwire (all unresolvable here), so the wave-14 rule keeps it at C; the public harness Olympus-HPC/proteus-benchmarks (driver.py, hecbench.toml, per-benchmark Makefiles with aot/proteus/jitify builds) has no results, GPU models or CPU stated.
- **Verifier notes:** Metadata checked: 54 stars, 10 forks, 397 commits, Apache-2.0 WITH LLVM-exception, last commit 2026-10-09 (active). The repo URL now redirects to github.com/llnl/proteus (README clones LLNL/proteus; the Olympus-HPC org no longer lists it), so consider a repo_url override to https://github.com/llnl/proteus while keeping the merged id. Retier to B if the CGO 2025 paper becomes readable; harness code at github.com/Olympus-HPC/proteus-benchmarks shows AOT and JIT builds use identical flags.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `caveats`, `claimed_speedup`, `hardware`
- **Shortcomings recorded by:** verifier batch-08 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Olympus-HPC/proteus>
  - <https://github.com/Olympus-HPC/proteus/commits/main>
  - <https://github.com/LLNL/proteus>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus/HEAD/README.md>
  - <https://github.com/Olympus-HPC>
  - <https://github.com/Olympus-HPC/proteus-benchmarks>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/hecbench.toml>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/driver.py>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/benchmarks/hecbench/cuda/adam/Makefile>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/benchmarks/hecbench/hip/adam/Makefile>
- **Sources the enricher read:**
  - <https://github.com/llnl/proteus>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/README.md>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/mkdocs.yml>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/docs/index.md>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/docs/user/resources.md>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/docs/user/annotations.md>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/docs/user/config.md>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/docs/user/install.md>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/docs/dev/concepts.md>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/docs/dev/proteus-internals.md>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/docs/dev/optimization-pipeline.md>
  - <https://raw.githubusercontent.com/llnl/proteus/HEAD/include/proteus/JitInterface.h>
  - <https://github.com/llnl/proteus/issues?q=is%3Aissue>
  - <https://github.com/llnl/proteus/issues/483>
  - <https://github.com/llnl/proteus/issues/525>
  - <https://raw.githubusercontent.com/Olympus-HPC/olympus-hpc.github.io/HEAD/assets/talks/cgo-2026-tutorial.pdf>
  - <https://github.com/Olympus-HPC/olympus-hpc.github.io/tree/main/assets>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/driver.py>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/hecbench.toml>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/benchmarks/hecbench/cuda/adam/Makefile>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/benchmarks/hecbench/hip/adam/Makefile>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/benchmarks/hecbench/cuda/adam/main.cu>
  - <https://raw.githubusercontent.com/Olympus-HPC/proteus-benchmarks/HEAD/benchmarks/hecbench/cuda/wsm5/main.cu>
  - <https://pypi.org/pypi/proteus-python/json>
  - https://computing.llnl.gov/about/newsroom/proteus (WebSearch snippet only)
  - https://2025.cgo.org/details/cgo-2025-papers/24/Proteus-Portable-Runtime-Optimization-of-GPU-Kernel-Execution-with-Just-In-Time-Comp (WebSearch snippet only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/olympus-hpc/proteus`) · [data/wave14/enrich/raw/github_com_olympus_hpc_proteus.json](../../../data/wave14/enrich/raw/github_com_olympus_hpc_proteus.json) (enrichment confidence 0.75)

</details>
