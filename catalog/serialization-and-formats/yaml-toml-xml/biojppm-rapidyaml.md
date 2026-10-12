# rapidyaml (ryml)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++11 YAML 1.2/JSON parser and emitter that builds a zero-copy flat tree; \~25-30x yaml-cpp parse, \~140x emit.

| | |
|---|---|
| **Beats** | yaml-cpp |
| **Claimed result** | README: 'ryml parses at \~200MB/s and emits at \~600MB/s, and is generally 30x (parse) / 150x (emit) faster than yamlcpp, and never less than 10x (parse) / 50x (emit)'. Linked travis.yml parse data: ryml variants 163.41-358.98 MB/s (13.96x-30.66x) vs yamlcpp_arena 11.71 MB/s (1.00x); libyaml_arena 86.79 MB/s (7.41x), libfyaml_arena 62.47 MB/s (5.34x), so ryml is several times faster than libyaml on this file (derived from page data). Linked travis.yml emit data: ryml_yaml_str 1608.06 MB/s (142.69x) vs yamlcpp 11.27 MB/s. |
| **Workload** | Parsing/emitting a real-world travis.yml YAML file and a compile_commands.json file, measuring MB/s, comparing ryml against yaml-cpp, libyaml, and libfyaml (bm/bm_parse.cpp, bm/bm_emit.cpp) |
| **Metric** | throughput |
| **Hardware** | CPU model not stated. The google-benchmark context in ryml-bm-parse-travis.json shows a local machine (host 'bach', 20 CPUs @ 4279 MHz, L1d 32 KiB, L2 1 MiB shared by 2, L3 \~19.25 MiB, CPU scaling disabled), not Travis/AppVeyor CI runners. |
| **Compiler and flags** | gcc 16.1, CMake Release build, C++17 (build directory 'linux-x86_64-gxx16.1-Release-17' in ryml-bm-parse-travis.md; readthedocs 'Is it rapid' page says 'This section shows results using gcc 16.1'; Windows results use Visual Studio 2026). Explicit optimization/arch flags are not stated. |
| **Adoption** | 756 stars; used by Google (jsonnet), NVIDIA, CERN (ROOT/LHCb), OpenTelemetry C++, Toyota Research Institute |
| **Last commit** | 2026-09-06 |
| **Links** | [repository](https://github.com/biojppm/rapidyaml) · [benchmark](https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.txt) |

## Verdict

First-party google-benchmark runs on the author's machine (gcc 16.1, CMake Release, C++17; CPU model not stated, 20 logical CPUs at \~4.3 GHz). Parsing the 4.1 KB travis.yml into a tree ran at 287-346 MB/s for the ryml tree variants vs 11.71 MB/s for yaml-cpp's YAML::Load (24.5x-29.6x), with libyaml at 86.8 and libfyaml at 62.5 MB/s; emitting to std::string ran at 1608 vs 11.27 MB/s for yaml-cpp's ostream emit (142.7x). Across 44 files the parse speedup over yaml-cpp was 9.7x-39.7x, and a Visual Studio 2026 Windows run showed 24.7x parse and 95.6x emit.

## Use it when

- Loading large YAML config or data files where yaml-cpp parse time is a bottleneck: the author's scatter data shows 19.6x-39.7x over yaml-cpp on 2-147 MB files (e.g. 303.8 vs 10.8 MB/s on a 147 MB file).
- Emit-heavy workloads that write YAML/JSON (dumps, state snapshots, code generation): 1.6 GB/s to std::string on travis.yml, and 45x-347x over yaml-cpp across the emit scatter set.
- Hot loops that re-parse many documents: reuse one Parser and Tree and parse in place; reserve the tree first with estimate_tree_capacity().
- Builds with exceptions disabled, custom allocators, or no STL in the data structures, including bare-metal and less common architectures (arm v4-v7, riscv64, s390x, ppc, mips, loongarch64, wasm) that the CI covers.
- Mixed YAML/JSON pipelines where you want one library: parse_json_in_place reached 908 MB/s on compile_commands.json, ahead of every tested JSON library except rapidjson in-situ.

## Skip it when

- Documents with container (complex) map keys: the parse engine accepts them, but ryml::Tree and the default Parser reject them. UTF-16/UTF-32 input is also unsupported (support was removed in 0.16.0).
- Untrusted input with anchors/aliases on the v0.16.0 release: tree.resolve() stack-overflows on cyclic aliases and expands 'billion laughs' input without bound (issue #656). The fix, which adds a max_size_multiplier defaulting to 50, is on master but not yet in a tagged release, and parse-time limits on depth, size and entry count are still an open request (#660).
- When you want a yaml-cpp-style owning, typed DOM that throws exceptions: ryml gives you non-owning, non-null-terminated views, lookups that scan linearly, and a default error handler that calls std::abort().
- Pure JSON at maximum throughput: in the author's table rapidjson in-situ parses at 1741.6 MB/s against ryml's 908, and the docs say simdjson is probably faster too.
- Files dominated by multi-line double-quoted or plain scalars: the lead shrinks to 9.7x over yaml-cpp and 1.4x-1.7x over libfyaml/libyaml (scalar_dquot_multiline: 246 vs 170 vs 144 MB/s).

## How it is fast

The parse engine is a non-recursive state machine templated on its event handler (static polymorphism, no virtual calls), so events feed straight into the tree builder. The tree is one contiguous array of trivially copyable NodeData records linked by integer ids (parent, first/last child, prev/next sibling), with key/value held as (tag, scalar, anchor) string views: no per-node heap allocation, no std::map, no string copies. Escape and folding filtering happens in place in the source buffer, only the node array and string arena ever allocate (both can be pre-reserved with estimate_tree_capacity, and parser and tree can be reused), and number conversion uses c4core charconv plus bundled fast_float. By contrast, the author's alternatives page describes yaml-cpp as built on std::map-style node pointers, allocations, string copies, polymorphism and C++ streams.

## Compared with alternatives

Pick ryml over fkYAML (header-only, owning typed nodes on std::string/std::map, \~7.5x yaml-cpp in its own suite), libfyaml (C API) or PipeYAML (\~10x yaml-cpp load) when raw parse/emit throughput and memory footprint dominate and you can manage buffer lifetimes. In ryml's own run it parsed travis.yml 5x faster than libfyaml (315.8 vs 62.5 MB/s). Pick fkYAML for a nlohmann-style owning DOM that drops in as headers. The sibling ratios come from different suites and machines, so compare them only roughly.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake; shared optional) or source-drop (amalgamated single header, or single .hpp + .cpp) |
| **Dependencies** | none external; vendors a subset of c4core and fast_float (can use a system c4core via RYML_SYSTEM_C4CORE; open issue #664 reports a build failure when that c4core lacks fast_float) |
| **Minimum toolchain** | C++11; claimed g++ 4.8+, clang++ 3.9+, Visual Studio 2015+, Intel; CMake 3.13+ recommended (open issue #350: single header fails on gcc 4.8.5) |
| **Platforms** | Linux, Windows, macOS, bare-metal; CI covers x64, x86, aarch64, armv4-v7, riscv64, loongarch64, mips/mips64 (both endians), ppc/ppc64/ppc64le, s390x, sparc64, wasm (emscripten); MinGW release builds fail tests (open #603) |
| **Thread safety** | Not documented for Tree/Parser. set_callbacks()/get_callbacks()/reset_callbacks() are documented as NOT thread-safe because they use global static state. |
| **Drop-in for the baseline** | no |

## Gotchas

- Scalars are csubstr views (pointer + length) and are not null-terminated, so never pass .str to printf/stof. With parse_in_place the source buffer must outlive the tree, and set_val() on a temporary std::string dangles; use set_serialized() to copy into the arena. Growing the arena can relocate it, and reorder() invalidates node ids.
- Parse errors call std::abort() by default. Set error callbacks that must never return (throw or longjmp) or build with RYML_DEFAULT_CALLBACK_USES_EXCEPTIONS; issue #527 shows the event handler's callbacks overriding the tree's unless you construct the handler with them.
- tree["key"] / find_child() does a linear scan of the children, so chained [] lookups inside a loop over a large map are quadratic. Iterate children in order, or build your own index.
- Aliases and '&lt;&lt;' merge keys stay unresolved until you call tree.resolve(); open issue #533 reports order-dependent merge-key results. Duplicate keys are accepted, and tab characters after ':' or '-' are rejected unless compiled with RYML_WITH_TAB_TOKENS.

## Caveats and trade-offs

First-party numbers from the author's own machine (the 'travis'/'appveyor' in result file names are the input files bm/cases/travis.yml and appveyor.yml, not CI runners). The CPU model is never named and flags beyond a CMake Release build are not given, so the tier is capped at C despite public, runnable benchmark code. The README's 'never less than 10x (parse)' is slightly overstated: the linked parse scatter data shows scalar_dquot_multiline at 9.73x vs yaml-cpp. The 0.16.0-pre result JSON records executable 'ryml-bm-parse-0.15.2' dated 2026-07-07. Independent success stories (rATHENA 10x-70x, OpenXcom 67x, CERN LHCb memory drop) corroborate large speedups over yaml-cpp.

Parses into a flat, index-based tree of string views into the source buffer rather than a DOM with owned strings; in-place parsing mutates the source buffer; C++11, deliberately avoids std containers in its own data structures

## Maintenance

Actively maintained (v0.16.0 released 2026-07-22, master commits into September 2026), MIT-licensed, and packaged in vcpkg, Conan and several Linux distros. It is still pre-1.0: 0.16.0 deprecated many operators, and ABI stability is promised only across patch releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party results from public benchmark code (bm/bm_parse.cpp, bm/bm_emit.cpp, yaml-cpp/libyaml/libfyaml pulled in by bm/CMakeLists.txt); compiler is stated (gcc 16.1, Release, per the results .md build path and the readthedocs page) but no CPU model and no explicit flags beyond a CMake Release build, so not A; not an independent suite, so not B.
- **Verifier notes:** Numbers match the linked results file and README. The record misread the result filenames as Travis/AppVeyor CI runs; hardware and compiler fields are corrected from the result .json/.md. last_commit was the repo pushed_at date (2026-09-24); the default-branch head is 2026-09-06.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.json>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.md>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-emit-travis.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-scatter-mega_bytes_per_second.txt>
  - <https://github.com/biojppm/rapidyaml>
  - <https://github.com/biojppm/rapidyaml/blob/master/README.md>
  - <https://github.com/biojppm/rapidyaml/blob/master/bm/bm_parse.cpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/bm/CMakeLists.txt>
  - <https://github.com/biojppm/rapidyaml-data>
  - <https://rapidyaml.readthedocs.io/latest/sphinx_is_it_rapid.html>
- **Sources the enricher read:**
  - <https://github.com/biojppm/rapidyaml>
  - <https://github.com/biojppm/rapidyaml/blob/master/README.md>
  - <https://github.com/biojppm/rapidyaml/blob/master/doc/sphinx_yaml_standard.rst>
  - <https://github.com/biojppm/rapidyaml/blob/master/doc/sphinx_is_it_rapid.md>
  - <https://github.com/biojppm/rapidyaml/blob/master/doc/sphinx_alternative_libraries.rst>
  - <https://github.com/biojppm/rapidyaml/blob/master/doc/sphinx_using.rst>
  - <https://github.com/biojppm/rapidyaml/blob/master/doc/doxy_main.md>
  - <https://github.com/biojppm/rapidyaml/blob/master/ROADMAP.md>
  - <https://github.com/biojppm/rapidyaml/blob/master/changelog/current.md>
  - <https://github.com/biojppm/rapidyaml/blob/master/changelog/0.16.0.md>
  - <https://github.com/biojppm/rapidyaml/blob/master/bm/bm_parse.cpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/bm/bm_emit.cpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/bm/libyaml.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/samples/quickstart.cpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/tree.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/tree.cpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/parse_engine.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/parse.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/parse_options.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/common.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/error.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/node.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/node_type.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/filter_processor.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/event_handler_tree.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/reference_resolver.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/src/c4/yml/resolve_options.hpp>
  - <https://github.com/biojppm/rapidyaml/blob/master/ext/c4core.src/c4/cpu.hpp>
  - <https://github.com/biojppm/rapidyaml/releases>
  - <https://github.com/biojppm/rapidyaml/issues>
  - <https://github.com/biojppm/rapidyaml/issues/656>
  - <https://github.com/biojppm/rapidyaml/issues/660>
  - <https://github.com/biojppm/rapidyaml/issues/527>
  - <https://github.com/biojppm/rapidyaml/issues/533>
  - <https://github.com/biojppm/rapidyaml/issues/655>
  - <https://github.com/biojppm/rapidyaml/issues/221>
  - <https://github.com/biojppm/rapidyaml/issues/331>
  - <https://github.com/biojppm/rapidyaml/issues/351>
  - <https://github.com/biojppm/rapidyaml/issues/534>
  - <https://github.com/biojppm/rapidyaml/issues/289>
  - <https://github.com/biojppm/rapidyaml/issues/301>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-travis.md>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-emit-travis.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-parse-scatter-mega_bytes_per_second.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/linux-release/ryml-bm-emit-scatter-mega_bytes_per_second.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/windows-release/ryml-bm-parse-travis.txt>
  - <https://raw.githubusercontent.com/biojppm/rapidyaml-data/master/bm/results/0.16.0-pre/windows-release/ryml-bm-emit-travis.txt>
  - <https://github.com/fktn-k/fkYAML/blob/main/README.md>
  - <https://github.com/pantoniou/libfyaml/blob/master/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/biojppm/rapidyaml`) · [data/wave4/enrich/raw/github_com_biojppm_rapidyaml.json](../../../data/wave4/enrich/raw/github_com_biojppm_rapidyaml.json) (enrichment confidence 0.85)

</details>
