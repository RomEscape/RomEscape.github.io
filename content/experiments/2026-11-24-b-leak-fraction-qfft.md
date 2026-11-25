---
title: QFFT의 적응형 추론은 QFFT만의 것이 아니었다, 학습 때의 단서가 빠지면 어디서나 같은 모양이 나온다
date: 2026-11-24
project: QFFT
status: 완료
idea: 후보
idea_rank: 2
method_name: CueResidual
method_examples:
  - title: 쉬운 문항과 어려운 문항에서 긴 풀이가 얼마나 남는지 계산하기
    kind: 실제 실험 예시
    problem: 'MATH500 Level 1 문항(64의 양의 제곱근과 세제곱근의 차, 정답 4)과 AIME25 문항(17_b가 97_b의 약수가 되는 9보다 큰 밑 b의 합, 정답 70)을 모델마다 16번씩 풀었습니다.'
    comparison: '원래 모델, SFT, QFFT의 평균 길이를 견줍니다. 남는 비율은 log(QFFT 길이 ÷ 원래 모델 길이) ÷ log(SFT 길이 ÷ 원래 모델 길이)입니다. 0이면 원래 모델과 같고 1이면 SFT와 같습니다.'
    assessment: '쉬운 문항은 295, 1,077, 332 tokens여서 남는 비율이 0.09이고, AIME25 문항은 942, 3,951, 1,789 tokens여서 0.45입니다. 묶음 단위로는 GSM8K 0.35, AIME25 0.93입니다. 평범하게 학습한 SFT에서 시스템 프롬프트만 빼도 같은 모양이 나왔습니다.'
summary: 저장된 결과로 모델마다 "긴 풀이가 얼마나 남는가"를 난도별로 쟀습니다. QFFT 네 모델 모두 쉬운 문제에서는 조금, 어려운 문제에서는 거의 전부 남았습니다. 평범하게 학습한 모델에서 시스템 프롬프트만 빼도 같은 모양이 나왔고, 학습 때의 단서가 그대로 있는 모델은 난도와 무관하게 늘 길었습니다.
published: true
---

**방법 이름: CueResidual.** 단서(cue)를 뺀 입력에서 파인튜닝으로 늘어난 길이가 얼마나 남는지(residual)를 재는 분석입니다. 글에서는 이 값을 "남는 비율"이라고 부릅니다.

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | SFT에서 시스템 프롬프트를 뺀 답과 공개 모델에서 프롬프트를 뺀 답은 둘 다 쉬운 문제에서 많이 짧아지고 어려운 문제에서는 길게 남았습니다. QFFT가 자기 학습 방법의 장점으로 보고한 모양과 닮았습니다. |
| 든 의문 | QFFT의 적응형 모양은 QFFT 학습만의 성질인가, 학습 때의 단서가 평가 입력에 없으면 어디서나 나오는 모양인가? |
| 그때까지 안 해 본 것 | 모델마다 길이의 크기가 달라 한 표에 놓고 견준 적이 없었습니다. 이 연결을 다룬 연구도 찾지 못했습니다. |
| 그래서 한 것 | 길이를 "파인튜닝으로 늘어난 길이 가운데 그 조건에서 남은 몫"(남는 비율)으로 바꿔, 저장된 평가 결과만으로 모델과 조건을 한 표에 놓았습니다. |
| 답 | 단서가 평가 입력에 그대로 있는 모델은 난이도와 무관하게 늘 길게 풀었습니다. 단서가 없는 경우는 쉬운 문제에서 조금, 어려운 문제에서 거의 전부 남았습니다. 같은 날 이어진 시험에서 "QFFT를 학습 때 형식으로 평가하면 쉬운 문제에서도 길게 풀 것"이라는 예측은 틀렸습니다. |
| 다음 의문 | 무엇이 단서인가? 시스템 프롬프트만인가, 대화 틀도인가? 학습 입력이 다른 모델은 다른 것을 단서로 삼는가? ([단서 사다리](2026-11-24-d-cue-ladder.html)) |

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

