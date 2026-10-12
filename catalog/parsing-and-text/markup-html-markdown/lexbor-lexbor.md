# lexbor

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Standards-compliant C99 HTML5/CSS/DOM/URL engine; beats libxml2-based bindings on HTML parsing and CSS selector throughput.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | Ryzen 3800x, same host language (derived from page data): parse, Crystal lexbor 4.75s vs Crystal Crystagiri(libxml2) 14.20s (\~3.0x); Ruby Nokolexbor(lexbor) 4.07s vs Ruby Nokogiri(libxml2) 18.67s (\~4.6x); CSS select, Nokolexbor 1.80s vs Nokogiri 92.69s (\~51x). The cross-language Crystal-lexbor 0.80s vs Ruby-Nokogiri 92.69s CSS ratio (\~116x) mixes host languages; there is no Crystal/libxml2 CSS number (Crystagiri column is '-'). Apple M1 (derived from page data): Nokolexbor 3.41s vs Nokogiri 18.22s parse (\~5.3x), CSS 1.11s vs 87.21s (\~79x); Crystal lexbor 2.77s vs Crystagiri 126.25s parse (\~45.6x) is anomalous (see caveats). |
| **Workload** | Parse a \~1.5MB Google search-results HTML page 1000 times and run 5000 CSS selector queries, using Crystal/Ruby bindings for lexbor vs myhtml vs libxml2 (via the Crystagiri and Nokogiri bindings). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 3800x; Apple M1 (two separate benchmark runs reported) |
| **Compiler and flags** | Crystal: `crystal build --release --no-debug`; Ruby 2.7 for the Nokogiri/Nokolexbor bindings |
| **Adoption** | 2.1k stars on lexbor/lexbor; used by PHP's DOM/HTML extension (since PHP 8.4), Selectolax, SerpApi, Nokolexbor |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/lexbor/lexbor) · [benchmark](https://github.com/kostya/lexbor#benchmark) |

## Verdict

