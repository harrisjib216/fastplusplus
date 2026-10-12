# Queue: extensions saved for the end

## Unfinished work (resume here first; updated 2026-10-13)

This section is the open backlog from the main wave loop. It is not an extension; run it before the
extension passes further down. Waves 1-14 are closed (see docs/build-log.md); extensions 2-4 below are done. The backlog seed sweep of
2026-10-07 seeded every uncatalogued lead with a reachable repo from waves 8-12 (29 projects, 22 verified,
4 duplicates), so what remains here is blocked on the environment or on the user:

1. **RetroWrite (wave 11) enrichment**: `data/wave11/enrich/prompts/github_com_hexhive_retrowrite.txt` has no
   `enrich/raw` file because its enricher was stopped by a safety classifier mid-write on 2026-10-06. Ask the
   user before relaunching; when relaunched, run `render_lists.py` again so the "missing enrichment" note clears.
2. **Paper-access retiers** (need an environment that reaches arXiv, ACM, IEEE, Springer, usenix, Dagstuhl,
   IACR ePrint, openproceedings, TUM, Saarland, STFC and the other hosts named in each wave's leads.md): wave 8
   (ttm, costa, pargeo, nicslu, spral, openequivariance, wrs, m4ri, amgt, tilespmv, kokkos-kernels, gpunufft,
   avxbls-sig ePrint 2026/947, SpLLT STFC papers, plus the older list in `data/wave8/leads.md`); wave 9 (h0_bv,
   spider, recoil, ds2i, mutable_rank_select, pwm, wavelet_forest, faster-minuter, avxwindowfmindex, mans, ZipNN,
   QPL, CPEF, simdcomp, DietGPU, bzip2gpu ICPP 2024, Chromium zlib via simonis/zlib-chromium); wave 10 (vvdec
   FOSDEM handout, Helix threads, IPOL, PCS2025 jpegli, libjpeg-turbo thread, aras-p bcdec charts, Kvazaar Jetson
   paper, BoofCV Performance page and SURF paper); wave 11 (Exgen-Malloc, SpeedMalloc, LWMalloc, LLFree, Dr. Memory,
   Coz, RFUSE, TriCache, UMap, NOVA, WineFS, SplitFS, vmcache, xNVMe, DAXFS, libseff, Nowa, Heartbeat, RetroWrite,
   SPDK); wave 12 (Instrew VEE'21, TPDE, Box64 EuroSys, aWsm, WARP, rv32emu VMIL, HHVM, Deegen, Pallene, YJIT,
   Wizard OOPSLA 2022 paper, mutable EDBT 2023 and ADC 2023 arXiv 2311.04692, Higgs arXiv 1507.02437, weval PLDI,
   riscv-sbt, Segue/ColorGuard ASPLOS 2025, LC thesis cross-check).
3. **Thin-yield searches queued for a re-run** from an environment that reaches HN Algolia, news.ycombinator.com
   and personal blogs: the b7/b8 assignments of waves 8-12 (`w{8..12}-*-{blogs,hn}`), which ran on WebSearch
   snippets plus github.com.
4. **Seed leads still unseeded** (no reachable repo, or surfaced after the sweep): wave 8 gMAGNUS (no repo), AVXPoS
   (ePrint 2026/1827, repo not found); wave 9 emmanuel-marty/em_inflate, smalLZ4, jibsen/blz4, LZ4X, Apple LZMESH
   (no repo), Tessil/sparse-map and other hash-map leads (wave 1 backfill), aditya12agd5/cuda_bzip2; wave 10 Vship
   (codeberg, blocked), Getreuer IPOL survey (ipol.im blocked), BlazeDiff (teimurjan/blazediff), ESP32_JPEG
   (precompiled), rav1d (slower than dav1d), mycophonic/flac, catid/Zdepth; wave 12 Wastrel (codeberg), treVM and
   Biotite (repos unknown), ClangJIT, Pycket (pycket/pycket), QMDB (LayerZero-Labs/qmdb, wave 5), asllvm (no
   numbers), Hazelight StaticJIT (gated). Repo_url overrides to consider: kostya/topaz (the fork that was measured),
   lmcad-unicamp/riscv-sbt (redirect), mpsops/mps-flash-attention (moved, folded into metal-flash-attention).
5. **Harness re-runs that would settle disputes** (need a build machine): HarfBuzz benchmark-shape with
   -Dkbts=enabled on kb v2.28, pillow-lunasvg against a release-profile resvg, libblur and kornia-rs against a
   pinned OpenCV build, bcn_decoder_tester on current bcdec and ConvectionKernels, ThePhD/lua-bindings-shootout for
   LuaBridge3 vs sol2, a JIT_NO_SUSPEND run of the AngelScript JIT, kvmserver's Wasmtime and isolated-vm groups for
   TinyKVM, a randomised-key memtier run for bluebox, an AVX2 randompack build for zurand.
6. **Cross-wave leads from wave 12 enrichers** (seed candidates for the named waves): radfordneal/xsum and
   radfordneal/matprod (wave 8 numerics), 6/qj (wave 4 json), eBay/tsv-utils (wave 3 csv-tabular), Turso Rust
   SQLite rewrite and QMDB (wave 5 databases), ml-rust/splintr (tokenizers), lmcad-unicamp/MOSFHET (crypto),
   klippa-app/go-pdfium wazero-vs-wazy benchmark (wasm cross-check).
7. **Usage-limit lesson:** 15-20 Opus or Sonnet agents at once exhausted the session limit on 2026-10-02 and
   again on 2026-10-06 (nine enrichers killed mid-run; their complete output files were kept). 8-12 at a time,
   recording each report before launching more, runs a full day without a kill.

Closed waves, for reference: wave 8 (398 then 401 verified), wave 9 (136 then 141), wave 10 (254 then 265),
wave 11 (144 then 145), wave 12 (220 then 227), wave 13 (303), wave 14 (274); details in docs/build-log.md.
Seed sweep of the wave 13-14 leads done 2026-10-13 (61 verified; see docs/build-log.md). Still open from it: ParlayLib, io-uring-echo-server, kbench9000, morton-nd, zp7, dSFMT_AVX512, amoeba, weaviate/sroar, NeuralAmpModeler-rs, MADDNESS (paper: id in dblalock/bolt), secpoline, and the paper-access retiers for OpenCilk, Lace, block-aligner, ish, sylph, aes-armcortexm, lazypoline, bolt and ksw2.
Added 2026-10-13: paper-access retiers for waves 13-14 (Savina TACO 2023, Rewrite-it-in-Rust CBET paper, NPB-Rust
arXiv 2502.15536, ixy ANCS 2019, Perceus TR cross-check) and the seed leads in `data/wave13/leads.md` and
`data/wave14/leads.md` (zipgrep, megadepth, sylph, zimdjson, Singeli, copia, armeria, hunt-rs, uutils/findutils,
noodles, dSFMT, zspell, sroar, zawk, qulacs, block-aligner, Verstable, daachorse, redcon.c, gnet, Dart AOT and Free
Pascal benchLANG/compiler-benchmark rows, and others) join items 2 and 4 above.

## Presentation: make the repo beautiful and useful for agents (added 2026-10-03)

Not part of the wave loop. Run it once waves 9-12 are in, or earlier if the user pulls it forward.
Each item is a separate PR against main.

**Status 2026-10-12 (public-release pass):** done: 1 (README with generated blocks), 2 (`catalog/catalog.jsonl`,
`catalog/catalog.csv`, `docs/schema.md`), 3 (`AGENTS.md`, `llms.txt`), 4 without the written category intros
(category pages show the spec's baselines; the 3-5 sentence section-writer intros are still open), 6, and 7
except CODEOWNERS (`CONTRIBUTING.md`, issue forms, PR template, CI that re-renders and runs
`pipeline/check_pii.py`). Open: 5 (static site; the user deferred it), 8 (freshness action), 9 (quality lint).
Also open: `paper:speedmalloc` is verified in both wave 1 and wave 11; the renderer keeps the wave 11 record.

1. **Landing README.** One screen: what the catalog is, how entries are tiered, the three lists,
   how to cite an entry, and a "for agents" block that points at the machine-readable files
   below. Badges for entry counts (generated by `render_lists.py`), last-updated date, license.
2. **Machine-readable exports.** `render_lists.py` also writes `catalog.json` (every verified
   entry with its enrichment, decision, shortcomings and measurements) and `catalog.csv` (one row
   per entry: name, repo, category, tier, baseline, speedup, usability, license, last_commit).
   Stable ids and a documented schema in `docs/SCHEMA.md`.
3. **Agent entry points.** `llms.txt` and `AGENTS.md` at the repo root: how an agent should
   query the catalog (grep patterns, the JSON paths, tier semantics, the "when not to use"
   field), and the rule that shortcomings are part of the answer, not footnotes. Keep both under
   200 lines so they fit in a prompt.
4. **Per-category pages.** `docs/<domain>/<category>.md` with a 3-5 sentence intro (what the
   baseline's weakness is, what the design space looks like), the entries ordered by tier then
   breadth of win, and a comparison table (speedup, workload, hardware, tier). This is the spec's
   "section writer" stage; render from data, never hand-edit.
5. **Static site.** GitHub Pages from `docs/` (MkDocs Material or plain Jekyll): search box,
   tier and category filters, one page per entry, dark mode. No build step beyond
   `render_lists.py` plus the site generator; CI publishes on push to main.
6. **Entry template polish.** Consistent headings across COPYABLE.md and REFERENCE.md, a
   one-line verdict at the top of each entry, collapsed `<details>` for the long shortcomings
   lists, and a link to the raw verification record.
7. **Contributing and governance.** `CONTRIBUTING.md` (how to propose an entry: open an issue
   with the schema fields, or a PR adding a seed record; what evidence tiers require; the
   keep-and-document rule), a PR template, a CODEOWNERS file, and issue templates for "new
   entry", "wrong number", "retier request".
8. **Freshness.** A monthly GitHub Action that re-checks `last_commit`, stars and archive status
   for every entry via the GitHub API and opens a PR with the diff, so maintenance_status stays
   honest without a full wave.
9. **Quality pass.** A script that lints entries: missing license, benchmark_url that 404s,
   speedup text with no number, enrichment confidence under 0.5. Output feeds the next retier
   pass.

---

Extensions extracted from a later rewrite of the spec (2026-09-25). They are **not active**: the spec
(`faster-than-std-agent-prompt.md`), the pipeline scripts and the records in `data/` stay as they are until
waves 3–12 finish. Everything below is additive and runs as its own pass at the end.

The rewrite was built on the original spec, so its tier definitions, 15–25 call budget, max 8 entries and
"verification recommended" were dropped here on purpose; the current spec's rules win.

## Order

1. **Seed-list mining, static lists** (section F): DONE 2026-10-11 (rounds 1 and 2: 152 groups, 266 verified, 637
   no-evidence seeds; see docs/build-log.md). Remaining per-list leads are in each wave's leads.md.
2. **Whole-stdlib decomposition** (end of section F): DONE 2026-10-13 as wave 1 stdlib seeds (10 entries enriched;
   `data/wave1/raw/w1-seed-stdlib-{a,b}.json`).
3. **Wave 13 — assembly-simd-kernels-and-wasm** (section D): DONE 2026-10-12 (303 verified, all enriched; see
   docs/build-log.md 2026-10-13).
4. **Wave 14 — other-languages-faster-than-c-cpp-asm** (section E): DONE 2026-10-13 (274 verified, all enriched;
   open paper-access retiers and seed leads in `data/wave14/leads.md`).
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
