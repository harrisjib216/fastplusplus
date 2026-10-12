# flacenc-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Pure-Rust embeddable FLAC encoder library and CLI; its multithreaded mode outruns single-threaded flac 1.4.3 at near -8 compression.

| | |
|---|---|
| **Beats** | FLAC reference encoder: flac 1.4.3 command-line tool (-f -8, -f -8 --lax, -f -5), single-threaded (1.4.3 predates flac's -j threading) |
| **Claimed result** | Nightly report (simd-nightly): flacenc st 331.5x and mt1 353.1x real time vs flac -8 229.7x (st 1.44x faster, derived from page data) but vs flac -5 550.4x (st 0.60x, derived from page data); default with 8 worker threads 1309.5x (5.7x flac -8 and 2.38x flac -5, derived from page data) against single-threaded flac. Average compression rate (output/input, lower is better): flacenc 0.5276 vs flac -8 0.5256 (flacenc output about 0.4% larger, derived from page data) and flac -5 0.5328. Stable report (default build from crates.io without simd-nightly): st 126.5x, mt1 131.2x, default 575.3x vs flac -8 230.9x and -5 572.1x, so single-thread stable is 0.55x of flac -8 and the 8-thread default only matches flac -5 (derived from page data). |
| **Workload** | Integration report from pytools/reporter.py: CLI against CLI (flacenc-bin vs the flac 1.4.3 binary), one wall-clock run (time.time around subprocess) per file and setting, including process start-up, WAV read and FLAC write; four Wikimedia recordings; reference settings opt8lax/opt8/opt5 and flacenc configs default (multithread, workers = logical cores = 8 on this VM), mt1 (multithread, 1 worker), st (single thread) and experimental (direct-MSE LPC); every flacenc output is decoded with flac -d and compared byte-for-byte with the input. |
| **Metric** | throughput |
| **Hardware** | GCP c2-standard-8 VM (asia-northeast1-a): Intel Xeon @ 3.10GHz, family 6 model 85 stepping 7 (Cascade Lake, AVX-512), 4 cores / 8 threads, Debian 12, kernel 6.6.122 (report/system_info.md, 2026-05-22) |
| **Compiler and flags** | flacenc-bin: rustc 1.95.0 stable and 1.97.0-nightly (2026-05-21) per report/system_info.md; release profile lto = fat, codegen-units 1, panic abort; .cargo/config.toml target-cpu=native; mimalloc, par, decode, experimental features; nightly report adds simd-nightly (portable_simd), stable report uses the fake portable_simd. flac 1.4.3 built with ./configure && make (configure.ac prepends -O3 -funroll-loops for GCC; no -march) inside a rust:1-slim-bookworm container with Debian build-essential; the C compiler version is not logged. |
| **Adoption** | 41 stars, 11 forks; crates.io flacenc 0.5.1, about 703k downloads (177k recent) |
| **Last commit** | 2026-06-29 |
| **Links** | [repository](https://github.com/yotarok/flacenc-rs) · [benchmark](https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/report.nightly.md) |

## Verdict

The repository's own report (pytools/reporter.py: one wall-clock CLI run per file and setting on four Wikimedia recordings, start-up and file I/O included, on a GCP c2-standard-8 Xeon Cascade Lake VM, 4 cores/8 threads) gives nightly flacenc 331.5x real time single-threaded and 1309.5x with 8 workers against flac 1.4.3 (generic ./configure build, single-threaded) at 229.7x for -8 and 550.4x for -5, with output 0.4% larger than -8; the stable build reaches 126.5x and 575.3x. Every flacenc output was decoded with flac -d and matched the input byte for byte, so the numbers are for lossless streams, but no configuration is both faster and at least as small as a tested flac setting at equal thread count.

## Use it when

- A Rust program that must emit FLAC without linking the C libFLAC: pure Rust, Apache-2.0, default dependencies are small (crc, md-5, heapless, crossbeam-channel).
- Batch encoding of long recordings on a multi-core machine where wall-clock throughput matters: the 8-thread default measured 1309.5x real time vs 229.7x for single-threaded flac 1.4.3 -8 on a 4-core/8-thread Cascade Lake VM (nightly build).
- Codec research or tuning: you want to inspect or post-process frames, subframes and residuals, change LPC order, window or stereo modes through a TOML config, or try direct-MSE LPC (`experimental` feature).
- A nightly toolchain is acceptable: with `simd-nightly` one thread is 1.44x the speed of flac -8 at files about 0.4% larger (derived from page data).

## Skip it when

- Stable Rust only: the single-thread build runs at 0.55x of flac -8 and 0.22x of flac -5 (126.5x vs 230.9x and 572.1x real time), and the 8-thread default only ties single-threaded flac -5 (575.3x vs 572.1x), derived from page data.
- You want the best ratio or a like-for-like multithreaded comparison: there are no -0..-8 levels, the default ratio (0.5276) sits between flac -8 (0.5256) and -5 (0.5328), block size is fixed, and flac 1.5.0 (February 2025) added multithreaded encoding in libFLAC and the flac CLI, which the reports do not test; an HN result snippet (thread not opened) cites flac -j16 at 5.47x its single-thread speed on 8 cores/16 threads.
- 24-bit material with abrupt noise-to-silence transitions: open issue #256 (flacenc 0.5.1) reports a 4096-sample 24-bit mono block encoding to about 3.08 GB instead of about 12 KB and overflowing STREAMINFO's 24-bit max_frame_size so decoders reject the file, and open PR #259 describes a u32 lane wrap in the Rice bit-count table at 24-bit signal-to-silence transitions; neither fix is merged.
- Streaming or low-memory encoding: `encode_with_fixed_block_size` returns the whole encoded `Stream` and the CLI writes the file only after encoding finishes; a streaming API is still open issue #91.
- 32-bit PCM (open issue #226) or non-WAV input to the CLI.

## How it is fast

It runs the standard FLAC search (constant, fixed and LPC subframes; left-side, right-side and mid-side stereo; partitioned Rice parameter choice) with a deliberately light default: LPC order 10 from one Tukey(0.4)-windowed autocorrelation and a Levinson recursion in f64, 15-bit coefficient quantization, and fixed-predictor order picked by an approximate-entropy estimate over 32 partitions instead of trial encoding. flac -8 searches more (max LPC order 12 with subdivide_tukey(3) windows). The windowed autocorrelation, residual computation and Rice bit-count table are written against std::simd (portable_simd); on stable a scalar `fakesimd` shim stands in, which is why the stable single-thread build is about 2.6x slower (126.5x vs 331.5x real time, derived from page data). In `par` mode the main thread reads and deinterleaves blocks into a pool of frame buffers, N worker threads encode frames independently over crossbeam channels, a separate thread updates MD5, and the frames are reassembled in order.

## Compared with alternatives

Against rusty_flac (pure Rust, measured single-core against FFmpeg 8.1.2's native flac encoder rather than libFLAC) and go-flac (Go, slower than libFLAC in its own table), pick flacenc-rs for a Rust library with serializable frame components, configurable search and built-in multithreading that has been on crates.io since 2022 (about 703k downloads). HALAC compresses and runs faster but is not FLAC, and libfoxenflac only decodes.

## Integration

| | |
|---|---|
| **Form** | crate (`flacenc` on crates.io) plus the `flacenc-bin` CLI crate |
| **Dependencies** | crc, heapless, md-5, num-traits, rustversion, seq-macro; optional crossbeam-channel (`par`, default on), log and serde (default on), nom (`decode`), nalgebra (`experimental`), mimalloc |
| **Minimum toolchain** | Rust 1.83 (MSRV, scalar fake SIMD); the `simd-nightly` feature needs nightly portable_simd, and crates.io 0.5.1 with it no longer builds on current nightly (issue #260; fixed on unreleased main by #249) |
| **Platforms** | any Rust target (portable code, no hand-written intrinsics; SIMD through std::simd on nightly); benchmarked only on x86-64 (Cascade Lake, AVX-512) |
| **Thread safety** | In `par` mode the encoder spawns its own worker threads (default count = available_parallelism, settable through `workers` or an environment variable) plus an MD5 thread; thread safety of the public types is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The crates.io release 0.5.1 (2025-12-18) lags main: it lacks RICE2 5-bit Rice parameters (#248; issue #246 saw a 24-bit step signal grow to 544 MB vs 47 KB at 16 bits), the portable_simd LaneCount fix (#249), and the STREAMINFO fix for inputs whose length is not a multiple of the block size (#255, merged 2026-06-29; strict decoders such as Symphonia rejected those files). The benchmark reports were built from unreleased main in May 2026, not from the published crate.
- The measured binaries use target-cpu=native from the repository's .cargo/config.toml (AVX-512 on the test VM) plus fat LTO, codegen-units 1, panic=abort and mimalloc; set RUSTFLAGS and the release profile yourself to reproduce that build in your own project.
- `mt1` (multithread with workers = 1) is not a one-core number: the reader/main thread and a separate MD5 thread run alongside the single worker. Only `st` (multithread = false) is single-threaded.
- The flacenc-bin README warns that the encoder "very rarely outputs broken signals" and suggests checking with the reference decoder's MD5; the parallel path also hits an `unreachable!` panic on out-of-range input samples (open issue #224) instead of returning an error.

## Known shortcomings

- CLI-versus-CLI comparison with one timing run per file; the flac C compiler is not logged. Single-threaded nightly SIMD build is 1.44x flac -8 but its output is 0.4% larger (0.60x against flac -5); the stable single-threaded build is 0.55x of flac -8; the 8-thread result is against single-threaded flac 1.4.3, which predates flac 1.5's -j option. Machine: GCP c2-standard-8 (Cascade Lake), rustc 1.95.0 and 1.97.0-nightly.
- The published reports were built from unreleased main (May 2026) while crates.io 0.5.1 (2025-12-18) lags it, so the record's 'stable report equals the crates.io default build' is wrong; 0.5.1 lacks RICE2 (#248; 24-bit step takes 544 MB, #246), the LaneCount fix (#249; the simd-nightly build is broken, #260) and the STREAMINFO tail-frame fix (#255; Symphonia rejected its files). Open robustness bugs: #256 (a 24-bit mono noise-to-silence block allocates 3.08 GB and overflows max_frame_size), unmerged PR #259 (u32 Rice bit-count wrap), #224 (unreachable! panic in the parallel path); the bin README admits it very rarely outputs broken signals. The mt1 mode is not single-core (reader thread plus one worker plus an MD5 thread) and flacenc's default searches less than flac -8 (LPC order 10 with one Tukey 0.4 window against order 12 with subdivide_tukey(3)); flac 1.5.0 has multithreading (-j16 at 5.47x single-thread per an HN snippet).

## Caveats and trade-offs

No measured configuration is both faster and at equal-or-better compression than a tested flac setting: single-thread flacenc (st) beats flac -8 in speed (1.44x nightly) while producing about 0.4% larger files, and against flac -5, whose files are about 1% larger, it is slower (0.60x nightly). The headline multi-threaded default uses 8 worker threads (4 physical cores with SMT) against flac 1.4.3, which has no threading; flac 1.5.0 (February 2025) added multithreaded encoding (-j/--threads) and was not benchmarked. On stable Rust, the crates.io default build, flacenc st runs at 0.55x of flac -8 and the 8-thread default only ties flac -5. flacenc is built with target-cpu=native (AVX-512 on this VM) while flac uses its generic configure build. Timing is a single wall-clock run per file with process start-up and file I/O included, on four recordings, no repeats. CLI against CLI, not library against library. The benchmark machine changed in May 2026 (c2-standard-8 replaced e2-standard-8, PR #253). The README makes no explicit speed claim and only links the reports.

FLAC encoder library designed for hackability, with an optional (experimental) decoder; the speed requires either nightly Rust with portable_simd or multi-threaded encoding (par feature, default on). Compression is about 0.4% larger than flac -8 (rate 0.5276 vs 0.5256).

## Maintenance

Active but slow to release (last commit 2026-06-29; crates.io 0.5.1 from December 2025 misses several correctness fixes on main, and issues #256 and #260 show no maintainer reply); Apache-2.0 and copyable, but pin a main-branch commit if you need the RICE2 and STREAMINFO fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The harness is public (pytools/reporter.py driven by Makefile.toml and bench_runner/runner_scripts/run_all.sh) and report/system_info.md logs the CPU (GCP c2-standard-8, Xeon Cascade Lake) and rustc versions, but the C compiler version used for flac 1.4.3 is not logged and timing is one wall-clock run per file; more importantly no measured configuration does equal work: single-thread flacenc beats flac -8 only at a slightly worse ratio and loses to flac -5, and the multi-threaded win is 8 threads against single-threaded flac 1.4.3. First-party, short of A: C.
- **Verifier notes:** Report numbers match the record; I added mt1, the derived ratios, and the compression-rate comparison the orchestrator asked for. Hardware, Rust versions and flags are now recorded from report/system_info.md and the bench_runner scripts. The flac 1.5 -j fact is from a WebSearch snippet (release-news results), not an opened page.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/report.nightly.md>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/report.stable.md>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/README.md>
  - <https://github.com/yotarok/flacenc-rs>
  - <https://github.com/yotarok/flacenc-rs/commits/main>
  - <https://github.com/yotarok/flacenc-rs/commits/main/report/report.nightly.md>
  - <https://github.com/yotarok/flacenc-rs/pull/253>
  - <https://github.com/yotarok/flacenc-rs/pull/254>
  - <https://github.com/yotarok/flacenc-rs/tree/main/bench_runner>
  - <https://github.com/yotarok/flacenc-rs/tree/main/report>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/Makefile.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/pytools/reporter.py>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/st.config.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/mt1.config.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/experimental.config.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/system_info.md>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/bench_runner/Containerfile>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/bench_runner/README.md>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/bench_runner/gce_run_job.sh>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/bench_runner/runner_scripts/run_all.sh>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/flacenc-bin/Cargo.toml>
  - <https://crates.io/api/v1/crates/flacenc>
  - <https://raw.githubusercontent.com/xiph/flac/1.4.3/configure.ac>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/report.nightly.md>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/report.stable.md>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/system_info.md>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/st.config.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/mt1.config.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/report/experimental.config.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/pytools/reporter.py>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/Makefile.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/bench_runner/runner_scripts/run_all.sh>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/flacenc-bin/Cargo.toml>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/flacenc-bin/README.md>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/flacenc-bin/src/main.rs>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/src/par.rs>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/src/lpc.rs>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/src/source.rs>
  - <https://raw.githubusercontent.com/yotarok/flacenc-rs/HEAD/CHANGELOG.md>
  - <https://github.com/yotarok/flacenc-rs/issues?q=is%3Aissue>
  - <https://github.com/yotarok/flacenc-rs/pulls?q=is%3Apr>
  - <https://github.com/yotarok/flacenc-rs/commits/main>
  - <https://github.com/yotarok/flacenc-rs/issues/256>
  - <https://github.com/yotarok/flacenc-rs/issues/246>
  - <https://github.com/yotarok/flacenc-rs/issues/242>
  - <https://github.com/yotarok/flacenc-rs/issues/224>
  - <https://github.com/yotarok/flacenc-rs/issues/260>
  - <https://github.com/yotarok/flacenc-rs/pull/259>
  - <https://github.com/yotarok/flacenc-rs/pull/255>
  - <https://github.com/yotarok/flacenc-rs/pull/248>
  - <https://crates.io/api/v1/crates/flacenc>
  - <https://raw.githubusercontent.com/xiph/flac/1.4.3/man/flac.md>
  - <https://raw.githubusercontent.com/xiph/flac/1.5.0/CHANGELOG.md>
  - WebSearch: FLAC encoder faster than libFLAC (result snippet for news.ycombinator.com/item?id=43012751, not opened)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/yotarok/flacenc-rs`) · [data/wave10/enrich/raw/github_com_yotarok_flacenc_rs.json](../../../data/wave10/enrich/raw/github_com_yotarok_flacenc_rs.json) (enrichment confidence 0.75)

</details>
