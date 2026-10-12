# cperl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-1.0-or-later OR Artistic-1.0-Perl` · 🔴 abandoned

> Diverged Perl 5 fork with types, faster signatures and FNV1a hashing; about 6% faster than perl 5.30.0 on PerlBench.

| | |
|---|---|
| **Beats** | perl5 releases 5.6.2 to 5.30.0 on the same machine (PerlBench); the README names 'perl5' and 5.14 |
| **Claimed result** | README: 'about 15%x faster than perl5 overall, more than 2x faster then 5.14' and the least memory measured since 5.6; the STATUS page says 'about 20% faster than perl5 overall'. Neither links a measurement. The project's own PerlBench run (2019-06-14, 41 micro-tests, 5.6.2 = 100, higher is better) gives Average 142.9 for cperl 5.30.0c vs 134.8 for perl 5.30.0 (about 1.06x, derived from page data; cperl wins 26 of 41 tests) and 114.6 vs 102.6 at 5.22 (about 1.12x), but cperl is equal or slower at 5.24 (125.5 vs 127.0), 5.26 (132.4 vs 131.9) and 5.28 (134.7 vs 136.9). Against perl 5.14 (101.9) cperl 5.30 is about 1.40x, not 2x (derived from page data). |
| **Workload** | PerlBench micro-benchmark suite (41 tests: arith, array, call, hash, loop, re, startup, string), scores relative to perl 5.6.2 = 100 |
| **Metric** | throughput |
| **Hardware** | Linux x86_64 machine ('reini'), Debian kernel 4.19.0-5-amd64; CPU model not stated |
| **Compiler and flags** | cperl 5.30c: pre-release dev build (smoke/relprep b745599, -Dusedevel), BOLT-configured (x86_64-linux-bolt, -Wl,-q, llvm-bolt), clang -O3 -march=native thin LTO, no -fwrapv; perl5 5.30.0: gcc 8.3 -O2; 5.14 built -O1 -g (CONFIG-5.30c.txt and the PerlBench page) |
| **Adoption** | 144 stars |
| **Last commit** | 2022-07-29 |
| **Links** | [repository](https://github.com/perl11/cperl) · [benchmark](https://github.com/perl11/perl11.github.io/blob/master/cperl/bench-all/index.html) |

## Verdict

In the project's own PerlBench page (one run on 2019-06-14, 41 micro-tests, Linux x86_64 host 'reini' on Debian kernel 4.19.0-5, CPU model not stated, scores relative to perl 5.6.2 = 100), cperl 5.30.0c averages 142.9 vs perl 5.30.0's 134.8: a 1.06x geomean, faster on 26 tests, slower on 13, tied on 2 (derived from page data). cperl was a BOLT-configured clang -O3 -march=native LTO dev build, while perl5 was gcc 8.3 -O2. At 5.24, 5.26 and 5.28 cperl scored 0.99x, 1.00x and 0.98x of perl5.

## Use it when

- A legacy code base pinned to Perl 5.22-5.30 that can swap interpreters and wants small gains on hash- and string-heavy code: at 5.30, cperl's per-test ratios are hash/get 1.29x, string/base64 1.29x, array/copy 1.26x, string/htmlparser 1.25x and re/w 1.21x.
- Perl 5.22 deployments: 5.22.5c vs perl 5.22.4 is the release pair with the clearest gain (1.12x geomean, 27 of 41 tests faster, regex group 1.59x).
- Code that already uses typed signatures or coretypes and accepts cperl's semantics (for example an empty @_ in subs with signatures).
- As a reference for interpreter techniques (type-specialised ops, unchecked array access in counted loops, signature binding without @_) to port into another VM.

## Skip it when

- Any new or security-sensitive deployment: the repository has been archived read-only since 2023-06-01, the last commit is from 2022-07-29 and the last release 5.30.0c from 2019-07-06, so it misses every perl5 fix and feature after 5.30.
- Code dominated by sub calls: at 5.30, cperl is slower than perl5 on call/1arg (0.82x), call/0arg (0.85x) and call/empty (0.87x), and the arith group is 0.96x.
- If you need a gain that holds across releases: cperl 5.24.4c, 5.26.5c and 5.28.2c score 0.99x, 1.00x and 0.98x of the matching perl5 releases in the same run, despite their -O3/-march=native builds.
- Workloads that need CPAN modules without cperl patches (autovivification, TryCatch and Catalyst::Runtime are listed for 5.28.0c), the -d debugger with signatures (documented as mostly broken), or Test2.
- Untrusted hash keys where you want a keyed hash: the default is unkeyed FNV1a with move-to-front chains, and flood protection relies on collision handling and security warnings; open issue #115 reports restricted Storable hashes broken under the PERL_PERTURB_KEYS_TOP strategy.

## How it is fast

Signatures bind arguments straight from the stack without also filling @_ (documented as 2x faster calls), and subs with a `my (...) = @_;` prologue are promoted to signatures automatically. Ops get type-specialised variants for arithmetic, padsv and sassign, constant subs are inlined without an empty prototype, static method calls are turned into plain function calls, and `for (0..$#a)` loops use an unchecked element op with no bounds check. Hashes default to FNV1a with move-to-front collision chains and a 90% fill rate, and strict, attributes, DynaLoader, XSLoader and Config are rewritten in C/XS to cut startup. The benchmarked builds also used clang -O3 -march=native with thin LTO.

## Compared with alternatives

No other Perl implementation is among the catalogued siblings. Next to PyPy (about 6.5x over CPython on kostya bench.b) or YJIT (about 2x over the CRuby interpreter), cperl's gain over its own baseline is small and varies by release, so pick it only when you must stay on Perl 5.22-5.30 semantics and want a CPAN-compatible interpreter with types and signatures.

## Integration

| | |
|---|---|
| **Form** | interpreter binary built from source (static libperl.a in the benchmarked builds); prebuilt el6/el7, Debian sid, macOS and Windows packages were published on perl11.github.io |
| **Dependencies** | A C compiler and the perl5 Configure toolchain; libffi for the builtin FFI (the 5.30c build links -lffi) |
| **Minimum toolchain** | Not documented; the benchmarked builds used gcc 7.2.0/8.2.0/8.3.0 and clang 7.0.1 |
| **Platforms** | Developed and tested on 64-bit Linux and darwin; Windows smoked with mingw, cygwin and MSVC 10/12 (32- and 64-bit); BSDs and Solaris tested only before releases (STATUS page) |
| **Thread safety** | Same interpreter model as perl5; every benchmarked build was non-threaded (-Uuseithreads), and perlcperl.pod calls native threads 'not fixable', favouring Coro |
| **Drop-in for the baseline** | partial — runs most perl5 code, but @_ is empty in subs with signatures, illegal prototypes die, base @ISA and Config are read-only, core modules such as Test::More are stricter about types, and some CPAN modules need distroprefs patches |

## Gotchas

- Harness confound behind the 1.06x: the CONFIG-5.30c.txt recorded for the benchmarked cperl binary shows a pre-release development build (git_branch=smoke/relprep, commit b745599 'cperl-5.29.2-464', -Dusedevel), not the 5.30.0c tag released three weeks later. It was configured for BOLT post-link optimisation (archname x86_64-linux-bolt@b745599, perlpath cperl5.30.0-nt-bolt, llvm-ar from an llvm-bolt build tree, -Wl,-q to keep relocations) and built with clang 7 -O3 -g -march=native thin LTO, without -fwrapv and with -fstack-protector. perl 5.30.0 was built with gcc 8.3 -O2, -fwrapv and -fstack-protector-strong. The gap therefore mixes toolchain and flags with source changes; cperl 5.28.2c, configured the same way, was 0.98x of perl 5.28.2.
- Single PerlBench run (2019-06-14) with no repetitions or error bars. Some of the 5.30 wins come from a perl5 regression rather than cperl gains: perl5 hash/get fell from 146 (5.28) to 107 (5.30) while cperl stayed at 129-138, which yields the 1.29x on that test.
- The README's 'about 15%x faster than perl5 overall' and the STATUS page's '20%' and '&gt;2x faster than 5.14' have no supporting run. The same page gives 1.40x over perl 5.14 (geomean of the 41 tests), and that baseline was a -O1 -g build (path perl5.14.4-nt@g).
- Behaviour differs from perl5: @_ is not populated in subs with signatures, Test::More::skip arguments are type-checked at compile time, use base @ISA is read-only, and a plain `my (...) = @_;` prologue may be rewritten into a signature.

## Known shortcomings

- Downgraded claim: the README's '15% faster, 2x vs 5.14' is unbacked; cperl's own PerlBench page (perl11.github.io cperl/bench-all, 2019) shows 5.30c at 142.9 vs perl 5.30 at 134.8 (about 1.06x), slower or equal at 5.24, 5.26 and 5.28, and 1.40x over 5.14 rather than 2x, with confounded builds (cperl clang -O3 LTO -march=native vs perl5 gcc -O2; 5.14 built -O1 -g) and no CPU model. Archived; off-baseline (perl5).
- Enricher: CONFIG-5.30c.txt shows the benchmarked binary is a pre-release dev build (smoke/relprep b745599, -Dusedevel), BOLT-configured (archname x86_64-linux-bolt, -Wl,-q, llvm-bolt toolchain) with clang -O3 -march=native thin LTO and no -fwrapv, against perl5 5.30.0 built gcc 8.3 -O2; the 1.06x is also partly a perl5 5.30 hash/get regression (146 to 107); a single run with no variance data; call tests 0.82-0.87x.

## Caveats and trade-offs

The README's 15% (and the STATUS page's 20%) and '2x faster than 5.14' have no benchmark behind them; the project's own PerlBench page shows about 6% over perl 5.30.0 and cperl slower than or equal to perl5 at 5.24, 5.26 and 5.28. The comparison is confounded: cperl builds used -O3, -march=native and (5.28c/5.30c) clang thin LTO, while perl5 builds used gcc -O2 without -march, and the 5.14 baseline was built at -O1 -g. No CPU model. Archived read-only on 2023-06-01, last commit 2022-07-29; based on old perl5 releases, so it lags current perl5. [retier] The README's '15% faster, 2x vs 5.14' is unbacked; the 2019 PerlBench page gives 5.30c at 142.9 vs perl 5.30 at 134.8 (about 1.06x, partly a perl5 5.30 hash/get regression from 146 to 107), slower or equal at 5.24, 5.26 and 5.28, 1.40x over 5.14 rather than 2x, call tests 0.82-0.87x; a single run with no variance data and no CPU model, with the cperl binary a BOLT-configured clang -O3 -march=native LTO dev build against gcc -O2 perl5. Archived; off-baseline (perl5).

