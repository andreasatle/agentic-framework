# Retrieval Done Well: A Tutorial on Chunking, Hybrid Search, Reranking, Evaluation, and Long Context vs. Retrieval

## What retrieval-augmented generation is, and the shape of a retrieval pipeline

A language model's factual knowledge is thought to sit largely in the connections of its very large feedforward layers[1].
Simple prompting is therefore unreliable for factual answers, because a model often hallucinates and is poorly calibrated, so it can give a very wrong answer with complete certainty[1].
A model also cannot answer questions about proprietary data absent from its pretraining corpus, and because it is static it cannot reflect events after its release[1].
Retrieval-augmented generation (RAG) supplies external documents, so the answer is grounded in a curated dataset and can be shown with the passage it came from[1].
In RAG, information retrieval (IR) selects documents likely to help answer the question, and a language model then generates an answer from them[1].
The pipeline in this tutorial has five stages: chunk and index the corpus offline, run first-stage retrieval, fuse scores from several retrievers, rerank the top candidates, and generate from a prompt holding the chosen chunks.

A bi-encoder encodes the query and each document separately into dense vectors, and scores a pair by the dot product or cosine of the two vectors[1].
Because document vectors do not depend on the query, they can be computed once and stored in an index.
Queries are encoded, and the closest stored vectors are returned[2].

A retriever returns stored passages, and the generative language model produces the response from the retrieved chunks[2].
Context precision and context recall are retrieval measures, while faithfulness and answer relevance are generation measures[2].
Because a wrong answer may come from either stage, retrieval should be measured on its own.

## Vector indexes and approximate nearest-neighbor search

Exact nearest-neighbor search over a data set $P \subset \mathbb{R}^d$ with $|P| = n$ is costly, because each query touches $O(nd)$ coordinates and checking all pairs needs roughly $n^2$ distance computations[3].
The key idea is precomputation: build a data structure $D_P$ on $P$ first, then answer queries quickly against it[3].

With Euclidean distance $d(p,q)=\lVert p-q\rVert_2$, a range query returns $D_P(q,r)=\{p\in P \mid d(p,q)\le r\}$ for a radius $r$, and a nearest-neighbor query returns $\varphi_P(q)=\arg\min_{p\in P} d(p,q)$[3].
For $\varepsilon\in(0,1]$, a point $p$ is an $\varepsilon$-approximate nearest neighbor of $q$ if $d(p,q)\le(1+\varepsilon)\,d(\varphi_P(q),q)$[3].

Random projection multiplies the vectors by a projection matrix; the more random the matrix, the better, though computing it can be costly[2].
Locality-sensitive hashing (LSH) uses hash functions under which close points are more likely to collide, so a query searches only the bucket its hash returns[3, 2].
Its query time is roughly $O(n^\rho)$ for a $\rho$ that depends on the approximation factor, which is not nearly logarithmic, though its guarantees are proven[3].
Product quantization segments each vector, clusters each group of segments, and assigns a code to each cluster, trading memory for accuracy[2].
Hierarchical clustering groups vectors by distance, identifies each group by its centroid, and searches by comparing the query with the centroids[2].
Graph-based HNSW links vertices by proximity in a layered graph, starts each search at the sparse top layer, and greedily descends toward the query through finer layers[3, 2].

Approximate search is a trade-off: accepting that some true neighbors are missed buys lower latency and lower memory[3].
ANN recall, the fraction of true nearest neighbors the index returns, is distinct from retrieval relevance, which asks whether the returned items answer the user's need.
Vector databases can associate stored vectors with metadata, which allows filtering[2].

The complexity bounds and LSH guarantees are analysis in the Utah notes, while the claim that graph methods beat LSH in practice is practitioner observation that the notes say lacks full mathematical explanation[3].
The CERN slides give a practitioner-level description of the index families[2].

## Chunking: deciding what a retrievable unit is

