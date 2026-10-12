# Zig (benchLANG strings workload, 19x19 word equality)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig 0.16 benchLANG Strings row: 19x19 short-word equality loop 1.42x faster than GCC -O3 C (memcmp) and 1.46x faster than C++ (string_view ==).

| | |
|---|---|
| **Beats** | C (GCC 16.2.0, `-O3 -march=native -flto -funroll-loops`, glibc memcmp per equal-length pair) and C++ (g++ same flags, std::string_view ==, libstdc++). |
| **Claimed result** | README results table (3 September 2026, one run per language), String Operations column: Zig 1.504 s, C 2.132 s, C++ 2.190 s, C# 2.235 s, D 2.351 s, Go 2.532 s, Ada 2.603 s, Rust 2.621 s, Nim 2.804 s. Zig is 1.42x faster than C and 1.46x faster than C++ (derived from page data). Zig is not faster overall: Fibonacci Zig 3.181 s vs C 1.694 s, and C ranks first on total runtime (9.762 s vs Zig 10.737 s, Zig factor 1.10x). |
| **Workload** | benchLANG 'Strings': 5M iterations of comparing every pair of the 19 words of a constant sentence for equality (19x19 pairs per iteration). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X locked at 3.5 GHz, 48 GB DDR4-3600, Arch Linux; one run per language, 3 September 2026 |
| **Compiler and flags** | Zig 0.16.0 `zig build-exe -OReleaseFast -mcpu=native -fstrip -lc`; C `gcc -O3 -march=native -flto -funroll-loops -ffp-contract=off -s` and C++ `g++ -std=c++20` with the same flags, GCC 16.2.0 from nixpkgs-unstable. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Adoption** | 8 stars, 0 forks |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/GlebOlsen/benchLANG) · [benchmark](https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/README.md) |

## Verdict

benchLANG's 3 September 2026 run on a Ryzen 9 5900X locked at 3.5 GHz (Arch Linux, 48 GB DDR4-3600) timed the Strings workload at 1.504 s for Zig 0.16.0 (zig build-exe -OReleaseFast -mcpu=native -fstrip -lc, std.mem.eql) against 2.132 s for C and 2.190 s for C++ built by GCC 16.2.0 with -O3 -march=native -flto -funroll-loops (glibc memcmp and libstdc++ string_view ==). Zig is 1.42x faster than C and 1.46x faster than C++ on this column (derived from page data), with identical checksums enforced by the analyzer and toolchains pinned in flake.nix.

## Use it when

- As a data point that inlined small-string equality beats an out-of-line memcmp call when the strings are a handful of bytes, e.g. token, keyword or identifier comparison in parsers and interpreters.
- When you already write Zig and compare many short []const u8 slices: std.mem.eql gives the fast path without extra code.
- As a template for a C or C++ fix: an inline length-dispatched compare (overlapping 4-byte loads for 4-16 bytes, three byte checks below 4) copies easily into a hot equality loop (inference; not measured in this repo).

## Skip it when

