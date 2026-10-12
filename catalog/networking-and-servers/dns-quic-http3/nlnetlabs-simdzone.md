# simdzone

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> SIMD DNS zone-file (presentation format) parser in C; about 4x Knot DNS's zscanner on the .se zone.

| | |
|---|---|
| **Beats** | Knot DNS libzscanner (zscanner) 3.3.4, and NSD 4.9's previous zonec zone parser |
| **Claimed result** | se.zone.txt: simdzone Haswell (AVX2) kernel 0.81 GB/s vs Knot 3.3.4 0.19 GB/s, about 4.3x (derived from page data); Westmere (SSE4.2) kernel 0.73 GB/s (about 3.8x, derived); scalar fallback kernel 0.38 GB/s (about 2.0x, derived). Cycles per byte 3.38 (Haswell) vs 17.06 (Knot); instructions per byte 11.90 vs 23.45. |
| **Workload** | Complete parse of the Sweden (.se) DNS zone file, 1361515551 bytes, one thread, counting accepted resource records in a callback; the harness includes disk read (file expected in page cache). |
| **Metric** | throughput |
| **Hardware** | CPU model not stated on the pages opened; the README output shows clock readings of 2.72 GHz to 3.16 GHz from Linux perf counters. The simdzone README separately quotes an Intel Core i7-1065G7 run (clang 17.0.6, Fedora 39) with no baseline. |
| **Compiler and flags** | CMake Release (default when no build type is given), C11 and C++20; Dockerfile is ubuntu:24.04 with g++ and clang installed; simdzone pinned to commit aab6386, zonec to 0196635, Knot from the libknot-dev package. Exact compiler and flags used for the quoted run are not stated. |
| **Adoption** | 137 stars; replaced the zone parser in NSD (NLnet Labs authoritative name server) |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/NLnetLabs/simdzone) · [benchmark](https://github.com/lemire/zone_benchmarks) |

## Verdict

On the 1,361,515,551-byte Sweden (.se) zone file, a full parse that counts records in a callback ran at 0.81 GB/s with the AVX2 kernel, 0.73 GB/s with SSE4.2 and 0.38 GB/s scalar versus 0.19 GB/s for Knot DNS 3.3.4's zscanner (about 4.3x, 3.8x and 2.0x, derived from page data), best of repeated runs in Daniel Lemire's zone_benchmarks (CMake Release, Ubuntu 24.04 Docker image, Knot from the distro package, CPU model and compiler not stated). NLnet Labs' NSD 4.10.0 announcement reports 1.6x to 3.8x faster zone loading end to end after the switch from the Flex+Bison parser, less for NSEC3 zones (search snippet only; the page is blocked here).

## Use it when

- Loading large zone files (TLD-scale: the .se zone is 1.36 GB, .com about 12-24 GB) where parse time dominates reloads, e.g. an authoritative server, zone signer or zone-diff tool
- x86-64 servers with AVX2 or SSE4.2, where the 0.73-0.81 GB/s kernels apply; the scalar fallback still measured about 2x Knot's zscanner in the same run
- You want validated wire-format RDATA per record through a callback and will build your own in-memory zone
- A C99, BSD-3-Clause dependency with no third-party runtime libraries that is already shipped inside NSD

## Skip it when

- Small zones or one-off parses, where start-up and I/O dominate and Knot's zscanner or ldns are already integrated
- ARM64, RISC-V or other non-x86 targets expecting SIMD speed: only the scalar fallback kernel exists there, and MSVC builds probably get only the fallback because kernels are gated on -march flags
- You need a serializer (wire to presentation text) or a zone object model: neither exists
- Untrusted zone input with \$INCLUDE left on (set no_includes), or reliance on strict NSEC validation in generic notation (open bug #232)
- You need the speedup confirmed for your own zone mix: the only public cross-parser numbers are one zone file from the co-author's 2024 harness

## How it is fast

It follows simdjson's two-stage design: stage 1 classifies 64-byte blocks with SIMD compares and nibble-table shuffles into bitmasks for newlines, backslashes, quotes, semicolons, blanks and special characters, finds escaped characters with simdjson's odd/even-sequence trick (code copied from simdjson), resolves quoted regions with prefix-XOR, and writes field-start and delimiter positions to a tape using popcount and trailing-zero counts. Comments still need a short branching loop because quotes and semicolons can nest either way. Stage 2 parses fields from the tape with type-specific parsers; RR type and class mnemonics are resolved through a generated perfect hash (magic multiply into a 256-entry table) and verified with an SSE compare. The AVX2 (Haswell) or SSE4.2+PCLMULQDQ (Westmere) kernel is picked at run time, with a scalar fallback.

## Compared with alternatives

None of the catalogued siblings parses zone files: Unbound, Hickory DNS, NailDNS and Bundy are DNS servers and the rest are QUIC/HTTP3 stacks, so pick simdzone whenever the bottleneck is reading presentation-format zone data, for example under one of those servers or a zone tool.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at run time (C standard library only); cmocka for tests, Doxygen and Sphinx for docs, all optional |
| **Minimum toolchain** | C99 compiler; CMake 3.10+ (an autoconf build is also shipped, as used by NSD); SIMD kernels need a GCC or Clang that accepts -march=westmere and -march=haswell |
| **Platforms** | x86-64 with AVX2 or SSE4.2 kernels chosen at run time; any other architecture (aarch64, RISC-V, big-endian) via the scalar fallback; Linux, BSDs (NSD CI covers FreeBSD, OpenBSD, NetBSD), MinGW and MSVC builds are supported by the CMake file |
| **Thread safety** | not documented; all parser state lives in the caller's zone_parser_t and buffers and zone.c holds no mutable globals, so one parser per thread should be safe (inferred from source) |
| **Drop-in for the baseline** | no |

## Gotchas

- zone_parse_string() requires the input to be null-terminated and padded by ZONE_BLOCK_SIZE (64) bytes (issue #174); issue #267, opened 2026-09-16, reports that strings ending in a token at an exact multiple of 64 bytes failed to parse, with a fix commit (d7bbff5) referenced but the issue still open.
- Open bug #232 (since 2024-09): check_nsec never advances its data pointer, so malformed NSEC type bitmaps given in generic \# notation can pass validation.
- The origin must be supplied in wire format, owner names and RDATA are handed to the callback in reusable scratch buffers (copy what you keep), and the ZONE_KERNEL environment variable overrides kernel selection on every parse.
- Harness caveats behind the quoted numbers: lemire/zone_benchmarks was last updated 2024-06-28 and pins simdzone aab6386; its README table predates the current bench.cpp (row names differ, no read_file or zonec rows); record counts are accumulated but never compared across parsers (both runs abort on any parse error, so a partial parse would not pass silently); Knot mmaps the whole file while simdzone reads 16 KB windows with fread, and both inside the timed region.

## Known shortcomings

- lemire/zone_benchmarks (co-author's repo): 0.81 vs Knot libzscanner 0.19 GB/s with CPU and compiler unstated and Knot taken from a distro package; the SPE 55(4) paper was seen through snippets only (arxiv blocked).
- Enricher: lemire/zone_benchmarks was last updated 2024-06-28 and pins simdzone aab6386; its README table predates the current bench.cpp (row names differ); record counts are never compared across parsers; Knot mmaps the whole file while simdzone freads 16 KB windows, both inside the timer. Open bugs #232 (check_nsec never advances its pointer, so bad NSEC bitmaps pass validation) and #267. NSD 4.10.0 snippet: 1.6x-3.8x faster zone load.

## Caveats and trade-offs

The quoted table is from the benchmark repo of Daniel Lemire, co-author of the simdzone paper (Koekkoek and Lemire, 'Parsing Millions of DNS Records per Second', Software: Practice and Experience 55(4), 2025; the simdzone README still says 'to appear'), so it is not independent of the project. The paper could not be opened (arxiv.org and r-libre.teluq.ca blocked); search snippets quote simdzone above 0.8 GB/s, Knot DNS at 0.19 to 0.32 GB/s and NSD's parser at 0.05 to 0.07 GB/s (snippet only). The README example output predates the current harness: it prints 'simdzonehaswell' and has no read_file or 'zonec (NSD 4.9)' rows, which bench.cpp now emits, so no published zonec number exists on the repo page. Build asymmetry: simdzone is fetched at commit aab6386 and built from source in CMake Release, while Knot's zscanner comes from Ubuntu 24.04's prebuilt libknot-dev package with distro flags. No CPU model or compiler version is given on reachable pages; the Dockerfile installs both g++ and clang and CMake picks the default. One zone file (.se) in the README; both parsers only count records in a callback rather than building a zone, and the timed region includes reading the file (expected to be in page cache). The simdzone repo README states no baseline comparison of its own (its i7-1065G7 .com run has no competitor). SIMD kernels are x86-64 only (SSE4.2, AVX2); other targets use the fallback kernel, which is about 2x Knot in this run (derived from page data).

SIMD kernels exist only for x86-64 (SSE4.2 Westmere and AVX2 Haswell, selected at run time); RISC-V and other targets use the scalar fallback kernel (0.38 GB/s in the quoted run, still about 2x Knot). Callback-based C library, deserializer only for now (serializer planned). Parts copied from simdjson under its BSD licence.

## Maintenance

Actively maintained by NLnet Labs (last commit 2026-09-30, recent fixes in September 2026) and shipped as NSD's parser since 4.10.0, which search results show vendored in NetBSD's and OpenBSD's NSD source trees; BSD-3-Clause and copyable, though version 0.1.0 carries a few open validation and padding bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** lemire/zone_benchmarks README (harness benchmarks/bench.cpp + simdzonehelper.h, public) shows simdzone haswell 0.81 GB/s, westmere 0.73, fallback 0.38 vs knot3.3.4 0.19 GB/s on the 1361515551-byte se.zone.txt, but no CPU model and no exact compiler, so not A. The win is backed by the peer-reviewed paper (Koekkoek and Lemire, Software: Practice and Experience 55(4), 2025), whose reported figures (simdzone above 0.8 GB/s, Knot 0.19-0.32 GB/s, NSD 0.05-0.07 GB/s) were seen only in search snippets because arxiv.org and the TELUQ repository are blocked.
- **Verifier notes:** Numbers match the zone_benchmarks README exactly; harness is a real full parse with a counting callback on both sides (no no-op). Metadata checked: BSD-3-Clause, 137 stars, 24 forks, not a fork, last commit 2026-09-30, active. Shortcomings to record: co-author's benchmark repo, CPU and compiler unstated, Knot from distro package vs simdzone built from source, paper seen via snippets only, x86-64-only SIMD.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** zone_benchmarks (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/lemire/zone_benchmarks>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/benchmarks/bench.cpp>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/benchmarks/simdzonehelper.h>
  - <https://github.com/NLnetLabs/simdzone>
  - <https://github.com/NLnetLabs/simdzone/commits>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/NLnetLabs/simdzone>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/README.md>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/include/zone.h>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/src/zone.c>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/src/haswell/parser.c>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/src/haswell/simd.h>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/src/generic/scanner.h>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/src/westmere/type.h>
  - <https://raw.githubusercontent.com/NLnetLabs/simdzone/HEAD/src/bench.c>
  - <https://github.com/NLnetLabs/simdzone/tree/main/src>
  - <https://github.com/NLnetLabs/simdzone/issues?q=is%3Aissue>
  - <https://github.com/NLnetLabs/simdzone/issues/267>
  - <https://github.com/NLnetLabs/simdzone/issues/232>
  - <https://github.com/lemire/zone_benchmarks/commits/main>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/benchmarks/bench.cpp>
  - <https://raw.githubusercontent.com/lemire/zone_benchmarks/HEAD/benchmarks/simdzonehelper.h>
  - <https://raw.githubusercontent.com/CZ-NIC/knot/master/src/libzscanner/scanner.rl>
  - <https://raw.githubusercontent.com/NLnetLabs/nsd/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/NLnetLabs/nsd/HEAD/doc/RELNOTES>
  - WebSearch: simdzone NSD 4.10 zone load time faster parser benchmark (snippets of nlnetlabs.nl NSD 4.10.0 announcement and community.nlnetlabs.nl 4.10.0rc1 thread)
  - https://nlnetlabs.nl/news/2024/Jun/13/nsd-4.10.0-released/ (EGRESS_BLOCKED)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/nlnetlabs/simdzone`) · [data/wave3/enrich/raw/github_com_nlnetlabs_simdzone.json](../../../data/wave3/enrich/raw/github_com_nlnetlabs_simdzone.json) (enrichment confidence 0.8)

</details>
