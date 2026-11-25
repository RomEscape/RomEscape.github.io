---
title: 연구 질문으로 다시 쓴 QFFT 연구, 어떤 현상을 보고 무엇이 궁금해서 무엇을 했나
date: 2026-11-25
project: QFFT
status: 진행 중
summary: 지금까지의 QFFT 연구를 실험 순서가 아니라 질문 순서로 다시 적었습니다. 질문마다 본 현상, 든 의문, 그때까지 안 해 본 것, 그래서 한 실험, 답, 다음 의문을 적었고 질문 열 개가 한 줄로 이어집니다. 함께 실험 글 82편이 실제로 그 순서로 진행됐는지 한 편씩 점검했습니다.
published: true
---

## 한 줄 요약

- 지금까지의 QFFT 연구를 실험 순서가 아니라 **질문 순서**로 다시 적었습니다. 질문마다 "본 현상 → 든 의문 → 그때까지 안 해 본 것 → 그래서 한 것 → 답 → 다음 의문"을 적었습니다.
- 큰 질문은 하나입니다. **긴 풀이를 배운 모델은 왜 쉬운 문제에도 길게 푸는가, 그리고 QFFT는 무엇을 바꿨기에 그러지 않는가.** 구체적으로는 "평가 입력에서 문제를 감싸고 있는 시스템 프롬프트와 프롬프트 템플릿이 답 길이에 영향을 주는가, 준다면 왜 주는가, 그 부분을 빼면 새로 학습하지 않고도 QFFT, A2와 같은 길이와 정답률이 되는가"를 묻습니다.
- 지금의 답은 이렇습니다. 모델은 길게 푸는 방식을, 학습 때 그 풀이와 늘 함께 있던 입력(풀이를 서술하는 지시문)에 의존해 켭니다. 표준 평가는 모든 모델에 같은 지시문을 주는데, 그 지시문은 SFT에게만 학습 때 본 것입니다. QFFT가 짧게 푸는 것의 큰 부분은 "질문을 지워서"보다 "긴 풀이가 그 지시문에 의존하지 않아서"로 설명됩니다.
- 이 답에는 빈 곳이 있습니다. 어려운 문제(AIME25)에서는 그 입력을 빼면 정답률이 내려가는 방향이고, 왜 풀이를 서술하는 지시문에만 의존이 생기는지는 아직 모릅니다. 열려 있는 질문 다섯 개와 각각에 답할 실험을 아래에 적었습니다.
- 함께, 홈페이지의 QFFT 실험 글 82편이 실제로 이 순서로 진행됐는지 한 편씩 점검했습니다. 관찰에서 나온 의문으로 시작한 글은 39편, 후보 목록이나 떠오른 생각에서 시작한 글은 28편이었습니다. 지금 남아 있는 결과는 모두 앞쪽에서 나왔고, 뒤쪽 28편은 그 자체로 방법이 된 것이 없었습니다.

## 이 글을 쓴 까닭

실험 글이 82편으로 늘면서 "무엇을 했고 수치가 얼마였다"는 있는데 "왜 그 실험을 했는가"는 한눈에 보이지 않게 됐습니다. 11월 25일 연구 회의에서 받은 지적은 이렇습니다. 실험과 숫자의 나열이 아니라, 어떤 현상을 보고 무엇이 이상해서 그 실험을 설계했는지가 보여야 한다는 것입니다. 연구 질문은 이런 순서로 잡습니다.

1. 이런 현상이 있었다(본 현상).
2. 왜 이런 일이 일어났는가(든 의문).
3. 생각해 보니 이렇게 해 본 적이 없었다. 왜 안 해 봤는가(그때까지 안 해 본 것).
4. 이렇게 하면 알 수 있겠다(그래서 한 것).
5. 결과가 의문에 무엇을 답했고, 무엇이 새로 이상한가(답, 다음 의문).

그래서 두 가지를 했습니다.

- 연구 전체를 이 순서로 다시 적었습니다(아래 "질문의 사슬").
- 실험 글 82편을 다시 읽어, 출발점이 "우리 자료에서 본 현상"이었는지 "후보 목록이나 떠오른 생각"이었는지 가렸습니다(아래 "점검").

새 실험은 없습니다. 수치는 모두 앞선 글에 있는 값이고, 질문마다 자세한 기록으로 가는 링크를 달았습니다.

## 용어 풀이

| 용어 | 뜻 | 이 글에서의 예 |
|---|---|---|
| Base | 파인튜닝하기 전의 모델(Qwen2.5-7B-Instruct) | MATH500 문항 하나에 평균 635 tokens |
| SFT | 어려운 수학 문제 817개와 긴 풀이(LIMO 자료)로 평범하게 파인튜닝한 모델 | MATH500 문항 하나에 평균 6,576 tokens |
| QFFT | 학습 자료에서 질문을 지우고 풀이만으로 파인튜닝한 모델(Question-Free Fine-Tuning) | 평균 4,630 tokens |
| A1 | 질문은 지우고 시스템 프롬프트는 남겨 학습한 모델 | 질문을 지웠는데도 SFT만큼 길게 풂 |
| 표준 입력 | 평가 때 모든 모델에 똑같이 주는 입력. 프롬프트 템플릿, 시스템 프롬프트, 질문으로 이루어짐 | 시스템 프롬프트는 "Please reason step by step, and put your final answer within \boxed{}." |
| 지시문 S | 위 시스템 프롬프트 문장. SFT가 학습 때도 본 문장 | 풀이 방식을 서술하는 지시문 |
| 단서 | 학습 때 긴 풀이와 늘 함께 있던 입력 요소 | SFT에게는 지시문 S와 프롬프트 템플릿 |
| 의존한다 | 그 입력 요소가 있을 때만 그 행동이 나온다는 뜻. 앞선 글에서는 "묶인다"로 적었습니다 | SFT의 긴 풀이는 S에 의존해, S를 빼면 쉬운 문제를 짧게 풂 |
| Long-CoT 비율 | 되짚는 표현(wait 등)이 여러 번 나오는 긴 풀이로 쓴 답의 비율. QFFT 논문의 분석 코드 기준 | SFT 91.4%, QFFT 44.1% (MATH500) |
| 남는 비율 | 파인튜닝으로 늘어난 길이 가운데 그 조건에서 남아 있는 몫. 0이면 Base와 같은 길이, 1이면 SFT의 표준 입력과 같은 길이 | SFT에 문제 글만 주면 GSM8K 0.08, AIME25 0.87 |
| 최대 길이 | 답 하나에 허용한 tokens의 한도. 한도까지 쓰고도 끝나지 않은 답은 오답으로 셈 | 공개 모델 시험 16,384, 직접 학습한 모델 시험 32,000 |
| 끝내지 못한 답 | 최종 답을 쓰고도 생성을 끝내지 못해 최대 길이까지 간 답 | 정답 9를 쓴 뒤 같은 줄을 16,384 tokens까지 되풀이 |
| 문단 첫머리 | 답 안에서 빈 줄 바로 다음 자리 | SFT의 답에서는 약 45 tokens마다 한 번 |
| 스모크 | 작은 크기로 먼저 돌려 보는 점검 실험 | 8문항을 8번씩 |

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
| 방법 (SPFI) | SFT | 시스템 프롬프트 제거 | 91.0 | 1,517 | 80.9 | 4,899 | 19.2 | 18,382 |
| 방법 (QOI) | SFT | 문제 글만 | 대기 | 대기 | 81.4 | 4,221 | 대기 | 대기 |
| 참고 | A1 | 시스템 프롬프트 제거 | 91.5 | 587 | 81.6 | 3,778 | 12.5 | 16,270 |
| 참고 | A2 | 시스템 프롬프트 제거 | 91.6 | 514 | 82.0 | 3,948 | 값 없음 | 값 없음 |
| 참고 | QFFT | 시스템 프롬프트 제거 | 91.3 | 630 | 82.5 | 4,122 | 값 없음 | 값 없음 |
| 참고 | QFFT | 문제 글만 | 대기 | 대기 | 77.5 | 5,046 | 대기 | 대기 |

