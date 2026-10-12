# QLIC (Quick Lossless Image Codec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Lossless image codec reaching JPEG XL effort-9 file sizes at about one-ninth of cjxl's single-thread encode time.

| | |
|---|---|
| **Beats** | JPEG XL lossless via stock cjxl (-d 0 -e 9 --num_threads=0) and WebP lossless via stock cwebp (-lossless -exact -z 6), per benchmark/run-large-matrix.ps1; the page also lists JPEG XL efforts 1-8, WebP presets 1-9 and an OxiPNG level 6 row. No PNG or QOI decoder is a baseline |
| **Claimed result** | Encode (one pinned logical processor, wall time including process startup and file I/O): QLIC 618.673 s vs JPEG XL lossless effort 9 5,674.173 s (about 9.2x faster, derived from page data) with a 0.30% smaller total (1,160,913,984 vs 1,164,424,898 bytes, per page). Against JPEG XL effort 5 (629.126 s, 1,230,084,951 bytes) encode time is about equal and QLIC output is 5.6% smaller (derived from page data). Against WebP lossless preset 6 (585.964 s) QLIC is about 5.6% slower but 9.97% smaller (page). OxiPNG level 6 took 9,105.634 s (about 14.7x slower than QLIC, derived from page data), but no public script runs OxiPNG. Decode (one untimed run, then the average of three pinned process runs per file, each including process startup and writing a PNG output): QLIC 236.927 s (8.291 MP/s) vs JPEG XL effort 9 files 307.602 s (6.386 MP/s, 29.83% slower per page, so QLIC about 1.30x faster, derived) but WebP preset 6 files 117.887 s (16.663 MP/s), about 2.0x faster than QLIC (derived from page data). |
| **Workload** | Lossless encode and decode of a 3,167-image corpus (1,964,362,720 pixels: DIV2K and CLIC 2022 validation, QOI benchmark categories, Enrico UI screenshots), one pinned logical processor, byte-exact roundtrip check on every file. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X3D, Windows 11, one pinned logical processor, encode order rotated |
| **Compiler and flags** | QLIC: published portable x86-64 build from Clang 22.1.4 (clang-cl), Release options from CMakeLists.txt: /O2 /Oi /Ot /Gy /Gw plus /clang:-O3, ThinLTO on the qlic target, codec/src/map_avx2.c compiled with /arch:AVX2; no -march=native, no PGO. Baselines: stock cjxl and cwebp binaries whose versions the current page does not state (the older docs/benchmark-0.5-historical.json names cwebp 1.6.0 and cjxl 0.12.0 with the same command lines); OxiPNG version and command line not stated |
| **Adoption** | 23 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/OzzyMitchell/QLIC) · [benchmark](https://github.com/OzzyMitchell/QLIC/blob/main/docs/benchmark-current.md) |

## Verdict

First-party run on a Ryzen 9 9950X3D under Windows 11, one pinned logical processor, wall time including process start and file I/O, 3,167 images (1.96 Gpx), byte-exact round trip on every file. The QLIC 1.0 portable Clang 22.1.4 build took 618.7 s for 1,160,913,984 bytes, against cjxl -d 0 -e 9 at 5,674.2 s for 1,164,424,898 bytes (about 9.2x faster and 0.30% smaller) and cwebp -lossless -z 6 at 586.0 s for 1,289,518,274 bytes. Decode took 236.9 s for QLIC, 307.6 s for djxl and 117.9 s for dwebp. Baseline versions are not on the current page (the 0.5 run used cjxl 0.12.0 and cwebp 1.6.0), and per-file rows stay in a private workspace.

## Use it when

- Archiving lossless images you would otherwise compress with cjxl -e 8 or -e 9, when single-thread encode CPU matters: similar total size for about 9x less encode time on the author's corpus.
- Mixed asset sets of UI screenshots, game textures, icons and structured graphics, where the author reports QLIC is often smaller than both JPEG XL and WebP.
- Closed pipelines where you control both ends (game assets, internal datasets, a desktop app) and can ship the C, Rust or Wasm decoder.
- Exact storage of 9-24-bit integer samples or PQ/HLG code values together with their metadata, without wrapping another image format.

## Skip it when

- Decode-latency-bound serving: WebP lossless decoded this corpus about 2x faster in wall time, and the architecture guide says QLIC's entropy decode is about 6.75x slower than WebP and 11.7x slower than WIC PNG.
- Interchange with browsers, operating systems or other tools: the format is not standardised and only QLIC's own WIC plugin and Wasm package read it.
- Fast encoding: about 3.2 MP/s single-threaded; JPEG XL efforts 1-4, WebP presets 1-6, fjxl or fpnge encode much faster at 10-33% larger output.
- Photographic and alpha-heavy content where JPEG XL e9 stays smaller, and corpora unlike the author's: on the wider 10,628-image qualification set QLIC's total is 0.45% larger than e9.
- Platforms outside Windows x64 and Linux x86-64 (untested), float/half HDR (unsupported), or needs for true streaming or cheap region decode (region decode still pays the full entropy decode).

## How it is fast

The encoder runs a bounded tournament instead of an exhaustive search. Cheap image facts (palette cardinality, block repetition, transform score, alpha shape) produce an early candidate and gate specialist representations such as palettes, filtered bytes with LZMS and horizontal bands; each specialist gets the current size as a cutoff, and the smallest completed file wins. The native QST1 stream applies reversible integer colour transforms, per-plane spatial prediction with predictor maps scored by AVX2 kernels, and adaptive binary range coding of residuals with context models (mode 52 is the main photographic path). Decode is a serial scalar range-decoding chain; the project's own architecture guide puts about 98% of hot decode time in plane entropy decoding.

## Compared with alternatives

Pick QLIC over HALIC or fNBLI when JPEG XL e9-level density matters more than raw speed and you want a maintained C library with Rust and Wasm decoders plus alpha, animation, wide-integer and metadata support. Pick libjxl fast_lossless, QOIR or fpnge when encode or decode throughput comes first and 15-30% larger files are acceptable.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (C17, CMake targets qlic::qlic_static and qlic::qlic, pkg-config) plus CLI; separate safe-Rust decoder crate and Wasm build |
| **Dependencies** | none for the codec core (LZMS is a bundled clean-room decoder); the CLI's input loaders use libpng, libwebp, libjxl, libavif and libtiff on Linux (libwim-dev also listed) and WIC on Windows |
| **Minimum toolchain** | C17, CMake 3.25+, Visual Studio 2022+ or Clang on Windows (published binary built with Clang 22.1.4), GCC or Clang on Ubuntu 24.04; Rust 1.85 for the Rust decoder |
| **Platforms** | Windows x64 and Linux x86-64 tested; portable x86-64 build with one AVX2 encoder-analysis source (map_avx2.c); wasm32 decoder; other architectures untested |
| **Thread safety** | sdk.md: separate threads can call the SDK at the same time; qlic_last_error is per thread. Encode and decode default to one thread, with opt-in workers for candidate trials and bands |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline size win is measured on the 3,167-image development corpus that the encoder's routes were built against; the architecture guide calls it 'a development gate, not a universal ranking'. On the wider 10,628-image qualification line QLIC totals 4,606,862,554 bytes vs JPEG XL e9 4,586,294,329 (0.45% larger, derived) and e8 4,607,544,830, while still encoding about 9x faster than e9.
- Decode figures are per-process wall time including start-up and writing a PNG. QLIC's CLI writes that PNG through the Windows WIC encoder at default settings, while djxl and dwebp use their own writers, so the published 1.30x lead over djxl is a whole-tool number and may not hold for in-process decode.
- QLIC 1.0.0 could write an invalid 32-byte file and report success for some large images with small, noisy palettes. Version 1.0.1 (2026-09-12) fixed it, so re-encode affected files and run qlic verify on stored archives.
- For untrusted files, set limits tighter than the 512 MiB / 67,108,864-pixel defaults and add an external time budget: the docs say limits cap allocation, not CPU time.

## Known shortcomings

- Borderline A: the public harness (benchmark/run-large-matrix.ps1) runs cjxl -e 9 and cwebp -z 6 on a single pinned core with ImageMagick checking pixels exactly (Clang 22.1.4, 9950X3D), but the current page names no baseline versions (the 0.5 record said cwebp 1.6.0 and cjxl 0.12.0), no script runs OxiPNG, decode times include process start-up and each tool's PNG writer, and WebP decodes about 2x faster than QLIC; the 9.2x win is against JPEG XL effort 9 while QLIC encodes at only 3.2 MP/s. Language is C, not C++. Weeks-old single-author repo.
- Enricher (e117, 2026-10-05): no correctness bug behind the totals (AE=0 on every file), but the headline uses the development corpus the encoder was built against; on the wider 10,628-image set in docs/architecture.md QLIC is 0.45% larger than JPEG XL effort 9, about level with effort 8, and still 8.99x faster to encode than effort 9. Decode is whole-process wall time including startup and PNG writing (QLIC writes PNG via WIC); the project's own docs put its core entropy decode 6.75x slower than WebP and 11.7x slower than WIC PNG, so the 1.30x lead over djxl is not a core-decoder ratio. Only QLIC, effort 9 and WebP z6 were re-timed in the final campaign. A is borderline but defensible for the encode matrix.

## Caveats and trade-offs

Single-author benchmark of a three-month-old project, Windows 11 only, one run. The 9.2x encode win is against JPEG XL effort 9, an extreme setting: at effort 5 encode time is similar and QLIC is 5.6% smaller, and JPEG XL efforts 1 to 4 and WebP presets 1 to 6 encode faster than QLIC but produce 10% to 33% larger output (derived from page data). QLIC encodes at only about 3.2 MP/s (derived), so it is a ratio-at-speed (Pareto) entry rather than a fast codec, and WebP decodes about 2x faster. Encode and decode wall times include process startup and file I/O; decode times also include each tool's own PNG writer for the output file, so the decode comparison partly measures three different PNG encoders. Baseline binary versions are not stated on the current page (the 0.5 historical record names cwebp 1.6.0 and cjxl 0.12.0); the OxiPNG row is not produced by any script in benchmark/; per-file results and the run summary.json are kept in a private development workspace, not in the repository. build.ps1 picks a Visual Studio generator without selecting clang-cl, so reproducing the Clang build needs a manual toolset choice. Release 1.0.1 (2026-09-12) fixed an encoder bug that could write an invalid 32-byte file for large palettes; the benchmark's exact-decode check would have stopped on such a file, so the published totals are not affected. Repository code is C (CMake project LANGUAGES C), not C++.

Lossless only. Not the decode winner: libwebp decodes this corpus about twice as fast, and encode time is close to WebP preset 6, not faster. Ships C/C++ SDK, CLI, Windows GUI and WIC plugin, a Rust decoder and a WebAssembly build; the Rust LZMS port keeps its MIT license. Very young project (first commit 2026-07-29, 1.0.0 on 2026-08-27).

## Maintenance

Active single-author project (first commit 2026-07-29, 1.0.1 on 2026-09-12, last commit 2026-10-02, 23 stars). The Apache-2.0 C library is vendorable, but the format is new and non-standard, so pin the decoder and keep a PNG or JPEG XL fallback.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmark-current.md numbers match the record; the encode matrix is produced by the public benchmark/run-large-matrix.ps1 (QLIC pack --threads 1, cjxl -d 0 -e 9 --num_threads=0, cwebp -lossless -exact -z 6, one pinned logical processor, rotated order, ImageMagick compare -metric AE must be 0 for every file), with JPEG XL efforts in run-jxl-efforts.ps1 and decode timing (one untimed run, then three pinned runs) in quick-benchmark.ps1; corpus pinned by URL, size and SHA-256 in downloads.json; compiler (Clang 22.1.4), Release flags (CMakeLists.txt) and CPU (Ryzen 9 9950X3D) are stated. Gaps noted in caveats: baseline binary versions are not on the current page, and the OxiPNG row has no public script.
- **Verifier notes:** Language should be C (CMakeLists.txt: project(qlic ... LANGUAGES C)); language is not a correctable field here, so the orchestrator may want an override. A is borderline: the harness, QLIC build flags, CPU and exact-pixel verification are public, but baseline tool versions for the current run are only implied by the older 0.5 record.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party campaign, public scripts
- **Pages the verifier opened:**
  - <https://github.com/OzzyMitchell/QLIC>
  - <https://github.com/OzzyMitchell/QLIC/commits>
  - <https://github.com/OzzyMitchell/QLIC/releases>
  - <https://github.com/OzzyMitchell/QLIC/tree/main/benchmark>
  - <https://github.com/OzzyMitchell/QLIC/tree/main/benchmark/tools>
  - <https://github.com/OzzyMitchell/QLIC/tree/main/docs>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/README.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/docs/benchmark-current.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/docs/benchmark-0.5-historical.json>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/run-large-matrix.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/run-jxl-efforts.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/quick-benchmark.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/summarize-results.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/downloads.json>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/corpus-summary.json>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/build.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/OzzyMitchell/QLIC>
  - <https://github.com/OzzyMitchell/QLIC/releases>
  - <https://github.com/OzzyMitchell/QLIC/issues>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/README.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/docs/benchmark-current.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/docs/benchmark-0.5-historical.json>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/docs/architecture.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/docs/format.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/docs/sdk.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/SUPPORT.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/gradient-topology-replay.md>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/run-large-matrix.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/run-jxl-efforts.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/quick-benchmark.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/benchmark/summarize-results.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/build.ps1>
  - <https://raw.githubusercontent.com/OzzyMitchell/QLIC/HEAD/codec/src/qlic.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ozzymitchell/qlic`) · [data/wave10/enrich/raw/github_com_ozzymitchell_qlic.json](../../../data/wave10/enrich/raw/github_com_ozzymitchell_qlic.json) (enrichment confidence 0.75)

</details>
