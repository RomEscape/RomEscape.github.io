---
title: 더 어려운 문제에서 latent의 몫 — AIME는 바닥, GSM-Symbolic에서는 latent 쪽이 앞섬
date: 2026-11-24
project: Middleflow
status: 진행 중
summary: GSM8K에서는 latent 없이 학습한 모델과 CODI의 차이가 확인되지 않았습니다. 이름과 숫자를 바꾼 GSM-Symbolic에서는 CODI가 4.8점, 풀이 단계를 하나 더한 문제에서는 CODI가 3.0점, Middleflow가 2.0점 앞섰습니다. 첫 layer에 넣는 L13→L0은 GSM8K에서는 CODI와 같았지만 GSM-Symbolic에서는 CODI보다 낮았습니다. AIME는 모든 모델이 0점 근처라 비교할 수 없었습니다.
published: true
---

<!-- mf-rq-start -->

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | GSM8K에서는 latent 없이 학습한 모델과 CODI의 차이가 확인되지 않았고, 풀이 단계별로 나눠도 판정할 수 없었습니다. |
| 든 의문 | 학습 자료가 GSM8K 학습 문항에서 만들어져, 익숙한 모양의 문항은 latent 없이도 맞히는 것 아닐까? 이름과 숫자를 바꾸거나 단계를 더한 문항에서는 latent의 몫이 드러나야 합니다. |
| 그때까지 안 해 본 것 | 같은 모델들을 GSM-Symbolic(같은 문항 틀에서 이름과 숫자를 바꾼 main, 단계를 더한 P1, P2)과 AIME로 견준 적이 없었습니다. |
| 그래서 한 것 | Llama-1B 아홉 모델을 GSM-Symbolic 세 세트(12,500문항)와 AIME24, AIME25로 평가했습니다. |
| 답 | AIME는 모두 0점이었습니다. GSM-Symbolic main에서는 CODI가 Latent 없음보다 4.8점 높았습니다. GSM8K에서 CODI와 같던 L13→L0은 바뀐 문항에서 2.5점 낮았습니다. |
| 다음 의문 | CODI와 Latent 없음의 정확도가 다른 모델에서 Middleflow의 정확도는 어디에 놓이는가([GPT-2 Small](2026-11-24-mf-j-gpt2-plan.html))? |

질문의 사슬 전체는 [연구 질문으로 다시 쓴 Middleflow 연구](2026-11-25-mf-o-research-questions.html)에 있습니다.

<!-- mf-rq-end -->

## 한 줄 요약

latent가 "어려운 문제에 강한가"를 보려고 더 어려운 벤치마크로 평가했습니다. 경시 문제(AIME)는 모든 모델이 0점 근처였습니다. GSM8K 문제의 이름과 숫자를 바꾸고 풀이 단계를 더한 GSM-Symbolic에서는, GSM8K에서 확인되지 않던 CODI와 Latent 없음의 차이가 나타났습니다.

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
2. AIME와 GSM-Symbolic 모두 Middleflow 계열 9개 변형을 평가했습니다. GSM-Symbolic의 마지막 네 변형(띄엄 배치, CODI latent 3개, 입력 고정, Distillation 제거)은 11월 24일 밤에 끝났습니다.

## 실험 예시

GSM-Symbolic의 같은 문제 틀에서 나온 두 문항입니다.

[![GSM-Symbolic 같은 틀의 main 문항과 P1 문항, 네 모델의 답](../uploads/middleflow/experiments/gsm-symbolic-example.png)](../uploads/middleflow/experiments/gsm-symbolic-example.png)

*왼쪽은 이름과 숫자를 바꾼 main 문항, 오른쪽은 같은 틀에 풀이 단계를 하나 더한 P1 문항입니다. 가운데 상자는 정답 풀이의 단계이고, 아래는 Llama-1B 네 모델(10 epoch, 시드 11)이 실제로 쓴 답입니다. 빨간 네모가 틀린 답입니다.*

**main (2단계, 정답 6).** A juggler can juggle 120 balls. A fifth of the balls are golf balls, and a quarter of the golf balls are black. How many black golf balls are there?

**P1 (3단계, 정답 4).** A juggler can juggle 360 balls. 1/5 of the balls are tennis balls, and a third of the tennis balls are teal of which 1/6 are marked. How many marked teal tennis balls are there?

