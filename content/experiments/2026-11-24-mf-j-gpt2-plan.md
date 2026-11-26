---
title: GPT-2 Small에서 같은 비교 — GSM8K는 CODI 41.47, Middleflow 37.38, Latent 없음 36.47
date: 2026-11-24
project: Middleflow
status: 진행 중
summary: Llama-1B와 달리 GPT-2 Small에서는 CODI가 Latent 없음보다 높았습니다(GSM8K +5.0점, MultiArith +24.4점). 가운데 5개 layer만 쓰는 Middleflow와 Latent 없음의 차이는 SVAMP, MultiArith에서는 그 68~74%, GSM8K, GSM-Hard에서는 0~18%였습니다. GPT-2 추가 학습(L9→L0 등)은 기존 모델 실험 뒤로 미뤘습니다.
published: true
---

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | Llama-1B에서는 latent 계산 없이 학습한 모델도 CODI와 정확도가 같아, Middleflow가 "필요 없는 계산을 줄인 것"인지 "필요한 계산을 싸게 한 것"인지 가를 수 없었습니다. PCCoT 논문 표 1에서는 같은 CODI 손실로 학습한 GPT-2 Small에서 latent 계산이 있는 모델이 없는 모델보다 약 9점 높았습니다. |
| 든 의문 | CODI와 Latent 없음의 정확도가 다른 모델에서 Middleflow의 정확도는 어디에 놓이는가? |
| 그때까지 안 해 본 것 | 같은 코드와 설정으로 GPT-2에서 CODI, Latent 없음, Middleflow를 학습해 견준 적이 없었습니다. |
| 그래서 한 것 | 코드를 GPT-2(layer 12개)로 옮기고 원본 CODI GPT-2 설정(40 epoch)으로 세 모델을 학습해 네 벤치마크, GSM-Symbolic, 추론 때 latent 바꾸기로 평가했습니다. |
| 답 | GPT-2에서는 CODI가 Latent 없음보다 높았습니다(CODI − Latent 없음이 다섯 평가 모두 0을 벗어남). Middleflow − Latent 없음은 그 차이의 일부였습니다(SVAMP 74%, MultiArith 68%, GSM-Symbolic main 39%, GSM8K 18%, GSM-Hard 0%). |
| 다음 의문 | 얕은 모델에서 latent가 몇 개 layer를 지나야 CODI와 같은 정확도가 나오는가? Llama처럼 첫 layer에 넣으면(L9→L0) CODI와 같아지는가? 이 질문에 답할 GPT-2 추가 학습은 미루고, 같은 질문을 지금까지 써 온 Llama에서 먼저 봅니다([기존 모델에서 방법 증명](2026-11-25-mf-r-llama-method-proof.html)). |

질문의 사슬 전체는 [연구 질문으로 다시 쓴 Middleflow 연구](2026-11-25-mf-o-research-questions.html)에 있습니다.

## 한 줄 요약

- GPT-2 Small에서는 CODI가 Latent 없음보다 높았습니다. CODI는 latent 없이 같은 손실로 학습한 모델보다 GSM8K 5.00점 [+2.68, +7.33], SVAMP 6.60점, MultiArith 24.44점, GSM-Hard 1.67점, GSM-Symbolic main 6.44점 높았습니다. Llama-1B에서는 이 차이가 확인되지 않았습니다.
- 가운데 5개 layer(L5~L9)만 쓰는 Middleflow와 Latent 없음의 차이는 그 일부였습니다. 풀이 단계가 적은 SVAMP(74%)와 MultiArith(68%)에서는 컸고, 단계가 많은 GSM8K(18%)와 GSM-Hard(0%)에서는 작았습니다.
- 추론 때 latent를 지우면 CODI는 11~20점, Middleflow는 6~9점 떨어졌습니다. 두 모델 모두 latent를 쓰고, Llama에서처럼 Middleflow가 덜 기댑니다.

## 왜 궁금했나

