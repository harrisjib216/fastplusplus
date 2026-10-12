# uriparser

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Strict RFC 3986 URI parser in C99; only evidence is a Ruby binding beating Ruby's URI.parse 4.5-5.5x.

| | |
|---|---|
| **Beats** | Ruby standard library URI.parse (pure Ruby, Ruby 2.6); measured through the ruby-uriparser binding, not through uriparser's C API |
| **Claimed result** | README headline: 'approximatelly 7.5x faster than the standard ruby URI library'. Table, 100,000 parses, measured (non-rehearsal) pass, complex URLs: URI 1.138771 s total (1.215291 real) vs UriParser 0.207083 s total (0.259723 real), about 5.5x on total and 4.7x on real (derived from page data); simple URLs: URI 0.710042 s (0.763542 real) vs UriParser 0.157204 s (0.170975 real), about 4.5x on both (derived from page data). Rehearsal pass complex URLs: 1.146867 s vs 0.156927 s, about 7.3x (derived from page data). Addressable: 2.413826 s (complex), 1.888074 s (simple). |
| **Workload** | 100,000 URI.parse-equivalent calls in a Ruby script (Benchmark.bmbm): a 'complex' URL https://www.ruby-lang.org/en/?a=1#test and a 'simple' URL https://www.ruby-lang.org/en/, Ruby URI vs the UriParser gem (a wrapper around the uriparser C library) vs Addressable. |
| **Metric** | throughput |
| **Hardware** | Mac OS X 10.15.6, 2.7 GHz Dual-Core Intel Core i5, 16 GB 1867 MHz DDR3 (per the wrapper README); Ruby 2.6; C extension compiler and flags not stated |
| **Adoption** | 416 stars |
| **Last commit** | 2026-07-27 |
| **Links** | [repository](https://github.com/uriparser/uriparser) · [benchmark](https://github.com/tlewin/ruby-uriparser) |

## Verdict

The only numbers come from the third-party ruby-uriparser gem's README (updated September 2020; macOS 10.15.6, 2.7 GHz dual-core Core i5, Ruby 2.6, mkmf default C flags, uriparser version unstated, probably the 0.9.4 release current then): 100,000 parses of https://www.ruby-lang.org/en/?a=1#test took 0.207 s through UriParser.parse against 1.139 s through Ruby 2.6 URI.parse (about 5.5x), and 0.157 s against 0.710 s for the simple URL (about 4.5x), derived from page data; the 7.5x headline matches only the rehearsal pass. This measures a C call that builds no component strings against Ruby regex matching plus object construction, not uriparser against any native URI parser.

## Use it when

- You need strict RFC 3986 generic-URI semantics (any scheme, section 5 reference resolution, section 6.2.2 normalization) rather than browser WHATWG URL behavior.
- C or C99-only code, or embedding in a language runtime (PHP 8.5 does), where a small BSD-3-Clause library with no dependencies is wanted.
- Windows or wide-string code that wants wchar_t URIs parsed natively without converting to UTF-8.
- You need a custom allocator: every allocating function has an \*Mm variant taking a UriMemoryManager.
- Replacing an interpreted-language URI parser through a C binding, where the gain comes from leaving the interpreter rather than from the parser design.

## Skip it when

- When speed against other native parsers is the point: no published numbers exist for uriparser against Ada, Boost.URL, curl or any C/C++ parser.
- When you need WHATWG URL behavior (browser compatibility, IDNA/punycode hosts, special-scheme rules); uriparser does none of it, and scheme-based normalization (RFC 3986 6.2.3) is left to the application.
- Allocation-sensitive hot paths on URLs with many path segments: each segment is a separate heap node.
- On old releases: before 1.0.0 (2025-12-15) long or crafted input could overflow the stack through recursion (CVE-2025-67899); 1.0.1 and 1.0.2 fixed three more CVEs in 2026 (integer overflow and ptrdiff_t truncation in range comparison, EqualsUri). Pin 1.0.2 or later.
- If your code reuses a UriUriA after a failed parse (open issue #343, see gotchas).

## How it is fast

A hand-written LL(1) parser with one C function per grammar rule that dispatches on the current character with switch statements (GOALS.txt: 'not using a jump table but one function per rule'); since 1.0.0 the formerly recursive rules are goto-based loops. Parsing is zero-copy: components are pointer pairs into the caller's buffer, so the only allocations are one calloc per path segment and a small struct for IPv4/IPv6 hosts. There is no SIMD or table-driven scanning; the measured gap over Ruby comes from compiled C that creates no per-component strings, against Ruby 2.6 URI.parse, which runs one large Onigmo regex with named captures and then builds a URI::HTTPS object.

## Compared with alternatives

Pick uriparser over Ada, liburlparser or lucid-url when you need RFC 3986 generic-URI semantics, a C99 API with wchar_t support, built-in reference resolution and normalization, or the parser PHP 8.5 ships; pick Ada when you parse web URLs with WHATWG rules and want a published speed lead (188 ns/URL against curl's 1471 ns/URL on its top100 set).

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake; URIPARSER_SHARED_LIBS defaults to ON) |
| **Dependencies** | none for the library; GoogleTest &gt;=1.8.0 for tests, Doxygen and Graphviz for docs, Clang for fuzzers |
| **Minimum toolchain** | C99 compiler (required since 1.0.0), CMake &gt;=3.15.0 |
| **Platforms** | cross-platform; CI builds on Linux, Windows (Visual Studio up to 18 2026; MinGW historically) and macOS (added 2026-07) |
| **Thread safety** | Design goal in GOALS.txt: no shared globals between parser instances, so one UriParserStateA/UriUriA per thread is safe; nothing further documented. The ruby-uriparser binding shares one static UriParserStateA, safe only under Ruby's global lock. |
| **Drop-in for the baseline** | no |

## Gotchas

- Parse results are non-owning: ranges point into the input buffer, so the input must outlive the UriUriA unless you call uriMakeOwnerA, and you must always call uriFreeUriMembersA (path segments are heap nodes). uriParseUriA needs a NUL-terminated string; use the Ex variants for ranges.
- Open issue #343 (opened 2026-09-29 against master 35a9299): after a failed uriParseSingleUriExA a non-owner URI keeps stale, half-open ranges; reusing the struct (uriSetHostRegNameA, then uriFreeUriMembersA) frees caller-owned memory (ASan double free), and uriCopyUriA/uriEqualsUriA overread. Fix PR #344 is unmerged; the 1.0.3 security release (issue #333, ETA 2026-08-01) is still open.
- Harness flaw in the only benchmark: ruby-uriparser's UriParser.parse (ext/uriparser_ext/uriparser.c) stores ranges into the caller's Ruby string without keeping a reference to that string (struct uri_data holds no source VALUE and the mark function marks none) and creates component strings lazily; benchmark.rb never reads a component, so the timed call skips the string work URI.parse does, and in normal use reading .host after the source string is freed or mutated reads dangling memory. Its GC mark function also resets the cached fields and the 'updated' flag, so setter changes made before a GC are silently dropped by to_s.
- ada's competitor bench BasicBench_uriparser_just_parse (benchmarks/benchmark_template.cpp, behind ADA_COMPETITION, off by default) calls uriParseSingleUriA in a loop on one UriUriA; each call memsets the struct via ResetUri without freeing, and uriFreeUriMembersA runs once at the end, so every iteration leaks its path-segment nodes. ada itself warns that this bench does 'not use a normalized task', so any numbers from it are not like-for-like.

## Known shortcomings

- Tier C: the only evidence is a 4-star third-party Ruby binding (tlewin/ruby-uriparser) vs pure-Ruby URI.parse (C vs interpreter, no C or C++ baseline); the wrapper builds component strings lazily so it does less work per call; 7.5x headline vs 4.5-5.5x measured; flags unstated, single run. Licence BSD-3-Clause core (LGPL-2.1-or-later tests, Apache-2.0 fuzzing). Lead: ada-url/ada benchmarks/bench.cpp has a uriparser row under ADA_COMPETITION (off by default), no published numbers.
- Enricher: the ruby-uriparser benchmark skips the string work URI.parse does (UriParser.parse keeps ranges into the caller's Ruby string without holding a reference and builds component strings lazily; benchmark.rb never reads a component), so the timed call is not like-for-like; reading .host after the source string is freed reads dangling memory and a GC mark loses setter changes. Baseline URI.parse is one Onigmo regex plus object build. Benchmark ran Sep 2020 on about uriparser 0.9.4, before the 1.0.0 recursion fix (CVE-2025-67899) and 2026 CVE fixes; open issue #343 (double free after failed parse, fix PR #344 unmerged). The ada BasicBench_uriparser_just_parse leaks path-segment nodes per iteration.

## Caveats and trade-offs

Weak evidence for the uriparser C library itself. The only numbers found are from a third-party Ruby binding (tlewin/ruby-uriparser, MIT, 4 stars, last commit 2021-03-25) timing a C parse against the pure-Ruby stdlib, so the gap is mostly compiled C versus interpreted Ruby and says nothing about uriparser against any C or C++ URI parser (Ada, Boost.URL, curl, Poco, QUrl). The two sides do unequal work: the wrapper's UriParser.parse (ext/uriparser_ext/uriparser.c) calls uriParseUriA and wraps the result, but creates the Ruby strings for scheme, userinfo, host, port, path, query and fragment lazily on first access, and the benchmark never reads them, while URI.parse builds a full URI::HTTPS object with all component strings. The 7.5x headline does not match the README's own table (4.5x-5.5x on the measured pass; 7.3x only on the rehearsal pass for complex URLs). The simple-URL row times Kernel#URI(...) for the Ruby baseline vs UriParser.parse. README says 100,000 calls while benchmark/benchmark.rb defaults to 10,000 unless an argument is passed. The C extension is built by mkmf with Ruby's default flags (extconf.rb sets none) against a system uriparser of unstated version. Single run, one machine. uriparser's own README says only 'fast' with no numbers; its ChangeLog, GOALS.txt and repo tree hold no benchmark. ada-url/ada's benchmarks/bench.cpp includes a BasicBench_uriparser_just_parse competitor (behind the ADA_COMPETITION CMake option, OFF by default) that could measure uriparser against curl, but no published uriparser numbers from it were found (ada's README chart lists only ada, servo url and curl). Licensing: the library is BSD-3-Clause, the test suite LGPL-2.1-or-later and the fuzzing code Apache-2.0 (GitHub shows 'Apache-2.0 and 2 other licenses'); all OSI-approved. A previous pass (w3-mine-h) filed uriparser as no evidence; this record exists only because of the wrapper's table.

Strictly RFC 3986 compliant (not WHATWG URL), C99, supports char and wchar_t builds; library is BSD-3-Clause, but the test suite is LGPL-2.1-or-later and the fuzzing code Apache-2.0 (per the README).

## Maintenance

Actively maintained (last commit 2026-07-27; 1.0.2 released 2026-05-09 with a 1.0.3 security release pending) and BSD-3-Clause, so copyable; its place in the catalogue rests on a weak tier-C Ruby-binding benchmark whose timed call skips component-string creation and whose lazy ranges can dangle once the source string is gone.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Only numbers are a 4-star third-party Ruby binding's own README table (tlewin/ruby-uriparser, benchmark/benchmark.rb) timing UriParser.parse against Ruby's URI.parse; the code is public but the C compiler and flags are unstated (extconf.rb uses mkmf defaults) and the CPU is given only as a 2.7 GHz Dual-Core Intel Core i5, and the wrapper author is measuring his own gem, so it is not an independent suite and stays C.
- **Verifier notes:** Numbers verified on the ruby-uriparser README (measured pass complex 1.138771 vs 0.207083 s total, simple 0.710042 vs 0.157204 s; rehearsal complex 1.146867 vs 0.156927 s); metadata confirmed (416 stars, last commit 2026-07-27, BSD-3-Clause core). Not a duplicate: the binding is only the evidence source, uriparser itself is not otherwise listed. Shortcomings to record: evidence comes only from a 4-star third-party Ruby binding versus pure-Ruby URI.parse (C versus interpreter, no C/C++ baseline), the wrapper defers component string creation so it does less work per call than URI.parse, headline 7.5x overstates the measured 4.5-5.5x, flags and uriparser version unstated, single run.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-81 (wave 5); enricher w5 pair-036
- **Pages the verifier opened:**
  - <https://github.com/tlewin/ruby-uriparser>
  - <https://github.com/tlewin/ruby-uriparser/commits>
  - <https://github.com/tlewin/ruby-uriparser/tree/master/ext/uriparser_ext>
  - <https://raw.githubusercontent.com/tlewin/ruby-uriparser/HEAD/README.md>
  - <https://raw.githubusercontent.com/tlewin/ruby-uriparser/HEAD/benchmark/benchmark.rb>
  - <https://raw.githubusercontent.com/tlewin/ruby-uriparser/master/ext/uriparser_ext/uriparser.c>
  - <https://raw.githubusercontent.com/tlewin/ruby-uriparser/master/ext/uriparser_ext/extconf.rb>
  - <https://github.com/uriparser/uriparser>
  - <https://github.com/uriparser/uriparser/commits>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/README.md>
  - <https://raw.githubusercontent.com/ada-url/ada/main/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ada-url/ada/main/benchmarks/bench.cpp>
  - <https://raw.githubusercontent.com/ada-url/ada/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/uriparser/uriparser>
  - <https://github.com/uriparser/uriparser/commits>
  - <https://github.com/uriparser/uriparser/issues>
  - <https://github.com/uriparser/uriparser/issues/343>
  - <https://github.com/uriparser/uriparser/issues/333>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/README.md>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/GOALS.txt>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/THANKS>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/include/uriparser/Uri.h>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/include/uriparser/UriBase.h>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/src/UriParse.c>
  - <https://raw.githubusercontent.com/uriparser/uriparser/HEAD/src/UriCommon.c>
  - <https://raw.githubusercontent.com/tlewin/ruby-uriparser/HEAD/README.md>
  - <https://raw.githubusercontent.com/tlewin/ruby-uriparser/HEAD/benchmark/benchmark.rb>
  - <https://raw.githubusercontent.com/tlewin/ruby-uriparser/HEAD/ext/uriparser_ext/uriparser.c>
  - <https://raw.githubusercontent.com/tlewin/ruby-uriparser/HEAD/ext/uriparser_ext/extconf.rb>
  - <https://raw.githubusercontent.com/tlewin/ruby-uriparser/HEAD/lib/uriparser.rb>
  - <https://github.com/tlewin/ruby-uriparser/commits/master/README.md>
  - <https://raw.githubusercontent.com/ruby/ruby/v2_6_0/lib/uri/rfc3986_parser.rb>
  - <https://raw.githubusercontent.com/ada-url/ada/main/benchmarks/bench.cpp>
  - <https://raw.githubusercontent.com/ada-url/ada/main/benchmarks/benchmark_template.cpp>
  - https://www.php.net/releases/8.5/en.php (WebSearch snippet only; direct fetch failed)
  - https://thephp.foundation/blog/2025/10/10/php-85-uri-extension/ (WebSearch snippet only)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/uriparser/uriparser`) · [data/wave5/enrich/raw/github_com_uriparser_uriparser.json](../../../data/wave5/enrich/raw/github_com_uriparser_uriparser.json) (enrichment confidence 0.6)

</details>
