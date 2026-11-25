---
title: 학습 형식이 정하는 것은 적응형 추론이 아니라 긴 풀이를 켜는 단서였다, 평범하게 학습한 모델도 문제 글만 주면 QFFT처럼 푼다
date: 2026-11-24
project: QFFT
status: 진행 중
idea: 후보
idea_rank: 5
method_name: CueLadder
method_examples:
  - title: 쉬운 지수 문제를 세 가지 입력으로 주기
    kind: 실제 실험 예시
    problem: 'MATH500 Level 1 문항은 2^8 = 4^x에서 x를 묻습니다. 정답은 4입니다. 원래 모델(Qwen2.5-7B-Instruct)은 이 문항에 평균 222 tokens를 씁니다.'
    comparison: '평범하게 학습한 SFT에 같은 문제를 세 가지로 줍니다. 대화 틀과 시스템 프롬프트가 모두 있는 표준 입력, 대화 틀만 있고 시스템 프롬프트가 없는 입력, 대화 틀도 없이 문제 글만 있는 입력입니다.'
    assessment: 'SFT의 평균 길이는 차례로 886, 850, 225 tokens였습니다. 문제 글만 주면 원래 모델과 같아지고, 첫머리도 "Okay, so I need to solve …"에서 "To solve the equation …"로 바뀝니다. MATH500 100문항, GSM8K 100문항, AIME25 30문항에서 이 입력의 SFT는 QFFT와 같은 길이 배분을 보였습니다(긴 풀이가 남는 비율이 GSM8K 0.08, MATH500 0.49, AIME25 0.87이고 QFFT는 0.16, 0.55, 0.90).'
  - title: 어려운 문제는 어떤 입력이든 길게 푼다
    kind: 실제 실험 예시
    problem: 'MATH500 Level 5 문항은 ω^1997 = 1이고 ω ≠ 1일 때 1/(1+ω) + 1/(1+ω^2) + … + 1/(1+ω^1997)의 값을 묻습니다. 정답은 1997/2입니다. 원래 모델은 평균 794 tokens를 씁니다.'
    comparison: '위와 같은 세 가지 입력을 SFT에 줍니다.'
    assessment: 'SFT의 평균 길이는 16,586, 16,832, 17,842 tokens로 세 입력 모두 길었습니다. 쉬운 문제는 학습 때 본 단서가 있어야 길어지고, 어려운 문제는 단서 없이도 길어집니다.'
summary: 평범하게 학습한 모델에 대화 틀과 시스템 프롬프트 없이 문제 글만 주었더니 길이 배분이 QFFT와 같아졌습니다. 학습 입력이 서로 다른 네 모델이 단서 없는 입력에서 같은 곡선에 모였고 길어지는 문항도 같았습니다. 학습 형식이 긴 풀이를 켜는 단서를 정한다는 읽기로 미리 적은 예측은 네 칸 가운데 두 칸만 맞았습니다(부분 지지). 학습 때 본 적 없는 지시 문장도 QFFT의 긴 풀이를 일부 켰습니다.
published: true
---

**방법 이름: CueLadder.** 입력의 단서(cue)를 한 단씩 빼거나 넣어 가며(ladder) 어느 단에서 긴 풀이가 켜지는지 재는 분석입니다.

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | SFT는 시스템 프롬프트만 빼면 길이가 0.60배가 되지만, 대화 틀이 남아 있으면 쉬운 문제에서도 긴 풀이가 많이 남았습니다(GSM8K 남는 비율 0.77). |
| 든 의문 | 시스템 프롬프트 말고 대화 틀도 단서인가? 단서를 하나씩 빼 가면 어디서 긴 풀이가 꺼지는가? 학습 입력이 다른 모델은 다른 것을 단서로 삼는가? |
| 그때까지 안 해 본 것 | 대화 틀까지 뺀 "문제 글만" 입력은 모델을 평소 쓰는 방식이 아니어서 넣어 본 적이 없었습니다. |
| 그래서 한 것 | 문제 글만, 문제 글 앞에 지시문, 대화 틀, 대화 틀과 시스템 프롬프트의 네 입력을 학습 입력이 서로 다른 모델들에 줬습니다. 칸마다 예측을 미리 적었습니다. |
| 답 | SFT도 문제 글만 주면 QFFT와 같은 모양으로 풀었습니다(남는 비율 0.08, 0.49, 0.87). 학습 입력이 다른 네 모델이 같은 곡선에 모였고 길어지는 문항도 같았습니다(문항 순서의 상관 0.73). 미리 정한 기준으로는 "부분 지지"입니다(판정을 가르는 세 칸 가운데 둘이 예측과 같음). |
| 다음 의문 | 단서를 뺀 입력의 답을 읽으니 "Okay"로 시작하는 답이 0%인데 긴 풀이는 22–36%였습니다. 이 답들은 어디서 길어졌는가? ([두 길](2026-11-24-e-two-routes-to-long-reasoning.html)) 그리고 모델들을 견준 것만으로는 원인이라고 할 수 없습니다. ([원인 실험](2026-11-24-g-causal-cue-swap.html)) |

질문의 사슬 전체와, 모델에 실제로 넣은 입력 문자열과 실제 답은 [연구 질문으로 다시 쓴 QFFT 연구](2026-11-25-a-research-questions.html)에 있습니다.

## 메인 표: Base, SFT, A1, A2, QFFT와 추론 입력을 바꾼 조건

<!-- qfft-main-table-start -->

**표 읽는 법.** 한 줄이 "모델 + 추론 입력" 하나입니다. ACC는 정답률(%), Tokens는 답 하나의 평균 출력 tokens입니다. 굵게 적은 A2와 QFFT가 견줄 기준이고, 그 아래 줄들이 추론 입력만 바꾼 조건입니다. "대기"는 지금 돌고 있는 칸입니다.

| 모델 | 추론 입력 | GSM8K ACC | GSM8K Tokens | MATH500 ACC | MATH500 Tokens | AIME25 ACC | AIME25 Tokens |
|---|---|---|---|---|---|---|---|
| Base | 기본 프롬프트 | 92.0 | 301 | 76.1 | 635 | 8.8 | 1,060 |
| SFT | 기본 프롬프트 | 91.6 | 2,060 | 81.0 | 6,576 | 16.7 | 20,574 |
| A1 | 기본 프롬프트 | 91.4 | 1,856 | 80.9 | 6,149 | 17.5 | 18,965 |
| **A2** | 기본 프롬프트 | **91.6** | **888** | **81.3** | **4,587** | **17.5** | **17,735** |
| **QFFT** | 기본 프롬프트 | **92.0** | **831** | **81.4** | **4,630** | **15.4** | **18,133** |
| SFT | 시스템 프롬프트 제거 | 91.0 | 1,517 | 80.9 | 4,899 | 19.2 | 18,382 |
| SFT | 문제 글만 | 대기 | 대기 | 81.4 | 4,221 | 대기 | 대기 |
| A1 | 시스템 프롬프트 제거 | 91.5 | 587 | 81.6 | 3,778 | 12.5 | 16,270 |
| A2 | 시스템 프롬프트 제거 | 91.6 | 514 | 82.0 | 3,948 | 값 없음 | 값 없음 |
| QFFT | 시스템 프롬프트 제거 | 91.3 | 630 | 82.5 | 4,122 | 값 없음 | 값 없음 |
| QFFT | 문제 글만 | 대기 | 대기 | 77.5 | 5,046 | 대기 | 대기 |

