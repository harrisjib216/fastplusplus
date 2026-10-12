# CacheAdvance

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Swift` · `Apache-2.0` · 🟢 active

> Size-capped append-only Swift log file (optional ring-buffer eviction); appends far faster than per-row-committed SQLite inserts.

| | |
|---|---|
| **Beats** | SQLite |
| **Claimed result** | "CacheAdvance persists log events 30x faster than SQLite" (README headline claim). |
| **Workload** | Appending log messages (a Lorum Ipsum message set) to an on-disk cache file, single-message and batch append, measured with XCTest `measure {}` performance tests against an equivalent SQLite-backed cache. |
| **Metric** | throughput |
| **Adoption** | 51 stars |
| **Last commit** | 2026-06-23 |
| **Links** | [repository](https://github.com/dfed/CacheAdvance) · [benchmark](https://github.com/dfed/CacheAdvance/blob/main/Tests/CacheAdvanceTests/SQLitePerformanceComparisonTests.swift) |

## Verdict

The '30x faster than SQLite' tagline is a first-party README claim from April 2020 with no published numbers, hardware or Xcode/Swift version. The PR that added the benchmarks (#41) said 'more than 15x' as a lower bound and mentioned runs above 50x; two days later the README was changed to 30x. The benchmarks are XCTest measure{} tests appending about 480 JSON-encoded Lorem-ipsum strings. The SQLite side runs COUNT(\*), prepares a fresh INSERT and autocommits every row under default rollback-journal synchronous=FULL (per sqlite.org, a few dozen transactions per second versus 50,000+ plain INSERTs), while CacheAdvance never fsyncs. It therefore compares durable per-row transactions with page-cache writes, and a batched or WAL-mode SQLite baseline was never tested.

## Use it when

- Swift apps on iOS 15+/macOS 11+/tvOS/watchOS/visionOS (or Linux with Swift 6) that need a crash-surviving on-disk buffer of recent log or analytics events before upload
- Write-heavy, read-rarely workloads: many small appends (tests use about 480 strings of roughly 50 bytes), then one bulk messages() read at upload or crash-report time
- When you want a hard on-disk size cap with automatic eviction of the oldest entries (shouldOverwriteOldMessages: true) and no compaction or vacuum
- When pulling in SQLite/Core Data just for a log table is overkill and a single dependency-free Swift source package is preferred

## Skip it when

- You need power-loss durability: appends are plain write() calls with no fsync, and the README only promises that data is 'persisted to disk' when append returns (i.e. handed to the OS)
- You need keyed lookup, filtering, deleting specific entries, a message count or partial reads: messages() decodes the whole cache into memory, and there is no count API (proposed in issue #34, absent from the current source)
- Read-heavy use: the author's own PR #41 reports that SQLite is 'significantly faster at reading messages'; reads cost two small read calls plus a JSON decode per message
- Multi-threaded or multi-process writers: instances are not thread-safe, the class is not Sendable under Swift 6, and there is no file locking
- Large messages or caches whose size or overwrite policy may change later: messages must stay under 2 GB, and changing maximumBytes or the overwrite flag after first use makes the file unwritable (fileNotWritable)

## How it is fast

Each append JSON-encodes the message (encoder is pluggable), prefixes it with a big-endian UInt32 length and writes it at the current FileHandle offset. It then rewrites one 8-byte offset field in a fixed 64-byte file header; an overwriting cache also updates the oldest-message pointer and advances a read cursor. That is a few write/seek syscalls per message. There is no SQL parsing, B-tree, journal, transaction or fsync (the source never calls synchronize/fsync). The SQLite path it is compared against pays a full autocommit transaction per insert.

## Compared with alternatives

Every sibling here is a keyed store with point lookups (for example CalicoDB, also benchmarked against SQLite, NuDB or the RocksDB-derived engines) and mostly C/C++/Go. Pick CacheAdvance only when you are in Swift and need a bounded, append-then-dump log file rather than a key-value store; for any keyed or read-heavy workload a sibling (or SQLite itself) is the right tool.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Foundation only); SQLite3 is imported only by the test target |
| **Minimum toolchain** | Swift 6.0 tools / Swift 6 language mode (Xcode 16+); Objective-C support removed in 4.0.0 |
| **Platforms** | iOS 15, tvOS 15, watchOS 7, macOS 11, Mac Catalyst 15, visionOS 1 (podspec); Linux x86-64 tested in CI with Swift 6.0.3 and 6.1; other OSes not documented |
| **Thread safety** | Not thread-safe: use one instance from a single serial queue (README). Calls do synchronous disk I/O, so keep them off the main queue. No cross-process locking. |
| **Drop-in for the baseline** | partial — it replaces the pattern of a bounded SQLite log table (append plus read-all) behind a different, SQL-free Swift API; it does not replace SQLite for anything that needs queries, keys, transactions or durability guarantees |

## Gotchas

- The file must already exist (for example via FileManager.createFile) before init; the handles open with forUpdating/forWritingTo and fail otherwise. The README's sample uses a 'file:' argument label, but the real initializer takes 'fileURL:'.
- maximumBytes and the overwrite flag are stored in the header and must never change: a mismatch leaves the file readable but append throws fileNotWritable. The encoder/decoder are not recorded, so changing them silently breaks decoding of old messages.
- Crash windows are documented in the source: a crash between the data write and the header update loses the newest message, and a crash mid-write can yield CacheAdvanceError.fileCorrupted, after which the README says to delete the file.
- The per-append cost is dominated by JSONEncoder (the author in PR #41 put encoding at about 15x the header cost); supply a cheaper MessageEncoder if throughput matters.

## Known shortcomings

- The 30x appears only in the README (earlier 15x) and the test file has no numbers. The SQLite baseline is naive (COUNT(\*) and a separate commit per append at default durability) while CacheAdvance does not fsync.
- The 30x is a README tagline with no published data or hardware (PR #41 said '&gt;15x'). The SQLite baseline uses COUNT(\*), a fresh prepare and an autocommit per row at synchronous=FULL, while CacheAdvance never fsyncs; the author concedes SQLite is much faster at reads. messages() loads the whole cache; no keys/count/delete.
- Not a key-value store but an append-only ring-buffer log (embedded-kv is a loose fit). Not thread-safe or Sendable, no process lock; the file must pre-exist; the README's init label is wrong (file: vs fileURL:). Swift 6 / Xcode 16+.

## Caveats and trade-offs

The 30x figure is a first-party README claim from April 2020 (commit 6ae0a74 changed an earlier '15x faster while utilizing 40% less memory than SQLite'). The benchmark_url test file measures but prints no stored results and gives no hardware or Xcode/Swift version, and performance tests are disabled on GitHub Actions. The SQLite baseline is naive: every append runs a SELECT COUNT(\*), prepares a fresh INSERT and commits it on its own under SQLite's default durability, with no batching, prepared-statement reuse or WAL. CacheAdvance's append path shows no fsync, so the comparison favors it.

No in-memory buffer, every append is a synchronous disk write; not thread-safe (single serial queue only); the SQLite comparison test is disabled on Linux (Apple platforms only).

## Maintenance

Active single-maintainer project (v4.0.0 June 2025, last push June 2026, 0 open issues, CI on Apple platforms and Linux); Apache-2.0 and 14 small Swift source files, so easy to vendor, though usage is modest (51 stars).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The '30x faster than SQLite' figure appears only in the README tagline, with no methodology or results. The public XCTest comparison (Tests/CacheAdvanceTests/SQLitePerformanceComparisonTests.swift) has no recorded numbers, compiler or hardware. That is first-party and short of A, so C.
- **Verifier notes:** The benchmark_url shows the SQLite comparison code but not the 30x number, which is only in the README tagline. The category 'embedded-kv' fits loosely: this is an append-only log/message cache. Metadata checks out: Apache-2.0, 51 stars, last commit 2026-06-23, active.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dfed/CacheAdvance/main/Tests/CacheAdvanceTests/SQLitePerformanceComparisonTests.swift>
  - <https://raw.githubusercontent.com/dfed/CacheAdvance/main/Tests/CacheAdvanceTests/PerformanceTestsEnabled.swift>
  - <https://raw.githubusercontent.com/dfed/CacheAdvance/main/README.md>
  - <https://raw.githubusercontent.com/dfed/CacheAdvance/main/Sources/CacheAdvance/CacheAdvance.swift>
  - <https://raw.githubusercontent.com/dfed/CacheAdvance/main/Sources/CacheAdvance/CacheHeaderHandle.swift>
  - <https://github.com/dfed/CacheAdvance>
  - <https://github.com/dfed/CacheAdvance/commit/6ae0a74291e63b77c760c649c1da92878fe77f2b>
  - <https://github.com/dfed/CacheAdvance/commit/42e5ada4f8256fb004d3f63c5e43d806b6be8011>
- **Sources the enricher read:**
  - <https://github.com/dfed/CacheAdvance>
  - <https://github.com/dfed/CacheAdvance/blob/main/README.md>
  - <https://github.com/dfed/CacheAdvance/blob/main/Package.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/CacheAdvance.podspec>
  - <https://github.com/dfed/CacheAdvance/blob/main/.github/workflows/ci.yml>
  - <https://github.com/dfed/CacheAdvance/blob/main/Sources/CacheAdvance/CacheAdvance.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Sources/CacheAdvance/CacheHeaderHandle.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Sources/CacheAdvance/CacheReader.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Sources/CacheAdvance/FileHandleExtensions.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Sources/CacheAdvance/FileHeader.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Sources/CacheAdvance/EncodableMessage.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Sources/CacheAdvance/MessageSpan.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Sources/CacheAdvance/CacheAdvanceError.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Tests/CacheAdvanceTests/SQLitePerformanceComparisonTests.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Tests/CacheAdvanceTests/FlushableCachePerformanceComparisonTests.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Tests/CacheAdvanceTests/PerformanceTestsEnabled.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Tests/CacheAdvanceTests/CacheAdvanceTests.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Tests/CacheAdvanceTests/LorumIpsumMessages.swift>
  - <https://github.com/dfed/CacheAdvance/blob/main/Tests/CacheAdvanceTests/TestableMessage.swift>
  - <https://github.com/dfed/CacheAdvance/pull/41>
  - <https://github.com/dfed/CacheAdvance/pull/98>
  - <https://github.com/dfed/CacheAdvance/issues/57>
  - <https://github.com/dfed/CacheAdvance/issues/34>
  - <https://github.com/dfed/CacheAdvance/releases/tag/4.0.0>
  - <https://github.com/dfed/CacheAdvance/releases/tag/3.0.0>
  - <https://github.com/dfed/CacheAdvance/commit/6ae0a74291e63b77c760c649c1da92878fe77f2b>
  - <https://github.com/dfed/CacheAdvance/commit/42e5ada4f8256fb004d3f63c5e43d806b6be8011>
  - <https://www.sqlite.org/pragma.html#pragma_synchronous>
  - <https://www.sqlite.org/faq.html>
  - <https://hn.algolia.com/api/v1/search?query=CacheAdvance>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/dfed/cacheadvance`) · [data/wave6/enrich/raw/github_com_dfed_cacheadvance.json](../../../data/wave6/enrich/raw/github_com_dfed_cacheadvance.json) (enrichment confidence 0.75)

</details>
