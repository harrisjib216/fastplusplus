# dups (c-blake/bu, Nim duplicate-file finder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Nim` · `MIT` · 🟢 active

> Nim exact-duplicate file finder; claimed \~2x over jdupes when RAM-cached, though the author's 2019 timing favored jdupes by 7%.

| | |
|---|---|
| **Beats** | jdupes (C) |
| **Claimed result** | 'I continue to benchmark it as \~2X faster than jdupes in a fully RAM-cached test case' (undated, no setup). The author's own like-mode measurement in cligen issue #99 (2019-06-30) has jdupes 410 ms vs dups 439 ms on a hot-cached /usr/src/linux, jdupes about 7% faster (enricher correction). |
| **Workload** | Finding sets of files with identical contents in a fully RAM-cached test case; the file set, file counts, machine, jdupes version and the options used on either side are not stated. |
| **Metric** | latency (wall time) |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 77 stars (repository) |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/c-blake/bu) · [benchmark](https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/dups.md) |

## Verdict

The only claim is one undated first-party sentence in doc/dups.md: \~2X faster than jdupes on a fully RAM-cached test case, with no file set, machine, versions, flags or script. The author's own concrete timing (cligen issue #99, 2019, /usr/src/linux hot cache, both tools confirming byte for byte) had jdupes 7% faster, and his April 2019 comment gave '1.25 to 2x' on three or four personal trees.

## Use it when

- Mapping duplicate data in local, page-cached trees (source trees, home directories, build outputs) when you want a report rather than automatic deletion
- Scripts that only need a yes/no answer: the exit status is non-zero if any duplicate exists, and -b stops after the first set
- Trees where most size collisions are pairs: those are always settled by an exact byte compare
- Nim programs that want a dupSets iterator over a size-to-paths table instead of shelling out
- Quick approximate pre-passes with -H size or -s slice before a careful -c pass

## Skip it when

- Deleting or hard-linking from the default output: groups of three or more same-size files are matched on a 64-bit non-cryptographic hash unless -c is given
- NFS, sshfs or other network/FUSE trees walked recursively: dups hard-codes eof0=false in its cligen/dents walk, whose short-read early-EOF shortcut the dents source says fails on sshfs/NFS, so entries can be skipped; feed a find -print0 list instead
- Cold-cache or slow-disk runs: the page itself says uncached use is dominated by I/O, and no cold numbers exist
- Windows: dups is commented out of the Windows bin list in bu.nimble
- When you need jdupes-style actions or flags; dups has no delete, link or dedupe options

## How it is fast

It walks with cligen/dents (getdents64 plus statx, one path kept per device/i-node pair) and groups files by st_size, so size-unique files are never opened. A size group of exactly two files gets one memcmp of both mmap'd files with no hashing ('1 cmp ALWAYS less work than 2 hash'). Groups of three or more get one whole-file 64-bit wyhash variant (cligen hashWY) over mmap, with the size prefixed to the digest so all groups share one hash table, and by default the hash is trusted with no confirmation pass; -c instead sorts the mmap'd files with memcmp. Optional -j hashes in a forked process pool, which the source says rarely helps because hashing outruns I/O.

## Compared with alternatives

No duplicate finder is catalogued in this category (fclones is a separate wave-11 entry); dups is built on the same author's cligen/dents walker, so it inherits that entry's NFS caveat. Pick dups for a small, hackable Nim reporter on cached local trees, and add -c before acting on its output.

## Integration

