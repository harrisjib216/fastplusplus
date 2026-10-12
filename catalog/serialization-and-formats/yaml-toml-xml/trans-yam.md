# yam

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Zero-copy C11 YAML 1.2 event parser and emitter with an SSE4.2 scanner; parses 1.6-13x faster than libyaml.

| | |
|---|---|
| **Beats** | libyaml |
| **Claimed result** | 1.6-13x faster than libyaml 0.2.5 and libfyaml 0.9.6 across inputs: e.g. config files 206 MB/s vs libyaml 125 MB/s; travis.yml 501 MB/s vs libyaml 149 MB/s; literal block scalars 3091 MB/s vs libyaml 290 MB/s |
| **Workload** | Parses generated YAML/JSON shapes (block mappings/sequences, mixed block+flow+quoted, JSON, config files with comments/anchors) plus real files repeated to \~10MB (travis.yml, appveyor.yml, compile_commands.json) and scalar-heavy block-scalar text, via `make bench-compare`. |
| **Metric** | throughput |
| **Hardware** | Intel Core Ultra 7 155H, one core |
| **Compiler and flags** | GCC 16.2, -O2 |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/trans/yam) · [benchmark](https://github.com/trans/yam/blob/main/README.md) |

## Verdict

The author's make bench-compare harness parses the same \~10 MB inputs (generated block/mixed/JSON/config YAML, rapidyaml's real travis.yml, appveyor.yml and compile_commands.json files, and scalar-heavy text) into events with yam, libyaml 0.2.5 and libfyaml 0.9.6. It ran on one pinned core of an Intel Core Ultra 7 155H, with yam built by GCC 16.2 at -O2 and the other two linked as system libraries. yam measured 1.65x (anchored config) to 13.4x (multi-line double-quoted) over libyaml, e.g. 501 vs 149 MB/s on travis.yml. This is first-party and not independently reproduced.

## Use it when

- C or C++ code that walks YAML as an event stream (config loaders, CI and Kubernetes-style files, converters) and wants more throughput than libyaml's yaml_parser_parse.
- Inputs dominated by long scalars: literal/folded block scalars and multi-line quoted strings measured 7-13x faster than libyaml, and 2-8x faster than rapidyaml's event parser.
- JSON-like or compile_commands.json-style files that are already in memory (about 2.2 GB/s vs 226 MB/s for libyaml in the author's table).
- You need strict YAML 1.2 conformance (all 308 valid and 94 invalid YAML Test Suite cases pass) plus a round-trip-safe emitter, on x86-64 Linux or macOS.

## Skip it when

- You want a document tree or DOM. yam only produces events, so you would build the tree yourself; libfyaml or rapidyaml give you one.
- You need streaming input from a FILE\*, a callback or a socket, or UTF-16/UTF-32 input. yam parses one contiguous UTF-8 buffer that has to stay alive, and emitter output goes to an in-memory buffer too.
- The documents use anchors, tags, %TAG/%YAML directives, flow keys in block mappings, merge keys or alias resolution. Any of these makes the parser re-parse the whole stream in eager mode and buffer every event, so memory grows with the whole stream. The anchored 'config' benchmark shows the smallest gain (206 vs 125 MB/s, 1.65x).
- Structure-heavy input with short keys and values, if C++ is an option: rapidyaml's event parser was 1.3-1.8x faster than yam on the generated block, mixed and JSON inputs.
- You are risk-averse about maturity. The project was created in Feb 2026, has 0 stars and no external issues, and one maintainer. 1.0.0 is in the header and CHANGELOG, but the newest git tag is v0.3.1.

## How it is fast

The scanner looks for structural bytes 16 at a time with SSE4.2 PCMPESTRI range compares and SSE2 compare-and-movemask. The SSE4.2 or scalar version is chosen once through function pointers set in a load-time constructor. Plain and quoted scalars that have no escapes or line breaks come back as zero-copy slices of the input. Block scalars, and quoted scalars with escapes or line breaks, are copied into a bump-allocated arena a line or a run at a time, not byte by byte. The parser is an incremental state machine; to decide whether a flow collection is a key, it looks ahead with a SIMD bitmask over 64-byte windows and caches the answer for nested collections, which keeps it linear.

## Compared with alternatives

Pick yam over libyaml or libfyaml when you want a plain C event API and more throughput: 1.6-3.4x on structure-heavy YAML and up to 13x on long scalars, with the same full test-suite conformance as libfyaml. Pick rapidyaml or chyaml instead if you are in C++ and your input is mostly short keys and values or you want a tree; also consider yeptris if you target Apple Silicon, since yam's SIMD is x86-only.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (Makefile builds libyam.a and libyam.so.1 plus yam.pc; about 8 C files, easy to vendor) |
| **Dependencies** | none (libc only) |
| **Minimum toolchain** | C11 with GCC or Clang (uses __attribute__((constructor)), target("sse4.2") and __builtin_cpu_supports; POSIX headers); tested with GCC and Clang on Linux and macOS; MSVC/Windows not documented |
| **Platforms** | x86-64 uses SSE4.2 when the CPU has it, with a scalar fallback chosen at runtime, so no -march=native is needed. There is no NEON path, so aarch64 and other non-x86 targets run the scalar code. CI covers Linux and macOS. |
| **Thread safety** | not documented. From the source: all state is per parser/scanner/emitter/arena, schema presets are static const, and the only global is the SIMD function-pointer table, which is set once at load time. So separate parsers on separate threads look safe, but a single parser or arena is not synchronized. |
| **Drop-in for the baseline** | no |

## Gotchas

- The parser stops with YAM_ERR_LIMIT after 10,000 events by default. The README says that is roughly 100-200 KB of dense YAML, and the author's benchmark sets it to 0. Call yam_parser_set_max_events() for large files.
- An event pointer is valid only until the next yam_parse_next() call. The value/anchor/tag spans are not NUL-terminated and stay valid only while both the input buffer and the arena are alive.
- It is stricter than libyaml, which implements YAML 1.1. Tabs as indentation, implicit keys spanning lines and similar input are errors. Schemas are opt-in, so scalars carry no resolved tag unless you set one. There is one deliberate leniency: a closing ] } or quote may sit at any indentation.
- Eager mode (tags, anchors, merge or alias expansion) parses recursively at roughly 1 KB of stack per nesting level. If you raise max_depth or set it to 0 (default 256), deep input can overflow the stack.

