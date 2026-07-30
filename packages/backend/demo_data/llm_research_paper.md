# Retrieval Quality, Not Model Scale, Dominates Document Q&A Accuracy: An Empirical Study

*This is an original sample document written for demonstration purposes.*

**Authors:** Sample Research Group
**Status:** Working paper (demonstration copy)

## Abstract

We study the relative contribution of retrieval quality and language-model scale to end-to-end accuracy in retrieval-augmented document question answering (RAG). Across 4,800 question–document pairs spanning financial filings, contracts, and technical manuals, we find that improving the retriever explains 2.9× more variance in answer correctness than upgrading the generator model by one capability tier. Chunking strategy alone shifts accuracy by up to 14 percentage points. We conclude with practical recommendations: invest first in retrieval (chunking, query expansion, re-ranking), ground every answer in citations, and expose confidence to end users.

## 1. Introduction

Retrieval-augmented generation has become the default architecture for question answering over private document collections. A persistent practitioner question is where marginal effort should go: a larger generator model, or a better retrieval pipeline? Anecdotal reports conflict, and public benchmarks typically hold the retriever fixed.

We isolate the two factors experimentally. Our study varies (a) generator capability across three tiers, (b) chunk size and overlap, (c) query expansion, and (d) cross-encoder re-ranking, measuring exact-answer accuracy judged by a held-out grader with 96% human agreement.

## 2. Method

**Corpus.** 120 documents: 40 annual reports (mean 48 pages), 40 commercial contracts (mean 22 pages), 40 technical manuals (mean 65 pages).

**Questions.** 4,800 questions written by domain annotators, split into extractive (61%), aggregative (27%), and inferential (12%) types. Each question has a gold answer span verified by two annotators.

**Conditions.** Chunk sizes of 400, 1,000, and 2,000 characters with 0%, 10%, and 25% overlap; top-k retrieval with k ∈ {3, 5, 10}; optional LLM query expansion (two paraphrases); optional cross-encoder re-ranking of the top 20 candidates.

## 3. Results

**Retrieval dominates.** Moving from the worst to the best retrieval configuration improved end-to-end accuracy from 61.2% to 83.7% (+22.5 points) with the generator fixed. Upgrading the generator one tier with retrieval fixed improved accuracy by 7.8 points on average.

**Chunking matters more than expected.** 1,000-character chunks with 10% overlap outperformed 2,000-character chunks by 9–14 points on extractive questions. Long chunks dilute the relevant span within the retrieved context.

**Query expansion helps vocabulary mismatch.** Expansion added 4.1 points overall but 11.3 points on the subset where the question shared fewer than two content words with the gold passage.

**Re-ranking is the best single addition.** Cross-encoder re-ranking of top-20 candidates into a final top-5 added 6.9 points at roughly 90 ms of added latency.

**Failure modes.** Of remaining errors, 44% were retrieval misses (gold passage absent from context), 31% were synthesis errors over correct context, 18% were table-structure misreads, and 7% were grader disagreements. Notably, when the gold passage was present in the top-3 retrieved chunks, generator accuracy exceeded 94% across all model tiers.

## 4. Practical Recommendations

1. **Fix retrieval first.** Until the gold passage reliably appears in retrieved context, generator upgrades buy little.
2. **Prefer ~1,000-character chunks with modest overlap** for mixed corpora.
3. **Show citations.** Because 44% of failures are silent retrieval misses, exposing the retrieved source text lets users detect unanswerable questions immediately.
4. **Expose confidence.** Retrieval similarity scores correlate (ρ = 0.62) with answer correctness and are cheap to surface.
5. **Treat tables separately.** Structure-aware extraction for tables addresses the second-largest error class.

## 5. Limitations

Our corpus is English-only, and our grader, while highly agreeing with humans, may share failure modes with the graded models. Scanned documents without a text layer were excluded; OCR quality is a separate and significant factor in production systems.

## 6. Conclusion

In document Q&A, retrieval quality is the dominant lever on accuracy. Teams should benchmark their retrieval pipeline before paying for larger generators, and should treat citations and confidence display as core product features rather than optional extras.