- QFFT는 "쉬운 문제는 짧게, 어려운 문제는 길게" 푸는 것을 자기 학습 방법의 장점으로 보고했습니다.
- 같은 모양이 다른 곳에서도 나옵니다. 평범하게 학습한 SFT에서 **시스템 프롬프트만 빼도**, 남이 공개한 모델에서 학습 프롬프트를 빼도, 쉬운 문제에서는 긴 풀이가 조금만 남고 어려운 문제에서는 거의 전부 남습니다.
- 반대로 긴 풀이가 묶인 단서(학습 때 늘 있던 시스템 프롬프트와 대화 틀)가 평가 입력에 그대로 있는 모델은 난도와 무관하게 늘 길게 풉니다.
- 위 분석은 새로 생성한 답 없이 저장된 평가 결과로 계산했습니다.
- 같은 날 뒤이은 시험에서, "QFFT를 학습 때 형식으로 평가하면 쉬운 문제에서도 길게 풀 것"이라는 예측은 틀린 것으로 나왔습니다(아래 "뒤이은 시험").

## 왜 궁금했나

- 같은 날 앞 글에서, 학습 프롬프트를 뺀 공개 모델은 원래 모델로 돌아가지 않고 어려운 문제일수록 긴 풀이가 더 많이 남았습니다.
- QFFT는 학습할 때 질문, 시스템 프롬프트, 대화 표지를 모두 지우고 풀이 글만 학습합니다. 그런데 평가할 때는 대화 틀, 시스템 프롬프트, 질문이 모두 들어갑니다. QFFT 모델은 늘 "학습 때 없던 입력"에서 쓰이는 셈입니다.
- 그렇다면 QFFT의 적응형 추론은 QFFT 학습만의 성질이 아니라, 학습 때의 단서와 평가 입력이 어긋날 때 생기는 공통 모양일 수 있습니다. 이 연결을 다룬 연구는 찾지 못했습니다.

## 용어 풀이

| 용어 | 뜻 | 이 분석에서의 실제 값 |
|---|---|---|
| 원래 모델 | 파인튜닝하기 전의 Qwen2.5-7B-Instruct | 문제를 짧게 바로 풂(평균 305–1,564 tokens) |
| SFT | 질문과 긴 풀이를 그대로 학습한 모델 | 학습 때 시스템 프롬프트 "Please reason step by step, and put your final answer within \boxed{}."가 늘 있었음 |
| QFFT | 질문 없이 풀이만 학습하는 논문 방법 | 우리가 재현한 모델과 저자가 공개한 모델, 학습 자료 두 가지(LIMO, S1.1)로 네 모델 |
| A1 | 학습 때 질문 자리만 비우고 시스템 프롬프트와 대화 틀은 둔 모델 | 우리가 학습 |
| 시스템 프롬프트 없이 학습한 SFT | SFT와 같지만 학습 입력에 시스템 프롬프트가 없던 모델 | 우리가 학습 |
| 남는 비율 | 파인튜닝으로 늘어난 길이 가운데 그 조건에서 남아 있는 몫 | 0이면 원래 모델과 같고, 1이면 SFT가 기본 시스템 프롬프트로 풀 때와 같음 |
| 묶음 | 난도가 비슷한 문항 무리 | GSM8K, MATH500 Level 1–5, AMC23, Minerva, AIME24, AIME25의 10개 |
| 난도 | 묶음이 얼마나 어려운지 | 1 − (SFT의 정답률). GSM8K 88.7%부터 AIME 16.7%까지 |
| Spearman 상관 | 두 값의 순서가 얼마나 같이 움직이는지(−1에서 1) | 남는 비율과 난도의 순서 |
| tokens | 모델이 글을 나눠 세는 단위 | 영어 낱말 하나가 대략 1–2 tokens |

## 실험 예시

### 남는 비율을 문항 하나로 계산해 보기

