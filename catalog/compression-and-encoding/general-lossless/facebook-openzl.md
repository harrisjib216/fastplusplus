# OpenZL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C / C++` · `BSD-3-Clause` · 🟢 active

> Meta's graph-of-codecs compression framework: format-aware compressors for structured data plus a native LZ that decodes about 2.3x faster than zstd -1.

| | |
|---|---|
| **Beats** | zstd |
| **Claimed result** | Release notes v0.3.0 (opened): on Silesia, OpenZL LZ v0.3.0 ratio 2.73, compression 467 MB/s, decompression 3062 MB/s vs zstd ratio 2.74, 419 MB/s, 1254 MB/s ("144% faster" decoding than zstd "at equivalent settings"); a Compression Transformer table on 868 numeric stream families (17.9 GB) reports ratio 7.76x vs zstd -19 5.752x and xz -9 5.920x (ratio, not speed). Snippet only (arXiv 2510.03203, not opened): on the PPMF Unit dataset a trained OpenZL compressor compresses at 340 MB/s vs zstd -3 at 220 MB/s with a better ratio; ppmf_person compresses 55% better than xz -9 and 11x as fast. |
| **Workload** | Format-aware compression of structured datasets (trained compressors) vs zstd and xz; separate native LZ engine vs zstd on Silesia. |
| **Metric** | throughput |
| **Adoption** | 3.2k stars; used at Meta |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/facebook/openzl) · [benchmark](https://github.com/facebook/openzl/releases/tag/v0.3.0) |

## Verdict

First-party release notes (v0.2.0 and v0.3.0) report Silesia at level 1: OpenZL LZ v0.3.0 ratio 2.73, 467 MB/s compress, 3062 MB/s decompress vs zstd -1 with a 64K window 2.74 / 419 / 1254 and plain zstd -1 2.89 / 424 / 1345; the linked gist names an AMD EPYC Genoa at 3 GHz and an internal clang-LTO buck build, with zli and zstd CLI commands for reproduction, but no zstd version or public compiler flags. Trained-compressor speed claims (e.g. 340 MB/s at ratio 2.06 vs zstd 220 MB/s at 1.31) come from Meta's whitepaper, seen only as a search snippet.

## Use it when

- Large volumes of structured or columnar data with a known layout (numeric arrays, records, CSV, Parquet, ML checkpoints) where ratio and speed must both beat zstd and you can afford to write an SDDL description or run training.
- Read-heavy pipelines on 64-bit servers that want faster decompression than zstd at a similar ratio: v0.3.0 LZ decodes Silesia at 3062 MB/s vs 1254-1345 MB/s for zstd -1.
- Numeric streams (8 to 64-bit integers): the v0.3.0 release reports a 7.76x mean ratio over 17.9 GB of numeric files vs 5.75x for zstd -19 and 5.92x for xz -9 (ratio only, no speed given).
- Fleets that need one decoder for many dataset-specific compressors, since every frame is decodable by the same universal decompressor.

## Skip it when

- Generic or small text where ratio matters: the native LZ on Silesia trails default zstd -1 on ratio (2.73 vs 2.89), and issue #207 reports a 264,383-byte Twitter JSON file growing to 305,949 bytes with the example JSON path.
- When you need a stable wire format or API off release tags: README says API, format and codec set will change, dev-branch commits carry no guarantees, and v0.3.0 bumped the frame format from 24 to 27 and renamed APIs.
- 32-bit targets: OpenZL requires a 64-bit platform (CMakeLists; issue #342 asks for 32-bit support and is open).
- MSVC-only Windows builds: README says MSVC may fail with C2099 on C11 features and recommends clang-cl or MinGW-w64.
- Teams that cannot invest in data descriptions or training: the large wins are on described or trained formats; without that, the gain shrinks to the LZ engine's faster decode.

## How it is fast

Compression is modelled as a directed acyclic graph of small codecs (parse into typed field streams, transpose, delta, tokenize, field LZ, entropy coding), so each stream reaches a coder suited to it; that gives better ratio than one generic LZ pass at similar or higher speed on structured data. A trainer (and, in v0.3.0, a 'Compression Transformer' neural selector) picks the graph per dataset. The native LZ engine got its v0.3.0 decode gain from PivCo Huffman, a Huffman layout that stores a bitmap per internal tree node and rebuilds the data bottom-up with SIMD instead of walking the bitstream symbol by symbol (PR #1035: 2574 vs 1416 MB/s decode against huf0 on AVX-512, for 12% slower encode), plus ARM NEON and SVE2 kernels.

## Compared with alternatives

Pick OpenZL over zstd when your data has a describable structure (numeric columns, records, Parquet) or decode speed dominates and you control both ends; stay on zstd for byte-stream interoperability, a stable format and the best ratio on generic text, and use LZ4 when compression speed matters more than ratio.

## Integration

| | |
|---|---|
| **Form** | static lib (shared optional via OPENZL_BUILD_SHARED_LIBS), plus zli CLI, C++ bindings and Python extension |
| **Dependencies** | zstd 1.5.7 (git submodule or fetched tarball with SHA-256 check); optional test, benchmark (Google Benchmark), Parquet and Python components |
| **Minimum toolchain** | C11 and C++17 compiler; CMake 3.20.2+ (or the bundled Makefile); clang-cl or MinGW-w64 on Windows |
| **Platforms** | 64-bit only (x86-64, aarch64; NEON and SVE2 kernels added in v0.3.0; wasm64 via Emscripten) |
| **Thread safety** | not documented in the headers read; state lives in explicit ZL_CCtx / ZL_DCtx contexts, so use one context per thread |
| **Drop-in for the baseline** | partial: OpenZL frames are not zstd frames and the API differs (ZL_CCtx / ZL_DCtx with a compressor graph); the zstd-style one-call compress was removed on purpose, though ZL_decompress(dst, cap, src, size) is one call |

## Gotchas

- The '144% faster than Zstandard' decode figure compares against zstd -1 with windowLog=16, hashLog=14 (the 64K-window row: ratio 2.74, 1254 MB/s); against default zstd -1 (ratio 2.89, 1345 MB/s) the decode gain is about 2.3x (derived from page data) and OpenZL's ratio is lower.
- Check optimization flags: issue #163 found the Makefile compiling at -O1 and decompression about 5x slower than zstd; the README now says BUILD_TYPE=OPT is the default, and `make show-config` prints the flags in use.
- Default compression is strict: if the input does not match the expected format (e.g. not a multiple of 4 bytes for a 32-bit graph) compression errors out unless ZL_CParam_permissiveCompression is set to fall back to generic compression.
- PivCo Huffman is enabled only for inputs of 16 KiB and larger (PR #1035), so small-buffer decode speed is lower than the headline number; inputs of several GB are split into about 16 MB chunks automatically (v0.2.0).

## Known shortcomings

- Tier C: the v0.3.0 release page gives LZ decompress 3062 vs zstd 1254 MB/s and compress 467 vs 419 MB/s on Silesia with no CPU, compiler or flags; the trained-compressor 340 vs 220 MB/s numbers are snippet-only (openzl.org and engineering.fb.com blocked).
- The zstd row behind '144% faster' (419/1254 MB/s, ratio 2.74) is zstd -1 with windowLog=16 and hashLog=14 (v0.2.0 release notes plus the terrelln gist); plain zstd -1 gives ratio 2.89 at 424/1345 MB/s, so decode is about 2.3x (derived from page data) at a lower OpenZL ratio (2.73). The gist run was an AMD EPYC Genoa 3 GHz with an internal buck clang-LTO build and no zstd version. 64-bit only (issue #342 open); issue #163: the Makefile built at -O1 decodes 5x slower than zstd; issue #207: Twitter JSON grew from 264,383 to 305,949 bytes; frame format moved from 24 to 27 in v0.3.0; PivCo only for inputs of 16 KiB or more.

## Caveats and trade-offs

Release-note numbers state no CPU model, compiler, flags, zstd version or level, or benchmark command; the repo's benchmark/ directory (Google Benchmark e2e/micro harness) publishes no results. Trained-compressor numbers come from Meta's own whitepaper, seen only as search snippets (arXiv, engineering.fb.com and openzl.org are blocked here). Gains on structured formats need a format description or training; on CSV compression speed is capped near 64 MB/s by parsing (snippet). lzbench lists openzl as a target but its README table has no openzl rows.

Wins come from describing the data format and training a compressor graph; decompression of format-aware streams is slower than zstd; API and format subject to change off release tags; requires C11 and C++17.

## Maintenance

Very active (v0.3.0 on 2026-09-29, last commit 2026-10-02, used in production at Meta), BSD-licensed; treat it as pre-1.0 and pin release tags because the frame format and API still change.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The v0.3.0 GitHub release notes (first-party) carry a table of OpenZL LZ v0.3.0 vs zstd on Silesia (decompression 3062 vs 1254 MB/s, compression 467 vs 419 MB/s) but state no CPU model, compiler, flags or zstd level; the trained-compressor numbers (340 vs 220 MB/s) come from Meta's own arXiv whitepaper, seen only as a search snippet and not peer-reviewed. First-party with partial methodology, so C.
- **Verifier notes:** Metadata checked on github.com: BSD license, 3.2k stars, not archived, last commit 2026-10-02 on dev. The LZ-vs-zstd numbers are now sourced from a page actually opened; the format-aware claims remain snippet-only.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/facebook/openzl>
  - <https://github.com/facebook/openzl/commits>
  - <https://github.com/facebook/openzl/tree/dev/benchmark>
  - <https://github.com/facebook/openzl/releases/tag/v0.3.0>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/facebook/openzl/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebook/openzl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebook/openzl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/facebook/openzl/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/facebook/openzl/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/facebook/openzl/HEAD/build-scripts/cmake/openzl-deps.cmake>
  - <https://raw.githubusercontent.com/facebook/openzl/dev/include/openzl/zl_compress.h>
  - <https://raw.githubusercontent.com/facebook/openzl/dev/include/openzl/zl_decompress.h>
  - <https://github.com/facebook/openzl/tree/dev/include/openzl>
  - <https://github.com/facebook/openzl/releases>
  - <https://github.com/facebook/openzl/releases/tag/v0.3.0>
  - <https://github.com/facebook/openzl/releases/tag/v0.2.0>
  - <https://gist.github.com/terrelln/412cda99d1e54126477219cacf38c971>
  - <https://github.com/facebook/openzl/pull/1035>
  - <https://github.com/facebook/openzl/issues?q=is%3Aissue+performance+OR+slow+OR+crash+OR+bug>
  - <https://github.com/facebook/openzl/issues/163>
  - <https://github.com/facebook/openzl/issues/207>
  - <https://github.com/facebook/openzl/issues/1079>
  - <https://github.com/MarcinZukowski/pivco-huffman>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/facebook/openzl`) · [data/wave9/enrich/raw/github_com_facebook_openzl.json](../../../data/wave9/enrich/raw/github_com_facebook_openzl.json) (enrichment confidence 0.75)

</details>