Documents must be split because embedding models and prompts have limits, and each chunk is vectorized and stored, so the unit decides what the retriever can return, what the vector database costs, and how much context the model reads[4].
Chunk size pulls against retrieval quality, storage cost, latency and hallucination risk at once, and halving it doubles the vector count[4].
A reasonable starting size matches the length of a complete answer in your corpus, which you can estimate by noting how much surrounding text a person needs to justify ten real answers[4].

Overlap repeats a stretch of text across neighbouring chunks, so a fact cut at a boundary can still appear whole in one chunk[4].
The cost is storage, because repeated text is embedded and indexed more than once[4].
Suppose a chunk ends after "The refund window is 30 days." and the next begins with "Unused items are excluded."
Neither chunk alone answers "How long is the refund window for unused items?", but with overlap the second chunk repeats the first sentence and can answer it.

- Fixed-size splitting cuts by character count and ignores sentence ends, which suits text with no structure such as transcripts[4].
- Recursive splitting tries paragraph, line, space and character separators in order, so no chunk straddles a paragraph break[4].
- Structure-aware splitting honours the headings and paragraphs an author marked, and paragraph-group chunking roughly doubled ranking quality against fixed character chunking across 1,080 configurations[4].
- Semantic splitting cuts where cosine similarity between adjacent sentences drops below a threshold, yet fixed-size chunking won on three of five evidence-retrieval datasets in one study[4].
- Context-enriched chunking prepends an LLM-written statement to each chunk before embedding, while late chunking embeds the whole document first and applies boundaries afterwards[4].

The practitioner benchmark advises starting with a tuned recursive splitter and adding advanced methods only when a named failure appears, since simple splitting captures most of the gain[4].
This is a benchmark blog's view rather than a controlled study, so treat it as a practical default and not a proven ranking.
To separate a chunking failure from a generation failure, score Chunk Relevance per retrieved chunk: if no chunk is relevant, the boundaries failed rather than the prompt[4].
Context Precision aggregates relevance over the retrieved set, weighted by rank, and consistently low values suggest chunks longer than they need to be[4].

## Hybrid search: keywords plus vectors, and how to fuse the scores

Classic retrieval scores a document by word overlap with the query, and an inverted index maps each term to the documents containing it, so only candidate documents need scoring[1].
Term weights begin with tf-idf, where $\mathrm{idf}_t=\log_{10}(N/\mathrm{df}_t)$ gives low weight to terms that occur in many of the $N$ documents[1].
BM25 scores query $q$ against document $d$ as $\sum_{t\in q}\mathrm{idf}_t \cdot \frac{\mathrm{tf}_{t,d}}{k\left(1-b+b\,|d|/|d_{avg}|\right)+\mathrm{tf}_{t,d}}$, where $\mathrm{tf}_{t,d}$ is the log-weighted count of term $t$ in $d$, $|d|$ its length and $|d_{avg}|$ the average length[1].
The parameter $k$ controls term-frequency saturation: $k=0$ reduces BM25 to binary term presence plus idf, while a large $k$ approaches raw frequency plus idf[1].
The parameter $b$ ranges from 1 (full length scaling) to 0 (no length scaling), and Manning et al. suggest $k\in[1.2,2]$ and $b=0.75$[1].
Lexical methods fail on vocabulary mismatch, while dense embeddings can capture synonymy[1].
In the Qdrant demo, the query "a good lunch" returned zero sparse results while dense search always returned results[5].
BEIR nonetheless found BM25 a robust zero-shot baseline, often outperforming more complex neural approaches out of domain[6].
BM25 is unbounded while cosine lies in $[-1,1]$, so the two scores live on incompatible scales[5].
One option is score normalization, such as min-max or L2 scaling followed by a weighted sum, but min-max and L2 normalization are sensitive to outliers[7].
The other is reciprocal rank fusion, $\mathrm{RRF}(d)=\sum_r \frac{1}{k+\mathrm{rank}_r(d)}$, summed over rankers $r$, with a default rank constant of $k=60$[7].
Because the formula reads only $\mathrm{rank}_r(d)$, any monotone rescaling of a ranker's scores leaves RRF unchanged; this is a derived property, not an experimental finding.
The constant $k$ damps top-rank dominance: the gap between ranks 1 and 2 is $1/(k+1)-1/(k+2)$, which shrinks as $k$ grows[7].
In a worked example, BM25 ranks $A$, $B$, $C$ first to third and dense search ranks $B$, $D$, $A$ first to third, with no other documents retrieved.
With $k=60$, $B$ scores $1/62+1/61\approx0.0325$, $A$ scores $1/61+1/63\approx0.0322$, $D$ scores $1/62\approx0.0161$, and $C$ scores $1/63\approx0.0159$, so $B$ leads.
In a vector database, a hybrid query is one request with a sparse and a dense subquery, plus a fusion step[5].
The Qdrant demo prefetches the top 3 by BM25 and the top 3 by dense similarity, then applies an RRF fusion query to merge them[5].
OpenSearch reports that RRF scored 3.86% lower NDCG@10 than score-based hybrid across six BEIR datasets, a measured result on one cluster rather than a general law[7].

