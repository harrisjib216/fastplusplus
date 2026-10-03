# Queue: extensions saved for the end

## Unfinished work (resume here first; updated 2026-10-03 evening)

This section is the open backlog from the main wave loop. It is not an extension; run it before the
extension passes further down. Wave 8 closed on 2026-10-03: all 156 verify batches have verdicts,
all 388 verified entries are enriched, lists re-rendered (COPYABLE 1180, REFERENCE 137).

1. **Wave 8 backfill seed pass (seed-j)** from this session's leads (`data/wave8/leads.md`, the
   2026-10-03 entries): chusitoo/flatbush (C++ Flatbush port), Cortex-Discovery/sobek and
   SNU-ARC/flashTP (equivariant tensor products), xing-cong/CB-Sparse (CB-SpMV) and
   CornellHPC/Ocean-SpGEMM (independent SpMV/SpGEMM suites that beat TileSpMV, DASP, OpSparse),
   bbuhrow/avx-ecm, philipturner/metal-flash-attention, hchengv/avxbls, wibraun/NICSLU (open
   NICSLU 3.0.1; may be a duplicate note), jirka-h/ranluxpp-portable, cd-mcfarland/fast_prng,
   dzhang314/MultiprecisionBenchmarks (QD vs MPFR harness), NLAFET/SyLVER, hpsim/OGL (likely a
   Ginkgo duplicate). Add a `seed` assignment with that `projects` list, run
   `python3 pipeline/seed.py data/wave8 --batch seed`, merge, verify, enrich, re-render.
