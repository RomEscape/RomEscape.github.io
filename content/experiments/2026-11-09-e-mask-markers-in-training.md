---
title: Wait 같은 말을 학습에서 빼면 긴 풀이가 줄어들까
date: 2026-11-09
project: QFFT
status: 판정 완료, 후속 진행 중
summary: 풀이 중의 Wait 같은 말을 학습할 때 점수 계산에서 빼 보는 작은 실험을 했다. 문단 첫 토큰을 뺀 조건만 미리 정한 기준을 넘었지만, 그 차이는 대부분 답이 같은 말을 끝없이 되풀이한 경우가 줄어서 생겼다. 비교 기준 모델에는 Wait가 거의 없어서 Wait를 뺀 효과도 읽을 수 없었다. 그래서 실험 설계를 고쳐 다시 재고 있다.
published: true
---

## 한 줄 요약

모델이 풀이 중에 쓰는 `Wait` 같은 말을 **학습할 때 채점에서 빼면** 쓸데없이 긴 풀이가 줄어드는지 작은 모델로 시험했습니다. 미리 정한 기준을 넘은 것은 **문단 첫 토큰을 뺀 조건** 하나뿐이었습니다. 그런데 그 차이는 대부분 답이 **같은 말을 끝없이 되풀이한 경우가 줄어서** 생겼고, 정답률은 낮아진 쪽이었습니다. 또 비교 기준으로 삼은 모델에 `Wait`가 거의 없어서, `Wait`를 뺀 효과를 이 실험으로는 알 수 없었습니다. 그래서 설계를 고쳐 다시 재고 있습니다.

## 왜 궁금했나

문제를 지우고 긴 풀이만으로 학습한 모델은 학습 때 첫 글자를 맞히는 점수를 빼면(첫 토큰 라벨 제외) 쓸데없이 길게 푸는 일이 줄어듭니다. 이미 있는 방법입니다. 그렇다면 첫 글자뿐 아니라 풀이 중간의 `Wait`, `Alternatively` 같은 말도 빼면 어떨까요? 그러면 모델이 **언제 망설일지**는 학습하지 않고, **망설인 다음에 무엇을 쓸지**는 그대로 배울 수 있습니다. 이 방향은 같은 연구를 찾지 못한, 새로운 방법 후보입니다.

전체 모델을 다시 학습하면 약 4시간이 넘게 걸립니다. 그래서 먼저 작은 학습으로 방향만 봅니다.

## 용어 풀이

| 용어 | 쉬운 뜻 | 이 글에서의 값 |
|---|---|---|
| 토큰 | 글을 나눈 작은 단위. 모델의 작업량을 재는 단위 | 답 하나에 수백–32,000 |
| LoRA | 원래 모델에 작은 추가 가중치만 붙여 짧게 학습하는 방식 | 400번 갱신, 조건당 약 17분 |
| 라벨 제외 | 학습할 때 어떤 토큰의 맞고 틀림을 채점하지 않아서, 그 토큰을 내는 습관을 학습하지 않게 하는 것 | |
| 표지 | 풀이 도중 방향이 바뀔 때 쓰는 말 | `Wait`, `Alternatively`, `Hmm` |
| 첫 토큰 | 답의 맨 앞 토큰 | `Okay`, `To` |
| 문단 첫 토큰 | 빈 줄 다음에 오는 토큰 | `Wait`, `So`, `Let` |
| 대조 | 효과가 진짜인지 보려고 함께 재는 비교 조건 | 같은 수의 무작위 토큰을 뺌 |
| 양성 대조 | 이 실험으로 효과를 잡아낼 수 있는지 먼저 확인하는 것 | 아래 판정 ① |
| 상한 도달 | 답이 끝나지 않고 32,000토큰까지 간 것 | 조건당 0–28개 |
| 되풀이 고리 | 같은 문장을 끝없이 반복하는 상태 | 아래 예시 |
| 토큰 비 | 그 조건의 평균 토큰 ÷ 기준 조건의 평균 토큰 | 0.59배 |

## 어떻게 했나

