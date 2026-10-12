# protobuf-c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Wire-compatible Protocol Buffers runtime and protoc plugin for C; about 5x nanopb's encode+decode throughput on host CPUs.

| | |
|---|---|
| **Beats** | nanopb |
| **Claimed result** | Arena 'Embedded - throughput' table: protobuf-c 328.0 MB/s (663,929 msg/s) vs nanopb 61.9 MB/s (125,240 msg/s), about 5.3x on both metrics (derived from page data). Older corroboration in the pbtools benchmark (eerimoq/pbtools benchmark/README.rst, gcc 8.3.0, Intel Core i7-4510U): encoding protobuf-c -O3 1.892 s vs nanopb -O2 9.580 s (about 5.1x) and decoding 2.508 s vs 6.433 s (about 2.6x) (derived from page data), with nanopb driven through its callback API. In the same pbtools table protobuf-c encodes faster than Google protobuf C++ 3.6.1 at -O3 (1.892 s vs 2.231 s, about 1.18x) but decodes slower (2.508 s vs 1.997 s, about 0.80x) (derived from page data). No msgpack comparison found. |
| **Workload** | Encode plus decode of one 494-byte protobuf message (all scalar widths, floats, strings, bytes, eight numeric arrays, a nested struct, an array of structs, Unicode strings) in the arena's c-embedded host target (languages/c-embedded). Each timed iteration packs the same statically built message into a preallocated buffer and then unpacks it: protobuf-c mallocs the decoded tree and frees it every iteration, and nanopb decodes into a memset stack struct with fixed-size fields set in nanopb/message.options. 500,000 iterations by default (bench.sh), best of 5 runs with a 10 s cooldown between runs. |
| **Metric** | throughput |
| **Compiler and flags** | gcc from the arena's Ubuntu 26.04 devcontainer (version not stated). The bench driver and the generated code are built with -Os -flto -std=c99 (languages/c-embedded/setup.sh). nanopb's runtime (git tag 0.4.9.1) is compiled from source at -Os -flto, but protobuf-c is linked with -lprotobuf-c against the distro's prebuilt libprotobuf-c (libprotobuf-c-dev), so the protobuf-c runtime's version and build flags are not stated and are not -Os. |
| **Adoption** | 3.0k stars |
| **Last commit** | 2025-04-07 |
| **Links** | [repository](https://github.com/protobuf-c/protobuf-c) · [benchmark](https://github.com/sofa-buffers/arena) |

## Verdict

In the SofaBuffers arena's c-embedded host target (gcc -Os -flto driver from an Ubuntu 26.04 devcontainer, unnamed x86-64 host, best of 5), a 494-byte proto3 message packed and unpacked 500,000 times ran at 663,929 msg/s (328.0 MB/s) with protobuf-c against 125,240 msg/s (61.9 MB/s) with nanopb 0.4.9.1, about 5.3x; protobuf-c pays malloc and free for the decoded tree on every iteration, while nanopb decodes into a memset stack struct. The older pbtools benchmark (gcc 8.3.0, Core i7-4510U, 2,000,000 iterations each of two messages) agrees: protobuf-c encodes about 5x and decodes about 2.6x faster than nanopb -O2. Do not set the arena's C++ row (Google protobuf at 530,747 msg/s) against this one: it chains encode(decode()) at -O3 -march=native, and the arena itself says rows are not comparable.

## Use it when

- C code (or C++ that wants a C ABI) on Linux-class hosts that must exchange standard protobuf wire data with messages of unbounded size and no per-field max_size options.
- Encode-heavy services or gateways where nanopb is the bottleneck: two third-party benchmarks show protobuf-c about 5x faster encoding than nanopb and 2.4-2.6x faster decoding (pbtools), and 5.3x faster on a combined round trip (SofaBuffers arena).
- Messages dominated by packed float, double or fixed-width arrays on little-endian targets, which take the memcpy paths.
- Projects that want a distro-packaged runtime (Ubuntu ships libprotobuf-c-dev and protobuf-c-compiler) and descriptor-level reflection in C (field descriptors, protobuf_c_message_check).
- Proto2 schemas with required fields and defaults, which the runtime enforces through a required-field bitmap during unpack.

## Skip it when

- Bare-metal MCUs without a heap or with tight flash: every decode allocates through ProtobufCAllocator, and the arena keeps protobuf-c out of its bare-metal footprint rows (nanopb is 6.6-7.5 KB there).
- Decode-heavy C++ code that can use Google protobuf: in pbtools' table protobuf-c decodes in 2.508 s against 1.997 s for Google protobuf C++ 3.6.1 at -O3 (0.80x, derived from page data), and pbtools itself beats protobuf-c on both encode and decode.
- Unwrapped untrusted input: unpack has no recursion-depth limit and no UTF-8 check on proto3 strings, and allocation-overflow reports #796 and #799 are still open against 1.5.2.
- Schemas that use proto3 `optional` or Editions: protoc-gen-c reports no supported features (GetSupportedFeatures returns 0) and caps the maximum edition at proto3; issue #476 has been open since 2021.
- Toolchains built on the newest Google protobuf or C++20: protoc-gen-c 1.5.2 fails to build against protobuf 34.0 (#795) and 35.0 (#801) and under C++20 (#802), all still open.

## How it is fast

Encoding is a single pass. protobuf-c.c writes each submessage at out+1 and memmoves it only when its length prefix needs more than one byte (prefixed_message_pack). Packed repeated fields reserve the minimum prefix size and shift by at most one byte, and on little-endian hosts packed float, double and fixed32/fixed64 arrays are copied with memcpy. nanopb 0.4.9.1, by contrast, encodes every submessage twice (a PB_OSTREAM_SIZING pass, then the real write) and also runs a sizing pass for packed varint arrays, so a submessage nested two deep is encoded about four times. Decoding takes two passes: the first scans all fields into a ScannedMember slab whose first 16 entries sit on the stack, so each repeated array can be allocated once at its exact size; the second parses the values. Tags are found by binary search over field ranges (int_range_lookup), with a shortcut that reuses the previous field.

## Compared with alternatives

Choose it over pbtools when you want the long-established, distro-packaged C runtime with proto2 required/default handling and descriptor reflection; pbtools was faster than protobuf-c on both encode and decode in its own benchmark. Choose it over protopuf, zpp::bits or Cap'n Proto when the code is C, not C++, and the wire format must be standard protobuf.

## Integration

| | |
|---|---|
| **Form** | shared lib (libprotobuf-c, static also possible) plus generated .pb-c.c/.pb-c.h sources compiled into your program |
| **Dependencies** | Runtime: libc only. Code generator protoc-gen-c: Google protobuf (&gt;= 3.0.0 per configure.ac, with libprotoc headers) and pkg-config; ./configure --disable-protoc builds the runtime alone. |
| **Minimum toolchain** | C compiler for the runtime; a C++17 compiler for protoc-gen-c (configure.ac AX_CXX_COMPILE_STDCXX(17)); autotools or CMake. |
| **Platforms** | Any platform with a C compiler; little- and big-endian (WORDS_BIGENDIAN fallbacks); MSVC builds fixed in 1.5.0. |
| **Thread safety** | Not documented. pack and unpack keep no shared mutable state (the default allocator is a stateless malloc/free pair), so separate messages can be processed on separate threads; a single message object is not synchronised. |
| **Drop-in for the baseline** | partial: wire-compatible with nanopb, so either side can be swapped, but the generated C API differs (heap-allocated tree from unpack, pointer plus count fields instead of fixed arrays), so calling code has to be rewritten. |

## Gotchas

- Unpack mallocs the whole decoded tree (each submessage, string, bytes field and repeated array) and must be released with free_unpacked using the same allocator. Unpacking onto the stack was declined in #154 (wontfix). To cut malloc cost, pass a bump or arena ProtobufCAllocator.
- Security on untrusted bytes: each nesting level recurses through protobuf_c_message_unpack and puts a 16-entry (512-byte) ScannedMember slab on the stack, with no depth limit. Proto3 strings are not UTF-8-validated. In 1.5.2 the count is narrowed with `unsigned n = *n_ptr` before `do_alloc(allocator, siz * n)` (open #796, #799). Past fixes: CVE-2022-48468 (integer overflow in parse_required_member, fixed in 1.4.1) and an uninitialised unknown_fields pointer that caused memory corruption (fixed in 1.5.1).
- Harness flaw behind both benchmarks: the runtime build is not matched. The arena compiles nanopb's runtime from source at -Os -flto but links the distro's prebuilt libprotobuf-c with -lprotobuf-c. pbtools links `-static -lprotobuf-c`, so its four protobuf-c rows (-Os, -Os -flto, -O3, -O3 -flto; 1.883-2.025 s encode) all run the same prebuilt runtime and the flag labels do not describe it. The direction still holds: even pairing protobuf-c's slowest pbtools row with nanopb's fastest, protobuf-c leads 4.7x on encode and 2.4x on decode (derived from page data). Applying pbtools' nanopb -Os-to-O2 gap (1.35x encode, 1.51x decode) suggests the arena's 5.3x would shrink to roughly 3.5-3.9x with a matched build (derived from page data, not measured).
- Generated .pb-c.h files carry version guards tied to the installed protobuf-c.h, so regenerate them in your build. The README advises against exporting generated symbols, or installing .pb-c.h files, in a stable library interface.

## Known shortcomings

- Tier C: the SofaBuffers arena figures (328.0 vs 61.9 MB/s, 663,929 vs 125,240 msg/s, about 5.3x vs nanopb) were run by a rival codec with no CPU or compiler version; the build is tilted (nanopb runtime built from source at -Os -flto, protobuf-c as the prebuilt distro library); the loop re-encodes a static message, one message shape. The older pbtools benchmark (gcc 8.3.0, i7-4510U) agrees at about 5.1x encode and 2.6x decode vs nanopb, but nanopb runs on its slow callback API and rows come from different runs; the same table has protobuf-c about 1.18x faster than Google protobuf C++ 3.6.1 on encode and about 1.26x slower on decode. Baseline is nanopb, not MessagePack. Stale (last commit 2025-04-07); BSD-2-Clause.
- Enricher: both sources run an unmatched runtime build (the arena bench builds the nanopb runtime from source at -Os -flto but links the distro prebuilt libprotobuf-c; pbtools links -static -lprotobuf-c so all four protobuf-c rows, 1.883-2.025 s, run the same prebuilt runtime and the flag labels do not describe it). Direction is robust: the slowest protobuf-c row vs the fastest nanopb row is still 4.7x encode and 2.4x decode (derived); a matched build might shrink the arena 5.3x to roughly 3.5-3.9x (derived, not measured). Speed comes from single-pass encoding (submessage written at out+1, memmove only if the length prefix grows) vs nanopb 0.4.9.1's sizing pass per submessage and packed array. No recursion-depth limit in unpack; no UTF-8 check on proto3 strings; open #796/#799 allocation overflow (unsigned n = \*n_ptr); CVE-2022-48468 fixed in 1.4.1; no proto3 optional or Editions (#476); build fails against protobuf 34/35 and C++20 (#795, #801, #802). Maintenance: master stops at 1.5.2 (2025-04-07) but the next branch has commits through 2026-08-22, so 'stale' is overstated.

## Caveats and trade-offs

Third-party numbers from a rival codec's benchmark arena (SofaBuffers, 0 stars) in which protobuf-c and nanopb are both baselines of the 'Embedded' throughput table, where speed is explicitly not the ranking metric. Host CPU and compiler version are not stated, so the run is not reproducible as published (the harness code is public). The build is asymmetric in protobuf-c's favour: every codec's bench driver and generated code are built -Os -flto and nanopb's runtime is compiled from source at -Os -flto, but protobuf-c's runtime is the distro's prebuilt libprotobuf-c linked with -lprotobuf-c, so its hot code runs at the distro's (unstated) flags; pbtools' own rows put nanopb at -Os about 1.35x (encode) to 1.5x (decode) slower than at -O2 (derived from page data). The c-embedded loops re-encode the original static message every iteration, not the freshly decoded one as the arena README describes for its maxspeed targets. One message shape, one unnamed host, and the 5.3x ratio compares two rows of one table. The older pbtools benchmark corroborates the direction but drives nanopb through its callback API (strings and sub-messages via pb_encode_string and pb_encode_submessage callbacks), mixes runs (protobuf-c -O3 rows from September 2019, nanopb -O2 rows re-run in January 2020 after commit 6000b5f switched common.mk to -O2), statically links an unstated libprotobuf-c version, and shows protobuf-c decoding about 1.26x slower than Google protobuf C++ 3.6.1 (derived from page data). The GLD.SerializerBenchmark C suite also lists protobuf-c, but according to the search record its protobuf-c row times a shared in-tree proto3 wire codec rather than protobuf-c itself (not re-checked by the verifier), so it was not used. No benchmark or performance numbers exist in the protobuf-c README. Last commit 2025-04-07 (release 1.5.2); the GLD suite author opened a benchmark-fairness review request (#803, 2026-07-17) and a spec-compliance report for 1.5.2 (#810, 2026-09-14), both still open. [retier] Baseline is nanopb, not MessagePack. Arena figures (328.0 vs 61.9 MB/s) run by rival codec SofaBuffers; nanopb built from source at -Os -flto while protobuf-c is the prebuilt distro library; pbtools table also links -static -lprotobuf-c for every flag row. Matched build might give roughly 3.5-3.9x (derived, unmeasured). vs Google protobuf C++ 3.6.1: about 1.18x faster encode, 1.26x slower decode. Unpack has no recursion-depth limit and no proto3 UTF-8 check; open allocation overflow #796/#799; builds fail against protobuf 34/35 and C++20. Development continues on the next branch (2026-08-22).

Wire-compatible with Google protobuf, so it needs protoc plus protoc-gen-c and a C runtime; decoded messages are allocated through a pluggable allocator (malloc by default), unlike nanopb's static allocation; the arena README calls it 'desktop-class' and ranks it for reference against footprint-oriented nanopb, so code size is larger than nanopb's.

## Maintenance

Releases are slow but development continues: master stops at 1.5.2 (2025-04-07), while the maintainer's next branch has commits through 2026-08-22 (ASan/UBSan CI, the oneof init fix for #804). Build breaks against protobuf 34/35 and open allocation-overflow reports are unreleased. BSD-2-Clause and packaged by Ubuntu, so usable as is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The arena harness is public (sofa-buffers/arena languages/c-embedded/setup.sh, protobuf/bench.c, nanopb/bench.c) and the figures match its README and results/RESULTS.txt, but the host CPU and compiler version are not stated and protobuf-c's runtime is a prebuilt distro library with unstated version and flags, so not A; the arena is a little-known rival-codec harness, not a well-known suite, so not B. The older pbtools benchmark (gcc 8.3.0, i7-4510U, flags per row) points the same way but drives nanopb through its slow callback API and mixes runs, so it does not lift the tier.
- **Verifier notes:** Arena numbers verified exactly (328.0 vs 61.9 MB/s, 663,929 vs 125,240 msg/s; 5.30x derived). Shortcomings to record: CPU and compiler version unstated, rival-codec arena, nanopb runtime built -Os -flto from source while protobuf-c uses the prebuilt distro library, static message re-encoded rather than the decoded one, one message shape; pbtools corroborates about 5x encode and 2.6x decode vs nanopb but with nanopb on callbacks, and there protobuf-c decodes slower than Google protobuf C++ 3.6.1. Metadata confirmed (BSD-2-Clause, 3.0k stars, last commit 2025-04-07, stale); not a duplicate, though pbtools (wave 1, tier A) already uses protobuf-c as a baseline.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-53 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/sofa-buffers/arena>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/README.md>
  - <https://github.com/sofa-buffers/arena/tree/main/languages/c-embedded>
  - <https://github.com/sofa-buffers/arena/tree/main/results>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/results/RESULTS.txt>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/setup.sh>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/bench.sh>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/bench.h>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/meta>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/protobuf/bench.c>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/nanopb/bench.c>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/nanopb/message.options>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/.devcontainer/Dockerfile>
  - <https://github.com/protobuf-c/protobuf-c>
  - <https://github.com/protobuf-c/protobuf-c/commits>
  - <https://github.com/protobuf-c/protobuf-c/issues/803>
  - <https://github.com/protobuf-c/protobuf-c/issues/810>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/README.rst>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/protobuf-c/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/protobuf-c/main.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/nanopb/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/nanopb/main.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/common.mk>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/Makefile>
  - <https://github.com/eerimoq/pbtools/commits/master/benchmark/common.mk>
- **Sources the enricher read:**
  - <https://github.com/protobuf-c/protobuf-c>
  - <https://raw.githubusercontent.com/protobuf-c/protobuf-c/HEAD/README.md>
  - <https://raw.githubusercontent.com/protobuf-c/protobuf-c/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/protobuf-c/protobuf-c/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/protobuf-c/protobuf-c/HEAD/protobuf-c/protobuf-c.h>
  - <https://raw.githubusercontent.com/protobuf-c/protobuf-c/HEAD/protobuf-c/protobuf-c.c>
  - <https://raw.githubusercontent.com/protobuf-c/protobuf-c/HEAD/protoc-gen-c/c_generator.h>
  - <https://github.com/protobuf-c/protobuf-c/releases>
  - <https://github.com/protobuf-c/protobuf-c/commits/next>
  - <https://github.com/protobuf-c/protobuf-c/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc>
  - <https://github.com/protobuf-c/protobuf-c/issues?q=is%3Aissue+recursion+OR+depth+OR+%22stack+overflow%22>
  - <https://github.com/protobuf-c/protobuf-c/issues?q=is%3Aissue+performance+OR+slow+OR+benchmark+OR+speed>
  - <https://github.com/protobuf-c/protobuf-c/issues/476>
  - <https://github.com/protobuf-c/protobuf-c/issues/796>
  - <https://github.com/protobuf-c/protobuf-c/issues/803>
  - <https://github.com/protobuf-c/protobuf-c/issues/810>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/README.md>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/results/RESULTS.txt>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/schema/message.proto>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/setup.sh>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/bench.sh>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/bench.h>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/meta>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/protobuf/bench.c>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/nanopb/bench.c>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/languages/c-embedded/nanopb/message.options>
  - <https://raw.githubusercontent.com/sofa-buffers/arena/HEAD/.devcontainer/Dockerfile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/README.rst>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/protobuf-c/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/nanopb/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/common.mk>
  - <https://raw.githubusercontent.com/nanopb/nanopb/0.4.9.1/pb_encode.c>
  - WebSearch: protobuf-c CVE-2022-48468 parse_required_member (snippets from docs.bell-sw.com, bugzilla.redhat.com, osv.dev)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/protobuf-c/protobuf-c`) · [data/wave1/enrich/raw/github_com_protobuf_c_protobuf_c.json](../../../data/wave1/enrich/raw/github_com_protobuf_c_protobuf_c.json) (enrichment confidence 0.65)

</details>
