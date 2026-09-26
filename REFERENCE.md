# Reference

No license, unclear/non-OSI license, mixed licensing, or paper-only. Study the idea and reimplement clean-room; do not copy the code.

## Verified

### parsing-and-text

#### lexers-tokenizers

##### StreamTok (Static Analysis for Efficient Streaming Tokenization)  `Rust`  `no license`  `unknown`  `Tier B`

Rust streaming tokenizer using static max-lookahead analysis for O(1)-per-symbol maximal-munch tokenization vs flex's backtracking

**Beats:** flex — Peer-reviewed benchmark (RQ3, Fig. 10) reports StreamTok 2x-3x faster than flex-generated C lexers across JSON/CSV/TSV/XML/YAML/FASTA/DNS-zone/log grammars on a 10MB input; application-level tests (RQ5, Table 2) show 2.5x-3.1x for log-to-TSV and up to 5.39x for JSON minify. RQ1-RQ2 ran on an Intel Xeon E5-2640 v4 @ 2.40GHz/128GB RAM; the flex throughput comparisons (RQ3-RQ6) ran on an AMD EPYC 7252 8-core @ 3.10GHz/256GB RAM. Rust compiler version and build flags are not stated in the paper.

**Known shortcoming:** Compared against flex, which is not in this category's baseline list (re2c and hand-written lexers).

**Known shortcoming:** Paper only: no public code was found.

**How:** The paper introduces 'maximum token neighbor distance' (max-TND): the worst-case number of extra symbols needed to confirm no longer token is possible past a given match. When max-TND is bounded (statically computed via a co-accessibility fixpoint over the tokenizer DFA, O(state^2)), StreamTok builds a second automaton via powerset construction that runs K symbols ahead of the main DFA, so a fixed-size lookahead buffer of size K replaces flex's unbounded backtracking. This turns per-symbol tokenization from flex's O(k) backtracking (worse for pathological grammars) into O(1) amortized work per symbol.