## Known shortcomings

- Any tag, anchor, alias, merge key or directive makes the parser restart in eager mode and buffer every event, so memory grows with the stream; the anchored input is the worst case (1.65x over libyaml). Default limit of 10,000 events (about 100-200 KB) stops larger files unless raised. SIMD is x86-only, input must be one in-memory UTF-8 buffer, and there is no Windows/MSVC support. Single author, 0 stars, created 2026-02.

## Caveats and trade-offs

First-party benchmark from the author's own harness (bench/compare/run.sh), run on one machine and one core; not independently reproduced. libyaml/libfyaml are linked as system-installed libraries (-lyaml/-lfyaml), so their build flags are whatever the distro used. The real-file and scalar-heavy inputs come from rapidyaml's benchmark set and are not bundled; they are passed in through CASES. The C++ rapidyaml event parser is 1.3-1.8x faster than yam on the generated structure-heavy inputs (README's own table). 0 stars; repo created Feb 2026.

C11 event/token-stream API rather than a DOM by default (a separate document layer would need to be built on top); zero-copy string spans require the source buffer to stay alive for the parser's lifetime; brand-new project competing with long-established libyaml/libfyaml.

## Maintenance

Actively developed by a single author (last commit 2026-09-24, 1.0.0 with an ABI-stability promise declared in the CHANGELOG), fuzzed on every push and daily through ClusterFuzzLite, and MIT-licensed. It is small enough to vendor, but it has no track record of outside users yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** README Performance table (MB/s) comes from the public harness bench/compare/run.sh (Makefile target bench-compare, per-library drivers bench/compare/cmp_yam.c, cmp_libyaml.c, cmp_libfyaml.c, shared timing loop cmp_common.h). It runs yam against libyaml 0.2.5 and states compiler (GCC 16.2), flags (-O2) and CPU (Intel Core Ultra 7 155H, one core), so A holds.
- **Verifier notes:** All three quoted pairs match the README table exactly: config 206 vs 125, travis.yml 501 vs 149, literal block scalars 3091 vs 290. The README itself states the 1.6-13x range; the 13x is multi-line double-quoted, 3006 vs 224 MB/s. Metadata checks out: MIT, not archived, not a fork, 0 stars, last commit 2026-09-24. The only change is caveats, which now note that rapidyaml leads on the generated inputs.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/trans/yam>
  - <https://github.com/trans/yam/blob/main/README.md>
  - <https://github.com/trans/yam/blob/main/bench/compare/run.sh>
  - <https://github.com/trans/yam/blob/main/bench/compare/cmp_common.h>
  - <https://github.com/trans/yam/blob/main/bench/compare/cmp_libyaml.c>
  - <https://github.com/trans/yam/blob/main/bench/compare/cmp_yam.c>
  - <https://github.com/trans/yam/blob/main/Makefile>
- **Sources the enricher read:**
  - <https://github.com/trans/yam>
  - <https://github.com/trans/yam/blob/main/README.md>
  - <https://github.com/trans/yam/blob/main/include/yam/yam.h>
  - <https://github.com/trans/yam/blob/main/Makefile>
  - <https://github.com/trans/yam/blob/main/CHANGELOG.md>
  - <https://github.com/trans/yam/blob/main/src/yam_simd.c>
  - <https://github.com/trans/yam/blob/main/src/yam_simd.h>
  - <https://github.com/trans/yam/blob/main/src/yam_scanner.c>
  - <https://github.com/trans/yam/blob/main/src/yam_parser.c>
  - <https://github.com/trans/yam/blob/main/src/yam_arena.c>
  - <https://github.com/trans/yam/blob/main/src/yam_schema.c>
  - <https://github.com/trans/yam/blob/main/src/yam_internal.h>
  - <https://github.com/trans/yam/blob/main/bench/compare/run.sh>
  - <https://github.com/trans/yam/blob/main/bench/compare/cmp_common.h>
  - <https://github.com/trans/yam/blob/main/bench/compare/cmp_yam.c>
  - <https://github.com/trans/yam/blob/main/bench/compare/cmp_libyaml.c>
  - <https://github.com/trans/yam/blob/main/bench/compare/cmp_libfyaml.c>
  - <https://github.com/trans/yam/blob/main/bench/compare/gen_inputs.c>
  - <https://github.com/trans/yam/blob/main/bench/bench_gen.h>
  - <https://github.com/trans/yam/blob/main/.github/workflows/ci.yml>
  - <https://github.com/trans/yam/blob/main/docs/api/index.md>
  - <https://github.com/trans/yam/issues>
  - <https://github.com/trans/yam/pulls>
  - <https://github.com/trans/yam/releases>
  - <https://github.com/trans/yam/tags>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/trans/yam`) · [data/wave4/enrich/raw/github_com_trans_yam.json](../../../data/wave4/enrich/raw/github_com_trans_yam.json) (enrichment confidence 0.75)

</details>
