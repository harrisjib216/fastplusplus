# libart (Adaptive Radix Tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> C99 Adaptive Radix Tree: ordered byte-key map/set, algorithmically faster than red-black trees (std::map's structure).

| | |
|---|---|
| **Beats** | red-black tree (the ART paper's own in-memory red-black-tree implementation, algorithmically what std::map/std::set are built on, but not literally libstdc++/libc++/MSVC's std::map) |
| **Claimed result** | From the ART paper's Fig. 10 (single-threaded lookups of random existing 32-bit keys; derived from page data: read off bar chart, approximate; measures the paper authors' ART, not libart): 65K keys: ART \~108M lookups/s dense, \~35M/s sparse vs red-black tree \~7.5M/s (\~14x dense, \~4.7x sparse); 16M keys: ART \~20M/s dense, \~10.7M/s sparse vs RB \~1.2M/s (\~17x / \~9x); 256M keys: ART \~10.1M/s dense, \~6.8M/s sparse vs RB \~0.65M/s (\~15x / \~10x). The paper's chained hash table beats ART on sparse keys at every size; in Fig. 11 (16M keys, 12 threads, 8-way software pipelining) ART dense \~195M/s vs hash table \~132M/s, but ART sparse \~110M/s is slower than the hash table. The paper's 1.6-1.7x (ART) and 1.2x (HT) figures are speedups from software pipelining, not ART-vs-HT ratios. |
| **Workload** | single-threaded lookups of existing random 32-bit-integer keys in an index of 65K, 16M, and 256M keys, both dense and sparse key distributions (also a 12-thread/8-way-software-pipelined variant at 16M keys), from the ART paper's micro-benchmarks |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 3930K, 6 cores/12 threads, 3.2GHz (3.8GHz turbo), 12MB shared L3 cache, 32GB quad-channel DDR3-1600 RAM, Linux 3.2 x86-64 |
| **Compiler and flags** | GCC 4.6 (optimization flags not stated in the text) |
| **Adoption** | 836 stars; the ART algorithm (the paper's implementation, not libart) was integrated into the HyPer main-memory database per the paper |
| **Last commit** | 2021-02-11 |
| **Links** | [repository](https://github.com/armon/libart) · [benchmark](https://db.in.tum.de/~leis/papers/ART.pdf) |

## Verdict

The claimed speedups (up to \~14-17x on dense keys, \~5-10x on sparse keys at 65K-256M random 32-bit keys) are entirely from the ART paper (Leis et al., ICDE 2013), which benchmarked the paper authors' own unreleased ART and red-black-tree implementations, compiled with GCC 4.6 on an Intel Core i7-3930K (6C/12T, 3.2GHz, 12MB shared L3, 32GB DDR3-1600, Linux 3.2 x86-64) — not libart, and not any std::map implementation. libart itself has no benchmark suite.

## Use it when

- Ordered map/set semantics (min/max, ordered iteration, prefix iteration) over keys you can encode as binary-comparable byte strings
- Read-heavy, single-threaded in-process indexes (e.g. routing tables, in-memory dictionaries) where you own the key encoding
- Key sets where no key is a byte-for-byte prefix of another key, or you pre-length-prefix/terminate keys to avoid that case
- x86/x86-64 targets, where the SSE2 Node16 fast path applies (other archs still work via scalar fallback, just without that speedup)
- You're willing to vendor and maintain the \~2-file source yourself since the project is unmaintained

## Skip it when

- Any key can be a strict byte-for-byte prefix of another key: issue #56 (open) documents out-of-bounds reads / incorrect leaf-splitting in recursive_insert for exactly this case, with no released fix
- Multi-threaded concurrent access: no locks, atomics, or volatile-qualified state in the source; maintainer-adjacent discussion in issue #53 confirms it is not thread-safe and points to forks (e.g. ARTSynchronized) for concurrent variants
- You need a drop-in std::map/std::set replacement: this is an untemplated C library with a byte-key/void\*-value function API, not a C++ generic container
- You need it actively maintained: last commit 2021-02-11, with confirmed bugs (#54 search returns null for prefix+NUL keys, #42 key_len issues, #35 crash in recursive_insert, #17 valgrind warning on prefix keys) still open
- You need project-specific speed evidence: libart ships no benchmarks of its own (repo has only src/ and tests/); every claimed number comes from the ART paper's own unreleased implementations, not this codebase

## How it is fast

ART uses four node types (4/16/48/256 children) sized to actual local fanout instead of one fixed node shape, so small nodes stay cache-small and dense nodes get direct/O(1) child lookup. Path compression (inline partial keys up to MAX_PREFIX_LEN=10 bytes) and lazy expansion collapse single-child chains, bounding worst-case overhead to about 52 bytes/key. On x86/x86-64, Node16's 16-way key comparison is vectorized with SSE2 (_mm_cmpeq_epi8 + movemask + ctz) instead of a scalar loop; other architectures fall back to a plain scan.

## Compared with alternatives

Pick libart only when you specifically need ordered + prefix iteration over binary-comparable byte-string keys and are willing to vendor and patch an abandoned C library. Every other sibling in this category (cpp-btree, tlx, frozenca/BTree, fast-containers, RadixMap, S+ tree, boost::container flat_set) has actual project-measured benchmarks against std::map; libart has none of its own, so prefer those when maintained, verifiable numbers matter more than ART's specific prefix/min/max feature set.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libcheck is only needed to build the test_runner test suite, not the library) |
| **Minimum toolchain** | C99; comments in art.c work around GCC 4.2.2's broken C99 inline support and a GCC 5.1 loop-unrolling bug, but no explicit minimum compiler version is stated |
| **Platforms** | any (portable C99); SSE2 fast path compiled only under __i386__/__amd64__ for Node16 child lookup, scalar fallback loop used elsewhere |
| **Thread safety** | not thread-safe / not documented as safe — no mutexes, atomics, or volatile-qualified fields in the source; see issue #53 |
| **Drop-in for the baseline** | partial — explain: same broad job as std::map/std::set (ordered key-value lookup) but a different C API (byte-buffer keys, void\* values, callback-based iteration), no templates or RAII |

## Gotchas

- Keys that are a byte-for-byte prefix of another inserted key can cause out-of-bounds reads and incorrect behavior in recursive_insert (issue #56, open; related #12, #17, #54)
- Path-compressed prefixes longer than MAX_PREFIX_LEN=10 bytes are only partially stored inline; matching a longer shared prefix requires re-reading a leaf key, a deliberate space/time tradeoff from the ART paper
- Keys must already be binary-comparable byte strings; signed integers, floats, and multi-field keys need an explicit transform before insertion, the library does none of this for you
- Leaf pointers are tagged in their low bit to distinguish them from internal nodes, so values/allocations the caller stores must not rely on odd pointer addresses

## Caveats and trade-offs

libart has no benchmarks of its own (repo has only src/ and tests/); all numbers come from the ART paper (ICDE 2013), which measured the authors' own ART and own red-black tree ('two textbook data structures'), not libart and not libstdc++/libc++/MSVC std::map; values are read off bar charts; the paper removed path compression for the 32-bit-key micro-benchmarks; the paper's hash table beats ART on sparse keys; libart last commit 2021-02-11 (abandoned).

keys are limited to fixed-width binary-comparable encodings (signed integers, floats, and strings all need a transform to sort correctly bitwise); path compression and lazy expansion are required to bound worst-case space to \~52 bytes/key; libart (this repo) is an independent open-source C99 implementation of the paper's algorithm, not the authors' original benchmark artifact

## Maintenance

Abandoned since its last commit on 2021-02-11; several confirmed bugs, including an unresolved out-of-bounds read for prefix-key inserts (#56), remain open years later. BSD-3-Clause and small enough (two files, src/art.c + src/art.h) to vendor and patch yourself if you accept that risk.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The ART paper (peer-reviewed) benchmarks the authors' own unreleased ART against their own red-black tree, not libart and not std::map; libart ships no benchmarks at all, so the only numbers are indirect algorithm-level evidence and cannot carry B for this repo (D is arguable if project-specific numbers are required).
- **Verifier notes:** Record misread Fig. 10 (the red-black tree is \~7.5M/s at 65K, not 10-15M/s, so the real ratio is larger) and misattributed the 1.2-1.7x software-pipelining speedups as an ART-vs-hash-table win (ART sparse is slower than HT). Downgraded because the evidence is for the algorithm, not this implementation; license verified BSD-3-Clause from LICENSE (GitHub reports NOASSERTION).
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://db.in.tum.de/~leis/papers/ART.pdf>
  - <https://github.com/armon/libart>
  - <https://github.com/armon/libart/blob/master/LICENSE>
  - <https://github.com/armon/libart/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/armon/libart>
  - <https://github.com/armon/libart/blob/master/README.md>
  - <https://github.com/armon/libart/blob/master/LICENSE>
  - <https://github.com/armon/libart/blob/master/src/art.h>
  - <https://github.com/armon/libart/blob/master/src/art.c>
  - <https://github.com/armon/libart/issues/53>
  - <https://github.com/armon/libart/issues/56>
  - <https://github.com/armon/libart/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/armon/libart`) · [data/wave1/enrich/raw/github_com_armon_libart.json](../../../data/wave1/enrich/raw/github_com_armon_libart.json) (enrichment confidence 0.45)

</details>