Llama-1B에서는 [latent 없이 학습한 모델](2026-11-09-mf-c-no-latent.html)이 CODI와 같아서, Middleflow의 비용 절감이 "필요 없는 계산을 줄인 것"인지 "필요한 계산을 싸게 한 것"인지 구분할 수 없었습니다. 그러나 latent 방법은 계산할 자리, 내용 전달, 교사에게서 배우는 학습 신호라는 이유로 나왔고, 첫째 이유는 계산 여유가 적은 모델에서 중요할 수 있습니다. PCCoT 논문(arXiv 2506.18582) 표 1에서 같은 CODI 손실로 학습한 GPT-2 Small은 latent 계산 48.24, 자리만 39.27, 자리 없음 37.78이었습니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| GPT-2 Small | 2019년에 공개된 작은 언어 모델. 위치 정보를 입력에서 한 번만 더함 | 매개변수 1억 2,400만 개, layer 12개(block 0~11) |
| CODI (전체 깊이) | latent를 마지막 layer의 출력에서 읽어 첫 layer의 입력에 넣는 원래 방식 | L11→L0. latent 하나가 block 12개를 모두 지남 |
| Middleflow (L9→L5) | latent를 block 9의 출력에서 읽어 block 5의 입력에 넣음 | latent 하나가 block 5~9의 5개만 지남 |
| Latent 없음 | latent 계산 없이 답 위치만 latent 6개만큼 띄워 같은 손실로 학습 | latent를 만드는 계산 0번 |
| 공개 체크포인트 | CODI 저자가 공개한 GPT-2 학습 결과 | 우리 평가 코드가 맞는지 확인하는 데만 씀 |
| 추론 때 latent 바꾸기 | 학습을 마친 모델이 답을 쓰기 전에 latent를 지우거나 바꿔, 답이 latent에 얼마나 기대는지 봄 | 지우기 4가지, 틀린 내용 넣기 2가지(아래 표) |

[![GPT-2 Small에서 학습하는 네 모델의 latent 계산 범위](../uploads/middleflow/experiments/gpt2-arms.png)](../uploads/middleflow/experiments/gpt2-arms.png)

*GPT-2 Small은 layer가 12개(L0~L11)입니다. 가로는 position(질문, latent 6개, 답), 세로는 layer이고 파란 칸이 latent를 계산하는 layer입니다. 질문과 답 토큰은 네 모델 모두 12개 layer를 다 지나고, 답 토큰은 파란 layer에서만 latent를 볼 수 있습니다. CODI, Latent 없음, Middleflow는 11월 24일부터 학습 중이고 L9→L0은 사선 경로 다음에 학습합니다. 그림을 누르면 원본 크기로 열립니다.*

## 처음에 세운 질문 (11월 24일)

1. latent 계산의 기여는 모델에 따라 달라지는가? (Llama-1B에서는 확인 안 됨, GPT-2 Small에서는?)
2. latent를 넣는 layer는 정확도와 latent 의존도를 어떻게 바꾸는가?
3. latent가 기여하는 조건에서, 가운데 layer만으로 계산해도 그 기여를 지키며 비용을 줄일 수 있는가?

## 방법

1. 우리 학습 코드를 GPT-2 구조(12개 layer, 위치 정보를 입력에서 더하는 방식)로 옮기고, 전체 깊이 설정이 원래 CODI 반복과 같은 값을 내는지 CPU 시험으로 확인합니다.
2. CODI 저자가 공개한 GPT-2 체크포인트를 우리 평가 코드로 채점해, 논문 값(GSM8K 43.7) 근처가 나오는지 봅니다.
3. CODI 원본의 GPT-2 설정(학습률 3e-3, 40 epoch, LoRA r128, latent 6개)으로 CODI, Latent 없음, Middleflow를 같은 코드, 같은 시드(11)로 학습합니다. 모델마다 GPU를 나눠 동시에 돌립니다.
4. 네 벤치마크, 추론 시간, 학습 시간, 추론 때 latent 바꾸기를 Llama-1B와 같은 방식으로 잽니다.

