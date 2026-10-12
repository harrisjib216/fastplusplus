# fastconstmap

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Immutable string-to-uint64 map for Python, C11 core, built on binary fuse filters; beats CPython dict lookups and memory.

| | |
|---|---|
| **Beats** | CPython dict |
| **Claimed result** | README Benchmark block (Apple M4 Max, Python 3.14.5, 1,000,000 string keys, each queried once in random order). Single lookup: dict[k] 336.1 ns/op vs ConstMap[k] 95.2 ns/op (about 3.5x) and VerifiedConstMap[k] 112.3 ns/op (about 3.0x; this is the dict-like variant). Batched, 2000 batches of 2000 keys, cold cache: a dict list comprehension takes 148.7 ns/op. ConstMap.get_many takes 24.2 ns/op (about 6.1x; both sides build a Python list), and get_many_into takes 14.2 ns/op (about 10.5x; it writes raw uint64s into a buffer with no list). VerifiedConstMap takes 33.7 ns/op with get_many (about 4.4x) and 23.9 with get_many_into (about 6.2x). All of these ratios are derived from page data. Hot-cache get_many_into is 6.1 ns/op, but the page has no hot-cache dict measurement, so no ratio against dict applies to it. Memory: 9.04 bytes/key vs 118.38 bytes/key for the dict counting table, keys and values, which the page states as 13.1x. |
| **Workload** | Python benchmark (benchmarks/benchmark.py) with 1,000,000 'key-{i}-{hex}' string keys. Single lookups query each key once in random order, from a list built in that order. Batched lookups run 2000 batches of 2000 randomly drawn keys, cold (rotating through 64 distinct batches) or hot (one replayed batch). The dict list comprehension is measured cold only, against ConstMap and VerifiedConstMap get_many and get_many_into. The C-level benchmarks/bench_batch.c compares only batched against looped lookups, with no dict baseline. |
| **Metric** | latency |
| **Hardware** | Apple M4 Max is the only machine the dict comparison ran on. The Intel Xeon Gold 6548N appears only in the C-level and Python-API batching tables, which have no dict baseline. |
| **Compiler and flags** | The C11 extension is built by setup.py with -O3 -std=c11 (/O2 on Windows). The C compiler and its version are not stated, and the README does not say whether the benchmarked build was a wheel or a source build. The dict comparison ran on Python 3.14.5 via `python benchmarks/benchmark.py 1000000`. The C-level benchmarks/bench_batch.c is built with `cc -O3 -std=c11` and has no dict baseline. |
| **Adoption** | 59 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/lemire/fastconstmap) · [benchmark](https://github.com/lemire/fastconstmap/blob/main/README.md) |

## Verdict

The author's own benchmarks/benchmark.py ran on an Apple M4 Max with CPython 3.14.5 and 1M 'key-{i}-{hex}' strings, each queried once in random order. VerifiedConstMap[k] took 112.3 ns vs dict[k] 336.1 ns (\~3.0x, derived); in cold 2000-key batches, VerifiedConstMap.get_many took 33.7 ns/key and ConstMap.get_many_into 14.2 ns/key, vs 148.7 ns/key for a dict comprehension (\~4.4x and \~10.5x, derived), with 9.04 vs 118.38 bytes/key. The numbers are from the pre-0.10 XXH3 build (the README says to add 1-5 ns per single lookup and 1-4 ns/key batched for today's XXH64 default), the extension's C compiler is not named, and there is no C/C++ comparison against std::unordered_map.

## Use it when

- Python processes that load a large, fixed string-to-int table once (ID maps, vocabularies; 1M keys measured) and query it many times. VerifiedConstMap[k] took 112 ns vs 336 ns for dict[k] on an M4 Max.
- Bulk lookups where keys already arrive as a list. get_many_into into an array('Q') or numpy uint64 buffer measured 14.2 ns/key (ConstMap) and 23.9 ns/key (VerifiedConstMap), vs 148.7 ns/key for a dict list comprehension.
- Memory-constrained deployments. It takes \~9 bytes/key (ConstMap) or \~18 (verified classes), vs \~118 bytes/key for a dict with its str keys and int objects, because the keys themselves are not stored.
- Pre-fork or multiprocessing worker pools that should share one read-only table. write_into puts it in a named SharedMemory block once, and from_buffer opens it in each process without a copy.
- Pipelines that build the table in Go (constmap) or Rust (rsconstmap) and read it from Python or C, because the default XXH64 file formats are byte-compatible on little-endian hosts.

## Skip it when

