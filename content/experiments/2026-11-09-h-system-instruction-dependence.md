---
title: 첫 토큰을 고정해도 시스템 지시문을 없애면 답이 짧아진다
date: 2026-11-09
project: QFFT
status: 진행 중
summary: 응답 글을 고정하고 프롬프트의 한 구역만 바꿔 다음 토큰 분포의 변화를 쟀고, 시스템 지시문을 없앴을 때 SFT가 A1보다 3.5–4.9배 크게 움직이는 것을 새 200문항에서 재현했다. 첫 토큰을 고정하고 실제로 답을 생성한 겹치지 않는 새 100문항에서 SFT와 다른 세 모델의 긴 풀이 격차는 시스템 턴이 있을 때 35–41%p, 없을 때 1.5–4.5%p였다. 학습 방식마다 모델이 하나뿐이고 첫 토큰을 고정한 결과라 아직 발견이라고 부르지 않는다.
published: true
---

## 한 줄 요약

첫 토큰이 지나간 뒤(16–256번째 토큰)에도 학습 방식에 따른 차이가 남아 있었습니다. **질문 내용을 바꿨을 때의 반응은 네 모델이 같습니다. 시스템 지시문을 없앴을 때의 반응은 질문을 보고 학습한 SFT만 3.5–4.9배 큽니다.** 미리 정한 기준으로 새 200문항에서 재현됐습니다. 이어서 실제로 답을 생성해 보니 첫 100문항에서는 세 모델이 모두 짧아져(SFT 0.52배, A1 0.66배, A2 0.79배) 판정을 보류했습니다. **겹치지 않는 새 100문항에서는 미리 정한 규칙으로 모델 순서가 재현됐습니다. 첫 토큰을 `To`로 고정했을 때 긴 풀이 비율은 SFT 79%, 나머지 세 모델 38–44%였고, 시스템 턴을 없애면 넷 모두 27–31.5%로 모였습니다.** 학습 방식마다 모델이 하나뿐이고 첫 토큰을 고정한 결과라 아직 발견이라고 부르지 않습니다.

## 왜 궁금했나

첫 토큰을 `To`로 고정해도 SFT의 긴 풀이 비율은 80.0%인데, 질문 없이 학습한 A1은 42.6%입니다. 두 모델의 학습 차이는 프롬프트에 질문이 있었는지입니다. 그렇다면 프롬프트의 어느 구역이 첫 토큰 뒤의 풀이에 영향을 주는지 재 볼 필요가 있습니다.

답을 새로 생성해서 비교하면 잡음이 큽니다. 같은 설정을 시드만 바꿔도 평균 토큰이 0.75–1.18배 움직였습니다. 그래서 답을 생성하지 않고 저장된 응답 글을 그대로 입력한 뒤, 프롬프트만 바꿔 다음 토큰의 확률 분포가 얼마나 달라지는지(KL)를 쟀습니다. 이 방식에는 생성의 표본 잡음이 없습니다.

## 실험 예시

