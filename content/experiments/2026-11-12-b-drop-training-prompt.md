---
title: 학습 프롬프트 빼기, 표준 SFT에서 시스템 프롬프트만 빼면 QFFT 수준이 된다
date: 2026-11-12
project: QFFT
status: 판정 완료, 후속 진행 중
idea: 후보
summary: 표준 SFT 모델은 추론 때 학습에 쓴 시스템 프롬프트만 빼도 답 길이가 문항 기준 0.60배로 줄고 정답률은 그대로다(MATH500, 500문항 × 4회). 그 프롬프트 없이 학습한 모델은 1.04배, 미세조정 전 기반 모델은 0.95배로 거의 변하지 않는다. 미리 정한 판정은 "재현"이다. QFFT와의 길이 차이는 1.98배에서 1.20배로 줄어든다.
published: true
---

## 한 줄 요약

표준 SFT 모델에서 **추론 때 학습에 쓴 시스템 프롬프트만 빼면** 답이 QFFT 수준으로 짧아지고 정답률은 그대로입니다.

- **길이:** 문항 기준 0.60배 [0.57, 0.64], 전체 토큰 0.75배입니다.
- **대조:** 그 프롬프트 없이 학습한 모델은 1.04배, 미세조정 전 기반 모델은 0.95배입니다. 같은 문구를 빼는데 표준 SFT만 줄어듭니다.
- **정답률:** 답 틀이 없는 답을 읽어 넣으면 80.2% 대 79.6%로 내려가지 않습니다.
- **판정:** 실험 전에 정한 두 예측이 모두 맞아 "재현"입니다.

모델과 조건의 이름은 [실험 이름표](2026-11-12-a-status-names-and-plan.html)를 따릅니다.

## 왜 궁금했나

QFFT 논문은 질문을 지우고 학습하면 모델이 쉬운 문제는 짧게, 어려운 문제는 길게 푼다고 보고합니다. 그 이유는 "질문을 보면 곧바로 긴 풀이로 가는 지름길을 배우지 않기 때문"이라고 설명합니다.

우리가 [11월 11일에 잰 결과](2026-11-11-b-later-part-bias-candidates.html)는 이 설명과 조금 달랐습니다.

- 풀이 도중 틀린 단계를 만났을 때 "Wait" 하고 되짚는 정도를 쟀더니, QFFT가 표준 SFT보다 더 잘 가려서 되짚지는 않았습니다. 덜 되짚을 뿐이었습니다.
- 표준 SFT도 평가 때 시스템 프롬프트를 빼면 QFFT와 같은 수준으로 덜 되짚었습니다.

그렇다면 물어볼 것은 이것입니다. **표준 SFT의 긴 풀이는 질문이 아니라 학습 때 본 시스템 프롬프트에 붙어 있는 것 아닌가.** 맞다면 QFFT처럼 다시 학습하지 않고, 추론 때 그 프롬프트만 빼도 답이 짧아져야 합니다. 이것을 표준 벤치마크에서 직접 확인했습니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 예 |
|---|---|---|
| 토큰 | 모델이 글을 읽고 쓰는 최소 단위. 영어 단어 하나나 그 일부 정도 | 표준 SFT는 MATH500 한 문항에 평균 6,507토큰을 씁니다 |
| 미세조정(SFT) | 이미 만들어진 모델에 자료를 더 보여 주어 습관을 바꾸는 학습 | 어려운 수학 문제 817개와 긴 풀이를 보여 줌 |
| 표준 SFT | 질문, 시스템 프롬프트, 풀이를 모두 넣고 학습한 모델 | 예전 글의 "SFT" |
| 기반 모델 | 미세조정 전의 원래 모델 | Qwen2.5-7B-Instruct, 한 문항에 평균 635토큰 |
| 시스템 프롬프트 | 질문 앞에 붙는 지시문. 학습 때도 평가 때도 같은 문장을 씁니다 | "Please reason step by step, and put your final answer within `\boxed{}`." |
| 추론 조건 | 답을 쓰게 할 때 프롬프트를 어떻게 주는가 | 표준 프롬프트, 시스템 프롬프트 제거 |
| 토큰 비 | 두 조건의 답 길이를 나눈 값. 1배면 변화 없음 | 0.60배면 40% 짧아짐 |
| 95% 구간 | 문항을 다시 뽑아도 값이 있을 범위. 대괄호로 적습니다 | 0.60배 [0.57, 0.64] |
| 답 틀 | 최종 답을 넣는 `\boxed{}`. 원본 채점은 이 안의 답만 봅니다 | `\boxed{2}` |
| %p(퍼센트포인트) | 퍼센트끼리의 차이 | 79.6%와 80.2%의 차이는 0.6%p |

