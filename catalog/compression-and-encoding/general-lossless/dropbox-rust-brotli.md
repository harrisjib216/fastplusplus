# rust-brotli (Dropbox Rust port of Brotli)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause AND MIT` · 🟢 active

> Safe, no_std-capable Rust port of Google's Brotli encoder and decoder; slower than the C reference, not faster.

| | |
|---|---|
| **Beats** | google/brotli C reference implementation |
| **Claimed result** | Not faster than C. Dropbox post (search snippets only): the safe Rust decompressor ran at 72% of the speed of the vanilla gcc-4.9 -O3 C decompressor on 4 MB blocks, 217 MB/s on an Intel Core i7-4790 @ 3.60GHz; turning off allocator zeroing raised it to 224 MB/s (+3.2%, derived from page data) and the unsafe feature (no bounds checks, no memory initialisation) to 249 MB/s, 82% of the C code. Author's 2017 Hacker News comment (snippet only): about 80-90% of the original's speed on average, with some files compressing faster in Rust than with the original codec. Independent: android-doctor issue #74 (2026-10-03) measured brotli crate 9.0 decode at 250 MB/s against 391 MB/s for the C reference (1.56x slower) on 10-core Apple Silicon, and 4.65 s against 2.28 s (2.04x) on firmware images. The book's 'over 10 percent after removing initialization and bounds checking' compares the port with its own earlier version, not with C. |
| **Workload** | Dropbox 2016 post: decompression of 4 MB Brotli blocks by the safe-Rust decompressor (now the separate rust-brotli-decompressor crate that rust-brotli depends on) against the vanilla C decompressor built with gcc-4.9 -O3; no compression-speed table exists in the repo or the post snippets. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i7-4790 CPU @ 3.60GHz (per post snippet, 2016) |
| **Compiler and flags** | C baseline: gcc-4.9 -O3 (per post snippet). Rust compiler, version and flags for the 2016 measurement not stated. Current Cargo.toml release profile sets lto = true, incremental = false. |
| **Adoption** | 953 stars; brotli crate on crates.io |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/dropbox/rust-brotli) · [benchmark](https://dropbox.tech/infrastructure/lossless-compression-with-brotli) |

## Verdict

Dropbox's 2016 post, seen only as search snippets because dropbox.tech does not resolve here, measured the safe Rust decompressor at 217 MB/s, 72% of the C decompressor built with gcc-4.9 -O3, on 4 MB blocks on an Intel Core i7-4790 at 3.60 GHz, rising to 249 MB/s (82%) with the unsafe feature; the Rust toolchain was not stated and no benchmark code is public. Independently, android-doctor issue #74 (October 2026, 10-core Apple Silicon, release build) measured brotli 9.0 decoding at 250 MB/s against 391 MB/s for C via Python brotli (1.56x slower), then 4.65 s against 2.28 s end to end after switching to vendored libbrotli 1.1.0; neither run states quality, Python brotli version or compiler flags, and both predate brotli-decompressor 6.1.x. No compression-speed comparison with C exists.

## Use it when

- You need the Brotli format in pure safe Rust: wasm, cross-compiles without a C toolchain, or a no_std kernel or embedded target with your own allocator.
- Sandboxed decoding where every allocation is front-loaded into a memory pool before SECCOMP or a similar jail is switched on.
- Splitting work across cores or chunks: compress_multi for multithreaded compression of one buffer, or catable/appendable streams joined by byte concatenation or catbrotli.
- HTTP content-encoding in Rust servers at moderate quality (tower-http depends on it and sets quality 4), where encoder CPU rather than decode throughput is the concern.
- Brotli with custom LZ77 prefix dictionaries or serialized shared dictionaries (draft-vandevenne-shared-brotli-format) from Rust.

## Skip it when

- Decode throughput matters: every published number puts it behind C, from 72-82% of C speed (Dropbox 2016) to 1.56x slower in a 2026 third-party test; that project (android-doctor) switched to vendored C libbrotli 1.1.0 and cut its firmware extraction from 4.65 s to 2.28 s.
- You can choose the format: the catalog's zstd and LZ4 entries report decompression at 1,550 and 4,970 MB/s, far above the 250-391 MB/s Brotli decode figures here (different hardware, so only indicative).
- You want the newest decoder optimisations through this crate: brotli 9.0.0 pins brotli-decompressor \~6.0 (&gt;=6.0.0, &lt;6.1.0), so the 6.1.x speed work is only reachable by depending on brotli-decompressor directly for decoding.
- Your policy excludes AI-authored code: brotli-decompressor 6.0.0's changelog says its commits were 'effectively authored by Claude' and advises such users to stay on 5.x, which brotli 9.0.0 cannot use.
- You need bit-exact output with C at quality 10 or 11: the README only promises identical output at levels 0-9.

## How it is fast

It is not faster than the baseline: it reuses the same algorithms as C Brotli (LZ77 with hash-chain or binary-tree matchers, context modeling, Huffman coding) in safe Rust, so speed tracks C minus safety costs. The decompressor README names the expected losses: an extra indirection in the Huffman-group tables, array bounds checks on every access, and no aligned 64- or 128-bit loads from a byte slice. brotli-decompressor's optional unsafe feature swaps slice indexing for get_unchecked and skips memory initialisation, and its 6.1.0/6.1.1 releases (October 2026) add bulk back-reference and dictionary copies, a faster bit-reader refill and leaner Huffman-tree lookups, none of which has published numbers.

## Compared with alternatives

Choose it over the C codecs in this category (zstd, LZ4, zlib-ng, libdeflate) only when the Brotli format is required and a pure safe-Rust, no_std or C-toolchain-free build matters more than speed. Unlike lz4_flex, which matches or beats its C reference, this port trails C Brotli decoding by roughly 1.2x to 2x.

## Integration

| | |
|---|---|
| **Form** | crate (brotli on crates.io); optional C shared library via the ffi-api feature |
| **Dependencies** | alloc-no-stdlib 3.x, brotli-decompressor \~6.0, alloc-stdlib 0.3.x with the default std feature; sha2 \~0.10 only with the validation feature |
| **Minimum toolchain** | Rust 1.59 (rust-version), edition 2015; the simd feature needs nightly |
| **Platforms** | any Rust target; no_std with default-features = false; no hardware SIMD unless the nightly simd feature is enabled |
| **Thread safety** | Not documented for the stream objects; each Compressor/Decompressor owns its state, and compress_multi requires Send allocators per thread. 9.0.0 fixed #257, where the FFI's SendableMemoryBlock&lt;T&gt; claimed Send for non-Send T. |
| **Drop-in for the baseline** | partial — the ffi-api build exports the C libbrotli interface (README: drop-in for google/brotli), but the FFI has been off by default since 5.0.0 to avoid symbol conflicts, and the Rust API is not the C API. |

## Gotchas

- BrotliEncoderParams::default() uses quality 11 (lgwin 22), which is very slow; issue #93 (open since 2023-03-21) asks for a lower default, and tower-http overrides it to 4.
- Quality 10 is reused as a proxy for '9.5' (a hash-chain H9 mode) in the one-shot compressor, so it does not mean C's quality 10; the portable-float feature also changes emitted bytes (about 0.006% ratio).
- brotli 9.0.0 has no unsafe feature of its own; brotli-decompressor's unsafe feature (get_unchecked indexing, no memory initialisation) is only reachable by adding that crate directly with the feature enabled so Cargo unifies it.
- The Cargo description says all included code is safe and the README excepts only the FFI bindings, but the seccomp feature turns on alloc-no-stdlib's unsafe calloc-backed pools; the 'safe' feature removes the FFI's unsafe Send impls along with the encoder and multicompress FFI entry points.

## Known shortcomings

- Not faster than C: every number found has the Rust port slower than C Brotli (Dropbox 2016 post, snippet only: 217 MB/s, 72% of gcc-4.9 -O3 C on an i7-4790; unsafe mode 249 MB/s, 82%; issue #74 250 vs 391 MB/s); the book's &gt;10% gain compares the port with itself; no public bench code, Rust flags unstated.
- Enricher: brotli 9.0.0 pins brotli-decompressor \~6.0, so every measurement predates the 6.1.x decoder releases; the android-doctor 4.65 s vs 2.28 s figure is end-to-end, not pure decode; default quality is 11, not 9.5 (issue #93).

## Caveats and trade-offs

Does not beat the baseline on any number found: every figure puts Rust at or below C. The 72% / 217 / 224 / 249 MB/s / 82% figures come from search-result snippets of the Dropbox post (2016, i7-4790, gcc-4.9 -O3 C baseline, 4 MB blocks); dropbox.tech could not be opened in this session (DNS failure), so they are snippet only, though two separate snippets agree. The post measured decompression, whose code lives in dropbox/rust-brotli-decompressor (a dependency of this crate), not in this repo; no Rust compiler version or flags were given and no benchmark code is published. The Hacker News comment (news.ycombinator.com/item?id=14903412) is a 2017 self-report seen only as a snippet, with no per-file numbers, CPU or flags. The repo README makes no speed claim; the decompressor README lists the expected losses against C (extra hgroup indirection, bounds checks on every access, no aligned 64/128-bit loads from a byte slice). Independent reports show Rust slower than C: github.com/dropbox/rust-brotli/issues/76 (comment, 2023-05-13) reports decompressing a 50 GB texture tarball in 160 s against 90 s (the comment does not name which tool took which time, context implies Rust was slower; hardware, flags and quality not stated); github.com/Vaibhav91one/android-doctor/issues/74 measured brotli crate 9.0 decode at 250 MB/s against 391 MB/s for the C reference via Python brotli on a 10-core Apple Silicon release build (no flags or C version stated), and a later comment 4.65 s against 2.28 s (2.04x) on firmware images. A later Dropbox post (Broccoli, snippet only) mentions a decompression bug in rust-brotli-decompressor that Dropbox patched upstream. No public benchmark code with compiler, flags and CPU exists, so tier A and B do not apply. Flagged entry: notable and maintained (9.0.0 released 2026-09-02), but a safety-first port that is slower than C. [retier] Enricher: brotli 9.0.0 pins brotli-decompressor \~6.0, so it cannot pick up the 6.1.0 and 6.1.1 decoder releases (crates.io, 2026-10-11 and 2026-10-21); every measurement predates them. The android-doctor 4.65 s versus 2.28 s figure is end-to-end against vendored libbrotli 1.1.0, not pure decode, and that project then switched to the C library. The brotli-decompressor 6.0.0 changelog says its code was AI-authored.

Memory-safe (library description says all included code is safe), no_std capable with a pluggable allocator, SECCOMP-friendly front-loaded allocation, multithreaded compression, catable streams, C-compatible FFI, custom dictionaries. Encoder is stated to be bitwise identical to the C compressor at quality 0-9; quality 10 and 11 differ (default 9.5). Cost is decoder speed: the decompressor README lists an extra indirection in the hgroups, array bounds checks on every access and no aligned 64/128-bit loads from [u8] as expected losses.

## Maintenance

Actively maintained (9.0.0 on 2026-09-02, brotli-decompressor 6.1.1 on 2026-10-21), BSD-3-Clause AND MIT, about 302.6 million crates.io downloads; the safe, portable Brotli choice in Rust, not the fast one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification C, tier now C.
- **Tier reason:** Only first-party numbers exist (Dropbox 2016 post, seen via two independent search snippets because dropbox.tech fails DNS here) with C flags and CPU but no public benchmark code or Rust toolchain/flags; the independent reports (rust-brotli issue #76, android-doctor issue #74) give timings without full methodology. Every figure shows the Rust code slower than the C reference.
- **Verifier notes:** Reject as not-faster on valid evidence (miniz precedent); under the keep-and-document rule the orchestrator may override to keep with the not-faster shortcoming, since the record itself is honest about it and the crate is notable (953 stars, widely used brotli crate). Metadata confirmed: BSD-3-Clause AND MIT (sidebar and Cargo.toml), 953 stars, last commit 2026-09-02, not a fork, not archived; Cargo.toml release profile lto = true, incremental = false. A second snippet now confirms the 249 MB/s / 82% unsafe-mode figure the record had as unconfirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-68 (book seed pass, 2026-10-24); enrichment (wave 9 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/dropbox/rust-brotli>
  - <https://github.com/dropbox/rust-brotli/commits/master>
  - <https://github.com/dropbox/rust-brotli/issues/76>
  - <https://github.com/Vaibhav91one/android-doctor/issues/74>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli/HEAD/README.md>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli-decompressor/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dropbox/rust-brotli/HEAD/README.md>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli/HEAD/src/enc/mod.rs>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli/HEAD/src/enc/encode.rs>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli/HEAD/src/enc/multithreading.rs>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli/HEAD/src/enc/backward_references/mod.rs>
  - <https://github.com/dropbox/rust-brotli/commits/master>
  - <https://github.com/dropbox/rust-brotli/issues?q=is%3Aissue+slow+OR+performance+OR+speed>
  - <https://github.com/dropbox/rust-brotli/issues/76>
  - <https://github.com/dropbox/rust-brotli/issues/93>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli-decompressor/HEAD/README.md>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli-decompressor/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli-decompressor/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli-decompressor/HEAD/src/memory.rs>
  - <https://raw.githubusercontent.com/dropbox/rust-brotli-decompressor/HEAD/src/decode.rs>
  - <https://github.com/dropbox/rust-brotli-decompressor/tree/master/src>
  - <https://github.com/dropbox/rust-brotli-decompressor/commits/master>
  - <https://crates.io/api/v1/crates/brotli>
  - <https://crates.io/api/v1/crates/brotli-decompressor>
  - <https://github.com/Vaibhav91one/android-doctor/issues/74>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/dropbox/rust-brotli`) · [data/wave9/enrich/raw/github_com_dropbox_rust_brotli.json](../../../data/wave9/enrich/raw/github_com_dropbox_rust_brotli.json) (enrichment confidence 0.75)

</details>
