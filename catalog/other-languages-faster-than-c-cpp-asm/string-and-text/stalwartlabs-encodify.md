# encodify (Rust Base64, Base32 and Quoted-Printable codecs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust SIMD Base64/Base32/quoted-printable codecs for mail protocols; matches or beats simdutf 7.7.1 (C++) on Base64 and MIME Base64.

| | |
|---|---|
| **Beats** | simdutf (C++) Base64 codec, called through the simdutf Rust crate |
| **Claimed result** | README criterion throughput, encodify vs simdutf (C++ via the simdutf 0.7 crate), 64 KiB. Apple M5 Max (NEON): Base64 encode 25.73 vs 25.95 GB/s (1.0x, simdutf marginally ahead); decode 18.12 vs 15.38 (1.2x); MIME encode with CRLF 21.27 vs simdutf LF-only 14.35 (1.5x); MIME decode 14.08 vs 10.08 (1.4x). AMD EPYC Zen 2 (AVX2, 4-vCPU VM): encode 19.17 vs 13.96 (1.4x); decode 14.97 vs 11.23 (1.3x); MIME encode 10.72 vs 9.50 (1.1x); MIME decode 8.61 vs 5.20 (1.7x). At 32 B: simdutf decode is about 3x slower (Apple 2.02 vs 6.08, AMD 0.56 vs 1.63); simdutf leads Apple MIME encode (5.75 vs 4.50) and AMD plain encode (1.99 vs 1.88). Against the fastest crate overall, the summary table shows parity with Rust base64-turbo for plain Base64 on AMD (19.2 and 15.0 GB/s, 1.0x). |
| **Workload** | Criterion throughput (GB/s) of Base64 encode and decode, MIME Base64 with 76-column CRLF lines, Base32 and Quoted-Printable at 32 B, 1 KiB, 64 KiB and 1 MiB (cargo bench --bench codec). |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max (NEON) and AMD EPYC Zen 2 (AVX2) |
| **Compiler and flags** | Criterion via 'cargo bench --bench codec' (bench profile inherits release opt-level 3, debug = true); benchmarks need Rust 1.93 or later, exact rustc not stated. simdutf C++ (version 7.7.1, vendored by simdutf-rs 0.7.0) is compiled by the cc crate with -std=c++17 and no explicit optimisation flags, so it takes cargo's opt-level (-O3 under the bench profile, inferred from cc defaults). C++ compiler not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README: SIMD kernels for NEON and SSSE3/AVX2 with runtime detection, output appended to caller-owned buffers or slices without zero-filling or hidden reallocations. |
| **Adoption** | 1 star, 0 forks, 3 commits; crates.io 858 downloads (encodify 1.0.2; first published 2026-09-28) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/stalwartlabs/encodify) · [benchmark](https://github.com/stalwartlabs/encodify) |

## Verdict

Author's criterion runs (cargo bench --bench codec, bench profile at opt-level 3, rustc and C++ compiler versions not stated) of encodify against simdutf 7.7.1 C++ called through the simdutf 0.7.0 crate, on an Apple M5 Max (NEON) and a 4-vCPU AMD EPYC Zen 2 VM (AVX2): at 64 KiB encodify ties simdutf on Apple plain encode (25.7 vs 26.0 GB/s), leads it 1.2x to 1.7x on the other Base64 and MIME rows (simdutf's MIME encode rows emit LF only), and ties the Rust base64-turbo crate on AMD plain Base64.

## Use it when

- Rust mail, IMAP, JMAP or DKIM code that decodes MIME Base64 bodies with 76-column CRLF lines: 14.1 vs 10.1 GB/s (Apple M5 Max) and 8.6 vs 5.2 GB/s (Zen 2 AVX2) over simdutf 7.7.1 at 64 KiB.
- Many small Base64 values (tokens, header encoded words, 32-byte blobs) decoded from Rust, where calling simdutf through FFI costs about 3x (6.08 vs 2.02 GB/s on Apple, 1.63 vs 0.56 on AMD at 32 B).
- Quoted-printable or Base32 hot paths: 5x to 9x the quoted_printable crate and 3x to 6.5x data-encoding at 64 KiB in the author's tables.
- One dependency-light crate (memchr, simdutf8) that also covers RFC 2047 words, IMAP UTF-7, PEM and folded vCard/iCalendar values.
- Targets without SIMD support in Rust (wasm32, RISC-V, 32-bit ARM): the portable table-driven fallbacks are 1.0x to 2.7x the base64 crate in the README.

## Skip it when

- C or C++ code: it is a Rust crate with no C API; use simdutf directly, and a current 9.x release rather than the 7.7.1 that was benchmarked.
- Bulk plain Base64 encode: parity with simdutf on Apple (25.7 vs 26.0 GB/s) and with the Rust base64-turbo crate on AMD (19.2 vs 19.9 GB/s); on AVX-512 machines simdutf has Ice Lake base64 kernels while encodify stops at AVX2.
- You need WHATWG forgiving-base64 semantics (JavaScript atob): encodify's STANDARD engine is strict and rejects whitespace, so you must pick LENIENT or MIME explicitly and check that its padding rules match.
- Risk-averse dependency policies: 3 commits, 1 star, first release 2026-09-28, one reverse dependency on crates.io (jmap-client), only first-party benchmarks.

