# KPHP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> VK's ahead-of-time compiler from strictly typed PHP to C++; first-party 5-7x over PHP 7.4 on Zend benchmarks.

| | |
|---|---|
| **Beats** | PHP 7.4 with OpCache (Zend micro_bench.php and bench.php); PHP 7.2 for the vk.com page timings |
| **Claimed result** | micro_bench avg 3.297 s on PHP 7.4 vs 0.460 s on KPHP; bench avg 0.659 s vs 0.119 s ('KPHP is found to be 5-7 times faster'); vk.com/feed 10.1 s vs 0.95 s, vk.com/im 1.25 s vs 0.46 s, vk.com/ads 0.73 s vs 0.20 s (PHP 7.2); neural networks with huge matrices \~8 s vs 0.24 s; deep decision trees \~5 s vs 0.14 s; README: 'when your code fits best practices, it runs 3-10 times faster than PHP'. Companion walk-through page (docs/various-topics/walk-through-php-kphp-cpp.md, quicksort of an int array): PHP 7.4 \~2100 ms vs KPHP \~480 ms (\~4x); with the array_swap_int_keys built-in and no wrapper call, PHP 7.4 \~1950 ms vs KPHP \~270 ms (\~7x); hand-written C++ with g++ -Os \~220 ms. |
| **Workload** | php-src Zend/micro_bench.php and Zend/bench.php (after removing a couple of tests that do not compile), 5 runs each; plus vk.com page generation times and ML-style kernels measured by the authors. |
| **Metric** | throughput |
| **Compiler and flags** | g++ on the generated C++ with kphp2cpp.cpp defaults -O2 -ggdb -fsigned-char and -march=sandybridge (the docs' -Os is outdated); PHP 7.4/7.2 baselines without opcache JIT; compiler version and CPU unstated |
| **Adoption** | 1.5k stars; production compiler at VK.com |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/VKCOM/kphp) · [benchmark](https://raw.githubusercontent.com/VKCOM/kphp/master/docs/kphp-language/kphp-vs-php/benchmarks.md) |

## Verdict

First-party docs only: on php-src Zend micro_bench.php and bench.php (with a couple of tests removed and errors fixed, scripts not published), five runs each, PHP 7.4 with OpCache and no JIT averaged 3.297 s and 0.659 s vs KPHP 0.460 s and 0.119 s (about 7.2x and 5.5x, derived from page data), with no CPU, KPHP version or compiler stated. A quicksort walk-through reports \~2100 vs \~480 ms (\~4x) and \~1950 vs \~270 ms after KPHP-specific tuning, and vk.com page timings vs PHP 7.2 show 2.7-10.6x.

## Use it when

- Large PHP code bases with CPU-bound business logic that can be kept strictly typed and deployed as a Linux service; VK reports 2.7-10.6x faster page generation than PHP 7.2 (vk.com/feed 10.1 s vs 0.95 s).
- Numeric or ML-style kernels over typed arrays: VK reports neural-network code at \~8 s vs 0.24 s and deep decision trees at \~5 s vs 0.14 s against PHP.
- PHP-style code that calls C libraries heavily: KPHP's FFI passes internal pointers and skips CData casts, and with critical sections disabled approaches native call speed.
- Teams that want whole-program compile errors and type, immutability and checked-exception checks before deploy, while still developing and testing on stock PHP.
- Embedding PHP-subset business logic into a C++ program through lib mode (static library and header).

## Skip it when

- Existing code that relies on eval, reflection, dynamic names, generators, anonymous classes, finally, func_get_args, general references, SPL, XML/DOM, \$_SESSION, image functions, file upload, Postgres/Redis clients or PHP extensions: none of these are supported, and the README warns existing code rarely compiles without rewriting.
- Code dominated by built-in C functions such as strpos or parse_url: the benchmarks page itself says KPHP gains almost nothing there.
- Allocation- and object-tree-heavy code: issue #541 (open since 2022-06-22, no maintainer reply) reports benchmarks-game binarytrees at 6.34 s user time on KPHP vs 1.94 s for PHP without JIT and 1.27 s with JIT.
- Comparisons against modern PHP: every number is against PHP 7.4 or 7.2 without the opcache JIT (PHP 8.0+); the catalogue's php-src entry shows that JIT alone gives 2-9.5x on numeric kernels without any rewrite, so the remaining gap over PHP 8.x is not measured.
- Windows hosts (Docker only) or systems without apt: deb packages are amd64-only for Ubuntu 20.04/22.04 and Debian 10/11, macOS needs a source build, and source builds have open failure reports (issue #1057, link error, open since 2024-08-05).

## How it is fast

Whole-program type inference replaces PHP's dynamic zvals with concrete C++ types (ints, floats, strings, typed vectors), so arithmetic and array access compile to native code. All symbols are resolved at compile time: constants are inlined, getters and setters are inlined, class fields are fixed memory offsets instead of hashtable lookups, access modifiers vanish at runtime, and refcount flapping is reduced; the runtime adds constant-array pre-initialization and script allocators. The generated C++ is then built by g++ or clang (current default -O2); the gain largely disappears when types degrade to mixed.

## Compared with alternatives

KPHP is the PHP counterpart of Codon, Shed Skin and mypyc (ahead-of-time compilers for a typed subset): pick it when the code base is PHP and you can accept rewriting to its typed subset for a 3-10x first-party gain. For unmodified PHP, PHP's own opcache JIT (php-src in this catalogue) needs no rewrite and on issue #541's binarytrees was faster than KPHP.

## Integration

| | |
|---|---|
| **Form** | compiler (PHP to C++ translator plus runtime library) producing a server or CLI binary, or a static lib plus header in lib mode |
| **Dependencies** | A C++ compiler at compile time (--cxx / KPHP_CXX); install via the vkcom/kphp Docker image or the kphp and vk-tl-tools deb packages from VK's artifactory; php7.4/8.x-vkext for developing on PHP; CMake 3.16+ for source builds |
| **Minimum toolchain** | KPHP itself: C++17 with gcc 8.3+ or clang 10+; the k2 light runtime: C++23 with gcc 10.1+ or clang 14+. Generated code is compiled with the same -std as the KPHP build. |
| **Platforms** | Linux x86-64 (generated code built with -march=sandybridge) and aarch64 (-march=armv8.2-a+crypto); macOS from source; no native Windows |
| **Thread safety** | Not documented as a threading model for user code; PHP code keeps single-threaded semantics, concurrency comes from the embedded server's process orchestration and KPHP coroutines (forks), and data shared across requests uses a dedicated shared-memory API. |
| **Drop-in for the baseline** | partial: compiles PHP source, but only a strictly typed subset without eval, reflection, generators, SPL or extensions; existing code usually needs rewriting, and a few behaviours differ (64-bit wrapping integer overflow, typed arrays returning non-null for missing keys) |

## Gotchas

- Build flags have changed since the docs were written: kphp2cpp.cpp now defaults the generated code's flags to '-O2 -ggdb -fsigned-char', and compiler-settings.cpp adds -fwrapv -fno-strict-aliasing -fno-omit-frame-pointer and -march=sandybridge on x86-64, while the walk-through still says KPHP builds with -Os. The doc's C++ comparison (-Os) and timings therefore do not describe current builds, and binaries will not run on x86-64 CPUs without AVX.
- Harness: the walk-through's \~7x step (PHP \~1950 ms vs KPHP \~270 ms) gives KPHP its native array_swap_int_keys built-in while PHP runs a userland polyfill with two isset checks per swap (PHP slowed from \~2100 to \~2650 ms when switched to it), PHP is never given an inlined swap, and the input comes from unseeded rand(); the Zend runs used locally modified scripts that are not published, on unstated hardware.
- Types that degrade to mixed erase most of the gain: the same quicksort fell from \~270 ms to \~940 ms once \$argv made the array mixed[], and object field access pays null checks because nullability is not tracked.
- Semantics differ from PHP in edge cases: integer overflow wraps as native 64-bit (compiled with -fwrapv) instead of becoming float, bitwise operators assume integers, and invalid-argument behaviour of standard functions differs.

## Known shortcomings

- benchmarks.md has no CPU model, the modified Zend scripts are not published, and the baseline is PHP 7.4/7.2 without the PHP 8 JIT; the vk.com and ML timings are not reproducible, and only a restricted typed PHP subset compiles (g++ -Os). Off-baseline: PHP, not CPython, Lua, MRI or V8.
- Enricher: kphp2cpp.cpp's default generated-code flags are now '-O2 -ggdb -fsigned-char' plus -march=sandybridge rather than the -Os the docs state; the walk-through's about 7x gives KPHP a native array_swap_int_keys while PHP runs a userland polyfill, with unseeded rand(). Open counterexample issue #541: binarytrees KPHP 6.34 s vs PHP 1.94 s without JIT and 1.27 s with JIT, no reply.

## Caveats and trade-offs

First-party numbers with no CPU model or KPHP/compiler version. The Zend micro_bench.php and bench.php had a couple of tests removed and errors corrected before running, and the modified scripts are not published. The doc itself calls the Zend comparison 'absolutely synthetic' and warns it is wrong to say KPHP is always faster (code dominated by C-implemented PHP functions such as strpos or parse_url gains almost nothing). The walk-through shows KPHP dropping to \~940 ms when types degrade to mixed[], and hand-written C++ still about 2x faster than plain KPHP. Baseline is PHP 7.4/7.2, without the PHP 8 JIT, so today's gap is probably smaller. vk.com page timings and ML kernels are not reproducible from public code. KPHP only compiles a restricted, strictly typed PHP subset (no generators, anonymous classes, SPL or XML), so existing code usually needs rewriting. The project website is on github.io (blocked here); pages were read from the repo's docs/ directory. [retier] benchmarks.md has no CPU model, the modified Zend scripts are unpublished and the baseline is PHP 7.4/7.2 without the PHP 8 JIT; the vk.com and ML timings are not reproducible, and only a restricted typed PHP subset compiles. The quicksort walk-through (about 7x) gives KPHP a native array_swap_int_keys while PHP runs a userland polyfill, with unseeded rand(). Open issue #541: binarytrees takes 6.34 s on KPHP against 1.94 s on PHP without JIT and 1.27 s with JIT. Off-baseline (PHP).

Ahead-of-time compiler from a limited, strictly typed PHP subset to C++ and then a native binary; no generators, anonymous classes, SPL or XML parsing, no call-by-name; existing PHP code usually needs rewriting to compile; the runtime is C++ and has a fast FFI.

## Maintenance

Active (last commit 2026-09-25; recent work is mostly the new k2 light runtime) and usable via Docker or amd64 deb packages, but GPL-3.0 with no linking exception in LICENSE, so distributed binaries that link the runtime carry GPL obligations.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party docs page (docs/kphp-language/kphp-vs-php/benchmarks.md) gives per-run Zend micro_bench/bench timings against PHP 7.4 with OpCache plus vk.com page and ML-kernel timings, but no CPU model, no compiler version, and the modified Zend scripts are not published; vk.com and ML timings are not reproducible. First-party with partial methodology is C.
- **Verifier notes:** Every quoted number matches the benchmarks.md page; added the walk-through quicksort numbers and the -Os build flag the docs mention. Metadata confirmed: GPL-3.0, about 1.5k stars, not archived, not a fork, last commit 2026-09-25 (active). Tier C stays.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/docs/kphp-language/kphp-vs-php/benchmarks.md>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/README.md>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/docs/various-topics/walk-through-php-kphp-cpp.md>
  - <https://github.com/VKCOM/kphp>
  - <https://github.com/VKCOM/kphp/commits>
- **Sources the enricher read:**
  - <https://github.com/VKCOM/kphp>
  - <https://github.com/VKCOM/kphp/commits/master>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/README.md>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/LICENSE>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/cmake/init-compilation-flags.cmake>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/compiler/compiler-settings.cpp>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/compiler/kphp2cpp.cpp>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/docs/kphp-language/kphp-vs-php/benchmarks.md>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/docs/various-topics/walk-through-php-kphp-cpp.md>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/docs/kphp-language/kphp-vs-php/kphp-vs-php-differences.md>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/docs/kphp-basics/installation.md>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/docs/kphp-basics/compile-existing-project.md>
  - <https://raw.githubusercontent.com/VKCOM/kphp/master/docs/kphp-basics/faq.md>
  - <https://github.com/VKCOM/kphp/issues?q=is%3Aissue+performance>
  - <https://github.com/VKCOM/kphp/issues/541>
  - <https://github.com/VKCOM/kphp/issues/1057>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/vkcom/kphp`) · [data/wave12/enrich/raw/github_com_vkcom_kphp.json](../../../data/wave12/enrich/raw/github_com_vkcom_kphp.json) (enrichment confidence 0.75)

</details>
