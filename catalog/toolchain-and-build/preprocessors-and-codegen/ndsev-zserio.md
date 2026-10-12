# Zserio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Preprocessors and code generators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Own-IDL C++/Java/Python serialization framework; bit-packed decode 1.2x-2.6x faster than protoc.

| | |
|---|---|
| **Beats** | protoc |
| **Claimed result** | Zserio-generated C++ decodes faster than protoc-generated C++ (ParseFromString) on all 4 datasets: addressbook 1.478ms vs 1.731ms (\~1.17x), apollo 0.244ms vs 0.641ms (\~2.63x), carsales 1.374ms vs 2.053ms (\~1.49x), simpletrace 0.221ms vs 0.386ms (\~1.75x). The byte-aligned schema variants are faster still: addressbook_align 0.844ms (\~2.05x) and carsales_align 0.925ms (\~2.22x) (derived from page data). |
| **Workload** | For each of 4 schemas (addressbook, Protobuf's own documentation example; apollo; carsales; simpletrace), the harness loads the JSON dataset and serializes it to binary as untimed setup. It then times only deserialization of that blob: protobuf ParseFromString in a loop (100 iterations by default), and zserio's read in the same way. The reported Time is per decode. C++, gcc 11.3.0, Protobuf 3.21.12 vs Zserio 2.10, on an Intel i7-9850H under Linux Mint 21.1. |
| **Metric** | latency |
| **Hardware** | Intel(R) Core(TM) i7-9850H CPU @ 2.60GHz, 64-bit Linux Mint 21.1 |
| **Compiler and flags** | gcc 11.3.0. Optimization flags are not stated on the page; the benchmark scripts default to a CMake Release build (scripts/common_tools.sh). |
| **Adoption** | 153 stars (zserio compiler); 6 stars (companion zserio-protobuf-benchmarks repo) |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/ndsev/zserio) · [benchmark](https://github.com/ndsev/zserio-protobuf-benchmarks) |

## Verdict

Per-decode time (protobuf ParseFromString vs zserio read, pre-serialized blob, JSON load/serialize untimed) on 4 schemas, gcc 11.3.0 CMake-Release build, Intel i7-9850H/Linux Mint 21.1: Zserio beat protoc-generated C++ by 1.17x-2.63x (addressbook 1.478 vs 1.731ms, apollo 0.244 vs 0.641ms, carsales 1.374 vs 2.053ms, simpletrace 0.221 vs 0.386ms); byte-aligned variants reached 2.05x and 2.22x. Benchmark is first-party (same org as Zserio, 6-star companion repo), evidence tier C.

## Use it when

- Designing a new wire format from scratch where blob size matters as much as decode speed
- Multi-language C++/Java/Python project willing to author .zs schemas instead of .proto
- Need built-in SQLite table serialization, JSON debug export, or generic reflection/services without hand-rolling them
- Functional-safety-conscious C++ codebase: C++11 runtime, &gt;600 unit tests, ASan/UBSan clean, 99% line coverage
- Deserialize-heavy workloads (parse once, read many) where a 1.2x-2.6x per-decode win compounds

## Skip it when

- Already invested in protobuf schemas, tooling, or cross-org interop; migration cost likely exceeds the modest measured speedup
- Need protobuf-style forward/backward field compatibility; Zserio's compactness comes partly from dropping field IDs and lengths
- Team can't add a Java-based external compiler step (zserio.jar) to the build
- Need platforms beyond 64/32-bit Linux and 64-bit Windows; macOS/ARM are not in the stated Supported Platforms list
- Want a larger, independently verified speedup: siblings RapidProto (\~7x) and vtprotobuf (\~1.7x) show bigger measured wins over protoc

## How it is fast

Zserio packs fields at the bit level rather than byte level, and its default schemas carry no per-field tag IDs or explicit length prefixes the way protobuf's wire format does, so there is less to scan per field during decode. Byte-aligning fields (the '_align' schema variants) trades blob size for speed by removing bit-shift work, cutting decode time roughly another 40-45% versus the default schema on addressbook and carsales in this benchmark. No SIMD or algorithmic trick is documented; the win is wire-format layout, not a decode algorithm.

## Compared with alternatives

Pick Zserio when you want a full schema framework (SQLite mapping, JSON debug strings, services/pub-sub, one schema for C++/Java/Python) and can move off .proto. Pick RapidProto or vtprotobuf instead if you must keep .proto files and want a bigger measured decode speedup with less schema-language lock-in.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the C++ runtime itself; bundled SQLite3 only if using the SQL-database extension; Java (JRE) needed at build time to run the zserio.jar code generator, not at runtime |
| **Minimum toolchain** | C++11; gcc 7.5.0+ (11.4.0/7.5.0 tested), clang 11.0.0+ (14.0.6/21.1.8 tested), MinGW 7.5.0+, MSVC 2017+; CMake 3.15+ if using the bundled CMake helper |
| **Platforms** | 64-bit Linux, 32-bit Linux, 64-bit Windows per README's Supported Platforms list; macOS/ARM not stated |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | false — different IDL (.zs vs .proto), different generated API, different wire format |

## Gotchas

- Byte-aligned (_align) and delta-packed (_packed) schema variants trade blob size against decode speed in opposite directions; pick per workload
- Compact wire format omits field tags/lengths, so schema-evolution/compatibility rules differ sharply from protobuf's
- Code generated by the zserio compiler inherits the license of the input .zs schema, separate from the BSD-3-Clause runtime license
- Open issue #577 'Consider to optimize C++ serialization performance' (still open) indicates maintainers see further headroom

## Caveats and trade-offs

The timed operation is deserialization only (protobuf ParseFromString vs zserio read of a pre-serialized blob), not a JSON-&gt;binary-&gt;JSON round trip. The README calls itself 'an independent benchmark', but it is run and published by the same organization (Navigation Data Standard e.V.) that builds Zserio. The companion repo was last committed 2025-02-03 and compares old versions (Zserio 2.10, Protobuf 3.21.12). Zserio encodes no field IDs or lengths, trading protobuf's schema-evolution compatibility for size and speed. Speedups are modest (1.17x-2.63x). The zserio repo is BSD-3-Clause plus a note on the licensing of generated code, which is why GitHub reports NOASSERTION.

Zserio's compactness partly comes from omitting Protobuf's per-field IDs and explicit field sizes, trading some forward/backward-compatibility flexibility for size and speed; requires authoring schemas in Zserio's own .zs language rather than .proto

## Maintenance

Active (last commit 2026-09-17, frequent releases); BSD-3-Clause runtime, with generated code separately licensed under the input schema's license.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification B, tier now C.
- **Tier reason:** The benchmark is first-party: the zserio-protobuf-benchmarks repo is by the same NDS org, has 6 stars and is not peer-reviewed. The code (scripts/benchmark.sh), compiler (gcc 11.3.0) and CPU (i7-9850H) are public or stated, but optimization flags are not stated on the page; the scripts only default to a CMake Release build. That makes it C, not B.
- **Verifier notes:** The numbers match the zserio-protobuf-benchmarks README exactly. The record's 'round-trip' description was wrong: benchmark.sh times only ParseFromString, with JSON load and serialize outside the timer. The zserio repo's own benchmarks/README shows identical zserio C++ times but labels them Zserio 3.12 / gcc 11.4.0, a version inconsistency across the org's pages. Metadata is correct: BSD-3-Clause, 153 stars, last commit 2026-09-17, active.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ndsev/zserio-protobuf-benchmarks>
  - <https://github.com/ndsev/zserio-protobuf-benchmarks/blob/master/scripts/benchmark.sh>
  - <https://github.com/ndsev/zserio-protobuf-benchmarks/blob/master/scripts/common_tools.sh>
  - <https://github.com/ndsev/zserio>
  - <https://github.com/ndsev/zserio/blob/master/LICENSE>
  - <https://github.com/ndsev/zserio/blob/master/benchmarks/README.md>
  - <https://github.com/ndsev/zserio/blob/master/scripts/benchmark.sh>
- **Sources the enricher read:**
  - <https://github.com/ndsev/zserio>
  - <https://github.com/ndsev/zserio/blob/master/README.md>
  - <https://github.com/ndsev/zserio/blob/master/compiler/extensions/cpp/README.md>
  - <https://github.com/ndsev/zserio/blob/master/benchmarks/README.md>
  - <https://github.com/ndsev/zserio/blob/master/LICENSE>
  - <https://github.com/ndsev/zserio/issues>
  - <https://github.com/ndsev/zserio-protobuf-benchmarks>
  - <https://github.com/ndsev/zserio-protobuf-benchmarks/blob/master/README.md>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/ndsev/zserio`) · [data/wave2/enrich/raw/github_com_ndsev_zserio.json](../../../data/wave2/enrich/raw/github_com_ndsev_zserio.json) (enrichment confidence 0.68)

</details>
