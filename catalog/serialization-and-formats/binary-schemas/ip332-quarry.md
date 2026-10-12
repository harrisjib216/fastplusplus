# Quarry

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Schema compiler emitting no-heap C99, C++20 and Python BRF codecs; its C decoder beats Protobuf C++ on large/nested payloads.

| | |
|---|---|
| **Beats** | Protocol Buffers (C++, including Arena allocation) |
| **Claimed result** | Results are mixed. The README table is from commit 04349e57, medians of 5 CI runs, in ops/s. Protobuf C++ wins telemetry encode (18.81M vs Quarry C 9.69M), telemetry decode (13.48M vs 5.45M) and large encode (1.60M vs 0.48M). Quarry C wins large decode: 0.85M vs 0.57M for Protobuf C++ (\~1.5x) and 0.45M for Protobuf Arena (\~1.9x). It also beats Protobuf Arena on large encode, 0.48M vs 0.37M (\~1.3x) (ratios derived from page data). Quarry C++ is slower than Protobuf C++ in every row. BRF is larger on the wire: 60 vs 16 bytes/record for telemetry and 1,661 vs 1,425 for large. |
| **Workload** | Encode/decode ops-per-second and bytes-per-record for telemetry and large-payload workloads, comparing Quarry's C and C++ generated code (BRF wire format) against protoc-generated Protobuf C++ (default and Arena) code, five aggregated CI runs. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7763 64-Core Processor, Linux x86_64, GitHub-hosted runner (docker compose dev container) |
| **Compiler and flags** | GCC 13.3.0 (`c++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`), CMake preset docker-benchmark with CMAKE_BUILD_TYPE=Release (CMake's GCC Release default: -O3 -DNDEBUG). The project builds as C++20 and the Quarry C harness as C99, in an Ubuntu 24.04 dev container. Protobuf/protoc 3.21.12 (libprotoc 3.21.12). |
| **Adoption** | 4 stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/ip332/quarry) · [benchmark](https://github.com/ip332/quarry#performance--footprint) |

## Verdict

Quarry's public-API benchmark (GCC 13.3 Release -O3, GitHub-hosted AMD EPYC 7763, medians of 5 runs, against Protobuf C++ 3.21.12 distro build, default and Arena) shows Quarry C decoding the large workload at 0.85M ops/s vs 0.57M (\~1.5x) in the README baseline (commit 04349e57) and 1.17M vs 0.57M (\~2.0x) at HEAD 5c8adcde, plus 2.84M vs 1.76M nested decode (\~1.6x) at HEAD, while losing telemetry encode/decode and large encode by 1.9-3.3x in the README table. Quarry C writes into caller-owned fixed buffers while Protobuf uses its allocating owning API, and the Arena harness deep-copies (`CopyFrom`) each record before serializing, so the wins partly measure the API and allocation model, not only codec speed.

## Use it when

- MCU-to-Linux or device-telemetry links where the embedded side needs a strict-C99, malloc-free codec with statically sized buffers; CI cross-builds the generated C for Cortex-M4 with arm-none-eabi-gcc.
- Decode-heavy C code on records with many bounded strings, bytes, arrays or repeated nested records. At HEAD (CI run on 5c8adcde), Quarry C decodes the large workload at 1.17M ops/s against 0.57M for Protobuf C++, and the nested workload at 2.84M against 1.76M.
- One schema shared by an embedded C producer and Python tooling. The README says C, C++ and Python encodings are verified byte-for-byte identical.
- Teams whose Protobuf/Nanopb schemas are already fully bounded (`max_size`/`max_count`) and who want to evaluate a no-heap alternative using the descriptor-set translator.

## Skip it when

- Small or sparse messages. At HEAD, Protobuf C++ is \~2x faster on telemetry decode (13.5M vs 6.9M ops/s) and \~2.8x faster on stress decode (18.7M vs 6.6M). BRF v2 records are also much larger: 84 bytes vs Protobuf's 16 (telemetry) and 5 (stress), because every declared field gets a slot.
- Bandwidth- or storage-bound links. Each record and each nested record carries its own 16-byte header, and the large workload is 1,771 bytes vs 1,425 for Protobuf at HEAD.
- C++ call sites. The generated C++ API returns owning std::vector/std::string values and is slower than Protobuf C++ in every benchmark row, e.g. large decode 0.22M vs 0.57M ops/s.
- Schemas that need Protobuf wire compatibility, oneof, maps, proto3 optional, recursive messages, nested arrays, unbounded strings/arrays or negative enum values. All of these are unsupported or rejected.
- Persisted data or public protocols that need a stable format. The project is pre-1.0 (v0.1.30-rc.3) with a single maintainer and 4 stars. Its release notes say BRF v1 data from RC1 is not wire-compatible with RC2/RC3 (BRF v2).

## How it is fast

The C path never touches the heap: decode validates the record and copies strings, bytes, arrays and nested records into inline fixed-capacity struct members sized from the schema bounds. Protobuf C++ allocates std::string/RepeatedField/sub-message storage for those fields on every parse, which largely explains Quarry C's large (\~2.0x) and nested (\~1.6x) decode wins at HEAD. The current wire format, BRF v2, is a schema-determined fixed-offset layout (16-byte header, presence bitmap, one slot per declared field in declaration order, fixed-width big-endian scalars inline, variable data behind 8-byte offset/length descriptors), so encoding is plain stores at known offsets with no per-scalar varint work. The cost is wire size, because absent fields still occupy their slots and nothing is varint-compressed.

## Compared with alternatives

Pick Quarry over SBE, YaFF or ProtoCache only when you need strict-C99, no-heap generated code for a microcontroller plus a matching Python backend from the same schema. Those siblings report far larger margins over Protobuf (e.g. SBE \~6.75x faster decode, ProtoCache \~20x decode+traverse), while Quarry C wins only on large and nested decode and loses on small messages.

## Integration

| | |
|---|---|
| **Form** | header-only runtime (`Quarry::runtime`, C++20 INTERFACE target; C codec primitives are `static inline` headers) plus generated .h/.c or .hpp per schema. The schema compiler is a built host tool. The generic QBS/BRF-inspection C runtime `Quarry::runtime_c` builds as a static lib, although its README calls it header-only. |
| **Dependencies** | Generated code and runtime: none beyond the C99 or C++20 standard library. The schema compiler needs libyaml, Protobuf (libprotobuf + protoc) and Abseil to build. |
| **Minimum toolchain** | C99 for generated C; C++20 for the C++ runtime and the compiler; CMake 3.20+. CI uses GCC 13.3 on Ubuntu 24.04 and arm-none-eabi-gcc for Cortex-M4. |
| **Platforms** | Any. The wire format is explicit big-endian with byte-wise, alignment-safe access. CI covers Linux x86-64 and a Cortex-M4 bare-metal cross-build; Windows and macOS are not in CI. |
| **Thread safety** | not documented (generated codecs are free functions over caller-owned structs and buffers) |
| **Drop-in for the baseline** | partial: not wire- or API-compatible with Protobuf. quarry-protobuf-translator turns a bounded subset of .proto descriptor sets into .brd schemas, but every call site must be rewritten. |

## Gotchas

- Generated C structs reserve worst-case capacity for every bounded field. The benchmark Workload struct is 3,576 bytes, against a 128-byte Protobuf message object. `_decode()` returns the whole record by value inside its result struct, so check stack budgets on MCUs.
- Field indexes are compiler-assigned, not author-assigned tags as in Protobuf. BRF v2 places slots in schema declaration order, and the BRF spec defers schema-evolution rules to future work, so treat reordering or inserting fields as a wire break.
- The README performance table comes from commit 04349e57 (Aug 2026), before the BRF v2 switch. At HEAD, telemetry encodes to 84 bytes, not 60, and the speeds differ. Use the CI `Benchmarks` artifact for current numbers.
- The README's Cortex-M4F table reports 6,243 cycles for 500 encodes, about 12.5 cycles per 85-byte record. A Cortex-M4 cannot store 85 bytes in that time, so treat the table as unverified.

## Known shortcomings

- Borderline: Protobuf wins most benchmark rows; Quarry's C implementation is faster only on large-payload decode (\~1.5-2x).

## Caveats and trade-offs

The project has 4 stars and a single maintainer. It was created 2026-06-19 and is pre-1.0 (v0.1.30-rc.3). The author says the suite 'does not rank backends' and calls the ownership differences 'not a backend-quality ranking'. Quarry C decodes into a caller-owned fixed-capacity struct with no heap allocation, while Protobuf C++ allocates a fresh owning message per decode, so the large-decode win mostly reflects the API model. Shared GitHub-hosted runners add noise. Protobuf 3.21.12 is the Ubuntu distro build, not current Protobuf. Numbers move between commits. The CI artifact for HEAD 5c8adcde (2026-09-20) has Quarry C ahead of Protobuf C++ on large decode (1.17M vs 0.574M ops/s, \~2.0x), nested decode (2.84M vs 1.76M, \~1.6x), large round-trip (\~1.6x), nested round-trip (\~1.3x) and configuration encode (\~1.09x). The same artifact has it behind on telemetry, stress, configuration decode and large/nested encode (ratios derived from artifact data). CI artifacts expire, so the README table is the stable reference.

Header-only/deterministic-footprint native runtime (claimed zero native runtime size) vs Protobuf's external runtime library. Larger wire format than Protobuf on tested workloads. Very new/low-adoption project; README explicitly warns shared-runner timing is 'informational' and depends on hardware/compiler/optimization/runtime/workload.

## Maintenance

Actively developed by one maintainer (last push 2026-09-20, v0.1.30-rc.3 prerelease, 4 stars, no external issues) and Apache-2.0 and copyable, but pre-1.0 with a wire-format break already between RC1 and RC2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README's 'Performance & footprint' section compares generated Quarry C/C++ with protoc-generated Protobuf C++, both default and Arena. It uses the public harness in benchmarks/c/proof_benchmark.c, benchmarks/cpp/proof_benchmark.cpp and benchmarks/protobuf/proof_benchmark.cpp, driven by benchmarks/scripts/run_benchmarks.py. The README states GCC 13.3.0, a Release build and an AMD EPYC 7763; the CI manifest confirms the compiler, CMAKE_BUILD_TYPE=Release and libprotoc 3.21.12. Code, compiler, flags and CPU are all present, so A.
- **Verifier notes:** The README table matches the record exactly. The case is borderline because Protobuf wins most rows and the author makes no speed claim. I kept it rather than rejecting as not-faster: Quarry C is measurably faster than Protobuf C++ on large-payload decode in both the README baseline and the latest CI run, which also shows a nested-decode win, and the record reports this honestly. I set compared_against_cpp_std_directly to false and added the compiler and flag provenance from the CI manifest.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ip332/quarry#performance--footprint>
  - <https://github.com/ip332/quarry>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/README.md>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/c/proof_benchmark.c>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/protobuf/proof_benchmark.cpp>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/ip332/quarry/blob/main/CMakeLists.txt>
  - <https://github.com/ip332/quarry/blob/main/CMakePresets.json>
  - <https://github.com/ip332/quarry/blob/main/.github/workflows/ci.yml>
  - <https://github.com/ip332/quarry/actions/runs/35518348476/artifacts/10607347748>
- **Sources the enricher read:**
  - <https://github.com/ip332/quarry>
  - <https://github.com/ip332/quarry#performance--footprint>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/README.md>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/schemas/workload.brd>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/schemas/workload.proto>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/c/proof_benchmark.c>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/cpp/proof_benchmark.cpp>
  - <https://github.com/ip332/quarry/blob/main/benchmarks/protobuf/proof_benchmark.cpp>
  - <https://github.com/ip332/quarry/blob/main/docs/specifications/binary-record-format.md>
  - <https://github.com/ip332/quarry/blob/main/docs/design/c-backend.md>
  - <https://github.com/ip332/quarry/blob/main/docs/design/schema-evolution.md>
  - <https://github.com/ip332/quarry/blob/main/runtime/README.md>
  - <https://github.com/ip332/quarry/blob/main/runtime_c/README.md>
  - <https://github.com/ip332/quarry/blob/main/runtime/CMakeLists.txt>
  - <https://github.com/ip332/quarry/blob/main/runtime_c/CMakeLists.txt>
  - <https://github.com/ip332/quarry/blob/main/CMakeLists.txt>
  - <https://github.com/ip332/quarry/blob/main/compiler/CMakeLists.txt>
  - <https://github.com/ip332/quarry/blob/main/include/quarry/runtime_c/binary_record_v2.h>
  - <https://github.com/ip332/quarry/blob/main/include/quarry/runtime/binary_record_v2.hpp>
  - <https://github.com/ip332/quarry/blob/main/tools/schema-translators/protobuf/README.md>
  - <https://github.com/ip332/quarry/blob/main/release-notes-v0.1.30-rc.3.md>
  - <https://github.com/ip332/quarry/blob/main/Dockerfile>
  - <https://github.com/ip332/quarry/blob/main/.github/workflows/ci.yml>
  - <https://github.com/ip332/quarry/blob/main/docs/development-environment.md>
  - <https://github.com/ip332/quarry/commit/04349e57f227ddd12880b4e65ab2b4fe7d7b06fe>
  - <https://github.com/ip332/quarry/commits/main>
  - <https://github.com/ip332/quarry/releases>
  - <https://github.com/ip332/quarry/issues?q=is%3Aissue>
  - <https://github.com/ip332/quarry/actions/runs/35518348476>
  - <https://github.com/ip332/quarry/actions/runs/35518348476/artifacts/10607347748>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/ip332/quarry`) · [data/wave4/enrich/raw/github_com_ip332_quarry.json](../../../data/wave4/enrich/raw/github_com_ip332_quarry.json) (enrichment confidence 0.8)

</details>
