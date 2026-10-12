# lexindex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust crate of immutable string-to-id dictionaries; front-coded DictIndex comes in smaller than MARISA and XCDAT on the author's 13 corpora.

| | |
|---|---|
| **Beats** | XCDAT 15 (C++ compressed double-array trie dictionary) and MARISA (marisa-trie 0.2.6) |
| **Claimed result** | Smallest structure on 13 of 13 corpora at 1M keys against the campaign's MARISA and XCDAT builds (e.g. words 2.51 vs 2.98 B/key for MARISA rho=2; titles-en 7.21 vs 8.19). HashedDictIndex (closed) lookup 14 to 61 ns against XCDAT 15's 54 to 449 ns at 1M keys. Strict exact-search structures still trail XCDAT 15 on 9 of 13 corpora at 1M keys. |
| **Workload** | Compressed string dictionary (string to dense id and back) over 13 corpora (Wikipedia titles, domains, PyPI names, paths, identifiers, UUIDs, DNA and others) at 1M and 10M keys; measures serialized bytes per key, single-key lookup latency, build time. |
| **Metric** | memory |
| **Hardware** | AMD Ryzen 7 5800HS (8 cores / 16 threads), Fedora 44, measured 2026-09-26 |
| **Compiler and flags** | C++ competitors (MARISA, XCDAT driver) built with c++ -O3 -march=native -std=c++17 (-DNDEBUG for XCDAT and floor drivers) per harness/build.sh; GCC 16.2.1, rustc 1.98.1; lexindex 4.5.2 from crates.io |
| **Adoption** | 3 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/ilgrad/lexindex) · [benchmark](https://github.com/ilgrad/string-index-benchmarks) |

## Verdict

In the author's own harness (string-index-benchmarks; competitors built at pinned commits with c++ -O3 -march=native -std=c++17, GCC 16.2.1, rustc 1.98.1, lexindex 4.5.2 from crates.io, Ryzen 7 5800HS, 2026-09-26), lexindex's smallest index has the smallest serialized file on 13 of 13 corpora at 1M keys against the campaign's MARISA (1 to 3 tries) and the other tries (words 2.51 vs 2.98 B/key), and HashedDictIndex closed answers member-only probes in 14 to 61 ns against XCDAT 15's 54 to 449 ns. Against MARISA at its smallest, paths is a tie (0.04 percent), and the lexindex README states that MARISA's smallest is 5.8 percent smaller on paths, which conflicts with the harness table.

## Use it when

- Static vocabularies, entity catalogs, URL, path or domain lists of 0.5M to 20M keys, where the file and mapped size of the dictionary is the main cost: DictIndex at block 1024 was the smallest structure on all 13 corpora at 1M keys against the harness's MARISA, XCDAT, CoCo-trie, PDT, FST and C2 builds
- Hot string-to-id paths on a closed vocabulary that also need id to key, prefix and range: HashedDictIndex answers id in 14 to 61 ns against XCDAT 15's 54 to 449 ns at 1M keys, at a smaller size than XCDAT
- Rust or Python services (also Polars through lexindex-polars) that want deterministic, mmap-able blobs and safe loaders for blobs from elsewhere
- Prefix counting or range scans: a prefix is an id range in DictIndex, so prefix_count costs two lookups where marisa-trie enumerates every match

## Skip it when

- Exact lookups that must reject unknown keys at trie speed: lexindex's fastest exact structure trails XCDAT 15 on 9 of 13 corpora at 1M keys (5 percent on uuid to 57 percent on pypi), and DictIndex at block 1024, the smallest one, is among the slowest to look up
- When the keys change often: every index is immutable, and Overlay edits work only on StringIndex, CompactHashIndex and PerfectHashIndex
- Path-like or highly shared keys where MARISA tuned to its smallest (many tries, tiny cache) ties or wins: 0.04 percent apart on paths at 1M, and MARISA is smaller once memory-mapped on 5 of 21 rows
- C++ code that needs prefix, range, fuzzy or common-prefix queries: the C ABI exposes only id, ids, contains and key, and leaves out DoubleArrayIndex
- Adversarial query streams: the hashes are unseeded and the fingerprint false-positive rate is a design rate, not a HashDoS or security defence (SECURITY.md)

## How it is fast

DictIndex front-codes sorted keys in blocks of 32 to 1024 split into microblocks of 16 to 32, compresses the suffixes with a per-shard FSST-style 255-symbol table or a packed alphabet over a mined phrase dictionary, and recodes mostly non-ASCII keys into an order-preserving 1-2 byte code. A lookup walks the microblock heads and rejects most entries on their one-byte header without decoding them, and the opt-in route_microblocks() trades about 0.5 B/key of memory for 19 to 31 percent faster id. HashedDictIndex adds an in-crate PHast/PTHash-style minimal perfect hash (about 1.92 bits/key) plus a bit-packed rank per slot, so id is a hash and one read instead of a dictionary search.

## Compared with alternatives

Pick lexindex over xcdat when size or id-to-key, prefix and range matter and you can call Rust or a C handle, or when a closed vocabulary makes HashedDictIndex's hashed id usable; keep xcdat (header-only C++) for the fastest exact lookup that rejects strangers on most corpora, and C2 when you need its MARISA, FST or CoCo variants inside a C++ trie framework. For matching a lexicon against Chinese text, DoubleArrayIndex was faster and smaller than darts-clone on the author's jieba measurement, but darts-clone is the drop-in C++ choice.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | fst 0.4 (with levenshtein); optional memmap2 0.9 (mmap feature, default on), optional pyo3 0.29 (python feature); the C ABI builds as a cdylib or staticlib with --features capi |
| **Minimum toolchain** | Rust 1.85 (edition 2024); Python wheel abi3 for CPython 3.11+ |
| **Platforms** | any Rust target, 32-bit and wasm32-unknown-unknown included (without mmap); benchmarks only on x86-64 (Ryzen 7 5800HS) |
| **Thread safety** | Indexes are immutable after build and the README mentions free-threaded CPython use; the C ABI's lexindex_last_error is per thread. No explicit Send/Sync statement was found in what was read. |
| **Drop-in for the baseline** | partial: it does the same string-to-dense-id job as MARISA or XCDAT but with its own API, ids and blob formats; from C++ it is reachable only through the C handle API |

## Gotchas

- HashedDictIndex closed (id_unchecked) and ClosedHashIndex return some valid id for a key that was never inserted. The 14 to 61 ns headline is that mode; use the 8-bit fingerprint (one more byte a key, 2.8 to 7.4x faster than XCDAT 15 per the README) or the dictionary search when strangers can arrive.
- Blob formats change across major versions: 2.0 and 4.0 changed the key hash, so pre-4.0 hash blobs and BDX1/BDX2 dictionaries are refused and must be rebuilt from the keys; ids are not stable across key sets. Only 4.5.x is supported, and 4.5.2 fixed a crafted DictIndex blob that could make a routed lookup panic.
- Loaders are safe Rust on arbitrary bytes, but StringIndex::from_bytes can panic on a crafted blob that carries a valid checksum (a fuzzer specimen is committed); use from_untrusted_bytes for blobs from strangers. load_mmap is unsafe because the file must not change while it is mapped, and through the C ABI any panic aborts the process.
- Keys are raw bytes with no normalization (normalize before build and query); the C ABI rejects non-UTF-8 keys. DoubleArrayIndex refuses corpora that need more than 2^23 slots or keys (7 of 13 at 1M keys).

## Known shortcomings

- Tier A on the ilgrad/string-index-benchmarks tables (-O3 -march=native, Ryzen 7 5800HS, GCC 16.2.1), but the harness is written by lexindex's own author. Rust.
- README says MARISA at its smallest is 5.8% smaller than lexindex on paths, but the harness table shows lexindex 0.04% smaller (a tie); the '13 of 13' holds only against the campaign's MARISA builds. Harness README says lexindex trails XCDAT 15 on 9 of 13 corpora while the lexindex README says 10. The 14-61 ns closed-hash lookup returns an id for unknown keys. The C ABI covers only id, ids, contains and key (no DoubleArrayIndex) and any panic aborts the process. StringIndex::from_bytes can panic on a crafted blob (use from_untrusted_bytes); 4.5.2 fixed a DictIndex routed-lookup panic. Blob formats break across major versions. Unseeded hashes, no HashDoS defence. Benchmark author is the library author.

## Caveats and trade-offs

Harness author is the lexindex author (conflict of interest, disclosed in the README; harness pins every competitor, fetches lexindex 4.5.2 from crates.io and publishes JSON artifacts). The 14 to 61 ns closed HashedDictIndex lookup returns some id for keys that were never inserted, so it is not equivalent to the tries' exact search. lexindex's fastest exact search trails XCDAT 15 on 9 of 13 corpora at 1M keys (5 percent on uuid to 57 percent on pypi), wins dna (0.95x) and numeric (0.55x); at 10M keys it wins dna, numeric, urls and titles-en and loses opaque (1.36x). Against MARISA at its smallest (1 to 32 tries, tiny cache, untimed) the size margin shrinks to 0.04 percent on paths and 3.8 percent on titles-en at 1M, 0.11 to 0.30 percent on titles-en/urls at 10M, and MARISA is smaller once loaded (mmap) on five rows. The numeric corpus win (301 bytes total) is a degenerate dense-id case. Baselines are succinct tries (MARISA, XCDAT, CoCo-trie, PDT, FST, C2 variants), not SDSL or sux directly. String-index-benchmarks repo has 0 stars.

Immutable string-to-id indexes only. Seven index types trade size against speed: front-coded DictIndex is smallest but slowest to look up; HashedDictIndex adds a perfect hash for fast id lookup. Rust crate with Python bindings and a C ABI, so usable from C++ only through the C interface.

## Maintenance

Very active single-maintainer project (version 4.5.2, commits through 2026-09-29, 3 stars, no known users, 4 open issues that are all documentation or feature requests); MIT, with a fuzzed loader and a written threat model, but the benchmark author is the library author.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The string-index-benchmarks README tables (artifact results/frontier-1m-2026-09-26-arz-be75a38.json) show lexindex DictIndex 1024 smallest on 13 of 13 corpora at 1M keys (words 2.51 vs MARISA rho=2 2.98, titles-en 7.21 vs 8.19) and HashedDictIndex closed at 14 to 61 ns vs XCDAT 15 at 54 to 449 ns; harness code is public (harness/build.sh compiles MARISA and XCDAT with c++ -O3 -march=native -std=c++17, -DNDEBUG for XCDAT and the floor/resident drivers), toolchain GCC 16.2.1 / rustc 1.98.1 and CPU AMD Ryzen 7 5800HS are stated.
- **Verifier notes:** All quoted numbers match the README tables of ilgrad/string-index-benchmarks. Metadata matches the lexindex repo page (MIT, 3 stars, latest commits 2026-09-29). Main claim is size; speed wins are confined to the closed-lookup variant and a few corpora.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/ilgrad/string-index-benchmarks>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/harness/build.sh>
  - <https://github.com/ilgrad/lexindex>
  - <https://github.com/ilgrad/lexindex/commits>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/README.md>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/include/lexindex.h>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/src/capi.rs>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/src/dict_index.rs>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/src/hashed_dict.rs>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/src/closed_hash.rs>
  - <https://raw.githubusercontent.com/ilgrad/lexindex/HEAD/src/mphf.rs>
  - <https://github.com/ilgrad/lexindex/tree/main/src>
  - <https://github.com/ilgrad/lexindex/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ilgrad/lexindex`) · [data/wave9/enrich/raw/github_com_ilgrad_lexindex.json](../../../data/wave9/enrich/raw/github_com_ilgrad_lexindex.json) (enrichment confidence 0.75)

</details>