| 모델 | main의 답 | P1의 답 |
|---|---|---|
| CODI | 6 (맞음) | 4 (맞음) |
| Middleflow | 6 (맞음) | 4 (맞음) |
| Latent 없음 | 6 (맞음) | 6 (틀림) |
| L13→L0 | 6 (맞음) | 4 (맞음) |

P1 문항은 360 ÷ 5 = 72, 72 ÷ 3 = 24, 24 ÷ 6 = 4로 세 번 차례로 계산해야 합니다. 단계가 하나 늘자 latent가 없는 모델만 틀렸습니다.

## 결과

**AIME (9개 변형 모두).** CODI, L13→L0, L13→L4, 띄엄 배치, CODI latent 3개, 입력 고정은 두 시험 모두 0/30이었습니다. Middleflow, Latent 없음, Distillation 제거는 AIME24에서 1/30이었는데, 세 모델이 맞힌 것은 모두 같은 문항(정답 25)이었습니다. 초등 수준 문장제로만 학습한 1B 모델이라 경시 문제는 모두 바닥이며, 이 시험으로는 비교할 수 없습니다.

**11월 26일에 더한 AIME 평가.** 그 뒤에 학습한 모델(L6→L0, Middleflow latent 14개, 같은 학습 시간 Middleflow, 같은 학습 시간 Latent 없음)은 두 시험 모두 0/30이었습니다. 학습은 그대로 두고 추론 때만 latent 수를 바꾼 조건은 AIME24에서 CODI 6 → 3개 0/30, Middleflow 6 → 14개 1/30(원래 Middleflow가 맞힌 것과 같은 문항), 같은 학습 시간 Middleflow 6 → 14개 0/30이었고, AIME25는 셋 다 0/30이었습니다. GPT-2 Small의 CODI와 Middleflow는 두 시험 모두 0/30입니다. GPT-2 Middleflow의 AIME25는 질문과 생성 길이의 합이 GPT-2의 위치 한도(1,024)를 넘어 처음 평가가 멈췄고, 생성 길이를 한도 안으로 줄여 다시 평가했습니다. 여전히 모든 모델이 바닥입니다.

**GSM-Symbolic 정확도(%).**

| 모델 | main | P1 | P2 |
|---|---:|---:|---:|
| CODI | 33.82 | 12.96 | 3.96 |
| Middleflow (L13→L7) | 28.82 | 12.00 | 4.76 |
| Latent 없음 | 29.02 | 9.98 | 3.52 |
| L13→L0 | 31.32 | 11.18 | 3.88 |
| L13→L4 | 31.42 | 12.68 | 4.72 |
| 띄엄 1, 3, …, 13 | 28.24 | 11.96 | 3.76 |
| CODI latent 3개 | 31.46 | 12.20 | 5.32 |
| 입력 고정 | 25.84 | 9.08 | 3.08 |
| Distillation 제거 | 17.82 | 5.64 | 3.56 |

**같은 문항 짝차이(문제 틀 단위 95% 구간).**

| 비교 | main | P1 | P2 |
|---|---|---|---|
| CODI − Latent 없음 | **+4.80 [+1.80, +8.08]** | **+2.98 [+0.48, +5.70]** | +0.44 [−1.28, +2.24] |
| Middleflow − Latent 없음 | −0.20 [−2.24, +1.86] | **+2.02 [+0.18, +4.12]** | +1.24 [−0.16, +2.80] |
| CODI − Middleflow | **+5.00 [+2.34, +7.92]** | +0.96 [−0.62, +2.64] | −0.80 [−2.40, +0.64] |
| L13→L0 − Latent 없음 | +2.30 [−0.40, +5.20] | +1.20 [−0.64, +3.34] | +0.36 [−1.04, +1.76] |
| L13→L0 − CODI | **−2.50 [−4.86, −0.26]** | **−1.78 [−3.62, −0.12]** | −0.08 [−2.04, +1.68] |
| L13→L4 − Latent 없음 | +2.40 [−0.04, +5.00] | **+2.70 [+0.32, +5.26]** | +1.20 [−0.56, +3.20] |
| 띄엄 1, 3, …, 13 − Middleflow | −0.58 [−2.68, +1.30] | −0.04 [−1.18, +1.22] | −1.00 [−2.76, +0.56] |
| CODI latent 3개 − Middleflow (같은 계산량) | +2.64 [−0.12, +5.36] | +0.20 [−2.00, +2.76] | +0.56 [−1.68, +3.40] |
| 입력 고정 − Middleflow | **−2.98 [−5.64, −0.70]** | **−2.92 [−5.26, −0.90]** | **−1.68 [−3.44, −0.28]** |
| Latent 없음 − Distillation 제거 | **+11.20 [+7.74, +15.16]** | **+4.34 [+2.06, +6.88]** | −0.04 [−1.96, +2.16] |

