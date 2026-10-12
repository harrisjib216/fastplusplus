# snap (Rust Snappy, BurntSushi/rust-snappy)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Pure-Rust Snappy (raw and frame formats) that roughly matches C++ Snappy 1.1.8: within about 10% either way per file.

| | |
|---|---|
| **Beats** | Snappy C++ reference implementation (google/snappy 1.1.8) |
| **Claimed result** | README: performance 'should roughly match' C++ Snappy on x86_64. From the README ratio columns (C++ column over snap column): decompress uflat07_txt2 916.6 vs 1001.8 MB/s (snap 1.09x faster), uflat09_txt4 857.2 vs 930.2 MB/s (1.09x), uflat03_jpg_200 1.08x, uflat06_txt1 1.08x, uflat08_txt3 1.07x, uflat01_urls 1.04x; compress zflat03_jpg_200 1.10x faster, zflat11_gaviota 1.07x faster. Losses: decompress uflat04_pdf C++ 1.10x faster, uflat10_pb 1.05x, compress zflat01_urls 1.04x, zflat10_pb 1.02x. |
| **Workload** | Snappy raw-format compress and decompress of the 12 files of the C++ library's own microbenchmark corpus (html, urls, jpg, pdf, txt1-4, pb, gaviota), both libraries driven by the same harness. |
| **Metric** | throughput |
| **Hardware** | Intel i7-6900K |
| **Compiler and flags** | Not stated. The Rust side is run with 'cargo bench --features cpp' in bench/ (Criterion 0.3), using Cargo's bench profile; the root Cargo.toml sets only debug = true for release. The C++ side is whatever system libsnappy shared library was installed: snappy-cpp/build.rs only emits 'cargo:rustc-link-lib=dylib=snappy', so its build flags are the distribution's and are not given. The rustc version is not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 514 stars; crates.io 'snap' |
| **Last commit** | 2026-07-15 |
| **Links** | [repository](https://github.com/BurntSushi/rust-snappy) · [benchmark](https://github.com/BurntSushi/rust-snappy) |

## Verdict

Criterion microbenchmarks on an Intel i7-6900K over the 12 files of Snappy's own test corpus, with one harness driving snap and the system libsnappy 1.1.8 through FFI: snap ranged from 10% slower (decompress pdf) to 10% faster (compress 200-byte jpg) and was within 2% on most rows. Compiler versions and the C++ build flags are not stated.

## Use it when

- Rust code that must read or write Snappy raw or framed data and should not need a C++ toolchain, pkg-config or a system libsnappy (static or cross builds).
- Many small messages (hundreds of bytes) compressed with one reused Encoder: the stack table avoids heap traffic, and the 200-byte rows are where snap beat C++ 1.1.8 most (compress 237.5 vs 262.4 ns, decompress 112.8 vs 122.4 ns).
- Streaming compression or decompression through std::io Read/Write adapters with framed CRC32C checks.
- Projects that want a widely used pure-Rust implementation (about 125 million crates.io downloads) rather than FFI bindings such as the `snappy` crate.

## Skip it when

- If you expect a speedup over current C++ Snappy: the only comparison is parity against 1.1.8 (Jan 2020); Snappy 1.1.9, 1.1.10, 1.2.x and 1.3.1 (Sep 2026) all list performance work and were never measured against snap.
- If you need Snappy 1.2's denser compression level 2 or other tuning knobs: snap's Encoder has no level setting.
- C or C++ consumers: use google/snappy directly; this crate exposes only a Rust API.
- no_std or allocation-free embedded targets: the crate depends on std (std::io, runtime CPU feature detection) and allocates a 32 KB table for blocks above 1 KB.
- Highly repetitive single-byte inputs: issue #34 (2020) reported a PyO3 binding of snap slower than python-snappy on such a file; the maintainer called the input pathological but did not show snap winning there.

## How it is fast

It reproduces the reference algorithm: a 4-byte multiplicative hash (0x1E35A7BD) into a u16 position table sized to the block, the skip heuristic that hashes less often in incompressible data, 8-byte unaligned match extension and 16-byte over-copies for short literals and copies, and a 256-entry tag lookup table in the decoder, with unchecked indexing in the hot loops. For blocks needing at most 1,024 table entries it uses a table embedded in the Encoder instead of the heap, which avoids the per-call heap working-memory allocation that Snappy 1.1.8 does. Frame-format CRC32C uses SSE4.2 when detected at run time on x86_64, else a slice-by-16 table.

## Compared with alternatives

Pick snap over Supersnappy (the Nim sibling, also measured against the C API of a prebuilt libsnappy) when you work in Rust or need the frame format and a large user base. Unlike libbzip2-rs or crabz, which claim wins over C, snap is a parity port: choose it to drop the C++ dependency, not for speed.

## Integration

| | |
|---|---|
| **Form** | crate (snap on crates.io); szip CLI in the same workspace |
| **Dependencies** | none at run time (criterion and the snappy-cpp FFI crate are used only by the bench and test crates) |
| **Minimum toolchain** | README states Rust 1.39.0, but CI bumped the pinned MSRV to 1.60 and then 1.70 and stopped testing an MSRV in August 2025, so the stated minimum is untested; edition 2018 |
| **Platforms** | any Rust target with std; performance claims cover x86_64 only; CRC32C hardware path on x86_64 with SSE4.2 |
| **Thread safety** | Encoder, Decoder and frame adapters are plain owned values driven through &mut self; use one per thread (not otherwise documented) |
| **Drop-in for the baseline** | partial: same raw and framed wire formats with byte-identical raw output to C++ 1.1.8, but a Rust API, not a replacement for the C++ library's API or ABI |

## Gotchas

- Harness asymmetry: the C++ side is whatever system libsnappy shared library was installed (README says 1.1.8; snappy-cpp/build.rs only links dylib=snappy, so its build flags are the distribution's), called through the C API over FFI. That C API path builds a heap WorkingMemory on every compress call (snappy.cc 1.1.8 WorkingMemory constructor), and the wrapper parses the length header twice on decompress, while snap uses an inline 1,024-entry table. The 200-byte jpg_200 rows (8-10% snap wins, 10-25 ns) mostly measure that per-call overhead, not the codecs. Both sides decompress snap-compressed input, which is fine given byte-identical output.
- Undefined behavior under Tree Borrows was found in Decompress::read_copy (issue #56, Dec 2023) and fixed in 1.1.1 (commit cda9838); use 1.1.1 or later. The hot loops are unsafe pointer code.
- The raw format caps input at u32::MAX bytes (MAX_INPUT_SIZE); use the frame format for larger or streaming data. Raw APIs require initialized output slices of max_compress_len bytes (MaybeUninit output is an open request, #62).
- 1.1.2 (2026-07-15) changed only error validation in the decoder (long-literal length bytes, varint header capped at 5 bytes), so the README numbers still describe the current hot loops; the C++ baseline is what has aged.

## Known shortcomings

- Parity only (wins and losses up to 10%); the C++ side is the system libsnappy dylib via FFI with flags unknown, old Snappy 1.1.8.
- Parity port, no real win: the baseline is the system Snappy 1.1.8 dylib through the C API over FFI, whose compress path heap-allocates WorkingMemory on every call while snap uses an inline 1,024-entry table, so the 8-10% jpg_200 wins mostly measure per-call overhead. Snappy 1.1.9 to 1.3.1 were never measured. Tree Borrows UB in read_copy (#56) was fixed in 1.1.1.

## Caveats and trade-offs

This is a parity result, not a clear win. The README says the Rust crate 'should roughly match' C++ Snappy on x86_64. snap is faster on about half the rows (up to 1.10x: compress zflat03_jpg_200, decompress uflat07_txt2 and uflat09_txt4 1.09x) and slower on others (decompress uflat04_pdf C++ 1.10x faster, uflat10_pb 1.05x, compress zflat01_urls 1.04x). The C++ side is the system libsnappy shared library called through Rust FFI (snappy-cpp/build.rs links dylib=snappy), so its optimisation flags are the distribution's and are not stated, and each call crosses a dynamic-library boundary. The 200-byte jpg_200 rows (about 120 to 260 ns per call), where snap wins by 8-10%, are the most sensitive to that call overhead. The numbers are from an old setup (Snappy/C++ 1.1.8, i7-6900K) and predate snap 1.1.2 (2026-07-15, 'impl: more closely align with the Snappy spec'). Newer Snappy 1.1.9+/1.2.x releases were not tested. First-party measurement by the crate author. [retier] A parity result, not a clear win: the README says the crate 'should roughly match' C++ Snappy on x86_64, and snap is faster on about half the rows (up to 1.10x) and slower on others (uflat04_pdf C++ 1.10x faster). The C++ side is the system Snappy 1.1.8 dylib (distribution build flags) called through the C API over FFI, whose compress path heap-allocates WorkingMemory on every call and whose wrapper parses the length header twice on decompress, while snap uses an inline 1,024-entry table, so the 8-10% jpg_200 wins (10-25 ns) mostly measure per-call overhead. Snappy 1.1.9 to 1.3.1 were never measured. Tree Borrows UB in read_copy (#56) was fixed in 1.1.1.

Compression output is byte-for-byte identical to the C++ library (README); also provides the Snappy frame format; pure Rust with no C++ dependency, so no FFI or build-time C++ toolchain.

## Maintenance

Maintained at low churn (1.1.2 released 2026-07-15; open issue #66 asks whether it is still maintained), BSD-3-Clause, about 125 million crates.io downloads; safe to depend on for Rust Snappy, but its speed evidence is a 2020-era parity table against Snappy 1.1.8.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section has a critcmp table for snappy/cpp (Snappy/C++ 1.1.8) and snappy/snap on an Intel i7-6900K, and the harness is public (bench/src/bench.rs with the snappy-cpp FFI crate). Compiler versions and the C++ library's build flags are not stated (it links the system libsnappy shared library), so it falls short of A. These are first-party numbers, so tier C.
- **Verifier notes:** Numbers match the README critcmp table exactly; this is a near-parity result (wins and losses of up to 10%) by the crate author, so it stays at tier C. Shortcomings to record: no clear win, the C++ baseline is a system shared library with unknown build flags called through FFI (this also affects the tiny jpg_200 rows), an old Snappy 1.1.8, no compiler versions. Metadata checked: BSD-3-Clause, 514 stars, not archived, last commit 2026-07-15.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-89 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/README.md>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/snappy-cpp/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/snappy-cpp/build.rs>
  - <https://github.com/BurntSushi/rust-snappy>
  - <https://github.com/BurntSushi/rust-snappy/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/README.md>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/bench/src/bench.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/snappy-cpp/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/snappy-cpp/build.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/snappy-cpp/src/lib.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/src/compress.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/src/decompress.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/src/crc32.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/src/bytes.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/src/read.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rust-snappy/HEAD/src/write.rs>
  - <https://raw.githubusercontent.com/google/snappy/HEAD/NEWS>
  - <https://raw.githubusercontent.com/google/snappy/1.1.8/snappy.cc>
  - <https://github.com/BurntSushi/rust-snappy/commits/master>
  - <https://github.com/BurntSushi/rust-snappy/commit/fea0488>
  - <https://github.com/BurntSushi/rust-snappy/issues?q=is%3Aissue>
  - <https://github.com/BurntSushi/rust-snappy/issues/61>
  - <https://github.com/BurntSushi/rust-snappy/issues/56>
  - <https://github.com/BurntSushi/rust-snappy/issues/34>
  - <https://crates.io/api/v1/crates/snap>
  - WebSearch: Rust snap crate vs C++ snappy 1.1.9/1.1.10/1.2 benchmark (no newer comparison found)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/burntsushi/rust-snappy`) · [data/wave14/enrich/raw/github_com_burntsushi_rust_snappy.json](../../../data/wave14/enrich/raw/github_com_burntsushi_rust_snappy.json) (enrichment confidence 0.8)

</details>
