# Publishable X drafts

## 1. Result first

DeepSeek V4 Flash 0731 Abliterated hit 47 tok/s on one GX10.

Same checkpoint and runtime:
21.50 tok/s baseline
46.88 tok/s with DSpark
2.18x faster

3 matched runs per arm. Every structured-output validator passed.

## 2. Runtime shift

DeepSeek V4 Flash 0731 Abliterated did not need another quant to reach 47 tok/s on one GX10.

Entrpi ds4 v0.6.2 + DSpark moved the same checkpoint from 21.50 to 46.88 served tok/s.

The runtime path delivered 2.18x.

## 3. Proof compact

One GX10. DeepSeek V4 Flash 0731 Abliterated.

Plain baseline: 21.50 tok/s
DSpark: 46.88 tok/s
Gain: 2.18x

Same checkpoint, runtime, sampler, prompt bytes, and hardware. Three measured runs per arm.

## First reply

Exact revisions, reproduction scripts, frozen prompts, validators, and machine-readable results:
https://github.com/sxuff/DeepSeek-V4-Flash-0731-Abliterated-GX10
