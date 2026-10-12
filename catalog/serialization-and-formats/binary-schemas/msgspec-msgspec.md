# msgspec

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (C extension)` · `BSD-3-Clause` · 🟢 active

> Python C-extension MessagePack/JSON codec with typed Struct decoding; \~2-2.6x faster round-trip than msgpack-python.

| | |
|---|---|
| **Beats** | msgpack (msgpack-python reference implementation) |
| **Claimed result** | Page text: msgspec is "measurably faster than other Python MessagePack libraries like msgpack or ormsgpack". Per-iteration times are embedded in the page source as results_msgpack and plotted in ms. msgpack 1.0.7: encode 0.403 ms, decode 0.799 ms. msgspec with no schema: 0.125 / 0.487 ms, so 3.23x encode, 1.64x decode and 1.96x round-trip. msgspec structs: 0.112 / 0.348 ms, so 3.62x encode, 2.30x decode and 2.62x round-trip. All ratios are derived from page data. The '5x to 60x' figure on the same page is only for Struct order comparison against attrs/dataclasses/pydantic and does not apply to MessagePack. |
| **Workload** | MessagePack encode/decode of a generated filesystem-like tree of 1000 File/Directory objects (make_filesystem_data, timeit autorange), msgspec 0.18.5 vs msgpack 1.0.7 and ormsgpack 1.4.1 on CPython 3.11 |
| **Metric** | throughput |
| **Hardware** | described only as "a \~2020 x86 Linux laptop", no exact CPU model |
| **Compiler and flags** | CPython 3.11 |
| **Adoption** | 4.1k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/msgspec/msgspec) · [benchmark](https://msgspec.dev/benchmarks) |

## Verdict

The author's bench_encodings.py encodes and decodes a 1000-object File/Directory tree with timeit autorange. It compares msgspec 0.18.5 with msgpack-python 1.0.7 and ormsgpack 1.4.1 on CPython 3.11, on an unnamed '\~2020 x86 Linux laptop'; the compiler and flags are not stated. msgpack-python takes 0.403 ms to encode and 0.799 ms to decode. Untyped msgspec takes 0.125 / 0.487 ms (3.2x / 1.6x, \~2.0x round-trip). msgspec with Struct schemas takes 0.112 / 0.348 ms (3.6x / 2.3x, \~2.6x round-trip); in that case the encoder receives Struct instances rather than dicts. Against ormsgpack, the Struct path is \~1.4x faster to encode and \~2.1x faster to decode. The page has not been re-run since 0.18.5, although the bench dependency group now pins msgpack 1.2.2 and ormsgpack 1.12.2.

## Use it when

- CPython services exchanging MessagePack whose schemas are known on both ends. Define Structs and reuse one Decoder per type: the author's benchmark shows \~3.6x faster encode and \~2.3x faster decode than msgpack-python.
- Drop-in-ish speedup for untyped dict/list payloads currently going through msgpack.packb/unpackb: \~3.2x encode and \~1.6x decode with no schema at all.
- Decoding untrusted MessagePack that you would validate anyway (types, Meta constraints, tagged unions). Validating during the decode replaces a separate pydantic or cattrs pass.
- Large messages made of many small records: Structs with array_like=True (the docs claim \~2x faster decode and \~1.5x faster encode) and gc=False reduce message size, allocations and GC pauses.
- Stacks that speak both JSON and MessagePack and want one set of types and hooks for both.

## Skip it when

- Streaming or incremental decoding of concatenated messages from a socket or file. There is no Unpacker/feed() API; issue #498 has been open since 2023, so you must frame the messages yourself.
- Protocols where one field can hold either str or bin. Unions allow at most one str-like type (str, bytes, datetime, UUID, Enum, ...), so `str | bytes` is rejected (issue #973, open). Unions also allow only one int-like, one array-like and one object-like type, and several Structs in one union need tags.
- Integers outside [-2\*\*63, 2\*\*64-1] in MessagePack, which the msgpack protocol path refuses to encode or decode.
- Runtimes other than CPython 3.10+: there are no PyPy classifiers or wheels, and setup.py refuses to build for 32-bit Windows.
- Cases where you need a cross-language schema IDL or codegen: the schema lives only in Python type annotations.

## How it is fast

The whole codec is hand-written C (about 23k lines in _core.c). It encodes straight into a growable output buffer that grows 1.5x at a time; encode_into can write into a caller-owned bytearray instead. It decodes in a single pass directly into the final Python objects. Typed decoding is driven by a precompiled TypeNode, a 64-bit mask of accepted types plus constraint details. Validation is therefore a bit test during parsing, not a second pass over the decoded data as with cattrs or pydantic v1. When decoding a Struct, each map key is compared with memcmp against the struct's field-name tuple, starting just after the last field matched, so keys that arrive in field order match on the first compare. For dict decoding, short ASCII keys (fixstr, up to 31 bytes) are interned in a 512-slot string cache indexed by a murmur2 hash. Structs have a __slots__-style layout and are GC-tracked only when they reference containers (or never, with gc=False), which cuts collector work during large decodes.

## Compared with alternatives

It is the only Python entry in this category. The MessagePack-focused siblings (msgp for Go; Nerdbank.MessagePack, Nino and MemoryPack for .NET) and the Rust crates (rkyv, bitcode, postcard) all target other runtimes, so pick msgspec whenever the codec runs in CPython. Its schema-from-types approach is closest in spirit to msgp's Go codegen. If you need a language-neutral schema IDL shared across services, look at an IDL-based sibling such as Bebop or SBE instead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for MessagePack/JSON; PyYAML for YAML; tomli_w (plus tomli on Python &lt; 3.11) for TOML |
| **Minimum toolchain** | CPython 3.10+. The PyPI 0.21.1 wheels cover cp310-cp314 including free-threaded 3.14t; main adds 3.15/3.15t. A source build needs a C compiler; MSVC builds pass /std:c11 /experimental:c11atomics. |
| **Platforms** | The 0.21.1 PyPI wheels cover manylinux and musllinux on x86_64/aarch64, macOS x86_64/arm64 and Windows AMD64/ARM64. riscv64 and Pyodide wasm32 wheels exist only in unreleased CI builds. There is no 32-bit Windows and no PyPy. |
| **Thread safety** | Encoder/Decoder methods have been threadsafe since 0.15.0 (PR #402). Free-threaded builds are supported since 0.20.0; in those builds the dict-key string cache is compiled out (#ifndef Py_GIL_DISABLED). |
| **Drop-in for the baseline** | partial — the output is standard MessagePack and interoperates with msgpack-python on the wire, but the API differs: encode/decode with enc_hook/dec_hook/ext_hook replace packb/unpackb and default/object_hook, and there is no Packer/Unpacker streaming class. |

## Gotchas

- The MessagePack timestamp extension decodes to datetime.datetime, which has microsecond precision and covers years 1-9999. Valid timestamps outside that range, such as year 0 or 9999-12-31T23:59:59.999999999Z (which rounds to year 10000), fail to decode (issue #1181, closed as not planned).
- Malformed input with a map or ext used as a map key raises a bare TypeError ('unhashable type: dict'), not msgspec.DecodeError (issue #1208, open on 0.21.1 and main). On untrusted input, catch both.
- The top-level msgspec.msgpack.encode/decode functions allocate per-call state, and decoders are typed. For the benchmarked speed, create one Encoder and one Decoder per target type and reuse them.
- encode_into grows the caller's bytearray to fit the largest message it has written and never shrinks it again. The docs warn that small messages may get slower with it.

## Known shortcomings

- The published page is from msgspec 0.18.5 vs msgpack 1.0.7 and was never re-run. The 'structs' case converts data to Structs before timing, so msgspec encodes Structs while msgpack-python encodes dicts. Releases lag main (0.21.1 on PyPI; 0.22.0 changelog includes an Ext reference-leak fix, untagged). No streaming Unpacker/feed() equivalent (#498); map/ext keys raise TypeError instead of DecodeError (#1208).

## Caveats and trade-offs

The MessagePack numbers are not SVG-only. The page embeds the raw per-iteration timings in JS (Vega plot), and ratios come from those. The win over msgpack is \~2-2.6x round-trip, mostly on encode (3.2-3.6x), with decode 1.6-2.3x. The results date from msgspec 0.18.5. Hardware is vague ('\~2020 x86 Linux laptop', no CPU model) and the C compiler and flags are not stated.

Struct-based API rather than dict-based; MessagePack output is not a portable schema-enforced IDL the way Protobuf or Cap'n Proto schemas are

## Maintenance

Actively maintained by three listed maintainers (latest commit on main 2026-09-24), BSD-3-Clause and installable with pip or conda. However, the newest PyPI release and git tag is 0.21.1 (2026-04-12): the 0.22.0 section on main's changelog, dated 2026-08-11 and including a fix for a msgpack Ext reference leak, has no tag or PyPI release yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark with public code (benchmarks/bench_encodings.py, run with -p msgpack). It states CPython 3.11 but gives only '\~2020 x86 Linux laptop' as hardware, with no CPU model and no C compiler or flags, so it is C.
- **Verifier notes:** The comparison against msgpack-python is real and numeric. The downgrade is because claimed_speedup attached an unrelated '5-60x' (Struct order-comparison) figure; the real MessagePack gain is \~2-2.6x round-trip. Tier stays C. The last commit on main is 2026-09-24 (pushed_at is 2026-09-25, probably another branch). Checked: BSD-3-Clause, 4,128 stars, not archived and not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`, `last_commit`
- **Pages the verifier opened:**
  - <https://msgspec.dev/benchmarks>
  - <https://github.com/msgspec/msgspec>
  - <https://github.com/msgspec/msgspec/blob/main/docs/benchmarks.rst>
  - <https://github.com/msgspec/msgspec/blob/main/benchmarks/bench_encodings.py>