- **모델.** Base는 파인튜닝 전의 Qwen2.5-7B-Instruct입니다. 나머지는 모두 LIMO 817문항으로 학습했습니다. SFT는 질문과 긴 풀이로, A1은 질문을 지우고, A2는 질문을 지우고 응답 첫 토큰의 loss까지 빼고, QFFT는 논문 방법대로 질문 없이 풀이만으로 학습한 모델입니다.
- **추론 입력.** 기본 프롬프트는 대화 틀, 시스템 프롬프트 "Please reason step by step, and put your final answer within \boxed{}.", 질문으로 이루어집니다. 시스템 프롬프트 제거는 거기서 시스템 프롬프트만 뺀 입력이고, 문제 글만은 대화 틀까지 빼고 질문 글자만 준 입력입니다. 실제 문자열은 아래 "실제 입력과 실제 답"에 있습니다.
- **크기.** GSM8K 1,319문항, MATH500 500문항, AIME25 30문항입니다. 기본 프롬프트 줄은 문항마다 16회, 나머지 줄은 4회 풀게 했습니다. 최대 32,000 tokens입니다.
- **채점.** GSM8K와 MATH500의 ACC는 `\boxed{}` 없이 끝난 답을 직접 읽어 반영하고, 표기만 다른 같은 답을 맞게 고친 값입니다(GSM8K는 평가 자료의 정답 16문항도 바로잡았습니다). AIME25는 공식 채점 스크립트 값 그대로입니다.
- **읽기.** MATH500에서 SFT에 문제 글만 준 조건은 ACC 81.4%, 4,221 tokens입니다. A2(81.3%, 4,587)와 QFFT(81.4%, 4,630)와 정답률이 같고 8–9% 짧습니다. 다시 학습하지 않은 SFT 그대로입니다. 다만 A2와 QFFT도 시스템 프롬프트를 빼면 더 짧아집니다(3,948, 4,122 tokens). GSM8K와 AIME25의 "문제 글만" 칸은 아직 돌지 않았습니다.

<!-- qfft-main-table-end -->

## 실제 입력과 실제 답: 같은 문항 하나를 모델과 입력을 바꿔 가며

문항은 MATH500의 Level 1 문제 하나입니다(정답 4). 그림의 칸은 모델에 실제로 넣은 입력이고, 글상자는 저장된 실제 출력입니다.

<!-- xp-q77 -->
<figure class="xp"><p class="xp-t">같은 SFT, 입력에서 학습 때의 단서만 뺍니다 (MATH500 문항 77, 정답 4)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">If $2^8=4^x$, what is the value of $x$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">입력 ① 기본 프롬프트(표준 평가)</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">If $2^8=4^x$, what is the value of $x$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">입력 ② 시스템 프롬프트 제거</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div></div><div class="xp-ctx"><div class="">If $2^8=4^x$, what is the value of $x$?</div></div><div class="xp-del"><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">입력 ③ 문제 글만</div></div></div><div class="xp-note"><b>바꾸는 것</b>추론 입력뿐입니다. ②는 시스템 프롬프트 칸을 뺐고, ③은 대화 표지까지 빼고 문제 글자만 줍니다.<b>그대로 두는 것</b>모델의 가중치(다시 학습하지 않음), 문제, 온도 0.6, top_p 1, 최대 32,000 tokens<b>재는 것</b>같은 문제의 답 길이(tokens)와 정답 여부. ①은 16번, ②와 ③은 4번 풀게 했습니다.</div><div class="xp-cols" style="margin-top:14px"><div><p class="xp-name">SFT, 입력 ①: 16번 모두 정답, 525–2,018 tokens(평균 886)</p><pre class="xp-ex"><span class="xp-hit">Okay</span>, so I need to solve this equation: 2^8 = 4^x. Hmm, let me see. I know that both 2 and 4 are powers of 2. Wait, maybe I can rewrite 4 as 2 squared. Yeah, that makes sense. So 4 is 2^2. Therefore, 4^x would be (2^2)^x. I …
<span class="xp-sp">(가운데 줄임)</span>
… here we are. Just converting between exponents. Powers of 2. Logarithms too. All leading to x=4. 
**Final Answer**
The value of \( x \) is \boxed{4}.</pre></div><div><p class="xp-name">SFT, 입력 ②: 4번 가운데 3번 정답, 665–993 tokens(평균 850)</p><pre class="xp-ex"><span class="xp-hit">Okay</span>, so I need to solve this equation: 2^8 = 4^x. Hmm, let me see. Both sides have exponents, but the bases are different. Wait, 4 is 2 squared, right? So, 4 equals 2 squared. Maybe I can rewrite 4^x as (2^2)^x. That way, both …
<span class="xp-sp">(가운데 줄임)</span>
… equals 2^(2x), exponents must be equal. So, 8 = 2x. Therefore, x = 4. That seems straightforward. I think that's correct.
**Final Answer**
\boxed{4}</pre></div><div><p class="xp-name">SFT, 입력 ③: 4번 모두 정답, 211–308 tokens(평균 239)</p><pre class="xp-ex"> <span class="xp-hit">To solve</span> the equation \(2^8 = 4^x\), we need to express both sides of the equation with the same base. Let's start by expressing 4 as a power of 2. Since \(4 = 2^2\), we can rewrite the equation as:
\[
2^8 = (2^2)^x
\]
Next, we …
<span class="xp-sp">(가운데 줄임)</span>
… other. Therefore:
\[
8 = 2x
\]
Solving for \(x\), we divide both sides by 2:
\[
x = \frac{8}{2} = 4
\]
Thus, the value of \(x\) is \(\boxed{4}\).</pre></div></div><div class="xp-cols" style="margin-top:14px"><div><p class="xp-name">A2, 입력 ①: 16번 모두 정답, 219–483 tokens(평균 298)</p><pre class="xp-ex"><span class="xp-hit">To solve</span> the equation \(2^8 = 4^x\), we need to express both sides of the equation with the same base. Let's start by expressing 4 as a power of 2. Since \(4 = 2^2\), we can rewrite the equation as:
\[
2^8 = (2^2)^x
\]
Next, we …
<span class="xp-sp">(가운데 줄임)</span>
… each other:
\[
8 = 2x
\]
Now, solve for \(x\) by dividing both sides by 2:
\[
x = \frac{8}{2} = 4
\]
Therefore, the value of \(x\) is \(\boxed{4}\).</pre></div><div><p class="xp-name">QFFT, 입력 ①: 16번 모두 정답, 187–355 tokens(평균 269)</p><pre class="xp-ex"><span class="xp-hit">To solve</span> the equation \(2^8 = 4^x\), we need to express both sides with the same base. Let's start by recognizing that 4 can be written as a power of 2. Specifically, \(4 = 2^2\). Therefore, \(4^x\) can be rewritten as …
<span class="xp-sp">(가운데 줄임)</span>
… each other. Therefore, \(8 = 2x\).
Solving for \(x\), we divide both sides by 2:
\[
x = \frac{8}{2} = 4
\]
Thus, the value of \(x\) is \(\boxed{4}\).</pre></div><div><p class="xp-name">Base, 입력 ①: 16번 모두 정답, 176–286 tokens(평균 222)</p><pre class="xp-ex"><span class="xp-hit">To solve</span> the equation \(2^8 = 4^x\), we start by expressing both sides of the equation with the same base. We know that \(4\) can be written as a power of \(2\), specifically \(4 = 2^2\). Therefore, we can rewrite the right-hand …
<span class="xp-sp">(가운데 줄임)</span>
… = 2x.\]
To solve for \(x\), we divide both sides of the equation by \(2\):
\[x = \frac{8}{2} = 4.\]
Thus, the value of \(x\) is \(\boxed{4}\).</pre></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 새로 생성</span></div><p class="xp-cap">글상자는 저장된 실제 출력의 첫 답입니다(가운데는 줄였습니다). 같은 SFT가 입력 ①과 ②에는 "Okay, so I need to …"로 시작해 혼잣말하듯 길게 풀고, 입력 ③에는 A2, QFFT, Base처럼 "To solve the equation …"으로 시작해 짧게 풉니다.</p></figure>
<!-- /xp-q77 -->

