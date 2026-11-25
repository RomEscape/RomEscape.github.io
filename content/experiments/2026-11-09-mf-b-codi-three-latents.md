---
title: 같은 계산량의 CODI(latent 3개)와 추론 때 latent 수 바꾸기
date: 2026-11-09
project: Middleflow
status: 완료
summary: CODI를 latent 3개로 처음부터 학습하면 계산량이 Middleflow와 비슷해지고, 속도와 정확도도 Middleflow와 차이가 확인되지 않았습니다. 학습된 모델의 latent 수를 추론 때 바꾸면 학습 때 쓴 수에서 가장 높았습니다.
published: true
---

<!-- mf-rq-start -->

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | Middleflow의 속도는 latent가 지나는 layer 횟수가 96번에서 42번으로 준 데서 나왔습니다. |
| 든 의문 | CODI의 latent 수를 6개에서 3개로 줄여도 48번이 됩니다. 그러면 같은 속도와 정확도가 나오지 않을까? 독자가 가장 먼저 물을 질문입니다. |
| 그때까지 안 해 본 것 | 같은 추론 계산량에서 "latent가 지나는 layer를 줄이기"와 "latent 수를 줄이기"를 견준 적이 없었습니다. |
| 그래서 한 것 | latent 3개 CODI를 처음부터 학습했고, 학습한 모델들의 latent 수를 추론 때만 0~12개로 바꿔 봤습니다. |
| 답 | 같은 추론 계산량이면 둘은 같았습니다(속도, 정확도 모두 차이 확인 안 됨). 추론 때만 latent를 늘려도 정확도는 오르지 않았습니다(Middleflow에 12개를 주면 48.45). |
| 다음 의문 | latent를 절반으로 줄여도, 가운데로 좁혀도 정확도가 거의 같습니다. latent 계산은 정확도에 얼마나 보태는가([Latent 없음](2026-11-09-mf-c-no-latent.html))? |

질문의 사슬 전체는 [연구 질문으로 다시 쓴 Middleflow 연구](2026-11-25-mf-o-research-questions.html)에 있습니다.

<!-- mf-rq-end -->

## 한 줄 요약

"속도만 원하면 CODI의 latent 수를 줄이면 되지 않느냐"는 질문에 답하려고 latent 3개 CODI를 학습했습니다. 추론 100.0 ms, 학습 15.4시간으로 Middleflow(98.4 ms, 15.0시간)와 거의 같았고, 네 벤치마크 정확도도 차이가 확인되지 않았습니다.

## 왜 궁금했나

Middleflow가 빠른 이유는 latent 계산 횟수가 96번에서 42번으로 줄었기 때문입니다. 그런데 CODI의 latent를 6개에서 3개로 줄여도 48번이 됩니다. 이 둘이 같다면 Middleflow의 속도 이점은 Middleflow만의 것이 아닙니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| latent 수 (학습 때) | 학습할 때 문항마다 만든 latent 개수 | CODI 6개, latent 3개 CODI 3개, Middleflow 6개 |
| latent 수 (추론 때) | 이미 학습한 모델로 문제를 풀 때 만드는 latent 개수. 학습을 다시 하지 않고 바꿀 수 있다 | 0, 1, 3, 6, 9, 12개 |
| latent 계산 횟수 | latent 수 × latent 하나가 지나는 layer 수 | CODI 96, latent 3개 CODI 48, Middleflow 42 |

## 방법

1. CODI 구조(L15에서 뽑아 L0에 넣음)는 그대로 두고 latent만 3개로 바꿔 처음부터 학습했습니다. 나머지 설정은 CODI와 같습니다. 추론도 3개로 했습니다.
2. 따로, 이미 학습한 CODI(6개), Middleflow(6개), latent 3개 CODI의 추론 latent 수를 0~12개로 바꿔 네 벤치마크를 다시 풀게 했습니다. 이 부분은 학습을 다시 하지 않은 추론 때만의 변화입니다.

[![latent 6개 CODI, latent 3개 CODI, Middleflow의 latent 계산 칸 비교](../uploads/middleflow/experiments/codi-three-latents.png)](../uploads/middleflow/experiments/codi-three-latents.png)

