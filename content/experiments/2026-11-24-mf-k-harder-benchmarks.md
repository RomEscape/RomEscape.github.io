---
title: 더 어려운 문제에서 latent의 몫 — AIME는 바닥, GSM-Symbolic에서는 latent 쪽이 앞섬
date: 2026-11-24
project: Middleflow
status: 진행 중
summary: GSM8K에서는 latent 없이 학습한 모델과 CODI의 차이가 확인되지 않았습니다. 이름과 숫자를 바꾼 GSM-Symbolic에서는 CODI가 4.8점, 풀이 단계를 하나 더한 문제에서는 CODI가 3.0점, Middleflow가 2.0점 앞섰습니다. AIME는 모든 모델이 0점 근처라 비교할 수 없었습니다.
published: true
---

## 한 줄 요약

latent가 "어려운 문제에 강한가"를 보려고 더 어려운 벤치마크로 평가했습니다. 경시 문제(AIME)는 모든 모델이 0점 근처였습니다. GSM8K 문제의 이름과 숫자를 바꾸고 풀이 단계를 더한 GSM-Symbolic에서는, GSM8K에서 보이지 않던 latent의 이득이 나타났습니다.

## 왜 궁금했나

[latent 없이 학습한 모델](2026-11-09-mf-c-no-latent.html)은 GSM8K 등 네 벤치마크에서 CODI와 차이가 확인되지 않았습니다. 그러나 latent가 나온 이유 중 하나는 "답 전에 계산할 자리를 더 준다"는 것이고, 그 효과는 쉬운 문제보다 여러 단계를 차례로 계산해야 하는 문제에서 나타나야 합니다. 그래서 문제를 단계적으로 어렵게 만든 벤치마크로 다시 확인했습니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| AIME24, AIME25 | 미국 수학 경시 문제. 답은 0~999 정수 | 각 30문항 |
| GSM-Symbolic main | GSM8K 시험 문항을 틀로 만들어 이름과 숫자를 바꾼 문항 | 문제 틀 100개 × 50개 = 5,000문항 |
| GSM-Symbolic P1, P2 | 같은 틀에 풀이 단계를 1개(P1), 2개(P2) 더한 문항 | P1 5,000문항, P2 2,500문항(틀 50개) |
| 문제 틀 단위 구간 | 같은 틀에서 나온 문항 50개는 서로 비슷하므로, 틀을 단위로 다시 뽑는 부트스트랩으로 구한 95% 구간 | 4,000번 다시 뽑음 |

## 방법

1. 이미 학습한 Llama-3.2-1B 모델(10 epoch, 시드 11)을 다시 학습하지 않고 그대로 평가했습니다. 각 모델의 GSM8K 평가 때 쓴 설정을 그대로 쓰고 자료만 바꿨습니다(greedy, 최대 256 토큰, 답 글의 마지막 숫자로 채점).
2. AIME는 Middleflow 계열 9개 변형, GSM-Symbolic은 CODI, Middleflow, Latent 없음, L13→L0부터 평가하고 나머지 변형은 이어서 평가하고 있습니다.

## 실험 예시

GSM-Symbolic의 같은 문제 틀에서 나온 두 문항입니다.

**main (2단계, 정답 6).** A juggler can juggle 120 balls. A fifth of the balls are golf balls, and a quarter of the golf balls are black. How many black golf balls are there?

**P1 (3단계, 정답 4).** A juggler can juggle 360 balls. 1/5 of the balls are tennis balls, and a third of the tennis balls are teal of which 1/6 are marked. How many marked teal tennis balls are there?

| 모델 | main의 답 | P1의 답 |
|---|---|---|
| CODI | 6 (맞음) | 4 (맞음) |
| Middleflow | – | 4 (맞음) |
| Latent 없음 | 6 (맞음) | 6 (틀림) |

