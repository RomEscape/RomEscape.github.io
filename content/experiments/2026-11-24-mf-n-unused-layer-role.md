---
title: Middleflow가 latent 계산에 쓰지 않는 layer는 무슨 일을 하나 — CODI에서 그 layer를 빼 보기
date: 2026-11-24
project: Middleflow
status: 완료
summary: Middleflow의 latent는 L7~L13만 지나는데도 CODI와 정확도 차이가 작았습니다. 학습한 CODI에서 추론할 때만 layer를 빼 보니, 답은 latent를 주로 L7~L13에서 읽었고, latent 계산에서도 가운데 layer를 빼면 바깥 layer를 뺄 때보다 두 배 크게 떨어졌습니다. 바깥 layer는 latent를 숫자로 읽히는 모양으로 바꾸고, 질문을 읽고 답을 쓰는 데 쓰였습니다.
published: true
---

## 한 줄 요약

Middleflow가 latent 계산에서 뺀 layer(L0~L6, L14~L15)는 CODI에서도 latent에 덜 중요한 쪽이었습니다. CODI의 답은 latent를 주로 L7~L13에서 읽었고, latent 계산에서도 가운데 layer의 몫이 더 컸습니다. 바깥 layer는 latent보다 질문을 읽고 답을 쓰는 일에 쓰였습니다.

## 왜 궁금했나

Middleflow는 latent 한 step의 계산을 Llama-3.2-1B의 16개 layer 중 L7~L13의 7개로 줄였습니다. 그런데도 GSM8K 정확도는 CODI보다 2.96점만 낮았습니다(50.42, 53.37). 뺀 layer가 무슨 일을 하길래 빼도 이 정도가 나오는지 확인했습니다.

