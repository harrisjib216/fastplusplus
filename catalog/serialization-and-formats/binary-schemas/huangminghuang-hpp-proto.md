# hpp-proto

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Wire-compatible C++23 Protobuf implementation; non-owning mode decodes and builds+serializes 1.5-1.9x faster than libprotobuf arenas.

| | |
|---|---|
| **Beats** | Protobuf (Google's C++ libprotobuf) |
| **Claimed result** | Linux numbers from the README prose (i9-11950H, gcc 13.3.0, protobuf 33.2). Deserialize, google arena vs hpp-proto non-owning: proto2 210 ns vs 141 ns (\~1.5x), proto3 252 ns vs 160 ns (\~1.6x). Deserialize regular: proto2 215 vs 210 ns, proto3 251 vs 212 ns. repeated_packed: google regular 4164 ns vs hpp-proto regular 2624 ns (\~1.6x); google arena 4263 ns vs hpp-proto non-owning 2550 ns. Set_message+serialize, google arena vs hpp-proto non-owning: proto2 186 vs 99.6 ns (\~1.9x), proto3 223 vs 121 ns (\~1.8x); regular: proto2 185 vs 139 ns, proto3 219 vs 148 ns. Google is faster on serialize-only: proto2 64.5 vs 85.1 ns, proto3 98.8 vs 102 ns. (Ratios derived from page data.) |
| **Workload** | Google Benchmark (benchmarks/benchmark.cpp) runs deserialize, set_message, serialize-only and set_message+serialize. It uses GoogleMessage1 (proto2 and proto3) from the protobuf v3.6.0 benchmarks.proto schema, with a single \~220-byte message filled in code by set_message_google, not the v3.6.0 dataset files. There is also a 'big' variant with 512- and 2048-byte strings, and a 1000-element packed repeated uint64 message with random values. Google protobuf runs in regular and arena modes; hpp-proto runs in regular and non-owning modes. |
| **Metric** | latency |
| **Hardware** | Apple M1 Pro (Mac); 11th Gen Intel Core i9-11950H @ 2.60GHz (Linux) |
| **Compiler and flags** | Apple clang 17.0.0 (Mac); gcc 13.3.0 (Linux); Google protobuf 33.2. Optimization flags and build type are not stated for the published results. The ReadMe run command sets no CMAKE_BUILD_TYPE; CMakePresets.json has a 'benchmark' preset with CMAKE_BUILD_TYPE=Release, but it is not tied to the published numbers. |
| **Adoption** | 43 stars |
| **Last commit** | 2026-08-03 |
| **Links** | [repository](https://github.com/huangminghuang/hpp-proto) · [benchmark](https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/ReadMe.md) |

## Verdict

This is a first-party Google Benchmark run against Google protobuf 33.2 on an i9-11950H with gcc 13.3.0, plus an M1 Pro with Apple clang 17; the build flags are not stated. Decoding one \~220-byte GoogleMessage1 takes 141/160 ns (proto2/proto3) in hpp-proto's non-owning mode vs 210/252 ns for Google's arena mode, and set+serialize takes 99.6/121 vs 186/223 ns. Owning-mode decode is near parity (proto2 210 vs 215 ns), and Google wins serialize-only (64.5 vs 85.1 ns).

## Use it when

- You exchange protobuf messages with existing libprotobuf or gRPC peers and want lower per-message C++ latency on small messages (the benchmark uses a \~220-byte GoogleMessage1) without changing the wire format.
- Hot decode paths where the input buffer outlives the parsed message: non_owning_traits with a std::pmr::monotonic_buffer_resource decode in 141 ns vs 210 ns for Google arena (proto2, i9-11950H).
- Build-then-send pipelines that fill a message and serialize it once: set+serialize takes 139 vs 185 ns (proto2, regular) and 99.6 vs 186 ns in non-owning vs arena mode.
- Large packed numeric arrays or proto3 messages with long strings: a 1000-element packed uint64 decodes in 2511 vs 3852 ns CPU, and the raw Linux output shows proto3 decode with 512/2048-byte strings at 518 ns vs 1007 ns.
- Binary-size-constrained or embedded targets: the Linux encode/decode test program is 111,816 bytes, against 3,829,824 for static libprotobuf and 1,748,216 for libprotobuf-lite.

## Skip it when

- Codebases that cannot move to C++23: it needs GCC 13+ or Clang 19+ (MSVC is also in CI) and CMake 3.25+.
- Workloads dominated by re-serializing messages that are already built. Google wins serialize-only: proto2 64.5 vs 85.1 ns on the i9, and 75.1 vs 132 ns on the M1 Pro.
- When you cannot guarantee buffer and arena lifetimes. Owning-mode decode is roughly even with Google on the small message (proto2 210 vs 215 ns), and the headline gains need view semantics that Google's arena mode does not use.
- Large libprotobuf codebases that rely on the accessor API, Google-style reflection or Arena semantics: the generated types are different, so migrating means rewriting call sites. Text format is not documented.
- Risk-averse production: the project is pre-1.0 (latest tag is the v1.0.0-beta.1 pre-release) with 43 stars, and fuzzing found a heap-buffer-overflow and a crash in the parser as recently as July and August 2026.

## How it is fast

Messages are plain structs. Field-number-to-member dispatch uses a consteval two-level 'masked lookup table', and varints go through the branch-predicted shift-mix decoder adapted from protobuf's varint_shuffle.h. Most of the headline gain comes from non_owning_traits: string, bytes and repeated fields become string_view/span views backed by the input buffer or a caller std::pmr arena, which removes per-field heap allocations and copies. Packed varint arrays are pre-sized by popcounting terminator bytes 8 at a time. The parser walks 16-byte overlapping 'slope' regions, or a caller-promised padded_input, so inner loops skip bounds checks; proto3 UTF-8 checks call simdutf's is_utf8, and serialization is two-pass with an external size cache in a 1 KiB stack-backed monotonic buffer.

## Compared with alternatives

Pick hpp-proto when you must keep the protobuf wire format and .proto schemas (existing peers, gRPC) and want a faster, smaller C++ codec. ProtoCache (a flat format for protobuf schemas, 132 vs 2620 ns decode+traverse), SBE and Apache Fory report bigger wins, but they use their own encodings, so every peer has to change.

## Integration

| | |
|---|---|
| **Form** | header-only core (hpp_proto::hpp_proto) plus the protoc-gen-hpp plugin built from source; optional compiled hpp_proto::dynamic_message library |
| **Dependencies** | is_utf8 (simdutf) for UTF-8 validation; glaze for JSON; protoc for code generation. CPM fetches missing dependencies unless CPM_LOCAL_PACKAGES_ONLY=ON. gRPC is needed only for the adapter. |
| **Minimum toolchain** | C++23 (README: Clang 19+ or GCC 13+), CMake 3.25+, protoc. CI also builds with MSVC and MinGW, and tests C++26 with Clang 22. |
| **Platforms** | Portable C++. CI covers Linux x86-64 (GCC 13/14, Clang 20/22), macOS (macos-latest) and Windows (MSVC, MinGW); benchmarks were run on x86-64 and an Apple M1 Pro. No ISA is required: on x86-64, popcnt is detected at runtime. |
| **Thread safety** | Not documented. The codec is free functions over caller-owned messages and buffers, and by default each call keeps its temp size cache on the stack. |
| **Drop-in for the baseline** | partial — it uses the same .proto files, protoc and wire format (binary and ProtoJSON), so it interoperates with libprotobuf peers. The generated C++ API (public-member structs, Traits templates, free read_binpb/write_binpb) is different, so application code must be rewritten; namespace_prefix lets both libraries coexist in one binary. |

## Gotchas

- non_owning_traits messages hold string_view/span into the input buffer or the alloc_from memory resource, and both must outlive the message. Map fields become key/value spans that are not deduplicated (the last duplicate wins). Mixing owning string_t with view-typed repeated_t leaks, because destructors never run.
- padded_input requires at least 16 readable bytes past the payload, and the first padding byte must be 0. Passing it without those guarantees defeats the parser's bounds-check-free loops.
- read_binpb/read_json report errors through a status and do not catch std::bad_alloc from containers. A failed parse may leave the target message partly modified.
- The README's FetchContent snippet pins the v1.0.0-beta.1 commit (2026-01-02). That commit predates two ClusterFuzzLite-found fixes: a heap-buffer-overflow in segmented packed-varint decoding (PR #199, merged 2026-07-21) and a non-owning unknown-field crash (PR #200, 2026-08-03). Pin a newer commit.

## Known shortcomings

- Google protobuf wins serialize-only (Linux 64.5 vs 85.1 ns; Apple M1 Pro 75.1 vs 132 ns, proto2). Owning-mode decode is about parity (210 vs 215 ns); the 1.5-1.9x headline needs non-owning view semantics, and the non-owning set_message row assigns string_views to literals while Google copies. The README's FetchContent pin (2026-01-02) predates two fuzzer-found parser fixes (heap overflow, PR #199; crash, PR #200). Pre-1.0.

## Caveats and trade-offs

First-party benchmark. Flags and build type are not stated for the published numbers. The README prose numbers do not exactly match the committed benchmarks/Linux_bench.result. For example, in the raw file repeated_packed takes 3966 ns wall / 3852 ns CPU for google regular (the prose says 4164) and 2650 / 2511 ns for hpp-proto regular (the prose says 2624). The workload is one small in-code GoogleMessage1 plus synthetic packed data, not the v3.6.0 dataset files. Google wins serialize-only (proto2 64.5 vs 85.1 ns). The headline gains compare hpp-proto non-owning mode with Google arena mode; in regular deserialize mode the gap is small (proto2 215 vs 210 ns). The Mac (M1 Pro) results have the same shape. Only two machines were tested, with no variance reported.

Requires C++23 compiler (Clang 19+ / GCC 13+); Google protobuf still wins on pure serialize-only of already-constructed objects; biggest gains require the non-owning/arena mode, which changes ownership semantics vs stock generated protobuf classes

## Maintenance

Actively maintained (last main-branch commit 2026-08-03, fuzzed with ClusterFuzzLite, CI on Linux, macOS and Windows) but still pre-1.0 with 43 stars. It is MIT-licensed and consumable via FetchContent or the in-repo vcpkg port and conanfile.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** benchmarks/ReadMe.md compares hpp-proto directly with Google protobuf 33.2 using public code (benchmarks/benchmark.cpp, Google Benchmark, built by benchmarks/CMakeLists.txt) and states the compilers (Apple clang 17.0.0, gcc 13.3.0) and CPUs (M1 Pro, i9-11950H). No optimization flags or build type are stated for the published numbers: the page's own run command (`cmake -B build -DHPP_PROTO_BENCHMARKS=ON`) sets no CMAKE_BUILD_TYPE, and only an unlinked 'benchmark' preset in CMakePresets.json sets Release. That rules out A, and first-party numbers are C.
- **Verifier notes:** The numbers match benchmarks/ReadMe.md (Linux section). The main branch's last commit is 2026-08-03; the 2026-09-25 date comes from a non-default cflite-corpus branch. If the orchestrator accepts the CMakePresets.json 'benchmark' preset (Release) as the stated flags, the entry would meet A, but the page itself states no flags.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `caveats`
- **Shortcomings recorded by:** Code size: the Linux encode/decode test binary is 111,816 bytes vs 3,829,824 with static libprotobuf and 1,748,216 with libprotobuf-lite.
- **Pages the verifier opened:**
  - <https://github.com/huangminghuang/hpp-proto>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/ReadMe.md>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/benchmark.cpp>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/Linux_bench.result>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/Mac_bench.result>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/Linux_bench.json>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/CMakeLists.txt>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/CMakePresets.json>
- **Sources the enricher read:**
  - <https://github.com/huangminghuang/hpp-proto>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/README.md>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/ReadMe.md>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/benchmark.cpp>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/Linux_bench.result>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/Mac_bench.result>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/Linux_sizes.json>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/CMakeLists.txt>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/CMakePresets.json>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/docs/frontend_apis.md>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/docs/Code_Generation_Guide.md>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/docs/grpc-adapter.md>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/docs/dynamic_message.md>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/include/hpp_proto/binpb/deserialize.hpp>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/include/hpp_proto/binpb/serialize.hpp>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/include/hpp_proto/binpb/varint.hpp>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/include/hpp_proto/binpb/utf8.hpp>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/include/hpp_proto/binpb/meta.hpp>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/include/hpp_proto/binpb/util.hpp>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/.github/workflows/linux.yml>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/.github/workflows/macos.yml>
  - <https://github.com/huangminghuang/hpp-proto/blob/main/.github/workflows/windows.yml>
  - <https://github.com/huangminghuang/hpp-proto/issues>
  - <https://github.com/huangminghuang/hpp-proto/issues/140>
  - <https://github.com/huangminghuang/hpp-proto/issues/174>
  - <https://github.com/huangminghuang/hpp-proto/pull/186>
  - <https://github.com/huangminghuang/hpp-proto/pull/199>
  - <https://github.com/huangminghuang/hpp-proto/pull/200>
  - <https://github.com/huangminghuang/hpp-proto/pulls>
  - <https://github.com/huangminghuang/hpp-proto/releases>
  - <https://github.com/huangminghuang/hpp-proto/commits/main>
  - <https://github.com/huangminghuang/hpp-proto/commit/f514a0a2a25eabfe7ea956c504c4091d199cbdfc>
  - <https://github.com/PeterRK/protocache>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/huangminghuang/hpp-proto`) · [data/wave4/enrich/raw/github_com_huangminghuang_hpp_proto.json](../../../data/wave4/enrich/raw/github_com_huangminghuang_hpp_proto.json) (enrichment confidence 0.85)

</details>
