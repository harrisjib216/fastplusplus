# SynapServe

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · ⚪ unknown

> Closed-source zero-allocation Rust HTTP/1.1 parser inside the SynapServe io_uring server; claims 1.11-1.25x faster tokenization than httparse.

| | |
|---|---|
| **Beats** | httparse |
| **Claimed result** | 1.11-1.25x faster raw tokenization vs httparse 1.10 (page: 1.25x on small 35B, 42 vs 52 ns; 1.15x on medium 368B, 1.71 vs 1.49 GiB/s; 1.11x on large 733B, 1.63 vs 1.47 GiB/s); 1.38x (220 vs 304 ns) and 1.46x (413 vs 604 ns) faster when equal semantic extraction work is included; 32-37x faster header lookup (0.59-0.67 ns O(1) vs 20.5-23.1 ns O(n)) |
| **Workload** | Parsing synthetic HTTP/1.1 requests of three sizes (35B GET/1 header, 368B POST/9 headers, 733B POST/20 headers) and header-lookup latency on a pre-parsed 9-header request, using Criterion with 100 samples on a single core, vs httparse 1.10 |
| **Metric** | throughput |
| **Links** | [benchmark](https://synapserve.io/posts/http-parser-performance/) |

## Verdict

First-party Criterion runs (100 samples, single core) against httparse 1.10 on three synthetic requests, where SynapServe also extracts content_length, chunked and keep_alive: 42 vs 52 ns at 35 B, 200 vs 230 ns at 368 B and 420 vs 466 ns at 733 B (1.25x/1.15x/1.11x). With a matching extraction loop added to httparse it is 220 vs 304 ns and 413 vs 604 ns (1.38x/1.46x), and known-header lookup is about 0.6 ns vs 20.5-23.1 ns. No CPU, OS, rustc version, flags or benchmark code is given for these parser runs; the site's separate static-file server benchmark ran on an Intel i7-8550U laptop under Linux 6.17.

## Use it when

- As a design reference for your own Rust HTTP/1.1 front end: u16 span output, a parse-time known-header bitmap index, and fused CRLF plus validation scans are the ideas worth copying.
- If you get the code from the vendor and every request handler checks the same few headers (Content-Length, Transfer-Encoding, Connection, Host). The page reports 0.59-0.67 ns vs 20.5-23.1 ns per lookup and 60-112 ns saved per handler, which is more than the parse gain.
- Small-to-medium request heads (35-733 B tested, 1-20 headers) where you would otherwise parse with httparse and then loop over the headers to find framing fields.
- Evaluating SynapServe itself as a Linux (kernel 6.1+) io_uring HTTP/1.1 server or reverse proxy, since the parser ships only inside it.

## Skip it when

- You need a dependency now: there is no public repo (the GitHub org, created 2026-02-20, has 0 public repositories), no crate on crates.io under any synapserve name, and no named license. The site promises an open-source core but its footer says 'All rights reserved'.
- Request heads over 64 KB or more than 64 headers: the founder calls the 64 KB header area, which follows from the u16 spans, a hard limit, and the header table is [Header; 64]. Neither case's behavior is documented.
- You need httparse's API inside hyper, axum or actix-web: the output type is different (buffer-relative spans, not slices), and nothing can be linked anyway.
- You need reproducible numbers: the page gives no benchmark code, CPU, OS, rustc version or flags for the parser runs. The honest parse-only gain is 1.11-1.25x, and the 1.38-1.46x figure depends on an unpublished extraction loop the author bolted onto httparse.
- Security-sensitive or production parsing: the founder says it is 'not production-battle-tested', and no fuzzing, conformance testing or request-smuggling handling (e.g. Content-Length plus Transfer-Encoding conflicts) is documented.

## How it is fast

The output is compact. Fields are Span{off: u16, len: u16} (4 bytes, Copy), so a header entry is 10 bytes in a [Header; 64] stack table (640 bytes) instead of httparse's 32-byte &str/&[u8] pairs, and a reset clears 29 bytes instead of re-initializing a 2 KB header array. Scanning uses hand-written SIMD with runtime dispatch (AVX2 or SSE4.2 on x86-64, NEON on aarch64, SWAR elsewhere), memchr for delimiters, and fused passes: the CRLF search also rejects NUL and bare CR, and tchar validation of header names runs in the same loop as the colon search. Known headers are recognized by length, then first byte, then word-sized compares (u64/u32 with |0x20 case folding), and recorded in a u32 presence bitmap plus a known_index[21] array, so a lookup is one bit test and one array load instead of a case-insensitive linear scan.

## Compared with alternatives

In practice, never as a dependency. httparse (catalogued, the baseline here) is what you would actually ship, and thhp and picohttpparser-rs are public Rust parsers with code you can benchmark yourself. SynapServe is only worth reading for its parse-time header index and fused semantic extraction, which none of those siblings do.

## Integration

| | |
|---|---|
| **Form** | crate (unpublished): named synapserve-http-parser in the post and synapserve-parse in llms-full.txt; not on crates.io and no public source |
| **Dependencies** | memchr (named on the page for delimiter searches); others not documented |
| **Minimum toolchain** | not documented |
| **Platforms** | Parser: x86-64 with AVX2 or SSE4.2 chosen at runtime, aarch64 with NEON chosen at compile time, SWAR fallback elsewhere. The surrounding server is Linux-only (io_uring, kernel 6.1+), with no plans for macOS or Windows. |
| **Thread safety** | Not documented for the parser. The server is thread-per-core with per-worker connections and buffers and, per the site, no Arc, Mutex or Send bounds. |
| **Drop-in for the baseline** | no |

## Gotchas

- The comparison table misstates the baseline. It lists httparse SIMD as 'SSE4.2 (compile-time only)', but in httparse 1.10's default std build src/simd/runtime.rs picks AVX2 or SSE4.2 at runtime via is_x86_feature_detected!, and build.rs turns on NEON for aarch64 with rustc 1.59+.
- The numbers do not agree with each other. The medium request parses in 200 ns in the tokenize chart but 220 ns in the equal-work chart. The large request takes 420 ns alone but 413 ns with extraction. The 'Response writer: 46% faster' heading and the '1.38-1.40x on responses' claim come with no baseline numbers, only absolute times (3.9 / 33.5 / 41.3 ns).
- O(1) lookup covers only the 21 headers recognized during parsing, and the list is not published (the benchmark shows it includes Content-Type, Content-Length and X-Request-Id). Lookup cost for any other header is not documented.
- Zero allocations is not a difference from the baseline: httparse also never allocates (the caller provides the header array), as the page's own table says. The real differences are entry size (10 vs 32 bytes) and reset cost.

## Known shortcomings

- No code and no licence: the SynapServe GitHub org (created 2026-02-20) has 0 public repos, no crates.io crate, 'All rights reserved' footer, and the benchmark crate the founder mentioned on HN was never published. The page misdescribes the baseline: httparse 1.10 selects AVX2/SSE4.2 at runtime and enables NEON on aarch64, not 'SSE4.2 compile-time only'. Internal inconsistencies (medium request 200 vs 220 ns; large request faster with extraction than without; response-writer claims with no baseline numbers). The 1.38-1.46x relies on an unpublished extraction loop added to httparse; raw parsing alone is 1.11-1.25x. No CPU, OS, rustc or flags for the parser runs. O(1) lookup covers only 21 unpublished headers; 64 KB header cap and 64-header table; 'not production-battle-tested', no fuzzing documented; server Linux-only (io_uring, 6.1+). Only activity: one blog post (2026-02-21) and a Show HN; solo founder's pitch site, partly AI-generated per the founder. Design reference only.

## Caveats and trade-offs

No public source repository found. The github.com/SynapServe organization has 0 public repositories (checked via GraphQL and the org page), and no synapserve crate is on crates.io. The site claims an 'open core' with SynapServe Core 'Open Source, Free' under an unnamed open-source license, but the page footer says '© 2026 SynapServe. All rights reserved.' So has_code, usability and license cannot be confirmed. No CPU model, OS, compiler or build flags are stated. The page is internally inconsistent: the comparison table gives medium parse as '200 ns (incl. semantics)', but the equal-work section gives 220 ns. The baseline (httparse) is a widely used incumbent, but it is not one of the three named assignment baselines (llhttp, http-parser, picohttpparser). The site is an investor-pitch page for a commercial product.

Claims zero-allocation, io_uring-based server design; the larger 1.38-1.46x figures bundle semantic/header-indexing work that httparse intentionally leaves to the caller, so those comparisons are not strictly apples-to-apples; single-core microbenchmark only

## Maintenance

Usable only as a reference. The GitHub org has been empty since 2026-02-20, nothing is on crates.io, and the license is unknown despite the promised open-source core. The only activity is a Feb 2026 blog post and a Show HN (2 points), and the roadmap on the site still lists its Q1 2026 milestone as in progress, so maintenance status is unknown for a solo-founder startup seeking seed funding.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party blog post (2026-02-21) gives Criterion head-to-head numbers against httparse 1.10: raw tokenization 1.25x/1.15x/1.11x, parse plus extraction 1.38x/1.46x, header lookup 32-37x. There is no public benchmark code and no CPU, OS, compiler or flags, so it is C.
- **Verifier notes:** All claimed numbers appear on the page. The only correction is that the page gives 1.25x for small requests, so the raw range is 1.11-1.25x, not 1.11-1.15x. SynapServe has no public code (GitHub org empty, crates.io 404). The only GitHub search hit, h-h-v/synapserve, is an unrelated Python ITSM ML project. Kept at C with has_code=false and usability=reference; I did not reject because the baseline is recognizable and the numbers exist.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://synapserve.io/posts/http-parser-performance/>
  - <https://synapserve.io/>
  - <https://synapserve.io/llms.txt>
  - <https://github.com/SynapServe>
  - <https://github.com/h-h-v/synapserve>
  - <https://crates.io/api/v1/crates/synapserve>
  - <https://crates.io/api/v1/crates/synapserve-http-parser>
  - <https://crates.io/api/v1/crates/synapserve-http>
- **Sources the enricher read:**
  - <https://synapserve.io/posts/http-parser-performance/>
  - <https://synapserve.io/>
  - <https://synapserve.io/posts/>
  - <https://synapserve.io/llms.txt>
  - <https://synapserve.io/llms-full.txt>
  - <https://synapserve.io/SynapServe_OnePager.pdf>
  - <https://synapserve.io/SynapServe_Investor_Deck.pdf>
  - <https://news.ycombinator.com/item?id=47136572>
  - <https://hn.algolia.com/api/v1/items/47136572>
  - <https://hn.algolia.com/api/v1/search?query=synapserve>
  - <https://github.com/SynapServe>
  - <https://crates.io/api/v1/crates/synapserve-parse>
  - <https://crates.io/api/v1/crates/synapserve-parser>
  - <https://crates.io/api/v1/crates/synapserve-core>
  - <https://crates.io/api/v1/crates?q=synapserve>
  - <https://github.com/seanmonstar/httparse/blob/v1.10.0/src/simd/mod.rs>
  - <https://github.com/seanmonstar/httparse/blob/v1.10.0/src/simd/runtime.rs>
  - <https://github.com/seanmonstar/httparse/blob/v1.10.0/build.rs>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `paper:synapserve`) · [data/wave5/enrich/raw/paper_synapserve.json](../../../data/wave5/enrich/raw/paper_synapserve.json) (enrichment confidence 0.3)

</details>