- **모델.** Base는 파인튜닝 전의 Qwen2.5-7B-Instruct입니다. 나머지는 모두 LIMO 817문항으로 학습했습니다. SFT는 QFFT 논문이 비교 기준으로 쓴 표준 SFT로, 시스템 프롬프트와 질문, 긴 풀이를 그대로 학습한 모델입니다. A1은 질문을 지우고, A2는 질문을 지우고 응답 첫 토큰의 loss까지 빼고, QFFT는 논문 방법대로 질문 없이 풀이만으로 학습한 모델입니다.
- **무엇을 견주는가.** A2와 QFFT는 학습 방법을 바꿔 새로 학습한 모델입니다. 방법 줄은 표준 SFT의 가중치를 그대로 두고 추론 입력만 바꾼 것입니다. A2나 QFFT 위에 얹은 것이 아니라, A2, QFFT와 나란히 견주는 다른 길입니다. 같은 입력 변경을 A1, A2, QFFT에 얹어 본 값은 참고 줄에 따로 두었습니다.
- **추론 입력.** 기본 프롬프트는 프롬프트 템플릿, 시스템 프롬프트 "Please reason step by step, and put your final answer within \boxed{}.", 질문으로 이루어집니다. 시스템 프롬프트 제거는 거기서 시스템 프롬프트만 뺀 입력이고, 문제 글만은 프롬프트 템플릿까지 빼고 질문 글자만 준 입력입니다. 실제 문자열은 아래 "실제 입력과 실제 답"에 있습니다.
- **크기.** GSM8K 1,319문항, MATH500 500문항, AIME25 30문항입니다. 기본 프롬프트 줄은 문항마다 16회, 나머지 줄은 4회 풀게 했습니다. 최대 32,000 tokens입니다.
- **채점.** GSM8K와 MATH500의 ACC는 `\boxed{}` 없이 끝난 답을 직접 읽어 반영하고, 표기만 다른 같은 답을 맞게 고친 값입니다(GSM8K는 평가 자료의 정답 16문항도 바로잡았습니다). AIME25는 공식 채점 스크립트 값 그대로입니다.
- **읽기.** MATH500에서 표준 SFT에 문제 글만 준 줄(QOI)은 ACC 81.4%, 4,221 tokens입니다. A2(81.3%, 4,587)와 QFFT(81.4%, 4,630)와 정답률이 같고 8–9% 짧습니다. GSM8K와 AIME25의 같은 칸은 아직 돌지 않았습니다. 참고 줄을 보면 A2와 QFFT도 시스템 프롬프트를 빼면 더 짧아집니다(3,948, 4,122 tokens).

<!-- qfft-main-table-end -->

## 큰 질문은 어떤 현상에서 나왔나

**본 현상.** 긴 풀이로 SFT한 모델은 쉬운 문제에도 길게 풉니다. MATH500에서 Base는 문항 하나에 평균 635 tokens를 쓰는데 SFT는 6,576 tokens를 씁니다. 가장 쉬운 수준의 문항 "2^8 = 4^x에서 x는?"에 Base는 평균 222 tokens, SFT는 886 tokens를 썼고 답은 같습니다(아래 "실제 입력과 실제 답").

**QFFT 논문의 설명.** 학습 자료에서 질문을 지우고 풀이만으로 학습하면 쉬운 문제는 짧게, 어려운 문제는 길게 풉니다. 질문을 보고 곧바로 긴 풀이로 가는 연결을 배우지 않기 때문이라고 설명합니다.

**한 가지 더 본 것.** 평가 때 모델에 넣는 입력은 문제만이 아닙니다. 프롬프트 템플릿(`<|im_start|>system`, `<|im_start|>user` 같은 역할 표시)과 시스템 프롬프트("Please reason step by step, and put your final answer within \boxed{}.")가 문제를 감싸고 있습니다. 표준 SFT는 학습 때도 바로 이 템플릿과 시스템 프롬프트를 긴 풀이와 함께 봤고, QFFT는 학습 때 둘 다 본 적이 없습니다.

**든 의문.** 정말 질문을 지운 것이 원인인가. 구체적으로는 이렇게 묻습니다.

1. 표준 SFT가 길게 푸는 것은 문제 때문인가, 문제를 감싼 입력 때문인가. 시스템 프롬프트 문장이 답 길이에 영향을 주는가. 프롬프트 템플릿이 영향을 주는가.
2. 영향을 준다면 왜 주는가. 학습 때 그 부분이 긴 풀이와 함께 있었기 때문인가.
3. 그 부분을 평가 입력에서 빼면 정답률은 유지되는가. 유지된다면 QFFT나 A2처럼 새로 학습하지 않고 그 부분만 빼도 같은 길이와 정답률을 얻는 것 아닌가.
4. 공개 모델과 더 어려운 문제에서도 같은가.

아래 질문 3–5가 1번, 질문 8이 2번, 질문 9와 10이 3번과 4번에 답합니다.

## 실제 입력과 실제 답: 같은 문항 하나를 모델과 입력을 바꿔 가며

문항은 MATH500의 Level 1 문제 하나입니다(정답 4). 그림의 칸은 모델에 실제로 넣은 입력이고, 글상자는 저장된 실제 출력입니다.

<!-- xp-q77 -->
<figure class="xp"><p class="xp-t">같은 SFT, 입력에서 학습 때의 단서만 뺍니다 (MATH500 문항 77, 정답 4)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">If $2^8=4^x$, what is the value of $x$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">입력 ① 기본 프롬프트(표준 평가)</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">If $2^8=4^x$, what is the value of $x$?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">입력 ② 시스템 프롬프트 제거</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div></div><div class="xp-ctx"><div class="">If $2^8=4^x$, what is the value of $x$?</div></div><div class="xp-del"><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">입력 ③ 문제 글만</div></div></div><div class="xp-note"><b>바꾸는 것</b>추론 입력뿐입니다. ②는 시스템 프롬프트 칸을 뺐고, ③은 프롬프트 템플릿까지 빼고 문제 글자만 줍니다.<b>그대로 두는 것</b>모델의 가중치(다시 학습하지 않음), 문제, 온도 0.6, top_p 1, 최대 32,000 tokens<b>재는 것</b>같은 문제의 답 길이(tokens)와 정답 여부. ①은 16번, ②와 ③은 4번 풀게 했습니다.</div><div class="xp-cols" style="margin-top:14px"><div><p class="xp-name">SFT, 입력 ①: 16번 모두 정답, 525–2,018 tokens(평균 886)</p><pre class="xp-ex"><span class="xp-hit">Okay</span>, so I need to solve this equation: 2^8 = 4^x. Hmm, let me see. I know that both 2 and 4 are powers of 2. Wait, maybe I can rewrite 4 as 2 squared. Yeah, that makes sense. So 4 is 2^2. Therefore, 4^x would be (2^2)^x. I …
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
- 이 문항에서는 시스템 프롬프트만 뺀 입력 ②로도 SFT가 여전히 "Okay"로 시작해 길게 풀었습니다(평균 850 tokens). 프롬프트 템플릿까지 빼야 짧아졌습니다. 500문항 전체로는 입력 ②에서도 평균이 6,576에서 4,899 tokens로 줍니다(위 메인 표).

### 입력을 정확히 이렇게 바꿉니다

**표 읽는 법.** 한 줄이 모델 하나입니다. 가운데 두 칸이 평소 평가 입력에 들어가는 것과 바꾼 입력에 남기는 것이고, 오른쪽 칸이 뺀 것입니다. 모델의 가중치는 건드리지 않습니다.

| 모델 | 평소 평가 입력에 들어가는 것 | 바꾼 입력에 남기는 것 | 빼는 것 |
|---|---|---|---|
| 표준 SFT | 프롬프트 템플릿, 시스템 프롬프트 "Please reason step by step, and put your final answer within \boxed{}.", 문제 문장 | 문제 문장만 | 시스템 프롬프트 문장과 프롬프트 템플릿 전부(위 그림의 입력 ③) |
| 공개 모델 (Bespoke-Stratos-7B, OpenThinker-7B) | 프롬프트 템플릿, 그 모델이 학습 때 본 시스템 프롬프트(1,312자, "Your role as an assistant involves thoroughly exploring questions …"), 질문 앞의 고정 문장 "Return your final response within \boxed{}.", 문제 문장 | 프롬프트 템플릿와 문제 문장 | 시스템 프롬프트와 고정 문장 |

