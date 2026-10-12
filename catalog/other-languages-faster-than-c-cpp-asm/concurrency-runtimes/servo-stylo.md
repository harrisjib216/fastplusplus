# Stylo (Rust parallel CSS style engine in Firefox Quantum) vs Gecko's previous C++ style system

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0` · 🟢 active

> Firefox's and Servo's Rust CSS style engine; its parallel cascade replaced Gecko's sequential C++ style system in Firefox 57.

| | |
|---|---|
| **Beats** | Gecko's previous sequential C++ style system (CSS selector matching and cascade) in Firefox before Quantum |
| **Claimed result** | 30% page load speedup for Amazon's homepage ('Parallelism leads to a lot of performance improvements, including a 30% page load speedup for Amazon's homepage'). Stylo replaces about 160,000 lines of C++ with 85,000 lines of Rust. |
| **Workload** | Firefox page load of Amazon's homepage, where style computation runs as a parallel work-stealing top-down cascade (rayon) instead of the old single-threaded C++ cascade. |
| **Metric** | latency |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Rust's ownership and Send/Sync checking made it practical to run the top-down style cascade in parallel with a rayon work-stealing traversal (child styles are independent once the parent is computed), where two earlier C++ attempts failed on thread-safety bugs. Stylo also shares computed style structs through Arc. The Hacks post additionally credits optimizations borrowed from other browsers (snippet only). |
| **Adoption** | 340 stars (servo/stylo); ships in Firefox since Quantum (version 57) and in Servo |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/servo/stylo) · [benchmark](https://raw.githubusercontent.com/rust-lang/blog.rust-lang.org/main/content/Fearless-Concurrency-In-Firefox-Quantum.md) |

## Verdict

A Rust blog post by Servo/Stylo developer Manish Goregaokar for the Firefox Quantum release (2017-11-14) says parallel styling gave 'a 30% page load speedup for Amazon's homepage' compared with Gecko's earlier sequential C++ style system. Compiler, flags, hardware, core count and number of runs are not given, and no benchmark code exists.

## Use it when

- Building a browser engine, HTML/CSS renderer or document layout tool in Rust that needs browser-grade CSS (cascade, inheritance, media queries, invalidation); crates.io shows Servo's crates and Blitz (blitz-dom, stylo_taffy) as the main dependents.
- Styling large documents (thousands of elements, wide DOM levels) on multi-core machines, where the work-stealing traversal can use up to 6 style threads.
- Using only the `selectors` crate for CSS selector matching in your own tree type; it is also standalone and far more widely used (about 85 million crates.io downloads versus about 395,000 for `stylo`).
- Studying how a production parallel tree traversal is structured in Rust: adaptive sequential-to-parallel switch, per-thread caches, Arc-shared immutable results.

## Skip it when

- As a C++ library: there is no C or C++ API outside mozilla-central's generated Gecko bindings, so a C++ engine cannot simply link it.
- Small documents or single-core targets: the traversal stays sequential until a DOM level is wider than the work-unit size, and with one thread or fewer no pool is created, so the parallel gain disappears.
- Projects that need a stable API: crate versions break roughly monthly (0.20.0 on 2026-08-04, 0.21.0 on 2026-09-08, 0.22.0 on 2026-09-30) and the main branch is rebased on every upstream sync, so `git pull` does not work across syncs.
- Simple stylesheet-to-attribute tasks (inline CSS for e-mail, CSS linting): the engine is large (it replaced about 160,000 lines of C++ with 85,000 lines of Rust, before later growth) and pulls in rayon, cssparser, ICU segmenter and many other crates.

## How it is fast

Styling is a top-down tree traversal, so once a parent's style is known its children are independent; Stylo walks the DOM breadth-first and hands chunks of discovered children to a rayon work-stealing pool (rayon in_place_scope_fifo / spawn_fifo in style/parallel.rs and style/driver.rs), staying sequential until a DOM level is wide enough to be worth splitting. Computed styles are split into immutable 'style structs' shared between elements through servo_arc::Arc with copy-on-write mutation. Per-thread caches avoid repeated work: a style sharing cache lets siblings and cousins with identical rule matches reuse a computed style without selector matching, and a counting Bloom filter of ancestors fast-rejects descendant selectors (the same idea as Gecko's AncestorFilter and WebKit/Blink's SelectorFilter); matched rules are inserted into a shared rule tree so elements with the same rule chain share one node.

## Compared with alternatives

The sibling entries are general runtimes and benchmarks (Rayon vs OpenMP, NPB-Rust, Tokio, Pony, CAF comparisons); pick Stylo only when you need a CSS engine, and treat it as the largest production example of rayon work-stealing applied to an irregular tree traversal. For general data-parallel loops use rayon directly, as in the NPB-Rust and Rayon vs OpenMP entries.

## Integration

| | |
|---|---|
| **Form** | crate (stylo 0.22.0, lib name `style`, plus selectors, servo_arc, stylo_traits, stylo_dom, stylo_atoms, stylo_static_prefs and derive crates) |
| **Dependencies** | rayon, cssparser 0.38, selectors, servo_arc, hashbrown, parking_lot, icu_segmenter, euclid, app_units, smallvec, thin-vec, string_cache and about 30 more crates; `gecko` feature additionally needs bindgen and mozilla-central bindings |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85+); CI builds with current stable; no rust-version field |
| **Platforms** | Linux, macOS and Windows in CI (debug builds and tests; release build on Linux); wasm32 has a no-thread code path; Firefox builds its copy inside mozilla-central |
| **Thread safety** | Designed for parallel use: a global rayon pool (default 0.75 x logical CPUs, capped at STYLO_MAX_THREADS = 6, overridable through the layout.threads pref in Servo or layout.css.stylo-threads in Gecko); DOM nodes are not Send and cross threads only through an unsafe SendNode wrapper, with per-element mutable state in AtomicRefCell that panics on conflicting borrows. |
| **Drop-in for the baseline** | no |

## Gotchas

- The only measurement is end-to-end Firefox page load on Amazon's homepage (30%, 2017), Firefox with Stylo against Firefox with the old C++ style system, with no hardware, core count, build flags or run count. It mixes parallelism with the rewrite's other optimisations (style sharing cache, rule tree and Bloom filter tuning), and the old C++ system shipped only in Firefox 56 and earlier (Mozilla wiki snippet), so the comparison cannot be rerun on a current build.
- Thread scaling is capped by design: style/global_style_data.rs limits the pool to 6 threads because 'the performance benefit of additional threads seems to level off at around six' (Mozilla bug 1431285 comment 14). The Mozilla Hacks claim of 'up to 2 or 4 or even 18 times faster' (seen only as a search snippet; hacks.mozilla.org is unreachable here) therefore cannot come from thread count alone and has no published method.
- The Servo flavour in this repo differs from Firefox's: downstream patches and prefs decide which CSS features are enabled (recent commits switch on writing modes, text-indent keywords and justify-items propagation for Servo), and open issue #235 notes that the default restyle damage 'rebuild_box' is bad for performance.
- Off-main-thread styling calls back into host code; the Rust blog post says such calls regularly exposed thread-safety bugs in Firefox's C++ caches and global mutable state, so a host's own callbacks must be thread-safe.

## Known shortcomings

- Blog claim only (30% Amazon page load, 160k lines of C++ vs 85k Rust), first-party with no methodology; parallel Rust against a serial C++ style system.
- The only evidence is one 2017 blog number (30% faster Amazon page load) with no method. global_style_data.rs caps the pool at 6 threads (STYLO_MAX_THREADS, bug 1431285), so the Hacks 'up to 18x' cannot come from threads alone. The old C++ style system shipped only up to Firefox 56, so the comparison cannot be rerun. hacks.mozilla.org and blog.nightly.mozilla.org unreachable.

## Caveats and trade-offs

First-party blog (Rust blog post by a Servo/Mozilla engineer, 2017-11-14) with a single headline number: no workload details beyond 'Amazon's homepage', no hardware, core count, Firefox build flags, run count or comparison builds, and no benchmark code. The comparison is Firefox with Stylo against Firefox with the old C++ style system, so it mixes the rewrite's other optimizations with the parallelism; a Mozilla Hacks post (hacks.mozilla.org was blocked here, so seen only as a WebSearch snippet) says the engine borrows optimizations from other browsers and would be fast without parallelism, and gives a best-case 'up to 2, 4 or even 18 times faster' style-computation range that scales with core count (snippet only, not verified). Baseline is a production C++ build, probably with PGO and LTO, but this is not stated. The repo servo/stylo is Servo's downstream copy of the code that lives in mozilla-central (the Firefox repo, already on the known list); it carries no benchmark. The blog's 'two earlier C++ attempts to parallelize the style system failed' is a claim about engineering difficulty, not a measurement. [retier] global_style_data.rs caps the pool at 6 threads (STYLO_MAX_THREADS, bug 1431285), so the Hacks 'up to 18x' cannot come from threads alone. The old C++ style system shipped only up to Firefox 56, so the comparison cannot be rerun.

Not a standalone library: it is wired into Gecko or Servo through Rust-to-C++ FFI and a DOM abstraction, and it needs those hosts to call back into C++ for some data. The blog says occasional calls into C++ code off the main thread surfaced thread-safety bugs in the C++ side (caches, global mutable state). Parallelism helps large pages and many cores; tiny documents gain little.

## Maintenance

Very active (daily commits, last 2026-10-11; monthly crate releases), MPL-2.0, shipped to every Firefox user since version 57 and used by Servo and Blitz; usable as a Rust crate if you implement its DOM traits, but the API churns every sync and the performance evidence is a single 2017 first-party number.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The Rust blog post (Manish Goregaokar, a Servo/Stylo developer, 2017-11-14) states 'a 30% page load speedup for Amazon's homepage' and '160,000 lines of C++ with 85,000 lines of Rust' verbatim, with no hardware, build, run count or benchmark code: first-party numbers without methodology, tier C.
- **Verifier notes:** Record accurate: blog text, MPL-2.0, 340 stars, last commit 2026-10-11 all confirmed; servo/stylo README says upstream lives in mozilla-central and this repo is Servo's downstream sync (not a GitHub fork). Shortcomings: one headline end-to-end number, parallel Rust vs serial C++ (parallelism and rewrite optimizations, not language codegen), no methodology. Same claim as merged record paper:stylo-w14-sys-blogs (systems-and-safety, same blog number, no benchmark_url): fold that one as duplicate of this id.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-93 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rust-lang/blog.rust-lang.org/main/content/Fearless-Concurrency-In-Firefox-Quantum.md>
  - <https://github.com/servo/stylo>
  - <https://github.com/servo/stylo/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rust-lang/blog.rust-lang.org/main/content/Fearless-Concurrency-In-Firefox-Quantum.md>
  - <https://github.com/servo/stylo>
  - <https://github.com/servo/stylo/commits/main>
  - <https://github.com/servo/stylo/issues?q=is%3Aissue+performance>
  - <https://github.com/servo/stylo/issues/235>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/README.md>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/SYNCING.md>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/style.paths>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/style/Cargo.toml>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/style/lib.rs>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/style/parallel.rs>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/style/driver.rs>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/style/global_style_data.rs>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/style/sharing/mod.rs>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/style/bloom.rs>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/style/rule_tree/mod.rs>
  - <https://raw.githubusercontent.com/servo/stylo/HEAD/.github/workflows/main.yml>
  - <https://crates.io/api/v1/crates/stylo>
  - <https://crates.io/api/v1/crates/selectors>
  - <https://crates.io/api/v1/crates/stylo/reverse_dependencies?per_page=50>
  - https://hacks.mozilla.org/2017/08/inside-a-super-fast-css-engine-quantum-css-aka-stylo/ (unreachable: ENOTFOUND; claim taken from a search snippet)
  - https://blog.nightly.mozilla.org/2017/07/25/stylo-is-ready-for-community-testing-on-nightly/ (unreachable: ENOTFOUND)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/servo/stylo`) · [data/wave14/enrich/raw/github_com_servo_stylo.json](../../../data/wave14/enrich/raw/github_com_servo_stylo.json) (enrichment confidence 0.45)

</details>
