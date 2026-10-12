# libcbor

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Full RFC 8949 CBOR library in C99; its low-level encoder writes CBOR 1.2x to 1.6x faster than Intel tinycbor in one third-party C shootout.

| | |
|---|---|
| **Beats** | tinycbor (Intel TinyCBOR 0.6.0) |
| **Claimed result** | GLD.SerializerBenchmark C data (gcc 11.4.0, i7-12800H): encode 1.2x-1.6x faster than tinycbor 0.6.0 (like for like, derived from page data); decode rows not comparable (author-written libcbor wrappers with a 16 MiB bump arena and O(1) indexed decoder vs an untuned quadratic tinycbor wrapper). Slower than mpack and msgpack-c on all 5 payloads. |
| **Workload** | Per-operation mean serialize + deserialize time (ns) of five fixed payload types (message, document, telemetry, strings, event) written to and read back from CBOR by a shared C harness, at 100 instances per payload (about 12 to 35 KB of CBOR) and at 1 instance (a few hundred bytes); libcbor's streaming cbor_encode_\* encoder and its cbor_load DOM decoder against tinycbor's CborEncoder and CborValue cursor API. |
| **Metric** | latency |
| **Hardware** | 12th Gen Intel Core i7-12800H (20 logical cores, up to 4700 MHz, governor powersave), 32 GB RAM, Linux 6.8.0-138-generic x86_64 (environment block of the result file; git state of the run marked dirty). |
| **Compiler and flags** | gcc (Ubuntu 11.4.0-1ubuntu1\~22.04.3) 11.4.0; harness c/CMakeLists.txt defaults to Release with add_compile_options(-O2 -Wall -Wno-unused-function); libcbor v0.11.0 built by c/scripts/fetch-and-build-deps.sh with its own CMake Release configuration (libcbor's CMakeLists.txt sets -O3 -Wall -DNDEBUG and enables interprocedural optimization when check_ipo_supported passes), static library; tinycbor v0.6.0 compiled with cc -O2 and no -DNDEBUG (so cbor_assert stays live), symbols prefixed tc_ via objcopy. |
| **Adoption** | 405 stars; used by Yubico libfido2, Amazon AWS C SDK, QEMU (per repo README) |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/PJK/libcbor) · [benchmark](https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/dashboard/public/data/c_latest.json.gz) |

## Verdict

GLD.SerializerBenchmark's C suite (run 2026-09-29-182101, gcc 11.4.0, i7-12800H on the powersave governor, IQR-filtered means) shows libcbor 0.11.0's streaming encoder plus arena-backed cbor_load decoder round-tripping five fixed payloads 1.45x to 4.4x faster than tinycbor 0.6.0 at 100 instances, with encode alone 1.2x to 1.6x faster and the decode gap mostly from tinycbor's untuned quadratic access wrapper; all rows passed the suite's fidelity check. The project itself publishes no benchmark, and the libcbor rows lose to mpack and msgpack-c on every payload.

## Use it when

- C or C++ code that writes CBOR into a preallocated buffer and wants a small, MIT-licensed, dependency-free encoder: the cbor_encode_\* path matched mpack's MessagePack encoder and beat tinycbor, QCBOR and zcbor on encode in the GLD run.
- You need random access to decoded CBOR (look up array element i or many keys) and can afford building a tree; with an arena allocator the tree decode beat tinycbor's cursor-based access on all five payloads.
- You need complete RFC 8949 coverage: indefinite-length items, tags, half floats, CBOR Sequences, streaming and incremental decoding of large inputs.
- WebAuthn/FIDO2, COSE or attestation code where libcbor is already in the dependency tree (libfido2, AWS C SDK, QEMU and fwupd use it per the README).

## Skip it when

