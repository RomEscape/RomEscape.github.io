---
title: 방법 정리, 지시문을 붙여 학습한 모델은 추론 때 그 단서를 빼면 재학습 없이 쉬운 문제는 짧게, 어려운 문제는 길게 푼다
date: 2026-11-24
project: QFFT
status: 진행 중
idea: 후보
idea_rank: 1
method_name: Question-Only Inference (QOI)
method_examples:
  - title: 쉬운 지수 문제에서 입력의 단서만 빼기
    kind: 실제 실험 예시
    problem: 'MATH500 Level 1 문항은 2^8 = 4^x에서 x를 묻습니다. 정답은 4입니다. 파인튜닝하기 전의 원래 모델(Qwen2.5-7B-Instruct)은 이 문항에 평균 222 tokens를 씁니다.'
    comparison: '평범하게 학습한 SFT에 같은 문제를 두 가지로 줍니다. 하나는 학습 때와 같은 표준 입력(프롬프트 템플릿과 시스템 프롬프트가 있음)이고, 다른 하나는 그 단서를 모두 뺀 입력(문제 글만)입니다. 모델은 다시 학습하지 않았습니다.'
    assessment: 'SFT의 평균 길이는 표준 입력에서 886 tokens, 단서를 뺀 입력에서 239 tokens였습니다(네 번 풀이의 평균). 단서를 빼면 원래 모델과 비슷한 길이로 풀고 답은 같습니다. 어려운 Level 5 문항에서는 두 입력 모두 16,000 tokens 넘게 썼습니다. 쉬운 문제만 짧아진 것입니다.'
summary: 긴 풀이를 학습한 모델을 다시 학습하지 않고 추론 입력에서 학습 때의 단서만 빼 길이를 줄이는 방법입니다. 표준 SFT는 MATH500에서 0.44배에 정답률을 지켰습니다. 공개 모델 둘은 0.26배, 0.52배로 줄지만 하나는 미리 정한 기준으로 정답률 손해입니다. 손해는 답을 쓰고도 끝내지 못한 답에서 나와, 첫 답에서 멈추면 없어집니다(시드를 바꾼 새 표본에서도 같았습니다. 다만 미리 정한 기준으로는 판정 불가입니다).
published: true
---

**방법 이름: Question-Only Inference (QOI), 문제만 넣는 추론.** 벤치마크 문제를 풀게 할 때(추론 때) 모델에 문제만 넣는 방법입니다. 표준 SFT라면 시스템 프롬프트와 프롬프트 템플릿을 모두 빼고 문제 문장만 넣습니다. 문제와 채점은 그대로이고, 모델은 다시 학습하지 않습니다. QFFT(Question-Free Fine-Tuning)가 학습에서 질문을 빼는 방법이라면, 이 방법은 추론에서 질문만 남깁니다.

## 이 방법과 근거 글의 관계

이 방법은 글 하나에서 나온 것이 아닙니다. 아래 글들이 차례로 쌓여 나왔습니다. 아래 글들은 따로 떨어진 방법이 아니라 이 방법의 근거입니다. "남는 비율" 분석은 이 방법이 왜 통하는지를 설명하는 글이고, 이 글은 그 설명을 써서 입력을 실제로 바꿔 돌린 결과입니다.

| 글 | 역할 | 한 일 | 보인 것 |
|---|---|---|---|
| [11월 9일, 시스템 프롬프트를 없애면 답이 짧아진다](2026-11-09-h-system-instruction-dependence.html) | 초기 관찰 | 프롬프트의 한 부분만 바꿔 다음 토큰 분포의 변화를 잼 | 시스템 프롬프트를 없애면 표준 SFT가 A1보다 3.5–4.9배 크게 움직였습니다 |
| [11월 12일, 시스템 프롬프트만 빼기](2026-11-12-b-drop-training-prompt.html) | 부분 적용 | 표준 SFT의 추론 입력에서 시스템 프롬프트만 빼고 MATH500 500문항 × 4회 생성 | 길이 0.60배, 정답률 그대로. 프롬프트 템플릿은 남긴 판입니다 |
| [11월 24일, 남는 비율 분석](2026-11-24-b-leak-fraction-qfft.html) | 근거 분석 | 새로 생성하지 않고 저장된 답으로 계산만 함 | QFFT가 쉬운 문제는 짧게, 어려운 문제는 길게 푸는 모양이 표준 SFT에서 시스템 프롬프트만 빼도 똑같이 나왔습니다. 이 모양은 QFFT 학습만의 결과가 아닙니다 |
| [11월 24일, 문제 글만 주기](2026-11-24-d-cue-ladder.html) | 첫 확인 실험 | 표준 SFT에 프롬프트 템플릿과 시스템 프롬프트 없이 문제 글만 넣음 | 길이 배분이 QFFT와 같아졌고 길어지는 문항도 같았습니다 |
| [11월 24일, 공개 모델 둘](2026-11-24-a-public-model-prompt-gate.html) | 공개 모델 확인 | 공개 모델 둘에서 학습 때의 시스템 프롬프트와 고정 문장을 뺌 | 두 모델 모두 긴 풀이 형식이 학습 때의 입력에 묶여 있었고, 묶인 부분은 모델마다 달랐습니다 |
| [11월 24일, 원인 실험](2026-11-24-g-causal-cue-swap.html) | 원인 실험 | 시스템 프롬프트 문장 하나만 무관한 문장으로 바꿔 새로 학습 | 무관한 문장은 긴 풀이를 켜지 못했습니다. 원래 지시문의 힘이 그 지시문으로 학습해서 생겼다는 절반만 확인됐습니다 |
| 이 글 | 방법 | 표준 SFT와 공개 모델 둘에 문제만 넣고 MATH500 500문항 × 4회 생성, 미리 정한 기준으로 판정 | 표준 SFT는 길이 0.44배에 정답률 유지. 공개 모델 둘은 0.26배, 0.52배이고 하나는 정답률 손해 |

## 연구 질문

| 순서 | 내용 |
|---|---|
| 본 현상 | 표준 SFT는 쉬운 문제에도 길게 풉니다. MATH500 한 문제에 평균 6,576 tokens를 쓰는데 학습 전 모델(Base)은 635 tokens, QFFT는 4,630 tokens입니다. 그런데 평가 때 모델에 넣는 입력은 문제만이 아닙니다. 프롬프트 템플릿(`<|im_start|>system`, `<|im_start|>user` 같은 역할 표시)과 시스템 프롬프트("Please reason step by step, and put your final answer within \boxed{}.")가 문제를 감싸고 있습니다. 표준 SFT는 학습 때도 바로 이 템플릿과 시스템 프롬프트를 긴 풀이와 함께 봤고, QFFT는 학습 때 둘 다 본 적이 없습니다. |
| 든 의문 | 표준 SFT가 길게 푸는 것은 문제 때문인가, 문제를 감싼 입력 때문인가? 나눠서 묻습니다. (1) 시스템 프롬프트 문장이 답 길이에 영향을 주는가. (2) 프롬프트 템플릿이 영향을 주는가. (3) 영향을 주는 부분을 평가 입력에서 빼면 정답률은 유지되는가. 유지된다면 QFFT나 A2처럼 새로 학습하지 않고 그 부분만 빼도 같은 길이와 정답률을 얻는 것 아닌가. (4) 공개 모델과 더 어려운 문제에서도 같은가. |
| 그때까지 안 해 본 것 | 평가 입력의 시스템 프롬프트와 프롬프트 템플릿은 모든 모델에 똑같이 넣는 고정값이어서, 이것을 바꿔 가며 답 길이와 정답률을 잰 적이 없었습니다. QFFT 논문도 학습 쪽만 바꾸고 평가 입력은 그대로 두었습니다. |
| 그래서 한 것 | 같은 표준 SFT, 같은 MATH500 500문제에 입력만 세 가지로 바꿔 넣었습니다. ① 평소 입력(프롬프트 템플릿 + 시스템 프롬프트 + 문제) ② 시스템 프롬프트만 뺀 입력(프롬프트 템플릿 + 문제) ③ 프롬프트 템플릿까지 뺀 입력(문제 문장만). 공개 모델 둘에는 그 모델이 학습 때 본 시스템 프롬프트와 질문 앞의 고정 문장("Return your final response within \boxed{}.")을 뺐습니다. 판정 기준은 결과를 보기 전에 정했고, 정답률이 떨어진 경우에는 답을 직접 읽었습니다. |
| 답 | 시스템 프롬프트와 프롬프트 템플릿 둘 다 영향을 줍니다. 평균 길이는 ① 6,576 tokens, ② 4,899 tokens, ③ 4,221 tokens였습니다. ②에서는 답의 48.7%가 여전히 긴 풀이의 시작 말 "Okay"로 시작했고 ③에서는 0%였습니다. 정답률은 81.0%, 80.9%, 81.4%로 그대로였습니다. ③은 새로 학습한 A2(4,587 tokens, 81.3%), QFFT(4,630 tokens, 81.4%)와 정답률이 같고 더 짧습니다. 공개 모델 둘도 길이가 4분의 1에서 절반으로 줄었지만 한 모델은 정답률이 5.3%p 떨어졌습니다. 읽어 보니 풀이가 틀려서가 아니라, 답을 쓰고도 생성을 끝내지 못하고 같은 줄을 제한 길이까지 되풀이한 답(전체의 7.7%)이 오답으로 세어진 것이었습니다. 가장 어려운 시험(AIME25)에서는 두 공개 모델 모두 정답률이 내려가는 쪽이었습니다. |
| 다음 의문 | 왜 시스템 프롬프트와 프롬프트 템플릿이 영향을 주는가? 학습 때 긴 풀이와 함께 있었기 때문인가? ([원인 실험](2026-11-24-g-causal-cue-swap.html)) 왜 답을 쓰고도 끝내지 못하는가? 어려운 문제에서는 언제 긴 풀이가 필요한가? ([열려 있는 질문](2026-11-25-a-research-questions.html)) |

질문의 사슬 전체는 [연구 질문으로 다시 쓴 QFFT 연구](2026-11-25-a-research-questions.html)에 있습니다.

## 메인 표: Base, SFT, A1, A2, QFFT와 추론 입력을 바꾼 조건

<!-- qfft-main-table-start -->

**표 읽는 법.** 한 줄이 "모델 + 추론 입력" 하나입니다. ACC는 정답률(%), Tokens는 답 하나의 평균 출력 tokens입니다. "구분"이 줄의 뜻입니다. 기준은 학습 방법이 다른 모델들을 표준 평가 그대로 잰 값이고, 굵게 적은 A2와 QFFT가 견줄 상대입니다. 방법은 표준 SFT를 다시 학습하지 않고 추론 입력만 바꾼 값입니다. 문제 글만 넣는 줄이 방법 QOI이고, 시스템 프롬프트만 뺀 줄은 그 부분 적용(프롬프트 템플릿은 남김)입니다. 참고는 같은 입력 변경을 다른 모델에 얹어 본 값입니다. "대기"는 지금 돌고 있는 칸입니다.

