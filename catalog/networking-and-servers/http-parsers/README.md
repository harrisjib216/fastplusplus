# HTTP parsers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md)</sub>

**What these beat:** llhttp, http-parser, picohttpparser  
**25 entries:** 5 tier A · 1 tier B · 18 tier C · 1 tier D · 22 copyable, 3 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**lucid-url**](lucid-softworks-url.md) | Dependency-free, safe-Rust WHATWG URL parser with Ada's API; faster than ada::url, slower than ada::url_aggregator and can_parse. | **A** | Rust | MIT | 🟢 active |
| 2 | [**blazehttp**](justiliane-blazehttp.md) | Go HTTP/1.1+HTTP/2 server/client with zero-copy header parser; \~11-14% more HTTP/1.1 req/s than fasthttp (author's wrk runs). | **A** | Go | MIT | 🟢 active |
| 3 | [**picohttpparser-rs**](logicpl4gue-picohttpparser-rs.md) | Safe-Rust, ABI-identical rewrite of picohttpparser; beats scalar -O2 C only on header-heavy requests, loses on six of eight workloads. | **A** | Rust | MIT | 🟢 active |
| 4 | [**ada-rs**](countradooku-ada-rs.md) | Memory-safe Rust port of the Ada WHATWG URL parser; 7.4% faster than C++ Ada on a 9-URL corpus. | **A** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 5 | [**picohttpparser AVX2 fork (vkrasnov)**](vkrasnov-picohttpparser.md) | AVX2 bitmap rewrite of picohttpparser's header scanner; 1.7-1.8x the SSE4.2 PCMPESTRI version on Haswell. | **A** | C | MIT OR Perl License… | 🔴 abandoned |
| 6 | [**Ada (WHATWG URL parser)**](ada-url-ada.md) | WHATWG-compliant C++20 URL parser used by Node.js; about 7.8x faster than libcurl's URL API on real-world URLs. | **B** | C++ | Apache-2.0 OR MIT | 🟢 active |
| 7 | [**Puma http11_parser (Mongrel/Ragel-based HTTP/1.x parser)**](puma-puma.md) | Mongrel's Ragel-generated C request/header tokenizer, vendored in Puma; \~1.26x faster than joyent http_parser in a 2016 test. | **C** | C | BSD-3-Clause | 🟢 active |
| 8 | [**httparse (Rust push parser for HTTP/1.x)**](seanmonstar-httparse.md) | Rust's standard zero-copy HTTP/1.x push parser; beats picohttpparser only when pico is built without SSE4.2. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 9 | [**uriparser**](uriparser-uriparser.md) | Strict RFC 3986 URI parser in C99; only evidence is a Ruby binding beating Ruby's URI.parse 4.5-5.5x. | **C** | C | BSD-3-Clause | 🟢 active |
| 10 | [**fast-http**](fukamachi-fast-http.md) | Pure Common Lisp HTTP/1.x request/response parser; on SBCL its README shows it 1.25x faster than joyent's C http-parser. | **C** | Common Lisp | MIT | 🟢 active |
| 11 | [**milo**](shogunpanda-milo.md) | Strict Rust HTTP/1.1 parser (crate, C++ lib, WASM) meant to replace llhttp in Node.js; \~1.07x llhttp in one test. | **C** | Rust | ISC | 🟢 active |
| 12 | [**zttp**](kludex-zttp.md) | Sans-IO HTTP/1.1 (plus HTTP/2, HTTP/3) parser for Python with a Zig core; out-parses httptools/llhttp on 13 of 14 microbenchmarks. | **C** | Zig | BSD-3-Clause | 🟢 active |
| 13 | [**ls-hpack (LiteSpeed HPACK)**](litespeedtech-ls-hpack.md) | LiteSpeed's C HPACK (RFC 7541) codec with 64K-entry two-byte Huffman tables; beat a 2016 nghttp2 Huffman encoder 2.4-5.8x. | **C** | C | MIT | 🟢 active |
| 14 | [**hparse**](nikneym-hparse.md) | Zig SIMD HTTP/1.x parser modeled on picohttpparser; about 1.14x faster than a gcc -O3 picohttpparser build on x86-64. | **C** | Zig | MIT | 🟢 active |
| 15 | [**liburlparser (abspath fast-path vs ada)**](mohammadraziei-liburlparser.md) | C++17 RFC 3986-style URL splitter with Public Suffix List domain extraction; its own parse+accessor loop runs \~1.25x ahead of ada. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 16 | [**gunicorn_h1c**](benoitc-gunicorn-h1c.md) | CPython C extension over vendored picohttpparser that parses HTTP/1.1 requests for Gunicorn; claims \~1.1-2.1x httptools throughput. | **C** | C | MIT | 🟢 active |
| 17 | [**httpp**](cebem1nt-httpp.md) | Single-header, zero-allocation C HTTP/1.1 request parser; \~2.26x picohttpparser's scalar build on one sample request, with far less validation. | **C** | C | MIT | 🟢 active |
| 18 | [**http.c3l**](lsfratel-http-c3l.md) | Sans-IO streaming HTTP/1.1 request parser in C3; ties picohttpparser with callbacks, \~13% faster only when extracting nothing. | **C** | C3 | MIT | 🟢 active |
| 19 | [**iohttpparser (stateful-strict/lenient profiles)**](ioplane-iohttpparser.md) | Pull-based C23 HTTP/1.1 parser with strict framing checks; beats llhttp on header-heavy messages, not on tiny requests. | **C** | C | MIT | 🟢 active |
| 20 | [**sorug (WHATWG URL parser, Rust)**](hocestnonsatis-sorug.md) | Safe-Rust WHATWG URL parser with a zero-copy fast path for canonical URLs; 3.4-4.1x faster than the url crate on ASCII. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 21 | [**thhp (Totemo-Hayai HTTP Parser)**](kei10in-thhp.md) | Small zero-copy Rust HTTP/1.x parser; beats picohttpparser only on short requests (1.14-1.29x), ties or loses on realistic ones. | **C** | Rust | MIT | 🔴 abandoned |
| 22 | [**jianrong7/http-parser (Go zero-alloc parser)**](jianrong7-http-parser.md) | Tiny zero-allocation Go HTTP/1.x request parser that records byte offsets; \~5-10x faster than net/http.ReadRequest, with far less validation. | **C** | Go | no license (study only) | 🟢 active |
| 23 | [**Picozig (zig-pico)**](solenopsys-zig-pico.md) | Pure-Zig port of picohttpparser's request parser. A self-run bench claims \~1.6x over scalar picohttpparser, but the baseline was not re-measured. | **C** | Zig | no license (study only) | 🟢 active |
| 24 | [**SynapServe**](paper-synapserve.md) | Closed-source zero-allocation Rust HTTP/1.1 parser inside the SynapServe io_uring server; claims 1.11-1.25x faster tokenization than httparse. | **C** | Rust | no license (study only) | ⚪ unknown |
| 25 | [**llhttp**](nodejs-llhttp.md) | Node.js's HTTP/1.x parser: a C state machine generated by llparse that replaced http_parser; README claims 2.56x its parsing bandwidth. | **D** | C | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