**무엇까지 빼야 충분한가.** 모델마다 다릅니다. 한 줄이 "모델 + 뺀 것" 하나입니다.

| 모델 | 뺀 것 | 결과 | 충분한가 |
|---|---|---|---|
| 표준 SFT | 시스템 프롬프트만(입력 ②) | MATH500에서 답이 평균 6,507 → 4,899 tokens(0.60배). 답 2,000개 가운데 974개(48.7%)는 여전히 "Okay"로 시작해 길게 풂 | 절반만 |
| 표준 SFT | 시스템 프롬프트와 프롬프트 템플릿(입력 ③) | 평균 6,576 → 4,221 tokens(0.44배). "Okay"로 시작하는 답은 2,000개 가운데 0개 | 충분 |
| Bespoke-Stratos-7B | 시스템 프롬프트만 | 생각 형식으로 시작하는 답이 360개 가운데 360개에서 0개로 | 충분 |
| OpenThinker-7B | 시스템 프롬프트만 | 생각 형식이 95–100% 그대로 남음 | 부족 |
| OpenThinker-7B | 시스템 프롬프트와 고정 문장 | 생각 형식 0–0.5% | 충분 |

- 무엇을 빼야 하는지는 그 모델의 학습 입력을 보면 정해집니다. 학습 때 긴 풀이와 늘 함께 있던 입력 요소를 모두 빼야 합니다. 하나라도 남으면 긴 풀이가 남을 수 있습니다(표준 SFT의 프롬프트 템플릿, OpenThinker-7B의 고정 문장).
- 정답률까지 지키려면 두 가지가 더 필요했습니다. 답을 `\boxed{}`에 넣게 하는 장치(그 지시가 함께 빠지므로)와, 처음 답을 쓴 곳에서 생성을 멈추는 규칙입니다([방법 정리 글](2026-11-24-h-drop-training-cues-method.html)의 "시험 ③ 넷째 결과").

## 질문의 사슬

**표 읽는 법.** 한 줄이 질문 하나입니다. "출발"은 그 질문이 실제로 어떻게 시작됐는지입니다. 아래에 질문마다 자세한 표가 있고, 그 표의 "다음 의문"이 다음 질문으로 이어집니다.

| 질문 | 때 | 답 한 줄 | 출발 |
|---|---|---|---|
| 1. QFFT의 효과는 질문을 지워서 생긴 것인가 | 9월 | 질문만 지운 모델은 SFT와 같았다. 응답 첫 토큰을 어떻게 배우는지가 길이를 정했다 | 재현에서 본 어긋남 |
| 2. 첫 토큰 밖에도 습관적으로 길어지는 자리가 있는가 | 10월 말–11월 8일 | 문제의 표기나 질문 끝 표현에서는 큰 편향이 없었다. 방법으로 이어진 것은 없다 | 후보 목록 |
| 3. 첫 토큰을 같게 맞춰도 SFT만 길다. 무엇 때문인가 | 11월 9일 | 시스템 프롬프트 때문이다. 없애면 네 모델이 같은 수준으로 모인다 | 답을 재다 본 어긋남 |
| 4. SFT에서 그 프롬프트만 빼면 QFFT처럼 되는가 | 11월 12일 | 된다. 길이 0.60배, 정답률은 그대로 | 앞 결과에서 나온 의문 |
| 5. 모델은 그 프롬프트의 무엇에 반응하는가 | 11월 15–19일 | 자리가 아니라 지시의 뜻에 반응한다. 어려운 문제에서는 빼도 길게 푼다 | 회의에서 받은 질문 |
| 6. 공개 모델도 그런가. QFFT의 모양은 QFFT만의 것인가 | 11월 24일 | 공개 모델 둘 다 그렇다. 단서가 없는 입력에서는 따로 학습한 모델들이 같은 모양에 모인다 | 앞 결과를 넓힘 |
| 7. 단서가 없는데도 길어지는 답은 어디서 길어지는가 | 11월 24일 | 풀다가 길어진다. 문제를 읽은 직후의 상태에 이미 예고돼 있다 | 답을 읽다 본 어긋남 |
| 8. 학습 입력의 문장을 바꾸면 켜는 단서도 따라 바뀌는가 | 11월 24–25일 | 아니다(미리 적은 예측이 틀림). 풀이를 서술하는 지시문으로 학습했을 때만 의존이 생겼다 | 원인인지 확인 |
| 9. 다시 학습하지 않고 단서만 빼는 것이 방법이 되는가 | 11월 24–25일 | 표준 SFT에서는 된다. 공개 모델에서는 정답률이 판정 불가와 손해로 나왔다 | 방법으로 쓸 수 있는지 확인 |
| 10. 공개 모델에서 정답률은 왜 내려갔나 | 11월 25일 | 큰 부분은 답을 쓰고도 끝내지 못한 답이었다. 어려운 문제의 손해는 따로 있다 | 답을 읽다 본 어긋남 |

### 질문 1. QFFT의 효과는 질문을 지워서 생긴 것인가 (9월)

| 순서 | 내용 |
|---|---|
| 본 현상 | 논문을 재현하니 정답률과 길이는 맞았습니다(QFFT 80.3%, 4,630 tokens. SFT 79.7%, 6,576 tokens). 그런데 질문만 지우고 학습한 모델(A1)은 SFT와 거의 같았습니다(Long-CoT 비율 86.0% 대 91.4%, 6,149 대 6,576 tokens). |
| 든 의문 | 질문을 지운 것이 원인이 아니라면, QFFT와 A1 사이에서 다른 무엇이 길이를 정하는가? |
| 그때까지 안 해 본 것 | 논문은 SFT와 QFFT 두 끝만 견줬습니다. 그 사이를 한 요소씩 바꾼 모델은 없었습니다. |
| 그래서 한 것 | 한 요소씩 다른 모델을 학습했습니다. A1은 질문만 지웠고, A2는 질문을 지우고 응답 첫 토큰을 맞히는 학습(loss)까지 뺐습니다. |
| 답 | A2에서 Long-CoT 비율이 39.9%로 내려갔습니다(QFFT는 44.1%). A1과 A2 사이의 차이는 약 92%가 응답 첫 토큰을 거쳐 일어났습니다. |
| 다음 의문 | 첫 토큰이 길이를 좌우한다는 관찰은 10월에 나온 논문(arXiv 2610.34350)에 이미 있어 이 연구만의 결과가 될 수 없었습니다. 첫 토큰 밖에서 길이를 정하는 것은 없는가? |
| 지금 돌아보면 | 이때 이미 실마리가 있었습니다. A1은 질문을 지웠는데도 길었고, A1의 학습 입력에는 시스템 프롬프트가 남아 있었습니다. 그때는 이것을 첫 토큰으로만 설명했고 시스템 프롬프트를 바꿔 볼 생각은 하지 못했습니다. 그 의문은 두 달 뒤 질문 3에서 나왔습니다. |

자세한 기록: [연구 개요의 "지금까지의 흐름"](../research/qfft-adaptive-reasoning.html), [모델마다 생각하는 습관](2026-10-15-reasoning-habits.html)

### 질문 2. 첫 토큰 밖에도 습관적으로 길어지는 자리가 있는가 (10월 말–11월 8일)

| 순서 | 내용 |
|---|---|
| 본 현상 | 출발점이 된 관찰은 없었습니다. 첫 토큰 쪽이 선행 연구와 겹친다는 것을 알고, 다른 자리의 후보를 여럿 세워 하나씩 작게 시험했습니다. |
| 든 의문 | 문제의 겉모습(수식 표기, 답 형식 지시), 문제를 다 읽은 직후의 상태, 풀이 도중의 되짚는 말(Wait, Alternatively)에 습관적으로 길어지는 편향이 있는가? |
| 그래서 한 것 | 스모크와 파일럿을 약 190개 돌렸습니다. 11월 8일의 글 열한 편이 그 일부입니다. |
| 답 | 표기와 질문 끝 표현에서는 큰 편향이 없었습니다. Wait와 Alternatively를 못 쓰게 하면 어려운 8문항에서 답이 절반으로 줄었지만 이미 있는 방법과 가까웠습니다. 방법으로 이어진 것은 없습니다. |
| 남은 관찰 | 두 가지가 뒤의 질문으로 이어졌습니다. 설명하듯 풀고 끝낸 답은 94.8%가 정답이고 되짚는 말로 넘어간 답은 62.0%만 정답이었습니다. 가장 긴 답 약 10%가 tokens의 절반을 쓰는데 그 답의 정답률은 15–22%였습니다. |
| 지금 돌아보면 | 이 시기는 "이것도 해 봤는데 이렇다"의 나열이었습니다. 후보마다 통과 기준은 미리 정했지만, 그 후보를 고른 까닭이 우리 자료의 현상이 아니었습니다. 떨어진 후보에서 "왜 안 됐는가"를 따지지 않아 다음 질문도 나오지 않았습니다. |

