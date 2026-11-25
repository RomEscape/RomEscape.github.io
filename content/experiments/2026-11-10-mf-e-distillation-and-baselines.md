---
title: distillation 제거(추가 실험 5)와 풀이 없음, 풀이 글쓰기 기준선
date: 2026-11-10
project: Middleflow
status: 완료
summary: latent 없이 학습한 모델에서 distillation 손실만 빼자 네 벤치마크가 모두 떨어졌습니다(GSM8K −15.5점). 답만 학습한 기준선은 30.86이었습니다. 이 설정에서 정확도의 큰 몫은 latent 계산이 아니라 distillation에서 옵니다. 풀이를 글로 쓰는 기준선은 학습이 무너져 아직 없습니다.
published: true
---

<!-- mf-rq-start -->

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | latent 없이 학습해도 CODI와 같았습니다. 두 모델에 공통으로 남은 것은 세 손실 항(교사 CE, 학생 CE, distillation)입니다. |
| 든 의문 | 정확도는 latent 계산이 아니라 학습 신호에서 오는가? |
| 그때까지 안 해 본 것 | 같은 코드에서 "답만 학습 → distillation까지 → latent 계산까지"를 한 줄로 나눈 적이 없었습니다. |
| 그래서 한 것 | Latent 없음에서 distillation 손실 하나만 빼고 다시 학습했고, 답만 학습한 기준선과 풀이를 글로 쓰는 기준선을 더했습니다. |
| 답 | 답만 학습 30.86 → distillation까지 52.16 → latent 계산까지 53.37. 오른 22.5점 중 21.3점이 distillation에서 나왔습니다. |
| 다음 의문 | latent가 보탠 몫이 작은 것은 이 모델(Llama-1B)의 이야기인가? latent가 필요하다고 보고된 모델에서는([GPT-2 Small](2026-11-24-mf-j-gpt2-plan.html))? |

질문의 사슬 전체는 [연구 질문으로 다시 쓴 Middleflow 연구](2026-11-25-mf-o-research-questions.html)에 있습니다.

<!-- mf-rq-end -->

## 한 줄 요약

정확도를 단계별로 나누면 답만 학습 30.86 → distillation까지 학습한 Latent 없음 52.16 → latent 계산까지 더한 CODI 53.37입니다. 오른 22.5점 가운데 21.3점이 distillation 단계에서 나왔습니다.

## 왜 궁금했나

[latent 없이 학습한 모델](2026-11-09-mf-c-no-latent.html)이 CODI와 정확도가 같았다면, 그 정확도는 어디서 온 것일까요? 남은 차이는 손실 항뿐이므로 하나씩 빼 봤습니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 값 |
|---|---|---|
| ① 교사 CE | 같은 모델이 질문과 풀이를 보고 풀이와 답을 맞히도록 하는 손실 | 계수 1 |
| ② 학생 CE | 풀이 없이(latent 뒤에, 또는 latent 없이) 답을 맞히도록 하는 손실 | 계수 1 |
| ③ distillation | 답 숫자 바로 앞 위치에서 학생의 내부 표현(hidden state)을 풀이를 본 교사의 것과 같아지도록 하는 손실. 17개 layer 경계의 평균 | 계수 20 |
| No-CoT-SFT | 질문에서 바로 답을 쓰도록 답 토큰만 학습한 기준선. `<bot>`, `<eot>`, position 간격도 없음 | 학습률 2e-4 |
| CoT-SFT | 질문 뒤에 풀이를 글로 쓰고 답하도록 학습한 기준선 | 학습 실패 |

## 방법

1. Latent 없음 모델에서 ③만 빼고 처음부터 학습했습니다(①②만 남음).
2. 답만 학습하는 No-CoT-SFT를 같은 자료로 학습했습니다. 처음에는 CODI의 학습률 8e-4를 그대로 썼다가 학습이 무너져, 학습률 2e-4로 다시 학습했습니다.
3. ②만 남긴 학습(학생 손실만)도 해 봤습니다.

