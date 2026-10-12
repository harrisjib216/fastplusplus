# Faster_SGEMM_CUDA (arekpaterek)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `CUDA C++` · `no license` · ⚪ unknown

> Deleted CUDA FP32 SGEMM repository; a Show HN title claimed up to 24% over cuBLAS on an RTX 4090.

| | |
|---|---|
| **Beats** | cuBLAS FP32 SGEMM |
| **Claimed result** | Snippet only. Hacker News thread title (item 41122018, as returned by search): 'FP32 matmul of large matrices up to 24% faster than cuBLAS on a 4090'. Search-result summaries of the thread, not verified against any page I could open: 24% on 12288^2 and 16384^2 on the 4090; +13% to +21% on a 4070 TS; +56% to +76% on a T4; +9% to +23% on an H100 (4096^2 to 12288^2); up to +43% at 12288^2 on an A100. |
| **Workload** | FP32 matmul of large square matrices on an RTX 4090 (title of the Show HN thread); search-result summaries of the thread also mention other GPUs (snippet only, unverified). |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 4090 (from the thread title); other GPUs only from snippets |
| **Links** | [repository](https://github.com/arekpaterek/Faster_SGEMM_CUDA) |

## Verdict

Nothing could be verified: the only claim is the Show HN title 'FP32 matmul of large matrices up to 24% faster than cuBLAS on a 4090' (HN item 41122018, known from search results), with no opened page giving matrix sizes, CUDA or cuBLAS version, or methodology.

## Use it when

- Not usable as it stands: there is no code to build
- Keep as a lead if the repository or a fork resurfaces, for FP32 (non-tensor-core) GEMM on large square matrices on consumer Ada GPUs such as the RTX 4090
- As a pointer that cuBLAS FP32 SGEMM may leave headroom at large sizes on some GPUs, to check with your own benchmark

## Skip it when

- Any production or research use: code, license, compiler, CUDA version and benchmark harness are all unavailable
- Citing the 24% figure: it comes only from a thread title and search summaries that could not be opened
- Workloads that can use TF32, FP16 or BF16 tensor cores, where an FP32 CUDA-core SGEMM is the wrong comparison
- Small or irregular shapes: the claim, as reported, covers only large square matrices

## How it is fast

not documented: the kernel source is unavailable. The name suggests it builds on the SGEMM_CUDA kernel series (siboehm/SGEMM_CUDA, whose README ladder runs from a naive kernel to warptiling at 93.7% of cuBLAS on an A6000), but that link is inferred from the name only and that README does not mention this repository.

## Compared with alternatives

Do not pick it: it has no code. For FP32 CUDA GEMM with code, gpu-compute (beats pedantic-FP32 cuBLAS on an RTX 5080 at small sizes) is the catalogued sibling; for tensor-core GEMM see blackwell-tensorcore-kernels or CUDA-L2; otherwise stay on cuBLAS.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | not documented (repository deleted; presumably the CUDA toolkit) |
| **Minimum toolchain** | not documented |
| **Platforms** | not documented beyond NVIDIA GPUs named in the HN title (RTX 4090) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The repository 404s on github.com and raw.githubusercontent.com, and the owner's public profile shows only two 2048 forks from 2014-2015, so the code appears deleted or made private.
- Every performance number (24% on a 4090; other GPUs in search summaries) is snippet-only from an HN thread that could not be opened.

## Known shortcomings

- Repository is missing (404 on github.com and raw; the owner has only two unrelated forks; no mirror found). Numbers come only from Hacker News search snippets, so nothing could be checked.
- Re-checked by the enricher: repo still 404; every field is undocumented.

## Caveats and trade-offs

Repository https://github.com/arekpaterek/Faster_SGEMM_CUDA returns 404 (re-checked 2026-10-02 via WebFetch and raw.githubusercontent.com README on HEAD/main/master); the owner's public repositories are only two 2048-game forks (allthe2048, 2048.directory), and a WebSearch for the exact repo name found no mirror. All numbers (24% over cuBLAS on an RTX 4090, and other GPUs) come only from search-result summaries of HN item 41122018, which could not be opened. No code, compiler, flags, CUDA version or license can be checked. Baseline is cuBLAS, not OpenBLAS/MKL/Eigen/BLIS.

Unknown: the code could not be read. The repo name suggests a CUDA SGEMM kernel derived from the well-known SGEMM_CUDA worklog series, but this is inferred from the name only.

## Maintenance

Repository missing (404, re-checked 2026-10-02), so maintenance status and license are unknown and the entry is a reference-only lead at tier D.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification C, tier now D.
- **Tier reason:** No benchmark page or code could be opened: the repo returns 404 on github.com and on raw.githubusercontent.com (HEAD, main, master), and the Hacker News thread is egress-blocked, so every number is snippet-only and the record cannot stay above D.
- **Verifier notes:** Repo deleted or private: 404 on github.com and raw, owner lists only two unrelated 2048 forks, one WebSearch found no mirror. Reject as repo-missing; if the orchestrator keeps it as a lead under keep-and-document, it is tier D with has_code false.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/arekpaterek/Faster_SGEMM_CUDA>
  - <https://raw.githubusercontent.com/arekpaterek/Faster_SGEMM_CUDA/HEAD/README.md>
  - <https://raw.githubusercontent.com/arekpaterek/Faster_SGEMM_CUDA/main/README.md>
  - <https://raw.githubusercontent.com/arekpaterek/Faster_SGEMM_CUDA/master/README.md>
  - <https://github.com/arekpaterek?tab=repositories>
- **Sources the enricher read:**
  - <https://github.com/arekpaterek/Faster_SGEMM_CUDA>
  - <https://raw.githubusercontent.com/arekpaterek/Faster_SGEMM_CUDA/HEAD/README.md>
  - <https://github.com/arekpaterek?tab=repositories>
  - <https://raw.githubusercontent.com/siboehm/SGEMM_CUDA/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/arekpaterek/faster_sgemm_cuda`) · [data/wave8/enrich/raw/github_com_arekpaterek_faster_sgemm_cuda.json](../../../data/wave8/enrich/raw/github_com_arekpaterek_faster_sgemm_cuda.json) (enrichment confidence 0.3)

</details>