## Reranking: spending more compute on fewer candidates

A two-stage pipeline splits the work between a cheap first stage that favours recall and an expensive second stage that favours precision[8].
The first stage retrieves a large set of candidates, such as the top 1,000 documents from BM25, and the second stage rescores them with a more computationally intensive method[9].
A bi-encoder loses information because the query and document are each compressed into a single vector and never see each other[10].

The first family is the cross-encoder, which feeds the query as sentence A and the passage as sentence B, and uses the [CLS] vector as input to a single-layer network that gives the probability that the passage is relevant[9].
Because query and passage are processed together, re-ranking $k$ candidates costs $O(k)$ forward passes per query[10].
Training minimises the cross-entropy loss below, where $J_{pos}$ and $J_{neg}$ are the relevant and non-relevant passages among the BM25 top 1,000 and $s_j$ is the predicted probability for passage $j$[9].

$$
L=-\sum_{j\in J_{pos}}\log(s_j)-\sum_{j\in J_{neg}}\log(1-s_j)
$$

On the MS MARCO passage task, the BERT re-ranker outperformed the previous state of the art by 27% relative in MRR@10, shown by experiment on that dataset[9].
On BEIR, the cross-encoder BM25+CE beat BM25 on 16 of 18 datasets, shown by experiment[6].

The second family is late interaction, exemplified by ColBERT, which keeps one embedding per token instead of pooling all tokens into one vector[10].
MaxSim takes, for each query token, the maximum similarity over all document tokens, and then sums these maxima over the query tokens[10].

$$
S(q,d)=\sum_{i=1}^{|q|} \max_{j} \, E_q(q_i)^{\top} E_d(d_j)
$$

Here $E_q(q_i)$ is the embedding of query token $i$ and $E_d(d_j)$ is the embedding of document token $j$[10].
Document token vectors are precomputed offline, but storing one vector per token needs far more space than one vector per document[10].
On BEIR, ColBERT beat BM25 on 9 of 18 datasets, and the authors suggest that cross-attention-like operations matter for out-of-distribution generalization[6].

The third family uses large language models as listwise rerankers, which output a ranked permutation of a group of passages rather than a score[8].
Because a model's context is limited, the authors slide a window over the candidates, rerank from the back of the list to the front, and report that GPT-4 with this permutation prompt beats supervised systems on nearly all datasets[8].
To check for contamination, the authors built NovelEval, a set of 21 questions about events after GPT-4's release, on which GPT-4 performed well[8].
The authors distil ChatGPT's permutations into a smaller student model with a listwise softmax cross-entropy, where $r_i$ is the ChatGPT rank of passage $i$ and $s_i$ is the student score[8].

$$
\mathcal{L}_{\text{CE}}=-\sum_{i}\mathbb{1}_{r_i=1}\log\frac{\exp(s_i)}{\sum_j \exp(s_j)}
$$

The softmax turns the student scores into a distribution over the candidates, so the loss is low when the passage ranked first by ChatGPT receives most of that mass.
A distilled 435M DeBERTa model outperformed the 3B monoT5 on BEIR, shown by experiment, and the authors hypothesise that ChatGPT's relevance judgements are more comprehensive than MS MARCO labels[8].
On DBPedia, re-ranking the top 100 BM25 documents with a cross-encoder took over 350 ms per query, against under 20 ms for dense retrievers[6].

