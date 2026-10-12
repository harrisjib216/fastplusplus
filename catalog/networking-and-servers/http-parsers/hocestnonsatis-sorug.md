# sorug (WHATWG URL parser, Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Safe-Rust WHATWG URL parser with a zero-copy fast path for canonical URLs; 3.4-4.1x faster than the url crate on ASCII.

| | |
|---|---|
| **Beats** | url crate (servo/rust-url) |
| **Claimed result** | vs servo/url (derived from page data): \~3.4x on Fast Path ASCII (28.3 ns vs 97 ns), \~3.9x on Complex Query/Fragment (56.0 ns vs 216 ns), \~1.27x on IDNA/Punycode (196 ns vs 248 ns), \~4.1x on File Edge Case (31.1 ns vs 129 ns). The same table has sorug ahead of ada-url on all four workloads (28.3 vs 31.9, 56.0 vs 140, 196 vs 277, 31.1 vs 95.0 ns). |
| **Workload** | Criterion benchmarks (release profile, lto=true, codegen-units=1) over four URL workloads: a simple ASCII URL, a URL with complex query/fragment, an IDNA/Punycode hostname, and a file-URL edge case; nanoseconds per parse. |
| **Metric** | throughput |
| **Compiler and flags** | Cargo [profile.bench]: opt-level=3, lto=true, codegen-units=1 (Criterion 0.5); rustc version not stated (edition 2024, MSRV 1.85) |
| **Adoption** | 1 GitHub star; 442 crates.io downloads (v0.6.2) |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/hocestnonsatis/sorug) · [benchmark](https://github.com/hocestnonsatis/sorug#benchmarks) |

## Verdict

The README Criterion table (measured 2026-08-07 on 'Linux' with lto and codegen-units=1; no CPU model or rustc version given) shows sorug at 28.3, 56.0, 196 and 31.1 ns against url 2.5 at 97, 216, 248 and 129 ns on four single URLs, three of which are already canonical and hit the zero-allocation path; ada-url (Rust bindings to C++ Ada) falls between the two except on IDNA, where it is slowest. The project's own informational CI job (GitHub ubuntu-24.04 runner, rustc 1.98.1, 20 samples, 2026-09-20) shows the same ordering at about twice the absolute times: 3.5x, 4.4x, 1.16x and 4.1x faster than url, 1.66x on an 8-URL mixed batch, and 3.2x slower than url on a long-ACE IDN host.

## Use it when

- High-volume parsing of already-normalized absolute http(s)/ws(s)/ftp/file URLs (crawl frontiers, access logs, config) where the source &str outlives the Url. This is the zero-allocation path, and the project's CI measured it at about 3.5-4.4x faster than url 2.5.
- You need pure safe Rust. The main crate has forbid(unsafe_code) and needs no C++ toolchain, unlike the ada-url bindings.
- no_std + alloc or wasm32-unknown-unknown targets that need WHATWG semantics. CI checks both.
- You want Node/Ada/WPT-aligned results where rust-url differs, such as keeping empty file: path segments, rejecting an empty '@' authority, and stricter IDNA Bidi/joiner checks.
- Mixed real-world URL streams, as long as you plan for roughly a 1.6x gain over url (the 8-URL batch in the project's CI) rather than the 3-4x single-URL headline.

## Skip it when

- Long or unusual IDN hosts. The IDNA_Long_ACE case, which the README table omits, took about 11 us in three CI runs, against 3.6-4.0 us for url and about 4.9 us for ada-url (2.8-3.2x slower than url). On the ordinary IDN case, the gain over url is only about 1.2x.
- Inputs that are not canonical: uppercase scheme or host, explicit default ports, dot segments, backslashes, characters that need percent-encoding, IPv4-like hosts, or anything parsed against a base. These take the full parser and allocate, and the published numbers do not measure them.
- Production code that needs a stable, proven dependency. It is on 0.x (minor bumps may break), has a single author, 1 star, 442 total downloads and 0 reverse dependencies, and went from 0.1.0 to 0.6.2 in nine days (2026-08-01 to 2026-08-09). 1.0 is held until the fuzz reliability clocks pass.
- Code that must match rust-url output exactly, or that hands url::Url to other crates. The divergences are intentional and documented, and there is no url::Url conversion, so a crate that needs url::Url still has to re-parse the string.
- You need URLPattern, an RFC 3986 mode, or detailed parse errors. The project lists these as non-goals, and ParseError stays Failure | InputTooLong through 1.0.

## How it is fast

A pre-pass (src/parser/fast.rs) handles absolute special URLs that have no base URL and are already canonical. It recognizes the scheme with one masked 64-bit little-endian compare (https://, http://, file:///, ftp://, ws(s)://). It finds delimiters with SWAR zero-byte detection (haszero(word ^ splat(c))) for spans under 64 bytes and memchr for longer ones, and checks each byte against 256-entry lookup tables. If nothing needs rewriting, the Url borrows the input string (Backing::Borrowed) and makes no heap allocation. The record is the href string plus eight u32 component offsets and a flag byte, like rust-url's layout. Any input that needs normalization falls through to a full WHATWG state machine that writes into an owned buffer. IDN labels made only of Latin-1 lowercase, CJK, kana or Hangul characters skip NFC and the Bidi/joiner checks and go straight to Punycode.

## Compared with alternatives

Pick sorug over Ada (C++) or its ada-url Rust bindings when you want pure safe Rust with no C++ build, a rust-url-shaped API, and mostly canonical ASCII input that can stay borrowed. ada-rs and lucid-url are measured against native C++ Ada, while sorug's Ada numbers go through the ada-url FFI crate, so the numbers across these entries are not directly comparable; for IDN-heavy input or production-critical parsing, Ada's maturity is the safer choice.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memchr 2.7 and unicode-normalization 0.1 (both no-default-features); optional serde 1 and http 1. build.rs generates IDNA range tables from the vendored Unicode 17.0.0 UCD files (about 1.2 MB of text shipped in the crate). A C cdylib/staticlib plus sorug.h is available from GitHub Releases only. |
| **Minimum toolchain** | Rust 1.85 (edition 2024; MSRV checked in CI) |
| **Platforms** | Any Rust target. SWAR is portable u64 code with no arch-specific intrinsics, and memchr picks SIMD itself. CI checks no_std on wasm32. File-path and socket helpers need std on unix, windows, redox, wasi or hermit. Prebuilt FFI binaries exist for linux-x86_64, macos-aarch64 and windows-x86_64. |
| **Thread safety** | Not documented. Url&lt;'a&gt; is plain data (a &str or String plus u32 offsets, no interior mutability), so it is Send + Sync through Rust auto traits. Origin::new_opaque uses a global AtomicUsize counter. |
| **Drop-in for the baseline** | partial: the method names follow rust-url (the cookbook has a migration table), but Url carries a lifetime (call into_owned() to get 'static), host() returns the host string instead of rust-url's typed Host (use host_parsed()), ParseError has only two variants, and results follow WHATWG/Node where rust-url differs |

## Gotchas

- The zero-copy result borrows the input. Storing it, returning it, or using FromStr/TryFrom&lt;&str&gt; (which call into_owned) allocates a copy, which gives back part of the benchmarked advantage.
- The fast path runs only for Url::parse with no base URL. join() and parse_with_base always go through the full state machine and allocate.
- UTS #46 value mapping is hand-written: NFKC plus to_lowercase plus a list of special cases. The Unicode 17 tables supply only membership (disallowed, Bidi, joiners), and the module doc calls the mapping 'deliberately small ... enough for the WPT urltestdata suite'. WPT and differential fuzzing against Node, Ada and rust-url are the safety net, so rare-script hosts could still diverge from ICU.
- rust-url's host() returns a typed Host, but sorug's host() returns Option&lt;&str&gt;. Code ported by name hits type errors, and code that wants the typed value must call host_parsed().

## Known shortcomings

- Part of the win comes from borrowing its input while servo/url always allocates a String; Ada is measured through its Rust FFI crate, not native C++. No CPU or rustc version. Created 2026-07.
- The README table omits the IDNA_Long_ACE case in the same benchmark, where sorug is 2.8-3.2x slower than url (about 11 us vs 3.6-4.0 us) in all three CI runs. Three of four README inputs are already canonical and take the zero-allocation borrowed path; on a mixed 8-URL batch the gain is \~1.6x over url and \~1.44x over ada-url. ada-url edges it on set_pathname. IDNA mapping is hand-written (NFKC + lowercase + special cases), backed by differential fuzzing. The ada numbers go through the Rust bindings, so they are not comparable with sibling entries that measure native C++ Ada. 0.1.0-0.6.2 released in nine days; 0 reverse dependencies. CI (GitHub ubuntu-24.04, rustc 1.98.1) reproduces the README ordering.

## Caveats and trade-offs

Entirely first-party and unreplicated. The README says 'Numbers are indicative. Absolute values vary by CPU; relative ordering is what we track', and it gives no CPU model or rustc version, only 'Linux'. The numbers were measured on 2026-08-07 during the 0.5/0.6 prep, and the current release is 0.6.2. sorug's parse borrows canonical ASCII input (Backing::Borrowed, copy-on-write), whereas url::Url::parse always builds an owned String, so part of the gap is an allocation the API design avoids. ada-url is measured through the ada-url 4 Rust FFI crate, not native C++ ada. The repo is young (created 2026-07-31) with 1 star, and the author has paused performance work until 1.0.

`forbid(unsafe_code)` (no unsafe in library code) unlike many fast parsers; no_std + alloc friendly; ships its own vendored Unicode/Punycode tables instead of depending on ICU/idna crate, which is a maintenance burden for Unicode updates; extremely new/unproven (single author, 1 star, published within days of this search).

## Maintenance

Maintained but young. The last release is 0.6.2 (2026-08-09), the only commits since are bot refreshes of the WPT fixtures, the author has frozen features and performance work until a 1.0 that waits on 30 days of daily and 8 weeks of weekly fuzz runs passing, and daily fuzz and CI runs pass; dual MIT/Apache-2.0 on crates.io.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks table (measured 2026-08-07) lists sorug / ada-url / servo url at 28.3/31.9/97 ns, 56.0/140/216 ns, 196/277/248 ns and 31.1/95.0/129 ns, matching the claim. The Criterion code is public (benches/url_benchmark.rs, `cargo bench --bench url_benchmark`) and Cargo.toml [profile.bench] sets opt-level=3, lto=true, codegen-units=1. There is no CPU model (only 'Linux') and no rustc version, so it is first-party C.
- **Verifier notes:** The numbers match the README exactly; the ratios are derived. The record's caveat called the repo 'days-old', but it was created 2026-07-31, about 8 weeks before today. Metadata checks out: dual MIT OR Apache-2.0 per Cargo.toml and both LICENSE files (GitHub detects Apache-2.0), last commit 2026-09-21, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/hocestnonsatis/sorug>
  - <https://github.com/hocestnonsatis/sorug#benchmarks>
  - <https://github.com/hocestnonsatis/sorug/blob/main/Cargo.toml>
  - <https://github.com/hocestnonsatis/sorug/blob/main/benches/url_benchmark.rs>
  - <https://crates.io/api/v1/crates/sorug>
- **Sources the enricher read:**
  - <https://github.com/hocestnonsatis/sorug>
  - <https://github.com/hocestnonsatis/sorug#benchmarks>
  - <https://github.com/hocestnonsatis/sorug/blob/main/Cargo.toml>
  - <https://github.com/hocestnonsatis/sorug/blob/main/benches/url_benchmark.rs>
  - <https://github.com/hocestnonsatis/sorug/blob/main/src/parser/fast.rs>
  - <https://github.com/hocestnonsatis/sorug/blob/main/src/parser/scan.rs>
  - <https://github.com/hocestnonsatis/sorug/blob/main/src/parser/mod.rs>
  - <https://github.com/hocestnonsatis/sorug/blob/main/src/parser/punycode.rs>
  - <https://github.com/hocestnonsatis/sorug/blob/main/src/lib.rs>
  - <https://github.com/hocestnonsatis/sorug/blob/main/build.rs>
  - <https://github.com/hocestnonsatis/sorug/blob/main/docs/cookbook.md>
  - <https://github.com/hocestnonsatis/sorug/blob/main/docs/differential-allowlist.md>
  - <https://github.com/hocestnonsatis/sorug/blob/main/docs/api-audit.md>
  - <https://github.com/hocestnonsatis/sorug/blob/main/docs/1.0-gate.md>
  - <https://github.com/hocestnonsatis/sorug/blob/main/CHANGELOG.md>
  - <https://github.com/hocestnonsatis/sorug/blob/main/CONTRIBUTING.md>
  - <https://github.com/hocestnonsatis/sorug/blob/main/ffi/README.md>
  - <https://github.com/hocestnonsatis/sorug/blob/main/data/ucd/README.md>
  - <https://github.com/hocestnonsatis/sorug/blob/main/.github/workflows/bench-informational.yml>
  - <https://github.com/hocestnonsatis/sorug/blob/main/.github/workflows/ci.yml>
  - <https://github.com/hocestnonsatis/sorug/commits/main>
  - <https://github.com/hocestnonsatis/sorug/issues>
  - <https://github.com/hocestnonsatis/sorug/actions>
  - <https://github.com/hocestnonsatis/sorug/actions/runs/35505545781>
  - <https://github.com/hocestnonsatis/sorug/actions/runs/34753485448>
  - <https://github.com/hocestnonsatis/sorug/actions/runs/31299845826>
  - <https://crates.io/api/v1/crates/sorug>
  - <https://crates.io/api/v1/crates/sorug/reverse_dependencies>
  - <https://static.crates.io/crates/sorug/sorug-0.6.2.crate>
  - <https://crates.io/api/v1/crates/ada-url>
  - <https://github.com/ada-url/rust>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/hocestnonsatis/sorug`) · [data/wave5/enrich/raw/github_com_hocestnonsatis_sorug.json](../../../data/wave5/enrich/raw/github_com_hocestnonsatis_sorug.json) (enrichment confidence 0.55)

</details>