**표 읽는 법.** 한 줄이 "모델 + 입력" 하나입니다. 입력 ①, ②, ③은 위 그림의 세 입력입니다. 길이는 그 문항을 여러 번 풀게 한 답의 tokens(가장 짧은 답–가장 긴 답, 평균)이고, 마지막 칸은 실제 답의 첫머리입니다.

| 모델 | 입력 | 길이 (tokens) | 정답 수 | 실제 답의 첫머리 |
|---|---|---|---|---|
| Base | ① | 176–286, 평균 222 | 16/16 | To solve the equation \(2^8 = 4^x\), we start by expressing both sides of the equation with the same base. |
| SFT | ① | 525–2,018, 평균 886 | 16/16 | Okay, so I need to solve this equation: 2^8 = 4^x. Hmm, let me see. I know that both 2 and 4 are powers of 2. Wait, maybe I can rewrite 4 as 2 squared. |
| A2 | ① | 219–483, 평균 298 | 16/16 | To solve the equation \(2^8 = 4^x\), we need to express both sides of the equation with the same base. |
| QFFT | ① | 187–355, 평균 269 | 16/16 | To solve the equation \(2^8 = 4^x\), we need to express both sides with the same base. |
| SFT | ② | 665–993, 평균 850 | 3/4 | Okay, so I need to solve this equation: 2^8 = 4^x. Hmm, let me see. Both sides have exponents, but the bases are different. |
| SFT | ③ | 211–308, 평균 239 | 4/4 | To solve the equation \(2^8 = 4^x\), we need to express both sides of the equation with the same base. Let's start by expressing 4 as a power of 2. |
| A2 | ② | 211–226, 평균 217 | 4/4 | To solve the equation \(2^8 = 4^x\), we need to express both sides of the equation with the same base. |
| QFFT | ③ | 295–518, 평균 373 | 4/4 | To solve the equation \(2^8 = 4^x\), we need to express both sides of the equation with the same base. |

- 같은 SFT가 입력 ①에는 "Okay, so I need to …"로 시작해 혼잣말하듯 길게 풀고, 입력 ③에는 Base, A2, QFFT와 같은 "To solve the equation …"으로 시작해 짧게 풉니다. 가중치는 같고 입력만 다릅니다.
- 이 문항에서는 시스템 프롬프트만 뺀 입력 ②로도 SFT가 여전히 "Okay"로 시작해 길게 풀었습니다(평균 850 tokens). 대화 틀까지 빼야 짧아졌습니다. 500문항 전체로는 입력 ②에서도 평균이 6,576에서 4,899 tokens로 줍니다(위 메인 표).


## 한 줄 요약

- QFFT는 질문 없이 풀이만 학습하면 "쉬운 문제는 짧게, 어려운 문제는 길게" 푼다고 보고한 방법입니다.
- 그런데 질문과 시스템 프롬프트를 모두 보고 평범하게 학습한 SFT도, **대화 틀과 시스템 프롬프트를 빼고 문제 글만 주면** 같은 모양으로 풉니다.
- 학습 입력이 서로 다른 네 모델(SFT, A1, 우리가 재현한 QFFT, 저자가 공개한 QFFT)이 "학습 때 본 단서가 입력에 없는" 경우에 같은 곡선에 모였습니다. 길어지는 문항도 같습니다(문항 순서의 상관 0.73).
- 읽은 뜻: **학습 형식이 정하는 것은 적응형 모양이 아니라, 무엇이 긴 풀이를 켜는 단서가 되는가**입니다. QFFT는 켜는 단서가 입력에 묶이지 않은 모델입니다.
- 이 읽기가 미리 정해 주는 값을 적어 두고 실제로 생성했습니다. 판정을 가르는 세 칸 가운데 둘은 예측과 같았고 하나는 어긋나, 미리 정한 기준으로 **"부분 지지"**입니다(아래 "지금 돌리는 확인"). 어긋난 칸에서, 무엇이 단서가 되는지는 학습 입력에 무엇이 함께 있었는가에 달려 있다는 것을 배웠습니다. 따로 예측을 적은 QFFT 칸도 어긋났습니다. 학습 때 본 적 없는 지시 문장을 글자로 붙이자 QFFT의 긴 풀이가 일부 켜졌습니다(GSM8K 0.16 → 0.63).

<figure class="xp">
<a href="../uploads/qfft/2026-11-24/d1-training-input-and-cue.png"><img src="../uploads/qfft/2026-11-24/d1-training-input-and-cue.png" alt="모델 네 개가 학습할 때 본 입력(system, user, assistant)과 평가 입력별 긴 풀이가 남는 비율. 학습 때 본 단서가 평가 입력에 없는 칸은 0.07–0.29로 낮다" style="display:block;width:100%;height:auto;border-radius:6px"></a>
<figcaption class="xp-cap">그림 1. 개념 그림. 모델마다 학습할 때 본 입력이 다르고, 그 입력이 평가 때 없으면 긴 풀이가 꺼집니다. 값은 GSM8K의 남는 비율입니다. 그림을 누르면 원본 크기로 열립니다.</figcaption>
</figure>

## 왜 궁금했나

- 같은 날 앞 글에서 "QFFT의 적응형 추론은 학습 형식과 평가 형식이 어긋나서 생긴다"는 읽기를 세웠고, QFFT를 학습 때 형식으로 평가해 보니 그 읽기는 틀렸습니다. QFFT는 어떤 형식으로 문제를 줘도 같은 모양으로 풀었습니다.
- 그때 비교용으로 SFT에도 문제 글만 넣어 봤습니다. SFT는 대화 틀과 시스템 프롬프트를 늘 보고 학습한 모델이라, 문제 글만 받으면 학습 때 본 단서가 하나도 없는 셈입니다.
- 이 비교 칸에서 SFT가 QFFT와 같은 값을 냈습니다. 그래서 저장돼 있던 다른 결과까지 같은 문항으로 다시 계산해 한 표에 모았습니다.

## 용어 풀이

