---
title: 공개된 긴 추론 모델 둘 다 학습 때의 입력 단서를 모두 빼면 긴 풀이 형식이 꺼진다, 묶인 단서는 모델마다 달랐다
date: 2026-11-24
project: QFFT
status: 진행 중
idea: 후보
idea_rank: 4
method_name: CueGate
method_examples:
  - title: 공개 모델에서 학습 때의 시스템 프롬프트만 빼기
    kind: 실제 실험 예시
    problem: 'MATH500 Level 1 문항은 64의 양의 제곱근과 세제곱근의 차를 묻습니다. 정답은 4입니다. 모델은 공개 모델 Bespoke-Stratos-7B입니다.'
    comparison: '한 조건은 학습 때 쓰인 시스템 프롬프트(1,312자)를 넣고, 다른 조건은 시스템 프롬프트 자리를 뺍니다. 사용자 칸은 두 조건이 같습니다.'
    assessment: '넣은 조건의 두 답은 1,016과 822 tokens이고 생각 형식 표지로 시작했습니다. 뺀 조건은 268과 305 tokens이고 "To solve the problem …"처럼 원래 모델식으로 시작했습니다. 네 답 모두 정답입니다. 전체로는 360개 답 모두에서 생각 형식이 사라졌고 길이는 0.30–0.40배였습니다. 다만 GSM8K 정답률은 96.0%에서 90.0%로 내려갔습니다.'
summary: 공개 모델 Bespoke-Stratos-7B는 학습 때 쓴 시스템 프롬프트를 빼자 생각 형식이 100%에서 0%가 됐습니다. 더 큰 자료를 학습한 OpenThinker-7B는 시스템 프롬프트만 빼면 95–100% 남았지만, 사용자 칸에 늘 붙던 고정 문장까지 빼자 0%가 됐습니다. 두 모델 모두 긴 풀이 형식이 학습 때의 입력 단서에 묶여 있고, 묶인 단서가 서로 다릅니다.
published: true
---

**방법 이름: CueGate.** 공개 모델에서 학습 때의 단서(cue)가 긴 풀이 형식을 여닫는 문(gate)처럼 작동한다는 관찰에 붙인 이름입니다.

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | 표준 SFT는 학습 때의 시스템 프롬프트를 평가 입력에서 빼면 답이 짧아집니다(평균 6,507 → 4,899 tokens). 다만 지금까지는 모두 직접 학습한 모델에서 본 것입니다. |
| 든 의문 | 공개된 긴 추론 모델(Bespoke-Stratos-7B, OpenThinker-7B)도, 그 모델이 학습 때 본 프롬프트를 빼면 긴 풀이를 하지 않게 되는가? |
| 그때까지 안 해 본 것 | 공개 모델은 늘 정해진 시스템 프롬프트를 붙여 평가합니다. 사용자들 사이에 "시스템 프롬프트가 없으면 생각 형식이 안 나온다"는 말은 있었지만, 답 길이와 정답률을 난이도별로 같은 조건에서 잰 자료는 찾지 못했습니다. |
| 그래서 한 것 | 공개 모델 둘(Bespoke-Stratos-7B, OpenThinker-7B)의 평가 입력에서, 그 모델이 학습 때 본 요소(시스템 프롬프트, 질문 앞에 늘 붙던 고정 문장)를 하나씩 뺐습니다. |
| 답 | Bespoke-Stratos-7B는 답 360개가 모두 생각 형식(`<|begin_of_thought|>`)으로 시작하다가, 시스템 프롬프트를 빼자 360개 모두 그 형식 없이 짧게 풀었습니다(길이 0.30–0.40배). OpenThinker-7B는 시스템 프롬프트만 빼면 95–100%가 여전히 생각 형식이었고, 질문 앞의 고정 문장까지 빼야 0%가 됐습니다. 모델마다 긴 풀이를 켜는 입력 요소가 달랐습니다. |
| 다음 의문 | QFFT가 장점으로 내세운 "쉬운 문제는 짧게, 어려운 문제는 길게"도, 학습 때의 입력 요소가 평가 입력에 없으면 어느 모델에서나 나오는 모양 아닌가? ([남는 비율로 QFFT 다시 읽기](2026-11-24-b-leak-fraction-qfft.html)) |

질문의 사슬 전체는 [연구 질문으로 다시 쓴 QFFT 연구](2026-11-25-a-research-questions.html)에 있습니다.

## 메인 표: Base, SFT, A1, A2, QFFT와 추론 입력을 바꾼 조건

<!-- qfft-main-table-start -->

**표 읽는 법.** 한 줄이 "모델 + 추론 입력" 하나입니다. ACC는 정답률(%), Tokens는 답 하나의 평균 출력 tokens입니다. "구분"이 줄의 뜻입니다. 기준은 학습 방법이 다른 모델들을 표준 평가 그대로 잰 값이고, 굵게 적은 A2와 QFFT가 견줄 상대입니다. 방법은 표준 SFT를 다시 학습하지 않고 추론 입력만 바꾼 값입니다. 참고는 같은 입력 변경을 다른 모델에 얹어 본 값입니다. "대기"는 지금 돌고 있는 칸입니다.

| 구분 | 모델 | 추론 입력 | GSM8K ACC | GSM8K Tokens | MATH500 ACC | MATH500 Tokens | AIME25 ACC | AIME25 Tokens |
|---|---|---|---|---|---|---|---|---|
| 기준 | Base | 기본 프롬프트 | 92.0 | 301 | 76.1 | 635 | 8.8 | 1,060 |
| 기준 | SFT | 기본 프롬프트 | 91.6 | 2,060 | 81.0 | 6,576 | 16.7 | 20,574 |
| 기준 | A1 | 기본 프롬프트 | 91.4 | 1,856 | 80.9 | 6,149 | 17.5 | 18,965 |
| 기준 | **A2** | 기본 프롬프트 | **91.6** | **888** | **81.3** | **4,587** | **17.5** | **17,735** |
| 기준 | **QFFT** | 기본 프롬프트 | **92.0** | **831** | **81.4** | **4,630** | **15.4** | **18,133** |
| 방법 (SysDrop) | SFT | 시스템 프롬프트 제거 | 91.0 | 1,517 | 80.9 | 4,899 | 19.2 | 18,382 |
| 방법 (CueDrop) | SFT | 문제 글만 | 대기 | 대기 | 81.4 | 4,221 | 대기 | 대기 |
| 참고 | A1 | 시스템 프롬프트 제거 | 91.5 | 587 | 81.6 | 3,778 | 12.5 | 16,270 |
| 참고 | A2 | 시스템 프롬프트 제거 | 91.6 | 514 | 82.0 | 3,948 | 값 없음 | 값 없음 |
| 참고 | QFFT | 시스템 프롬프트 제거 | 91.3 | 630 | 82.5 | 4,122 | 값 없음 | 값 없음 |
| 참고 | QFFT | 문제 글만 | 대기 | 대기 | 77.5 | 5,046 | 대기 | 대기 |

