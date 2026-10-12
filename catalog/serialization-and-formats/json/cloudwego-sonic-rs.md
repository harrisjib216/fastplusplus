# sonic-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Serde-compatible Rust JSON library using SIMD; about 1.7-2.8x faster than serde_json at typed parsing on x86_64.

| | |
|---|---|
| **Beats** | serde_json |
| **Claimed result** | README x86_64 Criterion means (ratios derived from page data). Untyped canada deserialize: sonic_rs_dom::from_slice 4.9568 ms vs serde_json::from_slice 16.980 ms (\~3.4x) and from_str 16.640 ms (\~3.4x); vs simd_json borrowed 12.164 ms (\~2.5x). Struct twitter deserialize: sonic_rs::from_slice_unchecked 707.83 us and validated from_slice 827.74 us, vs serde_json::from_slice 2.2895 ms (\~3.2x / \~2.8x), serde_json::from_str 1.3842 ms (\~2.0x / \~1.7x), and simd_json::from_slice 1.0872 ms (\~1.5x / \~1.3x). Untyped twitter serialize: 390.00 us vs serde_json 797.34 us (\~2.0x) and simd_json 981.14 us (\~2.5x). serde_json is slightly faster on canada serialization: 6.5747 vs 6.7082 ms untyped and 4.6281 vs 4.7481 ms struct. |
| **Workload** | Deserialize/serialize standard corpora (twitter.json, citm_catalog.json, canada.json) into typed Rust structs and into an untyped Value/DOM, via Criterion (`cargo bench`). |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) Platinum 8260 CPU @ 2.40GHz (x86_64); AArch64 numbers on Apple M1 Pro in docs/benchmark_aarch64.md |
| **Compiler and flags** | cargo bench (Criterion) with rustflags '-g -C target-cpu=native' (benchmarks/.cargo/config.toml). Current benchmarks/Cargo.toml release profile: opt-level=3, lto=true, codegen-units=1; jemalloc allocator; bench pinned to core 0. The rustc version is not stated. The numbers date from Oct-Dec 2023, when the README required nightly Rust. |
| **Adoption** | 922 stars; used internally at ByteDance/CloudWeGo |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/cloudwego/sonic-rs) · [benchmark](https://github.com/cloudwego/sonic-rs/blob/main/README.md) |

## Verdict

The numbers are first-party Criterion runs from the README, unchanged since late 2023 when the crate was about v0.3; the rustc, serde_json and simd-json versions are not stated. They were run on an Intel Xeon Platinum 8260 with -C target-cpu=native, LTO and jemalloc. Validated sonic_rs::from_slice parsed twitter.json into structs in 0.83 ms vs 1.38 ms for serde_json::from_str and 2.29 ms for from_slice, and parsed canada.json into an untyped Value in 4.96 ms vs 16.6-17.0 ms for serde_json; serde_json was about 2% faster at canada serialization.

## Use it when

- Rust services on x86_64 built with AVX2+PCLMULQDQ enabled that deserialize multi-KB-to-MB payloads into serde structs. In the README, validated from_slice beats serde_json::from_str by 1.7-2.3x and serde_json::from_slice by 2.2-2.8x on twitter/citm_catalog/canada.
- Parsing into an untyped DOM that is mostly read, not heavily key-searched. sonic_rs::Value parses 3.4-5.2x faster than serde_json::from_str into serde_json::Value on the Xeon, and 2.8-3.3x faster on Apple M1 Pro.
- Pulling a few fields out of large documents you already trust. get_unchecked read a twitter.json field in 76.8 us vs 363 us for gjson, and get, get_many and the lazy iterators avoid building a DOM at all.
- Serializing string-heavy data. twitter.json to_string took 390 us vs 797 us for serde_json (Value) and 448 vs 740 us (struct), thanks to the SIMD escape scan.

## Skip it when

- Small messages. In issue #150 a user's small-payload struct benchmark showed no gain over serde_json, and the maintainer answered that the JSON was too small to benefit from SIMD.
- Portable x86_64 binaries built for the default baseline. The SIMD paths are chosen at compile time (cfg target_feature avx2+pclmulqdq), and there is no runtime CPU dispatch (issue #14 is still open). Without -C target-cpu=native or the matching target features you get the scalar fallback. A native build may not run on older CPUs.
- Parsing untrusted, possibly deeply nested input into sonic_rs::Value, or using checked get_many on it. parser.rs has no depth guard, and 100,000 nested brackets abort the process with a stack overflow instead of returning an error (open issues #239 and #232). Typed serde deserialization is capped at 255 levels.
- Non-mainstream targets. 32-bit x86 (i686) fails to build (open issues #228 and #231). RISC-V and other architectures use a scalar fallback that the README says may be 'very slower'.
- Float-heavy serialization, or struct parsing on aarch64. serde_json matched or slightly beat it on canada.json serialization on both test CPUs. On M1 Pro, simd-json was faster at struct parsing of twitter and citm, and sonic-rs was only 1.1-1.7x ahead of serde_json::from_str.

## How it is fast

It does not use simdjson's two-stage structural-index/tape design. It is a single-pass recursive-descent parser that feeds serde visitors or the DOM directly, with no intermediate tape; the README credits this for beating simd-json on structs. SIMD (SSE2/AVX2 on x86_64, NEON on aarch64) speeds up the hot loops: string scanning with simdutf8 validation; whitespace skipping with simdjson's shuffle-table classifier and a cached 64-bit non-space bitmap; JSONSki-style bracket counting over a PCLMULQDQ prefix-XOR in-string mask, which skips whole containers for the get and lazy APIs; and a 32-byte copy-and-find escape loop on output. Numbers are parsed with 8-digit SWAR plus an Eisel-Lemire fast path and printed with zmij (Schubfach-based). The Value DOM uses a bumpalo arena, stores objects as flat key/value arrays instead of hash maps, and points strings into a padded copy of the input.

## Compared with alternatives

In Rust, pick it over simd-json for serde-struct parsing or a mutable DOM on x86_64. Its README shows it 1.3-2.0x faster there, and it parses from an immutable &[u8]/&str, while simd-json's serde entry point takes &mut [u8]. On Apple M1 Pro, simd-json ties or wins struct parsing. jiter's catalogued \~2x over serde_json comes from a different benchmark, and bytedance/sonic is the Go sibling built on the same ideas.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | ahash, bumpalo, bytes, cfg-if, faststr, itoa, ref-cast, serde, simdutf8, thiserror, zmij, plus in-repo sonic-number and sonic-simd |
| **Minimum toolchain** | Stable Rust, edition 2021. No rust-version is declared. The code calls pointer expose_provenance (stable since Rust 1.84), so 1.84+ is inferred. The optional avx512 feature needs Rust 1.89+ and the avx512f target feature. |
| **Platforms** | x86_64 (fast path needs compile-time AVX2 + PCLMULQDQ + SSE2) and aarch64 (NEON). wasm32 gets simd128 in the SIMD layer. Other targets use a scalar fallback, and i686 currently fails to build. CI covers Linux x86_64/arm64, macOS, Windows and wasm32-wasip1. |
| **Thread safety** | Not documented in prose. Value has unsafe Send + Sync impls; a parsed DOM sits in an Arc-shared arena. DOM parsing uses a thread-local node buffer, so concurrent parsing on separate threads is fine. |
| **Drop-in for the baseline** | partial: typed serde (de)serialization uses the same from_str/from_slice/to_string/to_vec/to_writer/json! entry points. But Value/Object has a different, trait-based API with O(n) object lookup and kept duplicate keys. RawValue maps to LazyValue. The error type differs. from_reader buffers the whole input. #[serde(flatten)] into maps of sonic_rs::Value fails (open issue #114). |

## Gotchas

- Object::get on a parsed Value is a linear scan (documented as O(n); issue #168 is open). Duplicate keys are all kept, and get returns the first. The migration guide flags duplicate-key handling as a difference from serde_json::Value.
- The \*_unchecked APIs are unsafe. from_slice_unchecked skips UTF-8 validation, and get_unchecked/to_object_iter_unchecked assume valid JSON ('may return unexpected result'). from_str already takes the same no-validation path internally, because &str is valid UTF-8. So the README's from_slice_unchecked timings are what from_str gets.
- Release builds read SIMD vectors past the end of a string tail when the read stays within the same page (check_cross_page), and LLVM sanitizers flag this. Hence the sanitize feature, which the README says costs about 30% of serialize speed and should not be used in production.
- A parsed Value keeps a padded copy of the whole input plus a bumpalo arena alive. Parsing reserves len/2+2 node slots, thread-local up to 3 MB and heap above that. Inputs of 4 GB or more are rejected.

## Caveats and trade-offs

The numbers are first-party README figures. They have not changed since Dec 2023 or earlier, when the crate was about v0.3 (it is now 0.5.10). The rustc, serde_json and simd-json versions used are not stated. The headline struct figure pairs from_slice_unchecked (no UTF-8 validation) with serde_json::from_slice, serde_json's slowest path. The validated from_slice against serde_json::from_str is about 1.7x. serde_json is slightly faster on canada serialization. On Apple M1 Pro, simd-json edges out sonic-rs on struct deserialization for twitter and citm_catalog. The SIMD paths need -C target-cpu=native on x86_64 or aarch64. Other architectures fall back to slower code.

Fastest on x86_64/aarch64 only, falls back (slow) on other architectures; requires `-C target-cpu=native` for full speed which hurts binary portability; `sanitize` feature causes \~30% perf loss under LLVM sanitizers.

## Maintenance

Actively maintained under Apache-2.0: 0.5.9 and 0.5.10 shipped 2026-09-11, and the crate has about 6.8M crates.io downloads. It is usable today on stable Rust, but deep-nesting stack overflows and the i686 build failure are still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The benchmark code is public (benchmarks/benches/deserialize_struct.rs, deserialize_value.rs, serialize_value.rs, serialize_struct.rs, run with Criterion against serde_json and simd-json). The CPU is stated (Xeon Platinum 8260), and the flags are in benchmarks/.cargo/config.toml and benchmarks/Cargo.toml. No rustc version is stated anywhere, so by the project rule this is not A. It is first-party with partial methodology, so C.
- **Verifier notes:** Metadata verified: Apache-2.0, not a fork, not archived, 922 stars, last commit 2026-09-11, active. The claimed numbers exist on the page, but the ranges were loosely stitched and favored the unchecked path, so claimed_speedup was rewritten with exact means. The A-to-C downgrade is only for the missing rustc version.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cloudwego/sonic-rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/README.md>
  - <https://github.com/cloudwego/sonic-rs/blob/main/docs/benchmark_aarch64.md>
  - <https://github.com/cloudwego/sonic-rs/blob/main/benchmarks/Cargo.toml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/benchmarks/.cargo/config.toml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/benchmarks/bench_quick.sh>
  - <https://github.com/cloudwego/sonic-rs/blob/main/benchmarks/benches/deserialize_value.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/benchmarks/benches/deserialize_struct.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/benchmarks/benches/serialize_value.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/.cargo/config.toml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/.github/workflows/ci.yml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/Cargo.toml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/cloudwego/sonic-rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/README.md>
  - <https://github.com/cloudwego/sonic-rs/blob/main/docs/performance.md>
  - <https://github.com/cloudwego/sonic-rs/blob/main/docs/serdejson_compatibility.md>
  - <https://github.com/cloudwego/sonic-rs/blob/main/docs/benchmark_aarch64.md>
  - <https://github.com/cloudwego/sonic-rs/blob/main/Cargo.toml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/.cargo/config.toml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/ROADMAP.md>
  - <https://github.com/cloudwego/sonic-rs/blob/main/.github/workflows/ci.yml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/scripts/sanitize.sh>
  - <https://github.com/cloudwego/sonic-rs/blob/main/scripts/test.sh>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/lib.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/parser.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/serde/de.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/serde/ser.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/value/node.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/value/object.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/value/shared.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/value/tls_buffer.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/util/arch/mod.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/util/arch/x86_64.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/util/string.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/src/util/utf8.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/sonic-simd/src/lib.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/sonic-simd/Cargo.toml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/sonic-simd/README.md>
  - <https://github.com/cloudwego/sonic-rs/blob/main/sonic-number/README.md>
  - <https://github.com/cloudwego/sonic-rs/blob/main/sonic-number/src/lib.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/sonic-number/src/lemire.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/sonic-number/src/arch/mod.rs>
  - <https://github.com/cloudwego/sonic-rs/blob/main/benchmarks/Cargo.toml>
  - <https://github.com/cloudwego/sonic-rs/blob/main/benchmarks/benches/deserialize_struct.rs>
  - <https://github.com/cloudwego/sonic-rs/issues>
  - <https://github.com/cloudwego/sonic-rs/issues/239>
  - <https://github.com/cloudwego/sonic-rs/issues/232>
  - <https://github.com/cloudwego/sonic-rs/issues/228>
  - <https://github.com/cloudwego/sonic-rs/issues/114>
  - <https://github.com/cloudwego/sonic-rs/issues/245>
  - <https://github.com/cloudwego/sonic-rs/issues/150>
  - <https://github.com/cloudwego/sonic-rs/issues/182>
  - <https://crates.io/api/v1/crates/sonic-rs>
  - <https://crates.io/api/v1/crates/zmij>
  - <https://doc.rust-lang.org/std/primitive.pointer.html>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/cloudwego/sonic-rs`) · [data/wave4/enrich/raw/github_com_cloudwego_sonic_rs.json](../../../data/wave4/enrich/raw/github_com_cloudwego_sonic_rs.json) (enrichment confidence 0.86)

</details>