| 용어 | 뜻 | 이 글에서의 실제 값 |
|---|---|---|
| 원래 모델 | 파인튜닝하기 전의 Qwen2.5-7B-Instruct | 문제를 짧게 바로 풂 |
| SFT | 질문과 긴 풀이를 그대로 학습한 모델 | 학습 입력에 대화 틀, 시스템 프롬프트, 질문이 모두 있었음 |
| A1 | 학습 때 질문 자리만 비운 모델 | 학습 입력에 대화 틀과 시스템 프롬프트는 있고 사용자 칸은 비어 있었음 |
| 시스템 프롬프트 없이 학습한 SFT | SFT와 같지만 학습 입력에 시스템 프롬프트가 없던 모델 | 학습 입력에 대화 틀과 질문이 있었음 |
| QFFT | 질문 없이 풀이만 학습하는 논문 방법 | 학습 입력에 대화 틀, 시스템 프롬프트, 질문이 모두 없었음. 우리가 재현한 모델과 저자가 공개한 모델 |
| 대화 틀 | 누가 말하는지 알리는 표지 | 아래 예시 입력 1에서 `user`, `assistant` 줄에 붙는 `im_start`, `im_end` 표지 |
| 시스템 프롬프트 | 대화 맨 앞에 넣는 지시 | "Please reason step by step, and put your final answer within \boxed{}." |
| 맨 글 입력 | 표지와 시스템 프롬프트 없이 문제 글만 넣는 입력 | 아래 예시의 셋째 입력 |
| 단서 | 그 모델이 학습 때 늘 보던 입력 요소 | SFT에게는 대화 틀, 시스템 프롬프트, 질문이 든 사용자 칸 |
| 남는 비율 | 파인튜닝으로 늘어난 길이 가운데 그 조건에서 남아 있는 몫 | 0이면 원래 모델과 같고, 1이면 SFT가 표준 입력으로 풀 때와 같음 |
| 긴 풀이 비율 | 답이 긴 추론 문체(되묻기, 다시 확인하기 등)로 쓰인 비율 | QFFT 논문의 낱말 기준으로 판별 |
| tokens | 모델이 글을 나눠 세는 단위 | 영어 낱말 하나가 대략 1–2 tokens |
| ACC | 정답률 | 공식 채점 기준 |

## 실험 예시

### 같은 문제를 세 가지 입력으로

<figure class="xp">
<a href="../uploads/qfft/2026-11-24/d2-same-question-three-inputs.png"><img src="../uploads/qfft/2026-11-24/d2-same-question-three-inputs.png" alt="같은 SFT 모델에 2^8 = 4^x 문제를 표준 입력, 시스템 프롬프트 없는 입력, 문제 글만 있는 입력으로 준 결과. 평균 886, 850, 225 tokens" style="display:block;width:100%;height:auto;border-radius:6px"></a>
<figcaption class="xp-cap">그림 2. 예시 그림. 같은 모델과 같은 문제에서 입력만 바꿨습니다. 붉은 칸은 Okay로 시작하는 긴 풀이, 푸른 칸은 To로 시작하는 짧은 풀이입니다. 그림을 누르면 원본 크기로 열립니다.</figcaption>
</figure>

MATH500 Level 1 문항입니다.

> If $2^8=4^x$, what is the value of $x$? (정답 4)

모델에 넣는 입력을 세 가지로 만들었습니다.

```
입력 1 (표준: 대화 틀 + 시스템 프롬프트)
<|im_start|>system
Please reason step by step, and put your final answer within \boxed{}.<|im_end|>
<|im_start|>user
If $2^8=4^x$, what is the value of $x$?<|im_end|>
<|im_start|>assistant

입력 2 (대화 틀, 시스템 프롬프트 없음)
<|im_start|>user
If $2^8=4^x$, what is the value of $x$?<|im_end|>
<|im_start|>assistant

입력 3 (맨 글)
If $2^8=4^x$, what is the value of $x$?
```

이 문항의 평균 답 길이입니다.

| 모델 | 입력 1 | 입력 2 | 입력 3 |
|---|---|---|---|
| 원래 모델 | 222 tokens | | |
| SFT | 886 | 850 | 225 |
| A1 | | 222 | |
| QFFT | 269 | | 320 |

- SFT는 입력 1에서 원래 모델의 4배로 길게 풉니다. 시스템 프롬프트만 빼도(입력 2) 850 tokens로 여전히 깁니다. 대화 틀까지 빼면(입력 3) 225 tokens로 원래 모델과 같아집니다.
- A1은 시스템 프롬프트만 빼도 222 tokens입니다. A1은 학습 때 사용자 칸이 늘 비어 있었으므로, 질문이 든 사용자 칸은 A1이 학습 때 본 단서가 아닙니다.
- 남는 비율로 쓰면, SFT의 입력 3은 log(225 ÷ 222) ÷ log(886 ÷ 222) = 0.01이고 입력 2는 0.97입니다.

실제 답의 첫머리도 달라집니다.

- SFT, 입력 1: "Okay, so I need to solve this equation: 2^8 = 4^x. Hmm, let me see. I know that both 2 and 4 are powers of 2. Wait, maybe I can rewrite 4 as 2 squared. …"
- SFT, 입력 3: "To solve the equation \(2^8 = 4^x\), we can express both sides of the equation with the same base. Let's start by expressing 4 as a power of 2. …"

### 어려운 문제에서는

MATH500 Level 5 문항입니다.

> If $\omega^{1997} = 1$ and $\omega \neq 1,$ then evaluate $\frac{1}{1 + \omega} + \frac{1}{1 + \omega^2} + \dots + \frac{1}{1 + \omega^{1997}}$. (정답 1997/2)

| 모델 | 입력 1 | 입력 2 | 입력 3 |
|---|---|---|---|
| 원래 모델 | 794 tokens | | |
| SFT | 16,586 | 16,832 | 17,842 |
| A1 | | 7,276 | |
| QFFT | 17,865 | | 14,873 |

- 어려운 문제에서는 어떤 입력이든 길게 풉니다. SFT는 문제 글만 받아도 17,842 tokens를 씁니다.
- 쉬운 문제에서는 단서가 있어야 길어지고, 어려운 문제에서는 단서가 없어도 길어집니다. 이것이 아래 표의 모양입니다.

## 무엇을 했나

1. 평가 입력을 세 가지로 나눴습니다. 표준 입력, 시스템 프롬프트를 뺀 입력, 맨 글 입력.
2. 문항은 MATH500 100문항, GSM8K 100문항, AIME25 30문항입니다. 맨 글 입력은 새로 생성했고(문항당 1–2회), 대화 틀 입력은 저장돼 있던 결과(문항당 4회 또는 16회)에서 같은 문항만 골라 다시 계산했습니다.
3. 칸마다 남는 비율을 냈습니다. 생성 설정은 모두 같습니다(temperature 0.6, 최대 32,000 tokens).
4. 맨 글 입력에서 답이 풀이가 아닌 글로 새지 않는지 직접 확인했습니다. 문제를 이어 쓰는 답은 1% 이하였습니다. 다만 GSM8K에서는 파인튜닝한 세 모델이 16–19%를 파이썬 코드 풀이로 답했습니다(원래 모델 2%). 이 답에는 답 상자가 없어 GSM8K의 ACC는 견주지 않았습니다.

