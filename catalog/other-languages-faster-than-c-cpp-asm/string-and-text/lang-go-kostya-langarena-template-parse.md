# Go: LangArena Template::Parse

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Plain Go byte loop with a built-in map for {{ key }} substitution; about 1.18x faster than every C and C++ build in LangArena Template::Parse.

| | |
|---|---|
| **Beats** | C and C++ hand-written {{ key }} template scanners with a hash-map lookup per placeholder; best C/C++ row is C/Gcc/Unsafe at 0.884 s, C/Gcc prod 0.897 s, C++/G++ prod 0.973 s |
| **Claimed result** | Go 0.751 s (Go/Opt 0.747 s) vs the best of all 16 C/C++ rows, C/Gcc/Unsafe at 0.884 s (-O3 -march=native -ffast-math), and the prod rows C/Gcc 0.897 s, C/Clang 0.946 s, C++/G++ 0.973 s and C++/Clang++ 1.089 s: about 1.18x faster than the best C/C++ row and 1.27x faster than the best C++ row, C++/G++/Unsafe 0.951 s (derived from page data). Zig (0.834 s) and Rust/PGO (0.876 s) are only marginally ahead of the best C row; Zig/Unchecked (ReleaseFast) runs 0.374 s. Peak RSS 75 MB for Go vs 41 MB for C/Gcc. The lead is stable across the five monthly runs checked: Go 0.784 s vs best C row 0.894 s on 2026-07-14 (1.14x), 0.781 vs 0.883 s on 2026-08-14 (1.13x), 0.803 vs 0.884 s on 2026-09-03 (1.10x), 0.776 vs 0.894 s on 2026-09-18 (1.15x) and 0.751 vs 0.884 s on 2026-10-05 (1.18x) (all derived from page data; Go 1.26.5 before September, 1.27.1 after). |
| **Workload** | Scan a generated HTML template of 50,000 table rows (about 150,000 {{ key }} placeholders with surrounding spaces, plus single-brace decoys) byte by byte, trim each key, look it up in a 150,001-entry variable map and append the value to a pre-reserved output buffer; 50 timed iterations after 10 untimed warm-up iterations. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37; the run notes say the host moved from Ubuntu to Arch Linux for this run) |
| **Compiler and flags** | C/C++: Clang 22.1.8 (official LLVM release tarball; docker/base_clang points cc, c++, gcc and g++ at clang via update-alternatives and sets no -stdlib flag, so the clang rows link the system libstdc++) and GCC 16.0.1 20260322 (trunk, Ubuntu build), -std=c++20, glibc malloc. Headline 'prod' build (cpp/Makefile CXXFLAGS_PROD, c/Makefile CFLAGS_PROD): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections (not -O3). The same suite also builds 'Fast' (-O3 -march=native -mtune=native -pipe ..., -flto=thin at link), 'Unsafe' (-O3 -march=native -ffast-math ..., -flto=full at link) and 'PGO' (-O2 plus -fprofile-instr-use or -fprofile-use) variants; the LTO flags appear only in LDFLAGS, so those builds probably get no real LTO (inference from the Makefiles). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO configurations were compared (instrumented PGO/Gen rows and the author's mycc/cproc compilers excluded; they are slower anyway). Go 1.27.1 (go.mod says go 1.24.0) 'go build -buildvcs=false' with default settings (no opt levels in Go); 'Go/Opt' adds -trimpath and a static link. Zig 0.17.0 'zig build build-zig': zig/build.zig builds this 'Zig' row with optimize = .ReleaseSafe (LLVM release optimisation with runtime safety checks kept) and b.standardTargetOptions(.{}), which defaults to the native host CPU, so it is closer to -O3 -march=native with bounds checks than to the generic -O2 prod C/C++ build; 'Zig/Unchecked' is the same source at .ReleaseFast. Rust: rustc 1.99.0 'cargo build --release'. Versions and build/run commands from the results file's version, build-cmd and run-cmd fields. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. The loop is nearly identical in Go and C++; the Go key is a zero-copy substring plus strings.TrimSpace, while the C++ test copies the key with substr and trim (this agent's reading of the sources, small effect). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In the 2026-10-05 LangArena run on an AMD Ryzen 7 3800X (Linux), Go 1.27.1 rendered the 6.0 MB template 50 times in 0.751 s, against 0.884 s for the best of 16 C/C++ configurations (C/Gcc/Unsafe, GCC 16.0.1 trunk, -O3 -march=native -ffast-math), 0.897 s for C/Gcc at -O2 and 0.973 s for C++/G++ at -O2 with libstdc++: about 1.18x over the best C/C++ row (derived from page data), with a 1.10-1.18x lead in five monthly runs since 2026-07-14.

## Use it when

- Choosing a language for a template renderer, log rewriter or other scan-and-substitute tool: idiomatic Go with a built-in map lands at or ahead of naive idiomatic C and C++.
- Workloads dominated by many small string-key lookups (150k keys of 4-15 bytes here) against a map too large for L2, where Go's map and allocation-free slicing help.
- As a reference point when your C++ code copies keys into std::string or uses std::unordered_map on a hot path: this row shows what that costs.
- Linux x86-64 batch jobs where Go's 1.8x higher peak RSS is acceptable.

## Skip it when

- As evidence that Go beats tuned C or C++: the same scan in Zig ReleaseFast runs 0.374 s, twice as fast as Go, and a C++ version with std::string_view keys and an open-addressing map was never measured.
- Inside an existing C++ codebase: the gain comes from the map and slicing idioms, which C++ can adopt (string_view keys, a flat hash map) without changing language.
- Memory-tight services: Go peaked at 75 MB RSS against 41 MB for C/Gcc and 38.6 MB for C++/G++ on this task.
- Latency-sensitive paths: each iteration allocates a fresh 9 MB output buffer, so the GC runs during the timed loop, and only total runtime is reported.

## How it is fast

Not code generation: the loop is the same on every side. The Go key is a zero-copy substring of the template, and the lookup goes to Go's built-in map (a Swiss-table design since Go 1.24, with an AES-based string hash on amd64; background knowledge, not checked in the Go sources this session). The C test mallocs and frees a copy of every key (150,001 per iteration) and looks it up in uthash (default Jenkins hash unless HASH_FUNCTION is set, which the sources do not do; chained buckets of separately malloc'd nodes, keys and values); the C++ test builds a std::string per key (49,000 of the 150,001 untrimmed keys exceed libstdc++'s 15-byte small-string buffer and hit the heap) and looks it up in a node-based std::unordered_map. No profile exists, so the split is unknown: the lookups into a 150,001-entry map are cache-miss bound, but the suite's Zig row drops from 0.834 s (ReleaseSafe) to 0.374 s (ReleaseFast) on the same zero-copy code, so the per-byte loop and its checks also weigh heavily (inference from the results and sources).

## Compared with alternatives

Among the catalogued LangArena rows this is the Go text-substitution data point, next to Go Distance::NGram (0.603 s vs 0.822 s) and Go Etc::Words (1.129 s vs 1.587 s); those two show larger margins over C++ than this 1.18x. If you need the fastest code for this exact task, the suite's own Zig ReleaseFast row (0.374 s) is about twice as fast as Go.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Go toolchain only (standard library strings package and built-in map); the measured build is go 1.27.1, go.mod says go 1.24.0 |
| **Minimum toolchain** | Go 1.27.1 measured (Go 1.26.5 in the July and August runs); go.mod declares go 1.24.0 |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X); the code is portable Go |
| **Thread safety** | Not documented; the task is single-threaded and Go maps are not safe for concurrent writes |
| **Drop-in for the baseline** | no |

## Gotchas

- The comparison is between allocation and container idioms, not compilers: C mallocs and frees a key copy per placeholder and uses uthash with strdup'd keys and values; C++ copies keys into std::string and uses std::unordered_map&lt;std::string,std::string&gt;. Rust, which also slices keys without copying but uses the default SipHash HashMap, runs 0.986 s, behind the best C row, so the hash map and hash function matter as much as the copies (inference from the results file).
- Times are wall clock on an 8-core CPU while every implementation is single-threaded: Go's concurrent GC can do its marking on otherwise idle cores, which C and C++ never need, and runtime.GC() runs before the timer starts. No CPU-time column was found in the results file.
- One timing per configuration per monthly run, no variance reported; within the same run C++/Clang++/PGO (1.386 s) is 27% slower than plain C++/Clang++ (1.089 s), so differences of about 10% between rows should not be over-read. The Go lead itself held at 1.10-1.18x in five monthly runs.
- No correctness bug found: all three sides scan identically (same '{{'/'}}' rules and same fallthrough when '}}' is missing), checksums are verified, and Go's Unicode-aware TrimSpace versus the C/C++ space-and-tab trim makes no difference on this input.

## Known shortcomings

- Small margin (1.18x, 1.10-1.18x over 5 monthly runs) from an allocation idiom, not codegen: zero-copy key slices and a Swiss-table map vs a malloc'd key copy per placeholder (C) and std::string temporaries (C++); 75 vs 41 MB RSS. Subjective AI-assisted suite, C/C++ production rows at -O2 with inert link-only -flto.
- No correctness bug: C, C++ and Go run the same scan and the checksums verify. The 1.18x margin comes from idioms: C mallocs a key copy per placeholder plus uthash, C++ builds std::string keys (49,000 of 150,001 per iteration go to the heap) plus a node-based std::unordered_map, Go uses zero-copy slices plus the built-in map. Timing is wall clock while Go's concurrent GC can use idle cores (no CPU-time column). Zig ReleaseFast at 0.374 s is 2x faster than Go on the same task; Go peak RSS 75 MB against C's 41 MB.

## Caveats and trade-offs

Small margin (1.10-1.18x over the best C/C++ row in five monthly runs) that rests on allocation and container idioms: the C test mallocs and frees a copy of every key, and the C++ test builds std::string temporaries, where C with a length-keyed HASH_FIND or C++ with std::string_view keys and a flat map would avoid that (inference, not measured); Go does not win on codegen, and its per-byte strings.Builder.WriteByte loop is if anything heavier than C's direct buffer store. Go's harness calls runtime.GC() after warm-up so the timed loop starts with a clean heap, but collections during the loop (a new output buffer of about 1.5x the template per iteration) are timed; Go uses 75 MB peak RSS against 41 MB for C. The C/C++ prod rows are -O2 with hardening flags, but the -O3 -march=native Fast and Unsafe rows and the PGO rows were also compared and lose, and the Makefiles pass the LTO flags only at link time. Go also loses badly on other text tests in the same suite (Etc::LogParser 30.9 s). LangArena's README calls it not an objective, peer-reviewed or industry-standard suite (rules and library choices are the author's judgment) and says AI tools helped translate the tests from Crystal, with the author reviewing them. Each configuration is timed once per monthly run (no repeats or variance within a run); every language, C and C++ included, runs 20% of the iterations as untimed warm-up and checksums are verified. The per-benchmark ratios are derived from the results files, not stated by the suite. Rows were picked by the search agent as text tests where a Rust, Zig or Go production row beats every C and C++ row; most other text tests in the suite go the other way (for example Base64::Encode and Base64::Decode, where C is about 3x faster than Rust, and Distance::Jaro, a tie). [retier] C, C++ and Go run the same scan and the checksums verify. The margin comes from idioms: C mallocs a key copy per placeholder plus uthash, C++ builds std::string keys (49,000 of 150,001 per iteration go to the heap) plus a node-based unordered_map, Go uses zero-copy slices plus the built-in map. Timing is wall clock while Go's concurrent GC can use idle cores (no CPU-time column). Zig ReleaseFast at 0.374 s is 2x faster than Go; Go peak RSS 75 MB against C's 41 MB.

