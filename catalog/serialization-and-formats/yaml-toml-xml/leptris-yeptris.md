# yeptris

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> C11 YAML 1.2 parser, DOM and emitter that parses 2-4x faster than libyaml on medium and large documents.

| | |
|---|---|
| **Beats** | libyaml |
| **Claimed result** | PERF-LEDGER 'Baseline 2026-09-01 (Apple silicon, Release+LTO, --quick)' table, libyaml event parse = 1.0x: DOM 2.2-3.6x, pull 2.7-4.0x, recorder 2.8-4.1x (e.g. scalar-heavy DOM 3.6x, wide-mapping DOM 3.5x, realworld-suite DOM 2.9x). The 'emit' column (4.8-6.9x) divides yeptris_serialize output MB/s by libyaml's PARSE MB/s. libyaml's emitter is never timed, so the emit column is not an emit-vs-emit win. This is the earliest table in the ledger. Later ledger entries give DOM 1.85-3.57x, and the README headline is scalar-heavy up to 3.36x, block \~2.3x, wide \~2.4x, anchor-heavy \~1.8x. |
| **Workload** | bench_matrix --quick uses seeded synthetic corpora (40k entries: block-heavy, flow-json, scalar-heavy, anchor-heavy, deep-nesting, wide-mapping) plus realworld-suite (libyaml snapshot files that both parsers accept), timed as min-of-3. yeptris DOM parse, pull, recorder, and serialize (emit from a pre-parsed DOM) are each divided by the same run's libyaml yaml_parser_parse event loop. libyaml builds no document, and its emitter is not measured. |
| **Metric** | throughput |
| **Hardware** | "Apple silicon" (exact CPU model not stated); CI additionally races the same matrix on shared GitHub Actions runners with libyaml pinned at commit 90a56d4 |
| **Compiler and flags** | yeptris: CMake Release with LTO (IPO) on by default; compiler and version not stated. libyaml reference: a separate static libyaml.a linked into the harness. CI builds it CMake Release without LTO; the build type of the dev-box libyaml behind the quoted table is not stated. |
| **Adoption** | 0 GitHub stars. The yeptris RubyGems gem (Ruby binding that vendors libyeptris) shows 136,902 total downloads per the rubygems.org API on 2026-09-25. |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/leptris/yeptris) · [benchmark](https://github.com/leptris/yeptris/blob/main/benchmarks/PERF-LEDGER.md) |

## Verdict

The quoted 2.2-3.6x (DOM) comes from the earliest table in the author's ledger: bench_matrix --quick on an unspecified Apple-silicon Mac, yeptris built Release+LTO against a static libyaml whose build flags are not stated. libyaml is timed as a bare event loop that builds no tree and includes parser teardown, while yeptris is timed without its free call. Later ledger entries and the README give 1.8-3.36x. The maintainer-linked serialbench C harness (2026-09-25, 8 CI runners, yeptris 0.6.21) broadly agrees on its 205 KB and 2.9 MB fixtures: parse 2.0-4.4x and parse+emit 1.4-3.9x libyaml. On its 163-byte fixture, yeptris was slower on 4 of 8 runners.

## Use it when

- C or C++ services that parse YAML configs or data files of roughly 200 KB to several MB, where the libyaml parse loop shows up in profiles. Both the author's ledger and the serialbench harness put yeptris at about 2-4x libyaml at these sizes.
- You want a ready tree with map lookups that are O(1) after first use, instead of building your own tree from libyaml events.
- Ruby or Python apps on Psych or PyYAML, both of which sit on libyaml. The yeptris gem and Python package present Psych- and PyYAML-compatible surfaces and bulk-drain events to avoid per-node FFI cost.
- You need strict YAML 1.2 conformance (395/395 yaml-test-suite, JSONTestSuite strict) but also want an opt-in YAML 1.1 compat schema for Psych-style implicit typing.
- Multi-document streams (logs, k8s manifests): iterparse and the recorder hold one document at a time, so memory is bounded by the largest document.

## Skip it when

- Tiny documents. On serialbench's 163-byte fixture, yeptris parse ran 0.14-1.78x libyaml and was slower on 4 of 8 CI runners. rapidyaml was faster than yeptris on 7 of 8 runners there, often by more than 2x.
- Emit-heavy workloads where rapidyaml is an option. Open issue #352 tracks YAML generation 1.24-1.98x behind rapidyaml, and serialbench medium parse+emit runs 0.51-0.80x of rapidyaml.
- Memory-tight services parsing untrusted input. The ledger measured DOM peak heap at 4.3-22.9x the input size (2026-09-02, before nodes shrank). Growth is capped at O(input), but the ledger says a 450 KB %TAG-expansion input can still drive about a 100 MB arena.
- Code that needs a mature, audited dependency. The repo was created on 2026-08-29, has 0 stars and is at 0.6.x. The authors call the libyaml-shaped event adapter internal, a gem release was yanked (#392), and ABI-pinned layouts are still changing in lockstep with the bindings.
- True streaming of one huge document, or a shared-library deployment. The recorder buffers until a document closes, and only the static library is installed (YEPTRIS_BUILD_SHARED is OFF).

## How it is fast

A single-pass, non-recursive indent-stack state machine classifies each line once. For the common shapes (`key: value`, `- item`) it builds DOM nodes directly instead of emitting and dispatching events, and it validates and builds JSON-class flow spans in one fused walk. Byte scanning uses nibble-lookup stop-set classification and SWAR loops, with AVX2 or NEON kernels picked at runtime via cpuid. One SIMD pre-scan counts structural bytes so the node array and arena are sized up front. Scalars are zero-copy views into the input. Nodes are compact (48-56 bytes) with 32-bit offset links in one contiguous arena, anchors go through an open-addressing hash interner, and numbers use a Clinger-bounded float fast path plus simdjson-style eight-digit SWAR.

## Compared with alternatives

Pick yeptris over rapidyaml when you need a plain C API, full yaml-test-suite acceptance (the ledger records rapidyaml rejecting suite-valid inputs), 1.1-compat typing or the Ruby/Python bindings. Parse speed on 0.2-3 MB documents is roughly even (serialbench 0.68-1.96x of rapidyaml), but rapidyaml wins clearly on tiny documents and on emitting. Over libfyaml, pick it for speed; yeptris's own plan treats libfyaml as the conformance and diagnostics reference and estimates it at only \~1-1.5x libyaml, a figure not measured here.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | No runtime dependencies beyond pthreads (Threads::Threads). The build needs CMake 3.20+. Tests fetch GTest. Benchmarks can optionally link libyaml, rapidyaml or simdjson. |
| **Minimum toolchain** | C11: it uses &lt;stdatomic.h&gt; and _Thread_local, and MSVC needs /experimental:c11atomics. CMake 3.20+. Tests and benchmarks need C++11 (C++20 under MSVC). Minimum GCC/Clang versions are not documented. |
| **Platforms** | x86-64 (AVX2 kernels via runtime cpuid dispatch, with SSE2/scalar fallback) and aarch64 (NEON). Other targets use the scalar path. CI tests Linux x64/arm64, macOS arm64/x64 and Windows x64/arm64. |
| **Thread safety** | Separate parses on separate threads are safe. One parsed document can be read from many threads: lazy map indexes and the handle pool sit behind a per-document mutex and are TSAN-tested. Parser, pull and recorder handles and document mutation are single-thread only. Errors go to a thread-local channel (yeptris_last_error). |
| **Drop-in for the baseline** | partial: not at the C level, where function names and event structs differ (the libyaml-shaped event adapter is internal). The Ruby gem and Python package are the drop-ins, for the libyaml-backed Psych and PyYAML. |

## Gotchas

- yeptris_parse borrows the input. The buffer must outlive the document, and scalar values are length-delimited views, not NUL-terminated strings. Pull and iterparse event strings are valid only until the next call.
- The default schema is YAML 1.2 Core, so yes/no/on/off stay strings and octal is 0o17. Pass YEPTRIS_SCHEMA_11_COMPAT to get libyaml/Psych-era implicit typing.
- yeptris_node_seq_at/map_at cache the child list of only the last container indexed, under a mutex. Interleaving index calls across containers rebuilds the cache each time, so iterate with yeptris_node_children.
- Free serialize buffers with yeptris_free: emit.h says the host free() is the wrong CRT on Windows, though docs/FFI.md still says libc free. The in-repo vcpkg port installs a LICENSE file the repo doesn't have (only LICENSE.md) and declares MIT, but the license is BSD-2-Clause.

## Caveats and trade-offs

All ratios are self-measured, first-party numbers. Hardware is given only as 'Apple silicon', and no compiler version is stated. The quoted table is the 2026-09-01 min-of-3 --quick snapshot of early code. Later ledger entries report lower DOM ratios (1.85-3.57x), and the README headline is 1.8-3.36x. The emit column divides yeptris serializer output throughput (bytes of output) by libyaml parse throughput, so it says nothing about libyaml's emitter. The timing is asymmetric: the libyaml timing includes parser teardown, while the yeptris DOM, pull, and recorder timings exclude their free calls. yeptris also gets LTO and libyaml does not. The ledger records a 1.35x floor on the first shared-runner CI run and repeated dev-box load and thermal noise. The ledger text calls flow-json DOM 2.5x the weakest cell, but anchor-heavy DOM 2.2x in the same table is lower. Current CI artifacts (run 36118925445, v0.6.22) show DOM 1.61-7.72x (ubuntu) and 2.09-6.99x (macOS), and pull 1.36-2.80x and 1.64-3.46x, against the libyaml parse. These CI numbers are not on the benchmark page.

C11 library with a Psych-compatible Ruby FFI gem and a PyYAML-compatible Python ctypes package; passes yaml-test-suite (395/395), JSONTestSuite YAML mode, and a libyaml parse-differential over 405 inputs; very new and unaudited (created Aug 2026, 0 stars).

## Maintenance

Actively developed and BSD-2-Clause: v0.6.22 shipped 2026-09-25, about four weeks after the repo was created, with 0 stars but \~137k gem downloads. It builds as a dependency-free CMake static library, but the API and ABI are still settling and nothing has been independently audited.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party ledger (benchmarks/PERF-LEDGER.md) whose public harness benchmarks/matrix/bench_matrix.cpp races an in-process libyaml (pinned 90a56d4). Hardware is given only as 'Apple silicon' and no compiler or version is stated. No peer-reviewed or independent third-party suite exists, so the record's tier B does not hold.
- **Verifier notes:** The claimed numbers match the ledger's 2026-09-01 baseline table verbatim, but tier B was wrong: every number is first-party, so the tier is C. Reading the harness code shows that the 'emit vs libyaml' ratios compare serializing against libyaml parsing, and the quoted table is the earliest, highest snapshot. GitHub reports the license as NOASSERTION, but LICENSE.md ('Ribose's BSD 2-Clause License', Ribose Inc) is the standard BSD-2-Clause text. The last commit is 2026-09-25 (v0.6.22); the repo is not a fork and not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/leptris/yeptris>
  - <https://github.com/leptris/yeptris/blob/main/benchmarks/PERF-LEDGER.md>
  - <https://github.com/leptris/yeptris/blob/main/benchmarks/matrix/bench_matrix.cpp>
  - <https://github.com/leptris/yeptris/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/leptris/yeptris/blob/main/.github/workflows/bench.yml>
  - <https://github.com/leptris/yeptris/blob/main/.github/workflows/profile.yml>
  - <https://github.com/leptris/yeptris/blob/main/CMakeLists.txt>
  - <https://github.com/leptris/yeptris/blob/main/CMakePresets.json>
  - <https://github.com/leptris/yeptris/blob/main/README.md>
  - <https://github.com/leptris/yeptris/blob/main/LICENSE.md>
  - <https://github.com/leptris/yeptris/blob/6797956e04b5640c0ac006dbc452872e76226095/benchmarks/matrix/bench_matrix.cpp>
  - <https://github.com/leptris/yeptris/blob/6797956e04b5640c0ac006dbc452872e76226095/benchmarks/PERF-LEDGER.md>
  - <https://github.com/leptris/yeptris/commits/main>
  - <https://github.com/leptris/yeptris/actions/runs/36118925445>
  - <https://github.com/leptris>
  - <https://rubygems.org/api/v1/gems/yeptris.json>
- **Sources the enricher read:**
  - <https://github.com/leptris/yeptris>
  - <https://github.com/leptris/yeptris/blob/main/README.md>
  - <https://github.com/leptris/yeptris/blob/main/PLAN.md>
  - <https://github.com/leptris/yeptris/blob/main/benchmarks/PERF-LEDGER.md>
  - <https://github.com/leptris/yeptris/blob/main/benchmarks/matrix/bench_matrix.cpp>
  - <https://github.com/leptris/yeptris/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/leptris/yeptris/blob/main/CMakeLists.txt>
  - <https://github.com/leptris/yeptris/blob/main/src/CMakeLists.txt>
  - <https://github.com/leptris/yeptris/blob/main/src/include/yeptris.h>
  - <https://github.com/leptris/yeptris/blob/main/src/include/yeptris/api.h>
  - <https://github.com/leptris/yeptris/blob/main/src/include/yeptris/parse.h>
  - <https://github.com/leptris/yeptris/blob/main/src/include/yeptris/types.h>
  - <https://github.com/leptris/yeptris/blob/main/src/include/yeptris/dom.h>
  - <https://github.com/leptris/yeptris/blob/main/src/include/yeptris/events.h>
  - <https://github.com/leptris/yeptris/blob/main/src/include/yeptris/emit.h>
  - <https://github.com/leptris/yeptris/blob/main/src/include/yeptris/error.h>
  - <https://github.com/leptris/yeptris/blob/main/src/include/yeptris/resolve.h>
  - <https://github.com/leptris/yeptris/blob/main/src/yeptris/memory/allocator.h>
  - <https://github.com/leptris/yeptris/blob/main/src/yeptris/common/simd_text.h>
  - <https://github.com/leptris/yeptris/blob/main/src/yeptris/scan/scan.h>
  - <https://github.com/leptris/yeptris/blob/main/src/yeptris/dom/dom.c>
  - <https://github.com/leptris/yeptris/blob/main/src/yeptris/events/yaml_compat.h>
  - <https://github.com/leptris/yeptris/blob/main/docs/ABI.md>
  - <https://github.com/leptris/yeptris/blob/main/docs/FFI.md>
  - <https://github.com/leptris/yeptris/blob/main/CHANGELOG.md>
  - <https://github.com/leptris/yeptris/blob/main/LICENSE.md>
  - <https://github.com/leptris/yeptris/blob/main/vcpkg.json>
  - <https://github.com/leptris/yeptris/blob/main/ports/yeptris/vcpkg.json>
  - <https://github.com/leptris/yeptris/blob/main/ports/yeptris/portfile.cmake>
  - <https://github.com/leptris/yeptris/blob/main/.github/workflows/test.yml>
  - <https://github.com/leptris/yeptris/blob/main/.github/workflows/bench.yml>
  - <https://github.com/leptris/yeptris/issues>
  - <https://github.com/leptris/yeptris/issues/352>
  - <https://github.com/leptris/yeptris/issues/342>
  - <https://github.com/leptris/yeptris/issues/377>
  - <https://github.com/serialbench>
  - <https://github.com/serialbench/serialbench-c>
  - <https://github.com/serialbench/serialbench-c/blob/main/src/bench.c>
  - <https://github.com/serialbench/serialbench-c/blob/main/.github/scripts/push-to-data.sh>
  - <https://github.com/serialbench/data/tree/main/runs/2026-09-25>
  - <https://github.com/serialbench/fixtures>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/leptris/yeptris`) · [data/wave4/enrich/raw/github_com_leptris_yeptris.json](../../../data/wave4/enrich/raw/github_com_leptris_yeptris.json) (enrichment confidence 0.8)

</details>
