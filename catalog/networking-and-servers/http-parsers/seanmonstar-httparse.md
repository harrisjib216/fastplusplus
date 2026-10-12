# httparse (Rust push parser for HTTP/1.x)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust's standard zero-copy HTTP/1.x push parser; beats picohttpparser only when pico is built without SSE4.2.

| | |
|---|---|
| **Beats** | picohttpparser |
| **Claimed result** | PR #40 (maintainer, rustc 1.27; pico built via pico-sys without SSE4.2): with -C target_cpu=native, httparse 405 ns vs pico 492 ns on the full browser request, \~1.21x (derived from page data), and 62 vs 72 ns on the short request, \~1.16x (derived). With runtime SIMD detection: 451 vs 492 ns, \~1.09x (derived), and 70 vs 72 ns. With SIMD off, httparse is slower on the full request (529 vs 492 ns) and faster only on the short one (66 vs 72 ns). The maintainer's summary: 'Without SIMD, httparse is oh-so-slightly faster than Pico when the requests are tiny, but a bit slower on a more realist request from a browser.' The record's 'faster than picohttpparser, when SIMD is not available' (lib.rs doc v1.2.3-v1.2.5, removed in v1.3.0) never came with numbers, and PR #40 contradicts it for realistic requests. |
| **Workload** | Rust nightly #[bench] with [profile.bench] lto=true (benches/parse.rs at v1.3.0). It parses one fixed \~700-byte, 10-header browser GET request (the 'hello-kitty-darth-vader' request) and one 3-line short request. picohttpparser is called over FFI through the pico-sys 0.0.1 crate. |
| **Metric** | throughput |
| **Compiler and flags** | rustc 1.27 (nightly bench harness), [profile.bench] lto=true; runs with SIMD off, with runtime SSE4.2/AVX2 detection, and with -C target_cpu=native. pico-sys compiles picohttpparser.c through the gcc crate with no -msse4.2, so pico runs its non-SSE4.2 path. |
| **Adoption** | 714 GitHub stars; \~742M crates.io downloads (\~169M recent); the de facto HTTP/1.x parser for Rust (hyper, actix-web and most of the Rust HTTP ecosystem) |
| **Last commit** | 2026-06-30 |
| **Links** | [repository](https://github.com/seanmonstar/httparse) · [benchmark](https://github.com/seanmonstar/httparse/pull/40) |

## Verdict

In the maintainer's PR #40 (June 2018; rustc 1.27 nightly #[bench], lto=true, an unnamed CPU with SSE4.2), a \~700 B, 10-header browser GET took 451 ns with runtime detection and 405 ns with target-cpu=native, vs 492 ns for picohttpparser built via pico-sys without SSE4.2 (\~1.09x / \~1.21x); the short request was 70 and 62 ns vs 72 ns. With SIMD off httparse lost (529 vs 492 ns), and a third party's equal-flags build (issue #85) had pico \~1.66x faster.

## Use it when

- You are writing or tuning a Rust HTTP/1.x server, client or proxy and need the head parsed straight out of a read buffer with zero allocations. It is the parser underneath hyper, and its crate has \~742M downloads and 551 reverse dependencies.
- You ship one generic x86-64 binary: runtime dispatch picks AVX2/SSE4.2 on its own. In PR #40 that took the \~700 B browser request from 529 ns (no SIMD) to 451 ns, against 492 ns for a default-built pico.
- You can build per host with -C target-cpu=native: the dispatch moves to compile time. That gave 405 ns on the same request, and 62 vs 72 ns on the short one.
- no_std or embedded targets: turn off the default 'std' feature. You get the SWAR fallback, which PR #123 measured at \~20% less time per request on x86_64 and \~40% less on Apple M1 than the old byte loop.
- Parsing messy real-world responses: ParserConfig can skip invalid header lines, accept obsolete line folding, and accept multiple spaces in the request/status line.

## Skip it when

- Raw speed against picohttpparser under equal build flags. The one fair-build report (issue #85: pico built with -msse4 and cross-language LTO) measured pico at \~2900 MB/s vs httparse at 1751 MB/s, and the project removed pico from its benches in 2022 (PR #112), so there has been no head-to-head since.
- Scalar-only builds on realistic requests: with both parsers' SIMD off, pico won 492 vs 529 ns (PR #40) and 405 vs 468 ns (PR #38). Those numbers predate the 2023 SWAR rewrite and were never re-run against pico.
- Ring buffers or scattered iovecs: parse takes a single contiguous slice (issue #74 is open), so wrapped data has to be copied first.
- Slow-drip or very large header blocks: every Partial re-parses from byte 0, and there is no last_len-style resume point. The docs (added 2026-02) warn that retry loops on a growing buffer can burn CPU fast, so cap head size and time yourself.
- You need HTTP semantics rather than tokenizing: it does not validate Content-Length or Transfer-Encoding, frame bodies or look up headers. For chunked bodies it only parses the size line and has no phr_decode_chunked equivalent. The URI check is a loose byte-range test (0x21-0x7E, 0x80-0xFF) followed by UTF-8 validation.

## How it is fast

It validates request-target and header-value bytes with SIMD range checks (16 bytes per step in the 'sse42' path, which really uses max_epu8/cmpeq/movemask; 32 with AVX2; 16 with NEON) and finds the first delimiter with trailing_ones on the movemask, falling back to SWAR word-at-a-time checks (8 bytes in a usize using borrow tricks). On x86 with std it picks AVX2, SSE4.2 or SWAR at runtime and caches the choice in an AtomicU8, while -C target-cpu=native moves the choice to compile time and removes the dispatch branch. Smaller tricks: 'GET '/'POST' are matched as 4-byte arrays, 'HTTP/1.x' as one u64 compare, and a raw-pointer Bytes cursor skips per-byte bounds checks. It won PR #40 because picohttpparser only uses its PCMPESTRI path when compiled with __SSE4_2__ and has no runtime dispatch, and pico-sys built it without that flag.

## Compared with alternatives

Pick httparse when you are in Rust and want the maintained, fuzzed, ecosystem-default parser with runtime SIMD dispatch and no_std support; thhp only ties pico (4421 vs 4393 MB/s with +sse4.2), and picohttpparser-rs is a C-ABI safety rewrite that wins only on header-heavy inputs. If you need a margin over picohttpparser itself, the non-Rust siblings httpp (\~2.26x), http.c3l (\~13%) and hparse (\~12.5% wall-clock) report larger ones but are far less deployed.

## Integration

| | |
|---|---|
| **Form** | crate (crates.io 'httparse', pure Rust) |
| **Dependencies** | none (criterion and rand are dev-dependencies only) |
| **Minimum toolchain** | Released v1.10.1: Rust 1.47 per CI, edition 2018, with a build.rs that probes rustc (NEON needs 1.59, otherwise SWAR). Unreleased master: rust-version 1.59, edition 2021, no build script. |
| **Platforms** | Any Rust target. SIMD on x86/x86_64 (SSE4.2 or AVX2, detected at runtime with std or selected at compile time via target_feature) and on aarch64 with NEON; everything else uses SWAR. CI covers x86_64 in each SIMD mode, i686-musl, aarch64 and miri. The --cfg httparse_disable_simd flag forces SWAR. |
| **Thread safety** | Not documented. Parsing only reads the caller's buffer and writes caller-owned structs. The only global is a relaxed AtomicU8 that caches CPU-feature detection, so separate Request/Response values can be parsed concurrently. |
| **Drop-in for the baseline** | false: it is a Rust API, not the phr_\* C ABI. The model is the same (stateless, zero-copy, caller-sized header array, re-parse on partial), but there is no last_len hint and no in-place chunked decoder. |

## Gotchas

- The header slice caps the header count. One header too many returns Error::TooManyHeaders rather than Partial. On Partial, Request fields can be half-filled (method set, path None), which is by design so callers can route early.
- Types are asymmetric. path is &str, so a non-UTF-8 request-target fails as Error::Token. Header values are &[u8] with trailing whitespace trimmed. A reason phrase containing obs-text comes back as "". A bare LF is accepted as a line ending.
- Open issue #222 (2026-07): with allow_space_before_first_header_name(true), a whitespace-only first header line ends the head with zero headers and leaves the real headers in the buffer, a request-smuggling hazard. The option is off by default.
- Pin a recent version. 1.9.5 fixed an unsound pointer::add (PR #185) and a runtime-dispatch lowering problem that had made generic x64 builds 2-10x slower on small header microbenchmarks (PR #181). 1.10.0 tightened method tokens to RFC tchar (PR #190). Before master's PR #214, no_std builds always used SWAR even with target features set. Despite the lib.rs doc, unsafe is not confined to one submodule: it appears throughout lib.rs, iter.rs and simd/, every block carries a clippy-enforced SAFETY comment, and CI runs miri and cargo-fuzz.

## Known shortcomings

- Not faster when both sides are built fairly: the maintainer's 2018 win was against picohttpparser built without SSE4.2; with SIMD off httparse is slower on the realistic request, and a third-party run with pico built with SSE4 and LTO had pico about 1.66x faster (#85, open). The pico comparison was removed from the benches in 2022.
- The win over picohttpparser holds only when pico is built without SSE4.2 (pico-sys uses default cc flags). With SIMD off on both, pico wins the full request (PR #40, #38); the one equal-flags build had pico \~1.66x faster (#85, open). No CPU named, numbers from 2018, pico dropped from the benches in 2022 (PR #112). Open issue #222: allow_space_before_first_header_name(true) lets a whitespace-only first header line end the head with zero headers (smuggling hazard; option off by default). Master (MSRV 1.59, compile-time SIMD for no_std) is unreleased; last release v1.10.1 (2025-03). Versions before 1.9.5 had an unsound pointer::add. The 'sse42' path uses no SSE4.2-specific instructions.

## Caveats and trade-offs

The only measured wins over picohttpparser pit httparse's SIMD paths against pico built without SSE4.2 (pico-sys uses default cc flags). Issue #85 (2021, still open) says this is not apples to apples, and the maintainer replied 'good point'. With pico built with -msse4 plus cross-language LTO, a third-party user reported pico at \~2900 MB/s vs httparse at 1751 MB/s (text in issue #85, full tables only as images). With both parsers' SIMD off, the maintainer's own PR #40 shows httparse slower on the realistic request (529 vs 492 ns) and ahead only on a tiny request (66 vs 72 ns). The 2018 contributor PR #38 shows it slower on both without SIMD (468 vs 405 ns, 54 vs 53 ns). No CPU model is given anywhere, and the numbers date from 2018. PR #112 (2022) removed the pico targets from benches, so current code no longer compares against picohttpparser. The out-of-the-box edge is real but fragile: httparse's runtime SIMD detection beats a generically built pico by \~1.09x on the full request.

no_std-friendly, allocation-free, push-style API (caller supplies header-slot buffer); safety-critical `unsafe` is scoped to a single submodule; the historical picohttpparser claim is explicitly qualified to only the no-SIMD case, which is increasingly rare since SIMD paths are now auto-detected at runtime.

## Maintenance

Actively maintained (last commit 2026-06-30, last release v1.10.1 on 2025-03-03, so master's MSRV bump and no_std SIMD are unreleased), MIT OR Apache-2.0, dependency-free and effectively the Rust HTTP/1.x default, so it is safe to adopt; its speed edge over pico is the weak part, not its maturity.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D. The record had no numbers page, but the maintainer's merged PR #40 (2018-06-22) has `cargo bench` results for httparse vs picohttpparser. The bench code is public (benches/parse.rs at v1.3.0, pico via the pico-sys crate) and the rustc version (1.27) and RUSTFLAGS are stated, but no CPU model is given (only 'my CPU has SSE4.2'). That is first-party C, not A.
- **Verifier notes:** The record's claim sentence is real (lib.rs doc in 1.2.3-1.2.5; v1.0-1.2.0 said '1.6 times slower than pico'), but the project's own later numbers contradict it for realistic requests. I kept the entry at C on PR #40, whose SIMD httparse beats non-SSE4.2 pico by 1.09-1.21x, and flagged the unfair-baseline issue (#85). If the orchestrator wants fair-baseline evidence only, this is a reject candidate ('not-faster'), because the only fair-build report has pico \~1.66x faster. Metadata checks out: MIT OR Apache-2.0, last commit 2026-06-30, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/seanmonstar/httparse>
  - <https://github.com/seanmonstar/httparse/blob/master/README.md>
  - <https://github.com/seanmonstar/httparse/blob/v1.0.0/src/lib.rs>
  - <https://github.com/seanmonstar/httparse/blob/v1.2.3/src/lib.rs>
  - <https://github.com/seanmonstar/httparse/blob/v1.3.0/src/lib.rs>
  - <https://github.com/seanmonstar/httparse/blob/v1.3.0/benches/parse.rs>
  - <https://github.com/seanmonstar/httparse/blob/v1.3.0/Cargo.toml>
  - <https://github.com/seanmonstar/httparse/commit/5deba4eb50>
  - <https://github.com/seanmonstar/httparse/pull/40>
  - <https://github.com/seanmonstar/httparse/pull/38>
  - <https://github.com/seanmonstar/httparse/issues/85>
  - <https://github.com/seanmonstar/httparse/pull/112>
  - <https://github.com/reem/rust-pico-sys/blob/master/build.rs>
  - <https://crates.io/api/v1/crates/httparse>
  - <https://crates.io/api/v1/crates/pico-sys>
- **Sources the enricher read:**
  - <https://github.com/seanmonstar/httparse>
  - <https://github.com/seanmonstar/httparse/blob/master/README.md>
  - <https://github.com/seanmonstar/httparse/blob/master/Cargo.toml>
  - <https://github.com/seanmonstar/httparse/blob/master/src/lib.rs>
  - <https://github.com/seanmonstar/httparse/blob/master/src/iter.rs>
  - <https://github.com/seanmonstar/httparse/blob/master/src/simd/mod.rs>
  - <https://github.com/seanmonstar/httparse/blob/master/src/simd/runtime.rs>
  - <https://github.com/seanmonstar/httparse/blob/master/src/simd/sse42.rs>
  - <https://github.com/seanmonstar/httparse/blob/master/src/simd/avx2.rs>
  - <https://github.com/seanmonstar/httparse/blob/master/src/simd/neon.rs>
  - <https://github.com/seanmonstar/httparse/blob/master/src/simd/swar.rs>
  - <https://github.com/seanmonstar/httparse/blob/master/benches/parse.rs>
  - <https://github.com/seanmonstar/httparse/blob/master/.github/workflows/ci.yml>
  - <https://github.com/seanmonstar/httparse/blob/v1.10.1/Cargo.toml>
  - <https://github.com/seanmonstar/httparse/blob/v1.10.1/build.rs>
  - <https://github.com/seanmonstar/httparse/blob/v1.10.1/.github/workflows/ci.yml>
  - <https://github.com/seanmonstar/httparse/pull/40>
  - <https://github.com/seanmonstar/httparse/pull/38>
  - <https://github.com/seanmonstar/httparse/pull/112>
  - <https://github.com/seanmonstar/httparse/pull/123>
  - <https://github.com/seanmonstar/httparse/pull/133>
  - <https://github.com/seanmonstar/httparse/pull/181>
  - <https://github.com/seanmonstar/httparse/pull/190>
  - <https://github.com/seanmonstar/httparse/pull/213>
  - <https://github.com/seanmonstar/httparse/pull/214>
  - <https://github.com/seanmonstar/httparse/issues/85>
  - <https://github.com/seanmonstar/httparse/issues/222>
  - <https://github.com/seanmonstar/httparse/issues/196>
  - <https://github.com/seanmonstar/httparse/issues/161>
  - <https://github.com/seanmonstar/httparse/issues/74>
  - <https://github.com/seanmonstar/httparse/issues/83>
  - <https://github.com/seanmonstar/httparse/issues?q=is%3Aopen>
  - <https://github.com/seanmonstar/httparse/releases>
  - <https://github.com/seanmonstar/httparse/commits/master>
  - <https://github.com/seanmonstar/httparse/security/advisories>
  - <https://github.com/rustsec/advisory-db/tree/main/crates/httparse>
  - <https://github.com/h2o/picohttpparser/blob/master/picohttpparser.h>
  - <https://github.com/h2o/picohttpparser/blob/master/picohttpparser.c>
  - <https://github.com/reem/rust-pico-sys/blob/master/build.rs>
  - <https://crates.io/api/v1/crates/httparse>
  - <https://crates.io/api/v1/crates/httparse/1.10.1>
  - <https://crates.io/api/v1/crates/httparse/reverse_dependencies>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/seanmonstar/httparse`) · [data/wave5/enrich/raw/github_com_seanmonstar_httparse.json](../../../data/wave5/enrich/raw/github_com_seanmonstar_httparse.json) (enrichment confidence 0.45)

</details>
