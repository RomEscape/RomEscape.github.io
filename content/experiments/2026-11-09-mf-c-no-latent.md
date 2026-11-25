---
title: latent 없이 학습한 모델(추가 실험 3)과 답 position 간격
date: 2026-11-09
project: Middleflow
status: 완료
summary: latent 계산 없이 같은 손실로 처음부터 학습한 모델이 네 벤치마크에서 CODI와 차이가 확인되지 않았고, 추론과 학습은 가장 빨랐습니다. 다만 이 모델은 답 position을 띄운 상태에 맞춰져 있어, 띄우지 않으면 풀이를 글로 쓰기 시작합니다.
published: true
---

<!-- mf-rq-start -->

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | latent 계산을 크게 줄여도(가운데 7개 layer만, 또는 latent 3개만) 정확도가 3점 안에서 남았습니다. |
| 든 의문 | latent 계산 자체가 필요한가? |
| 그때까지 안 해 본 것 | CODI 논문에는 latent 계산만 빼고 같은 손실로 학습한 모델이 없습니다(PCCoT 논문 표 1에 비슷한 기준선이 있습니다). |
| 그래서 한 것 | latent 계산 없이 답의 자리만 6칸 띄우고 같은 손실로 처음부터 학습했습니다. CODI와 Middleflow는 latent를 어디서 계산하는지만 다르므로 이 모델이 둘의 공통 대조군입니다. |
| 답 | GSM8K 52.16으로 CODI(53.37)와 차이가 확인되지 않았고, 추론과 학습이 가장 빨랐습니다. |
| 다음 의문 | 정확도는 어디서 오나([distillation 제거](2026-11-10-mf-e-distillation-and-baselines.html))? latent는 무엇을 넘기나([입력 고정](2026-11-09-mf-d-frozen-input.html))? 학습된 CODI는 latent의 내용을 쓰기는 하나([추론 때 latent 바꾸기](2026-11-12-mf-g-inference-interventions.html))? |

질문의 사슬 전체는 [연구 질문으로 다시 쓴 Middleflow 연구](2026-11-25-mf-o-research-questions.html)에 있습니다.

<!-- mf-rq-end -->

## 한 줄 요약

latent를 아예 계산하지 않고 답의 position만 6칸 띄운 모델을 CODI와 같은 손실로 학습했더니 GSM8K 52.16으로 CODI(53.37)와 차이가 확인되지 않았습니다. 추론 75.0 ms, 학습 12.3시간으로 가장 빨랐습니다.

## 왜 궁금했나

CODI와 Middleflow의 정확도가 latent 계산에서 오는지 확인하려면, latent 계산만 빼고 나머지는 같은 모델이 필요합니다. CODI와 Middleflow는 latent를 어디서 계산하는지만 다르므로, latent 계산을 빼면 둘은 같은 모델이 됩니다. 그래서 이 모델 하나가 두 방법의 공통 대조군입니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| Latent 없음 | 학습할 때도 추론할 때도 latent를 계산하지 않고 따로 학습한 모델. 학습이 끝난 CODI에서 latent를 뺀 것이 아니다 | 기본 Llama-3.2-1B-Instruct에서 출발해 10 epoch |
| 답 position 간격 | 질문 끝과 답 사이에 비워 둔 position 번호 수. latent 6개가 있을 때와 같은 번호를 답에 주려고 띄운다 | 학습 때 6 |
| 손실 세 항 | ① 교사 CE: 질문과 풀이를 보고 맞힘, ② 학생 CE: 풀이 없이 답을 맞힘, ③ distillation: 답 직전 위치에서 학생의 내부 표현을 교사와 같게 맞춤 | CODI와 같음(③의 계수 20) |

## 방법

1. latent 계산과 MLP를 빼고, 답 position 번호만 6칸 띄웠습니다. 손실 세 항, 학습 자료, 시드, 하이퍼파라미터는 CODI와 같습니다.
2. 네 벤치마크로 평가하고 CODI, Middleflow와 같은 문항끼리 짝지어 비교했습니다.
3. 따로, 학습한 이 모델의 답 position 간격을 추론 때 0, 3, 9, 12로 바꿔 봤습니다. 같은 모델을 시드 23으로 한 번 더 학습해 같은 시험을 했습니다.

