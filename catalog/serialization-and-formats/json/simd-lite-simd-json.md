# simd-json (Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust port of simdjson with serde support; 1.2-2.7x faster DOM parsing than serde_json in json-benchmark.

| | |
|---|---|
| **Beats** | serde_json |
| **Claimed result** | DOM parse: canada.json 380 vs serde_json 320 MB/s (\~1.19x), citm_catalog.json 720 vs 420 MB/s (\~1.71x), twitter.json 810 vs 300 MB/s (\~2.7x); struct parse: canada.json 580 vs 580 MB/s (1.0x), citm_catalog.json 1220 vs 710 MB/s (\~1.72x), twitter.json 1050 vs 550 MB/s (\~1.91x) (ratios derived from page data) |
| **Workload** | serde-rs/json-benchmark, a Rust port of nativejson-benchmark: in-memory parse to DOM (simd-json BorrowedValue vs serde_json Value), parse to typed structs, and DOM stringify of canada.json, citm_catalog.json and twitter.json; the best of 256 trials is kept, and the README takes the better of two runs |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6600U @ 2.60GHz (2015 laptop CPU) |
| **Compiler and flags** | rustc 1.59.0-nightly (0b6f079e4 2021-12-07); cargo run --release with RUSTFLAGS -C target-cpu=native (.cargo/config); release profile debug=true, panic=abort; jemalloc global allocator |
| **Adoption** | 1.4k stars |
| **Last commit** | 2026-08-23 |
| **Links** | [repository](https://github.com/simd-lite/simd-json) · [benchmark](https://github.com/serde-rs/json-benchmark/blob/master/README.md) |

## Verdict

serde-rs/json-benchmark (2021; simd-json 0.4.11 vs serde_json 1.0.72; best of 256 trials; rustc 1.59.0-nightly with target-cpu=native and jemalloc; Intel i7-6600U) measured DOM parse 1.19x/1.71x/2.7x and struct parse 1.0x/1.72x/1.91x faster on canada/citm_catalog/twitter JSON, with DOM stringify mixed (slower on twitter, 890 vs 910 MB/s). simd-json's timer excludes its per-trial buffer copy and its BorrowedValue borrows strings that serde_json::Value owns; a 2026 real-workload run (simd-json 0.13, OwnedValue plus a copy, i7-6820HQ) showed only 1.05-1.10x.

## Use it when

- You parse into a generic DOM (a serde_json::Value-style tree) from byte buffers you own and may overwrite, such as request bodies or log lines. This is where json-benchmark shows 1.2-2.7x over serde_json.
- The documents are string- and key-heavy (twitter.json and citm_catalog.json shapes). There, DOM parse was 1.7-2.7x and struct parse 1.7-1.9x faster than serde_json.
- The workload is read-mostly and repeated: use the tape or lazy value and reuse one Buffers across calls (to_tape_with_buffers, from_slice_with_buffers) to amortize allocations.
- You already have serde Deserialize types and want a faster decoder without rewriting them, on x86-64 (AVX2 or SSE4.2), aarch64 (NEON) or wasm with simd128.
- You control the build and can ship a non-portable x86 binary: default-features = false plus RUSTFLAGS=-C target-cpu=native is the configuration the README says performs best.

## Skip it when

- Your input is immutable (&str, shared &[u8], read-only mmap). You must copy it into a mutable buffer first. In the 2026 tegridy-benchie run, which used to_vec plus OwnedValue, simd-json was only 1.05x serde_json at 1 thread and 1.10x at 8 threads.
- The data is mostly floats (canada.json shape). Struct parse tied serde_json at 580 MB/s. In issue #370's criterion run, simd_json::serde::from_slice into serde_json::Value was slower than serde_json on canada (114 vs 153 MiB/s).
- You need streaming, NDJSON, or documents of 4 GiB or more. There is no streaming parser, NDJSON is an open request (#194), and inputs of u32::MAX bytes or more return InputTooLarge.
- Memory is tight. tegridy-benchie measured peak RSS of 166 MB vs 116 MB for serde_json at 1 thread, and 450 vs 379 MB at 8 threads.
- You need object key order preserved past 32 keys (halfbrown switches to a hash map; #378 is open), or strict rejection of lone high-surrogate escapes (#481 is open: "\ud800" decodes to U+0000 instead of an error).

## How it is fast

It uses simdjson's two-stage design. Stage 1 scans 64-byte blocks with AVX2, SSE4.2, NEON or wasm simd128 byte compares, finds quoted regions with a carry-less-multiply prefix XOR (PCLMULQDQ) and odd-backslash-run detection, validates UTF-8 with simdutf8, and writes a u32 index of structural characters. Stage 2 walks that index with a goto-style state machine to build a flat tape; strings are scanned 32 bytes at a time and unescaped back into the input buffer, so BorrowedValue does not allocate per string. Floats use 8-digits-at-a-time SWAR fraction parsing, a Clinger fast path, and a 128-bit power-of-ten multiply (Eisel-Lemire style) with a std fallback, and objects use halfbrown, which stores up to 32 keys in a plain vector.

## Compared with alternatives

Against jiter, the other Rust entry with serde_json as its baseline, pick simd-json when you need serde Deserialize structs, a mutable DOM, or serialization; jiter's README lists only JsonValue, a pull iterator and Python parsing. jiter was about 1.8x faster than simd-json in the same tegridy-benchie run (209.4 vs 115.2 MB/s at 8 threads), so prefer jiter for read-only extraction; the other siblings (go-json, Sonic, jsoniter, easyjson, Jsonifier, zzzJSON, LJSON) are Go or C/C++ and are not options in Rust.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | simdutf8, value-trait, halfbrown, ref-cast; serde and serde_json through the default serde_impl feature; optional beef (beef feature) and ahash (known-key feature) |
| **Minimum toolchain** | Rust 1.88 (rust-version), edition 2024; the hints feature needs nightly |
| **Platforms** | x86/x86-64 with runtime dispatch to AVX2+PCLMULQDQ or SSE4.2; aarch64 (NEON); wasm32 (simd128 when enabled); a scalar fallback elsewhere that the README calls significantly slower. CI runs Linux, Windows, macOS and big-endian s390x. |
| **Thread safety** | Not documented. Parsing keeps no shared mutable state apart from an atomically cached CPU-dispatch function pointer. The input and Buffers are taken by &mut, so use one Buffers per thread. |
| **Drop-in for the baseline** | partial — simd_json::serde::from_slice/to_string mirror serde_json and can target serde_json::Value, but input must be &mut [u8] (from_str is unsafe and takes &mut str). The native DOM types are simd-json's own BorrowedValue/OwnedValue behind the value-trait traits, and the error types differ. |

## Gotchas

- The parser overwrites your input buffer with unescaped strings. BorrowedValue and the tape borrow from that buffer, so it must outlive them. After serde::from_str the &mut str may hold invalid UTF-8, which is why that function is unsafe.
- The crate uses 'a lot' of unsafe code (README). Soundness and availability bugs were fixed recently: #471, an out-of-bounds read through an exhausted Deserializer, fixed in 0.18.1 (2026-08-23); #473, a stack overflow on deeply nested input in to_owned_value/to_borrowed_value, fixed in 0.18 with a default max depth of 1024; and #445, missing UTF-8 validation on one fallback path, merged 2026-07-08. RUSTSEC-2019-0008 (CVE-2019-15550) covered a page-boundary read in 0.1.x. Pin 0.18.1 or later.
- Several behaviors depend on feature flags. Without value-no-dup-keys, duplicate keys make Value behavior unspecified. Integers wider than 64 bits fail to parse unless you enable big-int-as-float or 128bit. Enabling beef can break other crates in your dependency tree that use simd-json.
- The default runtime-detection build is portable but not the fastest: the SSSE3 8-digit number path is compiled only when ssse3 is enabled at compile time. The README also recommends mimalloc, jemalloc or snmalloc over the system allocator.

## Caveats and trade-offs

The json-benchmark numbers date from 2021-12-08 and use simd-json 0.4.11 and serde_json 1.0.72. The Cargo.toml that matches them is at commit c8bf3ee. The repo is archived (last push 2024-03-26), later crate bumps to simd-json 0.12 were never re-run, and simd-json is now at 0.18.1. DOM stringify is mixed: 470 vs 430, 760 vs 560, and 890 vs 910 MB/s, so simd-json is slower on twitter.json. Struct parse ties on canada.json. A recent real-workload shootout (mihailnica10/tegridy-benchie RESULTS.md, generated 2026-09-23, 0 stars, single commit) shows only near parity. That run uses simd-json 0.13.11 with runtime detection and no target-cpu=native, OwnedValue plus a buffer copy, and a fused fact-reduction step. Its results are 115.2 vs 104.3 MB/s at 8 threads (\~1.10x), 50.6 vs 48.0 MB/s at 1 thread (\~1.05x), and \~1.01x at 2 and 4 threads. serde_json is slightly ahead in its Bun 8-worker FFI pool (124.5 vs 123.0 MB/s). simd-json's own README has only a qualitative performance claim and no numbers. Good results need AVX2/SSE4.2/NEON, and the parser mutates its input buffer.

Uses substantial unsafe code for SIMD intrinsics; Rust port of simdjson's design but its own README states it does not fully reach the C++ implementation's performance; jiter beat it head-to-head in the same shootout

## Maintenance

Actively maintained (0.18.1 shipped 2026-08-23 with soundness fixes) and dual MIT OR Apache-2.0 on crates.io, but the headline numbers come from 0.4.11 in 2021 and have not been re-run independently on current versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The record's tegridy-benchie RESULTS.md numbers match the native simd-json (rust) and serde_json rows, and the harness is public (rust/simdjson.rs, rust/serde.rs, rust/runner.rs, Cargo release profile opt-level=3, lto, codegen-units=1, CPU i7-6820HQ), so it already meets A without a rustc version. A stronger A source is serde-rs/json-benchmark (src/main.rs, .cargo/config target-cpu=native, rustc 1.59.0-nightly 2021-12-07, i7-6600U), a known benchmark run by serde's own author, so benchmark_url now points there.
- **Verifier notes:** The record was accurate: the tegridy-benchie numbers belong to the simd-json (rust) rows. I switched benchmark_url to serde-rs/json-benchmark because it isolates parsing, states the full toolchain, and shows a clear 1.2-2.7x DOM-parse win. The tegridy real-workload margin (\~1.0-1.1x) is kept in caveats. The license is dual MIT OR Apache-2.0 per the README and the LICENSE-MIT/LICENSE-APACHE files (the gh API reports only Apache-2.0). Metadata checks out: 1,422 stars, last commit 2026-08-23, not archived, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
  - <https://github.com/mihailnica10/tegridy-benchie>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/README.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/README.benchmark.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/Makefile>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/results.json>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/Cargo.toml>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/Cargo.lock>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/serde.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/simdjson.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/runner.rs>
  - <https://github.com/simd-lite/simd-json>
  - <https://github.com/simd-lite/simd-json/blob/main/README.md>
  - <https://github.com/simd-lite/simd-json/blob/main/Cargo.toml>
  - <https://github.com/serde-rs/json-benchmark>
  - <https://github.com/serde-rs/json-benchmark/blob/master/README.md>
  - <https://github.com/serde-rs/json-benchmark/blob/master/src/main.rs>
  - <https://github.com/serde-rs/json-benchmark/blob/master/.cargo/config.toml>
  - <https://github.com/serde-rs/json-benchmark/blob/master/Cargo.toml>
  - <https://github.com/serde-rs/json-benchmark/blob/c8bf3ee/Cargo.toml>
  - <https://github.com/simd-lite/simd-json/blob/v0.13.11/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/simd-lite/simd-json>
  - <https://github.com/simd-lite/simd-json/blob/main/README.md>
  - <https://github.com/simd-lite/simd-json/blob/main/Cargo.toml>
  - <https://github.com/simd-lite/simd-json/blob/main/src/lib.rs>
  - <https://github.com/simd-lite/simd-json/blob/main/src/serde.rs>
  - <https://github.com/simd-lite/simd-json/blob/main/src/value.rs>
  - <https://github.com/simd-lite/simd-json/blob/main/src/value/lazy.rs>
  - <https://github.com/simd-lite/simd-json/blob/main/src/stage2.rs>
  - <https://github.com/simd-lite/simd-json/blob/main/src/impls/avx2/deser.rs>
  - <https://github.com/simd-lite/simd-json/blob/main/src/impls/avx2/stage1.rs>
  - <https://github.com/simd-lite/simd-json/blob/main/src/numberparse.rs>
  - <https://github.com/simd-lite/simd-json/blob/main/src/numberparse/correct.rs>
  - <https://github.com/simd-lite/simd-json/blob/main/.cargo/config.toml>
  - <https://github.com/simd-lite/simd-json/blob/main/.github/workflows/tests.yml>
  - <https://github.com/simd-lite/simd-json/blob/main/.github/workflows/big-endian.yml>
  - <https://github.com/simd-lite/simd-json/commits/main>
  - <https://github.com/simd-lite/simd-json/issues>
  - <https://github.com/simd-lite/simd-json/issues/471>
  - <https://github.com/simd-lite/simd-json/issues/457>
  - <https://github.com/simd-lite/simd-json/issues/481>
  - <https://github.com/simd-lite/simd-json/issues/473>
  - <https://github.com/simd-lite/simd-json/pull/445>
  - <https://github.com/simd-lite/simd-json/issues/480>
  - <https://github.com/simd-lite/simd-json/issues/370>
  - <https://github.com/simd-lite/simd-json/issues/378>
  - <https://github.com/simd-lite/simd-json/issues/468>
  - <https://github.com/serde-rs/json-benchmark>
  - <https://github.com/serde-rs/json-benchmark/blob/master/README.md>
  - <https://github.com/serde-rs/json-benchmark/blob/master/src/main.rs>
  - <https://github.com/serde-rs/json-benchmark/blob/master/.cargo/config.toml>
  - <https://github.com/serde-rs/json-benchmark/blob/c8bf3ee/Cargo.toml>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/RESULTS.md>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/simdjson.rs>
  - <https://github.com/mihailnica10/tegridy-benchie/blob/main/rust/Cargo.toml>
  - <https://github.com/pydantic/jiter/blob/main/README.md>
  - <https://github.com/rustsec/advisory-db/blob/main/crates/simd-json/RUSTSEC-2019-0008.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/simd-lite/simd-json`) · [data/wave4/enrich/raw/github_com_simd_lite_simd_json.json](../../../data/wave4/enrich/raw/github_com_simd_lite_simd_json.json) (enrichment confidence 0.82)

</details>