## 실험 예시

GSM8K 시험 문항 하나에 공개 CODI GPT-2가 쓴 답입니다. 답 글의 마지막 숫자를 정답과 비교해 채점합니다.

**문항.** An eraser costs $2 and a pencil costs $3. How much do 6 erasers and 8 pencils cost?
**정답 36.** 2 × 6 = 12, 3 × 8 = 24, 12 + 24 = 36.

| 추론 때 바꾼 것 | 모델이 쓴 답 | 채점 |
|---|---|---|
| 그대로 (latent 6개) | The answer is: 36 | 맞음 |
| latent 0개 | 12 | 틀림 |
| latent 건너뜀 (위치만 비움) | 12 | 틀림 |
| 0 벡터 | 12 | 틀림 |
| 다른 문항의 latent | The answer is: 624 | 틀림 |

latent를 비운 세 경우 모두 첫 단계의 값(2 × 6 = 12)을 답했고, 다른 문항의 latent를 넣자 이 문항과 맞지 않는 624를 답했습니다. 한 문항의 예이며, 비웠을 때 첫 단계 값만 답한 문항이 전체에서 몇 개인지는 세지 않았습니다.

## 결과를 보기 전에 정한 판정

| GPT-2 결과 | 해석 |
|---|---|
| CODI가 Latent 없음보다 높고, Middleflow가 그 차이를 대부분 지킴 | latent는 계산 여유가 적은 모델에서 필요하고, 가운데 layer만으로도 그 이득을 지키며 비용을 줄일 수 있다 |
| CODI가 높지만 Middleflow가 그 이득을 잃음 | latent는 앞쪽 layer를 지나야 쓰인다. 넣는 layer와 의존도의 관계를 뒷받침 |
| CODI와 Latent 없음이 같음 | 선행 연구와 다른 결과. 원인 분석 필요 |

## 결과 (11월 25일)

**네 벤치마크와 GSM-Symbolic (GPT-2 Small, 40 epoch, 시드 11).**

| 모델 | GSM8K | SVAMP | MultiArith | GSM-Hard | GSM-Symbolic main | P1 | P2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| CODI (L11→L0) | 41.47 | 43.10 | 95.00 | 9.55 | 22.30 | 9.92 | 4.64 |
| Middleflow (L9→L5) | 37.38 | 41.40 | 87.22 | 7.73 | 18.36 | 7.30 | 2.80 |
| Latent 없음 | 36.47 | 36.50 | 70.56 | 7.88 | 15.86 | 5.88 | 3.36 |

**같은 문항 짝차이와 95% 구간.**

| 비교 | GSM8K | SVAMP | MultiArith | GSM-Hard |
|---|---|---|---|---|
| CODI − Latent 없음 | +5.00 [+2.68, +7.33] | +6.60 [+4.27, +8.93] | +24.44 [+17.62, +31.27] | +1.67 [+0.54, +2.80] |
| Middleflow − Latent 없음 | +0.91 [−1.13, +2.95] | +4.90 [+2.95, +6.85] | +16.67 [+10.41, +22.92] | −0.15 [−1.04, +0.74] |
| Middleflow − CODI | −4.09 [−6.19, −1.99] | −1.70 [−3.78, +0.38] | −7.78 [−12.51, −3.04] | −1.82 [−2.82, −0.82] |
| (Middleflow − Latent 없음) ÷ (CODI − Latent 없음) | 18% | 74% | 68% | 0% |

| 비교 | GSM-Symbolic main | P1 | P2 |
|---|---|---|---|
| CODI − Latent 없음 | +6.44 [+3.76, +9.56] | +4.04 [+1.62, +7.16] | +1.28 [−0.60, +4.00] |
| Middleflow − Latent 없음 | +2.50 [+1.00, +4.18] | +1.42 [+0.12, +2.92] | −0.56 [−1.84, +0.64] |
| Middleflow − CODI | −3.94 [−6.66, −1.62] | −2.62 [−5.54, −0.36] | −1.84 [−5.20, +0.36] |
| (Middleflow − Latent 없음) ÷ (CODI − Latent 없음) | 39% | 35% | 0% |

