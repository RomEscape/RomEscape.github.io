---
title: latent가 지나는 layer 경로를 step마다 바꾸기 — 루프, 사선, 후퇴 후 전진
date: 2026-11-24
project: Middleflow
status: 진행 중
summary: 지금까지의 변형은 모든 latent step에 같은 layer 범위를 썼습니다. 가운데 묶음을 두 번 돌거나(루프), step마다 한 칸씩 내려가 마지막에 첫 layer까지 닿거나(사선), 올라갔다 내려와 다시 올라가는(후퇴 후 전진) 경로를 GPT-2 Small에서 학습해 비교합니다. 코드와 시험을 마쳤고, 11월 25일 새벽부터 GPU 한 장에 하나씩 학습합니다.
published: true
---

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

## 세 가지 경로 (GPT-2 Small, layer 12개, block 0~11)

| 이름 | latent 한 step의 경로 | step당 block 계산 | 노리는 것 |
|---|---|---:|---|
| 비교: CODI | 0 → 11 | 12 | 기준 |
| 비교: L9→L0 | 0 → 9 | 10 | 넣는 곳을 첫 layer로 |
| 비교: Middleflow (L9→L5) | 5 → 9 | 5 | 가운데만 |
| **루프** | 5 → 9, 다시 5 → 9 | 10 | 같은 계산량이면 "가운데를 두 번"이 "더 넓게(L9→L0)"보다 나은가 |
| **사선** | step 1: 5→9, step 2: 4→8, …, step 6: 0→4 | 5 | Middleflow와 같은 계산량으로 마지막에 첫 layer까지 닿으면 latent를 더 쓰고 더 맞히는가 |
| **후퇴 후 전진** | 5 → 9, 내려와 7 → 9 | 8 | 한 번 올라간 뒤 앞 단계를 다시 거치는 것이 도움이 되는가 |

[![latent 경로 변형 세 가지와 기준 Middleflow의 step별 경로](../uploads/middleflow/experiments/latent-paths.png)](../uploads/middleflow/experiments/latent-paths.png)

*가로는 position(질문, latent 6개, 답), 세로는 GPT-2 Small의 layer(L0~L11)입니다. 루프와 후퇴 후 전진은 한 latent position에서 layer를 두 번 지나므로 칸을 둘로 나눠 그렸습니다. 연한 파랑은 지나지만 KV를 남기지 않는 칸(같은 step에서 다시 지나기 전), 진한 파랑은 KV를 남기는 칸입니다. 사선은 step마다 범위가 한 칸씩 내려가 z6은 L0~L4를 지납니다. 그림을 누르면 원본 크기로 열립니다.*

**표 읽는 법.** step당 block 계산이 같으면 latent에 드는 계산량이 같습니다. 그래서 루프는 L9→L0과(둘 다 10), 사선은 Middleflow와(둘 다 5) 짝지어 비교합니다. 후퇴 후 전진(8)은 Middleflow와 루프 사이입니다.

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

## 진행 상황 (11월 24일)

**코드와 시험.** latent가 step마다 정해진 block 순서를 지나도록 GPT-2 학습 코드에 변형을 더했습니다. 원래 코드는 고치지 않았습니다. 작은 무작위 모델로 하는 시험 12개를 모두 통과했습니다.

- 경로를 연속 구간 하나(예: 5→9)로 주면 기존 Middleflow와 출력과 학습 손실이 정확히 같고, 전체 구간(0→11)은 공식 CODI의 latent 반복과 같습니다.
- 루프, 사선, 후퇴 후 전진에서 step마다 지나는 block과 block마다 KV 캐시에 남는 latent 수가 위 표와 같습니다.
- KV 캐시를 쓰지 않고 처음부터 다시 계산한 결과와 답이 같고, 질문 앞을 빈칸으로 채워도 결과가 같으며, 학습 때 기울기가 학습하는 가중치에만 갑니다.

**학습 순서.** GPU 세 장이 지금 학습(CODI, Latent 없음, Middleflow)을 마치는 대로 한 장에 하나씩 이어서 학습합니다.

| 경로 | 시작 예정 | 그다음 |
|---|---|---|
| 사선 | 11-25 03:30쯤 (CODI 다음) | L9→L0 |
| 루프 | 11-25 05:25쯤 (Middleflow 다음) | – |
| 후퇴 후 전진 | 11-25 05:45쯤 (Latent 없음 다음) | – |

## 한계와 주의

- 가운데 묶음을 반복하는 선행 연구(ETD, 반복 깊이 모델)와 latent 여러 개를 함께 고쳐 가는 선행 연구(PCCoT)가 있습니다. 특히 루프는 이들과 겹칠 수 있어, 원문을 확인한 뒤 새로운 점을 정리합니다. step마다 layer 범위를 바꾸는 사선과 후퇴 후 전진은 지금까지 확인한 latent 추론 논문에는 없었습니다.
- 지금 세 학습의 속도로 어림하면 한 경로에 학습 약 15시간이 걸립니다. 시드는 하나입니다.

## 일지에서의 이름

`gpt2_path_diagonal_b5to9_b0to4_seed11`(사선), `gpt2_path_loop_b5to9x2_seed11`(루프), `gpt2_path_retreat_b5to9_b7to9_seed11`(후퇴 후 전진), `gpt2_r10_w0_seed11`(L9→L0).
