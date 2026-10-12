# Zstandard (zstd)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause OR GPL-2.0-only` · 🟢 active

> General-purpose lossless compressor beating zlib/deflate on speed and ratio, with tunable levels and negative fast modes.

| | |
|---|---|
| **Beats** | zlib |
| **Claimed result** | zstd 1.5.7 -1: 510 MB/s compression, 1550 MB/s decompression, ratio 2.896 vs zlib 1.3.1 -1: 105 MB/s compression, 390 MB/s decompression, ratio 2.743 (\~4.9x faster compression, \~4.0x faster decompression, derived from page data, at a better ratio). vs brotli 1.1.0 -1: 290 MB/s / 425 MB/s, ratio 2.883 (zstd \~1.8x faster compression, \~3.6x faster decompression, derived from page data, comparable ratio). zstd --fast=4: 665 MB/s / 2050 MB/s at ratio 2.146 vs zlib -1 (\~6.3x / \~5.3x, derived from page data, at a lower ratio). |
| **Workload** | In-memory compression/decompression speed and ratio on the Silesia compression corpus, single-thread, using lzbench. |
| **Metric** | throughput |
| **Hardware** | Core i7-9700K @ 4.9GHz, Ubuntu 24.04 (Linux 6.8.0-53-generic) |
| **Compiler and flags** | gcc 14.2.0 (lzbench build; lzbench version and optimization flags not stated in README) |
| **Adoption** | 27.9k stars; reference implementation of RFC 8878, used in Linux kernel, Chromium, FreeBSD, PostgreSQL, and many package managers |
| **Last commit** | 2026-09-18 |
| **Links** | [repository](https://github.com/facebook/zstd) · [benchmark](https://github.com/facebook/zstd) |

## Verdict

zstd 1.5.7 -1 measured 510 MB/s compression and 1550 MB/s decompression at ratio 2.896, vs zlib 1.3.1 -1 at 105 MB/s / 390 MB/s and ratio 2.743, in the project's own README Benchmarks table (lzbench, gcc 14.2.0, Silesia corpus, single-threaded, Core i7-9700K @ 4.9GHz, Ubuntu 24.04). The lzbench project's own README independently corroborates a similar zstd-vs-zlib gap on different hardware (AMD EPYC 9554, zstd 1.5.6 -1 at 422/1347 MB/s vs zlib 1.3.1 -1 at 93.0/323 MB/s).

## Use it when

- General file/stream compression where you want a better ratio than zlib at several times the throughput
- Workloads needing a single tunable speed/ratio knob, from --fast=# (skip ratio for max speed) up to level 22 (max ratio)
- Many small, structurally similar records (e.g. JSON/API payloads) via a trained dictionary, where per-item ratio would otherwise be poor
- Large-payload compression that can use multiple threads (built with ZSTD_MULTITHREAD + pthread)
- Codebases needing a permissive-or-copyleft license choice (dual BSD-3-Clause / GPLv2)

## Skip it when

- You need byte-compatible zlib/deflate/gzip output for an existing wire protocol or file format — zstd's container is a different, RFC 8878 format
- You need the best possible ratio regardless of CPU cost — the README's own table doesn't include xz, a stronger-ratio baseline it lists as uncompared here
- You're decompressing untrusted archives via the CLI's recursive mode: a crafted circular symlink can hang `zstd -d -r -f` (open issue #4081)
- You need the experimental/advanced API surface (behind ZSTD_STATIC_LINKING_ONLY) in a dynamically-linked build — it's explicitly static-link-only and unstable across versions
- You're on a toolchain where strict C90 portability doesn't matter and you'd rather have a simpler, smaller single-strategy codec

## How it is fast

Compression uses selectable match-finder strategies per level, from cheap hash-chain/greedy search at low levels up to binary-tree/optimal parsing at high levels, so speed vs ratio is a single tunable knob (including negative --fast=# levels that skip expensive search entirely). The entropy stage uses FSE (tANS) and Huff0, which decode faster than classic Huffman/zlib entropy coding. On x86-64 the library auto-dispatches to BMI2 instructions at runtime when available, mainly speeding up the decoder; optional dictionary training (ZDICT) amortizes the cost of small, similarly-shaped inputs.

## Compared with alternatives

Pick zstd over LZ4 when ratio matters more than raw peak speed: zstd -1 gets 2.896 ratio at 510/1550 MB/s vs LZ4's 2.101 ratio at 780/4970 MB/s in the same README table. Pick LZ4 instead when you need decompression well above 2 GB/s or compression above \~700 MB/s and can accept a much lower ratio.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib \| source-drop (Makefile is the reference build; CMake, Meson, Buck, Bazel, and VS project files are also maintained) |
| **Dependencies** | none for core library; POSIX pthread required only if built with ZSTD_MULTITHREAD for multithreaded compression |
| **Minimum toolchain** | strict C90 C (per CONTRIBUTING.md); no C99/C++ requirement for the library itself |
| **Platforms** | portable C90 baseline runs anywhere; x86-64 gets optional runtime BMI2 dispatch (auto-detected, not required); aarch64 supported; Windows via VS2008+/CMake; macOS Universal2 (x86_64/arm64) build documented |
| **Thread safety** | CCtx/DCtx are not thread-safe — use one context per thread for parallel calls. A created ZSTD_CDict is read-only and safe to share across threads concurrently. Default `make lib` builds a multithreaded dynamic library but a single-threaded static library; `lib-mt`/`lib-nomt` targets force one or the other. |
| **Drop-in for the baseline** | partial — same in-memory/streaming compression API shape as zlib (one-shot and streaming calls) but a different, non-interoperable wire format, so callers must change format, not just swap the library |

## Gotchas

- Static and dynamic library builds default to different threading modes (single- vs multi-threaded); mismatched expectations here are a common build-config surprise
- Advanced/experimental API (unlocked via ZSTD_STATIC_LINKING_ONLY) is explicitly forbidden with dynamic linking because its ABI is unstable
- CLI recursive decompress can hang on a crafted circular symlink (open issue #4081) — a library-embedding concern only if you shell out to the CLI
- Open performance-regression report (#4587) for level 18 after an internal API v2 change, unresolved as of this session

## Caveats and trade-offs

The numbers are reported first-party in the zstd README from an lzbench run. The compiler, CPU and OS are stated, but the compile flags and the lzbench version are not, so the evidence is not tier A. The --fast=4 speedups come with a lower compression ratio than zlib -1 (2.146 vs 2.743). Independent corroboration: the lzbench README (lzbench 2.0.1, gcc 14.2.0, AMD EPYC 9554) lists zstd 1.5.6 -1 at 422/1347 MB/s against zlib 1.3.1 -1 at 93.0/323 MB/s.

Speed/ratio is tunable via level and --fast=# negative levels; higher levels trade speed for ratio. Dual-licensed (BSD or GPLv2) so usable in both permissive and copyleft contexts. Table does not include xz (a listed baseline) directly, only zlib, brotli, and other fast codecs.

## Maintenance

Actively maintained (last commit 2026-09-18 on branch 'dev'), reference implementation of RFC 8878 used in the Linux kernel, Chromium, FreeBSD, and PostgreSQL; usability is 'copyable' and it is dual-licensed BSD-3-Clause OR GPLv2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification A, tier now B.
- **Tier reason:** The README table uses lzbench, a public, well-known third-party suite, and states gcc 14.2.0, a Core i7-9700K and Ubuntu 24.04 (Linux 6.8.0-53). It does not state compile flags, and the rule says missing flags means not A. This is B because the win comes from a well-known independent benchmark suite.
- **Verifier notes:** All numbers match the README Benchmarks table, and the ratios are correct. The license was verified as BSD-3-Clause (3-clause LICENSE) OR GPLv2 (COPYING), per the README; GitHub reports NOASSERTION. Other checks: 27,931 stars, not archived, not a fork, last commit 2026-09-18 on the default branch 'dev'.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/facebook/zstd>
  - <https://github.com/facebook/zstd/blob/dev/LICENSE>
  - <https://github.com/facebook/zstd/blob/dev/COPYING>
  - <https://github.com/inikep/lzbench>
  - <https://github.com/inikep/lzbench/blob/master/Makefile>
- **Sources the enricher read:**
  - https://github.com/facebook/zstd (README, via gh api repos/facebook/zstd/readme)
  - <https://github.com/facebook/zstd/blob/dev/lib/README.md>
  - <https://github.com/facebook/zstd/blob/dev/lib/zstd.h>
  - <https://github.com/facebook/zstd/blob/dev/SECURITY.md>
  - <https://github.com/facebook/zstd/blob/dev/CONTRIBUTING.md>
  - https://github.com/facebook/zstd (repo file tree, via gh api git/trees)
  - https://github.com/facebook/zstd/issues (gh search issues: performance regression)
  - https://github.com/facebook/zstd/issues (gh search issues: label:bug)
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/facebook/zstd`) · [data/wave0-seed/enrich/raw/github_com_facebook_zstd.json](../../../data/wave0-seed/enrich/raw/github_com_facebook_zstd.json) (enrichment confidence 0.88)

</details>