- Tables that change. Any insert or delete means a full rebuild: 0.145 s for 1M keys vs 0.004 s to copy a dict. The build needs the source dict plus transient C buffers of roughly 55-60 bytes/key (by the allocations in constmap.c).
- ConstMap when absent keys can be queried. It returns garbage with no error. Use a verified class, at twice the memory.
- Non-integer values, keys other than str/bytes, more than 2^32-1 keys, or code that needs to iterate keys or items. Keys are not stored and cannot be recovered.
- Small or cache-resident tables looked up one key at a time. No dict comparison below 1M keys is published, and the author says single m[k] cost (50-120 ns) is mostly Python call overhead, so the gain there is not documented.
- Free-threaded CPython (3.13t/3.14t). cp314t wheels are published, but the module uses single-phase init without PyUnstable_Module_SetGIL, so importing it re-enables the GIL with a warning. Lookups also never release the GIL.

## How it is fast

It uses the binary fuse filter construction (Graf & Lemire, ACM JEA 2022) as a static function. Each key is hashed (XXH64 by default, XXH3 optional) to three positions in adjacent segments of an array of about 1.125n 64-bit words, and hypergraph peeling sets the cells so that XOR-ing the three returns the value. A lookup is one hash, three independent loads and two XORs, with no probe loop and no key comparison, so the three cache misses overlap. Batched calls hash a block of 8 keys before gathering any values, which keeps 24 loads in flight at once. get_many_into writes raw uint64s so no PyLong is boxed per key, and PairedVerifiedConstMap stores value and check side by side so each slot is read as one 128-bit SSE2/NEON load.

## Compared with alternatives

Pick it over frozen or qlibs/mph (constexpr key sets fixed at C++ compile time) when the key set is large, known only at runtime, or must be serialized and shared across processes or languages. Versus constmap (Go), which shares the algorithm and file format, choose by host language; choose fph-table instead if you need occasional inserts or a C++ std::unordered_map-like API.

## Integration

| | |
|---|---|
| **Form** | module (pip wheels); the C core is a source-drop: src/constmap.c, src/constmap.h (extern "C"-guarded) and a vendored xxhash.h |
| **Dependencies** | none at runtime; vendors xxHash 0.8.2 (BSD-2), and a #error breaks the build if that header's version changes; links libm on non-Windows |
| **Minimum toolchain** | C11 compiler (setup.py passes -O3 -std=c11, /O2 on MSVC); Python &gt;= 3.8 per pyproject.toml. CI tests Python 3.9, 3.12 and 3.13 on Ubuntu, macOS and Windows. Compiler versions are not documented. |
| **Platforms** | PyPI wheels for CPython 3.8-3.14 (plus 3.14t) on Linux x86-64/aarch64 (manylinux and musllinux), macOS x86-64/arm64/universal2 and Windows AMD64. No 32-bit wheels. SSE2 (x86-64) or NEON (AArch64) is used for the paired layout, with a scalar fallback elsewhere. Zero-copy from_buffer and cross-language files need a little-endian host; from_bytes (copying) also loads on big-endian. |
| **Thread safety** | Maps are immutable after construction. The README says concurrent readers need no locking (stated for the shared-memory pattern). Construction releases the GIL; lookups, get_many and get_many_into hold it. The module does not declare free-threading support. |
| **Drop-in for the baseline** | partial — VerifiedConstMap/PairedVerifiedConstMap match dict reads (m[k] raising KeyError, get(k, default), `in`, len). They are built from an existing dict, immutable, limited to str/bytes keys and 64-bit int values, and have no iteration. ConstMap drops missing-key detection entirely. |

## Gotchas