자세한 기록: [방법 점검](2026-11-08-c-audit.html), [Wait와 Alternatively 금지](2026-11-08-g-g1.html), [표지 분석](2026-11-08-i-h01.html), [전체 점검](2026-11-09-a-diagnosis.html)

### 질문 3. 첫 토큰을 같게 맞춰도 SFT만 길다. 무엇 때문인가 (11월 9일)

| 순서 | 내용 |
|---|---|
| 본 현상 | 모델이 답을 길게 풀지 짧게 풀지는 답의 첫 단어에서 갈린다고 알고 있었습니다. 그래서 모든 모델의 답 첫 단어를 `To`로 똑같이 맞춰 봤습니다. 그런데도 표준 SFT는 답의 80.0%를 길게 풀었고, 질문 없이 학습한 모델(A1)은 42.6%만 길게 풀었습니다. |
| 든 의문 | 첫 단어가 같은데도 차이가 난다면 그 차이는 첫 단어 앞, 곧 모델에 넣어 준 입력에서 옵니다. 입력의 어느 부분 때문인가? |
| 그때까지 안 해 본 것 | 입력은 "질문이 있었나 없었나"로만 나눠 봤습니다. 시스템 프롬프트(입력 맨 앞의 지시 문장)는 모든 모델의 평가 입력에 늘 똑같이 붙어 있어서 바꿔 볼 생각을 하지 않았습니다. |
| 그래서 한 것 | 입력의 한 부분만 바꿔 가며(질문을 다른 질문으로 바꾸기, 시스템 프롬프트 없애기) 모델의 반응이 얼마나 달라지는지 쟀습니다. 시스템 프롬프트 없이 학습한 모델도 새로 만들어 견줬습니다. |
| 답 | 질문을 바꾸면 네 모델이 똑같이 반응했습니다. 시스템 프롬프트를 없애면 표준 SFT만 A1보다 3.5–4.9배 크게 반응했습니다. 없애고 나면 네 모델 모두 답의 27–31.5%만 길게 풀어 같은 수준이 됐습니다. 시스템 프롬프트 없이 학습한 모델은 평가 때 그 문장이 있든 없든 달라지지 않았습니다. |
| 다음 의문 | QFFT가 짧게 푸는 것도 "질문을 지워서"가 아니라, QFFT의 긴 풀이가 이 시스템 프롬프트에 기대고 있지 않아서가 아닌가? ([학습 프롬프트 빼기](2026-11-12-b-drop-training-prompt.html)) |

자세한 기록: [첫 토큰을 고정해도 시스템 프롬프트를 없애면 답이 짧아진다](2026-11-09-h-system-instruction-dependence.html)

### 질문 4. SFT에서 그 프롬프트만 빼면 QFFT처럼 되는가 (11월 12일)

| 순서 | 내용 |
|---|---|
| 본 현상 | 풀이 도중 틀린 계산을 만났을 때 모델이 "Wait" 하고 되짚는지를 쟀습니다. QFFT는 표준 SFT보다 틀린 곳을 더 잘 골라 되짚는 것이 아니었습니다. 맞는 곳이든 틀린 곳이든 덜 되짚을 뿐이었습니다. 그리고 표준 SFT도 평가 입력에서 시스템 프롬프트를 빼면 QFFT와 같은 수준으로 덜 되짚었습니다. |
| 든 의문 | 표준 SFT가 길게 푸는 것은 학습 때 본 시스템 프롬프트 때문 아닌가? 그렇다면 다시 학습하지 않고 그 문장만 빼도 QFFT만큼 짧아지지 않는가? |
| 그때까지 안 해 본 것 | 평가 때는 모든 모델에 같은 입력(시스템 프롬프트 + 질문)을 넣습니다. 공정해 보여서 그 입력을 바꿔 본 적이 없었습니다. 그런데 그 시스템 프롬프트는 표준 SFT가 학습 때 긴 풀이와 늘 함께 본 문장이고, QFFT는 학습 때 본 적이 없는 문장입니다. |
| 그래서 한 것 | 표준 SFT를 그대로 두고, 평가 입력에서 시스템 프롬프트만 빼 MATH500 500문제를 4번씩 풀게 했습니다. 그 문장 없이 학습한 모델과 Base에도 똑같이 해서 견줬습니다. |
| 답 | 표준 SFT의 답이 평균 6,507 tokens에서 4,899 tokens로 줄었습니다(같은 문제끼리 견주면 0.60배). 정답률은 80.5%에서 80.9%로 그대로였습니다. 그 문장 없이 학습한 모델과 Base는 길이가 달라지지 않았습니다(1.04배, 0.95배). |
| 다음 의문 | 뺀 것이 중요한가, 모델은 그 문장의 무엇에 반응하는가? 답을 `\boxed{}`에 넣으라는 한 문장만 질문 뒤에 붙여도 답 2,000개 가운데 1,997개가 다시 "Okay"로 시작하며 길게 풀었습니다. ([스모크 세 개](2026-11-15-a-system-prompt-smoke.html)) |

자세한 기록: [학습 프롬프트 빼기](2026-11-12-b-drop-training-prompt.html), [11월 12일 보고 정리](2026-11-12-c-report-findings.html)

### 질문 5. 모델은 그 프롬프트의 무엇에 반응하는가 (11월 15–19일)

| 순서 | 내용 |
|---|---|
| 본 현상 | 시스템 프롬프트 칸을 없애고 답 형식 지시 한 문장만 질문 뒤에 붙여도, 답 2,000개 가운데 1,997개가 다시 "Okay"로 시작했고 길이가 0.81배로 돌아왔습니다. |
| 든 의문 | 긴 풀이를 켜는 것은 시스템 프롬프트라는 자리인가, 문장의 글자인가, 뜻인가? 어려운 문제에서도 빼면 짧아지는가? 모델 안에서는 어디로 전달되는가? |
| 그때까지 안 해 본 것 | 시스템 프롬프트는 통째로 넣거나 빼기만 했습니다. 문장을 바꿔 넣거나, 난이도를 나눠 보거나, 모델 안의 상태를 직접 건드려 본 적은 없었습니다. |
| 그래서 한 것 | 같은 뜻의 다른 문장, 무관한 문장, 낱말 순서를 섞은 문장, 부정문, 한국어 번역을 넣었습니다. 어려운 벤치마크(AIME25)를 돌렸습니다. 시스템 프롬프트가 있을 때와 없을 때의 내부 상태 차이를 뽑아 응답이 시작되는 위치에 더했습니다. |
| 답 | 같은 뜻의 다른 문장은 0.81배로 다시 길어졌고 무관한 문장은 0.52배로 뺀 것과 같았습니다. 낱말을 섞거나 번역해도 길게 풀었습니다. AIME25에서는 빼도 18%만 줄고 Long-CoT가 90% 넘게 남았습니다. "reason step by step"을 "answer concisely"로 바꾸면 GSM8K는 0.49배, AIME25는 0.97배였습니다. 내부 상태의 차이를 응답 시작 위치 한 곳에 더하면 긴 풀이가 돌아왔고, 무관한 문장에서 뽑은 차이와 학습 전 모델에서는 켜지지 않았습니다. |
| 다음 의문 | 이것은 직접 학습한 모델 하나의 버릇인가, 공개 모델에서도 그런가? 그리고 QFFT의 "쉬운 문제는 짧게, 어려운 문제는 길게"가 바로 이 현상 아닌가? |

자세한 기록: [스모크 세 개](2026-11-15-a-system-prompt-smoke.html), [다음 실험 세 개](2026-11-18-a-system-prompt-start-state.html), [묶음 2](2026-11-19-a-system-prompt-batch2.html), [어려운 문제 확인](2026-11-19-d-concise-hard-and-midway-switch.html)

