# simd-adler32

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust Adler-32 with runtime-dispatched SSE2/SSSE3/AVX2 (AVX-512 on nightly) and NEON kernels; 17-23x the adler32 crate on x86.

| | |
|---|---|
| **Beats** | adler/adler2 crates (scalar Rust Adler-32; adler2 is the maintained successor used by miniz_oxide) and adler32 crate, plus wuffs std/adler32 built with gcc |
| **Claimed result** | README, i5-8300H Windows 10: 10k simd-adler32 212.61 ns (43.805 GiB/s) vs adler32 4.8084 us (1.9369 GiB/s, 22.6x derived from page data) vs adler 17.979 us (530.43 MiB/s, 84.6x derived) vs wuffs 3843 ns (2.63 GiB/s, 16.7x derived); 100k 33.320 GiB/s vs adler32 1.9207 GiB/s (17.3x derived). i9-9880H macOS 10k: 46.480 GiB/s vs adler32 2.2433 GiB/s (20.7x derived). Apple M3 Pro 10k: 37.090 GiB/s vs adler32 3.3894 GiB/s (10.9x derived) vs adler2 6.1280 GiB/s (6.1x derived). |
| **Workload** | Adler-32 checksum of 10k and 100k random bytes, criterion, crate versus adler, adler32, adler2 and wuffs. |
| **Metric** | throughput |
| **Hardware** | Intel i5-8300H @ 2.30GHz (Windows 10 Pro), MacBookPro16,1 Intel i9-9880H @ 2.30GHz, MacBook Pro 14 Apple M3 Pro |
| **Compiler and flags** | criterion 0.3 benches (bench/alts.rs; the older bench/compete.rs produced the adler rows); Cargo.toml [profile.release] opt-level = 2, debug = true, inherited by cargo bench; rustc version and RUSTFLAGS not stated (runtime CPU feature detection, so no target-cpu needed); wuffs row ran as 'wuffs bench -ccompilers=gcc -reps=1 -iterscale=300 std/adler32' under mingw64 |
| **Adoption** | 49 stars; crates.io simd-adler32 439,768,193 downloads (161,755,577 recent) as of 2026-10-11 |
| **Last commit** | 2026-07-14 |
| **Links** | [repository](https://github.com/mcountryman/simd-adler32) · [benchmark](https://github.com/mcountryman/simd-adler32) |

## Verdict

Author-run criterion benchmarks (opt-level 2, rustc version unstated) on random 10 KB and 100 KB buffers: on an i5-8300H under Windows 10, AVX2 simd-adler32 ran 212.61 ns per 10 KB (43.8 GiB/s) against 4.81 us for the adler32 crate (22.6x) and 17.98 us for adler 1.0.2; on an i9-9880H Mac it ran about 20x faster than adler32; on an Apple M3 Pro the NEON kernel reached 37.1 GiB/s against adler2's 6.1 GiB/s (6.1x). All figures are first-party.

## Use it when

- Hashing zlib/PNG payloads or other buffers of kilobytes and up in Rust: 43.8 GiB/s on 10 KB and 33.3 GiB/s on 100 KB (i5-8300H, AVX2) versus about 1.9 GiB/s for the adler32 crate.
- Apple Silicon or other aarch64 targets on 0.3.9 or later: the NEON kernel reached 37 GiB/s on an M3 Pro versus 6.1 GiB/s for adler2 (about 6x, derived from page data).
- Portable binaries that must not assume a CPU: with the default std feature the x86 kernel is picked at runtime by is_x86_feature_detected!, so no target-cpu flag is needed.
- You already depend on fdeflate, or on miniz_oxide or zune-inflate with their optional SIMD Adler-32 dependency (crates.io reverse dependencies), and want the same checksum elsewhere in the program.

## Skip it when

- Tiny inputs: every Adler32::new() runs the feature-detection chain and each write is an indirect call; alts.rs and variants.rs also time 10-byte inputs, but the README publishes no small-input numbers, so the win below about 1 KB is not documented.
- Stable Rust on AVX-512 hardware expecting AVX-512: that kernel is compiled only with the crate's nightly feature, so stable builds top out at AVX2.
- no_std, wasm32 or 32-bit ARM builds without explicit target features: there is no runtime detection there, so you get the scalar loop unless you pass -C target-feature (+avx2, +simd128, neon; 32-bit ARM NEON also needs the nightly feature).
- Codebases that forbid unsafe dependencies: every SIMD kernel is unsafe intrinsics code, and a 2023 release (0.3.5) had a misaligned-pointer dereference in the wasm kernel (issue #11, fixed in 0.3.6).
- When you need CRC-32 rather than Adler-32 (gzip, zip): this crate only does Adler-32.

## How it is fast

Data is processed in chunks of 5,536 bytes (the largest multiple of 32 below zlib's NMAX of 5,552), so the expensive modulo 65521 runs once per chunk instead of per byte. Inside a chunk each 32-byte block costs a handful of vector ops: _mm256_sad_epu8 against zero sums the bytes for A, _mm256_maddubs_epi16 with descending weights 32..1 followed by _mm256_madd_epi16 builds the weighted sum for B, and a running prefix vector, shifted left by 5 at the end, adds the 32\*A carry, the vectorised scheme from Chromium's zlib adler32_simd.c that the NEON port cites directly. The kernel is chosen once per hasher through a function pointer (AVX-512, NEON, AVX2, SSSE3, SSE2, wasm simd128, then scalar).

## Compared with alternatives

No other entry in this category computes checksums; simd-adler32 uses the same runtime-dispatch pattern as the memchr and argminmax crates, applied to Adler-32. Pick it when you want a standalone pure-Rust Adler-32. The C deflate libraries catalogued under general-lossless (zlib-ng, libdeflate) carry their own SIMD Adler-32 if you are already linking C.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (rand and criterion are dev-only; adler2 and adler32 are dev-only comparison crates) |
| **Minimum toolchain** | README and CI: rustc 1.36.0 with default-features = false, features = ["std"]; the default const-generics feature needs rustc 1.51; edition 2018; the AVX-512 kernel needs a nightly compiler plus the nightly feature |
| **Platforms** | x86 and x86_64 (SSE2, SSSE3, AVX2 by runtime detection; AVX-512F+BW on nightly), aarch64 NEON (always on), 32-bit ARM NEON (nightly feature or target_feature, fixed in 0.3.10), wasm32 simd128 (compile-time flag only), scalar fallback everywhere else including no_std |
| **Thread safety** | not documented; Adler32 is a plain value (two u16 and a fn pointer) with no shared state, so separate hashers can run on separate threads |
| **Drop-in for the baseline** | partial: same checksum values as adler2/adler32 (tests compare against adler2), but different type and method names |

## Gotchas

- Benchmark caveats behind the README tables: the x86 rows came from the older bench/compete.rs against adler 1.0.2 and adler32 1.2.0, and the headline 85x is against the slow adler 1.0.2 crate; the fair ratio is about 17-23x against adler32 and about 6x against adler2 (M3 Pro, the only table with adler2). The macOS 100k/adler row prints 534.69 MiB/s, but 83.776 us for 100,000 bytes is about 1,138 MiB/s (copied from the Windows table). The wuffs row ran through wuffs' own harness under mingw64 gcc. No rustc version is given, and Cargo.toml's opt-level = 2 release profile also applies to the baselines. The criterion harness itself is symmetric (one random buffer per run, results black-boxed); I found no correctness flaw behind the numbers.
- Documentation drift: README and docs.rs still say 'currently only x86 and x86_64'; the crate-level docs.rs table marks NEON as in progress and wasm as unsupported while the README table ticks both; the README credits afl fuzzing while CI runs cargo-fuzz for 30 minutes per target.
- finish() does not reset the state; call reset() or build a new hasher, otherwise later writes keep extending the previous checksum.
- from_checksum() splits any u32 into the A and B halves without checking that they are below 65521; tests cover it against adler2, but feeding a value that is not a valid Adler-32 state is not documented.

## Known shortcomings

- No rustc version (opt-level 2 from Cargo.toml); the 85x headline is against the slow old adler 1.0.2 crate, fair figures are about 17-23x vs adler32 and about 6x vs adler2 on an M3 Pro; the macOS 100k/adler throughput cell is a copy error (1138 MiB/s, not 534.69); the Wuffs row comes from another harness.
- AVX2 and NEON kernels read: overflow bounds and the modulo per 5,536-byte chunk are correct; the criterion harness is symmetric; no correctness flaw found. Known caveats confirmed: 85x is vs adler 1.0.2, the fair ratio is 17-23x vs adler32 and about 6x vs adler2 (M3 Pro); the macOS 100k/adler row is a copy error. The AVX-512 kernel needs the nightly feature; no_std, wasm32 and 32-bit ARM paths are selected by compile-time flags only; README and docs.rs platform tables are out of date; 10-byte inputs are timed but not published; wasm misaligned-pointer UB (issue #11, 0.3.5) fixed in 0.3.6. About 441M downloads via fdeflate, miniz_oxide and zune-inflate.

## Caveats and trade-offs

rustc version not stated. The 85x figure is against the old adler 1.0.2 crate at opt-level 2, which ran slower than adler32 in the same table; the fairer incumbent ratios are about 17-23x versus adler32 on x86 and about 6x versus adler2 on Apple M3 Pro (derived from page data). The wuffs row ran through a different harness (gcc under mingw64). The macOS 100k/adler row is internally inconsistent: 83.776 us for 100,000 bytes is about 1138 MiB/s, but the table prints 534.69 MiB/s (copied from the Windows table). The x86 tables predate the May 2026 switch of the benches from adler to adler2. Heavy use of unsafe SIMD code, fuzzed with afl before release. Arguably a checksum library rather than a general SIMD intrinsics library.

Runtime detection of SSE2, SSSE3, AVX2, AVX-512 and NEON, with scalar fallback; unsafe-heavy, fuzzed with afl; no_std supported.

## Maintenance

Actively maintained (0.3.10 published 2026-07-14, NEON kernel added and ARM build fixes merged March-May 2026, CI on x86/aarch64/ARM with miri and fuzzing), MIT-licensed with about 441M crates.io downloads, mostly through fdeflate and optional deps of miniz_oxide and zune-inflate; safe to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party criterion tables in the README with CPU models; benchmark code is public (bench/alts.rs now, bench/compete.rs when the adler rows were measured) and the opt-level comes from Cargo.toml, but the rustc version is never stated, so not A.
- **Verifier notes:** All quoted numbers are on the README; criterion harness is symmetric (same random buffer, result black-boxed). Shortcomings to record: no rustc version, 85x ratio is against a slow old adler crate (6x versus adler2 on M3 Pro is the fair incumbent figure), one copy error in the macOS 100k/adler throughput, wuffs row from a different harness. Very widely used despite 49 stars (about 440M crates.io downloads).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-59 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/mcountryman/simd-adler32>
  - <https://github.com/mcountryman/simd-adler32/commits>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/README.md>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/bench/alts.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/bench/variants.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/036b941/bench/compete.rs>
  - <https://crates.io/api/v1/crates/simd-adler32>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/036b941/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/mcountryman/simd-adler32>
  - <https://github.com/mcountryman/simd-adler32/commits/main>
  - <https://github.com/mcountryman/simd-adler32/issues?q=is%3Aissue>
  - <https://github.com/mcountryman/simd-adler32/issues/11>
  - <https://github.com/mcountryman/simd-adler32/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/README.md>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/bench/alts.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/bench/variants.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/hash.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/imp/mod.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/imp/scalar.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/imp/sse2.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/imp/ssse3.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/imp/avx2.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/imp/avx512.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/imp/neon.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/src/imp/wasm.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/.github/workflows/build.yaml>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/.github/workflows/fuzz.yaml>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/HEAD/.github/workflows/publish.yaml>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/036b941/bench/compete.rs>
  - <https://raw.githubusercontent.com/mcountryman/simd-adler32/036b941/Cargo.toml>
  - <https://crates.io/api/v1/crates/simd-adler32>
  - <https://crates.io/api/v1/crates/simd-adler32/reverse_dependencies?per_page=30>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mcountryman/simd-adler32`) · [data/wave13/enrich/raw/github_com_mcountryman_simd_adler32.json](../../../data/wave13/enrich/raw/github_com_mcountryman_simd_adler32.json) (enrichment confidence 0.8)

</details>
