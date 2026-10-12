# ECM-ELF (ECM stage 1, AVX-512 IFMA 8-curve batch backend)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C/C++ (GitHub lists C as primary; the AVX-512 kernels are .cpp; CUDA and OpenCL backends also exist)` · `GPL-3.0` · 🟢 active

> AVX-512 IFMA ECM stage 1 running 8 curves per core; 2.3-3x faster per curve than GMP-ECM on Mersenne numbers.

| | |
|---|---|
| **Beats** | GMP-ECM 7.0.6 (ecm-zen3.exe, built on GMP, curve family -param 0); the same table also compares Prime95 v31.04b05 (GWNUM FFT) |
| **Claimed result** | docs/ECM_Montgomery_STAGE1.md section 14.2, M4001, stage 1 only, one thread, per curve: B1=1e5 0.596 s vs GMP-ECM 1.787 s (3.00x faster); B1=1e6 6.264 s vs 15.008 s (2.40x); B1=2e6 13.455 s vs about 30 s (GMP-ECM value scaled, about 2.2x). Section 14.5 size sweep at B1=1e6 (README labels these rows measured, only M5755 and M8527 fitted): M1277 0.979 s vs 2.484 s (2.54x), M2203 2.285 s vs 5.804 s (2.54x), M3001 4.137 s vs 9.586 s (2.32x), M3500 5.164 s vs 11.656 s (2.26x), M4001 6.290 s vs 14.624 s (2.32x); about 1.7x at M5755 and M8527 and about 1.75x at M19701 (all columns fitted). Section 10.4 (earlier, before clock pinning), same-machine GMP-ECM ecm-zen3.exe, B2=B1: M1277 B1=1e5 0.135 vs 0.234 s per curve (1.74x), M1277 B1=1e6 1.418 vs 3.551 s (2.50x), M3001 B1=1e5 0.526 vs 1.148 s (2.18x). Against Prime95 v31.04b05 (a model calibrated on one measured M3001 point, 5.65 s, plus the M4001 B1=1e7 run; the 14.2 Prime95 values at B1 1e5-2e6 are scaled from 1e7): 32.7x at M127, 10.4x at M521, 3.94x at M1277, 1.37x at M3001, 0.90x at M4001, 0.17x at M19701 (fitted); the doc recommends the new code below about 3700 bits and Prime95 above about 6000 bits. |
| **Workload** | Elliptic-curve-method stage 1 only (B2=0 or B2=B1), Suyama sigma Montgomery curves, one thread on one physical core, on Mersenne numbers 2^k-1 (M127 to M19701), per-curve seconds; the SIMD backend runs 8 curves per batch (time divided by 8). Directly measured case: N = M4001 = 2^4001-1 at B1 = 1e5, 1e6 and 2e6. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen AI 9 HX 370 (Strix Point, Zen 5 plus Zen 5c, 256-bit FPU datapath so 512-bit IFMA runs as 2 x 256-bit); clocks pinned at 3990 MHz on the Zen 5 cores (logical CPUs 0-7) and 2995 MHz on Zen 5c; Windows (exe paths). Single-thread numbers stated reproducible to about +-3%. |
| **Compiler and flags** | Own code: MSVC Release build (build_vs18\Release\ecm.exe; README build section says 'Release build (MSVC /O2)'; the Visual Studio version is not stated, build_vs18 implies the VS 18 generator while the README dependency table recommends VS 2022). CMakeLists.txt gives /arch:AVX512 (or -mavx512f -mavx512ifma -mavx512dq on GCC/Clang) to src/cpu/simd_edwards.cpp, simd_mont_ifma.cpp and simd_mont_curve.cpp. Commands (section 14.4): echo (2^4001-1) \| ecm.exe --mont --mont-backend simd --mont-threads 1 -gpucurves 8 --sigma 4242 &lt;B1&gt; 0, versus ecm-zen3.exe -param 0 -c 2 &lt;B1&gt; &lt;B1&gt; (the section 14.1 table writes -c 8). Baseline: GMP-ECM 7.0.6 ecm-zen3.exe from the prebuilt ecm-2025.10.28-win.multiarch package (--enable-asm-redc); a WebSearch snippet places that package on download.mersenne.ca/GMP-ECM (host blocked here); its compiler and flags are not stated. |
| **Adoption** | 5 stars, 0 forks, 264 commits (github.com page, opened 2026-10-03) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/AllogeneSSRD/ECM-ELF) · [benchmark](https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/docs/ECM_Montgomery_STAGE1.md) |

