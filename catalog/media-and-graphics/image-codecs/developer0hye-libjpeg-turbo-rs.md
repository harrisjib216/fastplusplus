# libjpeg-turbo-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust port of libjpeg-turbo with AVX2/NEON kernels that decodes a few percent faster than C on x86_64 and encodes at about C speed.

| | |
|---|---|
| **Beats** | libjpeg-turbo 3.1.2 (decode) and 3.2.0 (encode) |
| **Claimed result** | README decode table, Intel i5-10400 vs C libjpeg-turbo 3.1.2: time ratios 0.77x (320x240 4:2:0), 0.87x (1280x720 4:2:0), 0.90x (1920x1080 4:2:0), 0.93x (2560x1440), 0.88x (3840x2160), but 1.23x (64x64) and 1.05x (640x480 4:2:0), i.e. about 3 to 23% faster on most sizes. Encode on Zen 3 and Zen 4 runners: stock build is 1.05 to 1.10x C 3.2.0's time at 1080p (slower); the target-cpu=native i5-10400 build is 2 to 7% faster than C 3.1.2. Apple M1 Pro: 0.99 to 1.07x of C. |
| **Workload** | JPEG decode (TurboJPEG-style decompress to RGB, quality 75) of in-repo fixtures tests/fixtures/photo_\*.jpg from 64x64 to 3840x2160 at 4:2:0, 4:2:2 and 4:4:4 (the 640x480 4:2:0 row is gradient_640x480.jpg), and encode of the same set at 320x240 to 1920x1080; Rust vs C in microseconds per image on Intel i5-10400, AMD EPYC 7763/9V74 runners and Apple M1 Pro. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-10400 @ 2.90GHz (turbo off); AMD EPYC 7763 (Zen 3) and Zen 4 GitHub runners; Apple M1 Pro |
| **Compiler and flags** | Decode table: stock cargo build --release (Cargo.toml [profile.release] lto = true), runtime AVX2/SSE2 dispatch; rustc version and the C libjpeg-turbo 3.1.2 build not stated. Encode portable table: rustc 1.98.1, no RUSTFLAGS, C harness compiled with cc -O2 against the official libjpeg-turbo 3.2.0 .deb (perf-portable-vs-native.yml). Supplementary i5-10400 encode table: RUSTFLAGS=-C target-cpu=native. |
| **Adoption** | 9 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/developer0hye/libjpeg-turbo-rs) · [benchmark](https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/README.md) |

## Verdict

Decode, first party: on an Intel i5-10400 (turbo off) a stock `cargo build --release` (fat LTO) decoded q75 fixtures in 0.87-0.97x of C libjpeg-turbo 3.1.2's time from 640x480 4:2:2 up to 3840x2160 and 0.77x at 320x240, but was slower at 64x64 (1.23x) and on the 640x480 gradient (1.05x). Both sides used the accurate integer IDCT and fancy upsampling (TurboJPEG FASTDCT=0, FASTUPSAMPLE=0; Rust defaults IsLow, merged upsampling off). The C loop reuses its output buffer while Rust's Criterion loop allocates one per decode. Encode is the only table with full methodology (rustc 1.98.1, official libjpeg-turbo 3.2.0 .deb, cc -O2 harness, AMD EPYC 7763), and there Rust is slower at 1.00-1.08x of C.

## Use it when

- Rust services that decode many photo JPEGs of 320x240 and up on x86_64 with AVX2: the repo's own runs put decode at 0.83-0.98x of C libjpeg-turbo's time on an i5-10400.
- You want libjpeg-turbo-identical output without a C toolchain: cross-compiling, wasm32 with SIMD128, or no_std + alloc firmware (thumbv7em is CI-built).
- Replacing zune-jpeg in `image`-crate pipelines: the README reports 31 wins and 3 losses out of 34 decode cases on aarch64 and 1.31x faster through the image bridge at 1080p.
- You need libjpeg features that lighter Rust decoders lack: progressive or arithmetic encode, lossless JPEG, 12/16-bit, DCT-coefficient access, lossless rotate/flip with marker copying.

## Skip it when

- C or C++ code that already links libjpeg-turbo: speed is at parity (M1 Pro decode 0.99-1.07x and encode 1.03-1.07x of C), and the C library is far more mature.
- Encode-heavy x86_64 work on a portable (distro-style) build: 1.00-1.08x of C 3.2.0's time on a Zen 3 runner and 1.09-1.10x on Zen 4 at 1080p. The float DCT path trails C by 1.4-1.9x (issue #600).
- Untrusted input where memory safety is the reason to choose Rust: the README makes no memory-safety guarantee while the unsafe SIMD boundary is audited, and issue #610 (open) is an out-of-bounds stack write reachable from safe Rust.
- Tiny images (64x64 decodes 1.23x slower than C; 16x16 cases lose on fixed cost) and 32-bit ARM or RISC-V Vector hardware, where there is no SIMD backend and the README estimates 2-5x (armv7) and roughly 1.5-4x decode (RVV) slower than C.
- As a system libjpeg.so.62 (v6b) or v7 replacement: the README says struct layouts differ and substitution corrupts memory; the v8 ABI is experimental.