## 결과

### 1. 단서 사다리

| 모델 (학습 입력에 있던 것) | 평가 입력 | GSM8K | MATH500 | AIME25 |
|---|---|---|---|---|
| SFT (대화 틀, 시스템 프롬프트, 질문) | 표준 | 1.00 | 0.98 | 1.00 |
| SFT | 시스템 프롬프트 없음 | 0.77 | 0.72 | 0.93 |
| SFT | 맨 글 | **0.08** | **0.49** | **0.87** |
| SFT | 맨 글 앞에 시스템 프롬프트 문장을 글자로 붙임 (같은 날 추가) | 0.97 | 0.97 | 0.95 |
| SFT | 대화 틀, 문장을 사용자 칸 앞에 넣음 (같은 날 추가) | 0.91 | 0.97 | 0.97 |
| A1 (대화 틀, 시스템 프롬프트, 빈 사용자 칸) | 표준 | 0.93 | 0.94 | 0.97 |
| A1 | 시스템 프롬프트 없음 | **0.12** | **0.43** | **0.90** |
| A1 | 맨 글 앞에 시스템 프롬프트 문장을 글자로 붙임 (같은 날 추가) | 0.74 | 0.79 | 0.93 |
| 시스템 프롬프트 없이 학습한 SFT (대화 틀, 질문) | 표준 | 아직 없음 | 0.96 | 아직 없음 |
| 시스템 프롬프트 없이 학습한 SFT | 시스템 프롬프트 없음 | 아직 없음 | 0.96 | 아직 없음 |
| QFFT (풀이 글만) | 표준 | 0.29 | 0.61 | 0.93 |
| QFFT | 시스템 프롬프트 없음 | **0.13** | **0.46** | 아직 없음 |
| QFFT | 맨 글 | **0.16** | **0.55** | **0.90** |
| QFFT | 맨 글 앞에 시스템 프롬프트 문장을 글자로 붙임 (같은 날 추가) | 0.63 | 0.81 | 0.96 |
| QFFT (저자 공개) | 맨 글 | **0.14** | **0.62** | **0.86** |
| 원래 모델 | 맨 글 | −0.07 | −0.02 | −0.01 |

**표 읽는 법.** 값은 남는 비율입니다. 1에 가까우면 SFT가 표준 입력으로 풀 때만큼 길고, 0에 가까우면 원래 모델만큼 짧습니다. 굵은 칸은 그 모델이 학습 때 본 단서가 평가 입력에 하나도 없는 칸입니다.

**횟수를 맞춘 값(11월 24일 13시 추가).** 새로 만든 칸(맨 글, 글자로 붙임, 사용자 칸)은 문항당 1–2회이고 저장돼 있던 칸은 4–16회입니다. 횟수가 적으면 남는 비율이 조금 낮게 읽힙니다. 저장된 칸을 같은 횟수로 줄여 다시 계산하면 GSM8K에서 0.05–0.07, MATH500에서 0.02–0.05 낮아집니다(SFT 시스템 프롬프트 없음 0.77 → 0.71과 0.72 → 0.69, A1 시스템 프롬프트 없음 0.12 → 0.07과 0.43 → 0.40, QFFT 표준 0.29 → 0.22와 0.61 → 0.56). 맞춘 뒤에도 굵은 칸은 GSM8K 0.07–0.16, MATH500 0.37–0.55에 모이고, 아래 예측 칸의 표시도 바뀌지 않습니다.

- 굵은 칸이 모두 같은 곡선에 있습니다. GSM8K 0.08–0.16, MATH500 0.43–0.62, AIME25 0.86–0.90입니다. 쉬운 문제에서는 거의 원래 모델 길이이고 어려운 문제에서는 거의 SFT 길이입니다.
- 학습 때 본 단서가 입력에 모두 있는 칸은 난도와 무관하게 0.93–1.00입니다.
- 단서가 일부만 있는 칸(SFT에서 시스템 프롬프트만 뺀 입력)은 그 사이입니다(0.77, 0.72, 0.93).
- 원래 모델은 맨 글 입력에서도 길이가 그대로입니다. 남는 비율의 기준이 입력 형식 때문에 흔들리지 않습니다.

### 2. 길어지는 문항도 같은가

평균만 같고 문항은 다를 수 있습니다. MATH500 100문항에서 문항마다 "원래 모델보다 몇 배 길어졌는지"를 내고, 칸끼리 문항 순서가 얼마나 같은지(Spearman 상관)를 봤습니다.

| 비교 | 상관 |
|---|---|
| 단서 없는 칸끼리, 모델이 다름 (9쌍) | 평균 0.73 (0.63–0.85) |
| 같은 모델(QFFT)의 다른 입력끼리 (3쌍) | 평균 0.76 |
| 단서 없는 칸과 단서 있는 칸 (20쌍) | 평균 0.59 |

**표 읽는 법.** 상관이 1이면 두 칸에서 길어지는 문항의 순서가 똑같다는 뜻입니다. 둘째 줄은 "같은 모델에 입력만 바꿔도 이 정도는 흔들린다"는 견줄 값입니다.

- 모델이 달라도(SFT, A1, QFFT, 저자 QFFT) 단서 없는 입력에서 길어지는 문항이 같습니다. 그 일치(0.73)는 한 모델 안에서 입력만 바꿨을 때(0.76)와 같은 크기입니다.
- 미리 정한 기준(평균 0.50 이상이고 견줄 값 − 0.15 이상이면 "문항 단위로도 같은 곡선")으로 "문항 단위로도 같은 곡선"입니다.

### 3. 정답률은 지키는가

저장된 전체 크기 결과(MATH500 500문항)로 QFFT 표준 평가와 견줬습니다.

| 칸 | ACC | QFFT 표준 평가와의 차 | 평균 tokens | 길이 (SFT 표준 대비) |
|---|---|---|---|---|
| QFFT, 표준 입력 | 80.1% | 기준 | 4,630 | 0.50 |
| A1, 시스템 프롬프트 없음 | 79.8% | −0.4 [−1.8, +1.0]%p | 3,778 | 0.37 |
| QFFT, 시스템 프롬프트 없음 | 79.3% | −0.8 [−2.5, +0.9]%p | 4,122 | 0.39 |
| SFT, 시스템 프롬프트 없음 | 76.8% | −3.3 [−5.1, −1.5]%p | 4,899 | 0.60 |
| SFT, 표준 입력 | 78.8% | −1.2 [−2.8, +0.4]%p | 6,507 | 1.00 |

**표 읽는 법.** 대괄호는 95% 신뢰구간입니다(문항을 다시 뽑는 방식 2,000회). 미리 정한 기준은 "구간의 아래 끝이 −2%p 이상이면 QFFT에 못지않음"입니다.

