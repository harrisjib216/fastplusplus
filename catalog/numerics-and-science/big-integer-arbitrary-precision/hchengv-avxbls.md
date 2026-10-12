# avxbls

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🟡 stale

> AVX-512 IFMA BLS12-381 optimal ate pairing built on blst; about 1.9x lower single-pairing latency than blst's x64 assembly.

| | |
|---|---|
| **Beats** | blst (non-vectorized x64 assembly BLS12-381 pairing) |
| **Claimed result** | Per the TCHES 2025(4):848-872 paper (abstract seen as a search snippet only): 1,265,314 cycles (Granger-Scott cyclotomic squaring) or 1,195,236 cycles (compressed cyclotomic squaring) for the full pairing versus blst at 2,351,615 cycles, i.e. blst is 1.86x (resp. 1.97x) slower. |
| **Workload** | Full optimal ate pairing on BLS12-381 (Miller loop plus final exponentiation), single pairing latency in CPU cycles, AVX-512 IFMA 52-bit limb arithmetic versus blst's mulx/adx scalar assembly. |
| **Metric** | latency |
| **Hardware** | Intel Core i3-1005G1 (Ice Lake) per the paper abstract snippet; the repo itself does not state the CPU. |
| **Compiler and flags** | Repo Makefile: gcc -O3 -fomit-frame-pointer -m64 -mbmi2 -march=native -fwrapv -mtune=native -z noexecstack; test and bench binaries built with -DTEST and -DBENCHMARK. Cycle counts use read_tsc via src/rdtsc64.S, 10000 iterations after cache warm-up (src/main.c timing_pairing). gcc version not stated in the repo. |
| **Adoption** | 9 stars, 1 fork |
| **Last commit** | 2025-09-27 |
| **Links** | [repository](https://github.com/hchengv/avxbls) · [benchmark](https://eprint.iacr.org/2025/1283) |

## Verdict

The TCHES 2025(4) paper by Cheng, Fotiadis, Grossschaedl and Page (read only through search-result abstracts; tches.iacr.org and eprint.iacr.org are blocked here) reports a full BLS12-381 optimal ate pairing in 1,265,314 cycles (Granger-Scott) or 1,195,236 cycles (compressed cyclotomic squaring) versus 2,351,615 cycles for blst's scalar x64 assembly, 1.86x and 1.97x, on an Intel Core i3-1005G1 (Ice Lake). Both sides are built with the same gcc -O3 -march=native flags in the repo (Makefile and baseline/Makefile) and timed with rdtsc; the gcc version and turbo settings were not readable here.

## Use it when

- Latency of a single BLS12-381 pairing matters (one signature verification, one pairing check) on a CPU with AVX-512 IFMA: Intel Ice Lake, Tiger Lake, Sapphire Rapids or later Xeons, or AMD Zen 4/Zen 5.
- You already build on blst and can vendor its field code, swapping in the vectorized Miller loop and final exponentiation.
- As a reference for how to map extension-field tower arithmetic onto 8-lane IFMA when writing your own pairing or BN254 code.
- Research or benchmarking where reproducing the TCHES 2025 numbers against blst on the same machine is the goal (both sides ship with identical gcc flags).

## Skip it when

- Multi-pairing products (n &gt; 1, e.g. aggregate BLS verification): the default vectorized Miller-loop step add_n_dbl_n_vector reads only T[0], Q[0] and Px2[0] and ignores n, so miller_loop_n with n &gt; 1 does not compute the product of pairings.
- CPUs without AVX-512 IFMA (Intel client cores from Alder Lake on, older Xeons, Arm): there is no fallback path, and the build uses -march=native so binaries are not portable.
- Production signing/verification stacks: no library build, no hash-to-curve, signature API or subgroup/input validation in the pairing entry points, no side-channel claims, 9 stars and last commit 2025-09-27.
- Throughput-bound batch verification: it is latency-optimized for one pairing; a batch-oriented design such as VROOM's RNS approach may fit better.

## How it is fast

Fp elements are held in radix 2^48 (8 limbs x 48 bits = 384 bits) inside 64-bit lanes so that AVX-512 IFMA's 52x52-bit multiply-accumulate (vpmadd52lo/hi) leaves 4 bits of headroom for lazy carry propagation; Montgomery multiplication and reduction run 8 lanes wide. The paper's contribution is choosing vectorization granularities per tower level (layouts named 8x1w, 4x2w, 2x2x2w, 1x4x2w in fp12_avx.h) so that independent Fp/Fp2 operations inside line doubling/addition, Fp12 squaring and cyclotomic squaring fill the 8 lanes, with values converted between blst's 64-bit radix and the 48-bit radix at step boundaries. Final exponentiation uses Granger-Scott cyclotomic squaring by default or Karabina-style compressed cyclotomic squaring via the COMPRESSED_CYCLOTOMIC_SQR compile-time switch.

## Compared with alternatives

Against VROOM (also AVX-512 IFMA BLS12-381 versus blst), pick avxbls when you want plain Montgomery arithmetic in radix 2^48 tuned for single-pairing latency and a peer-reviewed TCHES result; pick VROOM for its RNS formulation or broader curve coverage (BN254). The GMP-oriented siblings (ctbignum, intx, mp++) do not implement pairings.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the bundled blst-derived sources (src/assembly.S, fields, points, recip) and src/rdtsc64.S for timing |
| **Minimum toolchain** | gcc with AVX-512 IFMA intrinsics (Makefile: gcc -O3 -fomit-frame-pointer -m64 -mbmi2 -march=native -fwrapv -mtune=native); C99 for VLAs in miller_loop_n; gcc version not stated |
| **Platforms** | x86-64 with AVX-512F and AVX-512 IFMA plus BMI2/ADX (Linux/ELF toolchain assumed by the -z noexecstack flag) |
| **Thread safety** | not documented (functions are pure on caller buffers; no global mutable state seen in pairing.c) |
| **Drop-in for the baseline** | partial — same data types and math as blst's internal pairing code, but different function names, no blst public API (blst_miller_loop, pairing context) and single-pair only in the vectorized Miller loop |

## Gotchas

- miller_loop_n/optimal_ate_pairing accept n but the vectorized Miller loop only processes the first (P, Q) pair; start_dbl_n loops over n, so results for n &gt; 1 are silently wrong rather than rejected.
- The faster 1,195,236-cycle variant needs COMPRESSED_CYCLOTOMIC_SQR set to 1 in src/pairing.h; the default build is the Granger-Scott path (1,265,314 cycles in the paper).
- The bundled test checks bilinearity identities (e(P,[k]Q) == e([k]P,Q) and two variants) with a fixed scalar inside the same implementation; it does not compare output against blst or known-answer vectors.
- Cycle counts come from rdtsc over 10000 iterations after 1000 warm-up calls; on CPUs where rdtsc ticks at a fixed reference rate, turbo and AVX-512 frequency licensing affect the reading.

## Known shortcomings

- Tier B on TCHES 2025(4), but the cycle counts (1,265,314 and 1,195,236 vs blst 2,351,615 on an i3-1005G1) were seen only in a search snippet (tches.iacr.org 403, ePrint 2025/1283 blocked). Bench code is public (src/main.c, baseline/ blst build, same gcc flags) but the gcc version is unconfirmed, so not A. Last commit 2025-09-27.
- Code bug outside the measured n=1 numbers: add_n_dbl_n_vector reads only T[0]/Q[0]/Px2[0] and ignores n, so miller_loop_n and optimal_ate_pairing with n &gt; 1 give a silently wrong multi-pairing result. Limbs are radix 2^48 (8x48 bits) in IFMA 52-bit lanes, not 52-bit limbs. The default build is the Granger-Scott variant (1,265,314 cycles); the 1,195,236 figure needs COMPRESSED_CYCLOTOMIC_SQR=1. The test checks bilinearity only, not output against blst; no library target.

## Caveats and trade-offs

Cycle counts and CPU (Intel Core i3-1005G1, Ice Lake) come from the TCHES/ePrint abstract seen as a WebSearch snippet; tches.iacr.org and eprint.iacr.org are blocked here (403), so the full paper (compiler version, turbo settings) was not read. The repo is public and reproducible in structure: src/main.c measures Miller loop and final exponentiation with read_tsc over 10000 iterations after a cache warm-up, and baseline/ contains a blst-derived scalar implementation (pairing.c, fp12_tower.c, assembly.S, rdtsc64.S) built with the same gcc -O3 -fomit-frame-pointer -m64 -mbmi2 -march=native -fwrapv -mtune=native flags; a verifier with paper access may raise this to A. The README states no numbers or CPU. Cycle counts on one laptop-class CPU; AVX-512 frequency effects and wall-clock time are not reported in the abstract. Baseline is blst, not GMP or MPFR, so it is outside the listed baselines. Last commit 2025-09-27.

Requires AVX-512 with IFMA (Ice Lake or newer Intel, Zen 4/5 class AMD with IFMA). Latency-optimized for a single pairing, not aggregate batch throughput. Built on and bundles blst sources (a baseline directory carries the scalar reference). The repo is pairing only; signatures are in a separate project.

## Maintenance

Apache-2.0 research artifact (230 commits, last 2025-09-27, 9 stars) with no releases or library target; small enough to vendor for single-pairing latency work, but fix or avoid the n &gt; 1 path and validate against blst before relying on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed TCHES 2025(4):848-872 paper reports 1,265,314 / 1,195,236 cycles versus blst at 2,351,615 cycles on an Intel Core i3-1005G1 (seen only as a search-result abstract; tches.iacr.org returned 403 here). The repo has public bench code for both sides (src/main.c timing_pairing with read_tsc over 10000 iterations; baseline/ holds a blst-derived scalar build with the same gcc -O3 -march=native flags and rdtsc64.S), but the gcc version could not be confirmed without the paper, so not A.
- **Verifier notes:** Metadata confirmed on github.com: Apache-2.0, 9 stars, 1 fork, not a fork, 230 commits, last commit 2025-09-27 ('bump'). That is 364 days before the prompt's date (active by that date) but over 12 months by 2026-10-03; left as stale. benchmark_url set to the ePrint page found by search (not openable here).
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/README.md>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/baseline/Makefile>
  - <https://github.com/hchengv/avxbls>
  - <https://github.com/hchengv/avxbls/commits>
  - <https://github.com/hchengv/avxbls/tree/main/baseline>
- **Sources the enricher read:**
  - <https://github.com/hchengv/avxbls>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/README.md>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/src/pairing.h>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/src/pairing.c>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/src/intrin.h>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/src/fp12_avx.h>
  - <https://raw.githubusercontent.com/hchengv/avxbls/HEAD/baseline/Makefile>
  - <https://github.com/hchengv/avxbls/tree/main/src>
  - <https://github.com/hchengv/avxbls/tree/main/hybridmul>
  - WebSearch snippets of https://tches.iacr.org/index.php/TCHES/article/view/12431 and https://eprint.iacr.org/2025/1283 (blocked; not opened)
  - WebSearch snippets of https://eprint.iacr.org/2026/947 and https://github.com/ganqin-liu/avxbls-sig (not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/hchengv/avxbls`) · [data/wave8/enrich/raw/github_com_hchengv_avxbls.json](../../../data/wave8/enrich/raw/github_com_hchengv_avxbls.json) (enrichment confidence 0.75)

</details>
