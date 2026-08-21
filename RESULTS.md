# 47 tok/s result

DeepSeek V4 Flash 0731 Abliterated reached a **46.88 tok/s served-wall median**, rounded to **47 tok/s**, on one ASUS GX10 with NVIDIA GB10.

The matched plain baseline was **21.50 tok/s**. DSpark delivered a **2.18x** speedup on the structured JSON fixture.

| Arm | Run 1 | Run 2 | Run 3 | Median | Validator |
|---|---:|---:|---:|---:|---:|
| Plain baseline | 21.52 | 21.50 | 21.50 | 21.50 | 3/3 |
| DSpark | 46.88 | 46.69 | 47.03 | **46.88** | 3/3 |

## Comparison contract

- Same abliterated Headroom128 target and immutable revision
- Same Entrpi `ds4` runtime revision
- Same NVIDIA GB10 hardware
- Same structured JSON request payloads
- Same temperature-zero sampler
- One request at a time
- Three measured repetitions after warm-up
- Only treatment: `--no-spec` baseline versus DSpark
- Metric: completion tokens divided by non-streaming request wall seconds

The exact structured-output validator passed every measured run in both arms. This supports quality parity for this fixture, not a universal model-quality claim.

The complete frozen matrix, acceptance counters, safety telemetry, and broader canary results are retained in [`results/analysis.json`](results/analysis.json).
