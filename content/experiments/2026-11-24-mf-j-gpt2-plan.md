---
title: GPT-2 Small에서 같은 비교 — latent가 필요한 조건에서 Middleflow는 그 이득을 지키는가
date: 2026-11-24
project: Middleflow
status: 진행 중
summary: 선행 연구에서 latent 계산이 약 9점을 더한 GPT-2 Small로 CODI, Latent 없음, Middleflow를 같은 코드와 시드로 학습하고 있습니다. 코드 이식을 마치고 공개 CODI 체크포인트로 평가 경로를 확인했으며(GSM8K 42.46%), 세 학습은 11월 25일 새벽에 끝날 예정입니다.
published: true
---

## 한 줄 요약

latent의 효과는 모델에 따라 다를 수 있습니다. latent가 실제로 필요하다고 보고된 GPT-2 Small에서 CODI와 Latent 없음의 차이가 다시 나오는지, 그리고 Middleflow가 그 차이를 지키는지를 봅니다.

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

## 연구 질문

1. latent 계산의 기여는 모델에 따라 달라지는가? (Llama-1B에서는 확인 안 됨, GPT-2 Small에서는?)
2. latent를 넣는 layer는 정확도와 latent 의존도를 어떻게 바꾸는가?
3. latent가 기여하는 조건에서, 가운데 layer만으로 계산해도 그 기여를 지키며 비용을 줄일 수 있는가?

## 방법 (계획)

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

## 진행 상황 (11월 24일)

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

| 모델 | 시작 | step당 | 끝 예정 |
|---|---|---:|---|
| CODI (L11→L0, 전체 깊이) | 11-24 12:49 | 0.44초 | 11-25 03:30쯤 |
| Latent 없음 | 11-24 13:13 | 0.50초 | 11-25 05:45쯤 |
| Middleflow (L9→L5) | 11-24 14:31 | 0.44초 | 11-25 05:25쯤 |

step당 시간과 끝 예정은 11월 24일 14:55에 3분 동안 잰 값입니다. 세 GPU의 CPU 성능이 서로 달라 위 step당 시간은 학습 시간 비교에 쓰지 않습니다. 학습 시간은 끝난 뒤 한 기계에서 따로 잽니다.

**다음.** 학습이 끝나면 같은 GPU에서 네 벤치마크를 바로 평가하고, 이어서 GSM-Symbolic과 추론 때 latent 바꾸기로 평가합니다. 각 GPU는 지금 학습을 마치는 대로 다음 학습으로 넘어갑니다. CODI 다음은 Llama Middleflow를 CODI와 같은 학습 시간만큼 학습하고([학습 시간 맞춤](2026-11-24-mf-m-llama-codi-time.html)), 그다음 사선과 L9→L0을 학습합니다. Middleflow 다음은 루프입니다. Latent 없음 다음은 Llama Latent 없음의 학습 시간 맞춤, 그다음 후퇴 후 전진입니다([경로 변형 계획](2026-11-24-mf-l-latent-path-plan.html)). 순서는 11월 24일 22시에 바꿨습니다.

## 한계와 주의

- 시드 하나로 비교합니다.
- GPT-2 Small과 Llama-1B는 깊이뿐 아니라 크기와 사전학습도 다르므로, "깊이가 모자라서"라고 단정하지 않고 "모델에 따라 다르다"까지만 씁니다.
- GPT-2는 위치 정보를 입력에서만 더하므로, 가운데 layer에 넣는 latent의 위치 처리를 어떻게 했는지 결과와 함께 밝힙니다.