- **모델.** Base는 파인튜닝 전의 Qwen2.5-7B-Instruct입니다. 나머지는 모두 LIMO 817문항으로 학습했습니다. SFT는 QFFT 논문이 비교 기준으로 쓴 표준 SFT로, 시스템 프롬프트와 질문, 긴 풀이를 그대로 학습한 모델입니다. A1은 질문을 지우고, A2는 질문을 지우고 응답 첫 토큰의 loss까지 빼고, QFFT는 논문 방법대로 질문 없이 풀이만으로 학습한 모델입니다.
- **무엇을 견주는가.** A2와 QFFT는 학습 방법을 바꿔 새로 학습한 모델입니다. 방법 줄은 표준 SFT의 가중치를 그대로 두고 추론 입력만 바꾼 것입니다. A2나 QFFT 위에 얹은 것이 아니라, A2, QFFT와 나란히 견주는 다른 길입니다. 같은 입력 변경을 A1, A2, QFFT에 얹어 본 값은 참고 줄에 따로 두었습니다.
- **추론 입력.** 기본 프롬프트는 대화 틀, 시스템 프롬프트 "Please reason step by step, and put your final answer within \boxed{}.", 질문으로 이루어집니다. 시스템 프롬프트 제거는 거기서 시스템 프롬프트만 뺀 입력이고, 문제 글만은 대화 틀까지 빼고 질문 글자만 준 입력입니다. 실제 문자열은 아래 "실제 입력과 실제 답"에 있습니다.
- **크기.** GSM8K 1,319문항, MATH500 500문항, AIME25 30문항입니다. 기본 프롬프트 줄은 문항마다 16회, 나머지 줄은 4회 풀게 했습니다. 최대 32,000 tokens입니다.
- **채점.** GSM8K와 MATH500의 ACC는 `\boxed{}` 없이 끝난 답을 직접 읽어 반영하고, 표기만 다른 같은 답을 맞게 고친 값입니다(GSM8K는 평가 자료의 정답 16문항도 바로잡았습니다). AIME25는 공식 채점 스크립트 값 그대로입니다.
- **읽기.** MATH500에서 표준 SFT에 문제 글만 준 줄(CueDrop)은 ACC 81.4%, 4,221 tokens입니다. A2(81.3%, 4,587)와 QFFT(81.4%, 4,630)와 정답률이 같고 8–9% 짧습니다. GSM8K와 AIME25의 같은 칸은 아직 돌지 않았습니다. 참고 줄을 보면 A2와 QFFT도 시스템 프롬프트를 빼면 더 짧아집니다(3,948, 4,122 tokens).

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

### 공개 모델에 실제로 넣은 입력과 답

공개 모델 OpenThinker-7B에 실제로 넣은 입력과 저장된 실제 출력입니다. 문항은 MATH500의 Level 3 문제이고 정답은 9입니다. 시스템 프롬프트는 1,312자라 가운데를 줄였습니다.

<!-- xp-public -->
<figure class="xp"><p class="xp-t">공개 모델에서 학습 때의 단서를 뺍니다 (OpenThinker-7B, MATH500 문항 3, 정답 9)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Your role as an assistant involves thoroughly exploring questions through a systematic long thinking process before providing the final precise and accurate solutions. <span class="xp-sp">(가운데 줄임, 전체 1,312자)</span> Now, try to solve the following question through the above guidelines:</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Return your final response within \boxed{}.</div><div class="">How many positive whole-number divisors does 196 have?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">표준 입력(그 모델이 학습 때 본 입력)</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Your role as an assistant involves thoroughly exploring questions through a systematic long thinking process before providing the final precise and accurate solutions. <span class="xp-sp">(가운데 줄임, 전체 1,312자)</span> Now, try to solve the following question through the above guidelines:</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div></div><div class="xp-del"><div class="">Return your final response within \boxed{}.</div></div><div class="xp-ctx"><div class="">How many positive whole-number divisors does 196 have?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">단서를 뺀 입력</div></div></div><div class="xp-note"><b>바꾸는 것</b>추론 입력에서 학습 때의 시스템 프롬프트와, 사용자 칸 앞에 늘 붙던 고정 문장을 뺍니다. 대화 표지는 그대로 둡니다.<b>그대로 두는 것</b>모델의 가중치, 문제, 온도 0.6, top_p 1, 최대 16,384 tokens. 문항마다 4번 풀게 했습니다.</div><div class="xp-cols" style="margin-top:14px"><div><p class="xp-name">표준 입력: 4번 모두 정답, 1,485–2,019 tokens(평균 1,812)</p><pre class="xp-ex">&lt;|begin_of_thought|&gt;
Okay, so I need to figure out how many positive whole-number divisors 196 has. Let me start by recalling what a divisor is. A divisor of a number is another whole number that can …
<span class="xp-sp">(가운데 줄임)</span>
… 196 \).  
   This confirms there are **9 divisors**.
**Final Answer**:  
196 has \(\boxed{9}\) positive whole-number divisors.
<span class="xp-hit">&lt;|end_of_solution|&gt;</span></pre></div><div><p class="xp-name">단서를 뺀 입력: 1번은 557 tokens로 정답, 3번은 294–460 tokens 지점에서 정답을 쓰고도 끝내지 못해 16,384 tokens</p><pre class="xp-ex">To determine how many positive whole-number divisors 196 has, we start by finding its prime factorization. The number 196 is an even number, so it's …
<span class="xp-sp">(가운데 줄임)</span>
… 4, 7, 14, 28, 49, 98, 196

