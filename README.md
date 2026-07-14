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
 
**Method:** [N] hand-labeled hooks spanning the full scale. `evals.py` runs the scorer against them and reports two metrics:
 
- **Mean absolute error** — how far off the scores are on average
- **Exact agreement** — how often the scorer lands on the expected overall score exactly
Both are included because they each fail in different ways. A scorer that's always off by one has a decent mean absolute error and poor agreement. That means the scale is miscalibrated and should be fixed in the rubric. A scorer that is usually perfect but occasionally off by three has good agreement and a bad mean absolute error. This type of scorer has blind spots on specific kinds of hooks, which is a different and harder problem.
 
**Results:**
 
| Rubric version | Mean absolute error | Exact agreement |
|---|---|---|
| v1 — dimensions only | [X] | [X/N] |
| v2 — added few-shot failure cases | [X] | [X/N] |
 
---
 
## Where it breaks
 
The most useful thing I found.
 
**The model reads the grammar of a good hook and mistakes it for quality.** It scores a hook with the surface-level markers of strong creativity, and it scores that hook well even when there is nothing of substance underneath.
 
The clearest case in my golden set:
 
| Hook | My label | Model |
|---|---|---|
| "I threw out $600 of skincare last month. My skin's never been clearer." | 5 | [X] |
| "I threw out all my skincare. You won't believe what happened." | 2 | [X] |
 
These two hooks contain the same confessional and imply the same payoff. However, one has a number and a claim while the other has neither. [What the model did.]
 
TAKEAWAY: **form is learnable from text, substance isn't**. The model has no way to know that the second hook is hollow, because substance is not a property of the sentence. It is a property of the sentence relative to what actually draws in the viewer.
 
---
 
## What I would do next
 
1. **Ground it in performance data.** The rubric is my taste, which makes it a hypothesis, not gospel. With a library of ads and their actual results, the scorer should be retrieving comparable high- and low-performing hooks and scoring against what drew in the user rather than against what the model thought sounded clever. This is the most significant change that would move it from plausible to useful.
2. **Build the eval set with the people who do this for a living.** My labels are one person's judgment. A real gold standard is strategist-labeled, with disagreement between labelers measured rather than averaged away because where the experts disagree is exactly where the model's job is hardest.
3. **Log every score and every override.** The signal that matters isn't whether strategists *use* the tool, it's when they *overrule* it. That's the training set for version two.
4. **Tier the models.** A cheap model can triage obvious 1s and 2s; the expensive one earns its cost on the 3-vs-4 boundary, where judgment actually lives.
---
 
## Running it
 
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
 
python scorer.py      # score a single hook
python evals.py       # run the golde standard
streamlit run app.py  # the UI
```
