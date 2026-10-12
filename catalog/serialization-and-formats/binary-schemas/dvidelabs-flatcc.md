# flatcc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> FlatBuffers schema compiler and runtime for pure C. Wire-compatible with Google's flatc, and roughly as fast as its C++ code.

| | |
|---|---|
| **Beats** | Google FlatBuffers (C++) |
| **Claimed result** | Encode: flatcc 626.074 ns/op vs flatc C++ 701.606 ns/op, about 1.12x faster (derived from page data). Decode/traverse: flatcc 28.652 ns/op vs flatc C++ 28.866 ns/op, effectively tied (\~0.7%, derived from page data). The page itself says flatc and flatcc 'are close enough in performance for it not to matter much' and that flatcc's encode edge is 'likely due to less memory allocation'. |
| **Workload** | flatbench schema/dataset (same schema and dataset as Google FPL's FlatBuffers benchmark), 1,000,000 iterations of encode and decode/traverse, optimized (-O3 -DNDEBUG) builds, comparing flatcc's generated C reader/builder against Google FlatBuffers' flatc-generated C++ code. |
| **Metric** | throughput |
| **Hardware** | OS-X, 2.2 GHz Haswell Core i7 (JSON-benchmark section also reports numbers from the same hardware running Ubuntu in VirtualBox) |
| **Compiler and flags** | Compiler not named or versioned: the scripts use the system-default `c++` (CXX) with -O3 -DNDEBUG -std=c++11 for the flatc C++ build and `cc` (CC) with -O3 -DNDEBUG -std=c11 for the flatcc C build (test/benchmark/benchflatc/run.sh, test/benchmark/benchflatcc/run.sh). |
| **Adoption** | 769 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/dvidelabs/flatcc) · [benchmark](https://github.com/dvidelabs/flatcc/blob/master/doc/benchmarks.md) |

## Verdict

Setup: Google's flatbench schema (a container of 3 tables with structs and strings, about 336-344 bytes), 1M iterations, -O3 -DNDEBUG, unnamed system cc/c++, on a 2.2 GHz Haswell Core i7 under OS X. flatcc encoded in 626 ns/op against 702 ns/op for flatc C++ (about 1.12x) and traversed in 28.7 vs 28.9 ns/op (a tie). The C++ baseline is a FlatBuffers 1.0.0 header from 2014 vendored in the repo, rebuilt with a fresh builder every iteration. The repo's Ubuntu run (hardware not stated) has flatcc about 3% slower on encode (531 vs 516 ns) and about 8% faster on decode (27.5 vs 30.0 ns).

## Use it when

- A pure-C codebase (embedded, firmware, C-only services) that needs to read or write FlatBuffers. Users report it working on ESP32/FreeRTOS with newlib and on Arduino.
- Exchanging buffers with services that use Google's flatc in other languages, since flatcc produces the same wire format and flatc-compatible JSON.
- Read-heavy paths: reads are zero-allocation inline accessors with no runtime library. Traversing the benchmark message takes about 29 ns/op.
- Building many small buffers in a loop with one reused builder (`flatcc_builder_reset`), or streaming large buffers page by page through a custom emitter without holding the whole buffer in memory.
- Schema-specific JSON-to-FlatBuffer parsing and printing in C. The generated parser and printer handle a 722-byte message in about 1.2-2.2 µs.

## Skip it when

- A C++ project already using flatc and looking for speed. The results are a wash: encode is about 1.12x faster on the OS X run but about 3% slower on the repo's Ubuntu run, and decode is tied to about 8% faster.
- You need a large serialization speedup over FlatBuffers. This is the same format with the same costs, and only a different wire format can change those.
- Untrusted input where DAG blow-up matters. The verifier rejects cycles and caps nesting at about 100 levels, but unlike Google's verifier it does not limit the number of tables visited. Also, never modify an untrusted buffer in place, even after verifying it.
- You want vectors sorted by key while building. The builder cannot sort; you have to cast the finished buffer to mutable and sort it afterwards (in-place heap sort, not stable), and only on trusted buffers.
- You need a stable API across upgrades. Minor breaking changes to the header API happen occasionally, and generated code must match the include/flatcc version exactly.

## How it is fast

Reader accessors are generated as static inline functions that read fields straight out of the buffer through vtable offsets. They do no allocation, need no library, and let the compiler drop any code you don't use. The typeless builder keeps its internal stacks (vtable stack, data stack, frame stack, patch log) and a hash-table vtable-deduplication cache across builds: `flatcc_builder_reset` reuses that memory instead of freeing it. Output goes to an emitter that writes fixed-size pages (about 2.9 KB) in a ring buffer, not to one growing array. Vtables are clustered at the end of the buffer, and `create` calls and direct array copies skip the stack when no endian conversion is needed. The author attributes flatcc's encode edge to making fewer allocations. In the benchmark code, the C++ side constructs a fresh FlatBufferBuilder on every iteration, while the C side resets its builder.

## Compared with alternatives

Pick flatcc when you need actual FlatBuffers wire compatibility from C. Lite³, Karmem and YaFF report much larger wins over FlatBuffers, but each is its own format and cannot read or write existing FlatBuffers data. ProtoCache and hpp-proto target Protobuf and C++, not FlatBuffers from C.

## Integration

| | |
|---|---|
| **Form** | static lib (runtime libflatccrt, or compile src/runtime/\*.c directly). Reading needs only generated headers plus include/flatcc. The flatcc code generator must be built first (CMake). |
| **Dependencies** | At runtime, none beyond the C runtime library. Building the flatcc tool needs CMake 3.16+ and Ninja or make. |
| **Minimum toolchain** | C11 is the reference (C++11 or C++14 for C++ code that includes the generated headers). A portable header layer supports older compilers, and weekly CI covers GCC 4.4 and 9-15, Clang 5-22, and MSVC. `--pedantic` is not supported on GCC 8+. |
| **Platforms** | Any. Little-endian and big-endian hosts are supported (big-endian since 0.4.0, tested on AIX PowerPC and on s390x via QEMU, but not in regular CI). CI covers Linux x86-64 including 32-bit, macOS on Apple and Intel runners, and Windows with MSVC. |
| **Thread safety** | Reading and verifying are safe from many threads because they mutate no state. A builder is not thread-safe, so use one builder per thread (doc/security.md). |
| **Drop-in for the baseline** | partial: buffers, .fbs schemas and JSON are compatible with Google FlatBuffers, but the generated API is C, not flatc's C++ classes, so calling code has to be rewritten. |

## Gotchas

- The generated headers must come from the same flatcc version as include/flatcc and libflatccrt. A system-installed flatcc package can silently mismatch.
- Builder errors are not checked by default ("no hand holding"). A missing required field asserts in debug builds but writes an incorrect table in release builds. Link libflatccrt_d while developing and run the verifier on your output.
- The verifier requires the buffer to be aligned at its absolute memory address (e.g. 16-byte force_align fields). Plain malloc on 32-bit Windows gives only 8 bytes, so use `flatcc_builder_finalize_aligned_buffer` and `flatcc_builder_aligned_free`.
- Reading and verifying expect a file_identifier by default. Buffers without one, which some other language bindings produce, fail unless you pass a null identifier to the `_with_identifier` variants. If tests segfault, check strict aliasing (`-fno-strict-aliasing`, or `-DPORTABLE_MEM_PTR_ACCESS=0`).

## Known shortcomings

- Marginal win from 2015-2016 numbers: encode about 1.12x, decode tied, and the C++ builder is rebuilt each iteration while the C builder is reset. The repo's own Ubuntu run shows flatcc encode about 3% slower (531 vs 516 ns/op) and decode about 8% faster. No compiler named (system cc/c++, -O3 -DNDEBUG).
- Roughly equal to the baseline, not clearly faster: the C++ side uses a FlatBuffers 1.0.0 header from 2014, rebuilt per iteration, and the maintainer calls the benchmark 'very old' and expects current flatcc to be slightly slower (#382, 2026). Its value is FlatBuffers wire compatibility from C. Use &gt;= 0.6.4 for the schema-parser buffer-overrun fixes; the verifier does not limit DAG blow-up as Google's does.

## Caveats and trade-offs

First-party benchmark (run and published by the flatcc maintainer); the compiler vendor/version is never stated, so it falls short of Tier A. The numbers are old: doc/benchmarks.md content dates from 2015-2016 (last content change 2016-02, moved to its own doc 2017-07) and has not been refreshed against current flatc/flatcc. test/benchmark/README.md says allocation strategies differ (the C++ builder is constructed on every iteration while the C builder is reset), which the page itself credits for flatcc's encode edge. The repo's raw Ubuntu run (test/benchmark/benchout-ubuntu.txt) reverses the encode result: flatcc 531.227 ns/op vs flatc C++ 515.662 ns/op (flatcc \~3% slower), while decode is flatcc 27.539 vs 29.967 ns/op (\~8% faster). Overall the win over FlatBuffers C++ is marginal and platform-dependent.

flatcc generates C (not C++) code and produces a wire-compatible FlatBuffers binary, so it's usable from pure-C projects; the reported encode gain is attributed by the author mainly to reduced memory allocation rather than a fundamentally different algorithm. Only one schema/dataset is benchmarked, shared with Google's own FlatBuffers benchmark, not a broad corpus.

## Maintenance

Actively maintained: v0.6.4 was released 2026-09-16, fixing parser overruns on adversarial schemas that had been reported as CVEs, and there are commits up to 2026-09-25. It is Apache-2.0 and small enough to vendor, and in 2026 the maintainer said the benchmark code is 'very old' and has not been updated (issue #382).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** doc/benchmarks.md compares flatcc's C output with Google flatc-generated C++ on the flatbench schema, and the benchmark code is public (test/benchmark/benchflatc/run.sh, test/benchmark/benchflatcc/run.sh, driven by scripts/benchmark.sh). Flags (-O3 -DNDEBUG) and CPU (2.2 GHz Haswell Core i7) are stated, but the compiler is never named or versioned (scripts just call the system `cc`/`c++`), so this is first-party with partial methodology: C, not A.
- **Verifier notes:** Numbers on the page match the record exactly; the ratios are correctly marked as derived. Downgraded A to C only because the compiler is unnamed (the record's own caveats admitted this); metadata (Apache-2.0, 769 stars, last commit 2026-09-25, not a fork, not archived) all check out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dvidelabs/flatcc/blob/master/doc/benchmarks.md>
  - <https://github.com/dvidelabs/flatcc>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/README.md>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/benchall.sh>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/benchflatc/run.sh>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/benchflatcc/run.sh>
  - <https://github.com/dvidelabs/flatcc/blob/master/scripts/benchmark.sh>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/benchout-osx.txt>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/benchout-ubuntu.txt>
- **Sources the enricher read:**
  - <https://github.com/dvidelabs/flatcc>
  - <https://github.com/dvidelabs/flatcc/blob/master/README.md>
  - <https://github.com/dvidelabs/flatcc/blob/master/doc/benchmarks.md>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/README.md>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/benchout-ubuntu.txt>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/benchflatcc/benchflatcc.c>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/benchflatc/benchflatc.cpp>
  - <https://github.com/dvidelabs/flatcc/blob/master/test/benchmark/benchflatc/flatbuffers/flatbuffers.h>
  - <https://github.com/dvidelabs/flatcc/commits/master/test/benchmark/benchflatc/flatbuffers/flatbuffers.h>
  - <https://github.com/dvidelabs/flatcc/commits/master/test/benchmark/benchout-ubuntu.txt>
  - <https://github.com/dvidelabs/flatcc/blob/master/doc/security.md>
  - <https://github.com/dvidelabs/flatcc/blob/master/CHANGELOG.md>
  - <https://github.com/dvidelabs/flatcc/releases>
  - <https://github.com/dvidelabs/flatcc/blob/master/include/flatcc/flatcc_builder.h>
  - <https://github.com/dvidelabs/flatcc/blob/master/include/flatcc/flatcc_emitter.h>
  - <https://github.com/dvidelabs/flatcc/blob/master/CMakeLists.txt>
  - <https://github.com/dvidelabs/flatcc/blob/master/.github/workflows/weekly.yml>
  - <https://github.com/dvidelabs/flatcc/issues>
  - <https://github.com/dvidelabs/flatcc/issues/382>
  - <https://github.com/dvidelabs/flatcc/issues/272>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/dvidelabs/flatcc`) · [data/wave4/enrich/raw/github_com_dvidelabs_flatcc.json](../../../data/wave4/enrich/raw/github_com_dvidelabs_flatcc.json) (enrichment confidence 0.85)

</details>
