# fdeflate

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Safe-Rust zlib/deflate codec tuned for PNG data; decoder claimed on par with zlib-ng and zlib-rs, encoder still preliminary.

| | |
|---|---|
| **Beats** | zlib-rs and zlib-ng (zlib-compatible deflate/inflate); also compared with miniz_oxide and libdeflate on the plot |
| **Claimed result** | Third-party flate2_bench run (issue #75, Zen 4, Govdocs1 in 4 KiB chunks): level 1 fdeflate 91.5 MB/s vs zlib-ng 173.7 (slower); level 6 94.3 vs 65.5 MB/s (1.44x); level 9 53.5 vs 32.4 MB/s (1.65x) (derived from page data). |
| **Workload** | Deflate compression levels 1-7 and decompression of PNG-style data, measured with corpus-bench on the QOI benchmark corpus. |
| **Metric** | throughput |
| **Hardware** | AMD Zen 4 (model not stated), issue #75 run |
| **Adoption** | 38 stars; compression backend of the png crate; 175.7M all-time crates.io downloads (58.1M recent) |
| **Last commit** | 2026-05-31 |
| **Links** | [repository](https://github.com/image-rs/fdeflate) · [benchmark](https://github.com/image-rs/fdeflate/issues/75) |

## Verdict

The project's own evidence is directional: README says the decoder 'rivals or exceeds' zlib-ng and zlib-rs and the encoder beats zlib-rs at levels 1-3, backed only by a corpus-bench scatter plot on the QOI corpus (discussion #68, numbers unreadable here, no CPU or compiler). The only numbers found are third-party (issue #75, flate2_bench on Zen4, Govdocs1 in 4 KiB chunks): fdeflate main was about 1.4x zlib-ng at level 6 and 1.65x at level '9' (actually level 7), but about 0.5x zlib-ng at level 1.

## Use it when

- Rust programs that decode PNG or other zlib streams with many literals and want zlib-ng-class inflate speed without C dependencies or unsafe code in the codec itself.
- Real-time PNG encoding where file size matters less than speed: the ultra-fast mode targets QOI-like encode speed while staying zlib-compatible.
- Rust builds that track git main and want the 0.4 encoder: a third-party Zen4 run (issue #75, flate2_bench, Govdocs1 in 4 KiB chunks) measured 94.3 MB/s at level 6 vs zlib-ng 65.5 and zlib-rs 59.6 MB/s at a slightly lower ratio (1.809 vs 1.837).
- Code already going through the png crate, which pulls fdeflate in for you.

## Skip it when

- C or C++ projects: there is no C API or binding; zlib-ng or libdeflate give comparable decode speed with a C interface.
- Fast compression at level 1: issue #75 measured fdeflate level 1 at 91.5 MB/s and ratio 1.474 vs zlib-ng 173.7 MB/s / 1.650 and miniz_oxide 220.1 MB/s on Govdocs1 (Zen4), and the issue was closed as not planned.
- Maximum ratio: levels 8 and 9 are accepted but run the same configuration as level 7 (Compressor::new maps 7.. to one LazyParser setting), and ratio stays slightly below zlib-ng at every measured level.
- Decoding untrusted input where CPU time must be bounded: issue #83 (July 2026) shows chains of tiny dynamic-Huffman blocks forcing a full 4096-entry table rebuild each, about 3 s for 1,000,000 blocks with no output; it was closed as not planned and current main has no rebuild limit.
- Users needing a stable released encoder: crates.io still ships 0.3.7 (2024-12-06) with only ultra-fast compression; Cargo.toml on main is publish = false.

## How it is fast

The decoder uses a 4096-entry primary Huffman table to fit modern L1 caches, multi-symbol literal decoding (two or three literals per table lookup, the technique from Yann Collet's 'Huffman revisited part 4' post), precomputed fixed-Huffman tables and a 64-bit bit buffer refilled with one unaligned 8-byte load. The ultra-fast encoder writes a single block with one fixed Huffman tree trained on PNG images (codes of 12 bits or less) and emits only zero-run back-references, borrowing from fpnge. The 0.4 encoder uses greedy parsing with hash-table or hash-chain match finders at levels 1-3 and lazy parsing with a hybrid match finder at levels 4-7; Adler-32 comes from the SIMD simd-adler32 crate.

## Compared with alternatives

Pick it over zlib-ng or libdeflate only inside pure-Rust stacks (especially PNG pipelines) that refuse C dependencies; from C++ use zlib-ng, which is catalogued with full lzbench numbers, or libdeflate for whole-buffer work.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | simd-adler32 (runtime); miniz_oxide and rand only as dev-dependencies |
| **Minimum toolchain** | Rust 1.88 on main (rust-version in Cargo.toml); Rust 1.67 for the published 0.3.7 |
| **Platforms** | any Rust target; CI also runs tests on big-endian powerpc under QEMU; no architecture-specific code in the crate (SIMD only inside simd-adler32) |
| **Thread safety** | not documented; Decompressor and Compressor are plain owned state objects with no shared globals, so one instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Released 0.3.7 skips the Adler-32 update when read() returns early after flushing a queued RLE or back-reference run into a small output buffer, which can raise a false checksum error on a valid stream; main fixed it on 2026-05-27 (PR #82, test checksum_includes_queued_output) but no release carries the fix.
- Issue #80 (May 2026, closed as not planned with no maintainer comment) reports a panic on malformed input when the bit count wraps; in 0.3.7 the fill_buffer fast path computes input[(63 - nbits)/8..], which panics if nbits ever exceeds 63, while main masks nbits with & 63 since PR #50 (June 2025). consume_bits still only debug_asserts against underflow on main.
- Decompressor::read may write past the returned length and needs the previous 32 KiB of output kept in the same buffer; it panics if output_position is out of bounds.
- #![forbid(unsafe_code)] covers this crate only; the simd-adler32 dependency uses unsafe SIMD intrinsics. The encoder always writes zlib header bytes 0x78 0x01 regardless of level.

## Known shortcomings

- Directional only: the comparison against zlib-rs exists as a plot in discussion #68 (image host blocked) and the README gives no numbers. Kept as the png crate's backend (175.7M crates.io downloads).
- Released 0.3.7 has an Adler-32 bug: queued RLE or backref output is left out of the checksum, so a valid stream can fail with a checksum error; fixed on main by PR #82 (2026-05-27) but unreleased (Cargo.toml publish = false). Issue #80: fill_buffer in 0.3.7 panics on malformed input; main masks it with &63 but consume_bits still has only a debug_assert. Issue #83: Huffman-table rebuild DoS (about 3 s per 1M empty blocks), closed not planned. Levels 8-9 run level 7's config. No C API. Mixed against zlib-ng in the third-party flate2_bench run (Zen 4, Govdocs1 in 4 KiB chunks): level 1 91.5 vs 173.7 MB/s (slower), level 6 94.3 vs 65.5, level 9 53.5 vs 32.4.

## Caveats and trade-offs

No numbers could be read: the only data is a plot image in discussion #68 (blocked here), which the author calls very preliminary, and its compared libraries are not named in text. The benchmark harness is the separate fintelia/corpus-bench repo; no CPU or compiler stated. Baselines are zlib-rs and zlib-ng, not upstream zlib directly. Only levels 1-7 are implemented (8-9 missing). Rust only; not callable from C++ without writing a binding. Latest crates.io release is 0.3.7 (2024-12); the compressor work on main is unreleased. Re-tier to C if someone reads the plot values. [retier] Mixed result: slower than zlib-ng at level 1, faster at levels 6-9 on 4 KiB chunks.

Rust crate with no C API shown; safe Rust without unsafe. Optimised for PNG-style data (many literals), levels 8-9 not implemented, compressor still under development (0.4.x), ultra-fast mode uses one block, one fixed Huffman tree and no distance codes except zero runs, so ratio is low.

## Maintenance

Actively developed (last commit 2026-05-31) and dual MIT/Apache-2.0, but the improved encoder and the checksum fix exist only on unpublished main, and two 2026 robustness reports (#80, #83) were closed without fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now B.
- **Tier reason:** Discussion #68 (fintelia, 2026-01-17) has only a scatter plot from corpus-bench on the QOI corpus; it gives no numbers in text and names no libraries in text. The plot image (private-user-images.githubusercontent.com) was blocked, so no number could be checked. The README claims ('meaningfully outperforms zlib-rs for levels 1-3', decoder 'rivals or exceeds' zlib-ng and zlib-rs) are directional only.
- **Retiered** D to B: Raised D to B: the enricher found a third-party measurement with numbers in issue #75 (flate2_bench harness, AMD Zen 4, Govdocs1 in 4 KiB chunks) comparing fdeflate with zlib-ng: level 1 91.5 vs 173.7 MB/s (slower), level 6 94.3 vs 65.5 MB/s (1.44x), level 9 53.5 vs 32.4 MB/s (1.65x), derived from page data. Independent and numeric, so B; not A because rustc version and flags are not stated. The win is mixed and the caveats say so.
- **Verifier notes:** Downgraded C to D because the numbers could not be checked. Not rejected: it is notable through use (png crate backend, about 176M crates.io downloads). zlib-ng is already catalogued, so baseline_in_list is true. License MIT OR Apache-2.0 and last commit 2026-05-31 verified.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `stars_or_usage`, `caveats`, `benchmark_url`, `hardware`
- **Shortcomings recorded by:** first-party plot; independent flate2_bench run (issue #75, Zen 4)
- **Pages the verifier opened:**
  - <https://github.com/image-rs/fdeflate>
  - <https://github.com/image-rs/fdeflate/commits/main>
  - <https://github.com/image-rs/fdeflate/discussions/68>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/README.md>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/fdeflate>
- **Sources the enricher read:**
  - <https://github.com/image-rs/fdeflate>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/README.md>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/src/decompress.rs>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/src/tables.rs>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/src/huffman.rs>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/src/compress/mod.rs>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/src/compress/ultrafast.rs>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/HEAD/.github/workflows/rust.yml>
  - <https://raw.githubusercontent.com/image-rs/fdeflate/v0.3.7/src/decompress.rs>
  - <https://github.com/image-rs/fdeflate/tree/main/src/compress>
  - <https://github.com/image-rs/fdeflate/issues?q=is%3Aissue>
  - <https://github.com/image-rs/fdeflate/issues/75>
  - <https://github.com/image-rs/fdeflate/issues/80>
  - <https://github.com/image-rs/fdeflate/issues/83>
  - <https://github.com/image-rs/fdeflate/pull/82>
  - <https://github.com/image-rs/fdeflate/commits/main>
  - <https://github.com/image-rs/fdeflate/discussions/68>
  - <https://github.com/fintelia/corpus-bench>
  - <https://crates.io/api/v1/crates/fdeflate>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/image-rs/fdeflate`) · [data/wave9/enrich/raw/github_com_image_rs_fdeflate.json](../../../data/wave9/enrich/raw/github_com_image_rs_fdeflate.json) (enrichment confidence 0.7)

</details>