### 질문 6. 공개 모델도 그런가. QFFT의 모양은 QFFT만의 것인가 (11월 24일)

| 순서 | 내용 |
|---|---|
| 본 현상 | 질문 3–5의 결과는 모두 직접 학습한 모델에서 나왔습니다. 한편 QFFT의 표준 사용과 "SFT에서 단서를 뺀 답"은 길이가 난이도에 따라 달라지는 모양이 닮아 보였습니다. |
| 든 의문 | 공개된 긴 추론 모델도 학습 때의 프롬프트를 빼면 긴 풀이가 꺼지는가? QFFT의 적응형 모양은 QFFT 학습에서만 나오는가, 단서가 없는 입력이면 어디서나 나오는가? |
| 그때까지 안 해 본 것 | 공개 모델은 늘 정해진 시스템 프롬프트로 평가됩니다. 그 프롬프트 없이 길이, 난이도, 정답률을 같은 조건으로 잰 자료는 찾지 못했습니다. QFFT의 모양을 다른 모델의 "단서 없는 입력"과 나란히 놓은 연구도 찾지 못했습니다. |
| 그래서 한 것 | 공개 모델 둘(Bespoke-Stratos-7B, OpenThinker-7B)에서 학습 때의 프롬프트를 뺐습니다. 저장된 평가 결과로 모델마다 "남는 비율"을 계산해 한 표에 놓았습니다. |
| 답 | Bespoke-Stratos-7B는 답 360개가 모두 생각 형식으로 시작하다가 프롬프트를 빼면 0개가 됐습니다. OpenThinker-7B는 시스템 프롬프트만 빼면 95–100%가 남았고, 사용자 칸에 늘 붙던 고정 문장까지 빼야 0%가 됐습니다. 의존하는 단서가 모델마다 달랐습니다. 문제 글만 주면 남는 비율은 QFFT가 0.16, 0.55, 0.90이고 SFT가 0.08, 0.49, 0.87입니다(GSM8K, MATH500, AIME25). 따로 학습한 모델들이 같은 모양에 모였습니다. |
| 다음 의문 | 단서를 뺀 입력의 답을 읽다가 이상한 점을 봤습니다(질문 7). 그리고 지금까지는 모두 이미 있는 모델을 견준 것이라, 원인인지는 직접 본 적이 없습니다(질문 8). |

자세한 기록: [공개 모델](2026-11-24-a-public-model-prompt-gate.html), [남는 비율로 QFFT 다시 읽기](2026-11-24-b-leak-fraction-qfft.html), [단서 사다리](2026-11-24-d-cue-ladder.html)

### 질문 7. 단서가 없는데도 길어지는 답은 어디서 길어지는가 (11월 24일)

| 순서 | 내용 |
|---|---|
| 본 현상 | 학습 때의 입력 요소를 뺀 입력에서는 답이 "Okay"(긴 풀이의 시작 말)로 시작하는 경우가 하나도 없었습니다(0.0%). 그런데 긴 풀이로 분류되는 답은 MATH500에서 22–36%, AIME25에서 83–90%였습니다. |
| 든 의문 | 처음부터 길게 풀기로 한 답이 없는데 긴 답이 있다면, 그 답은 풀다가 길어진 것입니다. 어디서 길어지고, 무엇이 그것을 정하는가? |
| 그때까지 안 해 본 것 | 긴 풀이는 답의 첫 단어에서 정해진다고 보고 그 자리만 쟀습니다. 첫 단어는 짧은 풀이 쪽인데 뒤에서 길어지는 답을 따로 떼어 본 적이 없었습니다. |
| 그래서 한 것 | 답을 "Okay로 시작한 답"과 "풀다가 Wait가 나온 답"으로 나눠 난이도별로 셌습니다. 그리고 모델이 문제를 다 읽은 직후의 내부 상태만 보고 "이 문제는 풀다가 길어질 것"을 미리 맞힐 수 있는지 쟀습니다. |
| 답 | 긴 풀이로 들어가는 길은 둘이었습니다. 하나는 입력 요소가 켜는 길로, 쉬운 문제에서도 켜집니다. 다른 하나는 풀다가 켜지는 길로, 쉬운 문제에서는 12–17%, 어려운 문제에서는 50–61%였고 SFT, A1, QFFT가 같은 모양이었습니다. 이 길은 문제를 읽은 직후의 내부 상태로 83%까지 미리 맞힐 수 있었고, 실제로 "Wait"가 나오는 것은 그보다 600–900 tokens 뒤였습니다. |
| 다음 의문 | 모델은 풀기 전에 이미 "이 문제는 풀다가 길어질 것"을 알고 있습니다. 어려운 문제에서 긴 풀이가 필요한 때를 이 상태로 알아낼 수 있는가? ([풀이 상태를 보고 다음 행동 고르기](2026-11-24-f-state-aware-next-action.html)) |

자세한 기록: [긴 풀이로 들어가는 길은 둘이다](2026-11-24-e-two-routes-to-long-reasoning.html), [풀기 전에 정하고 풀다가 다시 정하기](2026-11-24-c-plan-and-replan.html)

### 질문 8. 학습 입력의 문장을 바꾸면 켜는 단서도 따라 바뀌는가 (11월 24–25일)

| 순서 | 내용 |
|---|---|
| 본 현상 | 모델마다 "학습 때 긴 풀이와 함께 있던 입력 요소"가 평가 입력에 없으면 답이 짧아졌습니다. 다만 견준 모델들은 학습 자료의 구성이 여러 군데 달라서, 그 요소가 정말 원인인지는 직접 본 적이 없었습니다. |
| 든 의문 | 학습 때 시스템 프롬프트 자리에 있던 문장이 원인인가? 원인이라면 그 자리에 아무 문장이나 넣고 학습해도 그 문장이 긴 풀이를 켜는 스위치가 되어야 합니다. |
| 그때까지 안 해 본 것 | 문장 하나만 다르고 나머지는 모두 같은 두 모델을 만들어 견준 적이 없었습니다. |
| 그래서 한 것 | 같은 자료와 같은 설정에서, 시스템 프롬프트 문장만 풀이와 무관한 문장(어촌 장터 이야기)으로 바꿔 새로 학습했습니다. 어떤 결과가 나올지와 판정 기준은 결과를 보기 전에 적어 두었습니다. 이어서 학습 전 모델에도 같은 문장들을 넣어 봤습니다. |
| 답 | 미리 적은 예측이 틀렸습니다. 새 모델은 그 무관한 문장이 있든 없든 똑같이 길게 풀었습니다. 무관한 문장은 스위치가 되지 않았습니다. 확인된 것은 절반입니다. 표준 SFT에서 원래 지시문이 긴 풀이를 켜는 힘은 그 지시문으로 학습해서 생긴 것이었습니다(학습 전 모델은 그 지시문을 붙여도 답 길이가 1.03–1.04배로 거의 그대로였습니다). |
| 다음 의문 | 왜 풀이 방식을 지시하는 문장에는 긴 풀이가 기대게 되고, 무관한 문장에는 그렇지 않은가? 문장의 뜻 때문인가, 익숙한 문장이어서인가? 뜻이 같고 낱말이 다른 지시문으로 학습해 봐야 가를 수 있습니다(학습 승인 대기). |

**실제 입력과 실제 답.** GSM8K의 한 문항입니다(정답 14). 프롬프트 템플릿의 시스템 프롬프트 칸에 무관한 문장을 넣어 두 모델에 줬습니다.

