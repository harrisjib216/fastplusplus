# Hare 0.26.0.1: compile throughput in nordlow/compiler-benchmark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Hare` · `GPL-3.0-only AND MPL-2.0` · 🟢 active

> Hare 0.26 toolchain (harec plus QBE) builds a generated 40,000-function program 2.6-3.0x faster than gcc -O0; clang wins.

| | |
|---|---|
| **Beats** | C (gcc-15 15.3.0, gcc 16.2.1, clang 23.1.1) and C++ (g++-15 15.3.0, g++ 16.2.1, clang++ 23.1.1) compiling the same generated arithmetic translation unit (200 call chains of depth 200, 40000 functions) with default optimization (no -O flag) |
| **Claimed result** | README table: Hare (hare 0.26.0.1) Total 150 us/f (150 build + 0.05 run), against C (gcc-15 15.3.0) 392, C (gcc 16.2.1) 454, C++ (g++-15) 303, C++ (g++ 16.2.1) 486, C++ (clang++ 23.1.1) 236. About 2.6x faster than gcc-15, 3.0x than gcc 16.2.1, 2.0x than g++-15 and 1.6x than clang++ (derived from page data). C (clang 23.1.1) is faster than Hare at 118 Total. |
| **Workload** | Microseconds per function to build (compile plus link) a single generated file of 200 x 200 trivial i64 add-chains; the 'Total' column is build plus a run of the resulting binary; Hare has no compile-only (object) measurement in the harness |
| **Metric** | compile-time |
| **Hardware** | AMD Ryzen AI 7 350 (8+8 cores) at 5.09 GHz, Arch Linux, sample run as of 2026-09; one worker per core, tasks pinned with sched_setaffinity and run in parallel, minimum of up to 10 runs |
| **Compiler and flags** | Harness file cbench (the README's ./benchmark). Hare: 'hare build -o &lt;bin&gt;' in default (non-release) mode, HARECACHE pointed at a fresh directory once per operation; the 'check' operation also runs 'hare build -o &lt;tmp&gt;', so Hare's Check column (135.9 us/f) is a full build. C with gcc and clang: '-Wall -Wextra' (clang also '-fno-color-diagnostics -fno-caret-diagnostics -fno-diagnostics-show-option'), no -O flag (GCC and Clang default -O0), build = compile plus link with '-o &lt;bin&gt;'. C++ with g++ and clang++: only '-Wno-c++11-extensions', no -O flag. Hare's QBE backend has no optimization levels and runs its fixed pass pipeline on every build. Linker and assembler versions are not stated. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not given. The README offers no Hare-specific explanation; it contrasts single-pass compilers such as tcc with multi-pass optimizing compilers in general. Inference: Hare's small language and module system avoid header parsing; not stated by the source. |
| **Adoption** | benchmark repo 167 stars; Hare stars not available (sr.ht hosted) |
| **Links** | [repository](https://git.sr.ht/~sircmpwn/hare) · [benchmark](https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md) |

## Verdict

In one run of nordlow/compiler-benchmark (tables updated 2026-10-09) on an AMD Ryzen AI 7 350 under Arch Linux, hare 0.26.0.1 in default debug mode built a generated program of 200 x 200 i64 add-chain functions, link included, in 150 us per function. The same C program at -O0 with -Wall -Wextra took 392 us/f with gcc 15.3.0 (193.8 object-only) and 454 with gcc 16.2.1. The C++ version took 303 with g++ 15.3.0, 486 with g++ 16.2.1 and 236 with clang++ (untemplated). clang 23.1.1 C was faster than Hare at 118.

## Use it when

- You already write Hare and want default debug builds of large generated files to stay cheaper than GCC -O0 builds: 150 us per function against 303 to 486 for the gcc and g++ rows.
- Static, libc-free binaries on Linux or FreeBSD (x86-64, aarch64, riscv64 per the 2022 announcement; the current platform list could not be checked) where a small toolchain is preferred.
- Toolchain comparisons: Hare lands next to Odin (147) and C3 (153) on this Total column.

## Skip it when

- When clang is available: clang C built the same program faster (118 us/f Total, 77.9 object-only), and so did clang++ on the templated variant (107).
- On memory-limited build hosts: the sampled peak RSS, summed over the process tree, was 110.8 kB per function, about 4.4 GB for this file (derived from page data), against 17.2 to 17.6 kB/f for the gcc builds and 6.8 for clang.
- On Windows or macOS: the project has no official support for non-free platforms (2022 announcement); only a community macOS port exists.
- For optimized-build or code-quality comparisons: only the default debug mode was measured (no -R), and QBE output was not compared with gcc -O2.
- To predict real project builds: the workload is one synthetic file of 40,000 i64 add-chain functions.

## How it is fast

The benchmark gives no Hare-specific reason. Inference, not measured: harec lowers straight to QBE's SSA IL, and QBE runs a short fixed pass list with no optimization levels, while GCC at -O0 still lowers through GENERIC, GIMPLE and RTL. The default build caches compiled standard-library modules (rt, os and the debug:: runtime that debug mode imports) in HARECACHE, and the reported minimum is over two repetitions, so the faster run probably reused modules compiled by the first, much as a C build links a prebuilt libc.

## Compared with alternatives

On this Total column Hare (150) ties Odin (147) and C3 (153) and trails Zig (110), Free Pascal (138, 103.6 object-only) and dmd (13), while using about 3x Odin's and 13x Zig's build memory per function (derived from page data). Pick Hare for a small, libc-free toolchain, not for the fastest builds.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (the 'hare' build driver plus harec, qbe and binutils; distribution packages such as Arch's hare 0.26.0.1 per search snippets, or a source build) |
| **Dependencies** | harec, qbe, an assembler and linker (as, ld); no libc by default |
| **Minimum toolchain** | hare 0.26.0.1 as measured (0.26.0 announced on the Hare blog 2026-02-13 per search results) |
| **Platforms** | Linux and FreeBSD on x86-64, aarch64 and riscv64 per the 2022 announcement (later BSD ports not confirmed); no official Windows or macOS; measured only on x86-64 Arch Linux |
| **Thread safety** | not applicable (command-line compiler); 'hare build' builds modules in parallel with -j defaulting to os::cpucount(), which counts the sched_getaffinity mask (source of a GitHub mirror), so under the harness's one-CPU pin it builds serially |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: Hare's Check cell is a second full build. bm_Hare's 'check' runs 'hare build -o &lt;tmp&gt;', the same command as 'build' apart from the output path, so Check (135.9 us/f) against Build (150) shows about 10% noise between identical commands, and the two RSS cells match (110.8). Hare has no link-free Compile number. Taken conservatively, Hare's full build including the link (150) against GCC's object-only compiles is about 1.3x faster than gcc 15 (193.8), 1.8x than g++ 15 (269.6) and 2.7x than gcc 16.2.1 (400.1), while clang++ object-only (82.4) is 1.8x faster than Hare (derived from page data).
- Cache and repetitions: HARECACHE is wiped once per operation, not per repetition. Every repetition compiles byte-identical source (cbench draws its random-constant pool once per process and restarts the index for each file) under a new file name, and builds of about 6 s keep the minimum of only 2 runs. The 6 s minimum shows the main module was rebuilt, but the standard-library modules compiled by the first run were probably reused.
- Unequal work, mostly against Hare: default (non -R) mode imports the debug:: runtime-support module (hare-build man page per search snippets) and QBE always runs its passes, while the C side builds at -O0 with only -Wall -Wextra added. The 222 B/f output size includes that debug runtime.
- One noisy run: tasks run concurrently, one pinned worker per core on a hybrid Zen 5 and Zen 5c part, and nothing checks the program's output. The 1.6x lead over clang++ rests on clang++'s untemplated Total (236), which is 2.9x its own Compile (82.4), while its templated Total is 107. The README summary now quotes the table's figures (clang 118), so the record's note about it citing clang 87 is out of date, but its section 3 still quotes GCC compile figures (226.7 to 382.6 us/f) that differ from the table (193.8 to 400.1).

## Known shortcomings

- Wins over GCC, g++ and clang++ only; clang C is faster (118 vs 150 us per function). Synthetic source, a single sample per cell with parallel tasks, and the README's Conclusions numbers drift about 30% from the tables; cbench builds gcc at -O0, which favours the baseline. Hare's licence and last commit unverified (git.sr.ht unreachable).
- Enricher: HARECACHE is wiped per operation, not per repetition, and builds keep the minimum of 2 runs, so the reported Build probably reused stdlib modules compiled in run 1 (C compilers get no such cache); the Check cell (135.9) is a second hare build, about 10% noise against Build (150); default debug mode pulls in the debug:: runtime; hare -j follows the affinity mask, so builds run serially under the harness pin; peak RSS about 4.4 GB. Conservative ratio: about 1.3x over gcc-15's object-only compile. Licence read from a GitHub mirror (Angluca/hare); last commit unverified.

## Caveats and trade-offs

repo_url is the canonical upstream named by packagers; git.sr.ht does not resolve from this sandbox (getaddrinfo ENOTFOUND), so the licence, star count and last commit of Hare itself are unverified (the GPL-3.0-only compiler and MPL-2.0 standard library split comes from packager metadata in search results). This is a compile-throughput claim for the toolchain (harec plus QBE against GCC's middle and back end), not a runtime or language-level win: clang compiling the same C file is faster than Hare (118 against 150 Total), so 'Hare faster than C' holds only against GCC and g++ and against clang++. The C/C++ side builds at -O0, which is GCC's fastest compile mode and so favours the baseline rather than crippling it, while QBE always runs its optimization passes. The workload is one synthetic 40000-function translation unit of i64 add chains with no headers and almost no standard library, so it does not predict real build times (the README says so). Within one invocation every repetition compiles byte-identical source (the constant pool and its index restart per file), and HARECACHE is wiped once per operation rather than per repetition, so the minimum-of-runs Hare build reuses standard-library modules (os, rt) cached by the first repetition, comparable to C linking a prebuilt libc; the 6-second per-build time shows the main module itself was not a cache hit. Tasks for all compilers run in parallel, one pinned worker per performance core, so concurrent builds share caches and memory bandwidth. The table is one sample run; the README's own Conclusions quote different numbers for the same machine (clang 87 us/f against 118 in the table, gcc 418 to 455 against 392 to 454), so results move by up to about 30% between samples, which does not threaten the 2.6x to 3.0x lead over GCC but does narrow the 1.6x lead over clang++. Warning flags are applied to C builds and not to Hare. The README was last edited 2026-10-12 (wording only) and its tables 2026-10-09. [retier] Enricher: HARECACHE is wiped per operation, not per repetition, and the minimum of 2 runs is kept, so the build probably reused cached stdlib modules; Check is a second build (about 10% noise); builds run serially under the harness pin; peak RSS about 4.4 GB; conservative ratio about 1.3x over gcc-15 object-only.

Hare has the highest memory footprint among the fast compilers in the table: 110.8 kB of peak RSS per function against 3.3 to 17.6 kB for the C compilers and 24.6 for Free Pascal. Output is 222.0 bytes per function against 121.1 for gcc.

## Maintenance

Hare is actively released (0.26.0 on 2026-02-13 per search results, and 0.26.0.1 is packaged by Arch and Alpine per search snippets), but git.sr.ht, harelang.org and the distro package pages are unreachable from this sandbox. The licence split (GPL-3.0-only for hare and harec, MPL-2.0 for the standard library) is taken from a GitHub mirror's README, and the last commit is unverified. The evidence is one single-machine run of a public harness in which Hare's Check column is just a second full build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** The README 'Modern Systems Languages' table (AMD Ryzen AI 7 350, Arch Linux, 2026-09 sample run) has Hare 150=150+0.05 us/f against C gcc-15 392, gcc 16.2.1 454, g++-15 303, g++ 16.2.1 486, clang++ 236 and clang C 118, exactly as claimed; the harness code is public (cbench, MIT: bm_Hare, bm_C_and_Cxx_using_gcc, bm_C_and_Cxx_using_clang, gcc_clang_op_flags), compiler versions are in the table, flags are in the script and the CPU model is stated, so A holds.
- **Retiered** A to C: Downgraded from A to C (asymmetric-harness precedent): the cache directory is wiped per operation rather than per repetition and builds keep the minimum of 2 runs, so Hare's reported build probably reused stdlib modules compiled in the first run while the C compilers rebuild everything; the conservative ratio is about 1.3x over gcc-15's object-only compile.
- **Verifier notes:** Numbers and harness verified in cbench and the README; A stands, but the win is the Hare toolchain against GCC and g++ (clang C is faster), so record it as compile throughput rather than a language-level runtime claim. why_faster from the source: the README attributes nothing to Hare; the plausible mechanism is QBE's small backend against GCC's GIMPLE/RTL pipeline, which runs even at -O0 (inference). Hare upstream metadata stays unverified because sr.ht is unreachable.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-118 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/benchmark>
  - <https://github.com/nordlow/compiler-benchmark>
  - <https://github.com/nordlow/compiler-benchmark/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/process_timer.py>
  - <https://github.com/nordlow/compiler-benchmark/commits>
  - <https://github.com/nordlow/compiler-benchmark/issues?q=is%3Aissue+pascal+OR+fpc+OR+hare>
  - <https://github.com/Angluca/hare>
  - <https://raw.githubusercontent.com/Angluca/hare/HEAD/README.md>
  - <https://raw.githubusercontent.com/Angluca/hare/HEAD/cmd/hare/build.ha>
  - <https://raw.githubusercontent.com/Angluca/hare/HEAD/os/+linux/platform_environ.ha>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:hare/nordlow/compiler-benchmark#compile-throughput`) · [data/wave14/enrich/raw/lang_hare_nordlow_compiler_benchmark_compile_throughput.json](../../../data/wave14/enrich/raw/lang_hare_nordlow_compiler_benchmark_compile_throughput.json) (enrichment confidence 0.55)

</details>
