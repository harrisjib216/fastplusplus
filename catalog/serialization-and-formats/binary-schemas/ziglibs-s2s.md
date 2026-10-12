# s2s (ziglibs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Single-file Zig binary serializer driven by comptime type reflection; 1.1-2x faster round trips than zig-protobuf in one benchmark.

| | |
|---|---|
| **Beats** | Protocol Buffers (Arwalk/zig-protobuf 5.0.0, generated from the suite's shared benchmark_v2.proto); MessagePack (serde.zig 1.2.1 backend) also compared |
| **Claimed result** | Serialize+deserialize time in run 2026-09-14-134825, 100-instance cells: 1.13-1.99x faster than zig-protobuf on all 5 fixtures in stream mode over all trials (document 1.88x, event 1.43x, message 1.43x, strings 1.13x, telemetry 1.99x). With bytes mode and the dashboard's default IQR filter it is 1.12-2.02x, and single-instance cells give 1.21-2.09x. Against serde.zig's MessagePack backend: 1.4-2.2x faster on 4 of 5 fixtures, slower on strings (0.92x). (all derived from page data) The Cap'n Proto '12.9-17.9x' figure is dropped: that row calls the C++ runtime through a C bridge compiled with no -O flag. |
| **Workload** | Serialize+deserialize time on 5 shared fixtures (document, event, message, strings, telemetry) from the suite's common IDLs. Single-instance and 100-instance cells, bytes and stream modes, 100 reps per cell with 1 warmup, in the GLD.SerializerBenchmark Zig runner |
| **Metric** | latency |
| **Hardware** | 12th Gen Intel Core i7-12800H (20 logical cores, powersave governor), 32 GB RAM, Ubuntu 22.04, Linux 6.8.0-138 |
| **Compiler and flags** | Zig 0.16.0, zig build -Doptimize=ReleaseFast (zig/scripts/run-benchmarks.sh); the Cap'n Proto C bridge is built by system c++ (g++ 11.4) with no -O flag |
| **Adoption** | 165 stars |
| **Last commit** | 2026-05-03 |
| **Links** | [repository](https://github.com/ziglibs/s2s) · [benchmark](https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/dashboard/public/data/stats_zig_latest.json.gz) |

## Verdict

In GLD.SerializerBenchmark run 2026-09-14-134825 (Zig 0.16.0 ReleaseFast, i7-12800H laptop on the powersave governor, Ubuntu 22.04), s2s 0.0.1's serialize+deserialize time for 100-instance batches beat Arwalk/zig-protobuf 5.0.0 on all five fixtures: document 1.88x, event 1.43x, message 1.43x, strings 1.13x, telemetry 1.99x (stream mode, all trials); single-instance cells gave 1.2-2.25x. This was one run, and protobuf's timed decode also copies the generated message into the suite struct. Serializing alone, s2s was slower than protobuf on 'strings' (36.8 vs 27.2 us per 100 instances).

## Use it when

- Both writer and reader are Zig programs built from the same type definitions, for example Zig-to-Zig IPC, caches, save files or messages inside a Zig-only system.
- Record-shaped data with ints, floats, enums, nested structs and slices of structs. On the suite's document, event, message and telemetry fixtures the serialize+deserialize round trip was 1.4-2.0x faster than zig-protobuf.
- You want no .proto file and no codegen step, because the Zig struct is the schema.
- You want cheap detection of mismatched types: deserialize rejects a stream whose 8-byte type hash differs, with error.UnexpectedData, before it reads any fields.
- Byte-heavy payloads ([]const u8, [N]u8), which s2s copies in bulk instead of element by element.

## Skip it when

- Anything a non-Zig program must read, and long-lived or public formats. There is no spec beyond s2s.zig, the version is 0.0.1, the benchmark suite's docs call it 'not a public interchange standard', and in issue #7 the author says they want to change the format in a breaking way.
- You need schema evolution. Adding, removing or retyping a field changes the type hash, so older data fails to decode with error.UnexpectedData. There are no defaults, optional fields or version numbers.
- Wire size or many small strings matter. Fixed-width integers and a u64 length on every slice made payloads 1.14-1.72x larger than protobuf's. On the 'strings' fixture s2s was only 1.13x faster than protobuf overall, slower to serialize, and slower than zig-flatbuffers, msgpack.zig and serde.zig's MessagePack backend.
- Untrusted input without a bounded or arena allocator. Slice lengths are read as u64 and passed straight to allocator.alloc, and fields already decoded are not freed when a later field fails.
- Types it cannot handle: cyclic or shared graphs, sentinel-terminated slices ([:0]const u8), untagged or extern unions, many-item and C pointers, and custom per-type encoding (no hooks; issue #7 has been open since 2023).

## How it is fast

The encoder and decoder are specialized at compile time. serializeRecursive/recursiveDeserialize switch on @typeInfo(T) and unroll struct fields with `inline for`, so there are no field tags, names, varints or runtime reflection: each field is written as fixed-width little-endian bytes in declaration order and decoded in place into the destination struct. u8 slices and arrays take a fast path, one writeAll/readSliceAll. The only framing is an 8-byte comptime FNV-1a-64 hash of the type's structure, a u64 length before each slice, and a 1-byte flag or tag for optionals and unions. The price is size: in the benchmark, payloads were 1.14-1.72x larger than protobuf's.

## Compared with alternatives

No other Zig library is catalogued in this category. The siblings are Rust, Go, C#, C++, Java, Python and Nim libraries, so none of them is an option in a Zig codebase. Pick s2s when both ends are Zig and you want no schema or codegen step; if another language must read the bytes, use one of the cross-language schema formats listed or stay on protobuf.

## Integration

| | |
|---|---|
| **Form** | module (one source file, s2s.zig; add it as a Zig package, where build.zig exposes module 's2s', or vendor the file) |
| **Dependencies** | none (Zig std only) |
| **Minimum toolchain** | Zig 0.15.0 (build.zig.zon minimum_zig_version). PR #23 made it compile on 0.16-dev while keeping 0.15.0 support, and the benchmark used Zig 0.16.0. The code uses the std.Io.Reader/Writer API, so older Zig needs an older commit. |
| **Platforms** | Any Zig target (pure Zig, no architecture-specific code). The wire format is explicitly little-endian and usize is always encoded as u64; a usize value too large for a 32-bit target fails to decode with error.UnexpectedData. |
| **Thread safety** | Not documented. The API is stateless free functions with no global state, so concurrent calls on separate streams need no locking. |
| **Drop-in for the baseline** | no |

## Gotchas

- The type hash covers field types and order but not field names. Renaming fields, or swapping two fields of the same type, is not detected, and old data then decodes into the wrong fields without any error.
- Each top-level serialize() call writes its own 8-byte hash and calls flush() on the writer. Serializing many small records one call at a time costs 8 bytes and a flush per record, so wrap them in a slice or struct instead.
- free() takes a pointer (`value: *T`) in s2s.zig, but the README shows `value: T`. Also, deserializeAlloc does not clean up partial allocations on error, so decode into an ArenaAllocator when input may be malformed.
- Error-set and error-union fields are nominally supported, but their tests have been disabled as failing since 2024 (enable_failing_test = false). Odd-width integers are widened to the next whole byte (a u1 takes a full byte).

## Known shortcomings

- Unsafe for untrusted input: slice lengths go straight to allocator.alloc unbounded, and deserializeAlloc leaks already-allocated fields on failure. The type hash ignores field names, so renamed or swapped same-type fields decode silently into the wrong fields; no schema evolution. Payloads are 1.14-1.72x larger than protobuf's, and serialize alone loses to protobuf on 'strings'. Version 0.0.1; the author plans a breaking format change (#7). zig-flatbuffers and msgpack.zig match or beat it on some fixtures in the same suite.

## Caveats and trade-offs

Third-party suite, but not a well-known one: the repo dates from 2015 (not first published 2026-09), has 25 stars, and added its Zig runner on 2026-08-29. This was a single-session run (the suite's own claim level L1) on a laptop CPU under the powersave governor. Protobuf's timed decode also converts the generated message back into the suite struct, while s2s decodes straight into it. s2s payloads are about 1.1-1.7x larger than protobuf's, and s2s serialize is slower than protobuf's on 'strings'. s2s loses to zig-flatbuffers on strings and telemetry, to msgpack.zig on strings (about a tie elsewhere), and to the suite's in-tree comptime-bin encoder on every fixture. The Cap'n Proto row is not a fair baseline because of the unoptimized C bridge and extra copies. s2s is a Zig-only format; its README calls it complete only for the 'trivial' case.

Zig-only, no IDL/schema, no versioning, not intended as a public interchange format (per author's own description); loses to FlatBuffers and to lalinsky/msgpack.zig on some of the 5 workloads even though it beats Protobuf/Cap'n Proto/serde.zig-msgpack on all of them

## Maintenance

Nearly every commit since 2023 is a port to a new Zig version (latest 2026-04-30, targets Zig 0.15-0.16). It is still versioned 0.0.1, and the benchmark author's fairness-review request (issue #25) has had no reply. MIT-licensed, a single \~870-line file with no dependencies, easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgrade from B. GLD.SerializerBenchmark publishes the harness: zig/src/extra.zig (encodeS2s/decodeS2s), zig/src/proto_ser.zig, zig/src/runner.zig and zig/scripts/run-benchmarks.sh, which builds with 'zig build -Doptimize=ReleaseFast'. It also publishes the run's environment in dashboard/public/data/zig_latest.json.gz: Zig 0.16.0 and a 12th Gen Intel Core i7-12800H. The run's dirty tree only held the dependency-pin bump committed with the data (4a51f66e). So code, compiler, flags and CPU model are all public for the s2s-vs-protobuf comparison.
- **Verifier notes:** The record's ratios do appear in the data file, but only for one unstated slice (100-instance, stream mode, all trials); I made the claim explicit and dropped the Cap'n Proto comparison because of the -O0 bridge. The record gave hardware as null, but zig_latest.json.gz has the CPU model, so I upgraded to A. The serde.msgpack adapter path changed after this run (#167), so that secondary comparison may shift on the next run. The s2s and protobuf paths have not changed since.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/leo-gan/GLD.SerializerBenchmark>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/docs/zig/index.md>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/dashboard/public/data/stats_zig_latest.json.gz>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/dashboard/public/data/zig_latest.json.gz>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/zig/scripts/run-benchmarks.sh>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/zig/build.zig>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/zig/src/proto_ser.zig>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/zig/src/extra.zig>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/zig/src/capnp/capnp_bridge.cpp>
  - <https://leo-gan.github.io/GLD.SerializerBenchmark/zig/>
  - <https://github.com/ziglibs/s2s>
- **Sources the enricher read:**
  - <https://github.com/ziglibs/s2s>
  - <https://github.com/ziglibs/s2s/blob/master/README.md>
  - <https://github.com/ziglibs/s2s/blob/master/s2s.zig>
  - <https://github.com/ziglibs/s2s/blob/master/build.zig>
  - <https://github.com/ziglibs/s2s/blob/master/build.zig.zon>
  - <https://github.com/ziglibs/s2s/issues>
  - <https://github.com/ziglibs/s2s/pulls>
  - <https://github.com/ziglibs/s2s/commits/master>
  - <https://github.com/ziglibs/s2s/issues/25>
  - <https://github.com/ziglibs/s2s/issues/15>
  - <https://github.com/ziglibs/s2s/issues/7>
  - <https://github.com/ziglibs/s2s/issues/3>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/zig/src/extra.zig>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/zig/src/data.zig>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/zig/src/proto_ser.zig>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/docs/zig/index.md>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/dashboard/public/data/stats_zig_latest.json.gz>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/blob/master/dashboard/public/data/zig_latest.json.gz>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/ziglibs/s2s`) · [data/wave4/enrich/raw/github_com_ziglibs_s2s.json](../../../data/wave4/enrich/raw/github_com_ziglibs_s2s.json) (enrichment confidence 0.78)

</details>
