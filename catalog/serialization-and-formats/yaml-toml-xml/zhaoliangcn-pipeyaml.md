# PipeYAML

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++17 YAML parser/emitter with a yaml-cpp-style API; author reports \~10x faster Load, \~5x faster Dump on sub-1 KB configs.

| | |
|---|---|
| **Beats** | yaml-cpp |
| **Claimed result** | Load: 9.4x-10.5x faster (e.g. 14.3us vs yaml-cpp's 150us on a medium document); Dump: 5.0x-5.3x faster; Roundtrip (load-&gt;modify-&gt;dump): 7.5x faster; cached int/double conversion: 34x/54x faster |
| **Workload** | Load/Dump/Roundtrip/Build-sequence/Build-map microbenchmarks (Google Benchmark) on medium (\~75 line), complex (anchors/aliases), and deeply-nested YAML documents, plus cached scalar type conversion, comparing against yaml-cpp 0.8 |
| **Metric** | latency |
| **Hardware** | "Intel Xeon" (no specific model number given) |
| **Compiler and flags** | GCC 9.4, C++17, Google Benchmark (README). Optimization flags are not stated. CMakeLists.txt sets no default CMAKE_BUILD_TYPE, and the README build is plain 'cmake ..'. yaml-cpp 0.8 is linked from a prebuilt YAML_CPP_DIR whose build type is also unstated. |
| **Adoption** | 0 stars; very new (created July 2026) |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/zhaoliangcn/PipeYAML) · [benchmark](https://github.com/zhaoliangcn/PipeYAML#performance-vs-yaml-cpp-08) |

## Verdict

The numbers come from the author's Google Benchmark suite: two separate executables with identical benchmark bodies and inputs, run on an unspecified 'Intel Xeon' with GCC 9.4 in C++17 mode and unstated optimization flags for both libraries. Loading a 747-byte, 55-line config takes 14.3 us against yaml-cpp 0.8's 150 us (10.5x). The 368-byte nested and 911-byte anchor/merge-key documents load 9.4-9.7x faster, Dump is 5.0-5.3x faster, and load-modify-dump is 7.5x faster. The README calls the config '\~75 lines'. The 34x/54x int/double figures time repeated as&lt;T&gt;() calls on one node, which PipeYAML answers from its cache, so they do not measure parsing. All results date from 2026-07-07 and were not re-run after the correctness fixes of 07-12 and 09-08.

## Use it when

- Your yaml-cpp code only uses YAML::Load/LoadFile, operator[], as&lt;T&gt;() and Dump, and parse or reload latency on small config files matters (short-lived CLI tools, services that re-read config often).
- Your inputs are small block-style configs you control, like the 368-911 byte documents in the published numbers. They use plain key: value pairs, nested maps, block sequences, quoted strings, simple anchors/aliases and |/&gt; block scalars.
- Hot code reads the same int, double or bool field many times through as&lt;T&gt;(). After the first call PipeYAML returns a cached value: about 10 ns in the author's run, against 357-574 ns for yaml-cpp, which parses the text again on every call.
- You want a small MIT codebase to vendor (about 3.1k lines in 7 headers and 6 .cpp files) and are prepared to fix parser bugs yourself.

## Skip it when

- YAML written by other tools or people (Kubernetes manifests, CI files, CloudFormation). Per the scanner source, an unquoted block value that contains , [ ] { } or ` is split at that character, and Load then usually throws (e.g. `msg: Hello, world`). Multi-line plain scalars also throw. Tags such as !!str or !Ref stay in the scalar text, `&lt;&lt;` merge keys are not expanded, '?' explicit keys are silently dropped, and UTF-16/32 input is rejected.
- Untrusted input that you later Dump. The parser shares one node for every alias, but the emitter writes each alias out in full and never emits &/\*. A billion-laughs document therefore parses cheaply, and its output then grows exponentially.
- Round-trip or data-exchange output. Anchors, comments and quoting style are lost. A quoted numeric string like "123" is re-emitted unquoted. A string with a comma in the middle is also written unquoted, so PipeYAML cannot load its own output.
- Large documents or wide maps. Key lookup and operator[] insertion both scan a vector of pairs linearly. Load copies the input and tokenizes the whole stream before parsing, and no published benchmark goes above about 1 KB of input.
- Anything production-critical. The code is AI-written, the repo was created 2026-07-03, it has 0 stars and no releases or tags, nothing has been fuzzed, and CI has failed on main since 2026-07-12. The published speedups were measured before the July and September fixes for infinite loops, comment truncation and swallowed sibling keys, and the author notes one flow-mapping defect that is still open.

## How it is fast

Load copies the whole input into one NUL-terminated std::string. The scanner reads it in string_view batches and dispatches on the first character with a single switch. It scans every token into a vector-plus-head-index queue, and a recursive-descent parser then builds a shared_ptr&lt;node_data&gt; tree in which each map is an insertion-ordered vector of key/value pairs. The emitter appends directly to a std::string instead of an ostringstream (the design doc credits this with a 41% cut in Dump time). Integers are decoded with std::from_chars, and each node caches its int/double/bool value after the first as&lt;T&gt;() call, which is where the 34x/54x conversion figures come from. The library has no SIMD and no arena allocator. Part of the gap to yaml-cpp probably comes from doing less work: the scanner ignores tags, drops '?' explicit keys, never expands merge keys and does not apply flow-context rules to plain scalars.

## Compared with alternatives

Pick it only when keeping yaml-cpp-style call sites (YAML::Load, Node, operator[], as&lt;T&gt;) matters more than spec coverage and maturity. fkYAML (header-only C++11 with its own fkyaml::node API, \~7.5x yaml-cpp on real files such as ubuntu.yml) and rapidyaml (C++11 with its own Tree API, claims \~30x on parse) are faster or better proven on real inputs. PipeYAML's own numbers work out to roughly 50-80 MB/s on sub-1 KB documents, which is fkYAML's range rather than rapidyaml's, and libfyaml is a C library at \~3x.

## Integration

| | |
|---|---|
| **Form** | static lib: CMake target pipeyaml, exported as PipeYAML::pipeyaml. The README's 'header-only style' only means there is a single include; 6 .cpp files still have to be compiled, and they are easy to source-drop. |
| **Dependencies** | None for the library. When the top-level CMakeLists is configured, FetchContent clones tinyTest from GitHub (branch main) unless TINYTEST_DIR is set, even with tests turned off. Google Benchmark and a prebuilt yaml-cpp are needed only for the benchmarks. |
| **Minimum toolchain** | C++17 (uses std::from_chars, std::optional and std::filesystem) and CMake 3.14. The README claims GCC 7+, Clang 5+ and MSVC 2017+. The only evidence is GCC 9.4 for the benchmarks and g++/clang++ on ubuntu-latest in CI, where the Clang build of the unit tests currently fails. |
| **Platforms** | The library is portable C++ with no intrinsics or OS-specific calls, so in principle it runs anywhere. In practice only Linux is exercised (CI on ubuntu-latest). The benchmark targets link pthread and rt, which makes them Linux-only. macOS and Windows appear only as goals in the design doc. |
| **Thread safety** | Not documented. as&lt;int&gt;(), as&lt;double&gt;() and as&lt;bool&gt;() are const but write a mutable per-node cache, so concurrent reads of one Node from several threads are a data race. Each Load() keeps its stream, scanner, parser and anchor table local to the call, and I found no mutable globals on the parse path. |
| **Drop-in for the baseline** | partial: it keeps yaml-cpp's YAML namespace, Load/LoadFile/LoadAll/Dump, Node, operator[], as&lt;T&gt;(), push_back and the Emitter manipulators. The differences: type queries are snake_case (is_map(), scalar(), type()); there are no begin()/end() iterators; convert&lt;T&gt;::encode is bool encode(const T&, Node&); the Flow/Block/quoting manipulators are accepted but ignored; and several valid YAML constructs are rejected or mis-parsed (see when_not_to_use). |

## Gotchas

- `node[0]` with a literal 0 is an ambiguous call, because 0 also converts to std::string through const char\*. Clang rejects it, which is why CI is red. Write node[std::size_t(0)] as the README does; an int or size_t variable as the index is fine.
- PipeYAML uses namespace YAML with the same class and function names as yaml-cpp, so the two cannot be linked into one binary. Its own comparison benchmark builds two separate executables. Migration is all-or-nothing per binary.
- `node = 3.14159265358979` stores "3.141593" and `node = 1e-9` stores "0.000000", because convert&lt;double&gt;::encode uses std::to_string. Emitter &lt;&lt; double uses 15 significant digits instead. Format doubles yourself before assigning them if precision matters.
- Node::operator== on two maps compares only their sizes. as&lt;std::vector&lt;T&gt;&gt;() links only for bool, int, double and std::string elements (explicit instantiations), and there are no std::map converters. Load() throws ParserException on empty or comment-only input. With no iterators, the only way to walk unknown keys is node.get_data()-&gt;map().

## Known shortcomings

- Correctness gaps found by reading the code: unquoted values containing , [ ] { } are split (e.g. `msg: Hello, world` likely fails to load), multi-line plain scalars throw, merge keys are not expanded, and dumped strings with commas are not quoted, so it cannot reload its own output. It shares the YAML namespace with yaml-cpp (cannot link both), and CI has failed on main since 2026-07-12. Benchmark inputs are tiny (368-911 bytes).

## Caveats and trade-offs

The repo description says the code was written by AI ('本项目代码由AI编写'), and commits are co-authored by an AI tool. The benchmark table was added in commit f1904fc (2026-07-07) and never re-run. Later commits fixed major correctness bugs: flow-parsing infinite loops (07-12), and on 09-08 comments that crashed or truncated parsing, sibling keys swallowed into nested maps, and missing block-scalar support. One known flow-map defect remains. Inputs are tiny (4.5-15 µs parses of a \~75-line config). The 34x/54x 'cached' conversions measure PipeYAML caching repeated as&lt;T&gt;() calls on the same node, which yaml-cpp does not do; they are not parse speedups, and 54x with unstated flags is above the &gt;50x cap. The CPU is the generic 'Intel Xeon' with no model. 0 stars, created 2026-07-03, with no external review or adoption yet.

Type-conversion caching (int/double/bool cached on first access, O(1) subsequent reads) trades a bit of memory/complexity for large gains on repeated field access; API intentionally mirrors yaml-cpp's Node interface for easy migration

## Maintenance

Active but brand-new: a single-author, AI-written project created 2026-07-03, last commit 2026-09-08, 0 stars, no releases, CI failing on main. It is MIT-licensed and about 3.1k lines, so it can be copied, but treat it as code you would have to own and fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party Google Benchmark code is public (benchmarks/bench_parse.cpp and its mirror benchmarks/bench_yamlcpp.cpp, both using the same inputs from bench_data.h), and GCC 9.4 is stated. Optimization flags are not stated, and the CPU is only 'Intel Xeon' with no model, so it is not A. There is no paper or third-party suite, so it is C.
- **Verifier notes:** Every claimed_speedup figure matches the README table exactly, and the benchmark code is symmetric for PipeYAML and yaml-cpp. The tier stays C. I added caveats: the numbers predate substantial correctness fixes, and the build flags for both sides are unknown.
- **Fields the verifier corrected:** `compiler_and_flags`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/zhaoliangcn/PipeYAML#performance-vs-yaml-cpp-08>
  - <https://github.com/zhaoliangcn/PipeYAML>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/CMakeLists.txt>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/.github/workflows/ci.yml>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/benchmarks/bench_parse.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/benchmarks/bench_yamlcpp.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/benchmarks/bench_data.h>
- **Sources the enricher read:**
  - <https://github.com/zhaoliangcn/PipeYAML>
  - <https://github.com/zhaoliangcn/PipeYAML#performance-vs-yaml-cpp-08>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/README.md>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/CMakeLists.txt>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/.github/workflows/ci.yml>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/PipeYAML%20%E6%9E%B6%E6%9E%84%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3.md>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/include/pipeyaml/pipeyaml.h>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/include/pipeyaml/node.h>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/include/pipeyaml/parser.h>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/include/pipeyaml/scanner.h>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/include/pipeyaml/stream.h>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/include/pipeyaml/emitter.h>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/include/pipeyaml/exception.h>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/src/convert.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/src/node.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/src/parser.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/src/scanner.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/src/stream.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/src/emitter.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/benchmarks/bench_parse.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/benchmarks/bench_yamlcpp.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/benchmarks/bench_data.h>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/tests/unit/test_node.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/tests/unit/test_parser.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/blob/main/tests/integration/test_roundtrip.cpp>
  - <https://github.com/zhaoliangcn/PipeYAML/commits/main>
  - <https://github.com/zhaoliangcn/PipeYAML/commit/522a664>
  - <https://github.com/zhaoliangcn/PipeYAML/issues>
  - <https://github.com/zhaoliangcn/PipeYAML/actions>
  - <https://github.com/zhaoliangcn/PipeYAML/actions/runs/34185462773>
  - <https://github.com/fktn-k/fkYAML>
  - <https://github.com/biojppm/rapidyaml>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/zhaoliangcn/pipeyaml`) · [data/wave4/enrich/raw/github_com_zhaoliangcn_pipeyaml.json](../../../data/wave4/enrich/raw/github_com_zhaoliangcn_pipeyaml.json) (enrichment confidence 0.78)

</details>