## Verdict

On one pinned 3990 MHz Zen 5 core of a Ryzen AI 9 HX 370 (MSVC Release, /arch:AVX512 on the IFMA files), stage 1 for param-0 curves on M4001 took 0.596 / 6.264 s per curve at B1 = 1e5 / 1e6 against 1.787 / 15.008 s for the prebuilt GMP-ECM 7.0.6 ecm-zen3.exe (3.0x and 2.4x), and a B1 = 1e6 sweep gives 2.26-2.54x for M1277 to M4001. Every input is a Mersenne number, where the code's fold reduction applies, and the Prime95 ratios come from a model anchored on a single measured M3001 run.

## Use it when

- Many ECM stage-1 curves on Mersenne numbers 2^k-1 below about 3700 bits, where the doc measures 2.26-2.54x per core over GMP-ECM 7.0.6 at B1=1e6 (M1277-M4001) and 3.0x at B1=1e5 on M4001.
- Small Mersenne inputs (M127 to M2203) where Prime95's smallest FFT length is oversized: the doc's model puts it 3.9x (M1277) to 32.7x (M127) ahead of Prime95 per curve.
- x86-64 machines with AVX512-F/DQ/IFMA, run with one thread per physical core and at least 8 curves per thread (128 curves to fill 16 cores).
- Pipelines that already hand stage 2 to Prime95 or GMP-ECM and want a faster stage 1 with interoperable save files, checkpoints and resume.

## Skip it when

- General (non-Mersenne) N: the fold domain is off and CIOS is used, which the doc measures 1.8x slower than the fold (section 19.8); section 19.4 gives about 0.85 s/curve for a 2999-bit semiprime at B1=1e5 on one thread (27.1 s for 32 curves), inside the doc's own GMP-ECM range for M3001 at that B1 (0.72-1.15 s/curve), so expect little or no gain (derived from page data; no general-N GMP-ECM comparison is published).
- Mersenne N above about 3760 bits: Prime95's GWNUM FFT wins per the doc's FFT-tier model (about 1.5x at 5755 bits, about 6x at 19701 bits).
- CPUs without AVX-512 IFMA: backend=simd exits with an error and backend=auto falls back to the scalar GMP mpn path, about 5.6 s/curve at M1277, B1=1e5 against 0.135 s for SIMD, far slower than GMP-ECM itself.
- When you need stage 2, P-1/P+1 or a linkable library: this is a stage-1 application only.
- Code that cannot take GPL-3.0, or a Linux/GCC build of the CPU path you need to trust: the documented desktop build is Windows/MSVC/vcpkg, and all published CPU timings are from one Windows laptop.

## How it is fast

All curves in a batch share one exponent s = lcm(1..B1), so eight curves run in lock-step as the lanes of one zmm register per 52-bit limb (radix 2^52, vpmadd52lo/hi) with no divergence. For N = 2^k-1 a Mersenne fold domain replaces Montgomery CIOS reduction, cutting a modular multiply from n(4n+3) to 2n^2 madds (squaring about n(n-1)+2n), and the binary Montgomery ladder keeps the difference point affine so the differential add costs 3M+2S. Multiplication stays schoolbook: the dev doc measured Karatsuba slower at every size up to about 8000 bits and reports the multiply phase at 91-96% of the machine's madd throughput.

## Compared with alternatives

Pick it over primefactors (whose own README says its GPU programs do not beat the CPU GMP-ECM path on hard inputs) and over generic batched Montgomery kernels such as the Truncated batch SIMD AVX512 code when the job is complete ECM stage 1 on Mersenne numbers with saves GMP-ECM and Prime95 can continue. For general N up to about 1000 bits, try AVX-ECM (bbuhrow/avx-ecm, BSD-2-Clause, not yet catalogued; its README claims 1.5-2.5x GMP-ECM throughput) first.

