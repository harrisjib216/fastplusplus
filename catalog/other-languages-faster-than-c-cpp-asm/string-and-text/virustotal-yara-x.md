# YARA-X (Rust rewrite of YARA)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Rust rewrite of the YARA malware-pattern scanner; vendor reports 1.85x faster full-ruleset scans than C YARA since v1.16.0.

| | |
|---|---|
| **Beats** | YARA (VirusTotal/yara, the C implementation; the blog calls it 'YARA (legacy)', version not stated) |
| **Claimed result** | Blog table (500 files, \~24 GB, YARA Forge rule set): YARA-X with daachorse 26.152 s, YARA (legacy) 48.275 s, which the blog states as 'YARA-X with daachorse is 1.85x faster'; the same table lists YARA-X with the previous aho_corasick crate at 57.584 s, i.e. slower than legacy YARA (about 1.19x slower, derived from page data). Docs page: the bitcoin_address regex rule on a \~200 MB file 'will take more than 20 seconds in YARA, but less than a second in YARA-X'; the 'for any i in (0..filesize-1)' rule 'will be 5-6x faster in YARA-X than in YARA'. Both pages say YARA-X is faster in almost all cases with a few exceptions where YARA is better. |
| **Workload** | Scanning files with YARA rules (multi-pattern Aho-Corasick string search plus regex and hex-pattern evaluation): full YARA Forge rule set over 500 random VirusTotal files (about 24 GB); single-rule docs examples (a Bitcoin-address regex over a \~200 MB file, and a for-loop rule). |
| **Metric** | throughput |
| **Compiler and flags** | Not stated on the blog or docs page. Defaults (not confirmed as what was benchmarked): YARA's Makefile.am adds -O3 when optimization is enabled (the configure default); YARA-X's Cargo.toml has no custom [profile.release], so cargo --release uses opt-level 3 (an optional release-lto profile adds LTO and codegen-units=1). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Blog (about the 2.2x gain over the previous YARA-X build, not directly versus YARA): swapping the aho_corasick crate for daachorse, a double-array Aho-Corasick with a tighter inner loop and cache-efficient storage; a later change groups many 'matches' regexes on one target into a single RegexSet pass. Docs give no mechanism for the regex and loop-rule gaps versus YARA beyond 'performs better ... with regular expressions and complex hex patterns'. |
| **Adoption** | 1.3k stars; VirusTotal states it runs YARA-X in production |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/VirusTotal/yara-x) · [benchmark](https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/site/content/blog/yara-x-just-got-faster/index.md) |

## Verdict

VirusTotal's own run (PR #654, blog 2026-05-13): 500 random VirusTotal files (\~24 GB, private), YARA Forge full rule set, 16 scan threads, precompiled rules, YARA-X with daachorse about 26.2 s versus legacy C YARA about 47.7-48.3 s (1.82-1.85x) and 1.54x on the core set; hardware, compilers, flags and the YARA version are not stated. Independent users measured older YARA-X builds 1.3-3.2x slower than YARA and v1.16.0 at rough parity (3% slower wall, 17% less CPU).

## Use it when

- Bulk scanning of large corpora (GB-scale, many files) with large rule sets such as YARA Forge, where match time dominates and the v1.16+ daachorse matcher applies.
- Rule sets with expensive regexes or complex hex patterns that YARA warns 'may slow down scanning'; the docs cite more than 20 s versus under 1 s for a bitcoin-address regex on a \~200 MB file.
- Rules with loops over the file (for any i in (0..filesize-1)), which the docs put at 5-6x faster than YARA.
- New Rust, C, Python or Go integrations that want memory safety, better error reporting, a reusable parser (formatter, language server) and per-scan timeouts, and can adopt a new API.

## Skip it when