<!-- xp -->
<figure class="xp"><p class="xp-t">무엇을 바꿨나: 응답 글은 그대로 두고 프롬프트의 한 구역만 바꿈</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Convert the point $(0,3)$ in rectangular coordinates to polar coordina …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To convert the point \((0, 3)\) from rectangular coordinates …</div></div><div class="xp-name">기준: 평가 프롬프트 그대로</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Convert the point $(0,3)$ in rectangular coordinates to polar coordina …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To convert the point \((0, 3)\) from rectangular coordinates …</div></div><div class="xp-name">시스템 턴 없앰</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div></div><div class="xp-del"><div class="xp-role">user</div><div class="">Convert the point $(0,3)$ in rectangular coordinates to polar coordina …</div></div><div class="xp-ctx"><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To convert the point \((0, 3)\) from rectangular coordinates …</div></div><div class="xp-name">질문을 비움</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함(채점 안 함)</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span></div><p class="xp-cap">저장된 MATH500 응답을 앞 512토큰까지 그대로 입력합니다. 빨간 테두리 안은 모델이 읽는 문맥이고, 회색은 지운 구역입니다. 답을 새로 만들지 않고, 각 위치에서 다음 토큰 분포가 기준과 얼마나 다른지(KL)만 잽니다.</p></figure>
<figure class="xp"><p class="xp-t">확인 실험(새 200문항, 응답 글 A2): 16–256번째 토큰의 평균 KL</p><div class="xp-bars"><span>시스템 턴 없앰: SFT</span><span class="xp-track"><i class="xp-fill bad" style="width:32.48%"></i></span><span>0.162</span><span>시스템 턴 없앰: A1</span><span class="xp-track"><i class="xp-fill" style="width:6.66%"></i></span><span>0.033</span><span>시스템 턴 없앰: A2</span><span class="xp-track"><i class="xp-fill" style="width:4.67%"></i></span><span>0.023</span><span>시스템 턴 없앰: QFFT</span><span class="xp-track"><i class="xp-fill" style="width:10.03%"></i></span><span>0.050</span></div><div class="xp-bars"><span>질문을 비움: SFT</span><span class="xp-track"><i class="xp-fill" style="width:84.45%"></i></span><span>0.422</span><span>질문을 비움: A1</span><span class="xp-track"><i class="xp-fill" style="width:83.21%"></i></span><span>0.416</span><span>질문을 비움: A2</span><span class="xp-track"><i class="xp-fill" style="width:82.70%"></i></span><span>0.413</span><span>질문을 비움: QFFT</span><span class="xp-track"><i class="xp-fill" style="width:81.84%"></i></span><span>0.409</span></div><p class="xp-cap">질문을 비웠을 때의 변화는 네 모델이 거의 같고, 시스템 턴을 없앴을 때의 변화는 SFT만 큽니다. 응답 글을 SFT나 QFFT가 쓴 답으로 바꿔도 방향이 같습니다.</p></figure>
<figure class="xp"><p class="xp-t">실제로 답을 생성(100문항 × 2회, 첫 토큰 To 고정): 기본 프롬프트 대비 토큰 비</p><div class="xp-bars"><span>같은 설정 다시 실행: SFT</span><span class="xp-track"><i class="xp-fill" style="width:78.09%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.98 (0.89–1.08)</span><span>같은 설정 다시 실행: A1</span><span class="xp-track"><i class="xp-fill" style="width:83.85%"></i><i class="xp-line" style="left:80.00%"></i></span><span>1.05 (0.96–1.16)</span><span>같은 설정 다시 실행: A2</span><span class="xp-track"><i class="xp-fill" style="width:80.47%"></i><i class="xp-line" style="left:80.00%"></i></span><span>1.01 (0.91–1.11)</span><span>step by step 문구 뺌: SFT</span><span class="xp-track"><i class="xp-fill" style="width:51.66%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.65 (0.58–0.73)</span><span>step by step 문구 뺌: A1</span><span class="xp-track"><i class="xp-fill" style="width:63.47%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.79 (0.73–0.87)</span><span>step by step 문구 뺌: A2</span><span class="xp-track"><i class="xp-fill" style="width:72.52%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.91 (0.82–1.00)</span><span>시스템 턴 없앰: SFT</span><span class="xp-track"><i class="xp-fill bad" style="width:41.92%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.52 (0.47–0.59)</span><span>시스템 턴 없앰: A1</span><span class="xp-track"><i class="xp-fill bad" style="width:52.50%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.66 (0.59–0.73)</span><span>시스템 턴 없앰: A2</span><span class="xp-track"><i class="xp-fill bad" style="width:63.44%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.79 (0.71–0.88)</span></div><p class="xp-cap">세로선이 1.0(기본 프롬프트와 같음)입니다. 문항마다 몇 배 달라졌는지를 평균낸 기하 평균 비이고, 괄호는 문항을 다시 뽑아 구한 95% 구간입니다. 같은 프롬프트를 시드만 바꿔 다시 돌린 줄이 잡음의 크기를 보여 줍니다.</p></figure>
<!-- /xp -->

## 미리 정한 기준과 결과

첫 실험(200문항)에서 본 패턴을 다른 200문항으로 다시 쟀습니다. 기준은 결과를 보기 전에 일지에 적었습니다.

| 판정 항목 | 기준 | 결과 |
|---|---|---|
| 시스템 지시문 의존 (SFT÷A1) | 응답 글 A2에서 3배 이상, 응답 글 SFT에서 2배 이상 | 4.88배 (3.98–5.97), 3.55배 (3.07–4.02) |
| 질문 내용 의존 (SFT÷A1) | 0.8–1.25배 | 1.01배 (0.94–1.09), 1.00배 (0.94–1.08) |
| **판정** | | **재현** |
| 무관한 문장 대 뜻이 같은 문장 | 두 응답 글 모두 3배 이상이면 "지시의 내용에 의존" | 3.00배, 1.57배로 **보류** |

