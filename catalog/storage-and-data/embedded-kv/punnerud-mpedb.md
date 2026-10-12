# mpedb

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `Rust` · `LicenseRef-mpedb-1.0 (custom source-available license: free except a one-time USD 0.07/device fee for organizations over \$5B revenue/valuation)` · 🟢 active

> Rust embedded SQL database (mmap'd copy-on-write B+tree, MVCC, sqlite3 C-API shim) that beats SQLite on in-process point operations.

| | |
|---|---|
| **Beats** | SQLite |
| **Claimed result** | Apple M3 Pro page: point-select (tmpfs, none-class) mpedb 1,975,698 vs SQLite 320,201 ops/s (\~6.2x, derived from page data). Point-select (disk, commit-class, mpedb durability=wal vs SQLite sync=FULL+WAL) 1,942,515 vs 762,437 (\~2.5x, derived from page data). Point-insert (tmpfs, none-class) 230,660 vs 115,491 ops/s (\~2.0x, derived from page data). Contended-writes (4 threads, tmpfs, none-class) 147,059 vs 102,066 (\~1.4x, derived from page data). Separate Linux run (RESULTS-linux-amd-epyc-milan-2c.md, AMD EPYC-Milan 2 cores, tmpfs none-class): point-select 490,310 vs SQLite 79,619 ops/s (\~6.2x, derived from page data). Durable single-client writes are roughly a tie on the M3. |
| **Workload** | 50,000-row seeded table per cell. Cells: point-insert, point-select, point-update, 4-thread contended-writes and 3-reader+1-writer read-while-write. Each runs in a none-class mode (tmpfs, no fsync) and a commit-class mode (real disk, durable-on-ack; mpedb commit and wal vs SQLite sync=FULL+WAL), plus a durability-class table for single-client durable inserts. The same harness was re-run separately on a 2-core AMD EPYC-Milan Linux VM (tmpfs=/dev/shm, disk=xfs), published as RESULTS-linux-amd-epyc-milan-2c.md. |
| **Metric** | throughput |
| **Hardware** | Apple M3 Pro, 11 cores, 36 GiB RAM, macOS 26.6 (Darwin 25.6.0); also measured on AMD EPYC-Milan, 2 cores, Linux 6.8 |
| **Compiler and flags** | rustc 1.96.0 (ac68faa20 2026-05-25) on macOS and rustc 1.96.1 on the Linux run; --release with workspace [profile.release] lto=thin, codegen-units=1. SQLite is the rusqlite 0.31 bundled 3.45.0 build, compiled by the same toolchain. |
| **Adoption** | 11 stars |
| **Last commit** | 2026-08-28 |
| **Links** | [repository](https://github.com/punnerud/mpedb) · [benchmark](https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/RESULTS-macos-apple-m3-pro-11c.md) |

## Verdict

The author's mpedb-bench harness ran once on 2026-07-23 on an Apple M3 Pro (11 cores, macOS 26.6), built with rustc 1.96.0 --release, thin LTO and codegen-units=1. It measured mpedb 0.1.0 against bundled SQLite 3.45.0 through rusqlite 0.31 (STRICT table, prepare_cached) on a 50,000-row table. Warm PK point-select ran at 1.98M vs 320k ops/s non-durable (tmpfs; SQLite journal=MEMORY, sync=OFF) and 1.94M vs 762k durable (mpedb wal vs SQLite WAL, sync=FULL plus fullfsync), and point-insert at 231k vs 115k, with SQLite ahead on durable update, single-client durable insert and the deferred-fsync class. A same-day 2-core AMD EPYC-Milan Linux run shows point-select at 490k vs 80k.

## Use it when

- Several processes on one host (workers, CLI tools, notebooks) writing one local database file, where SQLite gives you SQLITE_BUSY and retry loops. The README's fork test (none-class, median of 3) shows 250-302k writes/s for mpedb vs 79-90k for SQLite WAL with a 60 s busy_timeout.
- Read-heavy primary-key lookups through prepared plans on a table that fits in the mapped file. M3: 1.98M vs 320k ops/s in the non-durable config and 1.94M vs 762k in the durable WAL config.
- Readers that must keep going while a writer is active. M3 commit-class: 2.41M vs 1.32M reads/s against SQLite WAL, with durable write rates about equal (345 vs 338/s).
- Batched durable writes with durability=wal: 29.7k vs 27.4k rows/s at 100 rows/commit on the M3, and the README reports a larger lead on Linux.
- Development and test: running an existing Django or CPython sqlite3 suite through the shim as a stricter 'second opinion' before deploying to PostgreSQL. This is the use the author recommends, rather than replacing SQLite.

## Skip it when

- Single-writer durable workloads. On the M3 it ties or loses: durable insert 328 vs 353 ops/s, update 300 vs 392, and deferred-fsync inserts (mpedb async vs SQLite synchronous=NORMAL) 19,720 vs 86,062, so SQLite is 4.4x faster there. The default-style durability=commit manages only 143 ops/s.
- Production or long-lived deployments. The author calls it a 'personal research project' and 'not production-hardened'. It has one author, 11 stars and no externally filed issues, and the author names the multi-process write path, where harnesses found a leak (#37), an atomicity hole (#119) and a shared-page corruption (#160), as the part to be sceptical about.
- Organizations that need OSI licensing or have more than \$5B revenue or valuation. The custom license charges USD 0.07 per device, counted per device connecting to servers backed by it, with a five-year tail. It claims to apply retroactively to every prior version and says ambiguities resolve in the licensor's favour.
- Full libsqlite3 fidelity. Only about 50 of roughly 300 C functions are exported. Commit, update and authorizer hooks and tracing are silent no-ops, custom VFS (such as encryption) and loadable extensions are refused, SQLITE_OPEN_READONLY is not enforced, and writes to ATTACHed databases are refused. The pip module passed only 2/89 of sqlitedict's tests and 67/87 of diskcache's at 0.1.3, and PY-COMPAT.md lists an overlay INSERT OR REPLACE duplicate (#133) as a wrong answer.
- Windows, NFS or containers. On Windows the contended-insert cell is about 4x worse relative to SQLite than on Linux, with the cause unknown. Network filesystems are unsupported. Attaching from a different PID namespace is refused, and the platform table says nothing has run on Linux aarch64.

## How it is fast

SQL is compiled once into a content-hashed plan, so the hot path is execute(hash, params) with no parsing or statement lookup. Rows live in an LMDB-style copy-on-write B+tree inside a MAP_SHARED mmap'd file, with double-buffered meta pages. A read is an in-process walk over mapped pages under an MVCC snapshot, pinned in a lock-free reader table of packed {pid, seq} slots, so readers never take the writer lock. Writers enqueue into a shared-memory intent ring; whoever holds the single writer lock drains it in key-locality order and commits the batch with one meta flip and one flush (group commit). durability=wal appends lean records (only touched COW pages, with node free space elided) using one pwrite plus one fdatasync. The repo's own bisect credits the 1.26M to 1.98M ops/s point-select jump on the M3 to one plan-cache and parameter-resolution commit (7fb0d53).

## Compared with alternatives

Among the SQLite-baseline siblings (CalicoDB, ForestDB, ZoneTree, BTreePlus, DBX, CacheAdvance), pick mpedb when you want to keep SQL and existing libsqlite3/Python sqlite3 code while gaining multi-process writers and faster point reads. The others expose key-value or custom APIs, so adopting them means rewriting the data layer. Prefer them when a plain KV API is enough and you need a conventional license or a longer track record.

## Integration

| | |
|---|---|
| **Form** | crate (Cargo workspace used as a git dependency; not published on crates.io), plus a PyPI wheel (mpedb 0.3.1), a cdylib sqlite3 shim and a CLI |
| **Dependencies** | Engine: libc, xxhash-rust, blake3, toml, plus in-repo crates. Optional rusqlite 0.31 (bundled) behind the sqlite-checkpoint feature. The C-API shim adds cc to build a printf.c. The Python module uses PyO3 (abi3-py310). |
| **Minimum toolchain** | Rust edition 2021 with no rust-version declared (benchmarks built with rustc 1.96); CPython 3.10+ for the wheel |
| **Platforms** | Linux x86-64 (reference platform) and armv7 (tested on a Raspberry Pi 3); macOS Apple Silicon; Windows x86-64 (runs, markedly slower); wasm32 in-browser, single-process only. The platform table lists Linux aarch64 as 'nothing yet'. Local filesystems only, single PID namespace. |
| **Thread safety** | One Database handle is shared across threads via Arc (the benchmark does this), and many processes can attach one file. Readers are lock-free MVCC snapshots. All writers in a file serialize on one writer lock, so write parallelism comes from separate files in a Workspace. The facade rule is to prepare plans before opening a write session. Through the C-API, busy_timeout is honoured, but a write with a deadline never joins group commit, which the docs measure as 2.3-2.5x slower with 4 contended durable writers. |
| **Drop-in for the baseline** | partial — the libsqlite3 ABI shim runs unchanged CPython sqlite3, Django and SQLAlchemy suites (via LD_PRELOAD; PHP needs soname substitution because LD_PRELOAD silently binds nothing there), and `import mpedb as sqlite3` works for common DB-API code. Rigid typing, integer-overflow errors, narrower ORDER BY, a fixed file size, no-op hooks and a subset of exported functions mean some code breaks loudly. The docs disagree on CPython test_sqlite3: the README says 466/466, C-API-COMPAT.md says 459 of 467. |

## Gotchas

- The file size is fixed at creation: it is fallocate'd from size_mb, the shim defaults are 64 MiB file-backed and 16 MiB in-memory, and it never grows. Exceeding it gives DbFull or SQLITE_FULL. A reader that is alive but stalled (SIGSTOP, debugger, a long scan) pins its snapshot and can eventually stall every writer with DbFull, because snapshot eviction is only half built.
- Pick durability deliberately. `commit` (msync data, then meta) costs two device flushes, and on macOS each is a full F_FULLFSYNC, so it runs at about half the speed of `wal`. The benchmark page calls `wal` the like-for-like comparand. The data file and its -wal sidecar must be copied together for snapshots.
- The benchmark arms are not symmetric. mpedb shares one handle across threads and uses execute(hash); the batched-insert cell uses the typed insert_row, bypassing SQL, while SQLite gets one connection per thread and prepared SQL. WAL auto-checkpoint is deferred out of the timed cells for both engines. SQLite's none-class mode is journal_mode=MEMORY with synchronous=OFF, a rollback-journal setup in which SQLite's own point-select is 2.4x slower than in its WAL setup. That inflates the 6.2x headline and produces the pathological 180 reads/s read-while-write cell, which the author labels as such.
- The README's prebuilt-shim install line points at releases/latest, but v0.3.0 and v0.3.1 have no assets attached and the filename says 0.2.1. v0.2.9 has no macOS build either, so on current releases you build the shim with cargo.

## Known shortcomings

- The 'volume-backed' 490,310 vs 79,619 figure is a separate Linux EPYC run; SQLite wins some durable-mode cells; custom non-OSI license.
- LICENSE: custom non-OSI terms charging \$0.07 per device (counting server-connected devices, claimed retroactively), so not freely usable. The 6.2x headline is inflated (SQLite's 'none' class ran journal MEMORY + sync OFF, 2.4x slower than its own WAL; uneven arms); durable single-writer ties or loses on M3 and SQLite is 4.4x ahead in the deferred-fsync class; the bench is v0.1.0 while releases are at v0.3.1. File size is fixed at create (DbFull); a stalled reader can wedge writers; the SQLite shim covers \~50 of 300 functions with no-op hooks and unenforced READONLY; v0.3.x releases ship no assets; a single-author 'research project'.

## Caveats and trade-offs

The license is NOT OSI-approved. It is the custom 'mpedb License 1.0': free for everyone except a one-time USD 0.07/device fee for groups with more than \$5B revenue or valuation. The code can be used and studied, but it is not plain permissive open source. The benchmark was run on mpedb 0.1.0 and releases are now at 0.2.1. It is a single run on one machine with no confidence intervals, and the author says to treat differences under 20% as noise. mpedb does not win every cell. On the M3, SQLite is faster at durable point-update (392 vs 300 ops/s for mpedb wal), at single-client durable insert (353 vs 328), and at 4.4x in the crash-consistent-deferred class (86,062 vs 19,720 ops/s). The SQLite none-class baseline is journal_mode=MEMORY + synchronous=OFF. The author is careful about methodology: durability classes are kept separate, F_FULLFSYNC is forced on macOS, and the page states that every cell is reported, including the ones mpedb loses.

Claims class-for-class parity in durability guarantees (WAL vs WAL, none vs none) with an unusually thorough honesty/controls methodology; embedded/single-process like SQLite (fair architectural comparison, unlike the PostgreSQL rows in the same doc); ABI-compatible libsqlite3 shim for drop-in use.

## Maintenance

Actively developed by a single author: the repo was created 2026-07-13, the last commit was 2026-08-28, and the latest release is v0.3.1 (2026-08-22, also on PyPI), not the 0.2.1 in the record. The benchmark measured 0.1.0 and has not been re-run on 0.3.x. The author describes it as a research project rather than production software, and it ships under a custom non-OSI source-available license.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** RESULTS-macos-apple-m3-pro-11c.md is a head-to-head against SQLite 3.45.0 (bundled via rusqlite), PostgreSQL 16.14 and Turso 0.7.0, produced by the public harness crates/mpedb-bench/src (h2h.rs, eng_sqlite.rs, workloads.rs; `cargo run --release -p mpedb-bench`). The page states the compiler (rustc 1.96.0), the flags (--release, lto=thin; the workspace [profile.release] also sets codegen-units=1) and the CPU (Apple M3 Pro, 11 cores), so all A criteria are met.
- **Verifier notes:** The record's 'volume-backed re-run' numbers (490,310 vs 79,619) do not come from the M3 page. They are the tmpfs point-select cell of the separate Linux EPYC-Milan 2-core results file, so the label is fixed. All other M3 numbers match exactly. The commits API gives 2026-08-28 as the last commit on main (pushed_at is 2026-09-01). Metadata checks out: 11 stars, not a fork, not archived, spdx NOASSERTION with the custom license confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/punnerud/mpedb>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/RESULTS-macos-apple-m3-pro-11c.md>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/RESULTS-linux-amd-epyc-milan-2c.md>
  - <https://github.com/punnerud/mpedb/blob/main/LICENSE>
  - <https://github.com/punnerud/mpedb/blob/main/README.md>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/Cargo.toml>
  - <https://github.com/punnerud/mpedb/blob/main/Cargo.toml>
  - <https://github.com/punnerud/mpedb/blob/main/.cargo/config.toml>
- **Sources the enricher read:**
  - <https://github.com/punnerud/mpedb>
  - <https://github.com/punnerud/mpedb/blob/main/README.md>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/RESULTS-macos-apple-m3-pro-11c.md>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/RESULTS-linux-amd-epyc-milan-2c.md>
  - <https://github.com/punnerud/mpedb/blob/main/benchmarks/head-to-head.md>
  - <https://github.com/punnerud/mpedb/blob/main/benchmarks/README.md>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/src/eng_sqlite.rs>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/src/eng_mpedb.rs>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/src/workloads.rs>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-bench/Cargo.toml>
  - <https://github.com/punnerud/mpedb/blob/main/Cargo.toml>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-core/Cargo.toml>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb/Cargo.toml>
  - <https://github.com/punnerud/mpedb/blob/main/crates/mpedb-capi/Cargo.toml>
  - <https://github.com/punnerud/mpedb/blob/main/LICENSE>
  - <https://github.com/punnerud/mpedb/blob/main/design/DESIGN.md>
  - <https://github.com/punnerud/mpedb/blob/main/INNOVATIONS.md>
  - <https://github.com/punnerud/mpedb/blob/main/GUIDE.md>
  - <https://github.com/punnerud/mpedb/blob/main/C-API-COMPAT.md>
  - <https://github.com/punnerud/mpedb/blob/main/PY-COMPAT.md>
  - <https://github.com/punnerud/mpedb/releases>
  - <https://github.com/punnerud/mpedb/commits/main>
  - <https://github.com/punnerud/mpedb/issues>
  - <https://github.com/punnerud/mpedb/pulls>
  - <https://pypi.org/pypi/mpedb/json>
  - <https://crates.io/api/v1/crates/mpedb>
  - <https://hn.algolia.com/api/v1/search?query=mpedb>
  - <https://hn.algolia.com/api/v1/search?query=mpedb&tags=comment>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/punnerud/mpedb`) · [data/wave6/enrich/raw/github_com_punnerud_mpedb.json](../../../data/wave6/enrich/raw/github_com_punnerud_mpedb.json) (enrichment confidence 0.8)

</details>