[![교사는 질문과 풀이를 보고, 학생은 풀이 없이 답한다. distillation은 답 직전 위치의 내부 표현을 맞춘다](../uploads/middleflow/meeting-2026-11-12/distillation-removal.png)](../uploads/middleflow/meeting-2026-11-12/distillation-removal.png)

*예시는 GSM8K-Aug 학습 자료의 첫 문항입니다. 교사는 `<<600*30/100=180>> <<600*10/100=60>> <<180+60=240>>` 풀이를 보고 360을 답합니다.*

## 실험 예시

GSM8K 23번 문항: "A candle melts by 2 centimeters every hour that it burns. How many centimeters shorter will a candle be after burning from 1:00 PM to 5:00 PM?" (정답 8)

| 모델 (손실 항) | 출력 | 채점 |
|---|---|---|
| CODI (①②③ + latent) | The answer is: 8 | 맞음 |
| Middleflow (①②③ + latent) | The answer is: 8 | 맞음 |
| Latent 없음 (①②③) | The answer is: 8 | 맞음 |
| Distillation 제거 (①②) | The answer is: 10 | 틀림 |
| No-CoT-SFT (답만) | The answer is: 6 | 틀림 |

## 결과

| 모델 | GSM8K | SVAMP | MultiArith | GSM-Hard |
|---|---:|---:|---:|---:|
| CODI | 53.37 | 59.40 | 98.33 | 12.96 |
| Latent 없음 (①②③) | 52.16 | 57.60 | 97.78 | 12.28 |
| Distillation 제거 (①②) | 36.69 | 48.00 | 62.78 | 9.02 |
| No-CoT-SFT (학습률 2e-4) | 30.86 | 43.60 | 60.56 | 7.28 |
| 짝차이 (제거 − Latent 없음) | −15.47 [−18.04, −12.89] | −9.60 [−12.12, −7.08] | −35.00 [−42.30, −27.70] | −3.26 [−4.60, −1.92] |

**무너진 학습 두 개.**

| 학습 | 무슨 일이 있었나 | 판단 |
|---|---|---|
| No-CoT-SFT, 학습률 8e-4 | step 1,240 → 1,250에서 손실 0.447 → 5.790, 기울기 크기 0.3 → 14.0. 학습 중 점검이 2,541 step에서 멈춤 | 답 토큰만 학습하는 조건에 CODI용 학습률을 확인 없이 쓴 설정 문제. 2e-4로 다시 학습해 정상 |
| 학생 손실만 (②) | step 5,540 → 5,550에서 0.362 → 4.168로 같은 모양으로 무너짐. GSM8K 4.40 | 같은 원인으로 봄. 기준선으로 쓰지 않음 |
| CoT-SFT | 이어 학습하다 epoch 1.4에서 손실이 0.22에서 1.4대로 올라 자동 중단 | 결과 없음. 다시 학습 필요 |

**표 읽는 법.** 교사 CE(①)가 있는 학습 9개는 같은 학습률에서 무너지지 않았습니다. 무너진 두 학습은 모두 답 토큰만 학습한 조건입니다.

## 그래서 무슨 뜻인가

- 이 설정에서 정확도의 큰 몫은 풀이를 본 교사의 내부 표현을 따라 하게 하는 distillation에서 옵니다. CODI 논문의 GPT-2 distillation 제거 실험과 같은 방향입니다.
- 우리 No-CoT-SFT 값은 CODI 논문 표 1의 Llama-1B No-CoT-SFT(SVAMP 44.1, MultiArith 70.9, GSM-Hard 7.1)와 SVAMP, GSM-Hard는 가깝고 MultiArith는 10점 낮습니다.

## 한계

- 시드 하나입니다.
- CoT-SFT 기준선이 없어, 풀이를 글로 쓸 때와의 정확도, 시간 비교는 아직 못 합니다.

## 일지에서의 이름

`ablation_position_gap_no_distill_seed11`, `no_cot_lr2e4_seed11`, `no_cot_seed11`(무너짐), `ablation_position_gap_student_only_seed11`(무너짐), `explicit_cot_seed11`(중단).
