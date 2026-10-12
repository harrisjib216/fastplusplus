# libbson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> MongoDB's C library for building and iterating BSON; in one third-party C shootout it round-trips faster than cJSON on 4 of 5 payloads.

| | |
|---|---|
| **Beats** | cJSON (also jansson, json-c and parson as JSON serializers; cross-format comparison) |
| **Claimed result** | No claim by the project; numbers come from the third-party GLD.SerializerBenchmark C results (run 2026-09-29-182101, default paired-IQR k=1.5 statistics, mean ns). Ratios are derived from page data. Round trip at 100 instances, libbson ns vs cJSON ns: message 157,288 vs 338,948 (libbson 2.15x faster), document 546,018 vs 855,914 (1.57x), event 324,854 vs 502,001 (1.55x), telemetry 962,634 vs 3,078,221 (3.2x), but strings 1,168,630 vs 669,472 (cJSON 1.75x faster). Against jansson libbson is 1.97x to 3.28x faster on the same four payloads and equal on strings (1,168,630 vs 1,165,048); against json-c 2.13x to 2.81x faster on four payloads and 1.44x slower on strings; against parson 2.25x to 3.94x faster on four payloads and 1.52x slower on strings. Against yyjson libbson is slower on four of five payloads (document 546,018 vs 407,197; telemetry 962,634 vs 357,412) and only 1.06x faster on message. Against binary formats it is slower everywhere: mpack is 2.0x to 8.5x faster (document 191,878 ns) and libcbor-stream 1.4x to 5.5x faster. |
| **Workload** | Per-operation mean serialize + deserialize time (ns) of five fixed payload types (message, document, telemetry, strings, event) built with bson_append_\* and read back with bson_iter_\* versus the same payloads written and parsed by C JSON libraries, in one shared C harness, at 100 instances per payload (about 15 to 60 KB of BSON) and at 1 instance. |
| **Metric** | latency |
| **Hardware** | 12th Gen Intel Core i7-12800H (20 logical cores, up to 4700 MHz, governor powersave), 32 GB RAM, Linux 6.8.0-138-generic x86_64 (environment block of the result file; git state of the run marked dirty). |
| **Compiler and flags** | gcc (Ubuntu 11.4.0-1ubuntu1\~22.04.3) 11.4.0; harness c/CMakeLists.txt defaults to Release and adds add_compile_options(-O2 -Wall -Wno-unused-function), so in-tree cJSON compiles at -O2; libbson taken from mongo-c-driver 1.27.5, built by c/scripts/fetch-and-build-deps.sh with CMake -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS=-Wno-error, target bson_static; cJSON v1.7.19, jansson v2.15.1 (CMake Release), json-c 0.15 from the system package (per c/third_party/VERSIONS.md and the run's serializer list). |
| **Adoption** | 347 stars (archived standalone repo); the maintained copy is src/libbson in mongodb/mongo-c-driver (883 stars, last commit 2026-10-06) |
| **Last commit** | 2017-12-20 |
| **Links** | [repository](https://github.com/mongodb/mongo-c-driver) · [benchmark](https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/dashboard/public/data/c_latest.json.gz) |

## Verdict

GLD.SerializerBenchmark's C suite (run 2026-09-29-182101, gcc 11.4.0, i7-12800H on the powersave governor, IQR-filtered means) timed libbson 1.27.5 from mongo-c-driver against C JSON libraries on five fixed payloads: at 100 instances libbson's serialize plus deserialize was 1.55x to 3.2x faster than cJSON 1.7.19 on message, document, telemetry and event but 1.75x slower on strings; all rows passed the suite's fidelity check (1.0). The project makes no speed claim, the comparison is cross-format (BSON vs JSON text), and libbson is slower than every MessagePack, protobuf and FlatBuffers row in the same run.

## Use it when

- You already talk to MongoDB or store BSON and need a C serializer that matches the server's format byte for byte.
- You want a self-describing binary document format with typed fields (int64, decimal128, dates, binary) instead of JSON text, and can afford larger output.
- Write-heavy C code that today formats JSON with cJSON, json-c, jansson or parson: in the GLD shootout libbson serializes 1.5x to 10x faster than cJSON on message, document, telemetry and event (derived from page data).
- You need in-place, allocation-free iteration of received documents (bson_init_static + bson_iter_t) rather than building a tree.

## Skip it when

- You want the fastest C serializer of any format: in the same run mpack, msgpack-c, flatcc, the protobuf rows and libcbor's streaming encoder all beat libbson on every payload.
- You need the fastest JSON: yyjson round-trips faster than libbson on document, telemetry, strings and event (for example telemetry 357,412 ns vs 962,634 ns at 100 instances).
- Payloads dominated by strings or by arrays read element-by-element: libbson lost to cJSON, json-c and parson on the strings payload (1,168,630 ns vs cJSON 669,472 ns).
- Compactness matters: BSON stores array indexes as decimal key strings and fixed-width integers, so output was 1.2x to 1.7x larger than CBOR or MessagePack and larger than JSON text on three payloads.
- Out-of-memory handling matters: libbson's own docs say it calls abort() on OOM rather than returning an error.

## How it is fast

A bson_t carries a 120-byte inline buffer, so small documents are built without any heap allocation; appends memcpy little-endian scalars into one contiguous buffer and back-patch the length prefix. Reading is zero-copy: bson_init_static wraps an existing buffer and bson_iter_t walks it in place with no allocation, returning pointers into the buffer for strings and sub-documents. Against text JSON the gain comes from skipping number formatting/parsing and string escaping, not from any clever search; key lookup (bson_iter_find) is a linear scan.

## Compared with alternatives

Pick libbson over libcbor or flatcc only when the consumer is MongoDB or another BSON reader; on raw speed and size libcbor's streaming encoder (1.4x to 5.5x faster round trip in the same run) and flatcc (document 75,146 ns vs 546,018 ns) both win.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (built from mongo-c-driver with CMake; libbson can be built alone, target bson_static / bson::static in 2.x) |
| **Dependencies** | none beyond libc (part of the mongo-c-driver source tree; libmongoc is optional) |
| **Minimum toolchain** | C99 (CMAKE_C_STANDARD 99 by default), CMake 3.15+ |
| **Platforms** | cross-platform C: Linux, macOS, Windows (MSVC) and other POSIX systems; little- and big-endian handled in the byte-order layer |
| **Thread safety** | not documented as a guarantee for shared objects; bson_t and bson_iter_t are plain caller-owned structs with no internal locking, so share them across threads only with external synchronization; the global allocator vtable (bson_mem_set_vtable) is process-wide |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws behind the numbers: the GLD wrapper (c/src/serializers/ser_libbson.c) reads array element i with bson_iter_init_find on the key "i", a linear scan from the array start, and copies every scalar element into a freshly bson_init'ed wrapper document that is then destroyed; the writer formats every array key with snprintf instead of libbson's bson_uint32_to_string table or bson_array_builder_t, and writes every integer as INT64. cJSON's reader also walks its linked list per index (cJSON_GetArrayItem), so the index pattern is shared, but the wrapper documents and key parsing are libbson-only costs that probably explain the strings loss.
- BSON arrays are documents keyed "0", "1", ...; there is no O(1) indexing, so iterate once with bson_iter_next instead of looking up indexes.
- Small documents live in the bson_t's inline buffer and spill to the heap when they grow, so bson_destroy() is required even for stack-declared documents; bson_init_static wrappers must not outlive the buffer they point into.
- Security fixes keep landing: CVE-2025-0755 (bson_append_\* could write past the buffer near the INT32_MAX size limit) was fixed in 1.27.5, the version benchmarked; CVE-2024-6381 and CVE-2024-6383 hit bson_strfreev and bson_string_append (per secondary CVE aggregators, not NVD). The 2.x line removed bson_as_json and renamed the CMake package and targets.

## Known shortcomings

- Tier A on leo-gan/GLD.SerializerBenchmark c_latest.json.gz (gcc 11.4.0 -O2, i7-12800H), but the comparison is cross-format against cJSON, jansson and json-c (outside the category's baselines) and libbson is slower than every msgpack-c, mpack, protobuf and flatcc row in all ten cells; the harness reader slows libbson arrays (quadratic element lookup); the listed repo was archived in 2020 and the measured code is mongo-c-driver 1.27.5 (repo_url override).
- Enricher (GLD ser_libbson.c): element i is read by bson_iter_init_find on key 'i' (linear scan), each scalar element is copied into a new bson_init wrapper document, the writer snprintf's every array key instead of using the bson_uint32_to_string table or bson_array_builder_t, and all ints are written as INT64; cJSON's reader also walks its list per index, so the index pattern is shared but the wrapper documents and key parsing are libbson-only costs (probably behind the strings loss). Cross-format comparison; slower than yyjson, mpack, msgpack-c, protobuf, flatcc and libcbor-stream; measured 1.27.5 (now 2.5.6 and 1.30.13); CVE-2025-0755 fixed in 1.27.5, CVE-2024-6381/6383 earlier; the listed repo is archived and the live code is mongo-c-driver src/libbson.

## Caveats and trade-offs

Weak, indirect evidence. Nobody claims libbson is faster than a named baseline; the only comparison is a third-party multi-format shootout in which libbson beats the C JSON libraries on four of five payloads but loses to yyjson, mpack and libcbor, and loses to cJSON, json-c and parson on the strings payload. The comparison is cross-format (BSON vs JSON text) and off the category's baselines: in the same run libbson is slower than every MessagePack, Protobuf and FlatBuffers row (msgpack-c, mpack, Google protobuf and flatcc, plus the protobuf-c and nanopb rows, which time a shared in-tree wire codec) on all five payloads at both 100 and 1 instance, for example document at 100 instances 546,018 ns vs msgpack-c 208,797, Google protobuf 226,492 and flatcc 75,146 (derived from page data); among binary rows only ion-c is slower, and only on message, document and event. It says nothing about libbson against any other BSON implementation. The harness reader (c/src/serializers/ser_libbson.c) is pessimized for libbson: enter_elem finds each array element by its decimal key with bson_iter_init_find (a linear scan from the array start, so quadratic in array length) and copies every scalar array element into a freshly bson_init'ed wrapper document that is then destroyed; this probably explains the strings loss (decode 909,025 ns vs cJSON 452,216) and understates libbson. The writer appends every integer as INT64. Builds differ: libbson comes from mongo-c-driver's own CMake Release build (bson_static, -Wno-error), while cJSON is compiled inside the harness, where add_compile_options(-O2) follows CMake's Release flags. The listed repository mongodb/libbson is archived (2020-10-13) with last commit 2017-12-20 (version 1.9.0); the benchmark used libbson from mongo-c-driver 1.27.5, so the measured code is not in the listed repository (use https://github.com/mongodb/mongo-c-driver, src/libbson, for the live code). Host used the powersave governor; the run's git tree (commit 7cf1c19) was dirty, most likely with the Ion serializers committed next as f040bcc (ion-c appears in the run's serializer list and f040bcc is the only later change under c/src/serializers), so the libbson and cJSON wrappers at HEAD are what ran. The mongodb/mongo-c-driver-performance suite measures libbson alone with no baseline column (see data/seeds/no_evidence/w6-mine-a.json). The dashboard on github.io is blocked here and was not opened.

BSON output is 1.2x to 1.7x larger than CBOR or MessagePack for the same payload (document at 100 instances: 57,612 bytes vs 34,026 bytes) and larger than JSON text on document, event and strings (document 57,612 vs 45,878 bytes); the format exists for MongoDB's traversable on-disk layout, not for compactness. API is bson_append_\* and bson_iter_\* (iterator-based, no DOM).

## Maintenance

The listed mongodb/libbson repository has been archived since 2020-10-13 (last code 1.9.0, 2017); the maintained libbson lives in mongodb/mongo-c-driver under src/libbson (Apache-2.0, 883 stars, commits as recent as 2026-10-09, releases 2.5.6 and 1.30.13), with bugs tracked in MongoDB's CDRIVER JIRA rather than GitHub issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** c_latest.json.gz (run 2026-09-29-182101) carries every quoted iqr_1.5 mean (libbson 157,288 / 546,018 / 962,634 / 1,168,630 / 324,854 ns vs cJSON 338,949 / 855,914 / 3,078,222 / 669,472 / 502,002 ns at 100 instances) plus gcc 11.4.0 and the i7-12800H; the harness code (c/src/serializers/ser_libbson.c, ser_cjson.c, c/CMakeLists.txt -O2, c/scripts/fetch-and-build-deps.sh) is public, so A holds as reproducible evidence even though the comparison itself is weak and cross-format.
- **Verifier notes:** All quoted numbers and ratios check out against the result file (cJSON figures differ by 1 ns from rounding). Shortcomings to record: cross-format and off-category comparison (slower than every msgpack-c, mpack, protobuf and flatcc row on all ten cells), harness reader pessimizes libbson arrays (quadratic element lookup, per-scalar wrapper docs), loses to cJSON/json-c/parson on strings and to yyjson on 4 of 5, listed repo archived since 2020 with the measured code in mongo-c-driver; consider a repo_url override to https://github.com/mongodb/mongo-c-driver (Apache-2.0, 883 stars). Metadata confirmed (Apache-2.0, 347 stars, archived, last commit 2017-12-20).
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-62 (wave 4); enricher (wave 4)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/dashboard/public/data/c_latest.json.gz>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/CMakeLists.txt>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/third_party/VERSIONS.md>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/scripts/fetch-and-build-deps.sh>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/commits/master/c>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/commits/master/c/src/serializers>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/commits/master/dashboard/public/data/c_latest.json.gz>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_libbson.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_cjson.c>
  - <https://github.com/mongodb/libbson>
  - <https://github.com/mongodb/libbson/commits/master>
  - <https://github.com/mongodb/mongo-c-driver>
- **Sources the enricher read:**
  - <https://github.com/mongodb/libbson>
  - <https://github.com/mongodb/mongo-c-driver>
  - <https://github.com/mongodb/mongo-c-driver/commits/master/src/libbson>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/README.rst>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/NEWS>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/NEWS>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/src/bson/bson.h>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/src/bson/bson-types.h>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/src/bson/bson-keys.c>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/doc/index.rst>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/doc/bson_t.rst>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/doc/bson_iter_t.rst>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/doc/bson_iter_find.rst>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/doc/bson_iter_init_find.rst>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/doc/bson_array_builder_t.rst>
  - <https://raw.githubusercontent.com/mongodb/mongo-c-driver/HEAD/src/libbson/doc/bson_memory.rst>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/dashboard/public/data/c_latest.json.gz>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_libbson.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_cjson.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_yyjson.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/v2_codec.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/v2_codec.h>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/CMakeLists.txt>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/scripts/fetch-and-build-deps.sh>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/third_party/VERSIONS.md>
  - WebSearch: libbson CVE mongo-c-driver vulnerability (snippets from tracker.debian.org, cpe.gcve.eu, watchstack.io)
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/mongodb/libbson`) · [data/wave4/enrich/raw/github_com_mongodb_libbson.json](../../../data/wave4/enrich/raw/github_com_mongodb_libbson.json) (enrichment confidence 0.45)

</details>
