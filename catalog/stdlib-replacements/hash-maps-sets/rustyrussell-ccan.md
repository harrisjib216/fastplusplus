# CCAN htable (ccan/htable)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1-or-later` · 🟢 active

> Compact C open-addressing hash table of object pointers with hash bits folded into spare pointer bits; beats JudyL on random lookups.

| | |
|---|---|
| **Beats** | Judy arrays (JudyL, the Judy integer-key sparse array library) |
| **Claimed result** | htable wins random lookups and loses inserts and in-order lookups. Random hit, dense keys: Judy 361 ns, htable 330 (dense) / 357 (sparse) / 375 (dumb) ns. Random hit, sparse keys: Judy 736 ns, htable 405 / 386 / 445 ns, which is 1.65x to 1.9x faster (derived from page data). Judy wins initial insert (137 ns vs 332 / 471 / 482 ns) and linear hit (19 ns vs 174 / 176 / 214 ns on dense keys; 61 vs 215 / 202 / 265 ns on sparse keys). |
| **Workload** | 50,000,000 objects, total time divided by object count to give ns per operation: initial insert, in-order (linear) hit and random hit lookups, with dense sequential keys and then with sparse keys after delete and reinsert; htable run at 75 percent full (dense), 37 percent full (sparse) and 37 percent full with pointer bit-stealing disabled (dumb). |
| **Metric** | latency |
| **Adoption** | 1.2k stars (CCAN repo); search results show htable vendored in Samba (lib/ccan) and a 2014 htable licence-change request for Ruby |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/rustyrussell/ccan) · [benchmark](https://rusty.ozlabs.org/2010/11/08/hashtables-vs-judy-arrays-round-1.html) |

## Verdict

First-party November 2010 blog post by the author (rusty.ozlabs.org, blocked here, figures from an earlier search summary, setup confirmed by snippets): 50,000,000 unsigned int keys against JudyL, ns per operation, htable wins random hits (330 vs 361 ns dense; 386 to 445 vs 736 ns sparse) and loses inserts and in-order hits. The harnesses are ccan/htable/tools/speed.c and ccan/jmap/tools/speed.c (both -O3), but CPU, compiler and libJudy version are unpublished, and htable's tool and core have changed since (7218ee2, 3fcc6bf, e03b68c in 2022).

## Use it when

- C code that needs a lookup index over objects it already allocates (key stored inside the object), with lookups in random key order.
- Large tables (millions of entries) where per-entry memory matters: one 8-byte word per bucket on 64-bit at up to 87.5% load and no per-entry node allocation.
- Integer-key random lookups where JudyL is the incumbent: the author's 2010 run with 50,000,000 keys had htable ahead on random hits, 1.65x to 1.9x on sparse keys.
- Multisets: HTABLE_DEFINE_DUPS_TYPE keeps several objects under one key and iterates them with getfirst/getnext.
- Projects that already vendor a CCAN tree (Core Lightning ships ccan/ccan/htable).

## Skip it when

- Ordered iteration, range queries or in-order scans: in the same post Judy won in-order hits (19 vs 174 ns on dense keys) and inserts (137 vs 332 to 482 ns).
- Insert-heavy growth from empty with expensive hash functions: the full hash is not stored, so every doubling and tombstone cleanup calls the rehash callback on every element.
- Storing plain values: slots hold only non-NULL pointers other than (void \*)1, so structs need their own allocation and integers must be disguised as pointers (tools/density.c offsets them by 2 through ccan/ptrint).
- Concurrent writers: there is no internal locking, and the allocator hook set by htable_set_allocator is process-global, not per table.
- Codebases that cannot accept LGPL-2.1-or-later for static linking (htable is LGPL even though its dependencies ccan/str, ccan/compiler and ccan/hash are CC0).

## How it is fast

Open addressing with linear probing over a flat array of one machine word per bucket. Bits common to every stored pointer are masked out and replaced with extra hash bits (pointer bit stealing), so most non-matching probes are rejected without dereferencing the object, and a 'perfect' bit marks entries sitting in their home bucket. The table fills to 87.5% (7/8) before doubling, deletions leave tombstones (skipped when the next bucket is empty) and an in-place rehash runs when tombstones pass 12.5%. Random lookups cost one probe run in a flat array, whereas Judy's strength is key locality (the harness itself notes in-order lookups are cache-friendly for Judy).

## Compared with alternatives

Most catalogued siblings are C++ (abseil, Boost.Unordered, ankerl, folly F14) and store keys and values inline; Verstable is the other C option, MIT-licensed and single-header with inline storage. Pick htable when your objects already live elsewhere and you want a one-word-per-slot pointer index or the DUPS multiset variant and LGPL is acceptable; otherwise Verstable's licence and inline storage are simpler.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | ccan/compiler and ccan/str (which pulls ccan/build_assert), plus a CCAN config.h; ccan/hash (CC0, Bob Jenkins lookup3) is optional for hash functions; libc calloc/free unless htable_set_allocator is called |
| **Minimum toolchain** | C99 (stdint.h, stdbool.h, inline); typed wrappers with non-pointer keys need typeof (HAVE_TYPEOF, GCC or Clang), otherwise HTABLE_KTYPE assumes pointer keys |
| **Platforms** | any platform with uintptr_t-convertible pointers; a 32-bit allocation-size wrap on doubling was fixed in August 2026 (commit d3da452) |
| **Thread safety** | Not documented; no internal locking. Lookups take const pointers, but any add or delete needs external synchronization. htable_lock() is a nesting counter that asserts against adds during iteration, not a mutex. |
| **Drop-in for the baseline** | no |

## Gotchas

- Safety checks are asserts only: storing NULL or (void \*)1, adding a duplicate through a NODUPS type, or adding to a locked table are caught only in debug builds; with NDEBUG they corrupt silently. The hash passed to htable_add/htable_del must equal what the rehash callback returns, or the entry becomes unfindable after a resize.
- Docs disagree on iteration: htable.h says iteration is not safe across htable_add (the table may resize), while htable_type.h says iterating a changing table is safe but may miss elements; use &lt;name&gt;_lock() (added March 2026) to enforce no adds.
- Bit stealing had a correctness bug fixed in June 2022: when a pointer's unshared bits and the hash bits encoded to 0 (empty) or 1 (deleted), entries could vanish. An interim fix (7218ee2) slowed matched lookups from 54.8 to 83.3 ns in its own commit message before e03b68c moved the fix to a cold path. The 2010 Judy numbers predate this fix and the 75% to 87.5% density change (3fcc6bf, about 3% slower overall per its commit).
- Harness flaws behind the numbers: the Judy side does exist in the repo (ccan/jmap/tools/speed.c, -O3 -lJudy, same rows), so the run is repeatable, but 'random' lookups are a fixed stride of 10007 modulo the count; both speed.c files divide the delete-half and add-half loops (count/2 operations) by the full count, understating those rows 2x; the jmap half-random row reads objs[j+1] and dereferences NULL when the stride reaches the last object (at 10,000,000 keys, not at 1,000,000 or 50,000,000); and htable/tools/hsearchspeed.c's 'random' row looks up words[i] in order (j is computed but unused) with hsearch presized by hcreate, while stringspeed.c grows htable from empty.

## Known shortcomings

- Tier C: evidence is a 2010 first-party blog post with no CPU, compiler or flags; the Judy comparison harness is not in the repo and the ns figures could not be re-read (rusty.ozlabs.org blocked). Snippets confirm only the setup (50M objects, 75%/37%/37% occupancy, no bit-stealing). htable wins random lookups only and loses insert and in-order traversal to Judy. The repo's own hsearchspeed.c vs stringspeed.c harness (-O3, glibc hsearch) has no published results. Licence LGPL-2.1-or-later for ccan/htable.
- Enricher correction: the Judy harness is in the repo (ccan/jmap/tools/speed.c, -O3 -lJudy, same rows as ccan/htable/tools/speed.c), so the run is repeatable; CPU, compiler and libJudy version still unknown. Harness flaws: 'random' lookups are a fixed 10007 stride mod count; both speed.c files divide the delete-half/add-half loops (count/2 ops) by the full count, so those rows read 2x low; the jmap half-random row reads objs[num] and NULL-derefs at 10,000,000 keys; hsearchspeed.c's 'random' row looks up words[i] in order and hcreate presizes while stringspeed grows the htable from empty. Code changed since the 2010 numbers: June 2022 bit-stealing fix (entries could vanish; 7218ee2 interim fix cost 54.8 to 83.3 ns, e03b68c cold path) and density raised from 75% to 87.5% (3fcc6bf, about 3% slower). Asserts-only checks (NULL, (void \*)1, NODUPS duplicates, locked add) vanish under NDEBUG; htable_set_allocator is process-global; iteration docs contradict; no ordered iteration; the rehash callback runs on every element at each resize. Core Lightning vendors ccan/htable; Samba's lib/ccan is gone on master, so the Samba usage claim is stale.

## Caveats and trade-offs

Snippet only: rusty.ozlabs.org was EGRESS_BLOCKED for both the search agent and the verifier, so the post was never opened; web-search snippets confirm the post exists and its setup (JudyL vs htable at 75 percent full, 37 percent full and 37 percent full with bit-stealing disabled, 50,000,000 objects, total time divided by object count), but the specific ns figures in claimed_speedup come from an earlier search summary and were not seen by the verifier. Machine, CPU, compiler and flags of the post are unknown. First-party author blog post from November 2010, on code changed many times since (htable commits through 2026). The repo's ccan/htable/tools/speed.c times htable alone (its only Judy reference is a comment that in-order lookups are cache-friendly for Judy), so the Judy comparison is not reproducible from the repo. ccan/htable/tools/hsearchspeed.c does time glibc hsearch(3) on the same /usr/share/dict/words string workload as stringspeed.c (Makefile: -Wall -Werror -O3), so an htable vs libc hsearch comparison can be run from the repo, but no result numbers are published anywhere in the repo. Judy is a strong incumbent but not a standard-library facility, and the win is only on random-access lookups, not on inserts or sequential (in-order) access. No other numeric comparison found for any CCAN module. [retier] Judy comparison harness is in the repo (ccan/jmap/tools/speed.c, -O3 -lJudy). 2010 numbers predate the June 2022 bit-stealing correctness fix (interim fix cost 54.8 to 83.3 ns) and the 75% to 87.5% density change (about 3% slower). Harness: 'random' lookups use a fixed 10007 stride; delete-half/add-half rows divide count/2 ops by the full count (2x low); jmap half-random row NULL-derefs at 10M keys. Wins random lookups only; loses insert and in-order traversal to Judy. Samba usage claim stale (Core Lightning still vendors it). LGPL-2.1-or-later.

Unordered hash table of pointers with user-supplied hash and equality callbacks (htable_type.h adds typed wrappers) and a pointer bit-stealing mode that saves memory; no ordered iteration, unlike Judy, which is sorted and wins on dense in-order access. LGPL-2.1+ licence, C only.

## Maintenance

Active (htable commits through August 2026, repo through 2026-09-14) and vendored by Core Lightning (Samba's lib/ccan is gone from master), copyable as a small LGPL-2.1-or-later source drop; the Judy comparison is a 2010 first-party run on code since changed (density 75% to 87.5%, June 2022 vanishing-entry fixes) with a paired harness that divides half-size loops by the full count and calls a fixed 10007 stride 'random'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party author blog post (Rusty Russell, November 2010) comparing JudyL against htable at three densities; the post is EGRESS_BLOCKED here and search snippets confirm only the setup (50,000,000 objects, ns per operation, 75 percent dense, 37 percent sparse, 37 percent with bit-stealing disabled), not the numbers. No CPU, compiler or flags are known for the post and the repo carries no Judy harness, so it cannot reach A or B.
- **Verifier notes:** Real, notable module (CCAN 1.2k stars, htable vendored in Samba); tier C stands, but the quoted ns numbers are unverified (benchmark post blocked, snippets confirm setup only). Shortcomings: first-party 2010 blog numbers with no hardware/compiler/flags, Judy comparison not reproducible from the repo, htable wins only random lookups and loses inserts and in-order lookups to Judy; repo ships an hsearch(3) harness (hsearchspeed.c vs stringspeed.c) but no published results. License LGPL-2.1-or-later confirmed from ccan/htable/_info; last commit 2026-09-14 confirmed.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-51 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/rustyrussell/ccan>
  - <https://github.com/rustyrussell/ccan/commits>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/_info>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/LICENSE>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/tools/speed.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/tools/stringspeed.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/tools/hsearchspeed.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/tools/Makefile>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/_info>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/LICENSE>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/htable.h>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/htable.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/htable_type.h>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/tools/speed.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/tools/stringspeed.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/tools/hsearchspeed.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/tools/Makefile>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/tools/density.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/htable/test/run-clash.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/jmap/tools/speed.c>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/jmap/tools/Makefile>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/jmap/_info>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/jmap/jmap.h>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/str/_info>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/compiler/_info>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/ccan/hash/_info>
  - <https://raw.githubusercontent.com/rustyrussell/ccan/HEAD/README>
  - <https://github.com/rustyrussell/ccan>
  - <https://github.com/rustyrussell/ccan/commits/master/ccan/htable>
  - <https://github.com/rustyrussell/ccan/commit/7218ee2476d8a7e4f9413781e2bedcd2daaa8190>
  - <https://github.com/rustyrussell/ccan/commit/e03b68c761b870fd9e4c165bfe2358f5df82e49c>
  - <https://github.com/rustyrussell/ccan/commit/3fcc6bfb0447e07a69c4912951021a4104a6f726>
  - <https://github.com/rustyrussell/ccan/issues?q=htable>
  - <https://raw.githubusercontent.com/ElementsProject/lightning/HEAD/ccan/ccan/htable/htable.c>
  - <https://raw.githubusercontent.com/samba-team/samba/HEAD/lib/ccan/htable/htable.c>
  - <https://github.com/samba-team/samba/tree/master/lib/ccan>
  - <https://github.com/JacksonAllan/Verstable>
  - https://rusty.ozlabs.org/2010/11/08/hashtables-vs-judy-arrays-round-1.html (EGRESS_BLOCKED; WebSearch snippet only)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/rustyrussell/ccan`) · [data/wave1/enrich/raw/github_com_rustyrussell_ccan.json](../../../data/wave1/enrich/raw/github_com_rustyrussell_ccan.json) (enrichment confidence 0.72)

</details>
