# qajson4c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🔴 abandoned

> C99 JSON DOM parser building the whole tree in one caller-supplied buffer; claims lower parse memory than RapidJSON (unpublished).

| | |
|---|---|
| **Beats** | RapidJSON, nlohmann/json |
| **Claimed result** | No numbers found. README claims "Top scores at the nativejson-benchmark on category Parsing Memory, Parsing Memory Peak and AllocCount while scoring quite well at Parsing Time" (a memory claim, not a speed claim), but nativejson-benchmark's published sample results (2016-09-09) contain no qajson4c row. |
| **Workload** | miloyip/nativejson-benchmark shootout: parses/generates the suite's standard JSON test files across many C/C++ JSON libraries (including RapidJSON and nlohmann/json), measuring parse time, memory footprint, peak memory, and allocation count |
| **Metric** | memory |
| **Adoption** | 10 stars; wired into miloyip/nativejson-benchmark as a test target (submodule points to the fork USESystemEngineeringBV/qajson4c; PR #122 to repoint it to DeHecht/qajson4c is unmerged) |
| **Last commit** | 2019-03-22 |
| **Links** | [repository](https://github.com/DeHecht/qajson4c) · [benchmark](https://github.com/miloyip/nativejson-benchmark) |

## Verdict

Nothing has been measured. The README says qajson4c got top scores in nativejson-benchmark's Parse Memory, Memory Peak and AllocCount categories, but that suite's only published results (2016-09-09, clang 7.0, Core i7-4980HQ, mac64/mac32) predate the qajson4c integration (PR #78, merged 2017-05-05) and have no qajson4c row. No figures exist against RapidJSON or nlohmann/json on any compiler or hardware.

## Use it when

- Firmware or other no-heap targets: parse into a static buffer after sizing it exactly with QAJ4C_calculate_max_buffer_size, or bound it by the formula nodes x 16 B plus the bytes of strings longer than 10 chars.
- Read-mostly config, command or telemetry messages where you need O(1) array indexing and key lookup rather than a token stream.
- Writable input buffers where copying strings is unaffordable: QAJ4C_parse_insitu leaves only the node cells in the DOM buffer.
- Emitting small JSON documents without malloc: build with QAJ4C_Builder in a fixed buffer and stream them out through QAJ4C_print_callback (one char at a time) or QAJ4C_print_buffer_callback (chunks), for example to a UART.
- Callers that need a parse error code plus the byte position of the failure (QAJ4C_error_get_errno / QAJ4C_error_get_json_pos).

## Skip it when

- Parsing where throughput matters: the input is scanned twice, numbers go through strtoul/strtod, there is no SIMD, and no timing against RapidJSON exists. yyjson and simdjson have published speed wins.
- Round-tripping floating point: the printer formats doubles with "%1.10g" (at most 10 significant digits, so output is lossy), and NaN or Inf values print as null.
- Documents nested deeper than 32 levels (max_depth = 32 is hard-coded, so deeper input fails with QAJ4C_ERROR_DEPTH_OVERFLOW), or inputs over 4 GiB (internal offsets are uint32_t).
- Code that mutates or grows a parsed DOM: the parse result is const, and arrays and objects cannot be resized (calling set_object/set_array again wastes the old buffer space).
- MSVC toolchains, or projects that need upstream fixes: the library is abandoned since 2019 and open bug #8 (the Builder's deduplicate mode asserts instead of overwriting) has no response.

## How it is fast

It is built for low memory, not speed. The parse makes two passes. Pass one validates the input and counts nodes, long-string bytes and each container's member count, keeping the counts in the caller's buffer. Pass two writes the DOM into exactly that many bytes, so arrays and objects become plain C arrays with no per-node allocation and no slack. Each value is a 16-byte tagged cell on 64-bit (12 bytes on 32-bit), strings of up to 10 chars (6 on 32-bit) sit inside the cell, and in-situ mode points strings into the input instead of copying them. Objects with more than two members are sorted with qsort, so key lookup is a binary search.

## Compared with alternatives

jsmn is also allocation-free C, but it only returns tokens; qajson4c gives you a real DOM with array indexing and binary-search key lookup inside one precisely sized buffer. Against yyjson or simdjson, which have measured speed wins over RapidJSON, pick qajson4c only when a computable memory bound with no heap matters more than throughput and you accept unmaintained code.

## Integration

| | |
|---|---|
| **Form** | source-drop (qajson4c.c + qajson4c_internal.c and 3 headers); the bundled CMake also builds a static and a shared lib |
| **Dependencies** | none beyond the C standard library, whose calls are funneled through qajson_stdwrap.h so you can supply your own under NO_STDLIB |
| **Minimum toolchain** | C99; GCC or Clang only (structs use __attribute__((packed, aligned))); CMake 2.8.12 for the bundled build; MSVC not supported (Windows via MinGW) |
| **Platforms** | 32- and 64-bit targets where __WORDSIZE or _WIN32/_WIN64 is defined (otherwise #error). CI covered Linux x86-64 gcc (Travis) and Windows MinGW (AppVeyor). A 2019 branch commit mentions ARM test runs. |
| **Thread safety** | Not documented. Parser state lives on the stack and in the caller's buffer, so separate parses into separate buffers look reentrant from the code. The fatal-error handler is a process-wide global set by QAJ4C_register_fatal_error_function. |
| **Drop-in for the baseline** | no |

## Gotchas

- QAJ4C_parse is lenient by default: it accepts trailing commas, a leading '+', leading zeros and trailing garbage after the root value. Comments (/\* \*/ and //) are accepted even in strict mode. Pass QAJ4C_PARSE_OPTS_STRICT to QAJ4C_parse_opt for tighter validation.
- By default, parsed objects with more than 2 members are re-sorted (by key length, then bytes). Index iteration and printing then lose the input key order unless you pass QAJ4C_PARSE_OPTS_DONT_SORT_OBJECT_MEMBERS, and lookup with duplicate keys is undefined.
- A type-mismatched accessor (for example QAJ4C_get_int on a string) calls the fatal-error hook, which by default calls raise(SIGABRT). The header comment says it prints to stderr. Check with is_\* first, or register your own handler.
- The pointer returned by QAJ4C_parse_dynamic is the start of the realloc'd buffer, and you must free() it; only the nativejson-benchmark harness shows this, not the README or header. In-situ parsing and the \*_by_ref builder calls keep pointers into your strings, so those strings must outlive the DOM.

## Known shortcomings

- No speed measurement: the README claim is qualitative and about memory, and nativejson-benchmark's only published results (2016-09-09) predate qajson4c joining the suite, so it has no row there. 10 stars.
- Lossy and lenient: doubles print with at most 10 significant digits (NaN/Inf become null); the default parser accepts trailing commas, leading + and zeros, and trailing garbage; objects over 2 members are re-sorted so key order is lost. Depth capped at 32, no inputs over 4 GiB, GCC/Clang only, wrong-type access aborts. Abandoned since 2019.

## Caveats and trade-offs

No published measurement exists: nativejson-benchmark's sample results predate qajson4c and the README gives no figures. Claim is about memory footprint and allocation count, not speed. Default branch last commit 2019-03-22 (branch iterative_parsing 2019-11-01); abandoned.

No dynamic memory allocation required (buffer-based, caller-managed memory), aimed at embedded/memory-constrained targets; lower-level API than DOM-style libraries

## Maintenance

Abandoned: last master commit 2019-03-22 (iterative_parsing branch 2019-11-01), and nativejson-benchmark still points at the old USESystemEngineeringBV location (PR #122 unmerged). It is MIT-licensed, about 2.1k lines of C99 and easy to vendor, but GCC/Clang only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): reject; tier before verification B, tier now D.
- **Tier reason:** nativejson-benchmark's only published results (sample/, 'Update on: 2016-9-9', clang 7.0 on Corei7-4980HQ) predate qajson4c's addition to the suite (PR #78 merged 2017-05-05) and contain no qajson4c row. The qajson4c README has only a qualitative claim with no numbers, so no numbers exist for this project.
- **Verifier notes:** Checked nativejson-benchmark sample CSV/HTML (mac64 and mac32) and conformance files: zero qajson4c matches. A third-party mmJSON benchmark (project-gemmi/benchmarking-json) also excludes it. Metadata is correct: MIT, not a fork, 10 stars, last default-branch commit 2019-03-22, abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DeHecht/qajson4c>
  - <https://github.com/DeHecht/qajson4c/blob/master/LICENSE>
  - <https://github.com/miloyip/nativejson-benchmark>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/sample/performance_Corei7-4980HQ@2.80GHz_mac64_clang7.0.csv>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/sample/performance_Corei7-4980HQ@2.80GHz_mac64_clang7.0.html>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/sample/performance_Corei7-4980HQ@2.80GHz_mac32_clang7.0.html>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/sample/conformance.html>
  - <https://github.com/miloyip/nativejson-benchmark/pull/78>
  - <https://github.com/miloyip/nativejson-benchmark/pull/122>
  - <https://github.com/USESystemEngineeringBV/qajson4c>
  - <https://github.com/project-gemmi/benchmarking-json>
- **Sources the enricher read:**
  - <https://github.com/DeHecht/qajson4c>
  - <https://github.com/DeHecht/qajson4c/blob/master/src/qajson4c/qajson4c.h>
  - <https://github.com/DeHecht/qajson4c/blob/master/src/qajson4c/qajson4c.c>
  - <https://github.com/DeHecht/qajson4c/blob/master/src/qajson4c/qajson4c_internal.c>
  - <https://github.com/DeHecht/qajson4c/blob/master/src/qajson4c/qajson4c_internal.h>
  - <https://github.com/DeHecht/qajson4c/blob/master/src/qajson4c/qajson_stdwrap.h>
  - <https://github.com/DeHecht/qajson4c/blob/master/CMakeLists.txt>
  - <https://github.com/DeHecht/qajson4c/blob/master/src/CMakeLists.txt>
  - <https://github.com/DeHecht/qajson4c/blob/master/appveyor.yml>
  - <https://github.com/DeHecht/qajson4c/blob/master/.travis.yml>
  - <https://github.com/DeHecht/qajson4c/blob/master/src-test/unit_tests.cpp>
  - <https://github.com/DeHecht/qajson4c/issues/8>
  - <https://github.com/DeHecht/qajson4c/issues?q=is%3Aissue>
  - <https://github.com/DeHecht/qajson4c/commits/master>
  - <https://github.com/DeHecht/qajson4c/commits/iterative_parsing>
  - <https://github.com/DeHecht/qajson4c/tags>
  - <https://github.com/USESystemEngineeringBV/qajson4c>
  - <https://github.com/miloyip/nativejson-benchmark>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/src/tests/qajson4ctest.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/src/cjsonlibs/qajson4c_all.c>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/sample>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/sample/performance_Corei7-4980HQ@2.80GHz_mac64_clang7.0.csv>
  - <https://github.com/miloyip/nativejson-benchmark/pull/78>
  - <https://github.com/miloyip/nativejson-benchmark/pull/122>
  - <https://github.com/project-gemmi/benchmarking-json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/dehecht/qajson4c`) · [data/wave4/enrich/raw/github_com_dehecht_qajson4c.json](../../../data/wave4/enrich/raw/github_com_dehecht_qajson4c.json) (enrichment confidence 0.8)

</details>