[![CODI, Middleflow, Latent 없음 모델의 계산 범위](../uploads/middleflow/meeting-2026-11-12/no-latent-model.png)](../uploads/middleflow/meeting-2026-11-12/no-latent-model.png)

*Latent 없음은 latent 자리를 계산하지 않고 position 번호만 건너뜁니다. 그림의 번호는 질문이 35토큰인 문항의 예입니다.*

## 실험 예시

GSM8K 30번 문항: "Darrell and Allen's ages are in the ratio of 7:11. If their total age now is 162, calculate Allen's age 10 years from now." (정답 109)

| 조건 | 출력 | 채점 |
|---|---|---|
| Latent 없음, 학습 때와 같은 간격 6 | The answer is: 107 | 틀림 |
| 같은 모델, 간격 0 | 7+11=18>> <<11/18*162=99>>The answer is: 109 | 맞음. 풀이를 글로 씀 |

간격을 0으로 두면 모델은 학습 자료의 풀이 형식(`<<계산식>>`)으로 계산식을 쓴 뒤 답했습니다.

## 결과

| 모델 | GSM8K | SVAMP | MultiArith | GSM-Hard | 추론, 학습 시간 |
|---|---:|---:|---:|---:|---|
| CODI | 53.37 | 59.40 | 98.33 | 12.96 | 127.9 ms, 19.1시간 |
| Middleflow | 50.42 | 60.00 | 98.89 | 10.99 | 98.4 ms, 15.0시간 |
| Latent 없음 | 52.16 | 57.60 | 97.78 | 12.28 | 75.0 ms, 12.3시간 |

| 짝차이 | GSM8K | SVAMP | MultiArith | GSM-Hard |
|---|---|---|---|---|
| CODI − Latent 없음 | +1.21 [−1.11, +3.53] | +1.80 [−0.52, +4.12] | +0.56 [−1.88, +2.99] | +0.68 [−0.46, +1.82] |
| Middleflow − Latent 없음 | −1.74 [−3.92, +0.43] | +2.40 [+0.31, +4.49] | +1.11 [−1.06, +3.28] | −1.29 [−2.37, −0.21] |

[![답 position 간격에 따른 정확도와 출력 길이](../uploads/middleflow/experiments/position-gap-mode.png)](../uploads/middleflow/experiments/position-gap-mode.png)

| 추론 때 간격 | 0 | 3 | 6 (학습) | 9 | 12 |
|---|---:|---:|---:|---:|---:|
| GSM8K, 시드 11 | 57.85 | 51.55 | 52.16 | 51.78 | 52.08 |
| 평균 출력 토큰 | 22.4 | 7.2 | 7.2 | 7.2 | 7.2 |

**표 읽는 법.** CODI − Latent 없음은 네 벤치마크 모두 양수지만 구간이 모두 0을 포함해 "차이 확인 안 됨"입니다. 간격 0의 57.85는 1,319문항 중 818문항에서 계산식을 글로 쓴 결과라, latent 없이 답만 쓴 정확도와 나란히 놓으면 안 됩니다. 간격 3 이상은 답만 썼고 학습한 간격 6과 같았습니다.

## 그래서 무슨 뜻인가

- 이 모델과 이 과제에서는 latent 계산이 정확도에 더하는 몫이 확인되지 않았습니다. 같은 현상은 PCCoT 논문(arXiv 2506.18582) 표 1의 Llama-1B 기준선에도 있습니다.
- 그렇다고 "latent는 의미 없다"는 뜻은 아닙니다. 같은 표에서 GPT-2 Small은 latent 계산이 약 9점을 더했습니다. 계산 여유가 부족한 모델에서는 latent가 필요할 수 있습니다.
- latent가 없으면 학습과 추론이 가장 빠르지만, 추론 때 latent 수를 늘려 더 생각하게 할 수 없고, 중간 상태를 들여다볼 수도 없습니다.
- 이 모델의 정확도가 어디서 오는지는 [distillation 제거 기록](2026-11-10-mf-e-distillation-and-baselines.html)에서 봅니다.

## 한계

- 시드 11의 결과가 주이고, 시드 23은 GSM8K 50.72, GSM-Hard 11.22로 1점 남짓 낮았습니다. 1점 차이는 시드만 바꿔도 생깁니다.

## 일지에서의 이름

`ablation_position_gap_seed11`, `ablation_position_gap_seed23`, 간격 실험 `pg11_gap*`, `pg23_gap*`.
