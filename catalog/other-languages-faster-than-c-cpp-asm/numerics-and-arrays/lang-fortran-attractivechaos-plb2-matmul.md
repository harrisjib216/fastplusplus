# Fortran (gfortran) matmul in plb2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Fortran` · `CC0-1.0` · 🟡 stale

> Naive 1500x1500 double matmul in Fortran (gfortran -O3): 0.51 s against clang-built C's 0.54 s on an Apple M1 in plb2.

| | |
|---|---|
| **Beats** | C (clang 15.0.0, make flags -O3 -fwrapv -flto) 1500x1500 double matmul with the same i-k-j loop order using double\*\* rows |
| **Claimed result** | matmul elapsed seconds on Apple M1: Fortran gfortran 13.2.0 0.51 s versus C clang 15.0.0 0.54 s, about 6% faster (derived from page data). Other compiled languages on the same row: Rust 0.56, Zig 0.56, Nim 0.56, Swift 0.56, D ldc2 0.57, V 0.57, Julia 0.76, Mojo 1.12. Fortran is the only language in the table that beats C on matmul. |
| **Workload** | Multiply two 1500x1500 double-precision matrices with triple-nested loops (no BLAS), one of four plb2 tasks. C (src/c/matmul.c) uses row pointers into one contiguous calloc block with i-k-j order (inner loop over j, c[i][j] += a[i][k] \* b[k][j]); Fortran (src/fortran/matmul.F90) uses column-major explicit-shape dummy arrays with j-k-i order (inner loop over i), the same unit-stride access pattern and the same work. Elapsed wall time includes matrix generation and process startup. |
| **Metric** | throughput |
| **Hardware** | Apple M1 MacBook Pro (elapsed time, hyperfine) |
| **Compiler and flags** | Fortran: gfortran 13.2.0 with FFLAGS=-O3 (src/fortran/Makefile); C: clang 15.0.0 via \$(CC) with CFLAGS=-O3 -fwrapv -flto (src/c/Makefile). Neither side passes -march/-mcpu. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Why it wins** | Not stated by the source. Searcher inference only: Fortran dummy arguments may not alias and arrays are contiguous, so gfortran can vectorize the inner loop without alias checks, whereas the C version indexes through double\*\* rows. |
| **Adoption** | 286 stars; widely cited cross-language benchmark |
| **Last commit** | 2025-01-30 |
| **Links** | [repository](https://github.com/attractivechaos/plb2) · [benchmark](https://github.com/attractivechaos/plb2/blob/master/README.md) |

## Verdict

On an Apple M1 MacBook Pro, hyperfine elapsed time for a naive 1500x1500 double matmul was 0.51 s for gfortran 13.2.0 -O3 against 0.54 s for clang 15.0.0 -O3 -fwrapv -flto C using the same loop nest, about 6% faster (derived from page data); Fortran is the only language in the table ahead of C on this task, with Rust, Zig, Nim and Swift at 0.56 s.

## Use it when

- Writing new dense loop nests over contiguous double arrays (matrix kernels, stencils) where you want alias-free vectorization without sprinkling restrict through C code.
- Projects that already ship gfortran and Fortran numerics, where a hand-written kernel can stay in Fortran at C speed or slightly better.
- As evidence that naive Fortran compiled by gfortran -O3 is at least at parity with clang -O3 C for a simple matmul loop nest on Apple M1 (0.51 s versus 0.54 s; Rust, Zig, Nim and Swift 0.56 s).
- Teaching or comparing loop order: the program shows the column-major j-k-i order that matches C's row-major i-k-j.

## Skip it when

- When you actually need fast matrix multiplication: plb2 deliberately excludes libraries, and a naive triple loop at about 13 GFLOP/s (derived) is not what a blocked BLAS dgemm (OpenBLAS, Accelerate, MKL, BLIS) or Fortran's MATMUL intrinsic is for; use those instead.
- When you expect a dependable language-level win: the margin is about 6% from one machine, and on a contributor's laptop in issue #33 a flat-indexed C version (1.29 s) came within 7% of Fortran (1.21 s), while the as-shipped nested C took 1.58 s; compilers and CPU were not stated.
- Inside a C++ codebase: you add gfortran and libgfortran to the build, need BIND(C) wrappers, and must transpose or swap indices because Fortran arrays are column-major.
- When your C/C++ is built with GCC or uses a flat restrict-qualified buffer: no plb2 row measured gcc-built C, so the comparison against that baseline does not exist.

## How it is fast

The source gives no mechanism; in issue #33 the maintainer only says 'the difference might be related to compiler and CPU'. Both programs do the same 3.375e9 multiply-adds with unit-stride inner loops (about 6.6 G multiply-adds per second at 0.51 s, derived from page data). Plausible contributors, none verified: Fortran forbids aliasing between the INTENT(IN) and INTENT(OUT) dummy arrays, so gfortran can vectorize the inner loop with no runtime overlap check, while clang must assume c[i] and b[k] may overlap; and GCC's -O3 adds -floop-unroll-and-jam, -floop-interchange and -fpredictive-commoning with -ffp-contract=fast as the default (GCC 13 invoke.texi), so the gap may be the GCC backend rather than the language.

## Compared with alternatives

Choose this row over the D matmul entry in kostya/benchmarks (D/gdc 1.505 s against C/gcc 3.034 s, but D calls std.numeric.dotProduct on a transposed matrix) when you want the cleanest same-algorithm, same-access-pattern language comparison at tier A, accepting a far smaller margin. It is a near-tie in the same spirit as the fortran-lang poisson2d entry (4-9%), and neither is a matmul you should deploy; for real speed look at a BLAS or Gaius.jl.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | gfortran and its runtime (libgfortran); no libraries |
| **Minimum toolchain** | gfortran 13.2.0 as measured with FFLAGS=-O3; the code uses ISO_FORTRAN_ENV REAL64 and GET_COMMAND_ARGUMENT (Fortran 2003/2008) plus the GNU extension CALL EXIT |
| **Platforms** | Measured only on an Apple M1 MacBook Pro (macOS); portable Fortran otherwise |
| **Thread safety** | Not applicable; single-threaded program, no shared state beyond its own arrays |
| **Drop-in for the baseline** | no |

## Gotchas

- Compiler confound: the C row is built with \$(CC) (clang 15.0.0 on the Mac, -O3 -fwrapv -flto) and the Fortran row with gfortran 13.2.0 -O3; there is no gcc-built C row and no flang-built Fortran row, so the 6% cannot be attributed to the language. GCC -O3 enables loop unroll-and-jam and interchange that clang's default pipeline does not mirror (inference).
- Single figures from rows timed on different days: the Fortran row was added on 2024-01-04 (commit e21506c), with no variance shown; the maintainer's own hyperfine run in issue #33 gave the C program 540.9 +/- 2.9 ms. The timed matmul.F90 at e21506c differs from current master only in style (ALLOCATE/DEALLOCATE merged by PR #66, checked by diff).
- The C baseline's double\*\* layout is not the cost on the M1: the maintainer's flat-index variant was slower (557.0 +/- 2.5 ms versus 540.9 ms), and PR #53 (C99 version without the double indirection) showed 'no change in timing' on his machine before being closed; on other machines the layout did matter (issue #33 laptop: 1.58 s nested versus 1.29 s flat).
- Both programs compute the same matrices and print the same element (Fortran 1-based (i-j)\*(i+j-2) equals C 0-based (i-j)\*(i+j)), so the comparison is like for like; elapsed time includes process start, matrix generation and the zeroing of c (calloc in C, an explicit array assignment in Fortran).

## Known shortcomings

- About 6% near-tie (0.51 vs 0.54 s) with rows timed on different days; gfortran vs clang confounds language with compiler; mechanism unconfirmed; CC0 without patent grant; both -O3, neither -march.
- Compiler confound: the C row is built with clang 15.0.0 (-O3 -fwrapv -flto) and the Fortran row with gfortran 13.2.0 -O3, with no gcc-built C row and no flang-built Fortran row, so the 6% cannot be attributed to the language. The rows are single figures timed on different days (Fortran added 2024-01-04 in commit e21506c; the timed matmul.F90 differs from master only in style, PR #66). Issue #33 shows the margin is machine-dependent: the maintainer's hyperfine run gave C 540.9 +/- 2.9 ms on the M1, while a contributor's laptop gave nested C 1.58 s, flat C 1.29 s and Fortran 1.21 s. Both sides compute the same matrices; no bug found.

## Caveats and trade-offs

Margin is about 6% (0.51 s versus 0.54 s) on one machine, single figures without variance in the table, and the rows were timed on different days (Fortran timing added 2024-01-04 as plb2 grew through January 2024), so this is a near-tie that may sit within run-to-run noise. Different compiler backends (gfortran versus clang), so the language and the compiler are confounded; no gcc-built C row exists. Both sides are at -O3 and neither uses -march; the C side adds -fwrapv and -flto (no effect expected on a one-file program). Fortran is the only language in the table that beats C on matmul; the README notes Clang already hoists the inner-loop invariants that many other languages cannot. Elapsed wall time includes process startup. CC0-1.0 dedication: no patent grant. Repository last changed 2025-01-30. [retier] Enricher: compiler confound; the C row is built with clang 15.0.0 (-O3 -fwrapv -flto) and the Fortran row with gfortran 13.2.0 -O3, with no gcc-built C row and no flang-built Fortran row, so the 6% cannot be attributed to the language. Issue #33 shows the margin is machine-dependent (maintainer's hyperfine C 540.9 +/- 2.9 ms on the M1; a contributor's laptop gave nested C 1.58 s, flat C 1.29 s, Fortran 1.21 s). The timed matmul.F90 at e21506c differs from master only in style (PR #66); both sides compute the same matrices.

CC0 dedication (no patent grant). Fortran version needs gfortran; plb2 measures a naive triple loop, not tuned BLAS-level matmul.

## Maintenance

Stale but tiny: plb2 is CC0-1.0 (287 stars), last changed 2025-01-30, with PRs such as #77 (Chez Scheme), #79 (Chapel) and #82 (PDL matmul) open since 2024-2025; the Fortran file is a self-contained 70-line program to copy, not a maintained component.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Raised from B: the plb2 README appendix table (Apple M1 MacBook Pro, hyperfine) shows f90:gcc 13.2.0 matmul 0.51 s and c:clang 15.0.0 0.54 s, and the code (src/fortran/matmul.F90, src/c/matmul.c), flags (src/fortran/Makefile FFLAGS=-O3, src/c/Makefile CFLAGS=-O3 -fwrapv -flto), compiler versions and CPU model are all public, which meets A for an independent suite (as kostya-based entries in wave 12). The margin itself is small; see caveats.
- **Verifier notes:** Numbers match the README table; sources and Makefiles confirm the same algorithm and work on both sides (i-k-j row-major versus j-k-i column-major). same_opt_level corrected to true (both -O3, neither -march; the record wrongly implied C had -march). Shortcomings to record: about 6% near-tie on one M1 with rows timed on different days, gfortran versus clang confounds language with compiler backend, mechanism unconfirmed, CC0 has no patent grant.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-02 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/README.md>
  - <https://github.com/attractivechaos/plb2>
  - <https://github.com/attractivechaos/plb2/commits>
  - <https://github.com/attractivechaos/plb2/tree/master/src>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/c/matmul.c>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/c/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/fortran/matmul.F90>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/fortran/Makefile>
  - <https://github.com/attractivechaos/plb2/commits/master/src/fortran>
  - <https://github.com/attractivechaos/plb2/commits/master/src/c>
  - <https://github.com/attractivechaos/plb2/commits/master/README.md>
  - <https://github.com/attractivechaos/plb2/pull/66/files>
- **Sources the enricher read:**
  - <https://github.com/attractivechaos/plb2>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/c/matmul.c>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/c/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/fortran/matmul.F90>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/fortran/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/e21506c/src/fortran/matmul.F90>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/e21506c/src/fortran/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/e21506c/README.md>
  - <https://github.com/attractivechaos/plb2/issues?q=matmul>
  - <https://github.com/attractivechaos/plb2/issues/33>
  - <https://github.com/attractivechaos/plb2/pull/53>
  - <https://github.com/attractivechaos/plb2/pull/66/files>
  - <https://github.com/attractivechaos/plb2/commits/master/src/fortran>
  - <https://github.com/attractivechaos/plb2/commits/master/src/c>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-13/gcc/doc/invoke.texi>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:fortran/attractivechaos/plb2#matmul`) · [data/wave14/enrich/raw/lang_fortran_attractivechaos_plb2_matmul.json](../../../data/wave14/enrich/raw/lang_fortran_attractivechaos_plb2_matmul.json) (enrichment confidence 0.6)

</details>