**표 읽는 법.** 대괄호는 같은 문항을 두 모델이 맞혔는지 짝지어 낸 차이의 95% 구간입니다(GSM-Symbolic은 같은 문항 틀 100개 단위로 다시 뽑는 부트스트랩). 구간이 0을 포함하지 않으면 차이가 있다고 봅니다. 마지막 줄은 위 두 차이의 비율이고, Middleflow가 Latent 없음보다 낮으면 0%로 적었습니다.

[![Llama-1B와 GPT-2 Small에서 CODI, Middleflow와 Latent 없음의 정확도 차이](../uploads/middleflow/experiments/latent-gain-llama-gpt2.png)](../uploads/middleflow/experiments/latent-gain-llama-gpt2.png)

*파란 막대는 CODI, 주황 막대는 Middleflow가 Latent 없음보다 높은 정도입니다. 막대 끝의 선은 95% 구간, *는 구간이 0을 벗어난 것입니다. 왼쪽 Llama-1B는 GSM-Symbolic main만 CODI가 앞서고, 오른쪽 GPT-2는 다섯 평가 모두 CODI가 앞섭니다. 그림을 누르면 원본 크기로 열립니다.*

**추론 때 latent 바꾸기 (GSM8K, 학습은 그대로).**

| 추론 때 바꾼 것 | CODI | 변화 | Middleflow | 변화 |
|---|---:|---|---:|---|
| 그대로 | 41.47 | | 37.38 | |
| 0 벡터 | 30.63 | −10.84 [−13.34, −8.34] | 28.58 | −8.79 [−10.76, −6.82] |
| 답할 때 가림 | 22.67 | −18.80 [−21.55, −16.06] | 31.16 | −6.22 [−8.05, −4.38] |
| latent 건너뜀 | 22.59 | −18.88 [−21.62, −16.14] | 31.31 | −6.07 [−7.90, −4.23] |
| latent 0개 | 21.46 | −20.02 [−22.75, −17.28] | 31.31 | −6.07 [−7.92, −4.21] |
| 잡음 | 9.63 | −31.84 [−34.59, −29.09] | 27.60 | −9.78 [−11.86, −7.70] |
| 다른 문항의 latent | 5.69 | −35.78 [−38.54, −33.03] | 26.99 | −10.39 [−12.54, −8.23] |

**실제 문항과 실제 답.** GSM8K 828번 "Mulan has $40. Her father gave her $100. She buys two pairs of jeans at $30 each and a bag for $20. How much money does Mulan have left?" (정답 60)

| 모델 | 추론 때 바꾼 것 | 모델이 쓴 답 | 채점 |
|---|---|---|---|
| CODI | 그대로 | The answer is: 60 | 맞음 |
| Middleflow | 그대로 | The answer is: 80 | 틀림. 가방 값 20을 빼지 않음 |
| Latent 없음 | 그대로 | The answer is: 80 | 틀림. 같은 곳에서 멈춤 |
| CODI | latent 건너뜀 | 60>> <<2\*30+20=100>> <<100+100=200>>The answer is: 160 | 틀림 |
| CODI | 0 벡터 | 60>> <<2\*30=60>> <<60+20=80>> <<40+100=140>>The answer is: 60 | 맞음. 풀이를 글로 씀 |
| Middleflow | 0 벡터 | is: 120 | 틀림 |

Middleflow와 Latent 없음은 마지막 빼기 한 번을 빠뜨린 같은 답(80)을 썼습니다. 1,319문항 중 CODI만 맞히고 둘 다 틀린 문항은 92개입니다. 한 문항의 예이고, 이런 "한 단계 모자란" 답이 전체에서 몇 개인지는 세지 않았습니다.

