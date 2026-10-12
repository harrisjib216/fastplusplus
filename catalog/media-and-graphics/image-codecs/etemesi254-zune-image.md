# zune-png (zune-image workspace)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (C API via crates/zune-capi)` · `Apache-2.0 OR MIT OR Zlib` · 🟢 active

> Pure-Rust PNG/APNG decoder (zune-png) that decodes 1.5x-2.7x faster than an old libspng 0.6.3 build in the maintainer's criterion run.

| | |
|---|---|
| **Beats** | libspng 0.6.3 through the Rust spng 0.1.0 binding (spng-sys 0.1.0, 2021) linked to bundled stock zlib via libz-sys (zlib-ng feature off); libpng is not measured |
| **Claimed result** | benchmarks/benchmark-results.md (Darwin, criterion mean, ms; spng vs zune-png): baseline 297.4 vs 135.0 (spng 2.20x slower, as printed); interlaced 8bpp 378.0 vs 139.7 (2.71x, as printed); 16 bpp 541.2 vs 186.3 (2.9x, derived from page data); palette 53.59 vs 35.21 (1.5x, derived from page data). image-rs/png beats zune-png on 16 bpp (163.7 ms; zune 1.14x slower) and palette (28.31 ms; zune 1.24x slower). These ratios overstate the library gap: the spng side is libspng 0.6.3 (2021) on stock zlib with its ARM NEON path disabled, and it verifies chunk CRCs while zune-png verifies neither CRC nor Adler-32. |
| **Workload** | Criterion decode from an in-memory buffer of four PNG files from the zune-image test-images set (speed_bench.png, speed_bench_interlaced.png, speed_bench_16.png, speed_bench_palette.png), one thread per decode for all three libraries: zune-png decode_raw with default DecoderOptions, image-rs/png 0.18.0-rc.3 with EXPAND and ignore_checksums(true), and the spng 0.1.0 binding with Format::Png (native layout), TRANSPARENCY and IGNORE_ADLER32. Outputs are not cross-checked, and their layouts differ. |
| **Metric** | throughput |
| **Hardware** | Unnamed Darwin (macOS) machine; CPU model not given (the benchmarks README's Homebrew /opt/homebrew setup suggests Apple Silicon). The benchmarks README also lists an AMD EPYC-Rome KVM Linux box, but the results file has only Darwin columns. |
| **Compiler and flags** | cargo bench with criterion 0.8.1 (20 s measurement time) under the workspace bench profile (release opt-level 3 plus debug info, no target-cpu flags); libspng compiled by the cc crate in spng-sys build.rs (SPNG_SSE defined only for x86 targets with ssse3/sse4.1); rustc and C compiler versions not stated |
| **Adoption** | 505 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/etemesi254/zune-image) · [benchmark](https://raw.githubusercontent.com/etemesi254/zune-image/HEAD/benchmarks/benchmark-results.md) |

## Verdict

One first-party criterion run (commit 0875e77, 2026-09-21) on an unnamed Darwin machine, probably Apple Silicon, decoding four images from the maintainer's own test set: zune-png beat the Rust spng 0.1.0 binding (libspng 0.6.3 from 2021, stock zlib, NEON unfilter disabled, CRC still verified) by 2.20x baseline, 2.71x interlaced, 2.9x 16 bpp and 1.5x palette, but it lost to image-rs/png on 16 bpp and palette. The measured zune-png is unreleased dev-branch code that verifies neither checksum, libpng is not measured, and no rustc or C compiler version is given.

## Use it when

- Rust services or tools that decode many ordinary 8-bit RGB/RGBA PNGs and want a dependency-free, no_std-capable decoder (the run shows 135.0 ms vs 149.3 ms for image-rs/png on the baseline image).
- Adam7-interlaced 8-bit PNGs: the largest margin in the run (139.7 ms vs 232.8 ms for image-rs/png and 378.0 ms for spng).
- APNG playback where you want frame disposal and blending handled for you (ApngContext::process_frame).
- Pipelines already using zune-image (JPEG, QOI, HDR, filters) that want one Rust image type with 8/16-bit and f32 support.

## Skip it when

- C or C++ code that wants a libpng/libspng replacement: there is no PNG-level C API, only zune-capi's whole-library zil_\* calls built as a Rust staticlib/dylib.
- 16-bit or palette PNGs: image-rs/png beat zune-png in the same harness (163.7 vs 186.3 ms on 16 bpp; 28.31 vs 35.21 ms on palette).
- Untrusted or integrity-sensitive input: the benchmarked dev decoder cannot verify CRC-32 or Adler-32 at all, and issue #221 (52 fuzzer crash files with panics in zune-png, opened July 2024) and #384 (out-of-memory panic) are still open.
- Anyone installing from crates.io expecting these numbers: the measured decoder is the unreleased dev branch; zune-png 0.5.2 on crates.io (2026-03-11) is the older whole-buffer decoder on zune-inflate 0.2.54 (2023), which has no StreamingDecoder.
- Images wider or taller than 16384 pixels unless you raise max_width/max_height in DecoderOptions.

## How it is fast

The benchmarked dev-branch decoder (rewritten in May 2026) streams IDAT data through zune-inflate's StreamingDecoder, a libdeflate-style table-driven inflater, into a sliding buffer and unfilters each row as soon as it is available, writing straight into the output where no post-processing is needed (two-row ping-pong buffers only for palette/expansion cases). Row unfiltering uses SSE2/SSE4.1 kernels on x86 (sub, avg, paeth; selected by runtime CPU detection with std) and NEON on aarch64 for sub and avg, with paeth there done by an unrolled scalar loop. It also skips work a careful decoder does: the dev decoder never verifies chunk CRC-32 or the zlib Adler-32, regardless of options.

## Compared with alternatives

Pick zune-png over image-png (Rust png crate) when you are in Rust and mostly decode 8-bit RGB(A) or interlaced images and can live without checksum verification; pick image-png for 16-bit and palette images. From C or C++, libspng (verifies checksums, native C API) or ptpng (1.6x-1.8x over libpng with zlib-ng) are the practical choices.

## Integration

| | |
|---|---|
| **Form** | crate (Rust); C access via zune-capi staticlib/dylib (zil_c) |
| **Dependencies** | zune-core and zune-inflate (workspace crates; zune-inflate pulls simd-adler32 for its zlib feature); no C dependencies |
| **Minimum toolchain** | Rust 1.87 (zune-png rust-version; workspace root needs 1.88) |
| **Platforms** | any Rust target; SIMD unfiltering on x86/x86-64 (SSE2/SSE4.1, runtime-detected with std) and aarch64 (NEON for sub/avg); no_std supported; issue #205 reports the workspace failing to build on i386 |
| **Thread safety** | not documented; each PngDecoder owns its state, and the PNG path decodes on one thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Checksum options are dead in the benchmarked code: dev-branch zune-png skips every chunk CRC ('png: Remove crc from the PNGChunk') and the streaming inflater never reads the Adler-32, so DecoderOptions::set_strict_mode(true) or png_set_confirm_crc(true) changes nothing for PNG. The released 0.5.2 still honors both options.
- decode_raw returns 16-bit samples big-endian; use decode() for native-endian u16, or png_set_strip_to_8bit to drop the low byte.
- The benchmark's MiB/s column is compressed input bytes per second (criterion Throughput::Bytes of the PNG file), not decoded pixels.
- Build with optimizations even in debug profiles (the README recommends [profile.dev.package.zune-png] opt-level = 3); the intrinsics paths are slow unoptimized.

## Known shortcomings

- Rust with a C API via crates/zune-capi (language-filter mismatch). Downgraded to C: benchmark-results.md compares against the Rust spng 0.1.0 binding (2021) over libspng 0.6.3 with stock zlib (zlib-ng off), its ARM NEON path commented out and chunk CRCs verified, while zune-png's default skips CRC and Adler-32; output layouts differ, outputs are not cross-checked, libpng is not measured, and the Darwin CPU is unnamed. One thread on all sides.
- The benchmarked decoder is the unreleased dev-branch streaming rewrite (May 2026): crates.io zune-png 0.5.2 (2026-03-11) is the older whole-buffer decoder and zune-inflate 0.2.54 (2023) has no StreamingDecoder, so no published crate matches the numbers. The dev decoder never checks CRC or Adler-32 (set_strict_mode and png_confirm_crc are no-ops), so it does less work than spng and image-rs/png; the MiB/s column counts compressed input bytes (retier-09 corrects the caveats). Open issues #221 (52 fuzz-crash panics since 2024-07) and #384 (OOM panic); NEON covers sub and avg filters only; C access only through the whole-library zune-capi; default maximum dimension 16384 px.

## Caveats and trade-offs

The measured code does different work from the baseline. Checksums: zune-png's default options skip both chunk CRC and zlib Adler-32 checks, image-rs/png is told to ignore both, but spng only ignores Adler-32 and keeps libspng's default CRC verification of critical chunks (crc_action_critical = SPNG_CRC_ERROR). Baseline build: the spng crate pinned is 0.1.0 from March 2021 with libspng 0.6.3 (current libspng is 0.7.x), linked to stock zlib through libz-sys with the zlib-ng option off, and its ARM NEON unfilter path is commented out in that libspng version, so on an Apple machine spng runs scalar filters on stock zlib inflate. Output layouts differ: spng's Format::Png returns native rows (palette indices with tRNS not applied, host-endian 16-bit samples), while zune-png and image-rs expand palettes to RGB(A) and keep 16-bit samples big-endian. libpng, the category incumbent, is not measured at all. Single results file, Apple hardware, no CPU model, criterion timings on the maintainer's own image set. In the same file zune-jpeg is slower than mozjpeg on most cases (1.1x-1.3x slower on baseline and subsampled decodes, about 1.0x-1.1x faster only on some progressive cases), zune-inflate is 1.5x-2.5x slower than libdeflate, and zune-qoi is 1.88x slower than rapid-qoi, so the claim holds only for PNG against this spng build, not for the zune family generally. The README only promises 'on par with or better than reference libraries'. Language is Rust; a C API exists in crates/zune-capi (library name zil_c, wrapping zune-image), so it sits outside the C++ language filter unless used through that C API. [retier] The benchmarked decoder is the unreleased dev-branch streaming rewrite (May 2026); crates.io zune-png 0.5.2 is the older whole-buffer decoder and no published crate matches the numbers. The dev decoder skips CRC and Adler-32 verification entirely (set_strict_mode and png_confirm_crc are no-ops), so it does less work than spng and image-rs/png. The spng side is libspng 0.6.3 (2021) on stock zlib; image-rs/png beats zune-png on 16 bpp and palette inputs. MiB/s counts compressed input bytes. Open issues #221 (52 fuzz-crash panics, since 2024-07) and #384 (OOM panic); NEON covers the sub and avg filters only; C access only through the whole-library zune-capi; default maximum dimension 16384 px.

Pure-Rust decoders with minimal unsafe (only SIMD intrinsics); C access only through the separate zune-capi crate, so it is not a drop-in libpng or spng replacement for C++ code. The workspace also contains zune-jpeg, zune-inflate, zune-qoi, zune-heif and image filters.

## Maintenance

Actively developed (default branch dev, 505 stars, PNG decoder rewritten May 2026, latest benchmark commit September 2026) under MIT, Apache-2.0 or Zlib, but the benchmarked decoder is not yet in a crates.io release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party criterion run of the public benchmarks/benches/decode_png.rs, summarized in benchmarks/benchmark-results.md (commit 0875e77, 2026-09-21) for an unnamed Darwin machine with no CPU model or compiler version, so C. Downgraded on the claim, not the tier: the spng side is a handicapped 2021 build doing different checksum work.
- **Verifier notes:** Numbers match the page; downgraded because the spng comparison is not like-for-like (old libspng 0.6.3 on stock zlib, CRC verified on spng only, NEON off). Please set language to 'Rust (C API via crates/zune-capi)' via decisions; language is not a correctable field here.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/etemesi254/zune-image/HEAD/benchmarks/benchmark-results.md>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/benchmarks/benchmark-results.md>
  - <https://github.com/etemesi254/zune-image/tree/dev/benchmarks>
  - <https://github.com/etemesi254/zune-image/tree/dev/benchmarks/benches>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/benchmarks/benches/decode_png.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/benchmarks/Cargo.toml>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/benchmarks/README.md>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/Cargo.toml>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-core/src/options/decoder.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/decoder.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/Cargo.toml>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-capi/Cargo.toml>
  - <https://github.com/etemesi254/zune-image>
  - <https://github.com/etemesi254/zune-image/commits/dev>
  - <https://github.com/etemesi254/zune-image/commits/dev/benchmarks/benchmark-results.md>
  - <https://crates.io/api/v1/crates/spng>
  - <https://crates.io/api/v1/crates/spng/0.1.0/dependencies>
  - <https://crates.io/api/v1/crates/spng-sys>
  - <https://raw.githubusercontent.com/aloucks/spng-rs/v0.1.0/spng/src/lib.rs>
  - <https://raw.githubusercontent.com/aloucks/spng-rs/v0.1.0/spng-sys/build.rs>
  - <https://raw.githubusercontent.com/aloucks/spng-rs/v0.1.0/spng-sys/Cargo.toml>
  - <https://github.com/aloucks/spng-rs/tree/v0.1.0/spng-sys>
  - <https://raw.githubusercontent.com/randy408/libspng/264476a1521bcb1d526c05ece0ed68b855fcfc4c/spng/spng.c>
  - <https://raw.githubusercontent.com/randy408/libspng/264476a1521bcb1d526c05ece0ed68b855fcfc4c/spng/spng.h>
- **Sources the enricher read:**
  - <https://github.com/etemesi254/zune-image>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/README.md>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/Cargo.toml>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/benchmarks/benchmark-results.md>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/benchmarks/benches/decode_png.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/benchmarks/Cargo.toml>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/benchmarks/README.md>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/Cargo.toml>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/README.md>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/decoder.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/lib.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/streaming.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/headers/readers.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/crc.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/filters.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/filters/de_filter.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/filters/neon.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/filters/sse4.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/apng.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/encoder.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/utils.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-png/src/options.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-core/src/options/decoder.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-inflate/README.md>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-inflate/Cargo.toml>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-inflate/src/streaming_decoder.rs>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-capi/Cargo.toml>
  - <https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-capi/README.md>
  - <https://github.com/etemesi254/zune-image/tree/dev/crates/zune-png/src>
  - <https://github.com/etemesi254/zune-image/tree/dev/crates/zune-inflate/src>
  - <https://github.com/etemesi254/zune-image/commits/dev/crates/zune-png>
  - <https://github.com/etemesi254/zune-image/issues?q=is%3Aissue+png>
  - <https://github.com/etemesi254/zune-image/issues/221>
  - <https://github.com/etemesi254/zune-image/issues/384>
  - <https://crates.io/api/v1/crates/zune-png>
  - <https://crates.io/api/v1/crates/zune-inflate>
  - <https://static.crates.io/crates/zune-png/zune-png-0.5.2.crate>
  - <https://static.crates.io/crates/zune-inflate/zune-inflate-0.2.54.crate>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/etemesi254/zune-image`) · [data/wave10/enrich/raw/github_com_etemesi254_zune_image.json](../../../data/wave10/enrich/raw/github_com_etemesi254_zune_image.json) (enrichment confidence 0.8)

</details>