- **시스템 프롬프트를 뺀 A1은 QFFT 표준 평가와 정답률이 같고(판정 "QFFT에 못지않음") 길이는 QFFT의 0.74배입니다.** QFFT로 학습해야 얻는다던 길이 배분이, A1에서는 평가 때 시스템 프롬프트를 빼는 것만으로 나옵니다.
- 이 표의 A1과 QFFT 값 자체는 [11월 12일 글](2026-11-12-b-drop-training-prompt.html)에서 이미 보고한 것입니다. 오늘 더한 것은 문항 짝 구간과 미리 정한 기준의 판정, 그리고 이 값을 단서 사다리 안에서 읽는 것입니다.
- 시스템 프롬프트를 뺀 QFFT와 SFT는 "판정 불가"입니다(각각 약 975문항, 1,039문항이 있어야 가를 수 있음). SFT 쪽은 구간이 0을 포함하지 않아 낮은 쪽으로 기웁니다. SFT는 이 입력에서 단서가 일부 남아 길이도 0.60으로 덜 줄었습니다.
- GSM8K는 공식 채점으로는 견줄 수 없습니다. 시스템 프롬프트를 빼면 "답을 상자에 넣으라"는 지시도 함께 사라져 상자 없는 답이 늘고, 공식 채점이 그 답을 오답으로 셉니다(QFFT도 86.1% → 55.2%). 그래서 11월 12일에 해 둔 바로잡은 채점(정답표 16문항 수정, 상자 없는 답은 마지막 숫자와 직접 확인으로 채점, 1,319문항)으로 봤습니다. 시스템 프롬프트를 뺀 A1 91.5%, SFT 91.0%, QFFT 91.3%, QFFT 표준 92.0%로 모두 1%p 안입니다. 다만 GSM8K는 원래 모델도 92.0%라 정답률로 가를 것이 없는 벤치마크입니다.
- ACC는 저장 결과에 든 공식 채점 값입니다. 칸끼리의 차는 같은 채점기라 견줄 수 있지만, 정답표를 바로잡은 다른 글의 ACC와 직접 견주지는 않습니다.

## 그래서 무슨 뜻인가

- QFFT의 "적응형 추론"은 QFFT 학습이 만든 것이 아닐 수 있습니다. 같은 자료로 학습한 모델이면 학습 형식과 무관하게 **단서가 없을 때** 같은 길이 배분을 합니다.
- 학습 형식이 바꾸는 것은 **무엇이 긴 풀이를 켜는가**입니다.
  - SFT: 대화 틀, 시스템 프롬프트, 질문이 든 사용자 칸이 단서입니다. 다 있으면 쉬운 문제도 길게 풉니다.
  - A1: 시스템 프롬프트가 단서입니다. 그것만 빼면 바닥 곡선으로 내려갑니다.
  - QFFT: 입력 없이 풀이만 학습해서 학습 때 묶인 단서가 없습니다. 표준 입력, 시스템 프롬프트 없는 입력, 맨 글 입력에서 모두 바닥 곡선입니다. 다만 같은 날 추가한 칸에서, 지시 문장을 문제 글 앞에 글자로 붙이면 0.63, 0.81로 올라갔습니다(아래 예측 칸).
- 실용적으로는, 이미 학습해 둔 모델이 어떤 단서에 묶였는지 알면 **다시 학습하지 않고 입력만 바꿔** 같은 길이 배분을 얻을 수 있다는 뜻입니다. 다만 정답률까지 확인된 것은 A1의 MATH500뿐입니다.
- 단서가 없을 때의 긴 풀이는 첫 낱말부터가 아니라 풀다가 시작됩니다. 그 모양과, 그것이 풀기 전에 예고된다는 결과는 [다음 글](2026-11-24-e-two-routes-to-long-reasoning.html)에 정리했습니다.
- 이 읽기는 앞 글에서 버린 읽기("학습 형식과 평가 형식의 어긋남")와 다릅니다. 버린 읽기는 QFFT를 학습 형식으로 평가하면 늘 길어진다고 예측했고 틀렸습니다. 지금 읽기는 QFFT에 학습 때 묶인 단서가 없다고 봅니다(지시의 뜻에는 반응한다는 것을 같은 날 추가한 칸에서 확인했습니다).

## 지금 돌리는 확인: 예측을 먼저 적은 9칸

읽기가 맞다면 아직 만들지 않은 칸의 값이 정해집니다. 결과를 보기 전에 아래 표를 연구 기록에 적었습니다.

| 모델 | 평가 입력 | 그 모델이 학습 때 본 단서 가운데 입력에 있는 것 | 예측 |
|---|---|---|---|
| A1 | 맨 글 | 없음 | 바닥 곡선 → **맞음** (GSM8K 0.07, MATH500 0.37, AIME25 0.88) |
| 시스템 프롬프트 없이 학습한 SFT | 맨 글 | 없음 (질문 글은 있으나 대화 틀이 없음) | 바닥 곡선 → **어긋남** (GSM8K 0.18, MATH500 0.73, AIME25 0.97, 표시 "중간") |
| 시스템 프롬프트 없이 학습한 SFT | 시스템 프롬프트 없음 (GSM8K, AIME25 포함) | 모두 | 늘 긺 → **맞음** (GSM8K 0.88, MATH500 0.99, AIME25 0.96) |
| QFFT | 맨 글 앞에 시스템 프롬프트 문장을 글자로 붙임 | 학습 때 본 단서 자체가 없음 | 바닥 곡선 → **어긋남** (GSM8K 0.63, MATH500 0.81, AIME25 0.96, 표시 "중간") |
| S1.1 자료로 학습한 SFT | 맨 글 | 없음 | 바닥 곡선 → **맞음** (GSM8K 0.09, MATH500 0.40, AIME25 0.83) |

