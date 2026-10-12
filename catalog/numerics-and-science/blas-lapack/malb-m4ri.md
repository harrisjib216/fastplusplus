# M4RI (dense GF(2) linear algebra: Method of the Four Russians, Strassen-Winograd, PLE elimination)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `GPL-2.0-or-later` · 🟢 active

> C library for dense matrix arithmetic over GF(2); 2008 paper shows 1.4-1.5x faster multiplication than Magma on Core 2.

| | |
|---|---|
| **Beats** | Magma 2.14 (2.14-14 on the Core 2 Duo, 2.14-13 on the Opteron, per search snippets), the proprietary computer algebra system's asymptotically fast GF(2) matrix multiplication; GAP 4.4 also appears in the tables. None of the listed baselines (OpenBLAS, Intel MKL, Eigen, BLIS) apply because they do not operate on bit-packed GF(2) matrices. |
| **Claimed result** | SNIPPET ONLY (search-engine summaries of the tables in arXiv 0811.1714 / ACM TOMS Algorithm 898; the paper itself could not be opened). M4RI-20080821 vs Magma, 64-bit 2.33 GHz Core 2 Duo: n=10,000 2.210 s vs 1.504 s; n=16,384 8.670 s vs 6.074 s; n=20,000 16.030 s vs 10.721 s; n=32,000 58.730 s vs 43.197 s (about 1.47x, 1.43x, 1.50x and 1.36x, derived from snippet data); GAP 4.4 takes 6.130 s at n=10,000. 64-bit 2.6 GHz Opteron: n=10,000 2.656 s vs 2.490 s (about 1.07x); n=16,384 10.260 s vs 10.490 s; n=20,000 18.156 s vs 17.730 s; n=32,000 67.237 s vs 67.840 s (parity, within about 2% either way). The README quotes only 'considerable performance gains in practice when compared to the previously fastest implementation' for PLE elimination (arXiv 1111.6549), with no numbers. |
| **Workload** | Wall-clock time of dense GF(2) matrix multiplication for square 10,000 and 16,384 dimensions, M4RI-20080821 (M4RM plus Strassen-Winograd) versus Magma, as tabulated in the Albrecht-Bard-Hart multiplication paper (arXiv 0811.1714) according to a search-engine summary; the PLE elimination paper (arXiv 1111.6549) is described in the README abstract as a gain over 'the previously fastest implementation'. |
| **Metric** | latency |
| **Hardware** | Per the search snippet only: 64-bit 2.33 GHz Core 2 Duo and 64-bit 2.6 GHz Opteron (2008-era machines). |
| **Compiler and flags** | Per the search snippet only: GCC 4.3.1 with -O2 on the Opteron and -O2 -msse2 on the Core 2 Duo (not verified). Magma version and its flags were not seen. |
| **Adoption** | 98 stars, 35 forks; adopted into SageMath and packaged for Debian, Fedora and Homebrew according to the README and its history |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/malb/m4ri) · [benchmark](https://arxiv.org/abs/0811.1714) |

## Verdict

Snippet only: search-engine summaries of the Albrecht-Bard-Hart paper (arXiv 0811.1714, ACM TOMS Algorithm 898) report M4RI-20080821 multiplying square GF(2) matrices 1.36-1.50x faster than Magma 2.14 on a 2.33 GHz Core 2 Duo (for example 1.504 s vs 2.210 s at n=10,000), built with GCC 4.3.1 -O2 -msse2, and at parity with Magma (within about 2%) on a 2.6 GHz Opteron. Those are 2008 numbers against a proprietary baseline that cannot be reproduced; the repo's bench/ programs time M4RI only, and the PLE paper (arXiv 1111.6549) claims gains over the previous fastest implementation without numbers on any page opened here.

## Use it when

- Dense GF(2) matrices from hundreds to tens of thousands of rows and columns: cryptanalysis (linear systems from algebraic attacks, linearization), coding theory, Groebner-basis linear algebra over F2 (PolyBoRi-style)
- Rank, row echelon form, kernel or inverse of large bit matrices, where the O(n^3/log n) M4RI and PLE routines beat naive XOR elimination
- Products of large square or rectangular bit matrices, where M4RM plus Strassen-Winograd beats a hand-written word-parallel triple loop
- Linux x86-64 builds, the only platform the README promises to support; SSE2 code paths are used there
- Code already in the SageMath ecosystem, or code that needs the companion M4RIE library for GF(2^e), 2 &lt;= e &lt;= 10

## Skip it when

- Sparse GF(2) systems (LDPC, sieve matrices from factoring): dense bit-packed storage and O(n^2.807) work waste time; use a Wiedemann/Lanczos or structured-Gaussian-elimination code instead
- Many tiny products (64x64 times 64x1, 64x64 times 64x64, Nx64 times 64x64): open issue #10 calls M4RI's performance there 'embarrassingly bad'
- Fields other than GF(2), or floating-point BLAS work: it covers only F2 (GF(2^e) needs the separate M4RIE library)
- Proprietary or permissively licensed products: GPL-2.0-or-later is copyleft
- Windows (MSYS2/MinGW) or macOS deployments that need guaranteed support: the README calls these best effort that 'may disappear any time'; there are no AVX2/AVX-512/GFNI or NEON kernels (GFNI is only a proposal in open issue #36)

## How it is fast

Bit-packing turns 64 GF(2) additions or multiplications into one XOR or AND, and multiplication uses the Method of the Four Russians (Kronrod's method, M4RM): Gray-code tables of all 2^k combinations of k rows of B (up to six tables at once) replace inner products with table lookups and row XORs. Above a cache-derived cutoff it recurses with Strassen-Winograd (O(n^2.807)); elimination uses the M4RI algorithm (O(n^3/log n)) and a block-iterative PLE decomposition that reuses the same tables. Block sizes and cutoffs come from L1/L2/L3 cache sizes detected at configure time, because the authors found memory traffic and data locality, not arithmetic, to be the bottleneck.

## Compared with alternatives

None of the catalogued blas-lapack siblings (OpenBLAS-class GEMMs, BLASFEO, Eigen, faer, fast-matmul) handle GF(2): emulating F2 with 0/1 floats and a mod-2 step costs 32-64x the memory and loses M4RM's table tricks. Pick M4RI whenever the field is GF(2) and the matrices are dense; it is the reference implementation in this niche.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (autotools: autoreconf, ./configure, make; pkg-config file m4ri.pc) |
| **Dependencies** | none required; libpng optional (PNG matrix I/O, on by default if found), OpenMP optional (--enable-openmp), PAPI optional for benchmarks; the bench/ suite vendors libcpucycles and needs python3 to build |
| **Minimum toolchain** | C99 compiler (configure aborts without C99); headers wrap declarations in extern "C" for C++ (not under MSVC) |
| **Platforms** | Linux supported (x86-64 with SSE2 paths, portable 64-bit-word code elsewhere); macOS and Windows MSYS2/MinGW64 best effort; CI builds on ubuntu-latest (with AddressSanitizer), macos-latest and windows-latest |
| **Thread safety** | Not thread-safe by default: a global memory-block cache (MMC) and an mzd_t struct cache are on unless configured with --enable-thread-safe (OpenMP builds turn off the mzd cache only) |
| **Drop-in for the baseline** | no |

## Gotchas

- Cache sizes and the Strassen cutoff (min(sqrt(4\*L3), 4096)) and PLE cutoff are compiled in at configure time; a distro or cross-built binary is tuned for the build machine. Issue #4 reported L3 misdetection causing random failures with OpenMP on some systems; a fix ('Correct L3 Detection', #37) landed in December 2025, and --with-cachesize=L1:L2:L3 overrides detection.
- If the library was built with SSE2, client code must also be compiled with SSE2 enabled, or m4ri.h stops with #error.
- mzd_transpose does not work in place for square matrices (documented only in open issue #5); M4RI's solve_left corresponds to Sage's solve_right (issue #6); the PLUQ specification is flagged as unclear (issue #8, label bug).
- Allocation failure calls m4ri_die(), which prints and abort()s; there are no error codes. Windowed sub-matrices (mzd_init_window) share storage with their parent and need not be word-aligned.

## Known shortcomings

- Raised C to B on the peer-reviewed ACM TOMS Algorithm 898 (arXiv 0811.1714), seen only as search snippets (1.36-1.50x over Magma 2.14 on a Core 2 Duo; parity on an Opteron) because arxiv.org, ar5iv, wrap.warwick.ac.uk and malb.bitbucket.io were blocked. The baseline is Magma, not any listed BLAS; numbers are 2008-era.
- Not thread-safe by default (global MMC and mzd caches unless --enable-thread-safe); open issue #10 says 64x64-class products are 'embarrassingly bad'; cache sizes are fixed at configure time, and issue #4's L3 misdetection gave random OpenMP failures (fixed in #37, Dec 2025). No AVX2, AVX-512, GFNI or NEON kernels (GFNI only proposed, issue #36). The only numbers remain the 2008 snippet-only Magma tables.

## Caveats and trade-offs

No page containing the numbers could be opened: the Bitbucket wiki 'Performance' page returns HTTP 404, malb.bitbucket.io (old website performance.html) returns 403 from the proxy, and arxiv.org, ar5iv.labs.arxiv.org and wrap.warwick.ac.uk (the paper's open-access copy) are egress-blocked. The numbers come from search-result summaries that agree with each other but were not checked against the paper. The multiplication paper is peer reviewed (ACM TOMS Algorithm 898, Vol 37 No 1, 2010, per the ACM listing title in search results). They are 2008 numbers on 2008 hardware against Magma 2.14; M4RI wins 1.36-1.50x on the Core 2 Duo but is at parity with Magma on the Opteron at every size, so the win is CPU-specific, and later Magma and M4RI versions were not compared. The README history (2008/06/13) admits that an earlier Magma comparison on the Core 2 Duo was 'strongly biased' because a Magma build optimised for AMD64 was used on Intel64, and was corrected afterwards. Magma is proprietary, so third parties cannot reproduce the comparison. The repo's bench/ directory (bench_multiplication.c, bench_elimination.c, bench_ple.c, bench_trsm.c, bench_m4rm.c and others, with a vendored libcpucycles-20260625) times M4RI alone and stores no results. Compiler and flags (GCC 4.3.1, -O2 / -O2 -msse2) come from the search agent's snippet and were not re-seen here.

C library for GF(2) only (GF(2^e) is the separate M4RIE library). Uses x86 SSE2 where available and optional OpenMP parallelism (--enable-openmp, described as preliminary); Linux is the supported platform, Windows and macOS are best effort. GPL-2.0-or-later is copyleft. Algorithms: M4RM and Strassen-Winograd multiplication at O(n^log2(7)), PLE factorisation, and M4RI row echelon / inversion at O(n^3/log n).

## Maintenance

Actively maintained (tags 20251206, 20251207 and 20260122, last commit 2026-08-25, CI on Linux/macOS/Windows) and packaged by Debian, Fedora, Homebrew and SageMath; GPL-2.0-or-later, so usable as a linked library but copyleft.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the numbers come from the multiplication paper the README links (arXiv 0811.1714), which search results confirm was published peer-reviewed as ACM TOMS Algorithm 898, Vol 37 No 1 (doi 10.1145/1644001.1644010); three search snippets give consistent tables of M4RI versus Magma 2.14 showing a 1.36-1.50x win on a 2.33 GHz Core 2 Duo. The paper itself is egress-blocked (arxiv.org, ar5iv, wrap.warwick.ac.uk), so not A, and the win does not hold on the Opteron.
- **Verifier notes:** Metadata confirmed (98 stars, 35 forks, 861 commits, last commit 2026-08-25, GPLv2+ per README, GitHub sidebar shows GPL-2.0). Upgraded to B on the peer-reviewed ACM TOMS Algorithm 898 paper, following the ALP/Sputnik snippet-confirmed-paper precedent; a session that can open arXiv 0811.1714 should confirm the tables, flags and CPUs (could reach A since M4RI is public, if the paper states compiler and flags).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/malb/m4ri>
  - <https://github.com/malb/m4ri/commits/master>
  - <https://github.com/malb/m4ri/tree/master/bench>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/README.md>
  - <https://bitbucket.org/malb/m4ri/wiki/Performance>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/README.md>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/m4ri/m4ri.h>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/m4ri/mzd.h>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/m4ri/misc.h>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/m4ri/brilliantrussian.h>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/m4ri/strassen.h>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/m4ri/ple.h>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/m4ri/mmc.h>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/m4ri/m4ri_config.h.in>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/.github/workflows/distcheck.yml>
  - <https://raw.githubusercontent.com/malb/m4ri/HEAD/bench/bench_multiplication.c>
  - <https://github.com/malb/m4ri>
  - <https://github.com/malb/m4ri/issues>
  - <https://github.com/malb/m4ri/issues/4>
  - <https://github.com/malb/m4ri/issues/10>
  - <https://github.com/malb/m4ri/issues/36>
  - <https://github.com/malb/m4ri/commits/master>
  - <https://github.com/malb/m4ri/tags>
  - <https://github.com/malb/m4ri/tree/master/.github/workflows>
  - <https://github.com/malb/m4ri/compare/release-20200125...release-20240729>
  - <https://github.com/malb/blog>
  - <https://raw.githubusercontent.com/malb/blog/HEAD/efficient-multiplication-of-dense-matrices-over-gf2.org>
  - <https://raw.githubusercontent.com/malb/blog/HEAD/efficient-dense-gaussian-elimination-over-the-field-with-two-elements.org>
  - <https://raw.githubusercontent.com/malb/blog/HEAD/block-iterative-ple-decomposition.org>
  - <https://pypi.org/pypi/gf2/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/malb/m4ri`) · [data/wave8/enrich/raw/github_com_malb_m4ri.json](../../../data/wave8/enrich/raw/github_com_malb_m4ri.json) (enrichment confidence 0.6)

</details>