## Integration

| | |
|---|---|
| **Form** | application (CMake-built ecm.exe / ecm_cuda.exe); the IFMA kernels are C++ source files with a C header (source-drop at best) |
| **Dependencies** | GMP, OpenSSL (Crypto and SSL) and an OpenCL ICD, all REQUIRED by CMakeLists.txt for the ecm target; CUDA toolkit plus CGBN for ecm_cuda; optional Pari/GP for --go; Dear ImGui, Direct3D 11 and NVML for the Windows GUI |
| **Minimum toolchain** | CMake 3.20+; Visual Studio 2022 recommended (timed binary built with MSVC /O2 from build_vs18); CMAKE_CXX_STANDARD is commented out, so the minimum C++ standard is not documented; GCC/Clang get -mavx512f -mavx512ifma -mavx512dq on the IFMA files |
| **Platforms** | x86-64 with AVX512-F/DQ/IFMA for the fast path (measured only on an AMD Ryzen AI 9 HX 370, Zen 5); Windows is the documented desktop build; the OpenCL path also targets Linux, macOS and Android |
| **Thread safety** | ifma_ctx_t owns its scratch and is not thread-safe (header comment); the driver gives each worker its own context and hands out 8-curve tasks through an atomic counter, and results are byte-identical across thread counts per the doc |
| **Drop-in for the baseline** | partial — takes N on stdin and positional B1 B2 like GMP-ECM, and its param-0 saves resume in GMP-ECM 7.0.6 and Prime95, but the flags differ (--mont, --mont-backend, -gpucurves, --sigma) and it does stage 1 only |

## Gotchas

- The unit of parallelism is an 8-curve task, so 8 curves use one thread however many cores exist; SMT adds about 10% on the big cores but costs 19% once the whole Zen 5c cluster is loaded, and the README advises leaving affinity unset.
- field=auto uses the fold only when N = 2^k-1 with k &gt;= 64 and otherwise silently uses CIOS; field=mersenne errors on other N. Check the 'field layer :' log line before comparing timings.
- All published timings use hand-pinned clocks (3990 MHz on Zen 5 cores); the doc says the pinned single-thread runs are about 30% faster than earlier unpinned ones, so stock-clock results will differ.
- The GMP-ECM baseline itself varies: section 9.4 logs an earlier GMP-ECM 7.0.6 run on the same machine at about 0.72 s/curve for M3001 at B1=1e5, while section 10.4 measures 1.148 s/curve with ecm-zen3.exe for the same case.

## Known shortcomings

- Tier A (MSVC /O2 /arch:AVX512, Ryzen AI 9 HX 370, exact commands public), but the baseline is a prebuilt public GMP-ECM binary (ecm-zen3.exe) with unknown build flags, accepted under the MKL-baseline precedent. Inputs are Mersenne numbers only, where the folded reduction alone is worth about 2x per the README.
- The GMP-ECM baseline is unstable within the project's own docs: section 9.4 logs GMP-ECM 7.0.6 on the same machine at about 0.72 s/curve (M3001, B1=1e5) while section 10.4 has ecm-zen3.exe at 1.148 s/curve for the same case. General N likely gains nothing: section 19.4 gives 0.85 s/curve for a 2999-bit semiprime on the CIOS path (derived) and the Mersenne fold path is 1.8x faster than CIOS (section 19.8). The scalar fallback is much slower than GMP-ECM; only a Windows/MSVC build is documented.

## Caveats and trade-offs

