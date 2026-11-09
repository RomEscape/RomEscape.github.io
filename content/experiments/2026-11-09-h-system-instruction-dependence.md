---
title: 첫 토큰이 지나간 뒤에도 남는 차이, SFT만 시스템 지시문에 매달린다
date: 2026-11-09
project: QFFT
status: 진행 중
summary: 응답 글을 고정하고 프롬프트의 한 구역만 바꿔 모델의 다음 토큰 분포가 얼마나 달라지는지 쟀다. 질문 내용을 바꿨을 때는 네 모델이 똑같이 움직였지만, 시스템 지시문을 없앴을 때는 SFT만 3.5–4.9배 크게 움직였다. 새 200문항에서 재현됐다. 실제 답 길이로 이어지는지는 아직 모른다.
published: true
---

## 한 줄 요약

첫 토큰이 지나간 뒤(16–256번째 토큰)에도 학습 방식에 따른 차이가 남아 있었습니다. **질문 내용을 바꿨을 때의 반응은 네 모델이 같습니다. 시스템 지시문을 없앴을 때의 반응은 질문을 보고 학습한 SFT만 3.5–4.9배 큽니다.** 미리 정한 기준으로 새 200문항에서 재현됐습니다. 다만 이것은 다음 토큰 분포의 변화이고, 실제 답 길이가 달라지는지는 아직 검증 중입니다.

## 왜 궁금했나

첫 토큰을 `To`로 고정해도 SFT의 긴 풀이 비율은 80.0%인데, 질문 없이 학습한 A1은 42.6%입니다. 두 모델의 학습 차이는 프롬프트에 질문이 있었는지입니다. 그렇다면 프롬프트의 어느 구역이 첫 토큰 뒤의 풀이에 영향을 주는지 재 볼 필요가 있습니다.

답을 새로 생성해서 비교하면 잡음이 큽니다. 같은 설정을 시드만 바꿔도 평균 토큰이 0.75–1.18배 움직였습니다. 그래서 답을 생성하지 않고 저장된 응답 글을 그대로 입력한 뒤, 프롬프트만 바꿔 다음 토큰의 확률 분포가 얼마나 달라지는지(KL)를 쟀습니다. 이 방식에는 생성의 표본 잡음이 없습니다.

## 실험 예시

<!-- xp -->
<figure class="xp"><p class="xp-t">무엇을 바꿨나: 응답 글은 그대로 두고 프롬프트의 한 구역만 바꿈</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Convert the point $(0,3)$ in rectangular coordinates to polar coordina …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To convert the point \((0, 3)\) from rectangular coordinates …</div></div><div class="xp-name">기준: 평가 프롬프트 그대로</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Convert the point $(0,3)$ in rectangular coordinates to polar coordina …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To convert the point \((0, 3)\) from rectangular coordinates …</div></div><div class="xp-name">시스템 턴 없앰</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div></div><div class="xp-del"><div class="xp-role">user</div><div class="">Convert the point $(0,3)$ in rectangular coordinates to polar coordina …</div></div><div class="xp-ctx"><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To convert the point \((0, 3)\) from rectangular coordinates …</div></div><div class="xp-name">질문을 비움</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함(채점 안 함)</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span></div><p class="xp-cap">저장된 MATH500 응답을 앞 512토큰까지 그대로 입력합니다. 빨간 테두리 안은 모델이 읽는 문맥이고, 회색은 지운 구역입니다. 답을 새로 만들지 않고, 각 위치에서 다음 토큰 분포가 기준과 얼마나 다른지(KL)만 잽니다.</p></figure>
<figure class="xp"><p class="xp-t">확인 실험(새 200문항, 응답 글 A2): 16–256번째 토큰의 평균 KL</p><div class="xp-bars"><span>시스템 턴 없앰: SFT</span><span class="xp-track"><i class="xp-fill bad" style="width:32.48%"></i></span><span>0.162</span><span>시스템 턴 없앰: A1</span><span class="xp-track"><i class="xp-fill" style="width:6.66%"></i></span><span>0.033</span><span>시스템 턴 없앰: A2</span><span class="xp-track"><i class="xp-fill" style="width:4.67%"></i></span><span>0.023</span><span>시스템 턴 없앰: QFFT</span><span class="xp-track"><i class="xp-fill" style="width:10.03%"></i></span><span>0.050</span></div><div class="xp-bars"><span>질문을 비움: SFT</span><span class="xp-track"><i class="xp-fill" style="width:84.45%"></i></span><span>0.422</span><span>질문을 비움: A1</span><span class="xp-track"><i class="xp-fill" style="width:83.21%"></i></span><span>0.416</span><span>질문을 비움: A2</span><span class="xp-track"><i class="xp-fill" style="width:82.70%"></i></span><span>0.413</span><span>질문을 비움: QFFT</span><span class="xp-track"><i class="xp-fill" style="width:81.84%"></i></span><span>0.409</span></div><p class="xp-cap">질문을 비웠을 때의 변화는 네 모델이 거의 같고, 시스템 턴을 없앴을 때의 변화는 SFT만 큽니다. 응답 글을 SFT나 QFFT가 쓴 답으로 바꿔도 방향이 같습니다.</p></figure>
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

## 다음

남은 검증입니다.

1. 100문항에서 지시문을 없애거나 바꾼 뒤 실제로 답을 생성해, 같은 조건 반복의 변동을 넘어 길이가 달라지는지 확인합니다.
