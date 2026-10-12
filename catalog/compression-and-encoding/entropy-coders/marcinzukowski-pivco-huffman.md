# PIVCO-Huffman (pivco-huffman)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Block-SIMD Huffman decoder (pivoted coding) that decodes 2-6x faster than zstd's huf0 on most byte distributions.

| | |
|---|---|
| **Beats** | huf0 (zstd's Huffman decoder from FiniteStateEntropy, X1 single-symbol and X2 double-symbol variants) and an in-tree traditional 4-stream table Huffman decoder; Oodle Huffman (oo-huff) is wired into bench/bench_fair.c only when an Oodle SDK is linked and does not appear in the BENCHMARKS.md tables |
| **Claimed result** | Apple M4 Max: proba80 15,339 MB/s vs huf0 X2 2,617 (5.91x best-of-others); real text 4.3-4.8 GB/s, 2.0-2.5x huf0_x2; Xeon 6975P-C AVX-512: english 7,909 vs huf0 X2 1,875 (4.22x), html_wiki 4,765 (2.96x), proba80 22,581 (11.70x). Encoded size within 1-4% of traditional Huffman. |
| **Workload** | Decode of a 4M-symbol Huffman-coded block sequence repeated 100 times (400M symbols per run), 5 runs, median of 3 best; synthetic distributions (proba80, flat, zipfian, ...) and real files (html_wiki, english, json_api, source_c, ...). |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max (NEON, block 8192); Intel Xeon 6975P-C AVX-512 VBMI2 (AWS c8i, 2 vCPU); AWS Graviton 4 Neoverse V2 (c8g.large, taskset -c 0); AMD EPYC 7R13 Zen 3 AVX2/SSE4.1 (AWS c6a, 2 vCPU, block 4096) |
| **Compiler and flags** | GCC 11.5.0 on Amazon Linux 2023 for the Xeon 6975P-C (c8i) and Graviton 4 (c8g) tables, clang-20 for the AMD EPYC 7R13 Zen 3 (c6a) table; CMakeLists.txt adds -Wall -Wextra -O3 and, on AVX-512 hosts, -mavx512f -mavx512bw -mavx512vl -mavx512vbmi -mavx512vbmi2 -mavx512vpopcntdq -mavx2 -mbmi2 -msse4.1 -mpopcnt (AVX2 hosts: -mavx2 -mbmi2 -msse4.1 -mpopcnt); Apple M4 compiler not stated |
| **Adoption** | 38 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/MarcinZukowski/pivco-huffman) · [benchmark](https://github.com/MarcinZukowski/pivco-huffman/blob/main/docs/BENCHMARKS.md) |

## Verdict

The author's in-memory decode microbenchmark (400M symbols per run, median of the 3 best of 5 runs, 30 synthetic and real byte distributions, PH without FSE) measures pivco against huf0 X1/X2 from FiniteStateEntropy and an in-tree 4-stream table decoder on four hosts: on a Xeon 6975P-C with AVX-512 (GCC 11.5.0, -O3) it decodes english at 7,909 vs 1,875 MB/s for huf0 X2 (4.22x) and 2.96-3.79x on real text; on Apple M4 Max 1.94-2.71x on real text; on Graviton 4 1.29-1.98x; on Zen 3 0.94-1.42x on real text. Oodle Huffman is wired into a separate harness but has no published numbers in these tables.

## Use it when

- Read-heavy pipelines where you control both the encoder and the decoder and decode speed of an order-0 byte entropy stage is the bottleneck.
- x86 servers with AVX-512 VBMI2 (Ice Lake, Sapphire/Granite Rapids, Zen 4/5) or Apple M-series, where the published decode ratios over huf0 X2 are 2-4x on real text and up to 11.7x on skewed data.
- Heavily skewed or few-symbol data (proba80-like, bitmaps, scanned 1bpp images, DNA): PH decodes at 8-26 GB/s, and PHA gives about 28-32% smaller output than plain Huffman on proba80 and calgary_pic while still decoding about 2.2-2.6x faster than huf0 X2 on M4.
- Research or prototyping of SIMD entropy decoding; the repo documents its kernels, wire format and per-primitive costs in detail.

## Skip it when

- Production use today: the README marks it WIP and 'not production-ready by any means', and open issue #12 ('Make PH memory-safe and resilient') lists bounds checks on corrupted or adversarial bitmaps as still to do, so do not decode untrusted input with it.
- AVX2/SSE-only x86 such as Zen 3: html_wiki, json_api and log_apache lose to huf0 X2 (0.94-0.95x) and most real-text rows are only 1.06-1.3x.
- When you need compatibility with an existing Huffman stream (zstd, deflate, Oodle): the bitstream is new and still changes between versions.
- Small inputs or latency-bound single-block decodes: the gains come from decoding blocks of thousands of symbols (the benchmarks use 4096-8192; current defaults are 16K on Apple and 32K elsewhere).
- Encode-speed-sensitive paths: the published tables cover decode only; the README example shows encode at about 0.5-0.7 GB/s versus 3.6-5.4 GB/s decode.

## How it is fast

Pivoted coding (PivCo): instead of a per-symbol table lookup with a serial bit cursor, the encoder stores, for each internal node of the Huffman tree, a bitmap saying which symbols of the block go left or right, and the decoder partitions the whole block's index set level by level with SIMD compress/permute primitives (AVX-512 VBMI2 vpcompressb/w, NEON vqtbl, pshufb with compress tables on SSE/AVX2), then merges results bottom-up. Subtrees whose leaves all sit at one depth take a flat fast path: one packed D-bit code per element and a single code_to_sym lookup. This removes the serial bit-length dependency that limits table decoders like huf0, so throughput grows with SIMD width; the optional PHA mode additionally FSE/ANS-codes skewed bitmaps to beat plain Huffman ratio.

## Compared with alternatives

Pick it over FiniteStateEntropy's Huff0 when you can adopt a new format and want CPU Huffman decode several times faster on SIMD-rich hardware; hypersonic-rANS is the alternative if you want an interleaved SIMD rANS decoder (about 3 GB/s on enwik8 in its own README) rather than a Huffman stage, and the GPU decoders (CUHD, gap-array, ipdps22-opthuffdec) only make sense when the data already lives on a GPU.

## Integration

| | |
|---|---|
| **Form** | static lib (libpivco_huffman.a) or a single relocatable object (libpivco_huffman_local.o) with vendored FSE symbols localized |
| **Dependencies** | vendored FiniteStateEntropy submodule (ext/fse, required for PHA); libm on Linux; CMake 3.16+ |
| **Minimum toolchain** | C11 (CMake also enables C++17 for tools); the build auto-picks gcc-14 on AVX-512 Linux and clang-20 on Zen 3 and aarch64 Linux when present; benchmark tables used GCC 11.5.0 and clang-20 |
| **Platforms** | aarch64 with NEON (Apple M-series, Graviton), x86-64 with AVX-512 VBMI2, AVX2+BMI2 or SSE4.1+POPCNT tiers, scalar fallback elsewhere; SVE backend was tried and removed |
| **Thread safety** | Encoder/decoder contexts are single-threaded objects, one per thread; tables are built once and passed in. FSE statistics helpers are documented as not thread-safe, and issue #12 still lists removing global variables as open. |
| **Drop-in for the baseline** | no |

## Gotchas

- The CMake build detects the build host's CPU from /proc/cpuinfo and applies -mavx512\*/-mavx2 flags with add_compile_options to every source, so a binary built on an AVX-512 host is not safe to run on an older x86 CPU; build on (or for) the target machine.
- Linking it next to zstd or anything else that vendors FSE gives duplicate HUF_\*/FSE_\* symbols; link libpivco_huffman_local.o instead of the .a.
- The README's API names (pivco_huffman_build_table, pivco_huffman_set_fse_enabled) lag the header, which now uses pivco_build_table with a pivco_cfg_t and explicit encoder/decoder contexts; the header is authoritative.
- BENCHMARKS.md is a 2026-05-15 snapshot (block 8192/4096, --no-fse) while the code has since changed block-size defaults, wire format and table construction; re-measure on your own data with the bundled pivco_try or pivcohuf CLI.

## Known shortcomings

- Tier A (BENCHMARKS.md reproduces row by row from bench/bench_main.c; GCC 11.5.0 on Xeon and Graviton, clang-20 on Zen 3, -O3 plus -mavx512\*). Oodle appears only in bench_fair.c, not in the tables; on Zen 3 it loses on three real-text rows (0.94-0.95x).
- README says work in progress, 'not production-ready'; open issue #12 'Make PH memory-safe and resilient' (corrupt or adversarial bitmaps are not bounds-checked, globals remain), so unsafe for untrusted input. The wire format is still changing (pivcohuf v0.10); BENCHMARKS.md is a 2026-05-15 snapshot at block 8192 that predates the current defaults (32K, 16K on Apple); CMake applies the host's /proc/cpuinfo -mavx512\* flags to all sources, so binaries are not portable; README API names lag the header.

## Caveats and trade-offs

README marks the project as WIP and not production-ready; co-authored with an AI assistant per commit trailers. BENCHMARKS.md is a 2026-05-15 snapshot marked 'Last content review: NEVER'. On Zen 3 (SSE/AVX2) html_wiki, json_api and log_apache lose to huf0 X2 at 0.94-0.95x and several rows are only 1.06-1.3x; Graviton 4 real text is 1.29-1.47x. flat_M7 on M4 is only 1.43x. The README TL;DR's real-text range (4.3-4.8 GB/s, 2.0-2.5x) does not include the M4 table's english row (6142 MB/s, 2.55x). In-memory decode-only microbenchmark; huf0 uses 128 KB chunks while PIVCO uses 4096-8192-symbol blocks; tables use the --no-fse (PH) configuration. Paper (PDF on github.io) and arXiv copy not opened (hosts blocked).

Not a drop-in: new bitstream (PivCo partition bitmaps), block-based (4096-8192 symbol blocks), encoder walks the Huffman tree; needs SIMD with permute/compress primitives (NEON, AVX-512 VBMI2, AVX2). Encoded size 1-4% above traditional Huffman. PHA variant adds FSE/ANS coded bitmaps for better ratio on skewed data at lower decode speed.

## Maintenance

Actively developed (578 commits, last on 2026-09-17, many co-authored with an AI assistant) under Apache-2.0 and copyable, but explicitly a WIP research codebase with an unstable wire format and an open memory-safety issue; ZXC (hellobertrand/zxc) reimplements the PivCo layout for its entropy stage per issue #27.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/BENCHMARKS.md has per-host tables of pivco_bu decode vs huf0 X1/X2 (zstd's Huffman) and trad 4-stream, produced by the public bench code (bench/bench_main.c, bench/bench_distributions.c, pivco_huffman_bench target) with raw sweep files in results/; the Xeon 6975P-C table states GCC 11.5.0 on Amazon Linux 2023 and CMakeLists.txt sets -O3 plus the -mavx512\*/-mavx2 flags, so code, compiler, flags and CPU model are all present. Every number in claimed_speedup appears on the page or in the README TL;DR.
- **Verifier notes:** Numbers verified row by row against docs/BENCHMARKS.md (M4 proba80 15339 vs huf0 X2 2617, 5.91x; Xeon english 7909 vs 1875, 4.22x; html_wiki 2.96x; proba80 22581, 11.70x). Metadata matches: Apache-2.0, 38 stars, not a fork, last commit 2026-09-17.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/MarcinZukowski/pivco-huffman/blob/main/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/README.md>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/bench/CMakeLists.txt>
  - <https://github.com/MarcinZukowski/pivco-huffman>
  - <https://github.com/MarcinZukowski/pivco-huffman/commits>
- **Sources the enricher read:**
  - <https://github.com/MarcinZukowski/pivco-huffman>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/README.md>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/docs/DATA_FORMAT.md>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/include/pivco_huffman.h>
  - <https://raw.githubusercontent.com/MarcinZukowski/pivco-huffman/HEAD/include/pivcohuf_file.h>
  - <https://github.com/MarcinZukowski/pivco-huffman/issues?q=is%3Aissue>
  - <https://github.com/MarcinZukowski/pivco-huffman/issues/12>
  - <https://github.com/MarcinZukowski/pivco-huffman/issues/27>
  - <https://github.com/MarcinZukowski/pivco-huffman/commits/main>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/marcinzukowski/pivco-huffman`) · [data/wave9/enrich/raw/github_com_marcinzukowski_pivco_huffman.json](../../../data/wave9/enrich/raw/github_com_marcinzukowski_pivco_huffman.json) (enrichment confidence 0.85)

</details>
