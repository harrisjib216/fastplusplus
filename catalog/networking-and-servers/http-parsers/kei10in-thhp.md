# thhp (Totemo-Hayai HTTP Parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🔴 abandoned

> Small zero-copy Rust HTTP/1.x parser; beats picohttpparser only on short requests (1.14-1.29x), ties or loses on realistic ones.

| | |
|---|---|
| **Beats** | picohttpparser |
| **Claimed result** | README cargo bench output. With RUSTFLAGS="-C target-feature=+sse4.2": full request thhp 4421 MB/s (159 ns/iter +/- 23) vs picohttpparser 4393 MB/s (160 ns/iter +/- 37), about 1.006x (derived from page data), within the stated noise; short request thhp 1600 MB/s vs picohttpparser 1244 MB/s, about 1.29x (derived from page data). Without the flag: full request thhp 3550 MB/s vs picohttpparser 4594 MB/s, so thhp is slower (about 0.77x, derived from page data); short request thhp 1513 MB/s vs picohttpparser 1333 MB/s, about 1.14x (derived from page data). |
| **Workload** | cargo nightly bench (built-in #[bench], black_box) parsing a realistic full HTTP request and a short request, comparing thhp against picohttpparser-sys bindings and Rust's httparse crate |
| **Metric** | throughput |
| **Compiler and flags** | cargo +nightly bench (nightly version unstated); Cargo.toml [profile.bench] sets opt-level=3, lto=true, codegen-units=1; the explicit run sets RUSTFLAGS="-C target-feature=+sse4.2" and the implicit run sets no RUSTFLAGS; the baseline picohttpparser-sys 1.0 is built with its "sse4" feature in both runs |
| **Adoption** | 15 stars; about 5,000 all-time crates.io downloads (41 recent), latest version 0.2.0 (2018) |
| **Last commit** | 2018-12-22 |
| **Links** | [repository](https://github.com/kei10in/thhp) · [benchmark](https://github.com/kei10in/thhp/blob/master/README.md#benchmark) |

## Verdict

These are the author's own cargo +nightly #[bench] results (opt-level 3, LTO, codegen-units=1; nightly version, CPU and OS not stated). The baseline is picohttpparser as vendored in picohttpparser-sys 1.0, compiled by the cc crate with -msse4 and called over FFI, with httparse 1.3 as a third contestant. With RUSTFLAGS +sse4.2, the \~700-byte browser request took 159 vs 160 ns (a tie within noise) and the 56-byte request 35 vs 45 ns (\~1.29x). With default flags the results were 198 vs 153 ns (pico \~1.29x faster) and 37 vs 42 ns (\~1.14x). Each configuration is a single pasted run with no hardware stated and no third-party reproduction.

## Use it when

- A Rust server or proxy whose traffic is mostly small requests (tens of bytes, a few short headers). On the 56-byte request the README shows 35-37 ns for thhp vs 42-45 ns for picohttpparser (via FFI) and 41 ns for httparse 1.3.
- You want a tiny parser to vendor and change: about 1.2k lines including tests, MIT, no runtime dependencies (arrayvec 0.4 is optional), and a simple Complete/Incomplete API over &str slices.
- You control the x86-64 build and can pass RUSTFLAGS="-C target-feature=+sse4.2" (or an equivalent target-cpu). Only with that flag did the \~700-byte browser request reach parity with pico (159 vs 160 ns).
- Internal or controlled traffic where a strict ASCII-only policy is acceptable or wanted: control bytes and all bytes &gt;= 0x80 in the target, header values and reason phrase are rejected.

## Skip it when

- Realistic header-heavy browser requests on a default build. Without the explicit SSE4.2 flag, thhp took 198 ns vs pico's 153 ns (pico \~1.29x faster). With the flag, its 0.6% lead sits inside the +/-23 ns and +/-37 ns spreads.
- Public-facing traffic that may carry raw UTF-8 or obs-text bytes in paths, cookies or header values. thhp returns InvalidPath or InvalidFieldValue on those, while the pico version it was benchmarked against allows bytes &gt;= 0x80.
- You need what pico or httparse provide beyond the head parser: chunked-body decoding, obs-fold continuation lines (rejected as InvalidFieldName), pico's last_len incremental re-check (thhp re-parses from byte 0 on every call), or a C ABI.
- Anything that needs upkeep. The last commit and the 0.2.0 release are both from 2018-12-22. No issue or PR was ever filed, crates.io lists 0 reverse dependencies, no rust-version is declared, and the only CI was Travis in 2018.
- Non-x86 or no_std targets: they get the scalar table path only (no NEON or AVX2), and no_std mode needs nightly because of #![feature(alloc)].

## How it is fast

Character classes are 256-entry bool lookup tables (tchar, field-value and reason-phrase), scanned by a hand-unrolled 8-bytes-per-step loop (Scanner::read_while_continue_with), which is the same shape as pico's non-SSE path. Header values alone get an SSE4.2 path. PCMPESTRI (_mm_cmpestri with _SIDD_CMP_RANGES) scans 16-byte blocks for the first byte in 0x00-0x08, 0x0A-0x1F or 0x7F-0xFF, which is the same trick as pico's findchar_fast, and tails under 16 bytes fall back to scalar. Parsing is generic over the header collection and builds &str views with from_utf8_unchecked (sound because the tables admit ASCII only), so it monomorphizes and inlines fully under the bench profile's LTO with codegen-units=1. The README does not say why thhp wins on the short request. In the bench, pico is called over FFI, so its fixed per-call cost weighs more on a 56-byte request, and thhp never uses SIMD for the method, target or header names.

## Compared with alternatives

Among the Rust siblings, httparse is the default pick: it is maintained (last push 2026-06-30), has SSE4.2/AVX2/NEON/SWAR modules and supports no_std on stable. picohttpparser-rs wins only on header-heavy inputs and loses on tiny ones, while thhp is the reverse. Pick thhp only if you want a vendorable parser tuned for small requests (35-37 ns vs httparse 41 ns and pico 42-45 ns in its own 2018 bench); to beat pico in C by real margins, the vkrasnov AVX2 fork or httpp report much larger gains.

## Integration

| | |
|---|---|
| **Form** | crate (thhp 0.2.0 on crates.io; about 1.2k lines, easy to vendor) |
| **Dependencies** | none at runtime; optional arrayvec 0.4; build-dependency version_check 0.1 |
| **Minimum toolchain** | Not declared. The library targeted stable Rust (2018 Travis matrix: stable/beta/nightly; the last commit dropped the 1.20.0 job). build.rs enables SIMD only on rustc &gt;= 1.27. The code is 2015-edition with crate:: paths, which by inference needs rustc 1.30+. The benches (#![feature(test)]) and no_std mode need nightly. It was not rebuilt on a current rustc. |
| **Platforms** | Any target for the scalar path. x86/x86-64 builds with the std feature get the SSE4.2 header-value path, chosen at runtime by is_x86_feature_detected!. No NEON or AVX2. |
| **Thread safety** | Not documented. Request::parse and Response::parse are stateless functions over a caller-owned buffer and header collection, and the only statics are const lookup tables. |
| **Drop-in for the baseline** | no |

## Gotchas

- The Vec impl never grows: its capacity is the hard header limit, so Vec::new() fails with OutOfCapacity on the first header. The ArrayVec impl is fixed at 16 headers.
- The returned headers slice is the whole collection, and headers pushed before an Incomplete result stay in it. Call headers.clear() before every parse and every retry, as the bench does, or you get stale or duplicate headers.
- It is lenient in some places, per the code. An empty method (' / HTTP/1.1'), an empty target ('GET  HTTP/1.1') and an empty header name (':v') all parse successfully. Bare LF line endings are accepted, and header values keep their trailing whitespace. Responses must have a space after the 3-digit status, so 'HTTP/1.1 200\r\n' is rejected with InvalidStatusCode.
- The SSE4.2 path covers only header values of 16 bytes or more, with a runtime feature check on each call. find_fast has no #[target_feature(enable = "sse4.2")], so without RUSTFLAGS the PCMPESTRI intrinsic is probably not inlined. That fits the slower 'implicit SSE4.2' full-request result (198 vs 159 ns).

## Known shortcomings

- Inconsistent: on the full request it is within noise of picohttpparser with SSE4.2 and about 0.77x without it; wins only on the short request. Rust, abandoned since 2018.
- Only consistent win is the 56-byte request (1.14-1.29x); on a \~700-byte request it ties with RUSTFLAGS +sse4.2 and loses without it (198 vs 153 ns). One first-party run, no CPU or rustc version; pico is called over FFI, which weighs most on the tiny request. Rejects all bytes &gt;= 0x80 but accepts an empty method, target or header name; obs-fold rejected. Header Vec never grows (Vec::new() fails on the first header) and must be cleared before every parse/retry. No chunked decoder, no C ABI. Nightly needed for no_std and benches; untouched since 2018-12, 0 reverse dependencies.

## Caveats and trade-offs

Numbers are first-party only, with no CPU model and no nightly rustc version stated. On the full, realistic request the win over picohttpparser is only there with explicit SSE4.2, and even then it is about 0.6%, inside the +/- noise shown. Without the flag thhp is about 23% slower on that request. The consistent win is on the short request (about 1.29x with explicit SSE4.2, about 1.14x without), and only there. The README makes no explicit 'faster than picohttpparser' claim beyond its 'Very Fast HTTP Parser' title and the bench output. Last commit was in 2018.

requires Rust nightly (uses unstable #[bench]); results are inconsistent across the two reported runs, so any speed advantage over picohttpparser is not robust

## Maintenance

Abandoned since 2018-12-22 (the date of both the last commit and the 0.2.0 release; 15 stars, \~5,000 all-time downloads, 0 reverse dependencies). It is MIT and small with no runtime dependencies, so it can be vendored, but nothing has built it since its 2018 Travis CI and it was not built for this entry.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are first-party cargo #[bench] output pasted into the README. The benchmark code (benches/parse.rs) is public and compares against picohttpparser via picohttpparser-sys, but no CPU model or rustc nightly version is given, so it is C.
- **Verifier notes:** The benchmark_url (benches/parse.rs) is the bench code and does compare against picohttpparser, but it has no numbers. They are in the README Benchmark section, so benchmark_url is corrected to that. The record left out that thhp still beats pico on the short request without explicit SSE4.2 (1513 vs 1333 MB/s), so it is faster on the short request in both configurations and not a 'not-faster' reject. Tier C is unchanged.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kei10in/thhp>
  - <https://github.com/kei10in/thhp/blob/master/benches/parse.rs>
  - <https://github.com/kei10in/thhp/blob/master/README.md>
  - <https://github.com/kei10in/thhp/blob/master/Cargo.toml>
  - <https://github.com/kei10in/thhp/blob/master/LICENSE>
  - <https://crates.io/api/v1/crates/thhp>
- **Sources the enricher read:**
  - <https://github.com/kei10in/thhp>
  - <https://github.com/kei10in/thhp/blob/master/README.md>
  - <https://github.com/kei10in/thhp/blob/master/Cargo.toml>
  - <https://github.com/kei10in/thhp/blob/master/build.rs>
  - <https://github.com/kei10in/thhp/blob/master/.travis.yml>
  - <https://github.com/kei10in/thhp/blob/master/src/lib.rs>
  - <https://github.com/kei10in/thhp/blob/master/src/scanner.rs>
  - <https://github.com/kei10in/thhp/blob/master/src/simd.rs>
  - <https://github.com/kei10in/thhp/blob/master/src/errors.rs>
  - <https://github.com/kei10in/thhp/blob/master/src/vec_header.rs>
  - <https://github.com/kei10in/thhp/blob/master/src/arrayvec_header.rs>
  - <https://github.com/kei10in/thhp/blob/master/benches/parse.rs>
  - <https://github.com/kei10in/thhp/blob/master/tests/tests.rs>
  - <https://github.com/kei10in/thhp/blob/master/LICENSE>
  - <https://github.com/kei10in/thhp/issues?q=is%3Aissue+OR+is%3Apr>
  - <https://github.com/kei10in/thhp/commits/master>
  - <https://github.com/kei10in/thhp/commit/4242a0d>
  - <https://github.com/kei10in/thhp/commit/eebe5e5>
  - <https://github.com/kei10in/thhp/commit/bc42b0f>
  - <https://github.com/kei10in/thhp/commit/a5be67c>
  - <https://github.com/kei10in/thhp/tags>
  - <https://crates.io/api/v1/crates/thhp>
  - <https://crates.io/api/v1/crates/thhp/reverse_dependencies>
  - <https://docs.rs/thhp/0.2.0/thhp/>
  - <https://crates.io/api/v1/crates/picohttpparser-sys>
  - <https://github.com/kevinswiber/picohttpparser-sys/blob/HEAD/build.rs>
  - <https://github.com/kevinswiber/picohttpparser-sys/blob/HEAD/deps/picohttpparser/picohttpparser.c>
  - <https://github.com/seanmonstar/httparse>
  - <https://github.com/seanmonstar/httparse/blob/HEAD/README.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/kei10in/thhp`) · [data/wave5/enrich/raw/github_com_kei10in_thhp.json](../../../data/wave5/enrich/raw/github_com_kei10in_thhp.json) (enrichment confidence 0.45)

</details>
