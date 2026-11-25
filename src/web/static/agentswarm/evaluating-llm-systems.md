# Evaluating LLM Systems: A Tutorial on Test Sets, Judges, Calibration, Regression Tests and Score Noise

## What an evaluation score is: a measurement with a question

An evaluation is an experiment, and a score is an estimate of performance on an unseen population of questions, computed from a finite sample[^1].
Treating the questions as drawn at random from a hypothetical super-population means the reported number carries sampling uncertainty[^1].
Benchmark scores can also be heavily influenced by the choice of prompt, and random seeds across initialisations add variance[^2].
Your retrieval evaluation already has this structure: a query set with relevance judgements plays the role of a test set.
The sections that follow cover held-out checks, contamination, LLM judges and their biases, calibration, regression tests, and score noise.
The section on evaluating retrieval-augmented systems by component comes after these, and it is followed by a side-by-side comparison table and a summary with self-check questions.

## Building test sets and held-out checks

A golden dataset is a fixed set of test cases that you run your application against before every meaningful change, where each item records an input and, usually, a reviewed definition of a correct response[^3].
A held-out check is a set of items kept out of all prompt and model tuning, scored only at decision points such as a release, whereas the golden set is run during every iteration.
Because held-out items never inform a change, their score is an independent check on whether the change generalises.
Tuning repeatedly against one set turns it into a training signal, so its score can rise while performance on new inputs does not, which is overfitting to the test set.
Build the set from real production traces first, then from CSV imports, and add synthetic items only where real data is thin, reviewed with the same rigour[^3].
Scope each set to one component or behaviour so that a failure points at a cause[^3].
Practitioner sizing is about 10 items for exploring one issue, tens to low hundreds for a per-pull-request gate, and 100 to 1000 for a full regression set[^3].
Cover every failure mode seen in production, and grow the set from production failures, since a set of easy cases scores well forever[^3].
Maintain the set with schema validation, deduplication, and item versioning, and compare prompt versions by running one experiment per version against the same pinned dataset version[^3].
These sizes are practitioner guidance from the Langfuse Academy datasets module, not a statistical result, and the section on how much noise a score carries takes up how large a set must be[^3].

## Contamination and leakage: detecting benchmark data in training data

Data contamination is the presence of test data from downstream tasks in a model's training data, which may inflate performance and raise questions about the validity of evaluations and benchmarks[^4].
Because the model may have seen the answers during pre-training, a contaminated score is suspect[^4].
Golchin and Surdeanu assume no access to pre-training data and limited compute, so they detect contamination first for single instances and then for a whole partition, meaning one dataset split (train, test or validation)[^4].

Guided instruction gives the model the dataset name, the partition, a random-length initial segment of a reference instance, and its label where one exists, then asks it to finish the instance[^4].
An instance is flagged as contaminated when the completion exactly matches the withheld remainder, or nearly matches it[^4].
The general instruction omits the dataset and partition name, and it establishes a baseline so that the influence of guided instruction can be assessed[^4].
Label integration reduces false positives: a completion under the correct label can be an exact match, while the same segment under a wrong label is only an inexact match[^4].

Overlap is measured with ROUGE-L and BLEURT[^4].
Idea 1 marks a partition as contaminated when the average ROUGE-L or BLEURT overlap is significantly higher under guided than general instruction, tested by a non-parametric bootstrap on ten sampled instances[^4].
Idea 2 uses GPT-4 with few-shot in-context examples as a classifier, flagging a partition when at least one completion is an exact match or at least two are near-exact matches[^4].

Shown experimentally, across seven datasets with train and test or validation partitions, the GPT-4 classifier matched human experts in 14 of 14 partitions for GPT-4 and 13 of 14 for GPT-3.5[^4].
The bootstrap rule matched humans in 13 of 14 GPT-4 partitions with BLEURT and 11 of 14 with ROUGE-L, while on GPT-3.5 ROUGE-L outputs it was at chance (7 of 14)[^4].
The method needs a model that can be queried for completions[^4].
The best-performing method treats exact and near-exact replicas alike as indicators of contamination, and it does not pinpoint the source of contamination[^4].
In practice, keep private test items that are never published, check overlap between the benchmark and model outputs before trusting a score, and refresh sets over time.

