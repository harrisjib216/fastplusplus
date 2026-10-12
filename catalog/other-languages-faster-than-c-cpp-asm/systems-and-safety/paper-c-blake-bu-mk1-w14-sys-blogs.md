# mk1 (c-blake/bu, Nim up-to-date check for 1-to-1 build rules)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `MIT` · 🟢 active

> Nim freshness checker for 1-input-1-output rules; \~3x ninja's no-op check and \~40x GNU make on 40k pairs.

| | |
|---|---|
| **Beats** | ninja (C++) and GNU make (C); the table also times a bash while-read loop |
| **Claimed result** | 40,000 up-to-date file pairs on /dev/shm, one timed run each. mk1 0.039390 s wall. ninja second run with .ninja_log ('no work to do') 0.119358 s, about 3.03x (derived from page data); the README says \~3X faster than ninja's best case. Bash while-read loop 0.151993 s, about 3.86x (derived from page data); the README says \~4X. GNU make 1.550844 s, about 39x (derived from page data); the README says \~40X. ninja with the author's ninja-nv plus -t restat hack after removing .ninja_log 0.410272 s, about 10.4x (derived from page data). The 7.777944 s row is ninja's first run with no .ninja_log: it re-ran all 40,000 touch commands at 488% CPU, so it is a rebuild, not a freshness check. |
| **Workload** | Up-to-dateness check of 40,000 input/output file pairs in /dev/shm (nothing to rebuild), timed with the author's ru tool; mk1 reads a precomputed list of path pairs and prints the commands to run. |
| **Metric** | latency (wall time) |
| **Hardware** | Intel i7-1270P (Alder Lake), Linux 6.2.10, RAM file system (/dev/shm) |
| **Compiler and flags** | Not stated for mk1: no Nim version or flags, and the repo's nim.cfg holds only --path="." while bu.nimble sets no flags. 'Linux 6.2.10 built w/gcc-12' reads as the kernel's build compiler. ninja and GNU make versions and builds are not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Page: only a freshness check for many 1-to-1 pairs is done (about 60 lines of Nim originally, about 150 now, per the page's footnote), with no graph or log; the author attributes make's cost to subshell delegation and ninja's best case to its .ninja_log reuse. |
| **Adoption** | 77 stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/c-blake/bu) · [benchmark](https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/mk1.md) |

## Verdict

doc/mk1.md times one run of each tool with the author's ru on an i7-1270P (Alder Lake), Linux 6.2.10, /dev/shm, 40,000 up-to-date .c/.o pairs: mk1 0.039 s vs ninja's best no-op (second run with .ninja_log) 0.119 s (about 3x), a bash while-read loop 0.152 s (about 3.9x) and GNU make 1.55 s (about 39x). ninja's first run without .ninja_log took 7.78 s because it re-ran every touch command.

## Use it when

- Large fan-outs of independent per-file transforms (hashes, thumbnails, transcodes, compressed copies, shadow trees) re-checked often on a local file system
- Shell pipelines of the form find | tmpls IN OUT | mk1 'cmd %i &gt; %o' | sh, or into a parallel job runner
- Replacing a bash while-read loop with -nt tests (about 3.9x slower on the page) or a GNU make pattern rule over tens of thousands of files
- Scripts that only ask whether anything is stale: -q exits 1 when there is work

## Skip it when

- C/C++ compilation or anything with headers or several inputs per output: no depfile or multi-input support, so header edits go unnoticed
- When a changed command line should force rebuilds; ninja tracks commands in .ninja_log, mk1 compares mtimes only
- Network file systems: it passes AT_STATX_DONT_SYNC, which lets the kernel answer from cached attributes, so a remote update may be missed
- When the pair list is expensive to regenerate each time; the timed run starts from a ready-made list
- When you need the tool to run, schedule or clean up jobs; mk1 only prints commands, and the page's footnote shows the extra shell needed to create output directories and remove partial outputs

## How it is fast

It does only what the special case needs: one statx(STATX_MTIME) per path in batches of 32 pairs, a strict input-newer-than-output comparison and a print, with no manifest parse, no log, no graph and no implicit-rule search. Paths live in one growing char buffer addressed by offsets, so there is no per-path allocation. In the published run 34 of its 39 ms is system time for the 80,000 statx calls, while ninja's best case adds 73 ms of user time, mostly reading build.ninja and .ninja_log (an inference from the ru columns). A -d:batch build sends the statx calls through the author's out-of-tree batch-syscall kernel module.

## Compared with alternatives

No build-tool sibling is catalogued in this category; the nearest are the same author's stat-heavy replacements (cligen/dents, procs). Pick mk1 over ninja only when every rule is strictly 1-to-1 and freshness checks of tens of thousands of local files dominate; otherwise ninja's graph, depfiles and command tracking are worth the extra \~80 ms.

## Integration

| | |
|---|---|
| **Form** | module (single Nim source file built as a CLI by the bu nimble package) |
| **Dependencies** | cligen &gt;= 1.11.0 and bu/esquo (in the same repo); bu.nimble also requires adix, nio, fitl and spfun for other tools |
| **Minimum toolchain** | Nim 2.0.0+ (bu.nimble); nim.cfg and bu.nimble set no optimization flags |
| **Platforms** | Linux (statx; optional -d:batch kernel module path); other systems use Nim's getLastModificationTime, and mk1 is in bu.nimble's Windows bin list |
| **Thread safety** | Single-threaded CLI; not applicable |
| **Drop-in for the baseline** | no |

