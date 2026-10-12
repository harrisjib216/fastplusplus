# asdf (Mir/D)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `D` · `BSL-1.0` · 🟢 active

> D JSON library: parses to compact binary ASDF, binds typed structs; 1.16-1.46x faster than RapidJSON on kostya's JSON test.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | 0.133s (D/ldc2, Mir Asdf DOM) vs RapidJSON 0.154s (g++) and 0.194s (clang++) (\~1.16x-1.46x faster, derived from page data) |
| **Workload** | Parse a pretty-printed JSON file of 524,288 coordinate records (x/y/z floats, name string, nested opts object; json/generate_json.rb) and average x/y/z (kostya/benchmarks 'Json' test). Mir Asdf deserializes into typed structs (deserialize!Avg, ignoring name/opts), while RapidJSON parses into a full Document DOM. Both run in the same Docker image and on the same CPU. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) E-2324G, Docker base image Debian GNU/Linux forky/sid |
| **Compiler and flags** | Mir Asdf (dub package asdf \~&gt;0.7.17) built with D/ldc2 1.41.0 via DUB_BUILD = dub -q build --build=release-nobounds --compiler=ldc2 --single plus dub.sdl dflags -mcpu=native -linkonce-templates -enable-cross-module-inlining. RapidJSON built with g++ 16.1.0 (-std=c++23) and clang++ 22.1.8 (-std=c++23 -stdlib=libc++), COMMON_FLAGS = -Wall -Wextra -pedantic -Wcast-align -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries (kostya/benchmarks common/commands.mk, json/Makefile, json/test_mir_asdf.d) |
| **Adoption** | 23 stars |
| **Last commit** | 2025-11-06 |
| **Links** | [repository](https://github.com/libmir/asdf) · [benchmark](https://github.com/kostya/benchmarks#json) |

## Verdict

kostya/benchmarks' Json test parses a pretty-printed file of 524,288 coordinate records and averages x/y/z, on an Intel Xeon E-2324G in Docker, reporting medians ± MAD. asdf 0.7.x (LDC 1.41.0, dub release-nobounds, -mcpu=native, binding into typed structs) took 0.133 s, against a full RapidJSON Document at 0.154 s (g++ 16.1) and 0.194 s (clang++ 22.1/libc++, -O3 -march=native -flto). Against RapidJSON's full-precision mode (0.212/0.262 s) the margin grows to about 1.6-2.0x.

## Use it when

- You are writing D with LDC and need JSON bound straight into typed structs or classes, not into a generic DOM.
- Large files or high-volume JSON Lines (`parseJsonByLine`) where you read a few fields per record: undeclared keys and subtrees are skipped via their length prefixes.
- Reduce-while-parsing jobs: the kostya benchmark streams each coordinate into a `put()` sink (`@serdeLikeList` + `@serdeProxy`), so the array is never built. It used 61 MiB of extra memory vs RapidJSON's 123-129 MiB.
- You need correctly rounded doubles. kostya's notes list default RapidJSON and non-Mir D parsers as inexact on numbers, and asdf goes through Mir's precise decimal-to-float path.
- Filtering or reshaping JSON records (key-path lookup, `remove()` to set a deleted bit, re-emit) without fully decoding each one.

## Skip it when

- C or C++ projects: there is no C API, so use yyjson or simdjson instead.
- Maximum throughput: on the same kostya test, simdjson On-Demand (0.060 s), DAW JSON Link (0.070-0.089 s) and Rust serde (0.103-0.110 s) are all faster than asdf's 0.133 s.
- Inputs with object keys longer than 255 bytes, numbers longer than 255 characters, or strings, arrays or objects over 2^32-1 bytes: the parser rejects them with an error.
- Untrusted input that needs strict validation: raw bytes &gt;= 0x80 are not UTF-8-validated, and number tokens are only checked against the character set `+-.0-9eE` while parsing, with the full grammar checked only when a field is converted.
- Formats beyond JSON (Ion, MsgPack, YAML, CBOR) or a mutable DOM (`AsdfNode` can hold arrays only as leaf values): the Mir author's mir-ion covers those, though its Ion DOM was slower on kostya (0.220 s). Also weigh maturity: this is mostly a one-maintainer project with legacy Travis/AppVeyor CI configs.

## How it is fast

Parsing is a single goto-driven state machine. It turns JSON into ASDF, a length-prefixed binary format (a 1-byte type tag, uint32 lengths for strings, arrays and objects, and uint8 lengths for keys and numbers) written into one buffer allocated at 6x the input size. So there is no per-node allocation, and any subtree can be skipped by jumping over its length. With LDC and SSE4.2 enabled, strings and numbers are scanned 16 bytes at a time with PCMPISTRI; otherwise a 4x-unrolled lookup-table loop runs. Numbers stay as raw text until a field is bound, then go through Mir's precise decimal-to-float (`mir.bignum` decimalToFloatImpl), and struct binding is a compile-time-generated string switch over member keys, so undeclared keys are skipped without being decoded.

## Compared with alternatives

Pick asdf when your code is D. On kostya's test it ties gason (0.127-0.133 s) and yyjson (0.131-0.132 s), binds straight into typed structs with precise float parsing, and uses the least extra memory of the three (61 MiB vs 97 and 229 MiB). From C or C++, use yyjson or simdjson (whose On-Demand API is about 2.2x faster here); the repo's own old Haswell benchmark shows asdf's raw parse beating sajson 1.3-2.5x on 10 of 11 files but losing on nested.json.

## Integration

| | |
|---|---|
| **Form** | module (dub package `asdf`; a meson.build is also provided) |
| **Dependencies** | mir-algorithm (&gt;=3.10.43), which pulls in mir-core; the D runtime/GC and Phobos (std.experimental.allocator) |
| **Minimum toolchain** | Not documented. It needs a D compiler (DMD or LDC), and the SSE4.2 fast path needs LDC. The legacy CI matrix tested DMD 2.095.1 and LDC 1.25.1 plus the latest releases. The benchmark used LDC 1.41.0 with asdf \~&gt;0.7.17 (0.7.x). |
| **Platforms** | x86-64, x86 and aarch64 (Linux and macOS in legacy Travis CI; Windows x64 in AppVeyor). SIMD is used only via SSE4.2 on x86 with LDC; every other target uses a scalar path. |
| **Thread safety** | Not documented. Each `parseJson` call owns its parser and output buffer, but `parseJsonByLine` reuses one internal buffer across lines. |
| **Drop-in for the baseline** | no |

## Gotchas

- Struct fields are required by default. A missing key raises "non-optional member ... is missing" unless the field has `@serdeOptional`, while unknown keys are silently ignored.
- `parseJson` allocates an output buffer of 6x the input length up front, from the GC by default. Pass a std.experimental.allocator allocator to control this.
- `parseJsonByLine` reuses one buffer for every line, and by default silently skips invalid lines (`throwOnInvalidLines = No`). Values from `Asdf`, and strings from `@serdeScoped` or `const(char)[]` proxies, point into that buffer and become invalid once it moves on or is freed.
- Floats: JSON `null` deserializes to NaN, the strings "nan" and "inf" are accepted, and `serializeToJson` writes NaN as the string "nan". A malformed float token throws a plain `Exception` ("Failed to deserialize number") instead of a SerdeException.

## Known shortcomings

- kostya pins asdf 0.7.x (latest v0.8.0). Two-pass design: the whole document is converted to ASDF binary first, and the benchmark averages coordinates as decoded, which explains its lower memory. Keys and numbers capped at 255 bytes; output buffer preallocated at 6x input; raw bytes &gt;= 0x80 are not UTF-8-checked. SIMD only with LDC plus SSE4.2. D-only; thin maintenance (Travis/AppVeyor CI, mostly one maintainer).

## Caveats and trade-offs

Values are median ± median absolute deviation over repeated runs, not single runs. Margin vs default RapidJSON is \~1.16x (g++) and \~1.46x (clang++ with libc++). The page notes that default RapidJSON has number-parsing inaccuracies while the Mir-based D parsers are precise; against RapidJSON Precise (0.212s g++, 0.262s clang++) asdf is \~1.6-2.0x faster (derived from page data). Mir Asdf ties gason/yyjson (0.127-0.133s) and is \~2.2x slower than simdjson On-Demand (0.060s). This is one synthetic workload, and asdf's typed deserialization skips unused keys, while RapidJSON builds a full DOM.

D-only (needs ldc2/DUB toolchain, not usable from C++ directly); part of the larger Mir numerical ecosystem so pulls in extra dependencies; smaller community/less battle-tested than RapidJSON.

## Maintenance

Low activity but still maintained by the Mir author: v0.8.0 was tagged 2025-11-06 after a compile fix, the package gets about 1.8k dub downloads a month, and it is BSL-1.0. However, CI still points at legacy Travis/AppVeyor, and the README's API-docs link (asdf.libmir.org) did not resolve on 2026-09-25.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** kostya/benchmarks Json table, updated 2026-07-19, shows 'D/ldc2 (Mir Asdf DOM)' at 0.133s vs 'C++/g++ (RapidJSON)' at 0.154s and 'C++/clang++ (RapidJSON)' at 0.194s. Code is public (json/test_mir_asdf.d uses dub package asdf \~&gt;0.7.17 = libmir/asdf; json/test_rapid.cpp). Compilers are in the README, flags are in common/commands.mk and the dub.sdl header, and the CPU is an Intel Xeon E-2324G.
- **Verifier notes:** Numbers and tier A confirmed. The original compiler_and_flags wrongly attributed LDC2_BUILD -O5 to asdf; asdf actually uses DUB_BUILD release-nobounds with -mcpu=native. The original caveats wrongly said 'single-run' and '5-16%'. Metadata (BSL-1.0, 23 stars, last commit 2025-11-06, active) verified.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kostya/benchmarks#json>
  - <https://github.com/kostya/benchmarks/blob/master/json/test_mir_asdf.d>
  - <https://github.com/kostya/benchmarks/blob/master/json/test_rapid.cpp>
  - <https://github.com/kostya/benchmarks/blob/master/json/Makefile>
  - <https://github.com/kostya/benchmarks/blob/master/json/generate_json.rb>
  - <https://github.com/kostya/benchmarks/blob/master/json/mir-common-json/source/mir_common_json.d>
  - <https://github.com/kostya/benchmarks/blob/master/common/commands.mk>
  - <https://github.com/libmir/asdf>
- **Sources the enricher read:**
  - <https://github.com/libmir/asdf>
  - <https://github.com/libmir/asdf/blob/master/dub.json>
  - <https://github.com/libmir/asdf/blob/master/SPECIFICATION.md>
  - <https://github.com/libmir/asdf/blob/master/LICENSE.md>
  - <https://github.com/libmir/asdf/blob/master/meson.build>
  - <https://github.com/libmir/asdf/blob/master/.travis.yml>
  - <https://github.com/libmir/asdf/blob/master/.circleci/config.yml>
  - <https://github.com/libmir/asdf/blob/master/appveyor.yml>
  - <https://github.com/libmir/asdf/blob/master/test_travis.sh>
  - <https://github.com/libmir/asdf/blob/master/source/asdf/package.d>
  - <https://github.com/libmir/asdf/blob/master/source/asdf/jsonparser.d>
  - <https://github.com/libmir/asdf/blob/master/source/asdf/asdf.d>
  - <https://github.com/libmir/asdf/blob/master/source/asdf/serialization.d>
  - <https://github.com/libmir/asdf/blob/master/source/asdf/transform.d>
  - <https://github.com/libmir/asdf/blob/master/source/asdf/jsonbuffer.d>
  - <https://github.com/libmir/asdf/blob/master/source/mir/internal_asdf.d>
  - <https://github.com/libmir/asdf/blob/master/benchmarks/sajson/README.md>
  - <https://github.com/libmir/asdf/blob/master/benchmarks/sajson/source/app.d>
  - <https://github.com/libmir/asdf/commits/master>
  - <https://github.com/libmir/asdf/tags>
  - <https://github.com/libmir/asdf/issues?q=is%3Aissue>
  - <https://github.com/libmir/asdf/issues/22>
  - <https://github.com/libmir/asdf/issues/23>
  - <https://github.com/libmir/asdf/issues/26>
  - <https://github.com/libmir/asdf/issues/29>
  - <https://github.com/libmir/mir-ion>
  - <https://github.com/kostya/benchmarks#json>
  - <https://github.com/kostya/benchmarks/blob/master/json/test_mir_asdf.d>
  - <https://github.com/kostya/benchmarks/blob/master/json/mir-common-json/source/mir_common_json.d>
  - <https://github.com/kostya/benchmarks/blob/master/json/test_rapid.cpp>
  - <https://github.com/kostya/benchmarks/blob/master/json/Makefile>
  - <https://github.com/kostya/benchmarks/blob/master/common/commands.mk>
  - <https://code.dlang.org/packages/asdf>
  - <https://code.dlang.org/api/packages/asdf/stats>
  - <https://code.dlang.org/api/packages/asdf/latest>
  - <http://asdf.libmir.org/>
  - <https://asdf.dpldocs.info/>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/libmir/asdf`) · [data/wave4/enrich/raw/github_com_libmir_asdf.json](../../../data/wave4/enrich/raw/github_com_libmir_asdf.json) (enrichment confidence 0.85)

</details>
