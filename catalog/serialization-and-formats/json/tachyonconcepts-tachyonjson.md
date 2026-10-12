# Tachyon JSON (Rust, TachyonConcepts)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟡 stale

> Tiny unsafe Rust JSON writer for compile-time-constant objects into a fixed stack buffer; claims 8 ns vs serde_json's 23 ns.

| | |
|---|---|
| **Beats** | serde_json |
| **Claimed result** | Serde (zero-copy): 23 ns; Tachyon JSON: 8 ns, 1,000,000 iterations encoding {"message":"Hello, world!"} (\~2.9x faster, derived from page data) |
| **Workload** | Encoding a small fixed JSON object ({"message":"Hello, world!"}) over 1,000,000 iterations, zero-copy serde_json vs Tachyon buffer encode |
| **Metric** | latency |
| **Adoption** | 0 stars; 913 crates.io downloads (tachyon_json 1.0.1) |
| **Last commit** | 2025-07-21 |
| **Links** | [repository](https://github.com/TachyonConcepts/TachyonJson) · [benchmark](https://github.com/TachyonConcepts/TachyonJson#-performance) |

## Verdict

The README's only data is one pair of numbers: encoding {"message":"Hello, world!"} over 1,000,000 iterations took 23 ns with serde_json ('zero-copy') and 8 ns with Tachyon JSON (\~2.9x, derived). No benchmark code, CPU, compiler or serde_json version is published (the repo's .cargo/config.toml sets target-cpu=native, opt-level=3), and the Tachyon side encodes a compile-time-constant object with escaping off, through copy paths specialized for this payload's 7- and 13-byte strings, so it is not a like-for-like comparison.

## Use it when

- A fixed, string-only response known at compile time, such as the TechEmpower-style `/json` endpoint `{"message":"Hello, World!"}`. That is exactly how the author's own TachyonConcept web server uses it: `tachyon_object_noescape!` into a `TachyonBuffer<100>`.
- Hot paths where you control every key and value and can guarantee they contain no `"`, `\` or control characters, so skipping escaping is correct.
- Tiny outputs with a hard, known upper bound on size, so a stack buffer of size N can never be overrun.
- As a reference for how far a hand-specialized, unchecked writer can drop below serde_json on a trivial payload. It is small enough to read in one sitting and borrow the idea from, rather than to depend on.

## Skip it when

- Serializing your own Rust structs or enums, or anything using serde derives: there is no Serialize integration and no parser at all.
- Untrusted or arbitrary strings: object keys are never escaped, and with no_escape=true values are not either, so a `"` in the data produces invalid or injectable JSON.
- Output whose size you cannot bound: braces, quotes, commas, unescaped bytes and `tcopy!` copies are unchecked, so going over N writes past the buffer (undefined behavior) rather than failing.
- Integers above 2^53 or non-finite floats: Number is f64 only, and ryu's `format` prints NaN/inf/-inf, which are not valid JSON.
- Anything that needs a maintained dependency: 3 commits all on 2025-07-21, no tests, no doc comments, no issues, 0 stars, no crates.io reverse dependencies.

## How it is fast

There is no allocation and no serializer state: output goes into a caller-owned fixed-size array, and most writes (`write_char_fast`, `write_raw_bytes`, the `tcopy!` macro) skip bounds checks. With no_escape=true, string values are memcpy'd instead of scanned for characters to escape, and object keys are never escaped in either mode. `tcopy!` has hand-written fixed-width copy paths for exactly 7-byte strings (one unaligned u64 load/store) and 13-byte strings (u64 + u32 + 1 byte), the lengths of "message" and "Hello, world!" in the benchmark payload; numbers go through ryu. Because the benchmarked object is a compile-time constant, the runtime work is essentially copying 27 bytes.

## Compared with alternatives

sonic-rs is the catalogued serde_json alternative that covers serde into structs, an untyped Value, and both parsing and serialization, and simd-json (Rust), jiter and pikkr are catalogued for parsing. Pick Tachyon JSON only when you would otherwise hardcode the bytes of a fixed, trusted object in a bounded buffer; for any real data model, sonic-rs or serde_json itself is the safer choice.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | ryu 1 |
| **Minimum toolchain** | Rust 1.85+ implied by edition 2024 (no rust-version declared); the author's consumer project pins nightly |
| **Platforms** | any per source (portable Rust, unaligned access via ptr::read_unaligned, no SIMD or arch intrinsics); the repo's .cargo/config.toml builds with target-cpu=native |
| **Thread safety** | not documented; TachyonValue/TachyonObject hold raw pointers so they are !Send/!Sync, while TachyonBuffer is a plain value type (use one per thread) |
| **Drop-in for the baseline** | no |

## Gotchas

- Bounds checking is inconsistent. `write`/`write_str` (numbers, true/false/null, escape sequences) check capacity and set a private error flag, but `write_char_fast` and `tcopy!` do not. The error flag has no public getter, and `reset_pos()` does not clear it, so once it is set every later checked write on that buffer is silently dropped.
- `tcopy!`'s 7-byte path reads 8 bytes from the source string and stores 8 bytes into the buffer, one past each. Reading past the end of a `&str` is undefined behavior in Rust even when it happens to work for literals in .rodata.
- `FastStr::as_str(len)` is a safe fn that builds a `&'static str` from a raw pointer and any caller-supplied length, so safe code can trigger UB. A hand-built `TachyonObject` holds a raw pointer with no borrow on its pair array, so it can dangle.
- `encode`, `as_slice` and `as_str` are `unsafe fn` with no documented safety contract, and `as_str` returns "" on invalid UTF-8. A top-level `Undefined` sets the error flag, while `Undefined` inside objects and arrays is silently skipped.

