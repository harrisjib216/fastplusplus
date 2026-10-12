# KleidiAI (via the llama.cpp KleidiAI backend PR)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0 (the LICENSES directory also carries BSD-3-Clause.txt for some files)` · 🟢 active

> Arm's C micro-kernels for quantized/float matmul on NEON, SVE, SME; independent llama.cpp runs show wins only at 1-2 SME threads.

| | |
|---|---|
| **Beats** | llama.cpp ggml CPU backend's own Arm Q4_0 kernels (master at the time: AArch64 i8mm/dotprod repacked kernels); not XNNPACK, oneDNN or Eigen |
| **Claimed result** | llama.cpp PR #11390 (Arm-authored integration, merged 2025-02-20). Independent runs: max-krasnyansky (Qualcomm org member), Apple M4 Pro, llama 1B Q4_0, master vs KleidiAI SME: 1 thread pp128 160.94 vs 205.39, tg64 47.84 vs 62.22 (about 1.28x and 1.30x, derived from page data); 2 threads pp128 312.10 vs 389.43, tg64 87.31 vs 99.95; 4 threads pp128 586.83 vs 326.86, tg64 157.63 vs 110.52; 10 threads pp128 1173.93 vs 435.39, tg64 243.65 vs 162.36. KleidiAI I8MM on M4 Pro: 162.40, 304.78, 531.04, 1082.70 pp128 (equal or slower). Galaxy S25 (Snapdragon 8 Elite) 1 thread pp128 181.23 master vs 174.13 KleidiAI. slaren, M3 Max, llama 7B Q4_0, 12 threads: pp128 229.89 master vs 192.93 PR, tg32 31.54 vs 30.54 (slower). rmatif, Galaxy A34: pp512 84.25 master vs 87.11 PR, tg128 13.79 vs 11.00. First-party (chaxu01, Arm), Pixel 8, llama 7B Q4_0: pp512 19.33/37.59/69.59 master vs 20.48/40.40/74.00 PR at 1/2/4 threads, tg128 9.75/18.48/27.42 vs 11.58/21.40/28.27 (about 1.03-1.19x, derived). Comments as extracted: max-krasnyansky 'SME does much better on 1 and 2 threads and much worse from then on' and 'It looks like even Kleidi I8MM kernels perform worse than what we have in the master'; chaxu01 (Arm) 'KleidiAI's performance is generally comparable to the current AARCH64 kernels. However, we have observed performance degradation when using a high number of threads on hardware with high core count.' The record's quoted 'PR summary' ('KleidiAI SME excels with 1-2 threads but degrades significantly at higher core counts. I8MM kernels consistently underperform') was not found on the page. Later first-party claim, PR #24414 (chaxu01, merged 2026-07-14): SME2 F32 vs native F32 on Apple M4 Pro, Llama-3.2-1B F32, 19.70 vs 457.57 t/s at 1 thread up to 23.6x at 2 threads, 4.3x at 6 threads; test name and build flags not stated. |
| **Workload** | llama.cpp prompt processing (pp128) and token generation (tg64) with a llama 1B Q4_0 model (727.75 MiB, 1.24 B params), CPU backend, 1 to 10 threads, KleidiAI I8MM and SME micro-kernels versus llama.cpp master, in llama.cpp PR #11390 (merged 2025-02-20). |
| **Metric** | throughput |
| **Hardware** | PR #11390: Apple M4 Pro and Samsung Galaxy S25 (Snapdragon 8 Elite) run by max-krasnyansky (member of the Qualcomm GitHub org); Apple M3 Max (12 threads) by slaren; Galaxy A34 by rmatif; Google Pixel 8 by the PR author chaxu01 (Arm). PR #24414: Apple M4 Pro (Arm author). |
| **Compiler and flags** | From the PR (the PR does not say which build produced which table): Apple Clang with 'cmake -D CMAKE_BUILD_TYPE=Release -D GGML_METAL=OFF -D GGML_BLAS=OFF -D GGML_CPU_KLEIDIAI=ON -G Ninja'; or LLVM Clang 19.1.7 with CFLAGS/CXXFLAGS='-march=armv9.2a+nosve+sme', -D GGML_NATIVE=OFF -D GGML_CPU_ARM_ARCH='armv9.2a+nosve+sme+dotprod+i8mm' -D GGML_OPENMP=OFF. Build 119d3bf. |
| **Adoption** | 187 stars on the GitHub mirror (official source is gitlab.arm.com/kleidi/kleidiai); integrated in llama.cpp (GGML_CPU_KLEIDIAI), XNNPACK (open and merged KleidiAI PRs listed on github.com/google/XNNPACK/pulls); ExecuTorch use was named in the task lead and not verified by me |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/ARM-software/kleidiai) · [benchmark](https://github.com/ggml-org/llama.cpp/pull/11390) |

## Verdict

In llama.cpp PR #11390 (Arm-authored, merged 2025-02-20), reviewers outside Arm benchmarked llama 1B/7B Q4_0 with KleidiAI against llama.cpp's own AArch64 i8mm/dotprod repacked kernels, built with Apple Clang or LLVM Clang 19.1.7 and GGML_CPU_KLEIDIAI=ON. On an Apple M4 Pro, SME was about 1.3x faster at 1 thread but 2.7x slower at 10 threads, I8MM tied or trailed, and slaren's 12-thread M3 Max run was slower (pp128 192.93 vs 229.89 t/s); only Arm's Pixel 8 run showed 1.03-1.19x at 1-4 threads, and Arm's later SME2 F32 claim (PR #24414) has not been reproduced.

## Use it when

- You maintain an inference runtime for AArch64 (Android, Linux on Arm, Apple Silicon) that already has its own thread pool and allocator, and need int4/int8 x f32, bf16, fp16 or f32 matmul kernels you can vendor as plain .c/.h files with no dependencies and no dynamic allocation.
- Single-thread or 2-thread LLM decode/prefill on SME-capable CPUs: in PR #11390 an independent run on an Apple M4 Pro measured the SME kernels 1.28x (pp128) and 1.30x (tg64) faster than llama.cpp's own Arm kernels at 1 thread.
- F32 models in llama.cpp on SME2 hardware: Arm's own PR #24414 table shows 4.3x-23.6x over ggml's native F32 path on an M4 Pro (1B model, 1-8 threads), unreproduced but large enough to be worth a local test.
- Building llama.cpp for a phone-class Arm SoC with few big cores and Q4_0/Q8_0 models: try GGML_CPU_KLEIDIAI=ON and compare with llama-bench on your own device.

## Skip it when

- Any non-Arm target: the README FAQ says it does not compile for x86, including the packing and quantization kernels.
- Multi-threaded Q4_0 inference on many-core Arm chips: in PR #11390, M3 Max at 12 threads ran pp128 192.93 vs 229.89 t/s for llama.cpp master, and M4 Pro SME at 10 threads ran pp128 435 vs 1174 t/s; the I8MM kernels tied or trailed master on M4 Pro and Galaxy S25.
- You want complete operators with threading, memory management and fusion: Arm's own FAQ points those frameworks to the Compute Library (ACL) instead.
- llama.cpp with K-quant or IQ GGUF files, or MoE models: the backend only takes Q4_0, Q8_0 and F32 weights for MUL_MAT/GET_ROWS and has no MUL_MAT_ID path, so those ops fall back to ggml's kernels.
- You need a stable API: the README warns that API changes, including function renames, may occur without notice, with two releases a month.

## How it is fast

Hand-written kernels per Arm ISA feature: NEON SDOT (FEAT_DotProd), SMMLA (FEAT_I8MM), SVE/SVE2, and SME/SME2 outer-product (MOPA) accumulation into the ZA tile array. Operands are first packed into register-blocked panels (mr x kr for the LHS, nr x kr for the RHS, with scales and bias interleaved) so the inner loop streams contiguous memory. For the int4 paths, f32 activations are quantized to int8 per row or per 32-element block at run time (qai8dxp, qsi8d32p) and multiplied against int4 weights packed offline (qsi4cxp, qsi4c32p), with the output clamp fused. Separate GEMV (1xN) and GEMM (MxN) variants and several tile sizes let the framework pick per shape.

## Compared with alternatives

Pick KleidiAI when you are building or maintaining your own Arm inference runtime and want Arm-maintained, vendorable kernels with SME/SME2 coverage and many data types. If you just want faster llama.cpp-style CPU inference, T-MAC (catalogued at 4-5x over llama.cpp's low-bit kernels on a Surface Laptop 7) and ik_llama.cpp report larger gains over llama.cpp than KleidiAI's independent results, though ik_llama.cpp's catalogued numbers are from x86.

## Integration

| | |
|---|---|
| **Form** | source-drop (per-kernel .c/.h pairs plus kai_common.h) or static lib via the provided CMake build |
| **Dependencies** | none for the kernels; CMake for the build system (CMakeLists requires 3.16, README says 3.18); GoogleTest and Google Benchmark only for tests and benchmarks |
| **Minimum toolchain** | C99 kernels (C++17 for tests and examples); GCC 11+ or Clang 11+ (CMake warns below that); SME/SME2 kernels need SME-ABI compiler support or KLEIDIAI_INTERNAL_EXTRA_ARCH=+sme; MSVC builds a subset of NEON dotprod/i8mm kernels since v1.29.0 |
| **Platforms** | AArch64 only (Linux, Android, macOS; Windows on Arm via MSVC for some kernels); each variant needs the feature in its name (dotprod, i8mm, bf16, fp16, SVE, SVE2, SME, SME2) and runtime dispatch is the caller's job |
| **Thread safety** | Kernels are stateless with no internal threading; the API is built for callers to split the output among their own threads (examples/matmul_clamp_f32_qsi8d32p_qsi4c32p shows this). |
| **Drop-in for the baseline** | partial — inside llama.cpp it is a build flag (GGML_CPU_KLEIDIAI=ON) that replaces ggml's Arm kernels for Q4_0/Q8_0/F32 matmul; as a library it is a lower-level kernel API, not a replacement for XNNPACK, oneDNN or Eigen operators |

## Gotchas

- SME matrix units are shared per CPU cluster, so SME throughput stops scaling past the unit count: Arm's PR #24414 table on an M4 Pro (2 SME units) peaks at 2 threads (892 t/s) and drops to 452-609 t/s at 4-8 threads. Current llama.cpp caps SME threads at the detected unit count; GGML_KLEIDIAI_SME=N overrides it and 0 disables SME kernels.
- llama.cpp issue #26630 (2026-08, closed as not planned): with gcc 13.3 on Cortex-X925, the -mcpu=native feature probes fail, so GGML_CPU_KLEIDIAI=ON compiles zero kai_run_matmul kernels while the build banner still says KLEIDIAI = 1. The workaround is GGML_NATIVE=OFF with an explicit GGML_CPU_ARM_ARCH; the reported 1.42x-4.57x loss covers all Arm feature kernels, not KleidiAI alone.
- Packed RHS buffers are tied to one variant's mr/nr/kr/sr layout, and the LHS is quantized and packed on every call, so end-to-end gains depend on how the framework handles packing; in PR #11390 Arm noted that early reviewer runs lacked commit f4eb1b3, which made LHS packing multithreaded.
- Precondition checks (KAI_ASSUME/KAI_ASSERT) call abort(), or __builtin_trap with KLEIDIAI_ERROR_TRAP; the _ALWAYS variants stay active under NDEBUG. SME kernels used inside a call chain that already uses ZA need a compiler with SME-ABI support.

## Known shortcomings

- Downgraded B to C: the independent measurements in llama.cpp PR #11390 (M3 Max, M4 Pro, Galaxy S25, Galaxy A34) show KleidiAI mostly equal to or slower than llama.cpp's own Arm kernels; the only independent win is the SME path at 1-2 threads on M4 Pro (about 1.28-1.30x). The numbers showing a general win are Arm's own (Pixel 8 1.03-1.19x; PR #24414 SME2 F32 without test name or flags).
- llama.cpp issue #26630 (gcc 13.3 on Cortex-X925): GGML_CPU_KLEIDIAI=ON built zero kai_run_matmul kernels while the banner said KLEIDIAI = 1, closed as not planned. Arm's PR #24414 SME2 table stops scaling past 2 threads (892 t/s at 2, 452-609 at 4-8; the M4 Pro has 2 SME units). The llama.cpp backend handles only Q4_0, Q8_0 and F32 and no MUL_MAT_ID; the API can change without notice. gitlab.arm.com (the official issue tracker) was blocked.

## Caveats and trade-offs

First-party vs independent: the PR #11390 author is chaxu01 (Charles Xu; GitHub profile company 'Arm', Lund), so the integration and the Pixel 8 numbers are Arm's own; the M4 Pro, S25, M3 Max and A34 tables were posted by people outside Arm (max-krasnyansky is a member of the Qualcomm GitHub org, slaren is a ggml maintainer), and those independent tables mostly show KleidiAI slower than llama.cpp's own Arm kernels. Arm's own comment in the PR calls KleidiAI 'generally comparable' to those kernels, with degradation at high thread counts; on 2025-02-05 Arm noted that max-krasnyansky's runs lacked commit f4eb1b3 (multithreaded LHS packing), and on 2025-02-19 said the kernels 'are currently optimized for lower thread counts', so the scaling issue was still present at merge. The baseline is llama.cpp's own ggml Arm Q4_0 kernels, not a library on the project's baseline list (oneDNN, XNNPACK, Eigen). The later SME2 F32 claim (PR #24414: 4.3-23.6x vs ggml's native F32 path) is Arm-authored, gives no test name, build flags or BLAS/Accelerate setting, and no reviewer reproduced it. The KleidiAI README and the GitHub mirror carry no comparative figures; Arm's blog claims (ExecuTorch, MediaPipe, XNNPACK) were not opened. Values were read through WebFetch page extraction; the four headline M4 Pro values were consistent across three fetches. The PR conversation had 11 hidden items that WebFetch could not load. The GitHub repo is a read-only mirror of gitlab.arm.com/kleidi/kleidiai. Numbers are dated: KleidiAI and its llama.cpp integration changed substantially since (SME2 kernels, runtime kernel selection, dynamic scheduling in PR #23819).

Arm-only (AArch64; SME/SME2, SVE, i8mm, dotprod variants; will not build on x86). Micro-kernels with caller-controlled output tiling, no threading, no allocation, no dependencies, plain .c/.h pairs (callable from C++); weights must be prepacked (RHS pack) and activations dynamically quantized and packed (LHS pack) per call, so end-to-end gain depends on the framework integration. API may change between releases (two releases per month). Dual license files: Apache-2.0 and BSD-3-Clause in LICENSES/.

## Maintenance

Actively developed by Arm (v1.32.0, two releases a month; the GitHub repo is a read-only mirror of gitlab.arm.com/kleidi/kleidiai). It is Apache-2.0, with some files under BSD-3-Clause, and copyable as plain .c/.h files, but the API can change without notice.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The PR's independent measurements (slaren on M3 Max, max-krasnyansky on M4 Pro and Galaxy S25, rmatif on Galaxy A34) mostly show KleidiAI equal to or slower than llama.cpp's own Arm kernels; the only independent win is the SME path at 1-2 threads on M4 Pro (about 1.28-1.30x). The numbers showing a general win come from Arm: the PR author's Pixel 8 table (1.03-1.19x) and the later Arm-authored PR #24414 (SME2 F32, no test name or build flags), so the evidence for 'faster' is first-party with partial methodology.
- **Verifier notes:** Answer to the orchestrator: the PR is Arm-authored (chaxu01, profile company Arm), but the measurements the record cites were posted by non-Arm contributors (a Qualcomm org member and rmatif), and they show KleidiAI mostly not faster than llama.cpp's own kernels; Arm's own PR numbers are small wins. Downgraded to C; a shortcoming worth recording is 'independent llama.cpp measurements mostly slower than llama.cpp's own Arm kernels; wins only with SME at 1-2 threads'. The record's quoted 'PR summary' sentence was not found on the page.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `license`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/ggml-org/llama.cpp/pull/11390>
  - <https://github.com/ggml-org/llama.cpp/pull/24414>
  - <https://github.com/ggml-org/llama.cpp/pulls?q=is%3Apr+kleidiai>
  - <https://github.com/chaxu01>
  - <https://github.com/max-krasnyansky>
  - <https://github.com/ARM-software/kleidiai>
  - <https://github.com/ARM-software/kleidiai/commits/main>
  - <https://github.com/ARM-software/kleidiai/tree/main/LICENSES>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/README.md>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/LICENSES/Apache-2.0.txt>
- **Sources the enricher read:**
  - <https://github.com/ARM-software/kleidiai>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/README.md>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/kai/ukernels/matmul/README.md>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/kai/ukernels/matmul/pack/README.md>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/kai/ukernels/matmul/matmul_clamp_f32_qsi8d32p_qsi4c32p/kai_matmul_clamp_f32_qsi8d32p_qsi4c32p_interface.h>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/kai/kai_common.h>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/ARM-software/kleidiai/HEAD/docs/microkernel_tables.md>
  - <https://github.com/ggml-org/llama.cpp/pull/11390>
  - <https://github.com/ggml-org/llama.cpp/pull/24414>
  - <https://github.com/ggml-org/llama.cpp/issues/26630>
  - <https://raw.githubusercontent.com/ggml-org/llama.cpp/HEAD/ggml/src/ggml-cpu/kleidiai/kleidiai.cpp>
  - https://gitlab.arm.com/api/v4/projects/kleidi%2Fkleidiai/issues (egress-blocked, not read)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/arm-software/kleidiai`) · [data/wave8/enrich/raw/github_com_arm_software_kleidiai.json](../../../data/wave8/enrich/raw/github_com_arm_software_kleidiai.json) (enrichment confidence 0.75)

</details>