Counting these, we have 9 divisors. Thus, the answer is \(<span class="xp-hit">\boxed{9}</span>
<span class="xp-sp">(여기가 313 tokens 지점. 정답을 썼지만 끝내지 않고 이어 씀. 가운데 줄임)</span>
… 
Final Answer: <span class="xp-hit">\boxed{9}</span> 

After thorough analysis, the answer is <span class="xp-hit">\boxed{9}</span>. 

Final Answer: \boxed{</pre></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 새로 생성</span></div><p class="xp-cap">글상자는 저장된 실제 출력입니다. 표준 입력의 답은 학습 형식의 끝 표지(빨간 글자)로 끝납니다. 단서를 뺀 입력의 답은 정답을 쓴 뒤에도 "Final Answer" 줄을 최대 길이까지 되풀이했고, 채점 규칙은 최대 길이에 닿은 답을 오답으로 셉니다.</p></figure>
<!-- /xp-public -->

- 표준 입력으로는 네 번 모두 1,485–2,019 tokens로 맞혔습니다.
- 단서를 뺀 입력으로는 한 번은 557 tokens로 맞혔고, 세 번은 294–460 tokens 지점에서 정답 9를 쓰고도 끝내지 못했습니다. 채점 규칙은 최대 길이에 닿은 답을 오답으로 세므로 그 세 번은 오답입니다.


## 한 줄 요약

1. **공개 모델에서도 같은 현상.** Bespoke-Stratos-7B는 학습 때 쓴 시스템 프롬프트가 있으면 답 360개가 모두 `<|begin_of_thought|>`로 시작해 길게 풉니다. 그 프롬프트를 빼면 360개 모두에서 이 형식이 사라지고 "To …"로 시작하는 짧은 답이 됩니다. 길이는 0.30–0.40배가 됐고, 정답률은 MATH500에서 4.5%p, GSM8K에서 6.0%p 낮았습니다. 다만 파인튜닝하기 전의 원래 모델과 같아진 것은 아닙니다. 답은 원래 모델보다 1.3배(GSM8K), 2.2배(MATH500), 5.8배(AIME25) 길어, 어려운 문제일수록 긴 풀이가 더 많이 남았습니다.
2. **문턱 분석.** 표준 SFT에 지금까지 넣어 본 조건 18개를 한꺼번에 놓고 보면, 조건들은 "긴 풀이가 꺼진 쪽"과 "켜진 쪽" 두 묶음으로 갈립니다. 간결 문장("answer concisely")은 켜진 쪽입니다. 긴 풀이를 끄는 것이 아니라 켠 채로 짧게 쓰게 합니다.
3. **비교할 수 있게 크기를 맞춤.** 공개 모델 실험은 앞선 실험과 문항 수와 최대 길이가 달라, 직접 학습한 모델의 저장된 답을 같은 크기로 다시 계산해 나란히 놓았습니다.

4. **둘째 공개 모델도 묶여 있었고, 묶인 단서가 달랐습니다(같은 날 오후에 고침).** 같은 시스템 프롬프트로 더 큰 자료를 학습한 OpenThinker-7B는 시스템 프롬프트만 빼면 생각 형식이 95–100% 남았습니다. 그런데 학습 때 사용자 칸의 문제 앞에 늘 붙던 고정 문장("Return your final response within \boxed{}.")까지 빼자 0%, 0.5%, 0%가 됐습니다. 고정 문장 없이 시스템 프롬프트만 넣으면 다시 100%입니다. 이 모델은 두 단서 가운데 하나만 있어도 켜지고, 둘 다 없어야 꺼집니다. 오전에 적은 "하나는 꺼지지 않는다"는 단서를 하나만 뺀 값이었습니다.

공개 모델 쪽 조건은 11월 24일 오후에 모두 끝났습니다. 크기와 계열이 다른 공개 모델은 아직 보지 않았습니다.

<figure class="xp">
<a href="../uploads/qfft/2026-11-24/a2-two-public-models.png"><img src="../uploads/qfft/2026-11-24/a2-two-public-models.png" alt="공개 모델 두 개의 대조 표. MATH500에서 생각 형식으로 시작한 비율. Bespoke-Stratos-7B는 시스템 프롬프트와 고정 문장이 모두 있으면 100%, 고정 문장만 있으면 0%, 시스템 프롬프트만 있으면 100%, 둘 다 없으면 0%. OpenThinker-7B는 차례로 100%, 97%, 100%, 0.5%. 둘 다 없을 때의 길이는 0.29배와 0.40배이고 두 모델 모두 묶임 판정" style="display:block;width:100%;height:auto;border-radius:6px"></a>
<figcaption class="xp-cap">그림 1. 개념 그림. 같은 기반 모델과 같은 프롬프트로 학습한 공개 모델 둘이 다르게 반응했습니다. 그림을 누르면 원본 크기로 열립니다.</figcaption>
</figure>

## 왜 궁금했나

- 지금까지의 결과는 모두 우리가 직접 학습한 모델에서 나왔습니다. "긴 풀이는 학습 때 본 지시 문장에 묶여 있다"가 직접 학습한 모델만의 일인지, 긴 풀이를 따라 배운 모델의 일반 성질인지 알 수 없었습니다.
- 공개 모델은 학습 때 쓴 시스템 프롬프트가 학습 자료에 그대로 남아 있습니다. 그래서 새로 학습하지 않고도 같은 질문을 던질 수 있습니다.
- 사용자들 사이에서는 "시스템 프롬프트가 없으면 생각 형식이 안 나온다"는 말이 이미 있었습니다(아래 "선행 연구와의 관계"). 길이, 난도, 정답률을 같은 조건으로 잰 자료는 찾지 못했습니다.

## 용어 풀이

| 용어 | 뜻 | 이 실험에서의 실제 값 |
|---|---|---|
| 시스템 프롬프트 | 대화 맨 앞, 질문보다 먼저 들어가는 지시 자리 | 조건마다 바꾸거나 뺌 |
| Bespoke-Stratos-7B | 다른 연구팀이 Qwen2.5-7B-Instruct에 긴 풀이 약 1만 7천 개를 학습시켜 공개한 모델 | 직접 학습한 모델과 기반 모델이 같음 |
| 학습 프롬프트 (T) | 그 모델을 학습할 때 모든 자료에 붙어 있던 시스템 프롬프트 | "Your role as an assistant involves thoroughly exploring questions through a systematic long thinking process …"로 시작하는 1,312자 |
| 없음 (N) | 시스템 프롬프트 자리를 통째로 뺌 | 사용자 칸은 그대로 |
| 대화 틀 기본 문장 (D) | 시스템 프롬프트를 따로 주지 않으면 대화 틀이 자동으로 넣는 문장 | "You are Qwen, created by Alibaba Cloud. You are a helpful assistant." |
| 원래 모델 | 파인튜닝하기 전의 Qwen2.5-7B-Instruct | 같은 입력을 넣어 비교 |
| 사용자 칸 | 질문이 들어가는 자리 | 학습 자료와 같게 "Return your final response within \boxed{}. " 뒤에 문제 |
| 생각 형식 | 답이 `<|begin_of_thought|>` … `<|end_of_thought|>` 안에 긴 생각을 쓰고 그 뒤에 풀이를 쓰는 형식 | 이 표지가 있는 답의 비율로 잼 |
| Long-CoT | 재검토와 되돌아보기가 들어간 긴 풀이 | 원본 논문 분석 코드의 판별 규칙(낱말 기준) |
| tokens | 모델이 글을 나눠 세는 단위 | 영어 낱말 하나가 대략 1–2 tokens |
| 토큰 비 | 같은 문항에서 바꾼 조건의 평균 길이 ÷ 기준 조건의 평균 길이를 문항마다 구해 기하평균한 값 | 1보다 작으면 짧아진 것 |
| ACC | 정답률 | 공식 채점 함수, 정상으로 끝난 답만 정답 |
| 95% CI | 문항을 다시 뽑아 2,000번 계산했을 때 값의 95%가 들어오는 범위 | 대괄호 안의 두 수 |
| 표준 SFT | QFFT 논문이 비교 기준으로 쓴 표준 SFT. Qwen2.5-7B-Instruct에 LIMO 817문항을 시스템 프롬프트, 질문, 긴 풀이 그대로 학습시킨 모델(이 연구에서 직접 학습) | 학습 프롬프트는 "Please reason step by step, and put your final answer within \boxed{}." |
| 문턱 | 긴 풀이로 들어갈지를 가르는 기준선 | 조건마다 값 하나(b)로 맞춤 |

## 실험 예시

<figure class="xp">
<a href="../uploads/qfft/2026-11-24/a1-public-model-prompt-removal.png"><img src="../uploads/qfft/2026-11-24/a1-public-model-prompt-removal.png" alt="Bespoke-Stratos-7B에 학습 때의 시스템 프롬프트를 넣은 입력과 뺀 입력. 넣으면 생각 형식과 Okay로 시작해 1,016과 822 tokens, 빼면 To와 First로 시작해 268과 305 tokens" style="display:block;width:100%;height:auto;border-radius:6px"></a>
<figcaption class="xp-cap">그림 2. 예시 그림. 시스템 프롬프트 자리만 다른 두 입력과 응답의 시작입니다. 그림을 누르면 원본 크기로 열립니다.</figcaption>
</figure>

MATH500 Level 1 문항입니다(앞선 글들과 같은 문항).

> What is the difference between the positive square root of 64 and the cube root of 64? (정답 4)

Bespoke-Stratos-7B에 넣은 입력은 두 가지이고, 시스템 프롬프트 자리만 다릅니다.

| 조건 | 시스템 프롬프트 | 사용자 칸 |
|---|---|---|
| T | 학습 프롬프트 1,312자 | "Return your final response within \boxed{}. What is the difference …" |
| N | (자리 없음) | 위와 같음 |

조건마다 답을 두 번 받았습니다.

| 조건 | 길이 (tokens) | 끝 |
|---|---|---|
| T, 답 1 | 1,016 | `\boxed{4}` 뒤 `<|end_of_solution|>` |
| T, 답 2 | 822 | `\boxed{4}` 뒤 `<|end_of_solution|>` |
| N, 답 1 | 268 | "Final answer: `\boxed{4}`" |
| N, 답 2 | 305 | "So, the final answer is 4. `\boxed{4}`" |

응답의 첫머리:

- T, 답 1: "`<|begin_of_thought|>` Okay, let's tackle this problem step by step. The question is asking for the difference between …"
- T, 답 2: "`<|begin_of_thought|>` Okay, so I need to find the difference between the positive square root of 64 and the cube root of 64."
- N, 답 1: "To solve the problem of finding the difference between the positive square root of 64 and the cube root of 64, let's break it down step by step."
- N, 답 2: "First, let's find the positive square root of 64."

읽은 점:

- 네 답 모두 맞았습니다. 길이는 T가 N의 3배쯤입니다.
- T는 생각 형식으로 시작하고, N은 원래 모델처럼 바로 풀이로 들어갑니다.
- 채점은 마지막 `\boxed{}` 안의 답을 공식 채점 함수로 정답과 비교합니다.

## 무엇을 했나

| 실험 | 바꾼 것 | 기준 | 규모 |
|---|---|---|---|
| 공개 모델 스모크 | Bespoke-Stratos-7B의 시스템 프롬프트를 T, N, D로. 원래 모델에도 T와 N을 넣음 | 같은 모델의 T, 원래 모델의 N | MATH500 100문항 × 2회, AIME25 30 × 2회, GSM8K 100문항 × 1회. 조건 하나에 360답 |
| 크기 맞춤 | 저장된 표준 SFT 답을 위와 같은 문항, 같은 횟수, 같은 최대 길이로 다시 계산 | 표준 SFT의 기본 문장 | 새 생성 없음 |
| 문턱 분석 | 표준 SFT에 넣어 본 조건 18개(시스템 프롬프트 문장 12개, 시작 위치에 방향을 더한 조건 6개)를 한 식으로 맞춤 | | MATH500 100문항, 조건마다 200–400답. 새 생성 없음 |

- 생성 설정: temperature 0.6, top_p 1.0, 최대 16,384 tokens(앞선 실험은 32,000).
- 문턱 분석의 식: 조건마다 "긴 풀이로 들어갈 확률"을 문항의 성향 하나와 조건의 값 둘(문턱 b, 난도 민감도 s)로 맞춥니다. 문항의 성향은 그 조건을 뺀 나머지 조건에서 그 문항이 얼마나 자주 긴 풀이로 갔는지로 잽니다.
- 판정 기준은 결과를 보기 전에 연구 기록에 적었습니다. 다만 문턱 분석은 기준을 코드에 먼저 적어 두었고, 연구 기록에는 실행 뒤에 옮겼습니다(기록 명령의 오류 때문이며 기준은 바꾸지 않았습니다).

## 결과

### 1. 공개 모델: 학습 프롬프트를 빼면

| 벤치마크 | 조건 | 평균 tokens | 생각 형식 | Long-CoT | ACC |
|---|---|---|---|---|---|
| GSM8K | T | 1,552 | 100% | 66.0% | 96.0% |
| | N | 610 | 0% | 9.0% | 90.0% |
| | D | 405 | 0% | 7.0% | 92.0% |
| MATH500 | T | 4,307 | 100% | 88.0% | 84.0% |
| | N | 2,183 | 0% | 17.5% | 79.5% |
| | D | 1,856 | 0% | 21.5% | 88.0% |
| AIME25 | T | 13,298 | 100% | 100% | 16.7% |
| | N | 6,834 | 0% | 46.7% | 15.0% |
| | D | 7,321 | 0% | 58.3% | 11.7% |

| 벤치마크 | 토큰 비 N ÷ T [95% CI] | ACC 차 [95% CI] |
|---|---|---|
| GSM8K | 0.30 [0.26, 0.35] | −6.0 [−11.0, −2.0]%p |
| MATH500 | 0.33 [0.29, 0.38] | −4.5 [−9.5, +0.5]%p |
| AIME25 | 0.40 [0.30, 0.52] | −1.7 [−13.3, +11.7]%p |

**표 읽는 법.** MATH500 행의 0.33은 학습 프롬프트를 빼면 길이가 33%가 됐다는 뜻입니다. ACC 차 −4.5 [−9.5, +0.5]%p는 정답률이 4.5%p 낮았지만 범위가 0을 조금 넘어, 낮다고 단정하기는 이르다는 뜻입니다. GSM8K는 범위 전체가 0보다 낮아 낮아졌다고 말할 수 있습니다.

- T의 답 360개는 모두 `<|begin_of_thought|>`로 시작했습니다. N의 답 360개는 하나도 그렇지 않았고, 첫 낱말은 "To" 257개, "First," 44개, "Given" 20개, "Let's" 16개 순이었습니다.
- 형식은 완전히 사라졌지만, 낱말로 판별한 Long-CoT 비율은 N에서도 어려울수록 높았습니다(GSM8K 9%, MATH500 17.5%, AIME25 46.7%).
- 대화 틀 기본 문장만 있을 때(D)도 생각 형식은 0%였습니다. T와 비교한 길이는 0.29, 0.34, 0.47배입니다. MATH500 정답률은 88.0%로 T보다 낮지 않았습니다(차 +4.0 [−1.0, +9.0]%p). 이 모델을 시스템 프롬프트 없이 그냥 부르면 D가 됩니다.

### 원래 모델과 비교하면

| 모델 | 조건 | GSM8K tokens, ACC | MATH500 tokens, ACC | AIME25 tokens, ACC |
|---|---|---|---|---|
| Bespoke-Stratos-7B | T | 1,552, 96.0% | 4,307, 84.0% | 13,298, 16.7% |
| Bespoke-Stratos-7B | N | 610, 90.0% | 2,183, 79.5% | 6,834, 15.0% |
| 원래 모델 | N | 289, 88.0% | 509, 82.0% | 907, 5.0% |
| 원래 모델 | T | 333, 87.0% | 554, 75.5% | 914, 8.3% |

| 문항별 길이 비 [95% CI] | GSM8K | MATH500 | AIME25 |
|---|---|---|---|
| 공개 모델 N ÷ 원래 모델 N | 1.30 [1.15, 1.50] | 2.17 [1.82, 2.59] | 5.82 [4.25, 7.71] |
| 공개 모델 T ÷ 원래 모델 N | 4.38 [3.94, 4.93] | 6.52 [5.79, 7.45] | 14.60 [12.47, 16.90] |
| 프롬프트 없이 남는 비율 | 0.18 | 0.41 | 0.66 |

**표 읽는 법.** 둘째 표의 첫 행은 프롬프트를 뺀 공개 모델의 답이 원래 모델의 답보다 몇 배 긴지입니다. 셋째 행은 파인튜닝으로 늘어난 길이 가운데 프롬프트 없이도 남는 몫입니다(로그로 잰 비). 0이면 원래 모델과 같고, 1이면 프롬프트가 있을 때와 같습니다.

- 원래 모델에 학습 프롬프트만 넣으면 길이가 거의 그대로입니다(MATH500 554 tokens). 형식 표지는 12–27%에서만 나왔습니다. 긴 풀이는 지시문을 따라서 나오는 것이 아니라 파인튜닝이 만든 것입니다.
- 프롬프트를 뺀 공개 모델은 원래 모델과 같지 않습니다. 형식은 전부 꺼지지만 답은 더 길고, 어려울수록 더 깁니다. 남는 비율이 0.18(GSM8K), 0.41(MATH500), 0.66(AIME25)으로 올라갑니다.
- AIME25 정답률은 프롬프트를 뺀 공개 모델이 15.0%, 원래 모델이 5.0%입니다(차 +10.0 [0.0, +21.7]%p, 60답이라 범위가 넓음).

### 사용자 칸의 상자 문장까지 빼면

이 공개 모델은 학습 때 사용자 칸에도 늘 "Return your final response within \boxed{}."가 있었습니다. 시스템 프롬프트와 이 문장을 모두 빼고 문제만 넣었습니다.

| 벤치마크 | 평균 tokens | 생각 형식 | ACC | 길이 (T 대비) | 길이 (원래 모델 대비) |
|---|---|---|---|---|---|
| GSM8K | 473 | 0% | 79.0% | 0.24 [0.21, 0.28] | 1.07 |
| MATH500 | 1,386 | 0% | 81.5% | 0.27 [0.24, 0.30] | 1.74 |
| AIME25 | 4,316 | 0% | 16.7% | 0.25 [0.20, 0.32] | 3.71 |

- 상자 문장도 학습 때의 단서였습니다. 빼면 더 짧아집니다(MATH500 2,183 → 1,386 tokens).
- 학습 때의 단서를 모두 빼도 원래 모델과 같아지지는 않습니다. GSM8K는 거의 같고(1.07배), MATH500은 1.74배, AIME25는 3.71배로 어려울수록 긴 풀이가 남습니다.
- AIME25 정답률은 16.7%로 학습 프롬프트를 쓴 칸과 같고 길이는 4분의 1입니다(60답이라 범위가 넓음).
- GSM8K 정답률 79.0%는 답 상자가 없는 답 12%를 오답으로 센 값입니다.
- 뒤에 추가: 위 표의 "길이 (T 대비)"는 상자 문장이 있는 T 칸과 견준 값입니다. 상자 문장을 뺀 입력에 학습 프롬프트만 넣은 칸이 끝나, 같은 입력 형식끼리 다시 견줬습니다. 길이는 0.32 [0.29, 0.37](GSM8K), 0.29 [0.25, 0.32](MATH500), 0.29 [0.22, 0.39](AIME25)배이고 생각 형식은 100%에서 0%가 됩니다. 판정은 같습니다("묶임", "완전 차단"). MATH500 정답률은 82.0%에서 81.5%로 같았습니다.

### 2. 표준 SFT와 나란히 (같은 크기로 다시 계산)

| 모델 (학습 자료) | 시스템 프롬프트를 빼면 긴 풀이로 시작하는 비율 (MATH500) | 토큰 비 GSM8K, MATH500, AIME25 | MATH500 ACC 차 |
|---|---|---|---|
| 표준 SFT (817문항) | 100% → 45.5% | 0.65, 0.58, 0.86 | −0.5%p |
| Bespoke-Stratos-7B (약 1만 7천 개) | 100% → 0% | 0.30, 0.33, 0.40 | −4.5%p |

같은 식으로 MATH500에서 "프롬프트 없이 남는 비율"을 구하면 표준 SFT는 0.70, 공개 모델은 0.41입니다. 프롬프트가 있을 때의 길이는 두 모델이 비슷합니다(원래 모델의 6.4배, 6.5배).

- 두 모델 모두 긴 풀이가 학습 때의 시스템 프롬프트에 묶여 있습니다.
- 묶인 정도는 다릅니다. 표준 SFT는 프롬프트를 빼도 절반쯤은 길게 풀고, 어려울수록 더 길게 풉니다(AIME25 0.86배). 공개 모델은 형식이 전부 꺼지고 난도에 따른 차이가 작습니다.
- 이 차이가 어디서 오는지는 여기서 말할 수 없습니다. 학습 프롬프트의 종류, 학습 자료의 크기, 응답 형식이 함께 다릅니다.
- 표준 SFT의 값은 크기를 줄여도 그대로였습니다(전체 크기에서는 0.67, 0.60, 0.82–0.83).

### 3. 문턱 분석 (표준 SFT, 조건 18개)

| 묶음 | 조건 | 긴 풀이 비율 | 문턱 b | 난도 민감도 s |
|---|---|---|---|---|
| 꺼진 쪽 | 시스템 프롬프트 없음(두 번), 무관한 문장, 무관한 방향, 7층 방향 | 47.5–58.5% | −0.14 – +0.49 | 1.29–1.74 |
| 켜진 쪽 | 기본, 같은 뜻, 낱말 섞기, 부정, 한국어, 간결, 짧게, 조건부, 14층 방향 1배와 2배, 21층 방향 | 82.0–91.5% | +2.02 – +3.23 | 0.87–1.59 |

**표 읽는 법.** 문턱 b가 클수록 쉬운 문항까지 긴 풀이로 들어갑니다. 난도 민감도 s는 문항이 어려워질 때 긴 풀이로 가는 확률이 얼마나 빨리 오르는지입니다.

- 조건들은 두 묶음으로 갈렸고, 그 사이(b가 1쯤)에 놓인 조건은 없었습니다. 난도 민감도는 두 묶음이 비슷했습니다.
- 간결 문장은 켜진 쪽입니다(긴 풀이 82%). 길이가 0.67배로 준 것은 긴 풀이 안에서 짧게 쓴 결과입니다. 시스템 프롬프트를 뺐을 때(0.54–0.61배)는 문턱이 내려가 문항 절반이 짧은 풀이로 간 결과입니다. 길이가 주는 길이 서로 다릅니다.
- 미리 정한 규칙으로는 "난도 민감도가 조건마다 다름"으로 판정됐습니다. 어긋난 칸은 중국어 문장(중국어로 쓴 답의 긴 풀이를 판별 규칙이 못 잡음)과 답만 쓰라는 문장(512 tokens 과제)입니다. 위의 "두 묶음, 민감도 비슷"은 이 두 칸을 뺀 사후 읽기입니다.

### 둘째 공개 모델 OpenThinker-7B: 시스템 프롬프트만 빼면 꺼지지 않았다 (같은 날 추가)

OpenThinker-7B는 같은 기반 모델을 같은 시스템 프롬프트와 같은 생각 형식으로 학습한 공개 모델입니다. 학습 자료가 더 큽니다(모델과 함께 올라온 학습 기록 기준으로 3에폭에 갱신 3,561회, Bespoke-Stratos-7B는 3에폭에 522회). 조건, 문항, 최대 길이는 위와 같습니다.

| 벤치마크 | 조건 | 평균 tokens | 생각 형식 | 긴 풀이 비율 | ACC | 토큰 비 N ÷ T [95% 범위] |
|---|---|---|---|---|---|---|
| GSM8K 100 × 1 | T | 1,703 | 100% | 77.0% | 83.0% | |
| | N | 1,370 | 100% | 52.0% | 66.0% | 0.77 [0.71, 0.85] |
| MATH500 100 × 2 | T | 4,309 | 100% | 91.5% | 83.0% | |
| | N | 3,962 | 97% | 85.5% | 81.5% | 0.89 [0.82, 0.96] |
| AIME25 30 × 2 | T | 12,420 | 100% | 100% | 23.3% | |
| | N | 12,073 | 95% | 100% | 23.3% | 0.94 [0.82, 1.09] |

**표 읽는 법.** T는 학습 때의 시스템 프롬프트를 넣은 조건, N은 뺀 조건입니다. 생각 형식은 답이 `<|begin_of_thought|>` 형식으로 쓰인 비율입니다. 토큰 비는 문항마다 낸 비의 기하 평균입니다.

- **프롬프트를 빼도 생각 형식이 95–100% 남습니다.** Bespoke-Stratos-7B에서는 100%에서 0%가 됐던 값입니다. 길이도 0.77–0.94배로 조금만 줄었습니다.
- 미리 정한 기준으로는 "묶임"도 "묶이지 않음"도 아닌 **"중간"**입니다. MATH500 토큰 비 0.89는 "묶이지 않음"의 문턱 0.90 바로 아래이고, 생각 형식은 3%p만 줄었습니다. 난도 쪽 판정은 "난도와 무관하거나 약함"입니다.
- GSM8K에서는 프롬프트를 빼자 정답률이 83.0%에서 66.0%로 내려갔습니다(−17 [−27, −7]%p). 답 상자가 있는 답이 87%에서 71%로 준 것과 함께 봐야 합니다. MATH500(−1.5 [−7.0, +4.0]%p)과 AIME25(0.0 [−6.7, +6.7]%p)는 구간이 0을 포함합니다.
- 틀의 기본 문장만 넣은 조건도 N과 비슷합니다(토큰 비 GSM8K 0.80, MATH500 0.91, AIME25 1.00, 생각 형식 100%).
- 여기까지만 보면 "공개 모델도 학습 프롬프트를 빼면 꺼진다"는 두 모델 가운데 하나에서만 맞습니다. 다만 이 조건에는 사용자 칸의 고정 문장("Return your final response within \boxed{}.")이 남아 있었습니다. 그 문장까지 뺀 결과가 바로 아래 절입니다.

### 고정 문장까지 빼자 둘째 모델도 꺼졌다 (11월 24일 오후)

두 공개 모델은 학습 때 사용자 칸의 문제 앞에 늘 같은 문장("Return your final response within \boxed{}.")이 붙어 있었습니다. 시스템 프롬프트와 이 고정 문장을 각각 넣고 빼서 네 칸을 만들었습니다. 문항과 설정은 위와 같습니다.

**표 읽는 법.** 값은 답이 생각 형식(`<|begin_of_thought|>`)으로 시작한 비율이고, 차례로 GSM8K, MATH500, AIME25입니다. 가로는 시스템 프롬프트, 세로는 고정 문장입니다.

| 모델 | 고정 문장 | 시스템 프롬프트 있음 | 시스템 프롬프트 없음 |
|---|---|---|---|
| Bespoke-Stratos-7B | 있음 | 100%, 100%, 100% | 0%, 0%, 0% |
| | 없음 | 100%, 100%, 100% | 0%, 0%, 0% |
| OpenThinker-7B | 있음 | 100%, 100%, 100% | 100%, 97%, 95% |
| | 없음 | 100%, 100%, 100% | **0%, 0.5%, 0%** |

- **OpenThinker-7B도 두 단서를 모두 빼면 생각 형식이 꺼집니다.** 고정 문장만 남겼을 때 95–100%였던 값이 0%, 0.5%, 0%가 됐습니다.
- 고정 문장 없이 시스템 프롬프트만 넣으면 100%입니다. 실행 전에 적어 둔 예측(90% 이상)대로입니다. 이 모델은 두 단서 가운데 **하나만 있어도 켜지고**, Bespoke-Stratos-7B는 **시스템 프롬프트가 있어야만** 켜집니다.
- 같은 형식끼리(고정 문장이 없는 두 칸) 견준 미리 정한 판정은 **"묶임"**, **"완전 차단"**입니다. 길이는 시스템 프롬프트만 있는 칸의 0.36배 [0.30, 0.46](GSM8K), 0.40배 [0.34, 0.48](MATH500), 0.54배 [0.43, 0.66](AIME25)입니다.
- 정답률은 이 크기로 판정할 수 없습니다. MATH500은 83.5%에서 82.0%로 차 −1.5 [−8.5, +5.5]%p입니다. GSM8K는 68.0%에서 79.0%로 오히려 높게 나왔는데, 시스템 프롬프트만 있는 칸에서 답 상자가 있는 답이 74%뿐이었던 것과 함께 봐야 합니다.
- 단서를 모두 빼도 원래 모델과 같아지지는 않습니다. 파인튜닝으로 늘어난 길이 가운데 남는 몫은 0.34 [0.21, 0.47](GSM8K), 0.53 [0.44, 0.62](MATH500), 0.75 [0.66, 0.84](AIME25)로 어려운 벤치마크일수록 큽니다(Bespoke-Stratos-7B는 0.05, 0.31, 0.51). 이 값은 판정 없이 적는 보조 값입니다. 원래 모델에는 고정 문장이 없는 칸을 돌리지 않아, 원래 모델 쪽은 고정 문장이 있는 칸을 기준으로 썼습니다.
- 두 모델에서 묶인 단서가 왜 다른지는 가릴 수 없습니다. 학습 자료(약 1만 7천 행 대 약 11만 4천 행)와 갱신 횟수(522회 대 3,561회)가 함께 다르고 모델이 둘뿐입니다.

## 미리 정한 기준으로는

| 실험 | 기준 | 결과 |
|---|---|---|
| 공개 모델, 묶임 | MATH500 토큰 비 0.70 이하이고 생각 형식이 30%p 이상 줄면 "묶임" | 0.33, 100% → 0%로 **묶임** |
| 공개 모델, 난도 | N에서 생각 형식이 세 벤치마크 모두 5% 이하면 "완전 차단", AIME25가 GSM8K보다 20%p 이상 높으면 "어려울수록 켜짐" | 모두 0%라 **완전 차단** |
| 둘째 공개 모델(OpenThinker-7B), 묶임 | 위와 같음. 토큰 비 0.90 이상이고 10%p 미만으로 줄면 "묶이지 않음" | 0.89, 100% → 97%로 **중간** |
| 둘째 공개 모델, 난도 | 위와 같음 | N에서 100%, 97%, 95%라 **난도와 무관하거나 약함** |
| 둘째 공개 모델, 두 단서를 모두 뺌(같은 형식끼리) | 묶임과 난도 기준은 위와 같음 | 0.40, 100% → 0.5%로 **묶임**, 세 벤치마크 모두 5% 이하라 **완전 차단** |
| 둘째 공개 모델, 시스템 프롬프트만 넣음 | 실행 전 예측: 생각 형식 90% 이상이면 "두 단서 가운데 하나만 있어도 켜짐" | 100%로 **예측대로** |
| 문턱 분석 | 맞춘 조건들의 난도 민감도 범위가 모두 겹치면 "문턱만 움직임" | **난도 민감도가 조건마다 다름**(어긋난 칸은 측정 한계가 있는 두 칸) |

## 이 결과로 말할 수 있는 것과 없는 것

**말할 수 있는 것**

- 따로 학습해 공개된 긴 추론 모델 하나에서도, 긴 풀이의 형식은 학습 때 쓴 시스템 프롬프트에 묶여 있습니다. 빼면 생각 형식이 전부 사라지고 길이가 0.30–0.40배가 됩니다.
- 그 긴 풀이는 지시문을 따른 결과가 아닙니다. 원래 모델에 같은 프롬프트를 넣어도 길어지지 않습니다.
- 프롬프트를 빼도 원래 모델로 돌아가지는 않습니다. 어려운 문제일수록 긴 풀이가 더 많이 남습니다.
- 표준 SFT에서 간결 문장과 시스템 프롬프트 제거는 길이를 줄이는 방식이 다릅니다.
- 둘째 공개 모델(OpenThinker-7B)도 학습 때의 입력 단서를 모두 빼면 생각 형식이 꺼집니다. 본 두 모델 모두에서 긴 풀이 형식은 학습 때의 입력 단서에 묶여 있었습니다. 다만 무엇이 단서가 되는지는 모델마다 달랐습니다.

**아직 말할 수 없는 것**

- 두 모델에서 남는 비율이 다른 이유(학습 프롬프트, 자료 크기, 형식이 함께 다름).
- 프롬프트를 뺀 답의 정답률이 원래 모델보다 높은지(MATH500과 GSM8K는 범위가 0을 포함).
- 두 공개 모델에서 묶인 단서가 왜 다른지(학습 자료와 학습량이 함께 다르고 모델이 둘뿐임).
- 크기나 계열이 다른 공개 모델에서도 같은지(본 두 모델은 모두 Qwen2.5-7B 기반이고 학습 프롬프트가 같음).

## 선행 연구와의 관계

| 이번 실험 | 가장 가까운 자료 | 이번에 다른 점 |
|---|---|---|
| 공개 모델에서 학습 프롬프트 빼기 | Sky-T1과 s1의 GitHub 이슈에 "시스템 프롬프트가 없으면 생각 형식이 안 나온다", "다른 시스템 프롬프트면 정답률이 원래 모델 수준"이라는 사용자 보고가 있음. OpenThoughts 논문(2506.04178) 부록은 정확도만 비교 | 길이, 난도, 정답률을 같은 조건으로 재고, 직접 학습한 모델과 같은 크기로 나란히 놓음. 이 관찰 자체는 처음이 아님 |
| QFFT와의 연결 | QFFT(2506.12860)는 학습 때 질문, 시스템 프롬프트, 대화 표지를 함께 지움 | 시스템 프롬프트만 따로 본 연구는 찾지 못함 |
| OpenThinker-7B의 엇갈린 보고 | 모델 토론 게시판에 "다른 추론 프로그램으로 쓰면 추론이 시작되지 않는다"는 사용자 보고와 "시스템 프롬프트 없이도 추론한다"는 관리자 답이 함께 있음 | 이 글의 2×2가 둘을 함께 설명함. 시스템 프롬프트와 고정 문장이 둘 다 없을 때만 꺼지고 하나라도 있으면 켜짐 |
| 다른 계열의 증류 모델 | R1 증류 모델에서 권장 문장이 없으면 생각이 짧은 형식이 된다는 학회 제출작이 있음(초록만 확인, 본문은 열지 못함) | 대상 모델과 조작이 다름. 본문을 확인하면 고쳐 적음 |
| 문턱 분석 | 벡터 세기에 따른 반응 곡선(Fractional Reasoning 2506.15882, Controlling Thinking Speed 2507.03704), 첫 토큰이 길이를 정함(Beyond the Opening 2610.34350) | 긴 풀이 선택을 문항 성향과 조건의 문턱으로 맞춘 연구는 찾지 못함 |

## 한계

- 공개 모델은 둘이고, 문항당 1–2회입니다.
- 최대 길이가 16,384 tokens입니다. AIME25는 T에서 답의 53%가 상한에 걸려, 길이 비교로만 읽습니다.
- 공개 모델의 학습 설정은 모델 카드와 학습 자료로만 확인했습니다.
- 공개 모델은 사용자 칸의 "Return your final response within \boxed{}."도 학습 때 늘 있던 문장입니다. 이 문장까지 뺀 조건은 위 "고정 문장까지 빼자 둘째 모델도 꺼졌다" 절에 있습니다.
- 직접 학습한 모델과 공개 모델은 학습 자료의 크기가 다릅니다(817 대 약 1만 7천). 두 모델의 차이를 학습 프롬프트 때문이라고 읽으면 안 됩니다.
- "프롬프트 없이 남는 비율"은 결과를 본 뒤에 만든 지표입니다. 원래 모델의 길이는 문항당 1–2회로 쟀습니다.
- 문턱 분석은 모델 하나, 100문항이고, 문항의 성향을 같은 자료에서 잽니다.

## 다음

1. 공개 모델의 남은 조건은 모두 끝났습니다. 고정 문장까지 뺀 입력은 위에 있고, 시작 위치에 방향 하나만 더한 실험은 [설계 글](2026-11-24-c-plan-and-replan.html)의 실험 5에 있습니다(생각 형식은 돌아오지 않음). 다음은 크기가 다른 공개 모델(32B)입니다. 모델을 새로 받아야 해서 아직 정하지 않았습니다.
2. 시작 위치 방향을 0.25, 0.5, 0.75배로 넣어 문턱이 두 묶음 사이로 연속해서 움직이는지 봅니다.
3. 시스템 프롬프트 문장 32개의 시작 상태를 한 방향 위에 놓고, 아직 생성해 보지 않은 문장의 결과를 미리 맞히는지 시험합니다.
4. 학습 자료의 크기를 맞춘 비교는 같은 자료로 시스템 프롬프트만 바꿔 직접 학습해야 합니다.

## 일지에서의 실험 번호

공개 모델 스모크 = 공개 모델 학습 프롬프트 묶임 스모크, 문턱 분석 = 문턱 분석 (11월 24일).
