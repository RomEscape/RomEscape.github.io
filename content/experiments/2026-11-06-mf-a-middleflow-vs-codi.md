---
title: Middleflow와 CODI를 같은 설정으로 비교
date: 2026-11-06
project: Middleflow
status: 완료
idea: 후보
idea_rank: 2
method_name: Middleflow
method_examples:
  - title: 같은 문항을 latent 16개 layer와 7개 layer로 풀기
    kind: 실제 실험 예시
    problem: 'GSM8K 828번 "Mulan has $40. Her father gave her $100. She buys two pairs of jeans at $30 each and a bag for $20. How much money does Mulan have left?" (정답 60)'
    comparison: 'Llama-3.2-1B에서 CODI는 latent 6개가 각각 16개 layer를 지나고(96번), Middleflow는 L13에서 꺼내 L7에 넣어 7개 layer만 지납니다(42번). 질문과 답은 두 모델 모두 16개 layer를 지납니다.'
    assessment: '두 모델 모두 60을 맞혔습니다. 1,319문항 평균으로 Middleflow는 추론 98.4 ms로 CODI(127.9 ms)보다 23% 빨랐고 GSM8K는 2.96점 낮았습니다. GPT-2 Small에서는 같은 문항을 CODI만 맞히고 Middleflow는 80(가방 값을 빼지 않음)을 썼습니다.'
summary: latent를 가운데 7개 layer에서만 계산하는 Middleflow는 같은 설정의 CODI보다 추론이 23%, 학습이 21% 빨랐습니다. SVAMP와 MultiArith는 같았고 GSM8K는 2.96점, GSM-Hard는 1.97점 낮았습니다.
published: true
---

<!-- mf-rq-start -->

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | CODI는 latent 하나마다 마지막 layer(L15) 출력을 다음 자리의 첫 layer(L0)에 넣어 16개 layer를 모두 지납니다(latent 6개면 96번). 언어 모델 안을 들여다본 연구들은 마지막 layer 근처가 다음 토큰을 고르는 데, 처음 layer가 토큰을 문맥과 묶어 읽는 데 쓰이고, 가운데 layer는 빼거나 순서를 바꿔도 덜 무너진다고 보고했습니다([Lad 외 2024](https://arxiv.org/abs/2406.19384), [Sun 외 2024](https://arxiv.org/abs/2407.09298)). |
| 든 의문 | 마지막 layer의 출력은 다음 토큰 쪽으로 기운 표현이라 생각을 이어 가기에 깨끗한 상태가 아닐 수 있고, 첫 layer는 토큰이 아닌 latent에는 할 일이 없을 수 있습니다. latent를 가운데에서만 돌려도 같은 정확도를 더 싸게 얻지 않을까? |
| 그때까지 안 해 본 것 | CODI, Coconut, PCCoT 세 논문 모두 latent를 꺼내는 layer와 넣는 layer를 바꾼 실험이 없습니다. |
| 그래서 한 것 | 같은 코드, 같은 설정에서 꺼내는 곳(L13)과 넣는 곳(L7)만 바꾼 Middleflow를 CODI와 견줬습니다. |
| 답 | 추론 23%, 학습 21% 빨라졌습니다. SVAMP, MultiArith는 같고 GSM8K는 2.96점, GSM-Hard는 1.97점 낮았습니다. |
| 다음 의문 | 이 속도는 Middleflow만의 것인가([latent 3개 CODI](2026-11-09-mf-b-codi-three-latents.html))? 3점은 어디서 잃었나([넣는 layer](2026-11-12-mf-f-insert-layer.html), [쓰지 않는 layer](2026-11-24-mf-n-unused-layer-role.html))? |

질문의 사슬 전체는 [연구 질문으로 다시 쓴 Middleflow 연구](2026-11-25-mf-o-research-questions.html)에 있습니다.

<!-- mf-rq-end -->

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
- 다만 같은 계산량의 CODI(latent 3개)와 비교하면 속도와 정확도 모두 비슷해서, 속도 이점이 Middleflow만의 것은 아닙니다([latent 3개 CODI 기록](2026-11-09-mf-b-codi-three-latents.html)). 또 latent 없이 학습한 모델도 정확도가 같아([Latent 없음 기록](2026-11-09-mf-c-no-latent.html)), 이 모델에서는 CODI와 Latent 없음의 차이가 확인되지 않았습니다. Middleflow의 효과는 두 조건의 정확도가 다른 모델에서 다시 봐야 합니다.

## 한계

- 시드 하나, 모델 하나, 수학 문장제 네 가지입니다.
- CODI 비교 모델은 같은 코드의 전체 layer 설정이며 공식 코드를 직접 돌린 것은 아닙니다. 공식 코드와 다른 점은 latent 단계에서 질문의 왼쪽 채움 자리를 가린다는 것 하나입니다.

## 일지에서의 이름

Middleflow `middleflow_r14_w7_latent6_seed11`, CODI `codi_r16_w0_latent6_seed11` (코드 옵션 read_layer 14 / write_layer 7, read_layer 16 / write_layer 0).