| 구분 | 모델 | 추론 입력 | GSM8K ACC | GSM8K Tokens | MATH500 ACC | MATH500 Tokens | AIME25 ACC | AIME25 Tokens |
|---|---|---|---|---|---|---|---|---|
| 기준 | Base | 기본 프롬프트 | 92.0 | 301 | 76.1 | 635 | 8.8 | 1,060 |
| 기준 | SFT | 기본 프롬프트 | 91.6 | 2,060 | 81.0 | 6,576 | 16.7 | 20,574 |
| 기준 | A1 | 기본 프롬프트 | 91.4 | 1,856 | 80.9 | 6,149 | 17.5 | 18,965 |
| 기준 | **A2** | 기본 프롬프트 | **91.6** | **888** | **81.3** | **4,587** | **17.5** | **17,735** |
| 기준 | **QFFT** | 기본 프롬프트 | **92.0** | **831** | **81.4** | **4,630** | **15.4** | **18,133** |
| 방법 (QOI 부분 적용) | SFT | 시스템 프롬프트 제거 | 91.0 | 1,517 | 80.9 | 4,899 | 19.2 | 18,382 |
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

## 한 줄 요약

- **방법:** 긴 풀이를 학습한 모델(SFT)을 다시 학습하지 않습니다. 추론 입력에서 그 모델이 학습 때 긴 풀이와 늘 함께 본 단서(시스템 프롬프트, 사용자 칸의 고정 문장, 프롬프트 템플릿)만 뺍니다.
- **무엇에 쓰는가:** 표준 SFT에 씁니다. 표준 SFT는 QFFT 논문이 비교 기준으로 쓴 모델로, 시스템 프롬프트와 질문, 긴 풀이를 그대로 학습한 모델입니다. A2나 QFFT 위에 얹는 방법이 아닙니다. A2와 QFFT는 학습 방법을 바꿔 새로 학습한 모델이고, 이 방법은 표준 SFT를 그대로 두고 추론 입력만 바꿔 그 둘과 견줍니다(위 메인 표의 "방법" 줄 대 "기준" 줄).
- **얻는 것:** 쉬운 문제는 짧게, 어려운 문제는 길게 풉니다. QFFT가 새로 학습해서 얻는 길이 배분과 같은 모양입니다.
- **왜 맨 위인가:** 지금까지의 후보 가운데 근거가 가장 많이 쌓였고, 다시 학습할 필요가 없습니다. 왜 되는지에 대한 설명은 원인 실험으로 직접 시험했고, 절반만 맞았습니다(아래).
- **첫 결과(11-24 오후):** 표준 SFT에 문제 글만 주면 MATH500 500문항 × 4회에서 길이가 표준 입력의 0.44배 [0.41, 0.46]가 되고, 정답률은 +0.3 [−1.3, +1.9]%p로 미리 정한 기준에서 "못지않음"입니다. 가장 어려운 수준에서도 못지않았습니다.
- **원인 실험 결과(11-25 새벽):** 미리 정한 판정은 "반대"입니다. 학습 때 시스템 프롬프트 자리에 무관한 문장을 넣으면 그 문장은 단서가 되지 않았습니다. 긴 풀이가 지시문에 묶이는 것은 풀이를 서술하는 지시문("Please reason step by step, …")으로 학습했을 때였습니다. 그래서 **이 방법이 통하는 범위는 "지시문을 붙여 학습한 모델"입니다.** 지시문 없이 학습한 R1 증류 모델의 작은 시험은 "안 통함"이었습니다.
- **종합 표시(11-25 낮):** 미리 정한 규칙으로는 **"길이는 줄지만 정답률 손해"**입니다. 시험 ①이 "반대"이고, 공개 모델 OpenThinker-7B가 최대 길이를 32,000 tokens로 늘려 다시 재도 정답률 차 −5.3 [−7.4, −3.2]%p로 "낮음"이기 때문입니다. 그 손해는 답을 쓰고도 끝내지 못한 답에서 나옵니다. 첫 답에서 멈추는 규칙을 붙이면 차는 +0.3 [−1.6, +2.1]%p이고 길이는 0.31배입니다. 이 규칙은 결과를 본 뒤에 정한 것이라 새 표본으로 확인하고 있습니다(아래 "시험 ③ 넷째 결과").
- **가까운 선행(11-25에 원문 확인):** 긴 풀이로 학습하고 추론 때 생각 칸을 비우는 3TF(arXiv 2511.03408)가 방법의 기본 생각과 겹칩니다. 그래서 이 글에서 새로 말할 수 있는 부분은 방법 자체보다 "왜 되는가"의 설명 쪽입니다(아래 "이 방법의 약한 곳").
- **QFFT에 같은 입력을 준 결과(11-25 새벽):** QFFT는 문제 글만 줘도 더 짧아지지 않았고(1.06배) 정답률이 3.7%p 내려갔습니다. 빼낼 학습 단서가 없는 모델에서는 얻을 것이 없고 손해가 납니다. 한편 SFT에서 단서를 뺀 답은 난도 수준마다 QFFT의 표준 사용과 가까운 길이였고 정답률도 같았습니다(80.0% 대 80.3%).
- **공개 모델 첫 결과(11-25 아침):** Bespoke-Stratos-7B는 단서를 빼면 MATH500 500문항에서 길이가 0.26배 [0.25, 0.28]가 됐고, 정답률 차는 −0.1 [−2.1, +1.9]%p로 미리 정한 기준에서 "판정 불가"입니다. 다만 표준 입력 답의 11.4%가 최대 길이(16,384 tokens)에 잘려 오답으로 채점된 비교라서, 이 값으로 "정답률이 같다"고 쓰지 않습니다. 잘린 답을 이어 생성해 다시 잽니다(아래 "시험 ③ 첫 결과").
- **공개 모델 둘째 결과(11-25 아침):** OpenThinker-7B는 단서를 빼면 길이가 0.47배 [0.44, 0.51]가 됐고, 정답률 차는 −4.3 [−6.5, −2.1]%p로 미리 정한 기준에서 "정답률 손해"입니다. 답을 읽어 보니 손해의 큰 부분은 풀이가 틀려서가 아니라, 답을 쓰고도 생성을 끝내지 못해 최대 길이까지 같은 줄을 되풀이한 답(7.9%)에서 나왔습니다. 그 답의 73%는 처음 쓴 답이 정답이었습니다. 첫 답에서 생성을 멈추는 규칙을 붙여 새 표본으로 다시 잽니다(아래 "시험 ③ 둘째 결과").
- **공개 모델 AIME25(11-25 아침):** 가장 어려운 벤치마크에서는 두 공개 모델 모두 단서를 빼면 정답률이 내려가는 방향입니다(20.8% → 15.0%, 22.5% → 15.8%. 30문항이라 방향만 읽음). 표준 입력 답의 절반 넘게가 최대 길이에 잘린 비교라 실제 차는 더 클 수 있습니다. 여기서는 첫 답에서 멈추는 규칙을 걸어도 정답률이 돌아오지 않습니다(아래 "시험 ③ 셋째 결과").
- **새 표본 결과(11-25 오후):** 시드를 바꿔 새로 생성한 답에서도 OpenThinker-7B는 답을 쓰고도 끝내지 못한 답이 9.1%였고 그 69.8%가 정답이었습니다. 첫 답에서 멈추면 정답률 차가 −6.95%p에서 −0.80 [−2.65, +1.05]%p가 됩니다. 현상은 재현됐지만 미리 정한 기준("못지않음"은 하한 −2%p 이상)으로는 판정 불가입니다. 아래 "시험 ③ 다섯째 결과"에 있습니다.
- **아직 확인되지 않은 것:** 표준 SFT에 문제 글만 준 GSM8K와 AIME25의 칸(대기), 시드만 바꾼 학습(대기)입니다. 기준은 아래에 적었습니다. **가능성 확인은 아직 끝나지 않았습니다.**

## 방법

### 실제 입력과 실제 답: 같은 문항 하나

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
- 정답률까지 지키려면 두 가지가 더 필요했습니다. 답을 `\boxed{}`에 넣게 하는 장치(그 지시가 함께 빠지므로)와, 처음 답을 쓴 곳에서 생성을 멈추는 규칙입니다(아래 "시험 ③ 넷째 결과").

### 방법의 세 단계

1. **단서를 찾습니다.** 그 모델의 학습 자료에서 긴 풀이와 늘 함께 있던 입력 요소를 봅니다. 표준 SFT는 시스템 프롬프트 문장("Please reason step by step, …")과 프롬프트 템플릿이고, 공개 모델은 시스템 프롬프트와 사용자 칸 앞에 늘 붙던 고정 문장입니다.
2. **추론 입력에서 그 단서를 뺍니다.** 모델과 가중치는 그대로입니다.
3. **길게 풀게 하고 싶을 때는 단서를 다시 넣습니다.** 같은 모델이 두 방식으로 풉니다.

QFFT는 학습 자료에서 질문을 지우고 새로 학습해 같은 모양을 얻습니다. 이 방법은 이미 있는 모델에 그대로 씁니다.

**쓸 수 있는 모델(11-25에 좁힘).** 학습 입력에 풀이를 서술하는 지시문이 있던 모델입니다. 그런 모델에서는 긴 풀이가 지시문에 묶여 있어 지시문을 빼면 꺼집니다. 무관한 문장을 넣었거나 시스템 프롬프트 없이 학습한 모델은 긴 풀이가 프롬프트 템플릿에 묶여 있어 뗄 지시문이 없습니다(아래 "시험 ① 결과와 방법의 범위").

<figure class="xp">
<a href="../uploads/qfft/figures/2026-11-24-h-drop-training-cues-method/same-model-two-inputs.png"><img src="../uploads/qfft/figures/2026-11-24-h-drop-training-cues-method/same-model-two-inputs.png" alt="두 열 비교. 같은 SFT 모델에 표준 입력을 주면 긴 풀이 비율이 GSM8K 87%, MATH500 90%, AIME25 100%로 늘 길게 푼다. 단서를 뺀 입력(문제 글만)을 주면 14%, 27%, 90%로 쉬운 문제는 짧게, 어려운 문제는 길게 푼다. 남는 비율은 1.00, 0.98, 1.00에서 0.08, 0.49, 0.87이 된다." style="display:block;width:100%;height:auto;border-radius:6px"></a>
<figcaption class="xp-cap">그림 1. 위 예시를 벤치마크 전체로 요약한 개념 그림입니다(100문항 크기의 값). 방법은 입력에서 학습 때의 단서를 빼는 것뿐입니다. 쉬운 문제에서만 긴 풀이가 꺼지고 어려운 문제에서는 남습니다. 그림을 누르면 원본 크기로 열립니다.</figcaption>
</figure>

## 왜 궁금했나