P1 문항은 360 ÷ 5 = 72, 72 ÷ 3 = 24, 24 ÷ 6 = 4로 세 번 차례로 계산해야 합니다. 단계가 하나 늘자 latent가 없는 모델만 틀렸습니다.

## 결과

**AIME (9개 변형 모두).** CODI, L13→L0, L13→L4, 띄엄 배치, CODI latent 3개, 입력 고정은 두 시험 모두 0/30이었습니다. Middleflow, Latent 없음, Distillation 제거는 AIME24에서 1/30이었는데, 세 모델이 맞힌 것은 모두 같은 문항(정답 25)이었습니다. 초등 수준 문장제로만 학습한 1B 모델이라 경시 문제는 모두 바닥이며, 이 시험으로는 비교할 수 없습니다.

**GSM-Symbolic 정확도(%).**

| 모델 | main | P1 | P2 |
|---|---:|---:|---:|
| CODI | 33.82 | 12.96 | 3.96 |
| Middleflow (L13→L7) | 28.82 | 12.00 | 4.76 |
| Latent 없음 | 29.02 | 9.98 | 3.52 |
| L13→L0 | 평가 중 | 평가 중 | 3.88 |

**같은 문항 짝차이(문제 틀 단위 95% 구간).**

| 비교 | main | P1 | P2 |
|---|---|---|---|
| CODI − Latent 없음 | **+4.80 [+1.86, +7.94]** | **+2.98 [+0.52, +5.74]** | +0.44 [−1.36, +2.20] |
| Middleflow − Latent 없음 | −0.20 [−2.22, +1.88] | **+2.02 [+0.12, +4.10]** | +1.24 [−0.16, +2.76] |
| CODI − Middleflow | **+5.00 [+2.36, +7.84]** | +0.96 [−0.62, +2.64] | −0.80 [−2.56, +0.64] |

**표 읽는 법.** 굵은 칸은 구간이 0을 포함하지 않아 차이가 있다고 보는 칸입니다. GSM8K에서 CODI − Latent 없음은 +1.21 [−1.11, +3.53]로 확인되지 않았습니다. P2는 세 모델 모두 4% 안팎이라 차이를 가릴 수 없습니다.

## 그래서 무슨 뜻인가

- GSM8K 시험 문항 그대로는 latent의 몫이 보이지 않았지만, 이름과 숫자를 바꾼 문항과 풀이 단계를 더한 문항에서는 latent가 있는 모델이 앞섰습니다. "latent는 의미가 없다"가 아니라, **익숙한 문항에서는 latent 없이도 맞히고, 바뀐 문항과 더 긴 풀이에서 latent의 몫이 드러난다**는 쪽의 근거입니다.
- Middleflow는 원래 난도에서는 CODI보다 5점 낮지만, 단계를 하나 더한 문항에서는 CODI와 차이가 확인되지 않고 Latent 없음보다 높았습니다.
- 왜 GSM8K와 GSM-Symbolic의 결과가 다른지는 아직 모릅니다. 학습 자료(GSM8K-Aug)가 GSM8K 학습 문항에서 만들어져, 원래 GSM8K 문항에서는 latent 없는 모델도 익숙한 모양을 따라 맞힐 수 있다는 것이 한 가지 가설입니다.

## 한계와 남은 일

- 시드 하나입니다. 같은 틀의 문항 50개가 비슷해 문항 수만큼 독립적이지 않으므로, 틀 단위로 묶어 구간을 냈습니다.
- 나머지 변형(L13→L0의 main과 P1, L13→L4, 띄엄 배치, CODI latent 3개, 입력 고정, Distillation 제거)은 평가 중입니다. 끝나면 이 글을 고칩니다.
- latent가 실제로 필요하다고 보고된 GPT-2 Small에서 학습 중인 모델들도 끝나면 같은 묶음으로 평가합니다([GPT-2 Small 비교](2026-11-24-mf-j-gpt2-plan.html)).
- GSM-Symbolic(apple, CC BY-NC-ND 4.0)은 평가에만 썼습니다.
