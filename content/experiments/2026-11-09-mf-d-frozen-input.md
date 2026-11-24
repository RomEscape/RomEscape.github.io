---
title: latent 입력 고정(추가 실험 4) — step마다 바뀌는 latent 내용이 필요한가
date: 2026-11-09
project: Middleflow
status: 완료
summary: 매 step 직전 latent 대신 첫 latent만 여섯 번 넣도록 처음부터 학습하자 계산량과 속도는 같은데 GSM8K, SVAMP, MultiArith가 3~4점 떨어졌습니다. latent가 계산 자리만 주는 것이 아니라 내용도 전달한다는 뜻입니다.
published: true
---

## 한 줄 요약

latent가 step에서 step으로 정보를 넘기지 못하게 막았더니 정확도가 3~4점 떨어졌습니다. latent 내용이 아무 역할도 없는 것은 아닙니다.

## 왜 궁금했나

[latent 없이 학습한 모델](2026-11-09-mf-c-no-latent.html)도 정확도가 비슷했으므로, latent가 하는 일이 "계산할 자리를 주는 것"뿐인지 "중간 결과를 다음 step에 넘기는 것"까지인지 나눠 볼 필요가 있었습니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| z1, z2, …, z6 | step마다 다음 position에 넣는 벡터. 기본은 직전 latent의 L13 출력을 MLP에 넣어 만든다 | Middleflow는 매번 다름 |
| 입력 고정 | 질문 끝 `<bot>` 자리에서 만든 첫 벡터 z1을 여섯 step 모두에 넣음 | z1, z1, …, z1 |
| 계산량 | latent 6번 × L7~L13 7개 layer | 두 모델 같음(42번) |

## 방법

1. Middleflow 구조(L13 → L7)와 latent 6번의 L7~L13 계산은 그대로 둡니다.
2. 삽입하는 벡터만 매 step z1로 고정합니다. step 사이로 넘어가는 정보만 끊깁니다.
3. 추론 때만 바꾼 것이 아니라 학습부터 이 방식으로 처음부터 따로 학습했습니다. 나머지 설정은 Middleflow와 같습니다.

[![기본 모델은 z1~z6을 차례로 넣고, 입력 고정 모델은 z1만 반복해 넣는다](../uploads/middleflow/experiments/frozen-input.png)](../uploads/middleflow/experiments/frozen-input.png)

## 실험 예시

GSM8K 84번 문항: "A football team played 22 games. They won 8 more than they lost. How many did they win?" (정답 15)

| 모델 | 출력 | 채점 |
|---|---|---|
| Middleflow (z1~z6) | The answer is: 15 | 맞음 |
| 입력 고정 (z1 반복) | The answer is: 16 | 틀림 |

## 결과

| 모델 | GSM8K | SVAMP | MultiArith | GSM-Hard | 추론, 학습 시간 |
|---|---:|---:|---:|---:|---|
| Middleflow | 50.42 | 60.00 | 98.89 | 10.99 | 98.4 ms, 15.0시간 |
| 입력 고정 | 46.78 | 55.60 | 95.56 | 10.61 | 97.8 ms, 14.9시간 |
| 짝차이 (고정 − Middleflow) | −3.64 [−5.77, −1.51] | −4.40 [−6.72, −2.08] | −3.33 [−5.96, −0.71] | −0.38 [−1.42, +0.66] |  |

**표 읽는 법.** 시간은 같으니 차이는 계산량이 아니라 latent 내용 때문입니다. GSM-Hard만 차이가 확인되지 않았습니다.

## 그래서 무슨 뜻인가

- latent는 step 사이로 쓸모 있는 정보를 넘깁니다.
- 그런데 latent가 아예 없는 모델(52.16)은 입력 고정 모델(46.78)보다 높습니다. latent를 두되 내용을 막는 것은 latent가 없는 것보다 나빴습니다. 학습이 고정된 입력에 맞춰지면서 오히려 방해가 됐을 수 있습니다(해석).

## 한계

- CODI, Coconut, PCCoT 논문에 있는 표준 실험은 아닙니다. Middleflow 구조에서만 했고 CODI 구조에서는 하지 않았습니다.
- 시드 하나입니다.

## 일지에서의 이름

`ablation_frozen_input_seed11`.
