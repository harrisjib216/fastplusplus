# ZXC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Asymmetric LZ77 codec in C that decodes faster than LZ4, LZ4HC and zstd -1 at equal or smaller output.

| | |
|---|---|
| **Beats** | LZ4 (fast, default, HC -9) and zstd -1 |
| **Claimed result** | Decompression speed ratio ZXC vs competitor at each tier (Apple M2 / Axion Neoverse-V2 / EPYC 9B45 / EPYC 7B13): -1 vs lz4 --fast 2.62x / 1.92x / 2.20x / 1.81x; -3 vs lz4 1.75x / 1.41x / 1.36x / 1.22x; -6 vs lz4hc -9 1.50x / 1.25x / 1.19x / 1.10x; -7 vs zstd -1 2.60x / 1.94x / 2.21x / 2.13x. Ratio also slightly smaller output in each pairing (e.g. 61.76% vs 62.15%). |
| **Workload** | Single-threaded decompression speed on the Silesia corpus (202 MB) at matched ratio tiers, measured with lzbench 2.3.1 on four machines. |
| **Metric** | throughput |
| **Hardware** | Apple M2; Google Axion (Neoverse-V2, GCP C4A); AMD EPYC 9B45 (Zen 5, GCP C4D); AMD EPYC 7B13 (Zen 3, GCP C2D); SMT disabled on x86 |
| **Compiler and flags** | lzbench 2.3.1 built with MOREFLAGS="-march=native"; Clang 21 on macOS, GCC 14 on Linux |
| **Adoption** | 465 stars, 11 forks; zxc 0.14.1 is integrated in lzbench (listed 2026-09-20) and TurboBench (listed as added 2026/05) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/hellobertrand/zxc) · [benchmark](https://github.com/hellobertrand/zxc/blob/main/README.md) |

## Verdict

The author's lzbench 2.3.1 runs (-march=native; Clang 21 on Apple M2, GCC 14 on Axion, EPYC 9B45 and EPYC 7B13; single thread, silesia.tar, 512 KB blocks) show decode ratios of 1.81-2.62x over lz4 --fast at level -1, 1.22-1.75x over lz4 at -3, 1.10-1.50x over lz4hc -9 at -6 and 1.94-2.60x over zstd -1 at -7, each at a slightly smaller size. lzbench's maintainer independently measures 2.05x, 1.23x and 1.06x for the first three pairings on an EPYC 9555P (gcc 15.2.0, turbo off).

## Use it when

- Data compressed once (CI, build step, ingest) and decompressed many times, where decode throughput or effective bandwidth matters more than compression speed: game assets, app bundles, container layers, FOTA images.
- Replacing LZ4 or LZ4HC when you control both ends: in lzbench 2.4 on an EPYC 9555P, zxc -1 decodes at 8,151 vs 3,977 MB/s for lz4 --fast -17 at a slightly smaller size, and -3 at 4,716 vs 3,832 MB/s for lz4.
- ARM64 targets (Apple Silicon, Graviton, Axion), where its decode lead over LZ4 is largest (1.25-2.62x on the README's M2 and Axion rows).
- Firmware or kernel-side unpacking with tight RAM: in-place decompression with a caller-owned static context does no allocation inside the library.
- Small homogeneous records (JSON, logs, KV values) compressed in small blocks, using a trained .zxd dictionary.

## Skip it when

- Compression-speed-bound paths (logging, network streaming of fresh data): zxc -3 compresses at 168 MB/s vs 550 MB/s for lz4 in lzbench 2.4, and -6/-7 at single-digit to low-teens MB/s.
- Long-term archives before v1.0: format breaks have been clean at every bump (v6, v7, v8, v9) and v9 tools reject v8 archives; the maintainer only promises backward-readable archives after v1.0 (issue #457).
- When you need the best ratio: -7 reaches 33.09% on Silesia versus 31.20% for zstd -3; zstd, xz or bzip3 remain the choice for density.
- x86 at the high tier if the margin matters: lzbench's own run puts -6 only 1.06x ahead of lz4hc -9 on decode.
- Interop with existing LZ4/zstd consumers or tooling: the stream format is ZXC-only.

## How it is fast

Levels 1-5 are LZ77 with hash-chain and lazy matching that emit sequences in separate bit-packed streams (prefix varints, RLE) laid out for straight-line decoding, with SIMD match copies and NEON/SSE2/AVX2/AVX-512 paths. Levels 6-7 add optimal parsing and length-limited canonical Huffman for literals (and tokens at level 7) stored in the PivCo level-ordered layout from pivco-huffman: per-node branch bitmaps that the decoder rebuilds with byte-shuffle list merges (TBL, pshufb, vpexpandb) instead of a serial bit chain, which the whitepaper measures at about 3.1 GB/s, 77% over its earlier 4-stream Huffman decoder on Apple M3. Encode-side choices are priced with a size-versus-decode-time Lagrangian, trading ratio for decode cycles.

## Compared with alternatives

Pick ZXC over LZ4/LZ4HC when decode speed per compressed byte is the goal and compression runs offline, and over zstd -1 when you want about 2-2.6x faster decode at a similar ratio; stay with LZ4 when compression speed matters, and with zstd or bzip3 when ratio matters more than decode speed.

## Integration

| | |
|---|---|
| **Form** | static lib (shared optional) with CMake, pkg-config and Meson; also packaged in vcpkg, Conan, Homebrew, winget, Debian/Ubuntu, crates.io, PyPI and npm |
| **Dependencies** | none required (rapidhash is vendored; a system rapidhash.h can be used instead) |
| **Minimum toolchain** | C17 compiler (GCC, Clang or MSVC), CMake 3.14+; PGO only with GCC/Clang |
| **Platforms** | x86-64 (SSE2 baseline, AVX2/AVX-512 paths, runtime dispatch in release binaries), ARM64 NEON, ARMv7, ARMv6, RISC-V, POWER, s390x (big-endian), i386; a Linux kernel contrib tree exists |
| **Thread safety** | Documented as a thread-safe, stateless API; reusable cctx/dctx contexts hold sticky settings and are per-caller objects; stream functions spawn worker threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- A standalone CMake build defaults ZXC_NATIVE_ARCH=ON (-march=native), so a self-built binary may not run on an older CPU; pass -DZXC_NATIVE_ARCH=OFF for portable builds (vendored builds default it OFF, and the release archives dispatch AVX2/AVX-512 at runtime).
- A static decompression context accepts only archives made with its exact block size and no dictionary; dictionary archives also need the same .zxd passed explicitly (no auto-lookup).
- Default block size is 512 KB, so the compression context needs about 1.78 MB per thread (about 5.84 MB at level 6), and the in-place margin is about one block; small payloads want smaller blocks at some cost in ratio and speed.
- The README's 1.75x/1.50x figures at -3/-6 are Apple M2; on x86 the default and high tiers gain 1.10-1.41x.

## Known shortcomings

- Tier A on the README table; lzbench lists zxc 0.14.1 independently (EPYC 9555P, gcc 15.2.0): decode 2.05x vs lz4 --fast -17, 1.23x vs lz4, 1.06x vs lz4hc -9 (derived from page data).
- The format breaks before v1.0 (v6 to v9; v9 rejects v8, issue #457); compression is slow (lzbench 2.4: -3 at 168 vs lz4 550 MB/s); the standalone build defaults to -march=native (ZXC_NATIVE_ARCH=ON); the x86 high-tier gain is small (lzbench -6 1.06x). Levels 6-7 reimplement the PivCo Huffman layout (pivco issue #27). Vendored in ClickHouse (enable_zxc_codec); DwarFS integration open (#235).

## Caveats and trade-offs

README numbers are first party, but code, tool (lzbench), flags and CPUs are public and the CI benchmark workflow re-runs lzbench on ubuntu-latest and macos-26-xlarge. Independent check: the lzbench README (lzbench 2.4, gcc 15.2.0, single thread of AMD EPYC 9555P, turbo off) lists zxc 0.14.1 -1 at 8151 MB/s decode vs lz4 --fast -17 3977 MB/s (2.05x), -3 4716 vs lz4 3832 MB/s (1.23x), -6 3938 vs lz4hc -9 3703 MB/s (1.06x), with ratios 61.76/46.09/36.28% vs 62.15/47.60/36.75% (ratios derived from page data); zxc -7 is not in that table. The x86 gain at the high tier is small (1.06-1.19x); the win is largest on ARM64. Compression is much slower than LZ4 at -6 (9.04 vs 31.9 MB/s for lz4hc -9 in lzbench). Another repo (Vladexy88x/zxc) shows the same description and appears to be a copy. Repo is young.

Asymmetric: slow encoder (optimal parsing) for fast decoder, aimed at write-once/read-many data. Compression speed is lower than LZ4 at the fast tier. Bindings for Rust, Python, Node.js, Go, WASM. Optional seekable archives.

## Maintenance

Very active (586 commits; the record's last commit is 2026-10-02; format v9 is the v1.0 freeze candidate), BSD-3-Clause, fuzzed on OSS-Fuzz and shipped as an opt-in ClickHouse codec, so usable now if you can tolerate one more format break before 1.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** README Benchmarks section gives the per-tier decode ratios vs lz4 --fast, lz4, lz4hc -9 and zstd -1 on Silesia, with public benchmark code (lzbench 2.3.1, driven by .github/workflows/benchmark.yml), flags (MOREFLAGS=-march=native), compilers (Clang 21, GCC 14) and CPU models; the lzbench maintainer's own README table (lzbench 2.4, gcc 15.2.0, AMD EPYC 9555P) independently lists zxc 0.14.1 ahead of LZ4 on decode at matched ratio.
- **Verifier notes:** README table and ratio pairings match the record exactly. lzbench and TurboBench integration confirmed from their READMEs; lzbench's own run supports the decode lead at smaller margins than the README's x86 figures for -6.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** independent: lzbench README (EPYC 9555P, gcc 15.2.0); enricher
- **Pages the verifier opened:**
  - <https://github.com/hellobertrand/zxc>
  - <https://github.com/hellobertrand/zxc/commits/main>
  - <https://raw.githubusercontent.com/hellobertrand/zxc/HEAD/README.md>
  - <https://raw.githubusercontent.com/hellobertrand/zxc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/hellobertrand/zxc/HEAD/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/powturbo/TurboBench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/hellobertrand/zxc>
  - <https://raw.githubusercontent.com/hellobertrand/zxc/HEAD/README.md>
  - <https://raw.githubusercontent.com/hellobertrand/zxc/HEAD/docs/WHITEPAPER.md>
  - <https://raw.githubusercontent.com/hellobertrand/zxc/HEAD/docs/INSTALL.md>
  - <https://raw.githubusercontent.com/hellobertrand/zxc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/hellobertrand/zxc/HEAD/cmake/zxcCompilerFlags.cmake>
  - <https://github.com/hellobertrand/zxc/issues?q=is%3Aissue>
  - <https://github.com/hellobertrand/zxc/issues/457>
  - <https://github.com/hellobertrand/zxc/issues/248>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://github.com/MarcinZukowski/pivco-huffman/issues/27>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/hellobertrand/zxc`) · [data/wave9/enrich/raw/github_com_hellobertrand_zxc.json](../../../data/wave9/enrich/raw/github_com_hellobertrand_zxc.json) (enrichment confidence 0.85)

</details>
