# apple-bottom

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Objective-C` · `MIT` · 🟢 active

> Double-float (FP32-pair) DGEMM/ZGEMM on Apple Silicon GPUs via Metal; about 1.1-1.2x Accelerate's AMX DGEMM for resident N&gt;=2048 matrices.

| | |
|---|---|
| **Beats** | Apple Accelerate DGEMM on AMX (and OpenBLAS 6-thread in a Quantum ESPRESSO run) |
| **Claimed result** | M2 Max: DGEMM 2048^2 552 GFLOP/s vs Accelerate 468 (+18%), 4096^2 643 vs 566 (+14%). Quantum ESPRESSO Si64: 2:01 with apple-bottom vs 2:28 with OpenBLAS 6-thread (22% faster wall time, 47% less CPU usage); Si128 +12% wall. |
| **Workload** | DGEMM GFLOP/s using double-float (FP32 pair) arithmetic on Metal GPU kernels versus the CPU Accelerate AMX path, plus end-to-end Quantum ESPRESSO Si64 wall time. |
| **Metric** | throughput |
| **Hardware** | Apple M2 Max (38-core GPU, 64 GB unified memory) |
| **Compiler and flags** | clang: -Wall -Wextra -O3 -std=c11 for C and -O3 -fobjc-arc for the Objective-C++ Metal sources (Makefile). The compiler and Xcode version are not stated; the README requires an Xcode 16+ SDK for MTLMathModeSafe. |
| **Adoption** | 3 stars, 120 commits |
| **Last commit** | 2026-04-25 |
| **Links** | [repository](https://github.com/grantdh/apple-bottom) · [benchmark](https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/README.md) |

## Verdict

First-party, one Apple M2 Max (38-core GPU), clang -O3, compiler/Xcode version unstated: the README reports 552 vs 468 GFLOP/s (2048^2) and 643 vs 566 (4096^2) against Accelerate's AMX DGEMM, and the committed run shows 1.09-1.16x at N=2048-4096 but losses below N=2048. The 22% Quantum ESPRESSO Si64 wall-time gain was measured against 6-thread OpenBLAS, not Accelerate.

## Use it when

- Iterative codes on Apple Silicon (SCF, CG, GMRES, Lanczos) that keep square matrices of N &gt;= 2048 resident on the GPU across many GEMMs; the repo's steady-state run shows 1.09-1.16x Accelerate at N=2048-4096 on an M2 Max.
- ZGEMM-heavy workloads with N &gt;= 1024 kept in ABMatrix handles (the header's steady-state crossover).
- When you want to offload FP64-class GEMM from the CPU to free it for other work (the QE run reports 47% less CPU time).
- Applications that tolerate \~1e-15 relative error per element rather than bit-exact IEEE FP64, with values inside roughly 1e-30 to 1e30.

## Skip it when

- Through the drop-in BLAS ABI with raw pointers: the repo's own end-to-end sweep (commit 271a0f0) measures 2-20 GFLOP/s on the GPU path vs 250-690 for Accelerate at all shapes up to 2048^3 (roughly 28-200x slower), because FP64-to-double-float conversion runs at about 140 MB/s; the header itself recommends AB_MODE=cpu for Fortran hosts.
- Matrices below about N=1024-2048 or one-shot GEMMs: steady-state DGEMM is 0.18x Accelerate at 256 and 0.93x at 1024, with about 50-100 us dispatch overhead per call.
- Anything needing IEEE FP64 semantics: double-float has FP32 exponent range (validated 1e-30 to 1e30), flushes values below about 1e-38 to zero, and per-element errors reach 1e-11 to 1e-7 on some shapes; the README itself rules out pivoted LU and eigensolvers.
- Non-Apple platforms, or multi-threaded callers: Metal-only, and matrix operations are documented as not thread-safe.
- Production use that needs a track record: a single-author project (3 stars) measured on one M2 Max.

## How it is fast

Each double is stored as an unevaluated sum of two floats (hi, lo), and products/sums use Dekker/Knuth error-free transformations (twoSum, twoProduct; the DWTimesDW2 algorithm by default, DWTimesDW3 optionally), giving about 48 mantissa bits on the GPU's FP32 ALUs. The Metal kernel uses 64x64 tiles with 4x4 register blocking, compiled with MTLMathModeSafe so the shader compiler cannot reassociate the FMAs. Complex GEMM uses Gauss's 3-multiplication trick (three real GEMMs instead of four). The win comes from the GPU's FP32 throughput exceeding the CPU AMX unit's FP64 throughput at large N, once data already sits on the GPU.

## Compared with alternatives

Pick apple-bottom only when you need FP64-class GEMM on an Apple GPU with operands kept resident; for IEEE FP64 or FP32 on the CPU, MTGEMM-A (beats Accelerate sgemm/dgemm) or the SME kernels in sme-gemm and MaxMulSK are the safer choices, and they need no host-device conversion.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib |
| **Dependencies** | Metal and Foundation frameworks; Accelerate (re-exported by the dylib, used for CPU routing); OpenBLAS optional for the Fortran bridge |
| **Minimum toolchain** | macOS 14+ with an Xcode 16+ SDK (needed for MTLMathModeSafe; older SDKs build but give about 1e-8 precision); clang, C11 and Objective-C++ (-std=c++11) sources |
| **Platforms** | Apple Silicon (M1-M4) macOS only; benchmarked only on M2 Max |
| **Thread safety** | ab_init/ab_shutdown are thread-safe (dispatch_once); matrix operations are not (header: Metal command queue serializes) |
| **Drop-in for the baseline** | partial — the dylib exports dgemm_/zgemm_ and shadows Accelerate at link time, but in the default AB_MODE=auto that path sends DGEMMs of &gt;= 50M FLOPs to the GPU, where per-call conversion makes it far slower than Accelerate; speedups need the ABMatrix handle API |

## Gotchas

- Default AB_MODE is auto with a 50M-FLOP real / 100M-FLOP complex crossover, so a 512^3 DGEMM through the BLAS ABI goes to the slow GPU path; set AB_MODE=cpu or raise AB_CROSSOVER_FLOPS_REAL unless you use resident handles.
- The README's headline numbers (552/643 GFLOP/s vs 468/566) do not match the committed result files (654/670 vs 563/586 in 2026-04-22-b9b0641/dgemm.csv), and the benchmark times the GPU kernel on already-uploaded matrices while timing Accelerate whole.
- Linking order matters: libapplebottom must precede Accelerate/OpenBLAS so its dgemm_/zgemm_ win, which silently redirects every BLAS GEMM in the process.
- Hard limits: maximum dimension 46,340, 128 pool entries (ab_pool_get_matrix returns NULL when full), 64 matrices per session; ZHERK is marked deprecated in the README (20x slower than CPU) although the header claims a later GPU win at N &gt;= 1024.

## Known shortcomings

- GPU timing excludes double-double conversion, upload and download; README numbers are not in the committed results CSV; its own results show the GPU losing to Accelerate on QE-shaped ZGEMM (0.38-0.88x); the 22% QE win is vs OpenBLAS, not Accelerate; max per-element relative error up to 2.3e-7.
- Default AB_MODE=auto sends DGEMM &gt;=50M FLOPs through the BLAS ABI to the GPU, and the repo's own end-to-end sweep shows 2-20 vs 250-690 GFLOP/s for Accelerate (28-200x slower); the header itself recommends AB_MODE=cpu, so the drop-in and QE 22% claims are weak; FP32 exponent range, denormals below \~1e-38 flushed; not thread-safe.

## Caveats and trade-offs

The numbers are first-party from one machine (M2 Max), with no compiler version. The README's DGEMM rows (552 vs 468 GFLOP/s at 2048^2, 643 vs 566 at 4096^2) are not in the committed results. benchmarks/results/2026-04-23-5cfcd52/bench_paper.csv shows 656 vs 560 (1.17x) and 672 vs 604 (1.11x). The README headline says 618 GFLOP/s, and its prior-art table lists Accelerate at 536. benchmarks/bench_dgemm.c times only ab_dgemm on matrices already uploaded to the GPU, so FP64-to-double-float conversion, upload and download fall outside the timed loop, while the Accelerate loop is timed whole. Only 5 iterations are run at N &gt;= 2048, and Accelerate's thread count is left at its default. Per the repo's own results file, the GPU path loses to Accelerate below about N=1024-1536 (0.11x at 256, 0.95x at 1024) and on the Quantum ESPRESSO-like tall-skinny ZGEMM shapes (0.38-0.88x); ZHERK runs at 0.07-0.56x. The 22% Quantum ESPRESSO wall-time win is against 6-thread OpenBLAS, not Accelerate, and the Fortran bridge routes calls under 100M FLOPs to OpenBLAS/Accelerate. Double-float arithmetic gives a \~48-bit mantissa, not IEEE FP64. The normwise error is \~1e-14, but the same results file reports a maximum per-element relative error of up to 2.3e-7 (4096x150, K=150), and 'bit-identical energy' means agreement to the 8 printed decimals of the Ry energy. The project is Apple-GPU only (Metal) and has 3 stars.

Metal compute shaders with a C API (apple_bottom.h) and a Fortran bridge that routes calls under 100M FLOPs to OpenBLAS/Accelerate and large calls to the GPU; callable from C++. Not IEEE FP64: precision is about 1e-15 (double-float), so results are not bit-exact; ZHERK is slower than the CPU path; single calls under N=1024 are dominated by about 100 us GPU overhead; max dimension 46,340.

## Maintenance

Recently active single-author project (v1.3.1-dev, last commit 2026-04-25, no open issues) under MIT; small enough to vendor, but treat it as experimental because the default drop-in path is slower than Accelerate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party numbers on an Apple M2 Max, and the benchmark code is public (benchmarks/bench_dgemm.c, bench_paper.c) with -O3 flags in the Makefile. No compiler or Xcode version is stated, and the quoted DGEMM rows do not appear in the committed results, so the tier is C.
- **Verifier notes:** The record's numbers match the README table. The main shortcomings are methodological. GPU timings exclude data conversion and transfer. The README numbers differ from the committed results run. The repo's own results show the GPU losing to Accelerate on the QE-shaped ZGEMM calls behind the 22% application claim. The page confirms MIT, 3 stars and the last commit on 2026-04-25.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/grantdh/apple-bottom>
  - <https://github.com/grantdh/apple-bottom/commits/main>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/README.md>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/Makefile>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/LICENSE>
  - <https://github.com/grantdh/apple-bottom/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/benchmarks/bench_dgemm.c>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/benchmarks/bench_paper.c>
  - <https://github.com/grantdh/apple-bottom/tree/main/benchmarks/results>
  - <https://github.com/grantdh/apple-bottom/tree/main/benchmarks/results/2026-04-23-5cfcd52>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/benchmarks/results/2026-04-23-5cfcd52/bench_paper.csv>
- **Sources the enricher read:**
  - <https://github.com/grantdh/apple-bottom>
  - <https://github.com/grantdh/apple-bottom/issues>
  - <https://github.com/grantdh/apple-bottom/tree/main/benchmarks/results/2026-04-24-271a0f0-rect>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/README.md>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/Makefile>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/include/apple_bottom.h>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/src/blas_wrapper.c>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/docs/vv/PRECISION_ENVELOPE.md>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/docs/INTEGRATION.md>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/benchmarks/results/2026-04-22-b9b0641/dgemm.csv>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/benchmarks/results/2026-04-24-271a0f0-rect/dgemm_gpu_sweep1.csv>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/benchmarks/results/2026-04-24-271a0f0-rect/dgemm_cpu_sweep1.csv>
  - <https://raw.githubusercontent.com/grantdh/apple-bottom/HEAD/benchmarks/results/2026-04-24-271a0f0-rect/dgemm_auto_sweep1.csv>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/grantdh/apple-bottom`) · [data/wave8/enrich/raw/github_com_grantdh_apple_bottom.json](../../../data/wave8/enrich/raw/github_com_grantdh_apple_bottom.json) (enrichment confidence 0.8)

</details>
