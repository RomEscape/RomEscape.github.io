---
title: latent가 지나는 layer 경로를 step마다 바꾸기 — 루프, 사선, 후퇴 후 전진, 거꾸로
date: 2026-11-24
project: Middleflow
status: 보류
summary: latent가 step마다 다른 layer 경로를 지나게 하는 변형 넷(가운데를 두 번 도는 루프, 한 칸씩 내려가 첫 layer에 닿는 사선, 후퇴 후 전진, 거꾸로)을 GPT-2에서 학습하려던 계획입니다. 11월 25일에 기존 모델(Llama)에서 방법을 먼저 증명하기로 하면서 루프를 13.3 epoch에서 멈췄고 나머지는 시작하지 않았습니다.
published: true
---

<!-- mf-rq-start -->

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | 첫 layer에 넣으면 정확도가 CODI와 같았고([넣는 layer](2026-11-12-mf-f-insert-layer.html)), 가운데만 돌면 싸지만 latent가 필요한 GPT-2에서는 이득의 일부만 지켰습니다([GPT-2 Small](2026-11-24-mf-j-gpt2-plan.html), 11월 25일). |
| 든 의문 | 매 step 전체를 지나지 않고 step마다 한 layer씩 내려가 마지막 step에만 첫 layer에 닿으면(사선) 둘을 함께 얻을까? 가운데 계산이 모자란 것이라면 같은 가운데를 두 번 돌면(루프) 될까? 가운데 layer는 순서를 바꿔도 덜 무너진다는데 latent도 그런가(거꾸로)? |
| 그때까지 안 해 본 것 | 지금까지의 변형은 모두 6개 step이 같은 layer 범위를 지났습니다. |
| 그래서 한 것 | GPT-2에서 네 경로(루프, 사선, 후퇴 후 전진, 거꾸로)의 코드와 시험을 마치고 루프부터 학습했습니다. 이 계획은 11월 24일에 "해 볼 만한 경로"로 먼저 세웠고, 현상에서 나온 동기(위 두 줄)는 11월 25일 GPT-2 결과를 보고 다시 적었습니다. 후퇴 후 전진은 근거가 된 현상이 약합니다. |
| 답 | 없습니다. 11월 25일 낮에 기존 모델(Llama)에서 방법을 먼저 증명하기로 하면서 루프를 40 epoch 중 13.3 epoch에서 멈췄고, 나머지 셋은 시작하지 않았습니다. |
| 다음 의문 | 기존 모델에서 같은 비용이면 어느 경로가 나은지를 먼저 봅니다([기존 모델에서 방법 증명](2026-11-25-mf-r-llama-method-proof.html)). 그 결과를 본 뒤 이 변형들을 다시 할지 정합니다. |

질문의 사슬 전체는 [연구 질문으로 다시 쓴 Middleflow 연구](2026-11-25-mf-o-research-questions.html)에 있습니다.

<!-- mf-rq-end -->

## 한 줄 요약

latent가 지나는 layer를 step마다 다르게 정하는 세 가지 경로를 만들어, 같은 설정의 CODI, Latent 없음, Middleflow와 비교합니다.

## 왜 궁금했나

지금까지의 결과에서 두 가지가 보였습니다.

- latent를 넣는 layer가 latent를 쓰는 정도를 정했습니다. 첫 layer(L0)에 넣으면 latent에 크게 기대고 정확도도 CODI와 같았지만, 가운데에 넣으면 싸지만 덜 썼습니다([넣는 layer 기록](2026-11-12-mf-f-insert-layer.html)).
- 이름과 숫자를 바꾸거나 풀이 단계를 더한 문제에서는 latent가 있는 모델이 앞섰습니다([더 어려운 문제 기록](2026-11-24-mf-k-harder-benchmarks.html)).

