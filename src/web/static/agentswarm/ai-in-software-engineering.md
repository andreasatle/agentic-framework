# What the Documented Cases Show: AI in Software Engineering and IT Operations, Measured and Unmeasured

## Introduction: how to read AI productivity claims

Feeling faster and finishing faster are different questions; GitHub Next used both surveys and a controlled experiment to investigate Copilot’s effects (github.blog: Research: quantifying GitHub Copilot’s…).
This post separates **measured results** from controlled experiments and field studies, **company/vendor claims** attributed to their makers, and **surveys** naming who ran them and how many were asked, where reported.
We’ll examine coding assistants, code review, a code migration and incident root-causing, asking what was automated, what people reviewed and what was measured.
The sources contain no IT service desk case, so none is covered.

## Coding assistants: controlled experiments and field experiments

### Peng et al.: one timed task

**Measured, 2023:** Peng et al. randomly assigned 95 professional developers to implement an HTTP server in JavaScript with or without GitHub Copilot, which suggests code from context (arxiv.org: [2302.06590] The Impact of…).
Completion time ran from repository creation until all 12 correctness tests passed; among finishers, the Copilot group finished 55.8% faster, with a 95% confidence interval of 21–89% (arxiv.org: [2302.06590] The Impact of…).
Less-experienced developers, older developers and those coding more hours daily benefited more; this was one standardized task, not collaborative project work, and code quality was not examined (arxiv.org: [2302.06590] The Impact of…).

### GitHub Next: perceptions alongside experiments

**Survey:** GitHub Next combined surveys and experiments, surveying more than 2,000 developers; 73% reported help staying in flow and 87% reported conserving mental effort on repetitive tasks (github.blog: Research: quantifying GitHub Copilot’s…).
The survey findings are self-reported, but GitHub’s post also reports a timed experiment: 95 professional developers were split randomly into two groups and timed on writing an HTTP server in JavaScript (github.blog: Research: quantifying GitHub Copilot’s…).
The post questions whether outputs over inputs fit the complex problem solving and creativity of development work (github.blog: Research: quantifying GitHub Copilot’s…).
GitHub Next ran the HTTP-server experiment in partnership with Microsoft’s Office of the Chief Economist (github.blog: Research: quantifying GitHub Copilot’s…).

### Cui et al.: ordinary workplace tasks

**Measured, February 2025:** Cui et al. analyzed three company-run randomized controlled trials (RCTs), which randomly assigned Copilot access at Microsoft and Accenture and rollout dates at an anonymous Fortune 100 company (economics.mit.edu: [PDF] The Effects of…).
Across 4,867 developers, their preferred pooled estimate was 26.08% more completed weekly tasks, measured through pull requests (standard error: 10.3%); this estimates adoption’s effect on users, adjusting for imperfect take-up, rather than simply access (economics.mit.edu: [PDF] The Effects of…).
They also tracked commits, builds and build success; pooled increases were 13.55% for commits (SE: 10.0%) and 38.38% for builds (SE: 12.55%) (economics.mit.edu: [PDF] The Effects of…).
Individual experiments were noisy: low adoption, short rollout differences and variable output limited precision; build success declined at Accenture (economics.mit.edu: [PDF] The Effects of…).
At Microsoft, Copilot significantly raised task completion for more recent hires and junior developers but not for longer-tenure and senior developers (economics.mit.edu: [PDF] The Effects of…, p. 14).
Developers chose which suggestions to accept, and pull requests still went through human review before merging (economics.mit.edu: [PDF] The Effects of…, p. 6).

## Code review: Google and Cloudflare

Both cases automate part of code review, but they differ in what they claim and how they measure it.
Google's account is a peer-reviewed paper with an internal evaluation; Cloudflare's is the company's own blog post.

### Google: AutoCommenter checks coding best practices

