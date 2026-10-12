# cmp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🟡 stale

> Tiny allocation-free C89 MessagePack reader/writer; smaller than msgpack-c but 13-30% slower on write in the only shootout.

| | |
|---|---|
| **Beats** | msgpack-c (msgpack C API, v1.3.0 in the shootout) |
| **Claimed result** | No speed win exists. The project only says 'Fast, Lightweight, Flexible, and Robust' (no numbers). The independent shootout shows CMP v14 slower than msgpack C 1.3.0 on write: 7.33 us vs 6.42 us (small) and 660.19 us vs 544.24 us (large) on the AMD Phenom II X6 1090T desktop; 89.75 us vs 69.21 us (small) and 9206.05 us vs 8142.64 us (large) on a Raspberry Pi. CMP is the smallest MessagePack build on the desktop (3232 vs 4088 bytes for write) but not on the Raspberry Pi size build (2324 vs 1528 bytes). |
| **Workload** | Encoding (write test) of randomly generated schemaless data (2367-byte small and 248571-byte large MessagePack objects) into a growable buffer in the ludocode/schemaless-benchmarks suite, with the hash cost subtracted. CMP's incremental reader is also timed, but msgpack-c has no incremental-parser row in the suite, so only the write test is a like-for-like comparison against the baseline. |
| **Metric** | throughput |
| **Hardware** | AMD Phenom II X6 1090T desktop; first-generation Raspberry Pi Model B rev2 (ARMv6) |
| **Compiler and flags** | GCC 5.3.0 on Arch Linux, -Wall -O3 -flto -fno-fat-lto-objects -DPIC -fPIC -DNDEBUG, each test run 7 times for 10 s, best and worst dropped |
| **Adoption** | 370 stars; listed on msgpack.org |
| **Last commit** | 2025-08-06 |
| **Links** | [repository](https://github.com/camgunz/cmp) · [benchmark](https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/README.md) |

## Verdict

In ludocode/schemaless-benchmarks (2016, written by MPack's author; GCC 5.3.0 -O3 -flto, hash time subtracted), encoding random schemaless data into a growable buffer took CMP v14 7.33 us vs msgpack C 1.3.0 6.42 us (small) and 660.19 vs 544.24 us (large) on an AMD Phenom II X6 1090T, and 89.75 vs 69.21 us and 9206.05 vs 8142.64 us on a first-generation Raspberry Pi, with identical output hashes; CMP is 13-30% slower and the project publishes no numbers of its own. The harness code (cmp-write.c, buffer.h) treats both libraries alike: same object walk, a doubling buffer starting at 4 KB for CMP, one pass per run.

## Use it when

- Firmware or other heap-less targets that need MessagePack in strict C89 with no malloc and no internal buffers (an ESP-IDF component CMakeLists.txt is shipped).
- Streaming MessagePack straight to or from a file, socket or UART through your own read/write callbacks, without staging a whole message in RAM.
- Schema-known messages decoded with typed readers (cmp_read_int, cmp_read_str) instead of building a tree.
- Projects that want an MIT, two-file vendorable codec; c-toxcore vendors a TokTok fork as third_party/cmp.

## Skip it when

- Encode throughput matters: msgpack C 1.3.0 was 13-30% faster on every write row and MPack 0.8.1 about 3.4x faster (2.13 vs 7.33 us, small data, desktop) in the same shootout.
- You need a DOM, random access or zero-copy reads: every value is memcpy'd through the read callback, and zero-copy reading (issue #29) has been open since 2016.
- Size-optimized ARM builds: in the Raspberry Pi -Os build msgpack C's write path was smaller (1528 vs 2324 bytes) and still faster (67.35 vs 100.66 us).
- You need stable versioning: no semver, the author says no version is guaranteed compatible with another, and only tagged releases are called stable.

## How it is fast

It is not faster than msgpack-c; its design goal is minimal code and no buffering. Every value goes out as a one-byte type marker through one indirect ctx-&gt;write call and its length or payload through another, with byte swapping done by shift-based be16/be32/be64 helpers behind a runtime is_bigendian() test (compile-time if WORDS_BIGENDIAN is defined). That keeps the code to about 3.2 KB in the shootout's -O3 write build, but the extra callback per value is a plausible reason (our inference, not measured) why it trails msgpack C and MPack on encode throughput.

## Compared with alternatives

The catalogued siblings are C++ JSON or schema serializers (BitSerializer's MsgPack path, zpp::bits, Cap'n Proto), so pick CMP only when you need MessagePack from plain C with no allocation and tiny code; if C encode speed matters, MPack (ludocode/mpack, not yet catalogued) beat both msgpack-c and CMP in the same shootout.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (stdbool.h, stddef.h, stdint.h, string.h); the test suite needs cmocka |
| **Minimum toolchain** | C89 plus fixed-width integer types and bool (tests need C99) |
| **Platforms** | any; endianness detected at runtime or set with WORDS_BIGENDIAN; CMP_NO_FLOAT for FPU-less targets |
| **Thread safety** | a context must not be shared between threads; one context per thread is fine (README 'thread aware') |
| **Drop-in for the baseline** | no |

## Gotchas

- The README example and examples/example1.c and example2.c define the skipper as 'return fseek(...)'; fseek returns 0 on success, so the bool is false on every successful skip and true on failure. Since the 2025 commit 'Don't ignore errors reported by skip_bytes()' (PR #81, merged 2025-08-06), skips through that copied skipper fail; return fseek(...) == 0 instead.
- cmp_read_str needs a buffer of at least str_size + 1 bytes (it NUL-terminates); when the string is too long it fails after consuming the marker and length but not the payload, leaving the stream mid-object, so the caller must skip str_size bytes itself.
- Passing NULL read or write callbacks is allowed by cmp_init, but calling a read or write function then crashes (no check, per cmp.h); CMP_NO_FLOAT changes the ABI; cmp_skip_object_limit is deprecated after issue #45 (wrong on nested arrays), so use cmp_skip_object_flat or cmp_skip_object_no_limit.
- The shootout ran CMP v14, which predates v16's fix for float bytes mangled on little-endian machines (issue #24, cmp_write_float/cmp_read_float) and v17's extra skip argument to cmp_init, so its harness no longer compiles against current CMP. The test writes only doubles and its output hashes matched msgpack-c, so the timed rows are not affected.

## Known shortcomings

- Not faster: in the MPack author's 2016 shootout (GCC 5.3.0, CMP v14, growable buffer) msgpack-c 1.3.0 beats CMP on every write row (desktop 6.42 vs 7.33 us and 544.24 vs 660.19 us; RPi 69.21 vs 89.75 and 8142.64 vs 9206.05; Chromebook 11.90 vs 14.01 and 1338.33 vs 1463.82); same output hashes, so the numbers are real. The only win is desktop code size (3,232 vs 4,088 bytes; smaller msgpack-c under -Os on RPi); CMP's incremental reader beats msgpack-c's tree unpacker only on large data, a cross-category comparison. No first-party numbers. Kept as a documented not-faster entry.
- No speed win: 13-30% slower than msgpack-c 1.3.0 on write and MPack is 3.4x faster, in a fair shootout harness (same object walk, doubling buffer, matching hashes). The benchmarked v14 predates the v16 float byte-mangling fix (#24); the test writes only doubles so the rows are unaffected; the harness's 4-argument cmp_init no longer compiles (skip argument added in v17). Copy-paste bug: README and examples/example1.c, example2.c skipper 'return fseek(...)' reports failure on every successful skip, which breaks skips since the 2025 skip_bytes error fix (PR #81). cmp_read_str's too-long error leaves the stream mid-object. Latest release v20 lacks the 2024-2025 fixes.

## Caveats and trade-offs

Not faster than the named baseline. Every write row in the shootout (README and full-results-extended.md) has CMP v14 slower than msgpack C 1.3.0: desktop 7.33 vs 6.42 us small and 660.19 vs 544.24 us large; Raspberry Pi 89.75 vs 69.21 us and 9206.05 vs 8142.64 us; the extended results add an Intel Celeron 2957U Chromebook with 14.01 vs 11.90 us small and 1463.82 vs 1338.33 us large. Both write tests produce the same output hash (1a9c6681 small, b4ac134d large), so the numbers are real. CMP has no tree parser; its incremental reader is faster than msgpack C's tree unpacker on large data (533.46 vs 750.87 us desktop, 5713.58 vs 10287.89 us Raspberry Pi, derived from page data) but slower on small desktop data (7.43 vs 6.47 us), and that is a cross-category comparison, not a like-for-like win. The shootout was written by the author of MPack (a competitor; its own disclaimer says it may be biased), dates from 2016 (GCC 5.3.0, CMP v14, msgpack-c 1.3.0; the MPack README's feature table now lists CMP v19 and msgpack-c v3.3.0), and the CMP write test uses a harness-supplied growable buffer (buffer.h) because CMP has none, which the author notes is unfair for embedded comparisons. CMP's only measured advantage is code size in the desktop speed build (3232 vs 4088 bytes for write); in the Raspberry Pi -Os build msgpack C is smaller (1528 vs 2324 bytes). No numbers anywhere support a speed claim; candidate for the not-faster shortcoming list.

No internal buffers and no heap allocation, about 4k lines in cmp.c/cmp.h, C89, user supplies read/write/skip callbacks (no growable buffer, no tree parser). Small and portable rather than fast.

## Maintenance

Low activity (last commit 2025-08-06, latest tagged release v20, which predates the 2024 cleanups and the 2025 skip-error fix) but MIT-licensed and two files, so easy to vendor; TokTok maintains a fork for c-toxcore.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** No numbers anywhere show a speed win: the CMP README only has a 'Fast, Lightweight, Flexible, and Robust' heading with qualitative text. The ludocode/schemaless-benchmarks shootout would meet tier-A methodology (public code src/cmp/cmp-write.c and src/msgpack/msgpack-c-pack.c, GCC 5.3.0, -O3 -flto flags, AMD Phenom II X6 1090T), but it shows CMP v14 slower than msgpack C 1.3.0 on every write row, so it is evidence against the claim, not for it.
- **Verifier notes:** All numbers in claimed_speedup match the shootout README rows for CMP (v14) and msgpack C (1.3.0); metadata checked on github.com (370 stars, 85 forks, MIT, not archived, not a fork, last commit 2025-08-06, stale). Keep as a documented not-faster entry: shortcoming 'slower than msgpack-c on write in an independent (MPack-author) shootout; no first-party numbers; only wins on desktop code size'. Not a reject because the evidence is valid, just unfavourable.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** ludocode shootout (verifier, not faster); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/full-results-extended.md>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/cmp/cmp-write.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/msgpack/msgpack-c-pack.c>
  - <https://raw.githubusercontent.com/ludocode/mpack/HEAD/README.md>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/README.md>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/LICENSE>
  - <https://github.com/camgunz/cmp>
  - <https://github.com/camgunz/cmp/commits>
- **Sources the enricher read:**
  - <https://github.com/camgunz/cmp>
  - <https://github.com/camgunz/cmp/commits>
  - <https://github.com/camgunz/cmp/releases>
  - <https://github.com/camgunz/cmp/issues?q=is%3Aissue>
  - <https://github.com/camgunz/cmp/issues/24>
  - <https://github.com/camgunz/cmp/issues/52>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/README.md>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/cmp.h>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/cmp.c>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/Makefile>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/examples/example1.c>
  - <https://raw.githubusercontent.com/camgunz/cmp/HEAD/examples/example2.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/full-results-extended.md>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/cmp/cmp-write.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/cmp/cmp-read.c>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/common/buffer.h>
  - <https://raw.githubusercontent.com/ludocode/schemaless-benchmarks/HEAD/src/msgpack/msgpack-c-pack.c>
  - <https://raw.githubusercontent.com/TokTok/c-toxcore/HEAD/.gitmodules>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/camgunz/cmp`) · [data/wave1/enrich/raw/github_com_camgunz_cmp.json](../../../data/wave1/enrich/raw/github_com_camgunz_cmp.json) (enrichment confidence 0.8)

</details>