- The verified classes use 2\*\*64-1 as their internal not-found sentinel. A key stored with value 2\*\*64-1, or -1 (stored as two's complement), therefore raises KeyError or returns the default as if absent. Negative values in general come back as unsigned integers; the test suite checks 2\*\*64-1 only on ConstMap.
- Only the PairedVerifiedConstMap readers check that the header's segment parameters match the array length. ConstMap and VerifiedConstMap loads check only magic, length and an FNV-1a checksum (not tamper-resistant), and lookups index the array without bounds checks. Treat .cmap/.vmap files and buffers as trusted input.
- from_buffer borrows the memory: the buffer must stay alive and unmodified, and you must `del` the map before shm.close(). It also needs an 8-byte-aligned buffer, so a Go/Rust CMAP0001 file (28-byte header) cannot be viewed, only copied with load/from_bytes. Maps from Go/Rust report len() == 0.
- The key hash is fixed into each file. The default XXH64 (shared with Go/Rust) costs about 1-2 ns more per lookup than hash='xxh3', whose files only fastconstmap reads. Files written by 0.9 and earlier stay XXH3 and can only be moved to the shared format by rebuilding from the original keys.

## Caveats and trade-offs

First-party benchmark by the library author (Daniel Lemire). The baseline is CPython's dict, not std::unordered_map. The C core (src/constmap.c, src/constmap.h) is usable from C/C++, but no C/C++ hash-map baseline is measured. The README Benchmark block was last regenerated on 2026-08-27 (commit 74de1cea, XXH3 key hash) and predates v0.10.0, which made XXH64 the default. For the current default, the README says to add roughly 1-5 ns to a single m[k] and 1-4 ns/key to the batched columns, and the block lacks the PairedVerifiedConstMap rows the current script prints. ConstMap stores no keys and returns garbage for absent keys, so VerifiedConstMap (112.3 ns, about 3.0x) is the semantically comparable variant. The author says single-lookup times are dominated by Python call overhead. Construction takes 0.145 s vs 0.004 s for dict(d), a copy of an existing dict, at 1M keys. The dict memory figure counts the key strings and int objects, which ConstMap does not keep. The C compiler and version are unstated.

Immutable static map only: all keys must be known before construction, unusable as a general drop-in for dict where keys are added/removed at runtime. C core with a Python C-extension wrapper, so overhead/benefit differs when called from pure C vs through the Python API; author notes single-lookup numbers are dominated by Python call overhead, not raw map cost.

## Maintenance

Actively maintained by Daniel Lemire (v0.10.0 released 2026-09-17, no issues filed). It is Apache-2.0 and pip-installable on every mainstream OS, and the C core is two files plus xxhash.h, easy to vendor into a C/C++ project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README 'Benchmark' block compares ConstMap and VerifiedConstMap against CPython's dict on a stated Apple M4 Max with Python 3.14.5, using the public benchmarks/benchmark.py, and setup.py sets -O3 -std=c11. The C compiler that built the extension is never named or versioned. The block was also last regenerated on 2026-08-27 for the XXH3-hash 0.9.x build, so it does not reflect the current XXH64 default. That makes it first-party with partial methodology, which is tier C.
- **Verifier notes:** Every quoted number is in the README Benchmark block. However, the record's '\~24x' compared hot-cache get_many_into (6.1 ns) with a cold-only dict figure, which is not like for like, so that ratio was dropped. The 10x and 3.5x ratios were derived, not stated, and are now marked so. Downgraded A to C because the C compiler is unstated and the published numbers are from the pre-0.10 XXH3 build. Metadata checked via gh: Apache-2.0 (vendored xxHash is BSD-2), 59 stars, last commit 2026-09-17, not archived, not a fork, active.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lemire/fastconstmap>
  - <https://github.com/lemire/fastconstmap/blob/main/README.md>
  - <https://github.com/lemire/fastconstmap/blob/main/benchmarks/benchmark.py>
  - <https://github.com/lemire/fastconstmap/blob/main/benchmarks/bench_batch.c>
  - <https://github.com/lemire/fastconstmap/blob/main/setup.py>
  - <https://github.com/lemire/fastconstmap/blob/main/pyproject.toml>
  - <https://github.com/lemire/fastconstmap/blob/main/.github/workflows/test.yml>
  - <https://github.com/lemire/fastconstmap/commits/main/README.md>
  - <https://github.com/lemire/fastconstmap/commit/74de1cea>
  - <https://github.com/lemire/fastconstmap/commit/47c9f945>
- **Sources the enricher read:**
  - <https://github.com/lemire/fastconstmap>
  - <https://github.com/lemire/fastconstmap/blob/main/README.md>
  - <https://github.com/lemire/fastconstmap/blob/main/src/constmap.h>
  - <https://github.com/lemire/fastconstmap/blob/main/src/constmap.c>
  - <https://github.com/lemire/fastconstmap/blob/main/src/fastconstmap_module.c>
  - <https://github.com/lemire/fastconstmap/blob/main/fastconstmap/__init__.py>
  - <https://github.com/lemire/fastconstmap/blob/main/fastconstmap/_fastconstmap.pyi>
  - <https://github.com/lemire/fastconstmap/blob/main/setup.py>
  - <https://github.com/lemire/fastconstmap/blob/main/pyproject.toml>
  - <https://github.com/lemire/fastconstmap/blob/main/.github/workflows/test.yml>
  - <https://github.com/lemire/fastconstmap/blob/main/.github/workflows/buildwheels.yml>
  - <https://github.com/lemire/fastconstmap/blob/main/benchmarks/benchmark.py>
  - <https://github.com/lemire/fastconstmap/blob/main/benchmarks/bench_batch.c>
  - <https://github.com/lemire/fastconstmap/blob/main/tests/test_constmap.py>
  - <https://github.com/lemire/fastconstmap/issues?q=is%3Aissue>
  - <https://github.com/lemire/fastconstmap/pulls?q=is%3Apr>
  - <https://github.com/lemire/fastconstmap/commits/main>
  - <https://github.com/lemire/fastconstmap/releases>
  - <https://pypi.org/pypi/fastconstmap/json>
  - <https://docs.python.org/3/howto/free-threading-extensions.html>
  - <https://github.com/lemire/constmap>
  - <https://github.com/serge-sans-paille/frozen>
  - <https://github.com/renzibei/fph-table>
  - <https://github.com/qlibs/mph>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/lemire/fastconstmap`) · [data/wave1-phf/enrich/raw/github_com_lemire_fastconstmap.json](../../../data/wave1-phf/enrich/raw/github_com_lemire_fastconstmap.json) (enrichment confidence 0.85)

</details>
