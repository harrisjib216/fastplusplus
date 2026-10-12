# MELG-64 (MELG19937-64)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `MIT` · 🔴 abandoned

> Maximally equidistributed 64-bit Mersenne-Twister-type generators in C; MT19937-64-class speed with optimal high-dimensional uniformity.

| | |
|---|---|
| **Beats** | MT19937-64 reference C code (algorithmically std::mt19937_64) |
| **Claimed result** | README table, CPU seconds for 1e9 64-bit outputs: MELG19937-64 4.2123 (Intel Core i7-3770) / 6.2920 (AMD Phenom II X6 1045T) vs reference MT19937-64 5.1002 / 6.6490 (about 1.21x and 1.06x, derived from page data). SFMT19937-64 without SIMD is about level (4.2654 / 5.6123, faster on the AMD part) and with SIMD much faster (1.8457 / 2.8806). The README and paper describe the speed as 'equivalent to' / 'competitive with' MT19937-64; the claimed advantage is equidistribution (Delta=0 vs 7820 for MT19937-64). |
| **Workload** | CPU time to generate 10^9 64-bit unsigned integers with MELG19937-64, MT19937-64, MT19937-64 (ID3), SFMT19937-64 without SIMD and SFMT19937-64 with SIMD. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-3770 (3.40GHz) and AMD Phenom II X6 1045T (2.70 GHz) |
| **Compiler and flags** | gcc with -O3 on Linux (README Platforms section); compiler version not stated; build line 'gcc melg19937-64.c -o melg19937-64 -O3 -Wall'. No timing program is in the repo. |
| **Adoption** | 15 stars; ACM TOMS 44(3) 2018 paper |
| **Last commit** | 2023-03-18 |
| **Links** | [repository](https://github.com/sharase/melg-64) · [benchmark](https://github.com/sharase/melg-64) |

## Verdict

The README reports CPU time for 10^9 64-bit outputs with gcc -O3 on Linux (compiler version not given): 4.21 s on an Intel Core i7-3770 and 6.29 s on an AMD Phenom II X6 1045T, versus 5.10 s and 6.65 s for the reference mt19937-64.c (about 1.21x and 1.06x faster), 4.27 s and 5.61 s for SFMT19937-64 without SIMD, and 1.85 s and 2.88 s with SIMD. These are first-party numbers with no timing harness in the repo, and std::mt19937_64 itself was not measured.

## Use it when

- Monte Carlo or simulation code in C that already uses the reference mt19937-64.c API and wants better high-dimensional uniformity (maximal equidistribution) at similar or slightly better speed.
- Workloads that consume the most significant bits, e.g. 53-bit doubles via genrand64_res53(), where the equidistribution of leading bits matters.
- Single-stream programs that need a very long period and occasional jump-ahead by 2^256 to hand out disjoint streams.
- When you want to pick the state size: variants from 2^607-1 up to 2^44497-1 are provided.

## Skip it when

- Throughput is the goal: in the project's own table SFMT19937-64 with SIMD is 2.3x (Intel) and 2.2x (AMD) faster, and SFMT without SIMD is already faster on the AMD machine; a win over std::mt19937_64 was never measured.
- Multi-threaded code or several generators in one process: all state is in file-scope statics, so there is one generator per program (per copy of the file).
- C++ code that wants a &lt;random&gt; engine: there is no std::uniform_random_bit_generator wrapper.
- Commercial products before the licence question is settled: LICENSE.md says MIT, but the header of melg19937-64.c restricts free use to personal, academic or non-commercial purposes.
- Anything that must reproduce numbers from older copies: output values changed in 2017 (init_by_array64) and again in March 2021 (initialisation typo fix and the double output functions).

## How it is fast

The recurrence is MT-like (312-word state for the 2^19937-1 variant) but adds one extra 64-bit state word ('lung') and a lagged tempering term, so the output is tuned for equidistribution without adding much work per word. Each call produces one word incrementally instead of regenerating the whole state block, and the index wrap-around is handled by switching a global function pointer between four specialised case functions, so the hot path has no modulo or branch on the array index. There is no SIMD path; the measured edge over reference MT19937-64 is small (about 1.06-1.21x).

## Compared with alternatives

Pick MELG-64 over SFMT, VMT19937 or a faster std::mt19937_64 replacement only when maximal equidistribution of 64-bit outputs is the requirement and MT-class speed is enough; for raw throughput SFMT with SIMD (same table) or VMT19937's vectorised MT19937-64 are the better choices.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the C standard library (stdio, stdlib, math.h) |
| **Minimum toolchain** | C99 (unsigned long long, hex float literal 0x1.0p-53); README builds with gcc -O3 -Wall |
| **Platforms** | any platform with a 64-bit unsigned long long; README timings on x86-64 Linux only |
| **Thread safety** | Not thread-safe: state (melg[], melgi, lung) and the genrand64_int64 function pointer are file-scope globals; melg_jump() also rewrites that global state. |
| **Drop-in for the baseline** | partial — same function names and seeding API as the reference mt19937-64.c, so it can replace that file in C code, but it is not a C++ engine and its output stream differs from std::mt19937_64 |

## Gotchas

- genrand64_int64 is a global function pointer that stays NULL until init_genrand64() or init_by_array64() runs; calling it before seeding is a null-pointer call.
- Each .c file contains a demo main() that must be removed, there is no header, and the exported names (init_genrand64, init_by_array64, genrand64_int64, genrand64_real\*) clash with mt19937-64.c if both are linked.
- Use the most significant bits: the source notes the generators are optimised from the MSB down (Remark 4.1 of the paper), so taking low bits for small ranges forfeits the equidistribution guarantee.
- Licence mismatch between LICENSE.md (MIT, 2021) and the source-file notice (non-commercial, contact the author for commercial use).

## Known shortcomings

- Not faster than the incumbent: no timing harness in the repo, gcc version unstated, paper abstract claims 'equivalent' speed; only 6-21% faster than the reference mt19937-64.c, and std::mt19937_64 was never measured (VMT19937 data shows libstdc++ 1.17-1.76x faster than that same reference); source header says non-commercial while the paper says MIT.
- Licence conflict: LICENSE.md is MIT but the melg19937-64.c header says free only for personal/academic/non-commercial use and commercial users must contact the author. genrand64_int64 is a global function pointer, NULL until init; all state is file-scope globals (not thread-safe); symbol names clash with mt19937-64.c; output stream changed in 2017 and 2021.

## Caveats and trade-offs

Speed is parity-class, not a speedup: about 6-21% faster than the reference mt19937-64.c and slower than SFMT19937-64 without SIMD on the AMD part. No public timing harness, no compiler version, 2012-era CPUs. std::mt19937_64 itself was not measured; in VMT19937's tables (another project, other CPUs) libstdc++'s std::mt19937_64 runs 1.17-1.76x faster than the same reference mt19937-64.c, so a win over std::mt19937_64 is not shown. ACM TOMS 2018 paper (Harase and Kimoto) cited but not opened. Value is equidistribution quality (maximally equidistributed, N1=9603). Last commit 2023-03-18.

Plain C, 312-word state like MT19937-64; jump-ahead for disjoint streams; recommends using most significant bits; no SIMD path.

## Maintenance

Abandoned research code (last commit 2023-03-18, 3 issues all closed) that is small enough to vendor, but check the MIT-versus-non-commercial licence conflict first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README table (CPU time for 1e9 outputs, gcc -O3, i7-3770 and Phenom II X6 1045T) is first-party. The repo has no timing harness (melg19937-64.c's main only prints sample outputs) and no compiler version. The peer-reviewed ACM TOMS paper could not be opened, and its abstract claims 'speeds equivalent to 64-bit Mersenne Twisters', not a win, so B is not supported.
- **Verifier notes:** Numbers match the README exactly. Downgraded B to C: the paper's abstract (seen only in a WebSearch summary; ACM DL, arXiv and the author's site are blocked) claims equivalent speed, and the repo has no timing code. Kept rather than rejected because the table does show it ahead of MT19937-64; record 'not faster than std::mt19937_64 shown' as the shortcoming. Metadata: MIT (LICENSE.md, 2021), 15 stars, 3 forks, 35 commits; abandoned (&gt;3 years).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sharase/melg-64/HEAD/README.md>
  - <https://raw.githubusercontent.com/sharase/melg-64/master/melg19937-64/melg19937-64.c>
  - <https://raw.githubusercontent.com/sharase/melg-64/master/LICENSE.md>
  - <https://github.com/sharase/melg-64>
  - <https://github.com/sharase/melg-64/commits>
  - <https://github.com/sharase/melg-64/tree/master/melg19937-64>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sharase/melg-64/HEAD/README.md>
  - <https://raw.githubusercontent.com/sharase/melg-64/HEAD/melg19937-64/melg19937-64.c>
  - <https://raw.githubusercontent.com/sharase/melg-64/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/sharase/melg-64/HEAD/CHANGE-LOG.txt>
  - <https://github.com/sharase/melg-64>
  - <https://github.com/sharase/melg-64/issues?q=is%3Aissue>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sharase/melg-64`) · [data/wave8/enrich/raw/github_com_sharase_melg_64.json](../../../data/wave8/enrich/raw/github_com_sharase_melg_64.json) (enrichment confidence 0.85)

</details>
