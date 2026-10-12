# primefactors (CPU GMP/GMP-ECM reference plus CGBN GPU factoring programs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C and CUDA` · `MIT` · 🟢 active

> Hobby integer-factoring programs: CPU GMP-ECM reference plus CGBN GPU variants that, by the author's own numbers, lose to CPU ECM.

| | |
|---|---|
| **Beats** | GMP-ECM 7.0.6 (libecm, on GMP): the repo's own CPU reference path is GMP plus libecm, and the GPU programs are measured against it |
| **Claimed result** | None: the project claims no speedup and says the opposite. README 'Performance reality': the GPU programs 'do not beat the CPU for hard inputs'; for integers below 2^64 they are 'much slower than their GMP-ECM equivalent'; on an RTX 4080 a 16-digit factor takes about 8.7 s with GPU rho versus about 2 s for CPU ECM on the same number (about 4x slower, derived from page data), and 19-digit and larger factors are impractical. CPU path wall clock (32-core box, equal-size prime semiprime): 30-digit factor about 10.5 s, 35-digit about 20.6 s, 40-digit about 5.7 min. |
| **Workload** | Prime factorization of semiprimes: Pollard's rho on GPU (CUDA with the author's CGBN fork) against CPU ECM on the same number, 16-digit factor; CPU ECM wall clock on a 32-core box for 30-, 35- and 40-digit factors. |
| **Metric** | latency |
| **Hardware** | Tested on a laptop with RTX 4080 Ada (sm_89) and Core i9-14900HX, and an Intel NUC 13 Extreme with RTX PRO 4500 Blackwell (sm_120) and Core i9-13900K, Fedora 41 and 44; the 32-core CPU box for the ECM timings is not identified. |
| **Compiler and flags** | CPU: /usr/bin/gcc -O3 -std=c17 -Wall -Wextra -Wpedantic -funroll-loops -ftree-vectorize -ftree-slp-vectorize -fopenmp, -D_GNU_SOURCE -D_XOPEN_SOURCE=700, link -lecm -lgmp -lm -flto=32 -O3. GPU: nvcc (/usr/local/cuda-12.9, also tested with CUDA 13.2) -O3 -arch=sm_89 (sm_120 on Blackwell), OpenMPI 5.0.5 via mpicxx --showme, GMP-ECM 7.0.6 (from the Makefile and README). |
| **Adoption** | 1 star, 0 forks, 7 commits (github.com page) |
| **Last commit** | 2026-09-01 |
| **Links** | [repository](https://github.com/steleman/primefactors) · [benchmark](https://raw.githubusercontent.com/steleman/primefactors/HEAD/README.md) |

## Verdict

These are first-party wall-clock figures, and they are not a speedup. On an RTX 4080 (CUDA 12.9, nvcc -O3 -arch=sm_89) the GPU Pollard's rho needs about 8.7 s for a 16-digit factor, versus about 2 s for the CPU GMP-ECM path on the same number. The CPU path (gcc -O3 -fopenmp, GMP-ECM 7.0.6) took about 10.5 s, 20.6 s and 5.7 min for 30-, 35- and 40-digit factors on an unnamed 32-core machine, and was never compared with the stock ecm binary or with single-threaded GMP-ECM.

## Use it when

- As readable example code for CGBN: width dispatch through an X-macro, the cooperative atomicCAS + __shfl_sync claim of a result, exact modular squaring, per-thread CUDA streams, and a design PDF that records three reverted 'optimizations' with measured slowdowns (Brent batched gcd about 2.6x slower, per-instance ILP 2-4x, __launch_bounds__ capping).
- Quick CPU factoring of 30-40 digit factors on a many-core Linux box that already has GMP and libecm: the author reports about 10.5 s (30 digits), 20.6 s (35) and 5.7 min (40) for balanced semiprimes on a 32-core machine.
- Throughput experiments that split many small factors (up to about 16 digits) across several GPUs with one MPI rank per GPU; the author has not tested multi-node runs.
- A starting point for MPI-distributed trial division against a table of primes you have already proven.

## Skip it when

- You want something faster than GMP-ECM: GPU rho took about 8.7 s on an RTX 4080 for a 16-digit factor vs about 2 s for CPU ECM (about 4x slower, derived from page data); factors of 19 or more digits are impractical on the GPU path; below 2^64 both GPU programs are 'much slower' because of CUDA and MPI start-up.
- Factors beyond about 45 digits: the README says single-machine ECM tops out there, and there is no quadratic or number field sieve.
- You need guaranteed factorizations: primality is Miller-Rabin (40 rounds on the CPU, 12 fixed bases 2-37 in the GPU kernel), and when the rho or ECM budget runs out the composite is printed as a 'factor' after a warning.
- You need a library or multiplicities: these are CLI programs with global state that print distinct primes only, sorted, on stderr.
- You need maturity: 7 commits (2026-08-28 to 2026-09-01), 1 star, no test suite, MPI scaling never measured on a real cluster.

## How it is fast

It is not faster than its baseline; the design is about GPU parallelism. The CPU path runs one OpenMP task stream over a 12-level {B1, curves} ladder modelled on GMP-ECM's tables (15 to 70 digits), with no barrier between levels and a shared stop flag polled through libecm's stop_asap callback, so all cores stay busy and in-flight curves stop once one thread finds a factor. The GPU rho kernel runs about 8192 warps of independent Floyd walks (one constant c each), computes a double-width square then reduces it (cgbn_sqr_wide + cgbn_rem_wide), and sends each cofactor to the narrowest of nine CGBN widths (128 to 32768 bits). Per the design doc, those two changes cut the 16-digit case from about 37 s to 8.65 s on the GPU, which is still slower than CPU ECM.

## Compared with alternatives

Do not pick it for speed. ECM-ELF is the sibling that beats GMP-ECM (about 3x per curve in stage 1 with AVX-512 IFMA), and CGBN itself or mr_blackwell are better places to get GPU big-integer or Miller-Rabin throughput. Use this repo only as worked example code for CGBN, MPI and libecm orchestration.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CPU program: GMP, GMP-ECM 7.0.6 (libecm), OpenMP. GPU programs: CUDA toolkit (12.9 or 13.2), the author's CGBN fork steleman/nvidia-cgbn installed in /usr/local/include/cgbn (adds signed arithmetic, Ada/Blackwell support and widths up to 256K bits), GMP, OpenMPI 5.0.5; ecmcgbnprimefactorsmpi also needs libecm and pthreads |
| **Minimum toolchain** | GCC with C17 and OpenMP for the CPU program; nvcc from CUDA 12.9 (-arch=sm_89) or 13.2 (sm_120) for the GPU programs |
| **Platforms** | Linux (tested on Fedora 41 and 44, x86-64 hosts); GPU programs on NVIDIA Ada (RTX 4080) and Blackwell (RTX PRO 4500), other GPUs by editing GPU_ARCH |
| **Thread safety** | not applicable as a library (global factor array, CLI only); internally the OpenMP ECM threads each own an ecm_params with a distinct RNG seed, and the pthread workers in the trial-division program keep thread-local hit lists |
| **Drop-in for the baseline** | no |

## Gotchas

- cgbnprimefactors has no ECM fallback: after 7 rho attempts (walk length starts at 200,000 iterations and triples each time) it records the unsplit composite with only a warning, and results go to stderr alongside the warnings.
- ecmcgbnprimefactorsmpi treats every number in the primes file as proven prime and never tests it, so a bad table silently yields wrong factors; whatever the table misses goes to a single-threaded GMP-ECM ladder on rank 0.
- The Makefile hard-codes /usr/bin/gcc, /usr/local/cuda-12.9, sm_89 and /usr/lib64/openmpi, and its CPU link rule puts -lecm -lgmp before primefactors.o, which linkers that default to --as-needed reject. The README's dependency table (GMP-ECM and CUDA rows) does not match the Makefile, and the design PDF's ecmcgbnprimefactorsmpi command line predates the current -f/-t options.
- The README says the author used Claude Opus 5.0 for the Pollard's rho code and for testing and bug finding.

## Known shortcomings

- Not faster: the README's first-party figures put its GPU Pollard rho at 8.7 s against 2 s for CPU GMP-ECM, and the CPU path claims no win over stock GMP-ECM. Tier C, 1 star, last commit 2026-09-01.
- GPU Miller-Rabin uses the fixed bases 2-37 only; cgbnprimefactors has no ECM fallback and prints unsplit composites after a warning; the Makefile puts -lecm -lgmp before the object file, so linkers defaulting to --as-needed reject it; the README dependency table does not match the Makefile.

## Caveats and trade-offs

Does not qualify as faster than its baseline. The README ('Performance reality') and primefactors-design.pdf both say neither GPU program is meant to beat the CPU GMP-ECM path: GPU rho is about 4x slower on a 16-digit factor (8.7 s vs 2 s, derived from page data), 'much slower' below 2^64 because of CUDA/MPI start-up cost, and impractical at 19 or more digits. The CPU program wraps GMP and libecm with its own trial division, Pollard's rho and OpenMP curve-parallel ECM scheduling, but makes no comparison against the stock ecm binary or single-threaded GMP-ECM; its 30/35/40-digit wall-clock figures (about 10.5 s, 20.6 s, 5.7 min) come from an unidentified 32-core box. The design doc's \~37 s to \~8.65 s (\~4.3x) is GPU-vs-GPU tuning; three further GPU 'optimizations' were reverted as net-slower (Brent batched gcd about 2.6x slower, per-instance ILP 2-4x slower, __launch_bounds__ capping). Kept as a record so the shortcoming is documented. The README says the author used Claude Opus 5.0 for the Pollard's rho code and for testing and bug finding. The author's CGBN fork (steleman/nvidia-cgbn) was not examined.

Hobby research code. primefactors.c is arbitrary precision through GMP mpz_t with trial division, Pollard's rho and GMP-ECM curves spread across cores by OpenMP (memory grows with threads times B1). The two CUDA programs (cgbnprimefactors.cu, ecmcgbnprimefactorsmpi.cu) need CUDA, the author's CGBN fork and OpenMPI; GPU rho gains only about sqrt(k) from k parallel walks. Single-machine ECM tops out around 45 digits per the README; MPI scaling was never tested beyond one node.

## Maintenance

Hobby project, MIT, 7 commits ending 2026-09-01: copyable but unpackaged and untested beyond the author's two Fedora machines, catalogued only to record that it does not beat GMP-ECM.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification D, tier now C.
- **Tier reason:** The README gives first-party wall-clock numbers against the CPU GMP-ECM path: the RTX 4080 Pollard's rho takes about 8.7 s for a 16-digit factor vs about 2 s for CPU ECM. Methodology is partial (Makefile flags and GPU model, no benchmark harness, CPU for the comparison not named), so the evidence is C. It shows the GPU programs are slower, and the CPU path claims no win over plain GMP-ECM.
- **Verifier notes:** Reject (not-faster): by the author's own numbers the GPU paths are slower than CPU GMP-ECM, and the CPU path claims nothing over plain GMP-ECM. Under the keep-and-document rule, record the 'not faster' shortcoming. Metadata checked: MIT, 1 star, 0 forks, 7 commits, not a fork, last commit 2026-09-01 (active).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/steleman/primefactors>
  - <https://github.com/steleman/primefactors/commits>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/README.md>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/Makefile>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/primefactors-design.pdf>
- **Sources the enricher read:**
  - <https://github.com/steleman/primefactors>
  - <https://github.com/steleman/primefactors/commits>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/README.md>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/Makefile>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/primefactors-design.pdf>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/primefactors.c>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/cgbnprimefactors.cu>
  - <https://raw.githubusercontent.com/steleman/primefactors/HEAD/ecmcgbnprimefactorsmpi.cu>
  - <https://github.com/steleman/nvidia-cgbn>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/steleman/primefactors`) · [data/wave8/enrich/raw/github_com_steleman_primefactors.json](../../../data/wave8/enrich/raw/github_com_steleman_primefactors.json) (enrichment confidence 0.75)

</details>
