# sve-string-routines-benchmarks (Arm SVE strcpy, strncpy, strcmp, strncmp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Assembly (AArch64 SVE) with a C harness` · `LGPL-3.0 (repository LICENSE and harness sources); the routine sources derived from Arm optimized-routines keep Arm's header 'SPDX-License-Identifier: MIT OR Apache-2.0 WITH LLVM-exception' (checked in string/aarch64/new/strcpy-sve.S)` · 🟡 stale

> Research SVE assembly for strcpy, strncpy, strcmp and strncmp that times 1.3-1.6x faster than glibc on Graviton3E, but drops page-fault safety.

| | |
|---|---|
| **Beats** | GNU libc 2.39 string routines (strcpy, strncpy, strcmp, strncmp, strlen, memcpy as selected on Graviton3E) and the Arm Optimized Routines 23.01 SVE versions |
| **Claimed result** | README: the proposed SVE implementations 'never' regress against Arm optimized-routines and 'are competitive with their GNU libc counterparts, namely: strcpy, strncpy, strcmp and strncmp'. Derived from page data (raw .dat median runtimes, glibc time divided by proposed time, geometric mean over buffer sizes, aligned/unaligned): 64 B to 512 MiB strcpy 1.64x/1.61x, strncpy 1.40x/1.39x, strcmp 1.37x/1.32x, strncmp 1.45x/1.43x; 1 to 128 B strncpy 1.63x/1.58x, strcpy 1.32x/1.13x (unaligned dips to 0.37x at some lengths), strncmp 1.19x/1.18x, strcmp 1.13x/1.13x (as low as 0.55x at some short lengths). Against Arm optimized-routines 23.01 at 64 B to 512 MiB (derived): strcpy 2.8x, strlen 3.0x, strcmp 1.8x. The README lists memcpy, memcmp, strlen, strnlen, strchr and strrchr as inconclusive (memcpy geomean 0.76x of glibc at full sizes, strlen 0.94x). On NVIDIA Grace (results/raw/Grace, labelled glibc 2.34, derived, aligned full range) the gains shrink: strcpy 1.06x, strcmp 1.01x, strncmp 1.35x, strncpy 1.35x. |
| **Workload** | Median per-call runtime (101 samples, each the average of an inner repeat loop, after warm-up calls, hot cache, CLOCK_MONOTONIC_RAW) and bandwidth of string routines on random alphanumeric buffers: short strings 1 to 128 B in steps of 1, and a full range of 24 sizes doubling from 64 B to 512 MiB (the README says 128 B, the .dat files start at 64 B), aligned and unaligned allocations, on an AWS Graviton3E. |
| **Metric** | throughput |
| **Hardware** | AWS Graviton3E (hpc7g.16xlarge, Neoverse V1 with SVE); the latest commit message says NVIDIA Grace results were added (results/raw/Grace folder exists, not read) |
| **Compiler and flags** | GCC 12.3.0 on kernel 6.2.0-1018-aws; CMake C11 build with target_compile_options -march=armv8.4-a+sve and no optimization level (CMAKE_BUILD_TYPE Release is commented out, so the C harness builds at GCC's default -O0); the measured routines are hand-written .S files, so the driver flags matter little; -DSHORT_STRS, -DFULL_SIZE_RANGE, -DALIGNED_ALLOCS and -DCMP_LIBC select the modes |
| **Adoption** | 0 stars; research project of UVSQ LI-PaRAD with SiPearl and Eviden (EMOPASS); the authors say it is worth merging into Arm optimized-routines and glibc |
| **Last commit** | 2024-05-29 |
| **Links** | [repository](https://github.com/dssgabriel/sve-string-routines-benchmarks) · [benchmark](https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/results/README.md) |

## Verdict

On an AWS Graviton3E (hpc7g.16xlarge, kernel 6.2.0-1018-aws, harness built with GCC 12.3.0; glibc version labelled 2.39 but unconfirmed), median hot-cache per-call times in the raw .dat files give geomean speedups over glibc of 1.64x strcpy, 1.40x strncpy, 1.37x strcmp and 1.45x strncmp from 64 B to 512 MiB (aligned), and 2.8x, 3.0x and 1.8x over AOR 23.01 SVE strcpy, strlen and strcmp. On NVIDIA Grace the glibc gains shrink to about 1.0-1.35x. The routines measured are not fault-safe, and the strncpy is non-conforming.

## Use it when

- Studying why INCx-based SVE loops underperform on Neoverse V1 (Graviton3/3E) and testing the CNTx+ADD rewrite in your own SVE kernels.
- Benchmarking your own AArch64 string routines: the harness compares any routine against glibc or AOR across 1-128 B and 64 B-512 MiB, aligned and malloc-aligned.
- Internal code on Graviton3-class hardware where every string is known to sit in a buffer with at least one vector length (32 bytes on Graviton3) of readable memory after its terminator, and strncpy padding is not needed.

## Skip it when

- As a general libc replacement: the new strcpy, strcmp and strlen do unaligned full-vector LD1B loads with no first-fault or alignment step, so a string that ends within one vector of an unmapped page can raise SIGSEGV. glibc avoids this by aligning loads down to 16 bytes (bic src, srcin, 15), and AOR avoids it with LDFF1B.
- Anywhere strncpy semantics matter: the new strncpy ignores n on its first vector and does no zero padding (details under gotchas).
- On Neoverse V2 (NVIDIA Grace): the repo's own Grace data shows strcpy only 1.06x and strcmp 1.01x over glibc, so the gain is largely a Neoverse V1 quirk.
- Short unaligned strings: some lengths are up to 2.7x slower than glibc (strcpy dips to 0.37x).
- Non-SVE AArch64 or other ISAs: the routines need SVE (built with -march=armv8.4-a+sve).

## How it is fast

On Neoverse V1 the authors found SVE INCB/INCP loop-offset increments slow. They read the vector length once with CNTB and advance the offset with a plain ADD. They also removed the first-fault machinery (SETFFR, LDFF1B, RDFFRS and the partial-vector fallback path) that Arm's versions use. Each routine becomes a tight loop: full-vector LD1B, CMPEQ/CMPNE against zero, B.ANY or B.NONE, then BRKA/BRKB and LASTA to finish.

## Compared with alternatives

Pick it only as a reference for the Neoverse V1 INCx-versus-CNTx+ADD finding. For production AArch64 string functions, Arm Optimized Routines (its fault-safe upstream) or glibc are the safer choice. Among siblings it is the only one with public raw data comparing SVE string routines against both glibc and AOR on Graviton3E and Grace.

## Integration

| | |
|---|---|
| **Form** | source-drop (AArch64 SVE .S files with a C benchmark driver built by CMake) |
| **Dependencies** | none for the routines (they include the repo's asmdefs.h); the harness needs CMake 3.16+ and libm |
| **Minimum toolchain** | C11 compiler and assembler with SVE support (results built with GCC 12.3.0 and -march=armv8.4-a+sve) |
| **Platforms** | AArch64 with SVE only (measured on AWS Graviton3E and NVIDIA Grace) |
| **Thread safety** | Stateless leaf routines with no shared state; reentrant |
| **Drop-in for the baseline** | partial: same C signatures as strcpy/strncpy/strcmp/strncmp under new_\* names, but not safe to substitute for glibc because of the page-crossing loads and the strncpy semantic bugs |

## Gotchas

- Correctness bug (code reading): new_strncpy_aarch64_sve sets p0 with PTRUE and only applies WHILELO after the first vector. When n is less than the vector length it writes up to the terminator or a full vector regardless of n, so it can write past dst+n. It never zero-fills when src is shorter than n, and with n == 0 it still writes. The benchmark always passes n == strlen(src), so none of this shows up in the numbers, and the DEBUG-only check (strncmp(src, dst, n) == 0) would not catch it either.
- Memory-safety flaw behind the AOR comparison: the 2.8x (strcpy), 3.0x (strlen) and 1.8x (strcmp) gains over Arm Optimized Routines come partly from deleting the LDFF1B/RDFFRS first-fault path, which exists so that reads past the terminator cannot fault. The README says the FFR-free path is used only 'where the whole vector is known to be valid', but the code never checks this and uses unaligned full-vector LD1B from the first byte. The benchmark's malloc'd buffers always have mapped memory after the string, so the hazard never shows.
- Harness details: the C driver builds at GCC's default -O0 (CMAKE_BUILD_TYPE Release is commented out), so each timed call carries a fixed loop and indirect-call overhead that is a sizeable share of the roughly 2 ns short-string timings (it dilutes ratios rather than inflating them). The 'median' is sorted[nsamples/2 + 1] (the 52nd of 101 samples), and the printed SPEEDUP column uses means, not medians. Warm-up calls only the libc routine, and the baseline always runs first. 'Unaligned' mode is plain malloc rather than aligned_alloc(64), not arbitrary byte misalignment.
- The 'GNU libc 2.39' label is hard-coded in src/main.c, and the stpcpy build of new strcpy-sve.S (BUILD_STPCPY) uses predicate p2, which that routine never initialises (not built by default).

## Known shortcomings

- Full range starts at 64 B; on Grace the wins shrink to strcpy 1.06x and strcmp 1.01x (Neoverse V1-specific); the glibc 2.39 label is hard-coded; the harness is built at -O0 and its correctness asserts are DEBUG-only (never on); the .S files keep the Arm MIT OR Apache-2.0 WITH LLVM-exception header.
- Enricher (code reading): the new strcpy/strcmp/strlen dropped the LDFF1B first-fault path and use unaligned full-vector LD1B with no alignment step, so a string ending near an unmapped page can SIGSEGV (glibc aligns its loads, AOR uses LDFF1B), meaning the 2.8x/3.0x/1.8x gains over AOR partly come from removed fault safety; the new strncpy's first vector ignores n (writes past dst+n when n is below the vector length), has no zero padding and writes when n==0, never exercised because the benchmark passes n == strlen; the driver is built -O0, the median index is off by one and the stpcpy variant uses an uninitialised p2. Retiered to C, reference only.

## Caveats and trade-offs

Benchmark is by the authors of the new routines (research group, not independent). Hot-cache repeated calls with warm-up, so cold-cache and branch-predictor effects are not covered. The win comes from replacing SVE INCx with CNTx plus ADD, a Neoverse V1 latency issue: on NVIDIA Grace (Neoverse V2) the same harness shows strcpy 1.06x and strcmp 1.01x over glibc. glibc runs its own NEON/generic implementations on Graviton3E (the README mentions the NEON strcmp), not SVE ones. The 'GNU libc 2.39' name is a hard-coded label in src/main.c; the kernel 6.2.0-1018-aws suggests an Ubuntu release whose stock glibc is older, so the measured glibc version is not confirmed. Correctness asserts in src/main.c run only under -DDEBUG, which the CMakeLists never adds (its 'EQUAL Debug' test is a numeric comparison), so the timed builds do not check results. Short unaligned strcpy has lengths where the new routine is up to 2.7x slower than glibc (the README acknowledges drops). The ratios are derived by the reporter from results/raw/G3E/\*/\*.dat; the README itself only gives qualitative statements, plots and a truncated sample table. One size in the unaligned full-range strncpy data lacks a usable pair (23 of 24 sizes usable). [retier] Proposed routines lack first-fault loads and alignment (possible SIGSEGV near page ends); strncpy bounds and padding bugs unexercised by the harness; -O0 driver; median index off by one; stpcpy variant uses uninitialised p2

AArch64 with SVE only (Neoverse V1/V2, A64FX, Grace). The change replaces INCx loop-offset increments with CNTx plus ADD and drops FFR-dependent instructions in the full-vector path; it needs one more register. Some unaligned short-string lengths are slower than glibc (strcpy ratio down to 0.37x at one size, strcmp down to 0.55x). The code is a benchmark harness with the routines under string/aarch64/new, not a packaged library.

## Maintenance

Stale research code (last commit 2024-05-29, 0 stars, LGPL-3.0 harness with Arm's MIT OR Apache-2.0 headers on the routines); one search found no upstreamed version in glibc or AOR, and the page-fault and strncpy defects mean it should be treated as a reference for the CNTx+ADD idea, not copied into production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** results/README.md and the raw .dat files under results/raw/G3E compare the proposed SVE routines with GNU libc and Arm optimized-routines 23.01; the harness and routines are public (src/bench.c, src/driver.c, src/main.c, string/aarch64/new/\*.S, CMakeLists.txt with -march=armv8.4-a+sve), the compiler (GCC 12.3.0) and CPU (AWS Graviton3E, hpc7g.16xlarge) are stated. I re-derived every quoted geomean from the .dat median runtimes and they match.
- **Retiered** A to C: Enricher (2026-10-12): correctness bugs behind the measured numbers. The proposed strcpy/strcmp/strlen drop the first-fault LDFF1B path for unaligned full-vector LD1B loads with no alignment step, so they can fault on strings ending near an unmapped page while glibc and AOR stay safe, which means part of the measured gain is removed fault safety; the proposed strncpy ignores n in its first vector, omits zero padding and writes when n==0 (unexercised because the benchmark passes n == strlen); the driver is built at -O0 and the median index is off by one. Hot-path correctness-bug precedent; reference only.
- **Verifier notes:** Confirmed at A; every quoted geomean reproduces from the .dat files. Added the Grace cross-check (gains largely vanish on Neoverse V2 for strcpy/strcmp), the unverified glibc 2.39 label, the -O0 harness and DEBUG-only correctness checks, and the per-file Arm licence on the routines. Stale (last commit 2024-05-29), 0 stars.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `license`, `caveats`, `usability`
- **Shortcomings recorded by:** verifier batch-48 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/results/README.md>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/string/aarch64/new/strcpy-sve.S>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/src/bench.c>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/src/driver.c>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/results/raw/G3E/full/align/strcpy.dat>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/results/raw/G3E/full/noalign/strncpy.dat>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/results/raw/G3E/shrt/noalign/strcpy.dat>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/results/raw/Grace/full/align/strcpy.dat>
  - <https://github.com/dssgabriel/sve-string-routines-benchmarks>
  - <https://github.com/dssgabriel/sve-string-routines-benchmarks/commits>
  - <https://github.com/dssgabriel/sve-string-routines-benchmarks/tree/main/results/raw/G3E>
  - <https://github.com/dssgabriel/sve-string-routines-benchmarks/tree/main/results/raw/G3E/full>
  - <https://github.com/dssgabriel/sve-string-routines-benchmarks/tree/main/string/aarch64>
- **Sources the enricher read:**
  - <https://github.com/dssgabriel/sve-string-routines-benchmarks>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/results/README.md>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/src/driver.c>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/src/bench.c>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/src/utils.c>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/string/aarch64/new/strcpy-sve.S>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/string/aarch64/new/strncpy-sve.S>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/string/aarch64/new/strcmp-sve.S>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/string/aarch64/new/strncmp-sve.S>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/string/aarch64/new/strlen-sve.S>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/string/aarch64/baseline/strcpy-sve.S>
  - <https://raw.githubusercontent.com/dssgabriel/sve-string-routines-benchmarks/HEAD/string/aarch64/baseline/strcmp-sve.S>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/aarch64/strlen.S>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/aarch64/strcpy.S>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/aarch64/strcmp.S>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/dssgabriel/sve-string-routines-benchmarks`) · [data/wave13/enrich/raw/github_com_dssgabriel_sve_string_routines_benchmarks.json](../../../data/wave13/enrich/raw/github_com_dssgabriel_sve_string_routines_benchmarks.json) (enrichment confidence 0.8)

</details>
