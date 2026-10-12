# GNU gperf

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0-or-later` · ⚪ unknown

> Build-time generator of perfect-hash C/C++ lookup code for fixed keyword sets; about 2-5x faster lookups than std::unordered_map in third-party tests.

| | |
|---|---|
| **Beats** | std::unordered_map&lt;std::string_view, int&gt; (std::hash in the perfect_hashing harness; boost::hash in the qlibs/mph README nanobench tables) |
| **Claimed result** | GNU gperf's own manual and README give no lookup numbers; all numbers are third-party. (1) qlibs/mph perfect_hashing harness on an i7-12650H, plotted total time for size x 100,000 lookups, values read off the notebook's plots (derived from page data, about +/-0.01 s): 1024 string keys of length 1-8, all hits: std::unordered_map \~2.14 s vs gperf \~0.46 s, \~4.7x ('clang++-19' panel), \~2.06 s vs \~0.48 s, \~4.3x ('g++-13' panel), i.e. \~21 ns vs \~4.5 ns per lookup; 1024 keys of length exactly 8, all hits: \~1.58 s vs \~0.32 s, \~4.9x (\~1.62 vs \~0.33 s in the other panel); 1024 keys of length 1-8, all misses: \~0.66 s vs \~0.11 s, \~6x (\~0.70 vs \~0.11 s); 32 keys of length 1-8, all hits: \~0.052 s vs \~0.0125 s, \~4x ('clang++-19') and \~0.049 vs \~0.010 s, \~5x ('g++-13'). In the same harness mph is about 2-3x faster than gperf on hits (\~0.15 s at 1024 keys), while gperf edges mph on 1024-key all-miss runs (\~0.11 s vs \~0.13 s). (2) qlibs/mph README nanobench tables, ns/op gperf vs std::unordered_map (boost::hash): clang++: 5 keys len 4 7.70 vs 5.56 (gperf 1.38x slower), 5 len 8 7.70 vs 13.45 (1.75x faster), 6 len 2-5 7.94 vs 15.28 (1.92x), 100 len 8 8.04 vs 15.32 (1.91x), 100 len 1-8 13.06 vs 19.34 (1.48x); g++: 5 len 4 7.69 vs 5.29 (gperf 1.45x slower), 5 len 8 7.92 vs 13.36 (1.69x), 6 len 2-5 9.13 vs 17.56 (1.92x), 100 len 8 7.75 vs 15.01 (1.94x), 100 len 1-8 11.20 vs 25.35 (2.26x) (ratios derived from page data). (3) Kronuz/constexpr-phf README, 192 Xapiand field-type names: gperf 14 ns/op vs std::unordered_map 29 ns/op (2.07x, derived from page data) and std::set 82 ns/op; gperf is the fastest row there, ahead of constexpr-phf (18-21 ns). |
| **Workload** | qlibs/mph perfect_hashing harness: random alphanumeric string keys (length 1-8 or exactly 8; 1-32 and 1-1024 keys) known at compile time, size x 100,000 lookups from a pre-built vector with 100%, 50% or 0% hits (misses are runs of '.'), total time per binary (median of 3 runs, checksums asserted equal across targets); gperf generated with %compare-strncmp, %language=C++, %enum, %readonly-tables, %global-table, %struct-type and --multiple-iterations=1. Secondary: the qlibs/mph README nanobench tables (5, 6 or 100 random-string keys, ns per lookup) and Kronuz/constexpr-phf's string-dispatch benchmark on Xapiand's 192 field-type names. |
| **Metric** | latency |
| **Hardware** | 12th Gen Intel Core i7-12650H (notebook /proc/cpuinfo), pinned with taskset to logical CPU 1, Turbo Boost on, intel_pstate powersave governor (pyperf system tune output); the README tables state no CPU, and constexpr-phf says only x86_64. |
| **Compiler and flags** | perfect_hashing harness: notebook CXXFLAGS -std=c++20 -DNDEBUG -O3 -march=native, plus -fconstexpr-steps=1000000000 -ftemplate-depth=1024 from the Makefile; panels are labelled clang++-19 and g++-13, but the Makefile hard-codes CXX=clang++-18, which overrides the CXX environment variable the notebook passes, so both panels were most likely built with clang++-18; gperf version not stated (the Dockerfile does not install it). README tables: clang++ and g++ (versions not stated), -std=c++20 -O3 -DNDEBUG -mbmi2. constexpr-phf: GCC 11, -O3, x86_64. |
| **Adoption** | GitHub mirror has 0 stars; used by the GNU C, GNU C++, GNU Pascal and GNU Java compilers and GNU indent to recognise reserved words (gperf README and manual) |
| **Last commit** | 2022-02-08 |
| **Links** | [repository](https://www.gnu.org/software/gperf/) · [benchmark](https://github.com/qlibs/mph/tree/benchmark/perfect_hashing) |

## Verdict

gperf's own docs give no timings; in the third-party qlibs/mph perfect_hashing harness (i7-12650H, -O3 -march=native, built with clang++-18 despite clang++-19 and g++-13 panel labels, libstdc++ std::unordered_map&lt;std::string_view, int&gt; with std::hash) 1024 string keys of length 1-8 took about 0.46 s for 102.4 million all-hit lookups vs about 2.14 s (about 4.5 vs 21 ns per lookup, 4.3-4.7x), about 6x on all-miss runs and 4-5x at 32 keys, with values read off plots. Secondary sources agree in direction: the qlibs/mph README nanobench shows 1.5-2.3x except a 1.4x loss on 5 four-character keys, and Kronuz/constexpr-phf shows 14 vs 29 ns per lookup on 192 field names (GCC 11, -O3).

## Use it when

- Small to medium static keyword sets (tens to a few thousand keys; the manual says it is tuned for about 1000 and works on over 15,000) such as reserved words, HTTP header or field names, opcodes or config keys.
- Plain C code or older C++ toolchains where constexpr perfect-hash libraries (mph needs C++20, frozen C++14) are not an option; the default output is ANSI C and K&R C is still supported.
- Lookups dominated by misses on short strings: the length range and hash range checks reject most non-keywords before any string compare (about 6x faster than std::unordered_map on all-miss runs in the qlibs/mph harness).
- When you need per-keyword payload structs, ASCII case-insensitive matching (%ignore-case), or a PIC-friendly string pool for a shared library.

## Skip it when

- Large key sets: generation time grows sharply; rurban/Perfect-Hash reports every gperf run on a 99,171-word dictionary killed after 65-386 s, and gsauthof/phashtable reports it does not finish on 1.4 million ISINs.
- Sets that change at runtime, or that must be loaded from data at startup; gperf output is compiled source.
- Hit-heavy hot paths where the fastest option matters: in the same third-party harnesses qlibs/mph is about 2-3x faster than gperf on hits, and ConstexprCore/perfect_hash claims 1.08 vs 0.23 billion queries/s.
- Very small sets of very short fixed-length keys: in the qlibs/mph README table gperf is about 1.4x slower than std::unordered_map on 5 four-character keys with both compilers.
- Keywords that collide on every choice of byte positions (some permutation/anagram sets): -D makes the function handle them with extra comparisons, so it is no longer perfect.

## How it is fast

The hash is len plus a sum of 'associated values' looked up for a few selected byte positions (chosen automatically to minimise the number of positions, or set with -k), so a lookup is a handful of table reads, one bounds check and a single string compare against the one candidate slot. The associated values are searched at generation time until every keyword lands in a distinct slot; tables are near-minimal by default and can be made sparser with -s, which the manual notes speeds up unsuccessful searches. Alternative outputs include C switch statements (-S), constant tables (-C) and a position-independent string pool for shared libraries (-P).

## Compared with alternatives

Pick gperf over qlibs/mph, frozen or constexpr-phf when you need C output, a pre-C++20 toolchain or a mature, distro-packaged generator, and over Perfect::Hash or cmph only for small keyword sets; pick mph or ConstexprCore/perfect_hash for the fastest hit lookups in modern C++, and triehash or strager/perfect-hash-tables if their gperf-beating keyword-recognition numbers match your workload.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | the gperf executable at build time (GNU autotools build, or a distro package); the generated code needs only &lt;string.h&gt; for strcmp/strncmp (emitted when -I/%includes is given) |
| **Minimum toolchain** | generated code: ANSI C by default, K&R C or C++ via -L; generator: a C++ compiler (the mirror's 2020 commit made it C++17 compliant) |
| **Platforms** | any; generated code is portable C, and the generator builds on Unix-like systems and native Windows (MSVC/clang link fix in 2020) |
| **Thread safety** | not documented; generated lookups only read static tables (const with -C/%readonly-tables) and keep no state, so concurrent lookups are safe in practice |
| **Drop-in for the baseline** | no |

## Gotchas

- By default the input string must be NUL-terminated and exactly len bytes long; pass std::string_view or buffers only with %compare-strncmp (-c), and keywords containing NUL bytes need %compare-lengths (-l), which can greatly enlarge the output when the table range is large.
- Harness notes for the A-tier numbers (qlibs/mph benchmark branch, perfect_hashing): the miss keys are runs of 2 to 11 '.' characters (string_views built from &"..........."[i%10]), which gperf rejects on the length or hash-range check before any compare, and hits and misses come in fixed blocks of P percent per 100 lookups, so the miss rows are cheap and branch-predictable rather than adversarial. Each 1024-key run streams three vectors of 102.4 million string_views (about 1.6 GB each, derived from benchmark.hpp), so the fastest contenders may sit near a memory-bandwidth floor that compresses the gap between mph and gperf more than the gap between gperf and std::unordered_map. The Makefile's default CXXFLAGS is -Ofast; the notebook overrides it with -O3, and CXX=clang++-18 is hard-coded.
- The qlibs/mph README nanobench rows measure gperf output that was pasted into lambdas, given an extra index[] table and compared with strcmp; they time hits only, seed the key order from std::random_device, and use boost::hash rather than std::hash for the std::unordered_map baseline.
- The generator is GPL-3.0-or-later, but per the manual its output takes the licence of your keyword input; this GitHub mirror stops at gperf 3.2 (released 2022-01-05, last commit 2022-02-08), while upstream shipped 3.2.1 and 3.3 (3.3 documentation dated April 2025, generator 2-2.5x faster; WebSearch snippets only, Savannah and the distro patch pages are blocked here), so take sources from GNU or a distro package.

## Known shortcomings

- Evidence comes only from competitors' harnesses (qlibs/mph benchmark-branch perfect_hashing: public code, i7-12650H, -O3 -march=native; plot reads about 4.3-4.9x vs std::unordered_map at 1024 keys on hits, about 6x on misses; compiler labels unreliable, Makefile hard-codes clang++-18); the README baseline uses boost::hash; slower than std::unordered_map on 5 four-char keys. The GitHub mirror stops at 3.2 (2022-02-08); upstream 3.3 (2025) seen in snippets only. gperf is the de-facto baseline of perfect-hash-static-tables (triehash, strager, rurban and constexpr-phf all benchmark against it). Generated output is not GPL.
- Enricher: in qlibs perfect_hashing the misses are 2-11 '.' strings in fixed blocks, so cheap and predictable, and the 1024-key runs stream about 4.9 GB of string_views (possible memory floor, derived); the mph README nanobench is hits only with hand-edited gperf output and a random_device seed. The mirror is stuck at 3.2 (2022); upstream 3.3 (April 2025) is known from a snippet only.

## Caveats and trade-offs

All evidence is third-party and comes from competing perfect-hash libraries (qlibs/mph, Kronuz/constexpr-phf), both of which also show their own library beating gperf on hits. The perfect_hashing harness's compiler labels are unreliable (Makefile hard-codes clang++-18; identical binaries in both panels per the wave1-phf qlibs/mph record), the machine ran with turbo on and the powersave governor, the plots must be read off pixels, the 1024-key runs stream a size x 100,000 lookup vector (\~100M string_views) so per-lookup times may sit near a memory floor, and the misses are runs of '.' that gperf rejects on length or its first table probe, so the all-miss rows are cheap rather than adversarial. In the README nanobench tables the std::unordered_map baseline uses boost::hash (benchmark/benchmark.cpp), the gperf output is pasted into lambdas and edited to return an index, and gperf loses to std::unordered_map on 5 four-character keys (1.4x slower with both compilers). The qlibs.github.io page carrying the same plots is blocked here; the notebook and its embedded plots were read through raw.githubusercontent.com. libstdc++ is inferred (Ubuntu jammy Docker image, no -stdlib flag). Schmidt's 1990 USENIX C++ paper 'GPERF: A Perfect Hash Function Generator' was not reachable. gperf's output is not under the GPL (manual section 'The Copyright of the Output'): generated tables take the licence of the keyword input, so the GPL-3.0-or-later licence covers the generator only. The repo URL is an unofficial GitHub mirror (0 stars) that stops at gperf 3.2 (last commit 2022-02-08); WebSearch snippets (snippet only) show upstream releases 3.2.1 and 3.3 (3.3 packaged by IPFire in a patch dated 2025-05-24, NEWS: gperf itself 2-2.5x faster), so the mirror lags GNU Savannah, which is blocked here. Not a minimal perfect hash for large key sets: gperf targets small keyword sets and its tables keep empty slots (e.g. 5 keys in an 8-slot table in the README harness).

Build-time generator that emits C or C++ source (switch or table form) for a fixed keyword set; the generated code is not covered by the GPL (manual, 'The Copyright of the Output'), but the generator is GPL. Works on selected character positions, so it handles small and medium sets well; gsauthof/phashtable's README reports it does not terminate in a reasonable time on 1.4 million ISINs and gave a 10% table fill on smaller sets, and rurban/Perfect-Hash's README says it cannot deal with certain anagrams. Non-minimal tables by default.

## Maintenance

The GNU project is maintained (3.3 in 2025 per snippets) but this mirror is stale since 2022; the generator is GPL while its output is unencumbered, so generated tables are freely copyable into any codebase.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: the third-party qlibs/mph perfect_hashing harness (benchmark branch, perfect_hashing/gperf.cpp and unordered_map.cpp with benchmark.hpp, Makefile, benchmark.ipynb) times gperf-generated lookup against std::unordered_map with public code, stated flags (-std=c++20 -DNDEBUG -O3 -march=native) and CPU (i7-12650H from /proc/cpuinfo in the notebook); the same page earned qlibs/mph its A in wave1-phf. Compiler labels (clang++-19, g++-13) are unreliable because the Makefile hard-codes CXX=clang++-18.
- **Verifier notes:** Numbers in the record match the qlibs/mph README and constexpr-phf README (record omitted three g++ rows, now added). Tier raised C to A on the qlibs/mph perfect_hashing harness (public code, i7-12650H, -O3 -march=native), consistent with qlibs/mph's own A; shortcomings to record: third-party evidence from competitors only, unreliable compiler labels, plot-read values, gperf slower than std::unordered_map on 5 four-character keys, README baseline uses boost::hash, mirror repo lags upstream 3.3. Category: gperf is a static keyword-table generator, not a large-set MPHF, so it fits wave1-phf's perfect-hash-static-tables (frozen, qlibs/mph, constexpr-phf, triehash), where it is the de facto incumbent that triehash, strager/perfect-hash-tables and rurban/perfect-hash benchmark against; consider a category override and a repo_url override to https://www.gnu.org/software/gperf/ (the seed id). maintenance_status left 'unknown': the mirror's last commit is 2022-02-08 (abandoned by the rule), but upstream had a 3.3 release in 2025 per snippets only; git.savannah.gnu.org and sources.debian.org were EGRESS_BLOCKED.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_stdlib`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** qlibs/mph harness (verifier C to A); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/gnu-mirror-unofficial/gperf>
  - <https://github.com/gnu-mirror-unofficial/gperf/commits>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/gperf/HEAD/NEWS>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/gperf/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/gperf/HEAD/README>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/gperf/HEAD/COPYING>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/gperf/HEAD/doc/gperf.texi>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/gperf/HEAD/src/main.cc>
  - <https://github.com/qlibs/mph>
  - <https://github.com/qlibs/mph/tree/benchmark>
  - <https://github.com/qlibs/mph/tree/benchmark/benchmark>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/benchmark/CMakeLists.txt>
  - <https://github.com/qlibs/mph/tree/benchmark/perfect_hashing>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/Makefile>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/gperf.cpp>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/unordered_map.cpp>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/benchmark.hpp>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/benchmark.ipynb>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/benchmark_str_to_int.png>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/Dockerfile>
  - <https://raw.githubusercontent.com/Kronuz/constexpr-phf/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/gperf/HEAD/README>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/gperf/HEAD/NEWS>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/gperf/HEAD/doc/gperf.texi>
  - <https://github.com/gnu-mirror-unofficial/gperf/commits>
  - <https://github.com/qlibs/mph>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/Makefile>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/gperf.cpp>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/unordered_map.cpp>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/mph.cpp>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/benchmark.hpp>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/perfect_hashing/Dockerfile>
  - <https://raw.githubusercontent.com/qlibs/mph/benchmark/benchmark/benchmark.cpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/gnu-mirror-unofficial/gperf`) · [data/wave1/enrich/raw/github_com_gnu_mirror_unofficial_gperf.json](../../../data/wave1/enrich/raw/github_com_gnu_mirror_unofficial_gperf.json) (enrichment confidence 0.7)

</details>