## LLM-as-judge: pointwise, pairwise and reference-based, and how well it agrees with humans

Open-ended chatbot answers have no rule-based check, and reference answers are often missing, so string-overlap metrics such as ROUGE and BLEU are ineffective for them[^5].
Human grading is the gold standard but is slow and costly, so Zheng et al. propose a strong LLM as a surrogate judge, which they call LLM-as-a-judge[^5].
They describe three formats that can be used independently or in combination[^5].

- Pairwise comparison: the judge sees a question and two answers and says which is better or declares a tie; it may lack scalability because the number of pairs grows quadratically with the number of players[^5].
- Single-answer grading: the judge assigns a score to one answer; its absolute scores may fluctuate more when the judge model changes, and it may be unable to discern subtle differences between specific pairs[^5].
- Reference-guided grading: the judge is given a reference solution where applicable, with an example prompt for grading math problems[^5].

Setup S1 counts non-tie, tie and inconsistent votes, with inconsistent verdicts (changed after swapping order) counted as ties and random agreement 33%; setup S2 keeps only non-tie votes, with random agreement 50%[^5].
On MT-bench, GPT-4 with single-answer grading reached 85% agreement with humans in S2, above the 81% agreement among humans[^5].
Across both benchmarks the authors report that strong judges reach over 80% agreement, on par with agreement among human experts[^5].
This is a population-level result over many votes, so it does not guarantee that the judge is right on any single item.
MT-bench is a set of 80 multi-turn questions in eight categories, with 10 questions per category[^5].
Chatbot Arena is a crowdsourced platform where users pose the same question to two anonymous models and vote for the preferred response, collecting about 30K votes in one month[^5].
Pairwise votes of this kind are the input to Elo-style ratings, which summarise relative strength from wins and losses.

## Judge biases and how to mitigate them

Position bias is the tendency of a judge to favour a candidate because of where it sits in the prompt rather than what it says[^5].
A simple consistency metric is the share of cases in which the verdict is unchanged after the two answers are swapped[^5].
Shi et al. found experimentally that position consistency varies by judge and task across 15 judges, and that it rises with the quality gap between candidates[^6].
Zheng et al. mitigate this by judging twice with the order swapped and counting a win only when the same answer is preferred both times, treating disagreement as a tie[^5].

Verbosity bias is the preference for longer answers even when they are no clearer or more accurate[^5].
In a repetitive-list attack, a numbered list is rephrased and prepended to itself, and the attack succeeds when the judge prefers the padded answer[^5].
The failure rate was 91.3% for Claude-v1 and GPT-3.5, against 8.7% for GPT-4[^5].
Limited reasoning is a separate weakness, since judges can be misled by a wrong answer shown in the prompt even when they can solve the problem alone[^5].
On ten math questions, the default prompt failed 14 of 20 times, chain-of-thought 6 of 20, and a judge-generated reference answer 3 of 20[^5].

Self-preference bias is the tendency of a judge to rate its own outputs above human ratings[^7].
Wataoka et al. measure it with a Demographic-Parity-based score, where the judge's preference for the first response, $Y'=1$, is compared between its own output and another model's output[^7].
GPT-4 shows the highest self-preference bias, at 0.749, followed by Vicuna-13b at 0.382[^7].
The authors hypothesise that judges favour texts more familiar to them, as indicated by lower perplexity; this is supported by correlational evidence, not proven[^7].

Practical mitigations are to use a judge from a different model family than the system under test, to use an ensemble of judges, and to calibrate against human labels, as the section on calibration describes.

## Calibration: making confidence and judge scores mean something

Calibration asks whether a stated confidence means what it says: a system that reports confidence $p$ should be right a fraction $p$ of the time, so its least confident answers are the likeliest to be wrong and can be deferred to a person[^8].
Expected calibration error (ECE) bins predictions by confidence and averages the gap between accuracy and confidence in each bin, weighted by the fraction of samples in the bin[^8].
The Brier score is the mean squared error between confidence and the 0/1 correctness label[^8].
For example, if 1,000 answers fall in a bin with stated confidence 0.9 and 820 are correct, that bin's gap is 0.08 and it contributes to ECE in proportion to its share of the sample.

