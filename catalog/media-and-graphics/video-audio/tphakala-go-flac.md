# go-flac

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Pure-Go (no cgo) FLAC encoder and decoder with AVX2/NEON kernels; encodes slightly faster than FFmpeg's flac, about 1.5x slower than libFLAC.

| | |
|---|---|
| **Beats** | FFmpeg native flac encoder (libavcodec); the same README table also measures libFLAC and SoX, and libFLAC is faster than go-flac |
| **Claimed result** | Input MB/s on the default input: amd64 (i7-1260P) go-flac 147 vs ffmpeg 128 (about 1.15x, derived from page data), libFLAC 229, SoX 194; arm64 (Cortex-A76) go-flac 51 vs ffmpeg 48 (about 1.06x, derived), libFLAC 76. Real-recording snapshot: 16-bit about 19 ms vs about 71 ms, 24-bit about 25 ms vs about 61 ms for ffmpeg flac (machine not stated). README: 'libFLAC's reference encoder remains about 1.5x faster'. |
| **Workload** | Encode at level 5, single-threaded, of a deterministic 30-minute mono 48 kHz/16-bit generated mix using scripts/bench-encoders.sh; plus a 2026-09-05 snapshot on real 48 kHz recordings at 16/24/32-bit. |
| **Metric** | throughput |
| **Hardware** | Intel i7-1260P (amd64) and Cortex-A76 (arm64); machine for the real-recording snapshot not stated |
| **Compiler and flags** | go-flac built with plain 'go build' (default flags; Go toolchain version not stated, go.mod declares go 1.27). Baselines run as 'ffmpeg -threads 1 -c:a flac -compression_level 5', 'flac -5 -f -s', 'sox -C 5'; their versions and builds are not stated. |
| **Adoption** | 2 stars |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/tphakala/go-flac) · [benchmark](https://raw.githubusercontent.com/tphakala/go-flac/HEAD/README.md) |

## Verdict

One first-party run per encoder of scripts/bench-encoders.sh (GNU time wall clock, process start-up included) on a generated 30-minute mono 48 kHz/16-bit sine-plus-white-noise file at level 5, single-threaded: go-flac 147 vs ffmpeg 128 MB/s on an i7-1260P (1.15x) and 51 vs 48 MB/s on a Cortex-A76 (1.06x, within single-run noise), with libFLAC 229 and 76 MB/s; Go, ffmpeg, flac and SoX versions and OS are not stated. The table was committed on 2026-06-05 (commit 12138c9) and not re-run on the 1.x code, the input is mono so the stereo-decorrelation path is never timed, 'MB/s' is actually MiB/s, and 'level 5' is not equal work: current FFmpeg flacenc.c uses 105 ms blocks (4608 samples at 48 kHz) and Rice partition orders 0-8 at level 5, against 4096 and 0-5 for go-flac and libFLAC, so libFLAC is the like-for-like peer and it is faster.

## Use it when

- Go services that write FLAC (recording, clip export, uploads) and want to drop an ffmpeg subprocess or cgo libFLAC; BirdNET-Go's release 20260713 notes say its built-in Go FLAC encoder is now the only FLAC path, with no FFmpeg dependency.
- Cross-compiled or static Go binaries on amd64, arm64 (Raspberry Pi class Cortex-A76 was benchmarked) or any other Go target, since there is no cgo.
- Many short streams: pool encoders or decoders with Reset to skip the 1-2 MB per-encoder setup the in-repo benchmark comments describe.
- 32-bit integer PCM that must stay lossless; the README reports ffmpeg's flac encoder truncating to 24-bit there (first-party snapshot, no harness).

## Skip it when

- Raw encode speed from C or C++: libFLAC's flac -5 is about 1.56x faster on the i7-1260P and 1.49x on the Cortex-A76 in the README's own table (derived from page data) at an identical ratio.
- Smallest files: levels 7 and 8 share parameters and lack libFLAC's subdivide_tukey apodization (code comment calls it future work), only a fixed 4096-sample block size and one window exist, and ffmpeg level 5 already produced slightly smaller output (0.8519 vs 0.8523) on the harness input.
- Callers outside Go: no C API or c-shared build is provided or documented.
- Projects that need a long track record: first commit June 2026, 2 stars, one maintainer; the ratio and throughput regression gate (issue #45) is still open.

## How it is fast

It follows libFLAC's level-5 recipe (fixed 4096-sample blocks, Tukey(0.5) window, autocorrelation, Levinson-Durbin with the order picked from the per-order prediction error, up to 8, 15-bit quantized coefficients, Rice partition orders 0-5, all four stereo assignments estimated) and ranks fixed vs LPC predictors by a cheap Rice-bit estimate, running the full partition search only on the winner whose residual is carried forward rather than recomputed. Hot loops (fixed and LPC residuals, Rice partition cost, stereo decorrelation, min/max) are Go-assembly AVX2/NEON kernels in internal/i32 with runtime dispatch and a bit-identical pure-Go fallback; float64 autocorrelation and CRC-16 come from the author's tphakala/simd module. Per-encoder scratch buffers keep steady-state per-block allocations near zero.

## Compared with alternatives

Pick go-flac when the program is in Go and must avoid cgo or an ffmpeg binary; in Rust, flacenc-rs or rusty_flac fill the same role, and from C or C++ libFLAC itself is the faster choice at the same compression. libfoxenflac is decode-only and HALAC is a different, non-FLAC format.

## Integration

| | |
|---|---|
| **Form** | Go module (github.com/tphakala/go-flac, packages flac and pcm) plus the cmd/wav2flac demo CLI |
| **Dependencies** | github.com/tphakala/simd v1.9.0 (CPU detection, float64 autocorrelation, CRC-16) and its transitive golang.org/x/sys; go.mod also lists github.com/quasilyte/go-ruleguard/dsl for the repo's lint rules |
| **Minimum toolchain** | Go 1.27 (go.mod, bumped 2026-09-08) |
| **Platforms** | any Go target; AVX2 kernels on amd64 and NEON kernels on arm64 (Go assembly, runtime dispatch); pure-Go fallback elsewhere |
| **Thread safety** | not documented; Encoder and Decoder are per-stream stateful objects that the docs show being pooled with sync.Pool, so use one per goroutine |
| **Drop-in for the baseline** | partial: it replaces 'ffmpeg -c:a flac' or libFLAC calls in Go programs with a different, Go-only io.Writer/io.Reader API; output is standard FLAC, cross-validated against libFLAC 'flac -d' and the IETF test corpus |

## Gotchas

- Config.CompressionLevel's zero value is level 0 (fixed predictors only), not libFLAC's default 5; set it explicitly.
- Pass an io.WriteSeeker (for example \*os.File): with a plain io.Writer the streaming encoder leaves STREAMINFO MD5 and frame-size fields as 'unknown' unless TotalSamples is declared or the one-shot EncodeInterleaved is used.
- MD5 hashing costs about 10-14% of encode and decode (issue #40); Config.SkipMD5 removes it but writes an all-zero MD5.
- Early versions wrote frame headers that iOS/macOS CoreAudio rejected (issue #4, sample rate and bit depth coded as 'from STREAMINFO'); fixed in July 2026, so pin a 1.x release.

## Known shortcomings

- Go library (language-filter mismatch). Public harness scripts/bench-encoders.sh (level 5, single thread, one run each) supports throughput only: 1.15x on amd64 and 1.06x on arm64 over ffmpeg's FLAC encoder; the README's 'beats ffmpeg on both throughput and ratio' is contradicted by its own table (0.8523 vs ffmpeg 0.8519). The 19 ms vs 71 ms snapshot has no harness or machine; Go version unstated.
- The ratio-win claim is wrong (0.8523 against 0.8519, lower is better); the table is from commit 12138c9 (2026-06-05) and was not rerun on 1.x; mono input only (stereo path untimed); 'MB/s' is really MiB/s. 'Level 5' is not equal work: FFmpeg flacenc level 5 uses 4608-sample blocks and Rice partition orders 0-8 against 4096 samples and 0-5 for go-flac and libFLAC; the like-for-like peer libFLAC is 1.56x and 1.49x faster. Used by BirdNET-Go (release 20260713) for its Go FLAC encoder.

## Caveats and trade-offs

First-party claim with a public harness (scripts/bench-encoders.sh). That harness supports only the throughput claim, and modestly: on the harness table go-flac is 1.15x (amd64) and 1.06x (arm64) faster than ffmpeg's flac encoder (derived from page data). libFLAC is about 1.5x faster than go-flac. Each encoder is timed once with GNU time, so the wall time includes process start-up and WAV parsing, and the arm64 margin is within run-to-run noise. All encoders run level 5, single-threaded, on the same file, so they do comparable work. The default input is a synthetic 440 Hz sine plus white-noise mono mix (ratio about 0.85), not music. The README contradicts itself on compression ratio. 'Audio quality' says go-flac 'encodes faster and slightly smaller than ffmpeg's FLAC'. The benchmark section says it 'matches libFLAC's compression ratio exactly and beats ffmpeg on both throughput and ratio on each architecture'. Yet the README's own harness table lists go-flac 0.8523 vs ffmpeg 0.8519 (and SoX 0.8519), so ffmpeg's output is smaller and the ratio claim is contradicted by the only harnessed data. 'Slightly smaller' rests only on the 16-bit row of the 2026-09-05 snapshot (0.45 vs 0.46; 24-bit equal at 0.64; 32-bit 0.51 vs 0.48 where ffmpeg truncates to 24-bit). That snapshot has no script in the repo, no stated machine, and the README calls it 'a small directional sample'; a corpus-based gate is still open as issue #45. Young repo (commits from July 2026).

Pure Go with no cgo, SIMD kernels (AVX2 on amd64, NEON on arm64) bit-identical to the scalar fallback. Stays bit-exact at 32-bit where the README says ffmpeg's FLAC encoder truncates to 24-bit. Go only, so C++ callers would need a c-shared build or a rewrite.

## Maintenance

Active (last commit 2026-09-08, version bumped to 1.1.0 on 2026-08-23, 2 open issues) and MIT-licensed with no third-party code beyond the author's own simd module, so it is copyable; the speed edge over ffmpeg is small and first-party.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers. The harness, scripts/bench-encoders.sh, is public and fixes level 5, single thread and a deterministic generated input, and CPU models (i7-1260P, Cortex-A76) are stated. The Go toolchain version, ffmpeg/flac/sox versions and builds, and OS are not stated, and each encoder is timed once, so it is not A. The 16/24/32-bit snapshot (about 19 ms vs about 71 ms) has no harness in the repo and no stated machine.
- **Verifier notes:** Confirmed at C. Of the two README statements, only the throughput claim is supported by a harness; the ratio-win claim is contradicted by the README's own table. Language Go is correct (already set in the record). Metadata checked: MIT, 2 stars, 1 fork, not a fork, last commit 2026-09-08, active.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tphakala/go-flac>
  - <https://github.com/tphakala/go-flac/commits>
  - <https://github.com/tphakala/go-flac/tree/main/scripts>
  - <https://github.com/tphakala/go-flac/issues/45>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/README.md>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/scripts/bench-encoders.sh>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/go.mod>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/flac_test.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/Taskfile.yml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/README.md>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/scripts/bench-encoders.sh>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/go.mod>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/Taskfile.yml>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/flac_test.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/THIRD_PARTY.md>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/cmd/wav2flac/main.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/pcm/doc.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/pcm/pcm.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/pcm/encoder.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/pcm/ratio_test.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/pcm/realistic_bench_test.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/pcm/encode_bench_test.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/internal/frame/params.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/internal/frame/subframe_encode.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/internal/frame/encode.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/internal/frame/decorrelate.go>
  - <https://raw.githubusercontent.com/tphakala/go-flac/HEAD/internal/lpc/analyze.go>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/flacenc.c>
  - <https://github.com/tphakala/go-flac>
  - <https://github.com/tphakala/go-flac/commits/main>
  - <https://github.com/tphakala/go-flac/commits/main/README.md>
  - <https://github.com/tphakala/go-flac/commit/12138c9>
  - <https://github.com/tphakala/go-flac/issues?q=is%3Aissue>
  - <https://github.com/tphakala/go-flac/issues/45>
  - <https://github.com/tphakala/go-flac/tree/main/pcm>
  - <https://github.com/tphakala/go-flac/tree/main/internal>
  - <https://github.com/tphakala/go-flac/tree/main/internal/frame>
  - <https://github.com/tphakala/go-flac/tree/main/internal/lpc>
  - <https://github.com/tphakala/go-flac/tree/main/internal/i32>
  - <https://github.com/tphakala/birdnet-go/releases>
  - <https://github.com/mycophonic/flac>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/tphakala/go-flac`) · [data/wave10/enrich/raw/github_com_tphakala_go_flac.json](../../../data/wave10/enrich/raw/github_com_tphakala_go_flac.json) (enrichment confidence 0.8)

</details>
