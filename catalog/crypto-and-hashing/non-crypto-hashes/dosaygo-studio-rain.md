# Rain (Rainbow hash)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Small scalar multiply-rotate hash with 64/128/256-bit output; beats HighwayHash-128/256 and FarmHash-128 only on short-key latency.

| | |
|---|---|
| **Beats** | HighwayHash-128 and FarmHash-128.CM (128-bit hashes in the SMHasher3 results table); the repo names no baseline itself |
| **Claimed result** | Claim only (README): 'Rainbow is the fastest 128-bit hash, and the fastest 256-bit hash (non-crypto)'; README table gives Rainbow 3-6 GiB/s with no baseline. SMHasher3 results page data: rainbow-128 62.06 cycles on 1-31 byte keys vs HighwayHash-128 99.09 (\~1.6x faster, derived from page data), FarmHash-128.CM.seed1 69.61 (\~1.1x), MeowHash 61.51 (tie); rainbow-256 103.65 vs HighwayHash-256 154.48 (\~1.5x) and PearsonBlock-256 168.68. Not faster elsewhere: rainbow-128 is slower than a5hash-128 (30.27) and MuseAir-128 (30.97) on short keys, and bulk is 1.27 bytes/cycle (4.14 GiB/s at the assumed 3.5 GHz) vs HighwayHash-128 2.87, a5hash-128 6.92, MuseAir-128 7.15 and MeowHash 12.43; rainbow-256 bulk 1.28 vs HighwayHash-256 2.88 and RH512 2.50. |
| **Workload** | SMHasher3 Speed test as published in the SMHasher3 results README: average cycles/hash over 1-31-byte keys and bulk bytes/cycle at 262144-byte keys, Rainbow 128-bit and 256-bit v3.7.1 against the other hashes that pass all tests. Results page does not name the CPU (harness prints '@ 3.5 ghz'). |
| **Metric** | latency |
| **Adoption** | 134 stars, 9 forks |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/DOSAYGO-STUDIO/rain) · [benchmark](https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md) |

## Verdict

SMHasher3's maintainer-run results table (Rainbow v3.7.1, CPU, compiler and flags unstated, cycles converted at a nominal 3.5 GHz) lists rainbow-128 at 62.06 cycles/hash on 1-31-byte keys vs HighwayHash-128 99.09 and FarmHash-128.CM.seed1 69.61, and rainbow-256 at 103.65 vs HighwayHash-256 154.48; in bulk (262144-byte keys) Rainbow is 1.27-1.28 bytes/cycle, about half of HighwayHash and FarmHash-128.CM. The repo has no benchmark against any other hash; its own table only compares its C++ CLI with its WASM CLI.

## Use it when

- You need a 128- or 256-bit non-crypto digest of short keys (1-31 bytes) in portable scalar C++ and currently use HighwayHash-128/256 or FarmHash-128.CM: SMHasher3 shows 62.06 vs 99.09 and 69.61 cycles (128-bit) and 103.65 vs 154.48 cycles (256-bit).
- You want one roughly 140-line Apache-2.0 function whose 64-, 128- and 256-bit variants each pass all 250 SMHasher3 tests.
- Native C++ and browser/Node code must produce the same digests (the npm WASM build is checked against the same test vectors).
- Big-endian targets that must match little-endian digests (the bswap template parameter normalizes loads and stores).

## Skip it when

