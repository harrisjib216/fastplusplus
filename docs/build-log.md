# Build log

Status notes the orchestrating Claude Code session wrote at the close of each wave and backfill round, newest
first. Counts are as of each note; the live counts are in the [README](../README.md). The project rules these notes
refer to are in [CLAUDE.md](../CLAUDE.md), and the open backlog is in [QUEUE.md](QUEUE.md).

## Status (2026-10-13, seed sweep)

- Seed sweep of the wave 13 and 14 enricher leads closed 2026-10-13: 13 seed groups across ten waves (w1-seed-c,
  w3-seed-a, w5-seed-b, w6-seed-b, w7-seed-b, w8-seed-n, w10-seed-g, w11-seed-b, w13-seed-a/b, w14-seed-a/b/c; 64
  projects), 61 new verified entries, all enriched; duplicates leancrypto (PQRV kernels) and go-cv-simd (c2goasm of
  ermig1979/Simd); isa-l_crypto folded into its wave 7 entry; FreeBSD libmd carries a `paper:` id (freebsd-src is
  listed in wave 5). Lists: COPYABLE 2748, REFERENCE 265, REJECTED 41; 3014 verified (A 600, B 483, C 1671, D 260).
  Tier moves: grpc_bench rows to C (Pekko gRPC, Armeria, Vert.x gRPC, grpc-dotnet, grpc-go, tonic: cpp_grpc_mt
  pre-posts one call per completion queue, gRPC's own server 5000), parasail A to C (SSW timer includes FASTA
  parsing), Hare compile throughput A to C (stdlib cache reused across runs), noodles A to B, sylph and
  block-aligner B to C, Lace C to D, zspell D to C, ish, Quicker ADC C to B, pixman C to A (RVV commit benchmark).
  An org spend-limit kill mid-sweep killed 13 agents; all were relaunched after the restore of each wave's
  original `today` (see Lessons).

## Status (2026-10-13)

- Waves 13 and 14 closed and the single enrichment pass (wave 1 stdlib seeds, wave 13, wave 14) finished on
  2026-10-13; QUEUE extensions 2 (whole-stdlib decomposition, run as wave 1 stdlib seeds: 10 entries), 3 (wave 13)
  and 4 (wave 14) are done. Lists: COPYABLE 2689, REFERENCE 263, REJECTED 41; tiers A 594, B 475, C 1638, D 245;
  2953 verified entries across all waves, every one enriched except RetroWrite (user hold); SEEDS_NO_EVIDENCE 620.
  Every category sits in one domain (cafs-lib needed a `domain` override to stdlib-replacements). Next: QUEUE
  extensions 5-6 (per-language curated lists, dynamic pages), the paper-access retiers and thin-yield re-runs
  listed in QUEUE.md "Unfinished work", and the presentation pass.