- Many short scans of small files, each in a new process: issue #496 measured the yr CLI at 10.7 ms per small file versus YARA at 1.9 ms with precompiled rules, because loading rules JIT-compiles their WASM (2.68 ms for four rules) unless the non-default native-code-serialization feature is used.
- Existing code built on libyara's C API, or on yara-python and go-yara: the APIs differ and must be ported.
- Live process memory scanning, which YARA supports and YARA-X does not.
- Hardened or sandboxed hosts that forbid executable memory (macOS 26 Hardened Runtime killed scans in issue #645 without allow-jit and allow-unsigned-executable-memory entitlements); the opt-in 'pulley' interpreter avoids the JIT but one user measured about 3x lower throughput.
- Pinned older versions: before v1.16.0 independent users measured YARA-X slower than YARA (issue #391: 1.31x, 1.41x and 3.19x more wall time, derived from page data).

## How it is fast

Rule strings are reduced to short atoms and found in one pass with a double-array Aho-Corasick automaton (the daachorse crate since v1.16.0, PR #654) plus an in-tree Teddy SIMD prefilter adapted from the aho-corasick crate for small pattern sets; atom hits are then verified, with 'exact atoms' skipping verification when the atom alone proves a match, and regex verification runs on YARA-X's own FastVM with a PikeVM fallback (the docs give no mechanism for the regex gap versus YARA). Rule conditions are compiled to WebAssembly and JIT-compiled to native code by wasmtime's Cranelift, and since PR #657 (v1.17.0) many 'matches' tests on one field inside an 'or' are merged into a single regex::RegexSet pass.

## Compared with alternatives

Pick YARA-X when you need YARA rule semantics (conditions, counts, offsets, file-format modules) over many files; for plain multi-regex text search the Rust regex crate (which YARA-X uses for its RegexSet path) or Hyperscan in that sibling's benchmarks is the simpler tool, and fastgrep or similar grep replacements suit ad hoc searching.

## Integration

| | |
|---|---|
| **Form** | crate (yara-x on crates.io); C API as static or shared library (yara_x_capi); Python and Go bindings; yr CLI |
| **Dependencies** | wasmtime 48 with Cranelift, daachorse 5, regex and regex-automata, memchr, protobuf, plus parser crates per enabled module (nom, x509-parser, RSA/ECDSA crates for signature checks) |
| **Minimum toolchain** | Rust 1.95.0 (MSRV in Cargo.toml), edition 2024 |
| **Platforms** | Platforms Cranelift supports for the default JIT build; the optional 'pulley' feature interprets rule conditions for other targets or no-JIT environments; a wasm32 build exists (js-wasm). |
| **Thread safety** | Compiled Rules can be shared across threads; each Scanner scans one file or buffer at a time and should be used from one thread (one scanner per thread, per the crate docs and C header). |
| **Drop-in for the baseline** | partial — most YARA rules compile unchanged (stricter regex escaping, base64 and a few other documented differences), but the C, Python and Go APIs and compiled-rule files are not compatible with YARA's, and process scanning is missing. |

## Gotchas

- Harness note: the blog's 1.85x quotes run 1 of three per scanner from PR #654, and YARA's run 1 (48.275 s) was its slowest; three-run means give 47.671 s vs 26.155 s (1.82x), and the YARA Forge core set in the same PR gives only 32.103 s vs 20.871 s (1.54x, derived from page data). All runs used 'scan -r -p 16' with precompiled rules on unstated hardware and an unstated YARA version.
- The only independent same-session check after the daachorse change (issue #391, 2026-05-07, about 9,500 rules over /usr) shows YARA-X v1.16.0 at 9m59.056s wall versus YARA 9m41.222s, about 3% slower, while using about 17% less user CPU (derived from page data); the vendor's 1.85x is not reproduced on that workload.
- Atom extraction differs from YARA: in issue #444 the regex /[A-Za-z0-9+\/]{64,512}\x00/ yields 4096 two-byte atoms in YARA-X versus a single '00' atom in YARA, so one rule took about 10 s on a sub-700 KB file once another rule forced pattern search; profile with the rules-profiling feature.
- In November 2025 (issue #496) the maintainer still described YARA as about 2-3x faster at raw scanning; the docs page now claims YARA-X is faster in almost all cases, which rests on the v1.16.0 matcher swap.

## Known shortcomings

- Vendor-only numbers (26.152 s vs YARA 48.275 s, 1.85x) on a private 500-file corpus with no hardware or build details; before v1.16.0 YARA-X with aho_corasick was 57.584 s, slower than YARA; the win comes from architecture (daachorse, the regex engine, wasmtime-run conditions), not Rust codegen.
- The blog's 1.85x uses run 1 of 3 from PR #654, and YARA's run 1 was its slowest; three-run means give 1.82x and the core rule set only 1.54x (derived). The run used scan -r -p 16 with precompiled rules on unstated hardware. The only independent check after daachorse (issue #391, v1.16.0, about 9.5k rules over /usr): 9m59 vs 9m41 wall, about 3% slower with 17% less user CPU; older builds measured 1.31x, 1.41x and 3.19x slower. Small files cost 10.7 ms in YARA-X against 1.9 ms in YARA (WASM JIT at load, #496); one regex yields 4096 atoms and takes 10 s (#444); macOS 26 Hardened Runtime kills scans unless JIT entitlements are set (#645); the pulley interpreter is about 3x slower.

## Caveats and trade-offs

First-party claim from the vendor (VirusTotal, Google) with no hardware, compiler flags, YARA version or build options, and the 500-file corpus is private, so the 1.85x figure is not reproducible by others; tier C. The same blog table shows YARA-X was slower than YARA (57.584 s vs 48.275 s, about 1.19x slower, derived from page data) before the daachorse change in v1.16.0, and the docs concede some rules and files where YARA still wins. The single-rule claims (more than 20 s vs under 1 s for a bitcoin_address regex on a \~200 MB file; 5-6x for a for-loop rule) give no machine, file or version details and target rules YARA itself warns 'may slow down scanning'. The VirusTotal Livehunt figures (p99 over 6 s to under 3 s) compare YARA-X before and after PR #657, not YARA. The win is architectural (different matcher, regex engine and condition execution via wasmtime), not a Rust codegen effect, and both builds' optimisation levels are unstated (defaults are -O3 for YARA and opt-level 3 for YARA-X). Read from the markdown sources inside the repo (site/content/blog/yara-x-just-got-faster/index.md, site/content/docs/intro/yara_vs_yara-x.md); the rendered virustotal.github.io pages are blocked here. [retier] The blog's 1.85x uses run 1 of 3 from PR #654 (YARA's slowest run); three-run means give 1.82x and the core rule set 1.54x. The only independent check after daachorse (issue #391, v1.16.0, about 9.5k rules over /usr): 9m59 vs 9m41 wall, about 3% slower with 17% less user CPU. Small files cost 10.7 ms against 1.9 ms in YARA (WASM JIT at load, #496); one regex yields 4096 atoms and takes 10 s (#444); macOS 26 Hardened Runtime kills scans without JIT entitlements (#645).

Not a drop-in replacement: the C/C++, Python and Go APIs differ from YARA's (docs). No process scanning. A few rule semantics differ (docs 'differences with YARA'). Rust crate with C API in capi/.

## Maintenance

Actively developed by VirusTotal (v1.21.0 workspace version, last commit 2026-10-09, 1.3k stars, BSD-3-Clause) and run in VirusTotal production; usable today, but its speed advantage over YARA dates only from v1.16.0 (May 2026) and is vendor-measured, with the one independent post-1.16 check showing parity rather than 1.85x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party vendor numbers (VirusTotal blog 'YARA-X just got faster', 2026-05-13, and the docs page yara_vs_yara-x.md) against legacy YARA, with no hardware, compiler, flags, YARA version or build options and a private 500-file corpus; no public harness that runs both scanners. Vendor-blog evidence from the product's owner is tier C.
- **Verifier notes:** Blog table matches the record exactly (26.152 s daachorse, 57.584 s aho_corasick, 48.275 s legacy YARA, 1.85x stated) and docs claims match verbatim; license BSD-3-Clause, 1.3k stars, last commit 2026-10-09 confirmed. Shortcomings: vendor-only numbers, private corpus, no hardware or build details, YARA-X slower than YARA before v1.16.0, some rules still faster in YARA, win is architectural rather than language-level.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-94 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/site/content/blog/yara-x-just-got-faster/index.md>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/site/content/docs/intro/yara_vs_yara-x.md>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/VirusTotal/yara/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/VirusTotal/yara/HEAD/Makefile.am>
  - <https://github.com/VirusTotal/yara-x>
  - <https://github.com/VirusTotal/yara-x/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/README.md>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/site/content/blog/yara-x-just-got-faster/index.md>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/site/content/docs/intro/yara_vs_yara-x.md>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/site/content/docs/writing_rules/differences.md>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/lib/Cargo.toml>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/capi/Cargo.toml>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/capi/include/yara_x.h>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/lib/src/lib.rs>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/lib/src/scanner/mod.rs>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/lib/src/compiler/atoms/mod.rs>
  - <https://raw.githubusercontent.com/VirusTotal/yara-x/HEAD/lib/src/scanner/matches.rs>
  - <https://github.com/VirusTotal/yara-x>
  - <https://github.com/VirusTotal/yara-x/tree/main/site/content/docs/writing_rules>
  - <https://github.com/VirusTotal/yara-x/issues?q=is%3Aissue+slower+than+yara>
  - <https://github.com/VirusTotal/yara-x/issues/391>
  - <https://github.com/VirusTotal/yara-x/issues/496>
  - <https://github.com/VirusTotal/yara-x/issues/444>
  - <https://github.com/VirusTotal/yara-x/issues/645>
  - <https://github.com/VirusTotal/yara-x/pull/654>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/virustotal/yara-x`) · [data/wave14/enrich/raw/github_com_virustotal_yara_x.json](../../../data/wave14/enrich/raw/github_com_virustotal_yara_x.json) (enrichment confidence 0.75)

</details>