<!-- xp-causal -->
<figure class="xp"><p class="xp-t">시스템 프롬프트 칸에 무관한 문장을 넣어 두 모델에 줍니다 (GSM8K 문항 55, 정답 14)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class=""><span class="xp-hit">The harbor town holds a small fish market every Saturday near the old pier.</span></div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Jean has 30 lollipops. Jean eats 2 of the lollipops. With the remaining lollipops, Jean wants to package 2 lollipops in one bag. How many bags can Jean fill?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">입력: 두 모델 동일</div></div><div class="xp-note"><b>두 모델의 차이</b>기존 SFT는 학습 때 시스템 프롬프트로 "Please reason step by step, …"를 봤습니다. 새 단서 SFT는 같은 자료에서 그 문장만 위의 빨간 문장으로 바꿔 학습했습니다. 그 밖의 학습 설정은 같습니다.<b>미리 적은 예측</b>새 단서 SFT는 자기가 학습 때 본 이 문장이 있을 때만 길게 풀 것이다.<b>결과</b>새 단서 SFT는 이 문장이 있든 없든 길게 풀었습니다. 예측이 틀렸습니다.</div></div><div class="xp-cols" style="margin-top:14px"><div><p class="xp-name">기존 SFT: 97 tokens, 답 14는 맞지만 \boxed{} 없이 끝나 공식 채점은 오답</p><pre class="xp-ex">Jean initially has 30 lollipops. After eating 2, she has 30 - 2 = 28 lollipops left. She wants to package them in bags with 2 lollipops each. 
To find out how many bags she can fill, divide the remaining lollipops by the number per bag: 28 ÷ 2 = 14. 
So Jean can fill 14 bags.</pre></div><div><p class="xp-name">새 단서 SFT: 515 tokens, 정답</p><pre class="xp-ex"><span class="xp-hit">Okay</span>, let me try to figure this problem out step by step. It's about Jean and lollipops. Hmm. Let's see...
First, the problem says Jean has 30 lollipops. Then, Jean eats 2 of them. So, I need to …
<span class="xp-sp">(가운데 줄임)</span>
… the answer is 14. So, I think that's correct.
**Final Answer**
Jean can fill \boxed{14} bags.</pre></div><div><p class="xp-name">새 단서 SFT, 시스템 프롬프트 칸을 비움: 1,005 tokens, 정답</p><pre class="xp-ex"><span class="xp-hit">Okay</span>, let me try to figure this out. So, Jean starts with 30 lollipops. Then she eats 2 of them. Hmm, so how many are left? Let me subtract: 30 - 2 = 28. So, she has 28 lollipops left.
Now, she wants …
<span class="xp-sp">(가운데 줄임)</span>
… eaten ones. So, that's correct.
So, yes, the answer is 14. So, I think I'm good.
**Final Answer**
\boxed{14}</pre></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>모델이 새로 생성</span></div><p class="xp-cap">글상자는 저장된 실제 출력입니다(가운데는 줄였습니다). 한 문항의 예시이고, 판정은 본문 표의 200문항 값으로 냈습니다.</p></figure>
<!-- /xp-causal -->

자세한 기록: [원인 실험](2026-11-24-g-causal-cue-swap.html)

### 질문 9. 다시 학습하지 않고 단서만 빼는 것이 방법이 되는가 (11월 24–25일)

| 순서 | 내용 |
|---|---|
| 본 현상 | 표준 SFT는 쉬운 문제에도 길게 풉니다. MATH500 한 문제에 평균 6,576 tokens를 쓰는데 학습 전 모델(Base)은 635 tokens, QFFT는 4,630 tokens입니다. 그런데 평가 때 모델에 넣는 입력은 문제만이 아닙니다. 프롬프트 템플릿(`<|im_start|>system`, `<|im_start|>user` 같은 역할 표시)과 시스템 프롬프트("Please reason step by step, and put your final answer within \boxed{}.")가 문제를 감싸고 있습니다. 표준 SFT는 학습 때도 바로 이 템플릿과 시스템 프롬프트를 긴 풀이와 함께 봤고, QFFT는 학습 때 둘 다 본 적이 없습니다. |
| 든 의문 | 표준 SFT가 길게 푸는 것은 문제 때문인가, 문제를 감싼 입력 때문인가? 나눠서 묻습니다. (1) 시스템 프롬프트 문장이 답 길이에 영향을 주는가. (2) 프롬프트 템플릿이 영향을 주는가. (3) 영향을 주는 부분을 평가 입력에서 빼면 정답률은 유지되는가. 유지된다면 QFFT나 A2처럼 새로 학습하지 않고 그 부분만 빼도 같은 길이와 정답률을 얻는 것 아닌가. (4) 공개 모델과 더 어려운 문제에서도 같은가. |
| 그때까지 안 해 본 것 | 앞에서는 100문제로만 재서 정답률이 같은지 말할 수 없었습니다. 공개 모델을 500문제 전체로, 미리 정한 기준으로 잰 적이 없었습니다. |
| 그래서 한 것 | 같은 표준 SFT, 같은 MATH500 500문제에 입력만 세 가지로 바꿔 넣었습니다. ① 평소 입력(프롬프트 템플릿 + 시스템 프롬프트 + 문제) ② 시스템 프롬프트만 뺀 입력(프롬프트 템플릿 + 문제) ③ 프롬프트 템플릿까지 뺀 입력(문제 문장만). 공개 모델 둘에는 그 모델이 학습 때 본 시스템 프롬프트와 질문 앞의 고정 문장("Return your final response within \boxed{}.")을 뺐습니다. 판정 기준은 결과를 보기 전에 정했고, 정답률이 떨어진 경우에는 답을 직접 읽었습니다. |
| 답 | 표준 SFT에서는 됐습니다(길이 절반 이하, 정답률 그대로). 공개 모델 둘도 길이가 4분의 1에서 절반으로 줄었지만 정답률은 달랐습니다. Bespoke-Stratos-7B는 정답률 차 −2.0%p로 "떨어지지 않았다"고도 "떨어졌다"고도 할 수 없었고, OpenThinker-7B는 5.3%p 떨어졌습니다(제한 길이를 32,000 tokens로 늘려 잰 값). 가장 어려운 시험(AIME25)에서는 두 모델 모두 정답률이 내려가는 쪽이었습니다(20.8% → 15.0%, 22.5% → 15.8%). |
| 다음 의문 | OpenThinker-7B의 정답률은 쉬운 수준에서도 떨어졌습니다(Level 2에서 −7.2%p). 쉬운 문제를 짧게 풀다 틀렸다고 보기는 어렵습니다. 무엇이 틀렸는가? (질문 10) |

자세한 기록: [방법 정리](2026-11-24-h-drop-training-cues-method.html)

### 질문 10. 공개 모델에서 정답률은 왜 내려갔나 (11월 25일)

| 순서 | 내용 |
|---|---|
| 본 현상 | 손해가 쉬운 수준에서도 났습니다. 그리고 "최대 길이에 닿은 답"의 수가 두 입력에서 비슷했는데(141개 대 192개) 길이는 한쪽이 절반이었습니다. 짧게 푸는 쪽에서 최대 길이까지 간 답이 더 많다는 것이 이상했습니다. |
| 든 의문 | 단서를 뺀 입력에서 최대 길이까지 간 답은 무엇을 쓰고 있었나? |
| 그때까지 안 해 본 것 | 최대 길이에 닿은 답은 한 덩어리로 오답 처리했습니다. 그 답을 읽어 종류를 나눠 본 적이 없었습니다. |
| 그래서 한 것 | 최대 길이에 닿은 답을 직접 읽고 "풀이 중", "답 없이 되풀이", "답을 쓴 뒤 되풀이"로 나눴습니다. 다른 모델과 학습 전 모델에서도 같은 답을 셌습니다. |
| 답 | 표준 입력의 141개 가운데 121개는 풀이를 이어 가던 답이었습니다. 단서를 뺀 입력의 192개 가운데 158개는 답을 쓰고도 끝내지 못한 답이었고, 그 가운데 115개(73%)는 처음 쓴 답이 정답이었습니다. 첫 답에서 멈춘다고 놓으면 정답률 차는 최대 길이를 늘린 값 기준으로 −5.3%p에서 +0.3 [−1.6, +2.1]%p가 됩니다(규칙을 결과 뒤에 정했으므로 새 표본으로 다시 재는 중). 받기 전에 예측을 적어 둔 GSM8K 칸에서도 같은 일이 나왔습니다(끝내지 못한 답 6.3%, 그 74%가 정답). 학습 전 모델도 프롬프트 템플릿 없이 지시문과 문제 글만 주면 답의 32%가 그랬습니다. |
| 다음 의문 | 왜 끝내지 못하는가? 표준 입력의 끝난 답은 100%가 학습 형식의 끝 표지로 끝나고, 단서를 뺀 입력의 끝난 답은 0–0.4%만 그렇습니다(열려 있는 질문 2). 그리고 AIME25의 손해는 이것으로 설명되지 않습니다. 끝내지 못한 답의 처음 쓴 답이 한 개도 정답이 아니었습니다(열려 있는 질문 3). |

