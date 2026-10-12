# MyHTML

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1` · 🟡 stale

> Pure C99 HTML5 parser using a thread-pool tokenizer/tree-builder; beats Gumbo and html5ever on parse throughput.

| | |
|---|---|
| **Beats** | gumbo and html5ever (Rust, via html2html_lib C binding) |
| **Claimed result** | Ex vivo test over 466 Alexa Top-500 pages: MyHTML 0.50890s total vs Gumbo 6.12951s (\~12x) and HTML5Ever 4.50536s (\~8.9x); MyHTML Single Mode 0.72160s (\~8.5x vs Gumbo, \~6.2x vs HTML5Ever) (ratios derived from page data). The per-page CSV (Results/time/benchmark_0_100.csv) shows the same pattern, e.g. 163.com gumbo 0.05153s, html5ever 0.03694s, myhtml 0.00529s, myhtml_single 0.00845s. |
| **Workload** | 466 homepage HTML files from Alexa Top 500. The 'ex vivo' test parses all pages sequentially with one parser object; the 'in vivo' test forks per page (init, parse one page, free). MyHTML is tested threaded and in Single Mode against Gumbo and html5ever (via the html2html_lib C binding). Per-page timings are CSVs in Results/time/. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-3615QM @ 2.30GHz, 8 GB 1600 MHz DDR3, macOS (Darwin 15.3.0) |
| **Compiler and flags** | Apple LLVM 7.0.2 (clang-700.1.81); benchmark harness Makefile defaults to -O2; build flags for the myhtml, gumbo, and html5ever (Rust) libraries are not stated |
| **Adoption** | 1.7k stars; multiple language bindings (Perl, Crystal, Elixir, Swift) |
| **Last commit** | 2025-01-15 |
| **Links** | [repository](https://github.com/lexborisov/myhtml) · [benchmark](https://lexborisov.github.io/benchmark-html-parsers/) |

## Verdict

On the author's own 2016-era benchmark (466 Alexa Top-500 homepages parsed sequentially in one process, 'ex vivo'), threaded MyHTML totaled 0.509s vs Gumbo 6.130s (\~12x) and html5ever 4.505s (\~8.9x) on an Intel Core i7-3615QM / 8GB DDR3 Mac built with Apple LLVM 7.0.2 (clang-700.1.81); the harness Makefile default is only -O2 and library-specific build flags for myhtml, gumbo, and html5ever are unstated. MyHTML's Single Mode (single-threaded, the fairer comparison against the single-threaded baselines) totaled 0.722s, about 8.5x over Gumbo and 6.2x over html5ever.

## Use it when

- Bulk/offline HTML5 parsing where you can dedicate a thread pool per parser instance (e.g. batch crawling, corpus processing) and want the threaded mode's throughput
- C or C99 codebases that want a dependency-free, spec-conformant HTML5 tokenizer/tree builder without pulling in Rust or a GC runtime
- Existing consumers via the Perl, Crystal, Elixir/Erlang, or Swift bindings who need a fast HTML5 parse step without CSS selectors
- POSIX or Windows targets (source ports exist for both) where you don't need a selector engine and can build the library or vendor the source

## Skip it when

- New projects: the project's own README tells users to use the lexbor project instead, which is the maintained successor
- Anything needing CSS selectors or a renderer — MyHTML only builds the tree; you'd need Modest/lexbor on top
- Latency-sensitive single-page parsing on a resource-constrained host — thread-pool setup/teardown per page adds overhead unless you use Single Mode
- Code that touches token/attribute text from a different thread than the parser's workers without calling myhtml_token_node_wait_for_done first, since after-token-done callbacks fire on worker threads in the default threaded mode
- Projects wanting active upstream support: last commit 2025-01-15 and status is stale

## How it is fast

myhtml_init takes a thread_count and internally fans tokenization and tree construction out across a worker thread pool (thread_queue) backed by custom pool allocators (mcobject/mcsimple/mchar_async) instead of per-node malloc/free, so parsing one page overlaps tokenizing and tree-building work across cores. A single-threaded path (MyHTML_OPTIONS_PARSE_MODE_SINGLE, or building with MyCORE_BUILD_WITHOUT_THREADS=YES) exists for when thread overhead isn't worth it or POSIX threads aren't available.

## Compared with alternatives

Prefer lexbor (its own successor, already catalogued) for any new work — same author says so. MyHTML is only worth reaching for if you're maintaining an existing MyHTML integration or need one of its non-Rust/non-C bindings (Perl, Crystal, Elixir/Erlang, Swift) and don't need CSS selectors.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (pure C99; POSIX threads optional and can be disabled at build time) |
| **Minimum toolchain** | C99; GNU Make (or CMake) build; POSIX threads unless built with MyCORE_BUILD_WITHOUT_THREADS=YES |
| **Platforms** | POSIX (Linux/macOS/BSD) and Windows source ports (source/myport/posix, source/myport/windows_nt); benchmarked on macOS/x86-64 |
| **Thread safety** | Not a general guarantee — per api.h doc comments, in threaded mode (default) after-token-done and tree-node callbacks fire on worker threads, not the caller's thread, and callers must call myhtml_token_node_wait_for_done before reading attributes/text from another thread; single-threaded (MyHTML_OPTIONS_PARSE_MODE_SINGLE or no-threads build) runs all callbacks on the main thread |
| **Drop-in for the baseline** | partial — different API shape (separate myhtml_t/tree create+init steps, high/low-level C API, no CSS selectors) vs Gumbo's or html5ever's own APIs, so it is not a drop-in swap |

## Gotchas

- In default threaded mode, token/tree callbacks run on worker threads; reading node text/attributes from the caller thread without waiting (myhtml_token_node_wait_for_done) races with the parser
- No CSS selector engine — pair with Modest or lexbor if you need selectors or rendering
- The upstream README itself redirects new users to lexbor, the maintained successor already in this catalog
- Build flags used for the Gumbo/html5ever comparison binaries in the benchmark are not documented, so the exact magnitude of the speedup depends on how optimized those baselines were

## Caveats and trade-offs

The benchmark is by the MyHTML author and dates from 2016, so the gumbo and html5ever versions are old. The benchmark repo was renamed from benchmark-html-persers to benchmark-html-parsers. The default MyHTML run is multi-threaded while gumbo and html5ever are single-threaded; Single Mode is the fairer comparison (\~6-8.5x). Library build flags and the Rust build profile are not stated. The MyHTML README now tells users to use the Lexbor parser (lexbor/lexbor) instead.

Only builds an HTML5 tree (no CSS selector engine); threaded async parsing adds API complexity; project author now directs users to the successor lexbor project (already catalogued) for new work.

## Maintenance

Stale: last commit 2025-01-15, and the project's own README now directs users to the lexbor project instead; still LGPL-2.1 and small/dependency-free enough to vendor if you're stuck maintaining an existing integration.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Public benchmark code (lexborisov/benchmark-html-parsers, benchmark/) plus a results page stating the CPU (i7-3615QM) and compiler (Apple LLVM 7.0.2). Flags are only the harness Makefile default -O2. Build flags for the myhtml, gumbo, and Rust html5ever libraries are not stated, and the author is the same, so it is not A and stays C.
- **Verifier notes:** The record's CSV URL used the old repo name (it redirects). The linked results page has better aggregate numbers plus CPU and compiler, so I pointed benchmark_url there. Metadata checks out: LGPL-2.1, 1,718 stars, last commit 2025-01-15 (stale). Its successor lexbor is a separate known-list entry.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lexborisov/benchmark-html-persers/blob/master/Results/time/benchmark_0_100.csv>
  - <https://github.com/lexborisov/benchmark-html-parsers>
  - <https://github.com/lexborisov/benchmark-html-parsers/blob/master/benchmark/Makefile>
  - <https://github.com/lexborisov/benchmark-html-parsers/blob/master/Makefile>
  - <https://lexborisov.github.io/benchmark-html-parsers/>
  - <https://github.com/lexborisov/myhtml>
- **Sources the enricher read:**
  - <https://github.com/lexborisov/myhtml>
  - <https://github.com/lexborisov/myhtml/blob/master/README.md>
  - <https://github.com/lexborisov/myhtml/blob/master/INSTALL.md>
  - <https://github.com/lexborisov/myhtml/blob/master/include/myhtml/myosi.h>
  - <https://github.com/lexborisov/myhtml/blob/master/include/myhtml/api.h>
  - https://github.com/lexborisov/myhtml (full recursive file tree)
  - <https://lexborisov.github.io/benchmark-html-parsers/>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/lexborisov/myhtml`) · [data/wave3/enrich/raw/github_com_lexborisov_myhtml.json](../../../data/wave3/enrich/raw/github_com_lexborisov_myhtml.json) (enrichment confidence 0.55)

</details>
