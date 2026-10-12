# simdutf8

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> SIMD-accelerated UTF-8 validator for Rust, a drop-in replacement for std::str::from_utf8, up to 23x faster.

| | |
|---|---|
| **Beats** | Rust std::str::from_utf8 (also compared against simdjson's UTF-8 validator) |
| **Claimed result** | Up to 23x faster than the std library on valid non-ASCII, up to 4x faster on ASCII (x86-64 Zen2); up to 11x faster than std on non-ASCII, up to 4x on ASCII (Apple M1/aarch64); 'faster than simdjson on almost all inputs' |
| **Workload** | UTF-8 validation of valid/invalid ASCII and non-ASCII byte buffers (incl. a 64KiB error case) using criterion benchmarks |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 PRO 3700 (Zen2), Linux x86-64; Apple M1 (aarch64), macOS |
| **Compiler and flags** | Rust 1.52.0 (x86-64), rustc 1.54.0-nightly 881c1ac40 2021-05-08 (aarch64); default `cargo bench` optimized bench profile (no profile overrides in bench/Cargo.toml); no RUSTFLAGS stated |
| **Adoption** | 604 stars |
| **Last commit** | 2026-06-15 |
| **Links** | [repository](https://github.com/rusticstuff/simdutf8) · [benchmark](https://github.com/rusticstuff/simdutf8#benchmarks) |

## Verdict

On an AMD Ryzen 7 PRO 3700 (Zen2, Linux, Rust 1.52.0, default cargo bench profile), simdutf8's basic API validated valid non-ASCII UTF-8 up to 23x faster than std::str::from_utf8 and pure ASCII up to 4x faster; on an Apple M1 (aarch64, rustc 1.54.0-nightly) it was up to 11x faster on non-ASCII and up to 4x on ASCII. It was also faster than simdjson's own UTF-8 validator (simdutf8 built with #[inline(never)] for that comparison) on almost all tested inputs.

## Use it when

- Validating large buffers (well over 64 bytes) of UTF-8, especially non-ASCII text, where the current bottleneck is std::str::from_utf8
- Parsers or ingestion pipelines that mostly see valid or mostly-valid UTF-8 and want the fastest possible check before trusting the bytes
- Rust targets with SIMD support: x86/x86-64 (SSE4.2/AVX2/AVX-512), aarch64, wasm32, or armv7 on nightly
- no_std/embedded projects that can pick a target CPU feature at compile time via RUSTFLAGS
- Cases needing detailed error position on failure via the `compat` API instead of hand-rolled validation

## Skip it when

- Buffers routinely under 64 bytes — simdutf8 just forwards these to std::str::from_utf8, so there's no win and only added dependency weight
- Platforms without any of the supported SIMD extensions — it silently falls back to std with no speedup
- You need every from_utf8 call to also report the exact invalid byte position at basic-API speed — that requires the slightly slower `compat` flavor
- AltiVec/PowerPC targets — SIMD support there is an open feature request (issue #110), not implemented
- Taking the README's 23x/11x numbers at face value for today's stack — they're from 2021 (simdutf8 v0.1.2, Rust 1.52/1.54-nightly, simdjson v0.9.2) and haven't been re-run against current std or crate versions

## How it is fast

It ports simdjson's SIMD UTF-8 validation algorithm (Keiser & Lemire, 'Validating UTF-8 In Less Than One Instruction Per Byte') to Rust, with its own added ASCII fast path and x86 prefetching. At runtime on x86 it dispatches to the best available instruction set (AVX-512, AVX2, or SSE4.2) via `is_x86_feature_detected!`; aarch64/NEON, armv7/NEON and wasm32 simd128 are also supported, with SIMD chosen at compile time on those. Inputs under 64 bytes are simply handed to `core::str::from_utf8()` instead of invoking SIMD. The `basic` API further speeds things up by only checking the aggregated error state once at the end rather than per-block.

## Compared with alternatives

The other same-category entries (xutf, SimdUnicode, Parabix, utf8_range) beat C++/.NET/bitstream validators, not Rust's std — pick simdutf8 when you're writing Rust and want an actual crate that's near-drop-in for std::str::from_utf8. If your real target is beating simdutf (C++) specifically, simdutf8's own maintainers haven't benchmarked that comparison (open issue #54); look at xutf or SimdUnicode instead.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | flexpect (runtime, used internally); rustversion (build-dependency) |
| **Minimum toolchain** | MSRV 1.38.0 for the crate itself; aarch64 NEON needs Rust 1.61+, AVX-512 needs Rust 1.89+, armv7 NEON needs nightly |
| **Platforms** | x86/x86-64 (SSE4.2, AVX2, AVX-512), aarch64, armv7 (nightly, feature-gated), wasm32 (simd128), falls back to core::str::from_utf8 elsewhere |
| **Thread safety** | not documented explicitly; the validation functions are pure and stateless (no shared mutable state), so concurrent calls are safe |
| **Drop-in for the baseline** | partial — explain: basic::from_utf8 matches std's Ok(&str) return but its error type carries no position; compat::from_utf8 is a full drop-in including error details, at a small speed cost versus basic |

## Gotchas

- Building with opt-level = "z" disables inlining and makes it noticeably slower — the README explicitly warns against it
- no_std builds pick the SIMD implementation at compile time, not runtime, so you must set RUSTFLAGS (e.g. target-feature=+avx2 or +neon) to get anything faster than the fallback
- Internals use unsafe SIMD intrinsics; the project says it's fuzzed and has 'no known bugs' but that's a maintainer claim, not a formal audit
- AVX-512 is only auto-selected on CPUs supporting VBMI2 (Ice Lake+) to avoid the frequency throttling older AVX-512 CPUs incur

## Caveats and trade-offs

The benchmark numbers are from 2021 (simdutf8 v0.1.2, simdjson v0.9.2, Rust 1.52/1.54-nightly) and may not reflect current std or crate versions. For the simdjson comparison, simdutf8 was compiled with #[inline(never)]. It is not benchmarked against simdutf (C++) or ICU, only against Rust std::str::from_utf8 and simdjson's validator.

Requires unsafe SIMD intrinsics internally; 'basic' API omits error position (use 'compat' API for that, at a small perf cost); runtime CPU-feature dispatch adds a small branch.

## Maintenance

Actively maintained (last default-branch commit 2026-06-15, v0.1.5 on crates.io) under MIT OR Apache-2.0; adds as an ordinary Cargo dependency, no vendoring needed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Benchmarks section states 'up to 23 times faster than the std library on valid non-ASCII, up to four times on pure ASCII' (Zen2) and 'up to eleven times... up to four times' (M1). The public criterion code is bench/benches/throughput_std.rs vs throughput_basic.rs, and raw baselines are saved in bench/baselines/. The toolchains (Rust 1.52.0; 1.54.0-nightly 2021-05-08) and CPUs (Ryzen 7 PRO 3700, Apple M1) are stated. The flags are the default `cargo bench` profile; bench/Cargo.toml has no profile overrides.
- **Verifier notes:** The claims match the README text exactly. The license is MIT OR Apache-2.0 per Cargo.toml, LICENSE-MIT and LICENSE-Apache (GitHub reports NOASSERTION). The last default-branch commit is 2026-06-15; the record's 2026-06-22 was the pushed_at date.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rusticstuff/simdutf8>
  - <https://github.com/rusticstuff/simdutf8#benchmarks>
  - <https://github.com/rusticstuff/simdutf8/blob/main/bench/BENCHMARKING.md>
  - <https://github.com/rusticstuff/simdutf8/blob/main/bench/Cargo.toml>
  - <https://github.com/rusticstuff/simdutf8/blob/main/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/rusticstuff/simdutf8>
  - <https://github.com/rusticstuff/simdutf8#benchmarks>
  - <https://github.com/rusticstuff/simdutf8/blob/main/Cargo.toml>
  - <https://github.com/rusticstuff/simdutf8/blob/main/src/lib.rs>
  - <https://github.com/rusticstuff/simdutf8/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/rusticstuff/simdutf8`) · [data/wave3/enrich/raw/github_com_rusticstuff_simdutf8.json](../../../data/wave3/enrich/raw/github_com_rusticstuff_simdutf8.json) (enrichment confidence 0.75)

</details>