- Bulk hashing of large buffers: 1.27-1.28 bytes/cycle against HighwayHash 2.87, FarmHash-128.CM 2.61, a5hash-128 6.92, MuseAir-128 7.15, MeowHash 12.43 and XXH3-128 12.72 on the same SMHasher3 page.
- 64-bit hash-table keys: rainbow-64 takes 61.63 cycles on short keys and 1.28 bytes/cycle, against rapidhash 30.41/8.82, wyhash 29.31/6.98 and XXH-64 52.60/3.99.
- Picking the fastest passing 128- or 256-bit hash: a5hash-128 and MuseAir-128 beat rainbow-128 on both short keys and bulk, and RH512 (256-bit, 250/250 passing) beats rainbow-256 on both (79.73 cycles and 2.50 bytes/cycle vs 103.65 and 1.28).
- Anything adversarial (MACs, integrity against attackers, HashDoS resistance): Rainbow is explicitly non-cryptographic, no keyed-hash claim is documented, and the sibling Rainstorm is unvetted with a published reduced-round collision.
- Long-term stored digests: the README says hash definitions may evolve, and v3.7.1 already changed Rainbow's mixing after issue #79.

## How it is fast

State is four 64-bit lanes seeded with seed+length. Each 16-byte block is added to and subtracted from the lanes, then the code alternates mixA (two independent chains of multiply by an odd 64-bit prime, rotate, multiply, with xor coupling; eight multiplies) and mixB (four multiplies, seed injection, lane rotation, added in v3.7.1 after issue #79 showed no downward data flow). Keys under 16 bytes skip the loop and take only four mix calls plus the tail for a 64-bit digest (one or five more for 128 or 256 bits), which is why short-key latency is competitive; there is no SIMD, AES or 128-bit multiply, so bulk speed stays at about 1.28 bytes/cycle (12 dependent-chain multiplies per 32 bytes).

## Compared with alternatives

Pick Rainbow over a5hash or MuseAir only when you specifically need a 256-bit non-crypto digest from scalar code with matching native and WASM builds; for 64-bit keys rapidhash, wyhash or a5hash are about 2x faster on short keys, and for bulk data MeowHash (12.43 bytes/cycle), XXH3 (12.72) and AquaHash (15.84) are about 10-12x faster on the same SMHasher3 page.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the hash (src/rainbow.cpp + src/common.h); the rainsum CLI also needs cxxopts, zlib and OpenMP |
| **Minimum toolchain** | C++17 per the README; the Makefile builds with -std=c++20 -O3 -march=native using Homebrew LLVM clang++ on macOS |
| **Platforms** | any 64-bit-multiply target, little- or big-endian (endianness from GCC/Clang __BYTE_ORDER__); WASM via Emscripten |
| **Thread safety** | single-call rainbow() is a pure function with no global state (reentrant); a HashState instance must not be shared between threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the README's C++ vs WASM table (4x-23x): scripts/bench.mjs times whole child processes (./rainsum FILE vs node ./js/rainsum.mjs FILE) once per row, and the C++ side reads the file through std::istreambuf_iterator into a vector before hashing. The 10 B to 1 MB rows are all about 5-7 ms vs 127 ms, which is Node and process start-up; subtracting the 10-byte row, the 100 MB row implies about 2.3 GB/s native vs 1.3 GB/s WASM, roughly a 1.8x gap (derived from page data). The record's '4x to 23x slower' tradeoff should not be read as hash speed.
- The README headline 'fastest 128-bit hash, and the fastest 256-bit hash' is false on the SMHasher3 page it links: rainbow-128 is dominated by a5hash-128 and MuseAir-128, and rainbow-256 by RH512, on both short-key cycles and bulk bytes/cycle.
- The README says to link rainbow.o, but rainbow::rainbow is a file-static template, so the object exports nothing callable; the repo's own CLI #includes rainbow.cpp. The Makefile hard-codes /opt/homebrew/opt/llvm clang++, xcrun -isysroot, -fopenmp and -march=native, so Linux builds need edits.
- The streaming HashState was dead code that ignored every update after the first until 2026-07-27; it now matches the single-call hash but must be initialized with the total length, so it cannot hash a stream of unknown length. The README option list says the CLI defaults to Rainstorm while the code defaults to Rainbow, and open issue #170 reports that stream mode appends a text label to binary output.

## Known shortcomings

- SMHasher3 results (raw/rainbow-128.txt): the README 'fastest 128/256-bit' claim is false on that page. Wins only short-key latency against HighwayHash and FarmHash-128.CM; about 2x slower bulk than both and slower than XXH-64 and XXH3 on both metrics. No CPU or flags. The SMHasher3 maintainer is credited with code improvements to Rain.
- Enricher: the README C++ vs WASM table (4x-23x) times whole process launches (scripts/bench.mjs exec of ./rainsum vs node), one run per row, so the 10 B to 1 MB rows are start-up cost and net of start-up the 100 MB row is about 2.3 vs 1.3 GB/s (about 1.8x, derived). On SMHasher3 a5hash-128 and MuseAir-128 beat rainbow-128 on both short-key and bulk metrics, and RH512 (256-bit, 250/250 pass) beats rainbow-256 on both (79.73 vs 103.65 cycles, 2.50 vs 1.28 B/cycle). The README's 'link rainbow.o' exports nothing; the Makefile is macOS/Homebrew-only; streaming HashState was broken until 2026-07-27.

## Caveats and trade-offs

The README headline claim (fastest 128-bit and 256-bit non-crypto hash) is not supported by the SMHasher3 results page it links: several passing 128-bit hashes (a5hash-128, MuseAir-128, MeowHash) are faster in bulk and on short keys, and at 256 bits HighwayHash-256 and CityHashCrc-256 (which fails some tests) are faster in bulk. The only wins found are narrow (short-key latency against HighwayHash and FarmHash; MeowHash ties). Against the usual non-crypto incumbents it is slower on the same page: 64-bit rainbow is 61.63 cycles and 1.28 bytes/cycle vs XXH-64 52.60 and 3.99, and XXH3-128 (fails some tests) is 36.13 and 12.72. SMHasher3 results list the CPU nowhere; the SMHasher3 README describes the maintainer's machine (AMD Ryzen 9 3950X pinned to 3500 MHz, gcc 9.3) only for its runtime-comparison table, which fits the '@ 3.5 ghz' conversion but is not stated as the results machine. Results come from SMHasher3 20251015, 20251112 or 20260827 release builds. The table is the maintainer's single run; Rain's README licence line credits the SMHasher3 maintainer with improvements to the code, so the suite is not fully arm's length. Results were measured on Rainbow v3.7.1; the 4.0.0 release changed only Rainstorm (README: Rainbow digests unchanged). The repo's own results/smhasher3/rainbow-256-v3.7.1.txt came back as an empty file through raw.githubusercontent.com and was not used. The assigned URL github.com/DOSAYGO-Research/rain resolves to DOSAYGO-STUDIO/rain. [retier] SMHasher3 results (raw/rainbow-128.txt): the README 'fastest 128/256-bit' claim is false on that page; rainbow-128 wins only short-key latency against HighwayHash and FarmHash-128.CM, is about 2x slower bulk than both and slower than XXH-64 and XXH3 on both metrics, and a5hash-128 and MuseAir-128 beat it on both short-key and bulk; RH512 (256-bit, 250/250 pass) beats rainbow-256 on both (79.73 vs 103.65 cycles, 2.50 vs 1.28 B/cycle). No CPU or flags; the SMHasher3 maintainer is credited with code improvements to Rain. The README C++ vs WASM table (4x-23x) times whole process launches (scripts/bench.mjs exec of ./rainsum vs node), one run per row, so rows up to 1 MB are start-up cost and the 100 MB row is about 2.3 vs 1.3 GB/s (about 1.8x, derived). 'link rainbow.o' exports nothing; the Makefile is macOS/Homebrew-only; streaming HashState was broken until 2026-07-27.

Rainbow is a roughly 140-line multiply/rotate hash with scalable 64, 128 or 256-bit output that passes all 250 SMHasher3 tests (64-bit variant claimed), but its bulk speed is low (about 1.3 bytes/cycle). The repo also ships Rainstorm, a slower experimental crypto-style hash whose v4 README says an external review found a practical collision for a two-message-round reduction; it is unvetted. WASM port is 4x to 23x slower than the C++ build (README benchmark).

## Maintenance

Actively developed (last commit 2026-09-15, recent work is Rainstorm cryptanalysis), Apache-2.0 and small enough to vendor as two files, but the speed headline overstates the SMHasher3 data and Rainbow digests have changed between versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C to B: the SMHasher3 results summary (a well-known independent suite run by its maintainer, not the Rain author) lists rainbow-128 at 62.06 avg cycles on short keys against HighwayHash-128 at 99.09 and FarmHash-128.CM.seed1 at 69.61, and rainbow-256 at 103.65 against HighwayHash-256 at 154.48; raw/rainbow-128.txt confirms 62.06 cycles and 1.27-1.28 bytes/cycle. Not A because neither the summary nor the raw file names the CPU model, compiler or flags (only a nominal '@ 3.5 ghz' conversion); same treatment as the earlier SMHasher3-based B entries (ChibiHash, a5hash, MeowHash, AquaHash).
- **Verifier notes:** Numbers in claimed_speedup all match the SMHasher3 results summary and raw/rainbow-128.txt (whose small-key test is [1, 31]-byte keys although the summary header says 1-32). Metadata confirmed: Apache-2.0, 134 stars, 9 forks, not a fork, last commit 2026-09-15 (active). Shortcomings: README 'fastest 128-bit and 256-bit hash' claim is false on the page it cites; wins only on short-key latency vs HighwayHash-128/256 and FarmHash-128.CM, about 2x slower in bulk than both, and slower than XXH-64 and XXH3 on both metrics; suite maintainer is credited with Rain code improvements.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** SMHasher3 results (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://gitlab.com/fwojcik/smhasher3/-/blob/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/rainbow-128.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/README.md>
  - <https://github.com/DOSAYGO-STUDIO/rain>
  - <https://raw.githubusercontent.com/DOSAYGO-STUDIO/rain/HEAD/README.md>
  - <https://github.com/DOSAYGO-STUDIO/rain/commits/boss>
- **Sources the enricher read:**
  - <https://github.com/DOSAYGO-STUDIO/rain>
  - <https://github.com/DOSAYGO-STUDIO/rain/commits/boss>
  - <https://github.com/DOSAYGO-STUDIO/rain/issues?q=is%3Aissue>
  - <https://github.com/DOSAYGO-STUDIO/rain/issues/79>
  - <https://github.com/DOSAYGO-STUDIO/rain/issues/170>
  - <https://raw.githubusercontent.com/DOSAYGO-STUDIO/rain/HEAD/README.md>
  - <https://raw.githubusercontent.com/DOSAYGO-STUDIO/rain/HEAD/src/rainbow.cpp>
  - <https://raw.githubusercontent.com/DOSAYGO-STUDIO/rain/HEAD/src/common.h>
  - <https://raw.githubusercontent.com/DOSAYGO-STUDIO/rain/HEAD/src/tool.h>
  - <https://raw.githubusercontent.com/DOSAYGO-STUDIO/rain/HEAD/src/rainsum.cpp>
  - <https://raw.githubusercontent.com/DOSAYGO-STUDIO/rain/HEAD/scripts/bench.mjs>
  - <https://raw.githubusercontent.com/DOSAYGO-STUDIO/rain/HEAD/Makefile>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/README.md>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/rainbow-256.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/results/raw/RH512.txt>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/hashes/rainbow.cpp>
  - <https://gitlab.com/fwojcik/smhasher3/-/raw/main/hashes/g3-rh512-256.cpp>
  - <https://gitlab.com/api/v4/projects/fwojcik%2Fsmhasher3/repository/tree?path=hashes>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/dosaygo-studio/rain`) · [data/wave7/enrich/raw/github_com_dosaygo_studio_rain.json](../../../data/wave7/enrich/raw/github_com_dosaygo_studio_rain.json) (enrichment confidence 0.8)

</details>