**미리 정한 판정에 대어 보면.** CODI는 다섯 평가 모두 Latent 없음보다 높아 첫째 줄의 앞부분(CODI가 Latent 없음보다 높음)은 맞습니다. Middleflow가 그 차이를 "대부분 지킴"은 SVAMP와 MultiArith에서만 맞고, GSM8K와 GSM-Hard에서는 둘째 줄에 해당합니다. 판정은 벤치마크에 따라 갈렸습니다. 위 표의 "해석" 열은 결과를 보기 전에 적어 둔 것입니다. 이 결과로 확인된 것은 정확도의 차이이고, "latent가 필요하다"는 해석까지 확인된 것은 아닙니다.

## 그래서 무슨 뜻인가

- **CODI와 Latent 없음의 차이는 모델에 따라 다릅니다.** 같은 코드, 같은 손실로 학습해도 Llama-1B의 GSM8K에서는 차이가 확인되지 않았고 GPT-2 Small에서는 1.7~24.4점이었습니다(다섯 평가 모두 0을 벗어남). PCCoT 논문 표 1과 같은 방향입니다. 두 모델은 크기, layer 수, 사전학습 자료가 모두 달라, 무엇 때문에 다른지는 확인하지 않았습니다.
- **Middleflow와 Latent 없음의 차이는 계산 단계가 적은 문제에서 크고, 많은 문제에서 작았습니다.** SVAMP와 MultiArith는 계산식 한두 개로 풀리는 문항이 많고, GSM8K와 GSM-Hard는 여러 개를 차례로 이어야 합니다. 가운데 5개 layer만으로는 여러 단계를 이어 계산하기에 모자랄 수 있습니다(가설, 아직 단계별로 나눠 확인하지 않음).
- **Middleflow도 latent를 씁니다.** 지우면 6~9점, 다른 문항의 latent를 넣으면 10점 떨어졌습니다. 다만 CODI(11~36점)보다 덜 기댑니다. Llama에서 본 "넣는 layer가 latent 의존도를 정한다"와 같은 모습입니다.
- **Llama에서 본 해결책이 여기서도 통하는지가 다음 질문입니다.** Llama에서는 L13→L0(첫 layer에 넣기)이 CODI와 정확도가 같았습니다. GPT-2에서 같은 위치인 L9→L0이 CODI와 같은 정확도를 낸다면, latent는 꺼내는 곳보다 넣는 곳이 중요하다는 결론이 두 모델에서 같아집니다.

## 진행 기록

**코드 이식과 확인.**
- Middleflow 코드를 GPT-2 구조(layer 12개, 위치 정보를 입력에서 더하는 방식)로 옮겼습니다.
- 작은 무작위 모델로 하는 시험 7개를 모두 통과했습니다. 특히 전체 깊이 설정의 latent 반복과 학습 손실 세 항이 공식 CODI 코드와 같은 값을 냈습니다.
- 가운데 layer에 넣는 latent에는 위치 정보를 더하지 않습니다. 앞 layer 출력에서 이미 위치 정보를 갖고 오기 때문입니다.
- GPT-2 Middleflow는 Llama의 L13→L7을 비율대로 옮긴 L9→L5(block 5~9)입니다.

**평가 경로 확인.** CODI 저자가 공개한 GPT-2 체크포인트를 우리 평가 코드로 채점했습니다. GSM8K 1,319문항에서 42.46%였고(논문 43.7%), 공식 평가 방식(한 문항씩)과 1,319문항의 답이 모두 같았습니다.

**공개 CODI GPT-2에서 추론 때 latent 바꾸기 (GSM8K).**

| 추론 때 바꾼 것 | 정확도 |
|---|---:|
| 그대로 | 42.46 |
| latent 0개 | 22.37 |
| latent 건너뜀 (위치만 비움) | 22.90 |
| 0 벡터 | 22.44 |
| 답할 때 가림 | 22.90 |
| 잡음 | 11.98 |
| 다른 문항의 latent | 6.37 |

