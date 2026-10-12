# milo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `ISC` · 🟢 active

> Strict Rust HTTP/1.1 parser (crate, C++ lib, WASM) meant to replace llhttp in Node.js; \~1.07x llhttp in one test.

| | |
|---|---|
| **Beats** | llhttp |
| **Claimed result** | milo avg 30,765.1 req/s (338k requests in 11.02s) vs llhttp avg 28,808 req/s (317k requests in 11.02s): about 1.07x (derived from page data). The same deck says: "Milo matches or outperforms llhttp in native mode, but it is slower when compiled in WebAssembly." |
| **Workload** | autocannon HTTP load test against a Node.js native-addon HTTP server using milo vs the same server using llhttp for parsing ("preliminary" test, one run each) |
| **Metric** | throughput |
| **Adoption** | 76 stars |
| **Last commit** | 2026-06-25 |
| **Links** | [repository](https://github.com/ShogunPanda/milo) · [benchmark](https://raw.githubusercontent.com/ShogunPanda/talks/main/src/talks/milo/slides.yml) |

## Verdict

The only comparison is one autocannon run (11 one-second samples) against a Node.js native-addon HTTP server, shown in the author's NodeConf EU 2023 deck: milo averaged 30,765 req/s vs 28,808 req/s for llhttp (about 1.07x, with stdev about 1.4k req/s for each). The deck gives no CPU, OS, compiler, flags or harness. The repo's current C++ harness (clang -O3 -march=native -flto for llhttp v9.3.1, target-cpu=native for milo, no callbacks enabled on either) and its WASM harness (vs undici's llhttp_simd.wasm) publish no results.

## Use it when

- You want to embed a strict HTTP/1.1-only parser in Rust, C++ or JS/WASM, and rejecting obs-fold, bare LF/CR, HTTP/1.0, duplicate Content-Length, CL+TE together and GET/HEAD bodies is what you want (request-smuggling hardening).
- You build natively (not WASM) and want a span/callback parser like llhttp, written in readable Rust instead of llparse-generated C.
- You are evaluating the parser its author proposes as llhttp's successor in Node.js and can run the repo's benchmarks/cpp or benchmarks/wasm harness on your own hardware first.

## Skip it when

- Node.js/undici-style WASM deployments where speed is the reason to switch: the author's own 2023 deck says milo is slower than llhttp when compiled to WebAssembly, and no newer WASM numbers are published.
- Servers that must accept HTTP/1.0 clients, RTSP, obs-fold or bare-LF peers. Milo rejects all of these by design and does not aim for llhttp behavioural compatibility.
- Untrusted production traffic without your own fuzzing. Two fuzzing reports from 2026-06-08 are still open: #15, a memory leak on invalid input, and #16, OOM on malformed headers. The 0.x API also changed in five releases in June 2026.
- Servers holding many idle connections: each parser allocates a 64 KiB event buffer, whereas the README describes the parser state as only a few dozen fields.
- You only need an llhttp speedup you can verify: the single published comparison is a 7% gain within noise, from a 2023 build that predates the 2026 SIMD rewrite.

## How it is fast

It is a line-oriented state machine. Proc-macros (syn/quote) generate its states, matchers and byte lookup tables (token, request-target, quoted-string) at compile time. CR and separators are found with memchr/memchr2. Header lines are scanned 16 bytes at a time for CR and invalid control bytes, using SSE2 on x86-64, NEON on aarch64 and simd128 on wasm32, with a scalar fallback. The parser reports offsets into the caller's buffer instead of copying data; the one copy is an optional re-buffering of unconsumed input (manage_unconsumed). Since 0.8.0 events go to a 64 KiB per-parser buffer and callbacks are replayed from it at the end of parse().

## Compared with alternatives

Pick milo over iohttpparser when you need Rust, C++ and WASM builds from one strict codebase aimed at Node.js; iohttpparser has much stronger published evidence against llhttp (median req/s over 22 scenarios). zttp and gunicorn_h1c are only relevant if you are in Python.

## Integration

| | |
|---|---|
| **Form** | crate (milo-parser) \| static lib + header (libmilo.a, milo.h) \| npm WASM module |
| **Dependencies** | memchr (runtime). Building the C++/WASM artifacts also needs cargo-make, cbindgen, the wasm32-unknown-unknown target and Binaryen wasm-opt. |
| **Minimum toolchain** | The repo pins nightly Rust (rust-toolchain.toml; the C++/WASM tasks use -Z flags; PR #17 to build on stable is open). The crate is edition 2024 with no declared rust-version. C++ consumers compile with -std=c++11. The npm package needs Node &gt;= 22.21.0. |
| **Platforms** | any Rust target; hand-written SIMD paths for x86-64 (SSE2), aarch64 (NEON) and wasm32 (simd128), scalar fallback elsewhere |
| **Thread safety** | Not documented. A Parser is a mutable #[repr(C)] struct holding raw pointers (context, events, unconsumed), so use one parser per connection and do not share it across threads. |
| **Drop-in for the baseline** | partial: same callback-and-span model as llhttp, but different API names, error codes and flags, stricter acceptance rules, the caller must set skip_body for responses to HEAD, and there is no llhttp compatibility shim |

## Gotchas

- An incomplete line is left unconsumed: parse() returns fewer bytes than it was given. With manage_unconsumed on, milo copies the leftover bytes and prepends them on the next call. Reading parse.rs, the retained buffer is created with Vec::into_raw_parts and only rebuilt as a slice with from_raw_parts afterwards, which does not free it, so this mode appears to leak on every partial parse.
- When the 64 KiB event buffer fills, parse() stops early without an error or pause; the caller must drain events and call parse() again.
- Responses to HEAD require the caller to set skip_body; milo does not pair requests with responses. CONNECT responses likewise need application context.
- WASM release builds use immediate-abort panics, so a panic traps with no message; the debug build is needed to diagnose errors.

## Known shortcomings

- Only evidence is one 11-sample autocannon run in the 2023 NodeConf EU deck (30,765 vs 28,808 req/s, \~1.07x), within noise (stdev \~1.4k each), with no CPU, OS, compiler or harness, and predating the 2026 SIMD rewrite. The same deck says milo is slower than llhttp as WebAssembly, the build Node/undici use. The repo's C++ and WASM harnesses publish no results and enable no callbacks. Open fuzzing reports: memory leak on invalid input (#15), OOM on malformed headers (#16); code reading suggests manage_unconsumed leaks leftover input on every partial parse. Each parser allocates a 64 KiB event buffer (contradicting 'very small footprint'), and parse() stops early without error when it fills. Pinned nightly Rust (stable PR #17 open). Stricter than llhttp (rejects HTTP/1.0, RTSP, obs-fold, bare LF/CR, GET/HEAD bodies), so only a partial drop-in. 219 crates.io downloads; README says 0.4.0 (current 0.8.0) and dependency-free (depends on memchr).

## Caveats and trade-offs

The numbers come from Paolo Insogna's NodeConf EU 2023 talk deck (Nov 2023; linked from the README as [slides] https://talks.paoloinsogna.dev/milo), not from the repo. The deck pastes autocannon text from a slide labelled "Performance in Node (native, preliminary)": one run of 11 samples, with no CPU model, compiler or flags, and no public harness for this Node native-addon test. The speedup of about 1.07x is small and sits within about 1.4 stdev of the llhttp run. The numbers predate nearly 3 years of parser changes. The same deck admits milo is slower than llhttp when compiled to WebAssembly, and WASM is the build that undici and Node use. The repo does have comparative harnesses: benchmarks/cpp (milo with RUSTFLAGS=-C target-cpu=native vs llhttp release/v9.3.1 built with clang -O3 -DNDEBUG -march=native -flto) and benchmarks/wasm (vs undici llhttp_simd.wasm). It publishes no results from them, and its benchmarks README calls them "comparative smoke tests, not absolute performance claims".

Rust state-machine parser generated via proc-macros, compiles to native or WASM; explicitly stricter than llhttp (rejects HTTP/0.9, HTTP/1.0, RTSP, obs-fold, bare LF/CR, bodies on GET/HEAD); author states it is slower than llhttp when compiled to WebAssembly; project goal is to replace llhttp as Node.js's HTTP parser

## Maintenance

Actively developed and ISC-licensed; v0.8.0 shipped 2026-06-25. Adoption is small (219 crates.io downloads in total, about 8k npm downloads in the last month) and GitHub issue search found no milo issues in nodejs/undici or the nodejs org. Treat it as pre-1.0 and experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Slide 'Performance in Node (native, preliminary)' in the NodeConf EU 2023 deck shows autocannon output for llhttp (avg 28,808 req/s, 317k req in 11.02s) and milo (avg 30,765.1 req/s, 338k req in 11.02s). These are first-party numbers from a single run with no CPU, compiler, flags or harness code given. The repo's benchmarks/cpp and benchmarks/wasm harnesses against llhttp state flags but publish no numbers or CPU model, so the entry stays at C.
- **Verifier notes:** I opened the slides.yml URL (raw and via gh) and the rendered deck at talks.paoloinsogna.dev/milo; both carry the exact numbers. The metadata matches gh: ISC, not a fork, not archived, 76 stars, last commit 2026-06-25, so active. If enrichment runs, it could note the benchmarks/cpp harness as the path to a reproducible (tier A) number, but no one has published results from it.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ShogunPanda/talks/main/src/talks/milo/slides.yml>
  - <https://github.com/ShogunPanda/talks/blob/main/src/talks/milo/info.yml>
  - <https://talks.paoloinsogna.dev/milo>
  - <https://github.com/ShogunPanda/milo>
  - <https://github.com/ShogunPanda/milo/blob/main/README.md>
  - <https://github.com/ShogunPanda/milo/blob/main/benchmarks/README.md>
- **Sources the enricher read:**
  - <https://github.com/ShogunPanda/milo>
  - <https://github.com/ShogunPanda/milo/blob/main/README.md>
  - <https://github.com/ShogunPanda/milo/blob/main/benchmarks/README.md>
  - <https://github.com/ShogunPanda/milo/blob/main/benchmarks/cpp/Makefile.toml>
  - <https://github.com/ShogunPanda/milo/blob/main/benchmarks/cpp/src/main.cc>
  - <https://github.com/ShogunPanda/milo/blob/main/benchmarks/wasm/Makefile.toml>
  - <https://github.com/ShogunPanda/milo/blob/main/rust-toolchain.toml>
  - <https://github.com/ShogunPanda/milo/blob/main/parser/Cargo.toml>
  - <https://github.com/ShogunPanda/milo/blob/main/parser/Makefile.toml>
  - <https://github.com/ShogunPanda/milo/blob/main/macros/Cargo.toml>
  - <https://github.com/ShogunPanda/milo/blob/main/docs/design.md>
  - <https://github.com/ShogunPanda/milo/blob/main/macros/README.md>
  - <https://github.com/ShogunPanda/milo/blob/main/parser/README.md>
  - <https://github.com/ShogunPanda/milo/blob/main/parser/src/parse.rs>
  - <https://github.com/ShogunPanda/milo/blob/main/parser/src/matchers.rs>
  - <https://github.com/ShogunPanda/milo/blob/main/parser/src/lib.rs>
  - <https://github.com/ShogunPanda/milo/blob/main/docs/rust.md>
  - <https://github.com/ShogunPanda/milo/blob/main/docs/cpp.md>
  - <https://github.com/ShogunPanda/milo/blob/main/docs/js.md>
  - <https://github.com/ShogunPanda/milo/blob/main/CHANGELOG.md>
  - <https://github.com/ShogunPanda/milo/issues>
  - <https://github.com/ShogunPanda/milo/issues/16>
  - <https://github.com/ShogunPanda/milo/issues/15>
  - <https://github.com/ShogunPanda/milo/issues/11>
  - <https://github.com/ShogunPanda/milo/issues/9>
  - <https://github.com/ShogunPanda/milo/pulls>
  - <https://github.com/ShogunPanda/milo/pull/17>
  - <https://github.com/ShogunPanda/milo/releases>
  - <https://raw.githubusercontent.com/ShogunPanda/talks/main/src/talks/milo/slides.yml>
  - <https://crates.io/api/v1/crates/milo-parser>
  - <https://api.npmjs.org/downloads/point/last-month/@perseveranza-pets/milo>
  - <https://registry.npmjs.org/@perseveranza-pets/milo/latest>
  - <https://hn.algolia.com/api/v1/search?query=milo%20http%20parser&tags=story>
  - <https://github.com/search?q=repo%3Anodejs%2Fundici+milo&type=issues>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/shogunpanda/milo`) · [data/wave5/enrich/raw/github_com_shogunpanda_milo.json](../../../data/wave5/enrich/raw/github_com_shogunpanda_milo.json) (enrichment confidence 0.35)

</details>
