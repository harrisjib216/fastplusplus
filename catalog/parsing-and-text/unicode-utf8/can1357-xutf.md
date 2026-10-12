# xutf

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> SIMD Rust UTF-8/16/32 transcoder beating simdutf on most inputs, plus allocation-free grapheme/width/wrap terminal-text primitives.

| | |
|---|---|
| **Beats** | simdutf |
| **Claimed result** | Author: 'beats simdutf across nearly the entire grid, ASCII included, roughly 1.5-2x ahead on typical text, and 3-10x ahead on emoji-heavy input.' README tables (vs simdutf's validating entry points): UTF-32-&gt;UTF-8 emoji-4b 18.0 vs 4.6 GB/s (+294.0%) on Apple M4 Max and 30.5 vs 3.2 GB/s (+853.9%) on Xeon; UTF-8-&gt;UTF-16 cjk-3b 8.1 vs 6.7 GB/s (+20.1%) on Xeon and 9.7 vs 8.0 GB/s (+20.9%) on M4 Max. Across non-emoji transcoding rows the margin over simdutf ranges from -1.1% to +57.9%, below the headline 1.5-2x; the 3-10x emoji gains appear only for UTF-16/UTF-32 -&gt; UTF-8 (UTF-8 -&gt; UTF-16/32 emoji rows are +2.8% to +61.3%). |
| **Workload** | UTF-8/UTF-16/UTF-32 transcoding against simdutf (Rust `simdutf` 0.7.0 crate, C++ via FFI, validating convert_\* entry points), encoding_rs and std char iterators, plus grapheme iteration, width/truncation, word wrap and equality against Rust crates (unicode-segmentation, unicode-width, textwrap, memcmp) on \~1 MiB ascii/cjk/emoji corpora; custom best-of-7 ratio harness in benches/common.rs (optional divan mode), not criterion; Apple M4 Max and a 'Xeon x86-64' host |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max; a second host labeled only 'Xeon x86-64' (exact CPU model not given) |
| **Compiler and flags** | rustc nightly (rust-toolchain.toml channel = "nightly", exact version not pinned) via `cargo bench`, release profile lto = "thin", RUSTFLAGS="-C target-cpu=native" (scripts/bench_hosts.sh) |
| **Adoption** | 10 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/can1357/xutf) · [benchmark](https://github.com/can1357/xutf#benchmarks) |

## Verdict

Measured with a custom best-of-7 harness (not criterion; optional divan mode) on \~1 MiB ASCII/CJK/emoji corpora against the Rust `simdutf` 0.7.0 crate's validating convert_\* entry points (simdutf itself calls C++ via FFI); built with nightly rustc, release profile lto="thin", RUSTFLAGS="-C target-cpu=native", on an Apple M4 Max and a second host labeled only 'Xeon x86-64'. Non-emoji transcoding margins over simdutf range -1.1% to +57.9% (below the headline 1.5-2x), while UTF-16/32-&gt;UTF-8 on emoji input reaches +294% (M4 Max) and +854% (Xeon).

## Use it when

- Rust services doing bulk UTF-8/16/32 transcoding (log/network pipelines, file loaders) where simdutf's validating converters are the bottleneck, especially on emoji-heavy or mixed CJK+emoji text (+294% to +854% on UTF-16/32-&gt;UTF-8 emoji rows).
- Terminal/TUI code needing fast grapheme-cluster iteration, visible-width math, or width-bounded truncation/wrap without per-call allocation (3-13x over unicode-segmentation/textwrap on the README's corpora).
- Code that must decode untrusted or arbitrary bytes and can never error, rather than validating first and rejecting malformed input.
- Cross-encoding equality/ordering checks (e.g. UTF-8 buffer vs UTF-16 buffer) without an intermediate String conversion.
- Projects already on nightly Rust that can pin RUSTFLAGS="-C target-cpu=native" builds and accept a crates.io/git dependency to that toolchain.

## Skip it when

- Need strict validation with structured decode errors (reject malformed input) — xutf is permissive/lossy by design, different semantics from simdutf's validating convert_\* API.
- Need a C/C++-callable library directly — it's #![no_std] Rust with zero runtime deps, not usable from C++ without writing an FFI shim.
- Can't run nightly Rust: requires the core::simd/portable_simd feature, and rust-toolchain.toml only pins channel = "nightly" (no exact version).
- Risk-averse production use: 10 GitHub stars, no visible issue/bug history yet to judge maturity against, and the 'Xeon x86-64' benchmark host isn't identified by exact CPU model.
- Only need plain ASCII-range validation — the ASCII-only wins over simdutf are modest here (some rows within 20%, one row -1.1%), so a simpler validator may suffice.

## How it is fast

Ported from the C++ xstd branchless UTF kernel: UTF-8 is treated as a bit permutation, so one mask table drives both directions, with BMI2 pext gathering payload bits on decode and pdep scattering them on encode instead of per-codepoint branches or shuffle tables. Bulk paths use Rust's core::simd portable SIMD plus hand-written AVX-512 (src/x86.rs) and NEON (src/neon.rs) kernels. Decoding is also non-validating (never fails), removing the branchy error-checking state machine strict validators like simdutf must run.

## Compared with alternatives

Pick xutf over simdutf when you're already in pure Rust, don't need simdutf's strict validation errors, and want faster UTF-16/32&lt;-&gt;UTF-8 transcoding plus bundled grapheme/width/wrap terminal-text helpers in one crate. Pick encoding_rs instead if you need a far more battle-tested, widely-deployed transcoder or broader legacy-encoding support beyond UTF-8/16/32 (xutf's own tables show it beating encoding_rs by roughly 1.6-8x on non-ASCII).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none at runtime; #![no_std] + alloc, zero runtime dependencies (dev-dependencies only for its own benches/tests) |
| **Minimum toolchain** | Rust nightly (portable_simd feature), edition 2024; exact nightly version not pinned |
| **Platforms** | x86-64 (BMI2/AVX-512 kernels when available) and aarch64 (NEON kernels); other targets fall back to the portable core::simd path, not covered by the published benchmarks |
| **Thread safety** | not documented; the public API is pure functions/methods over slices and owned buffers with no global or interior-mutable state visible in src/lib.rs |
| **Drop-in for the baseline** | partial — explain: not drop-in for simdutf (different trait-based Rust API, no_std, non-validating decode vs simdutf's validating C++ API); the README's only explicit drop-in claim is for the utf8-chars crate's streaming BufRead-to-char interface |

## Gotchas

- Decoding never fails: truncated UTF-8 sequences, lone surrogates, and garbage bytes all decode to defined-but-lossy output (e.g. a truncated sequence decodes to codepoint 0) instead of erroring — do not use where strict validation is required.
- RUSTFLAGS="-C target-cpu=native" is required to reach the README's peak throughput numbers; a plain nightly build without it will be slower.
- UTF-16 low-surrogate encoding was deliberately changed from the original C++ xstd formula (which corrupted pairs when bit 13 of cp - 0x10000 is set, e.g. U+12000).
- simdutf's non-validating convert_valid_\* entry points are excluded from the README's comparison tables; only simdutf's validating convert_\* path is benchmarked against.

## Caveats and trade-offs

Second benchmark host is labeled only 'Xeon x86-64' (no CPU model), and the nightly toolchain version is not pinned. The headline '1.5-2x on typical text' exceeds the README tables, where non-emoji transcoding margins over simdutf are -1.1% to +57.9%; the 3-10x emoji wins apply only to UTF-16/UTF-32 -&gt; UTF-8. simdutf's validation-skipping convert_valid_\* results are measured (recorded as 'simdutf-valid' in benches/data/\*.jsonl) but excluded from the README tables. Grapheme/width/wrap/equality comparisons are against Rust crates, not simdutf. Very young project with 10 stars; requires nightly Rust.

Rust-only (no_std, zero dependencies) so not directly callable from C++ without FFI; decoding is designed to never fail (lossy on malformed input), which changes error-handling semantics versus strict validators like simdutf; younger and far less battle-tested than simdutf.

## Maintenance

Actively maintained (last commit 2026-09-03, v1.5.0 published on crates.io with about 32.5k downloads across 7 releases) but still a young project at 10 GitHub stars; rated 'copyable', though the nightly-only core::simd requirement and no_std/alloc design mean it can't simply be vendored into a non-Rust codebase the way a header-only C library could.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (benches/throughput.rs calling the simdutf crate via FFI, driven by scripts/bench_hosts.sh), the toolchain is rustc nightly (rust-toolchain.toml) with release profile lto="thin" and RUSTFLAGS="-C target-cpu=native", and the Apple M4 Max host is a named CPU model. Tier A rests on the M4 Max rows; the 'Xeon x86-64' rows lack a CPU model.
- **Verifier notes:** Numbers verified in README raw tables; one percentage in the record was misattributed (Xeon UTF-8-&gt;UTF-16 cjk-3b is +20.1%, +20.9% is the M4 Max row). Record said criterion; the harness is custom (divan optional). Metadata (MIT, 10 stars, last commit 2026-09-03, not fork/archived) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/can1357/xutf>
  - <https://github.com/can1357/xutf#benchmarks>
  - <https://github.com/can1357/xutf/blob/main/scripts/bench_hosts.sh>
  - <https://github.com/can1357/xutf/blob/main/rust-toolchain.toml>
  - <https://github.com/can1357/xutf/blob/main/Cargo.toml>
  - <https://github.com/can1357/xutf/blob/main/benches/throughput.rs>
  - <https://github.com/can1357/xutf/blob/main/benches/data/xeon-x86-64.jsonl>
- **Sources the enricher read:**
  - <https://github.com/can1357/xutf>
  - <https://github.com/can1357/xutf#benchmarks>
  - <https://github.com/can1357/xutf/tree/main>
  - <https://github.com/can1357/xutf/blob/main/Cargo.toml>
  - <https://github.com/can1357/xutf/blob/main/rust-toolchain.toml>
  - <https://github.com/can1357/xutf/blob/main/src/lib.rs>
  - <https://github.com/can1357/xutf/blob/main/scripts/bench_hosts.sh>
  - <https://github.com/can1357/xutf/issues>
  - <https://crates.io/crates/xutf>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/can1357/xutf`) · [data/wave3/enrich/raw/github_com_can1357_xutf.json](../../../data/wave3/enrich/raw/github_com_can1357_xutf.json) (enrichment confidence 0.7)

</details>
