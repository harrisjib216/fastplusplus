# HHVM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `PHP-3.01 AND Zend-2.0 (core); MIT (Hack typechecker and Hack Standard Library)` · 🟢 active

> Meta's JIT virtual machine for Hack; reported 1.6x over the 2014-era Zend PHP interpreter on real applications.

| | |
|---|---|
| **Beats** | PHP reference interpreter (Zend Engine), 2014-era version per the OOPSLA 2014 paper (version not seen); HPHPc as a second comparison |
| **Claimed result** | Snippet only (OOPSLA 2014 paper 'The HipHop Virtual Machine', Adams et al., not opened): 'in sandbox mode HHVM attains a 1.6x speedup over PHP when running real-world applications' (HPHPc could not run these applications; HHVM could not run Drupal); on the paper's benchmark suite HHVM reaches a geometric mean speedup of 2.64x in sandbox mode and 2.79x in production mode, compared to HPHPc's 1.93x (the snippet does not name the base of these ratios). The README itself only says HHVM 'uses a just-in-time (JIT) compilation approach to achieve superior performance'. |
| **Workload** | Server-side Hack (formerly PHP) programs executed by a JIT virtual machine. |
| **Metric** | throughput |
| **Adoption** | 18.7k stars; runs Meta's web tier |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/facebook/hhvm) · [benchmark](https://dl.acm.org/doi/10.1145/2660193.2660199) |

## Verdict

No numbers exist in the repo; the claim rests on search snippets of the peer-reviewed but first-party OOPSLA 2014 paper: HHVM about 1.6x faster than the PHP (Zend) interpreter of that time on real-world applications in sandbox mode, and 2.64x (sandbox) and 2.79x (production) geometric-mean speedups on its benchmark suite against 1.93x for the earlier HPHPc static compiler; PHP version, hardware and flags were not visible. A later first-party figure (PLDI 2018, snippet) is a 21.7% gain on the Facebook website from the region-based PGO JIT over HHVM's earlier tracelet JIT.

## Use it when

- You write Hack (or are migrating a large PHP 5-era codebase into Hack) and want a JIT VM tuned for a long-running, request-oriented web tier like Meta's.
- Large server-side codebases where a repo-authoritative (whole-program, pre-compiled bytecode) deployment and profile-guided warm-up are acceptable.
- Studying a production dynamic-language JIT: the hackers-guide docs and the region-based PGO design (PLDI 2018) are a good reference for type-specializing JITs.
- x86-64 servers with AVX2-class CPUs (the build uses -march=x86-64-v3) or aarch64 Linux.

## Skip it when

- Running PHP: the 3.30 series was the last that aimed for PHP compatibility and HHVM 4.0 (2019) is Hack-only (search snippets of hhvm.com and Phoronix; the pages were blocked here); for PHP use php-src with opcache JIT, the catalogued PHP JIT sibling.
- You need packaged, versioned releases: the GitHub repo has no tags after HHVM-4.172.3 and HHVM-4.168.4 (both 2023-05-02) even though master gets commits daily, so current code means building from source (the hackers guide warns the first build can take an hour or more).
- Short-lived CLI scripts or small sites: the JIT relies on profiling then retranslation, so warm-up matters; startup and memory cost are not documented in the repo.
- Pre-Haswell x86-64 CPUs, 32-bit systems, or PIE-only environments: CMake forces -march=x86-64-v3, refuses non-64-bit builds and links with -no-pie.
- Licence-sensitive redistribution: the core is PHP-3.01 plus Zend-2.0 (not OSI-approved); only the Hack typechecker and HSL are MIT.

## How it is fast

A type-specializing JIT: it observes the runtime types flowing through bytecode, emits machine code specialized for them and guards the assumptions with type checks. Code is first compiled as small 'tracelet' profiling regions, then retranslated with profile-guided optimization into large 'hot CFG' regions that can cover whole functions with loops. Regions are lowered HHBC to HHIR (SSA IR with a rich type lattice, guard relaxation, simplification, dead-code elimination) to vasm (low-level IR with its own register allocator) and then to x86-64 or arm64 code; HHBBC whole-program type inference in repo-authoritative mode removes more checks ahead of time.

