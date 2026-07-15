# Hook Scorer
 
This is an LLM-based evaluator for direct-response video ad hooks, which are the first two or three seconds that decide whether someone keeps watching the ad or scrolls past it.
 
Paste in a hook, get back structured scores across four dimensions, the reasoning behind them, and a stronger rewrite.
 
**Live:** https://hook-scorer.streamlit.app
**Stack:** Python, Anthropic API (forced tool use for structured output), Streamlit
 
---
 
## Why I built it
 
I wanted to understand the actual difficulty of teaching a model to evaluate creative quality. The interesting problem turned out not to be getting a score out of an LLM but rather getting a score I could *trust*, and then finding out where that trust broke.
 
---
 
## How it works
 
**Structured output via forced tool use.** The model is given a `score_hook` tool with a typed schema and `tool_choice` set to require it. It cannot respond in prose. Every call returns parseable JSON or fails.
 
**Four dimensions, scored 1–5:**
 
| Dimension | Question it answers |
|---|---|
| Attention | Does it stop the scroll in the first three seconds? |
| Clarity | Is the value proposition immediately legible? |
| Specificity | Concrete claim or vague hype? |
| Tension | Does it make the viewer crave resolution? |
 
The rubric resides in the system prompt and is anchored with few-shot examples at both ends of the scale. The scale is defined explicitly because the middle is where things get fuzzy and scorers deliver mediocre results.
 
- **1** — Not a hook. Corporate announcement, feature-led.
- **2** — Attempts a hook, but generic. Hype vocabulary, empty curiosity, interchangeable across products.
- **3** — Competent and forgettable. One real ingredient, missing the rest.
- **4** — Compelling. Makes the viewer crave resolution.
- **5** — Stops the viewer from scrolling. Specific, surprising, and it costs the speaker something.
---
 
## Evals
 
A tool that scores creative is worthless if I can't tell whether the scores are any good. So the scorer is evaulated against an established gold standard.
 
**Method:** 15 hand-labeled hooks spanning the full scale. `evals.py` runs the scorer against them and reports two metrics:
 
- **Mean absolute error** — how far off the scores are on average
- **Exact agreement** — how often the scorer lands on the expected overall score exactly
Both are included because they each fail in different ways. A scorer that's always off by one has a decent mean absolute error and poor agreement. That means the scale is miscalibrated and should be fixed in the rubric. A scorer that is usually perfect but occasionally off by three has good agreement and a bad mean absolute error. This type of scorer has blind spots on specific kinds of hooks, which is a different and harder problem.
 
**Results:**
 
| Rubric version | Mean absolute error | Exact agreement |
|---|---|---|
| v1 — dimensions only | 0.47 | 8/15 |
| v2 — added few-shot failure cases | 0.73 | 5/15 |
 
---
 
**v2 scored worse on both metrics — and understanding *why* was the most useful part of this project.**
 
I added examples to the system prompt to force the model to score each dimension independently in addition to examples that gave context for a low, middle-of-the-road, and high score. It did change the model's behavior. But instead of improving against my golden set, mean absolute error rose and exact agreement fell.
 
## What actually happened
 
The errors aren't random. Of the ten hooks where the model disagreed with my label, **all ten are cases where the model scored *lower* than I did. Not one is higher.**
 
The v2 examples didn't make the scorer noisier. They made it *harsher*, shifting its read of the entire scale down by roughly a point. And because my labels were written against the v1 scale, every score slid off in the same direction at once.
 
The evidence that this is calibration and not a breakdown in judgment: **the model's ranking is almost entirely preserved.** The hooks I scored 5 still land at the top; the 1s still sit at the bottom. What moved was the absolute scale, not the ordering. A metric built on exact agreement punishes a uniform shift severely even though a shift is the most benign kind of error there is, because it's correctable with a single recalibration.
 
## Where it actually breaks
 
Two real weaknesses, separate from the calibration shift:
 
**One genuine taste disagreement.** The only 2-point miss was *"Three things your dentist won't tell you"*. I scored it 4, the model scored it 2. The model doesn't rate the insider-knowledge curiosity gap the way I do. That's not a scale problem. That's just the model and I actually disagreeing about whether a familiar-but-effective hook structure is good. Which of us is right is an empirical question, and the answer lives in performance data I don't have, not in either of our opinions.
 
**The floor compresses the low end.** Several hooks I scored 2 got pushed to 1. Once the model turns harsh, everything soft piles up against the bottom of the scale and the distinction between "bad" and "actively generic" collapses.
 
**What it got right, that I'd expected to fail:** I seeded the set with a form-vs-substance trap, a hollow hook with the *structure* of a strong one (*"I threw out all my skincare. You won't believe what happened."*, labeled 2) next to its substantive twin (*"I threw out $600 of skincare last month. My skin's never been clearer."*, labeled 5). I expected the model to be fooled by the shared grammar and over-score the hollow one. It wasn't though. It scored them 2 and 5, exactly as labeled. In this run, the model read substance, not just form.
 
## The real lesson
 
The thing I'll take from this: **making a scorer more discriminating can make it look worse against imperfect ground truth.** My labels are one person's judgment, fixed at a moment in time. When I sharpened the model, the model and the labels drifted apart. With only exact-agreement and absolute-error to go on, I can't tell "the model got worse" from "the model got stricter and my labels didn't move." Those need to be distinguishable, and right now they aren't.
 
## What I'd do next
 
1. **Measure ranking, not just absolute error.** A rank correlation (either Spearman or Kendall) between the model's scores and the labels would be nearly unaffected by a uniform shift and would have told me immediately that v2 preserved the ordering while moving the scale. Absolute error alone hid that. This is the first thing I'd add.
2. **Recalibrate instead of reverting.** The v2 model is more discriminating; it's just centered a point low. A single anchoring example ("this hook is a 3, here's why") or a post-hoc offset would likely recover the metric *without* losing the sharper judgment. Reverting throws away the improvement to fix the symptom.
3. **Ground truth from performance data, not my taste.** The dentist disagreement is the tell: my rubric is a hypothesis, and where the model and I disagree, neither of us is authoritative. With a library of ads and their actual results, the scorer should be graded against what *converted* — and so should I. That's the change that turns this from plausible to useful.
4. **Build the golden set with strategists, and measure their disagreement.** One labeler is a single point of view. A real golden set is multi-labeled, and the hooks where *experts* disagree are exactly where the model's job is hardest and where I'd focus evaluation.
5. **Log every override in production.** When a strategist reads a score and does the opposite, that's the signal — either the model is wrong or it's teaching them something, and both are training data for the next version.
 
## Running it
 
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
 
python scorer.py      # score a single hook
python evals.py       # run the golde standard
streamlit run app.py  # the UI
```
