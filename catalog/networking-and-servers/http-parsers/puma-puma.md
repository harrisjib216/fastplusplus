# Puma http11_parser (Mongrel/Ragel-based HTTP/1.x parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Mongrel's Ragel-generated C request/header tokenizer, vendored in Puma; \~1.26x faster than joyent http_parser in a 2016 test.

| | |
|---|---|
| **Beats** | http-parser |
| **Claimed result** | \~1.26x faster (derived from page data): Puma http11_parser 3.215s vs http_parser 4.065s for 3M parses; 5.359s vs 6.778s for 5M parses (wall-clock `time`, three or two runs each, all within 0.003s) |
| **Workload** | Repeatedly parsing a single realistic HTTP/1.1 GET request (headers only, no body) 3,000,000 and 5,000,000 times, comparing nginx-derived joyent/http-parser (http_parser.c) against Puma's Ragel-generated http11 parser (originally Zed Shaw's Mongrel parser). |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2407 @ 2.20GHz (per /proc/cpuinfo pasted in README) |
| **Compiler and flags** | gcc -O2 per the repo Makefile (GCC version not stated; the README runs use ./a.out, not the Makefile's `-o test` output, so the flags for the recorded numbers are not certain) |
| **Adoption** | 7.9k stars (puma); benchmark repo itself has 2 stars |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/puma/puma) · [benchmark](https://github.com/jiakai1000/httpparsers) |

## Verdict

A January 2016 one-off (jiakai1000/httpparsers) on an Intel Xeon E5-2407 @ 2.20GHz parsed the same 365-byte, 9-header GET 3M and 5M times. Puma's -G2 Ragel parser (2016 copy, Ruby hooks stripped) took 3.215 s and 5.36 s; joyent http_parser 2.6.0 in its default strict mode took 4.065 s and 6.78 s. That is about 1.07 us vs 1.36 us per parse, 1.26x. Timing used wall-clock `time ./a.out` with empty callbacks and a strcpy per iteration in both loops; the Makefile says gcc -O2, but no GCC version is given and it is not certain the recorded binary was built that way.

## Use it when

- Server or proxy code that only needs the request line and headers of HTTP/1.x requests tokenized from one contiguous buffer, and handles framing (Content-Length/chunked) itself
- You want a small grammar you can audit and edit (method set, URI rules, header charset), then regenerate with Ragel; the same grammar also produces Puma's Java parser for JRuby
- CGI/Rack-style servers that want header names upper-cased with '-' turned into '_' while parsing, the form Puma's HTTP_\* env keys use
- Replacing legacy joyent/nodejs http_parser on a request-only path with small header blocks (the benchmark used a 365-byte, 9-header GET), where 2016 data showed about 1.07 us vs 1.36 us per request

## Skip it when

- You need response parsing, body/chunked decoding, or keep-alive/upgrade semantics: http_parser and its successor llhttp provide these, and this parser leaves them to the caller
- Streaming over non-contiguous reads: callbacks carry offsets into one growing buffer, so you must append every read to a single buffer and pass all of it again
- Peak throughput on modern x86: no SIMD, and the only benchmark found is from 2016 against the now-archived nodejs/http-parser; nothing read compares it with picohttpparser or llhttp
- Lenient intake of legacy clients: CRLF is required (bare LF rejected since the CVE-2021-41136 fix), obs-fold continuation lines are not in the grammar, and methods must be 1-20 chars of [A-Z0-9\$-_.]
- You want a versioned standalone library: it exists only as ext/puma_http11 inside the Ruby gem, and its header includes ruby.h

## How it is fast

Ragel compiles the regular grammar into a DFA, and Puma's Rakefile runs it with `-C -G2`, which emits goto-driven C: each state is a label with a switch on the current byte, so there are no transition tables and no function call per byte. Actions only store buffer offsets (MARK) and, at the end of each token, call a callback with a pointer and length into the caller's buffer, so nothing is copied. It also does less work than http_parser 2.6.0, which tracks Content-Length and the chunked/keep-alive/upgrade flags and ran with its default HTTP_PARSER_STRICT=1 in the benchmark. There is no SIMD; the scan is one byte at a time.

## Compared with alternatives

Pick it over the picohttpparser family (vkrasnov AVX2 fork, httpp, hparse) or llhttp-based parsers (iohttpparser, zttp) only when you want an editable Ragel grammar that generates both C and Java and does CGI-style header normalization during the parse. For raw speed use pico-style SIMD parsers, and for full HTTP/1.1 semantics and chunk-by-chunk streaming use llhttp/iohttpparser. None of these were benchmarked against Puma's parser in anything read.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | None for the generated C core once the ruby.h include and the VALUE request/body fields in http11_parser.h are removed (the benchmark repo did exactly this). Ragel is needed only to regenerate from the .rl files. Inside Puma the glue (puma_http11.c) links against the Ruby C API. |
| **Minimum toolchain** | Any C compiler; plain portable C with no intrinsics (Puma's extconf builds with -Werror plus -Wno-implicit-fallthrough for the Ragel output). Regenerating needs Ragel with `-C -G2`; CI installs the distro ragel without pinning a version, and the benchmark author used Ragel 6.8. |
| **Platforms** | any (byte-at-a-time C with no architecture-specific code; Puma's extconf also handles MinGW builds) |
| **Thread safety** | Not documented for the C core. All mutable state is in the puma_parser struct (the generated file has only static const state numbers), so one instance per connection is safe in practice. Puma's Ruby glue declares the extension Ractor-safe. |
| **Drop-in for the baseline** | false. The API is different: offset-based execute over the whole buffer, a fixed set of 8 callbacks instead of http_parser_settings, requests only, and no body, chunked, Content-Length or keep-alive handling. It fills only the header-tokenizing part of http_parser's role. |

## Gotchas

- It writes to the input even though execute takes `const char *`: the snake_upcase_field action casts away const and rewrites header-name bytes in place (a-z to A-Z, '-' to '_', '_' to ','). The buffer must be writable, and callbacks see normalized names, not the original bytes. Both benchmark loops strcpy the request into a fresh buffer on every iteration.
- The length limits (header name 256 B, value 80 KB, URI 12 KB, query 10 KB, whole header 112 KB) are enforced in Puma's Ruby glue callbacks, not in the Ragel core. A standalone copy has no limits unless your callbacks add them.
- The '_' to ',' rewrite, the header-value charset (any byte except CTLs, plus tab) and CRLF strictness came from hardening changes in 2020-2021: commit ad8197e4 'Reduce ambiguity of headers', the GHSA-48w2-rm65-62xx fix, and dc76d95b. The later CVE-2024-45614 underscore-header fix sits in the Ruby layer (allow_underscore_headers in client.rb). The 2016 benchmark copy predates all of them, and the current grammar has not been re-benchmarked.
- After the blank line the parser stops (fbreak) and stores body_start; bytes of a pipelined next request or of the body are left to the caller.

## Known shortcomings

- Only evidence is a 2016 third-party repo (about 1.26x over http-parser, gcc -O2, no version); the recorded runs used a different binary than the Makefile's test target. Ruby server component; the Ragel parser is C.
- The benchmarked copy predates several grammar changes (2020-2022), and the baseline, joyent http-parser 2.6.0, is archived; http_parser tracks Content-Length/chunked/keep-alive while Puma's parser stops at the headers. Not standalone (includes ruby.h), writes into its input buffer, and needs the whole request so far on every call. PR #3815 experiments with replacing it with pure Ruby.

## Caveats and trade-offs

The benchmark repo (jiakai1000/httpparsers, 2 stars, no license) was a one-off from 2016-01-13 and has had no commits since. It measures the 2016 Puma parser against joyent http_parser 2.6.0 (now superseded by llhttp) on one repeated 9-header GET, with wall-clock `time` and one strcpy per iteration in both loops. It gives the CPU model and a -O2 Makefile but no GCC version, and the recorded runs used ./a.out, not the Makefile binary. The results are indicative, not rigorous. The Puma parser (ext/puma_http11) is Ragel-generated C from Zed Shaw's Mongrel and ships inside the Ruby gem; it is copyable under Puma's BSD-3-Clause license.

Ragel-generated state machine (needs Ragel toolchain to regenerate from .rl source); handles only the request-line/header tokenizing role used by Puma/Mongrel/Unicorn/Thin, not full HTTP semantics (chunked/body handling done by caller); embedded as ext/puma_http11 inside the puma gem rather than shipped as a standalone library.

## Maintenance

Puma is actively maintained (last push 2026-09-16, BSD-3-Clause, 7.9k stars), but the grammar changes only for bug and security fixes (last .rl edit 2022-09), and an open experiment (issue #1889, PR #3815) looks at replacing it with pure-Ruby protocol-http1. Treat it as vendorable source rather than a library you depend on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The jiakai1000/httpparsers README (Jan 2016) has pasted `time ./a.out N nginx|puma` runs: http_parser (joyent/Node.js 2.6.0) 4.064-4.066s vs Puma http11_parser 3.215-3.217s at 3M, and 6.778-6.780s vs 5.359-5.361s at 5M, plus /proc/cpuinfo (Xeon E5-2407). The code is public (puma1.c, http11_parser1.c, http_parser.c) and the Makefile says `gcc ... -O2`, but no GCC version is given and the recorded runs used ./a.out rather than the Makefile's `-o test` binary, so the flags actually used are not certain; C, not A.
- **Verifier notes:** The numbers match the README exactly; the \~1.26x ratio is derived from them. The record's caveat 'unmaintained since May 2025' was wrong: the benchmark repo's last commit is 2016-01-13. Puma metadata checks out (BSD-3-Clause, 7,917 stars, last commit 2026-09-16, not a fork, not archived).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jiakai1000/httpparsers>
  - <https://github.com/jiakai1000/httpparsers/blob/master/README.md>
  - <https://github.com/jiakai1000/httpparsers/blob/master/Makefile>
  - <https://github.com/jiakai1000/httpparsers/blob/master/puma1.c>
  - <https://github.com/jiakai1000/httpparsers/blob/master/http_parser.h>
  - <https://github.com/jiakai1000/httpparsers/blob/master/http11_parser1.c>
  - <https://github.com/puma/puma>
  - <https://github.com/puma/puma/tree/master/ext/puma_http11>
  - <https://github.com/puma/puma/blob/master/ext/puma_http11/http11_parser.rl>
  - <https://github.com/puma/puma/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/puma/puma>
  - <https://github.com/puma/puma/blob/main/README.md>
  - <https://github.com/puma/puma/tree/main/ext/puma_http11>
  - <https://github.com/puma/puma/blob/main/ext/puma_http11/http11_parser.h>
  - <https://github.com/puma/puma/blob/main/ext/puma_http11/http11_parser.rl>
  - <https://github.com/puma/puma/blob/main/ext/puma_http11/http11_parser_common.rl>
  - <https://github.com/puma/puma/blob/main/ext/puma_http11/http11_parser.c>
  - <https://github.com/puma/puma/blob/main/ext/puma_http11/puma_http11.c>
  - <https://github.com/puma/puma/blob/main/ext/puma_http11/extconf.rb>
  - <https://github.com/puma/puma/blob/main/Rakefile>
  - <https://github.com/puma/puma/blob/main/.github/workflows/ragel.yml>
  - <https://github.com/puma/puma/blob/main/lib/puma/client.rb>
  - <https://github.com/puma/puma/security/advisories>
  - <https://github.com/puma/puma/security/advisories/GHSA-9hf4-67fc-4vf4>
  - <https://github.com/puma/puma/security/advisories/GHSA-48w2-rm65-62xx>
  - <https://github.com/puma/puma/security/advisories/GHSA-68xg-gqqm-vgj8>
  - <https://github.com/puma/puma/commits/main/ext/puma_http11/http11_parser.rl>
  - <https://github.com/puma/puma/commits/main/ext/puma_http11/http11_parser_common.rl>
  - <https://github.com/puma/puma/commits/main/ext/puma_http11/http11_parser.c>
  - <https://github.com/puma/puma/commit/ad8197e4>
  - <https://github.com/puma/puma/commit/acdc3ae5>
  - <https://github.com/puma/puma/commit/b6ef31ef>
  - <https://github.com/puma/puma/issues/1889>
  - <https://github.com/puma/puma/pull/3815>
  - <https://github.com/jiakai1000/httpparsers>
  - <https://github.com/jiakai1000/httpparsers/blob/master/README.md>
  - <https://github.com/jiakai1000/httpparsers/blob/master/Makefile>
  - <https://github.com/jiakai1000/httpparsers/blob/master/puma1.c>
  - <https://github.com/jiakai1000/httpparsers/blob/master/http11_parser.h>
  - <https://github.com/jiakai1000/httpparsers/blob/master/http11_parser1.c>
  - <https://github.com/jiakai1000/httpparsers/blob/master/http11_parser2.c>
  - <https://github.com/jiakai1000/httpparsers/blob/master/http11_parser.c>
  - <https://github.com/jiakai1000/httpparsers/blob/master/http_parser.h>
  - <https://github.com/nodejs/http-parser>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/puma/puma`) · [data/wave5/enrich/raw/github_com_puma_puma.json](../../../data/wave5/enrich/raw/github_com_puma_puma.json) (enrichment confidence 0.6)

</details>
