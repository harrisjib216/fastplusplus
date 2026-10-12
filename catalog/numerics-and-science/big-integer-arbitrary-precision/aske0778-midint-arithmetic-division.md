# midint-arithmetic-division (GPU multi-precision division)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `CUDA` · `no license` · 🟡 stale

> Thesis CUDA code for batched exact big-integer division on GPU (2^13-2^18 bits); 7-19x sequential GMP throughput.

| | |
|---|---|
| **Beats** | GMP |
| **Claimed result** | 11.3x faster than GMP at 2^18 bits; 14.0x at 2^17; 18.9x at 2^16; 12.6x at 2^15; 7.4x at 2^14; 11.1x at 2^13 |
| **Workload** | Batched shifted-inverse integer division on GPU for 2^13 to 2^18-bit operands |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100 GPU; GMP baseline on AMD EPYC 7352 CPU (sequential) |
| **Compiler and flags** | nvcc -O3 -arch=sm_80 (div/cuda/Makefile); versions not stated |
| **Adoption** | 1 star |
| **Last commit** | 2025-06-26 |
| **Links** | [repository](https://github.com/aske0778/midint-arithmetic-division) · [benchmark](https://arxiv.org/html/2606.06386) |

## Verdict

On an NVIDIA A100 (nvcc -O3 -arch=sm_80), batched shifted-inverse division ran 7.4x-18.9x faster than sequential single-core GMP mpz division on an AMD EPYC 7352, for 2^13- to 2^18-bit operands at a fixed 2^32 total bits of work per test. The same paper shows it 6.7-15.5x slower than one of its own GPU multiplications, and slower than CGBN where CGBN has division.

## Use it when

- You need many independent divisions or GCDs of same-size integers between 2^15 and 2^18 bits on an NVIDIA GPU, where CGBN has no division.
- Batch throughput matters and the data already lives on the GPU.
- You want a reference implementation of integer-only Newton (shifted-inverse) division to port or study.

## Skip it when

- Sizes of 2^15 bits or less: the paper measures it 3.63-7.36x slower than CGBN's division there.
- Single or few divisions, or latency-bound code: the GMP comparison is a whole A100 against one sequential CPU core.
- Operands above 2^18 bits or of mixed sizes: the shared-memory limit (\~100 KB per block) caps size, and the size is a compile-time template parameter.
- Any production use: there is no LICENSE file, so it is reference-only, and it is a one-star thesis repo last updated 2025-06-26.
- The Futhark port: the authors report poor performance due to compiler limitations.

## How it is fast

It implements Watt's shifted-inverse division: Newton iteration computes the whole shifted inverse floor(B^h/v) using only integer arithmetic, so the quotient comes from multiplications instead of long division. One CUDA block handles one division, with operands and intermediates in registers and shared memory (sequentialization factor Q=4) to avoid global-memory traffic. Throughput comes from running 2^14-2^19 such divisions in parallel across the GPU.

## Compared with alternatives

Pick it only if you need GPU-batched division above 2^15 bits; for CPU work, FLINT or mp++ are the practical GMP-beating options, and the truncated AVX512 Montgomery code covers batched modular multiplication rather than general division.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit (nvcc), GMP (benchmark validation and baseline only) |
| **Minimum toolchain** | nvcc targeting sm_80 per the Makefile (exact CUDA version not stated) |
| **Platforms** | NVIDIA GPUs (tested on A100 / sm_80) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The GMP baseline wrapper calls mpz_import, then mpz_div plus a separate mpz_mul and mpz_sub to get the remainder, then mpz_export, with mpz_init/clear on every instance. That overhead (and not using mpz_tdiv_qr) inflates the reported GMP times.
- The GPU kernel needs a large dynamic shared-memory carve-out (the GCD path sets 98000 bytes via cudaFuncSetAttribute).
- Limb arrays are fixed-length per template instantiation; divisors and dividends share the same allocated size M.

## Known shortcomings

- No license file (reference only); fork of coancea/midint-arithmetic; batched A100 runs compared against sequential single-core GMP; README says it does not beat CGBN; stale (last commit 2025-06-26).
- GMP baseline handicapped: per instance mpz_init/import, mpz_div plus separate mpz_mul and mpz_sub for the remainder (not mpz_tdiv_qr), export/clear; likely inflates the 7-19x, which also compares a whole A100 against one CPU core.

## Caveats and trade-offs

Fork of coancea/midint-arithmetic; no LICENSE file in fork or visible in parent, so reference-only; whole A100 GPU (batched) vs sequential single-core CPU GMP; README says it does not outperform CGBN (CGBN lacks division above 2^15 bits); CUDA, not a plain C++ library; arXiv preprint, no venue stated.

Requires NVIDIA GPU; batched workloads; CUDA/Futhark.

## Maintenance

Stale thesis artifact (last commit 2025-06-26, 1 star) with no license file, so read it as a reference design rather than code to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** arXiv paper Table 1 gives the per-size speedups over sequential GMP (11.3x/14.0x/18.9x/12.6x/7.4x/11.1x); benchmark code is public in the linked repo (div/cuda/main.cu, Makefile with nvcc -O3 -arch=sm_80 linking -lgmp), hardware stated (A100 GPU, AMD EPYC 7352 for GMP). Upgraded from B: the preprint shows no venue, but code+compiler+flags+hardware qualify for A (nvcc/host compiler versions not stated).
- **Verifier notes:** Numbers match the paper exactly. Shortcomings to record: no license (reference), GPU-batched vs sequential CPU GMP is apples-to-oranges, slower than CGBN where CGBN applies, stale (last commit 2025-06-26).
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `is_fork_of`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/html/2606.06386>
  - <https://arxiv.org/abs/2606.06386>
  - <https://github.com/aske0778/midint-arithmetic-division>
  - <https://github.com/aske0778/midint-arithmetic-division/commits>
  - <https://github.com/coancea/midint-arithmetic>
  - <https://raw.githubusercontent.com/aske0778/midint-arithmetic-division/HEAD/div/cuda/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/aske0778/midint-arithmetic-division/HEAD/README.md>
  - <https://raw.githubusercontent.com/aske0778/midint-arithmetic-division/HEAD/div/cuda/Makefile>
  - <https://raw.githubusercontent.com/aske0778/midint-arithmetic-division/HEAD/div/cuda/main.cu>
  - <https://raw.githubusercontent.com/aske0778/midint-arithmetic-division/HEAD/div/cuda/ker-division.cu.h>
  - <https://raw.githubusercontent.com/aske0778/midint-arithmetic-division/HEAD/div/cuda/helpers/helper.h>
  - <https://raw.githubusercontent.com/aske0778/midint-arithmetic-division/HEAD/LICENSE>
  - <https://arxiv.org/html/2606.06386>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/aske0778/midint-arithmetic-division`) · [data/wave8/enrich/raw/github_com_aske0778_midint_arithmetic_division.json](../../../data/wave8/enrich/raw/github_com_aske0778_midint_arithmetic_division.json) (enrichment confidence 0.75)

</details>
