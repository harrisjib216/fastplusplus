# Firetrail (formerly skim)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Zig` · `no license` · 🟢 active

> Zig word-hash codec (Density-style) that encodes faster than lz4 --fast=20 and zstd --fast=5, at a lower ratio.

| | |
|---|---|
| **Beats** | lz4 (also zstd) |
| **Claimed result** | Silesia: Firetrail White encodes at 1.67 GB/s and Orange at 1.54 GB/s versus lz4 1.10.0 --fast=20 at 0.98 GB/s and zstd 1.5.7 --fast=5 at 0.69 GB/s; geometric mean over four corpora: White 1.6x faster than lz4 and 2.5x faster than zstd on encode. Orange ratio on silesia 1.54x versus lz4 1.56x. Independent lzbench row for the earlier skim 0.1.0: 2313 MB/s compress, 3500 MB/s decompress, ratio 64.53% versus lz4 --fast -17 at 924 and 3977 MB/s and 62.15%. |
| **Workload** | End-to-end CLI runs (file in, file out, warm page cache), single thread, on silesia.tar, HDFS.log, enwik8 and enwik9. |
| **Metric** | throughput |
| **Hardware** | Ryzen 7 7800X3D, CachyOS, single thread |
| **Compiler and flags** | Firetrail built with Zig in release-fast mode (README: zig build bench --release=fast); the end-to-end tables come from scripts/bench.fish, which times the firetrail, zstd and lz4 CLIs with poop. Baseline zstd 1.5.7 and lz4 1.10.0 are system binaries with no build flags stated. |
| **Adoption** | 1 star (old skim repo 3 stars) |
| **Last commit** | 2026-08-04 |
| **Links** | [repository](https://github.com/VantorreWannes/firetrail) · [benchmark](https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/README.md) |

## Verdict

The author's end-to-end CLI timings (poop, single thread, warm page cache, Ryzen 7 7800X3D, CachyOS, Zig release-fast build versus distro lz4 1.10.0 --fast=20 and zstd 1.5.7 --fast=5, all -T1) put silesia.tar encode at 1.67 GB/s for White and 1.54 GB/s for Orange versus 0.98 GB/s for lz4 and 0.69 GB/s for zstd, with Orange's ratio 1.54x against lz4's 1.56x; geomean over four corpora is 1.6x lz4 and 2.5x zstd for White. Decoded output was not verified in the harness, and the independent lzbench row covers the predecessor skim 0.1.0, not this codec.

## Use it when

- Experiments with very fast single-thread encoding of large, repetitive, word-aligned data such as logs (HDFS.log: Orange 2.42 GB/s encode at 2.53x versus lz4 --fast=20 at 1.25 GB/s and 4.53x).
- A deployed static dictionary (White) for streams that share a vocabulary, where the dictionary is trained once with Red and shipped to both ends.
- Pipelines that are encode-bound and can accept a ratio of 1.2-1.5x on mixed data, in a Zig code base.
- Reading the code as a compact reference for Density-style word hashing (about 180 lines per codec).

## Skip it when

- Any production or redistributed use: the repository has no LICENSE file, so the code cannot legally be copied.
- Incompressible or already-compressed input with the CLI: an 8 MiB block of random data encodes to 8,519,680 bytes, but the decoder reads each compressed block into an 8,388,608-byte buffer (input_data_bound = block_size in main.zig), so such files cannot be decoded and, in ReleaseFast builds, the read overruns the heap buffer.
- Untrusted input: decompressBlockToBuffer runs with @setRuntimeSafety(false) and never checks the compressed length, and the CLI trusts the per-block sizes in the stream; there is no checksum or format magic.
- Decode-bound workloads: lz4 decodes faster on all four corpora (silesia 2.53 versus 1.89 GB/s for White).
- When ratio matters: lz4 and zstd compress smaller on silesia and HDFS.log, and zstd --fast=5 beats it everywhere on ratio.

## How it is fast

There is no match search or entropy coding: each 64-bit word costs one Fibonacci multiplicative hash, one table load and one compare, and every 8 words share a 1-byte flag header, so the loop is branch-light, unrolled at compile time (inline for) and built with runtime safety off. The README describes the design as inspired by Density. Because only whole words at 8-byte-aligned positions can match, the best possible ratio is about 3.76x (8 bytes become 2 bytes plus 1/8 of a header byte).

## Compared with alternatives

Against LZ4, Density and ZXC it only wins on single-thread encode speed for word-aligned repetitive data; pick LZ4 (or memlz for encode-only speed) for anything that needs decode speed, a stable format, a C API or a licence, and Density if you want this style of word-hash codec with a licence and a library API.

## Integration

| | |
|---|---|
| **Form** | module (Zig package) plus CLI binary |
| **Dependencies** | none at run time; zBench (Zig) for the in-memory benchmark target |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon) |
| **Platforms** | any Zig target in principle (portable code, explicit little-endian I/O, no SIMD intrinsics); benchmarks only on x86-64 Linux (Ryzen 7 7800X3D) |
| **Thread safety** | not documented; each encoder/decoder owns a mutable 512 KB table, so use one instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Encoder and decoder must start from identical tables: a White or Orange stream encoded with --import dict.bin decodes to wrong bytes without that same file, and nothing in the stream records which dictionary or codec was used.
- White without an imported dictionary compresses almost nothing, because its table starts zeroed and is never updated.
- No round-trip check anywhere: the algorithm files have no tests, and scripts/bench.fish times decode with poop but never compares the decoded file with the original.
- The published White figures use a dictionary trained on the very file being compressed and leave its 512 KB out of the size, so Orange is the fair cold comparison.