**표 읽는 법.** "그대로"와의 차이가 클수록 답이 latent에 기댄다는 뜻입니다. 위 네 줄(0개, 건너뜀, 0 벡터, 가림)은 latent의 정보를 없애고, 아래 두 줄(잡음, 다른 문항)은 틀린 정보를 넣습니다. 틀린 정보를 넣었을 때 비웠을 때보다 더 떨어지면, 모델이 latent의 내용을 실제로 읽어 쓴다는 근거입니다.

GPT-2 CODI는 latent를 비우면 20점, 틀린 내용을 넣으면 30~36점 떨어집니다. Llama의 CODI처럼 latent에 크게 기댑니다.

**학습 (모두 원본 CODI GPT-2 설정: 40 epoch, 학습률 3e-3, 119,960 step, 시드 11, 모델마다 GPU 한 장).**

| 모델 | 시작 | 끝 |
|---|---|---|
| CODI (L11→L0, 전체 깊이) | 11-24 12:49 | 11-25 03:30 |
| Latent 없음 | 11-24 13:13 | 11-25 05:28 |
| Middleflow (L9→L5) | 11-24 14:31 | 11-25 05:43 |

세 GPU의 CPU 성능이 서로 달라 학습 시간은 견주지 않습니다. 비용은 [FLOPs와 실제 시간](2026-11-25-mf-p-flops-vs-time.html)에 FLOPs로 적었습니다.

**평가.** 학습이 끝난 GPU에서 바로 네 벤치마크, GSM-Symbolic, 추론 때 latent 바꾸기를 평가했습니다. Latent 없음과 Middleflow의 GSM-Symbolic은 처음에 AIME25 단계에서 GPU 오류로 멈춰, 11월 25일 오전에 GSM-Symbolic 세 세트만 다시 평가했습니다. AIME는 세 모델 모두 AIME24에서 0/30이라 GPT-2에서는 평가에서 뺐습니다.

**다음 학습 (11월 25일 낮에 바꿈).** GPT-2 추가 학습은 미뤘습니다. 오전에는 L9→L0을 먼저 끝나는 GPU로 옮겼지만, 낮에 지금까지 써 온 Llama-3.2-1B에서 방법을 먼저 증명하기로 하면서 GPT-2 루프를 40 epoch 중 13.3 epoch에서 멈췄고 L9→L0, 사선, 후퇴 후 전진, 거꾸로는 시작하지 않았습니다. GPU 세 장은 지금 Llama 실험을 학습합니다([기존 모델에서 방법 증명](2026-11-25-mf-r-llama-method-proof.html)).

## 다음 질문

- 첫 layer에 넣으면(L9→L0) CODI와 같은 정확도가 나오는가? 그렇다면 Llama와 같은 결론(넣는 곳이 정확도를 정함)이 GPT-2에서도 성립합니다. 이 학습은 기존 모델 실험 뒤로 미뤘습니다.
- 얕은 모델에서 latent는 몇 개 layer를 지나야 하는가? 지금 있는 점은 0개, 5개, 12개입니다([layer 비율에 따른 정확도](2026-11-25-mf-q-layer-ratio.html)).
- 같은 질문을 기존 모델에서 먼저 봅니다. L0부터 7개 layer를 지나는 L6→L0, 추론 계산량을 CODI와 맞춘 Middleflow, layer 4개와 2개입니다([기존 모델에서 방법 증명](2026-11-25-mf-r-llama-method-proof.html)).

## 한계와 주의

- 시드 하나로 비교합니다.
- GPT-2 Small과 Llama-1B는 깊이뿐 아니라 크기와 사전학습도 다르므로, "깊이가 모자라서"라고 단정하지 않고 "모델에 따라 다르다"까지만 씁니다.
- GPT-2는 위치 정보를 입력에서만 더하므로, 가운데 layer에 넣는 latent의 위치 처리를 어떻게 했는지 결과와 함께 밝힙니다.