**실제 입력과 실제 답.** 공개 모델 OpenThinker-7B에 실제로 넣은 입력과 저장된 실제 출력입니다. 문항은 MATH500의 Level 3 문제이고 정답은 9입니다. 시스템 프롬프트는 1,312자라 가운데를 줄였습니다.

<!-- xp-public -->
<figure class="xp"><p class="xp-t">공개 모델에서 학습 때의 단서를 뺍니다 (OpenThinker-7B, MATH500 문항 3, 정답 9)</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Your role as an assistant involves thoroughly exploring questions through a systematic long thinking process before providing the final precise and accurate solutions. <span class="xp-sp">(가운데 줄임, 전체 1,312자)</span> Now, try to solve the following question through the above guidelines:</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Return your final response within \boxed{}.</div><div class="">How many positive whole-number divisors does 196 have?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">표준 입력(그 모델이 학습 때 본 입력)</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-del"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Your role as an assistant involves thoroughly exploring questions through a systematic long thinking process before providing the final precise and accurate solutions. <span class="xp-sp">(가운데 줄임, 전체 1,312자)</span> Now, try to solve the following question through the above guidelines:</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div></div><div class="xp-del"><div class="">Return your final response within \boxed{}.</div></div><div class="xp-ctx"><div class="">How many positive whole-number divisors does 196 have?</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class="">(끝까지 새로 생성)</div></div><div class="xp-name">단서를 뺀 입력</div></div></div><div class="xp-note"><b>바꾸는 것</b>추론 입력에서 학습 때의 시스템 프롬프트와, 사용자 칸 앞에 늘 붙던 고정 문장을 뺍니다. 프롬프트 템플릿는 그대로 둡니다.<b>그대로 두는 것</b>모델의 가중치, 문제, 온도 0.6, top_p 1, 최대 16,384 tokens. 문항마다 4번 풀게 했습니다.</div><div class="xp-cols" style="margin-top:14px"><div><p class="xp-name">표준 입력: 4번 모두 정답, 1,485–2,019 tokens(평균 1,812)</p><pre class="xp-ex">&lt;|begin_of_thought|&gt;
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

자세한 기록: [방법 정리의 "시험 ③ 둘째 결과"와 "셋째 결과"](2026-11-24-h-drop-training-cues-method.html), [원인 실험의 "학습 전 모델 확인"](2026-11-24-g-causal-cue-swap.html)

## 지금 열려 있는 질문

**표 읽는 법.** 한 줄이 아직 답하지 못한 질문 하나입니다. "본 현상"은 그 질문이 나온 자리이고, "답할 실험"은 설계와 지금 상태입니다.

| 질문 | 본 현상 | 아직 안 해 본 것 | 답할 실험과 상태 |
|---|---|---|---|
| 1. 왜 풀이를 서술하는 지시문에만 의존이 생기는가 | 지시문 S로 학습하면 의존이 생기고 무관한 문장으로 학습하면 생기지 않았습니다. 학습 전 모델은 S를 붙여도 1.03–1.04배였습니다 | 직접 학습해 본 서술형 지시문은 S 하나입니다. S는 널리 쓰이는 문장이라 "뜻 때문"과 "익숙한 문장이어서"를 가르지 못합니다 | S와 뜻이 같고 낱말이 다른 지시문으로 한 번 더 학습합니다. 학습이 필요해 승인을 기다립니다 |
| 2. 왜 답을 쓰고도 끝내지 못하는가 | 단서를 뺀 입력에서 답의 0.7–7.9%가 답을 쓰고도 끝내지 못하고 같은 줄을 되풀이했습니다. 학습 전 모델도 프롬프트 템플릿 없이 지시문과 문제 글만 주면 32%가 그랬습니다 | 끝낼지 계속할지가 정해지는 자리(답을 쓴 뒤의 문단 첫머리)에서 끝 토큰이 올 확률을 단서가 있을 때와 없을 때로 견준 적이 없습니다 | 저장된 답의 글을 그대로 읽히고 프롬프트만 바꿔 그 자리의 확률을 잽니다(새로 생성하지 않음). 새 표본의 재확인이 끝난 뒤에 합니다 |
| 3. 어려운 문제에서 단서가 필요한 때를 알 수 있는가 | AIME25에서 단서를 빼면 정답률이 내려가는 방향입니다(−5.8, −6.7%p). 한편 문제를 읽은 직후의 상태는 "풀다가 길어질 문항"을 0.83의 정확도로 가릅니다 | 그 상태 신호로 단서를 넣을 문항을 고른 적이 없습니다. 지금까지는 문항마다 다시 푸는 방식만 비교 기준으로 재 봤습니다 | 같은 중간 풀이에서 다음 행동을 바꿔 이어 써 보는 시험의 1단계가 돌고 있습니다 |
| 4. QFFT 학습은 단서를 빼는 것과 무엇이 다른가 | AIME25에서 QFFT는 SFT의 0.82배로 거의 줄이지 않는데, 공개 모델에서 단서를 뺀 입력은 0.29배, 0.56배로 크게 줄이고 정답률이 내려갑니다 | 표준 SFT에 문제 글만 준 AIME25와 GSM8K의 전체 크기 값이 없습니다 | 남은 일곱 칸이 오늘 돕니다 |
| 5. 학습을 한 번 더 해도 같은가 | 지금까지의 결과는 모델마다 학습 한 번에서 나왔습니다 | 시드만 바꾼 SFT가 없습니다 | 오늘 저녁 학습하고 내일 새벽 평가합니다 |

## 문장의 첫 토큰과 문단 단위에서 본 것

11월 25일 회의에서 "응답의 첫 토큰만이 아니라 문장마다의 첫 토큰(Hmm, Let's think), Okay나 Alright, 빈 줄 같은 자리, 그리고 낱말이 아니라 블록 단위에도 뜻하지 않은 편향이 있지 않은가"라는 생각거리가 나왔습니다. 지금까지 본 것과 안 본 것을 자리별로 정리합니다.

| 자리 | 지금까지 본 것 | 아직 안 본 것 |
|---|---|---|
| 응답의 첫 토큰 (Okay, To) | 질문 1: 모델 사이 길이 차의 약 92%가 이 자리를 거칩니다. 질문 5: 지시 한 문장으로 답 2,000개 가운데 1,997개가 Okay로 시작합니다. 선행 연구(arXiv 2610.34350, 2610.06851)와 겹칩니다 | 없음(겹쳐서 더 파지 않음) |
| 문단 첫머리의 되짚는 말 (Wait, Hmm, Alternatively) | 학습 풀이의 되짚는 말은 절반(51.9%)이 문단 첫머리에 있고, 53%는 앞의 되짚는 말에서 100 tokens 안에 또 나옵니다. 같은 글을 읽힐 때 시스템 프롬프트를 빼면 문단 첫머리에서 Wait가 나올 확률이 내려갑니다 | 되짚는 말의 종류마다(Wait와 Hmm) 단서에 반응하는 정도가 다른지 |
| 답을 쓴 뒤의 문단 첫머리 | 질문 10: 끝내지 못한 답은 "Final Answer" 줄 같은 블록 하나를 수백 번 되풀이합니다 | 이 자리에서 끝 토큰 대신 같은 블록이 다시 오는 까닭(열려 있는 질문 2) |

## 점검: 실험 글 82편은 이 순서로 진행됐는가

**어떻게 점검했나.** 홈페이지의 QFFT 실험 글 82편을 한 편씩 다시 읽고 출발점을 셋으로 나눴습니다.

- **관찰에서 나온 의문**: 글에 "앞서 우리 자료에서 본 구체적인 현상"(수치나 사례)이 적혀 있고, 실험이 그 현상에서 나온 의문을 확인하는 것.
- **후보에서 출발**: 구체적인 앞선 관찰 없이, 떠오른 생각이나 이미 있는 방법, 후보 목록을 직접 학습한 모델에 시험한 것.
- **점검, 계획, 정리**: 채점 점검, 설계, 보고 정리처럼 출발점을 따질 대상이 아닌 것.
- **현상을 살핀 분석**: 개입 없이 저장된 답을 읽고 세어 현상을 적은 것(네 번째 갈래로 따로 셌습니다).