Third-party Crystal-language benchmark (kostya/lexbor, not the lexbor project) parsed a 1.5MB Google search-results HTML page 1000 times and ran 5000 CSS selector queries on a Ryzen 3800x. Same-language comparisons show lexbor beating libxml2-backed bindings by \~3.0x (Crystal Crystagiri) to \~4.6x (Ruby Nokogiri) on parsing and \~51x-79x on CSS selection (Nokogiri's CSS runs through XPath translation); the headline 116x and the 45.6x M1 figures mix Crystal against Ruby or reflect an anomalous Crystal/libxml2 binding path and are not like-for-like.

## Use it when

- High-volume HTML5 parsing of real-world (possibly malformed) markup where a spec-conformant tokenizer matters, e.g. scraping/crawling pipelines (SerpApi runs lexbor in production for this).
- Need HTML parsing and CSS selector matching from one dependency-free C library instead of wiring libxml2 plus a separate CSS engine.
- Embedding in a size- or dependency-constrained project via the single-header amalgamation (perl single.pl --all), with no libxml2/expat linkage.
- Batch/throughput workloads (many documents or many CSS queries per run) where the benchmark shows the gap over libxml2-based bindings widens most.
- Already need URL parsing, 40+ text encodings, or Unicode normalization/IDNA alongside HTML/CSS, and want one codebase for all of it.

## Skip it when

- Need XML (non-HTML) parsing, XPath, or XSLT — lexbor targets HTML5/CSS/URL/DOM, not general XML; libxml2 still covers that ground.
- Multiple threads touching one parsed document concurrently: the CMake LEXBOR_WITHOUT_THREADS option is documented as inert ('Not used now, for the future'), and no locking is visible in the mraw arena allocator.
- Need well-defined reference-counted/GC'd DOM node lifetime across a long-lived app — 'Reference counting of DOM nodes' (issue #132) is still open and unresolved.
- Depend on the Layout or Fonts modules — both are marked 'in progress' in the README and are not usable yet.
- Writing in Crystal/Ruby/Python/Elixir without going through a wrapper: those bindings (kostya/lexbor, Nokolexbor, Selectolax, fast_html) add their own overhead, and part of the benchmark's largest ratios (51-79x, 116x CSS) come from the baseline's slow Ruby CSS-via-XPath path, not a guaranteed win in every host language.

## How it is fast

Hot scanning loops (tokenizer character search) use a SWAR (SIMD-within-a-register) bit-trick, lexbor_swar_seek4, that checks up to 4 target bytes per machine word instead of per-byte comparisons (source/lexbor/core/swar.h, based on the Stanford 'bit twiddling hacks' techniques). Keyword/tag lookups use a compact static binary search tree (lexbor_sbst_entry_static_t, source/lexbor/core/sbst.h) baked in at compile time instead of runtime hashing. Node and string allocation goes through a custom arena/region allocator (mraw) plus fixed-size object pools (dobject), cutting malloc/free call counts versus a generic tree library. The HTML tokenizer itself is a hand-written WHATWG-spec state machine rather than a generic/recursive parser.

## Compared with alternatives

Use lexbor directly, in C/C++, when you need HTML+CSS+URL+Encoding together with no dependency; on Python or Ruby, selectolax and Nokolexbor already embed lexbor as a backend, so use those instead of binding lexbor yourself. MyHTML (also lexborisov's) is lexbor's own now-superseded predecessor benchmarked against Gumbo/html5ever — lexbor is its actively developed successor, not a co-equal alternative.

## Integration

| | |
|---|---|
| **Form** | source-drop (single-header amalgamation via single.pl) or static/shared lib via CMake |
| **Dependencies** | none (pure C99) |
| **Minimum toolchain** | C99 compiler; CMake for building from source (no minimum GCC/Clang version stated in docs) |
| **Platforms** | prebuilt binaries for x86-64 (CentOS, Debian, Fedora, RHEL, Ubuntu) plus Homebrew/MacPorts on macOS and vcpkg; builds from source on any platform with a C99 compiler and CMake, including Windows via MSYS — other architectures require a source build (README asks to email support for anything beyond x86-64 binaries) |
| **Thread safety** | not documented as thread-safe; LEXBOR_WITHOUT_THREADS CMake flag exists but is explicitly inert ('Not used now, for the future'), and no locking is present in the mraw arena allocator |
| **Drop-in for the baseline** | false — own C API, not libxml2-API-compatible; language wrappers (Nokolexbor for Ruby, Selectolax for Python) offer a closer drop-in feel within their own ecosystems, not at the C level |

## Gotchas

- DOM node reference counting/lifetime is an open design question (issue #132, still open) — do not assume libxml2-style ownership semantics.
- Memory comes from a per-document arena (mraw) plus object pools (dobject); document teardown follows lexbor's own lifecycle calls, not ad hoc free().
- Layout and Fonts modules are listed 'in progress' in the README; only DOM, HTML, CSS, URL, Encoding, Unicode, and Punycode are marked ready.
- Project policy restricts AI-authored contributions to the core library (README 'AI Policy'): PRs touching core C code that read as AI-generated are likely to be rejected, relevant if you plan to upstream a patch.

## Caveats and trade-offs

Third-party benchmark by the author of the Crystal bindings (kostya/lexbor), not the lexbor project, run through Crystal/Ruby bindings; no run date. On M1, Crystagiri(libxml2) takes 126.25s while Nokogiri on the same libxml2 on the same machine takes 18.22s, so the \~45x M1 figure reflects the Crystal/libxml2 binding path, not libxml2 itself. Treat it as an outlier. The &gt;50x CSS ratios come from Nokogiri's CSS path (CSS translated to XPath through Ruby) and are not a pure C-vs-C comparison. The Crystal compiler version and the libxml2/lexbor versions and build flags are not stated. Gumbo test binaries are referenced in bench/run.sh but commented out in bench/build.sh, so Gumbo numbers are not present in the README despite a Gumbo test program existing.

Pure C99, zero external dependencies, modular (HTML/CSS/URL/Encoding/Unicode). The cited benchmark measures Crystal/Ruby language bindings rather than raw C-vs-C, so results include binding/runtime overhead on both sides. A separate, independently-run benchmark for the 'fast_html' Elixir wrapper also shows lexbor beating html5ever directly (125.12ms vs html5ever's 395.21ms parsing a 6.9MB document on an AMD Ryzen 9 3950X; https://fast-html.hexdocs.pm/readme.html), though that benchmark states hardware but not exact compiler flags so it was not used as the primary citation.

## Maintenance

Actively maintained (last commit 2026-09-22, \~2.1k stars) under Apache-2.0, and easy to vendor via the single-header amalgamation script (single.pl), so treated as 'copyable' usability.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public in kostya/lexbor bench/ (test-lexbor.cr, test-libxml.cr, test-libxml.rb, test-nokolexbor.rb, build.sh using `crystal build --release --no-debug`, run.sh; Ruby pinned to 2.7.5), and the README names the CPUs (Ryzen 3800x, Apple M1), so it meets A. It is borderline: the Crystal compiler version and the libxml2/lexbor library versions and build flags are not stated.
- **Verifier notes:** All README numbers match exactly and the derived ratios are arithmetically right. Downgraded only because the headline ratios (116x CSS, 45x M1) are cross-language or anomalous; like-for-like is \~3-5x parse and \~51-79x CSS (Ruby vs Ruby). Metadata checked: Apache-2.0, 2,091 stars, last commit 2026-09-22, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/kostya/lexbor#benchmark>
  - <https://github.com/kostya/lexbor/tree/master/bench>
  - <https://github.com/kostya/lexbor/blob/master/bench/build.sh>
  - <https://github.com/kostya/lexbor/blob/master/bench/run.sh>
  - <https://github.com/kostya/lexbor/blob/master/bench/shard.yml>
  - <https://github.com/kostya/lexbor/blob/master/shard.yml>
  - <https://github.com/lexbor/lexbor>
- **Sources the enricher read:**
  - <https://github.com/lexbor/lexbor>
  - <https://github.com/lexbor/lexbor/blob/master/README.md>
  - <https://github.com/lexbor/lexbor/blob/master/INSTALL.md>
  - <https://github.com/lexbor/lexbor/blob/master/SECURITY.md>
  - <https://github.com/lexbor/lexbor/blob/master/source/lexbor/core/swar.h>
  - <https://github.com/lexbor/lexbor/blob/master/source/lexbor/core/sbst.h>
  - <https://github.com/lexbor/lexbor/blob/master/source/lexbor/core/mraw.h>
  - <https://github.com/lexbor/lexbor/blob/master/source/lexbor/html/html.h>
  - <https://github.com/lexbor/lexbor/issues/132>
  - <https://github.com/kostya/lexbor#benchmark>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/lexbor/lexbor`) · [data/wave3/enrich/raw/github_com_lexbor_lexbor.json](../../../data/wave3/enrich/raw/github_com_lexbor_lexbor.json) (enrichment confidence 0.78)

</details>