Reranking thus buys quality with latency and storage, and these are measured costs on specific setups rather than a general law.

## Evaluating retrieval on its own

Evaluating the retriever on its own matters because a wrong RAG answer can come from retrieval or from generation, and only a separate test shows which to fix[11].
Offline metrics are computed on labelled queries before deployment, while online metrics come from real user interactions such as click-through rate[11].

Take one toy ranking of eight items in which the relevant items sit at ranks 2, 4, 5 and 7, so the relevant set is $R=\{2,4,5,7\}$ with $|R|=4$[11].
Let $\text{top}_k$ be the first $k$ returned items; precision@k is $P@k=|R\cap\text{top}_k|/k$ and recall@k is $R@k=|R\cap\text{top}_k|/|R|$[11].
On this ranking recall@3 is 0.25 and recall@5 is 0.75, and recall@k ignores order, so a relevant item at rank one scores the same as one at rank four[11].

Mean reciprocal rank (MRR) averages $1/\text{rank}_q$ over $Q$ queries, where $\text{rank}_q$ is the rank of the first relevant result for query $q$[11].
On the toy ranking the first relevant item is at rank 2, giving reciprocal rank $1/2$, and MRR ignores the other relevant items[11].

Average precision averages $P@k$ over the ranks where a relevant item appears, $\text{AP}=\frac{1}{|R|}\sum_k P@k\,\text{rel}_k$, where $\text{rel}_k$ is 1 if the item at rank $k$ is relevant and 0 otherwise, and MAP averages AP over queries[11].
Discounted cumulative gain handles graded relevance by summing the gain $\text{rel}_i$ at rank $i$ with a logarithmic position discount, $\text{DCG@}k=\sum_{i=1}^{k}\frac{\text{rel}_i}{\log_2(1+i)}$[11].
nDCG divides DCG by the ideal DCG of the most-relevant-first ordering, so $\text{nDCG@}k=\text{DCG@}k/\text{IDCG@}k$ reaches 1.0 for a perfect ranking[11].

- Recall@k is order-unaware and reaches a perfect score as K approaches N, so relying on it alone can be deceptive[11].
- MRR suits question answering, where the first relevant result matters, and is poor when several items must be returned[11].
- Recall@k suits a first-stage retriever that must not miss candidates, while MRR and nDCG suit a reranker that orders a short list.

BEIR evaluates retrievers zero-shot on 18 datasets from nine tasks and reports nDCG@10, because it handles both binary and graded judgements[6].
BM25 is a robust baseline, re-ranking and late-interaction models achieve the best zero-shot averages at high computational cost, and dense and sparse models are cheaper but often underperform[6].
Benchmark labels can be biased: on TREC-COVID the nDCG@10 of ANCE rose from 0.654 to 0.735 once unjudged hits were annotated[6].
Build a small labelled set from your own queries and documents and score candidate retrievers on it.

## Long context versus retrieval

A 100K-token window can accommodate long documents, but retrieval still reduces input length and cost[12, 13].
Transformer compute and memory grow with input length, and token-based API pricing makes longer prompts more expensive per query[12, 13].

Shown by experiment on nine LongBench and ∞Bench datasets, long context (LC) beats RAG on average with Gemini-1.5-Pro, GPT-4O, and GPT-3.5-Turbo when sufficiently resourced[13].
SELF-ROUTE answers from RAG when the model judges retrieved chunks sufficient and falls back to LC otherwise, cutting cost by 65% for Gemini-1.5-Pro and 39% for GPT-4O while staying close to LC performance[13].
Authors’ hypothesis: RAG acts as a prior regularizing attention onto retrieved segments, avoiding irrelevant distractions[13].

Shown by experiment on NaturalQuestions-based multi-document QA and synthetic key-value retrieval, accuracy often follows a U-shaped curve over answer position: highest at the edges, lowest in the middle, even for long-context models[12].
On NaturalQuestions-Open, moving from 20 to 50 retrieved documents improved GPT-3.5-Turbo accuracy by only about 1.5%, while retriever recall kept rising[12].

