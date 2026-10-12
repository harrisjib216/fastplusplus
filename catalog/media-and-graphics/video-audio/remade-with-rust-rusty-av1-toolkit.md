# rusty-av1-toolkit

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-2-Clause` · 🟢 active

> rav1e fork whose default AV1 encode is byte-identical to stock rav1e and about 1.10x faster single-threaded; bundles a rav1d fork.

| | |
|---|---|
| **Beats** | stock rav1e (AV1 encoder); decoder side is a fork of rav1d, itself a Rust port of dav1d |
| **Claimed result** | Default --racecar off (byte-identical to stock rav1e, 262,180 B): median 7.588 s vs 6.911 s = 1.098x (per-round 1.072-1.117x); QP sweep 1.126x at QP 60, 1.099x at QP 100, 1.058x at QP 160. Opt-in --racecar on (rav1e's existing tx_domain_rate + tx_domain_distortion options plus the kernels): 4.586 s vs 7.745 s for the stock code path = 1.69x (1.61x over the byte-identical mode at 7.399 s), but the bitstream grows from 262,180 to 419,010 B (+60%) and PSNR drops from 44.50 to 42.22 dB (-2.28 dB) at the default tune; with --tune Psnr the probe measured +48% size and -1.13 dB. Decoder: no speed claim ('same as rav1d, profiled at its performance floor'). |
| **Workload** | Real rav1e CLI: fork at opt-entropy HEAD 885a2887 vs stock rav1e 564ae3b0 (merge-base with xiph/master), both built with 'identical flags'; one synthetic 640x480, 60-frame ffmpeg testsrc2 clip, --speed 6 --quantizer 100 --tiles 1 --threads 1, 7 interleaved rounds, median wall-clock. A QP sweep (QP 60/100/160, 9/5/5 rounds) and the --racecar on ('nitro') runs (5 interleaved rounds) used the same clip on the same unnamed machine, which the ledger says has about 5% thermal noise. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated; the ledger says only that both binaries were 'built with identical flags'. rusty_av1e/Cargo.toml release profile uses lto = "thin" and debug = true; asm feature needs nasm; minimum rust-version 1.83.0, actual rustc version not given. |
| **Adoption** | 0 stars, 1 fork, 112 commits; crates.io rusty_av1e 0.8.0 (1,270 downloads) and rusty_av1d 1.2.0 (1,492 downloads); README banner claims 1,002 active installs (not verifiable). |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/Remade-With-Rust/rusty-av1-toolkit) · [benchmark](https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/docs/entropy-bricks.md) |

## Verdict

First-party, on an unnamed machine with about 5% thermal noise. The fork's rav1e CLI at 885a2887 against stock rav1e 564ae3b0 (an upstream xiph/rav1e master commit), built with the same unstated flags, encoded one synthetic 640x480, 60-frame ffmpeg testsrc2 clip at --speed 6 --quantizer 100 --tiles 1 --threads 1. Median 6.911 s vs 7.588 s (1.098x over 7 interleaved rounds, every round 1.072-1.117x), with identical 262,180-byte output; a single-binary racecar A/B reproduced 1.079x, and a QP sweep gave 1.058-1.126x. The 1.69x mode changes the bitstream (+60% bytes, -2.28 dB PSNR) and divides by a stock time from a different session; within one session it is 1.61x over the byte-identical mode.

## Use it when

- You already ship rav1e and want shorter encodes with output that is byte-identical to the default stock bitstream: 1.058-1.126x single-threaded at speed 6 on the authors' clip, with the full gain on x86-64 CPUs that have AVX2.
- Dense, high-rate encodes (low QP), where entropy coding is a larger share of encode time: 1.126x at QP 60 against 1.058x at QP 160.
- A pure-Rust, BSD-2 AV1 encoder embedded in a Rust application (it backs AVIF/AV1 encoding in remade_ffmpeg_rs), where a C encoder is not an option.
- CPU-bound, bandwidth-insensitive encoding where 50-60% more bytes is acceptable: `--racecar on --tune Psnr` ran about 1.6x faster than the byte-identical mode on the same clip.

## Skip it when

- When encode speed per core is the main goal and a C encoder is acceptable: SVT-AV1 is the catalogued fast AV1 encoder, and a 1.10x gain does not change rav1e's position against it (no cross-encoder numbers here).
- Multi-threaded or tiled production encodes: every A/B is `--threads 1 --tiles 1` on one synthetic 640x480 clip, and the gain at default threading is not measured.
- aarch64: the AVX2 stencil has no NEON twin yet (ledger item 9), so ARM gets only the portable B7a and Q2 changes, and its speedup is unmeasured.
- Bandwidth-limited delivery in `--racecar on`: +60% bitstream and -2.28 dB PSNR at the default tune; a faster stock `--speed` preset may be the better trade, and none was compared.
- Long-term dependencies that need upstream fixes: the code is vendored rather than a GitHub fork, upstream tracking is an unchecked roadmap item, there is no CI (PRs #3 and #4 adding a check workflow are still open), and the repo has 0 stars.

## How it is fast

Profiling put `write_coeffs_lv_map` (coefficient token coding) at 48.6% and quantize at 12.3% of a speed-6 single-thread encode, and three byte-identical changes were kept. B7a turns the per-scan-position non-zero-map context stencil into a full-area, column-contiguous kernel that can vectorize. B7a-SIMD is a hand-written AVX2 twin of that kernel (one ymm register per column of up to 32 rows, vpminub/vpaddb stencil, vpavgb for (mag+1)&gt;&gt;1). Q2 rewrites quantize's serial main loop branch-free, removing two data-dependent mispredicted branches. Per the ledger the stencil dropped from 878 to 96 ms and the quantize loop from 676-730 to 440-466 ms. `--racecar on` additionally switches on rav1e's existing `tx_domain_rate`/`tx_domain_distortion` options, which replace real token coding in RDO with a table-based rate estimate.

## Compared with alternatives

SVT-AV1 is the catalogued fast AV1 encoder (C); pick rusty_av1e only when you are tied to rav1e's Rust API or exact bitstream and want the same output sooner. For decoding, use the catalogued dav1d, or rav1d-safe if you need safe Rust; this repo's rusty_av1d makes no speed claim.

## Integration

| | |
|---|---|
| **Form** | crate (rusty_av1e 0.8.0 library plus `rav1e` CLI; rusty_av1d 1.2.0 library plus `dav1d` CLI); two separate Cargo projects, no top-level workspace |
| **Dependencies** | rusty_av1e defaults pull nasm (via nasm-rs and cc) for upstream asm, plus clap/y4m/ivf and the other CLI crates, and maybe-rayon for threading; `default-features = false` gives a no-asm build in which the AVX2 stencil still runs (std runtime detection). rusty_av1d needs nasm for x86 asm. |
| **Minimum toolchain** | rusty_av1e rust-version 1.83.0; rusty_av1d rust-version 1.79 for a stable library build, though its directory pins nightly-2026-02-05 |
| **Platforms** | any rav1e target; x86-64 with AVX2 gets the hand-written stencil (runtime-detected, scalar fallback); upstream x86 and ARM asm kept; Windows, macOS and Linux named in the README |
| **Thread safety** | As upstream rav1e (one Context per encode, rayon threads). The fork adds process-global OnceLock latches (racecar mode and about 40 RAV1E_\* environment knobs), read once per process and shared by every encoder in it. |
| **Drop-in for the baseline** | partial: same API, same CLI flags and byte-identical default output to stock rav1e 564ae3b0 per the authors, but the crate is renamed (`use rusty_av1e::...`), and the byte-identity is not enforced by any committed test |

## Gotchas

- The process environment changes output. About 40 RAV1E_\* variables (RAV1E_FAST, RAV1E_TRELLIS, RAV1E_LAMBDA_MULT, RAV1E_MODE_TOPK, RAV1E_WARP_FORCE and others) are latched into statics and alter encoder decisions. RAV1E_RACECAR=0 restores the stock kernels, and RAV1E_HARVEST=&lt;path&gt; appends CSV telemetry and panics if the file cannot be opened.
- The 'byte-identical gate' is not automated: tests/profile_encode.rs prints the bitstream FNV and only asserts run-to-run determinism, and the stock hash 688d5eeaee94d95e that the README says is pinned there is not in the file. Byte-identity at HEAD therefore rests on manual checks last ledgered on 2026-07-02, while later tier work landed behind environment gates.
- Naming is inverted between layers. On the CLI, `--racecar off` is the optimized default and `on` changes the bitstream, but racecar.rs and the toggle-site comments still describe the pre-remap meaning (racecar on = kernels = default). The dispatch comment says the AVX2 kernel honours RAV1E_CPU_TARGET, but the code calls `is_x86_feature_detected!("avx2")` directly, so RAV1E_CPU_TARGET cannot turn it off.
- `--racecar on` uses stock rav1e's own tx-domain rate estimator (off at every stock speed preset), not new fork code. It also forces `tx_domain_distortion` on, working around an upstream assert that the fork's ledger documents: tx_domain_rate with the psychovisual tune panics in `distortion_scale`, reachable through the API or a config file.

## Known shortcomings

- Rust (language-filter mismatch). The numbers are its own encoder kernels against stock rav1e 564ae3b0 (not vendored numbers), 1.098x median over 7 rounds on one testsrc2 640x480 60-frame clip, machine unnamed, and the ab.sh script is not in the repo; the --racecar 1.69x costs 60% more bytes and 2.28 dB. No decoder claim.
- All timings are one thread, one tile and one synthetic clip, 1.69x across sessions (1.61x same-session); the README's claim that the FNV gate is pinned in tests/profile_encode.rs is false (the test asserts determinism only) and byte identity has been unverified since 2026-07-02; no CI (PRs #3 and #4 open); the tier work is env-gated and off by default; no NEON twin of the AVX2 kernel; about 40 RAV1E_\* environment variables change output.

## Caveats and trade-offs

First-party, one synthetic 640x480 60-frame testsrc2 clip at speed 6, single thread and single tile; the machine, rustc version and flags are not named, and the A/B script (scratchpad/ab.sh) is not in the repo, although the binary keeps a '--racecar stock' mode that reproduces the stock code paths. The 1.10x gain is content dependent (1.058x to 1.126x by QP) and sits near the box's stated 5% thermal noise. The 1.69x mode is a quality trade, not a free speedup: it turns on rav1e's own tx-domain rate estimation (which stock rav1e leaves off at every speed) and costs +60% bitstream and -2.28 dB PSNR at the default tune; its 1.69x divides by a stock time taken from a separate sweep session. The numbers belong to this fork's own encoder kernels (B7a nz-map stencil, its AVX2 twin, Q2 branchless quantize), not to the vendored rav1e or rav1d projects; the decoder half (rav1d fork) has no speed claim. Not a GitHub fork; is_fork_of rav1e for the encoder, the decoder forks memorysafety/rav1d. Rust code with a Rust baseline (rav1e is not a wave-10 list baseline and not in the catalog). Part of Mata Network's 'Remade With Rust' initiative; README opens with an install-count banner and an advert. AV1 patent grant comes from the AOM Patent License 1.0 in rusty_av1e/PATENTS, separate from the BSD-2-Clause source license.

Encoder fork of rav1e (not a GitHub fork: the parent code is vendored into rusty_av1e/) with tuned hot kernels and asm; the content-adaptive 'RAV1E_FAST=fast' tier trades quality for speed and is content-dependent (measured +5.3% bus, +3.3% akiyo, -8.7% mobile BD-rate vs the default at speed 6). Rust only; the baseline is rav1e, not libaom, SVT-AV1 or x265.

## Maintenance

Last code change 2026-08-02 (113 commits; later commits through 2026-10-04 only edit an install-count banner), BSD-2-Clause plus the AOM patent licence, 0 stars, no issues, no CI. Reasonable to trial as a rav1e drop-in, but a thin, recently forked dependency to build on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party wall-clock A/B of the forked rav1e CLI against stock rav1e 564ae3b0, documented in rusty_av1e/docs/entropy-bricks.md (one synthetic testsrc2 clip, 7 interleaved rounds). The in-binary '--racecar stock' path and tests/profile_encode.rs are public, but the A/B script (scratchpad/ab.sh) is not in the repo, rustc version and flags are given only as 'identical flags', and the machine is never named, so it cannot be A.
- **Verifier notes:** Numbers are the fork's own encoder work measured against stock rav1e, so this is not a wrapper or duplicate of a listed project (rav1e and rav1d are not in the catalog); the decoder side carries no claim. Language is Rust (already set), a mismatch with the C++ language filter of the search. racecar.rs doc comment still describes the pre-remap default (racecar on), while README and ledger say the default is now off (byte-identical kernels).
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/README.md>
  - <https://github.com/Remade-With-Rust/rusty-av1-toolkit>
  - <https://github.com/Remade-With-Rust/rusty-av1-toolkit/commits>
  - <https://github.com/Remade-With-Rust/rusty-av1-toolkit/tree/main/rusty_av1e>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/docs/entropy-bricks.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/racecar.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/tests/profile_encode.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/LICENSE>
  - <https://crates.io/api/v1/crates/rusty_av1e>
  - <https://crates.io/api/v1/crates/rusty_av1d>
- **Sources the enricher read:**
  - <https://github.com/Remade-With-Rust/rusty-av1-toolkit>
  - <https://github.com/Remade-With-Rust/rusty-av1-toolkit/commits>
  - <https://github.com/Remade-With-Rust/rusty-av1-toolkit/issues?q=is%3Aissue>
  - <https://github.com/Remade-With-Rust/rusty-av1-toolkit/pulls>
  - <https://github.com/Remade-With-Rust/rusty-av1-toolkit/tree/main/rusty_av1e/src>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/docs/entropy-bricks.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/racecar.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/bin/common.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/bin/rav1e.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/context/transform_unit.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/encoder.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/harvest.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/tempfilter.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/src/warp.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1e/tests/profile_encode.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1d/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1d/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-av1-toolkit/HEAD/rusty_av1d/rust-toolchain.toml>
  - <https://github.com/xiph/rav1e/commit/564ae3b0>
  - <https://crates.io/api/v1/crates/rusty_av1e>
  - <https://crates.io/api/v1/crates/rusty_av1d>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/remade-with-rust/rusty-av1-toolkit`) · [data/wave10/enrich/raw/github_com_remade_with_rust_rusty_av1_toolkit.json](../../../data/wave10/enrich/raw/github_com_remade_with_rust_rusty_av1_toolkit.json) (enrichment confidence 0.65)

</details>