RLHF can worsen the calibration of a model's conditional probabilities[^8].
Experimentally, on TriviaQA, SciQ and TruthfulQA, verbalised confidence, where the model states a number or a phrase such as 'highly likely', was often better calibrated than conditional probabilities for ChatGPT, GPT-4 and Claude[^8].
Asking for several answer options before giving the confidence significantly improves verbalised calibration, and combined with temperature scaling it generally beats model probabilities, often reducing ECE by over 50%[^8].
These are experimental findings on specific models and datasets, not a proof that they hold for reasoning tasks, which the authors leave open[^8].

Prediction-powered inference (PPI) uses a small set of human labels to correct a judge's predictions on a much larger unlabelled set and yields confidence intervals[^9].
The estimator can be read as a judge estimate plus a measured rectifier: the mean judge score over unlabelled data, corrected by the average difference between judge and human labels on the labelled subset[^9].
Because the rectifier is estimated from labels, the labelled set can stay small while judge scores on the unlabelled set stay cheap[^9].

## Regression tests for prompts and model versions

A prompt regression test runs a pinned dataset version against each new prompt or model version and compares the scores with a designated baseline[^3].
The suite has a fast gate of tens to low hundreds of items for each pull request, and a full set of 100 to 1000 items for release branches or nightly runs[^3].
Each run is logged as an experiment with its prompt version in the metadata[^3].

A prompt change can shift behaviour without anyone intending it, because answers depend on how an instruction is worded[^10].
ProSA's PromptSensiScore averages the absolute difference in correctness between responses to paraphrases of the same instance[^10].
A test should therefore check several paraphrases of each behaviour, not one wording.

A delta between two versions is a regression only when it exceeds the noise of the comparison.
Madaan et al. show that the seed variance of a 7B model is generally well below the 95% confidence interval for the same benchmark, though the ratio of the two is quite variable[^2].
Because both versions run on the same items, the comparison should use per-item paired differences, as the next section explains.
The judge model and its version must also be pinned, since a changed judge moves scores with no change to the prompt.

- Pin the dataset version, the prompt versions, the model version, and the judge model with its version.
- Run the fast gate on every pull request that touches a prompt[^3].
- Compare each candidate with the baseline, and read the item-level rows that changed most[^3].
- Fail the gate when the paired delta exceeds the noise threshold, and run the full set before release.

## How much noise does a score carry?

Every eval score is a sample mean, and it changes from one draw of questions to another, so we need a way to measure that variation[^1].
For a large number of questions with finite-variance scores, the Central Limit Theorem gives a standard error that can be estimated from the observed scores, and a 95% confidence interval is $\bar{s} \pm 1.96 \times SE$[^1].

If an eval has $n$ independent questions scored 0 or 1 with true accuracy $p$, the standard error reduces to $SE = \sqrt{\bar{s}(1-\bar{s})/n}$[^1].
For 500 questions at 70% accuracy, $SE \approx 0.0205$, so the 95% interval $0.70 \pm 1.96 \times 0.0205$ runs from about 66% to 74%[^1].

Questions that share a passage are not independent, and on two popular evals clustered standard errors were up to about 3 times the naive value[^1].
Resampling each question $K$ times reduces the within-question variance by a factor of $K$, but gains flatten once that term is small relative to the variance of question difficulty[^1].
For two models scored on the same questions, positive correlation between their per-question scores shrinks the standard error of the difference, so pairing is more powerful than comparing two separate intervals[^1].

The sample size for detecting a difference $\delta$ between two models, with false-positive rate $\alpha$ and false-negative rate $\beta$, is $n = (z_{\alpha/2}+z_\beta)^2(\omega^2+\sigma_A^2/K_A+\sigma_B^2/K_B)/\delta^2$, where $\omega^2$ is the variance of the paired difference in per-question scores and $\sigma_A^2$, $\sigma_B^2$ are the expected within-question variances[^1].
With the author's fictional parameters, a 3-point difference at 80% power and 5% false-positive rate needs about 969 questions, so new evals should contain at least 1,000 questions[^1].

