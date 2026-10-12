# pbtools

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🔴 abandoned

> Python-generated C11 proto3 encoder/decoder with arena workspaces; beat libprotobuf C++ and protobuf-c on small messages at -O2.

| | |
|---|---|
| **Beats** | Google Protocol Buffers C++ (libprotobuf 3.6.1) and protobuf-c |
| **Claimed result** | Encoding (Message plus Message3, 2,000,000 iterations each): pbtools -O2 1.457 s vs Google protobuf C++ -O3 2.231 s (about 1.53x, derived from page data) and vs protobuf-c -O3 1.892 s (about 1.30x, derived from page data). Decoding: pbtools -O2 1.594 s vs Google -O3 1.997 s (about 1.25x, derived from page data) and vs protobuf-c -O3 2.508 s (about 1.57x, derived from page data). With -O2 -flto pbtools encodes in 1.319 s and decodes in 1.239 s. At -Os pbtools encodes in 3.398 s, slower than protobuf-c -Os (1.970 s) but faster than Google -Os (3.713 s); at -Os pbtools decodes in 1.749 s vs Google 2.350 s and protobuf-c 2.609 s. An earlier run (September 2019, all at -O3, replaced in commit 6000b5f) had pbtools at 1.118 s encode and 1.069 s decode. |
| **Workload** | Encode and decode of two protobuf messages from a proto derived from Google's protobuf benchmark messages (benchmark/benchmark.proto, java_package com.google.protobuf.benchmarks): 'Message' wrapping Message1 with a 566-byte wire size and Message3 with a 106-byte wire size, 2,000,000 iterations each, per library; whole-process time per row. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i7-4510U CPU @ 2.00GHz |
| **Compiler and flags** | gcc/g++ 8.3.0 with -ffunction-sections -fdata-sections -Wl,--gc-sections (benchmark/common.mk); per-row flags in the README tables: pbtools -O2, -O2 -flto, -Os, -Os -flto; protobuf-c -O3, -O3 -flto, -Os, -Os -flto (libprotobuf-c linked statically); Google -O3 and -Os (generated code and main only, linked against a shared libprotobuf 3.6.1 whose own build flags are not stated). The -O3 rows come from the September 2019 run when common.mk had OPT_SPEED = -O3; commit 6000b5f (2020-01-16) switched OPT_SPEED to -O2 and re-ran only pbtools, nanopb and flatbuffers. |
| **Adoption** | 82 stars |
| **Last commit** | 2023-06-04 |
| **Links** | [repository](https://github.com/eerimoq/pbtools) · [benchmark](https://github.com/eerimoq/pbtools/blob/master/benchmark/README.rst) |

## Verdict

In the project's own single-run benchmark (gcc 8.3.0, Intel Core i7-4510U), encoding a 566-byte and a 106-byte message 2,000,000 times each took 1.457 s with pbtools at -O2, against 2.231 s for Google protobuf C++ 3.6.1 and 1.892 s for protobuf-c at -O3; decoding took 1.594 s vs 1.997 s and 2.508 s. The baseline rows come from a September 2019 run and were not re-measured with the January 2020 pbtools build. The harnesses do unequal work: Google's encode loop heap-allocates a fresh message and copies every string each iteration (no Arena) and validates proto3 UTF-8, protobuf-c encodes through pack_to_buffer and mallocs and frees the whole tree on every decode, and both baseline runtimes are prebuilt distro libraries (only the generated code got the row's flags), while pbtools compiles its runtime with the row's flags and stores pointers to string literals.

## Use it when

- Embedded or RTOS C firmware that has to speak the proto3 wire format with no heap: a fixed stack or static workspace and output buffer per message.
- High-rate encode/decode of small messages (the benchmark used 106-byte and 566-byte messages) in builds optimized with -O2, where per-message heap allocation in libprotobuf or protobuf-c dominates.
- C-only builds that cannot take C++ or libprotobuf: one runtime .c/.h pair plus generated files (a CMakeLists.txt is provided); 17,484-byte text for the -O2 benchmark program vs 21,256 for nanopb and 77,538 for the Google C++ program (shared libprotobuf not counted).
- Messages that are built once and encoded, or decoded once and read, so the arena's no-free rule does not matter.

## Skip it when

- Decoding untrusted input, until the packed fixed-width out-of-bounds write described under gotchas is fixed or the input is pre-validated.
- proto2, services/gRPC, options, reserved fields and public imports (not supported); map fields are clumsy (README ToDo: one allocation per item); no reflection, JSON or text format; unknown fields are skipped and dropped on re-encode.
- Messages you mutate repeatedly or build incrementally: arena memory cannot be freed and repeated-field lengths cannot change after allocation; workspace sizing is left to the caller (issue #17 asks how to size it and has no visible answer).
- Size-optimized (-Os) builds: there pbtools encodes slower than protobuf-c (3.398 s vs 1.970 s in the project's own table).
- Large messages or long repeated arrays: there are no published numbers beyond 566-byte messages, every string and bytes field is copied into the arena on decode, and repeated fields are scanned twice. The project has had no commits since 2023-06-04.

## How it is fast

Encoding is single-pass and runs back to front: generated encode functions write fields in reverse order from the end of the output buffer, so each sub-message length is known when its tag is written. No ByteSize pre-pass is needed, and one memmove at the end shifts the result to the buffer start. There is no malloc: messages, repeated arrays and decoded strings are bump-allocated from the workspace, and per-message generated functions (a switch on field number) replace table-driven reflection. Repeated fields are decoded in two passes, counting first and then filling one contiguous arena array. Part of the measured lead comes from work the baselines do and pbtools does not (see verified_claims_summary).

## Compared with alternatives

Pick pbtools when you need the protobuf wire format from plain C with no heap. Cap'n Proto, zpp::bits, HPS and BitSerializer are faster or richer, but they are C++ and use their own formats, and cmp is the malloc-free C choice only if MessagePack is acceptable. Do not pick it for JSON workloads; the JSON siblings (simdjson-class parsers, DAW JSON Link) solve a different problem.

## Integration

| | |
|---|---|
| **Form** | source-drop (lib/src/pbtools.c and lib/include/pbtools.h plus generated .c/.h per proto file; lib/CMakeLists.txt builds a static library) |
| **Dependencies** | none at runtime beyond the C standard headers (stdint, stdbool, string, limits, stdalign); the generator needs Python 3.6+ and textparser&gt;=0.21.1 |
| **Minimum toolchain** | C11 (stdalign.h; CMake sets C_STANDARD 11, the tests build with -std=gnu11); char must be 8 bits |
| **Platforms** | any C11 target with 8-bit char; fixed-width values are assembled byte by byte, so endianness does not matter; -D PBTOOLS_CONFIG_FLOAT=0 removes float/double support for small MCUs |
| **Thread safety** | No mutable global state in pbtools.c, so calls are reentrant when each thread uses its own workspace and buffers; the README lists thread safety as a design goal, but issue #6 asking about it has no visible maintainer answer. A message and its workspace are not safe to share across threads without a lock. |
| **Drop-in for the baseline** | partial: wire-compatible with proto3 messages from libprotobuf and protobuf-c, but the generated C API (structs, char \* strings, workspace arguments, negative error codes) replaces the C++ classes, so calling code has to be rewritten |

## Gotchas

- Out-of-bounds write on malformed packed fixed-width fields (found by reading lib/src/pbtools.c, not executed): for packed fixed32/sfixed32/float/fixed64/sfixed64/double, the counting pass (repeated_info_decode_32bit/64bit) adds floor(len/4) or floor(len/8) items. The fill pass (decoder_read_repeated) keeps reading while any byte remains in the slice, so a payload of 4k+1..4k+3 bytes stores one extra zero item at items_p[k]: a 4- or 8-byte write past the arena allocation. Strings are allocated during the first pass and repeated arrays after it, so a crafted message can place that array at the very end of the caller's workspace. The test suite only covers well-formed packed input, and the ASan libFuzzer target runs 30 s by default.
- An N-byte encode buffer holds at most N-1 encoded bytes: encoder_write requires pos &gt;= size and pos starts at size-1, so a buffer sized exactly to the message returns PBTOOLS_ENCODE_BUFFER_FULL. Encoding writes from the end of the buffer and memmoves the result to the front on return.
- Strings are NUL-terminated char \*: every encode calls strlen on every string, embedded NUL bytes silently truncate the field, and there is no UTF-8 validation on encode or decode (protobuf 3.6.1's generated C++ for proto3 checks UTF-8 strictly, so the Google rows include work pbtools skips).
- Decode does not reset fields that are absent from the input: call \*_new() on the workspace before every decode (issue #14: decoding an empty message after an earlier decode kept the old values). Running out of workspace returns -PBTOOLS_OUT_OF_MEMORY (-3), and sub-message pointers are NULL when the field was absent.

## Known shortcomings

- Tier A (benchmark code in repo, gcc 8.3.0, flags per row, i7-4510U), but the headline mixes two runs: the Google and protobuf-c -O3 rows date from a September 2019 run while commit 6000b5f (2020-01-16) switched common.mk to -O2 and reran only pbtools, nanopb and flatbuffers. The harness tilts toward pbtools: Google encode builds a new heap Message each iteration (no Arena), protobuf-c encodes via the slower pack_to_buffer and its decode mallocs per iteration. pbtools loses at -Os encode (3.398 s vs protobuf-c 1.970 s). First-party single run against old protobuf 3.6.1; abandoned since 2023-06-04 (MIT, 82 stars).
- Enricher: library bug found reading lib/src/pbtools.c (not run): packed fixed32/sfixed32/float/fixed64/sfixed64/double fields whose payload length is not a multiple of 4 or 8 make the count pass floor len/4 or len/8 while decoder_read_repeated keeps reading while bytes remain, writing a zero item 4-8 bytes past the arena allocation; crafted input can reach past the caller's workspace; no test covers it (benchmark has no packed repeated fields). Harness: Google's loop heap-allocates a fresh message and copies strings with no Arena, Google 3.6.1 validates proto3 UTF-8 strictly while pbtools never validates, protobuf-c uses pack_to_buffer and mallocs the whole tree per decode, and both baseline runtimes are prebuilt distro libraries so the row flags apply only to generated code while pbtools compiles its runtime with the row's flags. An N-byte encode buffer holds only N-1 bytes; strings are NUL-terminated (strlen on every encode, embedded NUL truncates); decode keeps fields absent from input, so \*_new() must be called each time (issue #14); unknown fields dropped; proto3 only.

## Caveats and trade-offs

Benchmark is first-party, single run per row, no variance reported, small messages only, and the toolchain is old (gcc 8.3.0, Google libprotobuf/libprotoc 3.6.1 as a distro shared library, protobuf-c version not stated). The headline mixes two runs: the Google and protobuf-c -O3 rows date from September 2019 (common.mk then had OPT_SPEED = -O3), while the pbtools -O2 rows come from a January 2020 re-run (commit 6000b5f switched to -O2 and the top-level benchmark Makefile only rebuilds nanopb and pbtools), so the baselines were not re-measured against the pbtools version shown; the current Makefiles would build every library at -O2. Harness differences favour pbtools: its encode loop fills a fixed stack workspace and stores pointers to string literals, Google's encode loop constructs a fresh heap-allocated benchmark::Message every iteration (no Arena, although the proto sets cc_enable_arenas) and copies both \~230-byte strings before SerializeToString into a std::string, and protobuf-c encodes through pack_to_buffer with a ProtobufCBufferSimple callback rather than its direct pack() call (stack structs, no malloc on encode). On decode protobuf-c mallocs and frees the whole message tree per iteration (unpack with the default allocator), Google reuses one message object, and pbtools copies strings into its arena workspace. At -Os pbtools encoding is slower than protobuf-c (3.398 s vs 1.970 s). FlatBuffers decodes in 0.100 s (-O2) only because it decodes lazily. The repo's guessed baseline (msgpack) is wrong: msgpack is not in the benchmark. No commits since 2023-06-04. [retier] Headline mixes a September 2019 -O3 run for Google protobuf 3.6.1 and protobuf-c with a January 2020 -O2 rerun of pbtools only (commit 6000b5f). Baselines handicapped: Google loop heap-allocates a fresh message with no Arena and validates UTF-8 while pbtools never validates; protobuf-c uses pack_to_buffer and mallocs per decode; baseline runtimes are prebuilt distro libraries. pbtools loses at -Os encode (3.398 vs 1.970 s). Security: packed fixed-width repeated fields with a payload length not a multiple of the element size write past the arena allocation (read in lib/src/pbtools.c, untested). N-byte encode buffer holds N-1 bytes; NUL-terminated strings; proto3 only; abandoned since 2023-06-04.

Generates C source from proto3 files with a Python generator; no malloc/free, all allocations come from a caller-supplied workspace (arena) that cannot be freed, so repeated-field lengths cannot change after allocation; generates functions instead of tables, so executable size grows faster than table-driven libraries (README: text 17484 B vs nanopb 21256 B for the benchmark program, but growth is steeper); proto3 only, options, services (gRPC), reserved fields and public imports are not implemented; char must be 8 bits.

## Maintenance

Unmaintained since 2023-06-04 (v0.47.0 on PyPI, 82 stars, MIT). Small enough to vendor for trusted-input embedded use, but patch the packed fixed-width OOB write in decoder_read_repeated before decoding untrusted data, and treat the first-party speedups as harness-inflated: the baselines are from an older run and do extra allocation and UTF-8 work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public benchmark code in the repo (benchmark/pbtools/main.c, benchmark/google/main.cpp, benchmark/protobuf-c/main.c with their Makefiles and benchmark/common.mk), gcc 8.3.0, per-row optimization flags and the CPU (Intel Core i7-4510U @ 2.00GHz) are all stated in benchmark/README.rst, and the rows compare directly against Google protobuf C++ and protobuf-c. The -O3 baseline flags are also in public git history (common.mk had OPT_SPEED = -O3 until commit 6000b5f).
- **Verifier notes:** All headline numbers match benchmark/README.rst exactly and the derived ratios check out. Shortcomings to record: baseline rows (Google, protobuf-c at -O3) are from a September 2019 run not repeated when pbtools was re-measured at -O2 in January 2020; Google's encode loop builds a fresh heap message per iteration without an Arena and protobuf-c uses the slower pack_to_buffer path; first-party single run on gcc 8.3.0 and protobuf 3.6.1; pbtools loses to protobuf-c on -Os encoding; abandoned since 2023-06-04 (MIT, 82 stars, not a fork, not archived).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-52 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/eerimoq/pbtools>
  - <https://github.com/eerimoq/pbtools/commits>
  - <https://github.com/eerimoq/pbtools/tree/master/benchmark>
  - <https://github.com/eerimoq/pbtools/commits/master/benchmark/common.mk>
  - <https://github.com/eerimoq/pbtools/commits/master/benchmark/README.rst>
  - <https://github.com/eerimoq/pbtools/commit/6000b5f>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/README.rst>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/common.mk>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/google/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/protobuf-c/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/pbtools/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/pbtools/main.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/google/main.cpp>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/protobuf-c/main.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/benchmark.proto>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/lib/src/pbtools.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/README.rst>
- **Sources the enricher read:**
  - <https://github.com/eerimoq/pbtools>
  - <https://github.com/eerimoq/pbtools/issues?q=is%3Aissue>
  - <https://github.com/eerimoq/pbtools/issues/4>
  - <https://github.com/eerimoq/pbtools/issues/6>
  - <https://github.com/eerimoq/pbtools/issues/9>
  - <https://github.com/eerimoq/pbtools/issues/10>
  - <https://github.com/eerimoq/pbtools/issues/14>
  - <https://github.com/eerimoq/pbtools/issues/17>
  - <https://github.com/eerimoq/pbtools/commits/master>
  - <https://github.com/eerimoq/pbtools/tree/master/lib>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/README.rst>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/README.rst>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/common.mk>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/benchmark.proto>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/pbtools/main.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/pbtools/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/google/main.cpp>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/google/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/protobuf-c/main.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/benchmark/protobuf-c/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/lib/src/pbtools.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/lib/include/pbtools.h>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/lib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/examples/address_book/generated/address_book.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/tests/main.c>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/tests/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/Makefile>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/setup.py>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/eerimoq/pbtools/HEAD/crate/Cargo.toml>
  - <https://pypi.org/pypi/pbtools/json>
  - <https://raw.githubusercontent.com/protocolbuffers/protobuf/v3.6.1/src/google/protobuf/compiler/cpp/cpp_helpers.cc>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/eerimoq/pbtools`) · [data/wave1/enrich/raw/github_com_eerimoq_pbtools.json](../../../data/wave1/enrich/raw/github_com_eerimoq_pbtools.json) (enrichment confidence 0.85)

</details>
