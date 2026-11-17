# AI banau ya Skill? — faisla

Short answer: **skill**. Yahan kyun, aur kab AI banani padti hai.

| Cheez | Skill (ye repo) | Apna AI (model) |
|---|---|---|
| Kya chahiye | instructions + scripts + tests | data, training compute, eval pipeline, serving |
| Kharcha | ~0 | GPU + engineering + maintenance |
| Reasoning quality | Claude jitni (best-in-class) | jitni tumhara data/scale allow kare |
| "Bina ruke chalta rahe" | loop + round budget se | agent framework phir bhi likhna padega |
| Web research | built-in web search/fetch use karta hai | khud tool-calling + retriever banana padega |
| Update karna | SKILL.md edit | retrain / re-eval |
| Risk | model ka behaviour badal sakta hai | tumhare paas control, par tunhi bugs bhi |
| Time to first value | minutes | weeks-months |

## Skill hi kaafi hai jab...

- Problem "kaise karna hai" type ki hai: plan → build → verify → report.
- Verification machine se ho sakti hai (tests, exit codes, residuals).
- Tool use (shell, files, web) chahiye — Claude Code already deta hai.

## Apna model tabhi banao jab...

1. **Data moat**: tumhare paas aisa labelled data hai jo kisi model me nahi
   (proprietary sensor data, domain labels).
2. **Latency/cost**: per-call cost ya latency aisi hai ki hosted model afford
   nahi hota (bahut high volume, edge device).
3. **Privacy/on-prem**: data bahar nahi ja sakta.
4. **Specialised I/O**: audio/vision/EDA signals jaisa narrow modality jo
   general model theek se nahi karta.

In chaaron me se koi bhi na ho → skill likho, model train mat karo.

## Beech ka rasta (recommended)

1. Pehle **skill** likho (ye repo).
2. Kuch hafte chalao, failures collect karo (`checker` ke FAIL notes).
3. Jo failures **instructions** se theek ho jaate hain → SKILL.md me daal do.
4. Jo failures **knowledge** ki wajah se hain → RAG / docs add karo, retrain
   nahi.
5. Sirf jo bilkul repeatable, narrow, high-volume task bache → usme fine-tune
   ya chhota specialised model socho.

## "Duniya ke a to z physics topics" wali demand

Ise literally solve karne ki koshish mat karo — ye infinite hai aur aisa claim
jhooth hoga. Jo actually kaam karta hai:

- **Definition of Done** machine-checkable banao (test, residual, tolerance).
- **Coverage table** sirf un topics ki jo deliverable ko touch karte hain, aur
  har row me "kahan use hua" likho.
- **Checker** ko units, limits, conservation laws, aur independent recompute
  karwao — ye asli bugs pakadta hai, 500 topics ki list nahi.

Pendulum example isi ka proof hai: 9-row coverage table ne ek 30% error pakda
jo topic-count se kabhi nahi pakda jaata.