Other noise sources were measured experimentally, not derived.
Across ten 7B models differing only in initialisation seed, seed variance was generally below the per-model 95% confidence interval, but benchmarks with few items such as COPA and HumanEval varied most[^2].
Continuous metrics had higher signal-to-noise ratios than discrete ones, and cloze framing of MMLU raised monotonicity to 0.95 from 0.09 at 7B scale[^2].
Item analysis and item response theory did not meaningfully reduce variance[^2].
ProSA defines PromptSensiScore as the average discrepancy in correctness across paraphrased prompts for the same instance, and finds that few-shot examples and larger models tend to reduce it[^10].

## Evaluating retrieval-augmented systems

A RAG application has a retriever and a generator, so its quality has several parts that can be measured separately[^9].
Ragas therefore scores three dimensions without human reference answers: faithfulness, answer relevance and context relevance[^11].

- Faithfulness: the LLM extracts statements from the answer and verifies each against the context, giving $F = |V|/|S|$, where $|S|$ is the number of statements and $|V|$ the number judged supported[^11].
- Answer relevance: the LLM regenerates $n$ questions from the answer, and $AR = \frac{1}{n}\sum_i \mathrm{sim}(q, q_i)$ is the mean cosine similarity to the original question $q$[^11].
- Context relevance: the LLM extracts the sentences needed to answer the question, giving $CR$ as the extracted fraction of context sentences[^11].

On WikiEval, 50 recent Wikipedia pages with human pairwise judgements, annotators agreed with each other in about 95% of faithfulness and context cases[^11].
Ragas agreed with the human choices more often than GPT Score and GPT Ranking baselines, and context relevance was the hardest dimension[^11].
ARES instead generates synthetic query, passage and answer triples from the in-domain corpus, and trains a separate lightweight DeBERTa-v3-Large judge for each of the three dimensions[^9].
It then applies prediction-powered inference (PPI), which uses about 150 or more human labels to correct the judge's bias and give confidence intervals for ranking RAG configurations[^9].
The PPI intervals captured the ground-truth averages more than 95% of the time[^9].

The two designs differ in adaptability: Ragas relies on a few heuristic hand-written prompts, while ARES needs a corpus, few-shot examples and a labelled validation set[^9].
ARES judges lose accuracy under domain shift, reaching a Kendall's tau of only 0.33 on XGLUE, so a change of language or task needs new in-domain data[^9].
In the Ragas implementation and experiments, all prompts were evaluated with gpt-3.5-turbo-16k[^11].
Both are judges in the sense of the section on judge biases, so their verdicts need checking against human labels, and differences between systems should be read with the noise-aware methods of the section on score noise.

## Side-by-side comparison of the main approaches

| Approach | Measures | Cost | Main failure mode | Evidence |
|---|---|---|---|---|
| Golden set | Behaviour on reviewed test cases | Curation and review | Goes stale as traffic changes | Practitioner guidance[^3] |
| Held-out check | Score on data never used in tuning | Separate, untouched set | Overfitting once the set is used for tuning | Practitioner guidance[^3] |
| Contamination probe | Whether the model reproduces dataset items | Queries and completions per instance | Scores may reflect memorised answers | Shown experimentally[^4] |
| Pointwise judge | Score of a single answer | One call per answer | Scores may be unstable; subtle differences missed | Stated as a likely limitation[^5] |
| Pairwise judge | Which of two answers is better | Two calls per pair to control order | Position bias; pairs grow quadratically | Shown experimentally[^5] |
| Fine-tuned judge | Context relevance and faithfulness from a trained lightweight model | Synthetic data generation and fine-tuning | Dependence on the generating LLM | Shown experimentally[^9] |
| Logit probability calibration | Token probabilities as confidence | Per-token probabilities often unavailable | Over-confidence after RLHF | Shown experimentally[^8] |
| PPI with human labels | Judge-corrected accuracy with a confidence interval | A few hundred human labels plus judge calls | Needs valid human labels | Derived[^9] |
| Regression test | Score change on a pinned set | Running a fixed set on each version | Small deltas mistaken for real changes | Practitioner guidance[^3] |

