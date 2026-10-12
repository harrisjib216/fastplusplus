# Protocol Puffers (protopuf)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++20 protobuf-wire-compatible codec with messages as template types; encodes a tiny message 2-4x faster than libprotobuf.

| | |
|---|---|
| **Beats** | Google protobuf C++ (libprotobuf with protoc-generated classes; version not stated) |
| **Claimed result** | Per call: encode 17.2 ns (unsafe_mode) and 29.7 ns (safe_mode) vs protobuf 68.0 ns, about 4.0x and 2.3x faster; decode 188 ns (unsafe_mode) and 217 ns (safe_mode) vs protobuf 244 ns, about 1.30x and 1.12x faster (ratios derived from page data; times from the 'Before' table of PR #53). |
| **Workload** | Google Benchmark on one small message, Class{name, 3 x Student{id, name}} (45 bytes on the wire): encode into a 64-byte array and decode from a 45-byte buffer, protopuf vs protobuf SerializeToArray / ParseFromArray. |
| **Metric** | latency |
| **Compiler and flags** | Not stated beyond 'Release mode': the PR author introduces the tables as 'Here is a benchmarks (in Release mode)'; compiler, version, exact flags, CPU and protobuf version are not given. test/benchmark/CMakeLists.txt prints '[TIP] Release mode is expected in benchmark test'. |
| **Adoption** | 207 stars; packaged in vcpkg and Conan Center (README badges) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/PragmaTwice/protopuf) · [benchmark](https://github.com/PragmaTwice/protopuf/pull/53) |

## Verdict

The only numbers are the 'Before' table in contributor basiliscos's unmerged PR #53 (opened 2025-07-08), produced by the repo's Google Benchmark harness 'in Release mode' with no CPU, compiler, flags or libprotobuf version given. One 45-byte proto3 message (Class with a name and 3 Students) encodes in 17.2 ns (unsafe_mode) and 29.7 ns (safe_mode) vs 68.0 ns for libprotobuf SerializeToArray (about 4.0x and 2.3x), and decodes in 188 ns and 217 ns vs 244 ns for ParseFromArray (about 1.30x and 1.12x); the PR's faster 'After' decode figures come from a change the maintainer found a length-counting bug in.

## Use it when

- Small, flat or shallow messages on a hot encode path where you control the schema and want to emit protobuf-compatible bytes without linking libprotobuf or running protoc
- Header-only builds or constrained targets where libprotobuf's binary size and build integration are the bigger cost (no codegen step, CMake INTERFACE target, vcpkg/Conan packages)
- Talking to protobuf peers with simple schemas (scalars, strings, bytes, nested and repeated messages, packed repeated scalars, maps) where encode latency matters more than decode
- C++20 codebases that prefer describing messages as types next to the code over maintaining .proto files

## Skip it when

- Decode-heavy services: the only published decode numbers are 1.12x (safe_mode) and 1.30x (unsafe_mode) over libprotobuf on one 45-byte message, measured against protobuf without an Arena; per-field hash-map plus std::function dispatch leaves little headroom
- Untrusted input in unsafe_mode (no bounds checks at all; issue #41 was an out-of-bounds read and write), and even safe_mode is not hardened against malformed input (see gotchas)
- Schemas that need oneof (issue #14 open), unknown-field preservation (unknown fields are skipped and lost on re-encode), groups, proto2 extensions, reflection or JSON mapping
- Deeply nested messages: every embedded level reruns the size pass over its whole subtree before writing, so size computation grows with nesting depth squared, unlike libprotobuf's cached sizes
- Big-endian targets with fixed32/fixed64/float/double fields: the default std::bit_cast path writes host byte order without a swap (only the INT_CONVERSION_RECURSIVE_IMPL fallback is byte-order independent)

## How it is fast

Encoding is fully templated and inlined: each field's key is a compile-time constant ((number &lt;&lt; 3) | wire type), the field list is walked with a fold over base classes, and output goes straight into a caller buffer with no virtual calls or library boundary; unsafe_mode also removes every bounds check. Embedded-message lengths are computed by a recursive size pass (skipper::encode_skip) right before each nested message is written. Decoding is less static than the README suggests: each field key is looked up in a per-message std::unordered_map of std::function handlers (decode_map, and skip_map for unknown fields), which is why the decode win is small.

## Compared with alternatives

Pick protopuf over pbtools or protobuf-c when you are in C++20 and want protobuf wire compatibility without a code generator or a C runtime library; pbtools has a reproducible multi-message encode and decode comparison against libprotobuf 3.6.1, which protopuf lacks. zpp::bits also speaks protobuf through zpp::bits::pb_protocol, but its README calls that mode experimental and 2-5x slower than its native format, so use zpp::bits (native format) when both ends are your own C++ and protopuf when the bytes must be real protobuf.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake INTERFACE target protopuf; vcpkg port protopuf 3.1.0, Conan Center protopuf up to 3.1.0) |
| **Dependencies** | none at runtime; GoogleTest for the optional unit tests, libprotobuf and Google Benchmark only for the optional compatibility and benchmark targets |
| **Minimum toolchain** | C++20: GCC 11+, Clang 12+, MSVC 14.29 (VS 2019 16.9)+, Apple Clang 17 (Xcode 16.4)+; GCC 10 fails on an NTTP CTAD bug (PR96331); CMake 3.16 for the provided build |
| **Platforms** | any platform with a C++20 compiler for varint, string and message fields; fixed-width and floating-point fields assume a little-endian host on the default bit_cast path (not documented) |
| **Thread safety** | not documented; encode and decode are free functions over caller-owned data, and the shared decode/skip maps are const globals built during dynamic initialization, so concurrent decodes after startup only read shared state |
| **Drop-in for the baseline** | false: wire-compatible with protobuf in both directions for the supported field types, but the API (template message types, span-based encode/decode, optional results) replaces protoc-generated classes entirely |

## Gotchas

- Decoding matches on the full key (field number plus wire type), so a repeated scalar must be declared as array_field (packed) to read proto3 output from protobuf, and an unpacked encoding of the same field is silently skipped; issue #47 (proto3 repeated int32 not decoded) was closed with no code change. Any key with field number 0 ends the message as a success instead of an error.
- safe_mode is not fully safe on malformed input: an unknown field with wire type 3, 4, 6 or 7 reaches skip_map&lt;Mode&gt;.at() and throws std::out_of_range instead of returning an empty optional, and varint decoding has no 10-byte cap, so overlong varints shift by 7\*i past the integer width (undefined behaviour) rather than being rejected.
- decode_map and skip_map are inline variable templates holding std::unordered_map&lt;..., std::function&gt; built by dynamic initialization, with unordered initialization across translation units: decoding from another global's constructor can touch an unconstructed map. Despite the constexpr markers, decode cannot run at compile time.
- Benchmark harness (test/benchmark/main.cpp, the source of the PR #53 numbers): the encode loops discard the result and never pass the output buffer to DoNotOptimize or ClobberMemory, so stores from the fully inlined protopuf encoder may be partly dead-code-eliminated while protobuf's out-of-line SerializeToArray (which also runs ByteSizeLong) cannot be. Both decoders get the 64-byte zero-padded buffer: both stop at the zero byte after the 45 real bytes, so the work matches, but protopuf reports success while protobuf's ParseFromArray result (a failure on tag 0) is ignored. protobuf decodes into a fresh non-Arena message every iteration, and the 4.0x encode headline is unsafe_mode (safe_mode is 2.3x).

## Known shortcomings

- Tier C: all six 'Before' numbers match PR #53 (encode 4.0x/2.3x, decode 1.30x/1.12x vs Google protobuf C++) but only 'Release mode' is stated with no CPU, compiler or protobuf version; the PR is unmerged and its 'After' optimisation has a length-counting bug; encode output is not protected by DoNotOptimize; both decoders get a zero-padded 64-byte buffer with results unchecked; 45-byte message; the headline ratio comes from unsafe_mode. Apache-2.0, active.
- Enricher (test/benchmark/main.cpp, PR #53): encode output is never passed to DoNotOptimize or ClobberMemory, so the inlined encoder can be partly eliminated while protobuf's out-of-line call cannot; with the zero-padded decode buffer both decoders stop at the zero byte but protobuf's ParseFromArray failure is ignored while protopuf returns success; protobuf decoded without an Arena; the 4.0x headline is unsafe_mode. Code bugs outside the numbers: safe_mode skip_map.at() throws std::out_of_range on wire types 3/4/6/7; varint decode has no 10-byte cap (shift past width is undefined behaviour); field number 0 is accepted as end of message; decode dispatches through std::unordered_map plus std::function per field, not compile time; unpacked repeated scalars are silently dropped (issue #47 closed without fix); the nested size pass is quadratic in depth; fixed/float fields assume a little-endian host; no oneof (#14).

## Caveats and trade-offs

Numbers come from a contributor's (basiliscos) pull-request description (PR #53, opened 2025-07-08, still open) and not from the README, docs or CI. The PR says only that the runs were 'in Release mode' and omits CPU, compiler, flags and the protobuf version. The harness source is public (test/benchmark/main.cpp), so a rerun is possible, but the published figures are not fully specified. The same PR's decode optimization (145 ns unsafe, 162 ns safe) is unmerged, and review found a length-counting bug in it (it decremented an item count instead of a byte count), so only the 'Before' figures are used. Harness flaws: the encode loops pass neither the output buffer to DoNotOptimize nor call ClobberMemory, so stores from the header-only, fully inlined protopuf encoder could be eliminated, while protobuf's SerializeToArray is an out-of-line library call that also runs ByteSizeLong first. Both decoders are handed the whole 64-byte array (45 wire bytes plus 19 zero bytes) and neither result is checked; since tag 0 is invalid in protobuf, ParseFromArray should end with an error after parsing the real data. The message is tiny (45 bytes, all strings within small-string length), and both decode loops construct a fresh message per iteration (protobuf without an Arena). The unsafe_mode rows skip bounds checks, so the headline 4.0x encode ratio is with checks off; safe_mode gives 2.3x on encode and only 1.12x on decode. The README has no benchmark section, and the protopuf.surge.sh docs were not reachable (EGRESS_BLOCKED in the search session). [retier] First-party PR #53 numbers ('Release mode' only; no CPU, compiler or protobuf version; PR unmerged). Encode output never passed to DoNotOptimize (inlined encoder may be partly eliminated); decode buffer zero-padded with protobuf's ParseFromArray failure ignored; protobuf run without Arena; 4.0x headline is unsafe_mode; 45-byte message. safe_mode throws on wire types 3/4/6/7; varint decode uncapped; unpacked repeated scalars dropped (#47); little-endian only; no oneof (#14).

Messages are described as C++20 template types instead of .proto files (no code generator), so it needs GCC 11+, Clang 12+, MSVC 14.29+ or Apple Clang 17+ and compile times grow with templates; wire format is protobuf-compatible both ways. unsafe_mode skips bounds checks while safe_mode adds out-of-bounds checking and is slower. The README lists the supported field types but no benchmark section.

## Maintenance

Lightly maintained: functional changes stopped in May 2025 (safe_mode became the default in November 2024, bytes_field fix in May 2025), followed only by a README note in June 2025 and a CI fix on 2026-10-02, with PR #53 and oneof (#14) still open; Apache-2.0, header-only and packaged in vcpkg and Conan, so easy to adopt for simple schemas, but the speed evidence is a single unpinned contributor run.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #53's 'Before' table holds all six figures and the harness (test/benchmark/main.cpp, Google Benchmark) is public, but the post gives only 'Release mode': no CPU, compiler, flags or protobuf version. It is the project's own benchmark run by a contributor, so C.
- **Verifier notes:** All six 'Before' figures and the derived ratios (encode 4.0x unsafe and 2.3x safe, decode 1.30x and 1.12x) match the PR. Shortcomings to record: environment unspecified beyond Release mode, numbers from an unmerged PR whose 'After' optimization has a bug, encode output not protected by DoNotOptimize, both decoders given a zero-padded 64-byte buffer with results unchecked, tiny message, and the headline uses unsafe_mode. Metadata confirmed (Apache-2.0, 207 stars, last commit 2026-10-02, vcpkg and Conan Center badges); no duplicate found.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-53 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/PragmaTwice/protopuf/pull/53>
  - <https://github.com/PragmaTwice/protopuf>
  - <https://github.com/PragmaTwice/protopuf/commits>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/test/benchmark/main.cpp>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/test/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/PragmaTwice/protopuf>
  - <https://github.com/PragmaTwice/protopuf/commits/master>
  - <https://github.com/PragmaTwice/protopuf/pull/53>
  - <https://github.com/PragmaTwice/protopuf/issues?q=is%3Aissue>
  - <https://github.com/PragmaTwice/protopuf/issues/47>
  - <https://github.com/PragmaTwice/protopuf/issues/34>
  - <https://github.com/PragmaTwice/protopuf/tree/master/include/protopuf>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/README.md>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/test/benchmark/main.cpp>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/test/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/test/benchmark/message.proto>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/message.h>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/coder.h>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/coder_mode.h>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/skip.h>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/varint.h>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/array.h>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/field.h>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/byte.h>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/int.h>
  - <https://raw.githubusercontent.com/PragmaTwice/protopuf/HEAD/include/protopuf/float.h>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/protopuf/vcpkg.json>
  - <https://raw.githubusercontent.com/conan-io/conan-center-index/master/recipes/protopuf/config.yml>
  - <https://raw.githubusercontent.com/eyalz800/zpp_bits/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/pragmatwice/protopuf`) · [data/wave1/enrich/raw/github_com_pragmatwice_protopuf.json](../../../data/wave1/enrich/raw/github_com_pragmatwice_protopuf.json) (enrichment confidence 0.75)

</details>