괄호는 문항을 다시 뽑아 구한 95% 구간입니다.

## 조건별 값 (응답 글 A2, 16–256번째 토큰의 평균 KL)

| 바꾼 것 | SFT | A1 | A2 | QFFT |
|---|---:|---:|---:|---:|
| 시스템 턴 없앰 | 0.162 | 0.033 | 0.023 | 0.050 |
| `step by step` 문구 제거 | 0.077 | 0.015 | 0.009 | 0.032 |
| 무관한 지시문으로 교체 | 0.052 | 0.008 | 0.005 | 0.028 |
| 간결하게 답하라는 지시문으로 교체 | 0.080 | 0.012 | 0.008 | 0.042 |
| 뜻이 같은 다른 문장 | 0.017 | 0.009 | 0.006 | 0.015 |
| `step by step`을 사용자 칸으로 이동 | 0.009 | 0.009 | 0.009 | 0.010 |
| 질문을 비움 | 0.422 | 0.416 | 0.413 | 0.409 |
| 다른 문제의 질문으로 교체 | 0.462 | 0.455 | 0.446 | 0.468 |

- 질문을 지우거나 바꾸면 분포는 크게 달라지지만, 그 크기는 학습 방식과 거의 상관이 없습니다.
- 지시문을 없애거나 `step by step`을 빼면 SFT가 유독 크게 달라집니다.
- 같은 뜻의 문장으로 바꾸거나 그 문구를 다른 칸으로 옮기면 변화가 작습니다. 토큰 자리보다 지시의 내용에 달렸을 가능성이 있지만, 미리 정한 기준에는 미치지 못해 보류입니다.

## 왜 흥미로운가