- QFFT 논문은 "질문을 지우고 학습하면 모델이 상황에 맞게 짧은 풀이와 긴 풀이를 고른다"고 보고했습니다.
- 그런데 평범하게 학습한 SFT도 평가 입력에서 시스템 프롬프트를 빼면 짧아졌습니다. 문제 글만 주면 QFFT와 거의 같은 길이 배분이 됐습니다.
- 그렇다면 QFFT의 효과는 "새로 배운 능력"이 아니라 "긴 풀이를 켜는 단서가 평가 입력에 없어서" 생긴 것일 수 있습니다. 이 읽기가 맞다면 새로 학습하지 않고도 같은 것을 얻습니다.

## 용어 풀이

| 용어 | 뜻 | 이 글에서의 예 |
|---|---|---|
| SFT | 긴 풀이가 달린 문제 817개(LIMO)로 평범하게 파인튜닝한 모델 | 표준 입력에서는 쉬운 문제도 길게 풂 |
| QFFT | 학습 자료에서 질문을 지우고 풀이만으로 파인튜닝한 모델 | 쉬운 문제는 짧게, 어려운 문제는 길게 풂 |
| A1 | 질문은 지우고 시스템 프롬프트는 남겨 학습한 모델 | 시스템 프롬프트가 있으면 길게, 없으면 QFFT처럼 풂 |
| 단서 | 학습 때 긴 풀이와 늘 함께 있던 입력 요소 | 시스템 프롬프트 문장 |
| 남는 비율 | 파인튜닝으로 늘어난 길이 가운데 그 조건에서 남아 있는 몫 | 0이면 원래 모델과 같고, 1이면 SFT가 표준 입력으로 풀 때와 같음 |
| 긴 풀이 비율 | 되돌아보는 표현이 든 긴 풀이로 쓴 답의 비율 | QFFT 논문의 분석 코드 기준 그대로 |
| ACC | 정답률. 대괄호는 95% 구간 | −0.4 [−1.8, +1.0]%p |
| 최대 길이 | 답 하나에 허용한 tokens의 한도. 한도까지 쓰고도 끝나지 않은 답은 오답으로 셈 | 공개 모델의 시험은 16,384, 직접 학습한 모델의 시험은 32,000 |
| 이어 생성 | 한도에 걸려 끊긴 답을 그 글 그대로 다시 넣고 뒤를 이어 쓰게 하는 것 | 끊긴 답 228개를 합쳐 32,000 tokens까지 |
| 끝내지 못한 답 | 최종 답을 쓰고도 생성을 끝내지 못해 최대 길이까지 간 답 | 정답 9를 쓴 뒤 "Final Answer" 줄을 16,384 tokens까지 되풀이 |
| 첫 답에서 멈추기 | 첫 최종 답 표시(`\boxed{}`)가 닫히면 생성을 멈추는 규칙 | 위의 답이 294 tokens에서 끝남 |

## 지금까지의 근거

**표 읽는 법.** 한 줄이 "모델 + 단서를 뺀 방식" 하나입니다. 길이는 표준 입력 대비 토큰 비(1보다 작으면 짧아짐)이고, 정답률 차는 단서를 뺀 쪽에서 견줄 쪽을 뺀 값입니다. "크기" 칸이 작은 줄은 정답률을 판정할 수 없는 줄입니다.

| 모델 | 뺀 단서 | 길이 | 정답률 | 크기 |
|---|---|---|---|---|
| SFT | 시스템 프롬프트 | 0.60배 [0.57, 0.64] | 표준 입력 대비 +0.4 [−1.6, +2.2]%p (바로잡은 채점) | MATH500 500문항 × 4회 |
| A1 | 시스템 프롬프트 | QFFT의 0.74배 | QFFT 표준 대비 −0.4 [−1.8, +1.0]%p ("못지않음") | MATH500 500문항 |
| SFT | 시스템 프롬프트와 프롬프트 템플릿(문제 글만) | 0.44배 [0.41, 0.46] | 표준 입력 대비 +0.3 [−1.3, +1.9]%p ("못지않음", 공식 채점 그대로) | MATH500 500문항 × 4회 (11-24 새 결과) |
| SFT | 시스템 프롬프트와 프롬프트 템플릿(문제 글만) | 남는 비율 0.08, 0.49, 0.87 (GSM8K, MATH500, AIME25) | MATH500 81% 대 82% | 100문항 × 2회 (판정 불가) |
| Bespoke-Stratos-7B (공개 모델) | 시스템 프롬프트와 고정 문장 | 0.29배 [0.25, 0.32] | −0.5 [−7.5, +5.5]%p | 100문항 × 2회 (판정 불가) |
| OpenThinker-7B (공개 모델) | 시스템 프롬프트와 고정 문장 | 0.40배 [0.34, 0.48] | −1.5 [−8.5, +5.5]%p | 100문항 × 2회 (판정 불가) |

- 길이 쪽은 효과가 커서 작은 크기로도 판정이 났습니다. 정답률은 500문항인 세 줄에서만 판정이 났습니다.
- 문제 글만 주었을 때의 남는 비율은 QFFT가 0.16, 0.55, 0.90이고 SFT가 0.08, 0.49, 0.87입니다. 따로 학습한 여섯 모델이 이 입력에서 같은 모양으로 모였습니다([단서 사다리 글](2026-11-24-d-cue-ladder.html)).
- 공개 모델 둘도 학습 때의 단서를 모두 빼면 생각 형식이 100%에서 0%가 됩니다([공개 모델 글](2026-11-24-a-public-model-prompt-gate.html)).

## 가능성 확인: 네 가지 시험과 미리 정한 기준

**표 읽는 법.** "기준"은 결과를 보기 전에 연구 기록에 적은 것입니다. 네 시험이 모두 끝나면 맨 아래의 종합 표시를 붙입니다.

| 시험 | 묻는 것 | 크기 | 미리 정한 기준 | 상태 |
|---|---|---|---|---|
| ① 원인 | 학습 때의 문장만 바꿔 학습하면 켜는 단서가 따라 바뀌는가 | 새 학습 2회, 평가 100문항 | [원인 실험 글](2026-11-24-g-causal-cue-swap.html)의 "닫힘", "반대", "부분" | **반대**(11-25). 무관한 문장은 단서가 되지 않음. 원래 지시문의 힘이 그 지시문으로 학습해서 생겼다는 절반만 확인. 시드만 바꾼 학습은 11-25 저녁 |
| ② 직접 학습한 모델, 전체 크기 | 문제 글만 준 SFT가 표준 입력보다 짧으면서 정답률이 못지않은가 | SFT, QFFT, A1에 MATH500 500문항 × 4회, GSM8K 300문항 × 2회, AIME25 30문항 × 8회 | 길이: 토큰 비 구간 위쪽이 0.90 미만이면 "더 짧음". 정답률: 차의 구간 아래쪽이 −2%p 이상이면 "못지않음", 위쪽이 −2%p 미만이면 "낮음" | SFT와 QFFT의 MATH500 칸 판정 남(아래). 나머지 일곱 칸 대기 |
| ③ 공개 모델, 전체 크기 | 공개 모델 둘에서도 같은가 | 위와 같은 문항, 표준 입력 대 단서를 모두 뺀 입력 | "더 짧음"이고 "못지않음"이면 "방법이 통함", "더 짧음"이고 "낮음"이면 "정답률 손해" | MATH500 판정 끝(최대 길이를 32,000 tokens로 늘린 값이 주 값). Bespoke-Stratos-7B: 0.26배, −2.0 [−4.0, −0.1]%p로 **"판정 불가"**. OpenThinker-7B: 0.52배, −5.3 [−7.4, −3.2]%p로 **"정답률 손해"**. 첫 답에서 멈추는 규칙을 붙이면 OpenThinker-7B는 0.31배, +0.3 [−1.6, +2.1]%p(결과를 본 뒤 정한 규칙이라 새 표본으로 확인 중). AIME25는 두 모델 모두 정답률이 내려가는 방향. 아래 넷째 결과 |
| ④ 어려운 문제 | 단서를 빼면 어려운 문제에서 손해를 보는가 | ②와 ③의 MATH500 Level 5 (134문항 × 4회) | 정답률 차의 구간 아래쪽이 −5%p 이상이면 "못지않음", 위쪽이 −5%p 미만이면 "손해" | 표준 SFT에서는 "못지않음"(아래). 공개 모델은 최대 길이를 늘린 값으로 Bespoke-Stratos-7B −4.9 [−9.1, −0.2]%p, OpenThinker-7B −8.4 [−13.1, −3.7]%p로 둘 다 "판정 불가"이고 음수 쪽 |

**종합 표시(미리 정함).**

- ①이 "닫힘", ②에서 SFT가 "더 짧음"과 "못지않음", ③에서 두 모델 가운데 하나 이상이 "방법이 통함"이면 **"가능성 확인"**입니다.
- ②나 ③에서 정답률이 "낮음"으로 나오면 **"길이는 줄지만 정답률 손해"**로 적습니다. 그때는 이 방법을 "같은 정답률에서의 절감"이 아니라 "정답률과 맞바꾸는 절감"으로 고쳐 씁니다.
- 그 밖은 **"일부 확인"**으로 적고 어느 시험이 모자랐는지 밝힙니다.
- **지금 상태(11-25 낮):** ①이 "반대"이고 ③에서 OpenThinker-7B의 정답률이 최대 길이를 늘린 값으로도 "낮음"이므로, 종합 표시는 **"길이는 줄지만 정답률 손해"**입니다. 미리 정한 대로 이 방법을 "같은 정답률에서의 절감"이 아니라 "정답률과 맞바꾸는 절감"으로 적습니다. 다만 손해가 나온 곳이 답을 쓰고도 끝내지 못한 답이라, 첫 답에서 멈추는 규칙을 붙인 값을 나란히 적습니다(OpenThinker-7B +0.3 [−1.6, +2.1]%p, Bespoke-Stratos-7B −1.8 [−3.8, +0.1]%p). 이 값은 새 표본으로 확인한 뒤에 방법의 값으로 씁니다. 어려운 문제(Level 5, AIME25)에서는 멈추는 규칙을 붙여도 음수 쪽입니다.

## 시험 ① 결과와 방법의 범위 (11월 25일)

**표 읽는 법.** 한 줄이 모델 하나입니다. "학습 입력의 시스템 프롬프트"는 그 모델이 학습 때 본 것이고, "단서를 뺐을 때"는 추론 입력에서 그것을 뺀 결과입니다. 길이는 빼기 전 대비 토큰 비입니다(1보다 작으면 짧아짐). 빗금 앞은 GSM8K, 뒤는 MATH500입니다.