## Known shortcomings

- Tier C: lz4/zstd baselines are distro binaries with flags unstated; the White dictionary is trained on the same input it compresses; the lzbench row is the old skim 0.1.0. No license, so reference.
- Correctness bug: the CLI decoder reads each compressed block into an 8,388,608-byte buffer (main.zig input_data_bound = block_size) but an incompressible 8 MiB block encodes to 8,519,680 bytes, so random or already-compressed files cannot round-trip and ReleaseFast reads past the heap buffer. The decoder has @setRuntimeSafety(false), no input-length checks and no checksum. Algorithm files have no tests and bench.fish never compares decoded output with the original. No LICENSE. Zig 0.16+, no C API. Best possible ratio about 3.76x. Benchmark corpora compress, so the timed runs are unaffected.

## Caveats and trade-offs

Baselines are non-default fast settings (lz4 --fast=20, zstd --fast=5), both -T1. White's figures use a 512 KB dictionary trained by Red on the very input being compressed and not counted in the output size, which flatters White's ratio and is not a deployable setup; Orange (cold, no dictionary) is the fair comparison. lz4 still decodes faster on every corpus (2.53 GB/s versus 1.89 GB/s White on silesia), and lz4 and zstd compress smaller on silesia and HDFS.log. enwik8 nearly fits the 96 MB L3, which the author says flatters it. No LICENSE file in the repo, so code must not be copied. The old skim repo only shows a migration notice pointing to Firetrail; the lzbench row is for skim 0.1.0, an earlier codec version.

Density-inspired 8-byte word hash with a 512 KB table; ratio is low (1.3-1.5x on silesia). White needs a trained dictionary. Streaming with 15-20 MB RSS. Written in Zig; no C API is mentioned.

## Maintenance

Active hobby project (63 commits, last 2026-08-04, version 0.0.0, 1 star) with no licence, so treat it as a reference to read rather than code to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README tables (Ryzen 7 7800X3D, CachyOS, single thread) show White 1.67 GB/s and Orange 1.54 GB/s encode on silesia.tar versus lz4 --fast=20 at 0.98 and zstd --fast=5 at 0.69, and state the 1.6x / 2.5x geomeans; the harness is public (scripts/bench.fish, timing CLI runs with poop) but the lz4/zstd binaries are distro builds with no compiler or flags, so first-party C. The independent lzbench 2.4 row is for the predecessor skim 0.1.0 (2313 / 3500 MB/s, 64.53% versus lz4 --fast -17 at 924 / 3977 MB/s, 62.15%), not the current codec, so it does not lift the tier.
- **Verifier notes:** All README numbers match, including Orange ratio 1.54x versus lz4 1.56x on silesia. Repo: 1 star, 0 forks, 63 commits, no LICENSE file, last commit 2026-08-04; github.com/vantorrewannes/skim (3 stars) shows 'Skim migrated to Firetrail'.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/README.md>
  - <https://github.com/VantorreWannes/firetrail>
  - <https://github.com/VantorreWannes/firetrail/commits>
  - <https://github.com/VantorreWannes/firetrail/tree/main/scripts>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/scripts/bench.fish>
  - <https://github.com/vantorrewannes/skim>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/README.md>
  - <https://github.com/VantorreWannes/firetrail>
  - <https://github.com/VantorreWannes/firetrail/tree/main/src>
  - <https://github.com/VantorreWannes/firetrail/tree/main/src/algorithms>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/build.zig>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/scripts/bench.fish>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/src/hashers.zig>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/src/luts.zig>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/src/bench.zig>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/src/algorithms/orange.zig>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/src/algorithms/white.zig>
  - <https://raw.githubusercontent.com/VantorreWannes/firetrail/HEAD/src/algorithms/red.zig>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/vantorrewannes/firetrail`) · [data/wave9/enrich/raw/github_com_vantorrewannes_firetrail.json](../../../data/wave9/enrich/raw/github_com_vantorrewannes_firetrail.json) (enrichment confidence 0.75)

</details>