*색칠한 칸의 수가 latent 계산 횟수입니다.*

## 실험 예시

GSM8K 195번 문항: "A pen costs as much as a pencil and eraser combined. A pencil costs $1.20 and an eraser costs $0.30. How much will 8 pens cost?" (정답 12)

학습한 CODI(6개)의 추론 latent 수를 바꾸면 이렇게 답했습니다.

| 추론 때 latent 수 | 출력 | 채점 |
|---|---|---|
| 0개 | 1.50 | 틀림. 펜 한 자루 값에서 멈춤 |
| 3개 | 1.60 | 틀림 |
| 6개 (학습과 같음) | The answer is: 12 | 맞음 |

latent 수가 학습 때보다 적으면 한 단계 값에서 멈추거나 답 형식("The answer is:")조차 쓰지 못했습니다.

## 결과

**같은 계산량 비교 (모두 학습 때와 같은 latent 수로 추론).**

| 모델 | latent 계산 | GSM8K | SVAMP | MultiArith | GSM-Hard | 추론, 학습 시간 |
|---|---:|---:|---:|---:|---:|---|
| CODI | 96 | 53.37 | 59.40 | 98.33 | 12.96 | 127.9 ms, 19.1시간 |
| CODI, latent 3개 | 48 | 51.55 | 60.80 | 97.22 | 11.90 | 100.0 ms, 15.4시간 |
| Middleflow | 42 | 50.42 | 60.00 | 98.89 | 10.99 | 98.4 ms, 15.0시간 |

Middleflow − latent 3개 CODI는 GSM8K −1.14 [−3.27, +1.00], SVAMP −0.80 [−2.95, +1.35], MultiArith +1.67 [−0.76, +4.09], GSM-Hard −0.91 [−1.87, +0.05]로 네 벤치마크 모두 차이가 확인되지 않았습니다.

**추론 때 latent 수 바꾸기 (GSM8K).**

| 추론 때 latent 수 | 0 | 1 | 3 | 6 | 9 | 12 |
|---|---:|---:|---:|---:|---:|---:|
| CODI (6개로 학습) | 36.16 | 36.09 | 45.94 | **53.37** | 53.07 | 52.31 |
| Middleflow (6개로 학습) | 35.10 | 40.18 | 47.76 | **50.42** | 49.89 | 48.45 |
| CODI (3개로 학습) | 34.50 | 35.78 | **51.55** | 39.58 | 39.27 | – |

[![추론 때 latent 수에 따른 GSM8K 정확도](../uploads/middleflow/experiments/latent-count-at-inference.png)](../uploads/middleflow/experiments/latent-count-at-inference.png)

**표 읽는 법.** 굵은 값이 학습 때 쓴 latent 수입니다. 그보다 적으면 떨어지고, 많아도 오르지 않았습니다. 3개로 학습한 CODI는 6개 이상으로 늘리면 오히려 12점 떨어졌습니다.

## 그래서 무슨 뜻인가

- 지금 결과로는 Middleflow의 속도 이점을 CODI의 latent 수를 줄이는 것으로도 얻을 수 있습니다.
- 모델은 학습 때 쓴 latent 수에 맞춰져 있습니다. 추론 때 latent를 더 주어도 더 생각하지는 않았습니다.
- latent 0개는 latent 계산도 없고 답의 position도 띄우지 않은 조건입니다. 이때 CODI의 37.6%, Middleflow의 31.7%가 답 앞에 계산식을 글로 썼습니다. 그래서 0개 값은 "생각 없이 답한 정확도"와 같지 않습니다.

## 한계

- Middleflow를 latent 3개로 학습한 모델은 없습니다. latent 수 자체의 효과를 Middleflow에서 보려면 필요합니다.
- latent 3개 CODI의 학습은 중간에 저장 뒤 이어 학습했고, 마지막 1 step(29,989/29,990)이 덜 돌았습니다. 마지막 학습률이 거의 0이라 결과에 영향은 없다고 봅니다.
- 시드 하나입니다.

## 일지에서의 이름

`codi_r16_w0_thought3_seed11`, 추론 latent 수 실험은 `budget_sweep`과 `codi3_thoughts*`.