- "바닥 곡선"은 GSM8K 0.30 이하이고 MATH500 0.70 이하, "늘 긺"은 둘 다 0.85 이상으로 정했습니다. 경계는 위 표에서 이미 본 값으로 잡았고, 새 칸에만 적용합니다.
- 위 세 칸이 모두 맞으면 읽기를 유지하고, 하나라도 반대쪽 끝이면 읽기를 고칩니다.
- 04:42 기준 첫 칸(A1, 맨 글)이 끝났고 예측과 같습니다.
- 05:36 기준 둘째 칸(시스템 프롬프트 없이 학습한 SFT, 맨 글)은 **예측과 달랐습니다.** GSM8K는 바닥(0.18)이지만 MATH500이 0.73으로 바닥 띠(0.70 이하)를 넘었습니다. 반대쪽 끝("늘 긺")은 아니어서 칸 표시는 "중간"입니다. 이 칸 때문에 종합 판정은 잘해야 "부분 지지"입니다.
- 왜 어긋났는지 답을 직접 나눠 봤습니다(결과를 본 뒤의 탐색). 이 모델은 문제 글만 받아도 MATH500의 52.5%, AIME25의 75.0%를 "Okay,"로 시작합니다(GSM8K는 3.0%). SFT, A1, QFFT는 같은 입력에서 0%입니다. "Okay,"로 시작하지 않은 답만 보면 긴 풀이 비율이 21.1%로 다른 모델(22–30%)과 같습니다.
- 읽은 뜻: 이 모델은 학습 입력에 시스템 프롬프트가 없어서, 긴 풀이와 늘 함께 있던 문제 글의 내용 자체가 단서로 묶인 것으로 보입니다. 학습 자료와 닮은 대회 수학 문제에서는 켜지고 생활 문장제에서는 켜지지 않습니다. "문제 글만 주면 단서가 없다"는 전제가 이 모델에서는 틀렸습니다. 사후 설명이라 판정은 바꾸지 않습니다.
- 07:05 기준 셋째 칸(같은 모델에 대화 틀만 줌)은 예측과 같습니다. GSM8K에서도 0.88로 늘 길게 풀고, 답의 99%가 "Okay,"로 시작합니다.
- **종합 판정은 미리 정한 기준대로 "부분 지지"입니다.** 세 칸 가운데 둘은 예측과 같고 하나는 "중간"입니다.
- 지금의 정리: 그 모델이 학습 때 본 단서가 입력에 있으면 첫 낱말부터 긴 풀이가 켜집니다. 이 부분은 그대로입니다. 고쳐야 하는 부분은 "문제 글만 주면 어느 모델에게나 단서가 없다"입니다. 학습 입력에 시스템 프롬프트가 없던 모델에서는 문제 글의 내용이 단서였습니다. 무엇이 단서가 되는지를 학습 입력의 구성만 보고 미리 맞히는 규칙은 아직 없습니다.
- 예측 없이 기록만 하는 칸도 넷 있습니다. 시스템 프롬프트 문장을 사용자 칸에 넣은 입력, 맨 글 앞에 글자로 붙인 입력입니다. 문장이 시스템 프롬프트 칸이라는 자리에 있어야 켜지는지, 글자만으로 켜지는지를 봅니다.
- 그 가운데 첫 칸이 끝났습니다. SFT에 대화 틀 없이 "Please reason step by step, and put your final answer within \boxed{}."를 문제 글 앞에 글자로만 붙였더니 남는 비율이 0.97(GSM8K), 0.97(MATH500), 0.95(AIME25)로 늘 길게 풉니다. 문제 글만 줄 때의 0.08, 0.49, 0.87과 대조됩니다. SFT에게 충분한 단서는 문장 자체이고, 시스템 프롬프트 칸이라는 자리는 필요하지 않습니다. 이때 답은 "Okay,"가 아니라 "To determine…, I need to…"나 "Let me…" 같은 1인칭 혼잣말로 시작합니다(첫머리가 1인칭인 답 81–85%).
- 둘째 칸도 끝났습니다. 대화 틀에서 시스템 프롬프트 칸을 없애고 같은 문장을 사용자 칸 앞에 넣으면 0.91, 0.97, 0.97로 늘 길게 풉니다. SFT는 문장이 있으면 그 자리가 시스템 프롬프트 칸이든, 사용자 칸이든, 대화 표지 없는 맨 글이든 긴 풀이로 들어갑니다. 문장이 없으면 대화 틀이 있을 때 중간(0.77, 0.72), 없을 때 바닥(0.08, 0.49)입니다.
- 11:57 기준 QFFT 칸이 끝났고 **예측과 달랐습니다.** QFFT는 학습 때 이 문장을 본 적이 없는데도, 문제 글 앞에 글자로 붙이자 남는 비율이 0.16, 0.55, 0.90에서 0.63 [0.54, 0.72], 0.81 [0.73, 0.90], 0.96으로 올랐습니다. GSM8K의 긴 풀이 비율은 20%에서 57%가 됐습니다. 같은 문장을 대화 틀의 시스템 프롬프트 칸에 넣은 표준 입력(0.29, 0.61)보다도 높습니다. 판정을 가르는 세 칸에는 들지 않아 종합 판정 "부분 지지"는 그대로이지만, 예측을 적은 네 칸 가운데 두 칸이 어긋났습니다.
- A1에 같은 입력을 주면 0.74 [0.66, 0.82], 0.79 [0.73, 0.86], 0.93입니다(예측 없이 기록만 한 칸). 문장을 글자로 붙였을 때 켜지는 정도는 GSM8K 기준으로 SFT 0.97, A1 0.74, QFFT 0.63 순서입니다.
- 읽은 뜻(결과를 본 뒤의 정리): 이 문장은 학습 때 본 단서로만 작용하는 것이 아닙니다. 단계별로 풀라는 뜻이, 그 문장으로 학습한 적 없는 모델의 긴 풀이도 일부 켭니다. 원래 모델은 이 문장이 있는 표준 입력과 문장이 없는 맨 글 입력에서 길이가 거의 같으므로(남는 비율 −0.07, −0.02, −0.01), 긴 풀이를 배운 모델에서만 나오는 반응입니다. 그래서 위의 "QFFT에는 켜는 단서가 아예 없다"는 정리는 고칩니다. QFFT는 학습 때 묶인 단서가 없을 뿐이고, 지시의 뜻에는 반응합니다.

- 14:46 기준 마지막 두 칸이 끝나 9칸이 모두 나왔습니다. S1.1 자료(다른 학습 자료)로 학습한 SFT에 문제 글만 주면 남는 비율이 0.09 [−0.03, 0.21], 0.40 [0.30, 0.50], 0.83 [0.73, 0.91]로 **예측대로 바닥 곡선**입니다. 긴 풀이 비율은 GSM8K 7%, MATH500 16%, AIME25 83%입니다.
- 예측을 적은 다섯 칸의 결과는 맞음 셋, 어긋남 둘입니다. 종합 판정 "부분 지지"는 그대로입니다.
- 시스템 프롬프트 없이 학습한 SFT에 학습 문장을 글자로 붙인 칸(예측 없이 기록만 한 칸)은 0.47 [0.36, 0.58], 0.79, 0.92로 "중간"입니다. 이 모델의 맨 글 값(0.18, 0.73, 0.97)보다 GSM8K에서 높습니다.
- 같은 문장을 문제 글 앞에 글자로 붙였을 때의 GSM8K 값을 네 모델에서 모으면 SFT 0.97, A1 0.74, QFFT 0.63, 시스템 프롬프트 없이 학습한 SFT 0.47입니다. 이 문장을 학습 때 시스템 프롬프트로 본 두 모델(SFT, A1)이 높고, 본 적 없는 두 모델도 문장이 없을 때(0.16, 0.18)보다 높습니다. "학습 때 묶인 몫"과 "지시의 뜻으로 켜지는 몫"이 따로 있다는 읽기와 맞습니다. 학습은 모델마다 한 번이라 순서 자체는 확정이 아닙니다.

## 선행 연구와의 관계

- **원리 자체는 선행 연구가 있습니다(11월 24일 저녁에 원문 확인).** "Base Models Can Reason By Taking a Cue From Training Data"(arXiv 2610.06851, 2026년 10월)는 학습 자료에서 낱말이나 지시문의 구절을 무관한 것으로 바꿔 다시 학습하면 그것이 추론을 켜는 단서가 된다는 것을 보였습니다. 그래서 이 글의 읽기("학습 입력이 긴 풀이를 켜는 단서를 정한다")는 새 원리가 아닙니다. 이 글에 남는 것은 긴 풀이로 SFT한 모델과 QFFT 계열에서 그 원리로 길이 배분을 설명한 부분입니다. 후보 순위를 2에서 5로 내렸습니다.
- QFFT 논문은 평가를 대화 형식으로만 했습니다. 맨 글 입력으로 평가한 결과나, 다른 방식으로 학습한 모델에서 같은 모양이 나온다는 결과는 그 논문에 없습니다.
- 학습 때 넣은 시스템 프롬프트에 모델의 성향이 묶이고 빼면 덜 나타난다는 연구(inoculation prompting 계열)가 있습니다. 대상은 성향과 안전 쪽이고 추론 길이가 아닙니다.
- 공개된 긴 추론 모델의 저장소에는 "시스템 프롬프트가 없으면 생각 형식이 안 나온다"는 사용자 보고가 있습니다. 그래서 "프롬프트를 빼면 꺼진다"를 처음 발견한 것처럼 쓰지 않습니다.
- 학습 입력의 구성요소별로 추론 길이가 무엇에 묶이는지를 평가 입력과 엇갈려 본 연구는 확인한 범위에서 찾지 못했습니다.

