# nom (Rust parser combinator library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟡 stale

> Rust parser-combinator library; its own benchmarks show parity at best with handwritten C HTTP parsers, not a win.

| | |
|---|---|
| **Beats** | Handwritten C HTTP parsers Joyent http-parser and h2o picohttpparser (parser_benchmarks/http); the MP4 benchmark compares against hammer (UpstandingHackers), a C parser-combinator library rather than a handwritten parser. |
| **Claimed result** | nom README: 'just as fast' as handwritten C parsers and 'often outperform ... even handwritten C parsers' (no numbers in nom's README). parser_benchmarks http/README.md (late-2013 MacBook Pro, quad-core 2.3 GHz Core i7): idiomatic nom is slower than Joyent http-parser on every test: 889 vs 606 ns one_test, 59,918 vs 56,385 ns small_test, 333,344 vs 266,254 ns bigger_test, 1,544 vs 1,137 ns httparse_example_test (1.06-1.47x slower, derived from page data). The SIMD 'nom (optimized)' experiment against picohttpparser: 183 vs 170 ns one_test (1.08x slower), 12,253 (+/- 2,473) vs 13,260 (+/- 1,786) ns small_test (1.08x faster), 61,519 (+/- 14,660) vs 65,415 (+/- 5,058) ns bigger_test (1.06x faster), 308 (+/- 48) vs 350 (+/- 76) ns httparse_example_test (1.14x faster) (ratios derived from page data; all within the error bars). mp4/README.md (2015, nom 0.1.6): nom 240 / 195 ns per iteration vs hammer 32,424 / 26,523 ns on small.mp4 / bigbuckbunny.mp4 with optimisations (about 135x, derived from page data). |
| **Workload** | HTTP/1.x request parsing (one small request, the httparse example request, 55 requests in http-requests.txt, 275 requests in bigger.txt) against C parsers; MP4 top-level box parsing against the C combinator library hammer; JSON parsing compared only against Rust and other libraries (no C comparator). |
| **Metric** | throughput |
| **Hardware** | Late-2013 MacBook Pro, quad-core 2.3 GHz Intel Core i7 (exact CPU model not stated) |
| **Compiler and flags** | HTTP run: compiler versions not stated. Joyent http-parser built with 'gcc -Ofast -O3 -DNDEBUG' (http/joyent_http_parser/Makefile) and timed by its own C clock_gettime loop; nom-http and nom-optimized (nom ^4.0) built with release profile lto = "fat", codegen-units = 1 and timed with the Rust bencher crate; nom-optimized README gives RUSTFLAGS="-C target-feature=+sse2" (labelled SSE4.2; its take_while1_simd path emits PCMPESTRI); picohttpparser called via FFI from pico-sys 0.0.1, whose build.rs runs gcc::compile_library with crate defaults and no -msse4.2, so picohttpparser's __SSE4_2__ path is compiled out unless CFLAGS were set. MP4 run (2015): rustc 1.0.0-dev (522d09dfe 2015-02-19), nom 0.1.6, cargo bench; hammer at commit 4e8d319 built with Apple LLVM 6.0 (clang-600.0.56), scons --variant=opt, -Ofast -DNDEBUG, no -g. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README lists zero-copy slices, streaming parsing and safe memory handling as design points; it gives no mechanism for beating C. |
| **Adoption** | 10.5k stars, 849 forks; about 785 million crates.io downloads (crates.io API, 2026-10-12); latest release 8.0.0 (2025-01-26) |
| **Last commit** | 2025-08-26 |
| **Links** | [repository](https://github.com/rust-bakery/nom) · [benchmark](https://github.com/rust-bakery/parser_benchmarks/blob/master/http/README.md) |

## Verdict

nom's README claims parity with handwritten C ('just as fast') with no numbers; the linked parser_benchmarks tables (late-2013 MacBook Pro, 2.3 GHz quad-core Core i7, compiler versions not stated) show idiomatic nom 4 1.06-1.47x slower than Joyent http-parser built with gcc -Ofast -O3 on four HTTP request inputs. The nom-optimized experiment's 1.06-1.14x edge over picohttpparser is within the error bars, uses custom SSE4.2 code against a picohttpparser build without its SSE4.2 path, and the 2015 MP4 comparison against the C combinator library hammer measures different work, so no measurement shows nom beating C.

## Use it when

- Binary formats and protocols in Rust (TLV, X.509, pcap, TLS records, MP4 box headers) where memory safety and correct handling of partial input matter more than the last 10-50% of throughput.
- Porting a handwritten C parser into a Rust codebase when parity-class speed is acceptable: idiomatic nom 4 ran 1.06-1.47x slower than Joyent http-parser while building heap-allocated header vectors.
- Streaming parsers fed chunk by chunk (the streaming modules return Incomplete instead of a wrong result at buffer end).
- no_std or embedded targets: default-features = false, with alloc optional for the Vec-building combinators.
- Prototyping configuration or language parsers that need good error positions (nom-language VerboseError, nom_locate).

## Skip it when

- When the goal is beating C: in the same table idiomatic nom was 4.4-5.2x slower than picohttpparser (889 vs 170 ns one_test, 59,918 vs 13,260 ns small_test, derived from page data), and the only nom result faster than picohttpparser is the SIMD experiment discussed under gotchas.
- JSON: serde_json 1.0.32 beat the nom 5 JSON parser on every &str input in parser_benchmarks/json (canada.json 12.4 vs 27.7 ms); use a dedicated JSON library.
- Float-heavy grammars on nom 7.1+: the changelog says moving back to the standard library float parser was a performance regression and recommends recognize_float plus another converter.
- Teams that need fast upstream fixes: last commit 2025-08-26, about 50 open pull requests, and issue #1822 (possible nom 8 slowdown versus nom 7, maintainer suspects missing #[inline]) has been open since February 2025.
- Grammars written in idiomatic many0/many1 style that collect Vec values per item: every request in the HTTP benchmark allocated a Vec of headers plus a Vec per header value.

## How it is fast

Combinators are generic and marked #[inline(always)], so LLVM monomorphises a grammar into straight-line code with no runtime parser objects; outputs are zero-copy subslices, and byte or substring searches go through memchr. nom 8 adds an OutputMode with a Check mode that runs a parser without building its output or error value (used where combinators discard results), which the docs say greatly reduces generated code and memory. nom itself has no SIMD scanning: the 'nom (optimized)' HTTP experiment that edged out picohttpparser used hand-written unrolled loops and an SSE4.2 PCMPESTRI scanner defined in the benchmark repo, not in nom.

## Compared with alternatives

None of the systems-and-safety siblings is a parser toolkit; pick nom when you need a general grammar for a binary or text format in safe Rust. If the workload is JSON, the serde sibling (kostya/benchmarks json) is the tested fast path, and for raw HTTP/1.x header parsing a dedicated parser such as picohttpparser beat idiomatic nom by 4.4-5.2x in nom's own table.

## Integration

| | |
|---|---|
| **Form** | crate (nom on crates.io; nom-language companion crate) |
| **Dependencies** | memchr 2.3 (default features off; nom's std feature enables memchr/std) |
| **Minimum toolchain** | Rust 1.65 for nom 8 (edition 2021); MSRV changes only with a major release |
| **Platforms** | any Rust target; no_std with default-features = false, alloc feature for allocating combinators |
| **Thread safety** | not documented; parsers are functions or small structs over borrowed input, with no shared global state in the code read |
| **Drop-in for the baseline** | no |

## Gotchas

- The record's caveat that 'the C harness mallocs and memcpys every header' is wrong: in parser_benchmarks/http/joyent_http_parser/main.c the LOOK_BUSY define is commented out and the Makefile (gcc -Ofast -O3 -DNDEBUG) does not set it, so the http-parser callbacks only count messages. Idiomatic nom-http, by contrast, builds a Vec&lt;Header&gt; per request and a Vec&lt;&[u8]&gt; per header value inside the timed loop. The C side did less work and still won by 1.06-1.47x.
- The HTTP table mixes statistics and inputs: the C driver prints the arithmetic mean of 1,000 timed calls with no warm-up and a 'variance' loop that assigns instead of accumulating (acc2 = ... rather than +=), so the C '+/-' values reflect one sample; the Rust rows are bencher medians with a max-min range; and the Rust one_test literals use bare LF line endings (8 bytes shorter) while the C one_test uses CRLF. In the same table the httparse driver calls req.parse(buf) on the whole buffer instead of the advanced slice, so its small_test and bigger_test rows re-parse the first request.
- nom-optimized is benchmark-repo code, not nom: its take_while1_unrolled and take_while1_simd helpers use get_unchecked and read one byte past the slice end when the whole remaining input matches and its length is a multiple of 8 (or 16), or is empty; take_while1_simd loads 16 bytes from a 4- or 6-byte ranges constant; the SIMD URL scan accepts bytes 0x80-0xFF that the scalar is_url_token fallback rejects. Every token in the measured inputs ends before a line terminator, so the overreads were not triggered in the timed runs, but the code needs nightly feature gates (const_fn, stdsimd, cfg_target_feature) and nom 4 macros removed in nom 7, so it does not build today. Its picohttpparser opponent (pico-sys 0.0.1, gcc::compile_library with no -msse4.2) had its __SSE4_2__ paths compiled out.
- The MP4 '135x over hammer' row compares nom 0.1.6 (2015), which slices top-level box bodies without reading them, against a hammer grammar that turns every body byte into an h_uint8 token, uses the size field (which includes the 8-byte header) as the body length and re-parses ftyp inside an action; the checked-in nom-mp4 code is now nom 5 with jemalloc, so the table cannot be reproduced.

## Known shortcomings

- First-party tables exist (parser_benchmarks http/README.md and mp4/README.md) but show no valid win over C: plain nom is slower than Joyent http-parser on all four HTTP tests (1.06-1.47x, derived); the SIMD 'nom (optimized)' is 1.06-1.14x faster than picohttpparser on three tests and 1.08x slower on one, within error bars, and lopsided because nom uses SSE4.2 PCMPESTRI while the pico-sys 0.0.1 build lacks -msse4.2 (crippled baseline); the MP4 135x is over hammer, a C combinator library doing different work, from 2015 code (nom 0.1.6) since rewritten; last commit 2025-08-26.
- Record caveat corrected: the Joyent C harness has LOOK_BUSY commented out, so its callbacks only count messages and copy nothing, while idiomatic nom-http allocates a Vec&lt;Header&gt; per request and a Vec per header value, so C did less work and still won 1.06-1.47x. The C variance loop uses acc2 = rather than +=, so the C +- values come from one sample; the Rust one_test input uses LF line endings while C uses CRLF; the httparse driver parses buf rather than slice, so it re-parses the first request. nom-optimized's hot loops are custom benchmark-repo code, not nom; get_unchecked reads 1 byte past the slice end when the whole input matches and its length is a multiple of 8 or 16, and a 16-byte load reads a 4-byte ranges constant (not triggered in the timed runs); it needs nightly gates and nom 4 macros, so it does not build today.

## Caveats and trade-offs

The record said no numbers were openable; they are in parser_benchmarks http/README.md and mp4/README.md, and they do not support a win over C. (1) Idiomatic nom loses to Joyent http-parser on all four HTTP tests even though the C harness mallocs and memcpys every header name and value while nom returns borrowed slices; the two sides also use different timing harnesses (Rust bencher vs a C clock_gettime loop that drops the seconds field). (2) The nom-optimized edge over picohttpparser (1.06-1.14x on three tests, 1.08x slower on one_test) is inside the stated error bars and is asymmetric: nom-optimized uses SSE4.2 PCMPESTRI range scans while pico-sys 0.0.1 compiles picohttpparser without -msse4.2, disabling its own SSE4.2 path (crippled baseline by build default). (3) The MP4 135x over hammer is not a handwritten C parser and not the same work: the hammer harness parses every box body as per-byte h_uint8 tokens through h_length_value with arena allocation and treats the MP4 size field (which includes the 8-byte header) as the body length, so it appears to over-read and stop after the first box, while nom slices box bodies; the table comes from nom 0.1.6 on a pre-1.0 rustc (2015) and the checked-in nom-mp4 code is now nom 5 with jemalloc, so the numbers are not reproducible from current code. (4) The README's own wording is parity ('just as fast'). parser_benchmarks last commit 2019-12-10, 128 stars, no LICENSE shown. Kept for notability (10.5k stars, about 785 million crates.io downloads). [retier] Correction: the Joyent C harness has LOOK_BUSY commented out, so its callbacks only count messages and copy nothing, while idiomatic nom-http allocates a Vec&lt;Header&gt; per request and a Vec per header value; C did less work and still won 1.06-1.47x. The C variance loop uses acc2 = rather than +=, so the C +- values come from one sample; Rust one_test uses LF line endings while C uses CRLF; the httparse driver re-parses the first request. nom-optimized's hot loops are custom benchmark-repo code with out-of-bounds reads (not triggered in the timed runs) and no longer build.

Rust-only API; parsers are written in combinator style rather than as C state machines.

## Maintenance

Stale but massively used (about 786 million crates.io downloads, 8.0.0 released 2025-01-26, last commit 2025-08-26, about 50 open pull requests); MIT-licensed and safe to depend on for correctness-first parsing, but its speed-versus-C claim rests on 2015-2019 benchmarks that show parity or a loss.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** First-party numbers do exist (parser_benchmarks http/README.md and mp4/README.md, late-2013 MacBook Pro Core i7 2.3 GHz, exact CPU model not stated), but none is a valid win over a C baseline: idiomatic nom is slower than Joyent http-parser on all four HTTP tests, the nom-optimized edge over picohttpparser is within the error bars and pits Rust SSE4.2 PCMPESTRI code against a picohttpparser build whose SSE4.2 path the pico-sys default build compiles out (crippled-by-build-default precedent, AssemblyScript), and the 135x MP4 win over the C combinator library hammer measures different work on 2015 code (nom 0.1.6) that has since been rewritten. No valid measurement of a win stays at D.
- **Verifier notes:** Tier stays D, but the record's 'numbers not found' caveat is wrong: parser_benchmarks http/ and mp4/ READMEs carry first-party tables. Shortcomings to record: idiomatic nom 1.06-1.47x slower than Joyent http-parser (derived); nom-optimized vs picohttpparser within noise and SIMD-asymmetric (pico-sys default build drops picohttpparser's SSE4.2 path); hammer MP4 comparison measures different work on 2015 nom 0.1.6 code. Metadata checked: MIT (LICENSE file), not archived, not a fork, last commit 2025-08-26 'Fix for issue 1808 (#1811)', about 13.5 months old, so 'stale' is correct.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-110 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/README.md>
  - <https://github.com/rust-bakery/nom>
  - <https://github.com/rust-bakery/nom/commits/main>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/LICENSE>
  - <https://github.com/rust-bakery/parser_benchmarks>
  - <https://github.com/rust-bakery/parser_benchmarks/commits/master>
  - <https://github.com/rust-bakery/parser_benchmarks/tree/master/http>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/json/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/mp4/README.md>
  - <https://github.com/rust-bakery/parser_benchmarks/tree/master/http/picohttpparser>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/picohttpparser/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/picohttpparser/src/main.rs>
  - <https://github.com/rust-bakery/parser_benchmarks/tree/master/http/nom-optimized>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-optimized/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-optimized/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-optimized/src/main.rs>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-http/Cargo.toml>
  - <https://github.com/rust-bakery/parser_benchmarks/tree/master/http/joyent_http_parser>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/joyent_http_parser/Makefile>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/joyent_http_parser/main.c>
  - <https://github.com/rust-bakery/parser_benchmarks/tree/master/mp4>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/mp4/hammer/main.c>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/mp4/nom-mp4/src/main.rs>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/mp4/nom-mp4/Cargo.toml>
  - <https://crates.io/api/v1/crates/pico-sys/0.0.1/download>
  - <https://crates.io/api/v1/crates/nom>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/src/lib.rs>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/src/internal.rs>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/src/traits.rs>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/doc/choosing_a_combinator.md>
  - <https://github.com/rust-bakery/nom/tree/main/benchmarks/benches>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/benchmarks/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/benchmarks/benches/http.rs>
  - <https://raw.githubusercontent.com/rust-bakery/nom/main/benchmarks/benches/json.rs>
  - <https://github.com/rust-bakery/nom/commits/main>
  - <https://github.com/rust-bakery/nom/issues?q=is%3Aissue%20performance>
  - <https://github.com/rust-bakery/nom/issues/1822>
  - <https://github.com/rust-bakery/nom/issues/1870>
  - <https://crates.io/api/v1/crates/nom>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/json/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/mp4/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/joyent_http_parser/main.c>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/joyent_http_parser/Makefile>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-http/src/main.rs>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-http/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-optimized/README.md>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-optimized/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-optimized/src/main.rs>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/nom-optimized/src/combinators.rs>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/picohttpparser/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/picohttpparser/src/main.rs>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/http/httparse/src/main.rs>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/mp4/hammer/main.c>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/mp4/nom-mp4/src/main.rs>
  - <https://raw.githubusercontent.com/rust-bakery/parser_benchmarks/master/mp4/nom-mp4/Cargo.toml>
  - <https://crates.io/api/v1/crates/pico-sys/0.0.1/download>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/rust-bakery/nom`) · [data/wave14/enrich/raw/github_com_rust_bakery_nom.json](../../../data/wave14/enrich/raw/github_com_rust_bakery_nom.json) (enrichment confidence 0.8)

</details>
