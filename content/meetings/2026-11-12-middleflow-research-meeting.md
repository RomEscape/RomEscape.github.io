---
title: 11월 12일 Middleflow 연구 회의록 — latent는 어디서 계산해야 쓰이는가?
date: 2026-11-12
event: Middleflow 연구 회의
summary: CODI의 latent를 가운데 layer에서만 계산하는 Middleflow를 같은 설정의 CODI, 추가 실험 다섯 가지와 비교했다. latent 없이 학습해도 정확도가 같았던 결과를 어떻게 읽어야 하는지, 연구 질문과 다음 검증을 정리했다.
published: true
---

**회의 뒤 다시 세운 연구 질문은 “latent 추론의 정확도는 latent 계산에서 오는가, 학습 신호에서 오는가, 그리고 latent를 모델의 어느 layer에서 계산해야 모델이 그것을 실제로 쓰는가?”이다.** 발표에서는 Middleflow가 CODI보다 빠르다는 것과 함께, latent 없이 학습한 모델도 같은 정확도를 낸다는 결과를 보였다. 회의에서는 이 결과를 “latent는 의미가 없다”로 읽으면 안 된다는 점이 핵심으로 남았다. CODI 같은 방법은 분명한 이유가 있어서 나왔다. 그 이유 가운데 무엇이 이 모델과 이 과제에서 작동했고 무엇이 작동하지 않았는지 나누어 설명해야 Middleflow의 효과도 제대로 말할 수 있다.