그런데 지금까지의 변형(넣는 layer 바꾸기, 띄엄띄엄 배치, Latent 없음)은 모두 **6개의 latent step이 같은 layer 범위를 지나는 고정 배치**였습니다. step마다 다른 범위를 지나게 하면 "깊게 읽기"와 "싸게 계산하기"를 함께 얻을 수 있는지 보려 합니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| block | 모델의 layer 하나. 아래 block의 출력이 위 block의 입력이 됨 | GPT-2 Small은 block 0~11의 12개 |
| latent step | latent 하나를 만드는 한 번의 계산. 앞 step의 결과를 받아 다음 latent를 만듦 | 문항마다 6 step |
| 경로 | 한 step에서 latent가 지나는 block의 순서. 첫 block에 넣고 마지막 block의 출력을 다음 step에 넘김 | 예: Middleflow는 5, 6, 7, 8, 9 |
| step당 block 계산 | 한 step에서 지나는 block 수. latent에 드는 계산량의 척도 | CODI 12, Middleflow 5 |
| KV 캐시 | 토큰이나 latent가 block을 지날 때 그 block에 남기는 값(key, value). 뒤에 오는 토큰은 attention으로 이 값을 다시 봄 | 답을 쓸 때 각 block은 그 block의 KV 캐시에 남은 latent만 봄. block마다 latent 0~6개 |

## 네 가지 경로 (GPT-2 Small, layer 12개, block 0~11)

| 이름 | latent 한 step의 경로 | step당 block 계산 | 노리는 것 |
|---|---|---:|---|
| 비교: CODI | 0 → 11 | 12 | 기준 |
| 비교: L9→L0 | 0 → 9 | 10 | 넣는 곳을 첫 layer로 |
| 비교: Middleflow (L9→L5) | 5 → 9 | 5 | 가운데만 |
| **루프** | 5 → 9, 다시 5 → 9 | 10 | 같은 계산량이면 "가운데를 두 번"이 "더 넓게(L9→L0)"보다 나은가 |
| **사선** | step 1: 5→9, step 2: 4→8, …, step 6: 0→4 | 5 | Middleflow와 같은 계산량으로 마지막에 첫 layer까지 닿으면 latent를 더 쓰고 더 맞히는가 |
| **후퇴 후 전진** | 5 → 9, 내려와 7 → 9 | 8 | 한 번 올라간 뒤 앞 단계를 다시 거치는 것이 도움이 되는가 |
| **거꾸로** (11-24 추가) | 9 → 8 → 7 → 6 → 5 | 5 | Middleflow와 같은 layer를 순서만 뒤집어 지나도 같은 만큼 맞히는가 |

[![latent 경로 변형 네 가지와 기준 Middleflow의 step별 경로](../uploads/middleflow/experiments/latent-paths.png)](../uploads/middleflow/experiments/latent-paths.png)

*가로는 position(질문, latent 6개, 답), 세로는 GPT-2 Small의 layer(L0~L11)입니다. 루프와 후퇴 후 전진은 한 latent position에서 layer를 두 번 지나므로 칸을 둘로 나눠 그렸습니다. 연한 파랑은 지나지만 KV를 남기지 않는 칸(같은 step에서 다시 지나기 전), 진한 파랑은 KV를 남기는 칸입니다. 사선은 step마다 범위가 한 칸씩 내려가 z6은 L0~L4를 지납니다. 거꾸로는 Middleflow와 같은 칸을 흰 화살표 방향(위에서 아래)으로 지나고, block 5의 출력을 다음 step의 block 9에 넣습니다. 그림을 누르면 원본 크기로 열립니다.*

**표 읽는 법.** step당 block 계산이 같으면 latent에 드는 계산량이 같습니다. 그래서 루프는 L9→L0과(둘 다 10), 사선과 거꾸로는 Middleflow와(모두 5) 짝지어 비교합니다. 거꾸로는 Middleflow와 지나는 layer도 같고 순서만 다릅니다. 후퇴 후 전진(8)은 Middleflow와 루프 사이입니다.

