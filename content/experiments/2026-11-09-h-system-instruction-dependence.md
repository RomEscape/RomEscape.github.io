---
title: 첫 토큰을 고정해도 시스템 지시문을 없애면 답이 짧아진다
date: 2026-11-09
project: QFFT
status: 진행 중
summary: 응답 글을 고정하고 프롬프트의 한 구역만 바꿔 다음 토큰 분포의 변화를 쟀고, 시스템 지시문을 없앴을 때 SFT가 A1보다 3.5–4.9배 크게 움직이는 것을 새 200문항에서 재현했다. 첫 토큰을 고정하고 실제로 답을 생성한 겹치지 않는 새 100문항에서 SFT와 다른 세 모델의 긴 풀이 격차는 시스템 턴이 있을 때 35–41%p, 없을 때 1.5–4.5%p였다. 그러나 첫 토큰을 고정하지 않고 생성하면 시스템 턴 제거의 효과는 A1(0.42배)이 SFT(0.63배)보다 커서, 미리 정한 규칙대로 SFT 고유 주장은 접었다. 같은 문서로 학습 입력만 바꾼 작은 모델 2×2에서는 학습 때 시스템 턴을 본 팔만 평가 때 시스템 턴에 묶였다(시스템 턴을 없앴을 때 0.22배 대 0.84배). 되풀이 고장을 빼면 크기는 줄지만 방향은 같다. 전체 학습 재현이 없어 아직 발견이라고 부르지 않는다.
published: true
---

## 한 줄 요약

첫 토큰이 지나간 뒤(16–256번째 토큰)에도 학습 방식에 따른 차이가 남아 있었습니다. **질문 내용을 바꿨을 때의 반응은 네 모델이 같습니다. 시스템 지시문을 없앴을 때의 반응은 질문을 보고 학습한 SFT만 3.5–4.9배 큽니다.** 미리 정한 기준으로 새 200문항에서 재현됐습니다. 이어서 실제로 답을 생성해 보니 첫 100문항에서는 세 모델이 모두 짧아져(SFT 0.52배, A1 0.66배, A2 0.79배) 판정을 보류했습니다. **겹치지 않는 새 100문항에서는 미리 정한 규칙으로 모델 순서가 재현됐습니다. 첫 토큰을 `To`로 고정했을 때 긴 풀이 비율은 SFT 79%, 나머지 세 모델 38–44%였고, 시스템 턴을 없애면 넷 모두 27–31.5%로 모였습니다.** **첫 토큰을 고정하지 않고 생성하면 시스템 턴 제거의 효과는 오히려 A1(0.42배)이 SFT(0.63배)보다 컸고, 미리 정한 규칙대로 SFT 고유 주장은 접었습니다.** 사후 분석에서는 SFT가 `Okay`로 시작하거나 시스템 턴이 있으면 길게 풀고, 둘 다 없을 때만 짧았습니다. 같은 문서로 학습 입력만 바꾼 작은 모델 네 종류에서는 **학습 때 시스템 턴을 본 팔만 평가 때 시스템 턴에 묶였고**, 미리 정한 규칙으로 학습 형식이 원인이라는 쪽이 지지됐습니다. 다만 그중 일부는 되풀이 고장이어서 크기를 믿으면 안 되고, 전체 학습에서 재현되지 않았으므로 아직 발견이라고 부르지 않습니다.

## 왜 궁금했나

첫 토큰을 `To`로 고정해도 SFT의 긴 풀이 비율은 80.0%인데, 질문 없이 학습한 A1은 42.6%입니다. 두 모델의 학습 차이는 프롬프트에 질문이 있었는지입니다. 그렇다면 프롬프트의 어느 구역이 첫 토큰 뒤의 풀이에 영향을 주는지 재 볼 필요가 있습니다.

