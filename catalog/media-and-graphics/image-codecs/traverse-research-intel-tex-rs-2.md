# intel-tex-rs-2 (intel_tex_2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust bindings over a maintained fork of Intel's ISPC texture compressor; BC6H/BC7/ETC1 encode 2-6x faster than Intel's kernels on Apple Silicon.

| | |
|---|---|
| **Beats** | Intel's upstream ISPCTextureCompressor (ispc_texcomp) kernels as vendored on the crate's main branch (GameTechDev submodule, built with ISPC 1.20), plus the same upstream kernels rebuilt with ISPC 1.31 (PR #49 column) to isolate the compiler change; all through the same Rust binding and criterion harness, not a separately built Intel ispc_texcomp library |
| **Claimed result** | PR #50 (merged 2026-09-28 into the stacked branch ispc-1.31, not main), Apple M5 Max, 1 thread, criterion, 256x256: BC7 2.10-6.18x vs main (ISPC 1.20) and 1.99-6.08x vs PR #49 (same upstream kernels on ISPC 1.31), e.g. bc7_opaque/basic 51.07 ms (main) / 49.37 ms (#49) to 20.14 ms (2.54x / 2.45x), bc7_alpha/basic 68.44 / 68.21 ms to 13.18 ms (5.19x / 5.18x), bc7_alpha/slow 249.50 / 245.50 ms to 40.39 ms (6.18x / 6.08x), bc7_opaque/ultra_fast 0.81 / 0.76 ms to 0.38 ms (2.10x / 1.99x); BC6H 1.84-3.10x vs main (bc6h/fast 6.36 ms to 2.05 ms); ETC1 61.88 / 60.40 ms to 10.21 ms (6.06x / 5.91x); BC1-BC5 unchanged (0.94-1.06x). Full 4096x4096 example texture, single thread, best of 2 runs: all presets 255.64 s to 108.69 s (2.35x), bc7_opaque/basic 13.39 s to 5.25 s (2.55x), etc1 16.32 s to 2.86 s (5.71x). Follow-up PR #51 (merged into arm64-perf): bc7e-style partition ranking, opaque presets 0.95-1.73x on 24 Kodak images and 1.00-1.75x on the 4K texture vs the post-#50 state, with presets retuned at equal or higher PSNR; its text says bc7e is slower on the 4K texture on the same machine (veryfast 2.38 s vs 1.05 s at 51.27 dB, 2.3x; basic 8.84 s vs 5.21 s, 1.7x; derived from page data). |
| **Workload** | Single-threaded block encode of a 256x256 procedural 'natural' test image (tests/common/mod.rs, seeded RNG) for every BC6H and BC7 preset (criterion, sample size 10), plus BC1-BC5 and ETC1 slow at 64, 256 and 1024 px; separately a full 4096x4096 photo (examples/lambertian.jpg) across all presets, best of 2 runs, with no runner in the repository. |
| **Metric** | latency |
| **Hardware** | Apple M5 Max (ARM64 NEON), 1 thread; x86, Windows, Linux and Android binaries were regenerated but not benchmarked |
| **Compiler and flags** | ISPC 1.31 (LLVM 23) for the PR #49 and PR #50 columns, ISPC 1.20 for main. build.rs (ispc feature): ISPC opt_level(2); aarch64 target neon-i32x8 with CPU pinned to apple-a14 on macOS (x86 targets SSE2, SSE4, AVX1, AVX2, AVX512SKX-x16); the kernel libraries are prebuilt and checked into src/ispc, which is what the bench links. Rust release profile lto = true, opt-level = 3, codegen-units = 1 (Cargo.toml). Harness benches/compress.rs with criterion 0.8 (tests-and-benches and arm64-perf branches, open PR #48). rustc version not stated. |
| **Adoption** | 17 stars, 3 forks; crates.io intel_tex_2 0.5.0 (2025-07-02), 680,756 downloads total, 169,928 recent (crates.io API, 2026-10-04) |
| **Last commit** | 2026-07-01 |
| **Links** | [repository](https://github.com/Traverse-Research/intel-tex-rs-2) · [benchmark](https://github.com/Traverse-Research/intel-tex-rs-2/pull/50) |

## Verdict

Criterion (benches/compress.rs on the tests-and-benches and arm64-perf branches), Apple M5 Max, 1 thread, synthetic 256x256 'natural' image, kernels prebuilt with ISPC opt_level 2 and neon-i32x8. The cleanest baseline is the PR #49 column: Intel's unmodified kernels rebuilt with the same ISPC 1.31 and apple-a14 pin. Against it, PR #50 is 1.99-6.08x faster on BC7 (opaque basic 49.37 to 20.14 ms) and 5.91x on ETC1 (60.40 to 10.21 ms); BC1-BC5 are unchanged. Quality matches, checked with independent decoders (texture2ddecoder, bcdec_rs): BC7 within 0.0001 dB. The 'main' column (ISPC 1.20, built on CI via Rosetta without CPU pinning, and with the NaN-prone ETC1 kernel) overstates the ratios slightly. The 4K and bc7e numbers have no runner in the repo.

## Use it when

- Offline or build-time texture baking on Apple Silicon (or other aarch64) that needs BC7, BC6H or ETC1 at ispc_texcomp quality in a fraction of the time.
- Rust asset pipelines already on intel_tex_2 that want the speedup without changing calling code.
- One dependency covering desktop BCn (including HDR BC6H from half-float RGBA) and mobile ETC1, with prebuilt kernels so neither ISPC nor libclang is needed at build time.
- Pipelines that parallelize by splitting the image into horizontal strips on threads: each call is single-threaded over caller-owned buffers, and the repo's own threaded_strips benchmark does exactly this.
- C/C++ projects that today vendor Intel's ispc_texcomp: the Traverse-Research kernel fork is the drop-in upgrade with the same entry points.

## Skip it when

- You need the speedup from a crates.io release: 0.5.0 (2025-07-02, latest as of 2026-10-05) ships Intel's old kernels. The faster code sits on the arm64-perf branch behind open PR #48 (opened 2026-09-24), so you must use a git dependency.
- x86-64 is your main build host: only an Apple M5 Max was benchmarked. The PR says removing gathers 'matters less on AVX2/AVX-512', so the x86 gain is unmeasured and may be much smaller.
- Real-time or very high-volume ETC1/BC1 encoding: etcpak, Goofy or Basis Universal's etc1f/bc7f trade quality for far higher throughput.
- Byte-reproducible output against Intel's ispc_texcomp, for example asset caches keyed on encoder output: ETC1 tie-breaking changed (about 10% of blocks differ), PR #51 retuned BC7 presets under the same names, and BC6H moved slightly with the ISPC version.
- ASTC: the README lists it as pending, and the PR #48 tests mark ASTC compression unimplemented.

## How it is fast

The fork's 27 kernel commits remove per-lane gathers from the BC6H/BC7 hot loops. NEON has no gather, so each gather had become 8 scalar loads; the fork computes unquantization weights arithmetically and picks subsets with vector selects. It also inlines every helper, hoists per-subset setup out of the pixel loop, shares PCA work between modes 1/3 and 4/5, and skips the RGB-only modes 0-3 on blocks with alpha. ETC1 builds its 165-candidate list once per (flip, half) instead of 8 times, scores candidates with prefix sums and sorting networks, and uses exact integer lower bounds to skip candidates and tables that cannot win (branch and bound). PR #51 adds bc7e-style bounding-box partition ranking for modes 0-3.

## Compared with alternatives

Against bc7e (catalogued, B): pick this for one Rust dependency covering BC6H, ETC1 and BC1-BC5 as well as BC7. On Apple Silicon, PR #51's first-party numbers have it beating bc7e on a 4K texture (very_fast 1.05 s vs 2.38 s at 51.27 dB), but on x86 bc7e's independent lead over ispc_texcomp has not been re-checked against this fork. Against etcpak, Goofy and Basis Universal etc1f/bc7f: pick this when quality matters more than raw throughput.

## Integration

| | |
|---|---|
| **Form** | crate (static ISPC kernel libraries prebuilt and checked into src/ispc; the kernel fork is also usable from C/C++) |
| **Dependencies** | ispc_rt 2; ISPC 1.31 + libclang + cc only with --features ispc to regenerate kernels |
| **Minimum toolchain** | Rust 2021 edition; rust-version not declared (library code uses usize::div_ceil, stable since Rust 1.73); ISPC 1.31 (LLVM 23) to rebuild kernels |
| **Platforms** | x86/x86-64 (ISPC multi-target SSE2, SSE4, AVX1, AVX2, AVX-512 SKX); aarch64 NEON (neon-i32x8; macOS pinned to apple-a14, so M1 or later; iOS apple-a7); prebuilt for macOS, iOS, Linux, Windows, Android; only Apple M5 Max benchmarked |
| **Thread safety** | Not documented. Each call is a pure single-threaded kernel over caller buffers with no visible global state; the repo's threaded_strips benchmark runs concurrent calls on disjoint strips. |
| **Drop-in for the baseline** | partial: same API and entry points as Intel's ispc_texcomp kernels and intel_tex_2 0.5.0, but output bytes differ for ETC1 and the retuned BC7 presets, and the code is unreleased (git branch only) |

## Gotchas

- Widths that are not a multiple of 4 give a skewed block layout. The kernels' store_data advances output rows by width\*block_words bytes, not by (width/4) blocks, and edge blocks are dropped. calc_output_size sizes the buffer from the texel count, not a padded block grid. The bug is inherited from Intel and recorded as an ignored test (unaligned_width_encodes_full_blocks). Pad images to multiples of 4 yourself.
- BC6H encodes unsigned half floats, so negative inputs decode as 65504.0 instead of 0.0. This is a known bug, also recorded as an ignored test (bc6h_negative_values_clamp_to_zero); clamp HDR input to non-negative values before encoding.
- Intel's upstream ETC1 kernel, which crates.io 0.5.0 still ships, reads uninitialized colors[q][7..10] for empty clusters; the resulting NaNs can abort encoding. The fork fixes it in commit 6ddb057, which on its own is a reason to switch.
- bc7_alpha speedups (5.2-6.2x) come from a test image whose alpha varies in every block, where skipping the RGB-only modes pays off most. On a fully opaque 4K texture the PR reports about 2.3x for the alpha presets.

## Known shortcomings

- The Criterion harness (benches/compress.rs) lives only on the tests-and-benches and arm64-perf branches (open PR #48), not on main or in the crates.io 0.5.0 release of 2025-07-02; measured on one thread of an Apple M5 Max (ISPC 1.31 against 1.20, build.rs opt_level 2, neon-i32x8, apple-a14) against the unmodified Intel upstream kernels, with x86 unmeasured, the rustc version unstated, and the 4K and bc7e numbers lacking a runner.
- Enricher (e123, 2026-10-05): no bug behind the fork numbers; output quality was checked with independent decoders. The 'main' column is confounded (ISPC 1.20, a Rosetta CI build, no CPU pin, and the ETC1 kernel reads uninitialised colors[q][7..10]); the clean baseline is the PR #49 column (same upstream kernels on ISPC 1.31): BC7 1.99-6.08x, ETC1 5.91x. Tier A holds when the #49 ratios are cited. Gotchas: a width not a multiple of 4 skews the block layout (store_data; an ignored test); BC6H decodes negative input as 65504.0; crates.io 0.5.0 still ships the old kernels; bc7_alpha's 5-6x is on a synthetic all-alpha image, about 2.3x on opaque.

## Caveats and trade-offs

Unreleased and not on main: PRs #49, #50 and #51 were merged into a stack of branches (#49 into tests-and-benches, #50 into ispc-1.31, #51 into arm64-perf) that waits on open PR #48 into main; main's last commit is 2026-07-01 and crates.io 0.5.0 (2025-07-02) has the old kernels. The kernel changes live in the fork Traverse-Research/ISPCTextureCompressor (ISPC, C-callable; MIT, Intel copyright), which is the code a C++ user would take; this crate is its Rust binding. Only Apple Silicon was measured; the PR says x86, Windows, Linux and Android binaries were regenerated but not benchmarked, and much of the gain comes from removing per-lane gathers that NEON lacks, which 'matters less on AVX2/AVX-512', so the x86 gain over Intel's kernels is unknown and could be small. The 256x256 presets run on one synthetic image; the 4K numbers (best of 2) and the bc7e comparison in PR #51 have no runner in the repo, and bc7e's ISPC build for NEON is not described. ETC1 output is not bit-identical (last 4 commits change tie-breaking, +0.0010 dB measured against PR #49 because main's ETC1 aborts on an uninitialized-memory bug); BC6H moved -0.0004 to +0.0027 dB, mostly from the ISPC version change. PR #51 retunes the BC7 presets while keeping their names, so post-#51 presets do different work than upstream presets of the same name (PSNR equal or higher). PR text was read through a page summarizer on several fetches that agreed on every quoted row and whose ratios recompute from the times; treat per-row values as quoted. Dual MIT or Apache-2.0; vendored kernels MIT.

Rust bindings over prebuilt ISPC kernels (ISPC and libclang only needed with --features ispc to regenerate; binaries for macOS, iOS, Android, Linux and Windows are committed in the repo). Speedups came from removing per-lane gathers (NEON has no gather), inlining helpers, hoisting subset work and sharing work between modes, which also made fully inlined kernels much slower to compile (generate-binaries CI jobs went from about 2/3/4 minutes to 17/23/45 minutes on macOS/Linux/Windows). Quality: PSNR change within 0.0001 dB for BC1, BC3 and BC7, worst single image -0.006 dB (BC6H); ETC1 final commits changed tie-breaking so about 10% of blocks differ with equal or better PSNR. Kernels derive from the discontinued Intel ISPCTextureCompressor, now vendored from Traverse Research's fork. ASTC is listed as pending in the README.

## Maintenance

Actively developed by Traverse Research (MIT OR Apache-2.0, kernels MIT); the speedups were merged 2026-09-28 into a stacked branch chain waiting on open PR #48, and the kernel commits are AI-co-authored, so pin a commit and keep the round-trip quality tests on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the criterion harness that produced PR #50's 256x256 table is public at benches/compress.rs on the tests-and-benches and arm64-perf branches (open PR #48; bench_presets, synthetic 256x256 'natural' image, 1 thread), the ISPC flags are in build.rs (opt_level 2, neon-i32x8, CPU pinned to apple-a14, prebuilt kernels checked in), the compiler is stated (ISPC 1.31 on LLVM 23, ISPC 1.20 for the main column) and the CPU is an Apple M5 Max. The baseline is Intel's unmodified upstream ISPCTextureCompressor kernels run through the same binding and harness, and the PR #49 column holds the compiler fixed, so this is a fork-against-upstream comparison with output quality matched (BC7 PSNR within 0.0001 dB), not a self-comparison of the project's own earlier code; the 4K table and the bc7e comparison have no public runner and are C-level.
- **Verifier notes:** The orchestrator's 'no Criterion harness found' does not hold: benches/compress.rs exists on the non-default branches tests-and-benches and arm64-perf (open PR #48 into main), so I upgraded to A for the 256x256 Apple M5 Max table; if the orchestrator treats an unmerged branch harness or the missing rustc version as disqualifying, C is the fallback. Cross-reference for bc7e (listed, B): on ARM the improved Intel kernels beat bc7e per PR #51 (first-party, no harness). Language stays Rust for the binding, but the kernels are ISPC in Traverse-Research/ISPCTextureCompressor.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `last_commit`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party criterion runs (PR #50)
- **Pages the verifier opened:**
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/50>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/50/commits>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/49>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/51>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/48>
  - <https://github.com/Traverse-Research/intel-tex-rs-2>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/commits/main>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/branches>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pulls>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pulls?q=is%3Apr+is%3Amerged>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/tree/main/examples>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/HEAD/README.md>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/HEAD/examples/main.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/tests-and-benches/Cargo.toml>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/tests-and-benches/benches/compress.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/benches/compress.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/build.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/tests/common/mod.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/.gitmodules>
  - <https://github.com/Traverse-Research/ISPCTextureCompressor>
  - <https://github.com/Traverse-Research/ISPCTextureCompressor/tree/master/test>
  - <https://raw.githubusercontent.com/Traverse-Research/ISPCTextureCompressor/HEAD/readme.md>
  - <https://crates.io/api/v1/crates/intel_tex_2>
- **Sources the enricher read:**
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/50>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/49>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/51>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/48>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/tree/arm64-perf>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/tree/arm64-perf/tests>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/benches/compress.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/build.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/tests/common/mod.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/tests/api.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/tests/formats.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/tests/quality.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/Cargo.toml>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/src/lib.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/src/bc7.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/src/etc1.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/src/bc1.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/README.md>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/arm64-perf/.gitmodules>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/main/build.rs>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/main/Cargo.toml>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/main/README.md>
  - <https://raw.githubusercontent.com/Traverse-Research/intel-tex-rs-2/main/.gitmodules>
  - <https://github.com/Traverse-Research/ISPCTextureCompressor/commits/master>
  - <https://raw.githubusercontent.com/Traverse-Research/ISPCTextureCompressor/d80d4a7af5f63940f479bc0ebe6469cdb32150cc/ispc_texcomp/kernel.ispc>
  - <https://raw.githubusercontent.com/GameTechDev/ISPCTextureCompressor/master/ispc_texcomp/kernel.ispc>
  - <https://crates.io/api/v1/crates/intel_tex_2>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/traverse-research/intel-tex-rs-2`) · [data/wave10/enrich/raw/github_com_traverse_research_intel_tex_rs_2.json](../../../data/wave10/enrich/raw/github_com_traverse_research_intel_tex_rs_2.json) (enrichment confidence 0.75)

</details>