| 모델 | 학습 입력의 시스템 프롬프트 | 단서를 뺐을 때 | 읽기 |
|---|---|---|---|
| 표준 SFT | 풀이를 서술하는 지시문 S | 프롬프트 템플릿에서 S만 빼면 0.68배 / 0.61배. 문제 글만 주면 MATH500 0.44배이고 정답률 못지않음(500문항) | 방법이 통함 |
| 새 단서 SFT (원인 실험에서 새로 학습) | 무관한 문장 X | 프롬프트 템플릿에서 X를 빼도 0.95배 / 0.99배로 그대로. 프롬프트 템플릿까지 빼면 쉬운 문제는 짧아지지만 상자 없는 답이 늘어 GSM8K 정답률 57% | 뗄 지시문이 없음 |
| 시스템 프롬프트 없이 학습한 SFT | 없음 | 프롬프트 템플릿만으로 늘 길게 풂(남는 비율 0.88 / 0.99) | 뗄 지시문이 없음 |
| QFFT (질문을 지우고 풀이만으로 학습) | 없음. 질문도 없음 | 문제 글만 주면 MATH500 1.06배 [0.99, 1.14]로 짧아지지 않고 정답률 −3.7 [−5.4, −2.0]%p(500문항) | 뗄 지시문이 없음. 표준 사용이 이미 짧고, 더 빼면 손해 |
| DeepSeek-R1-Distill-Qwen-7B (공개 모델) | 없음 | 평가 때 붙인 S를 빼면 0.69배 / 0.91배. 문제 글만 주면 MATH500 0.73배이지만 정답률 −12.5 [−18.0, −7.5]%p | 안 통함 (100문항 스모크, 미리 정한 기준) |
| Bespoke-Stratos-7B (공개 모델) | 긴 서술형 지시문 | 지시문과 고정 문장을 빼면 MATH500 0.26배 [0.25, 0.28], 정답률 −0.1 [−2.1, +1.9]%p(500문항, 최대 16,384 tokens. 표준 입력 답의 11.4%가 그 길이에 잘림) | 길이는 줄어듦. 정답률은 판정 불가이고 표준 입력에 불리한 비교라 다시 재는 중 |
| OpenThinker-7B (공개 모델) | 긴 서술형 지시문 | 지시문과 고정 문장을 빼면 MATH500 0.47배 [0.44, 0.51], 정답률 −4.3 [−6.5, −2.1]%p(500문항, 최대 16,384 tokens). 단서를 뺀 답의 7.9%가 답을 쓰고도 생성을 끝내지 못함 | 길이는 줄지만 미리 정한 기준으로 정답률 손해. 손해의 큰 부분이 끝내지 못한 답이라 멈춤 규칙을 붙여 다시 재는 중 |

- 원인 실험의 자세한 값은 [원인 실험 글](2026-11-24-g-causal-cue-swap.html)에 있습니다. 미리 적은 예측("무관한 문장도 학습 때 넣으면 단서가 된다")은 틀렸습니다.
- 확인된 절반: 표준 SFT에서 S가 긴 풀이를 켜는 힘(GSM8K 남는 비율 +0.89)은 대부분 S로 학습해서 생긴 것입니다. S로 학습하지 않은 새 모델에서 S는 +0.23만 켭니다.
- R1 증류 모델에서 정답률이 내려간 까닭은 답을 읽어 확인했습니다. 문제 글만 주면 생각을 여는 표지 없이 생각 글을 쓰고, 상자 없이 끝나거나 최대 길이까지 가는 답이 늘었습니다(MATH500 오답 38개 가운데 상자 없는 답 17개).
- 그래서 이 방법을 "긴 풀이를 학습한 모든 모델"의 방법으로 쓰지 않습니다. **"학습 입력에 풀이를 서술하는 지시문이 있던 모델"의 방법으로 씁니다.** 표의 마지막 두 줄(공개 모델 둘)이 이 범위에 드는 공개 모델입니다. 두 모델의 전체 크기 결과는 아래 "시험 ③ 첫 결과"와 "시험 ③ 둘째 결과"에 적었습니다.
- 이 범위 나누기에는 한계가 있습니다. 직접 학습해서 견준 서술형 지시문은 S 하나입니다. 다른 지시문으로 학습한 모델은 공개 모델뿐이고, 그 모델들은 자료와 설정도 다릅니다.

## 시험 ② 첫 결과: 표준 SFT, MATH500 500문항 × 4회

**표 읽는 법.** 같은 SFT 모델에 문제 글만 준 답 2,000개를, 표준 입력으로 16번 푼 저장 결과와 같은 문항끼리 견줬습니다. "길이"는 문항마다 낸 토큰 비의 기하 평균입니다(1보다 작으면 짧아짐). 정답률 차는 문제 글만 준 쪽에서 견줄 쪽을 뺀 값입니다. 판정은 결과 전에 적은 기준 그대로입니다.

| 견준 것 | 값 (95% 구간) | 판정 |
|---|---|---|
| 길이: 문제 글만 ÷ 표준 입력 | 0.44배 [0.41, 0.46] | 더 짧음 |
| 정답률: 문제 글만 − 표준 입력 | +0.3 [−1.3, +1.9]%p | 못지않음 |
| 정답률: 문제 글만 − QFFT의 표준 평가 | −0.3 [−1.9, +1.2]%p | 못지않음 |
| 길이: 문제 글만 ÷ QFFT의 표준 평가 | 0.89배 [0.84, 0.93] | 판정 불가 |
| 가장 어려운 수준(Level 5, 134문항)의 정답률: 문제 글만 − 표준 입력 | +0.8 [−2.7, +4.5]%p | 어려운 문제에서도 못지않음 |

- 정답률은 80.0%이고 답 상자가 있는 답은 97.7%였습니다. 공식 채점 그대로의 값입니다.
- 쓴 tokens의 총량으로 견주면 표준 입력의 0.64배 [0.60, 0.68]입니다. 문항 기준(0.44배)보다 덜 줄어 보이는 까닭은 총량의 대부분을 긴 답이 차지하기 때문입니다. 비용을 말할 때는 0.64배를 씁니다.

**수준별 표 읽는 법.** 한 줄이 MATH500의 난도 수준 하나입니다. 쉬운 수준일수록 많이 줄고, 어려운 수준에서는 긴 풀이가 남습니다. 수준별 값은 미리 정한 판정이 아니라 덧붙여 계산한 값입니다.

| 수준 | 문항 | 길이(문항 기준) | 총량 | 정답률 차(표준 입력 대비) | 긴 풀이 비율 |
|---|---|---|---|---|---|
| Level 1 | 43 | 0.32배 [0.27, 0.38] | 0.44배 | −3.8 [−9.2, +0.9]%p | 14% |
| Level 2 | 90 | 0.44배 [0.38, 0.50] | 0.64배 | −1.4 [−5.2, +2.1]%p | 25% |
| Level 3 | 105 | 0.43배 [0.38, 0.49] | 0.61배 | +1.4 [−1.5, +3.8]%p | 25% |
| Level 4 | 128 | 0.44배 [0.39, 0.49] | 0.62배 | +1.5 [−2.1, +4.7]%p | 37% |
| Level 5 | 134 | 0.49배 [0.44, 0.54] | 0.68배 | +0.8 [−2.7, +4.5]%p | 56% |

**조심해서 읽을 곳.**

- 앞선 100문항 실험에 쓰지 않은 400문항만으로 보면 QFFT의 표준 평가 대비 −0.5 [−2.3, +1.2]%p입니다. 구간 아래쪽이 기준(−2%p)에 0.3%p 못 미쳐 400문항만으로는 "판정 불가"입니다. 500문항 전체로는 판정이 났습니다.
- 가장 쉬운 수준(Level 1, 43문항)의 정답률 차는 −3.8 [−9.2, +0.9]%p입니다. 미리 정한 판정이 아니고 문항이 적어 우연일 수 있습니다. 오답 18개가 8문항에 몰려 있었습니다. QFFT의 칸에서도 가장 쉬운 수준이 낮았고(−6.0 [−11.5, −1.0]%p), 답을 읽어 보니 문제 문장을 이어 쓰는 답이 들어 있었습니다(다음 절).
- 최대 길이(32,000 tokens)까지 가고도 끝나지 않은 답이 2.1%였습니다. 표준 입력의 저장 결과에서는 3.4%였으므로 이 입력에서 새로 생긴 문제는 아닙니다.
- 학습은 1회, 모델은 하나, 벤치마크는 MATH500 하나입니다. QFFT의 MATH500 칸은 다음 절에 있습니다. A1의 칸, GSM8K와 AIME25의 칸은 아직 돌지 않았습니다.

## 시험 ② 둘째 결과: QFFT, MATH500 500문항 × 4회 (11월 25일)

**표 읽는 법.** 한 줄이 MATH500의 난도 수준 하나이고, 한 칸에 "평균 tokens / 정답률"을 적었습니다. "표준"은 그 모델을 평소대로 쓴 저장 결과(16번 풀이)이고, "문제 글만"은 프롬프트 템플릿과 시스템 프롬프트를 모두 뺀 입력(4번 풀이)입니다. SFT의 "문제 글만" 칸과 QFFT의 "표준" 칸을 나란히 보면 됩니다. 수준별 값은 미리 정한 판정이 아니라 덧붙여 계산한 값입니다.

| 수준 | SFT 표준 | SFT 문제 글만 | QFFT 표준 | QFFT 문제 글만 |
|---|---|---|---|---|
| 전체 (500문항) | 6,576 / 79.7% | 4,221 / 80.0% | 4,630 / 80.3% | 5,046 / 76.6% |
| Level 1 (43) | 2,646 / 93.3% | 1,176 / 89.5% | 1,284 / 94.9% | 1,689 / 89.0% |
| Level 2 (90) | 3,092 / 92.5% | 1,975 / 91.1% | 1,654 / 92.7% | 2,581 / 88.1% |
| Level 3 (105) | 4,538 / 91.0% | 2,758 / 92.4% | 2,988 / 91.0% | 3,568 / 85.5% |
| Level 4 (128) | 6,961 / 76.9% | 4,332 / 78.3% | 4,868 / 77.1% | 5,054 / 74.4% |
| Level 5 (134) | 11,405 / 60.4% | 7,746 / 61.2% | 8,762 / 61.8% | 8,931 / 60.3% |

**판정 표 읽는 법.** 기준은 첫 결과와 같습니다. 길이는 문항마다 낸 토큰 비의 기하 평균이고, 정답률 차는 앞쪽에서 뒤쪽을 뺀 값입니다.

| 견준 것 | 값 (95% 구간) | 판정 |
|---|---|---|
| QFFT의 길이: 문제 글만 ÷ 표준 | 1.06배 [0.99, 1.14] | 판정 불가(짧아지지 않음) |
| QFFT의 정답률: 문제 글만 − 표준 | −3.7 [−5.4, −2.0]%p | 낮음(경계) |
| 정답률: SFT 문제 글만 − QFFT 문제 글만 | +3.4 [+1.5, +5.3]%p | 못지않음 |
| 길이: SFT 문제 글만 ÷ QFFT 문제 글만 | 0.83배 [0.77, 0.89] | 더 짧음 |