Go uses about 1.8x the memory of the C row.

## Maintenance

Active MIT-licensed suite (41 stars, last commit 2026-10-08, monthly reruns, no open or closed issues about this task); the author calls it subjective and says AI tools helped translate the Crystal originals, so treat the row as a language-level data point, not a component to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: public code for every side (golang/template.go TemplateParse.Run, c/src/template.c TemplateParse_run, cpp/src/template.cpp TemplateParse::run; workload in run.js: count 50,000, 50 iterations), C/C++ flags in the Makefiles, compiler versions, build commands and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js. The same scanning loop runs on every side, the mechanism can be read from the sources (allocation-free key slicing in Go against a malloc'd key copy per placeholder in C and std::string temporaries in C++), and the lead holds in all five monthly runs checked (1.10-1.18x), so the no-mechanism cap and the noise concern do not apply.
- **Verifier notes:** Confirm, upgraded C to A: the numbers match the Template::Parse-runtime rows of the 2026-10-05 results file, the same algorithm runs on every side, and four earlier monthly runs show the same 1.10-1.15x lead, so the record's noise concern is unfounded. Shortcomings to record: small margin driven by allocation idioms (malloc'd key copies in C, std::string temporaries in C++, zero-copy substrings and a Swiss-table map in Go), not codegen; 1.8x the memory of C; one timing per configuration per run; subjective AI-assisted suite. Metadata checks out (MIT, 41 stars, not a fork, last commit 2026-10-08).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-36 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/tree/master/results>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/clang_cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base_clang>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.h>
  - <https://github.com/kostya/LangArena/tree/master/golang>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/template.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/benchmark.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/go.mod>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/template.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/template.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/template.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue+template>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/template.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/benchmark.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/go.mod>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/template.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.h>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/template.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/template.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/template.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/template.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:go/kostya/langarena#template-parse`) · [data/wave14/enrich/raw/lang_go_kostya_langarena_template_parse.json](../../../data/wave14/enrich/raw/lang_go_kostya_langarena_template_parse.json) (enrichment confidence 0.7)

</details>