- **Sources the enricher read:**
  - <https://github.com/msgspec/msgspec>
  - <https://msgspec.dev/benchmarks/>
  - <https://github.com/msgspec/msgspec/blob/main/docs/benchmarks.rst>
  - <https://github.com/msgspec/msgspec/blob/main/benchmarks/bench_encodings.py>
  - <https://github.com/msgspec/msgspec/blob/main/docs/perf-tips.rst>
  - <https://github.com/msgspec/msgspec/blob/main/docs/install.rst>
  - <https://github.com/msgspec/msgspec/blob/main/docs/why.rst>
  - <https://github.com/msgspec/msgspec/blob/main/docs/usage.rst>
  - <https://github.com/msgspec/msgspec/blob/main/docs/supported-types.rst>
  - <https://github.com/msgspec/msgspec/blob/main/docs/structs.rst>
  - <https://github.com/msgspec/msgspec/blob/main/docs/extending.rst>
  - <https://github.com/msgspec/msgspec/blob/main/docs/changelog.md>
  - <https://github.com/msgspec/msgspec/blob/main/src/msgspec/_core.c>
  - <https://github.com/msgspec/msgspec/blob/main/src/msgspec/msgpack.pyi>
  - <https://github.com/msgspec/msgspec/blob/main/setup.py>
  - <https://github.com/msgspec/msgspec/blob/main/pyproject.toml>
  - <https://github.com/msgspec/msgspec/blob/main/.cibuildwheel.toml>
  - <https://github.com/msgspec/msgspec/blob/main/.github/workflows/build-wheels.yml>
  - <https://github.com/msgspec/msgspec/issues>
  - <https://github.com/msgspec/msgspec/issues/498>
  - <https://github.com/msgspec/msgspec/issues/973>
  - <https://github.com/msgspec/msgspec/issues/1181>
  - <https://github.com/msgspec/msgspec/issues/1208>
  - <https://github.com/msgspec/msgspec/commits/main>
  - <https://github.com/msgspec/msgspec/releases>
  - <https://github.com/msgspec/msgspec/tags>
  - <https://pypi.org/pypi/msgspec/json>
  - <https://pypi.org/pypi/msgspec/0.21.1/json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/msgspec/msgspec`) · [data/wave4/enrich/raw/github_com_msgspec_msgspec.json](../../../data/wave4/enrich/raw/github_com_msgspec_msgspec.json) (enrichment confidence 0.8)

</details>
