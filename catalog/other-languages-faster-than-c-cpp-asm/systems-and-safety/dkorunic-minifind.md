# minifind (dkorunic, Rust parallel find(1) reimplementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Parallel work-stealing Rust find(1) subset that lists a warm Linux kernel tree about 3.5x faster than GNU find.

| | |
|---|---|
| **Beats** | GNU find (findutils, C) |
| **Claimed result** | README: minifind 26.634-26.779 ms (26.702 ms point) vs find 92.463-93.565 ms (93.0 ms), about 3.5x faster (3.8M vs 1.1M entries/s). |
| **Workload** | Walking a shallow clone of the mainline Linux kernel tree (100,871 entries in 6,201 directories, \~2.1 GB) with a warm page cache; both tools run as subprocesses with output discarded; 100 Criterion samples. |
| **Metric** | latency |
| **Hardware** | 4-core / 8-thread Intel Xeon E5-1630 v3 @ 3.70 GHz, 48 GB RAM |
| **Compiler and flags** | cargo bench --bench walk (Criterion 0.8, 80 s warm-up, 400 s measurement); the bench profile inherits Cargo.toml [profile.release] opt-level = 3, lto = "fat", codegen-units = 1; mimalloc allocator. rustc version not stated (rust-version floor 1.85.1); GNU find is whatever 'find' is on PATH, version and build flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: parallel work-stealing traversal (most of the gap on 8 threads), raw getdents64 via rustix, d_type instead of a per-entry stat, batched output thread with a 256 KB writer, mimalloc. |
| **Adoption** | 10 stars, 0 forks, 106 commits |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/dkorunic/minifind) · [benchmark](https://raw.githubusercontent.com/dkorunic/minifind/HEAD/README.md) |

## Verdict

Criterion (100 samples, 80 s warm-up, 400 s measurement) on a 4-core/8-thread Xeon E5-1630 v3, warm page cache, over a shallow Linux kernel clone (100,871 entries, 6,201 directories). minifind defaults (fat-LTO release profile, mimalloc, 7 walkers) took 26.70 ms against 93.00 ms for the GNU find on PATH (version unstated), about 3.5x. Both runs included process startup and piped stdout into the harness; the harness checked neither output nor exit status.

## Use it when

- Listing or name/type-filtering large local trees (source checkouts, build outputs, home directories) on a multi-core machine with a warm page cache, where a single-threaded find is the bottleneck
- Scripts that need find-style metadata filters (-mtime, -size, -perm, -user, -newer) plus -print0 for xargs -0, without fd's gitignore and hidden-file rules
- Background scans on busy Linux hosts: --idle puts workers in SCHED_IDLE and IOPRIO_CLASS_IDLE at nice +19 with 2 threads
- I/O-throttled environments: -s/--max-scan-rate caps directories scanned per second

## Skip it when

- When you need find's actions or grammar (-exec, -delete, -printf, -o, -not, parentheses), file operands instead of directories, or find's deterministic depth-first output order; parallel workers emit in arbitrary order, so -quit/--max-results return an arbitrary match
- When errors must be visible: by code reading, a directory that fails to open or read (EACCES, a getdents error) is skipped silently and the exit status stays 0. GNU find prints a diagnostic and exits 1
- 1-2 core hosts or cold caches: the README says the gap shrinks toward parity there, and no single-thread or cold-cache numbers are published. --threads accepts 2 to 65535, and AGENTS.md says more than 21 threads gives no gain
- When total CPU time matters more than wall time: idle walkers poll with crossbeam Backoff::snooze (spin, then yield) instead of parking, and the benchmark reports wall time only
- Windows: the std::fs fallback has no --one-filesystem (dev = 0) and reports device, pipe and socket entries as File

## How it is fast

Most of the gap is parallelism: threads-1 walker threads (7 on the 8-thread test box) pull directory tasks from crossbeam-deque LIFO work-stealing queues. Each directory is read with raw getdents64 through rustix, and children are opened with openat relative to a shared parent fd. File type comes from d_type, so the default listing never stats an entry; metadata predicates statx lazily, after the name and type filters. Matches go to a dedicated output thread in 256-entry batches and through a 256 KB BufWriter; mimalloc is the global allocator.

## Compared with alternatives

Pick minifind over fd when you want find-style metadata predicates and no ignore-file filtering in a parallel walker. fd's catalogued win is over find -iregex/-iname matching, while minifind's is a plain listing, and no head-to-head between the two is published. Pick cligen/dents for a single-threaded Nim library hook, and dumac when you need du totals rather than paths.

## Integration

| | |
|---|---|
| **Form** | CLI binary (cargo-dist installers, Homebrew tap); also a library crate exposing minifind::run() |
| **Dependencies** | mimalloc, crossbeam-channel/deque/utils, rustix, libc, globset, regex, governor, lexopt, signal-hook, normpath, itertools, anyhow |
| **Minimum toolchain** | Rust 1.85.1 (edition 2021); no pinned toolchain |
| **Platforms** | Linux (getdents64 via rustix, statx, --idle), other Unix via rustix (stat instead of statx); Windows through a std::fs fallback. Release targets: x86_64 and aarch64 Linux (gnu, plus x86_64 musl), x86_64 and aarch64 macOS, x86_64 Windows |
| **Thread safety** | CLI: n/a. Library run() spawns its own walker and output threads, installs process-wide signal handlers, and main() raises RLIMIT_NOFILE to the hard limit, so treat run() as one call per process |
| **Drop-in for the baseline** | partial: plain 'find DIR' and many single-dash spellings (-name, -type, -size, -newer, -print0, -xdev) work, but there are no actions or boolean operators. -o means --one-filesystem, not OR. Defaults differ (d/f/l only, no mount crossing), output order is nondeterministic, and unreadable directories are skipped silently with exit 0 |

## Gotchas

- Harness flaw: benches/walk.rs runs each tool through Command::output() and discards the result. It checks neither the exit status nor that the two outputs match, so a failing or truncated run would still be timed. Only wall time is measured: 7 walker threads plus an output thread against single-threaded GNU find, with no CPU-time or per-thread figure.
- By code reading: walk.rs returns early when open_child/open_root fails, and the for_each_entry result is discarded (let _ =). Unreadable or vanished directories therefore disappear from the output with no message, and the documented exit status stays 0. Output write errors are also ignored (unwrap_or(())).
- The README numbers come from the 2026-06-19 'full-clock rerun' on the newly added fd-anchored walker. Later releases 0.9.0-0.10.2 added predicates, --idle and the man page without re-benchmarking. The GNU find version and build, and the rustc version, are not stated.
- AGENTS.md still says ignore::WalkBuilder applies .gitignore filters by default. CLAUDE.md and Cargo.toml show ignore is now only a dev-dependency since the custom walker replaced it in 0.8.0, so trust the code over AGENTS.md.

## Known shortcomings

- Win mostly from an 8-thread parallel walk against single-threaded GNU find (26.702 vs 92.998 ms, 3.5x, Xeon E5-1630 v3); find version, flags and rustc unstated; no output-equality check.
- benches/walk.rs ignores exit status and never compares outputs; wall time only, 7 walkers against single-threaded find. The code drops unreadable directories silently with exit 0, ignores write errors, and idle workers spin instead of parking. Numbers come from the 2026-06-19 walker and were not re-run for 0.9.0-0.10.2.

## Caveats and trade-offs

Win is mostly parallelism: minifind uses all 8 hardware threads (one reserved for output) while GNU find is single-threaded, and the README itself says the gap 'shrinks toward parity on a 1-2 core host'. Process startup is included for both; both tools' stdout is captured into a pipe by Command::output() and dropped. The benchmark does not check that the two outputs match; minifind defaults to one filesystem and types d/f/l, plain 'find' lists every type and crosses mounts (equivalent on a kernel clone). GNU find version and build flags (distribution packages are usually -O2) and rustc version are unstated. Numbers come from the 2026-06-19 'full-clock rerun' commit, made the same day the 'fd-anchored parallel walker' landed; warm page cache only, the README says the gap narrows on a cold cache. Single machine, one first-party run. Repo contains AGENTS.md and CLAUDE.md (AI-assisted development). [retier] benches/walk.rs ignores exit status and never compares outputs; wall time only, 7 walkers against single-threaded find. The code drops unreadable directories silently with exit 0, ignores write errors, and idle workers spin instead of parking. Numbers are from the 2026-06-19 walker, not re-run for 0.9.0-0.10.2.

Supports a subset of find(1) options. Uses mimalloc. README says the advantage scales with core count and shrinks toward parity on 1-2 core hosts and on a cold cache.

## Maintenance

Actively maintained (0.10.2, last commit 2026-10-10, MIT, 10 stars, AI-assisted development per CLAUDE.md/AGENTS.md) and easy to install as a binary. Treat it as a fast lister, not a find replacement: the speedup is mostly 8-thread parallelism, warm-cache only, and errors are swallowed silently (code reading, not run).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Criterion run with public code (benches/walk.rs), CPU model (Xeon E5-1630 v3) and minifind's profile flags in Cargo.toml, but rustc version and GNU find's version and build flags are not stated, so it falls short of A for the baseline side; C.
- **Verifier notes:** Numbers match the README exactly (26.634/26.702/26.779 ms vs 92.463/92.998/93.565 ms, about 3.5x). Shortcomings: parallel vs single-threaded baseline (not a codegen win; same_algorithm false), no output-equality check, GNU find build unstated. Related to sharkdp/fd (already listed, wave 14 C) but not a fork or port of it.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-108 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/README.md>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/benches/walk.rs>
  - <https://github.com/dkorunic/minifind>
  - <https://github.com/dkorunic/minifind/commits>
  - <https://github.com/dkorunic/minifind/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/README.md>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/benches/walk.rs>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/src/walk.rs>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/src/walk/unix.rs>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/src/args.rs>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/src/interrupt.rs>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/src/filetype.rs>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/src/sched.rs>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/man/minifind.1.scd>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/dkorunic/minifind/HEAD/CLAUDE.md>
  - <https://github.com/dkorunic/minifind>
  - <https://github.com/dkorunic/minifind/commits/main>
  - <https://github.com/dkorunic/minifind/tree/main/src>
  - <https://github.com/dkorunic/minifind/tree/main/src/walk>
  - <https://github.com/dylni/normpath>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/dkorunic/minifind`) · [data/wave14/enrich/raw/github_com_dkorunic_minifind.json](../../../data/wave14/enrich/raw/github_com_dkorunic_minifind.json) (enrichment confidence 0.75)

</details>
