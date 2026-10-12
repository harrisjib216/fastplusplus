# LHD (Least Hit Density) / RankCache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT (verbatim MIT text, Copyright 2017-2018 Carnegie Mellon University, plus a non-binding request to cite the LHD paper; GitHub reports NOASSERTION)` · 🔴 abandoned

> Trace-driven simulator for LHD, a size-aware eviction policy needing \~8x less cache than LRU for equal hit rate.

| | |
|---|---|
| **Beats** | LRU |
| **Claimed result** | LHD needs on average 8x less cache space than LRU (and 2-3x less than other proposed policies) to match the same hit rate; RankCache needs no synchronization in the common case, improving request throughput at 16 threads by 8x over LRU and 2x over CLOCK |
| **Workload** | Commercial Memcachier and enterprise storage (MSR) traces simulated for hit-rate/space comparisons; RankCache, an LHD-based memcached-derived KV-cache, benchmarked for request throughput at up to 16 threads |
| **Metric** | throughput |
| **Hardware** | Not stated in the extracted paper text for the RankCache throughput experiment |
| **Adoption** | 25 stars |
| **Last commit** | 2018-07-23 |
| **Links** | [repository](https://github.com/CMU-CORGI/LHD) · [benchmark](https://www.usenix.org/system/files/conference/nsdi18/nsdi18-beckmann.pdf) |

## Verdict

There are two separate results. First, an idealized simulation on a weeklong Memcachier trace and MSR block traces (512M requests after a 128M warm-up): on average LHD+ needed 8x less space than LRU to match hit rate, and 2.4x/2.5x/2.9x less than GDSF/Hyperbolic/AdaptSize. Second, RankCache, a modified memcached v1.4.33 that is not in this repo, was run on one server with the network bypassed, same-size objects and a synthetic Zipfian trace: at 16 threads it gave 8x (abstract) or 16x (intro) the throughput of list-based LRU, and 2x CLOCK at a 90% hit ratio. The paper gives no CPU, compiler or flags for these runs.

## Use it when

- Deciding whether a size-aware policy would beat LRU on your own key-value traces, where object sizes vary from a few bytes to \~1 MB (the Memcachier trace had a 100 B median), before building anything.
- Building your own sampled-eviction cache (Redis-style random sampling) and wanting a reference implementation of a principled ranking function to port; the core is about the first 200 lines of lhd.cpp.
- Workloads that mix scans with Zipf-like reuse, or that show LRU performance cliffs: the paper shows LHD avoiding the cliffs that LRU, GDSF and Hyperbolic hit on MSR src1_0 at 96 MB and proj_2 at 128 MB.
- Memory-bound cache tiers where hits per GB matter more than CPU per request: averaged across cache sizes, LHD+ had 45% fewer misses than LRU and 23-27% fewer than AdaptSize, GDSF and Hyperbolic.
- Multi-tenant caches where each request carries an app or tenant id, since LHD+ also classifies objects by app id (hashed into 16 classes).

## Skip it when

- You need a working cache or a faster memcached now: this is a single-threaded simulator. The RankCache server behind the 8x/16x throughput numbers (built on memcached v1.4.33) is not published here.
- Short traces or loop/scan-heavy traces. In open issue #1, Caffeine's author reports that the fixed 2^20-access reconfiguration interval gave 4% hit rate on a LIRS loop trace at cache size 512. Reconfiguring every 1,024 accesses raised that to 49.7%, but runtime rose from 2 s to 26 s. On his unit-size ARC and LIRS traces, LHD never had the best hit rate and was about on par with ARC at higher runtime cost.
- Anything that needs TTL/expiry, deletes or concurrent access: the simulator has none of them. libCacheSim's port of this code aborts on short TTL configurations ('LHD does not support expiration').
- Tight metadata budgets: the simulator allocates about 61 MB of fixed tables before any object is cached (256 classes x 20,000 ages x 3 float arrays), plus a 56-byte Tag struct (by field layout) and a std::unordered_map entry per object. RankCache reports 6.4 MB of rank tables plus 12.6 MB of counters per thread.
- You need comparisons against strong modern baselines. The paper compares against list-based LRU, GDSF, Hyperbolic, AdaptSize and CLOCK, not ARC or TinyLFU. An HN commenter noted it also misses memcached's modified-2Q LRU, which was the default from 1.5.0.

## How it is fast

Hit density = hit probability / (object size x expected time in cache). It is estimated from online histograms of hit ages and eviction ages. There is one histogram per class, 16 last-hit-age classes x 16 app-id classes. The histograms are EWMA-decayed and turned into a rank table indexed by coarsened age, in one linear pass every 2^20 accesses. To evict, it samples ASSOCIATIVITY random objects plus the last 8 low-ranked admissions and evicts the lowest, so there is no global ordered list and eviction cost is constant. ASSOCIATIVITY is 32 in lhd.hpp; example.cfg and RankCache use 64. The throughput gain belongs to RankCache: because eviction is by sampling, a hit only writes a per-object timestamp. Evictions use memcached's version-check optimistic concurrency instead of the serialized list operations of LRU or the serialized evictions of CLOCK, and a compact separate tag array makes 64 samples cost about 4 cache misses.

## Compared with alternatives

Pick LHD only as a research reference, to test hit-density eviction on your own traces or to port its ranking into your own sampled cache. For something deployable, use Pelikan/Segcache (memcached replacement, about 8x Memcached's throughput at 24 threads) or Caffeine (JVM); for a simple, scalable replacement for LRU, use SIEVE. libCacheSim (the SIEVE entry) already includes this LHD code behind its common C API next to many other policies, and is the easier way to run it.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | libconfig++ (linked with -lconfig++ and used for config parsing); otherwise the STL only. lhd.cpp depends on the simulator's own cache::Cache and parser::Request types. |
| **Minimum toolchain** | C++14 (the Makefile runs g++ -std=c++14 -O3 -march=native -ffast-math -funroll-loops -mcmodel=medium -Wall -Werror). Supported compiler versions are not documented. |
| **Platforms** | Linux x86-64 as shipped: parser.hpp uses stat64 and ioctl, and the Makefile hard-codes -march=native and -mcmodel=medium. Other platforms are not documented. |
| **Thread safety** | Not thread-safe. The simulator is single-threaded, and std::vector/std::unordered_map state is shared with no locks. The lock-free sampling design exists only in the unreleased RankCache. |
| **Drop-in for the baseline** | no |

## Gotchas

- example.cfg sets repl.appClasses, ageCoarseningErrorTolerance, accsPerInterval and ewmaDecay, but the code never reads them. The real values are constexpr constants in lhd.hpp (16, 0.01, 2^20, 0.9). Only repl.type, cache.assoc, cache.admissionSamples, cache.capacity (in MB) and the trace.\* keys are read.
- Trace paths are hard-coded in cache.cpp (/n/memcachier/snia/msr/&lt;file&gt;.trace and others), so running your own trace means editing cache.cpp or matching one of the binary header formats in parser.hpp. The full-format reader loops back to the start of the file at EOF, objects over 1 MB are trimmed, and 74 B of memcached overhead is added to every object size.
- rank() samples only 8 candidates until 50 reconfigurations (about 52M accesses) have passed, and explorer objects are admitted only during that window. The code comment calls this a warm-up hack that 'doesn't belong in a real system'. Age coarsening is re-tuned only at reconfigurations 5 and 25.
- reconfigure() prints stats to stdout every 2^20 accesses, errors are handled with assert(), and std::hash&lt;candidate_t&gt; hashes only the object id and ignores appId.

## Known shortcomings

- The repo is a single-threaded simulator only; RankCache (the memcached 1.4.33 fork behind the 8x/16x throughput claim) was never released, so the throughput claim cannot be reproduced. Throughput runs used synthetic Zipf, same-size objects and bypassed the network; no CPU/compiler/flags; abstract says 8x vs LRU, intro says 16x.
- Fixed 2^20-access reconfiguration gives 4% vs 49.7% hit rate on the LIRS loop trace (issue #1, unanswered). example.cfg keys appClasses/ewmaDecay/accsPerInterval are never read (constexpr); trace paths hard-coded. Linux x86-64 only, -Werror, needs libconfig++, \~61 MB fixed tables, no TTL. Baselines weak (no ARC/TinyLFU/segmented LRU); libCacheSim vendors this code and is the easier way to run it.

## Caveats and trade-offs

The 8x/2x throughput numbers are for RankCache, a separate prototype built on memcached 1.4.33 that is not in this repo. Its own README calls the CMU-CORGI/LHD repo 'simulation code' only, so the throughput claim cannot be reproduced from it. The throughput test ran inside one server with the network bypassed, on a random Zipfian trace with same-size objects. The paper's intro gives a different figure (16x over list-based LRU; 2x over CLOCK at a 90% hit ratio) than the abstract's 8x. The 8x space saving is an average across the Memcachier and MSR traces. MIT license: no patent grant.

LHD's ranking function relies on modeling conditional-probability hit density which needs periodic reclassification/recomputation; the GitHub repo ships only the trace-driven simulator, not the RankCache memcached-based prototype used for the throughput numbers

## Maintenance

Abandoned: one 'Initial LHD release' commit on 2018-07-23 and one open 2019 issue with no reply. It is MIT-licensed (with a request to cite the paper) and about 40 KB of source, so easy to vendor, but it is simulation code, not a cache library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed NSDI'18 paper's abstract states LHD needs on average 8x less space than LRU and 2-3x less than recent policies, and that RankCache at 16 threads improves throughput 8x over LRU and 2x over CLOCK. The repo has only the simulator, and the paper gives no CPU model, compiler or flags, so it is not A.
- **Verifier notes:** The claim is quoted almost verbatim from the abstract. The metadata (25 stars, last commit 2018-07-23, abandoned, not a fork) checks out. The LICENSE file is standard MIT plus a citation request, so 'copyable' stands.
- **Fields the verifier corrected:** `license`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/conference/nsdi18/nsdi18-beckmann.pdf>
  - <https://github.com/CMU-CORGI/LHD>
- **Sources the enricher read:**
  - <https://github.com/CMU-CORGI/LHD>
  - <https://github.com/CMU-CORGI/LHD/blob/master/README>
  - <https://github.com/CMU-CORGI/LHD/blob/master/lhd.hpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/lhd.cpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/repl.hpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/repl.cpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/cache.hpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/cache.cpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/parser.hpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/lru.hpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/candidate.hpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/config.hpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/rand.hpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/constants.hpp>
  - <https://github.com/CMU-CORGI/LHD/blob/master/Makefile>
  - <https://github.com/CMU-CORGI/LHD/blob/master/example.cfg>
  - <https://github.com/CMU-CORGI/LHD/blob/master/LICENSE>
  - <https://github.com/CMU-CORGI/LHD/issues/1>
  - <https://github.com/CMU-CORGI/LHD/commits/master>
  - <https://github.com/CMU-CORGI/LHD/forks>
  - <https://www.usenix.org/system/files/conference/nsdi18/nsdi18-beckmann.pdf>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/LHD/LHD_Interface.cpp>
  - <https://github.com/1a1a11a/libCacheSim/blob/develop/libCacheSim/cache/eviction/LHD/lhd.cpp>
  - <https://hn.algolia.com/api/v1/items/16825931>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cmu-corgi/lhd`) · [data/wave6/enrich/raw/github_com_cmu_corgi_lhd.json](../../../data/wave6/enrich/raw/github_com_cmu_corgi_lhd.json) (enrichment confidence 0.8)

</details>
