# base64-turbo (hacer-bark)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `0BSD` · 🟢 active

> 0BSD Rust base64 crate with AVX2/AVX-512 VBMI/NEON kernels; 2.7-6x the default base64 crate, roughly ties Turbo-Base64.

| | |
|---|---|
| **Beats** | base64 (RFC 4648) codecs: Turbo-Base64 (C, the prior fastest known codec) and the Rust default `base64` crate 0.23 (its SIMD path on by default), plus base64-simd and base64-ng, all in the same harness |
| **Claimed result** | At 64 KiB (encode/decode, GiB/s): base64-turbo 81.6/106.5 vs Turbo-Base64 80.7/107.8 on AWS c8a.large (AMD EPYC 9R45), and 25.7/36.9 vs 18.2/38.5 on c7i.large (Xeon Platinum 8488C). Against the default `base64` crate it is 81.6/106.5 vs 13.5/27.9 (c8a) and 25.7/36.9 vs 8.9/13.7 (c7i), which is about 6.0x/3.8x and 2.9x/2.7x (derived from page data). The c8a sweep peaks at 123.0 GiB/s encode and 118.1 GiB/s decode at 4 KiB. At that size the raw output has Turbo-Base64 decode at 119.7, so decode is still marginally behind (raw file). |
| **Workload** | criterion.rs benchmark (benches/encoding_bench.rs), base64 encode/decode across input sizes 32B-10MB, pinned to one core |
| **Metric** | throughput |
| **Hardware** | AWS c8a.large (AMD EPYC 9R45, Zen5) and c7i.large (Intel Xeon Platinum 8488C, Sapphire Rapids), pinned to one core |
| **Compiler and flags** | rustc version not stated (MSRV 1.93; the reproduction steps install the current rustup stable). `cargo bench` uses the default bench profile (opt-level 3, no custom RUSTFLAGS or target-cpu; kernels are picked at runtime). Criterion runs with a 5 s warm-up. The README says 15 s of measurement, but encoding_bench.rs actually uses 8/10/12 s depending on the size tier. Turbo-Base64 is compiled through the cc crate in benches/tb64-sys/build.rs with -O3 -DNDEBUG -fstrict-aliasing (-falign-loops on gcc) and upstream's per-file -march flags (ssse3, corei7-avx, haswell, skylake-avx512 -mavx512vbmi). The C compiler and its version are not stated. |
| **Adoption** | 2 stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/hacer-bark/base64-turbo) · [benchmark](https://github.com/hacer-bark/base64-turbo#benchmarks) |

## Verdict

In the author's criterion harness (random input, one core, encode GiB/s counted on raw bytes and decode on base64 text, rustc and C compiler versions not stated), at 64 KiB base64-turbo runs 81.6/106.5 GiB/s on AWS c8a.large (EPYC 9R45, Zen 5) and 25.7/36.9 on c7i.large (Xeon 8488C). The base64 crate 0.23 manages 13.5/27.9 and 8.9/13.7 (about 6.0x/3.8x and 2.9x/2.7x). Turbo-Base64, built from upstream source with its own per-file flags and default partial-validation mode, and timed with the author's own C-side harness, comes in essentially level at 80.7/107.8 and 18.2/38.5.

## Use it when

- Rust services on AVX-512 VBMI x86 (the author measured Zen 5 EPYC 9R45 and Sapphire Rapids) that encode/decode payloads of about 512 B to 1 MiB. On c8a.large at 64 KiB it runs 81.6/106.5 GiB/s against 13.5/27.9 for the base64 crate 0.23, whose SIMD path is on by default. It peaks at 123.0/118.1 GiB/s at 4 KiB.
- You want a faster base64 crate replacement for STANDARD or URL_SAFE (JWTs, URLs) with a permissive 0BSD license and unsafe SIMD backed by Kani proofs, MIRI, MSan and 250M+ fuzz iterations. The AVX2 box (c7i.large) still shows 2.7-2.9x at 64 KiB.
- Custom alphabets (bcrypt/crypt(3) and similar) at full vector speed, but only on AVX-512 VBMI; AVX2 and NEON fall back to scalar for them.
- no_std x86 targets that still want runtime-dispatched SIMD (0.5.0 detects through cpufeatures), or audit-sensitive builds that set --cfg base64_turbo_backend="soft" to get a #![forbid(unsafe_code)] scalar-only crate.

## Skip it when

- Your toolchain is older than Rust 1.93 or can't use edition 2024. The README also says the MSRV is pinned by Kani's bundled rustc and won't be lowered.
- Mostly multi-MB, DRAM-resident buffers. At 10 MB on c8a, Turbo-Base64 is about 28% faster encoding and 22% faster decoding (37.7/55.8 vs 29.4/45.7 GiB/s). On c7i at 10 MB it is only 1.2x/1.07x ahead of the base64 crate (10.9/14.2 vs 8.9/13.3), with everyone near memcpy.
- Many tiny (about 32 B) decodes: base64-simd wins there (7.6 vs 5.8 GiB/s on c8a, 4.1 vs 3.6 on c7i), and Turbo-Base64 wins 32 B encode.
- x86 without AVX2 (there is no SSE kernel), WASM SIMD, or other non-x86/non-ARM targets, which all run scalar only. The README FAQ calls NEON best-effort, not production-ready, with no Kani proofs, and says it may be deprecated.
- You need a long-maintained dependency: one author, repo created Jan 2026, 2 stars, about 3.6k crates.io downloads, no reverse dependencies, and breaking 0.4.0/0.5.0 releases 12 days apart in Sept 2026. There is no C API either, so C/C++ callers would need their own FFI shim.

## How it is fast

The AVX2 kernel ports aklomp/base64's approach: Mula/Lemire nibble-lookup validation for decode, and an offset-load encode loop with a single-LUT character map. The ALU work is interleaved across ports 0/1/5 so vpshufb on port 5 is not the bottleneck. The AVX-512 VBMI kernel encodes 48 bytes in three ops (vpermb gather, vpmultishiftqb to pull out all eight 6-bit fields, vpermb through the alphabet). It decodes with vpermi2b over a 128-entry reverse LUT and folds validity into a single vpternlogd OR tree, while k-masked passes handle the 1-31 byte tail without a scalar handoff. Both x86 kernels switch to non-temporal stores above 5/8 of the CPUID-reported last-level cache, and the CPU tier is cached in one atomic byte, so dispatch costs a single load per call.

## Compared with alternatives

In Rust, pick it over vb64 (std::simd; its blurb reports 1.2-2.5x over the base64 crate) or the base64 crate itself when throughput on AVX2/AVX-512 VBMI matters. Pick it over Turbo-Base64 when you need a permissive license instead of GPL-3, validation of every byte, base64url/no-pad/custom alphabets, or verified Rust memory safety at roughly equal in-cache speed. Stay with Turbo-Base64 for DRAM-sized buffers on Zen 5 or when calling from C, and use simdutf for whitespace-tolerant forgiving decoding.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cpufeatures 0.3 on x86/x86-64 only; none elsewhere |
| **Minimum toolchain** | Rust 1.93 (edition 2024) |
| **Platforms** | x86/x86-64: AVX-512 VBMI or AVX2 picked at runtime, else scalar. aarch64: NEON picked at compile time (best-effort). Everything else: safe scalar. No SSE or WASM SIMD kernels. |
| **Thread safety** | Engines are immutable consts/statics. The CPU tier and LLC size are cached in AtomicU8/AtomicUsize with Relaxed ordering (a race just computes the same value twice), so any thread can use them concurrently. |
| **Drop-in for the baseline** | partial — output is byte-identical to the base64 crate's for STANDARD/URL_SAFE and the method names match, but types, error enum and buffer-size rules differ and there are no streaming adapters; against Turbo-Base64 (C) there is no C API at all |

## Gotchas

- decode_slice returns BufferTooSmall unless the output holds decoded_len_estimate bytes, which can be up to 2 more than the real decoded length, so an exactly sized buffer is rejected.
- STANDARD/URL_SAFE require canonical padding, and the \*_PAD_INDIFFERENT engines decode on the scalar path only. For a misplaced '=', whether you get InvalidLength or InvalidCharacter is deliberately unspecified and depends on the kernel, so check is_err() and don't match the variant.
- 0.5.0 removed the avx2/avx512-vbmi/simd/neon Cargo features, so builds that name them fail. Backend narrowing is now a RUSTFLAGS --cfg that applies to the whole dependency graph, and base64_turbo_backend="avx512" on a CPU without VBMI falls back to scalar, not AVX2. --no-default-features now means no_std with SIMD, not scalar-only.
- The README's API-stability paragraph still promises compatibility 'throughout the 0.4.x lifecycle' while the crate is already at 0.5.0, so pin exact versions.

## Known shortcomings

- No rustc or C compiler version stated (retiered A to C). Against Turbo-Base64 it is about a tie and decodes slower; the real win is over the Rust `base64` crate (\~2.7-6x).
- Only ties Turbo-Base64 in cache and loses at 10 MB on c8a (-28% encode, -22% decode); loses 32-byte decode to base64-simd; on c7i at 10 MB only 1.07-1.2x over the base64 crate. Tiny adoption (1 author, 2 stars, \~3.6k downloads, 0 reverse deps); breaking 0.4.0 to 0.5.0 twelve days apart. MSRV 1.93 / edition 2024; no SSE or WASM kernel; NEON 'not production-ready'; custom alphabets fall back to scalar; decode_slice rejects exact-size buffers.

## Caveats and trade-offs

0BSD carries no explicit patent grant. Results against Turbo-Base64 are mixed. At 64 KiB base64-turbo wins encode but is slightly slower on decode on both machines. Turbo-Base64 also wins 32 B encode, and on c8a it pulls ahead once the data no longer fits in cache (README: about 28% faster encode and 22% faster decode at 10 MB). The clear win is over the Rust default `base64` crate. The author wrote the C-side timing harness and calls those margins 'directional'. Neither the rustc nor the C compiler version is stated. The 100+ GiB/s peaks need AVX-512 VBMI and hold only at 4 KiB. The project is very new with little visibility (2 stars, repo created 2026-01-20), and no one has reproduced the results independently.

Pure Rust; SIMD kernels use `unsafe` verified with Kani/MIRI/MSan/fuzzing, scalar fallback is `#![forbid(unsafe_code)]`; no published C API/bindings, so a C++ caller would need to write its own FFI shim; custom (non-RFC4648) alphabets lose AVX2/NEON acceleration

## Maintenance

Actively developed by a single author (0.5.0 released 2026-09-19; Kani, MIRI and test CI green) and 0BSD-licensed. Adoption is tiny and the API broke twice in September 2026, so vendor or pin it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README Benchmarks table and the checked-in raw criterion output (benches/results/c8a-large-latest.txt, c7i-large-latest.txt) match the claim. The harness is public (benches/encoding_bench.rs; Turbo-Base64 is built through benches/tb64-sys/build.rs), the flags are in code and both CPUs are named. But neither the rustc version nor the C compiler version is stated anywhere (only MSRV 1.93, and the repro script installs whatever rustup stable is current), so by batch precedent this is first-party with partial methodology: C, not A.
- **Verifier notes:** The numbers are all real and traceable to the raw criterion files, and 0BSD license, 2 stars and last commit 2026-09-19 all check out. The drop to C is only because no compiler versions are given. The stronger headline is the \~3-6x over the default `base64` crate. Against Turbo-Base64 it is roughly a tie.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/hacer-bark/base64-turbo>
  - <https://github.com/hacer-bark/base64-turbo#benchmarks>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/Cargo.toml>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/CHANGELOG.md>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/encoding_bench.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/results/c8a-large-latest.txt>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/results/c7i-large-latest.txt>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/tb64-sys/README.md>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/tb64-sys/build.rs>
- **Sources the enricher read:**
  - <https://github.com/hacer-bark/base64-turbo>
  - <https://github.com/hacer-bark/base64-turbo#benchmarks>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/Cargo.toml>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/CHANGELOG.md>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/build.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/src/lib.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/src/engine.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/src/cpu.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/src/error.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/src/simd.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/encoding_bench.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/results/c8a-large-latest.txt>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/results/c7i-large-latest.txt>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/tb64-sys/README.md>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/tb64-sys/build.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/benches/tb64-sys/src/lib.rs>
  - <https://github.com/hacer-bark/base64-turbo/blob/main/.github/workflows/tests.yml>
  - <https://github.com/hacer-bark/base64-turbo/issues>
  - <https://github.com/hacer-bark/base64-turbo/pulls>
  - <https://github.com/hacer-bark/base64-turbo/actions>
  - <https://github.com/hacer-bark/base64-turbo/graphs/contributors>
  - <https://crates.io/api/v1/crates/base64-turbo>
  - <https://crates.io/api/v1/crates/base64-turbo/reverse_dependencies>
  - <https://hn.algolia.com/api/v1/search?query=base64-turbo&hitsPerPage=10>
  - <https://github.com/powturbo/Turbo-Base64>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/hacer-bark/base64-turbo`) · [data/wave7/enrich/raw/github_com_hacer_bark_base64_turbo.json](../../../data/wave7/enrich/raw/github_com_hacer_bark_base64_turbo.json) (enrichment confidence 0.8)

</details>
