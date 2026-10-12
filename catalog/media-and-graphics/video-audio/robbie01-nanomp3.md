# nanomp3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Safe, no_std Rust port of minimp3 (MP3/MP2/MP1 decode), bit-exact, 6-21% faster than minimp3's SIMD build.

| | |
|---|---|
| **Beats** | minimp3 (SIMD and scalar builds) |
| **Claimed result** | 76.0 vs 71.9 MiB/s (minimp3 SIMD) and 67.8 (scalar) on 48 kHz stereo 320 kbps; 72.7 vs 60.3 / 53.0 on 22 kHz MPEG-2 mixed bitrates; 52.6 vs 47.5 / 42.5 on mode-switching short blocks (about 1.06x to 1.21x over minimp3 SIMD, derived from page data). |
| **Workload** | In-memory MP3 frame decode throughput (criterion, MiB/s of MP3 input, f32 output, decoder created per iteration) on three inputs from parity/benches/decode.rs: 'The Washington Post.mp3' (MPEG-1 48 kHz joint stereo 320 kbps, in nanomp3-core/src/tests), the minimp3 conformance vector M2L3_bitrate_22_all.bit (MPEG-2 LSF 22.05 kHz, all bitrates) and l3-he_mode.bit (mono, short blocks, intensity stereo mix). |
| **Metric** | throughput |
| **Hardware** | Windows x86-64, CPU model not stated |
| **Compiler and flags** | C references built by the cc crate in parity/build.rs with opt_level 3 plus -ffp-contract=off and -ftrivial-auto-var-init=zero (clang-cl on MSVC targets; README says clang -O3); minimp3 SIMD build uses its default SSE/NEON intrinsics with MINIMP3_ONLY_MP3 and MINIMP3_FLOAT_OUTPUT, scalar build adds MINIMP3_NO_SIMD. Rust side uses the default cargo bench profile (no profile overrides in the workspace Cargo.toml), wide feature on, no target-cpu flag; rustc version not stated (MSRV 1.89). Reproduce with cargo bench -p nanomp3-parity. |
| **Adoption** | 22 stars; 3 forks; crates.io nanomp3 0.2.0 (27,841 downloads, 20,154 recent) |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/robbie01/nanomp3) · [benchmark](https://github.com/robbie01/nanomp3) |

## Verdict

Criterion in-memory decode throughput (MiB/s of MP3 input, f32 output, decoder created per iteration) on Windows x86-64 with an unstated CPU and rustc: nanomp3 76.0 vs minimp3 SIMD 71.9 and scalar 67.8 on 48 kHz 320 kbps stereo, 72.7 vs 60.3 / 53.0 on 22 kHz MPEG-2 mixed bitrates, 52.6 vs 47.5 / 42.5 on mode-switching short blocks. The C baselines were built by parity/build.rs with -ftrivial-auto-var-init=zero, which makes minimp3 zero its whole on-stack mp3dec_scratch_t (about 16 KB, per minimp3.h) on every frame while nanomp3 keeps that scratch in the decoder and clears only scf, ist_pos and grbuf, so the baseline carries extra per-frame work stock minimp3 does not do (unmeasured; likely a few percent at most, smaller than the reported gaps); and on MSVC targets cc-rs caps the requested -O3 to clang-cl -O2.

## Use it when

- Rust applications or game/audio engines that need MP3 playback without linking C (no unsafe, no build script, only the optional wide dependency).
- Embedded or no_std targets: nanomp3-core builds for thumbv7em-none-eabihf and riscv32imac-unknown-none-elf in CI on Rust 1.89, with no allocator needed for the frame decoder.
- Projects already using minimp3 or minimp3_ex that want the same output bit for bit (f32 path) plus fixes for minimp3_ex's I/O and APEv2 trimming bugs, with Options::minimp3_compat when exact legacy behavior matters.
- Batch decoding of whole files in memory where a 6-21% throughput gain over minimp3 SIMD (x86-64, first-party) is worth a dependency swap.
- Gapless playback and sample-accurate seeking via Reader/SliceReader instead of writing your own frame-index logic.

## Skip it when

- C or C++ projects: there is no C API, so calling it means writing and maintaining a Rust FFI shim; minimp3 itself is a single header and nearly as fast.
- When you need a broader decoder (AAC, Vorbis, Opus, containers) or a reference-quality float pipeline such as libmpg123 or FFmpeg; nanomp3 is only as accurate as minimp3 and was not benchmarked against either.
- If the speed claim is the deciding factor on ARM or non-Windows hosts: the only numbers are one first-party table on Windows x86-64 with an unnamed CPU and rustc version.
- Maturity-sensitive deployments: 0.2.0 was published 2026-09-30 with breaking API changes from 0.1 (decode signature, generic sample type, non_exhaustive FrameInfo), and the project has one maintainer and 22 stars.
- Streams that need encoding, metadata editing or MPEG-2.5 extensions beyond what minimp3 decodes: not documented.

## How it is fast

The DSP kernels (IMDCT, polyphase synthesis, stereo processing) are written once over a small Lanes trait and instantiated for wide::f32x4 SIMD bodies and scalar tails; each lane does exactly the scalar arithmetic (no fused multiply-add, no reassociation), so vectorization keeps bit-exactness. Per-frame scratch (grbuf, scf, syn, ist_pos) and the main-data buffer live inside the decoder instead of on the stack, and only scf, ist_pos and grbuf are cleared per frame; the bit reader is bounded to the valid bytes so corrupt-stream over-reads see zeros without clearing the buffer. Both crates are #![forbid(unsafe_code)], so the gains come from data layout and explicit SIMD rather than unchecked indexing.

## Compared with alternatives

Pick it over minimp3 (lieff/minimp3, catalogued in this category) when you are in Rust and want no unsafe, no_std, gapless seeking and slightly higher throughput with identical f32 output; stay with minimp3 from C or C++. Pick it over remade_ffmpeg_rs when you want a small, bit-exact MP3-only decoder rather than a broader FFmpeg-style toolkit.

## Integration

| | |
|---|---|
| **Form** | crate (nanomp3 reader crate re-exporting nanomp3-core frame decoder) |
| **Dependencies** | none required; optional wide (explicit SIMD, default on). Without wide the same kernels run on plain arrays and rely on LLVM auto-vectorization (README: a few percent slower). |
| **Minimum toolchain** | Rust 1.89 (1.80 without the wide feature), edition 2021 |
| **Platforms** | any Rust target; CI tests ubuntu x86-64, ubuntu-24.04-arm, windows and macos, builds no_std for thumbv7em-none-eabihf and riscv32imac-unknown-none-elf, and runs Miri and fuzz jobs |
| **Thread safety** | Decoder is plain owned state with no globals or unsafe, so separate decoders can run on separate threads; a single decoder is used through &mut self. No further statement in the docs. |
| **Drop-in for the baseline** | partial — same frame-by-frame model and bit-identical f32 output as minimp3's scalar reference build, but a Rust API (Decoder::decode, Reader) rather than mp3dec_decode_frame/mp3dec_ex_\*; default i16 rounding deliberately differs unless minimp3_compat is set |

## Gotchas

- Bit-exactness is against minimp3 built with MINIMP3_NO_SIMD and -ffp-contract=off (parity/build.rs). Stock minimp3 SIMD builds, or C builds that contract multiply-adds into FMA (common on ARM64), can differ from nanomp3 in low bits.
- Default i16 output rounds half away from zero (about 0.3% of samples differ from minimp3 on the conformance vectors); use Decoder::new_minimp3_compat() or Options::minimp3_compat for minimp3's exact i16 output.
- The Decoder is about 23 KB by value (overlap and QMF state plus the per-frame scratch and main-data buffers, summed from the struct definitions in minimp3.rs), so placing it on a small embedded stack needs care; nanomp3-core does no buffering, and the README suggests keeping a read-ahead of several frames (16 KiB) yourself.
- 0.2.0 split the crate into nanomp3-core plus nanomp3 and changed Decoder::decode to return Result&lt;FrameInfo, DecodeError&gt;; items under __private, __compat and __Raw are not covered by semver.

## Known shortcomings

- Rust (language-filter mismatch). Baseline is minimp3 (recorded in this wave), not a listed incumbent. Criterion bench (parity/benches/decode.rs, f32, minimp3 submodule built at -O3 -ffp-contract=off -ftrivial-auto-var-init=zero) with bit-exact output against scalar minimp3 on all conformance vectors (parity/tests/parity.rs, CI on 4 OSes); CPU model and rustc version unstated.
- Minor bias toward nanomp3: parity/build.rs builds the C baselines with -ftrivial-auto-var-init=zero, so minimp3 zeroes its whole 16 KB on-stack mp3dec_scratch_t every frame while nanomp3 keeps its scratch in the decoder and clears only scf, ist_pos and grbuf (the verifier's 'nanomp3 also zeroes' caveat is wrong); likely a few percent, below the 6-21% gaps. The README's 'clang -O3' is capped to -O2 by cc-rs for clang-cl on MSVC targets; -ffp-contract=off is moot on x86-64 without FMA; bit-exact only against a NO_SIMD, fp-contract-off minimp3 build. lieff/minimp3 is a catalogued sibling, so baseline_in_list should read true.

## Caveats and trade-offs

Baseline minimp3 is itself a small decoder, not libmpg123 or FFmpeg, and nanomp3 is a port of it, so this is a modest win over its own port target: 6-21 percent over minimp3 SIMD and 12-37 percent over minimp3 scalar (derived from page data). CPU model and rustc version not stated, Windows x86-64 only, three inputs, first-party table. Decoding is bit-exact: parity/tests/parity.rs compares nanomp3's f32 output with minimp3's scalar builds on every conformance vector plus the march file, run in CI on ubuntu x86-64, ubuntu-24.04-arm, windows and macos; minimp3's own SIMD build, the faster C baseline, is not bit-exact with its scalar reference. The C builds use -ftrivial-auto-var-init=zero (zeroing minimp3's otherwise uninitialized per-frame scratch, which nanomp3 also zeroes) and -ffp-contract=off, so they are like-for-like with nanomp3 but may run slower than a stock minimp3 build by an unmeasured margin, which matters at a 6 percent gap. Default i16 rounding differs from minimp3 by design (bug fix; compat mode available); the benchmark uses f32. Comparison is Rust versus C, not C++ std.

Safe Rust port of minimp3 (forbid(unsafe_code)), bit-exact with minimp3 on its conformance vectors, no_std core crate with explicit SIMD via the wide crate; fixes a few minimp3 bugs by default (opt-out via minimp3_compat). No C API, so C++ callers need a wrapper. Also decodes MP1/MP2.

## Maintenance

Active single-maintainer project (last commit 2026-09-28, 0.2.0 on crates.io 2026-09-30, about 27,900 downloads), MIT OR Apache-2.0 and pure safe Rust, so easy to vendor in Rust projects but not directly usable from C++.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance table matches the record exactly and is produced by public code (parity/benches/decode.rs, criterion, with upstream minimp3 built from the parity/minimp3 submodule by parity/build.rs), but the CPU model and rustc version are not stated, so it falls short of A; first-party only.
- **Verifier notes:** All nine numbers in claimed_speedup match the README table; nanomp3 0.1 column shows the earlier release was slower than minimp3 (55.7 vs 71.9 MiB/s). baseline_in_list stays false. Rust crate found on crates.io, which does not fit the C++ language filter; language field set. Last commit 2026-09-28 confirmed (crates.io 0.2.0 published 2026-09-30).
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`, `baseline_in_list`
- **Pages the verifier opened:**
  - <https://github.com/robbie01/nanomp3>
  - <https://github.com/robbie01/nanomp3/commits/master>
  - <https://github.com/robbie01/nanomp3/tree/master/parity>
  - <https://github.com/robbie01/nanomp3/tree/master/parity/benches>
  - <https://github.com/robbie01/nanomp3/tree/master/parity/tests>
  - <https://github.com/robbie01/nanomp3/tree/master/.github/workflows>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/HEAD/README.md>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/parity/benches/decode.rs>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/parity/build.rs>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/parity/Cargo.toml>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/Cargo.toml>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/parity/tests/parity.rs>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/CHANGELOG.md>
  - <https://crates.io/api/v1/crates/nanomp3>
- **Sources the enricher read:**
  - <https://github.com/robbie01/nanomp3/tree/master/parity/src>
  - <https://github.com/robbie01/nanomp3/tree/master/nanomp3-core/src>
  - <https://github.com/robbie01/nanomp3/tree/master/nanomp3-core/src/minimp3>
  - <https://github.com/robbie01/nanomp3/issues?q=is%3Aissue>
  - <https://github.com/robbie01/nanomp3/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/README.md>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/Cargo.toml>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/.gitmodules>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/nanomp3-core/Cargo.toml>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/nanomp3-core/src/lib.rs>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/nanomp3-core/src/minimp3.rs>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/nanomp3-core/src/minimp3/lanes.rs>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/parity/Cargo.toml>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/parity/build.rs>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/parity/src/lib.rs>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/parity/benches/decode.rs>
  - <https://raw.githubusercontent.com/robbie01/nanomp3/master/parity/tests/parity.rs>
  - <https://raw.githubusercontent.com/lieff/minimp3/master/minimp3.h>
  - <https://raw.githubusercontent.com/rust-lang/cc-rs/main/src/lib.rs>
  - <https://crates.io/api/v1/crates/nanomp3>
  - WebSearch: Symphonia Rust audio decoder benchmark FFmpeg MP3 performance percent (checked for a sibling lead; Symphonia is already in data/wave10)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/robbie01/nanomp3`) · [data/wave10/enrich/raw/github_com_robbie01_nanomp3.json](../../../data/wave10/enrich/raw/github_com_robbie01_nanomp3.json) (enrichment confidence 0.75)

</details>
