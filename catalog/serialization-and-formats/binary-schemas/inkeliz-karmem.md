# Karmem

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🔴 abandoned

> Zero-copy, schema-compiled binary format for Go/TinyGo and WASM; own benchmark: 5-18x faster than FlatBuffers' Go implementation.

| | |
|---|---|
| **Beats** | FlatBuffers |
| **Claimed result** | README headline: 'almost 10 times faster than Google Flatbuffers'. benchstat, FlatBuffers (old) vs Karmem (new), Apple M1. Native: EncodeObjectAPI 2.54ms -&gt; 0.51ms (-79.85%, \~5x), DecodeObjectAPI 3.57ms -&gt; 0.20ms (-94.30%, \~18x), DecodeSumVec3 1.44ms -&gt; 0.16ms (-88.86%, \~9x). WASM on wazero: EncodeObjectAPI 17.2ms -&gt; 4.0ms (-76.51%, \~4.3x), DecodeObjectAPI 50.7ms -&gt; 1.9ms (-96.18%, \~27x), DecodeSumVec3 5.74ms -&gt; 0.75ms (-86.87%, \~7.7x). The x-ratios are derived from page data. Allocations are zero only natively: 0 vs 1.00k allocs/op for encode and 0 vs 110k for decode. Under WASM allocs/op are about equal (4 vs 4 encode, 4 vs 5 decode). |
| **Workload** | Go testing benchmarks in benchmark/ (main_test.go, main_fbs.go, main_km.go). They encode and decode, through the object API, a Monsters root of 1000 monsters; each monster has a 100-element Vec3 path, a 100-byte inventory, weapons, hitbox and status arrays. DecodeSumVec3 sums the path vectors with zero-copy readers. The FlatBuffers side uses the Go object API (Pack / UnPackTo) with a 'similar', not identical, schema. Runs cover native Go and a TinyGo-compiled WASI module inside wazero, on an Apple M1. |
| **Metric** | throughput |
| **Hardware** | MacOS/ARM64 (Apple M1) |
| **Compiler and flags** | Go and TinyGo versions for the README run are unstated. benchmark/go.mod declares go 1.18 and FlatBuffers Go v2.0.6; CI (.builds/ubuntu.yml) uses go1.18.4 on linux/amd64, but that is not the M1 run. Native: go test -tags fbs\|km -bench=. -benchmem -benchtime=5s -count 5. WASM: tinygo build -target wasi -gc conservative --no-debug -opt 2 -scheduler none, run under wazero. Results compared with benchstat. |
| **Adoption** | 683 stars |
| **Last commit** | 2023-03-03 |
| **Links** | [repository](https://github.com/inkeliz/karmem) · [benchmark](https://github.com/inkeliz/karmem#benchmark) |

## Verdict

The project's own benchmark encodes and decodes 1,000 monsters, each with a 100-element Vec3 path, on an Apple M1; toolchain versions are not stated, and FlatBuffers Go is v2.0.6. Natively, Karmem was \~5x faster to encode, \~18x faster to decode through the object API and \~9x faster to sum the paths with zero-copy readers (1.44 ms -&gt; 0.16 ms); under TinyGo WASM on wazero the ratios were \~4.3x, \~27x and \~7.7x. The baseline is FlatBuffers' allocation-heavy Go object API (110k allocs/op on decode) with a similar but not identical schema, and no C++ implementation of either format was measured.

## Use it when

- A TinyGo or Go WASM module that exchanges structured data with a host or with other guests written in Zig, C, AssemblyScript or Odin, where everyone reads one encoded buffer in place.
- Hot loops that repeatedly read a few fields or numeric arrays (e.g. Vec3 paths) out of large messages: Viewers hand back native slices over the buffer, with no per-element accessor calls.
- Go code that decodes many messages of the same type into one reused destination struct (e.g. from a sync.Pool) and wants 0 allocations per decode natively.
- Schemas made mostly of fixed-size numerics and bounded arrays ([N]T, [&lt;N]T) that only ever add fields, with little-endian machines on both ends.

## Skip it when

- C++ codebases: there is no C++ generator, the C target is a C99 header that relies on GCC/Clang packed attributes, and nobody benchmarked FlatBuffers' C++ path against it.
- Untrusted input: a malformed offset silently yields zero/default values instead of an error, and the README warns that shared offsets let a small message expand into large arrays under the Object API. The only mitigation offered is to use limited arrays and avoid the Object API.
- Schemas that need unions, optional/nullable fields, arrays of strings, tables or arrays, field removal, or a JavaScript/TypeScript generator. None of these is supported, and the unions (#25) and array-of-strings (#98) issues are still open.
- Projects that need a stable API or upstream fixes. The README says the API is unstable, the last code change was in Sep 2022, and the data-corruption report #102 has no reply. The package also panics at init on big-endian targets.
- Choosing it for native Go speed on this evidence alone. The only comparison is the project's own benchmark against FlatBuffers' Go object API with a similar but not identical schema, and a request for an independent comparison (#31) was never resolved.

## How it is fast

Layouts are fixed when the schema is compiled. A table is a uint32 size header followed by fields at constant offsets, with no FlatBuffers-style vtable, so reading a field costs one comparison against the table size plus an unsafe load at a constant offset. Arrays come back as native Go slices built over the buffer from hand-made slice headers, so a loop over them is plain indexing; FlatBuffers Go's Path(&obj, j) does a vtable lookup and a vector dereference for every element. In the README's raw-struct comparison this read loop takes 160 µs against 154 µs for summing a plain Go struct. Object-API decode copies into the destination's existing slices and strings and grows them only when they are too short (0 allocs/op natively, against 110k for FlatBuffers' UnPackTo, which makes fresh slices and pointer structs). Encoding is one pass of typed unsafe stores and memcpy into a preallocated buffer, with no endianness conversion.

## Compared with alternatives

Pick Karmem only for the job it was built for: a TinyGo/Go WASM module sharing one buffer with Zig, C, AssemblyScript or Odin code. For Go-only messaging, greenpack or ZebraPack are the catalogued Go options. For C++, YaFF (listed at \~2-2.5x faster flat reads than FlatBuffers) or SBE fit better, since Karmem has no C++ generator.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Go runtime package (karmem.org/golang): stdlib only (errors, unsafe). The code generator (karmem.org/cmd/karmem) needs golang.org/x/crypto for blake2b packet IDs. Each other target needs its runtime file (c/karmem.h, zig/karmem.zig, assemblyscript/karmem.ts, swift, odin, dotnet). |
| **Minimum toolchain** | Go 1.18 (go.mod; the generated code uses unsafe.Add). The README lists Go 1.19 / TinyGo 0.25.0, and CI used Go 1.18.4/1.19 and TinyGo 0.24.0. Other targets: Zig 0.10, AssemblyScript 0.20.16, Swift/SwiftWasm 5.7, .NET 7, C via Emscripten. |
| **Platforms** | Little-endian 32- or 64-bit only (the package panics at init otherwise). Packed layouts put fields at unaligned offsets. Benchmarked on Apple M1 (native Go and wasm32-wasi under wazero); CI ran on linux/amd64. |
| **Thread safety** | Not documented, apart from a source comment that Reader is not concurrency-safe and the buffer must not change while being read. Writer has no locking; the README takes a Writer from a sync.Pool for each encode. |
| **Drop-in for the baseline** | no |

## Gotchas

- Open issue #102 (Dec 2023, no reply): the Go generator treats offset 0 as 'allocate here', so a root inline struct whose first field is another inline struct is allocated twice and decodes as zeros. The reporter's workaround is a dummy leading field.
- Failures are silent. An out-of-bounds offset makes a Viewer point at a zeroed sentinel array, ReadAsRoot returns no error, and strings or arrays longer than their [&lt;N] bound are truncated to N on read.
- Viewer strings and slices alias the input buffer (zero-copy), so reusing or overwriting that buffer changes values you already hold. Without @packed(true), padding bytes are not cleared and can leak earlier buffer or system memory (README).
- C runtime (c/karmem.h): the growable KarmemWriter calls realloc() with the requested total but records capacity as max(2x old, total), so later allocations can write past the heap block. The fixed writer, which the benchmark uses, avoids this. The runtime functions and the generated _Null array are non-static definitions in headers, so include them from only one translation unit.

## Caveats and trade-offs

First-party benchmark only; no Go/TinyGo toolchain version is stated for the M1 run, which caps it below A. The FlatBuffers baseline goes through the Go object API (Pack/UnPackTo, very allocation-heavy: 110k allocs/op on decode) rather than FlatBuffers' idiomatic zero-copy accessors, except in DecodeSumVec3, where the gap is still \~9x natively. The schemas are 'similar', not identical: Karmem uses inline fixed arrays ([5]float64, [4]Weapon) where FlatBuffers uses vectors. Hacker News commenters (item 32302120) questioned the methodology and the '10x' claim, and the author did not answer those points in the thread. The README warns that the API is not stable. No commits since 2023-03-03 (&gt;3 years), so abandoned.

Designed primarily for WebAssembly host/guest data sharing (TinyGo/WASM), not general-purpose RPC; author states FlatBuffers 'causes panics due to lack of bound-checking' motivating the project. No Rust/C++ note beyond Go/TinyGo/AssemblyScript targets claimed in docs.

## Maintenance

Abandoned: last code change Sep 2022, last commit (a wazero bump) Mar 2023, latest tag v1.2.9 (Aug 2022), and a data-corruption report sits unanswered. It is BSD-3-Clause and the Go runtime is \~135 lines on the stdlib only, so vendoring it with the generated code is practical, but you inherit the generator's bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The numbers are the project's own benchstat output in the README 'Benchmark' section. The benchmark code is public (benchmark/Makefile, benchmark/main_test.go, main_fbs.go, main_km.go, main_native_fbs.go, main_native_km.go, main_wasi_bench_test.go) and the hardware is stated (Apple M1), but no Go or TinyGo toolchain version is given for the run. That makes it first-party with partial methodology, which is C, not B: no peer review and no independent suite (alecthomas/go_serialization_benchmarks does not include Karmem).
- **Verifier notes:** The numbers match the README exactly. Tier lowered from B to C because this is the project's own benchmark without toolchain versions, not an independent suite. The 'zero allocations' part of the claim holds only for native Go, not WASM. Metadata (BSD-3-Clause, 683 stars, last commit 2023-03-03, not archived, not a fork) is all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/inkeliz/karmem>
  - <https://github.com/inkeliz/karmem#benchmark>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/Makefile>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/go.mod>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/result/README.md>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_test.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_fbs.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_km.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_native_fbs.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_native_km.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_wasi_bench_test.go>
  - <https://github.com/inkeliz/karmem/blob/master/.builds/ubuntu.yml>
  - <https://news.ycombinator.com/item?id=32302120>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
- **Sources the enricher read:**
  - <https://github.com/inkeliz/karmem>
  - <https://github.com/inkeliz/karmem#benchmark>
  - <https://github.com/inkeliz/karmem/blob/master/golang/karmem.go>
  - <https://github.com/inkeliz/karmem/blob/master/go.mod>
  - <https://github.com/inkeliz/karmem/blob/master/c/karmem.h>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/testdata/game.km>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/testdata/game.fbs>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_test.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_fbs.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_km.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_native_fbs.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_native_km.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/main_km_fuzz_test.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/Makefile>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/go.mod>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/result/README.md>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/km/game_generated.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/km/game_generated.h>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/fbs/game_generated.go>
  - <https://github.com/inkeliz/karmem/blob/master/benchmark/c/main.c>
  - <https://github.com/inkeliz/karmem/blob/master/.builds/ubuntu.yml>
  - <https://github.com/inkeliz/karmem/blob/master/.builds/fedora.yml>
  - <https://github.com/inkeliz/karmem/blob/master/.github/workflows/coverage.yml>
  - <https://github.com/inkeliz/karmem/blob/master/cmd/karmem/main.go>
  - <https://github.com/inkeliz/karmem/blob/master/cmd/karmem/kmparser/parser.go>
  - <https://github.com/inkeliz/karmem/blob/master/cmd/karmem/kmparser/kmparser_extension.go>
  - <https://github.com/inkeliz/karmem/issues>
  - <https://github.com/inkeliz/karmem/issues/102>
  - <https://github.com/inkeliz/karmem/issues/90>
  - <https://github.com/inkeliz/karmem/issues/31>
  - <https://github.com/inkeliz/karmem/issues/92>
  - <https://github.com/inkeliz/karmem/issues/99>
  - <https://github.com/inkeliz/karmem/issues/25>
  - <https://github.com/inkeliz/karmem/issues/98>
  - <https://github.com/inkeliz/karmem/commits/master>
  - <https://github.com/inkeliz/karmem/releases>
  - <https://github.com/inkeliz/karmem/tags>
  - <https://github.com/gggrafff/karmem_bug>
  - <https://github.com/gggrafff/karmem_bug/blob/master/serialization_api/serialization_api.km>
  - <https://github.com/gggrafff/karmem_bug/blob/master/main.go>
  - <https://news.ycombinator.com/item?id=32302120>
  - <https://github.com/alecthomas/go_serialization_benchmarks>
  - <https://github.com/alecthomas/go_serialization_benchmarks/blob/master/report/data.js>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/inkeliz/karmem`) · [data/wave4/enrich/raw/github_com_inkeliz_karmem.json](../../../data/wave4/enrich/raw/github_com_inkeliz_karmem.json) (enrichment confidence 0.8)

</details>
