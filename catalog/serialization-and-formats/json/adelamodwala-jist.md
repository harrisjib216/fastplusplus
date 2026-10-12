# jist

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `GPL-3.0` · 🟡 stale

> Rust CLI that pulls one value by exact key/index path from multi-GB JSON files, far faster than jq.

| | |
|---|---|
| **Beats** | jq |
| **Claimed result** | 3.3GB file (get last element): jist 2.05s vs jq 34.17s (\~16.7x, derived from page data), 1600MB/s vs 96MB/s, 4.5GB vs 18GB memory. 28.9GB file: jist 1:30s, 9.7MB memory, 321MB/s (streaming json-tools fallback); jq could not run ('not enough ram'). |
| **Workload** | Extracting a single key-path value (the last array element) from large synthetic JSON array files (3.3GB via the simdjson path; 28.9GB via the streaming lexer fallback) |
| **Metric** | throughput |
| **Hardware** | Intel i7-12700H, 64GB DDR5@4800MT RAM |
| **Compiler and flags** | Both jist and the Rust data generator are built with 'cargo build --release' (the README marks building jist from source as optional). build.rs compiles the vendored simdjson with only -std=c++17 added, and neither the Rust nor the C++ compiler version is stated. |
| **Adoption** | 23 stars |
| **Last commit** | 2025-02-15 |
| **Links** | [repository](https://github.com/adelamodwala/jist) · [benchmark](https://github.com/adelamodwala/jist#benchmarks) |

## Verdict

The author's single-run test on an Intel i7-12700H with 64 GB DDR5 used a generated, pretty-printed 3.3 GB array of 10M objects and extracted [9999999].bar.baz. jist's simdjson path took 2.05 s and 4.5 GB, against jq's 34.17 s and 18 GB (about 16.7x, 1600 vs 96 MB/s). On a 28.9 GB file the streaming lexer took 1:30 with 9.7 MB of memory while jq ran out of RAM. The jq and compiler versions are not stated. The repo's jist_vs_jq.png shows the jq run timed with /usr/bin/time -v (0:34.17, 18.2 GB max RSS) next to an earlier jist run of 10.21 s at 7.8 MB RSS on the same query, which matches the streaming lexer, so there is no screenshot of the 2.05 s simdjson run.

## Use it when

- Scripts or ad-hoc shell work that need one known value (a token, a config field, the Nth record) from a JSON file of hundreds of MB to about 4 GB, and jq is slow or runs out of RAM
- Files larger than RAM or larger than 4 GiB, where the streaming fallback holds memory near 10 MB and still ran the author's 28.9 GB file at 321 MB/s
- Linux x86-64 machines where you can drop in the prebuilt v0.3 release binary rather than build the C++/Rust bridge
- Pretty-printed or NDJSON-style input with regular line breaks, which matches the benchmark data and suits the streaming fallback's newline-aligned chunking
- A quick schema summary of a JSON or NDJSON file (the schema feature is newer than the v0.3 binary, so this needs a source build)

## Skip it when

- Any real jq work: filters, select/map, wildcards, several outputs per run, reshaping or recursive descent. jist does exactly one key/index lookup
- Memory-tight machines with files under 4 GiB: the simdjson path loads the whole file (4.5 GB RSS on the 3.3 GB benchmark). Use -s to force the \~300 MB/s streaming path
- Minified single-line files (or single lines longer than 1 MB) in streaming mode. From reading buf_parser.rs, a 1 MB chunk with no newline returns 'result not found' instead of being processed (not tested)
- Pipelines that rely on exit codes or on stdin streaming. On the simdjson path a missing key or parse error is printed to stdout as 'JSON error: ...' with exit status 0, and stdin is always read fully into memory even with -s
- Projects that want a maintained, packaged tool: one author, 23 stars, no commits since 2025-02-15, GPL-3.0, and not on crates.io under this name

## How it is fast

For files under 4 GiB (u32::MAX bytes), a small C++ wrapper, called from Rust through autocxx/cxx, loads the whole file into a simdjson padded_string. It then runs simdjson 3.11.3 On Demand `document::at_path()`, which the header says supports only key and index paths that convert directly to JSON Pointer. The file gets SIMD structural indexing and lazy navigation that skips unrequested values without building a DOM, while jq builds a full tree (18 GB RSS for the 3.3 GB file). Larger files, or runs with -s, use a Rust fallback: the json-tools token lexer runs over 1 MB newline-aligned chunks, tracks depth and array-index counters, and reads the matched byte range back from the file by seeking to it. This keeps memory at about 10 MB but runs at about 300 MB/s.

## Compared with alternatives

Pick jist over the catalogued simdjson library when you want a ready-made shell command instead of writing C++; its speed is simdjson On Demand's at_path, so inside a C++ or Rust program call simdjson (or simd-json/sonic-rs) directly. Pick it over fastgron when you know the exact path and want one value rather than a greppable flattening of the whole file; JSONSki and Pison are research libraries for large-record path queries, not end-user CLIs.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Vendored amalgamated simdjson 3.11.3 (C++, compiled by build.rs). Crates: cxx, autocxx, json-tools, serde_json (preserve_order), clap, regex, futures, json_value_merge, lazy_static, log. Build-time: autocxx-build and miette. autocxx needs LLVM/libclang installed |
| **Minimum toolchain** | Rust 2021 edition. Probably Rust 1.79+, because src/schema_parser.rs uses std::path::absolute; no MSRV is stated. A C++17 compiler (build.rs passes -std=c++17 or /std:c++17) and LLVM/libclang for autocxx are also needed. Compiler versions are not documented |
| **Platforms** | Prebuilt binary is Linux x86-64 only (the jist.linux.x86_64 asset on v0.2 and v0.3). A source build should work wherever Rust, a C++17 compiler and libclang are available, but that is not documented or tested; build.rs has clang and MSVC flags. simdjson picks its SIMD kernel at runtime (no -march is set) |
| **Thread safety** | Not documented. It is a single-process CLI; path search is single-threaded, and the non-streaming schema summarizer uses a futures ThreadPool |
| **Drop-in for the baseline** | no |

## Gotchas

- `cargo install jist` installs an unrelated crate: the crates.io name 'jist' belongs to a programming-language project (v0.1.9). Build from the repo or use the GitHub release binary
- The v0.3 release binary (2025-01-11) predates the schema/NDJSON summarizer commits (from 2025-01-12), so it only does path search. The Cargo.toml version still says 0.1.0
- Output is not jq -r output. String values come back with JSON escapes still in them, and leading/trailing quote characters are trimmed greedily: the repo's own unit test expects the value "\"q\"" to print as \"q\ . Objects and arrays are re-serialized compactly through serde_json
- The simdjson path does not validate the whole document (simdjson's iterate docs say invalid JSON may not trigger an error), and the README says malformed input is tolerated in streaming mode as long as the target value is complete. From reading the code, the streaming path may also panic when a 1 MB chunk boundary splits a multi-byte UTF-8 character (not tested)

## Known shortcomings

- Rust CLI whose speed comes from a bundled copy of simdjson (C++); for C++ use, take simdjson directly. Works on JSON array files, not NDJSON. GPL-3.0; stale since 2025-02; 23 stars.
- The \~16.7x ratio compares two different sessions (no screenshot of the 2.05 s run; the screenshot's own streaming run is about 3.3x faster than jq), and jq and compiler versions are unstated. The simdjson path loads the whole file (4.5 GB RSS on 3.3 GB). One path lookup per run, no filters; not a jq replacement. 'cargo install jist' installs an unrelated crate. Missing keys print an error with exit status 0; the streaming fallback fails on single-line files over 1 MB (source reading).

## Caveats and trade-offs

jist itself is a Rust CLI (\~63KB of Rust) that calls a vendored simdjson (the source of GitHub's 'C++' language label) through autocxx/cxx. The C++ speed comes from simdjson, and the 28.9GB streaming run uses the Rust json-tools lexer, not simdjson. The benchmark is first-party: one synthetic data shape, one query, compared only with jq (a C tool), not with simdjson, RapidJSON or nlohmann directly. The generator is public but the jq invocation and timing method are not scripted, and compiler versions and flags are not documented.

Uses simdjson internally (does not itself beat simdjson) and falls back to a much slower (\~300MB/s) character-based lexer for files &gt;4.2GB or forced streaming mode; jq has vastly broader query capability than jist's single key-path extraction

## Maintenance

Stale: one author, last commit 2025-02-15, 0 open issues and only two self-merged PRs. It is usable today as a GPL-3.0 Linux x86-64 binary or a small (\~63 KB of Rust) source build, but for anything beyond one-off lookups treat it as a personal tool.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks tables compare jist with jq on a 3.3GB file (2.05s vs 34.17s, 1600 vs 96MB/s, 4.5GB vs 18GB) and a 28.9GB file (jq ran out of RAM), naming the CPU (i7-12700H). The data generator is public (benchmarking/src/main.rs), but there is no scripted jq run and no compiler versions or flags beyond 'cargo build --release', so this is first-party evidence with partial methodology: tier C.
- **Verifier notes:** The numbers match the README; the only claim fix is labelling the 16.7x ratio as derived. The orchestrator should consider changing language from C++ to Rust (a simdjson wrapper), since jist's own code is Rust and the corrections schema has no language field. Metadata checked with gh: GPL-3.0, 23 stars, not a fork, last commit 2025-02-15 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/adelamodwala/jist#benchmarks>
  - <https://github.com/adelamodwala/jist>
  - <https://api.github.com/repos/adelamodwala/jist>
  - <https://api.github.com/repos/adelamodwala/jist/commits?per_page=1>
  - <https://api.github.com/repos/adelamodwala/jist/readme>
  - <https://api.github.com/repos/adelamodwala/jist/languages>
  - <https://api.github.com/repos/adelamodwala/jist/license>
  - <https://github.com/adelamodwala/jist/blob/main/Cargo.toml>
  - <https://github.com/adelamodwala/jist/blob/main/build.rs>
  - <https://github.com/adelamodwala/jist/tree/main/benchmarking>
- **Sources the enricher read:**
  - <https://github.com/adelamodwala/jist>
  - <https://github.com/adelamodwala/jist#benchmarks>
  - <https://api.github.com/repos/adelamodwala/jist>
  - <https://api.github.com/repos/adelamodwala/jist/readme>
  - <https://api.github.com/repos/adelamodwala/jist/languages>
  - <https://api.github.com/repos/adelamodwala/jist/releases>
  - <https://api.github.com/repos/adelamodwala/jist/tags>
  - <https://api.github.com/repos/adelamodwala/jist/issues?state=all>
  - <https://api.github.com/repos/adelamodwala/jist/commits?per_page=40>
  - <https://api.github.com/repos/adelamodwala/jist/git/trees/HEAD?recursive=1>
  - <https://github.com/adelamodwala/jist/blob/main/Cargo.toml>
  - <https://github.com/adelamodwala/jist/blob/main/build.rs>
  - <https://github.com/adelamodwala/jist/blob/main/src/main.rs>
  - <https://github.com/adelamodwala/jist/blob/main/src/lib.rs>
  - <https://github.com/adelamodwala/jist/blob/main/src/simd_parser.rs>
  - <https://github.com/adelamodwala/jist/blob/main/src/simdjson/wrapper.cpp>
  - <https://github.com/adelamodwala/jist/blob/main/src/simdjson/wrapper.h>
  - <https://github.com/adelamodwala/jist/blob/main/src/simdjson/simdjson.h>
  - <https://github.com/adelamodwala/jist/blob/main/src/utils.rs>
  - <https://github.com/adelamodwala/jist/blob/main/src/buf_parser.rs>
  - <https://github.com/adelamodwala/jist/blob/main/src/schema_parser.rs>
  - <https://github.com/adelamodwala/jist/blob/main/src/schema_stream_parser.rs>
  - <https://github.com/adelamodwala/jist/blob/main/benchmarking/src/main.rs>
  - <https://github.com/adelamodwala/jist/blob/main/benchmarking/Cargo.toml>
  - <https://github.com/adelamodwala/jist/blob/main/jist_vs_jq.png>
  - <https://crates.io/api/v1/crates/jist>
  - <https://github.com/google/autocxx>
  - <https://github.com/google/autocxx/blob/main/book/src/tutorial.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/adelamodwala/jist`) · [data/wave4/enrich/raw/github_com_adelamodwala_jist.json](../../../data/wave4/enrich/raw/github_com_adelamodwala_jist.json) (enrichment confidence 0.72)

</details>