- Wave 13 (assembly-simd-kernels-and-wasm) closed 2026-10-12: 56 raw files (b1-b8 for all 7 categories plus seed
  passes), 344 merged, 118 verify batches, 303 verified (A 43, B 21, C 187, D 52; copyable 270, reference 30,
  mixed 3; wasm-libraries-and-apps 73, simd-intrinsics-libraries 58, assemblyscript-and-wasm-langs 46,
  hand-written-asm-kernels 45, asm-level-string-and-memory 34, assemblers-and-asm-tooling 32,
  wasm-runtimes-and-compilers 6, plus 9 filed in other waves' categories by override), 37 duplicates, 3 rejects for
  invalid evidence (tslime/simdmatrixalgorithm computes wrong answers; unconfirmedlabs/bcs measures TypeScript
  codegen while the bcs-zig wasm build is never called, Go-stdlib-libp2p precedent; industrial-algebra/orlando
  README table predates any benchmark, r8e precedent). Retier files retier-01 (2), retier-02 (1) and the
  enricher-driven retier-03 (156 entries): up to A dioxus, iced, simd-radix-sort, yaxpeax-x86, cafs-lib,
  positional-popcount, pqm4, corvus, neon-ntt, ultraviolet, quickenshtein, ermig1979/Simd, udis86, BLAKE3; to B
  bls-eth-wasm, ispc, loro, validateutf8-experiments, minotaur, source-map, rust-dominator, leptos,
  ppopp2017_artifact, vectorvisor, stoke, sycamore, unison, wasm-bindgen, faster-utf8-validator; 68 moved to C
  (asymmetric flags, first-party provenance gaps, numbers on code later fixed: fastnoise2, almide,
  parallelreductionsbenchmark, libgcrypt, libco, absurd-sql, argminmax, diamond-types, md5-simd, constantine,
  nasm, tinymembench, markdown-wasm, wasmtime-mte, simd-sort, uasm and others); 33 to D (no valid measurement,
  degenerate workloads, stale or never-run numbers: supercoder, memcpy_benchmark, ttf2woff2-wasm, faster,
  kmstrsearch, intel-intrinsics, mmemmove, brepkit, wasm-runtime-performance, ai-kernel-optimizer, tar-wasm,
  md5-wasm, memcpy_fast, clipper2-wasm, alphadev, sax-wasm, autozig, webmscore, wasmboy, camaro and others).
- Wave 14 (other-languages-faster-than-c-cpp-asm) closed 2026-10-13: 48 raw files (b1-b8 for all 6 active
  categories; historical-and-minimal yielded nothing cataloguable), 324 merged, 110 verify batches (107 files after
  deletions and re-renders), 274 verified (A 63, B 16, C 139, D 56 after enrichment; the verifier stage ended at
  A 73, B 21, C 157, D 23; copyable 254, reference 20; systems-and-safety 62, string-and-text 57, web-and-serving
  53, runtime-jit-beats-aot 45, numerics-and-arrays 35, concurrency-runtimes 21, one http-servers-frameworks by
  override), 49 duplicates (second claims on listed repos carry `paper:` ids), 1 reject (dev0x13/gemm-benchmark-2023
  Mojo kernels do not compute a full GEMM). Record ids are `lang:<language>/<owner>/<repo>#<benchmark>`, one row per
  benchmark. Enricher-driven retier-01 (274 entries): to D rust-sort, zog, statico, fastGPT, EvoTrees.jl, monolake,
  ziggit, ranwalk, SymbolicUtils.jl, FFTA.jl, Platinum Searcher, wut-server, awkrs, DiffEqGPU.jl, Traefik, PDFOxide,
  xerg, during, related_post_gen (C3, D and Rust rows), Chapel fbench, Erlang and Go thread-ring, yosssi
  Go-vs-nginx gist, JuliaLang Microbenchmarks userfunc_mandelbrot (Fortran and Julia rows: the project's own 2026
  data shows parity), xemantic almost-pseudo-random, alya Bun binary trees, AcceleratedKernels LJG, Lingua Franca
  Savina (actor-system startup charged to the CAF and Akka baselines only), Pony message ring (the Pony example
  runs one of its repetitions), c-blake dups (author's own like-mode run has jdupes faster); to C sambamba,
  llama2.zig, zipir, Futhark, zroar, hpla-rs, ioxide, needletail, PowPow, Kairos, Thruster, TrueAsync, libbzip2-rs,
  Undertow, JSON3.jl, Koka cfold (C++ port copies the spine per Add), OCaml benchLANG binary trees (C frees inside
  the timer, OCaml never collects), rustc compile throughput (unlocked rustup switches mid-run); up to A fib; to B
  hist-rs, hck, runiq. Name correction: kostya/jit-benchmarks k-nucleotide measures the OpenResty luajit2 fork.
  Category override bitdp to string-and-text. Open: paper-access retiers and seed leads in data/wave14/leads.md
  (Savina TACO 2023, Rewrite-it-in-Rust CBET paper, NPB-Rust arXiv 2502.15536, ixy ANCS 2019, plus the second-claim
  and project leads listed there).

## Status (2026-10-11)

- QUEUE extension 1 (seed-list mining, awesome-cpp and awesome-c, rounds 1 and 2) closed 2026-10-11: 152 seed groups
  (`data/waveN/raw/wN-mine-*.json`, about 7 seeds each), 324 raw records, 266 verified (A 39, B 41, C 153, D 33; wave 1
  68, wave 8 37, wave 11 26, wave 5 27, wave 4 28, wave 6 17, wave 10 18, wave 3 15, wave 12 11, wave 7 8, wave 9 6,
  wave 2 5), 637 no-evidence seeds in `data/seeds/no_evidence/` rendered to SEEDS_NO_EVIDENCE.md (620 after dedup).
  Lists: COPYABLE 2155, REFERENCE 210, REJECTED 36; tiers A 486, B 438, C 1309, D 132. Every verified entry is
  enriched except RetroWrite (user hold). Round 2 (2026-10-11) ran under the user's order "searches and verifies
  first, enrichment at the very end": 23 backfill groups (w10-mine-m to t, w11-mine-e to o, w12-mine-d to g), 26
  verify batches (w7 54-55, w8 172-179, w9 67, w10 112-119, w11 56-62, w12 98-100), then one enrichment pass of
  37 Opus pairs (73 entries across waves 5-12). Enricher-driven retiers from that pass: down PostgreSQL, MySQL and
  ODB to D (cross-run comparisons), Crypto++ and Botan to D (harness UB; OpenSSL re-keyed per message), clBLAS to D,
  ThreadPool to D (degenerate benchmark), GStreamer B to C (single-threaded FFmpeg baseline), Psi4 B to C, SHOGUN
  B to C (unequal k-means work, later rewritten), PEGTL B to C (stale cached build), TensorFlow B to C (asymmetric
  DLPerf harness), libfacedetection A to C (numbers predate PR #383), Box2D A to C, ONNX Runtime A to C, Ultimate++
  A to C, Boost.Log B to C, OpenEXR A to B; up G3log B to A (Quill benchmark), Sophia D to C (Howard Chu gist),
  MuJS C to B. Retier files: w5 retier-03, w6 retier-03/04, w7 retier-03, w8 retier-18, w9 retier-08, w10
  retier-40, w11 retier-05, w12 retier-02. Second claims on already-listed repos (FFmpeg ffvp9, OpenCV DNN,
  Boost.Fiber, icey, oneTBB parallel reduce, AngelScript, ChakraCore, pocketpy, QuickJS re-seeds) carry `paper:`
  ids with decision `duplicate`. Domain overrides now keep every category inside one domain. Next: QUEUE
  extension 2 (whole-stdlib decomposition), then waves 13-14.

## Status (2026-10-06, kept for history)

- Waves 1-12 are finished except the open items below. Lists after the 2026-10-07 backlog seed sweep: COPYABLE 1905,
  REFERENCE 202, REJECTED 34. The next open work is in QUEUE.md "Unfinished work" (wave 11 seed leads and the
  RetroWrite enrichment, wave 12 seed leads and paper-access retiers in data/wave12/leads.md; then the
  QUEUE extensions: waves 13-14, cross-language claims, presentation).
- Backlog seed sweep (2026-10-07, QUEUE "Unfinished work"): 29 uncatalogued leads from data/wave{8,9,10,11,12}/leads.md
  seeded in one pass (w8-seed-m, w9-seed-d, w10-seed-e/f, w11-seed-a, w12-seed-e; 6 Sonnet agents), 12 verify batches
  (w8 162-163, w9 63, w10 104-107, w11 50, w12 92-94), 22 verified and enriched, 4 duplicates (mps-flash-attention is a
  binding of metal-flash-attention, YAFU shares avx-ecm's only claim, goant is a Go port of ant, dsx-ai-factory/
  model-streamer is the renamed run-ai repo, recorded with a repo_url correction), 0 rejects. New A entries:
  tsl::array_map (wave 9, hash-maps-sets by category override), ConvectionKernels (wave 10), evm.zig (wave 12); B:
  JPEGDEC, hxcpp, Cuik; C or D for the rest (bluebox, zurand, SpLLT, bzip2gpu, DeLZSA repo 404, zenquant not faster,
  BoofCV, Canvas-Txt, nssfactory, honeydiff withdrawn 6x, Simd slower than OpenCV in user issues, scany, clownresampler,
  angelsea, Box86, FAFO). Enricher-driven retiers: avxbls-sig B to C (harness compares SwiftEC hashing against blst's
  SSWU), LC A to C (warm second run vs cold baselines, generic-arithmetic prefixes), AssemblyScript-style caveat
  corrections for hxcpp (JS rows double-counted), zurand (randompack built without AVX2), evm.zig (mock-host storage
  rows, stale baseline versions), BoofCV (unequal kernels), Canvas-Txt (cached mode, UAX-29 breaks), nssfactory
  (bm3dcuda BM3Dv2 ambiguity), JPEGDEC (TJpgDec not at its fastest; open OOB write #119), bzip2gpu (stateless RLE1
  decoder, CRC unchecked), Simd, FAFO (precomputed write sets), Box86 (stale). Retier files: wave8 retier-15, wave9
  retier-06, wave10 retier-39, wave11 retier-02, wave12 retier-01. Wave-aware helper copies (WAVE=N) of check_ids,
  addretier, gen_enrich and mk_verify live in the scratchpad; gen_enrich must skip prompts of entries later marked
  duplicate (stale prompts for maskedvbyte, iczelia/bzip3 and nanorand-rs were deleted). RetroWrite (wave 11) still
  needs the user's go before its enricher is relaunched.
- Wave 12 (interpreters-and-vms) closed 2026-10-06 in one cloud session: searches b1-b8 for all 4 categories
  (32 raw files; b7/b8 on WebSearch snippets plus github.com since blogs and HN were blocked, 36 records) plus
  seed-a..d (28 lead projects); 239 merged, 90 verify batches with 236 verdicts (confirm 209, downgrade 22,
  reject 5), 220 verified (A 38, B 62, C 112, D 8; copyable 214, reference 3, mixed 3; jits 57,
  embedded-scripting 56, bytecode-vms-and-wasm 53, language-interpreters 50, plus 4 filed by category override),
  every verified entry enriched. Rejected for invalid evidence: R8/NoClip (interpreter pattern-matches the
  benchmark's function names and replaces them with fused native loops, hard-coded pass_hash), wazero (PolkaVM
  benchtool compile row hits an in-memory module cache; MQF precedent), Pipa (RegExp suite fast path does a
  literal find, no regex runs; stb-zip precedent), r8e (memory figures are design targets copied from
  ARCHITECTURE.md) and zig-evm (README 5-6x table is a hard-coded array in src/benchmark_demo.zig; zokio
  precedent). 14 duplicates: LuaJIT Remake second id, libriscv second id, lua-aot and quickjs-ng suffixed ids,
  wasm-compiler suffix, rquickjs, bare, zig-mquickjs, OpenResty luajit2 (fork of LuaJIT with an anecdote only),
  fastschema/qjs (quickjs-ng on wazero), go-quickjs (Go port of quickjs-ng), ulua (Rust port of Luau),
  cinderx (same project as cinder). Retier file data/wave12/verify/raw/retier-01.json (82 entries): up to A
  fakelua, julia, GraalPython, ruby/ruby YJIT, CPython JIT, daScript, Apogee, wazy, goja-perf, musql, Loko, jz,
  jrsonnet, Zipp; to B WasmNow (copy-and-patch paper via a github.io mirror), Luau, Moddable, TruffleRuby,
  Wizard (OOPSLA 2022 artifact), wasmer, Graal, Pythran, evmone, Guile, revmc (SkelOT artifact); down
  Paserati A to C (numbers predate inline-cache fix #550), Topaz A to C (kostya fork breaks hash semantics,
  warm best-of-5 vs one cold CRuby iteration), pevm A to C and vnmakarov MJIT A to C (first-party, collapsed
  empty-loop row), AssemblyScript C to D (JS baseline crippled by useDefineForClassFields, reproduced 7x),
  zig-js and tpy-lang to D; many caveat corrections (Web49, Zef richards 20x loop, Regorus stale v0 commands,
  pocketlang module-scope Python loops, Wizard validation-excluded timer, Bigloo I/O rows, Quirrel swapped
  f2s/s2f rows, Cyber stale). Keep-and-document overrides for every verifier "not notable" reject. Open: seed
  leads in data/wave12/leads.md (angelsea, goant, Box86, hxcpp, fafo, 0xjojoex/evm.zig, Cuik, LC Scheme),
  paper-access retiers (Instrew VEE'21, TPDE, Box64 EuroSys, aWsm, WARP, rv32emu VMIL, HHVM, Deegen, Pallene,
  YJIT, mutable EDBT 2023 and ADC 2023 arXiv 2311.04692, Higgs arXiv 1507.02437), repo_url overrides to
  consider (kostya/topaz, lmcad-unicamp/riscv-sbt), and cross-wave leads (xsum, matprod, qj, tsv-utils,
  Turso, splintr) parked in QUEUE.md.
- Wave 11 (runtime-and-systems) closed 2026-10-06 in one cloud session: searches b1-b8 for all 6 categories
  (48 raw files; b7/b8 on WebSearch snippets since blogs and HN were blocked) , 147 merged, 49 verify batches,
  144 verified after three duplicate folds (A 19, B 19, C 92, D 14; copyable 125, reference 17, mixed 2;
  allocators-gcs, coroutines-fibers, filesystems-and-io, logging-tracing, profilers-and-instrumentation,
  thread-pools-work-stealing). Six verifier rejects were overridden to keep with shortcomings (Neco, llco,
  heapusage, Tracy, memtrail, E9Patch: no baseline or not faster); none rejected for invalid evidence.
  Duplicates: ForkUnion (second id), Morgan Stanley binlog (hyphenated id), google/sanitizers (same tool and
  numbers as the llvm-project ASan entry). Retier file data/wave11/verify/raw/retier-01.json (24 entries):
  up to A ThunderBolt-HT; to B Trio (SOSP paper from a repo mirror) and FastMap (author thesis from a repo
  mirror); to C obstack A, v8malloc A (competitor columns probably ran v8malloc itself), Marl D; to D
  fc_malloc (benchmarked a different file with bugs), dp::thread_pool (timed submission, never waited), hop
  (startup-dominated), memtrail; claim or licence corrections for ripgrep, zlob, NanoLog (Iyengar111, MIT),
  IsoAlloc ('jemalloc' row timed IsoAlloc), tbox, Tracy (2.25 ns/zone overstated 12x), ArenaAllocator, FluxIO
  and others. Open: RetroWrite has no enrich file (its enricher was stopped by a safety classifier mid-write,
  shortcomings recorded from its report; ask the user before relaunching), no seed pass was run.
- Wave 10 (media-and-graphics) closed 2026-10-05 across three cloud sessions (2026-10-03 to
  2026-10-05): searches b1-b8 for all 5 categories (40 raw files; b7/b8 on WebSearch snippets plus
  github.com, HN and blogs blocked) plus seed-a..d (32 lead projects); 276 merged, 103 verify
  batches with 269 verdicts (confirm 223, downgrade 41, reject 3, duplicate 2), 254 verified
  (A 28, B 22, C 174, D 30; copyable 230, reference 19, mixed 5; image-codecs 72, video-audio 58,
  color-and-resampling 57, rasterizers-2d 33, font-shaping-text-layout 23, plus 9 unicode-utf8,
  1 general-lossless and 1 websocket-grpc-rpc filed by category override), every verified entry
  enriched (128 enricher pairs). Rejected for invalid evidence: Imageflow (bench.sh backgrounds
  the tool with an unquoted '&', so hyperfine timed job launch; MQF precedent), fast_resize (NEON
  bilinear path wraps int16 and outputs 0 for channels at or above 128; stb-zip precedent),
  ucstrcase (self-comparison hits the s == t early return), zenwebp (numbers from an incomplete
  encoder, own parity report shows it slower) and av2-turbo (no encoder in the repo, disabled
  CPU-only perf test). 17 duplicates (wrappers and ports: sharp, net-vips, jpeg4py, pyspng,
  python-soxr, skia-canvas, @napi-rs/canvas, resvg-js, agg-rust, edge264-mvc, rusty_png, trez,
  nvavif-py, gamut, soundkit, savonet/shine, bc7enc_rdo tables identical to bc7enc). Retiers are
  in data/wave10/verify/raw/retier-{01..38}.json; tier moves: bc7e C to B and NV_path_rendering
  C to B (papers and independent runs reached), libspng B to A (wuffs doc/benchmarks.md),
  giflib-turbo D to C, pngencoder C to B (FPNG-Java JMH), bcdec D to C (aras-p harness, capped by
  the later-fixed-bug rule), muSkia D to B (camera-ready OOPSLA2 paper in bhargavkulk/skia-paper:
  1.12x geomean, not 18.7%); down: yuv2rgb A to C and libjxl fjxl A to C (numbers from code later
  fixed), uniwidth A to C (bug in hot path), FFmpeg swscale B to C, LunaSVG B to C (resvg-py
  baseline built at opt-level z), Smolscale, lodepng-turbo, RGB2Y, TGFX and libqoi to D. Many
  entries kept with harness flaws documented (opencodecs PackBits row an artifact, imgdiff claim
  obsolete, kb and fastGaussianBlur flagged not faster, sst-basic-blocks timed copy reads its
  table out of bounds).
- Wave 9 (compression-and-encoding) closed 2026-10-03: searches b1-b8 for all 4 categories
  (34 raw files, b7/b8 thin: blogs and HN blocked, 17 records) plus seed-a/b (13 lead projects);
  150 merged, 61 verify batches with 148 verdicts (confirm 123, downgrade 21, reject 4), 136
  verified (A 33, B 21, C 74, D 8; copyable 124, reference 10, mixed 2), every verified entry
  enriched. Rejected for invalid evidence: NZ1 (README table contradicted by its own tests.txt)
  and SnellerInc/iguana (decoder unimplemented, ClickHouse port slower than ZSTD); torch_ans and
  miniz rejects overridden to keep. Duplicates: zlib-rs, iczelia/bzip3, fast-pack/maskedvbyte,
  quickwit bitpacking, go-simd/bitpack, brotli, miara (PTHash port), pzip (klauspost wrapper),
  m77rip (misa77 port), hybrid-fenwick-tree (now in sux). Retiers in
  data/wave9/verify/raw/retier-{01..05}.json: 01 FastPFor C to A (SPE paper on the paperhub S3
  mirror); 02 fifteen lzbench 2.4 entries B to A for consistency with FastLZ (public Makefile
  flags, gcc 15.2.0, EPYC 9555P); 03 genedex restored to A (quadrank precedent); 04 fdeflate D
  to B and jtkukunas/zlib C to B on independent numbers; 05 PISA A to C (search-benchmark-game
  driver returns fewer than k docs and mis-parses queries; moved to text-search-and-indexing).
  ZipNN moved to general-lossless (vendored FSE Huffman).
- Wave 8 (numerics-and-science) closed: searches b1-b8 for all 7 categories and two seed passes
  (52 projects) plus seed-j/k/l merged; 404 verdicts (confirm 353, downgrade 37, reject 14), 398
  verified (A 74, B 78, C 221, D 25), every verified entry enriched. Retier checks 12-14
  (2026-10-03) re-tried 13 blocked papers: only gpuNUFFT moved (D to C on cufinufft issue #126);
  arXiv, ACM, IEEE, Springer, Dagstuhl, archive.org and zenodo all stay blocked here. Rejected for invalid evidence: SIMDxorshift,
  SIMD-MT, ra_prng, CUDA-L1, OxiBLAS, cpp-matmul; the other rejects were overridden to keep per
  the keep-and-document rule. Retiers are in data/wave8/verify/raw/retier-{01..14}.json (08 PFT
  C to B on the KDD paper; 09 metal-float64 usability to reference; 10 DASP B to C on harness and
  correctness evidence; 11 vpxyz/xorshift A to C on generator bugs).
- b7/b8 in this environment ran on WebSearch snippets plus github.com, since HN Algolia, HN
  threads, arXiv and most blogs were blocked; their yield was thin (55 records).
- Waves 9-12 are set up (2026-10-01): `data/wave{9,10,11,12}/assignments.json` (152 assignments,
  19 categories x b1-b8) and leads.md; b1/b2 prompts rendered. Re-render b1/b2 before launching a
  later wave so its known list is current. zlib-ng and libdeflate are already filed under wave 9's
  general-lossless category.
- Cloud-session workflow that worked on 2026-10-03: 8-10 agents at a time (Opus verifiers, then
  Opus enrichers with two prompts each; Sonnet searches and seed passes), record each report and
  push before launching the next; no usage-limit kills across wave 9 (about 110 agents). One
  agent left pip wheels in the repo root; tell agents never to pip download inside the repo and
  delete strays on sight. Enrichers often read code the verifier did not: when they find a
  correctness bug behind the measured numbers, write a retier file rather than only a
  shortcoming. Paper PDFs on an author's USERNAME.github.io repo (and hpcrl/ICS2025-webpage) are
  reachable through raw.githubusercontent.com even when the site itself is blocked.
- Decision ids must exist in verified.json: two decisions were recorded under mistyped ids (rusty_alloc,
  aw-backtrace) and had to be re-keyed; check ids against the verified list before recording (the scratchpad
  adddec.py wrapper refuses unknown ids). Hyphen, underscore and case variants of one repo (fork_union and
  forkunion, morgan-stanley and morganstanley) slip past merge: scan verified ids with punctuation stripped
  before enrichment. Never `git add` a whole raw directory while agents run; stage named finished files.