Practitioner evidence from 171 questions over 30 MMLongBench-Doc PDFs with Claude Sonnet 4.5: agentic RAG, where an agent dynamically retrieves evidence, scored 53.2% at $0.0827 per question versus 59.6% at $0.1885 for premium LlamaCloud full-context processing[14].
Agentic RAG had zero failed queries; its accuracy gap against premium full-context approaches was not significant under McNemar’s test at $\alpha=0.05$[14].

- Choose LC when documents fit the window, receive few questions, and accuracy outweighs cost[14].
- Choose retrieval for large corpora or high query volume, and prompt for passage citations when evidence matters[14, 1].
- Rerank relevant passages toward the prompt’s start and test answer-position sensitivity rather than assuming these model- and dataset-specific results generalize[12, 13].

## The main approaches side by side

The table compares the main approaches on what each computes, when it runs, what it costs, and the evidence behind it.

| Approach | Computes | Timing | Cost scaling | Main strength | Main failure mode | Evidence |
|---|---|---|---|---|---|---|
| BM25 / lexical | Token matching with TF-IDF-style weights | Index offline, query online | About 18GB index for BioASQ (about 15M documents) | Robust zero-shot baseline | Misses synonyms and paraphrase | Experimental (BEIR)[6] |
| Dense bi-encoder with ANN | Query and document vectors compared by similarity | Document vectors offline, query online | Under 20 ms per query on 1M DBPedia documents on GPU; about 3GB index | Captures semantic matches | Underperforms BM25 on large domain shifts | Experimental (BEIR)[6] |
| Hybrid with RRF or normalized sum | Fused lexical and dense rankings or scores | Online fusion of two searches | One extra search per query | Combines complementary signals | Score scale sensitivity when summing | Practitioner (OpenSearch benchmark)[7] |
| Late interaction (ColBERT) | Token-level MaxSim | Token vectors offline, MaxSim online | About 900GB for BioASQ index versus 18GB for BM25 | Fine-grained token matching | Large index size | Experimental (BEIR); practitioner (Weaviate)[6, 10] |
| Cross-encoder reranker | Joint query-passage relevance score | Online over top-k candidates | Above 350 ms latency on 1M DBPedia documents | Accurate reranking of candidates | Latency at inference | Experimental (BEIR)[6] |
| LLM reranker | Permutation of passages | Online over sliding windows | Multiple API calls per query over sliding windows | Zero-shot ranking | Sensitivity to initial order | Experimental (Sun et al[8].) |
| Long context | Answer generated from full context | Online per query | Cost grows with input tokens | Strong accuracy when resourced sufficiently | Cost grows with input tokens | Experimental (Li et al[13].) |
| Self-routing RAG | Answerability decision with fallback to full context | Online | Most queries use only retrieved chunks; fallback re-pays full context | Cost-accuracy balance | Assumes the model is well calibrated | Experimental (Li et al[13].) |

BEIR shows that BM25 remains a robust zero-shot baseline, and that cross-attentional rerankers and late interaction generalize best on average at high computational cost[6].
Self-routing keeps most of a long-context model's accuracy at lower cost, but this rests on one set of models and datasets[13].

A reasonable default pipeline chunks and indexes the corpus offline, retrieves candidates with hybrid search, reranks the top $k$ candidates with a cross-encoder, and evaluates the retriever with recall@k and nDCG[6].
For a small or high-value corpus, the pipeline can route queries to long context instead of retrieval[13].

## Summary and check-your-understanding questions

Retrieval is a recall-then-precision cascade: a cheap first stage gathers candidates, and a costlier stage orders the top few[6].
Chunk and index choices set the ceiling, because a passage that was never indexed or was cut badly cannot be recovered later.
Hybrid fusion covers each side's blind spots by combining exact keyword matching with meaning-based vectors[1].
Rerankers trade compute for accuracy, and evaluating the retriever separately keeps a retrieval miss from being mistaken for a generation error.
Long context versus retrieval is a trade-off among cost, accuracy and answer position[12, 13].

