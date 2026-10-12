# GNU MPFR with CUDA/CGBN backend (gnu-mpfr-cgbn)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-3.0` · 🟢 active

> MPFR 4.2.1 with a CUDA/CGBN backend: bit-identical batched mul/div/sqrt/fma, 18-30x over one CPU core, 115-284x device-resident.

| | |
|---|---|
| **Beats** | MPFR 4.2.1 scalar functions (GMP 6.3.0) on one CPU core |
| **Claimed result** | Peak batch speedups at n = 1024: div 30.4x and sqrt 28.2x at 32768 bits, mul 21.2x at 49152 bits, fma 18.3x at 40960 bits. Device-resident at n = 16384: fma 284x at 8192 bits, mul 230x at 4096, div 157x at 16384, add 120x at 8192, sqrt 115x at 16384. A single operation is always slower on the GPU (launch floor about 6.5 us resident, 16 us with transfers); batch add never beats the CPU (&lt;= 0.7x); div and sqrt above 32768 bits are slower than the CPU. |
| **Workload** | Correctly rounded mpfr_mul, add, div, sqrt and fma on batches of 1 to 16384 operands at 128 to 65536 bits of precision, GPU batch interface (with PCIe transfer) and device-resident vectors, versus the plain scalar MPFR function in a loop. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX PRO 4500 Blackwell (sm_120, 82 SMs at 2.41 GHz), CUDA 13.2; CPU baseline is 'one core, the same machine' (CPU model not stated) |
| **Compiler and flags** | nvcc from CUDA 13.2 (driver 595.71.05) with NVCCFLAGS '-O3 -arch=\$cuda_arch -Xcompiler -fPIC' (configure default arch 'native', sm_120 on the test GPU); host compiler GCC 14.3.1 per the design PDF's test-system table, but CFLAGS for the MPFR baseline are not stated |
| **Adoption** | 3 stars |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/steleman/gnu-mpfr-cgbn) · [benchmark](https://github.com/steleman/gnu-mpfr-cgbn) |

## Verdict

First-party wall-clock measurements (tests/cgbnbench) on an NVIDIA RTX PRO 4500 Blackwell with CUDA 13.2, MPFR 4.2.1, GMP 6.3.0 and GCC 14.3.1, against scalar MPFR in a loop on one core of an unnamed CPU in the same machine: batch peaks of 18-30x at n = 1024 (div 30.4x, sqrt 28.2x at 32768 bits) and resident peaks of 115-284x at n = 16384 (fma 284x at 8192 bits). Host CFLAGS and the CPU model are not stated, and a multi-core MPFR baseline was not measured.

## Use it when

- Many independent MPFR operations of one precision between 4096 and 16384 bits, in batches of a few thousand: the README calls this the sweet spot (resident mul 230x at 4096 bits, div 157x at 16384, n = 16384).
- Chains of operations that can stay on the GPU (vec_mul, vec_fma, vec_div ... then one vec_get): resident fma reaches 284x at 8192 bits.
- One-shot batches of about 1024 or more mul, div, sqrt or fma at 2048-32768 bits where data must round-trip each call: batch div 30.4x and sqrt 28.2x at 32768 bits, mul 4.9x at 4096 bits (n = 1024).
- Code that must keep MPFR's exact semantics (rounding modes, ternary values, exception flags) while moving bulk arithmetic to an NVIDIA GPU.

## Skip it when

- Single operations or small batches: n = 1 is always slower (launch floor about 6.5 us resident, 16 us with transfers), and batch mul at 128-512 bits stays at or below 1.8x even at n = 16384.
- Batched addition or subtraction with transfers: every add batch cell is 0.7x or less; add only pays on resident data between other operations.
- Division or square root above 32768 bits: CGBN switches to a much slower algorithm (div 71x, sqrt 163x slower per instance from 32768 to 40960 bits) and the backend still sends them to the GPU, where they lose to the CPU.
- Precision above 65536 bits, transcendental functions (exp, log, sin and others are not offloaded), batches with mixed result precisions, or hosts without an NVIDIA GPU and CUDA.
- When you can spread scalar MPFR over many CPU cores: all ratios are against one core, so a 16-core run at linear scaling would cut the 18-30x batch peaks to about 1-2x (derived from page data).

## How it is fast

Significands are packed left-aligned into fixed-width CGBN integers (a ladder of 13 widths from 128 to 65536 bits) and each element is computed by a cooperative group of 4-32 GPU threads per instance, so thousands of independent operations run in parallel. The kernels form the exact (2x or, for fma, 3x width) result with CGBN integer arithmetic and round it on the device; exponent range and flags are applied back on the host. Batches are staged through page-locked buffers in chunks of up to 32 MiB, and device-resident vectors skip the PCIe round trip entirely, which is where the 100x-plus factors come from.

## Compared with alternatives

Pick this over raw CGBN or midint-arithmetic-division when you need correctly rounded MPFR floating point (all rounding modes, flags) rather than fixed-width integers, and over APFP when the hardware is an NVIDIA GPU rather than an FPGA and the work is element-wise batches rather than 512-bit matrix multiply.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | GMP 5.0.0+ with GMP_NUMB_BITS a multiple of 32, CUDA toolkit with nvcc (developed against 13.2) and libcudart, the header-only CGBN tree (README links the author's fork steleman/nvidia-cgbn), libstdc++, pthreads (optional, for the device mutex) |
| **Minimum toolchain** | nvcc from CUDA 13.2 as tested (older toolkits not documented); host GCC 14.3.1 in the design PDF; GPU compute capability 3.5 or later |
| **Platforms** | NVIDIA GPUs only (sm_35+; tested on an RTX PRO 4500 Blackwell, sm_120); build instructions are Linux/autotools (gmake), other OSes not documented; static and shared libmpfr both supported |
| **Thread safety** | Concurrent calls from several threads are safe but serialized on one internal mutex when pthread.h is found at configure time (no lock otherwise); MPFR's flags and exponent range stay thread-local, but the auto-offload threshold is a plain process-wide global |
| **Drop-in for the baseline** | partial — it is ABI-compatible libmpfr and existing scalar code is unchanged, but speedups need the new mpfr_cgbn_\* batch or vector calls; the transparent scalar hook works but is slower (e.g. 1024-bit mul 0.18 us off vs 17.8 us on) |

## Gotchas

- Cost follows the width rung, not the precision asked for: a 33000-bit operand does 40960-bit work, and one bit above 40960 moves it to 49152.
- If the result elements in a batch do not all share one precision, or it exceeds 65536 bits, the call silently runs on the CPU; the return value (elements done on the device) is the only signal.
- Device-vector arithmetic runs in MPFR's extended exponent range; emin/emax checks and exception flags only happen in mpfr_cgbn_vec_get.
- Widths above 32768 bits use CGBN beyond its documented maximum (checked against GMP by tests/cgbn-verify); MPFR_RNDF is evaluated as MPFR_RNDZ with a meaningless ternary value.

## Known shortcomings

- Baseline is one CPU core; at n=1 it is about 3x-1570x slower than CPU MPFR (derived from page data); CPU model and CFLAGS missing (host GCC 14.3.1, tests/cgbnbench.c); LICENSE file GPL-3.0 while sources say LGPL-3.0+; not upstream MPFR though it carries FSF/INRIA copyright headers; single commit (2026-09-12).
- At 16 CPU cores the 18-30x batch peaks would drop to about 1-2x (derived); div/sqrt above 32768 bits still go to the GPU and lose to the CPU; the auto-offload threshold is a plain process-wide global; the device mutex exists only if pthread.h is found.

## Caveats and trade-offs

First-party measurements on a single machine; the CPU model is never given (README or design PDF), and the baseline is one core of scalar MPFR, so a multi-core MPFR run would shrink the ratios by up to the core count. A single operation (n = 1) is always a loss, about 3x to 1570x slower than the CPU (derived from page data); addition never wins in batch mode (every add batch cell is 0.7x or lower); the README's Limitations section says division and square root above 32768 bits are slower than the CPU. The repository is one 'Initial Github commit' (2026-09-12) of an MPFR 4.2.1 tree plus the GPU backend; no sign of upstream MPFR adoption was found, although the new source files carry the stock FSF/INRIA MPFR copyright header. The top-level LICENSE file is the GPL-3.0 text (as in upstream MPFR), while the library sources, including the new src/mpfr-cgbn.c and tests/cgbnbench.c, are LGPL-3.0-or-later. Uses CGBN beyond its documented maximum size (above 32768 bits), checked by tests/cgbn-verify.

Results are bit-identical to MPFR (same correctly rounded value, ternary value and flags for all five rounding modes); without --enable-cgbn the library is plain MPFR. Needs an NVIDIA GPU and CUDA. Precision above 65536 bits runs on the CPU, all results in one batch must share a precision, device calls are serialized on a mutex, and only mul/add/sub/div/sqrt/fma are offloaded.

## Maintenance

One 'Initial Github commit' on 2026-09-12 (3 stars, 0 forks, 0 issues) with a detailed README, design PDF and correctness tests; LGPL-3.0-or-later sources inside a stock MPFR 4.2.1 tree, so it is usable, but it is a personal fork with no upstream MPFR release carrying it found.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark against scalar MPFR 4.2.1 with public code (tests/cgbnbench.c, 'gmake bench-cgbn'), the GPU model, CUDA 13.2, nvcc flags and host GCC 14.3.1 (design PDF), but the CPU model of the baseline core and the host CFLAGS are never stated, so it cannot be A; not peer reviewed, so C.
- **Verifier notes:** Every peak figure in claimed_speedup matches the README's own summary and its tables (batch: div 30.4x, sqrt 28.2x at 32768 bits, mul 21.2x at 49152, fma 18.3x at 40960, n = 1024; resident at n = 16384: fma 284.1x, mul 230.3x, div 157.1x, add 120.1x, sqrt 114.8x). Results are claimed to be bit-identical to MPFR (rounding, ternary value, flags), checked by tests/tcgbn. Lead for the orchestrator: arXiv 2608.00085 (an MPFR/MPC port to CUDA, about 40-105x per a search snippet) was seen in search results but not opened.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/steleman/gnu-mpfr-cgbn>
  - <https://github.com/steleman/gnu-mpfr-cgbn/commits/main>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/HEAD/README.md>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/master/README.md>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/HEAD/mpfr-cgbn-design.pdf>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/main/tests/cgbnbench.c>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/main/src/mpfr-cgbn.c>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/steleman/gnu-mpfr-cgbn>
  - <https://github.com/steleman/gnu-mpfr-cgbn/commits/main>
  - <https://github.com/steleman/gnu-mpfr-cgbn/issues>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/HEAD/README.md>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/HEAD/mpfr-cgbn-design.pdf>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/HEAD/src/mpfr-cgbn.c>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/HEAD/src/mpfr-cgbn.h>
  - <https://raw.githubusercontent.com/steleman/gnu-mpfr-cgbn/HEAD/src/mpfr-cgbn-impl.h>
  - <https://github.com/steleman/nvidia-cgbn>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/steleman/gnu-mpfr-cgbn`) · [data/wave8/enrich/raw/github_com_steleman_gnu_mpfr_cgbn.json](../../../data/wave8/enrich/raw/github_com_steleman_gnu_mpfr_cgbn.json) (enrichment confidence 0.8)

</details>
