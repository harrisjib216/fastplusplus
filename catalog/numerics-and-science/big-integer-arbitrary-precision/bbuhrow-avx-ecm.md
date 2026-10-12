# avx-ecm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🔴 abandoned

> AVX-512 command-line ECM factoring program running 8 or 16 curves per thread; about 1.5-2.5x GMP-ECM curve throughput below \~1000 bits.

| | |
|---|---|
| **Beats** | GMP-ECM (the ecm program, built on GMP) |
| **Claimed result** | about 1.5 to 2.5 times the throughput (curves/sec) of GMP-ECM, for numbers up to a thousand bits or so (README, 'has been observed'). README adds that large numbers are more efficient with GMP-ECM because AVX-ECM does not use sub-quadratic multiplication. |
| **Workload** | Elliptic Curve Method factoring: curves per second for stage 1 and stage 2 on general inputs up to about 1000 bits, AVX-512 8-way (52-bit digits) or 16-way (32-bit digits) vector arithmetic per thread. |
| **Metric** | throughput |
| **Compiler and flags** | README names icc or gcc 7.3.0 or newer, e.g. 'make COMPILER=gcc730 SKYLAKEX=1' (KNL=1 for Knights Landing). The Makefile uses -O3 plus -march=skylake-avx512 (SKYLAKEX=1), -march=icelake-client -DIFMA (ICELAKE=1) or -march=tigerlake -DIFMA (TIGERLAKE=1); the IFMA options were added in a November 2020 commit and are not in the README. No flags or build are tied to the quoted ratio. |
| **Adoption** | 8 stars; discussed on mersenneforum.org thread 25056 |
| **Last commit** | 2021-03-09 |
| **Links** | [repository](https://github.com/bbuhrow/avx-ecm) · [benchmark](https://github.com/bbuhrow/avx-ecm) |

## Verdict

The only checked claim is the README's first-party statement of about 1.5 to 2.5 times GMP-ECM's curves per second for inputs up to about 1000 bits on AVX-512 CPUs, with no table, CPU model, GMP-ECM version or flags. Forum numbers (about 2x with 1 thread on a Xeon Gold 5122; a search summary also quotes 900-bit t35 at 2.78 s versus GMP-ECM 7.0.4 at 10.04 s per curve) were seen only as search snippets from mersenneforum.org, which is blocked here, and are unverified.

## Use it when

- Running many ECM curves (t30-t60 style work) on composites of roughly 200-1000 bits on Skylake-X, Cascade Lake, Ice Lake, Tiger Lake or later AVX-512 x86-64 CPUs.
- Batch stage 1 on AVX-512 hardware followed by GMP-ECM stage 2 from the savefile, when you want GMP-ECM's faster stage 2 but higher stage 1 throughput.
- Factoring Mersenne-like or 2^n+-c inputs, where the special reduction path applies.
- Choosing DIGITBITS=32 for sizes just above a 208-bit step, since the 32-bit build steps in 128 bits and can have higher throughput there.

## Skip it when

- CPUs without AVX-512 (all AVX2-only Intel and pre-Zen 4 AMD parts, and all ARM): the program targets AVX-512 intrinsics only.
- Inputs well above about 1000 bits: the README says GMP-ECM wins because this program has no sub-quadratic multiplication.
- Single-curve or latency-bound work: the speedup comes from running 8 or 16 curves together per thread.
- Production use that needs maintenance or bug fixes: the standalone repo's last commit is 2021-03-09; its one issue (a SIGSEGV in vecsqrmod52 reported from a YAFU build) was closed with no visible reply. The maintained copy lives inside YAFU (factor/avx-ecm).
- Embedding as a library: there is no documented API; the Makefile archives the objects (including main.c) into libavxecm.a only to link the program.

## How it is fast

Each AVX-512 lane carries a different curve over the same modulus, so Montgomery multiplication and squaring (vecmulmod52/vecsqrmod52) run 8 curves at once with 52-bit digits in 64-bit lanes (16 curves with DIGITBITS=32); ICELAKE/TIGERLAKE builds add -DIFMA for the 52-bit multiply-add instructions. Stage 1 uses Montgomery-form curves with Suyama sigma parametrization and Montgomery's PRAC Lucas chains; stage 2 is the standard continuation with pairing. Inputs of the form 2^n-1, 2^n+1 or 2^n-c switch to special Mersenne/pseudo-Mersenne reduction instead of REDC. Work is spread over threads with pthreads.

## Compared with alternatives

Pick it over ECM-ELF when you need a complete ECM (stage 1 and stage 2, multi-threaded, savefiles for GMP-ECM) on generic inputs rather than a stage 1 IFMA backend benchmarked on one Mersenne number, and over primefactors when you have AVX-512 CPUs rather than an NVIDIA GPU. For general big-integer arithmetic (not factoring), the GMP-replacement siblings such as FLINT or mp++ are the relevant entries; this program only does ECM.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | GMP (-lgmp), pthreads, libm; Intel builds also link MKL (-mkl) |
| **Minimum toolchain** | README: gcc 7.3.0 or icc (only these tested); MinGW64/MSYS2 supported via COMPILER=mingw |
| **Platforms** | x86-64 with AVX-512 (SKYLAKEX=1, KNL=1 for Knights Landing, ICELAKE=1 or TIGERLAKE=1 for IFMA); Linux and Windows (MinGW) |
| **Thread safety** | not documented; multi-threaded internally with pthreads, but the header defines process-wide globals (MAXBITS, NWORDS, NBLOCKS, lcg_state) sized for one input per run |
| **Drop-in for the baseline** | partial: different command line from GMP-ECM's `ecm`, but the stage 1 savefile is resumable by GMP-ECM stage 2 |

## Gotchas

- Run time is constant within 208-bit steps (128-bit with DIGITBITS=32): a 417-bit input costs the same as a 623-bit one, so the speedup over GMP-ECM depends strongly on where the input falls in a step.
- The Makefile hard-codes the author's GMP paths (/sppdg/scratch/..., ../../gmp-6.2.1) and a gcc-7.3.0 binary name; edit INC/LIBS before building. The IFMA build options (ICELAKE=1, TIGERLAKE=1) exist in the Makefile but not in the README.
- avx_ecm.h defines globals without extern (uint32_t MAXBITS; NWORDS; NBLOCKS; uint64_t \*lcg_state) in a header shared by several .c files; GCC 10+ defaults to -fno-common, so a link with multiple-definition errors is likely unless -fcommon is added (inferred from the source, not tested).
- The repo ships prebuilt Windows binaries (avx-ecm-32.exe, avx-ecm-52.exe, avx-ecm-52-icc-static) of unstated build provenance; prefer building from source.

## Known shortcomings

- Tier C: the README's '1.5 to 2.5x GMP-ECM' is first-party with no CPU stated; the Xeon Gold 5122 numbers live on mersenneforum (blocked). Last commit 2021-03-09, abandoned.
- Issue #1 (SIGSEGV in vecsqrmod52 on a YAFU build) closed with no visible reply. avx_ecm.h defines the globals MAXBITS, NWORDS, NBLOCKS and lcg_state without extern, so a GCC 10+ (-fno-common) link likely fails (inferred from source, not tested); the Makefile hard-codes the author's GMP paths; prebuilt .exe files sit in the repo. A mersenneforum post (blocked, snippet only) gives 2.78 s/curve vs GMP-ECM 7.0.4 at 10.04 s/curve on a 900-bit t35 (about 3.6x). The maintained copy lives in bbuhrow/yafu (factor/avx-ecm, commits through 2026-08-31).

## Caveats and trade-offs

README ratio is a first-party 'has been observed' range with no table, CPU model, GMP-ECM version or flags, and no benchmark script in the README. The mersenneforum thread (www.mersenneforum.org is blocked here) was seen only as a search snippet, which says about 2x GMP-ECM throughput with 1 thread on a Xeon Gold 5122 and, for one input size, 16 simultaneous 512-bit curves in 18.7 s (1.17 s/curve) versus GMP-ECM at 1.72 s/curve (ratio about 1.47, derived from snippet data); the snippet could not be opened, so treat those as unverified. The comparator is GMP-ECM, not GMP itself, so it only loosely matches the listed GMP/MPFR baselines. Last commit 2021-03-09 (repo inactive for over 5 years). Newer GMP-ECM releases and AVX-512 downclocking were not measured.

Needs AVX-512 (Skylake-X, Knights Landing, or IFMA on Ice Lake/Tiger Lake). Curves run in constant-time steps of 208 bits (128 bits with DIGITBITS=32), so 417-bit and 623-bit inputs cost the same. No sub-quadratic multiplier, so it loses to GMP-ECM on large inputs. Stage 2 is the standard continuation with pairing (B2 = 100 x B1 by default). It writes a stage 1 savefile that GMP-ECM stage 2 can resume. Multi-threaded with pthreads. Not a library: command-line program.

## Maintenance

Standalone repo abandoned since 2021-03-09 (34 commits, 8 stars) but BSD-2-Clause and small enough to vendor; active development continued inside bbuhrow/yafu under factor/avx-ecm (commits through 2026-08-31, with added Karatsuba and AVX-512 P-1 files), which is the better source today.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README states 'about 1.5 to 2.5 times the throughput (curves/sec) of GMP-ECM, for numbers up to a thousand bits or so' as a first-party observation with no table, CPU model, GMP-ECM version or benchmark script; C.
- **Verifier notes:** README text matches the record. Metadata confirmed on github.com: BSD-2-Clause (LICENSE file read), 8 stars, 0 forks, not a fork, 34 commits, last commit 2021-03-09, so abandoned is correct. mersenneforum numbers in caveats remain snippet-only (host blocked; not retried).
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/README.md>
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/LICENSE>
  - <https://github.com/bbuhrow/avx-ecm>
  - <https://github.com/bbuhrow/avx-ecm/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/README.md>
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/avx_ecm.h>
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/main.c>
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/ecm.c>
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/test.csh>
  - <https://raw.githubusercontent.com/bbuhrow/avx-ecm/HEAD/test_inputs.txt>
  - <https://github.com/bbuhrow/avx-ecm>
  - <https://github.com/bbuhrow/avx-ecm/issues?q=is%3Aissue>
  - <https://github.com/bbuhrow/avx-ecm/issues/1>
  - <https://github.com/bbuhrow/yafu>
  - <https://github.com/bbuhrow/yafu/tree/master/factor/avx-ecm>
  - <https://github.com/bbuhrow/yafu/commits/master/factor/avx-ecm>
  - <https://raw.githubusercontent.com/bbuhrow/yafu/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bbuhrow/avx-ecm`) · [data/wave8/enrich/raw/github_com_bbuhrow_avx_ecm.json](../../../data/wave8/enrich/raw/github_com_bbuhrow_avx_ecm.json) (enrichment confidence 0.6)

</details>
