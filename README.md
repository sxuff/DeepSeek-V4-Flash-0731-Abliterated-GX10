# DS4 Flash 0731 on one GX10

A matched serving pilot for the exact `apetersson/DeepSeek-V4-Flash-0731-Abliterated-DS4-Headroom128` target on one NVIDIA GB10.

## Result

Entrpi `ds4` v0.6.2 plus the pinned 0731 Q2K/Q8 DSpark drafter increased token-weighted served-wall throughput from **21.52 to 30.81 tok/s**, a **1.43x** gain.

Across the four frozen speed fixtures, the geometric-mean gain was **1.62x**.

| Fixture | Plain | DSpark | Speedup |
|---|---:|---:|---:|
| Code | 21.31 tok/s | 41.29 tok/s | 1.94x |
| Structured JSON | 21.50 tok/s | 46.88 tok/s | 2.18x |
| Reasoning | 21.47 tok/s | 35.64 tok/s | 1.66x |
| Prose | 21.60 tok/s | 21.29 tok/s | 0.99x |

The reported speed is `completion_tokens / non-streaming request wall time`. It is served-wall throughput, not isolated decode-kernel throughput.

## Quality verdict

- **36/36 request payload hashes matched between arms.**
- **12/12 speed outputs passed deterministic semantic validators in both arms.**
- **21/24 quality canaries passed in both arms.**
- **0 paired quality regressions.**
- **24/36 paired outputs were byte-identical.**

The absolute 23/24 quality gate did not pass because this quantized target returned the same wrong arithmetic answer, `16529`, in all three plain and all three DSpark repetitions. This blocks a claim that the model passed the absolute canary suite. It does not show a DSpark regression.

The defensible conclusion is:

> DSpark materially accelerated the exact abliterated Headroom128 target on one GX10 with measured task-quality parity. This is not a universal losslessness claim.

## Exact stack

### Target

- Repository: `apetersson/DeepSeek-V4-Flash-0731-Abliterated-DS4-Headroom128`
- Revision: `08f6c6225ab4d29a735ab7d48d46bd0a3a767a07`
- File: `DeepSeek-V4-Flash-0731-Abliterated-DS4-Headroom128.gguf`
- Bytes: `86,720,111,552`
- SHA-256: `55a46e7e9a51f3d6708559b8b284c3e60f6b97f9bab1f2c9633948c8331e99ee`

### Drafter

- Repository: `bleysg/DeepSeek-V4-Flash-DSpark-drafter-GGUF`
- Revision: `81c6fdd38f9582da45ba27f0ed7b63bcd3ea3b62`
- File: `DSpark-drafter-Q2K-Q8-0731.gguf`
- Bytes: `6,971,241,504`
- SHA-256: `8fa269560dc76fd73e4233ad9b1938b5f65dd363381fd9b1a5c6183f7d12d686`

### Runtime

- Repository: `Entrpi/ds4`
- Revision: `d183482b413ecd2e3b540b290e6497437e9fbb73`
- Version: `v0.6.2`
- Build: `make cuda-spark`
- Backend: CUDA `sm_121`
- Context: `32,768`
- Continuous banks: `2`
- Prefill chunk: `1,024`
- Memory floor: `6 GiB`

The target repository's bundled abliterated support GGUF uses the older DS4 metadata and tensor-name contract. It failed the v0.6.2 standalone validator before inference. The primary run therefore used the pinned clean 0731 drafter above. The target still verified and produced every final token.

## DSpark behavior

Across the measured run and its warm-ups:

- Draft hits: **5,534 / 6,001**
- Sampled acceptance: **92.2%**
- Terminal quenches: **7**

The quench policy kept the low-acceptance prose fixture effectively flat at `0.99x` instead of forcing a broad regression.

## Safety

| Arm | Minimum MemAvailable | Maximum swap growth | Incident |
|---|---:|---:|---|
| Plain | 18.87 GiB | 0 MiB | No |
| DSpark | 17.76 GiB | 13.75 MiB | No |

The server ran with `MemorySwapMax=0`, a 6 GiB MemAvailable floor, and an external watchdog that stopped only the experiment-owned unit if swap growth exceeded 512 MiB.

A pre-primary 65,536-context, four-bank smoke was stopped at 551,968,768 bytes of swap growth. The primary protocol was amended before any primary trace to use 32,768 context, two banks, and a 1,024-token prefill chunk. The safety threshold was not relaxed.

## Reproduce

1. Download and hash-verify the exact target and drafter above.
2. Build the pinned Entrpi runtime:

```bash
git clone https://github.com/Entrpi/ds4.git
cd ds4
git checkout --detach d183482b413ecd2e3b540b290e6497437e9fbb73
make cuda-spark
```

3. Launch the plain or DSpark arm with `scripts/serve.sh`.
4. Run the frozen fixture matrix:

```bash
python3 scripts/bench.py \
  --arm dspark_v062 \
  --base-url http://127.0.0.1:8001 \
  --fixtures protocol/fixtures.json \
  --out run/dspark \
  --repeats 3
```

The benchmark executes generated Python only in a disposable Docker sandbox with no network, a read-only root, an unprivileged user, dropped capabilities, bounded CPU, memory, PIDs, and wall time.

## Evidence map

- `results/analysis.json`: compact machine-readable result
- `RESULTS.md`: human-readable verdict
- `protocol/PROTOCOL.json`: frozen v2 protocol and safety amendment
- `protocol/fixtures.json`: exact prompt and validator manifest
- `scripts/bench.py`: request collector and deterministic validators
- `scripts/rescore.py`: post-run semantic rescore for documented validator defects
- `scripts/analyze.py`: matched analysis
- `card.png`: proof-only visual

The full private scientific archive retains raw outputs, server logs, watchdog telemetry, and superseded v1 rows. They are intentionally excluded from this compact distribution.

## Sources

- [Entrpi/ds4](https://github.com/Entrpi/ds4)
- [Entrpi/ds4-on-spark](https://github.com/Entrpi/ds4-on-spark)
- [antirez/ds4](https://github.com/antirez/ds4)
- [MiaAI-Lab DSpark recipe for 2x DGX Spark](https://github.com/MiaAI-Lab/DeepSeek-v4-Flash-DSpark-2x-DGX-Spark)
- [Headroom128 target](https://huggingface.co/apetersson/DeepSeek-V4-Flash-0731-Abliterated-DS4-Headroom128)
- [0731 Q2K/Q8 drafter](https://huggingface.co/bleysg/DeepSeek-V4-Flash-DSpark-drafter-GGUF)