- 한 step 안에서 같은 block을 두 번 지나면, 그 block의 KV 캐시에는 마지막으로 지날 때의 값만 남깁니다. 답을 쓸 때 각 block이 step마다 latent 하나만 보도록 하기 위해서입니다. 그래서 루프와 후퇴 후 전진은 Middleflow처럼 block 5~9의 KV 캐시에 latent가 6개씩 남습니다.
- 답 토큰은 지금처럼 12개 block을 모두 지나고, 각 block에서 그 block의 KV 캐시에 남은 latent만 봅니다.
- 사선은 step마다 지나는 block이 달라서, block마다 KV 캐시에 남는 latent 수가 다릅니다(아래 예시).

## 실험 예시

**사선 경로를 step별로 따라가기.** step 1에는 질문 마지막 토큰의 block 9 출력을 넣고, 그 뒤로는 앞 step의 마지막 block 출력을 다음 step의 첫 block에 넣습니다.

| step | 지나는 block | 다음 step에 넘기는 출력 | 다음 step에서 넣는 곳 |
|---|---|---|---|
| 1 | 5, 6, 7, 8, 9 | block 9 | block 4 |
| 2 | 4, 5, 6, 7, 8 | block 8 | block 3 |
| 3 | 3, 4, 5, 6, 7 | block 7 | block 2 |
| 4 | 2, 3, 4, 5, 6 | block 6 | block 1 |
| 5 | 1, 2, 3, 4, 5 | block 5 | block 0 |
| 6 | 0, 1, 2, 3, 4 | 마지막 step이라 넘기지 않음 | – |

여섯 step이 끝나면 block마다 KV 캐시에 남는 latent 수는 다음과 같습니다.

| block | KV 캐시에 남는 latent |
|---|---:|
| 4, 5 | 5개씩 |
| 3, 6 | 4개씩 |
| 2, 7 | 3개씩 |
| 1, 8 | 2개씩 |
| 0, 9 | 1개씩 |
| 10, 11 | 없음 |

모두 30개로 Middleflow(block 5~9에 6개씩, 30개)와 같지만, 가운데(block 4, 5)에 많이 모이고 첫 block까지 퍼집니다.

**루프와 후퇴 후 전진의 한 step.** 루프는 block 5→6→7→8→9를 지난 뒤 block 9의 출력을 그대로 block 5에 다시 넣어 5→9를 한 번 더 지납니다. 후퇴 후 전진은 5→9를 지난 뒤 block 7로 돌아가 7→8→9를 한 번 더 지납니다. 두 번째로 지날 때도 각 block은 그 block의 KV 캐시에 있는 앞 step들의 latent를 봅니다.