A1도 SFT와 똑같은 시스템 문장으로 학습했습니다. 그런데 첫 토큰 뒤의 정책이 그 문장에 묶인 정도는 A1이 훨씬 작습니다. 학습할 때 고정 토큰이 행동을 실어 나른다는 [기존 연구](https://arxiv.org/abs/2610.41480)와 비슷한 면이 있지만, 질문을 지운 학습에서 이 의존이 줄어든다는 점과, 지시를 옮겨도 유지된다는 점은 그 설명만으로 다 풀리지 않습니다.

## 이 결과로 말할 수 있는 것과 없는 것

- 말할 수 있는 것: 위치 16–256의 다음 토큰 분포에서, 시스템 지시문에 대한 의존은 SFT가 A1보다 3.5–4.9배 크고, 질문 내용에 대한 의존은 같았습니다. 다른 200문항에서 재현됐습니다.
- 말할 수 없는 것: SFT와 A1은 각각 한 번씩 학습한 모델이라 이 차이가 학습의 우연일 수 있습니다. 또 KL은 변화의 크기일 뿐이어서, 실제로 답이 길어지거나 짧아지는지는 말해 주지 않습니다.

## 추가 결과: 질문 유무만 다르게 학습한 작은 모델

SFT와 A1은 각각 따로 학습한 모델이라, 차이가 학습의 우연일 수 있습니다. 그래서 같은 문서, 같은 순서, 같은 시드로 질문 유무와 첫 토큰 라벨만 다르게 학습한 작은 모델 넷으로 같은 측정을 했습니다.

| 비교 | 시스템 턴 없앰 (A2 글 / SFT 글) | 질문 비움 (A2 글 / SFT 글) |
|---|---|---|
| 질문 있음 ÷ 질문 없음 (첫 토큰 학습함, SFT ÷ A1에 해당) | 2.55배 / 1.85배 | 0.99배 / 1.05배 |
| 질문 있음 ÷ 질문 없음 (첫 토큰 제외) | 1.52배 / 1.06배 | 1.00배 / 1.03배 |

미리 정한 판정은 **보류**입니다(기준은 네 값 모두 2배 이상). 방향은 전체 학습과 같고 질문 내용 의존이 같다는 점도 재현됐지만, 크기는 절반 정도이고 첫 토큰을 뺀 쌍에서는 약합니다. 질문 유무가 원인이라고 아직 단정하지 않습니다.

## 추가 결과: 실제로 답을 생성한 100문항

위의 KL은 다음 토큰 분포의 변화이므로, 앞서 쓰지 않은 100문항에서 답을 실제로 만들어 길이를 쟀습니다. 모든 조건에서 첫 토큰은 `To`로 고정했고, 표의 시드 반복은 같은 프롬프트를 시드만 바꿔 다시 돌린 값입니다. 비는 문항마다 몇 배 달라졌는지를 평균낸 값(기하 평균)이고, 괄호는 95% 구간입니다.

| 프롬프트 변경 | SFT | A1 | A2 |
|---|---|---|---|
| 시드 반복 (잡음의 크기) | 0.98 (0.89–1.08) | 1.05 (0.96–1.16) | 1.01 (0.91–1.11) |
| `step by step` 문구를 뺌 | 0.65 (0.58–0.73) | 0.79 (0.73–0.87) | 0.91 (0.82–1.00) |
| 무관한 지시문으로 교체 | 0.68 (0.61–0.77) | 0.82 (0.75–0.90) | 0.85 (0.78–0.92) |
| 시스템 턴을 없앰 | 0.52 (0.47–0.59) | 0.66 (0.59–0.73) | 0.79 (0.71–0.88) |

| 시스템 턴을 없앴을 때 | SFT | A1 | A2 |
|---|---|---|---|
| 정답률 변화 | −4.2%p (−9.5–+0.5) | +1.2%p (−3.0–+5.8) | −0.2%p (−4.2–+3.8) |
| 긴 풀이 비율 변화 | −37.5%p | −18.0%p | −10.0%p |
| 토큰 합계로 본 비용 비 | 0.71 (0.60–0.81) | 0.66 (0.53–0.80) | 0.85 (0.71–1.02) |

미리 정한 판정은 **보류**입니다. 기준은 "SFT는 뚜렷이 줄고 A2는 그대로(0.90–1.10)"였는데, A2의 시스템 턴 제거가 0.79배로 그 범위를 벗어났습니다. 기준을 결과에 맞춰 바꾸지 않았습니다.

- **확인된 것:** 첫 토큰을 고정해도 시스템 지시문을 바꾸면 세 모델 모두 답이 짧아집니다. 잡음의 크기(0.98–1.05)를 뚜렷이 넘습니다.
- **예상과 달랐던 것:** KL에서 SFT가 A1의 3.5–4.9배였던 차이는 길이에서는 약 1.6배로 줄었습니다. 토큰 합계로 본 실제 비용에서는 SFT와 A1을 가를 수 없습니다(이중비 1.07, 구간 0.83–1.37).
- **조심할 것:** SFT는 정답률 구간이 −9.5%p까지 내려가 정답률을 유지한다고 말할 수 없습니다. 모든 조건이 첫 토큰을 `To`로 고정했으므로, 그대로 생성했을 때의 비용과는 다릅니다. 프롬프트로 추론 길이를 조절할 수 있다는 일반론은 이미 알려져 있어, 여기서 후보로 남기는 것은 "학습 방식에 따라 그 의존 크기가 달라지는가"뿐입니다.

## 추가 결과: 새 100문항에서 순서가 다시 나왔습니다

<!-- xp2 -->
<figure class="xp"><p class="xp-t">실제 입력과 출력 예(새 100문항 중 SFT의 길이 비가 중앙값인 문항, 정답 143)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">The sum of the digits of a two-digit number is $13.$ The difference be …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><b>To</b> solve this problem, let's start by understandin …</div></div><div class="xp-name">기본: 1,176토큰, 긴 풀이 아님</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">The sum of the digits of a two-digit number is $13.$ The difference be …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><b>To</b> solve this problem, let's start by defining the …</div></div><div class="xp-name">step by step만: 666토큰, 긴 풀이 아님</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">The sum of the digits of a two-digit number is $13.$ The difference be …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><b>To</b> solve the problem, let's denote the two-digit n …</div></div><div class="xp-name">상자 지시만: 570토큰, 긴 풀이 아님</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">The sum of the digits of a two-digit number is $13.$ The difference be …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><b>To</b> solve the problem, let's denote the two-digit n …</div></div><div class="xp-name">시스템 턴 없앰: 428토큰, 긴 풀이 아님</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함(채점 안 함)</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span></div><p class="xp-cap">첫 토큰 To는 굵게 표시했고, 그 뒤는 SFT가 생성한 글의 앞부분입니다. 칸 아래에 그 답의 토큰 수와 긴 풀이 여부를 적었습니다. 이 문항은 SFT의 토큰 비가 100문항의 중앙값이 되는 문항으로 골랐고, 답 하나의 길이는 표본마다 크게 흔들립니다.</p></figure>
<figure class="xp"><p class="xp-t">긴 풀이 비율(새 100문항, 첫 토큰 To 고정, 네 모델)</p><div class="xp-bars"><span>기본: SFT</span><span class="xp-track"><i class="xp-fill bad" style="width:78.75%"></i></span><span>78.8%</span><span>기본: A1</span><span class="xp-track"><i class="xp-fill" style="width:39.25%"></i></span><span>39.2%</span><span>기본: A2</span><span class="xp-track"><i class="xp-fill" style="width:37.75%"></i></span><span>37.8%</span><span>기본: QFFT</span><span class="xp-track"><i class="xp-fill" style="width:44.00%"></i></span><span>44.0%</span></div><div class="xp-bars"><span>시스템 턴 없앰: SFT</span><span class="xp-track"><i class="xp-fill" style="width:31.50%"></i></span><span>31.5%</span><span>시스템 턴 없앰: A1</span><span class="xp-track"><i class="xp-fill" style="width:29.00%"></i></span><span>29.0%</span><span>시스템 턴 없앰: A2</span><span class="xp-track"><i class="xp-fill" style="width:27.00%"></i></span><span>27.0%</span><span>시스템 턴 없앰: QFFT</span><span class="xp-track"><i class="xp-fill" style="width:30.00%"></i></span><span>30.0%</span></div><p class="xp-cap">긴 풀이는 답 안에 wait가 네 번 이상이거나, wait와 alternatively가 함께 나온 답입니다. 기본 프롬프트에서는 SFT가 다른 셋보다 훨씬 높고, 시스템 턴을 없애면 네 모델이 거의 같아집니다.</p></figure>
<!-- /xp2 -->

앞 실험에 쓰지 않은 100문항으로 네 모델의 답을 모두 새로 생성했습니다. 첫 토큰은 `To`로 고정했고 조건마다 2번 생성했습니다. A1은 시스템 문장만 있고 질문은 없이 학습한 모델, A2는 거기에 첫 토큰 학습까지 뺀 모델, QFFT는 시스템 문장과 질문을 모두 빼고 학습한 모델입니다. 판정 기준은 답을 보기 전에 일지에 적었습니다.

| 프롬프트 변경 | SFT | A1 | A2 | QFFT |
|---|---|---|---|---|
| 시드 반복 (잡음의 크기) | 1.01 (0.92–1.11) | 1.09 (0.99–1.21) | 1.02 (0.90–1.15) | 0.98 (0.88–1.09) |
| 뜻이 같은 다른 문장 | 0.85 (0.78–0.93) | 0.89 (0.82–0.97) | 0.90 (0.83–0.98) | 0.98 (0.89–1.07) |
| `step by step` 문구를 뺌 (상자 지시만 남김) | 0.60 (0.53–0.66) | 0.75 (0.68–0.83) | 0.80 (0.73–0.89) | 0.80 (0.73–0.88) |
| 상자 지시를 뺌 (`step by step`만 남김) | 0.99 (0.90–1.09) | 1.05 (0.96–1.15) | 1.00 (0.92–1.08) | 1.14 (1.03–1.26) |
| 시스템 턴을 없앰 | 0.44 (0.39–0.49) | 0.72 (0.64–0.81) | 0.76 (0.69–0.83) | 0.78 (0.71–0.85) |

표의 수는 기본 프롬프트 대비 몇 배인지를 문항마다 구해 평균낸 값(기하 평균)이고, 괄호는 95% 구간입니다.

| 시스템 턴을 없앴을 때 | SFT | A1 | A2 | QFFT |
|---|---|---|---|---|
| 정답률 변화 | −1.2%p (−5.2–+2.5) | +3.0%p (−1.2–+7.2) | +0.2%p (−4.5–+4.8) | −4.0%p (−9.0–+0.5) |
| 긴 풀이 비율 (기본 → 시스템 턴 없음) | 78.8% → 31.5% | 39.3% → 29.0% | 37.8% → 27.0% | 44.0% → 30.0% |

| 미리 정한 판정 | 기준 | 결과 |
|---|---|---|
| 잡음 대조 | 시드 반복 네 모델 모두 0.90–1.10 | 통과 |
| 모델 순서 | SFT가 A2, A1보다 더 줄어듦(이중비 0.85·0.90 이하, 구간 위쪽 1 미만) | **재현**: A1 대비 0.61 (0.54–0.70), A2 대비 0.58 (0.51–0.66) |
| SFT 격차 축소 | 시스템 턴을 없애면 A1, A2와의 긴 풀이 격차가 절반 이상 줄어듦 | **재현**: A1 +39.5%p → +2.5%p, A2 +41.0%p → +4.5%p |
| QFFT 대조 | QFFT는 그대로이거나, 함께 줄면 일반 효과 | 보류: QFFT도 0.78배로 줄지만 SFT가 훨씬 더 줄어듭니다 |
| 어느 문구인가 | `step by step`만 남기면 그대로, 상자 지시만 남기면 줄어드는가 | `step by step` 문구: 0.99배, 0.60배 |
| 뜻과 글자 | 뜻이 같은 다른 문장에서 그대로이면 뜻, 줄면 글자 | 보류: 0.85배로 기준 경계에서 판정 불가 |
| 정답 유지 | 구간 아래쪽 −5%p 이상 | SFT 미충족 (−5.2%p), A1·A2 충족, QFFT 미충족 |

**이렇게 읽으면 됩니다.**

- 시스템 턴을 없애면 SFT가 가장 크게 줄었습니다(0.44배). 다른 세 모델은 0.72–0.78배입니다.
- 기본 프롬프트에서 SFT가 다른 세 모델보다 긴 풀이를 35–41%p 더 많이 내는데, 시스템 턴을 없애면 그 차이가 1.5–4.5%p로 줄어듭니다. 앞선 100문항에서도 같은 방향이었습니다(사후 관찰, 격차 축소율 0.62–0.74).
- 시스템 턴이 없을 때 네 모델의 평균적인 답 길이(기하 평균 1,132–1,210토큰)와 긴 풀이 비율(27–31.5%)은 거의 같았습니다. 학습 방식이 달라도 이 조건에서는 거의 구별되지 않습니다. 사후에 발견한 값이어서 다음 실험으로 확인해야 합니다.
- `step by step` 문구만 남겨도 SFT는 줄지 않았습니다.

**아직 말할 수 없는 것.** 학습 방식마다 모델이 하나뿐이라 학습 우연일 수 있습니다. 첫 토큰을 `To`로 고정한 결과라 자연스럽게 생성했을 때와 다를 수 있습니다. SFT의 정답 유지는 구간 아래쪽이 −5.2%p로 기준을 넘지 못했고, 상자 지시가 없는 조건에는 형식 문제도 섞여 있습니다. 프롬프트로 답 길이를 조절한다는 일반론은 이미 알려져 있고, 여기서 후보로 남기는 것은 질문을 보고 학습한 쪽의 초과 장문화가 시스템 지시문에 묶여 있다는 진단입니다.

**이미 있는 연구.** 프롬프트로 답 길이를 조절한다는 일반론은 알려져 있고, 학습과 평가의 시스템 프롬프트 유무를 교차한 실험도 이미 있습니다. [Flint 블로그](https://marcodsn.me/blog/reasoning-compression)와 공개 저장소는 압축된 풀이를 학습한 Qwen3.5-4B에서 이 2×2를 보고했고(심사 전 자료), 프롬프트로 학습한 모델이 프롬프트에 의존한다고 적었습니다. 저희는 긴 풀이를 학습한 모델에서 같은 방향의 의존을 보았고, 다른 점은 학습 때 질문을 봤는가에 따라 그 의존이 달라지는지를 본다는 데 있습니다. `To`로 시작을 강제하면 답이 크게 짧아진다는 보고([2507.03704](https://arxiv.org/abs/2507.03704))도 있어, 네 모델이 모인 현상이 `To`로 인한 바닥 효과일 수 있습니다. 다음 실험에서 이 점을 가립니다.

## 다음

순서대로 진행합니다. 판정 기준은 결과를 보기 전에 일지에 적습니다.

1. 첫 토큰을 고정하지 않고 자연스럽게 생성했을 때도 같은 일이 일어나는지 봅니다. SFT와 A1은 자연스럽게는 거의 `Okay`로 시작하므로, `To`로 강제한 상태와 다를 수 있습니다.
2. 학습할 때 질문을 넣고 빼는 것과 시스템 문장을 넣고 빼는 것을 교차해 작은 모델 네 종류를 학습 시드 두 개씩 학습하고, 이 의존이 학습 형식에서 생기는지, 질문을 봤을 때 더 커지는지 시험합니다.
3. 같은 답의 앞부분을 서로 다른 모델이 이어 쓰게 해, 긴 풀이가 어디에서 결정되는지(이미 쓴 글인가, 모델인가)도 함께 봅니다.
