# varint-simd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟡 stale

> Rust crate: branchless SSSE3/BMI2 protobuf-LEB128 varint encode/decode, 2-6x prost and rustc LEB128 on the author's benchmarks.

| | |
|---|---|
| **Beats** | prost varint, integer-encoding-rs and rustc LEB128 (scalar varint) |
| **Claimed result** | Coffee Lake i7-8850H, u32 decode: varint-simd unsafe 482.95 M int/s vs prost 196.05, rustc 191.37, integer-encoding-rs 120.16; u32 encode: 360.87 vs prost 77.402 (4.7x, derived from page data), rustc 157.95, integer-encoding-rs 125.00. u64 encode 303.72 vs prost 46.456 (6.5x, derived). Ryzen 5 2600X u32 decode 293.88 vs prost 150.05. |
| **Workload** | Encoding and decoding sequences of random LEB128 varints bounded by each integer width (u8 to u64), millions of integers per second. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8850H 'Coffee Lake' (2018 15-inch MacBook Pro); AMD Ryzen 5 2600X @ 4.125 GHz 'Zen+' |
| **Compiler and flags** | rustc version not stated (no rust-toolchain file); RUSTFLAGS -C target-cpu=native from .cargo/config.toml, release profile lto = "thin", native-optimizations feature; criterion 0.5 harness |
| **Adoption** | 141 stars; intended for protobuf/Avro implementations |
| **Last commit** | 2024-09-03 |
| **Links** | [repository](https://github.com/as-com/varint-simd) · [benchmark](https://github.com/as-com/varint-simd) |

## Verdict

Author-run criterion 0.5 benchmarks with target-cpu=native and thin LTO (rustc version unstated) on an Intel i7-8850H and a Ryzen 5 2600X decode and encode uniform random integers of each width; on the i7 u32 decode runs at 483 M/s (unsafe) and 332 M/s (safe) vs prost 196 and rustc LEB128 191, and u64 encode at 304 vs prost 46. An open third-party report (issue #14, Zen 3, rustc 1.92) could not reproduce the margin, measuring u64 decode at 232 unsafe and 151 safe vs 123 for a naive loop.

## Use it when

- Rust protobuf/Avro/LEB128 codecs on x86-64 where varint decode or encode shows up in profiles and you control target-cpu.
- Buffers that can carry 16 bytes of tail padding, so you can call decode_unsafe or the 2x/4x/8x batch decoders.
- Streams of small fixed-type fields (u8/u16) where decode_four_unsafe or decode_eight_u8_unsafe apply; the author reports 8x u8 decode at 896 M/s (i7-8850H) and 1,106 M/s (Ryzen 5 2600X).
- Workloads dominated by long varints (large u32/u64 values), where scalar byte loops are slowest.

## Skip it when

- C or C++ code: this is a Rust crate with no C API; look at MaskedVByte, Stream VByte or SFVInt instead.
- Non-x86 targets: no NEON and no scalar fallback (both on the README TODO list); the crate will not compile without SSSE3 set via target-cpu.
- Data with mostly 1-2 byte varints decoded through the safe interface: an independent Zen 3 report (issue #14, rustc 1.92) got only 151 vs 123 M/s over a naive loop for safe u64 decode and saw application throughput halve after switching.
- Generic binaries for unknown CPUs: the native-optimizations feature and PDEP choice are fixed at build time from the build machine's CPUID.
- Block integer compression of posting lists or columns: it does single-integer LEB128, not bit-packing; FastPFor, simdcomp or Stream VByte fit that job.

## How it is fast

Single decode is branchless: it reads 8 or 16 bytes unaligned, finds the terminating byte by inverting the continuation bits and taking trailing_zeros, masks the varint with a blsmsk-style trick, then compacts the 7-bit groups either with BMI2 PEXT (when the build script judges PDEP/PEXT fast) or with shift/mask arithmetic. Encode spreads the number into 7-bit lanes (PDEP or shifts), uses SSE2 compare + movemask and leading_zeros to get the byte count, and ORs in the continuation bits with a vector mask. Multi-value decode uses a movemask of the high bits plus a lookup table and PSHUFB to split adjacent varints. The integer type is a generic parameter, so short targets compile to shorter paths.

## Compared with alternatives

Pick it over MaskedVByte or Stream VByte when you are in Rust and must keep the standard protobuf LEB128 wire format one value at a time (Stream VByte uses its own format); for C++ protobuf-LEB128 decoding the catalogued alternative is SFVInt.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none at runtime (build dependency rustc_version; criterion, integer-encoding, rand, bytes for benches) |
| **Minimum toolchain** | Rust 2021 edition; no rust-version (MSRV) declared in Cargo.toml |
| **Platforms** | x86-64 (and 32-bit x86 cfg paths) with SSSE3 required; optional POPCNT, LZCNT, BMI2, AVX2; no aarch64 |
| **Thread safety** | pure functions with no shared state (from source); not otherwise documented |
| **Drop-in for the baseline** | partial: same LEB128 wire format as prost and integer-encoding-rs, but a different function API (fixed 16-byte output array, tuple results) |

## Gotchas

- The fast numbers are for the unsafe interface: it needs 16 readable bytes after the pointer and silently truncates values too large for the target type; the safe decode copies short inputs into a 16-byte stack buffer and runs extra checks (author's u32 decode: 332 safe vs 483 unsafe M/s).
- Before 0.4.1 (commit 'Correctly decode truncated inputs', 2024-09-03) safe decode::&lt;u8&gt;(&[128]) returned Ok((0, 2)) instead of NotEnoughBytes (issue #10); use 0.4.1 or later.
- Enable native-optimizations only with target-cpu=native; the build script disables PDEP/PEXT on AMD Zen/Zen+/Zen 2, where they are microcoded, and a separate 'dangerously-force-enable-pdep' feature overrides that.
- The benchmark draws uniform random values per type (rand Standard), so nearly every u32 is 5 bytes and most u64 values are 9-10 bytes; real protobuf fields skew short, where the gap to scalar loops is likely smaller (inferred from benches/varint_bench/main.rs).

## Known shortcomings

- Downgraded A to C: numbers reproduce but the rustc version is unstated (target-cpu=native, thin LTO), and it is a Rust crate measured against Rust baselines. Last commit 2024-09-03, stale.
- Open issue #14 (Dec 2025, Zen 3, rustc 1.92) cannot reproduce the README: u64 decode 232 unsafe / 151 safe vs 123 for the naive loop, app throughput halved after switching, no maintainer reply. The bench uses uniform random values, so mostly max-length varints, which favours SIMD. Issue #10: safe decode::&lt;u8&gt;(&[128]) returned Ok((0,2)), fixed in 0.4.1 (2024-09-03). Rust, x86-only, no scalar fallback.

## Caveats and trade-offs

Rust crate, not C++; baselines are Rust varint implementations (prost, rustc_serialize LEB128, integer-encoding-rs), not a C/C++ varint or protobuf library. rustc version unstated. Single-integer LEB128 varint, not block bit-packing. Requires SSSE3 minimum and x86_64 only (no NEON, no scalar fallback). Uses a lot of unsafe code; the fastest column is the 'unsafe' interface that skips overflow and bounds checks (safe decode u32: 332.11 vs prost 196.05). Last commit 2024-09-03.

Needs target-cpu set to a CPU with SSSE3/SSE4.1 (README says project will not compile otherwise); optional BMI2/AVX2/POPCNT/LZCNT paths; 'unsafe' variant requires padded input; Rust, not C++.

## Maintenance

Stale since the 0.4.1 release on 2024-09-03 with issue #14 (Dec 2025) unanswered, but MIT OR Apache-2.0, dependency-free and on crates.io (about 41k downloads, 5 reverse dependencies).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party README tables with public benchmark code (benches/varint_bench.rs, criterion 0.5) and CPU models, and flags visible in .cargo/config.toml (-C target-cpu=native) plus Cargo.toml (lto = "thin"), but the rustc version is never stated and no rust-toolchain file exists, so not A; no independent measurement, so C.
- **Verifier notes:** Every number in claimed_speedup matches the README tables; derived ratios 4.7x (360.87/77.402) and 6.5x (303.72/46.456) check out. License MIT OR Apache-2.0, 141 stars, last commit 2024-09-03 (stale) confirmed. Off-language for a C++ list; orchestrator may want a language shortcoming.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/as-com/varint-simd>
  - <https://github.com/as-com/varint-simd/commits>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/as-com/varint-simd>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/build.rs>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/src/decode/mod.rs>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/src/encode/mod.rs>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/src/num.rs>
  - <https://raw.githubusercontent.com/as-com/varint-simd/HEAD/benches/varint_bench/main.rs>
  - <https://github.com/as-com/varint-simd/issues?q=is%3Aissue>
  - <https://github.com/as-com/varint-simd/issues/14>
  - <https://github.com/as-com/varint-simd/issues/10>
  - <https://github.com/as-com/varint-simd/commits>
  - <https://crates.io/api/v1/crates/varint-simd>
  - <https://crates.io/api/v1/crates/varint-simd/reverse_dependencies>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/as-com/varint-simd`) · [data/wave9/enrich/raw/github_com_as_com_varint_simd.json](../../../data/wave9/enrich/raw/github_com_as_com_varint_simd.json) (enrichment confidence 0.8)

</details>