1. **모델.** Qwen2.5 7B 모델에 작은 추가 가중치를 붙입니다.
2. **학습 자료.** 문제를 지운 긴 풀이 자료(LIMO 817개)입니다. 조건마다 같은 문서를 같은 순서로 400번 갱신합니다.
3. **조건 여섯 개.** 다른 점은 채점에서 빼는 토큰뿐입니다.

| 조건 | 빼는 토큰 | 뺀 양(전체 대비) |
|---|---|---:|
| 아무것도 안 뺌 | 없음 | 0% |
| 첫 토큰만 뺌 (기준) | 답의 맨 앞 토큰 | 0.01% |
| + 표지 전부 | + `Wait`, `Alternatively`, `Hmm` | 0.55% |
| + 연쇄 표지만 | + 직전 표지에서 100토큰 안에 다시 나온 표지 | 0.30% |
| + 문단 첫 토큰 | + 모든 문단의 첫 토큰 | 2.62% |
| + 무작위 (대조) | + 표지 전부와 같은 수의 무작위 토큰 | 0.55% |

4. **평가.** 수학 8문제에 조건마다 8번씩 답을 뽑습니다(`temperature 0.6`, 32,000토큰 상한). 원래 모델(Base)도 함께 뽑습니다.

**결과를 보기 전에 정한 기준.**

- ① 양성 대조: "아무것도 안 뺌"의 1,000토큰당 `Wait`가 "첫 토큰만 뺌"의 1.3배 이상이면 이 실험이 차이를 잡아낼 수 있다고 봅니다.
- ② 첫 토큰만 뺀 조건과 비교합니다. 토큰 비 0.8배 이하이고 정답률이 13%p보다 많이 떨어지지 않으면 **통과**입니다. 정답률이 13%p 이상 떨어지고 토큰 비가 0.6배를 넘거나, 토큰 비가 0.95배 이상이고 정답률이 13%p 넘게 오르지 않으면 **탈락**입니다. 나머지는 **보류**입니다.
- ③ 표지를 뺀 조건은 무작위 대조보다 `Wait`와 토큰을 모두 더 줄여야 합니다.
- 후속 규칙: 양성 대조를 통과하고 표지 전부 또는 연쇄 표지 조건이 통과하면 전체 학습 후보로 올립니다.

## 실험 예시