<figure class="xp">
<a href="../uploads/qfft/2026-11-24/b1-what-leak-fraction-means.png"><img src="../uploads/qfft/2026-11-24/b1-what-leak-fraction-means.png" alt="남는 비율을 눈금 줄로 보인 그림. 쉬운 문항은 원래 모델 295, QFFT 332, SFT 1,077 tokens로 0.09, 어려운 문항은 942, 1,789, 3,951 tokens로 0.45" style="display:block;width:100%;height:auto;border-radius:6px"></a>
<figcaption class="xp-cap">그림 1. 개념 그림과 예시. 원래 모델을 0, SFT를 1로 둔 로그 눈금 위에서 QFFT가 어디에 있는지입니다. 그림을 누르면 원본 크기로 열립니다.</figcaption>
</figure>

MATH500 Level 1 문항입니다.

> What is the difference between the positive square root of 64 and the cube root of 64? (정답 4)

모델마다 이 문항을 16번 풀었을 때의 평균 길이입니다.

| 모델 | 평균 길이 (tokens) | 원래 모델의 몇 배 |
|---|---|---|
| 원래 모델 | 295 | 1.0 |
| SFT | 1,077 | 3.6 |
| QFFT | 332 | 1.1 |

- SFT는 원래 모델의 3.6배로 길게 풀고, QFFT는 1.1배만 씁니다.
- 남는 비율 = log 1.1 ÷ log 3.6 = 0.09. 쉬운 문항이라 QFFT에는 긴 풀이가 거의 남지 않았습니다.

AIME25의 한 문항입니다.

> Find the sum of all integer bases b>9 for which 17_b is a divisor of 97_b. (정답 70)

| 모델 | 평균 길이 (tokens) | 원래 모델의 몇 배 |
|---|---|---|
| 원래 모델 | 942 | 1.0 |
| SFT | 3,951 | 4.2 |
| QFFT | 1,789 | 1.9 |

- 남는 비율 = log 1.9 ÷ log 4.2 = 0.45. 어려운 문항에서는 더 많이 남습니다.

### 묶음 단위로는

실제 분석은 문항별 길이 비를 묶음 안에서 기하평균한 뒤 같은 식에 넣습니다.

| 묶음 | SFT는 원래 모델의 | QFFT는 원래 모델의 | 남는 비율 |
|---|---|---|---|
| GSM8K (쉬움) | 5.8배 | 1.9배 | 0.35 |
| AIME25 (어려움) | 19.2배 | 15.8배 | 0.93 |

## 무엇을 했나

| 항목 | 내용 |
|---|---|
| 자료 | 저장된 표준 평가(기본 시스템 프롬프트, 문항당 16회, 최대 32,000 tokens)와 앞선 실험의 시스템 프롬프트 제거 결과(문항당 4회) |
| 모델 | 원래 모델, SFT, A1, QFFT 네 가지, S1.1 SFT, 시스템 프롬프트 없이 학습한 SFT |
| 묶음 | GSM8K(300문항 표본), MATH500 Level 1–5, AMC23, Minerva, AIME24, AIME25 |
| 계산 | 남는 비율 = log(그 모델의 길이 ÷ 원래 모델의 길이) ÷ log(같은 자료로 학습한 SFT의 길이 ÷ 원래 모델의 길이) |

- 판정 기준은 계산 전에 연구 기록에 적었습니다.
- "남는 비율"이라는 지표 자체는 같은 날 공개 모델 결과를 본 뒤에 만들었습니다. QFFT와 다른 모델의 값은 기준을 적은 뒤에 계산했습니다.

## 결과

아래 표에서 "프롬프트"는 시스템 프롬프트를 줄여 쓴 말입니다.

쉬운 쪽(GSM8K와 MATH500 난이도 등급 L1–L5):

