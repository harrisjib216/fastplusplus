# bc and dc (Gavin Howard)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> POSIX bc/dc in C, plus the bcl library; its bignum math beats GNU bc 1.07.1, its interpreter loop does not.

| | |
|---|---|
| **Beats** | GNU bc 1.07.1 |
| **Claimed result** | With -O2 and no LTO (wall time, GNU bc vs this bc): addition 2.54 s vs 0.88 s, multiplication 7.15 s vs 2.20 s, division 3.36 s vs 1.61 s, power 11.30 s vs 0.73 s, timeconst.bc 16.71 s vs 13.16 s. With -O3 -flto -march=native: power 11.08 s vs 0.71 s, multiplication 7.01 s vs 1.59 s. Slower on a plain for-loop script (16.60 s GNU vs 22.76 s this bc at -O2). |
| **Workload** | bc scripts run through tests/script.sh (add, subtract, multiply, divide), 1234567890^100000, a patched timeconst.bc script and two 100,000,000-iteration loop scripts; best of four runs, wall-clock seconds. |
| **Metric** | throughput |
| **Hardware** | x86_64 machine running Gentoo Linux; CPU model not stated |
| **Compiler and flags** | clang 9.0.1; both bc builds compiled with the same flags: -O2 without LTO, then -O3 -flto -march=native, then -O3 -flto. |
| **Adoption** | 253 stars, 42 forks, 6,072 commits; per the README it is the system bc in FreeBSD, macOS and Android (AOSP external/bc) and in several Linux distributions, and it is packaged in Fedora |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/gavinhoward/bc) · [benchmark](https://github.com/gavinhoward/bc/blob/master/manuals/benchmarks.md) |

## Verdict

First-party manuals/benchmarks.md: bc 3.0.0 vs GNU bc 1.07.1, both built with clang 9.0.1 at -O2 (then -O3 -flto -march=native and -O3 -flto) on an unnamed x86_64 Gentoo machine, best of four time -p runs. 1234567890^100000 took 0.73 s vs 11.30 s (15.7x user time); print-heavy add/multiply/divide scripts and a patched Linux timeconst.bc loop were 1.19x-2.23x faster by user time, while a 100M-iteration for-loop was 37% slower.

## Use it when

- Shell scripts or build steps that call bc for large-number math (big powers, products of numbers with tens to millions of digits): the 1234567890^100000 test ran 15.7x faster than GNU bc in user time.
- Replacing GNU bc where you also want dc, extra built-ins (abs, divmod, scientific notation input/output, a seedable PRNG) and a parser that accepts code GNU bc rejects.
- Embedding decimal arbitrary-precision arithmetic in a C or C++ program via bcl when GMP's binary representation or LGPL licence is unwanted (BSD-2-Clause, pure C99, no dependencies besides pthreads).
- Windows 10+ builds of bc/dc from a Visual Studio solution, which GNU bc does not provide.

## Skip it when

- Loop-heavy scripts with little math: the 100,000,000-iteration for-loop was 37% slower than GNU bc at -O2 (22.76 s vs 16.60 s) and still 12% slower with -O3 -flto.
- As a general high-performance bignum engine: it is decimal, its division is schoolbook Algorithm D and its fastest multiplication is Karatsuba (no FFT/Toom), and no comparison against GMP or MPFR is published.
- If you need fresh, independent performance numbers: the only published comparison is bc 3.0.0 from 2019 on an unnamed x86_64 CPU; 7.x has no published GNU bc comparison.
- Windows 7 and older: issue #98 (open, May 2026) says builds after 5.2.5 hang on input there; only Windows 10+ is supported.
- Interrupting library calls with signals: bcl is not async-signal-safe; the manual says to run long calculations in a separate thread instead.

## How it is fast

Numbers are stored as limbs holding 9 decimal digits (base 10^9 in int_least32_t on 64-bit; 4 digits on 32-bit) instead of GNU bc's one digit per char, so every operation touches far fewer limbs. Multiplication switches from schoolbook to Karatsuba at BC_NUM_KARATSUBA_LEN (default 32 limbs, tunable with scripts/karatsuba.py); power is exponentiation by squaring on top of that; division is Knuth Algorithm D. The interpreter itself is split into many small cross-file functions, so it needs -O3 -flto to inline them and is still slower than GNU bc on math-free loops.

## Compared with alternatives

No sibling is a bc: the catalogued siblings (LuaJIT, PyPy, Wren and others) speed up general scripting languages, while this one only wins on bc's arbitrary-precision math. Pick it when the workload is a bc/dc script or an embedded decimal bignum calculation, and pick a sibling interpreter when the cost is in control flow rather than math.

## Integration

| | |
|---|---|
| **Form** | static lib (bcl, built as bin/libbcl.a with ./configure.sh -a) or standalone bc/dc executables |
| **Dependencies** | none for bc/dc; bcl needs -lpthread on POSIX; optional editline/readline and NLS |
| **Minimum toolchain** | C99 compiler on a POSIX 2008 + XSI system, or Visual Studio MSBuild on Windows 10+; author recommends clang with -O3 -flto |
| **Platforms** | Linux, FreeBSD, OpenBSD, NetBSD, macOS, Solaris, AIX, HP-UX (no history), Windows 10+; 9 digits per limb on 64-bit longs, 4 on 32-bit |
| **Thread safety** | bcl is documented MT-Safe with per-thread initialization (bcl_init per thread) and thread-local contexts; numbers must not cross threads (pass bcl_string() output instead); not async-signal-safe |
| **Drop-in for the baseline** | partial — documented as a drop-in POSIX bc and runs GNU extensions, but output wrapping, length() results and some parse behaviour differ from GNU bc by design, and dc lacks the ! command |

## Gotchas

- Harness flaw: the add/subtract/multiply/divide benchmarks run tests/script.sh with -lq and print every result (about 0.98 to 1.96 million printed numbers per run, derived from the bc 3.0.0 scripts) into a file that is then diffed. They measure number printing and output as much as arithmetic, and GNU bc's 1.3-2.5 s of sys time, which scales with the count of printed results and is not explained on the page, inflates the wall-clock ratios; by user time the -O2 gains are only 1.19x-2.23x. The scripts live under tests/bc/scripts/ only in the 3.0.0 tree; HEAD has a different benchmarks/ folder and scripts/benchmark.sh with no published results.
- Build flags matter more than usual: without LTO the cross-file helper functions (for example bc_vec_item) are not inlined, and the author found -march=native made it slower; clang is recommended over gcc (no numbers given).
- bcl.h has no extern "C" guard, so C++ code must wrap the include itself; non-_keep math functions consume (free) their arguments even on error.
- The latest releases 7.1.0 and 7.2.0 are labelled UNTESTED in NEWS.md; tested releases are offered under paid maintenance terms (MAINTENANCE-TERMS.md), and OSS-Fuzz was disabled over LeakSanitizer reports until a rebuild in August 2026 (issue #103).

## Known shortcomings

- No CPU model; bc 3.0.0 (2019) against GNU bc 1.07.1. Wall-time gains are inflated by GNU bc system time (user-time ratios: add 1.42x, power 15.7x); loop scripts are slower or level. Off-baseline (GNU bc, not a listed interpreter). It is the system bc in FreeBSD, macOS and Android.
- Enricher: the 3.0.0 add/sub/mult/div scripts (tests/script.sh with -lq) print every result to a file, 0.98M-1.96M lines, so they time number printing and output rather than arithmetic; GNU bc's 1.3-2.5 s of system time grows with the line count. By user time the gain is 1.19x-2.23x; power is a real 15.7x. No published comparison for 7.x. bcl.h has no extern "C" guard; releases 7.1.0 and 7.2.0 are labelled UNTESTED (paid maintenance terms); 'packaged in Fedora' is only a COPR; issue #98 reports a Windows 7 hang.

## Caveats and trade-offs

Numbers are from bc 3.0.0 (2019) against GNU bc 1.07.1, built with clang 9.0.1 on an unnamed x86_64 CPU, best of four runs. The project has had many releases since, and the benchmark scripts' paths (tests/bc/add.bc) no longer exist in the current tree. The wall-clock gains on add/subtract/multiply/divide are inflated by 1.3-2.5 s of sys time in GNU bc's runs (cause not stated on the page). By user time the -O2 gains are 1.42x add, 1.24x subtract, 2.23x multiply, 1.19x divide and 1.22x timeconst.bc, against 2.89x, 2.76x, 3.25x, 2.09x and 1.27x by wall time (all derived from page data). The power test (1234567890^100000) is the clear win at 15.7x user time. The interpreter itself is not faster: at -O2 the 100,000,000-iteration for-loop script is slower (22.76 s vs 16.60 s) and the while-loop script is level (16.98 s vs 17.32 s). The author also found -march=native makes this bc slower. GNU bc is not one of the category baselines (CPython, Lua, Ruby, V8), and bc is a calculator language rather than a general scripting language. The author calls bc complete (no new features) but still actively maintained.

POSIX bc plus dc in one binary and the bcl C library (callable from C++). Speed comes from packing several decimal digits per hardware integer and Karatsuba multiplication; author says the interpreter loop itself is slightly slower than GNU bc on scripts with little math.

## Maintenance

Actively maintained by one author (last commit 2026-10-03, a divmod fix) but feature-complete; BSD-2-Clause, pure C99 and widely shipped (FreeBSD, macOS, Android, Gentoo, LFS; Fedora only via a COPR), so it is safe to adopt, though the two newest releases are marked UNTESTED.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** manuals/benchmarks.md gives the exact commands, clang 9.0.1 and three flag sets used for both bcs (-O2; -O3 -flto -march=native; -O3 -flto), best of four runs, but no CPU model ('x86_64 machine running Gentoo Linux'). The scripts it uses (tests/bc/add.bc etc.) belong to the bc 3.0.0 tree and are no longer at those paths, so this is first-party evidence with partial methodology: C.
- **Verifier notes:** All claimed numbers appear in manuals/benchmarks.md, attributed correctly (-O2: add 2.54 vs 0.88 s, mult 7.15 vs 2.20, div 3.36 vs 1.61, power 11.30 vs 0.73, timeconst 16.71 vs 13.16; -O3 -flto -march=native: power 11.08 vs 0.71, mult 7.01 vs 1.59; for-loop 16.60 GNU vs 22.76 this bc). Shortcomings to record: off-baseline (GNU bc), no CPU model, 2019 version, and arithmetic wins partly sys-time driven. It is notable as the system bc of FreeBSD, macOS and Android. BSD-2-Clause, last commit 2026-10-03.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** user-time comparison on stated hardware; arithmetic-only timing of a current release
- **Pages the verifier opened:**
  - <https://github.com/gavinhoward/bc/blob/master/manuals/benchmarks.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/manuals/benchmarks.md>
  - <https://github.com/gavinhoward/bc>
  - <https://github.com/gavinhoward/bc/commits>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/README.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/tests/script.sh>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/scripts/benchmark.sh>
- **Sources the enricher read:**
  - <https://github.com/gavinhoward/bc>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/README.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/manuals/benchmarks.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/manuals/algorithms.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/manuals/build.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/manuals/bcl.3.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/include/num.h>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/include/bcl.h>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/MAINTENANCE-TERMS.md>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/VERSION.txt>
  - <https://raw.githubusercontent.com/gavinhoward/bc/3.0.0/tests/script.sh>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/tests/script.sh>
  - <https://raw.githubusercontent.com/gavinhoward/bc/3.0.0/tests/bc/scripts/add.bc>
  - <https://raw.githubusercontent.com/gavinhoward/bc/3.0.0/tests/bc/scripts/multiply.bc>
  - <https://raw.githubusercontent.com/gavinhoward/bc/3.0.0/tests/bc/scripts/divide.bc>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/gavinhoward/bc/HEAD/benchmarks/bc/add.bc>
  - <https://github.com/gavinhoward/bc/issues>
  - <https://github.com/gavinhoward/bc/issues/98>
  - <https://github.com/gavinhoward/bc/issues/103>
  - <https://github.com/gavinhoward/bc/commits>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/gavinhoward/bc`) · [data/wave12/enrich/raw/github_com_gavinhoward_bc.json](../../../data/wave12/enrich/raw/github_com_gavinhoward_bc.json) (enrichment confidence 0.72)

</details>