답을 새로 생성해서 비교하면 잡음이 큽니다. 같은 설정을 시드만 바꿔도 평균 토큰이 0.75–1.18배 움직였습니다. 그래서 답을 생성하지 않고 저장된 응답 글을 그대로 입력한 뒤, 프롬프트만 바꿔 다음 토큰의 확률 분포가 얼마나 달라지는지(KL)를 쟀습니다. 이 방식에는 생성의 표본 잡음이 없습니다.

## 실험 예시

<!-- xp -->
<figure class="xp"><p class="xp-t">무엇을 바꿨나: 응답 글은 그대로 두고 프롬프트의 한 구역만 바꿈</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Convert the point $(0,3)$ in rectangular coordinates to polar coordina …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><span class="xp-box">To</span> convert the point \((0, 3)\) from rectangular coordinates …</div></div><div class="xp-name">기준: 평가 프롬프트 그대로</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Convert the point $(0,3)$ in rectangular coordinates to polar coordina …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><span class="xp-box">To</span> convert the point \((0, 3)\) from rectangular coordinates …</div></div><div class="xp-name">시스템 턴 없앰</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div></div><div class="xp-del"><div class="">Convert the point $(0,3)$ in rectangular coordinates to polar coordina …</div></div><div class="xp-ctx"><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><span class="xp-box">To</span> convert the point \((0, 3)\) from rectangular coordinates …</div></div><div class="xp-name">질문을 비움</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함(채점 안 함)</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>입력이면서 각 위치의 다음 토큰 분포를 잼</span></div><p class="xp-cap">학습은 하지 않습니다. 이미 학습된 모델에 저장된 A2의 MATH500 응답을 앞 512토큰까지 그대로 입력하고, 답을 새로 만들지 않습니다. 빨간 테두리 안은 모델이 읽기만 하는 문맥이고, 회색은 지운 구역입니다. 응답의 첫 토큰 To도 입력으로만 들어가며 그 예측은 재지 않습니다. 둘째 토큰부터 각 위치에서 다음 토큰 분포가 기준과 얼마나 다른지(KL)를 재고, 아래 수치는 16–256번째 토큰의 평균입니다.</p></figure>
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
<figure class="xp"><p class="xp-t">실제 입력과 출력 예(새 100문항 중 SFT의 길이 비가 중앙값인 문항, 정답 143)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">The sum of the digits of a two-digit number is $13.$ The difference be …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><span class="xp-box">To</span> solve this problem, let's start by understandin …</div></div><div class="xp-name">기본: 1,176토큰, 긴 풀이 아님</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">The sum of the digits of a two-digit number is $13.$ The difference be …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><span class="xp-box">To</span> solve this problem, let's start by defining the …</div></div><div class="xp-name">step by step만: 666토큰, 긴 풀이 아님</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">The sum of the digits of a two-digit number is $13.$ The difference be …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><span class="xp-box">To</span> solve the problem, let's denote the two-digit n …</div></div><div class="xp-name">상자 지시만: 570토큰, 긴 풀이 아님</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">The sum of the digits of a two-digit number is $13.$ The difference be …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><span class="xp-box">To</span> solve the problem, let's denote the two-digit n …</div></div><div class="xp-name">시스템 턴 없앰: 428토큰, 긴 풀이 아님</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함(채점 안 함)</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 새로 생성</span></div><p class="xp-cap">첫 토큰 To는 모델이 고른 것이 아니라 입력 끝에 붙여 넣어 고정한 것이라 빨간 테두리로 표시했고, 그 뒤는 SFT가 생성한 글의 앞부분입니다. 칸 아래에 그 답의 토큰 수와 긴 풀이 여부를 적었습니다. 이 문항은 SFT의 토큰 비가 100문항의 중앙값이 되는 문항으로 골랐고, 답 하나의 길이는 표본마다 크게 흔들립니다.</p></figure>
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

