# libucl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> C parser and emitter for UCL, an nginx-style JSON superset; README shows it parsing JSON about 2x faster than jansson.

| | |
|---|---|
| **Beats** | jansson (C JSON parser and emitter) |
| **Claimed result** | Parse: jansson 1.3899 s vs UCL 0.6649 s (about 2.1x, derived from page data); UCL built with -O3 parses in 0.3002 s (about 4.6x vs the jansson figure, derived from page data, but the jansson figure is not stated to be -O3). Emit: jansson 0.2609 s vs UCL config 0.2423 s, JSON 0.2329 s, compact JSON 0.1811 s, YAML 0.2489 s (about 1.1x for JSON, derived from page data); UCL -O3 emit 0.1174 s config and JSON, 0.0991 s compact JSON, 0.1354 s YAML. |
| **Workload** | Parse and emit a 19 MB JSON file of about 700 thousand lines generated with json-generator.com, timing the whole-file parse and each emit format. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the jansson run. The first UCL set is described only as unoptimized, the second as 'compiled with optimizations (-O3)'. |
| **Adoption** | 1.7k stars; 162 forks |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/vstakhov/libucl) · [benchmark](https://github.com/vstakhov/libucl) |

## Verdict

The README times one parse of a generated JSON file of about 19 MB and 700 thousand lines (it matches the repo's tests/rcl_test.json.xz, which decompresses to 19,001,364 bytes and 693,050 lines): UCL 0.6649 s versus jansson 1.3899 s, about 2.1x or roughly 28.6 versus 13.7 MB/s (derived from page data), and 0.3002 s (about 63 MB/s) with UCL rebuilt at -O3; JSON emit is 0.2329 s versus 0.2609 s (about 1.1x). No CPU, compiler, jansson version or flags are given, the jansson harness is not public, and the numbers date from no later than December 2013.

## Use it when

- C or C++ daemons that want a human-friendly config format with includes, priorities, macros and comments that still accepts plain JSON
- Reading admin-controlled configuration and converting it to JSON, MessagePack or CBOR in one library
- Config files of kilobytes to a few megabytes where 30-60 MB/s parse speed is far more than enough
- You need JSON Schema v4 validation of the loaded config without a second library
- Platforms where FreeBSD-style tooling is expected: FreeBSD builds it in base as a private library

## Skip it when

- Bulk or hot-path JSON parsing: its own best figure is about 63 MB/s (-O3, derived from page data), measured in 2013 against jansson only, so a dedicated JSON parser is the better starting point
- Untrusted or adversarial input: the README says it is for trusted inputs only, and the open issue list carries many fuzzer-found memory-safety reports (use-after-free in ucl_hash_sort #388 and .inherit #387, possible heap overflow in macro parsing #367, OOB read #407, NULL dereference #410)
- Reading YAML, TOML or XML: YAML is write-only and limited, TOML and XML are not supported
- You need strict JSON semantics: duplicate keys silently become implicit arrays, relaxed syntax is accepted, and MessagePack or CBOR output keeps only the first value of an implicit array
- Multi-threaded parsing of untrusted keys: the hash seed defaults to time(NULL) and is lazily set through an unsynchronized static

## How it is fast

A hand-written single-pass state-machine parser classifies each byte through a 256-entry character-class bitmask table (ucl_chartable.h) instead of chains of comparisons. With UCL_PARSER_ZEROCOPY, keys and values that need no unescaping, lowercasing or variable expansion point into the input buffer instead of being malloc'd and copied, which cuts allocation on string-heavy JSON. Object members sit in klib khash tables keyed with mum-hash (since 0.7.0; the README numbers predate this and used uthash). There is no SIMD; it is a byte-at-a-time scanner that also tracks line and column numbers.

## Compared with alternatives

The catalogued siblings (rapidyaml, libfyaml, fkYAML, toml++ challengers such as teptris and TOMLDecoder, pugixml-class XML parsers) parse YAML, TOML or XML, which libucl cannot read; pick libucl only when you control the config format and want nginx-style UCL with includes, priorities and JSON/MessagePack/CBOR interchange in one C library, and use rapidyaml or libfyaml for YAML input and a TOML or XML sibling for those formats.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none required; optional libcurl or libfetch (URL includes), OpenSSL (signed includes), POSIX regex.h (schema patterns, on by default in autotools), Lua or LuaJIT (bindings) |
| **Minimum toolchain** | C compiler (no -std pinned in the CMake or autotools files); C++11 for the ucl++.h wrapper; CMake or autotools |
| **Platforms** | any; Linux, BSDs and macOS are the main targets, Windows builds exist (_WIN32 code paths, POSIX-only tests skipped since 0.9.4) |
| **Thread safety** | not documented; parsers are per-instance, but the mum-hash seed is a lazily initialised static with no synchronization, so create the first parser before starting threads |
| **Drop-in for the baseline** | no |

## Gotchas

- UCL_PARSER_ZEROCOPY requires the input buffer to outlive every object, and zero-copy strings are not NUL-terminated; open issue #352 (Feb 2026, PR #353 open) reports a use-after-free when ZEROCOPY is combined with ucl_parser_add_file\* because the library unmaps its own buffer, and #323 a SEGV emitting zero-copy keys with embedded NUL bytes.
- Hash seeding is time(NULL) unless the embedder defines UCL_RANDOM_FUNCTION at build time, so key-collision flooding is predictable; UCL_PARSER_SAFE_FLAGS plus ucl_parser_set_limits() are the documented hardening for less-trusted input, and only max_depth (1024) is limited by default.
- The README benchmark is a single run per figure that has been unchanged since tag 0.2.0 (2013-12-03), before the 0.7.0 move from uthash to klib; tests/speed.test pre-reads the file into page cache ('Preread file to cheat benchmark!'), test_speed.c starts the timer after mmap and parses with ZEROCOPY, and the jansson harness, version and build flags were never published, so the 2.1x parse ratio compares an unknown jansson build against a zero-copy UCL parse.
- Emitting returns a malloc'd buffer per call (free it), and the two README UCL result sets differ in optimisation level, so the -O3 figures cannot be set against the jansson numbers.

## Known shortcomings

- First-party README numbers (parse 0.6649 s vs jansson 1.3899 s), one run, no jansson harness or flags in the repo, mixed -O levels, JSON-only evidence. Filed under serialization-and-formats/yaml-toml-xml.
- Enricher: README numbers are unchanged since tag 0.2.0 (2013-12-03), before the uthash-to-klib switch in 0.7.0; one run each; test_speed.c starts the timer after mmap and parses ZEROCOPY while speed.test pre-reads the file ('Preread file to cheat benchmark!'); the jansson harness, version and flags were never published; best figure about 63 MB/s (-O3, derived) on tests/rcl_test.json.xz (19,001,364 bytes). Many open fuzzer-found memory-safety issues (#352 ZEROCOPY use-after-free, #388, #387, #367); the hash seed defaults to time(NULL) through an unsynchronized static.

## Caveats and trade-offs

First-party README numbers from one run on one generated 19 MB JSON file: no CPU, OS, compiler version, jansson version or jansson build flags are given, and the two UCL sets differ in optimization level (the first is unoptimized, the second -O3), so the ratios mix builds. tests/test_speed.c (2013 copyright header, so the numbers are probably old) times only UCL: it mmaps the file, uses UCL_PARSER_ZEROCOPY and times ucl_parser_add_chunk plus ucl_parser_get_object with clock_gettime; the jansson harness is not in the repo, and the README's 'make check' suggestion runs only UCL. Whether the quoted run used zero-copy is not said; zero-copy favours UCL over jansson, which allocates its own strings. The emit gap against jansson is small (about 1.1x for JSON). The only evidence is JSON parsing and emitting, not UCL's own config syntax or YAML/TOML/XML parsing against the category's baselines (libyaml, yaml-cpp, toml++, libxml2, pugixml). No independent benchmark including libucl was found. [retier] First-party README numbers (parse 0.6649 s vs jansson 1.3899 s) unchanged since tag 0.2.0 (2013-12-03), before the uthash-to-klib switch in 0.7.0; one run each, mixed -O levels, JSON-only evidence. test_speed.c starts the timer after mmap and parses ZEROCOPY while speed.test pre-reads the file ('Preread file to cheat benchmark!'); the jansson harness, version and flags were never published. Workload is public: tests/rcl_test.json.xz (19,001,364 bytes, 693,050 lines), best figure about 63 MB/s (-O3, derived). Many open fuzzer-found memory-safety issues (#352 ZEROCOPY use-after-free with add_file, #388, #387, #367); the hash seed defaults to time(NULL) through an unsynchronized static.

UCL is a configuration language that is a superset of JSON (macros, includes, variables, comments, implicit arrays, multiple values per key, JSON Schema v4 validation) with CBOR and MessagePack input and output, so the parse does more than plain JSON. The README warns that with all features enabled it is meant for trusted configuration input only and must not take adversarial input. C API with an object tree; zero-copy parsing is an opt-in flag (UCL_PARSER_ZEROCOPY). Bindings for Lua, Python and Haskell live in the repo.

## Maintenance

Actively maintained (0.9.4 released 2026-02-17, commits and new issue reports into October 2026), BSD-2-Clause and copyable, and built in FreeBSD base as a private library, but the open fuzzer-found memory-safety issues mean it should only see trusted configuration input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README 'Performance' section shows the quoted jansson vs UCL parse and emit times exactly, with no CPU, compiler, versions or jansson build flags; the repo's tests/test_speed.c times UCL alone and no jansson harness is public, so the comparison is not reproducible: C.
- **Verifier notes:** Numbers match the README verbatim; metadata checked: BSD-2-Clause (COPYING), 1.7k stars, 162 forks, not a fork, last commit 2026-10-04, active. Domain: the raw record carries domain parsing-and-text from the w3-mine-b assignment, but its category yaml-toml-xml belongs to serialization-and-formats, so record a domain override (domain is not a correction field here). Shortcomings to record: first-party one-run numbers, no jansson harness or flags, mixed optimization levels, JSON-only evidence.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/vstakhov/libucl>
  - <https://github.com/vstakhov/libucl/commits/master.atom>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/README.md>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/tests/test_speed.c>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/COPYING>
- **Sources the enricher read:**
  - <https://github.com/vstakhov/libucl>
  - <https://github.com/vstakhov/libucl/tags>
  - <https://github.com/vstakhov/libucl/tags?after=0.4.0>
  - <https://github.com/vstakhov/libucl/issues>
  - <https://github.com/vstakhov/libucl/issues/352>
  - <https://github.com/vstakhov/libucl/issues/323>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/README.md>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/COPYING>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/ChangeLog.md>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/include/ucl.h>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/include/ucl++.h>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/src/ucl_parser.c>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/src/ucl_hash.c>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/src/ucl_chartable.h>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/src/ucl_internal.h>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/tests/test_speed.c>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/tests/speed.test>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/tests/Makefile.am>
  - <https://raw.githubusercontent.com/vstakhov/libucl/HEAD/tests/rcl_test.json.xz>
  - <https://raw.githubusercontent.com/vstakhov/libucl/0.2.0/README.md>
  - <https://raw.githubusercontent.com/vstakhov/libucl/0.4.0/README.md>
  - <https://raw.githubusercontent.com/vstakhov/libucl/0.7.2/README.md>
  - <https://raw.githubusercontent.com/vstakhov/libucl/0.2.0/tests/test_speed.c>
  - <https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libucl/Makefile>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/vstakhov/libucl`) · [data/wave3/enrich/raw/github_com_vstakhov_libucl.json](../../../data/wave3/enrich/raw/github_com_vstakhov_libucl.json) (enrichment confidence 0.75)

</details>