| 모델과 평가 조건 | GSM8K | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|---|
| QFFT (우리 재현) | 0.35 | 0.43 | 0.46 | 0.60 | 0.67 | 0.79 |
| QFFT (저자 공개) | 0.32 | 0.43 | 0.45 | 0.58 | 0.66 | 0.78 |
| S1.1 QFFT (우리 재현) | 0.09 | 0.16 | 0.19 | 0.28 | 0.39 | 0.58 |
| S1 QFFT (저자 공개) | 0.07 | 0.12 | 0.17 | 0.25 | 0.37 | 0.56 |
| SFT, 프롬프트 뺌 | 0.80 | 0.65 | 0.65 | 0.67 | 0.73 | 0.83 |
| A1, 프롬프트 뺌 | 0.15 | 0.24 | 0.29 | 0.43 | 0.51 | 0.64 |
| QFFT, 프롬프트 뺌 | 0.16 | 0.27 | 0.34 | 0.47 | 0.53 | 0.68 |
| A1, 기본 프롬프트 | 0.94 | 0.94 | 0.94 | 0.95 | 0.96 | 0.96 |
| 프롬프트 없이 학습한 SFT, 기본 프롬프트 | | 0.93 | 0.95 | 0.97 | 0.96 | 0.99 |
| 프롬프트 없이 학습한 SFT, 프롬프트 뺌 | | 0.96 | 0.96 | 0.98 | 1.00 | 0.99 |

어려운 쪽:

| 모델과 평가 조건 | AMC23 | Minerva | AIME24 | AIME25 |
|---|---|---|---|---|
| QFFT (우리 재현) | 0.85 | 0.74 | 0.96 | 0.93 |
| QFFT (저자 공개) | 0.82 | 0.73 | 0.93 | 0.92 |
| S1.1 QFFT (우리 재현) | 0.64 | 0.50 | 0.84 | 0.74 |
| S1 QFFT (저자 공개) | 0.59 | 0.46 | 0.82 | 0.76 |
| SFT, 프롬프트 뺌 | | | | 0.93 |
| A1, 프롬프트 뺌 | | | | 0.90 |
| A1, 기본 프롬프트 | | | | 0.97 |

**표 읽는 법.** 한 칸은 "그 조건에서 긴 풀이가 얼마나 남았는가"입니다. 첫 행의 GSM8K 0.35는 쉬운 문제에서 QFFT에 긴 풀이가 35%만 남았다는 뜻이고, AIME25 0.93은 어려운 문제에서는 93%가 남았다는 뜻입니다. 빈칸은 저장된 결과가 없는 묶음입니다. L1–L5는 MATH500의 난이도 등급입니다.

- **첫 표의 위 일곱 행(오르는 모양).** QFFT 네 모델과 시스템 프롬프트를 뺀 세 조건은 모두 왼쪽(쉬움)에서 낮고 오른쪽(어려움)으로 갈수록 높아집니다. 둘째 표의 AIME에서는 0.74–0.96으로 모입니다.
- **첫 표의 아래 세 행(늘 높음).** A1의 기본 시스템 프롬프트 조건과 시스템 프롬프트 없이 학습한 SFT는 난도와 무관하게 0.93–1.00입니다. 이 모델들은 긴 풀이가 묶인 단서가 평가 입력에 그대로 있습니다.
- A1은 학습 때 질문 자리가 비어 있었는데도 늘 길게 풉니다. 질문이 학습 때 없고 평가 때 있다는 것만으로는 짧아지지 않습니다.
- 쉬운 쪽의 높이는 조건마다 다릅니다. 시스템 프롬프트를 뺀 SFT가 가장 높고(0.65–0.80), QFFT(0.35–0.46), 시스템 프롬프트를 뺀 A1과 QFFT(0.15–0.34), S1.1 QFFT(0.07–0.19) 순입니다.
- 구간 예: QFFT GSM8K 0.35 [0.31, 0.40], AIME25 0.93 [0.89, 0.97]. SFT에서 시스템 프롬프트를 뺀 조건 GSM8K 0.80 [0.77, 0.83], AIME25 0.93 [0.89, 0.97].
- 같은 날 앞 글의 공개 모델(Bespoke-Stratos-7B, 학습 프롬프트를 뺌)은 0.18(GSM8K), 0.41(MATH500), 0.66(AIME25)이었습니다. 이쪽은 최대 길이와 횟수가 다른 설정입니다.

## 뒤이은 시험: QFFT를 학습 때 형식으로 평가 (같은 날 추가)

