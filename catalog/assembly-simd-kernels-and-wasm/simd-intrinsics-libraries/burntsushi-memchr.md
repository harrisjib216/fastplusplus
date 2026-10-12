# memchr (Rust crate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Unlicense` · 🟢 active

> Rust crate of SIMD byte and substring search (memchr, memchr2/3, memrchr, memmem); about 4-6x faster than str::find, 2x faster than glibc memmem.

| | |
|---|---|
| **Beats** | Rust standard library substring search (rust/std/memmem: str::find / str::matches); the same rebar records also run glibc memmem and memchr through the libc engine (libc/memmem/oneshot, libc/memchr/oneshot) |
| **Claimed result** | README (2023-08-26 record, memchr 2.5.0 vs Rust std 1.73.0-nightly): geometric mean of speed ratios 1.03 vs 6.50 prebuilt (std about 6.3x slower) and 1.04 vs 5.26 oneshot (about 5.1x), derived from page data. Newest record benchmarks/record/x86_64/2026-07-30.csv (memchr 2.8.3 vs Rust std 1.99.0-nightly 1a833e165), pairwise geometric mean of median times: 4.64x prebuilt and 3.93x oneshot over 53 memmem benchmarks; 2.02x vs glibc memmem (libc/memmem/oneshot, 54 benchmarks, libc faster on 8); single-byte memchr 1.10x vs glibc memchr (15 benchmarks); StringZilla 5.0.5 memmem beats memchr on 39 of 54 benchmarks (memchr takes about 1.6x StringZilla's time, geometric mean) (all derived from page data). |
| **Workload** | rebar benchmark suite, 53 substring-search benchmarks on x86_64, prebuilt searcher and oneshot (build plus search) classes, geometric mean of speed ratios against the fastest engine. |
| **Metric** | throughput |
| **Compiler and flags** | Engines built with 'cargo build --release' (benchmarks/engines.toml); Rust std baseline 1.73.0-nightly 180dffba1 in the 2023-08-26 record and 1.99.0-nightly 1a833e165 in the 2026-07-30 record; libc engine version recorded as 'unknown'; RUSTFLAGS, target-cpu and the rustc version for the memchr engine not stated |
| **Adoption** | 1.6k stars; about 1.54 billion crates.io downloads (crates.io API, 2026-10-11) |
| **Last commit** | 2026-08-10 |
| **Links** | [repository](https://github.com/BurntSushi/memchr) · [benchmark](https://github.com/BurntSushi/memchr) |

## Verdict

rebar runs on the author's unnamed x86_64 machine, all engines built with plain cargo build --release (so memchr dispatches to AVX2 at runtime while Rust std's core search stays on SSE2): the README's 2023-08-26 rank output (memchr labelled 2.5.0 but actually the pre-release 2.6 code, vs std 1.73.0-nightly) gives geometric-mean speed ratios 1.03 vs 6.50 prebuilt and 1.04 vs 5.26 oneshot over 53 benchmarks, and the 2026-07-30 record (memchr 2.8.3 vs std 1.99.0-nightly) gives 4.64x prebuilt, 3.93x oneshot, 2.02x over libc memmem and 1.10x over libc memchr (pairwise, derived from page data). An aarch64 record from 2023-12-29 (memchr 2.7.1, host and libc unstated) shows 9.9x prebuilt and 8.2x oneshot over std, 7.8x over libc memmem and 1.86x over libc memchr (derived from page data).

## Use it when

- Rust code that searches byte or text buffers for a fixed substring (log scanning, protocol parsing, grep-like tools): rebar on x86_64 shows 3.9-4.6x over str::find/matches across 53 benchmarks (5.0-6.3x when the 12 timer-quantized 28-42 byte haystacks are left out, derived from page data).
- One needle searched across many haystacks (per-line search, per-record filters): build a memmem::Finder once; std must rebuild its searcher on every call.
- Finding the first or last of 1-3 delimiter bytes (memchr2/memchr3, memrchr) or substrings from the end (FinderRev): std has no SIMD equivalents for these.
- Binary or not-necessarily-UTF-8 data, where str::find would first need UTF-8 validation.
- Portable Rust builds on x86_64, aarch64 and wasm32 (with simd128 enabled), where AVX2 is picked up at runtime without target-cpu flags.

## Skip it when

- C or C++ projects: there is no C API, and StringZilla 5.0.5 (catalogued in wave 1, with a C/C++ API) beats memchr's memmem on 39 of 54 benchmarks in memchr's own 2026-07-30 record (memchr takes about 1.6x StringZilla's time, geometric mean; up to 69x on pathological/defeat-simple-vector-repeated-alphabet).
- Plain single-byte search where libc is already available: against glibc memchr it is roughly at parity on x86_64 (memchr 1.10x faster in the 2026 record, glibc 1.06x faster in the 2023 record, glibc ahead by 1.23-1.26x on the never/rare huge1 rows).
- Many short one-off searches with fresh needles: issue #161 (open since 2024-09-11) reports Finder construction and memmem::find on short haystacks about 3.3x slower in 2.6.0 and later than in 2.5.0, and the maintainer called it a likely 'regression we have to eat'.
- Highly periodic or adversarial inputs: std is up to 1.97x faster on the pathological/defeat-simple-vector-\* rows and glibc memmem about 3.1x faster on pathological/rare-repeated-\*-match in the 2026 record.
- Multi-pattern search or AVX-512: the crate searches a single needle, and AVX-512 is only being prepared (2026-08-03 commit 'refactor SIMD abstraction layer to prepare for AVX-512').

## How it is fast

Single-byte search uses vector compare-and-movemask loops (SSE2 and AVX2 on x86_64 picked by runtime CPU detection, NEON on aarch64, simd128 on wasm32, SWAR elsewhere). Substring search chooses per call: Rabin-Karp for very small haystacks, a 'Generic SIMD' packed-pair search for short needles that picks the two rarest needle bytes from a background byte-frequency table instead of the first and last bytes, and Two-Way otherwise with that SIMD routine as a candidate prefilter that switches itself off when it stops paying. Rust's std substring search lives in core, cannot use runtime feature detection, and so is limited to SSE2, and str::find has no reusable searcher; both gaps are where the measured ratios come from.

## Compared with alternatives

Pick memchr over libhat when you need exact byte or substring search from Rust rather than masked signature scanning in C++, and over vectorized_find, which is AVX2 std::find experiments rather than a maintained library; from C or C++, StringZilla (wave 1) is the faster and directly callable choice.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none by default (optional log with the 'logging' feature) |
| **Minimum toolchain** | Rust 1.61 (rust-version in Cargo.toml; may rise in minor releases), edition 2021 |
| **Platforms** | any Rust target; vector paths on x86_64 (SSE2 always, AVX2 by runtime detection when the std feature is on), aarch64 (NEON) and wasm32 (simd128 enabled at compile time); SWAR fallback elsewhere; no_std supported |
| **Thread safety** | not documented as such; the routines are pure functions over slices and Finder::find takes &self with per-search prefilter state created inside the call |
| **Drop-in for the baseline** | partial: memmem::find(h.as_bytes(), n.as_bytes()) replaces str::find(n) for string needles and returns the same byte offset, but there are no char, char-set or closure patterns, and it is not a C/C++ library |

## Gotchas

- Harness labelling flaw: the README's figures come from the 2023-08-26 record, which labels the memchr engine '2.5.0'; engine versions are hand-copied from each engine's Cargo.toml version field, the pinned memchr =2.5.0 engine (memchrold) in the same record is 1.36x slower (geometric mean, prebuilt, derived from page data), and 2.6.0 shipped on 2023-08-28, so the measured code was the unreleased 2.6 rewrite, not 2.5.0 (sliceslice is also mislabelled 2.5.0 there).
- The 12 teeny benchmarks (28-42 byte haystacks) have medians quantized to 10 ns ticks with zero MAD, so their ratios (1.0x, 1.5x, 2.5x) are single timer ticks; they pull the headline geometric means toward parity rather than inflating them.
- In the newest x86_64 record memchr 2.8.3 is no faster than the pinned 2.5.0 engine: geometric mean 1.00 on memmem prebuilt (slower on 21 of 57) and 0.92 on oneshot (slower on 31 of 54), derived from page data; the earlier 2.5.0-to-2.6 x86 regression (#139) was declared 'largely fixed' in 2.7.0, and the construction-cost regression (#161) is still open.
- No CPU model, OS or libc version is recorded for the x86_64 or aarch64 records (libc engine version 'unknown'), and the author wrote both the crate and the rebar harness; the harness does check every engine's match count.

## Known shortcomings

- First-party rebar results with no CPU or RUSTFLAGS; README numbers are from 2023 (newest record 2026-07-30: 3.9x to 4.6x vs Rust std, 2.0x vs glibc memmem, about par with glibc memchr); StringZilla (wave 1) is faster on 39 of 54 benchmarks; Rust crate, C++ needs FFI; weak category fit.
- Enricher: the README's 2023-08-26 record labels the memchr engine 2.5.0 (versions hand-copied from the engine Cargo.toml) but the pinned 2.5.0 engine runs 1.36x slower in the same record, and 2.6.0 shipped 2023-08-28, so the README measured unreleased 2.6 code; 12 teeny benchmarks quantised at 10 ns pull the geomeans toward parity (without them memchr is 6.3x/5.0x faster than std and 2.45x faster than glibc memmem); the 2026 record has 2.8.3 no faster than 2.5.0 (1.00 prebuilt, 0.92 oneshot); issue #161 (construction about 3.3x slower since 2.6) is open; StringZilla is faster on 39 of 54.

## Caveats and trade-offs

Baseline is Rust's std, not a C or C++ library; the README comparison covers substring search (memmem) only, and its numbers come from the 2023-08-26 record although newer records exist (2025-09-25, 2026-07-30). In the newest record the std gap is smaller (about 3.9x to 4.6x), the win over glibc memmem is about 2x, single-byte memchr is roughly at parity with glibc memchr (glibc 1.06x faster in the 2023 record, memchr 1.10x faster in 2026), and StringZilla, already catalogued in wave 1, is faster on 39 of 54 memmem benchmarks. The std prebuilt engine cannot exclude searcher construction, which the README admits. No CPU model or RUSTFLAGS stated. Author wrote both the library and the rebar harness. It is a Rust crate (C++ use needs FFI) and a string-search library rather than a general SIMD intrinsics library. [retier] README 2023-08-26 record measured unreleased 2.6 code under a hand-copied '2.5.0' label; 12 teeny 10 ns-quantised benchmarks dilute the geomeans (without them 6.3x/5.0x vs std, 2.45x vs glibc memmem); 2026 record shows 2.8.3 no faster than 2.5.0; issue #161 construction regression open; StringZilla faster on 39 of 54 rebar rows

Rust-only API (not callable from C++ without a binding); SSE2/AVX2 on x86_64, NEON on aarch64, wasm32 SIMD, SWAR fallback; Unlicense side is a public-domain dedication with no patent grant.

## Maintenance

Actively maintained (2.8.3 released 2026-07-08, commits through 2026-08-10, new rebar records for five more targets merged 2026-07-10), MIT OR Unlicense, about 1.54 billion crates.io downloads and 2,168 reverse dependencies; mature, fuzzed and property-tested, with pervasive internal unsafe.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party: the README quotes rebar rank output from benchmarks/record/x86_64/2023-08-26.csv, and both memchr and rebar are by the same author. Benchmark code and engine build commands are public (benchmarks/engines.toml, cargo build --release), but no CPU model or RUSTFLAGS are stated anywhere I opened, so not A.
- **Verifier notes:** README numbers match the record; I derived extra ratios from the public CSVs (pairwise geometric means of median times). Main shortcomings to record: first-party, no hardware stated, std-only headline, glibc memchr parity, StringZilla faster in memchr's own 2026 record; category fit is weak (string search rather than SIMD intrinsics library).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-12 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/BurntSushi/memchr>
  - <https://github.com/BurntSushi/memchr/commits/master>
  - <https://github.com/BurntSushi/memchr/tree/master/benchmarks>
  - <https://github.com/BurntSushi/memchr/tree/master/benchmarks/record/x86_64>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/README.md>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/engines.toml>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/record/x86_64/2023-08-26.csv>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/record/x86_64/2026-07-30.csv>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/memchr>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/README.md>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/src/memmem/mod.rs>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/engines.toml>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/record/x86_64/2023-08-26.csv>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/record/x86_64/2026-07-30.csv>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/record/aarch64/2023-12-29.csv>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/record/x86_64-pc-windows-msvc/2026-07-10.txt>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/engines/rust-memchr/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/engines/rust-memchrold/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/engines/libc/main.rs>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/engines/libc/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/engines/stringzilla/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/engines/stringzilla/main.rs>
  - <https://raw.githubusercontent.com/BurntSushi/memchr/HEAD/benchmarks/engines/rust-std/main.rs>
  - <https://github.com/BurntSushi/memchr/commits/master>
  - <https://github.com/BurntSushi/memchr/tree/master/src/arch>
  - <https://github.com/BurntSushi/memchr/tree/master/benchmarks/record>
  - <https://github.com/BurntSushi/memchr/tree/master/benchmarks/record/aarch64>
  - <https://github.com/BurntSushi/memchr/tree/master/benchmarks/record/x86_64-pc-windows-msvc>
  - <https://github.com/BurntSushi/memchr/issues?q=is%3Aissue+performance>
  - <https://github.com/BurntSushi/memchr/issues/161>
  - <https://github.com/BurntSushi/memchr/issues/139>
  - <https://github.com/BurntSushi/memchr/issues/107>
  - <https://github.com/BurntSushi/memchr/pull/229>
  - <https://crates.io/api/v1/crates/memchr>
  - <https://crates.io/api/v1/crates/memchr/versions?per_page=100>
  - <https://crates.io/api/v1/crates/memchr/reverse_dependencies?per_page=1>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/burntsushi/memchr`) · [data/wave13/enrich/raw/github_com_burntsushi_memchr.json](../../../data/wave13/enrich/raw/github_com_burntsushi_memchr.json) (enrichment confidence 0.8)

</details>