## Compared with alternatives

Pick HHVM only for Hack code; for PHP the php-src opcache JIT (catalogued at about 2.6x-9.5x faster than plain PHP 8.2 on kostya/jit-benchmarks numeric kernels, derived from its sibling summary) and JPHP (claims about 13% slower than PHP 7.4) are the relevant siblings, and current HHVM cannot run PHP at all. Compared with Meta's other catalogued JIT, Cinder (CPython), HHVM is the far more mature, production-proven design but locks you into the Hack language.

## Integration

| | |
|---|---|
| **Form** | standalone VM binary with built-in web server (not a library) |
| **Dependencies** | large: folly, fizz, wangle, mvfst, proxygen, fbthrift, mcrouter, Boost, OpenSSL, ICU, PCRE, RE2, libevent, libxml2, libsodium, libdwarf, libelf, libunwind, TBB, oniguruma and others (CMake/HPHPFindLibs.cmake, third-party/); OCaml via opam/dune and Rust/Cargo for the Hack frontend |
| **Minimum toolchain** | C++20 (CMakeLists.txt), CMake 3.18+, GCC or Clang; hackc crate uses Rust edition 2024 (so Rust 1.85 or newer) |
| **Platforms** | 64-bit Linux on x86-64 (built with -march=x86-64-v3) and aarch64; macOS has CMake handling (deployment target 10.15) but support level is not documented here |
| **Thread safety** | multi-threaded server; each request runs in its own request context, and process-wide state such as setlocale() leaks across requests (hphp/doc/limitations) |
| **Drop-in for the baseline** | no |

## Gotchas

