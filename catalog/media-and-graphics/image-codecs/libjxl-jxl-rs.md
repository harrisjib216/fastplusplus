# jxl-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Memory-safe pure-Rust JPEG XL decoder (Chrome, Firefox); roughly libjxl parity single-threaded, faster on lossless, slower on lossy VarDCT.

| | |
|---|---|
| **Beats** | libjxl (C++ JPEG XL reference decoder, djxl) |
| **Claimed result** | README: 'The performance of jxl-rs closely matches (and sometimes exceeds) the C++ reference implementation' (no numbers). PR #705 comment by hjanuschka (2026-03-15, repeated in issue #724), single-threaded, AMD EPYC 9645 (AVX-512), jxl-rs built with PGO, libjxl vs jxl-rs in MP/s: sunset_logo (modular) 6.31 vs 7.05 (1.12x), bike (VarDCT) 39.48 vs 36.69 (0.93x), green_queen_modular 8.99 vs 11.42 (1.27x), green_queen_vardct 35.83 vs 33.56 (0.94x), bicycles (modular+WP) 14.91 vs 12.05 (0.81x), delta_palette 10.60 vs 11.15 (1.05x), lz77_flower 3.52 vs 4.38 (1.24x), patches_lossless 13.81 vs 14.30 (1.04x), total 15.74 vs 16.35 MP/s (1.04x). Earlier draft PR #506 (2025-12-01) reported '30/39 conformance tests pass (2.23x avg vs C++)' and '6 tests faster than C++' (for example bike 226.15 ms Rust vs 163.10 ms C++). |
| **Workload** | Single-threaded decoding of 8 JPEG XL test images (sunset_logo, bike, green_queen modular and VarDCT, bicycles, delta_palette, lz77_flower, patches_lossless), throughput in MP/s, on the unmerged PR #705 branch; jxl_cli --speedtest measures jxl-rs alone and the libjxl command line and repetition count are not stated. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9645 (AVX-512), single-threaded |
| **Compiler and flags** | jxl-rs: PGO + AVX-512 per the PR #705 comments; repo release profile lto = "thin", panic = "abort"; rustc version, RUSTFLAGS and the libjxl build flags not stated. |
| **Adoption** | 712 stars; README says it is the JPEG XL decoder used in Google Chrome / Chromium and Mozilla Firefox |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/libjxl/jxl-rs) · [benchmark](https://github.com/libjxl/jxl-rs/pull/705#issuecomment-4063790496) |

## Verdict

One first-party single-threaded table from PR #705 (closed unmerged 2026-09-03; description targets libjxl 0.12, but libjxl's build, thread setting and repetitions are not stated) on an AMD EPYC 9645 with a PGO + AVX-512 jxl-rs build: 0.81x to 1.27x libjxl per image, with a 1.04x total that equals the geometric mean of the per-image ratios, while the arithmetic mean of MP/s gives 0.98x (derived from page data). The same PR's CI run on a GitHub x86-64 runner measured patches_lossless at 3.313 MP/s against 14.30 MP/s in the EPYC table, a 4.3x gap where the other seven images differ by 1.14x to 1.51x (derived from page data), so that row may not be the same file or setting; no number has been published for current main against libjxl.

## Use it when

- Rust services, browsers or tools that must decode untrusted JPEG XL input and want to avoid linking the C++ libjxl: the jxl crate denies unsafe code at its root and confines unsafe to SIMD and reviewed hot spots
- Lossless or modular JPEG XL images: in the PR #705 single-thread table jxl-rs was 1.04x to 1.27x libjxl on five of eight images (sunset_logo, green_queen_modular, delta_palette, lz77_flower, patches_lossless)
- Progressive or incremental display where lower memory use and partial rendering matter more than peak MP/s
- Targets libjxl is awkward to build for, such as wasm32 (simd128) or pure-Cargo builds, or projects already using the image crate (register_image_decoding_hook)

## Skip it when

- You need an encoder: jxl-rs only decodes (encoder support for the image integration is an open request, issue #959)
- Throughput-critical decoding of lossy VarDCT photos, the common web case: 0.93x and 0.94x libjxl in the PR #705 table, and the edge-preserving filter is called 'very slow' in open issue #950; a WebSearch snippet (page not opened) from the Chromium integration period cites 24-35% slower decode times than libjxl
- Weighted-predictor-heavy modular images such as bicycles (0.81x libjxl in the same table)
- C or C++ code bases that want a drop-in for libjxl's JxlDecoder C API; no C ABI crate ships in the workspace
- You need cropped decoding, LF-only (reduced resolution) decoding, some progressive modes or EXIF/XMP extraction: open issues #933, #857, #730 and #674

## How it is fast

SIMD kernels are written once against a SimdDescriptor trait and the simd_function! macro picks AVX-512F+BW, AVX2+FMA+F16C, SSE4.2 or scalar at runtime on x86-64 (NEON on aarch64, simd128 on wasm32). The March 2026 speed-up work re-landed from the closed PR #705 through PRs #707-#723 (tracked in issue #724) added bounds-check elimination, inlining changes, a faster BitReader, allocation removal and specialised modular predictor and MA-tree paths. Rows can be processed in parallel through the runner interface; jxl_cli drives it with a rayon pool.

## Compared with alternatives

No other JPEG XL decoder is catalogued: the libjxl fast_lossless (fjxl) entry is an encoder, so the two pair up (fjxl to write, jxl-rs to read in Rust); pick jxl-rs over the PNG/WebP/JPEG siblings (image-png, zune-png, wpd, zenjpeg) only when the format itself is JPEG XL.

## Integration

| | |
|---|---|
| **Form** | crate (jxl 0.7.4 on crates.io, plus jxl-image-rs-integration and the jxl_cli binary) |
| **Dependencies** | thiserror, byteorder, num-derive, num-traits, array-init and internal jxl_transforms/jxl_simd/jxl_macros; optional brotli-decompressor (brotli feature) and tracing; jxl_cli adds rayon |
| **Minimum toolchain** | Rust 1.89.0 (edition 2024) |
| **Platforms** | any Rust target with scalar fallback; runtime-dispatched SIMD on x86-64 (SSE4.2, AVX2+FMA+F16C, AVX-512F+BW), aarch64 NEON and wasm32 simd128 |
| **Thread safety** | Sharing one decoder across threads is not documented; parallel decode comes from an optional JxlParallelRunner passed to process/flush_pixels (jxl_cli uses a rayon pool), and the project runs Shuttle concurrency tests |
| **Drop-in for the baseline** | no |

## Gotchas

- The 1.04x total in PR #705 came from a PGO build on an AVX-512 EPYC 9645; the repository's release profile is only lto = "thin", panic = "abort", debug = true, so a plain cargo build is not that build
- -Ctarget-cpu=native halved modular decode speed in issue #803 (i5-12400, 14.757 to 7.895 MP/s, weighted predictor worst; closed), so test target-cpu flags before shipping them
- jxl_cli --speedtest uses all cores by default (--num-threads 0 means automatic); pass --num-threads 1 and a single-threaded djxl run to compare like for like
- The AVX-512 path the headline numbers ran on is not reliably exercised by CI: open issue #966 shows the 'avx512' job silently falls back to AVX2 on GitHub runners without AVX-512 (AMD EPYC 7763)

## Known shortcomings

- Raised D to C on the PR #705 comment (repeated in issue #724): single-threaded AMD EPYC 9645 AVX-512, PGO build, total 15.74 versus libjxl 16.35 MP/s (0.96x), VarDCT slower (0.93x, 0.94x), bicycles 0.81x; the PR was closed unmerged and the libjxl build is not stated. The older PR #506 measured 2.23x slower on average. Not faster than libjxl.
- PR #705's TOTAL 1.04x is a geometric mean of ratios; the arithmetic mean of MP/s gives 0.98x. patches_lossless shows 14.30 MP/s on the EPYC against 3.313 in the same PR's CI run (a 4.3x gap where other rows differ 1.14-1.51x), likely a different file or setting. PGO is not in the repo profile (#723 merged thin LTO only); #966 (AVX-512 path not reliably CI-tested) and #950 (EPF slow) open; a Chromium-era snippet puts jxl-rs 24-35% slower than libjxl.

## Caveats and trade-offs

Numbers are first-party (project collaborator hjanuschka) from PR #705, which maintainer veluca93 asked to split because it carried a lot of unsafe code and which was closed unmerged on 2026-09-03; its optimizations were re-landed through separate PRs tracked in issue #724, so current main may not reproduce the table. No public script measures libjxl and jxl-rs together: the CI benchmark (jxl-perfhistory in .github/workflows/pull_request.yml) compares a PR with its base only. jxl-rs is slower on the lossy VarDCT images that dominate web use (0.93x, 0.94x) and on bicycles (0.81x) and faster on modular/lossless images; the 1.04x total comes from a PGO build. Issue #803 (i5-12400, 2026-06-13) shows -Ctarget-cpu=native cutting a lossless modular decode from 14.757 to 7.895 MP/s, so build flags change results. A WebSearch snippet from a third-party article (page not opened, snippet only) says the Rust decoder 'performs within 15 to 25% of the C++ reference implementation's speed'. A separate WebSearch snippet about tirr-c/jxl-oxide (another Rust decoder) said djxl ran about 2.80x faster than jxl-oxide, so Rust decoders do not uniformly match libjxl.

Memory-safe Rust decoder (unsafe only for SIMD) developed inside the JPEG XL project; not yet an official reference implementation. Progressive rendering and lower memory use are stated advantages.

## Maintenance

Very active (commits to 2026-10-03, jxl 0.7.0-0.7.4 released in September 2026, 317k crates.io downloads) and BSD-3-Clause; shipped in Chrome and Firefox, but performance parity with libjxl rests on one first-party PGO measurement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D: the README has no numbers, but the project's own PR #705 (2026-03-15 comment, table repeated in issue #724) gives libjxl vs jxl-rs MP/s for 8 images measured single-threaded on an AMD EPYC 9645 (AVX-512); first-party, libjxl build and harness not stated, no public script runs both decoders, so C.
- **Verifier notes:** Orchestrator asked to confirm no number exists: numbers do exist in PR #705 and issue #724 (and older PR #506), so the entry moves from D to C with the CPU stated; parity overall, slower on VarDCT. Metadata (BSD-3-Clause, 712 stars, last commit 2026-10-03) checked and unchanged.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/libjxl/jxl-rs>
  - <https://github.com/libjxl/jxl-rs/commits/main>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/.github/workflows/pull_request.yml>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/.github/workflows/post_merge.yml>
  - <https://github.com/libjxl/jxl-rs/issues?q=is%3Aissue+benchmark>
  - <https://github.com/libjxl/jxl-rs/issues?q=djxl+performance>
  - <https://github.com/libjxl/jxl-rs/pull/705>
  - <https://github.com/libjxl/jxl-rs/issues/724>
  - <https://github.com/libjxl/jxl-rs/pull/506>
  - <https://github.com/libjxl/jxl-rs/issues/803>
  - <https://github.com/libjxl/jxl-rs/tree/main/tools>
  - <https://github.com/libjxl/jxl-rs/tree/main/ci>
  - <https://github.com/libjxl/jxl-rs/tree/main/.github/workflows>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/jxl/Cargo.toml>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/jxl/src/lib.rs>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/jxl/src/api/options.rs>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/jxl/src/api/decoder.rs>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/jxl_simd/Cargo.toml>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/jxl_simd/src/lib.rs>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/jxl_simd/src/x86_64/mod.rs>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/jxl_cli/Cargo.toml>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/jxl_cli/src/main.rs>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/libjxl/jxl-rs/HEAD/.github/workflows/pull_request.yml>
  - <https://github.com/libjxl/jxl-rs/pull/705>
  - <https://github.com/libjxl/jxl-rs/issues/724>
  - <https://github.com/libjxl/jxl-rs/pull/723>
  - <https://github.com/libjxl/jxl-rs/issues/803>
  - <https://github.com/libjxl/jxl-rs/issues/950>
  - <https://github.com/libjxl/jxl-rs/issues/966>
  - <https://github.com/libjxl/jxl-rs/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/libjxl/jxl-rs/issues?q=is%3Aissue+slower>
  - <https://github.com/libjxl/jxl-rs/pulls?q=is%3Apr+author%3Ahjanuschka>
  - <https://github.com/libjxl/bench>
  - <https://crates.io/api/v1/crates/jxl>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/libjxl/jxl-rs`) · [data/wave10/enrich/raw/github_com_libjxl_jxl_rs.json](../../../data/wave10/enrich/raw/github_com_libjxl_jxl_rs.json) (enrichment confidence 0.7)

</details>
