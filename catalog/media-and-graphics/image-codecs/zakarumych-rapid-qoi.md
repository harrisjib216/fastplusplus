# rapid-qoi

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Safe no_std Rust QOI encoder/decoder; decodes about 6% faster than the qoi crate but encodes about 14% slower.

| | |
|---|---|
| **Beats** | Two different QOI implementations, both already listed, and neither the category baseline: the README 'qoi' row is the phoboslab/qoi reference C implementation run through its own qoibench.c with --nopng (benches/m1/reference.md and benches/intel-msvc/reference.md carry qoibench.c's exact output format, with the 'rate' column and 'Grand total' line), measured in a separate run from the rapid_qoi row; the repo's Rust harness bench/src/main.rs compares rapid_qoi against the qoi crate 0.4 (aldanor/qoi-rust). Not libpng, libjpeg-turbo, libwebp or libavif. |
| **Claimed result** | README grand totals (ms, qoi vs rapid_qoi), where the 'qoi' row is the reference C qoibench run and the rapid_qoi row a separate Rust-harness run: Intel i9 decode 2.009 vs 1.404 and encode 2.706 vs 2.520; Apple M1 decode 1.676 vs 1.100 and encode 2.088 vs 1.836 (cross-harness ratios 1.43x/1.07x on i9 and 1.52x/1.14x on M1, derived from page data). The only same-run comparison, benches/m1/rapid.md (Rust harness, qoi crate vs rapid_qoi, 1 timed run): decode 1.161 vs 1.100 ms (rapid_qoi 1.06x faster) and encode 1.614 vs 1.836 ms (rapid_qoi 0.88x, about 14 percent slower), all derived from page data; rapid_qoi decodes faster in 12 of 13 image directories and encodes slower than the qoi crate in all 13. The README i9 rapid_qoi row (1.404/2.520 ms) is not in benches/intel-msvc/rapid.md, which reads 1.447/2.582 ms (1.39x decode, 1.05x encode vs the reference row, derived from page data). README text: 'one of the most efficient implementations of QOI encoder and decoder'. |
| **Workload** | Whole-image in-memory QOI encode and decode of RGBA pixels from the qoi_benchmark_suite PNGs, averaged per image and totalled over the suite. Rust harness (bench/src/main.rs): images loaded with the image crate, input stream encoded by rapid_qoi, one untimed warm-up call then N timed runs per library (M1 file: 1 run; Intel file: 5 runs), results dropped without black_box. Reference rows: phoboslab qoibench.c --nopng, 5 runs. The M1 Rust run skipped 2 screenshot_game PNGs that the image crate could not decode (CRC error, bad keyword), so the README's M1 rows average slightly different image sets. |
| **Metric** | throughput |
| **Hardware** | 'Intel i9' (exact model not stated) and 'Apple M1' |
| **Compiler and flags** | rapid_qoi rows: 'cargo run --release -p bench -- [iterations] [path]' (Rust release profile); rustc version and flags not stated; the Intel results folder is named benches/intel-msvc (Windows MSVC toolchain implied). Reference qoi rows: phoboslab qoibench.c; compiler and flags not stated (MSVC implied on Intel by the folder name, which would also handicap the C baseline against LLVM-built Rust). |
| **Adoption** | 100 stars, 3 forks; crates.io 4,539,514 all-time downloads (201,344 recent), latest version 0.6.3 |
| **Last commit** | 2026-08-26 |
| **Links** | [repository](https://github.com/zakarumych/rapid-qoi) · [benchmark](https://github.com/zakarumych/rapid-qoi) |

## Verdict

The README headline (decode 1.43x faster on an unnamed Intel i9 and 1.52x on an Apple M1) compares a Rust-harness rapid_qoi run against a separate run of phoboslab's C qoibench.c. On M1 the qoi crate alone in that same Rust harness already decodes 1.44x faster than the C row (1.161 vs 1.676 ms, derived from page data), so most of the headline gap is harness and implementation-language difference, not rapid-qoi-specific. The only same-run comparison (benches/m1/rapid.md, 1 timed run per image, RGBA, qoi_benchmark_suite minus 2 PNGs the image crate rejects) shows decode 1.100 vs 1.161 ms (1.06x) and encode 1.836 vs 1.614 ms (0.88x) against the qoi crate 0.4, with rustc version, flags and the i9 model unstated.

## Use it when

- Rust projects, including no_std or embedded targets, that need a tiny dependency-free QOI codec with no unsafe code.
- Decode-heavy workloads (asset loading of QOI files you produced yourself), where the only same-run measurement shows it about 6% faster than the qoi crate on an Apple M1 and faster in 12 of 13 suite directories.
- Row-by-row or tiled decode into a fixed buffer via `decode_range`, now that the June 2026 fix (PR #14) carries a QOI_OP_RUN across call boundaries instead of panicking.
- Builds where compile time matters: the crate is three source files with no dependencies since 0.6.3.

## Skip it when

- C++ projects: it is a Rust crate with no C API; use qoi.h or qoixx instead.
- Encode-heavy workloads: in the same-run M1 benchmark the qoi crate encodes about 14% faster overall and faster in all 13 directories.
- Decoding QOI files from arbitrary third-party encoders where spec conformance matters: the decoder does not add the pixel to the colour index after QOI_OP_RUN (open issue #11 from the QOI author, linked to phoboslab/qoi#258 and its edgecase.qoi), so a stream that starts with a run and later indexes slot 53 decodes as transparent instead of opaque black.
- Projects pinned to a Rust toolchain older than 1.88: 0.6.3 uses `slice::as_chunks`/`as_chunks_mut` (stabilised in Rust 1.88.0, 2025-06-26) after the bytemuck removal, but Cargo.toml declares no rust-version, so a `^0.6` requirement breaks on update for older compilers.
- Anything needing std::io streaming, channel conversion on decode, more than 8 bits per channel, or better compression than PNG.

## How it is fast

The decoder is a single loop that pattern-matches slice heads on the opcode byte ranges (INDEX, DIFF, LUMA, RGB, RGBA, RUN) and fills runs with `slice::fill` instead of per-pixel writes, with no per-byte bounds checks beyond the slice patterns. The colour-index hash (r\*3+g\*5+b\*7+a\*11 mod 64) is computed with one 64-bit multiply over a masked, duplicated pixel word (the 'hardqoi' bit hack merged in January 2026, which saves an AND; I checked it against the spec formula on 200,000 random pixels with no mismatch). The encoder replaces a run of exactly one with a QOI_OP_INDEX to the previous pixel (same size, slightly cheaper to decode), and the decoder skips the index write after INDEX and RUN chunks that qoi.h performs on every chunk.

## Compared with alternatives

Pick it over qoi (qoi-rust) only when decode speed matters more than encode speed and you control the encoder, or want the smallest dependency-free no_std crate; qoi-rust encodes faster in the same run, offers std::io streaming, declares MSRV 1.62, and is fuzz- and round-trip-tested. For C or C++ callers, qoixx or the reference qoi.h (or qoi-asm on x86-64-v3) are the relevant siblings, since rapid-qoi has no C API.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none in 0.6.3 (0.6.1 depended on bytemuck 1.x) |
| **Minimum toolchain** | Rust 1.88 for 0.6.3 (uses slice::as_chunks; not declared in Cargo.toml); edition 2018 |
| **Platforms** | any (portable scalar Rust; no SIMD; the hash constant goes through to_le() so it is endian-correct) |
| **Thread safety** | not documented; the functions keep no global state and work only on caller-supplied buffers and state |
| **Drop-in for the baseline** | partial: it reads and writes the same QOI format as qoi.h and the qoi crate (same output sizes in the bench), but its API differs and its decoder diverges from the spec on the leading-QOI_OP_RUN edge case |

## Gotchas

- Correctness bug in the release most users have: crates.io 0.6.1 (2022-02-18, 4,520,345 of the crate's roughly 4.54 million downloads) encodes 3-channel RGB images incorrectly. Its RGB encoder kept a 3-byte colour index zero-filled at start, so the first pure-black pixel matched an empty slot and was written as QOI_OP_INDEX, which a spec decoder reads as transparent black; that is my reading of the f4f1537 diff. Issue #6 (2022-02-20, still open, no maintainer reply) lists over 140 suite images where reference decoding of rapid-qoi output differs. The fix (f4f1537, 'Use 4 channel index for all cases', 2022-05-28, version 0.6.2) was never published; it first reached crates.io in 0.6.3 on 2026-08-26. The benchmark converts every image to RGBA with to_rgba8, so the published timings exercise the unaffected 4-channel path.
- The 3-channel decoder discards the alpha byte of QOI_OP_RGBA chunks and hashes pixels with alpha 255, while qoi.h keeps alpha internally whatever channel count is requested. A 3-channel file containing RGBA chunks with alpha below 255 could therefore resolve later QOI_OP_INDEX chunks differently. This comes from reading the source and was not tested.
- Testing is thin. The only test is tests/run_at_edge.rs (the #13 regression), and CI runs `cargo test` only. validate.sh, a round-trip check against the reference qoiconv, covers only the screenshot_game directory and is not wired into CI. The crate has no fuzzing, unlike the qoi crate, which is round-trip-tested against the C reference and fuzz-tested.
- The `io` feature in Cargo.toml has no code behind it, and decode always outputs the header's channel count.

## Known shortcomings

- The README headline (1.43x/1.52x) splices two harnesses: its 'qoi' row is phoboslab's qoibench.c --nopng output, not the qoi crate, while the same-run benches/m1/rapid.md against the qoi crate shows decode only 1.06x faster and encode 0.88x (slower in all 13 directories); the i9 README row is not in intel-msvc/rapid.md (1.447/2.582). An independent safe-Rust implementation rather than a qoi-rust port (kept); the 2026-06-29 clamp fix affects only chunked decode_range; 4.5M crates.io downloads.
- Enricher (e126, 2026-10-05): correctness bug in crates.io 0.6.1 (4,520,345 of about 4.54M downloads): the RGB encoder used a 3-byte zero-initialised index and wrote invalid streams (issue #6 still open, 140+ suite images fail); the fix f4f1537 (0.6.2, 2022-05) was never published and the first fixed release, 0.6.3, shipped on 2026-08-26. The bench uses to_rgba8, so the timed numbers are unaffected. The decoder skips the index write after QOI_OP_RUN and fails phoboslab's edgecase.qoi (issue #11 open). The bench files (2021-12 to 2022-02) predate the inverted-unlikely fix c5359a5 (2022-09) and the 2026 hash change, so no number describes 0.6.3. In the same Rust harness the qoi crate alone is 1.44x faster than the C qoibench row (derived), so the README headline is mostly harness gap. 0.6.3 needs Rust 1.88 (as_chunks) with no rust-version declared.

## Caveats and trade-offs

Off-baseline: compares only against other QOI implementations (phoboslab/qoi C reference and the qoi crate, both already listed), so it says nothing about libpng, libjpeg-turbo, libwebp or libavif. Mixed result: the README's headline rows splice a reference qoibench.c run (5 runs) with a separate Rust-harness run (M1: 1 run), and the i9 rapid_qoi row matches no checked-in result file. In the same-run M1 file the qoi crate (aldanor/qoi-rust) encodes about 14 percent faster than rapid_qoi in aggregate and in every one of 13 directories, while rapid_qoi decodes about 6 percent faster; qoi-rust's own README says it was the fastest Rust QOI implementation 'by a noticeable margin'. The Intel i9 model, rustc version and C compiler for the reference rows are not stated. The benchmark numbers date from 2021-2022 and predate the 2026-01-16 'Apply bit hack optimisation from hardqoi' and follow-up correctness commit; the 2026-06-29 fix (clamp QOI_OP_RUN split, commit 1900bc3) only affects chunked decode_range calls that panicked, not the whole-image decode the benchmark times. Lineage: an independent safe-Rust (forbid(unsafe_code), no_std) implementation of the QOI format; it reproduces the qoi.h spec text in its docs but does not derive from qoi-rust, so it is not a wrapper or port.

no_std and no unsafe, tiny crate (0.8 s clean build on an i9, per README). Rust crate only; no C API or C bindings found, so it is not callable from C++ without writing a wrapper. QOI itself compresses worse than PNG and is limited to 8-bit RGB/RGBA.

## Maintenance

Lightly maintained: the 2026 commits are contributor PRs (hash bit hack, run-clamp fix) plus a bytemuck removal, and 0.6.3 shipped on 2026-08-26, but correctness issues #6 and #11 have stayed open since 2022-2023 without a reply. The published benchmark files date from December 2021 to February 2022 and predate the September 2022 fix of an inverted `unlikely` branch hint (c5359a5) and the 2026 hash change, so no published number describes 0.6.3. MIT OR Apache-2.0, small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party numbers: bench/src/main.rs and the result files in benches/ are public, but the rustc version, flags and the exact Intel i9 model are not stated, and the README rows splice two different harnesses (the reference C qoibench.c for the 'qoi' row, the Rust bench for the 'rapid_qoi' row), so it is C. Tier unchanged from the record; verdict is downgrade because the headline 1.43x/1.52x decode claim is a cross-harness comparison and the only same-run comparison (benches/m1/rapid.md) shows rapid_qoi slower than the qoi crate at encoding.
- **Verifier notes:** Keep as its own entry (independent Rust implementation, not a port of qoi-rust) with the mixed-result and off-baseline shortcomings recorded. The record misidentified the README 'qoi' row as the qoi crate; reference.md files are phoboslab qoibench.c output, so the README headline is rapid_qoi vs the C reference across two harnesses, while the same-run comparison against the listed qoi crate shows faster decode but slower encode. Last commit 2026-08-26 ('Remove bytemuck') confirmed; default branch master.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party Rust harness
- **Pages the verifier opened:**
  - <https://github.com/zakarumych/rapid-qoi>
  - <https://github.com/zakarumych/rapid-qoi/commits>
  - <https://github.com/zakarumych/rapid-qoi/commits/master>
  - <https://github.com/zakarumych/rapid-qoi/commit/1900bc3b0322f1af0ad333645307e61e02e407b3>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/README.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/COPYING>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/bench/src/main.rs>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/benches/m1/rapid.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/benches/m1/reference.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/benches/intel-msvc/rapid.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/benches/intel-msvc/reference.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/src/decode.rs>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/src/encode.rs>
  - <https://raw.githubusercontent.com/phoboslab/qoi/master/qoibench.c>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/README.md>
  - <https://crates.io/api/v1/crates/rapid-qoi>
- **Sources the enricher read:**
  - <https://github.com/zakarumych/rapid-qoi>
  - <https://github.com/zakarumych/rapid-qoi/commits/master>
  - <https://github.com/zakarumych/rapid-qoi/commits/master/benches>
  - <https://github.com/zakarumych/rapid-qoi/issues?q=is%3Aissue>
  - <https://github.com/zakarumych/rapid-qoi/pulls?q=is%3Apr>
  - <https://github.com/zakarumych/rapid-qoi/issues/6>
  - <https://github.com/zakarumych/rapid-qoi/issues/10>
  - <https://github.com/zakarumych/rapid-qoi/issues/11>
  - <https://github.com/zakarumych/rapid-qoi/issues/13>
  - <https://github.com/zakarumych/rapid-qoi/pull/12>
  - <https://github.com/zakarumych/rapid-qoi/commit/f4f1537>
  - <https://github.com/zakarumych/rapid-qoi/commit/df9b52a>
  - <https://github.com/zakarumych/rapid-qoi/commit/c5359a5>
  - <https://github.com/zakarumych/rapid-qoi/tree/master/tests>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/README.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/bench/src/main.rs>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/benches/m1/rapid.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/benches/m1/reference.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/benches/intel-msvc/rapid.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/benches/intel-msvc/reference.md>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/src/decode.rs>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/src/encode.rs>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/qoiconv/src/main.rs>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/validate.sh>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/tests/run_at_edge.rs>
  - <https://raw.githubusercontent.com/zakarumych/rapid-qoi/HEAD/.github/workflows/badge.yml>
  - <https://crates.io/api/v1/crates/rapid-qoi/versions>
  - <https://crates.io/api/v1/crates/rapid-qoi/reverse_dependencies>
  - <https://crates.io/api/v1/crates/rapid-qoi/0.6.1/download>
  - <https://github.com/phoboslab/qoi/issues/258>
  - <https://raw.githubusercontent.com/phoboslab/qoi/master/qoi.h>
  - <https://raw.githubusercontent.com/aldanor/qoi-rust/HEAD/README.md>
  - <https://raw.githubusercontent.com/rust-lang/rust/master/RELEASES.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/zakarumych/rapid-qoi`) · [data/wave10/enrich/raw/github_com_zakarumych_rapid_qoi.json](../../../data/wave10/enrich/raw/github_com_zakarumych_rapid_qoi.json) (enrichment confidence 0.8)

</details>
