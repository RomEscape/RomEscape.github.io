---
title: GPT-2 Small에서 같은 비교 — latent가 필요한 조건에서 Middleflow는 그 이득을 지키는가
date: 2026-11-24
project: Middleflow
status: 계획
summary: Llama-3.2-1B에서는 latent 계산의 몫이 확인되지 않았지만, 선행 연구에서 GPT-2 Small은 latent 계산이 약 9점을 더했습니다. 같은 코드와 같은 시드로 GPT-2 Small의 CODI, Latent 없음, Middleflow를 학습해, latent가 필요한 조건에서 Middleflow가 그 이득을 지키는지 확인합니다.
published: true
---

## 한 줄 요약

latent의 효과는 모델에 따라 다를 수 있습니다. latent가 실제로 필요하다고 보고된 GPT-2 Small에서 CODI와 Latent 없음의 차이가 다시 나오는지, 그리고 Middleflow가 그 차이를 지키는지를 봅니다.

## 왜 궁금했나

Llama-1B에서는 [latent 없이 학습한 모델](2026-11-09-mf-c-no-latent.html)이 CODI와 같아서, Middleflow의 비용 절감이 "필요 없는 계산을 줄인 것"인지 "필요한 계산을 싸게 한 것"인지 구분할 수 없었습니다. 그러나 latent 방법은 계산할 자리, 내용 전달, 교사에게서 배우는 학습 신호라는 이유로 나왔고, 첫째 이유는 계산 여유가 적은 모델에서 중요할 수 있습니다. PCCoT 논문(arXiv 2506.18582) 표 1에서 같은 CODI 손실로 학습한 GPT-2 Small은 latent 계산 48.24, 자리만 39.27, 자리 없음 37.78이었습니다.

## 연구 질문

1. latent 계산의 기여는 모델에 따라 달라지는가? (Llama-1B에서는 확인 안 됨, GPT-2 Small에서는?)
2. latent를 넣는 layer는 정확도와 latent 의존도를 어떻게 바꾸는가?
3. latent가 기여하는 조건에서, 가운데 layer만으로 계산해도 그 기여를 지키며 비용을 줄일 수 있는가?

## 방법 (계획)

1. 우리 학습 코드를 GPT-2 구조(12개 layer, 위치 정보를 입력에서 더하는 방식)로 옮기고, 전체 깊이 설정이 원래 CODI 반복과 같은 값을 내는지 CPU 시험으로 확인합니다.
2. CODI 저자가 공개한 GPT-2 체크포인트를 우리 평가 코드로 채점해, 논문 값(GSM8K 43.7) 근처가 나오는지 봅니다.
3. CODI 원본의 GPT-2 설정(학습률 3e-3, 40 epoch, LoRA r128, latent 6개)으로 CODI, Latent 없음, Middleflow를 같은 코드, 같은 시드(11)로 학습합니다. 모델마다 GPU를 나눠 동시에 돌립니다.
4. 네 벤치마크, 추론 시간, 학습 시간, 추론 때 latent 바꾸기를 Llama-1B와 같은 방식으로 잽니다.

## 결과를 보기 전에 정한 판정

| GPT-2 결과 | 읽는 법 |
|---|---|
| CODI가 Latent 없음보다 높고, Middleflow가 그 차이를 대부분 지킴 | latent는 계산 여유가 적은 모델에서 필요하고, 가운데 layer만으로도 그 이득을 지키며 비용을 줄일 수 있다 |
| CODI가 높지만 Middleflow가 그 이득을 잃음 | latent는 앞쪽 layer를 지나야 쓰인다. 넣는 layer와 의존도의 관계를 뒷받침 |
| CODI와 Latent 없음이 같음 | 선행 연구와 다른 결과. 원인 분석 필요 |

## 한계와 주의

- 시드 하나로 비교합니다.
- GPT-2 Small과 Llama-1B는 깊이뿐 아니라 크기와 사전학습도 다르므로, "깊이가 모자라서"라고 단정하지 않고 "모델에 따라 다르다"까지만 씁니다.
- GPT-2는 위치 정보를 입력에서만 더하므로, 가운데 layer에 넣는 latent의 위치 처리를 어떻게 했는지 결과와 함께 밝힙니다.
