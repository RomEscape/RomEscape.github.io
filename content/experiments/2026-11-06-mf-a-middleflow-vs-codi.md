---
title: Middleflow와 CODI를 같은 설정으로 비교
date: 2026-11-06
project: Middleflow
status: 완료
idea: 후보
summary: latent를 가운데 7개 layer에서만 계산하는 Middleflow는 같은 설정의 CODI보다 추론이 23%, 학습이 21% 빨랐습니다. SVAMP와 MultiArith는 같았고 GSM8K는 2.96점, GSM-Hard는 1.97점 낮았습니다.
published: true
---

## 한 줄 요약

latent 하나가 16개 layer를 모두 지나는 CODI 대신, 가운데 7개 layer만 지나게 한 Middleflow는 계산이 56% 줄어 추론 23%, 학습 21% 빨라졌습니다. 정확도는 네 벤치마크 가운데 둘은 같고 둘은 2~3점 낮았습니다.

## 왜 궁금했나

CODI는 풀이를 글로 쓰지 않고 latent(모델 안의 벡터) 6개로 "생각"한 뒤 답합니다. 그런데 latent 하나를 만들 때마다 모델의 16개 layer를 처음부터 끝까지 다시 지납니다. 모델 안의 정보는 마지막 layer 전에 가운데 layer에서 상당 부분 만들어진다는 관찰이 있으니, latent를 가운데에서 꺼내 가운데에 다시 넣어도 같은 정확도가 나온다면 같은 생각을 더 싸게 할 수 있습니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| layer | 모델을 이루는 계산 단계. 0번부터 L0~L15로 센다 | Llama-3.2-1B-Instruct는 16개 |
| latent | 풀이 한 단계를 대신하는 모델 안의 벡터 하나. 다음 position의 입력으로 다시 넣는다 | 문항마다 6개 |
| 뽑는 layer → 넣는 layer | latent를 어느 layer 출력에서 꺼내 어느 layer 입력에 넣는지 | CODI L15→L0, Middleflow L13→L7 |
| latent 계산 횟수 | latent 수 × latent 하나가 지나는 layer 수 | CODI 6 × 16 = 96, Middleflow 6 × 7 = 42 |
| 같은 문항 짝차이 | 두 모델이 같은 문항에서 맞고 틀린 것을 짝지어 낸 정확도 차이 | 대괄호는 95% 구간. 0을 포함하면 "차이 확인 안 됨" |

## 방법

1. 같은 코드에서 뽑는 layer와 넣는 layer만 바꿔 두 모델을 만들었습니다. 뽑는 곳을 마지막, 넣는 곳을 처음으로 두면 CODI와 같아집니다. 공식 CODI의 반복과 같은 값이 나오는 것은 단위 시험으로 확인했습니다.
2. 두 모델 모두 기본 Llama-3.2-1B-Instruct에서 출발해 GSM8K-Aug(약 38만 문항의 수학 문장제와 계산식 풀이)로 처음부터 따로 학습했습니다. CODI 논문의 Llama-1B 설정을 그대로 썼습니다(LoRA r128, 학습률 8e-4, 10 epoch, latent 6개, 원본 코드의 고정 시드 11).
3. 네 벤치마크(GSM8K 1,319문항, SVAMP 1,000, MultiArith 180, GSM-Hard 1,319)를 greedy로 풀게 하고, 답 글의 마지막 숫자가 정답과 같은지 채점했습니다.
4. 같은 GPU 조각에서 문제당 추론 시간과 10 epoch 전체 학습 시간을 쟀습니다.

[![CODI는 L15 출력을 뽑아 L0에 넣고, Middleflow는 L13 출력을 뽑아 L7에 넣는다](../uploads/middleflow/meeting-2026-11-12/codi-vs-middleflow.png)](../uploads/middleflow/meeting-2026-11-12/codi-vs-middleflow.png)

*파란 칸이 latent가 계산되는 layer입니다. 질문과 답 토큰은 두 방법 모두 16개 layer를 다 지납니다.*

## 실험 예시

GSM8K 167번 문항으로 따라가 봅니다.

**실제 입력.** "Seth is twice as old as Brooke. In 2 years, the sum of their ages will be 28. How old is Seth?" (정답 16)

**조건별로 한 일.**
1. 질문 토큰을 16개 layer에 모두 통과시킵니다. 질문 끝에는 생각 시작 표시 `<bot>`이 붙습니다.
2. CODI는 `<bot>` 자리의 L15 출력을 작은 MLP에 넣어 첫 latent를 만들고, 다음 position의 L0에 넣어 16개 layer를 다시 지나게 합니다. 이것을 6번 합니다. Middleflow는 L13 출력을 뽑아 L7에 넣고 L7~L13만 지나게 합니다.
3. 생각 끝 표시 `<eot>`를 넣고 답을 씁니다. 답 토큰은 16개 layer를 모두 지나며, latent가 계산된 layer에서만 latent를 볼 수 있습니다.

**실제 출력.**

| 모델 | 출력 | 채점 |
|---|---|---|
| CODI | The answer is: 16 | 맞음 |
| Middleflow | The answer is: 18 | 틀림 |

## 결과

| 항목 | Middleflow | CODI | 차이 (Middleflow − CODI) |
|---|---:|---:|---|
| GSM8K | 50.42 | 53.37 | −2.96 [−5.09, −0.82] |
| SVAMP | 60.00 | 59.40 | +0.60 [−1.63, +2.83] |
| MultiArith | 98.89 | 98.33 | +0.56 [−1.33, +2.44] |
| GSM-Hard | 10.99 | 12.96 | −1.97 [−3.10, −0.84] |
| 추론 시간 (문제당) | 98.4 ms | 127.9 ms | 23% 적음 |
| 학습 시간 (10 epoch) | 15.0시간 | 19.1시간 | 21% 적음 |
| 추론 최대 메모리 | 2.54 GiB | 2.54 GiB | 같음 |

**표 읽는 법.** 정확도는 %입니다. 구간이 0을 포함하지 않는 GSM8K와 GSM-Hard만 차이가 있다고 봅니다. 시드가 하나라 구간 반폭이 약 2점이고, 1~2점 차이는 확정할 수 없습니다.

## 그래서 무슨 뜻인가

- latent를 가운데 layer로 좁히면 계산과 시간은 확실히 줄어듭니다.
- 정확도는 계산이 여러 단계인 GSM8K, GSM-Hard에서 조금 떨어졌습니다.
- 다만 같은 계산량의 CODI(latent 3개)와 비교하면 속도와 정확도 모두 비슷해서, 속도 이점이 Middleflow만의 것은 아닙니다([latent 3개 CODI 기록](2026-11-09-mf-b-codi-three-latents.html)). 또 latent 없이 학습한 모델도 정확도가 같아([Latent 없음 기록](2026-11-09-mf-c-no-latent.html)), 이 모델에서는 latent 계산 자체의 몫이 작습니다. Middleflow의 효과는 latent가 실제로 필요한 조건에서 다시 봐야 합니다.

## 한계

- 시드 하나, 모델 하나, 수학 문장제 네 가지입니다.
- CODI 비교 모델은 같은 코드의 전체 layer 설정이며 공식 코드를 직접 돌린 것은 아닙니다. 공식 코드와 다른 점은 latent 단계에서 질문의 왼쪽 채움 자리를 가린다는 것 하나입니다.

## 일지에서의 이름

Middleflow `middleflow_r14_w7_latent6_seed11`, CODI `codi_r16_w0_latent6_seed11` (코드 옵션 read_layer 14 / write_layer 7, read_layer 16 / write_layer 0).
