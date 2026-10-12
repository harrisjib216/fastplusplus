# walkdir and ignore walkers (dkorunic/bench_walk shootout)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Criterion shootout of Rust directory walkers; walkdir edges out a spawned GNU find, parallel ignore wins 3.7x with 8 threads.

| | |
|---|---|
| **Beats** | GNU find (C), system find invoked as 'find &lt;root&gt;' |
| **Claimed result** | Serial: walkdir 68.393 ms (best estimate) vs system find 90.621 ms, about 1.3x faster (derived from page data); walkdir_minimal 69.769 ms, ignore (serial unsorted) 73.457 ms, jwalk (serial) 77.011 ms, fts_walkdir 81.623 ms. Against the in-process C fts(3) walker through the fts crate (no process spawn, no printing, the closer like-for-like C row), walkdir is about 1.19x faster (derived from page data). Parallel winner: ignore (n threads, unsorted) 24.728 ms vs find 90.621 ms, about 3.7x faster (derived from page data); swdir 25.228 ms, jwalk 26.349 ms; the README says the three parallel leaders are each roughly 2.7x faster than the quickest serial walker. |
| **Workload** | Full recursive traversal of a shallow (--depth 1) clone of the mainline Linux kernel git tree, warm filesystem cache, Criterion (80 s warm-up, 400 s measurement per benchmark); single-threaded group and multi-threaded group. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E5-1630 v3 (4 cores, 8 threads with Hyper-Threading; the README calls it 8-core and says '8 physical cores'), 4-drive SATA RAID-10, ext4, warm page cache |
| **Compiler and flags** | Cargo [profile.bench] (used by cargo bench): opt-level 3, lto fat, codegen-units 1, strip symbols, debug-assertions and overflow-checks off (panic abort is set only in [profile.release], not in the bench profile); no target-cpu setting; rustc version not stated; Criterion 0.8.2; crates walkdir 2.5.0, ignore 0.4.26, jwalk 0.8.1, swdir 0.11.3, fts 0.3.0; GNU find is the distro binary, version and build flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Per the README: walkdir, ignore and jwalk read each directory once and use the d_type field from readdir(3), so they recurse without extra stat calls; ignore, swdir and jwalk additionally traverse in parallel with work stealing on 8 cores. |
| **Adoption** | 1 star; winners: walkdir (BurntSushi/walkdir, Unlicense/MIT, 680M crates.io downloads), ignore (crates/ignore in BurntSushi/ripgrep, Unlicense OR MIT, 189M downloads), swdir (nabbisen/swdir, Apache-2.0) |
| **Last commit** | 2026-06-06 |
| **Links** | [repository](https://github.com/dkorunic/bench_walk) · [benchmark](https://github.com/dkorunic/bench_walk) |

## Verdict

On one Xeon E5-1630 v3 (4 cores, 8 threads), ext4 on SATA RAID-10, warm cache, shallow Linux kernel clone, Criterion 80 s warm-up and 400 s measurement: walkdir 68.39 ms against a spawned GNU find 90.62 ms (about 1.3x, derived from page data) and against glibc fts via the fts crate 81.62 ms (about 1.19x), and parallel ignore 24.73 ms with 8 threads (about 3.7x against single-threaded find). Cargo bench profile is opt-level 3, fat LTO, one codegen unit; rustc, GNU find and glibc versions are not stated.

## Use it when

- Rust programs that must enumerate large trees (source checkouts, build outputs, backup scanners) and only need paths and file types: walkdir serially, ignore's build_parallel() when you can use several cores.
- Tools that need gitignore, hidden-file and glob filtering during the walk: ignore applies them while walking instead of filtering a find listing afterwards.
- Warm-cache traversals of tens of thousands of entries where per-entry stat calls would dominate (walker and fsindex, which stat every entry, were about 3x slower than walkdir here).
- Replacing a spawned find subprocess inside a Rust service, which also removes process start-up and stdout parsing.

## Skip it when

- As evidence that Rust walks faster than C: walkdir's own README says its speed is comparable with find and glibc nftw with no observable difference, and the 1.3x gap here sets an in-process iterator against a find subprocess whose output is piped and buffered.
- Shell use as a find replacement: these are crates; for a CLI see hunt, and find's predicate language (-newer, -exec, -perm) has no equivalent here.
- Workloads that need ordered output: every crate here ran with sorting disabled, and ignore's parallel visitor runs on several threads at once, so entries do not arrive in sorted order.
- Cold-cache or network filesystems: every number in the table is warm page cache on local ext4 RAID-10, so disk seek behaviour was not measured.
- Code that needs per-entry metadata anyway: once each entry is stat'ed, the d_type advantage that separates the top tier from walker and fsindex disappears.

## How it is fast

walkdir, walkdir_minimal, ignore and jwalk read each directory once and use the d_type field from readdir(3) to tell files from directories, so they never stat an entry when only paths are wanted; the README attributes the second tier (walker, fsindex and others several times slower) to a syscall per entry. ignore's parallel walker (crossbeam-deque work stealing) and jwalk/swdir spread directories over threads, giving about 2.7x over the best serial walker on 8 hardware threads because traversal is syscall-bound.

## Compared with alternatives

Use walkdir or ignore when traversal is embedded in your own Rust code; hunt is the catalogued CLI replacement for GNU find (12x on a first-match search), uutils findutils has no speed claim, and ripgrep is the listed tool that already ships the ignore walker.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | walkdir: same-file (plus winapi-util on Windows); ignore: crossbeam-deque, globset, log, memchr, regex-automata, same-file, walkdir (plus winapi-util on Windows) |
| **Minimum toolchain** | walkdir: Rust 1.60.0 (README MSRV policy); ignore 0.4.33: Rust 1.88 (crates.io rust-version; 0.4.26 as benchmarked declares none) |
| **Platforms** | any std target: walkdir is described as cross-platform and both crates carry Windows-specific dependencies; the benchmark itself ran only on Linux x86-64 |
| **Thread safety** | walkdir is a single-threaded iterator; ignore's WalkParallel builds one visitor per worker thread from a factory closure and runs them concurrently, so state shared between visitors must be synchronised |
| **Drop-in for the baseline** | partial — library replacements for the traversal part of find inside a Rust program, not for the find command or its predicates |

## Gotchas

- Harness asymmetry behind the serial win: src/lib.rs times find as Command::new("find").arg(root).output(), so the find row includes process spawn and writing every path through a pipe into a buffered Vec, while the crate rows only iterate (for _ in WalkDir::new(root) {}). walkdir's README reports parity with find and nftw on the author's own runs, so the 1.3x serial margin is most plausibly this overhead, not a faster walk; the ratio was stable at about 1.3x across the three published tables (Oct 2024: 54.98 ms vs 72.39 ms; June 2026: 69.50 vs 93.68 and 68.39 vs 90.62).
- The parallel 3.7x is 8 threads (num_cpus::get() on a 4-core, 8-thread Xeon E5-1630 v3, which the README calls 8-core and '8 physical cores') against single-threaded find; the fairer parallel comparison is only among the crates.
- The 'C' row closest to like-for-like, fts_walkdir, is glibc fts(3) called through the fts crate, whose wrapper copies each entry into two PathBufs (path and name), so walkdir's 1.19x margin over it also includes Rust wrapper cost.
- The test tree is a fresh depth-1 clone of torvalds/linux HEAD that the bench deletes when it finishes, and the kernel commit is not recorded, so absolute times are not comparable between README versions (they rose from 55 ms to 68 ms for walkdir between the 2024 and 2026 tables); each table itself comes from one run, since every row changed in each update.

## Known shortcomings

- The find row includes process spawn and captured output while the crate rows print nothing; the parallel 3.7x is 8 threads against single-threaded find. CPU is a Xeon E5-1630 v3 (4 cores, 8 threads; the README says 8-core); rustc and find versions unstated. A fairer C row: walkdir beats fts(3) by about 1.19x (derived from page data). The ignore crate is part of the listed ripgrep project.
- Enricher: the find row runs as a subprocess that pipes and buffers all output while the crate rows only iterate, and walkdir's own README says its speed is comparable to find and nftw, so the stable 1.3x serial win (three published tables) is most likely harness overhead; the parallel 3.7x is 8 threads on a 4-core/8-thread E5-1630 v3 against single-threaded find; the fts_walkdir row is glibc fts behind a Rust wrapper copying two PathBufs per entry.

## Caveats and trade-offs

The lead calls these Go walkers; they are Rust crates (the repo benchmarks Rust walking crates and benchmarks system find as the only non-crate baseline). The find baseline is not like-for-like: src/lib.rs runs it as Command::new('find').arg(root).output(), so the find row includes process spawn and capturing every printed path through a pipe into memory, while the crate rows only iterate entries (for _ in WalkDir::new(root) {}) without printing; the README itself says find 'additionally pays process-spawn and output-formatting overhead'. That asymmetry alone could account for the 1.3x serial gap, so the serial win over find is weak; the fairer C comparison on the page is the fts_walkdir row (glibc fts(3) through FFI, no_metadata), which walkdir beats by about 1.19x. The 3.7x parallel win is threads against a single-threaded find: ignore_parallel uses num_cpus::get() threads, which is 8 logical threads on this 4-core, 8-thread Xeon E5-1630 v3 (the README's '8-core' and '8 physical cores' are wrong). GNU find version, build flags and glibc are unstated, and the rustc version is unstated. Single machine and one tree (shallow Linux kernel clone including .git); results table last updated in the 2026-06-06 commits. The bench author also wrote minifind, a parallel Rust find clone. I report ignore as the headline winner against find; walkdir is the best serial walker. The ignore entry overlaps with ripgrep's existing record (ignore is the crates/ignore member of BurntSushi/ripgrep). [retier] Enricher: find runs as a subprocess that pipes and buffers all output while crate rows only iterate; walkdir's README itself says its speed matches find and nftw; the fts_walkdir row wraps glibc fts in Rust and copies two PathBufs per entry.

Library crates, not CLIs: walkdir is the serial readdir/d_type walker, ignore adds gitignore handling and a work-stealing parallel walker, jwalk and swdir are other parallel walkers. The README notes the speedup of the parallel walkers is sublinear (2.7x on 8 cores) because traversal is syscall and I/O bound.

## Maintenance

The shootout repo is active (last commits 2026-06-06, MIT) and the winners are healthy, widely used crates (walkdir 680M downloads, last release 2.5.0 in March 2024; ignore 189M downloads, 0.4.33 in August 2026, both Unlicense/MIT), but the serial win over find is a harness artifact and the parallel win is threads against one thread, so treat the entry as a crate recommendation rather than a language-speed result.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table (Criterion, benches/benchmark.rs plus src/lib.rs) shows walkdir 68.393 ms and parallel ignore 24.728 ms against system GNU find 90.621 ms on a stated CPU with Cargo profile flags in Cargo.toml, but the rustc version and the GNU find version and build flags are not stated and the find row is not like-for-like (process spawn plus captured output), so it falls short of A; a one-star personal shootout is not a well-known independent suite, so C.
- **Verifier notes:** Numbers match the README table exactly. Shortcomings: find row charged with process spawn and output capture while crate rows print nothing; parallel win is 8 threads against single-threaded find; README misstates the CPU as 8-core (it is 4 cores, 8 threads); rustc and find versions unstated. ignore is part of ripgrep, which is already listed; consider whether the orchestrator wants this shootout as its own entry or as a second claim.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-115 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/dkorunic/bench_walk>
  - <https://github.com/dkorunic/bench_walk/commits>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/HEAD/README.md>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/HEAD/benches/benchmark.rs>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/HEAD/README.md>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/HEAD/benches/benchmark.rs>
  - <https://github.com/dkorunic/bench_walk/commits>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/4faf795/README.md>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/df94007/README.md>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/9f25a40/README.md>
  - <https://raw.githubusercontent.com/dkorunic/bench_walk/aa1c26e/README.md>
  - <https://raw.githubusercontent.com/BurntSushi/walkdir/HEAD/README.md>
  - <https://raw.githubusercontent.com/dalance/fts-rs/HEAD/src/fts.rs>
  - <https://raw.githubusercontent.com/dalance/fts-rs/HEAD/src/walkdir.rs>
  - <https://crates.io/api/v1/crates/walkdir>
  - <https://crates.io/api/v1/crates/ignore>
  - <https://crates.io/api/v1/crates/jwalk>
  - <https://crates.io/api/v1/crates/fts>
  - <https://crates.io/api/v1/crates/swdir>
  - <https://crates.io/api/v1/crates/walkdir/2.5.0/dependencies>
  - <https://crates.io/api/v1/crates/ignore/0.4.26/dependencies>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/dkorunic/bench_walk`) · [data/wave14/enrich/raw/github_com_dkorunic_bench_walk.json](../../../data/wave14/enrich/raw/github_com_dkorunic_bench_walk.json) (enrichment confidence 0.8)

</details>