## Known shortcomings

- No benchmark code in the repo; the Tachyon side uses a no-escape macro and unsafe encode, so it may skip escaping that serde_json does. 0 stars, stale since 2025-07.
- The benchmark is tuned to its own payload: tcopy! has hand-written paths for exactly 7- and 13-byte strings ('message', 'Hello, world!'), and the Tachyon side encodes a compile-time object with escaping off. Built for one TechEmpower-style /json endpoint. Most writes skip bounds checks (stack buffer overflow on larger output), the 7-byte path reads past the string, and keys are never escaped. NaN/inf print as invalid JSON. Writer only, compile-time objects only, no serde integration; 3 commits, no tests.

## Caveats and trade-offs

No benchmark code published in the repo (numbers cannot be reproduced); no CPU model or compiler version stated (.cargo/config.toml builds with target-cpu=native, opt-level=3); single trivial fixed-message microbenchmark; README usage encodes with tachyon_object_noescape! and an unsafe encode call, so the Tachyon side may skip string escaping that serde_json always does; Cargo.toml says 'MIT OR Apache-2.0' but the LICENSE file is MIT only; 0 stars, 3 commits, very small/early project; distinct repo from mrcodechef/Tachyon.JSON which is already on the known list

Requires unsafe code and manual opt-in for escaping (tachyon_object_noescape! skips escaping by default); fixed-size stack buffer (TachyonBuffer&lt;N&gt;); appears to be a serializer only, no documented parser

## Maintenance

Stale since its single day of commits (2025-07-21), with \~900 crates.io downloads and nothing depending on it; it is MIT per LICENSE (Cargo.toml says MIT OR Apache-2.0) and small enough to vendor, but it is a companion to the author's web server that bills itself as 'powered by undefined behavior and bad ideas', which matches this code's unchecked writes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section gives only two first-party numbers (Serde zero-copy 23 ns vs Tachyon JSON 8 ns, 1,000,000 iterations on {"message":"Hello, world!"}); no benchmark code is in the repo (only src/buffer.rs, lib.rs, macros.rs, value.rs) and no CPU or compiler is stated, so C.
- **Verifier notes:** Numbers match the README exactly; the \~2.9x ratio was unmarked in the record and is now labelled as derived. Metadata (MIT, last commit 2025-07-21, stale, not fork) checked via gh and is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/TachyonConcepts/TachyonJson#-performance>
  - <https://github.com/TachyonConcepts/TachyonJson>
  - <https://crates.io/api/v1/crates/tachyon_json>
- **Sources the enricher read:**
  - <https://github.com/TachyonConcepts/TachyonJson>
  - <https://github.com/TachyonConcepts/TachyonJson#-performance>
  - <https://github.com/TachyonConcepts/TachyonJson/blob/main/README.md>
  - <https://github.com/TachyonConcepts/TachyonJson/blob/main/Cargo.toml>
  - <https://github.com/TachyonConcepts/TachyonJson/blob/main/Cargo.lock>
  - <https://github.com/TachyonConcepts/TachyonJson/blob/main/.cargo/config.toml>
  - <https://github.com/TachyonConcepts/TachyonJson/blob/main/LICENSE>
  - <https://github.com/TachyonConcepts/TachyonJson/blob/main/src/lib.rs>
  - <https://github.com/TachyonConcepts/TachyonJson/blob/main/src/macros.rs>
  - <https://github.com/TachyonConcepts/TachyonJson/blob/main/src/buffer.rs>
  - <https://github.com/TachyonConcepts/TachyonJson/blob/main/src/value.rs>
  - <https://github.com/TachyonConcepts/TachyonJson/commits/main>
  - <https://github.com/TachyonConcepts/TachyonJson/issues>
  - <https://github.com/TachyonConcepts/TachyonJson/pulls>
  - <https://crates.io/api/v1/crates/tachyon_json>
  - <https://crates.io/api/v1/crates/tachyon_json/reverse_dependencies>
  - <https://docs.rs/tachyon_json/1.0.1/tachyon_json/>
  - <https://docs.rs/crate/tachyon_json/1.0.1/builds.json>
  - <https://github.com/TachyonConcepts>
  - <https://github.com/TachyonConcepts/TachyonConcept>
  - <https://github.com/TachyonConcepts/TachyonConcept/blob/main/Cargo.toml>
  - <https://github.com/TachyonConcepts/TachyonConcept/blob/main/src/main.rs>
  - <https://github.com/TachyonConcepts/TachyonConcept/blob/main/src/library/server.rs>
  - <https://github.com/TachyonConcepts/TachyonConcept/blob/main/rust-toolchain.toml>
  - <https://docs.rs/ryu/1.0.20/ryu/struct.Buffer.html>
  - <https://github.com/cloudwego/sonic-rs>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/tachyonconcepts/tachyonjson`) · [data/wave4/enrich/raw/github_com_tachyonconcepts_tachyonjson.json](../../../data/wave4/enrich/raw/github_com_tachyonconcepts_tachyonjson.json) (enrichment confidence 0.8)

</details>
