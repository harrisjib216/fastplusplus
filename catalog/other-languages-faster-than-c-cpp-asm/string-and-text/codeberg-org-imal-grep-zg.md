# zrep (grep-zg, Zig grep clone)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Zig` · `no license` · ⚪ unknown

> Hobby multithreaded AVX2 grep in Zig (zrep); self-reported 9.6x faster than GNU grep 3.12 on one log, near ripgrep.

| | |
|---|---|
| **Beats** | GNU grep 3.12 (C); the same table also lists ripgrep 15.1.0 |
| **Claimed result** | Snippet only, from search-result summaries of the README (never opened): a 'norm' (normal search) row with zrep 32.7 ms, ripgrep 38.4 ms, GNU grep 314 ms, about 9.6x faster than GNU grep (derived from snippet data); one summary also reports a second table on a 271 MB, 2.5M-line log (warm cache, output piped through cat) with zrep 76 ms, ripgrep 198 ms and GNU grep 248 ms in normal mode (about 3.3x, derived from snippet data), and about 10 ms vs 49 ms (ripgrep) and 52 ms (GNU grep) for a count mode. |
| **Workload** | Unverified, snippet summaries conflict: the search agent's snippet described a recursive search for 'stdio.h' under /usr/include (409 MB, 41K files, warm cache, 28 cores, output piped through cat); two later snippets attribute the same 32.7/38.4/314 ms row to a single 205 MB log with 706K matches of 'debug' on 28 cores, and a second table to a 271 MB, 2.5M-line log with output piped through cat to avoid GNU grep's /dev/null shortcut. |
| **Metric** | latency |
| **Hardware** | 28 cores (CPU model not seen) |
| **Compiler and flags** | Zig 0.15.2 required to build; optimization mode and GNU grep build not seen |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Links** | [repository](https://codeberg.org/imal/grep-zg) · [benchmark](https://codeberg.org/imal/grep-zg) |

## Verdict

Self-reported README numbers, read only through search summaries: on a 205 MB log with 706K matches of 'debug', warm cache, zrep 32.7 ms vs ripgrep 38.4 ms vs GNU grep 3.12 314 ms for normal output (about 9.6x over GNU grep, derived), -v 121 ms vs 353 ms vs 770 ms, -c 38.0 ms vs 38.1 ms vs 288 ms; CPU reported only as 28 cores, Zig build mode and GNU grep build and locale not stated.

## Use it when

- Experimenting with within-file parallel search of one very large, warm-cache log on a many-core x86-64 machine with AVX2, where the README's -v row (121 ms vs ripgrep 353 ms vs GNU grep 770 ms on a 205 MB log) shows the largest gap.
- Reading as a compact Zig example of chunked, line-aligned multithreaded scanning with SIMD, if you can reach Codeberg or its zff.dev mirror.
- Ad-hoc literal searches where only the standard -v, -c, -n, -o modes are needed and GNU grep compatibility does not matter.

## Skip it when

- As a GNU grep replacement in scripts: option coverage, regex syntax (BRE/ERE/PCRE), locale and binary-file handling, exit codes and context flags are not documented in anything reachable here.
- When ripgrep is available: on the README's own 205 MB log ripgrep is faster with -n (33.6 ms vs 36.5 ms) and -o (33.4 ms vs 36.7 ms), ties with -c (38.1 ms vs 38.0 ms) and is only about 15% slower for plain output (38.4 ms vs 32.7 ms); ripgrep also has .gitignore handling, mature Unicode regex and a long track record.
- Recursive searches over many small files (source trees): the single-file chunking is the advertised advantage, and no directory-walk numbers were readable this session.
- Non-AVX2 CPUs or non-x86 platforms: the README advertises an AVX2 search and any fallback is not documented.
- Production use generally: a hobby project with no visible release history, license contents not seen, and no independent measurement.

## How it is fast

Per the README feature list (seen only through search-result summaries), it splits each file into line-aligned chunks and searches all chunks on every core at once with an AVX2-vectorised scanner. That is within-file parallelism, which GNU grep (single-threaded) and ripgrep (one thread per file, so one thread on a single large file) do not do. The source was not readable, so the exact substring algorithm (memchr-style first-byte filter, two-byte SIMD prefilter or other) and how output order is preserved across threads are unknown.

## Compared with alternatives

Among catalogued grep-like tools, fastgrep (Rust, 3.7-9.9x over GNU grep 3.12 with a warm trigram index) and The Platinum Searcher are better documented, and xerg only beats BSD grep; pick zrep only to study or try within-file parallel scanning of a single huge log, and otherwise prefer ripgrep or fastgrep.

## Integration

| | |
|---|---|
| **Form** | source-drop (standalone CLI built with zig build) |
| **Dependencies** | not documented (Zig toolchain only, as far as the search summaries show) |
| **Minimum toolchain** | Zig 0.15.2 (per build.zig.zon, from search summaries) |
| **Platforms** | x86-64 with AVX2 advertised; other platforms not documented |
| **Thread safety** | not applicable (CLI); runs multiple worker threads per file |
| **Drop-in for the baseline** | partial — same basic grep usage and common flags (-v, -c, -n, -o) appear in its benchmark, but flag coverage and regex dialect versus GNU grep 3.12 are not documented |

## Gotchas

- Every figure here comes from search-engine summaries of the README: codeberg.org (proxy CONNECT 403 and DNS failure), its zff.dev mirror and the besthub.dev article were all unreachable this session, and there is no GitHub mirror, so the benchmark script, corpus, CPU model, zrep's Zig release mode and GNU grep's build and locale were never inspected.
- The summaries attribute the 32.7 / 38.4 / 314 ms row to a 205 MB log with 706K matches of 'debug', while an earlier summary described a recursive /usr/include search, and a second table (271 MB, 2.5M-line log, output piped through cat to avoid GNU grep's /dev/null shortcut: zrep 76 ms vs ripgrep 198 ms vs GNU grep 248 ms) also exists; which methodology applies to which row is unverified.
- In the 205 MB table zrep's count mode (-c, 38.0 ms) is slower than its full printing mode (32.7 ms), which is unusual since counting does strictly less work; it may mean the printing row's output sink differs (for example /dev/null or a pipe) from the count row, but the harness could not be read to check.
- The headline gap over GNU grep compares a tool using all cores (the earlier summary says 28) within a single file against single-threaded GNU grep, so most of the 9.6x is parallelism rather than a better single-core matcher; against ripgrep, which is also effectively single-threaded on one file, the gap shrinks to 1.17x or reverses.

## Known shortcomings

- Snippets only (Codeberg proxy 403, zff.dev unreachable, no GitHub mirror) that disagree on the corpus for the 32.7/38.4/314 ms row (/usr/include vs a 205 MB log); 28 threads against single-threaded GNU grep; license unknown.
- Snippet only (confidence 0.25): codeberg.org (proxy CONNECT 403, ENOTFOUND), zff.dev, besthub.dev and Software Heritage were all unreachable, so the README, licence, code and benchmark method were never opened. Further snippet rows: -v 121/353/770 ms and -c 38.0/38.1/288 ms (zrep/ripgrep/GNU grep); ripgrep is faster on -n and -o; the 9.6x over GNU grep is mostly parallelism (AVX2 plus line-aligned chunks across all cores) and only 1.17x over ripgrep. zrep -c (38.0 ms) is slower than its plain print row (32.7 ms), so the output sink may differ between rows (unverified).

## Caveats and trade-offs

Snippet only: codeberg.org (proxy CONNECT 403), zff.dev (getaddrinfo ENOTFOUND) and the besthub.dev article (ENOTFOUND, and it covers a different 'zg', a semantic search tool) were unreachable, and there is no GitHub mirror, so the README, license, code, build mode and benchmark method were never opened; every figure and the language (Zig, Zig 0.15.2 per the earlier snippet) come from search-result summaries. The summaries disagree on which corpus the 32.7/38.4/314 ms row measured (/usr/include recursive vs a 205 MB log), and one says that row wrote to /dev/null while a second table piped output through cat. One machine, warm cache, a multi-threaded tool against single-threaded GNU grep, so the ratio is mostly parallelism; GNU grep's build (distro -O2 or otherwise) and zrep's Zig release mode are unknown. License, stars and last commit unverified. Low confidence; re-open the Codeberg README when a session can reach it and drop to D if the numbers differ. [retier] Snippet only: codeberg.org (proxy CONNECT 403, ENOTFOUND), zff.dev, besthub.dev and Software Heritage were unreachable and there is no GitHub mirror, so the README, licence, code, build mode and benchmark method were never opened; every figure comes from search-result summaries, which disagree on the corpus behind the 32.7/38.4/314 ms row. Further snippet rows: -v 121/353/770 ms and -c 38.0/38.1/288 ms (zrep/ripgrep/GNU grep); ripgrep is faster on -n and -o. The 9.6x over GNU grep is mostly parallelism (AVX2 search over line-aligned chunks across all cores) and only 1.17x over ripgrep; zrep -c (38.0 ms) is slower than its plain print row (32.7 ms), so the output sink may differ between rows (unverified).

Hobby project by its own description ('how fast grep could really go if you stripped everything away'), so features and regex coverage are likely far narrower than GNU grep; license, build and portability not checked.

## Maintenance

Maintenance status unknown (last commit, release history and license text not reachable; a LICENSE file exists per search summaries); a hobby, reference-only project hosted on Codeberg with a zff.dev mirror, so treat its numbers as unverified until the README and benchmark script can be opened.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Snippet only: codeberg.org (proxy CONNECT 403), zff.dev (ENOTFOUND) and no GitHub mirror (github.com/imal/grep-zg 404), so the README was never opened; three separate search summaries repeat the 32.7 ms / 38.4 ms / 314 ms row, so first-party numbers exist but their workload and method are unverified. Snippet-only numbers are capped at C; the orchestrator may prefer D because the corpus attribution conflicts.
- **Verifier notes:** Could not open any primary source (Codeberg blocked, zff.dev unresolvable, no GitHub mirror); kept at C on consistent snippet numbers but corpus attribution conflicts between snippets and the gap is likely threads, not Zig. Shortcomings: snippet only, unverified workload, multi-threaded vs single-threaded GNU grep, license and maintenance unknown, low notability.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-94 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/imal/grep-zg>
- **Sources the enricher read:**
  - https://codeberg.org/imal/grep-zg (unreachable: proxy CONNECT 403 via curl, ENOTFOUND via WebFetch)
  - https://codeberg.org/imal/grep-zg/raw/branch/main/README.md (unreachable: proxy CONNECT 403)
  - https://zff.dev/imal/grep-zg (unreachable: ENOTFOUND; content known only from WebSearch summaries)
  - https://www.besthub.dev/articles/grep-showdown-rg-vs-tgrep-vs-rawgrep-vs-zg-ba946eb122fa (unreachable: ENOTFOUND)
  - https://archive.softwareheritage.org/browse/origin/directory/?origin_url=https://codeberg.org/imal/grep-zg (unreachable: ENOTFOUND)
  - https://github.com/jmwoliver/zipgrep (a different Zig grep, binary also named zg, compared only against ripgrep)
  - WebSearch: 'zrep grep-zg Zig grep imal benchmark ripgrep'
  - WebSearch: '"zrep" Zig grep multithreaded SIMD mmap "hobby project" license'
  - WebSearch: 'grep-zg zrep README regex support -v -c ripgrep GNU grep 271 MB log benchmark cat /dev/null'
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://codeberg.org/imal/grep-zg`) · [data/wave14/enrich/raw/codeberg_org_imal_grep_zg.json](../../../data/wave14/enrich/raw/codeberg_org_imal_grep_zg.json) (enrichment confidence 0.25)

</details>
