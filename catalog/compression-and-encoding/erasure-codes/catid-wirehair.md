# Wirehair

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Erasure codes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> O(N) fountain (rateless) erasure code in C; the author's GF256 build encoded about 6.6x and decoded about 7.9x faster than his CM256 Reed-Solomon at k=m=128.

| | |
|---|---|
| **Beats** | CM256 (catid/cm256, O(N^2) Cauchy-matrix MDS Reed-Solomon codec; Longhair measured alongside) |
| **Claimed result** | Leopard's Benchmarks.md: WH256 wirehair_encode(N = 128) 661.644 MB/s and wirehair_decode 830.103 MB/s vs CM256 encode 99.6658 MBps and decode 104.651 MBps (Longhair 100.342 and 96.3757 MB/s), i.e. about 6.6x faster encode and 7.9x faster decode than CM256 (derived from page data). Text: Wirehair 'Encodes at 660 MB/s, and decodes at 830 MB/s for ALL cases' and is the fastest decoder in that comparison; Wirehair's README also states it scales as O(N) rather than O(N log N) (Leopard) or O(N^2) (Fecal). |
| **Workload** | Erasure-code encode and decode throughput for 128 data pieces of 64,000 bytes with 128 recovery pieces (code rate 1/2), WH256 (Wirehair with the GF256 inner loops) vs CM256, Longhair, FEC-AL and Leopard, on the author's AVX2 laptop. |
| **Metric** | throughput |
| **Hardware** | Author's 'few year old' laptop with AVX2 (CPU model not stated) |
| **Adoption** | 394 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/catid/wirehair) · [benchmark](https://raw.githubusercontent.com/catid/leopard/HEAD/Benchmarks.md) |

## Verdict

Leopard's Benchmarks.md, written by the same author, reports WH256 (the GF256 pre-production branch of Wirehair) encoding 128 x 64,000-byte pieces at 661.6 MB/s and decoding at 830.1 MB/s against his CM256 Cauchy Reed-Solomon at 99.7 and 104.7 MB/s (about 6.6x and 7.9x, derived from page data), on an unnamed 'few year old' AVX2 laptop with no compiler or flags given. The run is not reproducible because the wh256 code is gone, and the decode figure is measured with about 127 of 128 originals lost, CM256's worst case.

## Use it when

- Large block counts (hundreds to 64,000 blocks; the header says N around 1000 is most efficient) where O(K\*M) Reed-Solomon such as CM256 or Longhair is too slow or capped at 255 or 256 total pieces.
- Rateless delivery: multicast or broadcast file transfer, satellite or radio links, and store-and-forward relays (wirehair_decoder_becomes_encoder) where the sender cannot know the loss rate in advance.
- Heavy-loss or code-rate-1/2 workloads, where its decode time stays flat with the number of losses while matrix Reed-Solomon decode grows with the erasure count.
- Projects that need a dependency-free C API with Python bindings, an exported CMake package and a versioned shared-library ABI.

## Skip it when

- Storage or RAID-style layouts that need an MDS guarantee: any N of N + M pieces must decode. Wirehair sometimes needs N + 1 or N + 2 packets (the README's average is N + 0.02; the large-K sweep shows 98.3 to 99.6 percent exact-N success at 10 percent loss).
- Small N (below about 128): the README itself calls it a pretty inefficient codec there compared with Fecal (catid/fecal), and N = 1 is rejected.
- Few losses on moderate N: the Fecal README measures FEC-AL encoding about 2x faster with about 100 losses at N = 1000, and 4x faster encode and 2x faster decode with about 30 losses, because Wirehair pays a full matrix solve on both sides regardless of how many repair blocks are used.
- Pure encode throughput at k = m = 128: the author's own Leopard-RS (an MDS FFT Reed-Solomon) encoded about 3x faster (1965 MB/s vs 662 MB/s) in the same table; Wirehair only won decode there.
- Adversarial channels: issue #16 raises that an attacker who knows the deterministic PRNG could choose erasures that make decoding fail well beyond N packets (RaptorQ has the same exposure), and recovered data is not authenticated.

## How it is fast

It is a hybrid LDPC / Raptor-style code: a sparse binary peeling matrix solved by an O(N) peeling decoder, a Shuffle-2 dense binary submatrix plus a 6x18 GF(256) 'heavy' submatrix to repair what peeling misses, and Gaussian elimination only on the small (about sqrt(N)) residual square matrix, followed by back-substitution (WirehairCodec.h overview). Most row operations are XORs of whole blocks; GF(256) multiply-add uses the bundled gf256 library with SSSE3 shuffles and runtime-gated AVX2, AVX-512 and GFNI paths on x86 and NEON on ARM. Per-N seeds and dense counts are precomputed offline so the matrix for every N is known to be solvable, which keeps cost roughly linear in N instead of the O(K\*M) of Cauchy Reed-Solomon.

## Compared with alternatives

No siblings catalogued yet. Within the author's own family, pick Wirehair over Leopard-RS when you need a rateless code or the fastest heavy-loss decode, and over Fecal when N is large or losses are heavy; pick Leopard when you need an MDS guarantee or maximum encode speed.

## Integration

| | |
|---|---|
| **Form** | static lib (default CMake build; BUILD_SHARED_LIBS=ON or WIREHAIR_BUILD_BOTH=ON for shared), also usable as a source drop of the gf256 and Wirehair files |
| **Dependencies** | none external; the C++ runtime and threads library are private link dependencies (pkg-config --static adds them) |
| **Minimum toolchain** | C++11 (cxx_std_11), CMake 3.15; C consumers use the C header |
| **Platforms** | x86/x86-64 with SSSE3 base and runtime-dispatched AVX2, AVX-512 and GFNI; ARM with NEON (Apple arm64 included); portable fallback; big-endian supported by the current named profiles (s390x emulation tests). ARM64 Windows support is an open issue (#31). MARCH_NATIVE=ON builds are host-specific. |
| **Thread safety** | wirehair_init() is thread-safe; codec objects are not: use one codec per thread or your own lock, and do not race wirehair_encoder_detach_input() with encoding (README). |
| **Drop-in for the baseline** | no |

## Gotchas

- Packet equations are a wire contract separate from the C ABI: the unframed legacy APIs are pinned to the 2026-07 seed-fixup profile (768 peel and 163 dense exact-N seed overrides), so packets made by a pre-fixup build can silently decode to the wrong bytes with a current build; the profile ID cannot be detected from raw packets, so carry it in trusted framing and use the explicit profile APIs.
- Decode success only means the equations were solvable: corrupted, mismatched-profile or adversarial packets can 'recover' wrong data, so verify a trusted digest or MAC after wirehair_recover (README and header).
- wirehair_encoder_create borrows the message, which must stay allocated and unchanged until the encoder is freed, reused or detached; wirehair_encoder_create_owned copies it. Legacy decoders accept at most N + 1024 distinct packet IDs and then return Wirehair_ExtraInsufficient.
- The benchmarked code is not the shipping code: the Leopard numbers came from catid/wh256, a pre-production GF256 branch now returning 404, and the encode figure appears to include the one-time encoder_create matrix solve (in the Fecal README, encode time at N = 1000 is almost the same with 99 or 31 losses: 2174 vs 2282 usec), so encode throughput is about whole-message preparation, not per-repair-packet cost.

## Known shortcomings

- Tier C: numbers match Leopard's Benchmarks.md (WH256 661.644/830.103 MB/s vs CM256 99.6658/104.651) but are first-party on an unnamed AVX2 laptop with no compiler or flags, the baseline is the author's own CM256, the benchmarked catid/wh256 repo now 404s, and the author's Leopard encodes faster (1964.98 MB/s). Filed under erasure-codes by category override.
- Enricher: the measured code (catid/wh256) is gone (404), so the numbers cannot be rerun; the WH256 encode time is mostly the one-time encoder_create matrix solve (Fecal README: N=1000 encode 2174 vs 2282 us at 99 vs 31 losses) and decode was timed at about 127 of 128 losses, CM256's worst case and Wirehair's flat case. Not MDS; Leopard encodes 3x faster in the same table; pre-2026-07 and current builds use different packet equations and raw packets cannot tell which, so mixing them can silently decode wrong bytes; recovered data is unauthenticated; issue #16 (adversarial erasure) closed with no visible maintainer reply.

## Caveats and trade-offs

First-party numbers from the same author as CM256, 'not being very rigorous' on one laptop, with no CPU model, compiler or flags, and one configuration (k=m=128, 64 KB pieces). The measured code is catid/wh256, a pre-production GF256 branch; github.com/catid/wh256 now returns 404, so the benchmarked code is not public (current Wirehair 2 is described as a pure-GF(256) API, but its equivalence to WH256 is not shown). The numbers sit in the Leopard repo, not Wirehair's. The comparison covers only the author's own codecs; in the same table the author's Leopard encodes faster (1964.98 MB/s vs 661.644 MB/s), so Wirehair is fastest only at decode. Reed-Solomon (MDS, practical only up to 255 pieces) and a fountain code (about 0.025 extra blocks of overhead on average) are not like-for-like. Baseline is the author's own CM256 rather than Jerasure, ISA-L or Zfec, and the author notes CM256's inner loops could still be improved with GF256. Wirehair's own README benchmarks only compare Wirehair 1 with Wirehair 2 (GCC 13.3, AMD Ryzen Threadripper PRO 9985WX, per docs/benchmarks/README.md) and show WH2 slower at 64-byte blocks, so they are no evidence against an outside baseline. Category erasure-codes is not one of the wave categories; filed under compression-and-encoding as the nearest domain.

Not an MDS code: needs N + 0.02 packets on average and sometimes N + 1 or N + 2 (Benchmarks.md says about a 3% chance of one extra block). Rateless fountain code for large block counts (up to 64,000). Same page shows Leopard encodes about 3x faster (1.96 GB/s) at k=m=128, and the Fecal README shows FEC-AL encoding about 2x faster than Wirehair at N=1000 with about 100 losses and 4x faster with about 30 losses (Wirehair decodes about 2x faster at 100 losses, but 2x slower at 30). The Wirehair README itself calls it a pretty inefficient codec for N below about 128 compared with Fecal. Public C API; versioned wire profiles in the current tree.

## Maintenance

Actively developed by its single author (frequent commits through 2026-09-17, a V2 codec, versioned ABI map and wire profiles), BSD-3-Clause and dependency-free, so copyable; but the speed claim rests on a undated first-party measurement of a deleted branch, and the repo's own current benchmarks compare only Wirehair 1 with Wirehair 2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Leopard's Benchmarks.md lists WH256 encode 661.644 MB/s and decode 830.103 MB/s against CM256 99.6658/104.651 MBps and Longhair 100.342/96.3757 MB/s exactly as claimed, but these are first-party numbers ('not being very rigorous') on an unnamed AVX2 laptop with no compiler or flags, and the benchmarked catid/wh256 code now returns 404, so the run is not reproducible.
- **Verifier notes:** Numbers and derived 6.6x encode / 7.9x decode ratios check out against the page. Shortcomings: first-party, unnamed laptop CPU, no compiler/flags, baseline is the author's own CM256, benchmarked wh256 repo is gone (404), and the author's Leopard beats WH256 at encode in the same table. Metadata (BSD-3-Clause, 394 stars, last commit 2026-09-17, not fork/archived) confirmed.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-55 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/catid/leopard/HEAD/Benchmarks.md>
  - <https://raw.githubusercontent.com/catid/leopard/HEAD/README.md>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/README.md>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/docs/benchmarks/README.md>
  - <https://github.com/catid/wirehair>
  - <https://github.com/catid/wirehair/commits>
  - <https://github.com/catid/wh256>
- **Sources the enricher read:**
  - <https://github.com/catid/wirehair>
  - <https://github.com/catid/wirehair/commits/master>
  - <https://github.com/catid/wirehair/tree/master/codec>
  - <https://github.com/catid/wirehair/issues?q=is%3Aissue>
  - <https://github.com/catid/wirehair/issues/16>
  - <https://github.com/catid/wirehair/issues/4>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/README.md>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/docs/benchmarks/README.md>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/include/wirehair/wirehair.h>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/WirehairCodec.h>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/gf256.h>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/codec/README.md>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/LEGACY_WIRE_PROFILES.md>
  - <https://raw.githubusercontent.com/catid/wirehair/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/catid/leopard/HEAD/Benchmarks.md>
  - <https://raw.githubusercontent.com/catid/cm256/HEAD/README.md>
  - <https://raw.githubusercontent.com/catid/cm256/HEAD/unit_test/main.cpp>
  - <https://raw.githubusercontent.com/catid/fecal/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/catid/wirehair`) · [data/wave1/enrich/raw/github_com_catid_wirehair.json](../../../data/wave1/enrich/raw/github_com_catid_wirehair.json) (enrichment confidence 0.72)

</details>