2. **Paper-access retiers** (need arXiv/ACM/IEEE/Springer or an author-hosted PDF): ttm (ICCS
   2024, likely B), costa (ISC21), pargeo, nicslu (TCAD 2013), spral (TOMS 2016, arXiv
   1909.08104), openequivariance (ACDA25), wrs (ESA 2019, to A), m4ri (TOMS Alg. 898), amgt and
   tilespmv (SC '24, IPDPS 2021 numbers still snippet-only), auto-mpft (its KDD 2024 PDF is
   reachable at raw.githubusercontent.com/yongchanpark/yongchanpark.github.io/gh-pages/
   resources/2024/KDD/ParkKK24.pdf), kokkos-kernels (spECK PPoPP '20 counter-benchmark),
   gpunufft (cufinufft issue #126 vs the cuFINUFFT paper), plus the older list in
   `data/wave8/leads.md` (fmm-gen, fastshuffleexperiments, HPTT, heFFTe, CoDiPack, ALP, SPRK,
   polylidar, FBGEMM, PFT done, fbfft, SFFT, Edamatsu/Takahashi, stochastic-generation, SPRAL,
   TileSpMV, FFTN on gitlab.sac-home.org).
3. **Usage-limit lesson:** launching 15-20 Opus/Sonnet agents at once exhausted the account's
   session limit twice on 2026-10-02. Eight at a time, recording each report before launching
   more, ran a full day on 2026-10-03 without a kill.
4. **Waves 9-12** are set up but not launched: 152 assignments across 19 categories
   (wave 9 compression: entropy-coders, general-lossless, integer-bitpacking, succinct-structures;
   wave 10 media: color-and-resampling, font-shaping-text-layout, image-codecs, rasterizers-2d,
   video-audio; wave 11 runtime: allocators-gcs, coroutines-fibers, filesystems-and-io,
   logging-tracing, profilers-and-instrumentation, thread-pools-work-stealing; wave 12 languages:
   bytecode-vms-and-wasm, embedded-scripting, jits, language-interpreters). Re-render b1/b2 before
   launching so each known list is current. In a cloud session give every agent
   `pipeline/cloud_harness.md`; b7/b8 and paper retiers need an environment that can reach HN
   Algolia and arXiv.

---

Extensions extracted from a later rewrite of the spec (2026-09-25). They are **not active**: the spec
(`faster-than-std-agent-prompt.md`), the pipeline scripts and the records in `data/` stay as they are until
waves 3–12 finish. Everything below is additive and runs as its own pass at the end.

The rewrite was built on the original spec, so its tier definitions, 15–25 call budget, max 8 entries and
"verification recommended" were dropped here on purpose; the current spec's rules win.

## Order

1. **Seed-list mining, static lists** (section F): awesome-cpp (70 sections), awesome-c (55). Skip GUI, game,
   book and tutorial sections. Seeds feed a backfill pass for every finished wave. No current entry came from
   an awesome list, so yield should be real.
2. **Whole-stdlib decomposition** (end of section F): EASTL has only `eastl::vector` (tier C); ETL,
   micron.cpp, rpp, itlib, Coost, sfl are not catalogued.
3. **Wave 13 — assembly-simd-kernels-and-wasm** (section D), seeded from the asm/wasm lists and GitHub topics.
4. **Wave 14 — other-languages-faster-than-c-cpp-asm** (section E), seeded from the cross-language suites.
   Needs sections B and C.
5. **Per-language curated lists** (section F): locate each with `gh search repos`, then mine.
6. **Dynamic pages** (section F): re-mine topics/trending on a schedule once the list is published.

## Before running (do as new scripts / prompt copies, not edits to the current ones)

- **Schema:** the 4 keys in section C are optional. Existing records get defaults
  (`language_level_claim: false`, others `null`); `merge.py` must accept them without "extra keys" warnings.
- **Dedup key for wave 14:** language-level claims share one suite repo, so the canonical-URL key would
  collapse them. Use `suite#benchmark#language`.
- **No-evidence seeds** go to `SEEDS_NO_EVIDENCE.md` (section F rule 4), not tier D records as `seed.py` does
  for known-list projects.
- **Verifier:** add checks for `same_algorithm` / `same_opt_level` and allow correcting the 4 new fields.
- **Mining without WebSearch:** fetch each list's README with `gh api repos/OWNER/REPO/readme`, split by
  heading, give each Haiku agent one section's text.
- **Source status (checked 2026-09-25):**
  - fffaraz/awesome-cpp: 73k stars, active.
  - oz123/awesome-c: 11.6k stars, active.
  - mcuking/Awesome-WebAssembly-Applications: active.
  - kostya/benchmarks, smarr/are-we-fast-yet: active.
  - attractivechaos/plb2: last push 2025-01.
  - TechEmpower/FrameworkBenchmarks: **archived**; results frozen but readable.
  - Maijin/awesome-asm (2015, 82 stars), yifengyou/awesome-asm (2017, 27 stars): low yield.
  - Hack-Labs/awesome-assembler: 2023, 37 stars.
  - AssemblyScript/examples: 2022.
  - The r/C_Programming thread: Reddit blocks automated fetches here.
- The rewrite also put seed-list mining first in the per-wave pipeline ("runs once up front and feeds every
  wave"). Since waves 1–2 are done, run it as a backfill instead.

---

## A. Language filter examples (Part 2, extended)

```
Language filter: {LANGUAGE_FILTER}   (e.g. "any", "C++ only", "Rust", "Go", "Zig", "Ada/SPARK", "Fortran", "D", "Nim", "Odin", "Julia", "OCaml", "Common Lisp", "APL/BQN/K", "Chapel", "Futhark", "Halide/ISPC", "Forth", "BCPL/Oberon/Pascal (historical)", "Python", "Clojure/JVM")
```

## B. Cross-language claims (Part 2, WHAT COUNTS addition)

```
CROSS-LANGUAGE CLAIMS ("X in Ada/Fortran/Rust/Zig/... is faster than the
C/C++/asm version"): these are in scope and get their own wave, but they are
the easiest claims to get wrong, so record ALL of the following:
  - same_algorithm: was it the same algorithm, or a different one? A
    Fortran matmul beating naive C is an algorithm win, not a language win.
  - same_opt_level: -O3 / -O2 / release on both sides, LTO/PGO on both or
    neither, same SIMD width allowed on both.
  - why_faster: the mechanism the source gives — aliasing guarantees
    (Fortran/Rust noalias), bounds-check elision, better codegen, a runtime
    (GC, JIT), array semantics (APL/Fortran), lack of exceptions, etc.
    "the language is just faster" with no mechanism caps the tier at C.
  - Set language_level_claim=true when the claim is about the language or
    compiler itself rather than a specific library.
Historical languages (BCPL, Oberon, Modula-2, early Pascal, Forth) rarely
have benchmarks against modern C; record them as usability=reference with
whatever the source claims, tier C or D, and note in caveats which era of
hardware/compiler the comparison was made on.
```

## C. Schema keys (insert after `compared_against_cpp_std_directly`)

```
    "language_level_claim": true | false,
    "same_algorithm": true | false | null,
    "same_opt_level": true | false | null,
    "why_faster": "mechanism stated by the source, or null",
```

## D. Wave 13 — assembly-simd-kernels-and-wasm

| Category | Baselines |
|---|---|
| hand-written-asm-kernels | the compiler's -O3 output for the same C/C++ function; the libc/stdlib version (memcpy, memcmp, strlen, memset) |
| simd-intrinsics-libraries | scalar C/C++ reference, Highway, xsimd, Eigen, std::simd |
| asm-level-string-and-memory | glibc/musl string.h, std::string ops |
| assemblers-and-asm-tooling | GNU as, NASM, MASM (assemble time, output quality) |
| wasm-runtimes-and-compilers | wasmtime, wasmer, V8, WAMR, wasm-opt |
| wasm-libraries-and-apps | the same library compiled natively; the JS equivalent in-browser |
| assemblyscript-and-wasm-langs | TypeScript/JS in V8, C++ via Emscripten |

Note for this wave: hand-written assembly rarely ships a benchmark against `-O3` compiler output; agents should tier such claims C unless the repo includes the C reference and a harness. Anything targeting only one microarchitecture must record it in `hardware` and get a `tradeoffs` note about portability.

## E. Wave 14 — other-languages-faster-than-c-cpp-asm

The baseline for every category here is the same task in C or C++ at -O3 (or hand-written asm where the source compares to that). Two kinds of entry: a **library** in language L that beats the C/C++ equivalent, and a **language-level** claim that L's compiler emits faster code for a class of programs. Both are valid; `language_level_claim` distinguishes them.

| Category | Languages to sweep | Where they tend to win |
|---|---|---|
| numerics-and-arrays | Fortran, Julia, Chapel, Futhark, Halide, ISPC, APL/BQN/K, Mojo | aliasing guarantees, array semantics, auto-vectorization, GPU codegen |
| systems-and-safety | Ada/SPARK, Rust, Zig, D, Nim, Odin, C3, Carbon | bounds-check elision with proofs, noalias, comptime specialization, no-exception codegen |
| runtime-jit-beats-aot | Java/HotSpot, .NET, LuaJIT, SBCL (Common Lisp), OCaml (flambda), Julia | profile-guided inlining, escape analysis, specialization on runtime types |
| concurrency-runtimes | Go, Erlang/BEAM, Pony, Rust (tokio), Kotlin coroutines | scheduler design, message passing, cheap green threads |
| web-and-serving | Rust, Go, Zig, Java, .NET, Crystal (vs C/C++ servers) | TechEmpower-style throughput/latency |
| string-and-text | Rust, Go, Zig, Nim, Odin | UTF-8-native strings, SIMD stdlib |
| historical-and-minimal | BCPL, Oberon, Modula-2, Pascal/Free Pascal, Forth, PL/M | mostly reference-only; compile speed, code size, simplicity claims |

Baselines for language-level claims: the C/C++ implementation in the same benchmark suite (Benchmarks Game, kostya/benchmarks, plb2, Are We Fast Yet, TechEmpower). Record the suite and the exact benchmark name; a language beating C on `nbody` and losing on `regex-redux` is one row per benchmark, not "faster than C."

## F. Seed-list mining

Curated "awesome" lists, GitHub topic pages, and trending pages are dense candidate generators, but they are NOT evidence: an entry on awesome-cpp tells you a project exists and roughly what it claims, nothing about whether it beats a baseline. So they get their own agent type that emits **seeds**, not catalog entries. Seeds are handed to the Part 2 search agents as `{SEED_QUERY}` inputs with the repo URL pre-filled, which skips the discovery step and spends the search agent's budget on finding evidence.

### Seed sources

Static curated lists (mine once, re-mine quarterly):
| Source | What it holds | Mining notes |
|---|---|---|
| https://github.com/fffaraz/awesome-cpp | ~1500 C/C++ libraries by category, inline license tags, many performance claims in descriptions | Highest-yield single source. Categories map almost 1:1 to waves 1, 3, 4, 5, 6, 7, 8, 9, 10, 11. Also has a "Standard Libraries" section listing whole stdlib replacements (EASTL, ETL, micron.cpp, rpp, itlib) — those are wave-1 candidates in their own right. |
| https://awesomecpp.com | Web mirror of awesome-cpp | Skip if awesome-cpp already mined; use only as a fallback if GitHub rate-limits |
| https://github.com/oz123/awesome-c | C libraries by category, license tags | Same approach as awesome-cpp; C entries are especially valuable because they're usually copyable into any language via FFI |
| https://www.reddit.com/r/C_Programming/comments/83s7o8/awesome_c_a_curated_list_of_c_good_stuff/ | Discussion thread about awesome-c | Mine the comments for libraries people say are missing or better; the thread itself is not evidence |
| https://github.com/Maijin/awesome-asm | Assembly resources, tools, tutorials | Wave 13. Mostly learning material; pick out actual kernel/library repos |
| https://github.com/yifengyou/awesome-asm | Assembly resources (overlaps Maijin) | Dedup against Maijin list first |
| https://github.com/Hack-Labs/awesome-assembler | Assemblers and asm tooling | Wave 13 assemblers-and-asm-tooling |
| https://github.com/mcuking/Awesome-WebAssembly-Applications | WASM apps and libraries | Wave 13 wasm-libraries-and-apps; many are ports of native libs, so pair each with its native original as the baseline |
| https://github.com/AssemblyScript/examples | AssemblyScript sample projects | Wave 13; low yield for "faster than" but good for the JS-vs-WASM baseline pairing |

Per-language curated lists (wave 14 and cross-language entries in other waves; mine once, re-mine quarterly). Agents should locate each by searching its name and confirming the repo before mining — do not construct URLs from memory:
| List | Language | Notes |
|---|---|---|
| ohmyzsh/awesome-ada | Ada/SPARK | Sections on containers, parsing, web, crypto; SPARK-proven code is often bounds-check-free |
| rabbiabram/awesome-fortran (and "Fortran-lang" packages index) | Fortran | Numerics, BLAS/LAPACK-adjacent, stdlib project |
| rust-unofficial/awesome-rust | Rust | Very large; shard by section like awesome-cpp |
| awesome-zig (several forks; pick the most-starred) | Zig | Allocators, parsers, SIMD |
| dlang-community/awesome-d | D | Containers, parsers, mir numerics |
| xflywind/awesome-nim (or ringabout/awesome-nim) | Nim | Allocators, parsers, macros-driven specialization |
| awesome-odin, awesome-c3, awesome-carbon (search; small) | Odin, C3, Carbon | Low yield now; re-mine as they grow |
| svaksha/Julia.jl | Julia | Numerics, autodiff, DataFrames |
| avelino/awesome-go | Go | Networking, servers, serialization |
| ocaml-community/awesome-ocaml | OCaml | Parsers, flambda codegen claims |
| CodyReichert/awesome-cl | Common Lisp | SBCL numerics and codegen |
| awesome-apl / awesome-bqn / awesome-k (search; small) | APL, BQN, K | Array-language performance on data workloads |
| chapel-lang, futhark-lang, halide-lang org repos | Chapel, Futhark, Halide, ISPC | Compilers that target GPU/SIMD; compare against hand-tuned C/CUDA |
| awesome-forth (search), Martin Richards' BCPL distribution, Oberon/Modula-2 archives | Forth, BCPL, Oberon | Historical; reference-only. Mine for algorithms and compiler techniques, not benchmarks |

Cross-language benchmark suites (mine the results tables, not the READMEs; each row where a non-C/C++ entry beats the C/C++ entry is a seed):
| Suite | What it compares |
|---|---|
| The Computer Language Benchmarks Game (search "benchmarksgame") | ~10 toy programs across ~30 languages; per-program results, fastest submission per language |
| kostya/benchmarks | Language shootout on brainfuck, base64, JSON, matmul, havlak, etc. |
| attractivechaos/plb2 | Sorting, matmul, nqueens, bedcov across languages |
| smarr/are-we-fast-yet | Cross-language benchmark suite with identical algorithms — closest to a fair language-level comparison |
| TechEmpower/FrameworkBenchmarks | Web frameworks across languages: plaintext, JSON, DB queries, fortunes |
| "programming-language-benchmarks" (search; several projects use this name) | Newer suites; check which are maintained |

Dynamic pages (re-mine on a schedule; contents change daily):
| Source | Cadence | Notes |
|---|---|---|
| https://github.com/trending/assembly | weekly | Trending is a popularity signal, not a performance one; useful for catching new hand-written kernels early |
| https://github.com/topics/assembly-language?l=html | weekly | Note the `?l=html` filter is probably unintentional — mine `/topics/assembly-language`, `/topics/simd`, `/topics/avx2`, `/topics/avx512`, `/topics/neon`, `/topics/webassembly` with no language filter, sorted by stars and by recently-updated |
| GitHub topics for each wave (`/topics/hash-table`, `/topics/json-parser`, `/topics/http-server`, `/topics/compression`, `/topics/regex`, etc.) | per wave, then monthly | Derive the topic list from the Part 3/4 category names |

### Mining agent prompt

Use Haiku. One source × one section per call for the big lists (awesome-cpp has ~50 sections; give each agent one section). Output is a JSON array of seeds.

```
You are mining a curated list to produce SEED CANDIDATES for a catalog of
implementations that are faster than a default/incumbent tool. You are NOT
evaluating evidence and NOT deciding whether anything is actually fast. You
are extracting every entry that might plausibly qualify, with enough
metadata that a later agent can go look for proof.

Today's date: {TODAY}
Source URL:   {SOURCE_URL}
Section:      {SECTION}            (e.g. "Containers", "JSON", "all")
Skip list:    {KNOWN_LIST}         (canonical repo URLs already catalogued or seeded)

=====================================================================
PROCESS
=====================================================================
1. Open {SOURCE_URL}. Navigate to {SECTION}. If the page is a GitHub
   topic or trending page, iterate at least 3 pages of results.
2. For EVERY entry in the section, decide: could this plausibly be
   catalogued as faster than some baseline? Include it if ANY of these:
   - the description contains a performance claim (fast, fastest,
     high-performance, outperforms, faster than, low-latency,
     zero-copy, SIMD, lock-free, drop-in replacement, optimized, ⚡)
   - the category itself is performance-sensitive (containers, hash
     maps, sorting, JSON, compression, regex, allocators, networking,
     parsing, math/linear algebra, crypto/hashing, image codecs, logging)
   - it is a whole-stdlib or whole-libc replacement (EASTL-like)
   - it is a hand-written asm/SIMD kernel or a WASM port of a native lib
   Exclude only entries that are clearly out of scope: GUI toolkits,
   game engines, IDEs, books, tutorials, blogs, job boards, and anything
   whose job has no performance dimension (e.g. a coding-style guide).
   When in doubt, include; a bad seed costs one cheap search-agent run.
3. For each included entry, map it to a wave and category from the
   catalog taxonomy and guess the baseline it would be compared against.
   These are guesses; mark confidence accordingly.
4. Extract the license tag if the list provides one inline (awesome-cpp
   and awesome-c do: "[MIT]", "[Boost]", etc.). Do not open the repo to
   look for one — that is the search agent's job.
5. Skip anything whose canonical URL is in the skip list.

=====================================================================
HARD RULES
=====================================================================
- Do not open the individual repos. Mine only the list page. Volume and
  coverage matter here; verification happens downstream.
- Copy URLs exactly as they appear. Do not fix, guess, or canonicalize
  beyond stripping tracking parameters.
- Do not assign an evidence tier. That field does not exist at this
  stage.
- Output ONLY the JSON array.

=====================================================================
OUTPUT SCHEMA
=====================================================================
[
  {
    "name": "string",
    "repo_url": "string",
    "listed_description": "the list's own one-line description, verbatim",
    "listed_license": "SPDX-ish tag from the list, or null",
    "performance_claim_in_description": true | false,
    "claim_text": "the specific words that signal a claim, or null",
    "guessed_wave": "e.g. stdlib-replacements",
    "guessed_category": "e.g. hash-maps-sets",
    "guessed_baseline": "e.g. std::unordered_map, or null",
    "found_in": "{SOURCE_URL}#{SECTION}",
    "confidence": 0.0-1.0
  }
]
```

### What the orchestrator does with seeds

1. Dedup seeds by canonical URL against each other and against the known-list.
2. Group by `guessed_wave`. Each seed becomes a Part 2 search-agent job with `{SEED_QUERY}` = the repo URL and the search agent's step 1 replaced by "open this repo directly." Everything else in Part 2 (evidence tiers, schema, hard rules) applies unchanged.
3. Seeds with `performance_claim_in_description: true` go first in the queue; the rest are lower priority and can be batched to fill spare capacity.
4. A seed that the search agent cannot find any baseline comparison for is not dropped: it is recorded in a `SEEDS_NO_EVIDENCE.md` list with its listed description, so a later wave or a human can revisit. Awesome-list presence plus a performance claim in the description is worth keeping as a lead even with zero evidence.
5. Whole-stdlib replacements found in the "Standard Libraries" and "Frameworks" sections (EASTL, ETL, micron.cpp, rpp, itlib, Coost, sfl) get a special treatment: they are decomposed into per-facility entries by the search agent (EASTL's hash map, EASTL's vector, EASTL's sort) since a whole-library speedup claim is unverifiable but a per-container one is.
