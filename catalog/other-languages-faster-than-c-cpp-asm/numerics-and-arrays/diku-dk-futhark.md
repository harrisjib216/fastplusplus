# Futhark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Haskell (compiler); Futhark language` · `ISC` · 🟢 active

> Purely functional data-parallel language compiled to OpenCL/CUDA/HIP/multicore C; PLDI 2017 compared it with hand-written Rodinia, Parboil and FinPar GPU code.

| | |
|---|---|
| **Beats** | Hand-written OpenCL reference implementations from Rodinia 3.1 (CUDA for Myocyte on NVIDIA), Parboil 2.5 (MRI-Q) and FinPar (LocVolCalib, OptionPricing); the four Accelerate benchmarks (Crystal, Fluid, Mandelbrot, N-body) were compared against Accelerate 0.15.1 (a Haskell DSL with a CUDA backend), not C/C++. |
| **Claimed result** | PLDI 2017 paper: from about 0.6x (slower, FinPar LocVolCalib on AMD W8100) to 16x (Rodinia NN on GTX 780 Ti) against hand-written OpenCL/CUDA reference implementations; geometric mean 1.81x over the 12 benchmarks that have a low-level CUDA/OpenCL implementation; Futhark slower on 4 of those 12 (geometric mean 0.79x on them). Table 1 runtimes on GTX 780 Ti, reference vs Futhark in ms: NN 178.9 vs 11.0, Backprop 46.9 vs 20.7, K-means 1597.7 vs 572.2, Myocyte 2733.6 vs 555.4 (CUDA reference), Pathfinder 18.4 vs 7.4, SRAD 19.9 vs 16.1, MRI-Q 20.2 vs 15.5, OptionPricing 136.0 vs 106.8; slower: CFD 1878.2 vs 2235.9, HotSpot 35.9 vs 45.3, LavaMD 5.1 vs 6.7, LocVolCalib 1211.1 vs 1293.2. Artifact W8100 speedup files: srad 5.60, nn 5.14, hotspot 3.58, backprop 3.21, pathfinder 2.77, lavaMD 1.25, mri-q 1.24, OptionPricing 1.19, cfd 0.86, kmeans 0.79, LocVolCalib 0.62. |
| **Workload** | 16 GPU benchmarks manually translated to Futhark (Rodinia Backprop, CFD, HotSpot, K-means, LavaMD, Myocyte, NN, Pathfinder, SRAD; FinPar LocVolCalib, OptionPricing; Parboil MRI-Q; Accelerate Crystal, Fluid, Mandelbrot, N-body), datasets in the paper's Table 2; runtime averaged over 10 runs, excluding input upload, result readback and OpenCL context creation and kernel build on both sides (Rodinia timing patched to match). |
| **Metric** | throughput |
| **Hardware** | NVIDIA GeForce GTX 780 Ti with CUDA 8.0 and AMD FirePro W8100 (OpenCL benchmarks only); host CPU not stated. |
| **Compiler and flags** | Futhark compiler git 78c956ba58057ca6773cefb466efef2fa65c1386 with the OpenCL backend and no benchmark-specific flags; references built by their own suite Makefiles with gcc/g++ (-lOpenCL) and nvcc (CUDA 8.0 on NVIDIA). The paper and artifact state no host compiler versions or optimisation flags; Rodinia OpenCL Makefiles in the yuhc/gpu-rodinia mirror use g++ -g -O2 (backprop) and -g -O3 (nn). GPU kernels on both sides are compiled by the vendor OpenCL driver. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 2.8k stars, 210 forks; futhark-benchmarks 48 stars; futhark-pldi17 artifact 8 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/diku-dk/futhark) · [benchmark](https://github.com/diku-dk/futhark-pldi17) |

## Verdict

PLDI 2017 (Henriksen et al.): 16 benchmarks hand-translated to Futhark (compiler git 78c956b, OpenCL backend, no tuning), 10-run averages on a GTX 780 Ti (CUDA 8.0) and an AMD FirePro W8100. Against hand-written OpenCL (CUDA for Myocyte) from Rodinia 3.1, Parboil 2.5 and FinPar, the geometric mean is 1.81x over 12 benchmarks, from 0.6x (LocVolCalib) to 16x (NN). Futhark is slower on 4 of the 12 (0.79x geometric mean). The four Accelerate rows compare against Accelerate 0.15.1, a Haskell DSL, not C; the artifact keeps only the W8100 per-run data.

## Use it when

- Regular nested data-parallel kernels (map/reduce/scan nests, segmented reductions, histograms, stencils, Monte Carlo pricing) that you would otherwise write and maintain as hand OpenCL or CUDA
- Porting reference GPU code that leaves reductions on the host or lacks coalescing, as Rodinia NN, Backprop and K-means do: Futhark keeps those steps on the device
- One source that must target NVIDIA (CUDA/OpenCL), AMD (HIP/OpenCL) and multicore CPUs, called from a C/C++ host through the generated library
- Large, batched inputs that keep the GPU busy; the measured runs used megabyte-scale datasets

## Skip it when

- Against well-tuned hand GPU code: the paper's own estimate is 0.79x (geometric mean of CFD, HotSpot, LavaMD and LocVolCalib). Reasons given are unneeded copies, double buffering by copy instead of pointer swap, and no time tiling
- Dense linear algebra where cuBLAS or rocBLAS applies: there is no vendor-BLAS path, and open issue #1429 asks for one
- Irregular, pointer-based or recursive structures, and mostly sequential code: the language needs regular arrays and bulk operators
- Small inputs or many short kernels: the paper blames kernel launch overhead for NN's much smaller win on the AMD GPU
- Picking it on these numbers alone: they come from a 2017 compiler on 2013-2014 GPUs, the GTX column has no per-run data in the artifact, and futhark-benchmarks publishes no results

## How it is fast

The compiler fuses nested SOACs (map-map, map-reduce and streaming combinators), so intermediate arrays are never written to memory. It flattens nested parallelism into GPU kernels and sequentialises the excess inside each thread. It transposes arrays for coalesced access and does simple block tiling in local memory. Uniqueness-typed in-place updates keep sequential inner loops cheap. In the paper's ablation, fusion gave K-means 1.42x, LavaMD 4.55x and LocVolCalib 9.4x; coalescing gave K-means 9.26x and OptionPricing 8.79x; without in-place updates K-means was 8.3x slower.

## Compared with alternatives

Pick Futhark over Halide when the kernel is general nested map/reduce/scan code with segmented reductions rather than an image pipeline whose schedule you want to tune by hand. Pick DiffEqGPU.jl for ODE ensembles in Julia, and CBQN for CPU array scripting with no GPU.

## Integration

| | |
|---|---|
| **Form** | compiler (code generator); library mode emits C source plus header to compile into a C/C++ project |
| **Dependencies** | Futhark compiler (Haskell; binary releases or a GHC build); generated code needs a C compiler plus OpenCL, CUDA or HIP for GPU backends, pthreads for multicore, and ISPC 1.31+ for the ispc backend |
| **Minimum toolchain** | Compiler: futhark.cabal 0.29.0 needs base &gt;= 4.20 (GHC 9.10+). Generated code is plain C |
| **Platforms** | Generated code: sequential C, multicore C, ISPC, OpenCL, CUDA, HIP, Python/PyOpenCL and WebAssembly backends. The PLDI artifact was tested only on Linux with NVIDIA and AMD GPUs |
| **Thread safety** | Partly documented. CHANGELOG #1169 makes futhark_context_clear_caches() and the opaque-free functions thread-safe; general rules for sharing one context across threads were not read this session |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (K-means): the patched Rodinia timer wraps cluster(), and cluster() calls allocate(). In the yuhc/gpu-rodinia copy of Rodinia 3.1, allocate() creates a new OpenCL context and queue, reads and builds kmeans.cl, allocates buffers and uploads the whole feature matrix on every run. The paper says context creation, kernel build and upload were excluded. The W8100 file shows it: first reference run 1876.9 ms, then 1128.7-1154.6 ms; the mean is 1216.08 ms (1142.66 ms without run 1). The GTX 2.79x (1597.7 vs 572.2 ms) has no per-run data, so its inflation is unknown. futhark kmeans-futhark.runtimes holds 6 runs, not 10.
- Workload choice (NN): the artifact patch changes Rodinia's run line from '-r 5' to '-r 100'. That multiplies the reference's sequential CPU findLowest work by 20 (100 linear passes over all records instead of 5), and the timed loop also reads back every distance. Futhark does the 100 argmin reductions on the GPU. The paper attributes the NN gap to exactly those 100 CPU reductions, so the 16x headline rests on this parameter; the dataset table does not say the default was 5.
- lavaMD patch adds sleep(3) after each timed reference run (outside the timer). The idle GPU may downclock before each 5-9 ms kernel; the effect was not measured. Myocyte compares Futhark OpenCL with Rodinia's CUDA version, after the patch changed workload 1 to 65536 and mode 0 to 1.
- The generated library owns GPU memory through a Futhark context, so data crosses the API as Futhark arrays (copies in and out). Keep data in Futhark values between calls, or the transfer time the paper excluded will dominate.

## Known shortcomings

- Tier B from the PLDI 2017 paper (diku-dk/futhark-website pldi17.pdf) and the diku-dk/futhark-pldi17 artifact: 0.6x (LocVolCalib, W8100) to 16x (Rodinia NN, GTX 780 Ti) against hand-written OpenCL/CUDA, geomean 1.81x over 12 benchmarks but slower on 4 of 12 (geomean 0.79x); the big speedups come from under-optimised Rodinia references (NN reduce left sequential on the CPU, Backprop reduction, K-means centre update unparallelised), which the authors say makes 0.79x the better estimate against hand-optimised code; no host compiler versions, flags, driver versions or CPU stated; Accelerate rows use a Haskell DSL baseline.
- Two harness flaws in futhark-pldi17 (code reading, not run): the K-means Rodinia timer wraps cluster(), whose allocate() call in the yuhc/gpu-rodinia copy creates a new OpenCL context, builds kmeans.cl and uploads the features on every run, although the paper says those were excluded (W8100 reference runs: first 1876.9 ms, rest 1128.7-1154.6 ms, mean 1216.08 ms, 1142.66 without the first; the GTX 2.79x has no per-run data; the Futhark kmeans file holds 6 runs, not 10); the NN patch raises Rodinia's -r 5 to -r 100, growing the sequential CPU top-k work 20x, so the 16x headline rests on that parameter. Minor: lavaMD sleeps 3 s between timed reference runs; Myocyte is a CUDA reference against Futhark OpenCL.

## Caveats and trade-offs

The wins are mostly not a language-level effect: the paper attributes them to the hand-written references leaving work unoptimised, namely Rodinia NN leaving 100 reduce operations sequential on the CPU, Backprop leaving a reduction sequential, K-means not parallelising the cluster-centre update, and Myocyte/MRI-Q lacking coalescing or locality optimisation; the authors say the 0.79x geometric mean on the 4 slower benchmarks is 'a better estimation of where Futhark stands in relation to hand-optimised GPU code'. HotSpot and Pathfinder references use time tiling that Futhark lacks. Same benchmarks but different parallelisation strategies, so same_algorithm is false for the large speedups (NN 16x, Backprop, K-means, Myocyte). Accelerate rows compare against a Haskell DSL, not C. Timings exclude transfer and kernel build on both sides. Numbers are from 2017 Futhark on 2013-2014 GPUs; the C and multicore CPU backends are not compared against C here, and futhark-benchmarks itself publishes no results. futhark-website performance.md compares against Thrust and Rodinia HotSpot only as graphs, without numbers or hardware in the text. A 2026 arXiv snippet (seen only by the search agent) reports big-integer multiplication about 1.35x slower than hand-coded CUDA. Paper PDF: https://raw.githubusercontent.com/diku-dk/futhark-website/HEAD/publications/pldi17.pdf. [retier] Harness flaws in futhark-pldi17 (code reading): the K-means Rodinia timer wraps cluster(), whose allocate() in the yuhc/gpu-rodinia copy creates a new OpenCL context, builds kmeans.cl and uploads the features on every run although the paper says those were excluded (W8100 reference runs: first 1876.9 ms, rest 1128.7-1154.6 ms; the GTX 2.79x has no per-run data); the NN patch raises Rodinia's -r 5 to -r 100, growing the sequential CPU top-k work 20x, so the 16x headline rests on that parameter. lavaMD sleeps 3 s between timed reference runs; Myocyte is a CUDA reference against Futhark OpenCL.

Purely functional ML-family language; programs are rewritten in Futhark and called from C, Python or other hosts through generated code; sequential/irregular code does not fit.

## Maintenance

Actively developed (0.28.1 released, 0.29.0 at HEAD, last commit 2026-10-11, ISC, about 2.8k stars) and usable today as a C-emitting GPU code generator. The speed evidence, though, is a 2017 paper whose largest wins come from under-optimised Rodinia references. The artifact (code reading) shows two harness flaws: the K-means reference timer includes per-run OpenCL context creation, kernel build and upload, and NN's top-k count was raised from 5 to 100.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D: the peer-reviewed PLDI 2017 paper (Henriksen et al., PDF checked into diku-dk/futhark-website publications/pldi17.pdf) reports Table 1 runtimes and Figure 13 speedups against hand-written OpenCL/CUDA references from Rodinia 3.1, Parboil and FinPar on an NVIDIA GTX 780 Ti (CUDA 8.0) and an AMD FirePro W8100, and the public artifact repo diku-dk/futhark-pldi17 (Makefile, Rodinia instrumentation patch, paper_data/aux_runtimes matching the W8100 column) reproduces it. Not A: host compiler versions, flags, OpenCL driver versions and host CPU are not stated.
- **Retiered** B to C: Enricher: the futhark-pldi17 harness includes OpenCL context creation, kernel build and feature upload inside the K-means reference timer (which the paper says were excluded) and raises Rodinia NN's -r 5 to -r 100, growing the sequential CPU work behind the 16x headline 20x; unequal-work precedent (SHOGUN): B to C.
- **Verifier notes:** Tier upgraded from D to B: the PLDI 2017 paper and its artifact were reachable via GitHub (futhark-website/publications/pldi17.pdf; diku-dk/futhark-pldi17 paper_data/aux_runtimes matches the paper's W8100 column). Main shortcoming for the orchestrator: the large speedups come from under-optimised Rodinia references (sequential CPU reductions in NN and Backprop, an unparallelised K-means update), and the authors themselves estimate 0.79x against hand-optimised GPU code, so same_algorithm is false and this is not a language win; consider whether the NN and Backprop rows fall under the crippled-baseline precedent. Metadata confirmed: ISC licence, last commit 2026-10-11 ('This is 0.28.1'), not archived, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-23 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/diku-dk/futhark/HEAD/README.md>
  - <https://raw.githubusercontent.com/diku-dk/futhark/HEAD/LICENSE>
  - <https://github.com/diku-dk/futhark>
  - <https://github.com/diku-dk/futhark/commits>
  - <https://github.com/diku-dk/futhark-benchmarks>
  - <https://raw.githubusercontent.com/diku-dk/futhark-benchmarks/HEAD/README.md>
  - <https://github.com/HIPERFIT/futhark-pldi17>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/README.md>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/Makefile>
  - <https://github.com/diku-dk/futhark-pldi17/tree/master/paper_data/aux_runtimes>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/paper_data/aux_runtimes/nn.speedup>
  - <https://raw.githubusercontent.com/diku-dk/futhark-website/HEAD/publications/pldi17.pdf>
  - <https://github.com/diku-dk/futhark-website>
  - <https://raw.githubusercontent.com/diku-dk/futhark-website/HEAD/performance.md>
  - <https://raw.githubusercontent.com/yuhc/gpu-rodinia/master/opencl/nn/Makefile>
  - <https://raw.githubusercontent.com/yuhc/gpu-rodinia/master/opencl/backprop/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/diku-dk/futhark/HEAD/README.md>
  - <https://raw.githubusercontent.com/diku-dk/futhark/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/diku-dk/futhark/HEAD/futhark.cabal>
  - <https://raw.githubusercontent.com/diku-dk/futhark/HEAD/CHANGELOG.md>
  - <https://github.com/diku-dk/futhark>
  - <https://github.com/diku-dk/futhark/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance>
  - <https://github.com/diku-dk/futhark/issues?q=is%3Aissue+is%3Aopen+slow>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/README.md>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/Makefile>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/rodinia_3.1-some-instrumentation.patch>
  - <https://github.com/diku-dk/futhark-pldi17/tree/master/paper_data>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/paper_data/aux_runtimes/kmeans-rodinia.runtimes>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/paper_data/aux_runtimes/kmeans-futhark.runtimes>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/paper_data/aux_runtimes/kmeans-rodinia.avgtime>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/paper_data/aux_runtimes/kmeans-futhark.avgtime>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/paper_data/aux_runtimes/kmeans.speedup>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/paper_data/aux_runtimes/nn-rodinia.runtimes>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/paper_data/aux_runtimes/nn-futhark.runtimes>
  - <https://raw.githubusercontent.com/diku-dk/futhark-pldi17/HEAD/paper_data/aux_runtimes/lavaMD-rodinia.runtimes>
  - <https://raw.githubusercontent.com/diku-dk/futhark-website/HEAD/publications/pldi17.pdf>
  - <https://raw.githubusercontent.com/diku-dk/futhark-website/HEAD/performance.md>
  - <https://raw.githubusercontent.com/diku-dk/futhark-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/diku-dk/futhark-benchmarks/HEAD/rodinia/nn/nn.fut>
  - <https://raw.githubusercontent.com/diku-dk/futhark-benchmarks/HEAD/rodinia/kmeans/kmeans.fut>
  - <https://github.com/yuhc/gpu-rodinia>
  - <https://raw.githubusercontent.com/yuhc/gpu-rodinia/master/opencl/kmeans/cluster.c>
  - <https://raw.githubusercontent.com/yuhc/gpu-rodinia/master/opencl/kmeans/kmeans.cpp>
  - <https://raw.githubusercontent.com/yuhc/gpu-rodinia/master/opencl/kmeans/kmeans_clustering.c>
  - <https://raw.githubusercontent.com/yuhc/gpu-rodinia/master/opencl/kmeans/run>
  - <https://raw.githubusercontent.com/yuhc/gpu-rodinia/master/opencl/nn/nearestNeighbor.cpp>
  - <https://raw.githubusercontent.com/yuhc/gpu-rodinia/master/opencl/nn/run>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/diku-dk/futhark`) · [data/wave14/enrich/raw/github_com_diku_dk_futhark.json](../../../data/wave14/enrich/raw/github_com_diku_dk_futhark.json) (enrichment confidence 0.7)

</details>