Use a golden set as a release gate, and keep a held-out check untouched by tuning[^3].
Use contamination probes only when the model can be queried[^4].
Compare two models on the same questions and report paired differences with standard errors[^1].

## Summary and self-check questions

A benchmark score is an estimate of performance on an unseen population of questions, so it carries a standard error[^1].
Keep held-out data clean, because reusing it for tuning overfits it.
Verify judges against human labels and counter biases such as position bias[^5].
Calibrate a cheap judge with about 150 or more human labels[^9].
Regression-test with noise-aware thresholds: a paired difference whose 95% confidence interval excludes zero is statistically significant[^1].
Evaluate a RAG pipeline by component, with separate judges for context relevance, answer faithfulness and answer relevance[^9].

- For 500 questions at 70% accuracy, what is the standard error and 95% confidence interval[^1]?
- Why does a swap-and-agree test reduce position bias[^5]?
- Why does comparing guided with general instruction isolate memorisation[^4]?
- What does prediction-powered inference correct[^9]?
- Why does a paired comparison need fewer questions[^1]?

## References

[^1]: Miller, E. (2024). *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations*. arXiv preprint 2411.00640. Cited at pages 1, 2, 3, 4, 5, 7, 9, 10.
[^2]: Madaan, L., Singh, A. K., Schaeffer, R., Poulton, A., Koyejo, S., Stenetorp, P., Narang, S., Hupkes, D. (2024). *Quantifying Variance in Evaluation Benchmarks*. arXiv preprint 2406.10229. Cited at pages 1, 4, 5, 8.
[^3]: langfuse.com (n.d.). [*Golden dataset evaluation: build and maintain LLM test sets*](https://langfuse.com/resources/engineering/golden-dataset-evaluation). langfuse.com (commercial).
[^4]: Golchin, S., Surdeanu, M. (2023). *Time Travel in LLMs: Tracing Data Contamination in Large Language Models*. arXiv preprint 2308.08493. Cited at pages 1, 2, 3, 4, 5, 7, 8, 9, 15.
[^5]: Zheng, L., Chiang, W., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., et al. (2023). [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685). arxiv.org (scholarly). Cited at pages 2, 3, 4, 5, 6, 8, 10.
[^6]: Shi, L., Ma, C., Liang, W., Diao, X., Ma, W., Vosoughi, S. (2025). [*Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge*](https://aclanthology.org/2025.ijcnlp-long.18.pdf). International Joint Conference on Natural Language Processing and Conference of the Asia-Pacific Chapter of the Association for Computational Linguistics (IJCNLP-AACL). Cited at pages 2, 4.
[^7]: Wataoka, K., Takahashi, T., Ri, R. (2024). *Self-Preference Bias in LLM-as-a-Judge*. arXiv preprint 2410.21819. Cited at pages 1, 9.
[^8]: Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., Manning, C. D. (2023). [*Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback*](https://arxiv.org/abs/2305.14975). arxiv.org (scholarly). Cited at pages 1, 2, 3, 5.
[^9]: Saad-Falcon, J., Khattab, O., Potts, C., Zaharia, M. (2023). *ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems*. arXiv preprint 2311.09476. Cited at pages 1, 2, 3, 4, 8.
[^10]: Zhuo, J., Zhang, S., Fang, X., Duan, H., Lin, D., Chen, K. (2024). [*ProSA: Assessing and Understanding the Prompt Sensitivity of LLMs*](https://aclanthology.org/2024.findings-emnlp.108.pdf). Findings of the Association for Computational Linguistics: EMNLP (Findings of EMNLP).
[^11]: Es, S., James, J., Espinosa-Anke, L., Schockaert, S. (2023). *Ragas: Automated Evaluation of Retrieval Augmented Generation*. arXiv preprint 2309.15217. Cited at pages 3, 4, 5.