- The only speed numbers are first-party and snippet-only: the OOPSLA 2014 paper (1.6x over PHP on real-world apps in sandbox mode; 2.64x and 2.79x geomean on its benchmark suite vs HPHPc's 1.93x) and the PLDI 2018 JIT paper (21.7% faster on the Facebook website than the previous tracelet-based HHVM JIT, per a review snippet); neither paper was opened here, and the repo carries no benchmark.
- The PHP baseline is obsolete: it is the 2014-era Zend interpreter, before PHP 7 rewrote the engine and PHP 8 added a JIT, and current HHVM no longer runs PHP, so no current like-for-like comparison exists. Meta's own oss-performance harness (hhvm/oss-performance: WordPress, Drupal, MediaWiki and others on PHP 5, PHP 7 and HHVM) was archived on 2022-01-13 with the README saying it had no results to share.
- In-repo docs are partly stale: hphp/doc/hackers-guide says HHVM is written in C++14 and that PHP is 'currently supported for historical reasons', while CMakeLists.txt requires C++20 and PHP support ended in 2019; jit-core.md still lists a ppc64 backend, but the CMake files only detect x86_64 and aarch64.
- Type guards multiply: without guard relaxation, a translation with 4 guards can need up to 10^4 retranslations that chain linearly (jit-optimizations.md), so highly polymorphic code can fall off the fast path.

## Known shortcomings

- Raised D to C on the OOPSLA 2014 abstract (1.6x over PHP on real-world apps in sandbox mode), snippet only since the paper is blocked; the baseline is 2014 PHP and current HHVM runs Hack only. Zend-2.0 licence is not OSI-approved, so usability is mixed. Off-baseline.
- Enricher: no benchmark in the repo; all numbers are search snippets (OOPSLA 2014 1.6x over 2014 Zend, PLDI 2018 21.7% over the old tracelet JIT on facebook.com); Hack-only since 4.0 (2019), no GitHub tags since HHVM-4.172.3 (2023-05-02), x86 builds force -march=x86-64-v3, the hackers-guide docs are stale, and the hhvm/oss-performance harness was archived 2022-01-13 with no results.

## Caveats and trade-offs

Numbers are from search snippets of the OOPSLA 2014 paper (dl.acm.org and the SPLASH page are blocked here); PHP version, hardware and flags unverified. The comparison is against 2014-era PHP; PHP 7 and later changed the interpreter substantially, and the current README describes HHVM as a VM for programs written in Hack, so a Zend-PHP baseline no longer matches what current HHVM runs. Authors are Meta engineers (first-party, peer-reviewed). The Zend-2.0 licence part is not OSI-approved, hence usability mixed. Baseline is not one of PyPy, LuaJIT, V8, HotSpot.

Runs Hack (and, historically, PHP 5/7 code) only; HHVM now targets Hack and PHP support was dropped in later releases (not verified on the pages opened), so any PHP comparison is historical; needs a webserver such as Proxygen or FastCGI.

## Maintenance

Very actively developed (commits on 2026-10-06) as Meta's production Hack runtime, but with no GitHub release tags since May 2023, a heavyweight from-source build and a mixed PHP/Zend licence, it is practical only for teams committed to Hack.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now C.
- **Tier reason:** The repo page has no numbers (record's D was right for that page), but the peer-reviewed OOPSLA 2014 paper 'The HipHop Virtual Machine' by Meta engineers reports, per search snippets of its abstract and ACM PDF, a 1.6x speedup over PHP on real-world applications in sandbox mode; the paper (dl.acm.org) is blocked, so snippet-only numbers cap this at C. A paper-access retier could raise it to B.
- **Verifier notes:** Kept and raised D to C on paper-snippet numbers (1.6x over PHP on real-world apps, sandbox mode); paper not opened. Shortcomings: README has no numbers, evidence is a 2014 paper against PHP 5-era Zend, current HHVM runs Hack only per its README, Zend-2.0 licence non-OSI. Metadata checked: 18.7k stars, PHP-3.01 and Zend-2.0 core plus MIT Hack typechecker and HSL, last commit 2026-10-06.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/LICENSE.PHP>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/LICENSE.ZEND>
  - <https://github.com/facebook/hhvm>
  - <https://github.com/facebook/hhvm/commits/master>
  - <https://github.com/facebook/hhvm/tree/master/hphp/doc>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/LICENSE.PHP>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/CMake/HPHPCompiler.cmake>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/CMake/HPHPFindLibs.cmake>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/CMake/HHVMProject.cmake>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/third-party/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/hphp/hack/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/hphp/hack/src/hackc/Cargo.toml>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/hphp/doc/limitations>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/hphp/doc/threading>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/hphp/doc/hackers-guide/README.md>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/hphp/doc/hackers-guide/jit-core.md>
  - <https://raw.githubusercontent.com/facebook/hhvm/HEAD/hphp/doc/hackers-guide/jit-optimizations.md>
  - <https://github.com/facebook/hhvm>
  - <https://github.com/facebook/hhvm/commits/master>
  - <https://github.com/facebook/hhvm/tags>
  - <https://github.com/facebook/hhvm/tree/master/hphp/doc>
  - <https://github.com/hhvm/oss-performance>
  - https://hhvm.com/blog/2018/09/12/end-of-php-support-future-of-hack.html (EGRESS_BLOCKED; WebSearch snippet only)
  - https://research.facebook.com/publications/hhvm-jit-a-profile-guided-region-based-compiler-for-php-and-hack/ (EGRESS_BLOCKED; WebSearch snippet only)
  - https://dl.acm.org/doi/10.1145/2660193.2660199 (not opened; WebSearch snippet only)
  - https://blog.acolyer.org/2018/08/08/hhvm-jit-a-profile-guided-region-based-compiler-for-php-and-hack/ (not opened; WebSearch snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/facebook/hhvm`) · [data/wave12/enrich/raw/github_com_facebook_hhvm.json](../../../data/wave12/enrich/raw/github_com_facebook_hhvm.json) (enrichment confidence 0.6)

</details>
