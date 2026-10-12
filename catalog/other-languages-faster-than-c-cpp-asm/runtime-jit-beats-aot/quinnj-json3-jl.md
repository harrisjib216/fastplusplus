# JSON3.jl (Julia) vs nlohmann/json, json-c and Boost.PropertyTree in kostya/benchmarks JSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Deprecated Julia JSON reader built on a lazy tape; beats nlohmann/json, json-c and Boost.PropertyTree in kostya/benchmarks, loses to every fast C/C++ parser.

| | |
|---|---|
| **Beats** | nlohmann/json (C++), json-c (C library called from a C++ driver) and Boost.PropertyTree (C++) as built by kostya/benchmarks; JSON3 does NOT beat RapidJSON (all variants), Boost.JSON, simdjson, yyjson, yajl, gason or DAW JSON Link in the same table |
| **Claimed result** | Time in seconds (lower is better), kostya/benchmarks README Json table (median of runs, UPDATE: 2026-07-19): Julia (JSON3) 0.700; C++/clang++ (Nlohmann) 1.182; C++/g++ (Nlohmann) 1.266; C++/clang++ (json-c) 1.185; C++/g++ (json-c) 1.187; C++/clang++ (Boost.PropertyTree) 2.589; C++/g++ (Boost.PropertyTree) 2.907. About 1.7-1.8x faster than Nlohmann and json-c, 3.7-4.2x faster than Boost.PropertyTree (derived from page data). Slower than C++/g++ (RapidJSON) 0.154, C/gcc (yajl) 0.362, C++/g++ (Boost.JSON) 0.374, C++/clang++ (RapidJSON SAX Precise) 0.500 and Java (DSL-JSON) 0.571. |
| **Workload** | Parse a generated 524,288-object JSON file (generate_json.rb) and compute the mean of x, y and z using JSON3.read and iteration over jobj['coordinates'] (json/test.jl). |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) E-2324G (README Environment section; Docker on Debian forky/sid); README results marked UPDATE: 2026-07-19 |
| **Compiler and flags** | C++ rows measured 2025-08-17 with gcc 14.2.0 and clang 19.1.7 (flags per common/commands.mk at that date: -O3 -march=native -flto=auto); the JSON3 row was measured separately on 2025-08-19 (Julia v1.11.6, JSON3 presumably 1.14.3). The g++ 16.1.0 / clang++ 22.1.8 versions in the README environment table belong to the 2026-07-19 update, which did not re-run the Json table. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 222 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/quinnj/JSON3.jl) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

kostya/benchmarks Json test on an Intel Xeon E-2324G: parse a pretty-printed 524,288-object file from generate_json.rb and average x, y and z. Julia 1.11.6 with JSON3 took 0.700 s (median) vs nlohmann/json 1.182 s (clang++) and 1.266 s (g++), json-c 1.185 s and 1.187 s, and Boost.PropertyTree 2.589 s and 2.907 s, all built with -O3 -march=native -flto=auto -std=c++23: about 1.7-1.8x and 3.7-4.2x (derived from page data). The C++ rows were measured on 2025-08-17 with gcc 14.2.0 and clang 19.1.7, and the JSON3 row two days later in a separate run.

## Use it when

- Existing Julia code that already uses JSON3, especially the @generatetypes struct-generation feature, which the README says JSON.jl v1 does not fully replace yet.
- Reading large JSON documents in Julia and touching only some fields: unused strings and subtrees stay as tape entries and are never materialised.
- Typed decoding in Julia with JSON3.read(json, T) and StructTypes mappings instead of a generic Dict tree.
- Read-only access through the standard AbstractDict and AbstractVector interfaces; copy() turns a view into mutable Dict and Vector values when needed.

## Skip it when

- New projects: the README marks the package deprecated and points to JSON.jl v1; recent commits are compatibility fixes only (Julia 1.13 memhash, 2026-09-17).
- C or C++ code: in the same table simdjson On-Demand (0.060 s), yyjson (0.131 s), RapidJSON (0.154 s), yajl (0.362 s) and Boost.JSON (0.374 s) are 1.9-11.7x faster than JSON3's 0.700 s (derived from page data).
- Untrusted input through JSON3.read(string): short strings that name an existing file are read as that file, validation is lax, and every object key is interned as a Julia Symbol.
- Memory-tight processes: the suite reports 631.76 MiB base RSS for the Julia process (runtime, Pkg and the input text) against about 113 MiB for the C++ drivers; the peak increase (332.81 MiB) is lower than nlohmann's 359.88-447.88 MiB.
- Short-lived scripts that care about first-call latency: JIT compilation adds latency outside the measured window, and issue #33 reports extreme compile times for read(data, Vector{CustomType}).