- As evidence that Zig is faster than C in general: in the same table C ranks first overall (9.762 s vs Zig 10.737 s) and Zig loses Fibonacci(45) 3.181 s vs 1.694 s.
- For long strings or ordering comparisons: the measured words are 2-6 bytes, and the win comes from avoiding the call, not from a faster bulk compare; above 16 bytes eqlBytes switches to vector chunk loops with no measurement here.
- As a stable margin: the table is one run per language on 3 September 2026; the runner supports --runs N but the published numbers do not use it.
- If you need lexicographic order (memcmp's sign or std::string_view::compare): std.mem.eql answers equality only.

## How it is fast

The gain is the Zig standard library's byte-slice equality, not Zig code generation. std.mem.eql on u8 slices calls eqlBytes, which after the length check returns true at once when both slices share a pointer (the 19 diagonal pairs) and handles slices of 16 bytes or less inline and branch-light: three byte XORs below 4 bytes, otherwise four possibly overlapping 4-byte loads ORed together (read on the GitHub master of November 2025; the verifier read the same code at 0.15.1; the 0.16.0 source was not reachable). The C program does the same length filter but then calls glibc memcmp for each of the 103 equal-length pairs per iteration, a variable-length libc call GCC does not expand inline at -O3 (disassembly not checked); the C++ string_view == also compares sizes first and then goes through char_traits::compare, which in libstdc++ ends in a memcmp call (libstdc++ source not read this session). Per iteration that is about 300 ns for Zig against 426 ns for C, roughly 1.2 ns saved per equal-length compare (derived from page data).

## Compared with alternatives

Pick this entry when the question is specifically about short-string equality cost; for realistic text workloads the catalogued Zig LangArena Etc::Words entry (0.91 s vs C++ 1.638 s, tokenising and hash counting) and csv-zero show Zig wins on whole tasks, and the Rust and Go LangArena Etc::Words entries cover the same task in other languages.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Zig 0.16.0 standard library (std.mem, std.Io); -lc links libc only for std.heap.c_allocator in the binary-trees workload |
| **Minimum toolchain** | Zig 0.16.0 as measured (the program uses the 0.16 std.Io and std.process.Init APIs, so older Zig releases will not build it) |
| **Platforms** | Measured on x86-64 Linux only (flake.nix pins x86_64-linux); eqlBytes' fast path is enabled on every Zig backend except the self-hosted aarch64, powerpc, riscv64 and SPIR-V backends (LLVM builds use it) |
| **Thread safety** | Not applicable: single-threaded workload |
| **Drop-in for the baseline** | no |

## Gotchas

- Unequal work on the diagonal: std.mem.eql returns true without reading bytes when both slices share a pointer, so 19 of the 103 equal-length compares per iteration are skipped in Zig while C and C++ still call memcmp on them. That is legitimate library behaviour, but part of the 42% is less work, not faster work.
- Different setup on each side: Zig tokenises the compile-time constant sentence (Zig and LLVM may specialise word lengths or trip counts), C tokenises a heap strdup copy with strtok, and C++ fills a heap std::vector; whether LLVM exploited the constant was not checked (no disassembly), and the README explicitly counts constant folding as a valid result.
- Same LLVM backend, different library: Rust (rustc 1.97.1, also LLVM) takes 2.621 s on the same loop with plain == on &str, slower than C, which points at the equality routine rather than the code generator (inference from the README table and languages/Rust/bench.rs).
- The Zig std source for 0.16.0 could not be read here (the tag is not on the GitHub mirror, whose last lib/std/mem.zig commit is 22 November 2025, and codeberg.org was blocked), so the eqlBytes description assumes the routine did not change between that commit and the 0.16.0 release.

## Known shortcomings

- One run per language; the win comes from Zig's std.mem.eql (inlined short compare with a pointer-equality shortcut) vs out-of-line glibc memcmp, not codegen; C is still first overall in the suite.
- The win comes from Zig's std.mem.eql (eqlBytes): the short-slice compare is inlined and true is returned on pointer equality, which skips the 19 diagonal pairs of the 103 equal-length compares per iteration, while C calls out-of-line glibc memcmp on all 103, so part of the 42% gap is less work, not faster work. Rust is also LLVM-based yet slower than C (2.621 s), so the cause is the library routine, not codegen. No harness bug. Zig 0.16.0's mem.zig could not be read (GitHub tag 404, codeberg blocked), so master of 2025-11-22 was read instead.

## Caveats and trade-offs

One run per language (the runner supports --runs 3 but the published table is a single run); the CPU is locked at 3.5 GHz and the gap is 42%, so noise alone is unlikely to explain it. The win belongs to the Zig standard library's equality routine, not to Zig codegen: std.mem.eql inlines a branch-light short-slice compare (three byte XORs below 4 bytes, four overlapping 4-byte loads up to 16 bytes) and returns early when both slices share a pointer, which skips the byte compare on the 19 diagonal pairs of each iteration; the C and C++ versions call out-of-line glibc memcmp (variable length, so GCC presumably does not inline it; disassembly not checked) for each of the 103 equal-length pairs of the 361 per iteration. A C version with an inlined compare would likely close the gap (inference). The input is a compile-time constant 19-word sentence (README says constant folding counts as a result); C tokenises a strdup copy with strtok at run time while Zig tokenises the constant slice, so LLVM may specialise more (not checked). Zig 0.16.0's lib/std/mem.zig was not readable (the tag is not on the GitHub mirror); the eqlBytes code was read at 0.15.1 and master. Rust and Go are also slower than C on this task, and C ranks first overall in the same repository. [retier] Enricher: the win comes from Zig's std.mem.eql (eqlBytes), whose short-slice compare is inlined and which returns true on pointer equality, skipping the 19 diagonal pairs of the 103 equal-length compares per iteration while C calls out-of-line glibc memcmp on all 103, so part of the 42% gap is less work. Rust is also LLVM-based yet slower than C (2.621 s), so the cause is the library routine, not codegen; no harness bug found.

ReleaseFast removes Zig's safety checks. The Nix flake pins every toolchain, and the analyzer marks the ranking invalid if checksums differ between languages (README).

## Maintenance

Small single-author MIT repo (8 stars, 0 forks, 42 commits, last commit 2026-09-03) with Nix-pinned toolchains, so anyone can rerun it; the result is one run of one micro-workload and documents a standard-library technique, not something to adopt as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the benchmark code is public for both sides (languages/C/bench.c, languages/C++/bench.cpp, languages/Zig/bench.zig, run_benchmarks.sh, Nix-pinned toolchains in flake.nix/flake.lock), and the README states the compilers (GCC 16.2.0, Zig 0.16.0), the exact flags and the CPU (Ryzen 9 5900X locked at 3.5 GHz). The record's C cap ('source states no mechanism') is not a tier rule; the mechanism is now stated from the Zig standard library source. Single run per language is a caveat, not a tier criterion.
- **Verifier notes:** Numbers and flags match the README exactly; same algorithm and equivalent opt level (gcc/g++ -O3 -march=native -flto -funroll-loops vs zig -OReleaseFast -mcpu=native), so tier upgraded to A on the published methodology. Record shortcomings: one run per language, a narrow microbenchmark on tiny constant strings, the win comes from Zig's std.mem.eql (inlined short compare plus pointer-equality shortcut that does slightly less work on the diagonal) against an out-of-line glibc memcmp call, and C still wins on total runtime.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/README.md>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/C%2B%2B/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/languages/Zig/bench.zig>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/HEAD/run_benchmarks.sh>
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages/C>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages/C++>
  - <https://github.com/GlebOlsen/benchLANG/tree/main/languages/Zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/mem.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.1/lib/std/mem.zig>
- **Sources the enricher read:**
  - <https://github.com/GlebOlsen/benchLANG>
  - <https://github.com/GlebOlsen/benchLANG/commits/main>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/README.md>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C/bench.c>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/C%2B%2B/bench.cpp>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/Zig/bench.zig>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/languages/Rust/bench.rs>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/analyze_results.sh>
  - <https://raw.githubusercontent.com/GlebOlsen/benchLANG/main/flake.nix>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/mem.zig>
  - <https://github.com/ziglang/zig/commits/master/lib/std/mem.zig>
  - https://raw.githubusercontent.com/ziglang/zig/0.16.0/lib/std/mem.zig (404)
  - https://codeberg.org/ziglang/zig/raw/tag/0.16.0/lib/std/mem.zig (blocked, CONNECT 403)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/glebolsen/benchlang#strings`) · [data/wave14/enrich/raw/lang_zig_glebolsen_benchlang_strings.json](../../../data/wave14/enrich/raw/lang_zig_glebolsen_benchlang_strings.json) (enrichment confidence 0.75)

</details>
