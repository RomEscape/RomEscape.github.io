---
title: 11월 12일 보고 정리, QFFT는 무엇을 바꾸는가와 발견 네 가지
date: 2026-11-12
project: QFFT
status: 진행 중
summary: QFFT가 바꾸는 것은 어디서 되짚어야 하는지 아는 능력이 아니라 되짚는 문턱이고, 그 효과는 표준 SFT 모델에서 추론 때 학습 프롬프트만 빼도 대부분 재현된다. 기반 모델로 먼저 싸게 풀고 답이 갈릴 때만 긴 추론으로 넘기면 QFFT 한 번보다 정답률이 높고 토큰이 적다. 검증된 새 방법은 아직 없으며, 참신성이 있는 발견 위주로 예시와 함께 정리한다.
published: true
---

## 한 줄 요약

> **정정 (11월 12일 09시 50분).** 이 글에 적힌 MATH500 정답률은 원본 채점 스크립트 기준입니다. `\boxed{}` 없이 쓴 답과 표기만 다른 같은 답을 바로잡아 모든 조건을 다시 채점했고, 결론은 그대로이며 값만 1–4%포인트 올랐습니다 (예: SFT 80.5% → 시스템 프롬프트 제거 80.9%, QFFT 81.4% → 82.5%, "싼 풀이 먼저" 방식의 이득 +2.0%p → +1.7%p [+0.5, +2.8]). 표와 방법은 [학습 프롬프트 빼기](2026-11-12-b-drop-training-prompt.html)의 맨 위 "정정" 절에 있습니다.


**QFFT가 바꾸는 것은 "어디서 되짚어야 하는지 아는 능력"이 아니라 "되짚는 문턱"입니다.** 그리고 그 효과는 표준 SFT 모델에서 추론 때 학습 프롬프트만 빼도 대부분 재현됩니다.

| 발견 | 핵심 수치 | 근거의 굳기 |
|---|---|---|
| 1. 학습 형식을 바꿔도 가려내는 정도는 같고 되짚는 문턱만 다르다 | 여섯 모델의 가려내는 정도 1.13–1.21. 문턱은 표준 SFT 0.80, 나머지 1.04–1.11 | 측정 끝. 재는 척도에 따라 표현이 조금 달라짐 |
| 2. 표준 SFT에서 학습 프롬프트만 빼면 QFFT 수준이 된다 | MATH500에서 토큰 0.60배 [0.57, 0.64], 정답률 80.2% 대 79.6%. 같은 프롬프트로 학습한 다른 모델은 0.39배. 그 프롬프트 없이 학습한 모델은 1.04배, 기반 모델은 0.95배, QFFT는 0.78배. 묶인 곳은 시스템 프롬프트 칸이 아니라 지시 문장(답 형식 지시만 질문 뒤에 붙여도 0.81배로 돌아옴). 시스템 프롬프트를 빼면 RAK가 SFT 5.75 → 22.62, 질문 비움 SFT 7.35 → 49.54, QFFT 38.98 → 47.75 | 미리 정한 판정 "재현". 학습은 모델마다 한 번 |
| 3. QFFT 한 번보다 "싼 풀이 먼저, 갈리면 긴 추론"이 낫다 | QFFT 한 번 대비 MATH500 +1.6%p(토큰 0.87배), GSM8K +2.0%p(0.97배. 처음 적은 +6.6%p는 채점 방식 때문에 부풀려진 값), AIME25는 같음 | 저장된 답으로 고른 방식을 새 표본과 미리 정한 규칙으로 확인함(MATH500 +2.0%p, 토큰 0.89배) |
| 4. 틀린 지점만 가르치면 "틀렸을 때"가 아니라 "어려운 문제에서" 켜는 것을 배운다 | 가려내는 정도 0.74(일곱 모델 중 최저), 헛경보가 자료 난도를 따라 6.3%에서 20.1%로 | 미확정. 통제 실험 필요 |

검증된 새 방법은 아직 없습니다. 아래는 참신성이 있는 발견 위주의 정리입니다. 모델과 실험의 이름은 [실험 이름표](2026-11-12-a-status-names-and-plan.html)를 따릅니다.

## 배경: QFFT와 이 연구의 질문

- **긴 추론 학습의 문제.** 어려운 수학 문제의 긴 풀이로 미세조정한 모델(표준 SFT)은 쉬운 문제에도 길게 풉니다. MATH500에서 기반 모델은 평균 635토큰을 쓰는데 표준 SFT는 6,576토큰을 씁니다.
- **QFFT.** 학습할 때 질문을 지우고 풀이 글만 보여 주는 방법입니다. 논문은 이렇게 학습한 모델이 쉬운 문제는 짧게, 어려운 문제는 길게 푼다고 보고합니다. 우리 재현에서도 평균 토큰이 4,630으로 줄고 정답률은 80.3%로 유지됐습니다.
- **이 연구의 질문.** QFFT는 정확히 무엇을 바꾸는가. "길게 풀어야 할 곳을 더 잘 알게" 되는가, 아니면 "길게 푸는 일 자체를 덜 하게" 되는가. 그리고 같은 효과를 다시 학습하지 않고 얻을 수 있는가.

## 낱말

| 낱말 | 뜻 | 예 |
|---|---|---|
| 반성 표지 | 풀이 도중 앞을 되짚는 말 | "Wait, that doesn't seem right." |
| 문턱 | 반성 표지를 얼마나 쉽게 내는가. 높을수록 덜 냅니다 | 문턱 0.80인 모델이 1.04인 모델보다 자주 되짚습니다 |
| 가려내는 정도 | 틀린 단계 뒤와 오류가 없는 단계 뒤에서 되짚는 비율이 얼마나 다른가. 클수록 맞는 곳에서 되짚습니다 | 틀린 뒤 40%, 정상 뒤 9%면 약 1.1 |
| 헛경보 | 오류가 없는데 되짚는 것 | |
| 토큰 비(문항 기준) | 같은 문항에서 두 조건의 평균 토큰을 나눈 값을 문항에 걸쳐 곱셈 평균한 것 | 0.60배면 보통의 문항에서 40% 짧아짐 |
| 토큰 비(전체) | 모든 문항의 토큰을 더해 나눈 값. 실제 비용의 비율 | |
| 답 틀 | 최종 답을 넣는 `\boxed{}`. 원본 채점은 이 안의 답만 봅니다 | |