- **SFT에서 단서를 빼면 QFFT의 표준 사용과 같은 자리에 옵니다.** 수준마다 길이가 가깝고 전체 정답률도 같습니다(80.0% 대 80.3%, 첫 결과의 판정 "못지않음"). 두 모델을 견준 관찰입니다.
- **QFFT는 문제 글만 줘도 더 짧아지지 않았고 정답률이 내려갔습니다.** QFFT의 표준 사용은 이미 짧은 쪽이라 더 뺄 것이 없는 것으로 읽습니다. 위 범위 표의 "뗄 지시문이 없음" 줄들과 같은 방향입니다.
- **"경계"라고 적은 까닭.** 정답률 차의 구간 위쪽(−2.01%p)이 기준(−2%p)에 붙어 있습니다. 답 상자 없이 끝난 답 18개를 직접 읽어 최종 답이 맞는 4개를 정답으로 넣으면 −3.4 [−5.2, −1.9]%p가 되어 "판정 불가"입니다. 정답률이 내려간 것은 분명하고, 2%p를 넘는 손해인지는 경계입니다.
- **손실이 나온 곳.** 3.7%p 가운데 2.3%p가 최대 길이(32,000 tokens)까지 가고도 끝나지 않은 답 82개(4.1%)에서 나왔습니다. QFFT의 표준 평가에서는 2.4%였습니다. 82개 가운데 56개는 같은 글의 되풀이였습니다. 직접 읽은 답에는 웹 문서처럼 다른 질문과 광고 문구를 이어 쓴 답, 풀이를 마친 뒤 같은 답 상자를 끝없이 되풀이한 답이 있었습니다. SFT는 반대로 이런 답이 줄었습니다(3.4% → 2.1%).
- **문제 이어 쓰기.** 프롬프트 템플릿이 없으면 모델이 문제 문장 뒤에 문장을 덧붙이고 시작하는 답이 생깁니다(첫 문장이 물음표로 끝나거나 문제의 끝 문장으로 시작하는 답을 세어 QFFT 3.1%, SFT 1.8%. 이 답들의 정답률은 같은 문항의 표준 입력보다 약 21%p 낮았습니다. 처음에는 7.7%, 5.2%로 적었는데, 세는 규칙이 문제를 다시 적고 푸는 정상 풀이까지 세고 있어 11월 25일 아침에 고쳤습니다). 예: 문제는 하루에 필요한 열량이 몇 칼로리인지를 물었는데(정답 2000), SFT가 "하루 2,500칼로리가 필요한 사람은 이 통조림을 몇 개 먹어야 하나"라는 없던 질문을 덧붙이고 그 질문에 답했습니다(낸 답 63). 가장 쉬운 수준의 정답률이 두 모델에서 모두 낮게 나온 데에는 이 유형이 들어 있습니다.
- **채점에서 찾은 문제.** 공식 채점기가 채점 순서에 따라 답 1개(평면의 방정식을 다른 꼴로 적은 답)를 다르게 판정했습니다. 한 칸에서 0.05%p입니다. 위의 "경계" 판정에만 영향이 있어 두 값을 함께 적었습니다.

## 시험 ③ 첫 결과: 공개 모델 Bespoke-Stratos-7B, MATH500 500문항 × 4회 (11월 25일)

**무엇을 했나.** 공개된 긴 추론 모델 Bespoke-Stratos-7B에 같은 500문항을 두 가지 입력으로 줬습니다. 표준 입력은 그 모델이 학습 때 본 긴 시스템 프롬프트와 사용자 칸의 고정 문장("Return your final response within \boxed{}.")이 붙은 입력입니다. 단서를 뺀 입력은 사용자 칸에 문제만 넣은 입력입니다. 프롬프트 템플릿은 두 입력 모두 그대로입니다. 모델은 다시 학습하지 않았습니다. 최대 길이는 답 하나에 16,384 tokens입니다.

**실험 예시.** 실제 문항 세 개입니다. 문항마다 네 번씩 풀게 했습니다.

| 문항 | 표준 입력 | 단서를 뺀 입력 |
|---|---|---|
| Level 1: 2^8 = 4^x에서 x는? 정답 4 | 769–1,322 tokens, 네 번 정답 | 234–250 tokens, 네 번 정답 |
| Level 4: 평행사변형의 세 꼭짓점이 (5, 3), (6, 8), (7, 4)이고 나머지 한 점이 (x, y), x > 7일 때 x + y는? 정답 17 | 네 번 모두 최대 길이에 닿아 답을 내지 못함 | 835–1,293 tokens, 네 번 정답 |
| Level 5: 5차 다항식 p(x)가 n = 2, …, 7에서 p(n) = n/(n² − 1)일 때 p(8)은? 정답 3/56 | 세 번은 최대 길이에 닿음, 한 번은 9,309 tokens로 정답 | 2,161–6,109 tokens, 네 번 오답 |

첫 줄은 방법이 겨냥한 경우입니다. 둘째 줄은 표준 입력이 길게 헤매는 문항을 단서 없는 입력이 짧게 맞힌 경우입니다. 셋째 줄은 반대로, 길게 풀어야 맞는 문항을 단서 없는 입력이 짧게 풀다 틀린 경우입니다.

**표 읽는 법.** 한 줄이 입력 하나입니다. "생각 형식"은 그 모델이 학습한 생각 표지로 시작한 답의 비율입니다. "최대 길이에 닿은 답"은 16,384 tokens까지 쓰고도 끝나지 않은 답이고, 채점에서는 모두 오답으로 셉니다.

| 입력 | 평균 길이 (tokens) | 생각 형식 | 긴 풀이 비율 | ACC | 최대 길이에 닿은 답 |
|---|---|---|---|---|---|
| 표준 입력 | 5,151 | 100% | 87.1% | 79.15% (1,583/2,000) | 11.4% (228개) |
| 단서를 뺀 입력 | 1,632 | 0% | 8.5% | 79.10% (1,582/2,000) | 2.6% (52개) |

| 견준 것 | 값 (95% 구간) | 미리 정한 판정 |
|---|---|---|
| 길이: 단서를 뺀 입력 ÷ 표준 입력 | 0.26배 [0.25, 0.28] | 더 짧음 |
| 정답률: 단서를 뺀 입력 − 표준 입력 | −0.1 [−2.1, +1.9]%p | 판정 불가 (구간 아래쪽이 기준 −2%p를 0.1%p 넘음) |
| 가장 어려운 수준(Level 5, 134문항)의 정답률 차 | −1.1 [−5.4, +3.4]%p | 판정 불가 |

- **길이는 난도와 상관없이 4분의 1쯤으로 줄었습니다.** 수준별 비는 0.24, 0.29, 0.24, 0.26, 0.28배입니다. 단서를 빼면 생각 형식이 한 번도 나오지 않고(2,000개 가운데 0개) 바로 풀이를 씁니다. 표준 SFT처럼 쉬운 문제에서 더 많이 줄어드는 모양이 아니라 모든 수준에서 비슷하게 줄어듭니다.
- **정답률 값은 그대로 믿기 어렵습니다.** 표준 입력 답의 11.4%가 최대 길이에 닿아 오답으로 채점됐습니다. 가장 어려운 수준에서는 네 개 가운데 하나꼴입니다(25.9%). 이 228개 가운데 같은 글을 되풀이하던 답은 45개뿐이고, 나머지는 풀이를 이어 가던 중에 끊겼습니다. 최대 길이가 더 길었다면 그 가운데 일부는 맞았을 것입니다.
- **얼마나 달라질 수 있나.** 끊긴 답이 같은 문항의 끝난 답만큼 맞는다고 놓으면 표준 입력의 정답률은 84.0%가 되고 차는 −4.9 [−7.0, −2.7]%p입니다. 끊긴 답이 모두 틀린다고 놓은 값이 위 표의 −0.1%p입니다. 실제 값은 두 값 사이에 있습니다.
- **그래서 이 결과로 "공개 모델에서도 정답률이 유지된다"고 쓰지 않습니다.** 지금 말할 수 있는 것은 길이가 줄어든다는 것까지입니다.
- **다음.** 최대 길이에 닿은 답만 이어서 생성해(답 하나에 합쳐 32,000 tokens까지, 직접 학습한 모델의 시험과 같은 길이) 같은 기준으로 다시 판정합니다. 결과를 보기 전에 적은 예측은 "표준 입력의 정답률이 81–84%로 오르고 차는 −2에서 −5%p, 판정은 낮음 또는 판정 불가"입니다. 최대 길이를 결과를 본 뒤에 늘리는 것이므로 처음 판정(위 표)과 함께 적겠습니다.
- 모델 카드에 적힌 이 모델의 MATH500 값은 82.0(만든 곳의 카드)과 79.6(다른 공개 모델의 카드에 실린 값)입니다. 두 카드 모두 평가의 최대 길이는 적지 않았습니다.
- 프롬프트 템플릿이 남아 있어서, 문제 글만 넣은 입력에서 보인 "문제 이어 쓰기"는 한 건도 없었습니다.

## 시험 ③ 둘째 결과: 공개 모델 OpenThinker-7B, MATH500 500문항 × 4회 (11월 25일)

**무엇을 했나.** 두 번째 공개 모델 OpenThinker-7B에 같은 500문항을 같은 두 입력으로 줬습니다. 표준 입력은 그 모델이 학습 때 본 긴 시스템 프롬프트와 사용자 칸의 고정 문장이 붙은 입력이고, 단서를 뺀 입력은 사용자 칸에 문제만 넣은 입력입니다. 설정은 위 첫 결과와 모두 같습니다(최대 길이 16,384 tokens).

**실험 예시.** 실제 문항 세 개입니다. 문항마다 네 번씩 풀게 했습니다.

| 문항 | 표준 입력 | 단서를 뺀 입력 |
|---|---|---|
| Level 3: 196의 양의 약수는 몇 개인가? 정답 9 | 1,485–2,019 tokens, 네 번 정답 | 한 번은 557 tokens로 정답. 세 번은 294–460 tokens 지점에서 정답 9를 쓰고도 끝내지 못하고, 같은 줄을 되풀이하다 최대 길이에 닿음 |
| Level 4: 점근선이 y = 2x − 3과 y = 17 − 2x이고 점 (4, 7)을 지나는 쌍곡선의 두 초점 사이 거리는? 정답 2√5 | 2,968–4,074 tokens, 세 번 정답 | 두 번은 1,415와 1,538 tokens로 정답. 두 번은 답을 쓴 뒤 끝내지 못함(한 번은 쓴 답이 정답, 한 번은 오답) |
| Level 5: 2 × 3 × 4 × 5 + 1에 괄호를 넣어 만들 수 있는 값은 몇 가지인가? 정답 4 | 네 번 모두 경우를 세다가 최대 길이에 닿음 | 두 번은 8,626과 13,068 tokens로 끝났지만 오답, 두 번은 최대 길이에 닿음 |

첫 줄이 이 모델에서 새로 보인 모양입니다. 답은 짧게 맞혔는데 생성을 끝내지 못했습니다. 채점 규칙은 최대 길이에 닿은 답을 내용과 무관하게 오답으로 세므로, 그 세 번은 오답입니다. 셋째 줄은 표준 입력 쪽이 풀이 중에 끊긴 경우입니다.

