# triehash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🔴 abandoned

> Order-preserving minimal perfect hash generator emitting nested C switches for fixed string sets; 1.85-5x gperf's throughput in author's benchmark.

| | |
|---|---|
| **Beats** | gperf |
| **Claimed result** | README Performance table (GB/s, higher is better). On jak-x230 (amd64, Core i5-3320M), Trie is 2.4 vs gperf 1.3 case-sensitive [\~1.85x, derived from page data], and Trie (\*) is 2.2 vs gperf (\*) 0.7 case-insensitive [\~3.1x, derived from page data]. Comparing like with like across all 7 host/arch columns, Trie is \~1.85x (x230) to \~5x (plummer ppc64el, 2.0 vs 0.4) faster than gperf case-sensitive. Trie (\*) is \~2x (eller mipsel, 0.2 vs 0.1, coarsely rounded) to \~4x (asachi arm64, 0.8 vs 0.2) faster than gperf (\*) case-insensitive [derived from page data]. |
| **Workload** | Each of the 82 field names from Debian Packages/Sources files is hashed 1,000,000 times back-to-back. hashbench also probes 3 extra words: Hallo, PaCKage, PackageXXX. Throughput is the summed word bytes divided by the total ns, reported in GB/s. The table has 7 host/arch columns on 5 hosts: jak-x230 and backup (amd64), asachi.d.o (arm64/armel/armhf), plummer.d.o (ppc64el), and eller.d.o (mipsel). Other competitors are re2c, djb hash variants, and APT's AlphaHash. |
| **Metric** | throughput |
| **Hardware** | jak-x230: Intel Core i5-3320M (stated in the README legend). backup (amd64) and the Debian porterboxes asachi.debian.org (arm64/armel/armhf), plummer.debian.org (ppc64el) and eller.debian.org (mipsel) are named by hostname only, with no CPU model. The legend's 'barriere has an Opteron 23xx' refers to an earlier table; barriere is not in the current table. |
| **Compiler and flags** | Per the julian-klode/hashbench Makefile: gcc (CC := \$(CROSS)-gcc; version not stated). CFLAGS ?= -O2 -g -fPIE -fstack-protector-strong -Wformat -Werror=format-security, and LDFLAGS ?= --static. The gperf baseline is generated with `gperf --includes --pic --readonly-tables`, plus --ignore-case for gperf (\*). The README notes also point to gcc bug 77729 (extra zero-extend instructions). |
| **Adoption** | 49 stars; used in APT (Debian package manager) |
| **Last commit** | 2019-04-16 |
| **Links** | [repository](https://github.com/julian-klode/triehash) · [benchmark](https://github.com/julian-klode/triehash#performance) |

## Verdict

The numbers come from the author's 2016 hashbench. Each of 82 Debian Packages/Sources field names, plus 3 probe words, was looked up 1,000,000 times back-to-back in a static GCC -O2 build (GCC version not stated), against gperf generated with --pic --readonly-tables. On a Core i5-3320M, triehash reached 2.4 GB/s vs gperf's 1.3 case-sensitive (\~1.85x) and 2.2 vs 0.7 case-insensitive (\~3.1x). On Debian porterboxes of unstated CPU model, the case-sensitive gap reached \~5x (ppc64el, 2.0 vs 0.4) and the case-insensitive gap \~4x (arm64, 0.8 vs 0.2). re2c (1.7) and APT's unrolled AlphaHash (2.3) came close on the x230, and the repeated-word loop favors branchy switch code.

## Use it when

- Small, fixed sets of field names, keywords or verbs known at build time (the benchmark used 82 Debian control-file field names) that you want mapped to an enum you then `switch` on.
- ASCII case-insensitive matching of such keys. This is where the gap to gperf is widest: 2.2 vs 0.7 GB/s on a Core i5-3320M, and 0.8 vs 0.2 on arm64.
- Tokenizers or parsers that already have (pointer, length). The function takes an explicit length, reads only bytes [0, length) and needs no NUL terminator.
- GCC/Clang builds on x86-64, ppc64el or arm64, where the multi-byte chunk reads are active and the reported speedups are largest.
- Plain C or mixed C/C++ codebases that want generated code with no runtime dependency beyond &lt;stdint.h&gt; and &lt;stddef.h&gt;.

## Skip it when

- Lookups on an unpredictable mix of keys. The benchmark hashed the same word 1,000,000 times in a row, so the branch predictor was fully trained on nested switches. Open issue #3 raises this and it was never re-measured with shuffled inputs.
- Large key sets (thousands of keys and up). Code size grows with the trie; the Debian package description itself says the generated code is 'larger' than gperf's, and there is no data beyond \~85 words.
- Key sets built at runtime, or lookups that must return a payload richer than an integer enum. gperf can return a user struct; with triehash you index your own array with the enum.
- MSVC or other non-GNU compilers, and ARM targets without unaligned access. These silently fall back to the byte-at-a-time switch, which was not benchmarked.
- Case-insensitive matching beyond ASCII. The 0x20 trick is ASCII-only.

## How it is fast

The keys go into a trie that is split by word length. The generated code is an outer `switch (length)` that dispatches to one function per length, and each of those is nested `switch` statements over 8-, 4- or 1-byte chunks read as unaligned integers on GNU C. The compiler turns these into compare/jump trees. There is no hash arithmetic, no data table and no final strcmp: reaching a leaf means every byte already matched, and a mismatch exits at the first differing chunk. In `--ignore-case` mode it ORs 0x20 into each chunk (e.g. `| 0x20202020`) wherever every key at that trie level is an unambiguous letter, so it needs no separate upper/lowercase cases. The author's blog reports about 4 instructions per byte.

## Compared with alternatives

Pick triehash over ConstexprCore/perfect_hash or constexpr-phf (Kronuz), which also beat gperf but need C++ constexpr machinery, when you need plain C output or ASCII case-insensitive string-to-enum matching and can accept a Perl step at build time. In a C++17+ codebase that wants the compiler to build the table with no external generator, or needs mapped values rather than an enum, frozen or ConstexprCore/perfect_hash fit better; strager/perfect-hash-tables is research code rather than a packaged generator.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Perl at generation time (Debian package `triehash`); the generated code needs only &lt;stddef.h&gt; and &lt;stdint.h&gt; |
| **Minimum toolchain** | Perl 5.14+ to run the generator: it uses package-block syntax, per issue #7, and CI covered Perl 5.14-5.28. Generated code is C with stdint.h. The multi-byte fast path needs GNU C (GCC/Clang: `__attribute__((aligned(1)))`, `__BYTE_ORDER__`); other compilers get the byte-wise fallback. It also builds as C++ via --enum-class (APT compiles it as .cc). |
| **Platforms** | Any. Multi-byte reads work on GNU C little- and big-endian, are disabled automatically on ARM without __ARM_FEATURE_UNALIGNED, and can be forced off with TRIE_HASH_NO_MULTI_BYTE. Benchmarked on amd64, arm64, armel, armhf, ppc64el and mipsel. |
| **Thread safety** | Not documented. The generated function is pure switch code with no tables or mutable state, so it is reentrant by construction. |
| **Drop-in for the baseline** | partial — it plays the same role as gperf (build-time key set, generated C lookup taking str+len), but it returns an enum instead of a keyword-struct pointer and uses its own input format, so call sites and the key file must be rewritten |

## Gotchas

- The POD documents `--namespace` and `--class` for C++, but GetOptions never registers them, so passing either aborts with 'Could not parse options!'. Only `--enum-class` and `--enum-name` (which accepts a qualified name such as `Foo::Bar`) work.
- Enum values follow input order. Inserting or removing a key mid-list renumbers every later value. APT's tagfile-keys.list warns that this order is part of libapt's ABI and should only be appended to.
- Non-members return `Unknown` with no hint, so callers need their own fallback path. APT falls back to a separate BetaHash bucket table for unknown fields.
- Multi-byte loads cast `&string[i]` to `uint64_t`/`uint32_t` typedefs with `aligned(1)` but no `may_alias`. They only work on GNU C, and 2-byte reads are off by default (`--multi-byte=320`) because the author found they slow older Intel CPUs. The README also cites GCC bug 77729, where the compiler inserts extra zero-extend instructions.

## Caveats and trade-offs

The benchmark code is not in the triehash repo. It lives in github.com/julian-klode/hashbench (MIT, 0 stars, last commit 2016-10-06), which the author's 2016-09-25 blog post links. Its Makefile and render-results.py produce exactly the README table layout, and the table landed in triehash the same day (2016-10-06). The gcc version is not stated. Only jak-x230 (Core i5-3320M) has a CPU model; the other hosts are named by hostname only. The method favors branchy switch-based code: each word is hashed 1,000,000 times in a row, so the branch predictor is fully trained and the cache is hot. The gperf baseline was generated with --pic --readonly-tables rather than gperf defaults. The mipsel figures (0.1-0.2 GB/s) are too coarsely rounded for meaningful ratios. The numbers date from 2016. re2c matchers and APT's unrolled AlphaHash (apt (\*\*), 2.3 GB/s on x230) also come close to Trie. triehash is a Perl script (GitHub language: Shell) that generates C code, and the generated C is directly callable from C++. The last commit on main is 2019-04-16; the debian/master packaging branch has commits up to 2022-12-14. Both are more than 3 years old, so the project is abandoned. APT uses triehash: apt-pkg/CMakeLists.txt runs it with --ignore-case to generate tagfile-keys (verified on the Debian/apt GitHub mirror).

Order-preserving (unlike most minimal perfect hash schemes), which trades some construction flexibility for keeping key order in the output table. Generator only handles a fixed key set known at generation time (codegen tool, like gperf, not a runtime container).

## Maintenance

Upstream has been abandoned since the last main commit on 2019-04-16 (Debian 0.3-3 was uploaded in 2020 and its packaging branch last touched in 2022). It is still a required build tool for APT and ships as 0.3-3 in every current Debian suite, and the MIT-licensed 728-line Perl script, or its generated C, is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The README table (added in commit e4acd52a, 2016-10-06) is the output of the author's benchmark repo github.com/julian-klode/hashbench (bench-runner.c, Makefile, render-results.py), which the 2016 announcement post links. That repo states the compiler (gcc via \$(CROSS)-gcc) and flags (-O2 -g -fPIE -fstack-protector-strong, --static; gperf --pic --readonly-tables), and the README gives the jak-x230 CPU (Core i5-3320M). A covers only the jak-x230 column, and the gcc version is not stated.
- **Verifier notes:** Upgraded to A after finding the linked benchmark repo (julian-klode/hashbench), which states the compiler and flags. A covers only the x230 column and the gcc version is not stated; if the orchestrator requires a compiler version, the fallback is C, not B. The original '1.8-3.4x' range understated the gap across architectures and paired case-sensitive Trie with case-insensitive gperf. It is corrected to like-for-like ratios: \~1.85-5x case-sensitive and \~2-4x case-insensitive. The metadata checks out: MIT, 49 stars, not a fork, not archived, last commit on main 2019-04-16, used in APT.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/julian-klode/triehash>
  - <https://github.com/julian-klode/triehash#performance>
  - <https://github.com/julian-klode/triehash/blob/main/LICENSE.md>
  - <https://github.com/julian-klode/triehash/blob/main/.travis.yml>
  - <https://github.com/julian-klode/triehash/tree/main/tests>
  - <https://github.com/julian-klode/triehash/tree/prefix>
  - <https://github.com/julian-klode/triehash/tree/debian/master>
  - <https://github.com/julian-klode/triehash/commit/e4acd52a>
  - <https://github.com/julian-klode/triehash/commit/81a66472>
  - <https://jak-linux.org/projects/triehash/>
  - <https://blog.jak-linux.org/2016/09/25/introducing-triehash-a-order-preserving-minimal-perfect-hash-function-generator-for-c/>
  - <https://github.com/julian-klode/hashbench>
  - <https://github.com/julian-klode/hashbench/blob/master/Makefile>
  - <https://github.com/julian-klode/hashbench/blob/master/bench-runner.c>
  - <https://github.com/julian-klode/hashbench/blob/master/bench-hashes.c>
  - <https://github.com/julian-klode/hashbench/blob/master/render-results.py>
  - <https://github.com/julian-klode/hashbench/blob/master/wordlist>
  - <https://github.com/Debian/apt>
  - <https://github.com/Debian/apt/blob/main/apt-pkg/CMakeLists.txt>
  - <https://github.com/Debian/apt/blob/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/julian-klode/triehash>
  - <https://github.com/julian-klode/triehash#performance>
  - <https://github.com/julian-klode/triehash/blob/main/triehash.pl>
  - <https://github.com/julian-klode/triehash/blob/main/.travis.yml>
  - <https://github.com/julian-klode/triehash/blob/main/tests/run-tests.sh>
  - <https://github.com/julian-klode/triehash/blob/main/tests/framework.sh>
  - <https://github.com/julian-klode/triehash/blob/main/tests/test-basic>
  - <https://github.com/julian-klode/triehash/blob/main/tests/test-case-insensitive>
  - <https://github.com/julian-klode/triehash/blob/main/tests/test-enum-include-name-flags>
  - <https://github.com/julian-klode/triehash/blob/main/tests/test-multi-byte-level>
  - <https://github.com/julian-klode/triehash/issues?q=is%3Aissue>
  - <https://github.com/julian-klode/triehash/issues/3>
  - <https://github.com/julian-klode/triehash/issues/7>
  - <https://github.com/julian-klode/triehash/commits/main>
  - <https://github.com/julian-klode/triehash/branches>
  - <https://github.com/julian-klode/triehash/tags>
  - <https://github.com/julian-klode/triehash/compare/main...prefix>
  - <https://github.com/julian-klode/triehash/compare/main...debian/master>
  - <https://github.com/julian-klode/triehash/blob/debian/master/debian/control>
  - <https://blog.jak-linux.org/2016/09/25/introducing-triehash-a-order-preserving-minimal-perfect-hash-function-generator-for-c/>
  - <https://jak-linux.org/projects/triehash/>
  - <https://github.com/julian-klode/hashbench>
  - <https://github.com/julian-klode/hashbench/blob/master/Makefile>
  - <https://github.com/julian-klode/hashbench/blob/master/bench-runner.c>
  - <https://github.com/Debian/apt/blob/main/CMakeLists.txt>
  - <https://github.com/Debian/apt/blob/main/apt-pkg/CMakeLists.txt>
  - <https://github.com/Debian/apt/blob/main/apt-pkg/tagfile.cc>
  - <https://github.com/Debian/apt/blob/main/apt-pkg/tagfile-keys.list>
  - <https://github.com/Debian/apt/commits/main>
  - <https://github.com/strager/perfect-hash-tables>
  - <https://tracker.debian.org/pkg/triehash>
  - <https://gcc.gnu.org/bugzilla/show_bug.cgi?id=77729>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/julian-klode/triehash`) · [data/wave1-phf/enrich/raw/github_com_julian_klode_triehash.json](../../../data/wave1-phf/enrich/raw/github_com_julian_klode_triehash.json) (enrichment confidence 0.82)

</details>