## 발견 1. 학습 형식을 바꿔도 가려내는 정도는 같고 문턱만 다르다

QFFT를 포함해 학습 형식을 하나씩 바꾼 모델들은 틀린 풀이와 맞는 풀이를 가려서 되짚는 정도가 같았고, 되짚는 말을 얼마나 쉽게 내는가만 달랐습니다.

### 예시: 틀린 단계 뒤와 오류가 없는 단계 뒤

<!-- xp0 -->
<figure class="xp"><p class="xp-t">실제 입력과 출력 예(표준 SFT). 문제: Seth is twice as old as Brooke. In 2 years, the sum of their ages will be 28. How old is Seth?</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="">앞부분의 끝: … ld and Brooke will be \(B + 2\) years old. The sum of their ages in two years will be 28, so we can write another equation: \[(S + 2) + (B + 2) = 28\]</div></div><div class="">Simplifying this equation, we can combine like terms: \[S + B + 4 = 28\] Subtracting 4 from both sides gives: \[S + B = 24\] Now,  …</div></div><div class="xp-name">오류가 없는 단계 뒤: 8번 중 0번 되짚음</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="">앞부분의 끝(틀린 단계): Substituting the first equation into the second equation, we get: \[2B + 4 + B + 2 = 28\] \[3B + 6 = 28\] \[3B = 22\] \[B = \frac{22}{3}\]</div></div><div class="">But <span class="xp-hit">wait</span>, this gives Brooke's age as 22/3, which is approximately 7.333 years. Then Seth's age would be 22/3 * 2 = 44/3 ≈ 14.666 y …</div></div><div class="xp-name">틀린 단계 뒤: 8번 중 7번 되짚음</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>모델에게 준 풀이 앞부분(다른 모델이 쓴 풀이)</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 이어 쓴 글의 앞부분</span></div><p class="xp-cap">371문항 전체에서 앞 두 문장 안에 Wait가 나온 비율은 표준 SFT가 틀린 단계 뒤 40.9%, 오류가 없는 단계 뒤 8.5%이고, QFFT가 31.5%, 4.5%입니다. QFFT는 두 경우 모두에서 덜 되짚습니다. 틀린 단계 뒤에서만 더 되짚는 것이 아니므로, 가려내는 정도가 아니라 문턱이 달라진 것입니다.</p></figure>
<!-- /xp0 -->

**어떻게 쟀나.**

1. 사람이 첫 오류 단계를 표시해 둔 풀이 371문항을 씁니다(공개 자료 ProcessBench의 GSM8K, MATH, 올림피아드 문제 풀이).
2. 같은 문항에서 두 가지 앞부분을 만듭니다. 오류가 없는 단계까지의 앞부분과, 첫 틀린 단계까지 포함한 앞부분입니다.
3. 모델에게 그 뒤를 이어 쓰게 합니다(상태마다 8회).
4. 이어 쓴 글의 앞 두 문장 안에 "Wait"가 나오는지 셉니다.
5. 틀린 단계 뒤에 나온 비율과 오류가 없는 단계 뒤에 나온 비율로 두 값을 냅니다. 두 비율의 차이가 "가려내는 정도"이고, 두 비율이 함께 얼마나 낮은가가 "문턱"입니다.

**표 읽는 법.** 문턱이 높을수록 덜 되짚습니다. 가려내는 정도는 여섯 모델 모두 1.13–1.21 안에 있어 표에서 뺐습니다.

| 모델 | 문턱 |
|---|---|
| 표준 SFT | 0.80 |
| 질문 비움 SFT | 1.04 |
| 시스템 프롬프트 없이 학습한 SFT | 1.04 |
| QFFT | 1.09 |
| 질문 비움, 첫 토큰 미학습 SFT | 1.11 |

- 표준 SFT만 문턱이 낮습니다(자주 되짚음). 나머지 네 모델은 같은 수준입니다.
- 표준 SFT도 평가 때 시스템 프롬프트를 빼면 문턱이 0.35 올라 [+0.29, +0.41] 다른 모델과 같아집니다. 시스템 프롬프트 없이 학습한 SFT는 0.06만 변합니다.
- QFFT 논문은 불확실하거나 틀렸을 때 긴 반성으로 넘어간다고 설명합니다. 이 측정에서는 QFFT가 표준 SFT보다 덜 되짚을 뿐, 더 잘 가려서 되짚지는 않았습니다.
- 주의: "가려내는 정도가 같다"는 재는 척도에 따라 달라집니다. 확률 차로 보면 표준 SFT가 4.7%포인트 높고, 비율로 보면 QFFT 쪽이 높습니다. 어느 척도에서도 QFFT가 더 잘 가려낸다는 일관된 증거는 없습니다.

자세한 기록은 [풀이 뒷부분 편향 기록](2026-11-11-b-later-part-bias-candidates.html)에 있습니다.

## 발견 2. 표준 SFT에서 학습 프롬프트만 빼면 QFFT 수준이 된다

표준 SFT 모델은 추론 때 학습에 쓴 시스템 프롬프트만 빼도 답 길이가 문항 기준 0.60배로 줄고 정답률은 그대로입니다. 그 프롬프트 없이 학습한 SFT와 미세조정 전 기반 모델은 변하지 않습니다. 보지 않고 학습한 QFFT는 0.78배로 조금 줄어듭니다(11월 12일 아침 추가).

### 예시: 같은 문항에서 시스템 프롬프트만 뺐을 때