**첫 줄의 실제 입력과 실제 답.** 공개 모델 OpenThinker-7B에 실제로 넣은 입력과 저장된 실제 출력입니다. 문항은 MATH500의 Level 3 문제이고 정답은 9입니다. 시스템 프롬프트는 1,312자라 가운데를 줄였습니다.

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

**표 읽는 법.** 위 첫 결과의 표와 같습니다. 한 줄이 입력 하나이고, "최대 길이에 닿은 답"은 채점에서 모두 오답입니다.

| 입력 | 평균 길이 (tokens) | 생각 형식 | 긴 풀이 비율 | ACC | 최대 길이에 닿은 답 |
|---|---|---|---|---|---|
| 표준 입력 | 4,764 | 100% | 93.0% | 82.45% (1,649/2,000) | 7.0% (141개) |
| 단서를 뺀 입력 | 3,336 | 0.4% (7개) | 24.3% | 78.10% (1,562/2,000) | 9.6% (192개) |

| 견준 것 | 값 (95% 구간) | 미리 정한 판정 |
|---|---|---|
| 길이: 단서를 뺀 입력 ÷ 표준 입력 | 0.47배 [0.44, 0.51] | 더 짧음 |
| 정답률: 단서를 뺀 입력 − 표준 입력 | −4.3 [−6.5, −2.1]%p | 낮음 |
| 방법 판정 | | 정답률 손해 |
| 가장 어려운 수준(Level 5, 134문항)의 정답률 차 | −5.4 [−9.9, −0.9]%p | 판정 불가 |

- **미리 정한 판정은 "정답률 손해"입니다.** 길이는 절반 아래로 줄었지만 정답률이 4.3%p 낮았습니다. 재추출을 달리해도 세 번 모두 같은 판정이었습니다. 이 값을 그대로 적습니다.
- 수준별 길이 비는 0.40, 0.44, 0.48, 0.45, 0.55배입니다. 정답률 손해는 쉬운 수준에서도 나왔습니다(Level 2에서 −7.2%p, Level 3에서 −5.7%p). 쉬운 문제를 짧게 풀다 틀렸다고 보기 어려운 모양이어서 답을 직접 읽었습니다.

### 손해가 나온 곳: 답을 쓰고도 끝내지 못한 답 (결과를 본 뒤의 분석)

**표 읽는 법.** 최대 길이에 닿은 답을 내용으로 나눴습니다. "답"은 최종 답 표시 `\boxed{…}`가 있다는 뜻입니다.

| 최대 길이에 닿은 답 | 표준 입력 141개 | 단서를 뺀 입력 192개 |
|---|---|---|
| 답 없이 풀이를 이어 가던 답 | 121 | 20 |
| 답 없이 같은 글을 되풀이한 답 | 16 | 14 |
| 답을 쓴 뒤 같은 줄을 되풀이한 답 | 0 | 148 |
| 답을 쓴 뒤 다른 글을 이어 쓴 답 | 4 | 10 |

- **두 입력의 "최대 길이에 닿은 답"은 종류가 다릅니다.** 표준 입력은 풀이가 길어서 끊긴 답입니다. 단서를 뺀 입력은 답을 일찍 쓰고도(절반은 글의 앞 6% 안에서) 생성을 끝내지 못한 답입니다.
- **끝내지 못한 답 158개 가운데 115개(73%)는 처음 쓴 답이 정답이었습니다.** 채점 규칙이 이 답들을 오답으로 셌습니다. 답의 내용으로 채점하면 정답률 차는 −0.2 [−2.1, +1.8]%p입니다.
- **다른 모델에도 같은 답이 있는지 셌습니다.** 아래 표의 값은 답 전체에서 "답을 쓰고도 끝내지 못한 답"이 차지하는 비율입니다.

| 모델 (MATH500) | 표준 입력에서 | 단서를 뺀 입력에서 | 그 가운데 처음 쓴 답이 정답 |
|---|---|---|---|
| OpenThinker-7B | 0.2% | 7.9% (158개) | 73% |
| QFFT | 0.4% | 2.5% (51개) | 78% |
| Bespoke-Stratos-7B | 0.7% | 1.6% (32개) | 22% |
| SFT | 0.2% | 0.7% (13개) | 54% |

- 네 모델 모두 단서를 빼면 이런 답이 늘었습니다. 크기는 모델마다 다릅니다. 위 둘째 결과에서 QFFT의 손해 가운데 "최대 길이까지 가고도 끝나지 않은 답 2.3%p"로 적은 부분도 속은 이것이었습니다.

**첫 답에서 멈추기.** 단서를 뺀 입력에서 첫 최종 답 표시가 닫히면 생성을 멈춘다고 놓고 다시 셌습니다. 새로 생성하지 않고 저장된 글을 그 지점에서 잘라 채점했습니다(멈춤 조건을 걸고 생성한 답과 분포가 같습니다. 생성은 앞에서부터 차례로 이루어지기 때문입니다). 표준 입력은 그대로 둡니다.

| 모델 (MATH500 500문항) | 길이: 단서를 뺀 입력 ÷ 표준 입력 | 정답률 차 | 멈추기 전의 정답률 차 |
|---|---|---|---|
| OpenThinker-7B | 0.32배 [0.31, 0.34] | +1.4 [−0.5, +3.2]%p | −4.3 [−6.5, −2.1]%p |
| Bespoke-Stratos-7B | 0.25배 [0.24, 0.26] | +0.2 [−1.8, +2.1]%p | −0.1 [−2.1, +1.9]%p |
| SFT | 0.37배 [0.35, 0.40] | +0.2 [−1.5, +1.8]%p | +0.3 [−1.3, +1.9]%p |
| QFFT | 0.80배 [0.77, 0.84] | −1.5 [−3.1, +0.0]%p | −3.7 [−5.4, −2.0]%p |

- **이 표는 아직 결론이 아닙니다.** 까닭은 둘입니다. 첫째, 멈추는 규칙을 결과를 본 뒤에 정했습니다. 둘째, 공개 모델의 표준 입력은 풀이 중에 끊긴 답(OpenThinker-7B 121개, Bespoke-Stratos-7B 170개)이 오답으로 세어져 낮게 잡혀 있습니다. 이어 생성으로 그 답들이 끝나면 표준 입력의 정답률이 오르고 차는 내려갑니다.
- **그래서 결과를 보기 전에 두 가지를 적어 두고 다시 잽니다.** (1) 같은 500문항을 시드만 바꿔 새로 생성하고, 그 답에 같은 규칙을 걸어 이어 생성한 표준 입력과 견줍니다. (2) 아직 받지 않은 다른 벤치마크의 답에서 같은 현상이 나오는지 봅니다. 적어 둔 예측은 "OpenThinker-7B는 새 표본에서도 끝내지 못한 답이 5% 이상이고 그 60% 이상이 정답이며, 표준 입력과의 정답률 차는 −3.5에서 0%p로 판정 불가"입니다.
- **새 발견으로 내세우지 않습니다.** 학습 때와 다른 입력에서 생성을 끝내지 못하고 되풀이하는 것, 최종 답에서 생성을 멈추는 설정은 이미 알려져 있습니다. 이 글에서는 방법의 손해가 어디서 나오는지 나누고, 방법을 쓸 때 붙일 규칙을 정하는 데 씁니다.

## 시험 ③ 셋째 결과: 공개 모델 둘, AIME25 30문항 × 8회 (11월 25일)

**무엇을 했나.** 위의 두 공개 모델에 가장 어려운 벤치마크 AIME25의 30문항을 같은 두 입력으로 여덟 번씩 풀게 했습니다. 설정은 위와 같습니다(최대 길이 16,384 tokens). 30문항이라 정답률의 크기는 판정하지 않고 방향만 읽기로 미리 적어 두었습니다.

**실험 예시.** 실제 문항 세 개입니다. 칸의 값은 "여덟 번 가운데 맞힌 횟수, 끝난 답의 길이"입니다.

| 문항 | Bespoke-Stratos-7B 표준 입력 | Bespoke-Stratos-7B 단서를 뺀 입력 | OpenThinker-7B 표준 입력 | OpenThinker-7B 단서를 뺀 입력 |
|---|---|---|---|---|
| b진법으로 적은 17이 b진법으로 적은 97의 약수가 되는, 9보다 큰 정수 b를 모두 더하면? 정답 70 | 8번, 1,605–6,470 tokens | 7번, 624–1,339 tokens | 7번, 1,959–5,069 tokens | 8번, 708–1,412 tokens |
| 삼각형의 두 변 위에 놓인 점들과 그 대칭점으로 만든 칠각형의 넓이는? 정답 588 | 2번. 세 번은 최대 길이에 닿음 | 0번, 3,967–8,093 tokens | 2번. 네 번은 최대 길이에 닿음 | 0번, 4,702–13,746 tokens |
| 포물선 y = x² − 4를 원점 둘레로 60도 돌린 것과 원래 포물선이 제4사분면에서 만나는 점의 y좌표를 (a − √b)/c로 쓸 때 a + b + c는? 정답 62 | 0번. 여덟 번 모두 최대 길이에 닿음 | 2번, 1,651–7,809 tokens | 0번. 여덟 번 모두 최대 길이에 닿음 | 0번. 한 번은 최대 길이에 닿음 |

첫 줄은 방법이 겨냥한 경우입니다. 두 입력 모두 맞히고 단서를 뺀 쪽이 훨씬 짧습니다. 둘째 줄은 길게 풀어야 맞는 문항으로, 단서를 뺀 입력은 여덟 번 모두 틀렸습니다. 셋째 줄은 표준 입력이 여덟 번 모두 최대 길이에 닿아 답을 내지 못한 문항입니다.

**표 읽는 법.** 한 줄이 "모델 + 입력" 하나입니다. "최대 길이에 닿은 답"은 16,384 tokens까지 쓰고도 끝나지 않은 답이고, 채점에서는 모두 오답으로 셉니다.

| 모델 | 입력 | 평균 길이 (tokens) | 긴 풀이 비율 | ACC | 최대 길이에 닿은 답 |
|---|---|---|---|---|---|
| Bespoke-Stratos-7B | 표준 입력 | 12,819 | 98.8% | 20.8% (50/240) | 54.6% (131개) |
| Bespoke-Stratos-7B | 단서를 뺀 입력 | 4,397 | 25.4% | 15.0% (36/240) | 10.0% (24개) |
| OpenThinker-7B | 표준 입력 | 12,641 | 98.8% | 22.5% (54/240) | 51.7% (124개) |
| OpenThinker-7B | 단서를 뺀 입력 | 7,977 | 68.3% | 15.8% (38/240) | 15.4% (37개) |

| 모델 | 길이: 단서를 뺀 입력 ÷ 표준 입력 | 정답률: 단서를 뺀 입력 − 표준 입력 |
|---|---|---|
| Bespoke-Stratos-7B | 0.29배 [0.23, 0.36] | −5.83 [−11.25, −0.83]%p |
| OpenThinker-7B | 0.56배 [0.48, 0.64] | −6.67 [−11.67, −2.08]%p |

