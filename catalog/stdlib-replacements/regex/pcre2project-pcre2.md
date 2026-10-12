# PCRE2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Regex](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause WITH PCRE2-exception` · 🟢 active

> Mature C library for Perl-compatible regex matching; 4-12x faster than libstdc++'s std::regex on find-and-count benchmarks.

| | |
|---|---|
| **Beats** | std::regex |
| **Claimed result** | Default build: 4.07x faster total (C++ STL 1023.49ms vs C PCRE2 251.37ms: email 433.09-&gt;126.10ms, URI 344.74-&gt;112.17ms, IP 245.66-&gt;13.10ms). Optimized branch: 11.6x faster (C++ STL 1021.10ms vs PCRE2 87.87ms) (derived from page data: ratios computed from the stated ms totals). |
| **Workload** | Find-and-count non-overlapping matches of email/URI/IPv4 patterns over a \~concatenated text corpus (learnxinyminutes docs), default engine settings, compiled C++ STL std::regex vs C PCRE2 (10.36-2) via -lpcre2-8. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (16-inch, 2019), 2.4 GHz Intel Core i9, 32 GB 2667 MHz DDR4, macOS Big Sur 11.2.3 (host running the Docker container) |
| **Compiler and flags** | std::regex: g++ 7.5.0, `-std=c++11 -O3`. PCRE2: gcc 7.5.0, `-O3 -DNDEBUG`, linked against PCRE2 10.36-2 (-lpcre2-8). Both run inside the project's Docker image. |
| **Adoption** | 1,362 stars; used as the regex engine in PHP, Apache httpd, Nginx (via a bundled copy), Wireshark, and many other projects |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/PCRE2Project/pcre2) · [benchmark](https://github.com/mariomka/regex-benchmark/blob/master/README.md) |

## Verdict

On mariomka/regex-benchmark (non-overlapping find-and-count of email/URI/IPv4 patterns over a learnxinyminutes text corpus; MacBook Pro 16-inch 2019, 2.4GHz Core i9; gcc/g++ 7.5.0, -O3, run in Docker), C PCRE2 10.36-2 totaled 251.37ms without JIT versus libstdc++ std::regex's 1023.49ms (4.07x); with JIT enabled on the benchmark's optimized branch, PCRE2 dropped to 87.87ms (11.6x). Per-pattern and total figures were re-confirmed directly against the benchmark README and both branches' benchmark.c source this session.

## Use it when

- Need full PCRE/Perl regex syntax (lookaround, recursion, \K, Unicode properties) beyond what std::regex's ECMAScript grammar supports.
- A pattern is compiled once and matched repeatedly against many/large inputs, especially with JIT enabled -- the regime the benchmark measures.
- Building a portable C (not C++) project, or embedding regex support behind an FFI boundary the way PHP/Apache do.
- Can accept an external C library dependency and manual pcre2_code/pcre2_match_data lifetime management instead of RAII.
- Targets one of PCRE2's continuously tested platforms/architectures (Linux, Windows, macOS, BSDs, Solaris, z/OS; x86, ARM, RISC-V, POWER, S390X).

## Skip it when

- Want a C++-idiomatic, exception-based, RAII-managed interface -- PCRE2's C API requires manual free() of every code/match-data/context object.
- Need exact ECMAScript regex semantics to stay compatible with existing std::regex-authored patterns.
- Run patterns against untrusted input without setting match_limit/depth_limit -- the default backtracking engine is worst-case exponential time (per pcre2.txt).
- Need rock-solid JIT concurrency today: issue #924 (open) is a ThreadSanitizer-reported data race in JIT stack creation, and #974 (open) documents interpreter/JIT match-result discrepancies.
- Want a single-header drop-in; PCRE2 must be built and linked (CMake, Autoconf, Bazel, or zig build) or vendored as source, not header-only.

## How it is fast

Two matching engines: a default depth-first backtracking interpreter, and an optional JIT (built on the bundled sljit code, checked out as a git submodule) that compiles a pattern to native machine code via pcre2_jit_compile()/pcre2_jit_match(). On the mariomka/regex-benchmark suite the non-JIT interpreter alone already beats libstdc++ std::regex 4.07x (251.37ms vs 1023.49ms total, confirmed against c/benchmark.c which calls plain pcre2_match()); enabling JIT (confirmed against the optimized branch's benchmark.c) widens that to 11.6x (87.87ms).

## Compared with alternatives

Pick PCRE2 over Boost.Regex when JIT is enabled (87.87ms vs Boost's 104.23ms on this benchmark) or when you need a portable C library rather than a Boost/C++ dependency; pick Boost.Regex instead for a closer std::regex-like C++ interface without JIT's build complexity, or if the default (non-JIT) build is all you can ship (Boost then wins, 104.23ms vs PCRE2's 251.37ms). Pick PCRE2 over RE/flex when patterns are compiled at runtime rather than generated ahead-of-time as a scanner/lexer.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (also usable as source-drop by vendoring pcre2's .c files directly, per its README) |
| **Dependencies** | none for the core library; JIT support additionally requires the bundled sljit git submodule at build time |
| **Minimum toolchain** | C99 compiler; CMake or Autoconf/./configure (Bazel and zig build also supported per the README) |
| **Platforms** | Linux, Windows, macOS, FreeBSD, OpenBSD, Solaris, z/OS; x86, ARM, RISC-V, POWER, S390X (others reported to work) |
| **Thread safety** | Core library is thread-safe (no static/global state, per pcre2.txt); a single compiled pattern can be matched concurrently from multiple threads. JIT needs a separate pcre2_jit_stack per thread. A context object shared across threads may only be read, not mutated, without caller-supplied locking. |
| **Drop-in for the baseline** | partial -- explain: a POSIX-regex compatibility wrapper (pcre2posix) exists but pcre2.txt states it is not thread-safe and does not expose full PCRE2 functionality; there is no std::regex-compatible C++ interface, so adopting PCRE2 means rewriting call sites against its native C API. |

## Gotchas

- Default (non-JIT) engine backtracks depth-first and is worst-case exponential time; set match_limit/depth_limit for untrusted patterns or input.
- JIT is opt-in: requires checking out the sljit git submodule and calling pcre2_jit_compile() yourself, or you silently keep using the slower interpreter.
- Open issue #924: ThreadSanitizer flags a data race in get_page_alignment() during concurrent pcre2_jit_stack_create(). Open issue #974: interpreter and JIT can return different match results for some patterns.
- No RAII -- every pcre2_code, pcre2_match_data, and context object must be freed explicitly (pcre2_code_free, pcre2_match_data_free, etc.).

## Caveats and trade-offs

This benchmark only exercises libstdc++'s std::regex (g++ 7.5.0 inside a Linux container); libc++ and MSVC STL are not tested, so the win is not shown against all three stdlib implementations. Patterns are simple (email/URI/IPv4) over one fixed text corpus, not a broad workload. A separate, less-detailed independent shootout (github.com/xis19/regexp_benchmark, opened this session) shows the same qualitative gap for the older PCRE (8.38, pre-PCRE2) vs std::regex on 10 small patterns, but without stated compiler/hardware, so it is not used as primary evidence here.

C API (manual pattern/match-data lifetime management, no RAII) vs std::regex's C++ object model; PCRE (Perl-compatible) syntax has some divergences from the ECMAScript grammar std::regex uses; JIT compilation is an optional extra build/runtime step that widens the speed gap further but adds complexity; requires linking an external C library instead of header-only stdlib usage.

## Maintenance

Actively maintained (pushed 2026-09-24; the project commits to backporting security and high-severity fixes for at least five years). BSD-3-Clause-with-exception license makes it freely usable and vendorable, but as a C library it must be built and linked (or its .c files dropped into a project) rather than included as a header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** mariomka/regex-benchmark README has C++ STL 1023.49 ms vs C PCRE2 251.37 ms (default) and 1021.10 vs 87.87 ms (optimized branch). Public code is in c/benchmark.c and cpp/benchmark.cpp, and run-benchmarks.php gives the flags (gcc/g++ 7.5.0, -O3). Hardware is stated as MacBook Pro 16-inch 2019, 2.4 GHz Intel Core i9, so A.
- **Verifier notes:** All per-pattern and total numbers match; ratios 4.07x and 11.6x are correctly derived. The CPU is named only as '2.4 GHz Intel Core i9' in a MBP 16-inch 2019, and the run is inside Docker on macOS. The benchmark repo is archived (last commit 2021-10-18), which does not affect PCRE2. PCRE2 LICENCE.md SPDX is 'BSD-3-Clause WITH PCRE2-exception'; 1,362 stars, last commit 2026-09-22.
- **Pages the verifier opened:**
  - <https://github.com/PCRE2Project/pcre2>
  - <https://github.com/PCRE2Project/pcre2/blob/main/LICENCE.md>
  - <https://github.com/mariomka/regex-benchmark>
  - <https://github.com/mariomka/regex-benchmark/blob/master/README.md>
  - <https://github.com/mariomka/regex-benchmark/blob/master/run-benchmarks.php>
- **Sources the enricher read:**
  - <https://github.com/PCRE2Project/pcre2>
  - <https://github.com/PCRE2Project/pcre2/blob/main/README.md>
  - <https://github.com/PCRE2Project/pcre2/blob/main/LICENCE.md>
  - <https://github.com/PCRE2Project/pcre2/blob/main/doc/pcre2.txt>
  - <https://github.com/PCRE2Project/pcre2/issues?q=performance>
  - <https://github.com/PCRE2Project/pcre2/issues?q=label%3Abug>
  - <https://github.com/mariomka/regex-benchmark/blob/master/README.md>
  - <https://github.com/mariomka/regex-benchmark/blob/master/c/benchmark.c>
  - <https://github.com/mariomka/regex-benchmark/blob/optimized/c/benchmark.c>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/pcre2project/pcre2`) · [data/wave1/enrich/raw/github_com_pcre2project_pcre2.json](../../../data/wave1/enrich/raw/github_com_pcre2project_pcre2.json) (enrichment confidence 0.92)

</details>
