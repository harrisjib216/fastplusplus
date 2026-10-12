# zint

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `Apache-2.0 OR MIT` · 🟢 active

> Zig FastLanes bitpacking, FOR and delta codecs for u8-u256 arrays; decodes several times faster than lz4 or zstd -1.

| | |
|---|---|
| **Beats** | LZ4 and Zstandard level 1 (plain memcopy as the ceiling); no varint, Simple8b or FastPFor comparison |
| **Claimed result** | epyc9354.txt, T=u32, DATASET=width7, LENGTH=123321: zint_bitpack decompress 26.931GB/s, compress 29.128GB/s versus lz4 decompress 3.811GB/s, zstd(level 1) decompress 0.907GB/s and memcopy 15.429GB/s; width15 same length: zint_bitpack decompress 21.353GB/s versus lz4 9.016GB/s and zstd 2.436GB/s. README: right variant is 'massively faster than lz4 or zstd' and almost matches memcopy. |
| **Workload** | Compress and decompress synthetic u8 to u128 arrays (datasets width7, width15, width32, width33 in plain, delta_ and frame_ variants; lengths 10, 69, 1023, 1024, 1025, 123321, 262144, 263167) with FastLanes-based bitpacking, versus lz4, zstd(level 1) and memcopy. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9354 (inferred from file name epyc9354.txt; a second file ryzen7600x.txt exists); CPU model is not printed in the file |
| **Compiler and flags** | zig build bench -Doptimize=ReleaseFast (Makefile); build.zig.zon minimum_zig_version 0.16.0-dev.732+2f3234c76; actual Zig version used is not recorded in the result file |
| **Adoption** | 21 stars |
| **Last commit** | 2025-12-22 |
| **Links** | [repository](https://github.com/steelcake/zint) · [benchmark](https://github.com/steelcake/zint/blob/HEAD/benchmark_results/epyc9354.txt) |

## Verdict

The author's benchmark (zig build bench -Doptimize=ReleaseFast, Zig version not recorded, AMD EPYC 9354 inferred from the file name) compresses random slices of synthetic arrays, checks the round trip, and reports GB/s per uncompressed byte: u32 width7 at 123,321 elements decodes at 26.9 GB/s against lz4 3.8, zstd -1 0.9 and memcpy 15.4 GB/s, and u64 width7 at 262,144 elements at 28.0 GB/s against memcpy 20.7 GB/s. It beats memcpy only because it touches about a fifth of the bytes, and it is not compared against any integer codec (FastPFor, simdcomp, varint).

## Use it when

- Zig code bases (or a C ABI wrapper you write yourself) that store columns of integers with small ranges: bit widths well under the type width, timestamps or ids suited to FOR
- Columnar or analytical storage where decode throughput matters more than ratio: u32 width7 decodes at 26.9 GB/s against lz4 3.8 GB/s and zstd -1 0.9 GB/s on the author's EPYC 9354
- Arrays of thousands of values or more, ideally a multiple of 1024 elements, since whole blocks take the vectorized path
- Untrusted compressed input: decompress validates every per-block width and the total packed length before reading and returns error.InvalidInput, and the repo ships fuzz targets for round trips and garbage input
- 128- or 256-bit integer columns, which most C/C++ integer codecs do not handle

## Skip it when

- From C++ directly: it is a Zig module with no C header or exported C API, so you would have to write and maintain the C wrapper yourself
- Short arrays: at 10 or 69 elements, and on the up-to-1023-element remainder, it falls back to a scalar bitpacker and is slower than lz4 and memcpy (u8 width7, 1023 elements: 0.776 GB/s decode against lz4 5.042 GB/s)
- Data with outliers or sorted posting lists where a PFor patching scheme, Elias-Fano or Stream VByte would compress better: there are no exceptions or patches, so one large value widens its whole 1024-value block
- When you need a self-describing format: there is no magic, version, length or checksum, the layout is not binary-compatible with CWI's original FastLanes, and the crate is at version 0.0.3
- Big-endian targets (rejected by a compile error) or stable Zig toolchains older than 0.16.0-dev

## How it is fast

It uses the FastLanes layout (Afroozeh and Boncz, VLDB 2023): 1024-value blocks are packed in a transposed 'unified transposed layout' so that one generic scalar loop, fully unrolled at compile time for every bit width (inline for over 0..N_BITS), autovectorizes to whatever SIMD width the target has, including AVX-512. Each 1024-value block gets its own bit width (one byte of metadata), signed types go through zigzag, and FOR and delta are fused into the pack and unpack kernels so there is no separate pass. The code is a Zig port of spiraldb's Rust fastlanes (commit 8b655cf); there are no hand-written intrinsics.

## Compared with alternatives

Pick zint over FastPFor/simdcomp or TurboPFor when you work in Zig, need 128/256-bit or signed types, or want block-wise FOR/delta with validated decoding of untrusted input; choose FastPFor or TurboPFor from C++ and on outlier-heavy data, and Stream VByte when values arrive one at a time or in short lists. No sibling has been measured head to head against zint.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for the library (Zig std only); the benchmark pulls lz4 1.10.0 and zstd 1.5.7 through the Zig package manager |
| **Minimum toolchain** | Zig 0.16.0-dev.732+2f3234c76 (build.zig.zon minimum_zig_version); dev-branch Zig, so expect breakage across Zig releases |
| **Platforms** | any little-endian target Zig supports; SIMD width comes from LLVM autovectorization (the published results are from AMD EPYC 9354 and Ryzen 7600X) |
| **Thread safety** | Stateless functions; a Ctx scratch buffer must not be shared between threads that run at the same time (one Ctx per thread). Not documented otherwise. |
| **Drop-in for the baseline** | no |

## Gotchas

- \*_compress_bound and the compress offsets are computed in u32: once the input is about 4 GiB or larger (for example more than about 1.07 billion u32 values) the bound overflows, which is a panic in Debug or ReleaseSafe and illegal behavior with bounds checks off in ReleaseFast. The doc comment only promises an error at input.len &gt;= maxInt(u32), so split large arrays yourself (found by reading src/zint.zig).
- The remainder (len mod 1024 values) is stored first and packed with the scalar path; lengths such as 1023 or 1025 lose most of the speed.
- Pick the variant per column: deltapack on non-monotonic data expands (ratio 103 percent on u32 frame_width7) and is slower than memcpy even when it compresses well (u32 delta_width7: 10.2 GB/s decode at 21 percent size against memcpy 14.7 GB/s).
- Ctx is a 64 KB aligned allocation; allocate it once and reuse it, as the doc comment in src/zint.zig advises. Running the benchmark itself maps a 16 GiB buffer (BUFFER_SIZE 1 &lt;&lt; 34).

## Known shortcomings

- Bug in src/zint.zig: \*_compress_bound and the compress offsets are computed in u32, so inputs of about 4 GiB or more per call overflow (panic in safe builds, illegal behaviour in ReleaseFast); the doc comment only promises an error at len &gt;= maxInt(u32). Zig only, no C API, needs dev Zig 0.16.0-dev, little-endian only. Stream has no header, length or checksum; version 0.0.3. The remainder (len mod 1024) uses a scalar path. deltapack expands to 103% on frame_width7 and decodes at 10.2 GB/s vs memcpy 14.7 GB/s on u32 delta_width7. Benchmark maps a 16 GiB buffer and compares only lz4/zstd.

## Caveats and trade-offs

Compares against general-purpose lz4 and zstd, not against varint, Simple8b or FastPFor, so it does not show a win over the category's integer-codec baselines. Synthetic data. CPU model and Zig version come from the file name and build.zig.zon, not the result file. Lengths that are not a multiple of 1024 take a slow path: at u32 width7 LENGTH=1023 zint_bitpack decompresses at 3.709GB/s vs 8.359GB/s for memcopy and at u8 width7 LENGTH=1023 at 0.776GB/s vs lz4 5.042GB/s; at lengths 10 and 69 it is slower than lz4 and memcopy. zint_deltapack on non-delta data expands (ratio=103). The epyc results were committed on 2025-12-21, the day before the AVX-512 optimization commit, so they may not reflect HEAD. Author's own benchmark; zint_bitpack beating memcopy reflects throughput reported per uncompressed byte while touching about 21% of the bytes.

Zig library, not callable from C++ without a C wrapper. Based on a port of spiraldb's Rust FastLanes layout, which is not binary compatible with the original FastLanes. Fixed 1024-element blocks; delta variant is slower than memcopy. Safe on untrusted input.

## Maintenance

One-author project with 21 stars, last commit 2025-12-22 (the AVX-512 tuning commit came the day after the EPYC results were committed), no issues filed, dual Apache-2.0/MIT, small enough to vendor into a Zig project but tied to a dev-branch Zig toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** benchmark_results/epyc9354.txt shows T=u32/DATASET=width7/LENGTH=123321 zint_bitpack compress 29.128GB/s, decompress 26.931GB/s vs lz4 decompress 3.811GB/s, zstd(level 1) 0.907GB/s, memcopy 15.429GB/s, and width15 zint_bitpack decompress 21.353GB/s vs lz4 9.016GB/s, zstd 2.436GB/s. Author-run, bench code public (zig build bench -Doptimize=ReleaseFast) but the Zig version and CPU model are not printed in the result file (CPU only from file name), so C.
- **Verifier notes:** All claimed numbers found verbatim in epyc9354.txt. Metadata checked on github.com: Apache-2.0 OR MIT (README and LICENSE-APACHE/LICENSE-MIT), 21 stars, not a fork, not archived, last commit 2025-12-22 (active). Baseline lz4/zstd is a recognizable incumbent for compression, so kept, but it is off the category's integer-codec baselines.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** first-party epyc9354.txt
- **Pages the verifier opened:**
  - <https://github.com/steelcake/zint>
  - <https://github.com/steelcake/zint/commits>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/README.md>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/benchmark_results/epyc9354.txt>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/README.md>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/build.zig>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/Makefile>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/src/zint.zig>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/src/fastlanes.zig>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/src/scalar_bitpack.zig>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/src/zigzag.zig>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/bench.zig>
  - <https://raw.githubusercontent.com/steelcake/zint/HEAD/benchmark_results/epyc9354.txt>
  - <https://github.com/steelcake/zint/issues?q=is%3Aissue>
  - <https://github.com/steelcake/zint/commits>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/steelcake/zint`) · [data/wave9/enrich/raw/github_com_steelcake_zint.json](../../../data/wave9/enrich/raw/github_com_steelcake_zint.json) (enrichment confidence 0.75)

</details>
