# honeydiff (vizzly-testing)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Rust` · `MIT` · 🟢 active

> Closed-source Rust image-diff engine for Node (CIEDE2000, AA suppression, SSIM/GMSD); no current benchmark against odiff or pixelmatch.

| | |
|---|---|
| **Beats** | none compared (candidates odiff and pixelmatch) |
| **Claimed result** | No comparison against odiff, pixelmatch or any other library. Own timings only: Vizzly screenshot default \~2.81ms, strict/no-AA \~2.18ms, tall screenshot default \~147ms, tall strict/no-AA \~4.34ms, 1080p isolated SSIM \~14.7ms, GMSD \~10.9ms. CHANGELOG has self-comparisons only (SSIM 5x faster than the previous release, 239ms to 51ms at 1920x1080). |
| **Workload** | README 'Performance' snapshots from local benchmark runs on its own Vizzly screenshot fixtures (default and strict/no-AA comparison, tall screenshot) and isolated 1080p SSIM and GMSD; no other library timed. |
| **Metric** | latency |
| **Adoption** | 14 stars, 0 forks, 19 commits (release-tag commits only); npm @vizzly-testing/honeydiff 0.17.0 |
| **Last commit** | 2026-09-06 |
| **Links** | [repository](https://github.com/vizzly-testing/honeydiff) · [benchmark](https://github.com/vizzly-testing/honeydiff) |

## Verdict

There is no current cross-library measurement: the README lists only Honeydiff's own core timings (Vizzly screenshot \~2.81 ms default and \~2.18 ms strict, 18.3 MP tall screenshot \~147 ms default and \~4.34 ms strict, 1080p SSIM \~14.7 ms, GMSD \~10.9 ms) with no hardware stated, though CHANGELOG 0.11.1 names local Criterion runs on Apple Silicon. The only head-to-head the author published (README of 2026-05-19, v0.10.3, end-to-end CLI on the tall fixture) has odiff 4.2.1 at \~0.41 s against Honeydiff's \~1.27 s default and \~0.42 s exact mode.

## Use it when

- Node.js 22+ visual-regression pipelines (browser or app screenshots) that need a perceptual CIEDE2000 tolerance and anti-aliasing suppression rather than a raw pixel count.
- Diff triage tooling that wants region bounds, Delta E statistics, SSIM/MS-SSIM/GMSD and diff fingerprints from one call, for example to group the same header change across many pages.
- Full-page screenshots whose height changed by one inserted or removed block (alignHeightChanges: true keeps later changes visible).
- Strict gates on very tall screenshots with threshold 0, antialiasing false and minimumRegionPixels 1: the author reports \~4.34 ms core time for an 18.3 MP (750x24,412) fixture versus \~147 ms in default mode.
- Teams that also want WCAG contrast screening and CVD simulation from the same native package.

## Skip it when

- When end-to-end speed is the goal: the author's own README of 2026-05-19 (v0.10.3) measured odiff 4.2.1 at \~0.41 s against Honeydiff default \~1.27 s and exact/no-AA \~0.42 s on the tall fixture, so odiff was about 3.1x faster than the default mode (derived from page data).
- When you need the engine source, a Rust crate, a C/C++ or Python API, or to build it yourself: the engine lives in a private repo (package.json points to vizzly-testing/r-honeydiff, 404), nothing is on crates.io or PyPI, and the MIT licence covers only the JS loader you can see.
- On Intel macOS, musl/Alpine Linux or Node older than 22: prebuilt binaries exist only for macOS ARM64, Linux glibc x64/ARM64 and Windows x64, and the loader throws on anything else.
- Where API stability matters: pre-1.0 with breaking changes in 0.4.0 (ESM only), 0.5.0 (YIQ options replaced by CIEDE2000), 0.11.0 (SSIM/MS-SSIM/GMSD values changed) and 0.16.0 (include flags and result fields removed).
- Content with large anti-aliased or gradient areas in default mode: the AA path is \~34x the exact path on the tall fixture (147 vs 4.34 ms), and CHANGELOG 0.11.1 says synthetic full-surface gradient stress cases got slower after the stricter AA checks.

## How it is fast

The engine source is not public, so this comes from the CHANGELOG and symbol names in the shipped Linux x64 binary: rows are scanned in parallel on a rayon pool (compare_work collects per-row ScanSummary/RowDeltas), pixels with identical RGB skip the Lab conversion, and exact/no-AA count-only comparisons scan raw RGB rows directly (0.11.1). CIEDE2000 is computed in f64 through an sRGB-to-linear lookup table, regions are labelled with a union-find over row spans, SSIM uses a separable Gaussian blur in f64 with a direct path for small images, GMSD runs on 2x-downsampled luma, and height shifts are matched by row checksums. The x86-64 binary has no AVX instructions in its honeydiff_core functions (SSE2 only), so the speed comes from threads and short-circuits, not wide SIMD.

## Compared with alternatives

Pick it over odiff when you need Delta E thresholds, anti-aliasing suppression, region statistics or SSIM/GMSD inside Node and can accept a closed engine; pick odiff (open source, with a published hyperfine comparison against ImageMagick and pixelmatch) when raw end-to-end speed or a standalone CLI matters, since Honeydiff's own README measured odiff about 3x faster than its default mode. imgdiff is obsolete.

## Integration

| | |
|---|---|
| **Form** | shared lib (npm package with prebuilt Node native addons built with Neon 1.1.1; no Rust crate, C API or source) |
| **Dependencies** | none at runtime (package.json has no dependencies); the binaries statically include image 0.25.10 with default features (png 0.18.1, zune-jpeg, image-webp, tiff, exr, gif, rav1e/ravif), rayon 1.12 and neon 1.1.1 |
| **Minimum toolchain** | Node.js 22+ (engines &gt;=22.0.0, ESM-only since 0.4.0); binaries report rustc 1.98.1; cannot be built from the public repo |
| **Platforms** | macOS ARM64, Linux x64 and ARM64 (glibc builds only), Windows x64; no Intel macOS or musl binaries |
| **Thread safety** | Async APIs run as Neon tasks; all work shares one process-wide rayon pool sized by HONEYDIFF_THREADS or configureThreads(), which throws if the size is changed after work starts; concurrent-call guarantees otherwise not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Withdrawn odiff claim: until 2026-05-19 the README said '6x faster than odiff (79ms vs 474ms)' on a 750x24,162 screenshot (Apple M-series). Commit 4021bb5 removed it, stated that the Honeydiff table is core time on preloaded images without PNG decode, process startup or file output, and reported end-to-end CLI runs on the tall fixture where odiff 4.2.1 (\~0.41 s) beat Honeydiff default (\~1.27 s) and matched exact/no-AA (\~0.42 s). The 6x figure therefore appears to have set Honeydiff core time against an end-to-end odiff run; do not cite it.
- No harness, hardware or fixtures are published (benchmarks/BENCHMARK_RESULTS.md and docs/REFERENCES.md return 404) and the README table changes every release: after the 0.11 metric-correctness change Full HD default went from \~18.9 to \~31.6 ms and 4K from \~77.7 to \~131 ms (v0.10.3 vs v0.11.1 READMEs), and by v0.15.0 those synthetic rows were replaced with the Vizzly and tall-screenshot fixtures. Core time excludes PNG decode, which dominates real runs (tall fixture exact: \~4.9 ms core vs \~0.42 s CLI).
- The suppression logic has had false-negative bugs, the dangerous kind for regression tests: AA detection hid flat full-surface colour regressions (fixed 0.11.0) and thin border or divider recolouring (fixed 0.12.0), capped early-exit comparisons could report false identity (fixed 0.12.0, early exit removed in 0.16.0), and the 0.8.1 SSIM skip returned 1.0 when only AA-filtered pixels differed. The 0.8.1 '5x faster SSIM' (239 to 51 ms at 1920x1080) used integral images, i.e. a box window, before 0.11.0 switched to the Gaussian-weighted SSIM of the paper. Pin versions and re-baseline after upgrades.
- Packaging: the 0.17.0 tarball is 14.7 MB (36 MB unpacked) with all four platform binaries; the Linux x64 .node is unstripped with debug info (10.3 MB) and carries an AVIF encoder (rav1e) and EXR/TIFF/GIF codecs from the image crate's default features; the x86-64 build uses SSE2 only.

## Known shortcomings

- No baseline comparison anywhere; the repo is binary-only (no Rust source, Cargo.toml and r-honeydiff 404) and benchmarks/BENCHMARK_RESULTS.md is 404; the changelog has self-comparisons only and its 0.8.1 SSIM figures predate the 0.11.0 correctness change. Kept at D under the keep-and-document rule, reference (has_code false), 14 stars.
- Enricher: the README claimed '6x faster than odiff (79 ms vs 474 ms)' until commit 4021bb5 (2026-05-19) removed it; the replacement text says Honeydiff times are core-only (preloaded images, no PNG decode or startup), and the author's own end-to-end CLI run on the tall fixture gives odiff 4.2.1 about 0.41 s against Honeydiff default about 1.27 s and exact/no-AA about 0.42 s, so odiff was about 3.1x faster than the default mode (derived from page data) and the 6x claim is withdrawn. README rows change every release (after the 0.11 metric change Full HD went 18.9 to 31.6 ms and 4K 77.7 to 131 ms; gone by v0.15.0), the benchmark doc and docs/REFERENCES.md are 404, and there is no harness or hardware for the current table. AA suppression had false-negative bugs (fixed 0.11.0/0.12.0) and capped early-exit comparisons could report false identity (fixed 0.12.0). The shipped npm 0.17.0 binary (rustc 1.98.1, rayon, image 0.25.10 default features) is SSE2-only on x86-64 with no AVX; the engine repo is private.

## Caveats and trade-offs

The public repo holds only the JS loader (index.js, load-platform.cjs), type definitions, examples, assets and release metadata; the Rust engine source is not here (README's Development section says cargo build --release, but Cargo.toml and src/ return 404, and package.json's repository field points to vizzly-testing/r-honeydiff, which returns 404), so the MIT licence cannot be exercised on the engine code. README links benchmarks/BENCHMARK_RESULTS.md, which also returns 404. The 'current local benchmark snapshots' state no hardware, flags or harness; the CHANGELOG has self-comparisons only (0.8.1: SSIM 239 ms to 51 ms at 1920x1080, 35 ms to 8.3 ms at 640x480; 0.11.1: Criterion runs 'on Apple Silicon', tall screenshot \~192 ms default and \~4.1 ms exact/no-AA), and the 0.8.1 SSIM figures predate the 0.11.0 metric correctness change that made SSIM Gaussian-weighted and slowed the hot paths. No comparison against odiff, pixelmatch or any other diff tool; web searches in the earlier pass found no third-party honeydiff benchmark. Low notability (14 stars).

Node.js 22+ package with prebuilt native binaries (macOS ARM64, Linux x64/ARM64, Windows x64); CIEDE2000 perceptual threshold, anti-aliasing suppression, region clustering, SSIM/MS-SSIM/GMSD, WCAG contrast and CVD simulation. It is a richer feature set than pixel-count diffing, so it is not a like-for-like comparison with odiff or pixelmatch.

## Maintenance

Actively released (0.17.0 on 2026-09-06, single maintainer, release-tag commits only) but reference-only: the public repo is a JS loader plus binaries, the Rust engine is private, and the author's own May 2026 end-to-end run shows odiff faster, so the earlier '6x faster than odiff' README claim should be treated as withdrawn.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The README Performance table lists only honeydiff's own timings (2.81, 2.18, 147, 4.34, 14.7, 10.9 ms, matching the record) with no other library timed, no harness in the repo, and the linked benchmarks/BENCHMARK_RESULTS.md returns 404; with no baseline comparison anywhere, D is the right tier.
- **Verifier notes:** Kept at D per the keep-and-document rule (no baseline comparison, not notable, binary-only repo); nothing is invalid or fabricated. Shortcomings to record: no source in the public repo, no baseline, benchmark doc 404, 14 stars.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** any comparison against odiff or pixelmatch; end-to-end comparison against odiff with a public harness
- **Pages the verifier opened:**
  - <https://github.com/vizzly-testing/honeydiff>
  - <https://github.com/vizzly-testing/honeydiff/commits>
  - <https://github.com/vizzly-testing/r-honeydiff>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/README.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/package.json>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/benchmarks/BENCHMARK_RESULTS.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/Cargo.toml>
  - <https://registry.npmjs.org/@vizzly-testing/honeydiff/latest>
- **Sources the enricher read:**
  - <https://github.com/vizzly-testing/honeydiff>
  - <https://github.com/vizzly-testing/honeydiff/commits>
  - <https://github.com/vizzly-testing/honeydiff/commits/main>
  - <https://github.com/vizzly-testing/honeydiff/commits/main/README.md>
  - <https://github.com/vizzly-testing/honeydiff/commit/4021bb54a1660810b411fd8659693b89a47fc9ee>
  - <https://github.com/vizzly-testing/honeydiff/commit/4021bb54a1660810b411fd8659693b89a47fc9ee.diff>
  - <https://github.com/vizzly-testing/honeydiff/tree/main/examples>
  - <https://github.com/vizzly-testing/honeydiff/issues?q=is%3Aissue>
  - <https://github.com/vizzly-testing/honeydiff/issues/1>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/README.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/package.json>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/index.js>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/load-platform.cjs>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/index.d.ts>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/examples/basic.js>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/docs/REFERENCES.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/benchmarks/BENCHMARK_RESULTS.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/HEAD/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/965605b4543d5f1077c17ad9f9bc429def07ed15/README.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/82fe382c635170a29428a49bfcb913a15b76ba51/README.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/9894cb6fa36eed6830418148e87939fbf77409e3/README.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/9590401a672c159979422c6929d0c0251dfa7d05/README.md>
  - <https://raw.githubusercontent.com/vizzly-testing/honeydiff/a392cfd343c76a7d1282da95633a2462cc0e6478/README.md>
  - <https://registry.npmjs.org/@vizzly-testing%2fhoneydiff>
  - <https://registry.npmjs.org/@vizzly-testing/honeydiff/-/honeydiff-0.17.0.tgz>
  - <https://crates.io/api/v1/crates/honeydiff>
  - <https://crates.io/api/v1/crates/honeydiff-core>
  - <https://pypi.org/pypi/honeydiff/json>
  - <https://github.com/teimurjan/blazediff>
  - WebSearch: honeydiff vizzly image diff odiff benchmark
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/vizzly-testing/honeydiff`) · [data/wave10/enrich/raw/github_com_vizzly_testing_honeydiff.json](../../../data/wave10/enrich/raw/github_com_vizzly_testing_honeydiff.json) (enrichment confidence 0.6)

</details>