## 지금 결과로 어디까지 말할 수 있나 (11월 24일 오후 점검)

"이 결과만으로 논문이 되는가"를 주장별로 따져 봤습니다. 새 계산은 없고, 위 결과와 앞선 글의 판정 값을 크기와 함께 다시 놓은 것입니다.

**표 읽는 법.** "닫힘"은 미리 정한 기준으로 판정이 났다는 뜻입니다. 논문에 충분하다는 뜻은 아닙니다. "닫는 방법"에서 "추론만"은 이미 있는 모델로 문항 수만 늘리면 되는 것이고, "새 학습"은 모델을 다시 학습해야 하는 것입니다.

| 주장 | 지금 근거(크기) | 상태 | 닫는 방법 |
|---|---|---|---|
| SFT의 긴 풀이는 학습 시스템 프롬프트에 묶여 있고, 빼도 정답률은 유지된다 | MATH500 500문항 × 4회. tokens 0.60배 [0.57, 0.64], 바로잡은 ACC +0.4 [−1.6, +2.2]%p, 대조 둘([학습 프롬프트 빼기](2026-11-12-b-drop-training-prompt.html)) | 닫힘(이 모델, MATH500) | 새 학습: 시드를 바꾼 반복. 원인 실험과 함께 진행 중 |
| 단서를 모두 빼면 SFT도 QFFT와 같은 길이 배분이 된다 | 문제 글만 입력, 여섯 체크포인트, MATH500 100문항 × 2회. 문항 단위 상관 0.73 | 길이는 판정됨, 정답률은 판정 불가 | 추론만: 500문항 × 4회(등록함) |
| 어느 단서에 묶이는지는 학습 입력이 정한다 | 학습 형식 네 가지를 한 번씩 학습한 모델, 예측 다섯 칸 중 셋 맞음 | "부분 지지" | 새 학습: 같은 자료에서 학습 입력의 단서 하나만 바꿈. **11월 25일 결과: 미리 정한 판정 "반대".** 무관한 문장으로 바꿔 학습하면 그 문장은 단서가 되지 않았고, 원래 지시문의 힘이 그 지시문으로 학습해서 생겼다는 절반만 확인됨([원인 실험 글](2026-11-24-g-causal-cue-swap.html)) |
| 남이 공개한 모델에서도 같다 | 공개 모델 둘, 100문항. 단서를 빼면 생각 형식 100% → 0%([공개 모델 글](2026-11-24-a-public-model-prompt-gate.html)) | 두 모델에서 닫힘 | 추론만: 크기와 계열이 다른 공개 모델 |
| 재학습 없이 QFFT 수준의 절감을 얻는다 | A1에서 시스템 프롬프트만 빼면 MATH500 500문항에서 ACC −0.4 [−1.8, +1.0]%p, tokens 0.74배 | MATH500, 대화 틀 입력에서 닫힘 | 추론과 채점: 답 형식에 공정한 채점 |

- **왜 100문항으로는 정답률을 말할 수 없나.** 정답률 차의 95% 구간 반폭이 100문항 × 2회에서는 5–7%p였고, 500문항 × 4회에서는 1.4–1.9%p였습니다. ±2%p 안에서 "못지않다"를 말하려면 뒤의 크기가 필요합니다. 길이는 차이가 커서(남는 비율 0.08 대 0.97) 100문항으로도 판정이 납니다.
- **정리하면** 길이 쪽 현상은 이미 큰 효과로 판정됐습니다. 모자란 것은 세 가지입니다. 문제 글만 넣는 입력의 정답률(문항 수를 늘리면 됨), 원인 주장과 시드 반복(새 학습이 있어야 함), 모델 폭(공개 모델을 더 넣으면 됨)입니다.
- **가장 큰 위험.** 새 학습 뒤에도 원인 주장이 "부분 지지"에 머물면 주장을 "평가 입력의 단서가 길이를 가르고, QFFT의 효과는 그것으로 설명된다"로 좁혀야 합니다. 기반 모델이 하나(Qwen2.5-7B)라는 점, 프롬프트 형식에 따라 길이가 달라진다는 것 자체는 이미 알려져 있다는 점도 위험입니다.

## 한계

- 단서 사다리 표는 결과를 보고 모은 표입니다. 미리 정한 기준으로 판정한 것은 문항 단위 일치와 정답률 둘이고, 읽기 자체의 시험은 위 9칸입니다.
- 모델마다 학습은 1번입니다. 문항은 100, 100, 30개이고 맨 글 입력은 문항당 1–2회입니다. 같은 입력을 MATH500 500문항 × 4회로 다시 재는 확인을 11월 24일 오후에 등록했습니다.
- 정답률은 MATH500(A1에서 "못지않음")과 GSM8K(바로잡은 채점으로 1%p 안)에서 확인했습니다. GSM8K는 원래 모델도 92%라 변별이 없고, AIME25는 문항이 적어 판정하지 않았습니다. 어려운 문제에서의 정답률은 아직 열려 있습니다.
- 맨 글 입력은 모델이 평소 쓰이는 방식이 아닙니다. 파이썬 코드 풀이 같은 다른 문체가 섞입니다.

## 다음

1. 9칸은 모두 끝났습니다(위). 이어서 문제 글만 넣는 입력을 전체 크기로 다시 잽니다. SFT, QFFT, A1에 MATH500 500문항 × 4회, GSM8K 300문항 × 2회, AIME25 30문항 × 8회입니다. 미리 적은 예측은 "세 모델 모두 바닥 곡선", "SFT와 QFFT는 같은 곡선", "SFT의 정답률은 QFFT에 못지않음"입니다.
2. 어려운 벤치마크(AIME, AMC)에서 단서 없는 입력의 정답률을 문항 수를 늘려 봅니다.
3. 같은 자료로 학습 입력의 한 요소만 바꿔 학습해, 긴 풀이가 어느 요소에 묶이는지를 직접 봅니다. 11월 24일 오후에 학습을 시작했고 11월 25일 새벽에 결과가 나왔습니다. 미리 적은 예측은 틀렸습니다. 무관한 문장으로 학습한 모델은 그 문장에 묶이지 않고 시스템 프롬프트 없이 학습한 모델처럼 행동했습니다. 값과 판정은 [원인 실험 글](2026-11-24-g-causal-cue-swap.html)에 있습니다.

## 일지에서의 실험 번호

- 개발일지 2026-11-24 "대조 칸 결과", "단서 격자 계획", "단서 격자 보탬 계획", "단서 격자 보탬 결과"
- 연구일지 "2026-11-24 시스템 프롬프트 줄기 3"의 2-6