## Gotchas

- Unequal work: mk1 gets a precomputed flat pair list (tmpls, 3.76 ms by the author's tim, outside the timed run), while ninja parses a 40,000-statement build.ninja plus .ninja_log and GNU make expands \$(shell cat inp) and runs without -r, so built-in implicit rules stay active. Each tool ran once with no repeats, and no Nim, ninja or make versions or flags are given. The \~3x and \~40x come from a restricted problem, not Nim code generation.
- Harness flaw in the bash row (inference from the script, not measured): the loop runs '[ o -nt i ] || printf', which treats equal mtimes as stale, while mk1 rebuilds only when the input is strictly newer (mk1.nim line 107). The setup touches each directory's .c and .o files in one touch call on tmpfs, so many pairs probably share a timestamp. The bash row may then have printed rebuild commands to /dev/null instead of finding nothing to do, so the rows need not compute the same answer.
- An odd number of input lines silently drops the last unpaired input, because only complete pairs are added. An input that cannot be stat'd aborts with 'mk1: cannot age' and exit 1 unless -k is given.
- The 7.78 s ninja row is a full rebuild (no .ninja_log, all 40,000 touch commands re-run at 488% CPU), not a freshness check; compare against the 0.119 s second run.

## Known shortcomings

- Special-case tool against ninja/make with unequal work: the 7.78 s ninja row is a full rebuild, not a check; make ran without -r; no Nim flags or tool versions; single runs.
- Harness flaw (inference from the script, not measured): the bash row's '[ o -nt i ] || printf' treats equal mtimes as stale while mk1 needs the input strictly newer, and the same-touch tmpfs setup likely gave equal mtimes, so the rows may not compute the same answer. An odd line count silently drops the last input, and AT_STATX_DONT_SYNC is risky on NFS. The unequal-work caveat (precomputed pair list; ninja parses its manifest and log; make runs without -r) stands.

## Caveats and trade-offs

Compares a deliberately restricted tool (1-to-1 rules only, no dependency graph, no log) with general build systems on a special case, so same_algorithm is false. mk1 reads a precomputed flat list of path pairs (inp2, made by tmpls outside the timed run; the author's tim puts that at 3.76 ms), while ninja parses a 40,000-statement build.ninja plus .ninja_log. GNU make ran without -r, so its built-in implicit rules were active, on a Makefile that builds the target list with \$(shell cat inp). This may inflate make's 1.43 s user time; that is an inference, not measured. Each tool was timed once with ru and no repetitions; mk1's 39 ms is mostly system time (0.034 s sys). Build flags and tool versions are missing, though the script is complete and short enough to rerun. The footnote's 'over 4X faster than ninja' with a custom kernel module under Meltdown/Spectre mitigations has no numbers. First-party measurement by the author on a single machine. The win is less work, not Nim codegen. [retier] Enricher (inference from the script, not measured): the bash row's '[ o -nt i ] || printf' treats equal mtimes as stale while mk1 needs the input strictly newer, and the same-touch tmpfs setup likely gave equal mtimes, so the rows may not compute the same answer. An odd line count silently drops the last input, and AT_STATX_DONT_SYNC is risky on NFS.

Only handles the case where each output comes from exactly one input by one rule; no dependency graph, no depfile handling, no rule language, and it emits commands for a shell to run rather than running them.

## Maintenance

Active (bu last commit 2026-10-09), MIT, about 150 lines and easy to vendor; tier C single-run first-party numbers from a complete, rerunnable script, where the win is less work in a restricted problem and the bash baseline probably decided equal-mtime pairs differently.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/mk1.md has the complete shell benchmark script, its output, the CPU (i7-1270P) and the OS. It gives no Nim compiler or flags for mk1 and no ninja or GNU make versions or builds, and it is the author's own single run, so tier C (not A).
- **Verifier notes:** All timings match the page. Shortcomings to record: a special-case tool against general build systems (unequal work, no Nim mechanism); no mk1 build flags or tool versions; single unrepeated runs; the 7.78 s ninja row is a full rebuild, not a check; GNU make ran without -r (possible handicap, not measured). Repo: MIT, 77 stars, last commit 2026-10-09, active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-98 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/mk1.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/nim.cfg>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/bu.nimble>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/README.md>
  - <https://github.com/c-blake/bu>
  - <https://github.com/c-blake/bu/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/mk1.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/mk1.nim>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/tmpls.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/topn.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/zeh.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/README.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/bu.nimble>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/nim.cfg>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/mfile.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/sysUt.nim>
  - <https://github.com/c-blake/bu/commits/main>
  - <https://github.com/c-blake/bu/issues?q=is%3Aissue>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `paper:c-blake-bu-mk1-w14-sys-blogs`) · [data/wave14/enrich/raw/paper_c_blake_bu_mk1_w14_sys_blogs.json](../../../data/wave14/enrich/raw/paper_c_blake_bu_mk1_w14_sys_blogs.json) (enrichment confidence 0.65)

</details>