## How it is fast

It reimplements libjpeg-turbo's pipeline (Huffman decode, accurate integer IDCT, fancy upsampling, colour conversion) with hand-written AVX2/SSE2 intrinsics chosen by runtime CPUID dispatch and NEON on aarch64. Its own fused kernels go beyond C's, such as an AVX2 fancy H2V2 upsampler that does the vertical and horizontal triangle filters in one pass over 16 samples and a fused FDCT, quantize, colour and downsample encode path. The Huffman encoder skips zero coefficients with a bitmap using TZCNT/BLSR/LZCNT (BMI1/LZCNT) and has a runtime-dispatched BMI2 tier. The release profile uses fat LTO for cross-module inlining.

## Compared with alternatives

It is a port of libjpeg-turbo, so for C/C++ the original stays the default. Pick this one when a Rust or C-toolchain-free build needs libjpeg-turbo's exact output and full feature set at roughly equal speed. Compared with zenjpeg (faster Rust decode with different upsampling defaults) or the jpeg-nitro parallel decoders, it trades peak decode speed for bit-exact libjpeg-turbo compatibility and a TurboJPEG C ABI.

## Integration

| | |
|---|---|
| **Form** | crate (plus cdylib C ABI shims: libturbojpeg.so.0 for TurboJPEG 3, experimental libjpeg.so.8) |
| **Dependencies** | thiserror; optional png crate behind the `png` feature; no C libraries |
| **Minimum toolchain** | Rust 1.87 (MSRV, CI-enforced); the image-bridge crate needs 1.88 |
| **Platforms** | x86_64 (AVX2/SSE2 runtime dispatch, Linux/macOS/Windows), aarch64 (NEON), wasm32 (SIMD128); scalar on RISC-V, POWER, s390x, armv7 and thumbv7em (no_std) |
| **Thread safety** | Decoder is Send (installed marker callbacks must be Send, issue #384 per a source comment); the C ABI threading contract is in docs/ABI_COMPATIBILITY.md (not read) |
| **Drop-in for the baseline** | partial: the TurboJPEG 3 C ABI shim is the primary replacement target and the libjpeg v8 ABI is experimental; v6b/v7 ABIs are explicit non-goals, and the README itself makes no unqualified drop-in claim |

## Gotchas

- Issue #610 (open, 2026-09-08): Encoder::scan_script accepts a spectral end Se &gt; 63. On x86_64 the SSE2 prepare_ac_first_sse2 path then writes about 272 bytes past two [u16; 64] stack arrays and returns Ok with corrupt output; aarch64 panics instead. Validate custom scan scripts yourself until it is fixed.
- The newest crates.io release is 0.8.0 (2026-07-28), but the README's performance tables and the runtime BMI2/FMA dispatch come from main in September 2026. Pin a git revision if you need the measured code. Compile-time -C target-feature=+bmi2,+fma binaries fault on CPUs without those features.
- The x86_64 decode table (i5-10400, C 3.1.2) does not state the rustc version or how the C library was built (the encode harness's build comment links a conda \$CONDA_PREFIX libjpeg). Its best case, 0.77x at 320x240, looks like a C-side outlier: C's time there is 13.0 ns per pixel vs 10.8-11.3 ns at 1280x720 4:2:0 and 640x480 4:2:2 (derived from page data), and the repo's 2026-04-12 report on the same CPU measured 1.00x for that case.
- The repo root carries committed benchmark binaries (bench_c_decode_matrix is a Mach-O arm64 build linked to Homebrew's libjpeg.8.dylib; bench_c_encode_linux is an x86-64 ELF). The C sides of the aarch64 tables used the classic libjpeg API, while the x86 decode harness (benches/c_baseline.c) used TurboJPEG tj3Decompress8.

## Known shortcomings

- Pure-Rust port of libjpeg-turbo (not an FFI wrapper), so a port of the category's incumbent; kept because libjpeg-turbo itself is a baseline, not a catalogued entry. README x86 decode 3-23% faster on most sizes (i5-10400, libjpeg-turbo 3.1.2) with rustc and the C build unstated; the portable encode build is slower (1.05-1.10x at 1080p), and only that table is fully specified (rustc 1.98.1, cc -O2, official 3.2.0 deb, EPYC 7763). Rust (language-filter mismatch).
- Settings are like-for-like (islow plus fancy upsampling on both sides; Rust allocates per decode), but the 320x240 0.77x best case looks like a C outlier (13.0 versus 10.8-11.3 ns per pixel, derived from page data; the same CPU's 2026-04-12 report gave 1.00x), so the realistic x86 decode win is about 2-17%. rustc and the C build are unstated for the decode table (the encode harness comment links a conda libjpeg). Open issue #610: Encoder::scan_script with Se above 63 writes out of bounds on the stack from safe Rust on x86_64. crates.io 0.8.0 (2026-07-28) predates the measured main; about 40k downloads with 9 stars. A port of the listed libjpeg-turbo (zlib-rs precedent would fold it; kept per the libjpeg-turbo-rs decision).

## Caveats and trade-offs

Pure-Rust reimplementation (port) of libjpeg-turbo, not an FFI binding: no C dependency, byte-for-byte cross-validated against C in CI. Under the ports rule it may fold into libjpeg-turbo (zlib-rs precedent); it is listed here because it is measured against the original. First-party harness, tiny project (9 stars); recent commits are co-authored by Claude. The x86_64 decode win (README table, i5-10400 turbo off, C 3.1.2) is 3 to 23% on most sizes but 64x64 (1.23x) and the 640x480 gradient (1.05x) lose; that table is undated and does not state rustc or the C build. An earlier report on the same CPU (experiments/x86_64_avx2_final_report.md, 2026-04-12) gives different absolute times but the same direction (0.83 to 0.98x on most cases, progressive 0.83 to 0.91x). The stock portable encoder is 1.05 to 1.10x C 3.2.0's time at 1080p on Zen 3/Zen 4 runners (slower); only the target-cpu=native i5-10400 build beats C 3.1.2 by 2 to 7%. Apple M1 Pro: decode 0.99 to 1.07x, encode 1.03 to 1.07x of C (not faster). README says no memory-safety guarantee yet (unsafe SIMD under audit) and the classic libjpeg ABI is experimental.

Pure-Rust port of libjpeg-turbo with NEON, AVX2, SSE2 and WASM SIMD128 kernels, byte-for-byte cross-validated against C in CI; ships C ABI shims (TurboJPEG 3 and libjpeg-compatible) so C++ can link it. MSRV 1.87. Lossless transforms and progressive supported.

## Maintenance

Very active (last commit 2026-09-22, 1,759 commits, most recent ones co-authored with Claude), 9 GitHub stars but about 40k crates.io downloads (38.5k in the last 90 days), MIT OR Apache-2.0. 44 open issues, mostly C-ABI parity and unsafe-audit items, so treat the C ABI shims as pre-1.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables compare against C libjpeg-turbo with public harnesses (benches/c_baseline.c for C decode via tj3Decompress8 with accurate DCT and fancy upsampling, benches/decode.rs, examples/bench_c_encode_linux.c and examples/bench_encode_matrix.rs). The decode table that carries the win (i5-10400, C 3.1.2) states neither rustc version nor how the C library was built, so it is C. Only the encode portable table, where Rust is slower, has full methodology (rustc 1.98.1, cc -O2 harness, official libjpeg-turbo 3.2.0 .deb, AMD EPYC 7763).
- **Verifier notes:** Numbers in claimed_speedup match the README tables. It is a Rust port, not a wrapper (README: 'no FFI to a C codec'), so the duplicate question is a policy call for the orchestrator. Rust entry under a C++-filtered category: language-filter mismatch.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/README.md>
  - <https://github.com/developer0hye/libjpeg-turbo-rs>
  - <https://github.com/developer0hye/libjpeg-turbo-rs/commits>
  - <https://github.com/developer0hye/libjpeg-turbo-rs/tree/main/benches>
  - <https://github.com/developer0hye/libjpeg-turbo-rs/tree/main/scripts>
  - <https://github.com/developer0hye/libjpeg-turbo-rs/issues/361>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/METHODOLOGY.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/benches/c_baseline.c>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/benches/compare.rs>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/benches/decode.rs>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/.github/workflows/perf-portable-vs-native.yml>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/experiments/portable_vs_native_x86_64_2026-09-08.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/experiments/x86_64_avx2_final_report.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/docs/ENCODING_PERFORMANCE.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/bench_c_decode_matrix>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/bench_c_encode_linux>
- **Sources the enricher read:**
  - <https://github.com/developer0hye/libjpeg-turbo-rs>
  - <https://github.com/developer0hye/libjpeg-turbo-rs/commits>
  - <https://github.com/developer0hye/libjpeg-turbo-rs/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/developer0hye/libjpeg-turbo-rs/issues/610>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/METHODOLOGY.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/benches/c_baseline.c>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/benches/decode.rs>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/benches/compare.rs>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/examples/bench_c_encode_linux.c>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/examples/bench_encode_matrix.rs>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/.github/workflows/perf-portable-vs-native.yml>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/experiments/x86_64_avx2_final_report.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/experiments/portable_vs_native_x86_64_2026-09-08.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/docs/ENCODING_PERFORMANCE.md>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/src/api/high_level.rs>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/src/decode/pipeline.rs>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/src/decode/pipeline_impl/api.rs>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/bench_c_decode_matrix>
  - <https://raw.githubusercontent.com/developer0hye/libjpeg-turbo-rs/HEAD/bench_c_encode_linux>
  - <https://crates.io/api/v1/crates/libjpeg-turbo-rs>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/developer0hye/libjpeg-turbo-rs`) · [data/wave10/enrich/raw/github_com_developer0hye_libjpeg_turbo_rs.json](../../../data/wave10/enrich/raw/github_com_developer0hye_libjpeg_turbo_rs.json) (enrichment confidence 0.75)

</details>