Middleflow를 설계할 때의 가설은 이렇습니다. 앞쪽 layer는 토큰을 의미 표현으로 바꾸는 "읽기"를, 뒤쪽 layer는 표현을 다음 토큰으로 바꾸는 "쓰기"를 맡고, 생각하는 계산은 가운데에서 일어납니다. latent는 이미 표현이므로 읽기와 쓰기가 필요 없다는 생각입니다. 선행 연구도 학습하지 않은 언어 모델에서 가운데 layer는 빼거나 이웃 layer와 순서를 바꿔도 크게 무너지지 않고, 앞쪽과 마지막 layer가 중요하다고 보고했습니다([Lad 외 2024](https://arxiv.org/abs/2406.19384), [Sun 외 2024](https://arxiv.org/abs/2407.09298)). 이 가설이 latent에도 맞는지 봅니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| 건너뛰기 | 그 layer를 계산하지 않고 입력을 그대로 다음 layer로 넘김. 그 layer에는 latent의 KV가 남지 않아 답도 거기서 latent를 못 봄 | 예: "앞쪽 건너뜀"은 latent가 L7~L15만 지남 |
| 답이 latent를 본다 | 답 토큰이 attention으로 그 layer에 남은 latent의 KV를 읽음 | 그대로면 CODI는 L0~L15, Middleflow는 L7~L13 |
| 가림 | latent 계산은 그대로 두고, 답 토큰의 attention에서 latent 칸만 지움 | "답은 L7~L13에서만 봄"은 바깥 9개 layer에서 가림 |
| 변화량 | layer 하나를 지나기 전후 표현의 차이 크기를 지나기 전 크기로 나눈 값 | 0에 가까우면 그 layer가 latent를 거의 바꾸지 않음 |
| logit lens | 가운데 layer의 표현을 마지막 정규화와 출력층에 바로 넣어, 어느 토큰에 가까운지 보는 방법 | 맨 위 토큰이 그 문항 풀이의 중간 계산값과 같으면 "읽힘" |
| LoRA 끄기 | 학습으로 더한 가중치 변화(LoRA)를 그 layer에서만 0으로 되돌림 | 그 layer는 학습 전 Llama 가중치로 돌아감 |

## 실험 방법

1. 다시 학습하지 않습니다. 10 epoch CODI(latent가 L0~L15를 지남)와 Middleflow(L7~L13) 저장본으로 추론할 때만 바꿉니다. 원래 코드는 고치지 않고, 추론 때 쓰는 하위 클래스만 새로 만들었습니다.
2. 아무것도 바꾸지 않으면 원래 채점과 네 벤치마크 3,818문항의 답이 모두 같은지 먼저 확인했습니다(CODI, Middleflow 모두 같음). 작은 무작위 모델로 하는 시험 6개도 통과했습니다. 예를 들어 답에서 latent를 모두 가리면, latent 계산 없이 position만 띄운 결과와 같아야 하는데 실제로 같았습니다.
3. 네 벤치마크(GSM8K, SVAMP, MultiArith, GSM-Hard)와 GSM-Symbolic main, P1을 풀었습니다. GSM-Symbolic은 latent의 몫이 드러났던 묶음입니다([더 어려운 문제 기록](2026-11-24-mf-k-harder-benchmarks.html)). 비교 기준은 같은 GPU에서 잰 "그대로"입니다.
4. 변화량과 logit lens는 GSM8K 앞 256문항, latent 6개에서 쟀습니다.

[![CODI와 Middleflow 저장본에서 추론 때 바꾼 조건: latent가 지나는 layer와 답이 latent를 보는 layer](../uploads/middleflow/experiments/layer-role-conditions.png)](../uploads/middleflow/experiments/layer-role-conditions.png)

*세로는 Llama-3.2-1B의 layer(아래 L0, 위 L15)입니다. 진한 파랑은 latent를 계산하고 답이 그 layer에서 latent를 보는 칸, 연한 파랑은 계산하지만 답은 보지 못하는 칸, 빈 칸은 건너뛴 칸입니다. "둘 다 건너뜀"은 CODI 가중치로 Middleflow와 같은 경로(L7~L13)만 쓴 것입니다. 그림을 누르면 원본 크기로 열립니다.*

## 실험 예시

GSM8K 1번 문항입니다.

> Janet’s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?

풀이의 중간 계산값은 16 − 3 − 4 = **9**, 9 × 2 = **18**입니다. 두 모델의 둘째 latent를 layer마다 logit lens로 읽으면 다음과 같습니다.

| layer | L7 | L8 | L9 | L10 | L11 | L12 | L13 | L14 | L15 |
|---|---|---|---|---|---|---|---|---|---|
| CODI | ismatic | plat | ku | pedia | natur | itself | natur | **9** | **9** |
| Middleflow | aye | aye | -minus | -minus | -minus | -minus | -remove | (지나지 않음) | (지나지 않음) |

CODI에서는 중간값 9가 마지막 두 layer(L14, L15)에서야 읽힙니다. CODI의 넷째 latent도 L14, L15에서 9로 읽혔습니다. Middleflow는 latent가 L13에서 끝나는데, 같은 위치에서 "-minus", "-remove"처럼 빼기를 가리키는 토큰이 읽힙니다. 문항 하나의 예이며, 전체 비율은 아래 결과에 있습니다.

## 결과

**1. 답이 latent를 읽는 layer (CODI 저장본, latent 계산은 그대로).**

| 조건 | GSM8K | SVAMP | MultiArith | GSM-Hard | GSM-Symbolic main | P1 |
|---|---:|---:|---:|---:|---:|---:|
| 그대로 | 53.37 | 59.40 | 98.33 | 12.96 | 33.78 | 12.86 |
| 답은 L7~L13에서만 봄 | **−2.9** | +0.6 | **−6.1** | **−0.8** | **−1.8** | −0.3 |
| 답은 바깥 layer에서만 봄 | **−21.5** | −2.1 | **−38.9** | **−5.3** | **−17.8** | **−7.4** |
| 답은 latent를 못 봄 | **−17.2** | **−4.7** | **−59.4** | **−4.1** | **−10.9** | +0.2 |

**2. latent 계산에서 건너뛴 layer (CODI 저장본).**

| 조건 | latent가 지나는 layer 수 | GSM8K | SVAMP | MultiArith | GSM-Hard | GSM-Symbolic main | P1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 앞쪽 L0~L6 건너뜀 | 9 | **−8.7** | +0.8 | **−2.8** | **−2.6** | **−6.9** | **−3.3** |
| 뒤쪽 L14~L15 건너뜀 | 14 | **−7.0** | −1.1 | **−8.3** | **−2.0** | **−7.7** | **−2.3** |
| 둘 다 건너뜀 (Middleflow 경로) | 7 | **−11.9** | −1.6 | **−12.8** | **−4.0** | **−10.6** | **−4.9** |
| 대조: 가운데 L4~L12 건너뜀 | 7 | **−24.3** | −2.3 | **−53.9** | **−6.1** | **−19.3** | **−6.9** |
| 참고: Middleflow로 학습한 모델 − CODI | 7 | **−3.0** | +0.6 | +0.6 | **−2.0** | **−5.0** | −0.8 |

**3. Middleflow 저장본에서 더 줄이거나 가리기.**

| 조건 | latent가 지나는 layer | GSM8K | SVAMP | MultiArith | GSM-Hard |
|---|---|---:|---:|---:|---:|
| 그대로 | L7~L13 | 50.42 | 60.00 | 98.89 | 10.99 |
| 앞 3개 건너뜀 | L10~L13 | **−3.6** | **−1.4** | −1.1 | −0.2 |
| 뒤 3개 건너뜀 | L7~L10 | **−5.8** | −1.3 | **−3.9** | **−1.0** |
| 답은 latent를 못 봄 | L7~L13 | **−4.3** | **−2.6** | **−15.6** | −0.9 |

**4. 학습으로 바뀐 몫(LoRA) 끄기 (GSM8K, 그대로 대비).**

| 끈 layer | CODI | Middleflow |
|---|---:|---:|
| 앞쪽 L0~L6 | **−31.6** | **−31.5** |
| 뒤쪽 L14~L15 | **−37.6** | **−47.5** |
| 가운데 L7~L13 | **−52.5** | **−47.8** |

[![조건별 정확도 변화, layer마다 latent가 바뀌는 정도, 중간 계산값으로 읽히는 비율](../uploads/middleflow/experiments/layer-role-results.png)](../uploads/middleflow/experiments/layer-role-results.png)

*왼쪽 두 그림은 CODI 저장본에서 추론 때 바꾼 것별 정확도 변화와 95% 구간입니다. 맨 아래 파란 줄은 참고로 Middleflow로 학습한 모델과 CODI의 차이입니다. 가운데 그림은 layer 하나를 지날 때 latent 표현이 바뀌는 정도이고, 점선은 비교용 답 첫 토큰입니다. 오른쪽 그림은 logit lens로 읽은 맨 위 토큰이 그 문항의 중간 계산값과 같은 비율입니다. 옅은 파란 띠는 Middleflow의 latent가 지나는 L7~L13입니다.*

**표 읽는 법.** 표 1~4의 숫자는 같은 GPU에서 잰 "그대로"보다 몇 점 높은지(음수면 낮음)를 같은 문항끼리 짝지어 계산한 값입니다. 굵은 칸은 95% 구간이 0을 포함하지 않아 차이가 있다고 보는 칸입니다. GSM-Symbolic은 같은 문제 틀에서 나온 문항끼리 비슷하므로 문제 틀 단위로 구간을 냈습니다. 표 2의 "참고" 줄만 비교가 다릅니다. 짧은 경로로 처음부터 학습한 Middleflow를 CODI와 비교했습니다.

**layer마다 바뀌는 정도와 읽히는 비율.** CODI의 latent는 앞쪽 L0~L6을 지날 때 0.06~0.30만큼 바뀌고, L7~L15에서는 0.35~0.58만큼 바뀝니다. logit lens로 중간 계산값이 읽히는 비율은 L11까지 1% 이하이다가 L12 6%, L13 10%, L14 16%, L15 18%로 오릅니다. Middleflow의 latent는 L7~L13에서 0.22~0.37만큼 바뀌고, 마지막 L13에서 중간 계산값으로 읽히는 비율은 6%입니다.

## 그래서 무슨 뜻인가

- **CODI의 답도 latent를 주로 가운데 layer에서 읽습니다.** 답이 L7~L13에서만 latent를 보게 해도 GSM8K는 2.9점만 떨어졌습니다. latent를 아예 못 보게 하면 17.2점 떨어지므로, latent 몫의 대부분이 L7~L13에서 읽힙니다. 바깥 layer에서만 보게 하면 아예 안 볼 때보다도 낮았습니다. Middleflow가 latent의 KV를 L7~L13에만 남기는 설계가 CODI의 답이 원래 쓰던 곳과 맞습니다.
- **latent 계산에서도 가운데 layer의 몫이 더 큽니다.** CODI 가중치로 바깥 9개 layer를 건너뛰면 GSM8K가 11.9점, 같은 수의 가운데 layer를 건너뛰면 24.3점 떨어졌습니다. 앞쪽 layer는 latent를 덜 바꿉니다(변화량 0.06~0.30).
- **뒤쪽 L14~L15는 latent를 숫자로 읽히는 모양으로 바꿉니다.** 중간 계산값은 CODI에서 주로 L12~L15에서 읽혔습니다(예시 문항의 9). 하지만 답은 latent를 주로 L7~L13에서 읽으므로, 이 layer를 건너뛸 때의 손실(−7.0)은 가운데를 건너뛸 때보다 작았습니다.
- **남은 차이는 학습이 메웁니다.** CODI 가중치에 Middleflow 경로만 쓰면 GSM8K가 11.9점 떨어지지만, 그 경로로 처음부터 학습한 Middleflow는 CODI보다 3.0점 낮을 뿐이었습니다.
- **"쓰지 않는 layer"는 latent에 쓰지 않을 뿐, 질문을 읽고 답을 쓰는 데는 꼭 필요합니다.** 그 layer의 LoRA를 끄면 30점 넘게 떨어졌습니다. 질문과 답 토큰은 16개 layer를 모두 지나고, 학습은 그 layer들도 함께 고쳤습니다. latent가 지나지 않는 뒤쪽 L14~L15의 LoRA를 끄면 Middleflow는 47.5점 떨어져, CODI(37.6점)보다 이 layer의 학습된 변화에 더 기댔습니다.
- **Middleflow의 7개 layer도 모두 쓰입니다.** 추론 때 3개를 더 빼면 3.6~5.8점 떨어졌고, 뒤쪽 3개(L11~L13)를 뺄 때 더 떨어졌습니다.

## 한계와 주의

- 시드 하나, 모델 하나(Llama-3.2-1B)입니다.
- 추론 때만 바꾼 결과입니다. 예를 들어 CODI 가중치로 짧은 경로를 쓰는 조합은 모델이 학습 때 겪어 보지 못한 입력이라, 그 layer가 하는 일을 정확히 재기보다 대략의 크기로 읽습니다.
- logit lens는 가운데 layer의 표현을 출력층에 바로 넣는 근사입니다. 읽히지 않는다고 그 정보가 없다는 뜻은 아닙니다.
- 변화량은 크기만 봅니다. 무엇을 바꾸는지(방향)는 알려 주지 않습니다.
- LoRA를 끈 결과는 그 layer의 학습된 변화가 필요하다는 뜻이지, 그 layer가 무슨 계산을 하는지까지 보여 주지는 않습니다.

## 일지에서의 이름

`codi_none`, `codi_answer_mid`, `codi_answer_outer`, `codi_answer_none`, `codi_skip_front`, `codi_skip_back`, `codi_skip_both`, `codi_skip_mid9`, `codi_lora_off_front`/`back`/`mid`, `mf_none`, `mf_answer_none`, `mf_skip_first3`, `mf_skip_last3`, `mf_lora_off_front`/`back`/`mid`.