Vijayvergiya et al. (2024) describe AutoCommenter, a large-language-model system that flags coding best-practice violations in code under review (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).
It covers C++, Java, Python and Go, and was deployed to tens of thousands of Google developers (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).
Human reviewers still judge functionality; the system aims to free them from best-practice checks (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).
Developers can give thumbs up or thumbs down feedback on each comment (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).

The paper reports an A/B experiment in July 2023 on about half of developers, a measured result (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).
The control and treatment groups did not differ significantly in total review duration, active review time or comment-response iterations, though coding speed improved slightly (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).
The "useful ratio" (positive feedback over all feedback) plateaued at around 54% after several months of early usage (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).
Suppressing 17 non-actionable URLs raised it to 66%, and suppression plus manually updated summaries reached the 80% target for the next stage of deployment (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).
The 80% is a historical estimate computed on past feedback, not a measured live result (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).
The paper states that ground-truth labels are incomplete, so its precision and recall figures are "noisy" (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).

### Cloudflare: an orchestrated multi-reviewer system

Skidmore's post is the company's own account and reports no controlled experiment (blog.cloudflare.com: Orchestrating AI Code Review…).
Cloudflare described a queue of merge requests waiting for review, and said that across its internal projects the median wait time for a first review was often measured in hours (blog.cloudflare.com: Orchestrating AI Code Review…).
The post does not state a goal for the project in those words; it frames the problem as a bottleneck (blog.cloudflare.com: Orchestrating AI Code Review…).
A single prompt on a git diff was too noisy, so Cloudflare built a CI-native system around the OpenCode coding agent (blog.cloudflare.com: Orchestrating AI Code Review…).
A coordinator agent runs up to seven specialised reviewers, then deduplicates findings, judges severity and posts one structured comment (blog.cloudflare.com: Orchestrating AI Code Review…).

The post reports telemetry from 5,169 repositories, 10 March to 9 April 2026: 131,246 review runs, a median review time of 3 minutes 39 seconds, and "break glass" overrides on 0.6% of merge requests (blog.cloudflare.com: Orchestrating AI Code Review…).
These are operational counts with no control group and no before-and-after wait-time comparison (blog.cloudflare.com: Orchestrating AI Code Review…).
The post says the system "isn't a replacement for human code review" and lists its limits, including architectural awareness and subtle concurrency bugs (blog.cloudflare.com: Orchestrating AI Code Review…).

## Code migration: Amazon Q and Java upgrades

Amazon's goal, as Andy Jassy describes it, is to make the tedious work of updating foundational software less dreaded and less often put off (linkedin.com: How Amazon Q automates…).
The capability is a code transformation feature of Amazon Q, Amazon's GenAI assistant for software development, applied to Amazon's own needed Java upgrades (linkedin.com: How Amazon Q automates…).
The post does not describe how the transformation works internally.

These figures are company claims and estimates, not independent measurements, and the post gives no method for computing them (linkedin.com: How Amazon Q automates…).

- Company claim: the average time to upgrade an application to Java 17 "plummeted from what's typically 50 developer-days to just a few hours" (linkedin.com: How Amazon Q automates…).
- Company estimate: Amazon "estimate[s] this has saved us the equivalent of 4,500 developer-years of work" (linkedin.com: How Amazon Q automates…).
- Company claim: "In under six months," Amazon upgraded "more than 50%" of its production Java systems (linkedin.com: How Amazon Q automates…).

The post also says developers "shipped 79% of the auto-generated code reviews without any additional changes" (linkedin.com: How Amazon Q automates…).

The post does not say how many defects, if any, the upgrades introduced, and it reports no control group or independent check of the time savings (linkedin.com: How Amazon Q automates…).

## Incident response: root-causing cloud incidents at Microsoft