## How it is fast

Hand-written SIMD kernels: on aarch64 NEON (vld3q/vst4q deinterleave plus 64-entry vqtbl4q_u8 table lookups), on x86 SSSE3 and AVX2 pshufb nibble-table classification with 16-bit multiplies (mullo_epi16) for bit shuffling, picked by runtime feature detection. MIME bodies get dedicated line kernels: the decoder detects a run of equal-length lines from the first two lines (inputs of 512 bytes or more) and decodes across CRLF breaks without a separate strip pass, and the encoder writes CRLF between 76-column lines in the same pass. Output goes into caller-owned buffers through MaybeUninit without zero-filling; the portable fallbacks use table-driven Base64 (two symbols per 12-bit lookup when encoding, four pre-shifted tables when decoding) and SWAR quoted-printable (README).

## Compared with alternatives

Take encodify when you need transfer encodings inside a Rust process rather than a CLI (uutils coreutils' base64 is a command-line tool); mail-parser already depends on encodify for its Base64 and quoted-printable body decoding, so use encodify alone when you only need the codecs without MIME parsing.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memchr 2.7, simdutf8 0.1 |
| **Minimum toolchain** | Rust 1.89 (MSRV checked in CI); running the comparison benchmarks needs Rust 1.93 or later because of base64-turbo |
| **Platforms** | aarch64 (NEON chosen at compile time), x86 and x86-64 (SSSE3 and AVX2 chosen at runtime when SSE2 is in the target baseline), portable fallbacks on every other target including wasm32, RISC-V, PowerPC, s390x and 32-bit ARM |
| **Thread safety** | not documented; engines are immutable Copy constants with no shared mutable state in the code read (src/base64/mod.rs), so they can be used from any thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry in the plain-decode row: simdutf 7.7.1's base64_to_binary follows WHATWG forgiving-base64 and skips ASCII whitespace even with LastChunkHandlingOptions::Strict (simdutf.h in simdutf-rs v0.7.0), while encodify::base64::STANDARD is a strict decoder that does no whitespace handling, so the 1.2x (Apple) and 1.3x (AMD) decode leads compare unequal work; the 3x gap at 32 B also includes simdutf's non-inlinable FFI call and runtime dispatch.
- Stale baseline: the simdutf crate 0.7.0 (still the latest on crates.io) vendors simdutf 7.7.1 from December 2025; upstream reached 9.2.1 in September 2026 with an AVX2 base64 encoder alphabet-lookup rewrite and an arm64 insert_line_feed16 optimisation, which touch exactly the rows where encodify leads (AMD encode 1.4x, Apple MIME encode 1.5x).
- README tables have not changed since the v1.0.0 commit: the AMD Base32 rows predate the AVX2 Base32 kernel added in 1.0.2 (they match the SSSE3 table within 1%), and in 1.0.0 the build script ignored --cfg encodify_scalar (fixed in 1.0.1, CHANGELOG), so the published portable-fallback table could not have come from the published 1.0.0 tree as documented.
- MIME decode speed depends on a line-shape detector: the benchmark feeds perfectly regular 76-column CRLF lines, which always hit the line kernels; irregular line lengths, LF-only mixes or inputs under 512 bytes fall back to the generic quad loop and are not benchmarked. The crate denies unsafe_code globally but the kernels and buffer module opt back in (raw-pointer and MaybeUninit writes, each with a SAFETY comment; cargo-fuzz targets exist).

## Known shortcomings

- 'Plain Base64 parity' holds only for Apple encode (AMD 1.4x/1.3x over simdutf, MIME 1.1-1.7x); baseline simdutf 7.7.1 through the simdutf-rs FFI with -O3 inferred from cc defaults; new 3-commit repo; EPYC model missing.
- Harness flaw: the plain-decode row is unequal work, since simdutf 7.7.1's base64_to_binary does WHATWG forgiving decoding (skips whitespace) even in Strict mode while encodify STANDARD is strict. The baseline is stale: the simdutf crate 0.7.0 vendors 7.7.1 (December 2025) while upstream is 9.2.1 (September 2026) with AVX2 encode and arm64 line-feed optimisations, exactly the rows encodify wins. The README is unchanged since v1.0.0: the AMD Base32 rows predate the 1.0.2 AVX2 kernel, and --cfg encodify_scalar was broken in 1.0.0, so the portable-fallback table was not made from the published tree.

## Caveats and trade-offs

New first-party repo: 3 commits, 1.0.0 published 2026-09-28, 1.0.2 on 2026-10-02. The C++ baseline is simdutf 7.7.1 as vendored by the simdutf-rs 0.7.0 crate (February 2026), not necessarily current upstream. It is called through a Rust FFI wrapper that cannot be inlined, which inflates its per-call overhead at 32 B and 1 KiB. The simdutf MIME-encode rows emit LF only (fewer bytes than encodify's CRLF), which if anything favours simdutf. Plain Base64 against simdutf is parity only for Apple encode; elsewhere encodify leads simdutf by 1.2x to 1.4x. The fastest rival there is the Rust base64-turbo crate at parity. The x86 machine is a 4-vCPU Zen 2 VM with no model given. Not a language-level claim: the win comes from hand-written NEON/SSSE3/AVX2 kernels and a fused CRLF line-wrapping path versus simdutf's own SIMD kernels. No third-party reproduction. [retier] The plain-decode row is unequal work: simdutf 7.7.1's base64_to_binary does WHATWG forgiving decoding (skips whitespace) even in Strict mode while encodify STANDARD is strict. The simdutf crate 0.7.0 vendors 7.7.1 (December 2025) while upstream is 9.2.1 (September 2026) with AVX2 encode and arm64 line-feed optimisations, exactly the rows encodify wins. The AMD Base32 rows predate the 1.0.2 AVX2 kernel, and --cfg encodify_scalar was broken in 1.0.0, so the portable-fallback table was not made from the published tree.

Mail-protocol oriented API (RFC 2045, 2047, 2152, 3501, 7468); SIMD only on NEON and x86 SSSE3/AVX2.

## Maintenance

Brand new but active (3 commits from 2026-09-28 to 2026-10-02, 1.0.2 on crates.io with about 920 downloads, Apache-2.0 OR MIT, so copyable), with first-party tier C numbers measured against a simdutf release two major versions behind upstream and a plain-decode row that compares a forgiving decoder with a strict one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's criterion tables compare against simdutf (C++) via the simdutf crate, and the bench code (benches/codec.rs) is public. The rustc and C++ compiler versions are not stated and the x86 CPU is only 'AMD EPYC, Zen 2' in a 4-vCPU VM with no model. First-party, missing compiler and exact CPU, so tier C.
- **Verifier notes:** Numbers match the README; the record's 'plain Base64 is parity with simdutf' holds only for Apple encode (AMD shows 1.3x-1.4x over simdutf; the 1.0x there is against Rust base64-turbo). simdutf is already listed (wave 7, https://github.com/simdutf/simdutf), so baseline_in_list is true. Shortcomings to record: brand-new 3-commit repo, first-party only, simdutf 7.7.1 via an FFI wrapper (small-size rows penalised), C++ build flags inferred from cc defaults, EPYC model not given. Metadata checked: Apache-2.0 OR MIT (Cargo.toml and README), last commit 2026-10-02, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `baseline_in_list`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-81 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/stalwartlabs/encodify>
  - <https://github.com/stalwartlabs/encodify/commits>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/README.md>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/benches/codec.rs>
  - <https://crates.io/api/v1/crates/encodify>
  - <https://crates.io/api/v1/crates/simdutf>
  - <https://raw.githubusercontent.com/Nugine/simdutf-rs/HEAD/build.rs>
  - <https://raw.githubusercontent.com/Nugine/simdutf-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Nugine/simdutf-rs/v0.7.0/cpp/simdutf.h>
- **Sources the enricher read:**
  - <https://github.com/stalwartlabs/encodify>
  - <https://github.com/stalwartlabs/encodify/commits/main>
  - <https://github.com/stalwartlabs/encodify/commit/1d38afb>
  - <https://github.com/stalwartlabs/encodify/commit/a9837bd>
  - <https://github.com/stalwartlabs/encodify/tree/main/src>
  - <https://github.com/stalwartlabs/encodify/tree/main/src/base64>
  - <https://github.com/stalwartlabs/encodify/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/README.md>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/build.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/benches/codec.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/.github/workflows/rust.yml>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/src/buffer.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/src/base64/mod.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/src/base64/decode/mod.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/src/base64/encode.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/src/base64/kernel/mod.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/src/base64/kernel/neon.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/encodify/HEAD/src/base64/kernel/x86.rs>
  - <https://crates.io/api/v1/crates/encodify>
  - <https://crates.io/api/v1/crates/encodify/reverse_dependencies>
  - <https://crates.io/api/v1/crates/simdutf>
  - <https://raw.githubusercontent.com/Nugine/simdutf-rs/HEAD/build.rs>
  - <https://raw.githubusercontent.com/Nugine/simdutf-rs/HEAD/cpp/simdutf.h>
  - <https://raw.githubusercontent.com/Nugine/simdutf-rs/v0.7.0/cpp/simdutf.h>
  - <https://github.com/simdutf/simdutf/releases>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/stalwartlabs/encodify`) · [data/wave14/enrich/raw/github_com_stalwartlabs_encodify.json](../../../data/wave14/enrich/raw/github_com_stalwartlabs_encodify.json) (enrichment confidence 0.6)

</details>