**표 읽는 법.** 한 줄이 시기 하나이고 숫자는 글의 수입니다. "관찰에서 나온 의문" 칸의 괄호는 출발 관찰이 글에 수치나 실제 사례로 적혀 있는 글만 센 수입니다(링크나 문구로만 앞 결과를 가리킨 글을 뺀 수).

| 시기 | 글 | 관찰에서 나온 의문 | 후보에서 출발 | 현상을 살핀 분석 | 점검, 계획, 정리 | 남은 것 |
|---|---|---|---|---|---|---|
| 10월 15일 – 11월 8일, 첫 토큰 밖의 후보 시험 | 12 | 5 (5) | 3 | 1 | 3 | 방법 없음. 관찰 둘이 뒤의 질문으로 이어짐 |
| 11월 9–12일, 전체 점검과 시스템 프롬프트 | 15 | 5 (5) | 4 | 1 | 5 | 질문 3, 4의 결과 |
| 11월 15–19일, 프롬프트의 무엇에 반응하는가 | 6 | 4 (4) | 2 | 0 | 0 | 질문 5의 결과. 방법 후보 하나는 기준에 못 미쳐 뺌 |
| 11월 20–23일, 풀이 도중 멈추기, 여러 번 풀어 투표하기, 추론 강도 고르기 | 41 | 19 (10) | 19 | 0 | 3 | 방법 없음. 미리 정한 기준에 못 미친 결과가 든 글 35편 |
| 11월 24–25일, 학습 단서 | 8 | 6 (6) | 0 | 0 | 2 | 질문 6–10의 결과 |
| 합 | 82 | 39 (30) | 28 | 2 | 13 | |

**점검에서 본 것.**

- **지금 남아 있는 결과는 모두 재거나 읽다가 본 어긋남에서 시작했습니다.** 질문 1은 "질문을 지웠는데도 길다", 질문 3은 "첫 토큰을 같게 했는데도 SFT만 길다", 질문 4는 "QFFT는 더 잘 가려서 되짚는 것이 아니라 덜 되짚을 뿐이다", 질문 7은 "Okay로 시작한 답이 0%인데 긴 풀이가 22–36%다", 질문 10은 "짧게 푸는 쪽에서 최대 길이에 닿은 답이 더 많다"였습니다.
- **후보에서 출발한 28편은 그 자체로 방법이 된 것이 없었습니다.** 다만 한 편은 쓸모 있는 관찰을 남겼습니다. 풀이 뒷부분의 후보 26개를 점검하며 잰 "틀린 단계에서 되짚는 정도"가 질문 4의 출발 관찰이 됐습니다.
- **11월 20–23일의 41편은 출발점이 가장 약했습니다.** 진행 기록 한 편을 뺀 40편 가운데 38편이 첫 문장을 결과로 시작하고, "어떤 관찰에서 출발했는가"를 따로 적은 글은 1편입니다. 글들은 여섯 줄기로 이어지는데(풀이 속의 값으로 오답 반박하기 10편, 여러 번 풀어 투표할 예산 나누기 5편, 추론 강도와 투표 가운데 고르기 7편 등) 그 가운데 다섯 줄기는 첫 글이 출발 관찰 없이 시작했습니다. 결과에서 다음 의문을 적은 글은 16편이었습니다.
- 같은 시기의 좋은 점도 있습니다. 판정 기준을 미리 정했고, 40편 가운데 36편은 답을 읽어 결과가 왜 그렇게 나왔는지를 적었습니다. 모자랐던 것은 설계와 분석이 아니라 "왜 이 질문인가"였습니다.
- **글의 순서도 같은 문제를 가렸습니다.** 82편 가운데 "왜 궁금했나"처럼 출발점을 적은 절이 있는 글은 33편이고, 그 절도 대부분 결과 요약 뒤에 있었습니다. 그래서 지금 줄기의 글 열두 편 맨 앞에 "연구 질문" 절을 새로 넣었습니다.

**돌아보면 더 빨리 갈 수 있었던 곳.**

| 때 | 그때 한 것 | 지금 보면 |
|---|---|---|
| 9월 | 질문만 지운 모델이 SFT만큼 길다는 것을 보고 첫 토큰으로 설명했습니다 | 그 모델의 학습 입력에 남아 있던 시스템 프롬프트를 바로 의심했다면 질문 3에 두 달 일찍 닿았습니다 |
| 10월 말 – 11월 8일, 11월 20–23일 | 후보를 넓게 세워 작게 시험하고 기준에 못 미치면 다음 후보로 넘어갔습니다 | 두 시기를 합쳐 글 53편에서 방법이 나오지 않았습니다(앞 시기에만 스모크와 파일럿이 약 190개였습니다). 가장 이상한 관찰 하나를 깊게 파는 쪽이 나았습니다 |
| 11월 12일 | 시스템 프롬프트 제거를 "뺐더니 짧아지고 정답률이 유지됐다"로 적었습니다 | 회의에서 지적을 받고서야 "무엇에 반응하는가"를 물었습니다. 결과를 적을 때 다음 의문까지 적었어야 합니다 |
| 11월 25일 | 공개 모델의 정답률 손해를 미리 정한 기준으로 판정했습니다 | 판정 표만 읽었다면 "정답률 손해"로 닫았을 것입니다. 최대 길이에 닿은 답을 직접 읽어서 끝내지 못한 답을 찾았습니다 |


## 점검에서 배운 것, 앞으로 지킬 것

1. **계획의 첫 줄에 출발점을 적습니다.** 본 현상(수치나 사례), 든 의문, 그때까지 안 해 본 것을 적고 나서 설계를 적습니다. 후보 목록에서 고른 시험이면 그렇게 밝힙니다.
2. **글은 결과가 아니라 연구 질문으로 시작합니다.** 맨 앞에 "본 현상, 든 의문, 그때까지 안 해 본 것, 그래서 한 것, 답, 다음 의문"을 둡니다.
3. **기준에 못 미친 결과도 그냥 닫지 않습니다.** 답을 읽어 까닭 하나와 다음 의문을 적습니다. 다음 의문이 나오지 않으면 그 줄기는 거기서 닫습니다.
4. **판정을 내기 전에 답을 직접 읽습니다.** 지금 남아 있는 결과 가운데 둘(질문 7, 질문 10)은 판정 표가 아니라 답을 읽다가 나왔습니다.
5. **글마다 메인 표와 실제 글을 넣습니다.** A2, QFFT와 ACC, Tokens를 견준 표, 그리고 모델에 실제로 넣은 입력 문자열과 실제 답의 글입니다.


## 한계

- 이 글의 "그때까지 안 해 본 것"은 두 종류가 섞여 있습니다. 질문 5, 6, 8은 그때 선행 연구를 찾아보고 글에 적어 둔 것입니다. 질문 1–4, 7, 10은 이번에 다시 정리하면서 적은 것입니다. 뒤쪽은 그때 그렇게 생각하고 실험한 것이 아니라 지금 돌아본 것입니다.
- 출발점을 나눈 것은 글에 적힌 내용을 기준으로 했습니다. 글에 적지 않았을 뿐 실제로는 관찰에서 출발한 실험이 있을 수 있습니다. 11월 20–23일의 40편은 한 번에 다시 읽어 나눈 것이라 경계에 있는 글 몇 편은 다르게 볼 수 있습니다.
- 질문의 사슬은 지금 남아 있는 줄기를 따라 적었습니다. 11월 20일에 넓게 시험한 실험들(풀이 도중 멈추기, 여러 번 풀어 투표하기)은 사슬에 넣지 않고 점검 절에 따로 적었습니다.
- 모델은 Qwen2.5-7B-Instruct 계열이고 과제는 수학입니다. 모델마다 학습은 한 번입니다.

## 일지에서의 실험 번호

연구 질문 정리, 82편 점검, 메인 표의 "문제 글만" 줄의 채점 = 개발일지 11월 25일 "연구 질문으로 다시 정리, 실험 글 82편 점검, 메인 표" 항목. 메인 표의 나머지 줄 = 개발일지와 연구일지 11월 12일의 "MATH500 채점 확인과 최종 ACC", "GSM8K 채점 확인과 최종 ACC" 항목. 질문마다의 실험은 위 "자세한 기록"의 글 끝에 적힌 번호를 따릅니다.
