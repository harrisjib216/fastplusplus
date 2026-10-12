# Dr. Memory

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `LGPL-2.1-only (drfuzz and drltrace modules BSD)` · 🟢 active

> DynamoRIO-based memory error checker for unmodified binaries; about 2x faster than Valgrind Memcheck on SPEC CPU2006 per its CGO 2011 paper.

| | |
|---|---|
| **Beats** | Valgrind Memcheck |
| **Claimed result** | README: 'faster than comparable tools, including Valgrind' on SPEC CPU2006 (bar chart only). CGO 2011 paper (search snippet only): on average twice as fast as Memcheck, up to four times faster on individual benchmarks; Memcheck cannot run 434.zeusmp and 447.dealII. |
| **Workload** | Memory-error checking of SPEC CPU2006 on Linux; slowdown versus native for Dr. Memory and Valgrind. |
| **Metric** | throughput |
| **Adoption** | 2.8k stars |
| **Last commit** | 2025-12-12 |
| **Links** | [repository](https://github.com/dynamorio/drmemory) · [benchmark](https://github.com/DynamoRIO/drmemory/blob/master/README.md) |

## Verdict

The README states Dr. Memory beats Valgrind on SPEC CPU2006 on Linux and points to a bar chart from the peer-reviewed CGO 2011 paper (Bruening and Zhao); search snippets of that paper give a 2x average and up to 4x per-benchmark speedup over Memcheck, with Memcheck failing on 434.zeusmp and 447.dealII. CPU, compiler flags and the Valgrind version were not visible because the paper and chart hosts are blocked; independent support comes from the sanitizers comparison table (Dr. Memory about 10x vs Memcheck about 20x slowdown).

## Use it when

- Memory-error checking of Windows binaries, especially closed-source or third-party ones you cannot rebuild with AddressSanitizer: Valgrind does not run on Windows.
- Linux x86/x86-64 CI jobs where Valgrind Memcheck is too slow and recompiling with ASan is not possible.
- Hunting uninitialized reads in binaries, which ASan does not detect (MSan needs a full instrumented rebuild).
- Fast smoke runs with -light or -leaks_only when only unaddressable accesses or leaks matter.

## Skip it when

- When you can recompile: the sibling AddressSanitizer pages list about 2x slowdown for ASan vs about 10x for Dr. Memory and 20x for Memcheck.
- When you need current, documented performance numbers: the only head-to-head data is the 2011 paper against the Valgrind of that time, and its chart is on a blocked host.
- AArch64/ARM or macOS 64-bit: optionsx.h notes only pattern mode is supported on ARM (no uninitialized-read checks); 64-bit coverage gaps are open issues (e.g. #1632 byte-to-byte shadowing for 64-bit).
- Programs heavy in SIMD code: issues #1525 and #1562 note xmm operations still go through the slow path, and issue #1188 reports a 29x slowdown on wrf from 185M uninitialized-value events.
- If you need a stable release cadence: releases are automated cronbuild packages (latest cronbuild-2.6.20434, December 2024) and the tracker has about 1,000 open issues.

## How it is fast

It keeps shadow memory for every application byte and inlines a fast path for the common shadow check into DynamoRIO's code cache, dropping to a slow path only for uncommon cases (the paper per search snippets describes these fastpath/slowpath instrumentation optimizations as the source of the 2x average gain over Memcheck). It replaces malloc with its own allocator instead of wrapping it (-replace_malloc, on by default). Cheaper modes trade coverage for speed: -light and -no_check_uninitialized skip definedness tracking, -pattern uses sentinel values around heap blocks instead of shadow memory, -leaks_only checks leaks only, and -persist_code caches instrumented code across runs.

## Compared with alternatives

Pick Dr. Memory over AddressSanitizer when you cannot rebuild the target or need uninitialized-read checks on Windows, and over RetroWrite (binary-rewriting ASan, benchmarked on Linux SPEC CPU2006) when the binary is on Windows; if recompiling is possible, ASan is several times faster.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | DynamoRIO (a dynamorio directory in the repo tree; prebuilt packages include everything) |
| **Minimum toolchain** | not documented in the README (CMake build; binary packages recommended) |
| **Platforms** | Windows, Linux, Mac, Android on IA-32, AMD64 and ARM (README); ARM limited to pattern mode |
| **Thread safety** | Supports multi-threaded applications (it is a whole-process tool); per-option thread behaviour not documented in the README |
| **Drop-in for the baseline** | partial — same run-the-binary workflow as valgrind --tool=memcheck, but different command line, suppression format and reports |

## Gotchas

- -pattern and -unaddr_only disable uninitialized-read checks; -no_check_uninitialized also lowers leak-identification accuracy (optionsx.h).
- With -no_check_uninitialized, unaligned accesses and stack-relative references are not checked unless -check_alignment / -check_stack_access are set, so some overflows can be missed.
- Symbol processing can dominate startup on large Windows apps (issue #2175: msvcr120d.dll 40 s even with symcache; #1447 online symbolization bottleneck).
- License is LGPL-2.1-only for the core; drfuzz and drltrace are BSD.

## Known shortcomings

- ARM supports pattern mode only; 57 open Performance issues; latest release cronbuild-2.6.20434 (2024-12-13). The paper numbers (2x average, 4x maximum) are snippet only: burningcutlery.com and commit.csail.mit.edu are blocked.

## Caveats and trade-offs

Numbers are in a README chart image and in the CGO 2011 paper, both on burningcutlery.com, which is egress-blocked; the 2x average and 4x maximum figures come from search snippets only. Results are from 2011 against the Valgrind of that time. No flags or CPU model seen.

Built on DynamoRIO; Windows, Linux, Mac, Android. Different checks than Memcheck, not a drop-in clone.

## Maintenance

Maintained at a low pace (last commit 2025-12-12, automated cronbuild releases, 57 open Performance-labelled issues), LGPL-2.1 so usable as an external tool without licensing concerns.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** The README states Dr. Memory is faster than Valgrind on SPEC CPU2006 and cites the peer-reviewed CGO 2011 paper, but its numbers are only in a chart image on a blocked host. Search snippets of the paper say Dr. Memory is on average twice as fast as Memcheck and up to four times faster on individual benchmarks. B on the peer-reviewed comparison; no flags or CPU model seen, so not A.
- **Verifier notes:** license.txt says LGPL version 2.1 and no later version, with drfuzz/drltrace under BSD. 2.8k stars, last commit 2025-12-12 (active). A retier to check the paper's numbers needs burningcutlery.com or a GitHub copy of drmem-CGO11.pdf.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/DynamoRIO/drmemory>
  - <https://github.com/DynamoRIO/drmemory/commits/master>
  - <https://raw.githubusercontent.com/DynamoRIO/drmemory/HEAD/README.md>
  - <https://raw.githubusercontent.com/DynamoRIO/drmemory/HEAD/license.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/DynamoRIO/drmemory/HEAD/README.md>
  - <https://github.com/DynamoRIO/drmemory>
  - <https://github.com/DynamoRIO/drmemory/issues?q=is%3Aissue+is%3Aopen+label%3APerformance>
  - <https://raw.githubusercontent.com/DynamoRIO/drmemory/HEAD/drmemory/optionsx.h>
  - <https://github.com/DynamoRIO/drmemory/releases>
  - http://www.burningcutlery.com/derek/docs/drmem-CGO11.pdf (EGRESS_BLOCKED)
  - https://commit.csail.mit.edu/papers/2011/bruening-cgo11-drmemory.pdf (EGRESS_BLOCKED)
  - WebSearch: "Practical Memory Checking with Dr. Memory" CGO 2011 (snippets)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/dynamorio/drmemory`) · [data/wave11/enrich/raw/github_com_dynamorio_drmemory.json](../../../data/wave11/enrich/raw/github_com_dynamorio_drmemory.json) (enrichment confidence 0.7)

</details>