- **두 모델 모두 단서를 빼면 정답률이 내려가는 방향입니다.** 30문항이라 크기는 판정하지 않습니다.
- **이 비교는 표준 입력에 불리합니다.** 표준 입력 답의 절반 넘게(131개, 124개)가 최대 길이에 닿았고 대부분 풀이를 이어 가던 중이었습니다. 그 답은 오답으로 셌습니다. 끊긴 답이 같은 문항의 끝난 답만큼 맞는다고 놓으면 표준 입력의 정답률은 27.8%, 28.1%이고 차는 −12.8, −12.2%p입니다. 이어 생성한 값으로 다시 봅니다.
- **MATH500에서 본 손해와 종류가 다릅니다.** 끝내지 못한 답은 여기서도 단서를 뺀 입력에 더 많습니다(OpenThinker-7B 8.3% 대 1.2%). 그런데 그 답의 처음 쓴 답은 한 개도 정답이 아니었습니다. 그래서 첫 답에서 멈추는 규칙을 걸어도 정답률은 그대로이고 길이만 조금 줍니다(0.27배, 0.51배). 여기서는 끝난 답 자체가 덜 맞습니다.
- 문항으로 보면 Bespoke-Stratos-7B는 표준 입력만 맞힌 문항이 5개, 단서를 뺀 입력만 맞힌 문항이 1개입니다. OpenThinker-7B는 4개와 0개입니다. 표준 입력만 맞힌 문항은 표준 입력이 평균 9,000–16,000 tokens를 쓴 문항입니다.
- **QFFT와 견주면.** 직접 학습한 모델의 저장된 평가에서 QFFT는 AIME25를 SFT의 0.82배 [0.74, 0.91] 길이로 풀고 정답률 차는 −1.25 [−4.38, +1.88]%p입니다. QFFT는 이 벤치마크에서 길이를 거의 줄이지 않습니다. 공개 모델에서 단서를 뺀 입력은 훨씬 많이 줄이고 정답률이 내려갑니다. 다만 최대 길이가 다릅니다(공개 모델 16,384, 직접 학습한 모델 32,000 tokens). 그대로 견줄 수는 없고, 한도를 늘리면 공개 모델의 표준 입력이 더 길어지므로 비는 더 작아지는 쪽입니다. 표준 SFT에 문제 글만 준 AIME25 칸은 아직 돌지 않았습니다.

## 시험 ③ 넷째 결과: 최대 길이를 32,000 tokens로 늘려 다시 잰 값과 GSM8K (11월 25일 낮)

**무엇을 했나.** 위 세 결과는 답 하나에 16,384 tokens까지만 준 값입니다. 그 한도에 잘린 답만 골라, 원래 입력과 그때까지 쓴 글을 그대로 넣고 합쳐 32,000 tokens까지 이어 쓰게 했습니다(직접 학습한 모델의 시험과 같은 한도). 이 값을 주 값으로 쓰기로 결과 전에 적어 두었습니다. 같은 때에 GSM8K 300문항 × 2회도 끝났습니다.

**표 읽는 법.** 한 칸에 "길이의 비, 정답률 차 [95% 구간], 미리 정한 판정"을 적었습니다. 길이의 비는 단서를 뺀 입력 ÷ 표준 입력이고 정답률 차는 단서를 뺀 입력 − 표준 입력입니다. 오른쪽 열은 단서를 뺀 입력에만 "첫 답에서 멈추기"를 건 값입니다.

| 모델 (MATH500 500문항 × 4회) | 최대 16,384 tokens | 최대 32,000 tokens (주 값) | 주 값에 첫 답에서 멈추기를 붙이면 |
|---|---|---|---|
| Bespoke-Stratos-7B | 0.26배, −0.1 [−2.1, +1.9]%p, 판정 불가 | 0.26배, −2.0 [−4.0, −0.1]%p, 판정 불가 | 0.24배, −1.8 [−3.8, +0.1]%p, 판정 불가 |
| OpenThinker-7B | 0.47배, −4.3 [−6.5, −2.1]%p, 정답률 손해 | 0.52배, −5.3 [−7.4, −3.2]%p, **정답률 손해** | 0.31배, +0.3 [−1.6, +2.1]%p, 못지않음 |

- **미리 정한 판정은 바뀌지 않았습니다.** 한도를 두 배로 늘려도 OpenThinker-7B는 "정답률 손해", Bespoke-Stratos-7B는 "판정 불가"입니다.
- **결과 전에 적은 예측과 견줌.** "Bespoke-Stratos-7B의 표준 입력 정답률이 81.4–84.2%로 오른다"는 81.1%로 0.3%p 차로 틀렸습니다. "판정은 낮음 또는 판정 불가"는 맞았습니다.
- **잘렸던 답은 어떻게 됐나.** 표준 입력에서 풀이 중에 잘렸던 답은 대부분 끝났지만(OpenThinker-7B 121개 가운데 102개, Bespoke-Stratos-7B 170개 가운데 124개) 끝난 답의 정답률은 20%, 27%였습니다. 잘린 답은 원래 잘 안 풀리던 답이었습니다. 단서를 뺀 입력에서 답을 쓴 뒤 되풀이하던 답은 한도를 두 배로 줘도 끝나지 않았습니다(OpenThinker-7B 148개 가운데 144개, Bespoke-Stratos-7B 31개 가운데 29개). 길이 한도의 문제가 아니라는 뜻이고, 결과 전에 적은 예측("90% 이상이 끝나지 않는다")과 맞았습니다.
- **손해는 끝내지 못한 답에서 나옵니다.** OpenThinker-7B의 단서를 뺀 입력에는 답을 쓰고도 끝내지 못한 답이 153개(7.7%) 있고 그 가운데 114개는 처음 쓴 답이 정답입니다. 첫 답에서 멈추면 정답률 차가 −5.3%p에서 +0.3%p가 되고 길이는 0.52배에서 0.31배가 됩니다. 다만 멈추는 규칙은 이 답들을 본 뒤에 정한 것이라, 시드만 바꿔 새로 생성한 답으로 확인하고 있습니다.
- **어려운 수준에서는 멈추는 규칙을 붙여도 음수 쪽입니다.** Level 5의 정답률 차는 OpenThinker-7B −3.5 [−7.8, +0.7]%p, Bespoke-Stratos-7B −4.3 [−8.8, +0.2]%p입니다. 위 AIME25(−5.8, −6.7%p)와 같은 방향입니다.

**GSM8K (300문항 × 2회, 최대 16,384 tokens).**

**표 읽는 법.** 한 줄이 "모델 + 입력" 하나입니다. "상자 있는 답"은 최종 답 표시 `\boxed{}`가 있는 답의 비율이고, 공식 채점은 상자가 없는 답을 오답으로 셉니다. 오른쪽 두 열은 상자 없이 끝난 답을 마지막에 적힌 수로 세어 본 값입니다(직접 읽어 채점한 값은 아닙니다).

| 모델 | 입력 | 평균 길이 (tokens) | ACC (공식 채점) | 상자 있는 답 | 끝내지 못한 답 | 상자 없는 답을 마지막 수로 세면 | 거기에 첫 답에서 멈추기까지 |
|---|---|---|---|---|---|---|---|
| Bespoke-Stratos-7B | 표준 입력 | 1,547 | 92.8% | 99.7% | 0개 | 92.8% | 92.7% |
| Bespoke-Stratos-7B | 단서를 뺀 입력 | 467 | 77.3% | 87.3% | 3개 (0.5%) | 88.5% | 88.7% |
| OpenThinker-7B | 표준 입력 | 1,649 | 80.5% | 87.3% | 0개 | 91.3% | 91.3% |
| OpenThinker-7B | 단서를 뺀 입력 | 1,576 | 73.2% | 86.3% | 38개 (6.3%) | 85.7% | 90.2% |

- 공식 채점으로는 정답률 차가 −15.5 [−19.0, −12.0]%p, −7.3 [−12.0, −2.8]%p로 큽니다. 대부분 답 형식과 끝맺음에서 나온 차입니다. 단서를 빼면 "답을 상자에 넣으라"는 고정 문장도 빠져 상자 없이 끝난 답이 늘고, OpenThinker-7B는 끝내지 못한 답이 6.3% 생깁니다.
- 상자 없는 답과 끝내지 못한 답을 걷어내고 견주면 차는 Bespoke-Stratos-7B 약 −4%p, OpenThinker-7B 약 −1%p입니다. 길이는 첫 답에서 멈춘 기준으로 0.24배, 0.26배입니다.
- **보지 않았던 칸에서 예측 세 개가 맞았습니다.** MATH500의 답을 보고 "끝내지 못한 답"을 찾은 뒤, GSM8K 칸을 받기 전에 적어 둔 예측입니다. OpenThinker-7B의 단서를 뺀 입력에서 끝내지 못한 답이 3% 이상이고 그 60% 이상이 정답(실제 6.3%, 74%), 첫 답에서 멈추면 정답률이 2%p 넘게 오름(실제 +4.5 [+2.8, +6.2]%p), Bespoke-Stratos-7B는 3% 미만(실제 0.5%)입니다.
- OpenThinker-7B는 표준 입력에서도 GSM8K 답의 12.7%를 상자 없이 끝냅니다(예: "Josh made a **profit of \$70,000**." 뒤에 끝 표지). 그래서 표준 입력의 공식 ACC가 80.5%로 낮게 나옵니다.

## 시험 ③ 다섯째 결과: 시드를 바꾼 새 표본에서 첫 답에서 멈추기 (11월 25일 오후)

"답을 쓰고도 끝내지 못한 답이 정답률 손해의 원인이고, 첫 답에서 멈추면 없어진다"는 것은 결과를 본 뒤에 찾은 것이었습니다. 그래서 같은 500문항을 시드만 바꿔 새로 생성하고, 미리 적어 둔 기준으로 다시 쟀습니다.

**미리 적은 기준.** (재현) 새 표본에서 끝내지 못한 답이 5% 이상이고, 그 답의 첫 `\boxed{}`가 60% 이상 정답이며, 첫 답에서 멈췄을 때 달라지는 정답률의 구간 하한이 +2%p를 넘으면 "재현". (판정) 단서를 뺀 입력에만 멈추기를 걸고 표준 입력과 견줘, 토큰 비 구간 상한이 0.90 미만이면 "더 짧음", 정답률 차 구간 하한이 −2%p 이상이면 "못지않음".

**표 읽는 법.** 한 줄이 공개 모델 하나입니다. "끝내지 못한 답"은 단서를 뺀 입력에서 `\boxed{}`를 내고도 생성을 끝내지 못해 최대 길이까지 간 답입니다. 오른쪽 두 칸은 표준 입력과 견준 토큰 비와 정답률 차(대괄호는 95% 구간)입니다. MATH500 500문항 × 4회입니다.

