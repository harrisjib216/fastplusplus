# fast-http

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Common Lisp` · `MIT` · 🟢 active

> Pure Common Lisp HTTP/1.x request/response parser; on SBCL its README shows it 1.25x faster than joyent's C http-parser.

| | |
|---|---|
| **Beats** | http-parser (joyent/http-parser) |
| **Claimed result** | fast-http is 1.25x faster than http-parser: 0.086s vs 0.108s to parse the same header 100,000 times |
| **Workload** | Parsing the same 430-byte HTTP GET request header (request line plus 9 headers) 100,000 times: fast-http run-ll-benchmark (parse-request with empty callbacks, timed by SBCL `time`) vs a C loop of http_parser_init + http_parser_execute with null callbacks (timed by clock()) |
| **Metric** | latency |
| **Compiler and flags** | fast-http: SBCL 1.2.6 (no extra Lisp optimize settings stated in README). http-parser (C): bench driver built with 'gcc -Wall -Wextra -Werror -Wno-error=unused-but-set-variable -O3'; http_parser.o built with http-parser's own 'make http_parser.o' (Makefile flags not shown); gcc version unstated |
| **Adoption** | 362 stars |
| **Last commit** | 2026-04-06 |
| **Links** | [repository](https://github.com/fukamachi/fast-http) · [benchmark](https://github.com/fukamachi/fast-http/blob/master/README.markdown) |

## Verdict

The README times 100,000 parses of one 430-byte GET request (9 headers) with no callbacks: fast-http's low-level parse-request on SBCL 1.2.6 took 0.086 s (SBCL `time` real time) and joyent/http-parser took 0.108 s (timed with clock(); bench driver built with gcc -O3, http_parser.o via http-parser's own Makefile, which currently uses -O3 -DHTTP_PARSER_STRICT=0). That is 1.25x, run on Travis CI with no CPU model or gcc version given and never re-run since the 2014-era README; a 2014 third-party test (issue #8, macOS x86-64) found fast-http 2.5x faster than stock http-parser but 10% slower than a direct-threaded C variant (0.117 s vs 0.105 s), with a larger footprint (112-byte parser struct vs 32 stock / 48 tuned, and over 41 KB for the parse function alone vs about 13-15 KB for the whole C parser).

## Use it when

- You are writing a Common Lisp HTTP/1.x server, client or proxy on SBCL and want a callback parser that does not allocate during header parsing.
- You serve keep-alive or pipelined request streams (pipelining merged in 2023, PR #40) or need chunked-body decoding in Lisp.
- You need streaming multipart/form-data parsing in Lisp via make-multipart-parser.
- You already use the Woo server or the Dexador client, which use it (HN 2014 thread; issue #46), and want to call the parser directly.
- Internet-facing use only on v0.3.0 (2026-04-06) or later, which adds request-smuggling and DoS hardening.

## Skip it when

- Any non-Lisp codebase. From C/C++ use llhttp or picohttpparser. The 1.25x claim is against http-parser, whose README now says it is not actively maintained (see issue #38), and the benchmark has never been re-run against llhttp.
- A plain (ql:quickload :fast-http) from the Quicklisp 2026-01-01 dist installs fast-http-20241012-git. That snapshot predates v0.3.0's fixes for TE-TE and CL+TE request smuggling, conflicting duplicate Content-Length, chunk-size and Content-Length bignum DoS, and an out-of-bounds unhex-byte read. Pin git master or an ocicl snapshot of v0.3.0 or later.
- HTTP clients that must read close-delimited responses (a body with no Content-Length and no Transfer-Encoding). Open issue #46 (Aug 2026) shows these fail with a misleading invalid-version error, for example through dex:get.
- Large uploads through make-multipart-parser, which buffers each part body. Open issue #44 shows a 1 GiB upload failing with 'Buffer exceeded the limit: 1073741824'.
- Methods outside its hard-coded list of 27, such as QUERY (open issue #45), or HTTP/2 and HTTP/3: it is HTTP/1.x only.

## How it is fast

It is a hand-written byte-at-a-time state machine built from the proc-parse macros (with-octets-parsing, match-case). At compile time these expand into tagbody/go code, and fixed strings such as method names and the content-length, transfer-encoding and upgrade header names become a character trie of nested case dispatches instead of string compares. Hot functions are declared (optimize (speed 3) (safety 0)) with simple-byte-vector and fixnum type declarations, and helpers are inlined, so SBCL emits native code with no type checks; 128-entry lookup tables classify token and hex bytes. Callbacks receive offsets into the caller's buffer, so the low-level path allocates nothing (0 bytes consed over 100,000 parses in the README run).

## Compared with alternatives

It is the only Common Lisp parser in this category, so pick it when your stack is Lisp (Woo, Clack, Dexador). For C/C++ the siblings are the real options: Puma's Ragel-based http11_parser shows a similar \~1.26x over the same deprecated http-parser, and milo or iohttpparser (vs llhttp) and httparse or thhp (vs picohttpparser) are measured against current baselines.

## Integration

| | |
|---|---|
| **Form** | module (ASDF system, installed with Quicklisp or ocicl) |
| **Dependencies** | alexandria, cl-utilities, proc-parse, babel, xsubseq, smart-buffer (plus log4cl only with the fast-http-debug feature); tests use prove and cl-syntax-interpol |
| **Minimum toolchain** | Not documented. It needs an ANSI Common Lisp with ASDF. The benchmark used SBCL 1.2.6. The CI config (.travis.yml) lists SBCL, CCL, CLISP, ABCL and ECL, with an ECL load workaround in the .asd, and a LispWorks fix was merged in PR #33. |
| **Platforms** | Any OS/arch its Lisp implementation supports; the speed claim applies only to SBCL native code |
| **Thread safety** | Not documented. Each http struct and make-parser closure holds mutable parse state (state, mark, header-read, a buffered tail), so use one per connection and do not share it across threads. |
| **Drop-in for the baseline** | partial — the low-level callbacks struct mirrors http_parser_settings and uses (data start end) offsets, but it is a Lisp-only API that C/C++ cannot call. It is also not resumable at any byte the way http-parser is: on partial input it signals eof, and make-parser buffers and re-parses the tail. |

## Gotchas

- Hot paths are compiled with (safety 0), so the low-level API does not check argument types. Pass only simple (unsigned-byte 8) vectors and valid start/end. Before v0.3.0, unhex-byte read out of bounds on high bytes (commit 4d8cf4f), and a 2017 memory-fault report under Woo (issue #30) is still open.
- Streaming is replay-based: when a chunk ends mid-token, parse-request signals eof, and make-parser copies the unconsumed tail from http-mark and re-scans it together with the next chunk. Code comments call this O(N^2), bounded only by caps of 1024 chunk-extension bytes and 16 chunk-size hex digits.
- The header cap (+max-header-line+ = 1024) counts header lines, not bytes, so one huge header line is buffered until it ends. Enforce your own byte limit on the socket.
- Since v0.3.0 a make-parser closure that has hit a parsing-error is poisoned and signals parser-poisoned on reuse, so create a fresh parser after an error. Duplicate headers are joined with ', ' in the hash table, and set-cookie values are a list.

## Known shortcomings

- The 1.25x is against joyent/http-parser (now unmaintained), SBCL 1.2.6 on Travis CI with no CPU and empty callbacks, never re-run against llhttp. A 2014 third-party test (#8) found it 2.5x faster than stock http-parser but 10% slower than a direct-threaded C variant, with a larger footprint (112-byte parser struct vs 32; 41+ KB for the parse function vs \~13 KB for the whole C parser). The Quicklisp dist (2026-01-01) ships the 2024-10 snapshot, which lacks v0.3.0's fixes for TE-TE and CL+TE request smuggling, conflicting duplicate Content-Length, huge chunk-size/Content-Length DoS and an out-of-bounds read in unhex-byte. Hot paths compiled with (safety 0); a 2017 memory-fault report under Woo (#30) is open. Streaming re-parses the leftover tail on each chunk (O(N^2) per its comments); the header limit counts lines, not bytes. Open bugs: responses without Content-Length or Transfer-Encoding fail (#46), 1 GiB multipart limit (#44), no QUERY method (#45). No LICENSE file (MIT in README/.asd), only old Travis CI, no releases.

## Caveats and trade-offs

Repo has no LICENSE file; MIT is declared in the README License section and in fast-http.asd's :license field. The benchmark ran on Travis CI with no CPU model stated and uses SBCL 1.2.6 (2014-era), so it has not been re-run for the current release. The gcc version is unstated. The two sides use different timers (SBCL `time` real time vs C clock()). Only one \~430-byte request was tested.

Common Lisp only (requires SBCL/CL runtime), not directly usable from C++; low-level API avoids allocation during parsing but callback-driven API differs from http-parser's; benchmark uses one fixed payload size rather than a range

## Maintenance

Active in bursts (v0.3.0 on 2026-04-06 added smuggling and DoS hardening after a 2023-2026 gap; issues #44-#46 open) and MIT per README and .asd with no LICENSE file, but Quicklisp's current dist still ships the pre-0.3.0 2024-10-12 snapshot and the only CI config is the old .travis.yml.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmark section shows fast-http 0.086s vs joyent/http-parser (C) 0.108s ('1.25 times faster') for 100,000 parses of one request header. The benchmark code is public (t/benchmark.lisp run-ll-benchmark; C driver listed in the README) and the C side states gcc -O3, but the hardware is only 'Travis CI' with no CPU model, so this first-party result is C, not A.
- **Verifier notes:** Numbers and the 1.25x ratio match the README exactly. The record said the C compiler flags were unstated, but the README shows gcc -O3 for the driver; I corrected that and the request size (430 bytes, not \~500). Metadata checked via gh GraphQL: 362 stars, not archived, not a fork, no detected license, last commit 2026-04-06 (v0.3.0), so active.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fukamachi/fast-http>
  - <https://github.com/fukamachi/fast-http/blob/master/README.markdown>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/README.markdown>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/fast-http.asd>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/t/benchmark.lisp>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/fukamachi/fast-http>
  - <https://github.com/fukamachi/fast-http/blob/master/README.markdown>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/README.markdown>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/fast-http.asd>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/fast-http-test.asd>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/.travis.yml>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/t/benchmark.lisp>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/t/parser.lisp>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/benchmark/http-parser.c>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/src/parser.lisp>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/src/fast-http.lisp>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/src/util.lisp>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/src/http.lisp>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/src/error.lisp>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/src/byte-vector.lisp>
  - <https://raw.githubusercontent.com/fukamachi/fast-http/master/src/multipart-parser.lisp>
  - <https://github.com/fukamachi/fast-http/commits/master>
  - <https://github.com/fukamachi/fast-http/issues>
  - <https://github.com/fukamachi/fast-http/issues/8>
  - <https://github.com/fukamachi/fast-http/issues/30>
  - <https://github.com/fukamachi/fast-http/issues/38>
  - <https://github.com/fukamachi/fast-http/issues/44>
  - <https://github.com/fukamachi/fast-http/issues/45>
  - <https://github.com/fukamachi/fast-http/issues/46>
  - <https://github.com/fukamachi/fast-http/pull/32>
  - <https://raw.githubusercontent.com/fukamachi/proc-parse/master/README.markdown>
  - <https://raw.githubusercontent.com/fukamachi/proc-parse/master/src/proc-parse.lisp>
  - <https://raw.githubusercontent.com/nodejs/http-parser/main/Makefile>
  - <https://raw.githubusercontent.com/nodejs/http-parser/main/README.md>
  - <https://hn.algolia.com/api/v1/search?query=fast-http%20common%20lisp&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=fukamachi%20fast-http>
  - <https://hn.algolia.com/api/v1/items/8534866>
  - <http://beta.quicklisp.org/dist/quicklisp.txt>
  - <http://beta.quicklisp.org/dist/quicklisp/2026-01-01/releases.txt>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/fukamachi/fast-http`) · [data/wave5/enrich/raw/github_com_fukamachi_fast_http.json](../../../data/wave5/enrich/raw/github_com_fukamachi_fast_http.json) (enrichment confidence 0.8)

</details>
