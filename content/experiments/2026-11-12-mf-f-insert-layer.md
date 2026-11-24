---
title: latent를 넣는 layer 바꾸기(추가 실험 1) — L13→L0, L13→L4, L13→L7
date: 2026-11-12
project: Middleflow
status: 완료
idea: 후보
summary: 뽑는 곳(L13)은 그대로 두고 넣는 곳을 L7, L4, L0으로 앞당겼습니다. L13→L0은 CODI와 네 벤치마크 모두 1점 안팎으로 같았고 Middleflow보다 GSM8K가 2.65점 높았습니다. latent를 마지막 layer에서 뽑을 필요는 없었습니다.
published: true
---

## 한 줄 요약

latent를 L13에서 뽑아 L0에 넣은 모델은 CODI(L15→L0)와 정확도가 같았습니다(GSM8K −0.30 [−2.39, +1.79]). 정확도를 가른 것은 뽑는 곳이 아니라 넣는 곳이었습니다.

## 왜 궁금했나

[Middleflow](2026-11-06-mf-a-middleflow-vs-codi.html)는 CODI보다 GSM8K가 3점 낮았습니다. 그 차이가 latent를 마지막 layer가 아닌 곳에서 뽑아서인지, 앞쪽 layer를 건너뛰고 넣어서인지 나눠 보려고 했습니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| 뽑는 layer | latent를 꺼내는 layer 출력 | 모두 L13 |
| 넣는 layer | 꺼낸 latent를 다음 position에서 넣는 layer 입력 | L7, L4, L0 |
| 지나는 layer | latent 하나가 계산되는 layer 수 | 7개, 10개, 14개 |
| 판정 기준 | 결과 전에 정한 규칙. 차이가 1점 이내이고 구간이 0을 포함하면 "CODI와 일치" | CODI − L13→L0 기준 |

## 방법

1. 뽑는 곳을 L13으로 고정하고 넣는 곳만 L7, L4, L0으로 바꿔 세 모델을 처음부터 따로 학습했습니다. 나머지 설정은 모두 같습니다.
2. 네 벤치마크로 평가하고, 같은 GPU 조각에서 시간을 쟀습니다.

[![L13에서 뽑아 L7, L4, L0에 넣을 때 latent가 지나는 layer](../uploads/middleflow/meeting-2026-11-12/insert-layer.png)](../uploads/middleflow/meeting-2026-11-12/insert-layer.png)

## 실험 예시

GSM8K 80번 문항: "Two girls each got 1/6 of the 24 liters of water. Then a boy got 6 liters of water. How many liters of water were left?" (정답 10)

| 모델 | 출력 | 채점 |
|---|---|---|
| CODI (L15→L0) | The answer is: 10 | 맞음 |
| L13→L0 | The answer is: 10 | 맞음 |
| L13→L4 | The answer is: 14 | 틀림. 소년 몫 6을 빼지 않은 값 |
| Middleflow (L13→L7) | The answer is: 14 | 틀림 |

## 결과

| 설정 (지나는 layer) | GSM8K | SVAMP | MultiArith | GSM-Hard | 추론, 학습 시간 |
|---|---:|---:|---:|---:|---|
| CODI L15→L0 (16개) | 53.37 | 59.40 | 98.33 | 12.96 | 127.9 ms, 19.1시간 |
| L13→L0 (14개) | 53.07 | 59.20 | 97.22 | 12.51 | 117.0 ms, 17.9시간 |
| L13→L4 (10개) | 50.64 | 58.50 | 97.22 | 12.05 | 107.7 ms, 16.3시간 |
| Middleflow L13→L7 (7개) | 50.42 | 60.00 | 98.89 | 10.99 | 98.4 ms, 15.0시간 |

| 짝차이 | GSM8K | SVAMP | MultiArith | GSM-Hard |
|---|---|---|---|---|
| L13→L0 − CODI | −0.30 [−2.39, +1.79] | −0.20 [−2.35, +1.95] | −1.11 [−3.28, +1.06] | −0.45 [−1.48, +0.57] |
| L13→L0 − Middleflow | +2.65 [+0.37, +4.94] | −0.80 [−3.12, +1.52] | −1.67 [−3.54, +0.20] | +1.52 [+0.39, +2.65] |
| L13→L4 − Middleflow | +0.23 [−1.82, +2.27] | −1.50 [−3.78, +0.78] | −1.67 [−4.09, +0.76] | +1.06 [+0.12, +2.00] |

**표 읽는 법.** L13→L0의 추론 시간은 따로 잰 측정 실행의 값입니다. 같은 실행 안에서는 CODI 125.3 ms, Middleflow 96.0 ms였으므로, L13→L0은 CODI보다 7% 빠르고 Middleflow보다 22% 느립니다. 미리 정한 기준으로 L13→L0과 CODI는 "일치"입니다.

## 그래서 무슨 뜻인가

- latent를 마지막 layer에서 뽑을 필요는 없었습니다. L13에서 뽑아도 L0에 넣으면 CODI와 같습니다.
- 넣는 곳을 L4, L7로 옮기면 GSM8K가 2~3점 낮았습니다. L4와 L7 사이는 GSM-Hard만 차이가 있었습니다.
- 넣는 곳은 정확도보다 "답이 latent에 기대는 정도"를 더 크게 바꿨습니다. 이것은 [추론 때 latent 바꾸기 기록](2026-11-12-mf-g-inference-interventions.html)에 있습니다. CODI, Coconut, PCCoT 논문에는 뽑는 layer나 넣는 layer를 바꾼 실험이 없어, 이 부분을 논문 기여 후보로 봅니다(다른 latent 분석 논문은 원문 확인 전).

## 한계

- 뽑는 곳은 L13 하나만 봤습니다.
- 이 모델에서는 latent 계산 자체의 몫이 작아([Latent 없음 기록](2026-11-09-mf-c-no-latent.html)), 넣는 곳이 정확도에 주는 영향도 작게 보일 수 있습니다.
- 시드 하나입니다.

## 일지에서의 이름

`width14_r14_w0_seed11`(L13→L0), `width10_r14_w4_seed11`(L13→L4). 코드 옵션 read_layer 14, write_layer 0, 4, 7.