**이미 있는 연구.** 프롬프트로 답 길이를 조절한다는 일반론은 알려져 있고, 학습과 평가의 시스템 프롬프트 유무를 교차한 실험도 이미 있습니다. [Flint 블로그](https://marcodsn.me/blog/reasoning-compression)와 공개 저장소는 압축된 풀이를 학습한 Qwen3.5-4B에서 이 2×2를 보고했고(심사 전 자료), 프롬프트로 학습한 모델이 프롬프트에 의존한다고 적었습니다. 저희는 긴 풀이를 학습한 모델에서 같은 방향의 의존을 보았고, 다른 점은 학습 때 질문을 봤는가에 따라 그 의존이 달라지는지를 본다는 데 있습니다. `To`로 시작을 강제하면 답이 크게 짧아진다는 보고([2507.03704](https://arxiv.org/abs/2507.03704))도 있어, 네 모델이 모인 현상이 `To`로 인한 바닥 효과일 수 있습니다. 이 점은 아래 절에서 다룹니다.

## 추가 결과: 첫 토큰을 건드리지 않으면 순서가 뒤집혔습니다

<!-- xp3 -->
<figure class="xp"><p class="xp-t">실제 입력과 출력 예(같은 문항, SFT, 첫 토큰 고정 없음, 정답 3)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">A triangle has sides measuring 1 unit and 3 units. The length of the t …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><b>Okay,</b> so I have this problem here: A triangle ha …</div></div><div class="xp-name">시스템 턴 있음: 1,068토큰, 긴 풀이</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">A triangle has sides measuring 1 unit and 3 units. The length of the t …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><b>Okay,</b> so I have this problem here about a triang …</div></div><div class="xp-name">시스템 턴 없음, Okay로 시작: 1,115토큰, 긴 풀이</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">A triangle has sides measuring 1 unit and 3 units. The length of the t …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><b>To</b> determine the length of the third side of a t …</div></div><div class="xp-name">시스템 턴 없음, 다른 단어로 시작: 384토큰, 긴 풀이 아님</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함(채점 안 함)</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 새로 생성</span></div><p class="xp-cap">굵은 글자가 모델이 스스로 고른 첫 단어이고, 그 뒤는 생성된 글의 앞부분입니다. 시스템 턴이 없을 때 두 번 생성한 답 중 하나는 Okay로, 하나는 다른 단어로 시작한 문항 30개에서, 두 답의 토큰 비가 중앙값인 문항을 골랐습니다. 답 하나의 길이는 표본마다 크게 흔들립니다.</p></figure>
<figure class="xp"><p class="xp-t">긴 풀이 비율과 기하 평균 토큰(새 100문항, 첫 토큰을 건드린 경우와 건드리지 않은 경우)</p><div class="xp-bars"><span>SFT: 시스템 턴 있음, 자연 시작</span><span class="xp-track"><i class="xp-fill" style="width:90.25%"></i></span><span>90.2%, 3,282토큰</span><span>SFT: 시스템 턴 있음, To 고정</span><span class="xp-track"><i class="xp-fill" style="width:78.75%"></i></span><span>78.8%, 2,738토큰</span><span>SFT: 시스템 턴 없음, 자연 시작</span><span class="xp-track"><i class="xp-fill" style="width:62.00%"></i></span><span>62.0%, 2,053토큰</span><span>SFT: 시스템 턴 없음, To 고정</span><span class="xp-track"><i class="xp-fill bad" style="width:31.50%"></i></span><span>31.5%, 1,208토큰</span></div><div class="xp-bars"><span>A1: 시스템 턴 있음, 자연 시작</span><span class="xp-track"><i class="xp-fill" style="width:87.00%"></i></span><span>87.0%, 2,935토큰</span><span>A1: 시스템 턴 있음, To 고정</span><span class="xp-track"><i class="xp-fill" style="width:39.25%"></i></span><span>39.2%, 1,572토큰</span><span>A1: 시스템 턴 없음, 자연 시작</span><span class="xp-track"><i class="xp-fill" style="width:30.00%"></i></span><span>30.0%, 1,222토큰</span><span>A1: 시스템 턴 없음, To 고정</span><span class="xp-track"><i class="xp-fill bad" style="width:29.00%"></i></span><span>29.0%, 1,132토큰</span></div><div class="xp-bars"><span>SFT, 시스템 턴 없음, 자연 시작 중 Okay류로 시작</span><span class="xp-track"><i class="xp-fill" style="width:85.29%"></i></span><span>85.3%, 2,914토큰</span><span>SFT, 시스템 턴 없음, 자연 시작 중 다른 단어로 시작</span><span class="xp-track"><i class="xp-fill bad" style="width:37.76%"></i></span><span>37.8%, 1,425토큰</span></div><p class="xp-cap">자연 시작은 첫 토큰을 고정하지 않고 생성한 답, To 고정은 첫 토큰을 To로 넣고 이어 쓴 답입니다. 시스템 턴이 있는 칸은 같은 프롬프트로 시드만 바꿔 두 번 돌린 400행을 합쳤고, 없는 칸은 200행입니다. 맨 아래 두 줄은 답을 본 뒤 시작 단어로 나눈 값이라 선택 편향이 남아 있습니다.</p></figure>
<!-- /xp3 -->

앞 실험은 모든 답의 첫 토큰을 `To`로 고정했습니다. 그런데 SFT와 A1은 고정하지 않으면 대부분 `Okay`로 시작합니다. 그래서 같은 새 100문항에서 첫 토큰을 고정하지 않고 다시 생성했습니다. 조건마다 2번씩 모델당 600개를 만들었고, 판정 기준은 답을 보기 전에 일지에 적었습니다.

| 미리 정한 판정 | 기준 | 결과 |
|---|---|---|
| 잡음 대조 | 시드 반복이 0.90–1.10 | 통과: SFT 0.98, A1 1.07 |
| 시스템 턴을 없앨 때 길이 | SFT만 줄면 SFT 관문, 둘 다 줄면 공통 단축 | **공통 단축**: SFT 0.63 (0.55–0.71), A1 0.42 (0.36–0.47) |
| 첫 토큰 이동 | `Okay`류 비율이 20%p 이상 달라짐 | 이동: SFT 100% → 51%, A1 89% → 1% |
| 정답 유지 | 구간 아래쪽 −5%p 이상 | 둘 다 미충족: SFT −5.2%p (−10.5–+0.0), A1 −1.8%p (−6.8–+3.0) |

첫 토큰을 `To`로 고정했을 때는 SFT(0.44배)가 A1(0.72배)보다 훨씬 많이 줄었는데, 자연스럽게 시작하게 하니 반대로 A1(0.42배)이 SFT(0.63배)보다 더 줄었습니다. 미리 정한 규칙대로 **"자연스럽게 생성할 때 시스템 턴에 묶이는 것은 SFT만의 일"이라는 주장은 접습니다.** `To` 고정 상태의 결과는 그대로 남습니다.

**왜 뒤집혔나(사후 분석).** 표의 수는 기하 평균 토큰과 긴 풀이 비율입니다.

| | 시스템 턴 있음 | 시스템 턴 없음 |
|---|---|---|
| SFT, 자연 시작 | 3,282토큰, 90.2% (`Okay`류 100%) | 2,053토큰, 62.0% (`Okay`류 51%) |
| SFT, `To` 고정 | 2,738토큰, 78.8% | 1,208토큰, 31.5% |
| A1, 자연 시작 | 2,935토큰, 87.0% (`Okay`류 89%) | 1,222토큰, 30.0% (`Okay`류 1%) |
| A1, `To` 고정 | 1,572토큰, 39.2% | 1,132토큰, 29.0% |

- 시스템 턴을 없애면 첫 단어가 바뀝니다. A1은 `Okay`류가 거의 사라지고, SFT는 절반이 남습니다.
- SFT가 시스템 턴 없이 `Okay`로 시작한 답은, 같은 문항에서 시스템 턴이 있을 때의 `Okay` 답과 길이가 같았습니다(0.99배, 0.87–1.13, 66문항). 다른 단어로 시작한 답은 0.39배(0.32–0.48, 64문항)였습니다.
- 같은 문항, 같은 프롬프트에서 2번 생성했을 때 한 번은 `Okay`로, 한 번은 다른 단어로 시작한 경우가 30문항 있었습니다. 이 안에서도 다른 단어 쪽이 0.32배(0.22–0.46)로 짧았습니다.
- 시스템 턴이 없을 때 SFT가 자연스럽게 `To`로 시작한 답은 `To`를 강제한 답과 길이가 같았습니다(1.05배, 0.90–1.24, 55문항). 네 모델이 모였던 값은 `To` 강제의 부작용만은 아니고, `To`로 시작하고 시스템 턴이 없는 경로의 길이입니다. `Okay`로 시작하면 시스템 턴이 없어도 길게 풀므로, 학습 방식과 상관없는 바닥값이라고 볼 수는 없습니다.

즉 SFT는 **`Okay`로 시작하거나 시스템 턴이 있거나, 둘 중 하나만 있어도 길게 풀고 둘 다 없을 때만 짧습니다.** A1은 시스템 턴이 있어도 `To`로 시작하면 39%에 그치므로, 거의 `Okay`로 시작할 때만 깁니다.

**아직 말할 수 없는 것.** `Okay`로 시작할지는 모델이 고른 것이어서 선택 편향이 남아 있고, 이 분석은 답을 본 뒤에 한 것입니다. 또 시스템 턴 제거로 줄어든 만큼 정답률을 지켰다고 말할 수 없습니다. 그래서 겹치지 않는 문항에서 `Okay`를 강제해 다시 확인합니다.

## 추가 결과: 학습 때 시스템 턴을 봐야 시스템 턴에 묶입니다(작은 학습)

<!-- xp4 -->
<figure class="xp"><p class="xp-t">학습 때 보여 준 입력 네 가지(위)와 평가 결과(아래, 기하 평균 토큰, 첫 토큰 To 고정, 새 100문항, 학습 시드 2개 합침)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Find the last three digits of the product of the positive roots of $\s …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find the last three digits of …</div></div><div class="xp-name">시스템 턴 + 질문</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div></div><div class="xp-del"><div class="">Find the last three digits of the product of the positive roots of $\s …</div></div><div class="xp-ctx"><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find the last three digits of …</div></div><div class="xp-name">시스템 턴 + 빈 질문</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Find the last three digits of the product of the positive roots of $\s …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find the last three digits of …</div></div><div class="xp-name">질문만</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div></div><div class="xp-del"><div class="">Find the last three digits of the product of the positive roots of $\s …</div></div><div class="xp-ctx"><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find the last three digits of …</div></div><div class="xp-name">둘 다 없음</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함(채점 안 함)</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>다음 토큰을 맞히도록 채점</span></div><div class="xp-bars"><span>시스템 턴 + 질문: 평가에 시스템 턴 있음</span><span class="xp-track"><i class="xp-fill" style="width:95.76%"></i></span><span>3,447토큰, 상한 도달 75/200</span><span>시스템 턴 + 질문: 평가에 시스템 턴 없음</span><span class="xp-track"><i class="xp-fill bad" style="width:21.26%"></i></span><span>765토큰, 상한 도달 11/200</span><span>시스템 턴 + 빈 질문: 평가에 시스템 턴 있음</span><span class="xp-track"><i class="xp-fill" style="width:44.19%"></i></span><span>1,591토큰, 상한 도달 36/200</span><span>시스템 턴 + 빈 질문: 평가에 시스템 턴 없음</span><span class="xp-track"><i class="xp-fill bad" style="width:20.10%"></i></span><span>723토큰, 상한 도달 11/200</span><span>질문만: 평가에 시스템 턴 있음</span><span class="xp-track"><i class="xp-fill" style="width:32.91%"></i></span><span>1,185토큰, 상한 도달 28/200</span><span>질문만: 평가에 시스템 턴 없음</span><span class="xp-track"><i class="xp-fill bad" style="width:27.60%"></i></span><span>994토큰, 상한 도달 21/200</span><span>둘 다 없음: 평가에 시스템 턴 있음</span><span class="xp-track"><i class="xp-fill" style="width:22.33%"></i></span><span>804토큰, 상한 도달 11/200</span><span>둘 다 없음: 평가에 시스템 턴 없음</span><span class="xp-track"><i class="xp-fill bad" style="width:20.58%"></i></span><span>741토큰, 상한 도달 12/200</span></div><p class="xp-cap">학습 문서, 순서, 시드는 네 팔이 같고 응답 토큰 라벨도 같습니다. 회색으로 지운 부분만 학습 입력에서 뺐습니다. 시스템 턴과 질문을 함께 본 팔의 기본 조건은 200번 중 75번이 32,000토큰 상한까지 같은 글을 되풀이했습니다. 위의 평균에는 이 고장이 그대로 들어 있습니다.</p></figure>
<!-- /xp4 -->

전체 학습에서는 학습 형식마다 모델이 하나뿐이어서, 앞의 차이가 학습 형식 때문인지 확인할 수 없었습니다. 그래서 같은 문서를 같은 순서로 쓰되 학습 입력만 네 가지로 바꾼 작은 모델을 학습했습니다(문서 400개, 400단계, 학습 시드 2개). 평가는 위와 같은 새 100문항을 쓰고 첫 토큰은 `To`로 고정했습니다.

**미리 정한 기준과 결과.** 값은 시스템 턴을 없앴을 때 답 길이가 몇 배가 되는지입니다(문항 짝 기하 평균, 대괄호는 95% 구간). 1보다 작을수록 시스템 턴에 의존합니다.

| 학습 때 본 입력 | 시스템 턴을 없앴을 때 | 학습 시드별 |
|---|---:|---|
| 시스템 턴 + 질문 | 0.22배 [0.17, 0.28] | 0.31, 0.16 |
| 시스템 턴 + 빈 질문 | 0.45배 [0.38, 0.55] | 0.60, 0.34 |
| 질문만 | 0.84배 [0.72, 0.98] | 0.91, 0.77 |
| 둘 다 없음 | 0.92배 [0.80, 1.06] | 1.04, 0.82 |

| 비교 | 값 | 미리 정한 판정 |
|---|---:|---|
| 질문을 볼 때: 학습 시스템 턴 있음 ÷ 없음 | 0.26배 [0.20, 0.35] | 학습 형식이 원인이라는 쪽을 지지 |
| 시스템 턴을 볼 때: 질문 있음 ÷ 빈 질문 | 0.49배 [0.37, 0.63] | 질문을 보이면 의존이 커짐(재현) |
| 상호작용(앞의 비 ÷ 시스템 턴이 없을 때의 같은 비) | 0.54배 [0.39, 0.75] | 있음 |
| 시스템 턴이 없을 때: 질문 있음 ÷ 빈 질문 | 0.91배 [0.73, 1.13] | 표시만 함 |

**먼저 의심한 점.** 가장 많이 줄어든 `시스템 턴 + 질문` 팔은 시스템 턴이 있을 때 200번 중 75번이 32,000토큰 상한까지 같은 글을 되풀이했습니다. 시스템 턴이 없으면 11번입니다. 작은 학습이 만든 고장이 비를 부풀리므로, 긴 토큰을 잘라 계산한 값과 상한에 닿은 쌍을 뺀 값을 함께 봤습니다. 아래 표는 답을 본 뒤 계산한 값입니다.

| 계산 방식 | 시스템 턴 + 질문 | 질문만 | 학습 시스템 턴 있음 ÷ 없음 | 상호작용 |
|---|---:|---:|---:|---:|
| 미리 정한 계산(전체) | 0.22 | 0.84 | 0.26 [0.20, 0.35] | 0.54 [0.39, 0.75] |
| 8,192토큰에서 자름 | 0.34 | 0.88 | 0.39 [0.33, 0.46] | 0.66 [0.53, 0.81] |
| 4,096토큰에서 자름 | 0.43 | 0.91 | 0.47 [0.42, 0.53] | 0.72 [0.62, 0.84] |
| 상한에 닿은 쌍 제외 | 0.55 | 0.96 | 0.56 [0.48, 0.63] | 0.75 [0.64, 0.87] |

방향은 모든 계산에서 같고 구간도 1 아래입니다. 크기는 많이 줄어듭니다. 실제 합산 토큰(산술 평균)으로 보면 학습 시스템 턴 있음 ÷ 없음은 0.26배 [0.14, 0.44]이지만 상호작용은 0.73배 [0.33, 1.48]로 구간이 1을 포함합니다. 상호작용을 총비용의 사실로 말하지는 않습니다. 고장이 없는 행만 모으면 긴 풀이 비율은 `시스템 턴 + 질문` 팔이 시스템 턴이 있을 때 21.6%, 없을 때 0.0%이고, `질문만` 팔은 양쪽 모두 0.6%입니다.

**읽기.** 학습 입력에 시스템 턴이 있던 두 팔은 평가 때 시스템 턴이 없으면 크게 줄고, 없던 두 팔은 거의 줄지 않습니다. 질문을 보이면 이 의존이 더 커집니다. 학습 형식과 평가 조건이 일치하는 칸끼리 봐도 `시스템 턴 + 질문`이 3,447토큰, `질문만`이 994토큰이어서 "같은 형식이면 길게 쓴다"로는 설명되지 않습니다.

**풀이 어디까지 영향을 줄까.** 저장해 둔 KL 지도를 응답 위치별로 나눠 봤습니다(답을 본 뒤의 분석입니다). 시스템 턴 제거에 대한 SFT의 민감도는 16–64번째 토큰에서 가장 크고 뒤로 갈수록 줄지만, 256–512번째 토큰에서도 새 문항 묶음에서 A1의 2.1–2.6배입니다. 질문을 비우는 대조에서는 그 위치의 SFT÷A1이 1.0–1.2배입니다. 다음 한 토큰의 분포 차이일 뿐이어서 실제 답 길이가 달라지는지는 아래 2번 실험으로 확인합니다.

**말할 수 없는 것.** 작은 학습(400단계)의 결과이고 긴 풀이 일부는 고장입니다. 정답률은 고장 때문에 비교하기 어렵습니다. 첫 토큰을 `To`로 고정한 조건이고, 학습 시드 2개는 문서 집합의 절반이 다릅니다. 전체 학습에서 시스템 턴만 뺀 모델은 아직 없습니다. 학습과 평가의 시스템 프롬프트를 교차한 실험 자체는 앞 절에 적은 대로 이미 있고, 질문 유무와 교차한 칸만 새로울 수 있습니다. **그래서 아직 발견이 아니라 후보입니다.**

## 다음

순서대로 진행합니다. 판정 기준은 결과를 보기 전에 일지에 적습니다.

1. 같은 답의 앞부분을 서로 다른 모델이 이어 쓰게 해, 긴 풀이가 어디에서 결정되는지(이미 쓴 글인가, 모델인가) 봅니다(진행 중).
2. 같은 답의 앞부분을 그대로 두고 풀이 도중에 시스템 턴만 없애거나 넣어 이어 쓰게 합니다. 시스템 턴이 풀이 앞부분에서 한 번 작용하는지, 풀이 내내 읽히는지를 실제 답 길이로 가립니다.
3. 겹치지 않는 100문항에서 첫 토큰을 `Okay`로 강제하고 시스템 턴을 없애, 위의 "둘 중 하나만 있어도 길다"가 재현되는지 봅니다.
4. 작은 학습에서 나온 원인이 전체 학습에서도 보이는지는 시스템 턴만 뺀 전체 학습이 있어야 답할 수 있습니다.