This case is a research paper, and its source page is short.
Zhang et al. (FSE 2024, industry track) use GPT-4 with in-context learning (worked examples placed in the prompt, with no retraining) for root cause analysis (RCA) of cloud incidents (microsoft.com: Automated Root Causing of…).
RCA requires on-call engineers to identify primary issues and implement corrective actions (microsoft.com: Automated Root Causing of…).
The authors avoid fine-tuning GPT-4 because it demands heavy GPU resources and continual retraining as new data arrives (microsoft.com: Automated Root Causing of…).
The evaluation covers more than 100,000 production incidents and compares several large language models on multiple metrics (microsoft.com: Automated Root Causing of…).
This is a company/vendor claim by the authors: the approach beats a fine-tuned GPT-3 model by an average of 24.8% across all metrics and the zero-shot model by 49.7% (microsoft.com: Automated Root Causing of…).
In a human evaluation with actual incident owners, it reports a 43.5% improvement in correctness and an 8.7% improvement in readability over the fine-tuned model (microsoft.com: Automated Root Causing of…).
The page does not say how suggestions reach on-call engineers or what the model's exact inputs and outputs are (microsoft.com: Automated Root Causing of…).
Unproven from this page: it reports no production deployment outcome and no time-to-resolution figures, so the gains are offline results on historical incidents, not measured effects on live response (microsoft.com: Automated Root Causing of…).

## What went wrong: the METR slowdown study

Becker et al.’s 2025 METR randomized controlled trial randomly assigned tasks to allow or disallow AI (arxiv.org: [2507.09089] Measuring the Impact…).
Sixteen experienced open-source developers completed 246 tasks in mature repositories where they averaged 5 years of prior experience (arxiv.org: [2507.09089] Measuring the Impact…).
Developers mainly used Cursor Pro with Claude 3.5/3.7 Sonnet (arxiv.org: [2507.09089] Measuring the Impact…).
Allowing AI increased completion time by 19% (arxiv.org: [2507.09089] Measuring the Impact…).
Developers forecast a 24% speedup beforehand and estimated 20% afterward (arxiv.org: [2507.09089] Measuring the Impact…).
Economics and ML experts predicted 39% and 38% shorter times, respectively (arxiv.org: [2507.09089] Measuring the Impact…).
Of 21 potential slowdown factors, the authors found supporting evidence for 5, mixed or no evidence for 10, and evidence against 6 (arxiv.org: [2507.09089] Measuring the Impact…).
Supported factors included repository familiarity and large, complex repositories (arxiv.org: [2507.09089] Measuring the Impact…).
Experimental artifacts could not be entirely ruled out (arxiv.org: [2507.09089] Measuring the Impact…).
METR describes Peng et al.’s basic HTTP server task as "unrepresentative of most software development work" and likely similar to LLM training data (arxiv.org: [2507.09089] Measuring the Impact…).
The authors describe a "large disconnect" between perceived and actual AI productivity impact (arxiv.org: [2507.09089] Measuring the Impact…).
The METR authors say their results "are consistent with small greenfield projects or development in unfamiliar codebases seeing substantial speedup" (arxiv.org: [2507.09089] Measuring the Impact…, p. 12).
The authors suggest, rather than measure, that benchmarks may overstate real-world AI capability (arxiv.org: [2507.09089] Measuring the Impact…).
They did not measure code quality or security directly; developers reported that AI code needed major clean-up (arxiv.org: [2507.09089] Measuring the Impact…, p. 20).
Whether later models would speed up developers in this setting is unknown (arxiv.org: [2507.09089] Measuring the Impact…, p. 3).

## What the cases have in common, and what to take from them

The strongest lesson is conditional: measured gains on one task are not a promise about every engineering workflow (arxiv.org: [2302.06590] The Impact of…) (arxiv.org: [2507.09089] Measuring the Impact…, p. 3).
Peng’s 2023 controlled experiment measured 55.8% faster completion of a JavaScript server; Cui’s 2025 field experiments used workplace telemetry and estimated 26.08% more completed tasks among Copilot users (SE: 10.3%) (arxiv.org: [2302.06590] The Impact of…) (economics.mit.edu: [PDF] The Effects of…).
Google’s randomized rollout found no statistically significant reduction in review duration or active review time (homes.cs.washington.edu: AI-Assisted Assessment of Coding…).
Cloudflare’s company account describes deployment and internal telemetry, but supplies no quantified first-review wait reduction here (blog.cloudflare.com: Orchestrating AI Code Review…).
Amazon’s migration savings remain Andy Jassy’s company claims and estimates, not controlled measurements (linkedin.com: How Amazon Q automates…).
Microsoft’s incident study measured better root-cause outputs, including incident-owner ratings—not demonstrated reductions in downtime (microsoft.com: Automated Root Causing of…).
GitHub Next’s survey of more than 2,000 developers captures perceived benefits, a different outcome from timed work (github.blog: Research: quantifying GitHub Copilot’s…).

