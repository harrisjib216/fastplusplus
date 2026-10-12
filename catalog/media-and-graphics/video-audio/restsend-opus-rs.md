# opus-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Pure-Rust, no_std, zero-dependency port of libopus 1.6; first-party tables show parity on SILK and 5-28% gains on 48 kHz CELT encode.

| | |
|---|---|
| **Beats** | libopus 1.6.1 (C reference encoder) |
| **Claimed result** | README tables vs libopus 1.6.1, mono, wall-clock for the full frame set. Ryzen 7 5700X: 8 kHz/20 ms VoIP 39.9 vs 40.6 ms (Rust 2% faster); 16 kHz/20 ms VoIP 66.8 vs 67.1 ms (0.5%); 16 kHz/10 ms VoIP 73.2 vs 72.5 ms (C ahead, within noise); 48 kHz/20 ms Audio 25.1 vs 28.4 ms (12%); 48 kHz/10 ms Audio 29.7 vs 31.2 ms (5%). Apple Silicon M-series (run 2026-04-23): 8 kHz/20 ms 31.47 vs 31.20 ms (C 0.9% faster); 16 kHz/20 ms 51.19 vs 52.81 ms (Rust 3.1%); 16 kHz/10 ms 55.69 vs 55.49 ms (within noise); 48 kHz/20 ms 13.97 vs 19.39 ms (28%); 48 kHz/10 ms 16.19 vs 20.28 ms (20%). The VoIP (SILK) rows are at parity; the gains are in the 48 kHz Audio-application rows. |
| **Workload** | Mono encode-only of real speech (fixtures/answer_16k.wav) at 8/16/48 kHz with 10 and 20 ms frames, VoIP and Audio applications; wall-clock time for the full frame set, Criterion with 20 samples. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5700X; Apple Silicon M-series (model not stated) |
| **Compiler and flags** | README: cargo --release with 'opt-level=3 + ThinLTO'; Cargo.toml has no [profile.release] section (a local .cargo config is gitignored), rustc version not stated; libopus 1.6.1 built from a local opus-1.6.1/ tree that .gitignore excludes, its build flags not stated |
| **Adoption** | 50 stars, 7 forks; crates.io opus-rs 0.1.34: 181,963 downloads (131,859 recent); forked as Remade-With-Rust/rusty-opus |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/restsend/opus-rs) · [benchmark](https://github.com/restsend/opus-rs) |

## Verdict

The author's README tables time mono encoding of one 16 kHz speech clip (resampled crudely to 8 and 48 kHz) against libopus 1.6.1 built from a local, gitignored tree, Rust built with --release and ThinLTO (rustc version and C flags not stated): on a Ryzen 7 5700X the SILK VoIP rows are within 2% of libopus and the 48 kHz Audio rows are 5-12% faster; on an unnamed Apple M-series (2026-04-23, version 0.1.17) they are within 3% and 20-28% faster. The C-comparison harness is not public, the checked-in bench has no libopus arm and times encode plus decode, and the 48 kHz CELT rows benefit from the batched PVQ search and the absent tonality analysis, so the gain is not a like-for-like code-generation result.

## Use it when

- Rust VoIP, SIP or WebRTC services (the author's rustpbx and rustrtc stacks) that want Opus encode and decode without building or linking C, at about libopus speed on SILK and somewhat faster on 48 kHz CELT.
- Bare-metal, RTOS or wasm32-unknown-unknown targets: default-features = false gives a no_std, no-alloc build (libm feature for float math), verified by the author on thumbv7em-none-eabi and wasm32.
- Mono or stereo encode at 8, 16 or 48 kHz with 10 or 20 ms frames, the configurations the README tables and the interop tests cover.
- Pipelines holding PCM16 audio: encode_i16 feeds the SILK high-pass filter directly and is documented as byte-identical to encode() on the converted samples.

## Skip it when

- C or C++ projects: no C API, so libopus itself is the simpler choice, and the measured gain over it is at most 12% (Ryzen) on the 48 kHz rows and nil on the SILK rows.
- Encoding 24 kHz input (open issue #37: decodes to garbage in every application mode; resample to 48 kHz first), 60 ms frames (open issue #35: rejected as an invalid frame size), or in-band FEC at CBR (open issue #36: no LBRR emitted).
- Strict bit-exactness or interop expectations: open issues #34 (mono SILK decode one sample ahead of libopus) and #38 (48 kHz SILK/hybrid output lags libopus's pre-skip by up to 17 samples; low-bitrate Audio mangles the first \~200 ms), and the repo's own interop table lists hybrid mono 48 kHz decode at 14.6 dB SNR against libopus 1.6.1.
- Fleets that include AVX-without-FMA CPUs (Sandy Bridge, Ivy Bridge, Bulldozer, some VMs): open issue #30, still present at HEAD, where celt.rs gates the avx,fma comb_filter_const_avx kernel on an AVX-only check and the CPU gets SIGILL; fix PR #31 is unmerged.
- Workloads that rely on libopus's high-complexity quality tools: tonality analysis is not ported and PVQ search uses a batched approximation, so output at default complexity is not the same bitstream libopus would produce.

## How it is fast

Line-by-line port of libopus's float encoder and decoder with hand-written intrinsics: runtime-dispatched SSE/AVX/AVX2+FMA kernels on x86-64 (is_x86_feature_detected) and unconditional NEON on aarch64 for the comb filter, haar1, MDCT/kiss FFT and PVQ search. Part of the CELT gain is algorithmic rather than code generation: for bands with n &gt;= 32 and at least 8 pulses left after projection, pvq_search_fast_select places pulses four at a time from one select_nth_unstable ranking (BATCH_SIZE = 4 in src/pvq.rs), where libopus re-scores after every pulse, and the encoder has no port of libopus's tonality analysis (analysis.c), which libopus 1.6.1 float runs at complexity &gt;= 7 for 16-48 kHz input.

## Compared with alternatives

Pick opus-rs over ropus, ruopus, rusty-opus or gopus when you need a pure-Rust Opus encoder and decoder that is already widely pulled from crates.io (about 182,000 downloads), has zero runtime dependencies and builds no_std without an allocator; the siblings' own first-party numbers are larger (ruopus 1.4-1.8x libopus decode, opus-pure 1.09-1.76x encode, rusty-opus 1.50x on CELT speech), so do not pick opus-rs for speed alone.

## Integration

| | |
|---|---|
| **Form** | crate (opus-rs on crates.io, 0.1.34) |
| **Dependencies** | none at runtime with default features (std, heap); libm (pure Rust) for no_std builds; criterion, proptest and the opus 0.3 bindings crate (audiopus_sys) are dev-dependencies only |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85+); no rust-version is declared in Cargo.toml |
| **Platforms** | x86-64 with runtime SSE/AVX/AVX2 dispatch (compile-time detection without std, so build with -C target-feature=+avx2), x86 32-bit (AVX import fix in PR #16), aarch64 with NEON, thumbv7em-none-eabi and wasm32-unknown-unknown in no_std mode |
| **Thread safety** | Not documented. encode and decode take &mut self, so use one encoder or decoder per stream or thread; constant tables are built once through an internal heap-free OnceCell. |
| **Drop-in for the baseline** | partial: the same codec and bitstream format, with Opus packets decodable by libopus, but a Rust API with struct fields in place of opus_encoder_ctl, no C ABI, and gaps (24 kHz encode, 60 ms frames, FEC at CBR, tonality analysis) |

## Gotchas

- The README's command cargo bench --bench opus_vs_c_bench does not exist: Cargo.toml registers only opus_bench, whose opus_real group runs Rust encode plus decode at complexity 0, CBR, 20 or 64 kb/s, with 48 kHz input made by repeating each 16 kHz sample three times and 8 kHz input by dropping every other sample. libopus 1.6.1 skips tonality analysis below complexity 7, so if the private C bench matched complexity 0 the work was comparable; if it ran at the default complexity 9, libopus did analysis work opus-rs never does. The README does not say which.
- Byte-exact CELT output against libopus is claimed per architecture only: tests/oracle_celt.rs keeps separate x86_64 and aarch64 fixtures, and its impulse fixture diverges from libopus 1.6.1 after byte 7 because analysis.c is not ported. The PVQ cross-check against C (tests/verify_pvq_match.rs) uses n = 8, so it never reaches the batched n &gt;= 32 search path.
- Without the heap feature (no_std) OpusEncoder and OpusDecoder are about 250 KB and 175 KB inline, so place them in a static; before 0.1.29 even the std build needed about 0.85 MiB of stack to construct an encoder (issue #12).
- pvq.rs (71 unsafe occurrences) and celt.rs use raw-pointer loops and intrinsics; the crate is not #![forbid(unsafe_code)], and issue #7 (closed) asked for decoder hardening against untrusted packets.

## Known shortcomings

- Rust (language-filter mismatch). README numbers match but the libopus comparison is not reproducible: opus_vs_c_bench.rs and opus_vs_c_real.rs are 404, opus-1.6.1/ and tests/\*.c are gitignored, and the 0.1.17 crate has no C bench. The checked-in opus_real harness runs encode plus decode at complexity 0, CBR; VoIP rows are at parity. 181,963 crates.io downloads.
- The 48 kHz CELT gains rest on less work than libopus: src/pvq.rs at HEAD still uses a batch-4 PVQ approximation (pvq_search_fast_select, BATCH_SIZE 4 for n of 32 or more and k of 8 or more; issue #18) rather than libopus's per-pulse rescoring, the tonality analysis (analysis.c) is not ported although libopus 1.6.1 float runs it at complexity 7 and above (default 9), the README never states the C bench's complexity and the checked-in bench uses 0, and tests/verify_pvq_match.rs covers n = 8 only. Open bugs: #37 (24 kHz encode garbage), #35 (60 ms frames rejected), #36 (no LBRR at CBR), #34 and #38 (sample offsets versus libopus), #30 (SIGILL on AVX without FMA at celt.rs:824; fix PR #31 unmerged).

## Caveats and trade-offs

Rust crate (language-filter mismatch for a C++-first catalog). The README tells readers to run `cargo bench --bench opus_vs_c_bench`, but no such target exists: benches/ holds only opus_bench.rs (no libopus arm; the opus 0.3 dev-dependency is not used there), Cargo.toml registers only opus_bench, bench_quick.sh filters for 'opus_vs_c_real', and the published 0.1.17 crate (whose date matches the Apple run) has no C bench either; .gitignore excludes opus-1.6.1/ and tests/\*.c, so the C comparison cannot be reproduced. The checked-in Rust-only opus_real group does encode plus decode at complexity 0, CBR, 20/64 kbps, with 48 kHz input made by repeating each 16 kHz sample three times, which differs from the README's 'encode-only' description; whether the private C bench matched these settings is unknown. Single speech clip, mono; stereo and music untested. VoIP rows are within noise or favour C. The Apple numbers date from 2026-04-23 (0.1.17) and the CELT encoder was reworked for byte-exactness in August 2026, so the tables may be stale. Tier would be A if the C-comparison benchmark and the libopus build flags were public.

Pure Rust port of libopus 1.6, #![no_std] with no alloc option; Rust only, so not callable from C++ without a C ABI wrapper. Most results are within a few percent of libopus; the README calls it 'competitive'.

## Maintenance

Actively maintained (0.1.34 on 2026-09-22, 96 commits, outside contributors fixing CELT byte-exactness and SIMD bugs) and BSD-3-Clause, so it is easy to adopt from Rust, but nine issues were open on 2026-10-04, five of them encoder or decoder correctness bugs filed in late September 2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables against libopus 1.6.1 on a named CPU (Ryzen 7 5700X; Apple M-series model unstated), but the C-comparison benchmark (opus_vs_c_bench) is not public: benches/ holds only opus_bench.rs, which has no libopus arm, and the libopus 1.6.1 source tree and tests/\*.c are gitignored. Not A without public comparison code and C build flags.
- **Verifier notes:** Numbers match the README exactly (the record omitted the 16 kHz/20 ms rows, now added). Confirmed the missing C bench: benches/opus_vs_c_bench.rs and benches/opus_vs_c_real.rs return 404, and the C sources are gitignored. language already reads Rust; verify.py apply ignores the language key, so it is set here only for the record. Lead: Remade-With-Rust/rusty-opus, a fork with AVX2 SILK kernels, claims 1.50x libopus on CELT speech per core (seen in the remade_ffmpeg_rs README); it would need its own record or a duplicate decision.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/Cargo.toml>
  - <https://github.com/restsend/opus-rs>
  - <https://github.com/restsend/opus-rs/tree/main/benches>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/benches/opus_bench.rs>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/bench_quick.sh>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/.gitignore>
  - <https://github.com/restsend/opus-rs/commits/main>
  - <https://github.com/restsend/opus-rs/commits/main/benches>
  - <https://crates.io/api/v1/crates/opus-rs>
  - <https://static.crates.io/crates/opus-rs/opus-rs-0.1.17.crate>
- **Sources the enricher read:**
  - <https://github.com/restsend/opus-rs>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/bench_quick.sh>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/benches/opus_bench.rs>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/src/pvq.rs>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/src/compat.rs>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/src/celt.rs>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/tests/c_interop_diff.rs>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/tests/oracle_celt.rs>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/tests/verify_pvq_match.rs>
  - <https://github.com/restsend/opus-rs/tree/main/src>
  - <https://github.com/restsend/opus-rs/tree/main/tests>
  - <https://github.com/restsend/opus-rs/commits/main>
  - <https://github.com/restsend/opus-rs/issues?q=is%3Aissue>
  - <https://github.com/restsend/opus-rs/pulls?q=is%3Apr>
  - <https://github.com/restsend/opus-rs/issues/18>
  - <https://github.com/restsend/opus-rs/issues/20>
  - <https://github.com/restsend/opus-rs/issues/30>
  - <https://github.com/restsend/opus-rs/issues/37>
  - <https://raw.githubusercontent.com/xiph/opus/v1.6.1/src/opus_encoder.c>
  - <https://crates.io/api/v1/crates/opus-rs>
  - <https://crates.io/api/v1/crates/opus-rs/0.1.34>
  - <https://crates.io/api/v1/crates/opus/0.3.0/dependencies>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/restsend/opus-rs`) · [data/wave10/enrich/raw/github_com_restsend_opus_rs.json](../../../data/wave10/enrich/raw/github_com_restsend_opus_rs.json) (enrichment confidence 0.75)

</details>
