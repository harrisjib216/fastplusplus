# Copyable

Entries with a confirmed OSI license or a CC0/public-domain dedication: code can be vendored, wrapped, or forked. Grouped by license family, then domain and category; tier A/B first, tier C/D under *Unverified claims*.

## Permissive

### compression-and-encoding

#### general-lossless

##### LZ4  `C`  `BSD-2-Clause`  `active`  `Tier B`

In-memory block/frame compressor beating zlib deflate on speed, trading compression ratio for GB/s decode.

**Beats:** zlib — First-party lzbench run (LZ4 v1.9.0, GCC 8.2.0, Core i7-9700K @4.9GHz, Ubuntu 4.18.0-17) reports LZ4 default at 780/4970 MB/s (compress/decompress) and ratio 2.101, versus zlib deflate 1.2.11 -1 at 100/415 MB/s and ratio 2.730 — roughly 7.8x faster compression and 12.0x faster decompression at a lower ratio. An independent lzbench 2.0.1 run (gcc 14.2.0, AMD EPYC 9554) corroborates the direction: lz4 1.10.0 at 577/3716 MB/s vs zlib 1.3.1 -1 at 93.0/323 MB/s.

**How:** LZ4 uses a byte-oriented LZ77 variant with a simple hash-chain match finder and no entropy coding stage (no Huffman/range coding like deflate), so both compression and decompression are dominated by cheap memcpy-style literal/match copies instead of bit-level decoding. Decompression in particular is just a sequence of length-prefixed copy operations, which is why it reaches multi-GB/s per core. A tunable "acceleration" factor lets the compressor skip more match-search work for more speed at a lower ratio, and LZ4_FAST_DEC_LOOP enables an optimized decode loop on x86/x64/aarch64.

**Use it when:**
- Hot-path in-memory compression where decompression speed dominates (caches, IPC payloads, columnar/log formats)
- Read-heavy data where you decompress far more often than you compress
- Need dictionary compression for many small, similar payloads (frame API supports a 64KB dictionary window)
- Embedded/freestanding targets: single C90 source pair (lz4.c/lz4.h), optional LZ4_FREESTANDING build removes libc dependency
- Already have LZ4_HC available when you need a higher ratio at the same decompression speed but slower compression

**Skip it when:**
- Compression ratio matters more than speed: zlib -6 (3.099) and zstd both beat LZ4's 2.101 default ratio
- Need a drop-in replacement for a zlib/deflate API surface — LZ4's API and block/frame formats are different
- Want one universal knob for ratio/speed tradeoffs across a wide range — zstd's level range is broader than LZ4's acceleration + HC split
- Pulling in a released package manager build: the current tagged release (v1.10.0, 2024-07-22) predates a 2025-06-01 fix for unhandled NULL-pointer args in lz4frame (CVE-2025-62813); only the dev branch has it
- Need built-in multithreading: LZ4 itself is single-thread per call; parallelism is the caller's responsibility

**Integration:** source-drop (lz4.c+lz4.h minimum) | static lib | shared lib · none for block API; frame API (lz4frame) additionally needs xxhash.c/xxhash.h from the same repo; lz4file adds a <stdio.h> dependency · C90 (with long long and optional variadic macros); C99+ used opportunistically (e.g. restrict) with a C90 fallback · any C90 target incl. 32-bit and freestanding/embedded (LZ4_FREESTANDING=1 drops libc); LZ4_FAST_DEC_LOOP auto-enabled on x86, x64, aarch64

**Vs siblings:** Pick LZ4 over Zstandard when decompression throughput and minimal-dependency portability (down to freestanding C90) matter more than ratio; zstd's -1 level already beats LZ4's ratio (2.883 vs 2.101) at somewhat lower speed, and zstd exposes a much wider ratio/speed level range, so pick zstd when you want one tunable knob spanning LZ4-like speed to gzip-beating ratio.

**Gotchas:**
- Block API (lz4.h) is not self-describing: caller must transmit/store the compressed size and a max decompressed-size bound separately
- Advanced/experimental symbols behind LZ4_STATIC_LINKING_ONLY are excluded from the shared-library ABI and can break between versions — static-link only
- Repo license is split by directory: lib/ is BSD-2-Clause, programs/ (CLI, tests) is GPL-2.0-or-later; check which files you actually vendor
- Open issue #1779 (as of 2026-08) flags the streaming-decompression "synchronized mode" docs as wrong/misleading — verify ring-buffer streaming behavior against source, not just the header comment

**Status:** Actively maintained (dev branch commit 2026-06-01) but the latest tagged release is v1.10.0 from 2024-07-22, so a NULL-pointer-arg fix (CVE-2025-62813, merged 2025-06-01) is not yet in any released tag; usability is 'copyable' since every file carries an OSI license (BSD-2-Clause in lib/, GPL-2.0-or-later elsewhere).

[repo](https://github.com/lz4/lz4) · [benchmark](https://github.com/lz4/lz4)

##### Zstandard (zstd)  `C`  `BSD-3-Clause OR GPL-2.0-only`  `active`  `Tier B`

General-purpose lossless compressor beating zlib/deflate on speed and ratio, with tunable levels and negative fast modes.

**Beats:** zlib — zstd 1.5.7 -1 measured 510 MB/s compression and 1550 MB/s decompression at ratio 2.896, vs zlib 1.3.1 -1 at 105 MB/s / 390 MB/s and ratio 2.743, in the project's own README Benchmarks table (lzbench, gcc 14.2.0, Silesia corpus, single-threaded, Core i7-9700K @ 4.9GHz, Ubuntu 24.04). The lzbench project's own README independently corroborates a similar zstd-vs-zlib gap on different hardware (AMD EPYC 9554, zstd 1.5.6 -1 at 422/1347 MB/s vs zlib 1.3.1 -1 at 93.0/323 MB/s).

**How:** Compression uses selectable match-finder strategies per level, from cheap hash-chain/greedy search at low levels up to binary-tree/optimal parsing at high levels, so speed vs ratio is a single tunable knob (including negative --fast=# levels that skip expensive search entirely). The entropy stage uses FSE (tANS) and Huff0, which decode faster than classic Huffman/zlib entropy coding. On x86-64 the library auto-dispatches to BMI2 instructions at runtime when available, mainly speeding up the decoder; optional dictionary training (ZDICT) amortizes the cost of small, similarly-shaped inputs.

**Use it when:**
- General file/stream compression where you want a better ratio than zlib at several times the throughput
- Workloads needing a single tunable speed/ratio knob, from --fast=# (skip ratio for max speed) up to level 22 (max ratio)
- Many small, structurally similar records (e.g. JSON/API payloads) via a trained dictionary, where per-item ratio would otherwise be poor
- Large-payload compression that can use multiple threads (built with ZSTD_MULTITHREAD + pthread)
- Codebases needing a permissive-or-copyleft license choice (dual BSD-3-Clause / GPLv2)

**Skip it when:**
- You need byte-compatible zlib/deflate/gzip output for an existing wire protocol or file format — zstd's container is a different, RFC 8878 format
- You need the best possible ratio regardless of CPU cost — the README's own table doesn't include xz, a stronger-ratio baseline it lists as uncompared here
- You're decompressing untrusted archives via the CLI's recursive mode: a crafted circular symlink can hang `zstd -d -r -f` (open issue #4081)
- You need the experimental/advanced API surface (behind ZSTD_STATIC_LINKING_ONLY) in a dynamically-linked build — it's explicitly static-link-only and unstable across versions
- You're on a toolchain where strict C90 portability doesn't matter and you'd rather have a simpler, smaller single-strategy codec

**Integration:** static lib | shared lib | source-drop (Makefile is the reference build; CMake, Meson, Buck, Bazel, and VS project files are also maintained) · none for core library; POSIX pthread required only if built with ZSTD_MULTITHREAD for multithreaded compression · strict C90 C (per CONTRIBUTING.md); no C99/C++ requirement for the library itself · portable C90 baseline runs anywhere; x86-64 gets optional runtime BMI2 dispatch (auto-detected, not required); aarch64 supported; Windows via VS2008+/CMake; macOS Universal2 (x86_64/arm64) build documented

**Vs siblings:** Pick zstd over LZ4 when ratio matters more than raw peak speed: zstd -1 gets 2.896 ratio at 510/1550 MB/s vs LZ4's 2.101 ratio at 780/4970 MB/s in the same README table. Pick LZ4 instead when you need decompression well above 2 GB/s or compression above ~700 MB/s and can accept a much lower ratio.

**Gotchas:**
- Static and dynamic library builds default to different threading modes (single- vs multi-threaded); mismatched expectations here are a common build-config surprise
- Advanced/experimental API (unlocked via ZSTD_STATIC_LINKING_ONLY) is explicitly forbidden with dynamic linking because its ABI is unstable
- CLI recursive decompress can hang on a crafted circular symlink (open issue #4081) — a library-embedding concern only if you shell out to the CLI
- Open performance-regression report (#4587) for level 18 after an internal API v2 change, unresolved as of this session

**Status:** Actively maintained (last commit 2026-09-18 on branch 'dev'), reference implementation of RFC 8878 used in the Linux kernel, Chromium, FreeBSD, and PostgreSQL; usability is 'copyable' and it is dual-licensed BSD-3-Clause OR GPLv2.

[repo](https://github.com/facebook/zstd) · [benchmark](https://github.com/facebook/zstd)

### crypto-and-hashing

#### non-crypto-hashes

##### xxHash  `C`  `BSD-2-Clause (library xxhash.c/xxhash.h); xxhsum CLI is GPL-2.0-or-later`  `active`  `Tier A`

SIMD-vectorized non-cryptographic hash family; XXH3 beats CityHash ~2.7x on in-RAM buffer bandwidth.

**Beats:** CityHash — Project's own tests/bench program (Clang v10.0, -O3, Intel i7-9700K, Ubuntu 20.04 x64) measured XXH3 (AVX2) at 59.4 GB/s versus CityHash64 at 22.0 GB/s (~2.7x) and CityHash128 at 21.7 GB/s (~2.7x); versus Murmur3 (32-bit) at 3.9 GB/s (~15.2x, not width-matched). Small-data velocity: XXH3 133.1 vs City64 76.6 vs Murmur3 56.1.

**How:** XXH3 uses vectorized arithmetic (SSE2/AVX2/AVX512/NEON/VSX/RVV/LoongArch LSX-LASX, auto-selected at compile time or runtime-dispatched) with multiply-and-fold mixing tuned for both large-buffer bandwidth and small-key latency. XXH_INLINE_ALL header-only mode lets the compiler inline and constant-fold hashing when key length is a compile-time constant, reported at roughly +200% for small keys. Optional runtime ISA dispatch (Makefile DISPATCH=1 / LIBXXH_DISPATCH=1) picks the best available vector unit at startup instead of requiring a fixed -m flag at build time.

**Use it when:**
- Non-cryptographic hashing of in-RAM buffers where throughput dominates (checksums, hash tables, dedup, content-addressing)
- Hot loops hashing small/fixed-length keys, using XXH_INLINE_ALL for compile-time-constant lengths
- Need identical hash output across little/big-endian and 32/64-bit platforms
- Embedded or constrained targets: XXH32 for 32-bit-only hardware, or XXH_NO_STDLIB to avoid malloc/free
- Want SIMD speedup across x86 (AVX2/AVX512), ARM (NEON), POWER (VSX), or RISC-V (RVV) without hand-writing per-ISA paths

**Skip it when:**
- Cryptographic use cases (signatures, password storage, adversarial-input integrity) - README explicitly says do not use xxHash for these
- Comparing against 32-bit-only hashes and expecting a width-matched number: the project's own Murmur3 benchmark row is the 32-bit variant, not matched to XXH3's 64/128-bit output
- Raw single-thread bandwidth is the only criterion and the ~1.09x edge of wyhash (per catalog sibling entry) matters more than xxHash's broader platform/test-suite maturity
- Distributing the xxhsum CLI where GPL-2.0-or-later is unacceptable (the library itself, xxhash.c/xxhash.h, is BSD-2-Clause and unaffected)
- Need statically-allocated streaming state guaranteed correct with zero further testing: the streaming API has had real bugs in the past (see gotchas), now fixed but worth pinning a recent release

**Integration:** source-drop (xxhash.c + xxhash.h); also buildable as static/shared libxxhash, or header-only via XXH_INLINE_ALL · none required; optional use of stdlib.h (malloc/free, disable via XXH_NO_STDLIB) and string.h (memcpy/memset/memcmp, redirectable via XXH_memcpy/XXH_memset/XXH_memcmp macros) · C90 (ANSI C) baseline with optional C99/C++11 feature detection; compiles cleanly as C++ via an extern "C" guard (disable with XXH_NO_EXTERNC_GUARD) · x86/x64 (scalar, SSE2, AVX2, AVX512, runtime-dispatchable), aarch64/ARM (NEON), PowerPC (VSX), RISC-V (RVV), LoongArch (LSX/LASX), plus a portable scalar fallback everywhere; produces identical hashes on little- and big-endian systems

**Vs siblings:** wyhash edges out XXH3 by roughly 1.09x bandwidth per the catalog sibling entry, but xxHash documents wider SIMD/architecture coverage (SSE2/AVX2/AVX512/NEON/VSX/RVV/LoongArch), a dedicated massive collision tester plus SMHasher pass, and a mature package ecosystem (vcpkg, Repology-tracked distro packages); pick xxHash when portability across architectures and test-suite maturity outweigh a single-digit-percent throughput gap.

**Gotchas:**
- Explicitly not a cryptographic hash - README warns against signatures, password storage, or adversarial-integrity use
- Peak AVX2/AVX512 throughput needs either the matching -m compiler flag or Makefile DISPATCH=1/LIBXXH_DISPATCH=1 runtime dispatch; a naive build can silently run at scalar/SSE2 speed
- Streaming API has a history of real bugs: issue #816 "Streaming hashing is broken" (2023) and #378 "Uneven chunk size in xxh3 stream computes wrong hash" (2020), both closed/fixed but signal the incremental path is the more fragile part of the API
- XXH_FORCE_ALIGN_CHECK / XXH_FORCE_MEMORY_ACCESS build macros exist because some architectures need a different memory-access strategy for best performance; the defaults are auto-selected per architecture and may need tuning on unusual targets

**Status:** Actively maintained (last commit 2026-09-20, 11.3k stars, CHANGELOG shows ongoing RISC-V/LoongArch perf work); library (xxhash.c/xxhash.h) is BSD-2-Clause and trivially vendorable, while the separate xxhsum CLI is GPL-2.0-or-later.

[repo](https://github.com/Cyan4973/xxhash) · [benchmark](https://github.com/Cyan4973/xxhash)

##### wyhash  `C`  `Unlicense`  `active`  `Tier B`

Header-only 64-bit non-cryptographic hash + PRNG; about 9% faster bulk throughput than xxHash's XXH3.

**Beats:** xxHash — On the rurban/smhasher bulk-speed test (262144-byte keys, averaged across alignments 0-7) on the suite's AMD Ryzen 5 3350G 3.6GHz reference machine (compiler/flags not stated), wyhash measured 22,640.53 MiB/s versus xxHash's XXH3 at 20,853.74 MiB/s (~1.09x), City64 at 14,390.09 MiB/s (~1.57x), and Murmur3A at 3,027.30 MiB/s (~7.5x).

**How:** The core primitive is a 128-bit multiply-and-xor-mix (_wymum/_wymix, "MUM"), implemented via __uint128_t on GCC/Clang or the _umul128 intrinsic on MSVC x64, so one multiply produces two mixed 64-bit halves per round. For inputs >=48 bytes the main loop is unrolled to run three interleaved MUM mixes per 48-byte chunk (three independent accumulator states), overlapping multiply latency across chunks instead of serializing one mix per 16 bytes. Short inputs (<=16 bytes) take a separate branch that reads overlapping 3/4/8-byte windows directly instead of looping, avoiding per-byte overhead on small keys.

**Use it when:**
- Bulk hashing of large buffers (the benchmarked case is 256KB keys) where a ~9% throughput edge over XXH3 matters at scale, e.g. content-addressed storage or dedup
- Small/short keys (<=16 bytes), which get a dedicated fast path — this is why Go (1.17+), Zig, V, and Nim use it as their default map hash
- C/C++ projects that want a single vendorable header with no build step, working on 32- or 64-bit, big- or little-endian, x86/aarch64
- Internal hash tables or checksums where non-adversarial input is acceptable and ~62-bit (not full 64-bit) collision resistance is fine
- Projects already comfortable adopting a library whose own maintainer is steering new users toward its successor (see status_note)

**Skip it when:**
- Hashing untrusted/adversarial input with the default secret — the built-in _wyp constant is public; use make_secret() to derive a per-process secret for hash-flood resistance, which the library does not do automatically
- Anywhere full 64-bit collision resistance or a security review is required — the author states wyhash/wyrand are only about 62-bit collision resistant, per outside reports cited in the README
- Generating very long random streams with wyrand — the author's own README says wyrand fails PractRand at 32TB/23 days, and issue #130 separately reported wyrand failing 64-bit 1-D collision tests
- Using the separate 32-bit variant (wyhash32.h) on 4-byte keys from sparse/bitflip keysets — open issue #153 (filed 2026-02-27, still open) reports SMHasher3 failures there; this does not affect the 64-bit wyhash() function that was benchmarked here
- Starting a brand-new project where you want the actively promoted state of the art — the wyhash README itself says the project 'has evolved into rapidhash' and points new adopters there

**Integration:** header-only · none beyond the C standard library (stdint.h, string.h); <intrin.h> pulled in only for the MSVC x64 path · C99 / C++11-ish (stdint.h, static inline); relies on GCC/Clang __uint128_t or MSVC's _umul128 intrinsic for the 128-bit multiply, with a portable 32x32 fallback for other compilers · x86-64, aarch64, and 32-bit systems; both little- and big-endian (explicit byteswap paths); GCC, Clang, MSVC, Intel C++

**Vs siblings:** Pick wyhash over xxHash when the ~9% bulk-throughput edge (22,640.53 vs 20,853.74 MiB/s on the cited single-CPU run) is worth taking on a Tier-B, single-reference-machine result with no stated compiler/flags; xxHash (XXH3) is the safer default when you want a widely adopted, spec-documented hash with results reproduced across more hardware.

**Gotchas:**
- Default secret (_wyp) is a fixed, publicly known constant baked into the header; generate your own with make_secret(seed, secret) if flood resistance matters
- Only ~62-bit, not full 64-bit, collision resistance per the README's own limitations section
- wyrand fails PractRand on very long streams (32TB, ~23 days) per the author's README
- wyhash32.h (a separate, distinct file from the benchmarked 64-bit wyhash.h) currently fails SMHasher3 Sparse/Bitflip tests on 4-byte keys — open issue #153, unresolved as of 2026-08

**Status:** Actively maintained (last commit 2026-03-23; 19 open issues, not archived), and public-domain (Unlicense) so it costs nothing to vendor, but the author's own README states wyhash 'has evolved into rapidhash,' its designated successor, so new adopters are explicitly pointed elsewhere.

[repo](https://github.com/wangyi-fudan/wyhash) · [benchmark](https://github.com/rurban/smhasher)

### parsing-and-text

#### regex-engines

##### Hyperscan  `C`  `BSD-3-Clause`  `active`  `Tier B`

SIMD multi-pattern regex matching library beating PCRE2 6.9-183x on large network-security rulesets.

**Beats:** PCRE2 — Measured on a single core of an Intel Xeon Platinum 8180 (GCC 5.4) against PCRE2 v10.32 with JIT enabled: Hyperscan's multi-pattern mode matched the Suricata ET-Open ruleset (2,800 regexes) against a 1GB real HTTP trace in 133s vs PCRE2's 913s (6.9x), and the Snort Talos ruleset (1,300 regexes) in 2.15s vs 394s (183x); single-pattern mode was a more modest 1.8-2.3x over PCRE2 on the same traces.

**How:** Uses hybrid automata (combinations of NFA/DFA representations) plus SIMD-accelerated multi-literal prefilter engines (FDR/Teddy) to scan tens of thousands of patterns in one pass over the input, instead of running each regex independently as PCRE2 does. Minimum requirement is SSSE3; it can additionally use SSE4.2, BMI/BMI2, POPCNT, and AVX2 if present, selected at compile time. Because matching is batched across the whole compiled pattern database, speedups scale with ruleset size: 1.8-2.3x over PCRE2 for single-pattern matching but 6.9-183x for multi-pattern (multi-mode) matching.

**Use it when:**
- Large multi-pattern rulesets (hundreds to tens of thousands of regexes) scanned against the same input stream, e.g. Snort/Suricata-style DPI
- x86-64 or 32-bit x86 targets with at least SSSE3; larger gains with AVX2 present
- Throughput-bound network/security scanning where the multi-mode win (6.9-183x over PCRE2) matters more than compile-step latency
- Streaming matching across TCP-like flows using block or streaming scan modes
- Workloads where a fast approximate prefilter match followed by a slower exact-match confirmation pass is acceptable

**Skip it when:**
- Single-pattern lookups, where the win over PCRE2 is a modest 1.8-2.3x and API complexity may not be worth it
- Patterns needing backreferences, capturing sub-expressions, atomic/possessive quantifiers, conditional patterns, or arbitrary zero-width assertions -- these are compile errors, not degraded matches
- Non-x86 targets: no upstream ARM/aarch64/PowerPC support (issues #187, #197 open since 2018-19 unresolved); use the community Vectorscan fork instead
- Latency-sensitive single-shot small scans where the separate pattern-database compile step doesn't amortize
- Streaming mode when block mode is possible -- docs note streaming carries extra overhead per record versus block

**Integration:** static lib | shared lib · CMake >=2.8.11, Ragel 6.9, Python 2.7, Boost >=1.57 (headers only), OpenSSL (required, used for HMAC-SHA256 database integrity); pcap optional, only for example code · C99 + C++11; GCC 4.8.1+, Clang 3.4+, Intel C++ Compiler 15+, or MSVC 2017 Build Tools · x86-64 and 32-bit x86 only; minimum SSSE3, optionally uses SSE4.2/BMI/BMI2/AVX2; no official ARM or PowerPC build

**Vs siblings:** no siblings catalogued yet

**Gotchas:**
- Backreferences, capturing groups, lookaround/zero-width assertions, atomic and possessive quantifiers, and conditional patterns fail to compile rather than silently degrading
- Prefiltering mode returns a superset of true matches and requires a second exact-match pass with another engine
- OpenSSL is a hard build dependency (used for database integrity hashing), not optional
- No official ARM/aarch64 build; long-open issues (#187, #197) point users to the community Vectorscan fork instead

**Status:** Actively maintained (last commit 2026-09-17) under BSD-3-Clause, used in production DPI stacks like Snort/Suricata; last tagged release is 5.4.2 (2023-04-19), and it is flagged 'copyable' usability in this catalog.

[repo](https://github.com/intel/hyperscan) · [benchmark](https://www.usenix.org/system/files/nsdi19-wang-xiang.pdf)

### runtime-and-systems

#### filesystems-and-io

##### liburing  `C`  `MIT OR LGPL-2.1-or-later`  `active`  `Tier B`

Userspace wrapper around Linux's io_uring ring-buffer syscall interface; beats libaio and POSIX-AIO on IOPS and syscall overhead.

**Beats:** libaio — ScyllaDB (independent third party) ran fio 1KB random reads across 4 files on an 8-CPU/NVMe box, 72 jobs, iodepth=8: direct I/O gave io_uring 1.42-1.49M IOPS vs libaio 1.32M (~7-12% faster) and sync read/write 814K (~1.7-1.8x); hot-cache buffered I/O gave io_uring 5.02M IOPS vs libaio 4.13M (~22% faster, where libaio degrades toward sync behavior). A separate single-CPU 512B test on Intel Optane showed io_uring at 346MB/s / 1,470us vs libaio 330MB/s / 1,549us (~5% faster). CPU model, kernel version, fio version and compiler flags are not stated on the page.

**How:** The submission and completion queues are ring buffers shared via mmap, so many I/O requests can be queued and many results reaped without a syscall per operation — io_uring_enter can submit a whole batch of SQEs and/or reap a batch of CQEs in one call. Optional SQPOLL mode runs a kernel-side thread that polls the SQ directly, letting the application skip io_uring_enter for submission entirely. This avoids POSIX-AIO's thread-pool dispatch overhead and cuts the per-op syscall count that libaio still pays for io_submit/io_getevents, which is what produces the reported IOPS gains (largest over POSIX-AIO, smaller over libaio).

**Use it when:**
- High-IOPS NVMe/direct-I/O or socket workloads on Linux 5.1+ where syscall count per operation matters (fio-style random read/write, proxies, storage engines).
- Workloads that naturally batch many concurrent I/Os per thread, so ring-based submit/reap amortizes across a batch.
- Need I/O opcodes beyond read/write/fsync — accept, connect, splice, openat, provided-buffer recv, etc. — from one interface.
- Willing to dedicate a kernel thread (SQPOLL) to shave submission syscalls for sustained high-throughput pipelines.
- Already a Linux-only codebase (QEMU, RocksDB, ScyllaDB/Seastar are existing adopters) where portability isn't a constraint.

**Skip it when:**
- Need portability off Linux, or must support pre-5.1 kernels / distros that disable io_uring by policy (some hardened container platforms, ChromeOS).
- Low-concurrency, latency-insensitive I/O where the ~7-12% direct-I/O / ~22% buffered-I/O gain over libaio doesn't justify the added ring-management complexity.
- Security-sensitive or multi-tenant environments wary of io_uring's kernel-side CVE history.
- Constrained memlocked rlimit environments (older kernels, small containers) where registering buffers or large rings can hit RLIMIT_MEMLOCK.
- Need to submit from multiple threads against a single ring without adding your own locking — concurrent unsynchronized submission isn't documented as safe.

**Integration:** shared lib · none beyond the Linux kernel UAPI headers · not documented precisely; GCC/Clang with GNU extensions (built with -D_GNU_SOURCE), built via ./configure && make · Linux only, kernel 5.1+ (more opcodes/features on newer kernels); dedicated syscall/lib.h for x86, x86-64, aarch64, riscv64, generic fallback elsewhere

**Vs siblings:** no siblings catalogued yet

**Gotchas:**
- fio's io_uring engine (engines/io_uring.c) issues raw io_uring_enter syscalls directly and does not link liburing — the ScyllaDB benchmark measures the kernel io_uring interface liburing wraps, not liburing's own call overhead.
- SQPOLL and registered buffers eat into RLIMIT_MEMLOCK; a low default (~64K) can silently cap ring/buffer registration on kernels <=5.11.
- One vendored kernel header ships GPL-with-Linux-syscall-note-exception rather than the LGPL/MIT dual license covering the rest of the repo.
- CQEs can complete out of submission order; correlate them via user_data, not position.

**Status:** Actively maintained (latest release 2.15 per liburing.spec, commits as recently as 2026-09-11); MIT/LGPL-2.1+ dual license (one GPL-with-syscall-note kernel header excepted) and small enough to vendor.

[repo](https://github.com/axboe/liburing) · [benchmark](https://www.scylladb.com/2020/05/05/how-io_uring-and-ebpf-will-revolutionize-programming-in-linux/)

### serialization-and-formats

#### json

##### simdjson  `C++`  `Apache-2.0 OR MIT`  `active`  `Tier A`

SIMD-accelerated JSON parser with full UTF-8 validation; ~4x faster than RapidJSON, ~25x than nlohmann.

**Beats:** RapidJSON — On GCC 10 -O3 on an unnamed 3.4 GHz Skylake chip, the README's rome.png chart (code in benchmark/) shows simdjson at roughly 2.2-3.2 GB/s against RapidJSON at roughly 0.4-0.5 GB/s. The peer-reviewed VLDB Journal 2019 paper pins the same comparison down with named hardware: on an Intel i7-6700 (Skylake) with GCC 9.1 -O3 -march=native, Table 10 shows simdjson parsing twitter.json at 2.2 GB/s vs RapidJSON at 0.45 GB/s (~4.9x) and RapidJSON insitu at 0.72 GB/s (~3.1x).

**How:** Uses SIMD vector instructions to find structural characters, string boundaries, and numbers in bulk rather than byte-by-byte, splitting parsing into index-building and interpretation stages. The On-Demand front-end skips materializing a full DOM/tape, lazily interpreting bytes only as the caller touches them so unused fields/subtrees cost nothing. A runtime CPU-dispatch layer selects among icelake (AVX-512), haswell (AVX2), westmere (SSE4.2), arm64 (NEON), ppc64 (VSX/AltiVec), lsx/lasx (LoongArch), or a generic 64-bit fallback kernel, so one compiled binary runs optimally across chips.

**Use it when:**
- Large or numerous real-world JSON payloads (twitter.json-scale and up) where RapidJSON/nlohmann parsing throughput is the bottleneck
- Single-pass extraction of a known set of fields, read in roughly document order (log/event pipelines, API response parsing)
- x86-64 (SSE4.2+) or aarch64 targets where a runtime-CPU-dispatching binary is acceptable
- NDJSON or streamed multi-document workloads via parse_many/iterate_many, optionally multithreaded
- Need strict RFC 8259 + full UTF-8 validation with no correctness shortcuts

**Skip it when:**
- Random, out-of-order, or repeated access to the same keys with On-Demand — raises OUT_OF_ORDER_ITERATION or falls back to a much slower path (Glaze's independent ABC test measured On-Demand at 89 MB/s vs 1163 MB/s in-order)
- You need a true drop-in replacement for RapidJSON's API — the iterator/On-Demand or DOM interface differs and calling code must change
- Non-standard or very old embedded targets without a >=4KB page size or a supported compiler (GCC 7.4+/Clang 6+/VS2017+)
- Float-heavy documents (e.g. GeoJSON) — decimal-to-binary float conversion caps throughput at a few hundred MB/s regardless of SIMD
- Chips below SSE4.2/NEON/VSX — falls back to the generic kernel and loses most of the speedup

**Integration:** source-drop · none for the core library at runtime (bundles Dragonbox for float serialization and a Boost-licensed string_view shim for pre-C++17 compilers); the benchmark suite alone depends on RapidJSON/nlohmann/sajson/yyjson/etc. · C++11 minimum (GNU GCC 7.4+, LLVM Clang 6+, Xcode 11+, Visual Studio 2017+); C++17 unlocks padded_input convenience; C++20 unlocks u8string_view/ranges; C++26 unlocks reflection-based (de)serialization · x86-64 (SSE4.2 'westmere' floor, AVX2 'haswell', AVX-512-VBMI2 'icelake' auto-selected at runtime), aarch64 (NEON), ppc64 (VSX/AltiVec, tested little-endian), LoongArch (LSX/LASX), plus a generic 64-bit fallback; also tested on big-endian s390x

**Vs siblings:** Pick simdjson over yyjson when you need the widest CPU/platform dispatch matrix (AVX-512 down through ARM/PPC/LoongArch) or the lazy On-Demand API for single-pass field extraction; yyjson's simpler in-situ DOM is easier to reason about and still beats RapidJSON by roughly 2x with less API surface. Pick simdjson over glaze when you can't build a static C++ struct/reflection schema for glaze to compile against, or don't want On-Demand's key-order sensitivity — glaze generates a schema-specific path and isn't subject to the same out-of-order penalty.

**Gotchas:**
- On-Demand documents must generally be walked forward, once, in roughly key order; re-reading a field or skipping around triggers OUT_OF_ORDER_ITERATION or a slow path
- Input must be a padded buffer (SIMDJSON_PADDING extra bytes); raw pointers/spans without padding aren't accepted directly (padded_string::load, the _padded literal, or padded_string_view handle this)
- Exceptions are thrown by default on parse errors; the no-exception API/build path must be opted into explicitly
- Debug builds can need hundreds of KB of stack; the README recommends turning on optimization or increasing stack size in threaded/limited-stack environments

**Status:** Actively maintained (last commit 2026-09-23, 24.3k stars, used in Node.js, ClickHouse, Meta Velox, Apache Doris, Milvus, StarRocks and others); dual Apache-2.0/MIT licensed and small enough to vendor as a two-file source drop.

[repo](https://github.com/simdjson/simdjson) · [benchmark](https://github.com/simdjson/simdjson#performance-results)

##### yyjson  `C`  `MIT`  `active`  `Tier A`

ANSI C JSON DOM library beating RapidJSON via single-file design, in-situ parsing, and low-allocation strategy.

**Beats:** RapidJSON — On AWS EC2 (AMD EPYC 7R32, gcc 9.3, CMake Release build i.e. -O3 -DNDEBUG plus -march=native) yyjson(insitu) parses twitter.json at 1.80 GB/s and stringifies at 1.51 GB/s versus RapidJSON(insitu) 0.77 GB/s parse and RapidJSON(utf8) 0.26/0.39 GB/s parse/stringify, roughly 2.3x-6.9x. On Apple A14 (clang 12) yyjson reaches 2.39-3.51 GB/s parse versus RapidJSON's 0.30-0.75 GB/s.

**How:** No explicit SIMD anywhere (ANSI C89 throughout); the README attributes speed instead to a modern-CPU-friendly code shape (high ILP, good branch prediction, tolerant of misaligned access) plus three concrete design choices visible in the docs: a single up-front memory allocation per document sized via yyjson_read_max_memory_usage rather than per-node mallocs, an optional in-situ reader (YYJSON_READ_INSITU) that parses strings in place inside the caller's buffer to skip copies, and a built-in fast float parse/print path that bypasses libc strtod/dtoa (toggle: YYJSON_DISABLE_FAST_FP_CONV). doc/Performance.md is a TODO stub, so no deeper algorithmic writeup exists in-repo.

**Use it when:**
- Parsing/serializing JSON in a C or C++ codebase where RapidJSON is the current baseline and a plain-C DOM API is acceptable
- Need strict int64/uint64/double round-trip fidelity and RFC 8259 conformance
- Want to vendor one header + one source file with no build system, on ANSI C89 for portability (CI covers x86/arm/ppc/riscv/s390x/wasm with gcc/clang/msvc/tcc/watcom)
- Can parse into a mutable buffer and use YYJSON_READ_INSITU to cut allocation/copy overhead
- Need JSON Pointer/Patch/Merge Patch or opt-in JSON5 leniency (comments, trailing commas) built in

**Skip it when:**
- Access pattern is index/key lookup-heavy rather than sequential iteration — arrays/objects use a linked-list-like structure (README Limitations)
- Need to mutate a document immediately after parsing — read results are immutable; requires yyjson_doc_mut_copy first
- simdjson's On-Demand API applies (most fields known at compile time) — README states it beats yyjson there; this benchmark only covers DOM-vs-DOM
- Cross-version ABI stability is required — 'Ensure ABI stability' is still an unchecked TODO in the README
- Building/mutating one yyjson_mut_doc from multiple threads — mutable types are documented not thread-safe

**Integration:** source-drop · none (ANSI C89, no explicit SIMD); optionally built as a static/shared lib via CMake · C89 (CI also builds under gcc, clang, msvc, tcc, watcom) · x86, arm, ppc, riscv, s390x, wasm per CI matrix; no SIMD/CPU-feature requirement

**Vs siblings:** Pick yyjson over simdjson when you want one portable ANSI C89 file with no SIMD/CPU-feature dependency and a DOM object you keep around (simdjson's DOM stringify trails at 0.61 vs yyjson's 1.51 GB/s on the EC2 table); pick simdjson instead when its On-Demand API fits or peak SIMD throughput outweighs portability. Pick yyjson over glaze when the codebase is C rather than C++, or you need a runtime dynamic DOM instead of glaze's reflection-based static-type serialization.

**Gotchas:**
- YYJSON_READ_INSITU requires a mutable, non-const buffer with extra padding bytes; passing a const string with this flag is a caller error
- Parsed (immutable) docs can be edited via yyjson_set_* functions, but the README calls this 'breaking the immutable convention' and says to only do it from a single thread
- Duplicate object keys are preserved, not deduped or rejected (README Limitations; issue #254 asking for a forbid-duplicates flag is still open)
- Calling setlocale() concurrently with parsing can corrupt float parsing if the platform isn't IEEE-754 or YYJSON_DISABLE_FAST_FP_CONV is set (falls back to strtod)

**Status:** Active: release 0.13.0 shipped 2026-09-08, same day as the latest commit; MIT-licensed, 3,883 stars, and trivial to vendor as one .h/.c pair.

[repo](https://github.com/ibireme/yyjson) · [benchmark](https://github.com/ibireme/yyjson#performance)

### stdlib-replacements

#### allocators

##### arena-allocator (yaroslavaristov)  `C++`  `MIT`  `active`  `Tier A`

Bump-pointer mmap arena for single-threaded HFT hot paths; O(1) allocate/reset, 10x-27x faster than malloc/free.

**Beats:** malloc/free (system C allocator; the benchmark calls malloc/free directly, not operator new/delete) — On AMD EPYC 7763 (GitHub Codespaces, g++-14, C++23, Release flags -O3 -march=native -funroll-loops -DNDEBUG) the arena beat sequential malloc/free by 10x-27x for N=1 to 1024 64-byte objects, and by 15x on a mixed 8/64/256-byte alloc-then-release batch. The same benchmark binary showed 32x-342x and 15x respectively on an Apple M1, but that run was under OrbStack virtualization, which the README itself flags as not native hardware.

**How:** It sidesteps the general-purpose allocator entirely: one mmap/mlock call reserves and pre-faults memory at construction, and allocate() does alignment and bounds checking with bitwise arithmetic on a raw pointer, no heap metadata, freelist, or locking involved. Bulk deallocation is a single pointer reset instead of N individual free() calls, so malloc's per-call bookkeeping and heap fragmentation (visible in the README's own numbers as N grows) never happen on the arena side.

**Use it when:**
- Single-threaded HFT-style hot path: allocate a batch of same-lifetime objects (the benchmarks cover 1-1024 objects, 8-256 bytes each) then discard them all together
- Latency-critical loop where malloc/free tail latency or heap fragmentation is the risk you're trying to eliminate
- A fixed, known-upfront capacity is acceptable and can be rounded up to a power of two
- Linux x86-64 or aarch64 with mmap/mlock available (and tolerance for a stderr warning if HugePages or mlock aren't permitted)
- Already on C++23 with GCC 14+ or Clang 17+, so the toolchain floor isn't a blocker

**Skip it when:**
- Need to free individual objects before the whole batch ends -- there is no per-object free, only bulk reset()
- Variable or unbounded total allocation size -- capacity is fixed at construction, must be a power of two, and allocate() silently returns nullptr on overflow (callers must check)
- Multi-threaded access to one arena instance -- the class docstring says 'Not thread-safe', no internal synchronization exists
- Need a vetted, general-purpose replacement for malloc/new across a codebase -- this is a single header from one contributor, 1 GitHub star, unaudited, merged in the last two months
- Portability across OSes matters -- Linux-only (mmap/mlock/MAP_HUGETLB), plus a C++23 + GCC14/Clang17 floor rules out older toolchains

**Integration:** header-only (include/arena.hpp) · none for the library; Google Benchmark is only a dependency of the benchmark target · C++23, GCC 14+ or Clang 17+ (README-stated requirement); CMakeLists.txt additionally hard-pins CMAKE_CXX_COMPILER to g++-14 · Linux only -- relies on mmap, mlock, and MAP_HUGETLB; no Windows or macOS support documented

**Vs siblings:** Pick this over metapool or the ShortAlloc-based arena-allocator when you specifically want an mmap+HugePage-backed arena with mlock'd pages for HFT-style latency floors and don't need per-object free. metapool and ShortAlloc both report much larger multiples on their own benchmarks (up to 1300x and up to 230x respectively), so this entry is not the fastest arena catalogued -- it's a smaller, simpler single-header alternative with a narrower feature set (no per-object free, no stack-allocated buffer option).

**Gotchas:**
- Capacity must be an exact power of two or the constructor throws std::invalid_argument
- allocate<T>() returns nullptr (not an exception) when the arena is exhausted -- callers must check the return value
- reset() invalidates every previously returned pointer at once; nothing tracks or flags which pointers are now dangling
- Header comment says 'Lock-free arena allocator' but the class docstring says 'Not thread-safe' -- treat it as strictly single-threaded, not lock-free-safe for concurrent use

**Status:** Actively maintained (last commit 2026-07-21), MIT-licensed and small enough to vendor as one header, but it is a 1-star, single-contributor, zero-open-issues project with no external audit or peer review.

[repo](https://github.com/yaroslavaristov/arena-allocator) · [benchmark](https://github.com/yaroslavaristov/arena-allocator#benchmark-results)

##### metapool  `C++`  `MIT`  `active`  `Tier A`

Header-only, TLS pool allocator with compile-time size classes; up to 1380x faster reserve() than std::vector, 3.6x vs pmr::vector.

**Beats:** std::allocator (via std::vector), std::pmr::unsynchronized_pool_resource — On an AMD Ryzen 7 PRO 8840U (Arch Linux, glibc 2.42/ptmalloc, clang 20.1.8, -O3 -march=native -fstrict-aliasing -flto), metapool's mtp::vault construction+reserve() beat std::vector (std::allocator/ptmalloc) by roughly 940x-1380x (one 4763x outlier) and beat std::pmr::vector (pmr pool resource + monotonic_buffer_resource) by 2.65x-3.63x in the reserve microbenchmark; in the more representative emplace_back benchmark the margin over std::vector was only 1.2x-1.6x, and a churn simulation ranged from 1.58x slower to 1.66x faster than std depending on element size.

**How:** Allocations are grouped into stride (size-class) segregated freelists, each an intrusive singly-linked list carved once from a monotonic arena, so alloc/free are O(1) pointer push/pop with a 2-byte inline per-block header for O(1) stride lookup on free. Instances are thread-local by default, so the hot path needs no locking or atomics (confirmed: no mutex/atomic in allocator.hpp, freelist.hpp, or memory_model.hpp). The arena is sized to fit L1/L2 cache and is grabbed once, avoiding the malloc/free syscalls and heap bookkeeping std::vector triggers on every reserve().

**Use it when:**
- Game/simulation-style workloads with known, stable allocation size distributions that can be pre-declared in a metaset
- Hot single-thread loops doing frequent same-size alloc/dealloc or reserve() cycles, where the TLS lock-free path beats malloc/free churn
- Codebases that can adopt the std::allocator or std::pmr::memory_resource adapter to plug metapool into existing containers without rewriting them
- Bounded working sets that fit a preallocated arena, where avoiding heap/kernel allocation variance matters (e.g. real-time frame loops)
- Projects already on a C++23-capable compiler (tested: clang 20.1.8) that are fine vendoring a header-only library

**Skip it when:**
- Allocation sizes are unpredictable or span a wide unbounded range: no fallback exists beyond the configured strides
- Multiple threads need to share one allocator instance concurrently: no mutex/atomic found in the reviewed source, so mtp::shared is not proven thread-safe without external locking
- You need organic growth past the compile-time arena: exhaustion calls a noreturn fatal() that terminates the process, and reset() invalidates all live objects without running destructors
- Toolchain is not C++23-capable, or you need verified GCC/MSVC/ARM support (only clang 20.1.8 on x86-64 is documented/tested)
- You're chasing the headline >1000x number: that figure is from a single-vector reserve()/destroy microbenchmark dominated by glibc malloc/free of large blocks; realistic emplace_back gains are only 1.2x-1.6x, and one churn case (4096B/16384B elements) is up to 1.58x slower than std

**Integration:** header-only · none · C++23; tested with clang 20.1.8 (no GCC/MSVC verification found) · x86-64 tested (AMD Ryzen 7 PRO 8840U, Arch Linux); no ARM/other-arch support documented in files reviewed

**Vs siblings:** All 10 catalogued siblings (NUMAlloc, SuperMalloc, Hoard, scalloc, both arena-allocators, ltalloc, rpmalloc, smmalloc, SpeedMalloc) are general-purpose malloc/operator-new replacements. metapool is the only one requiring compile-time, per-workload tuning of a fixed stride layout (metaset) instead of being a drop-in allocator — pick it when allocation sizes are known ahead of time and you want a header-only, TLS, lock-free pool packed into L1/L2 cache (e.g. a game engine's per-frame allocations); pick a general allocator like rpmalloc or smmalloc instead when sizes vary unpredictably or you need a true whole-app malloc replacement.

**Gotchas:**
- MTP_ASSERT (bounds/pointer sanity checks throughout the alloc/free path) compiles to a no-op under NDEBUG, so release builds skip these checks entirely
- Total freelist exhaustion across all strides calls a [[noreturn]] fatal() that prints a framed error to stderr and terminates the process — this is not a C++ exception and cannot be caught
- reset() (needed to reclaim arena space) invalidates all previously constructed objects without calling destructors
- Allocations round up to the nearest configured stride; a gap in the metaset (e.g. smallest stride 1024B for a 2B request) wastes the difference per block

**Status:** Active (last commit 2026-02-21), MIT-licensed, header-only and small enough to vendor; but a young single-author project (created Aug 2025, 37 stars, 3 forks, 0 open issues) with benchmark results published only as a PNG and no independent verification found.

[repo](https://github.com/esterlein/metapool) · [benchmark](https://github.com/esterlein/metapool#benchmark)

##### mimalloc  `C`  `MIT`  `active`  `Tier A`

General-purpose malloc drop-in replacement using sharded per-thread free lists; beats jemalloc/tcmalloc on multi-threaded workloads.

**Beats:** jemalloc — mimalloc's own README Performance section runs the public mimalloc-bench suite (glibc 2.31, GCC 9.3.0/Clang 10.0.0, on a 16-core AMD 5950x and a 36-core Xeon c5.18xlarge) and states in prose that mimalloc is 'more than 2.5x faster than jemalloc' (5.2.1) on sh6bench, 'quite a bit faster' than jemalloc/tcmalloc on larsonN, and 13% faster than tcmalloc (2.8.1) on the leanN Lean self-build workload.

**How:** Each ~64KiB 'mimalloc page' (one size class) uses free-list sharding, and within a page mimalloc keeps two lists per size class: a thread-local free list for same-thread frees and a separate lock-free 'remote free' list for cross-thread frees, so freeing from another thread is a single CAS with no coordination -- this is what wins on cross-thread-free benchmarks like larsonN and xmalloc-testN. It also does eager page purging (decommit/reset OS pages once a shard empties) to cut RSS, and v3 adds true first-class heaps that can allocate from any thread and be destroyed in bulk instead of freeing objects individually.

**Use it when:**
- Multi-threaded server workloads with producer/consumer or cross-thread free patterns (allocate on one thread, free on another)
- Want a small (~10k LOC), portable allocator to vendor/port to less-common platforms (Haiku, WASM, various BSDs, MUSL, riscV)
- Want built-in, production-usable overflow/double-free detection (guarded mode with sampling, or full secure mode) without swapping allocators for debug builds
- C++ code that can override global new/delete and wants first-class heaps for bulk-allocate/bulk-destroy object arenas
- Long-running services where reduced steady-state RSS from eager purge matters more than avoiding purge syscall overhead

**Skip it when:**
- Need mature allocation-profiling/heap-diff tooling; mimalloc offers stats/ETW/verbose output, not an equivalent to jemalloc's jeprof
- Single-threaded, allocation-light workloads (README's own cfrac/redis benchmarks show mimalloc roughly ties jemalloc/tcmalloc there)
- Code that forks() while using large/huge OS pages -- copy-on-write duplicates the whole 1GiB/2MiB page on first write post-fork, which can spike memory
- Statically overriding malloc in a codebase you don't fully control -- README warns mixing pointers across heaps can occur unless every source uses mimalloc-override.h
- Teams that specifically need decades of hardening at extreme single-vendor scale (e.g. Google-internal), where gperftools/Google TCMalloc has the longer track record

**Integration:** static lib | shared lib | source-drop (single src/static.c + mimalloc.o) · none (uses only mmap/VirtualAlloc) · CMake >=3.18 to build the library (CMAKE_C_STANDARD 11 / CXX_STANDARD 17 internally); consumers just need a C or C++ compiler and mimalloc.h · x86-64 (opts to -march=haswell/AVX2 by default), arm64 (armv8.1, armv8.3 on Apple silicon), riscV (rv64gcb_zacas); Windows (incl. ARM64EC, UWP, Xbox), Linux, macOS, various BSDs, Haiku, MUSL, WASM

**Vs siblings:** Pick mimalloc over jemalloc when you want a much smaller (~10k LOC), easily-vendored codebase with broader OS/arch ports (Haiku, WASM, BSD, MUSL, riscV) and built-in guard-page/secure modes, at the cost of jemalloc's more mature profiling tooling. Pick it over snmalloc when you need that platform breadth more than snmalloc's extreme many-thread producer/consumer throughput, and over gperftools/Google TCMalloc when first-class heaps and lower baseline memory overhead matter more than TCMalloc's longer production track record at large single-vendor scale.

**Gotchas:**
- Static override via mimalloc-override.h only works reliably if ALL sources in the program are rebuilt with it; otherwise pointers from different heaps can mix and corrupt memory
- mimalloc-new-delete.h (C++ new/delete override) must be included in exactly one source file, not every file
- -DMI_SECURE=FULL (guard page after every 64KiB page) is explicitly 'not recommended in general' -- costs more and can hit Linux's max VMA count on large heaps
- Large/huge OS pages plus fork(): copy-on-write duplicates the entire 1GiB/2MiB page on first write in the child, which can balloon memory use

**Status:** Actively maintained: latest release v3.5.3 on 2026-09-16 with commits through 2026-09-17; MIT licensed and small enough to vendor as a single source file (src/static.c), consistent with its 'copyable' usability rating.

[repo](https://github.com/microsoft/mimalloc) · [benchmark](https://github.com/microsoft/mimalloc#performance)

##### SuperMalloc  `C++`  `MIT OR GPL-3.0-or-later`  `abandoned`  `Tier A`

Research malloc(3) replacement using 2MiB virtual-memory superblocks and optional Haswell HTM; beats DLmalloc/JEmalloc/Hoard/TBBmalloc.

**Beats:** best of DLmalloc, JEmalloc, Hoard, and TBBmalloc — On the author's malloc-test multithreaded allocate/free microbenchmark (ISMM'15 paper, gcc 4.8.3 -O3 -flto on Fedora 20/glibc 2.18), SuperMalloc reached ~2.1x the throughput of the best of DLmalloc 2.8.6, JEmalloc 3.6.0, Hoard 3.10, and TBBmalloc tbb43_20140724 at 1 thread; 2.75x at 8 threads using Haswell HTM on a Core i7-4770; and 3.4x at 32 threads without HTM on a 2-socket Xeon E5-2665.

**How:** Objects are allocated from 2MiB chunks that each hold one size class; chunk-number-to-metadata lookup uses a big mostly-uncommitted array instead of a tree, and most size classes use a prime number of cache lines (plus random alignment for large objects) to avoid cache associativity conflicts. Allocation/free paths use a 3-level cache (10-object per-thread cache, a per-CPU cache sized to roughly one L2's worth of objects per size class, and a global cache), with objects moved between levels in O(1) via array/bitmap operations. Everything a critical section needs is prefetched beforehand so the section itself is short, which speeds ordinary locking and raises the commit rate of the RTM hardware-transaction path.

**Use it when:**
- Reproducing or extending the ISMM'15 malloc-test throughput results on period-matched hardware/toolchain (Haswell+ with TSX, gcc 4.8.3-class compiler)
- Research into HTM-assisted allocator design or virtual-address-space-heavy (superblock/chunk) allocator layouts
- Workloads shaped like malloc-test: many threads doing tight fixed-size-class allocate/free cycles
- Willing to vendor and patch a ~2015-era C++11 source drop (dual MIT/GPLv3) instead of taking a maintained package
- Have access to Haswell+ HTM for the full-speed build, or accept the pthread-lock fallback build otherwise

**Skip it when:**
- Need an actively maintained allocator: last commit 2017-10-25, no response to open issues since
- Need production reliability: open/closed issues report crashes under mysql and sysbench, and 'make check results in Aborted (core dumped)' on some setups
- Need 8-byte-aligned allocation support: issue #36 requesting that mode is still open, i.e. unimplemented
- No Haswell+ TSX hardware and don't want to fall back to the slower pthread-mutex build
- Need current comparisons: no head-to-head vs mimalloc/snmalloc/rpmalloc exists, only vs 2014-era DLmalloc 2.8.6/Hoard 3.10/JEmalloc 3.6.0/TBBmalloc tbb43
- Virtual address space is constrained: allocates 2MiB chunks per size class rather than tightly packing

**Integration:** source-drop · none beyond libc/libdl (-ldl); vendored copies of Hoard/jemalloc/tbb exist only under other-mallocs/ for building benchmark comparisons, not for SuperMalloc itself · C++11 (-std=c++11) / C11; needs GCC with LTO (release build uses -O3 -flto); a Makefile comment notes it does not compile with gcc 4.8.0 · 64-bit Linux, x86-64 only; the RTM/HTM build additionally needs a Haswell+ CPU with TSX, otherwise use the libsupermalloc_pthread.so build

**Vs siblings:** Pick SuperMalloc over the sibling allocators (NUMAlloc, Hoard, scalloc, arena/pool allocators) when the question is specifically HTM-assisted allocator design validated by an A-tier paper benchmark against DLmalloc/JEmalloc/Hoard/TBBmalloc — not for production use, where NUMAlloc (maintained, benchmarked vs glibc 2.28 and mimalloc) or Hoard (still maintained) are safer choices.

**Gotchas:**
- Two separate shared libraries ship (HTM vs pthread); the README says a runtime auto-detect was 'planned' but was never added, so you must pick the right one yourself
- Runtime behavior is gated by undocumented env vars (SUPERMALLOC_THREADCACHE, SUPERMALLOC_TRANSACTIONS, SUPERMALLOC_PREDO) used throughout the benchmark Makefiles
- Reported crashes against real workloads: mysql (issue #23) and sysbench (issue #33)
- 8-byte-aligned allocation is requested but not implemented (issue #36, open)

**Status:** Abandoned: last commit 2017-10-25 with 20 open issues including build failures on CentOS 6.5 and lto1 errors; dual MIT/GPLv3-licensed C++11 source is small enough to vendor but expect to patch around a 2015-era toolchain assumption.

[repo](https://github.com/kuszmaul/SuperMalloc) · [benchmark](https://raw.githubusercontent.com/kuszmaul/SuperMalloc/master/paper/ismm15/supermalloc.tex)

##### Hoard  `C++`  `Apache-2.0`  `active`  `Tier B`

Drop-in multithreaded malloc replacement beating Solaris/Ptmalloc via per-processor heaps and bounded blowup.

**Beats:** Solaris default allocator, Ptmalloc (glibc malloc backing operator new/delete) — The ASPLOS 2000 paper (14x400MHz UltraSPARC Sun Enterprise 5000, Solaris 7, GNU C++ -O6) measured up to 60x over the Solaris default allocator and up to 18x over Ptmalloc at 14 processors on Larson, with threadtest 278% and shbench 85% faster than Ptmalloc at 14p, but a 6.2% average uniprocessor slowdown versus Solaris. The current README adds unreviewed first-party benchmarks on a 192-core 2-node AMD EPYC system claiming 1.3-1.5x higher Larson throughput than glibc/mimalloc/jemalloc and 1.6x over glibc at 128 threads on NUMA, while conceding jemalloc wins the linux-scalability workload.

**How:** Per-processor heaps plus a global heap reduce lock contention, with objects grouped into size-class "superblocks" that move between per-thread and global heaps to keep memory use provably bounded rather than growing per-CPU. Thread-local allocation buffers (TLAB, see hoardtlab.h/percputlab.h) give a lock-free fast path, and a remote-free queue (remotefreequeue.h) lets a thread free memory another thread allocated without a global lock. Superblocks are cache-line aligned to avoid false sharing, and the spinlock (futexlock.h) uses PAUSE/YIELD exponential backoff.

**Use it when:**
- Multithreaded server-style workloads with many short-lived allocations and cross-thread object passing (Larson-style)
- Multi-socket NUMA machines, where README claims up to 1.6x over glibc at 128 threads
- Realloc-heavy workloads (repeated grow/shrink), where README claims 2-5x over other allocators
- Programs suffering false sharing or heap contention from the default allocator on multiprocessor hardware
- Deployments wanting a mature (25+ yr), Apache-2.0, provably-bounded-blowup allocator rather than a newer research allocator

**Skip it when:**
- Single-threaded/uniprocessor programs — the original ASPLOS paper measured Hoard averaging 6.2% slower than the Solaris allocator uniprocessor (shbench +49.2% runtime, Ghostscript +10.6% runtime)
- Very high pure malloc/free-pair throughput with no work between calls (linux-scalability benchmark) — current README concedes jemalloc wins this workload
- Windows binaries statically linking the CRT (/MT) — Hoard cannot intercept allocation calls embedded in the executable, only /MD dynamic-CRT builds
- Code wanting a std::allocator-compatible template to plug into individual STL containers — Hoard replaces malloc/new globally, not per-container
- Extreme thread counts (256+) where README shows Hoard only matching mimalloc rather than leading

**Integration:** shared lib · none at runtime beyond libc; build fetches Heap-Layers, printf (allocation-free printf), and alloc8 (interposition library) via CMake FetchContent · CMake 3.15+; targets C++23 but CMAKE_CXX_STANDARD_REQUIRED is OFF; Linux needs libstdc++-dev installed · Linux, macOS (Intel + Apple Silicon arm64/arm64e), Windows (x86, x64, ARM, ARM64 via Microsoft Detours)

**Vs siblings:** Pick Hoard over NUMAlloc/scalloc when you want a long-deployed (AOL/Cisco/SAP-era), Apache-2.0, SPEC CPU2006-standard allocator with a proven bounded-blowup guarantee rather than a newer research allocator. SuperMalloc's own README claims to beat the best of DLmalloc/JEmalloc/Hoard/TBBmalloc outright, so prefer SuperMalloc if squeezing out more raw throughput matters more than Hoard's maturity and simpler (non-HTM) build.

**Gotchas:**
- Windows apps must be built with /MD; /MT static-CRT binaries embed their own allocator and Hoard can't hook them
- Historical Windows crashes from CRT/DLL interop (e.g. _onexit shimming, ucrtbase heap corruption) took years to fully resolve per issue #51; worth checking current behavior on your exact Windows/CRT version
- Multi-heap design bounds memory blowup mathematically but does not eliminate it — expect some extra memory versus a single-heap allocator in exchange for scalability
- linux-scalability (pure malloc/free pairs, no intervening work) is explicitly called out in the README as adversarial to Hoard's superblock design

**Status:** Actively maintained (last commit 2026-07-19, open PR/issue #84 adding hot-path optimizations); Apache-2.0 and a simple drop-in library, so easy to vendor or pin even if development slowed.

[repo](https://github.com/emeryberger/Hoard) · [benchmark](http://www.cs.utexas.edu/users/mckinley/papers/asplos-2000.pdf)

##### scalloc  `C++`  `BSD-2-Clause`  `stale`  `Tier B`

Multicore-scalable, low-fragmentation malloc replacement beating ptmalloc2; drop-in via LD_PRELOAD, rewritten since its OOPSLA'15 paper.

**Beats:** ptmalloc2 (glibc's default malloc, part of GNU libc; extends Doug Lea's dlmalloc) — The OOPSLA'15 paper (arXiv v2, Aug 2015) reports scalloc at roughly a 1.28x SPEC ratio vs ptmalloc2 on single-threaded SPEC CPU2006 483.xalancbmk (read off a Figure 5 bar, no printed number, no compiler/flags stated), measured on 4x 10-core Xeon E7-4850 with 128GB RAM; it separately claims scalloc beats TBB's average multithreaded throughput while using less memory across threadtest/shbench/larson/ACDC.

**How:** Uses 'virtual spans' (2MiB-aligned regions, kVirtualSpanShift=21) to treat small and large objects uniformly instead of separate size-class machinery. Per-thread local allocation buffers (LABs) handle the fast path, while a scalable global span pool reclaims and redistributes spans across cores. Allocation/deallocation are constant-time modulo synchronization, trading memory reuse against spatial locality to avoid false sharing.

**Use it when:**
- Multithreaded, allocation-heavy C/C++ workloads on Linux or OSX x86 where you want a drop-in swap without recompiling (LD_PRELOAD/DYLD_INSERT_LIBRARIES)
- Producer-consumer or varying-object-size workloads whose object sizes fit within 2MiB virtual spans
- You can tune the environment (overcommit accounting, transparent huge pages) for correct/best behavior
- Memory footprint under concurrency matters as much as raw throughput (paper claims lower memory than TBB at comparable/better speed)
- You're willing to re-benchmark on current hardware and current allocator code rather than trust the 2015 numbers

**Skip it when:**
- Windows: unsupported (override.h explicitly #errors on non-Linux/non-Apple)
- Build is gyp-based and broken on modern Python (open, unanswered GitHub issue #1, 'Switch to a supported build system')
- Single-threaded throughput vs ptmalloc2 is the goal: the paper's own numbers put scalloc mid-pack (~1.28x), behind TCMalloc/llalloc/TBB/SuperMalloc
- Address-space-constrained or containerized environments: reserves up to 32TB of virtual space per arena, which can hit mmap/overcommit limits
- Project is stale with a single unresolved open issue; README itself says the allocator was 'completely rewritten from scratch' since the benchmarked paper version, so published speedup numbers may not reflect current code

**Integration:** shared lib (built with gyp+make; loaded via LD_PRELOAD/DYLD_INSERT_LIBRARIES) · gyp (build-time only, fetched via tools/make_deps.sh); no runtime dependencies documented · not documented (no C++ standard stated); build needs Python for gyp, which is currently broken per open issue #1 · Linux and OSX (>10.6); README's design assumes 64-bit address space; no Windows (override.h errors on any other OS)

**Vs siblings:** Pick scalloc over SuperMalloc/NUMAlloc/Hoard only when you specifically want its virtual-span design for producer-consumer or mixed-size multithreaded workloads with lower memory use than TBB; for single-threaded throughput vs ptmalloc2, SuperMalloc and TCMalloc beat scalloc in its own paper's numbers, and SuperMalloc/NUMAlloc have more recent or broader comparative benchmarks.

**Gotchas:**
- gyp build is broken on modern Python versions; open issue #1 (filed 2025-06-02) is unresolved
- Needs vm.overcommit_memory=1 and transparent huge pages disabled on Linux for correct/best operation
- Reserves up to 32TB of virtual address space per arena; relies on on-demand paging/madvise to keep physical memory low
- OSX preload needs DYLD_FORCE_FLAT_NAMESPACE=1 in addition to DYLD_INSERT_LIBRARIES

**Status:** maintenance_status is stale and the BSD-2-Clause license makes it easy to vendor, but the gyp build is broken on current Python (open issue #1, unresolved) and the README itself says to re-benchmark since a full rewrite post-paper.

[repo](https://github.com/cksystemsgroup/scalloc) · [benchmark](https://arxiv.org/pdf/1503.09006)

##### snmalloc  `C++`  `MIT`  `active`  `Tier B`

Header-only C++ allocator using lock-free message-passing frees, beating glibc malloc on cross-thread and batch-deallocation workloads.

**Beats:** glibc malloc — ISMM 2019 paper, producer/consumer malloc-test thread sweep (64 threads, Ubuntu 18.04 on an Azure F64s_v2 VM, 64 vCPUs, dual-socket Xeon Platinum 8168, 128 GB RAM): snmalloc reaches roughly 190-220M allocs/sec versus glibc ptmalloc2's ~47M (~4x, read off chart data). On the symmetric same-thread workload the gap narrows to ~1.7x and jemalloc/tcmalloc/SuperMalloc beat snmalloc outright. No compiler or flags are given, which caps this at evidence tier B.

**How:** Frees on the allocating thread take no lock and no atomic operation. Frees from a different thread go through a lock-free message-passing scheme that batches remote deallocations and returns them to the owner with a single atomic operation instead of one per free, so throughput scales with core count. Large page ranges (superslabs) amortize metadata bookkeeping, and the malloc/free fast path is two branches under Clang on Linux.

**Use it when:**
- Multi-threaded C/C++ services with heavy cross-thread free (producer/consumer queues, thread pools, work-stealing schedulers).
- Workloads with bursty batch deallocation (freeing thousands of objects at once) that stall thread-caching allocators.
- Need a glibc- or jemalloc-API-compatible drop-in on Linux/BSD via LD_PRELOAD or static link.
- Rust services wanting the same allocator via the snmalloc-rs crate.
- Security-conscious C++ services that can absorb <5% overhead for the hardened build (guard pages, freelist-corruption checks, randomization).

**Skip it when:**
- Single-threaded or same-thread-dominated allocation patterns: the paper's own symmetric-workload chart (Fig 4) shows jemalloc, tcmalloc and SuperMalloc ahead of snmalloc there.
- OpenBSD: BUILDING.md lists it as a supported PAL, but issue #594 (open since 2023, still unresolved as of a Sept 2025 comment) says pagemap init fails because OpenBSD has no overcommit.
- NetBSD without a libatomic implementation or without Clang, since the default NetBSD toolchain emits libatomic calls snmalloc needs.
- Building with GCC — the project itself calls this 'not recommended' due to extra libatomic calls for 128-bit atomics.
- Long-running processes with certain shapes: open issues report committed-memory growth over time (#814, #846) and slab thrashing for transient large-object alloc/dealloc pairs (#811), unresolved as of Sept 2026.

**Integration:** header-only (also static/shared lib via CMake) · none at runtime; build needs CMake 3.21+ and Ninja · C++17 minimum (SNMALLOC_USE_CXX17 flag for legacy support); default build and PAL concept checks assume C++20; Clang 6.0+ recommended · Linux, macOS/iOS (XNU), Windows (Visual Studio 2019+/clang-cl), FreeBSD, NetBSD, Android out of the box; x86-64/ARM/PowerPC/RISC-V/SPARC plus experimental CHERI; OpenBSD is listed but currently broken (issue #594)

**Vs siblings:** Pick snmalloc over mimalloc/jemalloc/TCMalloc when the workload is dominated by cross-thread free or bursty batch deallocation — that's the specific case its message-passing remote-free design targets. The paper itself shows jemalloc and tcmalloc ahead of snmalloc on same-thread alloc/free, so prefer one of those siblings when allocation and deallocation mostly happen on the same thread.

**Gotchas:**
- Remote deallocation batches into a default 1 MiB outgoing buffer before memory returns to the owning thread — tunable, trades some memory for throughput.
- Hardened build (libsnmalloc-checks.so) adds guard pages, freelist-corruption checks and randomization; measured at <5% overhead on mimalloc-bench on a 72-core Azure VM, but it's a separate opt-in build, not the default.
- Metadata layout has changed significantly since the 2019 ISMM paper (per the README's own admission), so current performance and internals differ from what's described in snmalloc.pdf.
- RISC-V Linux: flat pagemap reservation is reported oversized on Sv39 (issue #861, open).

**Status:** Actively maintained — commits as recent as 2026-09-21 and 53 open issues being triaged; MIT-licensed and header-only so it vendors easily, but its internals have diverged substantially from the 2019 paper the headline numbers come from.

[repo](https://github.com/microsoft/snmalloc) · [benchmark](https://github.com/microsoft/snmalloc/blob/main/snmalloc.pdf)

#### async-tasks-threadpools

##### Boost.Fiber  `C++`  `BSL-1.0`  `active`  `Tier A`

Cooperative user-space fibers with a std::thread-like API, spawning and context-switching orders of magnitude cheaper than std::thread/std::async.

**Beats:** std::thread, std::async — On gcc-6.3.1 (variant=release, optimization=speed), dual Xeon E5-2620v4 (16C/32T), Linux x86_64, Boost's ported skynet microbenchmark (1,000,000 spawned actors; 10,000 for std::thread/std::async, which exhausted OS resources beyond that) measured std::thread at 52-73 us/unit and std::async at 106-122 us/unit versus Boost.Fiber at 0.05-0.09 us/unit with a work-stealing scheduler and tcmalloc (1.69-1.79 us/unit single-threaded round-robin).

**How:** Fiber creation and context switching save/restore registers and swap the stack pointer entirely in user space via Boost.Context primitives, skipping the kernel thread-creation syscall and stack guard-page setup that std::thread/std::async pay for. The fastest measurements add a work-stealing scheduler with per-thread local run queues (stealing idle fibers from other threads) plus tcmalloc in place of glibc's allocator to cut malloc contention under the skynet microbenchmark's million spawns.

**Use it when:**
- Spawning very large numbers of short-lived concurrent tasks (100k-1M+) where std::thread/std::async hit OS resource exhaustion
- Latency-sensitive, switch-heavy workloads where sub-microsecond task handoffs matter more than raw parallel throughput
- Existing Boost.Asio async I/O code that wants synchronous-looking control flow (fiber + yield) instead of callback chains
- Multi-core scaling via boost::fibers::algo::work_stealing across worker threads on many-core hardware (benchmarked on 16C/32T)
- Projects already on Boost (BSL-1.0, C++11+) that can add a compiled Boost library dependency

**Skip it when:**
- Code with blocking syscalls (file I/O, blocking sockets) not routed through the fiber-aware scheduler/Asio integration — one blocking call stalls every fiber on that thread
- CPU-bound fibers that never yield: there is no preemption, so they starve sibling fibers on the same thread
- Teams wanting a mechanical std::thread/std::async replacement — fiber is a different type with different join/sync semantics; call sites must be rewritten
- Toolchains that can't take a compiled (non-header-only) Boost dependency, or predate C++11
- Treating the >500x headline ratio as current: it's from gcc-6.3.1 (~2017) hardware/compiler, with tcmalloc required and no republished numbers on modern toolchains

**Integration:** static lib | shared lib · Boost.Context (stack switching), Boost.Config, Boost.Assert, Boost.IntrusivePtr, Boost.Predef; optional Boost.Asio for async I/O integration · C++11 minimum (README: "Boost.fiber requires C++11!"); benchmark used gcc-6.3.1 · x86-64 Linux is the only platform verified this session (benchmark hardware); broader OS/arch support rides on Boost.Context but was not independently confirmed

**Vs siblings:** The sibling entries (dispenso, TooManyCooks, utl::parallel, Taskflow, libfork, meet1214/thread-pool, BS::thread_pool) are all task/thread-pool schedulers for CPU-bound work units. Pick Boost.Fiber instead when you need actual blocking-style semantics — mutex, condition_variable, future.get() — that suspend only the calling task, e.g. porting synchronous networking or actor-style code to run as massed lightweight tasks, not a parallel-for or task graph.

**Gotchas:**
- Cooperative model: fibers must yield/block through the library's own API (or Asio's fiber-aware yield in examples/asio/round_robin.hpp); a raw blocking syscall stalls the whole underlying thread
- Stack allocator choice (fixedsize_stack vs segmented_stack) affects both speed and memory footprint; the headline numbers used fixedsize_stack
- BOOST_FIBERS_NO_ATOMICS disables inter-thread fiber synchronization entirely and has a confusing open compile-error report (issue #285, open since 2021)
- The fiber-side benchmark numbers are tcmalloc-only; the doc doesn't state whether the std::thread/std::async rows used the same allocator, so the comparison isn't fully allocator-matched

**Status:** Actively maintained as part of Boost (last commit 2026-06-15), BSL-1.0 licensed and freely copyable; the performance numbers themselves date to gcc-6.3.1 (~2017) and the docs give no indication they were re-run on a modern toolchain.

[repo](https://github.com/boostorg/fiber) · [benchmark](https://github.com/boostorg/fiber/blob/master/doc/performance.qbk)

##### dispenso  `C++`  `MIT`  `active`  `Tier A`

Meta's work-stealing C++ thread pool and parallel-algorithms library, faster than oneTBB on small/medium parallel-for loops.

**Beats:** oneTBB (Intel Threading Building Blocks) — On Meta's public benchmark dashboard (GNU 11.5.0, C++20, CMake Release build, AMD EPYC-Genoa host: 166 cores, 224GB RAM, Linux 6.16.1, TBB 2023.1.0), the summing_for microbenchmark shows dispenso::parallel_for beating tbb::parallel_for at low-to-mid thread counts: 1.61x at 1M elements/1 thread (279us vs 450us), 3.48x at 1M elements/8 threads (50.6us vs 175.8us), and 1.53x at 100M elements/16 threads (2.27ms vs 3.47ms). I independently pulled results/linux_x64.json from the repo and confirmed its machine_info block (compiler, standard, build type, CPU, core count) matches the record exactly. The same sweep also has TBB ahead at 128+ threads and at several low-thread 100M-element points, so the claimed numbers are favorable picks from a mixed comparison, not a uniform win.

**How:** A work-stealing ThreadPool underlies all scheduling; parallel_for supports static (equal up-front chunking, lowest overhead) or adaptive (stripe-based work-stealing that prefers same-L3-cache victims) chunking, tuned via minItemsPerChunk. Cascading parallel_for lets independent loops share the pool without oversubscription, which the project reports as a 32-50% win over TBB in production after porting. Lock-free primitives (a ChaseLevDeque work-stealing deque, MPMC/SPSC ring buffers, a bundled moodycamel::ConcurrentQueue) back the scheduler and containers with low per-task overhead.

**Use it when:**
- Nested or many independent parallel_for calls that would oversubscribe threads under TBB/OpenMP
- Need thread-safe shared futures with then()/when_all()/when_any(), which TBB lacks
- Need ASAN/TSAN-clean concurrent C++ (TBB is not sanitizer-friendly)
- Small-to-medium parallel-for workloads at low-to-mid thread counts, where the project's own EPYC-Genoa benchmark shows 1.5-3.5x over tbb::parallel_for
- Codebase pinned to a C++14 baseline that still wants a modern TBB/OpenMP alternative

**Skip it when:**
- Very high thread counts on large cores: on the project's own 166-core EPYC data, TBB is faster at 128 and 166 threads for the 1M-element case, and at 1-4 and 32 threads for the 100M-element case
- I/O-bound workloads — the FAQ explicitly says pool threads that block on I/O waste scheduling capacity and points to Folly instead
- Need OpenMP-style '#pragma omp reduction' syntax — dispenso has no first-class reduction API, only manual per-thread accumulation
- Need GPU/CUDA task graphs — TaskFlow supports CUDA graph mapping, dispenso does not
- macOS builds needing explicit CPU-pinning — CpuSet::bindCurrentThread() is a documented no-op there

**Integration:** static lib | shared lib · moodycamel::concurrentqueue (bundled by default under dispenso/third-party, or an installed copy via -DDISPENSO_USE_SYSTEM_CONCURRENTQUEUE=ON) · C++14 (default, fully supported); C++17/C++20 swap in std facilities and add concept constraints but change no behavior; CMake 3.12+ · Linux x86-64/ARM64, macOS x86-64/ARM64, Windows x86-64/ARM64, FreeBSD (full); Android ARM64 (partial CPU-affinity/topology)

**Vs siblings:** Versus other oneTBB-beating siblings here (TooManyCooks, libfork, Taskflow — all coroutine/C++20-leaning with bigger peak ratios in their own benchmarks), pick dispenso when you need a C++14-compatible, sanitizer-clean, explicitly-controlled thread pool rather than a coroutine scheduler, or when your workload is many independent/nested parallel_for loops where dispenso's cascading scheduling avoids oversubscription. Versus the std::thread/std::async-only siblings (Boost.Fiber, utl::parallel, BS::thread_pool, meet1214/thread-pool), dispenso is the pick when your actual incumbent is TBB or OpenMP rather than bare std primitives.

**Gotchas:**
- Exceptions thrown inside parallel_for/TaskSet lambdas are captured, not propagated immediately; the first one rethrows only when wait() runs (or the TaskSet destructor), and other in-flight tasks keep running
- Builds with -fno-exceptions call abort() instead of throwing
- moodycamel::ConcurrentQueue is a by-value member of ThreadPool, so it's part of dispenso's ABI — building the library against one concurrentqueue version while a consumer compiles against another is an undiagnosed ODR violation
- DISPENSO_SHARED_LIB defaults to ON, so a static build has to be requested explicitly

**Status:** Actively maintained by Meta (last commit 2026-09-02, current release v1.6.2, packaged for Conan/vcpkg/Homebrew/conda-forge/Fedora); MIT-licensed and small enough to vendor, but it is a built static/shared CMake library rather than header-only, with one bundled MIT/BSD-compatible dependency (moodycamel::concurrentqueue).

[repo](https://github.com/facebookincubator/dispenso) · [benchmark](https://facebookincubator.github.io/dispenso/benchmarks/)

##### TooManyCooks (TMC)  `C++`  `BSL-1.0`  `active`  `Tier A`

Header-only C++20 coroutine thread pool with continuation-stealing scheduling; 1.1-3.8x faster than oneTBB on fork-join workloads.

**Beats:** oneTBB (Intel/uxlfoundation Threading Building Blocks) — On a 64-core/64-thread AMD EPYC 7742 (Debian 13, Clang 21.1.7, -O3 -march=native, linked against libtcmalloc), TMC beat oneTBB by 3.77x on the skynet 100M-task benchmark (37,949us vs 142,887us), 1.79x on nqueens, 2.49x on fib(39), and 1.12x on matmul(2048), per the tzcnt/runtime-benchmarks suite that is maintained by TMC's own author but publishes reproducible code, compiler flags, and hardware specs.

**How:** Each worker owns a Chase-Lev lock-free work-stealing deque (own thread pushes/pops the tail, other threads steal from the head, buffer doubles on growth); when a coroutine's continuation is ready, the same worker keeps running it instead of handing back to a generic scheduler loop (continuation-stealing), avoiding round-trips through a central queue. Per-thread inboxes and a priority-bitmap scheduler reduce contention for load balancing, and hwloc integration lets thread placement follow real cache/NUMA topology on many-core servers.

**Use it when:**
- Recursive fork-join / divide-and-conquer workloads (skynet, nqueens, fib-style forking) on many-core machines (32-64+ threads) where oneTBB's per-task overhead dominates
- Codebase can standardize on C++20 coroutines and Clang 17+ (or GCC 14+ on Linux) for best codegen
- Need integrated async I/O (sockets, files, timers via Asio) alongside CPU task scheduling, not just a bare thread pool
- Want NUMA/topology-aware thread placement via hwloc on large multi-socket or many-core servers
- Fine vendoring a header-only library instead of linking a prebuilt TBB installation

**Skip it when:**
- Any code path that must build with MSVC: unsupported due to a documented compiler bug causing release-mode miscompilation (may run in Debug, crashes in Release)
- Workload is closer to matmul(2048)-style compute-bound with little forking, where the margin over oneTBB drops to ~1.1x - not worth an API rewrite
- Team can't or won't move to C++20 coroutines, or needs a signature-compatible replacement for std::async/std::thread
- Chasing best-in-class results specifically on this benchmark suite: citor (1.06x mean-ratio-to-best) and libfork (1.18x) beat TMC (1.32x) on the same four workloads
- Risk-averse on maturity: 281 stars, and a channel hazard-pointer crash was reported and only worked around (not code-fixed) as of August 2026

**Integration:** header-only · hwloc (optional, required by default in the CMake target; disable with TMC_USE_HWLOC=OFF); Asio or Boost.Asio (only needed for the tmc/asio/* network/file I/O headers) · C++20 coroutines; Linux: Clang 17+ (recommended) or GCC 14+, kernel 5.16+ for futex_waitv; Windows: clang-cl 17+ (MSVC unsupported); macOS: Apple Clang 17+ with -fexperimental-library · x86 (32/64-bit), AArch64, LoongArch LA64, riscv64

**Vs siblings:** Pick TMC over dispenso or Taskflow when the workload is naturally coroutine-shaped (co_await-driven recursive fork-join) and you also want built-in async I/O in the same runtime; libfork slightly beats TMC on this exact benchmark suite's mean ratio (1.18x vs 1.32x) if you don't need channels/Asio integration, so prefer libfork for pure recursive-task speed and TMC when the fuller feature set (channels, priorities, I/O) matters more than the last ~10% of throughput.

**Gotchas:**
- Per the project's own version notes, minor version bumps (not just majors) may include breaking API changes - pin a version rather than tracking main
- channel.hpp hazard-pointer issue reported in issue #275 (Aug 2026): reusing or sharing a single chan_tok across tasks/threads caused intermittent crashes; the maintainer's fix is disciplined per-task token copies, not a code patch, and a separate stale-hazard-pointer soundness edge case (extremely long token idle time) is acknowledged as theoretically possible but undocumented
- hwloc is a required dependency by default under the CMake target; must explicitly pass TMC_USE_HWLOC=OFF to drop it
- MSVC builds can appear to work in Debug but crash in Release due to a compiler thread_local-caching bug - do not rely on MSVC even for prototyping

**Status:** Actively maintained (commit as recent as 2026-09-22, currently v1.7.0) and BSL-1.0 licensed with Conan/vcpkg packaging, but still young (281 stars) - a channel hazard-pointer crash was still being triaged via GitHub issue as recently as August 2026, and the header-only form makes it cheap to vendor a pinned version if that matters.

[repo](https://github.com/tzcnt/TooManyCooks) · [benchmark](https://github.com/tzcnt/runtime-benchmarks)

##### utl::parallel (UTL ThreadPool)  `C++`  `MIT`  `active`  `Tier A`

Header-only C++17 work-stealing thread pool with recursion-safe futures; beats std::async on small and recursive tasks.

**Beats:** std::async — On a 6-core AMD Ryzen 5 5600H (hyper-threading off), g++ 11.4.0 -O2, against libstdc++: utl::parallel::ThreadPool reached 573.3% of serial throughput vs std::async's 214.0% on small (0-100us) tasks (~2.7x faster) and 583.0%/565.1% vs 161.1%/154.7% on shallow/deep recursive tasks (~3.6x faster), where BS::thread_pool and progschj/ThreadPool deadlocked entirely; on large (1-3ms) tasks the two were nearly tied (597.0% vs 564.2%, ~1.06x).

**How:** Work-stealing thread pool: each worker has a local LIFO deque fed by recursively spawned tasks (kept hot in cache) plus a global FIFO queue for externally submitted tasks; idle threads steal from the back of other workers' local deques. Recursive awaiting is made safe by a custom future_type wrapping std::future whose get()/wait() search for stealable work locally instead of blocking outright, which is what avoids both the thread-creation overhead of std::async and the deadlocks that plain std::future-based pools hit on nested awaits.

**Use it when:**
- Many small (well under 1ms) tasks where std::async's per-call thread-spawn overhead dominates runtime
- Recursive/scatter-gather workloads (divide-and-conquer, fan-out fibonacci-style spawning) that need awaitable subtasks without deadlocking
- Header-only C++17 codebases that want a single dependency-free, vendorable (~600-900 LOC) thread pool instead of pulling in a framework
- Cross-platform targets (Windows, Linux, macOS, FreeBSD all CI-tested) needing a pool with no platform-specific code
- Parallel-for / parallel-reduce over containers or index ranges with automatic grain-size splitting

**Skip it when:**
- Large uniform non-recursive tasks (1-3ms+): advantage over std::async nearly vanishes (~1.06x, roughly tied)
- Workloads wanting a vendor-optimized scheduler (OpenMP/TBB-class NUMA-aware or SIMD-tuned scheduling) — author explicitly disclaims superiority over those
- Code that needs a real std::future everywhere (generic code pattern-matching on std::future<T>); future_type is a custom wrapper, only constructible from std::future, not one itself
- Projects already committed to a C++20-only recursive pool (Leopard, riften::ThiefPool) if that ecosystem fits better; utl::parallel is intentionally capped at C++17
- High-stakes throughput decisions without your own validation: this is the project's single-machine (consumer laptop) benchmark with no independent third-party reproduction, and the library is small (336 stars) and young

**Integration:** header-only · none (standard library only: <thread>, <future>, <mutex>, <condition_variable>, <queue>, <optional>, etc.) · C++17 · any (CI-tested on Windows, Ubuntu, macOS, FreeBSD); no platform-specific code

**Vs siblings:** Pick utl::parallel over BS::thread_pool or meet1214/thread-pool when the workload has recursively-awaited subtasks — both siblings deadlock on that pattern per UTL's own benchmark, while utl::parallel stays correct and ~3.6x faster than std::async. For large-scale or NUMA-sensitive scatter-gather work, the oneTBB-class siblings (Taskflow, dispenso, TooManyCooks, libfork) are the more feature-complete choice; utl::parallel wins when you want a minimal, dependency-free, copy-pastable single header instead of a full framework.

**Gotchas:**
- future_type is not std::future; code that specifically requires std::future<T> (e.g. via type traits) won't accept it directly, only convert from one
- set_thread_count() blocks until all in-flight tasks finish before resizing, and throws std::runtime_error if invoked from inside the pool on itself
- Default grain size is hardware_concurrency()*4 subranges; very unevenly-costed per-element work may need a manually tuned grain_size
- Only 4 of the module's benchmark scenarios include BS::thread_pool/progschj/ThreadPool as recursion baselines; those two deadlock outright once tasks await nested subtasks

**Status:** Actively maintained (last commit 2025-12-08 on master; 336 stars); MIT-licensed, header-only, small enough (~600-900 LOC for this module) to vendor directly into a project.

[repo](https://github.com/DmitriBogdanov/UTL) · [benchmark](https://github.com/DmitriBogdanov/UTL/blob/master/docs/module_parallel.md)

##### Taskflow  `C++`  `MIT`  `active`  `Tier B`

Header-only C++ task-graph library that beats oneTBB FlowGraph on heterogeneous CPU+GPU DAG workloads.

**Beats:** Intel oneTBB (FlowGraph task scheduler) — On a 1920-layer sparse DNN inference task graph (LSDNN challenge) run as a CPU+GPU task graph with up to 4 cudaFlows, across up to 9 co-running processes on 40 Intel Xeon CPU cores plus 4 GeForce RTX 2080 GPUs (clang++ v10 host compiler, CUDA 11, -std=c++17 -O2), Taskflow's IEEE TPDS 2021 paper (arXiv 2004.10908) reports up to 29% faster runtime, 1.5x less memory, and 1.9x higher weighted throughput than Intel oneTBB 2021.1 FlowGraph.

**How:** Each worker has a bounded lock-free work-stealing queue (ring buffer, default 256 slots, log2-sized via TF_DEFAULT_BOUNDED_TASK_QUEUE_LOG_SIZE) backed by an unbounded overflow queue, so idle workers steal ready tasks instead of waiting on a central scheduler like FlowGraph's. Worker wakeup uses a non-blocking/atomic notifier rather than plain condition variables. GPU offload is captured as an Nvidia CUDA Graph and replayed via a single graph-exec launch, avoiding per-kernel CPU launch overhead, which is the mechanism behind the paper's reported gains on a mixed CPU+GPU task graph.

**Use it when:**
- Workload is itself an irregular task DAG mixing CPU and GPU kernels in one graph, not a flat parallel-for
- Graph structure is dynamic or recursive at runtime (subflows) rather than declared statically up front like TBB FlowGraph
- Multiple taskflows/processes co-run on the same CPU+GPU node and you care about aggregate throughput under contention, not just single-run latency
- You want built-in parallel algorithms (for_each/reduce/sort/pipeline) and a graph profiler (TFProf) bundled with the scheduler
- A C++20 toolchain is already available (GCC 11+/Clang 12+/MSVC 19.29+/NVCC 12.0+)

**Skip it when:**
- You just need flat parallel loops or fire-and-forget async calls; a simple thread pool or std::async has far less API surface
- You're pinned to C++17 or an older compiler; the current release (v4.0.0) requires C++20
- Tasks throw exceptions heavily: open issues report tf::Semaphore combined with exceptions can deadlock (#732) and throwing many exceptions is UB that can crash or silently lose the exception (#724)
- You need evidence measured against std::async/std::thread directly; this benchmark is tier B and compares against oneTBB FlowGraph, one step removed from the std baseline
- You want a minimal header with no GPU-adjacent code paths; the repo ships a full CUDA task-graph subsystem (taskflow/cuda/*) even if you never touch a GPU

**Integration:** header-only · none for CPU tasking; optional Nvidia CUDA Toolkit 12.0+ (nvcc) for cudaFlow GPU tasking · C++20: GCC 11+, Clang 12+, MSVC 19.29+ (VS2019), Apple Clang 13+, NVCC 12.0+, Intel oneAPI DPC++ 2022.0+ (current README; the cited paper's benchmark used an earlier Taskflow with clang++ v10 and -std=c++17) · Linux, Windows, macOS; x86-64 and other C++20-capable targets; optional Nvidia CUDA GPU offload via taskflow/cuda

**Vs siblings:** dispenso, TooManyCooks, and libfork also beat oneTBB, but against its flat parallel_for/task-group APIs on CPU-only workloads. Pick Taskflow over them (and over Boost.Fiber/utl::parallel/meet1214/BS::thread_pool, which target std::thread/std::async) when the job is a DAG with heterogeneous CPU+GPU tasks, subflows, or conditional/cyclic control flow rather than a flat thread-pool or fiber replacement.

**Gotchas:**
- Exception handling in tasks is a known weak spot: tf::Semaphore plus exceptions can deadlock (issue #732), and throwing many exceptions is undefined behavior that can crash or drop the exception (issue #724)
- Past releases had real throughput regressions (reported in 3.8 and 3.10, since fixed) — verify the specific version before trusting a benchmark number
- Per-worker bounded work-stealing queue defaults to 256 tasks; graphs with very deep/bursty fan-out spill into the slower unbounded overflow queue
- v4.0.0 raised the minimum standard to C++20, up from C++17 in earlier major versions — code and CI written for older Taskflow may not compile as-is

**Status:** Actively maintained (commit as recent as 2026-09-14, 12.2k stars, 36 open issues); MIT-licensed and header-only so it's easy to vendor, but GitHub's license detector shows NOASSERTION even though the LICENSE file is standard MIT text, and the current release requires a C++20 toolchain.

[repo](https://github.com/taskflow/taskflow) · [benchmark](https://arxiv.org/abs/2004.10908)

#### bitsets-and-succinct

##### CRoaring (Roaring Bitmaps)  `C`  `Apache-2.0 OR MIT`  `active`  `Tier A`

Compressed bitmap for sparse 32/64-bit integer sets; set-algebra ops beat std::unordered_set/vector by 3x-800x, loses on dense data.

**Beats:** std::unordered_set<uint32_t> and sorted std::vector<uint32_t> with STL set algorithms (std::set_intersection/union/difference, std::binary_search) from the standard library bundled with GCC 5.4; also an uncompressed bitset (the authors' portable C 'cbitset', same word-array layout as std::bitset/std::vector<bool>) — Paper (Lemire et al., Software: Practice and Experience 2018, arXiv:1709.07821) benchmarked CRoaring single-threaded on an Intel i7-6700 (Skylake, Turbo off) against GCC 5.4 libstdc++ std::vector+STL set algorithms, std::unordered_set, and the authors' own uncompressed 'cbitset', compiled with -O3 -march=native, across 8 real 32-bit integer-set datasets (200 sets each, timed with rdtsc). Roaring's pairwise intersections beat sorted-vector+std::set_intersection by ~3-36x and std::unordered_set by up to ~250x while using 15.1 bits/value on Census1881 vs 195 for std::unordered_set and 32 for std::vector, but a plain uncompressed bitset beat Roaring on every membership query and on set algebra for dense/small-universe datasets.

**How:** Values are bucketed by their high 16 bits into 'containers' that switch representation per bucket: a sorted array for sparse chunks, a plain bitset for dense chunks, or a run-length list for consecutive runs (include/roaring/containers/{array,bitset,run}.h), so every 65536-value chunk stores whatever layout is smallest. Set operations dispatch per-container based on both operands' types (mixed_intersection.h, mixed_union.h, etc.) and use runtime-dispatched AVX2/AVX-512 SIMD on x86-64 for bitset and array operations. This adaptivity is what produces both the ~35x memory reduction over an uncompressed bitset and the win over linear STL set algebra on sparse/clustered data.

**Use it when:**
- Sets of 32-bit (or 64-bit) integers with variable, often sparse cardinality where you repeatedly compute intersections/unions/differences (search-index posting lists, ID filtering, join pushdown)
- Memory is a constraint: paper Table 4 shows Roaring at 15.1 bits/value on Census1881 and 2.60 on CensusInc vs 195 for std::unordered_set and 32 for std::vector on every dataset
- Throughput-oriented batch set algebra rather than single-key latency-sensitive lookups
- x86-64 (gets AVX2/AVX-512 runtime dispatch) or ARM/POWER/big-endian/RISC-V via the generic scalar path
- Need cross-language interop: portable serialization format shared with the Java, Go, Python, and Rust Roaring implementations

**Skip it when:**
- Fixed-size dense bit flags: a plain uncompressed bitset (the authors' own cbitset) beats Roaring by ~1.7-3x on dense/small-universe datasets and by roughly an order of magnitude on every membership query in the paper's Tables 6/7
- Membership-query-heavy workloads on clustered/dense data: std::unordered_set was faster than Roaring on 4 of 8 paper datasets for random-access contains()
- Multithreaded mutation: no built-in locking; a bitmap being modified must not be queried on another thread, and safe sharing requires passing copies (optionally with copy-on-write enabled)
- 64-bit sets via Roaring64Map specifically — issue #225 (open) reports poor read/write performance for its std::map-of-32-bit-buckets design; the ART-based Roaring64 alternative is marked experimental
- Untrusted input handled carelessly: the 32-bit API's unsafe portable_deserialize can read out of bounds on malformed data; must use the *_safe variant plus roaring_bitmap_internal_validate

**Integration:** source-drop (amalgamated single-file roaring.c/roaring.h/roaring.hh via amalgamation.sh) or static/shared lib via CMake · none for the C library; C++11-capable compiler only if using the optional roaring.hh/roaring64map.hh wrapper · C11 (GCC 7+, clang 8+, MSVC 2022+, Xcode 11+, Intel oneAPI 2023.2+); C++11+ for the C++ wrapper · x86-64 (AVX2/AVX-512 runtime-dispatched, no special build flags needed), ARM, POWER, big-endian, generic scalar path for others including RISC-V

**Vs siblings:** Pick CRoaring over plf::bitset, better_bitset, BitLib, or sul::dynamic_bitset when the domain is a sparse, dynamically-sized 32/64-bit integer *set* with heavy AND/OR/XOR/ANDNOT algebra — those siblings instead accelerate fixed-width std::bitset/std::vector<bool>-style dense bit-vector ops like shift/test/reset. Prefer pasta::bit_vector or a plain uncompressed bitset instead of CRoaring for succinct rank/select or dense small-universe bitsets, where CRoaring's per-container overhead loses on both memory and membership-query latency.

**Gotchas:**
- roaring_bitmap_portable_deserialize (32-bit, unsafe variant) reads out of bounds on malformed input; use the *_deserialize_safe variant plus roaring_bitmap_internal_validate for untrusted data (the 64-bit API only exposes the safe form)
- Two distinct 64-bit classes exist: Roaring64Map (std::map-keyed 32-bit Roaring buckets, flagged as having bad read/write performance in open issue #225) vs Roaring64 (ART-based, wraps roaring64.h, marked experimental)
- Copy-on-write is opt-in and off by default; mixing bitmaps with different COW settings was flagged unsafe in a still-open issue (#97) — set it consistently before sharing bitmaps across threads
- Run-container compression (runOptimize()/runOptimize) is not automatic — a bitmap built by looping add() over consecutive ranges keeps its original array/bitset containers until you explicitly call it

**Status:** Actively maintained (push activity as of today, 1,887 stars, used in production by ClickHouse, Apache Doris, Redpanda, YDB, Alibaba Tair, and StarRocks); dual Apache-2.0/MIT licensed, so the amalgamated single-file build is safe to vendor regardless of future upstream changes.

[repo](https://github.com/RoaringBitmap/CRoaring) · [benchmark](https://arxiv.org/pdf/1709.07821)

#### concurrency-queues-locks

##### atomic_queue  `C++`  `MIT`  `active`  `Tier A`

Header-only lock-free MPMC/SPSC ring-buffer queues beating std::mutex-guarded queues by 4-10x in latency and throughput.

**Beats:** std::mutex — On the author's own shootout (gcc-14.2.0, libstdc++, Ryzen 5950X with SMT on), AtomicQueue's SPSC ping-pong round-trip latency is 42ns versus 320ns for a std::mutex-guarded ring buffer baseline (~7.6x lower), and OptimistAtomicQueue reaches 33ns (~9.7x lower); 1-producer/1-consumer throughput is ~142.7M msg/s for AtomicQueue and a highly variable ~1.23B msg/s for OptimistAtomicQueue versus ~4.1M msg/s for std::mutex, though with 2-16 producer/consumer pairs only OptimistAtomicQueue keeps a large (4-24x) lead while plain AtomicQueue is roughly at parity with std::mutex.

**How:** A ring buffer with compile-time or construction-time fixed capacity avoids heap allocation and pointer chasing after construction, and value semantics (no references into the buffer) avoid pointer aliasing. It issues the bare minimum of atomic instructions per push/pop, explicitly pads to avoid false sharing, and its SPSC mode drops expensive atomic read-modify-write ops in favor of plain atomic loads/stores. There is no OS-blocking wait path: push/pop either fail fast (try_ variants) or busy-spin (optimist push/pop), avoiding the roughly 1-3us syscall/wake-up latency of a blocked thread.

**Use it when:**
- Fixed/bounded number of in-flight small, cheaply copyable/movable messages (integers, pointers, small PODs) between a known set of threads.
- Sub-microsecond push-to-pop latency matters more than avoiding CPU spin, and dedicated cores/threads are available to spin.
- SPSC hot path (e.g. one I/O thread feeding one processing thread) where the SPSC-tuned mode avoids read-modify-write atomics entirely.
- Shared-memory IPC between processes: non-B variants are position-independent and can be placement-new'd into mmap/shm_open segments.
- Need back-pressure signaling via try_push failure rather than letting a queue grow unbounded.

**Skip it when:**
- Need unbounded or dynamically-growing capacity; maximum size must be fixed at compile time (array buffer) or construction time (B variants).
- Threads should sleep/block instead of spinning; there is no OS-blocking wait, so waiting threads pin a CPU core at 100%.
- Elements are large or expensive to copy/move, since push/pop always copies or moves the element and no in-place references are exposed.
- Need per-element priorities or ordering guarantees beyond FIFO/the optional totally-ordered mode.
- Atomic-element queues: pushing the reserved NIL sentinel is undefined behavior in release builds (only debug asserts catch it), so element type/value range must exclude it.

**Integration:** header-only · none to use the library; Boost.Test is needed only to build its own unit tests · C++14; also builds under C++20/C++23 as of v1.9.4 (v1.9.3 had a C++20 AtomicQueueB2 constructor bug on Apple clang, fixed in v1.9.4) · Linux x86_64 (primary dev/benchmark target); CI also covers Linux ARM, RISC-V, PowerPC, S390, LoongArch (via QEMU), Windows x86_64, and macOS ARM

**Vs siblings:** Pick atomic_queue's OptimistAtomicQueue when the workload has contention from multiple producer/consumer pairs, since it is the only queue in this shootout that keeps a large (4-24x) throughput lead over std::mutex from 2 to 16 pairs, or when queue objects must be position-independent for shared-memory IPC. For a pure low-contention SPSC channel, moodycamel::ReaderWriterQueue (43ns) and Boost.Lockfree spsc_queue (51ns) post comparable ping-pong latency with smaller, more established codebases, and plain (non-optimist) AtomicQueue itself is only at parity with std::mutex once several producer/consumer pairs contend.

**Gotchas:**
- NIL sentinel (default 0) must never be pushed into atomic-element queues; release builds have no runtime check and violation causes UB such as deadlocks or lost elements.
- No OS-blocking push/pop: busy-spin waiting consumes a full CPU core, unsuitable for threads that should yield or sleep.
- v1.9.3 broke AtomicQueueB2's constructor under -std=c++20 on Apple clang (issue #109, fixed in v1.9.4, released 2026-09-16); use >=1.9.4.
- Capacity is fixed once (compile time for array buffers, construction time for heap/B-variant buffers) and cannot grow; undersizing it makes try_push start failing under load.

**Status:** Actively maintained (recent commits and the v1.9.4 point release as of September 2026) under the MIT license; header-only and small enough to vendor directly.

[repo](https://github.com/max0x7ba/atomic_queue) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

##### Boost.Lockfree  `C++`  `BSL-1.0`  `active`  `Tier A`

Boost's lock-free MPMC/SPSC queue and stack family; beats std::mutex on latency, not contended MPMC throughput.

**Beats:** std::mutex — An independent third-party benchmark (the atomic_queue shootout; gcc-14.2.0 -O3 -march=native, AMD Ryzen 5950X, Linux) measured ping-pong round-trip latency of spsc_queue at 51ns and queue at 92ns against std::mutex at 320ns (about 6.3x and 3.5x lower). A separate 2017 evpp benchmark (gcc-4.8.2, Xeon E5-2630 v2) found boost::lockfree::queue giving 75-150% higher throughput than a mutex-guarded std::vector, but only with multiple producers. Neither benchmark is Boost's own, and the same shootout's MPMC throughput data shows boost::lockfree::queue losing to std::mutex once 2 or more producer/consumer pairs are contending.

**How:** queue implements Michael & Scott's lock-free MPMC algorithm with a tagged-pointer freelist that recycles nodes instead of returning memory to the OS on every pop. spsc_queue is a wait-free single-producer/single-consumer ring buffer (the same technique used in the Linux kernel) with no compare-and-swap on its hot path at all. Skipping mutex acquisition removes the futex/syscall path and priority-inversion risk that dominate std::mutex latency under contention. bounded_ticket_queue additionally implements a Vyukov turnstile algorithm that becomes wait-free when producer or consumer count is fixed to one side.

**Use it when:**
- Exactly one producer thread and one consumer thread need a ring buffer and latency matters (spsc_queue measured at 51ns vs std::mutex 320ns in the atomic_queue shootout)
- MPMC queue with a bounded/fixed-size capacity, where avoiding OS-level allocation and priority inversion matters more than peak contended throughput
- Already depend on Boost and want an actively maintained (last commit 2026-08-14), widely-used lock-free structure without adding a new third-party dependency
- Element type is a small, trivially-copyable POD (ints, small structs, raw pointers used carefully) rather than move-only or exception-throwing

**Skip it when:**
- Heavily contended MPMC throughput: in the atomic_queue shootout, boost::lockfree::queue loses to a std::mutex-guarded ring buffer at every count of 2+ producer/consumer pairs (5.9M vs 13.0M msg/s at 2 pairs; 1.5M vs 2.3M at 16)
- T is a pointer type: open issue #120 reports a data race where concurrent pop() can hand the same pointer to two threads
- Code depends on pop() returning false only when the queue is truly empty: open issue #119 shows pop() can spuriously return false under concurrent push/pop on a non-empty queue
- Need move-only element types or exception-safety guarantees in push/pop: unsupported (open request #125); docs explicitly discourage exceptions in lock-free code
- Need std::queue/std::stack API compatibility such as iteration or arbitrary resizing: the API is deliberately narrower

**Integration:** header-only · Boost.Align, Boost.Assert, Boost.Atomic, Boost.Config, Boost.Core, Boost.Parameter, Boost.Predef, Boost.Utility (ships as part of Boost, not standalone) · C++14 (CMake target_compile_features cxx_std_14); uses C++20 concepts opportunistically when available · any platform with CAS/double-width-CAS atomic support; internal tagged-pointer representation switches between a DCAS scheme and a pointer-compression scheme depending on platform, not documented as restricted to a specific ISA

**Vs siblings:** Pick Boost.Lockfree when you already depend on Boost and want an actively-maintained, well-tested queue without adding a new dependency. Pick atomic_queue or moodycamel::ReaderWriterQueue instead when SPSC latency is the priority (42-43ns vs Boost's 51ns) or for contended MPMC throughput, where boost::lockfree::queue loses to a plain std::mutex ring buffer.

**Gotchas:**
- boost::lockfree::queue<T*> has an open data-race report (issue #120): concurrent pop() can return the same pointer to two threads
- pop() can spuriously return false on a non-empty queue under concurrent push/pop (issue #119), so a false return does not strictly mean 'empty'
- T must be trivially copy-assignable and trivially destructible for queue; move-only types fail to compile rather than degrading gracefully
- capacity<> and allocator<> policy options are mutually exclusive (static_assert) - pick compile-time-fixed or runtime-allocated sizing, not both

**Status:** Actively maintained as part of mainline Boost (last commit 2026-08-14); BSL-1.0 licensed and header-only, so it is cheap to adopt if you already take Boost as a dependency.

[repo](https://github.com/boostorg/lockfree) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

##### contention_free_shared_mutex (AlexeyAB/object_threadsafe safe_ptr library)  `C++`  `Apache-2.0`  `abandoned`  `Tier A`

Per-thread sharded reader-writer lock and object wrapper claiming up to ~10x std::shared_mutex throughput under read-heavy contention.

**Beats:** std::shared_mutex — The author's own benchmark (bench_contfree, g++ -std=c++14 -pthread -O3, GCC 6.3.0, 16 threads on one Xeon E5-2660 v3) measured a std::map guarded by contention_free_shared_mutex<> against the same map guarded by std::shared_mutex: 34.60 vs 2.44 Mops at 0% writes (~14x) and 5.16 vs 0.74 Mops at 15% writes (~7x). The README's headline '10x' sits between these two figures; a separate real-app chart (2x Xeon E5-2686 v4, 20 usec forced inter-thread delay) shows near-parity up to 16 threads and only ~5x at 64 threads.

**How:** contention_free_shared_mutex shards the 'a reader is present' flag across a fixed-size array (default 36 slots), one cache-line-padded atomic<int> per registered thread; a reader touches only its own slot instead of contending on the single shared atomic that a typical std::shared_mutex reader count uses. A writer sets one global want_x_lock flag, then spins until every slot reports idle. Thread-to-slot mapping is cached in a thread_local unordered_map keyed by the mutex instance so repeat lock_shared() calls skip the registration scan.

**Use it when:**
- Shared state accessed by a bounded, roughly-known number of threads (<=36 by default, adjustable via the contention_free_count template parameter) under a read-heavy or mixed workload currently guarded by std::shared_mutex.
- You can accept the operator-> / operator* locking syntax instead of direct member access, or you only need contention_free_shared_mutex<> itself as a mutex-only drop-in.
- You want recursive locking across same-mode combinations (X->X, S->S) that std::shared_mutex does not provide.
- The project is small enough (one ~630-line header, Apache-2.0) to vendor and audit or patch yourself.

**Skip it when:**
- More than ~36 threads regularly contend: past the compiled-in slot count, get_or_set_index() returns -1 and lock_shared() falls back to competing for the same exclusive want_x_lock flag as lock(), erasing the advantage.
- Producer/consumer or queue-shaped concurrency -- this is a general object lock, not a lock-free queue like the sibling entries in this category.
- Any code path upgrades a shared lock to exclusive (S->X): explicitly documented in the header comment as undefined behavior.
- You create and destroy contention_free_shared_mutex instances repeatedly (e.g. on the stack): open, unfixed issue #5 shows the thread-local index cache can misidentify a new instance that reuses a freed instance's memory address, corrupting lock state.
- You need try_lock/try_lock_shared or timed locking: contention_free_shared_mutex only implements lock/unlock/lock_shared/unlock_shared, not the full BasicLockable/SharedTimedLockable interface std::shared_timed_mutex offers.

**Integration:** header-only · none beyond the standard library (<atomic>, <mutex>, <thread>, and <shared_mutex> when C++14 is detected) · C++11 for safe_ptr<>/safe_obj<>/contention_free_shared_mutex<>; C++14 (or MSVC 1900+) additionally enables the std::shared_timed_mutex-based shared_mutex_safe_ptr variant via an __cplusplus/_MSC_VER check. Benchmarks were built with g++ -std=c++14 -pthread -O3. · any platform with a C++11/14 standard library and std::atomic; benchmarked on x86-64 Linux with GCC, and ships MSVS 2015 project files for Windows.

**Vs siblings:** All six sibling entries in this category (atomic_queue, Boost.Lockfree, moodycamel::ReaderWriterQueue, oneTBB concurrent_bounded_queue, xenium, eventpp::SpinLock) are lock-free queues benchmarked against std::mutex for producer/consumer handoff latency; none targets std::shared_mutex. Pick object_threadsafe when the baseline is a std::shared_mutex-guarded object (e.g. a std::map) under a read-heavy or mixed workload with a bounded thread count, not a queue-shaped pipeline.

**Gotchas:**
- S->X lock upgrade (taking the exclusive lock while already holding a shared lock) is explicitly undefined behavior per the header's own comment.
- Contention-free behavior caps at contention_free_count threads (default 36); beyond that, lock_shared() falls back to the same exclusive want_x_lock path as lock(), per the registration logic in safe_ptr.h.
- Open issue #5 (unfixed as of this check): the per-thread slot index is cached in a thread_local map keyed by the mutex's `this` pointer, so a stack-allocated mutex that is destroyed and a new one reallocated at the same address can be misidentified, corrupting lock state.
- Every contention_free_shared_mutex<> instance allocates contention_free_count x 64-byte padded slots up front (~2.3 KB at the default of 36), a fixed per-instance memory cost regardless of actual thread count.

**Status:** Abandoned: last commit 2020-04-13, and a known thread-index correctness bug (issue #5) has sat open and unfixed since; still Apache-2.0 and a single ~630-line header, so it remains cheap to vendor and patch yourself.

[repo](https://github.com/AlexeyAB/object_threadsafe) · [benchmark](http://web.archive.org/web/20210806092034id_/https://www.codeproject.com/Articles/1183423/We-Make-a-std-shared-mutex-10-Times-Faster)

##### moodycamel::ReaderWriterQueue  `C++`  `BSD-2-Clause`  `active`  `Tier A`

Header-only lock-free SPSC queue for C++11; beats a mutex-guarded queue by ~7x in ping-pong latency.

**Beats:** std::mutex — In the independent max0x7ba/atomic_queue SPSC ping-pong shootout (gcc-14.2.0, -O3 -march=native -mtune=native, AMD Ryzen 5950X, readerwriterqueue commit 2ae710d), moodycamel::ReaderWriterQueue measured a 43ns mean round-trip latency versus 320ns for a mutex-guarded ring buffer used as the std::mutex baseline (~7.4x lower). The project's own benchmarks/bench.cpp never compares against std::mutex at all — only against the 1024cores SPSC queue and folly::ProducerConsumerQueue.

**How:** Queue-of-queues design: a circular-linked-list of fixed-size 'block' ring buffers, with the producer owning tail indices/pointers and the consumer owning front indices/pointers so each thread only writes its own state. Enqueue/dequeue are wait-free (no CAS loop, no spinning), O(1) except when a new block must be malloc'd. On x86/x86-64 the required memory barriers compile down to no-ops, so the hot path is just plain loads and stores.

**Use it when:**
- Exactly one fixed producer thread and one fixed consumer thread that never swap roles
- Passing small, cheaply-movable/copyable values (counters, pointers, small structs) between the two threads
- Need sub-100ns round-trip latency and want to avoid std::mutex-guarded queue overhead entirely
- Want a 2-file header-only drop with zero build step and zero external dependencies
- Running on x86/x86-64 (the best-tested and only architecture the author has directly validated)

**Skip it when:**
- Need multiple producers or multiple consumers (use the same author's moodycamel::ConcurrentQueue instead)
- Threads need to switch producer/consumer roles at runtime, or use the queue from more than 2 threads
- Targeting AArch64 or another weakly-ordered architecture on an old pinned commit: size_approx() had a real SIGSEGV race from a missing release fence before publishing new blocks (issue #171); fixed, but verify the fix is in your pinned commit
- Need a version-pinned release: the project ships no tags (open issues #144/#146 ask for one), so you pin a raw commit SHA
- Destroying the queue while a thread is blocked in wait_dequeue() is undefined behavior — risky in ad-hoc shutdown paths

**Integration:** header-only · none (readerwriterqueue.h + atomicops.h; atomicops.h embeds Preshing's zlib-licensed semaphore for the blocking variant) · C++11; MSVC2010+, GCC 4.7+ (GCC 4.6 has a fence bug), ICC 13+ · x86/x86-64 (only architecture directly tested by the author); portable to ARM/PowerPC per code comments but AArch64 had a confirmed weak-memory-model race, fixed in a recent commit (issue #171); explicitly not for DEC Alpha

**Vs siblings:** Pick this over atomic_queue, Boost.Lockfree, xenium, or oneTBB when you want the smallest possible header-only footprint (2 files, no build) purely for the SPSC case and don't need bounded/blocking strategy choices or MPMC support; atomic_queue's AtomicQueue (42ns) and OptimistAtomicQueue (33ns) edge it out slightly in the same shootout, so pick those instead if the last few nanoseconds matter more than dependency count.

**Gotchas:**
- size_approx() could dereference a null block on AArch64 due to a missing release fence in inner_enqueue() (issue #171) — fixed, but confirm the fix predates whatever commit you pin
- Plain enqueue() can malloc and grow the queue on demand; only try_enqueue() is guaranteed never to allocate
- Destroying the queue while a thread is blocked in wait_dequeue()/wait_dequeue_timed() is undefined behavior
- No tagged releases exist (open issues #144, #146); vendor a commit SHA rather than expecting semver tags

**Status:** Actively maintained (last commit 2026-09-07, 4.6k stars) but ships no tagged releases; BSD-2-Clause (Simplified BSD, per LICENSE.md — GitHub's license detector shows NOASSERTION) and small enough (2 headers) to vendor directly.

[repo](https://github.com/cameron314/readerwriterqueue) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

##### oneTBB concurrent_bounded_queue  `C++`  `Apache-2.0`  `active`  `Tier A`

Bounded/blocking FIFO queue in Intel's oneTBB parallelism library; non-blocking try_push/try_pop mode cuts round-trip latency ~3.9x vs std::mutex.

**Beats:** std::mutex — In the independent max0x7ba/atomic_queue SPSC ping-pong shootout on an AMD Ryzen 5950X (gcc-14.2.0, -O3 -march=native -mtune=native, TBB 2021.11.0-2ubuntu2, mitigations=off), tbb::concurrent_bounded_queue driven via non-blocking try_push/try_pop averaged 83ns round-trip latency versus 320ns for a std::mutex-guarded queue over libstdc++, about 3.9x lower latency; the same suite's MPMC throughput test showed only ~2x std::mutex at 1 producer/1 consumer, with std::mutex ahead at 2 and 4 pairs.

**How:** Enqueue/dequeue hand out monotonically increasing 'tickets' from head_counter/tail_counter atomics via compare-exchange, mapping each ticket to a slot in a lazily-grown ring of fixed-size micro-segments, so there is no single global mutex on the hot path. Blocking waits (capacity-limited push, empty pop) go through a dedicated concurrent_monitor wait/notify mechanism implemented in the compiled runtime rather than busy-spinning, and internal structures are cache-line aligned (cache_aligned_allocator, alignment asserts against max_nfs_size) to reduce false sharing between producer and consumer cache lines. The cited benchmark used non-blocking try_push/try_pop, which skips the monitor-wait path entirely and reduces each operation to a handful of atomics plus one CAS.

**Use it when:**
- Already linking oneTBB elsewhere in the app, so adding another dependency just for a queue is unnecessary
- Need bounded capacity plus real blocking push/pop with a documented cancellation path (abort())
- Producer/consumer counts are modest (roughly 1 pair) where ~3.9x lower latency and ~2x throughput over std::mutex is enough headroom
- Want an Apache-2.0, multi-platform (Windows/Linux/macOS/Android) queue backed by an industry foundation rather than a single-maintainer header library
- Value signed size()/empty() semantics that expose how many consumers are waiting

**Skip it when:**
- Pure SPSC ping-pong latency is the goal: moodycamel::ReaderWriterQueue (43ns) and atomic_queue (42ns) are faster and header-only
- Cannot add a compiled runtime/link dependency: the blocking and abort machinery lives in the compiled oneTBB library, not just the header
- Higher contention (2+ producer/consumer pairs): in the same shootout's MPMC throughput test std::mutex actually beat concurrent_bounded_queue at 2 pairs (13.0M vs 11.1M msg/s) and 4 pairs (6.9M vs 6.5M msg/s)
- Exceptions are disabled: abort() and blocked waiters signal cancellation by throwing exception_id::user_abort, not via a non-throwing flag
- Want a minimal, easily vendored single header; oneTBB is a large library with its own build/install story

**Integration:** shared lib (headers call into a compiled runtime; can also be built static via CMake) · oneTBB runtime library (libtbb) must be built/linked; no third-party deps for the queue itself. oneTBB overall optionally uses hwloc for NUMA-aware scheduling elsewhere in the library, not required for this queue. · C++11 minimum per the CMake default (CMAKE_CXX_STANDARD); GCC 8-16, Clang 7-22, MSVC 14.2+ (VS2019+), or Intel oneAPI DPC++/C++ per SYSTEM_REQUIREMENTS.md · x86-64 primary; Windows, Linux, and macOS officially supported, Android 9 supported; MinGW, FreeBSD, Windows on ARM/ARM64, and macOS on ARM64 are community-supported; separate WASM support documented

**Vs siblings:** Pick oneTBB's concurrent_bounded_queue over atomic_queue, Boost.Lockfree, moodycamel::ReaderWriterQueue, or xenium when you already depend on oneTBB or specifically need its bounded-capacity blocking push/pop plus abort()-based cancellation with vendor-grade, multi-platform support; all four siblings are faster in raw ping-pong latency (42-60ns vs 83ns) and are header-only, so prefer them when latency or a zero-dependency drop-in matters more than having one production parallelism library.

**Gotchas:**
- abort() and any blocked push()/pop() unblock by throwing exception_id::user_abort, so callers need exceptions enabled and abort-aware code, not a simple non-throwing cancel flag
- Default capacity is effectively unbounded (near SIZE_MAX / item size); set_capacity() is required to get real bounding, and the docs note bounded queues are slower than unbounded ones
- empty() means size() <= 0, not 'no elements present' — with pending pops, size() is negative
- Not a single-header drop-in: it links against a compiled oneTBB runtime rather than working as a standalone header like a typical lock-free queue library

**Status:** Actively maintained by the UXL Foundation as Intel's flagship C++ threading library (about 6.7k stars); Apache-2.0 licensed and copyable, but adopting concurrent_bounded_queue alone still means pulling in oneTBB's full compiled runtime, not vendoring a small file.

[repo](https://github.com/uxlfoundation/oneTBB) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

##### xenium  `C++`  `MIT`  `stale`  `Tier A`

Header-only lock-free MPMC queue templates (Michael-Scott, Ramalhete, Vyukov) beating std::mutex latency 2.5-5.7x.

**Beats:** std::mutex — Independent third-party shootout (max0x7ba/atomic_queue benchmarks.cc, gcc-14.2.0, xenium commit f6416d3, -O3 -march=native -mtune=native, libstdc++, AMD Ryzen 5950X, mitigations=off) measured mean round-trip ping-pong latency of 56ns for ramalhete_queue, 60ns for vyukov_bounded_queue, and 128ns for michael_scott_queue against 320ns for std::mutex — roughly 5.7x, 5.3x, and 2.5x lower respectively; xenium's own benchmark suite has no std::mutex comparison.

**How:** ramalhete_queue implements Ramalhete & Correia's FAAArrayQueue: array-segmented linked-list nodes with fetch-and-add push/pop index cursors instead of a CAS per element, cutting contention on the fast path. michael_scott_queue is the classic Michael & Scott (1996) CAS-based lock-free linked-list queue. vyukov_bounded_queue uses Vyukov's bounded MPMC ring-buffer design with per-slot sequence numbers so producers and consumers avoid contending on shared head/tail counters. In the benchmark that produced these numbers, both node-based queues were configured with xenium::reclamation::new_epoch_based (confirmed in atomic_queue's benchmarks.cc), avoiding hazard-pointer-style per-op bookkeeping.

**Use it when:**
- Low-latency SPSC/MPMC ping-pong or handoff paths where std::mutex+std::queue's lock overhead dominates (measured 56-128ns vs 320ns round trip)
- Fixed, known-capacity workloads where an allocation-free bounded ring buffer is acceptable -> vyukov_bounded_queue
- Value types that are raw pointers, std::unique_ptr, or small trivially copyable PODs and you want the fastest of the three -> ramalhete_queue
- Arbitrary movable value types where ramalhete_queue's type restriction is unacceptable and you can absorb per-push allocation -> michael_scott_queue
- C++17 codebases willing to vendor a header-only dependency and explicitly choose a reclamation-scheme policy

**Skip it when:**
- High push contention with ramalhete_queue: an open, maintainer-confirmed double-free bug in the node destructor when pop_idx/push_idx wrap (issue #44, opened Oct 2025, unresolved)
- Object destructors that themselves push to a xenium queue using the same reclamation scheme can recurse into reclamation and double-destruct (issue #41, open; workaround is using a different reclaimer per structure)
- Repo has had no commits in ~14 months (last push 2025-07-29); treat as stale, not actively developed
- Need arbitrary non-trivial value types and want the fastest queue: ramalhete_queue's type restriction (pointer-like or small trivially copyable) rules it out
- Teams that want to avoid template-heavy header-only code and reclamation-scheme decisions versus the simplicity of std::mutex+std::queue

**Integration:** header-only · none for library use (C++17 standard library only); googletest, taocpp/json, taocpp/config are only needed as submodules to build the unit tests/benchmarks · C++17; CI validates gcc9, clang10, Visual Studio 2019 · x86-64 confirmed in the cited benchmark (Ryzen 5950X, Linux); CI also covers Windows/VS2019; no documented architecture restriction, ARM not verified

**Vs siblings:** Pick xenium when you also want a reusable library of composable reclamation schemes (hazard pointers, epoch-based, stamp-it) shared across other lock-free structures like hash maps and sets, not just a queue; atomic_queue and moodycamel::ReaderWriterQueue are narrower, simpler, and measured faster (33-51ns) with no reclamation-scheme decision to make, and Boost.Lockfree/oneTBB trade some speed for being part of a more widely vetted, already-deployed library.

**Gotchas:**
- Open, maintainer-confirmed bug: ramalhete_queue's node destructor can double-free under high push contention when pop_idx/push_idx wrap around (issue #44, unresolved as of this writing)
- Pushing to a queue from inside an object's destructor while that object is being reclaimed by the same scheme can recurse and double-destruct (issue #41); maintainer recommends a different reclamation scheme per data structure
- ramalhete_queue only accepts raw pointers, std::unique_ptr (custom deleters not yet supported), or trivially copyable types no larger than a pointer
- stamp_it reclaimer emits -Winvalid-memory-model warnings under gcc12 with -Werror (issue #26, open since 2022, documented one-line workaround)

**Status:** Stale: no commits since 2025-07-29 (~14 months) though the maintainer still replies to issues; MIT-licensed, header-only, and small enough to vendor, but two open double-free/double-destruction bug reports (#41, #44) remain unresolved.

[repo](https://github.com/mpoeter/xenium) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

#### hash-maps-sets

##### abseil (absl::flat_hash_map, Swiss tables)  `C++`  `Apache-2.0`  `active`  `Tier A`

SwissTable-based hash map beating std::unordered_map on build, find, churn, and iteration speed.

**Beats:** std::unordered_map — Benchmarked by unordered_dense's third-party harness (scripts/ab/bench_readme.sh) against std::unordered_map on libstdc++, clang 22.1.8, -O3 -DNDEBUG -std=c++20, AMD Ryzen 9 7950X: absl::flat_hash_map is 5.99x faster build+destroy, 2.43x faster find, 3.52x faster churn, and 8.28x faster iterate on uint64_t keys (1.76x-24.8x across ops on std::string keys), while carrying roughly 1.11x the resident memory of std::unordered_map — a gap the benchmark authors attribute partly to glibc allocator arena retention rather than the map's own footprint.

**How:** SwissTable: an open-addressing table with quadratic probing over groups of slots, where a separate control-byte array stores a 7-bit hash fragment (H2) per slot and SIMD-style group instructions (SSE-like on x86, bit tricks on other architectures) scan a whole group at once to reject non-matches before touching slot memory. The control-byte array is dense and cache-friendly, packing more logical slots per cache line than a node-based table, and a small-object optimization keeps tiny tables entirely inline, avoiding allocation.

**Use it when:**
- uint64_t or small POD keys where build+destroy, find, or iteration dominate: 5.99x/2.43x/8.28x faster than std::unordered_map respectively on this benchmark.
- std::string-keyed maps needing faster iteration (24.8x) or build+destroy (1.76x) than std::unordered_map.
- Codebases already depending on Abseil (absl::Hash, absl::string_view) where adding one more absl:: type has no extra dependency cost.
- Iteration-heavy or lookup-heavy workloads on x86-64 or aarch64 where cache-friendly probing matters.
- General-purpose 'default hash map' choice, which is Abseil's own stated recommendation, when pointer/reference stability is not required.

**Skip it when:**
- Code that needs pointer/reference stability across insert/rehash — use absl::node_hash_map or std::unordered_map's node-based stability instead.
- Exception-safety requirements: flat_hash_map is explicitly documented as not exception-safe.
- Crossing dynamically-loaded library (.so/.dll) boundaries — unsupported because absl::Hash values are randomized per DSO.
- Untrusted or adversarial key input: absl::Hash is not a cryptographic hash, and open issue #2171 (opened 2026-09-23) shows fixed string pairs that collide for every seed, a hash-flooding-style risk.
- Insert-then-mostly-erase workloads: capacity only shrinks on rehash()/clear(), so tombstones from erase() bloat iteration cost (O(capacity), not O(size)).

**Integration:** source-drop / static lib (built via Bazel or CMake; not a single header) · none beyond the C++ standard library (absl/base itself has no dependency on other Abseil code) · C++17 (per README); CMake 3.16+ if using the CMake build · x86 (SIMD-style group scan) with a portable bit-trick fallback for other architectures such as aarch64, per raw_hash_set.h; any platform with a C++17 compiler and Bazel or CMake

**Vs siblings:** Pick abseil when you're already in the Abseil ecosystem or want a Google-maintained library with the widest deployment footprint (Chromium, TensorFlow); its u64 numbers (5.99x build+destroy, 8.28x iterate) sit close to boost::unordered_flat_map (5.00x/similar) and unordered_dense (4.84x/13x) on this harness. unordered_dense's own analysis of the same run notes boost::unordered_flat_map beats absl on u64 find and churn (absl scores 0.81x relative on both) — pick boost or unordered_dense instead if lookup/churn latency or a lighter, header-only dependency matters more than ecosystem fit.

**Gotchas:**
- rehash() and move invalidate all iterators, pointers, and references — std::unordered_map keeps references stable on rehash, flat_hash_map does not.
- Not exception-safe (stated directly in flat_hash_map.h's header comment).
- Iteration is O(capacity), not O(size); heavy erase() churn slows down begin()/++iterator, and capacity never shrinks except on rehash()/clear().
- Open issue #2171 (filed 2026-09-23, unresolved as of this writing): absl::Hash has fixed string-pair inputs that collide under every seed — worth checking if keys are attacker-controlled.

**Status:** Actively maintained by Google with a 'live-at-head' philosophy (last commit 2026-09-24) plus LTS releases for teams that can't track head; Apache-2.0, 18.1k stars, used at Chromium/TensorFlow/Google scale — mature and well-tested, but requires a Bazel or CMake build rather than a drop-in single header.

[repo](https://github.com/abseil/abseil-cpp) · [benchmark](https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md)

##### ankerl::unordered_dense  `C++`  `MIT`  `active`  `Tier A`

Vector-backed hash map beating std::unordered_map on build, iteration, and string-key workloads, with weaker reference stability.

**Beats:** std::unordered_map — On the library's own scripts/ab/bench_readme.sh harness (clang 22.1.8, -O3, transparent huge pages via madvise, pinned to one core, Fedora 44, AMD Ryzen 9 7950X; std::unordered_map presumed on libstdc++) with 1-2 million u64 or std::string keys, ankerl::unordered_dense::map beat std::unordered_map by 4.84x on build+destroy, 1.98x on find, 2.84x on churn, and roughly 110x on full-table iteration (0.19 vs 21.29 ns/element); with std::string keys build+destroy was 3.64x faster. This is a first-party benchmark — the author wrote both the map and the harness, which he states on the page — but the harness, raw CSV, and SVGs are public in the repo.

**How:** Values live in a std::vector, so iteration is a linear scan with no pointer chasing. Lookups use a separate flat array of 88-byte 'group' blocks (16 slots each: 16 one-byte fingerprints, 8 overflow counters, 16 value indices); a probe loads all 16 fingerprints and compares them in one SSE2 (x86-64) or NEON (AArch64) instruction. Overflow counters replace tombstones, so erase never forces a rehash. Inserts emplace_back onto the vector and record the slot in the index, keeping iteration order equal to insertion order until an erase reorders it.

**Use it when:**
- Workloads that iterate the whole table often (snapshotting, serialization, aggregation) — 0.19 ns/element vs 21.29 for std::unordered_map (~110x) and 5.5-13x faster than flat hash maps like abseil/boost
- std::string-keyed maps that are built and torn down repeatedly — 2.1-2.6x faster build+destroy than any flat map measured (93 ns/entry vs 192-237 ns)
- Need to debug/inspect the table's contents easily — data is a plain std::vector, visible in any debugger, plus a bundled LLDB formatter script
- Want a std::unordered_map-shaped container with pluggable storage: std::allocator, polymorphic allocators, a custom random-access container (e.g. boost::interprocess::vector), or a huge-page allocator
- Batch key lookups against a large or partially-missing key set — visit() gives 1.15-1.5x over one-at-a-time find() by overlapping independent memory accesses

**Skip it when:**
- Code that depends on iterator or reference stability across insert/erase — elements live in a std::vector, so growth reallocates and erase moves the last element into the freed slot
- Integer-keyed, find- or churn-dominated workloads where every ns counts — loses to boost::unordered_flat_map on u64 find (0.73x) and churn (0.61x), and to abseil's flat_hash_map similarly
- Erase-heavy workloads specifically — erase needs two lookups (the target slot and the slot of the element swapped into it), called out in the README as "relatively slow"
- Any code path where a value's destructor (or other callback) re-enters erase() on the same map while an erase is already in progress — this infinite-loops; the maintainer says it is unsupported and won't be fixed (GitHub issue #126)
- Need const Key in the stored pair (std::pair<const Key, Value>) — this map's pair has a non-const key, unlike std::unordered_map

**Integration:** header-only · none (include/ankerl/unordered_dense.h + include/ankerl/stl.h; huge_page_allocator.h is a separate optional header needing <sys/mman.h>) · C++17 for map/set; C++20 required only for the optional module build (import ankerl.unordered_dense) · x86-64 (SSE2 probe, part of the baseline, no flag needed), AArch64 (NEON probe, likewise automatic); any other architecture falls back to a portable word-at-a-time probe via ANKERL_UNORDERED_DENSE_HAS_SSE2/NEON=0. huge_page_allocator degrades to std::allocator on Windows/macOS.

**Vs siblings:** Pick unordered_dense over abseil::flat_hash_map or boost::unordered_flat_map when iteration speed or std::string-keyed build/destroy dominate (its 0.19 ns/element iterate and ~93 ns/entry string build+destroy beat both); pick abseil or boost instead when integer-keyed find/churn throughput is what matters, since unordered_dense loses to boost there (0.73x find, 0.61x churn) and to abseil similarly. Against folly's F14ValueMap, unordered_dense wins on both build+destroy (4.84x vs 3.97x) and find (1.98x vs 1.72x) per this catalog's numbers. robin_hood::unordered_map is an earlier project by the same author with a different (robin-hood) index; unordered_dense's 5.0 index replaced that design and is reported 1.6x faster build+destroy than it on u64 keys, per doc/benchmarks.md.

**Gotchas:**
- No iterator or reference stability on insert or erase — elements live in a std::vector, so any growth or erase can relocate other elements
- Reentrant erase() (e.g. a destructor triggered by that very erase calling erase() again on the same map) infinite-loops; maintainer confirmed this is unsupported and won't be fixed (issue #126)
- A custom hash functor without `using is_avalanching = void;` is silently treated as low-quality and gets an extra mixing step; forgetting the marker on a genuinely good hash costs speed with no warning (require_avalanching<Hash> exists to make this a compile error instead)
- Post-5.0 the index is one 88-byte block per 16 slots (5.5-9.5 bytes/slot depending on bucket_type), not one bucket per slot as in 4.x — code carried over from 4.x that computes memory as bucket_count() * sizeof(bucket_type) still compiles but silently gives the wrong number; use index_bytes() instead

**Status:** Actively maintained (last commit 2026-09-23, 1,482 stars, CMakeLists shows current release 5.0.1); MIT-licensed, header-only, and used in production projects including MySQL and PrusaSlicer per doc/users.md.

[repo](https://github.com/martinus/unordered_dense) · [benchmark](https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md)

##### Boost.Unordered (boost::unordered_flat_map)  `C++`  `BSL-1.0`  `active`  `Tier A`

Header-only SIMD open-addressing hash map/set for Boost; unordered_flat_map is 2.7x-11.6x faster than std::unordered_map.

**Beats:** std::unordered_map — On unordered_dense's public bench_readme.sh harness (clang 22.1.8, -O3 -DNDEBUG -std=c++20, transparent huge pages, one pinned core, Fedora 44, AMD Ryzen 9 7950X), boost::unordered_flat_map was 5.00x faster build+destroy, 2.70x faster find, 4.66x faster churn, and 11.60x faster iterate than std::unordered_map (libstdc++, inferred) on uint64_t keys, with 1.55x-32.9x gains on std::string keys.

**How:** Elements sit in groups of 15 slots backed by a 16-byte metadata word (per-slot reduced hash byte plus an overflow byte); SSE2/Neon SIMD scans the whole metadata word in one op to rule out non-matching slots before touching real elements, with quadratic probing to the next group on overflow (non-SIMD architectures emulate this via bit-interleaving). The library also auto-post-mixes ('avalanches') whatever hash function you supply so a poor-quality hash doesn't degrade open-addressing performance, at a small cost you can opt out of by declaring your hash `is_avalanching`.

**Use it when:**
- uint64_t or other cheap-to-hash keys, 1-2M+ entries, throughput-bound build/find/churn/iterate workloads
- Whole-container iteration is common — flat layout iterates 11.6x faster than std::unordered_map on u64 keys
- x86-64 (SSE2) or aarch64 (Neon) targets that benefit from SIMD metadata scanning
- Want boost::unordered_map's near-drop-in API but don't need pointer/reference stability across mutation
- Already use Boost, or can add a header-only dependency with no link step

**Skip it when:**
- Code relies on pointer/reference stability across insert/erase — use boost::unordered_node_map or std::unordered_map
- Memory is tighter than speed: in the same benchmark std::unordered_map had lower peak RSS per u64 entry (45.78 B) than every flat map
- Can't tolerate Boost's transitive include weight — issue #195 flags a large transitive-include graph hurting compile times
- Need concurrent mutation from multiple threads — use boost::concurrent_flat_map instead, unordered_flat_map has no built-in synchronization
- Bulk-loading one flat_map from another already-hashed container via a plain insert loop without reserve() first — open issue #178 documents quadratic insertion in that pattern

**Integration:** header-only · Boost (Boost.Container_hash, Boost.Core, Boost.Config, Boost.Assert and other Boost headers pulled in transitively) · C++11 (CTAD deduction guides need C++17) · any; SIMD-accelerated on x86-64 (SSE2) and aarch64 (Neon), portable bit-interleaved metadata scan elsewhere

**Vs siblings:** Pick Boost.Unordered when you want one vendor for the whole hash-container family (flat/node/concurrent variants, all header-only) rather than a single map type; abseil's absl::flat_hash_map is faster on these exact numbers (5.99x vs 5.00x build+destroy, 2.43x vs 2.70x find) but pulls in more of the Abseil ecosystem, and ankerl::unordered_dense is a smaller single-header option that wins on pure iteration speed but has no concurrent or pointer-stable variants.

**Gotchas:**
- Inserting into a flat_map by iterating another (already hash-ordered) container with plain insert() can degrade to quadratic time; call reserve() first or use the copy constructor instead (open issue boostorg/unordered#178)
- Open addressing is hash-quality sensitive; the library auto post-mixes your hash unless it's tagged `using is_avalanching = std::true_type;`, which skips the safety net for a small speed gain
- erase(iterator) returns a proxy object convertible to an iterator, not an iterator directly — code that assumes the std return type may need adjustment
- value_type must be move-constructible and there's no pointer stability under rehash or node extraction/insertion API (use boost::unordered_node_map if you need those)

**Status:** Actively maintained core Boost module (last commit 2026-06-17); BSL-1.0 licensed and header-only, so it's trivially vendorable despite the standalone module mirror's low star count — it ships inside every Boost install and is used far more broadly than that number suggests.

[repo](https://github.com/boostorg/unordered) · [benchmark](https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md)

##### emhash (ktprime/emhash: emhash5/6/7/8 + emilib)  `C++`  `MIT`  `active`  `Tier A`

Header-only open-addressing C++ hash table family; emhash7 beats std::unordered_map on insert/find/erase/iterate at 10M elements.

**Beats:** std::unordered_map — On an AMD Ryzen 7 5800H / Windows 10, GCC 11.3 (-O3 -march=native -std=c++17) build, emhash7 beat std::unordered_map (libstdc++) at 10M integer-key elements: insert ~4.5x (66.0 vs 295), find-hit ~2x (16.9 vs 33.0), find-miss ~2.9x (18.1 vs 52.0), erase ~14x (20.4 vs 293), and iterate ~85x (0.74 vs 62.6). These are the project's own docs/performance.md numbers, reproducible via bench/ebench but not independently re-run for this entry.

**How:** emhash7 stores key-value pairs inline in one contiguous array plus a separate bitmask for fast empty-slot scanning, and repairs the bucket chain on erase instead of leaving tombstones, so mixed insert/erase workloads don't degrade even at load factor 0.999. Iteration is a straight scan of that array, which is why it beats std::unordered_map's pointer-chasing linked-node layout by roughly 85x on the 10M-element iterate benchmark. The emilib variants instead use Swiss-table-style SIMD group probing with a 1-byte H2 tag per bucket to filter most candidates before a full key comparison.

**Use it when:**
- Mixed insert/find/erase workloads on integer or POD keys where throughput close to hand-tuned open addressing matters (emhash7)
- Need a load factor above 0.9 (up to 0.999) without the clustering/degradation open addressing usually shows at that density
- Iteration-heavy hot paths over the whole map/set (emhash7/emhash8), since the flat array scan beats std::unordered_map's node chasing by an order of magnitude
- Want a header-only, dependency-free drop-in (copy one .hpp) rather than adding a build dependency
- Input keys are trusted/internal, not adversarially chosen

**Skip it when:**
- Code holds long-lived references or pointers into the map across inserts — open addressing invalidates them on rehash; std::unordered_map does not
- Keys come from untrusted/adversarial input: emhash7/8 don't cap probe-sequence length by default, which SECURITY.md flags as a hash-flooding DoS risk unless you enable EMH_SAFE_HASH or switch to an emilib EMH_SAFE_PSL variant
- Multiple threads write concurrently without your own locking — emhash provides no internal synchronization
- You want independently reproduced numbers rather than the vendor's own benchmark (emhash's table is self-measured on one Windows/GCC config, not verified here against Ankerl 2022 or Allan 2024 methodology)
- Very large value types where rehash-driven moves are costly and you haven't wrapped them in unique_ptr

**Integration:** header-only · none (wyhash is bundled in config.hpp; pass -DEMH_NO_BUILTIN_WYHASH to supply your own) · C++17 (some examples use C++20); GCC, Clang, or MSVC · Windows, Linux, macOS; x86-64 and ARM64 (Apple M1/M2). emhash5-8 are scalar (no SIMD requirement); emilib variants add SSE2/AVX2/AVX-512 group probing where available

**Vs siblings:** Pick emhash over rigtorp::HashMap, ska::flat_hash_map, or tsl::robin_map/hopscotch_map when you need a load factor up to 0.999 without tombstone-driven degradation on mixed insert/erase workloads, or want a matched family (emhash6/7/8) tuned per access pattern instead of one fixed design. Pick a sibling instead when you want a single implementation whose speedup was measured by an independent, cross-library suite (e.g. Ankerl 2022) rather than the vendor's own benchmark.

**Gotchas:**
- emhash7/8 do not cap probe-sequence length by default; SECURITY.md calls this a hash-flooding DoS risk on untrusted keys. Mitigate with EMH_SAFE_HASH (~10% overhead) or an emilib EMH_SAFE_PSL variant
- Any insert that triggers a rehash invalidates all existing references and iterators, unlike std::unordered_map's node-based stability
- Erasing inside a plain range-for is undefined behavior; use the iterator-returning erase(it) or erase_if() instead
- Some thirdparty/emilib variants (e.g. emilib2ss) can degrade into a full table scan under an all-keys-collide attack; the maintained include/emilib/emihmap2.hpp (emilib2::HashMap) is not the affected fork, but pick emilib2o/emilib2s for untrusted input regardless

**Status:** Actively maintained (last commit 2026-09-05, v1.1.0) and MIT-licensed; header-only, so a single .hpp such as hash_table7.hpp can be vendored with no external dependency.

[repo](https://github.com/ktprime/emhash) · [benchmark](https://github.com/ktprime/emhash/blob/master/docs/performance.md)

##### folly F14 (F14ValueMap)  `C++`  `Apache-2.0`  `active`  `Tier A`

SIMD 14-way probing hash map (F14) in Facebook's Folly library; 2-4x faster build/find/churn, 16x faster iteration than std::unordered_map.

**Beats:** std::unordered_map — Read directly from martinus/unordered_dense's bench_readme.csv (clang 22.1.8, -O3 -DNDEBUG -std=c++20, libstdc++, AMD Ryzen 9 7950X, 1-2M entries): for u64 keys folly::F14ValueMap beat std::unordered_map 3.97x on build+destroy (29.05 vs 115.31 ns/op; inserts alone 2.81x, 27.98 vs 78.66), 1.72x on find (33.58 vs 57.89), 2.63x on churn (91.34 vs 240.49), and 16.35x on iteration (1.30 vs 21.29 ns/element); for std::string keys the wins were smaller on build/find/churn (1.48x/1.73x/1.62x) but iteration was 29.7x. std::unordered_map had lower peak RSS per u64 entry (45.78 B) than every SIMD/flat map tested, including F14ValueMap.

**How:** Each table position is a 14-slot chunk; F14 packs a 1-byte hash 'tag' per key into a 16-byte SIMD vector (SSE2 on x86_64, NEON on aarch64) so one vector compare filters up to 14 candidate slots per probe, letting the table run at a 12/14 max load factor with a ~1.04 average probe length on hits. Collisions resolve via double hashing with per-chunk 'overflow' reference counts standing in for tombstones, so insert/erase churn doesn't force the periodic full-table rehashes that tombstone-based open addressing needs to reclaim slots. F14ValueMap further stores entries inline in the chunk instead of behind a per-node heap allocation, which is what drives its build and iteration advantage over std::unordered_map's pointer-chasing.

**Use it when:**
- u64 or other small trivially-copyable keys where build/insert and find throughput matter more than reference stability (F14ValueMap or F14FastMap).
- Iteration-heavy workloads: F14ValueMap iterates 16x faster (u64) to 30x faster (std::string) than std::unordered_map on this harness because there's no per-node pointer chasing.
- High churn workloads (caches, dedup tables, repeated insert/erase cycles) where std::unordered_map's tombstone-driven rehashes hurt.
- You need std::unordered_map-compatible reference/iterator stability but still want a speed win over it: use F14NodeMap specifically (1.28x faster build+destroy, still much slower than F14ValueMap in this benchmark).
- You're already building/linking Folly (or accept doing so) on x86-64/aarch64 with a C++20 toolchain.

**Skip it when:**
- You want a header-only, dependency-free drop-in: F14 requires building and linking libfolly, whose manifest lists ~13 external deps (boost, gflags, glog, libdwarf, libevent, libsodium, fast_float, fmt, lz4, openssl, snappy, zstd, xz) plus Linux-only libaio/libiberty/libunwind.
- Targeting WebAssembly: an open folly issue (#1973) reports F14 is slower and more memory-hungry than std::unordered_map there.
- Less-common platforms: open build-failure issues on ppc64le (#1838) and other powerpc targets (#2128) show threading/endianness and compile rough edges; README's platform list (Linux/macOS/Windows/iOS, x86-32/64, ARM) is not the CI-tested set.
- You default to F14ValueMap/F14VectorMap/F14FastMap but need reference/iterator stability across mutation — only F14NodeMap provides that; the others may invalidate references on any insert.
- Exception safety must be contractually guaranteed: an open upstream issue (#2308, filed 2024, still open) states F14's exception safety is undocumented.

**Integration:** static lib · boost, gflags, glog, libdwarf, libevent, libsodium, fast_float, fmt, lz4, openssl, snappy, zstd, xz (googletest for tests only); Linux additionally needs libaio, libiberty, libunwind · C++20 (CMakeLists.txt pins CMAKE_CXX_STANDARD 20), CMake 3.14+, gcc/clang/MSVC · x86-64 (SSE2, a non-optional baseline ISA feature) and aarch64 (NEON) are the vectorized fast paths; a non-SIMD fallback exists but is untested by this benchmark. WASM and some powerpc targets have open correctness/perf issues.

**Vs siblings:** On this exact harness F14ValueMap is the slowest of the four SIMD hash maps compared for u64 keys: abseil's flat_hash_map (19.26 ns/op buildfree), Boost.Unordered's flat_map (23.04), and ankerl::unordered_dense (23.80) all beat F14ValueMap's 29.05, and similarly on find. Pick F14 when you're already building/linking Folly and want the ValueMap-vs-NodeMap choice between raw speed and std-compatible reference stability in one library, or need Folly's built-in heterogeneous/transparent lookup; pick a single-header sibling (unordered_dense, robin_hood) when you want the speed without Folly's ~13-dependency build.

**Gotchas:**
- F14ValueMap/F14VectorMap/F14FastMap may rehash before evaluating an insert's arguments, so code like map.insert(k2, map[k1]) is unsafe with them, per F14.md (same caveat as dense_hash_map and absl::flat_hash_map).
- Debug and ASAN builds intentionally randomize iteration order and inject extra rehashes to expose stability bugs, so two identically-constructed maps can iterate in different orders even in the same process/build.
- clear() frees all backing memory once a table has ever held >100 keys (std only requires O(size())), so a clear-and-refill loop on a table that grew large will repeatedly reallocate rather than reuse capacity.
- Only F14NodeMap provides std::unordered_map's reference/iterator stability; the other three variants can move or invalidate elements on any insert.

**Status:** Actively maintained (commits current as of 2026-09-24, 30.5k stars, heavy internal Meta production use) under Apache-2.0, but folly gives no ABI-compatibility guarantee across commits and its own README recommends static linking and pinning a version rather than tracking main.

[repo](https://github.com/facebook/folly) · [benchmark](https://github.com/martinus/unordered_dense/blob/main/doc/benchmarks.md)

##### google::dense_hash_map (sparsehash)  `C++`  `BSD-3-Clause`  `abandoned`  `Tier A`

Open-addressing C++ hash map beating std::unordered_map on lookups/inserts at large memory cost.

**Beats:** std::unordered_map — On Tessil's independent hash-table shootout (Clang 5.0, -O3 -march=native -DNDEBUG, libstdc++, Intel i5-5200u), google::dense_hash_map beat std::unordered_map in 20 of 21 tests, a ~2.3x geometric-mean speedup, including read_random_full at n=3,000,000 (0.054s vs 0.297s, ~5.5x) and insert_random_full (0.309s vs 1.056s, ~3.4x); its sole loss was insert_string at ~0.90x.

**How:** It stores all key/value pairs inline in one contiguous array (densehashtable.h) using quadratic-probing open addressing, so lookups walk cache lines instead of chasing per-node pointers/allocations the way node-based chaining maps do. A reserved empty-key sentinel marks free slots without a separate occupancy bitmap, and erase() writes a deleted-key tombstone instead of compacting, which avoids iterator invalidation but leaves stale entries until a resize. Confirmed against README.md, the dense_hash_map header, and densehashtable.h in the repo, and against Tessil's independent shootout (Clang 5.0, -O3 -march=native -DNDEBUG, Intel i5-5200u), which measured it fastest in 20 of 21 tests.

**Use it when:**
- Read-heavy workloads with fixed-size keys (integers, pointers, short strings) where lookup latency matters more than memory footprint.
- Data sets that comfortably fit in RAM with headroom to spare for a doubling resize.
- You can carve out two sentinel key values (empty + deleted) that will never appear as real data.
- You can build and run under an older/stable C++ toolchain (GCC/Clang pre-C++20) and pin -DNDEBUG so asserts don't eat the speed gain.
- You're fine vendoring a BSD-3-Clause, unmaintained-since-2020 header set rather than depending on active upstream support.

**Skip it when:**
- Memory-constrained services: README states a 2-4x steady-state overhead, rising to a 6x 'high-water mark' mid-resize (old 2x table plus new 4x table coexist).
- Heavy erase/reinsert cycles near max_load_factor(1): issue #141 shows find() on a missing key can loop forever once every bucket is either occupied or a deleted-tombstone.
- Very large datasets: issue #123 reports dense_hash_map hanging/failing around ~900M entries (16-process distributed job) where std::unordered_map ran fine.
- Element counts that land just below a power of two: issue #172 (open, filed Dec 2025) reports an unresolved, order-of-magnitude slowdown in the 2.0.4 release near power-of-two sizes, absent in 2.0.3.
- String-heavy or variable-length keys, and any build on GCC 11+ with -std=c++20/c++2b: Tessil's shootout shows it losing on insert_string (0.90x vs std::unordered_map), and open PRs/issues (#165, #166) report c++20 build fixes needed and a c++2b segfault in libc_allocator_with_realloc.

**Integration:** header-only · none at the API level, but the build needs autotools (./configure/make install) or an equivalent packaged sparseconfig.h to generate the platform's HASH_FUN_H macro before the headers are usable · C++03/11-era API (tr1-style hash<>); upstream has not verified newer standards - open reports of build failures/segfaults under -std=c++20/c++2b on GCC 11+ · any (README reports Linux, Solaris, FreeBSD, macOS, and Windows/MSVC support, last verified against toolchains circa 2010-2015; pure C++, no SIMD/intrinsics required)

**Vs siblings:** Within the sparsehash family, pick dense_hash_map over sparsepp when you have RAM to spare and want the fastest lookups; sparsepp trades some of that speed for much lower memory and reportedly beats dense_hash_map's stability at very large sizes. Against actively maintained alternatives (tsl::robin_map, ska::flat_hash_map, emhash), dense_hash_map's only real draw is its long-proven quadratic-probing design — those get comparable or better speed without the mandatory empty/deleted-key setup or an unmaintained-since-2020 codebase with open hang/perf-regression reports.

**Gotchas:**
- set_empty_key() must be called right after construction (or passed to the iterator-range constructor) and set_deleted_key() before any erase() call; skipping either, or inserting a key equal to one, causes undefined/mysterious failures per the header comments.
- erase() never reclaims memory or invalidates iterators; repeated erase/insert cycles bloat memory until you call resize(0), and at max_load_factor(1) a fully-occupied table (valid + deleted buckets only) can make find() on an absent key loop forever (issue #141).
- Resizing needs up to 6x the raw entry size as a transient high-water mark (README), so budget memory headroom well beyond the steady-state 2-4x overhead.
- dense_hash_map's disk-serialization methods (write_metadata/write_nopointer_data) are present in the API but unimplemented and always fail — only sparse_hash_map actually supports save/restore to disk.

**Status:** Abandoned since its last commit on 2020-08-12 — the repo has 20+ open issues/PRs including an unresolved December 2025 report of a severe performance regression near power-of-two sizes in the 2.0.4 release; it's BSD-3-Clause and small enough to vendor, but expect friction building under modern C++ standards/compilers.

[repo](https://github.com/sparsehash/sparsehash) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html)

##### robin_hood::unordered_map  `C++`  `MIT`  `abandoned`  `Tier A`

Header-only, single-file open-addressing hash map/set beating std::unordered_map on speed and memory.

**Beats:** std::unordered_map — On the author's 2019 map_benchmark suite (g++ 8.2.0, -O3 -march=native, libstdc++ std::unordered_map as baseline, Intel Core i7-8700 @3.2GHz locked), robin_hood::unordered_flat_map inserted+erased 100M int pairs in 16.9s using 1717MB vs. std::unordered_map's 99.7s / 3986MB (5.9x faster, ~2.3x less peak memory), both using robin_hood::hash; robin_hood::unordered_node_map took 45.5s / 2293MB (2.2x faster). Numbers are first-party, from a 2019-era g++ 8.2/libstdc++ toolchain.

**How:** Open addressing with Robin Hood hashing bounds probe-sequence-length variance, and backward-shift deletion removes the need for tombstones, so there's no per-node allocation or pointer chasing on the hot path. Each slot carries a 1-byte 'info' field packing probe distance plus hoisted hash bits, so most negative lookups are rejected without a full key comparison; the flat layout keeps keys/values contiguous for cache locality. A custom robin_hood::hash (multiply-shift avalanche, specialized fast paths for integers and std::string) is used by default; the node variant additionally uses a bulk pool allocator to avoid per-insert malloc calls. No SIMD is used — it's portable scalar C++ relying on bit-scan intrinsics, not vector instructions.

**Use it when:**
- Hot-path integer- or string-keyed maps/sets where insert/erase/find throughput dominates and you use robin_hood::hash (or another well-mixed hash)
- Large bulk workloads (tens of millions of entries) where std::unordered_map's per-node allocation and pointer chasing dominate runtime and RSS
- You want a drop-in std::unordered_map-shaped API without rewriting call sites: unordered_flat_map for max speed, unordered_node_map when pointer/reference stability is required
- Header-only vendoring is acceptable (single ~2500-line file, MIT) and you're fine freezing on an unmaintained snapshot
- C++11/14/17/20 codebase, including non-x86/non-AVX platforms, since the implementation is portable scalar C++

**Skip it when:**
- You need iterator stability across inserts — neither variant guarantees it, and unordered_flat_map also invalidates references/pointers on rehash
- You rely on a poorly-mixed or identity hash for integer keys (e.g. libstdc++'s default std::hash<int>) — the record's own caveats note robin_hood times out in several benchmarks without its own hash, and a badly mixed hash can make insert throw std::overflow_error
- Your workload spikes memory and then shrinks — unordered_node_map's bulk allocator never returns freed blocks to the OS for the life of the map, so peak RSS persists (GitHub issue #107)
- You need heterogeneous/transparent lookup (e.g. find by string_view into a map<std::string,...>) — attempts to use it hit unresolved problems per an open issue (#80)
- You need active maintenance, custom-allocator support, or a cheap operator= — the repo is archived since 2023 (author recommends ankerl::unordered_dense), custom allocators aren't supported (issue #136, closed unimplemented), and copy-assignment has an open perf bug where it frees then reallocates instead of reusing the buffer (issue #149)

**Integration:** header-only · none (C++ standard library only) · C++11 (header explicitly targets 11/14/17/20; the project's own CMakeLists.txt defaults CMAKE_CXX_STANDARD to 14) · any (portable scalar C++, no SIMD/AVX requirement); README states 'platform independent' and CI badges cover Linux/macOS (Travis) and Windows (AppVeyor)

**Vs siblings:** Pick robin_hood over abseil::flat_hash_map, Boost.Unordered, or folly::F14 when you want a single dependency-free header to vendor and can't pull in Abseil/Boost/Folly; for any new project, the author's own successor ankerl::unordered_dense is the better default since robin_hood is explicitly unmaintained and unordered_dense is the sibling entry it was retired in favor of.

**Gotchas:**
- unordered_node_map's bulk allocator never frees memory back to the OS during the map's lifetime — a one-time size spike leaves RSS elevated until the map is destroyed (issue #107)
- A sufficiently bad/adversarial hash can make insert throw std::overflow_error instead of degrading gracefully like std::unordered_map (README 'Design Choices' section)
- Heterogeneous/transparent lookup via is_transparent hash+equal does not work as expected in practice (issue #80, open)
- copy-assignment (operator=) frees all memory and reallocates from scratch rather than reusing the existing buffer (issue #149, open)

**Status:** Abandoned: the author stopped development (last commit 2023-04-21, repo carries a 'deprecated' issue template) and publicly recommends migrating to ankerl::unordered_dense, but it's MIT-licensed and small enough (one header) to vendor and freeze indefinitely.

[repo](https://github.com/martinus/robin-hood-hashing) · [benchmark](https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-03-01-result-InsertHugeInt/)

##### ska::flat_hash_map / ska::bytell_hash_map  `C++`  `BSL-1.0`  `abandoned`  `Tier A`

Header-only Robin Hood open-addressing hash map/set beating std::unordered_map on lookups, inserts, and erases.

**Beats:** std::unordered_map — Ankerl 2022 (martinus/map_benchmark; clang++13 -O3 -march=native; Intel i7-8700 @3200MHz; libstdc++), normalizing to the same hash function for both sides, measured ska::flat_hash_map at 2.06-2.32x std::unordered_map geometric-mean runtime (number find 2.8-3.6x, string find 1.55-1.95x, random insert/erase 4.0-4.6x, iteration 0.79-0.97x i.e. slightly slower) and ska::bytell_hash_map at 2.12-2.31x geomean (insert-then-erase 4.4-4.6x). The author's own 2017 post claims the fastest lookups he tested, but shows only graphs with no stated compiler or hardware.

**How:** Both use Robin Hood open addressing with backward-shift deletion (no tombstones) and cap worst-case probe length at max(4, log2(bucket_count)), so lookups stay bounded regardless of hash quality. flat_hash_map defaults to a fibonacci hash policy (multiply-shift, no modulo) with a low 0.5 max load factor to keep probe chains short; a power_of_two_std_hash wrapper opts into masking instead. bytell_hash_map keeps the same Robin Hood core but stores per-slot state in packed metadata blocks (a triangular-number jump-distance table) and raises max load factor to 0.9375, trading some speed for a smaller footprint.

**Use it when:**
- Hot lookup/insert/erase paths on int or short string keys, single-threaded, where you control hash quality: Ankerl 2022 shows 2.06-2.32x geomean over libstdc++ std::unordered_map with the same hash.
- Sizes known up front (reserve()-able) with light iteration, since the gain is on insert/erase/find, not on scanning.
- Insert/erase churn workloads, especially with bytell_hash_map (insert-then-erase ~4.4-4.6x vs std::unordered_map) where the 0.9375 load factor also keeps memory tight.
- Small vendorable dependency for game/offline C++11-14 code that can't take on Abseil or a newer-toolchain-only library.
- Trusted, non-adversarial key inputs (internal data, not user-controlled strings from the network).

**Skip it when:**
- Iteration-heavy code: flat_hash_map's iteration is 0.79-0.97x std::unordered_map (Ankerl 2022) and described by that benchmark as one of the slowest tested; memory use is also high.
- bytell_hash_map erase-during-iteration loops: issue #41 reports duplicate elements returned after erase() while iterating; a fix was posted in comments but never merged.
- Builds using -O2 -DNDEBUG with bytell_hash_map: issue #11 reports a 'free(): invalid pointer' SIGSEGV traced to sherwood_v8_block::empty_block()'s static sentinel; unresolved since 2018.
- Untrusted/attacker-influenced keys: no seeded/randomized hashing (issue #17, 'Unsafe with attacker controlled keys'), same exposure as raw std::hash but with nobody patching it.
- Code shared across shared-library/module boundaries: issues #43 and #26 describe static-data (empty_default_table) problems when the header is instantiated in multiple translation units.
- Anywhere you rely on std::unordered_map's iterator/reference stability: backward-shift deletion relocates other elements on erase (issue #30, 'Insert invalidate iterators').

**Integration:** header-only · none beyond the STL (<cstdint> <cstddef> <functional> <cmath> <algorithm> <iterator> <utility> <type_traits>; bytell_hash_map.hpp additionally includes flat_hash_map.hpp, <vector>, <array>) · C++11 (variadic templates, rvalue refs, allocator_traits; ships its own void_t shim rather than relying on C++14/17, so no later standard is required) · any standard C++ target, no SIMD/intrinsics; open issues note past failures on 32-bit ARM (fix referenced in issue #18) and a still-open concern about jump_distances on x86 builds for bytell_hash_map (issue #37)

**Vs siblings:** Pick this over emhash, sparsepp, robin-map, or rigtorp::HashMap when the independent Ankerl 2022 head-to-head numbers (same-hash, normalized geomean) matter more than a vendor's own benchmark, or when you specifically want bytell_hash_map's lower memory overhead (0.9375 load factor) at some cost to lookup/iteration speed. Prefer an actively maintained sibling (e.g. tsl::robin_map, emhash) if you need try_emplace, bucket() semantics, or bug fixes — this repo has had zero commits since 2018-07-15 and 42 open issues, including the correctness/crash bugs above.

**Gotchas:**
- erase() performs backward-shift deletion: elements after the erased slot get moved in memory, invalidating their iterators/references too, not just the erased one's (sherwood_v3_table::erase; issue #30).
- bytell_hash_map: duplicate-item-after-erase bug when erasing during iteration (issue #41), fix posted in comments but never merged.
- bytell_hash_map: reported SIGSEGV under -O2 -DNDEBUG tied to sherwood_v8_block::empty_block()'s static sentinel (issues #11, #14), unresolved.
- No seeded hashing; adversarial keys can force worst-case probing exactly like plain std::hash (issue #17).

**Status:** Abandoned since 2018-07-15 with 42 open issues, including two unresolved correctness/crash bugs specific to bytell_hash_map; declared BSL-1.0 in every header despite GitHub showing no LICENSE file, so it's freely copyable and small enough to vendor and patch yourself.

[repo](https://github.com/skarupke/flat_hash_map) · [benchmark](https://martin.ankerl.com/2022/08/27/hashmap-bench-01/)

##### sparsepp (spp::sparse_hash_map, greg7mdp/sparsepp)  `C++`  `BSD-3-Clause`  `active`  `Tier A`

Header-only open-addressing hash map/set beating std::unordered_map on memory and, per two independent suites, speed.

**Beats:** std::unordered_map — Two independent third-party suites (not the author's own graphs) show spp::sparse_hash_map beating libstdc++'s std::unordered_map: Ankerl 2022 (clang++13, -O3 -march=native, Intel i7-8700) measured geometric-mean speedups of 1.98-2.03x depending on hash choice, with number-find up to 2.51x, but spp timed out on integer insert/erase/find when using an unmixed identity hash. Tessil's 2017 shootout (Clang 5.0 with libstdc++, 200K-3M entries) measured 1.11-3.31x faster successful lookups and 1.15-5.60x faster misses, with inserts ranging 0.61-1.47x (slower than std::unordered_map on string keys).

**How:** Uses Google sparsehash's 'sparsetable' layout: slots are grouped (SPP_GROUP_SIZE, 32 or 64) and each group carries a bitmap (group_bm_type in spp.h) marking which slots are occupied, so mostly-empty regions cost almost nothing to store. Open addressing itself avoids std::unordered_map's per-node allocation and pointer chasing. The README says this layout also keeps the resize memory spike small compared to a plain open-addressing table, though the resize algorithm itself wasn't inspected this session. Integer keys get a built-in bit-mixing default hash to avoid the pathological slowdown that sequential/identity-hashed keys cause on non-present lookups.

**Use it when:**
- Memory-constrained C++ workloads (embedded, large in-memory indexes) where per-entry overhead or resize memory spikes from std::unordered_map/dense_hash_map are the bottleneck
- Integer or string key/value hash tables in the hundreds-of-thousands to ~100M entry range, matching the benchmarked workload
- Projects on pre-C++11 or older MSVC/g++ toolchains that can't take the C++11 requirement of greg7mdp/parallel-hashmap
- Throughput-oriented insert/lookup/erase workloads, not strict latency SLAs, with no need for concurrent writers
- Need built-in binary serialize()/unserialize() of the whole table to a file or stream

**Skip it when:**
- Peak throughput matters most: google::dense_hash_map beats sparsepp on insert, lookup, and delete in the author's own bench.md
- Any C++11+ toolchain is available: the author's README now recommends greg7mdp/parallel-hashmap (or gtl) instead of sparsepp
- Code holds long-lived references or pointers into the map across insert()/erase() — sparsepp invalidates them more aggressively than std::unordered_map
- Code uses a sparse_hash_map/set after moving from it — moved-from tables segfault on further use (issue #83, open, unresolved)
- Hash quality is uncertain (e.g. an unmixed identity hash on integer keys) — spp degrades badly or times out per Ankerl 2022

**Integration:** header-only · none (C++ standard library only) · Works with C++03; C++11 features (move semantics, initializer lists) auto-detected and used if the compiler supports them. Tested on VS2010-2015, g++, clang++. · Windows, Linux, macOS; x86/x64, no SIMD required. Compiler/platform detection macros derived from Boost for portability.

**Vs siblings:** Pick sparsepp over google::dense_hash_map when the final table size is unknown and you can't absorb dense_hash_map's larger resize memory spike; pick it over tsl::robin_map/ska::flat_hash_map/emhash mainly when stuck on a pre-C++11 toolchain, since for any C++11+ project the author's own README recommends parallel-hashmap (not sparsepp) over those newer designs too.

**Gotchas:**
- Moved-from sparse_hash_map/set is left in an inconsistent state; calling find() or other operations on it segfaults (issue #83, open as of 2026-09-23; author's own workaround suggestion is to switch to parallel-hashmap)
- insert()/erase() can invalidate references and pointers to stored values, unlike std::unordered_map where references survive unless a rehash occurs
- Default integer hash does bit-mixing to dodge sequential-key pathologies; a user-supplied hash with similar low-order bits across keys needs the SPP_MIX_HASH macro or collisions increase
- Copy construction/assignment is slow relative to the baseline (per verification caveats)

**Status:** Actively maintained (last commit 2026-09-19, BSD-3-Clause, 1311 stars, not a fork or archived) but the author's own README now steers users to greg7mdp/parallel-hashmap for any C++11+ project, calling it a better speed/memory trade-off than sparsepp.

[repo](https://github.com/greg7mdp/sparsepp) · [benchmark](https://martin.ankerl.com/2022/08/27/hashmap-bench-01/)

##### tsl::hopscotch_map (Tessil/hopscotch-map)  `C++`  `MIT`  `active`  `Tier A`

Header-only C++17 hopscotch-hashing hash map/set, faster than std::unordered_map with dense_hash_map-like speed.

**Beats:** std::unordered_map — Against std::unordered_map (libstdc++, Clang 5.0, -O3 -march=native -DNDEBUG, Intel i5-5200u/8GB RAM/Linux 4.11), the author's benchmark (200K-3M entries, int64 identity-hash and 15/50-char string keys) found hopscotch_map faster in every measured case: 1.08-2.67x on insert, 1.51-5.47x on successful/unsuccessful lookup, 1.55-10.1x on erase, and 4.6-13.2x on iteration.

**How:** Hopscotch hashing keeps every key within a fixed-size neighborhood (bitmap) of its ideal bucket, so a lookup only scans a small, cache-local run of buckets instead of following a chain; neighborhoods are rearranged on insert to preserve this bound. Elements are stored contiguously via open addressing, avoiding the per-node heap allocation std::unordered_map's separate chaining requires. The default power-of-two growth policy replaces modulo with a bitmask; a prime growth policy (_pg variants) is offered when the hash has weak low-bit entropy, at some speed cost. Optional hash caching (StoreHash) and passing a precalculated hash into find() avoid recomputing hashes on rehash/lookup.

**Use it when:**
- Read-heavy workloads (successful/unsuccessful lookup, iteration) with int64 or short-to-medium string keys, in the low-hundred-thousands to low-millions element range (benchmarked at 200K-3M).
- You want a near-drop-in replacement for std::unordered_map without adopting its chained-bucket allocation overhead, and can require C++17 and header-only integration.
- You want dense_hash_map-like throughput but without reserving sentinel/deleted-key values or accepting dense_hash_map's more restrictive API.
- You control the hash function well enough to avoid low-bit collisions, or are willing to switch to the _pg (prime growth) variant if you can't.
- You need optional worst-case DoS resistance (bhopscotch_map/set) for keys that are LessThanComparable, at a throughput cost.

**Skip it when:**
- Identity or otherwise weak hash functions on adversarial/clustered-bit-pattern keys with the default power-of-two policy: the independent Ankerl 2022 suite reports hopscotch timing out on random insert/erase with identity std::hash.
- Code that depends on std::unordered_map's iterator/reference stability across insert: hopscotch invalidates all iterators and references on any insert (only erase preserves them).
- Move-only value types whose move constructor isn't noexcept: not supported, since rehash needs the nothrow guarantee under open addressing.
- Code relying on bucket-introspection methods (bucket(), bucket_size(), etc.): not implemented.
- Inserting implicitly-converted move-only pairs (e.g. a derived-class unique_ptr into a base-class-keyed map) via the generic insert(P&&) overload: open bug #66, a regression after PR #63, still open as of 2026-09-23.

**Integration:** header-only · none for the library; Boost Test is needed only to build the test suite · C++17-compliant compiler · architecture-agnostic; the headers read include only standard library headers, no SIMD intrinsics or platform-specific code observed

**Vs siblings:** Pick hopscotch_map over robin_map/ska/emhash when you want the bhopscotch_map DoS-resistant option or heterogeneous lookups with dense_hash_map-like throughput and lower memory than dense_hash_map; robin-hood-style siblings (robin_map, ska::flat_hash_map, emhash) tend to edge it out on raw insert throughput in independent benchmarks.

**Gotchas:**
- Insert/emplace invalidate all iterators and references, unlike std::unordered_map's node-based stability; only erase is safe.
- it->second is not assignable; iterators dereference to const std::pair, so mutate via it.value() = ...
- Default growth policy is power-of-two; a hash with poor low-bit entropy causes heavy collisions — check overflow_size() and switch to the _pg (prime) variant if it's nonzero.
- Open issue #66: insert(P&&) is broken for implicitly-convertible move-only pairs (e.g. derived-to-base unique_ptr), a regression introduced after PR #63 and unresolved at time of writing.

**Status:** Actively maintained (last commit 2025-11-02) under MIT; small and header-only enough to vendor, but requires C++17 and currently has one open correctness bug (#66) in a move-only insert overload.

[repo](https://github.com/Tessil/hopscotch-map) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html)

##### tsl::ordered_map (Tessil/ordered-map)  `C++`  `MIT`  `active`  `Tier A`

Insertion-order-preserving hash map/set beating std::unordered_map on inserts, misses, and iteration.

**Beats:** std::unordered_map — Author-run benchmark (Tessil hash-table-shootout, tsl::ordered_map v0.4) on an Intel i5-5200u/8GB RAM/Linux 4.11 with Clang 5.0 -O3 -march=native -DNDEBUG, against libstdc++'s std::unordered_map: inserts 1.12-2.87x faster, unsuccessful lookups 2.34-4.40x faster, iteration 22-45x faster, successful lookups mixed at 0.55-2.02x, and about 84MB vs 126MB memory at 3M int64 entries.

**How:** Open addressing with linear robin hood probing plus backward shift deletion keeps probe sequences short and avoids tombstones, which speeds inserts and unsuccessful lookups relative to libstdc++'s node-based std::unordered_map. Storing values contiguously in a deque/vector instead of scattered nodes gives cache-friendly, pointer-chasing-free iteration, which is where the largest measured gains appear (22-45x). The tradeoff is an O(bucket_count) ordered erase() unless the O(1) pop_back()/unordered_erase() variants are used, which break insertion order.

**Use it when:**
- Insert- and miss-heavy workloads on int64 or short/medium string keys, where 1.12-2.87x (inserts) and 2.34-4.40x (unsuccessful lookups) gains were measured
- Need for insertion-order iteration (config/JSON-like objects, ordered dictionaries) that std::unordered_map cannot provide at all
- Iteration-heavy code paths (serialization, dumping, full-container walks) - 22-45x faster than std::unordered_map in the cited shootout
- Memory-constrained multi-million-entry containers (about 84MB vs 126MB at 3M int64 entries in the cited benchmark)
- C++11-only toolchains that need a header-only, dependency-free drop-in with no build step

**Skip it when:**
- Erase-heavy workloads that must preserve order: erase() is O(bucket_count); only unordered_erase()/pop_back() are O(1) and they break ordering
- Read-heavy workloads dominated by successful lookups: measured only 0.55-2.02x vs std::unordered_map, sometimes slower (e.g. read_random_shuffle_range)
- Code relying on bucket-level APIs (bucket(), bucket_size(), ...): not supported
- Decisions needing current-version confidence: the cited numbers are from v0.4 (2017) on an old i5-5200u laptop, not part of the newer Ankerl 2022 suite, and ordered_map is absent from the benchmark page's main charts
- Containers needing more than 2^32-1 values without raising the IndexType template parameter

**Integration:** header-only · none (Boost Test only needed to build the test suite) · C++11 (tested with GCC 4.8.4, Clang 3.5.0, Visual Studio 2015); C++20 required only for the optional module build · any (portable C++11, no SIMD/arch-specific requirement)

**Vs siblings:** Pick tsl::ordered_map over the other cataloged std::unordered_map beaters (hopscotch_map, robin_map, ska flat/bytell, emhash, sparsepp, rigtorp/HashMap, libcuckoo, Verstable, dense_hash_map) when insertion-order iteration is a hard requirement - it is the only one of these that preserves order. Those siblings generally win on raw insert/lookup throughput but give no ordering guarantee at all.

**Gotchas:**
- erase() is O(bucket_count); use unordered_erase()/pop_back() for O(1) removal, but this breaks insertion order
- Iterators expose const std::pair<Key,T>; modify values through it.value(), not it->second
- operator==/!= are order-dependent: two containers with identical key/value pairs inserted in different order compare unequal
- Default IndexType caps the container at 2,294,967,295 (2^32-1) values; raise the IndexType template parameter for larger sizes

**Status:** Active (last commit 2026-06-13, CI passing, MIT-licensed); header-only form makes it trivial to vendor and keep working even if upstream maintenance later lapses.

[repo](https://github.com/Tessil/ordered-map) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html)

##### tsl::robin_map (Tessil/robin-map)  `C++`  `MIT`  `active`  `Tier A`

Header-only robin hood open-addressing hash map/set beating std::unordered_map on insert, lookup, erase, and iteration.

**Beats:** std::unordered_map — Author-run benchmark (Clang 5.0, -O3 -march=native -DNDEBUG; Intel i5-5200u, 8GB RAM, Linux 4.11 x64; libstdc++) across 200K-3M entries with int64_t and 15/50-char string keys found robin_map faster than std::unordered_map in every measured case: inserts 1.08-3.63x, successful lookups 1.55-5.34x, unsuccessful lookups 1.66-6.57x, erase 1.58-13.5x, iteration 2.6-5.3x. The independent Ankerl 2022 suite puts the geometric-mean advantage around 2.4x, but in that same suite robin_map times out on random insert/erase with an identity std::hash and iterates slower (0.80-0.92x) than std::unordered_map.

**How:** Robin hood hashing with linear probing keeps entries close to their ideal bucket, so lookups scan a short, cache-resident run instead of chasing pointers through separate chaining nodes. Erase uses backward-shift deletion (no tombstones), which keeps probe sequences short after deletes. Optional per-entry hash caching (StoreHash) and a precalculated_hash parameter let callers skip recomputing hashes on rehash or lookup when the hash or key-equality function is expensive.

**Use it when:**
- int64_t or other cheap-to-hash keys where you supply a decent hash (not the identity std::hash) and want faster inserts/lookups/erases than std::unordered_map
- std::string keys, especially short (SSO-sized) strings, where robin_map's automatic hash caching gives a large insertion win
- workloads dominated by successful/unsuccessful lookups or full-table iteration at sizes from ~200K to several million elements
- code that needs heterogeneous lookup (find by a different-but-comparable type) or binary serialize/deserialize of the table
- environments where -fno-exceptions or TSL_NO_EXCEPTIONS is desired; the library supports exception-free builds via std::terminate

**Skip it when:**
- pointer/reference/iterator stability across modification matters: open addressing invalidates all of them on any insert, erase, or rehash, unlike std::unordered_map
- keys hashed with the default identity-like std::hash for integers combined with the default power-of-two growth policy: linear inserts can trigger exponential storage growth (GH issue #39); switch to robin_pg_map/robin_pg_set or supply a better hash
- code that erases elements while iterating and depends on visiting each element exactly once: backward-shift deletion can revisit an already-seen element (GH issue #20, open, no fix planned)
- memory-constrained int64 workloads at large scale: at 3M entries the author's own CSV shows ~202MB for robin_map vs ~126MB for std::unordered_map (~1.6x)
- key/value types that are not swappable or not copy/move constructible, or where you rely on std::unordered_map's bucket-inspection API (bucket(), bucket_size(), etc.), which robin_map omits

**Integration:** header-only · none for the library; Boost Test only needed to build the test suite · C++17 (README: "should work with any C++17 standard-compliant compiler") · portable C++17, no SIMD or arch-specific intrinsics in the source; CI covers Linux and macOS (GCC and Clang) and Windows (MSVC via Visual Studio 2025, x64 and x86)

**Vs siblings:** Prefer tsl::robin_map over ska::flat_hash_map/bytell_hash_map or sparsepp when you want an actively maintained, documented library with heterogeneous lookup, binary serialization, and a built-in prime-growth fallback (robin_pg_map) for weak hashes. Prefer tsl::hopscotch_map instead when erase-heavy iteration or memory density at high load factor matters more than raw lookup/insert throughput, since hopscotch avoids robin-map's backward-shift erase cost and identity-hash growth pathology.

**Gotchas:**
- Any insert, erase, or rehash invalidates all iterators, pointers, and references into the table (stricter than std::unordered_map).
- Default power-of-two growth policy + a poor/identity hash (common for std::hash<integral>) can make a linear insertion sequence blow up storage exponentially; use robin_pg_map/robin_pg_set or a stronger hash.
- erase(iterator) walks forward to the next nonempty bucket to return a valid iterator, which is O(expensive) at low load factor; use void erase_fast(iterator) when you don't need the returned iterator.
- Iterating while erasing can visit one element twice due to backward-shift deletion wrap-around; open upstream issue (#20) since 2019, maintainer's stance is 'that's the way it is'.

**Status:** Actively maintained (last commit 2026-06-13, 1508 stars, CI green across GCC/Clang/MSVC), MIT-licensed and header-only, so it is trivially vendorable even if upstream development ever stopped.

[repo](https://github.com/Tessil/robin-map) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html)

##### Verstable  `C`  `MIT`  `stale`  `Tier A`

Single-header C hash table beating std::unordered_map on lookups, erasures, and iteration; insertion only average.

**Beats:** std::unordered_map — On the author's own interactive benchmark (GCC 13.2.0 via MinGW-w64, -O3 -DNDEBUG, AMD Ryzen 7 5800H at 90% locked frequency, libstdc++'s std::unordered_map as baseline, across 32-bit int, 64-bit-int/large-value, and string-key workloads), the page states std::unordered_map is far slower than most open-addressing tables except at looking up existing keys, and at least an order of magnitude slower at iteration; Verstable is described as having extremely fast lookups and erasures of nonexisting keys, iteration beaten only by boost::unordered_flat_map, emilib2, and contiguous-storage tables (and faster than absl::flat_hash_map on iteration), but 'only average' insertion speed. Results are shown as interactive charts rather than a numeric table.

**How:** It's open addressing with quadratic probing, but colliding keys that hash to the same 'home bucket' are linked into a chain via an 11-bit displacement value; a 1-bit flag keeps each chain rooted at its home bucket by evicting non-belonging occupants on insert. This chain metadata, plus a 4-bit hash-code fragment per bucket, lives in a separate uint16_t array instead of alongside the key/value, so lookups can skip most non-matching keys without touching the buckets array or calling the comparison function, and iteration walks a compact metadata array rather than sparse, cache-missing buckets. Deletion and insertion move at most one existing key and require no tombstones. The author describes it as a hybrid of open addressing and separate chaining, related to Malte Skarupke's Bytell table and classic coalesced hashing.

**Use it when:**
- C code that needs a generic, type-safe hash map/set without hand-rolling one, or C++ code that can call a C API via extern "C"
- Lookup- and iteration-heavy workloads, including lookups of nonexisting keys, where std::unordered_map's node-based layout causes cache misses
- Large keys/values or expensive hash/compare functions, since insert/delete move at most one existing key instead of shifting many (unlike Robin Hood schemes)
- High load factors, since the design is described as largely impervious to load factor for lookup speed
- Willing to vendor a single header and accept a non-STL API in exchange for speed

**Skip it when:**
- Need a true drop-in std::unordered_map replacement with C++ container semantics, allocator/exception conventions, or STL iterator guarantees
- Insertion throughput is the dominant cost: the benchmark author calls Verstable's insertion 'only average', and it sits behind absl/boost on raw speed generally
- Keys with a weak, low-entropy, or attacker-influenced hash function: a bucket's collision chain is capped at ~2,048 keys, and hitting that repeatedly makes the table grow until it exhausts memory instead of degrading to a linear scan
- Targeting an FPU-less embedded platform: the default max-load-factor check uses floating point (open issue #23 asks for an integer-only option)
- Need active upstream maintenance guarantees: last commit 2025-05-06, tagged 'stale' by the catalog

**Integration:** header-only · none (C standard library only; malloc/free by default, both overridable) · C99 (with explicit HASH_FN/CMPR_FN); full vt_*-generic macro API requires C11 _Generic; tested under GCC, Clang, MinGW, and MSVC; usable from C++ via extern "C" · not documented as architecture-restricted (portable C, no SIMD intrinsics in the header); an open issue notes the floating-point load-factor check is awkward on FPU-less embedded hardware

**Vs siblings:** Pick Verstable when the code is C (or C++ that can bind to a C ABI) and you want a single-header, type-safe table with tombstone-free deletion and strong lookup/iteration speed; the sibling C++-only tables (ska::flat_hash_map/bytell_hash_map, tsl::robin_map, tsl::hopscotch_map) use similar open-addressing ideas but require a C++ compiler, and emhash/emilib2/google::dense_hash_map generally edge it out on raw insertion or peak throughput if a C-only API isn't a requirement.

**Gotchas:**
- Insert, get_or_insert, erase, erase_itr, reserve, and shrink invalidate all existing iterators; use erase_itr's return value to keep iterating while deleting
- No RAII: forgetting to call NAME_cleanup leaks the table's memory (a reported 'stuck insert' bug turned out to be missing cleanup across repeated runs, per issue #22)
- A degenerate hash function (near-constant output) can make a bucket chain exceed its ~2,048-key limit, causing the table to keep doubling until allocation fails rather than falling back to a slow linear scan
- Custom allocators need CTX_TY plus matching MALLOC_FN/FREE_FN signatures that take a size and context pointer, not a drop-in std::allocator interface

**Status:** Maintenance status is 'stale' (last commit 2025-05-06), but it's MIT-licensed and a single vendorable header, so freezing at the current commit carries little risk; the bigger adoption cost is its non-STL API rather than staleness.

[repo](https://github.com/JacksonAllan/Verstable) · [benchmark](https://jacksonallan.github.io/c_cpp_hash_tables_benchmark/)

##### libcuckoo (cuckoohash_map, efficient/libcuckoo)  `C++`  `Apache-2.0`  `active`  `Tier B`

Header-only concurrent cuckoo hash map with per-bucket locks; beats std::unordered_map only under real multi-core contention.

**Beats:** std::unordered_map — On a 16-core machine the EuroSys'14 paper reports ~40M inserts/sec and ~70M lookups/sec; Figure 1 (4-core Intel i7-4770 Haswell, 120M 8-byte-key/8-byte-value pairs, 1:1 read:write) places libcuckoo well above C++11 std::unordered_map, but the only explicit numeric multiplier given in text is 'up to 2.5x' vs Intel TBB concurrent_hash_map — the std::unordered_map comparison is visual-only in the figure, and the paper treats std::unordered_map as a single-writer table (run under a global or TSX lock), so the measured win is multi-core scalability, not single-threaded op speed.

**How:** Uses cuckoo hashing: each key maps to 2 candidate buckets of SLOT_PER_BUCKET=4 slots, so a lookup touches at most 2 cache lines and displacement chains stay short. Concurrency comes from fine-grained per-bucket spinlocks combined with a resize counter/versioning scheme (the EuroSys'14 optimistic-locking design), letting many writers and readers operate on different buckets simultaneously instead of serializing on one table-wide lock the way std::unordered_map does under concurrent access.

**Use it when:**
- Multi-threaded workloads with genuine concurrent inserts and lookups across several cores (paper measures gains at 4-16 cores, 1:1 read:write and mixed operation mixes).
- Fixed-shape, trivially hashable keys/values (paper benchmark uses 8-byte key/8-byte value, ~120M entries) where the 2-cache-line cuckoo probe pays off.
- Code that can adopt a non-STL API (out-parameter find, functor-based update/upsert) instead of std::unordered_map's interface.
- Workloads that need occasional safe bulk iteration via locked_table(), not concurrent iteration.
- C++11-capable toolchain on Linux/macOS; header-only, so easy to vendor into a build with no link step.

**Skip it when:**
- Single-threaded or low-contention use: the per-bucket spinlock/version machinery is pure overhead with no payoff.
- Memory-constrained settings: users report roughly 3x higher RSS than std::unordered_map for long-key/int-value maps at ~42M entries (issues #134, #136).
- Many reader threads hammering the same hot keys: open issue #159 reports spinlock contention degrading badly past ~16-64 threads, since even find() takes the bucket spinlock (no shared/exclusive mode).
- Code relying on std::unordered_map's free iterators or erase-while-iterating: normal access has no standalone iterators, only locked_table() does, and that locks the entire table.
- Scaling requirements beyond what's measured: the peer-reviewed numbers stop at 16 cores, and at least one independent report (issue #152) found scalability collapsing beyond ~16 threads in their own workload.

**Integration:** header-only · none (self-contained headers: cuckoohash_map.hh, bucket_container.hh, cuckoohash_config.hh, cuckoohash_util.hh; optional C wrapper in libcuckoo-c/) · C++11; clang++ >= 3.3 or g++ >= 4.8 per README (latest versions recommended for atomics support); CMake >= 3.1.0 needed only to build tests/examples · Tested on macOS >= 10.8 and Ubuntu >= 12.04 (README); no stated architecture restriction, plain std::atomic used, no SIMD/intrinsics observed in the header; Windows build status is an open/unclear question (issue #62)

**Vs siblings:** All catalogued siblings (emhash, dense_hash_map, rigtorp/HashMap, Verstable, sparsepp, hopscotch/ordered/robin-map, ska::flat_hash_map/bytell_hash_map) are single-threaded tables tuned for single-core cache behavior and are not safe for concurrent access without an external lock. Pick libcuckoo over any of them only when multiple threads genuinely insert into and look up the same map concurrently.

**Gotchas:**
- find(key, val) (bool-returning, out-parameter) and find(key) (returns mapped_type or throws std::out_of_range) are different overloads; there is no iterator/end() sentinel on the normal concurrent path.
- Automatic expansion throws load_factor_too_low if load factor falls below minimum_load_factor() (default 0.05) — a weak hash function or adversarial key set can trigger this.
- Bulk/STL-style iteration requires locked_table(), which takes an exclusive lock over the whole table for as long as it's held, blocking every other thread.
- Reported ~3x memory overhead vs std::unordered_map for 8-byte-key/4-byte-value workloads at scale (issues #134, #136); size capacity planning accordingly.

**Status:** Active (last commit 2026-07-31, 1747 stars); Apache-2.0, header-only, and small enough to vendor directly into a project (usability: copyable).

[repo](https://github.com/efficient/libcuckoo) · [benchmark](https://www.cs.princeton.edu/~mfreed/docs/cuckoo-eurosys14.pdf)

#### io-and-filesystem

##### reckless  `C++`  `MIT`  `abandoned`  `Tier A`

Asynchronous C++ logging library, drastically lower caller-side latency than std::fstream/fprintf and other async loggers.

**Beats:** std::fstream, fprintf (stdio) — First-party benchmarks (doc/performance.md, gcc 7.3.0, AMD Ryzen 7 2700X @3.7GHz, libstdc++) show reckless's caller-side latency far below std::fstream (flushed per line) and fprintf (fflush per call): about 41-44x lower under light periodic load, and up to ~5720x lower than fstream in the disk-I/O scenario, though this compares an async design against baselines that synchronously flush every line, not raw I/O throughput.

**How:** Call site only pushes args onto a lockless MPSC ring buffer (mpsc_ring_buffer.hpp) shared with the writer thread, so the common case costs about one function call with no kernel transition, no lock, and no formatting or I/O on the caller's thread. Formatting and writing happen entirely on the background thread, and bursts of queued entries are batched into fewer I/O operations. Uses a home-grown float-to-string routine (template_formatter) instead of the standard library's, trading some accuracy for speed.

**Use it when:**
- Latency-sensitive hot paths that log frequently but can tolerate async/eventual persistence
- Single-threaded or lightly-threaded workloads where formatting cost on a shared background thread won't bottleneck
- Windows or Linux targets on x86-family hardware; C++11-only codebases
- Willing to vendor/pin an unmaintained MIT library instead of using an actively developed logger
- Need low overhead specifically vs. synchronous std::fstream/fprintf-with-flush logging

**Skip it when:**
- Need macOS/BSD support (README: OS X unsupported, BSD only 'on the roadmap')
- High log-argument volume from many parallel threads, since all formatting funnels through one background thread (README calls this out as a scalability limit)
- Passing pointers/references to short-lived data without ensuring they outlive the flush (dangling-pointer risk by design)
- Need guaranteed-precise float formatting: custom float-to-string algorithm mismatches the exact/shortest round-trip representation for roughly 0.6% of values per the manual's own stats
- Want an actively maintained project: last commit 2021-04-10, open ThreadSanitizer data-race report (#35) unresolved

**Integration:** static lib (built via Make/CMake/Visual Studio; not header-only) · pthread (POSIX threads) on Linux; no other third-party deps for core library · C++11 (CMakeLists.txt sets CMAKE_CXX_STANDARD 11); GCC-compatible compiler or MSVC/Visual Studio · Windows and Linux only; no macOS/OS X, BSD listed as roadmap-only; no stated architecture restriction beyond x86 cache-line-size assumptions in the buffer sizing docs

**Vs siblings:** No siblings catalogued yet in this category target std::fstream/fprintf directly the way reckless does; CPath and FastReader address filesystem traversal and file reads, not logging, so they aren't substitutes for this use case.

**Gotchas:**
- Passing log arguments by pointer/reference requires the referenced data to stay valid until the log is flushed or closed; prefer std::string/shared_ptr/unique_ptr for dynamic data
- Crash safety requires explicit handling (panic_flush/crash_handler) since unflushed async data can be lost on crash, same class of issue as buffered fprintf but easier to overlook
- Custom float-to-string formatter is not always the shortest round-trip representation: manual reports 98.5% exact match and 99.4% correct-but-sometimes-longer over 100M random values
- worker_thread() exposes the internal std::thread for OS-level tuning (priority/affinity) but destructive operations on it (move/detach) will break the logger

**Status:** Abandoned: last commit on master 2021-04-10, no newer maintenance activity found; MIT licensed and small enough to vendor, but an unresolved ThreadSanitizer data-race report (#35) and a still-open VS2019 compile-error issue (#45) are unpatched.

[repo](https://github.com/mattiasflodin/reckless) · [benchmark](https://github.com/mattiasflodin/reckless/blob/master/doc/performance.md)

#### math-simd-linear-algebra

##### FastMath C++ Library (fast_math_cpp)  `C++`  `MIT`  `active`  `Tier A`

Header-only float math library beating glibc's <cmath> on composed functions (sinh, tanh, atan2, integer pow), not raw trig or exp/log.

**Beats:** <cmath> single-precision (float) overloads (std::sinh, std::tanh, std::atanh, std::atan2, std::pow, std::acos, std::log10, std::tan, std::exp, std::log, etc.), backed by glibc libm (sinhf, tanhf, ...) — Scalar float calls, both sides built with identical flags (-O3 -march=native -funroll-loops), best of 25 interleaved runs of 1,000,000 calls, on WSL2 x86_64 GCC 11.4 (no CPU model stated) and Raspberry Pi 4 GCC 12.2 against glibc's float <cmath>: composed functions like sinh (2.96x/3.94x), tanh (2.94x/3.91x) and integer pow (2.02x/4.54x) win; exp/log/log2/sqrt sit at parity (0.94x-1.01x) because they forward to std::; scalar sin/cos/sincos on wide angle ranges lose on ARM (0.63x-0.82x). A separate batch/array API for sin/cos/sincos/atan2 reached up to 6.16x (atan2) over a std:: loop on x86 and 3.48x on the Pi.

**How:** The scalar wins come from composing sinh/tanh/atanh/asinh/acosh/log10 directly out of std::exp/std::log rather than calling glibc's own (non-table-based) composed routines, plus binary exponentiation for pow(base,int). An FP-register rounding trick (add/subtract 1.5*2^23 to a float) gets the integer part needed for exp's and the angle reduction's range folding without crossing to the general-purpose register file. Where glibc already uses lookup tables (exp, log, log2, sqrt), the library forwards to std:: instead of trying to beat it with a polynomial. The batch API's speed comes from SIMD (GCC vector extensions compiling to SSE on x86 / NEON on aarch64) processing 4 floats per iteration, amortizing the call overhead and branches that dominate scalar timings.

**Use it when:**
- Scalar composed functions on floats: sinh/cosh/tanh/asinh/acosh/atanh/log10 -- 1.2x-4.5x over glibc, wider margin on ARM than x86
- Squared or small-integer-power distances: pow(base, int) is 1.5x-4.5x faster than std::pow via the explicit int overload
- Array workloads (lidar scans, particle sets): batch sin/cos/sincos/atan2, 2x-6.2x over a std:: loop depending on platform and function
- Scalar sin/cos/sincos on angles already normalized to [-pi, pi], where this ties or slightly beats std on both platforms
- Header/robotics C++17 codebases already tolerant of float precision that want one namespace instead of mixing FastMath:: and std::

**Skip it when:**
- exp, log, log2, sqrt, or pow with a fractional exponent -- these are thin std:: forwarders, switching buys nothing
- Scalar sin/cos/sincos on angles still needing range reduction ([-2pi,2pi]) on ARM -- measured slower than std (0.63x-0.82x on Pi)
- Anywhere double precision is needed -- the API is float-only, no double overloads exist
- Builds that require -ffast-math -- the library's rounding trick and inf/NaN/signed-zero contracts break under -ffinite-math-only, so it errors out rather than compiling silently wrong
- Dependencies where maintainer bus-factor matters -- 2 GitHub stars, single author, no issues or PRs filed to gauge responsiveness

**Integration:** static lib (default) or shared lib (CMake FAST_MATH_BUILD_SHARED_LIBS option) -- despite the README's 'Header-Only Design' claim, include/fast_math.hpp only declares functions; definitions live in src/fast_math.cpp and src/fast_math_batch.cpp and must be built/linked via CMake add_subdirectory + target_link_libraries · none for the library itself; GoogleTest required only to build the test target (BUILD_TESTS=ON by default, disable with -DBUILD_TESTS=OFF to skip the GTest dependency) · C++17, CMake 3.16+; CI builds with GCC 11 and Clang 15 · x86_64 and aarch64 (Raspberry Pi 4 / Cortex-A72) directly benchmarked; README badge also claims macOS/Windows but GitHub Actions CI only runs ubuntu-latest, so those are untested claims

**Vs siblings:** Pick this over VDT, SLEEF, fmath, or trigno_simd_cpp when the workload is scalar, float-only composed math (sinh/tanh/atan2/integer pow) rather than raw vectorized double trig or bulk elementwise arrays -- those siblings post larger, more consistent multiples (VDT 4.7x-12.8x on double exp/sin, SLEEF/fmath on vectorized batches), but fast_math_cpp is the only one of this set that documents where it loses (exp/log/sqrt/fractional pow at parity, ARM scalar sin/cos regressing on wide angles) rather than only showing wins.

**Gotchas:**
- CMakeLists.txt has a stray add_library(mcl::map ALIAS fast_math_cpp) -- looks like a leftover from a robotics 'MCL' (Monte Carlo Localization) template this was extracted from; harmless but a sign of how small/informal the project is
- -ffast-math is deliberately rejected by the build -- it silently breaks the FP-register rounding trick (folds (v+magic)-magic back to v), so the library errors out at compile time rather than returning wrong answers under it
- log, log2, asinh-family etc. return a sentinel (-1e38f) for out-of-domain input instead of -inf/NaN like std:: -- a behavioral difference from the baseline being replaced
- sqrt() returns 0 for non-positive input instead of NaN/domain-error like std::sqrt -- another silent semantic deviation

**Status:** Active (last commit 2026-07-28), MIT-licensed, small enough to vendor -- but a very small personal project (2 stars, no issues or PRs filed, single named author), so verify it still builds against your toolchain before depending on it.

[repo](https://github.com/hijimasa/fast_math_cpp) · [benchmark](https://github.com/hijimasa/fast_math_cpp/blob/main/README.md)

##### trigno_simd_cpp (SIMD trigonometric approximations, Goyal & Arora)  `C++`  `Apache-2.0`  `active`  `Tier A`

Piecewise rational sin/cos/tan approximation using AVX2 FMA plus a fast inverse-sqrt hack; beats scalar libm sin/cos/tan.

**Beats:** <cmath> std::sin, std::cos, std::tan — arXiv 2502.10831 (Goyal & Arora) measured mean speed-up vs 'inbuilt' std::sin/cos/tan of 5.49x/5.52x/4.44x over 1000 random angles in [-1e6, 1e6] (seed 2024873), each called 1e5 times through a function pointer, built with g++ -std=c++17 -mavx2 -mfma -O3 -march=native on an AMD Ryzen 9 5900HX under Windows/MinGW-w64. This is scalar per-call latency against the MinGW CRT libm, not glibc, and not array/batch throughput.

**How:** Replaces libm's accurate but branchy range reduction and polynomial/CORDIC evaluation with a cheap piecewise rational fit: angle reduction picks 1 of 7 precomputed coefficient sets (SinHelperParams/CosHelperParams/TanHelperParams), then computes (linear numerator) * fastInverseSqrt(quadratic denominator) via AVX2 FMA (_mm256_fmadd_pd). The reciprocal-sqrt step uses a Quake III-style fast inverse square root (magic constant 0x5fe6eb50c7b537a9 plus one Newton-Raphson refinement) instead of hardware division or sqrt, trading accuracy for fewer cycles.

**Use it when:**
- Scalar sin/cos/tan calls where ~3-4 significant digits (max rel error ~0.004; tan max abs error 0.27 near asymptotes) is acceptable, e.g. graphics, audio, game logic, DSP.
- x86-64 targets with AVX2+FMA, or FPGA/HLS synthesis (vitis_hls_code/ ships Vitis HLS variants of the same algorithm).
- Call sites currently latency-bound on libm sin/cos/tan, willing to trade IEEE correctness for ~4.4-5.5x fewer cycles per call.
- OK vendoring a handful of .h/.cpp files directly, since there is no packaged library to link.

**Skip it when:**
- Need IEEE-correctly-rounded or tightly error-bounded trig (scientific/numeric code checked against std::sin/cos/tan).
- Need real batch/vector throughput over arrays of independent angles: the public API is one angle in, one double out, with no array entry point despite internal AVX2 use.
- Angles very near odd multiples of pi/2 for tan: the function returns +infinity via explicit masking rather than a precise blow-up value.
- Non-x86 targets or CPUs without AVX2/FMA: no scalar or portable fallback is present in the source.
- Need a mature, widely-used dependency: 7 stars, single first-party arXiv preprint (not peer-reviewed), no CI/tests, no install target.

**Integration:** source-drop · none (only <immintrin.h> AVX2/FMA compiler intrinsics) · C++17; g++ (developed/tested with MinGW-w64 g++ on Windows; CMakeLists.txt requires CMake >=3.10) · x86-64 with AVX2 and FMA (uses __m256d/_mm256_* intrinsics); separate Vitis HLS C++ sources exist for FPGA synthesis in vitis_hls_code/

**Vs siblings:** Pick this over SLEEF or VDT only if you specifically want this piecewise-rational-plus-fast-inverse-sqrt technique or its FPGA/HLS variant; SLEEF gives true 4-wide vectorized libm replacements with selectable ulp accuracy, and VDT is an older, better-documented scalar libm-vs-SIMD comparison with wider function coverage — both are more mature (more usage, tests) than this 7-star single-paper repo.

**Gotchas:**
- Each call broadcasts the single scalar angle into all 4 AVX2 lanes and reads back only lane 0 — SIMD width is not used to batch multiple angles, so the reported per-call speedup may not translate into per-element throughput on arrays.
- tan() near odd multiples of pi/2 is special-cased to return +infinity via an AVX2 compare/blend, not computed from the rational approximation.
- Uses a Quake-style fast inverse square root (bit-hack + 1 Newton-Raphson step) in place of sqrt/division, an extra approximation layer on top of the rational fit.
- No CMake install or library target — the build only produces a benchmark executable (bin/trigno_benchmark.exe), so consumers copy the include/ and relevant src/ files into their own project.

**Status:** Actively maintained (last commit 2026-01-29 added tan asymptote masking) and Apache-2.0 licensed, but only 7 stars, no CI/tests, and no packaged library target — usability is 'copyable' source, not a dependency to pull in.

[repo](https://github.com/Nikhil0250/trigno_simd_cpp) · [benchmark](https://arxiv.org/pdf/2502.10831)

##### SLEEF (SIMD Library for Evaluating Elementary Functions)  `C`  `BSL-1.0`  `active`  `Tier B`

Vectorized C library of libm math functions (sin, cos, exp, log, pow); beats scalar <cmath>/libm when call sites are SIMD-batched.

**Beats:** <cmath> (scalar libm, represented in the paper by FDLIBM as the reference scalar implementation) — A peer-reviewed paper (Shibata & Petrogalli, IEEE TPDS vol. 31 no. 6, 2020; arXiv 2001.09258) Table 2 measured reciprocal throughput (ns/call) of SLEEF 3.4's 256-bit AVX2 double-precision vector functions (4 lanes/call, 1-ULP tier) against scalar FDLIBM 5.3, both built with gcc-7.3.0 -O3 -mavx2 -mfma, on an Intel Core i7-6700 with Turbo off: wide-domain sin/cos/tan ran ~3.2-3.6x faster per call, log ~2.0x, exp ~1.6x, pow ~1.25x; on narrow argument domains and for acos/atan, scalar FDLIBM was faster per call than vector SLEEF. This is a SIMD-vs-scalar comparison, not a like-for-like scalar replacement of std::sin/std::exp.

**How:** Processes multiple lanes per call (4/8 doubles, 8/16 floats depending on ISA) instead of looping scalar libm calls, and uses a modified Payne-Hanek argument-reduction algorithm redesigned to minimize the data-dependent branching that otherwise forces every SIMD lane onto the slow path if any single lane needs it (paper: 'SLEEF: A Portable Vectorized Library of C Standard Mathematical Functions', Shibata & Petrogalli). It offers a 1-ULP tier (compensated double-double arithmetic) and a faster ~3.5-ULP tier with a shorter polynomial, trading accuracy for speed. Portability comes from wrapping each ISA's intrinsics behind common inline-function/macro helper headers (helperavx2.h, helperadvsimd.h, helpersve.h, ...) compiled per-target.

**Use it when:**
- Hot loops that already batch scalar math across arrays and can call the Sleef_*dN_u10/u35 vector entry points directly instead of std::sin/std::exp per element
- Wide-domain or branchy transcendental workloads (large-magnitude arguments needing full range reduction) where scalar libm's branches hurt SIMD throughput — Table 2 shows ~3.2-3.6x per-call wins for wide-domain sin/cos/tan, ~2.0x log, ~1.6x exp, ~1.25x pow (SLEEF 4-wide AVX2 vs scalar FDLIBM)
- Need one source portable across AVX2, AVX512F, AdvSIMD (and experimentally SSE2/RISC-V) via runtime dispatch
- Can tolerate the 3.5-ULP accuracy tier for extra speed on non-critical paths
- Also need DFT or quad-precision elementary functions bundled with the math kernels

**Skip it when:**
- Scalar call sites (one value at a time): the benchmarked win is SIMD-vs-scalar, and on narrow argument domains or for acos/atan, scalar FDLIBM was faster per call than vector SLEEF in the same table
- Want a drop-in <cmath> replacement without restructuring loops to load SIMD vectors — API is a different symbol/type surface, not operator/name-compatible with std::sin
- SSE2-only x86 targets (experimental, 'seeking sponsorship') or RISC-V RVV targets (unmaintained, may be removed without notice)
- Code that compiles the inline-header path without -O3: open issue #436 reports wrong results in that configuration
- Need guaranteed-correct cos() when any vector lane's argument may reach >=1e14: open issue #444 reports inconsistent per-lane results there, and the benchmarked domain here goes up to 1e100

**Integration:** static lib | shared lib (CMake build; not header-only, though inline-header build path also exists) · none at runtime for the library itself; build needs CMake 3.18+ and matching C/C++ compiler versions; TLFloat is auto-fetched if not present; tests additionally need libssl/libcrypto, libgmp, libmpfr, libfftw · CMake 3.18+; GCC/Clang/MSVC (README requires the C and C++ compilers to be the same version) · x86-64 (SSE2 experimental, AVX2 and AVX512F mainline-supported), AArch64 AdvSIMD (mainline), RISC-V RVVM1/RVVM2 (unmaintained); toolchain files also exist for POWER (ppc64el) and s390x; CI-tested on Linux/Windows/macOS per the README support matrix

**Vs siblings:** Pick SLEEF over VDT, fmath, or trigno_simd_cpp when you need multiple ISAs (AVX2/AVX512F/AdvSIMD/RISC-V) behind one API with runtime dispatch, plus quad-precision or DFT routines, or want a tunable 1-ULP/3.5-ULP accuracy knob; those siblings target a single ISA/precision and a narrower function set.

**Gotchas:**
- Inline-header build path gives wrong results if the including translation unit is compiled without -O3 (open issue #436, since 2021)
- Vectorized cos() can give inconsistent per-lane results once any lane's argument is >=1e14 (open issue #444) — relevant since the benchmarked domain in this record runs up to 1e100
- exp and pow can return infinity earlier than correct (open issue #600, 2024)
- Runtime CPU-extension dispatch is not thread-safe on first call, per an open maintainer-acknowledged issue (#560)

**Status:** Actively maintained — last commit 2025-12-25, latest tagged release 3.9.0 (March 2025); this session found five open issues touching accuracy and thread-safety dating back to 2021. BSL-1.0 licensed and small enough to vendor or build as a static/shared lib; the cited benchmark used the older 3.4 branch, several major releases behind current master.

[repo](https://github.com/shibatch/sleef) · [benchmark](https://arxiv.org/pdf/2001.09258)

#### number-parsing-formatting

##### Boost.Charconv  `C++`  `BSL-1.0`  `active`  `Tier A`

Portable std::to_chars/from_chars reimplementation for pre-C++17 toolchains and MSVC, winning there and near-parity on GCC.

**Beats:** std::to_chars, std::from_chars — Maintainer-run benchmarks (test/STL_benchmark.cpp) on Linux GCC 13.1/libstdc++, Windows MSVC 14.3, and macOS ARM (M1 Pro) GCC 13.2 score Boost.Charconv against std::to_chars/from_chars, itself scored against std::printf/std::strtoX; results run from near-parity to ~1.3x in most cells, with the clearest wins on MSVC float/double from_chars (~2.0x/~4.2x) and Linux uint32_t from_chars (~1.3x), and a few Windows/ARM cells (double/uint64_t to_chars, ARM from_chars) slightly slower than std.

**How:** to_chars for floats uses the Dragonbox shortest-round-trip algorithm (detail/dragonbox/dragonbox.hpp, floff.hpp for fixed format); from_chars for floats uses Daniel Lemire's fast_float parser (detail/fast_float/); 80-bit/128-bit long double and __float128 go through Ryu's generic 128-bit path (detail/ryu/ryu_generic_128.hpp); integer to_chars uses precomputed digit-count/significand lookup tables (integer_search_trees.hpp, significand_tables.hpp) for branch-light itoa. These are the same published algorithms most std::to_chars/from_chars implementations already use, so gains show up mainly where the target stdlib (MSVC's) hasn't adopted them as aggressively.

**Use it when:**
- Targeting MSVC and needing float/double from_chars roughly 2-4x faster than std::from_chars (the largest measured win)
- Building for a C++11/14 toolchain (GCC 5+, Clang 3.8+, MSVC 2015+) that lacks <charconv> entirely
- Need to_chars/from_chars for __float128 or 80-bit long double, which std <charconv> doesn't cover
- Already depend on Boost and want one to_chars/from_chars-shaped API across compilers instead of per-compiler fallbacks
- High-volume uint32_t from_chars parsing on Linux/GCC, where Boost measures ~1.3x over std::from_chars

**Skip it when:**
- Already on a recent GCC/libstdc++ or Clang target, where most cells are near parity (0.97-1.0x) with std::to_chars/from_chars
- Want a true header-only drop-in: charconv ships src/to_chars.cpp and src/from_chars.cpp as separately-compiled sources, plus Boost.Assert/Config/Core as dependencies
- Parsing untrusted long double/__float128 strings over 1024 bytes, the one documented path where it allocates
- Need an independent (non-maintainer) benchmark; the published numbers are run and maintained by the library's own authors
- On Windows double/uint64_t to_chars, where Boost measured very slightly slower than std (15.26 vs 15.77; 2.06 vs 2.10)

**Integration:** static lib | shared lib (compiled sources in src/; not header-only) · Boost.Assert, Boost.Config, Boost.Core; optional libquadmath for __float128/std::float128_t · C++11 (GCC 5+, Clang 3.8+, MSVC 2015 / 19.24+, NVCC 12.8+ for optional CUDA); constexpr paths need C++14 · x86/x86_64/ARM on Linux, macOS, Windows; libquadmath path limited to Linux x86/x86_64/PPC64/IA64; partial CUDA and SYCL device support

**Vs siblings:** Pick Boost.Charconv when you need an actual std::to_chars/from_chars-compatible surface (same enums, same result types) on a pre-C++17 toolchain, MSVC, or for __float128/long double, not a different API or output format. Pick c4core, rigtorp/CharConv, or jeaiii/itoa instead when you want larger, unambiguous wins on a modern GCC/Linux stack and don't need std-API compatibility.

**Gotchas:**
- Parsing a long double/__float128 string longer than 1024 bytes is the one documented path that allocates, despite the library's non-allocating claim elsewhere
- The fixed-format float path (floff, Dragonbox-based) had buffer-overflow and internal-overflow bugs (issues #186, #190) fixed in 2024; a to_chars-with-precision correctness bug (#158) was also fixed; issue #166 (more to_chars problems) was still open as of the last check
- __float128/std::float128_t support needs libquadmath and only builds on Linux x86/x86_64/PPC64/IA64
- b2/CMake auto-detect and link libquadmath when available; other build systems must define BOOST_CHARCONV_HAS_QUADMATH and link it manually

**Status:** Actively maintained (last master commit 2026-08-13, CI/fuzzing/codecov all wired up); BSL-1.0 licensed and copyable, but as a Boost library it pulls in Boost.Assert/Config/Core and a compiled component rather than being a single vendorable header.

[repo](https://github.com/boostorg/charconv) · [benchmark](https://github.com/boostorg/charconv/blob/master/doc/charconv/benchmarks.adoc)

##### Dragonbox  `C++`  `Apache-2.0 WITH LLVM-exception OR BSL-1.0`  `stale`  `Tier A`

Shortest round-trip double/float-to-decimal conversion, faster than std::to_chars.

**Beats:** std::to_chars — On the independent fmtlib/dtoa-benchmark suite (Apple M1 Pro, Apple clang 21.0.0, Release build via libc++), Dragonbox's to_chars_n with the full cache table converts a double to its shortest round-trip decimal string in a mean 28.95ns vs 51.35ns for libc++'s std::to_chars (1.77x) and 744.72ns for sprintf (25.72x), over a mixed 1.7M-value pool spanning 1-17 significant digits.

**How:** Based on Schubfach (a continuous pigeonhole-principle argument), itself inspired by Grisu/Grisu-Exact. It picks the shortest correctly-rounded decimal digits directly from a precomputed power-of-10 cache table plus magic-number/branchless integer arithmetic, avoiding the big-integer or iterative digit-adjustment loops older dtoa algorithms use. A full cache table (9904 bytes for double) trades static data for speed; a compact table (584 bytes) is ~20% slower.

**Use it when:**
- Hot-path double/float-to-string conversion where scientific-notation output is acceptable and every ns matters
- Already depending on {fmt} indirectly and want the same algorithm standalone/header-only without the rest of fmt
- x86-64 target with a C++17-capable toolchain (C++20 unlocks constexpr everywhere)
- Want to tune static-data footprint via the full-vs-compact cache policy
- Need output strictly faster than libc++/libstdc++ std::to_chars on the same double-conversion workload

**Skip it when:**
- Need std::to_chars-compatible signature/namespace as a true drop-in replacement
- Need %f-style fixed-point output directly — Dragonbox only emits scientific notation (0.1 -> 1E-1); you write the reformatting
- Targeting ARM or other non-x86 architectures — maintainer-acknowledged correctness bugs in intrinsic fallback/detection are open and unresolved (issue #11, filed 2024)
- Require an actual C++11 toolchain — README claims C++11 but the shipped CMakeLists.txt requires cxx_std_17; a C++11 port was requested in 2023 and never delivered (issue #8)
- Low-volume/non-hot-path formatting where the ~22ns/call saved over std::to_chars doesn't justify vendoring three files and a template-heavy API

**Integration:** header-only (core dragonbox.h); to_chars string-generation layer adds dragonbox_to_chars.h + one .cpp · none (C++ standard library only; Ryu/Schubfach/Grisu-Exact in the repo are benchmark-only subprojects, not runtime deps) · CMakeLists.txt requires cxx_std_17 for both targets; README's 'C++11 or higher' claim is not what the build actually enforces (see issue #8). Full constexpr support needs C++20. · x86-64 (benchmarked/used in production via fmt); ARM and other architectures have open, maintainer-acknowledged correctness bugs in intrinsic fallback/detection (issue #11, opened 2024, still open) — not documented as safe there

**Vs siblings:** On the same fmtlib/dtoa-benchmark table, Dragonbox (28.95ns) beats both catalogued siblings Ryu (46.07ns) and {fmt} (36.84ns) and is the only one of the three verified directly against std::to_chars rather than just sprintf; pick it over them when raw to_chars-class conversion speed is the goal and the policy-template API/scientific-notation-only output are acceptable, and pick {fmt} instead when you also want its broader formatting API (fmt already uses Dragonbox internally). fast_float solves the reverse problem (string-to-double parsing), so it's complementary, not a substitute.

**Gotchas:**
- Output is always scientific notation (e.g. 0.1 -> 1E-1), never %f-style; callers add their own formatting for printf-like output
- README says C++11 but the CMakeLists.txt pins cxx_std_17 for both the dragonbox and dragonbox_to_chars CMake targets
- ARM/non-x86 support has open, maintainer-confirmed correctness bugs in intrinsic fallback detection (issue #11, unresolved since 2024)
- Policy-template API (sign, trailing-zero, decimal-to-binary rounding, binary-to-decimal rounding, cache) can cause binary bloat if many policy combinations get instantiated

**Status:** Stale by commit cadence (last commit 2025-09-12, ~1 year old) but not abandoned — issues still receive maintainer replies through 2026; dual Apache-2.0-with-LLVM-exception/BSL-1.0 licensing and a 3-file footprint for the to_chars path make it easy to vendor despite the slow pace.

[repo](https://github.com/jk-jeon/dragonbox) · [benchmark](https://github.com/fmtlib/dtoa-benchmark)

##### fast_double_parser  `C++`  `Apache-2.0`  `stale`  `Tier A`

Header-only C++11 double parser using the Eisel-Lemire algorithm; 2.5-9.5x strtod throughput, superseded by fast_float.

**Beats:** std::stod (strtod) — Benchmarked against strtod_l (C locale) on Apple clang 11.0.0 / Intel Core i7-7700K: 460.64 MB/s vs strtod's 186.90 MB/s (~2.5x) parsing random doubles in [0,1), and 662.01 MB/s vs 69.73 MB/s (~9.5x) parsing the canada.json real-world coordinate dataset; the README's '4x' headline sits between these two workload-specific ratios. The same run also reports abseil and double-conversion figures, both slower than fast_double_parser on both workloads.

**How:** Implements the Eisel-Lemire algorithm (Lemire, "Number Parsing at a Gigabyte per Second," arXiv:2101.11408): accumulate up to 19 significant digits into a 64-bit integer, then multiply it by a precomputed 64-bit truncated mantissa for the decimal exponent using a 128-bit full multiplication (hardware `_umul128`/`__uint128_t`, with an emulated fallback) to directly assemble the correctly-rounded IEEE754 bit pattern. This skips strtod's general parsing path entirely and falls back to the platform's locale-independent strtod_l/_strtod_l only for the rare >19-significant-digit or ambiguous-rounding cases.

**Use it when:**
- Hot-path parsing of many decimal doubles from files/network (GeoJSON, CSV, log lines) where strtod is a measured bottleneck
- JSON-shaped numeric literals only (no hex floats, no locale decimal comma)
- Header-only vendoring is acceptable (drop include/fast_double_parser.h into the build)
- C++11-only toolchains that can't adopt fast_float's newer API/build requirements
- Throughput-bound batch parsing (MB/s) rather than a single latency-critical call

**Skip it when:**
- Any new project — the README itself tells users to adopt fast_float instead (more grammar support, same speed, wider adoption/testing)
- Need std::from_chars-style explicit begin/end pointers rather than a null/non-numeric-terminated C string — use fast_float
- Need 32-bit float parsing — this library is double-only
- Need hex floats, NaN/Infinity, or non-JSON strtod grammar (e.g. leading '+', "0x1p3", leading zeros like "01")
- Repo is stale (last commit 2025-05-27) with only 2 open issues (macro hygiene, power-range tightening) and no active feature work

**Integration:** header-only · none (the benchmark target pulls in abseil and double-conversion, but the library itself has zero deps) · C++11 (CMakeLists sets CMAKE_CXX_STANDARD 11); MSVC, GCC, and Clang all supported · x86-64, ARM64, and 32-bit (native _umul128/__uint128_t 128-bit multiply where available, emulated fallback otherwise); Windows/Linux/macOS plus a stringstream-based strtod workaround for Cygwin/MSYS2/Solaris

**Vs siblings:** No catalogued sibling targets double parsing (they cover to_chars/from_chars formatting or integer conversions); the real alternative is its own successor fast_float. Pick fast_double_parser only when a C++11-only toolchain or an existing call site already depends on its exact pointer-in/pointer-out API — otherwise fast_float matches its speed with a std::from_chars-style API and broader (non-JSON-restricted) grammar support.

**Gotchas:**
- Global-namespace macros (WARN_UNUSED, really_inline, unlikely) defined in the header are never #undef'd and can collide with same-named macros pulled in transitively from other libraries (issue #66); this bit a real user combining it with Microsoft LightGBM, which itself vendors this same library
- Rejects some strtod-valid-but-JSON-invalid forms: leading zeros ("01"), a bare trailing decimal point ("1."), hex floats, and never produces NaN/Infinity
- Falls back to platform strtod_l for any number with >19 significant digits, so very long decimal mantissas get strtod's speed rather than the fast path
- Assumes the FPU rounding mode is round-to-nearest (FE_TONEAREST); behavior under other rounding modes is unverified

**Status:** Maintenance status is stale — last commit 2025-05-27, no active feature development, and the maintainer's own README recommends migrating to fast_float — but it's a single small header under a dual Apache-2.0/Boost-1.0 license, cheap to vendor and freeze if a project already depends on its exact API.

[repo](https://github.com/lemire/fast_double_parser) · [benchmark](https://github.com/lemire/fast_double_parser/blob/master/README.md)

##### fast_float  `C++`  `Apache-2.0 OR MIT OR BSL-1.0`  `active`  `Tier A`

Header-only C++ from_chars for float/double/int; 3-5x faster than glibc strtod, exact IEEE rounding.

**Beats:** std::stod/strtod — Peer-reviewed benchmark (Lemire, Software: Practice and Experience 51(8), 2021) measured fast_float::from_chars against glibc strtod, single-threaded, GCC 10.2 -O3 -DNDEBUG, on an Intel Skylake i7-6700: 45 Mfloat/s vs 9.0 Mfloat/s (5x) on the 111k-line 'canada' JSON coordinate corpus (Table 9); comparable 3-5x wins held on AMD Zen2, ARM Ampere, and IBM POWER9 CPUs, and against MSVC STL's std::from_chars on an Intel i7-7700K (Table 13).

**How:** Uses the Eisel-Lemire algorithm (named directly in a comment in include/fast_float/parse_number.h): a fast path that combines the decimal significand with precomputed power-of-five tables to compute the correctly-rounded binary value from one or two 64-bit multiplications (compute_product_approximation in decimal_to_binary.h). When that approximation cannot be proven correct, which is rare, it falls back to exact big-integer digit comparison (bigint.h / digit_comparison.h) instead of a slow generic parser, so the common case stays branch-light and allocation-free.

**Use it when:**
- Parsing large volumes of floats/doubles from text (JSON, CSV, scientific/columnar data) where strtod or std::from_chars throughput is a bottleneck
- Header-only C++11+ codebases that want a from_chars-shaped API without adding a build dependency
- Need locale-independent, correctly-rounded parsing with round-to-even tie-breaking
- Need JSON, JavaScript-literal, or Fortran-literal number grammars without hand-rolling the format checks
- Compile-time (constexpr) float parsing in C++20

**Skip it when:**
- Need long double parsing - unsupported; only float, double, and fixed-width float16/32/64/bfloat16 are covered
- Need hexadecimal floating-point literals - decimal format only
- Building with -ffast-math: infinity()/NaN handling is documented-incompatible in open issue #397 (unresolved as of 2026-09-24)
- Only parsing a handful of floats and every byte of compile time / include overhead matters, since it is a template-heavy header-only include vs. a plain libc call
- Want locale-aware parsing out of the box - the default from_chars is locale-independent; locale behavior requires the separate from_chars_advanced API

**Integration:** header-only · none · C++11 for the core library (CMakeLists.txt sets FASTFLOAT_CXX_STANDARD 11 by default); C++20 needed for constexpr parsing; CMake 3.14+ for the build/install targets · Windows/MSVC, macOS, Linux, FreeBSD per README; supports big- and little-endian, 32-bit and 64-bit systems; CI also exercises ARM, RISC-V, and s390x (big-endian)

**Vs siblings:** fast_float parses text to binary (beats strtod/std::from_chars); Dragonbox, Ryu, and {fmt} format binary to text (beat sprintf/std::to_chars) - they solve the opposite problem, so pick fast_float for the parsing side of a pipeline and pair it with one of those for the formatting side rather than treating them as substitutes.

**Gotchas:**
- -ffast-math builds break infinity/NaN handling (open issue #397 as of 2026-09-24; no fix merged yet)
- Locale-dependent decimal separators (e.g. comma) require the separate from_chars_advanced + parse_options call, not the default from_chars
- chars_format::json rejects bare inf/nan by default; use the non-standard json_or_infnan variant to allow them
- v8.2.0 had a big-endian regression on s390x (issue #354, closed/fixed) - use a current release rather than pinning that tag if targeting big-endian

**Status:** Actively maintained (last commit 2026-09-23, tagged v8.3.0), triple-licensed Apache-2.0/MIT/BSL-1.0, header-only and small enough to vendor; already embedded in GCC 12's std::from_chars and used by Chromium, WebKit/Safari, MySQL, DuckDB, Boost.JSON, ClickHouse, Blender, and Apache Arrow, which makes it low-risk to adopt.

[repo](https://github.com/fastfloat/fast_float) · [benchmark](https://arxiv.org/abs/2101.11408)

##### Ryu  `C`  `Apache-2.0 OR BSL-1.0`  `active`  `Tier A`

Shortest round-trip float/double-to-string conversion beating sprintf, plus a faster %f/%e printf replacement.

**Beats:** printf (sprintf) — The independent fmtlib/dtoa-benchmark (Google Benchmark, Apple clang 21.0.0, CMake Release build, Apple M1 Pro) measured Ryu's d2s_buffered at 46.07ns/double mean vs C sprintf("%.17g", value) at 744.72ns — 16.164x faster — across a mixed 1.7M-value pool of doubles at 1-17 significant digits; the same table puts std::to_chars (libc++) at 51.35ns, only about 1.11x slower than Ryu.

**How:** Ryu is a table-based shortest-decimal algorithm (successor to Dragon4/Grisu): fixed lookup tables of powers of 5 let it compute, without bignum arithmetic, the shortest decimal digit string whose rounding interval contains the original binary float in one pass. This avoids the double-rounding correctness checks and slow-path fallbacks that Grisu3-style algorithms need for hard cases. Ryu Printf reuses the same table machinery but is restricted to a fixed precision, letting it skip the general shortest-digit search entirely. Correctness for both is proven in peer-reviewed papers (PLDI'18, OOPSLA'19) rather than established only by fuzz testing.

**Use it when:**
- Hot paths serializing large volumes of doubles to text (JSON/CSV emitters, log lines, time-series export) where sprintf/ostringstream latency shows up in profiles.
- Need shortest round-trip decimal output (like Python repr or JS Number.toString) rather than a fixed %.17g dump.
- C/C++ codebase that can vendor a small, dependency-free source tree (CMake 3.10+ or Bazel build, no external libs).
- Want %f/%e output several times faster than platform printf while matching its rounding, and can live without other printf flags.
- Targeting x86-64/aarch64, or another platform where float and integer types share endianness; the hand-tuned fast paths cover 32/64-bit float/double.

**Skip it when:**
- Need full printf flag support (%g, width, padding, +, #) — Ryu Printf only implements %f/%e precision, not the full spec.
- Formatting mostly small-integer-valued doubles (counters, sensor readings) — issue #144 reports Ryu ~1.5-2x slower than double-conversion there; no built-in integer fast path.
- Need fast long double/__float128 conversion — only a slower generic 128-bit fallback exists for those widths, and it isn't available on MSVC (needs __uint128_t).
- Need a documented safe output-buffer-size constant before calling *_buffered — issue #149 (open) notes ryu.h has no #define for required buffer length.
- Want output identical to std::to_chars — the measured margin over libc++'s to_chars is only ~1.11x, and to_chars ships in the standard library with zero extra dependency.

**Integration:** static lib (source-drop; CMake or Bazel build, no header-only mode) · none for the C core; CMake 3.10+ or Bazel 0.14+ to build; JDK 8+ only for the separate Java port · C99 (uses stdint.h/inttypes.h); generic_128 (128-bit fallback) needs GCC/Clang/Intel for __uint128_t, not available on MSVC · x86-64, aarch64, and other platforms where the float type and same-width integer type share endianness (README states big-endian works under that condition); CI covers Ubuntu 18.04, macOS, Windows Server 1803

**Vs siblings:** Pick Ryu over Dragonbox when you want a plain-C implementation with the widest set of independent language ports to reference (Rust, Go, Julia stdlib, Erlang/OTP, etc.); Dragonbox is faster still on this same benchmark (25.7x vs sprintf and a direct win over Ryu) if closing that extra gap matters more than portability. Pick {fmt} instead if you're already pulling in a formatting/iostream-replacement library (it also uses Dragonbox internally) and want printf-style format strings rather than raw conversion functions.

**Gotchas:**
- Ryu, Dragonbox, and Schubfach (per the fmtlib benchmark's own notes) always emit exponential notation in shortest mode, e.g. 0.1 -> 1E-1, unlike %g's 0.1 — don't assume output matches sprintf's shortest-%g style.
- No documented #define for safe output buffer size (open issue #149); undersizing the buffer passed to a *_buffered_n function is a real overflow risk.
- f2s (float32) shortest mode has at least one known incorrect-rounding case still open as of 2025 (#235: 2147483904 is formatted as 2.147484E9 instead of the exact value) — the d2s/double path used in this benchmark is a separate code path but this signals the algorithm's edge cases aren't all closed.
- Public C identifiers (d2s, f2s, d2s_buffered, etc.) are unprefixed (open issue #148) and can collide with other libraries' symbols when statically linked.

**Status:** Actively maintained (last commit 2026-02-09, ~1.4k stars) under dual Apache-2.0/BSL-1.0 licensing, so it's copyable under either regime; the algorithm has been ported into a dozen-plus languages and standard libraries (Rust, Go, Julia's stdlib, Erlang/OTP, etc.), a strong maturity signal despite a few still-open ergonomics/correctness issues (undocumented buffer size, an f32 shortest-mode rounding edge case).

[repo](https://github.com/ulfjack/ryu) · [benchmark](https://github.com/fmtlib/dtoa-benchmark)

##### {fmt}  `C++`  `MIT`  `active`  `Tier A`

Type-safe C++ formatting library beating printf/iostreams; its Dragonbox-based float formatter is the speed driver here.

**Beats:** printf (sprintf) — On an Apple M1 Pro with Apple Clang 21.0.0, fmt::format_to with FMT_COMPILE converted a 1.7M-value pool of random doubles to shortest round-trip decimal strings in a mean 36.84ns each, versus 744.72ns for sprintf (20.214x) and 885.30ns for ostringstream (~24x), per the fmtlib/dtoa-benchmark suite that fmt's own README links from its Performance section.

**How:** Float-to-string conversion uses the Dragonbox algorithm for shortest, correctly-rounded, round-trip decimal output, confirmed directly in the dtoa-benchmark README ('fmt::format_to with compile-time format strings (uses Dragonbox)'). FMT_COMPILE parses the format string into formatting code at compile time — confirmed in include/fmt/compile.h, which requires C++17 constexpr-if support for the compiled fast path and otherwise silently falls back to a non-compiled string check. Output accumulates in fmt::memory_buffer, avoiding iostreams' per-call locale/stream-state overhead and sprintf's null-terminated buffer handling.

**Use it when:**
- Hot paths converting many doubles/ints to strings (logging, serialization) where printf/iostreams latency is measurable
- Format strings are known at compile time and paired with FMT_COMPILE to get the benchmarked fast path — the ~20x number does not apply to runtime-only format strings
- Need shortest, correctly-rounded, round-trip float-to-string output, which sprintf/ostringstream do not guarantee
- C++11+ codebase that can take on a header-only or compiled dependency for type-safe, low-allocation formatting
- Already moving toward C++20/23 std::format/std::print — fmt is the pre-standard superset (adds chrono, ranges, color/style output)

**Skip it when:**
- Format strings are assembled dynamically at runtime with unknown structure — loses the FMT_COMPILE path the benchmark measured
- printf's current latency is already acceptable and adding any dependency isn't worth it
- Pre-C++11 toolchain — CMakeLists.txt requires cxx_std_11 as a hard minimum
- Compile-time budget is tight across many translation units: fmt headers add ~5.1s vs printf's 1.6s per the README's 100-TU bloat-test (still far below IOStreams' 25.5s)
- Need it truly drop-in for existing printf/sprintf call sites — the fast {}-syntax API requires rewriting call sites; only fmt::printf approximates a drop-in and wasn't the path benchmarked

**Integration:** header-only (FMT_HEADER_ONLY macro) or compiled static/shared lib (default); minimum config is 3 headers (core.h, format.h, format-inl.h) per README · none (README: 'no external dependencies') · C++11 minimum (CMakeLists.txt: target_compile_features(fmt PUBLIC cxx_std_11)); C++17 constexpr-if needed for the FMT_COMPILE fast path used in the benchmark · any — README lists Linux/macOS/Windows CI (linux.yml, macos.yml, windows.yml workflows); no architecture-specific requirement found

**Vs siblings:** Pick fmt when you want a full formatting API (containers, chrono, positional args, color output) whose float path happens to use Dragonbox internally, not just a float-to-string primitive. Pick Dragonbox directly (1.77x faster than std::to_chars) or Ryu (16.164x vs sprintf) when you need a standalone dtoa routine with no formatting-library overhead; fast_float solves the reverse problem (string-to-double parsing) and isn't a substitute here.

**Gotchas:**
- FMT_COMPILE needs C++17 constexpr-if (__cpp_if_constexpr) to produce the compiled fast path; without it, it falls back to FMT_STRING (compile-time validated, not the fast-formatting path) — per include/fmt/compile.h
- Exceptions can be disabled for -fno-exceptions builds via FMT_USE_EXCEPTIONS (checked in include/fmt/format.h)
- basic_memory_buffer takes an Allocator template parameter (include/fmt/format.h) for custom allocation, but the default allocator is used unless a caller specifies otherwise

**Status:** Actively maintained (25,807 stars, MIT license, last commit 2026-09-21, 12 open issues, not archived) — low-risk long-term dependency; it's the reference basis for C++20 std::format.

[repo](https://github.com/fmtlib/fmt) · [benchmark](https://github.com/fmtlib/dtoa-benchmark)

##### fpconv (night-shift)  `C`  `BSL-1.0`  `stale`  `Tier B`

Tiny Grisu2 C library converting doubles to shortest round-trip strings, ~10x faster than std::ostringstream.

**Beats:** std::ostringstream (iostreams); page's headline ratio is vs sprintf() — On the independent miloyip/dtoa-benchmark RandomDigit case (1,000 random doubles, 1-17 significant digits, min of 10 trials x100 iterations), fpconv converts in 273.822ns vs sprintf's 1,256.376ns (4.59x) and std::ostringstream's 2,778.748ns (~10.1x, derived), measured with MSVC 2013 on Windows x64 on a Core i7-920 @2.67GHz.

**How:** Implements Fabian Loitsch's Grisu2 algorithm: the double's mantissa/exponent are converted to a 64-bit fixed-point `Fp` struct, scaled into a normalized range using a precomputed table of 87 power-of-ten cache constants (powers.h), and digits are generated directly via integer division against upper/lower boundary intervals (`generate_digits`/`round_digit`). This avoids the arbitrary-precision bignum arithmetic and locale/format-flag machinery that `sprintf`/`ostringstream` pay for, at the cost of Grisu2 occasionally emitting one digit more than the true shortest form (unlike Grisu3/Ryu, which always find the minimal digit count).

**Use it when:**
- Hot-path double serialization (JSON/log/wire-format emitters) where sprintf/ostringstream formatting overhead shows up in profiles
- C or C++ code that can vendor a single .c/.h pair rather than pull in a library or link a header-only C++ template
- Need the shortest round-trippable string and don't care about scientific/fixed formatting control
- Pre-C++17 toolchains without <charconv>/std::to_chars available
- Embedded or size-constrained builds where a ~300-line, dependency-free source drop is preferable to a bigger conversion library

**Skip it when:**
- Need std::to_chars/from_chars-compatible API, or sprintf-style format control (precision, fixed vs scientific) - fpconv only emits shortest round-trip form
- Need string-to-double parsing too - fpconv is dtoa-only, no strtod-equivalent shipped
- Want active upstream maintenance - repo is stale (last commit Dec 2023), single maintainer, tiny community (62 stars, 14 forks)
- Vendoring an old/pinned copy predating the Dec 2023 fix: versions before that had a documented 24-byte buffer overflow on some large-magnitude doubles (e.g. -2^77), overflowing the buffer the header itself recommends
- Want benchmark evidence against a modern baseline - the only published numbers are vs VC2013 ostringstream/sprintf on a 2009 Core i7-920, not vs std::to_chars

**Integration:** source-drop · none (only C stdlib headers: stdbool.h, string.h, stdint.h) · not documented; plain C99 (uses stdbool.h/stdint.h), no CMake or version pin in the repo · any platform with IEEE-754 doubles; pure C with no SIMD/intrinsics, bit access via a union type-pun

**Vs siblings:** On the same dtoa-benchmark page, both milo Grisu2 (138.021ns) and google/double-conversion (201.645ns) beat fpconv (273.822ns) outright, so pick this over them only when you specifically want a minimal plain-C .c/.h pair to vendor rather than a header-only C++ template (milo) or a heavier C++ library with a bignum fallback path (double-conversion); pick Boost.Charconv, c4core, or rigtorp/CharConv instead if you want a std::to_chars-shaped API.

**Gotchas:**
- Pre-Dec-2023 snapshots overflow the documented 24-byte buffer for some large-magnitude values (GitHub issue #5, e.g. -2^77); fixed in the same commit recorded as last_commit (2023-12-14), so only affects older vendored copies
- Output is not null-terminated; caller must track and use the returned length
- Grisu2 can emit one extra digit versus the true shortest representation in rare cases (no Grisu3/Ryu fallback)
- Repo also bundles an unmaintained D port (fpconv_ctfe.d); it is not covered by the same fix history as the C code

**Status:** Stale since its last commit in December 2023 (which was also the fix for the buffer-overflow bug) with a small community (62 stars, 14 forks), but it's a two-file BSL-1.0 source drop small enough to read end-to-end and vendor with confidence.

[repo](https://github.com/night-shift/fpconv) · [benchmark](https://github.com/miloyip/dtoa-benchmark)

##### google/double-conversion  `C++`  `BSD-3-Clause`  `active`  `Tier B`

Grisu3-based double<->string library extracted from V8; beats sprintf/ostringstream, covers both to_chars- and from_chars-like directions.

**Beats:** std::ostringstream (iostreams); page's headline ratio is vs sprintf() — On the independent miloyip/dtoa-benchmark RandomDigit workload (1,000 random doubles, 1-17 significant digits, shortest round-trippable ASCII, min of 10x100 trials), double-conversion's EcmaScriptConverter().ToShortest() averaged 201.645ns vs sprintf's 1256.376ns (6.23x) and std::ostringstream's 2,778.748ns (~13.8x, derived), on an Intel Core i7 920 @2.67GHz built with VC++2013 Win64 release config (only premake's {"Optimize"} flag is itemized, no literal compiler flags).

**How:** Formatting uses the Grisu3 algorithm (fast-dtoa.cc): 64-bit fixed-precision 'DiyFp' arithmetic plus precomputed cached powers of ten (cached-powers.cc) generate the shortest round-trippable decimal directly, skipping printf format-string parsing and avoiding arbitrary-precision math for the common case. When Grisu3 can't resolve a value unambiguously it falls back to an exact bignum algorithm (bignum-dtoa.cc). Parsing (strtod.cc) mirrors this: a DiyFp fast path handles typical inputs and only escalates to bignum arithmetic for correctly-rounded edge cases.

**Use it when:**
- JSON/serialization code needing shortest round-trippable double<->string conversion at high throughput (already used inside V8, Chromium, RapidJSON)
- Hot paths currently bottlenecked on sprintf/ostringstream for float formatting
- Need both formatting and parsing directions from one small dependency instead of stitching together separate libraries
- Targeting older/pre-C++11 toolchains (utils.h ships fallback macros for pre-C++11 compilation)
- Cross-platform desktop/server build via scons/cmake/bazel; willing to link a small library rather than stay header-only

**Skip it when:**
- Need an actual drop-in for std::to_chars/std::from_chars call sites — API shape is a converter class with explicit buffers/flags, not a function-call replacement
- Code relies on ToPrecision(): it can fall onto the slow bignum-fallback path for many inputs and become slower than sprintf (open issue #83, unresolved as of this research)
- Inputs frequently have decimal expansions of the form N*10^M — same Grisu3-fails/bignum-fallback slow path (open issue #28, open since 2016, still open)
- Need header-only, zero-build-step integration — this requires its own static/shared library build step (scons/cmake/bazel)
- Parsing throughput is the priority — open issue #153 reports StringToDouble is slower than other dtoa-style parsers on some inputs; a parsing specialist may win there

**Integration:** static lib | shared lib (also viable as a source-drop: 8 .cc files, no header-only mode) · none (Bazel BUILD links -lm) · no CMAKE_CXX_STANDARD is pinned; utils.h carries pre-C++11 fallback macros, so the code itself targets C++03+; CMake path requires CMake 3.29+, scons/bazel builds don't · x86-64, arm64 (issue #6 confirms arm64 support), and other GCC/Clang/MSVC targets; no SIMD/ISA requirement

**Vs siblings:** Pick this over milo Grisu2 (miloyip/dtoa-benchmark) when you want the battle-tested, actively maintained, V8-derived implementation with real production adoption (V8, Chromium, RapidJSON) rather than a single-header benchmark contender that happens to be faster in that one shootout. Pick c4core or fast_double_parser instead when raw throughput matters more than provenance: c4core's own README claims 40%-2x faster than std::to_chars, and fast_double_parser is a parsing-only specialist that issue #153 suggests may beat double-conversion's StringToDouble.

**Gotchas:**
- ToShortest() needs a buffer sized to at least kBase10MaximalLength+1 (or kMaxCharsEcmaScriptShortest=25 for the EcmaScript preset) or the call can fail; buffer sizing is the caller's responsibility
- ToPrecision() can silently take the slow bignum-fallback path and end up worse than sprintf for a large class of inputs (open issue #83)
- DoubleToAscii on N*10^M-shaped values hits the same Grisu3-fails/bignum-fallback slow path (open issue #28, open since 2016)
- ALLOW_HEX and ALLOW_OCTALS parsing flags only apply to integer literals; combining them with fractional/exponent characters yields 'trailing junk' rather than a parse error

**Status:** Actively maintained (last commit 2026-09-13, enrolled in OSS-Fuzz and OpenSSF Scorecard) and BSD-3-Clause; not header-only, so it needs a small build step or manual vendoring of its ~8 .cc files, but has no external dependencies.

[repo](https://github.com/google/double-conversion) · [benchmark](https://github.com/miloyip/dtoa-benchmark)

#### ordered-maps-trees

##### fast-containers (SIMD/hugepage B+Tree)  `C++`  `BSD-3-Clause`  `active`  `Tier A`

Header-only C++23 B+tree with SIMD search and hugepage allocators, 2-5x faster than std::map on large trees.

**Beats:** std::map — On an isolated core of an AMD Ryzen 9 5950X (Linux 6.16.3, Clang Release build with -O3 -march=haswell -mavx2 -mfma -flto=thin), the repo's own RDTSC-timed benchmark shows the SIMD+hugepage btree beating std::map by roughly 2.1-4.8x on P50/P99.9 insert/find/erase at 10M elements with 8-byte keys and 32B or 256B values; at 10K elements the advantage shrinks and std::map wins ERASE P99.9 with 256B values (213.6ns vs 245.7ns).

**How:** Fixed-size leaf/internal nodes (heuristically sized to ~1-2KB, 16-32 cache lines) replace the per-node pointer-chasing of a red-black tree. Node search uses AVX2 SIMD linear scans (`SearchMode::SIMD`) over a dense sorted array (`dense_map`) instead of branchy binary search. A pooling `HugePageAllocator` backs node storage with 2MB hugepages, cutting TLB misses and making allocation near-free compared to the default allocator; the README calls this 'the single most important optimization,' giving a 2-3x speedup on its own.

**Use it when:**
- Ordered int64-keyed maps with 32-256 byte values at large scale (roughly 1M-10M+ elements) where TLB misses and allocator overhead dominate runtime
- You need both P50 and P99.9 latency wins over std::map for insert/find/erase, not just throughput
- You control an x86-64 Linux environment with AVX2 (Haswell/Excavator or newer) and can configure OS hugepages
- You're willing to tune node size, SearchMode, and allocator per key/value size instead of relying on one default
- You're also considering Abseil's btree: this implementation beats absl+hugepages by 20-135% in the repo's own benchmarks

**Skip it when:**
- Trees under roughly 10K elements: std::map becomes competitive and even wins some tail-latency cases (e.g. ERASE P99.9 with 256B values: 213.6ns vs 245.7ns)
- Non-x86-64 or non-Linux targets — SIMD paths and RDTSC timing are x86-64-specific, and the README states Windows is untested
- Workloads relying on std::map's pointer/iterator stability across mutations; the header documents that some operations invalidate all iterators
- Environments where OS hugepages can't be configured/administered — losing hugepages removes most of the measured advantage
- Risk-averse adoption: single-author, explicitly AI-agent-assisted, actively-changing work-in-progress with self-reported, not independently reproduced benchmarks

**Integration:** header-only · none for the library itself; tests/benchmarks pull in Abseil, Google Benchmark, Catch2, lyra, unordered_dense, and a histograms library as git submodules · C++23, GCC 14+ or Clang 19+, CMake 3.30+ · x86-64 with AVX2 (Intel Haswell 2013+ / AMD Excavator 2015+); built and tested on Linux only

**Vs siblings:** Pick this over tlx::btree_map or boost::container::flat_map/flat_set when the workload is specifically very large (multi-million element), int64-keyed trees on x86-64 Linux and hugepages are available to configure; its P99.9 gains at 10M elements are larger than tlx's reported multiset comparisons and target a size range boost's flat_set (best at 2-256 elements) doesn't cover. Prefer tlx or boost instead for portability, small-to-mid-size trees, or a longer track record than a single-author work-in-progress.

**Gotchas:**
- Header docs state some operations invalidate all iterators — no red-black-tree-style iterator/pointer stability like std::map
- A closed bug (issue #47) found incorrect SIMD comparison semantics for composite and unsigned key types — fixed, but signals SIMD comparator correctness needs care for non-trivial key types
- The hugepage allocator needs OS-level hugepage configuration; without it the library is still faster than std::map but by a much smaller margin than the headline numbers
- The benchmarked 'winner' configuration (SIMD search + hugepage allocator, specific leaf/internal node sizes) is one tuned instantiation — other node-size/SearchMode combinations are meaningfully slower

**Status:** Actively developed (last commit 2026-01-06, all filed issues closed) but explicitly a single-author work-in-progress built with heavy AI-agent assistance; BSD-3-Clause and header-only make it cheap to vendor, but expect API and behavior churn before treating it as stable.

[repo](https://github.com/kressler/fast-containers) · [benchmark](https://github.com/kressler/fast-containers/blob/main/results/btree_benchmark_results.md)

##### tlx::btree_map / btree_set / btree_multimap (STX B+Tree lineage)  `C++`  `BSL-1.0`  `stale`  `Tier A`

Header-only B+ tree implementing STL's map/set/multimap/multiset; beats libstdc++'s red-black tree at large n.

**Beats:** std::map, std::multiset — Evidence tier A: the author's own STX-btree/tlx speedtest (code public in tests/container/btree_speedtest.cpp) measured random-integer multiset insert-only, insert+find+erase, and find-only workloads at n from 125 to tens of millions against libstdc++'s std::multiset/std::multimap (red-black tree). Per the benchmark page (fetched this session): the 2007 run (g++ 4.1.2, -O3 -fomit-frame-pointer, Pentium 4 3.2GHz) showed the red-black tree taking almost 2x as long as a 32-slot B+ tree above roughly 1,024,000 items; the 2011/2013 reruns (gcc 4.4.5/4.5.0, Core i7 9xx, -O3 with -fomit-frame-pointer or -march=native) show the same divergence starting near 100,000 items. The input record additionally reports a 2019 in-repo results PDF (btree_speedtest_results.pdf, not opened by me this session) showing tlx::btree_multiset roughly 3x faster than std::multiset by n=2^26, with no hardware/compiler stated for that run.

**How:** Leaf and inner nodes are sized by btree_default_traits to hold as many keys as fit in roughly a 256-byte block, so a comparison step touches one cache line instead of the one-key-per-node layout of a red-black tree. Leaves store keys and their associated data in two separate parallel arrays rather than an array of key/value pairs, and descent does an in-node search over a wide node instead of following per-key left/right/parent pointers. Net effect: fewer pointer-chasing cache misses per operation at large n, at the cost of more in-node comparisons per level.

**Use it when:**
- Large (roughly >100k-1M+ element) in-memory ordered map/set/multiset/multimap of cheaply-comparable keys (e.g. integers) where insert, find and erase are all exercised and cache-miss-bound traversal dominates.
- You want an STL-like drop-in-ish replacement for std::map/std::set without taking on SIMD or hugepage requirements.
- You need sorted-order range queries (lower_bound/upper_bound/equal_range) alongside point lookups; B+ tree leaves are linked so range scans stay cheap.
- You can vendor a small BSL-1.0 header (or the wider tlx repo) instead of a heavier dependency.
- Your workload includes bulk-loading a pre-sorted range into an empty container (bulk_load()).

**Skip it when:**
- You rely on std::map's pointer/reference/iterator stability across insert/erase; tlx's B+ tree gives no such guarantee.
- You need C++17/20 map features: emplace, try_emplace, insert_or_assign, extract, merge, or node_type/heterogeneous lookup; none appear in btree_map.hpp.
- You need move construction/assignment on the container itself; only a copy constructor, copy assignment, and swap() are defined in the header I read.
- Small containers (tens of elements or fewer); none of the record's benchmarks show a win below tens of thousands of items, and boost::flat_set/flat_map targets exactly that small-size regime.
- You need erase(first,last) or lock-free/concurrent access; range-erase is unimplemented (only aborts under a debug-only macro) and no synchronization is documented or visible in the header.

**Integration:** header-only (for the btree containers themselves; the wider tlx repo also builds a small static/shared libtlx for unrelated modules like digest/string helpers, but tlx/container/btree*.hpp are pure templates with no matching .cpp in LIBTLX_SOURCES) · none for normal insert/find/erase use (README states zero external dependencies; btree.hpp only includes <algorithm> <cassert> <cstddef> <functional> <iterator> <memory> <utility> and tlx/die/core.hpp). Caveat: verify() and the self_verify trait call tlx_die_unless() -> die_with_message(), which is declared in tlx/die/core.hpp but defined only in tlx/die/core.cpp, so using invariant verification requires linking libtlx or compiling that one file yourself. · C++11 minimum. Root CMakeLists.txt auto-probes compiler flags, preferring -std=c++20 and falling back through c++17/c++14/c++11/c++0x. CI (.github/workflows/cmake.yml) builds with GCC 7.5, 9.3 (incl. -m32), 11, 13 and Clang 15 on macOS 13-15; requires CMake >= 3.7. · x86-64 and 32-bit x86 on Linux, and macOS (Clang) are exercised in the GitHub Actions matrix I read; a Windows job exists in that same file but is commented out/disabled. README claims general portability ('smartphones, supercomputers, windows, etc.') and the README badge references a separate AppVeyor Windows build, which I did not open this session.

**Vs siblings:** Pick tlx::btree over fast-containers, S+/S-tree, or boost::container::flat_set/flat_map when the workload is genuinely dynamic (both insert and erase, not build-once-then-query) at large scale (roughly >100k-1M items) and you want a permissively licensed (BSL-1.0), dependency-free header with no SIMD/AVX/hugepage requirement; prefer S+/S-tree if the workload is static (bulk-built once, then read-only lower_bound queries), fast-containers if you can require SIMD+hugepages for its larger, more recently measured wins at 10M-element scale, or boost::flat_set/flat_map if containers stay small (roughly 2-128 elements).

**Gotchas:**
- verify()/self_verify require linking tlx/die/core.cpp (or libtlx) for die_with_message(); not fully header-only if you use invariant checking.
- No move constructor or move-assignment on btree_map/btree_set — only copy constructor, copy assignment, and swap() are defined.
- erase(first, last) is unimplemented: it only exists (and aborts) if TLX_BTREE_TODO is defined, otherwise the method is absent entirely.
- No iterator/pointer stability guarantee across insert/erase, unlike std::map/std::set — don't hold iterators or pointers across mutations.

**Status:** Stale: last commit 2025-01-10 per the record, and the only open GitHub issue I found (#62) concerns the unrelated d_ary heap, not btree. BSL-1.0 licensed (unlike the GPL-3.0 predecessor stx-btree) and small enough to vendor as a handful of headers — copyable per the record's usability field.

[repo](https://github.com/tlx/tlx) · [benchmark](https://panthema.net/2007/stx-btree/speedtest/)

#### priority-queues-heaps

##### prio_queue (rollbear)  `C++`  `BSL-1.0`  `stale`  `Tier A`

Header-only B-heap priority queue storing priority/payload in separate arrays; faster than std::priority_queue on cache-friendly workloads.

**Beats:** std::priority_queue — On an Intel Core i7-4500U (Ubuntu 15.04, 32KB L1d, 64B cache lines) with g++ 4.9.3 -O3 -std=c++14 against libstdc++'s std::priority_queue, the author's blog graphs (no numeric text given) show the B-heap 'always faster' than std::priority_queue<int> across all tested mini-heap sizes (8/16/32/64), and 'consistently much faster' than std::priority_queue<pair<int,int>> when priority/payload are split into separate arrays, over 320 push+pop cycles at increasing queue sizes; the same post reports worse-or-comparable results for a std::pair<int, unique_ptr<msg>> payload.

**How:** Core technique is a B-heap layout (mini-heap size tunable as a power of two, e.g. 8/16/32/64) that groups a node's ancestors/descendants into the same cache line, cutting the cache misses a plain array-backed binary heap incurs on deep trees. It pairs this with a 'structure of arrays' split of priority and payload (a custom skip_vector) so comparisons during sift only touch the small, dense priority array and never pull large payload objects into cache. GCC builds additionally use __builtin_expect branch hints on the hot sift loops.

**Use it when:**
- Hot push/pop loops (event queues, schedulers, simulations) with small trivially-copyable priority keys (e.g. int) where std::priority_queue's array-of-struct layout causes cache misses
- Workloads where priority and payload can be stored/passed separately via push(key, value) rather than bundled into one pair/struct
- Throughput-oriented benchmarking over many push+pop cycles rather than a single latency-critical operation
- x86-64 GCC/Clang, C++14+ codebases willing to tune miniheap_size to the target cache line size (64 bytes in the reference hardware)
- Projects that want a dependency-free single header they can vendor without pulling in a build system

**Skip it when:**
- Payload is a large or non-trivial type such as std::pair<int, std::unique_ptr<msg>> — the author's own benchmark shows this configuration can be worse than or comparable to std::priority_queue
- You need a stable ordering among equal priorities — it's an unstable B-heap (confirmed by the maintainer in issue #2); add a discriminator field if insertion order matters
- You rely on container-adaptor features std::priority_queue doesn't even need to promise here but users may expect: iterators, merge, or swap are not implemented
- Concurrent/multi-threaded access — thread safety is not documented and there is no internal synchronization
- You need active maintenance: no CI/CMake in the repo, no open issues or PRs, last commit 2025-09-18, and the maintainer said in 2022 he'd probably just use std::vector<> if writing it today

**Integration:** header-only · none for the library itself (only <vector>, <cassert>, <tuple>, <cstddef>); self_test.cpp and perf_benchmark.cpp additionally pull in Catch2, trompeloeil, and the author's own tachymeter benchmarking header, but none of those are needed to use prio_queue.hpp · C++14 (uses std::enable_if_t); originally built and benchmarked with g++ 4.9.3 -O3 -std=c++14 · any (portable C++, no SIMD/intrinsics); __builtin_expect is used under __GNUC__ with a no-op fallback elsewhere; miniheap_size should be tuned to the target's cache line size (64 bytes assumed in the reference benchmarks)

**Vs siblings:** Pick prio_queue when priorities are not monotonically non-decreasing (not a Dijkstra-style access pattern), you need an arbitrary Compare rather than radix bucketing, and you want a tiny dependency-free C++ header. Prefer radix-heap/RadixHeap or S3Q when your workload fits their monotonic-priority or graph-search assumptions — they report larger, more concretely quantified speedups (radix-heap 1.2-1.7x, S3Q 4.6-7x) than this entry's graph-only, unstated ratios.

**Gotchas:**
- Not a stable sort: equal-priority elements are not ordered by insertion (maintainer confirmed in issue #2); add an insertion-sequence discriminator to Prio if you need stability
- miniheap_size must be a power of two and matched to the CPU cache line / Prio size for the claimed gains; size 8 was 'consistently bad' in the author's own tests
- The speedup depends on splitting priority and payload into separate push(key, value) calls; storing both in one struct/pair defeats the optimization and can be slower than std::priority_queue
- Exception guarantee is conditional: strong guarantee only if Prio and Value have noexcept move constructors/assignment; otherwise only the weak guarantee (per README)

**Status:** Stale: last commit 2025-09-18, no open issues or PRs, and no CI/CMake in the repo, but it's a single BSL-1.0 header small enough to vendor and re-benchmark yourself; the maintainer noted in a 2022 issue he'd likely design it differently (plain std::vector<>) today.

[repo](https://github.com/rollbear/prio_queue) · [benchmark](https://playfulprogramming.blogspot.com/2015/08/cache-optimizing-priority-queue.html)

##### radix-heap (pair_radix_heap)  `C++`  `MIT`  `abandoned`  `Tier A`

Header-only C++ monotone radix heap: 1.2-1.7x faster than std::priority_queue on Dijkstra shortest-path workloads.

**Beats:** std::priority_queue — Benchmarked as pair_radix_heap vs. libstdc++'s std::priority_queue inside a standard Dijkstra implementation over DIMACS challenge-9 real USA road networks (264K to 24M vertices), compiled with gcc 4.6.3 -O3 on an Intel Xeon E5-2690 0 @ 2.90GHz / 256GB RAM / Linux 3.2.0, averaged over 100 random sources per graph. Pure priority-queue time was 1.40-1.74x faster (e.g. USA-road-t.USA.gr: 1.302186s vs 2.266316s); overall Dijkstra time including edge traversal was 1.12-1.29x faster (e.g. USA-road-t.USA.gr: 3.817832s vs 4.934690s), with the speedup shrinking on the smallest (264K-vertex NY) graphs.

**How:** Instead of a binary heap's comparison tree, it XOR-encodes keys into an order-preserving unsigned representation (internal::encoder, specialized for signed ints and IEEE float/double) and buckets each pushed key by the index of the highest bit where it differs from the last-extracted key (internal::find_bucket, via __builtin_clz/__builtin_clzll). Because extraction is monotone, popping only needs to redistribute the single lowest non-empty bucket into finer buckets one level at a time, rather than the O(log n) sift-down a binary heap performs on every pop -- giving O(1) amortized push and O(b) amortized pop where b is the key's bit width. This is the classic Ahuja/Mehlhorn/Orlin/Tarjan (1990) radix-heap algorithm.

**Use it when:**
- Dijkstra's algorithm or other monotone-priority-queue algorithms over non-negative edge/cost weights
- Keys are native signed/unsigned integers or float/double (32- or 64-bit) that internal::encoder already handles
- Graph/grid search at the sizes benchmarked here (roughly 264K to 24M vertices), where the per-pop constant factor on the hot path matters
- Willing to vendor a single ~250-line header rather than pull in a build dependency
- Building with GCC or Clang (the bucket-index trick relies on their __builtin_clz/__builtin_clzll builtins)

**Skip it when:**
- Need a general-purpose priority queue where extracted keys can decrease (A*, event simulation with re-priority, negative edge weights) -- violates the monotonicity assert and corrupts the heap silently in release builds
- Need a custom comparator or non-numeric/composite keys -- there is no comparator template parameter, only the built-in integer/float encoders
- Need MSVC support out of the box -- code depends on GCC/Clang builtins, not verified against MSVC's intrinsics
- Need active maintenance -- no commits since 2015-05-16, single closed issue (a README-language request), CI last validated on gcc 4.8/clang 3.4
- Need in-place decrease-key/update or erase of a pushed element -- not exposed; only push, pop, and clear

**Integration:** header-only · none beyond the C++ standard library (<algorithm>, <array>, <cassert>, <climits>, <cstdint>, <limits>, <type_traits>, <utility>, <vector>) · C++11 (std::array, constexpr, variadic templates, std::piecewise_construct); CI-tested with gcc 4.8 and clang 3.4 per README/Travis badge · GCC/Clang (uses __builtin_clz/__builtin_clzll); not documented or tested on MSVC

**Vs siblings:** Pick radix-heap when the workload is specifically a monotone shortest-path search (Dijkstra-style, non-negative weights) over integer/float keys in C++ -- prio_queue (rollbear) and Superscalar Sample Queue (S3Q) are general-purpose std::priority_queue replacements without the monotonicity restriction and are the better choice when keys can decrease or aren't numeric. If the same monotone-Dijkstra pattern is needed in Rust, use radix_heap_rust instead, since this library has no Rust port.

**Gotchas:**
- push() enforces monotonicity only via assert(last_ <= x); in a release build compiled with NDEBUG a non-monotone push is silently accepted and produces wrong pop order rather than an error
- Each radix_heap/pair_radix_heap instance holds a fixed std::array of digits+1 std::vector buckets as members (33 buckets for 32-bit keys, 65 for 64-bit) -- more per-instance state than std::priority_queue's single vector, though the extra vectors are empty until pushes land in them
- No decrease-key, update, or erase of an already-pushed element -- only push/emplace, pop, top, clear
- Floating-point and signed-integer keys pass through an XOR bit-transform (internal::encoder) before bucketing; this is transparent through the public API but means the class is not usable with arbitrary user-defined key types, only the specializations provided

**Status:** Abandoned since its last commit on 2015-05-16, but MIT-licensed (full license text in README.md, no separate LICENSE file) and a single ~250-line header, so it's cheap to vendor, read in full, and maintain yourself without upstream support.

[repo](https://github.com/iwiwi/radix-heap) · [benchmark](https://github.com/iwiwi/radix-heap/blob/master/example/README.md)

##### SimdQuickHeap  `Rust`  `MIT`  `active`  `Tier A`

SIMD-accelerated Rust priority queue, ~12x faster than std::collections::BinaryHeap on large monotone-key workloads; i32/u32/i64/u64 only.

**Beats:** Rust std::collections::BinaryHeap — On an AMD EPYC 9684X (Zen4), Rust nightly release build (target-cpu=native, fat LTO, single codegen unit), the paper's Table 1 shows SimdQuickHeapAvx2 at 35.6 ns/elem and Avx512 at 32.2 ns/elem versus Rust std::collections::BinaryHeap at 439.6 ns/elem (~12.3x / ~13.7x) on a monotone-key push/pop workload at n=2^25; the gap shrinks to near-parity at n=2^10. No C++ std::priority_queue was benchmarked -- only Rust's BinaryHeap and several C++ competitors (Boost.Heap, S3Q, radix heap, original QuickHeap) via LLM-generated FFI wrappers.

**How:** Uses QuickSelect-style recursive partitioning of elements into buckets by pivot (median-of-3 by default), keeping only the bottom bucket sorted once it drops below a size threshold (N=16), so most of the heap stays partitioned rather than fully ordered. Partitioning and insertion use SIMD (AVX2, or AVX-512 when compiled in) to compare and move several keys per instruction. This avoids the pointer-chasing and cache misses of array/pointer-based binary heaps once the queue exceeds L2/L3 cache, matching the paper's finding that the gap over BinaryHeap is huge at n=2^25 and nearly gone at n=2^10.

**Use it when:**
- Priority queue over i32/u32/i64/u64 keys, large enough to exceed cache (paper's gains are at n=2^25; negligible at n=2^10)
- x86-64 with AVX2 or AVX-512 available at compile time (target-cpu=native / -march=native)
- Monotone or near-sorted key sequences (Dijkstra-like, event queues, radix-heap-style workloads) -- where the paper's largest wins are shown
- Rust code that can pin to nightly (crate currently requires it) and can vendor a small, very new, unaudited crate
- C++ code able to build and statically/dynamically link a Rust cdylib and accept LLM-generated, unreviewed FFI bindings for a throughput win over a naive priority_queue

**Skip it when:**
- Keys can equal the type's MAX value (e.g. u64::MAX): open issue #6 shows pop() can silently return the wrong element because MAX is used internally as an empty-slot sentinel
- Need arbitrary Ord types, custom comparators, decrease-key, iteration, or merge -- only 4 fixed integer types and push/pop are supported
- No AVX2/AVX-512 target, or a stable-Rust-only build (crate needs nightly; issue #3 tracks moving off portable-simd)
- Heap stays small enough to fit in cache: measured advantage over BinaryHeap collapses to near-parity at n=2^10
- Need a mature, widely audited dependency: 35 stars, first public benchmark paper (ESA 2026, arXiv Sept 2026) with no independent replication, and an open correctness bug

**Integration:** crate · Rust: ensure_simd 0.1, rand 0.10, wide 1.2. C++ bindings: none beyond the compiled libquickheap.{so,dylib,a} plus quickheap.h/quickheap.hpp. · Rust nightly (rust-toolchain.toml pins channel = "nightly"); C++17 for the bindings example · x86-64 only; AVX2 or AVX-512 required at compile time. No other architectures documented.

**Vs siblings:** Pick this over prio_queue (rollbear) or radix-heap when working in Rust against std::collections::BinaryHeap with one of the four supported integer key types and a large, cache-exceeding, monotone-ish workload; it is the only sibling using SIMD partitioning and the only one benchmarked directly against S3Q and monotone radix heaps (1.2-2.8x, more representative than the ~12x BinaryHeap figure). Prefer RadixHeap (radix_heap_rust) instead if you need stable-Rust maturity over a nightly-only crate with an open correctness bug.

**Gotchas:**
- Pushing the type's MAX value (e.g. u64::MAX) can corrupt later pop() results -- MAX is used as an internal empty-slot sentinel (issue #6, open, unresolved as of 2026-09-02)
- No LICENSE file in the repo (GitHub reports license: null); MIT is declared only via Cargo.toml's license field
- Requires nightly Rust today; issue #3 (open) tracks replacing portable-simd with the stable `wide` crate
- C++ bindings are explicitly LLM-generated and unreviewed; authors recommend building with panic="abort" so a Rust panic can't unwind across the FFI boundary

**Status:** Actively maintained (last commit 2026-08-26) but very new (ESA 2026 paper, 35 stars) with an open, unresolved correctness bug on MAX-valued keys; usable as a copyable/vendorable crate, but MIT is only declared in Cargo.toml, not backed by a checked-in LICENSE file.

[repo](https://github.com/RagnarGrootKoerkamp/quickheap) · [benchmark](https://arxiv.org/abs/2604.25681)

##### Superscalar Sample Queue (S3Q)  `C++`  `MIT`  `active`  `Tier A`

Header-only C++17 cache-efficient priority queue beating std::priority_queue via batched, sample-sort-style bucket classification.

**Beats:** std::priority_queue — In a push+pop microbenchmark (2^13 to 2^27 elements) measured on GCC 9.3.0 -O3 (Ubuntu 20.04) across an Intel Xeon E5-2650 v2 and an AMD Athlon II X4 635, S3Q's speedup over min(S3QBH tuned binary heap, StdQueue) grows roughly logarithmically with N, reaching 4.6x-7x at the largest sizes; StdQueue in the benchmark harness is literally `std::priority_queue<T, std::vector<T>, std::greater<T>>` (confirmed in benchmarks/include/subjects/StdQueue.hpp), i.e. GCC's libstdc++ std::priority_queue.

**How:** It avoids per-insert branch mispredictions of a plain binary heap by batching pushes/pops and using a branchless, sample-sort-derived splitter classifier (borrowed from ips4o's classifier.hpp) to route items into buckets in bulk. Only a small base-case binary heap (sized to fit L1, `kBufBaseSize`, default ~32KiB/Item) is ever heap-ordered directly; the rest lives in coarser buckets that are split/merged in batches, giving amortized O(1/B log(M/B) N/M) cache misses per operation instead of O(log N) essentially-random accesses.

**Use it when:**
- Large queues (benchmark validated 2^13-2^27 elements) where cache-miss-driven throughput matters more than per-op latency
- Comparison-based key ordering needed with no monotonicity constraint (unlike radix heaps)
- Keys are mostly-unique or have modest duplication (see gotchas)
- C++17 project that can pull in ips4o, range-v3, and xoshiro as build dependencies
- Workload matches push/pop-heavy microbenchmark shape (bulk insert then repeated pop+push)

**Skip it when:**
- Workloads with many duplicate/near-duplicate keys: open issue #15 (opened 2026-04-10, still open) reports a stack overflow inserting millions of identical/near-identical keys; thesis 5.2.1 admits full duplicate-key handling is future work
- Need item keys at the extreme of the key's range (e.g. INT_MIN for i32 keys) — reserved internally as sentinels, confirmed problematic in issue #15
- Need a true drop-in for std::priority_queue's template interface (comparator + container) — S3Q requires a Cfg struct and different construction
- Concurrent/multi-threaded access — no synchronization in the code and thread safety is not documented
- Small queues that fit comfortably in L1 already — the bucket/classifier machinery adds setup overhead a plain heap doesn't need

**Integration:** header-only · ips4o (fork: raphinesse/ips4o, tag s3q.2), range-v3 (pinned commit 6f3d0e2af9ae), xoshiro (Reputeless/Xoshiro-cpp v1.1); benchmarks additionally pull tlx and raphinesse/SequenceHeap · C++17; thesis benchmarks used GCC 9.3.0 -O3. Closed issues #1, #5, #8 record and fix build failures on GCC 12-15 (-Werror=array-bounds, dangling-pointer warnings) · x86-64 tested in the thesis (Xeon E5-2650 v2, Athlon II X4 635); no SIMD intrinsics or arch-specific code visible in the headers I read, so likely portable, but only x86-64 is verified

**Vs siblings:** Pick S3Q over radix-heap/pair_radix_heap when keys aren't monotone or aren't well-suited to radix decomposition, since S3Q is purely comparison-based. Pick it over prio_queue (rollbear) when N is large enough (thesis tested up to 2^27) that cache-miss throughput dominates over a simpler binary-heap implementation; for smaller queues or simplicity, prio_queue's plain-heap approach avoids S3Q's extra dependencies and duplicate-key edge cases. If AVX2/AVX-512 hardware is available and the workload is monotone/constant-size, SimdQuickHeap is reported to beat S3Q itself by 1.4-2.8x.

**Gotchas:**
- Open issue #15 (still open as of 2026-05-27): stack overflow on inputs with large numbers of duplicate/near-duplicate keys; root cause is that overflowing buckets need enough distinct keys to split cleanly
- Item keys must avoid the extreme sentinel values of the key type (e.g. i32::MIN) — reserved internally for range bounds per the issue #15 discussion
- kBufBaseSize/kLogMaxDegree defaults are tuned for a 32KiB, 8-way, 64B-line L1D (per maintainer comment on issue #15); mismatched cache geometry may need retuning for best throughput
- Requires defining a Cfg struct per Item type (Item::key member or custom GetKey functor) — more upfront setup than a comparator-only API

**Status:** Actively maintained (last commit 2026-05-27, three build/correctness issues closed in 2025, one duplicate-key stack-overflow issue still open); MIT-licensed and header-only so it's easy to vendor, but small (7 stars) and the duplicate-key edge case is unresolved.

[repo](https://github.com/raphinesse/s3q) · [benchmark](https://ae.iti.kit.edu/documents/theses/MA-von-der-Gr%c3%bcn.pdf)

#### random

##### cpp_batched_random  `C++`  `MIT`  `active`  `Tier A`

Header-only drop-in std::shuffle replacement that batches multiple Fisher-Yates draws from one 64-bit random word.

**Beats:** std::shuffle — Lemire's 2024-08-17 blog post shuffled std::vector<uint64_t> with std::mt19937_64, comparing std::shuffle to the predecessor batched_random::shuffle_2. On an Apple M2 (Apple/LLVM 15, libc++): 12.4 vs 2.4 ns/element at 10,000 elements and 12.0 vs 2.5 ns/element at 1,000,000 elements (~4.8-5.2x; author says 'four to five times faster'). On Linux with an unspecified Intel CPU (GCC 12, libstdc++): 2.2 vs 1.7 ns/element at 10,000 and 3.5 vs 2.7 ns/element at 1,000,000 (~1.3x; author says 'about 30% faster'). I re-fetched the blog page this session and confirmed these numbers match exactly.

**How:** Instead of drawing one bounded random value per swap like std::shuffle, it extracts up to 6 bounded Fisher-Yates indices from a single 64-bit random word using 128-bit multiply-shift (Lemire's nearly-divisionless bounded-integer method, from Brackett-Rozinsky & Lemire, arXiv:2408.06213), amortizing each call to the underlying generator across multiple index draws. Batch size (2 through 6) is chosen based on how many elements remain, with rejection resampling on detected bias to keep the shuffle unbiased.

**Use it when:**
- Shuffling std::vector/array of trivially swappable elements with std::mt19937_64 (or any URBG with 64-bit output, min()==0, max()==UINT64_MAX).
- Running on libc++ (Apple/LLVM, e.g. macOS/iOS) where std::shuffle's bounded distribution is division-heavy -- biggest measured win (~4.8-5.2x).
- Throughput-sensitive shuffling (Monte Carlo simulations, dataset shuffling, deck/card simulations) where shuffle time is a measurable share of runtime.
- Header-only vendoring is acceptable -- single file, C++20 toolchain, no build-system integration beyond adding the header.
- Array size up to roughly 1 billion elements (technique requires the product of two ranges to fit in 64 bits, per the author).

**Skip it when:**
- RNG is 32-bit (std::mt19937, std::minstd_rand, etc.) -- fails to compile: static_assert requires result_type==uint64_t.
- Already on libstdc++/GCC -- measured gain shrinks to ~30%, may not justify the extra header dependency.
- Need a generic std::shuffle drop-in that works with arbitrary/non-standard URBGs without modification.
- Project is capped at C++17 or lacks 128-bit multiply support (no __uint128_t on GCC/Clang, no <__msvc_int128.hpp> on MSVC) -- CMakeLists.txt requires C++20.
- Tiny project (13 stars, zero issues filed) -- no track record of edge-case bug reports; read the ~120-line header yourself before trusting it in production.

**Integration:** header-only · none (standard library only: <iterator>, <concepts>, <type_traits>, <limits>; MSVC build also pulls <__msvc_int128.hpp>) · C++20 (CMakeLists.txt sets CMAKE_CXX_STANDARD 20); needs __uint128_t (GCC/Clang) or MSVC's _Unsigned128 for 128-bit multiply · x86-64, aarch64 (anywhere __uint128_t or MSVC's __msvc_int128.hpp is available); CI covers Ubuntu and Windows (VS2022), blog benchmarks ran on Apple M2; no 32-bit platform support documented

**Vs siblings:** Siblings (PCG, Random123, wjakob/pcg32, xoshiro_cpp, biski64, AESRand, nanobench::Rng) replace the RNG itself; cpp_batched_random keeps whatever 64-bit URBG you already use (even std::mt19937_64) and instead speeds up the Fisher-Yates shuffle built on top of it. Pick this when you must keep std::mt19937_64 for reproducibility or statistical-quality reasons but still want faster shuffling, or stack it on top of a sibling 64-bit generator for compounding gains.

**Gotchas:**
- static_assert enforces result_type==uint64_t, min()==0, max()==UINT64_MAX at compile time -- passing std::mt19937 (32-bit) is a compile error, not a runtime one.
- Requires 128-bit multiplication (__uint128_t on GCC/Clang, std::_Unsigned128 via <__msvc_int128.hpp> on MSVC) -- a compiler/platform requirement beyond just C++20.
- The blog's headline numbers (4.8-5.2x on libc++, ~1.3x on libstdc++) were measured against batched_random::shuffle_2 in a 2024 prototype header, the direct predecessor of this repo; this repo's current batched_random::shuffle uses the same technique (multi-index batches from one 64-bit word) but was not itself the subject of those published numbers.
- The repo's own benchmarks/benchmark.cpp runs the identical std::shuffle vs batched_random::shuffle comparison but publishes no results in the repo -- you must build and run it yourself.

**Status:** Active (last commit 2026-02-28), dual MIT / Apache-2.0-with-LLVM-exception licensed, single ~120-line header with zero open issues and only 13 stars -- small enough to read in full and vendor directly.

[repo](https://github.com/lemire/cpp_batched_random) · [benchmark](https://lemire.me/blog/2024/08/17/faster-random-integer-generation-with-batching/)

##### PCG (pcg-cpp)  `C++`  `Apache-2.0`  `abandoned`  `Tier A`

Header-only C++11 PCG-family RNG beating std::mt19937/std::mt19937_64 raw-generation throughput by ~2.6-4x.

**Beats:** std::mt19937 / std::mt19937_64 — On zeFresk/cpp-random-benchmarks (Google Benchmark, pcg-cpp pinned at commit 428802d, clang -O3 -DNDEBUG, Intel Core i5-3570, no AVX2): pcg32_fast measured 1071.97M generations/s vs std::mt19937's 270.65M/s (~3.96x), and pcg64_fast measured 763.50M/s vs std::mt19937_64's 294.26M/s (~2.59x). Which C++ standard library (libstdc++ vs libc++) backed the std::mt19937 baseline is not stated in the benchmark.

**How:** Each engine keeps a small 64-bit or 128-bit linear/multiplicative congruential generator (LCG/MCG) state, permuted through an output function (XSH-RR, XSL-RR, XSH-RS) on every call, instead of Mersenne Twister's ~20,000-bit state array and tempering step -- so a generated value costs one multiply-add plus a permute rather than a big-array update. The benchmarked '_fast' variants are MCG-based (pcg32_fast = mcg_xsh_rs_64_32, pcg64_fast = mcg_xsl_rr_128_64): they drop the increment/stream-selection add that the default setseq/oneseq engines perform every step, shortening the instruction path at the cost of a single fixed stream per type.

**Use it when:**
- Raw uint32_t/uint64_t generation is the bottleneck (Monte Carlo inner loops, procedural generation, shuffling large arrays) and you don't need many independent streams.
- Code already consumes std::uniform_int_distribution or other <random> distributions -- PCG engines satisfy UniformRandomBitGenerator so distributions work unchanged.
- Non-cryptographic use where 64-bit (pcg32_fast) or 128-bit (pcg64_fast) internal state is acceptable.
- You can vendor a small, unmaintained header-only library (Apache-2.0/MIT dual-licensed) rather than depend on an actively-updated package.
- You want tunable stream separation later (setseq/oneseq/unique variants) without changing the surrounding API shape, if you outgrow the fast/MCG variant.

**Skip it when:**
- You need many statistically independent streams (e.g. one RNG per thread/worker) -- pcg32_fast/pcg64_fast are MCG-based with a single fixed stream; use the setseq variants (pcg32/pcg64) instead, at lower throughput.
- Cryptographic or security-sensitive randomness is needed -- PCG is not a CSPRNG and issue #27 ('Seed securely by default') is still open, so default seeding is not secure by default.
- Your code relies on seed()/set_stream() being independent -- issue #94 documents that calling seed() or seed(itype) on pcg32/pcg64 resets the stream to the default, silently discarding a previously-selected stream.
- You need an actively maintained upstream -- last commit 2022-04-08; issue #106 (Dec 2025) proposes a third-party fork (Total-Random/pcg-cpp) for Windows ARM64/MSVC/128-bit-fallback fixes that are unmerged upstream.
- You're touching custom seeding/streaming edge cases without testing -- several other open issues (#85, #91, #102) report surprising stream-selection/repeat behavior in specific variants; verify your exact typedef and seeding path.

**Integration:** header-only · none (pcg_random.hpp includes pcg_extras.hpp and pcg_uint128.hpp from the same repo, no external deps) · C++11 · any; uses __SIZEOF_INT128__/compiler builtins where available and has MSVC-specific intrinsic paths for 128-bit ops in pcg_uint128.hpp, but community issue #106 reports unmerged fixes needed for Windows ARM64 and some MSVC/128-bit-fallback cases

**Vs siblings:** Pick imneme/pcg-cpp over wjakob/pcg32 when you need 64-bit generation or explicit stream-separation strategies (oneseq/setseq/unique/mcg, extended k-dimensional generators) -- wjakob/pcg32 is a smaller single-header 32-bit-only PCG (940M gen/s, ~3.47x) with less machinery. Pick it over xoshiro_cpp when you want PCG's settable-stream model (C++11 SeedSequence support, per-stream selection) rather than xoshiro256++'s larger 256-bit-state, no-stream-argument design, even though xoshiro256++ measured similarly (946M gen/s, ~3.22x) on the same benchmark suite.

**Gotchas:**
- pcg32_fast/pcg64_fast are MCG-based (mcg_xsh_rs_64_32 / mcg_xsl_rr_128_64): one fixed stream per instance, no per-object stream selection.
- seed() and seed(itype) on pcg32/pcg64 reinstall the default stream, discarding any stream previously set via set_stream() (issue #94, open).
- No secure-by-default seeding -- issue #27 (open) asks for default construction to seed from OS entropy; currently you must seed explicitly.
- Repository is a reference implementation with many similarly-named typedefs (pcg32 vs pcg32_oneseq vs pcg32_fast vs pcg32_k64 ...); picking the wrong one changes both speed and stream-independence guarantees.

**Status:** Abandoned upstream -- last commit 2022-04-08, more than 3 years with no update; Apache-2.0/MIT dual-licensed and small enough to vendor as-is. A community fork (Total-Random/pcg-cpp, referenced in issue #106) exists for modern-platform fixes but is not merged upstream.

[repo](https://github.com/imneme/pcg-cpp) · [benchmark](https://github.com/zeFresk/cpp-random-benchmarks)

##### wjakob/pcg32  `C++`  `Apache-2.0`  `abandoned`  `Tier A`

Tiny two-header PCG32 RNG beating std::mt19937 on speed, with an optional AVX2 8-wide variant.

**Beats:** std::mt19937 — In the zeFresk/cpp-random-benchmarks shootout (clang, -O3 -DNDEBUG, no -march flag, Intel i5-3570 @ 3.40GHz, 100 repetitions), pcg32::nextUInt averaged 940.39M gen/s vs std::mt19937's 270.65M gen/s (~3.47x). pcg32_8 measured 944.20M gen/s, but since this CPU has no AVX2, that number reflects the header's scalar 8-instance fallback path rather than the intended vectorized path.

**How:** Implements the PCG technique: a 64-bit linear congruential state advanced each step, with an XSH-RR permutation (xorshift on the high bits, then a data-dependent rotate) producing the 32-bit output. The 16-byte state and few-instruction step are cheaper than MT19937's 624-word state and tempering. pcg32_8 vectorizes eight independent PCG32 streams with AVX2 (32-bit lane multiplies via partial products, permutevar8x32 lane shuffles, variable-shift rotate) to emit 8 outputs per step on capable hardware.

**Use it when:**
- Bulk generation of 32-bit random values for non-cryptographic use (simulations, games, sampling)
- Need jump-ahead/jump-back (advance()) or stream-distance queries that std::mt19937 doesn't offer
- Want to vendor a tiny, dependency-free source drop (two headers) instead of linking a library
- Target CPU has AVX2 and the workload can batch draws 8 at a time (pcg32_8)
- MT19937-class statistical quality is sufficient; cryptographic security is not required

**Skip it when:**
- Cryptographic or adversarial contexts — neither PCG32 nor MT19937 is designed for that
- Need a native 64-bit output engine — this repo only has 32-bit pcg32 (use imneme/pcg-cpp for pcg64 variants)
- Code needs to satisfy std::uniform_random_bit_generator (e.g. pass the engine to std::uniform_int_distribution or std::shuffle) — pcg32 has no operator() or static min()/max()
- Building for a CPU without AVX2 while expecting the pcg32_8 speedup — it silently compiles to the scalar 8-instance fallback with no warning
- Need active upstream maintenance — no commits since June 2016 and an open 'Missing LICENSE' issue since 2021

**Integration:** header-only · none beyond the STL (pcg32.h: <inttypes.h>, <cmath>, <cassert>, <algorithm>; pcg32_8.h additionally: <immintrin.h>, <utility>, and includes pcg32.h) · not documented — no CMakeLists or pinned language standard; code uses only C++11-era features · pcg32.h: any platform with a C++ compiler; pcg32_8.h: x86-64 with AVX2 (guarded by #if defined(__AVX2__)), else compiles a portable scalar fallback

**Vs siblings:** Pick this over pcg-cpp (imneme/pcg-cpp) when you want the smallest possible PCG32-only source drop (two headers, no build system) rather than the full PCG engine family. On the same benchmark, pcg-cpp's pcg32_fast is about 14% faster (1071.97M vs 940.39M gen/s) and adds 64-bit engines, so prefer pcg-cpp when raw throughput or 64-bit output matters more than minimalism.

**Gotchas:**
- pcg32_8's AVX2 path is selected purely by the __AVX2__ macro at compile time; forgetting -mavx2 (or /arch:AVX2) silently yields the scalar fallback with no warning or error
- No operator()/min()/max(), so it can't be used as a standard UniformRandomBitGenerator with <random> distributions — use its own nextUInt(bound) or shuffle() instead
- Apache-2.0 is only stated in file header comments; there is no root LICENSE file, so GitHub reports 'no license' and an open issue (#2, 'Missing LICENSE', filed 2021) is still unresolved
- advance() and operator- assume both generators share the same inc (stream) value; this is only checked via assert(), which is compiled out in NDEBUG/release builds

**Status:** Abandoned since June 2016 (no further commits; an open 'Missing LICENSE' issue since 2021) but Apache-2.0-licensed (declared in file headers only) and small enough — two headers — to vendor as-is.

[repo](https://github.com/wjakob/pcg32) · [benchmark](https://github.com/zeFresk/cpp-random-benchmarks)

##### xoshiro_cpp (david-cortes)  `C++`  `CC0-1.0`  `abandoned`  `Tier A`

Header-only xoshiro256++/128++ wrapper that drop-in replaces std::mt19937(_64) for <random> distributions.

**Beats:** std::mt19937_64 — On zeFresk/cpp-random-benchmarks (Google Benchmark, 100 repetitions, clang -O3 -DNDEBUG, no architecture-specific flags, Intel i5-3570 @ 3.40GHz), xoshiro256++ generated 946.70M 64-bit values/s vs std::mt19937_64's 294.26M/s, about 3.2x, with both the benchmark source (src/xoshiro.cpp comparing directly against src/std.cpp) and the results table publicly readable.

**How:** Uses the xoshiro256++/128++ algorithm (Blackman & Vigna, 2019): a 256-bit (or 128-bit) state advanced with a few XORs, shifts and rotates per step, with a rotate-add-rotate output scrambler, no division and no large lookup tables, and a state small enough to sit in registers/L1 versus MT19937's ~2.5KB table and its tempering step. On the linked benchmark this measured 946.7M gen/s vs std::mt19937_64's 294.3M gen/s on the same hardware/compiler.

**Use it when:**
- Need higher raw 64-bit generation throughput than std::mt19937_64 for simulations, statistical/ML model initialization, or Monte Carlo work while keeping <random>-engine compatibility (distributions, std::shuffle)
- Want a much smaller generator state (32 bytes vs ~2.5KB for MT19937), e.g. per-thread or per-object RNG instances, or many concurrent generator states
- Need independent parallel streams: jump()/long_jump() advance the state by the canonical 2^128/2^192-draw offsets to split into non-overlapping subsequences (both methods and the correct jump-polynomial tables are present in xoshiro.h, confirmed by reading the source this session)
- Willing to vendor a single ~400-line public-domain header with no build step and no dependencies beyond the STL
- Non-cryptographic use where BigCrush-class statistical quality is enough

**Skip it when:**
- Need cryptographic-strength randomness: xoshiro256++ is explicitly not a CSPRNG
- Need output bit-for-bit reproducible with the reference prng.di.unimi.it implementation for a given integer seed: this wrapper's seed(uint64_t) path deliberately differs from the canonical seeding recipe (stated in the README)
- Rely on generator equality comparisons: operator== in both classes is implemented as a bare `return std::memcmp(...)` without comparing to 0, so it reports mismatched states as equal and identical states as unequal (verified by reading xoshiro.h this session) — do not use it
- Need an actively maintained or widely-adopted dependency: single-star, single-file personal project, no commits since 2021-09-08, no LICENSE file (CC0 notice only in source/README)
- Need runtime-selectable, arbitrary-count independent streams the way PCG offers (per-instance odd increment); xoshiro here only offers the two fixed jump offsets

**Integration:** header-only · none (STL only: <iostream>, <cstring>, <cstdint>) · C++11 (per README); code compiles conditionally for C++20 to drop the explicit operator!= · any — portable C++ using bit rotations and memcpy, no SIMD or architecture-specific intrinsics; benchmark itself ran on x86-64

**Vs siblings:** Pick this over PCG (pcg-cpp / wjakob pcg32) when you specifically want the xoshiro256++ statistical profile with built-in jump()/long_jump() streams in one dependency-free header; on the same benchmark PCG's pcg64_fast is slower (763.5M/s) while pcg32_fast is faster but 32-bit only (1072M/s). If raw throughput matters more than the specific algorithm, AESRand (27-34 GB/s, requires AES-NI) or biski64 (~2.5x std::mt19937_64) beat xoshiro256++ by a wide margin on their own benchmarks.

**Gotchas:**
- operator== is `return std::memcmp(...)` without `== 0`, so it evaluates backwards (identical states compare unequal, differing states compare equal) — confirmed in xoshiro.h this session; don't use it for equality checks
- Default-constructed instances start from a fixed hardcoded state (not randomly seeded), the same gotcha as std::mt19937's default constructor — call seed() explicitly for non-deterministic output
- Seeding logic is intentionally different from the canonical prng.di.unimi.it recipe (README: 'small change in the seeding logic'), so output won't match the reference C implementation for the same integer seed
- No LICENSE file in the repo, only a CC0 dedication noted in the README and the source header comment — a compliance process that requires an actual LICENSE file will flag this

**Status:** Abandoned since its last commit on 2021-09-08 (1 star, 1 fork, 0 open issues, no PRs) but it's a single ~400-line CC0/public-domain header with no LICENSE file — trivial to vendor and audit, so the lack of maintenance is low-risk beyond the license-file gap.

[repo](https://github.com/david-cortes/xoshiro_cpp) · [benchmark](https://github.com/zeFresk/cpp-random-benchmarks)

##### Random123  `C++`  `BSD-3-Clause`  `abandoned`  `Tier B`

Header-only counter-based CPU/GPU RNG family (Philox, Threefry, ARS); only AES-NI variants clearly beat std::mt19937_64.

**Beats:** std::mt19937_64 — In the peer-reviewed SC11 paper's Table 2 (confirmed directly from the PDF), on a 3.07GHz quad-core Xeon X5667 (Westmere) with gcc 4.5.3 and no stated optimization flags, std::mt19937_64 (the C++0x/libstdc++ engine) ran at 6.1 GB/s; the AES-NI-accelerated ARS-7 reached 11.1 GB/s (~1.8x) and ARS-5 reached 17.8 GB/s (~2.9x), while the portable, no-special-hardware Threefry-4x64-20 reached 6.4 GB/s, only a marginal ~1.05x.

**How:** Because each call is a pure function of (counter, key) with no state to read-modify-write, the generators vectorize and parallelize trivially and avoid the roughly 2.5KB of per-thread state std::mt19937 needs. ARS and AESNI reuse the hardware AES-NI round function directly, so on supporting CPUs ARS-7 needs only about 1.1 cycles/byte (ARS-5 about 0.7). Threefry (ARX rounds derived from the Skein/Threefish hash) and Philox (Feistel network plus one wide integer multiply per round) get most of their speed from a handful of cheap integer ops per output word rather than a large state-shuffle step.

**Use it when:**
- Monte Carlo / stochastic simulation workloads needing millions of independent, reproducible streams addressed by (counter,key) instead of stored per-thread generator state
- CUDA/OpenCL/Metal GPU kernels or heavily multithreaded CPU code, where per-thread state size and synchronization matter more than single-core throughput
- x86 CPUs with AES-NI, where ARS-7/ARS-5 give a real ~1.8x-2.9x throughput win over std::mt19937_64 (11.1-17.8 GB/s vs 6.1 GB/s)
- Checkpoint/restart or exact cross-run/cross-platform reproducibility, since output depends only on (counter,key), not call history

**Skip it when:**
- CPU-only code without AES-NI and no tolerance for a marginal win: the portable Threefry-4x64-20 is only about 1.05x std::mt19937_64 (6.4 vs 6.1 GB/s), and several Philox variants are slower than mt19937_64 on CPU
- Code needing a true drop-in std::mt19937/std::mt19937_64 replacement without writing adapter code; the native call shape rng(counter,key) differs from a stateful engine's operator()
- Cryptography or security-sensitive randomness: the README explicitly states these CBRNGs, despite being built from cipher-like primitives, are not suitable for crypto
- Projects wanting active upstream support: last commit on main was 2022-01-17, and open issues (NVCC optimization flags, RISC-V/LoongArch/HIP ports) have sat unanswered since 2022-2023

**Integration:** header-only · none for the core library; GNU Scientific Library only if using the optional gsl_cbrng/gsl_microrng adapters or the ut_gsl test · a reasonable C99 (C API) or C++98 compiler per tests/README; C++11 needed for the SeedSeq-based seed() overloads in r123::Engine; AES-NI-capable CPU plus compiler intrinsics needed for the ARS/AESNI speedups · x86 (AES-NI required for ARS/AESNI's advantage; a 64-bit-producing-128-bit multiply is needed for the Nx64 Philox variants); also ships CUDA, OpenCL, and Metal kernel code; ARM/RISC-V/LoongArch/HIP support is requested in open issues but not confirmed working

**Vs siblings:** Pick Random123 (ARS-7) over PCG/xoshiro/biski64/AESRand when the workload specifically needs stateless, independently-addressable (counter,key) streams for parallel/GPU Monte Carlo or exact reproducibility across runs; for plain single-threaded CPU throughput with a conventional stateful RNG API, PCG-cpp, wjakob/pcg32, xoshiro_cpp, or biski64 all show larger and more portable speedups over std::mt19937(_64) without requiring AES-NI hardware.

**Gotchas:**
- Engine<CBRNG>'s copy constructor calls fix_invariant() to recompute a cached output block when a sentinel (v.back()!=0) is set — an internal correctness detail worth knowing before subclassing or serializing it
- AESNI/ARS key_type is opaque and must be built from a separate ukey_type via key construction, unlike Threefry/Philox keys which can be used directly
- Philox's Nx64 forms only compile/run on hardware and compilers that support 64-bit multiplication producing a 128-bit result; Nx32 forms are the portable fallback
- README notes Random123 has been reported to use 16 bytes of static memory per CUDA thread, unintentionally, with no workaround given

**Status:** Abandoned: the last commit on main was 2022-01-17 (the repo's 2024-02-15 pushed_at is only a push/metadata timestamp, not a new commit) and several issues opened in 2022-2023 (NVCC optimization flags, new-architecture ports) remain unaddressed; still BSD-3-Clause licensed and header-only, so it is trivial to vendor and freeze regardless of upstream activity.

[repo](https://github.com/DEShawResearch/random123) · [benchmark](https://www.thesalmons.org/john/random123/papers/random123sc11.pdf)

##### xoshiro/xoroshiro generators  `C`  `0BSD (generator sources, e.g. xoshiro256plusplus.c, carry a public-domain dedication plus the 0BSD permission text; not CC0-1.0)`  `active`  `Tier B`

Public-domain xoshiro/xoroshiro PRNG family, faster than std::mt19937_64, not cryptographically secure.

**Beats:** std::mt19937_64 — On the project's own shootout table (gcc 12.2.1, -fno-unroll-loops, no -march=native, i7-12700KF @3.6GHz), xoshiro256++ emits 64 random bits in 0.75ns/0.34 cycles-per-byte versus 1.36ns/0.62 cycles-per-byte for a reference Matsumoto-Nishimura MT19937-64 C implementation (not std::mt19937_64 itself), about 1.8x faster; per the record's verification notes this is corroborated by a peer-reviewed 2021 ACM TOMS paper (arXiv:1805.01407, whose title/authors/thesis I confirmed but whose Table 1 numbers were not visible on the abstract page I fetched) reporting 0.86ns vs 2.19ns on different hardware.

**How:** Each generator keeps 128-1024 bits of state and does a handful of XOR/shift/rotate ops plus one integer add or multiply per call ('scrambled linear' generators), versus MT19937-64's much larger ~2.5KB state array and heavier tempering step. On the project's own shootout (gcc 12.2.1, -fno-unroll-loops, i7-12700KF), xoshiro256++ produces 64 bits in 0.75ns/0.34 cycles-per-byte against 1.36ns/0.62 cycles-per-byte for a reference MT19937-64 C implementation, about 1.8x. The small register-sized state also lets AVX2-vectorized builds run several lanes in parallel (xoshiro256+ drops to 0.19ns/64 bits at 8-wide), though the shootout table itself deliberately avoids -march=native.

**Use it when:**
- Non-cryptographic Monte Carlo / simulation / scientific-computing code generating large volumes of 64-bit random values where throughput matters
- Need many independent parallel random streams (per-thread, per-worker) - jump()/long_jump() give cheap non-overlapping subsequences without reseeding
- Vendoring a tiny, public-domain, single-file generator into a codebase - already the default behind Julia's Random, Rust's SmallRng, Java 17+ java.util.random, .NET 6, Lua, and GNU Fortran
- Replacing std::mt19937_64 in hot loops where its large state and tempering overhead show up in profiles
- Constrained/embedded targets needing a very small generator - xoroshiro128+ is used in Mbed/Zephyr, and 32/16-bit variants exist for smaller word sizes

**Skip it when:**
- Any cryptographic use (keys, nonces, tokens) - explicitly not cryptographically secure; use a CSPRNG (ChaCha20, AES-CTR) instead
- Need a zero-effort drop-in C++ <random> UniformRandomBitGenerator - these are raw C source files, not a std::mt19937_64-compatible class; you wire up seeding and state ownership yourself
- Statistical-test purism: xoshiro/xoroshiro fail a handful of specialized tests despite passing BigCrush overall (e.g. xoroshiro128+ shows a detectable low-bit Hamming-weight dependency after ~5TB of output)
- Code that depends on MT19937's enormous 2^19937-1 period for theoretical guarantees - xoshiro256++'s 2^256-1 period is smaller, though still astronomically large for practical use
- Wanting a conventional maintained repo with issue tracker/CI - this is a hand-maintained personal website distributing source files, not a git project

**Integration:** source-drop (single .c file per generator variant) · none for the core generator (stdint.h only); the separate f2x.c tool is only needed to compute custom/arbitrary jump distances · any C compiler with stdint.h (C99-era); no build system - compile or #include the .c file directly · any platform with the needed integer width (16/32/64-bit variants provided); the reference code has no SIMD/architecture-specific intrinsics, though hand-vectorized AVX2 builds are discussed on the page

**Vs siblings:** no siblings catalogued yet

**Gotchas:**
- Must not seed the state directly from a plain counter/timestamp - guidance on the page is to expand the seed through a different-family generator (SplitMix64), or output quality suffers
- xoroshiro128+'s low output bits have a detectable linear dependency (fails specific tests after ~5TB of output) - use xoroshiro128++ or xoroshiro128** if the low bits matter
- jump()/long_jump() only give fixed 2^128/2^192 strides; arbitrary jump distances require the separate f2x.c polynomial tool
- The all-zero state is a fixed point and invalid for these generators - any custom seeding routine must avoid it

**Status:** Hand-maintained personal website (not a git repo) rather than a conventional software release, marked 'active' with the xoshiro256plusplus.c file last modified June 2026; each generator is a single copy-pasteable public-domain/0BSD-licensed C file, consistent with its 'copyable' usability rating.

[repo](https://prng.di.unimi.it) · [benchmark](https://prng.di.unimi.it/)

#### regex

##### Boost.Regex  `C++`  `BSL-1.0`  `active`  `Tier A`

Header-only successor to std::regex: same backtracking engine, hand-tuned matcher and pooled allocation for real throughput gains.

**Beats:** std::regex — On mariomka/regex-benchmark (g++ 7.5.0, -std=c++11 -O3, Boost 1.65.1 linked via -lboost_regex, Docker ubuntu:bionic on a 2019 MacBook Pro i9), Boost.Regex compiled and matched 3 patterns (Email/URI/IPv4) over the Learn-X-in-Y-minutes corpus in 104ms total versus 1023ms for libstdc++'s std::regex (~9.8x, including compilation time). The independent rust-leipzig regex-performance suite (18 patterns over a ~16MB text file, AMD Threadripper 3960X, compiler unstated) confirmed the same direction on 13 of 14 shared patterns, from ~1.0x up to ~47x, losing on one alternation-heavy pattern ('([A-Za-z]awyer|[A-Za-z]inn)\s').

**How:** Same backtracking-NFA design as std::regex: basic_regex_creator compiles the pattern into a graph of states, then perl_matcher walks it. The implementation is heavily hand-tuned around that: a non-recursive matcher (perl_matcher_non_recursive.hpp) that uses an explicit stack instead of C++ call recursion, a pooled memory-block allocator (mem_block_cache.hpp) that reuses backtracking-stack memory across matches instead of hitting the heap, precompiled character-class bitmaps, and a leading-literal fast-skip so scanning for a required prefix doesn't reevaluate the whole state machine at every position. There is no SIMD and no asymptotic change over backtracking matching -- the win is fewer allocations and tighter C++, and it can still hit catastrophic backtracking on adversarial patterns just like std::regex.

**Use it when:**
- Need std::regex-shaped semantics (ECMAScript/Perl/POSIX syntax, smatch-like results) but higher matching throughput on typical (non-adversarial) patterns.
- Pattern set is compiled once and reused across many inputs, so per-call matching cost dominates over one-time compilation.
- Need the POSIX regcomp/regexec API, MFC string support, or ICU/Unicode string iteration that std::regex does not provide.
- Already on or willing to add Boost (or the standalone header mode) and accept BSL-1.0, for a well-documented ~9.8x total / up to ~47x per-pattern win over libstdc++ std::regex on text-scanning workloads like log or URI/email extraction.
- Building against Boost 1.77+ where the library is header-only, so no extra link step is needed for the core C++ API.

**Skip it when:**
- Patterns come from untrusted input (user-supplied regex or unbounded nested quantifiers/alternation): this is the same backtracking/ReDoS risk class as std::regex, not a safer engine (see GH issue #178, 'Subroutine call backtracking bug').
- Need a hard guarantee of linear-time matching regardless of pattern shape -- pick a DFA/Thompson-NFA engine like RE2 instead of any backtracking engine, including this one.
- Targeting Boost older than 1.77 (before Boost.Regex 6.0.0, 2021) where the library still requires linking a compiled boost_regex lib, as the mariomka benchmark used (Boost 1.65.1, built with -lboost_regex).
- Want a truly zero-dependency drop-in: even in standalone mode you still add a distinct type hierarchy (boost::regex != std::regex); non-standalone mode also pulls in Boost.Config/Assert/Predef/ThrowException.
- Small, one-off, latency-sensitive regex use where std::regex's ubiquity and zero extra header outweigh a ~2x-ish smaller, but still real, integration cost.

**Integration:** header-only · none in standalone mode (BOOST_REGEX_STANDALONE, or auto-detected under C++17 with __has_include when <boost/version.hpp> is absent); otherwise Boost.Config, Boost.Assert, Boost.Predef, Boost.ThrowException. Optional ICU for Unicode string integration. The POSIX C API (src/posix_api.cpp, src/wide_posix_api.cpp) is still compiled/linked separately if used. · C++11 minimum; C++03 support was formally deprecated in 6.0.0/Boost 1.77 (doc/history.qbk). C++17 is only needed for automatic standalone-mode detection via __has_include, not as a hard floor. · any (portable C++; no SIMD/ISA requirement found in headers or docs)

**Vs siblings:** Pick Boost.Regex over RE/flex or REAL when you want an API and feature set (POSIX/ICU/MFC support, Perl/ECMAScript syntax) almost identical to std::regex for an easy migration, rather than adopting a scanner-generator workflow (RE/flex) or a from-scratch header-only engine (REAL/real-regex) for their larger reported multipliers. Unformat is not comparable here -- it only handles fixed-shape format strings at compile time, not general regex.

**Gotchas:**
- Header-only status is recent (Boost.Regex 6.0.0 / Boost 1.77, 2021, confirmed via CMakeLists.txt's `add_library(boost_regex INTERFACE)`); the benchmark numbers in this record used Boost 1.65.1, compiled with `-lboost_regex`, from before that change.
- Same backtracking design as std::regex: pathological patterns can still blow up, with no linear-time guarantee (GH #178).
- Standalone mode drops Boost.Config's compiler-defect workarounds; if you disable exceptions in standalone mode you must define BOOST_NO_EXCEPTIONS yourself.
- Changing the global C locale from one thread while another thread is mid-match is explicitly called out as unsafe in the docs.

**Status:** Actively maintained (last commit 2026-05-22 on the default branch) and BSL-1.0 licensed, so freely copyable/vendorable; GitHub reports a null license for the repo, but the header comments carry the Boost Software License 1.0 text directly.

[repo](https://github.com/boostorg/regex) · [benchmark](https://github.com/mariomka/regex-benchmark)

##### PCRE2  `C`  `BSD-3-Clause WITH PCRE2-exception`  `active`  `Tier A`

Mature C library for Perl-compatible regex matching; 4-12x faster than libstdc++'s std::regex on find-and-count benchmarks.

**Beats:** std::regex — On mariomka/regex-benchmark (non-overlapping find-and-count of email/URI/IPv4 patterns over a learnxinyminutes text corpus; MacBook Pro 16-inch 2019, 2.4GHz Core i9; gcc/g++ 7.5.0, -O3, run in Docker), C PCRE2 10.36-2 totaled 251.37ms without JIT versus libstdc++ std::regex's 1023.49ms (4.07x); with JIT enabled on the benchmark's optimized branch, PCRE2 dropped to 87.87ms (11.6x). Per-pattern and total figures were re-confirmed directly against the benchmark README and both branches' benchmark.c source this session.

**How:** Two matching engines: a default depth-first backtracking interpreter, and an optional JIT (built on the bundled sljit code, checked out as a git submodule) that compiles a pattern to native machine code via pcre2_jit_compile()/pcre2_jit_match(). On the mariomka/regex-benchmark suite the non-JIT interpreter alone already beats libstdc++ std::regex 4.07x (251.37ms vs 1023.49ms total, confirmed against c/benchmark.c which calls plain pcre2_match()); enabling JIT (confirmed against the optimized branch's benchmark.c) widens that to 11.6x (87.87ms).

**Use it when:**
- Need full PCRE/Perl regex syntax (lookaround, recursion, \K, Unicode properties) beyond what std::regex's ECMAScript grammar supports.
- A pattern is compiled once and matched repeatedly against many/large inputs, especially with JIT enabled -- the regime the benchmark measures.
- Building a portable C (not C++) project, or embedding regex support behind an FFI boundary the way PHP/Apache do.
- Can accept an external C library dependency and manual pcre2_code/pcre2_match_data lifetime management instead of RAII.
- Targets one of PCRE2's continuously tested platforms/architectures (Linux, Windows, macOS, BSDs, Solaris, z/OS; x86, ARM, RISC-V, POWER, S390X).

**Skip it when:**
- Want a C++-idiomatic, exception-based, RAII-managed interface -- PCRE2's C API requires manual free() of every code/match-data/context object.
- Need exact ECMAScript regex semantics to stay compatible with existing std::regex-authored patterns.
- Run patterns against untrusted input without setting match_limit/depth_limit -- the default backtracking engine is worst-case exponential time (per pcre2.txt).
- Need rock-solid JIT concurrency today: issue #924 (open) is a ThreadSanitizer-reported data race in JIT stack creation, and #974 (open) documents interpreter/JIT match-result discrepancies.
- Want a single-header drop-in; PCRE2 must be built and linked (CMake, Autoconf, Bazel, or zig build) or vendored as source, not header-only.

**Integration:** static lib | shared lib (also usable as source-drop by vendoring pcre2's .c files directly, per its README) · none for the core library; JIT support additionally requires the bundled sljit git submodule at build time · C99 compiler; CMake or Autoconf/./configure (Bazel and zig build also supported per the README) · Linux, Windows, macOS, FreeBSD, OpenBSD, Solaris, z/OS; x86, ARM, RISC-V, POWER, S390X (others reported to work)

**Vs siblings:** Pick PCRE2 over Boost.Regex when JIT is enabled (87.87ms vs Boost's 104.23ms on this benchmark) or when you need a portable C library rather than a Boost/C++ dependency; pick Boost.Regex instead for a closer std::regex-like C++ interface without JIT's build complexity, or if the default (non-JIT) build is all you can ship (Boost then wins, 104.23ms vs PCRE2's 251.37ms). Pick PCRE2 over RE/flex when patterns are compiled at runtime rather than generated ahead-of-time as a scanner/lexer.

**Gotchas:**
- Default (non-JIT) engine backtracks depth-first and is worst-case exponential time; set match_limit/depth_limit for untrusted patterns or input.
- JIT is opt-in: requires checking out the sljit git submodule and calling pcre2_jit_compile() yourself, or you silently keep using the slower interpreter.
- Open issue #924: ThreadSanitizer flags a data race in get_page_alignment() during concurrent pcre2_jit_stack_create(). Open issue #974: interpreter and JIT can return different match results for some patterns.
- No RAII -- every pcre2_code, pcre2_match_data, and context object must be freed explicitly (pcre2_code_free, pcre2_match_data_free, etc.).

**Status:** Actively maintained (pushed 2026-09-24; the project commits to backporting security and high-severity fixes for at least five years). BSD-3-Clause-with-exception license makes it freely usable and vendorable, but as a C library it must be built and linked (or its .c files dropped into a project) rather than included as a header.

[repo](https://github.com/PCRE2Project/pcre2) · [benchmark](https://github.com/mariomka/regex-benchmark/blob/master/README.md)

##### RE/flex  `C++`  `BSD-3-Clause`  `active`  `Tier A`

Flex-style C++ lexer generator plus a multi-engine regex matcher library; DFA scanners far outrun std::regex, PCRE2, and Boost.Regex at tokenizing.

**Beats:** std::regex — On a 2 KB representative C source file tokenized into 244 tokens, a reflex --fast --noindent generated scanner (RE/flex 3.4.1) measured 8.7 us versus 6490 us for std::cregex_iterator (C++11 std::regex, libc++ inferred from platform) — about 746x faster — measured with clang 12.0.0 -O2 on a 2.9 GHz Intel Core i7 / 16 GB LPDDR3 Mac running macOS 12.6.9. The repo is now at 6.5.0; the std::regex leg was run through RE/flex's own std-ecma matcher adapter with one large alternation pattern rather than a hand-written std::regex loop.

**How:** The native RE/flex regex engine compiles patterns to a DFA using a backtrack-free lazy-matching transformation (credited to Robert van Engelen) that matches in linear time without backtracking, unlike std::regex's NFA engine. Generated scanners run as compact FSM code rather than re-entering a general matching engine per token. Matcher::find() and related search paths additionally use runtime-dispatched SIMD (SSE2/AVX2/AVX512BW on x86, NEON/AArch64 on Arm) to accelerate scanning for the next candidate match.

**Use it when:**
- Tokenizing/scanning a stream into many tokens (lexer/parser front-ends) where std::regex's per-call setup and backtracking overhead dominate
- Building a Flex/Bison-based C++ toolchain and wanting Unicode-aware, POSIX-compliant scanning with less porting effort than plain Flex++
- Need indent/dedent-sensitive tokenizing (Python-like languages) or multi-encoding (UTF-8/16/32, legacy code pages) file input
- Want one API that can fall back to PCRE2 or Boost.Regex for fuller Perl syntax while keeping the fast DFA engine on the hot path
- Large text/file scanning workloads (RE/flex backs ugrep) where guaranteed linear-time DFA matching is preferable to std::regex's backtracking risk

**Skip it when:**
- Need capture groups with RE/flex's own fast engine: not supported natively (open issue #95, only non-capturing groups); must switch to PCRE2Matcher/BoostMatcher/StdMatcher and give up some speed
- Need backreferences or lookaround: the native engine is IEEE POSIX P1003.2-compliant DFA matching, which structurally excludes these (only the PCRE2/Boost adapters support them)
- Only need a handful of ad hoc regex checks in otherwise std::regex-shaped code: the reflex code-generation step plus a libreflex build add more integration surface than warranted
- Pattern shapes with a leading unanchored wildcard (e.g. `.*literal`) used with Matcher::find(): one reported benchmark (#220) showed ~15000x slowdown versus removing the leading `.*`, so verify your actual pattern shape
- Strict correctness under MemorySanitizer: issue #234 reports a use-of-uninitialized-value warning in AbstractMatcher::reset_text() via text()

**Integration:** static lib | shared lib · none required; PCRE2 and Boost.Regex are optional, only needed if you use reflex::PCRE2Matcher or reflex::BoostMatcher · C++11 (CMAKE_CXX_STANDARD 11 in CMakeLists.txt); strview() needs C++17 · Windows, macOS, Linux, NetBSD, BSD; x86-64 with SSE2/AVX2/AVX512BW auto-detected at runtime (configure --disable-avx / --disable-sse2 to turn off), aarch64/NEON supported for search, portable C++ fallback otherwise

**Vs siblings:** Pick RE/flex over Boost.Regex, REAL, or Unformat when the job is generating a real tokenizer/scanner (many tokens per input, Flex/Bison-style workflow) rather than replacing scattered std::regex match/search calls; Boost.Regex and REAL are closer to a source-level drop-in for individual std::regex call sites with far less build/integration surface.

**Gotchas:**
- Native Matcher has no capture groups (non-capturing groups only); this is a known, still-open design gap, not a bug that will be fixed soon
- A leading unanchored `.*` in a pattern used with find() can be ~15000x slower than the equivalent anchored/literal search on the same input (issue #220)
- libreflex is a real build artifact (libreflex.a/.so via configure/make or CMake), not a header you can just #include and go
- SIMD (AVX2/AVX512BW) is auto-detected at runtime by default; disable via configure flags if you hit CPU-detection or build issues on older toolchains

**Status:** Actively maintained (last commit 2026-09-15, now versioned 6.5.0 vs. the benchmarked 3.4.1) and BSD-3-Clause/copyable, but the reflex code-generation step and libreflex build make it heavier to vendor than a header-only std::regex replacement.

[repo](https://github.com/Genivia/RE-flex) · [benchmark](https://github.com/Genivia/RE-flex/blob/master/README.md)

##### RE2  `C++`  `BSD-3-Clause`  `active`  `Tier B`

Linear-time, non-backtracking C++ regex engine beating classic PCRE on untrusted input; loses to PCRE2 JIT and Hyperscan.

**Beats:** PCRE — Third-party NSDI'19 Hyperscan paper (Xeon Platinum 8180, single core, GCC 5.4): RE2 serial mode beat JIT-enabled PCRE 8.41 by ~3.9x on Talos (6942s->1777s) and ~2.7x on ET-Open (12800s->4696s), but lost to JIT-enabled PCRE2 10.32 (1777s vs 394s; 4696s vs 913s) and to Hyperscan by ~9-10x; separately, WG21 paper P1433R0 found RE2 far faster than libstdc++/libc++ std::regex on a 1.3GB CSV scan, though with no hardware/flags stated.

**How:** RE2 compiles a pattern to an automaton and executes it with Thompson-NFA/lazy-DFA style simulation that evaluates all alternatives in parallel instead of backtracking, so match time is asymptotically linear in input length regardless of pattern shape, and there is no catastrophic-backtracking worst case like non-JIT PCRE. It uses no SIMD and no JIT compiler of its own — maintainers closed a request (issue #383) to add x86 SIMD to close the gap with Hyperscan — which is exactly why it loses to PCRE2's JIT and to Hyperscan in the cited benchmark.

**Use it when:**
- Untrusted or user-supplied regex patterns/input where guaranteed linear-time matching (no ReDoS/catastrophic backtracking) is a security requirement.
- Serial single-regex matching against classic non-JIT PCRE as the baseline: measured ~3.9x (Talos) and ~2.7x (ET-Open) faster on the NSDI'19 HTTP-traffic benchmark.
- C++17+ codebases already depending on Abseil that want a mature (production at Google since 2006), widely used (9.8k stars) engine.
- Need safe submatch extraction on adversarial input without recursion/stack-overflow risk.
- std::regex is the actual baseline: third-party WG21 paper P1433R0 found RE2 roughly 9x-160x faster than libstdc++/libc++ std::regex on a 1.3GB CSV scan.

**Skip it when:**
- Need backreferences or lookaround assertions — unsupported by design; a 'bounded lookaround' implementation (issue #585, open since Feb 2026) is only a proof of concept, not merged.
- Raw single-regex throughput matters more than backtracking safety and PCRE2 JIT or Hyperscan is available — RE2 lost to PCRE2 10.32 JIT (1777s vs 394s Talos; 4696s vs 913s ET-Open) and to Hyperscan by 9-10x in the same paper.
- Extracting many capturing groups per match on a hot path — GitHub issue #204 reports captures making RE2 ~10x slower than non-capturing matches, ending up slower than PCRE with captures on.
- Need a PCRE-compatible API/syntax for a true drop-in migration — RE2 requires rewriting call sites and possibly patterns.
- Unicode-heavy patterns where compile time matters — issue #46 reports Unicode regex compilation is noticeably slower; RE2 also does no Unicode normalization itself.

**Integration:** static lib (also buildable as shared lib via CMake/Bazel, or vendored as source via CMake add_subdirectory) · Abseil (required); optional ICU for extended \p/\P Unicode properties (RE2_USE_ICU); GoogleTest + Benchmark needed only to build tests/benchmarks · C++17; build via GNU make, CMake, or Bazel (Bazelisk); Visual Studio 2019+ on Windows · any — Linux, macOS, Windows (VS2019+, MinGW, Cygwin/MSYS); no SIMD or specific-arch requirement documented

**Vs siblings:** Pick RE2 over CTRE when the pattern is runtime-supplied or untrusted (user input, config-driven regexes) rather than known at compile time, or when the toolchain is C++17 without C++20; CTRE beats std::regex by ~10x-125x via compile-time NFA generation but requires the pattern to be a compile-time constant, which RE2 does not.

**Gotchas:**
- Capturing submatches is expensive: issue #204 measured captures making RE2 ~10x slower than non-capturing matches (2800ns vs 250ns in that benchmark), ending up slower than PCRE with captures enabled.
- No SIMD or JIT of its own, so throughput on modern hardware trails PCRE2 JIT and Hyperscan; maintainers closed a request to add x86 SIMD (issue #383).
- Backreferences and lookaround are unsupported by design; 'bounded lookaround' (issue #585) is an open proof-of-concept, not shipped.
- No Unicode normalization: a codepoint form and a combining-character form of the 'same' character won't match unless normalized before use (README).

**Status:** Actively maintained (last commit 2026-01-22, not archived or a fork), BSD-3-Clause, used in Google production since 2006; not header-only but the source is small and copyable/vendorable via CMake add_subdirectory.

[repo](https://github.com/google/re2) · [benchmark](https://www.usenix.org/system/files/nsdi19-wang-xiang.pdf)

#### searching

##### FastBinarySearch  `C++`  `MIT`  `stale`  `Tier A`

Header-only C++ library for O(1)/vectorized insertion-point search in sorted float arrays, beating std::lower_bound scalar and SIMD-batched.

**Beats:** std::lower_bound — On an Intel Xeon E5-2620 v3 (Haswell, 2014) with gcc 7 / libstdc++, the README's own benchmark (2048-element sorted array, single precision) shows the O(1) DirectCacheFMA method at 496.44M scalar searches/s vs std::lower_bound's 14.02M/s scalar -- about 35x, apples-to-apples. The larger '~71x/100x' figures instead compare AVX-2 batched throughput (992.87M/s) against std::lower_bound's scalar-only number, which only reflects real-world gains if the caller actually issues batched queries.

**How:** Its headline technique (Direct/DirectCache, the O(1) family) precomputes a linear scaling function that maps a float key straight to a bucket index in a preprocessed table, replacing comparison-based search with arithmetic and a table lookup for roughly log-uniformly distributed data. Other included algorithms (Eytzinger-layout cache-friendly binary search, branchless BitSet search, k-ary ternary/pentary/nonary search) cut iteration count or branch mispredicts more conventionally. The vectorial() path uses SSE4.1/AVX2 and FMA intrinsics to compute several insertion points per call instead of one.

**Use it when:**
- Repeated point-location queries against the same static sorted float/double array (spline interpolation, ECDF lookup) where upfront index preprocessing pays off
- Queries arrive in batches so the SIMD vectorial() path can be used -- this is where the largest (~35x scalar, ~70x+ batched) gains actually show up
- The array's values are close to log-uniformly distributed across their range, keeping the O(1) Direct index table compact
- Target is x86-64 with AVX2/FMA (or at least SSE4.1) available at compile time
- You can accept a template-heavy, per-array engine object instead of a generic iterator-based lower_bound(first,last,val) call

**Skip it when:**
- You need a generic, iterator-based drop-in for std::lower_bound over arbitrary containers/types -- this only supports float/double arrays via its own engine object
- The array is mutated often -- Direct/DirectCache methods need their index table rebuilt on every change, and preprocessing isn't free
- Target is ARM/other non-x86 -- no NEON/ARM port exists (open, unclaimed issue since 2023)
- Memory is tight -- DirectCache/Direct2 variants need extra memory for the index table on top of the array itself
- Workload is a single occasional scalar query -- realistic scalar-to-scalar gain is ~35x at best (per README numbers), not the headline ~100x figure, which mixes batched SIMD throughput against std::lower_bound's scalar number

**Integration:** header-only · none (STL only); Intel MKL is only an optional comparison target in the benchmark harness, not a library dependency · C++11-class syntax (paper benchmark builds with -std=c++0x); the library's own demo Makefile defaults to -std=c++17. Needs a compiler exposing SSE4.1/AVX2/FMA intrinsics (GCC/Clang -mavx2 -mfma, or MSVC equivalent) for the fast paths · x86-64 (SSE4.1/AVX2/FMA needed for the fastest scalar and all vectorial paths); no ARM/NEON support (issue #2, open, unclaimed as of 2023)

**Vs siblings:** Pick FastBinarySearch when the data is a sorted array of floats/doubles and you can preprocess it once and batch queries -- no sibling here offers an O(1) indexed technique or documented AVX2-batched throughput this large. Pick sb_lower_bound instead when you need a true drop-in, single-query, iterator-based replacement with zero preprocessing (its own gain, ~1.8x, is far more modest but has no setup cost or type restriction to floats).

**Gotchas:**
- A 2020 memory-alignment bug (issue #1) made release/non-DEBUG builds return wrong results for some SIMD levels; the author fixed it and the reporter confirmed correct output on master, but the issue itself is still open on GitHub and this session did not re-derive the fix's correctness independently
- That same issue shows -mavx (plain AVX, no AVX2/FMA) failing to compile on gcc 7 with an 'inlining failed... target specific option mismatch' error -- stick to the FMA/AVX2 or SSE2 SIMDLEVEL options that the README benchmarks actually use
- O(1) Direct/DirectCache methods validate the computed index range and throw std::invalid_argument if the array's value range would overflow a uint32 index, rather than silently corrupting results
- No ARM/NEON port; x86-only today

**Status:** Stale: last commit 2024-12-19 with sporadic activity, and both open GitHub issues (an unclaimed ARM-port request, and a 2020 miscompile report the author says he fixed but never closed) remain open. Still MIT-licensed, header-only, and small enough to vendor; a subset ships in NAG's commercial m01ndc routine, which is some evidence of real-world use beyond the 153 stars.

[repo](https://github.com/fabiocannizzo/FastBinarySearch) · [benchmark](https://github.com/fabiocannizzo/FastBinarySearch/blob/master/README.md)

#### sequence-containers

##### plf::colony (plf::hive)  `C++`  `Zlib`  `active`  `Tier A`

Unordered container beating std::vector/deque/list on erase-heavy workloads via O(1) erase that never invalidates other iterators.

**Beats:** std::vector, std::deque, std::list — Third-party benchmark (Baptiste Wicht, 2017) built g++-4.9.4 -std=c++11 -march=native -O2 on an Intel Core i7-4770 @3.4GHz/Gentoo Linux, comparing plf::colony against libstdc++'s std::vector/deque/list across fill, linear-search, random-insert, randomized iterate-and-erase (1%/50% probability), sort and destruction at element sizes 8B-4096B. At 1% erase probability with 1024B elements colony ran about three orders of magnitude faster than vector/deque; at 50% erase probability with 4096B elements colony was about 361,143x faster than vector. The same post reports colony ~3x slower than a reserved vector for plain 8B fill/back-insertion and ~50% slower than list for linear search.

**How:** Elements live in fixed-capacity memory blocks ('groups') allocated contiguously with a parallel 'skipfield' array; erase() marks the slot in the skipfield and threads it onto an intrusive free list instead of shifting or destroying neighboring elements, making erase O(1) per call regardless of position (vs vector/deque's O(n) shift). The skipfield lets ++/-- jump over erased runs without branching, and empty groups are freed so iteration stays bounded. This avoids the copy/move churn that dominates vector's cost under interleaved random erasure.

**Use it when:**
- Randomized insert/erase interleaved with iteration where other code holds pointers/iterators/references to elements that must stay valid across unrelated erasures (game entity/particle pools, object registries).
- Large element sizes (100s of bytes to multi-KB) under heavy erase churn -- the cited benchmark's largest wins (up to ~361,143x vs vector) occur at 4096B elements with 50% random erasure.
- Erase pattern is effectively random-access, not sequential from one end (where deque/list already do fine).
- Concurrent read+insert to different locations is acceptable per the docs (though iterate+write concurrently is not).
- No need for positional indexing or a defined element order.

**Skip it when:**
- Code relies on operator[] / positional indexing or a stable insertion/iteration order -- colony is explicitly unordered.
- Simple sequential fill / back-insertion of small elements: the cited benchmark measured colony ~3x slower than a reserve()'d std::vector for 8B elements.
- Linear-search-dominated access: colony measured ~50% slower than std::list in the same benchmark.
- Need flat contiguous memory for SIMD/gather-free vectorized access -- colony storage is chunked into blocks, not one array.
- Multithreaded iterate-while-write on the same container: the docs state colony cannot be safely iterated and written to at the same time.

**Integration:** header-only · none (C++ standard library only) · C++98/03 minimum (per README); move semantics and other modern features activate under C++11+; the plf::hive fork requires C++20+ · any (portable standard C++, no architecture-specific intrinsics); ships an MSVC .natvis debugger visualizer

**Vs siblings:** Pick colony/hive over plf::list, eastl::vector, fast_vector, or veque specifically when the workload does heavy random-order erasure while other code needs held pointers/iterators to stay valid -- those siblings speed up ordered, indexable, contiguous-or-node storage (growth/allocation/push_back patterns) but don't give colony's O(1) erase-without-invalidation guarantee.

**Gotchas:**
- erase(it) invalidates the iterator `it` passed to it (like vector) -- must reassign from erase()'s return value; GitHub issue #57 shows a user hitting this by continuing to use a stale iterator.
- Exception safety is the strong guarantee for all allocating operations except operator=, which only offers the basic guarantee: on exception during assignment the colony ends up empty rather than rolled back.
- clear() has been reported (issue #42) as slower than repeated erase() calls in some cases, which is counterintuitive versus typical container expectations.
- Skipfield element width (8-bit vs 16-bit) is chosen automatically from element size/alignment via the 'priority' template parameter, silently affecting per-block memory overhead.

**Status:** Actively maintained (last commit 2026-09-19, days before this review) under the permissive Zlib license, header-only so trivial to vendor into a project; the author now maintains a parallel C++20 fork, plf::hive, tracking the pending std::hive standardization proposal (P0447), so new C++20 codebases may prefer hive while pre-C++20 projects stay on colony.

[repo](https://github.com/mattreecebentley/plf_colony) · [benchmark](https://baptiste-wicht.com/posts/2017/05/cpp-containers-benchmark-vector-list-deque-plf-colony.html)

##### plf::list  `C++`  `Zlib`  `active`  `Tier A`

Node-clustering drop-in replacement for std::list; faster insertion, erasure, sort, and much faster clear/destruction.

**Beats:** std::list — On the project's own benchmark page (MinGW GCC 9.2 x64, -O2 -march=native, Intel Xeon E3-1241 Haswell, libstdc++), plf::list beat std::list by about 333% average insertion throughput, 77% faster sort, 70% faster reverse, 91% faster remove/remove_if, 63% faster unique, and roughly 25% faster in ordered 'real-world' modification scenarios; the multi-order-of-magnitude clear()/destruction gains apply only to trivially-destructible types (811%/1,248% for non-trivial types).

**How:** Each memory block keeps a per-block free list of erased slots; on insertion the algorithm searches outward from the target position for a nearby free slot before falling back to allocating a new block, which keeps blocks dense and cuts allocator calls compared to std::list's one-node-per-element scheme. sort() temporarily gathers node pointers into a contiguous array and quicksorts that array instead of mergesorting the linked list in place, which is faster but not guaranteed stable. clear()/destruction skip per-node destructor calls entirely for trivially-destructible element types, which is why those two benchmarks show multiple-order-of-magnitude speedups that don't generalize to non-trivial types.

**Use it when:**
- Hot paths doing frequent insertion/erasure in the middle of a list-like sequence, where std::list's per-node allocation overhead dominates
- Trivially-destructible or small POD element types, where the clear()/destructor speedups are largest
- Code that needs std::list's pointer/iterator stability under insertion and erasure but wants better cache locality from clustered nodes
- GCC/libstdc++ targets on x86-64 similar to the tested environment (MinGW GCC 9.2, Haswell), where the numbers are verified
- Projects that can vendor two headers (plf_list.h, plf_tools.h) and want C++98-through-C++23 portability without a build step

**Skip it when:**
- Code relying on partial (single-element or range) splicing between two separate list objects — only whole-list splice across instances is supported
- Code that needs a stable sort; plf::list's pointer-array quicksort is explicitly not guaranteed stable, unlike std::list::sort()
- Heavy multi-threaded use beyond simultaneous reads — docs describe only limited concurrency guarantees, not general thread safety
- Anything on libc++ or MSVC STL — only libstdc++ (MinGW GCC 9.2) is benchmarked, so gains on those standard libraries are unverified
- Very large heap-memory scenarios, where the project's own docs say erasure is only 'best... until very large amounts of memory are involved' without quantifying the falloff

**Integration:** header-only · none (bundles plf_tools.h / plf_tools_undef.h from the same repo for compiler-feature detection) · C++98 minimum; auto-detects and uses C++11/14/17/20 features (allocator_traits, variadics, concepts, ranges) when the compiler supports them · any (portable standard C++, no platform-specific code); benchmarked on x86-64 Windows/MinGW GCC 9.2

**Vs siblings:** Pick plf::list over plf::colony/hive when you need std::list's ordered, doubly-linked semantics and its splice/sort/merge/remove API; plf::colony is unordered and only a substitute when insertion order doesn't matter. The other siblings (eastl::vector, fast_vector, veque) target std::vector, not std::list, so they're not alternatives when you specifically need list-style pointer stability and O(1) mid-sequence insertion/erasure.

**Gotchas:**
- sort() is not guaranteed stable, unlike std::list::sort()
- The multiple-order-of-magnitude clear()/destruction speedups apply only to trivially-destructible types; non-trivially-destructible types see 811%/1,248% instead of 1,147,900%/6,350%
- shrink_to_fit() invalidates all pointers, iterators, and references — unlike ordinary insertion/erasure on plf::list
- Splicing an iterator to its own position is undefined behavior, matching std::list (raised as issue #34, closed by the maintainer as user error/UB, not a bug)

**Status:** Actively maintained (last commit 2026-09-19; all 29 historical GitHub issues are closed) and Zlib-licensed, so it's low-risk to vendor as two header files.

[repo](https://github.com/mattreecebentley/plf_list) · [benchmark](http://www.plflib.org/benchmarks_haswell_gcc.htm)

#### serialization-json

##### cjson.cpp  `C++`  `MIT`  `active`  `Tier A`

Header-only SIMD index/tape JSON parser for C++26 on the micron runtime, ~9-31x faster than nlohmann::json.

**Beats:** nlohmann::json — On the author's own benches/corpus_vs.cpp (GCC 16.1.1, -O3 -march=native -flto -ffat-lto-objects, AMD Ryzen 7 3700U, taskset -c 0, medians of 7 runs), cjson-reuse parses 1MB JSON at 2.52 GB/s vs nlohmann::json 3.12.0's 0.08-0.09 GB/s on comparable documents (twitter.json parse/tree: 0.08 GB/s) and extracts fields from twitter.json (cjson-dom) at 2.02 GB/s vs nlohmann's 0.08 GB/s; against simdjson-dom(warm) cjson-reuse is close (1.18x on 64KB, 0.99x on twitter/5MB) and behind on 12 of 18 corpus documents.

**How:** Two-stage SIMD engine: stage 1 scans 64-byte blocks to build structural indexes, quote/escape masks, and validate UTF-8 in one sweep (SSSE3/AVX2+PCLMUL on amd64, NEON on aarch64/armv7, a SWAR fallback elsewhere); stage 2 is a scalar FSM building a contiguous 16-byte value arena, i.e. a flat tape rather than a DOM tree. Strings stay as {offset,length} spans with lazy unescape and linear-scan object lookup, avoiding per-node allocation entirely; the 'cjson-reuse' variant additionally amortizes allocation by reusing a warm scratch buffer across calls. This is the same index/tape design used by simdjson-dom and yyjson (which is why cjson tracks those two closely), and it is what produces the large margin over owning-tree parsers like nlohmann, RapidJSON, Boost.JSON and glz::generic.

**Use it when:**
- Hot-path parse/extract of JSON from 64KB to tens of MB where an index/tape handle (not an owning, freely-mutable tree) is acceptable
- Already targeting C++26 on GCC and willing to build against the micron core library instead of STL/libc
- Need SIMD parsing on amd64 (SSSE3/AVX2+PCLMUL), aarch64/armv7 NEON, or a portable SWAR fallback, and can fix the build to one target ISA
- Want compile-time (consteval) JSON parsing/validation baked into a binary, e.g. static config literals
- Serialize-heavy workloads where cjson-reuse is claimed 2-3x over yyjson on twitter/1MB/5MB documents

**Skip it when:**
- Need a drop-in nlohmann::json replacement with a fully owning, freely-mutable std::string/vector/map tree
- Cannot take on a second core library (micron) or cannot leave the C++ STL/libc; README states no traditional STL support
- Need a single binary that runs across AVX2 and non-AVX2 hosts -- no runtime CPU dispatch is provided
- Need proven maturity: repo is about 7 weeks old, 2 stars, 1 open issue, single author, no third-party reproduction of the benchmark numbers
- Object-heavy or numeric corpora where cjson-reuse still trails simdjson-dom(warm), e.g. canada.json 0.55 vs 0.73 GB/s and numbers.json 0.61 vs 0.82 GB/s -- pick simdjson there instead

**Integration:** header-only · micron core library (github.com/rfgplk/micron.cpp) only; no STL, no libc · C++26; README states 'GCC 16+', INSTALL states 'g++ >= 14 (cjson uses -std=c++26 and `if consteval`)' -- the two documents disagree on the minimum GCC version · x86-64 (SSSE3, AVX2+PCLMUL), aarch64 (NEON), armv7 (NEON), portable SWAR fallback; no runtime CPU dispatch, so a binary built with AVX2 requires AVX2 at runtime

**Vs siblings:** Pick cjson over json.cpp, DAW JSON Link, or Tachyon.JSON when you want simdjson-class index/tape throughput (it tracks simdjson-dom within about 1x on several sizes) plus a native consteval parse mode and a lazy functional pipeline; those siblings stay on an STL-based, nlohmann-like data model, while cjson requires leaving the STL for micron.

**Gotchas:**
- Adopting cjson means leaving the C++ STL/libc for the micron core library -- a whole-program dependency change, not just adding a header
- No runtime CPU dispatch: a binary built for AVX2 will not run correctly on non-AVX2 hardware
- Erasing an object member does not reclaim its pool bytes, and a warm scratch buffer holds memory proportional to the largest document it has seen until release()
- Glaze's own author opened issue #2 arguing the DOM benchmark rows compare cjson against glz::generic (Glaze's schema-less owning-tree fallback), not Glaze's reflection-based fast path; this dispute is about the Glaze rows specifically, not the nlohmann numbers

**Status:** Active (created 2026-08-08, last commit 2026-08-14) but very new: about 7 weeks old, 2 stars, 1 open issue, single author, MIT-licensed and header-only so it is cheap to vendor even if development stalls.

[repo](https://github.com/rfgplk/cjson.cpp) · [benchmark](https://github.com/rfgplk/cjson.cpp/blob/master/benches/results/corpus_vs.txt)

##### DAW JSON Link  `C++`  `BSL-1.0`  `active`  `Tier A`

Header-only C++ JSON library that parses straight into your typed structs, beating RapidJSON, simdjson DOM, Boost.JSON and nlohmann.

**Beats:** RapidJSON (same suite also includes simdjson, yyjson, Boost.JSON, Boost.PropertyTree, nlohmann::json) — kostya/benchmarks Json test (parse + sum values from a generated coordinates JSON file) run on gcc 16.1.0 / clang 22.1.8 (libc++), -O3 -march=native -flto=auto -std=c++23, Intel Xeon E-2324G: DAW JSON Link 0.089s (g++) / 0.085s (clang++) beats RapidJSON 0.154s/0.194s (1.73x/2.28x), simdjson DOM 0.107s (1.20x), Boost.JSON 0.374s (4.2x) and nlohmann 1.266s (14.2x); simdjson On-Demand (0.060s) is faster than DAW. Memory column shows +0.00 MiB over baseline for DAW versus +175 MiB (simdjson DOM) and +96 MiB (gason), evidencing the no-parser-allocation claim. Older author-run tables (2015-2017 CPUs, gcc 9.2.1) showed 0.19s vs RapidJSON's 0.53s and 0.11s vs 0.26s, both independently confirmed.

**How:** No allocation inside the parser itself (memory shown in kostya's table is +0.00 MiB over baseline, versus +175 MiB for simdjson DOM and +96 MiB for gason); allocation, if any, happens only in the resulting user types. It skips DOM/tree construction entirely, parsing directly to constructor args in declaration order, and backtracks only if struct member order doesn't match JSON key order. Numeric parsing uses the Eisel-Lemire fast path for doubles and the Dragonbox algorithm for float-to-string; optional SSE4.2/AVX2/NEON paths exist for member-skip scanning, though the README says the constexpr non-SIMD path is often faster.

**Use it when:**
- JSON schema is fixed and known at compile time, and you want to build typed C++ objects without an intermediate DOM
- You need to construct immutable or non-default-constructible types straight from JSON via their constructors
- You want strictly bounded/zero parser-side allocation (embedded, latency-sensitive, or `-fno-exceptions` builds via `DAW_JSON_DONT_USE_EXCEPTIONS`)
- You're streaming large arrays or NDJSON/JSON-Lines files and want a thread-partitioning iterator built in
- You also need SAX-style minification, JSON Path lookups, or JSON Schema generation from the same mapping

**Skip it when:**
- You want a drop-in mutable DOM you can edit and reserialize with zero setup (nlohmann::json-style) rather than declaring a mapping per type
- Compile-time budget is tight: heavy template metaprogramming for the mapping machinery adds to build times
- Raw parse throughput is the only goal and DOM/typed structure doesn't matter: simdjson On-Demand beats it in the same kostya table (0.060s vs 0.089s g++)
- You need certified-accurate float parsing on adversarial inputs: kostya's README flags DAW JSON Link (checked variant) among libraries with known number-parsing inaccuracies (issue #226, still open as a research note citing Clinger's accurate-parsing paper, not confirmed fixed)
- Your team wants minimal per-type boilerplate and doesn't already use C++26 reflection or Boost.PFR/Describe for automatic mapping

**Integration:** header-only · daw::header_libraries and daw::utf_range (both header-only, same author, pulled automatically via CMake FetchContent from extern/CMakeLists.txt) · C++17 minimum (tested GCC 9-12, Clang 8-14, MSVC 19.29); C++20 enables inline NTTP member names; C++26 static reflection (or Boost.PFR/Boost.Describe adapters) enables automatic mapping without a manual json_data_contract · any C++17 target; optional SIMD member-skip paths for x86 SSE4.2/AVX2 and arm NEON, but README says the default constexpr (non-SIMD) path is generally faster

**Vs siblings:** Pick this over cjson.cpp/json.cpp/Tachyon.JSON/utl::json when you want direct-to-typed-struct parsing (no DOM, constructor-arg based) plus SAX/lazy-pull/NDJSON modes from one mapping, not just a faster nlohmann-shaped DOM. If raw throughput against simdjson On-Demand is the only metric, that (or Tachyon.JSON, which also beats simdjson On-Demand in its own table) is faster than DAW JSON Link here.

**Gotchas:**
- Struct member order should match JSON key order; mismatches force backtracking and slow parsing
- Missing/optional members slow parsing more than explicit nulls do, per the README's performance notes
- Exceptions are on by default (throws daw::json::json_exception); disabling them (or building with -fno-exceptions) falls back to std::terminate unless a custom thread_local handler is installed
- Duplicate JSON member names resolve to an unspecified one unless you explicitly use json_key_value to preserve or order all of them

**Status:** Actively maintained: last commit on default branch 'release' is 2026-09-09, with pushes as recent as 2026-09-18 on another branch. BSL-1.0 licensed and header-only (two small header-only same-author dependencies), so it is easy to vendor despite the heavier template metaprogramming and per-type mapping cost.

[repo](https://github.com/beached/daw_json_link) · [benchmark](https://github.com/kostya/benchmarks/blob/master/README.md)

##### HPS (High Performance Serialization)  `C++`  `MIT`  `abandoned`  `Tier A`

Header-only C++11 serializer for STL/user types; faster and smaller than Boost.Serialization, no schema needed.

**Beats:** Boost.Serialization — On GCC 7.2 -O3 (CentOS 7.2, Intel Xeon E5-2620 v4), HPS's own first-party benchmark (src/benchmark, run via benchmark.mk/ci.sh) times full serialize+parse round-trips against Boost 1.66.0, Protobuf 3.5.1, and Cap'n Proto 0.6.1 on a double array, sparse matrix, and string-to-double hash map; the README charts show HPS beating Boost on all three (up to ~2.5x, i.e. '150% faster', and up to 40% smaller output on several cases), while Cap'n Proto is faster than HPS specifically on the sparse-matrix case.

**How:** Signed integers are zigzag-encoded and routed through a varint-style unsigned-integer serializer (confirmed in src/basic_type/int_serializer.h), the same base idea Protobuf uses. The key difference from Protobuf is that HPS emits no field numbers or wire-type tags at all -- layout comes entirely from the C++ type at compile time (per-README) -- which cuts both encoded size and per-field dispatch overhead. It also skips the reflection/schema layer and message-builder allocation model that Cap'n Proto and Boost.Serialization pay for.

**Use it when:**
- Serializing STL containers (vector, map, unordered_map, set, deque, list, pair, unique_ptr, string, array) or composed user types within one C++ codebase/toolchain
- Want a smaller, faster wire format than Boost.Serialization without adopting an IDL or build-time codegen step (Protobuf/Cap'n Proto)
- OK vendoring a small header-only C++11 library with no runtime shared-lib dependency
- Numeric-heavy workloads (large arrays of primitives) similar to the library's own stated use case (quantum-chemistry data checkpointing)
- Internal format where both reader and writer compile from the same C++ headers, so no cross-language schema is needed

**Skip it when:**
- Need cross-language interop or generated bindings (Python/Java/Go) -- there is no .proto/.capnp equivalent
- Need zero-copy / read-without-parsing access into the buffer -- HPS parses into an object like Boost does; Cap'n Proto's own README-cited benchmark beats HPS specifically on the sparse-matrix case
- Need forward/backward wire compatibility as fields are added or removed -- there are no field tags, so there is no story for schema evolution (unlike Protobuf's optional fields)
- Project has been unmaintained since last commit 2022-01-17 with no recent validation against current compilers/Boost/Protobuf/Cap'n Proto versions
- Care about stream-based reads specifically: an unresolved open issue (#49) reports an abort() in StreamInputBuffer::load on a size mismatch, with no maintainer response

**Integration:** header-only · none at runtime (STL only); googletest is a test-only submodule, not a runtime dependency · C++11 (CI matrix tested GCC 5/6/7 and Clang 4.0/5.0 on Ubuntu Trusty via .travis.yml) · not documented beyond Linux CI; no architecture-specific code observed in the serializers read (no SIMD/intrinsics)

**Vs siblings:** Among the catalogued siblings, Cap'n Proto and zpp::bits are the closest (also binary serialization, not JSON-text parsers like the rest). Pick HPS over them when you're already on Boost.Serialization and want a smaller/faster same-shape replacement without adopting an IDL, schema compiler, or zero-copy buffer model -- but Cap'n Proto's own benchmark beats HPS on nested/sparse-matrix data and gives you cross-language schemas plus zero-copy reads that HPS doesn't offer.

**Gotchas:**
- Open, unresolved issue #49: a third-party project hit abort() in StreamInputBuffer::load on a read-position/file-size mismatch (oldpos 524288 vs size 589548); no fix visible in the thread
- No field numbers or wire types in the encoding -- reading with a mismatched type layout is undefined, unlike Protobuf's tag-based tolerance
- unordered_map/unordered_set serialize in iteration order, which is not guaranteed stable across runs or STL implementations
- Repo dormant since Jan 2022; last verified against 2017-era GCC 5-7 / Clang 4-5, so building with a modern compiler is unverified

**Status:** Abandoned: last commit 2022-01-17 and CI last green against 2017-era GCC 5-7/Clang 4-5 on Travis; MIT-licensed, header-only, and small enough to vendor and re-verify against a current compiler yourself.

[repo](https://github.com/jl2922/hps) · [benchmark](https://github.com/jl2922/hps)

##### json.cpp  `C++`  `Apache-2.0`  `active`  `Tier A`

Lean C++11 JSON parser/serializer beating nlohmann::json 2-3x on parse/round-trip latency and compile time.

**Beats:** nlohmann::json (nlohmann::ordered_json) — On gcc 13.2 -O3 (Ubuntu 24.04, AMD Ryzen Threadripper PRO 7995WX), json.cpp's own benchmark (2000 runs per fixture) reports roughly 2.8x-3.25x lower latency than nlohmann::ordered_json on object/deep/parse/round-trip micro-tests and about 1.6x on a locally modified json_test_suite run; this is a first-party, single-machine result with no independent reproduction found.

**How:** Speed comes from a small, allocation-conscious value type (a union of primitive/std::string/vector/map with no std::variant or type-erasure layer) and a direct byte-level recursive-descent parser that walks raw char pointers guided by a precomputed 256-entry classification table (kJsonStr) instead of stream or iterator abstractions. Float/double-to-string conversion is offloaded to Google's double-conversion library rather than the locale-aware sstream/strtod paths nlohmann and the STL use. The small overall code size (233 + 1,303 lines) also keeps compile times and instruction-cache pressure down versus nlohmann's single ~24,766-line header.

**Use it when:**
- Hot-path JSON parse/serialize where nlohmann::json's per-value overhead or header compile cost is the bottleneck
- Projects that can tolerate std::map key-ordered (not insertion-ordered) JSON objects
- Contexts where vendoring a small source-drop (json.h/json.cpp + double-conversion) beats pulling in a large header-only library
- Need accurate float32 round-tripping (e.g. embeddings served over HTTP) without upcasting to double
- C++11-only or less common toolchains/architectures: CI covers gcc/Ubuntu, ppc64le, s390x (via QEMU), macOS, and MSVC 2022

**Skip it when:**
- Need nlohmann::json's feature surface: JSON Pointer, SAX interface, custom (de)serializers, CBOR/MessagePack/BSON, or ordered_json's true insertion-order objects
- Need a widely audited, battle-tested parser; json.cpp has 796 stars and has been public only since late 2024, versus nlohmann's much longer track record
- Can't accept abort() as a possible outcome of a type-mismatch getter call in exception-disabled builds
- Can't take on Google double-conversion as a build dependency (vendored, but still required)
- Need independently reproduced numbers: the benchmark is first-party, single-machine, and the README itself flags an unexplained 39x result on the unmodified json_test_suite case

**Integration:** source-drop · Google double-conversion (vendored in-repo under double-conversion/) · C++11 (CMAKE_CXX_STANDARD 11 in CMakeLists.txt); builds with GCC, Clang/AppleClang, and MSVC 2022 per CI · x86-64, ppc64le, s390x (CI via QEMU), macOS, Windows (MSVC) — no SIMD requirement

**Vs siblings:** Among the nlohmann-beating siblings, pick json.cpp over utl::json when you want a much smaller (233+1,303-line) source drop instead of a header-only library and don't need utl::json's wider UTL ecosystem. If the workload needs SIMD-scale throughput on large documents rather than a 2-3x win over nlohmann on small/medium fixtures, look at a simdjson/yyjson-class parser instead (see DAW JSON Link's or Tachyon.JSON's comparisons).

**Gotchas:**
- Object keys are stored in std::map, so iteration/serialization order is alphabetical, not insertion order — a real behavioral difference from the ordered_json baseline used in its own benchmark
- Getter type mismatches call abort() by default, or throw std::logic_error instead if __cpp_exceptions/__EXCEPTIONS/_CPPUNWIND is defined at compile time (json.cpp, ON_LOGIC_ERROR macro)
- The headline json_test_suite benchmark number (~1.6x/3x) comes from a locally modified version of that test that keeps only the passing cases; the README states the unmodified test shows a 39x gap the authors 'haven't figured out how to explain yet'
- Requires Google double-conversion at build time; it's vendored in the repo (not a git submodule) so no separate fetch is needed, but it is a hard link dependency

**Status:** Actively maintained (last commit 2026-04-08, 796 stars, 3 open issues), Apache-2.0 licensed and small enough to vendor, but young (public since late 2024) and far less battle-tested than nlohmann::json.

[repo](https://github.com/jart/json.cpp) · [benchmark](https://github.com/jart/json.cpp/blob/main/README.md)

##### scnlib  `C++`  `Apache-2.0`  `active`  `Tier A`

Type-safe scanf/istream replacement; ~3-5x faster than std::stringstream and sscanf at parsing ints, floats, and words.

**Beats:** std::stringstream / sscanf — On an AMD Ryzen 7 5700X (Fedora 40, kernel 6.8.9), compiled with clang 18.1.1 at -O3 -DNDEBUG -march=haswell with LTO, scnlib's own in-repo benchmark suite (commit 3fd830de, run 2024-05-23) measured scn::scan averaging 27.1ns for int, 59.7ns for double, and 24.5ns for a whitespace-delimited string word, versus std::stringstream at 85.5ns/283ns/134ns and sscanf at 272.7ns/432ns/58.4ns — roughly 3.2x, 4.7x, and 5.5x faster than stringstream respectively. The same tables show std::from_chars (10.9ns int, 23.0ns double) and fast_float::from_chars beating scn::scan outright.

**How:** It parses the format string once and dispatches straight to type-specialized scanning routines, avoiding stringstream's locale-aware state construction and sscanf's repeated format-string reparsing and whitespace-skipping (the README attributes ~400ns of sscanf's overhead to %n handling and whitespace skipping). Integer scanning has a stripped-down fast path (scn::scan_int, scn::scan_int_exhaustive_valid) and float scanning is built on the fast_float library (or std::from_chars) rather than a locale-aware strtod-style conversion. It also avoids RTTI and, in its core scanning path, exceptions (built with -fno-exceptions -fno-rtti in CI).

**Use it when:**
- Hot loops parsing many ints/doubles/whitespace-delimited words out of in-memory text (logs, config, simple text protocols) where stringstream or sscanf overhead shows up in profiles
- C++17+ codebases on GCC 7+/Clang 8+/MSVC 2019+ that can add a CMake dependency and rewrite the affected parsing call sites
- Code that wants compile-time-checked format strings instead of scanf's unchecked '%' format bugs
- Environments that disable exceptions/RTTI, since scnlib's core scanning path is usable without either
- Cross-platform targets beyond x86: ARM/AArch64, RISC-V, ppc64le, s390x are all CI-tested

**Skip it when:**
- Pure numeric conversion only (string->int/double, no whitespace/word handling) — std::from_chars and fast_float::from_chars both beat scn::scan outright (10.9ns/23.0ns vs 27.1ns/59.7ns for int/double in the README's own table)
- Projects that need a header-only drop-in — scnlib builds a library (source-drop with a src/scn/impl.cpp) and pulls in fast_float via CMake FetchContent by default
- Teams unwilling to learn scn's format-string semantics, which are evaluated left-to-right per-type and are explicitly not a regex/pattern language (documented FAQ gotcha)
- Code paths hit by open correctness issues: wrong result scanning from a std::deque-backed range (#144), a multi-value scan failing after a string value (#134), and floats with very large/small magnitude (#126) — check these against the version you'd pin before relying on them
- I/O-bound parsing (reading from disk/socket dominates), since the measured gains are for in-memory string parsing only, not end-to-end I/O latency

**Integration:** static lib (default; shared lib via BUILD_SHARED_LIBS=ON; a C++20 module target scn::module is also available via SCN_MODULES) · fast_float (fetched via CMake FetchContent by default; can be pointed at an external/vendored copy, or disabled with SCN_DISABLE_FAST_FLOAT to fall back to std::from_chars). GTest and Google Benchmark are pulled in only when building scnlib's own tests/benchmarks, not for library consumers. · C++17; GCC 7+, Clang 8+, or Visual Studio 2019/2022 (CI-tested) · Windows, Linux, macOS (14/15); x86, x86-64, arm, aarch64, riscv64, ppc64le, s390x, mips64le all CI-tested; 32- and 64-bit Windows, MinGW/MSYS2 also covered. One open issue reports test failures on OpenBSD (#155) and another a build failure against libc++ 23 (#159)

**Vs siblings:** All the catalogued siblings (cjson.cpp, json.cpp, Cap'n Proto, DAW JSON Link, zpp::bits, Tachyon.JSON, utl::json, HPS) target structured JSON or binary (de)serialization; scnlib solves a different problem — unformatted, scanf/istream-style extraction of ints/floats/words from free text. Pick scnlib when the baseline you're replacing is std::stringstream/sscanf/operator>>, not when you're parsing or emitting JSON or a binary wire format.

**Gotchas:**
- Format strings are not regexes or patterns: scn::scan<std::string,std::string>(input, "{},{}") does NOT stop the first field at the comma — each {} scans per its type's default rule (a string reads until whitespace), and the literal text between fields is matched and discarded separately; use "{:[^,]},{}" to stop at a comma (documented in the FAQ)
- Requires and assumes Unicode input (UTF-8, UTF-16, or UTF-32); behavior on non-Unicode/binary input is not something this session verified
- Not exception-free end-to-end: a custom Scanner's parse() can still throw scn::scan_format_string_error even though the core value-scanning path avoids exceptions/RTTI
- This is the reference implementation of an in-progress ISO C++ proposal (P1729 'Text Parsing'), so API surface may still shift across major versions

**Status:** Actively maintained (latest master commit 2025-10-29, v4.0 docs current, ongoing releases and CI); Apache-2.0 and technically copyable, but it's a compiled library with a build step and a fast_float dependency, not a header you can just drop into a source tree.

[repo](https://github.com/eliaskosunen/scnlib) · [benchmark](https://github.com/eliaskosunen/scnlib)

#### small-buffer-and-strings

##### to_static_string  `C++`  `BSL-1.0`  `stale`  `Tier A`

Header-only C++17 wrapper over std::to_chars that returns a stack-based string, replacing allocating, locale-dependent std::to_string.

**Beats:** std::to_string — On an i7-10510U @ 1.80GHz with clang-18, CMake Release, C++20, libstdc++ (Ubuntu 22.04), via Google Benchmark: std::to_string(long) 45.3ns vs to_static_string(long) 27.7ns (~1.6x), and std::to_string(double) 1245ns vs to_static_string(double) 95.6ns (~13x). In both cases to_static_string tracks raw std::to_chars almost exactly (27.7 vs 27.4ns; 95.6 vs 98.4ns), so the measured win is really std::to_chars' win over std::to_string, delivered through a safer wrapper.

**How:** It is a thin, noexcept wrapper around std::to_chars: no heap allocation, no locale lookups, no exceptions. All work happens in a fixed-size stack buffer sized per type at compile time. The large win over std::to_string(double) comes from libstdc++'s locale-aware, snprintf-based double formatting being far slower than to_chars' direct digit-generation algorithm; the integer case gains less because libstdc++'s std::to_string(long) is already close to to_chars speed.

**Use it when:**
- Hot-path numeric-to-string conversion (logging, serialization, protocol encoding) where allocation matters
- Formatting doubles specifically, where the gap over std::to_string is largest (~13x in this benchmark)
- Code that wants a safe wrapper over std::to_chars without manually sizing and managing the output buffer
- C++17 codebases that want to_chars-level speed without hand-rolling buffer math
- Cases that need locale-independent, non-throwing numeric formatting

**Skip it when:**
- You need an owning std::string (e.g. stored beyond the current stack frame or in a container) — get() returns a string_view into a local buffer, so you must copy it into a std::string yourself
- You need custom formatting like thousands separators or printf-style width/padding — this only exposes what std::to_chars supports
- char8_t or other 'extension' integer types — README/tests mark these as untested TODOs
- You need release-build safety against conversion failure: errors from std::to_chars are only caught via assert(), which is compiled out under NDEBUG
- You need active maintenance or a track record — single author, 1 star, 0 forks, no commits since 2024-01-13

**Integration:** header-only · none for the library itself; Catch2 and Google Benchmark are only needed to build the tests/benchmarks · C++17 (CMakeLists.txt sets target_compile_features(... cxx_std_17)); a TO_STATIC_STRING_CXX23_CONSTEXPR macro hints at future full-constexpr support once __cpp_lib_constexpr_charconv is available · any platform with a std::to_chars implementation for the types used; only actually benchmarked on x86-64 Ubuntu 22.04 with clang-18/libstdc++

**Vs siblings:** Pick this over Str (MengRao/str) — the only sibling that also targets std::to_string/stoi — when you want a minimal, single-purpose std::to_chars wrapper rather than a broader string/parsing utility library; Str claims larger speedups but bundles more surface area than just numeric formatting.

**Gotchas:**
- Buffer size N is fixed per type at compile time (rounded to 8/16/32 bytes for integers, or computed from max_digits10 for floats) — it is not user-configurable
- std::to_chars errors are only checked via assert(result.ec == std::errc()); in a release (NDEBUG) build a conversion failure is silently ignored rather than surfaced
- get() returns a std::string_view referencing the returned object's internal buffer — do not outlive the cstatic_string instance
- char8_t and other extension integer types are explicitly untested (marked '// TODO' in test/test.cpp)

**Status:** Stale: single-author project, last commit 2024-01-13, 1 star, 0 forks, 0 open issues/PRs (low-traffic rather than actively triaged). BSL-1.0 licensed, header-only, and small enough (~150 lines) to read in full and vendor despite the inactivity; note vcpkg.json's manifest license field says 'MIT', which conflicts with the repository's actual BSL-1.0 license (LICENSE_1_0.txt and file headers) — treat BSL-1.0 as authoritative.

[repo](https://github.com/anarthal/to-static-string) · [benchmark](https://github.com/anarthal/to-static-string)

#### smart-pointers-and-refcount

##### CDRC atomic_weak_ptr (concurrent_deferred_rc)  `C++`  `MIT`  `abandoned`  `Tier A`

Header-only C++20 lock-free atomic weak/shared pointers, beating a commercial atomic<weak_ptr> implementation under contention.

**Beats:** just::thread's atomic<weak_ptr> (commercial third-party implementation of the C++20 std::atomic<std::weak_ptr> interface) — PLDI '22 paper Sec. 5.2/Fig. 12: on a 4-socket 72-core machine (4x Xeon E7-8867 v4, GCC 9.2.1 -O3), in a lock-free doubly-linked queue benchmark using atomic weak back-pointers (pop-then-reinsert, P=1-192 threads), CDRC's atomic_weak_ptr beat just::thread's atomic<weak_ptr> by 4.2x at P=8 and 10x at P=192, with CDRC's margin over just::thread at P=1 around 15x (derived, not the paper's often-cited 67x figure, which is the hand-tuned manual-reclamation baseline vs just::thread). CDRC itself trails that manual-reclamation queue by 4.5x at P=1, 19% at P=8, and 33% at P=192.

**How:** Uses 'concurrent deferred reference counting': reference-count updates are decoupled from object reclamation, which is handed to a pluggable safe-memory-reclamation backend (hazard pointers by default, or epoch-based/interval-based/Hyaline reclamation) bounding per-operation reclamation overhead. The snapshot_ptr/weak_snapshot_ptr types read the current object without incrementing the shared reference count, cutting atomic RMW traffic on hot traversal paths versus always producing a fully counted handle.

**Use it when:**
- Lock-free concurrent data structures (queues, stacks, structures with back-pointers) that need atomic weak pointers, at medium-to-high thread counts where the paper shows the advantage growing (4.2x at P=8, 10x at P=192 on a 72-core/4-socket box)
- You are currently bottlenecked on a commercial or hand-rolled atomic<weak_ptr>-style implementation (e.g. just::thread) under contention
- You can target a C++20-concepts-capable compiler (GCC 9+, Clang 13+, AppleClang, or MSVC 19, all green in CI) and restructure pointer usage around cdrc's own types
- You want to tune the throughput/memory tradeoff by swapping reclamation backends (hazard pointers vs EBR vs IBR vs Hyaline) for the same pointer API
- A research or experimental system where vendoring a small, unmaintained, MIT header-only library is acceptable

**Skip it when:**
- You need a true drop-in replacement for std::shared_ptr/std::weak_ptr/std::atomic<weak_ptr> with no code changes — cdrc's types are similarly shaped but distinct and require rewriting the pointer hierarchy
- Single-threaded or low-contention (P=1) hot paths: the paper's own data has CDRC 4.5x slower than a hand-tuned manual-reclamation queue at P=1, and non-default backends add explicit per-scope guard overhead
- Memory-constrained environments — EBR and Hyaline backends trade higher memory for throughput, and the library documents higher memory use than manual reclamation when oversubscribed
- You need dynamic_cast on managed pointers or easy debuggability of the managed object's storage — issue #6 (dynamic cast) is open, and issues #3/#4 flag the type-erased char-array storage as hard to inspect
- You need active upstream support — no commits since 2022-07-03, 5 open issues, 2 open unmerged PRs

**Integration:** header-only · none for the library itself; benchmarks additionally need CMake 3.5+, Boost (program_options), hwloc, jemalloc, Python3+Matplotlib, and optionally Folly or just::thread · C++20 (uses concepts); CI builds and tests pass on GCC 9, GCC 11, Clang 13, AppleClang, and MSVC 19 · Linux, macOS, Windows for the library (all three run in CI); benchmarks are Linux-only (require NUMA policy support)

**Vs siblings:** The only same-category sibling that is actually concurrency-focused is observable_unique_ptr/observer_ptr (oup), which targets single-threaded non-owning observers, not atomic weak pointers. Pick CDRC over oup when you need thread-safe, lock-free atomic<weak_ptr>-style pointers for lock-free concurrent data structures; pick oup instead for single-threaded ownership/observer tracking where a full shared_ptr/weak_ptr pair is overkill.

**Gotchas:**
- Default backend is hazard pointers (moderate throughput, low memory); switching to EBR or Hyaline for higher throughput requires wrapping every potentially concurrent access in an epoch_guard/hyaline_guard, and holding a guard too long delays reclamation
- atomic_rc_ptr and atomic_weak_ptr have deleted copy and move constructors/assignment — they must be used in place (e.g. as class members), not stored by value in containers
- Internal counted-object storage is a raw char array (type-erased); two long-open issues (#3 'getValue' typo, #4 debuggability) flag this as awkward to inspect in a debugger
- dynamic_cast on managed pointers is not supported and is an open, unresolved request (issue #6) as of the last commit

**Status:** Abandoned: no commits since 2022-07-03 despite a later recorded repo push (no new commits found); MIT-licensed, small and header-only enough to vendor, and CI still builds/tests green on GCC 9/11, Clang 13, AppleClang, and MSVC 19, but 5 issues and 2 PRs have sat open since 2022.

[repo](https://github.com/cmuparlay/concurrent_deferred_rc) · [benchmark](https://arxiv.org/pdf/2204.05985)

##### observable_unique_ptr / observer_ptr (oup)  `C++`  `MIT`  `active`  `Tier A`

Header-only unique-ownership smart pointer with observer_ptr; dereference is 3.5x-38.7x faster than std::weak_ptr::lock().

**Beats:** std::weak_ptr — README's own speed_benchmark.cpp results (median across int/float/std::string/std::array<int,65536> objects, relative to raw T*=1) show observer_ptr dereference beating std::weak_ptr::lock()-based dereference by ~3.5x on gcc 9.4.0/libstdc++-9/Ryzen 5 2600, ~9.4x-11.8x on MSVC 16.11.3/MS-STL/i7-7800X, and ~38.7x on Emscripten 2.0.34/libc++ under Node.js 14.15.5/Ryzen 5 2600. The same tables show creating the owner pointer itself is 1.1x-2.9x slower than std::unique_ptr/std::shared_ptr, so the win is specific to the observer/dereference path, not owner construction.

**How:** The reference/expiry counter is a plain (non-atomic) integer in a small heap control block, so dereferencing an observer_ptr is just a flag check plus pointer read, versus std::weak_ptr::lock() which does an atomic increment, constructs a temporary shared_ptr, then an atomic decrement. Dropping shared ownership also shrinks the control block to 4 bytes (vs shared_ptr's ~24-byte block), cutting a heap allocation's worth of bookkeeping touched per access.

**Use it when:**
- Object has one clear owner and you only need to detect "has this been destroyed yet", not extend its lifetime
- Observer dereference/expiry-check happens in a hot loop and the object and its observers stay on a single thread
- You want observer-pointer semantics without std::shared_ptr's control-block allocation and atomic refcount overhead
- Header-only C++17 codebase where adding a single header is acceptable (no build system integration required)
- Multiple inheritance with observer_from_this()-style self-observation (std::enable_shared_from_this doesn't support this)

**Skip it when:**
- Observer pointers or the owner must be touched from more than one thread — no synchronization on the refcount, unlike std::shared_ptr/weak_ptr
- You need shared ownership (multiple owners) rather than unique ownership with observers
- You need arrays (T[]) or custom allocator support — both unimplemented
- Owner-pointer construction/creation is on the hot path — creating an oup owner is 1.1x-2.9x slower than std::unique_ptr/std::shared_ptr in the project's own benchmark table
- You need observable_sealed_ptr with a custom deleter, or a default-constructible/copyable/movable T combined with enable_observer_from_this_sealed (that path requires T's constructor to accept a control block)

**Integration:** header-only · none · C++17 (CMakeLists.txt sets cxx_std_17; cmake_minimum_required 3.8+ if using the provided CMake target) · any; CI builds Linux (GCC/clang), Windows (MSVC 32/64), macOS (clang), WebAssembly (Emscripten)

**Vs siblings:** Pick oup over CDRC atomic_weak_ptr (concurrent_deferred_rc) when you have single-threaded or thread-confined ownership and want the smallest, simplest observer pointer; pick CDRC instead when observers must be read/written concurrently across threads, since oup has no synchronization at all. The std::function alternatives in this category (woid, Delegate, stdext::inplace_function, SmallFunction, sy_callback) solve a different problem (callable storage) and aren't a substitute for either.

**Gotchas:**
- enable_observer_from_this_sealed requires T's constructor to accept a control block argument, which makes T non-default-constructible, non-copyable, and non-movable
- enable_observer_from_this_unique uses virtual inheritance to support multiple inheritance, which has its own ABI/layout cost
- observable_sealed_ptr does not support a custom deleter (observable_unique_ptr does)
- observer_from_this() throws a documented exception type when called in situations where no valid control block exists yet (e.g., certain construction states)

**Status:** Actively maintained (last commit 2026-09-05, project at v0.7.3 per CMakeLists.txt, MIT licensed), but the README states the speed benchmarks were last run for v0.7.1, so current numbers are unverified against the latest code. Small single-header library with no open issues; safe to vendor given the license and size.

[repo](https://github.com/cschreib/observable_unique_ptr) · [benchmark](https://github.com/cschreib/observable_unique_ptr#speed-benchmarks)

##### woid  `C++`  `MIT`  `active`  `Tier A`

Header-only C++23 type-erasure toolkit; woid::Fun beats std::function via configurable SBO storage and const/noexcept-correct signatures.

**Beats:** std::function — Benchmark (bench/fun_bench.cpp, run via bench/plot.py) sorts vectors of ints (sizes 2^0-2^18) with a comparator wrapped in woid::Fun vs std::function<bool(int,int)> vs function2 vs a plain lambda, built Release (-O3 -DNDEBUG -fno-rtti -fno-exceptions) with Clang 21.1.6 on an Intel i9-10850K. Per the verifier's reading of the SVG plot geometry, woid::Fun is ~1.0x at the smallest sizes and roughly 1.2x-1.6x vs std::function on the std::less<int> comparator (up to ~2.55x on the 32-byte BigLess comparator around size 2^8); the README itself only claims woid 'ranks first in most cases' without giving exact multipliers.

**How:** Speed comes from configurable small-buffer optimization: callers size the inline buffer (Any<N>) to the actual capture, avoiding the heap allocation std::function often falls back to for anything beyond a word-sized capture. TrivialAny skips the stored copy/move/destroy function-pointer indirection entirely for trivially-movable/copyable callables, treating the buffer as raw bytes instead; ExceptionGuarantee::NONE (usable as a Storage policy) further removes strong-guarantee bookkeeping that std::function-like wrappers pay for. InterfaceBuilder avoids vtable indirection by storing function pointers directly in (or referenced from) the wrapper, and SealedInterfaceBuilder replaces indirection with std::variant + visitation when the polymorphic type set is known at compile time.

**Use it when:**
- Hot loops that repeatedly construct/invoke small comparator or callback closures (e.g. sort comparators), where std::function's heap fallback and call overhead show up in profiles
- Callables whose captures fit a known small size — size Any<N>/TrivialAny<N> to match the capture so SBO always applies and heap allocation is designed out
- You need call-signature const/noexcept correctness that std::function does not enforce
- You also want a non-intrusive virtual-function alternative (InterfaceBuilder) so unrelated types can share an interface without a base class, especially when the concrete type set is closed (SealedInterfaceBuilder + std::variant)
- C++23-only toolchains (tested with Clang 21 / GCC 15) where you're willing to vendor a single young header and re-verify before relying on it in production

**Skip it when:**
- Project is stuck on C++20 or earlier — woid requires C++23
- Need a battle-tested, widely-deployed std::function replacement; woid has 7 GitHub stars, 0 filed issues, and a first commit from 2025-10-23, so edge cases are largely unexercised outside the author's own tests
- Need documented thread-safety guarantees — none are stated for any woid type, so a shared Fun/Any used across threads needs synchronization you verify yourself
- Move-only captures needed alongside copyable ones elsewhere — you must pick a Copy::DISABLED storage up front; there's no separate move_only_function-style type or runtime toggle
- At the smallest input sizes (vector length 1-2 in the sort benchmark) woid::Fun is only ~1.0x vs std::function, so the win is workload-size-dependent, not universal

**Integration:** header-only · none for the library itself (single header include/woid.hpp); building the tests/benchmarks pulls in GTest, google/benchmark, Boost 1.76+, and the third_party submodules function2/boost::te/microsoft::proxy · C++23 (CMakeLists requires CMake 3.21+); tested with Clang 21.1.6 and GCC 15 · not documented — no architecture/OS restriction stated in README; author's benchmarks ran on x86-64 (Intel i9-10850K)

**Vs siblings:** Pick woid over Delegate/inplace_function/SmallFunction/sy_callback.hpp when you need const/noexcept-correct call signatures and configurable SBO storage shared with a broader type-erasure toolkit (Any + a virtual-function replacement) in one header; those siblings are narrower, longer-established std::function replacements with more real-world usage and no C++23 requirement.

**Gotchas:**
- TrivialAny silently falls back to heap allocation for non-trivial or non-trivially-movable/copyable objects unless kCanAllocate is disabled, in which case it becomes a compile error instead
- ExceptionGuarantee::NONE (a configurable, non-strict default) is UB if the stored callable's copy/move constructor throws; opting into STRONG costs performance and also disables SBO for non-nothrow-movable types
- No separate move-only Fun type: copyability of Fun/Any is inherited from the chosen Storage's Copy policy, so move-only captures require picking Copy::DISABLED explicitly
- 0 issues have ever been filed on the repo (young project), so failure modes beyond the author's own GTest suite are unverified

**Status:** Active (pushed 2026-02-09) but very young — first commit 2025-10-23, 7 GitHub stars, 0 issues filed; MIT-licensed and a single header, so it's cheap to vendor and drop if it stalls.

[repo](https://github.com/akopich/woid) · [benchmark](https://github.com/akopich/woid/blob/main/bench/plots/FunBench_benchVectorStdLess_speedup.svg)

##### stdext::inplace_function (WG21-SG14/SG14)  `C++`  `BSL-1.0`  `abandoned`  `Tier B`

Header-only, fixed-capacity callable wrapper beating std::function's invocation speed in 5 of 7 shootout categories.

**Beats:** std::function — Third-party CxxFunctionBenchmark (jamboree/CxxFunctionBenchmark, various.cpp) times stdext::inplace_function<int(int),40> against std::function<int(int)> on MSVC 64-bit/Visual Studio 15.9.4, Release build: inplace_function is faster in 5 of 7 invocation categories (e.g. 0.2365s vs 0.2640s for function_pointer, 0.1593s vs 0.1906s for compile_time_delegate) but slower for lambda_capture (0.1851s vs 0.1757s) and stateless_lambda (0.1845s vs 0.1799s); no CPU model or exact compiler flags are given beyond 'Release Build'.

**How:** It avoids the heap allocation std::function performs for non-trivial or captured callables: the object is placement-new'd into an inline aligned_storage buffer sized at compile time, and a small per-type vtable (invoke/copy/relocate/destroy function pointers) replaces the allocator plus type-erasure machinery libstdc++/MSVC use. This removes the allocate/deallocate pair on construction/destruction and an extra pointer indirection to heap-owned state, which is what the CxxFunctionBenchmark invocation timings pick up for stateful callables.

**Use it when:**
- The callable's captured/bound state fits a known small size (tested here at 40 bytes) and that bound can be enforced at compile time.
- Hot path repeatedly invokes an already-assigned callable (function pointers, member-fn delegates, small functors) and heap traffic is the std::function cost you're trying to remove.
- Embedded, low-latency, or game code where dynamic allocation is undesirable or banned.
- You're willing to hand-tune per-callsite capacity/alignment template arguments instead of using one universal type.
- MSVC or GCC/Clang toolchain with plain standard C++ (no platform-specific requirements).

**Skip it when:**
- Callable sizes are unknown or unbounded at the call site: std::function's heap fallback always compiles, inplace_function doesn't.
- Capturing/stateless lambdas dominate the workload: in this benchmark inplace_function was slower than std::function for lambda_capture (0.1851s vs 0.1757s) and stateless_lambda (0.1845s vs 0.1799s).
- Code crosses shared-library/DLL boundaries: open issue #170 flags ABI concerns for inplace_function used at library edges.
- You need an actively maintained dependency: last commit 2022-04-19, repo is abandoned, and 19 issues are open, several unresolved design questions.
- You need real concurrency guarantees: open issue #158 notes operator() is const but backed by a mutable, non-atomic buffer, so 'const-callable' isn't a thread-safety guarantee.

**Integration:** header-only · none (single header; uses <type_traits>, <utility>, <functional> from the standard library) · C++14 (repo's own alternate build command compiles with -std=c++14; header uses std::exchange and documents an aligned_storage workaround for older GCC/MSVC 32-bit) · any (portable standard C++, no SIMD/OS-specific code); the benchmark numbers here are MSVC 64-bit only

**Vs siblings:** Pick inplace_function over Delegate (bdiamand/Delegate) when compile-time capacity enforcement and WG21 pedigree (a standards proposal exists to make this std::inplace_function) matter more than raw speed — Delegate wins all 7 categories of the same CxxFunctionBenchmark shootout, where inplace_function only wins 5 of 7. Pick SmallFunction or woid instead for a smaller, single-purpose library without SG14's monorepo and open design questions.

**Gotchas:**
- Assigning a callable larger than Capacity or overaligned relative to Alignment is a hard compile error, not a runtime allocation; issue #160 'Giant Sized Buffers Required for Compilation' documents this surfacing in practice.
- Calling an empty (default-constructed or moved-from) inplace_function throws std::bad_function_call by default via the SG14_INPLACE_FUNCTION_THROW macro, which can be redefined before including the header to opt out of exceptions.
- operator() is declared const, but the underlying storage_ member is mutable, so a const inplace_function can still run a mutating call operator (see issue #158).
- License lives only in the header's comment block (Boost Software License 1.0); the SG14 repository itself has no license field set on GitHub.

**Status:** Abandoned since the last commit on 2022-04-19 (a repo-wide date covering all SG14 proposals, not just this header); BSL-1.0 licensed and small enough (one ~200-line header) to vendor regardless, but carries 19 open issues including unresolved questions about exception-free use and shared-library ABI.

[repo](https://github.com/WG21-SG14/SG14) · [benchmark](https://github.com/jamboree/CxxFunctionBenchmark#sample-result)

#### sorting

##### Boost.Sort — spreadsort  `C++`  `BSL-1.0`  `active`  `Tier A`

Hybrid radix/comparison sort in Boost; beats std::sort on large random integers, strings, and objects.

**Beats:** std::sort — In the library's own linux_single.qbk benchmark (GCC 6.3, -std=c++11 -march=native -O3, Intel i7-5820K, libstdc++), spreadsort sorted 100M random 64-bit ints in 4.2248s vs std::sort's 8.2154s (~1.94x), 10M random strings in 2.4323s vs 6.2442s (~2.57x), and 100M 8-byte objects with a heavy comparator in 5.10s vs 8.25s (~1.62x); spreadsort was slower than std::sort on reverse-sorted ints (1.87s vs 1.36s).

**How:** It is a hybrid radix/comparison sort: it recursively buckets elements by their most-significant bits (read via a right-shift functor) and dynamically chooses radix or comparison-based sorting per bucket, whichever has better worst-case cost. Worst case is the lesser of O(N log N) comparisons and O(N log(K/S + S)) operations, where K is key bit-width and S (max_splits, default 11) is a tunable constant. This gives near-linear behavior on wide or clustered integer/float/string keys where std::sort spends more time on comparisons.

**Use it when:**
- Sorting 100K-100M+ 64-bit integers, floats, or std::strings single-threaded, where the ~2x win on random data matters.
- Large or expensive-to-compare elements (long keys, heavy comparators, key+payload records) — the object benchmark shows bigger wins as element size grows.
- Data that is already sorted or nearly sorted forward — spreadsort has an early-exit fast path competitive with pdqsort.
- Custom numeric-like keys where you can write a correct right-shift functor (fixed-point types, custom integer wrappers).
- You are fine with an unstable sort, same as std::sort.

**Skip it when:**
- Reverse-sorted or adversarial input — the repo's own benchmark shows spreadsort slower than std::sort here (1.87s vs 1.36s on 100M ints).
- Inputs under ~1000 elements — falls back to pdqsort internally, so there is no spreadsort-specific benefit.
- Need a stable sort — use Boost's spinsort/flat_stable_sort instead, though neither beat std::stable_sort on random data in this same benchmark, only on near-sorted input.
- Indirect/argsort-style sorting through an index lookup — GitHub issue #85 shows overriding only the right-shift functor without also overriding the comparator silently falls back to plain (wrong-looking) comparison behavior for small inputs.
- Need the benchmarked ~2x margins reproduced on current hardware/toolchains — the doc's numbers are from GCC 6.3 on a 2017-era CPU and have not been re-run since.

**Integration:** header-only · Boost.Range, Boost.TypeTraits, Boost.Core (static_assert) — ships as part of Boost, not a standalone zero-dependency library · C++11 (README states a C++11 compiler is required; parallel algorithms in the same repo also need C++11) · any — portable C++ template code, no SIMD/intrinsics or arch-specific code observed in the spreadsort headers

**Vs siblings:** Pick spreadsort over comparison-based siblings (BlockQuicksort, pdqsort-class sorts) when data is plain integers/floats/strings with wide or clustered key bits and you don't need stability or multithreading; pick IPS4o or x86-simd-sort instead when you can parallelize or vectorize, and pick fluxsort/quadsort instead when stability matters more than raw unstable-sort throughput.

**Gotchas:**
- Right-shift functor must fully discriminate between elements consistent with operator< (documented requirement, GitHub issue #7).
- Overriding the right-shift functor alone for indirect/argsort use (sorting indices via a lambda into another array) without also overriding the comparator can give surprising results on small inputs that fall back to default comparison (issue #85).
- Doc header warns exceptions during comparisons, swaps/moves, the right shift, or iterator operations propagate and 'may cause data loss'; only the internal small-vector-resize-throw path is documented as data-loss-free.
- Needs O(key_length) extra memory for radix buckets, so memory scales with key bit-width as well as N — not a fixed small overhead like introsort's O(log N).

**Status:** Actively maintained as part of Boost (last commit 2026-04-11 on develop); BSL-1.0 licensed, header-only, and small enough to vendor without a build step.

[repo](https://github.com/boostorg/sort) · [benchmark](https://github.com/boostorg/sort/blob/develop/doc/linux_single.qbk)

##### Highway (vqsort)  `C++`  `Apache-2.0 OR BSD-3-Clause`  `active`  `Tier A`

SIMD-dispatched vectorized quicksort/quickselect for built-in key types; ~10x faster than LLVM std::sort on large arrays.

**Beats:** std::sort — hwy/contrib/sort/README.md shows vqsort at 1143 MB/s vs LLVM libc++ std::sort at 54 MB/s (~21x) sorting 1e6 uniform-random f32 keys under AVX3 (AVX-512) on a Xeon 6154 (Skylake-X) at 3 GHz, built with Clang 13.0.1/15.0.6 via `bazelisk build -c opt`; the README's own headline claim is the more conservative '~10x for large arrays of built-in types' as of 2022-06-07, and it separately notes pdqsort-class scalar sorts are about 2x std::sort, not 10x.

**How:** Vectorized Quicksort (VQSort paper, arXiv:2205.05982): wide-SIMD partitioning (AVX-512/AVX2/NEON/SVE-width) with in-register sorting networks for base cases, and pivot selection from a 384-byte random sample to balance partitions and avoid recursing into all-equal runs. Later work added 8x2/8x4/4x1/8x1 sorting-network shapes for small inputs and moved RNG seeding into a per-thread TLS cache (previously it fetched OS entropy on every call), which removed most of the small-array overhead (hwy/contrib/sort/README.md, 'Optimizations for small arrays').

**Use it when:**
- Sorting large arrays (README recommends >=100 KiB, i.e. roughly 100K+ elements) of built-in numeric types on hardware with real SIMD (AVX2/AVX3, NEON, SVE/SVE2, etc.)
- Throughput-bound bulk sorting where equal-key order doesn't need to be preserved (unstable sort)
- Sorting packed key-value pairs (K32V32, K64V64) or 128-bit keys without a separate index/permutation array
- Top-k or median-style workloads via VQPartialSort/VQSelect instead of a full sort
- Already-vectorized pipelines that keep AVX-512 'warm', so even small VQSort calls benefit without startup penalty (README AVX-512 startup analysis)

**Skip it when:**
- Sorting custom structs/classes or needing a user-supplied comparator — only fixed built-in key types with ascending/descending order are supported
- Anywhere a stable sort is required; VQSort does not preserve the relative order of equal keys
- Near-sorted input on aarch64/NEON: issue #3139 (open) reports VQSelect/VQSort running 2-4x slower than scalar sort in that case
- Small arrays dropped into an otherwise scalar codebase: AVX-512 warm-up/downclocking can shrink the effective speedup on ~10K-element inputs from ~10x to as little as 1.4x (README AVX-512 startup study)
- SVE2-128 targets: issue #3336 (open) reports a Clang-only Min-instruction workaround costs 26-40% of VQSort's runtime there

**Integration:** source-drop | static lib | shared lib · none for the sort module itself (only the rest of the Highway headers, e.g. hwy/base.h, hwy/os_rng.h); Highway's own test suite additionally uses googletest, not required for library use · C++17; CMake build (Bazel also supported); published sort benchmarks used Clang 13.0.1/15.0.6 · 27 Highway targets across x86-64 (SSE2 through AVX10.2), Armv7+/NEON/SVE/SVE2, POWER8-10, RISC-V (RVV), IBM Z14/Z15, LoongArch, and WebAssembly; the headline vqsort speedup needs AVX2/AVX3/NEON/SVE-class SIMD

**Vs siblings:** Pick vqsort over pdqsort/ska_sort/vergesort when the target hardware has AVX2/AVX3/NEON/SVE and the data is built-in numeric keys (or 32/64-bit key-value pairs) sorted in bulk at 100K+ elements — its wide-SIMD partitioning beats the scalar-only pdqsort/ska_sort/vergesort by roughly an order of magnitude over plain std::sort. Favor the scalar siblings instead when you need a custom comparator, arbitrary key types, a guaranteed-scalar target, or want to avoid Highway's runtime-dispatch machinery entirely.

**Gotchas:**
- Not a stable sort — equal keys can be reordered
- An earlier version re-seeded from OS entropy on every call, which was costly for arrays of ~100-1000 elements; fixed in PR #1334 by caching seeds in TLS per thread — some historical benchmark numbers predate this fix
- Near-sorted arrays on aarch64/NEON can be 2-4x slower than scalar sort (issue #3139, open as of 2026-09)
- The 'about 10x' headline figure assumes AVX-512 is already warm; in a scalar-only surrounding codebase the effective win on medium-small inputs can drop to ~1.4x due to AVX-512 startup and downclocking overhead

**Status:** Actively maintained as part of Google's Highway SIMD library (last commit 2026-09-23, 5.9k stars); dual Apache-2.0/BSD-3-Clause. Listed as 'copyable' — the sort module can be vendored as source (hwy/contrib/sort plus the core Highway headers it depends on) rather than requiring the full library as a prebuilt external dependency.

[repo](https://github.com/google/highway) · [benchmark](https://github.com/google/highway/blob/master/hwy/contrib/sort/README.md)

##### IPS⁴o (In-place Parallel Super Scalar Samplesort)  `C++`  `BSD-2-Clause`  `stale`  `Tier A`

In-place parallel/sequential comparison sort beating std::sort via cache-efficient block-based samplesort partitioning.

**Beats:** std::sort — On the four-machine benchmark suite (arXiv 2009.13569, GCC 7.5.0, -march=native -O3), sequential IPS4o averaged roughly 2x std::sort's throughput on double/uint64/uint32 keys (Table 1 'Total' slowdown factors 1.20-1.78 for IPS4o vs 2.47-3.93 for std::sort's libstdc++ introsort), and Fig. 11 shows std::sort off-plot and slower than IPS4o on uniform uint64 across all four machines (AMD Ryzen 9 3950X, AMD EPYC Rome 7702P, 2x Xeon E5-2683 v4, 4x Xeon Gold 6138). The paper gives no direct parallel-vs-std::sort figure; its parallel speedups (8.37x-40.92x) are relative to sequential IPS4o, not std::sort.

**How:** Superscalar samplesort: recursively partitions the array in-place into many buckets per pass using a branchless decision tree over sampled splitters, then permutes elements block-by-block to stay cache-efficient without extra memory. It special-cases inputs with many equal elements to avoid pathological partitioning, and the parallel version dynamically load-balances buckets across threads.

**Use it when:**
- Sorting large arrays/vectors of primitives, floats, or small records (Pair/Quartet/100-byte) in-place with no extra buffer
- Multi-core machines where parallel::sort (OpenMP or std::thread + TBB) can use the extra cores for large inputs (roughly n >= 2^18)
- Data with many duplicate keys or skewed distributions, which the branchless classifier handles without the usual pathological slowdown
- Sequential drop-in replacement for std::sort on Linux/macOS with a C++14-capable GCC or Clang toolchain

**Skip it when:**
- Windows builds -- the README states the code does not currently compile on Windows
- Very small inputs (n <= 2^15), where BlockQuicksort is faster per the record's caveats
- Need a stable sort that preserves the relative order of equal keys -- not documented as stable, and in-place bucket permutation gives no such guarantee
- Can't add TBB and libatomic (or -mcx16 / native 16-byte CAS) to the build -- parallel mode requires them; sequential-only mode is header-only with no dependencies
- Sanitizer-clean concurrency required -- open, unresolved TSan-flagged data race in the parallel presort check (issue #3)

**Integration:** header-only · sequential: none. parallel: pthreads/std::thread, TBB, libatomic (or -mcx16 / native 16-byte compare-and-exchange) · C++14 (CMakeLists sets CMAKE_CXX_STANDARD 14); benchmarked with GCC 7.5.0, -march=native -O3 · Linux/macOS, GCC or Clang, x86-64 (16-byte CAS needed for fastest parallel mode); does not compile on Windows

**Vs siblings:** Pick IPS4o over BlockQuicksort/quadsort/fluxsort when you need a parallel multi-core sort or must stay robust across many data types and skewed/duplicate-heavy distributions; pick those instead for a header-only, dependency-free sequential drop-in with a simpler build.

**Gotchas:**
- Parallel mode needs 16-byte atomic compare-and-exchange (-march=native or -mcx16, plus -latomic) or it falls back to lock emulation and loses speed
- CMake's IPS4O_OPTIMIZE_FOR_NATIVE defaults to ON (-march=native), which can produce binaries that crash on other CPUs if redistributed
- Open, unresolved TSan-flagged data race in the parallel presort check (issue #3)
- The ips4o/ips4o repo ships no benchmark code (only src/example.cpp); the paper's numbers come from the separate GPL-3.0 ips4o-benchmark-suite, which is not linked from the README

**Status:** Stale (last commit 2025-01-15) but the maintained successor to the deprecated SaschaWitt/ips4o fork; BSD-2-Clause and header-only for sequential use, so it is easy to vendor even without upstream activity.

[repo](https://github.com/ips4o/ips4o) · [benchmark](https://arxiv.org/abs/2009.13569)

##### pdqsort  `C++`  `Zlib`  `abandoned`  `Tier A`

Header-only C++ drop-in std::sort replacement: pattern-defeating quicksort with branchless partitioning and a guaranteed O(n log n) worst case.

**Beats:** std::sort, std::stable_sort — Per the record's verified README bar chart (std::vector<int>, 10^6 elements, i5-4670k @ 3.4GHz, g++ -std=c++11 -O2 -m64 -march=native), pdqsort beat GCC libstdc++ std::sort on all 8 tested distributions, from ~1.9x on shuffled ints to over 10x on ascending/all-equal/push-middle patterns. Against std::stable_sort it was faster on most patterns (~2.4x on shuffled) but ~2.3x slower on pipe organ and about tied on push front.

**How:** Quicksort with median-of-3 pivoting (Tukey's ninther above 128 elements), switching to insertion sort below 24 elements, and falling back to std::make_heap/std::sort_heap after O(log n) highly unbalanced (<12.5% or >87.5%) partitions, which bounds the worst case at O(n log n) like introsort. After every partition it checks whether the sequence was already partitioned and, if so, attempts a move-bounded insertion sort, giving linear time on sorted/equal/nearly-sorted patterns. For arithmetic types with a default comparator it uses the branchless partitioning technique from Edelkamp & Weiss's BlockQuicksort paper, filling small index buffers with unconditional stores to avoid branch mispredictions during partitioning.

**Use it when:**
- Sorting std::vector/array of built-in arithmetic types (int, float, double) with the default comparator, where the branchless fast path auto-activates
- Data likely to contain patterns: nearly-sorted, reverse-sorted, many duplicate keys, or one misplaced element in an otherwise sorted run
- Header-only C++03/C++11 codebases that want a drop-in std::sort replacement without adding a build/link dependency
- Large arrays (1000+ elements) where branch-misprediction overhead in a naive quicksort partition loop matters
- Need a guaranteed O(n log n) worst case (heapsort fallback) without giving up quicksort's average-case speed

**Skip it when:**
- Need a stable sort (equal elements keep relative order) — no stable variant is provided, unlike std::stable_sort
- Comparator itself is expensive (e.g. calls into an interpreted-language callback) — issue #20 shows pdqsort can invoke the comparator more often than glibc qsort/introsort, making it slower than std::sort or qsort when comparison cost dominates
- Data shaped like a 'pipe organ' (ascending then descending) sorted against libstdc++ std::stable_sort — the verified README chart shows pdqsort ~2.3x slower there, and roughly tied on 'push front'
- Need MSVC 64-bit builds warning-clean — open issue #22 (int64->int conversion warnings) is unresolved
- Need std::execution parallel policies or a maintained upstream — no commits since 2021-03-14 and issue #16 (C++17 parallel execution) is still open

**Integration:** header-only · none (standard library only: <algorithm>, <cstddef>, <functional>, <utility>, <iterator>, plus <cstdint>/<type_traits> under C++11) · C++03 compiles (branch-based path only); C++11+ enables automatic branchless dispatch and move semantics · any (portable C++, no SIMD/architecture-specific intrinsics); MSVC 64-bit builds emit C4244 int64->int conversion warnings (open issue #22)

**Vs siblings:** Prefer pdqsort over Highway (vqsort) when you can't require AVX2/AVX3 hardware or want to avoid a SIMD library dependency, and over ska_sort when your keys aren't specifically skewed/geometric-distributed integers. vergesort is the closest comparison (same libstdc++ pattern-detection premise, also unstable-vs-stable tradeoffs), but pdqsort additionally documents a branchless partitioning fast path for arithmetic types with default comparators.

**Gotchas:**
- Branchless auto-dispatch only triggers for arithmetic value types compared with std::less/std::greater under C++11; custom structs or comparators always take the slower branch-based path unless you call pdqsort_branchless explicitly
- Can make more comparator calls than a plain qsort/introsort in some cases (issue #20), so it loses to std::sort/qsort when the comparator itself is costly, even though it does fewer swaps
- Switches to std::make_heap/std::sort_heap after O(log n) highly unbalanced partitions, so pathological inputs degrade to heapsort speed, not quicksort speed
- Comparator ordering requirements (strict weak ordering vs. total order) are not documented in the README (issue #28, open question, unanswered as of last commit)

**Status:** Abandoned: no commits since 2021-03-14, the same day an integer-overflow fix (issue #13) landed; a later MSVC-warning issue (#22, 2022) and a C++17 parallel-execution request (#16, 2024) remain open and unaddressed. zlib-licensed and a single ~350-line header, so it's cheap to vendor and patch yourself if needed.

[repo](https://github.com/orlp/pdqsort) · [benchmark](https://github.com/orlp/pdqsort)

#### string-search-and-hashing

##### HighwayHash  `C++`  `Apache-2.0`  `abandoned`  `Tier A`

SIMD-based keyed hash function; ~5x faster than SipHash at 1 KiB while keeping DoS-resistant strong-hash security claims.

**Beats:** SipHash — On a single idle core of an Intel Xeon E5-2690 v3 (2.6 GHz) compiled with a patched GCC 4.9, the README's own benchmark table shows HighwayHashAVX2 at 0.24 cycles/byte for 1024-byte inputs vs SipHash's 1.26 cycles/byte (~5.25x) and 0.95 vs 1.93 cycles/byte at 64 bytes (~2x), consistent with the linked arXiv paper's stated 5.2-5.3x speedup at 1 KiB.

**How:** Mixes input using SIMD 32x32->64-bit multiplies and permutes over a 1024-bit internal state held in AVX2/SSE4.1/VSX/NEON registers, with specialized handling of partial vectors for small inputs. The AVX2 build reaches 0.24 cycles/byte at 1024 bytes vs SipHash's 1.26, more than twice as fast as the repo's own SipTreeHash variant. A runtime dispatcher (instruction_sets.h) selects AVX2, SSE4.1, VSX, NEON, or a portable fallback at first use so one binary can exploit the widest available SIMD without recompiling.

**Use it when:**
- Hash-flooding-resistant hashing where a strong keyed hash faster than SipHash is needed, especially for inputs >=64 bytes where the AVX2 speedup is largest
- x86-64 targets with AVX2 or SSE4.1, or POWER (VSX) / ARM/AArch64 (NEON) where the corresponding source file is included
- Applications that persist hashes long-term: output format is declared frozen forever, so stored hashes never break on upgrade
- Need 128- or 256-bit digests (checksums/integrity) from a single pass, not just a 64-bit hash
- Willing to vendor an archived Apache-2.0 source drop and pin a validated compiler rather than depend on a maintained package

**Skip it when:**
- Need a literal std::hash / std::unordered_map drop-in swap — HighwayHash needs explicit key management and its own state object, not a hasher functor substitution
- Target platform has none of AVX2/SSE4.1/VSX/NEON: falls back to a portable path the README says runs at ~10% of AVX2 throughput
- Building with a modern stock compiler without validating output first: open issue #94 (filed 2020, still open) reports a Portable-target hash mismatch on GCC 10.2, and the archived repo will never fix it
- Need the 'cryptographically strong' framing to hold at typical hash-table bin counts — the repo's own issue #28 is an unresolved dispute over that security claim
- Need active maintenance or security patching — GitHub shows the repository archived (read-only) and the hash output is explicitly frozen, so no further algorithmic or compiler-compat fixes will land

**Integration:** source-drop / static lib (Makefile and CMakeLists.txt build lib/libhighwayhash.a; CMake's BUILD_SHARED_LIBS option can produce a shared lib instead) · none beyond the C++ standard library; pthread is linked for the optional ThreadPool/profiling utilities, not required for hashing itself · C++11 (Makefile and CMakeLists.txt both pass -std=c++11); CMake >= 3.18 for the CMake build path; GCC/Clang new enough for AVX2/SSE4.1/NEON intrinsics as needed per target · x86-64 (AVX2 or SSE4.1), ARM/AArch64 (NEON), POWER (VSX), plus a portable C++ fallback for any other architecture

**Vs siblings:** Pick HighwayHash over komihash/MUM-hash/t1ha/rapidhash when the requirement is specifically SipHash's DoS-resistant strong-hash security framing plus multi-width (64/128/256-bit) SIMD output beating SipHash, not just the fastest possible non-cryptographic hashmap key hash; those sibling hashes target xxHash/CityHash/wyhash-class baselines for general-purpose hashing and are actively maintained, unlike this archived, output-frozen project.

**Gotchas:**
- Output is declared 'frozen forever' in the README: no future release will ever change existing hash values, but also none will ever improve speed or security further
- Intrinsics-using headers must be compiled into separate per-target translation units with matching flags (README 'Dispatch' section); mixing this up risks an ODR violation and crashes
- AVX2 carries a ~56K-cycle warmup penalty on Haswell-era CPUs per the README, so the authors recommend against AVX2 for infrequent/sporadic hashing in an otherwise non-AVX2 application
- Repository is GitHub-archived (read-only); open issue #94 (GCC 10.2 Portable-target hash mismatch, filed 2020) has no fix and, given the archival, never will

**Status:** Abandoned: the GitHub repo is archived (read-only), last commit 2024-04-18, and the hash output is explicitly declared frozen forever; it is Apache-2.0 licensed and small enough to vendor as a source drop, but pin and test the exact compiler version given the open, unresolved GCC 10.2 output-mismatch report (issue #94).

[repo](https://github.com/google/highwayhash) · [benchmark](https://github.com/google/highwayhash/blob/master/README.md)

##### komihash  `C`  `MIT`  `active`  `Tier A`

Header-only, non-cryptographic 64-bit hash beating wyhash and xxHash on short keys (0-31 bytes) via full 128-bit multiply accumulation.

**Beats:** xxHash (XXH3_64 / XXH64) and wyhash_final4 — Author-run README benchmark across 10 compiler/CPU/OS combinations (GCC 11.5, Clang 18/19, ICC 19, clang-cl 18, Apple Clang 15 on Ryzen 3700X/9950X, Xeon E-2386G, Core i7-7700K, Apple M1) shows komihash 5.34 averaging 7.2 cycles/hash (0-15 bytes) and 8.6 cycles/hash (8-28 bytes) versus wyhash_final4 13.5/18.0, XXH3_64 14.2/21.8, and XXH64 10.2/15.0 — roughly 1.9-2.5x fewer cycles on short keys. On 256,000-byte bulk buffers komihash (19.3-42.7 GB/s) loses to XXH3_64 (28.0-68.4 GB/s) on all 10 platforms and to wyhash_final4 on 8 of 10.

**How:** Unlike wyhash/CircleHash/lehmer64-style hashes, komihash keeps the full 128-bit result of each internal multiplication instead of folding it back into one 64-bit state word, so consecutive internal states stay distinguishable rather than losing entropy. It parses the input message without overlapping reads, which the author argues avoids the seed-value flaws overlap-based parsers can hit, while keeping branch count low on the 0-15/8-28 byte fast paths. It's scalar C99 (no SIMD requirement), so short-key speed comes from a tight instruction sequence rather than vector width.

**Use it when:**
- Hash table/map/Bloom-filter keying where short keys (0-31 bytes) dominate and you want lower cycles/hash than wyhash_final4 or XXH3_64 without requiring AVX2/SIMD
- Need identical hash values on both big- and little-endian platforms (e.g. hashes stored/compared across architectures)
- Hashing values whose total length isn't known upfront, or hashing many independent fixed-size fields incrementally (discrete-incremental API)
- Want a single dependency-free header (MIT) that's trivial to vendor into a C or C++ codebase
- Portable/scalar targets (no SIMD available) where a branch-light, non-vectorized hash is required

**Skip it when:**
- Bulk/large-buffer hashing (files, big blobs): on the README's own 256,000-byte test komihash (19.3-42.7 GB/s) loses to XXH3_64 (28.0-68.4 GB/s) on all 10 tested platforms and to wyhash_final4 on 8 of 10
- Adversarial or untrusted input where seeded collision-resistance matters: issue #23 (opened 2026-09-18, open as of this review) demonstrates a fixed 64-byte message pair that collides for ~91% of uniformly-random hidden 64-bit seeds, which weakens the README's 'seed it and hash-flooding risk is minimized' guidance
- Need a std::hash<T> drop-in for unordered_map/unordered_set without writing a wrapper — komihash exposes plain C functions, not a functor
- 32-bit target platforms, where the README states throughput is 'considerably lower' than 64-bit (no number given)
- Need cryptographic collision resistance — explicitly a non-cryptographic hash

**Integration:** header-only · none (standard C headers only: stdint.h, string.h) · ISO C99 (C++98 supported via a stdint.h fallback path; full auto C++ compatibility, with extra branch optimizations under C++11+) · x86, x86-64 (Intel/AMD), AArch64 (Apple Silicon); tested on Windows 10/11, AlmaLinux 9.6, macOS 26.4; scalar code, no SIMD required; 32-bit builds work but are notably slower per README

**Vs siblings:** Pick komihash over t1ha/CityHash/MUM-VMUM when you want the widest reproducible compiler/CPU benchmark matrix (10 combos) for short-key throughput and don't need SIMD. Pick rapidhash or another sibling instead if the open seed-dependent collision report (issue #23) is disqualifying for your threat model, or if bulk-buffer throughput matters more than short-key speed.

**Gotchas:**
- Open issue #23 (filed 2026-09-18, unresolved as of this review): a fixed 64-byte message pair collides under komihash for ~91% of uniformly-random hidden seeds, reproduced independently by the reporter against the released 5.34 header — a real gap in the 'seed it for collision-attack resistance' advice
- Default seed is 0 (no randomization) unless the caller passes one; self-seeding is required for any hash-flooding resistance, and per the issue above that resistance is weaker than the README implies
- No identity/passthrough hashing: README explicitly recommends using raw key values directly for fixed-size keys rather than hashing them, since komihash adds overhead a no-op wouldn't have
- Big-endian systems pay a ~20% bulk-throughput penalty from byte-swapping, which can be disabled via a macro but then breaks cross-platform hash-value portability

**Status:** Actively maintained (last commit 2026-08-04, MIT-licensed, 286 stars) and trivial to vendor as one header, but an unresolved collision report (issue #23, opened 2026-09-18, six days before this review) is a live caveat for any security-relevant use.

[repo](https://github.com/avaneev/komihash) · [benchmark](https://github.com/avaneev/komihash/blob/master/README.md)

##### MUM/VMUM hash  `C`  `MIT`  `active`  `Tier A`

Header-only C multiply-mix hash family (MUM/VMUM) rivaling xxHash3, beating CityHash and SipHash24 on most key sizes.

**Beats:** xxHash3, Google CityHash (City64), Bob Jenkins SpookyHash, SipHash24, MetroHash, t1ha2 — widely-used non-cryptographic hash functions used in place of std::hash for hash-table keys — Hashing 1,280M keys (3-1024 bytes) plus 10,000x16MB bulk keys, GCC -O3 (-flto added only for the competing hash functions, not MUM/VMUM), pinned single-core runs, minimum of 3 repeats kept: VMUM-V2's geomean relative throughput (1.00 baseline) is xxHash3 0.79, CityHash 0.38, SipHash24 0.21 on Apple M4 (GCC 14.2.1), and xxHash3 0.93, CityHash 0.48 on IBM Power10 (GCC 11.5.0) -- i.e. VMUM-V2 is ~1.3x faster than xxHash3 and ~2.6x faster than CityHash on M4, and roughly on par with xxHash3 on Power10.

**How:** MUM (Multiply and Mix) randomizes each 64-bit chunk with a 64x64->128-bit multiply, mixes the high/low halves with addition, and XORs into a running state, using a table of pre-generated random factors; the main loop is written to be unrolled by the compiler for out-of-order scheduling, with no per-byte branching. VMUM extends this with target vector instructions (AVX2 32x32->64 multiplies on x86-64, NEON on aarch64, Altivec on ppc64) processing multiple lanes per step, and runs two unrolled loops in parallel to keep OOO execution units busy; targets without vector support fall back to scalar emulation.

**Use it when:**
- Very short keys (3-16 bytes) where MUM/VMUM's fast startup wins on every benchmarked machine (ratio ~1.00 vs xxHash3's 0.7-0.95)
- Long keys (512-1024 bytes) and 16MB bulk hashing on AVX2 (x86-64) or NEON (aarch64) hardware, where VMUM-V2 is ~1.1-1.9x faster than xxHash3
- Apple M4 / aarch64 targets specifically, where VMUM-V2 beats xxHash3 by ~1.3x geomean and CityHash/SipHash24 by 2.6x/4.8x
- Hash-table implementations that want a header-only C hash with no crypto/library dependency and are willing to hand-write the call sites
- Cases wanting the collision-attack-resistant fixed hash by default (Nov 2025 fix), with the ability to opt back into the faster pre-fix variant via VMUM_V1/MUM_V3 macros for controlled environments

**Skip it when:**
- Mid-size keys, roughly 32-128 bytes (16 bytes on Power10): xxHash3 is faster there, e.g. 128 bytes is 1.98x faster on AMD, 1.81x on M4, 2.03x on Power10
- Targets without AVX2/NEON/Altivec and without a compiler 128-bit-integer extension: VMUM drops to scalar emulation and MUM needs GCC/Clang-style __int128 to hit its documented numbers
- Projects that require a real drop-in for std::hash/xxHash's call signature without touching call sites -- MUM/VMUM's API shape is different
- Teams uncomfortable with no LICENSE file at repo root (MIT is only asserted in per-file header comments; GitHub's own license detector shows none)
- Cross-platform byte-identical hashes across BE/LE or 32/64-bit targets, unless [V]MUM_TARGET_INDEPENDENT_HASH is explicitly defined (with a performance cost on BE/no-int128 targets)

**Integration:** header-only (single file: mum.h or vmum.h) · none beyond the C standard library (stddef.h, stdlib.h, string.h, limits.h, stdint.h) · C99; GCC or Clang recommended to get the 128-bit-integer multiply path (checked via __GNUC__); MSVC compiles via typedef shims but takes the non-__int128 fallback path · x86-64 (AVX2 needed for VMUM's full speed, e.g. -mavx2), aarch64 (NEON), ppc64 (Altivec); scalar emulation on any other target

**Vs siblings:** Pick VMUM over rapidhash, t1ha, or CityHash when hashing very short keys (<=16 bytes) or long/bulk keys on AVX2 or NEON hardware, where it edges out xxHash3 and clearly beats CityHash/SipHash24/t1ha2. Prefer xxHash3, rapidhash, or komihash instead for the common 32-128 byte range, where VMUM-V2 loses to xxHash3 by up to ~2x.

**Gotchas:**
- The pre-Nov-2025 VMUM/MUM-V3 variants have a collision-attack weakness (issue #18: an adversary can zero one operand of _vmum to force identical hashes); the fix is now default and costs ~10% throughput, old fast variants are opt-in via VMUM_V1/MUM_V3 macros
- No LICENSE file at repo root; MIT terms live only in the header comment of each source file (mum.h, vmum.h, mum512.h, mum-prng.h)
- Hash values are not target-independent by default (differ across BE/LE and 32/64-bit, and with/without int128 support) unless [V]MUM_TARGET_INDEPENDENT_HASH is defined
- VMUM needs an explicit compile flag (e.g. -mavx2 on x86-64, -mcpu=native/NEON on aarch64) to use its vector code path; without it, it silently falls back to slower scalar emulation

**Status:** Actively maintained (last commit 2026-06-02, with a collision-attack fix shipped Nov 2025); MIT-licensed via per-file source headers (no repo-root LICENSE file) and small enough as single headers to vendor directly.

[repo](https://github.com/vnmakarov/mum-hash) · [benchmark](https://github.com/vnmakarov/mum-hash#vmum-and-mum-benchmarking-vs-other-famous-hash-functions)

##### sse4-strstr (SIMD-friendly algorithms for substring searching)  `C++`  `BSD-2-Clause`  `abandoned`  `Tier A`

SIMD substring-search kernels (SSE2-AVX512, NEON) from a blog article; beats glibc strstr by ~1.3-1.8x on x86.

**Beats:** std::strstr / libc strstr (same problem as std::string::find and the default std::search) — On an Intel Skylake i7-6700 with GCC 5.4.1 (-O3 -mavx2), the repo's own speedup_avx2 benchmark scanning data/i386.txt for data/words shows glibc std::strstr at 0.662s vs the "AVX2 (generic)" kernel at 0.364s across three runs with identical checksums (~1.82x faster); "SSE2 (generic)" is 0.489s (~1.35x faster). std::string::find is not measured on this run -- the harness skips it on GCC/x86.

**How:** SWAR and SIMD kernels (SSE2, SSE4.1 MPSADBW, SSE4.2 PCMPESTRM, AVX2, AVX512F/BW, NEON) scan 16-64 bytes per iteration instead of glibc strstr's byte-at-a-time loop. The fastest "generic" kernel behind the cited 1.82x number (avx2_strstr_v2 -> avx2_strstr_anysize) broadcasts the needle's first and last byte across a 32-byte AVX2 vector, compares both in one pass to get a lane mask of candidate offsets, then verifies each candidate with a short memcmp -- a vectorized two-byte filter (0x80.pl's "SIMD-friendly Karp-Rabin" scheme), not a per-byte scan. Needles of length 2-12 get separate template-specialized SSE4.1/AVX2 kernels tuned per exact length.

**Use it when:**
- Exact single fixed-needle search over large in-memory byte buffers (logs, text corpora) on x86-64 with SSE4.1/AVX2/AVX512, or ARMv7/AArch64 with NEON, where the scan itself is the bottleneck
- You want reference/teaching code for SIMD substring-search techniques (the vectorized Karp-Rabin-style first/last-byte filter) rather than a dependency
- You can vendor a handful of individual .cpp/.h files into your own build instead of linking a packaged library
- Needle length and target ISA are known ahead of time so you can pick/compile the matching kernel (SSE4, AVX2, AVX512BW, NEON) for your CPU
- You're willing to own and patch the code yourself going forward -- no upstream maintenance since Jan 2022

**Skip it when:**
- You need a drop-in for std::string::find/strstr with wide-char support, custom predicates, or a std::string_view-friendly API -- none of that exists here
- You need multi-needle or streaming search; only a single fixed needle against a fully-buffered haystack is implemented (open issue #18 asks for multithreading, #19 for combining with Raita's algorithm -- both unaddressed)
- You need a maintained, packaged dependency: no releases, no build-system package config, last commit 2022-01-04, and confirmed bugs (#11, #16) are unfixed
- Needle length 1 passed directly to the low-level avx2_strstr_anysize kernel (bypassing the dispatcher) hits a confirmed bug: k-2 underflows (issue #11)
- On current hardware/libc the maintainer himself says (issue #12, 2020) "AVX2 won't help much" over a decent modern strstr -- re-benchmark on your own CPU/libc before adopting

**Integration:** source-drop · none (uses <immintrin.h>/<arm_neon.h> intrinsics and the C++11 standard library only) · C++11; GCC or Clang with the matching ISA flag per kernel (-msse4.2, -mavx2, -mavx512bw, -mfpu=neon) · x86-64 (SSE2 baseline; SSE4.1/4.2, AVX2, AVX512F/AVX512BW variants gated by build flags), ARMv7 (NEON) and ARMv8/AArch64

**Vs siblings:** Pick this over StringZilla or Boost.Algorithm's Boyer-Moore/Boyer-Moore-Horspool searchers only when you specifically want the raw, ISA-specific kernel source to vendor one function with zero dependencies (no Boost, no StringZilla) or to study the 0x80.pl vectorized Karp-Rabin technique; both siblings are actively packaged and maintained, and StringZilla in particular reports larger, more current speedups over std::string::find.

**Gotchas:**
- Raw per-length kernels (e.g. avx2_strstr_anysize, sse4_strstr_anysize) assert needle_size > 4 or > 0 depending on variant; only the top-level dispatchers (avx2_strstr, avx2_strstr_v2, sse4_strstr_anysize's callers) special-case short needles (0-4 bytes) via strchr/strstr/memcmp -- calling a raw kernel directly with a short needle is unsafe (issue #11, confirmed bug for k=1)
- The vectorized loops load fixed 16/32-byte windows (_mm256_loadu_si256 at s+i and s+i+k-1) per iteration, which can read past the logical end of the haystack near its tail; the README/code does not document a guaranteed-safe overread margin, so vendoring into a tightly-sized buffer needs care
- Open, unanswered GitHub issue (#16) questions whether the `next1` vector in avx2_strstr_eq (the 2-byte-needle path) is read before being fully initialized
- The repo's own speedup.cpp deliberately skips std::string::find on GCC/x86 builds ("proven to be utterly slow, don't waste our time"), so its own benchmark has no std::string::find numbers to compare against on x86

**Status:** Abandoned: last commit 2022-01-04, not archived, two confirmed/unanswered bugs (#11, #16) unaddressed; BSD-2-Clause and small enough to vendor a single kernel file, but the maintainer himself notes (2020) that on modern CPUs/libc the AVX2 advantage over strstr is small.

[repo](https://github.com/WojciechMula/sse4-strstr) · [benchmark](https://github.com/WojciechMula/sse4-strstr/blob/master/results/skylake-i7-6700-gcc5.4.1-avx2.txt)

##### t1ha (Fast Positive Hash)  `C`  `Zlib`  `abandoned`  `Tier A`

Portable C hash family (t1ha0/1/2) beating xxHash/Murmur on bulk throughput; modest edge on tiny keys.

**Beats:** xxHash32 (also xxHash64 and the Murmur2/Murmur3 family) in SMHasher speed tests — On SMHasher speed tests run in 2016 (GCC 5.4.0, -march=native -O3 -fPIC, Intel Core i7-6700K), t1ha_aes averaged 33.03 cycles/hash and t1ha 35.55 vs xxHash32's 43.72 over 1-31 byte keys (~1.2-1.3x fewer cycles), while on a 262144-byte bulk block t1ha_aes reached 34,636 MiB/s and t1ha 12,229 MiB/s vs xxHash32's 5,514 MiB/s (~6.3x/~2.2x) and xxHash64's 11,123 MiB/s (~3.1x/~1.1x). The verification pass found the source record had mislabeled those bulk MiB/s figures as the 'small keys' result; the real small-key edge over xxHash32 is only ~1.2-1.3x.

**How:** The t1ha0_ia32aes_* variants use AES-NI instructions for hardware-accelerated mixing (this is the 't1ha_aes' benchmark line); each AES-NI variant is compiled with its own flags (-maes plus -mavx/-mavx2 per meson.build) and t1ha0 picks among them, plus 32-bit and big-endian fallbacks, at runtime via T1HA0_RUNTIME_SELECT (optionally using GNU ELF indirect functions to cut call overhead). The core mixing uses a NH/UMAC-style multiply-add construction that the README's FAQ says was deliberately fixed to avoid the 'blinding multiplication' entropy-loss flaw it attributes to plain NH-family designs (and, per the README, to wyhash).

**Use it when:**
- Bulk hashing of large buffers (KB+: checksums, content fingerprinting, dedup) on x86_64 with AES-NI, where the 2016 SMHasher bulk numbers show t1ha_aes far ahead of xxHash32/64
- Need a single API that gives both a 64-bit and a 128-bit digest via the same streaming context (t1ha2_init/update/final)
- Already a portable C (not C++) codebase, or need a C-callable hash with existing Rust/Erlang/Go/Kotlin bindings (linked from the README)
- Willing to vendor a small, frozen, Zlib-licensed source drop (3 .c files) since no upstream fixes are coming
- Mixed/heterogeneous CPU fleet where t1ha0's automatic best-available-implementation dispatch is worth its small indirection cost

**Skip it when:**
- Tiny keys (a few bytes to ~31 bytes) on a modern CPU: the maintainer's own later self-check (i7-4600U, GCC 9.3, in the README) shows t1ha2_atonce at 17.25 cycles/hash already behind xxhash32 (16.55), xxh3_64 (15.1) and wyhash_v7 (14.1) -- the 2016 small-key win over xxHash32 was only ~1.2-1.3x and has since been erased by newer hashes
- Cryptographic or adversarial-input use: the header explicitly states 't1ha' is 'Not suitable for cryptography'; no hash-flood resistance is claimed
- Need active upstream maintenance: GitHub deleted the author's account in 2022 and this repo is a restored read-only mirror; the true origin moved to GitFlic, whose current activity is unverified (a GitFlic fetch timed out during verification)
- Need std::hash-style implicit drop-in: t1ha is an explicit C function call with a seed argument, not something ADL or template specialization picks up automatically
- About to reach for t1ha0_32le/32be or t1ha0_ia32aes without checking the table: the author flags several dispatch targets ('alien' 32-bit/big-endian variants) as niche, and picking the wrong one can be slower than a portable hash

**Integration:** source-drop (3 .c files from /src, or link as a static/shared lib via the provided Makefile/meson.build/vcxproj) · none (pure C, standard headers only: stdint.h, stddef.h, limits.h) · C99 (meson.build passes -std=c99); README recommends GNU C 5.5+, Clang 5.0+, or MSVC 2017 15.6+ for proper performance, older GNU C / VS2013+ also supported · any CPU with native 64-bit arithmetic (portable fallback); accelerated paths for x86/x86_64 (AES-NI, AVX/AVX2) and Elbrus/e2k; separate 32-bit little/big-endian and 64-bit big-endian variants exist but are marked non-primary

**Vs siblings:** Pick t1ha over MUM/VMUM, rapidhash, komihash, or CityHash when you specifically want the AES-NI bulk-throughput path on x86, a plain-C (not C++) implementation with existing Rust/Go/Erlang/Kotlin ports, or a Zlib license; the MUM/VMUM sibling entry directly reports beating t1ha2, and rapidhash/komihash report better small-key numbers than xxHash on modern CPUs, so for tiny-key or newest-hardware workloads check those siblings first.

**Gotchas:**
- t1ha0's chosen implementation depends on the host CPU's detected features, so its output is not guaranteed reproducible across machines; the README says t1ha0 results should only be used at runtime, never persisted or sent over a network -- use t1ha1/t1ha2 for stable, portable results
- t1ha2_atonce's 64-bit result and t1ha2_atonce128's 128-bit result are unrelated values (the 64-bit hash is not a truncation of the 128-bit one), per the header comment
- t1ha1 is documented to fail the strict avalanche criterion in some cases (per the README, discovered via Reini Urban's SMHasher fork); it is kept for compatibility but t1ha2 is the recommended, higher-quality successor
- The AES-NI variants need per-file compiler flags (-maes plus -mavx/-mavx2), not just runtime CPU detection -- building them without the matching flags for your toolchain silently loses the AES-NI path

**Status:** GitHub lists this repo as abandoned/archived, but per its own README that's because GitHub deleted the author's account in 2022 and this is a restored read-only mirror -- the stated true origin moved to GitFlic, whose activity level is unverified. Zlib-licensed and small (3 .c files), so it is cheap to vendor and self-maintain regardless.

[repo](https://github.com/erthink/t1ha) · [benchmark](https://github.com/erthink/t1ha/blob/master/README.md)

##### rapidhash  `C`  `MIT`  `active`  `Tier B`

Header-only, wyhash-derived 64-bit hash beating xxh3 on latency and throughput on most CPUs; ties or loses on AMD Ryzen.

**Beats:** xxh3 (xxHash3) — not literally std::hash, but the widely-used fast non-cryptographic hash function developers use in place of std::hash — README benchmarks (bench/ harness adapted from xxHash's benchHash, compiler/flags unstated) show rapidhash beating xxh3 on average per-hash latency for 4/8/16-byte keys on Apple M1 Pro, M3 Pro, ARM Neoverse V2, and AMD Turin (roughly tied on Ryzen 9700X), and beating xxh3 on peak throughput hashing 16KB-2MB files on M1 Pro, M3 Pro, M3 Ultra, M4, and Neoverse V2 (xxh3 wins on Ryzen 9700X, 78 vs 68 GB/s). Independently, rurban/smhasher's default-build results table (AMD Ryzen 5 3350G) also shows rapidhash ahead of xxh3 on both bulk throughput and small-key cycles/hash, without stating compiler flags.

**How:** The core is a wyhash-style multiply-mix: a 64x64->128-bit multiply (rapid_mum) folded with XOR (rapid_mix), deliberately avoiding AES-NI/CLMUL or other vectorized instructions so the same code path runs on x86-64 and aarch64. Clang 18+ compiles rapidhash to roughly 185 instructions on both architectures (rapidhashMicro ~140, rapidhashNano under 100, both stack-free). An optional RAPIDHASH_UNROLLED macro trades code size for large-input throughput; RAPIDHASH_PROTECTED trades speed for extra entropy protection against the multiply's zero-collapse cases.

**Use it when:**
- General-purpose in-memory hash-table/hash-map keys needing a fast, SMHasher-passing 64-bit hash as an xxh3 or wyhash replacement.
- Mixed key-size workloads (roughly 4 bytes to 2MB) on x86-64 or aarch64 where one algorithm should cover both tiny keys and large buffers.
- Latency-sensitive small-key hashing (4/8/16 bytes) on Apple Silicon, ARM Neoverse V2, or AMD Turin, where README numbers show rapidhash ~5-9% faster than xxh3.
- Code-size-constrained embedded/mobile targets hashing keys up to ~48 bytes: use rapidhashNano (<100 instructions, no stack usage).
- Cache-miss-sensitive HPC/server code hashing keys up to ~512 bytes: use rapidhashMicro (~140 instructions, no stack usage).

**Skip it when:**
- Streaming/incremental hashing where input length isn't known upfront and can't be buffered whole: no streaming API ships despite the README's 'Streamable' framing (maintainer confirms in issue #39 that the C/C++ side has no streaming implementation and the hash targets short, whole-buffer runs).
- Adversarial or untrusted-input contexts needing DoS resistance: with the default secret, same-length inputs above 16 bytes admit a documented collision construction (issue #25); mitigate by generating a per-process secret with the bundled secret.h.
- Any context requiring cryptographic hashing or collision resistance guarantees: explicitly non-cryptographic.
- Need for a 128-bit or 32-bit hash output: not offered (open issues #26 and #46, no stated plans).
- Peak throughput on AMD Zen5 desktop parts (Ryzen 9700X): xxh3 leads there in the README's own table (78 vs 68 GB/s).

**Integration:** header-only · none (stdint.h, string.h; intrin.h + _umul128 intrinsic on MSVC) · C99 or C++11; constexpr evaluation additionally needs C++14. README claims support for GCC, Clang, Intel icx, and MSVC; the ~185-instruction codegen figure is specifically for Clang 18+. · x86-64 and aarch64 are the tested/optimized targets (no AVX/AES-NI/CLMUL required); the header compiles generically elsewhere via its endianness macros, consistent with the README's 'platform-independent' claim, but only x86-64/aarch64 numbers are published.

**Vs siblings:** Pick rapidhash over komihash or MUM/VMUM when you want the specific hash already vendored into Chromium, Node.js, Folly's F14, Fuchsia, Ninja, JuliaLang, and Zig, plus size-tuned Micro/Nano builds for cache- or code-size-constrained targets. Pick HighwayHash instead if AVX2-level throughput matters more than portability, since HighwayHash depends on vector instructions rapidhash deliberately avoids; pick t1ha or CityHash if a longer independent track record matters more than the newest peak-speed numbers.

**Gotchas:**
- README markets the family as 'Streamable,' but no streaming API exists for C/C++ (open issue #39) — it's designed for short, whole-buffer runs, not incremental hashing.
- Default secret permits a documented collision construction for same-length inputs over 16 bytes (issue #25); use secret.h to generate a custom secret for any adversarial-input exposure.
- rapidhash, rapidhashMicro, and rapidhashNano only produce matching output below 80 and 48 bytes respectively — swapping variants for larger keys silently changes hash values.
- An older header-only revision could produce 'multiple definition of rapid_secret' linker errors across translation units (issue #6, fixed via a static/const macro); the vendored old_version/rapidhashV1.h may not carry that fix.

**Status:** Actively maintained single header (last commit 2026-08-19, V3 released 2025), MIT-licensed and trivial to vendor; open issues (no 128-bit or 32-bit output, no streaming API) mark real feature gaps rather than signs of abandonment.

[repo](https://github.com/Nicoshev/rapidhash) · [benchmark](https://github.com/Nicoshev/rapidhash#outstanding-performance)

### toolchain-and-build

#### build-systems

##### Mill  `Scala`  `MIT`  `active`  `Tier A`

JVM build tool for Java/Scala/Kotlin; 4-44x faster clean/incremental compiles than Maven, 3.6-10.2x than Gradle.

**Beats:** Apache Maven and Gradle — Mill's own docs page (mill-build.org/mill/comparisons/performance.html) benchmarked Mill 0.12.9-native (Java 17) against each project's default Maven/Gradle version on a 2021 M1 MacBook Pro (10 CPU, 32GB RAM), median wall time of 3 runs after warmup. Netty (~500k LOC, 47 modules) vs Maven: 4.0x-44.0x across sequential/parallel/single-module clean, incremental, and no-op compile. Mockito (~100k LOC, 22 modules) vs Gradle: 3.6x-10.2x for the same five scenarios.

**How:** Mill runs a persistent JVM background daemon, avoiding per-invocation JVM startup and classloading. It memoizes every build step as a fine-grained Task in a dependency graph, so unchanged tasks are skipped entirely (no-op compiles finish in ~0.1s). For Java/Scala incremental compiles it uses the Zinc incremental compiler to recompile only files whose changes affect downstream code. Unlike Maven, it works directly with classfiles on disk rather than round-tripping through .m2 jar packing/unpacking, and it parallelizes independent tasks by default.

**Use it when:**
- Multi-module Java/Scala/Kotlin monorepos where edit-compile-test iteration speed matters
- CI pipelines bottlenecked by Maven/Gradle daemon startup or full-module recompilation on every run
- Teams that want built-in selective test execution, test parallelism, and Chrome-trace build profiling without extra plugins
- New JVM projects willing to adopt a non-XML/non-Groovy build DSL from the start
- Want a self-contained native (Graal) launcher with fast CLI startup and no local JDK requirement

**Skip it when:**
- Large existing Maven/Gradle codebase with heavy reliance on the Maven Central/Gradle Plugin Portal plugin ecosystem, which Mill's is much smaller than
- Non-JVM projects (C++/CMake/Cargo, etc.) - not applicable at all
- Windows-ARM machines: Mill has no native executable there (upstream GraalVM limitation) and falls back to the slower JVM launcher, which also needs a system JDK 17+
- Teams running very high task parallelism on newer Mill versions: an open issue (#7381, 1.2.0-RC1) reports up to ~20x slowdown and thread-pool blowup at large --jobs values
- Projects needing mature BSP/IDE tooling parity - several Metals/BSP integration bugs have been filed (mostly closed, but recent)

**Integration:** source-drop (CLI tool + build.mill config file per project, not a library) · none for the default launcher (self-contained Graal native binary, downloads its own JVM for module builds); the '-jvm' launcher variant requires a system JDK 17+ · Mill supports JVM 11+ for evaluating builds (configurable per-project via mill-jvm-version); native launcher needs no local JDK, JVM launcher needs JDK 17+ · Native executables: Windows/Mac/Linux on Intel, Mac/Linux on ARM. Windows-ARM has no native executable and falls back to the JVM launcher.

**Vs siblings:** No sibling overlap: ccache, Buck2, tup, and xmake all target C/C++ or polyglot native builds, not the JVM. Pick Mill specifically when the baseline pain is Maven/Gradle overhead on a Java/Scala/Kotlin project; none of the catalogued siblings apply there.

**Gotchas:**
- PowerShell 5.1 writes UTF-16LE .mill-version files that Mill can't read; PowerShell 7+ is required on Windows
- Benchmark page itself is internally inconsistent on the Mill version used: the summary text says 'Mill 1.1.0' while the detailed benchmark tables specify 'Java 17 + Mill 0.12.9-native'
- The Netty and Mockito ports used for the benchmark are not 100% complete - some subprojects, linters, and Android/Kotlin/OSGI tests were disabled to make the comparison apples-to-apples
- Open bug (#7381) shows severe negative performance scaling (thread pool grows to thousands of blocked threads) at very high --jobs counts on a 1.2.0-RC1 build; unclear if it reached a stable release

**Status:** Actively maintained: latest commit is today (2026-09-24), 2.8k GitHub stars, MIT licensed. Distributed as a self-updating bootstrap script (Maven Central-hosted releases), so it's directly usable without vendoring.

[repo](https://github.com/com-lihaoyi/mill) · [benchmark](https://mill-build.org/mill/comparisons/performance.html)

#### compilers-frontends

##### zapcc  `C++`  `NCSA`  `abandoned`  `Tier B`

zapcc: a Clang fork with a persistent caching server that rebuilds template-heavy C++ 1.2-3.3x faster than GCC/Clang.

**Beats:** GCC, Clang — On Baptiste Wicht's 2016 ETL (header-only, template-heavy) benchmark on a 4-core/16GB desktop, zapcc++ (beta) built ETL's debug config at -j1 in 214s vs 469s for GCC 5.4.0 (~2.2x) and 710s for Clang 3.9 (~3.3x); the release config at -j1 took 640s vs 782s for GCC (~1.2x) and 960s for Clang (~1.5x). Colfax Research's independent 2017 compiler comparison found Zapcc 1.0.1 compiling the TMV library in 510s vs 848s for GCC 7.2.0 and 902s for Clang 5.0.0 (~1.7x) on a 2-socket Xeon Platinum 8168, corroborating the direction and rough magnitude of the gain.

**How:** The zapccs server keeps parsed ASTs, template instantiations, and generated IR/code resident in memory between compiles instead of redoing that work per translation unit, and can reuse results across source files in a way the README compares to link-time inlining decisions being made proactively. This turns repeated compilation of shared, heavily-templated headers (the dominant cost in libraries like ETL) into cache hits instead of full reparses/re-instantiations. The README claims single-file incremental recompiles are typically 10-50x faster than a cold build because only the changed dependency subgraph is reprocessed; full from-scratch builds see smaller (2-5x) gains that scale with how template/header-heavy the project is.

**Use it when:**
- Large, template/header-heavy C++ codebase (clang- or gcc-compatible source) built repeatedly on Linux x86-64, where CI or local dev-loop compile time dominates
- Iterative development where a single file changes and you rebuild often (the caching server gives its biggest wins here)
- Full debug builds of header-only template libraries similar in shape to ETL (measured 2-3.3x faster than Clang/GCC)
- You already know the project compiles cleanly with vanilla Clang and can dedicate a long-lived background process and extra RAM to the caching server
- You don't need sanitizers and can tolerate an unmaintained, LLVM-r325000-vintage (Feb 2018) fork

**Skip it when:**
- Plain C or lightly-templated C++, where the README itself says caching gives little to no acceleration
- Any build needing ASan/UBSan/TSan/MSan - explicitly unsupported
- Modern C++17/C++20 code: development stopped in 2020, last synced to LLVM trunk 2018-02-13, and -std=gnu++17 was still rejected as an invalid value as of the last activity on that issue (Dec 2018)
- Correctness-sensitive or release builds: a user reported (issue #42) non-deterministic object files and binaries that segfault at reproducible-but-build-order-dependent locations under parallel (-j>1) builds, not reproduced with plain clang, and it was never resolved
- Windows/macOS targets: only minimally/lightly tested, MSVC ABI and zapcc-cl are explicitly unsupported, and there is no one left maintaining platform fixes

**Integration:** source-drop · none beyond a standard LLVM/Clang build toolchain (CMake + Ninja, per README) · Effectively frozen at Clang/LLVM ~6.0-era conformance (last merged with LLVM r325000, 2018-02-13); build via CMake + Ninja exactly as for LLVM. -std=gnu++17 was not recognized as of the last relevant activity (issue #32, Dec 2018); treat full C++17/C++20 support as unverified/likely absent. · x86-64 Linux (thoroughly tested, primary target); Windows via MSVC or mingw-w64 targeting mingw-w64 32/64-bit (minimally tested; zapcc-cl/MSVC-ABI target explicitly unsupported); macOS via Clang (experimental, lightly tested). No aarch64 or RISC-V support (a RISC-V feature request was closed unresolved).

**Vs siblings:** Pick zapcc over MIR/c2m or TinyCC when the actual cost is template-instantiation and header re-parsing in a large, clang/gcc-compatible C++ codebase (its gains scale with template/header weight); MIR/c2m and TinyCC instead target small/simple C or C-subset inputs for fast one-shot JIT-style compiles and are both still maintained, whereas zapcc has been abandoned since 2020 with an open, unresolved correctness bug (issue #42).

**Gotchas:**
- The in-memory server can share/inline state across translation units, making -j>1 builds non-deterministic and, per issue #42, occasionally producing binaries that segfault at reproducible-but-order-dependent locations not seen with plain clang
- -std=gnu++17 was rejected as an invalid value as of the project's last active development (issue #32); it was never fixed before the maintainer confirmed (issue #47, 2021) the project is dead
- zapccs must be killed manually (pkill zapcc) to release memory or to pick up a freshly rebuilt zapcc binary; it also has a configurable memory cap (bin/zapccs.config MaxMemory) that silently resets the entire cache when hit
- README recommends -j should not exceed physical core count + 2, especially on hyperthreaded Intel CPUs that report double the physical core count — oversubscribing the server can make builds slower, not faster

**Status:** Abandoned since 2020 (last commit 2020-07-21, last synced to LLVM trunk 2018-02-13); the maintainer confirmed in a 2021 issue that the project is dead. NCSA/LLVM-Release-licensed and copyable, but it's a full compiler toolchain you'd have to build and maintain yourself, not a small vendorable file, and the known non-determinism/segfault correctness bug (issue #42) was never fixed.

[repo](https://github.com/yrnkrn/zapcc) · [benchmark](https://baptiste-wicht.com/posts/2016/12/zapcc-cpp-compilation-speed-against-gcc-54-and-clang-39.html)

#### formatters-linters-lsps

##### Oxlint (oxc-project/oxc)  `Rust`  `MIT`  `active`  `Tier A`

Rust-based JavaScript/TypeScript linter and toolchain that replaces ESLint with 50-100x faster linting.

**Beats:** ESLint — Oxc's own bench-linter repo (hyperfine, 1 warmup, non-zero exits ignored, ESLint v9, no ESLint cache) measured Oxlint linting the VS Code source tree at 62.10x/118.25x/60.09x ESLint's speed on an M2 Max 12-core / M4 Max / M3 Air 8-core respectively, and ~17x single-threaded (31.025s vs 1.824s on M2 Max); vs Biome on the same tree with only the no-debugger rule enabled, 2.72x/2.49x/3.31x across the same three machines; vs typescript-eslint with type-aware rules on Vue core and Sentry (M2 Max), 8.22x and 12.38x respectively.

**How:** Oxlint reuses oxc's own parser and semantic analyzer, built on an arena allocator (oxc_allocator), so most rules run in a single AST traversal instead of ESLint's per-rule/per-plugin dispatch. Files are linted in parallel across CPU cores via Rayon, with the `ignore` crate (SIMD-accelerated) walking the file tree, so throughput scales with core count. That parallelism is why the gap widens on more cores: ~17x single-threaded vs ESLint, up to ~62-118x multi-threaded on 8-12 core machines in the project's own benchmark.

**Use it when:**
- Large JS/TS monorepos where ESLint's per-file startup and plugin dispatch overhead dominates CI time
- Standard-rule linting (no exotic plugin needs) where raw throughput matters more than full rule-set parity
- Multi-core CI runners or dev machines, since the speedup scales with thread count
- Teams migrating incrementally, running Oxlint alongside ESLint to cover the remaining rule gap
- Projects wanting near-instant `npx oxlint` feedback with zero required config

**Skip it when:**
- Codebases that depend on ESLint plugins with no Oxlint equivalent or JS-plugin bridge
- Projects needing full type-aware linting parity with typescript-eslint - gain drops to 8-12x and rule coverage is narrower, and it needs the separate oxlint-tsgolint/TypeScript 7 component
- Repos still on legacy ESLint v8 config - must convert to flat config via @eslint/migrate-config before the official migration tool works
- Setups with local/custom ESLint plugins - these do not migrate automatically
- Single-core or low-core environments, where the advantage shrinks toward the ~17x single-threaded figure

**Integration:** crate · Rust workspace of internal oxc_* crates (oxc_allocator, oxc_parser, oxc_linter, oxc_semantic, ...) plus rayon, bpaf, napi, tower-lsp-server; npm CLI package ships a prebuilt native binary with no user-facing JS deps · Rust 1.96.0 (workspace MSRV, N-2 policy), edition 2024; no Rust toolchain needed to use the prebuilt npm binary · Linux (glibc/musl; x86-64, arm/aarch64, riscv64, powerpc64le), macOS (x86-64, arm64), Windows (x86-64, i686, arm64), plus wasm and OpenHarmony targets per the npm package's optionalDependencies

**Vs siblings:** Over Biome specifically: the same VS Code benchmark run by the Oxc project shows Oxlint 2.5-3.3x faster (though that test used only the no-debugger rule, so treat it as a floor, not a full-ruleset comparison). The other catalogued siblings (Ruff, Pyrefly, ty, clangd-tidy) target Python or C++, so within JS/TS linting Oxlint is the only ESLint-throughput entry here besides Biome.

**Gotchas:**
- Legacy ESLint v8 configs must be converted to flat config first (via @eslint/migrate-config) before the @oxlint/migrate tool works
- Local/custom ESLint plugins don't migrate automatically and need manual setup
- Type-aware rules require the separate oxlint-tsgolint binary, which depends on TypeScript 7
- The published Oxlint-vs-Biome benchmark enables only a single rule (no-debugger) on both linters, so the ~2x figure isn't representative of full rule-set performance

**Status:** Actively maintained (commits as recent as today, 22.9k stars across the oxc monorepo) with VoidZero backing; MIT licensed and directly usable via `npx oxlint`, though ESLint rule/plugin parity is still incomplete.

[repo](https://github.com/oxc-project/oxc) · [benchmark](https://github.com/oxc-project/bench-linter)

##### Pyrefly  `Rust`  `MIT`  `active`  `Tier A`

Rust type checker and LSP for Python; faster than mypy and Pyright on cold, whole-project checks.

**Beats:** mypy; Pyright — Astral's ty_benchmark harness (public, pinned revisions) ran a cold CLI type-check of home-assistant/core with no cache on an Apple M4: Pyrefly 5.32s vs Pyright 19.62s (~3.7x faster) vs mypy 45.66s (~8.6x faster). The same post's LSP incremental-recheck test on PyTorch showed Pyrefly was the slowest of the three, ~2.4-2.6s vs Pyright's ~370-386ms and ty's ~4.5-4.7ms; no compiler flags are relevant since these are prebuilt/uv-installed binaries, hardware is stated only as 'M4'.

**How:** The whole tool is a single Rust binary; type-checking is parallelized across modules with rayon, backed by concurrent data structures (dashmap, parking_lot) and jemalloc/mimalloc allocators. Per its own ARCHITECTURE.md, it deliberately favors module-level incrementality over fine-grained, binding-level incrementality (the Salsa/rust-analyzer or Roslyn/TypeScript approach): each module's bindings are solved sequentially and completely, betting that whole-module solving is fast enough that finer-grained caching isn't needed. That design gives fast cold/batch checks but is the likely reason its LSP incremental recheck lagged both Pyright and ty in Astral's benchmark.

**Use it when:**
- Cold or CI type-checks of large, multi-module Python codebases (millions of LOC) where batch throughput matters more than incremental recheck latency
- Migrating an existing mypy or Pyright project and wanting built-in tooling (`pyrefly init`, `pyrefly suppress`) to stage the rollout
- Codebases heavy on Pydantic, Django, or pytest patterns, where Pyrefly's built-in framework modeling reduces false positives
- Wanting one tool that is both the CLI checker and the editor LSP with consistent results (VS Code, Neovim, Zed)
- Multi-core CI machines, since checking parallelizes across modules with rayon

**Skip it when:**
- Editor-driven inner loop where every-keystroke/save recheck latency matters most: Astral's benchmark measured Pyrefly's incremental LSP recheck on PyTorch at ~2.4-2.6s, versus ~370ms for Pyright and ~4.5ms for ty
- Memory-constrained dev machines: multiple open issues report very high RSS, including one reporting the VS Code extension reaching up to 100GB on a large repo
- Older Linux hosts on glibc 2.17, where a memory-allocation crash has been reported
- Teams that need strict semver stability: Pyrefly's own version policy states monthly minor releases can introduce new type errors or other breaking changes
- Relying on the README's PyTorch '15x faster than mypy/Pyright' headline for capacity planning — no hardware or methodology is published for it

**Integration:** crate · none to run (pip install pyrefly ships a prebuilt Rust binary); building from source pulls a Rust workspace (rayon, dashmap, parking_lot, lsp-server, ruff_python_parser/ruff_notebook, tokio, etc.) · Rust stable, edition 2024 (Rust 1.85+) to build from source; rust-toolchain.toml pins channel=stable with no exact version · Linux x86_64/i686/aarch64 (glibc and musl), macOS x86_64/arm64, Windows x86_64/i686/aarch64 — all built as prebuilt release binaries

**Vs siblings:** Pick Pyrefly over ty (astral-sh/ty) when you value production-scale proof (Instagram's 20M-LOC codebase, PyTorch, JAX adoption) and built-in Pydantic/Django/pytest modeling over raw speed — in the same benchmark ty beat Pyrefly on both cold checks (2.19s vs 5.32s) and, by a wide margin, incremental LSP rechecks (4.5ms vs 2.6s).

**Gotchas:**
- README claims IDE rechecks 'typically complete in under 10 milliseconds,' but Astral's independent benchmark measured 2.4-2.6s for Pyrefly's LSP recheck on PyTorch — a large, credible gap
- Multiple open GitHub issues report excessive memory use, including one titled 'Pyrefly consumes A LOT of memory' and another reporting the VS Code extension using up to 100GB
- Reported crash allocating memory on glibc 2.17 (older Linux distros)
- Does not follow strict semver: any minor version bump (monthly) may add new type errors or change behavior; `pyrefly suppress` exists specifically to manage that churn

**Status:** Actively maintained — commits as of today (2026-09-24), monthly minor releases, 1.0 tagged as stable; MIT-licensed and installable as a prebuilt binary via pip, so adoption cost is low despite the non-semver upgrade churn.

[repo](https://github.com/facebook/pyrefly) · [benchmark](https://astral.sh/blog/ty)

##### ty  `Rust`  `MIT`  `active`  `Tier A`

Rust-based Python type checker and language server from Astral; 10-100x faster cold checks than mypy and Pyright.

**Beats:** mypy; Pyright — Astral's own blog (astral.sh/blog/ty, dated 2025-12-16) reports, on an Apple M4: cold no-cache CLI type-check of home-assistant/core at ty 2.19s vs Pyrefly 5.32s vs Pyright 19.62s vs mypy 45.66s (~9x over Pyright, ~21x over mypy), and LSP incremental re-check after editing a file in pytorch/pytorch at ty 4.5ms vs Pyright 370.5ms vs Pyrefly 2.60s (~82x over Pyright, ~578x over Pyrefly; prose cites slightly different 4.7ms/386ms/2.38s). No tool versions or exact M4 variant/RAM are stated on the page; the harness (astral-sh/ruff scripts/ty_benchmark) is public with pinned lockfiles. The repo's own BENCHMARKS.md, run separately on an Apple M3 Max (128GB) with pinned versions (ty 0.0.55, Pyright 1.1.410, mypy 2.1.0, Pyrefly 1.1.1), corroborates the same ranking on other projects (e.g. Black: ty 69.5ms vs Pyrefly 128.3ms vs mypy 1.316s vs Pyright 1.420s) though with different magnitudes than the blog.

**How:** Written in Rust and built on the `salsa` incremental-computation framework (the same query/memoization engine used by rust-analyzer), giving fine-grained incremental re-analysis so editing one file only recomputes affected queries instead of re-checking the project. It parallelizes work with `rayon`, and on Linux/other non-macOS/Windows targets swaps in `tikv-jemallocator` for allocation-heavy workloads. Cold/no-cache runs are fast because the whole pipeline (parsing, semantic indexing, inference) is Rust-native rather than Python, unlike mypy.

**Use it when:**
- Large monorepos where cold, no-cache CLI type-check latency matters (CI, pre-commit)
- IDE/language-server usage where sub-second incremental re-check after each keystroke/save matters
- Projects already on the Astral toolchain (uv, Ruff) wanting one vendor for lint/format/type-check
- Teams willing to tolerate a beta, fast-moving type checker in exchange for speed
- Python 3.10+ targeted codebases (earlier versions type-check with more false positives/negatives)

**Skip it when:**
- Projects needing a stable, versioned API/behavior contract — ty is 0.0.x with no stable-API guarantee and diagnostics can change between any two releases
- Codebases relying on mypy/pyright-specific strict-mode flags or plugins with no ty equivalent yet (see docs/coming-from-mypy-or-pyright.md rule-mapping gaps)
- Code with very complex/deeply nested expressions where bidirectional type inference has known 'dismal performance' and regression reports (astral-sh/ty#3180, #3505)
- Warm/cached CLI re-check comparisons — the headline benchmark is a no-cache scenario; only mypy supports warm cached re-checks in that comparison, so it doesn't show ty's cache-hit CLI behavior
- Teams that need mature third-party plugin ecosystems (e.g. mypy plugins) that ty doesn't support

**Integration:** source-drop (prebuilt standalone binary / PyPI wheel built via maturin from a Rust binary crate in the astral-sh/ruff monorepo) · none (Python package pyproject.toml declares zero deps; the Rust binary statically bundles its own dependencies) · none required to use it (install via uvx/pipx/pip/standalone installer/Docker); building from source requires Rust 1.96+ per astral-sh/ruff's workspace Cargo.toml · macOS, Linux, Windows (prebuilt binaries via GitHub Releases, PyPI wheels, standalone installer script, Docker image ghcr.io/astral-sh/ty)

**Vs siblings:** Versus Pyrefly (the only true sibling here — same baseline of mypy/Pyright): pick ty when incremental LSP re-check latency matters most (Astral's benchmark shows ty beating Pyrefly by ~500x on that metric) and you want a public, pinned, reproducible benchmark harness rather than Pyrefly's README claim with no stated methodology; pick Pyrefly if you need functionality ty doesn't yet have. Biome/Oxlint/clangd-tidy/Ruff aren't real alternatives here — different languages or different tool category (linting/formatting, not type checking).

**Gotchas:**
- 0.0.x versioning: no stable API yet, diagnostics/behavior can change between any two releases (README 'Version policy')
- Default checking mode is stricter than mypy/pyright defaults in several ways (e.g. always checks unannotated function bodies) with no flag to relax it, which can surface new errors when migrating
- Complex/deeply nested expressions can trigger severe slowdowns from bidirectional type inference cost (open issues: 'Dismal performance when some complex expressions exist', a sympy performance regression)
- The astral-sh/ty GitHub repo is mostly packaging/docs; the actual Rust type-checker source lives in the astral-sh/ruff repo's crates/ty* via a git submodule

**Status:** Actively developed beta from Astral (same team as Ruff/uv), with commits as recent as today; MIT licensed and usable now via uvx/pipx/pip, but the 0.0.x version policy means no stable API and diagnostics can change release to release.

[repo](https://github.com/astral-sh/ty) · [benchmark](https://astral.sh/blog/ty)

#### linkers

##### mold  `Rust`  `MIT`  `active`  `Tier A`

Drop-in ELF linker beating LLVM lld and GNU ld via pervasive data-parallelism across the whole link pipeline.

**Beats:** lld — On 9 real-world programs (Blender, Chromium, Clang, ClickHouse, Firefox, Godot, LibreOffice, PyTorch, TensorFlow, some ARM64 variants) linked in both debug and release configurations, mold beat LLVM lld by 4.9x at the median (per-program range ~1.5x-16.1x) and wild by 1.9x at the median. All three linkers were built from source in release mode as of 2026-08-28 with default options; measurements are wall-clock, median of 3 runs after a warm-up, on an AMD Ryzen Threadripper 7980X/Ubuntu 24.04 and an Apple M1 Ultra/Fedora Asahi Remix 42.

**How:** Per the ASPLOS 2027 paper ('mold: A Massively Parallel Linker'), mold decouples the traditionally entangled passes of Unix linking — symbol resolution, archive-member pulling, relocation, output layout — so each stage is split across a rayon-based work-stealing thread pool (capped at 32 threads by default) instead of running mostly single-threaded like lld/gold. Section-merging deduplication uses a custom lock-free, open-addressing concurrent hash map (CAS-claimed buckets, per-shard probing) whose table size is pre-estimated with HyperLogLog cardinality counting rather than grown/resized on the fly. The paper's ablation study found no single optimization dominates — the speedup is cumulative across nearly every pass being parallelized.

**Use it when:**
- Large C/C++/Rust ELF builds on Linux/Unix where the link step dominates the debug-edit-rebuild loop — mold shows 4x-16x over lld on multi-GB debug binaries (per-program table in README).
- Many-core workstations or CI runners (Threadripper-class) where lld/gold leave most cores idle during linking.
- Toolchains that already select a linker via `-fuse-ld=`/`-B` (Clang, GCC 12.1+, Rust via `.cargo/config.toml`) — swapping in mold is a one-line config change.
- Any of the 16 listed non-Windows/non-macOS ELF targets, including cross-linking ARM64 output from an x86 host.
- Teams that want bit-for-bit deterministic link output with no host-specific default paths baked in.

**Skip it when:**
- Native Windows/MSVC or macOS/Mach-O link jobs: the mold.exe binary builds and runs on Windows, but per the maintainer (issue #1658) it 'can only be used to link ELF binaries' — no PE/COFF or Mach-O support, and macOS support was explicitly ruled out (issue #1052 thread).
- Projects relying on non-trivial linker-script features (custom SECTIONS/memory layouts, embedded/microcontroller link maps) — mold supports only the minimal subset needed to parse glibc's loader script and has stated no plan to add more (open issue #243, 'SECTIONS doesn't seem to be implemented').
- Workloads needing incremental or partial linking (gold-style `--incremental`, or `-r` combined with LTO) — not supported; every invocation is a full relink.
- Small link jobs on few-core machines: on the M1 Ultra debug table mold actually regressed vs. lld for Clang (0.9x) — the parallel design needs enough cores/input size to pay for itself.
- If you need long field-history on the exact codebase in production: the linker rewrote from C++ to Rust just before this snapshot (Sept 2026, issue #1655), so 'production since 2021' applies to the predecessor C++ implementation, not the current Rust one.

**Integration:** crate (Cargo workspace building a CLI binary `mold` + companion shared object `mold-wrapper.so`; not a library you link against) · Rust crates: rayon, hashbrown, memmap2, blake3, xxhash-rust, crc32fast, zstd, flate2, libz-sys, cpp_demangle, rustc-demangle, bstr, memchr, getrandom, libc. Build also needs a C compiler (GCC/Clang) and Git. · Rust stable toolchain (Cargo.toml workspace edition 2024, i.e. rustc 1.85+); rust-toolchain.toml pins channel "stable". · Linux/Unix ELF targets: x86-64, i386, ARM32/64 (+BE), RISC-V32/64 (+BE), PowerPC32/64 (v1/v2), s390x, LoongArch32/64, SPARC64, m68k, SH-4. Also builds on Windows (CI job build-windows.ps1 produces mold.exe) but, per the maintainer, can then only link ELF output, not PE/COFF.

**Vs siblings:** Pick mold over wild when you need broader architecture coverage (16 ISAs vs. wild's more limited set) or maximum throughput on many-core Linux boxes: mold is ~1.9x faster than wild at the median, and wild is marked N/A (can't link at all) on several rows in mold's own table, including Chromium release builds because it lacks --icf=all. mold and zld don't really compete — zld targets Apple's ld64/Mach-O toolchain exclusively, so on macOS zld is the only option of the two; mold has explicitly ruled out macOS support.

**Gotchas:**
- --start-group/--end-group are accepted for compatibility but silently ignored — mold (like lld) tracks archive symbols globally so link order doesn't matter, which can surprise anyone relying on that flag's traditional semantics.
- No incremental or partial (-r + LTO) linking; every run is a full relink.
- Only a minimal linker-script subset is supported (just enough to read glibc's ASCII libc.so loader script); no plans to extend it.
- Windows builds of the CLI exist but only link ELF, not PE/COFF — don't expect an MSVC linker replacement.

**Status:** Actively maintained (last commit 2026-09-23; 140+ contributors; CI test-builds ~19,000 Gentoo packages against GNU ld as a control before each release); MIT-licensed with prebuilt binaries via most distro package managers and GitHub releases, though the linker core is a very recent (Sept 2026) full rewrite from C++ to Rust.

[repo](https://github.com/rui314/mold) · [benchmark](https://github.com/rui314/mold#benchmark)

##### Wild (wild-linker)  `Rust`  `Apache-2.0 OR MIT`  `active`  `Tier A`

Rust linker for Linux that beats LLVM lld on debug-build link time via mmap'd input and rayon-parallelized phases.

**Beats:** lld — Verified against mold's own August 2026 README benchmark table (all three linkers built from source in release mode as of 2026-08-28, wall-clock median of 3 runs after warm-up, on a Threadripper 7980X/Ubuntu 24.04 and an M1 Ultra/Fedora Asahi 42): wild beat lld on all 28 rows where it could link (per-row ratios 1.38x-4.18x, median ~2.1x, e.g. Chromium debug 16.64s to 3.98s), while mold beat wild on those same rows by ~1.9x at the median.

**How:** Wild mmaps input files instead of read()-ing them, deduplicates merge-string sections up front, and resolves symbols through a hashmap before touching relocations — the same input-handling strategy mold uses. Its phases (symbol_db, resolution, layout, elf_writer) run on a rayon-owned thread pool, using par_iter/par_bridge to parallelize the relocation-graph traversal and the copy/relocate step in the ELF writer, with only a few phases left single-threaded. It isn't algorithmically different from mold — both are mmap-plus-parallel-ELF-writer designs — it is simply slower in practice today (mold's README puts wild ~1.9x behind mold at the median on the same benchmark).

**Use it when:**
- Iterative Linux debug builds (Rust/Cargo, or C/C++ via Clang or GCC 16.1+/CMake 4.4+) where lld's link time is the edit-compile-link bottleneck, for a program wild can link (Blender, Clang, ClickHouse, Godot, LibreOffice, PyTorch, Chromium debug all measured 1.4x-4.2x faster than lld).
- Projects already invoking lld via -fuse-ld=lld/--ld-path=lld — swapping to wild is a flag-value change, no build-system rework.
- x86-64, ARM64, riscv64gc, PPC64LE, or LoongArch64 Linux targets, especially with Clang or GCC 16.1+ / CMake 4.4+ for first-class integration.
- Teams that want an actively developed, Rust-native alternative to mold specifically because mold's author has ruled out incremental linking.
- Experimental wasm32-wasip1/wasm32-unknown-unknown linking, if you're comfortable with a feature flagged as experimental (--features wasm).

**Skip it when:**
- Release builds needing --icf=all (identical code folding) — wild doesn't implement it, so it is N/A on the mold benchmark's Chromium-release rows rather than just losing some size savings.
- Programs wild can't link at all yet: TensorFlow 2.21, Firefox debug builds, and ARM64 Chromium/Firefox are N/A for wild in the mold benchmark suite.
- Any Mach-O (Apple) or Windows target, or non-Linux host — unsupported.
- Builds depending on fuller linker-script features (SEARCH_DIR, STARTUP, TARGET, INSERT, NOCROSSREFS, REGION_ALIAS, MEMORY '>region' placement, PHDRS AT attribute) — only partially implemented per LINKER_SCRIPT_SUPPORT.md.
- When mold is an option and Rust-native tooling isn't a requirement: mold links the same benchmark suite ~1.9x faster than wild at the median and covers more architectures (adds i386, PowerPC, s390x, LoongArch32, SPARC64, m68k, SH-4).

**Integration:** crate (cargo-installed binary) — invoked as your linker executable, not linked into your program · none to vendor as a unit; Rust workspace of 7 crates pulling ~40 crates.io deps, notably rayon (thread pool), hashbrown/foldhash (symbol hashmap), gimli (DWARF), iced-x86, blake3, zlib-rs, clap · Rust 1.97.1 (workspace rust-version), edition 2024, to build wild itself; to use it as your linker you need Clang or GCC 16.1+ for -fuse-ld=wild, or CMake 4.4+ for CMAKE_LINKER_TYPE=WILD · Linux only — x86-64, ARM64, RISC-V (riscv64gc), LoongArch64 and PPC64LE (both 'initial support'); WebAssembly output experimental behind --features wasm; no Mach-O, no Windows

**Vs siblings:** Pick wild over lld whenever your debug-link target is in its supported set — it's 1.4x-4.2x faster with an identical invocation. Pick mold instead of wild when you just want the fastest available Linux linker today (mold beats wild by ~1.9x at the median on the same benchmark) and don't specifically need Rust-native tooling or wild's incremental-linking roadmap; zld isn't a real alternative here since it only targets Apple's ld64, not ELF.

**Gotchas:**
- GCC before 16.1 rejects -fuse-ld=wild outright; use the ld.wild symlink plus -B/tmp workaround documented in the README.
- Archive entry load order and symbol-resolution priority don't yet fully match GNU ld/LLD semantics (open issue #600), which can change which duplicate symbol wins in ambiguous builds.
- wild's Chromium-release 'N/A' in the mold benchmark is a deliberate limitation (no --icf=all), not a crash — don't assume every N/A row is a bug.
- The repo was transferred from davidlattimore/wild to the wild-linker org; the old URL redirects, but pin CI/install scripts to the new path.

**Status:** Actively maintained (3,998 stars, commits the same day as this record, not archived or a fork) and permissively dual-licensed (Apache-2.0 OR MIT confirmed in-repo, though GitHub's UI reports only Apache-2.0); still pre-1.0 (v0.10.0) with incremental linking — the project's actual reason for existing — not yet built.

[repo](https://github.com/wild-linker/wild) · [benchmark](https://github.com/rui314/mold#benchmark)

#### preprocessors-and-codegen

##### asp (algebraic, staged parsing)  `OCaml`  `MIT`  `stale`  `Tier B`

Staged, typed OCaml parser combinators (MetaOCaml) that beat ocamlyacc/ocamllex throughput on 4 of 5 grammars.

**Beats:** ocamlyacc/ocamllex — Verified directly in the PLDI'19 paper (Figure 8, Section 7): staged asp combinators, compiled with BER MetaOCaml N107 and run on an AMD FX 8320/16GB Debian machine via Core_bench (95% CIs), beat ocamlyacc/ocamllex throughput on 4 of 5 benchmarks (arith 14.31 vs 10.96 MB/s, pgn 33.26 vs 21.29, ppm 11.83 vs 6.75 — the paper states 75% for PPM, sexp 43.65 vs 28.6) but lose on json, 60.32 vs 80.42 MB/s (~25% slower). Exact ocamlopt/compiler flags used for the benchmark build are not stated in the paper.

**How:** Combinators build a first-order GADT-typed grammar representation that is type-checked for unambiguity and absence of left-recursion, which guarantees linear-time, single-token-lookahead, backtrack-free parsing. Multi-stage programming (BER MetaOCaml brackets/escapes) then specializes the generic combinator interpreter into a flat, mutually-recursive first-order program per grammar, using CPS-based binding-time improvements, 'the Trick', and type-directed branch pruning (FIRST/NULL sets) to eliminate the combinator-dispatch and redundant-peek overhead present in the unstaged version.

**Use it when:**
- Grammar is unambiguous, non-left-recursive, and parseable with one token of lookahead (arith expressions, PGN, S-expressions measured 31-75% faster than ocamlyacc/ocamllex)
- Throughput on MB/s-scale character streams matters more than avoiding a new toolchain
- Willing to adopt BER MetaOCaml and write parsers as staged combinator code instead of .mly/.mll grammar files
- Want static rejection of ambiguous or left-recursive grammars at type-check time rather than at ocamlyacc build time
- Research/prototype context where vendoring a small, peer-reviewed artifact (PLDI'19 Distinguished Artifact Award) is acceptable

**Skip it when:**
- String/JSON-heavy grammars: staged asp measured ~25% slower than ocamlyacc on JSON (60.32 vs 80.42 MB/s) due to per-character string handling overhead
- Can't add BER MetaOCaml to the build; it is a distinct OCaml variant/toolchain, not stock OCaml plus opam
- Need an actively maintained library: last commit 2025-05-16, and the repo has received only toolchain-compatibility updates since 2019
- Need the unstaged/plain-combinator form for simplicity: it is 4.5-125x slower than ocamlyacc (as low as <1% of ocamlyacc's JSON throughput), so only the staged path is usable in production
- Need backtracking or ambiguous-grammar support: the type system deliberately forbids ambiguous and left-recursive grammars

**Integration:** module · letrec (metaocaml-letrec); the BER MetaOCaml compiler itself · BER MetaOCaml (paper benchmarks used N107; current opam/README target the 4.11.1+BER switch; closed issues show added support for N111 and N153); not plain OCaml · not documented beyond the paper's test machine (AMD FX 8320, Debian Linux); no explicit platform restriction in source

**Vs siblings:** The sibling entries (RapidProto, Zserio, FlatBuffers, vtprotobuf) all beat protoc on serialization codegen, a different problem from asp's parser-combinator-vs-ocamlyacc/ocamllex target, so none is a substitute. Pick asp only when the real baseline is ocamlyacc/ocamllex, the grammar is unambiguous/LL(1), and BER MetaOCaml is acceptable in the build.

**Gotchas:**
- type_check rejects ambiguous or left-recursive grammars outright with no backtracking fallback, so some grammars simply cannot be expressed
- Parser(S).compile returns a MetaOCaml `code` value, not a ready function; it must be run through MetaOCaml staging/execution, an extra step versus ocamlyacc's directly generated .ml
- the Unstaged module (same combinators, no staging) is 4.5-125x slower than ocamlyacc per the paper, so don't use it expecting usable performance
- string-heavy tokens (e.g. JSON) go through per-char list conversion, which the paper identifies as the specific cause of the JSON slowdown; still unfixed as of the last commit

**Status:** Stale: last commit 2025-05-16 was toolchain-compatibility only, and all 6 closed issues concern supporting newer BER MetaOCaml releases, not fixes or features. MIT-licensed and small enough to vendor, with a Docker-based PLDI artifact, but depends on the niche BER MetaOCaml toolchain rather than stock OCaml.

[repo](https://github.com/yallop/ocaml-asp) · [benchmark](https://www.cl.cam.ac.uk/~jdy22/papers/a-typed-algebraic-approach-to-parsing.pdf)

## Permissive — Unverified claims (tier C/D)

### serialization-and-formats

#### json

##### glaze  `C++`  `MIT`  `active`  `Tier C`

Header-only, C++23 reflection-based JSON (plus BEVE/CBOR/MessagePack/TOML/YAML/CSV) library; beats RapidJSON in first-party benchmarks.

**Beats:** RapidJSON — On a single-core MacBook Pro M1 with Clang 17 (optimization flags not specified in the benchmark harness), Glaze round-trips a nested JSON test struct 1,000,000 times in 1.01s (1396 MB/s write / 1200 MB/s read) versus RapidJSON's 3.76s (289 MB/s write / 416 MB/s read) — roughly 3.7x roundtrip, 4.8x write, 2.9x read — per the author-run json_performance benchmark (results dated June 8, 2025), which also appears verbatim in the Glaze README's Performance table.

**How:** Uses C++23 compile-time reflection (or C++26 P2996 on GCC 16+/Bloomberg clang-p2996) to generate per-struct parse/serialize code at compile time instead of runtime introspection or macro-generated boilerplate, writing directly into destination objects rather than an intermediate DOM. Adds compile-time perfect-hash maps for key lookup and runtime SIMD dispatch (SSE2 through AVX-512BW on x86-64, NEON on ARM, SIMD128 on Wasm, auto-selected from compiler target macros) for UTF-8 validation, string escaping, and structural whitespace skipping.

**Use it when:**
- Reading/writing C++ structs known at compile time to/from JSON without hand-written (de)serialization code or macros.
- Need one struct definition to serialize to multiple formats (JSON, BEVE, CBOR, MessagePack, TOML, YAML, CSV).
- Input JSON keys can be missing or out of declared order — Glaze doesn't fall back to re-scanning the way simdjson On-Demand does (1219 MB/s vs simdjson's 89 MB/s in the author's out-of-order-keys test).
- Embedded/constrained builds that want no exceptions and no RTTI (-fno-exceptions/-fno-rtti).
- Team can adopt a C++23 toolchain (Clang 17+, GCC 13+, MSVC 2022+ with /Zc:preprocessor).

**Skip it when:**
- Stuck on C++17/C++20 — Glaze requires C++23, a higher bar than RapidJSON or nlohmann (C++11+).
- Need a DOM/Value-tree API for dynamic, schema-less JSON manipulation rather than struct binding.
- Non-aggregate classes (custom constructors, virtual functions, private members) without opting into C++26 P2996 reflection, which needs GCC 16+ or a Bloomberg clang fork — not mainstream compilers.
- Care about independently verified numbers: the entire published performance table is first-party (author-designed workload, author-run), evidence tier C, with no stated optimization flags in the benchmark harness's CMakeLists.txt.
- Endianness matters for your target: installation.md states little-endian only, while the README's Compiler/System Support section claims big-endian is supported and CI-tested via QEMU on s390x — the two docs disagree, so verify directly for your platform.

**Integration:** header-only · none for core JSON/binary formats (self-contained, SIMD paths built in); optional networking module (HTTP/WebSocket) pulls in Asio · C++23; Clang 17+ (18+ in CI), GCC 13+, MSVC 2022+ (requires /Zc:preprocessor) · x86-64 (SSE2 through AVX-512BW auto-detected), aarch64 (NEON), WebAssembly (SIMD128); 64-bit and 32-bit; endianness support is disputed between docs (see gotchas)

**Vs siblings:** Pick Glaze over simdjson when JSON keys can arrive missing or out of declared order — simdjson's On-Demand API degrades sharply there (89 MB/s vs Glaze's 1219 MB/s in the author's ABC test) — or when you want one API spanning JSON, BEVE, CBOR, MessagePack, TOML, YAML, and CSV from the same struct. Pick yyjson instead if the codebase is C (not C++23) or you need a DOM-style API rather than compile-time struct binding.

**Gotchas:**
- docs/installation.md says little-endian systems only; the README's Compiler/System Support section says big-endian is supported and tested via QEMU on s390x — conflicting docs, confirm for your target before relying on either.
- No exceptions/RTTI by default (-fno-exceptions/-fno-rtti); errors come back as glz::error_code, not exceptions, unless you opt into the separate throwing helper API.
- C++26 P2996 reflection (non-aggregate types, unlimited struct members, private member access, automatic enum serialization) needs GCC 16+ or Bloomberg's clang-p2996 fork — not available on the mainstream GCC 13+/Clang 17+ builds most users have.
- MSVC builds need the /Zc:preprocessor flag; without it the standard-conformant preprocessing Glaze's reflection relies on breaks.

**Status:** Actively maintained (last commit 2026-09-24, ~3k stars, no open bug-labeled issues found in a repo search); MIT-licensed and header-only so trivially vendorable, but the C++23 requirement (Clang 17+/GCC 13+/MSVC 2022+) is a real adoption bar versus older-standard baselines like RapidJSON.

[repo](https://github.com/stephenberry/glaze) · [benchmark](https://github.com/stephenberry/json_performance)

### stdlib-replacements

#### allocators

##### gperftools TCMalloc  `C++`  `BSD-3-Clause`  `active`  `Tier C`

Thread-caching malloc replacement for glibc's ptmalloc2; per-thread free lists cut lock contention and per-call cost.

**Beats:** glibc 2.3 malloc (ptmalloc2) — The first-party ~2005 design doc claims ptmalloc2 (glibc 2.3) took ~300ns per small malloc/free pair versus ~50ns for TCMalloc, both measured on a single 2.8 GHz 32-bit Pentium 4, with no compiler, flags, or benchmark harness given. A Dec 2024 maintainer's note in the same document calls those exact numbers obsolete while still asserting gperftools remains somewhat faster than modern glibc.

**How:** Gives each thread a lock-free thread-local cache of free lists spanning ~88 size-classes for objects <=256KB; medium/large objects go through a central page heap and a best-fit red-black tree instead. The allocation/deallocation fast path only touches the thread-local free list, so it takes no locks at all in the common case. A slow-start algorithm resizes each per-thread free list to balance central-list traffic against idle memory, and a build-time --with-tcmalloc-pagesize option trades memory for fewer page-heap operations.

**Use it when:**
- Multi-threaded C++ services with frequent small (<=256KB) alloc/free churn where ptmalloc2 lock contention or per-thread-arena memory stranding is a measured problem
- You want the bundled pprof-compatible heap/CPU profiler alongside the allocator, not just a faster malloc
- Linux/x86, aarch64, or riscv targets with native TLS, where gperftools documents its fast path as fully optimized
- Retrofitting an existing binary via LD_PRELOAD without rebuilding
- Workloads that hand large blocks of memory off between phases or threads, where ptmalloc2's per-thread arenas can't reclaim it

**Skip it when:**
- You need a modern, reproducible speed number vs glibc: the ~6x claim is a 2005-era 32-bit P4 measurement, and the maintainer's Dec 2024 note says glibc has since closed much of that gap
- Your code loads the allocator via dlopen(): TCMalloc's initial-exec TLS model breaks under dlopen (documented in INSTALL)
- Heavy fork() + multithreading without an immediate exec(): internal locks aren't fully wrapped in pthread_atfork (open issue #1425), so children can hang or profiling data can corrupt on exit()
- musl libc targets where you need profiling: backtracing/profiling has repeated musl-specific breakage (issues #1282, #1602, #693); plain malloc is more reliable there
- Windows or heap-profiling on non-Linux platforms: Windows support is tcmalloc_minimal only (no heap/CPU profiler), and CMake build support is explicitly called 'preliminary'

**Integration:** shared lib (static lib also supported) · none for tcmalloc_minimal; full tcmalloc/profiler builds use libunwind (default on most platforms) or built-in backtrace (s390, macOS) for stack unwinding · C++17 (AX_CXX_COMPILE_STDCXX 17 mandatory in configure.ac); autotools (primary, fully supported) or CMake 3.12+ (preliminary); MSVC 2019+ or MinGW for Windows · x86, aarch64, riscv Linux (primary, fully tested); FreeBSD, NetBSD, macOS (aarch64), Solaris x86, QNX, AIX (partial, per INSTALL); Windows via MSVC 2019+/MinGW limited to tcmalloc_minimal

**Vs siblings:** Pick gperftools when you also want its bundled pprof-compatible CPU/heap profiler and are specifically displacing glibc's ptmalloc2 on Linux with a mature, widely-packaged allocator. For a pure allocator-speed decision today, snmalloc and mimalloc publish newer benchmarks claiming wins over tcmalloc itself, so prefer those siblings' Tier B/A evidence over tcmalloc's 2005-era numbers when raw throughput is the deciding factor.

**Gotchas:**
- Loading via dlopen() breaks tcmalloc's TLS assumptions; it must be linked at startup or LD_PRELOADed, not dlopen'd (INSTALL)
- CPU profiling doesn't work correctly across fork() unless the child immediately exec()s; if the child calls exit() instead of _exit(), profile data can be corrupted (README)
- --with-tcmalloc-pagesize and CXXFLAGS=-DTCMALLOC_SMALL_BUT_SLOW are build-time, not runtime, speed/memory tradeoffs (INSTALL)
- musl libc builds have a history of breakage in backtracing/profiling code across multiple issues; core malloc is more reliable there than the profilers

**Status:** Actively maintained (last commit 2026-09-05, 8,976 stars, not archived), BSD-3-Clause and small enough to vendor or package; historically used in Chrome/Chromium and widely distributed as libtcmalloc across Linux distros.

[repo](https://github.com/gperftools/gperftools) · [benchmark](https://github.com/gperftools/gperftools/blob/master/docs/tcmalloc.adoc)

##### jemalloc  `C`  `BSD-2-Clause`  `active`  `Tier C`

General-purpose malloc(3) with per-thread arenas and decay-based purging; beats FreeBSD's phkmalloc under concurrency.

**Beats:** phkmalloc (FreeBSD libc malloc, the incumbent jemalloc replaced) — Evans' 2006 BSDCan paper (first-party, not peer-reviewed, no compiler/flags given, on a 4-CPU dual-dual AMD Opteron 275 / FreeBSD-CURRENT box) shows jemalloc beating FreeBSD's phkmalloc by roughly 1.1x-1.55x mean run time across five single-threaded programs (cca, gs, sh6bench, smlng, cfrac), and by roughly two orders of magnitude or more in throughput on a 20-thread malloc-test microbenchmark, where phkmalloc collapses below 1e5 allocs/sec by 10 threads while jemalloc plateaus near 3e7.

**How:** Splits the heap into multiple independent arenas (selected per-CPU or per-thread) so unrelated threads rarely contend on the same lock, backed by per-thread caches (tcache) that serve small size-class allocations without touching an arena at all. Size-class segregation limits fragmentation, and unused pages are reclaimed via time-based decay (dirty_decay_ms/muzzy_decay_ms) instead of immediate unmap, trading a little steady-state memory for fewer syscalls. The 5.4.0 release (Sep 2026) adds an HPA (huge-page-aware) extent allocator and demand-adaptive tcache refill/flush, replacing the older fixed-size tcache tuning knobs.

**Use it when:**
- Multi-threaded servers/daemons with heavy concurrent alloc/dealloc (its own paper's use case: Redis-, MySQL-style workloads) where a single global heap lock serializes threads
- Long-running processes where fragmentation avoidance over time matters more than the fastest possible single-thread malloc/free pair
- You want built-in heap profiling/leak detection (--enable-prof, jeprof) instead of bolting on a separate tool
- Target platform is Linux, FreeBSD, macOS, illumos, or Windows (all have dedicated CI workflows in the repo) and you're willing to link or LD_PRELOAD it
- You're prepared to tune arena count / decay times / percpu_arena for your workload rather than accept the generic defaults

**Skip it when:**
- Single-threaded or low-concurrency programs, where multiple arenas can raise peak RSS without a throughput win (per the record's tradeoffs note)
- Short-lived CLI tools where allocator warm-up and tuning overhead isn't worth it
- You need documented, current jemalloc-vs-glibc numbers: README/TUNING.md carry no benchmarks, and the only numeric evidence in the repo's history is a 2006 phkmalloc/dlmalloc comparison
- You want a simple mental model: open issues (#2688, #2751, #2808) show users struggling to reason about dirty/muzzy decay and HPA purging behavior in production
- You're pinning a malloc_conf tuning string from before 5.4.0 — that release silently drops seven legacy tcache mallctls (lg_tcache_nslots_mul and friends), so an old config may stop tuning anything without an error

**Integration:** source-drop, built via autoconf into a static or shared lib · none to build from a release tarball; autoconf is required only when building from a git/dev checkout (autogen.sh) · not documented — README/INSTALL.md give no minimum C standard or compiler version, only that autoconf is needed · Linux, FreeBSD, macOS, illumos, Windows (per .github/workflows: linux-ci, freebsd-ci, illumos-ci, macos-ci, windows-ci); specific CPU architectures are not enumerated in the README

**Vs siblings:** Pick jemalloc over mimalloc/snmalloc/TCMalloc when you need its mature jeprof heap-profiling and fine-grained arena/decay tuning knobs, or you're already on a codebase built around it (Redis, FreeBSD libc); the sibling entries' own numbers (mimalloc >2.5x faster than jemalloc on sh6bench, snmalloc ~4x glibc at 64 threads) suggest mimalloc or snmalloc are more likely to win a raw throughput shootout today.

**Gotchas:**
- Decay-based purging is a frequent confusion point: open issues report dirty_decay_ms 'not taking effect' (#2688) and ask for clearer docs on decay/purging (#2751), so memory isn't released back to the OS as immediately or predictably as a naive malloc
- Retained/metadata memory can accumulate and has no obvious release path (#2675, 'How to release retained and metadata')
- 5.4.0 removed seven legacy tcache tuning mallctls (lg_tcache_nslots_mul, tcache_nslots_small_min/max, etc.); malloc_conf strings referencing them are now silently ignored rather than erroring
- Under vm.overcommit_memory=2, vm.max_map_count can grow steadily from jemalloc's extent/arena mmap behavior (#1328), which matters for containers with strict map-count limits

**Status:** Actively maintained: 5.4.0 shipped Sep 17 2026 with 160+ commits and the dev branch was pushed the same day as this review; BSD-2-Clause licensed and small enough to vendor, but the repo itself carries no modern jemalloc-vs-glibc benchmark numbers.

[repo](https://github.com/jemalloc/jemalloc) · [benchmark](http://people.freebsd.org/~jasone/jemalloc/bsdcan2006/jemalloc.pdf)

##### ltalloc  `C++`  `BSD-3-Clause`  `active`  `Tier C`

Single-file source drop-in overriding operator new/delete; thread-local free lists speed up many small (<256B) allocations vs CRT malloc.

**Beats:** operator new/delete (CRT/C runtime malloc) — Third-party smmalloc README table (128-byte concurrent alloc/free stress test, compiler/flags/units unstated) shows ltalloc vs CRT malloc on Windows 10/i7-2600: ~62.5M vs ~23.9M ops at 1 thread (~2.6x) and ~27.3M vs ~14.6M at 5 threads (~1.9x); on PS4: ~28.6M vs ~4.4M at 1 thread (~6.4x) and ~14.7M vs ~332K at 4 threads (~44x). In that same table ltalloc trails rpmalloc, hoard, and smmalloc at every thread count. I confirmed these exact figures by reading the smmalloc README directly.

**How:** Each thread keeps a per-size-class free list (a TCMalloc-inspired thread cache) so alloc/free for blocks under 56KB is O(1) with, in the common case, a single conditional branch. Size-class selection is computed from constants only (no dynamic data), so with LTO/inlining enabled (-flto, /GL, -ipo) the compiler can inline the whole allocation path at the call site. Blocks are moved between the thread-local list and a shared central list in batches of up to 256 to bound cross-thread contention (at most one spin-lock per 256 ops), and chunks carry one 64-byte header per 64KB instead of a per-allocation header, cutting fragmentation.

**Use it when:**
- Hot path is many small (<256B) alloc/free calls, e.g. STL container churn, especially with a producer-consumer pattern where one thread allocates and another frees.
- You can add a single ltalloc.cc to the build and build with LTO (-flto/-ipo//GL) to get the compile-time size-class inlining benefit.
- You want a drop-in for global operator new/delete with no per-container allocator template changes.
- Target is Windows (MSVC) or Linux/macOS; ARM64/ARM64EC support was merged in April 2026 for those wanting arm64.
- You're fine manually reclaiming memory to the OS (via ltalloc_squeeze()) instead of relying on automatic trim.

**Skip it when:**
- You need memory returned to the OS automatically; small-block memory is only released when you explicitly call ltalloc_squeeze().
- You need allocator statistics/introspection - none is provided by design (no malloc_stats equivalent).
- Correctness matters more than raw throughput: open, unresolved issues report a segfault in ptrie_insert (#23), a realloc() hang/CPU-spin (#27), and chunk leaks (#30).
- You want an actively developed project: real bug-fix activity stopped in 2019; the only 2026 commit was an externally contributed ARM64 PR merge.
- Peak throughput vs. other allocators (not just CRT) matters: in the third-party smmalloc benchmark table, ltalloc trails smmalloc, rpmalloc, and hoard at both 1 and 5 threads on i7-2600.

**Integration:** source-drop · none (stdlib.h; optional <new>/<limits> only for the ltalloc.hpp STL-allocator wrapper) · Compiles as C or C++ (no C++11 required); thread-local storage via compiler builtins (__thread / __declspec(thread)), not the C++11 thread_local keyword; LTO (-flto/-ipo//GL) recommended for full inlining benefit · Windows (MSVC, AppVeyor CI) and Linux/macOS (Travis CI); ARM64/ARM64EC support merged April 2026; primarily x86/x86-64

**Vs siblings:** Pick ltalloc over rpmalloc or smmalloc (same category, both also beat CRT malloc) only when you want the absolute smallest integration footprint - one .cc file, no build-system hookup - and can tolerate a project with no real bug-fix activity since 2019 and open segfault/hang reports; in the shared smmalloc benchmark table ltalloc is consistently slower than both rpmalloc and smmalloc, so neither is chosen for raw throughput.

**Gotchas:**
- Full performance depends on LTO so the compiler can inline the compile-time size-class computation; without it you keep correctness but lose much of the speed edge.
- Memory for small blocks is never returned to the OS automatically; call ltalloc_squeeze() yourself (e.g. periodically from a background thread) to release it.
- No memory-usage statistics API exists by design; wrap in your own malloc if you need introspection.
- Several correctness bugs are open and unfixed as of the last commit (April 2026): segfault in ptrie_insert, realloc() hang, chunk leaks.

**Status:** GitHub marks the repo active (pushed April 2026, not archived) and it is not a fork, but real development stopped in 2019 - the only 2026 activity was merging one external ARM64/ARM64EC PR - and 8 issues remain open including unresolved crash/hang reports. BSD-3-Clause and a single source file, so it's cheap to vendor and pin even though upstream is effectively dormant.

[repo](https://github.com/r-lyeh-archived/ltalloc) · [benchmark](https://github.com/SergeyMakeev/smmalloc#performance)

##### rpmalloc  `C`  `MIT`  `active`  `Tier C`

Lock-free, per-thread-caching malloc replacement for C/C++, drop-in via LD_PRELOAD or override, faster than glibc/tcmalloc/jemalloc under threaded churn.

**Beats:** crt (system glibc malloc on Ubuntu 16.10, backing operator new/delete); charts also include tcmalloc, ptmalloc3, jemalloc, lockfree-malloc, scalloc, lockless — Verifier-confirmed numbers come from the project's own (now separate) rpmalloc-benchmark suite run on one Ubuntu 16.10 machine (8 logical cores; CPU model and compiler unstated): roughly 2.3x crt (glibc malloc) throughput at 1 thread and 3.4x at 4 threads for random 16-1000B allocations, and about 2.4x at 1 thread for 512B-160000B allocations, all read approximately off chart images (tier C, no raw numbers in the page text). The suite's own 'lockless' allocator beats rpmalloc in the large-size chart, contradicting the page's 'faster than all tested allocators except lockfree-malloc' claim.

**How:** Each thread owns a private heap and the hot allocate/free path takes no locks. Memory is organized span (256MiB-aligned) -> page -> block by fixed size class, so free() locates the owning span/page header in O(1) by masking the pointer's low bits instead of a table lookup. Blocks freed by a non-owning thread are pushed to a per-page atomic deferred free list and reclaimed lazily by the owner thread, avoiding the double thread-cache hop other allocators pay on producer/consumer handoff.

**Use it when:**
- Multi-threaded C/C++ workloads with heavy alloc/free churn, especially cross-thread frees (producer/consumer handoff) where lock contention dominates.
- Need a quick libc malloc swap to test allocator impact via LD_PRELOAD/DYLD_INSERT_LIBRARIES without recompiling the target binary.
- Want natural 16-byte alignment on every allocation without calling aligned-alloc variants.
- Want a small (~3.3k-line core), single-vendor C11 allocator you can vendor as source and actually read.
- Workloads whose high/low allocation water-mark swing fits the free-page retention thresholds, so committed pages stay resident instead of thrashing decommit/recommit.

**Skip it when:**
- Code that relies on operator new throwing std::bad_alloc on OOM — rpnew.h's overrides call rpmalloc() directly and return null on failure instead of throwing, silently breaking exception-based OOM handling.
- You need a std::allocator-compatible type to plug into individual std:: containers rather than a global malloc replacement.
- Threads that touch a few blocks from many different size classes each commit a page per class, wasting resident memory versus a single shared arena.
- Windows with explicit huge pages enabled: huge-page-backed ranges can't be partially decommitted and stay committed until the whole span unmaps.
- Targets outside Windows/Linux/macOS/iOS/Android on x86-64/arm64 (also LoongArch, arm64ec per changelog) — no WASM or other embedded targets in CI.

**Integration:** source-drop (rpmalloc.c/h, ~3.3k LOC core; also builds as static/shared lib via configure.py + ninja) · none · C11 (C++ optional, only needed for the operator new/delete override in rpnew.h) · Windows, Linux (glibc and musl/Alpine), macOS, iOS, Android; x86-64 and arm64 covered in CI

**Vs siblings:** Pick rpmalloc over the arena/pool-style siblings (metapool, the two arena-allocator entries, ShortAlloc) when you need a general-purpose, thread-safe, drop-in replacement for the whole process's malloc rather than a scoped bump/arena allocator for one object's lifetime; pick it over SuperMalloc, Hoard, scalloc, or NUMAlloc when you want a small, single-vendor, actively maintained C11 source you can vendor and read, instead of a research-grade or NUMA/HTM-specific allocator with heavier build or hardware requirements.

**Gotchas:**
- Overridden operator new returns null on allocation failure instead of throwing std::bad_alloc (confirmed in rpnew.h — no null-check/throw logic anywhere in the override), breaking code that expects exception-based OOM handling.
- If rpmalloc is compiled as a static lib and the caller only ever invokes plain malloc/free (never an rp*-prefixed symbol), the linker can drop the override object entirely; call the provided rpmalloc_linker_reference() dummy, or include rpmalloc.h in a translation unit, to force inclusion.
- On Windows, huge-page-backed memory can't be partially decommitted, so unused ranges stay committed until the whole span unmaps; on Linux, unused huge-page ranges are only decommitted on kernel 5.18+.
- The custom memory_map/memory_unmap interface changed in 2.0 (gained separate commit/decommit callbacks) and is not source-compatible with pre-2.0 custom map/unmap implementations.

**Status:** Actively maintained (last commit 2026-07-15, current release 2.0.1) and public-domain/MIT dual-licensed; the verified crt numbers predate a major 2.0.0 architecture redesign (span->page->block replacing the earlier span->block design, confirmed in the CHANGELOG read this session), so they may not reflect current performance — the current README/BENCHMARKS.md use a newer mimalloc-bench-based methodology that has not been independently verified to this tier.

[repo](https://github.com/mjansson/rpmalloc) · [benchmark](https://github.com/mjansson/rpmalloc-benchmark/blob/master/BENCHMARKS.md)

##### smmalloc  `C++`  `MIT`  `stale`  `Tier C`

Lock-free, thread-cached proxy allocator for small (16-992B) game allocations; passes everything else through to CRT malloc.

**Beats:** CRT malloc/free (C runtime heap, the allocator under default operator new) — README's own (unreproduced, Tier C) tables show smmalloc's ops/sec beating CRT malloc/free on a multithreaded random 16-80B alloc/free stress test: ~3.9x at 1 thread and ~2.6x at 5 threads on Windows 10/i7-2600, and ~8.1x at 1 thread on PS4; neither table states the compiler or optimization flags used.

**How:** Each thread keeps a small local cache (stack of up to SMM_MAX_CACHE_ITEMS_COUNT items per bucket) so most alloc/free calls touch no shared state. When a thread cache misses, each size-class bucket is backed by a lock-free singly-linked freelist using an atomic tagged-index (tag+offset packed into a 64-bit head) compare-and-swap to avoid ABA races without a lock. No per-allocation header/metadata is stored, so overhead is near zero, matching the README's own ~40-cycles-per-op figure for cache hits. Bucket sizes are computed algorithmically (default piecewise-linear partitioning) instead of via a lookup table.

**Use it when:**
- Multithreaded C++ game/engine code with many repeated small (roughly 16-992B under the default partitioning) allocations and frees, e.g. per-frame temporaries
- You already have a general-purpose fallback allocator and just want a fast path for a handful of known hot small sizes
- Console targets where the platform default heap is a bottleneck (shipped in Warface on PS4, Xbox One, Switch)
- You can manage explicit thread-cache create/destroy calls as part of each worker thread's lifecycle
- You're fine choosing bucket counts/size classes up front rather than using a fully general allocator

**Skip it when:**
- You need a true process-wide drop-in replacement for operator new/malloc (no LD_PRELOAD/global-override support; issue #5 requesting this is open, unresolved since 2022)
- Your allocation sizes fall mostly outside the configured buckets — those pass straight through to the fallback allocator with no benefit
- You need active upstream maintenance: no commits since 2023-10-13, and several issues (plain-C usage, LD_PRELOAD, Conan packaging) are open and unanswered
- You need a pure C API/codebase — this is C++11 (templates, namespaces, std::atomic); issue #7 asking about plain-C use has no reply
- You need independently reproduced numbers or a stated compiler/optimization-flag methodology — the README benchmark names hardware but not compiler or flags

**Integration:** source-drop · none (C++ standard library only: <atomic>, <memory>, <array>, etc.) · C++11 (CMakeLists.txt sets CMAKE_CXX_STANDARD 11 / -std=c++11 for GCC) · x86/x64; CI (GitHub Actions) builds and runs tests on Ubuntu and macOS with g++/clang++ and on Windows (Win32 and x64) with MSVC; also shipped on PS4 per README, though PS4 isn't in public CI

**Vs siblings:** Pick smmalloc over ltalloc or rpmalloc when you want a thin proxy layer restricted to a few known small size classes (e.g. per-frame game allocations) rather than a full malloc replacement; on the same i7-2600/CRT benchmark smmalloc's own reported numbers beat ltalloc (~3.9x vs ~2.6x CRT at 1 thread) and it has real console shipping history (Warface on PS4/X1/Switch) that the smaller general-purpose siblings don't claim.

**Gotchas:**
- Must call _sm_allocator_thread_cache_create for every thread that allocates/frees through smmalloc and destroy it before the thread exits, or you lose the fast path or leak the cache
- Bucket count and total pool size are fixed at _sm_allocator_create time; undersizing them silently routes more traffic to the fallback allocator with no error
- The three bucket-size partitioning schemes (linear/piecewise-linear/float) are compile-time #defines, not runtime options — switching requires recompiling smmalloc
- No per-allocation size/metadata is stored, so _sm_free/_sm_msize must be called against the same allocator instance that produced the pointer; mixing instances is undefined behavior

**Status:** Maintenance is stale (no commits since 2023-10-13, and issues on LD_PRELOAD support and plain-C usage remain open and unanswered), but it's MIT-licensed, dependency-free, and small enough (4 source files) to vendor as-is.

[repo](https://github.com/SergeyMakeev/smmalloc) · [benchmark](https://github.com/SergeyMakeev/smmalloc#performance)

##### TCMalloc (google/tcmalloc)  `C++`  `Apache-2.0`  `active`  `Tier D`

Google's per-CPU-cache C/C++ allocator, positioned as a faster-at-scale alternative to glibc malloc, though unquantified in the repo.

**Beats:** glibc malloc — No numeric benchmark of google/tcmalloc vs glibc malloc (or std::allocator/operator new) appears in the repo; overview.md only claims it is 'designed to be more efficient at scale.' The only peer-reviewed numbers found (Hunter, Kennelly et al., OSDI 2021) measure TCMalloc's hugepage-aware TEMERAIRE backend against TCMalloc's own prior legacy pageheap, not glibc: +7.7% RPS / -2.4% RAM (abstract), +5.2% average throughput (Table 1) across 8 Google WSC apps, pageheap overhead 14.3%->10.6% (Fig. 15), fleet IPC +1.2%, and Redis 6.0.9 +0.75%/+0.44% RPS (LLVM -O3, Skylake Xeon, 2000 trials).

**How:** Fast-path allocation/free happens in a per-CPU cache (default) or per-thread cache (fallback), both lock-free for the common case. Per-CPU mode uses Linux restartable sequences (RSEQ, kernel >=4.18) so a core-local push/pop either completes atomically or is transparently restarted on preemption/migration, avoiding atomic instructions. Cache misses refill from a CentralFreeList/TransferCache middle-end sized by allocatable size-classes, backed by a hugepage-aware page-heap (TEMERAIRE) that cuts TLB pressure and fragmentation versus the legacy pageheap.

**Use it when:**
- Highly parallel, multi-threaded C++ server workloads on Linux x86-64/AArch64 with RSEQ kernel support (>=4.18)
- Already building with Bazel and Abseil, or willing to add both as dependencies
- Need built-in heap telemetry/sampling (MallocExtension) for fleet-scale memory tracking
- Large-fleet deployments where small reductions in pageheap overhead/RAM matter at scale (per the OSDI 2021 TEMERAIRE data)
- OK rebuilding from source at or near HEAD rather than linking a stable prebuilt library

**Skip it when:**
- Non-Linux targets: no documented Windows/macOS support; only Linux is supported, PPC is 'best effort'
- Kernels <4.18 or RSEQ disabled: falls back to legacy per-thread caching, losing the main fast-path win
- Code that needs std::bad_alloc/exception-based OOM handling: TCMalloc crashes directly on allocation failure instead of throwing
- Projects that cannot add Abseil (and Bazel, or the experimental CMake path) as build dependencies
- Anything needing dynamic load/unload of the allocator or ABI stability across TCMalloc versions: neither is supported or promised

**Integration:** source-drop / static lib (built from source with Bazel; no prebuilt binary, no header-only mode) · Abseil (hard dependency, pinned in MODULE.bazel); also pulls in protobuf, re2, bazel_skylib as Bazel deps · C++17 (C11 for C code); gcc 12.1+ or clang 11.0+; Bazel 4.0+ (CMake support experimental) · Linux x86 and AArch64, little-endian 64-bit, libstdc++/libc++ (PPC best-effort); no Windows/macOS documented

**Vs siblings:** Pick over gperftools' tcmalloc when you want the actively developed successor with per-CPU RSEQ caching and the hugepage-aware TEMERAIRE backend, instead of gperftools' legacy per-thread-only pageheap. Pick mimalloc/jemalloc/snmalloc instead when you want a documented head-to-head number against your baseline in-repo — none of google/tcmalloc's docs quantify it against glibc, std::allocator, or those allocators.

**Gotchas:**
- No ABI stability: docs/compatibility.md says build from source (ideally HEAD), don't depend on a compiled representation, don't open namespace tcmalloc, don't take the address of its API functions
- Allocation failure crashes the process instead of throwing std::bad_alloc, which can surprise code relying on exception-based OOM handling
- No dynamic loading/unloading support
- The RSEQ fast path is fragile in practice: closed issue #292 documents crashes on Linux >=6.19 from RSEQ ABI interaction with glibc's own rseq registration

**Status:** Actively maintained (commits current as of the record date) and Apache-2.0/copyable, but not a drop-in swap: expect to vendor the source, add Abseil, and build with Bazel rather than link a stable prebuilt library.

[repo](https://github.com/google/tcmalloc) · [benchmark](https://github.com/google/tcmalloc/blob/master/docs/overview.md)

#### async-tasks-threadpools

##### BS::thread_pool  `C++`  `MIT`  `active`  `Tier D`

Single-header C++17/20/23 thread pool that reuses worker threads to avoid std::thread's per-task creation overhead.

**Beats:** std::thread — No direct std::thread- or std::async-vs-pool number is published anywhere in the README; the only measured figure is a 24.2x multithreaded-vs-single-threaded speedup on the project's own Mandelbrot benchmark (32-thread Intel i9-13900K, MSVC, C++23, /O2), which quantifies parallel scaling of the pool itself, not the per-task OS-thread-creation overhead the Motivation section claims std::thread has.

**How:** The entire speed case is avoiding OS thread creation/teardown per task: threads are spawned once at pool construction and repeatedly pull work off one shared task queue guarded by a mutex/condition variable for the pool's lifetime, instead of std::thread's per-call CreateThread()/clone(). Optional features (priority, pause, deadlock checks) are selected via a bitmask template parameter, so pools that don't enable them pay no extra runtime cost. There is no work-stealing, lock-free queue, or SIMD involved -- it is one shared FIFO queue plus thread reuse, not algorithmic scheduling cleverness.

**Use it when:**
- Need a zero-dependency, header-only pool that drops into an existing C++17 project without a new build dependency
- Many short-lived tasks (thousands+) where std::thread's per-call OS thread creation would dominate runtime
- Want built-in loop parallelization (submit_loop/detach_loop) instead of hand-rolling chunking over std::thread
- Need optional task priority, pause/resume, or deadlock detection without adopting a larger framework like oneTBB or Taskflow
- HPC/scientific-computing workloads with many uniform-sized tasks, where a single shared queue is enough

**Skip it when:**
- Imbalanced task graphs where some threads finish early and idle -- no work-stealing, so tail latency suffers vs. TooManyCooks/dispenso/libfork under uneven task sizes
- Need a hard measured number vs. std::thread/std::async before adopting -- none is published; only a self-referential single-vs-multithreaded Mandelbrot speedup is measured
- Calling wait()/wait_for()/wait_until() recursively from inside a task on the same pool without enabling wait_deadlock_checks -- deadlocks silently by default (documented in the README's own example)
- Need fiber/coroutine-style cooperative scheduling or tight oneTBB/OpenMP interop -- this is a plain OS-thread pool
- Apple Clang + C++20 module import path: README states Apple Clang is not officially supported there (plain header-only include is unaffected)

**Integration:** header-only · none (C++ standard library only) · C++17 (C++20/23 optional, enables module import and extra perf); verified with Clang 21, GCC 15, MSVC 19.50 · any C++17-conformant compiler/OS; native extensions (thread/process priority, affinity, naming) additionally target Windows, Linux, macOS

**Vs siblings:** Pick BS::thread_pool over Boost.Fiber, dispenso, TooManyCooks, libfork, or Taskflow when you want one self-contained header with zero dependencies beyond the standard library and don't need work-stealing or fiber-level concurrency; pick a work-stealing pool instead (dispenso, TooManyCooks, libfork) when task sizes are uneven or you need a published std::thread/std::async number, which this project doesn't provide.

**Gotchas:**
- wait()/wait_for()/wait_until() called from inside a task running on the same pool deadlocks by default; opting into BS::tp::wait_deadlock_checks (BS::wdc_thread_pool) turns that into a thrown BS::wait_deadlock instead of a hang
- Optional features (priority, pause, wait-deadlock checks) are chosen via a bitmask template parameter at the pool's type, so combining features means a distinct pool type per combination, not a runtime toggle
- The pool cannot forcibly terminate a running task; cancellation requires the task itself to poll a flag
- Task priority is a signed 8-bit value (-128 to 127, higher runs first) only when BS::tp::priority is enabled -- ignored otherwise

**Status:** Actively maintained (pushed 2026-01-04, 0 open issues, MIT-licensed, 3,055 stars, companion SoftwareX paper and arXiv:2105.00613); single header is trivially small enough to vendor into any project.

[repo](https://github.com/bshoshany/thread-pool) · [benchmark](https://github.com/bshoshany/thread-pool#readme)

#### bitsets-and-succinct

##### BitLib  `C++`  `BSD-3-Clause`  `stale`  `Tier C`

Header-only bit_vector and STL-style bit algorithms that beat std::vector<bool> by operating word-at-a-time instead of bit-at-a-time.

**Beats:** std::vector<bool> — First-party Google Benchmark results in BitLib's README, run on undocumented hardware/compiler/stdlib, show bit:: algorithms beating std:: on std::vector<bool> at 'large' size (2^24 bits): shift_left 371,224ns vs 105,227,752ns (~283x), reverse 1,245,260ns vs 293,563,397ns (~236x), count 365,194ns vs 58,934,071ns (~161x), rotate 7,333,284ns vs 514,697,313ns (~70x), and set 1.90ns vs 2.39ns (~1.26x); the same table also benchmarks against pinam45/dynamic_bitset and noporpoise/BitArray.

**How:** The library is built on 'bit iterators' (from Vincent Reverdy's bit/bit-algorithms projects) that track a word pointer plus a sub-word bit position, letting algorithms process a full WordType (typically uint64_t) per step instead of std::vector<bool>::iterator's implicit bit-by-bit proxy-reference access. Word-aligned ranges get bulk word operations (memmove-style shifts, popcount via libpopcnt for count, word-wise bitwise ops for transform), with a separate slower path for unaligned (U) boundaries. An optional SIMD path via Google Highway (BITLIB_HWY) is available but not on by default.

**Use it when:**
- Bulk bitset operations (shift, rotate, reverse, transform, count) over large bit ranges (tens of thousands of bits and up) where std::vector<bool>'s bit-by-bit iteration is the bottleneck
- Code already calling <algorithm> functions on std::vector<bool> that can be swapped to bit:: equivalents with matching signatures
- Word-aligned or mostly-aligned access patterns (aligned ranges are 1.5-5x faster than unaligned in BitLib's own numbers)
- Projects that can pin to a single header-only vendored dependency and C++17 or newer
- Prototyping/research code where a stale-but-working header is acceptable and the library can be forked/patched in place

**Skip it when:**
- You need the exact std::vector<bool> ABI/type (e.g. interop with code expecting std::vector<bool> by value) rather than a similarly-shaped but distinct bit_vector type
- Small containers (small = 256 bits): several bit:: operations are still faster than std but by single-digit-ns margins, not worth a new dependency for
- You need algorithms not yet implemented (sort, stable_sort, inner_product, shuffle, sample, mismatch, search, search_n, move_backward are all open feature requests, not present)
- You need active upstream support: last commit 2024-06-06, no releases/tags visible, solo maintainer
- You need SIMD acceleration out of the box: Highway support exists but is opt-in and unbenchmarked in the published table

**Integration:** header-only · none for core library; Google Highway only if BITLIB_HWY SIMD path is enabled; GoogleTest/Google Benchmark only for building tests/benchmarks · C++17 (CMakeLists defaults to C++17, notes C++20 is faster and adds std::shift_* interop); CI tests GCC 11 on Ubuntu 20.04/22.04 with -std=17 and -std=20 only · not documented beyond CI: only Linux+GCC 11 is exercised in CI (.github/workflows/cmake.yml); no macOS/Windows/clang CI coverage, no ISA requirement for the core path (SIMD path via Highway is optional)

**Vs siblings:** Pick BitLib over sul::dynamic_bitset when you need the fuller STL-algorithm surface (rotate, transform, swap_ranges, copy_backward) rather than just a bitset type, and over plf::bitset/better_bitset (which target std::bitset, a fixed-size type) when your container size is runtime-determined like std::vector<bool>. sul::dynamic_bitset showed a larger small-size shift_left win in BitLib's own table (13.1ns vs BitLib's 26.8ns), so for small, shift-heavy workloads it may edge out BitLib.

**Gotchas:**
- Bit position within a word increases LSB to MSB, which is the opposite of how people usually read a printed bit string; the README calls this out as a common source of bugs when writing custom algorithms against bit_iterator directly
- Aligned (A) vs unaligned (U) vs random (R) iterator boundaries materially change performance (e.g. bit::reverse (large) 1.25ms aligned vs 1.80ms unaligned) — the win over std:: shrinks (but does not disappear) on misaligned ranges
- SIMD path requires manually defining BITLIB_HWY and adding Google Highway as a dependency; it is not covered by the published benchmark table
- Only 10 of the library's own open issues are unimplemented std::algorithm equivalents (sort, mismatch, search, search_n, shuffle, sample, inner_product, move_backward) — check the list before assuming full <algorithm> parity

**Status:** Stale: last commit 2024-06-06, 11 open issues (all feature requests, no known correctness bugs found), 76 stars, single maintainer; BSD-3-Clause and header-only, so it is cheap to vendor and patch even without upstream activity.

[repo](https://github.com/bkille/BitLib) · [benchmark](https://github.com/bkille/BitLib/blob/master/README.md)

##### sul::dynamic_bitset  `C++`  `MIT`  `active`  `Tier C`

Header-only C++17/20 dynamic bitset beating std::vector<bool> on word-level shift/count operations in third-party benchmarks.

**Beats:** std::vector<bool> — On BitLib's (bkille/BitLib) third-party Google Benchmark suite — not dynamic_bitset's own repo — sul::dynamic_bitset beat std::vector<bool> by ~26x (small) to ~165x (16,777,216-bit) on shift_left and ~37x to ~161x on count; it was ~1.9x faster than std:: on small fill but ~1.2x slower on large fill (429,375 ns vs 356,517 ns), with large-size set roughly tied (2.37 ns vs 2.39 ns). No compiler, compiler flags, or CPU model are stated on the benchmark page.

**How:** Operations work a whole block (64 bits by default) at a time over an internal std::vector<Block>, instead of the per-bit iteration generic std:: algorithms perform on std::vector<bool>'s bit-reference proxy. Shifts, fills, and transforms move/OR/AND whole words; population count uses compiler builtins or C++20 <bit> intrinsics, and can optionally call kimwalisch/libpopcnt (SIMD popcount) if its header is found at compile time.

**Use it when:**
- Large bit vectors (roughly 10^5+ bits) doing frequent shift_left/shift_right, count, fill, or transform, where std::vector<bool>'s per-bit loop dominates runtime
- Want boost::dynamic_bitset-like ergonomics (resizable size, bitwise operators, find-next) without taking a Boost dependency
- Bitset size is only known at runtime, ruling out std::bitset<N>
- Want an optional SIMD-accelerated popcount (via libpopcnt) for hot counting loops without writing it yourself
- Want a single header you can vendor into a codebase with no build step

**Skip it when:**
- Small bitsets (<=256 bits) doing fill/set-style operations: the measured win over std::vector<bool> is marginal (~1.9x) or a loss (large-size fill is ~1.2x SLOWER, large set is roughly tied)
- Code needs std::bitset's fixed compile-time size, constexpr-friendliness, or std::vector<bool>'s standard iterator/algorithm compatibility
- Code performs bitwise ops (&, |, ^, comparisons) on operands of different sizes expecting boost-style zero-padding: the maintainer explicitly rejected that semantics (see gotchas)
- Need boost::dynamic_bitset's full feature surface (this library states a narrower one)
- Want first-party, reproducible performance numbers before committing: the cited results are from a third-party (BitLib) README, not dynamic_bitset's own benchmark repo, and no compiler, flags, or CPU model are given

**Integration:** header-only · none required; optional kimwalisch/libpopcnt (auto-detected via __has_include, used for faster count() if present and not disabled with DYNAMIC_BITSET_NO_LIBPOPCNT) · C++17 (C++20 optional, enables <bit> intrinsics); CMake 3.10+ only needed if consumed as a CMake subproject · any (CI covers Ubuntu, Windows MSVC, Windows MSYS2, macOS); no SIMD/ISA requirement for the library itself, only for the optional libpopcnt dependency

**Vs siblings:** Pick this over BitLib when you want an in-place, resizable container with boost::dynamic_bitset-style ergonomics rather than a span/iterator-based bit-algorithms library (BitLib actually posted faster shift_left/reverse numbers on the same large-size benchmark). Pick over plf::bitset when the size is only known at runtime, not compile-time. CRoaring and pasta::bit_vector target compressed/succinct/rank-select workloads, not general mutable dense bitsets, so they answer a different problem than dynamic_bitset.

**Gotchas:**
- operator&, |, ^, ==, and comparisons all require the caller to manage sizes; the maintainer explicitly rejected boost-style 'pad the shorter operand with zeros' semantics (issue #4) because it breaks algebraic properties like (a^b^b)==a, so mixed-size use needs care
- No standard iterators: bit access uses a reference-proxy object (like std::vector<bool>), so range-for/std::algorithm code expecting real iterators won't compile
- libpopcnt use is silent and header-detected at compile time; vendoring only dynamic_bitset.hpp without libpopcnt.h means count() falls back to builtin popcount, so the cited count() benchmark numbers may not reproduce as-is
- As of the versions discussed in issue #9, there was no documented to_ulong()/to_ullong()-style conversion beyond unsigned long long width without asserts/UB — check the current header if you need numeric conversion

**Status:** Actively maintained (last commit 2026-09-12, MIT license) by a single maintainer who has said free time is limited; being a small header-only file, it's easy to vendor and keep working even if upstream slows further.

[repo](https://github.com/pinam45/dynamic_bitset) · [benchmark](https://github.com/bkille/BitLib/blob/master/README.md)

#### concurrency-queues-locks

##### eventpp::SpinLock (eventpp GeneralThreading policy)  `C++`  `Apache-2.0`  `stale`  `Tier C`

Header-only spinlock policy for eventpp's EventQueue/EventDispatcher, swapping std::mutex for a std::atomic_flag test-and-set lock at <=core-count thread counts.

**Beats:** std::mutex — On one Intel Core i5-8300H laptop (4 cores/8 threads, Windows 10) compiled with MinGW GCC 11.3.0, moving 10M events across 100 event types/listeners through eventpp's EventQueue: eventpp::SpinLock beat std::mutex only at 1 enqueue/1 process thread (1303ms vs 1824ms, ~1.4x faster) and was roughly tied at 2/2 and 4/4 threads; it lost at 1/3 threads (3186 vs 2989ms) and was ~2.7x slower than std::mutex at 16/16 threads (1891 vs 708ms). The doc itself attributes this to thread count exceeding core count. No optimization flags or build type are stated, so evidence is capped at tier C.

**How:** It is a raw test-and-set spinlock: one std::atomic_flag, with lock() spinning on test_and_set(memory_order_acquire) and unlock() calling clear(memory_order_release) - no backoff, no OS involvement. This skips the kernel-mutex path (futex/CRITICAL_SECTION) std::mutex takes under contention, which wins when critical sections are short and thread count is at or below the core count. There is no yielding, so once threads outnumber cores it just burns CPU instead of sleeping.

**Use it when:**
- Thread count is roughly at or below the physical core count (benchmark shows a win at 1/1 and near-ties at 2/2 and 4/4 threads on a 4-core/8-thread laptop)
- You are already using eventpp's EventQueue, EventDispatcher, or CallbackList and want a drop-in policy swap without restructuring code
- Critical sections guarding the event/listener list are short (enqueue/dequeue bookkeeping, not long listener execution)
- Throughput on the enqueue/process path matters more than CPU headroom for other work
- You can control or know the thread count won't exceed available cores

**Skip it when:**
- Thread count exceeds CPU cores: the 16-enqueue/16-process benchmark shows SpinLock ~2.7x slower than std::mutex from busy-wait CPU burn
- Listeners or event processing hold the lock for any non-trivial time, since spinning wastes cycles instead of descheduling
- You need try_lock, timed_lock, recursive locking, or fairness/ordering guarantees; SpinLock implements only lock()/unlock()
- Power- or CPU-budget-constrained environments (laptops on battery, oversubscribed containers/VMs) where busy-waiting steals cycles from co-scheduled work
- You want portable, well-controlled benchmark evidence: only one first-party Windows/MinGW run exists with no stated optimization flags (evidence tier C)

**Integration:** header-only · none · C++11 for the library; author tests MSVC 2019/2022, MinGW GCC 7.2+, Ubuntu GCC 5.4, Intel C++ 2022, macOS GCC (benchmark itself used MinGW GCC 11.3.0) · any platform with a conforming C++11 compiler and std::atomic_flag (portable standard C++, no arch-specific intrinsics); benchmarked on Windows/x86-64

**Vs siblings:** The sibling entries (atomic_queue, Boost.Lockfree, moodycamel::ReaderWriterQueue, oneTBB concurrent_bounded_queue, xenium) are all standalone lock-free concurrent queues usable in any C++ codebase, with consistent multi-x nanosecond-latency wins over std::mutex. eventpp::SpinLock is not a queue at all — it only makes sense if you're already using eventpp's EventQueue/EventDispatcher/CallbackList and want to shave mutex overhead there at <=core-count thread counts; for a general-purpose concurrent queue outside eventpp, pick one of the lock-free siblings instead, since their evidence is stronger and their wins don't flip to a loss at higher thread counts the way SpinLock's does.

**Gotchas:**
- Plain test-and-set spinning with no backoff/pause/yield: it will peg a CPU core at 100% while waiting, unlike std::mutex which can block via the OS
- No fairness or ordering guarantee — it's a simple TAS lock, not a ticket/queued lock, so waiting threads can be starved under heavy contention
- Only takes effect where you explicitly wire it in via a custom Threading policy (GeneralThreading<SpinLock>); the library's default remains std::mutex
- Missing try_lock/timed_lock means code that needs std::unique_lock's try-lock or timed variants can't use it as-is

**Status:** Stale but not abandoned: last commit 2024-12-08, the README calls the project 'actively maintained' despite release gaps; Apache-2.0 licensed (GitHub's license detector shows NOASSERTION but the LICENSE file text is Apache-2.0) and header-only, so it's low-risk to vendor.

[repo](https://github.com/wqking/eventpp) · [benchmark](https://github.com/wqking/eventpp/blob/master/doc/benchmark.md)

##### moodycamel::ConcurrentQueue  `C++`  `BSD-2-Clause OR BSL-1.0`  `active`  `Tier C`

Lock-free MPMC C++11 queue with per-producer sub-queues and bulk ops, beating boost::lockfree::queue on throughput.

**Beats:** boost::lockfree::queue — On an 8-core AWS c1.xlarge, moodycamel with tokens reached 795.01k ops/s vs boost::lockfree::queue's 647.96k ops/s (~1.2x) at 8 threads under a balanced producer/consumer workload; the large 70-226x figures are from a producer-only, single-item-with-tokens enqueue microbenchmark, and the ~4-5x weighted averages include moodycamel's bulk operations, which boost and tbb do not support. g++ version and optimization flags are not stated for the AWS runs.

**How:** Each producer gets its own internal sub-queue built from contiguous, freelist-recycled blocks (default 32 elements) instead of a shared linked list, so producers rarely contend; consumers scan sub-queues for a non-empty one. Tokens let a thread cache its producer/consumer handle to skip repeated lookups, and bulk enqueue/dequeue amortize per-operation atomic/CAS overhead across many elements at once. try_enqueue never allocates once the queue is correctly pre-sized, trading a possible false-full return for zero lock/alloc cost on the hot path.

**Use it when:**
- Producer/consumer pipelines with many independent threads, where cross-producer linearizability is not required
- Workloads that can batch items — bulk enqueue/dequeue is where the largest measured gains are (up to ~226x on producer-only microbenchmarks vs boost::lockfree in this record)
- Need both non-blocking (spin/poll) and blocking (wait_dequeue) consumer modes from one library
- Header-only C++11 codebase that can't take a Boost or TBB dependency
- Per-item ordering only needs to hold within a single producer, not globally

**Skip it when:**
- Need strict global linearizable ordering across independent producers — explicitly not guaranteed
- NUMA machines where cross-socket memory reuse patterns matter — not NUMA-aware by the author's own admission
- Single-item, low-contention enqueue only, where boost::lockfree::queue is just ~1.2x slower and you'd rather have a narrower API
- Compilers older than g++4.8 / pre-VS2012, or g++4.6 specifically (documented std::atomic bug)
- Strict per-producer FIFO ordering is load-bearing: issue #437 (open, reported Dec 2025) describes a model-checker-found case where bulk, token-less enqueue/dequeue with small block sizes may reorder a producer's own sequence; unresolved as of this write-up

**Integration:** header-only · none for ConcurrentQueue; BlockingConcurrentQueue additionally needs lightweightsemaphore.h, shipped in the same repo · C++11; VS2012+ or g++ 4.8+ (g++4.6 has a known std::atomic bug and is unsupported) · any (pure C++11 atomics, no inline assembly); CI cross-compiles and runs tests for riscv64 Linux under QEMU; author-tested on Linux (Fedora) and Windows on x86

**Vs siblings:** no siblings catalogued yet

**Gotchas:**
- Not linearizable across independent producers; ordering is only guaranteed within a single producer's own enqueues
- try_enqueue never allocates — correct pre-sizing requires working through the block-size/producer-count formulas in the README, and even then contention can cause spurious false-full returns under weak memory ordering
- Exception safety requires element destructors and any bulk-operation iterators to never throw; only enqueue-side constructor exceptions roll back cleanly
- Open issue #437 (unresolved) questions whether bulk, token-less dequeue can skip a prefix of a sub-queue under certain interleavings with small block sizes

**Status:** Actively maintained (last commit 2026-07-11, 12.5k GitHub stars, packaged in vcpkg); dual BSD-2-Clause/BSL-1.0 single header, trivial to vendor.

[repo](https://github.com/cameron314/concurrentqueue) · [benchmark](http://moodycamel.com/blog/2014/a-fast-general-purpose-lock-free-queue-for-c++#benchmarks)

#### hash-maps-sets

##### parallel-hashmap (phmap)  `C++`  `Apache-2.0`  `active`  `Tier C`

Header-only, Abseil-derived flat/node hash maps and a btree; drop-in for std::unordered_map/map, ~3x faster inserts.

**Beats:** std::unordered_map — Per the record's verification of the repo's own raw benchmark data (100M random 8-byte-integer-key inserts, MSVC Visual Studio 2017, cl -EHsc -DNDEBUG -O2, CPU model not stated): std::unordered_map took 48.38s vs phmap::flat_hash_map 14.41s vs phmap::parallel_flat_hash_map 14.47s, roughly 3.4x faster than std::unordered_map. The writeup's own '~3x faster' sentence actually describes absl::flat_hash_map vs VS2017's std::unordered_map, not phmap directly.

**How:** Uses Abseil's swiss-table design: an open-addressed table with a parallel one-byte-per-slot metadata array probed with SSE2 (checks 16 slots at once), letting load factor run up to 87.5% before resizing. flat_hash_map/set store keys and values directly in the bucket array (no per-node allocation/indirection). parallel_* variants split the table into N (default 16) independently resizable submaps, which lowers peak resize memory and lets different threads lock different submaps concurrently.

**Use it when:**
- Insert/lookup-heavy replacement for std::unordered_map/set where you can accept flat_hash_map's pointer/iterator invalidation on mutation.
- Need pointer stability but still want a faster-than-std table: use node_hash_map/set instead of flat.
- Multithreaded code with a few large maps read/written from many threads: parallel_flat_hash_map/parallel_node_hash_map with an explicit mutex template argument (std::mutex, boost::shared_mutex, etc.) and if_contains/modify_if/try_emplace_l.
- Header-only C++11 codebase (old GCC/Clang/MSVC, embedded/toolchain-constrained) that can't pull in full Abseil.
- Want a std::map/set-like ordered container with lower memory than a red-black tree: btree_map/btree_set family.

**Skip it when:**
- Code relies on std::unordered_map/std::map pointer/iterator stability across mutation: flat_hash_map and all btree containers move elements in memory on rehash/mutation.
- Highly skewed concurrent insert workloads (most inserts hitting one key/submap): parallel_flat_hash_map throughput collapses under submap-lock contention (repo issue #215: 240M inserts, ~239M identical keys, CPU usage dropped to ~19%, 233s vs 17s for a Windows concurrent_unordered_map).
- Assuming built-in thread safety: the parallel_* default mutex is NullMutex (no locking); concurrent read+write without supplying a real mutex template parameter is undefined behavior and has produced real crashes (issue #181, EXC_BAD_ACCESS).
- Need Abseil's randomized iteration order for DoS resistance against adversarial keys: phmap disables that randomization by default (opt-in via PHMAP_NON_DETERMINISTIC).
- Large, expensive-to-move value types (roughly >100 bytes per README's own caveat): flat_hash_map's in-place moves get costly; node_hash_map is the safer choice.

**Integration:** header-only · none required; optional Abseil headers (include before phmap.h + define PHMAP_USE_ABSL_HASH) to use absl::Hash instead of std::hash, optional boost::hash_value() support · C++11 required (C++14/17 APIs like try_emplace available when the compiler supports them); GCC 4.7+, Xcode/Apple clang 4.2.1+, MSVC roughly VS2015 update3+ per phmap_config.h version gate; README states CI coverage on GCC 4.8-12, Clang 3.9-16, VS2015/2017/2019/2022, Intel 18/19 · tested on Windows, Linux, macOS; x86/x86-64 uses SSE2 for the parallel probe (per swiss-table design); phmap_config.h also has __arm__/__aarch64__ branches, so ARM builds are supported through the portable path

**Vs siblings:** phmap is the only sibling that bundles flat AND node hash variants, submap-sharded parallel_* variants with built-in per-submap locking, and a btree ordered-map family in one header-only, actively maintained package — pick it over ska::flat_hash_map/tsl::robin_map/sparsepp/Verstable when you specifically want that locking-capable multithreaded variant or the flat/node choice, and over libcuckoo when your concurrency needs are moderate (a few large maps, not massively parallel) since phmap's parallel_* design loses badly under heavy single-key contention (issue #215) where libcuckoo's design is built for exactly that.

**Gotchas:**
- flat_hash_map/set and all btree containers can relocate stored elements in memory on mutation, invalidating pointers/iterators — unlike std::unordered_map/std::map. Use node_hash_map/set if you need stability.
- parallel_* tables default to NullMutex (no locking); you must supply a real mutex type as the template's last parameter to get thread-safe concurrent access, or you risk crashes under concurrent read/write (issue #181).
- parallel_* insert throughput can collapse under extreme key skew because most threads contend for the same submap's lock (issue #215: near-total single-key workload dropped to ~19% CPU use and lost to a naive concurrent map).
- Abseil-style randomized iteration order (DoS mitigation) is off by default in phmap; enable explicitly with #define PHMAP_NON_DETERMINISTIC 1 before including phmap.h if that matters for your use case.

**Status:** Actively maintained (last commit 2026-09-10, 3.2k stars, Apache-2.0, header-only so trivially vendorable), but the author is directing new feature development to the C++20 successor repo 'gtl'; treat parallel-hashmap as the stable C++11-compatible branch rather than where new capabilities land.

[repo](https://github.com/greg7mdp/parallel-hashmap) · [benchmark](https://greg7mdp.github.io/parallel-hashmap/)

##### rigtorp/HashMap  `C++`  `MIT`  `stale`  `Tier C`

Header-only open-addressing hash map with backshift deletion, up to ~5x faster than std::unordered_map on delete-heavy workloads.

**Beats:** std::unordered_map — Self-published benchmark (README + src/HashMapBenchmark.cpp), gcc 10.2.1 on an AMD Ryzen 9 3900X (Fedora, isolcpus-isolated CCX), against libstdc++'s std::unordered_map in a delete-heavy insert-or-erase loop with size_t keys and 24-byte values. In-cache (100K entries): HashMap mean 24 ns/iter vs std::unordered_map 67 ns/iter (~2.8x). Out-of-cache (10M entries): HashMap 75 ns/iter vs 408 ns/iter (~5.4x). Optimization flags are not stated (CMakeLists.txt sets no CMAKE_BUILD_TYPE, only -mavx2 and warnings), and it's a single hardware configuration with no independent reproduction.

**How:** Open addressing with linear probing stores entries directly in a single contiguous std::vector of buckets, avoiding per-node allocation and pointer chasing. On erase it uses backshift deletion (shifting later entries back into the vacated slot) instead of tombstones, so probe sequences stay short even under the paired insert/erase churn in the benchmark. Bucket count is kept a power of two so index computation is a mask (idx & mask) rather than a modulo, and load factor is hard-capped at 50% to bound probe length.

**Use it when:**
- Delete-heavy or high-churn workloads (repeated insert+erase of the same keyspace) where backshift deletion avoids the tombstone buildup that degrades linear probing over time
- Keys/values are cheap, default-constructible, and copyable (the benchmark uses size_t keys and a 24-byte POD value), and you can reserve one sentinel value as the 'empty key'
- You want a single-header, zero-dependency container to vendor rather than pull in Abseil/Folly for a hash map
- Latency matters for both cache-resident and larger-than-L3 working sets, and you can tolerate stricter iterator-invalidation and no-destructor-on-erase semantics

**Skip it when:**
- You need a true drop-in replacement: the constructor signature differs (bucket_count, empty_key) and Key/T must be default constructible, which is also why it's excluded from Martin Ankerl's independent map_benchmark suite (per repo issue #2)
- Values own resources (std::string, std::vector, std::unique_ptr, etc.) where you rely on the destructor running on erase — HashMap does not call destructors on erase
- You need iterator/reference/pointer stability across mutations — every insert, erase, or rehash invalidates them, stricter than std::unordered_map
- You need >50% load factor for memory efficiency, multi-threaded access (thread safety is undocumented), or an actively maintained dependency (last commit 2023-09-25, effectively unmaintained)

**Integration:** header-only · none (STL only). The benchmark binary optionally links Abseil and uses x86 CRC32/AVX2 intrinsics plus a Linux huge-page allocator, but none of that is required by the library itself. · C++14 (CMake target_compile_features cxx_std_14 for the library; the benchmark target additionally requires C++17 and -mavx2) · any (the library is portable, architecture-agnostic C++14); only the benchmark's CRC32 hash, AVX2 flag, and MAP_HUGETLB allocator are x86-64/Linux-specific

**Vs siblings:** Pick HashMap when you want the smallest possible dependency (one ~250-line header, no external deps) specifically for delete-heavy/churn workloads where backshift deletion matters; the in-repo numbers show it beating both std::unordered_map and absl::flat_hash_map at that workload. Prefer emhash, ska::flat_hash_map/tsl::robin_map, or absl instead when you need iterator stability, don't want to manage an empty-key sentinel, or want a design that's actually included in independent benchmark suites (Ankerl 2022) and sees ongoing maintenance.

**Gotchas:**
- A reserved empty-key sentinel is mandatory at construction; using that value as a real key is undefined behavior (only asserted in debug builds)
- Destructors are never invoked on erase — backshift deletion just moves/overwrites slots, so resource-owning values leak until overwritten or the table is destroyed
- Iterators, pointers, and references are invalidated by every insert, erase, or rehash, not just rehashes as in std::unordered_map
- Max load factor is hard-coded to 50%; every insert path calls reserve(size_+1), so the table silently doubles capacity earlier than std::unordered_map would, trading memory for probe length

**Status:** Maintenance is stale (last commit 2023-09-25, about to cross into 'abandoned'), but it's MIT-licensed, header-only, and small enough (~250 lines) to vendor and audit directly rather than depend on for long-term support.

[repo](https://github.com/rigtorp/HashMap) · [benchmark](https://github.com/rigtorp/HashMap)

##### SIGMOD 2025 Contest Solution - Hash Join Pipeline (Robin Hood/Hopscotch/Cuckoo/Unchained)  `C++`  `MIT`  `active`  `Tier C`

Coursework hash-join pipeline: four custom open-addressing tables plus a columnar 'Unchained' design that beat std::unordered_map on an IMDB join benchmark.

**Beats:** std::unordered_map — On a 113-query IMDB hash-join benchmark (MacBook Pro, Apple M4 Pro, 14 cores, 48GB RAM; CMake Release + -march=native; compiler unstated), swapping std::unordered_map for the Unchained hashtable cut single-threaded hash insert+lookup time from 14,560ms to 7,343ms (~2.0x) and column-store total runtime from 24,696ms to 15,698ms (~1.57x), per REPORT.md's per-stage tables. Robin Hood, Hopscotch, and Cuckoo alone (row-store, Part 1) were only 3-18% faster than std::unordered_map. The repo's own 'Final speedup: ~16x' headline additionally folds in column-store layout, late materialization, and 14-core parallel execution against a single-threaded baseline -- it is not a hash-table-vs-std::unordered_map number.

**How:** Part 1's three tables use open addressing to shorten probe chains versus std::unordered_map's separate chaining: Robin Hood displaces by probe-sequence length, Hopscotch checks a 32-64-slot neighborhood bitmap, Cuckoo uses two tables with a splitmix64 second hash -- this alone is only ~3-18% faster. Most of the headline speedup comes from architecture: late materialization defers string payloads to (table,column,page,offset) references, an 8KB-paged column-store improves sequential access, and 'Unchained' sorts tuples by hash prefix into one contiguous adjacency array with a directory of precomputed 16-bit Bloom-filter tags per slot, trading pointer chasing for sequential scans and rejecting most misses before touching the array. Part 3 parallelizes tuple collection/build/probe across 16 threads via a 3-level slab allocator (each thread owns a private memory region, no allocator contention) and atomic-counter work stealing over fixed-size chunks.

**Use it when:**
- You want a worked, single-file reference for Robin Hood, Hopscotch, Cuckoo, or 'Unchained' (directory + adjacency array + Bloom tags) hashing in modern C++17.
- You're building your own analytical hash-join engine over int32 join keys and can adopt the surrounding column-store/late-materialization design, not just swap a container.
- Build-then-probe multimap workloads (many row-ids per key) rather than a general mutable map with deletes.
- 8-16+ core x86-64 or aarch64 machines where a work-stealing parallel build/probe pipeline amortizes across many queries.
- Benchmarking/prototyping hash-table variants against std::unordered_map on your own dataset before picking one.

**Skip it when:**
- You need a drop-in std::unordered_map replacement: the API is insert(key,row)/find(key), not the STL container interface (no erase, no iterators, no operator[]), and only int32 keys are exercised in tests/benchmarks despite the Key template parameter.
- You need a thread-safe table for concurrent insert/lookup from multiple threads on one instance: none of the four tables have internal synchronization -- the repo's own parallelism partitions data across separate thread-local structures instead.
- Your target lacks SSE4.2 (x86) or the ARM CRC32 extension: Unchained.hpp hashes via hardware CRC32 intrinsics (nmmintrin.h / arm_acle.h) with no portable software fallback.
- You need key deletion: none of the four HashMultiMap implementations expose remove/erase.
- You need production maturity: 1-star, 3-student university coursework repo with no independent replication and no issue/CVE history to check.

**Integration:** header-only for Robin Hood/Hopscotch/Cuckoo (single .hpp each); source-drop for Unchained (Unchained.hpp + Unchained.cpp, plus slab_allocator/tuple_collector/parallel_probing headers if you want the parallel build) · none for the hash tables themselves beyond the C++ standard library, plus hardware CRC32 intrinsics for Unchained only (nmmintrin.h on x86 / arm_acle.h on ARM). The surrounding application pulls in abseil, re2, nlohmann/json, sql-parser, range-v3, fmt, DuckDB, and Catch2 via CMake FetchContent, but those are not required to use the hash tables in isolation. · C++17 (CMakeLists.txt sets CMAKE_CXX_STANDARD 17), CMake >= 3.16; README recommends 'Clang 18 (recommended)' but the compiler actually used to produce the published numbers is not stated · x86-64 (SSE4.2 needed for Unchained's CRC32 intrinsic) or aarch64 (ARM CRC32 feature); CMakeLists.txt unconditionally adds -march=native except on PowerPC, so built binaries are tied to the build machine's CPU unless that flag is changed

**Vs siblings:** Pick this over the catalogued sibling hash maps only when you want a worked example of pairing a hash table with a column-store + late-materialization join pipeline and parallel build/probe, and are willing to extract and adapt a header (e.g. RobinHoodHash.hpp) yourself. For a maintained, general-purpose std::unordered_map replacement, prefer emhash, tsl::robin_map, or ska::flat_hash_map -- all have broader validation, non-coursework provenance, and don't require hardware CRC32 support.

**Gotchas:**
- Robin Hood (max_load 0.4) and Cuckoo (max_load 0.6) rehash by doubling; Cuckoo caps kick-outs at max_kicks=512 before forcing a full rehash+reinsert, a latency spike on adversarial key sets.
- Hopscotch throws std::runtime_error('Rehash failed during rehashing...') if neighborhood displacement fails while already rehashing -- an unguarded abort path under pathological hash distributions rather than a graceful fallback.
- Unchained caches a 64-bit CRC32-derived hash per tuple (HashTuple.hash) and reuses it across build passes to avoid recomputing CRC32+multiplication; if you repurpose the struct, keep that field in sync with your own hash function.
- All four tables are templated on Key via std::hash<Key>, but only int32 join keys are covered by the benchmarks and unit tests -- correctness/performance for string or composite keys is not demonstrated.

**Status:** Last commit 2026-08-08 (active), but this is University of Athens K23a coursework by 3 students with 1 star, zero pull requests, and no bug-tagged issues to check; MIT-licensed and small enough to vendor the individual headers, but treat it as a reference implementation rather than a maintained library.

[repo](https://github.com/ArisS44/Sigmod-2025-contest-solution) · [benchmark](https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/REPORT.md)

#### io-and-filesystem

##### CPath  `C`  `MIT`  `abandoned`  `Tier C`

Single-header C directory traversal library; faster than `find`, TinyDir, Cute Files, and Python os.walk on recursive walks.

**Beats:** find (GNU findutils), TinyDir, Cute Files, Python os.walk — Averaged over 100 runs of a recursive traversal over a large synthetic directory tree (MacBook Air7,2, dual-core Intel i5 @ 1.6GHz, -O3, compiler unnamed), CPath (C or C++, recursion or emplace) measured 0.082-0.083s wall time versus 0.147s for GNU find, 0.237s for Python os.walk, 0.284s for Cute Files, and 0.294s for TinyDir — about 1.8x faster than find and roughly 3.4-3.6x faster than Cute Files/TinyDir (derived from the reported wall times). It was not benchmarked against std::filesystem.

**How:** It does not eagerly call stat() on each entry; size/time info is loaded only on demand via `cpathGetFileInfo`, cutting per-entry syscalls versus TinyDir/Cute Files which stat every entry unconditionally. Its 'open file' (get file info from a path) needs a single syscall, versus TinyDir's approach of reopening and rescanning the parent directory (up to O(n) syscalls). The benchmark shows CPath and `find` have near-identical user time but CPath has much lower system time, consistent with the syscall-count reduction being the source of the win rather than faster CPU-bound logic.

**Use it when:**
- Cross-platform (Windows + POSIX) recursive directory listing from C or pre-C++17 C++ without pulling in std::filesystem or Boost.Filesystem
- You only need file names/types during traversal and want to skip stat() calls unless you actually need size/time
- A small, vendorable single-header dependency (~2.5k lines, MIT) is acceptable in the build
- Latency-sensitive walks over large trees where syscall count, not CPU work, dominates wall time
- You're willing to pin to and self-patch an abandoned header if bugs surface

**Skip it when:**
- You need std::filesystem/Boost.Filesystem feature parity (symlink handling, watching, permissions, atomic ops) — the author explicitly states CPath is not a std::filesystem replacement
- Windows-heavy usage: `cpathCanonicalise` has an open, unfixed length bug on Windows (issue #6), and CI never runs on Windows at all
- You need active maintenance: master's last commit is 2019-09-28, and 7 issues opened in 2023 (including a real init bug) remain untouched
- You need performance validated beyond one machine/toolchain: the only benchmark is first-party, single 2015 MacBook Air (dual-core i5 @ 1.6GHz), compiler unnamed, never independently reproduced
- You need paths longer than a fixed stack buffer: paths are stored in fixed-size `CPATH_MAX_PATH_LEN` buffers, not dynamically sized (open issue #7 acknowledges this)

**Integration:** header-only · none beyond the C standard library (dirent.h/windows.h, sys/stat.h, stdlib.h, string.h, etc.) · C89/C99-era C; C++ bindings target pre-C++17 compilers (no C++17 required); CI builds with gcc on Ubuntu 16.04/latest and macOS 10.14/latest · POSIX (Linux, macOS) and Windows in source (windows.h/tchar.h path exists), but CI only exercises Linux and macOS — Windows has an open, unresolved bug (issue #6) and is untested by CI

**Vs siblings:** The siblings (FastReader, reckless) beat std::ifstream/fstream and stdio for reading/writing file contents and logging, a different problem than directory enumeration — there's no real overlap. Pick CPath only when the bottleneck is recursive directory listing itself; use FastReader for fast file reads or reckless for high-throughput logging.

**Gotchas:**
- cpathGetNextFile does not stat() automatically — call cpathGetFileInfo (File::GetFileInfo in C++) explicitly or size/time fields stay unpopulated
- Open issue #1: the `file` output parameter isn't zero-initialized before a NULL check inside cpathGetNextFile — worth reading the source before relying on that check
- Paths live in fixed CPATH_MAX_PATH_LEN stack buffers rather than growing dynamically; very long paths can fail rather than resize (open issue #7)
- Windows cpathCanonicalise has a known, unfixed length-calculation bug (issue #6)

**Status:** Abandoned: master's last commit is 2019-09-28 (the raw repo pushed_at of 2023-09-24 reflects an unmerged side branch, not master); MIT-licensed and small enough (~2.5k-line single header) to vendor and patch yourself if needed.

[repo](https://github.com/BraedonWooding/cpath) · [benchmark](https://github.com/BraedonWooding/cpath#benchmarks)

#### math-simd-linear-algebra

##### Axiom (C++ tensor library)  `C++`  `MIT`  `active`  `Tier C`

Lazy-evaluated C++20 NumPy/PyTorch-style tensor library for CPU and Metal GPU; beats Eigen3 on some unary math ops, loses on others.

**Beats:** Eigen3 element-wise Array ops (A.array().sin()/cos()/exp()/log() on float32 MatrixXf) — docs/BENCHMARKS.md (auto-generated 2026-02-21; Test Environment states only 'Darwin 25.3.0 arm64', no CPU model or compiler) reports 4096x4096 float32 unary-op GB/s vs Eigen3: sin 26.0 vs 11.0 (~2.4x), cos 25.2 vs 11.0 (~2.3x), exp 23.0 vs 16.4 (~1.4x), log 17.0 vs 13.1 (~1.3x); the same table shows sqrt (39.0 vs 66.3) and tanh (14.3 vs 21.5) slower than Eigen3. Code confirms macOS sin/cos/exp/log dispatch to Apple Accelerate vForce ahead of Axiom's own Highway kernels, so the measured win largely reflects Accelerate vs Eigen3's own vectorization rather than a novel Axiom algorithm.

**How:** CPU element-wise ops dispatch through three tiers (seen in src/backends/cpu/cpu_operations.cpp): Apple Accelerate/vDSP (vvsinf/vvcosf/vvexpf/vvlogf) on macOS, then Google Highway's portable SIMD kernels (AVX2/AVX-512/NEON/SVE/RVV, see src/backends/cpu/simd/simd_dispatch.hpp) as the cross-platform fallback, then a scalar loop parallelized with OpenMP for large tensors. Matmul/linear algebra route through a BLAS/LAPACK backend (Accelerate, OpenBLAS, or native). A lazy graph compiler fuses chained elementwise operations and reuses buffers to cut materialization and memory traffic.

**Use it when:**
- On macOS/Apple Silicon, want NumPy/PyTorch ergonomics in C++ with a Metal GPU path and zero-copy CPU/GPU transfers
- Whole-tensor elementwise math (exp/log/sin/cos) at large sizes (~4096x4096 float32) where Accelerate vForce or Highway SIMD beats Eigen3's own vectorization
- Want einops-style rearrange/reduce and a lazy fused computation graph instead of hand-rolled expression templates
- Need built-in FFT, numpy/safetensors/flatbuffers IO, or basic NN layers (Linear, Conv, Attention, RNN) alongside tensor math
- Can link a built library (CMake, C++20 toolchain) rather than needing a header-only drop-in

**Skip it when:**
- Need a scalar, single-value <cmath>-style API — Axiom has no fine-grained per-value math entry point
- The op is sqrt or tanh specifically — Axiom's own benchmark table shows both slower than Eigen3 on the tested hardware
- Off-macOS (Linux/Windows), where the fast path is Highway SIMD + OpenMP, not Accelerate — the published GB/s numbers are macOS/Accelerate-specific and won't transfer as-is
- Need GPU acceleration beyond Apple Metal — no CUDA/ROCm backend
- Production use requiring API stability — v0.5.1, 114 stars, open issue on CPU-only macOS builds failing to link (#28) and a tracked gap in public-interface docs (#9)

**Integration:** static lib | shared lib (CMake FetchContent source-drop; not header-only) · bundled: Highway, mimalloc, pocketfft, flatbuffers, nlohmann_json, FP16, FXdiv; optional: OpenBLAS, Apple Accelerate framework (macOS), OpenMP, Metal/MPSGraph (macOS GPU) · C++20, CMake 3.20+, Clang/GCC/MSVC · macOS (Accelerate + Metal GPU), Linux, Windows; portable SIMD via Highway (SSE2 through AVX-512, NEON, SVE, RVV)

**Vs siblings:** trigno_simd_cpp, SLEEF, FABE13-HX, fast_math_cpp, fmath, and VDT are scalar/vector math-function libraries meant to drop into existing loops in place of <cmath>/libm calls; Axiom is a whole-tensor library with a lazy graph and GPU path, so pick it only when you also want NumPy/PyTorch-style tensor ops and fusion — not when you just need a faster std::sin/std::exp replacement, where the siblings are the direct fit and Axiom is not.

**Gotchas:**
- On macOS the measured unary-op speedups over Eigen3 come from Apple Accelerate vForce (vvsinf/vvcosf/vvexpf/vvlogf), not Axiom's own SIMD kernels — the win is largely Accelerate's, not portable
- sqrt and tanh are slower than Eigen3 in Axiom's own benchmark table — op-specific, not a blanket win
- Open issue #28: CPU-only builds on macOS can fail to link because some Metal call sites guard on __APPLE__ instead of the AXIOM_METAL_SUPPORT flag
- Library type follows BUILD_SHARED_LIBS (defaults to SHARED); set it explicitly before FetchContent/add_subdirectory if you need a single static archive

**Status:** Actively maintained (last commit 2026-05-29, v0.5.1, MIT) but young and small (114 stars, 5 open issues); 'copyable' usability means a real CMake build with bundled third-party deps, not a single header to vendor.

[repo](https://github.com/Frikallo/axiom) · [benchmark](https://github.com/Frikallo/axiom/blob/main/docs/BENCHMARKS.md)

##### FABE13-HX  `C`  `MIT`  `stale`  `Tier C`

SIMD sin/cos/sincos array kernel for C beating libm; rational Ψ-Hyperbasis approximation, no bit-exact IEEE guarantee.

**Beats:** libm sin/cos/sincos (the implementation <cmath>'s std::sin/std::cos ultimately call into) — The README compares fabe13_sincos array throughput to system libm's sincos (GNU math.h on Replit Linux/Clang 14, macOS system math.h on AppleClang 16) on unspecified x86 AVX2+FMA hardware, claiming 'up to 8.4x' only via headline text and chart images, with no table. Its one real table, for unspecified ARM64/NEON hardware, shows 1.00x-2.56x for N=10-10k, 1.53x at N=100k, and 4.36x-5.82x from N=1M-1e9, with max sin/cos error ~1.2e-11 vs libm; both fabe13 and the libm reference loop were built with -Ofast -ffast-math.

**How:** Replaces libm's polynomial minimax approximations with a rational 'Ψ-Hyperbasis' core, Ψ(x) = x/(1+(3/8)x²), plus rational correction terms for sin/cos, avoiding some of the work a general-purpose libm does. A GCC/Clang constructor function probes the CPU once at load time (AVX-512F > AVX2+FMA > NEON > scalar) and locks in one dispatch target for the process. The array path uses branchless quadrant correction and Payne-Hanek range reduction, unrolled and vectorized per architecture, so large arrays amortize reduction cost across SIMD lanes.

**Use it when:**
- Batch sin/cos/sincos over arrays of roughly 1e6-1e9 doubles on x86-64 (AVX2+FMA or AVX-512F) or aarch64 (NEON), where the README's own numbers show the real gains (4.4x-5.8x on ARM).
- You can build with -Ofast -ffast-math (or accept its semantics) and don't need bit-exact/IEEE-754-strict results — max observed diff vs libm is ~1.2e-11.
- You want a single small MIT-licensed C99 source pair to vendor directly into a build rather than link a shared library.
- You only need sin/cos/sincos/tan/cot/sinc acceleration, not asin/acos/atan, which just forward to libm here.

**Skip it when:**
- Small arrays (N <= 10,000): the README's own ARM table shows only 1.0x-2.56x there, and x86 has no per-size table at all, only headline chart images.
- You need strict IEEE-754 semantics or bit-reproducible output — default build flags are -Ofast -march=native -ffast-math.
- You need float32/single-precision (fabe13_sinf, etc.) — listed only on the roadmap, not implemented.
- You need an actively maintained or independently reproduced benchmark — last commit 2025-04-20, zero GitHub issues, single-author README-only numbers, no CPU model given for any platform.
- You need accelerated asin/acos/atan — those symbols exist but call straight into system libm.

**Integration:** source-drop (fabe13.c + fabe13.h) or static lib via the provided CMakeLists.txt · none for the library itself; links libm (m) for the atan/asin/acos passthroughs and the reference benchmark, which also links rt on non-Apple platforms · C99 (CMakeLists sets C_STANDARD 99); CMake 3.15+ for the provided build; verified with Clang 14 and AppleClang 16.0 · x86-64 (AVX2+FMA baseline, optional AVX-512F via FABE13_USE_AVX512), aarch64 (NEON); scalar fallback elsewhere

**Vs siblings:** Pick FABE13 only if you want a tiny, MIT, two-file C sincos batch kernel to vendor and don't need rigor; SLEEF and VDT are the safer defaults for sin/cos vs libm since they carry more independent/peer-reviewed benchmarking, and trigno_simd_cpp is a closer weight-class alternative but also less scrutinized than SLEEF/VDT.

**Gotchas:**
- fabe13_atan, fabe13_asin, fabe13_acos sit next to the accelerated functions but the header/source say they 'use standard libm' — no speedup despite looking like part of the same API.
- FABE13_ENABLE_FAST_FP (opt-in compile define) sets FTZ/DAZ on the CPU's MXCSR, relaxing subnormal handling process-wide, not just for this library's own calls.
- The default build (build.sh, CMakeLists.txt) compiles everything, including the libm comparison loop inside the benchmark, with -Ofast -march=native -ffast-math, so relaxed FP semantics apply to both sides of the reported comparison.
- fabe13_get_active_implementation_name()/fabe13_get_active_simd_width() let you check which kernel (AVX-512F/AVX2/NEON/scalar) was actually selected at load time — worth calling once at startup to confirm you got a SIMD path, not scalar fallback.

**Status:** Stale: last commit 2025-04-20, zero open or closed GitHub issues (no community vetting); MIT-licensed and small enough to vendor (2 files, C99), but the LICENSE file only exists under fabe13-old/LICENSE so GitHub's own license badge reports none.

[repo](https://github.com/farukalpay/FABE) · [benchmark](https://github.com/farukalpay/FABE/blob/main/README.md)

##### fmath (herumi)  `C++`  `BSD-3-Clause`  `active`  `Tier C`

SIMD array-mode log/exp for float buffers, 9-19x faster than std::logf/std::expf via AVX2/AVX-512.

**Beats:** std::logf, std::expf (<cmath>) — On the project's own readme benchmark tables (average CPU cycles per 32 elements), fmath's array-mode logf_v/expf_v beat scalar std::log/std::exp array loops by 15.7x/18.5x on a Linux Xeon w9-3495X (AVX-512), 16.9x/19.5x on a Windows Core i7-1165G7 (AVX-512), and 9.4x/12.9x on a Windows Core i7-1255U without AVX-512; compiler and flags used for these numbers are not stated. The comparison code (test/log_v.cpp, test/exp_v.cpp), which loops std::log/std::exp over the same arrays, is public in the repo.

**How:** The log/exp kernels are not written as C++ that the compiler auto-vectorizes; they are generated ahead of time as raw x86 machine code by a Python script (src/gen_fmath.py) using the bundled s_xbyak assembler-generation library, emitting GAS (src/fmath.S) or MASM (src/fmath.asm) that gets assembled into libfmath. This gives hand-tuned SIMD kernels that process 8 (AVX2) or 16 (AVX-512) floats per instruction using a polynomial/lookup-table approximation (table size tunable via LOG_L), amortizing per-call overhead across the whole array in one pass. fmath_init(), run via a GCC constructor attribute or an MSVC CRT init-section hook before main(), auto-selects the AVX-512 kernel when the CPU supports AVX512F+DQ, else falls back to the AVX2 baseline.

**Use it when:**
- Hot loops applying std::logf/std::expf over float arrays with n >= 16 that can be laid out as contiguous src/dst buffers
- x86-64 targets guaranteeing AVX2; extra speedup available automatically on AVX-512F+DQ Xeons/desktops
- Single-precision-only workloads (audio, ML feature transforms, scientific arrays) where a fast SIMD approximation's accuracy is acceptable
- Throughput-bound batch processing rather than single-call latency, e.g. bulk activation functions or vectorized transforms

**Skip it when:**
- Calls with n < 16 elements — the readme explicitly states fmath's array functions are slower than std:: there
- Double precision needed — fmath.h declares only float (logf/expf) variants, no logd/expd in this version
- Scalar call sites that can't be restructured into array form, since the API has no single-value entry point of its own
- Platforms without AVX2 (older x86-64 chips, ARM/aarch64) — AVX2 is a hard minimum, not degraded gracefully further
- Projects wanting a small header-only drop-in — this ships as generated assembly built into a static lib, not header-only, despite include/fmath.h existing

**Integration:** static lib · bundled s_xbyak.py (codegen) and xbyak_util.h (runtime CPU feature detection); Python 3 to (re)generate src/fmath.S/.asm; no external runtime deps once built · C++20 (Makefile builds with -std=c++20, mk.bat with /std:c++20); GCC/Clang on Linux or MSVC cl on Windows · x86-64 with AVX2 required minimum; auto-upgrades to AVX-512F+DQ kernels if detected at startup; no ARM/aarch64 support documented

**Vs siblings:** Among siblings, VDT and SLEEF also cover exp/log but at per-call scalar latency (VDT: ~2.8-12.8x vs libm) or double precision; fmath is narrower (float32 logf/expf only, array-mode only) but shows the largest claimed log/exp speedup (9.4-19.5x) because it measures bulk array throughput on AVX2/AVX-512, not single calls. Pick fmath when you specifically need bulk float32 log/exp over large contiguous arrays on x86-64 and can restructure call sites into array form; pick VDT/SLEEF/FastMath C++ instead for scalar call sites, double precision, or a broader function set (sin/cos/pow, etc.).

**Gotchas:**
- Dispatch can be pinned to the AVX2 kernel with the FMATH_CPU=avx2 environment variable, and the AVX-512 log variant switched to the lower-max-error 'tq' form with FMATH_LOG=tq
- No LICENSE file exists in the repo (GitHub's detector reports license: null); BSD-3-Clause is only stated in readme.md and the fmath.h header comment
- This is a rewrite that is explicitly not backward compatible with the older single-header fmath.hpp/Xbyak-JIT version; a since-fixed NaN bug (exp(89.0f), issue #14) was reported and patched against that old version, not this one
- Benchmark numbers are cycles-per-32-elements on specific CPUs; the readme does not state which compiler or flags produced them

**Status:** Actively maintained (last commit 2026-08-31, 244 stars, 36 forks) and BSD-3-Clause per readme/header, but there is no standalone LICENSE file, and this version is a non-backward-compatible rewrite of the older fmath.hpp/Xbyak-JIT API, so old issues and usage examples don't carry over.

[repo](https://github.com/herumi/fmath) · [benchmark](https://github.com/herumi/fmath/blob/master/readme.md)

##### LibRapid  `C++`  `MIT`  `stale`  `Tier C`

Templated C++20/23 array/tensor library with SIMD, OpenMP, CUDA and OpenCL backends; beats naive std::vector loops on elementwise math.

**Beats:** std::vector (nested-loop elementwise array/matrix operations) — First-party dev.to benchmark: elementwise res = aa*bb-cc on 1000x1000 double arrays, run repeatedly (~15,000 iterations), averaged 1.589ms/iteration for naive nested std::vector<std::vector<double>> loops vs 284.405us/iteration for LibRapid's Array, a ~5.59x ratio (the page's '558.71%' is that ratio expressed as a percentage, not '558.71% faster'). Measured on MSVC 19.33 with default project settings, AMD Ryzen 9 3950X, Windows 10 Pro, with LibRapid's 'Optimise Small Arrays' option off.

**How:** Elementwise expressions like aa * bb - cc are built as an expression tree and evaluated in one fused pass instead of allocating a temporary per operator, then dispatched to SIMD kernels (via the bundled Vc library) and OpenMP threads, or offloaded to CUDA/OpenCL/BLAS backends chosen with a template parameter. Linear-algebra expressions get compile-time rewriting into a single BLAS-style call, e.g. dot(3*a, 2*transpose(b)) becomes one GEMM with alpha/beta/transpose flags folded in. The one verified benchmark compares this fused, vectorized path against naive triple-nested std::vector<std::vector<double>> loops, which allocate a temporary per operator and get no fusion.

**Use it when:**
- Elementwise or linear-algebra-heavy numeric code currently written as nested std::vector loops, on x86-64 with AVX/SSE
- Willing to standardize on one array/tensor type across CPU, CUDA and OpenCL backends via a template parameter instead of separate GPU code paths
- C++20/23 toolchain available and OK pulling in a CMake build with several optional native dependencies (fmt, Vc, CLBlast, pocketfft, OpenBLAS, MPIR/MPFR, FFTW)
- Want BLAS-backed GEMM, FFT, complex/multiprecision arithmetic and NN activation functions from one library instead of assembling Eigen + FFTW + Boost.Multiprecision
- Prototyping or research code where a small, actively-evolving (though currently stalled) single-maintainer library is an acceptable risk

**Skip it when:**
- Need a drop-in replacement for std::vector/std::valarray: requires rewriting to lrc::Array<T> and its own Shape/indexing API, not a header swap
- Need OpenCL on Apple Silicon: issue #245 (open since 2023) tracks OpenCL support on macOS Mx as unresolved
- Rely on array slicing or generic array views: slicing (#139) and OpenCL GeneralArrayView (#253) are both open and labeled 'Requires Rewrite' since 2023
- Need automatic differentiation or trig functions to be bug-free: open issues from Aug 2025 report bugs in the AD product-rule implementation (#273) and in trig functions (#270), filed the week before the project's last commit
- Need active maintenance: solo student-maintainer project, last commit 2025-08-21, 15 open issues including 4 unresolved bugs filed just before that final commit

**Integration:** source-drop, CMake build (not header-only — CMakeLists globs .hpp under librapid/include plus .cpp/.cxx under librapid/src and cxxblas into a compiled target) · bundled submodules: fmt, Vc (SIMD), pocketfft, scnlib, CLBlast, Jitify; optional external: OpenMP, CUDA, OpenCL, OpenBLAS, MPIR, MPFR, FFTW, toggled via CMake options · C++20 minimum (CMake enforces this with a FATAL_ERROR check), C++23 used by default when built standalone; CMake >= 3.16 · x86-64 primary target (bundles Vc SIMD, LIBRAPID_NATIVE_ARCH on by default); Linux/macOS/Windows for CPU backend; CUDA and OpenCL backends optional and platform-gated, with OpenCL on Apple Silicon macOS unresolved (issue #245)

**Vs siblings:** Pick LibRapid over the sibling scalar-math libraries (SLEEF, VDT, fmath, trigno_simd_cpp, FABE13-HX, fast_math_cpp) when the need is a whole array/tensor container with fused elementwise expressions and optional GPU backends, not a faster std::sin/exp/log drop-in; pick Axiom instead if the goal is specifically an Eigen-compatible elementwise-math replacement, since Axiom benchmarks against Eigen3's array ops rather than raw std::vector loops.

**Gotchas:**
- 'Optimise Small Arrays' is a separate opt-in CMake option (LIBRAPID_OPTIMISE_SMALL_ARRAYS, OFF by default and OFF in the published benchmark), so small-array performance without it is untested by the cited numbers
- The benchmark's std::vector baseline is naive nested loops, not std::valarray or a vectorization-friendly std::transform/std::reduce pipeline, so the measured ratio likely overstates the gap versus a tuned STL baseline
- Array slicing and generic array views are flagged 'Requires Rewrite' in open issues (#139, #253) rather than treated as stable
- The top-level CMakeLists forces BUILD_SHARED_LIBS off on Windows, so shared-library builds aren't exercised on that platform

**Status:** Stale: solo student-maintainer project, last commit 2025-08-21, with 4 unresolved bug reports (autodiff product rule, indexing, trig functions, CUDA typo) filed the week before that last commit; MIT-licensed, but its CMake build with multiple optional native/GPU dependencies makes it a heavier vendor than a header-only library.

[repo](https://github.com/LibRapid/librapid) · [benchmark](https://dev.to/librapid/writing-faster-shorter-code-with-librapid-38lf)

##### NumKong (formerly SimSIMD)  `C++`  `Apache-2.0`  `active`  `Tier C`

Header-only SIMD kernel library beating GCC's auto-vectorized f16 loops in dot product and distance metrics 20-118x.

**Beats:** hand-written C++ dot-product/reduction loop, semantically equivalent to std::inner_product / std::transform_reduce, auto-vectorized by GCC 12 -O3 — On Intel Sapphire Rapids, single-threaded, NumKong's f16 kernels beat a scalar f16 loop auto-vectorized by GCC 12 (-O3 -march=native -ffast-math per the author's blog; flags not stated in the README itself) by 31x (inner product), 20x (cosine distance), 36x (squared Euclidean distance), and 118x (Jensen-Shannon divergence), per the README's first-party 'Auto-Vectorization & Loop Unrolling' table. This is not a benchmark against a literal std::inner_product/std::transform_reduce call.

**How:** Runtime CPU-feature dispatch selects a kernel per architecture (AVX-512-FP16, F16C, SVE, VNNI, AMX/SME) instead of relying on the compiler to auto-vectorize a scalar loop, and low-precision types get algorithmic transforms (lookup tables, algebraic domain shifts, widened-accumulator FMA) that scalar auto-vectorization does not synthesize. Masked loads (e.g. _mm512_maskz_loadu_ps, svld1_f32) replace the usual unrolled-body-plus-scalar-tail pattern, so remainder elements run the same arithmetic path as the SIMD body. The library deliberately avoids source-level loop unrolling, leaning on out-of-order execution and register renaming instead, to control binary size and compile time across 1,500+ kernel endpoints.

**Use it when:**
- Single- or half-precision (f16/bf16/e4m3) dot product, cosine distance, squared Euclidean, or Jensen-Shannon divergence over vectors, where GCC/Clang auto-vectorization of a scalar loop is the realistic alternative
- Need mixed-precision accumulation (f16->f32, i8->i32) to avoid the silent overflow a naive same-type reduction would hit
- Cross-platform kernels wanted from one header-only source: x86 (AVX2/AVX-512), Arm (NEON/SVE), RISC-V, WASM
- Caller already manages its own threading and wants a numerics layer with no hidden thread pool
- Small binary footprint matters (Python wheels, npm, Rust crates) versus linking a full BLAS

**Skip it when:**
- Need a literal drop-in for std::inner_product/std::transform_reduce call sites — the API differs and requires rewriting
- f32-only workloads on GCC: GCC already auto-vectorizes plain float loops reasonably well (3,810 K/s in the README's own f32 row), so the large multipliers shown are f16-specific, not universal
- Trigonometric/element-wise kernels (sin/cos/atan): the README only benchmarks those against NumKong's own scalar reimplementation, not against std::sin/cos, so no verified std:: comparison exists for that portion
- Extreme-magnitude inputs through the serial fallback path: open bug (#384) shows nk_euclidean_f64_serial returns 0 after fp64 overflow
- Need C++ exceptions for error handling: the library passes by pointer and does not throw

**Integration:** header-only · none for the core C/C++ headers; pthreads (via CMake's Threads package) for optional threading helpers · C++20 for the C++ layer, C99 for the C layer (include/README.md); CMake for prebuilt/shared-lib builds · x86-64 (SSE/AVX2/AVX-512/F16C/VNNI), Arm (NEON/SVE, AMX/SME on supporting chips), RISC-V, LoongArch, Power, WebAssembly; Linux, macOS, Windows, Android for the C/C++ package

**Vs siblings:** Pick NumKong over the trig-focused siblings (SLEEF, FABE13-HX, fmath, VDT, fast_math_cpp, trigno_simd_cpp) when the workload is dot-product/distance/reduction linear algebra rather than elementwise transcendental functions, since those all target std::sin/cos/exp/log while NumKong's verified numbers here cover inner product, cosine distance, squared Euclidean, and JS divergence. Pick Axiom or LibRapid instead when a tensor/array-expression API is wanted rather than a flat kernel-call API.

**Gotchas:**
- Open bug: nk_euclidean_f64_serial returns 0 instead of the correct distance after fp64 overflow on extreme-magnitude inputs (issue #384, reproduced on v7.8.2)
- macOS arm64 Python wheel reported loading a second libomp runtime and crashing alongside PyTorch (issue #373), despite the core README's 'no hidden thread pool' claim — appears tied to an optional/bundled component, not the header-only C++ core
- nk.moments reported ~30x slower on N-D arrays than on a flattened 1D view of the same data (issue #336) — memory layout matters for the reduction kernels
- No exceptions: errors are communicated by return value/pointer, not C++ exceptions

**Status:** Actively maintained (default-branch HEAD commit 2026-09-01, ~1,894 stars, not archived) and Apache-2.0 licensed; the header-only C/C++ core is copyable/vendorable on its own. The project renamed from SimSIMD to NumKong, and github.com/ashvardanian/SimSIMD now redirects to github.com/ashvardanian/NumKong.

[repo](https://github.com/ashvardanian/SimSIMD) · [benchmark](https://github.com/ashvardanian/SimSIMD/blob/main/README.md)

##### xsimd  `C++`  `BSD-3-Clause`  `active`  `Tier D`

Header-only C++ SIMD abstraction: portable batch<T,Arch> type replaces scalar loops across x86/ARM/RISC-V/WASM.

**Beats:** std::transform / scalar loops — No numeric benchmark is published anywhere in the repo, docs, or README. The repo's benchmark/ directory (main.cpp, xsimd_benchmark.hpp) is a Google-Benchmark-style harness that times scalar loops against xsimd batches, but no results are committed or published, so 'faster than scalar/std::transform' is an unverified qualitative claim, not a measured number against any specific compiler, flag set, or hardware.

**How:** It compiles operators and math functions directly to the target ISA's real SIMD instructions instead of relying on the autovectorizer or scalar code, via either an explicit Arch template parameter or auto-selection based on compiler flags (e.g. -mavx2). The vectorized math functions (exp/log/trig/pow) are lightweight polynomial-approximation implementations inherited from the now-deprecated boost.SIMD project. xsimd::dispatch() adds runtime ISA dispatch so one binary can pick the best available instruction set at startup.

**Use it when:**
- Tight numeric kernels applying the same arithmetic/math op over large arrays of floats/doubles/ints
- Need one portable source across x86-64, ARM (NEON/SVE), RISC-V (RVV), WASM, PowerPC (VSX), LoongArch, or IBM z, without hand-written per-ISA intrinsics
- Want vectorized exp/log/trig/pow without trusting the compiler's autovectorizer
- Header-only vendoring is acceptable (no separate build/link step)
- Need runtime dispatch across multiple ISAs from a single binary via xsimd::dispatch()

**Skip it when:**
- Workload sizes rarely align to the SIMD width and remainder-loop bookkeeping is unwanted overhead
- Using -ffast-math with log() on AVX2 pre-fix builds: issue #1264 showed materially wrong results (now closed/fixed, but confirm the fix is in your pinned version)
- Chained math-function expressions (e.g. sqrt((cos+sin)/2) over 1e8 elements): issue #880 is an open, unresolved report of xsimd being ~3x slower than the scalar std:: equivalent on AVX2 for that pattern
- You need a published, reproducible benchmark before committing — none exists in this repo (evidence tier D, no numbers in README/docs/benchmark/)
- Toolchain is older than GCC 10 / Clang 16 / MSVC 2022, or pre-C++17

**Integration:** header-only · none (optional: xtl, only if you enable XSIMD_ENABLE_XTL_COMPLEX for xtl::xcomplex constructors) · C++17; GCC 10+, Clang 16+, MSVC 2022+ · x86-64 (SSE2..AVX512, FMA3/FMA4), ARM (NEON, NEON64, SVE), WebAssembly (WASM), PowerPC64 (VSX), RISC-V (RVV), LoongArch64 (LSX/LASX), IBM z/Architecture (VXE)

**Vs siblings:** no siblings catalogued yet

**Gotchas:**
- log() on AVX2 compiled with -ffast-math produced wrong results (issue #1264); reported closed/fixed but verify against your pinned xsimd version
- Compound math expressions (cos/sin/sqrt combined) were reported ~3x slower than the equivalent scalar std:: code on AVX2 over 1e8 elements (issue #880, open, unconfirmed by maintainers) — benchmark your actual expression before assuming a win
- Pinning an explicit Arch template parameter (e.g. batch<double, xsimd::avx2>) fails to compile on hardware lacking that ISA; leave Arch unset to auto-select based on compiler flags for portability
- Caller owns tail-loop correctness: batch operations only cover size - (size % simd_size) elements

**Status:** Actively maintained (last commit 2026-09-22; 2.8k stars; used by Firefox, Apache Arrow, Pandas, KDE Krita, Meta Velox, Milvus, and Pythran); BSD-3-Clause and header-only, so it is trivial and low-risk to vendor even without ongoing upstream engagement.

[repo](https://github.com/xtensor-stack/xsimd)

#### number-parsing-formatting

##### c4core (charconv/xtoa/atox module)  `C++`  `MIT`  `active`  `Tier C`

Low-level C++ utility library whose charconv module (xtoa/atox) beats std::to_chars and std::from_chars on integers.

**Beats:** std::to_chars, std::from_chars — On Linux with g++11.2 Release, c4core's own CI microbenchmark (bm/bm_charconv.cpp) shows c4::to_chars beating std::to_chars by 1.07x-2.44x and c4::from_chars beating std::from_chars by 1.05x-1.54x across 8/16/32/64-bit signed and unsigned integers, measured in MB/s. Float/double comparisons exist only as PNG charts from a separate g++12.1 (Linux) / VS2019 (Windows) run; no CPU or hardware is disclosed for either run.

**How:** For integers, c4core uses its own digit-counting and decimal-digit extraction routines (digits_dec()/write_dec()/read_dec()) with no locale handling, format-flag dispatch, or allocation, avoiding overhead present in libstdc++/MSVC STL's std::to_chars/from_chars. For float/double, c4core does not implement its own parsing algorithm: from_chars for floating types is answered by the bundled fast_float submodule (already catalogued separately) when C++17 and the fastfloat option are enabled (the default), so the float speedup is fast_float's algorithm, not original c4core code.

**Use it when:**
- Hot loops converting many fixed-width integers (u8-u64, i8-i64) to/from decimal ASCII, e.g. log lines or serialization formatting
- Already using c4core/rapidyaml or want one low-level utility library instead of many point solutions
- Comfortable with a substr/csubstr buffer API instead of std::to_chars' pointer-pair + result-struct signature
- Building on a toolchain without full C++17 <charconv>: c4core still gets integer speedups on C++11, and floats route through fast_float
- Want MIT-licensed source that can be vendored as a single amalgamated header (tools/amalgamate.py)

**Skip it when:**
- Only need fast float/double parsing: use fast_float directly, since c4core's float path is just fast_float underneath with extra library weight on top
- Want a minimal, single-purpose charconv library: c4core pulls in a large general-purpose utility library (span, allocators, error handling, etc.)
- Need the exact std::to_chars/from_chars call signature for drop-in replacement without call-site changes
- Need independently-verified numbers: only the project's own README/CI benchmarks exist (evidence tier C), with no hardware/CPU disclosed
- Targeting old MSVC (<2019): std::to_chars/from_chars interop is unavailable, and the README's text table itself is from an older g++11.2 run vs. current CI's newer compilers

**Integration:** source-drop (CMake subproject/static lib) or single-header via tools/amalgamate.py · fast_float (bundled git submodule, used for float/double parsing when C++17 + fastfloat option enabled, the default); sg14 inplace_function (BSL-1.0) and debugbreak (BSD-2-Clause) are bundled for other parts of c4core, not charconv itself · C++11 minimum for the library and integer xtoa/atox; C++17 with MSVC2019+/GCC or a compiler exposing <charconv> is needed to enable the std::to_chars/from_chars interop path · x64, x86, arm, aarch64, wasm (emscripten), ppc64le, s390x tested in CI; bare-metal, RISC-V and LoongArch reported working via issues/PRs but not in the official CI matrix

**Vs siblings:** Pick c4core's charconv when you already want its broader utility library (substr, span, error handling) and only need integer to/from-decimal speed; its documented integer wins (1.05x-2.44x over std) are smaller than Boost.Charconv's or rigtorp/CharConv's claimed multiples, so choose one of those instead — or fast_double_parser/fast_float — if isolated charconv or float-parsing performance alone is the goal.

**Gotchas:**
- Requires cloning with --recursive (or `git submodule update --init`) for the cmake/, fast_float, and debugbreak submodules; the amalgamation script is the alternative for header-only use
- On MSVC, c4core deliberately disables std::from_chars in favor of fast_float ('prefer fast_float with MSVC'), so float from_chars comparisons on Windows are effectively fast_float vs. an MSVC STL that also uses similar techniques internally
- A static-assertion failure in charconv.cpp on VS2019 was reported (issue #19, closed as duplicate in 2020) — worth checking current MSVC versions before relying on it
- Float/double results in the README exist only as PNG charts (g++12.1 Linux / VS2019 Windows), not in the text MB/s table, which covers integers only

**Status:** Actively maintained (last commit 2026-09-03, ~149 stars); MIT-licensed core with permissively-licensed bundled dependencies (fast_float, sg14 BSL-1.0, debugbreak BSD-2-Clause), so it is safely copyable/vendorable, including via the single-header amalgamation script.

[repo](https://github.com/biojppm/c4core) · [benchmark](https://github.com/biojppm/c4core/blob/master/README.md)

##### CharConv.h (rigtorp)  `C++`  `MIT`  `stale`  `Tier C`

Header-only base-10 int32/int64 to/from-string conversion; beats stringstream, to_string, atoi/strtol, stoi.

**Beats:** iostreams (std::stringstream); std::to_string; std::stoi/atoi/strtol — In-repo Google Benchmark dated 2017-12-26 on a Xeon E5-2620 v4 (compiler/flags not disclosed): to_chars ran 9-20ns vs sprintf 73-87ns, std::to_string 76-90ns, and std::stringstream 34-55ns; checked from_chars ran 9-19ns vs atoi/strtol 14-28ns and std::stoi 16-29ns; from_chars_unchecked ran 4-10ns. No std::to_chars/std::from_chars comparison exists in the repo.

**How:** to_chars precomputes the exact digit count with a clz-based bit-length-to-decimal-digits formula (__builtin_clz/__builtin_clzll against a static power-of-10 table) so it writes straight into a correctly sized span instead of a scratch buffer plus reversal or a strlen pass, then emits digits back-to-front via repeated /10, %10. from_chars accumulates digits with __builtin_mul_overflow/__builtin_add_overflow so overflow detection adds no separate check pass; a from_chars_unchecked variant skips overflow checks for a further speedup. Everything is noexcept, constexpr, and hinted with __builtin_expect.

**Use it when:**
- Hot loops converting many 1-9 digit signed/unsigned 32/64-bit integers to base-10 text (log lines, CSV/JSON emitters, wire protocols).
- Parsing base-10 integers with overflow detection but without exceptions or locale overhead (from_chars).
- Trusted, pre-validated input where the unchecked from_chars_unchecked path's extra speed is worth skipping validation.
- You already have a fixed buffer/pointer and want to skip std::to_string's allocation or stringstream's formatting machinery.
- GCC/Clang-only target where vendoring one ~200-line, zero-dependency header is acceptable.

**Skip it when:**
- Need floating-point to_chars/from_chars — not implemented at all here.
- Need MSVC support — code depends on GCC/Clang builtins (__builtin_clz, __builtin_clzll, __builtin_mul_overflow, __builtin_add_overflow) with no MSVC equivalents provided.
- Need real interchangeability with std::to_chars/std::from_chars (exact result types, base 2-36, std::chars_format) — this API is similar but distinct, not a swap-in.
- Want the fastest available integer formatter — sibling libraries (jeaiii/itoa, c4core) use digit-pair lookup tables and report larger margins; this repo never benchmarks against them or against actual std::to_chars.
- Expect upstream maintenance — no commits, issues, or PRs since the 2023-09-25 push; algorithm and code are unchanged since the 2018 copyright.

**Integration:** header-only · none for consumers (vendors Google Benchmark and Catch2 only for the repo's own benchmark/test binaries) · C++17 (if constexpr); relies on GCC/Clang builtins, exact minimum GCC/Clang version not documented · any GCC/Clang target (x86-64, aarch64, etc.); MSVC not supported, no intrinsic fallback provided

**Vs siblings:** Pick this over Boost.Charconv or c4core when you want a zero-dependency, ~200-line header covering only base-10 32/64-bit integers and don't need float support; pick Boost.Charconv or c4core instead when you need floats or an actual std::to_chars/from_chars head-to-head, since this repo never benchmarks against std at all.

**Gotchas:**
- from_chars_unchecked skips overflow validation entirely — only safe on pre-validated input.
- to_chars_result/from_chars_result are rigtorp's own types, not std::to_chars_result/std::from_chars_result — don't assume interchangeability.
- Caller must size the output buffer itself (worst case 11 bytes for int32/uint32 with sign, 20 for int64/uint64); no allocating convenience wrapper is provided.
- Compiler-builtin dependent (__builtin_clz/__builtin_mul_overflow/etc.) — porting off GCC/Clang requires substituting equivalents.

**Status:** Stale since the last push on 2023-09-25 (0 open issues/PRs, no recent activity) but MIT-licensed, header-only, and small enough to vendor as-is.

[repo](https://github.com/rigtorp/CharConv) · [benchmark](https://github.com/rigtorp/CharConv/blob/master/README.md)

##### jeaiii/itoa  `C++`  `MIT`  `abandoned`  `Tier C`

Header-only branchless integer-to-ASCII conversion, ~7-9x faster than sprintf/MSVC _itoa, ~1.6-1.8x vs {fmt}.

**Beats:** sprintf (C standard library, MSVC CRT) and MSVC _itoa/_ui64toa in the README's release charts; {fmt} in the godbolt table. No std::to_chars comparison exists. — Author-run release-mode benchmark (Visual C++ 2019, win64, hardware unstated) using jeaiii's fork of miloyip/itoa-benchmark shows, on uniform-random-digit-length inputs, u32toa at 20.5 cycles vs sprintf's 160.5 and MSVC _ui64toa's 174.5 (~8x), and vs {fmt}'s 33.5 (~1.6x); u64toa is 32.75 cycles vs sprintf's 226.75 and MSVC's 312 (~7-9x), and vs {fmt}'s 58 (~1.8x). A separate debug-built Google Benchmark on godbolt, which the author explicitly disclaims as not a good benchmark, shows 10.2ns vs {fmt}'s 16.6ns. No comparison against std::to_chars is published anywhere in the repo.

**How:** Uses a per-digit-length unrolled code path chosen by a small binary-search branch tree on the number's decimal length, so short numbers take fewer branches than long ones instead of looping once per digit. Digits are produced two at a time via fixed-point multiply-shift arithmetic against a 100-entry '00'-'99' ASCII lookup table, avoiding per-digit division; only one true integer divide is used, to split 64-bit values into two 8-digit halves. The fixed-point constants follow the classic multiply-by-2^k/10^n itoa trick, refined using the mathematical analysis in dragonbox author Junekey Jeon's write-up, which removed a redundant addition.

**Use it when:**
- Hot paths that serialize many plain base-10 integers to text (logging, JSON/CSV encoders, protocol formatting) on MSVC, clang, or gcc
- Fixed 8/16/32/64-bit integer types where you control the destination buffer size and will add the null terminator yourself
- Workloads with uniform or skewed digit-length distributions (IDs, counters) where branch-prediction-unfriendly random lengths matter
- Need a single self-contained, zero-dependency header (not even <cstdint>) that works from C++11 up, easy to vendor
- You're comfortable auditing/patching abandonware yourself rather than depending on upstream maintenance

**Skip it when:**
- Need floating-point-to-string conversion; integers only, no float/double support at all
- Need std::to_chars' API contract: error_code / bool success return, [first,last) bounds-checked span; this header has neither
- Need guaranteed-correct output without your own verification: the repo has shipped at least two silent, large-magnitude correctness bugs on big 64-bit inputs (issues #12, #18), both fixed only because users noticed
- Want zero-padding or fixed-point/decimal formatting; explicitly requested in issue #15 and not implemented
- Need a plain-C API; this is C++ template code with no official C binding (issue #10 still open, unresolved)

**Integration:** header-only · none · C++11 (compiles on clang, MSVC, and gcc per README) · any (no architecture-specific intrinsics in the header; author's benchmarks are x86/x64 Windows/VC2019)

**Vs siblings:** Pick jeaiii/itoa over CharConv.h (rigtorp) or c4core when you want the smallest possible single header with zero includes and don't need from_chars/parsing or float formatting. Pick c4core or Boost.Charconv instead when you need a maintained, std::to_chars/from_chars-compatible API with float support and bounds-checked spans.

**Gotchas:**
- Output is not null-terminated; caller must write '\0' at the returned pointer (see test/main.cpp's to_string wrappers)
- No bounds checking: caller must size the buffer for the worst case (up to 20 digits + sign for 64-bit) or risk a buffer overflow
- History of silent large-magnitude correctness bugs on 64-bit inputs (issue #12: off by 10,000,000 on a 19-digit value; issue #18: wrong values near a specific 11-digit range), both fixed before the final 2022-11-24 commit but with no maintainer left to catch new regressions
- Repo contains multiple header variants (include/itoa/jeaiii_to_text.h is current; itoa/to_text_from_integer.h and itoa/int_to_chars_jeaiii.h are older macro-based versions) — include the one under include/itoa/, not the legacy ones

**Status:** Abandoned since its last commit on 2022-11-24 with no tagged releases; MIT-licensed and small enough (~200-line single header) to vendor and patch yourself, but its history of correctness bugs on large 64-bit values means you should add your own exhaustive round-trip test before trusting it in production.

[repo](https://github.com/jeaiii/itoa) · [benchmark](https://github.com/jeaiii/itoa/blob/main/README.md)

##### milo Grisu2 (header-only, via miloyip/dtoa-benchmark)  `C++`  `MIT`  `abandoned`  `Tier C`

Header-only Grisu2 double-to-string routine; fastest entry in its author's own benchmark, beating std::ostringstream and sprintf().

**Beats:** std::ostringstream (iostreams); page's headline ratio is vs sprintf() — On the benchmark's own RandomDigit case (1,000 random doubles with 1-17 significant decimal digits, minimum of 10 trials x 100 iterations each), milo averaged 138.021 ns/conversion versus sprintf's 1256.376 ns (9.10x, the page's own figure) and versus std::ostringstream's 2,778.748 ns (~20.1x, derived from the same table), measured on an Intel Core i7 920 @ 2.67GHz with Visual C++ 2013, Windows 64-bit, release config.

**How:** Implements Loitsch's Grisu2 algorithm: converts the double into a DiyFp (64-bit significand plus binary exponent), then generates digits using only fixed-width integer/bit arithmetic against a precomputed table of cached powers of ten (GetCachedPower), avoiding the arbitrary-precision bignum fallback that fully-correct converters like Grisu3-based double-conversion sometimes need. A 200-byte two-digit lookup table (GetDigitsLut) speeds up decimal digit and exponent formatting in WriteExponent/Prettify. Being Grisu2 rather than Grisu3, it can occasionally emit a decimal one digit longer than the true shortest representation in exchange for never invoking the slow bignum path.

**Use it when:**
- Hot double-to-ASCII serialization paths (e.g. JSON/log writers) on x86/x86-64 where you control the toolchain (MSVC or GCC/Clang) and can vendor a single header.
- You've already excluded NaN/Inf upstream and can size and validate the output buffer yourself.
- You want the fastest Grisu-family converter shown in this specific benchmark and are willing to re-benchmark it against double-conversion/fpconv on your own hardware and compiler rather than trust the 2013-era, i7-920/VC2013 numbers.
- 'Almost always shortest' output (not the guaranteed-shortest of Grisu3+bignum) is acceptable for your format.

**Skip it when:**
- You need a std::to_chars-compatible signature (pointer-pair/span, error code, format flags) — this is a raw C-style buffer writer, not drop-in.
- You need guaranteed-correct NaN/Inf handling — the code only asserts !isnan/!isinf, which is compiled out under NDEBUG (undefined behavior in release).
- Your value distribution can hit the known unresolved out-of-bounds read in DigitGen (e.g. 0.020000000000000005, kappa = -14) — GitHub issue #7, filed 2016, still open as of 2026-09-24, caught by Clang ASan, no fix landed in this repo.
- You need an actively maintained dependency — repo has had no default-branch commits since 2020-04-27, and issue #18 explicitly asks the maintainer to transfer ownership because he isn't accepting pull requests.
- Target is a non-x86 platform — the fast paths use MSVC's _umul128/_BitScanReverse64 or GCC/Clang's __int128/__builtin_clzll on x86-64; other architectures fall back to an untested, unbenchmarked portable path.

**Integration:** header-only (source-drop from a benchmark repo; not distributed as a standalone package — must be extracted from src/milo/dtoa_milo.h) · none beyond the C/C++ standard library (assert.h, math.h, stdint.h); on MSVC it also pulls in a bundled msinttypes/stdint.h shim and <intrin.h> · not documented; the source itself only requires C++03-level syntax plus compiler intrinsics/extensions (MSVC any version with _umul128/_BitScanReverse64; GCC >=4.6 or Clang for __int128 on x86-64); portable fallback compiles with any C++ compiler · x86-64 optimized via MSVC or GCC/Clang intrinsics; portable C++ fallback for other compilers/architectures exists in source but is not covered by the published benchmark numbers

**Vs siblings:** Against fpconv (also Grisu2, 4.59x vs sprintf) and google/double-conversion (Grisu3+bignum fallback, 6.23x, always-shortest), milo is the fastest of the three on this same benchmark/hardware (9.10x vs sprintf) but carries the same Grisu2 not-always-shortest caveat as fpconv plus an unresolved OOB read that neither sibling has documented against it; pick milo only after your own benchmark confirms the throughput edge and you can tolerate or patch the DigitGen edge case, otherwise prefer double-conversion (more correctness testing, used in V8) or Boost.Charconv/c4core (independently benchmarked, actively maintained, std::to_chars-compatible APIs).

**Gotchas:**
- Open, unresolved bug (issue #7, filed 2016): certain values, e.g. 0.020000000000000005, cause an out-of-bounds read on the internal kPow10 table inside DigitGen (kappa = -14), caught by Clang AddressSanitizer.
- assert(!isnan(value)); assert(!isinf(value)) — with NDEBUG (release builds) these are no-ops, so NaN/Inf input is undefined behavior rather than a checked error.
- No buffer-size parameter or internal bound check; caller must supply a sufficiently large buffer with no guidance from the header on how large that needs to be.
- Issue #20 (wrong result for 16385.0, a rounding-direction bug in the cached-power exponent calculation) was fixed by the maintainer, closed on the same date as the repo's last commit (2020-04-27) — confirms the currently-read source no longer has that specific bug, but shows fixes were rare and reactive.

**Status:** Abandoned: no default-branch commits since 2020-04-27, and an open issue (#18) asks the maintainer to transfer ownership since he no longer accepts pull requests; MIT-licensed and small enough to vendor as a single header, but ships with at least one known, unresolved memory-safety bug (issue #7) that has sat open since 2016.

[repo](https://github.com/miloyip/dtoa-benchmark) · [benchmark](https://github.com/miloyip/dtoa-benchmark)

##### SSE2 itoa (Muła algorithm, via miloyip/itoa-benchmark)  `C++`  `MIT`  `stale`  `Tier C`

SSE2-vectorized itoa for uint32/int32/uint64/int64 in Milo Yip's benchmark repo; 25.51x faster than sprintf on 9-10 digit values.

**Beats:** sprintf (C stdio); std::ostringstream/std::to_string also tested but disabled by default with no numbers published on this page — On the repo's own README table (Core i7 920 @2.67GHz, Visual C++ 2013, Win64 release build), the SSE2 u32toa implementation averages 7.614 ns per call vs sprintf's 194.225 ns across the sequential 1-10 digit benchmark (100,000 reps/group, min of 10 trials) -- a 25.51x speedup, ahead of branchlut (23.04x) and countlut (19.57x) in the same table; std::ostringstream/std::to_string are compiled out by default (RUN_CPPITOA macro) and have no published numbers on this page.

**How:** For short values (<10^8 for u32, <10^16 for u64) the code falls back to the same digit-pair lookup table (gDigitsLut) used by the repo's lut/countlut/branchlut entries -- the SIMD path there is wrapped in #if 0 because, per the author's own comment, experiments found SSE2 slower in that range. For 9-10 digit u32 values and all u64 conversions it runs Wojciech Mula's SSE2 algorithm (Convert8DigitsSSE2): a chain of SIMD multiply-high/shift operations divides 8 decimal digits by powers of ten in parallel in a 128-bit register, packs the results into ASCII bytes with _mm_packus_epi16, then uses a movemask/ctz trick to trim leading zeros.

**Use it when:**
- Hot-path serialization of high-volume 32-bit or especially 64-bit integers to decimal ASCII (logging, JSON/CSV writers, wire protocols) where sprintf's format-string parsing is the bottleneck.
- Your integers are frequently large (9-10 digit uint32_t, or most uint64_t/int64_t values) -- the only range where this file's SIMD path actually runs instead of falling back to scalar/LUT code.
- x86 or x86-64 targets that guarantee SSE2 (default on effectively all x86-64 CPUs); no ARM or other-arch support needed.
- You're willing to hand-extract two files (sse2.cpp + digitslut.h) from a benchmark harness, strip the REGISTER_TEST macro/test.h dependency, and own buffer-size correctness yourself since there is no bounds checking.

**Skip it when:**
- You need a maintained, versioned library rather than one file inside a 10+-implementation benchmark shootout with issues and PRs open since 2016 and no formal releases.
- Non-x86 targets: the file compiles to nothing outside `#if defined(i386) || __amd64 || _M_IX86 || _M_X64`, with no portable fallback provided.
- Values are mostly 1-8 decimal digits -- the SIMD kernel is dead code there by the author's own admission, so you get the same LUT-pair scalar performance as branchlut/countlut without SSE2's added complexity.
- You need std::to_chars-style safety (returned end pointer, error reporting, no overflow) -- this API just writes to a raw buffer with zero bounds checking.
- You want the speedup verified independently or on current hardware -- the only published numbers are first-party, from a Core i7 920 (2010-era) with Visual C++ 2013, and the std:: baselines (ostringstream/to_string) were never enabled for this table.

**Integration:** source-drop · digitslut.h (200-byte const lookup table, in-repo); test.h is only needed for the REGISTER_TEST self-registration macro used by the benchmark harness and must be stripped/replaced to vendor standalone · not documented; source uses <cassert>, <stdint.h>, and <emmintrin.h> SSE2 intrinsics with no C++11-only syntax, so most C++ toolchains with SSE2 intrinsic support should compile it (published results used Visual C++ 2013) · x86/x86-64 only, guarded by #if defined(i386) || defined(__amd64) || defined(_M_IX86) || defined(_M_X64); requires SSE2 (baseline on all x86-64; needs explicit enabling on some 32-bit x86 toolchains); no fallback for other architectures in this file

**Vs siblings:** Most siblings in this category target floating-point/general charconv (Boost.Charconv, c4core, fast_double_parser, fpconv, double-conversion, milo Grisu2) or a broader iostream replacement (rigtorp CharConv, fast_io, stb_sprintf); pick this one specifically when you want a SIMD kernel for many-digit unsigned/signed 32- or 64-bit integers on x86 and are fine hand-extracting it from a benchmark harness -- jeaiii/itoa is the closer apples-to-apples sibling (also integer-only, from a similar shootout) but is header-only, scalar, and easier to vendor without SSE2 intrinsics.

**Gotchas:**
- Issue #8 (closed) flagged that i32toa_sse2/i64toa_sse2 previously computed `value = -value` on the most-negative int, which is signed-overflow UB and reportedly segfaulted on g++ 4.9.1; the code read this session already uses the recommended two's-complement fix (`u = ~u + 1`).
- No bounds checking: caller must size the buffer correctly (worst case ~11 bytes incl. sign/null for i32, ~21 for i64) or risk a buffer overflow.
- The vectorized 8-digit SSE2 kernel (Convert8DigitsSSE2) is dead code for u32toa values under 100,000,000 -- that branch is behind #if 0 with a comment that SSE2 measured slower there, so most 1-8-digit conversions actually run the same scalar/LUT-pair code as the branchlut/countlut entries, not SIMD.
- Uses 16-byte-aligned static constant tables (ALIGN_PRE/ALIGN_SUF macros); if copy-pasting only part of the file, bring the matching aligned constants along.

**Status:** Not a maintained library in its own right: it's one implementation file inside a community benchmark repo that still gets sporadic commits/PRs (last push 2025-02-10) but has open issues and PRs dating back to 2016 and no versioned releases; MIT-licensed and small (~250 lines plus a header), so it's cheap to vendor and re-audit yourself.

[repo](https://github.com/miloyip/itoa-benchmark) · [benchmark](https://github.com/miloyip/itoa-benchmark)

##### stb_sprintf (nothings/stb)  `C`  `MIT OR Unlicense`  `active`  `Tier C`

Single-header, public-domain sprintf/snprintf replacement claiming 4-35x faster formatting than MSVC 2008's CRT.

**Beats:** sprintf/snprintf (C runtime, MSVC/GCC CRT) — The library's own header (stb_sprintf.h, "PERFORMANCE vs MSVC 2008 32-/64-bit") reports first-party speedups against MSVC 2008's CRT sprintf, e.g. %f 7.3x/6.0x faster, %e 8.1x/6.0x, %g 10.0x/7.1x, %d 4.8x/4.0x, and a 512-char string format 35.0x/32.5x faster (32-bit/64-bit builds respectively); no CPU model, optimizer flags, or benchmark harness are given, and GCC's CRT is claimed qualitatively "even slower than MSVC" with no numbers.

**How:** It bypasses the CRT's generic, often locale-aware formatting machinery with hand-written, allocation-free integer/float-to-ASCII routines that feed a small internal buffer and a callback, so it never calls malloc and stays small enough to fit in cache (header states ~8K compiled with float support, ~4K without, vs. ~16K pulled in by MSVC's static sprintf). Float-to-string conversion uses an internal double-double (~105-bit) arithmetic scheme for round-trip-correct output without going through the CRT's arbitrary-precision or locale-sensitive dtoa path (documented in the header's FLOATS/DOUBLES section).

**Use it when:**
- Game/graphics/embedded C or C++ codebases that want a small, dependency-free, single-header drop-in for heavy sprintf/snprintf call volume
- Cross-platform code that wants one format-string dialect instead of juggling MSVC (%I64d) vs GCC (%lld) differences for 64-bit integers
- Formatting-heavy hot paths (many floats/ints or long strings per frame/tick) where CRT sprintf throughput is a known bottleneck
- Code-space-constrained targets (embedded, consoles) where ~8K of formatting code beats linking in a full CRT static sprintf (~16K per the header)
- Want built-in thousands separators or SI/JEDEC-suffix number formatting (%'d, %$d, %$$d) without hand-rolling it

**Skip it when:**
- Strict C-standard sprintf conformance is required: open issues document divergent behavior for '+'/' '/'0' flags on unsigned types, negative width via '*', and %n with non-default size (issues #1788-#1790, #1785, #1778)
- Format strings or precision values come from untrusted input: issue #1792 shows a buffer overrun via large integer precision (e.g. "%0.513x"), and issue #1963 shows stbsp_snprintf(buf, 0, ...) with a non-NULL buf writes one byte before the buffer -- both open, unpatched as of 2026-09-24
- You rely on the common "call with count=0 to get required length" idiom against a non-NULL buffer pointer -- that exact pattern triggers the #1963 OOB write
- You need independently benchmarked, modern numbers before committing: the header's speedup table is first-party, measured against MSVC 2008's CRT only, no CPU model or flags given (Tier C evidence)
- 16-bit int platforms are a target: issue #1779 is an open feature request, not currently supported

**Integration:** header-only · none (only <stdarg.h> and <stddef.h> from the C standard library) · C89/C99-compatible C or C++ compiler; no C++ standard required. Explicit shims for MSVC, GCC (>=4.8), and Clang (including ASan attribute handling) · any (portable C; explicit 32-/64-bit pointer-size detection for x86, x86-64, aarch64, ppc64, s390x)

**Vs siblings:** The catalogued siblings (Boost.Charconv, c4core, fast_double_parser, rigtorp CharConv, fpconv, double-conversion, milo Grisu2, itoa variants) are narrow number<->string converters that replace std::to_chars/from_chars or a single strtod/itoa call. stb_sprintf is scoped differently: it is a full printf-style format-string engine (mixed text plus args, width/precision, %n, etc.), so pick it when you need a drop-in-shaped replacement for whole sprintf/snprintf call sites -- especially in C or C-style C++ (game/graphics) code that already uses sprintf throughout -- rather than a targeted numeric conversion routine.

**Gotchas:**
- Two open, unresolved correctness/security bugs as of 2026-09-24: stbsp_snprintf(buf, 0, ...) with non-NULL buf writes one byte before the buffer (#1963); large integer precision like "%0.513x" overruns the internal conversion buffer (#1792)
- stbsp_set_separators() changes process-wide global state (comma/period), not thread-local or per-call
- Float insignificant digits differ from glibc/MSVC CRT output (documented in header) even though round-trip via atof is exact
- Several open issues catalog format-flag edge cases (nan/inf capitalization, %A case, negative precision crash) that diverge from strict C sprintf semantics

**Status:** Actively maintained (pushed 2026-08-02, part of the 34.7k-star stb collection, not archived) but has a cluster of open correctness/security issues, including two out-of-bounds-write bugs, unresolved as of 2026-09-24. Dual MIT/public-domain (Unlicense) licensed per the header's own license block, so it is trivially copyable and safe to vendor regardless of upstream fixes.

[repo](https://github.com/nothings/stb) · [benchmark](https://github.com/nothings/stb/blob/master/stb_sprintf.h)

#### ordered-maps-trees

##### boost::container::flat_set / flat_map  `C++`  `BSL-1.0`  `active`  `Tier C`

Vector-backed sorted set/map beating std::set on insert+remove at small sizes, up to ~256 elements.

**Beats:** std::set — A single-author 2014 blog benchmark (500,000 random insert-then-erase operations on int keys, -O3, compiler and hardware unstated) timed boost::container::flat_set against std::set across sizes 2-8192: flat_set was ~2.5x faster at size 2, ~1.1x faster at 128, then lost ground from 256 elements up, with std::set ~13.4x faster at 8192.

**How:** Core technique is cache-friendly linear storage: a sorted vector-like sequence (default plain vector, or a user-supplied vector-like container) gives contiguous memory and random-access iterators, avoiding the pointer-chasing and per-node allocation of a red-black tree. For small containers this locality and lack of per-element allocation outweighs the O(n) shifting cost of insert/erase; std::set's balanced-tree structure only pays off once n is large enough that O(log n) tree operations beat O(n) vector shifts (crossover around 128-256 elements per the cited benchmark).

**Use it when:**
- Sets/maps that stay small (roughly <=128-256 elements per container), even if there are many such containers
- Read-mostly or lookup-heavy workloads where iteration/cache locality matters more than mutation cost
- Cheap-to-move key types (ints, small PODs) where shifting on insert/erase is cheap
- Existing std::set/std::map code that can tolerate iterator/reference invalidation on mutation
- Memory-constrained code avoiding the per-node allocation overhead of tree containers

**Skip it when:**
- Large sets/maps (thousands+ elements) mutated frequently -- std::set was ~13.4x faster than flat_set at 8192 elements in the cited benchmark
- Code relying on iterator/reference/pointer stability across insert/erase -- flat containers invalidate on shift/reallocation
- Bulk one-at-a-time insertion of very large unsorted datasets -- GitHub issue #154 reports near-hang (100% CPU) inserting ~9M elements individually into flat_map
- Workloads needing guaranteed O(log n) worst-case insert/erase (latency-bounded mutation)
- Large or expensive-to-move key/value types, since every insert/erase move-shifts surrounding elements

**Integration:** header-only · Boost.Config, Boost.Move, Boost.Intrusive (ships as part of Boost; no separately compiled library) · C++03 baseline (README states C++03 support); has conditional code paths for C++11 features like initializer_list and variadic templates when available · any (portable C++, no architecture-specific code observed)

**Vs siblings:** Pick flat_set/flat_map over fast-containers, S+ tree, or tlx::btree when the working set stays small (roughly <=128-256 elements) and you want a true drop-in std::set/map replacement shipped with Boost and no extra dependency; the sibling B-tree/B+tree structures target much larger n (up to 10M-scale) and win precisely in the size range where flat_set has already crossed over to being slower than std::set.

**Gotchas:**
- Insert/erase invalidate iterators and references to elements after the mutation point (vector shift/reallocation), unlike std::set's per-node stability
- Underlying sequence container is swappable (e.g. stable_vector, static_vector, small_vector) -- use stable_vector for reference stability at the cost of contiguity
- One-at-a-time insertion of large unsorted data can effectively hang (see issue #154); prefer bulk/sorted-range construction to amortize shifting
- Provides random-access iterators, so generic code that dispatches on iterator category behaves differently than with std::set's bidirectional iterators

**Status:** Actively maintained as a core part of Boost (repo shows a commit dated 2026-09-23) and BSL-1.0 licensed, so it is freely copyable/redistributable with no licensing friction.

[repo](https://github.com/boostorg/container) · [benchmark](https://blog.fellstat.com/?p=376)

##### cpp-btree (Kronuz)  `C++`  `Apache-2.0`  `abandoned`  `Tier C`

Header-only B-tree replacement for std::map/set/multimap/multiset with C++17 try_emplace API and lower per-element memory.

**Beats:** std::map, std::set, std::multimap, std::multiset — The header comment (btree/btree.h, lines ~51-101) reproduces Google's original 2010 btree_bench table comparing the STL red-black-tree set/map against btree::set/map (node size 256) for int32, int64 and string keys/values, run on 'pmattis-warp.nyc (4 X 2200 MHz CPUs)': integer-key ops improve roughly 40-84% (e.g. set_int32_lookup 1160ns to 414ns, set_int32_fwditer 158ns to 26ns), string-key ops improve much less (set_string_lookup 1709ns to 1600ns, +6.38%) and two fifo benchmarks regress (set_string_fifo -61.01%, map_string_fifo -49.75%). No compiler, flags, or exact CPU model are given, and this repo ships no benchmark harness to reproduce the numbers.

**How:** Each node packs many keys/values into a fixed target size (256 bytes by default, tunable via the TargetNodeSize template parameter) instead of one value per red-black-tree node with three pointers plus color bit, so a lookup does several in-node comparisons per cache line touched rather than one pointer-chasing hop per comparison. The header's own comment attributes the win to better cache locality from this packing, not to a different asymptotic complexity — both are O(log n); a btree::set<int32_t> reportedly uses ~4.9 bytes/element total vs ~20 bytes for the red-black-tree set.

**Use it when:**
- Large in-memory ordered containers of small fixed-size keys (int32/int64) where memory footprint and cache-miss-bound lookup/insert/delete dominate
- Workloads with heavy forward iteration, where the header's own numbers show the largest gains (e.g. +83.54% on BM_set_int32_fwditer, +80%+ on int64/map variants)
- Call sites that don't retain iterators across mutation (short-lived iterators, no insert/erase while iterating elsewhere)
- Willing to vendor a small, unmaintained 3-file header rather than depend on absl::btree or another maintained B-tree
- Need per-instantiation control of node size for your specific key/value size

**Skip it when:**
- String or other expensive-to-move keys/values: gains shrink to single digits (+6.38% string set lookup, +1.16% string set insert) and fifo-pattern workloads regress (-61.01% set_string_fifo, -49.75% map_string_fifo) because rebalancing moves values between nodes
- Code that holds iterators across mutation — std::map's stable-iterator guarantee does not hold here; any insert/erase can invalidate unrelated iterators
- Need an actively maintained dependency: last commit 2021-01-08, one open unresolved bug (#2: assertion failure / later segfault reachable via operator[] -> try_emplace on a non-trivial value type) with zero maintainer response since it was filed in 2020
- Need heterogeneous/transparent lookup (is_transparent-style comparators) — requested in still-open issue #10, not implemented
- Need documented thread-safety guarantees — none are given anywhere in the headers; treat it as unsynchronized, same as std::map

**Integration:** header-only · none beyond the C++ standard library (<algorithm>, <functional>, <memory>, <iterator>, etc.) · C++11 minimum (variadic templates, forward_as_tuple, piecewise_construct used throughout); README targets C++17-style semantics (try_emplace); contains() only compiles under C++20 (#if __cplusplus > 201703L) · any — portable C++ template code; no SIMD intrinsics or platform-specific code in btree.h/map.h/set.h

**Vs siblings:** Pick cpp-btree over frozenca/BTree or fast-containers when you want a minimal, dependency-free, three-header vendor-in rather than a SIMD-tuned or hugepage-backed B-tree; its own numbers are far more modest (roughly 1.1-1.85x on integer-key ops, near-parity or a regression on strings) than frozenca/BTree's ~4.7-5.2x or fast-containers' ~2.1-4.8x, so prefer those when benchmark rigor and larger margins matter more than a small self-contained header.

**Gotchas:**
- Any insert/erase/rebalance invalidates every outstanding iterator on the container, not just ones pointing at removed elements — a real semantic break from std::map/std::set
- The header's own CAVEATS comment still points to a 'safe_btree' iterator-safe wrapper as a workaround, but no safe_btree.h ships in this repo — only btree.h, map.h and set.h exist
- Open issue #2 (filed 2020-09-24, still unresolved): assertion failure / later segfault in btree_node::construct_value, reached via operator[] -> try_emplace on a non-trivial value type; no maintainer response
- Values are moved within and between nodes on every rebalance, so an expensive-to-move value_type can make this slower than std::map despite the smaller footprint

**Status:** Abandoned since the last real commit on 2021-01-08, with one open, unanswered bug report from 2020; Apache-2.0-licensed, header-only, and small enough (3 header files) to vendor as-is despite the lack of maintenance.

[repo](https://github.com/Kronuz/cpp-btree) · [benchmark](https://github.com/Kronuz/cpp-btree/blob/master/btree/btree.h)

##### frozenca/BTree  `C++`  `Apache-2.0 WITH LLVM-exception OR BSL-1.0`  `stale`  `Tier C`

Header-only C++20 B-tree (BTreeSet/Map) with optional AVX-512 SIMD search, ~5x faster than std::set on int64 keys.

**Beats:** std::set — Author-run benchmark (gcc 11.2, -O3, libstdc++, CPU model not stated, 200 repeats) inserting/looking up/erasing 1M random std::int64_t keys: frozenca::BTreeSet (fanout 64, SIMD) averaged 175.5/197.8/211.3ms vs std::set's 907.1/961.9/990.0ms (~4.7-5.2x); the same test without the SIMD path averaged 204.2/221.0/249.8ms (~4.0-4.4x). For 1M std::string keys (length 1-50) the gap narrows to ~1.04-1.4x (e.g. insert 1519.6ms vs std::set's 1662.9ms).

**How:** Wider nodes (fanout 64 default, tunable) mean far fewer cache-line-missing pointer chases per operation than a red-black tree's one-key-per-node layout, and in-node key search can use either linear or binary search depending on a tunable threshold. For signed integer/float keys on AVX-512 hardware, an optional SIMD intrinsics path (macro-toggled, credited to Algorithmica's Static B-Trees) vectorizes the in-node comparison; the README's own figures show fanout-64 without SIMD is already ~4.0-4.4x over std::set, with SIMD adding roughly another 10-20% on top.

**Use it when:**
- Ordered set/map of primitive keys (int64, float) where insert/lookup/erase throughput matters more than per-node iterator stability, on x86-64 with AVX-512 for the full ~5x gain
- Need operations std::set lacks: O(log n) k-th/rank queries (kth/order), range enumerate()/erase_range(), or tree join()/split()
- Want an out-of-core ordered container: DiskBTreeSet/DiskBTreeMap memory-maps a file, which std::set cannot do at all
- Already on a C++20 toolchain (gcc 11.2+/MSVC 19.32+) and willing to vendor a small, header-only, currently unmaintained library
- Bulk-loading sorted or near-sorted ranges via insert_range(), which the README documents as faster than repeated single inserts

**Skip it when:**
- Code relies on std::set/map's iterator/reference stability across insert and erase elsewhere in the container — any insert/erase here can invalidate iterators anywhere in the tree
- Keys are std::string or other non-trivial-comparison types: measured speedup drops to ~1.04-1.4x because the SIMD path only covers signed integers/floats
- Need thread safety: concurrency is explicitly unsupported ('thread safety is not guaranteed'), no lock-free path implemented
- Stuck on C++17 or earlier, or need an actively maintained/widely-used dependency: last commit 2024-10-29, 249 stars, effectively a single-maintainer project with no open issues but no recent activity either
- Profiling debug builds: full-tree O(n) sanity checks run on every insert/erase/join/split unless a macro is disabled (per issue #3), so debug-build timings are misleading

**Integration:** header-only · none for library use; Catch2 only to build the test suite (per vcpkg.json) · C++20; README states verified against gcc 11.2 and MSVC 19.32. "There are currently no plans to support C++17 and earlier." Apple Clang compile errors were reported and fixed via PRs (issue #7) but Clang isn't in the README's stated verified-compiler list · x86-64 for the optional AVX-512 SIMD path; base header-only containers are architecture-agnostic. POSIX and Windows both supported for the memory-mapped disk variant

**Vs siblings:** Pick this over cpp-btree or tlx::btree when you specifically want std::set-compatible rank queries (kth/order), range enumerate()/erase_range(), tree join()/split(), or the disk-backed memory-mapped variant, none of which those siblings offer; prefer cpp-btree or tlx::btree instead if you need broader compiler/standard support, since this one hard-requires C++20 and its full headline speedup needs AVX-512.

**Gotchas:**
- Any insert or erase can invalidate iterators anywhere in the tree, because a B-tree node holds multiple keys, unlike std::set's one-key-per-node stability guarantee
- SIMD path only helps signed integer/floating-point keys and requires both a macro toggle and AVX-512 hardware; without it the README's own non-SIMD numbers show ~4.0-4.4x rather than ~5x
- DiskBTreeSet/DiskBTreeMap requires std::trivially_copyable key/value types with alignment at least that of a pointer, and its memory-mapped pool cannot be extended after creation without invalidating all allocator pointers
- Debug builds run O(n) full-tree sanity checks on every insert/erase/join/split (confirmed in closed issue #3, 'Performance issue'); only release-build numbers are meaningful

**Status:** Stale: last commit 2024-10-29, effectively single-maintainer, 249 stars, all 15 filed issues closed with none open; but it's header-only and small enough to vendor as-is if C++20 support is acceptable. License is plain Apache-2.0 per LICENSE.md and GitHub's own detection, despite the README additionally advertising an Apache-2.0-with-LLVM-exception/BSL-1.0 dual license.

[repo](https://github.com/frozenca/BTree) · [benchmark](https://github.com/frozenca/BTree/blob/main/README.md)

##### libart (Adaptive Radix Tree)  `C`  `BSD-3-Clause`  `abandoned`  `Tier C`

C99 Adaptive Radix Tree: ordered byte-key map/set, algorithmically faster than red-black trees (std::map's structure).

**Beats:** red-black tree (the ART paper's own in-memory red-black-tree implementation, algorithmically what std::map/std::set are built on, but not literally libstdc++/libc++/MSVC's std::map) — The claimed speedups (up to ~14-17x on dense keys, ~5-10x on sparse keys at 65K-256M random 32-bit keys) are entirely from the ART paper (Leis et al., ICDE 2013), which benchmarked the paper authors' own unreleased ART and red-black-tree implementations, compiled with GCC 4.6 on an Intel Core i7-3930K (6C/12T, 3.2GHz, 12MB shared L3, 32GB DDR3-1600, Linux 3.2 x86-64) — not libart, and not any std::map implementation. libart itself has no benchmark suite.

**How:** ART uses four node types (4/16/48/256 children) sized to actual local fanout instead of one fixed node shape, so small nodes stay cache-small and dense nodes get direct/O(1) child lookup. Path compression (inline partial keys up to MAX_PREFIX_LEN=10 bytes) and lazy expansion collapse single-child chains, bounding worst-case overhead to about 52 bytes/key. On x86/x86-64, Node16's 16-way key comparison is vectorized with SSE2 (_mm_cmpeq_epi8 + movemask + ctz) instead of a scalar loop; other architectures fall back to a plain scan.

**Use it when:**
- Ordered map/set semantics (min/max, ordered iteration, prefix iteration) over keys you can encode as binary-comparable byte strings
- Read-heavy, single-threaded in-process indexes (e.g. routing tables, in-memory dictionaries) where you own the key encoding
- Key sets where no key is a byte-for-byte prefix of another key, or you pre-length-prefix/terminate keys to avoid that case
- x86/x86-64 targets, where the SSE2 Node16 fast path applies (other archs still work via scalar fallback, just without that speedup)
- You're willing to vendor and maintain the ~2-file source yourself since the project is unmaintained

**Skip it when:**
- Any key can be a strict byte-for-byte prefix of another key: issue #56 (open) documents out-of-bounds reads / incorrect leaf-splitting in recursive_insert for exactly this case, with no released fix
- Multi-threaded concurrent access: no locks, atomics, or volatile-qualified state in the source; maintainer-adjacent discussion in issue #53 confirms it is not thread-safe and points to forks (e.g. ARTSynchronized) for concurrent variants
- You need a drop-in std::map/std::set replacement: this is an untemplated C library with a byte-key/void*-value function API, not a C++ generic container
- You need it actively maintained: last commit 2021-02-11, with confirmed bugs (#54 search returns null for prefix+NUL keys, #42 key_len issues, #35 crash in recursive_insert, #17 valgrind warning on prefix keys) still open
- You need project-specific speed evidence: libart ships no benchmarks of its own (repo has only src/ and tests/); every claimed number comes from the ART paper's own unreleased implementations, not this codebase

**Integration:** source-drop · none (libcheck is only needed to build the test_runner test suite, not the library) · C99; comments in art.c work around GCC 4.2.2's broken C99 inline support and a GCC 5.1 loop-unrolling bug, but no explicit minimum compiler version is stated · any (portable C99); SSE2 fast path compiled only under __i386__/__amd64__ for Node16 child lookup, scalar fallback loop used elsewhere

**Vs siblings:** Pick libart only when you specifically need ordered + prefix iteration over binary-comparable byte-string keys and are willing to vendor and patch an abandoned C library. Every other sibling in this category (cpp-btree, tlx, frozenca/BTree, fast-containers, RadixMap, S+ tree, boost::container flat_set) has actual project-measured benchmarks against std::map; libart has none of its own, so prefer those when maintained, verifiable numbers matter more than ART's specific prefix/min/max feature set.

**Gotchas:**
- Keys that are a byte-for-byte prefix of another inserted key can cause out-of-bounds reads and incorrect behavior in recursive_insert (issue #56, open; related #12, #17, #54)
- Path-compressed prefixes longer than MAX_PREFIX_LEN=10 bytes are only partially stored inline; matching a longer shared prefix requires re-reading a leaf key, a deliberate space/time tradeoff from the ART paper
- Keys must already be binary-comparable byte strings; signed integers, floats, and multi-field keys need an explicit transform before insertion, the library does none of this for you
- Leaf pointers are tagged in their low bit to distinguish them from internal nodes, so values/allocations the caller stores must not rely on odd pointer addresses

**Status:** Abandoned since its last commit on 2021-02-11; several confirmed bugs, including an unresolved out-of-bounds read for prefix-key inserts (#56), remain open years later. BSD-3-Clause and small enough (two files, src/art.c + src/art.h) to vendor and patch yourself if you accept that risk.

[repo](https://github.com/armon/libart) · [benchmark](https://db.in.tum.de/~leis/papers/ART.pdf)

##### RadixMap (radix-map)  `C++`  `Apache-2.0`  `active`  `Tier C`

Header-only PATRICIA/radix-tree map beating std::map on insert/contains for string and numeric keys.

**Beats:** std::map — README's Catch2 [benchmark]-tagged test cases (Release build, -O3, compiler version and CPU unstated), inserting and then contains()-checking 20,000 keys, report RadixMap 3.2x faster insert and 5.4x faster contains() than std::map for std::string keys (~111-118ms/~70-73ms vs std::map's ~366-369ms/~379-407ms), and 2.2x faster insert / 2.3x faster contains() for double keys (~101-104ms/~46-47ms vs std::map's ~215-234ms/~100-109ms).

**How:** Uses a PATRICIA/radix-tree structure that stores each shared key prefix once per node (a node for "http://" is shared by every key starting with it) instead of comparing whole keys node-by-node like a red-black tree, and branches via an adaptively-sized bit-mask over the next byte rather than per-byte/per-key comparison. Nodes and values are allocated from a block-based bump/arena allocator (RadixMapArena) rather than individually. For fixed-length keys (integral/floating-point), the find()/lower_bound() traversal stack is backed by the vendored BoundedVector, making that state heap-allocation-free.

**Use it when:**
- Sorted map over std::string or integral/floating-point keys where insert/contains throughput matters most: 3.2x/5.4x faster than std::map for strings, 2.2x/2.3x for doubles at 20,000 keys (Release, -O3, per README).
- Need prefix search over string keys (prefix_range) instead of hand-rolling lower_bound() plus an increment-last-byte upper bound that breaks on a 0xFF-terminated prefix.
- Workload dominated by contains()/at()/operator[] rather than find()/lower_bound(): contains() is far cheaper than find() in the same benchmarks (e.g. ~70-73ms vs ~452-461ms for 20,000 string keys).
- Single-threaded or externally-synchronized use only — no built-in thread safety.
- C++20 codebase willing to vendor two header files (RadixMap.hpp + BoundedVector.hpp) rather than link a library.

**Skip it when:**
- Need reverse iteration: no rbegin()/rend()/operator--, forward-only because the tree has no parent pointers.
- Need a custom comparator or allocator template parameter — the header's own doc comment lists both as unsupported.
- Erase-heavy workloads: erase() is a tombstone that clears the value but leaves the compressed tree structure (and its memory) untouched, so memory grows with churn beyond the live entry count.
- Key type has no RadixMapKeyTraits specialization and you don't want to write one (only std::string and arithmetic types are built in).
- Risk-averse selection: 0 GitHub stars, first commit 2026-07-06, single author, 0 issues opened yet, no independent benchmarking or production use documented.

**Integration:** header-only · none at runtime; Catch2 3 is required only to build/run the bundled RadixMap-test.cpp benchmark/test suite; optional integration with a separate Ensure.hpp project for throw_if(), falls back to an equivalent local implementation if that header isn't present · C++20 (CMakeLists.txt sets CMAKE_CXX_STANDARD 20) · no explicit architecture requirement documented; CI (.github/workflows/ci.yml) builds and tests on ubuntu-24.04 and macos-latest via CMake+Ninja; Windows/MSVC not covered by CI

**Vs siblings:** Pick RadixMap over the B-tree-family siblings (fast-containers, Flat-Map-RB-Tree, cpp-btree, frozenca/BTree, tlx::btree_map) when you specifically need prefix_range()-style prefix queries over std::string keys, or want a two-header vendor-and-go dependency rather than a library benchmarked at multi-million-element scale. Pick libart instead if you want a more independently scrutinized adaptive radix tree (with a C API, not a std::map-like C++ interface); pick a B-tree sibling if you need comparator/allocator customization or verified performance at 1M+ elements, since RadixMap has only been measured at 20,000 keys by its sole author.

**Gotchas:**
- Range-for needs auto&& or auto, never auto&: operator*() returns a proxy Entry{Key first; Value& second;}, not a reference into a stored pair, so 'for(auto &entry : map)' fails to compile.
- +0.0 and -0.0 double keys encode to different byte patterns and are treated as distinct, unlike std::map<double,...>'s default std::less which treats them as equal.
- erase() does not reclaim compression: repeated insert/erase churn leaves memory usage above the current live-entry count, with no compact() available yet.
- prefix_range() degenerates to at most a single entry for fixed-width key types like double, since a shorter double isn't itself a valid key — it only does useful prefix work for std::string keys.

**Status:** Active but very new (first commit 2026-07-06, last commit 2026-07-09), single-author, 0 stars, 0 issues opened; Apache-2.0 licensed and header-only (two files: RadixMap.hpp + BoundedVector.hpp), trivial to vendor or drop.

[repo](https://github.com/lrmoorejr/radix-map) · [benchmark](https://github.com/lrmoorejr/radix-map/blob/main/README.md)

#### priority-queues-heaps

##### RadixHeap (radix_heap_rust)  `Rust`  `Apache-2.0`  `active`  `Tier C`

Monotone bucket-based radix heap for Rust; ~1.7-2x faster than std BinaryHeap<Reverse<u32>> for large random u32 heapsort.

**Beats:** Rust std::collections::BinaryHeap (with Reverse) — The project's own Criterion benchmark (benches/benchmark.rs) pushes N random u32 keys then pops all of them (N = 125,000 << i, i in 0..10, i.e. 125K-64M) against std::collections::BinaryHeap<Reverse<u32>>, on an unspecified 'mid-range desktop CPU' with no compiler version or flags stated; reported totals: 1M ~180ms vs ~320ms, 8M ~1.6s vs ~3.0s, 64M ~15s vs ~28s (~1.7-2x faster).

**How:** Classic radix-heap bucketing: on push, the key is XORed with the last-extracted minimum and the position of the highest differing bit picks a bucket (RadixHeap::get_bucket_to_insert_into in src/heap.rs), so push is an O(1) append with no per-element comparisons against existing heap contents, unlike BinaryHeap's O(log n) sift. pop scans for the first nonempty bucket and, only when it isn't bucket 0, redistributes that bucket's elements into finer buckets (rearrange()) before returning the true minimum (tracked per-bucket via a real `<` comparison, not the XOR trick). For fixed-width integers the bit range is a small constant (e.g. 32 for u32), making amortized pop cost effectively O(1) in practice.

**Use it when:**
- Dijkstra / SSSP or other monotone-extraction graph algorithms where extracted keys are non-decreasing
- Fixed-width integer keys (u8-u128, i8-i128, usize/isize) or f32/f64, large N (millions), push-all-then-pop-all or monotone-interleaved throughput workloads
- Rust code currently doing BinaryHeap<Reverse<K>> for a min-heap and able to change call sites, not just imports
- Willing to accept a hard panic (not a Result) as the failure mode if a non-monotone key is ever pushed
- OK vendoring a small (4-file), unaudited, non-1.0 crate rather than depending on a maintained package

**Skip it when:**
- General-purpose priority queue where later-pushed keys can be smaller than an already-popped minimum (this panics; BinaryHeap just works)
- You need BinaryHeap's API surface: peek_mut, into_sorted_vec, iterator support, From<Vec>, etc. -- none exist here
- Non-numeric or custom key types beyond what you're willing to hand-implement Key (xor + position_of_highest_set_bit) for yourself
- Multi-threaded/concurrent access -- no Sync/Send or synchronization documented or present in source
- Production reliance on correctness/maintenance guarantees: 0-star, two-author WS2023/24 university coursework crate with no releases

**Integration:** crate · rand 0.8.5 (runtime); proptest 1.3.1 and criterion 0.5 (dev-only, for tests/benches) · Rust 2021 edition (Cargo.toml edition = "2021"); exact MSRV not documented · not documented; pure safe Rust with no unsafe blocks, no SIMD intrinsics, and no arch-specific code observed in heap.rs, bucket.rs, or key.rs

**Vs siblings:** Pick this over prio_queue (rollbear) or pair_radix_heap when you're in Rust, not C++ (those are C++-only). Versus SimdQuickHeap, the other Rust sibling beating the same BinaryHeap baseline, SimdQuickHeap reports far larger per-element speedups (~12-14x, AVX2/AVX512) and isn't monotone-restricted, so prefer this crate only when you specifically want the simpler bucket/XOR radix-heap technique for a Dijkstra-style monotone workload without SIMD or nightly-feature requirements.

**Gotchas:**
- push() panics with "Invalid Key" (not a Result/Option) if the key is smaller than the last-extracted minimum -- a crash risk if input isn't guaranteed monotone
- f32/f64 support XORs raw IEEE-754 bit patterns via to_bits() with no separate sign-order transform; verified only by two fixed 5-element unit tests (f32, f64) -- the proptest random-key property test covers only u32, not floats
- LICENSE file in the repo is Apache-2.0, while Cargo.toml and the README both declare MIT -- check which actually applies before vendoring
- A compiled binary (src/main.exe) is committed to the repo alongside src/main.rs, suggesting light packaging/CI hygiene

**Status:** Last commit 2026-05-14 (active by date) but is a two-author WS2023/24 university coursework project with 0 stars, 0 forks, and no tagged releases beyond Cargo.toml's 0.1.0; small and dependency-light enough to vendor, but treat as unaudited/unmaintained-risk rather than a supported package.

[repo](https://github.com/Frank10969/radix_heap_rust) · [benchmark](https://github.com/Frank10969/radix_heap_rust)

#### random

##### AESRand  `C++`  `MIT`  `abandoned`  `Tier C`

AES-NI hardware-accelerated PRNG streaming 256 bits per iteration, far outpacing std::mt19937 in raw throughput.

**Beats:** std::mt19937 — On the author's own benchmark (5-10 billion iteration tight loop, Visual Studio 2017 x64 build, AMD Threadripper 1950x manually locked to 3.4GHz), AESRand measured 27.45 GB/s single-stream / 34.35 GB/s dual-stream versus 0.858 GB/s for std::mt19937 (MSVC STL) — about 32x/40x higher throughput, or 3.69 cycles per 32-byte iteration versus mt19937's 14.76 cycles per 4-byte iteration. The README itself flags that mt19937 was not inlined in this test, which may inflate the ratio.

**How:** The 'counter' portion (AESRand_increment) is a single SIMD add with 1-cycle latency, kept deliberately minimal since it bounds the loop's critical path. The 'mixer' chains 2-3 AESENC/AESDEC round instructions per iteration, which have 1-per-cycle (or 2-per-cycle on AMD Zen) throughput, so instruction-level parallelism across loop iterations hides most of the ~4-cycle AES latency. The dual-stream variant runs two independent counter/mixer chains to expose more ILP, measured at 2.95 cycles/iteration vs 3.69 for the single-stream version.

**Use it when:**
- Bulk random-byte generation on x86-64 with AES-NI (Westmere/Bulldozer or newer) where throughput, not API compatibility, is the goal
- Workloads that can consume 256 bits per draw at once (buffer fill, Monte Carlo sampling, fuzz-input generation)
- You're willing to vendor a small source drop and manage RNG state explicitly per thread/stream yourself
- You need many verified-independent parallel streams (PractRand-clean to 4TB across the tested stream space) rather than a single sequential stream
- You're prototyping/researching AES-NI-based RNG design rather than shipping a supported dependency

**Skip it when:**
- Target hardware lacks AES-NI / ARMv8 crypto extension / Power9 crypto builtins (no software fallback exists)
- You need a std::mt19937-compatible engine you can plug into <random> distributions or std::shuffle without wrapper code
- You need cryptographic-strength randomness; this is a statistical PRNG only, with an author-documented weakness to single-bit counter changes
- You'd run the parallel-stream (dual-output) variant past 8TB of PractRand-equivalent output, where it's known to fail
- You need active maintenance, releases, CI, or community support (repo is a single-author research prototype, abandoned since 2019)

**Integration:** source-drop · none beyond compiler intrinsics (immintrin.h on x86, arm_neon.h on aarch64, GCC PPC crypto builtins on Power9) · C++11 (AESRand_Paper's ARM Makefile pins -std=c++11, built with g++-8.3; the x86 Makefile passes no -std flag, just -maes; the Windows benchmark used VS2017/v141) · x86-64 with AES-NI required for the benchmarked path; AESRand_Paper additionally ships aarch64 (ARMv8 crypto ext, via Makefile.arm) and Power9/PPC64 (via Makefile.power9) implementations, but only the x86 path was benchmarked

**Vs siblings:** Pick AESRand over ALU-based siblings (PCG, xoshiro_cpp, wjakob/pcg32, biski64, nanobench::Rng) when you specifically want to saturate AES-NI throughput for bulk byte generation rather than a small, portable, dependency-free integer generator. Prefer Random123 (also AES-NI-based) instead if you want a similarly hardware-accelerated generator with more independent, peer-reviewed statistical validation — Random123's reported margin over std::mt19937_64 (~1.8x) is far more conservative than AESRand's ~32-40x, partly reflecting AESRand's larger per-call output and its non-inlined mt19937 baseline.

**Gotchas:**
- Author's own benchmark notes std::mt19937 was NOT inlined by MSVC, which may inflate the measured speedup vs. an inlined baseline
- 1-bit changes to the counter increment are a documented weak direction; the design compensates by changing the full 128-bit state every step
- The parallel-stream (dual-output) variant only varies the top 64 bits and fails PractRand beyond 8TB, so only ~2^35 verified-independent streams exist despite a 2^64 theoretical claim
- Three near-duplicate implementations exist in-tree (Windows/VS2017, AESRand_Linux, AESRand_Paper) with slightly different APIs (e.g. AESRand_rand vs AESRand_rand_uint32); pick one and expect to adapt it

**Status:** Abandoned since its last commit in April 2019; MIT-licensed and small enough to vendor as source, but it's a single-author research prototype with no releases, no CI, and only one (non-bug) closed issue — treat it as a design reference to adapt, not a supported dependency.

[repo](https://github.com/dragontamer/AESRand) · [benchmark](https://github.com/dragontamer/AESRand/blob/master/BenchmarkResults.md)

##### biski64  `C`  `MIT`  `stale`  `Tier C`

Tiny 3-word Weyl+rotate PRNG beating std::mt19937_64 on raw throughput; not a drop-in, ships as Rust crate + C reference source.

**Beats:** std::mt19937, std::mt19937_64 — In planet36/prng-test-bench's Google Benchmark harness (7 threads on an 8-vCPU VM, g++ -O3 -flto=auto -march=native, C++26), that harness's own C++ port of biski64 sustained 13.8 GB/s median / 14.0 GB/s mean per-thread next()-call throughput versus 5.63/5.54 GB/s for libstdc++'s std::mt19937_64 (~2.5x) and 5.01/5.02 GB/s for std::mt19937 (~2.8x). biski64's own README instead benchmarks against xoshiro/PCG/wyrand/sfc64/Java generators on an AMD Ryzen 9 7950X3D and does not include std::mt19937.

**How:** Each step is 3 register-sized XOR/add/rotate operations with no multiplication, no lookup tables, and no branches, which is why the author's own benchmarks show it tying wyrand/sfc64 and beating xoshiro256++/xoroshiro128++ in ns/call. A 64-bit Weyl sequence (fast_loop += 0x9999999999999999) guarantees the period never drops below 2^64 regardless of how mix/loop_mix behave, letting the design use less state than xoshiro-family generators, which need a larger state array for their period guarantee. Against std::mt19937/mt19937_64 specifically, the win is the generic 'small counter+mix generator beats tempering-heavy Mersenne Twister' gap, not a biski64-specific trick.

**Use it when:**
- Non-cryptographic, throughput-bound 64-bit generation (simulation, sampling, shuffling) where you'd otherwise use std::mt19937_64 and want a smaller/faster algorithm to port in.
- Rust projects on rand_core/rand 0.9 wanting a no_std-compatible RngCore/SeedableRng implementation via the biski64 crate.
- Parallel workloads needing independent streams from one seed: biski64_stream()/from_seed_for_stream() space fast_loop per stream without a separate jump-ahead call.
- Memory- or register-constrained targets: 3 x 64-bit words of state; a user reports it running on an ESP32 (issue #11).
- You've already accepted a Weyl-sequence design's 2^64 minimum period as sufficient for the workload.

**Skip it when:**
- You need a literal drop-in for std::mt19937/mt19937_64 in C++: biski64's C code has no std::random-compatible interface (no operator(), min()/max()), so adoption is a rewrite, not a swap.
- Long-running, high-volume statistical workloads: a third party (SmokeRand author, issue #8) reports biski16/32/64 fail a Hamming-distance test at roughly 1 TiB of output, and issue #10 shows biski64 failing PractRand's expanded/extra-folding test set at 2^34 bytes (16 GB), traced to periodicity in the Weyl sequence's low bits.
- Cryptographic or adversarial contexts: not designed or claimed to be cryptographically secure.
- You want a battle-tested, widely audited generator: first published 2025, 152 stars, last commit 2025-06-12 and now stale; PCG and xoshiro have years more scrutiny and independent implementations.
- You need maximum period margin: 2^64 minimum vs 2^256 for xoshiro256++, relevant for very long single-stream runs or huge numbers of parallel streams.

**Integration:** source-drop (C: copy struct + 3 functions from c/biski64.c) | crate (Rust: biski64 on crates.io) · C: none beyond stdint.h. Rust: rand_core 0.9 (rand 0.9 / rand_xoshiro / criterion are dev-only, for the crate's own benchmark comparisons). · C: C99 (stdint.h only, no other requirement found in source). Rust: edition 2021, no_std compatible. The C++ port used for the benchmark (planet36/prng-test-bench) needs C++20 for std::rotl, but that's the harness, not upstream biski64. · any (plain integer ops, no SIMD/intrinsics observed); reported working on an ESP32 microcontroller in issue #11 (closed).

**Vs siblings:** Pick biski64 over PCG (pcg-cpp), wjakob/pcg32, or xoshiro_cpp when a smaller 3-word state matters more than track record and you accept a newer, less-audited design with a 2^64 period floor. Prefer PCG or xoshiro_cpp instead when you need a C++-native, std::random-compatible API today (biski64's C code has none) or want a generator without the open statistical-weakness reports noted above.

**Gotchas:**
- c/biski64.c ships with its own main(); PR #6 (open) proposes a fix. Until merged, strip main() or apply the workaround from that PR before including the file.
- Seeding functions run a 16-iteration warmup (biski64_warmup / the loop in from_seed_for_stream) before first use; a hand-rolled state init that skips this would start on weaker, non-warmed state.
- Two independent third-party reports found statistical weaknesses invisible to BigCrush/PractRand's default settings: SmokeRand's hamming_distr test (issue #8, ~1 TiB) and PractRand with extra folding (issue #10, fails at 2^34 bytes / 16 GB).
- Parallel-stream seeding (biski64_stream / from_seed_for_stream) needs total_streams fixed up front to space fast_loop; there is no independent jump-ahead/split function for streams created later.

**Status:** Last commit 2025-06-12, marked stale by the catalog's maintenance check; MIT-licensed and small (three functions, ~150 lines of C) so easy to vendor regardless, but two open issues (SmokeRand hamming_distr failure, PractRand extra-folding failure at 16 GB) show the statistical design is still under active scrutiny.

[repo](https://github.com/danielcota/biski64) · [benchmark](https://github.com/planet36/prng-test-bench/blob/main/results/prng-next-benchmark.json)

##### nanobench::Rng (RomuDuoJr)  `C++`  `MIT`  `active`  `Tier C`

nanobench's built-in RomuDuoJr generator: a drop-in <random>-style 64-bit PRNG, ~1.3-3.9x faster than std::mt19937_64.

**Beats:** std::mt19937_64 — Nanobench's own tutorial.rst shows two different first-party runs, neither stating compiler, flags, or CPU: a relative()-table run has ankerl::nanobench::Rng at 1.57 ns/uint64_t vs std::mt19937_64 at 2.03 ns (~1.3x) and vs std::default_random_engine at 35.87 ns (~22.8x); a separate compare()-table run (with 95% CI) has nanobench::Rng at 0.49 ns/uint64_t vs std::mt19937 at 1.71 ns (3.48x, CI 3.46-3.50x) and vs std::mt19937_64 at 1.90 ns (~3.9x). The two runs disagree by roughly 3x on the margin over mt19937_64, and the second table's exact RNG lineup (includes an unlabeled 'lcg by hand') has no corresponding source file checked into the repo.

**How:** Implements RomuDuoJr (Mark Overton's Romu family), a non-cryptographic generator with only 128 bits of state (two uint64_t words) and a per-call update of one 64-bit multiply plus a subtract-then-rotate, far cheaper than Mersenne Twister's large state array and tempering step. operator() is declared inline in the header so it can fully inline at the call site. The design trades statistical rigor and state size for minimal instructions per call.

**Use it when:**
- Feeding random inputs to a nanobench benchmark loop where RNG overhead must stay well below the measured operation's own cost
- Non-cryptographic hot loops needing a fast 64-bit value or ranged integer where std::mt19937/mt19937_64 throughput is the bottleneck
- Already depending on nanobench and wanting to avoid pulling in a second PRNG library for lightweight randomness
- Need a fast, slightly-biased container shuffle (shuffle()) instead of std::shuffle
- Deterministic-but-throwaway sequences within a single build (seed via Rng(seed)) where cross-version reproducibility isn't required

**Skip it when:**
- Anything security- or cryptography-adjacent - the header states outright it is not cryptographically secure
- Large-scale simulation or Monte Carlo work - the author's own doc comment caps estimated capacity at ~2^51 bytes and calls it 'not enough for large jobs'
- Code that must reproduce the same sequence across nanobench upgrades - the header warns the underlying algorithm may change between releases
- Multi-threaded code sharing one generator instance - thread safety isn't documented and Rng is move-only (copy disabled), implying one instance per thread
- Workloads needing an unbiased bounded-integer distribution - bounded() uses a fast biased reduction, not rejection sampling

**Integration:** header-only · none (C++ standard library only) · C++11 (CMake target_compile_features cxx_std_11; repo advertises C++11/14/17/20 support) · platform-independent - pure integer/multiply ops, no SIMD or ISA requirement

**Vs siblings:** Pick it only if you're already using nanobench and want a zero-dependency fast RNG for generating benchmark inputs. For general-purpose or higher-throughput random number generation, PCG (pcg-cpp/wjakob pcg32) or xoshiro_cpp are better studied, and the tutorial's own numbers show nanobench::Rng's edge over std::mt19937_64 (~1.3-3.9x, inconsistent across two runs) is smaller and shakier than PCG's (~3.5-4x) or xoshiro256++'s (~3.2x) measured margins.

**Gotchas:**
- Copy constructor and copy-assignment are deleted; use .copy() or move semantics instead of copying by value
- The algorithm may change between nanobench releases (documented in the header), so seeded sequences aren't guaranteed stable across upgrades
- bounded(range) uses a fast, slightly biased reduction rather than rejection sampling
- Using it outside nanobench still requires building the one translation unit compiled with ANKERL_NANOBENCH_IMPLEMENT, like the rest of the header-only library

**Status:** Active (last commit 2026-09-06) and MIT-licensed; the whole library is one header plus a one-line implementation .cpp, trivial to vendor even if development ever stalls.

[repo](https://github.com/martinus/nanobench) · [benchmark](https://github.com/martinus/nanobench/blob/master/src/docs/tutorial.rst)

#### regex

##### CTRE (compile-time regular expressions)  `C++`  `Apache-2.0`  `active`  `Tier C`

Header-only C++ template-metaprogramming regex engine for compile-time-known patterns, with large wall-clock wins over std::regex.

**Beats:** std::regex — First-party `time`-command runs (clang-bench.txt and gcc-bench.txt, committed 2018-10-23) show CTRE beating std::regex by roughly 11x-125x wall-clock across four patterns under clang (e.g. 10.093s vs 21m9.309s on 'ABCD|DEFGH|EFGHI|A{4,}') and roughly 14x-24x under gcc (e.g. 3.982s vs 0m55.058s on the same pattern), with no compiler version, optimization flags, CPU, or input size recorded. A separate WG21 P1433R0 table gives CTRE 3.172s vs std::regex/libstdc++ 33.585s on Linux/gcc and CTRE 11.11s vs std::regex/libc++ 1655s on macOS/clang, and that macOS figure duplicates a clang-bench.txt number exactly, so the two sources' data provenance is unclear.

**How:** Regex parsing and construction of the matching logic both happen at compile time via constexpr functions and template metaprogramming (the bundled ctll parser), so the compiler emits specialized branch/comparison code for one exact pattern instead of interpreting a generic runtime NFA the way std::regex does. This removes std::regex's per-call pattern-compilation cost entirely and lets ordinary compiler optimizations (inlining, constant folding) act directly on the matcher. The tradeoff is longer compile times and larger generated code in exchange for eliminated runtime interpretation overhead.

**Use it when:**
- Pattern is a compile-time literal or constexpr reused across many match calls (parsers, lexers, validators), not built from runtime user input.
- Hot-path matching/parsing where std::regex's per-invocation compile step dominates runtime.
- Want structured-binding capture access (e.g. `auto [whole, year, month] = ...`) instead of std::smatch/std::ssub_match.
- Project can require clang 14+, gcc 9+, or MSVC 16.11+ and build with C++17/20.
- Header-only vendoring is acceptable — a single-header variant exists for easy drop-in as a source file.

**Skip it when:**
- Pattern arrives at runtime (user-supplied, config-loaded) — CTRE patterns must be compile-time-known, so it can't replace std::regex there.
- Need PCRE features CTRE excludes: callouts, comments, conditional patterns, \cX control-char escapes, \K match-point reset, named characters, octal numbers, subroutines, \X grapheme clusters.
- Toolchain predates clang 14 / gcc 9 / MSVC 16.11 (VS 2019 16.11).
- Taking the README's or bench files' >50x numbers at face value: they are tier-C, dated 2018-10-23, with no CPU, compiler version, flags, or input size stated.
- Correctness on edge cases matters as much as speed: open bugs include incorrect matches with repeated capture groups (#300) and lookahead failing to compile with UTF-8 input (#338).

**Integration:** header-only · none (bundles its own ctll template-parser headers) · C++17 (C++20 for the `<pattern>` NTTP syntax); clang 14+, gcc 9+, MSVC 16.11+ (VS 2019 16.11) · any (portable standard C++, no architecture-specific code)

**Vs siblings:** Pick CTRE over RE2 when the pattern set is fixed at compile time and you want zero runtime regex-compile overhead with PCRE-like syntax and structured-binding captures; pick RE2 instead when patterns are supplied at runtime or you need its linear-time worst-case guarantee against untrusted/adversarial input.

**Gotchas:**
- Pattern must be compile-time-known: a template argument or constexpr ctll::fixed_string, never something assembled at runtime.
- The N3599 UDL syntax (`"regex"_ctre`) on GCC 9.1+ requires defining CTRE_ENABLE_LITERALS and building without -pedantic.
- Unicode support is opt-in via separate `<ctre-unicode.hpp>` + `<unicode-db.hpp>` includes; omitting them gives missing-symbol link errors, not silent fallback.
- Open bugs: incorrect match with repeated capture groups (#300, 2025), lookahead fails to compile with UTF-8 strings (#338, 2025), MSVC internal compiler error on some inputs (#255, 2022).

**Status:** Actively maintained (last commit 2026-09-11, CMakeLists reports v3.11.0) with 3.9k stars and used as the reference implementation for WG21 proposal P1433; Apache-2.0 licensed and header-only, so cheap to vendor even though its headline benchmark numbers are old (2018) and thinly documented.

[repo](https://github.com/hanickadot/compile-time-regular-expressions) · [benchmark](https://github.com/hanickadot/compile-time-regular-expressions/blob/main/clang-bench.txt)

##### REAL (real-regex)  `C++`  `MIT`  `active`  `Tier C`

Header-only C++20 linear-time regex engine with lookaround support, beating std::regex 8x-152x and RE2 on every supported pattern.

**Beats:** std::regex — REAL's own in-repo benchmark (benchmarks/bench_engines.cpp via make bench-engines, c++ -std=c++20 -O2; g++ 13.3.0 on an unnamed x86-64 host, Apple Clang 16 on arm64 Apple Silicon) counted non-overlapping matches for 12 general-purpose patterns and measured REAL 8.20x-41.97x faster than std::regex (libstdc++) on x86-64 and 15.31x-151.97x faster than std::regex (libc++) on arm64, 2.90x-16.34x/2.41x-11.53x faster than RE2 where RE2 supports the pattern, and ahead of PCRE2-JIT on 7 of 12 rows on both ISAs - all figures matched exactly what is published in docs/BENCHMARKS.md this session.

**How:** Routes each compiled pattern to the cheapest execution tier that can handle it - exact-literal/fixed-shape fast paths, a one-pass DFA, a lazy DFA with a bounded state cache, or the general Pike VM (Thompson-NFA simulation) as fallback - instead of always running one general matcher. Character-class steps use SIMD probing (engine/simd.hpp), and a required-literal prefilter rejects non-matching input (e.g. classic ReDoS patterns) in microseconds without entering the NFA at all. Constexpr-friendly parsing/compilation lets patterns known at compile time be parsed, compiled and matched at compile time.

**Use it when:**
- C++20 codebase needing linear-time, ReDoS-safe matching AND lookaround in the same engine (RE2/Rust regex lack lookaround, PCRE2/std::regex backtrack)
- Single-pattern throughput workloads - word/digit/field extraction, hex/date matching, alternation - where the project's own benchmark shows 8.20x-41.97x (x86-64) / 15.31x-151.97x (arm64) over std::regex and wins over RE2 in every case RE2 supports
- Untrusted or adversarial regex patterns/subject text where catastrophic backtracking (e.g. (a+)+b) is a real operational risk
- Need the same engine exposed from Python, Rust, Go and C via the project's own bindings, not just C++
- Willing to pay a header-only compile-time cost (measured 4.3s / 213KiB __text for one TU vs 1.1s / 47KiB for <regex>, arm64 clang -O2) in exchange for the runtime win

**Skip it when:**
- Pattern needs backreferences or conditional groups - REAL rejects these outright by design (real::regex_error, no silent fallback in its native API)
- Matching many patterns against one text at once (regex_set) with N much above ~56 - REAL's pure N-walk mode degrades hard (~559 MB/s at N=16 down to ~39 MB/s at N=128 on the project's own bench) and loses to RE2::Set/Hyperscan at scale
- Lookahead-heavy or fixed-width date/hex workloads specifically - PCRE2-JIT still wins those rows outright (0.71x-0.92x, i.e. PCRE2 faster) in REAL's own tables
- Toolchain stuck below C++20 - this is a hard minimum, asserted in every header, versus std::regex's C++11 floor
- Risk-averse teams: this is an extremely new project (4 stars, repo created 2026-06-13) with benchmarks that are self-published and not yet independently reproduced

**Integration:** header-only · none (zero runtime deps; the SciForge harness is only needed to build the test suite/CI, never the library itself) · C++20 (hard requirement, enforced via a static_assert in every header); tested in CI with g++ 13.3.0, Apple Clang 16, and MSVC on Windows · Linux x86-64 and AArch64, macOS arm64, Windows (MSVC) per CI matrix; no specific SIMD ISA extension (e.g. AVX2) documented as mandatory

**Vs siblings:** Pick REAL over Boost.Regex when you need a linear-time ReDoS-safe guarantee with lookaround - Boost.Regex is a backtracking engine like std::regex and doesn't offer that guarantee. Pick it over RE/flex when you need general runtime regex matching rather than an offline lexer-generator workflow, and over Unformat when the task is general pattern matching rather than std::format-style structured parsing.

**Gotchas:**
- Possessive quantifiers/atomic groups are only linear-time (Tier 1) for a single atom or one atom wrapped in one capturing group ([^x]*+, \d++, (?>\w+)); a compound body inside them is rejected outright, never silently mismatched
- Nullable patterns (a*, (x)?) keep REAL's ReDoS-safe search/match, but regex_replace and iteration on them are delegated to std::regex per-operation - the linear-time guarantee doesn't cover every operation on every pattern
- find_iter (and Python finditer) do not get the trailing-lookahead fast path that count_matches/search/match/replace get - benchmarks that compare via len(findall(...)) rather than count_matches are not comparable to this project's own numbers
- Backreferences, recursion, subroutine calls and callouts are excluded by design (raise real::regex_error) - not a roadmap gap but a permanent rejection to preserve the linear-time guarantee

**Status:** Actively maintained - near-daily CalVer releases (release notes run through v2026.9.7, last commit 2026-09-24) - and MIT-licensed, header-only, so trivially vendorable, but still a very new, small project (4 stars, repo created 2026-06-13) with no external validation of its benchmarks beyond its own suite.

[repo](https://github.com/RECHE23/real-regex) · [benchmark](https://github.com/RECHE23/real-regex/blob/main/docs/BENCHMARKS.md)

##### Unformat  `C++`  `Unlicense`  `active`  `Tier C`

Single-header scanf-style '{}' field extractor for fixed-shape strings; beats std::regex when regex is overkill.

**Beats:** std::regex — On the repo's own Google Benchmark run (32 x 2420 MHz CPUs; compiler, flags, and OS unstated), Unformat took 32.6 ns per call (11.5 ns with the constexpr make_format path) versus 3269 ns for std::regex parsing the same 4-field string. The std::regex leg constructs (compiles) the regex object inside the timed loop every iteration, so that 3269 ns bundles NFA compilation with the match itself; against a precompiled regex the gap would be far smaller than the ~100x-284x (or advertised '300x') headline suggests.

**How:** It avoids std::regex entirely: no NFA construction, no std::string allocations, no capture-group bookkeeping. The constexpr make_format path precomputes each placeholder's byte offset and delimiter character at compile time, so unformat_internal just walks pointers with inlined, per-type combined scan+parse loops (fixed-point digit accumulation instead of std::stoi/std::stof). Numeric parsing accumulates an integer mantissa and applies one final multiply against precomputed powers-of-10 tables, with a noinline cold path reserved for scientific notation or >18-digit literals.

**Use it when:**
- Extracting a handful of ints/floats/strings from a fixed, known-shape line (logs, telemetry, simple protocols) where std::regex would only be used for its capture groups, not real pattern matching.
- Hot loops calling the same format thousands of times per second, where std::regex's per-construction NFA compile is the bottleneck (the benchmarked 3269 ns/call includes that compile, not just matching).
- The format string can be pinned as a compile-time literal, so ay::make_format runs at compile time (11.5 ns vs 32.6 ns for the runtime-parsed path, per the repo's own benchmark).
- Header-only vendoring is acceptable: copy unformat.h into a codebase with no other dependencies and no build-system integration.
- Input is trusted and guaranteed to match the format exactly (internal data, not raw user/network input).

**Skip it when:**
- You need actual regex features -- wildcards, character classes, alternation, quantifiers, anchors; Unformat only matches literal text between '{}' tokens.
- Input may be malformed, truncated, or adversarial: the string_view/char scan path (unformat_arg_scan<ay::string_view> in unformat.h) has no check against the input's terminating null while hunting for a delimiter, so a non-matching string can read past the buffer end.
- You need match/fail feedback: there is no success return, exception, or optional -- bad input silently yields wrong values (a 'does this match' check was requested in issue #3 back in 2017 and is still open).
- More than 16 '{}' placeholders in one format string (hard-coded format::MAX_COUNT = 16).
- Your real baseline is a precompiled std::regex rather than one rebuilt every call -- the ~100x-284x gap narrows a lot once compilation is amortized (see verified_claims_summary).

**Integration:** header-only · none (only <cstddef> from the standard library) · C++14 in practice for the constexpr make_format path -- make_format_non_template declares a local variable, uses a loop, and a throw, which need C++14 relaxed-constexpr rules. CMakeLists.txt sets CMAKE_CXX_STANDARD 11 for the test/benchmark build, which predates that; the plain runtime unformat() call compiles fine under C++11. · any -- portable C++, no SIMD/intrinsics; MSVC/GCC/Clang are detected via macros only to pick inline/noinline/restrict hints, with a generic fallback for other compilers

**Vs siblings:** Pick Unformat over Boost.Regex, RE/flex, or REAL when you're pulling a few typed fields out of a fixed-shape string and don't need any real regex syntax (wildcards, classes, alternation) -- it's a smaller, dependency-free single header, where the siblings are full regex engines (or, for RE/flex, a code-generation tool) sized for genuine pattern-matching workloads.

**Gotchas:**
- The string_view/char scan path has no null-terminator check while hunting for a placeholder's end delimiter -- malformed input that never contains that delimiter can read out of bounds (verified in unformat.h's unformat_arg_scan<ay::string_view> specialization).
- Exceeding 16 '{}' placeholders throws a raw string literal ("Max number of {} has been exceeded.") from the format constructor -- a compile error in a constexpr context, an untyped throw at runtime.
- ay::string_view is a bare {const char* data; size_t size;}, non-owning into the original input buffer -- it dangles if the source string is freed, reallocated, or goes out of scope.
- CMakeLists.txt declares C++11 but constexpr make_format needs C++14 relaxed-constexpr to actually compile as constexpr; verify your compiler's effective standard before relying on the compile-time path.

**Status:** Actively maintained as of March 2026, with recent commits micro-optimizing numeric parsing and the pow10 tables; public-domain (Unlicense) and small enough (one header) to vendor and maintain yourself even if upstream activity stops.

[repo](https://github.com/adamyaxley/Unformat) · [benchmark](https://github.com/adamyaxley/Unformat/blob/master/README.md)

#### searching

##### sb_lower_bound (Fastest Branchless Binary Search)  `C++`  `MIT`  `abandoned`  `Tier C`

Branchless drop-in-shaped replacement for std::lower_bound that relies on clang emitting cmov instead of a branch.

**Beats:** std::lower_bound — Author's own benchmark (test.cpp) on one unspecified Intel Kaby Lake i7, g++-10/clang++-10 -std=c++20 -O2 -march=haswell, against libstdc++'s std::lower_bound: with clang and -mllvm -x86-cmov-converter=false, sb_lower_bound averages 33.24 ns/call vs 61.30 ns for std::lower_bound (~1.84x) on primitive types; without that flag, or under gcc, results are roughly parity, and for 8-byte string keys sb_lower_bound is slightly slower in every measured configuration. A later post on the same site reports the separate prefetching variant sbpm_lower_bound at ~71 ns vs std::lower_bound's ~161 ns (~2.3x) on arrays up to ~128M entries.

**How:** Classic binary search on random data mispredicts branches roughly half the time, stalling the pipeline; sb_lower_bound's comparison-and-advance step is written so clang (with -mllvm -x86-cmov-converter=false) lowers it to a cmov, letting the CPU avoid that misprediction penalty at the cost of doing k+1 comparisons per lookup instead of std::lower_bound's average log2(n+1). A separate variant in the same repo, sbpm_lower_bound, adds __builtin_prefetch calls on both candidate cache lines once the range exceeds an L2-sized threshold (256KB), which the author's later post credits for most of the gain on multi-hundred-MB arrays.

**Use it when:**
- Sorted arrays of primitive integer/float/pointer keys with a single-instruction comparator
- Hot search loops compiled with clang on x86-64 where you can add -mllvm -x86-cmov-converter=false
- Very large (multi-MB to GB scale) arrays where the prefetching variant (sbpm_lower_bound/sbp_lower_bound) can hide memory latency
- Latency-critical code dominated by branch mispredictions from unpredictable/random query patterns
- Willing to vendor a small header and pin toolchain/flags rather than depend on portable stdlib codegen

**Skip it when:**
- Comparators over strings or other multi-instruction keys - the author's own numbers show it is slightly slower than std::lower_bound for 8-byte string keys in every tested configuration
- Building with GCC, or clang without the cmov flag - branchless codegen doesn't happen and performance is roughly parity with std::lower_bound
- Anything outside x86-64 - all reported gains are clang+cmov on one Haswell-class -march target; no ARM/other-arch data exists
- Only forward iterators are available - despite the 'ForwardIt' template parameter name, the implementation uses operator[], so it actually requires random-access iterators
- Codebases wanting an actively maintained dependency - last commit July 2023, 24 stars, zero issues or PRs to gauge real-world robustness beyond the author's own benchmark

**Integration:** header-only · none (only <bit>, <functional> from the standard library) · C++20 (repo's own build commands use -std=c++20; functions are constexpr); benchmarked with g++-10 / clang++-10 · x86-64 only in the evidence given (branchless gains shown solely with clang + -mllvm -x86-cmov-converter=false, -march=haswell); GCC does not produce the branchless path

**Vs siblings:** Pick sb_lower_bound over the SIMD/layout-restructuring siblings (FastBinarySearch, Lemire's SIMD Quad search, simdsearch) when you want a minimal single-header, std::lower_bound-signature-compatible branchless search for primitive keys on clang/x86-64 without SIMD intrinsics or a precomputed/cache-friendly array layout; pick scandum/binary_search instead if your actual baseline is C's bsearch() rather than std::lower_bound.

**Gotchas:**
- The 'ForwardIt' template parameter is misleading: the body indexes with first[half], so only random-access iterators actually work
- The headline 2x/1.84x numbers require clang plus -mllvm -x86-cmov-converter=false; without that flag (or under gcc) it's roughly as fast as std::lower_bound
- Makes k+1 comparisons per call (2^k <= n < 2^(k+1)) versus std::lower_bound's average log2(n+1), so it can lose on cheap comparators even when branch prediction isn't the bottleneck
- The prefetching variants (sbp_/sbpm_lower_bound) hardcode an L2-sized 256KB threshold and cache-line constants tuned to the author's own benchmark machine

**Status:** Abandoned since its last commit on 2023-07-06 (repo not archived, but no open issues or PRs exist to gauge upkeep); MIT-licensed via LICENSES/MIT.txt and per-file SPDX headers even though GitHub's own license detector reports none, and it's small and header-only enough to vendor as-is.

[repo](https://github.com/mh-dm/sb_lower_bound) · [benchmark](https://mhdm.dev/posts/sb_lower_bound/)

##### scandum/binary_search (monobound / boundless binary search)  `C`  `Unlicense`  `stale`  `Tier C`

C binary-search variants; monobound_bsearch() is a bsearch()-compatible drop-in ~1.4-2.35x faster than libc bsearch().

**Beats:** bsearch() (C standard library) — In the repo's own monobound_bsearch() vs. libc bsearch() table (gcc -O3, GCC 7.5.0 on Ubuntu 18.04 under WSL2, CPU stated only as 'Intel i3 quad-core', 1,000 runs best-of, 32-bit integer arrays), monobound_bsearch() beats bsearch() by roughly 1.4x-2.35x across sizes from 10 to 10,000,000 elements (e.g. 0.000136s vs 0.000202s at 10 elements; 0.002641s vs 0.003784s at 10,000,000). The more prominently stated 'two to four times faster' and 'up to 60% faster' README claims are against the repo's own standard_binary_search (a textbook algorithm), not against bsearch() or std::binary_search.

**How:** Monobound search replaces the classic bot/mid/top bookkeeping with a single running offset and a size that is halved each iteration, giving one key check, one integer compare and dynamic loop unrolling (README claims this unrolling, not fewer comparisons, is the real source of the gain, unlocking further compiler/CPU-level optimization). Boundless binary search similarly drops the explicit upper-bound variable tracked by the textbook algorithm to cut per-iteration integer assignments, worth about 20% per the README. A GitHub issue (#7) challenged the README's explanation of why unrolling helps (ILP/branch-removal wording), but the reporter walked the objection back in the same thread; the loop-unrolling mechanism itself is not otherwise disputed in what I read.

**Use it when:**
- Sorted 32-bit-int (or similarly cheap-to-compare primitive) arrays where code already calls libc bsearch() and you want a same-signature swap with a measured 1.4-2.35x speedup (repo's own gcc -O3 benchmark).
- Small-to-medium arrays (well under 1M elements), where the README reports the largest monobound gains ('two to four times faster' vs the repo's own textbook binary search, not vs bsearch()).
- C or C-callable codebases that can vendor a single small .c file under a public-domain-equivalent license (Unlicense) with zero third-party dependencies.
- Builds that reliably use -O1/-O2/-O3 — the README states monobound 'degrades badly under -O0'.
- Cases needing a stable binary search (README states all variants return the rightmost index on duplicate keys) and defined zero-length-array behavior.

**Skip it when:**
- C++ code calling std::lower_bound/std::binary_search/std::equal_range directly — there's no header-only C++ template here; you'd have to hand-port the algorithm into your own templated function.
- Workloads wanting SIMD/vectorized search or the largest possible speedups on very large arrays — sibling entries (FastBinarySearch, SIMD Quad, simdsearch, sb_lower_bound) target that more directly with more rigorous, more recent hardware.
- Projects needing active maintenance — last commit 2025-06-20, single maintainer, no releases/tags/CI, no test suite beyond the benchmark harness.
- Decisions that need current-hardware evidence — every published number is from one 2018-era Ubuntu 18.04 / GCC 7.5.0 WSL2 machine described only as 'Intel i3 quad-core' (no exact SKU); real gains on modern CPUs/compilers are unverified here.
- Non-integer or expensive-comparator keys — all headline numbers are for 32-bit integer comparisons; the README only speculates (unbenchmarked) that the deferred-equality tradeoff changes for string comparisons.

**Integration:** source-drop · none (standard C headers only: stdlib.h, stdio.h, string.h; sys/time.h and time.h are used only by the benchmark harness, not the search functions themselves) · not documented beyond 'C' compiled with gcc -O1/-O2/-O3 (benchmarks used GCC 7.5.0); no C99/C11 requirement is stated · not documented; only benchmarked on x86-64 Linux (WSL2/Ubuntu 18.04). The code itself is portable C with no architecture-specific intrinsics in the two files read

**Vs siblings:** Pick this when you need a bsearch()-compatible C drop-in with a same-signature comparator interface and are fine with a dated but directly-against-bsearch() benchmark; sb_lower_bound, FastBinarySearch, and SIMD Quad/simdsearch all target C++ std::lower_bound/std::binary_search or memmem with more recent, more rigorous hardware evidence and larger claimed speedups, and are the better pick if you can use C++ templates or need SIMD-scale gains.

**Gotchas:**
- monobound_binary_search must be compiled with -O1/-O2/-O3; the README explicitly warns it 'degrades badly under -O0'.
- Default semantics are stable/rightmost-index on duplicate keys (per README) — check this matches your needs if you actually want lower_bound-style leftmost-index behavior.
- Quaternary, monobound-interpolated and adaptive variants are described in the README prose but only monobound_interpolated_search appears in the benchmark tables I read; quaternary/adaptive have no benchmark numbers in this repo.
- Issue #7 disputes part of the README's technical explanation for the speedup (ILP/branch-removal wording); worth a skim before citing the 'why' verbatim, though the numbers themselves aren't challenged there.

**Status:** Stale but stable: last commit 2025-06-20, single-maintainer repo with no releases, CI, or test suite beyond the benchmark harness itself; Unlicense (public domain equivalent) and a single small .c file make it cheap to vendor and audit despite the inactivity.

[repo](https://github.com/scandum/binary_search) · [benchmark](https://github.com/scandum/binary_search/blob/master/README.md)

#### sequence-containers

##### eastl::vector (EASTL)  `C++`  `BSD-3-Clause`  `active`  `Tier C`

EA's from-scratch STL reimplementation for games; eastl::vector targets faster push_back/indexing than std::vector.

**Beats:** std::vector — The only available measurement is a first-party 2007 EA/WG21 committee paper (N2271, evidence tier C) comparing eastl::vector<uint64> against std::vector: push_back was 1.63x faster on Windows/Pentium4/VC8, 2.18x on a 64-bit PowerPC console/VC7, 1.02x on Linux/Pentium4/GCC4.1/libstdc++, and 1.59x on Mac G5 PowerPC/GCC4.0/libstdc++; operator[] on Linux/libstdc++ was 1.29x faster; sort on Linux/libstdc++ was 0.92x (slower than std::sort).

**How:** EASTL avoids the deep, virtual-free but call-heavy chains that make debug-build STL slow, so its win is largest in unoptimized builds and on weak historical STL implementations (MSVC VC7/VC8, console STL). For trivially-copyable element types it uses memcpy/memmove during vector reallocation instead of invoking copy/move constructors per element (documented in doc/Gotchas.md). It also guarantees no allocation for a newly-constructed empty container and supports fully disabling exception handling, removing that overhead from the container/allocator path.

**Use it when:**
- Game/console codebases where debug (unoptimized) container performance matters and you can standardize on one non-standard container library across all target platforms
- Workloads dominated by push_back/reallocation of trivially-copyable structs, where the memcpy/memmove optimization applies
- You also want fixed_vector/intrusive_list-style zero-allocation containers alongside vector, not just a faster vector
- Targeting older or console toolchains (VC7/VC8-era, GCC 3.x+) where std STL implementations were measurably weak
- You're comfortable vendoring a large source-drop plus its EABase dependency rather than a single header

**Skip it when:**
- You need a literal drop-in for std::vector with zero porting cost: allocator model, exception semantics, and operator= behavior differ
- You're on an EASTL release older than 3.27.00 (Oct 2025): eastl::vector::push_back(v.back()) (self-referential push_back) silently corrupted data on reallocation (issue #524), fixed only in that release
- Concurrent writers without your own locking: EASTL containers are not thread-safe for mutation from multiple threads, same as std::vector
- You need certainty of a speedup on current hardware: the only public numbers are a first-party 2007 WG21 paper (evidence tier C) on Pentium 4/PowerPC-era hardware and compilers; libstdc++ push_back gain was only 1.02x and eastl::sort was 0.92x (slower) than std::sort on libstdc++
- Sort-heavy workloads on libstdc++-class standard libraries, where the same paper showed EASTL losing to std::sort

**Integration:** source-drop · EABase (EA's base config/type-traits header library; CMakeLists.txt fetches it via FetchContent) · C++14 per CMakeLists.txt (target_compile_features cxx_std_14), but include/EASTL/vector.h currently uses unguarded `if constexpr`, which warns/fails below C++17 (open issue #587) -- C++17 recommended in practice · any C++14+ compiler, 32-bit and 64-bit; no OS-specific code path required, historically used across PC, console, and Mac/Linux toolchains

**Vs siblings:** Pick eastl::vector when you want one consistent container ecosystem (fixed_*, intrusive_*, allocator model) across an entire codebase, especially on older/console toolchains, rather than swapping in a single faster vector type. For a narrowly-scoped, better-evidenced vector replacement alone, fast_vector or veque have more direct current benchmarks; plf::colony is the better pick if the workload is erase-heavy rather than push_back-heavy.

**Gotchas:**
- eastl::vector::push_back(v.back()) (self-referential push_back) silently corrupted data on reallocation before release 3.27.00 (Oct 2025) -- pin to >=3.27.00 (issue #524)
- vector::operator=() does not copy the source container's allocator, unlike some std implementations
- vector::size() is computed by pointer subtraction and can trigger an integer division when sizeof(T) isn't a power of two
- Overriding the global allocator requires supplying EASTL's two custom operator new[] overloads, not a standard C++ allocator

**Status:** Actively maintained by EA (latest release 3.27.01, Nov 2025), BSD-3-Clause, 9,367 stars; usable via source-drop or CMake, but it's a large, non-trivial dependency (EABase plus a big header/source tree), not a lightweight vendor-in.

[repo](https://github.com/electronicarts/EASTL) · [benchmark](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2271.html)

##### fast_vector (sigerror/fast-vector)  `C++`  `MIT`  `abandoned`  `Tier C`

Header-only C++17 vector without zero-init, exceptions, or a real allocator; beats std::vector on trivial-type push_back workloads.

**Beats:** std::vector — On an Intel i7-4720HQ (Visual Studio 2017, MSVC STL, Windows 10), Google Benchmark over 10,000 elements showed fast_vector roughly 1.4-2.1x faster than std::vector for trivial-type push_back, reserve+push_back, and push_back+pop_back, but only about 1.0-1.3x for non-trivial types, with non-trivial reserve+push_back essentially a wash (88,303ns vs 88,671ns).

**How:** For trivial T, reserve/resize skip the construct/destruct loops std::vector runs and grow via realloc() in place instead of malloc+copy+free; push_back writes trivial elements by assignment rather than placement-new. Bounds and precondition checks are assert()-based, so unlike std::vector's exception-safety machinery they cost nothing under NDEBUG. There is no SIMD, custom allocator, or branchless logic involved — the win is purely from removing zero-initialization and object-lifetime bookkeeping that trivial types don't need.

**Use it when:**
- Hot loops doing push_back/emplace_back on many trivial (POD) elements where leaving memory uninitialized (instead of value-initialized) is acceptable
- Codebases already built assertions-first/exceptions-off (e.g. game or low-latency style code) that want realloc-based growth instead of malloc+copy+free
- Header-only vendoring into a C++17 project where pulling in a full container library is undesirable
- Non-trivial types specifically via emplace_back (~1.3x measured) rather than push_back+pop_back or reserve+push_back, which show little to no win for non-trivial T

**Skip it when:**
- Any code that copies or copy-assigns a fast_vector<T> where sizeof(T) > 1: the copy ctor/operator= call memcpy(dst, src, other.m_size) using element count instead of byte count, under-copying data (open issue #2, unresolved since 2019)
- operator=(const fast_vector&) never frees the destination's existing allocation before overwriting the pointer, leaking the old buffer on reassignment
- Anything needing insert()/erase() at arbitrary positions, at(), swap(), comparison operators, or initializer-list construction — none exist (open issue #1)
- Release builds where out-of-bounds safety matters: assert() is a no-op under NDEBUG, so operator[]/front/back/pop_back have zero bounds checking in release
- Non-trivial-type reserve+push_back workloads specifically: the README's own numbers show std::vector 88,303ns vs fast_vector 88,671ns, i.e. no measured win

**Integration:** header-only · none (only <cassert>, <cstdlib>, <cstring>, <new>, <type_traits> from the standard library) · C++17 (stated in README); benchmarked with Visual Studio 2017, no other compiler/version documented · any — portable C++17, no platform-specific intrinsics or code observed in fast_vector.h

**Vs siblings:** Pick it over plf::colony/plf::list/veque/EASTL only when you want a minimal, header-only, std::vector-shaped container purely for trivial-type push_back-heavy code and can tolerate its two open correctness bugs; veque and plf::colony/plf::list report larger, more thoroughly benchmarked wins for their respective access patterns, and EASTL is a more mature, allocator-aware drop-in that fast_vector doesn't match.

**Gotchas:**
- Copy constructor and copy-assignment memcpy the wrong byte count (other.m_size instead of other.m_size * sizeof(T)) for trivial T larger than 1 byte — filed as issue #2, still open at last commit
- Copy-assignment operator leaks the destination's prior allocation: it never calls std::free on the old m_data before reassigning the pointer
- grow_factor is advertised as 'modifiable' but is a static constexpr size_type = 2 baked into the header, not a template or runtime parameter — changing it means editing the source
- reserve()/resize() assert preconditions (new_cap > capacity; count != size) that are silently skipped in release builds rather than raising an error

**Status:** Abandoned since its last commit on 2019-04-20, with two unresolved open issues (a copy-constructor memcpy bug and a missing insert/erase request); MIT-licensed, 21 stars, and small enough — one header — to vendor and patch yourself.

[repo](https://github.com/sigerror/fast-vector) · [benchmark](https://github.com/sigerror/fast-vector)

##### veque  `C++`  `BSL-1.0`  `active`  `Tier C`

Header-only C++20 double-ended vector: std::vector's contiguous storage plus std::deque's fast front growth.

**Beats:** std::vector; std::deque — In the project's own performance/main.cpp harness (g++-9 -O3, CPU/hardware unstated), veque totaled 2,492,954us across seven operations vs std::vector's 10,248,719us (~4.1x) and std::deque's 3,480,344us (~1.4x); the largest single gap was front growth, where std::vector's O(n)-per-op reallocation cost 6,685,217us vs veque's 30,739us (~217x), while veque itself was slower than std::deque on both front growth (30,739 vs 16,386us) and back growth (552,027 vs 342,218us) in the same run.

**How:** Unused capacity is kept on both sides of the live elements instead of only at the back, so front insertion/growth is amortized O(1) like std::deque instead of std::vector's O(n) full-buffer shift. Arbitrary-position insert/erase can shift elements toward whichever end (front or back) is closer, roughly halving the average number of elements moved compared to std::vector's always-shift-to-back behavior. A ResizeTraits policy (fast_resize_traits by default) controls this trade-off and lets callers dial down to std::vector-style behavior (vector_compatible_resize_traits, std_vector_traits, no_reserve_traits) when they need std::vector's iterator-invalidation guarantees instead.

**Use it when:**
- Vector-like contiguous container that also needs frequent push_front/pop_front or resize_front, not just back growth
- Insert/erase happen near either end of the sequence, not predominantly in the middle, so closest-side shifting pays off
- C++20 codebase (concepts/ranges already required) that can take a single dependency-free header
- Want tunable memory-vs-invalidation behavior per container instantiation via the ResizeTraits template parameter
- Want a strong-exception-guarantee pop-and-return primitive (pop_back_element/pop_front_element)

**Skip it when:**
- Toolchain is pre-C++20 (header requires <concepts> and <ranges>); no C++14/17 build exists despite a README wishlist entry
- Memory is tight: veque reserves slack at both front and back by default, so its footprint exceeds std::vector's at the same size()
- Workload is back-growth-heavy: in the project's own benchmark veque was slower than std::deque on back growth (552,027 vs 342,218us) and front growth (30,739 vs 16,386us)
- Code depends on std::vector's partial iterator-invalidation guarantees on insert/erase; the default fast_resize_traits invalidates all iterators/references on those ops (opt into vector_compatible_resize_traits to get std::vector's rules back, at the cost of the closest-side speedup)
- Need std::vector<bool>'s bit-packed specialization; veque<bool> is explicitly not specialized
- Project is small and thinly used (128 stars, ~10 forks, effectively one author) with a past heap-corruption bug in assign() (fixed 2023) — worth vetting before production use

**Integration:** header-only · none (standard library only: <algorithm>, <concepts>, <cstddef>, <cstring>, <iterator>, <limits>, <ranges>, <ratio>, <string>, <type_traits>, <stdexcept>, <utility>) · C++20 (uses <concepts> and <ranges>); the benchmark's sample-output comment is labelled g++-9, which predates full <ranges> support, so that sample may be stale relative to current code · not documented; no platform-specific code observed, standard C++20 only

**Vs siblings:** Pick veque over the catalogued siblings (plf::colony/hive, plf::list, eastl::vector, fast_vector) when you need std::vector's contiguous, ordered, drop-in-ish interface but also do real front-side growth (push_front/pop_front/resize_front): eastl::vector and fast_vector only optimize back-end std::vector operations, and plf::colony/plf::list trade away contiguous ordered storage entirely.

**Gotchas:**
- Default ResizeTraits (fast_resize_traits) invalidates ALL iterators and references on any insert/erase, unlike std::vector's partial invalidation — use vector_compatible_resize_traits for std::vector's guarantees
- veque<bool> is not specialized/bit-packed, unlike std::vector<bool>
- Closed issue #9 reported heap corruption after veque destruction, triggered via assign(); maintainer marked it fixed in a later release (2023-06-20) — pin a recent commit rather than an old tag
- fast_resize_traits preallocates slack at both ends by default, so memory use is higher than std::vector even at equal size(); no_reserve_traits removes that at the cost of resize speed

**Status:** Actively maintained (last commit 2026-09-15, BSL-1.0 license) but small and effectively single-author (128 stars, ~10 forks); a past heap-corruption bug in assign() was reported and fixed, so use a current commit rather than an old release.

[repo](https://github.com/Shmoopty/veque) · [benchmark](https://raw.githubusercontent.com/Shmoopty/veque/master/performance/main.cpp)

#### serialization-json

##### blazingio  `C++`  `MIT`  `stale`  `Tier C`

Header-only mmap+SIMD std::cin/cout replacement, ~5x faster than libstdc++ iostream for competitive-programming I/O.

**Beats:** iostream (std::cin/std::cout, with sync_with_stdio(false)) — blazingio's own CI benchmarks it against std::cin/std::cout with sync_with_stdio(false) ('iostream_detached') on GitHub Actions ubuntu-latest x86_64 runners, g++ -std=c++17 -O2 (exact gcc version and CPU model not recorded). Across the 74 read/write test-and-mode pairs in benchmark-results/linux-x86_64.json (opened and spot-checked directly), per-test speedup ranges from about 1x (plain line input) to about 80x (bitset input), geomean about 4.7x; the README's headline '5x faster' figure describes typical integer/string I/O on Linux+libstdc++, with larger geomean speedups reported on macOS/libc++ (~22x) and Windows/MSVC (~15x) because those iostream implementations are slower.

**How:** It avoids libstdc++'s buffered streambuf and virtual-dispatch-heavy formatting entirely: the whole input is mmap'd once, then parsed and printed with hand-written SIMD kernels (AVX2, SSE4.1, or NEON -- picked at compile time -- with a scalar SWAR/bit-trick fallback) that scan for whitespace and convert digit or bitset runs a vector-width at a time. There's no locale handling, no exceptions, and no runtime CPU-feature dispatch, and formatting is restricted to fixed decimal, 12-digit-fraction output.

**Use it when:**
- Competitive-programming/judge submissions (Codeforces, ejudge, etc.) where whole-program I/O time is scored and you control the entire source.
- Heavy reading/writing of integers, floats, strings, std::complex<T>, or std::bitset<N> where sync_with_stdio(false) iostream is still the bottleneck.
- Source-size-limited judges: copy-paste the pre-minified blazingio.min.hpp (single file, includes attribution link).
- Target CPU's SIMD extension is known ahead of time -- x86_64/i386 with AVX2 or SSE4.1, or aarch64 with NEON.
- You can tolerate UB on malformed input in exchange for maximum throughput on a single, short-lived process.

**Skip it when:**
- Any production or user-facing code -- the README explicitly warns invalid input can trigger UB 'including security vulnerabilities'.
- Code needs real std::istream/ostream (templates, manipulators, locale, non-decimal bases, precision/width, exception-based error handling).
- Need >1 ulp float accuracy or std's scientific notation for magnitudes below 1.
- Multi-threaded I/O, or judges/hosts where the assumed SIMD extension might be absent (no runtime detection; wrong assumption is UB).
- Very large output (roughly >0.5 GiB, or >24 MiB on old-style ejudge problems) may be truncated depending on the judge.

**Integration:** header-only (ships a pre-generated single-file blazingio.min.hpp, plus a Python generator (minimize.py/common.py + config) to build custom platform/feature configurations) · none beyond the C++ standard library and platform headers (sys/mman.h, unistd.h on Linux/macOS; windows.h, io.h on Windows) · C++17 (test.py compiles with -std=c++17); CI builds with g++, and also exercises clang/MSVC per repo workflows · x86_64, i386 (AVX2 or SSE4.1 optional), aarch64 (NEON optional) on Linux/macOS/Windows; SIMD ISA is fixed at build time, no runtime CPU dispatch

**Vs siblings:** Only scnlib is a close analog (std::stringstream/sscanf replacement); scnlib returns errors and stays safe on bad input, making it viable in production, while blazingio is faster and cin/cout-syntax-compatible but explicitly UB-on-error and competitive-programming-only -- pick blazingio when you want near-zero code changes from std::cin/cout, need bitset/complex I/O, and can accept unsafe behavior for maximum throughput in a single-shot batch program. The JSON-serialization siblings (cjson.cpp, json.cpp, Cap'n Proto, etc.) solve a different problem (structured data, not whole-program scalar I/O) and aren't real alternatives.

**Gotchas:**
- SIMD extension is chosen at compile time via the config file's architecture= list; running on a CPU lacking that extension is undefined behavior, not a graceful fallback.
- No error handling beyond EOF detection (if (std::cin)); malformed input is UB, per the README's own security warning.
- std::bitset<N> input requires at least N input characters -- std zero-pads shorter input, blazingio does not.
- Output is capped at roughly 0.5 GiB generally, 24 MiB on old-style ejudge-based judges.

**Status:** Effectively unmaintained (last commit 2024-11-23, zero open issues, one trivial closed issue) but MIT-licensed, small when pre-minified, and self-contained enough to vendor as-is; usability is 'copy blazingio.min.hpp and go', not a library you'd integrate into a build system.

[repo](https://github.com/purplesyringa/blazingio) · [benchmark](https://raw.githubusercontent.com/purplesyringa/blazingio/master/README.md)

##### Cap'n Proto  `C++`  `MIT`  `active`  `Tier C`

Zero-copy binary serialization/RPC system: wire format equals in-memory layout, beating RapidJSON-based JSON serialize/deserialize by ~2.8x/1.6x.

**Beats:** JSON serialization (RapidJSON) — On chronoxor/CppSerialization's fixed trading-object shootout (accounts/balances/orders) on an Apple M1 Pro under macOS with CppBenchmark's 'release' configuration (compiler and flags not stated), Cap'n Proto serialized in 247ns to 208 bytes and deserialized in 184ns, versus RapidJSON-based JSON at 696ns serialize / 291ns deserialize / 301 bytes — about 2.8x faster to serialize and 1.6x faster to deserialize than JSON in that fixture; independently confirmed against the current CppSerialization README table.

**How:** The wire format is identical to the in-memory layout: messages live in arena-allocated segments (BuilderArena/SegmentBuilder) navigated by struct/list/far pointers, so writing is just placing fields directly and reading is pointer validation with no separate decode pass. This skips the DOM-build-then-stringify step JSON needs to write and the parse-then-materialize step JSON needs to read, which is consistent with the benchmark's bigger win on serialize (~2.8x) than deserialize (~1.6x, and that JSON figure excludes JSON's own parse cost, reported separately at 771ns).

**Use it when:**
- C++ service-to-service messaging or RPC (not just wire format) where you can adopt promise pipelining via capnp-rpc
- Structured, schema-evolving payloads shared across services/languages, where a build-time codegen step is acceptable
- Read-heavy or partial-read workloads over a message buffer, since Cap'n Proto readers touch only the fields accessed instead of materializing the whole object
- Trading/finance-shaped fixed object graphs like the benchmarked one (accounts, balances, orders) where both serialize and deserialize latency matter
- Cases where message size matters too: 208 bytes here vs. JSON's 301 bytes for the same object

**Skip it when:**
- You need a human-readable, greppable, or hand-editable wire format (logs, configs, ad hoc debugging) — stay with JSON
- Pure C++-to-C++ traffic with no RPC/schema-evolution need and raw speed is the only goal — zpp::bits (34ns/37ns in the same suite) is ~7x faster with no schema compiler
- Small one-off tools/scripts where adding a .capnp schema and `capnp compile` build step isn't worth the setup
- Teams needing a dynamic/schema-less path in C++ — the generated-code path is the primary supported workflow
- Long-lived buffer lifetime is hard to guarantee — zero-copy readers require the backing buffer to outlive them

**Integration:** static lib | shared lib (plus a codegen step: `capnp compile` generates .h/.c++ from your .capnp schema, which you then build) · none required for core capnp/kj; optional deps only for extras — OpenSSL (kj-tls), zlib (kj-gzip), Brotli — and the `capnp` schema compiler is needed at build time · Stable 1.0 line (`master` branch): C++14, GCC 5+/Clang 5+/MSVC 2017+. The repository's current default branch (`v2`, in active development) raises this to C++20, built with -std=gnu++23/​/std:c++23preview · Linux, macOS, Windows (per CMake/Bazel build files and the CppSerialization benchmark's cross-platform build); no SIMD/CPU-arch requirement documented

**Vs siblings:** Pick Cap'n Proto over the JSON-focused siblings (DAW JSON Link, cjson.cpp, json.cpp, Tachyon.JSON, utl::json) when you can drop JSON as the wire format entirely and want cross-language schemas plus an RPC layer, not just a faster JSON parser. Pick zpp::bits instead when you stay C++-only and don't need RPC or schema evolution — it's markedly faster in the same benchmark (34ns/37ns vs. 247ns/184ns) with no schema compiler.

**Gotchas:**
- Message buffers must outlive every Reader built from them — readers view the buffer directly (zero-copy), so freeing or reusing it early dangles
- MessageBuilder::getOrphanage() is documented in-source as not thread-safe even though adjacent accessors look read-only
- Binary wire format isn't eyeball-debuggable like JSON; inspecting a message needs `capnp decode`/`capnp convert` against the schema
- Schema changes require rerunning `capnp compile` and rebuilding generated headers; there's no schema-less mode on the standard C++ path

**Status:** Actively maintained (commits as of the record date) under the MIT license, 13.2k stars, used in production by Cloudflare and Sandstorm; MIT terms make it freely redistributable, but it is not a small vendor-in-header — expect to build libcapnp/libkj and wire the capnp compiler into your build.

[repo](https://github.com/capnproto/capnproto) · [benchmark](https://github.com/chronoxor/CppSerialization)

##### utl::json (part of the UTL header-only library collection)  `C++`  `MIT`  `active`  `Tier C`

Header-only C++17 JSON library, 2-4x faster than nlohmann::json at parsing and serializing; RapidJSON still wins parsing.

**Beats:** nlohmann::json (also PicoJSON; beats RapidJSON on serialization tasks only, loses to it on most parsing tasks) — First-party nanobench tables in docs/module_json.md (no compiler, flags, or CPU model given) show utl::json parsing 2.2x faster than nlohmann::json on twitter.json (402.89 vs 182.76 op/s) and 2.4x on apache_builds.json (2,134.76 vs 881.03 op/s), and serializing 1.6-1.9x faster on those same files. RapidJSON parses faster than utl::json on numbers.json (1.29-1.45x), twitter.json (2.07-2.22x), apache_builds.json (1.63-1.72x) and database.json (1.30-1.40x), and roughly ties it at serializing apache_builds.json.

**How:** Single-pass recursive-descent parser with no separate tokenizing stage: node type is decided from the first character inside Parser::parse_node(), so the document is scanned once while the recursive Node tree is built. Numbers go through std::charconv's from_chars/to_chars, with a locale-based istringstream fallback only on libc++ <20 (no floating-point from_chars there). The header's own dev docs state it uses no intrinsics or compiler-specific code anywhere, so the win over nlohmann comes from a leaner single-scan design and std::charconv, not vectorization -- which is also why hand-tuned RapidJSON still beats it on most parsing runs.

**Use it when:**
- Already modeling data with std::map/std::vector/std::string and want JSON that interoperates with those containers directly, no custom container API to learn
- Want recursive struct<->JSON reflection (UTL_JSON_REFLECT macro) without hand-writing serializers
- Currently on nlohmann::json and want a similarly-shaped, header-only replacement that's 2.2-4x faster parsing and 1.6-2.4x faster serializing, without needing RapidJSON/simdjson-class throughput
- Need a tiny dependency footprint: single header, under 1k lines, MIT, no third-party deps
- Workload looks like the benchmarked files (twitter.json/apache_builds.json/strings.json/numbers.json shape) rather than deeply object-keyed documents

**Skip it when:**
- Baseline to beat is RapidJSON, not nlohmann: RapidJSON parses faster on 3 of 4 benchmarked files (numbers.json, twitter.json, apache_builds.json), only strings.json parsing favors utl::json
- Object-heavy / heavily-keyed documents: object_type is std::map, so map insertion/iteration dominates runtime -- the author names this the library's main perf weak point
- Need SIMD-class throughput (simdjson, Glaze, yyjson): utl::json deliberately avoids intrinsics and compiler-specific code for portability, at the cost of top-end speed
- Need distinct integer vs float JSON numbers: number_type is a single double for every JSON number (open, unaddressed feature request #2), so integers beyond 2^53 lose precision
- Building with Clang + libc++ < 20: falls back to a much slower locale-based istringstream number parser (check UTL_JSON_FROM_CHARS_FALLBACK), narrowing or erasing the published speedup on that toolchain (mostly a macOS issue)

**Integration:** header-only · none (self-contained single header; nlohmann/PicoJSON/RapidJSON are only benchmark-harness comparisons, not runtime deps) · C++17; MSVC needs /Zc:preprocessor for the UTL_JSON_REFLECT macro to expand correctly · any -- CI covers Windows, Ubuntu, macOS, FreeBSD; no intrinsics or architecture-specific code in the parser

**Vs siblings:** Pick utl::json over cjson.cpp / json.cpp / DAW JSON Link / Tachyon.JSON when the goal is STL-container-backed Node values plus macro-based recursive struct reflection in one sub-1k-line header; pick one of those siblings instead when the target baseline is RapidJSON or simdjson rather than nlohmann, since utl::json's wins are consistent only against nlohmann::json and PicoJSON.

**Gotchas:**
- object_type is std::map<std::string, Node, std::less<>> — object-heavy JSON pays std::map insertion/iteration cost; documented as the main performance weak point
- number_type is one double for every JSON number, no separate integer type; a feature request for int/float split is open and unresolved (issue #2)
- from_string()/from_file() default recursion_limit=100 to cap stack depth against maliciously deep nesting, throwing std::runtime_error past the limit — raise it if legitimate documents nest deeper
- Clang + libc++ <20 silently swaps in a slower locale-based float parser (no std::from_chars); detect with #ifdef UTL_JSON_FROM_CHARS_FALLBACK before trusting benchmark numbers on that toolchain

**Status:** Actively developed (repo pushed 2026-09-19) but the published master branch — what a consumer actually pulls — last moved 2025-12-08; MIT-licensed, 336 stars, not a fork, small enough to vendor as one header.

[repo](https://github.com/DmitriBogdanov/UTL) · [benchmark](https://github.com/DmitriBogdanov/UTL/blob/master/docs/module_json.md#benchmarks)

##### zpp::bits  `C++`  `MIT`  `active`  `Tier C`

Header-only C++20 binary serializer using compile-time aggregate reflection; no schema, no codegen, faster than JSON via RapidJSON in third-party benchmarks.

**Beats:** JSON serialization (RapidJSON) — In chronoxor/CppSerialization's trading-object-graph benchmark on Apple M1 Pro (macOS, CppBenchmark 'release' build, compiler/flags otherwise unstated), zpp::bits serialized in 34ns and deserialized in 37ns for a 130-byte message, versus RapidJSON-based JSON at 696ns/291ns for a 301-byte message — about 20x/7.9x faster. This compares a binary format to JSON text rather than the same facility, and the 291ns JSON-deserialize figure excludes a separately reported 771ns JSON-parse step.

**How:** Member enumeration happens at compile time via structured bindings or an explicit `zpp::bits::members<N>` count, so there is no RTTI or runtime reflection, and the library is written almost entirely `constexpr` so the compiler can inline and specialize per type. It writes fields directly into a contiguous byte buffer (vector, array, or span) with no intermediate DOM/tree, unlike a JSON library that must build an object model. Field sizes can be fixed-width or opted out entirely, avoiding the text formatting and number parsing that JSON serialization pays for on every field.

**Use it when:**
- Both ends of the wire are C++ and you control the schema, so a text/interop format isn't needed
- Latency-sensitive object graphs (trading, telemetry) with primitives, vectors, optionals, or variants where nanosecond-scale serialize/deserialize matters
- C++20 toolchain available (CI covers GCC 11-16 and Clang 13/17-22 on Linux and macOS) and types are aggregates or structured-binding-friendly
- Want a single vendorable header (no build step, no schema compiler, no external dependency)
- Need simple RPC (request/response dispatch) without standing up a separate schema/IDL toolchain

**Skip it when:**
- Need JSON or another human-readable/interoperable wire format — output is a custom binary layout, not JSON
- Need cross-language interop without hand-porting the format — no schema/codegen like Protobuf, Cap'n Proto, or FlatBuffers provide
- Targeting MSVC — CI does not cover it and users have hit internal compiler errors (issue #99) and VS2019 compile failures (issue #80)
- Object graph contains std::vector<bool> — fails to compile as of the open issue #153 (std::_Bit_reference binding error)
- Smallest possible message size matters more than speed — SimpleBinaryEncoding produced smaller messages in the same benchmark shootout

**Integration:** header-only · none (optionally detects and uses zpp::throwing if that header is present, for coroutine-based error handling) · C++20; CI tests GCC 11-16 and Clang 13, 17-22 on Ubuntu and macOS (Clang 17/18) — MSVC not in CI and has open compile-failure/ICE reports · x86-64 and aarch64 (Linux and macOS in CI); no SIMD or architecture-specific intrinsics used

**Vs siblings:** Pick over Cap'n Proto when you don't want an IDL/schema-compiler step and want the fastest raw numbers in the same chronoxor/CppSerialization suite (34ns/37ns vs Cap'n Proto's 247ns/184ns); pick over the JSON-based siblings (cjson.cpp, DAW JSON Link, Tachyon.JSON, utl::json) whenever human-readable or cross-language JSON output isn't required and both ends are C++.

**Gotchas:**
- std::vector<bool> serialization does not compile (open issue #153)
- Non-aggregate types need `using serialize = zpp::bits::members<N>;` (member count stated explicitly) or an ADL `serialize()` overload before C++26 lifts this requirement
- RPC layer had a reported memory-leak bug (issue #188, closed) — confirm the fix is in the version you pin
- Raw/non-owning pointers and null pointers are intentionally unsupported (README 'Limitations'); use std::optional instead

**Status:** Actively maintained (last commit 2026-08-09; CI runs on push/PR and a daily cron against GCC 11-16 and Clang 13-22); MIT-licensed single 6,000-line header, trivially copyable/vendorable into a project with no package manager or build step.

[repo](https://github.com/eyalz800/zpp_bits) · [benchmark](https://github.com/chronoxor/CppSerialization)

#### small-buffer-and-strings

##### FastString  `C++`  `MIT`  `stale`  `Tier C`

Fixed-capacity, stack-allocated, constexpr string class that avoids the heap allocation std::string needs past SSO.

**Beats:** std::string — On MSVC 19.28.29334.0 (Windows; CPU reported only as "8 x 1498 MHz" with L1d 48KiB x4, L1i 32KiB x4, L2 512KiB x4, L3 8MiB — no CPU model given, no optimization flags stated), Google Benchmark shows constructing a short string from const char* averaging 498ns wall / 148ns CPU for std::string versus 46.9ns / 16.3ns for fixed_size_str<15> (~10.6x on wall time), and constructing a 45-character string in 1048ns versus 153ns (~6.8x). Append is roughly at parity (190ns vs 164ns for a fixed_size_str<63> case) while a small-buffer append case is slightly slower for FastString (50.0ns vs 61.5ns).

**How:** Storage is a single fixed `CharT buffer_[max_length + 1]` plus a `std::size_t` length counter, both on the stack, so there is never a heap allocation, unlike std::string once an input exceeds small-string-optimization capacity (typically ~15-22 chars). Construction, append, and reset are just `Traits::copy`/`std::copy` calls capped at the compile-time capacity, and most member functions are `constexpr`, so short/compile-time-known strings can be folded away entirely. The repo's own Godbolt comparison (compiler_analysis.jpg) shows visibly smaller MSVC/gcc-trunk codegen for FastString versus std::string's allocation/SSO-branch logic for the same construct-and-return-length function.

**Use it when:**
- Short strings with a length bound known at compile time (order IDs, tickers, fixed-format codes) in latency-sensitive hot paths.
- Struct/message fields where predictable, allocation-free stack storage and fixed sizeof matter more than a general string API.
- Code that already consumes std::string_view and can call .str() to hand off for further processing.
- Compile-time (constexpr) string construction and simple manipulation.
- Workloads that can tolerate silent truncation of oversized input rather than needing growth or errors.

**Skip it when:**
- Any string whose length can exceed the chosen template capacity at runtime — it truncates silently instead of growing or signaling an error.
- Code expecting std::string's full interface (find, mutating substr, operator+, resize/reserve, stream extraction) — FastString's surface is much smaller.
- Append-heavy workloads on strings already inside SSO range: the project's own numbers show FastString roughly at parity (190ns vs 164ns) or slightly slower (50.0ns vs 61.5ns, i.e. ~0.8x) than std::string append in two of the four benchmarked scenarios.
- Toolchains without mature C++20 constexpr support — the repo's own open issue shows GCC 12.2.1 fails to compile the bundled example over a constexpr std::string_view::substr() error.
- Projects that need an actively maintained dependency: last commit 2024-03-31, 27 stars, and two pull requests (missing <cstdint> include, smaller size-type) sitting open and unmerged.

**Integration:** header-only · none for the library itself (single header uses only <string_view>, <algorithm>, <string>, <ostream>); benchmark/test targets pull Google Benchmark and Google Test via CMake FetchContent · C++20 (constexpr std::copy is required); README states MSVC 19.27.29111+ or x86-64 gcc-trunk; open issue #4 shows GCC 12.2.1 fails to compile the example over a constexpr std::string_view::substr() limitation · any (portable C++20, no architecture-specific intrinsics); the only published benchmark numbers are from MSVC on Windows, and a multi-platform CMake CI workflow exists but its results were not inspected

**Vs siblings:** Pick FastString when you specifically want stack-only, compile-time-sized strings with a minimal-dependency, genuinely constexpr-friendly header for constructing short strings in latency-critical code and can accept silent truncation. The other cataloged siblings solve different problems — to_static_string targets numeric-to-string conversion, buffet/fstring/Str/the Dicanio pool-allocator benchmark target more general-purpose (still growable or heap-backed) string replacements, zuu_string_view targets search over views, and jank's persistent_string is a language runtime's immutable string — none offer FastString's fixed-capacity, constexpr, stack-only design.

**Gotchas:**
- Construction/append/reset silently truncate any input longer than the compile-time capacity — no exception, no error flag, no way to detect truncation at the call site.
- remove_prefix/remove_suffix perform no bounds checking (string_view-style); an out-of-range length is undefined behavior.
- Length is stored as a full std::size_t per instance (8 bytes on 64-bit) even for tiny fixed strings; an open, unmerged PR (#5) proposes a smaller configurable size type to cut this overhead.
- GCC 12.2.1 fails to compile the bundled example (open issue #4, unresolved as of the last commit) due to a constexpr std::string_view::substr() error — check your exact GCC version before adopting.

**Status:** Stale (last commit 2024-03-31) with two open, unmerged pull requests and one unresolved GCC 12.2.1 compile-failure issue; MIT-licensed and small enough (~140-line single header) to vendor and patch yourself if you accept the maintenance risk.

[repo](https://github.com/m3janitha/FastString) · [benchmark](https://raw.githubusercontent.com/m3janitha/FastString/master/README.md)

##### Pool-allocator string (Dicanio STL/ATL/Pool string benchmark)  `C++`  `MIT`  `stale`  `Tier C`

Fixed-chunk pool allocator for bulk wide-char strings, beating ATL CStringW and std::wstring on creation.

**Beats:** std::string — On Windows 10 64-bit with VS2019 64-bit Release on an unspecified Intel i7, one sample run building a vector of ~3.2M shuffled std::wstring-length strings via push_back took 954ms for ATL CStringW, 866ms for MSVC STL std::wstring, and 506ms for the pool allocator (~1.7x vs std::wstring, ~1.9x vs ATL); the subsequent sort was a near-tie between STL and pool, and a separate SSO/tiny-string run reversed the result, with STL winning both phases.

**How:** Uses bump-pointer allocation within large chunks reserved via VirtualAlloc (default 512KB, rounded to system allocation granularity), so most string allocations are just a pointer increment instead of a heap call, and a new chunk is requested only when the current one fills up. This amortizes many small OS/heap allocations into a few large ones, based on the technique from the 'Old New Thing' blog post on dictionary-loading allocation patterns. It also sidesteps ATL CStringW's copy-on-write reference counting (_InterlockedIncrement/_InterlockedDecrement), which the author identifies as ATL's main slowdown.

**Use it when:**
- Bulk-building a read-only collection of many small-to-medium wide strings in one pass (e.g. load, sort, discard) where the whole set is freed together
- Windows/MSVC codebases already comfortable linking Win32 (VirtualAlloc) or ATL
- Strings long enough to defeat std::wstring's SSO, so real heap allocation cost is being paid per element
- One-shot latency-sensitive construction of a vector of strings, not incremental mutation or long-lived per-string ownership
- Prototyping/benchmarking the pooling technique itself rather than needing a finished library

**Skip it when:**
- Tiny strings that fit std::wstring's SSO buffer: the author's own TEST_TINY_STRINGS run shows plain STL wins creation and sorting by 'an important margin'
- Sort/comparison-heavy workloads: the benchmark shows STL and pool strings 'perform very similarly' once sorting starts
- Any case needing to free or reuse a single string's memory before the whole pool is destroyed
- Non-Windows or non-wide-char code: implementation is Win32 VirtualAlloc/WCHAR only, not templated for char or portable
- Production dependencies: this is a demo class in a one-off benchmark repo (1 star, no tests/CI), not a maintained, packaged library

**Integration:** source-drop · Windows.h (VirtualAlloc/VirtualFree), crtdbg.h (_ASSERTE); the benchmark harness additionally links ATL (atlstr.h) but CStringPoolAllocator itself needs only Windows.h · not documented precisely; built and measured with Visual Studio 2019, 64-bit Release (no explicit /std flag visible in the .vcxproj) · Windows x86/x64 only (VirtualAlloc-based), MSVC toolchain

**Vs siblings:** Only for the specific pattern of bulk-creating many medium/long, read-only wide strings that are discarded together on Windows/MSVC — none of the catalogued siblings (to_static_string, buffet, FastString, fstring, Str, zuu_string_view, jank persistent_string) target this pool-and-discard arena shape; all of them are more general-purpose, portable, and actually packaged/usable as libraries, so prefer them for anything beyond this narrow demo.

**Gotchas:**
- No per-string free: individual allocations live until the whole CStringPoolAllocator is destroyed and all its chunks VirtualFree'd at once
- AllocString throws std::bad_alloc if VirtualAlloc fails or if a string exceeds kchMaxCharAlloc (1,048,576 WCHARs, ~2MB)
- Default minimum chunk size is 512KB; many short-lived or small allocators will over-reserve memory relative to std::wstring's SSO
- The destructor's chunk-walking logic explicitly fixes a leak/wrong-size bug present in the original 'Old New Thing' blog code that this class is based on (documented in comments)

**Status:** Stale since December 2023 (1 star, no CI/tests, last commit 2023-12-01) but MIT-licensed and small enough (one header) to vendor as a reference implementation of the pooling technique rather than as a maintained library.

[repo](https://github.com/GiovanniDicanio/StringBenchmarkStlAtlPool) · [benchmark](https://giodicanio.com/2023/12/01/c-plus-plus-string-benchmark-stl-vs-atl-vs-custom-pool-allocator/)

##### Str (MengRao/str)  `C++`  `MIT`  `abandoned`  `Tier C`

Fixed-capacity char-array type with SIMD-accelerated equality, compare, and fixed-width integer/string conversion, beating std::string and stoi/to_string in author benchmarks.

**Beats:** std::string, std::to_string/stoi — Author's own bundled microbenchmarks (benchmark/benchcmp.cc for comparisons, benchmark/benchnum.cc for conversions; built with g++ -march=native -O3, no compiler version or hardware stated) report Str's operator==/compare running about 2x faster than strncmp/memcmp/std::string equivalents, and fromi/toi running about 10x faster than stoi/strtol/to_string/sprintf for fixed-width numeric conversions. The README gives only these round numbers, with no result tables.

**How:** operator==/compare fold the array into 8-byte word comparisons and use __builtin_ctzll to locate the first differing byte, avoiding a per-byte loop, and switch to AVX-512 (VL+BW) masked byte compares (_mm512/256/128_cmpneq_epu8_mask) when the target supports it. fromi/toi convert between fixed-width, zero-padded decimal digits and integers using a branchless SIMD digit-pair multiply-add trick (SSE4.1 pmaddubsw/pmaddwd chain, citing arXiv:1902.08318 Fig.7) for 8/16-digit chunks, plus a precomputed 2-character lookup table for the remaining/non-SIMD path, replacing libc's division-per-digit stoi/to_string loop.

**Use it when:**
- Fixed-width string fields known at compile time (exchange/ticker symbols, FIX/ITCH-style protocol codes, instrument IDs)
- Hot-path equality/ordering comparisons of short (up to tens of bytes), fixed-length keys, e.g. market-data order-book keys
- Fixed-width, zero-padded decimal integer<->string conversion where the exact digit width is known ahead of time (e.g. date/session codes)
- x86-64 targets that can build with -march=native or at least enable SSE4.1/AVX-512 to hit the accelerated code paths
- Low-latency code already avoiding heap allocation that wants a trivially-copyable POD string type usable as a map/hash key

**Skip it when:**
- Variable-length or arbitrary strings: Str has no resize/append/growth, its capacity is baked into the template parameter
- General integer parsing/formatting: fromi/toi require the number to fit exactly in SIZE zero-padded digits; no sign handling or variable width like stoi/to_string
- Non-x86 targets: Str.h includes <x86intrin.h> unconditionally, so it will not compile on ARM/aarch64
- Constructing Str from a C-string/buffer shorter than SIZE: the (const char*) constructor does a raw SIZE-byte struct copy and can read past the source buffer
- Projects wanting upstream support: last commit 2021-07-04, single maintainer, 127 stars, no CI beyond the bundled benchmarks

**Integration:** header-only · none (STL headers + x86 intrinsics only) · C++11 minimum; C++17 only needed for tosv() (std::string_view). Benchmarks build with g++ -march=native -O3 (benchfindstr/benchfindint additionally add -std=c++17); GCC version not stated. · x86-64 only (unconditionally includes <x86intrin.h>); AVX-512VL+AVX-512BW enable the SIMD compare path, SSE4.1 enables the SIMD toi/fromi path, otherwise a generic 8-byte-word fallback is used

**Vs siblings:** Pick Str over to_static_string/FastString/fstring/buffet when the field width is a known compile-time constant (fixed-width protocol/exchange codes) and you want the fastest possible equality/compare plus fixed-width numeric conversion via word-at-a-time/AVX-512 compare and SIMD digit conversion; for general resizable strings or variable-width number formatting, use one of those siblings instead.

**Gotchas:**
- Str(const char*) does a raw SIZE-byte struct copy (`*(const Str<SIZE>*)p`), which can read past the source buffer if it is shorter than SIZE — no null-termination or bounds checks
- fromi/toi require the value to fit exactly in SIZE zero-padded decimal digits (no sign, no variable width); correctness is only exercised via asserts in the author's own benchmark, not enforced by the header
- Which code path (and therefore the speedup) you get is decided at compile time by preprocessor macros (__AVX512VL__/__AVX512BW__/__SSE4_1__), so build flags like -march=native directly determine performance
- AlignSize is documented but not enforced: Str is not required to be aligned, but the README/header notes that aligning it speeds up comparisons

**Status:** Abandoned since 2021-07-04 (last commit), single maintainer, 127 stars, 2 open issues and no CI; MIT-licensed and small enough (single header) to vendor and freeze as-is.

[repo](https://github.com/MengRao/str) · [benchmark](https://github.com/MengRao/str)

#### smart-pointers-and-refcount

##### SmallFunction (LoopPerfect/smallfunction)  `C++`  `MIT`  `abandoned`  `Tier C`

Header-only, fixed-capacity alternative to std::function that placement-news the callable into an inline stack buffer instead of the heap.

**Beats:** std::function — First-party Google Benchmark (100 identical lambdas capturing int i and unsigned N, assigned into a vector and invoked via std::transform per iteration) on g++6 and clang++6/libc++, no CPU stated: std::function averaged 1141 ns (g++6) / 1511 ns (clang++6+libc++) versus SmallFun buffers from 312 ns (32-byte) up to 870 ns (2048-byte) on g++6 — about 3.0-3.7x faster at 32-256-byte buffers, narrowing to 1.3x at 2048 bytes (up to ~5.0x on clang at the smallest buffer).

**How:** Classic type erasure (SFConcept/SFModel, i.e. a hand-rolled PImpl) combined with small-buffer optimization: the Model is placement-new'd directly into a char[N] member on the stack, removing the heap allocation and one pointer indirection that std::function pays on every assignment. The repo's own Google Benchmark constructs and invokes 100 small lambdas per iteration; because the gain is almost entirely 'no malloc', it is largest for small buffers and shrinks as N grows and the inline copy itself gets more expensive to construct/copy.

**Use it when:**
- Hot loops that repeatedly construct/reassign many short-lived small-capture callables (the upstream benchmark: 100 lambdas capturing one int and one unsigned, assigned and invoked per iteration).
- Capture size is small and known ahead of time — the largest wins (3-5x) are at 32-256 byte buffers.
- A single call site can commit to one fixed buffer size and doesn't need to store arbitrarily-sized callables behind one type.
- You're willing to vendor a ~100-line single header (MIT) and patch it yourself rather than rely on upstream maintenance.
- Target has relaxed alignment handling for unaligned/misaligned loads (see gotchas) or you've verified/fixed the alignment issue yourself.

**Skip it when:**
- You need to store callables of unpredictable or varying size behind one type — oversized captures are a hard compile error here, not a transparent heap fallback like std::function.
- Captures include pointers or other over-aligned members on strict-alignment platforms (e.g. ARM) — issue #1 shows UBSan-confirmed misaligned member-access crashes because storage is a plain char[N] with no alignas.
- Code paths may call a default-constructed or moved-from SmallFun — invoking an empty one is undefined behavior; std::function would throw std::bad_function_call instead.
- You require move semantics for move-only state — SmallFun only defines copy construction/assignment.
- You need an actively maintained dependency — last commit 2018-01-04, the alignment bug is still open, and the only fix (PR #3, alignof(std::max_align_t)) was never merged.

**Integration:** header-only · none (only <type_traits>) · C++14 (uses std::enable_if_t); upstream benchmarked with g++6 and clang++6/libc++ · any standard C++ target in principle; not safe on strict-alignment platforms without patching the buffer's alignment (see gotchas)

**Vs siblings:** Pick SmallFun over woid, Delegate, or sy_callback.hpp when you want the smallest possible (~100-line) header-only SBO implementation to vendor and are willing to patch the known alignment bug yourself; stdext::inplace_function (WG21-SG14) implements the same idea with an actively-referenced SG14 design and no open alignment defect, and is the safer default when that matters more than minimalism.

**Gotchas:**
- Storage is a raw char[size] member with no alignas; open issue #1 documents a UBSan-caught case (pointer capture placed after a bool member) producing 'member call on misaligned address ... requires 8 byte alignment' crashes. An unmerged PR (#3) fixes this via alignof(std::max_align_t), but master still ships without it.
- operator() has no allocated-flag check, so calling a default-constructed or emptied SmallFun is undefined behavior rather than throwing.
- No move constructor or move-assignment operator is defined — only copy, which round-trips through the stored callable's own copy constructor.
- Exceeding the fixed buffer size for a given signature is a compile-time SFINAE failure, so bumping a lambda's capture set can break the build until you also raise the template's size parameter.

**Status:** Abandoned: no commits since 2018-01-04, the same day an alignment bug (issue #1) was reported and an unrelated operator= bug (issue #2) was fixed; MIT-licensed and small enough to vendor and patch, but the alignment issue is unresolved on master and its only proposed fix (PR #3) was never merged.

[repo](https://github.com/LoopPerfect/smallfunction) · [benchmark](https://github.com/LoopPerfect/smallfunction#benchmarks)

##### sy_callback.hpp  `C++`  `Apache-2.0`  `stale`  `Tier C`

Header-only type-erased callback wrapper beating std::function on construct/destroy, move, and assign; no SBO.

**Beats:** std::function — First-party README benchmarks (clang++ -O2, Apple M1 macOS, libc++) over 10M reps claim sy_callback beats std::function on init+destroy (~6x for non-capturing lambdas, ~15x for 1024-byte captures), move (~14x), assign (~7x), copy (~1.5x), and most call-time paths (~1.8x for non-capturing lambdas/global functions); std::function is ~5x faster specifically when the callback wraps a std::bind'd member function. Only the call-time numbers have a public harness (test.cpp); init/destroy, copy/move/assign, and compile-time tables are unverified first-party figures.

**How:** The object is 16 bytes: an object_ptr slot plus a thunk_fn that returns one of two static function pointers (invoke_fn, life_fn) rather than std::function's typical vtable/control-block scheme. Non-capturing lambdas and plain function pointers are stored directly in the pointer slot and invoked with no heap allocation, so construct/destroy/move for that common case is just pointer copies instead of allocator traffic. invoke_prediction<T>() lets a caller assert the concrete static type to skip the thunk indirection on the call, at a claimed ~10-20% gain per the README.

**Use it when:**
- Hot loops that construct, destroy, move, or assign large numbers of callbacks (per-frame game/embedded code) where std::function's allocation and vtable overhead dominates
- Callbacks are mostly non-capturing lambdas or plain function/static-member pointers, which avoid heap allocation entirely in this design
- Binary-size or compile-time sensitive code instantiating many distinct callback signatures (README's 1000-callback table shows much smaller generated code and faster compiles than std::function in most rows, though this table has no public benchmark source)
- Single-threaded callback ownership, or lifetime changes (move/assign/swap/reset) externally synchronized
- C++11-only toolchains/embedded targets where a minimal, dependency-free header is preferable to <functional>'s std::function

**Skip it when:**
- Callbacks built from std::bind-wrapped member functions: the README's own numbers show std::function ~5x faster than sy_callback there
- Multi-threaded code that moves, destroys, assigns, swaps, or resets a shared callback concurrently — only copy is documented thread-safe
- Expecting small-buffer optimization for small captures: there is none, so every capturing lambda or functor heap-allocates regardless of capture size
- Anything requiring production-grade maturity: single-contributor repo, 0 stars, no CI, no releases/tags, most benchmark tables (init/destroy, copy/move/assign, compile-time) have no published harness
- Code needing package-manager distribution or CMake config — it's a bare header plus a manual test.cpp, no build tooling included

**Integration:** header-only · none beyond the C++ standard library (<functional>, <type_traits>, <typeindex>) · C++11 minimum; compiles an additional noexcept-function-pointer code path under C++17 (__cplusplus >= 201703L) · not documented beyond the benchmark machine (Apple M1 macOS, clang++); no CI workflows in the repo and no explicit platform support statement

**Vs siblings:** Among the std::function-beating siblings (woid, Delegate, stdext::inplace_function, SmallFunction), pick sy_callback when you specifically want zero heap allocation for non-capturing lambdas/plain functions and a minimal 16-byte base object, and can tolerate heap allocation for every capturing case; pick inplace_function or SmallFunction instead when you need true SBO for small captures, since those have broader validation than this single-contributor, 0-star repo.

**Gotchas:**
- Calling an empty or moved-from callback throws std::bad_function_call() (reused from <functional>), not a library-specific exception type
- target<T>() relies on RTTI (typeid/std::type_index) internally
- invoke_prediction<T>() requires the caller to name the exact static type (or member-function pointer) to get the fast path; a wrong guess still works correctly but the speedup is only ~10-20% per the README, with some code-size increase
- No SBO: capturing lambdas and functors always heap-allocate, even for a single captured byte; only non-capturing lambdas and plain function pointers avoid the heap

**Status:** Stale: single-contributor repo created 2025-09-01, last pushed 2025-09-18, 0 stars, no releases/tags/CI; Apache-2.0 licensed and copyable as one header, so cheap to vendor and read despite the lack of outside validation.

[repo](https://github.com/ShigamiYune/sy_callback.hpp) · [benchmark](https://github.com/ShigamiYune/sy_callback.hpp/blob/main/README.ENG.md)

#### sorting

##### blitsort  `C`  `Unlicense`  `stale`  `Tier C`

In-place, stable, adaptive C sort beating std::stable_sort via rotations instead of an O(n) swap buffer.

**Beats:** std::stable_sort — On the author's wolfsort harness (g++ -O3 -w -fpermissive, WSL2 gcc 7.5.0, libstdc++'s std::stable_sort as baseline), blitsort sorted 100,000 random-order 64-bit ints in avg 0.002518s vs 0.006207s for std::stable_sort (~2.5x) and 32-bit ints in 0.002341s vs 0.006025s (~2.6x); gains are far larger on structured distributions (e.g. ~17x on descending order) but shrink to roughly parity on 128-bit long doubles. No CPU model was reported for the runs.

**How:** Two custom primitives do most of the work: a 'trinity rotation' (the author's own array-rotation algorithm, described as significantly faster than standard triple-reversal rotation) used to move partitions in place instead of copying to a swap buffer, and a 'monobound binary search' used to locate rotation points, claimed up to 2x faster than a typical binary search. An analyzer detects already-sorted, reverse-sorted, and mostly-sorted runs up front and routes them to rotate quadsort/fluxsort fast paths. On primitive types, uncommenting the `cmp` macro (or defining it before include) switches to branchless comparisons, which the README says roughly doubles throughput.

**Use it when:**
- Need a stable sort in C with a small, bounded auxiliary-memory footprint (no O(n) swap buffer) rather than std::stable_sort's allocation.
- Input has structure (ascending/descending runs, sawtooth, pipe-organ, partially sorted tails) — the adaptive analyzer gives the largest wins here (README table: ~17x on 100K descending 32-bit ints vs std::stable_sort).
- Sorting primitive 32/64-bit integers, doubles, or long doubles, or larger records via pointer indirection (e.g. strings) under a qsort-compatible call site.
- Codebase can vendor a small C source drop (blitsort.h/.c + bundled quadsort.h/.c) rather than link a library, and wants roughly 2.5x throughput over libstdc++ std::stable_sort on random 64-bit data.
- Migrating qsort() call sites incrementally without adopting a templated/iterator C++ API.

**Skip it when:**
- 128-bit / long double keys: the README's own table shows blitsort roughly at parity with std::stable_sort on random order (0.011423s vs 0.011047s avg) and clearly behind pdqsort/crumsort there.
- 'Ascending tiles' and 'bit reversal' distributions: blitsort is measurably slower than std::stable_sort in the README's own data (0.001397s vs 0.000948s; 0.002160s vs 0.001355s), so gains aren't universal.
- Stability isn't required and raw speed on plain random order is the goal: the README's own benchmark shows pdqsort and crumsort both beating blitsort on random-order 32/64-bit ints.
- Need a modern templated/iterator C++ API, exceptions, or custom allocator support: blitsort is a C, qsort()-signature function, not a std::sort drop-in.
- Want active upstream maintenance or CI/test coverage signals: last commit 2024-07-27, no CI config visible in the tree, and the published benchmarks run on gcc 7.5.0 inside WSL2 with no bare-metal CPU model given.

**Integration:** source-drop · quadsort.c/quadsort.h (bundled in src/, required include); otherwise only the C standard library · not documented precisely; header uses <stdalign.h> (C11) and assert/errno/string/stdio/float.h; README benchmarks built with gcc 7.5.0 / g++ -O3 -w -fpermissive · any (portable C, no intrinsics in the public API); all published benchmarks are x86-64 under WSL2, no other platform data given

**Vs siblings:** Pick blitsort over its own siblings quadsort/fluxsort when you need stability but can't spare their O(n) auxiliary buffer, and over crumsort/pdqsort when stability is required (both are unstable, and crumsort is faster than blitsort on plain random-order data per the README's own pdqsort/crumsort table). Pick fluxsort or quadsort instead when O(n) scratch memory is available and stability plus a bit more raw speed matters more than memory footprint.

**Gotchas:**
- Full branchless speedup requires manually defining the `cmp` macro before including blitsort.h (or editing bench.c); without it, primitive comparisons go through a function pointer and the README says throughput roughly halves.
- blitsort_prim() only supports 32/64-bit signed/unsigned integers (size codes 4/5/8/9); other sizes hit an assert.
- blitsort() itself only dispatches sizes matching char/short/int/long long/long double; any other element size falls through to an assert rather than a qsort() fallback (that fallback line is commented out in blitsort.h).
- 'In-place' is the loose community definition: it still uses up to 512 elements of swap memory by default (configurable down to 32 or sqrt(n)) plus O(log n) recursion stack, not strict O(1).

**Status:** Stale since the last commit on 2024-07-27 (0 open issues, all 5 historical issues closed with no unresolved bugs), but Unlicense (public domain, no patent grant) and a small qsort-compatible C source make it cheap to vendor and freeze at a known-good commit.

[repo](https://github.com/scandum/blitsort) · [benchmark](https://github.com/scandum/blitsort/blob/main/README.md)

##### crumsort  `C`  `Unlicense`  `stale`  `Tier C`

Branchless in-place unstable C quicksort/quadsort hybrid, ~1.4-1.5x faster than pdqsort on random 32/64-bit ints.

**Beats:** pdqsort — Author's own wolfsort/bench.c harness (g++ -O3 -w -fpermissive, WSL gcc 7.5.0 on Ubuntu 18.04, no CPU model given) shows crumsort averaging 0.001927s vs pdqsort's 0.002668s on 100,000 random 64-bit ints (~1.4x) and 0.001812s vs 0.002705s on 32-bit ints (~1.5x), each best-of/avg-of 100 runs; on 128-bit long doubles pdqsort is faster (0.005975s vs crumsort's 0.008316s). No comparison against std::sort or std::stable_sort appears on the page.

**How:** Its 'fulcrum' partitioning scheme (a BlockQuicksort-style branchless variant of Hoare partitioning) holds the pivot in a swap slot so each element move takes 2 assignments instead of 3, and widens the swap buffer to batch 16 boundless comparisons branchlessly. Pivot selection scales pseudomedian-of-9/median-of-16 for small partitions up to median-of-128/256/512 for large ones. An analyzer pre-scans for sortedness and reverts to quadsort per segment, and quadsort (not insertion sort) handles partitions under 24 elements. Pivot retention (borrowed from pdqsort) triggers a reverse partition on runs of duplicate pivots for generic/low-cardinality data.

**Use it when:**
- Sorting large arrays (README cites >1,000,000 elements) of random-order 32/64-bit integers or pointer-sized keys where stability is not required
- Sorting 'tables' (structs/rows) by a 64-bit key or pointer, including tables that embed long doubles, since crumsort only moves the pointer, not the 128-bit payload
- Data with many duplicate/low-cardinality values (e.g. gender, age columns) thanks to the dual-pivot-style reverse partition on repeated pivots
- Environments where you can vendor plain C source (no package manager) and want a qsort drop-in with better throughput on primitives
- Throughput-oriented batch sorts rather than latency-sensitive incremental/partial sorts

**Skip it when:**
- Sorting arrays of long double (128-bit) directly as the array element type — README and this session's benchmark both show pdqsort winning there (0.005975s vs 0.008316s avg, 100K elements)
- Any workload requiring stability (equal keys must keep relative order) — crumsort is explicitly unstable; use fluxsort or quadsort instead
- Large nearly-sorted arrays where fluxsort will outperform it — crumsort runs on only 512 elements of auxiliary stack memory and, being unstable, scrambles pre-existing order more than fluxsort's mid-partition ordered-run detection
- Projects wanting an actively maintained dependency — last commit 2024-07-27, tagged stale, and the author's own TODO admits the long-double slowdown is unfixed
- Codebases wanting a single, normally-linked translation unit — crumsort.h uses macro-based generic instantiation that re-#includes crumsort.c per type, which is source-drop only, not a conventional compiled library

**Integration:** source-drop · none (crumsort.h pulls in quadsort.h/quadsort.c from the same repo; both are vendored together) · C11 (crumsort.h includes stdalign.h); README's own benchmark compiles it with g++ -O3 -w -fpermissive, so it also compiles as permissive C++ · not restricted to any ISA in source — plain portable C with no explicit SIMD intrinsics (branchlessness relies on compiler codegen, not intrinsics); README benchmark run was WSL/x86-64 only, no other platform is documented

**Vs siblings:** Over fluxsort (same author, catalogued sibling): pick crumsort when you don't need stability and want the extra throughput crumsort gets from being truly in-place, especially sorting large random-order integer/pointer arrays or tables with long-double payloads — fluxsort remains the better choice for large near-sorted data or when stability matters. crumsort is not shown against BlockQuicksort, Boost.Sort spreadsort, or IPS⁴o in this repo, so no direct comparison to those siblings is documented.

**Gotchas:**
- Header/source layering is macro-driven: crumsort.h does #define VAR/FUNC then #include "crumsort.c" repeatedly to generate typed variants — you vendor and #include the .c files, you don't link a normal compiled object
- crumsort_prim() only covers 32/64-bit signed/unsigned integers (size must be sizeof(int)/sizeof(long long), +1 for unsigned per an internal assert); other primitive/custom types require editing crumsort.h/quadsort.h yourself
- Uses 512 elements of stack swap memory shared with quadsort, plus O(log n) recursion stack — not a strictly O(1)-memory sort despite being 'in-place' in the informal sense
- The `cmp` macro must be defined (uncommented, per README) to get the fully branchless comparison path; without it you fall back to a normal function-pointer comparator with lower throughput

**Status:** Maintenance is stale (last commit 2024-07-27) but the Unlicense public-domain dedication and small source-drop footprint (two headers, two .c files) make it cheap to vendor and freeze at a known-good revision regardless.

[repo](https://github.com/scandum/crumsort) · [benchmark](https://github.com/scandum/crumsort/blob/main/README.md)

##### fluxsort  `C`  `Unlicense`  `stale`  `Tier C`

Stable branchless quicksort/mergesort hybrid with a qsort-style C interface, claimed ~3x faster than std::stable_sort on random ints.

**Beats:** std::stable_sort — Author's own bench.c (wolfsort benchmark suite), compiled with g++ -O3 -w -fpermissive on GCC 7.5.0/Ubuntu 18.04 under WSL, hardware unstated: best-of-100 sorting 100,000 random 32-bit ints took 0.001906s for fluxsort vs 0.006113s for std::stable_sort (~3.2x); on ascending-order input, 0.000044s vs 0.000804s (~18x); 64-bit random ints were 0.002032s vs 0.006008s (~3.0x).

**How:** A top-down analyzer first checks for fully ordered/reversed runs and per-quarter presortedness, falling back to its sibling quadsort when a segment is mostly ordered. Partitioning is quicksort-style but partially in-place: elements <=pivot are written back in place and elements >pivot go to an auxiliary swap buffer, which cuts the branch-misprediction cost that plagues classic quicksort and gives memory-level parallelism on the writes. Pivots are chosen via a branchless quasimedian-of-9 (up to a median of 1024 for large partitions, an approximation of cbrt(n)), and partitions under 96 elements are sorted with quadsort's branchless small-array routine; a 1/16 partition-imbalance guard bounds the worst case to n log n.

**Use it when:**
- Stable sorting of primitive fixed-width integers, longs, or doubles (8/16/32/64-bit, long double) where you would otherwise use std::stable_sort
- Arrays from ~10K to 10M elements of random or partially-ordered data on x86-64/GCC, where extra O(n) scratch memory is affordable
- Data with exploitable structure - ascending/descending runs, sawtooth, pipe-organ patterns - where the analyzer gives the largest (10-18x) gains
- C/C++ code that can vendor a small C source drop and compile it with GCC -O3 (the author's tuned toolchain)
- Offline/batch sorting where a first-party-benchmarked throughput gain is sufficient evidence, not latency-critical or safety-certified code

**Skip it when:**
- You need the actual std::stable_sort C++ template API (iterators, allocators, arbitrary value types by move) - fluxsort is a C function with the qsort comparator contract, a code change, not a header swap
- Memory is constrained: fluxsort allocates n elements of swap memory (shared with quadsort); if allocation fails it silently falls back to quadsort's slower in-place rotations. Use blitsort (same author) for a true in-place stable sort
- Your comparator is subtraction-based (`a - b`) or otherwise not a strict, overflow-safe ordering - reported "bugs" (issue #10 buffer overflow, issue #4 stability failure) both turned out to be caller comparator mistakes, but they show how easy this footgun is to hit
- You need current, independently verified performance evidence: the project is stale (last commit 2024-07-27) and every published benchmark is first-party (author's own bench.c/wolfsort suite) on an old GCC 7.5.0/WSL toolchain with hardware unstated
- You're sorting only unsigned 32-bit ints at very large scale and can use radix sorting instead - the README itself says wolfsort (adaptive radix, same author) beats fluxsort on 8/16/32-bit types, and crumsort beats it if stability isn't required

**Integration:** header-only · none (fluxsort.h textually includes fluxsort.c and bundles quadsort.h/quadsort.c for the small-array/run fallback; all four files must sit in the same directory) · Plain C (no version stated beyond needing stdlib.h/string.h/assert.h); author recommends compiling with gcc -O3 for the numbers claimed - the README's own clang-10 benchmark shows some fluxsort/quadsort routines 2-3x slower under clang · any (portable C, no SIMD/intrinsics in the header); all published benchmarks are x86-64 (WSL/Ubuntu)

**Vs siblings:** Pick fluxsort over the unstable/radix/SIMD siblings (BlockQuicksort, IPS4o, x86-simd-sort, LearnedSort, poor-circle/radix_sort) when you need a stable, portable scalar C sort rather than raw unsigned-int throughput. Prefer quadsort itself, its stablemate, when the data has long ordered runs or is strings/objects (README: quadsort's branchless merge beats fluxsort there); fluxsort's edge is random or low-cardinality data plus the same qsort-style interface.

**Gotchas:**
- Comparator must be a real strict ordering that returns a consistent sign for all inputs; `a - b`-style comparators on 64-bit values silently truncate/overflow to int and cause out-of-bounds writes or unstable results (reported as a fluxsort bug in issue #10, root-caused to the caller's comparator)
- fluxsort_prim only covers 32/64-bit signed/unsigned integers (size = sizeof(int) or sizeof(long long), +1 to select unsigned); anything else needs fluxsort_size with a by-reference comparator, same as sorting an array of pointers
- Falls back silently to quadsort (still stable, but in-place via rotations) if the swap-memory malloc fails - a correctness safety net that is also a silent performance cliff
- A closed 2024 issue shows a Rust-glue port mismapped its comparator into fluxsort's internal contract and produced an apparent stability failure; the C library itself is not the source of that bug, but it illustrates how fragile porting the comparator convention is

**Status:** Stale (last commit 2024-07-27) but Unlicense (public-domain) makes it safe to freeze and vendor; the only known-good configuration is the author's GCC 7.5.0 -O3 toolchain, and no independent benchmark against std::stable_sort was found.

[repo](https://github.com/scandum/fluxsort) · [benchmark](https://github.com/scandum/fluxsort#benchmarks)

##### gridsort  `C`  `Unlicense`  `stale`  `Tier C`

Stable C sort using a cache-friendly bucketed grid; qsort-compatible interface; 1.4x-2.6x faster than std::stable_sort on 1M-int arrays.

**Beats:** std::stable_sort — Against libstdc++ std::stable_sort (g++ -O3 -w -fpermissive, WSL gcc 7.5.0/Ubuntu 18.04, comparisons inlined, no CPU model stated), sorting 1,000,000 random-order 32-bit ints, 10-sample average: gridsort 0.051147s vs std::stable_sort 0.073191s (~1.4x); on 'generic order' 1M 32-bit, 0.016224s vs 0.041741s (~2.6x). A separate, older benchmark (gcc -O3, WSL gcc 7.4.0, comparisons not inlined) shows gridsort ~1.6x faster than glibc's qsort() (a mergesort variant, not std::sort) on 100,000 random-order 128-bit elements (0.012730s vs 0.019996s).

**How:** Speed comes from three layered techniques: a boundless binary search (README claims up to 2x faster than a bounds-checked binary search) to pin down the right bucket, a self-balancing grid ('binary cube') sized so buckets stay cache-resident, and quadsort's branchless merge (8-element memcpy blocks with head/tail branchless merges) used both to sort overflowing buckets and to do the final merge. It also switches to an adaptive binary search once it detects already-sorted runs, which is consistent with its larger lead over std::stable_sort on 'generic order' and ascending/descending inputs than on pure random data.

**Use it when:**
- C codebases already calling qsort() that want a stable, drop-in-signature replacement and can tolerate O(n) extra memory
- 1M-element-scale arrays of 8/16/32/64-bit ints or long doubles with partial existing order (ascending/descending runs, sawtooth, 'generic order') -- this is where gridsort showed its largest measured edge (~2.6x vs std::stable_sort)
- Sorting arrays of pointers or handles (size_t/void*-sized elements) to indirectly sort structs, since the sort itself only accepts elements of size 1/2/4/8/sizeof(long double)
- Projects wanting a small, dependency-free, public-domain (Unlicense) C source drop rather than a C++ template library

**Skip it when:**
- Elements whose size isn't exactly 1, 2, 4, 8, or sizeof(long double) bytes -- gridsort asserts on other sizes, and that assert compiles out under NDEBUG, silently skipping the sort
- Multi-threaded callers: gridsort.c/gridsort.h declare a single global size_t BSC_Z reused by every type specialization and recomputed at the start of each grid build -- observed directly in source, not documented, and not safe for concurrent gridsort() calls
- Memory-constrained environments: needs O(n) auxiliary allocation (2*sqrt(n) blocks of sqrt(n) elements per the README) versus in-place alternatives
- C++ code wanting a literal std::stable_sort drop-in -- the interface is qsort-style (void*, size_t, size_t, CMPFUNC*), not iterators/functors, so it needs a wrapper and is only exercised on POD-like data in the benchmarks
- Chasing the best possible raw random-data throughput or an actively maintained option -- the README's own 'Porting' notes point to the author's newer fluxsort/quadsort as faster/simpler alternatives, and the repo has had no commits since 2024-07-27

**Integration:** source-drop · none beyond the C standard library (stdlib.h, stdio.h, assert.h, errno.h; quadsort.h adds float.h, string.h); bundles its own copy of quadsort.h/quadsort.c in the same src/ directory · not documented; bench.c's header comment lists gcc -O3, clang -O3, or g++ -O3 as working compile lines; plain C with no version-specific features observed · any (portable C, no SIMD intrinsics or threading in gridsort.c/quadsort.c); note sizeof(long double) is platform/ABI-dependent, which affects the 128-bit type-size dispatch case

**Vs siblings:** Among the sibling stable sorts from the same author/repo family (quadsort, fluxsort, blitsort), pick gridsort specifically for its bucket/binary-cube behavior on partially-ordered or structurally patterned data ('generic order', ascending/descending runs), where its README-measured lead over std::stable_sort was largest (~2.6x vs ~1.4x on pure random order); for best raw random-data throughput or lower memory overhead, the README's own porting notes point to the newer fluxsort/quadsort instead.

**Gotchas:**
- Only element sizes matching sizeof(char/short/int/long long/long double) are supported; other sizes hit an assert() that is a no-op under NDEBUG, so release builds can silently fail to sort
- Falls back to plain quadsort() for nmemb < BSC_X*BSC_X (1024 elements), so small arrays never exercise the grid/bucket logic
- Global BSC_Z is shared mutable state across all five type specializations (8/16/32/64/128-bit) -- not safe to call from multiple threads concurrently
- The 'long double' case is used as the stand-in for 128-bit elements; its actual byte width varies by platform/ABI, so the size dispatch is not portable as-is

**Status:** Stale: last commit 2024-07-27 (over two years old as of this writing) with zero open issues and no CPU model given for either benchmark; still Unlicense (public-domain, no patent grant) and small enough (two header + two source files, no dependencies) to vendor as-is.

[repo](https://github.com/scandum/gridsort) · [benchmark](https://github.com/scandum/gridsort/blob/main/README.md)

##### quadsort  `C`  `Unlicense`  `stale`  `Tier C`

Stable branchless bottom-up adaptive merge sort in C, beating std::stable_sort on random and partially ordered arrays.

**Beats:** std::stable_sort — On WSL2/Ubuntu 18.04 with g++ 7.5.0 (-O3 -w -fpermissive), the author's own wolfsort bench.c measured quadsort at 0.005664s vs std::stable_sort's 0.013871s (best-of-50) sorting weighted random arrays of 513-1024 32-bit ints, about 2.4x, with roughly 2.0-4.9x across the full 1-4096 item weighted sweep; no CPU model is stated. The README's larger 100,000-element, 11-distribution table (~4-16x claims) is mislabeled 'fluxsort' in its row data despite a 'quadsort' bar-graph caption, so those bigger numbers cannot be confidently attributed to quadsort itself.

**How:** An 8-element analyzer detects ascending or descending runs using a 4-comparison bitmask trick, cutting branch mispredictions to about 0.2 per 8 elements versus ~3.2 for naive comparisons, and exits with pre-sorted 8-element blocks. Small blocks are combined with branchless swap and 'parity merge' macros, then merged bottom-up with a single reusable O(n) swap buffer (like std::stable_sort's own auxiliary buffer) instead of per-level allocation. The branchless macros are written as GCC-style conditional stores on gcc and as ternary expressions on clang, so codegen and speed differ by compiler.

**Use it when:**
- Large arrays (100K+) of primitives on gcc/x86 where std::stable_sort's overhead is measured to be a bottleneck
- Partially ordered input (ascending/descending runs, sawtooth, pipe-organ patterns) where the run-detecting analyzer pays off most
- C codebases already built around qsort-style comparators, or C++ call sites that can pass contiguous arrays of PODs
- Fixed-width 32/64-bit integer arrays, via quadsort_prim, to skip comparator call overhead entirely
- Projects fine vendoring a small, unlicensed (public-domain) header/source pair instead of linking a library

**Skip it when:**
- Call sites that need std::stable_sort's actual iterator/comparator signature over arbitrary containers, not just contiguous arrays
- Bit-reversal-ordered input: the vendor's own benchmark table shows quadsort slower than std::stable_sort there
- Building with clang instead of gcc: author states the branchless merge/small-sort routines run 2-3x slower under clang
- Need current, independently reproduced numbers: last commit 2024-07-27 ('stale'), sole benchmark is first-party with no CPU stated, and the README's big 100,000-element per-distribution table is mislabeled 'fluxsort' even though its graph is captioned 'quadsort'
- Memory-constrained sorts expecting an in-place win: quadsort still needs an O(n) auxiliary swap buffer, same as std::stable_sort

**Integration:** header-only (quadsort.h #includes quadsort.c internally; single #include "quadsort.h" is enough) · none (stdlib.h, stdio.h, assert.h, errno.h, float.h, string.h only) · plain C (no C99/C11-specific features observed); README benchmarks used GCC 7.5.0 and clang 10 with -O3; the C++ bench harness needed -fpermissive to compile the C header as C++ · any target with a C compiler; portable C with no SIMD intrinsics, but branchless codegen and measured speed are tuned for gcc/x86 (2-3x slower merge/small-sort routines under clang per the author)

**Vs siblings:** Pick quadsort over the same author's fluxsort when you specifically want the mergesort half without fluxsort's quicksort partitioning (fluxsort itself is the faster average-case hybrid per the vendor's own comparisons); pick quadsort over BlockQuicksort, Boost.Sort/spreadsort, IPS4o, LearnedSort, or x86-simd-sort specifically when stability is required, since those all target unstable std::sort rather than std::stable_sort.

**Gotchas:**
- QUAD_CACHE (default 262144) gates performance for pointer/struct sorts via quadsort_size; the header comments say it needs tuning for large arrays and L3 cache size
- Branchless macros branch on the __clang__ define, so gcc and clang run genuinely different code paths for the same source, not just different optimizer output
- quadsort and quadsort_size malloc their own O(n) swap buffer internally with no custom-allocator hook, and assert() on malloc failure rather than returning an error code
- A user-filed correctness question about cross_merge's tail pointer possibly running past the block's tail (issue #20) is closed but its resolution isn't confirmed in the visible thread

**Status:** Maintenance is stale (last commit 2024-07-27, no recent activity) but the code is Unlicense (public domain) and a small, single header/source pair, cheap to vendor and freeze indefinitely.

[repo](https://github.com/scandum/quadsort) · [benchmark](https://github.com/scandum/quadsort#benchmark-quadsort-vs-stdstable_sort-vs-timsort)

##### ska_sort  `C++`  `BSL-1.0`  `abandoned`  `Tier C`

Header-only radix/American-flag sort beating std::sort by ~2x on ints, floats, structs and strings via key extraction.

**Beats:** std::sort — The only benchmark is the author's 2016 blog post (Google Benchmark, ns/item charts) reporting ska_sort about 2x faster than std::sort on uniform-distribution integers and 'many times faster' on skewed (std::geometric_distribution(0.001)) integers, with similar or better results for (bool,float) pairs, 128-1024 byte structs, and short strings; no compiler, flags, or CPU model are stated, and the post itself notes performance degrades toward std::sort's O(n log n) on long strings with shared prefixes.

**How:** Recursively partitions elements byte-by-byte into 256 buckets (LSD-style radix sort) instead of comparing elements, giving roughly O(n*b) behavior for b key bytes versus std::sort's O(n log n). For partitions under the American-flag-sort threshold (1024 elements) it uses an in-place American flag sort whose inner loop ('ska byte sort') processes swaps for many not-yet-placed elements at once rather than completing one swap chain at a time, improving instruction-level parallelism. Partitions under 128 elements, or string keys whose recursion exceeds 16 levels (pathological shared prefixes), fall back to std::sort.

**Use it when:**
- Large arrays (roughly >128 elements) of integers, IEEE-754 floats, bools, or other types with a cheap ExtractKey returning a radix-sortable value
- Structs/tuples sorted by a fixed-width key (128-1024 byte records in the author's benchmarks), via an ExtractKey with operator[]
- Skewed/low-entropy integer distributions, where the author reports the largest wins ('many times faster' on std::geometric_distribution(0.001))
- Throughput-focused batch sorts where instability and an optional O(n) auxiliary buffer (ska_sort_copy) are acceptable
- Header-only C++ codebases that want to vendor one file rather than add a build dependency

**Skip it when:**
- You need a stable sort — ska_sort is not stable
- Keys aren't radix-extractable, or the container isn't random-access — this fails to compile rather than silently falling back to std::sort
- Very large collections: one blog-comment reader reports ska_sort slower than std::sort on 1.2 billion uint64_t (unverified, possibly paging-related)
- Long, variable-length strings with many shared prefixes — the author says it degrades toward O(n log n) behavior there
- Strict C++20 builds: the header uses std::result_of (deprecated C++17, removed C++20), and the repo has been unmaintained since 2017 so this is unlikely to be patched upstream

**Integration:** header-only · none for ska_sort.hpp (STL only: <cstdint>, <algorithm>, <type_traits>, <tuple>, <utility>); the bundled ska_sort_tests_and_benchmarks.cpp additionally needs GTest and Google Benchmark to build, but that file is not required to use the sort · C++14 (generic lambdas); std::result_of usage makes strict C++20 mode risky without patching · any (plain C++, no SIMD/intrinsics); float/double keys assume IEEE-754 representation

**Vs siblings:** Pick ska_sort over pdqsort/vergesort when your keys are natively radix-extractable (fixed-width ints/floats, short strings, small structs) and you want a small single-header drop-in with no build dependency; pdqsort and vergesort are comparison sorts with broader type support and adaptivity to existing order, and Highway's vqsort needs AVX-512/SIMD hardware plus a real build dependency, both heavier asks than ska_sort's plain C++14 header.

**Gotchas:**
- ska_sort_copy's bool return says whether the sorted output landed in buffer_begin (true) or the original range (false); using the wrong one silently gives unsorted/stale data
- Float/double keys are reinterpreted as unsigned integers through a union, which is undefined behavior in standard C++, with no compile-time IEEE-754 (is_iec559) guard — flagged in open issue #2, never fixed
- Types without a usable ExtractKey/subscript operator fail to compile rather than falling back to std::sort
- Open issue #3 (2017) reports MSVC/VS2015 'class template has already been defined' compile errors for some custom key types; the repo's last two commits addressed similar SFINAE issues but the issue was never closed

**Status:** Abandoned since the last commit on 2017-05-15 (5 open issues, no README, no LICENSE file though BSL-1.0 is stated in the file headers); it is a single copy-pasteable header, so age is low-risk to vendor, but expect to patch std::result_of yourself for a C++20 toolchain.

[repo](https://github.com/skarupke/ska_sort) · [benchmark](https://probablydance.com/2016/12/27/i-wrote-a-faster-sorting-algorithm/)

##### vergesort  `C++`  `MIT`  `active`  `Tier C`

Presortedness-detecting merge layer over pdqsort; beats std::sort/std::stable_sort when input has long sorted runs.

**Beats:** std::sort, std::stable_sort — Chart-derived cycles-per-element numbers (std::vector<int>, 10^6 elements, MinGW g++ 6.1.0 -std=c++1z -O2 -march=native, libstdc++, no CPU model stated) show vergesort's pdqsort-backed random-access version beating libstdc++ std::sort on every distribution charted (e.g. shuffled ~365 vs ~713, pipe organ ~22 vs ~885, push front ~15 vs ~858) and beating std::stable_sort on most patterns, but losing to std::stable_sort on the 'Alternating' pattern (~307 vs ~185).

**How:** The random-access overload jumps n/log n elements at a time instead of scanning one by one, so it can decide a run is not 'big enough' after O(log n) comparisons and bail out to pdqsort almost immediately on random data. When a big-enough run is found it records its bounds (reversing descending runs) instead of sorting it, and once the whole range is scanned it k-way-merges the collected runs with std::inplace_merge. The bidirectional overload lacks the jump-scan (it must walk linearly) and falls back to plain median-of-9 quicksort instead of pdqsort, which is why the README documents it as slower and O(n^2) worst case.

**Use it when:**
- Large std::vector-like collections of comparison-sortable types that frequently contain long sorted or reverse-sorted runs (>= n/log n), e.g. pipe-organ, push-front/push-middle, or nearly-sorted-log patterns
- You already use (or would use) pdqsort/std::sort and want a near-zero-cost presortedness check layered on top, since the fallback triggers in O(log n) comparisons on random data
- std::list or other bidirectional-only sequences where std::list::sort could benefit from run detection, if you can accept the bidirectional overload's O(n^2) worst case
- Header-only, dependency-free, C++03-compatible environments where vendoring one file is preferable to adding a library
- One-shot throughput sorts of 10^6+ elements where instability is acceptable

**Skip it when:**
- You need a stable sort: vergesort reverses descending runs in place, which makes it unstable even though its fallback (pdqsort) is also unstable
- Data is uniformly random/shuffled with no long runs: the win over calling pdqsort directly is essentially just avoiding vergesort's own scan overhead, not a speedup over pdqsort
- Bidirectional-iterator use (e.g. std::list) where adversarial input could hit the documented O(n^2) worst case from the median-of-9 quicksort fallback
- Workloads resembling the README's 'Alternating' pattern, where the shown benchmark has vergesort slower than std::stable_sort (~307 vs ~185 cycles/element)
- Serious/production integer-sorting workloads chasing maximum speed: the repo's own maintainer calls this standalone header 'more of a demonstrator' and points to the same author's cpp-sort library (cppsort::verge_sort) as the tuned, faster version

**Integration:** header-only · none — bundles its own pdqsort, insertion sort, iter_sort3, log2 and quicksort helper headers; standard library only · C++03 for the standalone header (README: 'Everything should work with even C++03'); benchmarks were built with MinGW g++ 6.1.0 -std=c++1z -O2 -march=native · any (portable C++, no platform-specific intrinsics in the header); benchmark hardware itself is undocumented

**Vs siblings:** Pick vergesort over pdqsort when your data regularly contains long sorted/reverse-sorted runs (pipe-organ, push-front/middle, nearly-sorted-log shapes) and unstable output is acceptable — pdqsort alone is the safer default for uniformly random data since vergesort only adds a fast-fail scan there. Prefer ska_sort or Highway's vqsort instead when the win you need comes from key-type specialization (integer radix) or SIMD partitioning rather than run detection, since vergesort's fallbacks.md shows it still beats raw ska_sort on presorted patterns but the 'vergesort killer' pattern narrows that gap (139 vs 127 cycles/element).

**Gotchas:**
- Unstable by design: it uses std::reverse on descending runs before merging, which discards relative order of equal elements even when the fallback sorter is stable
- A real 2020 bug (issue #13) had the standalone header's random-access overload silently misnamed/uncalled, so it fell through to the much slower bidirectional path — fixed after report, but shows the single-header demo has drifted out of sync with cpp-sort's verge_sort before
- The 'big enough' run threshold is a fixed n/log n heuristic with no tuning parameter; the author notes it is sometimes suboptimal versus always falling back
- The bidirectional-iterator variant cannot use the jump-scan optimization and falls back to a plain median-of-9 quicksort, giving it O(n^2) worst case (vs O(n log n) worst case for the random-access version)

**Status:** Actively maintained (pushed 2025-11-07) and MIT-licensed, but the author has stated on the issue tracker that this standalone single-header version is 'more of a demonstrator' favoring small code size and C++03 backward compatibility over raw speed — the actively tuned, faster implementation is cppsort::verge_sort in the same author's cpp-sort project.

[repo](https://github.com/morwenn/vergesort) · [benchmark](https://github.com/morwenn/vergesort)

##### voracious_radix_sort  `Rust`  `MIT`  `active`  `Tier C`

Rust MSD/LSD radix-sort crate for primitive types and custom structs, several times faster than Rust's own sort on large arrays.

**Beats:** std::sort — A first-party benchmark checked into results/benchmark_1_2_0/ on an AMD Ryzen 3950x compares Voracious's trait sort against Rust's own sort_unstable (pdqsort-era) and stable sort on i64 arrays, not C++ std::sort. At 1,000,000 elements Voracious took 9.31ms vs sort_unstable's 37.9ms (~4.1x) and stable sort's 66.8ms (~7.2x); at 10,000,000 elements the gap was ~4.6x and ~6.4x respectively. At 1,000 elements Voracious is roughly tied with sort_unstable because it has already fallen back to pdqsort at that size. Compiler flags for the specific run are not stated.

**How:** Uses most-significant-digit (MSD) radix partitioning derived from Ska sort, with a Verge-sort pre-processing heuristic to detect near-sorted runs and switch strategy; depending on type and size it may instead use DLSD (a diverting LSD radix sort) or 'Rollercoaster' (MSD then LSD hybrid, the author's own contribution). The multithreaded Peeka sort is an in-place parallel MSD radix sort based on MIT's Regions-sort. Per-type/size constants (radix width, diversion thresholds, thread chunk sizes) are hand-'profiled' ahead of time rather than computed at runtime, cutting overhead once arrays are large enough to amortize the histogram passes.

**Use it when:**
- Large in-memory arrays (roughly 1M+ elements) of primitive integer, float, bool or char types where extra memory for an out-of-place sort is acceptable
- Types already covered in PROFILING.md's tuned table (bool, char, f32/f64, u8/u32/u64, i32/i64, usize/isize 8/32/64) on x86-64 hardware similar to a Ryzen 3950x
- Throughput-bound batch sorting where you can re-run the benchmarks and re-tune constants on your own CPU before committing
- Multithreaded sorts of very large arrays (RELEASES.md 1.2.0 fixed Peeka sort scaling past 1B elements) via the voracious_multithread feature

**Skip it when:**
- Small or medium arrays below the per-type diversion threshold (e.g. ~300-800 elements for f64) — you're just paying trait dispatch over calling Rust's own sort directly
- Sorting String, tuples, or arrays — unsupported (Rust's orphan rule blocks tuple impls; String has no implementation yet)
- Types outside the profiled table (u16, u128, i8/i16/i128, and most custom-struct field types) — these fall back to an untuned 'default default' profile the README says is 'clearly not optimized'
- Memory-constrained environments — the out-of-place trait variants can use up to 2x the input array's memory
- Needing an actively released, MSRV-stable dependency — crates.io's last documented release is 1.2.0 (March 2023) and the README's own 'last tested' toolchain is rustc 1.46.0 (2020), despite commits into late 2025

**Integration:** crate · none for single-thread use; optional rayon 1.7 pulled in only by the 'voracious_multithread' feature flag · edition 2018; README's stated 'last tested' toolchain is rustc 1.46.0 stable (2020) — no formal MSRV policy documented · not explicitly documented; all tuning constants in PROFILING.md are profiled on an AMD Ryzen 9 3950x (x86-64) and the README says they are 'valid only for the computer on which I am doing the profiling'

**Vs siblings:** It's the only Rust entry among these siblings (the others are C++), so pick it when you're already in a Rust codebase sorting large primitive arrays and don't want an FFI shim to a C++ sort. If you need a C/C++ library instead, poor-circle/radix_sort is the closer analog (also LSD-style radix sort, benchmarked directly against std::sort/std::stable_sort at up to 1B int32).

**Gotchas:**
- Falls back to Rust's stock sort below a per-type size threshold, so 'wins' on small arrays in the benchmark data are really just measuring Rust's own sort_unstable/stable sort
- Only the types checked off in PROFILING.md's table are actually tuned; everything else (u16, u128, i8/i16/i128, most struct field types) uses an unoptimized default profile
- Closed GitHub issue #22 reports voracious_mt_sort appearing to hang for 2+ hours (192 threads) sorting 200 billion u64 values; the issue was closed with no comments or stated fix, so the failure mode is unresolved in the public record
- Tuning constants (radix, diversion thresholds, thread chunk sizes) are hardcoded per the maintainer's own Ryzen 3950x — PROFILING.md explicitly warns gains may not transfer to other CPUs without re-profiling

**Status:** Repository shows commits into late 2025 (maintenance_status: active), but the crate's own RELEASES.md stops at 1.2.0 (March 2023) and the README's 'last tested' toolchain is rustc 1.46.0 from 2020. MIT-licensed and small enough to vendor or fork if you need to refresh the tuning constants or toolchain yourself.

[repo](https://github.com/lakwet/voracious_sort) · [benchmark](https://github.com/lakwet/voracious_sort/blob/master/results/benchmark_1_2_0/benchmark_results_trait_i64)

##### vxsort-cpp  `C++`  `MIT`  `abandoned`  `Tier C`

AVX2/AVX-512 vectorized quicksort for primitive arrays; beats a ported .NET GC introsort, not std::sort.

**Beats:** scalar introsort ported from the .NET CoreCLR GC (gcsort::introsort_orig), not std::sort — The README's reported ~4.5-4.8x speedup (e.g., 1M int64: 53.08ns/elt scalar vs 11.54ns/elt with 8x unroll; measured on an AMD Ryzen 9 3950X @3.8GHz in a June 2020 benchmark) is against gcsort::introsort_orig, a scalar port of the .NET CoreCLR GC's introsort — not std::sort. No compiler version is stated, and no std::sort numbers are published even though the current repo contains a BM_fullsort.stdsort.cpp benchmark file.

**How:** Branchless AVX2/AVX-512 vectorized partitioning (the 'partition machine') replaces std::sort's scalar Hoare partition, falling back to an in-register bitonic sorting network for blocks under 1024 elements instead of insertion sort. A depth-limited heap-sort fallback guards worst-case recursion, and an Unroll template parameter (1-12) controls how many vector lanes are processed per partitioning step, trading code size for fewer loop-carried dependencies.

**Use it when:**
- Sorting large arrays (benchmarked 4,096 to 1,048,576 elements) of raw i16/u16/i32/u32/i64/u64/f32/f64 on x86-64 with AVX2 or AVX-512 available
- Throughput-bound batch sorts where you can pick the ISA/unroll variant at compile time and don't need a comparator or non-primitive keys
- You want per-element latency down for pointer-sized keys (README: int64 drops from ~53ns/elt scalar introsort to ~11.5ns/elt with unroll x8, unverified against std::sort)
- You're OK vendoring a small, currently unmaintained C++ codebase (MIT) and rebuilding it for your target ISA

**Skip it when:**
- Need a drop-in std::sort replacement with comparators, custom types, or non-x86 targets — no comparator API, and NEON/AArch64 support is stubbed (issue #1, open since 2020) but not implemented
- Need std::sort-relative numbers to justify the switch — README only compares against a self-ported CoreCLR-GC scalar introsort, not std::sort, and no std::sort numbers are published despite a BM_fullsort.stdsort.cpp benchmark existing in the repo
- Care about active maintenance — the default branch's last commit is 2023-05-10; only an unrelated-history 'nextgen' branch has recent (2026) activity
- Small arrays under 4K elements (not benchmarked) or workloads needing a stable sort — this is in-place but not stable, and uses a fixed-size internal scratch buffer sized per template instantiation
- Want CI confidence out of the box — an open 'Build fail' issue (#2) shows the bench/test build breaking against a newer clang/CMake/googlebenchmark combination

**Integration:** static lib · cpu_features (Google, ISA detection), fmt; googlebenchmark and googletest additionally for bench/tests only · C++20 (CMakeLists sets CMAKE_CXX_STANDARD 20), CMake 3.24+; clang recommended by the README, GCC also handled in CMakeLists · x86-64 with AVX2 or AVX-512 (ISA chosen per template instantiation at compile time); AArch64/NEON detection is present in demo.cpp but the sort call is unimplemented

**Vs siblings:** Pick this only if you specifically want an AVX2/AVX-512 partition-plus-bitonic-network vectorized quicksort port of .NET's VxSort for raw numeric arrays and don't need comparator/generic-type support; x86-simd-sort, BlockQuicksort, quadsort, and fluxsort all publish real std::sort or std::stable_sort comparisons and are more actively maintained, so prefer one of them when the baseline claim matters or adoption/maintenance risk is a concern.

**Gotchas:**
- ISA is selected at compile time via which header you include (vxsort.avx2.h vs vxsort.avx512.h) and the vxsort_targets_enable_*.h wrapper; using the wrong one for the running CPU is a caller error (the demo does its own cpu_features runtime check before choosing)
- Only built-in numeric types appear in the benchmark/test suite (i16/u16/i32/u32/f32/i64/u64/f64); no evidence of support for arbitrary structs, strings, or custom comparators
- Internally falls back to heap_sort past a depth limit and to a bitonic-network small-sort under 1024 elements — behavior isn't a single flat algorithm the way std::sort's introsort is, though this is invisible at the call site
- Open issue #2 shows the benchmark/test build breaking under newer clang/CMake due to a googlebenchmark C-dialect flag mismatch — unrelated to the sort code but relevant if you try to reproduce the published numbers

**Status:** Abandoned on its default branch since 2023-05-10 (later activity moved to an unrelated-history 'nextgen' branch); MIT-licensed and small/self-contained enough to vendor, but only 33 stars and an open build-fail issue against its bench/test harness.

[repo](https://github.com/damageboy/vxsort-cpp) · [benchmark](https://github.com/damageboy/vxsort-cpp#results-ryzen-3950x-38ghz)

##### x86-simd-sort (numpy/x86-simd-sort)  `C++`  `BSD-3-Clause`  `active`  `Tier C`

AVX-512/AVX2 SIMD quicksort/select library beating std::sort on primitive arrays and key-derived struct sorts (object_qsort).

**Beats:** std::sort — Numbers come from x86-simd-sort's own README benchmark (benchmarks/bench-objsort.hpp, Google Benchmark, run with --benchmark_filter=*obj*), comparing object_qsort against std::sort on arrays of 3D Point structs (float or double x/y/z) sorted by one coordinate or by Manhattan, Euclidean, or Chebyshev distance from the origin, on an unspecified x86 processor with AVX-512 and no disclosed compiler or flags: up to ~5x faster for float (32-bit) keys and ~4x for double (64-bit) keys sorting by one coordinate, up to ~10x faster sorting by Euclidean distance.

**How:** Built-in-type routines vectorize quicksort partitioning using AVX-512 compressstore instructions (with an AVX2 fallback), based on two cited SIMD-partitioning papers, and drop to bitonic sorting networks on AVX-512/AVX registers for arrays below a size threshold (64-512 elements). object_qsort does not vectorize struct comparisons directly: it extracts each object's key into a separate array, sorts the resulting (key, index) pairs with the SIMD keyvalue_qsort, then permutes the original object array into place with a scalar cycle-following swap loop. Its speedup therefore comes from the primitive keyvalue sort plus, for expensive keys like Euclidean distance, auto-vectorized key computation, not from vectorizing the object comparisons themselves.

**Use it when:**
- Sorting arrays of built-in 16/32/64-bit ints, floats, or doubles (or key-value pairs) on x86-64 hardware with AVX2 or AVX-512, where std::sort's per-element comparator overhead dominates
- Sorting an array of structs by one scalar key -- a single member or a computed metric like Euclidean/Manhattan/Chebyshev distance -- via object_qsort's key-extraction lambda
- Need argsort/argselect/partial_qsort with built-in NaN placement control (nans_last) instead of hand-rolling NaN partitioning around std::sort/std::nth_element
- Batch or offline sorts where allocating O(N) extra memory for keys and an index array is acceptable
- Comfortable depending on code already proven at NumPy/PyTorch/OpenJDK vendoring scale rather than a smaller, newer project

**Skip it when:**
- Target hardware lacks AVX2/AVX-512, or is not x86-64 (no aarch64/ARM support)
- Sort key isn't reducible to one scalar of 32 or 64 bits -- object_qsort's key_func must return exactly float/double/(u)int32/64, not a multi-field comparator
- Memory-constrained settings: object_qsort needs O(N) extra space (a key array plus a uint32/64 index array) on top of the object array itself
- Need numbers independently verified on disclosed hardware/compiler: the object_qsort chart names only 'a processor with AVX-512', no CPU model, compiler, or flags, and the numbers are first-party
- Care about scaling on adversarial input distributions: an independent 2023 analysis (Voultapher sort-research-rs) found worse-than-O(N log N) scaling for the primitive AVX-512 qsort on a random_p5 pattern

**Integration:** header-only (src/x86simdsort-static-incl.h, compile-time AVX2/AVX-512 selection) or static/shared lib (Meson build under lib/, runtime CPUID dispatch) · none for the core routines; googletest and Google Benchmark (>=1.9.2) only if building the optional test/benchmark suite; OpenMP optional for parallelizing qsort/argsort/keyvalue_qsort · C++17; GCC 8+ (GCC 12+ required for _Float16/AVX-512FP16), Clang 8.0+, MSVC 2019 16.8+, or Intel icx · x86-64 with AVX2 or AVX-512 (exact subset varies: skylake-avx512 for 32/64-bit, icelake-client for 16-bit, sapphirerapids for _Float16); no aarch64/ARM

**Vs siblings:** A maintainer directly asked how this compares to vxsort-cpp (issue #12) and no comparison was ever produced, so there's no first-party head-to-head with that sibling. Pick x86-simd-sort over the other primitive-array sorters in this catalog (BlockQuicksort, Boost.Sort spreadsort, IPS4o, LearnedSort, fluxsort, quadsort, radix_sort) specifically when the workload is 'sort a struct by one field or a derived distance metric' via object_qsort, not a flat array of ints -- none of the other siblings' benchmarks target that struct/key-sort shape.

**Gotchas:**
- object_qsort's gain shrinks as sizeof(T) grows or the key gets cheap to compute relative to swap cost, since the final struct permutation is a scalar cycle-following swap loop, not SIMD
- object_qsort's key_func return type must be exactly 32 or 64 bits (float/double/int32/int64/uint32/uint64) or the call fails a static_assert at compile time
- For built-in-type routines, hasnan defaults to false; if the array actually contains NaNs and hasnan isn't set true, behavior is undefined
- GCC 16.0.1 with LTO enabled reportedly failed to build (issue #224, closed without a posted fix) when vendored into NumPy, due to an 'inlining failed: target specific option mismatch' error on an always_inline comparator

**Status:** Actively maintained (last commit 2026-06-25); BSD-3-Clause. 'Copyable' fits since the src/ headers can be vendored standalone at compile time -- as NumPy, PyTorch, and OpenJDK already do -- while the runtime-dispatching library form requires a Meson build.

[repo](https://github.com/numpy/x86-simd-sort) · [benchmark](https://github.com/numpy/x86-simd-sort/blob/main/README.md)

#### string-search-and-hashing

##### Boost.Algorithm Boyer-Moore / Boyer-Moore-Horspool searchers  `C++`  `BSL-1.0`  `active`  `Tier C`

Header-only Boyer-Moore / Boyer-Moore-Horspool string searchers, ~4-5x faster than std::search on long patterns.

**Beats:** std::search — PR #25 (opened 2016 by Jeremy Murphy, still open/unmerged) republishes edited test/search_test2.cpp output on a 2,756,252-entry random 8-bit corpus: std::search 0.4848s vs boyer_moore_search 0.1171s (~4.1x) and boyer_moore_horspool_search 0.1076s (~4.5x) for a 105-entry pattern found mid-corpus, and std::search 1.028s vs boyer_moore_horspool_search 0.1825s (~5.6x) for a 91-entry not-found pattern; compiler, flags, CPU model, and standard library are not stated, and the PR author notes ~5-10% run-to-run variance.

**How:** Both algorithms precompute a bad-character skip table from the pattern (full Boyer-Moore adds a good-suffix table) so on a mismatch the search can jump ahead by more than one position instead of std::search's linear rescan. The skip table is a fixed-size array (O(2^CHAR_BIT) entries) for small numeric value types like unsigned char, or a boost::unordered_map/std::unordered_map otherwise, giving O(pattern length + alphabet size) preprocessing. Horspool drops the good-suffix table for cheaper preprocessing at the cost of slightly weaker worst-case skips.

**Use it when:**
- Long patterns (tens to hundreds of elements) searched against large corpora, the shape of the PR's benchmark (105/43/91-entry patterns over a 2.76M-entry corpus)
- The same pattern is searched repeatedly against many or large corpora: construct a boyer_moore/boyer_moore_horspool object once and reuse operator() to amortize the skip-table build
- Pre-C++17 toolchains, or any C++03/11/14 codebase that can take a Boost dependency but can't use std::boyer_moore_searcher
- Searching over random-access ranges of non-char element types with comparable (and ideally hashable) values, not just byte strings

**Skip it when:**
- Short, one-off pattern searches — the skip-table build can cost more than a plain linear scan for a single small search
- C++17+ code already reaching for std::boyer_moore_searcher/std::boyer_moore_horspool_searcher, which is the same algorithm with no Boost dependency
- Forward-only or input iterators — both searchers require random-access iterators, unlike std::search
- Mixed-type pattern/corpus comparisons — a BOOST_STATIC_ASSERT requires identical value_type on both iterators
- Workloads wanting SIMD-level throughput on x86/ARM byte strings — this is a scalar algorithm; StringZilla or sse4-strstr target that instead

**Integration:** header-only · Boost.Config, Boost.Assert, Boost.StaticAssert, Boost.Range, Boost.Core, Boost.TypeTraits, Boost.Array, and Boost.Unordered (all header-only Boost libraries; part of full Boost distributions) · C++03 (README lists 'Properties: C++03, Header-only'; falls back to boost::unordered_map when BOOST_NO_CXX11_HDR_UNORDERED_MAP is defined, std::unordered_map otherwise) · any (portable C++, no SIMD or architecture-specific code observed in the headers read)

**Vs siblings:** Pick this over sse4-strstr or StringZilla when the workload needs a portable, non-SIMD, header-only implementation that works over arbitrary random-access element types (not just bytes) or that reuses a prebuilt search object across many corpora; pick StringZilla or sse4-strstr instead when the goal is maximum single-call byte-string throughput on x86/ARM via SIMD.

**Gotchas:**
- Random-access iterators are required for both corpus and pattern; forward/input iterators that std::search accepts will not compile
- Pattern and corpus iterators must share the same value_type, enforced at compile time via BOOST_STATIC_ASSERT
- Non-numeric or wide value types fall back to an unordered_map-based skip table, which is slower to build and probe than the fixed array table used for byte-like data
- The much larger Musser-Nishanov searcher proposed in the same PR #25 (still open/unmerged) had a reported segfault on large real-world corpora during development; that bug is in the unmerged code, not the mainline boyer_moore/boyer_moore_horspool searchers this benchmark measures

**Status:** Actively maintained mainline Boost.Algorithm code (develop branch last commit 2026-08-05), BSL-1.0 licensed and header-only, trivial to vendor a single header pair; the PR these benchmark numbers come from has sat open and unmerged since 2016 and proposes a different, unrelated Musser-Nishanov searcher.

[repo](https://github.com/boostorg/algorithm) · [benchmark](https://github.com/boostorg/algorithm/pull/25)

##### CityHash  `C++`  `MIT`  `abandoned`  `Tier C`

Non-cryptographic 64/128-bit string hash family beating Murmur2/Murmur3F, ~1.7-2.5x faster at 64 bytes.

**Beats:** MurmurHash2/MurmurHash3 (Murmur2, Murmur3F, Murmur3A) — widely-used non-cryptographic hash functions used in place of std::hash — Google's own README (MIT, ~2011-2013 numbers) reports CityHash64 v1.0.3 vs Murmur2/Murmur3F on a single core of a 2.67GHz Xeon X5550: 9ns vs 15ns/23ns at 64 bytes (~1.7x-2.5x faster), and CityHashCrc256 at 5-5.5 bytes/cycle vs Murmur3F's 2.4 bytes/cycle on long strings (~2.1x-2.3x faster); compiler and flags used for these specific numbers are not stated.

**How:** Short inputs (<=4, <=8, <=16, <=32, <=64 bytes) each get a dedicated fast path using register-width multiply/rotate mixing tuned to that length bucket, so most hash-table-key-sized strings finish in a handful of instructions. For long strings, CityHashCrc128/256 layer that same multiply-rotate mixing on top of the hardware CRC32 instruction (_mm_crc32_u64) as a cheap mixing primitive, reaching about 5-5.5 bytes/cycle versus ~2.4 bytes/cycle for pure-software Murmur3F.

**Use it when:**
- Fixed, fully-buffered byte strings (not streamed) used as hash-table keys, especially short strings in the 1-64 byte range
- x86-64 targets with SSE4.2 available, where CityHashCrc128/256 can use the CRC32 instruction for long-string throughput
- Codebases that want to vendor a tiny, frozen source drop (city.cc/city.h/citycrc.h) rather than add a package-manager dependency
- Need an MIT-licensed implementation with a stable, unchanging API (no upstream churn since 2013)
- Non-adversarial input, or input always hashed with a caller-supplied random seed via the *WithSeed variants

**Skip it when:**
- Need to hash data arriving in chunks/streams — no incremental API exists
- Want the fastest available long-string throughput on modern hardware — newer SIMD-tuned hashes (xxh3, rapidhash, komihash) beat it and are actively maintained
- Non-x86-64 or no-SSE4.2 platform and you wanted the CRC-based variants (CityHashCrc128/256 hard-require _mm_crc32_u64)
- Untrusted/adversarial keys going into a hash table without supplying a random seed — CVE-2012-6051 hash-flooding DoS applies to unseeded CityHash
- Want a maintained project — repo is archived by Google, last real release was v1.1.1 in June 2013

**Integration:** source-drop · none (stdint.h, utility); CRC variants additionally need an SSE4.2-capable CPU and compiler support for the _mm_crc32_u64 intrinsic · not documented precisely; header only uses uint32_t/uint64_t/std::pair, autoconf build dates to 2011-2013, no C++11-only constructs observed · little-endian x86/x86-64 primarily (CRC variants need SSE4.2); header states big-endian support is only lightly tested

**Vs siblings:** Pick CityHash mainly for legacy/reproducibility reasons (matching an existing on-disk hash or a 2011-era baseline); for new code, komihash, rapidhash, or t1ha in this catalog beat both CityHash and Murmur with active maintenance, and MUM/VMUM-V2 explicitly benchmarks itself against CityHash64 and wins.

**Gotchas:**
- No seed randomization by default: CityHash64/CityHash32 without a seed are vulnerable to a hash-flooding DoS (CVE-2012-6051); pass a random seed via the *WithSeed/*WithSeeds variants for adversarial input
- CRC-based variants (CityHashCrc128/256 in citycrc.h) require an SSE4.2 CPU and the _mm_crc32_u64 intrinsic; the autoconf build's --enable-sse4.2 flag must be set or citycrc.h isn't installed
- hash(a+b) cannot be derived from hash(a) and hash(b) for any function in this file (stated in the header) — no incremental combination of partial hashes (open issue #17)
- Big-endian support is explicitly called out in city.h as 'only lightly tested'

**Status:** Archived by Google; last commit 2022-07-19 was housekeeping, last real release was v1.1.1 in June 2013. MIT-licensed and small enough (3 source files) to vendor, but expect no further fixes — known issues such as CVE-2012-6051 and #46 (Windows byteswap.h detection) remain open.

[repo](https://github.com/google/cityhash) · [benchmark](https://github.com/google/cityhash/blob/master/README)

##### StringZilla  `C++`  `Apache-2.0`  `active`  `Tier C`

Header-only SIMD string kernels (search, hashing, sort, UTF-8) beating std::string::find and find_first_of.

**Beats:** std::string::find — README Performance table: finding the first occurrence of a ~5-byte random word, std::string::find (STL, GCC+glibc) hit 9.1 GB/s vs sz_find 21.0 GB/s (~2.3x) on an Intel Sapphire Rapids Xeon4, and 10.9 vs 37.1 GB/s (~3.4x) on Apple M5 Pro (Apple Clang+libc++). Splitting lines on \n/\r, std::string::find_first_of hit 1.1 GB/s vs sz_find_byteset 13.8 GB/s on Xeon4, and 4.1 vs 23.7 GB/s on M5 Pro.

**How:** Per-ISA SIMD kernels (SSE4.2/AVX2/AVX-512 on x86, NEON/SVE/SVE2 on ARM, plus WASM SIMD128, RISC-V RVV, PowerPC VSX, LoongArch) selected at compile time or via a runtime dispatch table in the optional shared build. Needle-length-adaptive algorithm choice: brute-force SIMD comparisons at multiple needle offsets for short needles, Boyer-Moore-Horspool with a bad-character shift table and Raita-style character-anomaly detection for mid/long needles, and SWAR (64-bit word) fallback with no SIMD.

**Use it when:**
- Hot substring search over large text buffers where std::string::find shows up in a profile
- Splitting/tokenizing on multiple delimiter bytes (replacing find_first_of/strcspn) via sz_find_byteset
- Multi-language pipelines that need identical search/hash/sort kernels across C/C++/Python/Rust/Go/Swift/JS/C#/Java
- Unicode case-folding, segmentation, or normalization at C speed instead of ICU/ICU4X
- Apple Silicon or ARM server targets, where the README reports the widest gap over the system libc strstr

**Skip it when:**
- Multi-pattern literal matching: no Aho-Corasick automaton is shipped; README points to hyperscan or pyahocorasick instead
- Need a std::hash-compatible hasher: sz's hash is a separate AES-based non-standard function, not a std::hash specialization
- Building for i386 — currently broken (open issue #341)
- Need find_all() match offsets relative to the parent string — reported broken in open issue #278
- Very short, early-diverging comparisons (equality/order checks) — README itself says vectorization is 'almost useless' there
- Risk-averse adoption of sz::argsort right now — open crash report (#337) and an open UBSAN misaligned-write report (#279)

**Integration:** header-only · none (freestanding build available via SZ_AVOID_LIBC=1); optional precompiled shared library for runtime dispatch · C99 / C++11 minimum to compile; CI-validated on GCC 12+, Clang 16+, MSVC 2022, NVCC CUDA 12+ (GCC 10 and older fail STL insert conformance needed by the test suite) · x86-64 (SSE4.2/AVX2/AVX-512 tiers), aarch64 (NEON/SVE/SVE2), WebAssembly (SIMD128 via wasm32-wasip1), RISC-V (RVV), PowerPC (VSX), LoongArch; i386 currently fails to build (issue #341)

**Vs siblings:** sse4-strstr is the closest sibling but covers only substring search as a single header with no bindings; pick StringZilla when you also need byte-set scanning, hashing, sorting, or non-C++ language bindings and can accept a larger, fast-moving dependency. Pick sse4-strstr instead when you want a small, frozen, single-purpose kernel to vendor with nothing else attached.

**Gotchas:**
- sz_find_byte_serial historically mis-compared bytes > 0x7F when compiled with -fsigned-char (issue #306, closed/fixed) — a signed-char caution sign for anyone pinning old versions
- find_all() results reportedly cannot recover the match's position within the parent string (open issue #278)
- sz::argsort has an open crash report (#337)
- UBSAN reports a misaligned-address write in a SWAR code path (open issue #279)

**Status:** Actively maintained (last commit 2026-08-12, 3,563 stars, Apache-2.0); header-only core is easy to vendor ('copyable'), but several open bugs (i386 build failure, argsort crash, misaligned-write UBSAN report) mean trusting specific kernels rather than the whole surface unverified.

[repo](https://github.com/ashvardanian/StringZilla) · [benchmark](https://github.com/ashvardanian/StringZilla/blob/main/README.md)

### toolchain-and-build

#### build-systems

##### Buck2  `Rust`  `MIT OR Apache-2.0`  `active`  `Tier C`

Meta's Rust rewrite of the Buck build system; up to 2x faster than Buck1 in Meta's internal monorepo usage.

**Beats:** Buck1 (Meta's original Buck build system) — The only first-party number is the README's 'up to 2x faster than Buck1 in practice,' sourced from Meta's internal production usage comparing Buck2 to Buck1 across Meta's monorepo. No specific workload, project, methodology, compiler/stdlib, or hardware is given, and the README itself says comparisons against Bazel-class systems 'have yet to be performed.'

**How:** Core build graph runs on `dice`, Meta's own incremental computation engine, so only invalidated nodes recompute on a change. Remote Execution support (Bazel's REAPI, works with BuildBarn/BuildBuddy/EngFlow/NativeLink) enables distributed/cached builds and, when used, hermeticity: all rule inputs must be declared or the build fails. A persistent background daemon (buckd) plus filesystem watching avoids repeated startup/scan cost on ultra-large repos. Build files and rules are parsed/evaluated with `starlark-rust`, Meta's own fast Starlark interpreter.

**Use it when:**
- Large, multi-language monorepos already paying the cost of Make/Bazel-style top-down builds and needing better incremental-rebuild accuracy
- Teams that can invest in Remote Execution infrastructure to get real hermetic, cacheable builds
- Projects wanting a single build/test/query tool across languages with cross-language dependencies (e.g. Rust crate <- OCaml <- Python)
- Teams willing to write/port BUCK/Starlark rule definitions instead of reusing existing CMake/Make/Cargo build files
- Users comfortable tracking a fast-moving HEAD with no stable release tag

**Skip it when:**
- Small or single-language projects where Make/CMake/Cargo already work fine — migration cost isn't justified
- Teams wanting hermetic guarantees without standing up Remote Execution: local-only build steps are not sandboxed/hermetic (README footnote)
- Projects needing precompiled-header support: open issue #368 says PCH 'don't seem to be working'
- Workloads sensitive to daemon startup latency: open issue #507 notes 'daemon startup is a bit slow'
- Anyone needing a stable, versioned release: no stable release tag exists, Meta itself tracks HEAD

**Integration:** source-drop · none (self-contained Rust workspace; Remote Execution backend optional and external, e.g. BuildBarn/BuildBuddy/EngFlow/NativeLink) · prebuilt binaries via GitHub releases or dotslash; building from source uses a pinned Rust nightly (rust-toolchain.toml: nightly-2026-07-05) · Linux, macOS, Windows (CI has setup_linux_env/setup_macos_env/setup_windows_env and a Cross.toml)

**Vs siblings:** Pick Buck2 over Mill/tup/xmake when you need true multi-language monorepo builds with Remote-Execution-backed hermeticity and are willing to adopt Starlark BUCK files; its 2x number is Meta-internal Buck1-vs-Buck2 only (evidence tier C, no workload/hardware given), so it is not a verified head-to-head against Make/CMake/Ninja/Bazel/Cargo the way tup's or Mill's numbers are.

**Gotchas:**
- Local-only build steps are NOT sandboxed/hermetic; only Remote-Execution-backed builds get full hermeticity (README footnote)
- Open issue #340: buck2 recompiles *all* source files when a link-only dependency changes
- No stable release tag; Meta itself runs latest HEAD, so 'rough edges' are expected for outside users (README warning)
- Precompiled headers reportedly not working (issue #368)

**Status:** Actively maintained (commits as of 2026-09-24, 4.4k stars, used in production at Meta), but usability is 'copyable' rather than a stable package: no stable release tag, dual MIT/Apache-2.0 licensed.

[repo](https://github.com/facebook/buck2) · [benchmark](https://github.com/facebook/buck2/blob/main/README.md)

##### xmake  `C`  `Apache-2.0`  `active`  `Tier C`

Lua-scripted cross-platform build tool with built-in package manager; beats CMake+Make, roughly matches plain Ninja.

**Beats:** Make (via CMake-generated Makefiles) — First-party README benchmark building xmake's own in-repo xmake-core (C) target: on Termux (8-core, -j12) xmake finished in 24.890s vs cmake(gen+make)'s 5.416s+28.473s=33.889s total (~1.36x), but plain ninja ran in 25.682s, barely behind xmake; on macOS (8-core, -j12) xmake was 12.264s vs cmake(gen+make)'s 1.203s+14.030s=15.233s total (~1.24x), while plain ninja was faster than xmake at 11.327s. Single-threaded (-j1) gaps vs cmake+make were smaller (~1.08-1.15x). Exact CPU model and compiler/flags are not stated.

**How:** xmake's core engine (xmake-core, written in C, bundled with a modified Lua/tbox runtime) parses xmake.lua and runs the resulting dependency DAG directly in one process and one invocation, the same way Ninja does, instead of the two-stage 'generate Makefiles, then run recursive make' path CMake+Make requires. The measured speedup is specifically against that generate+make baseline (~1.24-1.36x at -j12, ~1.08-1.15x at -j1); xmake does not claim to beat Ninja's own scheduler and is measurably not doing so here. It also ships an optional content-based local/remote build cache (not exercised in this particular benchmark).

**Use it when:**
- Migrating off raw CMake+Make (not CMake+Ninja) where a single tool that configures and builds without a separate generate step is the goal
- Want a built-in cross-platform package manager instead of wiring vcpkg/conan into CMake by hand
- Targeting niche platforms/toolchains in one config file (WDK drivers, CUDA, Zig, Rust, embedded compilers like Keil/IAR/TI, arbitrary cross toolchains) that CMake supports poorly
- New small-to-medium C/C++ project where xmake.lua's terser syntax is a feature rather than a migration cost
- Want distributed/remote build or a build cache without separately standing up distcc/ccache/sccache

**Skip it when:**
- Project already builds via CMake+Ninja or Meson: per this same README, xmake is on par with or slightly slower than plain Ninja, so there is no measured win there
- Team depends on CMake's mature IDE/CI/third-party tooling ecosystem; xmake's own IDE plugins (VSCode/Sublime/IDEA/Zed) are official but far smaller in adoption
- Large existing CMake codebase: there is no automatic CMakeLists.txt -> xmake.lua converter in this repo, so migration means hand-porting build logic
- Treating the claimed multiplier as portable: this is a first-party, tier-C benchmark with no CPU model, OS version, or compiler/flags disclosed
- Need airtight incremental-build correctness across all language backends: open issues report gaps for at least one backend (see gotchas)

**Integration:** CLI binary (not a library) — precompiled install via curl/wget/PowerShell script or OS package managers · none to install (self-contained binary); requires whatever C/C++/other-language toolchain the project itself needs (GCC/Clang/MSVC/etc.), which xmake detects rather than provides · not documented as a minimum — no dependencies outside the standard library per README; current release v3.1.1 (2026-08-27); source-build requirements (compiler for xmake-core, Lua) not stated in README · Windows, macOS, Linux, FreeBSD/NetBSD/OpenBSD/DragonflyBSD, Solaris, Android, iOS, watchOS, tvOS, visionOS, MSYS/MinGW/Cygwin, Wasm, Haiku, HarmonyOS, and arbitrary cross-toolchains, each with multiple listed architectures

**Vs siblings:** None of the catalogued siblings are direct substitutes: ccache caches compiler invocations and composes with any build system including xmake; Mill/Buck2 target JVM/Meta monorepo ecosystems, not general C/C++; tup targets the specific pathology of huge (100k-file) trees with slow no-op/rebuild checks under Make. Pick xmake over CMake+Make when you also want a bundled package manager and one-file multi-language config, but pick tup instead if your real bottleneck is Make's no-op/rebuild-check cost at large scale, since xmake's own numbers show it merely tying Ninja rather than tup's claimed order-of-magnitude jump.

**Gotchas:**
- The repo's default branch is 'dev', not 'master'; benchmark_url points at master but the same numbers appear on dev's README
- README's headline claim is 'on par with Ninja' — in this exact benchmark table xmake (12.264s parallel / 39.937s single, macOS) is slower than plain ninja (11.327s / 38.995s), so 'faster' here means faster than CMake+Make, not faster than Ninja
- Benchmark hardware is described only as '8core' with no CPU model, OS version, or compiler/flags disclosed
- Open issues report incremental-build gaps for at least one language backend ('rust project not being rebuilt when modified', #4790) and occasional flaky build failures fixed only by restarting (#4796); verify incremental correctness for your specific toolchain before relying on it

**Status:** Actively maintained: last commit 2026-09-22, latest release v3.1.1 (2026-08-27), 259 open issues, 12.2k stars, no open security advisories found; Apache-2.0 licensed and distributed as a self-contained precompiled binary, so it's cheap to adopt or vendor.

[repo](https://github.com/xmake-io/xmake) · [benchmark](https://github.com/xmake-io/xmake/blob/master/README.md)

#### compile-caching-and-distribution

##### FASTBuild  `C++`  `Zlib`  `active`  `Tier C`

Full build system combining object caching, unity builds and distributed compilation; replaces make/MSBuild, not a wrapper.

**Beats:** the same build without FASTBuild's object cache, Unity/Blob builds or distributed compilation (implicit; no baseline tool is named) — fastbuild.org's features page gives first-party, unqualified figures — object caching 'up to 10x', Unity/Blob builds 'improvements of 10x or more', distributed compilation 'speedups of 5x are common' — each measured against the same build without that FASTBuild feature enabled. No workload, hardware, compiler, or flags are given, so these are vendor round numbers, not a reproducible benchmark.

**How:** Unity/Blob builds merge many .cpp files into fewer translation units, cutting per-file compiler startup/parse overhead. The object cache stores compiled objects keyed by build inputs and reuses them across machines instead of recompiling identical code. Distributed compilation preprocesses source locally then ships it to idle worker machines running FBuildWorker, so object compilation runs in parallel across a farm rather than being limited to one machine's core count.

**Use it when:**
- Large multi-platform (PC/console/mobile) C/C++ game or engine codebase, where you're willing to author the build in FASTBuild's own BFF language
- Team has spare workstation or render-farm capacity to run FBuildWorker for network distribution
- CI or local dev with deterministic compiler output, where object-cache hits repeat across builds and machines
- Cross-compiler shop needing one build tool across MSVC, GCC, Clang, SNC, GreenHills, CodeWarrior, NVCC
- Want unity-build automation without hand-writing jumbo .cpp generation scripts

**Skip it when:**
- Want to keep an existing CMake/Make/MSBuild/Ninja build and just add caching or distribution without rewriting build files
- No dedicated worker machines or spare network compute — distributed mode adds nothing without hardware to distribute to
- Non-deterministic compiler output or unusual toolchains: issue #1021 (cache errors when system locale differs) and #992 (clang-cl PCH + cache 'fatal error in some situations') show real cache-correctness edge cases
- Linux build farm with >32 cores per worker: issue #1197 reports the CPU-affinity mask is 32-bit, giving a wrong mask on wider machines
- Small or single-machine project where compile time is already short — BFF authoring and cache/worker setup cost may not pay off

**Integration:** source-drop · none documented for the core build; the OSUI component links native OS UI frameworks (WinAPI on Windows, Cocoa .mm files on macOS) · not documented as a stated minimum; Linux CI (Linux.yml) builds and tests with GCC 10 and Clang 15 on Ubuntu 22.04 — Windows/macOS minimum compiler versions not checked this session · Windows, Linux and macOS as build hosts (README); used to target PC, Mac, Linux, consoles, smartphones and retro systems as build outputs — specific host CPU architectures not documented

**Vs siblings:** Pick FASTBuild when you're building (or willing to rebuild) a multi-platform C/C++ project around its own BFF language and want unity builds, object cache and worker-farm distribution bundled in one tool. Pick NativeLink or HOMCC instead when you need to keep an existing Bazel/REAPI or distcc-compatible build and only add remote caching or distributed compilation without rewriting build files, or octobuild when the target is specifically Unreal Engine's UBT/UAT pipeline.

**Gotchas:**
- Cache correctness assumes deterministic compiler output; issue #1021 shows cache errors when the system locale differs and #992 shows clang-cl PCH + cache producing a fatal error in some situations
- Distributed compilation is reported to intermittently fail (issue #1058, open, 'Need More Info')
- Linux CPU-affinity helper uses a 32-bit mask (issue #1197), so it can compute the wrong core mask on machines with more than 32 cores
- GitHub's UI reports 'no license' for this repo because the license file lives at Code/LICENSE.TXT rather than repo root, even though it is zlib-licensed

**Status:** Actively maintained — the dev branch (where patches land) was last committed 2026-09-20, days before this entry — and zlib-licensed (Code/LICENSE.TXT), so it's free to vendor; its 1.4k GitHub stars understate real usage since it's mainly distributed via fastbuild.org binaries and used by many closed-source game studios.

[repo](https://github.com/fastbuild/fastbuild) · [benchmark](https://www.fastbuild.org/docs/features.html)

##### HOMCC  `Python`  `MIT`  `active`  `Tier C`

Distributed C/C++ compiler wrapper replacing distcc with server-side dependency caching and compression for thin uplinks.

**Beats:** distcc — On an internal, non-public Celonis C++ codebase built with clang++-14 (server job limit 112, 60 compilation threads), the README's bar chart shows homcc beating distcc by about 6.3x at 5/25 Mbps (~9.2 vs ~57.5 min), narrowing to ~1.4x at 40/200 Mbps, and homcc being slightly slower than distcc at gigabit (~5.8 vs ~4.9 min). No CPU/hardware spec, raw data, or runnable benchmark script is published; the numbers are estimated from bar heights in an image, and the README's prose claim of gains 'by some orders of magnitude' overstates what its own chart shows.

**How:** On a cache miss homcc still sends preprocessed sources like distcc, but homccd keeps a persistent, size-bounded (LRU, `HOMCC_MAX_DEPENDENCY_CACHE_SIZE`) cache of dependency files keyed by content hash, so once warm only genuinely new headers/sources cross the network instead of the full preprocessed unit every time. Transferred sources and resulting object files are additionally compressed with lzo or lzma. Both mechanisms specifically target bandwidth, not CPU parallelism, which is why the reported gains shrink to nothing as link speed rises.

**Use it when:**
- Remote/distributed C or C++ builds (gcc or clang) over thin or variable-bandwidth links (roughly 5-40 Mbps in the README's own numbers), e.g. work-from-home developers hitting an office build farm
- Teams already using a distcc-style CCACHE_PREFIX or conan-profile hook and willing to swap in a different client/server pair
- Need sandboxed remote compilation per client via schroot profiles or docker containers rather than running arbitrary code directly on the build host
- Debian/Ubuntu-based build infrastructure (packaged and tested as .deb on Ubuntu 22.04)
- Want to tunnel remote compiles over SSH (multiplexed ControlMaster) instead of exposing a plaintext TCP service

**Skip it when:**
- Gigabit or otherwise unconstrained links to the build farm — the project's own chart shows distcc is not slower (slightly faster) once bandwidth stops being the bottleneck
- Untrusted/public networks without a VPN or SSH tunnel — there is no built-in TLS; homcc transmits source over plain TCP by default and the README explicitly warns not to expose homccd publicly
- Environments needing per-client connection limits on the server — homccd does not cap simultaneous connections from one client, so a single client can exhaust the job pool
- Non-Debian/Ubuntu targets or languages other than C/C++ — schroot sandboxing and the packaging are Debian-specific, and gcc/clang are the only supported compilers
- Projects wary of small-team tooling — 24 stars, single corporate maintainer (Celonis), no independent adopters visible; internal benchmark numbers cannot be reproduced by outsiders

**Integration:** source-drop · python-lzo (>=1.12, needs liblzo2-dev/apt python3-lzo) for compression; sysv_ipc for the client's semaphore-based concurrency control; optional schroot or docker for sandboxed remote execution; ssh for tunneled hosts · Python 3.9+ (debian/control declares X-Python3-Version >= 3.9; CI runs on 3.9); gcc or clang on both client and server · Linux, packaged and CI-tested for Debian/Ubuntu (ubuntu-22.04); schroot sandboxing is Debian/Ubuntu-specific, docker sandboxing is more portable but the server itself targets Linux

**Vs siblings:** Pick homcc over NativeLink, FASTBuild, or octobuild specifically when your bottleneck is a thin/variable uplink to an existing distcc-style distributed build farm and you want server-side dependency caching plus compression to shrink that — NativeLink targets single-machine local build acceleration (no distribution), FASTBuild is a from-scratch build system with its own distribution/unity-build model, and octobuild is scoped to Unreal Engine's UBT/UAT toolchain; none of them are distcc drop-in replacements for bandwidth-constrained remote C/C++ compilation.

**Gotchas:**
- No built-in transport encryption: plain TCP hosts send source unencrypted; use an SSH-tunneled `@HOST`/`user@HOST` entry or a VPN, and never expose homccd on an untrusted network
- homccd does not limit simultaneous connections per client, so one misbehaving client can consume the entire server job pool
- docker sandboxing requires the container to bind-mount the host's /tmp to /tmp so the server-side dependency cache is reachable inside the container; schroot sandboxing has the same /tmp-mount requirement
- Client relies on SysV semaphores for concurrency bookkeeping — historically a source of race-condition bugs (see issues 'Fix SysV semaphore race', 'AttributeError on HostSemaphore __exit__'), now fixed but worth knowing if debugging odd hangs

**Status:** Actively maintained by Celonis (last commit 2026-08-18, v1.0.4 tagged the same day, zero open issues) under the MIT license; small adoption (24 stars) but the codebase is compact and copyable/vendorable if you accept the Debian/Ubuntu-oriented packaging.

[repo](https://github.com/celonis/homcc) · [benchmark](https://github.com/celonis/homcc#readme)

##### octobuild  `Rust`  `MIT`  `active`  `Tier C`

Rust compiler cache for Unreal Engine that impersonates IncrediBuild's xgConsole to speed up re-compiles vs. no cache.

**Beats:** stock Unreal Build Tool / Unreal Automation Tool build without octobuild (README 'Without octobuild' column) — The README's first-party benchmark table (unnamed UE 5.0.3 game project, DebugGame configuration, no stated compiler flags) shows a fully warm (100%) cache beating a build without octobuild by about 2.4x-6.5x across platforms — e.g. Linux 3m54s to 36s, Win64 8m4s to 2m15s (MSVC 2019) — on an AMD Ryzen 7 3700X/32GB (Linux) or Intel Core i7-9700F/32GB (Windows/console) with SSD storage; a cold (0%) cache showed no speedup and was up to ~25% slower on Win64 (8m4s to 10m6s).

**How:** It is a content-addressed disk cache of individual compile actions, similar in spirit to ccache/sccache, avoiding re-invocation of cl.exe/clang for translation units it has already built. The repo also ships octo_agent/octo_builder/octo_coordinator and a src/cluster module, suggesting optional distributed-build support beyond local caching, but this is undocumented in the README and not covered by the benchmark. Per the README's own numbers the entire measured speedup is cache-hit driven: at 0% cache hit rate it is roughly neutral to slower than no octobuild at all, presumably from added hashing/IPC overhead.

**Use it when:**
- Unreal Engine or UE-based game project doing iterative DebugGame rebuilds after small source edits, with a cache that can stay warm between builds
- Team already using, or willing to enable, IncrediBuild-style XGE executor integration in UBT/UAT
- Windows target with MSVC 2019/2022 (the benchmarked and best-documented path)
- Linux or macOS target where you can apply the listed UE engine patches (some already merged in UE >= 5.2 / >= 5.3)
- Dev or CI machines with spare local SSD space for a large (default 64GB) persistent cache

**Skip it when:**
- Cold-cache or from-scratch CI builds: the README's own table shows octobuild is equal to or up to ~25% slower than no octobuild at 0% cache hit rate (Win64 8m4s -> 10m6s)
- You need a validated comparison against ccache, sccache, distcc, or IncrediBuild itself — none appears in the README; the only baseline is 'without octobuild'
- Non-Unreal C/C++ projects: it's UE-specific (vs/clang compiler pre/postprocessing, XGE action-graph parser), not a general-purpose compiler cache
- You can't spare disk for a multi-GB persistent cache, or your build environment is ephemeral so the cache never warms up
- You need compiler flags and an exact reproducible harness for the benchmark numbers — the README doesn't state flags and uses an unnamed game project

**Integration:** source-drop · Rust crates (bincode, crossbeam-channel, petgraph, reqwest, serde, sha2, xml-rs, figment, thiserror, uuid, etc.) plus the octobuild/daemon-rs and octobuild/ipc-rs git dependencies; winapi/winreg on Windows. Also distributed as prebuilt packages via Chocolatey, WinGet, Homebrew, and apt/deb. · Rust stable (edition 2021 crate, CI builds against dtolnay/rust-toolchain@stable with no pinned MSRV); Windows build additionally needs Visual Studio 2019 or 2022 with the C++ desktop workload · Win64 (MSVC 2019/2022), Linux, macOS, plus PS4/PS5/Xbox One/Xbox Series X and Android/iOS listed as supported; console/mobile targets build through UE's own toolchains

**Vs siblings:** Pick octobuild specifically because the project is Unreal Engine or UE-based — its xgConsole/ib_console impersonation and MSVC/clang postprocessing are UE-specific integration points that NativeLink, FASTBuild, and HOMCC don't provide. Those siblings target generic CMake/Ninja or distcc-based C/C++ builds and would need a custom UE integration to be used at all, whereas octobuild works with UBT/UAT's existing XGE executor path out of the box.

**Gotchas:**
- Cold cache makes the build slower than not using octobuild at all (README: Win64 8m4s without octobuild vs. 10m6s at 0% cache hit)
- Default disk cache is 64GB; tune via OCTOBUILD_CACHE_LIMIT_MB, and OCTOBUILD_CACHE_MODE can set it to read-only or fully disabled
- On Windows, long command lines can hit 'ERROR: The filename or extension is too long (os error 206)' — fix is OCTOBUILD_USE_RESPONSE_FILES=true, which is already the Windows default
- Source tree contains cluster/agent/coordinator/builder binaries implying distributed (multi-machine) build support, but this is undocumented in the README and unmeasured in the benchmark

**Status:** Actively maintained (last commit 2026-09-15, 285 stars, packaged for Chocolatey/WinGet/Homebrew/apt) and MIT-licensed, but it's a set of UE-specific CLI binaries rather than a general library, so 'copyable' means vendoring the tool, not embedding source into another project.

[repo](https://github.com/octobuild/octobuild) · [benchmark](https://github.com/octobuild/octobuild#benchmark)

#### compilers-frontends

##### MIR / c2m (C2MIR)  `C`  `MIT`  `active`  `Tier C`

Lightweight JIT toolkit whose C11 front-end (c2m) compiles a header-free C function ~80x faster than gcc -O2.

**Beats:** GCC — On an Intel i5-13600K (Fedora 37, GCC 12.3.1), c2m -eg compiled a single header-free C function (Eratosthenes sieve) in 336us vs gcc -O2's 27.1ms (~80x) and gcc -O0's 26.1ms (~77x, with gcc reading source from an in-memory filesystem to remove disk I/O); the resulting c2m-generated machine code then ran at ~92% of gcc -O2 speed on that same sieve and ~91% geomean (0.96 average) across 15 small C benchmarks from the repo's own suite.

**How:** c2m uses a hand-written 4-pass pipeline (PEG-based recursive-descent parser, no yacc/flex, then context checking, then MIR generation) instead of a heavyweight preprocessor/parser/optimizer stack. MIR-generator itself runs only a short, deliberately minimal optimization pipeline (SSA built via Braun's algorithm, global value numbering, copy/dead-store/dead-code elimination, and a priority-based linear-scan register allocator with aggressive coalescing) instead of GCC's full middle end, keeping per-function compile overhead in the hundreds-of-microseconds range.

**Use it when:**
- Embedding a C-based JIT inside an interpreter or dynamic-language runtime (the README's own target: CRuby/MRuby-style hot-path specialization)
- Latency-sensitive compile paths where a single small function needs microsecond-scale turnaround rather than a whole translation unit
- Lazy or basic-block-level code generation (-el/-eb) to defer codegen cost until a function or block is actually executed
- Targeting x86-64, aarch64 (including Apple Silicon), ppc64le, s390x, or riscv64 on Linux/macOS and willing to vendor a small (~55K LOC), MIT-licensed compiler
- Compiling small, self-contained C programs (no large #include trees) from the command line without installing GCC

**Skip it when:**
- Code needs VLAs, `_Complex`, `_Atomic`, or `_Thread_local` -- c2m's C11 subset omits them (c2mir/README.md lists them as unimplemented; issue #394 is an open request for `_Thread_local`)
- Large, multi-file, header-heavy production builds -- the quoted ~80x is a single function with no #include files on an in-memory gcc run; a real build sees a much smaller gap per the record's own tradeoffs note
- You need GDB-quality source-level debug info for compiled/JITted code -- still an open feature request (#442, opened Jul 2026)
- Untrusted or adversarial C input -- several open heap-buffer-overflow/segfault issues in the parser and preprocessor (#353, #360, #362, #364, #365, #366) mean the front-end isn't hardened
- You need generated code to match or beat gcc -O2 at runtime -- c2m -eg trades that away, running at ~91% geomean / ~92% on sieve of gcc -O2 speed

**Integration:** static lib + shared lib + source-drop (also builds a standalone `c2m` compiler binary) · none to build (self-contained, builds with system gcc/clang); programs it compiles link libc/libm at runtime · C11/gnu11 to build MIR itself (GCC or Clang); c2m implements a C11 subset (no VLA/_Complex/_Atomic/_Thread_local) plus some GNU extensions · x86-64, aarch64 (incl. Apple Silicon), ppc64le, s390x, riscv64 on Linux; x86-64/aarch64 macOS; Windows (MinGW/MSVC) is built by GNUmakefile though the README disclaimer only warranties the Linux/OSX/ppc64le/s390x/riscv64 CI-tested platforms

**Vs siblings:** Pick MIR/c2m over TinyCC when you need an embeddable JIT library (interpret-or-generate, lazy per-function/per-block codegen, MIR IR you can also build directly via API) rather than just a fast standalone `cc`; TinyCC's ~9x-over-gcc number is for a traditional whole-program compile-and-link and doesn't offer c2m's lazy JIT interfaces. Neither zapcc (a caching Clang wrapper for incremental full C++ builds) nor cg_clif (a Rust/Cranelift backend) is a real alternative here -- both target different languages and build workflows entirely.

**Gotchas:**
- No `_Thread_local`, `_Atomic`, VLA, or `_Complex` support in c2m (c2mir/README.md; issue #394 open)
- Thread safety is per-MIR_context: separate contexts per thread need no synchronization, but sharing one context across threads isn't documented as safe
- Using C as the JIT input (instead of building MIR IR directly via the API) can slow compilation up to 2x, per README
- Multiple segfault/heap-buffer-overflow issues remain open in the parser/preprocessor path (e.g. #360, #362, #364, #365, #366), so malformed C input isn't guaranteed to fail safely

**Status:** Actively maintained -- commits and issue activity continue through Sep 2026 (last commit 2026-06-19, new issues as recent as #475 on 2026-09-03); MIT-licensed and small (~55K LOC per README) enough to vendor, with 'copyable' usability meaning a source/library integration rather than a packaged install.

[repo](https://github.com/vnmakarov/mir) · [benchmark](https://github.com/vnmakarov/mir/blob/master/README.md)

##### rustc_codegen_cranelift (cg_clif)  `Rust`  `MIT OR Apache-2.0`  `active`  `Tier C`

Drop-in Cranelift codegen backend for rustc that replaces LLVM to cut debug-build compile times.

**Beats:** rustc — First-party numbers only. bjorn3's Nov 2024 progress report says that on the rustc-perf suite, after enabling lld for non-LLVM backends, cg_clif was '10-50% faster' than cg_llvm on most benchmarks, with a couple of pathological benchmarks still regressed; no hardware, exact rustc version, or raw data are given. Separately, issue #878 (2020) reported debug-profile clean and baseline-incremental builds about 10-60% faster (often ~40%) versus cg_llvm, but clean-incremental builds up to ~200% slower due to uncached object files.

**How:** Cranelift is a simpler, JIT-oriented code generator with far less optimization machinery than LLVM, so it spends much less time per function translating MIR to machine code, trading away optimized codegen quality that doesn't matter for debug builds. The Nov 2024 progress report attributes the bulk of the observed win to switching the link step to lld for non-LLVM backends (rust-lang/rust PR #132774) and to adding a BufWriter around object-file writes, which fixed a specific regression on the 'coercions' rustc-perf benchmark.

**Use it when:**
- Local dev-loop cargo build/cargo check cycles where debug binaries are compiled and rerun repeatedly and compile latency matters more than runtime speed
- Projects already on Rust nightly, running on Linux, macOS, or x86_64 Windows
- Codebases that avoid heavy std::arch SIMD intrinsics and unwinding-based panic handling (or already build with -Cpanic=abort)
- Willing to opt in per-profile via Cargo.toml/.cargo/config.toml so only the debug profile uses cg_clif
- Crates that hit an unsupported feature can fall back to the default LLVM backend without any code change

**Skip it when:**
- Release/optimized builds -- cg_clif is not a target here and produces slower-running code than LLVM -O
- Code leaning on std::arch SIMD intrinsics beyond the partially-supported subset (std::simd portable SIMD does work fully)
- Programs that unwind on panic when targeting Windows or macOS -- unwinding support there is experimental and unsupported
- Crates with 'pathological' codegen shapes -- the Nov 2024 report notes a few secondary benchmarks still regress vs cg_llvm
- Anyone who needs stable (non-nightly) Rust, since it's only distributed for nightly via rustup

**Integration:** compiler backend, distributed as a rustup component and loaded via -Zcodegen-backend · none for the user; Cranelift is pulled in by the backend itself · Rust nightly (requires the unstable -Zcodegen-backend / codegen-backend cargo feature) · Linux x86-64/AArch64/RISC-V/s390x, macOS x86-64/AArch64, Windows x86-64 (fully tested per README matrix); FreeBSD and some Linux targets are unverified

**Vs siblings:** The catalogued siblings (zapcc, MIR/c2m, TinyCC) all target C/C++ toolchains; cg_clif is the only Rust-ecosystem entry here, so it's the pick whenever the baseline being replaced is rustc/cargo rather than gcc/clang.

**Gotchas:**
- -Cpanic=abort is enabled by default because stack unwinding is experimental and unsupported on Windows/macOS
- std::arch SIMD intrinsics are only partially supported; std::simd portable SIMD is fully supported
- 2020 measurements (issue #878) showed clean-incremental builds up to ~200% slower because compiled object files were not cached in the incremental cache (#760); the Nov 2024 report does not say whether this was fixed
- JIT mode requires all dependencies to be available as dynamic libraries and lacks incremental compilation, so it can be slower than normal AOT builds

**Status:** Actively maintained (commit as of 2026-09-23) and distributed as an official nightly-only rustup component, but still labeled experimental overall; MIT/Apache-2.0 dual-licensed and adopted by adding a build flag rather than vendoring a library.

[repo](https://github.com/rust-lang/rustc_codegen_cranelift) · [benchmark](https://bjorn3.github.io/2024/11/14/progress-report-nov-2024.html)

#### formatters-linters-lsps

##### Biome  `Rust`  `Apache-2.0`  `active`  `Tier C`

Rust toolchain combining a formatter (97% Prettier-compatible) and linter (500+ rules) that replace ESLint and Prettier/dprint.

**Beats:** ESLint (linting); Prettier and dprint (formatting) — The only public numbers are Nov 2022 hyperfine runs on a MacBook Pro 13-inch M1 (2020) comparing Biome's Rome-era predecessor against Prettier, parallel-prettier/xargs -P prettier, and dprint for formatting (~25x, ~20x, ~20x, and 1.5-2x faster respectively, single-threaded ~7x), and against ESLint for linting (~15x faster, rules both tools support, no type-aware rules, single-threaded ~4x), plus a separate M1 Max 10-core run cited for a '100x faster than Prettier' figure. No compiler flags, tool versions, or raw output are given, and the benchmark/ directory that produced these numbers was deleted from main in commit 8e4ada5 (2026-05-13).

**How:** It's compiled Rust, avoiding Node.js/V8 startup and interpreter overhead. Formatting and linting run against one shared lossless CST (biome_rowan, a rowan-style Green/Red tree that preserves full trivia) instead of each tool doing its own parse. Biome's own benchmark notes say the linter batches rule matching against one semantic model and control-flow graph rather than running each rule as an independent AST visitor, and the CLI parallelizes file processing across threads (tunable via the BIOME_THREADS env var). The scanner also skips filesystem traversal into folders irrelevant to the current run when project-wide type rules are disabled.

**Use it when:**
- You already run Prettier (or dprint) + ESLint on JS/TS/JSON/CSS/GraphQL and want one faster CLI/LSP, bootstrapped from existing configs via `biome migrate`.
- Editor-in-the-loop formatting/linting on medium-large monorepos where ESLint's per-keystroke latency is the pain point — Biome's LSP targets interactive use.
- CI wants a fast cold full-repo check across JS/TS/CSS/GraphQL without needing type-aware rules.
- You want a self-contained native binary with no Node.js dependency for the CLI itself (the npm package just wraps a platform binary).
- You want broad out-of-the-box rule coverage (500+ rules pulled from ESLint/typescript-eslint/jsx-a11y/unicorn) without assembling an ESLint plugin stack.

**Skip it when:**
- You depend on ESLint plugins or custom rules with no Biome equivalent — `biome migrate eslint` only maps recognized rules (eslint, typescript, jsx-a11y, unicorn, jest), not arbitrary plugins.
- You need full type-aware lint parity with typescript-eslint: Biome's type-aware 'project domain' rules (noFloatingPromises, noUnresolvedImports, noImportCycles) are new in v2, opt-in, and docs cite performance dropping from ~800ms to ~2s per 2,000 files when enabled.
- You rely on incremental/cached formatting for large repos with few changed files — Biome has no incremental formatting like Prettier/dprint; every run is a cold run.
- You want to cite the headline speedup numbers as current: the published ~25x/~15x figures are Nov 2022 Rome-era hyperfine runs, never re-measured, and the benchmark/ code that produced them was deleted from main in May 2026.
- Your codebase has deeply parenthesized object expressions in arrow functions (`() => ({...})`) — a real regression made formatting 'dramatically slower' on that shape between 2.5.10 and 2.5.11 (GH #11747), a sign perf isn't uniformly stable release-to-release.

**Integration:** crate (Rust workspace of 100+ biome_* crates), distributed as a prebuilt native CLI binary via the @biomejs/biome npm package · none to run (self-contained native binary; npm install only adds one platform-specific optionalDependency binary, no JS deps). Building from source needs the Rust toolchain. · Rust edition 2024 (~1.85+) to build from source; via npm, Node.js >=14.21.3 is only the install mechanism, not required to run the binary · linux-x64/arm64 (glibc + musl), darwin-x64/arm64, win32-x64/arm64 (per npm optionalDependencies); also compiles to WASM for the online playground

**Vs siblings:** Pick Biome over Oxlint when you need one tool for both formatting and linting plus LSP/editor support and a Prettier-config migrator; Oxlint's README claims ~2x faster linting than Biome and 50-100x vs ESLint but is lint-only with no formatter. Ruff is the closest analog outside JS (Rust linter+formatter replacing Flake8+Black) if you're evaluating the pattern rather than a JS-specific tool.

**Gotchas:**
- Type-aware lint rules (project domain: noFloatingPromises, noUnresolvedImports, noImportCycles) are opt-in and materially slower — docs cite ~800ms to ~2s per 2,000 files when enabled, plus higher memory use.
- No incremental/cached formatting: every `biome format`/`check` run reformats cold, unlike Prettier/dprint — confirmed in Biome's own benchmark notes.
- Formatter hit a real perf cliff on large parenthesized object expressions in arrow functions, reported as 'dramatically slower' between 2.5.10 and 2.5.13 (GH #11747).
- Dual-licensed MIT OR Apache-2.0 per Cargo.toml/package.json, though GitHub's repo-level license detection reports just Apache-2.0.

**Status:** Actively maintained (pushed 2026-09-24, 25.9k stars, not archived); dual MIT/Apache-2.0, published as compiled binaries for every major OS/arch, so it's safe to adopt for day-to-day formatting/linting today — just don't cite the 2022 speedup numbers as current without re-benchmarking.

[repo](https://github.com/biomejs/biome) · [benchmark](https://github.com/biomejs/biome/blob/fdf8555f57dbb763f5dfcbe27be89814b2d0df0c/benchmark/README.md)

##### clangd-tidy  `Python`  `MIT`  `active`  `Tier C`

CLI wrapper around clangd that reports clang-tidy diagnostics much faster than standalone clang-tidy.

**Beats:** clang-tidy — The README's 'Comparison with clang-tidy' section states clangd-tidy is 'significantly faster than clang-tidy (over 10x in my experience)' when running the same checks over a codebase, because clangd only builds an AST from included headers where clang-tidy checks all headers. No benchmark script, target codebase, compiler flags, or hardware are given — it's the author's stated personal experience, not a reproducible measurement.

**How:** Standalone clang-tidy parses and checks the full AST of every included header for every translation unit, even though it suppresses warnings from headers by default. clangd instead builds and caches an AST scoped to what a file actually needs, the same incremental analysis it uses for live editor diagnostics, so clangd-tidy inherits that lighter-weight AST construction instead of clang-tidy's from-scratch per-file header checking. No other technique (caching, parallel dispatch beyond clangd's own worker pool, etc.) is described in the README or source.

**Use it when:**
- Running clang-tidy-style checks in CI on a C/C++ codebase where wall-clock time matters
- You already have clangd installed/configured and a working compile_commands.json
- You want per-file grouped diagnostics instead of clang-tidy's duplicated per-header warnings
- You want incremental linting of only changed lines via clangd-tidy-diff (e.g. gradual rollout of checks on a legacy codebase)
- You also want code-formatting checks (clang-format) folded into the same CI step (-f/--format)

**Skip it when:**
- You need --fix / automatic fixups; clangd-tidy has no fix-application support, only editor code actions
- You rely on clang-tidy checks that clangd's TidyProvider doesn't support; those are silently dropped, not reported as skipped
- Exact diagnostic parity with clang-tidy matters (there are open, acknowledged behavioral discrepancies, e.g. issues #7, #15, #16)
- You can't install/configure clangd in your CI image, or don't have a compile_commands.json
- You want a large, heavily-used, battle-tested tool; this is a small single-maintainer project (161 stars)

**Integration:** source-drop · clangd (external binary); Python 3.8+; attrs, cattrs, typing-extensions (auto-installed via pip); tqdm optional for progress bar · Python 3.8+; a clangd binary (version affects available .clangd diagnostics config, e.g. UnusedIncludes needs clangd-14+, MissingIncludes needs clangd-17+) · POSIX (per PyPI classifiers: Operating System :: POSIX); no Windows classifier listed

**Vs siblings:** Not directly comparable to the other sibling entries (Biome, Oxlint, Pyrefly, ty, Ruff), which target JS/TS or Python; clangd-tidy is the only C/C++ formatter-linter-LSP entry in this category so far, so 'no siblings catalogued yet' for its actual competitor set (clang-tidy variants).

**Gotchas:**
- Silently disables clang-tidy checks unsupported by clangd's TidyProvider (listed in LLVM's TidyProvider.cpp) rather than erroring or warning
- No --fix option; the README suggests using editor code actions instead since the tool targets CI, not local fix workflows
- Known behavioral discrepancies vs clang-tidy are tracked as open issues (#7, #15, #16), not resolved
- Default -j (clangd async workers) is 1, so out-of-the-box throughput depends on tuning -j for parallelism

**Status:** Actively maintained (last commit 2026-02-09) and MIT-licensed, but a small, single-maintainer project (161 stars) — usability tagged 'copyable' rather than a heavyweight dependency.

[repo](https://github.com/lljbash/clangd-tidy) · [benchmark](https://github.com/lljbash/clangd-tidy#comparison-with-clang-tidy)

##### Ruff  `Rust`  `MIT`  `active`  `Tier C`

Rust linter and formatter replacing Flake8, Black, isort, pyupgrade, and more with one fast CLI.

**Beats:** Flake8 (linting); Black (formatting); also compared to pycodestyle, pyflakes, pylint — CONTRIBUTING.md's reproducible hyperfine benchmark (Ruff release build vs. the CPython 3.10 tree, pinned tool versions, Python 3.11) shows Ruff at 294ms cold vs Flake8 12.26s (41.66x), pyflakes 15.79s (53.64x), pycodestyle 46.92s (159.43x), and autoflake 6.18s (20.98x) — but states no CPU model. The larger headline figures (~150x vs Flake8, ~60ms incremental re-lint) come from the founder's 2022 blog post on unspecified macOS hardware, not this repo benchmark; the Black formatting-speed claim appears only in the README, with no benchmark numbers given anywhere.

**How:** Written in Rust and shipped as a single native binary, it avoids the per-file Python interpreter and plugin-subprocess overhead that Flake8's plugin architecture incurs; rules are natively re-implemented in Rust rather than shelled out to separate Python checkers. It also has built-in result caching so unchanged files are skipped on incremental runs. CONTRIBUTING.md's own benchmark shows most of the incremental win comes from that cache: a cold lint of CPython takes ~294ms, a cached rerun ~48ms.

**Use it when:**
- Python 3 codebase already on Flake8 with few/no exotic plugins, run alongside a formatter
- Want one tool for both linting and Black-style formatting instead of two separate ones
- Large codebases or monorepos where whole-repo lint/format time matters in CI or pre-commit
- Need editor/LSP integration (VS Code and others via ruff_server) with fast on-save checks
- Want built-in autofix for import sorting, unused imports, and pyupgrade-style modernization in one pass

**Skip it when:**
- Team depends on specific Flake8 plugins Ruff hasn't re-implemented natively
- Need output byte-identical to Black on code that wasn't already Black-formatted (FAQ notes more deviation there)
- Need full Pylint parity; coverage is partial and some Pylint-style rule requests are still open
- Using `--extend-per-file-ignores` together with leading recursive glob patterns — open issue reports an extreme performance penalty (#8626)
- Autofixes for PERF401/PERF403 rules have open bug reports of making code slower in some cases (#21890, #21891) — review fixes before accepting

**Integration:** CLI binary (installed via pip/pipx/uv/cargo); source is a Rust crate workspace (crates/*) · none for the prebuilt binary (self-contained, no Python runtime required to run it) · Rust 1.96 (edition 2024) to build from source; prebuilt wheels declare Python >=3.7 as the package requirement · PyPI classifier lists 'OS Independent'; wheels are published for common platforms but no explicit CPU-architecture list was found this session

**Vs siblings:** No catalogued sibling targets Python lint/format specifically: Biome and Oxlint are the JS/TS equivalents (ESLint/Prettier), Pyrefly and ty are Python type-checkers (a different job than linting/formatting), and clangd-tidy is the C/C++ equivalent. Pick Ruff whenever the baseline being replaced is Flake8, Black, isort, or pylint on a Python codebase.

**Gotchas:**
- Formatting non-Black-formatted code produces more diffs than the near-100% match figure implies (FAQ)
- `--extend-per-file-ignores` combined with leading recursive glob patterns triggers an 'extreme performance penalty' (issue #8626, open)
- PERF401/PERF403 autofix suggestions have open bug reports of producing slower code in some cases (#21890, #21891)
- Ruff's linter and Black/ruff-format treat line-length enforcement differently, so E501 can still fire even with the formatter enabled

**Status:** Actively maintained (last commit 2026-09-24, 49,764 stars, MIT license); copyable either as a pip-installed prebuilt binary or as a vendorable Rust crate workspace, so there's little build/toolchain risk for adopters.

[repo](https://github.com/astral-sh/ruff) · [benchmark](https://notes.crmarsh.com/python-tooling-could-be-much-much-faster)

#### linkers

##### zld  `C++`  `MIT`  `abandoned`  `Tier C`

Drop-in fork of Apple's ld64 that speeds up incremental Xcode debug linking; archived, maintainer now recommends lld instead.

**Beats:** Apple ld (ld64) — First-party misc/benchmarks.md (with the full captured ld command lines) shows zld beating stock Apple ld64 on three real Xcode/Mach-O debug links on a 'high-end Mac desktop': Signal's iOS app binary 390ms->250ms (~1.6x), Firefox macOS's XUL framework 5.2s->2.20s (~2.4x), and Firefox iOS's Storage.framework 495ms->340ms (~1.5x), with similar percentage gains reported on a 2014 MacBook Pro. No specific CPU model, run count, or variance is given, and the exact Xcode/clang version used for the benchmark itself isn't stated (the captured ld invocations reference clang 11.0.0 and 9.0.1 runtime libs).

**How:** Replaces ld64's STL hash maps/sets with Abseil's Swiss Tables (open-addressing, SIMD-probed hash containers) for the linker's internal symbol/string tables. Parallelizes stages that ld64 runs serially, including library parsing, output-file writing, and sorting. Also caches and speeds up string hashing (hash caching plus a faster hash function) and persists some object/library-name metadata under /tmp/zld-... between runs to warm later links.

**Use it when:**
- Xcode, Bazel, or Cargo debug builds on macOS/iOS where a single ld64 link already takes >=500ms and faster edit-build-run loops matter
- Projects that must stay on Apple's own ld64 codebase for behavioral/stability reasons rather than switching linker families entirely
- Debug-only linking (not release, not App Store archive builds) where a small correctness/regression risk is acceptable
- Teams that can pin to a matching Xcode/ld64 vintage (repo's last activity is 2023, roughly Xcode 13-14 era) and won't chase newer toolchains
- x86_64 or arm64 Xcode debug targets where the arm64_32/Mac Catalyst fallback gap (see gotchas) doesn't apply

**Skip it when:**
- Any release, App Store, or otherwise correctness-critical build -- the README states it is untested/unintended for that
- Newer Xcode/ld64 versions past 2023: repo is archived (last commit 2023-02-15), so toolchain drift bugs like the Xcode 14 undefined `_objc_msgSend$...` selector-stub issue (#113, #125) won't be fixed
- Apple Silicon (M1) hosts, where users reported SIGKILL crashes and codesigning issues with certain Rust/Cargo link setups (#110, referencing #85)
- arm64_32 or Mac Catalyst link targets: zld knows it has issues there and silently falls back to the real ld unless you also pass `-zld_original_ld_path`
- New projects generally: the maintainer's own 2022 RFC (#112) says lld is faster and more reproducible and is what they'd pick today; the README's top line now tells readers to use lld instead

**Integration:** source-drop · cmake (build-time); vendors Abseil (for Swiss Tables) and Apple's ld64/corecrypto sources in-tree; requires the full Xcode.app (not just Command Line Tools) to build and run · macOS with a full Xcode install; built via `make`/cmake; benchmark and issue history point to an Xcode 13-14 / clang 11.0.0 / ld64 vintage, unmaintained since 2023-02-15 · macOS hosts only (Intel and Apple Silicon), producing Mach-O output for macOS/iOS/watchOS/tvOS targets; not applicable to Linux/Windows/GNU/MSVC toolchains

**Vs siblings:** mold and Wild are ELF/Linux linkers competing with lld; neither links Mach-O/Xcode debug builds, so they aren't substitutes for zld's use case. Pick zld over them only when the job is specifically Xcode/Bazel/Cargo debug-linking on macOS/iOS -- and even then, the maintainer's own RFC and the archived README both point to lld as the better current choice for that same job.

**Gotchas:**
- Without also passing -Wl,-zld_original_ld_path,<real ld>, zld silently falls back to Apple's stock linker for cases it knows are broken (arm64_32, Mac Catalyst) with no warning
- Needs the full Xcode.app installed, not just Xcode Command Line Tools, or builds/runs fail (#106, #109)
- Caches metadata under /tmp/zld-...; README says to run a link twice before judging speedup because the first run pays cold-cache cost
- Reported SIGKILL/codesigning crashes on Apple Silicon with some Rust+Cargo configurations (#110, #85), and an Xcode 14 undefined-symbol bug with ObjC selector stubs (#113, #125)

**Status:** Archived since 2023-02-15 (MIT license, 1,191 stars); the README's own top line now says to use lld instead, echoing the maintainer's 2022 'Future of zld' RFC (#112) that lld is faster, more reproducible, and what they'd choose for a new project today.

[repo](https://github.com/michaeleisel/zld) · [benchmark](https://github.com/michaeleisel/zld/blob/master/misc/benchmarks.md)

#### preprocessors-and-codegen

##### FlatBuffers  `C++`  `Apache-2.0`  `active`  `Tier C`

Zero-copy binary serialization with schema-generated accessors; reads fields in place without unpacking, unlike protoc.

**Beats:** protoc — FlatBuffers's own C++ benchmark page (docs/source/benchmarks.md) reports, per 1M iterations on a ~10-object struct (array, 4 strings, mixed int/float scalars): Decode+Traverse+Dealloc 0.08s (FlatBuffers binary) vs 302s (Protocol Buffers LITE C++ runtime from protoc), ~3775x, and Encode 3.2s vs 185s, ~58x. Run on 'Windows 7 64bit' with no compiler, flags, or CPU model stated.

**How:** Tables are encoded as offset-linked vtables and structs as fixed, aligned inline scalar layouts, so field access is pointer arithmetic through the received buffer rather than a parse pass — no intermediate object graph is allocated on decode (0 bytes/blocks reported vs Protobuf LITE's 760B/20 blocks in the project's own benchmark). `FlatBufferBuilder` constructs buffers back-to-front to avoid backpatching offsets during encode. There's an optional slower object API (`--gen-object-api`) that unpacks into STL containers, but the default zero-copy path is what produces the measured speedup.

**Use it when:**
- Game engines or real-time systems reading many small/medium structured messages per frame (scene data, network packets) where allocation-free decode matters
- Read-many, build-once workloads: mmap'd assets, IPC payloads, or config blobs accessed repeatedly after being written once
- Cross-language data exchange needing schema-driven forward/backward field compatibility without adopting full gRPC/protobuf tooling
- Memory-constrained platforms (mobile, embedded) where avoiding a fully parsed object graph saves RAM
- You control both producer and consumer and can regenerate code from `.fbs` schemas as part of your build

**Skip it when:**
- Data arrives from an untrusted source and you don't run flatbuffers::Verifier first — direct field access does no bounds checking on malformed offsets
- You need protobuf's broader ecosystem (gRPC-first tooling, dynamic/reflective message manipulation, established schema registries) with minimal migration cost
- Wire size is the priority over decode speed: FlatBuffers's own benchmark shows its binary format larger than Protobuf's for the same object (344B vs 228B)
- You need a fully mutable object graph by default — that requires the object API, which unpacks the tree and gives up most of the zero-copy advantage
- Team is unfamiliar with offset/vtable-based wire formats and wants protobuf's simpler 'parse into a plain object' mental model

**Integration:** header-only · none for the core C++ runtime (all headers under include/flatbuffers); optional grpc.h integration needs gRPC if used · C++11 (README: works on 'any [platform] with a recent C++ compiler (C++ 11 and newer)'); CMake exposes an optional C++17 test target, not a runtime requirement · Windows, macOS, Linux, Android per README, plus 'any others with a recent C++ compiler'; no architecture-specific (SIMD/AVX) requirement found in headers

**Vs siblings:** Pick FlatBuffers over RapidProto, Zserio, or vtprotobuf when you want true zero-copy field access with no unpack step at all — those alternatives still build or touch a parsed object on decode, just cheaper than stock protoc. Pick one of them instead if you must stay on the actual Protobuf wire format/schema/gRPC ecosystem while cutting decode cost.

**Gotchas:**
- Direct field access skips validation; run flatbuffers::Verifier (include/flatbuffers/verifier.h) before trusting a buffer from an untrusted source, or bad offsets can read out of bounds
- Accessors return pointers into the original buffer, not owned copies — the backing buffer must outlive every object/string pointer you keep
- The convenient, fully mutable object API (--gen-object-api) unpacks the whole tree into STL containers, forfeiting most of the zero-copy speed this entry is cataloged for
- The wire format carries no self-describing type tag/version — a reader must already know the schema (or use the separate reflection API) to interpret a buffer

**Status:** Actively maintained (last commit 2026-09-14, 26.5k stars, used at Google, Unity, Facebook, and many game engines), Apache-2.0 and copyable; but the specific protobuf-comparison benchmark code lived in a now-deleted `benchmarks` git branch and isn't reproducible today, so the >3000x decode figure should be read skeptically (likely an unoptimized/debug protobuf build) even though the library's own speed reputation is well established elsewhere.

[repo](https://github.com/google/flatbuffers) · [benchmark](https://github.com/google/flatbuffers/blob/master/docs/source/benchmarks.md)

##### RapidProto  `C++`  `Apache-2.0`  `active`  `Tier C`

Header-only codegen protobuf decoder for C++: arena and streaming models beating protoc's Arena decode and protozero.

**Beats:** protoc — On the project's own in-repo harness (tests/bench.py), decoding a 2000-record mixed Dataset (strings, nested/repeated messages, packed scalars) serialized by protoc, the arena decoder ran ~7x protoc+google::protobuf::Arena's throughput at 0.49x its peak payload memory on g++-13 (~6x on clang++-20), and the streaming decoder ran ~12x protoc+Arena and ~1.8x protozero; on protobuf's own google_message1/2 corpora and a 20MB OSM PBF extract the arena/streaming decoders beat protoc's protobuf-layer throughput by roughly 28-155% depending on payload shape. All figures use protobuf 4.25.3, -O3 -DNDEBUG; no CPU model is documented, only 'a quiesced box' with SMT/turbo off and core pinning.

**How:** Per docs/optimizations.md, the gains stack from compile-time specialization: borrowed string_view fields instead of copies, packed-array pre-sizing (a bulk memcpy for fixed-width packed fields, a length-bounded allocation for varint arrays), forced full inlining of the wire-read call tree (RP_FLATTEN), a fused single-bounds-check tag read, SWAR (SIMD-within-a-register) 64-bit varint kernels that decode multiple bytes' continuation bits per branch instead of one byte at a time, a one-byte dispatch hub for low field numbers, and field-order threading that jumps straight to the next expected field's label when fields arrive in ascending wire order (protoc's own emission order). Together these moved the arena decoder from 2.4x protoc to 6-7x protoc on the project's mixed Dataset benchmark.

**Use it when:**
- Hot decode path for schemas you can regenerate ahead of time via codegen (not reflection-based), where protoc+Arena decode throughput or peak memory is the bottleneck
- Read-mostly consumption of a message tree needing random/repeated accessor access (arena model), e.g. a mixed record with strings, nested/repeated messages, packed scalars
- Extracting a handful of fields or forwarding data without materializing objects (streaming model) — zero allocation, faster than protozero on most shapes
- Input strings/bytes can be safely borrowed as views into a buffer you keep alive (or you accept the cost of decode_owned for a self-contained handle)
- Linux/macOS/Windows C++17 projects on GCC/Clang/AppleClang/MSVC that can add a header-only generated decoder without a new link dependency

**Skip it when:**
- You need to serialize, mutate, or produce protobuf messages — RapidProto is decode-only; keep protoc for the write path
- You need real closed-enum semantics or strict proto3 string UTF-8 validation — RapidProto decodes all enums open and does not validate UTF-8 (part of where its speed margin over protoc comes from)
- You rely on protobuf's normal merge behavior for a repeated singular sub-message on the wire — the arena decoder rejects the buffer (RepeatedSingularMessage) instead of merging it
- You decode large packed scalar arrays mainly through the streaming model — it is slower than protozero there since a callback can't batch a bulk store; use the arena model for that shape
- The project is 3 stars, about three months old (created 2026-06-28), with first-party-only benchmarks that don't state a CPU model — weigh that immaturity against protoc for anything load-bearing today

**Integration:** header-only · none (generated headers are self-contained; rapidprotoc itself needs only a C++17 toolchain to build, or use a prebuilt release binary) · C++17; GCC, Clang (incl. AppleClang), or MSVC — CI/benchmarks use g++-13 and clang++-20 · Linux, macOS, Windows (all three CI-covered); no documented CPU-architecture requirement (SWAR only, no SIMD intrinsics)

**Vs siblings:** Pick RapidProto over Zserio or vtprotobuf when you're staying on the .proto/protoc ecosystem but want a much larger raw C++ decode throughput and memory win than Zserio's ~1.17-1.2x over protoc, and can accept a narrower, decode-only, C++-only tool (vtprotobuf targets Go). Pick FlatBuffers instead when you can drop the protobuf wire format entirely for true zero-copy access with no decode step at all.

**Gotchas:**
- Arena tree strings/bytes/raw payloads are borrowed views into the input buffer: the tree is valid only while both the Arena and the input outlive it, unless you use decode_owned
- A duplicate singular sub-message field on the wire is rejected outright (ArenaDecodeError::RepeatedSingularMessage), not merged the way protoc merges two concatenated messages
- Enums always decode open, even proto2/editions-CLOSED enums — an unrecognized value arrives as a raw integer instead of routing to unknown fields
- Recursion-depth guards against pathological nesting are sized for an 8MB stack; Windows defaults to a 1MB stack, so untrusted deeply-nested input needs a larger linked stack (/STACK:8388608) to stay safely rejecting

**Status:** Active (last commit 2026-09-14) and Apache-2.0-licensed, but a brand-new, 3-star project (created 2026-06-28) with no independent benchmark or adoption track record yet; it is copyable/vendorable since the consumer-facing output is generated header-only code, but treat the maturity as early.

[repo](https://github.com/VeaaC/rapidproto) · [benchmark](https://github.com/VeaaC/rapidproto/blob/main/docs/benchmarks.md)

##### vtprotobuf (protoc-gen-go-vtproto)  `Go`  `BSD-3-Clause`  `active`  `Tier C`

protoc plugin generating reflection-free Marshal/Unmarshal/Size/Equal/Clone helpers for Go protobuf APIv2; ~1.7x faster unmarshal than stock protoc-gen-go.

**Beats:** protoc — Per the author's 2021 Vitess blog post (Vicent Marti), a synthetic VReplication stress test replicating a large MySQL table between keyspaces measured 7.17 CPU-seconds of unmarshal overhead with stock protoc-gen-go (APIv2) vs 4.15 CPU-seconds with vtprotobuf's UnmarshalVT (~1.7x), falling to 0.63 CPU-seconds (~11x) when vtprotobuf's generated memory pooling is also used; the post gives no hardware, Go version, or compiler flags, and the repo ships no benchmark code to reproduce the numbers.

**How:** All (de)serialization logic is fully unrolled per-field at codegen time (ported from gogo/protobuf's approach to the APIv2 API), so there is no reflection walk over the message descriptor at runtime. SizeVT precomputes the exact encoded size so MarshalVT allocates its output buffer once. UnmarshalVTUnsafe casts wire bytes directly into string/[]byte fields instead of copying them. The optional generated sync.Pool-backed object pools (ResetVT/ReturnToVTPool/FromVTPool) let callers reuse whole message structs across unmarshal calls, avoiding allocation entirely, which is where most of the reported speedup comes from.

**Use it when:**
- Go services already on google.golang.org/protobuf (APIv2) with (de)serialization visible as CPU cost in profiles (RPC hot paths, replication/streaming row processing).
- gRPC, DRPC, or Twirp services that can install vtprotobuf's provided codec so all messages benefit without touching call sites.
- Teams that can explicitly opt into memory pooling per message type and manage single-owner reuse lifetime carefully, where most of the >10x gain reported by the author lives.
- Want reflection-free CloneVT/EqualVT/SizeVT even without wiring the whole RPC path.
- Comfortable checking in generated *_vtproto.pb.go files as part of the normal protoc build step.

**Skip it when:**
- Still generating APIv1/gogo code: vtprotobuf targets APIv2 only and is explicitly not compatible with APIv1-generated code per the README.
- Can't tolerate unsafe byte aliasing: UnmarshalVTUnsafe pins the entire input buffer alive via GC for the life of any string/bytes field taken from the message (open issue #167), which can silently balloon retained memory if a field is cached long-term.
- Messages are small or short-lived: the author's own post notes many protobuf messages are too small for pooling to help, and the ~1.7x codegen-only gain (no pooling) is the realistic floor.
- Need pooling correctness for repeated fields, maps, or nested messages: multiple open issues report pooled ResetVT/ReturnToVTPool bugs with repeated fields (#92) and note pooling only reaches the outer message, not nested children (#162, 'Recursive Pool Usage').
- Want a single drop-in replacement for proto.Marshal/Unmarshal with zero call-site changes and no RPC codec registration step.

**Integration:** source-drop · google.golang.org/protobuf (APIv2) required; optional integration deps on google.golang.org/grpc, storj.io/drpc, or github.com/twitchtv/twirp for the provided codecs · go.mod pins `go 1.26.4` to build the plugin/runtime as of the last commit; the `unique` string-interning field option additionally needs Go 1.23+ in consumer code · any (pure Go, no architecture-specific code in the repo tree)

**Vs siblings:** The catalogued siblings (RapidProto, Zserio, FlatBuffers) are all C++ alternatives to protoc's C++ output; pick vtprotobuf instead whenever the stack is Go on google.golang.org/protobuf APIv2, since it optimizes protoc's existing Go codegen and wire format rather than replacing either.

**Gotchas:**
- UnmarshalVTUnsafe keeps the whole input wire buffer alive via GC for as long as any string/bytes field from the message is reachable (unsafe.String aliasing); documented as an open gap in issue #167, not yet in the README.
- UnmarshalVT on a non-zeroed message behaves like proto.Merge rather than a fresh Unmarshal; call Reset() first or use a freshly allocated message.
- Memory pooling is opt-in per message (`option (vtproto.mempool)` or `--go-vtproto_opt=pool=...`) and, as of issue #162, only pools the outer message — nested/child messages are still freshly allocated on each unmarshal.
- Returning a pooled repeated-field message has open correctness bugs (issue #92, generated ResetVT); verify pool behavior with your own message shapes before relying on it in production.

**Status:** Actively maintained (last commit 2026-07-02, 1118 stars, used in production by Vitess/PlanetScale and widely adopted in the Go gRPC ecosystem); BSD-3-Clause and small enough to vendor, but 'copyable' here means installing the plugin and wiring it into your protoc invocation, not literally copying a header.

[repo](https://github.com/planetscale/vtprotobuf) · [benchmark](https://vitess.io/blog/2021-06-03-a-new-protobuf-generator-for-go/)

##### Zserio  `C++`  `BSD-3-Clause`  `active`  `Tier C`

Own-IDL C++/Java/Python serialization framework; bit-packed decode 1.2x-2.6x faster than protoc.

**Beats:** protoc — Per-decode time (protobuf ParseFromString vs zserio read, pre-serialized blob, JSON load/serialize untimed) on 4 schemas, gcc 11.3.0 CMake-Release build, Intel i7-9850H/Linux Mint 21.1: Zserio beat protoc-generated C++ by 1.17x-2.63x (addressbook 1.478 vs 1.731ms, apollo 0.244 vs 0.641ms, carsales 1.374 vs 2.053ms, simpletrace 0.221 vs 0.386ms); byte-aligned variants reached 2.05x and 2.22x. Benchmark is first-party (same org as Zserio, 6-star companion repo), evidence tier C.

**How:** Zserio packs fields at the bit level rather than byte level, and its default schemas carry no per-field tag IDs or explicit length prefixes the way protobuf's wire format does, so there is less to scan per field during decode. Byte-aligning fields (the '_align' schema variants) trades blob size for speed by removing bit-shift work, cutting decode time roughly another 40-45% versus the default schema on addressbook and carsales in this benchmark. No SIMD or algorithmic trick is documented; the win is wire-format layout, not a decode algorithm.

**Use it when:**
- Designing a new wire format from scratch where blob size matters as much as decode speed
- Multi-language C++/Java/Python project willing to author .zs schemas instead of .proto
- Need built-in SQLite table serialization, JSON debug export, or generic reflection/services without hand-rolling them
- Functional-safety-conscious C++ codebase: C++11 runtime, >600 unit tests, ASan/UBSan clean, 99% line coverage
- Deserialize-heavy workloads (parse once, read many) where a 1.2x-2.6x per-decode win compounds

**Skip it when:**
- Already invested in protobuf schemas, tooling, or cross-org interop; migration cost likely exceeds the modest measured speedup
- Need protobuf-style forward/backward field compatibility; Zserio's compactness comes partly from dropping field IDs and lengths
- Team can't add a Java-based external compiler step (zserio.jar) to the build
- Need platforms beyond 64/32-bit Linux and 64-bit Windows; macOS/ARM are not in the stated Supported Platforms list
- Want a larger, independently verified speedup: siblings RapidProto (~7x) and vtprotobuf (~1.7x) show bigger measured wins over protoc

**Integration:** source-drop · none for the C++ runtime itself; bundled SQLite3 only if using the SQL-database extension; Java (JRE) needed at build time to run the zserio.jar code generator, not at runtime · C++11; gcc 7.5.0+ (11.4.0/7.5.0 tested), clang 11.0.0+ (14.0.6/21.1.8 tested), MinGW 7.5.0+, MSVC 2017+; CMake 3.15+ if using the bundled CMake helper · 64-bit Linux, 32-bit Linux, 64-bit Windows per README's Supported Platforms list; macOS/ARM not stated

**Vs siblings:** Pick Zserio when you want a full schema framework (SQLite mapping, JSON debug strings, services/pub-sub, one schema for C++/Java/Python) and can move off .proto. Pick RapidProto or vtprotobuf instead if you must keep .proto files and want a bigger measured decode speedup with less schema-language lock-in.

**Gotchas:**
- Byte-aligned (_align) and delta-packed (_packed) schema variants trade blob size against decode speed in opposite directions; pick per workload
- Compact wire format omits field tags/lengths, so schema-evolution/compatibility rules differ sharply from protobuf's
- Code generated by the zserio compiler inherits the license of the input .zs schema, separate from the BSD-3-Clause runtime license
- Open issue #577 'Consider to optimize C++ serialization performance' (still open) indicates maintainers see further headroom

**Status:** Active (last commit 2026-09-17, frequent releases); BSD-3-Clause runtime, with generated code separately licensed under the input schema's license.

[repo](https://github.com/ndsev/zserio) · [benchmark](https://github.com/ndsev/zserio-protobuf-benchmarks)

## Copyleft

### numerics-and-science

#### blas-lapack

##### Eigen  `C++`  `MPL-2.0`  `active`  `Tier A`

Header-only C++ template library for dense/sparse linear algebra; beats OpenBLAS at small-to-mid sizes without linking BLAS.

**Beats:** OpenBLAS — On an Intel Xeon Gold 6444Y (GCC 13.3.0, -O3 -DNDEBUG -mavx512dq -mfma, single-threaded), Eigen's own kernels beat OpenBLAS 0.3.26's geometric-mean GFLOP/s on GEMV, DOT, TRSM, POTRF and SYEV across most size bands (roughly 1.1-4.9x), are near parity on large GEMM, and lose on GEEV and GESDD; against Intel oneMKL 2025.3, Eigen is generally slower at large sizes. The harness (Google Benchmark 1.8.3, median of 10 reps) is public but still an unmerged GitLab merge request (!2903), and frequency was not locked during the run.

**How:** Expression templates fuse chained operations into a single loop at compile time, avoiding temporaries. Eigen's own GEMM kernel does three-level cache blocking -- mc x kc panels packed for L2/L3, mr x kc micro-panels kept in L1, and a register-blocked micro-kernel -- the same family of technique GotoBLAS/BLIS use, confirmed in the header comment of GeneralBlockPanelKernel.h. Kernels are explicitly SIMD-vectorized (SSE/AVX/AVX-512/NEON/etc.), and small fixed-size matrices get compile-time loop unrolling that skips packing overhead entirely, which is why Eigen's edge over OpenBLAS is largest at small sizes (DOT 4.9x, GEMV 2.2x at n<=16) and shrinks or reverses as size grows.

**Use it when:**
- Small and medium dense ops (roughly n<=1024) where OpenBLAS's dispatch/call overhead dominates -- GEMV and DOT measured 1.1-4.9x faster than OpenBLAS here
- You want a header-only dependency with no external BLAS/LAPACK to build, package, or version-pin
- Fixed-size or compile-time-sized linear algebra (small transforms, small solvers) where Eigen's unrolled kernels apply
- TRSM, POTRF, SYEV workloads at small/mid size, where Eigen beat OpenBLAS by 1.25-3.6x per this benchmark
- C++ codebases that want expression-template ergonomics instead of raw BLAS call signatures

**Skip it when:**
- Very large dense GEMM/SYRK (n in the 1500+ range) where Eigen is roughly at parity with OpenBLAS and often slower than oneMKL
- GEEV (nonsymmetric eigenvalues) -- measured at 0.45x OpenBLAS at 192-1024, and well behind oneMKL at large sizes
- GESDD (SVD) at mid-to-large sizes -- measured 0.6-0.9x OpenBLAS
- Large-scale multi-threaded numerics -- this benchmark and Eigen's own kernels are single-threaded; OpenMP only parallelizes some ops (dense GEMM, PartialPivLU, a few iterative sparse solvers), not the full LAPACK surface
- Storing fixed-size Eigen objects in STL containers or passing them by value without alignment care -- triggers runtime alignment assertions on SIMD builds

**Integration:** header-only · none (STL only); optional external BLAS/LAPACK backend for large-matrix offload · C++14 (target_compile_features cxx_std_14 in CMakeLists.txt); CMake 3.18+ only needed for the optional install/test build, not for using the headers · x86-64 (SSE2 baseline, AVX/AVX2/AVX-512 optional), aarch64/ARM NEON, PowerPC Altivec/VSX, MIPS MSA; this benchmark ran on AVX-512

**Vs siblings:** no siblings catalogued yet

**Gotchas:**
- Fixed-size vectorizable types (Vector4d, Matrix4d, Quaternionf, etc.) assert at runtime if misaligned -- avoid storing them by value in STL containers or passing by value without EIGEN_MAKE_ALIGNED_OPERATOR_NEW
- OpenMP thread count should match physical cores, not logical/hyperthreads -- oversubscription slows things down since Eigen's kernels already saturate a core
- Heavy expression-template usage increases compile times
- For very large dense problems, Eigen's own docs and this benchmark both point toward linking an external BLAS/LAPACK backend instead of relying solely on Eigen's kernels

**Status:** Actively maintained (last commit 2026-09-23) with a large downstream user base (ROS, TensorFlow, Ceres Solver, OpenCV, Blender); MPL-2.0, header-only, trivial to vendor.

[repo](https://gitlab.com/libeigen/eigen) · [benchmark](https://libeigen.gitlab.io/benchmarks/2026-09-xeon-gold-6444y-blas-lapack-avx512/)

### stdlib-replacements

#### async-tasks-threadpools

##### libfork  `C++`  `MPL-2.0`  `active`  `Tier A`

Header-only C++20/23 coroutine fork-join library beating oneTBB and OpenMP on fine-grained task throughput and memory.

**Beats:** oneTBB (Intel Threading Building Blocks) and OpenMP (libomp) — The arXiv:2402.18480 preprint (Williams & Elliott) benchmarked libfork 3.5.0 against oneTBB 2021.10.0, Clang-bundled OpenMP/libomp, and Taskflow 3.6.0 on fib(42), integration, matmul, nqueens(14), and UTS tree-search, compiled with Clang 18.0.0 at the paper's 'highest optimization setting,' on 2x Intel Xeon Platinum 8480+ (112 cores, 2 NUMA nodes, 500GiB RAM), swept from 1-112 cores. Abstract-stated averages are 2.7x faster / 6.2x less memory than oneTBB and 7.2x faster / 10x less memory than OpenMP; the frequently quoted 7.5x/19x (vs TBB) and 24x/24x (vs OpenMP) figures are peak ratios on the fib benchmark specifically at 112 cores, not typical-case numbers.

**How:** A continuation-stealing work-stealing scheduler lets the worker that forks a task keep running the child immediately while only the continuation is exposed to be stolen, minimizing deque traffic on the common path. Coroutine frames are placed on an (almost) non-allocating 'cactus stack' built from segmented stacks instead of being heap-allocated per task, giving fork/call overhead about 10x a bare function call. NUMA-aware pools (optionally using hwloc for topology detection) reduce cross-socket stealing cost, which the paper credits for near-linear time and memory scaling up to 112 cores.

**Use it when:**
- Very fine-grained recursive divide-and-conquer workloads (fib-style, tree search, numerical integration) where oneTBB/OpenMP per-task overhead dominates runtime
- Codebases willing to rewrite hot-path functions as C++20 coroutines (lf::task<T>) rather than keep existing std::async/TBB/OpenMP call sites unchanged
- Multi-socket/NUMA machines with high core counts (paper benchmarked 1-112 cores, 2 NUMA nodes) where linear time/memory scaling matters
- Workloads where peak RSS is as important as speed - libfork's memory footprint was measured far below TBB/OpenMP/Taskflow on the UTS tree-search benchmark
- Projects that can pin a recent compiler (current main requires C++23 per CMakeLists) via CMake, vcpkg, or Conan

**Skip it when:**
- Any deployment target still on MSVC: BUILDING.md states libfork compiles on MSVC 19.35-19.37 but seg-faults at runtime due to an open Visual Studio symmetric-transfer/coroutine codegen bug
- Coarser-grained parallel loops: a real integration into BLIS's GEMM (issue #113) showed libfork's busy_pool at only 55% of OpenMP's GFLOPS at matrix dim=512, only beating OpenMP once dim >= 2048, partly because libfork lacks a flat bulk-spawn/parallel_invoke API
- Teams unwilling to convert call sites to coroutine-returning lf::task<T> and to handle its exception_before_join + rethrow-on-join exception model
- Older/unpatched compilers: Clang <=16 needs a thread_local workaround with a performance penalty, and GCC below -O2 can stack-overflow because it doesn't guarantee coroutine symmetric-transfer tail calls
- Anyone requiring peer-reviewed evidence: the only performance writeup is an arXiv v1 preprint (Feb 2024) with no journal/conference publication, and its headline 'up to' ratios are peak fib/integrate figures at 112 cores, well above the abstract's stated averages (2.7x/7.2x)

**Integration:** header-only · none required beyond a compiler and Threads; optional hwloc >=2.5.0 for NUMA topology detection (LF_USE_HWLOC) · C++20 per docs (C++23 preferred); current main CMakeLists.txt sets target_compile_features(... cxx_std_23) on the library interface target. Compiler support table: Clang 15-18 (16 and below need a thread_local workaround with a perf penalty due to LLVM bugs #63022/#47179), GCC 11-13 (needs >= -O2 for guaranteed coroutine tail calls), Apple Clang (Xcode-shipped, with the same old-Clang mitigations), MSVC 19.35-19.37 compiles but seg-faults at runtime · Linux, macOS, Windows CI configured (linux.yml/macos.yml/windows.yml), any arch with a conforming C++20/23 coroutine compiler; NUMA-aware scheduling is opt-in via hwloc

**Vs siblings:** Pick libfork over TooManyCooks/dispenso/Taskflow when the workload is extremely fine-grained recursive fork-join (fib-like or UTS-style tree search) run across dozens to 100+ cores and peak memory matters as much as latency; TMC and dispenso report comparable 'beats oneTBB' wins with a simpler non-coroutine API and less compiler sensitivity, so prefer them if you don't want to rewrite call sites as C++20/23 coroutines or can't guarantee a modern compiler.

**Gotchas:**
- Strict fork-join is enforced: every forked/called child must be joined with co_await lf::join before the parent task returns - there is no fire-and-forget
- Exceptions from a child surfaced before the join point arrive as exception_before_join; you must catch it and still call join, which then rethrows the child's real exception (include/libfork/core/exceptions.hpp)
- Current main branch requires C++23 (cxx_std_23 in CMakeLists.txt) even though the README/BUILDING.md prose still advertises 'C++20 coroutines' - check your compiler before adopting HEAD
- MSVC builds compile but crash at runtime (known upstream MSVC coroutine codegen bug); do not ship an MSVC build without testing

**Status:** Actively maintained - default-branch last commit 2026-01-17 - and header-only/copyable under MPL-2.0, so it can be vendored without a package manager, but current HEAD needs a C++23-capable compiler, MSVC support is presently broken at runtime, and the last tagged release (v3.8.0) is from 2024-05-10 with substantial unreleased work since.

[repo](https://github.com/ConorWilliams/libfork) · [benchmark](https://arxiv.org/abs/2402.18480)

#### bitsets-and-succinct

##### pasta::bit_vector  `C++`  `GPL-3.0`  `stale`  `Tier A`

Header-only C++20 rank/select bit vector: 8% faster rank, 16.5% faster select than cs-poppy.

**Beats:** cs-poppy (Zhou, Andersen & Kaminsky, SEA'13 compact rank/select bit-vector structure) — In the SPIRE 2022 paper (arXiv:2206.01149), pasta-flat/pasta-poppy rank is up to 8% faster and pasta-flatSIMD select up to 16.5% faster than cs-poppy (Zhou, Andersen & Kaminsky, SEA'13) at matching ~3.51% space overhead, measured single-core on an AMD Ryzen 9 3950X with GCC 10.2, -O3 -march=native -DNDEBUG. Not compared directly against any C++ stdlib facility, since none offers rank/select.

**How:** Uses a two-level (L1/L2) block metadata layout in the lineage of cs-poppy (Zhou, Andersen & Kaminsky, SEA'13), with 512-bit L2 blocks, tuned to hold the same ~3.51% space overhead while improving cache-friendliness of the 'flat' layout. The select path can locate the target L2 block with x86-64 SIMD intrinsics (FindL2FlatWith::INTRINSICS, compiled under __x86_64__) instead of linear or binary search over block summaries, which is where most of the select speedup comes from.

**Use it when:**
- Need succinct rank/select over a static, uncompressed bit vector (e.g., building an FM-index or other compact text index)
- Already using or evaluating cs-poppy-style compact rank/select structures and want the same space overhead with somewhat faster queries
- Target is x86-64 and can compile with -march=native to get the SIMD-accelerated select path
- Single-threaded/sequential query workload (paper's benchmarks are single-core)
- C++20 codebase where GPL-3.0 header-only vendoring is acceptable

**Skip it when:**
- Need a std::bitset/std::vector<bool>-compatible API — this is a separate type with its own construction and query interface, not a drop-in replacement
- License must be MIT/BSD-permissive — this is GPL-3.0, more restrictive than the sibling libraries in this category
- Rank-only workload where extra memory is acceptable — sdsl-v and rank9select answer rank faster but use 1.75-6.98x more space (per verification notes)
- Stuck on C++17 or earlier, or on a non-x86-64 platform where the SIMD select path is unavailable
- Need an actively maintained dependency — single-author project, last commit 2025-04-07, only 36 stars

**Integration:** header-only · tlx (github.com/tlx/tlx) and pasta-toolbox/utils, both pulled automatically via CMake FetchContent when building tests/benchmarks; no git submodules · C++20; CMake 3.25 to build tests/benchmarks via the provided presets (paper's benchmarks used GCC 10.2) · x86-64 for the SIMD-accelerated select path (FindL2FlatWith::INTRINSICS, gated on __x86_64__); a non-intrinsic linear/binary-search fallback exists for other architectures but is not the configuration benchmarked in the paper

**Vs siblings:** None of the catalogued siblings (CRoaring, plf::bitset, better_bitset, BitLib, sul::dynamic_bitset) implement rank/select at all — they speed up direct std::bitset/std::vector<bool> operations like shifts, iteration, and set algebra. Pick pasta::bit_vector when the workload specifically needs succinct rank/select queries; for plain bit-twiddling workloads without that need, a sibling that benchmarks directly against std is the safer, lower-friction choice.

**Gotchas:**
- Support structures (e.g. FlatRankSelect) are constructed from an existing BitVector instance and query through that wrapper; build the bit vector first, then attach the rank/select structure you need
- Multiple rank/select variants exist (Rank/RankSelect, FlatRank/FlatRankSelect, WideRank/WideRankSelect) with WideRank explicitly meant for vectors up to 2^40 bits; the docs don't give a clear size crossover for picking one over another
- Building tests/benchmarks requires network access at configure time for CMake FetchContent to pull tlx and pasta-toolbox/utils
- The headline select speedup depends on -march=native and x86-64 SIMD intrinsics being enabled; behavior without that flag isn't the benchmarked configuration

**Status:** Maintenance is stale (single-author, last commit 2025-04-07, 36 stars), but it's header-only and small enough to read fully and vendor; GPL-3.0 licensing is the main adoption friction, not code quality.

[repo](https://github.com/pasta-toolbox/bit_vector) · [benchmark](https://arxiv.org/abs/2206.01149)

#### math-simd-linear-algebra

##### VDT (VectoriseD maTh)  `C++`  `LGPL-3.0-or-later`  `stale`  `Tier B`

Header-only Padé-polynomial libm replacements for exp/log/trig/asin-acos-atan/isqrt, auto-vectorizable, 1.3-13x faster scalar.

**Beats:** <cmath> (libm) — The refereed CHEP2013 paper (glibc 2.12 libm vs VDT v0.3.6, GCC 4.8.1, Intel Core i7-4770K) reports scalar double-precision speedups from ~1.3x (isqrt) to ~12.8x (exp), with AVX2+FMA-vectorized log reaching ~22x; the README's separate i7-3930K table shows smaller but consistent scalar gains (Exp 2.7x, Log 2.8x, Tan 3.7x) rising to 4-8x with SSE/AVX. Both sources agree that scalar single-precision expf/logf/isqrtf are slower than libm.

**How:** Each function is a Padé/minimax rational-polynomial approximation adapted from the Cephes math library, evaluated with a small fixed number of multiply-adds instead of libm's argument-reduction-and-table-lookup algorithms. The scalar code uses no intrinsics, so it auto-vectorizes under GCC/Clang/ICC into SSE/AVX/AVX2(+FMA) loops; the array (*_v) signatures make this explicit for the compiler and unlock the larger SIMD gains. Accuracy is deliberately relaxed (~0.1-0.5 average LSB difference from libm per the README's own table) to keep polynomial degree and branching low.

**Use it when:**
- Hot loops calling exp/log/sin/cos/tan/asin/acos/atan/atan2/isqrt millions of times where ~0.1-0.5 ULP error is acceptable, e.g. physics simulation and reconstruction code (VDT originated at CERN and is used in Geant4 and LHC experiment software).
- Code that can call the array (*_v) signatures or already auto-vectorizes, since SIMD gains (SSE/AVX/AVX2+FMA) are consistently larger than scalar gains in both the README table and the cited paper.
- x86-64 builds where you can pick SSE/AVX/AVX2/FMA at CMake configure time, or ARM builds via the NEON CMake option (though NEON is not exercised in the published benchmarks).
- Projects willing to vendor a small LGPL-3 header-only library and either call vdt:: functions directly or use the PRELOAD build to intercept an existing libm-calling binary without recompiling it.

**Skip it when:**
- Need bit-identical results to libm/std math (finance, reproducibility-critical or correctness-critical code) — VDT trades ~0.1-0.5 ULP accuracy for speed on every function.
- Building on Windows: issue #1 (open) reports it isn't compatible (__restrict__ vs __restrict, missing _USE_MATH_DEFINES) with no merged fix.
- Building on aarch64: default CMake option SSE=ON still passes -msse and breaks the build (issue #21, filed 2025-04-29, open, unresolved as of the last commit).
- Scalar single-precision expf/logf/isqrtf specifically — the record's own benchmark numbers show these particular scalar variants are slower than glibc libm.
- Teams that need active upstream support: last commit 2025-04-03, several issues open for years (CMake overwrites user CXX flags, clang linking error, Python 3.12 removed the imp module the Python scripts depend on).

**Integration:** header-only · none (optional Vc library integration via USE_VC CMake option) · GCC >=4.8, AppleClang >=5.0, Clang >=3.3, or ICC >=15.0 (enforced by CMakeLists.txt); C++11 is required only to build the optional DIAG benchmarking/unit-test tools, not to use the headers · x86-64 primarily (SSE on by default, AVX/AVX2/FMA opt-in via CMake flags); NEON is an opt-in CMake option for ARM but the default aarch64 build is currently broken by the SSE flag (issue #21); not Windows-compatible per issue #1

**Vs siblings:** Pick VDT over SLEEF or trigno_simd_cpp when you want one small header-only LGPL library covering the whole transcendental family (exp/log/trig/inverse-trig/isqrt) with a production track record in CERN/Geant4 physics code, rather than SLEEF's correctly-rounded (1-ulp) precision or trigno_simd_cpp's narrower sin/cos/tan-only scope; choose SLEEF instead when correct rounding matters more than raw speed.

**Gotchas:**
- fast_expf has a documented undefined-behavior bug (left shift of a negative value) for large negative inputs such as -163.48, caught by UBSan; open since 2019 (issue #10) with a proposed but unmerged fix.
- Default CMake option SSE=ON means a plain `cmake .` still emits -msse even on non-x86 targets, which currently breaks aarch64 builds (issue #21).
- Accuracy varies per function: the README's own table shows isqrt averaging ~0.45 LSB off libm, the largest deviation of any function in the library.
- CMake overwrites user-supplied CMAKE_CXX_FLAGS instead of appending to them (issue #8, open since 2018).

**Status:** Maintenance is stale (last commit 2025-04-03; multiple issues from 2016-2025 remain open, including a Windows-incompatibility report and an unfixed UB bug), but it's LGPL-3.0-or-later, header-only, and small enough to vendor; it's still cited in the repo description as used in CERN's Geant4 and LHC experiment software.

[repo](https://github.com/dpiparo/vdt) · [benchmark](https://iopscience.iop.org/article/10.1088/1742-6596/513/5/052027)

#### ordered-maps-trees

##### Flat-Map-RB-Tree (dro::FlatMap)  `C++`  `GPL-3.0`  `stale`  `Tier A`

Header-only flat red-black tree map/set in a vector; 1.4-1.9x faster than std::map at scale.

**Beats:** std::map — On gcc 14.2.1 with libstdc++, -DCMAKE_BUILD_TYPE=Release, on an isolcpus-pinned Intel Core i5-9300H (4 cores), dro::FlatMap beat std::map at 10,000,000 int32 elements: insert 622ns vs 855ns, find 551ns vs 774ns, erase 627ns vs 916ns (~1.4-1.9x across sizes); numbers are from the repo's committed benchmarks/results/*.txt, not chart-reading.

**How:** Storing nodes in a vector keeps the tree cache-contiguous and lets the implementation prefetch the next probed level during binary search on insert/erase, cutting cache misses versus a pointer-chasing red-black tree. Rotations swap node and child slots in place rather than relocating via pointers, and erase swaps the deleted key with the in-order successor then moves it to the vector's end instead of freeing/reallocating a node.

**Use it when:**
- Insert/find/erase-heavy workloads on int32-like keys where std::map's per-node allocation dominates, especially at 1M-10M elements (1.4-1.9x measured gain).
- You can pick a MaxSize index type (uint8_t-uint64_t) matching your expected element count for space efficiency.
- Keys/values are default-constructible and you don't need pointer/reference stability across inserts/erases.
- You want ordered iteration plus a map-like API without accepting flat_map's insert/erase cost.

**Skip it when:**
- Find-dominated workloads at large sizes: boost::flat_map find is faster than dro::FlatMap by 1M elements (134ns vs 234ns), and folly::heap_vector_map overtakes dro on find from ~100K elements.
- Code that holds iterators across modifying operations: every insert/erase/clear invalidates ALL iterators, not just erased ones.
- Long-lived containers with heavy erase churn: erased slots stay allocated until shrink_to_fit() or destruction, so memory can grow unbounded between compactions.
- Key/value types that aren't default-constructible.
- Production use requiring maturity: project is self-labeled Beta Testing with ~50% test coverage and has no issue-tracker history to gauge stability (issue tracker is empty).

**Integration:** header-only · none (standard library only: <vector>, <stdexcept>, <concepts>, <type_traits>, etc.) · C++20 per README; repo's own CMakeLists.txt builds with C++23 · not documented (no architecture-specific intrinsics in the header; no platform restrictions stated)

**Vs siblings:** Pick over boost::container::flat_set/flat_map when insert/erase throughput matters more than find at scale (boost::flat_map degrades sharply on insert/erase, e.g. 146,200ns at 1M vs dro's 283ns), but pick boost::flat_map instead if find dominates. Versus fast-containers or frozenca/BTree (larger, more mature B-tree alternatives with wider verified gains), dro::FlatMap is a smaller header-only option but is explicitly beta with ~50% test coverage.

**Gotchas:**
- All iterators are invalidated by any modifying operation (insert/erase/clear/swap), not just iterators to erased elements as in std::map.
- erase() does not free memory; call shrink_to_fit() or destroy the container to reclaim space from erased slots.
- Key and Value types must be default-constructible in addition to copy/move-assignable.
- The MaxSize template parameter (an integral type) bounds max_size() and throws std::runtime_error if the container grows past it.

**Status:** Stale: last commit 2024-11-16, GPL-3.0, and the project self-labels 'Beta Testing' with ~50% coverage — usable as a copyable single header, but treat as unmaintained and verify against current libstdc++ before relying on it.

[repo](https://github.com/drogalis/contiguous-rb-tree-map) · [benchmark](https://github.com/drogalis/contiguous-rb-tree-map/blob/main/README.md)

#### sorting

##### BlockQuicksort  `C++`  `GPL-3.0`  `abandoned`  `Tier A`

In-place Quicksort using block-buffered Hoare partitioning to avoid branch mispredictions; ~88% more elements/s than GCC std::sort on random ints.

**Beats:** std::sort — On GCC 4.8.4 (-O3 -march=native) on an Intel Core i5-2500K (4 cores, Ubuntu 14.04.4), the optimized BlockQuicksort variant needs ~45 ns/element vs ~85 ns/element for the repo's bundled copy of GCC 4.7.2's std::sort at n=2^28 on random 32-bit ints (~88% more elements sorted per second); smaller but still positive gains hold on 10-dim Vector and 21-field Record comparators for the mo-sqrt(n), duplicate-check variant, and std::sort wins on sorted/nearly-sorted input.

**How:** partition.h's hoare_block_partition_* functions compare a BLOCKSIZE=128 chunk of elements against the pivot into small fixed-size index buffers first, then do the swaps in a second, branch-free loop, so the CPU's branch predictor never has to guess the per-element comparison outcome during the swap phase. Pivot selection samples a median of ~sqrt(n) elements (median.h), and the qsort_double_pivot_check main loop (quicksort.h) adds a check for duplicate-heavy partitions adapted from Elmasry/Katajainen/Stenmark's Tuned Quicksort, falling back to insertion sort/std::partial_sort at small sizes like libstdc++'s introsort.

**Use it when:**
- Sorting large (n in the hundreds of millions) arrays of random 32-bit ints where per-element comparison is cheap and branch mispredictions dominate cost — the paper's largest reported gain (~88%) is at n=2^28.
- Multi-field comparators (the paper's 10-dim Vector / 21-field Record benchmarks) where smaller but still positive gains hold for the mo-sqrt(n),dc variant.
- Batch/offline throughput-oriented sorts where an unstable, in-place sort is acceptable and you're willing to hand-integrate a research header into your own call sites.
- As a reference implementation or benchmarking baseline for new sequential sort research — it's already used as the 'closest sequential competitor' in the IPS4o paper.
- Random or otherwise non-sorted input distributions; the paper itself reports std::sort wins on sorted/nearly-sorted input.

**Skip it when:**
- Need stability (equal elements keep relative order) — not stable, no stable variant provided.
- Sorted or nearly-sorted input — the input record's own claim notes std::sort wins there.
- Want a true drop-in replacement for std::sort with no call-site changes — this exposes sort() under its own namespace, not an overload of std::sort.
- Production/commercial use needing an actively maintained, permissively-licensed dependency — repo abandoned since Nov 2021 with two issues open and unanswered since 2019, and it's GPL-3.0 (the branch-avoidance technique itself has since been reimplemented under more permissive licenses in pdqsort and PPQSort).
- Want to just include one clean header — mixing more than one *.h++ interface file in the same translation unit causes duplicate-template-definition compile errors (open issue #6, unresolved).

**Integration:** source-drop · none external; each *.h++ variant needs matching repo-internal headers (quicksort.h, partition.h, median.h, insertionsort.h, rotations.h) included alongside it · C++11 (repo makefile: g++ -O3 -std=c++11 -march=native; benchmarked with GCC 4.8.4) · x86-64 only benchmarked (-march=native, Intel Core i5-2500K); portable C++11 templates with no explicit SIMD intrinsics observed — the branch-avoidance win depends on the compiler auto-vectorizing/optimizing the small fixed-size block-classification loop, so results are compiler- and arch-dependent

**Vs siblings:** Pick this over Boost.Sort/IPS4o/LearnedSort/etc. only when you specifically want the original peer-reviewed (ESA 2016 / JEA 2019) branch-avoidance partitioner — e.g. reproducing or benchmarking against it as IPS4o did — since the technique itself is now available in actively maintained, permissively-licensed form in pdqsort and PPQSort; for production sequential sorting prefer fluxsort or a pdqsort-family library instead of this abandoned GPL-3.0 repo.

**Gotchas:**
- Including more than one *.h++ interface header in the same translation unit triggers 'redefinition of template' errors from median.h (issue #6, open since 2019).
- Release-flag builds compile with -DNDEBUG, so the assert() sanity checks scattered through partition.h are stripped in the benchmarked configuration.
- The README recommends only blocked_double_pivot_check_mosqrt.h++ and blocked_simple.h++ out of ~40 header variants; a user asked in issue #5 (2019, still open) for clearer guidance on which variant to actually use.
- BLOCKSIZE (128) and pivot-sample-size constants are compile-time #defines tuned for the paper's int/Vector/Record types on one CPU; other key types or hardware may need retuning.

**Status:** Abandoned since its last commit on 2021-11-29, with two open issues unanswered since 2019, but classified 'copyable' — the source is small enough to vendor directly if your project's license tolerates GPL-3.0.

[repo](https://github.com/weissan/BlockQuicksort) · [benchmark](https://drops.dagstuhl.de/opus/volltexte/2016/6389/pdf/LIPIcs-ESA-2016-38.pdf)

##### LearnedSort  `C++`  `GPL-3.0`  `abandoned`  `Tier A`

CDF-model-based sort for numeric arrays, ~4x faster than std::sort on random data, ~15-20x on sorted/duplicate data.

**Beats:** std::sort — On 50M double-precision keys via Google Benchmark (GCC 9.3.0-10ubuntu2, CMake Release with -O3 -march=native -mavx, Intel Xeon Gold 6150), LearnedSort ran ~1080-1150ms vs std::sort's ~4850-5030ms (~4.2-4.6x) across Uniform, Exponential, Mixture-of-Gaussians, Zipf-0.75, and TwoDups, and ~50-60ms vs std::sort's ~750-1000ms (~15-20x) on Sorted, ReverseSorted, and Identical -- all read off the README's bar chart (plots/perf_charts.png), which prints no exact numeric labels.

**How:** Builds a two-layer 'recursive model index' (RMI): a root linear model plus, by default, 1000 leaf linear models trained on a 1% sample of the keys, which together approximate the empirical CDF. Each key's model-predicted CDF value picks one of ~1000 buckets directly (O(1) per key instead of O(log n) comparisons), the array is partitioned into those buckets in one pass, and each bucket is finished with std::sort/insertion sort. Separately, sort() first does a linear is_sorted/is_reverse_sorted check and returns immediately if it hits, which is why Sorted/ReverseSorted/Identical inputs are ~15-20x faster than std::sort -- that path bypasses the CDF model entirely.

**Use it when:**
- Large batches (tens of millions+) of primitive numeric keys (double/int/long) with no attached payload
- Data from a reasonably smooth/well-behaved distribution (uniform, exponential, Gaussian mixture, Zipfian, moderate duplicates) where the RMI's CDF approximation is accurate
- One-off or batch/offline sorts where the model-training cost amortizes over a large input, not per-call microsorts
- You can vendor a small header-only GPL-3.0 dependency and your project tolerates copyleft
- x86-64 Linux/GCC builds with AVX and -march=native, matching the environment this was actually benchmarked on

**Skip it when:**
- Sorting records/structs with payloads or string keys -- explicitly unsupported per the README's Limitations section
- Small inputs -- below roughly fanout x threshold (1000 x 100 = 100,000 elements by default) it just calls std::sort, so there's no upside
- GPL-3.0 is unacceptable for the target codebase -- heavier copyleft than most sibling sort libraries in this catalog
- Need active maintenance -- no commits since August 2021, all filed issues closed, unmaintained academic prototype
- Sorted, reverse-sorted, or all-duplicate inputs where you want a general-purpose winner -- the project's own chart shows IS4o matching or beating LearnedSort there

**Integration:** header-only · none for the sort itself (STL only, include/learned_sort.h + rmi.h + utils.h); the repo's benchmark/test harness additionally pulls in Google Benchmark, Google Test, and several third-party sort implementations, but those aren't needed to call learned_sort::sort · C++20 (CMakeLists.txt sets CMAKE_CXX_STANDARD 20); benchmarked with GCC 9.3.0-10ubuntu2 · Only tested on Linux (RHEL 7, Ubuntu 20.04); Release flags include -march=native -mavx, so x86-64 with AVX is assumed. A Windows/MinGW-w64 GCC10 user hit a correctness bug (issue #16), since fixed

**Vs siblings:** Pick LearnedSort over IPS4o/BlockQuicksort/x86-simd-sort/radix_sort when you have large batches (10M+) of doubles or ints from a smooth distribution and accept GPL-3.0 plus an unmaintained codebase for the ~4x win; for sorted/duplicate-heavy or adversarial data, or if you need ongoing support, IS4o matches or beats it on those inputs per LearnedSort's own benchmark chart.

**Gotchas:**
- Automatically short-circuits to std::sort for inputs at or below ~fanout*threshold elements (100,000 by default) or when RMI training fails, so the learned path silently never runs on small inputs
- The huge Sorted/ReverseSorted speedups come from an explicit is_sorted()/is_reverse_sorted() linear-scan pre-check with early return, not from the CDF model doing work
- Historically had several correctness bugs specific to integer key types (slope underflow, int-division in RMI training, failures with many repeated keys) -- all filed as issues and fixed via PRs by mid-2021, but there's been no activity since to catch anything similar
- No payload/tuple or string-key support (README 'Limitations'); only bare numeric arrays are sortable

**Status:** Abandoned academic prototype: no commits since August 2021 and every filed issue is closed with no further activity, but it's a small header-only, GPL-3.0 library, so it's easy to vendor and freeze at the last known-good GCC 9/10 toolchain.

[repo](https://github.com/anikristo/LearnedSort) · [benchmark](https://github.com/anikristo/LearnedSort/blob/master/plots/perf_charts.png)

## Copyleft — Unverified claims (tier C/D)

### stdlib-replacements

#### io-and-filesystem

##### FastReader  `C++`  `GPL-3.0`  `abandoned`  `Tier C`

Windows memory-mapped line reader using memchr; ~4x faster line iteration than std::ifstream::getline on a 9 KB file.

**Beats:** std::ifstream — On the repo's own Google Test 'Timing' suite (mean of 10 samples x 3 full passes over the repo's 9,194-byte TestFile.txt), CFileHandler averaged 56,700 ns versus 241,000 ns for std::ifstream + std::getline against the MSVC STL — about 4.25x faster — with no CPU disclosed and the Debug-vs-Release build configuration used for the published numbers unstated.

**How:** Maps the file into the process address space once instead of streaming through libc/CRT buffered I/O, avoiding per-getline syscalls and intermediate buffer copies. Line boundaries are found with memchr, which uses a vectorized/optimized scan, rather than std::getline's char-by-char sentry loop with locale-aware traits comparisons. Each line is copied exactly once, directly from the mapped pages into the returned std::string.

**Use it when:**
- Windows-only tool that repeatedly parses a small-to-medium text file line-by-line and can absorb the one-time CreateFileMapping cost
- Read-only, whole-file-fits-in-memory workloads (log parsing, config files) where std::ifstream + getline overhead is a measured bottleneck
- Codebases already linking ATL (atlbase.h/CHandle), so the extra dependency is free
- Prototyping or benchmarking where GPL-3.0 licensing of the file itself is acceptable

**Skip it when:**
- Any non-Windows target - code compiles only against WinAPI + ATL
- Files without a trailing newline: memchr returning nullptr on the last unterminated line yields (BYTE*)0 + 1, an invalid non-null pointer bug present in both the constructor and operator++
- Proprietary/closed-source projects that cannot take on GPL-3.0
- Anything needing formatted input, seeking, writing, or multi-threaded access - no documented thread safety, and CFileHandler holds raw pointers with no locking
- Production use generally: single-maintainer, 5 stars, no commits since 2019-11-13, no issues or PRs on record

**Integration:** source-drop · WinAPI (CreateFile/CreateFileMapping/MapViewOfFile) and ATL (atlbase.h, for CHandle) · Visual Studio 2019, PlatformToolset v142 per FastReader.vcxproj; uses std::iterator<> as an iterator base, which is deprecated in C++17 and removed in C++20, so it will not compile unmodified under /std:c++20 · Windows x86 and x64 (Win32 and x64 configs in the vcxproj); WinAPI-dependent, no POSIX path

**Vs siblings:** Neither catalogued sibling (CPath, reckless) targets line-by-line file reading, so this is the only io-and-filesystem entry solving that specific std::ifstream problem; pick it only if the workload is Windows-only line iteration and the GPL-3.0 license, ATL dependency, and unterminated-newline bug are all acceptable.

**Gotchas:**
- Unterminated final line (no trailing '\n') triggers memchr returning nullptr, which the code adds 1 to unchecked, producing an invalid pointer instead of a clean end-of-file marker
- Copy constructor and assignment are deleted with no move alternative provided, so CFileHandler cannot be stored in most STL containers directly
- CFileHandlerIterator::operator* allocates a new std::string per line, so iteration is not zero-copy despite the memory-mapped backing
- Requires ATL (atlbase.h) solely for CHandle's RAII wrapper around HANDLE, pulling in more than a plain WinAPI call would need

**Status:** Abandoned since 2019-11-13 (single maintainer, no open issues or PRs, 5 stars); GPL-3.0 plus the ATL dependency make it copyable only into GPL-compatible, Windows-with-ATL projects.

[repo](https://github.com/GeorgiiFirsov/FastReader) · [benchmark](https://github.com/GeorgiiFirsov/FastReader#test-results)

#### small-buffer-and-strings

##### buffet  `C`  `GPL-3.0`  `stale`  `Tier C`

C buffer type with SSO and refcounted views beating std::string on append, but not on plain memcopy or views.

**Beats:** std::string — On an unnamed "weak Core i3" (no CPU model given), Google Benchmark via g++ -std=c++2a -O2 against libstdc++: buffet's append beats real std::string (built with operator+=) by ~1.2-1.7x at 8/16, 24/4 and 24/32 init/append byte sizes, but loses at 8/4 (16.3 vs 10.9 ns). The headline SPLITJOIN figure (1397ns vs 3317ns) is not a std::string comparison - src/bench.cpp's SPLITJOIN_cpp splits into vector<string_view> and joins into a malloc'd char*, bypassing std::string entirely. std::string_view beats buffet's view construction by ~10x, and plain C memcpy beats buffet's memcopy at every size from 32 to 8192 bytes.

**How:** Small strings (<=21 bytes on 64-bit) live inline in the union, avoiding heap allocation and the pointer chase std::string sometimes needs. Substring 'views' (VUE/SSV/OWN-shared tags) alias the original data with a bumped refcount instead of copying, so split() returns a list of views rather than N allocated+copied strings, and join() writes them into one new store instead of many intermediate concatenations - this is what drives the SPLITJOIN number down. Appends resize via the same tagged-union/store machinery with -O2 codegen, giving a modest edge over std::string's growth strategy at some size pairs.

**Use it when:**
- Pure-C codebases that want std::string-like ergonomics (SSO, no-copy slicing) without pulling in C++
- Split/join-heavy workloads on many small-to-medium substrings, where view aliasing avoids per-substring allocation
- Incremental string building in roughly the 8-32 byte init/append range, matching the one workload buffet actually beats std::string on
- Short strings (<=21 bytes) where SSO avoids heap allocation entirely
- GPL-3.0 licensing is acceptable for the project

**Skip it when:**
- Proprietary/closed-source code - GPL-3.0 requires the whole linked work to be GPL-compatible
- Multithreaded sharing of a Buffet or its views - README lists thread safety as a TODO; refcounts are plain, non-atomic
- Read-only scanning/viewing of existing memory - std::string_view beats buffet's view construction by ~10x (0.609 vs 6.36 ns) in the repo's own bench
- Plain memcopy of buffers 32 bytes and up - raw C malloc+memcpy beats buffet at every size from 32 to 8192 bytes in the bench; buffet only wins at 8 bytes
- Anything needing C++ ergonomics (operators, RAII) or long-term maintenance guarantees - C API only, manual bft_free, no commits since Nov 2023, and the author calls the lib 'not much optimized' and the bench 'maybe amateurish'

**Integration:** static lib (source-drop friendly: single buffet.c/buffet.h pair, `make` builds bin/libbuffet.a) · none for the library; Google Benchmark (libbenchmark-dev) only to build the optional bench target · C11 for the library (gcc -std=c11); usable from C++ via the built-in extern "C" guard. Building the bundled benchmark harness needs C++20 (g++ -std=c++2a -fpermissive) · not explicitly documented; the tagged-union layout is asserted at compile time for 64-bit size_t/pointers, and the README's own TODO list includes '"test 32-bit and small RAM"', i.e. 32-bit is unverified

**Vs siblings:** Pick buffet over the C++-only siblings (FastString, fstring, Str, zuu_string_view, jank persistent_string, to_static_string) specifically when the codebase is plain C and needs reference-counted no-copy slicing for split/join-heavy string work; none of the other catalogued entries offer a C API. For pure view/scan-heavy work or C++ projects, prefer std::string_view or zuu_string_view instead, since buffet's own bench shows it losing to string_view by ~10x on plain views.

**Gotchas:**
- Never alias a Buffet with plain `=`; refcounts get corrupted. Use bft_dup() instead - README calls this out explicitly.
- Appending to an SSO Buffet that has live views can fail (returns 0) rather than growing, because growth would invalidate the views; release views first.
- Freeing the last view of a shared OWN store frees the underlying memory - any remaining un-bft_dup'd alias becomes a dangling pointer (README's own Security section shows this failure case).
- MEMCHECK/DEBUG guards that catch aliasing/double-free bugs are opt-in (`MEMCHECK=1 make` / `DEBUG=1 make`), not default.

**Status:** Stale: no commits since 2023-11-16 and the author's own README calls the library 'not much optimized' and the bench 'maybe amateurish'. Small enough to vendor as a single .c/.h pair, but GPL-3.0 blocks embedding in proprietary code.

[repo](https://github.com/alcover/buffet) · [benchmark](https://raw.githubusercontent.com/alcover/buffet/main/README.md)

##### jank persistent_string  `C++`  `MPL-2.0`  `active`  `Tier D`

jank's built-in immutable string (jtl::immutable_string, backing persistent_string); claims to tie or beat std::string and folly::fbstring.

**Beats:** std::string — The jank blog runs nanobench microbenchmarks (construction, copy, find, substr, at 'foo'-sized and 128-char sizes) comparing jank's persistent_string against libstdc++ std::string and folly::fbstring, claiming jank ties or wins every chart (notably beating both on large-string copy and large substr). The page states no numeric axis values and no compiler, flags, or hardware; the underlying gist baseline is std::basic_string with jank's own GC allocator, not std::allocator.

**How:** It follows folly::fbstring's three-word (24-byte on 64-bit) layout: a tagged union of an inline small-string buffer and a {pointer,size,flags} large-string struct, discriminated by 2 bits in the last byte, giving small-string optimization for strings up to 23 bytes with zero heap allocation. Large strings are either 'owned' (allocated with GC_malloc_atomic, so the Boehm GC doesn't scan their bytes) or 'shared': copy-construction and substr() of large strings just flip a category flag and reuse the source buffer with no refcounting, relying on jank's GC to keep the memory alive, unless the substring discards more than 512 bytes relative to the source, in which case it deep-copies instead of pinning a large buffer alive. The hash is cached inside the object's otherwise-unused word, so repeated hashing (e.g., as a map key) after the first call is O(1).

**Use it when:**
- You're already building on jank's Clojure-on-LLVM runtime, where this is the string type used throughout the compiler and generated code.
- Workloads dominated by copying or substring-ing large (24+ byte) strings, where GC-backed sharing can avoid the copy std::string/fbstring would perform.
- Short strings (<=23 bytes) where SSO avoids allocation entirely, similar in spirit to libstdc++/folly SSO.
- Read-mostly immutable string data where repeated hashing matters, since the hash is cached on first computation.
- Single-process native code already managed by a garbage collector, not code that must interoperate with plain std::string APIs.

**Skip it when:**
- You need a standalone C++ string library: this type only builds/links inside jank's compiler+runtime tree and depends on jank's object/oref system, jtl utilities, and Boehm GC.
- You need in-place mutation (append, resize, element write outside construction) — there is no mutator API; jank uses a separate string_builder for building strings incrementally.
- You need audited numbers: the benchmark page publishes only unlabeled SVG bar charts, no ns values, and states no compiler, flags, or CPU, so the real-world magnitude of any win is unverified (evidence tier D).
- You're sensitive to buffer lifetime: substring sharing keeps the parent large buffer alive via the GC until it's dropped or c_str() forces an owned copy, which can extend memory retention versus a copying string.
- You need a stable, versioned API: jank is alpha-stage language tooling, so this type's shape can change with the language rather than being maintained as an independent, stable library.

**Integration:** source-drop · jank's runtime object/oref system, jtl utility library (immutable_string_view, string_builder), Boehm GC (GC_malloc_atomic/GC_free) — not usable in isolation · C++20 (compiler+runtime/CMakeLists.txt sets cxx_std_20) · Linux (ubuntu-24.04) and macOS (macos-26) built in CI (.github/workflows/build-compiler+runtime.yml); a separate Windows workflow file exists in the repo but its status was not checked this session

**Vs siblings:** Only pick it if you're already targeting jank itself; for a standalone C++ project, buffet or FastString (both catalogued with page-stated numeric std::string construction/append speedups) are closer to drop-in replacements, and to_static_string covers the numeric-to-string conversion niche persistent_string doesn't address.

**Gotchas:**
- c_str() lazily converts a shared large string into an owned copy (allocation + memcpy) the first time it's called; data()/size() do not force this and are not guaranteed null-terminated for shared strings.
- Copy-constructing a large string mutates the source object's internal flag byte (const_cast) to mark both sides 'shared' — surprising side effect on a type documented as immutable.
- substr() cost is not uniform: small results or results within 512 bytes of the source size share the buffer (cheap), but discarding more than 512 bytes triggers a full deep copy.
- The small-string threshold is 23 bytes on a 64-bit machine (24-byte storage minus 1 flag byte); crossing it switches the code path from inline copy to GC allocation.

**Status:** Actively maintained (last commit 2026-09-21), MPL-2.0, 'copyable' usability but only as part of jank's own compiler+runtime source tree — the project itself is alpha-stage language tooling, not a standalone, independently versioned string library.

[repo](https://github.com/jank-lang/jank) · [benchmark](https://jank-lang.org/blog/2023-12-30-fast-string/)

#### sorting

##### poor-circle/radix_sort  `C++`  `GPL-3.0`  `abandoned`  `Tier C`

Header-only C++20 LSD byte-radix sort for ints/floats/pointers/pairs/structs; drop-in call syntax beats std::sort.

**Beats:** std::sort — First-party benchmark (author's benchmark/benchmark.cpp, MSVC 2022 release build, Intel i9-9900K @4.7GHz / DDR4-3000): sequential radix_sort sorted 1e9 int32 elements in 6402ms vs std::sort's 91407ms (~14.3x) and std::stable_sort's 82896ms (~12.9x); the margin narrows to ~5.2x on uint64 and ~2.9x on pair<uint64,uint64>, and measured against std::sort(par) instead of sequential std::sort the parallel win is only ~4.8x on int32, with radix_sort(par) slightly slower than std::sort(par) on pair<uint64,uint64> (24608ms vs 23532ms).

**How:** LSD (least-significant-byte-first) radix sort: one 256-bucket counting-sort pass per byte of the key (histogram, prefix-sum, scatter), so it never does a per-element comparison. The count and scatter loops are manually unrolled 4-wide with Duff's device, and each pass ping-pongs the data between the input and an auxiliary buffer rather than sorting in place. The `std::execution::par` overload shards the range across std::async tasks that count locally, merge per-thread histograms, then scatter concurrently for each byte pass, layering thread parallelism on top of the linear-time algorithm.

**Use it when:**
- Sorting large (1e6+) arrays of int32/uint32/float/pointer keys, where the key type already has or can get a radix_trait
- Composite keys such as std::pair<K,V> or small structs, where a byte-radix trait can be written for the sort key
- Throughput-bound batch sorting, sequential or with std::execution::par, on x86 with MSVC-class compilers
- Need for stable, comparator-free sorting of fixed-width keys rather than an arbitrary Compare predicate
- Willing to vendor one C++20 header (GPL-3.0 permitting) into the project

**Skip it when:**
- Need arbitrary/custom comparators (sort by a runtime-selected field or lambda) — radix_sort needs a compile-time radix_trait, not a Compare object
- Wide keys (64-bit ints, pair<uint64,uint64>): sequential speedup drops to ~2.9-5.2x, and radix_sort(par) can be slightly slower than std::sort(par) (measured 24608ms vs 23532ms on 1e9 pair<uint64,uint64>)
- Memory-constrained workloads: needs an O(n) auxiliary buffer the size of the input unless the caller supplies one
- Non-MSVC toolchains: the author only benchmarked MSVC STL on Windows, not libstdc++/libc++
- Projects needing active upstream support: single author, no commits since Jan 2022, one open usage question unanswered

**Integration:** header-only · none (standard library only: <vector>, <array>, <execution>, <future>, <memory>, <cstring>, <limits>) · C++20 (uses std::unsigned_integral/signed_integral/floating_point concepts and requires-clauses) · any (portable C++20, no SIMD or platform intrinsics); author only benchmarked Windows/MSVC x86-64

**Vs siblings:** Unlike the comparison-based siblings (BlockQuicksort, IPS4o, LearnedSort, x86-simd-sort) or the stable-sort replacements (fluxsort, quadsort), radix_sort is the only non-comparison LSD byte-radix sort in this set; pick it when the key is an integer, float, pointer, or a pair/struct you can describe with a byte-radix trait and you want the largest win on 32-bit keys, and prefer a comparison-sort sibling for 64-bit/wide keys or arbitrary comparators where radix_sort's edge shrinks or vanishes.

**Gotchas:**
- std::execution::par is accepted only as a dispatch tag; it always drives its own std::async tasks internally rather than routing through a standard execution-policy engine
- demo/demo.cpp's custom-struct example does not compile as written (its radix_trait<mystruct> and my_trait reference undefined p1/p2 identifiers) — follow the README's mystruct pattern instead
- Signed integers and floats flip the sign/exponent bit (XOR 0x80) inside the built-in radix_trait so byte order matches numeric order; a hand-written trait for a new type must replicate this or sort order breaks silently
- Without a caller-supplied buffer, every call allocates a full extra copy of the input (sizeof(value_type) * n bytes)

**Status:** Abandoned since its last commit on 2022-01-31 (single author, one unanswered open issue); GPL-3.0-licensed and a single header, so still copyable, but expect no fixes or support.

[repo](https://github.com/poor-circle/radix_sort) · [benchmark](https://github.com/poor-circle/radix_sort#benchmark)

### toolchain-and-build

#### build-systems

##### ccache  `C++`  `GPL-3.0-or-later`  `active`  `Tier C`

Compiler cache that skips re-running GCC/Clang/MSVC on unchanged source, reusing prior object output.

**Beats:** Uncached compilation (same compiler command run without ccache); the page does not involve Make/Ninja and does not name the compiler — First-party ccache.dev page reports median-of-100-runs, single-file cache-hit timings on an Intel Core i5-4690K with SSD (compiler unnamed, ccache 3.7.1): compiling ccache.c (-g -O2 -MD) was 145.39x/137.81x/28.33x faster than an uncached compile in direct/depend/preprocessor mode, and compiling the header-heavy c++_includes.cc (-MD) was 29.10x/29.32x/5.09x faster. These are cache-hit-only, single-file numbers against a plain uncached compile, not end-to-end project build speedups, and the same page shows cache misses running 0.83-0.98x (slightly slower) than uncached.

**How:** In direct mode it hashes the raw, unpreprocessed source plus its `#include`d headers (using mtime/ctime plus content hashes) to form a cache key, skipping the preprocessor pass entirely on a hit. Preprocessor mode falls back to running cpp and hashing its output when direct mode is unsafe (e.g. macros like __TIME__). Depend mode derives the key from the compiler's -MD/-MMD dependency list. Hashing uses BLAKE3 and results are stored zstd-compressed, so a hit is a hash computation plus a file copy instead of a full parse/codegen/link.

**Use it when:**
- Repeated local or CI rebuilds of the same C/C++/CUDA/Objective-C tree where most translation units are unchanged (branch switches, re-running CI on similar commits)
- Toolchains already on GCC, Clang, MSVC, or NVCC on Linux, macOS, or native Windows (mingw-w64), where masquerading as the compiler via symlink or PATH prefix is acceptable
- Shared build farms or multi-developer teams that want cross-machine hits via ccache's Redis or HTTP remote storage backends
- Header-heavy C++ files where preprocessing dominates wall time and hit rate is expected to be high

**Skip it when:**
- True cold/clean builds or CI that wipes the cache every run — the vendor's own numbers show cache misses at 0.83-0.98x (i.e. slightly slower) than an uncached compile
- Source using __TIME__, __DATE__, or __TIMESTAMP__, which forces the slower preprocessor-mode fallback unless you opt into `sloppiness=time_macros`
- Build flags that defeat the cache key: most -Xpreprocessor uses, -Wp options other than -MD/-MMD/-D/-U, or filesystems with coarse mtime granularity that make ccache disable caching as a race-condition safeguard
- Windows setups needing more than mingw-w64 parity — MSYS2 and other Unix-likes are only partially supported, and MSVC-style compilers don't get full direct-mode support
- Situations demanding fully reproducible, audited benchmark numbers — the vendor's own performance page never names the compiler used

**Integration:** source-drop · Required: BLAKE3, fmt, tl-expected, xxhash, Zstandard (bundled or auto-downloaded if not found locally). Optional: cpp-httplib and hiredis for HTTP/Redis remote storage, doctest for tests. · CMake 3.15+ to build; C++20 compiler (GCC 11+, Clang 12+, AppleClang 10+) plus a C99 compiler. Note: the benchmarked version (3.7.1) predates this and had much looser requirements. · Linux and macOS (Level A, regularly tested on Ubuntu 22.04/24.04 and macOS 14); native Windows via mingw-w64 (Level A); Windows/MSYS2 and other Unix-likes (Level B, partial)

**Vs siblings:** No direct siblings — Mill, Buck2, tup, and xmake are build-graph orchestrators, while ccache caches individual compiler invocations underneath any of them. Use ccache alongside those tools when the bottleneck is redundant single-file recompiles rather than build-graph scheduling or dependency tracking.

**Gotchas:**
- __TIME__/__DATE__/__TIMESTAMP__ in source disables direct mode and forces the slower preprocessor-mode path
- If an included header's mtime is newer than the time ccache started, it disables caching entirely for that compile as a race-condition safeguard (tune with sloppiness=include_file_ctime,include_file_mtime)
- Default cache size cap is 5 GB with no file-count limit; old entries are evicted silently once the cap is hit
- Direct mode has compiler-option restrictions (most -Xpreprocessor uses and non-dependency -Wp options force preprocessor mode)

**Status:** Actively maintained (last commit 2026-09-19; current release targets C++20/CMake 3.15+), GPL-3.0-or-later, and easy to obtain via package managers or source build — it's the de facto default compiler cache bundled in many Linux distros and CI images.

[repo](https://github.com/ccache/ccache) · [benchmark](https://ccache.dev/performance.html)

##### tup  `C`  `GPL-2.0`  `active`  `Tier C`

File-based build tool that beats Make's incremental-rebuild scanning via a persistent Linux-only file monitor and per-command sandboxing.

**Beats:** Make — On tup's own synthetic C-project generator (log-scale graphs, N up to 100k files / ~200k with headers, make run as `make -rR`, no CPU/OS/compiler flags stated), tup reports ~0s no-op checks and ~0.1s single-file rebuilds versus make's figures of roughly 20-30 minutes at 100k files; tup's cold/initial build is itself 5-30% slower than make, and tup's own file monitor took up to 2min:30s to cold-start at 200k files.

**How:** Speed comes from a persistent background 'monitor' process (inotify on Linux) that watches the filesystem so tup never has to stat/walk the whole tree like make does on every invocation; state lives in an embedded SQLite database rather than being recomputed each run. Per-command FUSE sandboxing produces an exact dependency graph (not user-declared globs), so a change dirties only the affected graph nodes -- turning no-op and single-file rebuild checks into near O(changed files) instead of O(all files).

**Use it when:**
- Large Linux C/C++ trees (tens of thousands of files) where make's per-invocation directory scan/stat dominates the edit-compile-test loop.
- Teams willing to run a persistent `tup monitor` daemon in the background and keep it warm.
- Projects that want undeclared-dependency errors caught automatically via file-access tracing instead of hand-maintained header dependency lists.
- GPL-2.0-compatible projects that can vendor the tool as-is (it already bundles Lua, PCRE2 and SQLite3, no external runtime deps).

**Skip it when:**
- Clean/cold builds: tup measured 5-30% slower than make across sizes on the vendor's own benchmark.
- macOS/Windows, or Linux without FUSE: the fast-path monitor is inotify/Linux-specific, the OSX shim has an open unresolved issue since 2014, and FUSE-based sandboxing broke on libfuse3 3.17.1 as recently as 2025 (issue #518).
- Teams needing Makefile compatibility, mainstream IDE integration, or a large plugin ecosystem -- 1.3k stars versus make's ubiquity.
- Build outputs generated dynamically/implicitly -- tup requires every output declared up front; undeclared writes are errors, which is a real migration cost.
- One-off or CI-only cold builds where the monitor never warms up -- most of the claimed win depends on a hot monitor and hot OS cache.

**Integration:** source-drop (build tup itself from source via bootstrap.sh; not header-only) · none required to vendor -- bundles Lua, PCRE2, SQLite3 in-tree; needs libfuse on Linux for command sandboxing · not documented precisely -- plain C, built via its own bootstrap.sh/tup; Windows build via build-win32.sh (MinGW) · Linux (full speed: inotify monitor + FUSE sandbox), macOS (dllinject/ldpreload shim, no monitor -- open issue since 2014), Windows (dllinject-based tracing)

**Vs siblings:** Pick tup over xmake/Mill/Buck2/ccache when the specific pain is make's linear directory-scan overhead on a huge Linux C/C++ tree during interactive edit-rebuild, and you can run a persistent monitor daemon and rewrite the build in Tup's DAG syntax; xmake is the closer choice for a faster Make-compatible generator without changing build files, and ccache if the bottleneck is recompilation itself rather than dependency scanning.

**Gotchas:**
- Near-zero no-op/rebuild times require `tup monitor` already running; without it tup falls back to scanning, and a third-party benchmark (issue #268) found it slower than make/ninja.
- libfuse3 ABI changes have broken tup's build-command file sandboxing before (3.17.1, reported 2025).
- Monitor cold-start took 2min:30s at 200k files in the vendor's own benchmark (2.5s once cache is hot).
- All build outputs must be declared explicitly; undeclared writes are treated as errors, not warnings.

**Status:** Actively maintained (last commit 2026-07-30, closed a race-condition crash as recently as July 2026) but niche -- 1,262 stars, 168 open issues; GPL-2.0 and copyable/vendorable, though its FUSE-based build sandboxing has broken on newer libfuse3 as recently as 2025.

[repo](https://github.com/gittup/tup) · [benchmark](http://gittup.org/tup/make_vs_tup.html)

#### compilers-frontends

##### TinyCC (tcc)  `C`  `LGPL-2.1`  `active`  `Tier C`

Tiny self-hosting C compiler/JIT that compiles about 9x faster than gcc -O0, trading away optimization.

**Beats:** GCC — On Fabrice Bellard's own tcc benchmark page, compiling the Links web browser (76,936 source lines, but 1,950,947 lines / 67.2MB actually compiled due to repeated header inclusion) on a 2.4GHz Pentium 4: TinyCC 0.9.22 finished in 2.27s (859,000 lines/s, 29.6MB/s) versus GCC 3.2 at -O0 in 20.0s (98,000 lines/s, 3.4MB/s), about a 9x wall-clock advantage. Both compilers ran with no comparable optimization flags enabled (tcc has none), and the hardware/compiler versions are roughly 2003-2005 era.

**How:** It skips almost everything gcc's pipeline does beyond translation: no real optimizer (tcc has no flag comparable to -O1/-O2/-O3), a single fast pass from source straight to machine code, and its own integrated preprocessor/assembler/linker avoid forking out to separate cc1/as/ld processes. It also natively supports 6 target architectures (i386, x86-64, ARM, AArch64, RISC-V64, plus legacy TMS320C67xx) with a simple, non-SSA-optimizing code generator per target. The cost of skipping optimization is codegen roughly at gcc -O0/-O1 quality.

**Use it when:**
- Tight edit-compile-run development loops where compiler latency, not runtime speed, dominates iteration time
- Ad hoc 'C scripting' -- running a .c file directly via a #!tcc -run shebang instead of compiling a real binary
- Embedding a C compiler/JIT inside another program (via libtcc) for runtime code generation, e.g. compiling small C snippets to native code and calling them in-process
- Bootstrapping or rescue environments where binary size matters (GNU Mes uses tcc to bootstrap a build from source)
- Local/CI dev builds of large C codebases where a project bundles tcc for fast iteration and uses a real compiler for release builds (this is how the V language uses it)

**Skip it when:**
- Producing optimized release binaries -- there is no optimization pass comparable to gcc -O1/-O2/-O3, so generated code is measurably slower
- Code relying on full C11 or the broader GNU C extension surface -- tcc covers 'many' C11 features and GNU extensions, not all of them (not documented as 100% coverage)
- C++ code -- tcc is a C compiler only
- Toolchains that depend on gcc/clang-specific features such as LTO, sanitizers, or vendor-specific builtins not implemented by tcc
- Programs combining the -b bounds checker with signal handlers or fork() in a multi-threaded process -- the docs call this out as a known incompatibility because the bounds-checking code uses locks

**Integration:** source-drop / standalone compiler binary (CLI, gcc-like flags); optional static and shared libtcc library for embedding as an in-memory JIT · none required to build (self-hosting: ./configure && make, or make test); optional -lpthread when using the -pthread flag · Any ANSI C (C89) host compiler to bootstrap from source, or tcc itself; as a language target it implements ISO C99, many ISO C11 features, and GNU C extensions (inline asm, _Thread_local, __attribute__((cleanup)), _Static_assert, asm goto, stdatomic) · x86 (i386), x86-64, ARM, AArch64, RISC-V64, legacy TMS320C67xx; Linux/BSD (ELF), native macOS x86-64 (Mach-O), Windows (PE, see tcc-win32.txt), Android (position-independent executables)

**Vs siblings:** Pick tcc over zapcc or MIR/c2m when you want a mature, widely-deployed, general-purpose C compiler and embeddable JIT rather than a narrower research/prototype tool: zapcc is an abandoned Clang fork focused on incremental C++ template caching, and MIR/c2m is a newer, more experimental C-to-MIR JIT (bigger claimed speedup, less production track record). Neither zapcc nor cg_clif target C the way tcc does (zapcc is C++-only via Clang, cg_clif is a Rust backend), so for straight C dev-loop speed or in-process C JITing, tcc is the direct fit.

**Gotchas:**
- The -b bounds checker is incompatible with signal handlers (checking is disabled inside them) and interacts badly with fork() in multi-threaded programs, per tcc-doc.texi -- both stem from locking inside the bounds-checking runtime
- Bound-checked code (-b) is not included in shared libraries; the main executable must itself be built with -b for the checker to take effect
- Codegen quality sits around gcc -O0/-O1; don't compare tcc binaries' runtime speed to an optimized gcc/clang build
- -std=version only distinguishes c11/gnu11 (sets __STDC_VERSION__ to 201112) from everything else (199901); it isn't a fine-grained standards switch like gcc's

**Status:** Actively maintained: this GitHub mirror tracks the upstream repo.or.cz mob development branch and was pushed 2026-09-22; current in-tree version is 0.9.28rc. LGPL-2.1, small self-contained C source tree, easy to vendor -- matches its 'copyable' usability rating.

[repo](https://github.com/TinyCC/tinycc) · [benchmark](https://bellard.org/tcc/)