All GMP-ECM comparisons use Mersenne numbers 2^k-1, where this code switches to a folded-domain reduction that the README says makes 2^k-1 about 2x faster than a general integer of the same size; no comparison on general N is published, and the doc does not show whether GMP-ECM's own special 2^k+-1 arithmetic was active. One author, one laptop-class machine (Ryzen AI 9 HX 370, 256-bit FPU datapath) with hand-pinned clocks, and Prime95 was running on other cores during the section 14 measurements (doc says single-thread numbers reproduce to about +-3%). The section 14.5 footnote says the fit (about 2.98e-7\*k^2 + 3.79e-4\*k s) built from the measured 1277-4001-bit points extrapolates the larger sizes, and the README table marks only M5755 and M8527 as fitted, so the 1277-4001 rows read as measurements; the M4001 row (6.290/14.624 s) differs slightly from section 14.2 (6.264/15.008 s), suggesting a separate run. The 'about 30 s' GMP-ECM figure at B1=2e6 is scaled, not measured; the section 10.4 numbers predate clock pinning; the doc gives -c 8 in section 14.1 and -c 2 in section 14.4 for GMP-ECM. The prebuilt GMP-ECM binary's compiler and flags are unknown. Stage 1 only (stage 2 is handed to GMP-ECM or Prime95). The repo changes daily (2026-10-02 commits are on the GPU stage 2 path) and the numbers, dated 2026-09-24, were not re-run against HEAD. The scalar GMP mpn backend is only a cross-check (about 5.6 s/curve at M1277, B1=1e5, versus 0.135 s/curve for SIMD), so there is no win against raw GMP mpn arithmetic to claim. GPU backends (CUDA CGBN, OpenCL) are not covered by this entry. GPL-3.0.

Stage 1 only (stage 2 is handed to Prime95 or GMP-ECM through compatible .save files). The fast path needs AVX-512 IFMA hardware (explicit error otherwise; auto falls back to a slow scalar mpn backend). Gains come from 8-lane batches, a Mersenne fold domain for N = 2^k-1 (about 2x faster than general N per the README) and affine differential ladder; general N uses Montgomery CIOS. Cost grows about n^1.66 in word count, so Prime95's FFT overtakes it above about 3700 bits. GPL-3.0 copyleft. Windows-first build; Chinese-language README (README.en.md exists). Renamed from OpenCL-ECM.

## Maintenance

Active single-author project (264 commits, last commit 2026-10-02, no issues filed, 5 stars) under GPL-3.0, so usable as a tool but not vendorable into closed code; the benchmark numbers date from 2026-09-24 and were not re-run against HEAD.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/ECM_Montgomery_STAGE1.md sections 14.1-14.5 time the repo's own ecm.exe (SIMD backend, exact command lines in 14.4) against GMP-ECM 7.0.6 ecm-zen3.exe on the same machine, with the CPU named (Ryzen AI 9 HX 370, clocks pinned per section 13), an MSVC Release build (build_vs18\Release; README: MSVC /O2) and /arch:AVX512 on the IFMA translation units in the public CMakeLists.txt. The baseline is a named prebuilt public release binary (like an MKL baseline), so its unstated build flags do not block A; the compiler version is only implied by the build_vs18 directory name.
- **Verifier notes:** Numbers all found on the doc page; the README carries the same section 14.5 table. Main scope limit: the 2.3-3x margin over GMP-ECM is for Mersenne inputs only, where the code uses a special folded reduction. download.mersenne.ca (baseline binary source) was EGRESS_BLOCKED; its existence comes from a WebSearch snippet.
- **Fields the verifier corrected:** `last_commit`, `stars_or_usage`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/docs/ECM_Montgomery_STAGE1.md>
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/README.md>
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/CMakeLists.txt>
  - <https://github.com/AllogeneSSRD/ECM-ELF>
  - <https://github.com/AllogeneSSRD/ECM-ELF/commits>
- **Sources the enricher read:**
  - <https://github.com/AllogeneSSRD/ECM-ELF>
  - <https://github.com/AllogeneSSRD/ECM-ELF/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/README.md>
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/README.en.md>
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/docs/ECM_Montgomery_STAGE1.md>
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/src/cpu/simd_mont_ifma.h>
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/src/cpu/simd_mont_ifma.cpp>
  - <https://raw.githubusercontent.com/AllogeneSSRD/ECM-ELF/HEAD/src/cpu/simd_mont_curve.cpp>
  - <https://github.com/bbuhrow/avx-ecm>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/allogenessrd/ecm-elf`) · [data/wave8/enrich/raw/github_com_allogenessrd_ecm_elf.json](../../../data/wave8/enrich/raw/github_com_allogenessrd_ecm_elf.json) (enrichment confidence 0.7)

</details>
