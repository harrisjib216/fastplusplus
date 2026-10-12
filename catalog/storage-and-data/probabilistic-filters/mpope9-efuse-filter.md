# efuse_filter (Erlang NIF, Binary Fuse Filter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Erlang` · `Apache-2.0` · 🔴 abandoned

> Erlang/Elixir NIF wrapping FastFilter's C binary fuse8 filter; static membership filter beating BEAM Bloom libraries on lookup latency.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | Figures are Benchee average time per 10,000 lookups. At 1M: fuse8 1.42 ms (705.73 ips) vs Bloomex 8.87 ms, Blex 13.17 ms and erbloom 4.01 ms, which is 6.26x, 9.29x and 2.83x (derived from page data, ips ratios). At 10M: fuse8 1.54 ms (648.42 ips) vs Bloomex 15.24 ms and Blex 18.47 ms, which is 9.88x and 11.98x (derived from page data). The page's 'erbloom 10M' row (3.90 ms, 2.53x derived) is invalid, because the script builds that filter from the 10k-key list. The page's Benchee 'x slower' figures (6.69x, 9.94x, 3.03x, 11.50x, 13.93x, 2.95x) are measured against the fastest row, fuse8 over a 100-element filter, not against the same-size fuse8. |
| **Workload** | Benchee (mpope9/exor_bechmark, lib/exor_benchmark.exs; warmup 2 s, time 5 s) builds each filter over the integer keys 1..N, for N = 100, 1k, 100k, 1M and 10M. Each iteration then looks up keys 1..10,000, which are all positive lookups for N &gt;= 10k. The fuse8 filters are built with `:none`, so their lookups skip erlang:phash2 on each key. The xor8/xor16 filters use default hashing, and the Bloom libraries hash internally. The Bloom libraries are Bloomex (pure Elixir, scalable, error 0.1), Blex (Erlang atomics, 0.01) and erbloom (Rust NIF, 0.1). efuse_filter is pinned in mix.lock at commit 7fc2c2d (2021-08-07). The 'erbloom 10M' filter is actually created from the 10k list (create_erbloom(bin10k)). |
| **Metric** | latency |
| **Hardware** | Intel Core i5-7267U CPU @ 3.10GHz, 4 cores, 8GB RAM, macOS (per repo's own Benchee output) |
| **Compiler and flags** | Elixir 1.12.2 and Erlang/OTP 24.0.5, per the Benchee output. efuse_filter is a C NIF wrapping FastFilter's binaryfusefilter.h, not Rust. Its c_src/Makefile defaults on macOS to `cc -O3 -std=c99 -arch x86_64 -finline-functions`, and the compiler version is not stated. erbloom is the Rust NIF, and its build profile is not stated. |
| **Adoption** | 7 stars; hex.pm efuse_filter 0.1.0 (only release, 2021-08-08), 298 all-time downloads |
| **Last commit** | 2021-08-17 |
| **Links** | [repository](https://github.com/mpope9/efuse_filter) · [benchmark](https://github.com/mpope9/exor_bechmark#benchee-output) |

## Verdict

The author's own Benchee suite ran on an Intel Core i5-7267U laptop under macOS with Elixir 1.12.2 and OTP 24.0.5; the NIF was built with the Makefile's -O3 defaults and the compiler version is not stated. 10,000 positive lookups of pre-hashed integers took 1.42 ms on a 1M-key fuse8 filter, against 4.01 ms for the Rust-NIF erbloom (\~2.8x), 8.87 ms for Bloomex and 13.17 ms for Blex. At 10M keys it was 1.54 ms against 15.24 ms and 18.47 ms (\~9.9x and \~12x); all ratios are derived. Only fuse8 skipped phash2, the Bloom filters ran at looser 10% and 1% FPRs, and the 'erbloom 10M' row was really built from 10k keys.

## Use it when

- A read-mostly deny list, seen-ID set or cache pre-check in an Erlang/Elixir service, built once from a known key set (thousands to tens of millions of keys) and queried from many processes.
- You already have well-distributed 64-bit integer hashes and can use new/2 with `none`. That is the benchmarked mode, and it keeps the false-positive rate near 0.39% at millions of keys.
- You want to ship or persist the filter. to_bin produces a 28-byte little-endian header plus the fingerprint array, and contain queries that binary in place without deserializing it.
- You are replacing Bloomex or Blex and lookup latency is the bottleneck. At 1M keys the author's benchmark shows about 6x and 9x faster lookups, and about 2.8x over the Rust-NIF erbloom (ratios derived).

## Skip it when

- The set changes. There is no insert or delete after finalize, so every update is a full rebuild. The rebuild needs roughly 32 bytes per key of transient C memory (derived from the key buffer plus populate's scratch arrays), on top of the Erlang list and the `sets` dedup copy.
- Default hashing on large sets. erlang:phash2/1 returns only 27-bit values (0..2^27-1), so any non-member whose phash2 value collides with a member's is a false positive. The derived effective rate is \~1.1% at 1M keys and \~7.8% at 10M, against 0.39% for the filter alone. Use `none` with a 64-bit hash instead.
- You need a false-positive rate below \~0.4%. Only fuse8 is exposed (no fuse16); exor_filter offers xor16.
- Filters come from untrusted sources. The NIF checks only that the binary length matches its ArrayLength field (its minimum-size check is 16 bytes, for a 28-byte header) and never validates the segment fields, so a crafted binary can drive out-of-bounds reads inside the VM.
- You need a maintained dependency. There has been a single 0.1.0 release (2021), and the vendored binaryfusefilter.h predates two upstream fixes: guards for 0-2-key sets (2021-08-21/22), and a construction retry path that did not reset its state or reseed (2022-03-23, commit ed27385).

## How it is fast

It is a binary fuse filter (Graf & Lemire, 'Binary Fuse Filters: Fast and Smaller Than Xor Filters'). Each key goes through a seeded murmur64 finalizer and maps to three slots in adjacent segments of a byte array. A lookup XORs those three bytes and compares the result with the key's fingerprint, so every query is exactly three memory reads with no loop over k hash functions. The array is built by hypergraph peeling and takes about 9 bits per key at large n (size factor max(1.125, 0.875 + 0.25\*ln(10^6)/ln n) in the vendored header). Against Bloomex and Blex, most of the measured gap comes from running the probe in C instead of BEAM code. Each contain is still one NIF call, about 140 ns per lookup at 1M keys in the author's run (derived; this includes Enum and fun-call overhead).

## Compared with alternatives

Pick it over exor_filter (same author, xor8/xor16 NIF) when you want the smaller binary fuse layout and fuse8's error rate is good enough; the xorfilter entry cites \~13% over the information-theoretic bound, against \~23% for xor filters. The shared benchmark's \~9% lookup edge over xor8 at 1M keys is confounded, because only fuse8 skipped phash2. Choose exor_filter for 16-bit fingerprints, a custom hash function or a lower-memory incremental build, and outside the BEAM use the upstream C header (xor_singleheader) or xorf/xorfilter directly.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | None at runtime, because FastFilter's binaryfusefilter.h is vendored. Building needs make (gmake on FreeBSD) and a C99 compiler, run by a rebar3 pre-compile hook. |
| **Minimum toolchain** | Erlang/OTP 24+ (per the README; it uses sets version 2), rebar3 or Mix, and a C99 compiler with __uint128_t (GCC or Clang) |
| **Platforms** | rebar3 build hooks exist only for Linux, macOS, FreeBSD and Solaris, so there is no Windows build. It is 64-bit only in practice because it needs __uint128_t, and the macOS Makefile defaults target x86_64 only. |
| **Thread safety** | Not documented. Built filters are immutable NIF resources or binaries and contain only reads them, so concurrent lookups from many processes look safe (inferred from the source). |
| **Drop-in for the baseline** | partial — it is not API-compatible with Bloomex, Blex or erbloom. It needs the whole key set before the build, cannot add keys afterwards, and has no FPR parameter. The README says it is almost API-compatible with exor_filter (xor8/xor16). |

## Gotchas

- NIF errors are stored in the record instead of being returned. new(List, none) only checks that some element is an integer (lists:any), so a mixed list or negative integers produce a #fuse8{} whose reference is {error, convert_to_uint64_t_error}. The first contain on that record raises case_clause. A negative integer key passed to contain on a `none` filter also raises case_clause.
- A serialized filter built with `none` must be queried with contain/4 (..., none) or reloaded with from_bin/2. contain/2 and contain/3 on a binary always apply phash2, which gives silent false negatives.
- The helper named over_100k matches on 10_001, so builds of more than 10,000 elements (not 100k, as its doc says) run on a dirty CPU scheduler. Smaller builds and every contain call run on normal schedulers; open issue #4 proposes a dirty contain for large filters.
- On macOS the Makefile's default CFLAGS and LDFLAGS hard-code `-arch x86_64`. An Apple Silicon (arm64) BEAM therefore needs those variables overridden before the NIF will load (inferred from the Makefile, not tested).

## Known shortcomings

- The published ratios came from Benchee's 'vs fastest row' column; at equal size the derived gains are 6.26x/9.29x/2.83x (1M, vs Bloomex/Blex/erbloom) and 9.88x/11.98x (10M). The 'erbloom 10M' row really used 10k keys (script bug); fuse8 got pre-hashed keys while the others hashed. The NIF is C, not Rust.
- The default phash2 hash is only 27 bits, giving \~1.1% FPR at 1M keys and \~7.8% at 10M (the filter alone is 0.39%). NIF errors are stored in the record rather than returned (case_clause crash); a filter built with 'none' and then serialized has contain/2,3 apply phash2 (silent false negatives); the serialized binary is barely validated (out-of-bounds reads on crafted input); the vendored header predates upstream fixes; macOS Makefile hard-codes -arch x86_64; fuse8 only; abandoned since 2021.

## Caveats and trade-offs

The benchmark suite (exor_bechmark, 0 stars, no license) is by the same author as efuse_filter and exor_filter. It ran on a laptop, which the page itself flags as 'not a production environment'. Only fuse8 gets pre-hashed keys (`:none`), which skips erlang:phash2 on every lookup, while the other rows hash. Bloomex and Blex are pure Elixir/Erlang, so most of the 6-12x gap over them is C NIF vs BEAM code. The fairest baseline is erbloom, the Rust NIF: \~2.8x at 1M (derived). The erbloom 10M row is really a 10k-key filter. The Bloom filters were configured at looser FPRs (0.1 or 0.01) than fuse8's \~0.4%. Lookups are positive-only, on sequential integer keys. The hex.pm package has a single 0.1.0 release (2021-08-08).

Filters are immutable once finalized; incremental build path uses Erlang `sets` and has a higher memory footprint than the batch API; NIF-based (Rust), so requires native compilation.

## Maintenance

Abandoned: there has been one hex release (0.1.0, 2021-08-08, \~300 downloads), the last commit was 2021-08-17, and in November 2024 the author wrote that it had been 'quite a while' since he last touched it. It is Apache-2.0 and about 1,150 lines of C and Erlang, so vendoring it is realistic, and the Zabrane/efuse_filter fork carries an unmerged update to the latest upstream header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** This is a first-party suite by the same author. The code is public (mpope9/exor_bechmark lib/exor_benchmark.exs), and the page states the CPU (i5-7267U) and Elixir/OTP versions. The measured C NIF's compiler and flags are not stated on the page (only Makefile defaults), and erbloom's Rust build is unstated. The script also has a sizing bug, so it stays C. The downgrade is for the overstated ratios, not the tier.
- **Verifier notes:** The ms and ips values are on the page, but most of the record's ratios came from Benchee's comparison column, which is relative to 'fuse8 100' rather than the same-size fuse8. Of the record's ratios, only erbloom 1M (2.8x) was a correct same-size ratio. The record also wrongly called the NIF Rust; it is C. The metadata checks out: Apache-2.0, 7 stars, not a fork, not archived, last commit 2021-08-17, abandoned. The language field says Erlang, but the hot path is C (the language field is not correctable here).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/mpope9/efuse_filter>
  - <https://github.com/mpope9/efuse_filter/blob/main/c_src/Makefile>
  - <https://github.com/mpope9/efuse_filter/blob/main/LICENSE>
  - <https://github.com/mpope9/efuse_filter/blob/7fc2c2d66260a02dfacfe2ede970f22c21224216/src/fuse8.erl>
  - <https://github.com/mpope9/efuse_filter/commits/main>
  - <https://github.com/mpope9/exor_bechmark#benchee-output>
  - <https://github.com/mpope9/exor_bechmark/blob/master/lib/exor_benchmark.exs>
  - <https://github.com/mpope9/exor_bechmark/blob/master/mix.exs>
  - <https://github.com/mpope9/exor_bechmark/blob/master/mix.lock>
  - <https://hex.pm/api/packages/efuse_filter>
- **Sources the enricher read:**
  - <https://github.com/mpope9/efuse_filter>
  - <https://github.com/mpope9/efuse_filter/blob/main/c_src/fuse_filter_nif.c>
  - <https://github.com/mpope9/efuse_filter/blob/main/c_src/binaryfusefilter.h>
  - <https://github.com/mpope9/efuse_filter/blob/main/c_src/Makefile>
  - <https://github.com/mpope9/efuse_filter/blob/main/src/fuse8.erl>
  - <https://github.com/mpope9/efuse_filter/blob/main/src/efuse_filter.erl>
  - <https://github.com/mpope9/efuse_filter/blob/main/src/efuse_filter.app.src>
  - <https://github.com/mpope9/efuse_filter/blob/main/rebar.config>
  - <https://github.com/mpope9/efuse_filter/blob/main/test/efuse_filter_test.erl>
  - <https://github.com/mpope9/efuse_filter/issues/4>
  - <https://github.com/mpope9/efuse_filter/issues/5>
  - <https://github.com/mpope9/efuse_filter/pulls?q=is%3Apr>
  - <https://github.com/mpope9/efuse_filter/commits/main>
  - <https://github.com/mpope9/efuse_filter/forks>
  - <https://github.com/mpope9/efuse_filter/compare/main...Zabrane:efuse_filter:main>
  - <https://hex.pm/api/packages/efuse_filter>
  - <https://repo.hex.pm/tarballs/efuse_filter-0.1.0.tar>
  - <https://github.com/mpope9/exor_bechmark#benchee-output>
  - <https://github.com/mpope9/exor_bechmark/blob/master/lib/exor_benchmark.exs>
  - <https://github.com/mpope9/exor_bechmark/blob/master/mix.lock>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/include/binaryfusefilter.h>
  - <https://github.com/FastFilter/xor_singleheader/commits/master/include/binaryfusefilter.h>
  - <https://github.com/FastFilter/xor_singleheader/commit/ed27385e1ca4a67abfc17ecd0da13045fe244ba8>
  - <https://github.com/FastFilter/xor_singleheader/issues/27>
  - <https://github.com/FastFilter/xor_singleheader/issues/44>
  - <https://github.com/FastFilter/xor_singleheader/issues/77>
  - <https://github.com/mpope9/exor_filter>
  - <https://github.com/mpope9/exor_filter/issues>
  - <https://github.com/mpope9/exor_filter/blob/master/c_src/Makefile>
  - <https://www.erlang.org/doc/apps/erts/erlang.html>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/mpope9/efuse_filter`) · [data/wave6/enrich/raw/github_com_mpope9_efuse_filter.json](../../../data/wave6/enrich/raw/github_com_mpope9_efuse_filter.json) (enrichment confidence 0.7)

</details>
