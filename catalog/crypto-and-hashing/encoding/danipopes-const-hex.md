# const-hex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust hex codec with runtime-dispatched SIMD and const-fn API; near drop-in for `hex`, 6–100x faster on README benches.

| | |
|---|---|
| **Beats** | hex (Rust `hex` crate) |
| **Claimed result** | 10 to 50 times faster than the `hex` crate in encoding and decoding, and 100+ times faster than libstd's hex formatting; e.g. at 1MB, decode is 108,937 ns vs hex crate's 6,409,293 ns (\~59x, derived from page data) |
| **Workload** | Encoding/decoding byte buffers from 32 bytes to 1MB to/from hex strings, criterion 'cargo bench' |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X |
| **Compiler and flags** | rustc 1.83.0-nightly (9ff5fc4ff 2024-10-03), target x86_64-unknown-linux-gnu |
| **Adoption** | 67 stars; \~60.5M crates.io downloads (\~16.8M recent) |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/DaniPopes/const-hex) · [benchmark](https://raw.githubusercontent.com/DaniPopes/const-hex/master/README.md) |

## Verdict

The README's libtest run used rustc 1.83.0-nightly (2024-10-03) on x86_64 Linux on an AMD Ryzen 9 7950X with the default bench profile. At 1 MB it shows decode 108,937 ns vs `hex` 6,409,294 ns (\~59x), encode 30,716 ns vs 3,048,496 ns (\~99x), and Display formatting \~158x faster than std. At 32 bytes the gap narrows to \~6x decode, \~7–8x slice encode and \~14x String encode (all derived from page data). The numbers predate the 2025–26 rewrites (divan/CodSpeed benches, single-pass AVX2 decode, NEON decode) and were not re-run.

## Use it when

- Replacing `hex` on hot Rust paths that print or parse digests, keys or IDs; the README shows about 59x at 1 MB and still 6–14x at 32 bytes.
- 0x-prefixed hex strings: prefixed encoders exist and decode strips the prefix for you.
- Hex constants built at compile time (const_decode_to_array, const_encode) or allocation-free formatting of fixed-size arrays through Buffer&lt;N&gt;.
- Code shipping to aarch64 (NEON) or wasm32 with simd128, where the README positions it ahead of faster-hex, which only optimizes x86.
- no_std or embedded crates that still want a SIMD fast path; only cfg-if and cpufeatures are required.

## Skip it when

- When you must match `hex`'s serde wire format exactly: `#[serde(with = "const_hex")]` writes a 0x prefix (see gotchas).
- Strict parsers that must reject a leading '0x'/'0X': decode, decode_to_slice and check strip it silently.
- The last few percent of x86 slice-encode throughput: in the README's encode_to_slice rows faster-hex was 6–12% faster from 2 kB up. There is no AVX-512 path.
- Code that needs every safe API to be sound: issue #47 shows safe Buffer methods producing an invalid-UTF-8 &mut str (UB under Miri), closed by the maintainer as 'too contrived' to fix.
- Non-Rust projects: the siblings cover C++ and Node.

## How it is fast

Encoding splits each byte into nibbles and maps them through a 16-entry table with one byte-shuffle (pshufb/_mm256_shuffle_epi8 on x86, vqtbl1q_u8 on NEON), then interleaves with unpack/zip. With AVX2 that turns 32 input bytes into 64 characters per step. Since 2026-03, x86 decoding validates and decodes in one pass using Muła & Langdale's 'validating hex parse' Algorithm #3: saturating adds map digits and letters to 0..15, anything invalid lands above 15 and trips the sign bit, and vpmaddubsw merges nibble pairs (hi\*16+lo) before a pack/permute. Output goes straight into uninitialized capacity. The CPU path (AVX2, then SSSE3/SSE2, then a scalar lookup table) is picked at runtime via is_x86_feature_detected! or cpufeatures.

## Compared with alternatives

For Rust, pick const-hex over fast-hex (zbjornson, C++/Node) and hx (a NEON table-lookup encode experiment). Its older AVX2 unchecked-decode path descends from fast-hex via faster-hex, and it is the only one of the three shipped as a maintained crate with runtime dispatch, validation and a `hex`-compatible API.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if; cpufeatures on x86/x86-64; optional serde_core (feature `serde`) and proptest (internal fuzzing) |
| **Minimum toolchain** | Rust 1.64 (CI builds on 1.64, stable and nightly). The `core-error` feature needs Rust 1.81; the `nightly` and `portable-simd` features need nightly. |
| **Platforms** | Any target. SIMD paths: x86/x86-64 (SSE2/SSSE3/AVX2, detected at runtime), aarch64 NEON, wasm32 with simd128, and std::simd on nightly; a scalar lookup table elsewhere. |
| **Thread safety** | not documented; the functions keep no state apart from cached CPU-feature detection, and Buffer is a plain owned value |
| **Drop-in for the baseline** | partial — same function names, trait names and error variants as `hex`, but FromHexError is a separate type, decode also accepts a 0x/0X prefix, serde output adds a 0x prefix by default, and ToHex is deprecated |

## Gotchas

- Serde: `#[serde(with = "const_hex")]` serializes with a leading "0x", unlike `hex` (issue #34). Use `const_hex::serde::no_prefix` (1.18.0+) to keep the old JSON. Deserialization accepts both forms.
- Decode is more permissive than `hex`: a leading 0x/0X is stripped before validation, so '0x…' strings that `hex` treats as invalid now parse.
- `ToHex` is deprecated (open issue #26). The maintainer says its iterator-of-char API forces slow one-item-at-a-time output and keeps it only for `hex` compatibility, so migrations surface deprecation warnings; use ToHexExt, encode_to_slice or display().
- Buffer::as_mut_byte_array() followed by as_mut_str() lets safe code build a non-UTF-8 str (issue #47). The maintainer won't fix it, so don't write non-ASCII bytes through the byte-array view.

## Known shortcomings

- Rust-only; headline 10-50x is against the Rust `hex` crate, a slow scalar baseline, rather than other SIMD hex encoders.
- README numbers are from a 2024 nightly and stale (AVX2 validating decode and NEON decode added 2026-03). At 32 bytes the gap is only 6-14x; faster-hex is 6-12% faster on encode_to_slice at 2 kB and up; no AVX-512. Not a true drop-in for `hex`: serde adds a 0x prefix by default, decode strips 0x, own FromHexError type. Soundness issue #47 (safe Buffer API can produce invalid UTF-8 str) closed won't-fix.

## Caveats and trade-offs

Rust `hex` crate baseline, not a C/C++ implementation; benchmarks are reproducible via `cargo bench` but this session did not re-run them, only read the published numbers.

Rust-only; on x86/x86-64 performance is comparable to faster-hex, its main SIMD-based competitor, but const-hex is portable to other architectures where faster-hex has no SIMD path

## Maintenance

Actively maintained: 1.19.3 released 2026-09-16, MSRV 1.64 tested in CI along with Miri and fuzzing, dual MIT/Apache-2.0, \~60.5M downloads and 166 reverse dependencies. The `hex` baseline's last release was 0.4.3 in 2021-03.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README benchmark log puts const_hex against the hex crate (plus rustc_hex, faster_hex and std formatting) in the same run. It states rustc 1.83.0-nightly (9ff5fc4ff 2024-10-03) and an AMD Ryzen 9 7950X. The numbers came from the libtest benches in benches/bench/main.rs at commit ce406b5 (2024-10-06). At that commit Cargo.toml had no [profile] override, so the flags are the default cargo bench profile (opt-level=3).
- **Verifier notes:** The benchmark_url pointed at the 'main' branch, which returns 404; the default branch is master. The license is dual MIT OR Apache-2.0 (Cargo.toml and README), although gh reports only Apache-2.0. The README numbers date from 2024-10 and were produced with the old libtest harness, but the benches have used divan since 2025-06. Page data gives ratios up to \~99x at 1MB encode (derived from page data) and \~158x for 1MB std formatting (derived from page data), above the README's '10 to 50 times' phrasing.
- **Fields the verifier corrected:** `benchmark_url`, `license`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/DaniPopes/const-hex>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/main/README.md>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/README.md>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/Cargo.toml>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/benches/bench/main.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/ce406b594973adc1516b0cd0f535f84c3e10b9ec/Cargo.toml>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/ce406b594973adc1516b0cd0f535f84c3e10b9ec/benches/bench/main.rs>
  - <https://crates.io/api/v1/crates/const-hex>
- **Sources the enricher read:**
  - <https://github.com/DaniPopes/const-hex>
  - <https://api.github.com/repos/DaniPopes/const-hex/git/trees/HEAD?recursive=1>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/README.md>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/Cargo.toml>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/lib.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/arch/mod.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/arch/x86.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/arch/aarch64.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/arch/generic.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/arch/portable_simd.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/arch/wasm32.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/error.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/traits.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/buffer.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/serde.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/display.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/output.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/src/impl_core.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/benches/bench/main.rs>
  - <https://raw.githubusercontent.com/DaniPopes/const-hex/master/fuzz/fuzz_targets/fuzz_const_hex.rs>
  - <https://github.com/DaniPopes/const-hex/issues?q=is%3Aissue>
  - <https://github.com/DaniPopes/const-hex/issues/47>
  - <https://github.com/DaniPopes/const-hex/issues/26>
  - <https://github.com/DaniPopes/const-hex/issues/29>
  - <https://github.com/DaniPopes/const-hex/issues/34>
  - <https://crates.io/api/v1/crates/const-hex>
  - <https://crates.io/api/v1/crates/const-hex/reverse_dependencies>
  - <https://crates.io/api/v1/crates/hex>
  - <https://crates.io/api/v1/crates/faster-hex>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/danipopes/const-hex`) · [data/wave7/enrich/raw/github_com_danipopes_const_hex.json](../../../data/wave7/enrich/raw/github_com_danipopes_const_hex.json) (enrichment confidence 0.85)

</details>
