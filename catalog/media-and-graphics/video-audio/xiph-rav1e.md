# rav1e

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `BSD-2-Clause` · 🟢 active

> Rust AV1 encoder with dav1d-derived SIMD asm and a C API; its 'fastest' claim is unsupported: slower than libaom at equal quality.

| | |
|---|---|
| **Beats** | libaom (AV1 reference encoder) |
| **Claimed result** | README only: 'The fastest and safest AV1 encoder' and 'most suitable for cases where libaom (the reference encoder) is too slow'. No number in the README, doc/, CHANGELOG or releases. The available numbers contradict a like-for-like win. rav1e issue #2759 (maintainer shssoichiro, 2021-07-09): 'our speed 6 still trails aomenc's cpu-used 6 by about 30% BD-rate, while also being slower (assuming one tile and no parallel encoding)', and speed 0 comes closer 'at the cost of rav1e being 2700% slower'. In the independent master-of-zen/AV1-benchmarks 2020.08.05 run (dota2 clip, 8-bit, Av1an chunked encoding), aomenc cpu-used 6 against rav1e speed 0 gives VMAF BD-rate -1.571% with 87.311% less time. rav1e speed 6 ran about 1.7x faster than aomenc cpu-used 6 (mean 38.9 s vs 66.9 s) at about 16% higher VMAF BD-rate, and speed 10 ran about 3.0x faster at about 63% higher BD-rate (derived from page data). Its speed advantage is therefore lower-quality output, which is different work. |
| **Workload** | AV1 video encoding speed; the README positions rav1e for cases where libaom is too slow, with speed presets 0-10. |
| **Metric** | throughput |
| **Adoption** | 4.2k stars; widely referenced AV1 encoder (Xiph/Mozilla) |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/xiph/rav1e) · [benchmark](https://github.com/xiph/rav1e) |

## Verdict

The repository holds no speed number against libaom. Its only measured figure is an internal 11-13% gain from target-cpu builds, and benches/ has only criterion microbenchmarks of write_b, CDEF, CfL RDO, intra prediction and entropy coding at speed 10. The external evidence runs against the claim. Maintainer issue #2759 (2021) puts rav1e behind aomenc at matched presets. The independent master-of-zen 2020.08.05 Av1an run (xiph dota2 clip, 8-bit, git snapshots of each encoder, CPU model and flags unstated, chunked wall time) shows rav1e speed 6 at a mean 38.9 s against 66.9 s for aomenc cpu-used 6, but rav1e needs roughly 16% more bitrate for the same VMAF. Speed 10 is about 3x faster only with a BD-rate gap above 60% (derived from page data). Its speed lead therefore comes from doing less compression work.

## Use it when

- Rust codebases that need an AV1 or AVIF encoder without linking libaom: ravif, its largest crates.io dependent (20.7M downloads), builds on it, and rav1e itself has 49.7M downloads.
- Still-image AVIF encoding (still_picture mode), where per-frame encode speed matters less than a permissively licensed (BSD-2-Clause plus the AOM patent license) encoder written mostly in a memory-safe language.
- Chunked, many-process pipelines (Av1an style), where a fast preset that gives up compression is acceptable. In the independent 2020 Av1an run, speed 6 finished about 1.7x faster than aomenc cpu-used 6 but needed about 16% more bitrate for the same VMAF (derived from page data).
- C or C++ applications that want a small encoder API with string key/value configuration (rav1e_config_parse) and a pkg-config package.

## Skip it when

- When encode time at a given quality matters, which is the actual comparison with libaom. The maintainers' own issue #2759 (2021, still open) says speed 6 trails aomenc cpu-used 6 by about 30% BD-rate while also being slower single-tile, and that matching aomenc needs speed 0 at about 2700% more time. In the 2020 Av1an run, aomenc cpu-used 6 reached slightly better VMAF BD-rate (-1.571%) than rav1e speed 0 in 87.3% less time.
- Single-stream encodes on many cores with default settings: a 1080p encode uses one tile unless you pass --tiles or tile_cols/tile_rows, and frame-parallel encoding is missing (doc/QUALITY_&_SPEED_FEATURES.md). Parallel-GOP encoding exists only behind the unstable channel API, and issue #1831 ('Improve the multithread support') has been open since 2019.
- Low-latency or bitrate-capped live encoding through the C API: open issue #3416 reports packets far above a 200 kb/s target, 13 frames of delay with rdo_lookahead_frames=5, and no latency change from tiles or threads. It has no maintainer reply.
- When you need the 'safest' claim to hold in practice: much of the speed lives in hand-written assembly, issue #3469 (May 2026) asks for a private channel to report API soundness issues and has no public answer, and issue #3392 reports an illegal-instruction crash on Apple M1 with 0.7.1.
- Monochrome input (not supported, per the README) or development that expects regular releases: crates.io is still at 0.8.1 (2025-06-16), and the last weekly pre-release is p20250902.

## How it is fast

Speed comes mainly from presets 0-10 that prune rate-distortion search. The default, speed 6, drops RDO transform-type decision, uses the reduced transform set, disables full-search motion estimation and cuts temporal-RDO lookahead to 20 frames. Speed 7+ uses simple prediction modes, a single reference and fast deblocking; speed 8 turns off loop restoration; speeds 9-10 restrict partitions to 16x16-32x32 and then 32x32 only, with fast scene detection and no SATD subpel. Distortion is measured in the transform domain by default. The hot kernels are hand-written NASM imported from dav1d (motion compensation, inverse transforms, intra prediction, CDEF, loop filter, loop restoration, film grain; VideoLAN/Two Orioles headers), plus rav1e's own SAD, SATD, motion-search and CDEF-distortion asm, in SSE2 through AVX-512 (Ice Lake) versions picked at runtime by CPUID, and NEON on aarch64. Threads come from a rayon pool working across tiles; there is no frame-parallel encoding.

## Compared with alternatives

Against SVT-AV1, pick rav1e for a Rust-native crate, AVIF through ravif, or a small BSD-licensed C API, and pick SVT-AV1 when throughput at a given quality on many cores matters. rusty-av1-toolkit, a rav1e derivative, claims about 1.10x shorter encode time with byte-identical output in its default mode, so check it if you are tied to rav1e's bitstream. dav1d is a decoder and does not compete.

## Integration

| | |
|---|---|
| **Form** | crate (Rust library plus rav1e CLI); C static/shared library with header and pkg-config via cargo-c |
| **Dependencies** | NASM 2.14.02+ on x86_64 for the default asm feature (gas or clang assembler on aarch64); Rust crates including maybe-rayon, av-scenechange, v_frame, bitstream-io, av1-grain; cargo-c to build the C API |
| **Minimum toolchain** | Rust 1.85 (edition 2021), NASM 2.14.02 (CI uses 2.15.05) |
| **Platforms** | x86-64 (SSE2 baseline; SSSE3, SSE4.1, AVX2, AVX-512 and AVX-512 ICL asm chosen at runtime, RAV1E_CPU_TARGET overrides), aarch64 NEON, pure-Rust fallback elsewhere, wasm feature; no Windows arm64 release binaries (#3425), no RISC-V asm (#3402) |
| **Thread safety** | Not documented for concurrent calls on one Context. Internally it uses a rayon thread pool (threads=0 means all logical CPUs) shared by tile encoding and lookahead; the CLI help warns that more tiles may be needed to use the threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- The published 0.8.0 and 0.8.1 crates depend on av-scenechange with default features off and no 'asm' feature (checked on crates.io), so scene-change detection runs without its assembly. Commit b7bf390 (2025-09-21) says this was 'accidentally disabled' during the migration to that crate and re-enables it, but no release carries the fix yet; the slowdown has not been measured.
- The default is speed 6, not 0. The C API documentation lists rdo_lookahead_frames as default 40, but the speed-6 preset sets 20, so read the effective settings rather than the doc comment.
- Building with RUSTFLAGS='-C target-cpu=native' or x86-64-v3 is 11-13% faster per the README, but the binary then faults on CPUs that lack AVX2, BMI1/2, FMA, LZCNT or POPCNT. RAV1E_CPU_TARGET=rust disables all asm at runtime, which is useful for bisecting asm bugs.
- The README's 'weekly pre-release every Tuesday' is stale: master has commits through 2026-08-31, but the newest pre-release (p20250902) and crate (0.8.1) date from 2025.

## Known shortcomings

- No libaom number exists in the repo README, doc/, CHANGELOG or releases (benches/ holds internal kernel benchmarks only), so tier D. The project's own issue #2759 (2021) has speed 6 trailing aomenc cpu-used 6 by about 30% BD-rate while also slower single-tile, and speed 0 '2700% slower'. The independent master-of-zen/AV1-benchmarks (2020-08-05, Av1an runs) puts rav1e speed 6 about 1.7x faster than aomenc cpu-used 6 at about 16% worse BD-rate (derived from page data), so different work, with no CPU model, flags or versions. C API via cargo-c; AOM patent licence applies.
- Enricher (e125, 2026-10-05): D stands, the speed claim is contradicted (issue #2759; Av1an 2020 comparisons). New speed regression: crates.io 0.8.0, 0.8.1 and the p20250902 pre-release build av-scenechange without the 'asm' feature (verified in the crates.io dependency lists); the fix b7bf390 (2025-09-21) is on master only, unreleased. Default 1080p encoding uses one tile and no frame parallelism. Issue #3469 soundness report unanswered.

## Caveats and trade-offs

No speed number against libaom in the repo. Counter-evidence: (1) rav1e issue #2759 (2021) says that at speed 6 rav1e trails aomenc cpu-used 6 by about 30% BD-rate and is also slower single-tile, and that speed 0 is 2700% slower; doc/QUALITY_&_SPEED_FEATURES.md lists frame-parallel encoding as missing in rav1e but present in libaom. (2) In master-of-zen/AV1-benchmarks (2020.08.05 and 2020.05.06 folders; public Av1an scripts and raw data files), rav1e's faster presets beat aomenc wall time only at clearly worse compression; at equal quality aomenc cpu-used 6 is about 7.9x faster than rav1e speed 0 (derived from page data). That benchmark is from 2020 and names no CPU model (one folder says a 12-thread system), no build flags and only 'git' snapshots of each encoder. Since then libaom has added faster presets and rav1e has had little speed work, and SVT-AV1 is widely reported as faster than both. The 'fastest' claim is therefore unsupported. The README's only measured number is an internal 11-13% gain from building with target-cpu=native or x86-64-v3. The crate is Rust with large hand-written assembly; it provides a C API (library, header, pkg-config) via cargo-c, so it can be called from C/C++. Licensed BSD-2-Clause plus the Alliance for Open Media Patent License 1.0.

Written in Rust with hand-written x86_64 NASM and NEON assembly; needs NASM 2.14.02 or newer and Rust 1.85 or newer. A C API can be built (README section 'Building the C-API'), so it is callable from C++. 11 speed settings from exhaustive to near real-time.

## Maintenance

Maintenance mode: the last commits (2026-08-31) are an MSRV bump and a rand update, the last functional fix dates from Sep 2025, and crates.io is still at 0.8.1 (2025-06-16). It remains widely used (49.7M crates.io downloads, mostly through ravif), BSD-2-Clause with the AOM patent license, and easy to vendor as a crate or a cargo-c C library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification D, tier now D.
- **Tier reason:** The README, doc/ (QUALITY_&_SPEED_FEATURES.md is a feature checklist only), CHANGELOG and releases give no speed number against libaom, and benches/ holds only internal kernel microbenchmarks. The numbers that do exist do not support a like-for-like win: the maintainers' issue #2759 says rav1e is slower than aomenc at matched presets, and an independent Av1an-based comparison shows rav1e is faster only at much worse BD-rate. So the claim stays directional, and the evidence against it is stated.
- **Verifier notes:** Kept as a notable (4.2k stars), active, BSD-2-Clause AV1 encoder with a C API, but its speed claim against libaom is contradicted by the project's own issue #2759 and by independent 2020 Av1an runs; the documented shortcoming is 'not faster than libaom at equal quality'. Metadata checked on the github.com repo and commits pages: BSD-2-Clause, 4.2k stars, 293 forks, not archived, not a fork, last commit 2026-08-31 ('Update to rand v0.10'). WebSearch used 3 queries and found no peer-reviewed or reproducible tier A/B speed win.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** none (not faster)
- **Pages the verifier opened:**
  - <https://github.com/xiph/rav1e>
  - <https://github.com/xiph/rav1e/commits>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/README.md>
  - <https://github.com/xiph/rav1e/tree/master/doc>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/doc/QUALITY_%26_SPEED_FEATURES.md>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/doc/PROFILING.md>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/CHANGELOG.md>
  - <https://github.com/xiph/rav1e/tree/master/benches>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/benches/bench.rs>
  - <https://github.com/xiph/rav1e/releases>
  - <https://github.com/xiph/rav1e/wiki>
  - <https://github.com/xiph/rav1e/issues?q=is%3Aissue+libaom+speed>
  - <https://github.com/xiph/rav1e/issues/2759>
  - <https://github.com/xiph/rav1e/issues/3197>
  - <https://github.com/xiph/rav1e/issues/1248>
  - <https://github.com/master-of-zen/AV1-benchmarks>
  - <https://github.com/master-of-zen/AV1-benchmarks/tree/master/2020.08.05%20Aomenc%20SVT-AV1%20Rav1e>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.08.05%20Aomenc%20SVT-AV1%20Rav1e/README.md>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.08.05%20Aomenc%20SVT-AV1%20Rav1e/aom_data.txt>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.08.05%20Aomenc%20SVT-AV1%20Rav1e/rav1e_data.txt>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.08.05%20Aomenc%20SVT-AV1%20Rav1e/comparecodecs>
  - <https://github.com/master-of-zen/AV1-benchmarks/tree/master/2020.05.06%20AOM%20RAV1E%20X265>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.05.06%20AOM%20RAV1E%20X265/README.md>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.05.06%20AOM%20RAV1E%20X265/benchmark_aom.sh>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.05.06%20AOM%20RAV1E%20X265/benchmark_rav1e.sh>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.05.06%20AOM%20RAV1E%20X265/aom_git_nature.mkvdata.txt>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.05.06%20AOM%20RAV1E%20X265/rav1e_nature.mkvdata.txt>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.05.06%20AOM%20RAV1E%20X265/plot.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/README.md>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/build.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/doc/README.md>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/doc/QUALITY_%26_SPEED_FEATURES.md>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/api/config/speedsettings.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/api/config/encoder.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/api/config/mod.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/capi.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/cpu_features/x86.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/cpu_features/mod.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/encoder.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/tiling/tiler.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/bin/common.rs>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/benches/bench.rs>
  - <https://github.com/xiph/rav1e/tree/master/src/x86>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/x86/mc_avx2.asm>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/x86/satd.asm>
  - <https://raw.githubusercontent.com/xiph/rav1e/HEAD/src/x86/itx_avx512.asm>
  - <https://github.com/xiph/rav1e/commits/master>
  - <https://github.com/xiph/rav1e/commit/b7bf39066ec4f004c9b9cdb81c91734ec2edfac7>
  - <https://github.com/xiph/rav1e/releases>
  - <https://github.com/xiph/rav1e/issues?q=is%3Aissue%20is%3Aopen%20sort%3Aupdated-desc>
  - <https://github.com/xiph/rav1e/issues/2759>
  - <https://github.com/xiph/rav1e/issues/1831>
  - <https://github.com/xiph/rav1e/issues/3416>
  - <https://github.com/xiph/rav1e/issues/3469>
  - <https://github.com/xiph/rav1e/issues/3392>
  - <https://crates.io/api/v1/crates/rav1e>
  - <https://crates.io/api/v1/crates/rav1e/reverse_dependencies?per_page=10>
  - <https://crates.io/api/v1/crates/rav1e/0.8.1/dependencies>
  - <https://crates.io/api/v1/crates/rav1e/0.8.0/dependencies>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.08.05%20Aomenc%20SVT-AV1%20Rav1e/README.md>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.08.05%20Aomenc%20SVT-AV1%20Rav1e/comparecodecs>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.08.05%20Aomenc%20SVT-AV1%20Rav1e/rav1e_data.txt>
  - <https://raw.githubusercontent.com/master-of-zen/AV1-benchmarks/master/2020.08.05%20Aomenc%20SVT-AV1%20Rav1e/aom_data.txt>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/xiph/rav1e`) · [data/wave10/enrich/raw/github_com_xiph_rav1e.json](../../../data/wave10/enrich/raw/github_com_xiph_rav1e.json) (enrichment confidence 0.8)

</details>