- Why does RRF not need score normalization? It uses only each document's rank in each list, so BM25 and cosine scores never need to share a scale[7].
- For a toy ranking with relevant items at ranks 2 and 5, where each relevant item has gain 1 and every other item has gain 0, what are recall@3 and MRR? Recall@3 is 1/2, since one of the two relevant items appears in the top three, and MRR is 1/2, since the first relevant item sits at rank 2.
- Why can a cross-encoder not serve as a first stage over millions of documents? It needs a forward pass per query-document pair, so cost grows with the corpus[8].
- What does MaxSim compute, and what must be stored for it? For each query token it takes the maximum similarity over document tokens and sums these, so token-level vectors must be stored for each document[10].
- Why does accuracy depend on answer position in a long prompt? Performance is highest when relevant information sits at the very beginning or end of the input context, and it significantly degrades when information sits in the middle[12].
- When should you choose long context over RAG? For small corpora that fit the window, low query volume, and high-value queries where cost is secondary.

## References

1. web.stanford.edu (2026). [*Speech and Language Processing. Daniel Jurafsky & James H. Martin.*](https://web.stanford.edu/~jurafsky/slp3/11.pdf). web.stanford.edu (scholarly). Cited at pages 1, 2, 3.
2. indico.cern.ch (n.d.). [*RAG*](https://indico.cern.ch/event/1433679/contributions/6032028/attachments/2890543/5066702/RAG.pdf). indico.cern.ch (institutional). Cited at pages 1, 4, 5, 6, 7, 8, 17, 21, 30.
3. users.cs.utah.edu (2025). [*5 Approximate Nearest Neighbors + HNSW*](https://users.cs.utah.edu/~jeffp/teaching/DM/LN/L5-ANN+HNSW.pdf). users.cs.utah.edu (institutional).
4. Bhavsar, P. (). *Advanced Chunking Techniques: What The Benchmarks Actually Show*. Splunk blog.
5. qdrant.tech (n.d.). [*Demo: Implementing a Hybrid Search System*](https://qdrant.tech/course/essentials/day-3/hybrid-search-demo). qdrant.tech (commercial).
6. Thakur, N., Reimers, N., Rücklé, A., Srivastava, A., Gurevych, I. (2021). *BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models*. arXiv preprint 2104.08663. Cited at pages 1, 5, 6, 7, 8.
7. Kolchina, R. B. M. G. M. S. F. (2025). [*Introducing reciprocal rank fusion for hybrid search*](https://opensearch.org/blog/introducing-reciprocal-rank-fusion-hybrid-search). opensearch.org (official).
8. Sun, W., Yan, L., Ma, X., Wang, S., Ren, P., Chen, Z., Yin, D., Ren, Z. (2023). *Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents*. arXiv preprint 2304.09542. Cited at pages 1, 3, 4, 5, 7, 8, 17.
9. Nogueira, R., Cho, K. (2019). *Passage Re-ranking with BERT*. arXiv preprint 1901.04085.
10. Monigatti, L., Williams, D., Slocum, V. (2025). [*An Overview of Late Interaction Retrieval Models: ColBERT, ColPali, and ColQwen*](https://weaviate.io/blog/late-interaction-overview). weaviate.io (commercial).
11. Carnevali, L. (2023). [*Evaluation Measures in Information Retrieval*](https://www.pinecone.io/learn/offline-evaluation). pinecone.io (commercial).
12. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., Liang, P. (2023). *Lost in the Middle: How Language Models Use Long Contexts*. arXiv preprint 2307.03172. Cited at pages 1, 2, 3, 10.
13. Li, Z., Li, C., Zhang, M., Mei, Q., Bendersky, M. (2024). *Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach*. arXiv preprint 2407.16833. Cited at pages 1, 2, 3, 4.
14. Team, S. (2026). [*Agentic RAG vs Long-Context LLMs: A 171-Question Benchmark on 30 Long PDFs*](https://www.surfsense.com/blog/agentic-rag-vs-long-context-llms-benchmark). surfsense.com (commercial).
