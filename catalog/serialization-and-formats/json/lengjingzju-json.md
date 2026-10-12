# LJSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Pure-C JSON5 DOM/SAX library; its arena/in-situ modes parse up to 2.5x and print \~3x faster than RapidJSON.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | README headline figures are best-case single files ('最快可达' = 'up to' in README_zh-cn): 'parses 131% faster and prints 147% faster than RapidJSON' on Cortex-A53 (twitter.jsonx10: RapidJSON parse 178 vs LJSON reuse mode 77 ms, unformatted print 109 vs 44 ms); 'parses 75% faster and prints 133% faster' on i7-10700 (twitter.jsonx100 parse 138 vs 79 ms; canada.jsonx100 unformatted print 844 vs 362 ms). On i7-1260P the README says 'parses 166% faster and prints 215% faster' (without file I/O), but the published screenshot's best parse ratio is 1000xtwitter RapidJSON 864 vs LJSON mode 3 345 ms (\~2.5x, 150% faster); the print figure matches (formatted 759 vs 241 ms, \~3.15x). On canada.json the parse gain is small: 64 vs 44 ms (A53), 477 vs 444 ms (i7-10700, x100), 333 vs 297 ms (i7-1260P, x100) (derived from page data) |
| **Workload** | Single-shot, millisecond-resolution DOM parse and formatted/unformatted print timings on nativejson-benchmark files (canada, twitter, citm_catalog) and author-built concatenations (twitter x10/x100/x1000, canada x100, citm x1000). The best of LJSON's 7 modes (reuse and fast arena modes) is compared with RapidJSON's default Document::Parse plus Writer/PrettyWriter, and with cJSON and yyjson |
| **Metric** | throughput |
| **Hardware** | ARM64 dev board / ARM CortexA53 (Linux-5.15); Intel i7-10700 (Ubuntu 18.04, VirtualBox); Intel i7-1260P (Debian 13, VMWare) |
| **Compiler and flags** | gcc/g++ -O2 with default options (README Note 1 and build commands; ljson is also built with -ffunction-sections -fdata-sections). gcc 14.2.0 (Debian 14.2.0-19) is shown only in the i7-1260P screenshot. Compiler versions for the Cortex-A53 and i7-10700 runs are not stated |
| **Adoption** | 28 stars |
| **Last commit** | 2026-07-25 |
| **Links** | [repository](https://github.com/lengjingzju/json) · [benchmark](https://github.com/lengjingzju/json/blob/master/README.md) |

## Verdict

These are author-run, single-shot millisecond timings at gcc -O2 on an i7-1260P under Debian 13 in VMware (gcc 14.2, LJSON v5.0.2). On 1000x-concatenated twitter.json (603 MB), LJSON's arena/reuse modes parsed in 345 ms against RapidJSON Document::Parse at 864 ms (\~2.5x) and printed formatted/compact in 241/203 ms against 759/649 ms (\~3.1-3.2x); on 1000x citm_catalog parsing took 876 vs 1490 ms (\~1.7x), and on 100x canada.json only 297 vs 333 ms (\~1.1x). RapidJSON ran with default options (no SSE4.2, not in-situ), the README's '166% faster parse' is not supported by the screenshot, and the older Cortex-A53 and i7-10700 runs show similar patterns but give no compiler version.

## Use it when

- C or embedded services that parse and emit many small-to-medium messages in a loop. You keep one json_mem_t arena, a json_items_t and a print buffer, and call pjson_memory_refresh after each message; this is the README's 'zero-heap-allocation' pattern.
- Workloads heavy on serialization: in the author's i7-1260P run, printing beat RapidJSON's Writer/PrettyWriter by about 1.9-3.2x on all three test files, including number-heavy canada.json (2.3-2.75x).
- String- and object-heavy documents (twitter/citm shapes) where you want an editable DOM: parse was about 1.7-2.5x RapidJSON in reuse/arena mode, and in-situ strings stay editable.
- Reformatting or minifying multi-GB files on bounded memory. The SAX + file-streaming modes parse while reading and print while writing; the author claims KB-level memory for 1 GB files, but that figure is not benchmarked.
- Targets with no SIMD, or where SIMD is unwanted (ARM Cortex-A53 boards, MSVC builds): the code is scalar C, and the author's Cortex-A53 table still shows gains over RapidJSON.

## Skip it when

- If you will only call json_parse_str/json_parse_file (the malloc DOM). In the author's own i7-1260P screenshot, mode 1 parsed slower than RapidJSON on every file (1108 vs 864, 1972 vs 1490 and 527 vs 333 ms), and a user in issue #2 found it roughly 30% slower than yyjson.
- Number-dominated input: parsing canada.json gained only about 1.1x over RapidJSON (297 vs 333 ms at 100x on the i7-1260P, 477 vs 444 ms on the i7-10700).
- When doubles must round-trip exactly or output must be IEEE-exact. The default ldouble printer is documented as not fully IEEE-754 compliant (the README says 17-digit precision, the intro note says 16). Build with DTOA=3 (dragonbox) or DTOA=2 (grisu2) to use those printers instead, at the cost of speed.
- When you need a strict RFC 8259 validator out of the box. By default the parser accepts trailing commas, raw control characters in strings, hex numbers, leading '+'/'.' numbers, NaN/Infinity and top-level scalars, and it rejects empty keys (""). The README reports 100% nativejson-benchmark conformance only after recompiling with different macro settings.
- When you need a mature project: one maintainer, 28 stars, 0 forks, and no CI, conformance or fuzz suite in the repo; the only test files are benchmark drivers. For raw read-only parse speed, the author concedes yyjson's immutable mode is slightly faster in some cases.

## How it is fast

The speed comes from avoiding allocations and copies, not from SIMD. The fast modes bump-allocate 32-byte nodes, keys and strings from three separate arenas (pjson_memory_alloc), which pjson_memory_refresh resets for reuse. Reuse mode unescapes strings in place in the caller's buffer instead of copying them, much like RapidJSON's in-situ parsing, which the benchmark did not turn on. The parser is an iterative goto state machine over a byte-at-a-time scanner, with a 256-entry character-class table, likely/unlikely hints and manual loop unrolling (off on MSVC). Each string caches its length and an 'escaped' bit so the printer can skip strlen and escape scanning, and doubles are printed by the author's ldouble shortest-digits algorithm (128-bit multiply, lookup tables, division by reciprocal multiplication) instead of sprintf.

## Compared with alternatives

Against zzzJSON, the other catalogued C-level RapidJSON beater (about 1.3-1.55x), pick LJSON when you need an editable DOM plus SAX, file streaming or JSON5 in plain C and can use its arena modes. Its best-mode gains over RapidJSON are larger on string-heavy documents (1.7-2.5x parse, 1.9-3.2x print) but small on canada.json. Jsonifier's catalogued results are against simdjson on tiny-value tests, and the Go/Rust siblings (Sonic, go-json, jsoniter, easyjson, jiter, simd-json) are not options for C code.

## Integration

| | |
|---|---|
| **Form** | source-drop (json.c + jnum.c + json.h/jnum.h); the Makefile also builds libljson.a and libljson.so |
| **Dependencies** | none beyond libc (the Makefile links -lm) |
| **Minimum toolchain** | A C11 compiler: in C mode json.h uses _Generic unconditionally, and C++ callers get overloads under extern "C". GCC/Clang enable __int128 and the unrolled paths. On Windows there is a Visual Studio 2022 project. The only compiler version stated for the benchmarks is gcc 14.2 at -O2. |
| **Platforms** | Any; the code is scalar with no ISA requirements. The benchmarks ran on x86-64 Linux and ARM64 Cortex-A53 Linux, and Windows is covered by a Visual Studio 2022 project and MinGW branches in json.c. |
| **Thread safety** | Not documented. Parse state is per call or in caller-owned json_mem_t/json_items_t, and the only static shared between calls is a sentinel memory manager that the code compares against. So one arena per thread is the implied model; a DOM or arena shared across threads needs external locking. |
| **Drop-in for the baseline** | false: it is a C API in the style of cJSON, not RapidJSON's C++ Document/Writer templates, and you must adopt its arena and ownership rules to get the speedup |

## Gotchas

- Reuse mode (mode 3, zero-heap) writes into your input buffer: it unescapes strings and NUL-terminates them in place. The buffer must be writable, NUL-terminated (the scanner stops on '\0') and alive for as long as the DOM is.
- In arena modes, individual nodes cannot be freed; detached or replaced nodes stay in the pool until pjson_memory_refresh or pjson_memory_free. A parse error calls pjson_memory_free on the whole pool, which also destroys any other DOM stored in it.
- json_get_object_item and json_get_array_item walk a singly linked child list (strcmp per key). For large objects, call json_get_items, which builds a hash-sorted array for O(log n) lookup and grows by 16 entries per realloc. String and key lengths are stored in a 26-bit field, which caps them at 64 MiB; the only explicit length check is for binary values.
- Behavior is set by macros inside json.c. JSON_ERROR_PRINT_ENABLE is hard-coded to 1, so parse errors are printf'd to stdout and a -D flag cannot turn them off (issue #4). The README's Parse Config list shows SKIP_COMMENT and SPECIAL_QUOTES set to 1, but both default to 0 in the source. v5's 32-byte object layout is not compatible with v3.x.

## Known shortcomings

- The speedup comes only from the arena modes (2 and 3): in the author's own i7-1260P screenshot the default malloc mode (json_parse_str) parses slower than RapidJSON on every file. Defaults are lenient (trailing commas, NaN/Infinity, raw control characters) rather than strict JSON.

## Caveats and trade-offs

First-party benchmark run by the sole author on three of their own machines, two of them VMs, and not independently reproduced. Headline percentages are best-case files with LJSON's best arena/reuse mode. The Chinese README says 'up to', but the English README drops it. The i7-1260P parse figure (166%) could not be reproduced from its screenshot, where the best visible figure is \~150%. Timings are single runs at ms resolution. RapidJSON is built with default options (no SSE4.2/NEON, not in-situ). The 'with file reading and writing' label on the A53/i7-10700 claims does not fit the matching rows, which exclude file I/O. The author says numbers shift between releases

cJSON-inspired C API; DOM/SAX dual mode with memory-pool reuse and zero-heap-allocation mode; custom ldouble float&lt;-&gt;string codec is not fully IEEE-754 compliant (17-digit precision only) in exchange for speed

## Maintenance

Actively maintained by a single author: latest tag v5.0.3, last commit 2026-07-25, and 4 open issues, including #4 asking for configurable stdout error logging. It is MIT-licensed and small enough to vendor (two .c files), but v5 broke compatibility with v3.x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** Tier A applies only to the i7-1260P run. Its screenshot shows gcc (Debian 14.2.0-19) 14.2.0. The README states -O2 with default options and gives the CPU model. The benchmark code is public: json_test.c (LJSON modes 1-7) and benchmark/rapidjson_test.c, run by the README's test script. The ARM Cortex-A53 and i7-10700 runs give no compiler version.
- **Verifier notes:** Downgraded because the claim is overstated, not because of the tier. The quotes are verbatim from the English README, but they are best-case 'up to' figures, and the i7-1260P parse figure is not supported by the chart. The corrected claim uses the screenshot values. Metadata checks out: MIT, 28 stars, last commit 2026-07-25, active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lengjingzju/json/blob/master/README.md>
  - <https://github.com/lengjingzju/json>
  - <https://github.com/lengjingzju/json/blob/master/README_zh-cn.md>
  - <https://github.com/lengjingzju/json/blob/master/benchmark/rapidjson_test.c>
  - <https://github.com/lengjingzju/json/blob/master/benchmark/benchmark.sh>
  - <https://github.com/lengjingzju/json/blob/master/json_test.c>
  - <https://github.com/lengjingzju/json/blob/master/image/test_for_aarch64.png>
  - <https://github.com/lengjingzju/json/blob/master/image/test_for_x86_64.png>
  - <https://github.com/lengjingzju/json/blob/master/image/test_for_x86_64-2.png>
  - <https://github.com/lengjingzju/json/commit/83d1a016>
- **Sources the enricher read:**
  - <https://github.com/lengjingzju/json>
  - <https://github.com/lengjingzju/json/blob/master/README.md>
  - <https://github.com/lengjingzju/json/blob/master/README_zh-cn.md>
  - <https://github.com/lengjingzju/json/blob/master/notes/introduction.md>
  - <https://github.com/lengjingzju/json/blob/master/notes/optimization.md>
  - <https://github.com/lengjingzju/json/blob/master/notes/cmp_yyjson.md>
  - <https://github.com/lengjingzju/json/blob/master/json.h>
  - <https://github.com/lengjingzju/json/blob/master/json.c>
  - <https://github.com/lengjingzju/json/blob/master/jnum.h>
  - <https://github.com/lengjingzju/json/blob/master/jnum.c>
  - <https://github.com/lengjingzju/json/blob/master/json_test.c>
  - <https://github.com/lengjingzju/json/blob/master/Makefile>
  - <https://github.com/lengjingzju/json/blob/master/pcfiles/ljson.pc>
  - <https://github.com/lengjingzju/json/blob/master/benchmark/rapidjson_test.c>
  - <https://github.com/lengjingzju/json/blob/master/image/test_for_aarch64.png>
  - <https://github.com/lengjingzju/json/blob/master/image/test_for_x86_64.png>
  - <https://github.com/lengjingzju/json/blob/master/image/test_for_x86_64-2.png>
  - <https://github.com/lengjingzju/json/issues>
  - <https://github.com/lengjingzju/json/issues/2>
  - <https://github.com/lengjingzju/json/issues/3>
  - <https://github.com/lengjingzju/json/issues/4>
  - <https://github.com/lengjingzju/json/tags>
  - <https://github.com/lengjingzju/json/commits/master>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/lengjingzju/json`) · [data/wave4/enrich/raw/github_com_lengjingzju_json.json](../../../data/wave4/enrich/raw/github_com_lengjingzju_json.json) (enrichment confidence 0.8)

</details>