<!-- xp -->
<figure class="xp"><p class="xp-t">실제 입력과 출력 예(표준 SFT, MATH500의 한 문항, 정답 2). 같은 문항에서 시스템 프롬프트만 뺐습니다</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find an integer x that satisfies the inequality $\f …</div></div><div class="xp-name">표준 프롬프트: 2,630토큰, 정답</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To determine the integer \( x \) that satisfies the inequality \( \fra …</div></div><div class="xp-name">시스템 프롬프트 제거, To로 시작한 답: 750토큰, 정답</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find an integer x that fits between 1/4 and 1/3 whe …</div></div><div class="xp-name">시스템 프롬프트 제거, Okay로 시작한 답: 1,245토큰, 정답</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>모델이 읽는 프롬프트</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 뺀 부분</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 쓴 답의 앞부분</span></div><p class="xp-cap">이 문항의 평균 토큰은 표준 프롬프트 1,682, 시스템 프롬프트 제거 1,013로 0.60배입니다. 시스템 프롬프트를 빼면 같은 문항에서도 답이 "To"로 시작하기도 하고 "Okay"로 시작하기도 합니다.</p></figure>
<figure class="xp"><p class="xp-t">시스템 프롬프트를 뺐을 때의 토큰 비(MATH500, 같은 문항끼리 견준 값). 세로 선이 1배(변화 없음)입니다</p><div class="xp-bars"><span>표준 SFT (학습 때 시스템 프롬프트를 봄)</span><span class="xp-track"><i class="xp-fill bad" style="width:48.00%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.60배 (0.57–0.64)</span><span>질문 비움 SFT (봄)</span><span class="xp-track"><i class="xp-fill bad" style="width:31.20%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.39배 (0.37–0.42)</span><span>시스템 프롬프트 없이 학습한 SFT (안 봄)</span><span class="xp-track"><i class="xp-fill" style="width:83.20%"></i><i class="xp-line" style="left:80.00%"></i></span><span>1.04배 (1.00–1.07)</span><span>기반 모델 (미세조정 전)</span><span class="xp-track"><i class="xp-fill" style="width:76.00%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.95배 (0.93–0.97)</span></div><p class="xp-cap">같은 문구를 빼는데, 그 문구를 보고 학습한 두 모델만 짧아집니다. 괄호는 95% 구간입니다.</p></figure>
<!-- /xp -->

**무엇을 했나.** MATH500 500문항을 문항당 4회 풀게 했습니다. 추론 조건은 표준 프롬프트와 시스템 프롬프트 제거 두 가지입니다. 결과를 보기 전에 예측 두 가지를 적어 두었습니다. ① 표준 SFT는 프롬프트를 빼면 0.90배 아래로 줄어든다. ② 시스템 프롬프트 없이 학습한 SFT보다 더 많이 줄어든다.

| 모델 | 추론 조건 | 평균 토큰 | 정답률(표준 채점) | 정답률(답 틀 없는 답을 읽어 넣음) |
|---|---|---|---|---|
| 표준 SFT | 표준 프롬프트 | 6,507 | 78.9% | 79.6% |
| 표준 SFT | 시스템 프롬프트 제거 | 4,899 | 76.8% | 80.2% |
| 시스템 프롬프트 없이 학습한 SFT | 표준 프롬프트 | 6,356 | 79.8% | 79.8% |
| 시스템 프롬프트 없이 학습한 SFT | 시스템 프롬프트 제거 | 6,506 | 77.4% | 79.2% |
| 기반 모델 | 표준 프롬프트(저장된 평가 16회) | 635 | 75.4% | 읽지 않음 |
| 기반 모델 | 시스템 프롬프트 제거 | 627 | 76.0% | 읽지 않음 |
| QFFT | 표준 프롬프트(저장된 평가 16회) | 4,630 | 80.3% | 읽지 않음 |

**판정은 "재현"입니다.** 시스템 프롬프트를 뺐을 때 토큰은 표준 SFT가 문항 기준 0.60배 [0.57, 0.64], 전체 0.75배 [0.71, 0.80]이고, 시스템 프롬프트 없이 학습한 SFT는 1.04배 [1.00, 1.07]입니다. 두 예측이 모두 맞았습니다.

### 정답률은 내려가지 않는다

<!-- xp2 -->
<figure class="xp"><p class="xp-t">답 틀이 없어 오답으로 처리된 맞은 답의 예(정답 0, 문제: Determine the remainder of 54 (mod 6).)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="">…  54 is 0. So yeah, the remainder is 0. So modulus 6 of 54 is 0. So I think that's correct. **Final Answer** The remainder of 54 modulo 6 is \boxed{0}.</div></div><div class="xp-name">표준 프롬프트의 답 끝부분. 표준 채점: 정답</div></div><div class="xp-card"><div class="xp-turn"><div class="">… 6: 54 ÷ 6 = 9 Since 6 multiplied by 9 is 54 (6*9=54), there is no remainder. Thus, the remainder is 0. So, 54 ≡ 0 (mod 6). Therefore, the answer is 0.</div></div><div class="xp-name">시스템 프롬프트 제거의 답 끝부분. 표준 채점: 오답(답 틀 없음). 직접 읽기: 맞음</div></div></div><p class="xp-cap">원본 채점은 \boxed{} 안의 답만 봅니다. 시스템 프롬프트를 빼면 답 형식 지시도 함께 빠져서, 맞게 풀고도 틀에 넣지 않은 답이 늘어납니다.</p></figure>
<!-- /xp2 -->

표준 채점에서 보이는 약 2%포인트 하락은 길이가 줄지 않은 모델에도 똑같이 나타납니다. 시스템 프롬프트 안에 답 형식 지시가 함께 들어 있어서, 빼면 맞은 답을 틀에 넣지 않는 경우가 늘기 때문입니다.

- 답 틀이 없는 답 128개를 어느 조건인지 가린 채 읽었습니다. 117개가 맞은 답이었습니다.
- 읽어 넣으면 표준 SFT의 정답률 차는 +0.5%포인트 [−1.3, +2.5]입니다.

### 지시문 문구 자체의 효과가 아니다

표준 시스템 프롬프트에는 "단계별로 추론하라"는 말이 있으니, 빼면 짧아지는 것이 당연하다는 반론이 가능합니다. 그래서 그 프롬프트로 학습하지 않은 두 모델에서 같은 실험을 했습니다.

- 미세조정 전 기반 모델: 0.95배 [0.93, 0.97]. 거의 그대로입니다.
- 시스템 프롬프트 없이 학습한 SFT: 1.04배 [1.00, 1.07]. 그대로입니다.

같은 문구를 빼는데 그 문구를 보고 학습한 표준 SFT는 0.60배로 크게 줄어듭니다. 나중에 잰 QFFT는 보지 않았는데도 0.78배로 줄어, 지시문 자체의 효과도 일부 있습니다(아래 "오늘 아침에 더한 것").

### 추론 지시만 빼면 조금만 짧아진다

<!-- xp4 -->
<figure class="xp"><p class="xp-t">네 가지 추론 조건의 실제 입력과 답의 앞부분(표준 SFT, 같은 문항, 정답 2)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find an integer x that satisfies the ineq …</div></div><div class="xp-name">표준 프롬프트: 1,809토큰</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find an integer x that fits between 1/4 a …</div></div><div class="xp-name">추론 지시만 제거: 1,444토큰. 여전히 Okay로 시작</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?<br><br>Put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find an integer x that satisfies the ineq …</div></div><div class="xp-name">답 형식 지시를 질문 뒤에: 932토큰. 시스템 프롬프트 칸이 없어도 Okay로 시작</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To determine the integer \( x \) that satisfies the inequali …</div></div><div class="xp-name">시스템 프롬프트 제거: 750토큰. To로 시작</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>모델이 읽는 프롬프트</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 쓴 답의 앞부분</span></div><p class="xp-cap">이 문항을 4번씩 푼 평균 토큰은 표준 프롬프트 1,682, 추론 지시만 제거 1,314, 답 형식 지시를 질문 뒤에 940, 시스템 프롬프트 제거 1,013입니다. 한 문항의 값은 문항마다 달라서, 전체 경향은 아래 막대(500문항)로 봅니다. 카드의 답은 4번 가운데 길이가 가운데쯤인 것입니다(시스템 프롬프트 제거는 To로 시작한 답).</p></figure>
<figure class="xp"><p class="xp-t">표준 프롬프트 대비 토큰 비(표준 SFT, MATH500 500문항 × 4회, 같은 문항끼리 견준 값)</p><div class="xp-bars"><span>표준 프롬프트</span><span class="xp-track"><i class="xp-fill bad" style="width:80.00%"></i><i class="xp-line" style="left:80.00%"></i></span><span>기준, 평균 6,507토큰, Okay류로 시작 2,000개 중 2,000</span><span>추론 지시만 제거</span><span class="xp-track"><i class="xp-fill bad" style="width:68.80%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.86배 (0.83–0.90), 5,992토큰, Okay류 1,999</span><span>답 형식 지시를 질문 뒤에</span><span class="xp-track"><i class="xp-fill bad" style="width:64.80%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.81배 (0.78–0.84), 5,870토큰, Okay류 1,997</span><span>시스템 프롬프트 제거</span><span class="xp-track"><i class="xp-fill" style="width:48.00%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.60배 (0.57–0.64), 4,899토큰, Okay류 974</span></div><p class="xp-cap">답 형식 지시 문장이 입력 어디에든 있으면(시스템 프롬프트 칸이든 질문 뒤든) 답은 Okay류로 시작하고 길이도 긴 쪽에 머뭅니다. 그 문장이 어디에도 없을 때만 첫 낱말이 바뀌고 크게 짧아집니다.</p></figure>
<!-- /xp4 -->

시스템 프롬프트에서 "단계별로 추론하라"만 빼고 답 형식 지시는 남기면("Put your final answer within `\boxed{}`.") 어떻게 되는지도 돌렸습니다. 그리고 시스템 프롬프트 칸은 없애고 그 답 형식 지시 한 문장만 질문 뒤에 붙인 조건도 돌렸습니다.

| 추론 조건(표준 SFT) | 평균 토큰 | 표준 프롬프트 대비(문항 기준) | 정답률(표준 채점) | Okay류로 시작한 답 |
|---|---|---|---|---|
| 표준 프롬프트 | 6,507 | 기준 | 78.9% | 2,000개 중 2,000 |
| 추론 지시만 제거 | 5,992 | 0.86배 [0.83, 0.90] | 79.1% | 1,999 |
| 답 형식 지시를 질문 뒤에(시스템 프롬프트 칸 없음) | 5,870 | 0.81배 [0.78, 0.84] | 80.0% | 1,997 |
| 시스템 프롬프트 제거 | 4,899 | 0.60배 [0.57, 0.64] | 76.8%(읽어 넣으면 80.2%) | 974 |

- 추론 지시 문구만 빼면 14%쯤 짧아지는 데 그치고, 첫 낱말은 그대로 "Okay"입니다.
- 긴 풀이로 들어가는 문은 시스템 프롬프트라는 칸이 아니라 지시 문장에 묶여 있습니다. 칸을 없애고 답 형식 지시 한 문장만 질문 뒤에 붙여도 답은 다시 "Okay"로 시작하고 0.81배로 돌아옵니다. 그 문장이 입력 어디에도 없을 때만 첫 낱말이 바뀌고 0.60배가 됩니다.
- 앞선 판에 적은 "시스템 프롬프트 칸이 있다는 것 자체에 묶여 있다"는 해석은 이 결과로 거뒀습니다(11월 12일 아침).
- 표준 SFT에서는 답 형식을 지키게 하려고 이 문장을 다시 넣으면 답이 다시 길어집니다. 질문 비움 SFT는 지시가 없어도 답을 틀에 넣어 이 문제가 없습니다.
- 네 조건의 정답률은 같습니다(79–80%, 시스템 프롬프트 제거는 읽어 넣은 값).

### 다른 학습 형식에서도 같다

시스템 프롬프트를 보고 학습한 두 번째 모델(질문 비움 SFT)에서도 같은 일이 일어났습니다.

| 모델 | 학습 때 시스템 프롬프트 | 뺐을 때 토큰 비(문항 기준) | 정답률 차(표준 채점) |
|---|---|---|---|
| 표준 SFT | 봄 | 0.60배 [0.57, 0.64] | 읽어 넣으면 +0.5%p [−1.3, +2.5] |
| 질문 비움 SFT | 봄 | 0.39배 [0.37, 0.42] | +0.2%p [−1.2, +1.6] |
| 시스템 프롬프트 없이 학습한 SFT | 안 봄 | 1.04배 [1.00, 1.07] | 읽어 넣으면 −0.7%p [−2.2, +0.9] |
| 기반 모델 | 미세조정 없음 | 0.95배 [0.93, 0.97] | +0.6%p [−0.6, +1.8] |

- 질문 비움 SFT는 시스템 프롬프트가 없어도 답을 틀에 넣습니다. 그래서 사람이 읽어 넣지 않은 표준 채점만으로 정답률이 그대로입니다(79.7% 대 79.8%).
- 시스템 프롬프트를 뺀 질문 비움 SFT는 평균 3,778토큰, 79.8%로 QFFT(4,630토큰, 80.3%)보다 전체 토큰이 0.82배 [0.77, 0.86]이고 정답률 차는 −0.4%포인트 [−1.8, +0.9]입니다.
- 질문만 지우고 학습한 이 모델은 표준 프롬프트에서는 표준 SFT만큼 깁니다(6,149토큰). 길이를 가르는 것은 질문을 보고 학습했는지보다, 학습 때 본 시스템 프롬프트가 평가 때 있는지에 가깝습니다.
- QFFT는 0.78배 [0.74, 0.81], 정답률 차 −1.0%p [−2.7, +0.8]입니다(학습 때 시스템 프롬프트를 보지 않음). 질문 비움 첫 토큰 미학습 SFT는 평가 대기입니다.

### 오늘 아침에 더한 것: QFFT도 줄어든다, 시작어 분포, Long 비율과 RAK

이 절은 바꾼 용어로 씁니다(대응은 [이름표](2026-11-12-a-status-names-and-plan.html)).

- **QFFT도 추론 시 시스템 프롬프트를 제거하면 0.78배 [0.74, 0.81]로 줄어듭니다.** 평균 Tokens 4,630 → 4,122, ACC 80.3% → 79.3%(자동 채점, `\boxed{}` 누락 응답 51개)입니다. 보지 않고 학습한 모델도 줄어들므로 "본 모델만 줄어든다"는 앞선 표현은 고쳤습니다. 본 모델에서 가장 크게 줄어듭니다(SFT 0.60배, A1 0.39배).
- **Long 비율과 RAK.** 시스템 프롬프트를 제거하면 세 모델 모두 RAK가 오릅니다.

| 모델 | 기본 프롬프트: Long 비율, RAK | 시스템 프롬프트 제거: Long 비율, RAK |
|---|---|---|
| SFT | 90.8%, 5.75 | 61.0%, 22.62 |
| 질문 제거 SFT (A1) | 86.0%, 7.35 | 29.2%, 49.54 |
| QFFT | 44.1%, 38.98 | 33.4%, 47.75 |
| 시스템 프롬프트 없이 학습한 SFT | 90.1%, 6.08 | 92.2%, 4.45 |

- **시작어 분포 측정.** 프롬프트를 12가지로 바꿔 응답의 앞 8 tokens만 생성했습니다. SFT는 추론 지시문이든 답안 형식 지시문이든, 위치가 어디든, 표현이 달라도 97–100%가 Okay/Alright로 시작합니다. A1은 추론 지시문이 있을 때만 그렇고(92–99%), 답안 형식 지시문만 있으면 3–9%입니다. 빈 시스템 프롬프트로는 SFT 61.9%, A1 0.1%라 시스템 프롬프트라는 위치는 원인이 아닙니다.
- **GSM8K에서도 SFT는 시스템 프롬프트를 제거하면 0.67배 [0.65, 0.68]로 줄어듭니다**(평균 Tokens 2,060 → 1,517). 다만 응답의 92%가 여전히 Okay/Alright로 시작하고 Long 비율 69.6%, RAK 5.10이라 QFFT(831 tokens, RAK 22.30) 수준은 아닙니다. ACC는 91.6%에서 91.0%로 유지됩니다(차 −0.6%p [−1.3, +0.0]). 이 값은 `\boxed{}` 없는 응답도 최종 답을 확인해 채점하고, 평가 자료의 정답 오류 16문항을 원본 GSM8K대로 고친 값입니다(11월 12일 09시). 원본 채점 그대로는 77.5%인데 `\boxed{}` 누락이 13.5%로 늘어난 탓입니다. 같은 채점으로 Base, SFT, A1, A2, QFFT의 GSM8K ACC는 91.4–92.0%로 같습니다.
- **질문 제거 SFT (A1)는 추론 지시문만 제거하고 답안 형식 지시문을 남겨도 Short-CoT를 유지합니다**(11월 12일 09시). 기본 프롬프트 대비 0.47배 [0.44, 0.49], ACC 80.5%, `\boxed{}` 누락 11개, RAK 44.18입니다. 미리 정한 기준 셋을 모두 충족해, 수동 채점 없이 원본 채점만으로 확인된 조건입니다. SFT에서는 같은 조건이 0.86배였습니다.
- 새 조건의 RAK는 문항당 4회 값이고 신뢰구간은 아직 없습니다. 표와 방법은 [학습 프롬프트 빼기](2026-11-12-b-drop-training-prompt.html)의 "추가 결과" 절에 있습니다.

### QFFT와 견주면

| 비교 | 토큰 비(문항 기준) | 토큰 비(전체) |
|---|---|---|
| 표준 SFT, 표준 프롬프트 ÷ QFFT | 1.98배 [1.89, 2.08] | 1.41배 [1.34, 1.48] |
| 표준 SFT, 시스템 프롬프트 제거 ÷ QFFT | 1.20배 [1.14, 1.26] | 1.06배 [1.01, 1.11] |
| 질문 비움 SFT, 시스템 프롬프트 제거 ÷ QFFT | 0.73배 [0.70, 0.76] | 0.82배 [0.77, 0.86] |
| QFFT, 시스템 프롬프트 제거 ÷ QFFT | 0.78배 [0.74, 0.81] | 0.89배 [0.84, 0.94] |

길이 차이의 대부분이 추론 프롬프트 하나로 사라집니다. 효과의 대부분은 첫 낱말을 거칩니다. 프롬프트가 없으면 답의 51%가 "Okay" 대신 "To" 같은 말로 바로 풀이를 시작하고(이 가운데 "To"가 43%포인트) 이 답은 0.41배입니다. 자세한 기록은 [학습 프롬프트 빼기](2026-11-12-b-drop-training-prompt.html)에 있습니다.

## 발견 3. QFFT 한 번보다 "싼 풀이 먼저, 갈리면 긴 추론"이 낫다

기반 모델로 두 번 풀어 답이 같으면 끝내고, 다르면 QFFT로 한 번 푸는 방식이 QFFT 한 번보다 정답률이 높거나 같고 토큰은 적습니다.

### 예시: 쉬운 문항과 어려운 문항

<!-- xp3 -->
<figure class="xp"><p class="xp-t">싼 풀이 먼저, 갈리면 긴 추론: 방식과 실제 문항 두 개(MATH500, 저장된 답)</p><div class="xp-flow"><div class="xp-step"><b>① 기반 모델로 두 번 풉니다</b><br>한 번에 평균 630토큰</div><div class="xp-arrow">→</div><div class="xp-step"><b>② 두 답이 같은가</b><br>같으면 그 답으로 끝냅니다</div><div class="xp-arrow">→</div><div class="xp-step"><b>③ 다르면 QFFT로 한 번</b><br>긴 추론은 여기서만 씁니다</div></div><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="">문제: A regular hexagon can be divided into six equilateral triangles. If the perimeter of one of the triangles is 2 …</div><div class="">기반 모델 1번째 답: 42 (288토큰)</div><div class="">기반 모델 2번째 답: 42 (262토큰)</div></div><div class="xp-name">쉬운 문항: 두 답이 같아 여기서 끝. 합계 550토큰, 정답</div></div><div class="xp-card"><div class="xp-turn"><div class="">문제: The set of points $(x,y,z)$ that satisfy \[2x = 3y = -z\]is a line. The set of points $(x,y,z)$ that satisfy \ …</div><div class="">기반 모델 1번째 답: 97 (1,226토큰)</div><div class="">기반 모델 2번째 답: 90 (770토큰)</div><div class="">QFFT의 답: 90 (757토큰), 정답 90^\circ</div></div><div class="xp-name">어려운 문항: 두 답이 달라 QFFT로 넘김. 합계 2,753토큰, 정답</div></div></div><p class="xp-cap">MATH500에서 QFFT 한 번은 평균 4,626토큰에 80.3%, 이 방식은 평균 4,031토큰에 82.0%입니다(저장된 답을 조합해 계산).</p></figure>
<figure class="xp"><p class="xp-t">방식별 정답률과 평균 토큰(MATH500). 세로 선은 QFFT 한 번의 정답률입니다</p><div class="xp-bars"><span>기반 모델 한 번</span><span class="xp-track"><i class="xp-fill" style="width:75.40%"></i><i class="xp-line" style="left:80.30%"></i></span><span>75.4%, 630토큰</span><span>기반 모델 5번 다수결</span><span class="xp-track"><i class="xp-fill" style="width:79.80%"></i><i class="xp-line" style="left:80.30%"></i></span><span>79.8%, 3,172토큰</span><span>QFFT 한 번</span><span class="xp-track"><i class="xp-fill bad" style="width:80.30%"></i><i class="xp-line" style="left:80.30%"></i></span><span>80.3%, 4,626토큰</span><span>표준 SFT 한 번</span><span class="xp-track"><i class="xp-fill bad" style="width:79.60%"></i><i class="xp-line" style="left:80.30%"></i></span><span>79.6%, 6,585토큰</span><span>싼 풀이 먼저, 갈리면 긴 추론</span><span class="xp-track"><i class="xp-fill" style="width:82.00%"></i><i class="xp-line" style="left:80.30%"></i></span><span>82.0%, 4,031토큰</span><span>(상한) 기반 모델이 틀릴 때만 QFFT</span><span class="xp-track"><i class="xp-fill" style="width:86.10%"></i><i class="xp-line" style="left:80.30%"></i></span><span>86.1%, 3,496토큰</span></div></figure>
<!-- /xp3 -->

**표 읽는 법.** 저장된 표준 평가(문항당 16회)의 답을 조합해 계산한 값입니다. 정답 차와 토큰 비는 QFFT 한 번과 견준 것입니다.

| 벤치마크 | QFFT 한 번 | 싼 풀이 먼저, 갈리면 긴 추론 | 정답 차 [95% 구간] | 토큰 비 |
|---|---|---|---|---|
| GSM8K (1,319문항) | 92.0%, 830토큰 | 94.0%, 802토큰 | +2.0%p [+1.5, +2.6] | 0.97배 |
| MATH500 (500문항) | 80.3%, 4,626토큰 | 82.0%, 4,031토큰 | +1.6%p [+0.6, +2.6] | 0.87배 |
| AIME25 (30문항) | 15.2%, 18,185토큰 | 14.8%, 17,784토큰 | −0.3%p [−4.2, +3.4] | 0.98배 |

- 기반 모델을 다섯 번 풀어 다수결하면 MATH500에서 QFFT 한 번과 정답률이 구간 안에서 같고(−0.6%p [−2.6, +1.4]) 토큰은 0.69배입니다.
- **GSM8K의 값을 바로잡았습니다(11월 12일 08시).** 처음에는 +6.6%포인트로 적었는데, 채점 방식 때문에 부풀려진 값이었습니다. 원본 채점은 `\boxed{}` 안의 답만 봅니다. QFFT는 GSM8K 답의 5.0%를 `\boxed{}` 없이 끝내 그 답이 모두 오답이 됐습니다(그 가운데 96%는 마지막 수가 정답). 그런 답만 "끝부분의 마지막 수가 정답과 같은가"로 따로 채점하면 QFFT 한 번은 90.9%로 기반 모델 한 번과 같고, 이 방식의 이득은 +2.0%포인트 [+1.5, +2.5]입니다. 이 보조 채점은 결과를 본 뒤에 정한 규칙입니다. **09시에 한 번 더 바로잡았습니다.** 평가 자료의 정답 16문항이 원본 GSM8K와 달라(천 단위 쉼표 뒤가 잘린 14문항, 음수 2문항) 모든 값이 약 1.1%포인트 낮게 나오고 있었습니다. 정답을 고치고 `\boxed{}` 없는 응답을 직접 확인해 채점하면 QFFT 한 번 92.0%, 이 방식 94.0%이고, 이득은 그대로 +2.0%포인트 [+1.5, +2.6]입니다. 자세한 내용은 [학습 프롬프트 빼기](2026-11-12-b-drop-training-prompt.html)의 GSM8K 절에 있습니다.
- 어려운 AIME25에서는 거의 모든 문항이 긴 추론으로 넘어가 QFFT 한 번과 같아집니다. 손해는 없습니다.
- 넘길 때를 완벽하게 알면 MATH500에서 86.1%, 토큰 0.76배까지 갑니다. 지금 방식과의 차이 약 4%포인트가 "언제 긴 추론으로 넘길지 정하는 신호"의 여지입니다.

### 새 표본으로 확인했습니다

위 표는 결과를 보면서 고른 방식의 값이라, 따로 확인했습니다. 기반 모델에게 MATH500을 새로 4번씩 풀게 하고, 실행 전에 적어 둔 규칙("QFFT 한 번보다 정답률이 높고 토큰이 적은가, 구간까지")으로 다시 계산했습니다.

| 방식(MATH500, 새 기반 모델 표본) | 정답률 | 평균 토큰 | QFFT 한 번 대비 정답 차 | 토큰 비 | 판정 |
|---|---|---|---|---|---|
| 싼 풀이 먼저, 갈리면 긴 추론 | 82.3% | 4,119 | +2.0%p [+0.9, +3.2] | 0.89배 [0.83, 0.95] | 확인 |
| 한 번 풀고 확신 낮으면 긴 추론 | 78.5% | 2,592 | 아래 설명 | | 미통과 |

- **확인됐습니다.** 문항의 26.6%만 QFFT로 넘어가고, 나머지는 기반 모델 두 번으로 끝납니다.
- **한 번만 풀고 정하는 방식은 통과하지 못했습니다.** 기반 모델이 답을 쓸 때의 확신도(토큰 확률)가 낮으면 넘기는 방식입니다. 같은 비율(26.6%)만큼 넘기게 맞췄을 때 정답률이 두 번 푸는 방식보다 3.7%포인트 낮았습니다 [−4.9, −2.6]. 확신도는 기반 모델의 답이 맞는지를 잘 가리지 못합니다(맞은 답과 틀린 답의 순서를 맞히는 비율 0.67, 0.5가 찍기).
- 두 번 풀어 답이 같은지를 보는 것이 지금까지 가장 좋은 신호입니다.

**주의.** 구성 자체는 이미 알려진 방식이고([2310.03094](https://arxiv.org/abs/2310.03094)), 모델 두 개가 필요합니다. 새로운 것은 QFFT와의 비교 결과와 남은 여지의 크기입니다. 실제로 이어서 돌린 것이 아니라 따로 뽑은 답을 조합한 기대값입니다.

## 발견 4 (미확정). 틀린 지점만 가르치면 난도를 배운다

짧은 풀이가 실제로 틀린 지점에서만 "Wait,"로 긴 풀이를 열도록 가르친 모델(오류 지점 승급 SFT)은 표준 SFT보다 나빴습니다. 틀렸을 때가 아니라 어려운 문제에서 되짚는 것을 배운 것으로 보입니다.

| 지표 | 오류 지점 승급 SFT | 표준 SFT |
|---|---|---|
| 정답률(난도별로 고른 48문항 × 4회) | 43.2% | 55.7% |
| 상한에 걸려 최종 답을 못 낸 답변 | 43개 | 21개 |
| 가려내는 정도 | 0.74 [0.59, 0.89] | 1.14 |

- 정답률 차는 −12.5%포인트 [−20.8, −4.2]입니다.
- 오류가 없는 풀이 뒤에도 되짚는 비율(헛경보)이 자료의 난도를 따라 올라갑니다. 쉬운 GSM8K 풀이에서 6.3%, 어려운 올림피아드 풀이에서 20.1%입니다.
- 원인 가설: 학습 자료에서 "Wait,"가 든 예는 모두 중간 난도 문항이고 없는 예는 모두 쉬운 문항이었습니다. 모델은 풀이의 상태를 보지 않고 문제만 보고도 맞힐 수 있었습니다.
- 주장하려면 통제 실험이 필요합니다. 같은 문제의 같은 위치에서 맞게 가는 상태와 틀린 상태를 짝지은 균형 자료로 한 번 더 학습해 견주는 실험입니다.

자세한 기록은 [승급 자료 기록](2026-11-11-a-state-escalation-data.html)에 있습니다.

## 벤치마크 조건이 같은가

기준 모델과 새 실행은 프롬프트, 생성 설정, 채점이 같고 문항당 횟수만 다릅니다.

| 항목 | 기준(저장된 표준 평가) | 새 실행 |
|---|---|---|
| 대상 | 기반 모델, 표준 SFT, QFFT, 질문 비움 SFT | 표준 SFT, 시스템 프롬프트 없이 학습한 SFT, 기반 모델의 추론 조건 바꾸기 |
| 벤치마크 | GSM8K, MATH500, AIME25 | MATH500 |
| 프롬프트 | 원본 평가 그대로 | 표준 프롬프트는 글자까지 같음(전 문항 확인) |
| 생성 설정 | temperature 0.6, 최대 32,000토큰 | 같음 |
| 문항당 횟수 | 16회 | 4회 |
| 채점 | 원본 채점 함수 | 같은 함수 |

- 채점이 같은지는 저장된 답 7,396개를 다시 채점해 확인했습니다. 모두 저장된 채점과 일치했습니다.
- 새 실행의 코드 경로는 표준 SFT로 확인했습니다. 새 실행과 저장된 표준 평가의 정답률 차는 −0.8%포인트 [−2.1, +0.7], 토큰은 0.99배 [0.96, 1.02]입니다.
- 발견 3은 세 벤치마크 모두 저장된 표준 평가의 답만으로 계산했으므로 조건이 같습니다.

## 참신성: 무엇이 새롭고 무엇이 아닌가

참신성이 있다고 말할 수 있는 것은 발견 쪽이고 그것도 좁습니다. 방법 쪽에서 새로운 설계는 아직 없습니다.

| 항목 | 참신성 | 근거 |
|---|---|---|
| 발견 1. 문턱만 옮긴다 | 좁게 있음 | 재는 방식은 선행에서 빌렸습니다([2610.30882](https://arxiv.org/abs/2610.30882)). 이 방식으로 QFFT와 학습 형식을 비교한 논문은 못 찾았습니다 |
| 발견 2. 학습 프롬프트만 빼면 QFFT 수준 | 좁게 있음 | QFFT를 이렇게 다시 해석한 논문은 못 찾았습니다(QFFT를 인용한 논문 11편 확인). 다만 학습 때의 프롬프트에 행동이 묶인다는 것([2402.18540](https://arxiv.org/abs/2402.18540))과 첫 낱말이 길이를 가른다는 것([2605.17026](https://arxiv.org/abs/2605.17026))은 이미 발표됐습니다 |
| 발견 3. 싼 풀이 먼저 방식이 QFFT 한 번보다 낫다 | 비교 결과만 | 방식의 구성은 이미 있습니다([2310.03094](https://arxiv.org/abs/2310.03094)) |
| 발견 4. 틀린 지점만 가르치면 난도를 배운다 | 좁게 있음, 미확정 | 이렇게 재서 보인 논문은 못 찾았습니다. 균형 자료의 구조 자체는 이미 있습니다([2606.18844](https://arxiv.org/abs/2606.18844)) |
| 풀이 도중 신호로 반성을 켜는 제어 | 없음 | 여러 편이 이미 있고([2601.03093](https://arxiv.org/abs/2601.03093), [2510.06052](https://arxiv.org/abs/2510.06052), [2604.07922](https://arxiv.org/abs/2604.07922)), 탐지는 되는데 회복은 안 된다는 보고가 많습니다([2605.31561](https://arxiv.org/abs/2605.31561), [2608.07528](https://arxiv.org/abs/2608.07528)) |

"못 찾음"은 찾아본 범위 안의 결과이며 최근 한두 달 논문은 빠졌을 수 있습니다.

## 한계

- **학습이 형식마다 한 번입니다.** 같은 형식을 다른 시드로 다시 학습한 확인이 없습니다.
- **새 평가는 MATH500 하나, 문항당 4회입니다.**
- **발견 3은 모델 두 개가 필요합니다.** 실제로 이어서 돌린 것이 아니라 따로 뽑은 답을 조합한 기대값입니다. 새 표본 확인은 MATH500에서만 했습니다.
- **답 틀이 없는 답은 한 사람이 읽었습니다.** 조건은 가렸지만 128개 가운데 12개는 앞서 조건이 보이는 채로 본 적이 있습니다.
- **발견 1의 앞부분은 다른 모델이 쓴 풀이입니다.** 모델 자신의 풀이에서 생긴 오류에 대한 반응은 따로 확인해야 합니다.

## 다음 계획과 필요한 결정

| 할 일 | 무엇을 위해 | 자원 | 필요한 결정 |
|---|---|---|---|
| 첫 낱말만 뽑기(어느 문장과 문구가 긴 방식을 부르는가), 학습 형식별 프롬프트 빼기, GSM8K | 발견 2의 근거 넓히기와 묶인 곳 좁히기 | 평가만, 11월 12일 오전까지 | 없음 |
| 표준 SFT 시드 반복 | 발견 1, 2가 학습 한 번의 우연이 아님을 확인 | 전체 파인튜닝 약 5.9시간과 평가 약 4시간 | 승인 |
| 균형 상태 짝 학습 | 발견 4의 통제 실험 | 자료 만들기, 전체 파인튜닝 약 6.7시간, 평가 | 승인 |
| 넘길 때를 정하는 신호 개선 | 발견 3의 남은 여지 약 4%포인트 | 추가 학습 없음 | 없음. 선행 연구가 많아 겹침 확인을 먼저 함 |

*일지에서의 이름: 표지 문턱의 학습 형식별 분해와 평가 형식 교차(발견 1), 같은 조건 MATH500 평가와 학습 프롬프트 빼기(발견 2), 배분 규칙 훑어보기(발견 3), 승급 모델 평가(발견 4)*
