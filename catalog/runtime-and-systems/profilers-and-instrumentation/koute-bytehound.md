# bytehound

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🔴 abandoned

> LD_PRELOAD heap profiler for Linux recording every allocation with full backtraces, positioned as a cheaper heaptrack/massif alternative.

| | |
|---|---|
| **Beats** | heaptrack and Valgrind massif/DHAT |
| **Claimed result** | README: custom stack unwinding makes it 'a lot cheaper than other similar tools, potentially up to orders of magnitude faster in some cases'. No numbers. |
| **Workload** | Memory profiling of native programs (C/C++ via LD_PRELOAD) recording every allocation with full stack traces. |
| **Metric** | throughput |
| **Adoption** | 4.8k stars |
| **Last commit** | 2023-07-28 |
| **Links** | [repository](https://github.com/koute/bytehound) · [benchmark](https://github.com/koute/bytehound) |

## Verdict

No measurement exists: the README only says its custom unwinding makes it 'a lot cheaper than other similar tools, potentially up to orders of magnitude faster in some cases', without naming a baseline, hardware or workload. The heaptrack/Valgrind comparison comes from the author's Hacker News comments (search snippets only), and issue #55 asking for a heaptrack comparison has no answer.

## Use it when

- Finding leaks, peak-memory culprits, temporary-allocation churn or fragmentation in C, C++ or Rust programs on Linux without recompiling
- Long-running services, using MEMORY_PROFILER_CULL_TEMPORARY_ALLOCATIONS to keep only allocations that live longer than a threshold (default 10 s)
- Profiling on memory-constrained targets (AMD64, ARM, AArch64, MIPS64) by streaming data to another machine
- Rust programs using the jemallocator crate on AMD64, which heaptrack-style malloc hooks miss
- When you want scriptable analysis (Rhai) or want to export into the heaptrack GUI

## Skip it when

- If you need a measured overhead guarantee: the project publishes no numbers against heaptrack, massif or DHAT
- macOS, Windows or any non-Linux target
- When you need a maintained tool: last commit 2023-07-28, 44 open issues including segfaults under LD_PRELOAD (#93), aarch64 unwind-table failures (#114) and infinite recursion when glibc's __tls_get_addr calls malloc (#131, 2025)
- Programs that fork without exec, or that rely heavily on longjmp/setjmp: child tracking after fork is a reported problem (#80) and longjmp is only partially supported
- Very long full-detail captures: data files can exceed RAM at analysis time and the strip subcommand itself can run out of memory (#113)

## How it is fast

The speed claim rests on custom unwinding from koute's not-perf crates (nwind): per-thread and global backtrace caches deduplicate stacks (16384 and 327680 entries by default), and a 'shadow stack' mode, on by default, is described as a more intrusive, faster unwinding algorithm; turning it off 'will on average significantly slow down unwinding'. Allocations are still served by the real glibc (or jemalloc) allocator with a small tracking id appended to each block, and the profiler's own memory comes from a vendored mimalloc. The 0.10.0 release notes say CPU overhead on allocation-heavy multithreaded programs dropped by up to about 80%, but no comparison against heaptrack or Valgrind is published.

## Compared with alternatives

Pick it over heaptrack when you need jemalloc-aware profiling, temporary-allocation culling for multi-day runs, remote streaming or scriptable analysis; pick heaptrack (maintained by KDE) or memtrail when you want an actively maintained tool, and tracing_malloc if you need a published wall-time comparison against Valgrind.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Building needs GCC, Rust nightly (rust-toolchain pins nightly-2022-10-13; README says only 1.62 or newer) and Yarn for the web GUI; runtime needs only LD_PRELOAD |
| **Minimum toolchain** | Rust 1.62 nightly (pinned nightly-2022-10-13) |
| **Platforms** | Linux on AMD64, ARM, AArch64, MIPS64 (MIPS64 needs an out-of-tree perf_event_open kernel patch); jemalloc profiling AMD64-only |
| **Thread safety** | Profiles multithreaded programs with per-thread unwind contexts and backtrace caches |
| **Drop-in for the baseline** | partial — same LD_PRELOAD workflow as heaptrack and can export heaptrack files, but its own .dat format, CLI and GUI differ from massif/DHAT |

## Gotchas

- Each allocation is enlarged by an internal tracking id stored at the end of the usable block, so the profiled program's memory layout and malloc_usable_size results differ from an unprofiled run.
- The fast shadow-stack unwinder is intrusive; past releases fixed crashes from calling backtrace and from exceptions under it, and it can be disabled with MEMORY_PROFILER_USE_SHADOW_STACK=0 at a large unwinding cost.
- By default it embeds the program binary and all loaded libraries into the output file (MEMORY_PROFILER_WRITE_BINARIES_TO_OUTPUT=1), which inflates files and can leak binaries if the .dat is shared.
- SIGUSR1 and SIGUSR2 handlers are installed by default and will collide with programs that use those signals.

## Known shortcomings

- Still no numbers anywhere; issue 55 (heaptrack comparison) is unanswered. Open crash issues 93, 114 and 131. Toolchain pinned to nightly-2022-10-13. Program allocations still go to glibc with a tracking id appended; mimalloc is used only for the profiler's own internals. Rust, not C++.

## Caveats and trade-offs

No numbers in the README and no baseline named there ('other similar tools'); the heaptrack and Valgrind comparison comes from the author's HN comments (search snippets only, not verified here). Heaptrack appears in the README only as an output format. Last commit 2023-07-28, over 3 years old (abandoned).

Linux only; preload library written in Rust (nightly toolchain to build); no support for profiling by sampling.

## Maintenance

Abandoned since 2023-07-28 (last release 0.11.0) but dual Apache-2.0/MIT licensed with 4.8k stars; building needs the pinned 2022 nightly Rust toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** README says custom stack unwinding makes it 'a lot cheaper than other similar tools, potentially up to orders of magnitude faster in some cases' with no numbers and no named baseline; heaptrack is mentioned only as an export format.
- **Verifier notes:** Kept at D: notable (4.8k stars) but purely qualitative claim. Metadata confirmed: Apache-2.0 OR MIT, not archived, last commit 2023-07-28, which is just over 3 years before today, so maintenance_status corrected to abandoned.
- **Fields the verifier corrected:** `caveats`, `maintenance_status`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/koute/bytehound>
  - <https://github.com/koute/bytehound/commits>
  - <https://raw.githubusercontent.com/koute/bytehound/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/koute/bytehound>
  - <https://raw.githubusercontent.com/koute/bytehound/HEAD/README.md>
  - <https://github.com/koute/bytehound/releases>
  - <https://github.com/koute/bytehound/issues?q=is%3Aissue+slow+OR+crash+OR+overhead>
  - <https://github.com/koute/bytehound/issues/55>
  - <https://github.com/koute/bytehound/tree/master/docs/src>
  - <https://raw.githubusercontent.com/koute/bytehound/HEAD/docs/src/introduction.md>
  - <https://raw.githubusercontent.com/koute/bytehound/HEAD/docs/src/common_issues.md>
  - <https://raw.githubusercontent.com/koute/bytehound/HEAD/docs/src/configuration.md>
  - <https://raw.githubusercontent.com/koute/bytehound/HEAD/docs/src/getting_started.md>
  - <https://raw.githubusercontent.com/koute/bytehound/HEAD/rust-toolchain>
  - <https://raw.githubusercontent.com/koute/bytehound/HEAD/preload/Cargo.toml>
  - <https://raw.githubusercontent.com/koute/bytehound/HEAD/preload/src/api.rs>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/koute/bytehound`) · [data/wave11/enrich/raw/github_com_koute_bytehound.json](../../../data/wave11/enrich/raw/github_com_koute_bytehound.json) (enrichment confidence 0.7)

</details>
