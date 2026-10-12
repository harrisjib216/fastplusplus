# exor_filter (Erlang NIF, Xor Filter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Erlang` · `Apache-2.0` · 🔴 abandoned

> Erlang/Elixir C NIF for static xor8/xor16 filters; 2.6-10x faster lookups than BEAM Bloom libraries in the author's benchmark.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | Benchee, 10,000 lookups per iteration: xor8 8 1M 1.55 ms avg (645.20 ips) vs Bloomex 1M 8.87 ms, Blex 1M 13.17 ms, erbloom 1M 4.01 ms (5.7x / 8.5x / 2.6x, derived from page data). xor16 10M 1.77 ms avg (565.42 ips) vs Bloomex 10M 15.24 ms, Blex 10M 18.47 ms, erbloom 10M 3.90 ms (8.6x / 10.4x / 2.2x, derived from page data). The page's own 'Comparison' column is relative to the fastest row (fuse8 100), not to exor_filter. |
| **Workload** | mpope9/exor_bechmark Benchee shootout (lib/exor_benchmark.exs; exor_filter pinned to v0.5.2): filters of 100/1k/100k/1M/10M elements, 10,000 lookups per iteration, 2 s warmup and 5 s time, comparing exor_filter xor8/xor16 (and efuse_filter fuse8) against Bloomex, Blex and erbloom. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-7267U CPU @ 3.10GHz, 4 cores, 8GB RAM, macOS (per repo's own Benchee output) |
| **Compiler and flags** | Elixir 1.12.2, Erlang/OTP 24.0.5. exor_filter is a C NIF (c_src/xor_filter_nif.c wrapping FastFilter xor_singleheader), not Rust; its c_src Makefile defaults to CFLAGS ?= -O3 -std=c99 -finline-functions. The C compiler and version are not stated. erbloom is a Rust NIF. |
| **Adoption** | 35 stars; hex.pm exor_filter 1,087 all-time downloads (latest 0.8.2) |
| **Last commit** | 2021-12-02 |
| **Links** | [repository](https://github.com/mpope9/exor_filter) · [benchmark](https://github.com/mpope9/exor_bechmark#benchee-output) |

## Verdict

In the author's own Benchee run (exor_filter pinned to v0.5.2, a C NIF built with -O3 -std=c99 by an unnamed compiler, on Elixir 1.12.2 and OTP 24.0.5, on an Intel i5-7267U macOS laptop), 10,000 lookups per iteration took 1.55 ms for xor8 on a 1M-key filter, against 8.87 ms for Bloomex, 13.17 ms for Blex and 4.01 ms for the erbloom Rust NIF (about 5.7x, 8.5x and 2.6x), and 1.77 ms for xor16 at 10M against 15.24 ms (Bloomex) and 18.47 ms (Blex). The Bloom filters were configured at 10% or 1% FPR, the queried keys 1..10,000 are all members of the large filters, and the script builds its 'erbloom 10M' filter from only 10k keys, so the 2.2x erbloom-at-10M ratio is not like-for-like.

## Use it when

- An Erlang or Elixir service needs a read-mostly membership pre-check over a set that is built once, such as a blocklist, a seen-ID set, or a guard in front of a slow store or cache, and many processes query it.
- Lookup latency matters more than build time. The author's run shows about 1.5-1.8 ms per 10,000 lookups on 1M-10M-key filters, against 4-18 ms for Bloomex, Blex and erbloom.
- You want less memory per unit of accuracy than a Bloom filter: xor8 uses about 9.8 bits/key at a 2^-8 (\~0.4%) FPR, and xor16 about 19.7 bits/key at a 2^-16 (\~0.0015%) FPR.
- The set has up to about 20K keys with the default hash, or you can supply your own collision-free 64-bit hash (or pre-hashed uint64 keys) for larger sets.
- You need to ship a filter to another node or system. to_bin produces a flat binary that contain/2 can query directly without deserializing.

## Skip it when

- The set changes after construction. There is no add or delete on a finalized filter, so every change means rebuilding from the full key list. Blex and Bloomex support incremental puts.
- Large sets with the default hash. erlang:phash2/1 returns only 27 bits (0..2^27-1 per the Erlang docs), so every non-member that collides with a member is a false positive. By our arithmetic that adds about 0.7% FPR at 1M keys and about 7% at 10M, which swamps xor8's 0.4%.
- You need the best filter available on the BEAM today. The same author's efuse_filter (binary fuse filters, OTP 24+, almost API-compatible) beat xor8 and xor16 at every size in the same benchmark (though its rows used pre-hashed `none` keys, skipping phash2). The vendored xorfilter.h also predates the upstream binary fuse filters.
- Strict license policies or proprietary distribution. The NIF compiles in git's EWAH bitmap files (bitmap.c, ewah_bitmap.c, ewok.h), which are GPL-2.0-or-later, alongside the Apache-2.0 code.
- Production use that needs an actively maintained native dependency. It has had no release since 0.8.2 (2021-12-02) and has no CI (issue #19 open). It has no Windows build hook, and any NIF memory bug crashes the whole BEAM node, as the fixed double-free in issue #17 showed.

## How it is fast

It is a xor filter (Graf & Lemire): each key maps to 3 slots in a table of about 1.23n 8- or 16-bit fingerprints. A lookup is one murmur64 finalizer mix, three multiply-shift range reductions (Lemire's alternative to modulo), three loads and one XOR compare, so it always costs exactly 3 memory accesses. A Bloom filter probes k bits instead. Construction peels a random 3-hypergraph and retries with a new seed up to 100 times. On the BEAM, much of the gain also comes from doing the whole probe in one C NIF call on a native resource. Bloomex probes in pure Elixir and Blex probes over Erlang atomics. The benchmark's roughly 155 ns per lookup includes the Elixir loop, phash2 and NIF-call overhead, not just the C probe.

## Compared with alternatives

Pick it only when the code runs on the BEAM and you want a ready-made NIF rather than writing one. Outside Erlang/Elixir, use the C library it wraps (Xor Filter / xor_singleheader, which now also has smaller binary fuse filters) or xorf in Rust. On the BEAM, first consider the same author's efuse_filter, whose fuse8 rows beat xor8 in the same benchmark.

## Integration

| | |
|---|---|
| **Form** | module (hex.pm/rebar3/mix package that compiles a C NIF shared library via make at build time) |
| **Dependencies** | No runtime deps. The build needs a C99 compiler, make (gmake on FreeBSD) and erl_interface (libei). It vendors xor_singleheader (Apache-2.0) and git's EWAH bitmap code (GPL-2.0+). |
| **Minimum toolchain** | Erlang/OTP 23+ for 0.8.x (the README says to use v0.5.2 below OTP 23), plus a C99 compiler. Newer OTP releases are not tested or documented; the benchmark used OTP 24.0.5 and Elixir 1.12.2. |
| **Platforms** | Linux, macOS (Apple Silicon since 0.8.2), FreeBSD and Solaris, per the rebar3 pre_hooks and Makefile. There is no Windows build hook. The code is endian-portable only for xor8 serialization. |
| **Thread safety** | Not documented. contain/2 only reads the finalized NIF resource, so sharing one filter across processes looks safe. The incremental builder is mutated in place by add/2 with no locking. |
| **Drop-in for the baseline** | false. The interface differs from Bloomex/Blex/erbloom: you build from a complete list up front, cannot add or delete later, choose the filter by module (xor8/xor16) rather than by target FPR, and the filter value is a {Reference \| Binary, HashFunction} tuple. |

## Gotchas

- The README says the default phash2 hash 'uses 60 bits on a 64-bit system', but erlang:phash2/1 returns 0..2^27-1. Colliding members are silently deduplicated (usort), so there is an FPR floor of roughly n/2^27. With a custom fun or `none`, keys are not deduplicated, and construction returns {error, duplicates_in_hash_error} if any hashes repeat.
- The incremental builder is not dirty-scheduled, so a large finalize can block a normal scheduler (open issue #21). It supports only the default hash (open issue #15). add/2 mutates and returns the same resource. add_elements_to_bitset also overwrites filter-&gt;bitmap without freeing the previous EWAH bitmap, so each add appears to leak it.
- contain/2 and from_bin/1 accept raw binaries, and their size check multiplies an unchecked 64-bit blockLength read from the binary. A crafted binary can therefore pass validation and cause out-of-bounds reads that crash the node. Only query or deserialize binaries you produced. xor16 to_bin copies host-endian uint16s (a 'TODO endianness' in the source).
- Errors come back as {error, Atom} tuples rather than exceptions or false. For example, a custom hash that returns a negative number or one above 2^64 makes contain return {error, get_key_for_contains_error}, and contain on an unfinalized builder returns {error, unfinalized_filter_error}.

## Known shortcomings

- Ratios are derived; the Bloom baselines ran at FPR 0.1/0.01 vs xor8's \~0.39%, so FPRs are not matched; the NIF is C built with -O3 (compiler unnamed).
- The default phash2 hash is only 27 bits (README says 60), adding \~0.7% FPR at 1M keys and \~7% at 10M. GPL-2.0+ EWAH files are compiled into the Apache-2.0 NIF (license risk). from_bin/contain size checks can overflow so a crafted binary causes an out-of-bounds read and node crash; incremental add seems to leak and is not dirty-scheduled (#21). Abandoned since 0.8.2 (2021-12); the same author's efuse_filter is faster.

## Caveats and trade-offs

This is a non-independent benchmark by the library author, run on a laptop (the README warns about this). The Bloom baselines are not set to xor8's FPR: Bloomex scalable and erbloom are configured at 0.1 error and Blex at 0.01, while xor8 is about 0.39%. The page's ratio column is against the fastest row (fuse8), so the ratios versus Bloom are derived. xor8/xor16 belong to the xor-filter family; the qualifying comparison is against the Bloom libraries. The C compiler is not stated.

Filters are immutable once finalized; large (&gt;10K element) initialization uses dirty NIFs and needs correct VM scheduler config; NIF-based (Rust), needs native compilation.

## Maintenance

Abandoned since 0.8.2 (2021-12-02), with 3 open issues including no CI and blocking incremental builds, and about 1,100 all-time hex downloads. The Erlang and xor code is Apache-2.0 but the bundled EWAH files are GPL-2.0+; at about 900 lines of NIF C it is small enough to fork, strip the EWAH builder from, and vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The mpope9/exor_bechmark README Benchee output (code at lib/exor_benchmark.exs) lists xor8 8 1M at 1.55 ms/645.20 ips and xor16 10M at 1.77 ms/565.42 ips, against Bloomex, Blex and erbloom rows that match the record. CPU, Elixir and OTP are stated, and the exor_filter c_src Makefile defaults to -O3, but the C compiler is never named. It is first-party, laptop-run and non-independent, so it stays at C.
- **Verifier notes:** The numbers match exactly. The fixes are: the ratios are now marked as derived, the NIF is C (the record said Rust), the size list includes 100, and the mismatched Bloom FPR settings are added to caveats. Metadata checked: Apache-2.0, last commit 2021-12-02 (abandoned), 35 stars, not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mpope9/exor_filter>
  - <https://github.com/mpope9/exor_bechmark>
  - <https://github.com/mpope9/exor_bechmark#benchee-output>
  - <https://raw.githubusercontent.com/mpope9/exor_bechmark/master/lib/exor_benchmark.exs>
  - <https://github.com/mpope9/exor_bechmark/blob/master/mix.exs>
  - <https://github.com/mpope9/exor_filter/blob/master/rebar.config>
  - <https://raw.githubusercontent.com/mpope9/exor_filter/master/c_src/Makefile>
  - <https://hex.pm/api/packages/exor_filter>
- **Sources the enricher read:**
  - <https://github.com/mpope9/exor_filter>
  - <https://github.com/mpope9/exor_filter/blob/master/README.md>
  - <https://github.com/mpope9/exor_filter/blob/master/c_src/xor_filter_nif.c>
  - <https://github.com/mpope9/exor_filter/blob/master/c_src/xorfilter.h>
  - <https://github.com/mpope9/exor_filter/blob/master/c_src/Makefile>
  - <https://raw.githubusercontent.com/mpope9/exor_filter/master/c_src/bitmap.c>
  - <https://raw.githubusercontent.com/mpope9/exor_filter/master/c_src/ewah_bitmap.c>
  - <https://raw.githubusercontent.com/mpope9/exor_filter/master/c_src/ewok.h>
  - <https://raw.githubusercontent.com/mpope9/exor_filter/master/c_src/git-compat-util.h>
  - <https://github.com/mpope9/exor_filter/blob/master/src/exor_filter.erl>
  - <https://github.com/mpope9/exor_filter/blob/master/src/xor8.erl>
  - <https://github.com/mpope9/exor_filter/blob/master/src/exor_filter.app.src>
  - <https://github.com/mpope9/exor_filter/blob/master/rebar.config>
  - <https://github.com/mpope9/exor_filter/blob/master/test/exor_filter_test.erl>
  - <https://github.com/mpope9/exor_filter/issues?q=is%3Aissue>
  - <https://github.com/mpope9/exor_filter/issues/15>
  - <https://github.com/mpope9/exor_filter/issues/17>
  - <https://github.com/mpope9/exor_filter/issues/19>
  - <https://github.com/mpope9/exor_filter/issues/21>
  - <https://github.com/mpope9/exor_filter/pull/18>
  - <https://github.com/mpope9/exor_filter/pull/20>
  - <https://github.com/mpope9/exor_filter/pull/22>
  - <https://github.com/mpope9/exor_filter/tags>
  - <https://github.com/mpope9/exor_bechmark>
  - <https://github.com/mpope9/exor_bechmark#benchee-output>
  - <https://github.com/mpope9/exor_bechmark/blob/master/lib/exor_benchmark.exs>
  - <https://github.com/mpope9/exor_bechmark/blob/master/mix.exs>
  - <https://raw.githubusercontent.com/mpope9/efuse_filter/master/README.md>
  - <https://hex.pm/api/packages/exor_filter>
  - <https://hex.pm/api/packages/efuse_filter>
  - <https://www.erlang.org/doc/apps/erts/erlang.html>
  - <https://hn.algolia.com/api/v1/search?query=exor_filter&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/mpope9/exor_filter`) · [data/wave6/enrich/raw/github_com_mpope9_exor_filter.json](../../../data/wave6/enrich/raw/github_com_mpope9_exor_filter.json) (enrichment confidence 0.8)

</details>
