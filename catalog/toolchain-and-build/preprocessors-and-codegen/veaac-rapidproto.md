# RapidProto

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Preprocessors and code generators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only codegen protobuf decoder for C++: arena and streaming models beating protoc's Arena decode and protozero.

| | |
|---|---|
| **Beats** | protoc |
| **Claimed result** | \~7x faster arena decode than protoc+google::protobuf::Arena (g++-13; \~6x on clang++-20), with \~0.49x peak payload memory; streaming decoder \~12x faster than protoc+Arena and \~1.8x faster than protozero; +61% MB/s vs protoc on the OSM PBF protobuf-layer decode |
| **Workload** | Decoding a realistic 2000-record mixed Dataset payload (strings, nested/repeated messages, packed scalar arrays) serialized by protoc, plus protobuf's own google_message1/google_message2 corpora and a 20MB OpenStreetMap PBF extract |
| **Metric** | throughput |
| **Compiler and flags** | g++-13 and clang++-20, -O3 -DNDEBUG, against protobuf 4.25.3 |
| **Adoption** | 3 stars (new project, created 2026-06-28) |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/VeaaC/rapidproto) · [benchmark](https://github.com/VeaaC/rapidproto/blob/main/docs/benchmarks.md) |

## Verdict

On the project's own in-repo harness (tests/bench.py), decoding a 2000-record mixed Dataset (strings, nested/repeated messages, packed scalars) serialized by protoc, the arena decoder ran \~7x protoc+google::protobuf::Arena's throughput at 0.49x its peak payload memory on g++-13 (\~6x on clang++-20), and the streaming decoder ran \~12x protoc+Arena and \~1.8x protozero; on protobuf's own google_message1/2 corpora and a 20MB OSM PBF extract the arena/streaming decoders beat protoc's protobuf-layer throughput by roughly 28-155% depending on payload shape. All figures use protobuf 4.25.3, -O3 -DNDEBUG; no CPU model is documented, only 'a quiesced box' with SMT/turbo off and core pinning.

## Use it when

- Hot decode path for schemas you can regenerate ahead of time via codegen (not reflection-based), where protoc+Arena decode throughput or peak memory is the bottleneck
- Read-mostly consumption of a message tree needing random/repeated accessor access (arena model), e.g. a mixed record with strings, nested/repeated messages, packed scalars
- Extracting a handful of fields or forwarding data without materializing objects (streaming model) — zero allocation, faster than protozero on most shapes
- Input strings/bytes can be safely borrowed as views into a buffer you keep alive (or you accept the cost of decode_owned for a self-contained handle)
- Linux/macOS/Windows C++17 projects on GCC/Clang/AppleClang/MSVC that can add a header-only generated decoder without a new link dependency

## Skip it when

- You need to serialize, mutate, or produce protobuf messages — RapidProto is decode-only; keep protoc for the write path
- You need real closed-enum semantics or strict proto3 string UTF-8 validation — RapidProto decodes all enums open and does not validate UTF-8 (part of where its speed margin over protoc comes from)
- You rely on protobuf's normal merge behavior for a repeated singular sub-message on the wire — the arena decoder rejects the buffer (RepeatedSingularMessage) instead of merging it
- You decode large packed scalar arrays mainly through the streaming model — it is slower than protozero there since a callback can't batch a bulk store; use the arena model for that shape
- The project is 3 stars, about three months old (created 2026-06-28), with first-party-only benchmarks that don't state a CPU model — weigh that immaturity against protoc for anything load-bearing today

## How it is fast

Per docs/optimizations.md, the gains stack from compile-time specialization: borrowed string_view fields instead of copies, packed-array pre-sizing (a bulk memcpy for fixed-width packed fields, a length-bounded allocation for varint arrays), forced full inlining of the wire-read call tree (RP_FLATTEN), a fused single-bounds-check tag read, SWAR (SIMD-within-a-register) 64-bit varint kernels that decode multiple bytes' continuation bits per branch instead of one byte at a time, a one-byte dispatch hub for low field numbers, and field-order threading that jumps straight to the next expected field's label when fields arrive in ascending wire order (protoc's own emission order). Together these moved the arena decoder from 2.4x protoc to 6-7x protoc on the project's mixed Dataset benchmark.

## Compared with alternatives

Pick RapidProto over Zserio or vtprotobuf when you're staying on the .proto/protoc ecosystem but want a much larger raw C++ decode throughput and memory win than Zserio's \~1.17-1.2x over protoc, and can accept a narrower, decode-only, C++-only tool (vtprotobuf targets Go). Pick FlatBuffers instead when you can drop the protobuf wire format entirely for true zero-copy access with no decode step at all.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (generated headers are self-contained; rapidprotoc itself needs only a C++17 toolchain to build, or use a prebuilt release binary) |
| **Minimum toolchain** | C++17; GCC, Clang (incl. AppleClang), or MSVC — CI/benchmarks use g++-13 and clang++-20 |
| **Platforms** | Linux, macOS, Windows (all three CI-covered); no documented CPU-architecture requirement (SWAR only, no SIMD intrinsics) |
| **Thread safety** | Streaming decode() is const/stateless, so concurrent decodes of one unmutated buffer are safe; arena decode() mutates its Arena, so give each thread its own Arena — the resulting read-only tree can then be shared (docs/semantics.md) |
| **Drop-in for the baseline** | partial — explain: replaces protoc's read path with a different API (arena accessor tree or streaming callbacks, not protoc's generated message classes/reflection); decode-only, so you still need protoc (or another encoder) to produce the bytes, and any existing mutation/serialization code stays on protoc |

## Gotchas

- Arena tree strings/bytes/raw payloads are borrowed views into the input buffer: the tree is valid only while both the Arena and the input outlive it, unless you use decode_owned
- A duplicate singular sub-message field on the wire is rejected outright (ArenaDecodeError::RepeatedSingularMessage), not merged the way protoc merges two concatenated messages
- Enums always decode open, even proto2/editions-CLOSED enums — an unrecognized value arrives as a raw integer instead of routing to unknown fields
- Recursion-depth guards against pathological nesting are sized for an 8MB stack; Windows defaults to a 1MB stack, so untrusted deeply-nested input needs a larger linked stack (/STACK:8388608) to stay safely rejecting

## Caveats and trade-offs

The CPU model is not stated anywhere in the benchmark docs (only a 'quiesced box' with SMT/turbo off and core pinning), so this falls short of A. The numbers are first-party and come from a very new, low-star project. Per the doc, part of the arena-vs-protoc gap is a feature gap: protoc validates UTF-8 on every proto3 string and RapidProto does not, and RapidProto borrows strings/bytes as views into the input instead of copying them. The streaming decoder is slower than protozero on large packed arrays. The authors call the ratios 'a box-specific rule of thumb, not a cross-machine constant'.

Decode-only (no serialization/mutation); arena tree strings/bytes/raw payloads are borrowed views into the input, so they stay valid only while both the input and the Arena outlive them; does not validate string UTF-8 (protoc does); enums decode as open even when the schema declares them closed

## Maintenance

Active (last commit 2026-09-14) and Apache-2.0-licensed, but a brand-new, 3-star project (created 2026-06-28) with no independent benchmark or adoption track record yet; it is copyable/vendorable since the consumer-facing output is generated header-only code, but treat the maturity as early.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification B, tier now C.
- **Tier reason:** These are first-party numbers from the project's own harness (tests/bench.py). Compiler, flags and protobuf version are stated (g++-13 / clang++-20, -O3 -DNDEBUG, protobuf 4.25.3), but no CPU model appears in docs/benchmarks.md, architecture.md or the README. It is not a peer-reviewed or independent third-party suite either, so it is C, not B.
- **Verifier notes:** All claimed figures appear on docs/benchmarks.md: \~7x arena vs protoc+Arena on g++-13 (\~6x clang), 0.49x payload memory, streaming \~12x vs protoc+Arena and \~1.8x vs protozero, OSM PBF protobuf-layer +61% (arena warm, 441 vs 274 MB/s). Metadata is correct: Apache-2.0, 3 stars, created 2026-06-28, last commit 2026-09-14. The only change is the tier, B-&gt;C.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/VeaaC/rapidproto/blob/main/docs/benchmarks.md>
  - <https://github.com/VeaaC/rapidproto>
  - <https://github.com/VeaaC/rapidproto/blob/main/architecture.md>
- **Sources the enricher read:**
  - <https://github.com/VeaaC/rapidproto>
  - <https://github.com/VeaaC/rapidproto/blob/main/README.md>
  - <https://github.com/VeaaC/rapidproto/blob/main/docs/benchmarks.md>
  - <https://github.com/VeaaC/rapidproto/blob/main/docs/semantics.md>
  - <https://github.com/VeaaC/rapidproto/blob/main/docs/optimizations.md>
  - <https://github.com/VeaaC/rapidproto/blob/main/architecture.md>
  - <https://github.com/VeaaC/rapidproto/issues>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/veaac/rapidproto`) · [data/wave2/enrich/raw/github_com_veaac_rapidproto.json](../../../data/wave2/enrich/raw/github_com_veaac_rapidproto.json) (enrichment confidence 0.7)

</details>