## How it is fast

One recursive-descent pass over the bytes writes two UInt64 words per value into a preallocated Vector{UInt64} tape (sized at input length / 10, grown on demand): a type/length word and a payload. Numbers are parsed eagerly with Parsers.jl (Float64, demoted to Int64 when integral); strings and keys are stored only as offset, length and an escape bit into the input buffer, so nothing is copied, unescaped or UTF-8 validated during parsing; containers record their tape span so skipping a subtree is O(1). Object and Array views are built lazily when accessed (a Dict{Symbol,Int} key index per object, a Vector{Int} of offsets per array), whereas the nlohmann and Boost.PropertyTree drivers build an owning DOM and destroy it inside the timed call.

## Compared with alternatives

Pick it only inside Julia. DSL-JSON (Java), from the same kostya Json table, is faster (0.571 s vs 0.700 s) and beats the same three C/C++ baselines. The other Julia siblings (built-in sort, NonuniformFFTs.jl, no-BLAS matmul) are not JSON libraries.

## Integration

| | |
|---|---|
| **Form** | module (registered Julia package, installed with Pkg.add("JSON3")) |
| **Dependencies** | Parsers, StructTypes, PrecompileTools, plus Julia stdlibs Dates, Mmap and UUIDs; optional ArrowTypes package extension |
| **Minimum toolchain** | Julia 1.6 (Project.toml compat); version 1.14.3; the 2026-09-17 commit fixes Julia 1.13+ |
| **Platforms** | any platform Julia supports; the read path is plain Julia with no architecture-specific code |
| **Thread safety** | not documented (Object and Array are immutable read-only views) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the Json table is a cross-run patchwork. The C++ rows date from the 2025-08-17 maintenance run (README then listed gcc 14.2.0, clang 19.1.7, Debian trixie/sid); the Julia test had been commented out of the runner, and commit 14ae218 ('Restored Julia JSON test', 2025-08-19) re-enabled it and inserted the single JSON3 row from a separate run. The 2026-07-19 update left the Json table byte-for-byte unchanged, so the record's g++ 16.1.0 and clang++ 22.1.8 do not apply to these numbers. Julia at measurement time was v1.11.6; JSON3 was presumably 1.14.3, the latest release then.
- JSON3.read(json::AbstractString) treats any string shorter than 255 bytes that names an existing file as a path and mmaps that file (read_json_str); use JSON3.parse for strings and JSON3.parsefile for files (both added in December 2024, #302).
- Lax validation: string values are scanned only for quotes, backslashes and control characters, keys not even for control characters, with no UTF-8 validation; escapes are decoded only when a string is materialised; parse returns after the root value without checking for trailing bytes.
- The per-coordinate work in the benchmark is not free: each Object accessed in the loop allocates a new Dict{Symbol,Int} of its 5 keys and interns each key through jl_symbol_n, so iterating 524,288 objects allocates 524,288 Dicts inside the timed window. Interned symbols are never freed, which matters for documents with many distinct keys.

## Known shortcomings

- Same kostya suite, code, flags and CPU as the DSL-JSON row; mechanism from source is a flat UInt64 tape vs nlohmann's std::map DOM; loses to the fast C/C++ parsers; the package is deprecated, the JSON3 version unpinned (Pkg.add) and the Julia version unclear (README v1.11.6, Dockerfile 1.12.6).
- The kostya/benchmarks Json table is a cross-run patchwork: the C++ rows (nlohmann, json-c, PropertyTree) come from the 2025-08-17 run with gcc 14.2.0 and clang 19.1.7, while the JSON3 row was inserted alone on 2025-08-19 by commit 14ae218 ('Restored Julia JSON test'; the Julia test had been commented out of the runner) from a separate run; the 2026-07-19 update left the Json table byte-identical and re-measured only Primes plus the environment table, so the record's g++ 16.1.0 and clang++ 22.1.8 are wrong for these numbers (Julia v1.11.6, JSON3 presumably 1.14.3). JSON3.read(str) treats a string under 255 bytes that names an existing file as a path; no UTF-8 validation or trailing-byte check; the benchmark loop allocates one Dict{Symbol,Int} per object (524,288 Dicts in the timed window), so the verifier's 'no per-node objects' was wrong; peak RSS increase 332.81 MiB is below nlohmann's 359.88-447.88.

## Caveats and trade-offs

Beats only the slow C/C++ libraries; the fast ones are about 1.4-11.7x faster in the same table, yajl and Boost.JSON included (derived from page data). Work is not the same: JSON3.read fills one flat Vector{UInt64} tape (numbers parsed eagerly with Parsers.jl, strings left as offsets into the input buffer, no per-node objects), while the nlohmann test builds a full DOM of std::map nodes and std::string copies and destroys it inside the timed window; the json-c driver never frees its tree. The Julia loop is type-unstable (x = y = z = 0 starts as Int; coord["x"] returns Any), which handicaps Julia. Self-test calls calc twice on tiny inputs before timing, so most JIT compilation is outside the window but not explicitly separated. Results are printed, not cross-checked between languages. JSON3 version unpinned (Pkg.add) and Julia version ambiguous (README v1.11.6, Dockerfile 1.12.6). Package deprecated in favour of JSON.jl v1 (README notice, commit 2025-10-10), which this suite did not measure; the JSON3 README only says it is 'for speed and slick struct mapping'. [retier] Cross-run table: the C++ rows come from the 2025-08-17 run and the JSON3 row from a separate 2025-08-19 run (commit 14ae218), and the 2026-07-19 update left the Json table byte-identical. The benchmark loop allocates one Dict{Symbol,Int} per object (524,288 Dicts in the timed window). JSON3.read(str) treats a short string naming an existing file as a path; no UTF-8 validation or trailing-byte check.

Package is deprecated in its own README ('migrate to JSON.jl v1'); the last commit only fixes compatibility with Julia 1.13. Memory in the table is 631.76 MiB base + 332.81 MiB increase, far above the C++ rows. Lazy tape-based reading.

## Maintenance

Deprecated in favour of JSON.jl v1 (README notice 2025-10-10) and maintained only for compatibility (last commit 2026-09-17); MIT-licensed. Its benchmark win compares a separate 2025-08-19 Julia run against C++ rows from 2025-08-17, and it rests on slow DOM baselines.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgraded from C: same public suite and methodology as the DSL-JSON record (benchmark code json/test.jl vs json/test_nlohmann_json.cpp, json/test_libjson.cpp, json/test_boost_ptree.cpp; Julia v1.11.6 run with --optimize=3 --check-bounds=no per README and common/commands.mk; C++ flags in common/commands.mk; CPU Intel Xeon E-2324G). A missing mechanism is not a tier criterion, and the mechanism is readable in the JSON3 sources (tape-based reader).
- **Retiered** A to C: Enricher: the JSON3 row was inserted alone on 2025-08-19 from a separate run while the C++ rows date from 2025-08-17 (gcc 14.2.0, clang 19.1.7), and the recorded compiler versions belong to the 2026-07-19 environment table that never re-ran the Json table; cross-run row with the wrong toolchain recorded: A to C.
- **Verifier notes:** Numbers verified on the kostya/benchmarks README; tier raised C to A for consistency with the DSL-JSON record from the same table (code, compilers, flags and CPU all public). Main shortcomings: beats only slow DOM libraries, loses to every fast C/C++ parser incl. yajl; lazy tape against a full nlohmann DOM whose teardown is timed, so the gain is library design; package deprecated, JSON3 and Julia versions not pinned. If the orchestrator prefers to keep deprecated-package entries capped, record that as a shortcoming rather than a tier cap.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-92 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kostya/benchmarks>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/generate_json.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_nlohmann_json.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_libjson.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/xtime.rb>
  - <https://github.com/quinnj/JSON3.jl>
  - <https://github.com/quinnj/JSON3.jl/commits>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/src/read.jl>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/src/JSON3.jl>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/src/JSON3.jl>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/src/read.jl>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/src/utils.jl>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/src/structs.jl>
  - <https://raw.githubusercontent.com/quinnj/JSON3.jl/HEAD/src/write.jl>
  - <https://github.com/quinnj/JSON3.jl>
  - <https://github.com/quinnj/JSON3.jl/commits>
  - <https://github.com/quinnj/JSON3.jl/issues?q=is%3Aissue+performance>
  - <https://github.com/quinnj/JSON3.jl/issues/289>
  - <https://github.com/JuliaIO/JSON.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test.jl>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_nlohmann_json.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_libjson.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test_boost_ptree.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/generate_json.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://github.com/kostya/benchmarks/commits/master/README.md>
  - <https://github.com/kostya/benchmarks/commit/14ae218>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/14ae218/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/4d4ac9a/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/199aa74/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/common/commands.mk>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/quinnj/json3.jl`) · [data/wave14/enrich/raw/github_com_quinnj_json3_jl.json](../../../data/wave14/enrich/raw/github_com_quinnj_json3_jl.json) (enrichment confidence 0.6)

</details>