| 모델 | 끝내지 못한 답 | 그 답의 첫 답이 정답 | 멈추기로 달라진 정답률 | 재현 | 규칙 그대로 | 첫 답에서 멈춘 뒤 | 판정 |
|---|---|---|---|---|---|---|---|
| OpenThinker-7B | 182개(9.1%) | 127개(69.8%) | +6.15 [+4.90, +7.45]%p | 재현 | 0.48배 [0.44, 0.52], −6.95 [−9.10, −4.80]%p | 0.30배 [0.29, 0.32], −0.80 [−2.65, +1.05]%p | 판정 불가 |
| Bespoke-Stratos-7B | 29개(1.4%) | 6개 | +0.15 [−0.15, +0.50]%p | 해당 없음 | 0.26배 [0.24, 0.27], −1.55 [−3.50, +0.40]%p | 0.24배 [0.23, 0.25], −1.40 [−3.35, +0.55]%p | 판정 불가 |

- **미리 적은 예측과 견주면.** OpenThinker-7B의 "재현"과 "판정 불가", 토큰 비 0.30–0.36은 맞았습니다. Bespoke-Stratos-7B의 끝내지 못한 답 3% 미만과 토큰 비 0.23–0.27도 맞았습니다. Bespoke-Stratos-7B의 정답률 차는 −2에서 −6%p로 적었는데 −1.40%p로 예측보다 작았습니다.
- **읽기.** OpenThinker-7B의 정답률 손해가 끝내지 못한 답에서 나온다는 것은 새 표본에서도 같았습니다. 첫 답에서 멈추면 손해가 −6.95%p에서 −0.80%p로 줄어듭니다. 그러나 구간 하한이 −2.65%p라 "못지않음"으로 닫히지는 않습니다. 가장 어려운 수준(Level 5)에서는 두 모델 모두 −4%p 안팎이 남습니다(OpenThinker-7B −4.5 [−8.8, −0.2]%p, Bespoke-Stratos-7B −4.1 [−9.0, +0.7]%p).
- **종합 표시는 그대로입니다.** 미리 정한 규칙으로는 "길이는 줄지만 정답률 손해"이고, 첫 답에서 멈추기를 붙인 값은 "판정 불가"로 적습니다.

## 이 방법의 약한 곳

- **답 형식.** 단서를 빼면 "답을 상자에 넣으라"는 지시도 함께 빠집니다. 상자 없는 답이 늘고, 공식 채점은 그런 답을 오답으로 셉니다. 쉬운 문장제(GSM8K)에서 특히 그렇습니다. 그래서 정답률은 MATH500으로 판정하고, 상자 비율을 함께 적습니다.
- **어려운 문제.** AIME25에서 공개 모델 둘은 단서를 빼면 정답률이 내려가는 방향입니다(−5.8, −6.7%p, 30문항 × 8회, 위 셋째 결과). 표준 입력이 절반 넘게 최대 길이에 잘린 비교라서 실제 차는 더 클 수 있고, 첫 답에서 멈추는 규칙으로는 돌아오지 않습니다. 앞선 작은 시험에서도 낮게 나온 값이 있었습니다(OpenThinker-7B 26.7% → 18.3%, 차 −8.3 [−16.7, 0.0]%p). 30문항이라 크기는 판정할 수 없고, MATH500의 가장 어려운 수준은 시험 ④로 봅니다.
- **공개 모델 시험의 최대 길이.** 공개 모델의 처음 시험은 답 하나에 16,384 tokens까지만 줬습니다. 표준 입력은 길게 풀어서 이 한도에 더 많이 걸립니다. 그래서 잘린 답을 32,000 tokens까지 이어 생성해 다시 쟀고, 그 값을 주 값으로 씁니다(위 넷째 결과). 표준 입력의 정답률은 1.2–2.0%p 올랐습니다. 앞선 100문항 값(0.29배, 0.40배)은 16,384 한도에서 잰 값입니다.
- **끝맺음.** 단서를 빼면 답을 쓰고도 생성을 끝내지 못하는 답이 늡니다(네 모델에서 답의 0.7–7.9%). 그런 답은 최대 길이까지 tokens를 쓰고 채점에서는 오답입니다. 첫 답에서 멈추는 규칙을 붙이면 없어지지만, 그 규칙은 결과를 본 뒤에 정한 것이라 새 표본으로 다시 재는 중입니다. 풀이 중간에 답 표시를 쓰고 뒤에서 고치는 모델에는 이 규칙이 손해입니다(SFT와 QFFT의 표준 입력에 걸면 정답률 −0.5, −1.8%p). 끝내지 못하는 답은 학습 전 모델에서도 나옵니다. 프롬프트 템플릿 없이 지시문과 문제 글만 주면 답의 32%가 정답을 쓴 뒤 끝내지 못했습니다([원인 실험 글](2026-11-24-g-causal-cue-swap.html)의 "학습 전 모델 확인").
- **프롬프트 템플릿을 빼는 입력.** 문제 글만 넣는 입력은 모델이 평소 쓰이는 방식이 아닙니다. 이 입력에서 정답률이 못지않다는 것은 위 첫 결과에서 MATH500으로만 확인했습니다. 이 입력에서는 끝내지 못하는 답과 문제를 이어 쓰는 답이 생깁니다(위 둘째 결과). SFT에서는 그 손실이 다른 답에서 얻은 값에 덮였고, QFFT에서는 그대로 정답률 손해가 됐습니다. 프롬프트 템플릿을 남긴 채 시스템 프롬프트만 빼는 쪽은 A1에서는 잘 되고 SFT에서는 중간(남는 비율 0.77, 0.72)입니다.
- **새로움의 범위(11월 24일 저녁에 선행 조사를 다시 함, 11월 25일에 고침).** 원리는 새것이 아닙니다. 학습 자료의 연결이 추론을 켜는 단서를 정한다는 것(arXiv 2610.06851), 학습 때와 다른 틀로 추론하면 파인튜닝으로 생긴 행동이 덜 켜진다는 것(2402.18540)이 이미 보고돼 있습니다. 행동을 불러내는 지시문을 붙여 학습하면 지시문 없는 입력에서 그 행동이 덜 나오고, 무관한 지시문으로는 훨씬 덜 통한다는 것도 안전 성향에서 보고돼 있습니다(2510.04340, 2510.05024). 원인 실험의 결과는 이 마지막 보고와 같은 방향입니다.
- **방법으로서 가장 가까운 선행은 3TF(arXiv 2511.03408)입니다.** 생각 방식 전환이 원래 있는 Qwen3 계열을 긴 풀이 자료 10만 문항으로 학습한 뒤, 추론 때 생각 칸을 비우고 답하게 합니다. Qwen3-14B의 표 값으로 GSM8K는 정답률 94.4%에 275 tokens(생각 방식은 94.6%에 1,525 tokens), MATH-500은 98.6%에 1,613 tokens(생각 방식은 98.8%에 3,748 tokens)이고, 쉬운 과제에서 더 짧아진다고 적었습니다. "학습 때의 단서 없이 추론하면 짧아지고 정답률이 거의 유지된다"는 방법의 기본 생각은 이 연구와 겹칩니다. 다른 점은 셋입니다. 이 글은 생각 방식 전환이 없는 대화 모델을 817문서로 평범하게 SFT한 경우를 다루고, 새로 학습하지 않고 이미 있는 모델의 입력만 바꾸며, 긴 풀이가 무엇에 묶이는지를 학습 입력을 바꿔 직접 시험했습니다.
- **그래서 새로 말할 수 있는 부분은 방법 자체보다 설명 쪽입니다.** QFFT의 효과를 이 원리로 다시 읽는 것, 긴 풀이가 묶이는 곳이 학습 입력에 지시문이 있었는지에 따라 갈린다는 것을 같은 자료의 학습으로 확인한 것, 그리고 긴 풀이로 SFT한 모델에서 단서를 빼면 난도별 배분이 나오면서 정답률이 유지된다는 것을 전체 크기로 확인한 것입니다.
- **맞서는 결과.** R1 증류 모델에서는 "프롬프트만 바꿔서는 난도에 따른 배분이 나오지 않는다"는 보고(AutoThink, 2505.10832)와, 입력 조건이 달라지면 추론이 짧아지면서 정확도가 내려간다는 보고(Reasoning Shift, 2604.01161)가 있습니다. 우리 결과와 모델 계열이 다릅니다. R1 증류 모델에서 작은 크기로 확인한 결과는 "안 통함"이었습니다(위 "시험 ① 결과와 방법의 범위"). 앞의 보고와 같은 방향입니다. 그래서 방법의 범위를 좁혀 씁니다.
- 기반 모델은 Qwen2.5-7B-Instruct 하나이고 과제는 수학입니다.

## 다른 후보를 맨 위에 두지 않은 이유

| 후보 | 지금 근거 | 이유 |
|---|---|---|
| 남는 비율로 QFFT 다시 읽기 | 저장 결과 분석, 선행 조사에서 직접 겹치는 문헌을 찾지 못함 | 이 방법과 한 묶음입니다. 2순위로 올렸습니다 |
| 단서 사다리, 두 길 | 관찰(예측 다섯 칸 중 셋) | 방법을 받치는 분석입니다. 단서 사다리의 원리는 선행 연구(2610.06851)가 있어 5순위로 내렸습니다 |
| 상태를 보고 다음 행동 고르기 | 25문항 스모크(+3.2 [−0.3, +7.4]%p) | 아직 파일럿이고, 값이 "늘 단서를 넣기"와 구분되지 않습니다 |
| 응답 시작 상태에 방향 더하기 | 생각 형식은 안 켜짐, 난도 방향은 늘지도 줄지도 않음 | 미리 정한 기준에서 떨어졌습니다 |

## 일지에서의 실험 번호

방법 정리와 가능성 확인 계획 = 개발일지 11월 24일 "학습 단서 빼기 방법의 가능성 확인 계획" 항목. 시험 ① = "원인 실험 계획", ② = "맨 글 입력 전체 크기 확인 계획", ③과 ④ = 같은 날 가능성 확인 계획 3절. 시험 ①의 결과와 R1 증류 모델 시험 = 개발일지 11월 25일의 두 항목(00:55, 02:20).

시험 ③의 첫 결과(Bespoke-Stratos-7B)와 잘린 답 이어 생성 계획 = 개발일지 11월 25일 05:41 항목.

시험 ③의 둘째 결과(OpenThinker-7B), 끝내지 못한 답 분석, 첫 답에서 멈추기와 새 시드 재실행 계획 = 개발일지 11월 25일 07:24 항목.

시험 ③의 셋째 결과(공개 모델 둘의 AIME25) = 개발일지 11월 25일 09:24 항목.

시험 ③의 넷째 결과 = 개발일지 11월 25일 11:08 항목(Bespoke-Stratos-7B의 이어 생성), 11:25 항목(GSM8K), 12:18 항목(OpenThinker-7B의 이어 생성과 종합 표시).
