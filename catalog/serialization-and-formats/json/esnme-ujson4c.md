# ujson4c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Small C decode-only JSON DOM (UltraJSON decoder plus arena allocator); 4-10% faster than RapidJSON on citm/twitter, slower on canada.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | Parse to DOM, citm_catalog.json: ujson4c 1.841 ms vs RapidJSON 1.950 ms and RapidJSON_Insitu 1.922 ms (\~1.04-1.06x faster); twitter.json: ujson4c 1.114 ms vs RapidJSON 1.227 ms (\~1.10x faster) but slower than RapidJSON_Insitu 0.995 ms; canada.json: ujson4c 5.990 ms vs RapidJSON 4.755 ms (slower). Times verbatim from the CSV; ratios derived from page data. |
| **Workload** | nativejson-benchmark '1. Parse' test (parse JSON text into a DOM) on canada.json, citm_catalog.json and twitter.json; ujson4c wins on citm_catalog.json and on twitter.json vs plain RapidJSON. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4980HQ @ 2.80GHz (MacBook Pro, mac64) |
| **Compiler and flags** | clang 7.0, mac64 (per results file name); premake5 gmake 'release' configuration: optimize "Full", NDEBUG, -march=native -Wall -Wextra (build/premake5.lua) |
| **Adoption** | 155 stars |
| **Last commit** | 2014-04-08 |
| **Links** | [repository](https://github.com/esnme/ujson4c) · [benchmark](https://github.com/miloyip/nativejson-benchmark/blob/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

nativejson-benchmark's '1. Parse' test (JSON text to DOM), CSV committed 2016-09-09, Core i7-4980HQ @ 2.80 GHz, clang 7.0 on macOS, release build with full optimization and -march=native, testing ujson4c at its final commit e14f3fd: 1.841 vs 1.950 ms for RapidJSON on citm_catalog.json (\~1.06x) and 1.114 vs 1.227 ms on twitter.json (\~1.10x), but 5.990 vs 4.755 ms on canada.json (RapidJSON \~1.26x faster). RapidJSON's in-situ mode is faster than ujson4c on twitter (0.995 ms) and canada (5.197 ms) and slightly slower on citm (1.922 ms).

## Use it when

- A C-only or legacy build that parses whole documents once and reads a handful of fields, where a four-file source drop with no dependencies is convenient.
- Object-heavy documents with many short strings and integers (citm_catalog/twitter shape), where the 2016 benchmark puts its parse time 4-10% ahead of plain RapidJSON.
- Code that wants wide strings anyway (for example Windows wchar_t APIs), so the UTF-8 to wchar_t conversion during parse is useful work rather than overhead.
- Embedded or game code that wants to hand the parser its own initial buffer (1 KB minimum, stack is fine) plus malloc/free/realloc hooks through UJHeapFuncs.

## Skip it when

- Untrusted input: the parser stops at a NUL byte rather than at cbInput and reads past the end otherwise (issue #11), accessors crash on the NULL returned by a failed decode (issue #6), and the bundled decoder still has the code patterns fixed upstream in UltraJSON 5.4.0 as CVE-2022-31117 (double free when realloc fails) and CVE-2022-31116 (unpaired surrogates mis-decoded).
- Float-heavy data or anything that needs exact doubles: canada.json parses about 1.26x slower than RapidJSON, nativejson-benchmark scores it 34/66 on Parse Double, integers beyond int64 are rejected, and some 20-digit values wrap silently (45913141877270640000.0 decodes as 9.0196537298515364e+18).
- Workloads that walk the whole tree: its linked-list DOM made the benchmark's Statistics traversal 2.3-3.0x slower than RapidJSON (citm 0.488 vs 0.161 ms), so parse plus walk on citm totals 2.33 ms vs 2.11 ms for RapidJSON (derived from the same CSV).
- Memory-constrained parsing: on citm_catalog it used 4,698,144 bytes (peak 12,656,672) vs RapidJSON's 1,123,008 (peak 1,131,472). wchar_t strings cost 4 bytes per character, and the first string in a large document allocates a scratch buffer of remaining input bytes x sizeof(wchar_t).
- Anything that needs serialization, strict validation (it accepts trailing commas in objects, leading zeros, raw tabs and newlines in strings, and '0e'), or an upstream that fixes bugs: the repo is archived and the last commit is 2014-04-08.

## How it is fast

The decoder is hand-written recursive descent: a switch on the first byte picks the value parser, and a 256-entry lookup table classifies string bytes (plain, UTF-8 lead length, quote, escape, NUL). Every node comes from a bump (arena) allocator that starts with a 16 KB slab and doubles each new slab, so a whole document costs about 10 mallocs (AllocCount 10-11 in the benchmark vs 25-61 for RapidJSON) and is freed in one pass. Numbers take a fast path that is not correctly rounded: integers accumulate in a uint64, fraction digits (max 15) scale through a pow10 table and exponents call pow(); the strtod path (preciseFloat) is switched off by UJDecode. There is no SIMD.

## Compared with alternatives

For new C code, yyjson is the better pick: it is also plain C, maintained, and parses about 2.3x faster than RapidJSON in-situ on twitter.json per its entry. In the same 2016 CSV ujson4c beats gason and sajson on citm_catalog (1.841 vs 2.105 and 1.981 ms) but loses to both on twitter (1.114 vs 1.013 and 0.901 ms), so choose it only if you already vendor it or need wchar_t output from a pure-C parser.

## Integration

| | |
|---|---|
| **Form** | source-drop: copy src/ujdecode.c, src/ujdecode.h, 3rdparty/ultrajson.h and 3rdparty/ultrajsondec.c into your project (per the README) |
| **Dependencies** | none beyond the C standard library (math.h pow, strtod, wchar.h) |
| **Minimum toolchain** | Not stated. The code needs C99 (stdint.h, // comments, inline) or a C++ compiler (the header wraps the API in extern "C"); MSVC is handled through _WIN32 typedefs and __fastcall. nativejson-benchmark built it with clang 7.0 in 2016; the last code change upstream was a clang -Wall -Wextra warning cleanup in 2013. |
| **Platforms** | Any little- or big-endian target (ultrajson.h stops with #error if the byte order cannot be detected); no SIMD. The arena allocator does not align allocations, so nodes after some strings land on 4-byte (2-byte on Windows) boundaries: harmless on x86-64, undefined behavior in C and a risk on strict-alignment CPUs. |
| **Thread safety** | Not documented. In the source, each UJDecode call keeps its state in its own arena and shares only static const tables, so separate documents can be decoded on separate threads. Each call also puts a 128 KB escape buffer on the stack (JSON_MAX_STACK_BUFFER_SIZE), which matters for small thread stacks. |
| **Drop-in for the baseline** | no |

## Gotchas

- UJObjectUnpack assigns outputs in the order keys are found in the JSON, not the order of keyNames, so a missing or reordered key puts values in the wrong variables (issues #7 and #10; fix PR #3 was closed unmerged).
- Pass a NUL-terminated buffer: cbInput is used only for the trailing-data check and scratch sizing, not as the parse bound (issue #11).
- Check UJDecode's return before touching the tree: UJGetType, UJIsObject and UJObjectUnpack dereference the pointer with no NULL check (issue #6). There are no allocation checks either; a failed malloc of the default 16 KB heap or of a new slab is dereferenced (issue #9).
- Strings are wchar_t, so \u0000 becomes an embedded NUL in a NUL-terminated wide string; UJIsInteger is declared as taking UJObject\* (issue #4); nesting is capped at 1024 levels (JSON_MAX_OBJECT_DEPTH).

## Known shortcomings

- Weak conformance in nativejson-benchmark (Parse Double 34/66, Parse String 5/9) and about 4x RapidJSON's memory. Unmaintained since 2014-04.
- Unsafe for untrusted input: stops at NUL rather than cbInput (over-read, #11), no NULL checks on failed decodes (#6) or malloc (#9), and it bundles UltraJSON decoder code with the patterns behind CVE-2022-31117 and CVE-2022-31116. UJObjectUnpack fills outputs in document order, not caller order (#7, #10). Parse plus full walk is slower than RapidJSON on citm (2.33 vs 2.11 ms, derived); peak memory 12.66 MB vs 1.13 MB. The Parse String 5/9 score is partly a harness artifact; Parse Double 34/66 is real.

## Caveats and trade-offs

2016 benchmark numbers on old hardware and compiler (clang 7.0); the margin over RapidJSON is small (\~4-10%) and workload-specific: it beats plain RapidJSON on citm_catalog.json and twitter.json, beats RapidJSON_Insitu only on citm_catalog.json, and loses on canada.json. It uses about 4x RapidJSON's memory on citm_catalog.json (4,698,144 vs 1,123,008 bytes). nativejson conformance is weak (Parse Double 34/66, Parse String 5/9 correct) and it has no stringify support. The repo is archived; the last commit is 2014-04-08. GitHub reports license NOASSERTION, but LICENSE.txt is BSD-3-Clause text (Electronic Arts), and the bundled decoder carries TCL-derived numeric code.

Wraps UltraJSON's C tokenizer with a decode-helper layer; RapidJSON is still faster on the other two test files in the same suite (canada.json, twitter.json), so this is not a general win; project has been archived since 2015 (unmaintained, GitHub-flagged 'Other' license though the bundled LICENSE.txt is a standard BSD-3-Clause EA grant).

## Maintenance

Archived (last commit 2014-04-08, nine open issues including crash and wrong-output bugs) and BSD-3-Clause per LICENSE.txt, although GitHub reports NOASSERTION and the decoder also carries MODP_ASCII and TCL-derived code notices; at about 2,300 lines in four files it is easy to vendor and patch, but you own every fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The independent nativejson-benchmark CSV (committed 2016-09-09) has ujson4c and RapidJSON '1. Parse' rows on an i7-4980HQ with clang 7.0; the code is public (src/tests/ujson4ctest.cpp, src/cjsonlibs/ujson4c_all.c) and build/premake5.lua sets release flags (optimize Full, NDEBUG, -march=native). Code, compiler, flags and CPU model are all stated, so A holds.
- **Verifier notes:** The citm_catalog numbers match the CSV exactly. The record's claim that ujson4c loses on the other two files was wrong: it also beats plain RapidJSON on twitter.json. last_commit is corrected from 2015-04-21 (that is the repo pushed_at date) to 2014-04-08, the date of the last commit on master.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/build/premake5.lua>
  - https://github.com/miloyip/nativejson-benchmark/blob/master/sample/conformance_ujson4c%20(C).md
  - <https://github.com/esnme/ujson4c>
  - <https://github.com/esnme/ujson4c/blob/master/LICENSE.txt>
  - <https://github.com/esnme/ujson4c/blob/master/3rdparty/ultrajsondec.c>
- **Sources the enricher read:**
  - <https://github.com/esnme/ujson4c>
  - <https://github.com/esnme/ujson4c/blob/master/README.rst>
  - <https://github.com/esnme/ujson4c/blob/master/LICENSE.txt>
  - <https://github.com/esnme/ujson4c/blob/master/src/ujdecode.h>
  - <https://github.com/esnme/ujson4c/blob/master/src/ujdecode.c>
  - <https://github.com/esnme/ujson4c/blob/master/3rdparty/ultrajson.h>
  - <https://github.com/esnme/ujson4c/blob/master/3rdparty/ultrajsondec.c>
  - <https://github.com/esnme/ujson4c/blob/master/tests/benchmark.c>
  - <https://github.com/esnme/ujson4c/commits/master>
  - <https://github.com/esnme/ujson4c/issues>
  - <https://github.com/esnme/ujson4c/pulls?q=is%3Apr>
  - <https://github.com/esnme/ujson4c/issues/5>
  - <https://github.com/esnme/ujson4c/issues/6>
  - <https://github.com/esnme/ujson4c/issues/7>
  - <https://github.com/esnme/ujson4c/issues/9>
  - <https://github.com/esnme/ujson4c/issues/10>
  - <https://github.com/esnme/ujson4c/issues/11>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - https://github.com/miloyip/nativejson-benchmark/blob/master/sample/conformance_ujson4c%20(C).md
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/src/tests/ujson4ctest.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/src/cjsonlibs/ujson4c_all.c>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/build/premake5.lua>
  - <https://github.com/ultrajson/ultrajson/security/advisories/GHSA-fm67-cv37-96ff>
  - <https://github.com/ultrajson/ultrajson/security/advisories/GHSA-wpqr-jcpx-745r>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/esnme/ujson4c`) · [data/wave4/enrich/raw/github_com_esnme_ujson4c.json](../../../data/wave4/enrich/raw/github_com_esnme_ujson4c.json) (enrichment confidence 0.8)

</details>