**Use it when:**
- You're building/generating a tokenizer for a grammar you can statically analyze up front (JSON, CSV/TSV, XML, YAML, log formats, DNS zone files) and want to prove/bound the lookahead cost
- Streaming or memory-constrained pipelines where you cannot buffer the whole input the way a flex backtracking lexer might need to
- Grammars with pathological repeated-prefix ambiguity (the paper's synthetic (a{0,k}b)|a family) where flex's backtracking degrades with grammar parameter k but StreamTok stays O(1) per symbol
- Research/prototyping contexts where you can implement the pre-analysis + Rust runtime yourself, since there is no published crate

**Skip it when:**
- You need a drop-in flex replacement today: no public source, crate, or build artifact exists for StreamTok as of this writing
- Your grammar has unbounded max-TND — the paper found this true for ~32% of a 2,669-grammar GitHub sample, including C, R, and SQL, which fall back to non-constant (unbounded lookahead) behavior
- You need production maturity guarantees: this is a single ASPLOS '26 paper's evaluation artifact with no maintenance history, license, or usage outside the paper
- Computing max-TND for an arbitrary grammar is PSPACE-hard in the worst case (practical instances reportedly analyze in <100ms for 99.4% of the sampled grammars, but there's no guarantee for yours)
- You need C interop or the flex/re2c ecosystem (skeleton files, %option flags, yacc/bison integration) — StreamTok has none of that tooling

**Vs siblings:** Pick StreamTok over the other flex-beating entries (LRSTAR, simd-lexing, Ragel, CrossDB's hand-written parser) only if you specifically need a formal, provable bound on streaming lookahead for maximal-munch tokenization and are willing to reimplement from the paper — those other tools are usable today with real repos, while StreamTok has no code to run.

**Gotchas:**
- Falls back to unbounded lookahead behavior on grammars with unbounded max-TND (no error is thrown per se, but the O(1) guarantee disappears)
- Requires an upfront static-analysis and DFA/powerset-construction build step before any streaming can start, unlike flex's simpler generate-then-run model
- No public source, artifact, or package exists to inspect for actual API ergonomics or unsafe code use

**Status:** Maintenance status is unknown because no public repository exists at all; usability is 'reference' — this is an ASPLOS '26 paper's evaluation prototype, not a distributed library.

[benchmark](https://github.com/bojieli/ai-infra-book/blob/main/references/proceedings/ASPLOS/2026/paper-152.txt)

#### regex-engines

##### BLARE (Blazingly Fast Regular Expression)  `C++`  `no license`  `stale`  `Tier B`

Research framework that decomposes regexes into reordered sub-matches via a bandit-picked plan, layered on RE2/PCRE2/Boost/ICU.

**Beats:** RE2 — The peer-reviewed paper (Proc. ACM Manag. Data 1(2), Art. 152, SIGMOD 2023), run single-threaded on an Azure Xeon Platinum 8370C VM with C++17 code at -O3, reports BLARE 1.6x-3.7x faster than RE2 (09-2022 build), 3.4x-7.9x faster than Boost 1.65.1, and 3.1x to over 100x faster than PCRE2 10.40/JIT, across 2 Microsoft-internal production log workloads and the public US-Accidents Kaggle dataset; only the RE2/US-Accidents comparison (~1.6x) can be independently rerun from the public repo, and the ACM DOI page returns HTTP 403 to automated fetches (paper is mirrored as BLARE.pdf in the repo).

**How:** The regex is split (3-way split_regex or N-way split_regex_multi) into sub-patterns, and a multi-armed-bandit policy picks which sub-pattern to evaluate first based on observed cost/selectivity, so cheap or highly discriminating fragments reject non-matching lines before the full pattern is ever run through the underlying engine. Because the same regex is reused across many lines (log/dataset scanning), the bandit amortizes its exploration cost and converges on a near-optimal evaluation order for that workload; the final per-fragment match still calls the wrapped engine (RE2/PCRE2/Boost/ICU), so BLARE is an execution-order optimizer on top of those engines, not a replacement matcher.

**Use it when:**
- Batch, single-threaded scanning of many lines against one recurring regex (e.g. log parsing, dataset filtering) where the bandit can amortize warm-up
- You already depend on RE2, PCRE2, Boost.Regex, or ICU Regex and want extra throughput without switching engines
- Regexes with decomposable structure (alternations, literal anchors) that benefit from evaluating a cheap/selective piece first
- Reproducing or extending the SIGMOD 2023 paper's results, using original_codebase/BLARE_CODE for exact numbers
- First-match-per-line extraction workloads similar to the paper's US-Accidents / production log benchmarks

**Skip it when:**
- Any production dependency requiring maintenance or support: last commit 2023-11-20, 9 stars, 0 forks, no CI visible
- Anywhere licensing matters: no LICENSE file, so GitHub marks it all-rights-reserved by default
- Environments that can't add Abseil, Boost >=1.65.1, ICU4C, and PCRE2/jPCRE2 as build dependencies
- Multi-threaded or latency-sensitive services: paper benchmarks are single-threaded only; thread safety is not documented
- Anything needing the exact paper numbers from current main: README states main-branch code 'may not produce results identical to that in the BLARE paper'
- Non-Linux targets: build instructions are Ubuntu/apt-based and the original experiment flags use -march=native, tying binaries to the build host's CPU

**Vs siblings:** Pick BLARE over re2jit or rejit only when the goal is specifically reproducing or studying the SIGMOD 2023 decomposition/bandit technique on RE2, PCRE2, Boost, or ICU; for a production RE2 speedup, re2jit is the safer sibling (20-30% faster on capture-group workloads, no extra Abseil/Boost/ICU/PCRE2 dependency chain) since BLARE is stale and unlicensed.

**Gotchas:**
- Main-branch code is under active change and the README itself warns it may not reproduce the paper's numbers; use original_codebase/BLARE_CODE for that
- No LICENSE file is present (GitHub reports 'license: none'), so usage/redistribution rights are unclear by default
- The bundled US-Accidents CSV requires 'git lfs pull'; a newer Kaggle CSV format breaks the hard-coded read_traffic parser and needs manual edits
- Two of the three paper workloads (DB-X, System-Y) are Microsoft-internal logs and cannot be rerun outside Microsoft; only the 1.6x-vs-RE2 US-Accidents result is publicly reproducible

**Status:** Stale research prototype (last commit 2023-11-20, 9 stars, no LICENSE) — useful as a reference implementation of the decompose-and-reorder technique, not something to take a runtime dependency on.

[repo](https://github.com/mush-zhang/Blare) · [benchmark](https://dl.acm.org/doi/10.1145/3589297)

### serialization-and-formats

#### binary-schemas

##### Cornflakes  `Rust`  `no license`  `abandoned`  `Tier B`

Rust research serialization library and kernel-bypass UDP stack that sends large fields zero-copy via NIC scatter-gather, beating Protobuf/FlatBuffers/Cap'n Proto.

**Beats:** Protobuf, FlatBuffers and Cap'n Proto via the pure-Rust crates protobuf 3.0.3 (rust-protobuf), flatbuffers 2.1.2 and capnp 0.13.6 (cf-kv/Cargo.toml); Redis handwritten serialization for Table 3 — The SOSP 2023 paper runs a single-core Rust KV server on CloudLab c6525-100g machines (2x EPYC 7402P, ConnectX-5Ex 100 Gb, MTU 9000), with every system on the Cornflakes UDP stack and the pure-Rust protobuf 3.0.3, flatbuffers 2.1.2 and capnp 0.13.6 crates as baselines; the rustc version is not stated. Cornflakes served 366.5k vs 161.0-186.1k objects/s on the CDN image trace, delivered 15.4-45.9% more throughput on the Twitter trace (p99 about 52-61 us) and roughly tied on Google's small-field trace; in Redis, get/mget/lrange gained 15-40.1% over Redis's own handwritten serialization.

**Known shortcoming:** Research prototype, abandoned since 2023-07. No win on small objects (paper Table 1). Baselines are the pure-Rust protobuf/flatbuffers/capnp crates, not the C++ libraries, and the Redis gains are against Redis's own handwritten serialization.

**Known shortcoming:** Needs a kernel-bypass NIC datapath (mlx5); the Linux-socket datapath always copies. Single-core, single-jumbo-frame prototype with no segmentation or write protection for buffers in flight. Code defaults use a 256 B zero-copy threshold, while the paper's numbers use 512 B. C bindings exist but use from C++ is undocumented, and generated code fails for int32-only messages (issue #1, open since 2021).

**How:** Protobuf, FlatBuffers and Cap'n Proto copy each bytes/string field into a contiguous buffer and then again into DMA memory; Cornflakes instead posts each pinned-memory field of 512 B or more as its own NIC scatter-gather entry (zero-copy transmit), and a per-buffer reference count keeps that memory alive until the DMA completes. A per-field size threshold, checked when the field's smart pointer (CFBytes/CFPtr) is constructed, chooses copy or zero-copy: smaller fields go into an arena-backed copy buffer, because below about 512 B the reference-count cache miss costs more than the memcpy. Serialize-and-send writes the packet header, the object header and the copied data into one entry and posts the zero-copy entries directly onto the NIC ring, with no intermediate scatter-gather array (a 7.7-17.4% throughput gain in the paper). All framing (a field bitmap plus u32 size/offset forward pointers) is at the front of the object, so each zero-copy field needs only one extra scatter-gather entry.

**Use it when:**
- Microsecond-scale datacenter services such as caches and KV stores that already run on kernel bypass with Mellanox ConnectX-5/6 or Intel E810 NICs, where serialization copies are a large share of CPU time per request.
- Responses built from values of 512 B or more that already sit in pinned memory, e.g. a store that returns stored blobs. On the paper's CDN image trace (objects of 1 KB and up) it served 97-128% more objects/s than the three baselines.
- Workloads that mix small and large values, like the Twitter cache trace (about 32% of requests are 512 B or more), where the hybrid copy/zero-copy path beat pure scatter-gather by 2.3-3.9% and beat the copy-based libraries by 15.4-45.9%.
- Applications that never modify data in place while it is being sent, such as Redis-style stores, versioned stores, or code that updates by allocating and swapping pointers.
- As a reference design and threshold-calibration method (paper Section 5) when adding zero-copy serialization to your own kernel-bypass stack.

**Skip it when:**
- Small-field workloads. On Google's field-size distribution (94.9% of fields are 512 B or less) it ties or slightly trails Protobuf (844.7 vs 852.5 k req/s at 1 value) and wins only at 1-8 and 1-16 values per list.
- Standard Linux sockets. The linux-datapath returns usize::MAX as its copy threshold (always copies), and many of its functions are unimplemented!().
- Messages larger than one jumbo frame. The prototype has no segmentation: the CDN benchmark split objects into sub-objects that fit a jumbo frame, and the copy path carries a 'doesn't work if buffer is > than an MTU' TODO.
- Production or multicore use, or any need for Protobuf wire compatibility, proto2 required fields, or recursive pointer-based types (the author confirms in issue #7 that trees with pointers are not supported). The paper evaluates a single-core server and leaves multicore to future work.
- Any project that needs a license: the repo has no LICENSE file.

**Vs siblings:** Pick it over rkyv, or over FlatBuffers-family formats such as Karmem and Lite³, only when your bottleneck is the transmit-path memcpy on a kernel-bypass NIC and your fields are 512 B or larger. Those siblings speed up CPU encode/decode over any transport, but Cornflakes's gain comes from NIC scatter-gather and disappears for small fields or on normal sockets.

**Gotchas:**
- The kv app's --copy_threshold CLI default and the mlx5 datapath default are both 256 B, not the paper's 512 B. The experiment configs pass 512 explicitly (cornflakes-dynamic-512). The paper recommends re-measuring the threshold on your own NIC and CPU.
- Zero-copy applies only to data inside the stack's registered pinned memory. For any other pointer, recover_metadata returns None and the field is copied without any warning.
- Copied entries come before zero-copy entries on the wire. As a result, peers configured with different thresholds can serialize repeated elements in different orders.
- Issue #1, open since 2021: the code generator emits code with lifetime errors for messages that contain only int32 fields.

**Status:** Abandoned research prototype: the main branch was last committed on 2023-07-27 (the timetrace branch on 2024-01-19), and there is no LICENSE file, so use it as a reference design to study, not as a dependency.

[repo](https://github.com/deeptir18/cornflakes) · [benchmark](https://people.eecs.berkeley.edu/~matei/papers/2023/sosp_cornflakes.pdf)

#### json

##### Mison (speculative structural-index JSON parser)  `C++`  `no license`  `unknown`  `Tier B`

VLDB 2017 JSON parser (no public code) that jumps straight to queried fields; reports 5.5-9.1x over best of RapidJSON/Jackson/Gson.

**Beats:** RapidJSON — The authors' own single-threaded benchmark ran field-projection queries on a 3.5 GHz Xeon E5-1620 v3 under Windows 10, with data preloaded into memory and no compiler or flags stated. On Twitter records, Mison was 5.5-9.1x faster than the best of Jackson, Gson and RapidJSON (all using their streaming APIs; Jackson, not RapidJSON, was the strongest), and about 2x faster than Jackson when all 31 GitHub fields were read. No one has reproduced the full parser; Sparser's authors reimplemented only the index step, found Mison over 2 GB/s per core and over 5x RapidJSON, and noted that the implementation 'is not open source'.

**How:** First it builds a per-record structural index. AVX2 compares 32 bytes at a time against quote, backslash, colon and braces (and brackets or commas when arrays are queried), and the results become bitmaps. 64-bit bit tricks (x&(x-1), x&-x, x^(x-1), popcnt) then drop escaped quotes, build a string mask, and use a brace stack to split colons into 'leveled colon bitmaps', one per nesting depth, built only down to the deepest queried field. The k-th set bit therefore locates the k-th field's key/value boundary without tokenizing. Second, it parses speculatively. 'Pattern trees', trained on a sample (the first 1,000 records in the paper, keeping patterns seen more than 1% of the time), predict each queried field's ordinal position. The parser jumps there, checks that the key name matches, tries less frequent patterns if it doesn't, and falls back to scanning every colon at that level if none match. In the paper's Fig. 11, index-only (basic) Mison was 3.6x faster than Jackson and speculation raised that to 10.2x.

**Use it when:**
- In-memory scans of newline-delimited record streams where a query needs 1-2 fields out of dozens (the Twitter records had 25-30 top-level fields plus a 37-38-field user object). That is where the paper shows its 8-9x best case.
- Record collections that share a few layouts in a stable field order, such as the paper's GitHub user records (31 fields, always in the same order) or Twitter's user field, which sat at position 11 in 80.7% of tweets and 12 in the rest. Speculation pays off there.
- Selective filters that can be evaluated before projection. In the Spark TPC-H runs, queries with 0.5-3.7% selectivity on lineitem ran 16.3-32.5x faster with Mison than with Spark's Jackson path.
- As a design reference for a query-on-raw-JSON engine. The leveled colon/comma bitmap index is implemented in C++ in AutomataLab/Pison (MIT). The full algorithm, including pattern-tree speculation, exists in the Rust crate pikkr (MIT).

**Skip it when:**
- You need a maintained library. No official code exists, and the reimplementations are research or hobby code: pikkr's last push was 2017, and its open issue #76 reports it doesn't build on Rust 1.80. The misosoup README says 'DO NOT use for production use'. gomison contains only a README and a LICENSE.
- Full-document parsing, DOM building or serialization. With all 31 GitHub fields read, the lead over Jackson falls to about 2x. Mison has no writer and builds no tree.
- Untrusted or possibly malformed input. The simdjson paper notes that Mison does not validate documents and assumes pure ASCII rather than UTF-8. pikkr, which follows the same design, accepts {"x":0,} and returns the value '0,'.
- Highly irregular or schema-drifting data, optional fields, and arrays. In the paper, Q5 (a field with 7 root-level patterns) was slower, and Q6-Q8 needed Bloom filters or leveled comma bitmaps, which cut Mison's advantage.
- Data you will query many times. The paper itself finds converting to Parquet faster (Spark+Parquet was 1.6x faster than Spark+Mison, geometric mean over TPC-H SF1, not counting about 100 s of conversion). A single huge JSON document is also a poor fit: Mison indexes each record serially, and Pison was built to parallelize that case.

**Vs siblings:** For shipping code, use simdjson's On-Demand API: the simdjson paper says it follows Mison's structural-index outline but with branchless stage-1 code, and On-Demand skips fields you never access while validating the ones you use. Reach for Mison, in practice pikkr or Pison, only to study or reproduce pattern-tree speculation and leveled-bitmap projection. For full parsing or writing, yyjson or glaze fit better.

**Gotchas:**
- Keys are assumed unique within an object (the paper states this assumption), and input is assumed to be ASCII. Neither is checked.
- A missing queried field makes Mison either skip the whole record or return null, depending on configuration. Choosing skip silently drops rows; the Anghagaed/MISON reimplementation lists exactly this as a known bug compared with Spark.
- Speculation depends on a one-time training sample, and patterns below the weight threshold are pruned. The paper describes no retraining, so if the data layout drifts, every record falls back to the slower basic parse.
- The training cost is included in the paper's timings, but the paper does not report how much of the total it is.

**Status:** Nothing was ever released: the MSR page carries only the PDF, and Microsoft's FishStore used Mison in its SIGMOD 2019 paper but ships simdjson in the open-source repo, so treat Mison as a reference design whose nearest usable code is pikkr (Rust, MIT, dormant since 2017) or Pison (C++, MIT, index only, no speculation).

[benchmark](http://www.vldb.org/pvldb/vol10/p1118-li.pdf)

### stdlib-replacements

#### allocators

##### NUMAlloc  `C++`  `no license`  `abandoned`  `Tier B`

NUMA-aware LD_PRELOAD malloc replacement, ~21% faster than glibc malloc and ~16% faster than mimalloc on 128-thread NUMA workloads.

**Beats:** default Linux allocator (glibc 2.28 malloc) — Per the ISMM'23 manuscript (source/ISMM2023/evaluation.tex, read directly): on an Intel Xeon Platinum 8153 (8 nodes x 16 cores, 512GB RAM, Debian 10, GCC-8.3.0, THP+AutoNUMA on, hyperthreading off), averaged over 30 runs at 128 threads across PARSEC, five CORAL-2 OpenMP/MPI apps, and 7 real applications, NUMAlloc was 20.9% faster than glibc-2.28's default malloc and 15.7% faster than the next-best allocator tested (mimalloc-1.6.7), also beating TCMalloc, TCMalloc-NUMA, and TBB by 18-21%; the OpenMP/MPI subset alone showed 26.1% over glibc and 16.5% over mimalloc; best case fluidanimate was 5.3x glibc and 4.6x mimalloc. A superseded SC'22 draft in the same repo reports different numbers (19.0% vs glibc) for an overlapping but not identical benchmark set.

**How:** Layers a fast per-thread heap over a per-node heap tier, so the common malloc/free path never touches cross-node state; freed objects are returned to the heap tier matching the node they came from ('origin-aware' return) instead of a shared free list, keeping frees node-local under NUMA. During a program's single-threaded startup/teardown, an optional interleaved 'inter-heap' spreads allocations across all nodes to avoid one node absorbing all pre-fork memory. It's also built with transparent huge pages (-DUSE_HUGE_PAGE) to cut TLB misses on the large per-node heaps, which the ISMM'23 paper's own remote-access/TLB-miss profiling (perf) ties directly to the wins on dedup, fluidanimate, pbzip2, streamcluster and swaptions.

**Use it when:**
- Multi-socket/multi-node NUMA Linux servers (paper: 8-node, 128-core Xeon Platinum 8153) running allocation-heavy, multi-threaded HPC or server workloads similar to PARSEC, CORAL-2 OpenMP/MPI, httpd, MySQL, or Memcached
- You can rebuild the allocator with -DNUMA_NODES=<actual node count> -- it's hardcoded at compile time and the shipped Makefile defaults to 2
- A plain C/C++ executable you can LD_PRELOAD, not something needing a vendored/linked allocator API
- You can pin to an old toolchain matching the paper (GCC 8.3.0, C++14, Debian 10) and, critically, a pre-2.34 glibc
- Research/reference use where you can independently validate results, not a production dependency

**Skip it when:**
- Any current Linux distro: an open, unmerged PR (#1, filed 2026-07-08) shows NUMAlloc infinite-recurses and crashes via an assertion the moment a second thread is created on glibc >= 2.34 (Ubuntu 22.04+, Debian 12+, effectively any 2022+ distro), because its pthread_create interposition looks for a libpthread.so.0 that glibc merged into libc.so.6
- Single-socket/single-NUMA-node machines -- the whole design is cross-node locality, so on one node you likely get the ~10-12% THP memory overhead for no throughput gain
- Production or license-sensitive use -- no top-level LICENSE file; core NUMA-specific headers (pernodeheap.hh, perthreadheap.hh, interheap.hh) carry no license header at all, and files inherited from the FreeGuard project are GPL-2.0-or-later
- Need active maintenance -- last push 2023-03-01, 2 GitHub stars, and the repo is a research dump of ~10 UTSASRG projects plus a dozen near-duplicate source-* variant folders with no indication which one produced the paper's numbers
- Serial-phase-heavy programs -- the interleaved inter-heap exists specifically to offset interleaving costs during single-threaded phases, so a program that spends most of its time before spawning threads pays extra bookkeeping for little benefit

**Vs siblings:** Pick NUMAlloc over SuperMalloc/Hoard/scalloc/rpmalloc/ltalloc/smmalloc only if you specifically need NUMA-node-local allocation on an 8-node-class multi-socket server, can rebuild for your topology, and are willing to fix the glibc>=2.34 pthread_create crash yourself; those siblings target single-node thread-count scaling and work off the shelf today, whereas NUMAlloc is an abandoned research prototype that currently fails to launch multi-threaded programs on modern Linux.

**Gotchas:**
- Open, unmerged PR #1 (2026-07-08): pthread_create resolves to the library's own wrapper instead of the real symbol on glibc >= 2.34, causing infinite self-recursion and an assertion crash on the second thread spawned under LD_PRELOAD; the author confirms the same bug exists in all ~12 source-* copies in the repo
- NUMA_NODES is a compile-time constant (Makefile default 2, paper implies 8) -- building for the wrong node count is a silent topology mismatch, not a runtime-detected error
- Heap is placed at a fixed virtual address (0x100000000000) rather than obtained from mmap(NULL, ...), which can collide with sanitizers or other tools that reserve that address range
- About 10-12% higher RSS than glibc from transparent-huge-page use; drops to roughly glibc-comparable memory use with THP disabled (dropping -DUSE_HUGE_PAGE), per the input record's tradeoffs

**Status:** Abandoned since its last push on 2023-03-01 (2 GitHub stars) and usability is 'reference' only -- no top-level LICENSE, several core headers unlicensed, GPL-2.0-or-later on FreeGuard-derived files, and an unresolved crash-on-second-thread bug on any glibc >= 2.34 system as of this writing.

[repo](https://github.com/UTSASRG/numalloc) · [benchmark](https://raw.githubusercontent.com/UTSASRG/numalloc/master/ISMM2023/evaluation.tex)

#### bitsets-and-succinct

##### plf::bitset (plf_bitsets)  `C++`  `Computing For Good License v1.01 (non-OSI; zlib-style terms plus ethical field-of-use restrictions 4a-4e)`  `active`  `Tier A`

Header-only bitset beating std::bitset at ranged set/reset, shifts, and bit search, minus from-string constructors.

**Beats:** std::bitset — First-party benchmark (plflib.org/bitsets.htm, author's own numbers, methodology and code published) on an Intel i7-9750H under Windows 10, GCC 13.2 (libstdc++) and MSVC 2022 (MSVC STL), O2/AVX2/C++23 release build: plf::bitset beat std::bitset by 24%/20% overall on a full-operation test-suite loop, ~101%/98% (GCC) and 35%/22% (MSVC) on left/right shift, and 34,652%/67,612% on set_range/reset_range across 10,000 random ranges of a 128,000-bit bitset - the last figure mostly reflects that std::bitset has no bulk range-set primitive at all rather than a raw constant-factor win.

**How:** Same word-array layout as std::bitset (array of storage_type words), but set_range/reset_range write whole words with masks instead of looping bit-by-bit like std::bitset callers have to (std::bitset has no bulk range primitive at all, which is why that number is ~340x-676x rather than a small constant factor). Bit search (first/next/prev one or zero) uses compiler builtins directly (__builtin_ctz/_BitScanForward64, or std::countr_zero/std::popcount under C++20's <bit>) instead of a generic scan loop. No SIMD/AVX intrinsics are used in the header itself despite the AVX2 benchmark flag - the ~20-24% overall test-suite gain comes from tighter, more branch-light word-level code (e.g. compile-time-eliminated overflow-bit handling, template-gated bounds checks) rather than a different algorithm.

**Use it when:**
- Fixed-size bit flags where you already use std::bitset and don't rely on its from-string constructor
- Workloads that set/clear/query contiguous ranges of bits (set_range/reset_range) instead of single bits in a loop
- Need a runtime-sized or user-buffer-backed bitset (plf::bitsetb) - e.g. per-instance variable size, or placement over pre-allocated/arena memory
- GCC or MSVC targets on x86-64, where the author's release numbers were actually measured (i7-9750H, O2/AVX2, C++23)
- Want first/last-one/zero search or an allocation-free swap that std::bitset doesn't offer

**Skip it when:**
- Code that constructs std::bitset from a string or unsigned long/long long - those constructors aren't implemented here
- Organizations that require an OSI-approved license - Computing For Good v1.01 is zlib-like but adds ethical-use restrictions (4a-4e) and is not OSI-approved
- Clang/libc++ targets - the author states libc++ was not tested or benchmarked
- Projects that need independently-reproduced numbers - all benchmark results are first-party (author's own page and repo), with 14 stars and no third-party reproduction found
- Code paths hitting the four currently-open correctness issues (overflow-bit restoration, not-found sentinels - see gotchas) until they're resolved

**Vs siblings:** Pick plf::bitset over CRoaring, pasta::bit_vector, better_bitset, BitLib, and sul::dynamic_bitset when you specifically want std::bitset's fixed-size, non-succinct, no-rank/select shape (not a compressed/sparse structure like CRoaring, not a rank/select index like pasta::bit_vector) but need faster ranged set/reset or shifts than std::bitset provides; use plf::bitsetb instead of BitLib or sul::dynamic_bitset when you want that same std::bitset-shaped API with a runtime-determined size or a user-supplied buffer rather than a vector<bool>-style resizable container.

**Gotchas:**
- Four issues are open on the repo (#3, #4, #5 filed against overflow-bit restoration in set_overflow_to_one, all_range's empty-range path, and next/prev_zero's not-found path; #6 requests a proper not-found sentinel for the search functions) - check these before relying on exact behavior at bitset-size edges
- from-string / from-ulong / from-ullong constructors aren't implemented - existing std::bitset(str) call sites need to be rewritten, not just retyped
- The third template parameter (hardened, default false) controls bounds checking; with it left at default, operator[] is unchecked like std::bitset's, while test() still throws - read the header if you rely on a specific check point
- License is Computing For Good v1.01, not a standard permissive license - clauses 4a-4e restrict use by field/purpose, which needs a legal read some organizations won't accept

**Status:** Actively maintained (last commit 2026-09-19, four open bug-tracking issues under active triage); usability is marked 'reference' rather than drop-in because the non-OSI Computing For Good v1.01 license's ethical-use clauses (4a-4e) call for a legal review before production adoption at most companies.

[repo](https://github.com/mattreecebentley/plf_bitsets) · [benchmark](https://plflib.org/bitsets.htm)

#### ordered-maps-trees

##### S+ tree (Algorithmica static B-tree array layout)  `C++`  `no license`  `abandoned`  `Tier A`

SIMD (AVX2) static B+-tree array layout beating std::lower_bound/std::set on batched int32 lookups.

**Beats:** std::lower_bound (primary), std::set (bench code binsearch/set.cc actually uses std::multiset), absl::btree — Reciprocal-throughput microbenchmarks on an AMD Zen 2 CPU with Clang 10 (-O3 -march=native) show the S+ tree up to ~15x faster than std::lower_bound on cache-resident sorted int32 arrays (~8x for arrays >1e6, up to 2^25 elements), up to ~30x faster than std::multiset::lower_bound, and (pointer variant) ~15x faster than Abseil's absl::btree on large arrays; the author explicitly notes real single-query latency gains are much smaller than these throughput figures.

**How:** The sorted array is rearranged into a B-ary tree (16 keys per node/cache line, branching factor 17) stored as one flat array with compile-time layer offsets instead of pointers (the 'S+ tree' = separate internal/leaf layers, vs. the pointer/Eytzinger-numbered 'S-tree'). Each node comparison loads 16 keys into two AVX2 256-bit registers, does _mm256_cmpgt_epi32 SIMD compares, permutes/packs the masks, and extracts the branch index with tzcnt, replacing several scalar branchy comparisons per level with one branchless SIMD step; large trees also use aligned_alloc + madvise(MADV_HUGEPAGE) to cut TLB misses. The headline numbers are reciprocal-throughput over batches of independent queries, which lets the CPU overlap several independent tree descents (~3x ILP per the article) rather than shrinking single-query latency much.

**Use it when:**
- Read-mostly/static sorted 32-bit-integer key sets that are bulk-built once (or rarely rebuilt), not mutated incrementally
- Workloads that issue many independent lookups that can be batched/pipelined (joins, index probes, columnar scans) so the reciprocal-throughput gains actually materialize
- x86-64 targets with AVX2 where you can build with -march=native and enable transparent huge pages for large (>1e6-element) arrays
- Arrays that fit or mostly fit in cache, where the article's ~15x-over-std::lower_bound number applies (~8x still holds up to 2^25 elements)
- You're willing to vendor and adapt a single .cc file into your own build rather than link a maintained library

**Skip it when:**
- You need insert/delete or any online mutation of the key set -- no dynamic update path is implemented, only a full prepare() rebuild
- Latency-sensitive single-query paths with data-dependent lookups (pointer chasing between queries) -- the author states real per-query latency gains are much smaller than the throughput numbers
- Non-x86 or AVX2-unavailable targets -- the article says porting to AVX-512 or Arm NEON needs 'non-trivial changes', and none is provided in this repo
- You need arbitrary key/value types, comparators, or a runtime-chosen array size -- N is a compile-time constant baked into the offset/height calculations
- Anything beyond experimentation/benchmarking in production -- no LICENSE file, abandoned since 2022, and the author frames this as teaching/reference code

**Vs siblings:** Pick this over tlx::btree or boost::container::flat_set/fast-containers when your key set is effectively static (bulk-loaded, then read-heavy) and lookups can be batched for throughput; those siblings are actual libraries supporting online insert/erase/find, whereas amh-code is an unpackaged technique reference you'd have to adapt, re-tune, and maintain yourself.

**Gotchas:**
- Array size N is a preprocessor/constexpr constant (binsearch.hh defaults to 1<<20), so each key-set size effectively needs its own compiled variant rather than being a runtime parameter
- Requires AVX2 codegen (-march=native or explicit target attributes); there is no scalar fallback path in these files
- Large-array speedups depend on aligned_alloc + madvise(MADV_HUGEPAGE) actually getting huge pages from the OS; without that configured, expect smaller gains than reported
- Headline speedups are reciprocal-throughput over batches of independent queries -- single dependent-query ('real') latency shows a much smaller win, per the author's own caveat in the article

**Status:** Abandoned reference code (last commit 2022-10-06, no LICENSE file) published as teaching/benchmark material for the Algorithmica HPC book, not a maintained library -- treat it as a technique to study and port, not a dependency to pull in.

[repo](https://github.com/sslotin/amh-code) · [benchmark](https://en.algorithmica.org/hpc/data-structures/s-tree/)

#### perfect-hash-static-tables

##### zmph (Zig Minimal Perfect Hash Map)  `Zig`  `no license`  `active`  `Tier A`

Pure-Zig minimal perfect hash map for fixed string key sets; about 1.7x faster average lookups than std.StringHashMap.

**Beats:** Zig std.StringHashMap and std.StaticStringMap — The author's own zBench run (Zig 0.15.1, ReleaseFast, Core i7-8750H, Debian) built each map at runtime from /usr/share/dict/words and timed 100,000 single lookups, all hits, one timer per call: zmph averaged 26 ns (min 18, p99 38), std.StringHashMap 45 ns (min 22, p99 106), and std.StaticStringMap 10.4 us, because its lookup is a linear scan over keys of equal length. Build times were 28.9 ms, 6.1 ms and 2.0 ms. Timer overhead is included in every figure and the comptimeInit path was never measured, so the ~1.7x is an average of wall-clock samples, not an exact ratio of lookup costs.

**How:** It uses hash-and-displace minimal perfect hashing, as in Steve Hanov's 'Throw away the keys' post (which cites CHD by Belazzougui, Botelho and Dietzfelbinger), and this is what the README links to. Keys are grouped into n buckets by Murmur3_32 with seed 0. Buckets are placed largest first by trying seeds d = 1, 2, ... until every key in the bucket lands in a free slot, and single-key buckets go straight into the leftover slots, stored as -slot-1. A lookup reads one displacement entry, computes a second Murmur3_32 only for keys from multi-key buckets, and does one key comparison, with no probing and no empty slots; std.StringHashMap is open addressing with linear probing (Wyhash, 80% max load), so its lookups can probe several slots.

**Use it when:**
- Zig code with a fixed string key set (a word list, command names, identifiers) that is built rarely and read very often. From the README averages, the extra ~23 ms of build time versus StringHashMap on a dictionary is paid back after roughly 1.2M lookups per build (derived: 22.8 ms / 19 ns).
- Read paths where tail latency matters on a large set: the README reports p99 38 ns vs 106 ns and max 96 ns vs 29.8 us against StringHashMap (all hits, dictionary-sized key set).
- Dictionary-sized string sets where you would otherwise use std.StaticStringMap. That map scans every key of the same length, which is why it is ~400x slower in this benchmark.
- Small key sets known at compile time, such as a tokenizer's keyword table (see examples/parser.zig). `comptimeInit` puts the table in the binary with no runtime build and no allocator. Note that this path is not benchmarked.

**Skip it when:**
- Maps that change after they are built. There is no put, remove or iteration, so any change means a full rebuild. `init` is documented as O(N^2), and the build took 28.9 ms vs 6.1 ms for StringHashMap on the same word list.
- Lookups where many keys are absent, on a map built with `init()` at runtime. See gotchas: from my reading of the source, a miss that lands on an empty bucket is illegal behavior. The benchmark and the tests only look up keys that are present.
- Non-string keys. K is generic, but getIndex compares with `std.mem.eql(u8, ...)`, so in practice only `[]const u8` keys compile.
- Small keyword sets where StaticStringMap is the incumbent. Nothing in the repo measures that size, which is the size StaticStringMap is designed for ('optimized for small sets of disparate string keys').
- Anything you need to ship or modify. There is no LICENSE file, it has 8 stars, and no CI run has ever been recorded (the test workflow only runs when triggered by hand).

**Vs siblings:** It is the only Zig entry in this category, so choose it when you write Zig and want faster reads than StringHashMap on a large fixed string set. In C++ (frozen, qlibs mph, constexpr-phf), Rust (rust-phf, QuickPHF) or Go (constmap), use those siblings instead, and since zmph has no license, treat it as a reference for writing your own hash-and-displace table.

**Gotchas:**
- On a map built with `init()`, empty buckets keep displacement maxInt(isize). getIndex then @intCasts that value to a u32 hash seed. The Zig 0.15.1 langref calls this safety-checked illegal behavior: a panic in Debug/ReleaseSafe, anything can happen in ReleaseFast. So misses can crash a map built this way. `comptimeInit` fills empty slots with 0 and avoids the problem.
- Duplicate keys are not detected. Two equal keys always hash to the same slot, so the seed search never succeeds. Keys are stored as borrowed slices, so the key bytes must outlive the map. Do not call `deinit` on a `comptimeInit` map, because its allocator field is left undefined.
- `comptimeInit` builds n buckets that each hold an n-slot fixed array and sets an n^2 eval branch quota, so compile-time memory and work grow quadratically. It suits keyword-sized tables, not dictionaries. It also failed to compile from the Aug 2025 port to Zig 0.15.1 until the v0.2.1 fix on 2026-01-31.
- build.zig.zon pins zBench by hash to a branch archive (refs/heads/zig-0.15.1). That branch changed zbench.zig in Dec 2025, after the pin, so a fresh fetch will likely fail the hash check, and because the dependency is not lazy, projects that depend on zmph may hit this too. examples/build.zig still passes the pre-0.15 addExecutable fields (root_source_file/target/optimize), which Zig 0.15.1 removed.

**Status:** Active but small: v0.2.1 was released 2026-01-31, it has one author and 8 stars, and no issues or CI runs have ever been recorded. With no LICENSE file it is reference-only, so read it to learn the technique rather than vendoring it.

[repo](https://github.com/PaNDa2code/zmph) · [benchmark](https://github.com/PaNDa2code/zmph/blob/master/README.md)

#### searching

##### SIMD Quad search (Lemire blog benchmark)  `C++`  `no license`  `active`  `Tier A`

SIMD quaternary-interpolation search over sorted 16-bit arrays in 16-element blocks; beats std::binary_search on Roaring-Bitmap-style containers.

**Beats:** std::binary_search — On an Intel Emerald Rapids server (GCC) and an Apple M4 (Apple LLVM), Release-mode C++23 builds (CMake default -O3 -DNDEBUG, no -march flags) benchmarking membership queries on sorted uint16_t arrays (sizes 2-4096, 100,000 arrays per size, 10M cold-cache + 10M warm-cache queries per size): simd_quad beat std::binary_search in every tested configuration, with the >2x speedup holding specifically for Intel-warm-cache and Apple-M4-cold-cache; the opposite cache mode on each platform showed smaller, numerically unstated gains (charts only, no numeric tables in the post text).

**How:** It narrows to a candidate 16-element block using quaternary interpolation search over block-boundary keys (comparing 3 split points per round instead of binary search's 1, so fewer rounds), then checks all 16 candidates in that block with one SIMD compare pass (NEON vceqq_u16 or SSE2 _mm_cmpeq_epi16 over two 8-lane loads, ORed and reduced) instead of continuing scalar element-by-element comparisons.

**Use it when:**
- Sorted arrays of uint16_t, roughly 16-4096 elements (the tested range and Roaring array-container size cap)
- Membership-only lookups (found/not-found), not insertion-point queries
- Workload is warm-cache-dominated on x86 (author measured >2x vs std::binary_search there) or cold-cache-dominated on Apple Silicon (>2x there)
- You can adapt call sites to the array_container_t{const uint16_t*, size_t} shape and compile with NEON or SSE2 guaranteed
- You're comfortable vendoring a ~40-line function rather than linking a library

**Skip it when:**
- Any key type other than uint16_t — the compares are hardcoded to 16-bit values
- General-purpose sorted containers with arbitrary element types/sizes where std::binary_search/lower_bound already fits
- Platforms without SSE2 or NEON — no scalar/AVX2/SVE fallback beyond a small-array linear scan below 16 elements
- Need for an insertion point (lower_bound semantics) — simd_quad only returns a boolean
- Anything requiring production hardening: this is unpackaged blog-benchmark code with no test suite beyond a self-check against std::binary_search inside the benchmark harness itself, and no issue tracker for this specific function

**Vs siblings:** Pick simd_quad over the generic siblings (sb_lower_bound, scandum/binary_search, FastBinarySearch) only when you're already working with sorted uint16_t arrays capped near 4096 elements in the Roaring-Bitmap array-container shape and can adapt to its struct-based calling convention; for generic sorted-array membership or lower_bound over other primitive types or larger/unbounded sizes, the siblings are closer to drop-in replacements for std::lower_bound/bsearch and are the better fit.

**Gotchas:**
- Assumes the array is already sorted ascending; the code does not check this and will silently return wrong answers on unsorted input
- Arrays smaller than 16 elements (the fixed block size) skip the SIMD/interpolation path entirely and fall back to a plain linear scan, so there's no benefit below that size
- The quaternary-interpolation step over plain SIMD-binary-search only helped in the author's own ablation on the Intel machine (large arrays, cold cache); on Apple M4 it had little effect, so porting it as-is to ARM buys less than the Intel numbers suggest

**Status:** Not a maintained library — it's single-author blog-benchmark code; the repo README explicitly disclaims industrial-strength quality ('don't expect or ask for industrial-strength software... it can be wrong, slow, poorly coded') and states the code is public domain ('don't bother forking, just steal it') even though no formal LICENSE file exists. Usability is reference-only: read the technique, don't depend on the repo as a dependency.

[repo](https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog) · [benchmark](https://lemire.me/blog/2026/04/27/you-can-beat-the-binary-search/)

## Unverified claims (tier C/D)

### parsing-and-text

#### text-search-and-indexing

##### trigrep  `Rust`  `no license`  `active`  `Tier C`

Rust CLI that pre-builds a disk-backed trigram index of a repo, then searches only candidate files, beating ripgrep in a first-party benchmark.

**Beats:** ripgrep — First-party README benchmark on a clone of git/git (4 patterns, 5 timed runs + 1 warmup each, index pre-built) reports mean query time 0.0405s for trigrep vs 0.0640s for ripgrep and 0.5990s for grep, i.e. ~1.58x and ~14.79x; medians for trigrep and ripgrep are tied at 0.0500s. Timed with `/usr/bin/time -p` (10ms resolution) over 20 samples; no CPU model or rustc version given, and index build time is excluded.

**How:** Indexing extracts every overlapping 3-byte trigram per file and writes a sorted, mmap'd lookup table (`lookup.bin`) plus posting lists (`postings.bin`), enabling binary search instead of a byte scan. At query time the regex is parsed into a `regex-syntax` HIR and decomposed into an AND/OR tree of literal trigrams; posting lists are intersected/unioned (smallest-first) to shrink the file set before the real regex engine ever runs. An 8-bit `loc_mask` (byte-offset adjacency) and an 8-bit `next_mask` Bloom filter on the following byte further prune false-positive candidates pre-verification. Indexing itself is parallelized with rayon.

**Use it when:**
- Large, mostly-static trees (git.git-scale or bigger) searched repeatedly, so index-build cost amortizes
- AI coding agents or scripted workflows issuing many regex searches per checkout, as the README targets
- Patterns with real literal content (e.g. TODO|FIXME, ^#include) that decompose into selective trigrams
- Need for grep-compatible text output or structured JSON output in the same tool
- Prebuilt-binary install wanted on Linux/macOS (x86_64/aarch64) or Windows (x86_64) without a Rust toolchain

**Skip it when:**
- One-off or rarely-repeated searches on a tree: index-build time is excluded from the published benchmark and isn't amortized
- Anything requiring code reuse or redistribution rights: no LICENSE file and no license field in either Cargo.toml, so it is reference-only
- Patterns with no extractable literal (bare character classes, anchors, `.`) fall back to a MatchAll node, losing index selectivity
- Decisions resting on the headline 1.58x: trigrep and ripgrep have the same 0.0500s median, so the gap is mean-only and close to the 10ms timer resolution used
- Concurrent or long-lived multi-process use where index staleness/locking matters: thread/process safety around the on-disk index is not documented

**Vs siblings:** Pick trigrep over ngi or ugrep-indexer mainly for its Cursor-derived on-disk format (mmap'd trigram lookup + loc/next-mask filtering) rather than for the strength of the evidence: ngi reports 1.7x-5.9x and ugrep-indexer 10x-21x with clearer separation, while trigrep's own numbers show tied medians and only a mean-based 1.58x over ripgrep.

**Gotchas:**
- Search auto-builds the index if missing, so a cold first query pays full index-build cost that the published benchmark excludes
- No LICENSE file and no license field in Cargo.toml: code can be read but not legally reused or redistributed
- The next_mask adjacency filter is a Bloom filter (false positives possible, no false negatives); correctness depends on the final real-regex verification pass, not the index alone
- `trigrep status` checks staleness against git HEAD but the index is not auto-refreshed on file edits without rerunning `trigrep index`

**Status:** Actively maintained (last commit 2026-04-30, 46 stars) but ships with no license, so usability is reference-only rather than reusable/redistributable.

[repo](https://github.com/PythonicNinja/trigrep) · [benchmark](https://github.com/PythonicNinja/trigrep#benchmark)

#### unicode-utf8

##### Parabix (bitstream UTF-16 validation kernel)  `C++`  `OSL-3.0`  `abandoned`  `Tier C`

Bitstream-parallel text-processing framework whose LLVM-JIT'd SIMD kernel beat a simdutf CLI wrapper on UTF-16 validation.

**Beats:** simdutf — On valid UTF-16LE corpora (128/256 MiB, single thread, Apple M1, median of 7 runs), a third-party benchmark measured Parabix's SIMD kernel at 2900-3760 MiB/s raw (5075-5205 MiB/s overhead-adjusted) against a simdutf v9.0.0 CLI wrapper (clang -O3 -std=c++17) at 1824-2532 MiB/s raw (1883-2600 MiB/s adjusted) -- about 1.18-2.0x raw and 2.0-2.7x adjusted -- but the simdutf wrapper reads the whole file into memory before validating while Parabix streams it, so part of the gap reflects I/O handling rather than the validation kernels.

**Known shortcoming:** The benchmarked UTF-16 validator is not in this mirror: it is a patch in an unlicensed 0-star student repo (dakshkashyap/cmpt479-project-group8), and its timings are whole-process runs dominated by file I/O rather than validation.

**How:** Core technique is Cameron et al.'s parallel bit-stream method: input is transposed (s2p) into 8/16 bitstreams, each holding one bit-position across the whole buffer, turning per-character branching into bitwise AND/OR/shift ops across a full register width, plus optional multicore pipeline parallelism (--thread-num). On this specific benchmark part of the apparent win is a process/I-O gap rather than kernel speed: Parabix streams the file through ReadSourceKernel while the simdutf wrapper CLI reads the whole file into a std::vector via ifstream before validating; the benchmark authors' own methodology doc says I/O is not equalized between the two.

**Use it when:**
- Building a new streaming text pipeline (regex search, XML parsing, transcoding) where adopting the whole Parabix framework is acceptable, not just linking a validator
- Multi-stage text transforms where replacing many per-character branches with bitwise ops across a full register/vector width is the goal (icgrep-style regex matching)
- Research or teaching on bit-parallel SIMD algorithms and LLVM JIT code generation
- Environments that can carry an LLVM 5+/Boost 1.61+/Z3/CMake toolchain at both build and run time
- Workloads that also want multicore pipeline parallelism (thread-num > 1) inside the same kernel model

**Skip it when:**
- You need a small, embeddable UTF-8/UTF-16 validator with a stable C/C++ API — no such component exists in this mirror; use simdutf directly
- Startup latency matters: Parabix's LLVM JIT pipeline load adds ~0.019s fixed overhead per process vs ~0.002s for simdutf, dominating small-input timings
- You need permissive licensing — Parabix/icgrep is OSL-3.0 (strong copyleft), unlike simdutf's permissive license
- You need an actively maintained project — no commits on this mirror since 2021-08-10
- You need UTF-8 rather than UTF-16 — this benchmark and the validator it measures are UTF-16LE only

**Vs siblings:** None of the catalogued UTF-8 siblings (ada-url/idna, simdutf8, xutf, SimdUnicode, utf8_range) target UTF-16, so there's no direct sibling for this workload; pick Parabix over building your own UTF-16 path only if you're already adopting its whole bit-parallel framework for other text processing, not for a standalone validator.

**Gotchas:**
- The benchmarked tools/utf16validate isn't in this GitHub mirror; it's added by a third-party patch to Parabix commit f0369dd pulled from the SFU GitLab, and that commit postdates this mirror's last sync (2021-08-10)
- Fixed per-process overhead (~0.019s, mostly LLVM JIT pipeline load) is roughly 9x simdutf's (~0.002s) — raw wall-clock throughput on small inputs is dominated by this, use the benchmark's overhead-adjusted numbers instead
- GitHub reports this repo's license as NOASSERTION even though the README and OSL3.0.txt/LLVM-LICENSE.txt in the tree declare OSL-3.0 for Parabix code and the LLVM Release License for vendored LLVM files
- This is a read-only mirror: it does not accept GitHub pull requests; patches go to an SFU GitLab research repo instead

**Status:** Abandoned on this mirror since 2021-08-10 (no evidence in this session of active development elsewhere) and usability is mixed: it's a research framework with no stable API, requiring a full LLVM/Boost/Z3 build toolchain rather than a library you can drop in.

[repo](https://github.com/parabix/parabix-devel-mirror) · [benchmark](https://github.com/dakshkashyap/cmpt479-project-group8/blob/main/results/utf16_benchmark_apple_arm64_summary.md)

### serialization-and-formats

#### binary-schemas

##### MTS-1 (Lightweight Delta-Encoded Telemetry Format)  `Rust`  `CC-BY-4.0`  `unknown`  `Tier C`

Rust per-packet binary telemetry format (MTS-1/MWire) reporting ~5% smaller payloads than MessagePack on synthetic host metrics.

**Beats:** MessagePack — The only claim is size: on a synthetic 10k-record set, per-packet MTS-1 totals 1,390,000 B vs 1,469,521 B for MessagePack (rmp-serde, structs as arrays) and 5,475,079 B for JSON (5.4% and 74.6% smaller), and the 20k and 50k sets scale linearly. Protobuf was not measured, and no compiler, hardware or timings are given. My arithmetic on the repo's generator reproduces the MessagePack and MTS-1 byte counts exactly for all three sizes.

**Known shortcoming:** Size-only claim, no speed numbers. The benchmark generator runs with delta encoding off on synthetic sin/cos data at 1 s intervals, so the 139 B/record is the fixed packet size. The MessagePack baseline stores the UUID as a 36-char string; with a binary UUID MessagePack would be about 127 B and win (derived from the generator, not measured). No root LICENSE file although the README says MIT.

**How:** The win is in size, not speed. Each present field is a 1-byte tag (3-bit type, 5-bit field number) followed by a fixed-width little-endian value, absent fields are skipped, and the UUID is stored as 16 raw bytes. In the paper's generator this gives a constant 139 B per record: a 2 B length prefix, 15 B header, 18 B device ID, 16 B UUID, 84 B payload and 4 B CRC. The 'delta' mode is change suppression: a delta packet or frame carries the new values of fields that changed (optionally only past a per-field epsilon), not arithmetic differences. Per-packet LZ4 (lz4_flex block mode) is optional.

**Use it when:**
- Reproducing or auditing the paper: the repo's generate_dataset binary and committed tele20k/tele50k files let you re-derive Table I byte counts.
- Rust host agents sending fixed host metrics (CPU %, temperature, frequency, memory, disk, network counters, uptime) where you own both ends and want a checksummed packet with timestamp, sequence number and a LAN-proxy flag.
- Slowly changing metric streams stored as JSON arrays, where the MTS1 stream mode stores field names once and writes only changed fields between snapshots (every 10th record by default).
- As a small reference design for a telemetry packet layout: the core crate is about 100 KB of Rust in 7 files, with no unsafe code.

**Skip it when:**
- You need speed numbers. No encode or decode timings are published. The README's ~65,000 encode / ~112,000 decode records/s gives no hardware, method or baseline, and no results from the criterion comparison bench are published.
- You want a fair size win over MessagePack. The 5.4% margin exists because the baseline stores the UUID as a 36-char hex string (38 B) while MTS-1 stores 16 raw bytes. By my arithmetic on the generator code (not a measurement), rmp-serde MessagePack with a binary UUID would be ~127 B per record vs MTS-1's 139 B.
- C++ codebases, or platforms without prebuilt artifacts. It is Rust only, with no C/C++ API. The only prebuilt artifacts are a Windows x86-64 mwire.exe and a single PyPI wheel (magenta-telemetry 0.1.0, CPython 3.11 win_amd64). Nothing is published on crates.io.
- Untrusted input. The decoders call `Vec::with_capacity` / `HashMap::with_capacity` with u32 counts read from the packet, and CRC32 is not authentication, so a crafted packet can request very large allocations.
- Production dependencies. It is single-author code (5 stars, 6 commits from 2026-02-15 to 2026-03-01, no issues filed) with no root LICENSE file. The packet format has a fixed field table (numbers 0-31). A lost snapshot breaks delta reconstruction, and an epsilon above 0 makes delta mode lossy.

**Vs siblings:** Pick it only if you want a ready-made, CRC-checked host-metrics packet in Rust. For compactness alone, JSON BinPack (smallest or tied-smallest across 27 documents) and qdf (IoT/OTLP batch fixtures) have broader size evidence, and fernBuffer's MessagePack comparison covers more data shapes.

**Gotchas:**
- The paper's 'delta-encoded' results do not use delta mode. generate_dataset.rs calls `encode()` on full records with `is_delta` false, so Table I measures plain fixed-width packets. The constant 139 B per record is therefore the natural packet size, not evidence of computed numbers.
- The paper and the code describe different methods. The paper cites real Magenta samples at ~30 s intervals and deltas of c_i - c_(i-1). The generator uses sin/cos synthetic values at 1 s intervals with one device ID and UUID, and delta frames carry replacement values. The paper's 100-host example (1.95 GB vs 0.24 GB, '87.7%') also disagrees with its own 548 B vs 139 B per payload.
- The two spec documents disagree. docs/FORMAT.md's type-ID table (e.g. 0x01 = Null) and its legacy flag bits do not match core/src/types.rs and encoder.rs, which follow FORMAT_SPEC.md (0x06 = Null, delta = flag bit 4). Treat the code as the spec.
- Per-packet LZ4 makes these packets larger (2,794,270 vs 2,780,000 B on S2) because `compress_prepend_size` adds a 4-byte length and the ~84-byte payload barely compresses. Only the stream mode's whole-body LZ4 pays off: DISTRIBUTION_README reports 1,340,041 vs 4,440,224 B on a 25,957-record dataset.

**Status:** Single-author research code behind a non-peer-reviewed January 2026 arXiv preprint: last commit 2026-03-01, one v1.0.0 Windows release, MIT according to the README and Cargo.toml but with no root LICENSE file; use it as a reference, not a maintained dependency.

[repo](https://github.com/ndourc/mwire) · [benchmark](https://arxiv.org/abs/2601.01602)

##### psio / pSSZ (successor to fracpack)  `C++`  `no license`  `active`  `Tier C`

C++23 reflection-driven, SSZ-derived binary format with zero-copy views; author benchmarks show faster encode/decode than libprotobuf, capnp, FlatBuffers, msgpack.

**Beats:** Protobuf, Cap'n Proto, FlatBuffers, MessagePack — On the author's own psio_bench_vs_externals harness (unspecified Apple M-series, llvm-clang 22.1, -O3 -DNDEBUG, library versions not stated), per-shape geomeans show libprotobuf 6.4x slower than pSSZ to decode and 43x slower to encode, FlatBuffers 1.23x slower to decode and 2.3x slower on a single-field view, and Cap'n Proto 5.4x slower to decode and 48x slower on a view. The comparison is weaker than it looks: the external encode cells include copying a native C++ struct into the library's builder or message, FlatBuffers and capnp 'decode' means materializing a native struct, the validate ratios are against psio's own re-implementations of those formats, and the anchor CSV is not committed.

**Known shortcoming:** The validate ratios are against psio's own reimplementations of protobuf, flatbuffers and capnp, not the canonical libraries. The C++ core has no LICENSE file (only the Rust and npm manifests declare MIT). Published ratios are latency, measured on an unspecified Apple M-series chip.

**Known shortcoming:** The competitor encode timings include copying a native struct into each library's builder, FlatBuffers/capnp 'decode' builds a full native struct, and the capnp view timing constructs a new reader per call, likely inflating the 43-82x and 47.57x ratios. Decode and view are unchecked (only validate reports errors). Verified only on macOS ARM64; host byte order only; requires C++23, Boost and Homebrew LLVM on macOS.

**How:** Each record is a fixed region (scalars inline, one offset slot per variable field) followed by a dynamic region, so a field's position is a compile-time constant that a view reads with one load, and a variable field's size comes from the next offset instead of a length prefix. The offset width (1, 2 or 4 bytes) is chosen per type at compile time from length_bound and maxDynamicData annotations. Records marked definitionWillNotChange() (DWNC) drop the extensibility header, and a trivially copyable, unpadded DWNC record (or a vector of them) encodes and decodes as one memcpy. Validation is one bounds check per offset slot, with nesting depth capped at 64.

**Use it when:**
- C++23 services that exchange existing structs between processes you control, and want to serialize them with no separate IDL or codegen step.
- Read-heavy paths that pull one field out of a validated buffer. The spec's view_one table shows 0.33-0.56 ns for pSSZ, against 0.58-3.46 ns for FlatBuffers and 17-28 ns for Cap'n Proto on the same shapes.
- Content-addressed or signed payloads that need exactly one canonical byte sequence per value (spec §15).
- Bulk arrays of fixed-layout records such as validator or tick lists. Marking the record DWNC and trivially copyable turns encode and decode into a memcpy.
- Small bounded messages, where length_bound annotations shrink offset slots and headers to 1 or 2 bytes.

**Skip it when:**
- Integer-heavy or sparse payloads where wire size matters most. In the author's table Avro, MessagePack and Protobuf are 0.56-0.65x pSSZ's raw size. The gap narrows to 0.87-0.91x after zstd-1.
- Streaming or incremental parsing. Offsets are container-relative, so the whole container must be in memory before any field can be read.
- Polyglot systems. pSSZ exists only in C++ and Rust: JS/TS has no pSSZ, and no Python, Go or Java port exists. psio's own Protobuf, MessagePack, capnp and FlatBuffers codecs are covered by only two shared fixture records each.
- Production code or code that parses untrusted input today. The library is at 0.1.0 with no tags or releases and no LICENSE file, and it has been verified only on macOS ARM64. Its own release checklist asks for sanitizer and fuzz jobs 'before accepting untrusted inputs'.
- Builds with -fno-exceptions or for WASI guests. The docs say the exception-free profile is incomplete: headers still contain unguarded throws.

**Vs siblings:** Pick pSSZ when both ends run C++ (or Rust) and you want one reflected struct declaration to give zero-copy single-field reads, canonical bytes and append-only schema evolution together, and you can accept a pre-release, unlicensed codebase. Pick hpp-proto if you must stay on the Protobuf wire, and rkyv for a Rust-only zero-copy codebase.

**Gotchas:**
- Only validate reports errors. error.hpp says decode and view accessors assume the input has already been validated, so call psio::validate<T>(psio::pssz{}, bytes) on every untrusted buffer first. The 64-level depth cap applies to validate, not to decode.
- The offset width W is derived from the type and never stored on the wire. Changing a length_bound in a way that flips W, or adding definitionWillNotChange() to an existing record, silently breaks bytes that are already stored. Encoding more than maxDynamicData throws codec_exception.
- Unknown trailing fields are silently dropped, strings are not checked for UTF-8 unless you use validate_strict (which also fully decodes), and appending a variant-typed field is not a safe evolution.
- The spec promises single-pass encode, but the C++ encode entry point first runs size_of over the value and then writes into the pre-sized buffer with unchecked memcpy (fast_buf_stream).

**Status:** Actively worked on (last push 2026-09-16) but pre-release, so treat it as a reference design rather than a dependency: version 0.1.0, 0 stars, no tags or releases, verified only on macOS ARM64, and no LICENSE file (the Rust and npm manifests declare MIT, while the C++ core declares no license).

[repo](https://github.com/gofractally/psio) · [benchmark](https://github.com/gofractally/psio/blob/main/docs/format-comparison.md)

#### yaml-toml-xml

##### SupXML (sup-xml)  `Rust`  `Proprietary source-available (Supported Source; LICENSE requires a paid or free-tier license certificate to use the code; not OSI)`  `active`  `Tier C`

Source-available Rust XML stack with a libxml2-compatible C ABI; the vendor reports ~2.1x median DOM-parse throughput over libxml2.

**Beats:** libxml2 — This is a first-party bench (cargo bench -p sup-xml-bench --bench head_to_head). It compares sup-xml's bumpalo-arena DOM (parse_bytes_unchecked, default options, input copied into an owned buffer) with libxml2 xmlParseMemory plus xmlFreeDoc through FFI, taking best-of-N MiB/s per fixture. The 11 fixtures shown range from 1.61x to 3.75x, the claimed median over 21 is ~2.1x, and the XSTS 1.0 wall-clock is 2.86 s vs 6.81 s with libxml2's 3 timeouts excluded. No CPU, OS, rustc version, flags or libxml2 version is disclosed; build.rs links whatever libxml2 pkg-config or the macOS system provides, and the numbers have not been independently reproduced.

**Known shortcoming:** Proprietary source-available licence (needs a licence certificate). The timed SupXML run skips UTF-8 validation (parse_bytes_unchecked) while libxml2 validates inside its timing, contradicting the page's 'matched contract' claim. No CPU, rustc or libxml2 version; the repo's own COMPARISON.md says only ~1.0-1.3x vs libxml2; the XSD validation text and table disagree. 1 star.

**Known shortcoming:** The timed run also skips encoding sniffing and namespace processing (namespace_aware false) while libxml2 is namespace-aware; best-of-2, no warmup. The project's documents contradict each other (COMPARISON.md ~1.0-1.3x vs the docs page's ~2.1x; W3C suite 255/257 vs 244/257). By its own numbers quick-xml streams faster on 4 of 5 fixtures and its fastest DOM mode reaches about half of pugixml. The libxml2 C shim frees arenas only at thread exit and is off by default because linking it with real libxml2 is undefined behaviour. Parsing hard-fails without a licence certificate. Enrichment confidence 0.4.

**How:** The tokenizer is a strict byte-level SAX reader built on memchr SIMD searches. Text runs scan for '<', '&' and ']' in one memchr3 pass. A start tag jumps to the first '>' and accepts it if a memchr2 count of both quote characters before it is even; otherwise it falls back to a quote-aware scan. XML Name characters are checked against 256-entry ASCII lookup tables. XML 1.0 §2.2 character validation is one upfront SWAR pass over the whole document (the has-zero-byte trick, 8 bytes per iteration) instead of per-token checks, and UTF-8 is validated with simdutf8 (AVX2/SSE4.2/NEON dispatch). The DOM uses libxml2-shaped nodes allocated in one bumpalo arena per document, so each node costs a pointer bump and the whole arena is freed at once. Strings are borrowed from the owned source buffer where possible. An opt-in parse_bytes_in_place mode decodes entities inside the input buffer to avoid copies.

**Use it when:**
- Rust services that need libxml2-class features (XSD 1.0 validation, XPath 1.0, XSLT, C14N for XML-DSig/SAML, recovery mode) without linking C, and that can get a Supso certificate: paid commercial, free 30-day evaluation, or free hobbyist for non-monetized projects
- DOM-parsing UTF-8 documents from about 15 KB to 95 MB into an owned tree. The vendor's table shows 1.61x (pubmed) to 3.75x (Arabic gazali_maqasid_ar, 599 KB) over libxml2's xmlParseMemory; the largest gains are on text-heavy and non-ASCII documents
- XSD pipelines with complex Microsoft-style particle and derivation schemas. On W3C XSTS 1.0, libxml2 goes quadratic and times out at 30 s on 3 schemas that SupXML compiles in under 1 ms, and total schema-compile time is 1.74 s vs 3.96 s
- Browser or edge runtimes that need XML, XPath, XSLT, XSD or HTML parsing: it builds for wasm32-unknown-unknown with every feature except network-resolver
- As a reference design for a strict, validating XML tokenizer built from memchr, SWAR and lookup tables

**Skip it when:**
- Any open-source, redistributable or unlicensed deployment. The LICENSE is proprietary Supported Source (not OSI), and every document-parse entry point returns a fatal error unless a valid certificate is found
- Pure streaming or event workloads. The vendor's own page shows quick-xml faster on 4 of the 5 fixtures it lists (nasa 0.74x, swiss_prot 0.59x, wikipedia_ww2 0.11x), with only ~1.04x median across 21 fixtures at the matched contract
- Maximum DOM speed on trusted input. Its own docs say parse_bytes_in_place with all four skip_* flags reaches 'roughly half of pugixml's throughput', and pugixml-beating siblings go further
- HTML parsing for speed. It wraps html5ever and is at parity with libxml2 (~1.02x geomean on the docs page); COMPARISON.md even shows hn.html at 35 vs 45 MiB/s
- Long-running processes that use the C-ABI shim on persistent threads, because per-document arenas are freed only at thread exit. Also note the maturity: 1 contributor, 1 GitHub star and 121 crates.io downloads

**Vs siblings:** Choose it over yxml, quick-xml, xmloxide or rusty_xml only when you need libxml2's broader surface (XSD, XSLT, XPath, C14N, recovery) in memory-safe Rust or behind a libxml2 C ABI, and you are willing to license it. For plain streaming, quick-xml beats it on most fixtures in SupXML's own table. yxml offers a similar ~2.2-2.4x over libxml2 in a tiny C SAX parser. xmloxide is the other pure-Rust libxml2 reimplementation, catalogued at roughly libxml2 parity.

**Gotchas:**
- Runtime license gate: the first parse in a process looks for a certificate (SUPSO_LICENSE_PATH, ~/.supso/license_certificates/, ./.supso/license_certificates/). Without one, every parse returns a fatal error. An expired certificate only gets a logged grace period before parsing fails.
- The headline benchmark is not symmetric. The timed sup-xml call is parse_bytes_unchecked, which skips encoding sniffing and SIMD UTF-8 validation (the harness checks UTF-8 outside the timer). It also runs with the default namespace_aware: false, so there is no xmlns scanning or QName resolution. libxml2's xmlParseMemory does detection and validation inside the timer and uses its namespace-aware SAX2 interface. Timing is best-of-N with no warmup (default N=2), and 'MB/s' is actually MiB/s.
- The project's own documents disagree. COMPARISON.md gives ~1.0-1.3x median vs libxml2 against the docs page's ~2.1x. The README claims 255/257 on the W3C XML Conformance Suite, but the COMPARISON.md table shows 244/257. An XSD instance-validate time of 1.12 s vs 2.85 s is described as 'parity'. A bench comment still says gazali parses at ~14 MB/s vs libxml2's ~140 MB/s.
- The defaults differ from libxml2: namespace_aware is false (set it true for prefixed XPath), there is a 1 MB entity-expansion cap and a depth limit of 256, and external DTDs are not loaded. The 'memory-safe' claim is scoped: unsafe code is allowed in the scanner, readers, parser, encoding and dom.rs, and the C shim is #![allow(unsafe_code)] even though CONTRIBUTING lists the shim among the forbid-unsafe modules.

**Status:** The project is actively developed by a single maintainer (111 commits from one contributor; v1.3.0 released 2026-06-17; last commit 2026-06-20). It is reference-only here because the proprietary Supported Source license requires a paid or free-tier certificate, and parsing fails without one.

[repo](https://github.com/SupsoOrg/sup-xml) · [benchmark](https://supso.org/projects/sup-xml/docs/reference/performance/)

### stdlib-replacements

#### allocators

##### arena-allocator (ShortAlloc)  `C++`  `no license`  `stale`  `Tier C`

Single-file bump-pointer arena allocator with an STL-compatible wrapper; beats glibc malloc via std::vector, especially above the mmap threshold.

**Beats:** operator new/delete (GNU/glibc malloc via std::vector's default std::allocator) — On QuickBench (clang 17.0, -O3, -std=c++20, libstdc++, single CPU core from a shared AWS pool), std::vector<TestClass, ShortAlloc> doing 100 emplace_back calls was 2.2x-4.4x faster than std::vector's default allocator (glibc malloc) for 8B-512B objects, and 93x-230x faster for 1KB-8KB objects — the latter driven by the default allocator crossing glibc's mmap threshold during vector reallocation, not a general per-allocation speed advantage at that size.

**How:** Allocation is a pointer bump plus an alignment round-up (no free-list search, no locking, no syscalls) as long as the arena has room, so it stays in cache and skips heap-manager bookkeeping entirely. The largest gains (93x-230x) show up once std::vector's reallocations grow past glibc's mmap threshold (~128KB total), where the default allocator pays for an mmap syscall and first-touch page faults that the arena avoids by staying on the stack-backed buffer.

**Use it when:**
- Short-lived, single-threaded scopes with a known upper bound on total allocation, e.g. a function-local std::vector that shouldn't touch the heap
- Many same-sized emplace_back/reallocation cycles where the arena can be sized to the container's peak footprint
- LIFO-order allocate/deallocate patterns, since deallocate() only reclaims the block at the top of the arena
- Containers whose elements grow into the 1KB-8KB+ range, where you want to sidestep glibc's mmap-threshold latency cliff
- Reference/teaching use: a ~180-line file showing a bump allocator plus STL-allocator plumbing

**Skip it when:**
- Multi-threaded code — no locking or atomics in Arena or ShortAlloc; concurrent use is undefined behavior
- Workloads needing out-of-order or random-order frees, since only the most recent allocation can be reclaimed
- Long-running or size-unbounded containers — the arena is a fixed std::array<N> and silently falls back to global operator new once exhausted, with no bookkeeping to route the matching free back correctly
- Anywhere licensing matters — the repo ships no LICENSE file, so reuse terms are undefined
- Copy-pasting the repo as-is into production — the committed source has active std::cout debug prints in allocate()/deallocate() that the benchmarked version did not have

**Vs siblings:** Pick this over general-purpose allocator replacements in the catalog (Hoard, SuperMalloc, NUMAlloc, scalloc) when you want a tiny, dependency-free, single-file bump allocator for a bounded, single-threaded, LIFO-style scope rather than a global malloc replacement for multi-threaded programs. Against the other same-domain arena-allocator (yaroslavaristov), prefer that one for broader, harder benchmark evidence (AMD EPYC and Apple M1, direct malloc/free comparison); prefer this one specifically for the ready-made STL-compatible ShortAlloc wrapper usable as std::vector<T, Alloc>.

**Gotchas:**
- The GitHub source (arena-benchmark.cpp) has its std::cout diagnostic lines active inside allocate()/deallocate(); the QuickBench snippet that produced the published numbers has those lines commented out, so running the repo file as-is will not reproduce the benchmark
- deallocate() silently no-ops (leaks the block) if you free anything that isn't both in-buffer and the most-recently-allocated block — no error or assertion is raised
- Once the arena is exhausted, allocate() falls back to ::operator new, but deallocate() has no bookkeeping to route those heap-backed blocks to ::operator delete except via the top-of-stack pointer check — mixed arena/heap blocks can be freed incorrectly
- The free operator== / operator!= for ShortAlloc reference a nonexistent `rhs.arena` member (the field is actually private `d_arena`) and access it without a friend declaration — this code would fail to compile if a container ever invoked allocator comparison

**Status:** Stale (last commit 2025-03-13, 9 GitHub stars, no open issues, no LICENSE file) and marked 'reference' usability — best read as a worked example of a bump allocator plus STL-allocator wiring rather than adopted as-is; the repo currently ships the un-optimized, debug-print-enabled source, so strip those lines before reusing it.

[repo](https://github.com/shantanu/arena-allocator) · [benchmark](https://github.com/shantanu/arena-allocator#%EF%B8%8F-performance-benchmarks)

##### SpeedMalloc  `C++`  `no license`  `unknown`  `Tier C`

Hardware support-core design offloading malloc/free; gem5-simulated 1.75x throughput over jemalloc, no real silicon exists.

**Beats:** jemalloc (also compared against TCMalloc, mimalloc, Mallacc, Memento) — In gem5 full-system simulation (1-16 AArch64 out-of-order big cores + 1 in-order support core, GCC 9.4 -O3 -march=armv8.1-a), the paper reports SpeedMalloc achieves 1.75x/1.18x/1.15x/1.23x/1.18x geomean throughput over jemalloc/TCMalloc/mimalloc/Mallacc/Memento+ across 10 multithreaded workloads (7 from mimalloc-bench, GAPBS BFS and BC, NAS DC), with smaller single-threaded gains of ~1.09x/1.08x/1.04x/1.03x over jemalloc/TCMalloc/mimalloc/Mallacc. It never compares against glibc malloc or std::allocator directly.

**How:** Metadata never touches main-core caches: the support-core holds a segregated free-list layout in its own L1, eliminating the cache pollution and cross-core atomic-instruction traffic (up to ~22.8% of cycles in the paper's jemalloc/TCMalloc profiling) that shared/thread-local allocator metadata causes today. Hardware message queues (dispatcher, malloc/free queues, scheduler, response queue) in the support-core pipeline and round-robin allocation requests from up to 16 cores instead of serializing on coherence traffic. free() is fire-and-forget and returns to the main core immediately (processed asynchronously off the critical path); malloc() only stalls the main core if it has no independent work to overlap while waiting for the support-core's 'end' signal.

**Use it when:**
- You're researching or designing CPU memory-subsystem hardware and want a concrete design point for offloading allocator metadata to a dedicated core
- Comparing hardware-accelerated allocator proposals (Mallacc, Memento) for multithreaded, many-core AArch64 systems
- Need a gem5 full-system reference for quantifying cache-pollution and metadata-synchronization overhead across allocators
- Interested in the paper's 'butterfly effect' data: allocation is ~4.4% of instructions but choice of allocator swings whole-program performance up to 2.7x

**Skip it when:**
- You need something to link into a real program today: has_code is false, no repo, no artifact was published with the paper
- Your target is x86 or any platform without a custom support-core wired above the LLC and a modified ISA/compiler toolchain
- Single-threaded or lightly threaded workloads: SpeedMalloc's edge there is only ~1.09x/1.08x/1.04x over jemalloc/TCMalloc/mimalloc
- You need peer-reviewed or independently reproduced results: this is a v1 arXiv preprint ('manuscript submitted to ACM'), not yet reviewed
- Any production or deployment use case: the authors state they could not prototype even on FPGA because the required ISA and coherent-bus hardware do not exist in current systems

**Vs siblings:** Not applicable for real use: every catalogued sibling (metapool, NUMAlloc, SuperMalloc, Hoard, scalloc, both arena-allocators, ltalloc, rpmalloc, smmalloc) is a software allocator you can build and link today, while SpeedMalloc requires hardware that does not exist. Treat it only as a research reference for hardware/software co-design ideas, never as a substitute for any of the software allocators.

**Gotchas:**
- Interrupts and exceptions are masked on the main core while it waits for the support-core's 'end' signal during a malloc() call
- free() completes asynchronously off the critical path, so its completion is not visible/synchronous to the caller
- Gains are concentrated in multithreaded workloads (1.75x geomean over jemalloc); single-threaded gains are much smaller (~1.09x)
- No FPGA or real-silicon prototype exists — footnote 8 states current ISA and hardware cannot support one; every number is gem5-simulated

**Status:** Research preprint only (arXiv v1, Aug 2025, 'manuscript submitted to ACM'), not peer-reviewed and with no linked code or artifact; usability is 'reference' and maintenance status is not applicable since nothing is released to maintain.

[benchmark](https://arxiv.org/abs/2508.20253)

#### async-tasks-threadpools

##### meet1214/thread-pool  `C++`  `no license`  `active`  `Tier C`

Header-only C++17 fixed-size thread pool with typed futures and exception propagation, beats std::async by reusing worker threads.

**Beats:** std::async — README's own benchmark/benchmark.cpp, run once on an unspecified 4-core Linux box with no compiler or flags stated, timed 100 std::sqrt-loop tasks: single-threaded 68ms, std::async 18ms (3.8x), ThreadPool at 4 threads 10ms (6.8x) and at 8 threads 7ms (9.7x) — all relative to the single-threaded run; against std::async directly that's about 1.8x (4 threads) to 2.6x (8 threads) faster.

**How:** Amortizes thread-creation cost: std::async(std::launch::async, ...) typically spawns a fresh OS thread per call, while ThreadPool spawns n threads once and reuses them across all submitted tasks via a locked queue. Workers block on a condition_variable when idle (no busy-waiting). No lock-free structures, work stealing, or SIMD — the entire speedup story is 'don't call clone()/pthread_create() 100 times.'

**Use it when:**
- Many short-lived CPU-bound tasks where std::async's per-call thread spawn is the dominant cost
- You want a drop-in-shaped replacement for ad-hoc std::async fan-out with typed futures and exception propagation
- A single-header dependency is acceptable and you can vendor code without a LICENSE file being a blocker (internal/prototype use)
- A fixed, known worker count is fine and you don't need cancellation or priorities
- Teaching/reference use: the README's architecture section is a clear worked example of the packaged_task + shared_ptr pattern for storing move-only tasks in std::function

**Skip it when:**
- Any production dependency where a license is required — there is no LICENSE file despite an MIT badge in the README (404 on GitHub)
- Workloads needing task cancellation, priorities, or dynamic pool resizing — none are implemented
- High task-submission-rate workloads — single global queue/mutex/condvar means no work stealing and one contention point across all workers
- Any decision that needs trustworthy performance numbers — the published benchmark shows superlinear speedup (3.2x on 2 threads, 9.7x on 8 threads, all on a 4-core machine), a single untimed-repetition run, and an unoptimized default build
- Projects wanting an actively maintained, community-vetted pool — 0 stars, single author, no issues or PRs, so no external validation exists

**Vs siblings:** Pick this only as a tiny, license-free-to-check, easy-to-read reference implementation of the packaged_task/shared_ptr pattern; for real use, BS::thread_pool (also header-only, mature, widely used) or utl::parallel (also targets std::async, with a somewhat more detailed benchmark) are safer choices since both have far more scrutiny and, in BS::thread_pool's case, an actual license.

**Gotchas:**
- No LICENSE file exists despite the README's MIT badge — legal status of reuse is actually undefined
- CMakeLists.txt sets no CMAKE_BUILD_TYPE and only passes -Wall -Wextra, so the documented `cmake -B build && cmake --build build` produces an unoptimized (likely -O0) benchmark and test build
- Single shared queue/mutex/condvar design (no work stealing) means throughput will not scale past the point where lock contention dominates, unlike pools built for high task-submission rates
- The benchmark's std::async row spawns 100 OS threads for 100 tasks, so the reported 'ThreadPool beats std::async' number is largely measuring thread-creation overhead, not scheduling efficiency

**Status:** Repo shows recent activity (last push 2026-04-01, marked active) but has zero stars, one author, no issues/PRs, and no LICENSE file, so despite MIT branding it is usable only as a reference, not a dependency to actually take on.

[repo](https://github.com/meet1214/thread-pool) · [benchmark](https://github.com/meet1214/thread-pool#benchmark-results)

#### bitsets-and-succinct

##### better_bitset  `C++`  `no license`  `abandoned`  `Tier C`

Header-only C++20 bitset adding fast first_one/first_zero bit-scan that std::bitset lacks above 64 bits.

**Beats:** std::bitset — First-party Google Benchmark (compiler/flags unstated) on a 20-logical-core ~3.6GHz host: better_bitset::first_one() beats a naive std::bitset .test(i) bit-by-bit loop from N=8 through N=8192 (e.g. 18,134ns vs 953,294ns at N=8192, ~52.6x; 1,789ns vs 128,450ns at N=1024, ~71.8x), but is ~1.6x slower than std::bitset at N=4 (405ns vs 250ns). The mean of the 13 per-size ratios is ~34x, well below the README's claimed '60x average'.

**How:** first_one()/first_zero() call std::countr_zero()/std::countr_one() on each 64-bit (or smaller) storage chunk instead of the .test(i) bit-by-bit loop std::bitset forces on scans above 64 bits. On x86 these compile to a single hardware bit-scan instruction (the BSF/TZCNT family) per chunk, turning an O(N) per-bit test into O(N/64) chunk-level instructions. No SIMD or manual vectorization beyond whatever the compiler emits for those built-ins.

**Use it when:**
- Fixed-size bitsets above 64 bits where you need the position of the first set/unset bit (e.g. slot allocation) without hand-writing a scan loop
- Bitsets of 16 bits or fewer, where the smaller backing integer type (uint8_t/uint16_t) saves a few bytes versus std::bitset
- You're willing to vendor a single ~200-line header and require only C++20, with no upstream support expected
- Reference/inspiration for implementing your own countr_zero/countr_one-based bit-scan rather than using the library directly
- N is not tiny: the measured gains hold from N=8 up through N=8192 in the authors' own benchmark

**Skip it when:**
- You need bitwise operators (&, |, ^, ~) between bitsets — not implemented
- You need std::bitset's assignable reference proxy (bs[i] = true) — operator[] here is const-only
- You need a maintained dependency — inactive since last commit 2022-04-08, 8 stars, two open issues with no response
- You need to ship/vendor code under a known license — no LICENSE file exists and an open issue (#4) asking for one is unanswered
- Your bitsets are consistently very small (N=4) — the authors' own benchmark shows better_bitset ~1.6x slower than std::bitset there

**Vs siblings:** Pick better_bitset over plf::bitset only if you want a single tiny header with zero build configuration and care solely about first_one/first_zero on fixed-size bitsets above 64 bits; plf::bitset covers more operations (set_range/reset_range, shifts) with gains measured on both GCC and MSVC and is the more complete std::bitset alternative in this catalog. For runtime-sized bitsets use sul::dynamic_bitset or BitLib instead (they target std::vector<bool>), and for sparse/succinct workloads use CRoaring or pasta::bit_vector.

**Gotchas:**
- No LICENSE file in the repo; an open, unanswered GitHub issue (#4, filed 2024-11-03) asks the maintainer to add one — treat the code as look-but-don't-ship
- Open issue #3 (2024-10-01, unaddressed) disputes the correctness of first_one/first_zero for some bit patterns; unresolved since the repo has had no commits since 2022
- Benchmark numbers are self-reported with no stated compiler or optimization flags (the CMakeLists sets neither CMAKE_BUILD_TYPE nor compile options), so real gains under -O2/-O3 may differ
- Only smaller than std::bitset for N<=16; at N=4 in the authors' own benchmark it was slower than std::bitset's naive loop (405ns vs 250ns)

**Status:** Abandoned since its last commit on 2022-04-08 (8 stars); no LICENSE file exists and a 2024 issue asking for one is unanswered, so it's readable reference code, not something to vendor as-is.

[repo](https://github.com/MrElectrify/better_bitset) · [benchmark](https://github.com/MrElectrify/better_bitset/blob/master/benchmark/results.txt)

#### hash-maps-sets

##### CYBHash  `C++`  `no license`  `stale`  `Tier C`

Header-only bit-packing + BMI2 pext lookup for fixed-format Chinese futures/stock/option ticker symbols, vs std::unordered_map.

**Beats:** std::unordered_map — The README states CYBHash is 'approximately 10 times faster than std::unordered_map' for symbol-to-value lookup, while the repo's separate GitHub description says 'approximately 5-30 times faster' -- the two first-party figures disagree. testCYBHash.cc + test.sh do contain a real benchmark harness (bench_file_unordered_map alongside the symbol-table benches, run via g++ -std=c++17 -mbmi2 -O3 -DNDEBUG over bundled combine.txt/shfe.txt/stock.txt/dce.txt/option.txt files), but no output numbers, hardware, or compiler version tied to the README's claim are published anywhere in the repo.

**How:** Each fixed-length ticker string (5-16 bytes) is packed into a uint64 id via per-table bit-selection logic (get_id), then find_min_mask_by_cost greedily/bruteforce-searches for a small bit mask whose _pext_u64 (BMI2 pext instruction) extraction gives few collisions across the known key set. Lookups become one pext plus linear-probe over a flat vector<pair<id,value>>, skipping std::unordered_map's string hashing and bucket-chain traversal entirely. The idea is borrowed from qlibs/mph (pext-based hashing) and MengRao/str (fast fixed-size string keys, bundled as Str.h/StrHash.h though unused in the active benchmark path).

**Use it when:**
- Keys are exactly Chinese futures/stock/option ticker symbols (5-16 ASCII chars, e.g. '600000.SSE', 'eb2505-C-10000') that fit this project's packing rules
- The key set is known/stable before the hot lookup loop (build via sync_with_unordered_map() once, then read-only queries)
- Running on x86-64 hardware with BMI2 (pext) available
- Throughput on symbol->value lookup matters more than general-purpose map semantics
- You are prototyping/studying the technique rather than shipping it verbatim (no license to redistribute)

**Skip it when:**
- Any key format other than these narrow ticker patterns -- get_id()'s bit layout is hard-coded per table type, not a general string hash
- Keys are inserted/removed continuously; the design assumes a build-then-freeze workflow, not interleaved mutation
- Target platform lacks BMI2 (older x86, most ARM/aarch64) -- pext isn't available, and the code isn't portable around it
- You need a license to copy/redistribute the code -- no LICENSE file exists at the repo root
- You need verified performance numbers before adopting -- no benchmark output, hardware, or run data is published, and the project shows no CI, tests-as-assertions beyond ad hoc checks, or recent activity

**Vs siblings:** Only if your keys are literally these Chinese exchange ticker formats and you're willing to vendor unlicensed, unbenchmarked code for a niche win; for general string/integer key hashing, catalogued siblings like emhash, tsl::robin_map, or Verstable are general-purpose, actively tested, and (unlike CYBHash) carry reproducible benchmark data and clear licenses.

**Gotchas:**
- Symbol length is constrained to 5-16 characters; if length is 16 the last byte must be '0', otherwise sync_with_unordered_map() prints an error and calls std::exit(0)
- Table size is capped at 1<<MAX_BIT_SIZE (2^25) entries; sync returns false / prints 'table size too large' beyond that
- get_id() bit-packing differs per subclass (option/stock/stock6/future) and is specific to real Chinese exchange symbol formats (e.g. '.SSE'/'.SZE'/'.BSE' suffixes, 'eb2505-C-10000' style option codes) -- using it outside those formats gives undefined/garbage ids
- future_symbol_table's calculate_mask disallows id conflicts and can abort (exit(0)) if no collision-free mask is found within the search space

**Status:** Last commit 2025-03-14 with 10 stars; maintenance looks stale (no issues, PRs, releases, or CI found). Usability stays reference-only: GitHub reports license: null (no repo-root LICENSE file), even though CYB_Hash.h itself carries an inline MIT header (Copyright 2023 Chen Yibo) and the bundled StrHash.h/Str.h carry a separate inline MIT header (Copyright 2019 Meng Rao) -- the absence of a formal LICENSE file leaves redistribution rights ambiguous despite these in-file notices.

[repo](https://github.com/chenyibo1029/CYBHash) · [benchmark](https://github.com/chenyibo1029/CYBHash/blob/main/README.md)

#### number-parsing-formatting

##### fast_io  `C++`  `Anti-Tivo License (ATL) v1.0 (custom, non-OSI-approved)`  `active`  `Tier C`

Header-only C++20 I/O library replacing iostream/cstdio and std::to_chars with buffered, syscall-near I/O.

**Beats:** iostreams (std::fstream); std::to_chars (MSVC, for double formatting) — Author-run benchmarks (no CPU model or optimization flags stated) show fast_io's buffered file I/O beating std::fstream by roughly 6-15x for writing/reading 10 million integers on GCC 11 (Linux and MinGW-W64) and MSVC 19.26, and beating MSVC's std::to_chars(charconv) by about 23% (~1.29x throughput) for round-trip formatting of 10 million doubles, also on MSVC 19.26.

**How:** Devices are abstracted through C++20 concepts (static polymorphism), avoiding the vtable dispatch, locale machinery, and sentry-object overhead that <iostream>/streambuf carry on every call. I/O goes through the library's own buffered file objects close to the raw syscall/native-handle level rather than through libc FILE* layering. Integer formatting uses the jeaiii digit-pair method (include/fast_io_core_impl/integers/jeaiii_method.h, the same technique as the jeaiii/itoa sibling entry). Double round-trip formatting is implemented in include/fast_io_unit/floating/roundtrip.h, whose header comment attributes the algorithm to 'Dragonbox' (Jk Jeon) even though the readme's benchmark section calls it the 'Ryu algorithm' — these are different, related fast float-to-string algorithms.

**Use it when:**
- Bulk sequential file I/O (writing/reading millions of integers or lines) where std::fstream or stdio throughput is the bottleneck.
- Already on C++20 with a concepts-capable compiler (GCC>=14, Clang>=17, or MSVC per current support.md) and able to adopt a non-drop-in API.
- Low-level, embedded, kernel-driver, or freestanding/WASM targets that need direct handle/syscall-level I/O and small binaries (readme's static-link comparison: 155KB fast_io vs 925KB fstream).
- Need Unicode-aware (UTF-8/16/32) transcoding I/O in the same layer as raw throughput.
- Can accept the Anti-Tivo License's non-standard terms in exchange for the speed.

**Skip it when:**
- Need a true drop-in replacement for std::iostream or std::to_chars without touching call sites — fast_io's API shape and exceptions-only error model differ substantially.
- Legal review requires an OSI-approved permissive or conventional copyleft license — Anti-Tivo License v1.0 is custom and not OSI-approved.
- Toolchain can't reach the current minimum (GCC>=14/Clang>=17 per support.md), which is notably newer than the GCC 11/MSVC 19.26 used in the readme's own benchmark numbers.
- Need independently reproduced numbers before adopting — all published results are the author's own, with no CPU model or optimization flags stated, and the readme's cited benchmark paths no longer exist in the reorganized benchmark/ directory.
- Multithreaded writers by default — the fast unbuffered types are not thread-safe; the thread-safe *_mutex variants give up much of the speed edge (readme: 0.049s to 0.146s output time on MinGW for the mutex variant).

**Vs siblings:** Pick fast_io over Boost.Charconv, c4core, fast_double_parser, rigtorp/CharConv, or jeaiii/itoa when the goal is whole-file/stream I/O throughput via buffered file objects and syscall-near handles, not just isolated number<->string conversion — those siblings only replace to_chars/from_chars/stoi/strtod, while fast_io replaces the entire iostream/cstdio layer (and internally reuses jeaiii's itoa method for its own integer formatting).

**Gotchas:**
- readme's cited benchmark source paths (benchmarks/0000.10m_size_t/unit, benchmarks/0001.10m_double/charconv) do not exist in the current repo; benchmark/ has been reorganized into numbered dirs (e.g. 0002.file_io_tsc, 0004.file_io_floating).
- readme calls the double round-trip formatting the 'Ryu algorithm', but the implementation header (include/fast_io_unit/floating/roundtrip.h) is commented 'Algorithm: Dragonbox, Author: Jk Jeon' — a different, related algorithm.
- MinGW benchmark numbers required the author to patch libstdc++'s BUFSIZ from 512 bytes to 1MB before comparing against fstream; the out-of-the-box gap on stock MinGW would be smaller.
- License is the custom Anti-Tivo License v1.0 (non-OSI-approved, GitHub reports it as NOASSERTION) — review it before shipping, it is not a standard permissive or copyleft license.

**Status:** Actively maintained (last commit 2026-07-02 on the 'next' branch, 2026-03-13 on master); usability is capped at 'reference' because of the non-OSI Anti-Tivo License, not because of code immaturity — 851 stars and an extensive examples/benchmark/fuzzing tree.

[repo](https://github.com/cppfastio/fast_io) · [benchmark](https://github.com/cppfastio/fast_io/blob/master/readme.md)

#### perfect-hash-static-tables

##### strager/perfect-hash-tables  `C++`  `CC-BY-NC-ND-4.0`  `abandoned`  `Tier C`

Research generator of CRC32-hashed perfect hash tables for 80 JS/TS keywords; beats gperf ~1.2-1.4x except on keyword-only input.

**Beats:** gperf — The author's dev log (notes.txt: rounded '~' figures, no raw output) gives time per benchmark iteration, where one iteration looks up every identifier in a ~287 KB corpus built from jquery-3.5.1.js. pht icrc32 + check1memcmp took ~69 us vs ~95 us for stock gperf 3.1 on non-keywords (~1.38x) and ~152 us vs ~188 us on mixed (~1.24x; ~1.21x vs gperf with inline strings), and only tied gperf on keywords-only. Builds are -O3 -std=c++20 with g++-12 or a local clang on Linux x86-64; notes.txt names no CPU or compiler for these figures, and the Ryzen 9 5950X appears only in its perf-stat section.

**How:** Stock gperf hashes with len + asso_values[s[0]] + asso_values[s[1]] + asso_values[s[len-1]]. The winning pht variant instead packs four selected bytes (first two and last two) into one 32-bit word and hashes it with a single SSE4.2 CRC32 instruction (_mm_crc32_u32). The generator brute-forces the seed and table size until all 80 keys land in distinct slots (a perfect hash: one probe, no collision chain); the --table-size=small search settled on 262 slots. A lookup rejects lengths outside 2..11, compares the first character, memcmps the rest, and checks the length by reading the NUL at entry_keyword[size], with keywords stored inline in 13-byte entries instead of gperf's default const char* pointers. Other variants try SIMD compares (SSE2 movemask, PTEST, PCMPESTRM, NEON), cmov-based branchless result selection, and AES, Lehmer-128, xxHash3, FNV-1a and Pearson hashers.

**Use it when:**
- You write a lexer and want to know how to beat gperf on a small fixed keyword set (here 80 keys of 2-11 bytes); read generate-pht.cpp and the committed generated/ outputs as a worked design study.
- Your lookups are mostly misses (identifiers that are not keywords). The length bounds check plus the first-character check rejected them fastest: ~69 us vs ~95 us for stock gperf on the non-keyword corpus.
- You target x86-64 with SSE4.2. The winning hasher is the CRC32 instruction, and the Makefile builds the icrc32 variants only on Linux x86-64.
- You want a ready harness that compares gperf options, frozen::unordered_map, std::unordered_map, binary/linear search and Rust phf on one key set, using Google Benchmark and perf stat.

**Skip it when:**
- Anything you ship or modify. LICENSE is CC-BY-NC-ND-4.0 and README says 'EDUCATIONAL USE ONLY', so commercial use and derivatives are not allowed.
- Keyword-heavy input. On the keywords-only corpus gperf was only 'competitive' with the best pht variant, so expect no win there.
- A plain memcmp compare. Every pht hasher with --string-compare=memcmp lost to gperf on all three corpora; the gain comes from the check1memcmp compare.
- Key sets that change at runtime or come from a file. Keys are compiled in from token.h, there is no insertion, and the generator exits with 'character selection is not unique' if the chosen characters do not tell the keys apart.
- Non-x86-64 or big-endian targets for the winning config. icrc32 needs the SSE4.2 CRC32 intrinsic, and pht.h has a FIXME noting that its 2-byte memcpy character load is endian-dependent.

**Vs siblings:** Pick this repo to learn why a gperf-class keyword table is fast or slow: it ablates hasher, character selection, table size and compare strategy against gperf 3.1 options and frozen::unordered_map on one workload. For code you can ship, use triehash (also benchmarked against gperf) or frozen (a constexpr C++ container API), after you check their licenses, because this repo forbids derivatives.

**Gotchas:**
- The SIMD compare variants (sse2, ptest, cmpestri, neon-mask-test) load 16 bytes, and chunk84 loads 12 bytes, from the input pointer whatever the key length. The harness pads every buffer by 32 bytes (padding_bytes in token.h). The check1memcmp winner reads only `size` input bytes.
- --no-early-bounds-check read past the end of the table through entry_keyword[size] (issue #1). It is safe only together with --keyword-size-in-entry, which is how the Makefile pairs them.
- The 'gperf --inline-strings' baseline is not a stock gperf 3.1 option. The Makefile strips the flag and defines GPERF_INLINE, which changes token.gperf's struct to inline char arrays. mygperf is a Python post-processor of gperf's tables with the author's compare code.
- Source files carry GPL-3.0-or-later 'part of quick-lint-js' headers, while README and LICENSE say CC-BY-NC-ND-4.0, and issue #3 about licensing is still open. Treat the code as read-only reference.

**Status:** Abandoned since 2023-03-12 (not archived, 2 open issues) and licensed CC-BY-NC-ND-4.0 'EDUCATIONAL USE ONLY', so read it rather than vendor it; the author's maintained GPL-3.0 descendant of the technique is quick-lint-js's tools/generate-lex-keyword.cpp, which hashes the first two and last two characters with a multiply-shift into a power-of-two table.

[repo](https://github.com/strager/perfect-hash-tables) · [benchmark](https://github.com/strager/perfect-hash-tables/blob/master/notes.txt)

#### searching

##### simdsearch (Needle-Hammer)  `C++`  `no license`  `active`  `Tier C`

Header-only SIMD substring search with a linear-time worst-case fallback; ~30x libc memmem on Apple M-series.

**Beats:** memmem (platform libc; the headline figure is on an Apple M-series core) — The README claims about 45 GB/s substring-search throughput on an unnamed Apple M-series core, roughly 30x the platform's libc memmem, measured on ordinary text at memory speed. The repo's own benchmark/README.md notes Apple's memmem 'uses a much simpler scan and lands well behind strstr,' so the 30x figure is against a weak platform baseline, and the top-level README tells readers to reproduce numbers on their own machine rather than publishing a results table for this specific claim.

**How:** Needle-Hammer picks 2-4 selective bytes from the needle as anchors and SIMD-filters 256 haystack positions per AVX-512 iteration (64 on NEON) against them, narrowing survivors byte by byte. A per-call work counter caps how much filtering it does; once the budget is spent on adversarial input it hands off to a Crochemore-Perrin two-way search, so every call stays O(n+m) instead of degrading like an unguarded anchor filter.

**Use it when:**
- Substring/byte search over ordinary text or binary data on x86-64 with AVX-512F+BW, or any AArch64 core (NEON is architectural there)
- Throughput-bound scanning (log grepping, large-buffer search) rather than a single short lookup, since the design targets memory-speed scanning
- You can tolerate adversarial-input inputs falling back only to two-way's O(n+m), not needing sublinear worst-case behavior
- You can vendor a header-only, dependency-free library and compile per target machine (a checked-in single header and single-header releases exist)
- You need byte-exact, NUL-safe, non-UTF-8-aware search rather than a character-aware routine

**Skip it when:**
- Shipping one binary to x86-64 machines with unknown/mixed CPUs — there is no runtime dispatch; a CPU without AVX-512F+BW hits an illegal instruction
- Targeting mainstream x86-64 client parts (most Intel client chips have AVX-512 fused off, pre-Zen4 AMD lacks it) or 32-bit/RISC-V/POWER, all unsupported
- Building with MSVC — unsupported, since the headers use GCC/Clang builtins and attributes
- Needing a licensed dependency for production use — the repo ships no LICENSE file
- Wanting a published, apples-to-apples comparison against std::search or std::string::find — the benchmark driver includes both but no numbers for them are in the README

**Vs siblings:** The catalogued siblings (sb_lower_bound, scandum/binary_search, SIMD Quad search, FastBinarySearch) all accelerate binary search over sorted arrays; simdsearch instead accelerates unsorted substring/byte search, i.e. memmem/strstr territory. Pick it when the task is finding a byte pattern inside a buffer, not locating a key in an already-sorted sequence.

**Gotchas:**
- No runtime CPU dispatch: an AVX-512-compiled binary executes illegal instructions on hardware without AVX-512F+BW; the caller must detect the CPU and keep a fallback path itself
- find_unguarded skips the work-counter guard entirely (a few percent faster on ordinary text) but reverts to O(n·m) worst case; documented as safe only on input the caller controls
- Tuning constants (NH2_START_ANCHORS, NH2_BUDGET_DEN, etc.) were fitted on Emerald Rapids, Zen 5 and Apple M4 Max; the README says you shouldn't need to touch them but does not claim they are optimal on other hardware
- No LICENSE file anywhere in the repo, so there is no stated legal basis for use, modification, or redistribution

**Status:** Active: created 2026-07-28, last commit 2026-09-21, with one merged PR already fixing kernel correctness issues, but it is a brand-new, single-contributor project (9 stars, no LICENSE file), so treat it as reference material rather than something to depend on directly.

[repo](https://github.com/lemire/simdsearch) · [benchmark](https://github.com/lemire/simdsearch#readme)

#### serialization-json

##### Tachyon.JSON v6  `C++`  `Proprietary (TACHYON PROPRIETARY SOURCE LICENSE v1.0; LICENSE file allows free personal/commercial use but forbids redistribution of source, sub-licensing, and modifying the ASM/SIMD kernels)`  `active`  `Tier C`

Single-header AVX2 JSON parser under a proprietary license; benchmarks nlohmann/simdjson but times only its structural-bitmask build, not full parsing.

**Beats:** nlohmann::json (also compared against simdjson and Glaze) — README claims Tachyon's parse_view() (builds only a structural bitmask index, no value materialization) reaches 4,577 MB/s on a 25MB in-memory generated array and 5,585 MB/s on canada.json, vs simdjson's ondemand parser.iterate() at 1,886/3,541 MB/s (~2.4x/~1.6x) and nlohmann::json's full json::parse() DOM build at 25/31 MB/s (~183x/~180x), built with g++ -std=c++23 -O3 -march=native -flto (compiler version unstated) on an unspecified Intel Xeon (Haswell). The harness runs 1000 iterations for Tachyon and simdjson, 100 for Glaze, and only 10 for nlohmann, despite the README stating a uniform 'median of 1000 iterations'.

**How:** The structural scan (SIMD::compute_structural_mask) loads 128 bytes at a time into four 256-bit AVX2 registers, uses a PSHUFB (_mm256_shuffle_epi8) nibble lookup table to classify bytes as quote/backslash/structural in one pass, and derives a per-32-byte token-boundary bitmask with _mm256_movemask_epi8. String/escape state is tracked with a branchless XOR-prefix-sum over the quote bitmask rather than a byte-by-byte state machine, falling back to a scalar loop only when a chunk contains a backslash. Because parse_view() stops at building this index and never allocates or decodes individual values, the benchmarked 'parse' step skips the DOM construction that nlohmann, simdjson OnDemand, and Glaze all pay for in the same loop -- which accounts for most of the measured gap.

**Use it when:**
- Read-heavy code that only probes a few keys/values from a large document via Cursor-based lazy lookup and never needs a materialized DOM
- x86-64 deployments where AVX2 is guaranteed and build flags can be tuned per machine (e.g. -march=native)
- Studying/benchmarking a PSHUFB structural-classification + branchless quote-escape-bitmask technique, given the license blocks reusing the code itself
- Data that is only integers, strings, and booleans -- no fractional numbers anywhere in the document
- Throwaway internal tooling where a 0-star, single-maintainer, unlicensed-for-redistribution header is acceptable

**Skip it when:**
- Any JSON containing floating-point values: materialize() and the lazy number accessor both parse bare numbers as int64_t via std::from_chars, so "3.14" silently becomes 3, and dump() has no serialization case for the double variant (a json built from a double prints the literal string "null")
- Anything needing portability: the scan hard-requires AVX2 (_mm256_* intrinsics) with no scalar fallback and no runtime CPU dispatch like simdjson's -- it won't build/run on non-AVX2 x86 or ARM
- Commercial or open-source products you need to redistribute, fork, or modify -- the TACHYON PROPRIETARY SOURCE LICENSE v1.0 forbids redistribution and forbids modifying the ASM/SIMD kernels
- CBOR or MessagePack support -- from_cbor()/from_msgpack() are stubs that throw std::runtime_error
- Trusting the throughput numbers as apples-to-apples: the README times Tachyon's index-only parse_view() against nlohmann's/simdjson's/glaze's full value decode, runs nlohmann for only 10 iterations vs 1000 for Tachyon/simdjson (README claims uniform 'median of 1000') and has no CPU model, compiler version, or public CI run behind the numbers

**Vs siblings:** Rarely: the catalogued siblings (cjson.cpp, json.cpp, DAW JSON Link, utl::json) all measure the same operation on both sides of their comparison and ship under permissive licenses. Tachyon's index-only benchmark isn't measuring the same thing as a full nlohmann/simdjson parse, and its DOM path silently mangles floating-point data, so pick it only to study the AVX2 structural-bitmask/PSHUFB technique in isolation -- not for production parsing, redistribution, or any dataset with fractional numbers.

**Gotchas:**
- Materializing to DOM (or calling as_int64() on any lazy node) parses every bare number as int64_t via std::from_chars, silently truncating fractional values (3.14 -> 3); there is no reachable path that produces a double from parsed text
- json::dump() has no case for the double variant -- a json constructed from a C++ double (e.g. json(3.14)) serializes to the literal string "null"
- No scalar/fallback path for non-AVX2 hardware: compute_structural_mask and skip_whitespace assume 256-bit AVX2 registers are available at compile time
- from_cbor()/from_msgpack() exist as API stubs and always throw std::runtime_error("... not fully implemented")

**Status:** Repo history spans only 2026-01-02 to 2026-01-04 (created and last pushed within days of each other), 0 stars, and the proprietary license permits free use but forbids redistribution, forking, or modifying the SIMD kernels -- reference/study-only despite counting as 'active' under a 12-month recency rule.

[repo](https://github.com/mrcodechef/Tachyon.JSON) · [benchmark](https://github.com/mrcodechef/Tachyon.JSON)

#### small-buffer-and-strings

##### zuu_string_view  `C++`  `no license`  `active`  `Tier C`

Header-only C++11 SWAR-accelerated string_view alternative; faster find/rfind/find_first_of than std::string_view, slower on not_of scans.

**Beats:** std::string_view — README's first-party Google Benchmark table (one ~95-char haystack, compiler/flags/stdlib unstated, hardware reported only as '12x 2096 MHz CPU') shows zuu::string_view beating std::string_view on find_first_of (6.11 vs 15.7 ns, ~2.5x), find/substring (11.1 vs 14.1 ns), rfind/substring (11.4 vs 16.7 ns), find_last_of (11.0 vs 14.7 ns), and find/char (1.56 vs 2.24 ns), while std::string_view wins on find_first_not_of (5.01 vs 6.22 ns) and find_last_not_of (5.00 vs 6.82 ns).

**How:** The positive-search functions (find, rfind, find_first_of, find_last_of) use SWAR (SIMD-within-a-register): they memcpy 8 bytes at a time into a uint64_t 'tape', broadcast the needle byte(s) across all 8 lanes, XOR against the tape, and apply the classic branchless haszero/hasless byte-detection trick (0x7F7F...7F and 0x8080...80 masks) plus count_trailing_zeros/count_leading_zeros to locate the matching byte in one shot instead of a per-byte loop. Multi-char searches (find_first_of family) extend this with a 256-bit bitmap built from 4 uint64_t lookup words. This path only triggers for sizeof(CharT)==1 outside constexpr evaluation; everything else falls back to a scalar loop.

**Use it when:**
- Hot-path find/rfind/find_first_of/find_last_of/find(char) calls over ASCII/byte strings (README's own test string is ~95 chars) where a few nanoseconds per call matters
- C++11-only codebases that want string_view-style ergonomics without raising the language standard
- Header-only vendoring is acceptable: just include/zuu/string_view.hpp + include/zuu/char_class.hpp, no build step
- Single-threaded or read-only-shared usage (it's a raw pointer+length pair with no internal synchronization)
- Data provably under ~4 billion characters, since length is stored as a 32-bit unsigned int

**Skip it when:**
- find_first_not_of / find_last_not_of-heavy code: the README's own numbers show zuu 20-26% slower than std::string_view there
- Buffers that could exceed ~4B characters, or code that assumes std::string_view's std::size_t-typed npos/return values
- wchar_t/char16_t/char32_t workloads or constexpr contexts: the SWAR path is disabled there (sizeof(CharT)==1 and non-constexpr only), so performance likely reduces to the scalar fallback, which is unbenchmarked
- Projects that need a licensed dependency to ship: no LICENSE file and no license field in vcpkg.json
- Teams wanting proven maturity: repo created 2026-09-11, all 30 commits land within about a day, 0 stars, 0 issues, no third-party validation

**Vs siblings:** It's the only catalogued entry benchmarked against std::string_view itself (the other siblings target std::string/std::to_string), so pick it specifically when your bottleneck is string_view::find-family calls on a C++11 toolchain; for std::string construction/formatting/conversion speedups, use FastString, to_static_string, or Str instead.

**Gotchas:**
- size_type and npos are `unsigned int` (32-bit), not std::size_t like std::string_view — a real interop gap, not just a naming difference
- The SWAR fast path only activates when sizeof(CharT)==1 and outside constexpr evaluation; wide-char types and constexpr calls silently use the scalar loop instead
- find_first_not_of and find_last_not_of are slower than std::string_view (20-26% per the README), the opposite of the library's headline claim
- No LICENSE file and no license field in vcpkg.json, so legal usability is unresolved even though the source is public

**Status:** Actively developed as of the last commit (2026-09-12) but very early: v0.4.0, all 30 commits landed within about a day of creation (2026-09-11), 0 stars, and no LICENSE file, so treat it as unlicensed and unproven rather than production-ready.

[repo](https://github.com/zuudevs/zuu_string_view) · [benchmark](https://github.com/zuudevs/zuu_string_view)

#### smart-pointers-and-refcount

##### Delegate (bdiamand/Delegate)  `C++`  `Custom permissive notice in the delegate.h header (not an OSI-approved license; no LICENSE file)`  `abandoned`  `Tier C`

Fixed-size, heapless C++17 delegate beating std::function's invocation speed by 1.1-1.4x in a third-party benchmark.

**Beats:** std::function — On MSVC 15.9.4 (Visual Studio, 64-bit Release, Boost 1.69.0, CPU unspecified) in jamboree/CxxFunctionBenchmark's various.cpp, Delegate beat MSVC STL's std::function in all 7 invocation categories (e.g. function_pointer 0.210s vs 0.264s, ~1.26x; compile_time_function_pointer 0.132s vs 0.188s, ~1.42x), and was the fastest of 13 implementations in 5 of 7 categories (stdex::function and func::function tied or edged it out in heavy_functor and lambda_capture).

**How:** Never allocates: captured state is stored inline in a fixed-size aligned byte buffer (default 12 bytes, resizable via DELEGATE_ARGS_SIZE macro), so there is no heap round-trip on construction, copy, move, or destruction. Dispatch uses a raw function pointer plus a small static per-type vtable (copy/move/destroy) built once via templates, avoiding the extra indirection and RTTI/exception bookkeeping std::function implementations carry. No dynamic memory management and no exception-safety machinery to execute on the hot call path.

**Use it when:**
- Callback/handler slots where the callable's capture state is small and known ahead of time (fits in ~12-20 bytes, adjustable via DELEGATE_ARGS_SIZE)
- Hot paths that construct/copy/destroy callables frequently and need to avoid heap allocation and its jitter
- Embedded or latency-sensitive code that wants predictable, allocation-free memory behavior
- Code that already avoids RTTI/exceptions and does not need std::function's arbitrary-size type erasure
- Move-only captures (e.g. unique_ptr) via the MoveDelegate variant, where std::function historically disallows or complicates this

**Skip it when:**
- Captures larger than the fixed buffer size — code fails to compile (static_assert), unlike std::function's silent heap fallback
- Codebases that rely on std::function's RTTI/exception interplay or allocator-aware construction
- Projects needing an OSI-approved license: this ships a custom permissive header notice, not MIT/Apache/BSD
- Long-term maintenance risk: repo has been inactive since 2022-07-27 and only 43 stars
- Multi-threaded use without external synchronization — no thread-safety guarantees are documented or implemented

**Vs siblings:** Pick Delegate over stdext::inplace_function or SmallFunction when you want the smallest reported invocation times in this same benchmark suite for pointer/lambda-heavy call patterns; pick stdext::inplace_function instead if you need an OSI-approved (SG14/Boost-style) license, since Delegate's license is a non-standard permissive notice.

**Gotchas:**
- Default capture buffer is only sizeof(int)+sizeof(int*) (12 bytes on typical 64-bit builds), plus 8 bytes of vtable/call-pointer overhead; override via #define DELEGATE_ARGS_SIZE / DELEGATE_ARGS_ALIGN before including the header if captures don't fit
- Copying a Delegate built from a non-copyable functor calls std::terminate() at runtime rather than failing to compile (only FuncCopyable's copy path is affected; use MoveDelegate to avoid this class of captures entirely)
- No exception awareness at all — the header does not catch or propagate exceptions from the wrapped callable differently than a normal call would
- No LICENSE file; licensing is a custom notice embedded in the delegate.h comment block requiring the comment block to remain in derived works

**Status:** Abandoned since the last commit on 2022-07-27; usability is 'reference' because the custom header license is not OSI-approved, though the code is small (~350 lines) and easy to vendor or re-license by copying and adapting.

[repo](https://github.com/bdiamand/Delegate) · [benchmark](https://github.com/jamboree/CxxFunctionBenchmark#sample-result)

### toolchain-and-build

#### compile-caching-and-distribution

##### NativeLink  `Rust`  `FSL-1.1-Apache-2.0`  `active`  `Tier C`

REAPI remote build-cache and execution server for Bazel/Buck2/CMake; beats local-only, non-distributed builds.

**Beats:** local, non-distributed single-machine build (no remote cache / no distributed compilation) — Independent blog (Reid Kleckner, 2026-03-30): a full LLVM+Clang build via CMake/Ninja/recc took 1026s locally (laptop, PCH disabled, Ninja default -j) versus 257s distributed at -j96 through NativeLink on a home Kubernetes/Talos cluster (~4.0x); with PCH enabled the local build dropped to 683s, making the real distributed gain 2.65x, which the author calls the 4x headline an overstatement. No CPU models are given for the laptop or cluster nodes, and each configuration was run once (evidence tier C).

**How:** Content-addressed storage caches and reuses previously-built objects across machines and CI runs so unchanged actions are skipped entirely. A scheduler fans independent build actions from the action graph out to remote worker pods for parallel execution over the REAPI protocol (the same protocol Bazel, Buck2, and reclient use). In the verified benchmark this let a CMake/Ninja LLVM build run at -j96 across a home Kubernetes cluster instead of the client machine's default -j.

**Use it when:**
- Already building with Bazel, Buck2, Goma/Siso, or another REAPI client, where integration is closer to transparent
- CMake/Ninja C/C++ projects willing to add the recc compiler-launcher shim
- Large action graphs with many independent, cacheable steps (e.g. LLVM/Chromium-scale monorepos)
- Teams/CI where a cache and worker pool shared across many machines pays off more than single-machine speed
- You can operate a Docker/Kubernetes cluster to host the CAS, scheduler and workers

**Skip it when:**
- Solo local dev with no cluster to distribute to — the verified benchmark shows no win without remote workers
- Builds that depend on precompiled headers through recc: its input scanner doesn't recognize PCH files, so PCH had to be disabled, and re-enabling it locally cut the measured gain from ~4.0x to ~2.65x
- Teams that want a single dependency-free binary rather than standing up and operating a CAS/RE server
- Production use of the metrics/persistent-worker modules without a commercial license — those are Business Source Licensed separately from the FSL-1.1 core
- Windows Bazel builds: README claims Windows support but an open issue reports Bazel tests failing on Windows x64 (#485, unresolved since 2024)

**Vs siblings:** Pick NativeLink over FASTBuild/HOMCC/octobuild when you're already on, or willing to adopt, a Bazel Remote Execution API client (Bazel, Buck2, or CMake via recc) and want a shared cache plus a horizontally scalable Kubernetes-style execution cluster, rather than the single-protocol local caching (FASTBuild) or distcc-style compiler forwarding (HOMCC, octobuild) the siblings use.

**Gotchas:**
- recc's input scanner doesn't recognize precompiled headers as build inputs; disabling PCH was required, and doing so alone accounts for most of the gap between the claimed 4.0x and the author's corrected 2.65x
- Core is FSL-1.1 (source-available, permits only non-competing use, converts to Apache-2.0 two years after each release, not OSI-approved); the metrics and persistent-worker modules are separately Business Source Licensed, needing a commercial license for shared production use
- Open issue reports Bazel tests failing on a Windows x64 machine (#485, open since 2024)
- The only third-party speedup evidence is a single-author, single-run personal blog post; the vendor's own '4-15x' homepage claim has no published methodology

**Status:** Actively maintained (last commit 2026-09-24; 1.6k stars, 244 forks; vendor claims 10B+ build requests/month in production including Samsung); usability is 'reference' because it's infrastructure to deploy and operate, not a library to link.

[repo](https://github.com/TraceMachina/nativelink) · [benchmark](https://reidkleckner.dev/posts/llvm-recc-nativelink/)
