# Harper

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust (WebAssembly build for browsers)` · `Apache-2.0` · 🟢 active

> Rule-based English grammar and spell checker in Rust (native, LSP, WebAssembly); claims millisecond lints versus LanguageTool's seconds, unmeasured.

| | |
|---|---|
| **Beats** | LanguageTool (Java grammar checker) |
| **Claimed result** | README (author claim, no benchmark): takes milliseconds to lint a document while LanguageTool 'would take several seconds'; uses 'less than 1/50th of LanguageTool's memory footprint'. |
| **Workload** | Linting a moderate-size English document; memory footprint compared with LanguageTool. |
| **Metric** | latency |
| **Adoption** | 16.3k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/Automattic/harper) · [benchmark](https://github.com/Automattic/harper) |

## Verdict

Nothing was measured against the baseline: the README asserts that Harper lints a document in milliseconds while LanguageTool 'would take several seconds' and uses under 1/50th of LanguageTool's memory, with no document size, hardware, versions or harness. The repo's Criterion benches and the wasm fuzzy_match harness time Harper alone and publish no numbers, and a WebSearch found no independent comparison.

## Use it when

- In-browser or in-editor grammar checking where text must never leave the device and a JVM or server is not an option (harper.js in a WorkerLinter, harper-ls in an editor).
- Keystroke-rate re-linting of one English document being edited: the per-chunk and per-sentence lint caches make repeat passes cheap.
- Rust applications that want an embeddable English linter as a library (harper-core on crates.io, Apache-2.0) instead of calling out to LanguageTool's Java server.
- Linting comments and prose inside source code, LaTeX, AsciiDoc, HTML or git commit messages through harper-ls and the CLI, which ship dedicated parsers; the wasm API itself accepts only plain text, Markdown and Typst.

## Skip it when

- Any language other than English (the wasm API exposes American, British, Australian, Canadian and Indian dialects only); LanguageTool covers dozens of languages.
- When recall matters more than speed: Harper's rule set is far smaller than LanguageTool's and has no n-gram confusion-word model, so equal work per document is not being done.
- When you need a measured speed or memory win to justify a switch: the project publishes no Harper-versus-LanguageTool numbers, and its own benches never run LanguageTool.
- Memory-tight long-running desktop or extension deployments today: open issue #3874 reports the desktop app and Firefox extension growing to tens of GB (41 GB, 6 GB freed by disabling the extension) with no fix merged.
- Bundle-size-sensitive web apps: the harper.js 2.10.0 npm package unpacks to about 75 MB (several full and slim wasm variants, some base64-inlined); the slim binary drops the thesaurus and Typst, and calling it with Typst input panics ('Typst is not supported in this version of Harper').

## How it is fast

There is no statistical language model to load: about 360 hand-written rule modules (mostly token-pattern 'expr' linters) run over a tokenized document, with part-of-speech tags from a Brill tagger and noun phrases from a small Burn neural chunker whose results are memoized (10,000-entry CachedChunker). Spelling suggestions come from an fst-crate finite-state map searched with Damerau-Levenshtein automata (levenshtein_automata, transposition cost one). LintGroup keeps two 1,000-entry LRU caches keyed by a hash of each chunk's or sentence's characters plus the config, so re-linting an edited document reruns pattern rules only on changed chunks; the release profile uses opt-level 3 and fat LTO, and the wasm build goes through wasm-opt.

## Compared with alternatives

No other grammar checker is catalogued here; among wasm text tools it is closest to sanity-lint (groq-wasm), which at least states a 5-10x figure against its TypeScript twin, whereas Harper has only an unmeasured comparison with a native Java program. Pick Harper when you need English prose checking on-device and accept that its speed advantage over LanguageTool is plausible but undocumented.

## Integration

| | |
|---|---|
| **Form** | crate (harper-core), npm module (harper.js wrapping harper-wasm), language server and CLI binaries |
| **Dependencies** | harper-core: fst, levenshtein_automata, hashbrown, lru, pulldown-cmark, regex, serde/serde_json, zip and about 25 other crates plus harper-brill (Brill tagger and Burn chunker models embedded as JSON and msgpack); harper.js: fflate at runtime |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85+, stable channel; no rust-version declared); wasm-pack with the wasm32-unknown-unknown target for the web build |
| **Platforms** | any Rust target; wasm32 in browsers and Node (harper.js is ESM, built with wasm-pack --target web) |
| **Thread safety** | harper-core's 'concurrent' feature swaps Rc for Arc; the wasm build disables default features, so it is single-threaded and harper.js offers WorkerLinter to move linting off the main thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness note: the Criterion lint_essay bench (harper-core/benches/parse_essay.rs, an 11,436-byte, 1,783-word essay) reuses one LintGroup and one Document, so after the first iteration every chunk and sentence hits the LRU lint caches; it times the warm re-lint path. Even lint_essay_uncached rebuilds the Document but still hits the process-wide thread-local CachedChunker memo of the neural noun-phrase chunker (whose source comment calls inference 'extremely expensive'), so it is not a cold-start number either. The harper.js Linter.bench.ts times only config get/set and ignore-state calls, not linting.
- The memory claim has moved without a measurement: the README now says 'less than 1/50th of LanguageTool's memory footprint', while an older README copy (WebSearch snippet only) said about 1/2 percent. Issue #4071 measured 99.9 MB VmRSS right after FstDictionary::curated() for the English dictionary, because the curated MutableDictionary stays alive next to the FST copy (a patch cuts it to 56.2 MB); issue #3725 measured about 735 bytes per expanded word form in FstDictionary.
- harper-core's README says the 'concurrent' feature is 'Disabled by default', but harper-core/Cargo.toml lists default = ["thesaurus", "concurrent"], so default crate users get Arc and the boxcar dependency.
- harper.js on npm lags the repository (latest 2.10.0 versus 2.12.0 in the manifests), and the wasm Linter calls swap the lint config on every call (with_curated_config), which changes the cache key whenever the config differs.

## Known shortcomings

- Downgraded C to D: README claim only ('milliseconds' vs LanguageTool's 'several seconds', 1/50th the memory) with no LanguageTool benchmark (harper-core/benches and harper-wasm benches time Harper alone); fewer rules than LanguageTool (forum snippet); a native-vs-Java claim, off-category.
- Enricher: still no LanguageTool measurement; the Criterion lint_essay reuses one LintGroup and Document so after iteration 1 every chunk and sentence hits the LRU lint caches, and lint_essay_uncached still hits the thread-local CachedChunker memo; harper.js Linter.bench.ts times only config calls; the memory claim drifted (README now 1/50th, older copy about 1/2%); the English dictionary alone is 99.9 MB VmRSS (#4071) and a desktop/extension leak is open (#3874); README says 'concurrent' is off by default while Cargo.toml enables it.

## Caveats and trade-offs

Author assertion only: no benchmark against LanguageTool exists in the repo or (per a WebSearch, snippet only) anywhere public; 'milliseconds' and 'several seconds' are not measurements, and the 1/50th figure is memory, not latency. harper-core/benches (parse_essay.rs, lint_essay, spellcheck.rs) and harper-wasm/benches/wasm_bench.js time Harper alone (the wasm harness reuses the native word lists so wasm and native could be compared, but no numbers are published). The claim is not wasm-versus-native: the baseline is a native Java tool and the claim is about the native Rust engine, so it fits this category poorly. Harper covers far fewer rules than LanguageTool (a forum commenter, snippet only) and supports English only, so the work done per document is not equal.

English only; far fewer rules than LanguageTool and no n-gram data set; the WebAssembly build is one delivery target alongside native binaries and a language server.

## Maintenance

Very active (16.3k stars, 4,755 commits, Apache-2.0, harper-core 2.11.0 on crates.io with about 123k downloads, last commit 2026-10-11) and safe to depend on as a library; the evidence tier stays D because the speed and memory claims are author assertions, and the desktop and extension builds carry an open, unreproduced memory-leak report (#3874).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README only asserts that Harper lints 'in milliseconds' where LanguageTool 'would take several seconds' and uses 'less than 1/50th' of its memory; no measured latency, document size, hardware or harness is given anywhere. The repo's own Criterion benches (harper-core/benches/parse_essay.rs, spellcheck.rs) time Harper alone and never run LanguageTool, so the speed claim is directional only.
- **Verifier notes:** Real, notable project (16.3k stars, Apache-2.0, last commit 2026-10-11) but the speed claim has no numbers, so it drops from C to D; keep and document per the keep-and-document rule. Shortcomings: no LanguageTool benchmark, unequal rule coverage, claim is native-versus-Java rather than wasm-versus-native or wasm-versus-JS (off-category baseline).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-15 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/README.md>
  - <https://github.com/Automattic/harper>
  - <https://github.com/Automattic/harper/commits>
  - <https://github.com/Automattic/harper/tree/master/harper-core>
  - <https://github.com/Automattic/harper/tree/master/harper-core/benches>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/benches/parse_essay.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/benches/spellcheck.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-wasm/benches/wasm_bench.js>
- **Sources the enricher read:**
  - <https://github.com/Automattic/harper>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/README.md>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/README.md>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/Cargo.toml>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-wasm/README.md>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/benches/parse_essay.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/benches/spellcheck.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/benches/essay.md>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-wasm/benches/wasm_bench.js>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/src/linting/mod.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/src/linting/lint_group/mod.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/src/lib.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/src/document.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-core/src/spell/fst_dictionary.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-brill/Cargo.toml>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/harper-brill/src/lib.rs>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/justfile>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/packages/harper.js/package.json>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/packages/harper.js/README.md>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/packages/harper.js/src/Linter.bench.ts>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/packages/harper.js/src/main.ts>
  - <https://raw.githubusercontent.com/Automattic/harper/HEAD/packages/harper.js/src/LocalLinter.ts>
  - <https://github.com/Automattic/harper/tree/master/packages/harper.js/src>
  - <https://github.com/Automattic/harper/issues?q=is%3Aissue%20slow%20OR%20performance%20OR%20memory>
  - <https://github.com/Automattic/harper/issues/3725>
  - <https://github.com/Automattic/harper/issues/3874>
  - <https://github.com/Automattic/harper/issues/4071>
  - <https://crates.io/api/v1/crates/harper-core>
  - <https://registry.npmjs.org/harper.js/latest>
  - WebSearch: Harper grammar checker vs LanguageTool speed memory benchmark (snippets only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/automattic/harper`) · [data/wave13/enrich/raw/github_com_automattic_harper.json](../../../data/wave13/enrich/raw/github_com_automattic_harper.json) (enrichment confidence 0.75)

</details>
