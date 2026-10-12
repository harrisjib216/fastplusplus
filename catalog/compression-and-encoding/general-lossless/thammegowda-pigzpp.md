# pigzpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Zlib` · 🟢 active

> C++23 rewrite of pigz as a thread-safe library and CLI on ISA-L/zlib-ng; 2.1x to 8.5x pigz compression throughput.

| | |
|---|---|
| **Beats** | pigz 2.6 (system zlib) and gzip (archived run metadata records gzip 1.10; the README table labels it gzip 1.12) |
| **Claimed result** | CLI compress: gzip 1.12 -6 17 MB/s (ratio 2.83); pigz 2.6 -6 -p8 133 MB/s (2.83); pigzpp --engine zlib 285 MB/s (2.81), stated as 2.1x faster than pigz at the same ratio; pigzpp --engine isal (default) 1124 MB/s (2.58), stated as 8.5x faster than pigz with about 9% more output. Decompression: pigzpp 711 MB/s vs pigz 212 MB/s vs gzip 166 MB/s. |
| **Workload** | Compress a 128 MB multilingual (English + Chinese Wikipedia) text corpus at level 6 with 8 workers on the command line; also decompression of a level-6 gzip stream. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon W-2235 host; Ubuntu 22.04 WSL2 guest (kernel 6.18.33.2-microsoft-standard-WSL2) exposing 5 cores / 10 logical CPUs; median of 7 timed samples after 1 warm-up; affinity, turbo and frequency not controlled (per metadata timing_policy) |
| **Compiler and flags** | C++23 via CMake Release build (README/report state the C++ core is Release -O3 for the Go/OCI benchmark); C++ compiler name and version not recorded in README, report/pigzpp-report.pdf or the archived metadata, which lists only rustc 1.93.0, go 1.22.5, node 22.16.0 and a conda Python built with GCC 14.3.0 |
| **Adoption** | 14 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/thammegowda/pigzpp) · [benchmark](https://github.com/thammegowda/pigzpp) |

## Verdict

The author's run in an Ubuntu 22.04 WSL2 guest (5 cores / 10 logical CPUs of a Xeon W-2235) compressed a 128 MB English+Chinese Wikipedia text corpus at level 6 with 8 workers; medians of 7 samples. Results: 1124 MB/s (ISA-L, ratio 2.58) and 285 MB/s (zlib-ng, 2.81) vs pigz 2.6 on system zlib at 133 MB/s (2.83) and gzip at 17 MB/s; decompression 711 vs 212 vs 166 MB/s. The C++ compiler and version are not recorded, and the archived run came from a dirty working tree.

## Use it when

- Replacing pigz or gzip in pipelines that compress large text or log streams on x86-64 multicore machines, where 9% more output is an acceptable price for about 8x pigz throughput (ISA-L default).
- When the output must stay gzip-compatible and the ratio must match pigz: --engine zlib (zlib-ng) gave 285 vs 133 MB/s at ratio 2.81 vs 2.83 at level 6 with 8 workers.
- Calling parallel gzip in-process from Python, Go (for example OCI layer compression, 381 MB/s zlib-ng / 1437 MB/s ISA-L vs Go compress/gzip 34 MB/s on a 637 MB layer), Rust or WASM instead of shelling out to pigz.
- Faster gzip decompression than pigz/gzip on x86-64 (711 vs 212 vs 166 MB/s on the level-6 text stream), mostly from the ISA-L inflater.
- Writing ZIP archives or PNG files from Python faster than zipfile or Pillow.

## Skip it when

- When the compression level must mean what it means in gzip/pigz: with the default ISA-L engine, levels 5 to 9 all map to ISA-L level 3, so -6 and -9 give the same ratio (2.58 on the test text vs pigz 2.83).
- Incompressible data at level 1 with --engine zlib: the archived robustness run shows ratio 0.948 on random data (about 5.5% expansion) vs 0.9997 for pigz, and zlib-ng level 1 also gave ratio 1.88 vs pigz 2.40 on text.
- ARM64 and WebAssembly: ISA-L is x86-64 only, so these platforms get only the zlib-ng path (about 2.1x pigz in the CLI run, not 8.5x).
- Maturity-sensitive production use: very new single-author project (15 commits, 14 stars, PyPI 1.1.1 uploaded 2026-10-03), described by its author as an experiment in AI-assisted modernization, with one benchmark machine (WSL2 guest) and one text corpus.
- Toolchains older than C++23: it needs GCC 13+, Clang 17+ or a recent MSVC, plus CMake 3.20+.

## How it is fast

It uses pigz's design: the input is cut into blocks, each block is deflated on its own worker thread with the last 32 KiB of the previous block set as a preset dictionary, and CRC-32s are combined. The per-block DEFLATE is no longer system zlib: it is zlib-ng (SIMD match finding and CRC) or Intel ISA-L's hand-written x86 assembly deflate, and ISA-L is the default on x86-64. Decompression is a single sequential inflate (ISA-L isal_inflate or zlib-ng) with separate write and check (CRC) threads, as in pigz.

## Compared with alternatives

Pick pigzpp over pigz when you want pigz's parallel gzip as an in-process library with zlib-ng/ISA-L backends. Pick it over using ISA-L igzip or zlib-ng directly when you want multithreaded gzip output and bindings for several languages. For parallel decompression of a single large gzip file, Rapidgzip is the stronger choice, since pigzpp inflates sequentially.

## Integration

| | |
|---|---|
| **Form** | static lib + CLI (CMake, git submodules); C ABI library libpigzppc; Python abi3 wheels on PyPI; Go, Rust and WASM bindings |
| **Dependencies** | zlib-ng and ISA-L (vendored as submodules; system zlib possible with PIGZPP_USE_ZLIB_NG=OFF); zopfli for level 11; nanobind for Python; GoogleTest for tests |
| **Minimum toolchain** | C++23 (GCC 13+, Clang 17+ or recent MSVC), CMake 3.20+; Python 3.12+ for the module, Go 1.22+, Rust 1.75+, Emscripten for WASM |
| **Platforms** | Linux, macOS, Windows on x86-64 and ARM64 (prebuilt CLI and wheels); ISA-L backend x86-64 only; WebAssembly with SIMD and optional pthreads |
| **Thread safety** | README states the library is thread-safe with no global state (config replaces pigz's global struct g); C++ API reports errors by exceptions, C ABI returns an error string |
| **Drop-in for the baseline** | partial — the CLI accepts pigz's interface and produces standard gzip streams, but the default ISA-L engine changes the size/level trade-off, and the library API is new |

## Gotchas

- The default engine is ISA-L, not zlib-ng, so switching from pigz silently grows files about 9% at -6 unless --engine zlib (CLI) or engine=zlib is passed.
- In the in-memory buffer API, rsyncable, zopfli (level 11) and ZIP framing are routed through temporary file descriptors on tmpfs and copied back, so those modes are slower than the headline buffer path.
- pigzpp_gzip_decompress is sequential; its threads argument is kept only for API compatibility.
- Much of the speedup is the backend swap: pigz built against zlib-ng (the catalogued pigz entry's pigz-ng) already narrows the gap, and the baseline pigz 2.6 here used system zlib.

## Known shortcomings

- Downgraded A to C: numbers reproduce from the README, in-repo report PDF and raw JSON, but the C++ compiler is never named, the tree was dirty and the gzip version was 1.10 against the README's 1.12; the arXiv paper is a first-party preprint.
- The default ISA-L engine maps levels 5-9 to ISA-L level 3, so -6 and -9 give the same ratio 2.58 and the 8.5x is not a same-level comparison; robustness.tsv shows --engine zlib -1 expanding random data (ratio 0.948 vs pigz 0.9997) and dropping the text ratio to 1.88 vs pigz 2.40. Decompression is sequential; the buffer API sends rsyncable/zopfli/zip modes through tmpfs file descriptors.

## Caveats and trade-offs

Very new, single-author C++23 rewrite of pigz (described by the author as an experiment in AI-agent-assisted modernization). Baseline pigz uses the system zlib, so much of the gain is zlib-ng and ISA-L (both already catalogued) rather than new compression code. gzip is single-threaded, so the 66x-vs-gzip figure is mostly parallelism. Benchmarks ran in a WSL2 guest on one CPU with one text corpus; the archived metadata marks the working tree as dirty (commit e7e3286, dirty=true) and records gzip 1.10 while the README says gzip 1.12. The 8.5x figure trades about 9% more output (ratio 2.58 vs 2.83). Compiler name/version for the CLI run not stated. The technical report (arXiv 2608.24153, also checked in as report/pigzpp-report.pdf) is a first-party preprint.

Library plus CLI with C API, Python, Go, Rust and WASM bindings; speed comes from the zlib-ng and ISA-L DEFLATE backends. ISA-L backend is x86-64 only and gives about 9% larger output (ratio 2.58 vs 2.81); on ARM64 and WASM only the zlib-ng path is available.

## Maintenance

Active (commits through 2026-10-03, PyPI 1.1.1 released 2026-10-03) and zlib-licensed, so copyable, but it is a weeks-old single-author rewrite with no issue history yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** Benchmark code (benchmarks/report/run_report_benchmarks.py, benchmarks/core) and raw samples (benchmarks/results/2026-07-14/report-benchmarks.json) are public and the CPU is named (Xeon W-2235, WSL2 guest), but the C++ compiler and version for the CLI build are not stated in the README, the technical report PDF, or the archived metadata, so not A; the arXiv report is a first-party preprint, not peer review, so C.
- **Verifier notes:** All CLI and decompression numbers match the README, the checked-in report PDF and the raw JSON (gzip 16.6, pigz 132.9, pigzpp zlib 284.6, isal 1124.4 MB/s; decompress 165.5/212.1/711.4 MB/s). Downgraded A to C only because the C++ compiler is never named; the arXiv paper was read via its in-repo PDF copy.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/benchmarks/results/2026-07-14/report-benchmarks.json>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/report/pigzpp-report.pdf>
  - <https://github.com/thammegowda/pigzpp>
  - <https://github.com/thammegowda/pigzpp/commits>
- **Sources the enricher read:**
  - <https://github.com/thammegowda/pigzpp>
  - <https://github.com/thammegowda/pigzpp/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/src/pigzpp/pigzpp.h>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/src/pigzpp/compress.cpp>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/src/pigzpp/decompress.cpp>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/src/pigzpp/capi.h>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/src/pigzpp/config.h>
  - <https://raw.githubusercontent.com/thammegowda/pigzpp/HEAD/report/plots/data/robustness.tsv>
  - <https://pypi.org/pypi/pigzpp/json>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/thammegowda/pigzpp`) · [data/wave9/enrich/raw/github_com_thammegowda_pigzpp.json](../../../data/wave9/enrich/raw/github_com_thammegowda_pigzpp.json) (enrichment confidence 0.75)

</details>
