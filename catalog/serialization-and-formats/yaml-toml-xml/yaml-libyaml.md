# LibYAML

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Portable C89 YAML 1.1 parser/emitter (the engine under PyYAML's C loaders); about 6-7x yaml-cpp's YAML::Load throughput.

| | |
|---|---|
| **Beats** | yaml-cpp |
| **Claimed result** | travis.yml parse: libyaml_arena 86.79 MB/s vs yamlcpp_arena 11.71 MB/s, shown as 7.41x on the page, CPU time per parse 0.05 ms vs 0.35 ms; compile_commands.json parse (rapidyaml README table): libyaml_arena 135.06 MB/s vs yamlcpp_arena 22.53 MB/s, 6.00x. |
| **Workload** | Parse of a small CI file (travis.yml, about 4 KB) into an in-memory tree, comparing libyaml events fed into a rapidyaml tree (LibyamlParser) with YAML::Load into a yaml-cpp Node; also compile_commands.json parsed as YAML. |
| **Metric** | throughput |
| **Hardware** | 20 logical CPUs at 4279 MHz (model name not stated), CPU scaling and ASLR disabled, Linux, run dated 2026-07-07 (results dir 0.16.0-pre). |
| **Compiler and flags** | g++ 16.1, CMake Release build, C++17, per the build directory name linux-x86_64-gxx16.1-Release-17 in ryml-bm-parse-travis.md; exact flags not stated. Google Benchmark v1.9.5, library_build_type release. libyaml is fetched from its master branch (shallow) and yaml-cpp is pinned to commit 587b24e2eedea1afa21d79419008ca5f7bda3bf4 in bm/CMakeLists.txt. Benchmark source bm/bm_parse.cpp in https://github.com/biojppm/rapidyaml. |
| **Adoption** | 1.2k stars |
| **Last commit** | 2026-08-21 |
| **Links** | [repository](https://github.com/yaml/libyaml) · [benchmark](https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.txt) |

## Verdict

In rapidyaml's own parse suite (bm/bm_parse.cpp, Google Benchmark v1.9.5, g++ 16.1 Release C++17 per the build-directory name, 20 logical CPUs at 4279 MHz whose 1 MiB L2 and 19.25 MiB L3 fit a 10-core part, model not named, scaling and ASLR off, one repetition on 2026-07-07), libyaml master events fed into a ryml tree parsed the 4067-byte travis.yml at 86.79 MB/s (0.047 ms). yaml-cpp's YAML::Load (2019 commit 587b24e2) reached 11.71 MB/s (0.347 ms), 7.41x slower; the README's compile_commands.json row shows 135.06 vs 22.53 MB/s (6.00x).

## Use it when

- C or C++ code that needs a YAML parser and emitter every Linux distribution already packages, with a stable C ABI (libtool-versioned shared library) and no dependencies beyond libc.
- Hot config-loading paths currently using yaml-cpp's YAML::Load, where you can consume events or build your own light tree: 86.79 vs 11.71 MB/s on a 4 KB CI file in rapidyaml's suite.
- Streaming large or multi-document input through the event API (yaml_parser_parse) without building a tree; memory stays at the fixed reader buffers plus the current event.
- When parse results must match PyYAML's C loaders or other language bindings that wrap libyaml.
- Generating YAML from C with the event-level emitter or yaml_emitter_dump.

## Skip it when

- Peak parse throughput: rapidyaml's ryml_yaml_\* rows parse the same travis.yml at 286.67-346.22 MB/s against libyaml's 86.79 MB/s (3.3-4.0x, derived from page data), and catalogued siblings yam and yeptris claim 1.6-13x and 2.2-4.1x over libyaml.
- You want a typed, queryable DOM (node["key"].as&lt;int&gt;()): libyaml returns string scalars with style and tag only and does no type resolution.
- Strict YAML 1.2 behaviour: the scanner follows the 1.1 grammar (since 0.2.3 it accepts %YAML 1.2 directives); open issue #351 (GLD Serializer Benchmark) reports spec-compliance misses in 0.2.5; libfyaml targets 1.2.
- Untrusted, deeply nested input on the 0.2.5 release that distributions ship: nesting limits exist only on master and in 0.2.6-rc.1, and issue #251 (the loader cycles on 1,048,576 '{' characters) is still open.
- You need a custom allocator or arena: yaml_malloc/yaml_realloc/yaml_free call malloc/realloc/free directly (feature request #178 open since 2020).

## How it is fast

It is a hand-written two-stage pipeline: a scanner with a token queue, a 'simple key' lookahead and an indentation stack for block collections, feeding an LL(1) recursive-descent parser written as an explicit state machine that emits events one at a time. Input passes through a 16 KB raw buffer that is decoded and validated into a 48 KB UTF-8 buffer, and nothing is materialised unless you call the loader. So the cost is one pass, a character-by-character copy of each scalar into a growable string and one malloc per scalar, anchor or tag. There is no SIMD and no zero-copy path. That copying is why in-place parsers such as rapidyaml are 3-4x faster than libyaml on the same file, while libyaml still beats yaml-cpp's DOM-building YAML::Load by about 6-7x.

## Compared with alternatives

Pick libyaml over rapidyaml, fkYAML or libfyaml when you want a plain-C dependency that every distribution already ships and whose behaviour matches PyYAML and the other libyaml bindings. Pick rapidyaml (3.3-4.0x faster on the same file), yam or yeptris when throughput matters, and libfyaml when you need YAML 1.2 with a C document API.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (autotools or CMake build; packaged as libyaml in most distributions) |
| **Dependencies** | none (libc only) |
| **Minimum toolchain** | C89 compiler; CMake 3.10+ on current master, or autoconf/libtool/make (./bootstrap) for a git checkout |
| **Platforms** | any: portable C with no SIMD or architecture-specific code; Linux, macOS and Windows (CMake/MSVC, YAML_DECLARE_STATIC for static builds) |
| **Thread safety** | Not documented. Parser and emitter state lives in per-object structs, so use one yaml_parser_t per thread; the exception is the master-only nesting limit, a process-wide plain int (MAX_NESTING_LEVEL, default 1000) changed by yaml_set_max_nest_level without synchronisation. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (output fidelity, not speed): rapidyaml's LibyamlParser wrapper (bm/libyaml.hpp) discards libyaml's decoded scalar and stores the raw source slice m_input.str + start_mark.index instead. libyaml's mark.index counts characters, not bytes (SKIP/READ do index++ while advancing the pointer by the UTF-8 width), so on any non-ASCII input the slices are shifted. Quoted, escaped and block scalars are stored undecoded, and aliases are a no-op case. travis.yml is pure ASCII (4067 bytes, no anchors), and the timed loop still includes libyaml's full scan plus its per-scalar malloc'd copies, so the headline row is not inflated. It does measure libyaml events plus a cheap borrowed-string ryml tree, not libyaml's own yaml_parser_load DOM, for which no number exists.
- Unequal versions and a single run: libyaml is cloned from master at build time (post-0.2.5 nesting-limit commits), while yaml-cpp is pinned to commit 587b24e2 of 2019-11-30, between 0.6.3 and 0.7.0, so it misses later yaml-cpp releases. Each row is one Google Benchmark repetition (14930 vs 2024 iterations), and the result JSON names the binary ryml-bm-parse-0.15.2.
- A parser takes its input only once: yaml_parser_set_input_string/_file/set_input assert(!parser-&gt;read_handler), so you must call yaml_parser_delete and yaml_parser_initialize per document stream. Under NDEBUG the assert is compiled out and the misuse goes unchecked. Do not mix yaml_parser_load with yaml_parser_scan/yaml_parser_parse on one parser.
- Security record: past fuzzing found heap overflows and stack overflows, mostly in the emitter, now closed. Issues for CVE-2024-35325/35326/35328/35329 are still open; the maintainer disputes 35326/35328/35329 as API misuse (structs not initialised with the library's init functions).

## Known shortcomings

- Tier B on the rapidyaml suite (86.79 vs yaml-cpp 11.71 MB/s, 7.41x, on travis.yml; 135.06 vs 22.53 MB/s, 6.00x, on compile_commands.json): the compiler (g++ 16.1 Release C++17) is known only from the build path in the result .md, no exact flags or CPU model; libyaml ran through the ryml wrapper into a ryml Tree so the DOMs differ and the wrapper fails on anchors; yaml-cpp pinned to an old commit while libyaml ran master; libfyaml beats libyaml on compile_commands.
- Enricher (orphaned file): rapidyaml's LibyamlParser wrapper (bm/libyaml.hpp) discards libyaml's decoded scalar and stores the raw source slice from start_mark.index, which counts characters not bytes, so non-ASCII input is sliced wrong, quoted and block scalars stay undecoded and aliases are a no-op (output fidelity, not speed; travis.yml is pure ASCII). libyaml is cloned from master at build time while yaml-cpp is pinned to commit 587b24e2 (2019-11-30); each row is one Google Benchmark repetition (14930 vs 2024 iterations) from binary ryml-bm-parse-0.15.2. A parser takes its input only once (yaml_parser_set_input_\* assert(!parser-&gt;read_handler), compiled out under NDEBUG). Last stable release 0.2.5 (June 2020), 0.2.6-rc.1 April 2026; issues for CVE-2024-35325/35326/35328/35329 still open (the maintainer disputes three as API misuse).

## Caveats and trade-offs

Independent of both libraries but not a libyaml-focused suite: the rapidyaml benchmark exists to show ryml is about 3.6x faster than libyaml on this file (about 310 MB/s vs 86.79 MB/s). libyaml here is driven through rapidyaml's own wrapper (c4::yml::LibyamlParser in bm/libyaml.hpp) that builds a ryml Tree, whereas yaml-cpp builds its own Node DOM via YAML::Load, so the output structures differ; the wrapper cannot handle anchors and references (the suite skips libyaml on trusty.yml for that reason). The result JSON names the executable ryml-bm-parse-0.15.2 although the results directory is 0.16.0-pre. Exact compiler flags are not in the result files (only the build-directory name g++ 16.1 Release C++17) and the CPU model is not named, which keeps it below tier A. Single small file for the headline row (the README adds scatter plots over many files whose raw table was not read). The compile_commands.json row (135.06 vs 22.53 MB/s, 6.00x) comes from the README's JSON performance table, where libfyaml is faster than libyaml (149.15 MB/s). yaml-cpp is a widely known slow baseline and is pinned to an older fixed commit while libyaml is built from master.

Plain C89 event-based API (no DOM), YAML 1.1 only, so a tree or typed access has to be built on top; recent releases added nest-depth limits. yaml-cpp gives a ready Node DOM and targets YAML 1.2 features.

## Maintenance

Active but slow-moving: the last stable release is 0.2.5 (June 2020), 0.2.6-rc.1 was tagged in April 2026 and master last changed on 2026-08-21 (nest-depth getter); MIT-licensed, small portable C, so taking it from distribution packages or vendoring it is low-risk.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** rapidyaml's published benchmark suite (bm/bm_parse.cpp, results in biojppm/rapidyaml-data) is independent of both libyaml and yaml-cpp and shows libyaml_arena 86.79 MB/s vs yamlcpp_arena 11.71 MB/s on travis.yml; the compiler (g++ 16.1, Release, C++17) appears only in the build-directory name and exact flags and the CPU model are not stated, so it stays below A.
- **Verifier notes:** All claimed numbers match ryml-bm-parse-travis.txt (86.79 vs 11.71 MB/s, 7.41x; 0.05 vs 0.35 ms) and the rapidyaml README JSON table (135.06 vs 22.53 MB/s, 6.00x); hardware matches the result JSON context (20 CPUs at 4279 MHz, scaling and ASLR off, dated 2026-07-07). Added the compiler found in the result .md build path and the library pins from bm/CMakeLists.txt. Metadata checked: MIT, 1.2k stars, not archived, last commit 2026-08-21; the PyYAML CSafeLoader record already folds into this entry.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 4); enricher (wave 4)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.json>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.md>
  - <https://github.com/biojppm/rapidyaml-data/tree/master/bm/results/0.16.0-pre/linux-release>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/README.md>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/bm/bm_parse.cpp>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/bm/bm_common.hpp>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/bm/CMakeLists.txt>
  - <https://github.com/yaml/libyaml>
  - <https://github.com/yaml/libyaml/commits/master>
- **Sources the enricher read:**
  - <https://github.com/yaml/libyaml>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/ReadMe.md>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/announcement.msg>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/Changes>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/License>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/include/yaml.h>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/src/yaml_private.h>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/src/api.c>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/src/scanner.c>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/src/parser.c>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/src/loader.c>
  - <https://raw.githubusercontent.com/yaml/libyaml/HEAD/src/reader.c>
  - <https://github.com/yaml/libyaml/commits/master>
  - <https://github.com/yaml/libyaml/tags>
  - <https://github.com/yaml/libyaml/issues?q=is%3Aissue+slow+OR+performance+OR+CVE+OR+overflow+OR+crash>
  - <https://github.com/yaml/libyaml/issues/251>
  - <https://github.com/yaml/libyaml/issues/302>
  - <https://github.com/yaml/libyaml/issues/351>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/README.md>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/bm/bm_parse.cpp>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/bm/bm_common.hpp>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/bm/libyaml.hpp>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/bm/CMakeLists.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml/HEAD/bm/cases/travis.yml>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.json>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.md>
  - <https://github.com/jbeder/yaml-cpp/commit/587b24e2eedea1afa21d79419008ca5f7bda3bf4>
  - <https://github.com/jbeder/yaml-cpp/commit/587b24e2eedea1afa21d79419008ca5f7bda3bf4.patch>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/yaml/libyaml`) · [data/wave4/enrich/raw/github_com_yaml_libyaml.json](../../../data/wave4/enrich/raw/github_com_yaml_libyaml.json) (enrichment confidence 0.8)

</details>