위 결과에서 한 가지 예측을 세워 시험했습니다. QFFT는 대화 틀과 시스템 프롬프트 없이 풀이 글만 학습했으니, 평가도 그 형식(문제 글만)으로 하면 쉬운 문제에서도 길게 풀 것이라는 예측입니다.

| 벤치마크 | 남는 비율: 학습 형식(문제 글만) | 남는 비율: 대화 형식 | 학습 형식의 평균 길이 | 긴 풀이 비율 |
|---|---|---|---|---|
| GSM8K | 0.16 | 0.29 | 957 tokens | 20.0% |
| MATH500 | 0.55 | 0.61 | 4,199 tokens | 29.5% |
| AIME25 | 0.90 | 0.93 | 17,349 tokens | 88.3% |

- **예측이 틀렸습니다.** 학습 때 형식으로 평가해도 쉬운 문제는 짧게, 어려운 문제는 길게 풉니다. 미리 정한 기준(GSM8K와 MATH500의 값이 대화 형식 값 + 0.15 미만이면 "학습 형식에서도 적응형")으로 "학습 형식에서도 적응형"입니다.
- 그래서 "QFFT의 적응형 추론은 대화 형식과의 어긋남에서 온다"는 읽기는 버립니다.
- 남는 읽기는 이렇습니다. QFFT는 입력 없이 풀이만 학습해서, 긴 풀이를 켜는 단서가 대화 형식에도 맨 글 형식에도 없습니다. 그래서 어떤 형식으로 문제를 주든 같은 모양이 나옵니다. 단서를 보고 학습한 모델은 그 단서를 뺐을 때 같은 모양이 됩니다. 질문만 지우고 단서는 둔 A1은 단서가 있으면 늘 깁니다.
- 우리가 재현한 QFFT 한 모델, MATH500 100문항 × 2회, AIME25 30 × 2회, GSM8K 100문항 × 1회의 결과입니다. 저자 공개 모델도 0.14(GSM8K), 0.62(MATH500), 0.86(AIME25)으로 같은 판정이 나왔습니다.
- 비교용으로 SFT에 같은 입력(문제 글만)을 넣었더니 SFT도 0.08, 0.49, 0.87로 같은 값을 냈습니다. 이 결과와 그 뒤의 분석은 [단서 사다리 글](2026-11-24-d-cue-ladder.html)에 정리했습니다.

## 미리 정한 기준으로는

| 판정 | 기준 | 결과 |
|---|---|---|
| QFFT 네 모델 각각 | 묶음 10개에서 남는 비율과 난도의 Spearman 상관이 0.7 이상이면 "난도에 따라 오름" | 네 모델 모두 0.879로 **오름** |
| 시스템 프롬프트를 뺀 SFT 대 QFFT | 둘 다 값이 있는 묶음 7개에서 차의 절댓값 평균이 0.15 이하면 "같은 곡선" | 0.149로 **같은 곡선**(기준에 걸친 값) |

"같은 곡선" 판정은 기준을 아슬아슬하게 넘었습니다. 두 곡선은 오르는 모양과 어려운 쪽의 값이 같고, 쉬운 쪽에서는 시스템 프롬프트를 뺀 SFT가 더 많이 남습니다(GSM8K 0.80 대 0.35).

## 이 결과로 말할 수 있는 것과 없는 것

**말할 수 있는 것**

- "쉬운 문제에서는 긴 풀이가 조금 남고 어려운 문제에서는 거의 다 남는" 모양은 QFFT 네 모델에서 모두 나옵니다.
- 같은 모양이 QFFT가 아닌 평범한 SFT에서도, 평가 때 시스템 프롬프트를 빼기만 하면 나옵니다.
- 긴 풀이가 묶인 단서가 평가 입력에 그대로 있는 모델에서는 이 모양이 없습니다.

**아직 말할 수 없는 것**

