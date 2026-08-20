# DS4 Headroom128 speed study

**Verdict: OPERATIONAL_SPEED_GO_QUALITY_PARITY; ABSOLUTE_QUALITY_GATE_NOT_MET**

Entrpi ds4 v0.6.2 plus the 0731 Q2K/Q8 DSpark drafter delivered **1.62x** geometric-mean served-wall throughput across four matched fixtures on one GX10. The slowest fixture was **0.99x**. Both arms scored **21/24** on the corrected semantic rescore, with **0** paired regressions.

| Fixture | Plain | DSpark | Speedup |
|---|---:|---:|---:|
| code_merge_intervals | 21.31 | 41.29 | 1.94x |
| json_square_table | 21.50 | 46.88 | 2.18x |
| prose_tracing | 21.60 | 21.29 | 0.99x |
| reasoning_89 | 21.47 | 35.64 | 1.66x |

- Token-weighted speed: 21.52 → 30.81 served wall tok/s, 1.43x.
- DSpark draft hits: 5534/6001, 92.2% sampled acceptance. Quenches: 7.
- Exact output hash matches: 24/36 paired requests. Request payload hashes matched 36/36.
- Minimum MemAvailable: plain 18.87 GiB, DSpark 17.76 GiB.
- Maximum swap growth: plain 0.0 MiB, DSpark 13.7 MiB.

The preregistered absolute 23/24 quality gate did not pass because the target itself returned the same wrong arithmetic answer in both arms. This blocks a claim that the model passed the absolute canary suite, but it does not show a DSpark quality regression. The publishable claim is a matched speed gain with measured task-quality parity, not universal losslessness.