- You are free to pick the format and want the fastest round trip: in the same run mpack and msgpack-c beat libcbor-stream on all five payloads (decode 1.4x to 2x faster), and flatcc and the protobuf rows are faster still.
- Tiny embedded targets that cannot afford heap use or a tree: tinycbor's allocation-free cursor or zcbor fit better; libcbor's fast decode path builds one item per value.
- Parsing untrusted input with the default allocator: cbor_load pre-allocates definite-length arrays and maps by their declared count, so a few bytes can request a huge allocation unless you install a capping allocator.
- Building documents through the cbor_item_t API in a hot loop: the DOM build was 2x to 4x slower than tinycbor's encoder (document 277,071 vs 71,654 ns at 100 instances); use the cbor_encode_\* functions instead.
- You need semantic validation (valid UTF-8 policies, tag semantics, NaN rules): libcbor checks well-formedness only, by design (issue #440).

## How it is fast

The low-level encoder is a set of small functions that emit minimal-width CBOR heads straight into the output buffer and return the byte count; definite-length containers are announced up front, so there is no close-container bookkeeping. cbor_load builds maps and arrays as contiguous handle arrays, so decoded elements are reachable by index in O(1) instead of re-walking the byte stream. Allocation goes through a replaceable malloc/realloc/free triple (cbor_set_allocs), which lets a caller point the tree at an arena; the benchmark rows rely on that.

## Compared with alternatives

Pick libcbor over libbson when you control the format: in the same GLD C run libcbor-stream round-trips faster than libbson on every payload with 1.2x to 1.7x smaller output. Pick flatcc instead when a schema is acceptable and zero-copy reads matter, and minicbor when the code is Rust rather than C.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake; also Bazel module and distro packages such as libcbor-dev, Homebrew libcbor) |
| **Dependencies** | none at runtime |
| **Minimum toolchain** | C99 (uses C23 when the compiler offers it since 0.13.0); CMake 3.5+ from 0.13.0 (0.11.0, the benchmarked version, needed CMake 3.0) |
| **Platforms** | Linux, macOS, Windows, BSD on x86, x86-64, arm, arm64, mips(el) and riscv64 (README test matrix) |
| **Thread safety** | README claims no shared global state, but cbor_set_allocs replaces process-global allocator pointers and is documented as not thread-safe with any libcbor function that uses the heap; item refcounts are plain size_t, so share cbor_item_t trees across threads only with external locking |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws behind the numbers: both libcbor rows were reworked by libcbor's own author (GLD PR #117, merged 2026-08-25 as 797bcbb) with a 16 MiB static bump arena installed through cbor_set_allocs (free is a no-op, reset every op) and an O(1)-indexed DOM decoder, while the tinycbor wrapper was never tuned: it finds every key with cbor_value_map_find_value and reaches array element i by advancing i times from the start, so its decode grows quadratically with array length. In the PR the GLD maintainer said the stream row's decode is not comparable to tinycbor's allocation-free parser. Builds are asymmetric too: libcbor 0.11.0 at -O3 -DNDEBUG with LTO, tinycbor at plain -O2 with asserts live. Only the encode-only numbers (1.2x to 1.6x) are a like-for-like comparison, and even they carry the flag gap.
- The arena pattern used in the benchmark is unsafe in general code: it is global, not thread-safe, and invalidates every live item on reset; with the default malloc, the per-item allocations of cbor_load and cbor_build_\* are paid in full.
- Untrusted input: definite-length containers are allocated by declared size before any element is read (issues #418, #428, #431); the documented mitigation is a capping custom malloc that makes cbor_load fail with CBOR_ERR_MEMERROR.
- The benchmark measured 0.11.0; 0.12.0, 0.13.0 and 0.14.0 (2026-04-07) and unreleased master changed NaN encoding, made cbor_incref/cbor_decref inline (ABI break; PR #434 is said by its author to speed DOM-building workloads 1.3x to 1.5x), return NULL handles for empty items (custom free must accept NULL), and fixed NULL dereferences and an integer overflow in the builder's map-start callback.

## Known shortcomings

- GLD.SerializerBenchmark C data (gcc 11.4.0 -O2, i7-12800H) vs tinycbor 0.6.0: the libcbor wrappers were tuned after the #433 review while the tinycbor wrapper kept a quadratic access pattern, libcbor was built -O3 -DNDEBUG with IPO against tinycbor at -O2 with asserts live, and libcbor is slower than mpack and msgpack-c (the category baseline) on all 5 payloads; the harness uses an arena allocator.
- Enricher: both libcbor rows were written by libcbor's own author (GLD PR #117, merged 2026-08-25 as 797bcbb) using a 16 MiB bump arena whose free is a no-op and an O(1)-indexed DOM decoder, while the tinycbor wrapper was never tuned (key search per lookup, quadratic element access) and the GLD maintainer said in PR #117 that the stream-row decode is not comparable to tinycbor; only encode (1.2x-1.6x) is like for like. Loses to mpack and msgpack-c on all 5 payloads; cbor_load pre-allocates by declared size (DoS issues #418/#428/#431); global non-thread-safe cbor_set_allocs; measured 0.11.0 vs current 0.14.0 plus breaking master.

## Caveats and trade-offs

Not a project claim and not a pure parser throughput test: the harness wrappers decide the access pattern. The libcbor rows install a 16 MiB bump-arena allocator through cbor_set_allocs (reset every op, free is a no-op), which the wrapper calls the documented amortization pattern; default malloc-backed libcbor would be slower. The libcbor wrappers were reworked on 2026-08-25 (GLD commit 797bcbb, 'Rework libcbor rows: streaming wrapper, DOM tuning, native decoder') in answer to the call-path review request PJK/libcbor#433, while the tinycbor wrapper got no equivalent tuning: it locates every key with cbor_value_map_find_value (linear scan) and reaches array element i by advancing i times from the start, so its decode time grows quadratically with array length; most of the 4x to 5x decode gaps on strings and telemetry come from that access pattern, not from raw parsing speed. Build flags are asymmetric in libcbor's favour: libcbor v0.11.0 is built by its own CMake Release configuration (-O3 -Wall -DNDEBUG, plus interprocedural optimization when check_ipo_supported passes), while tinycbor is compiled with plain cc -O2 and no -DNDEBUG, so its cbor_assert checks stay live; part of the 1.2x to 1.6x encode-only gap may come from this. The fairest numbers are still the encode-only ones and the single-instance rows. The plain DOM row is slower than tinycbor at serialization and on the event payload. Against the category's MessagePack baseline libcbor is slower in the same run: mpack and msgpack-c beat libcbor-stream on all five payloads at 100 instances (for example telemetry 113,338 and 122,695 ns vs 174,795 ns), and every protobuf-wire and flatcc row is faster still (derived from page data). Results were measured on libcbor v0.11.0, before master's PR #434 (merged 2026-08-23: inline cbor_incref and cbor_decref, said by its author to give about 1.3x to 1.5x on DOM-building workloads). The benchmark's maintainer filed libcbor issues #433 (call-path review request, now closed) and #440/#441 (spec compliance misses, closed), so the suite's own compliance matrix lists libcbor misses. The result file is a dashboard snapshot (dashboard/public/data/c_latest.json.gz, run 2026-09-29-182101, re-folded on 2026-10-05); the interactive dashboard on github.io is blocked here and was not opened. Host used the powersave governor; the run's git tree (commit 7cf1c19) was dirty, most likely with the Ion serializers committed next as f040bcc, the only later change under c/src/serializers, so the libcbor and tinycbor wrappers at HEAD are what ran. About 84 to 96 kept samples per row after IQR filtering. libcbor's own README and docs have no benchmark. [retier] libcbor rows contributed by libcbor's author (GLD PR #117, 2026-08-25); arena free is a no-op; tinycbor wrapper never tuned; libcbor -O3 -DNDEBUG with LTO vs tinycbor -O2 with asserts live. cbor_load pre-allocates by declared size (#418/#428/#431); cbor_set_allocs is global and not thread-safe; measured 0.11.0, current 0.14.0.

libcbor builds a reference-counted cbor_item_t tree (one allocation per item unless cbor_set_allocs is pointed at an arena) and is the more complete CBOR implementation with streaming and incremental decoding; the speed here comes from its low-level cbor_encode_\* functions, which write straight into a caller buffer, and from O(1) random access into decoded arrays. tinycbor allocates nothing and has a smaller footprint but is a forward-only cursor API.

## Maintenance

Actively maintained (MIT, 406 stars, last commit 2026-10-04, release 0.14.0 on 2026-04-07 with a breaking master after it) and widely packaged; vendoring is easy, but pin a version because recent releases carry breaking changes to NaN encoding, empty-item handles and the refcount ABI.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now C.
- **Tier reason:** c_latest.json.gz has every quoted libcbor, libcbor-stream and tinycbor mean (round trip, encode, decode, 100 and 1 instance) plus gcc 11.4.0 and the i7-12800H; the harness (c/src/serializers/ser_libcbor.c, ser_libcbor_stream.c, ser_libcbor_common.c, ser_tinycbor.c, c/CMakeLists.txt, c/scripts/fetch-and-build-deps.sh) and all build flags are public, so A holds; the access-pattern and flag asymmetries are caveats, not missing methodology.
- **Retiered** A to C: Tier C confirmed and sharpened: the libcbor rows in GLD.SerializerBenchmark were contributed by libcbor's own author (PR #117) with an arena allocator and an O(1) DOM decoder against an untuned, quadratic tinycbor wrapper built at -O2 with asserts live; the GLD maintainer called the decode rows not comparable. Only encode is like for like.
- **Verifier notes:** Every number in claimed_speedup matches the result file (1 ns rounding differences only). Corrected caveats: #433 is closed, not open; libcbor wrappers were tuned after the #433 review while tinycbor's quadratic access pattern was not; libcbor built -O3 -DNDEBUG (+IPO) vs tinycbor -O2 with asserts; both libcbor rows lose to the category's MessagePack rows (mpack, msgpack-c). Metadata confirmed (MIT, 405 stars, last commit 2026-10-04, active).
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`, `claimed_speedup`
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
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_libcbor.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_libcbor_stream.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_libcbor_common.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_tinycbor.c>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/commit/797bcbb>
  - <https://raw.githubusercontent.com/PJK/libcbor/v0.11.0/CMakeLists.txt>
  - <https://raw.githubusercontent.com/intel/tinycbor/v0.6.0/src/compilersupport_p.h>
  - <https://raw.githubusercontent.com/intel/tinycbor/v0.6.0/src/cborparser.c>
  - <https://github.com/PJK/libcbor>
  - <https://github.com/PJK/libcbor/commits/master>
  - <https://github.com/PJK/libcbor/pull/434>
  - <https://github.com/PJK/libcbor/issues/433>
  - <https://github.com/PJK/libcbor/issues/440>
- **Sources the enricher read:**
  - <https://github.com/PJK/libcbor>
  - <https://github.com/PJK/libcbor/commits/master>
  - <https://github.com/PJK/libcbor/issues?q=is%3Aissue>
  - <https://github.com/PJK/libcbor/issues/433>
  - <https://github.com/PJK/libcbor/issues/440>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/pull/117>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/README.md>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PJK/libcbor/v0.11.0/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/src/cbor/common.h>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/src/cbor/encoding.h>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/doc/source/api.rst>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/doc/source/api/item_reference_counting.rst>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/doc/source/api/streaming_decoding.rst>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/doc/source/internal.rst>
  - <https://raw.githubusercontent.com/PJK/libcbor/HEAD/doc/source/standard_conformance.rst>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/dashboard/public/data/c_latest.json.gz>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_libcbor.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_libcbor_stream.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_libcbor_common.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_tinycbor.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/v2_codec.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/CMakeLists.txt>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/scripts/fetch-and-build-deps.sh>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/third_party/VERSIONS.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/pjk/libcbor`) · [data/wave4/enrich/raw/github_com_pjk_libcbor.json](../../../data/wave4/enrich/raw/github_com_pjk_libcbor.json) (enrichment confidence 0.6)

</details>