For your own rollout:

- The METR study defined tasks before randomizing them and used a fixed outcome measure, speedup on those tasks, while using unfiltered, "live" open-source repository tasks rather than synthetic or cherry-picked ones (arxiv.org: [2507.09089] Measuring the Impact…).
- Include review and rework time, and do not substitute impressions for outcomes: METR participants forecast 24% shorter times and afterward estimated 20% shorter times, despite a measured 19% slowdown (arxiv.org: [2507.09089] Measuring the Impact…).
- Keep human review: Copilot developers select suggestions, Google reviewers retain merge authority, and Cloudflare provides a human override (economics.mit.edu: [PDF] The Effects of…) (homes.cs.washington.edu: AI-Assisted Assessment of Coding…) (blog.cloudflare.com: Orchestrating AI Code Review…).
- Treat vendor savings as claims until the evaluation method supports more (linkedin.com: How Amazon Q automates…).

The evidence leaves long-term quality and security largely unproven, and results may not transfer across tasks or settings (arxiv.org: [2302.06590] The Impact of…) (economics.mit.edu: [PDF] The Effects of…) (arxiv.org: [2507.09089] Measuring the Impact…, p. 3).
These sources contain no IT service desk case, and the Microsoft source covers cloud incident root-cause analysis instead (microsoft.com: Automated Root Causing of…).

## References

- arxiv.org (2023). [*[2302.06590] The Impact of AI on Developer Productivity: Evidence from GitHub Copilot*](https://arxiv.org/abs/2302.06590). arxiv.org (scholarly).
- arxiv.org (2025). [*[2507.09089] Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity*](https://arxiv.org/abs/2507.09089). arxiv.org (scholarly).
- blog.cloudflare.com (n.d.). [*Orchestrating AI Code Review at scale | Cloudflare Blog*](https://blog.cloudflare.com/ai-code-review). blog.cloudflare.com (official).
- economics.mit.edu (n.d.). [*[PDF] The Effects of Generative AI on High-Skilled Work - MIT Economics*](https://economics.mit.edu/sites/default/files/inline-files/draft_copilot_experiments.pdf). economics.mit.edu (scholarly).
- github.blog (n.d.). [*Research: quantifying GitHub Copilot’s impact on developer productivity and happiness - The GitHub Blog*](https://github.blog/news-insights/research/research-quantifying-github-copilots-impact-on-developer-productivity-and-happiness). github.blog (commercial).
- homes.cs.washington.edu (n.d.). [*AI-Assisted Assessment of Coding Practices in Modern ...*](https://homes.cs.washington.edu/~rjust/publ/code_review_automation_aiware_2024.pdf). homes.cs.washington.edu (scholarly).
- linkedin.com (n.d.). [*How Amazon Q automates software development with GenAI | Andy Jassy posted on the topic | LinkedIn*](https://www.linkedin.com/posts/andy-jassy-8b1615_one-of-the-most-tedious-but-critical-tasks-activity-7232374162185461760-AdSz). linkedin.com (official).
- microsoft.com (n.d.). [*Automated Root Causing of Cloud Incidents using In-Context Learning with GPT-4 - Microsoft Research*](https://www.microsoft.com/en-us/research/publication/automated-root-causing-of-cloud-incidents-using-in-context-learning-with-gpt-4). microsoft.com (institutional).
