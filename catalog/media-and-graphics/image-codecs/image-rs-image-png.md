# image-png (Rust png crate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-safe-Rust PNG/APNG decoder and encoder that decodes faster than libpng on most images; Chromium's default PNG decoder.

| | |
|---|---|
| **Beats** | libpng 1.6.37 (Debian Bullseye) |
| **Claimed result** | Wuffs doc/benchmarks.md (September 2022), rust_png decode vs mimiclibpng: 19k_8bpp 187 vs 122 MB/s (1.53x), 40k_24bpp 260 vs 147 MB/s (1.77x), 77k_8bpp 330 vs 370 MB/s (0.89x), 552k_32bpp_verify_checksum 299 vs 289 MB/s (1.03x), 4002k_24bpp 264 vs 214 MB/s (1.23x); ratios are the page's vs_mimic column. Faster than libpng on four of five images. Crate README: 'Performance is typically on par with or better than libpng' and an fdeflate-powered fast encoding mode 'dramatically faster than the fastest mode of libpng while simultaneously providing better compression ratio' (no numbers on that page). |
| **Workload** | PNG decode to BGRA in the Wuffs 'mimic' benchmarks on five test images (bricks-gray 19k 8bpp, hat 40k 24bpp, bricks-dither 77k 8bpp, hibiscus.primitive 552k 32bpp with checksum verification, harvesters 4002k 24bpp), Rust 1.48 with png 0.17.5 / deflate 1.0.0 / miniz_oxide 0.5.3 vs Debian's libpng 1.6.37 through its simplified API; 5 reps after a warm-up rep. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-10210U @ 1.60GHz |
| **Compiler and flags** | Rust side: Rust 1.48, `cargo run --release` in script/bench-rust-png (default release profile, no profile overrides in its Cargo.toml), png 0.17.5. libpng side: Debian Bullseye's packaged libpng 1.6.37 linked into the Wuffs C harness test/c/std/png.c, compiled with gcc 10.2.1 or clang 11.0.1 at -O3 plus '-DWUFFS_MIMIC -lm -lpng -lz' (per the comment at the top of png.c); Debian's own build flags for libpng are not stated. |
| **Adoption** | 522 stars; png crate has 244.8 million crates.io downloads (79.8 million recent) |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/image-rs/image-png) · [benchmark](https://raw.githubusercontent.com/google/wuffs/HEAD/doc/benchmarks.md) |

## Verdict

Third-party Wuffs mimic benchmark, September 2022: png 0.17.5 (Rust 1.48, `cargo --release`, miniz_oxide 0.5.3 inflate with Adler-32 and CRC checked) vs Debian Bullseye libpng 1.6.37 through the simplified API (harness built with gcc 10.2.1 / clang 11.0.1 -O3), decoding five test images to BGRA (gray stays gray) on an Intel Core i5-10210U: 1.53x, 1.77x, 0.89x, 1.03x and 1.23x libpng's MB/s. The Rust side's timed loop also includes a scalar RGB/RGBA-to-BGRA swizzle that libpng does internally, so the comparison slightly handicaps Rust; current 0.18.x has not been re-measured on that page.

## Use it when

- Rust or mixed Rust/C++ codebases that decode untrusted PNG/APNG and want memory safety without giving up speed (it is Chromium's default PNG decoder since M139 and backs GNOME's glycin).
- Throughput-bound batch decoding of typical web/screenshot/photo PNGs: the maintainers' QOI-corpus run (2,848 images) reports 339.9 vs 180.4 MP/s geomean against libpng+zlib-ng on a Ryzen 9 7950X.
- APNG decoding or encoding, which upstream libpng does not support.
- Fast lossless PNG writing where a lighter compression ratio is acceptable: the fdeflate-based fast mode (fpnge-inspired) trades ratio for an order-of-magnitude encode speedup per the blog.

## Skip it when

- Plain C++ projects that cannot add a Rust toolchain and an FFI layer: the crate exposes only a Rust API (Chromium wrote its own integration).
- Android/ARM64 latency-sensitive decoding: Chromium's M136 field trial showed decode-time regressions of +2% to +9% across percentiles on Android while desktop improved about 15% in total (discussion #562).
- Windows builds where unfiltering dominates: issue #567 (Jan 2025) measured total decode time at 101% of libpng on Windows vs 79% on Linux, and 114-151% on one Paeth-heavy RGBA image, from different auto-vectorized code.
- When you need libpng's full transform set (gamma correction, rgb-to-gray, background compositing, custom row callbacks): only EXPAND, STRIP_16 and ALPHA exist; colour handling is left to the caller.
- Small-image workloads where the 2022 Wuffs numbers apply: on the 77k 8bpp paletted image png 0.17.5 was 0.89x libpng.

## How it is fast

Since 0.17.8 (after the Wuffs measurement) decompression always uses fdeflate, a custom safe DEFLATE decoder, and the zlib Adler-32 check is skipped by default while chunk CRC32 is still verified (crc32fast, simd-adler32 when checking). Unfiltering is written as component-wise unrolled byte-array loops that LLVM auto-vectorizes (src/filter/optimization-notes.md, PR #382), with explicit `std::simd` Paeth paths only behind the nightly `unstable` feature. 0.18 unfilters in place and shrinks internal buffers so data stays in cache between inflate and unfilter (image-rs blog, 2026-06-18).

## Compared with alternatives

Pick it over libspng when you can host Rust: in the 2026 QOI-corpus run it decodes about 1.46x spng's geomean on the 7950X (339.9 vs 233.1 MP/s, derived), while libspng stays the C option. Pick it over zune-png for broader adoption, APNG, encoding and a slight decode lead in the same run (339.9 vs 313.2 MP/s), and over Wuffs when you want a conventional Rust crate rather than generated C (Wuffs' C decoder was 1.55x-3.16x libpng and faster than png 0.17.5 on every image in 2022).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | bitflags, crc32fast, fdeflate, flate2 (miniz_oxide backend by default; optional zlib-rs feature) |
| **Minimum toolchain** | Rust 1.81 (rust-version in Cargo.toml for 0.18.1); `unstable` feature needs nightly |
| **Platforms** | any Rust target; SIMD comes from compiler auto-vectorization at the target's baseline (SSE2 on x86-64 unless you raise target-cpu); wasm32 builds |
| **Thread safety** | not documented beyond Rust's type system: each Decoder/Reader is a single-owner object; decode different images on different threads |
| **Drop-in for the baseline** | partial: replaces libpng's decode/encode role but with a different Rust API, no C ABI and fewer transforms |

## Gotchas

- Adler-32 is ignored by default (zlib.rs: `ignore_adler32: true`); call `Decoder::ignore_checksums(false)` or the StreamingDecoder setter if you need libpng-equivalent zlib integrity checking. Chunk CRCs are still verified.
- Default output is the IDENTITY transform: paletted, low-bit-depth and 16-bit images come back in their stored layout unless you set EXPAND / STRIP_16 (`Transformations::normalize_to_color8()`); there is no BGRA or filler output.
- 0.18 changed the API: `Decoder` needs `BufRead + Seek`, `output_buffer_size()` returns `Option<usize>`, and the `Decoded` event enum was reworked; code written for 0.17 does not compile unchanged.
- The nightly `unstable` (std::simd) feature can make decoding slower: Chromium disabled it after Windows regressions (issue #567), and the blog says it regresses ARM performance cores.

## Known shortcomings

- Rust crate (language-filter mismatch; C++ use needs FFI). Tier A on Wuffs doc/benchmarks.md (script/bench-rust-png and test/c/std/png.c at -O3, i5-10210U) against libpng 1.6.37: faster on 4 of 5 images, 0.89x on the 77k image; the measured png 0.17.5 dates from 2022 (now 0.18.1), and Wuffs's own C decoder is faster on every image.
- The 2022 Wuffs rows are sound (png 0.17.5 with miniz_oxide 0.5.3 checked Adler-32 and CRC), but bench-rust-png has no Cargo.lock (png = "0.17"), so a rerun resolves 0.17.16, and current 0.18 ignores Adler-32 by default; the Rust side also times an RGB-to-BGRA swizzle that libpng does internally, slightly handicapping Rust. Newer first-party evidence (image-rs blog 2026-06-18, harness fintelia/corpus-bench@png-0.18.0, 2848 QOI images: geomean 339.9 versus libpng plus zlib-ng 180.4 MP/s on a 7950X; M4 310.5 versus 177.6) skews toward image-png (libpng forced to RGBA8 output, one decode per image without warm-up, no output check, libpng version unstated), so it is an upper bound at C. Chromium data: discussion #562 (M136 trial: desktop decode 15% faster in total, Android 9% slower) and issue #567 (79% of libpng runtime on Linux, 101% on Windows).

## Caveats and trade-offs

Rust crate, not C++: it fails the C++ language filter and is usable from C++ only through FFI. Mixed result: one of five images is slower than libpng (0.89x on 77k_8bpp). The numbers are for png 0.17.5 measured in September 2022 on one laptop CPU; the current release is 0.18.1 (rust-version 1.81, fdeflate-based decoding) and has not been re-measured on that page. The same page shows Wuffs' own C decoder at 1.55x-3.16x of libpng, faster than rust_png on every image. The Rust harness times an extra RGB/RGBA-to-BGRA conversion loop that libpng's simplified API does internally. The crate's own benches/decoder.rs is a criterion self-benchmark with no libpng comparison. The fast-encode claim has no numbers on the crate page. zune-image's benchmarks/benchmark-results.md (Darwin, CPU not named) compares against the spng binding, not libpng: image-rs/png is faster than spng on all four PNG decode cases (for example 149.3 ms vs 297.4 ms on the baseline image) but slower than zune-png on two of them.

Pure Rust, no unsafe code, fuzzed on OSS-Fuzz, so it is not callable from C++ without bindings. Also supports APNG. Fast encode mode uses fdeflate (already catalogued separately).

## Maintenance

Actively maintained (last commit 2026-09-23, 0.18.1 current, about 245 million crates.io downloads), MIT OR Apache-2.0, shipped to all Chrome users since M139 (August 2025) and used by GNOME 49 through glycin; only one open bug-labelled issue (#286, zlib decompression may exceed allocation limits, 2021).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Third-party (Wuffs authors) mimic benchmark against libpng 1.6.37 with public code (google/wuffs script/bench-rust-png/src/main.rs for the Rust side, test/c/std/png.c plus test/c/mimiclib/png.c for libpng, built with -O3), stated toolchains (Rust 1.48 cargo --release, gcc 10.2.1 / clang 11.0.1, Debian Bullseye) and CPU (Intel Core i5-10210U); all five rust_png rows match the record.
- **Verifier notes:** Numbers verified line by line in the Wuffs doc; the record said six images but the rust_png benchmark has five (552k appears once). Language field is correctly Rust; orchestrator should apply the C++ language-filter policy (keep with shortcoming or move to an 'any language' bucket). Metadata checked on github.com: MIT OR Apache-2.0, not archived, not a fork, last commit 2026-09-23.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** image-rs blog 2026-06-18 (fintelia/corpus-bench at png-0.18.0, 2848 QOI-suite images, upper bound: libpng forced to RGBA8, no warm-up, no output check): geomean 339.9 MP/s versus libpng plus zlib-ng 180.4 MP/s on a Ryzen 9 7950X; Apple M4 310.5 versus 177.6 MP/s. Chromium M136 field trial (discussion #562): desktop decode 15% faster in total, Android 9% slower.
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/script/bench-rust-png/Cargo.toml>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/script/bench-rust-png/src/main.rs>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/test/c/std/png.c>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/README.md>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/benches/decoder.rs>
  - <https://github.com/image-rs/image-png>
  - <https://github.com/image-rs/image-png/commits>
  - <https://crates.io/api/v1/crates/png>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/HEAD/README.md>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/HEAD/benchmarks/benchmark-results.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/README.md>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/benches/decoder.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/src/common.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/src/decoder/mod.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/src/decoder/zlib.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/src/decoder/stream.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/src/decoder/unfiltering_buffer.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/src/encoder.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/src/filter/mod.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/HEAD/src/filter/optimization-notes.md>
  - <https://raw.githubusercontent.com/image-rs/image-png/v0.17.5/src/decoder/zlib.rs>
  - <https://raw.githubusercontent.com/image-rs/image-png/v0.17.5/src/decoder/stream.rs>
  - <https://raw.githubusercontent.com/Frommi/miniz_oxide/0.5.3/miniz_oxide/src/inflate/core.rs>
  - <https://github.com/image-rs/image-png/tree/master/src>
  - <https://github.com/image-rs/image-png/tree/master/src/filter>
  - <https://github.com/image-rs/image-png/issues?q=is%3Aissue+libpng+performance>
  - <https://github.com/image-rs/image-png/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/image-rs/image-png/issues/415>
  - <https://github.com/image-rs/image-png/issues/567>
  - <https://github.com/image-rs/image-png/discussions/562>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/script/bench-rust-png/src/main.rs>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/script/bench-rust-png/Cargo.toml>
  - <https://raw.githubusercontent.com/google/wuffs/HEAD/test/c/mimiclib/png.c>
  - <https://github.com/image-rs/image-rs.github.io>
  - <https://github.com/orgs/image-rs/repositories?q=blog>
  - <https://github.com/image-rs/blog.image-rs.org>
  - <https://github.com/image-rs/blog.image-rs.org/tree/gh-pages/_posts>
  - <https://raw.githubusercontent.com/image-rs/blog.image-rs.org/gh-pages/_posts/2026-06-18-png-adoption.md>
  - <https://github.com/fintelia/corpus-bench/tree/png-0.18.0>
  - <https://raw.githubusercontent.com/fintelia/corpus-bench/png-0.18.0/README.md>
  - <https://raw.githubusercontent.com/fintelia/corpus-bench/png-0.18.0/Cargo.toml>
  - <https://raw.githubusercontent.com/fintelia/corpus-bench/png-0.18.0/Cargo.lock>
  - <https://raw.githubusercontent.com/fintelia/corpus-bench/png-0.18.0/decode-png/Cargo.toml>
  - <https://raw.githubusercontent.com/fintelia/corpus-bench/png-0.18.0/decode-png/build.rs>
  - <https://raw.githubusercontent.com/fintelia/corpus-bench/png-0.18.0/decode-png/src/main.rs>
  - <https://raw.githubusercontent.com/fintelia/corpus-bench/png-0.18.0/harness/Cargo.toml>
  - <https://raw.githubusercontent.com/fintelia/corpus-bench/png-0.18.0/harness/src/lib.rs>
  - <https://raw.githubusercontent.com/fintelia/corpus-bench/png-0.18.0/third_party/qoi/qoibench.c>
  - <https://raw.githubusercontent.com/image-rs/image/v0.25.8/src/codecs/png.rs>
  - WebSearch: Chromium Rust png crate SkPngRustCodec replace libpng performance (snippets only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/image-rs/image-png`) · [data/wave10/enrich/raw/github_com_image_rs_image_png.json](../../../data/wave10/enrich/raw/github_com_image_rs_image_png.json) (enrichment confidence 0.8)

</details>
