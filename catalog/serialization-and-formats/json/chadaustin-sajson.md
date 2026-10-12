# sajson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> Single-header, in-situ C++11 JSON DOM parser; 1.1-1.8x faster than RapidJSON insitu in the simdjson paper.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | Paper text: "In practice, we find that another C++ parser, sajson, is faster [than RapidJSON]". Paper Table 10 (Skylake i7-6700, GCC 9.1, GB/s): sajson (static allocation) 0.62-1.2 vs RapidJSON insitu 0.41-1.0 and RapidJSON default 0.38-0.86. Examples: twitter 1.0 vs 0.72 insitu / 0.45 default; apache_builds 1.2 vs 0.80 / 0.48; canada 0.76 vs 0.43 / 0.43. Derived from page data: sajson is 1.10-1.77x faster than RapidJSON insitu (geomean \~1.4x) and 1.37-2.5x faster than RapidJSON default (geomean \~1.9x). Paper Table 9 (twitter, parse only): 1.0 vs 0.8 GB/s on Skylake and 0.9 vs 0.7 GB/s on Cannon Lake. README: "sajson's performance is excellent - it frequently benchmarks faster than RapidJSON, for example". |
| **Workload** | Full in-memory parse with UTF-8 validation, single-threaded, best time. 14 files: apache_builds, canada, citm_catalog, github_events, gsoc-2018, instruments, marine_ik, mesh, mesh.pretty, numbers, random, twitter, twitterescaped, update-center. sajson uses static (bounded) allocation. RapidJSON 1.1.0 runs with kParseValidateEncodingFlag in both default and insitu modes. |
| **Metric** | throughput |
| **Hardware** | Paper: Intel i7-6700 Skylake, 3.4 GHz base / 3.7 GHz max, hyper-threading disabled; also Intel i3-8121U Cannon Lake. Author blog chart titles: Haswell i7-4771 (Windows 7, MSVC 14 and MinGW), Broadwell i5-5200U (Ubuntu 16.04, gcc/clang), iPhone SE (Xcode 8.3.2), Atom D2700 (Ubuntu, 64-bit). |
| **Compiler and flags** | Paper: GCC 9.1, -O3 -march=native, Linux, no PGO. Author blog harness (chadaustin/Web-Benchmarks json/SConstruct): -O2 -g -fno-exceptions -DNDEBUG -std=c++11 with gcc/clang (versions not stated); MSVC 14; Xcode 8.3.2. |
| **Adoption** | 573 stars |
| **Last commit** | 2025-04-06 |
| **Links** | [repository](https://github.com/chadaustin/sajson) · [benchmark](https://arxiv.org/abs/1902.08318) |

## Verdict

The peer-reviewed simdjson paper (Skylake i7-6700, GCC 9.1 -O3 -march=native) compared a 2018-09-20 sajson snapshot using a pre-sized bounded buffer against RapidJSON 1.1.0 with UTF-8 validation. sajson parsed all 14 files at 0.62-1.2 GB/s, against 0.41-1.0 GB/s for RapidJSON insitu (1.1-1.8x) and 0.38-0.86 GB/s for RapidJSON default. yyjson's README independently shows twitter.json at 1.16 vs 0.77 GB/s (AMD EPYC 7R32, gcc 9.3) and 1.74 vs 0.75 GB/s (Apple A14, clang 12) against RapidJSON insitu. The author's own blog says the gap is small with GCC and large with MSVC and clang.

## Use it when

- Read-only, single-pass parsing of complete UTF-8 documents already in a writable buffer (file read, network receive buffer) where the buffer can outlive the parsed document.
- String- and object-heavy payloads such as API responses and logs: the paper's gains over RapidJSON insitu include apache_builds 1.2 vs 0.80 GB/s and twitter 1.0 vs 0.72 GB/s.
- Embedded, mobile or WebAssembly builds that need zero library allocations: bounded_allocation parses into a caller-owned size_t array, with no exceptions, RTTI or longjmp, and the README calls the code size suitable for Emscripten.
- Code that needs random access into the parsed tree: O(1) array element access and key lookup (binary search above 100 keys), unlike linked-list DOMs.
- Deeply nested or adversarial structure where native stack overflow is a concern: parsing uses O(1) C stack and has been fuzzed with AFL.

## Skip it when

- Payloads with 64-bit integers such as IDs: only int32 is stored as an integer, and larger values silently become doubles that lose precision above 2^53 (issue #39, open since 2017).
- When strict conformance matters: UTF-8 validation is partial (it accepts overlong forms, encoded surrogates, code points above U+10FFFF and stray continuation-byte leads such as 0xb1 0x87), scalar roots like `42` are rejected (issue #46), and doubles are not always correctly rounded (issue #10; open PR #59 shows 1.65 parsing to the wrong neighbor).
- When you must write, modify or stream JSON: there is no serializer, no mutable DOM and no incremental or SAX mode.
- Large documents on memory-tight hosts in the fastest mode: single allocation reserves 8 bytes per input byte on 64-bit. Dynamic mode is 10-40% slower per the README, and in the paper it loses to RapidJSON insitu on 6 of 14 files.
- Peak throughput or active maintenance: simdjson is 1.4-2.9x faster on the same 14 files, yyjson's README shows 1.80 vs 1.16 GB/s on twitter.json, and sajson's parser code has not changed since 2021.

## How it is fast

In single-allocation mode one buffer of one word per input byte holds both the parse stack, which grows up from the bottom, and the AST, which is written down from the top, so the hot path has no capacity checks. Values are tagged words with 3 low tag bits, and null/true/false take no storage. The parser is a goto-based state machine with an explicit stack (no recursion) and __builtin_expect branch hints. It scans strings 4 bytes per iteration through a 256-entry lookup table and drops to a slow path only for escapes or non-ASCII bytes. Strings are unescaped and NUL-terminated inside the input buffer, so no string copies are made. There is no SIMD, and numbers use a plain digit loop scaled by a power-of-10 table.

## Compared with alternatives

Over gason, pick sajson when you need indexed access (gason uses linked lists without random access) or parse string- and object-heavy data (paper: apache_builds 1.2 vs 0.91 GB/s, twitter 1.0 vs 0.80), but gason wins number-heavy files (canada 0.95 vs 0.76, mesh 0.77 vs 0.62). simdjson and yyjson are faster; yyjson also reads int64 exactly, and simdjson leaves the input untouched. Choose sajson over them only when a tiny single header with a zero-allocation bounded mode and O(1) indexed DOM access matters more than peak speed.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only; SAJSON_NO_STD_STRING removes the &lt;string&gt; dependency) |
| **Minimum toolchain** | C++11 per README, and the Bazel library target uses -std=c++11. However, current master defines its lookup table as an in-class constexpr static member with no out-of-class definition. Issue #48 reports undefined-reference link errors from `g++-9 -g` and GCC 10 builds, and the repo's Bazel tests build with -std=c++17. Use C++17 or apply open PR #54. |
| **Platforms** | any; portable scalar C++ with no SIMD. The SCons matrix builds gcc and clang for 32- and 64-bit; the header has MSVC-specific macros; the repo includes a Swift binding. |
| **Thread safety** | Not documented. The parser keeps no mutable global state (only a constexpr lookup table), so parses of separate buffers are independent. document is move-only and value objects are read-only views into it. mutable_string_view shares copied input through a non-atomic refcount, so do not copy those views across threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- The input buffer is overwritten: escapes are decoded in place and the closing quote becomes NUL. The buffer must stay writable and alive for the document's lifetime, and embedded \u0000 truncates as_cstring() results.
- Objects with more than 100 keys are sorted at parse time (by length, then bytes), so get_object_key(i) no longer follows document order unless SAJSON_UNSORTED_OBJECT_KEYS is defined, which makes all lookups linear. Duplicate keys are accepted without error.
- Type and bounds checks are assert()-only: calling get_integer_value() on a double or indexing past get_length() is undefined behavior in NDEBUG builds. A missing key returns a null value.
- Buffer sizes are in size_t words, not bytes (issue #51). A caller-supplied single_allocation buffer fails with ERROR_OUT_OF_MEMORY unless it has at least one word per input byte.

## Known shortcomings

- The C++11 claim is broken on master: parse_flags is a constexpr static member without an out-of-class definition, giving link errors on GCC 9/10 (#48; fix PR #54 unmerged). Integers outside int32 silently become doubles (the paper says they are rejected). UTF-8 validation is partial, scalar roots are rejected, doubles are not always correctly rounded (#10), and checks are assert()-only. The paper benchmarked a 2018 snapshot in bounded_allocation mode. gason beats it on number-heavy files (canada, mesh). Parser unchanged since 2021-09.

## Caveats and trade-offs

Paper numbers use sajson's static-allocation mode. In dynamic-allocation mode (0.46-1.0 GB/s) sajson is slower than RapidJSON insitu on 6 of 14 files: citm_catalog, gsoc-2018, instruments, mesh.pretty, random and update-center. Snapshots are from 2018-2019: sajson 2018-09-20 and RapidJSON 1.1.0. sajson supports only 32-bit integers, does partial UTF-8 validation (it accepts some invalid sequences) and parses in situ (it modifies the input). The author's own 2017 blog numbers are only in chart images. That blog says that with GCC, RapidJSON, sajson and pjson are 'very similar'; its large wins (about 2-3x) are with MSVC, clang and iPhone builds. The repo's own benchmark/benchmark.cpp times only sajson and does not run RapidJSON.

In-situ parser that mutates the input buffer; no UTF-16/UTF-32 support; no 64-bit integer type; single-allocation mode requires sizing the worst-case output buffer up front

## Maintenance

Stale: the last parser change was in September 2021 (a full int32 range fix), the 2025 commit only added Bazel support, and 8 issues plus 3 PRs are open. It is MIT-licensed and a single 2.6k-line header, so it is easy to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now A.
- **Tier reason:** Tier raised from C to A. The simdjson paper (Langdale & Lemire, VLDB Journal 28(6) 2019, arXiv 1902.08318) is peer-reviewed; its Table 10 and Fig. 9 show sajson faster than RapidJSON 1.1.0 on all 14 files. The paper states the CPU (Intel i7-6700 Skylake), compiler (GCC 9.1) and flags (-O3 -march=native). The benchmark code is public in simdjson benchmark/parsingcompetition.cpp (tag v0.2.1), and the artifact repo simdjson/simdjson_experiments_vldb2019 runs it in experiments/comparison with a gcc:9.1 Docker image.
- **Verifier notes:** The original benchmark_url (the README #performance section) has only the verbatim qualitative sentence and no numbers. The numbers come from the author's 2017 blog charts (read from chart images) and from the independent peer-reviewed simdjson paper, which is now the benchmark_url. Metadata checks OK: MIT, 573 stars, not archived, not a fork, last commit 2025-04-06, stale.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `caveats`
- **Shortcomings recorded by:** yyjson README (independent of sajson): twitter.json sajson 1.16 vs RapidJSON insitu 0.77 GB/s on EPYC 7R32 with gcc 9.3, and 1.74 vs 0.75 GB/s on Apple A14 with clang 12; yyjson and simdjson are faster than sajson there.
- **Pages the verifier opened:**
  - <https://github.com/chadaustin/sajson>
  - <https://github.com/chadaustin/sajson#performance>
  - <https://github.com/chadaustin/sajson/blob/master/benchmark/benchmark.cpp>
  - <https://github.com/chadaustin/sajson/blob/master/SConstruct>
  - <https://github.com/chadaustin/sajson/blob/master/s/bench>
  - <http://chadaustin.me/tag/sajson/>
  - <https://chadaustin.me/2017/05/writing-a-really-really-fast-json-parser/>
  - <https://chadaustin.me/wp-uploads/perf-msvc-haswell-1024x556.png>
  - <https://chadaustin.me/wp-uploads/perf-mingw-haswell-1024x556.png>
  - <https://chadaustin.me/wp-uploads/perf-linux-broadwell-1024x555.png>
  - <https://chadaustin.me/wp-uploads/perf-iphone_se-1024x556.png>
  - <https://chadaustin.me/wp-uploads/perf-atom-d2700-1024x556.png>
  - <https://github.com/chadaustin/Web-Benchmarks>
  - <https://github.com/chadaustin/Web-Benchmarks/blob/master/json/SConstruct>
  - <https://github.com/chadaustin/Web-Benchmarks/blob/master/json/perf.cpp>
  - <https://github.com/chadaustin/Web-Benchmarks/blob/master/json/perf-native.csv>
  - <https://arxiv.org/abs/1902.08318>
  - <https://arxiv.org/pdf/1902.08318>
  - <https://github.com/simdjson/simdjson/blob/v0.2.1/benchmark/parsingcompetition.cpp>
  - <https://github.com/simdjson/simdjson/blob/v0.2.1/Makefile>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019/blob/master/experiments/comparison/Dockerfile>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019/blob/master/experiments/comparison/run.sh>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019/blob/master/results/skylake/comparison/alltwitter.table>
- **Sources the enricher read:**
  - <https://github.com/chadaustin/sajson>
  - <https://github.com/chadaustin/sajson/blob/master/include/sajson.h>
  - <https://github.com/chadaustin/sajson/blob/master/include/sajson_ostream.h>
  - <https://github.com/chadaustin/sajson/blob/master/example/main.cpp>
  - <https://github.com/chadaustin/sajson/blob/master/example/zero-allocation.cpp>
  - <https://github.com/chadaustin/sajson/blob/master/tests/test.cpp>
  - <https://github.com/chadaustin/sajson/blob/master/benchmark/benchmark.cpp>
  - <https://github.com/chadaustin/sajson/blob/master/BUILD.bazel>
  - <https://github.com/chadaustin/sajson/blob/master/MODULE.bazel>
  - <https://github.com/chadaustin/sajson/blob/master/SConstruct>
  - <https://github.com/chadaustin/sajson/blob/master/SConscript>
  - <https://github.com/chadaustin/sajson/blob/master/s/bench>
  - <https://github.com/chadaustin/sajson/blob/master/.travis.yml>
  - <https://github.com/chadaustin/sajson/issues>
  - <https://github.com/chadaustin/sajson/pulls>
  - <https://github.com/chadaustin/sajson/commits/master>
  - <https://github.com/chadaustin/sajson/issues/10>
  - <https://github.com/chadaustin/sajson/issues/15>
  - <https://github.com/chadaustin/sajson/issues/28>
  - <https://github.com/chadaustin/sajson/issues/39>
  - <https://github.com/chadaustin/sajson/issues/45>
  - <https://github.com/chadaustin/sajson/issues/46>
  - <https://github.com/chadaustin/sajson/issues/48>
  - <https://github.com/chadaustin/sajson/issues/51>
  - <https://github.com/chadaustin/sajson/pull/54>
  - <https://github.com/chadaustin/sajson/pull/58>
  - <https://github.com/chadaustin/sajson/pull/59>
  - <https://arxiv.org/abs/1902.08318>
  - <https://arxiv.org/pdf/1902.08318>
  - <https://chadaustin.me/2017/05/writing-a-really-really-fast-json-parser/>
  - <https://github.com/simdjson/simdjson/blob/v0.2.1/benchmark/parsingcompetition.cpp>
  - <https://github.com/ibireme/yyjson>
  - <https://github.com/vivkin/gason>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/chadaustin/sajson`) · [data/wave4/enrich/raw/github_com_chadaustin_sajson.json](../../../data/wave4/enrich/raw/github_com_chadaustin_sajson.json) (enrichment confidence 0.8)

</details>
