# gdu

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Parallel Go disk usage analyzer (TUI, CLI and web UI); scans about 6.5x faster than GNU du on a cold SSD.

| | |
|---|---|
| **Beats** | GNU du -hs and ncdu |
| **Claimed result** | Cold cache gdu -npc 4.716s vs du -hs 30.608s (6.5x, derived from page data) and ncdu 33.163s; warm cache 466.1ms vs du 1255.2ms and ncdu 2222.4ms. diskus is faster in both (4.489s cold, 270.8ms warm), pdu faster on warm cache. |
| **Workload** | Scan a 90G directory (100k directories, 400k files) with hyperfine, cold cache (drop_caches) and warm cache (5 warmups); commands in Makefile benchmark target |
| **Metric** | latency |
| **Hardware** | 500 GB SSD; CPU model not stated (cpupower governor set to performance) |
| **Compiler and flags** | Go build via Makefile: -trimpath, -pgo=default.pgo, CGO_ENABLED=0 |
| **Adoption** | 6.1k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/dundee/gdu) · [benchmark](https://github.com/dundee/gdu) |

## Verdict

First-party hyperfine run on a 90 GB home directory (100k dirs, 400k files) on a 500 GB SSD, CPU model not stated, governor set to performance: cold cache gdu -npc 4.716 s vs du -hs 30.608 s (6.5x) and ncdu 33.163 s; warm cache 466.1 ms vs du 1255.2 ms (2.7x, derived from page data) and ncdu 2222.4 ms. Build flags are in the Makefile (-trimpath, -pgo=default.pgo, CGO_ENABLED=0), but the binary version used for the table is not stated.

## Use it when

- Interactive cleanup of a large tree on SSD/NVMe where ncdu takes tens of seconds: same browse-and-delete workflow, about 7x faster cold in the README run.
- Scripted totals where you want something faster than du -hs and can accept gdu's output format (`gdu -nps`).
- Saving a scan to JSON or SQLite/BadgerDB and browsing it later or on another machine.
- Machines where a single static binary with no runtime dependencies is preferred (Linux, macOS, Windows, BSD, Android arm64 builds are released).

## Skip it when

- Pure 'how big is this directory' speed: diskus is faster cold (4.489 s vs 4.716 s) and warm (270.8 ms vs 466.1 ms), and pdu is faster warm (299.1 ms) in gdu's own table.
- Rotating HDDs: README says the gain is small there; use --sequential.
- Database-backed modes when speed matters: --db=tmp.db took 44.989 s cold and 8.25 s warm, slower than du -hs (30.608 s / 1.255 s).
- When you need a C++ library to embed: it is a Go tool, and the pkg/analyze API is not documented as stable.
- Exact du compatibility (flags, output format, --apparent-size semantics): it is not a drop-in.

## How it is fast

Each directory is read with os.ReadDir and every subdirectory is handed to a new goroutine, gated by a global semaphore of 2 x GOMAXPROCS, so many getdents/lstat calls are in flight at once and SSD queue depth is used (pkg/analyze/parallel.go). Non-interactive runs without --top/--depth use a TopDirAnalyzer that keeps only top-level totals, so memory stays flat on large trees. Disk usage comes from stat.Blocks x 512, and hard links are deduplicated by inode in a sync.Map. Release builds use profile-guided optimization (-pgo=default.pgo) with CGO disabled.

## Compared with alternatives

Pick gdu over diskus or pdu when you want an interactive browser with deletion, JSON/DB export or a web UI rather than just the fastest total; for raw total-size speed diskus and pdu win in gdu's own benchmark, and zdu claims to beat pdu on some trees.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Go modules: tcell/tview (TUI), cobra, logrus, badger/v4, modernc SQLite (per sqlite_modernc.go), ulikunitz/xz and others in go.mod; prebuilt static binaries need nothing |
| **Minimum toolchain** | Go 1.26.0 (go.mod) |
| **Platforms** | Linux, macOS (amd64/arm64), Windows (amd64/arm64), FreeBSD/NetBSD/OpenBSD, Android arm64, 32-bit ARM |
| **Thread safety** | Internal scan is concurrent; the library API's thread-safety is not documented (issue #643 fixed a race in StoredDir.updateStats). |
| **Drop-in for the baseline** | partial — replaces ncdu's workflow and du -s totals at the shell, but flags and output differ from GNU du |

## Gotchas

- Concurrency is fixed at 2 x GOMAXPROCS; the README tables show GOMAXPROCS=80 widening cold-cache variance (3.627-9.993 s) rather than helping on average.
- Hard links are deduplicated by inode number only (stat.Ino when Nlink &gt; 1), not by (device, inode); not documented whether this can merge distinct files across filesystems when -x is not used.
- Default ignore list is /proc,/dev,/sys,/run; scanning / with -i overridden can walk pseudo-filesystems.
- Interactive and web modes can delete files; use --no-delete on shared machines, and the web UI has no authentication for browsing (bind to localhost).

## Caveats and trade-offs

Go, not C++ (a tool, not a library); CPU not stated; first-party table; gdu loses to diskus (cold and warm) and to pdu on warm cache; database-backed modes are slower than du.

Optimised for SSD; diskus is faster in the same table; Go binary.

## Maintenance

Actively maintained (last commit 2026-10-05, 6.1k stars), MIT-licensed, widely packaged; a tool rather than a library, so 'copyable' means the Go source and static binaries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README hyperfine tables compare gdu with du -hs and ncdu; benchmark commands are public in the Makefile 'benchmark' target, but hardware is only '500 GB SSD' with no CPU model and Go build flags unstated, so first-party C.
- **Verifier notes:** Numbers match README. MIT (LICENSE.md), 6.1k stars, not archived, not a fork. Last commit date not checked (record value left unchanged). Language Go is out of the C++-first scope; orchestrator may want to tag accordingly.
- **Fields the verifier corrected:** `hardware`, `workload`, `claimed_speedup`, `caveats`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://github.com/dundee/gdu>
  - <https://raw.githubusercontent.com/dundee/gdu/HEAD/README.md>
  - <https://raw.githubusercontent.com/dundee/gdu/HEAD/Makefile>
  - <https://raw.githubusercontent.com/dundee/gdu/HEAD/LICENSE.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dundee/gdu/HEAD/README.md>
  - <https://raw.githubusercontent.com/dundee/gdu/HEAD/Makefile>
  - <https://raw.githubusercontent.com/dundee/gdu/HEAD/go.mod>
  - <https://github.com/dundee/gdu/tree/master/pkg/analyze>
  - <https://raw.githubusercontent.com/dundee/gdu/HEAD/pkg/analyze/parallel.go>
  - <https://raw.githubusercontent.com/dundee/gdu/HEAD/pkg/analyze/parallel_top_dir.go>
  - <https://raw.githubusercontent.com/dundee/gdu/HEAD/pkg/analyze/dir_linux-openbsd.go>
  - <https://github.com/dundee/gdu/issues?q=is%3Aissue+performance+OR+slow+OR+memory>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/dundee/gdu`) · [data/wave11/enrich/raw/github_com_dundee_gdu.json](../../../data/wave11/enrich/raw/github_com_dundee_gdu.json) (enrichment confidence 0.8)

</details>