| | |
|---|---|
| **Form** | module (single Nim source file built as a CLI by the bu nimble package; dupSets iterator importable) |
| **Dependencies** | cligen &gt;= 1.11.0 (bu.nimble also requires adix, nio, fitl and spfun for other tools); always links OpenSSL libcrypto (-lcrypto) for the SHA option, even when it is not used |
| **Minimum toolchain** | Nim 2.0.0+ (bu.nimble); nim.cfg and bu.nimble set no optimization flags, and the author advises -d:release for any timing (cligen issue #99) |
| **Platforms** | Linux and other POSIX systems; macOS linking of libcrypto was fixed in August 2026 (bu issue #9); excluded from the Windows build |
| **Thread safety** | Not applicable to the CLI; -j uses forked worker processes (cligen procpool), not threads; library thread safety not documented |
| **Drop-in for the baseline** | partial — same job as jdupes's default listing, but different flags and output, no delete/link actions, and recursion must be asked for with -r 0 |

## Gotchas

- Default -H wy trusts the hash for groups of three or more; only -c compares bytes, and even with -c a set of 4000 or more files (the mmap limit in carefulSplit) is printed uncompared with a 'too big to sort' warning, which matters most with -H size -c.
- Correctness bug found by reading dups.nim (not run): when digest() cannot open or mmap a file it writes an all-zero digest, overwriting the size prefix, so every unreadable file in a size group of three or more lands under the same key and is printed as one duplicate set (exit 1) unless -c is given; only the stderr 'dups: digesting ...' lines warn.
- Default -r 1 recurses only one directory level (0 means unlimited), and on NFS/sshfs the hard-coded early-EOF directory read can drop entries, so the help text's 'False negatives not possible' does not hold there.
- Evidence conflict: in cligen issue #99 (2019-06-30) the author compared like modes (jdupes -mnr vs dups -cbls, or jdupes -Q vs dups without -c) and his only published numbers, a hot-cache /usr/src/linux run, had jdupes faster: 410 ms vs 439 ms. The doc's undated \~2X therefore depends on the tree and is not backed by any published setup.

## Known shortcomings

- Prose-only '\~2X vs jdupes' on RAM-cached data; unequal default work since dups trusts wyhash (cmp=false) while jdupes confirms byte for byte unless -Q (jdupes behaviour from search snippets; repo 404).
- The author's own data contradicts the \~2X claim: in cligen issue #99 (2019-06-30), with like modes (jdupes -mnr vs dups -cbls) on a hot-cached /usr/src/linux, jdupes took 410 ms against dups 439 ms, jdupes 7% faster; an April 2019 comment said 1.25-2x. The doc's \~2X is undated with no setup. Correctness bug (code reading, not run): digest() gives unreadable files an all-zero digest that overwrites the size prefix, so unreadable files in size groups of three or more are printed as one duplicate set with exit 1 unless -c is given; eof0=false is hard-coded in the dents walk, so NFS and sshfs can drop entries; with -c, sets of 4000 or more files are printed uncompared; the default is -r 1; it always links -lcrypto. Retiered to D.

## Caveats and trade-offs

One sentence of prose with no script, file set, machine, jdupes version or flags, and no date. The default work differs: dups (Hash=wy, cmp=false in dups.nim) groups files by size, compares 2-file size groups directly and otherwise trusts a whole-file wyhash over mmap'd files. jdupes by default checks size, then partial and full hashes, then confirms each match byte for byte, and only -Q skips that pass (jdupes man pages, seen as search snippets only). Unless the run used dups -c or jdupes -Q, which the page does not say, the \~2X compares unequal work. The earlier caveat that dups differs by using a non-cryptographic hash was wrong: jdupes hashes non-cryptographically too, and the real difference is the confirmation pass. The cached-only condition removes the I/O bound that the page itself says dominates uncached use. The same author's rr, du and find claims are recorded separately under cligen; fclones (wave 11) is a separate entry that also beats jdupes. [retier] Enricher: the author's own data contradicts the claim; in cligen issue #99 (2019-06-30), with like modes (jdupes -mnr vs dups -cbls) on a hot-cached /usr/src/linux, jdupes took 410 ms against dups 439 ms, and an April 2019 comment said 1.25-2x. Correctness bug (code reading): digest() gives unreadable files an all-zero digest that overwrites the size prefix, so unreadable files in size groups of three or more are printed as one duplicate set with exit 1 unless -c is given; eof0=false is hard-coded in the dents walk; with -c, sets of 4000 or more files are printed uncompared; the default is -r 1; it always links -lcrypto.

Default hash is wyhash, so equal hashes can be false positives unless --cmp is given (sorting or compare can be slow with many large same-size files); options differ from jdupes.

## Maintenance

Active (bu last commit 2026-10-09; dups macOS link fix August 2026), MIT, a roughly 200-line file easy to vendor, but the speed claim is undated and contradicted by the author's own 2019 measurement, and code reading shows unreadable files reported as duplicates of each other unless -c is used.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The only evidence is one first-party sentence in doc/dups.md ('\~2X faster than jdupes in a fully RAM-cached test case') with no script, file set, machine, versions or flags: a number without methodology is tier C.
- **Retiered** C to D: Downgraded from C to D: the author's own like-for-like measurement contradicts the \~2X claim (cligen issue #99, 2019-06-30: jdupes -mnr 410 ms vs dups -cbls 439 ms on a hot-cached /usr/src/linux, jdupes 7% faster), the \~2X is undated with no setup, and the tool has a correctness bug that prints unreadable files as a duplicate set.
- **Verifier notes:** Numbers check out: the page really says \~2X versus jdupes, cached only. Shortcomings to record: prose-only claim; default work is unequal (dups trusts its wyhash, jdupes confirms byte for byte unless -Q); the hash caveat is corrected; no Nim-language mechanism. baseline_in_list is set to true for consistency with this wave's C/C++ baseline rule.
- **Fields the verifier corrected:** `baseline_in_list`, `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-98 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/dups.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/dups.nim>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/README.md>
  - <https://github.com/c-blake/bu>
  - <https://github.com/c-blake/bu/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/doc/dups.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/dups.nim>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/README.md>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/bu.nimble>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/nim.cfg>
  - <https://raw.githubusercontent.com/c-blake/bu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/fileUt.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/mfile.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/strUt.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/sysUt.nim>
  - <https://raw.githubusercontent.com/c-blake/cligen/HEAD/cligen/dents.nim>
  - <https://github.com/c-blake/cligen/issues/99>
  - <https://github.com/c-blake/bu/commits/main>
  - <https://github.com/c-blake/bu/issues?q=is%3Aissue>
  - <https://github.com/c-blake/bu/issues/9>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `paper:c-blake-bu-dups-w14-sys-blogs`) · [data/wave14/enrich/raw/paper_c_blake_bu_dups_w14_sys_blogs.json](../../../data/wave14/enrich/raw/paper_c_blake_bu_dups_w14_sys_blogs.json) (enrichment confidence 0.65)

</details>
