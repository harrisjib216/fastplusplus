# mpack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Embeddable C MessagePack codec; beat msgpack-c 1.1-3x in its author's 2016 suite; independent 2026 run: encode only.

| | |
|---|---|
| **Beats** | msgpack-c (msgpack C 1.3.0 and msgpack C++ 1.3.0) |
| **Claimed result** | schemaless-benchmarks (author-run, 2016, MPack 0.8.1 vs msgpack-c 1.3.0): gross times small-write 4.39 vs 8.68 us (1.98x), small-tree 8.60 vs 10.08 us (1.17x), large-tree 767.61 vs 1104.32 us (1.44x), derived from page data; the published 3.0x / 1.30x / 1.81x subtract a separately measured hash time. msgpack's C++ packer is within 1.1-1.3x. GLD.SerializerBenchmark (2025) has MPack 1.03-1.35x slower than msgpack-c on decode, partly from duplicate-key validation. |
| **Workload** | Encode (write), tree-parse and incremental-parse of randomly generated schemaless objects (2367-byte 'small' and 248571-byte 'large' MessagePack documents with mixed maps, arrays, strings, ints, doubles), hash time subtracted. |
| **Metric** | throughput |
| **Hardware** | AMD Phenom(tm) II X6 1090T (x86_64, 6402 bogomips) desktop PC; also a first-generation Raspberry Pi table |
| **Compiler and flags** | GCC 5.3.0 on Arch Linux; -Wall -O3 -flto -fno-fat-lto-objects -DPIC -fPIC -DNDEBUG (-O3 and -flto always enforced) |
| **Adoption** | 636 stars (mpack); 58 stars (schemaless-benchmarks) |
| **Last commit** | 2026-08-08 |
| **Links** | [repository](https://github.com/ludocode/mpack) · [benchmark](https://github.com/ludocode/schemaless-benchmarks) |

## Verdict

In ludocode/schemaless-benchmarks (written by MPack's author, 2016; GCC 5.3.0 -O3 -flto, AMD Phenom II X6 1090T, 7 runs of 10 s with best and worst dropped, hash time subtracted), MPack 0.8.1 encoded random schemaless data in 2.13 vs 6.42 us (msgpack C 1.3.0) and 2.77 us (msgpack C++) for a 2367-byte message and tree-parsed it in 4.99 vs 6.47 and 9.40 us, with matching output hashes. An independent 2026 run (GLD.SerializerBenchmark, MPack 1.1.1 vs msgpack-c 6.0.1, gcc 11.4.0 -O2, i7-12800H, about 90 trials per cell) confirms the encode lead (1.15-1.68x) but shows MPack's decode 1.03-1.35x slower in every group.

## Use it when

- Encoding MessagePack from C on a hot path: faster than msgpack-c in the author's 2016 suite (1.1-3.0x) and in the independent 2026 GLD.SerializerBenchmark run (1.15-1.68x against msgpack-c 6.0.1 across 10 workload groups, derived from its data).
- Firmware and other constrained targets: no libc or allocator requirement, fixed buffers and node pools, builds for AVR/Arduino with 16-bit int and size_t, WebAssembly and inside the Linux kernel.
- Parsing untrusted MessagePack into a random-access tree in C with one error check at the end, optional UTF-8 validation and message size and node-count limits (mpack_tree_set_limits).
- Continuous streams such as RPC over a socket: mpack_tree_init_stream parses message after message, including non-blocking parsing.
- Schema-known messages where the README recommends the Expect API for maximum speed and minimal memory (that path is not benchmarked anywhere read here).

## Skip it when

- Decode-heavy services already on current msgpack-c: in the 2026 GLD run (MPack 1.1.1 vs msgpack-c 6.0.1, gcc 11.4.0 -O2, i7-12800H) MPack's Node-API decode into structs was 1.03-1.35x slower in all 10 groups, and the round trip was a wash (MPack ahead in 5 groups, behind in 5).
- JSON workloads: MessagePack only; the JSON siblings (yyjson-class parsers, json.cpp, cjson.cpp) are a different format.
- C++ code that wants struct-level serialization from types or schemas: BitSerializer's MsgPack path, zpp::bits or protobuf-c generate that code, while MPack is a hand-written element-by-element API.
- Reading untrusted data with the latest tagged release: v1.1.1 (2023-01-09) predates the August 2026 develop fixes for unbounded recursion in mpack_discard() (#126, stack overflow on deeply nested input), size_t overflow checks (#123, #124) and a range check in mpack_expect_\*_alloc(); build from develop or backport.
- Maps with many keys looked up by name: every mpack_node_map_cstr lookup scans all keys of the map to detect duplicates, so k lookups cost O(k\*n).

## How it is fast

Each write encodes straight into the writer's buffer: MPACK_WRITE_ENCODED checks the space left behind an MPACK_LIKELY branch, stores the big-endian bytes with __builtin_bswap helpers and only calls mpack_writer_ensure/flush when the 4096-byte buffer (MPACK_BUFFER_SIZE) fills. msgpack-c 1.3.0's C packer instead hands every element to a function pointer (msgpack_pack_append_buffer expands to (\*user-&gt;callback)(...)), which plausibly explains why the C API trailed by 3.0x on small writes while msgpack's templated C++ packer trailed by only 1.3x (inference from the code, not profiled). The Node API parses iteratively with an explicit level stack rather than recursion, allocates node structs in 4 KB pages with each compound's children contiguous, points string and binary nodes into the source buffer without copying, and bounds allocation on hostile input by a 'possible nodes left' count (every element takes at least one byte).

## Compared with alternatives

Among catalogued C MessagePack options pick MPack over CMP whenever speed matters: in the same suite it wrote small data 3.4x faster (2.13 vs 7.33 us) and parsed incrementally 2.3x faster (3.20 vs 7.43 us), with CMP winning only on code size (3232 vs 4088 bytes). Prefer BitSerializer, zpp::bits or Cap'n Proto when you are in C++ and want type-driven serialization rather than an element-level C API.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none required; libc, stdio and malloc are optional and set by config macros (MPACK_STDLIB, MPACK_STDIO, MPACK_MALLOC); the repo's own build only runs the unit tests |
| **Minimum toolchain** | C89/gnu89 (supported since v1.1), later C standards and C++; builds clean under /W4 with Visual Studio 2015-2019 |
| **Platforms** | any: desktop and mobile OSes, WebAssembly, the Linux kernel (mpack-linux-kernel config), 8-bit AVR/Arduino; float and double can be disabled individually |
| **Thread safety** | not documented; writers, readers and trees are caller-owned structs, so the natural pattern is one per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the cited suite: a fixed, separately measured hash time is subtracted from every row, which inflates ratios. Gross times give small-write 4.39 vs 8.68 us (1.98x, not 3.0x), small-tree 8.60 vs 10.08 us (1.17x, not 1.30x) and large-tree 767.61 vs 1104.32 us (1.44x, not 1.81x) against msgpack C (derived from page data). The 3.0x write headline mostly measures msgpack-c's callback-based C packer; msgpack's C++ packer is within 1.1-1.3x.
- The 2016 numbers are for MPack 0.8.1 and msgpack-c 1.3.0 on GCC 5.3.0, and the harness uses the 0.8 API (mpack_tree_init parses immediately; 1.0 split it into init plus mpack_tree_parse), so the suite does not build against current MPack unchanged. The README's 'except CWPack' remark is not backed by the suite, which never ran CWPack.
- The GLD comparison is not quite like for like on decode: its msgpack-c wrapper returns on the first matching key, while MPack's mpack_node_map_cstr_optional scans the whole map and flags duplicate keys as errors, so part of MPack's 1.03-1.35x decode deficit is extra validation.
- Sticky errors mean a failed write or lookup silently returns 0/nil until you check mpack_writer_destroy() or mpack_tree_destroy(); element-count tracking for mpack_start_map/array is off in release builds (MPACK_READ_TRACKING and write tracking follow MPACK_DEBUG), so count mismatches are only caught in debug.

## Known shortcomings

- Tier A on the author's schemaless-benchmarks (GCC 5.3.0 -O3 -flto, Phenom II X6; Celeron extended run agrees) but author-run with 2016 versions (msgpack-c 1.3.0); msgpack-c is not a spec-listed baseline (baseline_in_list false); the libbson 'tree' row is faster but uses in-place iteration; the CWPack claim is not backed by the suite.
- Enricher (orphaned file): the cited suite subtracts a fixed, separately measured hash time from every row, which inflates the ratios; gross times give small-write 4.39 vs 8.68 us (1.98x, not 3.0x), small-tree 8.60 vs 10.08 us (1.17x, not 1.30x) and large-tree 767.61 vs 1104.32 us (1.44x, not 1.81x) against msgpack-c (derived from page data); the 3.0x headline mostly measures msgpack-c's callback-based C packer while msgpack's C++ packer is within 1.1-1.3x. The 2016 numbers are MPack 0.8.1 vs msgpack-c 1.3.0 on GCC 5.3.0 with the 0.8 API (mpack_tree_init parsed immediately), so the suite does not build against current MPack unchanged; the 'except CWPack' remark is not backed by the suite. In the GLD comparison the msgpack-c wrapper returns on the first matching key while mpack_node_map_cstr_optional scans the whole map and flags duplicates, so part of MPack's 1.03-1.35x decode deficit is validation. Sticky errors silently return 0/nil until destroy() is checked; element-count tracking is off in release builds. Last release v1.1.1 (2023-01-09), later security fixes unreleased.

## Caveats and trade-offs

Benchmark is written and run by the MPack author (the suite README says it may be biased). Benchmarked versions are MPack 0.8.1 and msgpack-c 1.3.0 (2016 era, GCC 5.3.0 on Arch Linux, Phenom II), while the MPack README now describes MPack 1.1 and msgpack-c 3.3.0 (msgpack-c has since moved to separate C and C++ release lines), so current ratios are unknown. Method: 7 runs of 10 s each, best and worst dropped, a fixed hash time subtracted; output hashes match across the MessagePack encoders, so the work is equivalent. The extended results (full-results-extended.md) add an Intel Celeron 2957U run that agrees: write small 2.19 vs 11.90 us (msgpack C) and 3.44 us (msgpack C++); tree small 8.93 vs 10.34 and 13.15 us. Not all rows are wins: libbson's tree row (4.45 us small, 301.90 us large) is faster, but that row is libbson-iter.c, which walks the BSON buffer in place rather than building a tree, so it is not like for like, and libbson is BSON, not MessagePack. msgpack C's encode row (6.42 us) is the weakest baseline; msgpack C++ is only 1.1x to 1.3x behind on writes. The README claim 'except CWPack' is not backed by the suite, which never benchmarks CWPack (neither README nor full-results-extended.md mentions it). msgpack-c is not in the category's baseline list (iostreams + std::string, std::format). Ratios are derived from the page tables. [retier] Author-run 2016 suite on the 0.8 API (does not build against current MPack unchanged); hash time subtracted from every row inflates ratios; the 'except CWPack' remark is unbacked. Sticky errors return 0/nil until destroy() is checked; count tracking off in release builds. Last release v1.1.1 (2023), later security fixes only on develop.

C library, amalgamation (mpack.h and mpack.c) embeddable, runs on 8-bit microcontrollers and in the Linux kernel; MessagePack only (not a JSON drop-in); stateful error handling instead of per-call return codes; tree API gives an immutable node tree; README recommends the Expect API (known schema) for maximum performance, which that suite does not cover.

## Maintenance

Active again on develop (fixes through 2026-08-08) but the last release is v1.1.1 from 2023-01-09, so security fixes for untrusted input are unreleased; MIT and two files, easy to vendor. The record's A-tier evidence is author-run on 2016 versions, and current independent data supports only the encode claim.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** ludocode/schemaless-benchmarks publishes the harness (src/mpack/mpack-write.c, mpack-node.c, src/msgpack/msgpack-c-pack.c, msgpack-c-unpack.c, msgpack-cpp-\*.cpp, Makefile), the compiler (GCC 5.3.0), flags (-Wall -O3 -flto -fno-fat-lto-objects -DPIC -fPIC -DNDEBUG) and CPU (AMD Phenom II X6 1090T); every claimed number is in its README desktop tables. Author-run, which A allows.
- **Verifier notes:** All write and tree numbers match the desktop tables of schemaless-benchmarks (small 2367-byte and large 248571-byte MessagePack objects confirmed). Tier A stands; baseline_in_list set to false because msgpack-c is not a listed serialization-json baseline (the CMP entry kept true for the same baseline, so the orchestrator may prefer consistency). Shortcomings: author-run, 2016-era versions and toolchain, libbson faster on its in-place 'tree' row, CWPack claim unbacked by the suite.
- **Fields the verifier corrected:** `baseline_in_list`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-69 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/ludocode/schemaless-benchmarks>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/full-results-extended.md>
  - <https://github.com/ludocode/mpack>
  - <https://github.com/ludocode/mpack/commits/develop>
  - <https://raw.githubusercontent.com/ludocode/mpack/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/ludocode/mpack>
  - <https://github.com/ludocode/mpack/commits/develop>
  - <https://github.com/ludocode/mpack/releases>
  - <https://github.com/ludocode/mpack/issues>
  - <https://github.com/ludocode/mpack/issues/122>
  - <https://github.com/ludocode/mpack/issues/128>
  - <https://github.com/ludocode/mpack/commit/ab80621be5074f458f641e3b89facddb6b1ac303>
  - <https://github.com/ludocode/mpack/commit/3d54d1215bdb5478d3ddecaf85884c58b382cd9b>
  - <https://raw.githubusercontent.com/ludocode/mpack/HEAD/README.md>
  - <https://raw.githubusercontent.com/ludocode/mpack/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/LICENSE>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/AUTHORS.md>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/docs/features.md>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/docs/node.md>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/docs/expect.md>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/docs/reader.md>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/docs/protocol.md>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/src/mpack/mpack-platform.h>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/src/mpack/mpack-common.h>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/src/mpack/mpack-writer.h>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/src/mpack/mpack-writer.c>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/src/mpack/mpack-node.h>
  - <https://raw.githubusercontent.com/ludocode/mpack/develop/src/mpack/mpack-node.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/common/benchmark.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/common/benchmark.h>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/common/buffer.h>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/mpack/mpack-write.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/mpack/mpack-node.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/mpack/mpack-read.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/msgpack/msgpack-c-pack.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/msgpack/msgpack-c-unpack.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/msgpack/msgpack-cpp-pack.cpp>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/msgpack/msgpack-cpp-unpack.cpp>
  - <https://raw.githubusercontent.com/msgpack/msgpack-c/cpp-1.3.0/include/msgpack/pack.h>
  - <https://raw.githubusercontent.com/msgpack/msgpack-c/cpp-1.3.0/include/msgpack/sbuffer.h>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/tree/master>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/tree/master/c>
  - <https://github.com/leo-gan/GLD.SerializerBenchmark/tree/master/dashboard>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/dashboard/public/data/c_latest.json.gz>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/dashboard/public/data/stats_c_latest.json.gz>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/CMakeLists.txt>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_mpack.c>
  - <https://raw.githubusercontent.com/leo-gan/GLD.SerializerBenchmark/HEAD/c/src/serializers/ser_msgpack_c.c>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ludocode/mpack`) · [data/wave1/enrich/raw/github_com_ludocode_mpack.json](../../../data/wave1/enrich/raw/github_com_ludocode_mpack.json) (enrichment confidence 0.8)

</details>