- 두 현상의 원인이 같다는 것. 관찰한 모양이 같을 뿐이고, 모델은 각각 한 번씩만 학습했습니다. 뒤이은 시험에서 "대화 형식과의 어긋남이 원인"이라는 한 가지 설명은 틀린 것으로 나왔습니다.
- 쉬운 쪽의 높이가 조건마다 다른 이유.
- 정답률. 이 분석은 길이만 봤습니다. "적응형"이라고 부르려면 정답률이 유지되는지도 함께 봐야 합니다(앞선 글들에서 SFT는 MATH500과 Minerva에서 유지, 가장 어려운 묶음은 판정 불가였습니다).

## 선행 연구와의 관계

| 이번 분석 | 가장 가까운 자료 | 이번에 다른 점 |
|---|---|---|
| QFFT의 적응형 추론을 다른 조건과 한 지표로 비교 | QFFT(2506.12860)는 질문과 시스템 프롬프트, 대화 표지를 함께 지우고 학습한 결과로 보고. 저장소의 저자 댓글에 "시스템 프롬프트를 두든 빼든 QFFT 학습 결과가 비슷했다"는 한 줄이 있음 | 평범한 SFT에서 평가 때 시스템 프롬프트만 빼도 같은 모양이 나온다는 것, 단서가 그대로 있는 모델에서는 안 나온다는 것을 같은 지표로 보임 |
| 학습 자료의 연결이 추론을 켜는 단서를 정한다는 원리 | "Base Models Can Reason By Taking a Cue From Training Data"(2610.06851). 학습 자료의 낱말이나 지시문 구절을 무관한 것으로 바꿔 학습하면 그것이 추론 단서가 됨. 대화 형식을 배우기 전의 모델, 지표는 정답률 | 이 원리를 QFFT에 적용해, QFFT의 길이 배분이 "단서가 평가 입력에 없어서" 나온다는 것을 평범한 SFT와 나란히 보임. 원리는 새것이 아님 |
| 프롬프트만 바꿔 난도별 배분을 얻을 수 있는가 | AutoThink(2505.10832)는 R1 증류 모델에서 "프롬프트만으로는 난도에 따른 배분이 나오지 않는다"고 보고. Reasoning Shift(2604.01161)는 입력 조건이 달라지면 추론이 짧아지고 정확도가 내려간다고 보고 | 우리 결과는 긴 풀이로 SFT한 모델에서 학습 단서를 빼면 난도별 배분이 나오고 MATH500 정답률이 유지된다는 것. 모델 계열이 달라 맞서는 결과로 함께 적고, R1 증류 모델에서의 확인을 계획 |
| 학습 때의 조건에 행동이 묶인다는 틀 | 학습 때 넣은 시스템 프롬프트에 성향이 묶여, 빼면 그 성향이 줄어든다는 연구들(2510.04340, 2510.05024). 모두 안전 성향 대상 | 추론 길이에 적용하고, 줄어드는 정도가 난도에 따라 달라진다는 점을 봄 |

## 한계

- 모든 모델은 학습을 한 번씩만 했습니다.
- 원래 모델의 길이는 기본 시스템 프롬프트 조건의 것을 모든 칸에 썼습니다.
- 시스템 프롬프트를 뺀 조건은 문항당 4회, 표준 평가는 16회입니다. GSM8K는 300문항 표본입니다.
- 지표를 결과를 본 뒤 만들었습니다(판정 기준과 QFFT의 값은 그 뒤).
- 길이만 봤고 정답률은 넣지 않았습니다.

## 다음

1. 정답률을 같은 묶음으로 나란히 놓아, 길이가 준 만큼 정답률을 잃는지 봅니다. → MATH500 전체 문항으로 계산해 단서 사다리 글에 넣었습니다(시스템 프롬프트를 뺀 A1은 QFFT와 정답률이 같음).
2. 쉬운 쪽의 높이를 정하는 것이 무엇인지 봅니다(빠진 단서의 종류와 양).
3. 같은 자료로 시스템 프롬프트만 바꿔 직접 학습하면 이 곡선이 어떻게 움직이는지 봅니다(학습이 필요한 실험).

## 일지에서의 실험 번호

남는 비율 분석 (11월 24일).
