# lsr

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig ls(1) clone that batches directory open, statx and passwd/group/localtime reads through io_uring; beats GNU ls -al.

| | |
|---|---|
| **Beats** | GNU ls 9.7 (readdir/stat syscalls); also eza, lsd, uutils, busybox |
| **Claimed result** | hyperfine, directory of n plain files, '-al': n=10,000 lsr 22.1 ms vs GNU ls 38.0 ms (1.72x, derived from page data), busybox 32.5 ms, eza 40.2 ms, uutils 89.6 ms, lsd 153.4 ms; n=10 lsr 372.6 us vs ls 1.4 ms (3.8x, derived from page data). strace -c at n=10,000: 848 syscalls vs 30,396 for GNU ls. |
| **Workload** | Listing a directory of n plain files (10 to 10,000) with ls -al, timed with hyperfine, syscalls counted with strace -c. |
| **Metric** | latency |
| **Compiler and flags** | zig build -Doptimize=ReleaseSmall (install instruction; benchmark build flags not explicit) |
| **Adoption** | 52 stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/rockorager/lsr) · [benchmark](https://github.com/rockorager/lsr/blob/main/README.md) |

## Verdict

First-party hyperfine runs on Linux on directories of n plain files with -al: lsr 0.1.0 took 22.1 ms vs 38.0 ms for GNU ls 9.7 at n=10,000 (1.72x, derived from page data) and 372.6 us vs 1.4 ms at n=10, with busybox 1.36.1 close at every size (32.5 ms at n=10,000); strace -c counted 848 vs 30,396 syscalls. CPU, kernel, filesystem, cache state and lsr's build mode are not stated, and the large-n runs used the version that dropped some stat tasks.

## Use it when

- Interactive long listings (-l) on Linux with a kernel that has io_uring statx support, where startup and per-entry syscall cost dominate
- Small directories (tens to hundreds of files), where the README shows the largest gap: 372.6 us vs 1.4 ms for GNU ls at n=10
- As a reference design for batching many stat-like metadata calls through io_uring in your own C/C++ tool (see liburing for the C API)

## Skip it when

- Scripts that depend on exact GNU ls flags or output format; the option set is smaller and output differs (icons, colors, sizes)
- macOS/BSD: it builds and runs but gets no syscall batching, so the speed claim does not apply
- Environments that disable io_uring (many container runtimes and hardened kernels restrict it; the HN discussion raised its security record)
- Code that needs a library API; nothing here is callable from C++
- Versions before the 2026-09-19 commit on directories with more than about 252 entries: entries could get dropped stat tasks and wrong metadata (issue #5)

## How it is fast

It submits the directory open, one statx per entry and the opens/reads of /etc/localtime, /etc/passwd and /etc/group as io_uring requests through the author's ourio library (256-entry ring), so thousands of stat calls become a few io_uring_enter syscalls (848 syscalls vs 30,396 for GNU ls at 10,000 files). It parses /etc/passwd and /etc/group itself instead of calling getpwuid/getgrgid per entry (libc lookup is only a fallback for uids not in the file), sorts a small name+kind struct before stat results arrive, and uses an arena with a 1 MiB stack-fallback buffer in release builds.

## Compared with alternatives

Pick lsr when you want a faster ls -l specifically; for recursive traversal (find-style listing) bfs or al-dente are the catalogued choices, and for building your own batched-metadata code in C/C++ use liburing directly, since lsr exposes no library.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | ourio (author's io_uring/kqueue library), zeit (time zones), zzdoc (man page generation); all pinned in build.zig.zon; links libc |
| **Minimum toolchain** | Zig 0.15.1 |
| **Platforms** | Linux (io_uring path); macOS and BSD build without the batching benefit |
| **Thread safety** | not applicable (single-threaded command-line program) |
| **Drop-in for the baseline** | partial — common flags (-a, -A, -l, -r, -t, -1, -C) match ls, but many GNU ls options are missing and the output format differs |

## Gotchas

- The benchmark table was produced with lsr 0.1.0; at n=1,000 and 10,000 that version overflowed the 256-slot ring and dropped stat tasks, so some entries showed undefined metadata (issue #5: a file printed as root/root, 0 B, 31 Dec 1969). The fix landed on 2026-09-19 ('io: keep stat batches within the ring capacity'), after the published numbers.
- /etc/passwd is read in a single 16 KiB read and /etc/group in a single 8 KiB read; larger files are truncated, and the parser unwraps the third field of each line, so a line cut before its second colon could abort the program (read from src/main.zig; not reported as an issue).
- Symlink targets are resolved with a blocking readlink per link (the code notes io_uring cannot do readlink), so link-heavy directories lose part of the benefit.
- Open issue #7 reports that --help does not work as expected; a 2025-12-28 commit moved --help output to stdout.

## Known shortcomings

- The README table ran lsr 0.1.0, which at n=1,000 and 10,000 overflowed the 256-slot ourio ring and dropped stat tasks, so some entries got undefined metadata (issue 5, open at the time); fixed on 2026-09-19 in commit 2098707, after the numbers were published. Zig, not C++.

## Caveats and trade-offs

First-party; CPU, kernel, filesystem and cache state not stated; no benchmark script in the README; a tool comparison (io_uring-batched statx) rather than a library. The relative gap versus GNU ls is largest at small n (3.8x at n=10) and narrows to 1.72x at n=10,000; busybox is close at every size. io_uring batching only on Linux; macOS/BSD builds get no syscall benefit.

Linux io_uring benefit only; on macOS/BSD no syscall batching; Zig 0.15.1 build; ls clone (not a library, not callable from C++ as an API); HN thread raised security concerns about io_uring.

## Maintenance

Actively maintained (last commit 2026-09-19, fixing a ring-overflow metadata bug), MIT-licensed, about 1,400 lines of Zig; useful as a tool or as a design to copy, not as a linkable library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks section gives first-party hyperfine and strace -c tables against GNU ls 9.7, busybox 1.36.1, eza, lsd and uutils with versions, but no benchmark script, CPU model, kernel or build flags; first-party with partial methodology is C.
- **Verifier notes:** All numbers match the README tables exactly. The record's caveat that smaller directories narrow the gap was backwards and is corrected. Metadata (MIT, 52 stars, last commit 2026-09-19) checked on github.com.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/rockorager/lsr>
  - <https://github.com/rockorager/lsr/blob/main/README.md>
  - <https://github.com/rockorager/lsr/commits/main>
  - <https://raw.githubusercontent.com/rockorager/lsr/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/rockorager/lsr>
  - <https://raw.githubusercontent.com/rockorager/lsr/HEAD/README.md>
  - <https://raw.githubusercontent.com/rockorager/lsr/HEAD/build.zig>
  - <https://raw.githubusercontent.com/rockorager/lsr/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/rockorager/lsr/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/rockorager/lsr/HEAD/src/main.zig>
  - <https://github.com/rockorager/lsr/issues?q=is%3Aissue>
  - <https://github.com/rockorager/lsr/issues/5>
  - <https://github.com/rockorager/lsr/commits/main>
  - <https://github.com/rockorager/lsr/commit/HEAD>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/rockorager/lsr`) · [data/wave11/enrich/raw/github_com_rockorager_lsr.json](../../../data/wave11/enrich/raw/github_com_rockorager_lsr.json) (enrichment confidence 0.7)

</details>