**거꾸로의 한 step.** block 9에 넣어 9→8→7→6→5 순서로 지나고, block 5의 출력을 MLP를 거쳐 다음 step의 block 9에 넣습니다. 첫 step에는 질문 마지막 토큰의 block 5 출력을 넣습니다. block 5~9의 KV 캐시에 latent가 6개씩 남는 것은 Middleflow와 같고, 답 토큰이 latent를 보는 layer도 같습니다. 학습하지 않은 모델에서도 가운데 layer는 빼거나 이웃 layer와 순서를 바꿔도 크게 무너지지 않는다는 보고가 있어([Lad 외 2024](https://arxiv.org/abs/2406.19384), [Sun 외 2024](https://arxiv.org/abs/2407.09298)), 학습까지 하면 순서를 통째로 뒤집어도 latent 계산이 되는지 봅니다.

## 비교 방법

1. CODI, Latent 없음, Middleflow와 같은 설정(40 epoch, 학습률 3e-3, 시드 11)으로 처음부터 학습합니다.
2. 네 벤치마크, GSM-Symbolic(main, P1, P2), 추론 때 latent 바꾸기로 평가합니다.
3. 학습 시간과 추론 시간은 모든 모델을 같은 기계에서 따로 잽니다.

## 결과를 보기 전에 정한 해석 기준

| 결과 | 해석 |
|---|---|
| 사선이 Middleflow보다 높고 CODI와 차이가 확인되지 않음 | 같은 계산량으로 첫 layer까지 닿는 경로가 latent의 이득을 되찾는다 |
| 루프가 L9→L0보다 높음 | 같은 계산량이면 가운데를 깊게 도는 것이 넓게 지나는 것보다 낫다 |
| 셋 모두 Middleflow와 차이가 확인되지 않음 | 경로 모양보다 계산량이나 넣는 위치가 중요하다 |
| 거꾸로가 Middleflow와 차이가 확인되지 않음 | 가운데 layer의 순서는 latent 계산에 중요하지 않다 |
| 거꾸로가 Middleflow보다 낮음 | 같은 layer라도 아래에서 위로 지나는 순서가 latent 계산에 쓰인다 |

## 진행 상황 (11월 24일)

**코드와 시험.** latent가 step마다 정해진 block 순서를 지나도록 GPT-2 학습 코드에 변형을 더했습니다. 원래 코드는 고치지 않았습니다. 작은 무작위 모델로 하는 시험 13개를 모두 통과했습니다(거꾸로 경로는 11월 24일 23시에 더함).

- 경로를 연속 구간 하나(예: 5→9)로 주면 기존 Middleflow와 출력과 학습 손실이 정확히 같고, 전체 구간(0→11)은 공식 CODI의 latent 반복과 같습니다.
- 루프, 사선, 후퇴 후 전진, 거꾸로에서 step마다 지나는 block과 그 순서, block마다 KV 캐시에 남는 latent 수가 위 표와 같습니다.
- KV 캐시를 쓰지 않고 처음부터 다시 계산한 결과와 답이 같고, 질문 앞을 빈칸으로 채워도 결과가 같으며, 학습 때 기울기가 학습하는 가중치에만 갑니다.

**학습 순서.** GPU 세 장이 지금 학습(CODI, Latent 없음, Middleflow)을 마치는 대로 한 장에 하나씩 이어서 학습합니다. 11월 24일 22시에 Llama에서 학습 시간을 CODI와 같게 맞춘 학습 두 개([학습 시간 맞춤](2026-11-24-mf-m-llama-codi-time.html))를 먼저 하기로 했고, 23시에 후퇴 후 전진을 루프 다음(같은 GPU)으로 옮겨 보고(11월 26일 15시) 전에 경로 세 가지가 끝나게 했습니다. 그 자리에서 L9→L0을 학습하고, 거꾸로는 후퇴 후 전진 다음에 학습합니다.

**11월 25일 오전.** 루프는 11월 25일 05:43에 시작했고, 10시 39분에 40 epoch 중 9.7 epoch(step당 0.61초)였습니다.

**11월 25일 낮, 보류.** 지금까지 써 온 Llama-3.2-1B에서 방법을 먼저 증명하기로 하면서 루프 학습을 12:34에 멈췄습니다(40 epoch 중 13.3 epoch, 마지막 저장본은 남겨 둠). 후퇴 후 전진, 거꾸로, 사선, 비교 모델 L9→L0은 시작하지 않았습니다. 이 변형들은 본 현상보다 "해 볼 만한 경로"에서 시작한 계획이었고, GPU는 본 현상에서 나온 질문에 먼저 씁니다([기존 모델에서 방법 증명](2026-11-25-mf-r-llama-method-proof.html)). 그 결과를 본 뒤 다시 할지 정합니다.

## 한계와 주의

- 가운데 묶음을 반복하는 선행 연구(ETD, 반복 깊이 모델)와 latent 여러 개를 함께 고쳐 가는 선행 연구(PCCoT)가 있습니다. 특히 루프는 이들과 겹칠 수 있어, 원문을 확인한 뒤 새로운 점을 정리합니다. step마다 layer 범위를 바꾸는 사선과 후퇴 후 전진, 순서를 뒤집는 거꾸로는 지금까지 확인한 latent 추론 논문에는 없었습니다.
- 지금 세 학습의 속도로 어림하면 한 경로에 학습 약 15시간이 걸립니다. 시드는 하나입니다.

## 일지에서의 이름

`gpt2_path_diagonal_b5to9_b0to4_seed11`(사선), `gpt2_path_loop_b5to9x2_seed11`(루프), `gpt2_path_retreat_b5to9_b7to9_seed11`(후퇴 후 전진), `gpt2_path_reverse_b9to5_seed11`(거꾸로), `gpt2_r10_w0_seed11`(L9→L0).
