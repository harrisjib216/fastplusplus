# BTreePlus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C#` · `MIT for the Community Edition NuGet package (binary only) and the demo/docs repo; the engine source is not published; the Pro/Enterprise Edition is proprietary (private NuGet feed plus license token)` · 🟢 active

> Binary-only fixed-width B+Tree index for .NET; vendor claims 4.4-7x faster bulk inserts than SQLite (paid Pro build).

| | |
|---|---|
| **Beats** | SQLite |
| **Claimed result** | 4M rows: 4.53s (SQLite) vs 1.03s (BTreePlus Pro) = 4.4x; 1B rows: 2410s (SQLite) vs 346s (BTreePlus Pro) = 7x; also \~16% faster than PostgreSQL on a 1B-row WAL-enabled insert (6m08s vs 5m10s) |
| **Workload** | Bulk insert benchmarks of 4M and 1B rows with 32KB pages on NVMe under .NET 9.0/Linux; separate 1-billion-record (14-byte payload) bulk insert vs PostgreSQL with WAL enabled on both. |
| **Metric** | throughput |
| **Hardware** | NVMe SSD (SQLite comparison, exact CPU not stated); Intel i9-13900 + Samsung 990 PRO NVMe (PostgreSQL comparison) |
| **Compiler and flags** | .NET 9.0 |
| **Adoption** | 9 stars |
| **Last commit** | 2026-01-23 |
| **Links** | [repository](https://github.com/koyllis/BTreePlus) · [benchmark](https://www.nuget.org/packages/BTreePlus) |

## Verdict

According to the vendor's NuGet README (the only evidence), the paid BTreePlus Pro, using 32 KB pages on NVMe under .NET 9.0/Linux, bulk-inserted 4M rows in 1.03 s vs 4.53 s for SQLite (4.4x) and 1B rows in 346 s vs 2410 s (7x), with no CPU, SQLite pragmas, batching method or harness published. A separate i9-13900 + Samsung 990 PRO run loaded 1B 14-byte records in 5m10s vs PostgreSQL's 6m08s (\~1.19x throughput), labelled 'WAL enabled for both engines' even though the same README says BTreePlus has no WAL.

## Use it when

- A .NET process that needs a local sorted index over fixed-width keys (big-endian Int64 IDs, Unix timestamps, padded product codes) with small fixed-size values, e.g. a POS/kiosk secondary index or a log keyed by sequence number.
- Loading tens of millions to billions of fixed-width records in key order when losing uncommitted work on a crash is acceptable. This is the shape of the published SQLite and PostgreSQL runs.
- Hot-path point lookups that must not allocate: Find writes into a caller-supplied Span&lt;byte&gt;, so a SQL engine's parsing and row materialisation are avoided.
- You are prepared to evaluate and license the commercial Pro Edition. Every published speedup is for that build (page cache plus Bulk Insert), not for the free package.

## Skip it when

- You need source you can audit, patch or vendor. The engine is closed, and the MIT license covers only the free binary and the docs.
- You need crash-safe atomic commits. The NuGet README says it is 'not journaling-based' and has no WAL: power loss during a write can lose the latest uncommitted operation, and consistency is promised only after a successful Commit().
- Variable-length keys or values, secondary queries, multi-statement transactions, or concurrent readers. Each tree has one Monitor lock that serialises Find, Insert, Erase and Commit.
- You expect the free Community build to be fast. The vendor calls it 'not optimized for speed' (page cache disabled, \~418K inserts/s in the PDF), so the 4.4x/7x figures do not apply to it.
- Production-critical use generally. It has 9 GitHub stars, zero issues, one Show HN post with no comments and no independent benchmarks. The release DLL even ships its delete/rebalance test suite as a public class (DeleteEdgeCases) with a hard-coded /home/mmh/... log path and 'ROUTING BUG DETECTED' repro strings.

## How it is fast

It has no SQL or VM layer: fixed-width key/value slots sit directly in fixed-size pages (pageSize x 512 bytes, up to 64 KB) and are compared as raw bytes. The vendor attributes the headline numbers mainly to a write-back page cache with deferred flush: dirty pages are written at Commit(), at a byte watermark or by a \~1 s auto-commit, and the PDF gives \~3.16M inserts/s with the cache on vs \~418K/s with it off. Other speed paths are an append fast path for monotonically increasing keys (TryAppendFastPath in the DLL), a bottom-up BulkLoad into an empty tree (0.90 leaf fill) and FNV-1a hash sharding across several trees (ShardManager) for parallel batch inserts. It also has no journal (no WAL or rollback journal), so it avoids the double write SQLite pays for crash safety.

## Compared with alternatives

For .NET, ZoneTree (MIT, source on GitHub, a transactional ACID LSM engine that also reports beating SQLite) is the default pick. Choose BTreePlus only if you want a minimal fixed-width B+Tree file with a published on-disk format that third-party readers can parse, and you are willing to license the closed Pro build to get the advertised speed.

## Integration

| | |
|---|---|
| **Form** | NuGet package (binary-only managed DLL btree.dll, \~137 KB; no source) |
| **Dependencies** | System.Memory &gt;= 4.5.5 (the netstandard2.0 dependency; the README's 'zero dependencies' ignores it); no native libraries |
| **Minimum toolchain** | .NET Standard 2.0 (.NET Core 2.0+ / .NET Framework 4.6.1+ per the PDF); vendor benchmarks used .NET 9.0 |
| **Platforms** | any .NET runtime; pure managed code. Release notes claim Windows, Linux and ARM edge devices. |
| **Thread safety** | Each tree has one Monitor lock. Insert, Find and Erase take it via Monitor.TryEnter with a timeout when bLock=true (the default), so calls are safe but fully serialised, readers included, and a lock timeout raises an exception. Parallelism comes only from ShardManager spreading keys over several trees. |
| **Drop-in for the baseline** | no |

## Gotchas

- In the public 1.3.1 DLL the BTree constructor overwrites the enableCache argument with false (visible in the IL), so CreateOrOpen(..., enableCache: true), as used in the GitHub demo and the PDF, is silently ignored. A public SetUseCache(bool) method with no license check exists, but its behaviour in the free build is not documented.
- The docs contradict each other and the binary. The GitHub README shows a new BTree(path, keyLength, ...) constructor in namespace BTreePlus that the DLL does not use (it is mmh.BTree with static factories), and it credits the Community Edition with the cache-on 3M-inserts-in-0.95 s result. The NuGet README lists Erase as free, while NOTICE.md and the PDF call it Enterprise-only. The DLL publicly exposes Erase, BulkLoad, FindRangeValues, PageCache and ShardManager anyway.
- Plan capacity up front. max_recs sizes the page allocation table (PAT), and the DLL has 'PAT is full (fixed size)' and 'PAT exhausted after second grow' errors. In-memory trees are capped by the MemoryStream size limit. Count is an int that is recomputed across all leaf pages on each call.
- Ordering is raw byte order. Integers must be written big-endian and right-aligned, and strings zero-padded, or range order is wrong. The format spec says over-long keys are truncated to keylen, so distinct long keys can collide.

## Known shortcomings

- Binary-only NuGet (engine source not published); the fast numbers come from the closed paid Pro build, and the README's Community 3.26x conflicts with the vendor PDF.
- The engine is a binary-only NuGet DLL (MIT covers the free binary and docs only) and the 4.4x/7x claims are for the paid Pro build. In 1.3.1 the constructor forces enableCache=false, so the demo/PDF's enableCache:true is silently ignored. No WAL/journal, yet the PostgreSQL bench is labelled 'WAL enabled for both'; no CPU/pragmas/harness for the SQLite table. One Monitor lock per tree serializes readers and writers; fixed-capacity errors; the release DLL ships a test/fuzz class and a hard-coded /home/mmh log path; 9 stars.

## Caveats and trade-offs

The engine is binary-only. NOTICE.md says 'Engine source code is not included in this repository'; the GitHub repo holds only docs, a demo Program.cs and a csproj that references the NuGet package. The headline SQLite and PostgreSQL numbers use the closed, paid Pro Edition (page cache plus Bulk Insert, both of which Community lacks). The Community Edition runs with the cache off, which the vendor PDF puts at \~418K inserts/s vs \~3.16M with the cache on. The GitHub README credits the Community Edition with '3M inserts 0.95 s vs SQLite (WAL) 3.10 s (\~3.26x)', which conflicts with those PDF figures. The SQLite table gives no CPU, SQLite pragmas or transaction batching; the PostgreSQL table gives i9-13900 + Samsung 990 PRO. The \~16% vs PostgreSQL is a time reduction (6m08s vs 5m10s, \~1.19x throughput). Only 9 GitHub stars (NuGet: \~11.8K downloads).

The 4.4x/7x-faster numbers are for the closed-source commercial 'Pro Edition' (adds page caching, sharding, range scans); the MIT-licensed 'Community Edition' on GitHub explicitly disables the page cache and is documented as 'not optimized for speed' -- so the actual open-source code does not deliver the claimed speedup.

## Maintenance

Maintained: NuGet 1.3.1 shipped in December 2025 and the GitHub docs were updated 2026-01-23 by a single vendor (MMH Systems), but usability is mixed: the free MIT package is binary-only with its page cache forced off, and the advertised speed needs a closed commercial license.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The NuGet README ('Fast Benchmark (2025)') gives first-party SQLite-vs-BTreePlus Pro timings (4M: 4.53 s vs 1.03 s; 1B: 2410 s vs 346 s) and the PostgreSQL WAL comparison. It gives no benchmark code, no SQLite configuration and no CPU for the SQLite table. The GitHub repo and the documentation PDF contain no SQLite benchmark harness either, so C stands.
- **Verifier notes:** The numbers match the NuGet page exactly, and the record correctly notes that the SQLite comparison gives no CPU. The main fix is has_code=false: no engine source exists publicly, only an MIT-licensed binary. Metadata verified: repo license MIT, 9 stars, last commit 2026-01-23, not a fork, not archived.
- **Fields the verifier corrected:** `has_code`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://www.nuget.org/packages/BTreePlus>
  - <https://github.com/koyllis/BTreePlus>
  - <https://github.com/koyllis/BTreePlus/blob/main/README.md>
  - <https://github.com/koyllis/BTreePlus/blob/main/NOTICE.md>
  - <https://github.com/koyllis/BTreePlus/blob/main/COMMERCIAL.md>
  - <https://github.com/koyllis/BTreePlus/blob/main/LICENSE>
  - <https://github.com/koyllis/BTreePlus/blob/main/BTreePlus.Demo.csproj>
  - <https://github.com/koyllis/BTreePlus/blob/main/Program.cs>
  - <https://mmhsys.com/BTreePlus.pdf>
- **Sources the enricher read:**
  - <https://github.com/koyllis/BTreePlus>
  - <https://github.com/koyllis/BTreePlus/blob/main/README.md>
  - <https://github.com/koyllis/BTreePlus/blob/main/API.md>
  - <https://github.com/koyllis/BTreePlus/blob/main/FILE_FORMAT.md>
  - <https://github.com/koyllis/BTreePlus/blob/main/NOTICE.md>
  - <https://github.com/koyllis/BTreePlus/blob/main/COMMERCIAL.md>
  - <https://github.com/koyllis/BTreePlus/blob/main/Program.cs>
  - <https://github.com/koyllis/BTreePlus/blob/main/BTreePlus.Demo.csproj>
  - <https://raw.githubusercontent.com/koyllis/BTreePlus/main/bench.png>
  - <https://github.com/koyllis/BTreePlus/issues>
  - <https://github.com/koyllis/BTreePlus/commits/main>
  - <https://www.nuget.org/packages/BTreePlus>
  - <https://api.nuget.org/v3/registration5-gz-semver2/btreeplus/index.json>
  - <https://api.nuget.org/v3-flatcontainer/btreeplus/1.3.1/btreeplus.1.3.1.nupkg>
  - <https://mmhsys.com/BTreePlus.pdf>
  - <https://hn.algolia.com/api/v1/search?query=BTreePlus>
  - <https://news.ycombinator.com/item?id=46045384>
  - <https://github.com/koculu/ZoneTree>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/koyllis/btreeplus`) · [data/wave6/enrich/raw/github_com_koyllis_btreeplus.json](../../../data/wave6/enrich/raw/github_com_koyllis_btreeplus.json) (enrichment confidence 0.75)

</details>