Diverged fork of perl5 adding types, classes, native compilation hooks and security hardening while keeping CPAN compatibility; not a drop-in for every perl5 release.

## Maintenance

Abandoned: archived read-only on 2023-06-01, last commit 2022-07-29, last release 5.30.0c (2019-07-06); GPL-1.0+ or Artistic licensed, so it is usable as a source of interpreter-optimisation ideas, not as a supported Perl.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification C, tier now C.
- **Tier reason:** The repo README carries the '15%x faster than perl5 overall, more than 2x faster then 5.14' sentence with no methodology; the project's own PerlBench page (perl11.github.io repo, cperl/bench-all/index.html, run 2019-06-14) gives per-build compilers and flags but no CPU model, and its numbers do not support the README claim, so first-party C with the claim corrected.
- **Verifier notes:** Downgrade of the claim, not the tier: the 15%/20%/2x figures are unsupported and the project's own PerlBench run shows about 1.06x over perl 5.30.0 (cperl 5.30.0c) with cperl slower at 5.24 and 5.28, and with cperl built at -O3/-march=native/LTO against perl5 at -O2. perl5 is not one of the category baselines (CPython, Lua, MRI, V8); category language-interpreters is right. The cperl STATUS and bench-all pages are on blocked perl11.github.io but readable from the perl11/perl11.github.io repo via raw.githubusercontent.com.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/perl11/cperl>
  - <https://github.com/perl11/cperl/commits>
  - <https://raw.githubusercontent.com/perl11/cperl/HEAD/README>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/STATUS.html>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/bench-all/index.html>
  - <https://github.com/perl11/perl11.github.io/blob/master/cperl/bench-all/index.html>
- **Sources the enricher read:**
  - <https://github.com/perl11/cperl>
  - <https://github.com/perl11/cperl/commits/master>
  - <https://github.com/perl11/cperl/releases>
  - <https://github.com/perl11/cperl/issues?q=is%3Aissue%20is%3Aopen%20label%3Abug>
  - <https://raw.githubusercontent.com/perl11/cperl/HEAD/README>
  - <https://raw.githubusercontent.com/perl11/cperl/HEAD/pod/perlcperl.pod>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/STATUS.html>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/index.html>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/bench-all/index.html>
  - <https://github.com/perl11/perl11.github.io/tree/master/cperl/bench-all>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/bench-all/CPU_FACTOR>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/bench-all/CONFIG-5.30.txt>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/bench-all/CONFIG-5.30c.txt>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/bench-all/CONFIG-5.28.txt>
  - <https://raw.githubusercontent.com/perl11/perl11.github.io/HEAD/cperl/bench-all/CONFIG-5.28c.txt>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/perl11/cperl`) · [data/wave12/enrich/raw/github_com_perl11_cperl.json](../../../data/wave12/enrich/raw/github_com_perl11_cperl.json) (enrichment confidence 0.8)

</details>
