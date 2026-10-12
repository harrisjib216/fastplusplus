# flatty

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `MIT` · 🟢 active

> Binary serializer for plain Nim types; \~38x faster serialize, \~36x faster deserialize than JSON-based std/marshal.

| | |
|---|---|
| **Beats** | Nim std/marshal |
| **Claimed result** | Serialize min time: 2.265 ms vs 85.178 ms for std/marshal (\~37.6x); avg 2.413 vs 93.228 ms (\~38.6x). Deserialize min time: 2.643 ms vs 148.723 ms (\~56.3x); avg 4.285 vs 155.663 ms (\~36.3x). (derived from page data) |
| **Workload** | Serialize and deserialize an 11,125-node ref-object tree (bool, int, 3 strings, uint16[32], uint64[16] and a child seq per node), 100 runs each with benchy timeIt; std/marshal serializes to JSON text |
| **Metric** | latency |
| **Adoption** | 95 stars |
| **Last commit** | 2026-08-13 |
| **Links** | [repository](https://github.com/treeform/flatty) · [benchmark](https://github.com/treeform/flatty#speed) |

## Verdict

The README's benchy table (100 runs each) for an 11,125-node ref-object tree shows serialize 2.265 ms vs 85.178 ms for std/marshal's JSON `$$` (\~37.6x on min, \~38.6x on average) and deserialize 2.643 ms vs 148.723 ms (\~56x on min, \~36x on average). Nim version, compiler flags and hardware are not stated (tests/config.nims only sets --path), and the numbers were recorded before the PR #55 hardening, so current deserialize is likely nearer 24-40x (derived from PR #55's 1.4-1.5x slowdown).

## Use it when

- Nim-to-Nim messages or save files where both ends are built from the same type definitions, e.g. game state over UDP with netty plus supersnappy compression (the stack the README describes).
- Payloads dominated by seqs/arrays of numbers or flat objects, which encode and decode as a single memcpy per container.
- Snapshotting acyclic ref-object trees: about 2.3 ms to serialize an 11,125-node tree in the README benchmark.
- Decoding untrusted network blobs: since the July 2026 hardening, every read is bounds-checked (also under -d:danger), length prefixes are validated before allocation, and a fuzzer runs in tests.
- Hashing arbitrary nested Nim objects by content with the bundled hashy module.

## Skip it when

- Data read by non-Nim programs: the format is defined only by Nim types, with no IDL and no other-language implementation (the JS target is Nim-compiled JS only).
- Long-lived storage while types evolve: the README says there is no versioning, so any change to a type breaks reading old blobs.
- Graphs with shared or cyclic refs: `toFlatty` on a ref writes a nil flag plus the value with no identity tracking, so shared refs come back as copies and cycles recurse until the stack overflows. std/marshal tracks ref addresses and keeps both.
- Big-endian targets (compile-time error) or JS builds with int64/uint64 fields, which the README says are supported badly.
- Polymorphic ref hierarchies or variants with more than one `case` discriminator: encoding follows the static type, and objvar.nim reads only the first discriminator (PR #36 for multiple/nested discriminators was closed unmerged).

## How it is fast

Encoding and decoding are generic overloads resolved at compile time per type, while std/marshal walks runtime type info (`typeinfo.Any`), writes JSON text and records every ref address in an IntSet. For seqs and arrays whose element type is 'flat' (supportsCopyMem, no pointers, variants, ranges or int-width mismatch), flatty writes a length prefix and moves the whole block with one copyMem; strings are also one copyMem, and decode allocates with newStringUninit/setLenUninit to skip zero-fill. Output is appended to a plain string with setLen plus copyMem instead of StringStream, values keep native little-endian layout with no byte swapping, and hot procs are `{.inline.}`.

## Compared with alternatives

Every catalogued sibling targets another language (Rust, Go, C#, C++, Zig); none is a Nim library, so pick flatty inside a Nim-only system. Pick a cross-language schema format such as Bebop or SBE instead when non-Nim peers must read the data or the schema must evolve, since flatty has no IDL and no versioning.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Nim standard library only) |
| **Minimum toolchain** | Nim &gt;= 2.0.0 (flatty.nimble); install with nimble or atlas |
| **Platforms** | Little-endian native targets only (compile error on big-endian); CI on Linux, macOS and Windows plus the Nim JS backend under Node; the decode stack guard is off on emscripten and unrecognized platforms |
| **Thread safety** | Not documented. Procs work on caller-owned strings, and the only global state is a `{.threadvar.}` stack limit, so separate buffers on separate threads look safe by inspection. |
| **Drop-in for the baseline** | partial — the call swap is one line (`$$x` to `x.toFlatty`, `to[T](s)` to `s.fromFlatty(T)`), but the binary format cannot read existing std/marshal JSON and does not preserve shared or cyclic refs |

## Gotchas

- Blobs are build-dependent: `int`/`uint` and lengths use the target's native width unless both sides compile with the same -d:flatty32 or -d:flatty64, copyable seq/array elements are raw memory images (sizeof(T) each, padding included), and every enum is written as 8 bytes.
- Malformed input raises FlattyError (bad length, count or enum), IndexDefect (truncation) or RangeDefect (range type out of bounds); the README tells you to catch both CatchableError and Defect.
- The README benchmark predates the July 2026 hardening (PR #55), which itself reports ref-tree deserialize \~1.4-1.5x slower afterwards; serialize is unchanged.
- Much of the gap to std/marshal is marshal's reflection, not binary vs text: in the same table jsony (JSON) serializes in 9.618 ms, \~8.9x faster than marshal, while the binary peer bingo is only \~16% slower than flatty on serialize (min).

## Known shortcomings

- Binary format measured against Nim's std/marshal, which writes JSON text, so the 37-56x gap is binary vs JSON. Ratios use minimum times (average-time deserialize is about 36x). No compiler, flags or hardware stated.
- The README table predates decode hardening (PR #55, 2026-07-14) that made ref-tree deserialize about 1.4-1.5x slower, so the current deserialize gap is likely about 24-40x (estimate). The gap mostly reflects std/marshal's reflection overhead; bingo, another binary Nim serializer, is only about 16% slower than flatty. Shared refs come back as copies and cyclic graphs overflow the stack on serialize. Little-endian only, int width depends on build flags, no versioning or IDL, no other-language implementation.

## Caveats and trade-offs

The baseline is Nim's std/marshal, whose format is JSON, so this compares a binary format against a JSON-text serializer. It is not one of the category's named baselines (Protobuf/FlatBuffers/Cap'n Proto/MessagePack). Among binary peers, bingo is only \~16% slower on serialize (2.632 vs 2.265 ms min). No hardware, compiler or flags are stated. The std/marshal row was added on 2026-05-25. The benchmark code is public in tests/bench.nim. flatty has no versioning, per its README.

Schemaless, requires 'flat' (non-cyclic, non-pointer) Nim object layouts for best performance; no cross-language support, no versioning

## Maintenance

Active: nimble version 0.4.0, last commit 2026-08-13, decode path fuzzed and hardened in July 2026; MIT, pure Nim with no dependencies, small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Speed section is a first-party benchy table comparing flatty against Nim's std/marshal (plus bingo, frosty and jsony). The code is public in tests/bench.nim, but no compiler version, flags or hardware are given; tests/config.nims only sets --path. The deserialize min-time gap is over 50x with flags unstated, so C is also the cap.
- **Verifier notes:** The numbers match the README exactly. The record's ratios use the min-time column; with average times the deserialize gap is \~36x, not 56x. Repo metadata is correct: MIT, not a fork, 95 stars, last commit 2026-08-13, active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/treeform/flatty#speed>
  - <https://github.com/treeform/flatty>
  - <https://github.com/treeform/flatty/blob/master/tests/bench.nim>
  - <https://github.com/treeform/flatty/blob/master/tests/config.nims>
  - <https://nim-lang.org/docs/marshal.html>
- **Sources the enricher read:**
  - <https://github.com/treeform/flatty>
  - <https://github.com/treeform/flatty#speed>
  - <https://github.com/treeform/flatty/blob/master/README.md>
  - <https://github.com/treeform/flatty/blob/master/src/flatty.nim>
  - <https://github.com/treeform/flatty/blob/master/src/flatty/binny.nim>
  - <https://github.com/treeform/flatty/blob/master/src/flatty/objvar.nim>
  - <https://github.com/treeform/flatty/blob/master/src/flatty/hashy.nim>
  - <https://github.com/treeform/flatty/blob/master/flatty.nimble>
  - <https://github.com/treeform/flatty/blob/master/tests/bench.nim>
  - <https://github.com/treeform/flatty/blob/master/tests/bench_flatty_types.nim>
  - <https://github.com/treeform/flatty/blob/master/tests/config.nims>
  - <https://github.com/treeform/flatty/blob/master/tests/test_flatty.nim>
  - <https://github.com/treeform/flatty/blob/master/.github/workflows/build.yml>
  - <https://github.com/treeform/flatty/issues/33>
  - <https://github.com/treeform/flatty/issues/38>
  - <https://github.com/treeform/flatty/issues/40>
  - <https://github.com/treeform/flatty/pull/36>
  - <https://github.com/treeform/flatty/pull/46>
  - <https://github.com/treeform/flatty/pull/52>
  - <https://github.com/treeform/flatty/pull/55>
  - <https://github.com/treeform/flatty/pull/56>
  - <https://github.com/treeform/flatty/commit/4031efaa>
  - <https://github.com/treeform/flatty/commit/d9f0d0c3>
  - <https://nim-lang.org/docs/marshal.html>
  - <https://github.com/nim-lang/Nim/blob/devel/lib/pure/marshal.nim>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/treeform/flatty`) · [data/wave4/enrich/raw/github_com_treeform_flatty.json](../../../data/wave4/enrich/raw/github_com_treeform_flatty.json) (enrichment confidence 0.8)

</details>