<!-- xp -->
<figure class="xp"><p class="xp-t">무엇을 바꿔 학습했나: 질문을 지운 쪽과 남긴 쪽</p><div class="xp-cols"><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div></div><div class="xp-del"><div class="xp-role">user</div><div class="">Find the last three digits of the product of the positive roots of …</div></div><div class="xp-ctx"><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><span class="xp-mask">Okay</span>, so I need to find the last three digits …</div></div><div class="xp-name">L1: 질문을 지우고 라벨을 뺌</div></div><div class="xp-card"><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">system</div><div class="">Please reason step by step, and put your final answer within \boxed{}.</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">user</div><div class="">Find the last three digits of the product of the positive roots of …</div><div class="xp-sp">&lt;|im_end|&gt;</div></div></div><div class="xp-turn"><div class="xp-ctx"><div class="xp-sp">&lt;|im_start|&gt;</div><div class="xp-role">assistant</div></div><div class=""><span class="xp-mask">Okay</span>, so I need to find the last three digits …</div></div><div class="xp-name">L2: 질문을 남기고 라벨을 뺌</div></div></div><div class="xp-legend"><span><i class="xp-sw" style="box-shadow:inset 0 0 0 2px var(--xp-ctx)"></i>입력으로 읽기만 함(채점 안 함)</span><span><i class="xp-sw" style="background:var(--xp-del)"></i>입력에서 지움</span><span><i class="xp-sw" style="background:var(--xp-mask)"></i>입력에는 있고 채점만 뺌(라벨 −100)</span><span><i class="xp-sw" style="background:var(--sheet);border-color:var(--ink)"></i>다음 토큰을 맞히도록 채점</span></div><p class="xp-cap">모델은 Qwen2.5-7B-Instruct에 LoRA(작은 추가 학습)를 400 업데이트 얹은 것입니다. 두 쪽 모두 같은 LIMO 문서 817개를 같은 순서로 학습합니다. 위 그림의 노란 칸은 첫 토큰을 뺀 조건의 예입니다.</p></figure>
<figure class="xp"><p class="xp-t">조건별로 채점에서 빠지는 토큰: 학습 자료 첫 문서의 실제 토큰(질문을 지운 L1)</p><div class="xp-tbl"><table><tr><th>토큰 위치</th><th>0</th><th>1</th><th>2</th><th class="gap">…</th><th>44</th><th>45</th><th>46</th><th class="gap">…</th><th>68</th><th>69</th><th>70</th><th class="gap">…</th><th>243</th><th>244</th><th>245</th><th class="gap">…</th><th>477</th><th>478</th><th>479</th></tr><tr><th>토큰</th><td>Okay</td><td>,</td><td>␣so</td><td class="gap"></td><td>.</td><td>␣Hmm</td><td>,</td><td class="gap"></td><td>␣⏎⏎</td><td>The</td><td>␣equation</td><td class="gap"></td><td>.⏎⏎</td><td>Alternatively</td><td>,</td><td class="gap"></td><td>␣is</td><td>␣</td><td>1</td></tr><tr><td><b>입력 token ID</b></td><td>32313</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td></tr><tr><td>아무것도 안 뺌 (plain)</td><td>32313</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td></tr><tr><td>첫 토큰만 (first_only)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td></tr><tr><td>첫 토큰 + 표지 전부 (trans_all)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td></tr><tr><td>첫 토큰 + 연쇄 표지 (trans_chain)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td></tr><tr><td>첫 토큰 + 문단 첫 토큰 (para_first)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td class="m">−100</td><td>23606</td><td class="gap"></td><td>382</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td></tr><tr><td>첫 토큰 + 무작위 대조 (random_sham)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td class="m">−100</td><td>16</td></tr></table></div><p class="xp-cap">노란 칸의 −100은 그 자리의 예측을 채점하지 않는다는 뜻입니다. 입력에는 그대로 남습니다. 무작위 대조는 표지와 같은 개수의 토큰을 무작위로 뺍니다. 이 문서의 2,266토큰 가운데 다섯 구간만 보였습니다.</p></figure>
<figure class="xp"><p class="xp-t">질문을 남긴 실험(L2)의 조건: 같은 문서, 같은 구간</p><div class="xp-tbl"><table><tr><th>토큰 위치</th><th>0</th><th>1</th><th>2</th><th class="gap">…</th><th>44</th><th>45</th><th>46</th><th class="gap">…</th><th>68</th><th>69</th><th>70</th><th class="gap">…</th><th>243</th><th>244</th><th>245</th><th class="gap">…</th><th>477</th><th>478</th><th>479</th><th class="gap">…</th><th>12</th><th>13</th><th>14</th><th class="gap">…</th><th>32</th><th>33</th><th>34</th></tr><tr><th>토큰</th><td>Okay</td><td>,</td><td>␣so</td><td class="gap"></td><td>.</td><td>␣Hmm</td><td>,</td><td class="gap"></td><td>␣⏎⏎</td><td>The</td><td>␣equation</td><td class="gap"></td><td>.⏎⏎</td><td>Alternatively</td><td>,</td><td class="gap"></td><td>␣is</td><td>␣</td><td>1</td><td class="gap"></td><td>␣the</td><td>␣product</td><td>␣of</td><td class="gap"></td><td>log</td><td>_{</td><td>1</td></tr><tr><td><b>입력 token ID</b></td><td>32313</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td><td class="gap"></td><td>279</td><td>1985</td><td>315</td><td class="gap"></td><td>839</td><td>15159</td><td>16</td></tr><tr><td>아무것도 안 뺌 (q_plain)</td><td>32313</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td><td class="gap"></td><td>279</td><td>1985</td><td>315</td><td class="gap"></td><td>839</td><td>15159</td><td>16</td></tr><tr><td>첫 토큰만 (q_first)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td><td class="gap"></td><td>279</td><td>1985</td><td>315</td><td class="gap"></td><td>839</td><td>15159</td><td>16</td></tr><tr><td>표지만, 첫 토큰 남김 (q_t)</td><td>32313</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td><td class="gap"></td><td>279</td><td>1985</td><td>315</td><td class="gap"></td><td>839</td><td>15159</td><td>16</td></tr><tr><td>표지 수 맞춘 무작위 (q_rt)</td><td>32313</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td class="m">−100</td><td>16</td><td class="gap"></td><td>279</td><td>1985</td><td>315</td><td class="gap"></td><td>839</td><td>15159</td><td>16</td></tr><tr><td>문단 첫 토큰만, 첫 토큰 남김 (q_p)</td><td>32313</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td class="m">−100</td><td>23606</td><td class="gap"></td><td>382</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td><td class="gap"></td><td>279</td><td>1985</td><td>315</td><td class="gap"></td><td>839</td><td>15159</td><td>16</td></tr><tr><td>문단 수 맞춘 무작위 (q_rp)</td><td>32313</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td><td class="gap"></td><td>279</td><td class="m">−100</td><td>315</td><td class="gap"></td><td>839</td><td class="m">−100</td><td>16</td></tr><tr><td>첫 토큰 + 표지 (q_trans_all)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td><td class="gap"></td><td>279</td><td>1985</td><td>315</td><td class="gap"></td><td>839</td><td>15159</td><td>16</td></tr><tr><td>첫 토큰 + 문단 (q_para_first)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td class="m">−100</td><td>23606</td><td class="gap"></td><td>382</td><td class="m">−100</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td><td class="gap"></td><td>279</td><td>1985</td><td>315</td><td class="gap"></td><td>839</td><td>15159</td><td>16</td></tr><tr><td>첫 토큰 + 무작위 (q_random_sham)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td class="m">−100</td><td>16</td><td class="gap"></td><td>279</td><td>1985</td><td>315</td><td class="gap"></td><td>839</td><td>15159</td><td>16</td></tr><tr><td>첫 토큰 + 문단 수 무작위 (q_rp0)</td><td class="m">−100</td><td>11</td><td>773</td><td class="gap"></td><td>13</td><td>88190</td><td>11</td><td class="gap"></td><td>4710</td><td>785</td><td>23606</td><td class="gap"></td><td>382</td><td>92014</td><td>11</td><td class="gap"></td><td>374</td><td>220</td><td>16</td><td class="gap"></td><td>279</td><td class="m">−100</td><td>315</td><td class="gap"></td><td>839</td><td class="m">−100</td><td>16</td></tr></table></div><p class="xp-cap">첫 토큰을 남긴 조건(q_t, q_p)에서는 위치 0의 Okay가 채점됩니다. 첫 토큰 효과와 표지 효과를 나눠 보려고 만든 조건입니다. 수를 맞춘 무작위 조건은 "라벨을 몇 개 뺐는가"의 영향을 가립니다.</p></figure>
<!-- /xp -->

**학습 자료의 실제 문장과 채점에서 빠지는 토큰.** 자료의 첫 문서 일부입니다. `⟦ ⟧`로 표시한 토큰이 "표지 전부" 조건에서 채점에서 빠집니다.

```text
⟦Okay⟧, so I need to find the last three digits of the product of the positive roots of the
equation √(1995) * x^(log_{1995} x) = x².⟦ Hmm⟧, let's see. First, let me try to understand the ...
```

그 뒤의 `, let's see. First, ...`는 그대로 채점합니다. 즉 `Hmm` 다음에 올 내용은 배우되, `Hmm`을 낼지 말지는 배우지 않습니다.

**평가 문제와 답의 시작.** 문항 443은 등차수열 문제입니다(정답 45).

```text
What is the integer value of x in the arithmetic sequence 3^2, x, 3^4?
```

| 조건 | 첫 부분 | 토큰 |
|---|---|---:|
| Base | `To determine the integer value of x ...` | 326 |
| 아무것도 안 뺌 | `Okay, so I need to find the integer value of x ...` | 572 |
| 첫 토큰만 뺌 | `To find the integer value of x ...` | 320 |
| + 표지 전부 | `To find the integer value of x ...` | 387 |

첫 토큰을 채점에서 빼면 모델이 원래의 `To` 말투를 유지합니다.

**되풀이 고리의 실제 예.** 문항 92는 해적이 섬 7개에서 보물을 찾는 확률 문제입니다(정답 448/15625). "아무것도 안 뺌" 조건의 답 하나는 32,000토큰까지 가면서 끝이 이렇게 됩니다.

```text
... 17.92 is 17.92. Wait, 17.92 is 17.92. Wait, 17.92 is 17.92. Wait, 17.92 is 17.92. Wait, ...
```

**채점.** 답의 `\boxed{}` 안 값을 뽑아 저장된 정답 판정표와 비교합니다. 답을 내지 못하면 오답입니다.

## 결과

| 조건 | 정답률 | 평균 토큰 | Wait/1,000토큰 | 상한 도달 | 토큰 비 | 정답률 차 | 판정 |
|---|---:|---:|---:|---:|---:|---:|---|
| Base (참고) | 51.6% | 823 | 0.00 | 0/64 | | | |
| 아무것도 안 뺌 | 43.8% | 15,424 | 16.03 | 28/64 | | | |
| 첫 토큰만 뺌 (기준) | 59.4% | 8,126 | 0.25 | 14/64 | | | |
| + 표지 전부 | 45.3% | 7,576 | 0.00 | 12/64 | 0.93 | −14.1%p | 탈락 |
| + 연쇄 표지만 | 50.0% | 6,875 | 0.03 | 11/64 | 0.85 | −9.4%p | 보류 |
| + 문단 첫 토큰 | 50.0% | 4,766 | 0.00 | 7/64 | 0.59 | −9.4%p | 통과 |
| + 무작위 (대조) | 53.1% | 8,062 | 0.42 | 13/64 | 0.99 | −6.2%p | 탈락 |

**표 읽는 법.** 답마다 8문제 × 8번 = 64개입니다. 토큰 비와 정답률 차는 "첫 토큰만 뺌"과 비교한 값입니다. 문제 수가 적어 정답률은 ±13%p 안팎으로 흔들립니다.

**미리 정한 판정.**

- ① 양성 대조 통과(16.03 대 0.25).
- ② 표지 전부 탈락, 연쇄 표지 보류, 문단 첫 토큰 통과, 무작위 대조 탈락.
- ③ 표지를 뺀 세 조건은 모두 무작위 대조보다 `Wait`와 토큰이 적습니다.
- 후속 규칙: 표지 전부나 연쇄 표지 조건이 통과하지 못했으므로 **전체 학습 후보는 생기지 않습니다.**

## 결과를 보고 따로 살펴본 것

이 절은 결과를 본 뒤 만든 분석이라 판정을 바꾸지 않습니다.

**1. 비교 기준에 `Wait`가 거의 없습니다.** "아무것도 안 뺌"은 답의 62.5%에 `Wait`가 있지만 "첫 토큰만 뺌"은 6.2%뿐입니다. 전체 학습 모델의 `Wait`(1,000토큰당 약 4개)보다 훨씬 적습니다. 비교 대상에 `Wait`가 없는데 `Wait`를 뺀다고 차이가 날 수 없습니다. 양성 대조는 규칙으로는 통과했지만, 본래 알고 싶던 "표지 제외의 효과"를 볼 수 있는 상태는 아니었습니다.

**2. 토큰 차이는 대부분 되풀이 고리에서 왔습니다.** 상한에 닿은 답은 끝부분의 67–92%가 같은 조각의 반복입니다. 상한 안에서 끝난 답끼리 비교하면 "문단 첫 토큰"의 평균 1,421토큰은 "첫 토큰만"의 1,441토큰과 같습니다. 즉 0.59배는 상한 도달이 14개에서 7개로 줄어서 나온 값입니다.

| 조건 | 상한 안에서 끝난 답 | 그 답의 평균 토큰 |
|---|---:|---:|
| Base | 64 | 823 |
| 아무것도 안 뺌 | 36 | 2,532 |
| 첫 토큰만 뺌 | 50 | 1,441 |
| + 표지 전부 | 52 | 1,940 |
| + 연쇄 표지만 | 53 | 1,661 |
| + 문단 첫 토큰 | 57 | 1,421 |
| + 무작위 | 51 | 1,961 |

**3. 대조의 양이 다릅니다.** 무작위 대조는 "표지 전부"와 같은 0.55%를 뺐습니다. "문단 첫 토큰"은 2.62%로 4.7배 많이 뺍니다. 많이 빼서 달라진 것인지 문단 첫 토큰이어서 달라진 것인지 이 실험으로는 알 수 없습니다.

**4. 문제를 다시 뽑아 구한 95% 범위(첫 토큰만 뺀 조건 대비).**

| 조건 | 토큰 비 | 정답률 차 |
|---|---|---|
| + 표지 전부 | 0.49–1.13 | −31.2 – 0.0%p |
| + 연쇄 표지만 | 0.37–1.34 | −20.3 – +1.6%p |
| + 문단 첫 토큰 | 0.23–0.99 | −23.4 – +3.1%p |
| + 무작위 | 0.74–1.14 | −17.2 – +3.1%p |

토큰 비의 범위가 넓어 어느 조건도 확정적이지 않습니다.

## 그래서 무슨 뜻인가

- 첫 토큰 라벨 제외가 긴 추론 진입을 크게 줄이는 현상은 이 작은 학습에서도 보였습니다. 이 관찰 자체는 [이미 보고되어 있습니다](https://arxiv.org/abs/2610.34350).
- 표지를 빼면 효율이 좋아지는지는 **아직 모릅니다.** 이 실험은 그것을 볼 수 있는 조건이 아니었습니다.
- 문단 첫 토큰 제외의 통과를 그대로 믿지 않습니다. 되풀이 고리가 줄어든 효과이고, 정답률 추정치는 9.4%p 낮으며, 양이 맞는 대조도 없습니다. 다만 "문단 머리에서 무엇을 쓸지 정하는 학습이 되풀이 고리에 관여한다"는 가설은 다시 재 볼 만합니다.

## 다른 연구와 겹치는가

전환 표지 토큰만 학습 채점에서 빼는 실험은 지금까지 찾지 못했습니다. 찾지 못했다는 것이 없다는 보장은 아닙니다. 가까운 연구로는 문장 머리의 토큰을 작은 모델에 맡기는 생성 방법 [FoReaL-Decoding](https://arxiv.org/abs/2506.06998)이 있습니다. 이 방법은 학습이 아니라 생성 단계입니다. 표지 뒤 행동이 대부분 확인이라는 관찰은 [First Try Matters](https://arxiv.org/abs/2510.08308)에 있습니다. 전체 학습으로 올리면 그 전에 다시 찾습니다.

## 한계

- 400번 갱신만 한 작은 학습이라 전체 학습 모델과 다른 상태입니다. 답의 최대 44%가 되풀이 고리로 끝납니다.
- 문제가 8개입니다. 정답률 차이는 대부분 흔들림 범위 안입니다.
- 문제 8개 중 항상 긴 문제가 2개이고 거의 안 긴 문제가 5개여서 전체 분포와 다릅니다.

## 다음에 할 일

실험을 고쳐 지금 다시 돌리고 있습니다.

- 문제를 **지우지 않고** 학습합니다. 질문을 남긴 채 표지만 빼면 질문을 지우는 방법의 대안이 될 수 있어서, 더 새로운 쪽입니다.
- 첫 토큰을 **남긴** 조건을 추가했습니다. 이러면 비교 기준에 `Wait`가 살아 있어 표지를 뺀 효과가 보입니다.
- 무작위 대조의 양을 표지 조건과 문단 조건 각각에 **똑같이** 맞췄습니다.
- 토큰 감소가 되풀이 고리 때문이기만 하면 "효율 개선"으로 부르지 않기로 미리 정했습니다.

## 일지에서의 실험 번호

개발일지와 연구일지에서는 L1로 적었습니다. 후속 실험은 L2입니다.
