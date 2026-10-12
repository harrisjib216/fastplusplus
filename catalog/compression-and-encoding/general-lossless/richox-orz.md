# orz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust ROLZ compressor: near-xz -6 ratio on enwik8 text with about 13x faster single-threaded encode; decode slower than zstd.

| | |
|---|---|
| **Beats** | xz -6, zstd -19/-15/-10, brotli -9/-8/-7, bzip2 -9, lzfse, gzip -6 (GNU gzip CLI) |
| **Claimed result** | orz -l2 compresses enwik8 to 26,892,825 bytes in 3.360 s versus xz -6 26,665,156 bytes in 44.936 s and zstd -19 26,944,223 bytes in 45.985 s (derived from page data: about 13x faster encode than xz -6 at 0.85% larger output). orz -l0: 27,898,433 bytes in 1.773 s versus gzip -6 36,548,933 bytes in 2.441 s (smaller and faster) and zstd -10 30,697,508 bytes in 1.958 s. Decode is slower than zstd and gzip: orz 0.578-0.603 s versus zstd 0.082-0.085 s and gzip -6 0.107 s; xz -6 decodes in 0.812 s. |
| **Workload** | Compression and decompression of enwik8 (100 MB Large Text Compression Benchmark file) with each tool's command line; the repo also runs the table in a GitHub Actions workflow (enwik8-benchmark.yml) on ubuntu-latest. |
| **Metric** | throughput |
| **Hardware** | README table: not stated. Workflow: GitHub-hosted ubuntu-latest runner, CPU model not stated. |
| **Compiler and flags** | Workflow: Rust nightly via actions-rust-lang/setup-rust-toolchain, rustflags '--allow warnings -C target-feature=+aes', cargo build --release (Cargo.toml release profile: opt-level 3, lto true, codegen-units 1, overflow-checks false). Baseline tools are apt packages on ubuntu-latest (versions not pinned). |
| **Adoption** | 817 stars; latest tag v1.6.2 |
| **Last commit** | 2026-03-18 |
| **Links** | [repository](https://github.com/richox/orz) · [benchmark](https://raw.githubusercontent.com/richox/orz/HEAD/README.md) |

## Verdict

First-party README table, single wall-clock runs on enwik8 (100 MB English text) on an unnamed machine: orz -l2 26,892,825 bytes in 3.360 s encode versus xz -6 26,665,156 bytes in 44.936 s and zstd -19 26,944,223 bytes in 45.985 s; orz -l0 27,898,433 bytes in 1.773 s versus gzip -6 36,548,933 bytes in 2.441 s; decode 0.578-0.603 s versus zstd 0.082-0.085 s. The GitHub Actions workflow reruns a similar but not identical set (gzip -9, brotli -6/-9, no lzfse) on ubuntu-latest with apt baseline CLIs and Rust nightly release/LTO, using the shell time builtin.

## Use it when

- Archiving or shipping large text-like data (logs, wikis, source dumps) where you want xz -6 / zstd -19 class ratio but cannot afford 45 s per 100 MB of encode time
- Single-threaded compression pipelines where encode CPU is the bottleneck and a decode of about 0.6 s per 100 MB is acceptable
- Rust projects that control both producer and consumer and can build with a nightly toolchain
- As a faster-than-gzip -6 replacement for internal text blobs where ratio matters more than decode speed (orz -l0 was both smaller and faster than gzip -6 on enwik8)

## Skip it when

- Decode-heavy workloads (read-many, serving): orz decodes enwik8 in about 0.58-0.60 s versus about 0.08 s for zstd, roughly 7x slower
- Untrusted or possibly corrupted input: the decoder trusts length fields from the stream and writes through unchecked raw pointers (see gotchas), and the format has no checksum or magic header
- C or C++ projects wanting a C ABI: the crate builds staticlib/cdylib, but the ffi module is commented out in src/lib.rs, so there is no exported C API
- Interoperability needs (HTTP content-encoding, tar.xz/.zst tooling): the format is private to orz and appears to change between releases
- Small inputs or memory-constrained targets: the encoder allocates about 80 MB of buffers and the decoder about 112 MB up front regardless of input size (from buffer constants in src/lib.rs)

## How it is fast

It uses ROLZ (reduced-offset Lempel-Ziv): matches are searched only among recent positions in one of 256 buckets selected by the previous byte (4094 entries each), so an offset is a small bucket index rather than a full distance and match search is cheap. Symbols (literals, 2-byte word predictions, and reduced-offset/length ids) go through a context-sensitive symbol-ranking (move-to-front) transform and then static Huffman coding per 1 MB chunk. The hot paths use nightly portable_simd 16-byte compares for match length, unchecked indexing and unaligned raw-pointer loads and stores.

## Compared with alternatives

Pick orz over zstd -19 or xz -6 when encode time dominates and decode speed does not (similar enwik8 size, about 13x faster encode); prefer zstd when decode speed or a standard format matters, and Kanzi, libbsc or bzip3 when you need a C/C++ library with a C API or multithreading. libzling, the same author's older C++ ROLZ codec, is the choice if you need C++ source rather than a nightly Rust crate.

## Integration

| | |
|---|---|
| **Form** | crate (git dependency) plus CLI binary |
| **Dependencies** | bitfield-struct, clap (CLI), unchecked-index |
| **Minimum toolchain** | Rust nightly (edition 2024; #![feature(portable_simd)] and #![feature(likely_unlikely)]) |
| **Platforms** | not documented; portable_simd code is architecture-generic, CI runs only x86-64 ubuntu-latest with -C target-feature=+aes (no AES use found in src) |
| **Thread safety** | not documented; single-threaded, encoder/decoder state is per-stream and owned by &mut self |
| **Drop-in for the baseline** | no |

## Gotchas

- Memory safety on bad input (from reading src/lz.rs, src/coder.rs, src/mem.rs; not tested): LZDecoder::decode loops for a match_items_len read from the stream and writes at spos via raw-pointer put() with no check against sbuf length, and BitBuffer::load_u32 reads 4 bytes at input_pos with no check against the chunk length, so a crafted or truncated .orz can cause out-of-bounds heap reads and writes in release builds. The symbol range check uses an inclusive bound (0..=SYMRANK_NUM_SYMBOLS), one past the table size. Issue #24 'Remove unsafe blocks without hurting performance' is open.
- BytesConstPtrExt::get starts from MaybeUninit::uninit().assume_init() for integer and SIMD types, which is undefined behaviour under Rust's rules even though the bytes are then overwritten.
- The crates.io name 'orz' belongs to an unrelated project (a multi-agent server, v2.1.4), so 'cargo add orz' pulls the wrong crate; use the git tag (README: cargo install orz --git ... --tag v1.6.2). Cargo.toml on master still says version 1.6.1.
- No container magic, version byte or checksum; recent commits ('reduce bytes size of initial symrank table', 'improve huffman table encoding effeciency') change the bitstream, so keep the producing version pinned. Issue #27 (stack overflow on Windows, 2022) is still open, though the current code heap-allocates its big buffers.

## Known shortcomings

- No CPU model. The CI workflow runs gzip -9 and brotli -6/-9 while the README table says gzip -6 and brotli -7/-8/-9. Baseline is GNU gzip, not zlib. Rust only, no C API.
- Read in code, not run: LZDecoder::decode's output position and BitBuffer::load_u32's input position are never checked against buffer lengths, and match_items_len comes from the stream, so a crafted or truncated .orz can read and write past heap buffers in a release build. The symbol range check is off by one. MaybeUninit::uninit().assume_init() on integer/SIMD types is UB. The format has no checksum, magic or version byte and the bitstream changes between releases. Needs Rust nightly (portable_simd); the ffi module is commented out so there is no C ABI; the crates.io name orz belongs to an unrelated project. The decoder allocates about 112 MB up front and decodes about 7x slower than zstd. Issues #24 (unsafe) and #27 (Windows stack overflow) open.

## Caveats and trade-offs

The benchmark script is public and the workflow gives the compiler and flags, but no CPU model is stated and the baseline tool versions are not pinned (apt on ubuntu-latest), so it falls short of tier A. The README table was produced on an unnamed machine and does not match the workflow's rows: the workflow runs gzip -9 and brotli -6/-9 and has no lzfse, while the README shows gzip -6, brotli -7/-8/-9 and lzfse. The gzip row is the GNU gzip CLI, not the zlib library. Only one file was tested (enwik8, English text), so the ratio claims may not hold for binary data. The baseline levels are mostly the high-ratio ones. Decoding is not a win: orz decodes in about 0.58-0.60 s against 0.08 s for zstd and 0.107 s for gzip, though it is faster than xz -6 (0.812 s) and bzip2 (1.795 s). The claim is compression speed at a matched ratio. It is a ROLZ codec with its own format, so it does not replace the zlib or zstd formats. Same author as libzling.

ROLZ + move-to-front + static Huffman: strong ratio for text at high compression speed but slow decode compared with zstd, brotli, gzip (about 7x slower than zstd). CPU-feature flag +aes is set in the workflow, which suggests the Rust build is tuned for x86 with AES; portability of the speed claim to other CPUs is untested. Rust nightly toolchain needed (edition 2024).

## Maintenance

Active (last commit 2026-03-18, regular performance commits through 2025-2026, 817 stars), MIT OR Apache-2.0; usable as a Rust CLI or crate, but not as a hardened library for untrusted input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Every number in the README enwik8 table matches the record. The benchmark script is public (.github/workflows/enwik8-benchmark.yml) and the build flags are given, but no CPU model is stated and the README table's machine is unnamed, so it falls short of A. The numbers are first-party, so C.
- **Verifier notes:** The README table matches the record exactly, and the derived ratios check out (44.936/3.360 = 13.4x; size is 0.85% larger). Metadata from github.com: 817 stars, 50 forks, MIT/Apache-2.0, latest tag v1.6.2, last commit 2026-03-18, active.
- **Fields the verifier corrected:** `compiler_and_flags`, `baseline`, `caveats`
- **Shortcomings recorded by:** first-party README table
- **Pages the verifier opened:**
  - <https://github.com/richox/orz>
  - <https://github.com/richox/orz/commits/master>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/README.md>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/.github/workflows/enwik8-benchmark.yml>
- **Sources the enricher read:**
  - <https://github.com/richox/orz/tree/master/src>
  - <https://github.com/richox/orz/issues?q=is%3Aissue>
  - <https://github.com/richox/orz/issues/27>
  - <https://github.com/richox/orz/issues/29>
  - <https://github.com/richox/orz/commits/master>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/README.md>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/.github/workflows/enwik8-benchmark.yml>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/lz.rs>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/coder.rs>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/huffman.rs>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/matcher.rs>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/mem.rs>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/symrank.rs>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/ioutil.rs>
  - <https://raw.githubusercontent.com/richox/orz/HEAD/src/progress.rs>
  - <https://crates.io/api/v1/crates/orz>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/richox/orz`) · [data/wave9/enrich/raw/github_com_richox_orz.json](../../../data/wave9/enrich/raw/github_com_richox_orz.json) (enrichment confidence 0.75)

</details>