## 실험 예시

<!-- xp -->
<figure class="xp"><p class="xp-t">실제 입력과 출력 예(표준 SFT, MATH500의 한 문항, 정답 2). 같은 문항에서 시스템 프롬프트만 뺐습니다</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find an integer x that satisfies the inequality $\f …</div></div><div class="xp-name">표준 프롬프트: 2,630토큰, 정답</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To determine the integer \( x \) that satisfies the inequality \( \fra …</div></div><div class="xp-name">시스템 프롬프트 제거, To로 시작한 답: 750토큰, 정답</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find an integer x that fits between 1/4 and 1/3 whe …</div></div><div class="xp-name">시스템 프롬프트 제거, Okay로 시작한 답: 1,245토큰, 정답</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>모델이 읽는 프롬프트</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 뺀 부분</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 쓴 답의 앞부분</span></div><p class="xp-cap">이 문항의 평균 토큰은 표준 프롬프트 1,682, 시스템 프롬프트 제거 1,013로 0.60배입니다. 시스템 프롬프트를 빼면 같은 문항에서도 답이 "To"로 시작하기도 하고 "Okay"로 시작하기도 합니다.</p></figure>
<figure class="xp"><p class="xp-t">시스템 프롬프트를 뺐을 때의 토큰 비(MATH500, 같은 문항끼리 견준 값). 세로 선이 1배(변화 없음)입니다</p><div class="xp-bars"><span>표준 SFT</span><span class="xp-track"><i class="xp-fill bad" style="width:48.00%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.60배 (0.57–0.64)</span><span>시스템 프롬프트 없이 학습한 SFT</span><span class="xp-track"><i class="xp-fill" style="width:83.20%"></i><i class="xp-line" style="left:80.00%"></i></span><span>1.04배 (1.00–1.07)</span><span>기반 모델(미세조정 전)</span><span class="xp-track"><i class="xp-fill" style="width:76.00%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.95배 (0.93–0.97)</span></div><p class="xp-cap">같은 문구를 빼는데, 그 문구를 보고 학습한 표준 SFT만 짧아집니다. 괄호는 95% 구간입니다.</p></figure>
<figure class="xp"><p class="xp-t">평균 토큰과 정답률(MATH500)</p><div class="xp-bars"><span>표준 SFT, 표준 프롬프트</span><span class="xp-track"><i class="xp-fill bad" style="width:92.96%"></i></span><span>6,507토큰, 79.6%</span><span>표준 SFT, 시스템 프롬프트 제거</span><span class="xp-track"><i class="xp-fill" style="width:69.99%"></i></span><span>4,899토큰, 80.2%</span><span>QFFT, 표준 프롬프트</span><span class="xp-track"><i class="xp-fill" style="width:66.14%"></i></span><span>4,630토큰, 80.3%</span><span>기반 모델, 표준 프롬프트</span><span class="xp-track"><i class="xp-fill" style="width:9.07%"></i></span><span>635토큰, 75.4%</span></div><p class="xp-cap">표준 SFT의 두 줄은 답 틀이 없는 답을 읽어 넣은 정답률이고, QFFT와 기반 모델은 표준 채점 값입니다.</p></figure>
<!-- /xp -->

### 문항 하나로 따라가 보기

<!-- xp1 -->
**어느 문항인가.** MATH500의 342번 문항입니다. 500문항 가운데 토큰 비가 전체 값(0.60배)에 가장 가깝고, 8개 답이 모두 맞은 문항을 규칙으로 골랐습니다. 정답은 2입니다.

**실제 입력: 표준 프롬프트.** 모델이 받는 글 전체입니다.

```
<|im_start|>system
Please reason step by step, and put your final answer within \boxed{}.<|im_end|>
<|im_start|>user
What integer $x$ satisfies $\frac{1}{4}<\frac{x}{7}<\frac{1}{3}$?<|im_end|>
<|im_start|>assistant
```

**실제 입력: 시스템 프롬프트 제거.** 위에서 system 칸 두 줄만 뺐습니다. 질문과 나머지는 글자까지 같습니다.

```
<|im_start|>user
What integer $x$ satisfies $\frac{1}{4}<\frac{x}{7}<\frac{1}{3}$?<|im_end|>
<|im_start|>assistant
```

**조건별로 한 일.** 같은 문항을 조건마다 4번 풀게 했습니다. 모델은 매번 조금씩 다른 답을 씁니다.

| 추론 조건 | 1번째 | 2번째 | 3번째 | 4번째 | 평균 토큰 |
|---|---|---|---|---|---|
| 표준 프롬프트 | 2,630토큰, Okay로 시작, 정답 | 1,164토큰, Okay로 시작, 정답 | 1,809토큰, Okay로 시작, 정답 | 1,124토큰, Okay로 시작, 정답 | 1,682 |
| 시스템 프롬프트 제거 | 750토큰, To로 시작, 정답 | 671토큰, To로 시작, 정답 | 1,245토큰, Okay로 시작, 정답 | 1,385토큰, Okay로 시작, 정답 | 1,013 |

- 이 문항의 토큰 비는 1,013 ÷ 1,682 = 0.60배입니다.
- 표준 프롬프트에서는 4번 모두 "Okay"나 "Alright"로 시작합니다. 시스템 프롬프트를 빼면 같은 문항에서도 "To"로 시작하는 답과 "Okay"로 시작하는 답이 섞여 나옵니다.

**500문항을 합치는 법.**

1. 문항마다 위와 같은 토큰 비를 구합니다.
2. **문항 기준 토큰 비**는 그 비들의 곱셈 평균입니다. 예를 들어 세 문항의 비가 0.5배, 0.6배, 1.0배라면 0.5 × 0.6 × 1.0 = 0.3의 세제곱근인 0.67배입니다. 500문항 전체로는 0.60배입니다.
3. **전체 토큰 비**는 500문항의 토큰을 모두 더해 나눈 값입니다. 4,899 ÷ 6,507 = 0.75배입니다.
4. 두 값이 다른 이유는 어려운 문항 때문입니다. 어려운 문항은 답이 길어 전체 토큰의 큰 몫을 차지하는데, 덜 줄어듭니다. 가장 어려운 수준 5의 134문항은 0.70배입니다.

**실제 출력 일부.** 표준 프롬프트의 1번째 답(2,630토큰) 앞부분입니다.

```
Okay, so I need to find an integer x that satisfies the inequality $\frac{1}{4} < \frac{x}{7} < \frac{1}{3}$. Let me try to figure this out step by step. First, I should probably handle each part of the inequality separately. So, breaking it down, I have two inequalities here: 1. $\frac{1}{4} < \frac{x}{7}$ 2. $\frac{x}{7} < \fr …
```

시스템 프롬프트를 뺐을 때 "To"로 시작한 답(750토큰) 앞부분입니다.

```
To determine the integer \( x \) that satisfies the inequality \( \frac{1}{4} < \frac{x}{7} < \frac{1}{3} \), we need to solve the compound inequality step by step. First, let's break down the inequality into two parts: 1. \( \frac{1}{4} < \frac{x}{7} \) 2. \( \frac{x}{7} < \frac{1}{3} \) We will solve each part separately and t …
```

**채점.** 답에서 마지막 `\boxed{}` 안의 글을 꺼내 정답과 수학적으로 같은지 봅니다. 위 두 답에서 꺼낸 값은 "2"와 "2"이고 정답 2와 같아 둘 다 정답입니다. `\boxed{}`가 없으면 꺼낼 값이 없어 오답이 됩니다.
<!-- /xp1 -->

## 무엇을 했나

| 항목 | 내용 |
|---|---|
| 문항 | MATH500 500문항, 문항당 4회. 첫 낱말은 고정하지 않았습니다 |
| 추론 조건 | 표준 프롬프트(학습과 표준 평가에 쓰는 시스템 프롬프트 그대로), 시스템 프롬프트 제거(질문만 줌) |
| 모델 | 표준 SFT(질문, 시스템 프롬프트, 풀이로 학습), 시스템 프롬프트 없이 학습한 SFT(질문과 풀이로만 학습), 기반 모델(미세조정 전) |
| 생성 설정 | 원본 평가와 같습니다. temperature 0.6, 최대 32,000토큰 |
| 채점 | 원본 평가의 채점 함수 그대로. 저장된 답 7,396개를 다시 채점해 저장된 채점과 모두 일치함을 확인했습니다 |

**미리 정한 예측.** 결과를 보기 전에 두 가지를 적어 두었습니다.

1. 표준 SFT는 시스템 프롬프트를 빼면 토큰이 0.90배 아래로 줄어든다(구간 전체가 1배 아래).
2. 표준 SFT가 시스템 프롬프트 없이 학습한 SFT보다 더 많이 줄어든다.

둘 다 맞으면 "재현", 하나만 맞으면 "부분 재현", 둘 다 틀리면 "재현 안 됨"으로 적기로 했습니다.

**세 모델을 함께 본 이유.** 표준 시스템 프롬프트에는 "단계별로 추론하라"는 말이 들어 있습니다. 그러니 "그 말을 빼면 짧아지는 것은 당연하다"는 반론이 가능합니다. 이 반론이 맞다면 어떤 모델이든 짧아져야 합니다. 학습 때 그 프롬프트를 본 모델만 짧아진다면, 문구의 뜻이 아니라 학습 때 생긴 묶임 때문입니다.

## 결과

**표 읽는 법.** 한 줄이 "모델 + 추론 조건" 하나입니다. 정답률은 두 가지로 적었습니다. 표준 채점은 원본 채점 그대로이고, 오른쪽 칸은 답 틀이 없는 답을 사람이 읽어 맞은 것을 더한 값입니다. 왜 두 가지인지는 아래 절에 있습니다.

| 모델 | 추론 조건 | 평균 토큰 | 정답률(표준 채점) | 정답률(답 틀 없는 답을 읽어 넣음) |
|---|---|---|---|---|
| 표준 SFT | 표준 프롬프트 | 6,507 | 78.9% | 79.6% |
| 표준 SFT | 시스템 프롬프트 제거 | 4,899 | 76.8% | 80.2% |
| 시스템 프롬프트 없이 학습한 SFT | 표준 프롬프트 | 6,356 | 79.8% | 79.8% |
| 시스템 프롬프트 없이 학습한 SFT | 시스템 프롬프트 제거 | 6,506 | 77.4% | 79.2% |
| 기반 모델 | 표준 프롬프트(저장된 평가 16회) | 635 | 75.4% | 읽지 않음 |
| 기반 모델 | 시스템 프롬프트 제거 | 627 | 76.0% | 읽지 않음 |
| QFFT | 표준 프롬프트(저장된 평가 16회) | 4,630 | 80.3% | 읽지 않음 |

**표 읽는 법.** 아래 표는 시스템 프롬프트를 뺐을 때의 변화입니다.

- **토큰 비(문항 기준):** 같은 문항에서 "뺀 조건의 평균 토큰 ÷ 표준 프롬프트의 평균 토큰"을 구하고, 500문항의 값을 곱셈 평균한 것입니다. 0.60배면 보통의 문항에서 답이 40% 짧아졌다는 뜻입니다. 아주 긴 답 몇 개에 끌려가지 않습니다.
- **토큰 비(전체):** 500문항의 토큰을 모두 더해 나눈 값입니다. 실제로 드는 비용의 비율입니다. 긴 답이 많이 반영됩니다.
- **대괄호:** 95% 구간입니다. 문항을 다시 뽑는 계산을 2,000번 해서 얻었습니다. 구간이 1배를 포함하지 않으면 변화가 우연으로 보기 어렵다는 뜻입니다.

| 모델 | 토큰 비(문항 기준) | 토큰 비(전체) | 정답률 차 |
|---|---|---|---|
| 표준 SFT | 0.60배 [0.57, 0.64] | 0.75배 [0.71, 0.80] | 읽어 넣은 값으로 +0.5%p [−1.3, +2.5] |
| 시스템 프롬프트 없이 학습한 SFT | 1.04배 [1.00, 1.07] | 1.02배 [0.98, 1.06] | 읽어 넣은 값으로 −0.7%p [−2.2, +0.9] |
| 기반 모델 | 0.95배 [0.93, 0.97] | 0.99배 [0.91, 1.08] | 표준 채점으로 +0.6%p [−0.6, +1.8] |

**판정.** 예측 1은 표준 SFT 0.60배(구간 상한 0.64)로 맞았습니다. 예측 2도 맞았습니다. 두 모델의 차이는 로그로 −0.54 [−0.61, −0.48]입니다. 따라서 "재현"입니다.

기반 모델의 표준 프롬프트 쪽은 새로 돌리지 않고 저장된 평가를 썼습니다. 새 평가 코드가 저장된 평가와 같은 값을 내는지는 표준 SFT로 확인했습니다(정답률 차 −0.8%p [−2.1, +0.7], 토큰 0.99배).

## 정답률을 두 가지로 적은 이유

<!-- xp2 -->
<figure class="xp"><p class="xp-t">답 틀이 없어 오답으로 처리된 맞은 답의 예(정답 0, 문제: Determine the remainder of 54 (mod 6).)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="">…  54 is 0. So yeah, the remainder is 0. So modulus 6 of 54 is 0. So I think that's correct. **Final Answer** The remainder of 54 modulo 6 is \boxed{0}.</div></div><div class="xp-name">표준 프롬프트의 답 끝부분. 표준 채점: 정답</div></div><div class="xp-card"><div class="xp-turn"><div class="">… 6: 54 ÷ 6 = 9 Since 6 multiplied by 9 is 54 (6*9=54), there is no remainder. Thus, the remainder is 0. So, 54 ≡ 0 (mod 6). Therefore, the answer is 0.</div></div><div class="xp-name">시스템 프롬프트 제거의 답 끝부분. 표준 채점: 오답(답 틀 없음). 직접 읽기: 맞음</div></div></div><p class="xp-cap">원본 채점은 \boxed{} 안의 답만 봅니다. 시스템 프롬프트를 빼면 답 형식 지시도 함께 빠져서, 맞게 풀고도 틀에 넣지 않은 답이 늘어납니다.</p></figure>
<!-- /xp2 -->

표준 시스템 프롬프트는 "Please reason step by step, and put your final answer within `\boxed{}`."입니다. 추론 지시와 답 형식 지시가 한 문장에 함께 있습니다. 그래서 시스템 프롬프트를 빼면 맞은 답을 `\boxed{}`에 넣지 않는 경우가 늘고, 원본 채점은 이것을 오답으로 칩니다.

- **길이가 줄지 않은 모델에서도 똑같이 내려갑니다.** 시스템 프롬프트 없이 학습한 SFT는 길이가 1.04배로 그대로인데, 표준 채점 정답률은 2.5%포인트 내려갔습니다. 짧아져서 틀린 것이 아닙니다.
- **답 틀이 없는 답을 직접 읽었습니다.** 네 조건에서 답 틀이 없는 답은 128개였습니다. 어느 조건의 답인지 가리고 섞은 뒤, 답의 끝부분과 정답만 보고 판정했습니다. 판정 규칙은 읽기 전에 적어 두었습니다(끝부분에서 최종 답으로 밝힌 값이 정답과 수학적으로 같으면 맞음, 답을 밝히지 않았거나 알 수 없으면 틀림).
- **128개 중 117개가 맞은 답이었습니다.** 표준 SFT에서 시스템 프롬프트를 뺀 조건은 73개 중 67개, 표준 프롬프트 조건은 17개 중 14개가 맞았습니다.
- **읽어 넣으면 정답률은 내려가지 않습니다.** 표준 SFT는 80.2% 대 79.6%입니다.

답 형식 지시는 남기고 추론 지시만 빼는 조건도 돌렸습니다. 답 틀 문제는 없어졌지만 길이가 거의 줄지 않았습니다(아래 "추가 결과"). 표준 채점만으로 견주려면 시스템 프롬프트 칸은 없애고 답 형식 지시를 질문 뒤에 붙이는 조건이 필요해, 이어서 돌립니다.

## QFFT와 견주면

| 비교 | 토큰 비(문항 기준) | 토큰 비(전체) |
|---|---|---|
| 표준 SFT, 표준 프롬프트 ÷ QFFT | 1.98배 [1.89, 2.08] | 1.41배 [1.34, 1.48] |
| 표준 SFT, 시스템 프롬프트 제거 ÷ QFFT | 1.20배 [1.14, 1.26] | 1.06배 [1.01, 1.11] |

표준 SFT는 QFFT보다 문항 기준으로 약 2배 깁니다. 시스템 프롬프트 하나를 빼면 1.2배가 됩니다. 길이 차이의 대부분이 추론 프롬프트 하나로 사라지고, 완전히 같아지지는 않습니다.

## 어디를 거쳐 짧아지나

- 표준 프롬프트에서는 답 2,000개가 모두 "Okay"나 "Alright"로 시작합니다. 혼잣말하듯 길게 푸는 방식입니다.
- 시스템 프롬프트를 빼면 51%가 "To" 같은 설명체로 시작합니다. 기반 모델이 원래 쓰던 짧은 방식입니다.
- 설명체로 시작한 답은 0.41배, "Okay"로 시작한 답도 0.84배입니다. 효과의 대부분은 첫 낱말을 거치고, 첫 낱말이 같아도 조금 짧습니다.
- 같은 문항에서도 답마다 첫 낱말이 갈립니다. 500문항 가운데 228문항은 4번 가운데 두 방식이 섞여 나왔습니다.
- 11월 10일의 [첫 낱말 강제 실험](2026-11-09-h-system-instruction-dependence.html)(약 80%가 첫 낱말 경로)과 맞습니다.

## 추가 결과: 추론 지시만 빼면 조금만 짧아진다

<!-- xp3 -->
<figure class="xp"><p class="xp-t">세 가지 추론 조건의 실제 입력과 답의 앞부분(표준 SFT, 같은 문항, 정답 2)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find an integer x that satisfies the ineq …</div></div><div class="xp-name">표준 프롬프트: 2,630토큰</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">Okay, so I need to find an integer x that fits between 1/4 a …</div></div><div class="xp-name">추론 지시만 제거: 860토큰. 여전히 Okay로 시작</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">What integer $x$ satisfies $\frac{1}{4}&lt;\frac{x}{7}&lt;\frac{1}{3}$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">To determine the integer \( x \) that satisfies the inequali …</div></div><div class="xp-name">시스템 프롬프트 제거: 750토큰. To로 시작</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>모델이 읽는 프롬프트</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 쓴 답의 앞부분</span></div></figure>
<figure class="xp"><p class="xp-t">표준 프롬프트 대비 토큰 비(표준 SFT, MATH500 500문항 × 4회, 같은 문항끼리 견준 값)</p><div class="xp-bars"><span>표준 프롬프트</span><span class="xp-track"><i class="xp-fill bad" style="width:80.00%"></i><i class="xp-line" style="left:80.00%"></i></span><span>기준, 평균 6,507토큰, Okay류로 시작 100%</span><span>추론 지시만 제거</span><span class="xp-track"><i class="xp-fill bad" style="width:68.80%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.86배 (0.83–0.90), 5,992토큰, Okay류 100%</span><span>시스템 프롬프트 제거</span><span class="xp-track"><i class="xp-fill" style="width:48.00%"></i><i class="xp-line" style="left:80.00%"></i></span><span>0.60배 (0.57–0.64), 4,899토큰, Okay류 49%</span></div><p class="xp-cap">시스템 프롬프트 칸이 남아 있으면 답 형식 지시만 있어도 답은 Okay류로 시작하고 길이도 거의 그대로입니다. 칸을 통째로 없애야 첫 낱말이 바뀌고 크게 짧아집니다.</p></figure>
<!-- /xp3 -->

시스템 프롬프트에는 두 가지 지시가 한 문장에 들어 있습니다. "단계별로 추론하라"와 "답을 `\boxed{}`에 넣으라"입니다. 어느 쪽이 길이를 정하는지 보려고, 추론 지시만 빼고 답 형식 지시는 남긴 조건을 돌렸습니다. 시스템 프롬프트는 "Put your final answer within `\boxed{}`." 한 문장입니다.

**표 읽는 법.** 세 줄 모두 표준 SFT이고 추론 조건만 다릅니다. "Okay류로 시작"은 답 2,000개 가운데 "Okay"나 "Alright"로 시작한 답의 수입니다.

| 추론 조건 | 평균 토큰 | 표준 프롬프트 대비(문항 기준) | 정답률(표준 채점) | Okay류로 시작 | 답 틀 없는 답 |
|---|---|---|---|---|---|
| 표준 프롬프트 | 6,507 | 기준 | 78.9% | 2,000 | 17 |
| 추론 지시만 제거 | 5,992 | 0.86배 [0.83, 0.90] | 79.1% | 1,999 | 6 |
| 시스템 프롬프트 제거 | 4,899 | 0.60배 [0.57, 0.64] | 76.8%(읽어 넣으면 80.2%) | 974 | 73 |

- **추론 지시만 빼면 14%쯤 짧아지는 데 그칩니다.** 전체 토큰으로는 0.92배입니다. 정답률은 그대로입니다(차 +0.2%포인트 [−1.6, +1.9]).
- **첫 낱말이 바뀌지 않습니다.** 답 형식 지시 한 문장만 있어도 답은 여전히 "Okay"로 시작합니다. 긴 풀이로 들어가는 문은 "단계별로 추론하라"라는 말이 아니라, 시스템 프롬프트 칸이 있다는 것 자체에 묶여 있습니다.
- **크게 짧아지려면 칸을 통째로 없애야 합니다.** 그때 답의 절반이 "To"로 시작하면서 0.60배가 됩니다. 그 조건에서 "Okay"로 시작한 답은 0.84배였는데, 이번의 0.86배와 같은 크기입니다. 즉 추론 지시 문구의 몫이 약 15%, 첫 낱말이 바뀌는 몫이 나머지입니다.
- 미세조정 전 기반 모델에서 같은 문구를 빼면 0.91배였습니다. 문구 자체의 효과는 어느 모델에서나 작습니다.
- 11월 10일에 첫 낱말을 "To"로 고정하고 잰 같은 조건은 0.60배였습니다. 그 값은 첫 낱말을 묶어 둔 값이라 이번 값과 다릅니다.

**아직 남은 것.** 답 형식 지시를 남기면 답 틀 문제는 없어지지만(6개) 길이가 QFFT 수준으로 내려가지 않습니다. 그래서 "짧은 방식의 정답률을 사람이 읽지 않고 표준 채점만으로 확인한다"는 목적은 이 조건으로 이루지 못했습니다. 시스템 프롬프트 칸은 없애고 답 형식 지시만 질문 뒤에 붙이는 조건을 이어서 돌립니다.

## 이 결과로 말할 수 있는 것과 없는 것

**말할 수 있는 것.**

- 표준 SFT의 긴 풀이 습관은 학습 때 본 시스템 프롬프트에 붙어 있습니다. 그 프롬프트를 본 적이 없는 두 모델은 같은 프롬프트를 넣고 빼도 길이가 변하지 않았습니다.
- QFFT가 주는 "짧아짐"의 대부분은 다시 학습하지 않아도, 표준 SFT 모델의 추론 프롬프트를 바꾸는 것으로 얻을 수 있습니다(MATH500 기준).

**말할 수 없는 것.**

- 다른 벤치마크와 다른 학습 자료에서도 같다고는 아직 말할 수 없습니다.
- 시스템 프롬프트를 뺀 표준 SFT가 QFFT만큼 "문제에 맞춰" 길이를 조절하는지는 따로 재야 합니다. 여기서 잰 것은 평균 길이와 정답률입니다.
- 학습을 다른 시드로 다시 했을 때도 같은지는 확인하지 못했습니다.

## 선행 연구와의 자리

- 학습 때의 프롬프트 틀에 행동이 묶인다는 일반 현상은 이미 알려져 있습니다([2402.18540](https://arxiv.org/abs/2402.18540)).
- 증류한 추론 모델에서 "Okay", "Alright"와 "To" 같은 첫 낱말이 긴 풀이와 짧은 풀이를 가른다는 것도 이미 발표됐습니다([2605.17026](https://arxiv.org/abs/2605.17026)).
- 표준 SFT 모델에서 학습 시스템 프롬프트를 빼면 QFFT와 비슷해진다는 보고, 그리고 QFFT를 이렇게 다시 해석한 논문은 찾은 범위에서 없었습니다. QFFT를 인용한 논문 가운데 추론 관련 11편을 확인했습니다. 최근 한두 달 논문은 빠졌을 수 있습니다.

## 한계

- 학습은 모델마다 한 번입니다. 같은 형식을 다른 시드로 다시 학습한 확인이 없습니다.
- 벤치마크는 MATH500 하나, 문항당 4회입니다.
- 답 틀이 없는 답은 한 사람이 읽었습니다. 128개 가운데 12개는 앞서 조건이 보이는 채로 본 적이 있습니다.
- QFFT의 정답률은 답 틀이 없는 답을 읽어 넣지 않은 표준 채점 값입니다.

## 다음

- 답 형식 지시를 질문 뒤에 붙이기(시스템 프롬프트 칸은 없앰). 표준 채점만으로 정답률을 확인합니다.
- 다른 학습 형식의 모델(질문 비움 SFT, QFFT)에서 시스템 프롬프트 제거. 프롬프트를 보고 학습한 모델만 짧아지는지를 다른 모델로 반복합니다.
- GSM8K에서 같은 실험.

*일지에서의 이름: 같은 조건 MATH500 평가(11월 11일), 학습 프롬프트 빼기(11월 12일)*
