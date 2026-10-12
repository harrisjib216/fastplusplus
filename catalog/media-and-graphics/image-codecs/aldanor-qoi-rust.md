# qoi (qoi-rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟡 stale

> Safe-Rust QOI image codec (crate qoi) that decoded about 1.5x and encoded about 1.3x faster than reference qoi.h.

| | |
|---|---|
| **Beats** | QOI reference C implementation (phoboslab/qoi qoi.h, commit 00e34217 as of the 2022-01-06 measurement; the README later relabelled it 8d35d93 without re-measuring) |
| **Claimed result** | Decode 427.4 Mp/s versus 282.9 Mp/s for qoi.h and encode 290.0 Mp/s versus 225.3 Mp/s (1477.7 versus 978.3 MiB/s decode, 1002.9 versus 778.9 MiB/s encode), about 1.5x decode and 1.3x encode (derived from page data); measured 2022-01-06 against qoi.h 00e34217. |
| **Workload** | Encode and decode of 2846 PNG images from the upstream QOI benchmark suite (1.32 GPixels, 4.46 GB of raw pixels), via the repo's bench/src/main.rs: per image and codec, repeated timed encodes and decodes filling a default 1-second budget (at least 2 runs each), median by default, with a round-trip pixel check; totals are sums of per-image medians. |
| **Metric** | throughput |
| **Hardware** | Apple M1 laptop |
| **Compiler and flags** | qoi.h (phoboslab/qoi submodule at 8d35d93) compiled by the cc crate at opt_level 3 with QOI_NO_STDIO and QOI_IMPLEMENTATION (libqoi/build.rs); rustc version, C compiler and Rust build profile not stated. |
| **Adoption** | 129 stars; crates.io crate qoi with 68.4M downloads (17.4M recent) |
| **Last commit** | 2025-07-27 |
| **Links** | [repository](https://github.com/aldanor/qoi-rust) · [benchmark](https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/README.md) |

## Verdict

On one Apple M1 laptop (rustc, C compiler and Cargo profile not stated; qoi.h built by the cc crate at opt-level 3), the author's bench/src/main.rs encoded and decoded 2846 images from the QOI benchmark suite (1.32 Gpixels), taking the median of repeated runs per image and summing them: qoi-rust decoded at 427.4 Mp/s against 282.9 for qoi.h and encoded at 290.0 against 225.3 Mp/s (about 1.5x and 1.3x, derived from page data). The numbers date from January 2022 and were measured against qoi.h at phoboslab/qoi@00e34217, not 8d35d93 as the README now says; the 'MB/s' columns are MiB/s.

## Use it when

- Rust programs that need very fast lossless 8-bit RGB/RGBA encode and decode and can accept PNG-class or worse compression: asset caches, screenshots, intermediate frames.
- no_std or embedded Rust targets (core only, with an optional alloc feature).
- Decoding untrusted QOI in Rust where memory safety matters: the crate has #![forbid(unsafe_code)] and the README says it is fuzz-tested and round-trip-tested against qoi.h.
- Streaming encode or decode straight from std::io Read/Write without buffering the whole file.

## Skip it when

- C++ projects: there is no C API, so an FFI layer and a Rust toolchain are needed; the reference qoi.h or the catalogued C++ qoixx drop in directly.
- Decoding RGBA files to RGB with Decoder::with_channels(Channels::Rgb) when alpha is not all 255: the RGB path hashes pixels with alpha forced to 255 (Pixel&lt;3&gt;::as_rgba(0xff) in the slice decoder, Pixel&lt;3&gt;::hash_index in the stream decoder), so its colour index drifts from the encoder's and later QOI_OP_INDEX chunks return wrong colours. Found by code reading on master and 0.4.1, not covered by any test.
- The crates.io release 0.4.1 (2022-10-16, nearly all of the 68.4M downloads) with QOI files from other encoders or on big-endian hosts: it lacks master's 2025 fixes for black pixels decoded as transparent when the first chunk is a run (issue #16, PR #17; it hit image-rs/image and GNOME glycin), the stream decoder's index update on runs, and decode_to_buf with an oversized buffer (#18). Its encoder hash is wrong on big-endian targets and produces malformed images (open issue #26, s390x). A request for a new release (issue #14, April 2025) has no reply.
- Interop with files whose header says 3 channels but that contain QOI_OP_RGBA chunks: qoi.h decodes them, qoi-rust (master too) returns an error, and the maintainer noted in PR #17 that upstream's phoboslab/qoi#258 test files stay incompatible because of this channel mismatch.
- When file size matters: QOI compresses no better than qoi.h, and the catalogued QOIR, fpnge or Zpng give better ratios at similar speeds.

## How it is fast

The decoder walks the input with Rust slice patterns (match data { [b1 @ QOI_OP_INDEX..=QOI_OP_INDEX_END, tail @ ..] =&gt; ... }), so chunk dispatch and the length checks collapse into one match without per-byte bounds checks, and it is monomorphised over the output channel count (3 or 4) and over whether QOI_OP_RGBA chunks can occur. Runs are written with slice fill, INDEX and RUN chunks skip the colour-index update, and the 6-bit hash (r\*3 + g\*5 + b\*7 + a\*11) mod 64 is one 64-bit multiply on the packed pixel. The encoder writes into a pre-sized slice through a small Writer trait, range-tests DIFF and LUMA deltas with OR-mask tricks, and emits QOI_OP_INDEX instead of a length-1 QOI_OP_RUN. Everything is scalar code: there are no SIMD intrinsics and no unsafe blocks.

## Compared with alternatives

Pick qoi-rust in Rust code that needs the QOI format with no unsafe code or with no_std; in C or C++ use the reference QOI (phoboslab/qoi) or qoixx, which also beats qoi.h without an FFI layer, and use QOIR or fpnge when you can choose the format and want better compression.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bytemuck only (&gt;= 1.12 in 0.4.1, 1.22 on master) |
| **Minimum toolchain** | Rust 1.61 for crates.io 0.4.1; on master Cargo.toml says rust-version 1.67.0 while the README still says 1.62.0 |
| **Platforms** | Any Rust target, std or no_std; scalar code only. The 0.4.1 encoder is broken on big-endian targets (#26); master's from_le_bytes hash fixes it but is unreleased. |
| **Thread safety** | Not documented; the API is free functions and per-call Encoder/Decoder values over caller-owned buffers with no global state, so separate images can be coded on separate threads (inferred from the source). |
| **Drop-in for the baseline** | partial — same QOI format and file size, and it decodes qoi.h output, but it is a Rust API with no C ABI, and the default encoder's bytes differ from qoi.h unless the 'reference' feature is enabled |

## Gotchas

- The default encoder replaces length-1 runs with QOI_OP_INDEX, so its output is valid QOI but not byte-identical to qoi.h; the 'reference' Cargo feature restores identical output, which Cargo.toml says 'may be slower'.
- encode_to_vec zero-fills a worst-case buffer of pixels x (channels + 1) + 22 bytes and truncates it without shrinking, so each returned Vec keeps that capacity; call shrink_to_fit if you hold many encoded images.
- Images over 400,000,000 pixels are rejected (QOI_PIXELS_MAX), and the decoder only produces 3 or 4 channels.
- The README benchmark is from January 2022: commit 3fb2a4d (11 Oct 2023) changed the reference label from phoboslab/qoi@00e34217 to 8d35d93 without changing a single number, so the table was measured against the Dec 2021 qoi.h and the qoi-fast code of that time, not the current submodule or release.

## Known shortcomings

- Rust (language-filter mismatch). Independent re-implementation of QOI (not a port; qoixx precedent) benchmarked in bench/src/main.rs against qoi.h at -O3 with no rustc or C compiler versions, Apple M1 only; the harness repeats and takes the median. The default encoder emits INDEX for run-1 (bytes differ from qoi.h, same size). 68.4M crates.io downloads.
- README numbers are from 2022-01-06 against qoi.h 00e34217; commit 3fb2a4d relabelled the baseline to 8d35d93 without re-measuring (retier-01 corrects the record). The crates.io release 0.4.1 (2022, 68.3M downloads) lacks master fixes: first-op RUN decoded black as transparent (#16, #17; hit image-rs and glycin) and the stream RUN index bug (#18); big-endian encoder output is malformed (#26 open); release request #14 unanswered. Code reading on master and 0.4.1 (untested by the enricher, reproduced in a Python model of the loop): with_channels(Rgb) on RGBA input with alpha not 255 hashes pixels with alpha 255, so INDEX chunks decode to wrong colours; 3-channel files holding QOI_OP_RGBA are rejected. The benchmark path (self round-trip, header channels) is unaffected.

## Caveats and trade-offs

Rust, not C++ (the search's C++ language filter does not match). An independent safe-Rust re-implementation of the QOI format, not an FFI binding or wrapper of qoi.h, so like wx257osn2/qoixx it can sit beside phoboslab/qoi rather than fold into it as a duplicate. Baseline is the QOI reference qoi.h (commit 8d35d93), not a listed category baseline (libjpeg-turbo, libpng, libwebp, libavif). First-party numbers from one Apple M1 laptop with no rustc or C compiler version. By default the encoder emits QOI_OP_INDEX instead of a length-1 QOI_OP_RUN where allowed, so its byte stream can differ from qoi.h's (same size, still valid QOI; the 'reference' feature restores identical output), and each codec decodes its own encoder's output. The README says it is the fastest of the Rust QOI crates but gives no table for the others. The crates.io release (0.4.1) dates from 2022-10-16.

Pure safe Rust (unsafe forbidden), no_std support; usable from C++ only through FFI, there is no C API in the README. Same QOI format and compression ratio as the reference.

## Maintenance

Stale but not abandoned (last commit 2025-07-27, PRs open since 2025); dual MIT/Apache-2.0 and about 1,300 lines of safe Rust, but the only release is 0.4.1 from 2022, so either pin a master commit to get the decoder fixes or wait for a release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks table matches the record exactly (qoi.h 282.9/225.3 Mp/s versus qoi-rust 427.4/290.0 Mp/s decode/encode) and the harness is public (bench/src/main.rs; qoi.h built at -O3 by libqoi/build.rs), but rustc version, C compiler and the Rust build profile are not stated, so it falls short of A; first-party, so C.
- **Verifier notes:** Numbers verified on the README; the record's 'single run per codec' was wrong (the harness repeats and takes medians) and is corrected. Not a duplicate under the qoixx precedent, but flag the Rust language mismatch. Metadata confirmed: MIT OR Apache-2.0, 129 stars, last commit 2025-07-27 (stale), not archived.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`, `baseline`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/README.md>
  - <https://github.com/aldanor/qoi-rust>
  - <https://github.com/aldanor/qoi-rust/commits>
  - <https://github.com/aldanor/qoi-rust/tree/master/ext>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/bench/src/main.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/libqoi/build.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/libqoi/Cargo.toml>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/encode.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/lib.rs>
  - <https://github.com/phoboslab/qoi/commit/8d35d93>
  - <https://crates.io/api/v1/crates/qoi>
- **Sources the enricher read:**
  - <https://github.com/aldanor/qoi-rust/issues?q=is%3Aissue>
  - <https://github.com/aldanor/qoi-rust/pulls?q=is%3Apr>
  - <https://github.com/aldanor/qoi-rust/issues/10>
  - <https://github.com/aldanor/qoi-rust/issues/14>
  - <https://github.com/aldanor/qoi-rust/issues/16>
  - <https://github.com/aldanor/qoi-rust/issues/26>
  - <https://github.com/aldanor/qoi-rust/pull/17>
  - <https://github.com/aldanor/qoi-rust/tree/master/tests>
  - <https://github.com/aldanor/qoi-rust/tree/master/ext>
  - <https://github.com/aldanor/qoi-rust/commits/master/README.md>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/README.md>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/bench/src/main.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/libqoi/build.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/libqoi/Cargo.toml>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/libqoi/src/lib.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/encode.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/decode.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/pixel.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/consts.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/header.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/error.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/types.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/src/utils.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/tests/common.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/tests/test_chunks.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/tests/test_gen.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/tests/test_misc.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/tests/test_ref.rs>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/a75e7fe44545077945a519a5b62c0cfb1e7d45a4/README.md>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/3fb2a4d7d9f4d841eb60d3986655c4aa715fd42f/README.md>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/3fb2a4d7d9f4d841eb60d3986655c4aa715fd42f%5E/README.md>
  - <https://crates.io/api/v1/crates/qoi>
  - <https://static.crates.io/crates/qoi/qoi-0.4.1.crate>
  - <https://raw.githubusercontent.com/phoboslab/qoi/master/qoi.h>
  - <https://github.com/phoboslab/qoi/commits/master/qoi.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/aldanor/qoi-rust`) · [data/wave10/enrich/raw/github_com_aldanor_qoi_rust.json](../../../data/wave10/enrich/raw/github_com_aldanor_qoi_rust.json) (enrichment confidence 0.8)

</details>