| 11월 12일 논점 | 발표에서 확인한 것 | 회의에서 남긴 질문 |
|---|---|---|
| [1. Middleflow와 CODI](#main) | 추론 23%, 학습 21% 빠르다. SVAMP, MultiArith는 같고 GSM8K, GSM-Hard는 2~3점 낮다. | 빠르다는 이점이 Middleflow만의 것인가? latent 수를 줄인 CODI와 무엇이 다른가? |
| [2. latent를 넣는 layer](#insert) | 넣는 곳을 L0으로 옮기면 CODI와 정확도가 같아지고, 추론 때 latent를 바꾸면 크게 떨어진다. | layer 위치가 정확도가 아니라 “latent를 쓰는 정도”를 바꾸는 이유는 무엇인가? |
| [3. latent 없이 학습한 모델](#no-latent) | latent 계산 없이 학습해도 네 벤치마크에서 CODI와 차이가 확인되지 않았다. 정확도의 큰 몫은 distillation에서 왔다. | latent가 효과를 내는 조건은 무엇인가? latent가 없을 때 얻는 것과 잃는 것은 무엇인가? |

**자료와 조건.** 수치는 11월 12일 발표자료 *Research Report_261112*를 따른다. 모델은 Llama-3.2-1B-Instruct(layer 16개, 0번부터 L0~L15로 센다), 학습 자료는 GSM8K-Aug(약 38만 문항의 수학 문장제와 계산식 풀이)다. 모든 모델을 같은 코드, 같은 하이퍼파라미터로 처음부터 따로 학습했다. LoRA r128, 학습률 8e-4, 10 epoch, latent 6개, 원본 코드의 고정 시드 11이다. CODI는 같은 코드에서 latent를 전체 layer로 돌리는 설정이며, 공식 CODI 코드를 직접 돌린 결과는 아니다. 같은 코드에서 L15→L0으로 두면 공식 CODI의 반복과 같은 값이 나오는 것을 단위 시험으로 확인했다. 차이는 모두 같은 문항을 짝지어 계산했고 대괄호는 95% 구간이다.

[![그림 1. CODI는 L15 출력을 뽑아 다음 position의 L0에 넣어 latent 하나마다 16개 layer를 통과하고, Middleflow는 L13 출력을 뽑아 L7에 넣어 7개 layer만 통과한다](../uploads/middleflow/meeting-2026-11-12/codi-vs-middleflow.png)](../uploads/middleflow/meeting-2026-11-12/codi-vs-middleflow.png)

*그림 1. 발표 3쪽. 가로는 position(질문, latent 6개, 답), 세로는 layer다. 파란 칸이 latent가 실제로 계산되는 layer다. 질문과 답 토큰은 두 방법 모두 16개 layer를 다 지나고, 답 토큰은 파란 layer에서만 latent를 볼 수 있다. 그림을 누르면 원본 크기로 열린다.*

### 용어 풀이

| 용어 | 뜻 | 이 발표에서의 값 |
|---|---|---|
| latent (잠재 생각) | 풀이를 글로 쓰는 대신 모델 안에서 만드는 벡터 하나. 다음 position의 입력으로 다시 넣는다 | 문항마다 6개 |
| 뽑는 layer → 넣는 layer | latent를 어느 layer 출력에서 꺼내 어느 layer 입력에 넣는지. 이름의 L13→L7이 이것이다 | CODI L15→L0, Middleflow L13→L7 |
| CODI 학습 손실 | ① 교사 CE: 질문과 풀이를 보고 풀이와 답을 맞힘, ② 학생 CE: latent 뒤에 답을 맞힘, ③ distillation: 답 직전 위치에서 학생의 내부 표현을 교사와 같게 맞춤 | ③의 계수 20, 17개 layer 경계의 평균 |
| 같은 문항 짝차이 | 두 모델이 같은 문항에서 맞고 틀린 것을 짝지어 낸 정확도 차이 | 구간이 0을 포함하면 “차이 확인 안 됨” |
| 추론 시간 | 같은 GPU 조각에서 잰 문제당 평균 시간 | ms 단위 |
| 학습 시간 | 10 epoch(29,990 step) 전체 시간 | 시간 단위 |

<h2 id="main">1. Middleflow와 CODI: 빠르지만 GSM8K 계열은 낮다</h2>

**Middleflow는 latent 하나가 7개 layer만 지나므로 latent 계산이 6 × 16 = 96번에서 6 × 7 = 42번으로 줄었다.** 그만큼 추론과 학습이 빨라졌다. SVAMP와 MultiArith는 차이가 없었고, GSM8K와 GSM-Hard는 낮았다.

| 항목 | Middleflow (L13→L7) | CODI (L15→L0) | 차이 (Middleflow − CODI) |
|---|---:|---:|---|
| GSM8K | 50.42 | 53.37 | −2.96 [−5.09, −0.82] |
| SVAMP | 60.00 | 59.40 | +0.60 [−1.63, +2.83] |
| MultiArith | 98.89 | 98.33 | +0.56 [−1.33, +2.44] |
| GSM-Hard | 10.99 | 12.96 | −1.97 [−3.10, −0.84] |
| 추론 시간 (문제당) | 98.4 ms | 127.9 ms | 23% 적음 |
| 학습 시간 (10 epoch) | 15.0시간 | 19.1시간 | 21% 적음 |

**표 읽는 법.** 정확도는 %다. 대괄호 구간이 0을 포함하지 않으면(GSM8K, GSM-Hard) 차이가 있다고 본다. 시드가 하나라서 1~2점 차이는 확정할 수 없다. 추론 최대 메모리는 두 모델 모두 2.54 GiB로 같았다.

[![그림 2. 문제당 추론 시간과 GSM8K 정확도. Latent 없음이 75 ms로 가장 빠르고, 일곱 모델의 정확도 구간이 서로 겹친다](../uploads/middleflow/meeting-2026-11-12/accuracy-and-latency.png)](../uploads/middleflow/meeting-2026-11-12/accuracy-and-latency.png)

*그림 2. 발표 7쪽. 왼쪽일수록 빠르고 위일수록 정확하다. 세로 선은 95% 구간이다.*

**같은 계산량의 CODI(추가 실험 2).** “속도만 원하면 CODI의 latent 수를 줄이면 되지 않느냐”는 질문에 답하려고, CODI를 latent 3개로 처음부터 학습했다(latent 계산 3 × 16 = 48번). 추론 100.0 ms, 학습 15.4시간으로 Middleflow와 거의 같았다. 정확도 차이(Middleflow − latent 3개 CODI)는 GSM8K −1.14 [−3.27, +1.00], SVAMP −0.80 [−2.95, +1.35], MultiArith +1.67 [−0.76, +4.09], GSM-Hard −0.91 [−1.87, +0.05]로 네 벤치마크 모두 확인되지 않았다. **지금 결과로는 Middleflow의 속도 이점을 latent 수를 줄이는 것으로도 얻을 수 있다.**

<h2 id="insert">2. latent를 넣는 layer: 정확도보다 “latent를 쓰는 정도”를 바꾼다</h2>

**추가 실험 1은 뽑는 곳(L13)은 그대로 두고 넣는 곳만 L7 → L4 → L0으로 앞당겼다.** latent가 지나는 layer가 7개, 10개, 14개로 늘어난다.

[![그림 3. 이어진 latent 두 position에서 L13 출력을 뽑아 L7, L4, L0에 넣을 때 latent가 지나는 layer](../uploads/middleflow/meeting-2026-11-12/insert-layer.png)](../uploads/middleflow/meeting-2026-11-12/insert-layer.png)

*그림 3. 발표 8쪽. 세 설정 모두 처음부터 따로 학습했다.*

| 설정 (지나는 layer) | GSM8K | SVAMP | MultiArith | GSM-Hard | 추론, 학습 시간 |
|---|---:|---:|---:|---:|---|
| CODI L15→L0 (16개) | 53.37 | 59.40 | 98.33 | 12.96 | 127.9 ms, 19.1시간 |
| L13→L0 (14개) | 53.07 | 59.20 | 97.22 | 12.51 | 117.0 ms, 17.9시간 |
| L13→L4 (10개) | 50.64 | 58.50 | 97.22 | 12.05 | 107.7 ms, 16.3시간 |
| Middleflow L13→L7 (7개) | 50.42 | 60.00 | 98.89 | 10.99 | 98.4 ms, 15.0시간 |

L13→L0과 CODI의 차이는 네 벤치마크 모두 1점 안팎이었다(GSM8K −0.30 [−2.39, +1.79]). 미리 정한 판정 기준으로 “일치”다. L13→L0은 Middleflow보다 GSM8K가 +2.65 [+0.37, +4.94] 높았다. L13→L0의 추론 시간은 따로 잰 측정 실행의 값이고, 같은 실행 안에서 비교하면 CODI보다 7% 빠르고 Middleflow보다 22% 느렸다.

**추론 때 latent 바꾸기.** 학습이 끝난 세 모델을 그대로 두고, 추론할 때만 latent 자리를 바꿨다. 건너뜀, 0 벡터, 답할 때 가림은 latent 내용을 비우는 방법이다. 잡음과 다른 문항의 latent는 틀린 내용을 넣는 방법이다.

[![그림 4. 추론 때 latent를 비우거나 틀린 내용을 넣었을 때 CODI, L13→L0, Middleflow의 GSM8K 정확도](../uploads/middleflow/meeting-2026-11-12/inference-interventions.png)](../uploads/middleflow/meeting-2026-11-12/inference-interventions.png)

*그림 4. 발표 18쪽. 괄호는 그대로일 때보다 몇 점 바뀌었는지다. 점선은 처음부터 latent 없이 학습한 모델(52.2)이다. GSM8K만 평가했고 시드는 하나다.*

| 추론 때 바꾼 것 | CODI (L0에 넣음) | L13→L0 (L0에 넣음) | Middleflow (L7에 넣음) |
|---|---:|---:|---:|
| 그대로 | 53.4 | 53.1 | 50.4 |
| latent 건너뜀 (계산 없이 position만 비움) | −17.3 | −14.6 | −4.0 |
| 0 벡터 삽입 | −26.2 | −20.6 | −2.2 |
| 답할 때 가림 | −17.2 | −14.9 | −4.3 |
| 다른 문항의 latent | −42.2 | −37.1 | −25.9 |

**읽는 법.** latent를 비우면 L0에 넣은 두 모델만 15~26점 떨어졌다. L13→L0과 Middleflow는 같은 L13에서 뽑으므로, 이 차이를 가른 것은 뽑는 곳이 아니라 넣는 곳이다. 다른 문항의 latent를 넣으면 세 모델 모두 크게 떨어졌으므로, 셋 다 latent 내용을 읽어 답에 쓴다. 그래서 이 결과는 “Middleflow가 더 강건하다”가 아니라 **“L7에 넣으면 답이 latent에 덜 의존한다”**로 읽는 것이 정확하다. latent에 많이 기대는 모델(CODI, L13→L0)도 정확도는 latent 없이 학습한 모델보다 높지 않았다.

**이후 확인(11-24).** 저장된 답 글을 다시 읽어 보니, latent를 비운 답의 일부는 답 앞에 학습 자료의 풀이 형식(`<<계산식>>`)으로 계산식을 글로 쓰고 답했다. 0 벡터를 넣었을 때 그런 답이 Middleflow는 45.9%, CODI는 11.3%였다. 글로 쓰지 않은 답만 보면 Middleflow 45.8%, CODI 23.0%였다. Middleflow가 덜 떨어진 데에는 글로 풀이를 쓰는 쪽으로 더 자주 넘어간 몫과, 글을 쓰지 않고도 덜 떨어진 몫이 함께 들어 있다. 자세한 표는 [추론 때 latent 바꾸기 기록](../experiments/2026-11-12-mf-g-inference-interventions.html)에 있다.

<h2 id="no-latent">3. latent 없이 학습한 모델과 distillation</h2>

**추가 실험 3의 Latent 없음은 학습이 끝난 CODI에서 latent를 뺀 것이 아니다.** 기본 Llama-3.2-1B-Instruct에서 출발해 학습할 때도 추론할 때도 latent 계산 없이 따로 학습한 모델이다. 답 토큰의 position 번호는 latent 6개가 있을 때와 같게 띄웠고, 손실 세 항도 같다.

[![그림 5. CODI, Middleflow, Latent 없음 모델의 계산 범위. Latent 없음은 latent 자리를 계산하지 않고 position 번호만 건너뛴다](../uploads/middleflow/meeting-2026-11-12/no-latent-model.png)](../uploads/middleflow/meeting-2026-11-12/no-latent-model.png)

*그림 5. 발표 12쪽. position 번호는 질문이 35토큰인 문항의 예다.*

손실 항은 Distillation 제거만 ①②이고 나머지 셋은 ①②③이다. latent 계산은 CODI 6 × 16번, Middleflow 6 × 7번, 아래 두 모델은 없음이다.

| 모델 | GSM8K | SVAMP | MultiArith | GSM-Hard | 추론, 학습 시간 |
|---|---:|---:|---:|---:|---|
| CODI | 53.37 | 59.40 | 98.33 | 12.96 | 127.9 ms, 19.1시간 |
| Middleflow | 50.42 | 60.00 | 98.89 | 10.99 | 98.4 ms, 15.0시간 |
| Latent 없음 (추가 3) | 52.16 | 57.60 | 97.78 | 12.28 | 75.0 ms, 12.3시간 |
| Distillation 제거 (추가 5) | 36.69 | 48.00 | 62.78 | 9.02 | 미측정, 12.5시간 |

CODI − Latent 없음은 GSM8K +1.21 [−1.11, +3.53] 등 네 벤치마크 모두 차이가 확인되지 않았다. 반면 Latent 없음에서 ③ distillation만 빼면 GSM8K −15.47 [−18.04, −12.89], MultiArith −35.00 [−42.30, −27.70]으로 네 벤치마크가 모두 떨어졌다. **이 설정에서 정확도의 큰 몫은 latent 계산이 아니라, 풀이를 본 교사의 내부 표현을 따라 하게 하는 distillation에서 왔다.** CODI 논문의 distillation 손실 제거 실험(GPT-2)과 같은 방향이다.

[![그림 6. 교사는 질문과 풀이를 보고, 학생은 풀이 없이 답한다. distillation은 답 숫자 직전 위치에서 학생의 내부 표현을 교사와 같게 맞추는 손실이다](../uploads/middleflow/meeting-2026-11-12/distillation-removal.png)](../uploads/middleflow/meeting-2026-11-12/distillation-removal.png)

*그림 6. 발표 16쪽. 예시는 GSM8K-Aug 학습 자료의 첫 문항이다.*

**latent 내용 고정(추가 실험 4).** 매 step 직전 latent 대신 질문 끝에서 만든 첫 벡터를 여섯 번 되풀이해 넣도록 학습했다. 계산량은 같고 step 사이로 넘어가는 정보만 끊긴다. Middleflow보다 GSM8K −3.64 [−5.77, −1.51], SVAMP −4.40, MultiArith −3.33 떨어졌다. latent 내용이 아무 역할도 없는 것은 아니다.

## 회의에서 남긴 질문과 정리

### “latent 없이도 같다”를 “latent는 의미 없다”로 읽으면 안 되는 이유

CODI 같은 latent 추론은 세 가지 이유로 나왔다. 이 발표의 결과는 그중 일부가 **이 모델과 이 과제에서는** 필요하지 않았다는 뜻이지, 이유 자체가 틀렸다는 뜻이 아니다.

| latent가 주는 것으로 기대한 것 | 이 발표에서 확인된 것 | 아직 남은 것 |
|---|---|---|
| **계산을 더 할 자리.** 답을 내기 전에 모델이 직렬 계산을 더 할 수 있다. 풀이를 글로 쓰는 CoT가 효과적인 이유로 제시된 것과 같은 성격이다 | Llama-1B, GSM8K-Aug에서는 이 자리가 없어도(Latent 없음) 정확도가 같았다 | 선행 연구(PCCoT 표 1)에서 GPT-2 Small은 같은 CODI 손실로 학습했을 때 latent 계산이 있는 쪽이 약 9점 높았다. 계산 여유가 부족한 작은 모델이나 더 긴 풀이에서는 이 자리가 필요할 수 있다 |
| **풀이 내용을 벡터로 전달.** 글 대신 연속 벡터로 중간 결과를 넘긴다 | 세 모델 모두 다른 문항의 latent를 넣으면 크게 떨어졌고, 내용을 고정하면 3~4점 떨어졌다. 모델은 latent 내용을 실제로 읽는다 | 내용을 읽는다고 정확도가 오르는 것은 아니었다. latent 없는 모델은 같은 정보를 답 토큰의 계산 안에서 만든다고 볼 수 있다(가설) |
| **풀이를 본 교사에게서 배우는 학습 신호.** CODI의 distillation | 정확도의 큰 몫이 여기서 왔다(제거 시 GSM8K −15.5점) | 이 신호가 latent가 있을 때와 없을 때 같은 방식으로 작동하는지는 아직 모른다 |

**latent가 없을 때의 이점.** 학습이 가장 빠르고(12.3시간, CODI의 64%) 추론도 가장 빠르다(75.0 ms, CODI의 59%). latent를 차례로 계산하는 반복이 없어 구현이 단순하다. 이 설정에서는 정확도 손해도 확인되지 않았다.

**latent가 없을 때 잃는 것.** 추론 때 latent 수를 늘려 계산을 더 쓰는 선택지가 없다(학습된 CODI는 추론 latent 0개 36.2%에서 6개 53.4%로 올랐다). 답 직전의 중간 상태를 들여다보거나 바꿔 보는 분석 지점이 없다. 계산 여유가 부족한 모델에서는 정확도를 잃을 수 있다(선행 연구의 GPT-2 결과). 또 이 모델은 답의 position을 띄운 상태에 맞춰 학습되어, 띄우지 않으면 풀이를 글로 쓰기 시작한다(간격 0에서 출력 22.4토큰, 57.85%). 이 값은 latent 없이 푼 결과와 나란히 놓으면 안 된다.

**Middleflow의 효과를 말하는 방식.** Middleflow는 latent 계산을 가운데 layer로 좁혀 비용을 줄였고, 넣는 곳에 따라 답이 latent에 기대는 정도가 크게 달라진다는 것을 보여 주었다. 다만 이 모델에서는 latent 계산의 기여 자체가 작아서, 비용을 줄인 효과와 정확도를 지킨 효과를 구분해 보이기 어렵다. Middleflow의 이점은 **latent가 실제로 필요한 조건**에서 확인해야 분명해진다.

### 다시 세운 연구 질문

1. latent 추론의 정확도 향상은 latent 계산, latent가 전달하는 내용, distillation 학습 신호 가운데 어디에서 오는가?
2. latent를 계산하는 layer 범위(특히 넣는 layer)는 모델이 latent를 쓰는 정도와 정확도를 어떻게 바꾸는가?
3. latent 계산이 정확도에 기여하는 조건에서, 가운데 layer만으로 latent를 계산해도 그 기여를 지키면서 비용을 줄일 수 있는가?

### 다음 검증

1. **latent가 실제로 기여하는 모델에서 같은 비교.** CODI 원본 코드에 GPT-2 Small 설정과 공개 체크포인트가 있다. 먼저 공개 체크포인트로 평가 경로를 확인하고, CODI, latent 없이 같은 손실로 학습한 모델, Middleflow, 넣는 layer를 바꾼 모델을 같은 설정으로 학습한다.
2. **여러 시드.** 1~3점 차이를 판정하려면 선행 연구처럼 시드 3개가 필요하다.
3. **공식 CODI 코드 재현과 가까운 선행 연구 비교.** 같은 코드의 CODI 설정이 공식 코드와 같은 값을 내는지 확인하고, 가운데 layer를 되풀이하는 선행 연구(ETD, T²MLR)와 차이를 정리한다.

## 회의 뒤 진행 중인 실험 (11월 24일 기준)

회의에서 정한 다음 검증과 그 뒤에 더한 실험의 진행 상황이다. 시각은 한국 시각이다.

| 실험 | 회의의 어느 질문에 답하나 | 상태 (11월 24일) | 기록 |
|---|---|---|---|
| GPT-2 Small에서 같은 비교 | 다음 검증 1, 연구 질문 3 | 세 모델 학습 중, 11월 25일 새벽 끝 예정 | [GPT-2 Small 비교](../experiments/2026-11-24-mf-j-gpt2-plan.html) |
| 더 어려운 문제(GSM-Symbolic, AIME) | latent가 효과를 내는 조건 | Llama-1B 다섯 모델 끝, 나머지 평가 중 | [더 어려운 문제](../experiments/2026-11-24-mf-k-harder-benchmarks.html) |
| latent 경로 변형(루프, 사선, 후퇴 후 전진) | 연구 질문 2, 3 | 코드와 시험 끝, 루프는 11월 25일 새벽, 사선과 후퇴 후 전진은 25일 밤과 26일 새벽 학습 시작 | [경로 변형](../experiments/2026-11-24-mf-l-latent-path-plan.html) |
| Llama 학습 시간을 CODI와 같게 | Middleflow가 아낀 학습 시간을 더 학습에 쓰면 CODI만큼 맞히나 | 코드와 시험 끝, 11월 25일 새벽 학습 시작 | [학습 시간 맞춤](../experiments/2026-11-24-mf-m-llama-codi-time.html) |
| 띄엄 배치 10 epoch | 연구 질문 2 | 셋 중 하나 끝, 둘 보류 | [띄엄 배치](../experiments/2026-11-14-mf-i-layer-placement-and-stride.html) |

다음 검증 2(여러 시드)는 11월 24일에 시드 하나(11)로 비교 조건을 늘리는 쪽으로 바꿨다. 아래 결과도 모두 시드 하나다.

### GPT-2 Small에서 같은 비교 (다음 검증 1)

[![그림 7. GPT-2 Small에서 같은 설정으로 학습하는 네 모델의 latent 계산 범위](../uploads/middleflow/experiments/gpt2-arms.png)](../uploads/middleflow/experiments/gpt2-arms.png)

*그림 7. GPT-2 Small(layer 12개)에서 같은 설정으로 학습하는 네 모델. 파란 칸이 latent를 계산하는 layer다. Middleflow는 Llama의 L13→L7을 layer 비율대로 옮긴 L9→L5(5개 layer)다.*

CODI 저자가 공개한 GPT-2 체크포인트를 우리 평가 코드로 채점하니 GSM8K 42.46%(논문 43.7%)였고, 공식 평가 방식과 1,319문항의 답이 모두 같았다. 이 모델은 추론 때 latent를 비우면 22% 안팎, 다른 문항의 latent를 넣으면 6.37%로 떨어져 latent에 크게 기댄다. CODI(11월 24일 12:49 시작), Latent 없음(13:13), Middleflow(14:31)를 원본 CODI GPT-2 설정(40 epoch)으로 GPU 한 장씩 학습하고 있고, 11월 25일 03:30~05:45쯤 끝난다. L9→L0은 사선 경로 다음에 학습한다.

### 더 어려운 문제에서 latent의 몫 (latent가 효과를 내는 조건)

[![그림 8. GSM-Symbolic 같은 틀의 main 문항과 P1 문항, 네 모델의 답](../uploads/middleflow/experiments/gsm-symbolic-example.png)](../uploads/middleflow/experiments/gsm-symbolic-example.png)

*그림 8. GSM-Symbolic 같은 틀에서 나온 두 문항과 Llama-1B 네 모델의 실제 답. 풀이 단계가 하나 늘자 Latent 없음만 틀렸다.*

[![그림 9. GSM-Symbolic에서 각 모델과 Latent 없음의 짝차이](../uploads/middleflow/experiments/gsm-symbolic-diff.png)](../uploads/middleflow/experiments/gsm-symbolic-diff.png)

*그림 9. 각 모델 − Latent 없음의 같은 문항 짝차이와 문제 틀 단위 95% 구간. 채운 점은 구간이 0을 포함하지 않는다. 11월 24일 15:14까지 끝난 모델만 그렸다.*

GSM8K에서는 CODI와 Latent 없음의 차이가 확인되지 않았지만(+1.21 [−1.11, +3.53]), 이름과 숫자를 바꾼 main에서 CODI가 4.80점, 풀이 단계를 하나 더한 P1에서 CODI 2.98점, L13→L4 2.70점, Middleflow 2.02점 높았다. 회의에서 본 "latent 없이도 같다"는 GSM8K 문항 그대로에서의 결과였고, 바뀐 문항에서는 latent가 있는 모델이 앞섰다. AIME24, AIME25는 모든 모델이 0~1/30이라 비교할 수 없었다.

### latent 경로 변형 (연구 질문 2, 3)

[![그림 10. latent 경로 변형 세 가지와 기준 Middleflow의 step별 경로](../uploads/middleflow/experiments/latent-paths.png)](../uploads/middleflow/experiments/latent-paths.png)

*그림 10. 기준 Middleflow와 경로 변형 세 가지. 루프와 후퇴 후 전진은 한 latent position에서 layer를 두 번 지나므로 칸을 둘로 나눠 그렸다. 연한 파랑은 지나지만 KV를 남기지 않는 칸, 진한 파랑은 KV를 남기는 칸이다.*

넣는 layer가 latent를 쓰는 정도를 바꾼다는 회의 결과에서 출발해, step마다 지나는 layer 범위를 바꾸는 경로 세 가지를 만들었다. 계산량이 같은 짝으로 루프는 L9→L0과, 사선은 Middleflow와 비교한다. 코드와 시험 12개를 11월 24일에 마쳤다. 루프는 GPT-2 Middleflow가 끝나는 11월 25일 05:25쯤 시작한다. 사선과 후퇴 후 전진은 11월 24일 22시에 순서를 바꿔, 아래 Llama 학습 시간 맞춤 학습 뒤인 25일 23시쯤과 26일 01시쯤 시작한다. 한 경로에 약 15시간이 걸릴 것으로 본다.

### Llama 학습 시간을 CODI와 같게 (회의 뒤 추가)

[![그림 12. 학습 시간을 CODI와 같게 맞춘 학습 길이와 학습률 일정](../uploads/middleflow/experiments/codi-time.png)](../uploads/middleflow/experiments/codi-time.png)

*그림 12. 왼쪽은 원래 10 epoch 학습 시간(진한 막대)과 CODI의 19.1시간까지 더 학습하는 몫(연한 막대), 오른쪽은 학습률 일정이다. 세 일정은 최고 학습률과 warmup 비율이 같고 길이만 다르다.*

지금까지의 비교는 모두 10 epoch였다. Middleflow는 latent 계산이 적어 10 epoch 학습이 CODI보다 4.1시간 짧았다(15.0시간, 19.1시간). 그 시간만큼 더 학습하면(38,166 step, 12.73 epoch) CODI와의 GSM8K 차이(−2.96 [−5.09, −0.82])를 메우는지 본다. 같은 방식으로 Latent 없음(46,554 step, 15.52 epoch)도 학습해, 오른 몫이 latent 덕인지 더 학습한 덕인지 가른다. 10 epoch 저장본 세 개를 새 GPU에서 다시 채점하니 네 벤치마크 3,818문항의 답이 원래와 모두 같았으므로, 새 결과는 원래 결과와 그대로 비교한다. 11월 25일 새벽에 GPU 두 장에서 하나씩 시작해 25일 23시쯤과 26일 01시쯤 끝날 것으로 본다.

### 띄엄 배치 (연구 질문 2)

[![그림 11. 1 epoch 예비 비교의 다섯 배치에서 latent가 지나는 7개 layer](../uploads/middleflow/experiments/stride-placement.png)](../uploads/middleflow/experiments/stride-placement.png)

*그림 11. Middleflow와 같은 7개 layer를 앞쪽 연속, 또는 한 칸씩 건너뛰어 둔 배치. 이어진 두 latent position만 확대해 그렸다.*

10 epoch로 끝난 block 1, 3, …, 13 배치는 GSM8K 49.51로 Middleflow와 차이가 확인되지 않았고(−0.91 [−3.02, +1.20]) CODI보다 3.87점 낮았다. 나머지 두 배치는 11월 15일 새벽에 멈춘 뒤 보류 중이다.

## 한계

- 모든 결과가 시드 하나, 모델 하나(Llama-3.2-1B-Instruct), 수학 문장제 네 가지다.
- 추론 때 latent를 바꾼 분석은 GSM8K만 평가한 탐색적 분석이다.
- CODI 비교 모델은 같은 코드의 전체 layer 설정이며, 공식 코드와 다른 점은 latent 단계에서 질문의 왼쪽 채움 자리를 가린다는 것 하나다.
- 위의 “latent가 주는 것” 표에서 이 발표의 수치로 확인한 칸과 선행 연구에 기댄 칸을 나눴다. 선행 연구 수치는 설정이 달라 우리 수치와 나란히 비교하지 않는다.

관련 글: [Middleflow 연구 개요](../research/middleflow.html)