[![GSM-Symbolic에서 각 모델과 Latent 없음의 짝차이](../uploads/middleflow/experiments/gsm-symbolic-diff.png)](../uploads/middleflow/experiments/gsm-symbolic-diff.png)

*각 모델이 Latent 없음보다 몇 점 높은지와 문제 틀 단위 95% 구간입니다. 채운 점은 구간이 0을 포함하지 않는 칸입니다. Latent 없음을 뺀 8개 모델을 모두 그렸습니다(11월 24일 밤).*

**표 읽는 법.** 앞 모델이 맞히고 뒤 모델이 틀린 문항 비율에서 그 반대 비율을 뺀 값(점)입니다. 괄호는 문제 틀을 4,000번 다시 뽑아 구한 95% 구간(시드 0)이고, 굵은 칸은 구간이 0을 포함하지 않아 차이가 있다고 보는 칸입니다. GSM8K에서 CODI − Latent 없음은 +1.21 [−1.11, +3.53]로 확인되지 않았습니다. P2는 세 모델 모두 4% 안팎이라 차이를 가릴 수 없습니다.

## 그래서 무슨 뜻인가

- GSM8K 시험 문항 그대로는 latent의 몫이 보이지 않았지만, 이름과 숫자를 바꾼 문항과 풀이 단계를 더한 문항에서는 latent가 있는 모델이 앞섰습니다. "latent는 의미가 없다"가 아니라, **익숙한 문항에서는 latent 없이도 맞히고, 바뀐 문항과 더 긴 풀이에서 latent의 몫이 드러난다**는 쪽의 근거입니다.
- Middleflow는 원래 난도에서는 CODI보다 5점 낮지만, 단계를 하나 더한 문항에서는 CODI와 차이가 확인되지 않고 Latent 없음보다 높았습니다.
- 첫 layer에 넣는 L13→L0은 GSM8K에서 CODI와 같았지만(53.07, 53.37, 짝차이 −0.30 [−2.39, +1.79]), GSM-Symbolic main과 P1에서는 CODI보다 2.5점, 1.8점 낮았고 Latent 없음과의 차이는 확인되지 않았습니다. GSM8K에서 같던 두 모델이 바뀐 문항에서는 갈렸습니다.
- 마지막 네 변형: 첫 latent(z1)만 되풀이해 넣는 입력 고정은 main, P1, P2 모두 Middleflow보다 낮았습니다(−2.98, −2.92, −1.68). GSM8K에서 낮았던 것(−3.64 [−5.77, −1.51])과 같은 방향입니다. Distillation을 빼고 학습한 모델은 main에서 Latent 없음보다 11.20점 낮아, GSM8K(15.47점 낮음)처럼 정확도의 큰 몫이 distillation과 함께 움직였습니다. Middleflow와 latent 계산량이 같은 CODI latent 3개(main +2.64 [−0.12, +5.36])와 띄엄 배치(main −0.58 [−2.68, +1.30])는 Middleflow와 차이가 확인되지 않았습니다.
- 왜 GSM8K와 GSM-Symbolic의 결과가 다른지는 아직 모릅니다. 학습 자료(GSM8K-Aug)가 GSM8K 학습 문항에서 만들어져, 원래 GSM8K 문항에서는 latent 없는 모델도 익숙한 모양을 따라 맞힐 수 있다는 것이 한 가지 가설입니다.

## 한계와 남은 일

- 시드 하나입니다. 같은 틀의 문항 50개가 비슷해 문항 수만큼 독립적이지 않으므로, 틀 단위로 묶어 구간을 냈습니다.
- Llama 9개 변형의 평가는 모두 끝났습니다. 학습 시간을 CODI와 같게 맞춰 더 학습하는 Middleflow와 Latent 없음도 끝나면 같은 묶음으로 평가합니다([학습 시간 맞춤](2026-11-24-mf-m-llama-codi-time.html)).
- 선행 연구에서 latent 계산이 있는 모델과 없는 모델의 정확도가 달랐던 GPT-2 Small에서 학습 중인 모델들도 끝나면 같은 묶음으로 평가합니다([GPT-2 Small 비교](2026-11-24-mf-j-gpt2-plan.html)).
- GSM-Symbolic(apple, CC BY-NC-ND 4.0)은 평가에만 썼습니다.
